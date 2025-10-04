# this_file: playwrightauthor/src/playwrightauthor/helpers/interaction.py
"""Browser page interaction utilities."""

from playwright.sync_api import Page


def scroll_page_incremental(
    page: Page, scroll_distance: int = 600, container_selector: str | None = None
) -> None:
    """
    Scroll down incrementally to load more content in infinite-scroll pages.

    The function tries to scroll a specific container first (if provided),
    then falls back to window scrolling if the container doesn't exist or
    isn't scrollable.

    Args:
        page: Playwright page object (sync API)
        scroll_distance: Pixels to scroll (default: 600, ~1.5 rows of cards)
        container_selector: Optional CSS selector for container to scroll.
                          If None or container not found, scrolls window.

    Example:
        >>> from playwrightauthor import Browser
        >>> with Browser() as browser:
        ...     page = browser.page
        ...     page.goto("https://example.com/infinite-scroll")
        ...     # Scroll specific container
        ...     scroll_page_incremental(page, scroll_distance=1200,
        ...                            container_selector='div[data-scroll="true"]')
        ...     # Scroll window
        ...     scroll_page_incremental(page)

    Note:
        Migrated from application-level code. The original version had
        an `aggressive` boolean parameter (600px vs 1200px). This version uses
        the more flexible `scroll_distance` parameter instead.

        For aggressive scrolling (~3 rows): use scroll_distance=1200
        For normal scrolling (~1.5 rows): use scroll_distance=600 (default)

        This is sync-only as it uses sync Page.evaluate().
    """
    # Default to generic infinite-scroll container if none specified
    if container_selector is None:
        container_selector = 'div[fontviewtype="grid"]'  # Default grid container

    try:
        page.evaluate(
            f"""
            (() => {{
                // Try scrolling the specified container
                const container = document.querySelector('{container_selector}');
                if (container && container.scrollHeight > container.clientHeight) {{
                    container.scrollBy(0, {scroll_distance});
                    return;
                }}

                // Fall back to window scroll
                window.scrollBy(0, {scroll_distance});
            }})()
        """
        )
    except Exception:
        # Silently fail - scrolling is not critical
        pass
