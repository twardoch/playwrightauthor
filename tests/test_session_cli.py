# this_file: tests/test_session_cli.py
"""CLI status is read-only and stop requests are restricted to owned sessions."""

from unittest.mock import MagicMock

import pytest


def test_status_does_not_launch_or_create_a_profile(tmp_path):
    from playwrightauthor.session_cli import command

    result = command("status", engine="chromium", profile_root=str(tmp_path))
    assert result["status"] == "stopped" and result["auth_status"] is None
    assert not list(tmp_path.iterdir()), "Status must not launch or mutate profiles"


def test_stop_without_owner_does_not_signal_processes(tmp_path):
    from playwrightauthor.session_cli import command

    assert (
        command("stop", engine="chromium", profile_root=str(tmp_path))["status"]
        == "stopped"
    )


def test_run_closes_owned_session_and_removes_control_record(tmp_path, monkeypatch):
    from playwrightauthor import session_cli

    session = MagicMock()
    session.__enter__.return_value = session
    session.new_page.return_value.title.return_value = "fixture"
    session.new_page.return_value.is_closed.return_value = False
    monkeypatch.setattr(session_cli, "BrowserSession", lambda **kwargs: session)
    result = session_cli.command("run", engine="chromium", profile_root=str(tmp_path))
    assert result["title"] == "fixture"
    session.__exit__.assert_called_once()
    assert not list(tmp_path.rglob("cli-owner.json"))


def test_auto_requires_service_probe_and_never_launches_interactive(tmp_path):
    from playwrightauthor.session_cli import command

    with pytest.raises(ValueError, match="auth_url"):
        command("run", engine="chromium", mode="auto", profile_root=str(tmp_path))


def test_invalid_action_rejected_before_launch():
    from playwrightauthor.session_cli import command

    with pytest.raises(ValueError, match="action"):
        command("remove")


def test_invalid_owner_token_cannot_create_a_stop_file(tmp_path):
    import json

    import psutil

    from playwrightauthor.session_cli import command

    path = tmp_path / "chromium/default/cli-owner.json"
    path.parent.mkdir(parents=True)
    path.write_text(
        json.dumps(
            {
                "pid": psutil.Process().pid,
                "created": psutil.Process().create_time(),
                "token": "../../outside",
            }
        )
    )
    assert (
        command("stop", engine="chromium", profile_root=str(tmp_path))["status"]
        == "stopped"
    )
    assert not list(tmp_path.rglob("*.stop"))


def test_stale_owner_is_not_reported_running(tmp_path):
    import json

    import psutil

    from playwrightauthor.session_cli import command

    path = tmp_path / "chromium/default/cli-owner.json"
    path.parent.mkdir(parents=True)
    path.write_text(
        json.dumps({"pid": psutil.Process().pid, "created": 0, "token": "0" * 32})
    )
    assert (
        command("status", engine="chromium", profile_root=str(tmp_path))["status"]
        == "stopped"
    )


def test_login_is_explicit_interactive_without_modal_notice(tmp_path, monkeypatch):
    from playwrightauthor import session_cli

    session = MagicMock()
    session.__enter__.return_value = session
    session.new_page.return_value.is_closed.return_value = False
    session.auth_status.return_value = None
    factory = MagicMock(return_value=session)
    monkeypatch.setattr(session_cli, "BrowserSession", factory)
    result = session_cli.command(
        "login", engine="chromium", profile_root=str(tmp_path), hold_seconds=0
    )
    assert factory.call_args.kwargs["mode"] == "interactive"
    assert factory.call_args.kwargs["suppress_dialog"] is True
    assert result["auth_status"] is None, "Unprobed sign-in must remain unknown"


def test_service_probe_rejects_redirect_and_closes_its_tab():
    from playwrightauthor.session_cli import _probe

    page = MagicMock(url="https://example.com/login")
    page.goto.return_value.status = 200
    context = MagicMock()
    context.new_page.return_value = page
    assert _probe("https://example.com/settings", "#account")(context) is False
    page.close.assert_called_once()


def test_run_failure_closes_context_and_removes_control_record(tmp_path, monkeypatch):
    from playwrightauthor import session_cli

    session = MagicMock()
    session.__enter__.return_value = session
    session.new_page.return_value.goto.side_effect = RuntimeError("fixture failure")
    monkeypatch.setattr(session_cli, "BrowserSession", lambda **kwargs: session)
    with pytest.raises(RuntimeError, match="fixture failure"):
        session_cli.command("run", engine="chromium", profile_root=str(tmp_path))
    session.__exit__.assert_called_once()
    assert not list(tmp_path.rglob("cli-owner.json"))


def test_stop_reports_foreign_profile_without_writing_requests(tmp_path, monkeypatch):
    from playwrightauthor import session_cli
    from playwrightauthor.session_errors import ProfileBusy

    (tmp_path / "chromium/default").mkdir(parents=True)

    def foreign(directory):
        raise ProfileBusy("Fixture foreign browser")

    monkeypatch.setattr(session_cli, "reject_running_profile", foreign)
    result = session_cli.command("stop", engine="chromium", profile_root=str(tmp_path))
    assert result["status"] == "profile_in_use"
    assert not list(tmp_path.rglob("*.stop")), (
        "Unowned processes cannot receive stop requests"
    )


def test_service_probe_requires_visible_account_marker():
    from playwright.sync_api import TimeoutError

    from playwrightauthor.session_cli import _probe

    page = MagicMock(url="https://example.com/settings")
    page.goto.return_value.status = 200
    context = MagicMock()
    context.new_page.return_value = page
    probe = _probe("https://example.com/settings", "#account")
    assert probe(context) is True
    page.locator.return_value.first.wait_for.side_effect = TimeoutError("fixture")
    assert probe(context) is False
    assert page.close.call_count == 2


def test_owned_stop_request_is_private_and_token_scoped(tmp_path):
    import json

    import psutil

    from playwrightauthor.session_cli import command

    root = tmp_path / "chromium/default"
    root.mkdir(parents=True)
    token = "a" * 32
    (root / "cli-owner.json").write_text(
        json.dumps(
            {
                "pid": psutil.Process().pid,
                "created": psutil.Process().create_time(),
                "token": token,
            }
        )
    )
    assert (
        command("status", engine="chromium", profile_root=str(tmp_path))["status"]
        == "running"
    )
    assert (
        command("stop", engine="chromium", profile_root=str(tmp_path))["status"]
        == "stop_requested"
    )
    request = root / (token + ".stop")
    assert request.stat().st_mode & 0o777 == 0o600


def test_cli_login_stop_hint_preserves_custom_profile_root(
    tmp_path, monkeypatch, capsys
):
    from playwrightauthor.__main__ import Cli

    monkeypatch.setattr(
        "playwrightauthor.session_cli.command",
        lambda *args, **kwargs: {"status": "closed"},
    )
    custom = str(tmp_path / "profiles with spaces")
    Cli().session(
        "login",
        engine="chromium",
        profile="secondary",
        profile_root=custom,
        hold_seconds=0,
    )
    hint = " ".join(capsys.readouterr().err.split())
    assert "--profile-root=" in hint and "profiles with spaces" in hint
    assert "--profile=secondary" in hint
