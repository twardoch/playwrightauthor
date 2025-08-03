# this_file: playwrightauthor/exceptions.py

"""Custom exceptions for PlaywrightAuthor."""

class PlaywrightAuthorError(Exception):
    """Base exception for all PlaywrightAuthor errors."""
    pass

class BrowserManagerError(PlaywrightAuthorError):
    """Raised for errors related to browser management."""
    pass
