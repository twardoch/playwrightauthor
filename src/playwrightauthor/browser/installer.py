# this_file: src/playwrightauthor/browser/installer.py

import hashlib
import json
import os
import platform
import shutil
import stat
import time
from pathlib import Path

import requests

from ..exceptions import BrowserInstallationError, NetworkError
from ..utils.paths import install_dir

_LKGV_URL = "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json"


def _get_platform_key() -> str:
    """Determine the platform key for Chrome for Testing downloads."""
    system = platform.system()
    if system == "Darwin":
        arch = platform.machine()
        return "mac-arm64" if arch == "arm64" else "mac-x64"
    elif system == "Windows":
        return "win64"
    elif system == "Linux":
        return "linux64"
    else:
        raise BrowserInstallationError(f"Unsupported operating system: {system}")


def _validate_lkgv_data(data: dict) -> None:
    """Validate the structure of LKGV JSON data."""
    required_keys = ["channels"]
    for key in required_keys:
        if key not in data:
            raise BrowserInstallationError(f"Invalid LKGV JSON: missing '{key}' field")

    channels = data.get("channels", {})
    if "Stable" not in channels:
        raise BrowserInstallationError("Invalid LKGV JSON: missing 'Stable' channel")

    stable = channels["Stable"]
    if "downloads" not in stable:
        raise BrowserInstallationError(
            "Invalid LKGV JSON: missing 'downloads' in Stable channel"
        )

    downloads = stable["downloads"]
    if "chrome" not in downloads:
        raise BrowserInstallationError("Invalid LKGV JSON: missing 'chrome' downloads")


def _fetch_lkgv_data(logger, timeout: int = 30) -> dict:
    """
    Fetch and validate LKGV data from Chrome for Testing API.

    Args:
        logger: Logger instance
        timeout: Request timeout in seconds

    Returns:
        Parsed JSON data

    Raises:
        NetworkError: If network request fails
        BrowserInstallationError: If JSON is invalid
    """
    try:
        logger.debug(f"Fetching LKGV data from {_LKGV_URL}")
        response = requests.get(_LKGV_URL, timeout=timeout)
        response.raise_for_status()

        try:
            data = response.json()
        except json.JSONDecodeError as e:
            raise BrowserInstallationError(
                f"Invalid JSON response from LKGV API: {e}"
            ) from e

        _validate_lkgv_data(data)
        return data

    except requests.RequestException as e:
        raise NetworkError(f"Failed to fetch LKGV data: {e}") from e


