#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["pyobjc-framework-ApplicationServices==12.2.2; sys_platform == 'darwin'", "pyobjc-framework-Cocoa==12.2.2; sys_platform == 'darwin'"]
# ///
# this_file: scripts/verify_macos_attention.py
"""Observe an explicitly supplied headless test command without changing macOS UI.

Uses NSWorkspace's supported activeSpaceDidChangeNotification, per-application
AXFocusedUIElement and on-screen window IDs. Never reads field values, sends
keystrokes, changes Spaces, activates an app or requests accessibility consent.
Docs: https://developer.apple.com/documentation/appkit/nsworkspace/activespacedidchangenotification
"""

import argparse
import json
import math
import platform
import signal
import subprocess
import sys
import tempfile
import time
from datetime import UTC, datetime
from pathlib import Path


def verify(command: list[str], output: Path, timeout: float) -> dict:
    if timeout <= 0 or not math.isfinite(timeout):
        raise ValueError("timeout must be finite and positive")
    if sys.platform != "darwin":
        raise RuntimeError("This observation requires macOS")
    import ApplicationServices as AX
    import Quartz
    from AppKit import NSWorkspace, NSWorkspaceActiveSpaceDidChangeNotification
    from CoreFoundation import CFEqual
    from Foundation import NSDate, NSDefaultRunLoopMode, NSRunLoop

    workspace = NSWorkspace.sharedWorkspace()
    trusted = bool(AX.AXIsProcessTrusted())
    browser_names = {
        "Google Chrome for Testing",
        "Chromium",
        "Firefox",
        "Nightly",
        "Camoufox",
    }

    def sample() -> dict:
        app = workspace.frontmostApplication()
        error, element, role = None, None, None
        if trusted:
            application = AX.AXUIElementCreateApplication(app.processIdentifier())
            AX.AXUIElementSetMessagingTimeout(application, 0.25)
            error, element = AX.AXUIElementCopyAttributeValue(
                application, AX.kAXFocusedUIElementAttribute, None
            )
            if error == 0:
                role_error, role = AX.AXUIElementCopyAttributeValue(
                    element, AX.kAXRoleAttribute, None
                )
                if role_error != 0:
                    role = None
        windows = Quartz.CGWindowListCopyWindowInfo(
            Quartz.kCGWindowListOptionOnScreenOnly, Quartz.kCGNullWindowID
        )
        return {
            "app": str(app.bundleIdentifier() or "unknown"),
            "element": element,
            "error": error,
            "role": role,
            "windows": {
                int(window["kCGWindowNumber"])
                for window in windows
                if window.get("kCGWindowOwnerName") in browser_names
            },
        }

    events = []
    center = workspace.notificationCenter()
    observer = center.addObserverForName_object_queue_usingBlock_(
        NSWorkspaceActiveSpaceDidChangeNotification,
        None,
        None,
        lambda notification: events.append(time.monotonic()),
    )
    center.postNotificationName_object_(
        NSWorkspaceActiveSpaceDidChangeNotification, workspace
    )
    bootstrap = len(events) == 1
    events.clear()
    assert bootstrap, "Spaces notification observer failed its local bootstrap test"
    baseline = sample()
    samples, app_changes, focus_changes, focus_errors, new_windows = (
        0,
        set(),
        0,
        set(),
        set(),
    )
    deadline = time.monotonic() + timeout
    process = None
    try:
        with tempfile.TemporaryFile() as log:
            process = subprocess.Popen(
                command, stdin=subprocess.DEVNULL, stdout=log, stderr=log
            )
            while True:
                current = sample()
                samples += 1
                if current["app"] != baseline["app"]:
                    app_changes.add(current["app"])
                if current["error"]:
                    focus_errors.add(current["error"])
                if (
                    baseline["element"] is not None
                    and current["element"] is not None
                    and not CFEqual(baseline["element"], current["element"])
                ):
                    focus_changes += 1
                new_windows.update(current["windows"] - baseline["windows"])
                if process.poll() is not None:
                    break
                if time.monotonic() >= deadline:
                    raise TimeoutError(
                        "Headless observation command exceeded its deadline"
                    )
                NSRunLoop.currentRunLoop().runMode_beforeDate_(
                    NSDefaultRunLoopMode, NSDate.dateWithTimeIntervalSinceNow_(0.1)
                )
                time.sleep(0.02)
            returncode = process.returncode
    finally:
        center.removeObserver_(observer)
        if process is not None and process.poll() is None:
            process.send_signal(signal.SIGINT)
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.terminate()
                process.wait(timeout=5)
    result = {
        "checked_at": datetime.now(UTC).isoformat(),
        "platform": platform.system() + " " + platform.machine(),
        "child_returncode": returncode,
        "samples": samples,
        "baseline_frontmost": baseline["app"],
        "frontmost_changes": sorted(app_changes),
        "accessibility_already_trusted": trusted,
        "baseline_focused_role": baseline["role"],
        "baseline_focus_error": baseline["error"],
        "focus_query_errors": sorted(focus_errors),
        "focused_object_unchanged": None
        if baseline["element"] is None
        else not focus_changes and not focus_errors,
        "focus_change_samples": focus_changes,
        "new_browser_window_ids": sorted(new_windows),
        "space_observer_self_test": bootstrap,
        "runtime_space_change_notifications": len(events),
        "space_observer_registration_removed": True,
        "not_verified": [
            "actual text typing",
            "Stage Manager layout",
            "other hardware",
            "provider authorization",
        ],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n")
    assert (
        returncode == 0
        and samples
        and not app_changes
        and not new_windows
        and not events
    ), "Native attention acceptance failed; inspect recorded observations"
    assert result["focused_object_unchanged"] is True, (
        "Focused object stability remains unverified"
    )
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path, default=Path("issues/340-macos-attention.json")
    )
    parser.add_argument("--timeout", type=float, default=90)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not command:
        parser.error("Provide an explicit headless verification command after --")
    print(json.dumps(verify(command, args.output, args.timeout), indent=2))
