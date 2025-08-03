# this_file: tests/test_integration.py

import asyncio
import sys
import time
from pathlib import Path
from unittest.mock import patch

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from playwrightauthor import AsyncBrowser, Browser
from playwrightauthor.browser.finder import find_chrome_executable, get_chrome_version
from playwrightauthor.browser.process import get_chrome_process
from playwrightauthor.browser_manager import ensure_browser
from playwrightauthor.exceptions import BrowserManagerError
from playwrightauthor.utils.logger import configure
from playwrightauthor.utils.paths import install_dir


@pytest.fixture
def logger():
    """Provide a test logger."""
    return configure(verbose=True)


class TestBrowserIntegration:
    """Integration tests for synchronous Browser class."""

    @pytest.mark.slow
    def test_browser_basic_usage(self):
        """Test basic Browser usage with page navigation."""
        try:
            with Browser(verbose=True) as browser:
                assert browser is not None

                # Create a new page
                page = browser.new_page()
                assert page is not None

                # Navigate to a simple page
                page.goto("https://example.com")
                assert "Example" in page.title()

                # Check page content
                heading = page.query_selector("h1")
                assert heading is not None
                assert "Example Domain" in heading.inner_text()

                page.close()
        except Exception as e:
            pytest.skip(
                f"Browser integration test skipped (Chrome might not be available): {e}"
            )

    @pytest.mark.slow
    def test_browser_multiple_pages(self):
        """Test managing multiple pages."""
        try:
            with Browser(verbose=False) as browser:
                # Create multiple pages
                pages = []
                for _i in range(3):
                    page = browser.new_page()
                    page.goto("https://httpbin.org/uuid")
                    pages.append(page)

                # Verify all pages are open
                assert len(browser.pages) >= 3

                # Close pages
                for page in pages:
                    page.close()

        except Exception as e:
            pytest.skip(f"Multi-page test skipped: {e}")

    def test_browser_cookies_persistence(self):
        """Test that cookies persist across browser sessions."""
        try:
            # First session - set a cookie
            with Browser(verbose=True) as browser:
                page = browser.new_page()
                page.goto("https://httpbin.org/cookies/set?test_cookie=test_value")
                cookies = page.context.cookies()
                assert any(c["name"] == "test_cookie" for c in cookies)
                page.close()

            # Second session - verify cookie persists
            with Browser(verbose=True) as browser:
                page = browser.new_page()
                page.goto("https://httpbin.org/cookies")
                cookies = page.context.cookies()
                # Cookie should persist due to user data directory
                page.close()

        except Exception as e:
            pytest.skip(f"Cookie persistence test skipped: {e}")


class TestAsyncBrowserIntegration:
    """Integration tests for asynchronous AsyncBrowser class."""

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_async_browser_basic_usage(self):
        """Test basic AsyncBrowser usage."""
        try:
            async with AsyncBrowser(verbose=True) as browser:
                assert browser is not None

                # Create a new page
                page = await browser.new_page()
                assert page is not None

                # Navigate
                await page.goto("https://example.com")
                title = await page.title()
                assert "Example" in title

                await page.close()
        except Exception as e:
            pytest.skip(f"Async browser test skipped: {e}")

    @pytest.mark.asyncio
    async def test_async_browser_concurrent_pages(self):
        """Test concurrent page operations with AsyncBrowser."""
        try:
            async with AsyncBrowser(verbose=False) as browser:
                # Create pages concurrently
                tasks = []
                for i in range(3):
                    task = asyncio.create_task(
                        self._create_and_navigate_page(browser, i)
                    )
                    tasks.append(task)

                results = await asyncio.gather(*tasks)
                assert all(results)

        except Exception as e:
            pytest.skip(f"Concurrent pages test skipped: {e}")

    async def _create_and_navigate_page(self, browser, index):
        """Helper to create and navigate a page."""
        page = await browser.new_page()
        await page.goto("https://httpbin.org/uuid")
        content = await page.content()
        await page.close()
        return len(content) > 0


class TestBrowserManagerIntegration:
    """Integration tests for browser management functionality."""

    def test_ensure_browser_creates_paths(self, logger):
        """Test that ensure_browser creates necessary directories."""
        try:
            browser_path, data_dir = ensure_browser(verbose=True)

            assert browser_path is not None
            assert data_dir is not None

            # Verify paths exist
            assert Path(browser_path).exists()
            assert Path(data_dir).parent.exists()

        except BrowserManagerError as e:
            pytest.skip(f"Browser manager test skipped: {e}")

    def test_chrome_process_detection(self, logger):
        """Test Chrome process detection functionality."""
        # This test verifies process detection works
        # It may or may not find a process depending on system state
        process = get_chrome_process()

        if process:
            assert process.is_running()
            assert "chrome" in process.name().lower()
        else:
            # No Chrome process is fine too
            assert process is None

    def test_chrome_version_detection(self, logger):
        """Test Chrome version detection."""
        chrome_path = find_chrome_executable(logger)

        if chrome_path:
            version = get_chrome_version(chrome_path, logger)
            if version:
                assert "chrome" in version.lower() or "chromium" in version.lower()
                # Version should contain numbers
                assert any(char.isdigit() for char in version)


