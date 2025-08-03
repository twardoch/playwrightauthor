#!/usr/bin/env -S uv run -s
# /// script
# dependencies = ["platformdirs"]
# ///
# this_file: src/playwrightauthor/utils/paths.py

"""Cross-platform install locations."""

from pathlib import Path

from platformdirs import user_cache_dir, user_config_dir, user_data_dir


def install_dir() -> Path:
    """Get the directory for browser installations."""
    return Path(user_cache_dir("playwrightauthor")) / "browser"


def data_dir() -> Path:
    """Get the directory for persistent data storage."""
    return Path(user_data_dir("playwrightauthor"))


def config_dir() -> Path:
    """Get the directory for configuration files."""
    return Path(user_config_dir("playwrightauthor"))
