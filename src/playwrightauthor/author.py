#!/usr/bin/env -S uv run -s
# /// script
# dependencies = ["playwright"]
# ///
# this_file: src/playwrightauthor/author.py

"""The core Browser and AsyncBrowser classes."""

from datetime import datetime
from typing import TYPE_CHECKING

from .browser_manager import ensure_browser
from .config import get_config
from .connection import async_connect_with_retry, connect_with_retry
from .lazy_imports import get_async_playwright, get_sync_playwright
from .state_manager import get_state_manager
from .utils.logger import configure as configure_logger

if TYPE_CHECKING:
    from playwright.async_api import Browser as AsyncPlaywrightBrowser
    from playwright.async_api import Playwright as AsyncPlaywright
    from playwright.sync_api import Browser as PlaywrightBrowser
    from playwright.sync_api import Playwright


class Browser:
    """
    A sync context manager for an authenticated Playwright Browser.

    This class handles the setup and teardown of a Playwright browser instance that is connected
    to a persistent browser session. This allows you to maintain your login sessions and other
    browser data between runs.

    Args:
        verbose (bool, optional): Whether to enable verbose logging. Defaults to False.
        profile (str, optional): Browser profile name to use. Defaults to "default".
    """

    def __init__(self, verbose: bool = False, profile: str = "default"):
        self.verbose = verbose
        self.profile = profile
        self.logger = configure_logger(verbose)
        self.config = get_config()
        self.state_manager = get_state_manager()
        self.playwright: Playwright | None = None
        self.browser: PlaywrightBrowser | None = None

    def __enter__(self) -> "PlaywrightBrowser":
        """
        Enter the context manager and return an authenticated Playwright Browser instance.

        This method automatically handles:
        - Ensuring Chrome for Testing is installed and running
        - Starting the Playwright sync context
        - Connecting to the browser with retry logic and health checks
        - Updating profile usage statistics

        Returns:
            PlaywrightBrowser: A connected Playwright browser instance ready for automation

        Raises:
            BrowserManagerError: If browser setup or connection fails
            NetworkError: If connection to debug port fails
            TimeoutError: If browser startup exceeds configured timeout

        Example:
            ```python
            with Browser(verbose=True) as browser:
                page = browser.new_page()
                page.goto("https://github.com")
                print(page.title())
            ```
        """
        self.logger.info(
            f"Starting sync browser session with profile '{self.profile}'..."
        )
        ensure_browser(self.verbose, profile=self.profile)

        # Use lazy loading for Playwright
        sync_playwright = get_sync_playwright()
        self.playwright = sync_playwright.start()

        # Connect to browser using configured port with health checks and retry logic
        debug_port = self.config.browser.debug_port
        max_retries = self.config.network.retry_attempts
        retry_delay = self.config.network.retry_delay

        self.browser = connect_with_retry(
            self.playwright.chromium,
            debug_port,
            max_retries=max_retries,
            retry_delay=retry_delay,
            timeout=self.config.browser.timeout // 1000,  # Convert ms to seconds
        )

        # Update profile last used time
        profile_data = self.state_manager.get_profile(self.profile)
        profile_data["last_used"] = datetime.now().isoformat()
        self.state_manager.set_profile(self.profile, profile_data)

        self.logger.info("Sync browser session started.")
        return self.browser

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the context manager and clean up browser resources.

        This method handles proper cleanup by:
        - Closing the browser connection gracefully
        - Stopping the Playwright sync context
        - Logging session completion

        Args:
            exc_type: Exception type if an exception was raised, None otherwise
            exc_val: Exception value if an exception was raised, None otherwise
            exc_tb: Exception traceback if an exception was raised, None otherwise

        Note:
            This method is called automatically when exiting the `with` statement,
            even if an exception occurs during browser automation.
        """
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        self.logger.info("Sync browser session closed.")

    def _get_timestamp(self) -> str:
        """
        Get current timestamp in ISO 8601 format.

        Returns:
            str: Current timestamp in ISO format (e.g., "2025-08-04T10:30:45.123456")

        Note:
            This is used internally for profile usage tracking and logging.
            The timestamp includes microsecond precision for accurate tracking.
        """
        return datetime.now().isoformat()


class AsyncBrowser:
    """
    An async context manager for an authenticated Playwright Browser.

    This class is the asynchronous version of the Browser class. It handles the setup and teardown
    of a Playwright browser instance that is connected to a persistent browser session. This allows
    you to maintain your login sessions and other browser data between runs.

    Args:
        verbose (bool, optional): Whether to enable verbose logging. Defaults to False.
        profile (str, optional): Browser profile name to use. Defaults to "default".
    """

    def __init__(self, verbose: bool = False, profile: str = "default"):
        self.verbose = verbose
        self.profile = profile
        self.logger = configure_logger(verbose)
        self.config = get_config()
        self.state_manager = get_state_manager()
        self.playwright: AsyncPlaywright | None = None
        self.browser: AsyncPlaywrightBrowser | None = None

    async def __aenter__(self) -> "AsyncPlaywrightBrowser":
        """
        Enter the async context manager and return an authenticated Playwright Browser instance.

        This method automatically handles:
        - Ensuring Chrome for Testing is installed and running
        - Starting the Playwright async context
        - Connecting to the browser with async retry logic and health checks
        - Updating profile usage statistics

        Returns:
            AsyncPlaywrightBrowser: A connected async Playwright browser instance ready for automation

        Raises:
            BrowserManagerError: If browser setup or connection fails
            NetworkError: If connection to debug port fails
            TimeoutError: If browser startup exceeds configured timeout

        Example:
            ```python
            async with AsyncBrowser(verbose=True) as browser:
                page = await browser.new_page()
                await page.goto("https://github.com")
                title = await page.title()
                print(title)
            ```
        """
        self.logger.info(
            f"Starting async browser session with profile '{self.profile}'..."
        )
        ensure_browser(self.verbose, profile=self.profile)

        # Use lazy loading for Playwright
        async_playwright = get_async_playwright()
        self.playwright = await async_playwright.start()

        # Connect to browser using configured port with health checks and retry logic
        debug_port = self.config.browser.debug_port
        max_retries = self.config.network.retry_attempts
        retry_delay = self.config.network.retry_delay

        self.browser = await async_connect_with_retry(
            self.playwright.chromium,
            debug_port,
            max_retries=max_retries,
            retry_delay=retry_delay,
            timeout=self.config.browser.timeout // 1000,  # Convert ms to seconds
        )

        # Update profile last used time
        profile_data = self.state_manager.get_profile(self.profile)
        profile_data["last_used"] = datetime.now().isoformat()
        self.state_manager.set_profile(self.profile, profile_data)
        self.logger.info("Async browser session started.")
        return self.browser

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the async context manager and clean up browser resources.

        This method handles proper cleanup by:
        - Closing the browser connection gracefully (async)
        - Stopping the Playwright async context
        - Logging session completion

        Args:
            exc_type: Exception type if an exception was raised, None otherwise
            exc_val: Exception value if an exception was raised, None otherwise
            exc_tb: Exception traceback if an exception was raised, None otherwise

        Note:
            This method is called automatically when exiting the `async with` statement,
            even if an exception occurs during browser automation.
        """
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        self.logger.info("Async browser session closed.")
