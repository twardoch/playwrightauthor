#!/usr/bin/env -S uv run -s
# /// script
# dependencies = ["loguru"]
# ///
# this_file: src/playwrightauthor/utils/logger.py

"""Project-wide Loguru configuration."""

from loguru import logger


def configure(verbose: bool = False):
    logger.remove()
    level = "DEBUG" if verbose else "INFO"
    logger.add(lambda m: print(m, end=""), level=level)
    return logger
