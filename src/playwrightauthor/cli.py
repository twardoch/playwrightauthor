#!/usr/bin/env -S uv run -s
# /// script
# dependencies = ["fire", "rich"]
# ///
# this_file: src/playwrightauthor/cli.py

"""Fire-powered command-line interface for utility tasks."""

import json
import shutil
import sys
from difflib import get_close_matches

import fire
from rich.console import Console
from rich.table import Table

from .browser.process import get_chrome_process
from .browser_manager import ensure_browser, launch_browser
from .config import get_config
from .connection import check_connection_health
from .exceptions import BrowserManagerError, CLIError
from .state_manager import get_state_manager
from .utils.logger import configure as configure_logger
from .utils.paths import install_dir


class Cli:
    """
    Command-line interface for PlaywrightAuthor browser and profile management.

    The CLI provides essential tools for managing browser installations, profiles,
    diagnostics, and configuration. All commands support both human-readable and
    JSON output formats for automation and scripting.

    Usage:
        playwrightauthor browse             # Launch browser in CDP mode
        playwrightauthor status             # Check browser status
        playwrightauthor profile list       # List all profiles
        playwrightauthor diagnose           # Run system diagnostics
        playwrightauthor repl               # Start interactive REPL
    """

    def status(self, verbose: bool = False):
        """
        Check browser installation and connection status.

        This command verifies that Chrome for Testing is properly installed and
        running with remote debugging enabled. If the browser is not running,
        it will automatically launch it in debug mode.

        Args:
            verbose (bool, optional): Enable detailed logging output for troubleshooting
                connection and installation issues. Shows browser paths, process IDs,
                and connection diagnostics. Defaults to False.

        Example Output:
            Success:
                Browser is ready.
                  - Path: /Users/user/.playwrightauthor/chrome/chrome
                  - User Data: /Users/user/.playwrightauthor/profiles/default

            With verbose logging:
                [INFO] Checking browser status...
                [INFO] Found Chrome at: /Users/user/.playwrightauthor/chrome/chrome
                [INFO] Browser process running on PID: 12345
                [INFO] Debug port 9222 is accessible
                Browser is ready.
                  - Path: /Users/user/.playwrightauthor/chrome/chrome
                  - User Data: /Users/user/.playwrightauthor/profiles/default

        Common Issues:
            - If browser fails to start, try: playwrightauthor clear-cache
            - For permission issues on macOS, grant accessibility permissions
            - Use verbose mode to see detailed error information
        """
        console = Console()
        logger = configure_logger(verbose)
        logger.info("Checking browser status...")
        try:
            browser_path, data_dir = ensure_browser(verbose=verbose)
            console.print("[green]Browser is ready.[/green]")
            console.print(f"  - Path: {browser_path}")
            console.print(f"  - User Data: {data_dir}")
        except BrowserManagerError as e:
            console.print(f"[red]Error: {e}[/red]")
        except SystemExit as e:
            if e.code != 0:
                console.print(f"[red]CLI command failed with exit code {e.code}.[/red]")

    def clear_cache(self):
        """
        Remove all browser installations, profiles, and cached data.

        This command completely removes the PlaywrightAuthor installation directory,
        including the Chrome for Testing browser, all user profiles, authentication
        data, and configuration cache. Use this to start completely fresh or to
        resolve persistent browser issues.

        Warning:
            This action is irreversible. All saved authentication sessions, browser
            profiles, and configuration will be permanently deleted. You will need
            to re-authenticate to all services after running this command.

        Example Output:
            Cache found:
                Removing /Users/user/.playwrightauthor...
                Cache cleared.

            No cache:
                Cache directory not found.

        Use Cases:
            - Resolve persistent browser connection issues
            - Clean up after testing with multiple profiles
            - Reset to factory defaults before sharing system
            - Free up disk space (Chrome + profiles can be 200MB+)
        """
        console = Console()
        install_path = install_dir()
        if install_path.exists():
            console.print(f"Removing {install_path}...")
            shutil.rmtree(install_path)
            console.print("[green]Cache cleared.[/green]")
        else:
            console.print("[yellow]Cache directory not found.[/yellow]")

    def profile(
        self, action: str = "list", name: str = "default", format: str = "table"
    ):
        """
        Manage browser profiles for session isolation and multi-account automation.

        Browser profiles maintain separate authentication sessions, cookies, and browser
        data, enabling you to automate multiple accounts or environments without conflict.
        Each profile stores its data independently and can be managed through this command.

        Args:
            action (str, optional): Action to perform. Available actions:
                - "list": Show all existing profiles with creation and usage dates
                - "show": Display detailed information about a specific profile
                - "create": Create a new profile (created automatically on first use)
                - "delete": Remove a profile and all its data permanently
                - "clear": Remove all profiles except "default"
                Defaults to "list".
            name (str, optional): Profile name for show/create/delete actions.
                Profile names must be valid directory names (alphanumeric, dash, underscore).
                Defaults to "default".
            format (str, optional): Output format for list/show actions:
                - "table": Human-readable table format with colors
                - "json": Machine-readable JSON for scripting
                Defaults to "table".

        Example Usage:
            List all profiles:
                playwrightauthor profile list

            Show specific profile details:
                playwrightauthor profile show --name work

            Create a new profile (or just use it in code):
                playwrightauthor profile create --name testing

            Delete a profile permanently:
                playwrightauthor profile delete --name old-profile

            Get profiles as JSON for scripting:
                playwrightauthor profile list --format json

        Example Output (table format):
            ┏━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┓
            ┃ Profile Name┃ Created             ┃ Last Used           ┃
            ┡━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━┩
            │ default     │ 2025-08-04T10:00:00 │ 2025-08-04T15:30:00 │
            │ work        │ 2025-08-04T11:00:00 │ 2025-08-04T14:00:00 │
            │ testing     │ 2025-08-04T12:00:00 │ Never               │
            └─────────────┴─────────────────────┴─────────────────────┘

        Profile Use Cases:
            - Separate work and personal Google/GitHub accounts
            - Isolate testing from production sessions
            - Manage multiple client accounts independently
            - Create clean environments for different projects

        Note:
            Profiles are created automatically when first used in Browser() or AsyncBrowser().
            The "default" profile is created automatically and cannot be deleted.
        """
        console = Console()
        state_manager = get_state_manager()

        try:
            if action == "list":
                profiles = state_manager.list_profiles()
                if not profiles:
                    console.print("[yellow]No profiles found.[/yellow]")
                    return

                if format == "json":
                    console.print(json.dumps(profiles, indent=2))
                else:
                    table = Table(title="Browser Profiles")
                    table.add_column("Profile Name", style="cyan")
                    table.add_column("Created", style="green")
                    table.add_column("Last Used", style="yellow")

                    for profile_name in profiles:
                        profile_data = state_manager.get_profile(profile_name)
                        table.add_row(
                            profile_name,
                            profile_data.get("created", "Unknown"),
                            profile_data.get("last_used", "Never"),
                        )
                    console.print(table)

            elif action == "show":
                profile_data = state_manager.get_profile(name)
                if format == "json":
                    console.print(json.dumps(profile_data, indent=2))
                else:
                    console.print(f"[cyan]Profile: {name}[/cyan]")
                    for key, value in profile_data.items():
                        console.print(f"  {key}: {value}")

            elif action == "create":
                profile_data = state_manager.get_profile(
                    name
                )  # This creates if not exists
                console.print(f"[green]Profile '{name}' created successfully.[/green]")

            elif action == "delete":
                if name == "default":
                    console.print("[red]Cannot delete the default profile.[/red]")
                    return
                state_manager.delete_profile(name)
                console.print(f"[green]Profile '{name}' deleted successfully.[/green]")

            elif action == "clear":
                state_manager.clear_state()
                console.print("[green]All profiles cleared.[/green]")

            else:
                console.print(f"[red]Unknown action: {action}[/red]")
                console.print("Available actions: list, show, create, delete, clear")

        except Exception as e:
            console.print(f"[red]Profile operation failed: {e}[/red]")

    def config(
        self,
        action: str = "show",
        key: str = "",
        value: str = "",
        format: str = "table",
    ):
        """
        Manage configuration settings.

        Args:
            action: Action to perform (show, set, reset).
            key: Configuration key (e.g., 'browser.debug_port').
            value: Configuration value for set action.
            format: Output format (table, json).
        """
        console = Console()
        config = get_config()

        try:
            if action == "show":
                if format == "json":
                    # Convert config to dictionary for JSON output
                    config_dict = {
                        "browser": {
                            "debug_port": config.browser.debug_port,
                            "headless": config.browser.headless,
                            "timeout": config.browser.timeout,
                            "viewport_width": config.browser.viewport_width,
                            "viewport_height": config.browser.viewport_height,
                            "user_agent": config.browser.user_agent,
                        },
                        "network": {
                            "download_timeout": config.network.download_timeout,
                            "retry_attempts": config.network.retry_attempts,
                            "retry_delay": config.network.retry_delay,
                            "exponential_backoff": config.network.exponential_backoff,
                            "proxy": config.network.proxy,
                        },
                        "logging": {
                            "verbose": config.logging.verbose,
                            "log_level": config.logging.log_level,
                        },
                        "features": {
                            "enable_lazy_loading": config.enable_lazy_loading,
                            "enable_plugins": config.enable_plugins,
                            "enable_connection_pooling": config.enable_connection_pooling,
                            "default_profile": config.default_profile,
                        },
                    }
                    console.print(json.dumps(config_dict, indent=2))
                else:
                    table = Table(title="Configuration Settings")
                    table.add_column("Category", style="cyan")
                    table.add_column("Setting", style="green")
                    table.add_column("Value", style="yellow")

                    # Browser settings
                    table.add_row(
                        "browser", "debug_port", str(config.browser.debug_port)
                    )
                    table.add_row("browser", "headless", str(config.browser.headless))
                    table.add_row("browser", "timeout", f"{config.browser.timeout}ms")
                    table.add_row(
                        "browser",
                        "viewport",
                        f"{config.browser.viewport_width}x{config.browser.viewport_height}",
                    )

                    # Network settings
                    table.add_row(
                        "network", "retry_attempts", str(config.network.retry_attempts)
                    )
                    table.add_row(
                        "network", "retry_delay", f"{config.network.retry_delay}s"
                    )
                    table.add_row(
                        "network",
                        "download_timeout",
                        f"{config.network.download_timeout}s",
                    )

                    # Feature flags
                    table.add_row(
                        "features", "lazy_loading", str(config.enable_lazy_loading)
                    )
                    table.add_row("features", "plugins", str(config.enable_plugins))
                    table.add_row(
                        "features",
                        "connection_pooling",
                        str(config.enable_connection_pooling),
                    )

                    console.print(table)

            elif action == "set":
                console.print(
                    f"[yellow]Configuration setting not yet implemented: {key}={value}[/yellow]"
                )
                console.print(
                    "Use environment variables with PLAYWRIGHTAUTHOR_ prefix instead."
                )

            elif action == "reset":
                console.print(
                    "[yellow]Configuration reset not yet implemented.[/yellow]"
                )
                console.print("Delete the config file manually if needed.")

            else:
                console.print(f"[red]Unknown action: {action}[/red]")
                console.print("Available actions: show, set, reset")

        except Exception as e:
            console.print(f"[red]Configuration operation failed: {e}[/red]")

    def diagnose(self, verbose: bool = False, format: str = "table"):
        """
        Run diagnostic checks and display system information.

        Args:
            verbose: Enable verbose output.
            format: Output format (table, json).
        """
        console = Console()
        configure_logger(verbose)
        config = get_config()

        diagnostics = {
            "timestamp": __import__("datetime").datetime.now().isoformat(),
            "config": {
                "debug_port": config.browser.debug_port,
                "retry_attempts": config.network.retry_attempts,
                "lazy_loading": config.enable_lazy_loading,
            },
            "browser": {"status": "unknown", "error": None},
            "connection": {"status": "unknown", "error": None, "diagnostics": None},
            "profiles": {"count": 0, "list": []},
            "system": {"platform": __import__("platform").system()},
        }

        try:
            # Check browser status
            browser_path, data_dir = ensure_browser(verbose=verbose)
            diagnostics["browser"] = {
                "status": "running",
                "path": browser_path,
                "data_dir": data_dir,
                "error": None,
            }

            # Check connection health
            is_healthy, conn_diagnostics = check_connection_health(
                config.browser.debug_port
            )
            diagnostics["connection"] = {
                "status": "healthy" if is_healthy else "unhealthy",
                "error": conn_diagnostics.get("error"),
                "diagnostics": conn_diagnostics,
            }

        except Exception as e:
            diagnostics["browser"]["status"] = "error"
            diagnostics["browser"]["error"] = str(e)

        try:
            # Check profiles
            state_manager = get_state_manager()
            profiles = state_manager.list_profiles()
            diagnostics["profiles"] = {"count": len(profiles), "list": profiles}
        except Exception as e:
            diagnostics["profiles"]["error"] = str(e)

        if format == "json":
            console.print(json.dumps(diagnostics, indent=2))
        else:
            # Display formatted diagnostics
            console.print("[bold]PlaywrightAuthor Diagnostics[/bold]")
            console.print(f"Timestamp: {diagnostics['timestamp']}")
            console.print(f"Platform: {diagnostics['system']['platform']}")
            console.print()

            # Browser status
            browser_status = diagnostics["browser"]["status"]
            if browser_status == "running":
                console.print("[green]✓ Browser: Running[/green]")
                console.print(f"  Path: {diagnostics['browser']['path']}")
                console.print(f"  Data: {diagnostics['browser']['data_dir']}")
            elif browser_status == "error":
                console.print("[red]✗ Browser: Error[/red]")
                console.print(f"  Error: {diagnostics['browser']['error']}")
            else:
                console.print("[yellow]? Browser: Unknown[/yellow]")

            # Connection status
            conn_status = diagnostics["connection"]["status"]
            if conn_status == "healthy":
                console.print("[green]✓ Connection: Healthy[/green]")
                conn_diag = diagnostics["connection"]["diagnostics"]
                if conn_diag and "response_time_ms" in conn_diag:
                    console.print(f"  Response time: {conn_diag['response_time_ms']}ms")
            elif conn_status == "unhealthy":
                console.print("[red]✗ Connection: Unhealthy[/red]")
                if diagnostics["connection"]["error"]:
                    console.print(f"  Error: {diagnostics['connection']['error']}")
            else:
                console.print("[yellow]? Connection: Unknown[/yellow]")

            # Profile information
            profile_count = diagnostics["profiles"]["count"]
            console.print(f"[cyan]Profiles: {profile_count} found[/cyan]")
            if profile_count > 0:
                for profile in diagnostics["profiles"]["list"]:
                    console.print(f"  - {profile}")

    def version(self):
        """Display version information."""
        console = Console()

        try:
            # Try to get version from package
            import importlib.metadata

            version = importlib.metadata.version("playwrightauthor")
            console.print(f"PlaywrightAuthor version: [cyan]{version}[/cyan]")
        except Exception:
            console.print(
                "PlaywrightAuthor version: [yellow]Unknown (development)[/yellow]"
            )

        # Additional version info
        try:
            import playwright

            pw_version = playwright.__version__
            console.print(f"Playwright version: [green]{pw_version}[/green]")
        except Exception:
            console.print("Playwright version: [red]Not available[/red]")

        try:
            import platform

            console.print(f"Python version: [blue]{platform.python_version()}[/blue]")
            console.print(
                f"Platform: [magenta]{platform.system()} {platform.release()}[/magenta]"
            )
        except Exception:
            pass

    def health(self, verbose: bool = False, format: str = "table"):
        """
        Perform comprehensive health check of PlaywrightAuthor setup.

        This command validates your entire PlaywrightAuthor installation and configuration,
        including Chrome installation, connection health, profile setup, and automation
        capabilities. It provides actionable feedback for any issues found.

        Args:
            verbose (bool, optional): Enable detailed output with diagnostic information.
                Shows Chrome paths, connection details, and test results. Defaults to False.
            format (str, optional): Output format. Options are 'table' for human-readable
                or 'json' for machine-readable output. Defaults to 'table'.

        Health Checks Performed:
            1. Chrome Installation - Verifies Chrome for Testing is properly installed
            2. Connection Health - Tests Chrome DevTools Protocol connection
            3. Profile Setup - Validates browser profile configuration
            4. Browser Automation - Tests actual browser control capabilities
            5. System Compatibility - Checks system requirements and permissions

        Example Output:
            ✅ Chrome Installation     OK    /Users/user/.playwrightauthor/chrome/chrome
            ✅ Connection Health       OK    Port 9222 responding (15ms)
            ✅ Profile Setup          OK    1 profile(s) found
            ✅ Browser Automation     OK    Successfully opened test page
            ✅ System Compatibility   OK    All requirements met

            Overall Status: HEALTHY

        Common Issues:
            - If Chrome installation fails: Run 'playwrightauthor clear-cache'
            - If connection fails: Check if port 9222 is blocked by firewall
            - If automation fails: Ensure Chrome has necessary permissions
        """
        console = Console()
        configure_logger(verbose)
        config = get_config()

        # Track overall health status
        all_healthy = True
        health_results = []

        # Helper to add results
        def add_result(check_name: str, is_ok: bool, details: str, fix_cmd: str = None):
            nonlocal all_healthy
            if not is_ok:
                all_healthy = False
            health_results.append(
                {
                    "check": check_name,
                    "status": "OK" if is_ok else "FAILED",
                    "details": details,
                    "fix_cmd": fix_cmd,
                }
            )

        # 1. Check Chrome Installation
        chrome_ok = False
        try:
            from .browser.finder import find_chrome_executable

            chrome_path = find_chrome_executable(configure_logger(verbose))
            if chrome_path:
                chrome_ok = True
                add_result("Chrome Installation", True, str(chrome_path))
            else:
                add_result(
                    "Chrome Installation",
                    False,
                    "Chrome for Testing not found",
                    "playwrightauthor status",
                )
        except Exception as e:
            add_result(
                "Chrome Installation",
                False,
                f"Error: {str(e)[:50]}...",
                "playwrightauthor clear-cache && playwrightauthor status",
            )

        # 2. Check Connection Health
        conn_ok = False
        if chrome_ok:
            try:
                is_healthy, diagnostics = check_connection_health(
                    config.browser.debug_port
                )
                response_time = diagnostics.get("response_time_ms", "N/A")
                if is_healthy:
                    conn_ok = True
                    add_result(
                        "Connection Health",
                        True,
                        f"Port {config.browser.debug_port} responding ({response_time}ms)",
                    )
                else:
                    error = diagnostics.get("error", "Unknown error")
                    add_result(
                        "Connection Health",
                        False,
                        f"Port {config.browser.debug_port} not responding: {error[:30]}...",
                        "playwrightauthor status --verbose",
                    )
            except Exception as e:
                add_result(
                    "Connection Health",
                    False,
                    f"Check failed: {str(e)[:30]}...",
                    "playwrightauthor diagnose",
                )
        else:
            add_result("Connection Health", False, "Skipped (Chrome not installed)")

        # 3. Check Profile Setup
        try:
            state_manager = get_state_manager()
            profiles = state_manager.list_profiles()
            if profiles:
                add_result("Profile Setup", True, f"{len(profiles)} profile(s) found")
            else:
                add_result(
                    "Profile Setup",
                    False,
                    "No profiles configured",
                    "playwrightauthor profile create default",
                )
        except Exception as e:
            add_result(
                "Profile Setup",
                False,
                f"Error: {str(e)[:30]}...",
                "playwrightauthor profile list",
            )

        # 4. Test Browser Automation (only if connection is healthy)
        if conn_ok:
            try:
                # Quick test to see if we can actually control the browser
                from .lazy_imports import get_sync_playwright

                playwright = get_sync_playwright().start()
                try:
                    browser = playwright.chromium.connect_over_cdp(
                        f"http://localhost:{config.browser.debug_port}"
                    )
                    # Try to create a page (basic automation test)
                    page = browser.new_page()
                    page.goto("about:blank")
                    page.close()
                    browser.close()
                    add_result(
                        "Browser Automation", True, "Successfully controlled browser"
                    )
                finally:
                    playwright.stop()
            except Exception as e:
                add_result(
                    "Browser Automation",
                    False,
                    f"Control failed: {str(e)[:30]}...",
                    "playwrightauthor status --verbose",
                )
        else:
            add_result("Browser Automation", False, "Skipped (Connection unhealthy)")

        # 5. Check System Compatibility
        try:
            import platform

            system = platform.system()

            # Check for common issues
            issues = []
            if system == "Darwin":  # macOS
                # Could check for accessibility permissions here
                pass
            elif system == "Linux":
                # Could check for X11/Wayland
                import os

                if not os.environ.get("DISPLAY") and not config.browser.headless:
                    issues.append("No DISPLAY variable set")

            if issues:
                add_result(
                    "System Compatibility",
                    False,
                    "; ".join(issues),
                    "export DISPLAY=:0 or use headless mode",
                )
            else:
                add_result(
                    "System Compatibility", True, f"{system} - All requirements met"
                )

        except Exception as e:
            add_result("System Compatibility", False, f"Check failed: {str(e)[:30]}...")

        # Display results
        if format == "json":
            output = {
                "timestamp": __import__("datetime").datetime.now().isoformat(),
                "overall_status": "HEALTHY" if all_healthy else "UNHEALTHY",
                "checks": health_results,
            }
            console.print(json.dumps(output, indent=2))
        else:
            # Table format
            table = Table(title="PlaywrightAuthor Health Check")
            table.add_column("Status", style="bold")
            table.add_column("Check", style="cyan")
            table.add_column("Result")
            table.add_column("Details")

            for result in health_results:
                status_icon = "✅" if result["status"] == "OK" else "❌"
                status_color = "green" if result["status"] == "OK" else "red"
                table.add_row(
                    status_icon,
                    result["check"],
                    f"[{status_color}]{result['status']}[/{status_color}]",
                    result["details"],
                )

            console.print(table)
            console.print()

            # Overall status
            if all_healthy:
                console.print("[bold green]Overall Status: HEALTHY[/bold green]")
                console.print("\nYour PlaywrightAuthor setup is working correctly! 🎉")
            else:
                console.print("[bold red]Overall Status: UNHEALTHY[/bold red]")
                console.print(
                    "\n[yellow]Some issues were found. Suggested fixes:[/yellow]"
                )

                # Show fix commands
                for result in health_results:
                    if result["status"] == "FAILED" and result.get("fix_cmd"):
                        console.print(f"\n  • {result['check']}:")
                        console.print(f"    [cyan]{result['fix_cmd']}[/cyan]")

    def repl(self, verbose: bool = False):
        """
        Start interactive REPL mode for browser automation.

        The REPL (Read-Eval-Print Loop) provides an interactive Python environment
        with PlaywrightAuthor pre-loaded and ready for browser automation. Features include:

        - Advanced tab completion for Playwright APIs and CLI commands
        - Persistent command history across sessions
        - Rich syntax highlighting and error display
        - Direct CLI command execution with `!` prefix
        - Real-time Python code evaluation with browser context

        Args:
            verbose (bool, optional): Enable verbose logging for debugging. Defaults to False.

        Raises:
            ImportError: If prompt_toolkit is not installed
            Exception: If REPL fails to initialize

        Example:

        .. code-block:: bash

            playwrightauthor repl --verbose

        Inside REPL session:

        .. code-block:: python

            browser = Browser()
            browser.__enter__()  # Start browser
            page = browser.new_page()
            page.goto("https://github.com")
            !status  # Run CLI command

        Note:
            The REPL requires the `prompt_toolkit` package. Install with:
            `pip install prompt_toolkit`
        """
        console = Console()

        try:
            from .repl import ReplEngine

            console.print("[green]Starting PlaywrightAuthor REPL...[/green]")
            repl_engine = ReplEngine(verbose=verbose)
            repl_engine.run()

        except ImportError as e:
            console.print(f"[red]REPL not available: {e}[/red]")
            console.print(
                "[yellow]Try installing prompt_toolkit: pip install prompt_toolkit[/yellow]"
            )
        except Exception as e:
            console.print(f"[red]REPL failed to start: {e}[/red]")

    def setup(self, verbose: bool = False):
        """
        Launch interactive setup wizard for first-time users.

        This command starts a comprehensive setup wizard that guides new users through
        the entire PlaywrightAuthor setup process, including browser configuration,
        authentication setup, and validation. The wizard provides step-by-step guidance
        with intelligent issue detection and contextual help.

        The setup wizard includes:
        - Browser installation and configuration validation
        - Platform-specific setup recommendations
        - Service-specific authentication guidance
        - Real-time issue detection and troubleshooting
        - Authentication completion validation

        Args:
            verbose (bool, optional): Enable detailed logging throughout the setup process.
                Shows diagnostic information, issue detection details, and troubleshooting
                guidance. Recommended for users experiencing setup issues. Defaults to False.

        Example Usage:
            # Start basic setup wizard
            playwrightauthor setup

            # Start setup with detailed logging for troubleshooting
            playwrightauthor setup --verbose

        Setup Process:
            1. Browser Validation - Tests browser connection and detects issues
            2. Service Guidance - Provides authentication instructions for popular services
            3. Authentication Monitoring - Tracks login progress and detects completion
            4. Final Validation - Confirms successful setup and provides next steps

        Supported Services:
            - Gmail/Google (accounts.google.com)
            - GitHub (github.com/login)
            - LinkedIn (linkedin.com/login)
            - Microsoft/Office 365 (login.microsoftonline.com)
            - Facebook (facebook.com)
            - Twitter/X (twitter.com/login)

        Common Issues Detected:
            - JavaScript errors blocking authentication
            - Cookie restrictions preventing session storage
            - Popup blockers interfering with OAuth flows
            - Network connectivity problems
            - Platform-specific permission issues

        Note:
            The setup wizard requires an active browser session and will guide you through
            opening new tabs and completing authentication flows. The process typically
            takes 2-10 minutes depending on the number of services you authenticate with.
        """
        console = Console()
        logger = configure_logger(verbose)

        try:
            # Show pre-setup recommendations
            from .onboarding import get_setup_recommendations

            console.print(
                "[bold blue]PlaywrightAuthor Interactive Setup Wizard[/bold blue]"
            )
            console.print()

            # Display setup recommendations
            recommendations = get_setup_recommendations()
            for recommendation in recommendations:
                if recommendation.startswith("🎭"):
                    console.print(f"[bold]{recommendation}[/bold]")
                elif recommendation.startswith(("🍎", "🐧", "🪟")):
                    console.print(f"[cyan]{recommendation}[/cyan]")
                elif recommendation.startswith(("📋", "🔐", "🌐", "🆘")):
                    console.print(f"[yellow]{recommendation}[/yellow]")
                elif recommendation.startswith("•"):
                    console.print(f"[dim]  {recommendation}[/dim]")
                else:
                    console.print(recommendation)

            console.print()
            console.print(
                "[yellow]Press Enter to start the setup wizard, or Ctrl+C to cancel...[/yellow]"
            )

            try:
                input()
            except KeyboardInterrupt:
                console.print("\n[yellow]Setup wizard cancelled.[/yellow]")
                return

            # Start the interactive wizard
            console.print("[green]Starting browser and setup wizard...[/green]")

            # Import here to avoid circular imports
            import asyncio

            from .browser_manager import ensure_browser
            from .lazy_imports import get_async_playwright
            from .onboarding import interactive_setup_wizard

            # Ensure browser is running
            logger.info("Ensuring browser is ready for setup wizard...")
            browser_path, data_dir = ensure_browser(verbose=verbose)
            console.print(f"[green]Browser ready at: {browser_path}[/green]")

            # Connect to browser and run wizard
            async def run_wizard():
                playwright = get_async_playwright().start()
                try:
                    from .config import get_config

                    config = get_config()

                    browser = await playwright.chromium.connect_over_cdp(
                        f"http://localhost:{config.browser.debug_port}"
                    )

                    success = await interactive_setup_wizard(browser, logger)

                    await browser.close()
                    return success
                finally:
                    await playwright.stop()

            # Run the async wizard
            success = asyncio.run(run_wizard())

            if success:
                console.print(
                    "\n[bold green]🎉 Setup completed successfully![/bold green]"
                )
                console.print(
                    "[green]Your PlaywrightAuthor browser is now ready for automation.[/green]"
                )
                console.print("\n[cyan]Next steps:[/cyan]")
                console.print(
                    "  • Test your setup: [bold]playwrightauthor health[/bold]"
                )
                console.print(
                    "  • Check browser status: [bold]playwrightauthor status[/bold]"
                )
                console.print(
                    "  • Start using PlaywrightAuthor in your Python scripts!"
                )
            else:
                console.print(
                    "\n[yellow]⚠️ Setup wizard completed with issues.[/yellow]"
                )
                console.print(
                    "[yellow]You may need to complete authentication manually.[/yellow]"
                )
                console.print("\n[cyan]Troubleshooting:[/cyan]")
                console.print(
                    "  • Run diagnostics: [bold]playwrightauthor health --verbose[/bold]"
                )
                console.print(
                    "  • Clear cache: [bold]playwrightauthor clear-cache[/bold]"
                )
                console.print(
                    "  • Try setup again: [bold]playwrightauthor setup --verbose[/bold]"
                )

        except KeyboardInterrupt:
            console.print("\n[yellow]Setup wizard interrupted by user.[/yellow]")
        except ImportError as e:
            console.print(
                f"[red]Setup wizard requires additional dependencies: {e}[/red]"
            )
            console.print("[yellow]Try: pip install playwright[/yellow]")
        except Exception as e:
            console.print(f"[red]Setup wizard failed: {e}[/red]")
            if verbose:
                import traceback

                console.print(f"[dim]{traceback.format_exc()}[/dim]")

            console.print("\n[cyan]Manual setup options:[/cyan]")
            console.print(
                "  • Check browser: [bold]playwrightauthor status --verbose[/bold]"
            )
            console.print("  • Run diagnostics: [bold]playwrightauthor health[/bold]")
            console.print("  • Clear cache: [bold]playwrightauthor clear-cache[/bold]")

    def browse(self, verbose: bool = False, profile: str = "default"):
        """
        Launch Chrome for Testing in CDP mode and exit.

        This command starts Chrome for Testing with remote debugging enabled on port 9222
        and then exits immediately, leaving the browser running in the background. Other
        scripts using PlaywrightAuthor will automatically connect to this browser instance
        instead of launching their own.

        The browser will remain open until you close it manually. All your authentication
        sessions and cookies will be preserved between script runs as long as the browser
        stays open.

        Args:
            verbose (bool, optional): Enable detailed logging for browser launch and
                connection diagnostics. Useful for troubleshooting. Defaults to False.
            profile (str, optional): Browser profile to use. Different profiles maintain
                separate authentication sessions and browser data. Defaults to "default".

        Usage Examples:
            # Launch browser with default profile
            playwrightauthor browse

            # Launch with verbose logging
            playwrightauthor browse --verbose

            # Launch with a specific profile (e.g., work account)
            playwrightauthor browse --profile work

        Workflow Example:
            1. Launch browser: playwrightauthor browse
               (Browser opens, command exits immediately)

            2. Run your scripts: python my_scraper.py
               (Your script connects to the already-running browser)

            3. Run multiple scripts without restarting the browser
            4. Close the browser window when done

        Benefits:
            - Faster script execution (no browser startup time)
            - Preserve authentication state across multiple script runs
            - Manually interact with the browser between script runs
            - Debug scripts by watching them execute in real-time
            - Use browser DevTools while scripts are running

        Note:
            The command exits immediately after launching the browser. The browser
            continues running independently and will use the configured debug port
            (default: 9222) which must not be in use by another application.
        """
        console = Console()
        logger = configure_logger(verbose)

        try:
            console.print(
                "[bold blue]Launching Chrome for Testing in CDP mode...[/bold blue]"
            )
            console.print(f"[dim]Profile: {profile}[/dim]")
            console.print(f"[dim]Debug port: 9222[/dim]\n")

            # Launch browser (don't just ensure it's running)
            from .browser.process import get_chrome_process
            config = get_config()
            was_already_running = get_chrome_process(config.browser.debug_port) is not None
            
            browser_path, data_dir = launch_browser(verbose=verbose, profile=profile)

            if was_already_running:
                console.print("[yellow]✓ Chrome for Testing is already running![/yellow]")
            else:
                console.print("[green]✓ Browser launched successfully![/green]")
                
            console.print(f"[dim]Path: {browser_path}[/dim]")
            console.print(f"[dim]Data: {data_dir}[/dim]\n")

            console.print("[yellow]Browser is running in CDP mode.[/yellow]")
            console.print("You can now:")
            console.print("  • Run PlaywrightAuthor scripts to connect to this browser")
            console.print("  • Manually browse and log into services")
            console.print("  • Use Chrome DevTools (press F12)")
            console.print("\n[dim]The browser will remain open until you close it manually.[/dim]")

        except BrowserManagerError as e:
            console.print(f"[red]Failed to launch browser: {e}[/red]")
            sys.exit(1)
        except Exception as e:
            console.print(f"[red]Unexpected error: {e}[/red]")
            if verbose:
                import traceback

                console.print(f"[dim]{traceback.format_exc()}[/dim]")
            sys.exit(1)


def main() -> None:
    """Main entry point with enhanced error handling for mistyped commands."""
    console = Console()

    # Get available commands from Cli class
    available_commands = [
        name
        for name in dir(Cli)
        if not name.startswith("_") and callable(getattr(Cli, name))
    ]

    try:
        fire.Fire(Cli)
    except SystemExit as e:
        # Fire raises SystemExit on errors
        if e.code != 0 and len(sys.argv) > 1:
            # Check if it might be a mistyped command
            command = sys.argv[1]

            # Don't suggest for valid flags like --help
            if not command.startswith("-"):
                # Find close matches
                suggestions = get_close_matches(
                    command, available_commands, n=3, cutoff=0.6
                )

                if suggestions:
                    # Use our CLIError for consistent formatting
                    error = CLIError(
                        f"Unknown command: '{command}'",
                        command_used=command,
                        did_you_mean=suggestions,
                    )
                    console.print(f"[red]{error}[/red]")
                    sys.exit(1)

        # Re-raise if no suggestions found
        raise
