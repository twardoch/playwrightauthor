---
layout: default
title: Selectable Browser Engines
nav_order: 2
---

# Selectable Browser Engines
<!-- this_file: docs/01-browser-engines.md -->

PlaywrightAuthor supports multiple browser engines, allowing you to switch between standard automated browsers and enhanced stealth/anti-detect environments with a single configuration.

## Supported Engines

1. **Chrome for Testing (`chrome`)** - *Default*
   - Official Google distribution designed specifically for browser automation.
   - Bypasses CDP automation restrictions found in regular Chrome.
   - Recommended for general scraping, automated testing, and standard workflows.
2. **CloakBrowser (`cloak`)**
   - Stealth-optimized Chromium client designed to bypass advanced anti-bot fingerprinting and protection systems (like Cloudflare, Akamai, etc.).
   - Lazily imported to ensure zero overhead if not used.

---

## Configuration

You can select the active browser engine via two methods:

### 1. In Code (Configuration)
Set the `engine` parameter in `BrowserConfig` or when initializing `Browser` / `AsyncBrowser`:

```python
from playwrightauthor import Browser, BrowserConfig

# Method A: Direct initialization
with Browser(engine="cloak") as browser:
    page = browser.new_page()
    page.goto("https://bot.sannysoft.com")

# Method B: Via BrowserConfig
config = BrowserConfig(engine="cloak", headless=False)
with Browser(config=config) as browser:
    # ...
```

### 2. Environment Variables
You can override the engine globally using the `PLAYWRIGHTAUTHOR_ENGINE` environment variable:

```bash
export PLAYWRIGHTAUTHOR_ENGINE=cloak
python my_script.py  # Will use CloakBrowser automatically
```

---

## CLI Integration

All CLI commands support selecting the browser engine via the `--engine` option:

```bash
# Launch CloakBrowser interactively
playwrightauthor browse --engine cloak

# Check the current status of the CloakBrowser process and profile
playwrightauthor status

# Run diagnostics with CloakBrowser
playwrightauthor diagnose
```

---

## Deep Dive: Architecture & Implementation

### 1. Process Management (`process.py`)
Standard process matching for Chrome for Testing has been enhanced to detect `chromium`/`cloakbrowser` processes on macOS and Linux/Unix. This ensures that:
- PlaywrightAuthor can locate already-running CloakBrowser sessions.
- Process status and PID checks work seamlessly.

### 2. Process Launcher (`launcher.py`)
The process launcher has been refactored to:
- Bypass strict Chrome for Testing string checks when launching CloakBrowser executable paths.
- Support appending custom command-line arguments (`extra_args`) to the launcher.

### 3. Lazy Imports (`engine.py` and `cloak.py`)
To prevent packaging issues or import crashes on environments where the private `CloakBrowser` library is not installed:
- The `cloakbrowser` module is loaded dynamically at runtime only when `engine="cloak"` is requested.
- It resolves the project path dynamically and checks the `./private/CloakBrowser/` directory.

### 4. Engine Adapters (`engine.py`)
PlaywrightAuthor implements a polymorphic adapter registry using `EngineAdapter` and `AsyncEngineAdapter` protocols.
- **`ChromeEngineAdapter`**: Handles downloading, launching, and connecting to Chrome for Testing.
- **`CloakEngineAdapter`**: Handles launching and connecting to CloakBrowser.
