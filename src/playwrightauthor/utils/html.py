# this_file: playwrightauthor/src/playwrightauthor/utils/html.py
"""HTML processing utilities."""

import html2text


def html_to_markdown(
    html_content: str,
    ignore_links: bool = False,
    ignore_images: bool = False,
    body_width: int = 0,
    **html2text_options: dict,
) -> str:
    """Convert HTML content to clean Markdown using html2text.

    Args:
        html_content: Raw HTML content to convert
        ignore_links: If True, links will be converted to plain text
        ignore_images: If True, images will be omitted
        body_width: Width for line wrapping (0 = no wrapping)
        **html2text_options: Additional options to pass to html2text.HTML2Text()

    Returns:
        Clean Markdown text

    Example:
        >>> html = '<p><strong>Hello</strong> world!</p>'
        >>> md = html_to_markdown(html)
        >>> print(md)
        **Hello** world!

    Note:
        This function is sync-only as html2text doesn't require I/O.
        Originally from playpi.html module, migrated to playwrightauthor
        for reuse across multiple projects.
    """
    # Configure html2text for clean output
    h = html2text.HTML2Text()
    h.ignore_links = ignore_links
    h.ignore_images = ignore_images
    h.body_width = body_width
    h.unicode_snob = True
    h.skip_internal_links = True

    # Apply any additional options
    for key, value in html2text_options.items():
        setattr(h, key, value)

    # Convert to markdown
    markdown = h.handle(html_content)

    # Clean up the markdown
    lines = markdown.split("\n")
    cleaned_lines = []

    for raw_line in lines:
        # Remove excessive whitespace
        line = raw_line.strip()
        # Skip empty lines in sequences
        if line or (cleaned_lines and cleaned_lines[-1]):
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines).strip()
