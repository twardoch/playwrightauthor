# this_file: src/playwrightauthor/sessions.py
"""Owned persistent contexts with one OS-backed lease per engine/account identity.

Legacy Browser/AsyncBrowser CDP wrappers retain their existing defaults. These
additive APIs never attach to a detached process or borrow existing human tabs.
"""

import asyncio
from contextlib import AsyncExitStack, ExitStack
from typing import Any

from playwright.async_api import Error as AsyncPlaywrightError
from playwright.async_api import async_playwright
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright

from .dialognano import notify_interactive_task
from .profiles import reject_running_profile
from .session_errors import AuthenticationRequired, ProfileBusy
from .session_options import SessionOptions, launch_failure
from .session_runtime import sync_driver


async def _finish_task(task: asyncio.Task[Any]) -> Any:
    """Finish owned work before propagating cancellation and releasing its lease."""
    cancellation = None
    while not task.done():
        try:
            await asyncio.shield(task)
        except asyncio.CancelledError as error:
            cancellation = error
    result = task.result()
    if cancellation is not None:
        raise cancellation
    return result


class BrowserSession(SessionOptions):
    """Own one persistent Playwright context; new_page always creates a task tab."""

    context: Any = None
    browser: Any = None
    _stack: ExitStack | None = None

    def __enter__(self) -> "BrowserSession":
        if self._stack is not None:
            raise ProfileBusy("This session is already active.")
        stack = self._stack = ExitStack()
        try:
            self._lease.acquire()
            stack.callback(self._lease.release)
            reject_running_profile(self.profile_dir)
            engine, options = self.launch_options()
            playwright = stack.enter_context(sync_driver(sync_playwright))
            try:
                self.context = getattr(playwright, engine).launch_persistent_context(
                    self.profile_dir, **options
                )
            except PlaywrightError as error:
                raise launch_failure(error, self.engine) from error
            stack.callback(self.context.close)
            self.browser = self.context.browser
            if self.mode == "auto" and not self.auth_status():
                raise AuthenticationRequired(
                    f"Sign in to {self.service or 'the service'} explicitly with engine {self.engine} and profile {self.profile}."
                )
            if self.mode == "interactive":
                notify_interactive_task(
                    task="Complete sign-in or the requested manual browser task.",
                    profile=self.profile,
                    service=self.service,
                    suppress=self.suppress_dialog,
                )
            return self
        except BaseException:
            self.close()
            raise

    def new_page(self) -> Any:
        """Create a task-owned page in the authenticated context."""
        if self.context is None:
            raise RuntimeError("Enter the browser session before requesting a page")
        return self.context.new_page()

    def get_page(self) -> Any:
        """Compatibility spelling that still creates a separate task-owned page."""
        return self.new_page()

    def auth_status(self) -> bool | None:
        """Run the caller's service probe; absent probe means authorization is unknown."""
        if self.auth_probe is None:
            return None
        if self.context is None:
            raise RuntimeError(
                "Enter the browser session before checking authorization"
            )
        result = self.auth_probe(self.context)
        if not isinstance(result, bool):
            raise TypeError("A synchronous auth_probe must return bool")
        return result

    def close(self) -> None:
        """Close the owned context and driver before releasing the profile lease."""
        stack, self._stack = self._stack, None
        try:
            if stack is not None:
                stack.close()
        finally:
            self.context = self.browser = None

    def __exit__(self, *exc: Any) -> None:
        self.close()


class AsyncBrowserSession(SessionOptions):
    """Async counterpart with cleanup on startup cancellation and task failure."""

    context: Any = None
    browser: Any = None
    _stack: AsyncExitStack | None = None
    _cleanup_task: asyncio.Task[None] | None = None

    async def __aenter__(self) -> "AsyncBrowserSession":
        if self._stack is not None:
            raise ProfileBusy("This session is already active.")
        stack = self._stack = AsyncExitStack()
        try:
            self._lease.acquire()
            stack.callback(self._lease.release)
            reject_running_profile(self.profile_dir)
            preparation = asyncio.create_task(asyncio.to_thread(self.launch_options))
            engine, options = await _finish_task(preparation)
            playwright = await async_playwright().start()
            stack.push_async_callback(playwright.stop)
            try:
                self.context = await getattr(
                    playwright, engine
                ).launch_persistent_context(self.profile_dir, **options)
            except AsyncPlaywrightError as error:
                raise launch_failure(error, self.engine) from error
            stack.push_async_callback(self.context.close)
            self.browser = self.context.browser
            if self.mode == "auto" and not await self.auth_status():
                raise AuthenticationRequired(
                    f"Sign in to {self.service or 'the service'} explicitly with engine {self.engine} and profile {self.profile}."
                )
            if self.mode == "interactive":
                notify_interactive_task(
                    task="Complete sign-in or the requested manual browser task.",
                    profile=self.profile,
                    service=self.service,
                    suppress=self.suppress_dialog,
                )
            return self
        except BaseException:
            await self.close()
            raise

    async def new_page(self) -> Any:
        """Create one independent tab; other callers' tabs are never reused."""
        if self.context is None:
            raise RuntimeError("Enter the browser session before requesting a page")
        return await self.context.new_page()

    async def get_page(self) -> Any:
        """Compatibility spelling returning a new task page."""
        return await self.new_page()

    async def auth_status(self) -> bool | None:
        """Run an async service probe without inferring identity from cookie names."""
        if self.auth_probe is None:
            return None
        if self.context is None:
            raise RuntimeError(
                "Enter the browser session before checking authorization"
            )
        result = await self.auth_probe(self.context)
        if not isinstance(result, bool):
            raise TypeError("An asynchronous auth_probe must return bool")
        return result

    async def close(self) -> None:
        """Close owned browser resources even if an earlier cleanup callback fails."""
        stack = self._stack
        try:
            if stack is not None:
                if self._cleanup_task is None:
                    self._cleanup_task = asyncio.create_task(stack.aclose())
                await _finish_task(self._cleanup_task)
        finally:
            self._stack = self._cleanup_task = None
            self.context = self.browser = None

    async def __aexit__(self, *exc: Any) -> None:
        await self.close()