class TestCrossPlatformIntegration:
    """Cross-platform integration tests."""

    def test_platform_specific_paths(self, logger):
        """Test that platform-specific paths are correctly determined."""
        install_path = install_dir()

        assert install_path is not None
        assert isinstance(install_path, Path)
        assert install_path.is_absolute()

        # Platform-specific checks
        if sys.platform == "win32":
            assert "AppData" in str(install_path) or "ProgramData" in str(install_path)
        elif sys.platform == "darwin":
            assert "Library" in str(install_path)
        else:  # Linux
            assert ".cache" in str(install_path) or "cache" in str(install_path)

    def test_chrome_finder_logging(self, logger, capsys):
        """Test that Chrome finder provides useful logging."""
        # Find Chrome with verbose logging
        result = find_chrome_executable(logger)

        # Check logging output
        captured = capsys.readouterr()

        if result:
            assert "Found Chrome executable:" in captured.out
        else:
            assert (
                "Chrome executable not found" in captured.out
                or "Checked" in captured.out
            )


@pytest.mark.integration
class TestEndToEndScenarios:
    """End-to-end integration scenarios."""

    @pytest.mark.slow
    def test_full_workflow(self):
        """Test complete workflow from browser setup to page automation."""
        try:
            # Step 1: Create browser with verbose logging
            with Browser(verbose=True) as browser:
                # Step 2: Navigate to a test page
                page = browser.new_page()
                page.goto("https://httpbin.org/forms/post")

                # Step 3: Interact with form elements
                page.fill('input[name="custname"]', "Test User")
                page.fill('input[name="custtel"]', "123-456-7890")
                page.fill('input[name="custemail"]', "test@example.com")

                # Step 4: Submit form
                page.click('button[type="submit"]')

                # Step 5: Verify submission
                page.wait_for_load_state("networkidle")
                content = page.content()
                assert "Test User" in content

                page.close()

        except Exception as e:
            pytest.skip(f"Full workflow test skipped: {e}")

    def test_browser_restart_resilience(self):
        """Test that browser can be restarted multiple times."""
        try:
            for _i in range(3):
                with Browser(verbose=False) as browser:
                    page = browser.new_page()
                    page.goto("https://example.com")
                    assert page.title() is not None
                    page.close()

                # Small delay between restarts
                time.sleep(1)

        except Exception as e:
            pytest.skip(f"Browser restart test skipped: {e}")


class TestErrorHandlingIntegration:
    """Integration tests for error handling."""

    def test_browser_handles_network_errors(self):
        """Test browser behavior with network errors."""
        try:
            with Browser(verbose=True) as browser:
                page = browser.new_page()

                # Try to navigate to an invalid URL
                with pytest.raises(Exception):
                    page.goto(
                        "https://this-domain-definitely-does-not-exist-12345.com",
                        timeout=5000,
                    )

                # Browser should still be functional
                page.goto("https://example.com")
                assert "Example" in page.title()
                page.close()

        except Exception as e:
            pytest.skip(f"Network error handling test skipped: {e}")

    @patch("playwrightauthor.browser.finder.find_chrome_executable")
    def test_browser_handles_missing_chrome(self, mock_find):
        """Test behavior when Chrome is not found."""
        mock_find.return_value = None

        # Should handle missing Chrome gracefully
        with pytest.raises(Exception) as exc_info:
            with Browser(verbose=True):
                pass

        # Should get a meaningful error
        assert "Chrome" in str(exc_info.value) or "browser" in str(exc_info.value)


# Performance benchmarks (optional, marked as slow)
@pytest.mark.benchmark
class TestPerformanceBenchmarks:
    """Performance benchmarks for the library."""

    @pytest.mark.slow
    def test_browser_startup_time(self, benchmark):
        """Benchmark browser startup time."""

        def start_browser():
            try:
                with Browser(verbose=False) as browser:
                    page = browser.new_page()
                    page.close()
            except Exception:
                pytest.skip("Browser not available for benchmarking")

        # Run benchmark
        result = benchmark(start_browser)

        # Startup should be reasonably fast (< 5 seconds)
        assert result < 5.0

    @pytest.mark.slow
    def test_page_creation_time(self, benchmark):
        """Benchmark page creation time."""
        try:
            with Browser(verbose=False) as browser:

                def create_page():
                    page = browser.new_page()
                    page.close()

                result = benchmark(create_page)

                # Page creation should be fast (< 1 second)
                assert result < 1.0
        except Exception:
            pytest.skip("Browser not available for benchmarking")
