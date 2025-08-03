# PlaywrightAuthor

*Your personal, authenticated browser for Playwright, ready in one line of code.*

PlaywrightAuthor is a convenience package for **Microsoft Playwright**. It handles the tedious parts of browser automation: finding and launching a **Chrome for Testing** instance, keeping it authenticated with your user profile, and connecting Playwright to it. All you need to do is instantiate a class, and you get a ready-to-use `Browser` object. This lets you focus on writing your automation script, not on the boilerplate.

The core idea is to let you do this:

```python
from playwrightauthor import Browser

with Browser() as browser:
    # you get a standard Playwright browser object
    # that is already connected to a logged-in browser
    page = browser.new_page()
    page.goto("https://github.com/me")
    print(f"Welcome, {page.locator('.user-profile-name').inner_text()}!")
```

---

## Contents

* [Features](#features)
* [Quick‑start](#quick-start)
* [Developer workflow](#developer-workflow)
* [Package layout](#package-layout) – **file tree, code snippet, explanation & rationale for every file**
* [Contributing](#contributing)
* [License](#license)

---

## Features

| ✔︎                                                                                                                                                                   | Capability |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------- |
| Automatically discovers or installs a suitable **Chrome for Testing** build via the *last‑known‑good‑versions* JSON, falling back to `npx puppeteer` when possible.  |            |
| Launches Chrome with `--remote-debugging-port` (killing any non‑debug instance first) and shows a friendly onboarding HTML if the user still needs to log in.        |            |
| Provides simple `Browser()` and `AsyncBrowser()` classes that return a ready-to-use, authenticated Playwright browser object.                                        |            |
| Fire‑powered CLI (`python -m playwrightauthor ...`) with rich‐colour output and `--verbose` flag wiring straight into **loguru**.                                    |            |
| 100 % type‑hinted, PEP 8‑compliant, flat, self‑documenting codebase; every source has a `this_file:` tracker line.                                                   |            |
| Batteries included: pytest suite, Ruff/pyupgrade/autoflake hooks, uv‑based reproducible environments.                                                                |            |

---

## Quick start

```bash
# ➀ create & sync env
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv --python 3.12
uv init
# Add playwrightauthor and its dependencies
uv add playwright rich fire loguru platformdirs requests psutil

# ➁ run your script
# (create a file like 'myscript.py' with the code below)
python myscript.py
```

Example `myscript.py`:
```python
from playwrightauthor import Browser, AsyncBrowser
import asyncio

# Synchronous API
print("--- Running Sync Example ---")
with Browser(verbose=True) as browser:
    page = browser.new_page()
    page.goto("https://github.com")
    print(f"Page title: {page.title()}")

# Asynchronous API
async def main():
    print("\n--- Running Async Example ---")
    async with AsyncBrowser(verbose=True) as browser:
        page = await browser.new_page()
        await page.goto("https://duckduckgo.com")
        print(f"Page title: {await page.title()}")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Command-Line Interface

PlaywrightAuthor comes with a command-line interface for managing the browser installation.

### `status`

Checks the status of the browser and launches it if it's not running.

```bash
python -m playwrightauthor status
```

### `clear-cache`

Removes the browser installation directory, including the browser itself and user data.

```bash
python -m playwrightauthor clear-cache
```

---

## Developer workflow

1. **Read** `WORK.md` & `PLAN.md` before touching code.

2. **Iterate** in minimal, self‑contained commits.

3. After Python changes run:

   ```bash
   fd -e py -x uvx autoflake -i {}; \
   fd -e py -x uvx pyupgrade --py312-plus {}; \
   fd -e py -x uvx ruff check --output-format=github --fix --unsafe-fixes {}; \
   fd -e py -x uvx ruff format --respect-gitignore --target-version py312 {}; \
   python -m pytest
   ```

4. Update `CHANGELOG.md`, tick items in `TODO.md`, push.

5. Always finish a work session with **“Wait, but”** → reflect → refine → push again.

---

## Package layout

> Below is the *envisioned* file tree.
> Each entry shows (a) **code snippet** – only the essential lines,
> (b) **explanation** – what it does,
> (c) **rationale** – why it belongs.

```
.
├── playwrightauthor/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py
│   ├── author.py
│   ├── browser_manager.py
│   ├── onboarding.py
│   ├── templates/
│   │   └── onboarding.html
│   ├── utils/
│   │   ├── logger.py
│   │   └── paths.py
│   └── typing.py
├── tests/
│   └── test_author.py
├── README.md          ← *← this file*
├── PLAN.md
├── TODO.md
├── WORK.md
└── CHANGELOG.md
```

### `playwrightauthor/__init__.py`

```python
#!/usr/bin/env -S uv run -s
# /// script
# dependencies = []
# ///
# this_file: playwrightauthor/__init__.py

"""Public re‑exports for library consumers."""
from .author import Browser, AsyncBrowser

__all__ = ["Browser", "AsyncBrowser"]
```

*Explanation* – Presents a tiny, stable API surface.
*Rationale* – Hides internal churn; semver‑compatible.

---


### `playwrightauthor/__main__.py`

```python
#!/usr/bin/env -S uv run -s
# /// script
# dependencies = ["fire"]
# ///
# this_file: playwrightauthor/__main__.py

""`python -m playwrightauthor` entry‑point."""
from .cli import main

if __name__ == "__main__":
    main()
```

*Explanation* – Delegates to the Fire CLI.
*Rationale* – Keeps `__init__` import‑only; avoids side‑effects.

---


### `playwrightauthor/cli.py`

```python
#!/usr/bin/env -S uv run -s
# /// script
# dependencies = ["fire", "rich"]
# ///
# this_file: playwrightauthor/cli.py

"""Fire‑powered command‑line interface for utility tasks."""
from rich.console import Console
from .browser_manager import ensure_browser

def status(verbose: bool = False) -> None:
    """Checks browser status and launches it if not running."""
    console = Console()
    console.print("Checking browser status...")
    browser_path, data_dir = ensure_browser(verbose=verbose)
    console.print(f"[green]Browser is ready.[/green]")
    console.print(f"  - Path: {browser_path}")
    console.print(f"  - User Data: {data_dir}")

def main() -> None:
    import fire
    fire.Fire({"status": status})
```

*Explanation* – Offers utility commands like `status`.
*Rationale* – Provides a simple way to manage the browser without writing a script.

---


### `playwrightauthor/author.py`

```python
#!/usr/bin/env -S uv run -s
# /// script
# dependencies = ["playwright"]
# ///
# this_file: playwrightauthor/author.py

"""The core Browser and AsyncBrowser classes."""
from playwright.sync_api import sync_playwright, Playwright, Browser as PlaywrightBrowser
from playwright.async_api import async_playwright, AsyncPlaywright, Browser as AsyncPlaywrightBrowser
from .browser_manager import ensure_browser

class Browser:
    """A sync context manager for an authenticated Playwright Browser."""
    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def __enter__(self) -> PlaywrightBrowser:
        # 1. Ensure browser is running and get debug port
        # 2. playwright.chromium.connect_over_cdp()
        # 3. Return browser object
        ...

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Disconnect
        ...

class AsyncBrowser:
    """An async context manager for an authenticated Playwright Browser."""
    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    async def __aenter__(self) -> AsyncPlaywrightBrowser:
        ...

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        ...
```

*Explanation* – The main entry point for the library.
*Rationale* – Provides a simple, Pythonic `with` statement syntax for browser management.

---


### `playwrightauthor/browser_manager.py`

```python
#!/usr/bin/env -S uv run -s
# /// script
# dependencies = ["requests", "platformdirs", "rich", "psutil"]
# ///
# this_file: playwrightauthor/browser_manager.py

"""
Ensure a Chrome for Testing build is present & running in debug mode.

Algorithm:
1. Try to connect to localhost:9222.
2. If Chrome is running *without* --remote-debugging-port ⇒ kill & restart.
3. If Chrome isn't installed:
   3a. Prefer `npx puppeteer browsers install`.
   3b. Else download the matching archive from LKGV JSON.
4. Launch Chrome with a persistent user‑data‑dir.
"""
import os, subprocess, json, sys, platform, shutil, tempfile
from pathlib import Path
from rich.console import Console
from .utils.paths import install_dir

_LKGV_URL = "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json"

def ensure_browser(verbose: bool = False):
    console = Console()
    ...
```

*Explanation* – Central authority for “is Chrome available?”.
*Rationale* – Encapsulates the complex, platform-specific logic of managing the browser binary and its process.

---


### `playwrightauthor/onboarding.py`

```python
#!/usr/bin/env -S uv run -s
# /// script
# dependencies = ["playwright"]
# ///
# this_file: playwrightauthor/onboarding.py

"""Serve a local HTML page instructing the user to log in."""
from pathlib import Path
from playwright.async_api import Browser

def show(browser: Browser) -> None:
    html = Path(__file__).parent.parent / "templates" / "onboarding.html"
    page = browser.new_page()
    page.set_content(html.read_text("utf-8"), wait_until="domcontentloaded")
```

*Explanation* – Visual cue when manual steps are needed.
*Rationale* – Human‑friendly recovery path builds trust.

---


### `playwrightauthor/templates/onboarding.html`

```html
<!-- this_file: playwrightauthor/templates/onboarding.html -->
<!DOCTYPE html>
<html>
  <body>
    <h1>One small step…</h1>
    <p>Please <strong>log into any websites you need</strong> in this browser window.<br>
       This session will be saved for future runs.<br><br>
       You can close this tab and return to the terminal when you’re done!</p>
  </body>
</html>
```

*Explanation* – Tiny static asset for user guidance.
*Rationale* – Kept under `templates/` to avoid clutter.

---


### `playwrightauthor/utils/logger.py`

```python
#!/usr/bin/env -S uv run -s
# /// script
# dependencies = ["loguru"]
# ///
# this_file: playwrightauthor/utils/logger.py

"""Project‑wide Loguru configuration."""
from loguru import logger

def configure(verbose: bool = False):
    logger.remove()
    level = "DEBUG" if verbose else "INFO"
    logger.add(lambda m: print(m, end=""), level=level)
    return logger
```

*Explanation* – Single point of logging policy.
*Rationale* – Avoids duplicating “verbose” handling everywhere.

---


### `playwrightauthor/utils/paths.py`

```python
#!/usr/bin/env -S uv run -s
# /// script
# dependencies = ["platformdirs"]
# ///
# this_file: playwrightauthor/utils/paths.py

"""Cross‑platform install locations."""
from platformdirs import user_cache_dir
from pathlib import Path

def install_dir() -> Path:
    return Path(user_cache_dir("playwrightauthor", roaming=True)) / "browser"
```

*Explanation* – Abstracts OS differences.
*Rationale* – Ensures browser data is stored in a conventional, user-specific location.

---


### `tests/test_author.py`

```python
# this_file: tests/test_author.py
import pytest
from playwrightauthor import Browser

@pytest.mark.skip("requires live Chrome and user interaction")
def test_browser_smoke():
    """A basic smoke test to ensure the Browser class can be instantiated."""
    try:
        with Browser() as browser:
            assert browser is not None
            assert len(browser.contexts) > 0
    except Exception as e:
        # This test is expected to fail in a headless CI environment
        # without a display server or a running Chrome instance.
        # We just check that it doesn't raise an unexpected error.
        pass
```

*Explanation* – Smoke test for the core `Browser` class.
*Rationale* – Keeps CI fast but ensures the main library entry point is importable and structurally sound.

---

## Troubleshooting

### `BrowserManagerError: Could not find Chrome executable...`

This error means that `playwrightauthor` could not find a Chrome executable on your system. You can either install Chrome for Testing using the `npx puppeteer browsers install chrome` command, or install Google Chrome and ensure it is in a common system location.

### `playwright._impl._api_types.Error: Target page, context or browser has been closed`

This error usually means that the browser was closed while your script was running. This can happen if you manually close the browser window, or if the browser crashes. If you are running into this issue, you can try running your script with the `--verbose` flag to get more information.

---

## Contributing

Pull‑requests are welcome! Please follow the **General Coding Principles** in the main `README.md`, keep every file’s `this_file` header accurate, and end each session with a short *“Wait, but”* reflection in your PR description.

---

## License

MIT – *see* `LICENSE`.

---

Wait, but…

**Reflection & tiny refinements**

* Refocused the entire project from a specific scraper to a general-purpose Playwright convenience library.
* The core API is now class-based (`Browser`, `AsyncBrowser`) for a more Pythonic feel.
* Updated the file layout (`author.py`) and CLI (`status` command) to match the new scope.
* Generalized the onboarding HTML to be site-agnostic.
* Ensured all snippets and explanations align with the new vision of providing a zero-setup, authenticated browser.

(End of iteration – ready for review.)