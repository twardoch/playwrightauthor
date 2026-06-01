# this_file: src/playwrightauthor/engines/cloak.py

"""CloakBrowser engine adapter.

Wraps the private CloakBrowser binary discovery and launch flow.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING

from playwrightauthor.browser.launcher import launch_chrome_with_retry
from playwrightauthor.browser.process import get_chrome_process
from playwrightauthor.connection import (
    async_connect_with_retry,
    connect_with_retry,
)
from playwrightauthor.engine import (
    AsyncEngineAdapter,
    EngineAdapter,
)
from playwrightauthor.utils.logger import configure as configure_logger
from playwrightauthor.utils.paths import data_dir as get_data_dir

if TYPE_CHECKING:
    from playwright.async_api import Browser as AsyncBrowser
    from playwright.sync_api import Browser as SyncBrowser

    from playwrightauthor.config import PlaywrightAuthorConfig


def _ensure_cloakbrowser_importable():
    """Ensure cloakbrowser package is importable, checking private/CloakBrowser."""
    try:
        import cloakbrowser

        return cloakbrowser
    except ImportError:
        # Resolve project root (3 levels up from src/playwrightauthor/engines/cloak.py)
        project_root = Path(__file__).resolve().parents[3]
        cloak_path = project_root / "private" / "CloakBrowser"
        if cloak_path.exists() and str(cloak_path) not in sys.path:
            sys.path.insert(0, str(cloak_path))
            try:
                import cloakbrowser

                return cloakbrowser
            except ImportError as e:
                raise ImportError(
                    "CloakBrowser is present in private/CloakBrowser but could not be imported."
                ) from e
        else:
            raise ImportError(
                "CloakBrowser engine requested but private/CloakBrowser package is not available. "
                "Ensure that the private/CloakBrowser directory exists."
            ) from None


def ensure_cloak_browser(
    config: PlaywrightAuthorConfig,
    verbose: bool = False,
    max_retries: int | None = None,
    profile: str = "default",
) -> tuple[str, str]:
    """Ensure CloakBrowser is downloaded, running and ready to connect."""
    logger_instance = configure_logger(verbose)
    debug_port = config.browser.debug_port

    # 1. Check if CloakBrowser/Chromium is already running on the debug port
    existing_proc = get_chrome_process(debug_port)
    profile_data_dir = get_data_dir() / "profiles" / profile
    profile_data_dir.mkdir(parents=True, exist_ok=True)

    if existing_proc:
        logger_instance.info(f"CloakBrowser is already running on port {debug_port}")
        return "", str(profile_data_dir)

    # 2. Get binary path of CloakBrowser (using its downloader)
    cloakbrowser = _ensure_cloakbrowser_importable()
    logger_instance.info("Ensuring CloakBrowser binary is available...")
    binary_path = Path(cloakbrowser.download.ensure_binary())

    # 3. Build stealth args from cloakbrowser config
    stealth_args = list(cloakbrowser.config.get_default_stealth_args())

    # Add proxy if configured
    if config.network.proxy:
        stealth_args.append(f"--proxy-server={config.network.proxy}")

    # Add headless if configured
    if config.browser.headless:
        stealth_args.append("--headless=new")

    # Add custom args if any
    if config.browser.args:
        stealth_args.extend(config.browser.args)

    # 4. Launch CloakBrowser as a detached process
    logger_instance.info("Launching CloakBrowser in debug mode...")
    launch_chrome_with_retry(
        binary_path,
        profile_data_dir,
        debug_port,
        logger_instance,
        max_retries=max_retries or config.network.retry_attempts,
        extra_args=stealth_args,
    )

    return str(binary_path), str(profile_data_dir)


class CloakEngineAdapter(EngineAdapter):
    """CloakBrowser engine using CDP connect."""

    def __init__(
        self,
        config: PlaywrightAuthorConfig,
        profile: str,
        verbose: bool = False,
    ) -> None:
        """Initialize CloakBrowser engine adapter.

        Args:
            config: BrowserConfig instance
            profile: Profile name
            verbose: Enable verbose logging
        """
        self.config = config
        self.profile = profile
        self.verbose = verbose

    def ensure_browser(self) -> None:
        """Ensure CloakBrowser binary is available and launched."""
        ensure_cloak_browser(
            self.config,
            verbose=self.verbose,
            profile=self.profile,
        )

    def start(self, playwright_chromium) -> SyncBrowser:
        """Start CloakBrowser and connect over CDP.

        Args:
            playwright_chromium: Playwright chromium API instance

        Returns:
            Playwright Browser instance connected over CDP.
        """
        self.ensure_browser()
        debug_port = self.config.browser.debug_port
        max_retries = self.config.network.retry_attempts
        retry_delay = self.config.network.retry_delay
        timeout = self.config.browser.timeout // 1000

        browser = connect_with_retry(
            playwright_chromium,
            debug_port,
            max_retries=max_retries,
            retry_delay=retry_delay,
            timeout=timeout,
        )
        return browser

    def __repr__(self) -> str:
        return (
            f"CloakEngineAdapter(profile={self.profile!r}, "
            f"port={self.config.browser.debug_port})"
        )


class AsyncCloakEngineAdapter(AsyncEngineAdapter):
    """Async CloakBrowser engine using CDP connect."""

    def __init__(
        self,
        config: PlaywrightAuthorConfig,
        profile: str,
        verbose: bool = False,
    ) -> None:
        """Initialize async CloakBrowser engine adapter.

        Args:
            config: BrowserConfig instance
            profile: Profile name
            verbose: Enable verbose logging
        """
        self.config = config
        self.profile = profile
        self.verbose = verbose

    async def ensure_browser_async(self) -> None:
        """Ensure CloakBrowser binary is available and launched (runs sync launch)."""
        ensure_cloak_browser(
            self.config,
            verbose=self.verbose,
            profile=self.profile,
        )

    async def start_async(self, playwright_chromium) -> AsyncBrowser:
        """Start CloakBrowser and connect over CDP asynchronously.

        Args:
            playwright_chromium: Playwright async chromium API instance

        Returns:
            Async Playwright Browser instance connected over CDP.
        """
        await self.ensure_browser_async()
        debug_port = self.config.browser.debug_port
        max_retries = self.config.network.retry_attempts
        retry_delay = self.config.network.retry_delay
        timeout = self.config.browser.timeout // 1000

        browser = await async_connect_with_retry(
            playwright_chromium,
            debug_port,
            max_retries=max_retries,
            retry_delay=retry_delay,
            timeout=timeout,
        )
        return browser

    def __repr__(self) -> str:
        return (
            f"AsyncCloakEngineAdapter(profile={self.profile!r}, "
            f"port={self.config.browser.debug_port})"
        )
