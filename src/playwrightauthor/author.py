#!/usr/bin/env -S uv run -s
# /// script
# dependencies = ["playwright"]
# ///
# this_file: src/playwrightauthor/author.py

"""The core Browser and AsyncBrowser classes."""

from datetime import datetime
from typing import TYPE_CHECKING

from .browser.process import get_chrome_process
from .browser_manager import ensure_browser
from .config import get_config
from .connection import async_connect_with_retry, connect_with_retry
from .lazy_imports import get_async_playwright, get_sync_playwright
from .monitoring import AsyncBrowserMonitor, BrowserMonitor
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

    PlaywrightAuthor's Browser class automatically handles Chrome for Testing installation,
    launching, and connection management. It provides a persistent browser session that
    maintains login state between script runs, eliminating the need for repeated authentication.

    The Browser class is designed to be used as a context manager, ensuring proper resource
    cleanup and connection management. It connects to a Chrome instance running in debug mode,
    allowing you to leverage any existing authentication sessions.

    Args:
        verbose (bool, optional): Enable detailed logging for debugging connection and browser
            management issues. Useful for troubleshooting authentication or setup problems.
            Defaults to False.
        profile (str, optional): Browser profile name to use for session isolation. Different
            profiles maintain separate authentication states, cookies, and browser data.
            Useful for managing multiple accounts or environments. Defaults to "default".

    Usage Examples:
        Basic import and class inspection:

        >>> from playwrightauthor import Browser
        >>> Browser.__name__
        'Browser'
        >>> hasattr(Browser, 'profile')  # Check if profile attribute exists
        False

        Basic usage with automatic browser management:

        .. code-block:: python

            from playwrightauthor import Browser
            with Browser() as browser:
                page = browser.new_page()
                page.goto("https://github.com")
                print(f"Title: {page.title()}")

        Using verbose logging for troubleshooting:

        .. code-block:: python

            with Browser(verbose=True) as browser:
                # Detailed logs help debug connection issues
                page = browser.new_page()
                page.goto("https://accounts.google.com")

        Managing multiple profiles for different accounts:

        .. code-block:: python

            # Work profile with work Google account
            with Browser(profile="work") as browser:
                page = browser.new_page()
                page.goto("https://mail.google.com")
                # Uses work account authentication

            # Personal profile with personal accounts
            with Browser(profile="personal") as browser:
                page = browser.new_page()
                page.goto("https://mail.google.com")
                # Uses personal account authentication

    Common Issues:
        - **Authentication Required**: If you get logged-out pages, manually log in using
          the browser that PlaywrightAuthor launches, then run your script again.
        - **Connection Failed**: Run `playwrightauthor diagnose` to check browser status
          and connection health.
        - **Permission Denied**: On macOS, you may need to grant accessibility permissions
          to Terminal or your Python environment.

    Note:
        The Browser class automatically installs Chrome for Testing if not present,
        launches it with remote debugging enabled, and connects Playwright to it.
        All browser data is stored in a persistent profile directory, maintaining
        sessions across script runs.
    """

    def __init__(self, verbose: bool = False, profile: str = "default"):
        self.verbose = verbose
        self.profile = profile
        self.logger = configure_logger(verbose)
        self.config = get_config()
        self.state_manager = get_state_manager()
        self.playwright: Playwright | None = None
        self.browser: PlaywrightBrowser | None = None
        self.monitor: BrowserMonitor | None = None
        self._restart_count = 0

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

        # Start monitoring if enabled
        if self.config.monitoring.enabled:
            self._start_monitoring()

        self.logger.info("Sync browser session started.")
        
        # Add helper method to get page in existing context
        def get_page():
            """Get a page from the existing browser context to reuse sessions."""
            contexts = self.browser.contexts
            self.logger.debug(f"Found {len(contexts)} browser contexts")
            
            if contexts:
                # Use the first (default) context which has the logged-in sessions
                context = contexts[0]
                pages = context.pages
                self.logger.debug(f"Context has {len(pages)} pages")
                
                if pages:
                    # Find a regular page (not extension pages)
                    for page in pages:
                        if not page.url.startswith("chrome-extension://"):
                            self.logger.debug(f"Reusing existing page: {page.url}")
                            return page
                    
                    # All pages are extension pages, create a new one
                    self.logger.debug("All existing pages are extension pages, creating new page")
                    return context.new_page()
                else:
                    # Create a new page in the existing context
                    self.logger.debug("Creating new page in existing context")
                    return context.new_page()
            else:
                # No existing context, create a new page (will create a new context)
                self.logger.debug("No existing context found, creating new page")
                return self.browser.new_page()
        
        # Attach the helper method to the browser object
        self.browser.get_page = get_page
        
        return self.browser

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the context manager and clean up browser resources.

        This method handles proper cleanup by:
        - Closing the browser connection gracefully
        - Stopping the Playwright sync context
        - Stopping browser monitoring if active
        - Logging session completion and metrics

        Args:
            exc_type: Exception type if an exception was raised, None otherwise
            exc_val: Exception value if an exception was raised, None otherwise
            exc_tb: Exception traceback if an exception was raised, None otherwise

        Note:
            This method is called automatically when exiting the `with` statement,
            even if an exception occurs during browser automation.
        """
        # Stop monitoring first
        if self.monitor:
            self.monitor.stop_monitoring()
            metrics = self.monitor.get_metrics()
            self.logger.info(f"Browser session metrics: {metrics.to_dict()}")

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

    def _start_monitoring(self) -> None:
        """Start browser health monitoring with crash detection."""
        debug_port = self.config.browser.debug_port

        # Get Chrome process PID
        chrome_proc = get_chrome_process(debug_port)
        browser_pid = chrome_proc.pid if chrome_proc else None

        # Create monitor with crash handler
        self.monitor = BrowserMonitor(
            debug_port=debug_port,
            check_interval=self.config.monitoring.check_interval,
            on_crash=self._handle_browser_crash,
        )

        # Start monitoring in background thread
        self.monitor.start_monitoring(browser_pid)
        self.logger.info(
            f"Started browser monitoring (interval: {self.config.monitoring.check_interval}s)"
        )

    def _handle_browser_crash(self) -> None:
        """Handle browser crash with automatic restart if enabled."""
        self.logger.error("Browser crash detected!")

        if not self.config.monitoring.enable_crash_recovery:
            self.logger.warning("Automatic restart disabled, not recovering from crash")
            return

        if self._restart_count >= self.config.monitoring.max_restart_attempts:
            self.logger.error(
                f"Maximum restart attempts ({self.config.monitoring.max_restart_attempts}) reached, "
                f"not attempting further restarts"
            )
            return

        self._restart_count += 1
        self.logger.info(
            f"Attempting browser restart ({self._restart_count}/{self.config.monitoring.max_restart_attempts})..."
        )

        try:
            # Clean up existing browser connection
            if self.browser:
                try:
                    self.browser.close()
                except Exception as e:
                    self.logger.debug(f"Error closing crashed browser: {e}")

            # Re-ensure browser is running
            ensure_browser(self.verbose, profile=self.profile)

            # Reconnect to browser
            debug_port = self.config.browser.debug_port
            max_retries = self.config.network.retry_attempts
            retry_delay = self.config.network.retry_delay

            self.browser = connect_with_retry(
                self.playwright.chromium,
                debug_port,
                max_retries=max_retries,
                retry_delay=retry_delay,
                timeout=self.config.browser.timeout // 1000,
            )

            # Restart monitoring with new process
            if self.monitor:
                self.monitor.stop_monitoring()
                self._start_monitoring()

            self.logger.info("Browser successfully restarted after crash")

        except Exception as e:
            self.logger.error(f"Failed to restart browser after crash: {e}")
            # Prevent infinite restart loops by maxing out counter
            self._restart_count = self.config.monitoring.max_restart_attempts


