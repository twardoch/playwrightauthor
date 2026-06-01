# this_file: src/playwrightauthor/engine.py

"""Engine adapter protocols and registry for browser engines.

This module defines the contracts that each browser engine must implement,
and provides a registry to retrieve the appropriate adapter for a given engine.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from playwright.async_api import Browser as AsyncBrowser
    from playwright.sync_api import Browser as SyncBrowser

    from playwrightauthor.config import BrowserConfig


@runtime_checkable
class EngineAdapter(Protocol):
    """Contract for browser engine adapters (synchronous).

    Each engine must implement start() to return a Playwright Browser instance.
    """

    def start(self, playwright_chromium) -> SyncBrowser:
        """Start the browser engine and return a Playwright Browser instance.

        Args:
            playwright_chromium: Playwright chromium API instance

        Returns:
            Playwright Browser instance
        """
        ...

    def ensure_browser(self) -> None:
        """Ensure the browser binary is available."""
        ...  # noqa: DAR401


@runtime_checkable
class AsyncEngineAdapter(Protocol):
    """Contract for browser engine adapters (asynchronous).

    Each engine must implement start_async() to return an async Playwright Browser instance.
    """

    async def start_async(self, playwright_chromium) -> AsyncBrowser:
        """Start the browser engine asynchronously and return a Playwright Browser instance.

        Args:
            playwright_chromium: Playwright async chromium API instance

        Returns:
            Async Playwright Browser instance
        """
        ...

    async def ensure_browser_async(self) -> None:
        """Ensure the browser binary is available asynchronously."""
        ...  # noqa: DAR401


def get_engine(
    engine_name: str, config: BrowserConfig, profile: str, verbose: bool = False
) -> EngineAdapter:
    """Get the engine adapter for the given engine name.

    Args:
        engine_name: Engine name ("chrome" or "cloak")
        config: BrowserConfig instance
        profile: Profile name
        verbose: Enable verbose logging

    Returns:
        EngineAdapter instance for the specified engine

    Raises:
        ValueError: If engine_name is invalid (no engine adapter found)
    """
    if engine_name == "chrome":
        from playwrightauthor.engines.chrome import ChromeEngineAdapter

        return ChromeEngineAdapter(config, profile, verbose)
    elif engine_name == "cloak":
        # Add to sys.path if cloakbrowser is inside private/CloakBrowser
        project_root = Path(__file__).resolve().parents[2]
        cloak_path = project_root / "private" / "CloakBrowser"
        if cloak_path.exists() and str(cloak_path) not in sys.path:
            sys.path.insert(0, str(cloak_path))

        try:
            from playwrightauthor.engines.cloak import CloakEngineAdapter

            return CloakEngineAdapter(config, profile, verbose)
        except ImportError as e:
            raise ImportError(
                "CloakBrowser engine requested but private/CloakBrowser package is not available. "
                "To use CloakBrowser, ensure private/CloakBrowser is installed and on the import path."
            ) from e
    else:
        # This should never happen due to validation in BrowserConfig,
        # but we keep the check for direct callers.
        raise ValueError(f"Unknown engine: {engine_name}. Valid engines: chrome, cloak")


def get_engine_async(
    engine_name: str, config: BrowserConfig, profile: str, verbose: bool = False
) -> AsyncEngineAdapter:
    """Get the async engine adapter for the given engine name.

    Args:
        engine_name: Engine name ("chrome" or "cloak")
        config: BrowserConfig instance
        profile: Profile name
        verbose: Enable verbose logging

    Returns:
        AsyncEngineAdapter instance for the specified engine

    Raises:
        ValueError: If engine_name is invalid (no engine adapter found)
        ImportError: If CloakBrowser requested but not available
    """
    if engine_name == "chrome":
        from playwrightauthor.engines.chrome import AsyncChromeEngineAdapter

        return AsyncChromeEngineAdapter(config, profile, verbose)
    elif engine_name == "cloak":
        # Add to sys.path if cloakbrowser is inside private/CloakBrowser
        project_root = Path(__file__).resolve().parents[2]
        cloak_path = project_root / "private" / "CloakBrowser"
        if cloak_path.exists() and str(cloak_path) not in sys.path:
            sys.path.insert(0, str(cloak_path))

        try:
            from playwrightauthor.engines.cloak import AsyncCloakEngineAdapter

            return AsyncCloakEngineAdapter(config, profile, verbose)
        except ImportError as e:
            raise ImportError(
                "CloakBrowser engine requested but private/CloakBrowser package is not available. "
                "To use CloakBrowser, ensure private/CloakBrowser is installed and on the import path."
            ) from e
    else:
        raise ValueError(f"Unknown engine: {engine_name}. Valid engines: chrome, cloak")