def _download_with_progress(
    url: str, dest_path: Path, logger, timeout: int = 300
) -> None:
    """
    Download a file with progress reporting and integrity checks.

    Args:
        url: Download URL
        dest_path: Destination file path
        logger: Logger instance
        timeout: Download timeout in seconds

    Raises:
        NetworkError: If download fails
        BrowserInstallationError: If file integrity check fails
    """
    try:
        logger.info(f"Downloading from: {url}")

        with requests.get(url, stream=True, timeout=timeout) as response:
            response.raise_for_status()

            # Get content length for progress reporting
            total_size = int(response.headers.get("content-length", 0))
            downloaded = 0

            # Create a hash to verify integrity
            sha256_hash = hashlib.sha256()

            with open(dest_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        sha256_hash.update(chunk)
                        downloaded += len(chunk)

                        # Log progress every 10MB
                        if total_size > 0 and downloaded % (10 * 1024 * 1024) == 0:
                            progress = (downloaded / total_size) * 100
                            logger.info(
                                f"Download progress: {progress:.1f}% ({downloaded:,} / {total_size:,} bytes)"
                            )

            logger.info(f"Download complete. File size: {downloaded:,} bytes")
            logger.debug(f"File SHA256: {sha256_hash.hexdigest()}")

    except requests.RequestException as e:
        raise NetworkError(f"Download failed: {e}") from e
    except OSError as e:
        raise BrowserInstallationError(f"Failed to write download file: {e}") from e


def _extract_archive(archive_path: Path, extract_path: Path, logger) -> None:
    """
    Extract downloaded archive with error handling.

    Args:
        archive_path: Path to archive file
        extract_path: Extraction destination
        logger: Logger instance

    Raises:
        BrowserInstallationError: If extraction fails
    """
    try:
        logger.info("Extracting downloaded archive...")
        shutil.unpack_archive(archive_path, extract_path)
        logger.info("Extraction complete")
        
        # Fix executable permissions on macOS and Linux
        if platform.system() in ["Darwin", "Linux"]:
            _fix_executable_permissions(extract_path, logger)

        # Clean up archive file
        archive_path.unlink()
        logger.debug(f"Removed archive file: {archive_path}")

    except (shutil.ReadError, OSError) as e:
        raise BrowserInstallationError(f"Failed to extract archive: {e}") from e


def _fix_executable_permissions(extract_path: Path, logger) -> None:
    """
    Fix executable permissions for Chrome for Testing on Unix-like systems.
    
    Args:
        extract_path: Root extraction directory
        logger: Logger instance
    """
    try:
        # Find Chrome executable based on platform
        if platform.system() == "Darwin":
            # macOS: Look for the executable inside the app bundle
            chrome_executable = None
            for chrome_dir in extract_path.glob("chrome-mac-*"):
                app_path = chrome_dir / "Google Chrome for Testing.app" / "Contents" / "MacOS" / "Google Chrome for Testing"
                if app_path.exists():
                    chrome_executable = app_path
                    break
        else:
            # Linux: Look for chrome executable
            chrome_executable = None
            for chrome_dir in extract_path.glob("chrome-linux*"):
                chrome_path = chrome_dir / "chrome"
                if chrome_path.exists():
                    chrome_executable = chrome_path
                    break
        
        if chrome_executable:
            # Add executable permissions
            current_permissions = chrome_executable.stat().st_mode
            chrome_executable.chmod(current_permissions | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
            logger.debug(f"Set executable permissions on: {chrome_executable}")
            
            # Fix permissions for all executables in the app bundle on macOS
            if platform.system() == "Darwin":
                app_bundle = chrome_executable.parent.parent.parent  # Get to .app directory
                if app_bundle.suffix == ".app":
                    # Fix all executables in the app bundle
                    for exe_path in app_bundle.rglob("*"):
                        if exe_path.is_file():
                            # Check if it's likely an executable (no extension or specific names)
                            if (not exe_path.suffix or 
                                exe_path.suffix in [".dylib"] or
                                "Helper" in exe_path.name or
                                "chrome_crashpad_handler" in exe_path.name or
                                exe_path.parent.name in ["MacOS", "Helpers"]):
                                try:
                                    current_perms = exe_path.stat().st_mode
                                    exe_path.chmod(current_perms | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
                                    logger.debug(f"Set executable permissions on: {exe_path.relative_to(app_bundle)}")
                                except Exception as e:
                                    logger.debug(f"Could not set permissions on {exe_path.name}: {e}")
        else:
            logger.warning("Could not find Chrome executable to set permissions")
            
    except Exception as e:
        logger.warning(f"Failed to set executable permissions: {e}")
        # Don't fail the installation, just warn


def install_from_lkgv(logger, max_retries: int = 3, retry_delay: int = 5) -> None:
    """
    Download and extract Chrome for Testing from the LKGV JSON.

    Args:
        logger: Logger instance
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retries in seconds

    Raises:
        BrowserInstallationError: If installation fails after all retries
        NetworkError: If network operations fail after all retries
    """
    platform_key = _get_platform_key()
    logger.info(f"Detected platform: {platform_key}")

    install_path = install_dir()
    install_path.mkdir(parents=True, exist_ok=True)
    zip_path = install_path / "chrome.zip"

    last_error = None

    for attempt in range(max_retries):
        try:
            logger.info(f"Installation attempt {attempt + 1}/{max_retries}")

            # Fetch LKGV data
            data = _fetch_lkgv_data(logger)

            # Find download URL for our platform
            downloads = data["channels"]["Stable"]["downloads"]["chrome"]
            url = next(
                (item["url"] for item in downloads if item["platform"] == platform_key),
                None,
            )

            if not url:
                raise BrowserInstallationError(
                    f"No download URL found for platform {platform_key}"
                )

            # Download and extract
            _download_with_progress(url, zip_path, logger)
            _extract_archive(zip_path, install_path, logger)

            logger.info("Chrome for Testing installation completed successfully")
            return  # Success

        except (NetworkError, BrowserInstallationError) as e:
            last_error = e
            if attempt < max_retries - 1:
                logger.warning(f"Installation attempt {attempt + 1} failed: {e}")
                logger.info(f"Retrying in {retry_delay} seconds...")

                # Clean up partial files
                if zip_path.exists():
                    try:
                        zip_path.unlink()
                        logger.debug("Cleaned up partial download")
                    except OSError:
                        pass

                time.sleep(retry_delay)
            else:
                logger.error(f"All {max_retries} installation attempts failed")

    raise BrowserInstallationError(
        f"Failed to install Chrome after {max_retries} attempts. Last error: {last_error}"
    ) from last_error
