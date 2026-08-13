from __future__ import annotations

import subprocess
from typing import cast

import pytest
from click.testing import CliRunner

from braid_simulator.desktop_launcher import (
    DEFAULT_CONTROL_ROOM_PORT,
    DEFAULT_SITE_PORT,
    IROONLINK3_ROOT,
    REPO_ROOT,
    ServiceCommand,
    _main,
    ensure_port_available,
    make_service_commands,
    parse_node_major_version,
    validate_desktop_runtime,
)


def test_make_service_commands_use_expected_defaults() -> None:
    site, control_room = make_service_commands()

    assert site.cwd == REPO_ROOT
    assert site.port == DEFAULT_SITE_PORT
    assert site.command[-2:] == ["http.server", str(DEFAULT_SITE_PORT)]

    assert control_room.cwd == IROONLINK3_ROOT
    assert control_room.port == DEFAULT_CONTROL_ROOM_PORT
    assert control_room.command == ["node", "server.js"]


def test_make_service_commands_allow_custom_ports() -> None:
    site, control_room = make_service_commands(9090, 3100)

    assert site.port == 9090
    assert control_room.port == 3100
    assert site.url == "http://127.0.0.1:9090"
    assert control_room.url == "http://127.0.0.1:3100"


def test_validate_desktop_runtime_accepts_current_repo(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = tmp_path / "iroonlink3"
    entrypoint = root / "server.js"
    node_modules = root / "node_modules"
    node_modules.mkdir(parents=True, exist_ok=True)
    entrypoint.write_text("console.log('ok');", encoding="utf-8")
    monkeypatch.setattr("braid_simulator.desktop_launcher.IROONLINK3_ROOT", root)
    monkeypatch.setattr("braid_simulator.desktop_launcher.IROONLINK3_ENTRYPOINT", entrypoint)
    monkeypatch.setattr("braid_simulator.desktop_launcher.IROONLINK3_NODE_MODULES", node_modules)
    monkeypatch.setattr("braid_simulator.desktop_launcher.shutil.which", lambda name: "/usr/bin/node" if name == "node" else None)
    monkeypatch.setattr(
        "braid_simulator.desktop_launcher.subprocess.run",
        lambda *args, **kwargs: subprocess.CompletedProcess(args[0], 0, stdout="v20.11.1\n"),
    )

    validate_desktop_runtime()


def test_validate_desktop_runtime_requires_node(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = tmp_path / "iroonlink3"
    entrypoint = root / "server.js"
    node_modules = root / "node_modules"
    node_modules.mkdir(parents=True, exist_ok=True)
    entrypoint.write_text("console.log('ok');", encoding="utf-8")
    monkeypatch.setattr("braid_simulator.desktop_launcher.IROONLINK3_ROOT", root)
    monkeypatch.setattr("braid_simulator.desktop_launcher.IROONLINK3_ENTRYPOINT", entrypoint)
    monkeypatch.setattr("braid_simulator.desktop_launcher.IROONLINK3_NODE_MODULES", node_modules)
    monkeypatch.setattr("braid_simulator.desktop_launcher.shutil.which", lambda name: None)

    with pytest.raises(RuntimeError, match="Node.js 18\\+ is required"):
        validate_desktop_runtime()


def test_validate_desktop_runtime_rejects_old_node(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = tmp_path / "iroonlink3"
    entrypoint = root / "server.js"
    node_modules = root / "node_modules"
    node_modules.mkdir(parents=True, exist_ok=True)
    entrypoint.write_text("console.log('ok');", encoding="utf-8")
    monkeypatch.setattr("braid_simulator.desktop_launcher.IROONLINK3_ROOT", root)
    monkeypatch.setattr("braid_simulator.desktop_launcher.IROONLINK3_ENTRYPOINT", entrypoint)
    monkeypatch.setattr("braid_simulator.desktop_launcher.IROONLINK3_NODE_MODULES", node_modules)
    monkeypatch.setattr("braid_simulator.desktop_launcher.shutil.which", lambda name: "/usr/bin/node" if name == "node" else None)
    monkeypatch.setattr(
        "braid_simulator.desktop_launcher.subprocess.run",
        lambda *args, **kwargs: subprocess.CompletedProcess(args[0], 0, stdout="v16.20.2\n"),
    )

    with pytest.raises(RuntimeError, match="Node.js 18\\+ is required"):
        validate_desktop_runtime()


def test_parse_node_major_version_accepts_standard_version_strings() -> None:
    assert parse_node_major_version("v20.11.1\n") == 20
    assert parse_node_major_version("18.19.0") == 18


def test_parse_node_major_version_rejects_unexpected_version_strings() -> None:
    assert parse_node_major_version("") is None
    assert parse_node_major_version("node-20") is None


def test_ensure_port_available_rejects_untracked_port(monkeypatch: pytest.MonkeyPatch) -> None:
    service = ServiceCommand(
        label="Website",
        command=["python", "-m", "http.server", "8080"],
        cwd=REPO_ROOT,
        host="127.0.0.1",
        port=8080,
    )
    monkeypatch.setattr("braid_simulator.desktop_launcher.is_port_open", lambda host, port: True)

    with pytest.raises(RuntimeError, match="Website port 8080 is already in use"):
        ensure_port_available(service, process=None)


def test_ensure_port_available_allows_live_tracked_process(monkeypatch: pytest.MonkeyPatch) -> None:
    service = ServiceCommand(
        label="Control Room",
        command=["node", "server.js"],
        cwd=IROONLINK3_ROOT,
        host="127.0.0.1",
        port=3000,
    )

    class LiveProcess:
        def poll(self) -> int | None:
            return None

    monkeypatch.setattr("braid_simulator.desktop_launcher.is_port_open", lambda host, port: True)

    ensure_port_available(service, process=cast(subprocess.Popen[bytes], LiveProcess()))


def test_cli_auto_mode_falls_back_to_headless(monkeypatch: pytest.MonkeyPatch) -> None:
    runner = CliRunner()
    recorded: dict[str, object] = {}
    monkeypatch.setattr("braid_simulator.desktop_launcher.has_graphical_display", lambda: False)
    monkeypatch.setattr("braid_simulator.desktop_launcher.load_tk_module", lambda required=False: None)
    monkeypatch.setattr(
        "braid_simulator.desktop_launcher.run_headless",
        lambda site_port, control_room_port, open_browser: recorded.update(
            site_port=site_port,
            control_room_port=control_room_port,
            open_browser=open_browser,
        ),
    )

    result = runner.invoke(_main, ["--site-port", "9090", "--control-room-port", "3100", "--open-browser"])

    assert result.exit_code == 0
    assert "GUI launcher unavailable; starting in headless mode." in result.output
    assert recorded == {
        "site_port": 9090,
        "control_room_port": 3100,
        "open_browser": True,
    }
