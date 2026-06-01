---
layout: default
title: Home
nav_order: 1
---

# PlaywrightAuthor Documentation
<!-- this_file: docs/index.md -->

Master browser automation with persistent authentication.

## Documentation Structure

### 1. Browser Engines
- **[Selectable Browser Engines](01-browser-engines.md)** - Switching between Chrome for Testing and CloakBrowser

### 2. Authentication Workflows
- **[Authentication Workflows Overview](02-auth-overview.md)** - Maintaining persistent authentication sessions
- **[Gmail/Google Authentication](03-auth-gmail.md)** - Handling 2FA and Workspace accounts
- **[GitHub Authentication](04-auth-github.md)** - Access tokens, OAuth authorization, and MFA
- **[LinkedIn Authentication](05-auth-linkedin.md)** - Scraping and automation with anti-bot handling
- **[Troubleshooting Authentication](06-auth-troubleshooting.md)** - Diagnosing cookie and session problems

### 3. Architecture Deep Dive
- **[Architecture Overview](07-architecture-overview.md)** - Component layout and sequence diagrams
- **[Browser Lifecycle Management](08-architecture-lifecycle.md)** - Automated binary discovery, installation, and launch
- **[Component Details](09-architecture-components.md)** - API modules, state, and browser managers
- **[Error Handling & Recovery](10-architecture-errors.md)** - Resiliency logic and exceptions

### 4. Platform Guides
- **[Platform-Specific Guides Overview](11-platform-overview.md)** - Multi-platform support summary
- **[macOS Guide](12-platform-macos.md)** - Universal binaries, Accessibility permissions, Homebrew
- **[Windows Guide](13-platform-windows.md)** - PowerShell, Defender, and UAC elevation
- **[Linux Guide](14-platform-linux.md)** - Dependencies, Alpine, Docker containers

### 5. Performance Optimization
- **[Performance Optimization Overview](15-performance-overview.md)** - Latency, CPU and scaling benchmarks
- **[Memory Management](16-performance-memory.md)** - Resource blocking, leak checks, and memory status
- **[Connection Pooling](17-performance-pooling.md)** - Browser process queueing and reuse
- **[Performance Monitoring](18-performance-monitoring.md)** - Real-time metrics and tracing

---

## Quick Start

```python
from playwrightauthor import Browser

# First run - follow the authentication prompts
with Browser() as browser:
    page = browser.new_page()
    page.goto("https://mail.google.com")
    # Browser stays open for manual login

# Subsequent runs - already authenticated
with Browser() as browser:
    page = browser.new_page()
    page.goto("https://mail.google.com")
    # Automatically logged in
```

## Getting Help

- **Installation/Auth Issues**: [Troubleshooting guide](06-auth-troubleshooting.md)
- **Platform-Specific Problems**: [Platform guides](11-platform-overview.md)
- **Performance Optimization**: [Optimization strategies](15-performance-overview.md)
- **Bug Reports**: [GitHub Issues](https://github.com/twardoch/playwrightauthor/issues)