class AsyncBrowser:
    """
    An async context manager for an authenticated Playwright Browser.

    AsyncBrowser provides the same functionality as Browser but with asynchronous operation,
    enabling high-performance concurrent browser automation. It's ideal for scenarios requiring
    parallel page processing, concurrent data extraction, or integration with async frameworks
    like FastAPI, aiohttp, or asyncio-based applications.

    Like the synchronous Browser class, AsyncBrowser automatically handles Chrome for Testing
    installation, launching, and connection management while maintaining persistent authentication
    sessions across script runs.

    Args:
        verbose (bool, optional): Enable detailed logging for debugging connection and browser
            management issues. Particularly useful for troubleshooting async connection patterns
            and concurrent operation issues. Defaults to False.
        profile (str, optional): Browser profile name to use for session isolation. Different
            profiles maintain separate authentication states, enabling concurrent automation
            with multiple accounts or environments. Defaults to "default".

    Usage Examples:
        Basic import and class inspection:

        >>> from playwrightauthor import AsyncBrowser
        >>> AsyncBrowser.__name__
        'AsyncBrowser'
        >>> hasattr(AsyncBrowser, '__aenter__')  # Check if it's an async context manager
        True

        Basic async usage:

        .. code-block:: python

            import asyncio
            from playwrightauthor import AsyncBrowser

            async def scrape_data():
                async with AsyncBrowser() as browser:
                    page = await browser.new_page()
                    await page.goto("https://github.com")
                    title = await page.title()
                    return title

            # Run the async function
            asyncio.run(scrape_data())

        Concurrent automation with multiple profiles:

        .. code-block:: python

            async def scrape_multiple_accounts():
                tasks = []
                profiles = ["work", "personal", "testing"]

                for profile in profiles:
                    async with AsyncBrowser(profile=profile) as browser:
                        page = await browser.new_page()
                        await page.goto("https://mail.google.com")
                        # Each browser uses a different authentication profile
                        tasks.append(process_inbox(page))

                results = await asyncio.gather(*tasks)
                return results

        Integration with FastAPI for web scraping service:

        .. code-block:: python

            from fastapi import FastAPI
            app = FastAPI()

            @app.get("/scrape/{url}")
            async def scrape_url(url: str):
                async with AsyncBrowser(verbose=True) as browser:
                    page = await browser.new_page()
                    await page.goto(url)
                    title = await page.title()
                    return {"url": url, "title": title}

    Performance Considerations:
        - AsyncBrowser excels at I/O-bound operations like page loading and network requests
        - Use async/await consistently throughout your automation code
        - Consider connection pooling for high-throughput scenarios
        - Profile different approaches for your specific use case

    Common Issues:
        - **Mixed Sync/Async**: Don't mix sync and async Playwright calls. Use `await` consistently.
        - **Connection Timeouts**: Increase timeout settings for slow async operations
        - **Resource Management**: Always use `async with` to ensure proper cleanup
        - **Concurrent Limits**: Be mindful of system resource limits when running many concurrent browsers

    Note:
        AsyncBrowser shares the same underlying Chrome installation and configuration as Browser,
        but provides async/await interfaces for all operations. Both classes can be used in the
        same application for different use cases.
    """

    def __init__(self, verbose: bool = False, profile: str = "default"):
        self.verbose = verbose
        self.profile = profile
        self.logger = configure_logger(verbose)
        self.config = get_config()
        self.state_manager = get_state_manager()
        self.playwright: AsyncPlaywright | None = None
        self.browser: AsyncPlaywrightBrowser | None = None
        self.monitor: AsyncBrowserMonitor | None = None
        self._restart_count = 0

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

        # Start monitoring if enabled
        if self.config.monitoring.enabled:
            await self._start_monitoring()

        self.logger.info("Async browser session started.")
        return self.browser

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the async context manager and clean up browser resources.

        This method handles proper cleanup by:
        - Closing the browser connection gracefully (async)
        - Stopping the Playwright async context
        - Stopping browser monitoring if active
        - Logging session completion and metrics

        Args:
            exc_type: Exception type if an exception was raised, None otherwise
            exc_val: Exception value if an exception was raised, None otherwise
            exc_tb: Exception traceback if an exception was raised, None otherwise

        Note:
            This method is called automatically when exiting the `async with` statement,
            even if an exception occurs during browser automation.
        """
        # Stop monitoring first
        if self.monitor:
            await self.monitor.stop_monitoring()
            metrics = self.monitor.get_metrics()
            self.logger.info(f"Browser session metrics: {metrics.to_dict()}")

        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        self.logger.info("Async browser session closed.")

    async def _start_monitoring(self) -> None:
        """Start browser health monitoring with crash detection."""
        debug_port = self.config.browser.debug_port

        # Get Chrome process PID
        chrome_proc = get_chrome_process(debug_port)
        browser_pid = chrome_proc.pid if chrome_proc else None

        # Create monitor with crash handler
        self.monitor = AsyncBrowserMonitor(
            debug_port=debug_port,
            check_interval=self.config.monitoring.check_interval,
            on_crash=self._handle_browser_crash,
        )

        # Start monitoring in background task
        await self.monitor.start_monitoring(browser_pid)
        self.logger.info(
            f"Started async browser monitoring (interval: {self.config.monitoring.check_interval}s)"
        )

    async def _handle_browser_crash(self) -> None:
        """Handle browser crash with automatic restart if enabled."""
        self.logger.error("Browser crash detected!")

        if not self.config.monitoring.enable_crash_recovery:
            self.logger.warning("Automatic restart disabled, not recovering from crash")
            return

        if self._restart_count >= self.config.monitoring.max_restart_attempts:
            self.logger.error(
                f"Maximum restart attempts ({self.config.monitoring.max_restart_attempts}) reached, "
                f"not attempting further restarts"
            )
            return

        self._restart_count += 1
        self.logger.info(
            f"Attempting browser restart ({self._restart_count}/{self.config.monitoring.max_restart_attempts})..."
        )

        try:
            # Clean up existing browser connection
            if self.browser:
                try:
                    await self.browser.close()
                except Exception as e:
                    self.logger.debug(f"Error closing crashed browser: {e}")

            # Re-ensure browser is running (sync call)
            ensure_browser(self.verbose, profile=self.profile)

            # Reconnect to browser
            debug_port = self.config.browser.debug_port
            max_retries = self.config.network.retry_attempts
            retry_delay = self.config.network.retry_delay

            self.browser = await async_connect_with_retry(
                self.playwright.chromium,
                debug_port,
                max_retries=max_retries,
                retry_delay=retry_delay,
                timeout=self.config.browser.timeout // 1000,
            )

            # Restart monitoring with new process
            if self.monitor:
                await self.monitor.stop_monitoring()
                await self._start_monitoring()

            self.logger.info("Browser successfully restarted after crash")

        except Exception as e:
            self.logger.error(f"Failed to restart browser after crash: {e}")
            # Prevent infinite restart loops by maxing out counter
            self._restart_count = self.config.monitoring.max_restart_attempts
