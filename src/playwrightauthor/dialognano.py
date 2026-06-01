#!/usr/bin/env python3
# this_file: src/playwrightauthor/dialognano.py
"""dialognano: a zero-dependency, cross-platform modal dialog in one function.

Shows a simple message dialog with either a single "OK" button, or two
buttons "OK" and "Cancel". No third-party packages: it drives the native
dialog facility of each OS, falling back to tkinter (stdlib) and finally a
plain terminal prompt.

    from dialognano import dialog

    dialog("Saved successfully.")                 # one OK button
    if dialog("Delete the file?", ok_cancel=True):  # OK / Cancel
        ...
"""

from __future__ import annotations


def notify_interactive_task(
    task: str,
    profile: str,
    service: str | None = None,
    suppress: bool = False,
) -> bool:
    """Show an interactive-browser task notice unless suppressed."""
    if suppress:
        return True

    service_line = f"Service: {service}" if service else "Service: not specified"
    message = "\n".join(
        [
            "PlaywrightAuthor opened a persistent browser profile for an interactive task.",
            "",
            service_line,
            f"Profile: {profile}",
            f"Task: {task}",
            "",
            "Use the browser window to finish any required sign-in, consent, captcha, or other manual check.",
            "After that, return to the command or script that requested this browser.",
        ]
    )
    return dialog(message, title="PlaywrightAuthor needs your browser")


def dialog(message: str, title: str = "Message", ok_cancel: bool = False) -> bool:
    """Display a modal dialog and return the user's choice.

    Args:
        message: The text shown in the dialog body.
        title: The window/title-bar text.
        ok_cancel: If False (default) show a single "OK" button. If True show
            both "OK" and "Cancel".

    Returns:
        True if the user pressed "OK" (or, for a one-button dialog, dismissed
        it). False if the user pressed "Cancel" or closed an "OK/Cancel"
        dialog without confirming.

    The function tries, in order: the OS-native dialog, tkinter, then a
    terminal prompt. The first mechanism that works wins; failures fall
    through to the next so it always returns something.
    """
    import sys

    message = str(message)
    title = str(title)

    # --- 1. OS-native dialog ------------------------------------------------
    try:
        if sys.platform == "darwin":
            import subprocess

            buttons = '{"Cancel", "OK"}' if ok_cancel else '{"OK"}'
            # Pass message/title as argv to sidestep AppleScript quoting.
            script = (
                "on run argv\n"
                "  display dialog (item 1 of argv) with title (item 2 of argv) "
                "buttons "
                + buttons
                + ' default button "OK"'
                + (' cancel button "Cancel"' if ok_cancel else "")
                + "\n"
                "end run"
            )
            proc = subprocess.run(
                ["osascript", "-e", script, message, title],
                capture_output=True,
            )
            # osascript exits 0 on OK; non-zero (user-cancelled = 1) otherwise.
            return proc.returncode == 0

        if sys.platform == "win32":
            import ctypes

            MB_OK = 0x0
            MB_OKCANCEL = 0x1
            MB_ICONINFORMATION = 0x40
            IDOK = 1
            flags = (MB_OKCANCEL if ok_cancel else MB_OK) | MB_ICONINFORMATION
            res = ctypes.windll.user32.MessageBoxW(0, message, title, flags)
            return res == IDOK

        # Linux / other Unix: prefer zenity if present.
        import shutil
        import subprocess

        if shutil.which("zenity"):
            if ok_cancel:
                cmd = [
                    "zenity",
                    "--question",
                    "--title",
                    title,
                    "--text",
                    message,
                    "--ok-label",
                    "OK",
                    "--cancel-label",
                    "Cancel",
                ]
            else:
                cmd = ["zenity", "--info", "--title", title, "--text", message]
            return subprocess.run(cmd).returncode == 0
    except Exception:
        pass  # fall through to tkinter

    # --- 2. tkinter (standard library, works everywhere it's installed) -----
    try:
        import tkinter
        from tkinter import messagebox

        root = tkinter.Tk()
        root.withdraw()
        try:
            if ok_cancel:
                result = bool(messagebox.askokcancel(title, message))
            else:
                messagebox.showinfo(title, message)
                result = True
        finally:
            root.destroy()
        return result
    except Exception:
        pass  # fall through to terminal

    # --- 3. Terminal fallback ----------------------------------------------
    banner = f"{title}\n{message}" if title else message
    if not ok_cancel:
        try:
            input(banner + "\n[Press Enter to continue] ")
        except (EOFError, KeyboardInterrupt):
            pass
        return True
    try:
        answer = input(banner + "\n[OK]/Cancel? ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        return False
    return answer in ("", "o", "ok", "y", "yes")


if __name__ == "__main__":
    confirmed = dialog("Proceed with the operation?", "dialognano demo", ok_cancel=True)
    dialog("You chose: %s" % ("OK" if confirmed else "Cancel"), "dialognano demo")
