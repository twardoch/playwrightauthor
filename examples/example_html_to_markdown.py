#!/usr/bin/env -S uv run --quiet
# this_file: examples/example_html_to_markdown.py
"""
Example demonstrating HTML to Markdown conversion.

The html_to_markdown helper converts HTML content to clean Markdown format,
with options for handling links, images, and formatting.
"""

from playwrightauthor import Browser
from playwrightauthor.utils.html import html_to_markdown


def main():
    """Demonstrate HTML to Markdown conversion."""
    print("=== HTML to Markdown Conversion Example ===\n")

    # Example 1: Basic HTML conversion
    print("Example 1: Basic HTML conversion\n")

    basic_html = """
    <h1>Main Title</h1>
    <p>This is a <strong>bold</strong> paragraph with <em>italic</em> text.</p>
    <ul>
        <li>First item</li>
        <li>Second item</li>
        <li>Third item</li>
    </ul>
    """

    markdown = html_to_markdown(basic_html)
    print("Input HTML:")
    print(basic_html)
    print("\nOutput Markdown:")
    print(markdown)
    print()

    # Example 2: HTML with links
    print("\nExample 2: HTML with links\n")

    links_html = """
    <h2>Resources</h2>
    <p>Check out <a href="https://example.com">Example Site</a> for more info.</p>
    <p>Also see <a href="https://docs.example.com">Documentation</a>.</p>
    """

    markdown_links = html_to_markdown(links_html)
    print("Input HTML:")
    print(links_html)
    print("\nOutput Markdown:")
    print(markdown_links)
    print()

    # Example 3: HTML with images
    print("\nExample 3: HTML with images\n")

    images_html = """
    <h2>Gallery</h2>
    <p>Here's an image:</p>
    <img src="https://example.com/image.png" alt="Example Image">
    <p>And another: <img src="/local/image.jpg" alt="Local"></p>
    """

    markdown_images = html_to_markdown(images_html)
    print("Input HTML:")
    print(images_html)
    print("\nOutput Markdown:")
    print(markdown_images)
    print()

    # Example 4: Extract and convert from live page
    print("\nExample 4: Extract and convert from live page\n")

    with Browser(verbose=False) as browser:
        page = browser.page
        page.goto("https://example.com")

        # Get the page HTML
        page_html = page.content()

        # Convert entire page to markdown
        full_markdown = html_to_markdown(page_html)
        print("Full page converted to Markdown:")
        print("-" * 50)
        print(full_markdown[:500])  # Show first 500 chars
        print("...")
        print("-" * 50)
        print(f"\nTotal length: {len(full_markdown)} characters")
        print()

        # Example 5: Convert specific element
        print("\nExample 5: Convert specific element\n")

        # Get just the body content
        body_html = page.inner_html("body")
        body_markdown = html_to_markdown(body_html)

        print("Body content as Markdown:")
        print("-" * 50)
        print(body_markdown)
        print("-" * 50)
        print()

        # Example 6: Convert with custom processing
        print("\nExample 6: Code blocks and formatting\n")

        code_html = """
        <h2>Code Example</h2>
        <p>Here's some Python code:</p>
        <pre><code>def hello():
    print("Hello, World!")
    return True</code></pre>
        <p>And some inline <code>code</code> too.</p>
        """

        code_markdown = html_to_markdown(code_html)
        print("Input HTML:")
        print(code_html)
        print("\nOutput Markdown:")
        print(code_markdown)
        print()

    # Example 7: Compare before and after
    print("\nExample 7: Before/After comparison\n")

    complex_html = """
    <article>
        <h1>Article Title</h1>
        <p class="byline">By <strong>John Doe</strong></p>
        <p>First paragraph with <a href="https://example.com">a link</a>.</p>
        <h2>Section 1</h2>
        <p>Content with <em>emphasis</em> and <strong>strong text</strong>.</p>
        <ol>
            <li>Ordered item 1</li>
            <li>Ordered item 2</li>
        </ol>
        <blockquote>
            <p>A famous quote goes here.</p>
        </blockquote>
    </article>
    """

    complex_markdown = html_to_markdown(complex_html)

    print("BEFORE (HTML):")
    print("=" * 50)
    print(complex_html)
    print()
    print("AFTER (Markdown):")
    print("=" * 50)
    print(complex_markdown)
    print()

    # Example 8: Handling tables
    print("\nExample 8: Tables\n")

    table_html = """
    <table>
        <thead>
            <tr>
                <th>Name</th>
                <th>Age</th>
                <th>City</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>Alice</td>
                <td>30</td>
                <td>New York</td>
            </tr>
            <tr>
                <td>Bob</td>
                <td>25</td>
                <td>London</td>
            </tr>
        </tbody>
    </table>
    """

    table_markdown = html_to_markdown(table_html)
    print("Table HTML:")
    print(table_html)
    print("\nTable Markdown:")
    print(table_markdown)
    print()

    print("=== Conversion Complete ===")


if __name__ == "__main__":
    main()
