# this_file: src/playwrightauthor/session_errors.py
"""Stable error codes shared by session consumers and the CLI."""

from .exceptions import BrowserManagerError


class SessionError(BrowserManagerError):
    """Session failures expose a machine-readable code without private browser data."""

    code = "BROWSER_SESSION_FAILED"


class ProfileBusy(SessionError):
    """The requested identity cannot be safely leased or attached."""

    code = "PROFILE_BUSY"


class EngineUnavailable(SessionError):
    """An engine's executable or optional dependency is unavailable."""

    code = "ENGINE_UNAVAILABLE"


class BackendUnsupported(SessionError):
    """A backend or capability is not implemented by the session API."""

    code = "BACKEND_UNSUPPORTED"


class AuthenticationRequired(SessionError):
    """A service probe rejected the current authorization without opening UI."""

    code = "AUTH_REQUIRED"
