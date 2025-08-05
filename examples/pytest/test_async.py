#!/usr/bin/env python3
# examples/pytest/test_async.py

"""
Async browser automation tests using PlaywrightAuthor with pytest.

This module demonstrates asynchronous browser automation patterns including
concurrent operations, async context management, and performance optimization.
"""

import asyncio

import pytest
from playwright.async_api import expect


@pytest.mark.asyncio
async def test_async_browser_initialization(async_browser):
    """
    Test that async browser initializes correctly and is ready for automation.

    Demonstrates basic async browser setup and page creation patterns.
    """
    # Verify async browser is ready
    assert async_browser is not None
    assert hasattr(async_browser, "new_page")

    # Create a page asynchronously
    page = await async_browser.new_page()
    assert page is not None

    # Clean up
    await page.close()


@pytest.mark.asyncio
async def test_async_navigation(async_browser, test_urls):
    """
    Test basic async page navigation and content verification.

    Demonstrates the fundamental async navigation pattern with proper
    await handling for network operations.
    """
    page = await async_browser.new_page()

    # Navigate asynchronously
    response = await page.goto(test_urls["example"])
    assert response.status == 200

    # Verify page loaded correctly
    title = await page.title()
    assert "Example Domain" in title

    # Verify page content asynchronously
    heading = page.locator("h1")
    await expect(heading).to_have_text("Example Domain")

    await page.close()


@pytest.mark.asyncio
async def test_concurrent_page_operations(async_browser, test_urls):
    """
    Test concurrent operations on multiple pages simultaneously.

    Demonstrates the power of async automation for handling multiple
    pages concurrently, which is much faster than sequential operations.
    """
    # Create multiple pages concurrently
    pages = await asyncio.gather(*[async_browser.new_page() for _ in range(3)])

    urls = [test_urls["example"], test_urls["github"], test_urls["google"]]

    try:
        # Navigate all pages concurrently
        responses = await asyncio.gather(
            *[page.goto(url) for page, url in zip(pages, urls, strict=False)]
        )

        # Verify all responses are successful
        for response in responses:
            assert response.status == 200

        # Get all page titles concurrently
        titles = await asyncio.gather(*[page.title() for page in pages])

        # Verify expected titles
        assert "Example Domain" in titles[0]
        assert "GitHub" in titles[1]
        assert "Google" in titles[2]

        print(f"✓ Successfully loaded {len(pages)} pages concurrently")

    finally:
        # Clean up all pages concurrently
        await asyncio.gather(*[page.close() for page in pages], return_exceptions=True)


@pytest.mark.asyncio
async def test_async_form_interaction(async_browser, test_urls):
    """
    Test async form filling and submission patterns.

    Demonstrates async form automation with proper wait handling
    and response verification.
    """
    page = await async_browser.new_page()

    # Navigate to httpbin forms page
    await page.goto(f"{test_urls['httpbin']}/forms/post")

    # Fill form fields concurrently where possible
    await asyncio.gather(
        page.fill('input[name="custname"]', "Async Test Customer"),
        page.fill('input[name="custtel"]', "555-987-6543"),
        page.fill('input[name="custemail"]', "async@example.com"),
    )

    # Select dropdown and radio button
    await page.select_option('select[name="size"]', "large")
    await page.check('input[value="cheese"]')

    # Fill textarea
    await page.fill('textarea[name="comments"]', "Async automation test")

    # Submit form and wait for navigation
    async with page.expect_navigation():
        await page.click('input[type="submit"]')

    # Verify submission was successful
    assert "httpbin.org" in page.url

    # Check response contains our data
    content = await page.content()
    assert "Async Test Customer" in content
    assert "async@example.com" in content

    await page.close()


