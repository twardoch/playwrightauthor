#!/usr/bin/env -S uv run -s
# /// script
# dependencies = ["playwright", "psutil", "loguru", "fire"]
# ///
# this_file: scripts/verify_headless_launch.py
"""Exercise the real legacy launcher using a disposable profile on macOS.

Run from the checkout with `uv run python scripts/verify_headless_launch.py BINARY`.
No login data is used. Samples prove only observed launcher noninterference;
provider authentication, persistent session ownership and Poe parity are separate.
"""

import asyncio
import json
import socket
import subprocess
import threading
from datetime import UTC, datetime
from pathlib import Path
from tempfile import TemporaryDirectory

import fire
from loguru import logger
from playwright.async_api import async_playwright
from playwright.sync_api import sync_playwright

from playwrightauthor.browser.launcher import launch_chrome

_OBSERVE = """ObjC.import('AppKit'); ObjC.import('CoreGraphics');
var w=ObjC.deepUnwrap(ObjC.castRefToObject($.CGWindowListCopyWindowInfo(1,0)));
JSON.stringify({frontmost:$.NSWorkspace.sharedWorkspace.frontmostApplication.bundleIdentifier.js,
windows:w.filter(x=>x.kCGWindowOwnerName==='Google Chrome for Testing').length});"""


def observe() -> dict:
    """Read frontmost app and on-screen CfT window count without UI automation."""
    result = subprocess.run(
        ["/usr/bin/osascript", "-l", "JavaScript", "-e", _OBSERVE],
        capture_output=True,
        text=True,
        check=True,
        timeout=10,
    )
    return json.loads(result.stdout)


async def check_async(port: int) -> None:
    """Connect to the real launched browser using the async Playwright API."""
    async with async_playwright() as playwright:
        browser = await playwright.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
        page = await browser.contexts[0].new_page()
        await page.goto("data:text/html,<title>async smoke</title><p>headless</p>")
        assert await page.title() == "async smoke"
        await page.close()
        await browser.close()


def verify(binary: str, output: str = "issues/340-headless-launch.json") -> dict:
    """Launch only an owned disposable process; record sampled focus and windows."""
    baseline = observe()
    samples = []
    errors = []
    done = threading.Event()

    def sample() -> None:
        while not done.is_set():
            try:
                samples.append(observe())
            except Exception as error:
                errors.append(type(error).__name__)
                return
            done.wait(0.1)

    observer = threading.Thread(target=sample)
    process = None
    version = None
    with TemporaryDirectory(prefix="pwa340-") as temporary:
        with socket.socket() as reservation:
            reservation.bind(("127.0.0.1", 0))
            port = reservation.getsockname()[1]
        observer.start()
        try:
            process = launch_chrome(
                Path(binary).resolve(),
                Path(temporary),
                port,
                logger,
                extra_args=["--headless=new"],
            )
            with sync_playwright() as playwright:
                browser = playwright.chromium.connect_over_cdp(
                    f"http://127.0.0.1:{port}"
                )
                version = browser.version
                page = browser.contexts[0].new_page()
                page.goto("data:text/html,<title>sync smoke</title><p>headless</p>")
                assert page.title() == "sync smoke"
                page.screenshot(path=str(Path(temporary) / "smoke.png"))
                page.close()
                browser.close()
            asyncio.run(check_async(port))
        finally:
            try:
                if process is not None:
                    process.terminate()
                    process.wait(timeout=10)
                samples.append(observe())
            finally:
                done.set()
                observer.join(timeout=12)
    focus_unchanged = bool(samples) and all(
        sample.get("frontmost") == baseline.get("frontmost") for sample in samples
    )
    no_windows = baseline["windows"] == 0 and all(
        sample["windows"] == 0 for sample in samples
    )
    result = {
        "scope": "legacy launcher only; disposable unauthenticated profile",
        "sync_navigation_screenshot": True,
        "async_new_tab_navigation": True,
        "checked_at": datetime.now(UTC).isoformat(),
        "browser_version": version,
        "focus_unchanged": focus_unchanged,
        "no_visible_cft_windows": no_windows,
        "observation_errors": errors,
        "samples": len(samples),
        "owned_process_stopped": not process.is_running(),
        "not_verified": [
            "Poe login/balance/update",
            "profile leases",
            "Intel hardware",
            "typing target and Spaces",
        ],
    }
    destination = Path(output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, indent=2) + "\n")
    assert not observer.is_alive() and not errors, errors
    assert focus_unchanged and no_windows, (
        "Focus or window count changed; see evidence JSON"
    )
    return result


if __name__ == "__main__":
    fire.Fire(verify)
