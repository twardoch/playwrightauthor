#!/usr/bin/env -S uv run -s
# /// script
# dependencies = ["prompt_toolkit"]
# ///
# this_file: src/playwrightauthor/repl/completion.py

"""Advanced tab completion for PlaywrightAuthor REPL."""

from prompt_toolkit.completion import Completer, Completion


class PlaywrightCompleter(Completer):
    """Advanced completer for PlaywrightAuthor REPL with contextual awareness."""

    def __init__(self):
        self.browser_methods = [
            "new_page",
            "new_context",
            "close",
            "contexts",
            "version",
            "browser_type",
            "is_connected",
        ]

        self.page_methods = [
            "goto",
            "click",
            "fill",
            "type",
            "press",
            "wait_for_selector",
            "locator",
            "get_by_text",
            "get_by_role",
            "get_by_label",
            "screenshot",
            "title",
            "url",
            "content",
            "inner_text",
            "query_selector",
            "query_selector_all",
            "evaluate",
            "wait_for_timeout",
            "wait_for_load_state",
            "reload",
            "go_back",
            "go_forward",
            "close",
            "set_viewport_size",
            "emulate_media",
        ]

        self.locator_methods = [
            "click",
            "fill",
            "type",
            "press",
            "hover",
            "focus",
            "blur",
            "check",
            "uncheck",
            "select_option",
            "text_content",
            "inner_text",
            "inner_html",
            "get_attribute",
            "is_visible",
            "is_enabled",
            "is_checked",
            "is_disabled",
            "count",
            "first",
            "last",
            "nth",
            "and_",
            "or_",
            "filter",
        ]

        self.cli_commands = [
            "status",
            "clear_cache",
            "profile",
            "config",
            "diagnose",
            "version",
        ]

        self.python_keywords = [
            "def",
            "class",
            "if",
            "elif",
            "else",
            "try",
            "except",
            "finally",
            "for",
            "while",
            "with",
            "as",
            "import",
            "from",
            "return",
            "yield",
            "break",
            "continue",
            "pass",
            "async",
            "await",
            "True",
            "False",
            "None",
            "and",
            "or",
            "not",
            "in",
            "is",
            "lambda",
        ]

    def get_completions(self, document, complete_event):
        """Generate completions based on current context."""
        word = document.get_word_before_cursor()
        text = document.text_before_cursor

        # CLI commands (prefixed with !)
        if text.strip().startswith("!"):
            text.strip()[1:]  # Remove '!' prefix
            for command in self.cli_commands:
                if command.startswith(word):
                    yield Completion(command, start_position=-len(word))

        # Browser object methods
        elif "browser." in text and not any(x in text for x in ["page.", "locator."]):
            for method in self.browser_methods:
                if method.startswith(word):
                    yield Completion(
                        method, start_position=-len(word), display_meta="Browser method"
                    )

        # Page object methods
        elif "page." in text and "locator." not in text:
            for method in self.page_methods:
                if method.startswith(word):
                    yield Completion(
                        method, start_position=-len(word), display_meta="Page method"
                    )

        # Locator object methods
        elif "locator." in text or any(
            selector in text for selector in [".get_by_", ".locator("]
        ):
            for method in self.locator_methods:
                if method.startswith(word):
                    yield Completion(
                        method, start_position=-len(word), display_meta="Locator method"
                    )

        # Python keywords and built-ins
        else:
            for keyword in self.python_keywords:
                if keyword.startswith(word):
                    yield Completion(
                        keyword,
                        start_position=-len(word),
                        display_meta="Python keyword",
                    )

            # Common Python built-ins
            builtins = [
                "print",
                "len",
                "str",
                "int",
                "float",
                "list",
                "dict",
                "set",
                "tuple",
            ]
            for builtin in builtins:
                if builtin.startswith(word):
                    yield Completion(
                        builtin,
                        start_position=-len(word),
                        display_meta="Built-in function",
                    )
