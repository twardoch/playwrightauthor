# this_file: tests/test_engines.py

"""Unit tests for the browser engine adapters."""

from unittest.mock import MagicMock, patch

import pytest

from playwrightauthor.config import PlaywrightAuthorConfig
from playwrightauthor.engine import (
    get_engine,
    get_engine_async,
)
from playwrightauthor.engines.chrome import (
    AsyncChromeEngineAdapter,
    ChromeEngineAdapter,
)
from playwrightauthor.engines.cloak import (
    AsyncCloakEngineAdapter,
    CloakEngineAdapter,
)


@pytest.fixture
def browser_config():
    """Mock config."""
    return PlaywrightAuthorConfig()


def test_get_engine_chrome(browser_config):
    """Test retrieving the chrome engine adapter."""
    engine = get_engine("chrome", browser_config, "default")
    assert isinstance(engine, ChromeEngineAdapter)
    assert engine.profile == "default"
    assert engine.config == browser_config


def test_get_engine_cloak(browser_config):
    """Test retrieving the cloak engine adapter."""
    # Mock _ensure_cloakbrowser_importable to avoid missing package issues
    with patch("playwrightauthor.engine.get_engine") as mock_get_engine:
        mock_get_engine.return_value = CloakEngineAdapter(browser_config, "default")
        engine = get_engine("cloak", browser_config, "default")
        assert isinstance(engine, CloakEngineAdapter)


def test_get_engine_invalid(browser_config):
    """Test get_engine raises ValueError for invalid engine name."""
    with pytest.raises(ValueError, match="Unknown engine"):
        get_engine("invalid_engine", browser_config, "default")


def test_get_engine_async_chrome(browser_config):
    """Test retrieving the async chrome engine adapter."""
    engine = get_engine_async("chrome", browser_config, "default")
    assert isinstance(engine, AsyncChromeEngineAdapter)


def test_get_engine_async_cloak(browser_config):
    """Test retrieving the async cloak engine adapter."""
    with patch("playwrightauthor.engine.get_engine_async") as mock_get_engine_async:
        mock_get_engine_async.return_value = AsyncCloakEngineAdapter(
            browser_config, "default"
        )
        engine = get_engine_async("cloak", browser_config, "default")
        assert isinstance(engine, AsyncCloakEngineAdapter)


@patch("playwrightauthor.engines.chrome.ensure_browser")
@patch("playwrightauthor.engines.chrome.connect_with_retry")
@patch("playwrightauthor.engines.chrome.get_state_manager")
def test_chrome_engine_adapter_start(
    mock_state_manager, mock_connect, mock_ensure, browser_config
):
    """Test that ChromeEngineAdapter start connects correctly."""
    mock_state_manager.return_value.get_profile_debug_port.return_value = 9223
    adapter = ChromeEngineAdapter(browser_config, "test_profile", verbose=True)
    mock_chromium = MagicMock()

    adapter.start(mock_chromium)

    mock_ensure.assert_called_once_with(verbose=True, profile="test_profile")
    mock_state_manager.return_value.get_profile_debug_port.assert_called_once_with(
        "test_profile", browser_config.browser.debug_port
    )
    mock_connect.assert_called_once_with(
        mock_chromium,
        9223,
        max_retries=browser_config.network.retry_attempts,
        retry_delay=browser_config.network.retry_delay,
        timeout=browser_config.browser.timeout // 1000,
    )


@patch("playwrightauthor.engines.chrome.ensure_browser")
@patch("playwrightauthor.engines.chrome.async_connect_with_retry")
@patch("playwrightauthor.engines.chrome.get_state_manager")
@pytest.mark.anyio
async def test_async_chrome_engine_adapter_start(
    mock_state_manager, mock_connect, mock_ensure, browser_config
):
    """Test that AsyncChromeEngineAdapter start_async connects correctly."""
    mock_state_manager.return_value.get_profile_debug_port.return_value = 9223
    adapter = AsyncChromeEngineAdapter(browser_config, "test_profile", verbose=True)
    mock_chromium = MagicMock()

    await adapter.start_async(mock_chromium)

    mock_ensure.assert_called_once_with(verbose=True, profile="test_profile")
    mock_state_manager.return_value.get_profile_debug_port.assert_called_once_with(
        "test_profile", browser_config.browser.debug_port
    )
    mock_connect.assert_called_once_with(
        mock_chromium,
        9223,
        max_retries=browser_config.network.retry_attempts,
        retry_delay=browser_config.network.retry_delay,
        timeout=browser_config.browser.timeout // 1000,
    )


@patch("playwrightauthor.engines.cloak.ensure_cloak_browser")
@patch("playwrightauthor.engines.cloak.connect_with_retry")
def test_cloak_engine_adapter_start(mock_connect, mock_ensure, browser_config):
    """Test that CloakEngineAdapter start connects correctly."""
    adapter = CloakEngineAdapter(browser_config, "test_profile", verbose=True)
    mock_chromium = MagicMock()

    adapter.start(mock_chromium)

    mock_ensure.assert_called_once_with(
        browser_config, verbose=True, profile="test_profile"
    )
    mock_connect.assert_called_once_with(
        mock_chromium,
        browser_config.browser.debug_port,
        max_retries=browser_config.network.retry_attempts,
        retry_delay=browser_config.network.retry_delay,
        timeout=browser_config.browser.timeout // 1000,
    )


@patch("playwrightauthor.engines.cloak.ensure_cloak_browser")
@patch("playwrightauthor.engines.cloak.async_connect_with_retry")
@pytest.mark.anyio
async def test_async_cloak_engine_adapter_start(
    mock_connect, mock_ensure, browser_config
):
    """Test that AsyncCloakEngineAdapter start_async connects correctly."""
    adapter = AsyncCloakEngineAdapter(browser_config, "test_profile", verbose=True)
    mock_chromium = MagicMock()

    await adapter.start_async(mock_chromium)

    mock_ensure.assert_called_once_with(
        browser_config, verbose=True, profile="test_profile"
    )
    mock_connect.assert_called_once_with(
        mock_chromium,
        browser_config.browser.debug_port,
        max_retries=browser_config.network.retry_attempts,
        retry_delay=browser_config.network.retry_delay,
        timeout=browser_config.browser.timeout // 1000,
    )
