#!/usr/bin/env -S uv run -s
# /// script
# dependencies = ["prompt_toolkit", "rich"]
# ///
# this_file: src/playwrightauthor/repl/__init__.py

"""Interactive REPL module for PlaywrightAuthor."""

from .engine import ReplEngine

__all__ = ["ReplEngine"]
