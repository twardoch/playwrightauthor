# this_file: src/playwrightauthor/browser/process.py

import time

import psutil

from ..exceptions import ProcessKillError, TimeoutError


def get_chrome_process(port: int | None = None) -> psutil.Process | None:
    """Find a running Chrome for Testing process, optionally filtered by debug port."""
    for proc in psutil.process_iter(["name", "cmdline", "exe"]):
        try:
            proc_name = proc.info["name"].lower()
            # Check if it's a Chrome process (including main Chrome for Testing)
            if "chrome" in proc_name and not any(helper in proc_name for helper in ["helper", "crashpad"]):
                # Try to get the executable path to verify it's Chrome for Testing
                try:
                    exe_path = proc.info.get("exe", "") or ""
                    exe_lower = exe_path.lower()

                    # Check if this is Chrome for Testing
                    # Look for "chrome for testing" in path or our install directory patterns
                    is_chrome_for_testing = (
                        "chrome for testing" in exe_lower
                        or "chrome-mac-" in exe_lower
                        or "chrome-win" in exe_lower
                        or "chrome-linux" in exe_lower
                    )

                    # If we're not looking for a specific port, only return Chrome for Testing
                    if port is None:
                        if is_chrome_for_testing:
                            return proc
                    else:
                        # Check for the debug port in command line
                        if any(
                            f"--remote-debugging-port={port}" in arg
                            for arg in proc.info["cmdline"]
                        ):
                            # Only return if it's Chrome for Testing
                            if is_chrome_for_testing:
                                return proc
                except (AttributeError, TypeError):
                    # If we can't get exe path, skip this process
                    pass
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return None


def kill_chrome_process(proc: psutil.Process, timeout: int = 10, logger=None) -> None:
    """
    Kill a Chrome process gracefully with fallback to force kill.

    Args:
        proc: The process to kill
        timeout: Maximum time to wait for graceful termination
        logger: Optional logger for status messages
    """
    if logger:
        logger.info(f"Attempting to terminate Chrome process (PID: {proc.pid})")

    try:
        # First try graceful termination
        proc.terminate()

        # Wait for graceful termination
        try:
            proc.wait(timeout=timeout // 2)
            if logger:
                logger.info("Chrome process terminated gracefully")
            return
        except psutil.TimeoutExpired:
            if logger:
                logger.warning("Graceful termination timed out, force killing...")

        # Force kill if still running
        if proc.is_running():
            proc.kill()

            # Wait for force kill to complete
            start_time = time.time()
            while proc.is_running() and (time.time() - start_time) < timeout:
                time.sleep(0.1)

            if proc.is_running():
                raise ProcessKillError(
                    f"Failed to kill Chrome process (PID: {proc.pid}) within {timeout}s"
                )

            if logger:
                logger.info("Chrome process force killed successfully")

    except psutil.NoSuchProcess:
        # Process already dead
        if logger:
            logger.info("Chrome process already terminated")
    except (psutil.AccessDenied, OSError) as e:
        raise ProcessKillError(f"Failed to kill Chrome process: {e}") from e


def wait_for_process_start(
    port: int, timeout: int = 30, check_interval: float = 0.5
) -> psutil.Process:
    """
    Wait for a Chrome for Testing process with debug port to start.

    Args:
        port: Debug port to wait for
        timeout: Maximum time to wait
        check_interval: Time between checks

    Returns:
        The Chrome for Testing process

    Raises:
        TimeoutError: If Chrome for Testing process doesn't start within timeout
    """
    start_time = time.time()
    while (time.time() - start_time) < timeout:
        proc = get_chrome_process(port)
        if proc:
            return proc
        time.sleep(check_interval)

    raise TimeoutError(
        f"Chrome for Testing process with debug port {port} did not start within {timeout}s"
    )
