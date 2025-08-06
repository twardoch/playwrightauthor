# this_file: src/playwrightauthor/connection.py

"""Connection health checking and optimization utilities for PlaywrightAuthor."""

import json
import time
from typing import Any

import requests
from loguru import logger

from .exceptions import ConnectionError as PAConnectionError


class ConnectionHealthChecker:
    """Checks and monitors Chrome DevTools Protocol connection health."""

    def __init__(self, debug_port: int):
        """Initialize the connection health checker.

        Args:
            debug_port: Chrome debug port to check.
        """
        self.debug_port = debug_port
        self.base_url = f"http://localhost:{debug_port}"

    def is_cdp_available(self, timeout: float = 5.0) -> bool:
        """Check if Chrome DevTools Protocol is available.

        Args:
            timeout: Request timeout in seconds.

        Returns:
            True if CDP is available, False otherwise.
        """
        try:
            response = requests.get(f"{self.base_url}/json/version", timeout=timeout)
            return response.status_code == 200
        except (requests.RequestException, ConnectionError):
            return False

    def get_browser_info(self, timeout: float = 5.0) -> dict[str, Any] | None:
        """Get browser information via CDP.

        Args:
            timeout: Request timeout in seconds.

        Returns:
            Browser info dictionary or None if unavailable.
        """
        try:
            response = requests.get(f"{self.base_url}/json/version", timeout=timeout)
            if response.status_code == 200:
                return response.json()
        except (requests.RequestException, ConnectionError, json.JSONDecodeError):
            pass
        return None

    def wait_for_cdp_available(
        self, timeout: float = 30.0, check_interval: float = 0.5
    ) -> bool:
        """Wait for CDP to become available.

        Args:
            timeout: Maximum time to wait in seconds.
            check_interval: Time between checks in seconds.

        Returns:
            True if CDP becomes available, False if timeout.
        """
        start_time = time.time()
        while (time.time() - start_time) < timeout:
            if self.is_cdp_available():
                return True
            time.sleep(check_interval)
        return False

    def get_connection_diagnostics(self) -> dict[str, Any]:
        """Get detailed connection diagnostics.

        Returns:
            Dictionary with connection diagnostic information.
        """
        diagnostics = {
            "debug_port": self.debug_port,
            "base_url": self.base_url,
            "timestamp": time.time(),
            "cdp_available": False,
            "browser_info": None,
            "response_time_ms": None,
            "error": None,
        }

        start_time = time.time()
        try:
            response = requests.get(f"{self.base_url}/json/version", timeout=5.0)
            response_time = (time.time() - start_time) * 1000
            diagnostics["response_time_ms"] = round(response_time, 2)

            if response.status_code == 200:
                diagnostics["cdp_available"] = True
                diagnostics["browser_info"] = response.json()
            else:
                diagnostics["error"] = f"HTTP {response.status_code}: {response.text}"

        except requests.RequestException as e:
            diagnostics["error"] = str(e)
            diagnostics["response_time_ms"] = round(
                (time.time() - start_time) * 1000, 2
            )

        return diagnostics


def check_connection_health(
    debug_port: int, timeout: float = 5.0
) -> tuple[bool, dict[str, Any]]:
    """Quick connection health check with diagnostics.

    Args:
        debug_port: Chrome debug port to check.
        timeout: Request timeout in seconds.

    Returns:
        Tuple of (is_healthy, diagnostics_dict).
    """
    checker = ConnectionHealthChecker(debug_port)
    diagnostics = checker.get_connection_diagnostics()
    is_healthy = diagnostics["cdp_available"]

    if is_healthy:
        logger.debug(
            f"CDP connection healthy (port {debug_port}, {diagnostics['response_time_ms']}ms)"
        )
    else:
        logger.warning(
            f"CDP connection unhealthy (port {debug_port}): {diagnostics.get('error', 'Unknown error')}"
        )

    return is_healthy, diagnostics


