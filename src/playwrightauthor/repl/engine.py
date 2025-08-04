#!/usr/bin/env -S uv run -s
# /// script
# dependencies = ["prompt_toolkit", "rich", "playwright"]
# ///
# this_file: src/playwrightauthor/repl/engine.py

"""Core REPL engine for PlaywrightAuthor interactive mode."""

import ast
from typing import Any

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.styles import Style
from pygments.lexers import PythonLexer
from rich.console import Console
from rich.pretty import Pretty
from rich.syntax import Syntax
from rich.traceback import Traceback

from ..author import AsyncBrowser, Browser
from ..utils.logger import configure as configure_logger
from ..utils.paths import config_dir
from .completion import PlaywrightCompleter


class ReplEngine:
    """Interactive REPL engine for PlaywrightAuthor."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.console = Console()
        self.logger = configure_logger(verbose)

        # Initialize REPL state
        self.globals: dict[str, Any] = {
            "__name__": "__main__",
            "__doc__": None,
            "Browser": Browser,
            "AsyncBrowser": AsyncBrowser,
        }
        self.locals: dict[str, Any] = {}
        self.browser: Any | None = None

        # Setup prompt session
        history_file = config_dir() / "repl_history.txt"
        history_file.parent.mkdir(parents=True, exist_ok=True)

        self.session = PromptSession(
            lexer=PygmentsLexer(PythonLexer),
            completer=PlaywrightCompleter(),
            history=FileHistory(str(history_file)),
            style=Style.from_dict(
                {
                    "prompt": "#00aa00 bold",
                    "continuation": "#666666",
                }
            ),
            multiline=True,
            prompt_continuation="... ",
        )

    def print_banner(self):
        """Print the REPL welcome banner."""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                    PlaywrightAuthor REPL                     ║
║              Interactive Browser Automation                   ║
╠══════════════════════════════════════════════════════════════╣
║  Commands:                                                   ║
║    browser = Browser()   # Create a browser instance         ║
║    !status               # Run CLI commands (prefix with !) ║
║    help()                # Python help                       ║
║    exit() or Ctrl+D      # Exit REPL                        ║
╚══════════════════════════════════════════════════════════════╝
        """
        self.console.print(banner, style="cyan")

    def print_help(self):
        """Print REPL-specific help."""
        help_text = """
Available objects and functions:
  Browser, AsyncBrowser  - Browser context managers
  browser                - Current browser instance (if created)

Special commands:
  !<command>             - Execute PlaywrightAuthor CLI commands
  exit() or Ctrl+D       - Exit the REPL
  help()                 - Show this help

Example usage:
  >>> browser = Browser()
  >>> browser.__enter__()  # Start browser
  >>> page = browser.new_page()
  >>> page.goto("https://github.com")
  >>> page.title()
  'GitHub'
        """
        self.console.print(help_text, style="yellow")

    def execute_cli_command(self, command: str) -> None:
        """Execute a CLI command from within the REPL."""
        try:
            # Import CLI here to avoid circular imports
            from ..cli import Cli

            cli = Cli()

            # Parse command and arguments
            parts = command.strip().split()
            if not parts:
                return

            cmd_name = parts[0]
            args = parts[1:] if len(parts) > 1 else []

            # Execute the command
            if hasattr(cli, cmd_name):
                method = getattr(cli, cmd_name)
                try:
                    if args:
                        # Try to call with arguments
                        method(*args)
                    else:
                        method()
                except TypeError as e:
                    self.console.print(f"[red]Command error: {e}[/red]")
                    self.console.print(f"[yellow]Usage: !{cmd_name} [args][/yellow]")
            else:
                self.console.print(f"[red]Unknown command: {cmd_name}[/red]")
                self.console.print(
                    "[yellow]Available commands: status, clear_cache, profile, config, diagnose, version[/yellow]"
                )

        except Exception as e:
            self.console.print(f"[red]CLI command failed: {e}[/red]")

    def execute_code(self, code: str) -> Any:
        """Execute Python code and return the result."""
        try:
            # Try to parse as expression first
            try:
                node = ast.parse(code, mode="eval")
                result = eval(
                    compile(node, "<repl>", "eval"), self.globals, self.locals
                )
                return result
            except SyntaxError:
                # If not an expression, execute as statement
                exec(compile(code, "<repl>", "exec"), self.globals, self.locals)
                return None

        except SystemExit:
            raise
        except KeyboardInterrupt:
            raise
        except Exception as e:
            # Pretty print the traceback
            traceback_obj = Traceback.from_exception(
                type(e), e, e.__traceback__, show_locals=self.verbose
            )
            self.console.print(traceback_obj)
            return None

    def format_result(self, result: Any) -> None:
        """Format and display the result."""
        if result is not None:
            if isinstance(result, str) and len(result) > 200:
                # For long strings, show with syntax highlighting
                syntax = Syntax(result, "text", theme="monokai", line_numbers=False)
                self.console.print(syntax)
            else:
                # Use Rich's pretty printing
                self.console.print(Pretty(result))

    def run(self) -> None:
        """Run the interactive REPL loop."""
        self.print_banner()

        try:
            while True:
                try:
                    # Get input from user
                    code = self.session.prompt(">>> ")

                    # Skip empty input
                    if not code.strip():
                        continue

                    # Handle special commands
                    if code.strip() == "help()":
                        self.print_help()
                        continue
                    elif code.strip() in ("exit()", "quit()"):
                        break
                    elif code.strip().startswith("!"):
                        # CLI command
                        cli_command = code.strip()[1:]  # Remove '!' prefix
                        self.execute_cli_command(cli_command)
                        continue

                    # Execute Python code
                    result = self.execute_code(code)
                    self.format_result(result)

                except KeyboardInterrupt:
                    self.console.print("\n[yellow]KeyboardInterrupt[/yellow]")
                    continue
                except EOFError:
                    break

        except Exception as e:
            self.console.print(f"[red]REPL error: {e}[/red]")
        finally:
            self.console.print("\n[cyan]Goodbye![/cyan]")

            # Cleanup browser if it exists
            if self.browser and hasattr(self.browser, "__exit__"):
                try:
                    self.browser.__exit__(None, None, None)
                except Exception as e:
                    self.logger.debug(f"Error cleaning up browser: {e}")
