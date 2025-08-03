#!/usr/bin/env -S uv run -s
# /// script
# dependencies = ["fire", "rich"]
# ///
# this_file: playwrightauthor/cli.py

"""Fire-powered command-line interface for utility tasks."""

import fire
from rich.console import Console
import shutil
from .browser_manager import ensure_browser
from .exceptions import BrowserManagerError
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


def main() -> None:
    fire.Fire(Cli)
