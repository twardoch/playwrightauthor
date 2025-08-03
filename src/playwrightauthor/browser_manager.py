#!/usr/bin/env -S uv run -s
# /// script
# dependencies = ["requests", "platformdirs", "rich", "psutil"]
# ///
# this_file: playwrightauthor/browser_manager.py

"""
Ensure a Chrome for Testing build is present & running in debug mode.
"""

import sys
import time
import psutil
from rich.console import Console
from .utils.paths import install_dir
from .utils.logger import configure as configure_logger
from .exceptions import BrowserManagerError
from .browser.finder import find_chrome_executable
from .browser.installer import install_from_lkgv
from .browser.launcher import launch_chrome
from .browser.process import get_chrome_process

_DEBUGGING_PORT = 9222

def ensure_browser(verbose: bool = False) -> tuple[str, str]:
    """
    Ensures a Chrome for Testing instance is running with remote debugging.
    Returns the path to the browser executable and the user data directory.
    """
    console = Console()
    logger = configure_logger(verbose)
    start_time = time.time()

    if get_chrome_process(_DEBUGGING_PORT):
        logger.info(f"Chrome is already running in debug mode on port {_DEBUGGING_PORT}.")
        browser_path = find_chrome_executable()
        data_dir = install_dir()
        if not browser_path:
            raise BrowserManagerError("Could not find Chrome executable even though process is running.")
        logger.info(f"ensure_browser took {time.time() - start_time:.2f}s")
        return str(browser_path), str(data_dir)

    proc = get_chrome_process()
    if proc:
        logger.warning("Found a running Chrome instance without the debugging port. Killing it...")
        kill_start_time = time.time()
        try:
            proc.kill()
            for _ in range(5):
                if not proc.is_running():
                    break
                time.sleep(1)
            else:
                raise BrowserManagerError("Failed to kill existing Chrome process.")
            logger.info(f"Chrome process killed in {time.time() - kill_start_time:.2f}s")
        except psutil.NoSuchProcess:
            pass

    find_start_time = time.time()
    browser_path = find_chrome_executable()
    logger.info(f"Finding executable took {time.time() - find_start_time:.2f}s")
    if not browser_path:
        logger.warning("Chrome for Testing not found. Attempting to install...")
        install_start_time = time.time()
        try:
            install_from_lkgv(logger)
        except BrowserManagerError as e:
            console.print(f"[red]{e}[/red]")
            sys.exit(1)
        logger.info(f"Installation took {time.time() - install_start_time:.2f}s")

        browser_path = find_chrome_executable()
        if not browser_path:
            raise BrowserManagerError("Failed to find Chrome for Testing after installation.")
        logger.info(f"Chrome for Testing installed at: {browser_path}")

    data_dir = install_dir()
    launch_start_time = time.time()
    try:
        launch_chrome(browser_path, data_dir, _DEBUGGING_PORT, logger)
    except BrowserManagerError as e:
        console.print(f"[red]{e}[/red]")
        sys.exit(1)
    logger.info(f"Chrome launch took {time.time() - launch_start_time:.2f}s")

    logger.info("Chrome for Testing launched successfully.")
    logger.info(f"ensure_browser took {time.time() - start_time:.2f}s")
    return str(browser_path), str(data_dir)
