#!/usr/bin/env -S uv run -s
# /// script
# dependencies = []
# ///
# this_file: playwrightauthor/__init__.py

"""Public re-exports for library consumers."""

from .author import Browser, AsyncBrowser

__all__ = ["Browser", "AsyncBrowser"]
