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

### ✨ **Zero-Configuration Browser Automation**
- **Automatic Chrome Management**: Discovers, installs, and launches Chrome for Testing with remote debugging enabled
- **Persistent Authentication**: Maintains user sessions across script runs using persistent browser profiles
- **Cross-Platform Support**: Works seamlessly on Windows, macOS, and Linux with optimized Chrome discovery

### 🚀 **Performance & Reliability**
- **Lazy Loading**: Optimized startup time with on-demand module imports
- **Connection Health Monitoring**: Comprehensive diagnostics and automatic retry logic
- **State Management**: Intelligent caching of browser paths and configuration for faster subsequent runs
- **Error Recovery**: Graceful handling of browser crashes with automatic restart capabilities

### 🛠 **Developer Experience**
- **Simple API**: Clean `Browser()` and `AsyncBrowser()` context managers
- **Rich CLI Interface**: Comprehensive command-line tools for browser and profile management
- **Type Safety**: 100% type-hinted codebase with full mypy compatibility
- **Comprehensive Testing**: Extensive test suite with CI/CD pipeline on multiple platforms

### 📋 **Advanced Management**
- **Profile System**: Create, manage, and switch between multiple browser profiles
- **Configuration Management**: Environment variable support and flexible configuration options
- **Diagnostic Tools**: Built-in troubleshooting and system health checks
- **JSON Output**: Machine-readable output formats for automation and scripting

---

## Installation

```bash
# Install PlaywrightAuthor
pip install playwrightauthor

# Install Playwright browsers (required)
playwright install chromium
```

## Quick start

```bash
# Create your script file
cat > example.py << 'EOF'
from playwrightauthor import Browser

with Browser() as browser:
    page = browser.new_page()
    page.goto("https://github.com")
    print(f"Page title: {page.title()}")
EOF

# Run your script
python example.py
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

PlaywrightAuthor comes with a comprehensive command-line interface for managing browsers, profiles, and diagnostics.

### Browser Management

```bash
# Check browser status and launch if needed
python -m playwrightauthor status

# Clear browser cache and user data
python -m playwrightauthor clear-cache

# Run comprehensive diagnostics
python -m playwrightauthor diagnose
```

### Profile Management

```bash
# List all browser profiles
python -m playwrightauthor profile list

# Create a new profile
python -m playwrightauthor profile create myprofile

# Show profile details
python -m playwrightauthor profile show myprofile

# Delete a profile
python -m playwrightauthor profile delete myprofile

# Clear all profiles
python -m playwrightauthor profile clear
```

### Configuration

```bash
# Show current configuration
python -m playwrightauthor config show

# Show version and system information
python -m playwrightauthor version
```

All commands support `--json` output format and `--verbose` for detailed logging.

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

## Package Architecture

PlaywrightAuthor follows modern Python packaging standards with a clean `src/` layout and comprehensive testing.

```
src/playwrightauthor/
├── __init__.py              # Public API exports (Browser, AsyncBrowser)
├── __main__.py              # CLI entry point
├── author.py                # Core Browser context managers
├── browser_manager.py       # Legacy browser management (compatibility)
├── cli.py                   # Fire-powered CLI with rich output
├── config.py                # Configuration management system
├── connection.py            # Connection health and diagnostics
├── exceptions.py            # Custom exception classes
├── lazy_imports.py          # Performance optimization for imports
├── onboarding.py            # User authentication guidance
├── state_manager.py         # Persistent state management
├── typing.py                # Type definitions and protocols
├── browser/                 # Modular browser management
│   ├── __init__.py
│   ├── finder.py            # Cross-platform Chrome discovery
│   ├── installer.py         # Chrome for Testing installation
│   ├── launcher.py          # Browser process launching
│   └── process.py           # Process management and control
├── templates/
│   └── onboarding.html      # User guidance interface
└── utils/
    ├── logger.py            # Loguru-based logging configuration
    └── paths.py             # Cross-platform path management

tests/                       # Comprehensive test suite
├── test_author.py           # Core functionality tests
├── test_benchmark.py        # Performance benchmarks
├── test_integration.py      # Integration tests
├── test_platform_specific.py # Platform-specific tests
└── test_utils.py            # Utility function tests
```

## Key Components

### Core API
The library exposes a minimal, clean API through two main classes:
- `Browser()` - Synchronous context manager
- `AsyncBrowser()` - Asynchronous context manager

Both provide identical functionality and return standard Playwright browser objects.

### Browser Management
- **Automatic Discovery**: Finds Chrome installations across Windows, macOS, and Linux
- **Smart Installation**: Downloads Chrome for Testing when needed using official Google endpoints
- **Process Management**: Handles Chrome launching with debug port and graceful cleanup
- **Profile Persistence**: Maintains user authentication across sessions

### Configuration System
- **Environment Variables**: `PLAYWRIGHTAUTHOR_*` prefix for all settings
- **State Management**: Caches browser paths and configuration for performance
- **Profile Support**: Multiple named profiles for different use cases

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