# this_file: tests/test_author.py
import pytest

from playwrightauthor import AsyncBrowser, Browser


@pytest.mark.skip(
    reason="This is an integration test that requires a live Chrome instance and potentially user interaction."
)
def test_browser_smoke():
    """A basic smoke test to ensure the Browser class can be instantiated."""
    try:
        with Browser(verbose=True) as browser:
            assert browser is not None
            page = browser.new_page()
            page.goto("https://www.google.com")
            assert "Google" in page.title()
            page.close()
    except Exception as e:
        pytest.fail(f"Browser smoke test failed with an exception: {e}")


@pytest.mark.skip(
    reason="This is an integration test that requires a live Chrome instance and potentially user interaction."
)
@pytest.mark.asyncio
async def test_async_browser_smoke():
    """A basic smoke test to ensure the AsyncBrowser class can be instantiated."""
    try:
        async with AsyncBrowser(verbose=True) as browser:
            assert browser is not None
            page = await browser.new_page()
            await page.goto("https://www.duckduckgo.com")
            title = await page.title()
            assert "DuckDuckGo" in title
            await page.close()
    except Exception as e:
        pytest.fail(f"AsyncBrowser smoke test failed with an exception: {e}")
