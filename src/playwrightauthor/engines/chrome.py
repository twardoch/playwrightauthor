# this_file: src/playwrightauthor/engines/chrome.py

"""Chrome for Testing engine adapter.

Wraps the existing CfT launch + CDP connect flow.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from playwrightauthor.browser_manager import ensure_browser
from playwrightauthor.connection import (
    async_connect_with_retry,
    connect_with_retry,
)
from playwrightauthor.engine import (
    AsyncEngineAdapter,
    EngineAdapter,
)

if TYPE_CHECKING:
    from playwright.async_api import Browser as AsyncBrowser
    from playwright.sync_api import Browser as SyncBrowser

    from playwrightauthor.config import PlaywrightAuthorConfig


class ChromeEngineAdapter(EngineAdapter):
    """Chrome for Testing engine using CDP connect."""

    def __init__(
        self,
        config: PlaywrightAuthorConfig,
        profile: str,
        verbose: bool = False,
    ) -> None:
        """Initialize Chrome engine adapter.

        Args:
            config: BrowserConfig instance
            profile: Profile name
            verbose: Enable verbose logging
        """
        self.config = config
        self.profile = profile
        self.verbose = verbose

    def ensure_browser(self) -> None:
        """Ensure Chrome for Testing binary is available and launched."""
        ensure_browser(
            verbose=self.verbose,
            profile=self.profile,
        )

    def start(self, playwright_chromium) -> SyncBrowser:
        """Start Chrome browser and connect over CDP.

        Args:
            playwright_chromium: Playwright chromium API instance

        Returns:
            Playwright Browser instance connected over CDP.
        """
        self.ensure_browser()
        debug_port = self.config.browser.debug_port
        max_retries = self.config.network.retry_attempts
        retry_delay = self.config.network.retry_delay
        timeout = self.config.browser.timeout // 1000

        browser = connect_with_retry(
            playwright_chromium,
            debug_port,
            max_retries=max_retries,
            retry_delay=retry_delay,
            timeout=timeout,
        )
        return browser

    def __repr__(self) -> str:
        return (
            f"ChromeEngineAdapter(profile={self.profile!r}, "
            f"port={self.config.browser.debug_port})"
        )


class AsyncChromeEngineAdapter(AsyncEngineAdapter):
    """Async Chrome for Testing engine using CDP connect."""

    def __init__(
        self,
        config: PlaywrightAuthorConfig,
        profile: str,
        verbose: bool = False,
    ) -> None:
        """Initialize async Chrome engine adapter.

        Args:
            config: BrowserConfig instance
            profile: Profile name
            verbose: Enable verbose logging
        """
        self.config = config
        self.profile = profile
        self.verbose = verbose

    async def ensure_browser_async(self) -> None:
        """Ensure Chrome for Testing binary is available and launched (runs sync launch)."""
        ensure_browser(
            verbose=self.verbose,
            profile=self.profile,
        )

    async def start_async(self, playwright_chromium) -> AsyncBrowser:
        """Start Chrome browser and connect over CDP (async wrapper).

        Args:
            playwright_chromium: Playwright async chromium API instance

        Returns:
            Async Playwright Browser instance connected over CDP.
        """
        await self.ensure_browser_async()
        debug_port = self.config.browser.debug_port
        max_retries = self.config.network.retry_attempts
        retry_delay = self.config.network.retry_delay
        timeout = self.config.browser.timeout // 1000

        browser = await async_connect_with_retry(
            playwright_chromium,
            debug_port,
            max_retries=max_retries,
            retry_delay=retry_delay,
            timeout=timeout,
        )
        return browser

    def __repr__(self) -> str:
        return (
            f"AsyncChromeEngineAdapter(profile={self.profile!r}, "
            f"port={self.config.browser.debug_port})"
        )
