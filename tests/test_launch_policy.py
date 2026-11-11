# this_file: tests/test_launch_policy.py
"""Regression tests for issue 340's legacy launch policy."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from playwrightauthor import AsyncBrowser, Browser, browser_manager
from playwrightauthor.browser.launcher import launch_chrome
from playwrightauthor.config import PlaywrightAuthorConfig


@pytest.mark.parametrize("entrypoint", ["ensure_browser", "launch_browser"])
@pytest.mark.parametrize("headless", [True, False])
def test_launch_policy_forwards_effective_config(tmp_path, entrypoint, headless):
    config = PlaywrightAuthorConfig()
    config.browser.headless = headless
    config.browser.args = ["--lang=en-GB"]
    with (
        patch.object(browser_manager, "require_free_debug_port"),
        patch.object(
            browser_manager,
            "get_state_manager",
            return_value=MagicMock(get_profile_debug_port=MagicMock(return_value=9229)),
        ),
        patch.object(
            browser_manager, "get_chrome_process", return_value=None
        ) as lookup,
        patch.object(browser_manager, "get_data_dir", return_value=tmp_path),
        patch.object(
            browser_manager,
            "find_chrome_executable",
            return_value=tmp_path / "chrome-testing",
        ),
        patch.object(browser_manager, "launch_chrome_with_retry") as launch,
    ):
        getattr(browser_manager, entrypoint)(profile="policy", config=config)
    args = launch.call_args.kwargs["extra_args"]
    assert ("--headless=new" in args) == headless
    assert "--lang=en-GB" in args
    assert config.browser.args == ["--lang=en-GB"], "Do not mutate shared configuration"
    assert all(call.args for call in lookup.call_args_list), (
        "Never discover an arbitrary process to kill"
    )


@pytest.mark.parametrize("wrapper", [Browser, AsyncBrowser])
def test_headless_session_never_notifies(wrapper):
    instance = wrapper()
    instance.config = PlaywrightAuthorConfig()
    instance.config.browser.headless = True
    with patch("playwrightauthor.author.notify_interactive_task") as notify:
        assert instance._notify_interactive_task() is False
    notify.assert_not_called()


@pytest.mark.anyio
async def test_async_browser_exposes_awaitable_existing_context_page():
    page = MagicMock(url="https://example.test/")
    context = MagicMock(pages=[page], new_page=AsyncMock())
    browser = MagicMock(contexts=[context], close=AsyncMock())
    playwright = MagicMock(stop=AsyncMock())
    instance = AsyncBrowser(suppress_dialog=True)
    instance.config = PlaywrightAuthorConfig()
    instance.config.monitoring.enabled = False
    with (
        patch(
            "playwrightauthor.author.get_async_playwright",
            return_value=MagicMock(start=AsyncMock(return_value=playwright)),
        ),
        patch(
            "playwrightauthor.author.get_engine_async",
            return_value=MagicMock(start_async=AsyncMock(return_value=browser)),
        ),
        patch.object(instance.state_manager, "get_profile", return_value={}),
        patch.object(instance.state_manager, "set_profile"),
    ):
        async with instance as connected:
            assert await connected.get_page() is page
            context.pages = []
            assert await connected.get_page() is context.new_page.return_value
            context.new_page.assert_awaited_once()
            context.pages = [MagicMock(url="chrome-extension://extension")]
            assert await connected.get_page() is context.new_page.return_value
            browser.contexts = []
            browser.new_page = AsyncMock()
            assert await connected.get_page() is browser.new_page.return_value
            browser.new_page.assert_awaited_once()


def test_launcher_does_not_modify_browser_bundle(tmp_path):
    binary = tmp_path / "chrome-testing"
    binary.touch()
    process = MagicMock()
    process.poll.return_value = None
    with (
        patch(
            "playwrightauthor.browser.launcher.subprocess.Popen", return_value=process
        ) as popen,
        patch("playwrightauthor.browser.launcher.subprocess.run") as run,
        patch("playwrightauthor.browser.launcher.time.sleep"),
        patch(
            "playwrightauthor.browser.launcher.wait_for_process_start",
            return_value=process,
        ),
    ):
        launch_chrome(
            binary,
            tmp_path / "profile",
            9229,
            MagicMock(),
            extra_args=["--headless=new"],
        )
    run.assert_not_called()
    command = popen.call_args.args[0]
    assert "--headless=new" in command
    assert "--remote-debugging-address=127.0.0.1" in command


@pytest.mark.parametrize("headless", [True, False])
def test_cli_run_notifies_only_for_visible_mode(headless):
    from playwrightauthor.__main__ import Cli

    config = PlaywrightAuthorConfig()
    config.browser.headless = headless
    with (
        patch("playwrightauthor.__main__.get_config", return_value=config),
        patch("playwrightauthor.__main__.get_state_manager") as state,
        patch(
            "playwrightauthor.__main__.launch_browser",
            return_value=("chrome", "profile"),
        ) as launch,
        patch("playwrightauthor.__main__.notify_interactive_task") as notify,
        patch("playwrightauthor.__main__.get_chrome_process", return_value=None),
    ):
        state.return_value.get_profile_debug_port.return_value = 9229
        Cli().run(profile="policy")
    assert notify.call_count == (0 if headless else 1)
    assert launch.call_args.kwargs["config"] is config


def test_cli_run_when_browser_already_running_then_no_dialog():
    from playwrightauthor.__main__ import Cli

    config = PlaywrightAuthorConfig()
    config.browser.headless = False
    with (
        patch("playwrightauthor.__main__.get_config", return_value=config),
        patch("playwrightauthor.__main__.get_state_manager") as state,
        patch(
            "playwrightauthor.__main__.launch_browser",
            return_value=("chrome", "profile"),
        ),
        patch("playwrightauthor.__main__.notify_interactive_task") as notify,
        patch(
            "playwrightauthor.__main__.get_chrome_process", return_value=MagicMock()
        ),
    ):
        state.return_value.get_profile_debug_port.return_value = 9229
        Cli().run(profile="policy")
    notify.assert_not_called()


@pytest.mark.parametrize("wrapper", [Browser, AsyncBrowser])
@pytest.mark.parametrize("running", [True, False])
def test_visible_session_notifies_only_when_browser_not_running(wrapper, running):
    instance = wrapper()
    instance.config = PlaywrightAuthorConfig()
    instance.config.browser.headless = False
    with (
        patch("playwrightauthor.author.notify_interactive_task", return_value=True) as notify,
        patch(
            "playwrightauthor.author.get_chrome_process",
            return_value=MagicMock() if running else None,
        ),
        patch.object(instance.state_manager, "get_profile_debug_port", return_value=9333),
    ):
        instance._notify_interactive_task()
    assert notify.call_count == (0 if running else 1), (
        "Dialog must be skipped when the profile's browser is already open"
    )
