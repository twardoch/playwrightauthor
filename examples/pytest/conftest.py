#!/usr/bin/env python3
# examples/pytest/conftest.py

"""
Pytest configuration and fixtures for PlaywrightAuthor integration.

This module provides reusable fixtures for browser automation testing with
proper setup, teardown, and error handling.
"""

import asyncio
from contextlib import contextmanager

import pytest

from playwrightauthor import AsyncBrowser, Browser


def pytest_configure(config):
    """Configure pytest markers for test categorization."""
    config.addinivalue_line("markers", "smoke: Quick smoke tests")
    config.addinivalue_line("markers", "auth: Authentication-related tests")
    config.addinivalue_line("markers", "profile: Multi-profile tests")
    config.addinivalue_line("markers", "performance: Performance tests")
    config.addinivalue_line("markers", "slow: Slow-running tests")


@pytest.fixture(scope="session")
def browser_config():
    """
    Session-scoped browser configuration.

    Returns configuration dictionary that can be customized per test session.
    """
    return {
        "verbose": True,  # Enable detailed logging for debugging
        "profile": "pytest-default",  # Default profile for tests
    }


@pytest.fixture
def browser(browser_config):
    """
    Function-scoped browser fixture for synchronous tests.

    Provides a fresh browser instance for each test with proper cleanup.
    Each test gets its own browser instance to avoid state pollution.

    Args:
        browser_config: Session configuration for browser setup

    Yields:
        Browser: Authenticated browser instance ready for automation

    Example:
        def test_page_title(browser):
            page = browser.new_page()
            page.goto("https://github.com")
            assert "GitHub" in page.title()
    """
    browser_instance = None
    try:
        browser_instance = Browser(
            verbose=browser_config["verbose"], profile=browser_config["profile"]
        )

        # Enter the context manager and yield the browser
        playwright_browser = browser_instance.__enter__()
        yield playwright_browser

    except Exception as e:
        pytest.fail(f"Failed to initialize browser: {e}")

    finally:
        # Ensure proper cleanup
        if browser_instance:
            try:
                browser_instance.__exit__(None, None, None)
            except Exception as cleanup_error:
                # Log cleanup errors but don't fail the test
                print(f"Warning: Browser cleanup error: {cleanup_error}")


@pytest.fixture
async def async_browser(browser_config):
    """
    Function-scoped async browser fixture for asynchronous tests.

    Provides a fresh async browser instance for each test with proper cleanup.
    Use this fixture for tests that require async/await patterns.

    Args:
        browser_config: Session configuration for browser setup

    Yields:
        AsyncBrowser: Authenticated async browser instance

    Example:
        @pytest.mark.asyncio
        async def test_async_navigation(async_browser):
            page = await async_browser.new_page()
            await page.goto("https://github.com")
            title = await page.title()
            assert "GitHub" in title
    """
    browser_instance = None
    try:
        browser_instance = AsyncBrowser(
            verbose=browser_config["verbose"],
            profile=f"{browser_config['profile']}-async",
        )

        # Enter the async context manager and yield the browser
        playwright_browser = await browser_instance.__aenter__()
        yield playwright_browser

    except Exception as e:
        pytest.fail(f"Failed to initialize async browser: {e}")

    finally:
        # Ensure proper cleanup
        if browser_instance:
            try:
                await browser_instance.__aexit__(None, None, None)
            except Exception as cleanup_error:
                print(f"Warning: Async browser cleanup error: {cleanup_error}")


@pytest.fixture
def profile_browser():
    """
    Fixture factory for creating browsers with specific profiles.

    Returns a function that creates browser instances with custom profiles.
    Useful for testing scenarios that require multiple isolated browser sessions.

    Returns:
        function: Factory function for creating profile-specific browsers

    Example:
        def test_multi_account(profile_browser):
            with profile_browser("work") as work_browser:
                work_page = work_browser.new_page()
                work_page.goto("https://mail.google.com")

            with profile_browser("personal") as personal_browser:
                personal_page = personal_browser.new_page()
                personal_page.goto("https://mail.google.com")
    """

    @contextmanager
    def _create_profile_browser(profile_name: str, verbose: bool = True):
        """Create a browser with the specified profile."""
        browser_instance = None
        try:
            browser_instance = Browser(
                verbose=verbose, profile=f"pytest-{profile_name}"
            )
            playwright_browser = browser_instance.__enter__()
            yield playwright_browser
        except Exception as e:
            pytest.fail(f"Failed to create browser with profile '{profile_name}': {e}")
        finally:
            if browser_instance:
                try:
                    browser_instance.__exit__(None, None, None)
                except Exception as cleanup_error:
                    print(f"Warning: Profile browser cleanup error: {cleanup_error}")

    return _create_profile_browser


