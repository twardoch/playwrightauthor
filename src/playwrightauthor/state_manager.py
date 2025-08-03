# this_file: src/playwrightauthor/state_manager.py

"""Browser state management for PlaywrightAuthor.

This module handles saving and loading browser state, including cookies,
localStorage, sessionStorage, and other browser data that needs to persist
across sessions.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, TypedDict

from loguru import logger

from .exceptions import BrowserManagerError
from .utils.paths import data_dir


class BrowserState(TypedDict, total=False):
    """Type definition for browser state data."""

    version: int
    last_updated: str
    chrome_path: str | None
    chrome_version: str | None
    profiles: dict[str, dict[str, Any]]
    default_profile: str
    config: dict[str, Any]


class StateManager:
    """Manages browser state persistence and migration."""

    CURRENT_VERSION = 1
    STATE_FILENAME = "browser_state.json"

    def __init__(self, state_dir: Path | None = None):
        """Initialize the state manager.

        Args:
            state_dir: Directory to store state files. Defaults to data_dir().
        """
        self.state_dir = state_dir or data_dir()
        self.state_file = self.state_dir / self.STATE_FILENAME
        self._ensure_state_dir()

    def _ensure_state_dir(self) -> None:
        """Ensure the state directory exists."""
        self.state_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"State directory: {self.state_dir}")

    def load_state(self) -> BrowserState:
        """Load browser state from disk.

        Returns:
            The loaded browser state, or a new default state if none exists.
        """
        if not self.state_file.exists():
            logger.debug("No existing state file found, returning default state")
            return self._default_state()

        try:
            with open(self.state_file, encoding="utf-8") as f:
                state = json.load(f)

            # Migrate if needed
            if state.get("version", 0) < self.CURRENT_VERSION:
                logger.info(
                    f"Migrating state from version {state.get('version', 0)} to {self.CURRENT_VERSION}"
                )
                state = self._migrate_state(state)

            logger.debug(f"Loaded state from {self.state_file}")
            return state

        except (OSError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load state file: {e}")
            logger.warning("Using default state due to load error")
            return self._default_state()

    def save_state(self, state: BrowserState) -> None:
        """Save browser state to disk.

        Args:
            state: The browser state to save.
        """
        # Update metadata
        state["version"] = self.CURRENT_VERSION
        state["last_updated"] = datetime.now().isoformat()

        try:
            # Write to temporary file first for atomicity
            temp_file = self.state_file.with_suffix(".tmp")
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2, sort_keys=True)

            # Atomic replace
            temp_file.replace(self.state_file)
            logger.debug(f"Saved state to {self.state_file}")

        except OSError as e:
            logger.error(f"Failed to save state file: {e}")
            raise BrowserManagerError(f"Failed to save browser state: {e}") from e

    def get_chrome_path(self) -> Path | None:
        """Get the cached Chrome executable path.

        Returns:
            Path to Chrome executable, or None if not cached.
        """
        state = self.load_state()
        chrome_path = state.get("chrome_path")

        if chrome_path and Path(chrome_path).exists():
            logger.debug(f"Using cached Chrome path: {chrome_path}")
            return Path(chrome_path)

        return None

    def set_chrome_path(self, path: Path) -> None:
        """Cache the Chrome executable path.

        Args:
            path: Path to Chrome executable.
        """
        state = self.load_state()
        state["chrome_path"] = str(path)
        self.save_state(state)
        logger.debug(f"Cached Chrome path: {path}")

    def get_profile(self, name: str = "default") -> dict[str, Any]:
        """Get a browser profile by name.

        Args:
            name: Profile name. Defaults to "default".

        Returns:
            Profile data dictionary.
        """
        state = self.load_state()
        profiles = state.get("profiles", {})

        if name not in profiles:
            logger.debug(f"Creating new profile: {name}")
            profiles[name] = self._default_profile()
            state["profiles"] = profiles
            self.save_state(state)

        return profiles[name]

    def set_profile(self, name: str, profile_data: dict[str, Any]) -> None:
        """Save a browser profile.

        Args:
            name: Profile name.
            profile_data: Profile data to save.
        """
        state = self.load_state()
        profiles = state.get("profiles", {})
        profiles[name] = profile_data
        state["profiles"] = profiles
        self.save_state(state)
        logger.debug(f"Saved profile: {name}")

    def list_profiles(self) -> list[str]:
        """List all available profile names.

        Returns:
            List of profile names.
        """
        state = self.load_state()
        return list(state.get("profiles", {}).keys())

    def delete_profile(self, name: str) -> None:
        """Delete a browser profile.

        Args:
            name: Profile name to delete.
        """
        if name == "default":
            raise BrowserManagerError("Cannot delete the default profile")

        state = self.load_state()
        profiles = state.get("profiles", {})

        if name in profiles:
            del profiles[name]
            state["profiles"] = profiles
            self.save_state(state)
            logger.info(f"Deleted profile: {name}")
        else:
            logger.warning(f"Profile not found: {name}")

    def clear_state(self) -> None:
        """Clear all saved state."""
        if self.state_file.exists():
            self.state_file.unlink()
            logger.info("Cleared all browser state")

    def _default_state(self) -> BrowserState:
        """Create a default browser state.

        Returns:
            Default browser state dictionary.
        """
        return {
            "version": self.CURRENT_VERSION,
            "last_updated": datetime.now().isoformat(),
            "chrome_path": None,
            "chrome_version": None,
            "profiles": {"default": self._default_profile()},
            "default_profile": "default",
            "config": {},
        }

    def _default_profile(self) -> dict[str, Any]:
        """Create a default profile.

        Returns:
            Default profile dictionary.
        """
        return {
            "created": datetime.now().isoformat(),
            "last_used": datetime.now().isoformat(),
            "user_data_dir": None,
            "preferences": {},
            "extensions": [],
            "auth_state": {},
        }

    def _migrate_state(self, state: dict[str, Any]) -> BrowserState:
        """Migrate state to the current version.

        Args:
            state: State to migrate.

        Returns:
            Migrated state.
        """
        version = state.get("version", 0)

        # Migration logic for future versions
        if version < 1:
            # Version 0 -> 1 migration
            logger.debug("Migrating from version 0 to 1")
            # Add any missing fields
            if "profiles" not in state:
                state["profiles"] = {"default": self._default_profile()}
            if "default_profile" not in state:
                state["default_profile"] = "default"
            if "config" not in state:
                state["config"] = {}

        # Set current version
        state["version"] = self.CURRENT_VERSION

        return state


# Singleton instance for easy access
_state_manager: StateManager | None = None


def get_state_manager(state_dir: Path | None = None) -> StateManager:
    """Get the global StateManager instance.

    Args:
        state_dir: Optional state directory. Only used on first call.

    Returns:
        The global StateManager instance.
    """
    global _state_manager

    if _state_manager is None:
        _state_manager = StateManager(state_dir)

    return _state_manager
