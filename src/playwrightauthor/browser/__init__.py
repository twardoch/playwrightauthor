# this_file: src/playwrightauthor/browser/__init__.py

"""Browser management modules for PlaywrightAuthor.

This package contains modules for finding, installing, launching, and managing
Chrome for Testing instances.
"""

from .finder import find_chrome_executable, get_chrome_version
from .installer import install_from_lkgv
from .launcher import launch_chrome, launch_chrome_with_retry
from .process import get_chrome_process, kill_chrome_process, wait_for_process_start

__all__ = [
    # Chrome discovery and version detection
    "find_chrome_executable",
    "get_chrome_version",
    # Chrome installation
    "install_from_lkgv",
    # Chrome launching
    "launch_chrome",
    "launch_chrome_with_retry",
    # Process management
    "get_chrome_process",
    "kill_chrome_process",
    "wait_for_process_start",
]
