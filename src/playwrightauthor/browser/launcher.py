# this_file: src/playwrightauthor/browser/launcher.py

import subprocess
import time
from pathlib import Path

from ..exceptions import BrowserLaunchError, TimeoutError
from .process import wait_for_process_start


def launch_chrome(
    browser_path: Path, data_dir: Path, port: int, logger, timeout: int = 30
):
    """
    Launch Chrome executable as a detached process with verification.

    Args:
        browser_path: Path to Chrome executable
        data_dir: User data directory path
        port: Remote debugging port
        logger: Logger instance
        timeout: Maximum time to wait for launch

    Raises:
        BrowserLaunchError: If launch fails
        TimeoutError: If launch times out
    """
    logger.info(f"Launching Chrome from: {browser_path}")

    # Prepare launch command with additional stability flags
    command = [
        str(browser_path),
        f"--remote-debugging-port={port}",
        f"--user-data-dir={data_dir}",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-background-timer-throttling",
        "--disable-backgrounding-occluded-windows",
        "--disable-renderer-backgrounding",
    ]

    try:
        # Launch process
        logger.debug(f"Executing command: {' '.join(command)}")
        process = subprocess.Popen(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,  # Detach from parent process
        )

        # Give Chrome a moment to start
        time.sleep(1)

        # Check if process is still alive (didn't crash immediately)
        return_code = process.poll()
        if return_code is not None:
            raise BrowserLaunchError(
                f"Chrome process exited immediately with code {return_code}"
            )

        # Wait for Chrome to actually start accepting debug connections
        logger.info("Waiting for Chrome debug port to become available...")
        try:
            wait_for_process_start(port, timeout=timeout)
            logger.info("Chrome launched successfully and debug port is available")
        except TimeoutError as e:
            # Try to clean up the process if it's still running
            try:
                if process.poll() is None:
                    process.terminate()
                    process.wait(timeout=5)
            except (subprocess.TimeoutExpired, OSError):
                pass
            raise BrowserLaunchError(f"Chrome launch verification failed: {e}") from e

    except (OSError, subprocess.SubprocessError) as e:
        raise BrowserLaunchError(f"Failed to launch Chrome: {e}") from e


def launch_chrome_with_retry(
    browser_path: Path,
    data_dir: Path,
    port: int,
    logger,
    max_retries: int = 3,
    retry_delay: int = 2,
) -> None:
    """
    Launch Chrome with retry logic.

    Args:
        browser_path: Path to Chrome executable
        data_dir: User data directory path
        port: Remote debugging port
        logger: Logger instance
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retries in seconds

    Raises:
        BrowserLaunchError: If all retry attempts fail
    """
    last_error = None

    for attempt in range(max_retries):
        try:
            logger.info(f"Chrome launch attempt {attempt + 1}/{max_retries}")
            launch_chrome(browser_path, data_dir, port, logger)
            return  # Success

        except (BrowserLaunchError, TimeoutError) as e:
            last_error = e
            if attempt < max_retries - 1:
                logger.warning(
                    f"Launch attempt {attempt + 1} failed: {e}. Retrying in {retry_delay}s..."
                )
                time.sleep(retry_delay)
            else:
                logger.error(f"All {max_retries} launch attempts failed")

    raise BrowserLaunchError(
        f"Failed to launch Chrome after {max_retries} attempts. Last error: {last_error}"
    ) from last_error
