# this_file: playwrightauthor/tests/test_helpers_interaction.py
"""Tests for helpers.interaction module."""

from unittest.mock import MagicMock

from playwrightauthor.helpers.interaction import scroll_page_incremental


def test_scroll_page_incremental_window_scroll_no_container():
    """Test window scroll when no container selector provided."""
    page = MagicMock()

    scroll_page_incremental(page, scroll_distance=800)

    # Should call page.evaluate with window scroll script
    page.evaluate.assert_called_once()
    call_args = page.evaluate.call_args[0][0]
    assert "window.scrollBy(0, 800)" in call_args
    assert 'div[fontviewtype="grid"]' in call_args  # default container


def test_scroll_page_incremental_container_scroll():
    """Test scrolling specific container when provided."""
    page = MagicMock()

    scroll_page_incremental(
        page, scroll_distance=1200, container_selector="div.content-container"
    )

    # Should call page.evaluate with container selector
    page.evaluate.assert_called_once()
    call_args = page.evaluate.call_args[0][0]
    assert "div.content-container" in call_args
    assert "container.scrollBy(0, 1200)" in call_args


def test_scroll_page_incremental_default_distance():
    """Test that default scroll distance is 600px."""
    page = MagicMock()

    scroll_page_incremental(page)

    # Should use default 600px
    call_args = page.evaluate.call_args[0][0]
    assert "600" in call_args


def test_scroll_page_incremental_window_fallback():
    """Test fallback to window scroll logic (in JavaScript)."""
    page = MagicMock()

    scroll_page_incremental(
        page, scroll_distance=500, container_selector="#mycontainer"
    )

    # Script should include both container and window scroll logic
    call_args = page.evaluate.call_args[0][0]
    assert "#mycontainer" in call_args
    assert "window.scrollBy(0, 500)" in call_args  # fallback


def test_scroll_page_incremental_handles_exceptions():
    """Test that exceptions in page.evaluate are silently caught."""
    page = MagicMock()
    page.evaluate.side_effect = RuntimeError("JavaScript error")

    # Should not raise exception
    scroll_page_incremental(page, scroll_distance=600)

    # evaluate was called despite error
    page.evaluate.assert_called_once()


def test_scroll_page_incremental_various_distances():
    """Test different scroll distances."""
    page = MagicMock()

    # Test small scroll
    scroll_page_incremental(page, scroll_distance=100)
    assert "100" in page.evaluate.call_args[0][0]

    # Test large scroll
    page.reset_mock()
    scroll_page_incremental(page, scroll_distance=2000)
    assert "2000" in page.evaluate.call_args[0][0]

    # Test exact default
    page.reset_mock()
    scroll_page_incremental(page, scroll_distance=600)
    assert "600" in page.evaluate.call_args[0][0]


def test_scroll_page_incremental_various_selectors():
    """Test different CSS selectors."""
    page = MagicMock()

    # Test ID selector
    scroll_page_incremental(page, container_selector="#scroll-container")
    assert "#scroll-container" in page.evaluate.call_args[0][0]

    # Test class selector
    page.reset_mock()
    scroll_page_incremental(page, container_selector=".scroll-area")
    assert ".scroll-area" in page.evaluate.call_args[0][0]

    # Test attribute selector
    page.reset_mock()
    scroll_page_incremental(page, container_selector='div[data-scroll="true"]')
    assert 'div[data-scroll="true"]' in page.evaluate.call_args[0][0]


def test_scroll_page_incremental_script_structure():
    """Test that the generated JavaScript has correct structure."""
    page = MagicMock()

    scroll_page_incremental(page, scroll_distance=800, container_selector="#test")

    script = page.evaluate.call_args[0][0]

    # Check for IIFE pattern
    assert "(() => {" in script
    assert "})()" in script

    # Check for container query
    assert "document.querySelector('#test')" in script

    # Check for scrollHeight check
    assert "container.scrollHeight > container.clientHeight" in script

    # Check for scrollBy calls
    assert "container.scrollBy(0, 800)" in script
    assert "window.scrollBy(0, 800)" in script

    # Check for return after container scroll
    assert "return;" in script
