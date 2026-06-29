# this_file: tests/conftest.py
"""
Shared pytest fixtures for the PlaywrightAuthor test suite.

This module provides an autouse fixture that makes ALL tests fast and fully
offline by mocking the three slow layers:

1. Playwright server startup (2 s per call)
2. Chrome for Testing launch / installation (2–40 s per call)
3. npx / subprocess calls to the Puppeteer browser CLI

Individual tests can override any of these mocks by applying their own
``@patch`` decorators; test-level patches are applied *inside* the fixture's
context and therefore take priority.

Tests that genuinely require a live Chrome browser should be marked with
``@pytest.mark.slow`` and run explicitly::

    pytest -m slow
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from playwrightauthor.exceptions import BrowserManagerError


@pytest.fixture(autouse=True)
def _no_real_browser():
    """Autouse fixture: block all real browser, Chrome-install, and Playwright
    startup calls so the entire suite stays fast and offline.

    What gets mocked
    ----------------
    ``playwrightauthor.author.get_sync_playwright``
        Returns a lightweight MagicMock instead of starting the Playwright
        browser server.  ``mock.start()`` returns another MagicMock that
        satisfies the ``.chromium`` attribute lookup in ``Browser.__enter__``.

    ``playwrightauthor.author.get_async_playwright``
        Same treatment for the async path.

    ``playwrightauthor.engines.chrome.ensure_browser``
        Raises ``BrowserManagerError`` immediately, short-circuiting the
        Chrome-launch path in ``ChromeEngineAdapter.start()``.

    ``playwrightauthor.engines.cloak.ensure_cloak_browser``
        Same for the optional CloakBrowser engine.

    ``playwrightauthor.browser.installer.subprocess.run``
        Returns a non-zero exit code, preventing any real ``npx`` download.
    """
    mock_playwright = MagicMock()
    mock_pw_ctx = MagicMock()
    mock_pw_ctx.start.return_value = mock_playwright

    with (
        patch(
            "playwrightauthor.author.get_sync_playwright",
            return_value=mock_pw_ctx,
        ),
        patch(
            "playwrightauthor.author.get_async_playwright",
            return_value=MagicMock(),
        ),
        patch(
            "playwrightauthor.engines.chrome.ensure_browser",
            side_effect=BrowserManagerError(
                "Chrome not available in offline test environment"
            ),
        ),
        patch(
            "playwrightauthor.engines.cloak.ensure_cloak_browser",
            side_effect=BrowserManagerError(
                "CloakBrowser not available in offline test environment"
            ),
        ),
        patch(
            "playwrightauthor.browser.installer.subprocess.run",
            return_value=MagicMock(
                returncode=1, stdout="", stderr="blocked in test environment"
            ),
        ),
    ):
        yield
