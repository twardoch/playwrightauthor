# this_file: playwrightauthor/browser/installer.py

import os
import platform
import shutil
import time
import requests
from ..utils.paths import install_dir
from ..exceptions import BrowserManagerError

_LKGV_URL = "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json"

def install_from_lkgv(logger, retries=3, delay=5):
    """Download and extract Chrome for Testing from the LKGV JSON."""
    for attempt in range(retries):
        try:
            logger.info(f"Fetching latest versions from {_LKGV_URL} (attempt {attempt + 1}/{retries})...")
            response = requests.get(_LKGV_URL, timeout=30)
            response.raise_for_status()
            data = response.json()

            if platform.system() == "Darwin":
                arch = platform.machine()
                platform_key = "mac-arm64" if arch == "arm64" else "mac-x64"
            elif platform.system() == "Windows":
                platform_key = "win64"
            elif platform.system() == "Linux":
                platform_key = "linux64"
            else:
                raise BrowserManagerError("Unsupported operating system")

            logger.info(f"Detected platform: {platform_key}")
            downloads = data.get("channels", {}).get("Stable", {}).get("downloads", {}).get("chrome")
            if not downloads:
                raise BrowserManagerError("Could not find 'chrome' downloads in LKGV JSON.")

            url = next((item["url"] for item in downloads if item["platform"] == platform_key), None)
            if not url:
                raise BrowserManagerError(f"Could not find a download URL for platform {platform_key}")

            logger.info(f"Downloading from: {url}")
            install_path = install_dir()
            install_path.mkdir(parents=True, exist_ok=True)
            zip_path = install_path / "chrome.zip"

            with requests.get(url, stream=True, timeout=300) as r:
                r.raise_for_status()
                with open(zip_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)

            logger.info("Download complete. Extracting...")
            shutil.unpack_archive(zip_path, install_path)
            logger.info("Extraction complete.")
            os.remove(zip_path)
            return

        except requests.RequestException as e:
            logger.warning(f"Download failed: {e}. Retrying in {delay} seconds...")
            time.sleep(delay)
        except (OSError, ValueError, shutil.ReadError, BrowserManagerError) as e:
            raise BrowserManagerError(f"Failed to install Chrome: {e}") from e

    raise BrowserManagerError(f"Failed to download Chrome after {retries} attempts.")
