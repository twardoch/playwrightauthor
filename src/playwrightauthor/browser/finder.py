# this_file: src/playwrightauthor/browser/finder.py

import os
import platform
import subprocess
import sys
from collections.abc import Generator
from pathlib import Path

from ..utils.paths import install_dir


def _get_windows_chrome_paths() -> Generator[Path, None, None]:
    """Generate possible Chrome for Testing paths on Windows."""
    install_path = install_dir()

    # Chrome for Testing in our install directory (primary location)
    yield install_path / "chrome-win64" / "chrome.exe"
    yield install_path / "chrome-win32" / "chrome.exe"

    # Environment variables
    program_files = os.environ.get("ProgramFiles", "C:\\Program Files")
    program_files_x86 = os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")

    # Chrome for Testing system installations
    chrome_paths = [
        # Chrome for Testing in Program Files
        Path(program_files) / "Google" / "Chrome for Testing" / "chrome.exe",
        Path(program_files_x86) / "Google" / "Chrome for Testing" / "chrome.exe",
    ]

    yield from chrome_paths


def _get_linux_chrome_paths() -> Generator[Path, None, None]:
    """Generate possible Chrome for Testing paths on Linux."""
    install_path = install_dir()

    # Chrome for Testing in our install directory (primary location)
    yield install_path / "chrome-linux64" / "chrome"

    # Chrome for Testing system installations
    search_paths = [
        Path("/opt/google/chrome-for-testing"),
        Path("/usr/local/chrome-for-testing"),
    ]

    for search_path in search_paths:
        yield search_path / "chrome"


def _get_macos_chrome_paths() -> Generator[Path, None, None]:
    """Generate possible Chrome for Testing paths on macOS."""
    install_path = install_dir()

    # Determine architecture
    machine = platform.machine()
    if machine == "arm64":
        architectures = ["arm64", "x64"]  # ARM Macs can run x64 via Rosetta
    else:
        architectures = ["x64"]

    # Chrome for Testing in our install directory (primary location)
    for arch in architectures:
        yield (
            install_path
            / f"chrome-mac-{arch}"
            / "Google Chrome for Testing.app"
            / "Contents"
            / "MacOS"
            / "Google Chrome for Testing"
        )

    # System-wide Chrome for Testing installations
    app_paths = [
        "/Applications/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing",
    ]

    for app_path in app_paths:
        yield Path(app_path)

    # User-specific Chrome for Testing installations
    home = Path.home()
    user_app_paths = [
        home
        / "Applications/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing",
    ]

    for app_path in user_app_paths:
        yield app_path


def find_chrome_executable(logger=None, use_cache: bool = True) -> Path | None:
    """
    Find the Chrome for Testing executable on the system.

    Args:
        logger: Optional logger for debugging output
        use_cache: Whether to use cached Chrome path if available

    Returns:
        Path to Chrome for Testing executable, or None if not found
    """
    # Try to use cached path first
    if use_cache:
        try:
            from ..state_manager import get_state_manager

            state_manager = get_state_manager()
            cached_path = state_manager.get_chrome_path()
            if cached_path and cached_path.exists():
                if logger:
                    logger.debug(f"Using cached Chrome path: {cached_path}")
                return cached_path
        except Exception as e:
            if logger:
                logger.debug(f"Failed to load cached Chrome path: {e}")
    # Select the appropriate platform-specific function
    if sys.platform == "darwin":
        path_generator = _get_macos_chrome_paths()
    elif sys.platform == "win32":
        path_generator = _get_windows_chrome_paths()
    elif sys.platform.startswith("linux"):
        path_generator = _get_linux_chrome_paths()
    else:
        if logger:
            logger.error(f"Unsupported platform: {sys.platform}")
        return None

    # Try each potential path
    checked_paths = []
    for path in path_generator:
        checked_paths.append(path)
        try:
            if path.exists() and path.is_file():
                # Verify it's executable (on Unix-like systems)
                if sys.platform != "win32":
                    if os.access(path, os.X_OK):
                        if logger:
                            logger.debug(f"Found Chrome executable: {path}")
                        # Cache the path for future use
                        _cache_chrome_path(path, logger)
                        return path
                    elif logger:
                        logger.debug(f"Found Chrome but not executable: {path}")
                else:
                    # On Windows, existence is enough
                    if logger:
                        logger.debug(f"Found Chrome executable: {path}")
                    # Cache the path for future use
                    _cache_chrome_path(path, logger)
                    return path
        except (OSError, PermissionError) as e:
            if logger:
                logger.debug(f"Error checking path {path}: {e}")

    # Log all paths that were checked if nothing was found
    if logger:
        logger.warning(
            f"Chrome for Testing executable not found. Checked {len(checked_paths)} locations:"
        )
        for path in checked_paths[:10]:  # Show first 10 paths
            logger.debug(f"  - {path}")
        if len(checked_paths) > 10:
            logger.debug(f"  ... and {len(checked_paths) - 10} more locations")

    return None


def get_chrome_version(chrome_path: Path, logger=None) -> str | None:
    """
    Get the version of Chrome at the given path.

    Args:
        chrome_path: Path to Chrome executable
        logger: Optional logger

    Returns:
        Version string or None if unable to determine
    """
    try:
        # Different commands for different platforms
        if sys.platform == "win32":
            cmd = [str(chrome_path), "--version"]
        else:
            cmd = [str(chrome_path), "--version"]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

        if result.returncode == 0:
            version = result.stdout.strip()
            if logger:
                logger.debug(f"Chrome version: {version}")
            return version
        else:
            if logger:
                logger.warning(f"Failed to get Chrome version: {result.stderr}")
            return None

    except (subprocess.TimeoutExpired, OSError) as e:
        if logger:
            logger.error(f"Error getting Chrome version: {e}")
        return None


def _cache_chrome_path(path: Path, logger=None) -> None:
    """Cache the Chrome executable path for future use.

    Args:
        path: Path to Chrome executable
        logger: Optional logger
    """
    try:
        from ..state_manager import get_state_manager

        state_manager = get_state_manager()
        state_manager.set_chrome_path(path)
        if logger:
            logger.debug(f"Cached Chrome path: {path}")
    except Exception as e:
        if logger:
            logger.debug(f"Failed to cache Chrome path: {e}")
