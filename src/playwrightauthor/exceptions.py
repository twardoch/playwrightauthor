# this_file: src/playwrightauthor/exceptions.py

"""Custom exceptions for PlaywrightAuthor."""


class PlaywrightAuthorError(Exception):
    """Base exception for all PlaywrightAuthor errors."""


class BrowserManagerError(PlaywrightAuthorError):
    """Raised for errors related to browser management."""


class BrowserInstallationError(BrowserManagerError):
    """Raised when browser installation fails."""


class BrowserLaunchError(BrowserManagerError):
    """Raised when browser launch fails."""


class ProcessKillError(BrowserManagerError):
    """Raised when process termination fails."""


class NetworkError(PlaywrightAuthorError):
    """Raised for network-related errors."""


class TimeoutError(PlaywrightAuthorError):
    """Raised when operations exceed timeout."""
