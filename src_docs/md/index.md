# PlaywrightAuthor Documentation

Welcome to the PlaywrightAuthor documentation. This library is a convenience package for Microsoft Playwright that handles browser automation setup automatically.

## TL;DR

PlaywrightAuthor eliminates the boilerplate for browser automation by:

- **Automatically managing Chrome for Testing installation and updates**
- **Handling browser process management with debug mode setup**
- **Providing persistent user authentication through profile reuse**
- **Offering simple context managers for immediate browser access**
- **Supporting both sync and async operations**

```python
from playwrightauthor import Browser

# Simple synchronous usage
with Browser() as browser:
    page = browser.new_page()
    page.goto("https://example.com")
    # Browser is authenticated and ready to use
```

## Documentation Chapters

### 1. [Getting Started](getting-started.md)
Installation, prerequisites, and your first automation script. Learn how to set up PlaywrightAuthor and run your first browser automation.

### 2. [Basic Usage](basic-usage.md)
Core concepts, context managers, and simple examples. Master the fundamental patterns for using PlaywrightAuthor effectively.

### 3. [Configuration](configuration.md)
Settings, environment variables, and customization options. Configure PlaywrightAuthor to match your specific requirements.

### 4. [Browser Management](browser-management.md)
Chrome installation, process handling, and debugging. Deep dive into how PlaywrightAuthor manages browser instances.

### 5. [Authentication](authentication.md)
User profiles, session persistence, and login workflows. Learn how to maintain authenticated sessions across automation runs.

### 6. [Advanced Features](advanced-features.md)
Async operations, monitoring, custom configurations, and performance optimization. Explore sophisticated usage patterns.

### 7. [Troubleshooting](troubleshooting.md)
Common issues, debugging techniques, and solutions. Resolve problems quickly with comprehensive troubleshooting guides.

### 8. [API Reference](api-reference.md)
Complete API documentation with examples. Detailed reference for all classes, methods, and configuration options.

### 9. [Contributing](contributing.md)
Development setup, testing, and contribution guidelines. Join the PlaywrightAuthor development community.

## Quick Navigation

- **New to browser automation?** Start with [Getting Started](getting-started.md)
- **Need to configure authentication?** Check [Authentication](authentication.md)
- **Having issues?** Visit [Troubleshooting](troubleshooting.md)
- **Looking for specific methods?** Browse [API Reference](api-reference.md)
- **Want to contribute?** Read [Contributing](contributing.md)

## Key Features

- 🚀 **Zero-config setup** - Works out of the box
- 🔐 **Authentication handling** - Persistent user sessions
- 🌐 **Cross-platform** - Windows, macOS, Linux support
- ⚡ **Performance optimized** - Efficient browser management
- 🛠️ **Developer friendly** - Rich logging and debugging tools