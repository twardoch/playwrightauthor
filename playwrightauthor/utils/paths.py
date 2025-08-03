#!/usr/bin/env -S uv run -s
# /// script
# dependencies = ["platformdirs"]
# ///
# this_file: playwrightauthor/utils/paths.py

"""Cross-platform install locations."""

from platformdirs import user_cache_dir
from pathlib import Path


def install_dir() -> Path:
    return Path(user_cache_dir("playwrightauthor")) / "browser"