def connect_with_retry(
    playwright_browser,
    debug_port: int,
    max_retries: int = 3,
    retry_delay: float = 1.0,
    timeout: float = 10.0,
):
    """Connect to browser with retry logic and health checks.

    Args:
        playwright_browser: Playwright browser object (sync or async).
        debug_port: Chrome debug port.
        max_retries: Maximum retry attempts.
        retry_delay: Delay between retries in seconds.
        timeout: Connection timeout per attempt.

    Returns:
        Connected browser instance.

    Raises:
        BrowserManagerError: If connection fails after all retries.
    """
    last_error = None
    url = f"http://localhost:{debug_port}"

    for attempt in range(max_retries + 1):
        try:
            # Check CDP health before attempting connection
            is_healthy, diagnostics = check_connection_health(debug_port, timeout=5.0)

            if not is_healthy:
                error_details = diagnostics.get("error", "Unknown error")
                error_msg = (
                    f"Cannot connect to Chrome DevTools Protocol on port {debug_port}"
                )

                # Provide specific guidance based on error type
                if "refused" in str(error_details).lower():
                    error_msg += " - Connection refused"
                elif "timeout" in str(error_details).lower():
                    error_msg += " - Connection timeout"

                logger.warning(
                    f"CDP not available (attempt {attempt + 1}/{max_retries + 1}): {error_details}"
                )
                last_error = PAConnectionError(error_msg)

                if attempt < max_retries:
                    time.sleep(retry_delay * (2**attempt))  # Exponential backoff
                    continue
                else:
                    raise last_error

            # Attempt connection
            logger.debug(
                f"Attempting CDP connection to {url} (attempt {attempt + 1}/{max_retries + 1})"
            )
            browser = playwright_browser.connect_over_cdp(url)

            logger.info(f"Successfully connected to Chrome on port {debug_port}")
            
            # Get existing contexts to reuse sessions
            contexts = browser.contexts
            logger.debug(f"Found {len(contexts)} existing browser contexts")
            
            return browser

        except Exception as e:
            error_str = str(e)
            base_msg = f"Failed to connect to Chrome on port {debug_port}"

            # Provide specific error message based on exception type
            if "connect_over_cdp" in error_str:
                error_msg = f"{base_msg} - Playwright connection failed"
            elif "timeout" in error_str.lower():
                error_msg = f"{base_msg} - Connection timed out after {timeout}s"
            else:
                error_msg = f"{base_msg} - {error_str}"

            logger.warning(
                f"Connection failed (attempt {attempt + 1}/{max_retries + 1}): {e}"
            )
            last_error = PAConnectionError(error_msg)

            if attempt < max_retries:
                time.sleep(retry_delay * (2**attempt))  # Exponential backoff
            else:
                break

    # All retries exhausted
    raise last_error or PAConnectionError(
        f"Failed to connect to Chrome on port {debug_port} after {max_retries + 1} attempts. "
        f"Chrome may not be running or the debug port may be blocked."
    )


async def async_connect_with_retry(
    playwright_browser,
    debug_port: int,
    max_retries: int = 3,
    retry_delay: float = 1.0,
    timeout: float = 10.0,
):
    """Async version of connect_with_retry.

    Args:
        playwright_browser: Async Playwright browser object.
        debug_port: Chrome debug port.
        max_retries: Maximum retry attempts.
        retry_delay: Delay between retries in seconds.
        timeout: Connection timeout per attempt.

    Returns:
        Connected browser instance.

    Raises:
        BrowserManagerError: If connection fails after all retries.
    """
    import asyncio

    last_error = None
    url = f"http://localhost:{debug_port}"

    for attempt in range(max_retries + 1):
        try:
            # Check CDP health before attempting connection
            is_healthy, diagnostics = check_connection_health(debug_port, timeout=5.0)

            if not is_healthy:
                error_details = diagnostics.get("error", "Unknown error")
                error_msg = (
                    f"Cannot connect to Chrome DevTools Protocol on port {debug_port}"
                )

                # Provide specific guidance based on error type
                if "refused" in str(error_details).lower():
                    error_msg += " - Connection refused"
                elif "timeout" in str(error_details).lower():
                    error_msg += " - Connection timeout"

                logger.warning(
                    f"CDP not available (attempt {attempt + 1}/{max_retries + 1}): {error_details}"
                )
                last_error = PAConnectionError(error_msg)

                if attempt < max_retries:
                    await asyncio.sleep(
                        retry_delay * (2**attempt)
                    )  # Exponential backoff
                    continue
                else:
                    raise last_error

            # Attempt connection
            logger.debug(
                f"Attempting async CDP connection to {url} (attempt {attempt + 1}/{max_retries + 1})"
            )
            browser = await playwright_browser.connect_over_cdp(url)

            logger.info(f"Successfully connected to Chrome on port {debug_port}")
            return browser

        except Exception as e:
            error_str = str(e)
            base_msg = f"Failed to connect to Chrome on port {debug_port}"

            # Provide specific error message based on exception type
            if "connect_over_cdp" in error_str:
                error_msg = f"{base_msg} - Playwright connection failed"
            elif "timeout" in error_str.lower():
                error_msg = f"{base_msg} - Connection timed out after {timeout}s"
            else:
                error_msg = f"{base_msg} - {error_str}"

            logger.warning(
                f"Async connection failed (attempt {attempt + 1}/{max_retries + 1}): {e}"
            )
            last_error = PAConnectionError(error_msg)

            if attempt < max_retries:
                await asyncio.sleep(retry_delay * (2**attempt))  # Exponential backoff
            else:
                break

    # All retries exhausted
    raise last_error or PAConnectionError(
        f"Failed to connect to Chrome on port {debug_port} after {max_retries + 1} attempts. "
        f"Chrome may not be running or the debug port may be blocked."
    )
