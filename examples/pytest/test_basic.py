#!/usr/bin/env python3
# examples/pytest/test_basic.py

"""
Basic browser automation tests using PlaywrightAuthor with pytest.

This module demonstrates fundamental browser automation patterns including
navigation, element interaction, and content verification.
"""

import pytest
from playwright.sync_api import expect


@pytest.mark.smoke
def test_browser_initialization(browser):
    """
    Test that browser initializes correctly and is ready for automation.

    This is a fundamental smoke test that verifies the basic browser setup
    and connection is working properly.
    """
    # Verify browser is ready
    assert browser is not None
    assert hasattr(browser, "new_page")

    # Create a page and verify it works
    page = browser.new_page()
    assert page is not None

    # Clean up
    page.close()


@pytest.mark.smoke
def test_simple_navigation(browser, test_urls):
    """
    Test basic page navigation and title verification.

    Demonstrates the most common browser automation pattern:
    navigating to a page and verifying its content.
    """
    page = browser.new_page()

    # Navigate to example.com
    response = page.goto(test_urls["example"])
    assert response.status == 200

    # Verify page loaded correctly
    assert "Example Domain" in page.title()

    # Verify page content
    heading = page.locator("h1")
    expect(heading).to_have_text("Example Domain")

    page.close()


@pytest.mark.smoke
def test_github_homepage(browser, test_urls):
    """
    Test GitHub homepage navigation and basic elements.

    Demonstrates testing against a real-world website with
    dynamic content and modern web technologies.
    """
    page = browser.new_page()

    # Navigate to GitHub
    response = page.goto(test_urls["github"])
    assert response.status == 200

    # Verify GitHub loaded
    assert "GitHub" in page.title()

    # Check for key elements that should be present
    # (These selectors may need updates as GitHub evolves)
    search_input = page.locator('[placeholder*="Search"]').first
    expect(search_input).to_be_visible()

    # Verify we can interact with the search box
    search_input.click()
    search_input.fill("playwright")

    # Clean up
    page.close()


def test_form_interaction(browser, test_urls):
    """
    Test form filling and submission using httpbin.org.

    Demonstrates form automation patterns including input validation,
    dropdown selection, and form submission handling.
    """
    page = browser.new_page()

    # Navigate to httpbin forms page
    page.goto(f"{test_urls['httpbin']}/forms/post")

    # Fill out the form
    page.fill('input[name="custname"]', "Test Customer")
    page.fill('input[name="custtel"]', "555-123-4567")
    page.fill('input[name="custemail"]', "test@example.com")

    # Select from dropdown
    page.select_option('select[name="size"]', "medium")

    # Select radio button
    page.check('input[value="bacon"]')

    # Fill textarea
    page.fill('textarea[name="comments"]', "Test automation with PlaywrightAuthor")

    # Submit form and verify response
    with page.expect_navigation():
        page.click('input[type="submit"]')

    # Verify form was submitted successfully
    assert "httpbin.org" in page.url

    # Check response contains our submitted data
    page_content = page.content()
    assert "Test Customer" in page_content
    assert "test@example.com" in page_content

    page.close()


def test_javascript_execution(browser, test_urls):
    """
    Test JavaScript execution and evaluation in the browser.

    Demonstrates how to execute custom JavaScript and extract
    results from the browser context.
    """
    page = browser.new_page()
    page.goto(test_urls["example"])

    # Execute JavaScript and get result
    result = page.evaluate("() => document.title")
    assert result == "Example Domain"

    # Execute more complex JavaScript
    page_info = page.evaluate("""
        () => ({
            url: window.location.href,
            title: document.title,
            hasLocalStorage: !!window.localStorage,
            userAgent: navigator.userAgent,
            viewport: {
                width: window.innerWidth,
                height: window.innerHeight
            }
        })
    """)

    assert page_info["url"] == test_urls["example"]
    assert page_info["title"] == "Example Domain"
    assert page_info["hasLocalStorage"]
    assert "width" in page_info["viewport"]

    page.close()


