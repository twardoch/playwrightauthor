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
from .utils.paths import install_dir, data_dir as get_data_dir


def launch_browser(
    verbose: bool = False, max_retries: int | None = None, profile: str = "default"
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
            logger.info("Chrome for Testing is already running, no need to launch.")
            return str(browser_path), str(profile_data_dir)
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
                install_from_lkgv(logger, max_retries=max_retries)
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
                browser_path, profile_data_dir, debug_port, logger, max_retries=max_retries
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
            command="playwrightauthor browse -v"
        )
        console.print(f"[red]{wrapped_error}[/red]")
        raise wrapped_error from e


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
        existing_chrome = get_chrome_process(debug_port)
        logger.debug(f"Checking for existing Chrome on port {debug_port}: {existing_chrome}")
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
                    command="playwrightauthor clear-cache && playwrightauthor status",
                )
            logger.info(f"ensure_browser completed in {time.time() - start_time:.2f}s")
            return str(browser_path), str(profile_data_dir)

        # Check for any existing Chrome for Testing process without debug port
        proc = get_chrome_process()
        if proc and not existing_chrome:
            logger.info(
                "Found running Chrome for Testing instance without debug port. "
                "Killing it to relaunch with debugging enabled..."
            )
            try:
                # Kill the existing Chrome for Testing process
                kill_chrome_process(proc, logger=logger)
                # Wait a moment for the process to fully terminate
                time.sleep(1)
                logger.info("Successfully killed Chrome for Testing process without debug port")
            except ProcessKillError as e:
                logger.error(f"Failed to kill Chrome for Testing process: {e}")
                raise BrowserManagerError(
                    "Could not kill existing Chrome for Testing process to enable debugging.",
                    suggestion=(
                        "Please manually close Chrome for Testing and try again. "
                        "Use 'playwrightauthor browse' to launch with debugging enabled."
                    ),
                    command="pkill -f 'chrome.*testing' && playwrightauthor browse"
                ) from e

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
                install_from_lkgv(logger, max_retries=max_retries)
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
                        command="playwrightauthor clear-cache && playwrightauthor status -v",
                    )
                logger.info(f"Chrome for Testing installed at: {browser_path}")

            except (BrowserInstallationError, NetworkError) as e:
                logger.error(f"Chrome for Testing installation failed: {e}")
                # Print the full error with all helpful information
                console.print(f"[red]{e}[/red]")
                # Re-raise the specific exception with its enhanced error message
                raise

        # If we get here, Chrome for Testing is not running with debug port
        # Launch Chrome for Testing with debugging enabled
        logger.info("Launching Chrome for Testing with remote debugging enabled...")
        
        # Use proper profile directory
        profile_data_dir = get_data_dir() / "profiles" / profile
        profile_data_dir.mkdir(parents=True, exist_ok=True)
        
        # Launch Chrome with retry logic
        launch_start_time = time.time()
        try:
            chrome_proc = launch_chrome_with_retry(
                browser_path, 
                profile_data_dir, 
                debug_port, 
                logger, 
                max_retries=max_retries
            )
            
            if chrome_proc:
                logger.info(
                    f"Chrome for Testing launched successfully in {time.time() - launch_start_time:.2f}s "
                    f"(PID: {chrome_proc.pid})"
                )
                logger.info(f"ensure_browser completed in {time.time() - start_time:.2f}s")
                return str(browser_path), str(profile_data_dir)
            else:
                raise BrowserLaunchError(
                    "Chrome for Testing launch returned no process",
                    suggestion="Chrome may have crashed immediately after launch",
                    command="playwrightauthor diagnose -v"
                )
                
        except (BrowserLaunchError, PATimeoutError) as e:
            logger.error(f"Failed to launch Chrome for Testing: {e}")
            raise

    except BrowserManagerError:
        # Re-raise our own exceptions
        raise
    except Exception as e:
        # Catch any unexpected errors and wrap them with helpful guidance
        error_type = type(e).__name__
        error_msg = f"Unexpected {error_type} in browser management: {str(e)}"
        logger.error(error_msg)

        # Provide helpful suggestions based on common error patterns
        suggestion = (
            "An unexpected error occurred. This might be a system-specific issue."
        )
        command = "playwrightauthor diagnose -v"

        if "permission" in str(e).lower():
            suggestion = (
                "Permission denied. You may need elevated privileges or the directory "
                "might be protected by security software."
            )
            command = "sudo playwrightauthor status  # Try with elevated permissions"

        elif "no such file" in str(e).lower() or "not found" in str(e).lower():
            suggestion = (
                "Required files are missing. The installation might be incomplete "
                "or corrupted. Try clearing the cache and reinstalling."
            )
            command = "playwrightauthor clear-cache && playwrightauthor status"

        wrapped_error = BrowserManagerError(
            error_msg, suggestion=suggestion, command=command
        )
        console.print(f"[red]{wrapped_error}[/red]")
        raise wrapped_error from e
