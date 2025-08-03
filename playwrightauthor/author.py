#!/usr/bin/env -S uv run -s
# /// script
# dependencies = ["playwright"]
# ///
# this_file: playwrightauthor/author.py

"""The core Browser and AsyncBrowser classes."""

from playwright.sync_api import (
    sync_playwright,
    Playwright,
    Browser as PlaywrightBrowser,
)
from playwright.async_api import (
    async_playwright,
    Playwright as AsyncPlaywright,
    Browser as AsyncPlaywrightBrowser,
)
from .browser_manager import ensure_browser, _DEBUGGING_PORT
from .utils.logger import configure as configure_logger


class Browser:
    """
    A sync context manager for an authenticated Playwright Browser.

    This class handles the setup and teardown of a Playwright browser instance that is connected
    to a persistent browser session. This allows you to maintain your login sessions and other
    browser data between runs.

    Args:
        verbose (bool, optional): Whether to enable verbose logging. Defaults to False.
    """
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.logger = configure_logger(verbose)
        self.playwright: Playwright | None = None
        self.browser: PlaywrightBrowser | None = None

    def __enter__(self) -> PlaywrightBrowser:
        self.logger.info("Starting sync browser session...")
        ensure_browser(self.verbose)
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.connect_over_cdp(f"http://localhost:{_DEBUGGING_PORT}")
        self.logger.info("Sync browser session started.")
        return self.browser

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        self.logger.info("Sync browser session closed.")

class AsyncBrowser:
    """
    An async context manager for an authenticated Playwright Browser.

    This class is the asynchronous version of the Browser class. It handles the setup and teardown
    of a Playwright browser instance that is connected to a persistent browser session. This allows
    you to maintain your login sessions and other browser data between runs.

    Args:
        verbose (bool, optional): Whether to enable verbose logging. Defaults to False.
    """
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.logger = configure_logger(verbose)
        self.playwright: AsyncPlaywright | None = None
        self.browser: AsyncPlaywrightBrowser | None = None

    async def __aenter__(self) -> AsyncPlaywrightBrowser:
        self.logger.info("Starting async browser session...")
        ensure_browser(self.verbose)
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.connect_over_cdp(f"http://localhost:{_DEBUGGING_PORT}")
        self.logger.info("Async browser session started.")
        return self.browser

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        self.logger.info("Async browser session closed.")
