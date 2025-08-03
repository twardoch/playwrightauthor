#!/usr/bin/env -S uv run -s
# /// script
# dependencies = ["playwright"]
# ///
# this_file: src/playwrightauthor/onboarding.py

"""Enhanced onboarding with login detection and user guidance."""

import asyncio
from pathlib import Path

from playwright.async_api import Browser as AsyncBrowser
from playwright.async_api import Page


async def _detect_login_activity(page: Page, logger) -> bool:
    """
    Detect if the user has performed login activities.

    Returns True if login activity is detected, False otherwise.
    """
    try:
        # Check for common login indicators
        [
            # Common cookie names that indicate authentication
            lambda: page.context.cookies(),
            # Check for localStorage items that might indicate login
            lambda: page.evaluate("() => Object.keys(localStorage).length > 0"),
            # Check for sessionStorage items
            lambda: page.evaluate("() => Object.keys(sessionStorage).length > 0"),
        ]

        # Check cookies for authentication-related names
        cookies = await page.context.cookies()
        auth_cookie_patterns = [
            "session",
            "auth",
            "token",
            "login",
            "user",
            "jwt",
            "access_token",
            "sid",
            "sessionid",
            "PHPSESSID",
            "connect.sid",
            "_session",
            "laravel_session",
        ]

        auth_cookies = [
            cookie
            for cookie in cookies
            if any(
                pattern.lower() in cookie["name"].lower()
                for pattern in auth_cookie_patterns
            )
        ]

        if auth_cookies:
            logger.info(f"Detected {len(auth_cookies)} authentication-related cookies")
            return True

        # Check for local/session storage (indicates interaction with web apps)
        try:
            local_storage_count = await page.evaluate(
                "() => Object.keys(localStorage).length"
            )
            session_storage_count = await page.evaluate(
                "() => Object.keys(sessionStorage).length"
            )

            if local_storage_count > 0 or session_storage_count > 0:
                logger.info(
                    f"Detected browser storage activity (localStorage: {local_storage_count}, sessionStorage: {session_storage_count})"
                )
                return True
        except Exception:
            pass  # Storage might not be available on all pages

        return False

    except Exception as e:
        logger.debug(f"Error detecting login activity: {e}")
        return False


async def _wait_for_user_action(page: Page, logger, timeout: int = 300) -> str:
    """
    Wait for user to either navigate away or perform login activities.

    Returns:
        'navigation' if user navigated away
        'login_detected' if login activity was detected
        'timeout' if timeout occurred
    """
    start_time = asyncio.get_event_loop().time()
    check_interval = 5  # Check every 5 seconds

    logger.info("Monitoring for user activity...")

    try:
        while (asyncio.get_event_loop().time() - start_time) < timeout:
            # Check if user navigated away
            if page.url != "about:blank" and not page.url.startswith("data:"):
                logger.info(f"User navigated to: {page.url}")
                return "navigation"

            # Check for login activity
            if await _detect_login_activity(page, logger):
                logger.info("Login activity detected")
                return "login_detected"

            # Wait before next check
            await asyncio.sleep(check_interval)

        logger.warning(f"Timeout after {timeout} seconds")
        return "timeout"

    except Exception as e:
        logger.error(f"Error waiting for user action: {e}")
        return "error"


async def show(browser: AsyncBrowser, logger, timeout: int = 300) -> None:
    """
    Shows the onboarding page and waits for user authentication or navigation.

    Args:
        browser: Playwright browser instance
        logger: Logger instance
        timeout: Maximum time to wait for user action (seconds)
    """
    html_path = Path(__file__).parent / "templates" / "onboarding.html"

    if not html_path.exists():
        logger.error(f"Onboarding template not found: {html_path}")
        return

    page = await browser.new_page()

    try:
        # Load onboarding page
        html_content = html_path.read_text("utf-8")
        await page.set_content(html_content, wait_until="domcontentloaded")
        logger.info("Onboarding page displayed")

        # Wait for user action
        result = await _wait_for_user_action(page, logger, timeout)

        if result == "navigation":
            logger.info("User successfully navigated away from onboarding page")
        elif result == "login_detected":
            logger.info(
                "Authentication activity detected - onboarding considered complete"
            )
        elif result == "timeout":
            logger.warning(
                "Onboarding timed out - user may need to manually close this tab"
            )
        else:
            logger.error("Onboarding completed with errors")

    except Exception as e:
        logger.error(f"Error during onboarding: {e}")
    finally:
        try:
            if not page.is_closed():
                await page.close()
                logger.debug("Onboarding page closed")
        except Exception as e:
            logger.debug(f"Error closing onboarding page: {e}")


async def show_with_retry(
    browser: AsyncBrowser, logger, max_retries: int = 2, timeout: int = 300
) -> None:
    """
    Show onboarding with retry logic for error resilience.

    Args:
        browser: Playwright browser instance
        logger: Logger instance
        max_retries: Maximum number of retry attempts
        timeout: Timeout per attempt
    """
    for attempt in range(max_retries):
        try:
            logger.info(f"Starting onboarding attempt {attempt + 1}/{max_retries}")
            await show(browser, logger, timeout)
            return  # Success

        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(
                    f"Onboarding attempt {attempt + 1} failed: {e}. Retrying..."
                )
                await asyncio.sleep(2)  # Brief delay before retry
            else:
                logger.error(f"All onboarding attempts failed. Last error: {e}")
                raise
