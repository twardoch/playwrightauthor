# this_file: src/playwrightauthor/profiles.py
"""Profile naming, OS-backed leases and fail-closed legacy CDP attachment."""

import re
import socket
from pathlib import Path

import psutil
from filelock import FileLock, Timeout

from .session_errors import ProfileBusy


def validate_profile(profile: str) -> str:
    """Keep an account identity within a single profile directory."""
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,99}", profile):
        raise ValueError(
            "Profile must be 1-100 letters, digits, dots, underscores or hyphens, starting with a letter or digit"
        )
    return profile


class ProfileLease:
    """Hold an exclusive native file lock for a session's entire lifetime.

    A leftover lock file is harmless: the OS releases the lock on process death.
    Browser data is never deleted to reclaim a profile.
    """

    def __init__(self, directory: Path):
        self.directory = directory.resolve()
        self.lock = FileLock(str(self.directory) + ".lock", mode=0o600)

    def acquire(self) -> None:
        """Fail immediately when another session already owns this identity."""
        self.directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.directory.chmod(0o700)
        try:
            self.lock.acquire(timeout=0)
        except Timeout as error:
            raise ProfileBusy(
                "Profile is in use; close its session before changing modes."
            ) from error

    def __enter__(self) -> "ProfileLease":
        self.acquire()
        return self

    def __exit__(self, *exc: object) -> None:
        self.release()

    def release(self) -> None:
        """Release this caller's lease, safely repeatable during cleanup."""
        self.lock.release()


def validate_attachment(
    process: psutil.Process, directory: Path, executable: Path, headless: bool
) -> None:
    """Never attach to an identity, executable or mode merely matching a port."""
    try:
        args = process.cmdline()
        profiles = [
            arg.split("=", 1)[1] for arg in args if arg.startswith("--user-data-dir=")
        ]
        modes = [
            arg for arg in args if arg == "--headless" or arg.startswith("--headless=")
        ]
        matches = (
            len(profiles) == 1
            and Path(profiles[0]).resolve() == directory.resolve()
            and Path(process.exe()).resolve() == executable.resolve()
            and bool(modes) == headless
            and all(mode in {"--headless", "--headless=new"} for mode in modes)
        )
    except (OSError, psutil.Error, ValueError, TypeError) as error:
        raise ProfileBusy(
            "Cannot verify the running browser's identity; refusing attachment."
        ) from error
    if not matches:
        raise ProfileBusy(
            "Debug port belongs to a different profile, engine or visibility mode; close the matching session explicitly."
        )


def reject_running_profile(directory: Path) -> None:
    """Do not relaunch a detached or externally opened profile in another mode."""
    for process in psutil.process_iter(["cmdline"]):
        try:
            args = process.info["cmdline"] or []
            profiles = [
                arg.split("=", 1)[1]
                for arg in args
                if arg.startswith("--user-data-dir=")
            ]
            profiles.extend(
                args[index + 1]
                for index, arg in enumerate(args[:-1])
                if arg == "--user-data-dir"
            )
            if any(Path(value).resolve() == directory.resolve() for value in profiles):
                raise ProfileBusy(
                    "This profile is already open in another browser process; close it explicitly before starting a new session."
                )
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue


def require_free_debug_port(port: int) -> None:
    """A listening port without a verified browser owner is a collision, not a session."""
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=0.2):
            pass
    except ConnectionRefusedError:
        return
    except OSError as error:
        raise ProfileBusy(
            "Cannot verify availability of the requested debug port."
        ) from error
    raise ProfileBusy(
        "The debug port is already occupied by an unverified process; choose another port or stop its owner explicitly."
    )
