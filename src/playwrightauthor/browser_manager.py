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
from .browser.process import get_chrome_process
from .config import PlaywrightAuthorConfig, get_config
from .exceptions import (
    BrowserInstallationError,
    BrowserLaunchError,
    BrowserManagerError,
    NetworkError,
)
from .exceptions import TimeoutError as PATimeoutError
from .profiles import (
    ProfileLease,
    reject_running_profile,
    require_free_debug_port,
    validate_attachment,
    validate_profile,
)
from .state_manager import get_state_manager
from .utils.logger import configure as configure_logger
from .utils.paths import data_dir as get_data_dir


def launch_browser(
    verbose: bool = False,
    max_retries: int | None = None,
    profile: str = "default",
    *,
    config: PlaywrightAuthorConfig | None = None,
) -> tuple[str, str]:
    """Serialize profile launch/attachment without owning a detached process."""
    validate_profile(profile)
    config = config or get_config()
    if config.browser.engine == "cloak":
        from .engines.cloak import ensure_cloak_browser

        return ensure_cloak_browser(config, verbose, max_retries, profile)
    directory = get_data_dir() / "profiles" / profile
    with ProfileLease(directory):
        return _launch_browser(verbose, max_retries, profile, config=config)


def _launch_browser(
    verbose: bool = False,
    max_retries: int | None = None,
    profile: str = "default",
    *,
    config: PlaywrightAuthorConfig | None = None,
) -> tuple[str, str]:
    """
    Launch Chrome for Testing with remote debugging, or return existing instance info.

    This is used by the 'browse' command to launch Chrome or connect to existing.

    Args:
        verbose: Enable verbose logging
        max_retries: Maximum retry attempts for browser operations. Uses config default if None.
        profile: Browser profile name to use

    Returns:
        Tuple of (browser_path, user_data_dir)

    Raises:
        BrowserManagerError: If browser launch fails
    """
    console = Console()
    logger = configure_logger(verbose)
    start_time = time.time()

    validate_profile(profile)
    # Load configuration
    config = config or get_config()
    if config.browser.engine == "cloak":
        from .engines.cloak import ensure_cloak_browser

        return ensure_cloak_browser(config, verbose, max_retries, profile)

    # Use configured retry attempts if not specified
    if max_retries is None:
        max_retries = config.network.retry_attempts

    # Get state manager for profile handling
    state_manager = get_state_manager()
    debug_port = state_manager.get_profile_debug_port(
        profile, config.browser.debug_port
    )

    try:
        # Check if Chrome is already running with debug port
        existing_chrome = get_chrome_process(debug_port)
        if existing_chrome:
            logger.info(
                f"Chrome for Testing is already running in debug mode on port {debug_port}"
            )
            browser_path = find_chrome_executable(logger)
            # Use proper profile directory, not install directory
            profile_data_dir = get_data_dir() / "profiles" / profile
            profile_data_dir.mkdir(parents=True, exist_ok=True)
            if not browser_path:
                raise BrowserManagerError(
                    "Chrome for Testing process is running but executable cannot be found. "
                    "This usually indicates a corrupted or incomplete installation.",
                    suggestion=(
                        "Clear the installation cache and reinstall Chrome for Testing. "
                        "This will download a fresh copy and fix any corruption issues."
                    ),
                    command="playwrightauthor clear-cache && playwrightauthor browse",
                )
            validate_attachment(
                existing_chrome, profile_data_dir, browser_path, config.browser.headless
            )
            logger.info("Chrome for Testing is already running, no need to launch.")
            return str(browser_path), str(profile_data_dir)
        require_free_debug_port(debug_port)
        reject_running_profile(get_data_dir() / "profiles" / profile)
        # Find or install Chrome executable
        find_start_time = time.time()
        browser_path = find_chrome_executable(logger)
        logger.info(
            f"Chrome for Testing executable search took {time.time() - find_start_time:.2f}s"
        )

        if not browser_path:
            logger.warning("Chrome for Testing not found. Attempting installation...")
            install_start_time = time.time()

            try:
                # Get chrome_version from config if specified
                chrome_version = config.browser.chrome_version
                install_from_lkgv(
                    logger, version=chrome_version, max_retries=max_retries
                )
                logger.info(
                    f"Installation took {time.time() - install_start_time:.2f}s"
                )

                # Try to find executable again after installation
                browser_path = find_chrome_executable(logger)
                if not browser_path:
                    raise BrowserInstallationError(
                        "Chrome for Testing installation completed but executable not found. "
                        "Installation may be corrupted or incomplete.",
                        suggestion=(
                            "The installation directory exists but Chrome executable is missing. "
                            "This often happens due to antivirus software or incomplete downloads."
                        ),
                        command="playwrightauthor clear-cache && playwrightauthor browse -v",
                    )
                logger.info(f"Chrome for Testing installed at: {browser_path}")

            except (BrowserInstallationError, NetworkError) as e:
                logger.error(f"Chrome for Testing installation failed: {e}")
                # Print the full error with all helpful information
                console.print(f"[red]{e}[/red]")
                # Re-raise the specific exception with its enhanced error message
                raise

        # Launch Chrome with retry logic
        # Use proper profile directory, not install directory
        profile_data_dir = get_data_dir() / "profiles" / profile
        profile_data_dir.mkdir(parents=True, exist_ok=True)
        launch_start_time = time.time()

        try:
            launch_chrome_with_retry(
                browser_path,
                profile_data_dir,
                debug_port,
                logger,
                max_retries=max_retries,
                extra_args=[
                    *(["--headless=new"] if config.browser.headless else []),
                    *config.browser.args,
                ],
            )
            logger.info(
                f"Chrome for Testing launch took {time.time() - launch_start_time:.2f}s"
            )

        except (BrowserLaunchError, PATimeoutError) as e:
            logger.error(f"Chrome for Testing launch failed: {e}")
            # Print the full error with all helpful information
            console.print(f"[red]{e}[/red]")
            # Re-raise the specific exception with its enhanced error message
            raise

        logger.info("Chrome for Testing launched successfully")
        logger.info(f"launch_browser completed in {time.time() - start_time:.2f}s")
        return str(browser_path), str(profile_data_dir)

    except BrowserManagerError:
        # Re-raise our own exceptions
        raise
    except Exception as e:
        # Catch any unexpected errors and wrap them with helpful guidance
        error_type = type(e).__name__
        error_msg = f"Unexpected {error_type} in browser launch: {str(e)}"
        logger.error(error_msg)

        wrapped_error = BrowserManagerError(
            error_msg,
            suggestion="An unexpected error occurred during browser launch.",
            command="playwrightauthor browse -v",
        )
        console.print(f"[red]{wrapped_error}[/red]")
        raise wrapped_error from e


def ensure_browser(
    verbose: bool = False,
    max_retries: int | None = None,
    profile: str = "default",
    *,
    config: PlaywrightAuthorConfig | None = None,
) -> tuple[str, str]:
    """Ensure a browser through the same serialized, identity-checked launch path."""
    return launch_browser(verbose, max_retries, profile, config=config)
