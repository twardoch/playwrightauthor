# this_file: tests/test_integration.py
import pytest
from playwrightauthor import Browser


def test_browser_integration():
    """A basic integration test to ensure the Browser class can be instantiated and used."""
    try:
        with Browser(verbose=True) as browser:
            assert browser is not None
            page = browser.new_page()
            page.goto("https://www.google.com")
            assert "Google" in page.title()
            page.close()
    except Exception as e:
        pytest.fail(f"Browser integration test failed with an exception: {e}")
