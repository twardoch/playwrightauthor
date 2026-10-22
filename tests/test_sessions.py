# this_file: tests/test_sessions.py
"""Context-oriented sessions own their browser and never borrow arbitrary tabs."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from playwrightauthor import AsyncBrowserSession, BrowserSession
from playwrightauthor.session_errors import (
    AuthenticationRequired,
    BackendUnsupported,
    ProfileBusy,
)


@pytest.fixture
def sync_runtime(monkeypatch):
    context = MagicMock()
    playwright = MagicMock()
    playwright.chromium.launch_persistent_context.return_value = context
    playwright.firefox.launch_persistent_context.return_value = context
    monkeypatch.setattr(
        "playwrightauthor.sessions.sync_playwright",
        lambda: MagicMock(start=MagicMock(return_value=playwright)),
    )
    return playwright, context


@pytest.mark.parametrize("engine", ["chromium", "firefox"])
def test_sync_session_owns_context_and_separates_task_pages(
    tmp_path, sync_runtime, engine
):
    playwright, context = sync_runtime
    with BrowserSession(
        engine=engine, profile="primary", profile_root=tmp_path
    ) as session:
        assert session.context is context
        assert session.new_page() is context.new_page.return_value
        assert session.get_page() is context.new_page.return_value
        assert session.auth_status() is None
        assert session.profile_dir == tmp_path / engine / "primary"
        with pytest.raises(ProfileBusy):
            with BrowserSession(
                engine=engine, profile="primary", profile_root=tmp_path
            ):
                pytest.fail("Concurrent writer entered")
    context.close.assert_called_once()
    playwright.stop.assert_called_once()
    launch = getattr(playwright, engine).launch_persistent_context
    assert launch.call_args.kwargs["headless"] is True
    if engine == "chromium":
        assert launch.call_args.kwargs["channel"] == "chromium"
    session.close()
    context.close.assert_called_once()


def test_auto_session_fails_without_probe_or_on_rejected_auth(tmp_path, sync_runtime):
    with pytest.raises(ValueError, match="auth_probe"):
        BrowserSession(engine="chromium", mode="auto", profile_root=tmp_path)
    playwright, context = sync_runtime
    with pytest.raises(AuthenticationRequired) as error:
        with BrowserSession(
            engine="chromium",
            mode="auto",
            auth_probe=lambda context: False,
            profile_root=tmp_path,
        ):
            pytest.fail("Unauthenticated auto session entered")
    assert error.value.code == "AUTH_REQUIRED"
    context.close.assert_called_once()
    playwright.stop.assert_called_once()
    with BrowserSession(engine="chromium", profile_root=tmp_path):
        pass


@pytest.mark.parametrize(
    "engine,mode",
    [
        ("lightpanda", "headless"),
        ("chrome", "hidden"),
        ("safari", "headless"),
        ("msedge", "headless"),
        ("webkit", "headless"),
    ],
)
def test_session_rejects_unimplemented_backends_and_modes(engine, mode):
    with pytest.raises(BackendUnsupported):
        BrowserSession(engine=engine, mode=mode)


def test_session_startup_failure_and_body_error_release_lease(tmp_path, sync_runtime):
    playwright, context = sync_runtime
    playwright.chromium.launch_persistent_context.side_effect = RuntimeError(
        "failed startup"
    )
    with pytest.raises(RuntimeError, match="failed startup"):
        with BrowserSession(engine="chromium", profile_root=tmp_path):
            pass
    playwright.stop.assert_called_once()
    playwright.chromium.launch_persistent_context.side_effect = None
    with pytest.raises(ValueError, match="body"):
        with BrowserSession(engine="chromium", profile_root=tmp_path):
            raise ValueError("body")
    context.close.assert_called_once()


@pytest.fixture
def async_runtime(monkeypatch):
    context = MagicMock(close=AsyncMock(), new_page=AsyncMock())
    playwright = MagicMock(stop=AsyncMock())
    playwright.chromium.launch_persistent_context = AsyncMock(return_value=context)
    playwright.firefox.launch_persistent_context = AsyncMock(return_value=context)
    monkeypatch.setattr(
        "playwrightauthor.sessions.async_playwright",
        lambda: MagicMock(start=AsyncMock(return_value=playwright)),
    )
    return playwright, context


@pytest.mark.anyio
async def test_async_session_auth_new_pages_and_cleanup(tmp_path, async_runtime):
    playwright, context = async_runtime
    probe = AsyncMock(return_value=True)
    async with AsyncBrowserSession(
        engine="chromium", mode="auto", auth_probe=probe, profile_root=tmp_path
    ) as session:
        assert session.context is context
        assert await session.new_page() is context.new_page.return_value
        assert await session.get_page() is context.new_page.return_value
        assert await session.auth_status() is True
        assert probe.await_count == 2
    context.close.assert_awaited_once()
    playwright.stop.assert_awaited_once()
    await session.close()
    context.close.assert_awaited_once()


@pytest.mark.anyio
async def test_async_startup_cancellation_releases_driver_and_lease(
    tmp_path, async_runtime
):
    import asyncio

    playwright, context = async_runtime
    playwright.chromium.launch_persistent_context.side_effect = asyncio.CancelledError
    with pytest.raises(asyncio.CancelledError):
        async with AsyncBrowserSession(engine="chromium", profile_root=tmp_path):
            pytest.fail("Cancelled startup entered")
    playwright.stop.assert_awaited_once()
    playwright.chromium.launch_persistent_context.side_effect = None
    async with AsyncBrowserSession(engine="chromium", profile_root=tmp_path):
        pass
    context.close.assert_awaited_once()


@pytest.mark.anyio
async def test_async_close_cancellation_keeps_profile_locked_until_cleanup(
    tmp_path, async_runtime
):
    import asyncio

    from playwrightauthor.profiles import ProfileLease

    playwright, context = async_runtime
    closing = asyncio.Event()
    finish = asyncio.Event()

    async def close_context():
        closing.set()
        await finish.wait()

    context.close.side_effect = close_context
    session = AsyncBrowserSession(engine="chromium", profile_root=tmp_path)
    await session.__aenter__()
    close = asyncio.create_task(session.close())
    await closing.wait()
    close.cancel()
    await asyncio.sleep(0)
    contender = ProfileLease(session.profile_dir)
    with pytest.raises(ProfileBusy):
        contender.acquire()
    with pytest.raises(ProfileBusy):
        await session.__aenter__()
    finish.set()
    with pytest.raises(asyncio.CancelledError):
        await close
    playwright.stop.assert_awaited_once()
    contender.acquire()
    contender.release()


def test_sync_cleanup_failure_still_stops_driver_and_releases_lock(
    tmp_path, sync_runtime
):
    from playwrightauthor.profiles import ProfileLease

    playwright, context = sync_runtime
    context.close.side_effect = RuntimeError("close failed")
    with pytest.raises(RuntimeError, match="close failed"):
        with BrowserSession(engine="chromium", profile_root=tmp_path) as session:
            pass
    playwright.stop.assert_called_once()
    contender = ProfileLease(session.profile_dir)
    contender.acquire()
    contender.release()


def test_nested_sync_profiles_share_driver_but_close_separate_contexts(
    tmp_path, sync_runtime
):
    playwright, context = sync_runtime
    second_context = MagicMock()
    playwright.chromium.launch_persistent_context.side_effect = [
        context,
        second_context,
    ]
    with BrowserSession(engine="chromium", profile="first", profile_root=tmp_path):
        with BrowserSession(engine="chromium", profile="second", profile_root=tmp_path):
            pass
        second_context.close.assert_called_once()
        context.close.assert_not_called()
        playwright.stop.assert_not_called()
    context.close.assert_called_once()
    playwright.stop.assert_called_once()


def test_session_options_reject_identity_flags_and_binary_overrides(
    tmp_path, sync_runtime
):
    from playwrightauthor.config import PlaywrightAuthorConfig
    from playwrightauthor.session_errors import EngineUnavailable

    config = PlaywrightAuthorConfig()
    config.browser.args = ["--headless=false"]
    with pytest.raises(ValueError, match="managed"):
        BrowserSession(engine="chromium", config=config, profile_root=tmp_path)
    for engine in ("chromium", "firefox"):
        with pytest.raises(ValueError, match="executable override"):
            BrowserSession(
                engine=engine, executable_path=tmp_path / "custom"
            ).launch_options()
    with pytest.raises(EngineUnavailable):
        BrowserSession(executable_path=tmp_path / "missing").launch_options()
    binary = tmp_path / "ordinary-browser"
    binary.touch()
    with pytest.raises(EngineUnavailable, match="Chrome for Testing"):
        BrowserSession(executable_path=binary).launch_options()


def test_session_probe_contract_and_inactive_pages(tmp_path, sync_runtime):
    session = BrowserSession(
        engine="chromium", auth_probe=lambda context: None, profile_root=tmp_path
    )
    with pytest.raises(RuntimeError, match="Enter"):
        session.new_page()
    with pytest.raises(RuntimeError, match="Enter"):
        session.auth_status()
    with session:
        with pytest.raises(TypeError, match="bool"):
            session.auth_status()


@pytest.mark.parametrize(
    "message,code",
    [
        ("Executable doesn't exist at missing", "ENGINE_UNAVAILABLE"),
        ("Failed to create a ProcessSingleton", "PROFILE_BUSY"),
        ("browser exited", "BROWSER_SESSION_FAILED"),
    ],
)
def test_launch_failure_preserves_structured_code_without_private_arguments(
    message, code
):
    from playwright.sync_api import Error

    from playwrightauthor.session_options import launch_failure

    error = launch_failure(Error(message), "chromium")
    assert error.code == code
    assert "missing" not in str(error)


@pytest.mark.anyio
async def test_cancelled_option_preparation_keeps_profile_locked_until_thread_finishes(
    tmp_path, async_runtime, monkeypatch
):
    import asyncio
    import threading

    from playwrightauthor.profiles import ProfileLease

    started, finish = threading.Event(), threading.Event()
    session = AsyncBrowserSession(engine="chromium", profile_root=tmp_path)

    def prepare():
        started.set()
        assert finish.wait(5), "Fixture preparation thread did not finish"
        return "chromium", {"headless": True}

    monkeypatch.setattr(session, "launch_options", prepare)
    task = asyncio.create_task(session.__aenter__())
    assert await asyncio.to_thread(started.wait, 2)
    task.cancel()
    await asyncio.sleep(0.01)
    contender = ProfileLease(session.profile_dir)
    try:
        with pytest.raises(ProfileBusy):
            contender.acquire()
    finally:
        finish.set()
        with pytest.raises(asyncio.CancelledError):
            await task
    contender.acquire()
    contender.release()
