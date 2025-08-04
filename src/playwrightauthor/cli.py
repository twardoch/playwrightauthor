#!/usr/bin/env -S uv run -s
# /// script
# dependencies = ["fire", "rich"]
# ///
# this_file: src/playwrightauthor/cli.py

"""Fire-powered command-line interface for utility tasks."""

import json
import shutil

import fire
from rich.console import Console
from rich.table import Table

from .browser_manager import ensure_browser
from .config import get_config
from .connection import check_connection_health
from .exceptions import BrowserManagerError
from .state_manager import get_state_manager
from .utils.logger import configure as configure_logger
from .utils.paths import install_dir


class Cli:
    """CLI for PlaywrightAuthor."""

    def status(self, verbose: bool = False):
        """Checks browser status and launches it if not running."""
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
        Removes the browser installation directory, including the browser itself and user data.
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
        Manage browser profiles.

        Args:
            action: Action to perform (list, show, create, delete, clear).
            name: Profile name for show/create/delete actions.
            format: Output format (table, json).
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
            ```bash
            playwrightauthor repl --verbose

            # Inside REPL:
            >>> browser = Browser()
            >>> browser.__enter__()  # Start browser
            >>> page = browser.new_page()
            >>> page.goto("https://github.com")
            >>> !status  # Run CLI command
            ```

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


def main() -> None:
    fire.Fire(Cli)
