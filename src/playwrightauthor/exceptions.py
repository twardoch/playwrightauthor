# this_file: src/playwrightauthor/exceptions.py

"""Custom exceptions for PlaywrightAuthor."""


class PlaywrightAuthorError(Exception):
    """Base exception for all PlaywrightAuthor errors."""

    pass


class BrowserManagerError(PlaywrightAuthorError):
    """Raised for errors related to browser management."""

    pass


class BrowserInstallationError(BrowserManagerError):
    """Raised when browser installation fails."""

    pass


class BrowserLaunchError(BrowserManagerError):
    """Raised when browser launch fails."""

    pass


class ProcessKillError(BrowserManagerError):
    """Raised when process termination fails."""

    pass


class NetworkError(PlaywrightAuthorError):
    """Raised for network-related errors."""

    pass


class TimeoutError(PlaywrightAuthorError):
    """Raised when operations exceed timeout."""

    pass
