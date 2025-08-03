# this_file: playwrightauthor/browser/finder.py

import os
import sys
from pathlib import Path
from ..utils.paths import install_dir

def find_chrome_executable() -> Path | None:
    """Find the Chrome for Testing executable in the install directory or common system locations."""
    install_path = install_dir()
    if sys.platform == "darwin":
        exec_paths = [
            install_path
            / "chrome-mac-arm64"
            / "Google Chrome for Testing.app"
            / "Contents"
            / "MacOS"
            / "Google Chrome for Testing",
            install_path
            / "chrome-mac-x64"
            / "Google Chrome for Testing.app"
            / "Contents"
            / "MacOS"
            / "Google Chrome for Testing",
            Path("/Applications/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"),
            Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
        ]
    elif sys.platform == "win32":
        exec_paths = [
            install_path / "chrome-win64" / "chrome.exe",
            Path(os.environ.get("ProgramFiles(x86)", "")) / "Google" / "Chrome" / "Application" / "chrome.exe",
            Path(os.environ.get("ProgramFiles", "")) / "Google" / "Chrome" / "Application" / "chrome.exe",
        ]
    elif sys.platform.startswith("linux"):
        exec_paths = [
            install_path / "chrome-linux64" / "chrome",
            Path("/usr/bin/google-chrome"),
        ]
    else:
        return None

    for path in exec_paths:
        if path.exists():
            return path
    return None
