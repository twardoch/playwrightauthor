#!/usr/bin/env -S uv run -s
# /// script
# dependencies = ["fire"]
# ///
# this_file: playwrightauthor/__main__.py

"""`python -m playwrightauthor` entry-point."""

from .cli import main

if __name__ == "__main__":
    main()
