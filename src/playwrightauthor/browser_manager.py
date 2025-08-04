#!/usr/bin/env -S uv run -s
# /// script
# dependencies = ["requests", "platformdirs", "rich", "psutil"]
# ///
# this_file: src/playwrightauthor/browser_manager.py

"""
Ensure a Chrome for Testing build is present & running in debug mode.
"""

import time

from rich.console import Console

from .browser.finder import find_chrome_executable
from .browser.installer import install_from_lkgv
from .browser.launcher import launch_chrome_with_retry
from .browser.process import get_chrome_process, kill_chrome_process
from .config import get_config
from .exceptions import (
    BrowserInstallationError,
    BrowserLaunchError,
    BrowserManagerError,
    NetworkError,
    ProcessKillError,
)
from .exceptions import TimeoutError as PATimeoutError
from .state_manager import get_state_manager
from .utils.logger import configure as configure_logger
from .utils.paths import install_dir


def ensure_browser(
    verbose: bool = False, max_retries: int | None = None, profile: str = "default"
) -> tuple[str, str]:
    """
    Ensures a Chrome for Testing instance is running with remote debugging.

    Args:
        verbose: Enable verbose logging
        max_retries: Maximum retry attempts for browser operations. Uses config default if None.
        profile: Browser profile name to use

    Returns:
        Tuple of (browser_path, user_data_dir)

    Raises:
        BrowserManagerError: If browser setup fails after all retries
    """
    console = Console()
    logger = configure_logger(verbose)
    start_time = time.time()

    # Load configuration
    config = get_config()
    debug_port = config.browser.debug_port

    # Use configured retry attempts if not specified
    if max_retries is None:
        max_retries = config.network.retry_attempts

    # Get state manager for profile handling
    get_state_manager()

    try:
        # Check if Chrome is already running with debug port
        if get_chrome_process(debug_port):
            logger.info(f"Chrome is already running in debug mode on port {debug_port}")
            browser_path = find_chrome_executable(logger)
            data_dir = install_dir()
            if not browser_path:
                raise BrowserManagerError(
                    "Could not find Chrome executable even though process is running. "
                    "This may indicate a corrupted installation."
                )
            logger.info(f"ensure_browser completed in {time.time() - start_time:.2f}s")
            return str(browser_path), str(data_dir)

        # Kill any Chrome process without debug port
        proc = get_chrome_process()
        if proc:
            logger.warning(
                "Found running Chrome instance without debug port. Terminating..."
            )
            kill_start_time = time.time()
            try:
                kill_chrome_process(proc, timeout=10, logger=logger)
                logger.info(
                    f"Chrome process terminated in {time.time() - kill_start_time:.2f}s"
                )
            except ProcessKillError as e:
                logger.error(f"Failed to kill existing Chrome process: {e}")
                # Continue anyway - Chrome might still be launchable on a different port

        # Find or install Chrome executable
        find_start_time = time.time()
        browser_path = find_chrome_executable(logger)
        logger.info(
            f"Chrome executable search took {time.time() - find_start_time:.2f}s"
        )

        if not browser_path:
            logger.warning("Chrome for Testing not found. Attempting installation...")
            install_start_time = time.time()

            try:
                install_from_lkgv(logger, max_retries=max_retries)
                logger.info(
                    f"Installation took {time.time() - install_start_time:.2f}s"
                )

                # Try to find executable again after installation
                browser_path = find_chrome_executable(logger)
                if not browser_path:
                    raise BrowserInstallationError(
                        "Chrome for Testing installation completed but executable not found. "
                        "Installation may be corrupted."
                    )
                logger.info(f"Chrome for Testing installed at: {browser_path}")

            except (BrowserInstallationError, NetworkError) as e:
                error_msg = f"Failed to install Chrome for Testing: {e}"
                logger.error(error_msg)
                console.print(f"[red]{error_msg}[/red]")
                raise BrowserManagerError(error_msg) from e

        # Launch Chrome with retry logic
        data_dir = install_dir()
        launch_start_time = time.time()

        try:
            launch_chrome_with_retry(
                browser_path, data_dir, debug_port, logger, max_retries=max_retries
            )
            logger.info(f"Chrome launch took {time.time() - launch_start_time:.2f}s")

        except (BrowserLaunchError, PATimeoutError) as e:
            error_msg = f"Failed to launch Chrome: {e}"
            logger.error(error_msg)
            console.print(f"[red]{error_msg}[/red]")
            raise BrowserManagerError(error_msg) from e

        logger.info("Chrome for Testing launched successfully")
        logger.info(f"ensure_browser completed in {time.time() - start_time:.2f}s")
        return str(browser_path), str(data_dir)

    except BrowserManagerError:
        # Re-raise our own exceptions
        raise
    except Exception as e:
        # Catch any unexpected errors and wrap them
        error_msg = f"Unexpected error in browser management: {e}"
        logger.error(error_msg)
        console.print(f"[red]{error_msg}[/red]")
        raise BrowserManagerError(error_msg) from e
