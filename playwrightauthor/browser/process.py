# this_file: playwrightauthor/browser/process.py

import psutil

def get_chrome_process(port: int | None = None) -> psutil.Process | None:
    """Find a running Chrome process."""
    for proc in psutil.process_iter(["name", "cmdline"]):
        try:
            if "chrome" in proc.info["name"].lower():
                if port is None:
                    return proc
                if any(
                    f"--remote-debugging-port={port}" in arg
                    for arg in proc.info["cmdline"]
                ):
                    return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return None
