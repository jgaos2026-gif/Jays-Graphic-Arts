from __future__ import annotations

import os
import signal
import shutil
import socket
import subprocess
import sys
import threading
import time
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType

import click


REPO_ROOT = Path(__file__).resolve().parents[1]
IROONLINK3_ROOT = REPO_ROOT / "IROONLINK3"
IROONLINK3_ENTRYPOINT = IROONLINK3_ROOT / "server.js"
IROONLINK3_NODE_MODULES = IROONLINK3_ROOT / "node_modules"
DEFAULT_SITE_PORT = 8080
DEFAULT_CONTROL_ROOM_PORT = 3000
PROCESS_STARTUP_GRACE_SECONDS = 0.2
HEADLESS_POLL_INTERVAL_SECONDS = 0.2


def is_port_open(host: str, port: int, timeout: float = 0.5) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        return sock.connect_ex((host, port)) == 0


def stop_process(process: subprocess.Popen[bytes] | None) -> None:
    if process is None or process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()


def wait_for_port(host: str, port: int, timeout: float = 15.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if is_port_open(host, port):
            return
        time.sleep(0.1)
    raise TimeoutError(f"Timed out waiting for {host}:{port}")


def parse_node_major_version(version_output: str) -> int | None:
    normalized = version_output.strip()
    if normalized.startswith("v"):
        normalized = normalized[1:]
    major, _, _ = normalized.partition(".")
    if not major.isdigit():
        return None
    return int(major)


def validate_desktop_runtime() -> None:
    if not IROONLINK3_ROOT.exists():
        raise RuntimeError(f"IROONLINK3 directory not found at {IROONLINK3_ROOT}")
    if not IROONLINK3_ENTRYPOINT.exists():
        raise RuntimeError(f"IROONLINK3 entrypoint not found at {IROONLINK3_ENTRYPOINT}")
    node_path = shutil.which("node")
    if node_path is None:
        raise RuntimeError("Node.js 18+ is required to run the IROONLINK3 control room.")
    try:
        version_result = subprocess.run(
            [node_path, "--version"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise RuntimeError("Unable to determine the installed Node.js version.") from exc
    node_major_version = parse_node_major_version(version_result.stdout)
    if node_major_version is None or node_major_version < 18:
        raise RuntimeError("Node.js 18+ is required to run the IROONLINK3 control room.")
    if not IROONLINK3_NODE_MODULES.exists():
        raise RuntimeError(
            f"IROONLINK3 dependencies are missing. Run `npm ci` in {IROONLINK3_ROOT} and try again."
        )


@dataclass
class ServiceCommand:
    label: str
    command: list[str]
    cwd: Path
    host: str
    port: int

    @property
    def url(self) -> str:
        return f"http://{self.host}:{self.port}"


def spawn_service(service: ServiceCommand, env: dict[str, str] | None = None) -> subprocess.Popen[bytes]:
    return subprocess.Popen(
        service.command,
        cwd=service.cwd,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=os.name != "nt",
    )


def spawn_service_checked(service: ServiceCommand, env: dict[str, str] | None = None) -> subprocess.Popen[bytes]:
    process = spawn_service(service, env=env)
    time.sleep(PROCESS_STARTUP_GRACE_SECONDS)
    if process.poll() is not None:
        raise RuntimeError(
            f"{service.label} failed to start. Check whether port {service.port} is available and dependencies are installed."
        )
    return process


def make_service_commands(site_port: int = DEFAULT_SITE_PORT, control_room_port: int = DEFAULT_CONTROL_ROOM_PORT) -> tuple[ServiceCommand, ServiceCommand]:
    python = sys.executable
    site = ServiceCommand(
        label="Website",
        command=[python, "-m", "http.server", str(site_port)],
        cwd=REPO_ROOT,
        host="127.0.0.1",
        port=site_port,
    )
    control_room = ServiceCommand(
        label="Control Room",
        command=["node", "server.js"],
        cwd=IROONLINK3_ROOT,
        host="127.0.0.1",
        port=control_room_port,
    )
    return site, control_room


def ensure_port_available(service: ServiceCommand, process: subprocess.Popen[bytes] | None) -> None:
    if process is not None and process.poll() is None:
        return
    if is_port_open(service.host, service.port):
        raise RuntimeError(f"{service.label} port {service.port} is already in use.")


def start_services(
    site_port: int = DEFAULT_SITE_PORT,
    control_room_port: int = DEFAULT_CONTROL_ROOM_PORT,
) -> tuple[ServiceCommand, ServiceCommand, subprocess.Popen[bytes], subprocess.Popen[bytes]]:
    validate_desktop_runtime()
    site, control_room = make_service_commands(site_port, control_room_port)
    ensure_port_available(site, process=None)
    site_process = spawn_service_checked(site)
    try:
        wait_for_port(site.host, site.port)
        ensure_port_available(control_room, process=None)
        env = os.environ.copy()
        env["PORT"] = str(control_room.port)
        control_room_process = spawn_service_checked(control_room, env=env)
        try:
            wait_for_port(control_room.host, control_room.port)
        except Exception:
            stop_process(control_room_process)
            raise
    except Exception:
        stop_process(site_process)
        raise
    return site, control_room, site_process, control_room_process


def load_tk_module(required: bool = False) -> ModuleType | None:
    try:
        import tkinter as tk
    except ImportError as exc:
        if required:
            raise click.ClickException(f"tkinter is required for GUI mode: {exc}") from exc
        return None
    return tk


def has_graphical_display() -> bool:
    if sys.platform.startswith("linux"):
        return bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))
    return True


def run_headless(site_port: int, control_room_port: int, open_browser: bool) -> None:
    site, control_room, site_process, control_room_process = start_services(site_port, control_room_port)
    stop_event = threading.Event()
    install_signal_handlers = threading.current_thread() is threading.main_thread()
    previous_sigint = None
    previous_sigterm = None
    sigterm_supported = hasattr(signal, "SIGTERM")
    if install_signal_handlers:
        def handle_stop_signal(_signum, _frame) -> None:
            stop_event.set()

        previous_sigint = signal.getsignal(signal.SIGINT)
        signal.signal(signal.SIGINT, handle_stop_signal)
        if sigterm_supported:
            previous_sigterm = signal.getsignal(signal.SIGTERM)
            signal.signal(signal.SIGTERM, handle_stop_signal)
    try:
        click.echo("Integrated launcher is running in headless mode.")
        click.echo(f"Website: {site.url}")
        click.echo(f"Control Room: {control_room.url}")
        click.echo("Press Ctrl+C to stop both services.")
        if open_browser:
            webbrowser.open(site.url)
            webbrowser.open(control_room.url)
        while not stop_event.is_set():
            time.sleep(HEADLESS_POLL_INTERVAL_SECONDS)
        click.echo("Stopping services...")
    finally:
        if install_signal_handlers:
            signal.signal(signal.SIGINT, previous_sigint or signal.default_int_handler)
        if install_signal_handlers and sigterm_supported:
            signal.signal(signal.SIGTERM, previous_sigterm or signal.SIG_DFL)
        stop_process(control_room_process)
        stop_process(site_process)


class DesktopLauncherApp:
    def __init__(
        self,
        tk_module,
        site_port: int = DEFAULT_SITE_PORT,
        control_room_port: int = DEFAULT_CONTROL_ROOM_PORT,
        auto_open_browser: bool = False,
    ) -> None:
        self.tk = tk_module
        self.root = tk_module.Tk()
        self.root.title("Jays Graphic Arts Desktop Launcher")
        self.root.geometry("560x280")
        self.root.resizable(False, False)

        self.site_port = tk_module.StringVar(value=str(site_port))
        self.control_room_port = tk_module.StringVar(value=str(control_room_port))
        self.status_text = tk_module.StringVar(value="Ready.")

        self.site_process: subprocess.Popen[bytes] | None = None
        self.control_room_process: subprocess.Popen[bytes] | None = None
        self.process_lock = threading.Lock()
        self.auto_open_browser = auto_open_browser
        self.browser_opened = False

        self._build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _build_ui(self) -> None:
        frame = self.tk.Frame(self.root, padx=20, pady=20)
        frame.pack(fill="both", expand=True)

        self.tk.Label(frame, text="Integrated local launch for the website and IROONLINK3.", anchor="w").pack(fill="x")

        ports = self.tk.Frame(frame, pady=12)
        ports.pack(fill="x")
        self.tk.Label(ports, text="Website port").grid(row=0, column=0, sticky="w")
        self.tk.Entry(ports, textvariable=self.site_port, width=10).grid(row=0, column=1, padx=(8, 24), sticky="w")
        self.tk.Label(ports, text="Control Room port").grid(row=0, column=2, sticky="w")
        self.tk.Entry(ports, textvariable=self.control_room_port, width=10).grid(row=0, column=3, padx=(8, 0), sticky="w")

        buttons = self.tk.Frame(frame, pady=12)
        buttons.pack(fill="x")
        self.tk.Button(buttons, text="Start all", width=18, command=self.start_all).grid(row=0, column=0, padx=(0, 8), pady=4)
        self.tk.Button(buttons, text="Stop all", width=18, command=self.stop_all).grid(row=0, column=1, padx=8, pady=4)
        self.tk.Button(buttons, text="Open website", width=18, command=self.open_website).grid(row=1, column=0, padx=(0, 8), pady=4)
        self.tk.Button(buttons, text="Open control room", width=18, command=self.open_control_room).grid(row=1, column=1, padx=8, pady=4)

        details = self.tk.Frame(frame, pady=8)
        details.pack(fill="x")
        self.website_label = self.tk.Label(details, anchor="w")
        self.website_label.pack(fill="x")
        self.control_room_label = self.tk.Label(details, anchor="w")
        self.control_room_label.pack(fill="x")
        self._refresh_labels()

        status_box = self.tk.LabelFrame(frame, text="Status", padx=12, pady=12)
        status_box.pack(fill="both", expand=True, pady=(8, 0))
        self.tk.Label(status_box, textvariable=self.status_text, justify="left", anchor="nw").pack(fill="both", expand=True)

    def _refresh_labels(self) -> None:
        site, control_room = self._commands()
        self.website_label.config(text=f"Website: {site.url}")
        self.control_room_label.config(text=f"Control Room: {control_room.url}")

    def _commands(self) -> tuple[ServiceCommand, ServiceCommand]:
        try:
            site_port = int(self.site_port.get())
            control_room_port = int(self.control_room_port.get())
        except ValueError as exc:
            raise ValueError("Ports must be whole numbers.") from exc
        if site_port < 1 or site_port > 65535 or control_room_port < 1 or control_room_port > 65535:
            raise ValueError("Ports must be between 1 and 65535.")
        return make_service_commands(site_port, control_room_port)

    def _set_status(self, message: str) -> None:
        self.status_text.set(message)

    def _launch_background(self, target) -> None:
        thread = threading.Thread(target=target, daemon=True)
        thread.start()

    def start_all(self) -> None:
        try:
            self._refresh_labels()
        except ValueError as exc:
            self._set_status(str(exc))
            return
        self._launch_background(self._start_all)

    def _start_all(self) -> None:
        try:
            validate_desktop_runtime()
            site, control_room = self._commands()
            self._set_status("Starting services...")

            with self.process_lock:
                site_process = self.site_process
            ensure_port_available(site, site_process)
            if site_process is None or site_process.poll() is not None:
                new_site_process = spawn_service_checked(site)
                with self.process_lock:
                    self.site_process = new_site_process
                wait_for_port(site.host, site.port)

            with self.process_lock:
                control_room_process = self.control_room_process
            ensure_port_available(control_room, control_room_process)
            if control_room_process is None or control_room_process.poll() is not None:
                env = os.environ.copy()
                env["PORT"] = str(control_room.port)
                new_control_room_process = spawn_service_checked(control_room, env=env)
                with self.process_lock:
                    self.control_room_process = new_control_room_process
                wait_for_port(control_room.host, control_room.port)

            self._set_status(
                f"Running.\n- Website: {site.url}\n- Control Room: {control_room.url}"
            )
            if self.auto_open_browser and not self.browser_opened:
                webbrowser.open(site.url)
                webbrowser.open(control_room.url)
                self.browser_opened = True
        except Exception as exc:
            self.stop_all()
            self._set_status(f"Startup failed: {exc}")

    def stop_all(self) -> None:
        with self.process_lock:
            control_room_process = self.control_room_process
            site_process = self.site_process
            self.control_room_process = None
            self.site_process = None
            self.browser_opened = False
        stop_process(control_room_process)
        stop_process(site_process)
        self._set_status("Stopped.")

    def open_website(self) -> None:
        try:
            site, _ = self._commands()
        except ValueError as exc:
            self._set_status(str(exc))
            return
        webbrowser.open(site.url)

    def open_control_room(self) -> None:
        try:
            _, control_room = self._commands()
        except ValueError as exc:
            self._set_status(str(exc))
            return
        webbrowser.open(control_room.url)

    def on_close(self) -> None:
        self.stop_all()
        self.root.destroy()

    def run(self) -> None:
        self.root.mainloop()


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.option("--mode", type=click.Choice(["auto", "gui", "headless"]), default="auto", show_default=True)
@click.option("--site-port", type=click.IntRange(1, 65535), default=DEFAULT_SITE_PORT, show_default=True)
@click.option("--control-room-port", type=click.IntRange(1, 65535), default=DEFAULT_CONTROL_ROOM_PORT, show_default=True)
@click.option("--open-browser/--no-open-browser", default=False, show_default=True)
def desktop_launcher_cli(mode: str, site_port: int, control_room_port: int, open_browser: bool) -> None:
    if mode == "headless":
        run_headless(site_port, control_room_port, open_browser)
        return

    gui_available = has_graphical_display()
    if mode == "gui" and not gui_available:
        raise click.ClickException("No graphical display is available for GUI mode. Use --mode headless instead.")

    tk = load_tk_module(required=mode == "gui")
    if tk is None or not gui_available:
        click.echo("GUI launcher unavailable; starting in headless mode.")
        run_headless(site_port, control_room_port, open_browser)
        return

    app = DesktopLauncherApp(
        tk,
        site_port=site_port,
        control_room_port=control_room_port,
        auto_open_browser=open_browser,
    )
    app.run()


def main() -> None:
    desktop_launcher_cli(standalone_mode=True)


if __name__ == "__main__":
    main()
