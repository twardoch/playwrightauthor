# Dependencies
<!-- this_file: DEPENDENCIES.md -->

This file documents the dependencies used in `playwrightauthor` and the rationale for choosing them.

## Core Runtime Dependencies

- **filelock >=3.20**
  - **Purpose:** Exclusive per-profile leases and serialized legacy launch checks.
  - **Rationale:** Uses native OS locking on macOS/Unix/Windows, released on process
    death; avoids custom stale-PID or marker-file recovery. The new session API
    holds the lease until browser cleanup completes, including cancellation.

- **playwright**
  - **Purpose:** Core browser automation protocol. Used to control Chromium/Chrome for Testing and browser contexts.
  - **Rationale:** Standard, highly reliable modern browser automation library backed by Microsoft.

- **rich**
  - **Purpose:** Beautiful terminal formatting, tables, console status, and progress bars.
  - **Rationale:** De facto standard library for building attractive, responsive terminal UIs in Python.

- **fire**
  - **Purpose:** Automatic CLI generation.
  - **Rationale:** Allows quickly exposing class and function APIs as standard command-line interfaces with minimal boilerplate.

- **loguru**
  - **Purpose:** Simple and elegant logging utility.
  - **Rationale:** Offers clean configuration, structured output, and simpler syntax compared to Python's standard `logging` module.

- **platformdirs**
  - **Purpose:** Locate OS-standard app directories (data, cache, config).
  - **Rationale:** Simplifies multi-platform directory finding following standard conventions (e.g., Application Support on macOS, standard cache directories on Linux/Windows).

- **requests**
  - **Purpose:** Synchronous HTTP library.
  - **Rationale:** Used during Chrome for Testing binary downloads and verification checks. Reliable, simple API.

- **psutil**
  - **Purpose:** Cross-platform process monitoring and management.
  - **Rationale:** Necessary to detect, check health, and cleanly terminate detached Chrome or CloakBrowser processes.

- **prompt_toolkit**
  - **Purpose:** Interactive terminal command prompts and line editing.
  - **Rationale:** Used to build interactive shells or prompts (such as the interactive browser control loops).

- **html2text**
  - **Purpose:** Render HTML pages or elements into Markdown.
  - **Rationale:** Allows fast extraction of webpage content into readable Markdown format.

- **tomli-w**
  - **Purpose:** Write TOML configuration files.
  - **Rationale:** Modern, standard format configuration writing library. (Complements standard library `tomllib` which is read-only).

- **httpx**
  - **Purpose:** Modern HTTP client supporting both sync and async request models.
  - **Rationale:** A necessary dependency of CloakBrowser, allowing API handshakes and download checks over sync/async channels.

## Development and Test Dependencies

- **pytest**
  - **Purpose:** Unit and integration testing framework.
  - **Rationale:** The industry standard for Python testing.

- **ruff**
  - **Purpose:** Fast linting and formatting tool.
  - **Rationale:** Replaces multiple linters (flake8, black, isort, etc.) with extremely fast execution.

- **mypy**
  - **Purpose:** Static type checking.
  - **Rationale:** Ensures type-safety compliance across the 100% type-hinted codebase.

### Optional Camoufox session engine

`playwrightauthor[camoufox]` pins Camoufox 0.5.8, whose dependency requires
Playwright <1.63 (tested 1.62.0). Install its binary explicitly with
`python -m camoufox fetch`. Profiles retain generated device config privately
in device.json; new package versions require a compatible or new profile.

The macOS-only attention verification script declares PyObjC Cocoa and
ApplicationServices 12.2.2 as isolated script dependencies. They observe native
focus/window/Spaces state and are not runtime package requirements.
