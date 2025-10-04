# this_file: playwrightauthor/src/playwrightauthor/helpers/extraction.py
"""Content extraction utilities with fallback selector patterns."""

from collections.abc import Callable

from playwright.async_api import Page as AsyncPage
from playwright.sync_api import Page as SyncPage


def extract_with_fallbacks(
    page: SyncPage,
    selectors: list[str],
    validate_fn: Callable[[str], bool] | None = None,
    attribute: str = "inner_text",
) -> str | None:
    """Extract content by trying fallback selectors in order (sync version).

    Tries each selector in order until one returns content. Optionally validates
    the extracted content with a custom function.

    Args:
        page: Playwright page object (sync API)
        selectors: List of CSS selectors to try in order
        validate_fn: Optional function to validate extracted text.
                    Should return True if text is valid, False otherwise.
        attribute: Attribute to extract ('inner_text', 'inner_html', 'text_content')

    Returns:
        Extracted string if any selector succeeds, None if all fail

    Example:
        >>> from playwrightauthor import Browser
        >>> with Browser() as browser:
        ...     page = browser.page
        ...     page.goto("https://example.com")
        ...     # Try multiple selectors
        ...     content = extract_with_fallbacks(
        ...         page,
        ...         selectors=['.main-content', '#content', 'article', 'body'],
        ...         validate_fn=lambda text: len(text) > 100
        ...     )

    Note:
        This is the sync version for use with Browser (sync API).
        Use async_extract_with_fallbacks for AsyncBrowser.

        Originally extracted from playpi.html.extract_research_content and
        virginia-clemm-poe.updater._extract_with_fallback_selectors.
    """
    for selector in selectors:
        try:
            element = page.locator(selector).first
            if element.count() > 0:
                # Extract the requested attribute
                if attribute == "inner_text":
                    text = element.inner_text()
                elif attribute == "inner_html":
                    text = element.inner_html()
                elif attribute == "text_content":
                    text = element.text_content() or ""
                else:
                    raise ValueError(f"Unknown attribute: {attribute}")

                # Validate if function provided
                if text and (not validate_fn or validate_fn(text)):
                    return text
        except Exception:
            # Selector failed, try next one
            continue

    return None


async def async_extract_with_fallbacks(
    page: AsyncPage,
    selectors: list[str],
    validate_fn: Callable[[str], bool] | None = None,
    attribute: str = "inner_text",
) -> str | None:
    """Extract content by trying fallback selectors in order (async version).

    Async version of extract_with_fallbacks for use with AsyncBrowser.

    Args:
        page: Playwright page object (async API)
        selectors: List of CSS selectors to try in order
        validate_fn: Optional function to validate extracted text.
                    Should return True if text is valid, False otherwise.
        attribute: Attribute to extract ('inner_text', 'inner_html', 'text_content')

    Returns:
        Extracted string if any selector succeeds, None if all fail

    Example:
        >>> from playwrightauthor import AsyncBrowser
        >>> async with AsyncBrowser() as browser:
        ...     page = browser.page
        ...     await page.goto("https://example.com")
        ...     # Try multiple selectors
        ...     content = await async_extract_with_fallbacks(
        ...         page,
        ...         selectors=['.main-content', '#content', 'article', 'body'],
        ...         validate_fn=lambda text: len(text) > 100
        ...     )

    Note:
        This is the async version for use with AsyncBrowser.
        Use extract_with_fallbacks for Browser (sync API).
    """
    for selector in selectors:
        try:
            element = page.locator(selector).first
            if await element.count() > 0:
                # Extract the requested attribute
                if attribute == "inner_text":
                    text = await element.inner_text()
                elif attribute == "inner_html":
                    text = await element.inner_html()
                elif attribute == "text_content":
                    text = await element.text_content() or ""
                else:
                    raise ValueError(f"Unknown attribute: {attribute}")

                # Validate if function provided
                if text and (not validate_fn or validate_fn(text)):
                    return text
        except Exception:
            # Selector failed, try next one
            continue

    return None
