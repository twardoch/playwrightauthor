# this_file: playwrightauthor/browser/launcher.py

import subprocess
from pathlib import Path
from ..exceptions import BrowserManagerError


def launch_chrome(browser_path: Path, data_dir: Path, port: int, logger):
    """Launch the Chrome executable as a detached process."""
    logger.info(f"Launching Chrome from: {browser_path}")
    command = [
        str(browser_path),
        f"--remote-debugging-port={port}",
        f"--user-data-dir={data_dir}",
    ]
    try:
        process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            process.wait(timeout=30)
        except subprocess.TimeoutExpired:
            logger.info("Chrome launched successfully as a detached process.")
    except (OSError, subprocess.SubprocessError) as e:
        raise BrowserManagerError(f"Failed to launch Chrome: {e}") from e
