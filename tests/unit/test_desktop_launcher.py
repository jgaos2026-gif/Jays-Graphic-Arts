from __future__ import annotations

from braid_simulator.desktop_launcher import (
    DEFAULT_CONTROL_ROOM_PORT,
    DEFAULT_SITE_PORT,
    IROONLINK3_ROOT,
    REPO_ROOT,
    make_service_commands,
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
