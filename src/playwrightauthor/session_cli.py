# this_file: src/playwrightauthor/session_cli.py
"""Foreground owned sessions and cooperative, identity-scoped stop requests."""

import json
import math
import os
import tempfile
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit
from uuid import UUID, uuid4

import psutil
from playwright.sync_api import TimeoutError as PlaywrightTimeout

from .profiles import reject_running_profile
from .session_errors import AuthenticationRequired, ProfileBusy
from .session_options import SessionOptions
from .sessions import BrowserSession


def _write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    descriptor, temporary = tempfile.mkstemp(prefix=".cli-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w") as stream:
            json.dump(value, stream)
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def _owner(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
        if UUID(data["token"]).hex != data["token"]:
            return None
        if psutil.Process(data["pid"]).create_time() == data["created"]:
            return dict(data)
    except (psutil.Error, KeyError, TypeError, ValueError):
        pass
    return None


def _probe(url: str, selector: str) -> Any:
    expected = urlsplit(url)
    if expected.scheme not in {"https", "http"} or not expected.hostname:
        raise ValueError("auth_url must be an HTTP(S) service endpoint")

    def check(context: Any) -> bool:
        page = context.new_page()
        try:
            response = page.goto(url, wait_until="domcontentloaded", timeout=30000)
            current = urlsplit(page.url)
            if (
                response is None
                or response.status != 200
                or (current.scheme, current.netloc, current.path)
                != (expected.scheme, expected.netloc, expected.path)
            ):
                return False
            page.locator(selector).first.wait_for(state="visible", timeout=5000)
            return True
        except PlaywrightTimeout:
            return False
        finally:
            page.close()

    return check


def command(
    action: str = "run",
    url: str = "about:blank",
    engine: str = "chrome",
    profile: str = "default",
    mode: str = "headless",
    hold_seconds: float | None = None,
    executable_path: str | None = None,
    profile_root: str | None = None,
    auth_url: str | None = None,
    auth_selector: str | None = None,
) -> dict[str, Any]:
    """Run/login in the foreground; status never launches; stop never kills a PID.

    Login opens an interactive profile for up to 300 seconds. Finish manual login,
    then use session stop from another terminal. Without a service probe,
    authorization remains unknown. The saved profile is retained after shutdown.
    """
    if action not in {"run", "login", "status", "stop"}:
        raise ValueError("action must be run, login, status or stop")
    if bool(auth_url) != bool(auth_selector) or (
        mode == "auto" and not auth_url and action == "run"
    ):
        raise ValueError(
            "Provide both auth_url and auth_selector for a service probe; auto requires them"
        )
    hold = (300 if action == "login" else 0) if hold_seconds is None else hold_seconds
    if hold < 0 or not math.isfinite(hold):
        raise ValueError("hold_seconds must be finite and nonnegative")
    probe = _probe(auth_url, auth_selector) if auth_url and auth_selector else None
    launch_mode = "interactive" if action == "login" else mode
    if action in {"status", "stop"}:
        launch_mode = "headless"
    options: dict[str, Any] = {
        "engine": engine,
        "profile": profile,
        "mode": launch_mode,
        "executable_path": Path(executable_path) if executable_path else None,
        "profile_root": Path(profile_root) if profile_root else None,
        "auth_probe": probe,
        "suppress_dialog": True,
    }
    identity = SessionOptions(**options)
    control = identity.profile_dir / "cli-owner.json"
    owner = _owner(control)
    base = {"engine": engine, "profile": profile, "auth_status": None}
    if action in {"status", "stop"}:
        if owner is None and identity.profile_dir.exists():
            try:
                reject_running_profile(identity.profile_dir)
            except ProfileBusy:
                return base | {"status": "profile_in_use"}
        if action == "stop" and owner:
            _write(identity.profile_dir / (owner["token"] + ".stop"), {})
        return base | {
            "status": "stop_requested"
            if action == "stop" and owner
            else "running"
            if owner
            else "stopped"
        }
    with BrowserSession(**options) as session:
        token = uuid4().hex
        stop = identity.profile_dir / (token + ".stop")
        _write(
            control,
            {
                "pid": os.getpid(),
                "created": psutil.Process().create_time(),
                "token": token,
            },
        )
        try:
            page = session.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            deadline = time.monotonic() + hold
            while (
                time.monotonic() < deadline
                and not stop.exists()
                and not page.is_closed()
            ):
                page.wait_for_timeout(100)
            auth = True if mode == "auto" and action == "run" else session.auth_status()
            if auth is False:
                raise AuthenticationRequired(
                    "The service probe did not verify authorization; sign in explicitly."
                )
            return base | {
                "status": "closed",
                "auth_status": auth,
                "title": None if page.is_closed() else page.title(),
            }
        finally:
            control.unlink(missing_ok=True)
            stop.unlink(missing_ok=True)