@pytest.mark.asyncio
async def test_async_javascript_execution(async_browser, test_urls):
    """
    Test async JavaScript execution and evaluation.

    Demonstrates running JavaScript in the browser context
    asynchronously and extracting complex data structures.
    """
    page = await async_browser.new_page()
    await page.goto(test_urls["example"])

    # Execute simple JavaScript asynchronously
    title = await page.evaluate("() => document.title")
    assert title == "Example Domain"

    # Execute complex JavaScript with async operations
    page_analysis = await page.evaluate("""
        async () => {
            // Simulate some async operations in the browser
            await new Promise(resolve => setTimeout(resolve, 100));

            return {
                url: window.location.href,
                title: document.title,
                elements: {
                    headings: document.querySelectorAll('h1, h2, h3, h4, h5, h6').length,
                    paragraphs: document.querySelectorAll('p').length,
                    links: document.querySelectorAll('a').length
                },
                performance: {
                    loadTime: performance.timing.loadEventEnd - performance.timing.navigationStart,
                    domContentLoaded: performance.timing.domContentLoadedEventEnd - performance.timing.navigationStart
                },
                features: {
                    hasLocalStorage: !!window.localStorage,
                    hasSessionStorage: !!window.sessionStorage,
                    supportsWebGL: !!window.WebGLRenderingContext
                }
            };
        }
    """)

    # Verify the analysis results
    assert page_analysis["url"] == test_urls["example"]
    assert page_analysis["title"] == "Example Domain"
    assert page_analysis["elements"]["headings"] >= 1
    assert isinstance(page_analysis["performance"]["loadTime"], int | float)
    assert page_analysis["features"]["hasLocalStorage"]

    await page.close()


@pytest.mark.asyncio
@pytest.mark.slow
async def test_async_performance_timing(async_browser, test_urls):
    """
    Test async performance measurement and timing analysis.

    Demonstrates measuring page load performance and network timing
    using async patterns for accurate measurements.
    """
    page = await async_browser.new_page()

    # Measure navigation timing
    start_time = asyncio.get_event_loop().time()
    await page.goto(test_urls["github"])
    navigation_time = asyncio.get_event_loop().time() - start_time

    # Get detailed timing from the browser
    timing_info = await page.evaluate("""
        () => {
            const timing = performance.timing;
            const navigation = performance.getEntriesByType('navigation')[0];

            return {
                // Legacy timing API
                legacyTiming: {
                    total: timing.loadEventEnd - timing.navigationStart,
                    dns: timing.domainLookupEnd - timing.domainLookupStart,
                    connect: timing.connectEnd - timing.connectStart,
                    response: timing.responseEnd - timing.responseStart,
                    dom: timing.domContentLoadedEventEnd - timing.domContentLoadedEventStart
                },
                // Modern navigation timing API
                navigationTiming: navigation ? {
                    total: navigation.loadEventEnd - navigation.fetchStart,
                    dns: navigation.domainLookupEnd - navigation.domainLookupStart,
                    connect: navigation.connectEnd - navigation.connectStart,
                    response: navigation.responseEnd - navigation.responseStart,
                    dom: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart
                } : null
            };
        }
    """)

    print(f"Navigation time (Python): {navigation_time:.2f}s")

    if timing_info["navigationTiming"]:
        nav_timing = timing_info["navigationTiming"]
        print(f"Total load time: {nav_timing['total']:.0f}ms")
        print(f"DNS lookup: {nav_timing['dns']:.0f}ms")
        print(f"Connection: {nav_timing['connect']:.0f}ms")
        print(f"Response: {nav_timing['response']:.0f}ms")
        print(f"DOM processing: {nav_timing['dom']:.0f}ms")

        # Assert reasonable performance
        assert nav_timing["total"] < 30000  # 30 seconds max

    await page.close()


@pytest.mark.asyncio
async def test_async_element_waiting(async_browser, test_urls):
    """
    Test async element waiting and interaction patterns.

    Demonstrates proper async waiting for dynamic content and
    element state changes.
    """
    page = await async_browser.new_page()
    await page.goto(test_urls["github"])

    # Wait for search input asynchronously
    search_input = page.locator('[placeholder*="Search"]').first
    await search_input.wait_for(state="visible", timeout=10000)

    # Interact with element asynchronously
    await search_input.click()
    await search_input.fill("playwright async")

    # Wait for search suggestions (if they appear)
    try:
        suggestions = page.locator('[role="listbox"], .suggestions').first
        await suggestions.wait_for(state="visible", timeout=3000)
        print("✓ Search suggestions appeared")
    except Exception:
        print("ℹ No search suggestions detected")

    await page.close()


