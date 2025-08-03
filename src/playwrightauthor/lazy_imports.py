# this_file: src/playwrightauthor/lazy_imports.py

"""Lazy import utilities for PlaywrightAuthor.

This module provides lazy loading for heavyweight imports like Playwright,
reducing startup time and memory usage when these imports are not needed.
"""

import importlib
import sys
from typing import TYPE_CHECKING, Any

from loguru import logger

if TYPE_CHECKING:
    pass


class LazyModule:
    """A lazy module that imports on first attribute access."""

    def __init__(self, module_name: str):
        """Initialize the lazy module.

        Args:
            module_name: Name of the module to import lazily.
        """
        self._module_name = module_name
        self._module = None

    def _load(self) -> Any:
        """Load the module if not already loaded."""
        if self._module is None:
            logger.debug(f"Lazy loading module: {self._module_name}")
            self._module = importlib.import_module(self._module_name)
        return self._module

    def __getattr__(self, name: str) -> Any:
        """Get attribute from the loaded module."""
        module = self._load()
        return getattr(module, name)

    def __dir__(self) -> list[str]:
        """List attributes of the loaded module."""
        module = self._load()
        return dir(module)


class LazyPlaywright:
    """Lazy loader for Playwright with both sync and async APIs."""

    def __init__(self):
        """Initialize the lazy Playwright loader."""
        self._sync_api = None
        self._async_api = None
        self._sync_playwright = None
        self._async_playwright = None

    @property
    def sync_api(self):
        """Get the synchronous Playwright API."""
        if self._sync_api is None:
            logger.debug("Lazy loading playwright.sync_api")
            from playwright.sync_api import sync_playwright

            self._sync_api = sys.modules["playwright.sync_api"]
            self._sync_playwright = sync_playwright
        return self._sync_api

    @property
    def async_api(self):
        """Get the asynchronous Playwright API."""
        if self._async_api is None:
            logger.debug("Lazy loading playwright.async_api")
            from playwright.async_api import async_playwright

            self._async_api = sys.modules["playwright.async_api"]
            self._async_playwright = async_playwright
        return self._async_api

    def sync_playwright(self):
        """Get the sync_playwright context manager."""
        _ = self.sync_api  # Ensure module is loaded
        return self._sync_playwright()

    def async_playwright(self):
        """Get the async_playwright context manager."""
        _ = self.async_api  # Ensure module is loaded
        return self._async_playwright()


# Global lazy Playwright instance
_playwright = LazyPlaywright()


def get_sync_playwright():
    """Get the sync_playwright context manager lazily.

    Returns:
        The sync_playwright context manager.
    """
    return _playwright.sync_playwright()


def get_async_playwright():
    """Get the async_playwright context manager lazily.

    Returns:
        The async_playwright context manager.
    """
    return _playwright.async_playwright()


def get_sync_api():
    """Get the synchronous Playwright API module lazily.

    Returns:
        The playwright.sync_api module.
    """
    return _playwright.sync_api


def get_async_api():
    """Get the asynchronous Playwright API module lazily.

    Returns:
        The playwright.async_api module.
    """
    return _playwright.async_api


# Other heavy imports that can be lazy loaded
_psutil = None


def get_psutil():
    """Get psutil module lazily.

    Returns:
        The psutil module.
    """
    global _psutil
    if _psutil is None:
        logger.debug("Lazy loading psutil")
        import psutil

        _psutil = psutil
    return _psutil


_requests = None


def get_requests():
    """Get requests module lazily.

    Returns:
        The requests module.
    """
    global _requests
    if _requests is None:
        logger.debug("Lazy loading requests")
        import requests

        _requests = requests
    return _requests
