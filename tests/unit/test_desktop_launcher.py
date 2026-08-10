from __future__ import annotations

import subprocess
from typing import cast

import pytest

from braid_simulator.desktop_launcher import (
    DEFAULT_CONTROL_ROOM_PORT,
    DEFAULT_SITE_PORT,
    IROONLINK3_ROOT,
    REPO_ROOT,
    ServiceCommand,
    ensure_port_available,
    make_service_commands,
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


def test_validate_desktop_runtime_accepts_current_repo(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("braid_simulator.desktop_launcher.shutil.which", lambda name: "/usr/bin/node" if name == "node" else None)

    validate_desktop_runtime()


def test_validate_desktop_runtime_requires_node(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("braid_simulator.desktop_launcher.shutil.which", lambda name: None)

    with pytest.raises(RuntimeError, match="Node.js 18\\+ is required"):
        validate_desktop_runtime()


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