@pytest.mark.asyncio
async def test_async_screenshot_generation(async_browser, test_urls, tmp_path):
    """
    Test async screenshot generation and file operations.

    Demonstrates taking screenshots asynchronously with proper
    file handling and cleanup.
    """
    page = await async_browser.new_page()
    await page.goto(test_urls["example"])

    # Take screenshots asynchronously
    screenshot_tasks = []

    # Full page screenshot
    full_screenshot_path = tmp_path / "async_full_page.png"
    screenshot_tasks.append(
        page.screenshot(path=str(full_screenshot_path), full_page=True)
    )

    # Element screenshot
    heading = page.locator("h1")
    element_screenshot_path = tmp_path / "async_heading.png"
    screenshot_tasks.append(heading.screenshot(path=str(element_screenshot_path)))

    # Execute screenshots concurrently
    await asyncio.gather(*screenshot_tasks)

    # Verify screenshots were created
    assert full_screenshot_path.exists()
    assert element_screenshot_path.exists()
    assert full_screenshot_path.stat().st_size > 0
    assert element_screenshot_path.stat().st_size > 0

    await page.close()


@pytest.mark.asyncio
async def test_async_error_handling(async_browser):
    """
    Test async error handling patterns and exception management.

    Demonstrates proper async exception handling for common
    failure scenarios in browser automation.
    """
    page = await async_browser.new_page()

    # Test async navigation error
    with pytest.raises(Exception):
        await page.goto(
            "https://invalid-domain-for-testing.invalid",
            wait_until="load",
            timeout=5000,
        )

    # Test async element waiting timeout
    await page.goto("https://example.com")
    with pytest.raises(Exception):
        await page.wait_for_selector(".non-existent-element", timeout=2000)

    # Test async JavaScript execution error
    with pytest.raises(Exception):
        await page.evaluate("async () => { throw new Error('Async test error'); }")

    await page.close()


@pytest.mark.asyncio
@pytest.mark.slow
async def test_async_concurrent_automation_workflow(async_browser, test_urls):
    """
    Test complex concurrent automation workflow.

    Demonstrates a realistic async automation scenario with multiple
    concurrent operations and proper resource management.
    """

    # Define a complex automation task
    async def analyze_page(url, page_name):
        """Analyze a single page and return metrics."""
        page = await async_browser.new_page()
        try:
            # Navigate and measure timing
            start_time = asyncio.get_event_loop().time()
            await page.goto(url)
            load_time = asyncio.get_event_loop().time() - start_time

            # Analyze page content
            analysis = await page.evaluate("""
                () => ({
                    title: document.title,
                    headings: document.querySelectorAll('h1, h2, h3').length,
                    paragraphs: document.querySelectorAll('p').length,
                    links: document.querySelectorAll('a').length,
                    images: document.querySelectorAll('img').length,
                    scripts: document.querySelectorAll('script').length,
                    stylesheets: document.querySelectorAll('link[rel="stylesheet"]').length
                })
            """)

            return {
                "page_name": page_name,
                "url": url,
                "load_time": load_time,
                "analysis": analysis,
            }

        finally:
            await page.close()

    # Analyze multiple pages concurrently
    pages_to_analyze = [
        (test_urls["example"], "Example"),
        (test_urls["github"], "GitHub"),
        (test_urls["google"], "Google"),
    ]

    # Execute all analyses concurrently
    results = await asyncio.gather(
        *[analyze_page(url, name) for url, name in pages_to_analyze]
    )

    # Verify all analyses completed successfully
    assert len(results) == 3

    for result in results:
        assert result["load_time"] > 0
        assert len(result["analysis"]["title"]) > 0
        assert result["analysis"]["headings"] >= 0
        print(
            f"✓ {result['page_name']}: {result['analysis']['title']} "
            f"({result['load_time']:.2f}s)"
        )

    print("✓ Concurrent automation workflow completed successfully")


@pytest.mark.asyncio
async def test_async_context_manager_cleanup(async_browser):
    """
    Test proper async context manager cleanup and resource management.

    Verifies that async resources are properly cleaned up even
    when exceptions occur during execution.
    """
    pages_created = []

    try:
        # Create multiple pages
        for _i in range(3):
            page = await async_browser.new_page()
            pages_created.append(page)
            await page.goto("https://example.com")

        # Simulate an error
        raise ValueError("Simulated error for cleanup testing")

    except ValueError:
        # Expected error - now verify cleanup
        pass

    # Clean up pages (normally handled by fixtures)
    cleanup_results = await asyncio.gather(
        *[page.close() for page in pages_created], return_exceptions=True
    )

    # Verify cleanup succeeded (or returned exceptions)
    assert len(cleanup_results) == 3
    print("✓ Async cleanup handling test completed")
