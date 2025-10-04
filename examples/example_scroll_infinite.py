#!/usr/bin/env -S uv run --quiet
# this_file: examples/example_scroll_infinite.py
"""
Example demonstrating infinite scroll handling using scroll_page_incremental.

This helper function handles both window scrolling and container scrolling,
waiting for new content to load after each scroll.
"""

from playwrightauthor import Browser
from playwrightauthor.helpers.interaction import scroll_page_incremental


def main():
    """Demonstrate infinite scroll handling."""
    print("=== Infinite Scroll Example ===\n")

    with Browser(verbose=False) as browser:
        page = browser.page

        # Example 1: Scroll entire window (typical infinite scroll)
        print("Example 1: Scrolling entire window\n")
        page.goto("https://httpbin.org/links/20/0")  # Page with 20 links

        # Count elements before scrolling
        initial_links = page.query_selector_all("a")
        print(f"Initial links visible: {len(initial_links)}")

        # Scroll incrementally (simulating infinite scroll behavior)
        print("Scrolling down in increments...")
        for i in range(3):
            scroll_page_incremental(
                page,
                distance=500,  # Scroll 500px each time
                max_scrolls=2,  # Maximum 2 scrolls per call
                wait_after_scroll_ms=300,  # Wait 300ms after each scroll
            )

            # Check element count (in real infinite scroll, this would increase)
            current_links = page.query_selector_all("a")
            print(f"  Scroll {i + 1}: {len(current_links)} links visible")

        print(f"\nFinal links visible: {len(current_links)}")

        # Example 2: Scroll specific container
        print("\n\nExample 2: Scrolling specific container\n")
        page.goto("https://example.com")

        # Create a scrollable container with JavaScript
        page.evaluate(
            """() => {
            const container = document.createElement('div');
            container.id = 'scroll-container';
            container.style.cssText = 'height: 300px; overflow-y: scroll; border: 1px solid black;';

            // Add lots of content
            for(let i = 0; i < 50; i++) {
                const p = document.createElement('p');
                p.textContent = `Item ${i+1}`;
                p.className = 'scroll-item';
                container.appendChild(p);
            }

            document.body.appendChild(container);
        }"""
        )

        # Count initial items in view
        items_in_view = page.evaluate(
            """() => {
            const container = document.getElementById('scroll-container');
            const items = Array.from(container.querySelectorAll('.scroll-item'));
            const containerRect = container.getBoundingClientRect();

            return items.filter(item => {
                const rect = item.getBoundingClientRect();
                return rect.top >= containerRect.top && rect.bottom <= containerRect.bottom;
            }).length;
        }"""
        )
        print(f"Items initially in view: {items_in_view}")

        # Scroll the container
        print("Scrolling container incrementally...")
        scroll_page_incremental(
            page,
            selector="#scroll-container",  # Scroll this specific element
            distance=100,  # Scroll 100px at a time
            max_scrolls=5,  # Scroll 5 times
            wait_after_scroll_ms=200,
        )

        # Check scroll position
        scroll_position = page.evaluate(
            """() => {
            const container = document.getElementById('scroll-container');
            return container.scrollTop;
        }"""
        )
        print(f"Final scroll position: {scroll_position}px")

        # Example 3: Scroll until no more content loads
        print("\n\nExample 3: Scroll until bottom reached\n")

        # Track scroll position
        last_scroll_height = 0
        scroll_count = 0
        max_attempts = 10

        while scroll_count < max_attempts:
            # Get current scroll height
            current_scroll_height = page.evaluate("document.body.scrollHeight")

            # If height hasn't changed, we've reached the bottom
            if current_scroll_height == last_scroll_height:
                print(f"✓ Reached bottom after {scroll_count} scrolls")
                break

            # Scroll down
            scroll_page_incremental(
                page, distance=500, max_scrolls=1, wait_after_scroll_ms=300
            )

            last_scroll_height = current_scroll_height
            scroll_count += 1
            print(f"  Scroll {scroll_count}: Height = {current_scroll_height}px")

        if scroll_count >= max_attempts:
            print(f"⚠ Stopped after {max_attempts} scrolls (max limit)")

        print("\n=== Scroll Complete ===")


if __name__ == "__main__":
    main()
