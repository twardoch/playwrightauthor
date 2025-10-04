# this_file: tests/test_utils_html.py
"""Tests for utils.html module."""

from playwrightauthor.utils.html import html_to_markdown


def test_html_to_markdown_basic():
    """Test basic HTML to Markdown conversion."""
    html = "<p><strong>Hello</strong> world!</p>"
    md = html_to_markdown(html)
    assert "**Hello**" in md
    assert "world!" in md


def test_html_to_markdown_with_links():
    """Test HTML with links conversion."""
    html = '<p>Visit <a href="https://example.com">Example</a> site</p>'
    md = html_to_markdown(html, ignore_links=False)
    assert "[Example]" in md
    assert "https://example.com" in md


def test_html_to_markdown_ignore_links():
    """Test ignoring links in HTML."""
    html = '<p>Visit <a href="https://example.com">Example</a> site</p>'
    md = html_to_markdown(html, ignore_links=True)
    assert "[Example]" not in md or "https://example.com" not in md
    assert "Example" in md


def test_html_to_markdown_with_images():
    """Test HTML with images conversion."""
    html = '<p><img src="image.jpg" alt="Test Image"/></p>'
    md = html_to_markdown(html, ignore_images=False)
    # html2text should include image reference
    assert "image.jpg" in md or "Test Image" in md


def test_html_to_markdown_ignore_images():
    """Test ignoring images in HTML."""
    html = '<p><img src="image.jpg" alt="Test Image"/> Some text</p>'
    md = html_to_markdown(html, ignore_images=True)
    assert "Some text" in md
    # Image should be removed
    assert "image.jpg" not in md


def test_html_to_markdown_line_wrapping():
    """Test line wrapping behavior."""
    html = "<p>" + "word " * 50 + "</p>"

    # No wrapping (default)
    md_nowrap = html_to_markdown(html, body_width=0)
    lines = md_nowrap.split("\n")
    # Should be mostly on one line (excluding empty lines)
    non_empty_lines = [line for line in lines if line.strip()]
    assert len(non_empty_lines) <= 3, "Should not wrap with body_width=0"

    # With wrapping
    md_wrap = html_to_markdown(html, body_width=40)
    lines_wrap = md_wrap.split("\n")
    non_empty_lines_wrap = [line for line in lines_wrap if line.strip()]
    assert len(non_empty_lines_wrap) > 5, "Should wrap with body_width=40"


def test_html_to_markdown_unicode():
    """Test Unicode handling."""
    html = "<p>Hello 世界 🌍</p>"
    md = html_to_markdown(html)
    assert "Hello" in md
    assert "世界" in md
    assert "🌍" in md


def test_html_to_markdown_empty_string():
    """Test empty HTML string."""
    html = ""
    md = html_to_markdown(html)
    assert md == ""


def test_html_to_markdown_whitespace_cleanup():
    """Test excessive whitespace cleanup."""
    html = """
    <p>Line 1</p>


    <p>Line 2</p>

    <p>Line 3</p>
    """
    md = html_to_markdown(html)

    # Should not have excessive empty lines
    lines = md.split("\n")
    empty_line_sequences = []
    count = 0
    for line in lines:
        if not line.strip():
            count += 1
        else:
            if count > 0:
                empty_line_sequences.append(count)
            count = 0

    # No sequence of more than 1 empty line
    assert all(seq <= 1 for seq in empty_line_sequences)


def test_html_to_markdown_complex_structure():
    """Test complex HTML structure."""
    html = """
    <html>
    <body>
        <h1>Title</h1>
        <p>Paragraph with <strong>bold</strong> and <em>italic</em>.</p>
        <ul>
            <li>Item 1</li>
            <li>Item 2</li>
        </ul>
        <pre><code>code block</code></pre>
    </body>
    </html>
    """
    md = html_to_markdown(html)

    assert "Title" in md
    assert "**bold**" in md or "bold" in md
    assert "Item 1" in md
    assert "Item 2" in md
    assert "code block" in md


def test_html_to_markdown_custom_options():
    """Test custom html2text options."""
    html = '<p>Test <a href="#">link</a></p>'

    # Pass custom option
    md = html_to_markdown(html, skip_internal_links=False)
    # Result should still work
    assert "Test" in md


def test_html_to_markdown_nested_formatting():
    """Test nested HTML formatting."""
    html = "<p><strong><em>Bold and italic</em></strong></p>"
    md = html_to_markdown(html)
    # Should contain formatting
    assert "Bold and italic" in md
