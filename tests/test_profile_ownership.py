# this_file: tests/test_profile_ownership.py
"""Profile identity and lease regressions, independent of browser fixtures."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from playwrightauthor.profiles import (
    ProfileBusy,
    ProfileLease,
    validate_attachment,
    validate_profile,
)


@pytest.mark.parametrize(
    "profile", ["", ".", "..", "../other", "/tmp/foo", "a/b", "a\\b", "a b"]
)
def test_profile_rejects_unsafe_names(profile):
    with pytest.raises(ValueError):
        validate_profile(profile)


def test_profile_lease_rejects_another_writer_and_releases(tmp_path):
    first = ProfileLease(tmp_path / "profiles" / "chrome" / "primary")
    second = ProfileLease(first.directory)
    first.acquire()
    try:
        with pytest.raises(ProfileBusy) as error:
            second.acquire()
        assert error.value.code == "PROFILE_BUSY"
    finally:
        first.release()
    second.acquire()
    second.release()
    second.release()
    assert first.directory.stat().st_mode & 0o777 == 0o700


def test_attachment_requires_exact_profile_mode_and_executable(tmp_path):
    binary = tmp_path / "chrome-testing"
    directory = tmp_path / "primary"
    process = MagicMock()
    process.exe.return_value = str(binary)
    process.cmdline.return_value = [
        str(binary),
        f"--user-data-dir={directory}",
        "--headless=new",
    ]
    validate_attachment(process, directory, binary, True)
    for target, mode, executable in [
        (tmp_path / "other", True, binary),
        (directory, False, binary),
        (directory, True, Path("/other/chrome")),
    ]:
        with pytest.raises(ProfileBusy):
            validate_attachment(process, target, executable, mode)
    process.terminate.assert_not_called()


def test_attachment_rejects_uninspectable_or_duplicate_flags(tmp_path):
    process = MagicMock()
    process.exe.return_value = str(tmp_path / "chrome")
    process.cmdline.return_value = [
        f"--user-data-dir={tmp_path}",
        "--user-data-dir=/other",
    ]
    with pytest.raises(ProfileBusy):
        validate_attachment(process, tmp_path, tmp_path / "chrome", False)
    process.cmdline.side_effect = PermissionError
    with pytest.raises(ProfileBusy):
        validate_attachment(process, tmp_path, tmp_path / "chrome", False)


@pytest.mark.parametrize("entrypoint", ["ensure_browser", "launch_browser"])
def test_legacy_manager_rejects_wrong_profile_before_attach(
    tmp_path, monkeypatch, entrypoint
):
    from playwrightauthor import browser_manager
    from playwrightauthor.config import PlaywrightAuthorConfig

    process = MagicMock()
    process.exe.return_value = str(tmp_path / "chrome-testing")
    process.cmdline.return_value = [f"--user-data-dir={tmp_path / 'other'}"]
    monkeypatch.setattr(browser_manager, "get_chrome_process", lambda port: process)
    monkeypatch.setattr(
        browser_manager,
        "find_chrome_executable",
        lambda logger: tmp_path / "chrome-testing",
    )
    monkeypatch.setattr(browser_manager, "get_data_dir", lambda: tmp_path)
    monkeypatch.setattr(
        browser_manager,
        "get_state_manager",
        lambda: MagicMock(get_profile_debug_port=MagicMock(return_value=9229)),
    )
    with pytest.raises(ProfileBusy):
        getattr(browser_manager, entrypoint)(
            profile="primary", config=PlaywrightAuthorConfig()
        )
    process.terminate.assert_not_called()


@pytest.mark.parametrize(
    "args", [["--user-data-dir={directory}"], ["--user-data-dir", "{directory}"]]
)
def test_live_profile_process_blocks_relaunch_without_termination(
    tmp_path, monkeypatch, args
):
    from playwrightauthor.profiles import reject_running_profile

    process = MagicMock(
        info={"cmdline": [arg.format(directory=tmp_path) for arg in args]}
    )
    monkeypatch.setattr(
        "playwrightauthor.profiles.psutil.process_iter", lambda attrs: [process]
    )
    with pytest.raises(ProfileBusy):
        reject_running_profile(tmp_path)
    reject_running_profile(tmp_path / "other")
    process.terminate.assert_not_called()


def test_exact_debug_port_discovery_does_not_match_prefix(monkeypatch):
    from playwrightauthor.browser.process import get_chrome_process

    process = MagicMock(
        info={
            "name": "Google Chrome for Testing",
            "cmdline": ["--remote-debugging-port=92220"],
            "exe": "/Applications/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing",
        }
    )
    monkeypatch.setattr(
        "playwrightauthor.browser.process.psutil.process_iter", lambda attrs: [process]
    )
    assert get_chrome_process(9222) is None
    assert get_chrome_process(92220) is process


def test_unverified_listening_debug_port_is_not_reused():
    import socket

    from playwrightauthor.profiles import require_free_debug_port

    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        listener.listen()
        port = listener.getsockname()[1]
        with pytest.raises(ProfileBusy, match="occupied"):
            require_free_debug_port(port)
    require_free_debug_port(port)
