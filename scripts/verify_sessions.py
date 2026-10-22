#!/usr/bin/env -S uv run -s
# /// script
# dependencies = ["playwright", "psutil", "loguru", "fire", "filelock"]
# ///
# this_file: scripts/verify_sessions.py
"""Real persistent-context regression with disposable identities and a local site.

No Poe/provider credentials are used. Run from the checkout with `uv run python
scripts/verify_sessions.py --chrome-binary=PATH`. Requires installed Playwright
Chromium and Firefox, plus Chrome for Testing at PATH. Results never include
profile paths, cookie values, window titles or the user's frontmost application.
"""

import asyncio
import json
import select
import subprocess
import sys
import threading
import time
from datetime import UTC, datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from tempfile import TemporaryDirectory

import fire
from verify_headless_launch import _OBSERVE

from playwrightauthor import AsyncBrowserSession, BrowserSession
from playwrightauthor.profiles import ProfileLease
from playwrightauthor.session_errors import ProfileBusy


class LocalPage(BaseHTTPRequestHandler):
    """Serve a stable origin for persistent cookies and localStorage."""

    def do_GET(self) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(b"<title>session smoke</title><p>local session smoke</p>")

    def log_message(self, *args: object) -> None:
        pass


def observe() -> dict:
    """Sample all tested browser window names; never inspect page titles."""
    script = _OBSERVE.replace(
        "x.kCGWindowOwnerName==='Google Chrome for Testing'",
        "['Google Chrome for Testing','Chromium','Firefox','Nightly'].indexOf(x.kCGWindowOwnerName)>=0",
    )
    result = subprocess.run(
        ["/usr/bin/osascript", "-l", "JavaScript", "-e", script],
        capture_output=True,
        text=True,
        check=True,
        timeout=10,
    )
    return json.loads(result.stdout)


async def read_async(options: dict, url: str) -> None:
    """Reopen the same identity with a new Playwright driver and async context."""
    async with AsyncBrowserSession(**options) as session:
        page = await session.new_page()
        await page.goto(url)
        cookies = await session.context.cookies(url)
        assert any(
            cookie["name"] == "smoke" and cookie["value"] == "persisted"
            for cookie in cookies
        )
        assert await page.evaluate("localStorage.getItem('smoke')") == "persisted"
        other = await session.new_page()
        await other.goto(url)
        await page.close()
        assert await other.title() == "session smoke", (
            "A failed/closed task must not close other tabs"
        )
        await other.close()


def check_engine(engine: str, root: Path, url: str, chrome_binary: str) -> dict:
    """Verify context ownership, persistence, same-profile exclusion and isolation."""
    options = {"engine": engine, "profile": "primary", "profile_root": root}
    if engine == "chrome":
        options["executable_path"] = Path(chrome_binary)
    with BrowserSession(**options) as session:
        page = session.new_page()
        page.goto(url)
        session.context.add_cookies(
            [
                {
                    "name": "smoke",
                    "value": "persisted",
                    "url": url,
                    "expires": time.time() + 3600,
                }
            ]
        )
        page.evaluate("localStorage.setItem('smoke','persisted')")
        version = session.browser.version if session.browser else None
        try:
            with BrowserSession(**options):
                raise AssertionError("Concurrent profile writer entered")
        except ProfileBusy:
            pass
        isolated = dict(options, profile="secondary")
        with BrowserSession(**isolated) as other:
            assert not other.context.cookies(url), "Separate identity inherited cookies"
            second = other.new_page()
            second.goto(url)
            second.close()
        assert page.title() == "session smoke", (
            "Other profile shutdown affected this session"
        )
    asyncio.run(read_async(options, url))
    return {
        "engine": engine,
        "version": version,
        "sync_to_async_restart_persistence": True,
        "same_profile_exclusion": True,
        "other_profile_cookie_and_shutdown_isolation": True,
        "independent_task_pages": True,
    }


def check_crashed_lease(root: Path) -> None:
    """An owner killed before cleanup must not leave a false busy lock."""
    directory = root / "lease-crash"
    code = "from pathlib import Path; from playwrightauthor.profiles import ProfileLease; import sys; lease=ProfileLease(Path(sys.argv[1])); lease.acquire(); print('ready', flush=True); sys.stdin.read()"
    owner = subprocess.Popen(
        [sys.executable, "-c", code, str(directory)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,
    )
    try:
        assert select.select([owner.stdout], [], [], 10)[0], (
            "Lease owner did not become ready"
        )
        assert owner.stdout.readline().strip() == "ready"
        contender = ProfileLease(directory)
        try:
            contender.acquire()
            raise AssertionError("Live process lock was ignored")
        except ProfileBusy:
            pass
    finally:
        owner.kill()
        owner.wait(timeout=10)
    contender.acquire()
    contender.release()


def verify(chrome_binary: str, output: str = "issues/340-native-sessions.json") -> dict:
    """Measure runtime results without claiming provider authorization or Intel parity."""
    server = ThreadingHTTPServer(("127.0.0.1", 0), LocalPage)
    serving = threading.Thread(target=server.serve_forever, daemon=True)
    serving.start()
    baseline = observe()
    samples, errors, results = [], [], []
    stop = threading.Event()

    def sample() -> None:
        while not stop.is_set():
            try:
                samples.append(observe())
            except Exception as error:
                errors.append(type(error).__name__)
                return
            stop.wait(0.1)

    sampler = threading.Thread(target=sample)
    sampler.start()
    try:
        with TemporaryDirectory(prefix="pwa340-sessions-") as temporary:
            root = Path(temporary)
            check_crashed_lease(root)
            for engine in ("chrome", "chromium", "firefox"):
                results.append(
                    check_engine(
                        engine,
                        root,
                        f"http://127.0.0.1:{server.server_port}/",
                        chrome_binary,
                    )
                )
    finally:
        stop.set()
        sampler.join(timeout=12)
        server.shutdown()
        server.server_close()
        serving.join(timeout=5)
    evidence = {
        "checked_at": datetime.now(UTC).isoformat(),
        "platform": sys.platform,
        "engines": results,
        "crashed_owner_lease_recovered": True,
        "samples": len(samples),
        "observation_errors": errors,
        "focus_unchanged": bool(samples)
        and all(s.get("frontmost") == baseline.get("frontmost") for s in samples),
        "no_visible_test_browser_windows": baseline["windows"] == 0
        and all(s["windows"] == 0 for s in samples),
        "scope": "disposable local-origin session acceptance only",
        "not_verified": [
            "real service/provider authorization",
            "Poe balance/update parity",
            "Intel hardware",
            "typing target and Spaces",
        ],
    }
    destination = Path(output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(evidence, indent=2) + "\n")
    assert not errors and not sampler.is_alive()
    assert (
        evidence["focus_unchanged"] and evidence["no_visible_test_browser_windows"]
    ), "Focus/window acceptance failed; see recorded evidence"
    return evidence


if __name__ == "__main__":
    fire.Fire(verify)