@pytest.fixture(scope="session")
def test_urls():
    """
    Session-scoped fixture providing common test URLs.

    Returns:
        dict: Dictionary of commonly used URLs for testing
    """
    return {
        "github": "https://github.com",
        "google": "https://www.google.com",
        "example": "https://example.com",
        "httpbin": "https://httpbin.org",
        "github_login": "https://github.com/login",
    }


@pytest.fixture
def wait_for_element():
    """
    Utility fixture for waiting for elements with timeout.

    Returns function that waits for elements to appear with proper error handling.

    Returns:
        function: Element waiting utility with timeout handling
    """

    def _wait_for_element(page, selector: str, timeout: int = 30000):
        """
        Wait for element to be visible with timeout.

        Args:
            page: Playwright page object
            selector: CSS selector for the element
            timeout: Maximum wait time in milliseconds

        Returns:
            Element handle if found

        Raises:
            AssertionError: If element is not found within timeout
        """
        try:
            element = page.wait_for_selector(selector, timeout=timeout)
            assert element is not None, (
                f"Element '{selector}' not found within {timeout}ms"
            )
            return element
        except Exception as e:
            pytest.fail(f"Failed to find element '{selector}': {e}")

    return _wait_for_element


# Async pytest configuration
@pytest.fixture(scope="session")
def event_loop():
    """
    Session-scoped event loop for async tests.

    Ensures all async tests in the session use the same event loop,
    preventing issues with concurrent async operations.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


# Custom pytest hooks for better error reporting
def pytest_runtest_makereport(item, call):
    """
    Custom test report generation with browser context information.

    Adds browser profile and configuration information to test reports
    for better debugging when tests fail.
    """
    if call.when == "call" and call.excinfo is not None:
        # Add browser context to error reports
        if hasattr(item, "fixturenames") and "browser" in item.fixturenames:
            call.excinfo.value.args = call.excinfo.value.args + (
                f"\nBrowser Profile: {getattr(item.instance, '_browser_profile', 'default')}"
                f"\nTest URL: {getattr(item.instance, '_test_url', 'unknown')}",
            )


# Performance testing utilities
@pytest.fixture
def performance_timer():
    """
    Fixture for measuring test execution time and browser operations.

    Provides utilities for measuring and asserting on performance metrics.

    Returns:
        dict: Performance measurement utilities
    """
    import time

    measurements = {"start_time": None, "measurements": {}}

    def start_timer(name: str = "default"):
        """Start timing a specific operation."""
        measurements["measurements"][name] = {"start": time.time()}
        if measurements["start_time"] is None:
            measurements["start_time"] = time.time()

    def end_timer(name: str = "default") -> float:
        """End timing and return duration in seconds."""
        if name not in measurements["measurements"]:
            pytest.fail(f"Timer '{name}' was not started")

        end_time = time.time()
        start_time = measurements["measurements"][name]["start"]
        duration = end_time - start_time
        measurements["measurements"][name]["duration"] = duration
        return duration

    def assert_duration_under(name: str, max_seconds: float):
        """Assert that an operation completed within the specified time."""
        if name not in measurements["measurements"]:
            pytest.fail(f"Timer '{name}' was not started")

        duration = measurements["measurements"][name].get("duration")
        if duration is None:
            pytest.fail(f"Timer '{name}' was not ended")

        assert duration < max_seconds, (
            f"Operation '{name}' took {duration:.2f}s, expected < {max_seconds}s"
        )

    return {
        "start": start_timer,
        "end": end_timer,
        "assert_under": assert_duration_under,
        "measurements": measurements,
    }
