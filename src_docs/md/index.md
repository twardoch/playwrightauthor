# PlaywrightAuthor Documentation

PlaywrightAuthor is a convenience wrapper for Microsoft Playwright that automates browser setup and configuration.

## TL;DR

PlaywrightAuthor removes the tedious setup work from browser automation:

- **Installs and updates Chrome for Testing automatically**
- **Manages browser processes, including debug mode**
- **Persists user authentication across sessions**
- **Provides simple context managers for browser access**
- **Supports both sync and async operations**

```python
from playwrightauthor import Browser

# Simple synchronous usage
with Browser() as browser:
    page = browser.new_page()
    page.goto("https://example.com")
    # Browser is ready with authentication
```

## Documentation Chapters

### 1. [Getting Started](getting-started.md)
Installation, prerequisites, and your first script.

### 2. [Basic Usage](basic-usage.md)
Context managers and essential patterns.

### 3. [Configuration](configuration.md)
Settings and environment variables.

### 4. [Browser Management](browser-management.md)
Chrome installation and process handling.

### 5. [Authentication](authentication.md)
User profiles and session persistence.

### 6. [Advanced Features](advanced-features.md)
Async operations and performance tuning.

### 7. [Troubleshooting](troubleshooting.md)
Common issues and fixes.

### 8. [API Reference](api-reference.md)
Complete API documentation.

### 9. [Contributing](contributing.md)
Development setup and contribution guidelines.

## Quick Navigation

- **New to browser automation?** [Getting Started](getting-started.md)
- **Need authentication?** [Authentication](authentication.md)
- **Having issues?** [Troubleshooting](troubleshooting.md)
- **Looking for methods?** [API Reference](api-reference.md)
- **Want to contribute?** [Contributing](contributing.md)

## Key Features

- **Zero-config setup** - Works immediately after install
- **Authentication persistence** - No need to re-login every time
- **Cross-platform support** - Windows, macOS, Linux
- **Performance optimized** - Minimal overhead
- **Developer tools** - Logging and debugging included