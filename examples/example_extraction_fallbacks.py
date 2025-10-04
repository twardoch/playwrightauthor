#!/usr/bin/env -S uv run --quiet
# this_file: examples/example_extraction_fallbacks.py
"""
Example demonstrating extraction with multiple selector fallbacks.

The extract_with_fallbacks helper tries multiple selectors in order
until one succeeds, with optional validation.
"""

import asyncio

from playwrightauthor import AsyncBrowser, Browser
from playwrightauthor.helpers.extraction import (
    extract_with_fallbacks,
    extract_with_fallbacks_async,
)


def main_sync():
    """Demonstrate synchronous extraction with fallbacks."""
    print("=== Synchronous Extraction with Fallbacks ===\n")

    with Browser(verbose=False) as browser:
        page = browser.page
        page.goto("https://example.com")

        # Example 1: Extract with multiple selectors
        print("Example 1: Multiple selector fallbacks\n")

        # Try multiple selectors in order
        heading = extract_with_fallbacks(
            page,
            selectors=[
                "h1.main-title",  # Try specific class first
                "h1#title",  # Try specific ID
                "h1",  # Fall back to any h1
                "h2",  # Last resort: h2
            ],
            extract_fn=lambda el: el.inner_text(),
        )

        if heading:
            print(f"✓ Found heading: '{heading}'")
            print("  (Used fallback selector since specific classes/IDs don't exist)\n")
        else:
            print("✗ No heading found\n")

        # Example 2: Extract with validation
        print("Example 2: Extraction with validation\n")

        def is_valid_heading(text):
            """Validate that heading is non-empty and reasonable length."""
            return text and len(text) > 0 and len(text) < 100

        validated_heading = extract_with_fallbacks(
            page,
            selectors=["h1", "h2", "h3"],
            extract_fn=lambda el: el.inner_text(),
            validate_fn=is_valid_heading,
        )

        if validated_heading:
            print(f"✓ Valid heading: '{validated_heading}'")
            print(f"  Length: {len(validated_heading)} characters\n")
        else:
            print("✗ No valid heading found\n")

        # Example 3: Extract attribute instead of text
        print("Example 3: Extract link href with fallbacks\n")

        page.goto("https://httpbin.org/links/5/0")  # Page with links

        # Extract href from first available link
        link_url = extract_with_fallbacks(
            page,
            selectors=[
                "a.primary-link",  # Try specific class
                "a#main-link",  # Try specific ID
                "a",  # Fall back to any link
            ],
            extract_fn=lambda el: el.get_attribute("href"),
        )

        if link_url:
            print(f"✓ Found link URL: {link_url}\n")
        else:
            print("✗ No link found\n")

        # Example 4: Extract with custom processing
        print("Example 4: Extract and process content\n")

        def extract_and_clean(element):
            """Extract text and clean it."""
            text = element.inner_text()
            return " ".join(text.split())  # Normalize whitespace

        cleaned_text = extract_with_fallbacks(
            page,
            selectors=["p", "div", "span"],
            extract_fn=extract_and_clean,
        )

        if cleaned_text:
            print(f"✓ Cleaned text: '{cleaned_text}'\n")
        else:
            print("✗ No text content found\n")


async def main_async():
    """Demonstrate asynchronous extraction with fallbacks."""
    print("\n=== Asynchronous Extraction with Fallbacks ===\n")

    async with AsyncBrowser(verbose=False) as browser:
        page = browser.page
        await page.goto("https://example.com")

        # Example: Async extraction with fallbacks
        print("Example: Async multi-selector extraction\n")

        heading = await extract_with_fallbacks_async(
            page,
            selectors=["h1.title", "h1", "h2"],
            extract_fn=lambda el: el.inner_text(),
        )

        if heading:
            print(f"✓ Found heading (async): '{heading}'")
        else:
            print("✗ No heading found (async)")

        # Example: Extract multiple elements
        print("\nExample: Extract from multiple elements\n")

        page_text = await extract_with_fallbacks_async(
            page,
            selectors=["p", "div"],
            extract_fn=lambda el: el.inner_text(),
            extract_all=True,  # Get all matching elements
        )

        if page_text:
            print(f"✓ Found {len(page_text)} text elements:")
            for i, text in enumerate(page_text[:3], 1):  # Show first 3
                print(f"  {i}. {text[:50]}...")  # Truncate long text
        else:
            print("✗ No text elements found")


def main():
    """Run both sync and async examples."""
    # Run sync example
    main_sync()

    # Run async example
    asyncio.run(main_async())

    print("\n=== Extraction Complete ===")


if __name__ == "__main__":
    main()
