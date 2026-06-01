# this_file: tests/test_cli.py

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

from playwrightauthor.__main__ import Cli


def test_status_uses_requested_profile_debug_port(monkeypatch, capsys):
    state_manager = Mock()
    state_manager.get_profile_debug_port.return_value = 9223
    monkeypatch.setattr(
        "playwrightauthor.__main__.get_state_manager", lambda: state_manager
    )
    monkeypatch.setattr(
        "playwrightauthor.__main__.get_config",
        lambda: SimpleNamespace(
            browser=SimpleNamespace(debug_port=9222, engine="chrome")
        ),
    )

    ensure_browser = Mock(
        return_value=(Path("/tmp/chrome"), Path("/tmp/profiles/google-primary"))
    )
    monkeypatch.setattr("playwrightauthor.__main__.ensure_browser", ensure_browser)

    Cli().status(profile="google-primary")

    state_manager.get_profile_debug_port.assert_called_once_with("google-primary", 9222)
    ensure_browser.assert_called_once_with(verbose=False, profile="google-primary")
    output = capsys.readouterr().out
    assert "Profile: google-primary" in output
    assert "Debug Port: 9223" in output