def test_screenshot_capture(browser, test_urls, tmp_path):
    """
    Test screenshot capture functionality.

    Demonstrates visual testing capabilities and file handling
    with proper cleanup using pytest's tmp_path fixture.
    """
    page = browser.new_page()
    page.goto(test_urls["example"])

    # Take a full page screenshot
    screenshot_path = tmp_path / "example_page.png"
    page.screenshot(path=str(screenshot_path), full_page=True)

    # Verify screenshot was created
    assert screenshot_path.exists()
    assert screenshot_path.stat().st_size > 0

    # Take element screenshot
    heading = page.locator("h1")
    element_screenshot_path = tmp_path / "heading.png"
    heading.screenshot(path=str(element_screenshot_path))

    assert element_screenshot_path.exists()
    assert element_screenshot_path.stat().st_size > 0

    page.close()


def test_wait_for_element(browser, wait_for_element, test_urls):
    """
    Test element waiting functionality using custom fixture.

    Demonstrates proper element waiting patterns and timeout handling
    using the wait_for_element fixture from conftest.py.
    """
    page = browser.new_page()
    page.goto(test_urls["example"])

    # Wait for page heading to appear
    heading = wait_for_element(page, "h1", timeout=10000)
    assert heading is not None

    # Verify element text
    expect(page.locator("h1")).to_have_text("Example Domain")

    page.close()


@pytest.mark.slow
def test_multiple_pages(browser, test_urls):
    """
    Test handling multiple browser pages simultaneously.

    Demonstrates advanced browser management with multiple tabs/pages
    and proper resource cleanup.
    """
    # Create multiple pages
    pages = []
    urls = [test_urls["example"], test_urls["github"], test_urls["google"]]

    try:
        for url in urls:
            page = browser.new_page()
            page.goto(url)
            pages.append(page)

        # Verify all pages loaded
        assert len(pages) == 3

        # Check each page has expected content
        assert "Example Domain" in pages[0].title()
        assert "GitHub" in pages[1].title()
        assert "Google" in pages[2].title()

        # Test switching between pages
        for i, page in enumerate(pages):
            page.bring_to_front()
            # Verify we can interact with the current page
            assert page.url in urls[i]

    finally:
        # Clean up all pages
        for page in pages:
            try:
                page.close()
            except Exception as e:
                print(f"Warning: Failed to close page: {e}")


def test_error_handling(browser):
    """
    Test proper error handling for common failure scenarios.

    Demonstrates robust error handling patterns for network failures,
    missing elements, and other common issues in browser automation.
    """
    page = browser.new_page()

    # Test navigation to invalid URL
    with pytest.raises(Exception):
        page.goto(
            "https://this-domain-definitely-does-not-exist.invalid",
            wait_until="load",
            timeout=5000,
        )

    # Test waiting for non-existent element
    page.goto("https://example.com")
    with pytest.raises(Exception):
        page.wait_for_selector(".non-existent-element", timeout=2000)

    # Test JavaScript execution error
    with pytest.raises(Exception):
        page.evaluate("() => { throw new Error('Test error'); }")

    page.close()


@pytest.mark.performance
def test_performance_timing(browser, test_urls, performance_timer):
    """
    Test page load performance and timing measurements.

    Demonstrates performance testing patterns using the custom
    performance_timer fixture for timing assertions.
    """
    page = browser.new_page()

    # Measure page navigation time
    performance_timer["start"]("navigation")
    page.goto(test_urls["example"])
    performance_timer["end"]("navigation")

    # Assert navigation completed within reasonable time
    performance_timer["assert_under"]("navigation", 10.0)  # 10 seconds max

    # Measure element interaction time
    performance_timer["start"]("interaction")
    heading = page.locator("h1")
    expect(heading).to_be_visible()
    performance_timer["end"]("interaction")

    # Assert interaction was fast
    performance_timer["assert_under"]("interaction", 2.0)  # 2 seconds max

    page.close()


def test_browser_context_isolation(browser):
    """
    Test that browser context provides proper isolation between tests.

    Verifies that cookies, localStorage, and other browser state
    is properly isolated between test runs.
    """
    page1 = browser.new_page()
    page1.goto("https://example.com")

    # Set some browser state
    page1.evaluate("localStorage.setItem('test-key', 'test-value')")

    # Get cookies (if any)
    page1.context.cookies()

    page1.close()

    # Create new page and verify isolation
    page2 = browser.new_page()
    page2.goto("https://example.com")

    # Check that localStorage is empty (new context)
    page2.evaluate("localStorage.getItem('test-key')")
    # Note: In same profile, localStorage might persist - this depends on setup

    page2.context.cookies()

    # The exact assertions here depend on browser profile configuration
    # For true isolation, you'd use different profiles per test

    page2.close()
