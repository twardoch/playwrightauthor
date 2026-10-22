# this_file: src/playwrightauthor/session_options.py
"""Validated identity and native persistent-context launch options."""

from collections.abc import Callable
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from loguru import logger
from playwright.sync_api import Error as PlaywrightError

from .browser.finder import find_chrome_executable
from .config import PlaywrightAuthorConfig, get_config
from .profiles import ProfileLease, validate_profile
from .session_errors import (
    BackendUnsupported,
    EngineUnavailable,
    ProfileBusy,
    SessionError,
)
from .utils.paths import data_dir


@dataclass
class SessionOptions:
    """Settings shared by sync/async sessions; no UI or browser starts at construction."""

    engine: str = "chrome"
    profile: str = "default"
    mode: str = "headless"
    service: str | None = None
    suppress_dialog: bool = False
    verbose: bool = False
    config: PlaywrightAuthorConfig | None = None
    profile_root: Path | None = None
    executable_path: Path | None = None
    auth_probe: Callable[[Any], Any] | None = None
    profile_dir: Path = field(init=False)
    _lease: ProfileLease = field(init=False, repr=False)

    def __post_init__(self) -> None:
        validate_profile(self.profile)
        if self.engine not in {"chrome", "chromium", "firefox", "cloak", "camoufox"}:
            raise BackendUnsupported(f"Unsupported session engine: {self.engine}")
        if self.mode not in {"headless", "interactive", "auto"}:
            raise BackendUnsupported(f"Unsupported session mode: {self.mode}")
        if self.mode == "auto" and self.auth_probe is None:
            raise ValueError("auto mode requires an auth_probe for the target service")
        self.config = deepcopy(self.config or get_config())
        reserved = (
            "--headless",
            "--user-data-dir",
            "--remote-debugging",
            "--no-startup-window",
        )
        if any(
            arg.startswith(reserved)
            for arg in self.config.browser.args
            + self.config.browser.ignore_default_args
        ):
            raise ValueError(
                "Session launch identity and visibility flags are managed by the session API"
            )
        self.profile_dir = (
            (self.profile_root or data_dir() / "profiles") / self.engine / self.profile
        ).resolve()
        self._lease = ProfileLease(self.profile_dir)

    def launch_options(self) -> tuple[str, dict[str, Any]]:
        """Use real Chromium for headless parity, patched Firefox for Gecko."""
        assert self.config is not None
        browser = self.config.browser
        options: dict[str, Any] = {
            "headless": self.mode != "interactive",
            "timeout": browser.timeout,
            "args": list(browser.args),
            "ignore_default_args": list(browser.ignore_default_args),
            "viewport": {
                "width": browser.viewport_width,
                "height": browser.viewport_height,
            },
        }
        if browser.user_agent:
            options["user_agent"] = browser.user_agent
        if self.config.network.proxy:
            options["proxy"] = {"server": self.config.network.proxy}
        if (
            self.engine in {"chromium", "firefox", "camoufox"}
            and self.executable_path is not None
        ):
            raise ValueError(
                "Use Playwright browser installation for chromium/firefox without an executable override"
            )
        if self.engine == "camoufox":
            from .camoufox_session import launch_options

            return "firefox", launch_options(self.profile_dir, options)
        if self.engine == "chromium":
            options["channel"] = "chromium"
        elif self.engine in {"chrome", "cloak"}:
            options["executable_path"] = str(self._binary())
        return ("firefox" if self.engine == "firefox" else "chromium"), options

    def _binary(self) -> Path:
        """Discover supported binaries without modifying installed application signatures."""
        binary = self.executable_path
        if binary is None and self.engine == "chrome":
            binary = find_chrome_executable(logger)
        if binary is None and self.engine == "cloak":
            from .engines.cloak import _ensure_cloakbrowser_importable

            try:
                binary = Path(
                    _ensure_cloakbrowser_importable().download.ensure_binary()
                )
            except ImportError as error:
                raise EngineUnavailable("CloakBrowser is not installed.") from error
        if binary is None or not Path(binary).is_file():
            raise EngineUnavailable(
                f"Install {self.engine} or supply its supported executable_path."
            )
        binary = Path(binary).resolve()
        if self.engine == "chrome" and not any(
            part in str(binary).lower() for part in ("chrome for testing", "chrome-")
        ):
            raise EngineUnavailable(
                "The chrome session engine requires Chrome for Testing."
            )
        return binary


def launch_failure(error: PlaywrightError, engine: str) -> SessionError:
    """Classify launch failures without copying browser arguments or credentials."""
    message = str(error).lower()
    if "singleton" in message or "already in use" in message:
        return ProfileBusy("The browser profile is already open outside this session.")
    if "executable doesn't exist" in message:
        return EngineUnavailable(
            f"Install the {engine} browser before starting this session."
        )
    return SessionError(
        f"The {engine} browser could not start; inspect its installation and profile."
    )
