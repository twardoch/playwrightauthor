# PlaywrightAuthor Documentation

Master browser automation with persistent authentication.

## Documentation Structure

### [Authentication Workflows](auth/index.md)
Step-by-step guides for authenticating with popular services:
- [Gmail/Google Authentication](auth/gmail.md)
- [GitHub Authentication](auth/github.md)
- [LinkedIn Authentication](auth/linkedin.md)
- [Troubleshooting Authentication](auth/troubleshooting.md)

### [Architecture](architecture/index.md)
Understanding PlaywrightAuthor's internals:
- [Browser Lifecycle Management](architecture/browser-lifecycle.md)
- [Component Architecture](architecture/components.md)
- [Error Handling & Recovery](architecture/error-handling.md)

### [Platform-Specific Guides](platforms/index.md)
Setup and optimization for each platform:
- [macOS Guide](platforms/macos.md) - M1/Intel, permissions, Homebrew
- [Windows Guide](platforms/windows.md) - UAC, antivirus, PowerShell
- [Linux Guide](platforms/linux.md) - Distributions, Docker, dependencies

### [Performance](performance/index.md)
Optimization and best practices:
- [Resource Optimization](performance/optimization.md)
- [Memory Management](performance/memory.md)
- [Connection Pooling](performance/connection-pooling.md)
- [Monitoring & Debugging](performance/monitoring.md)

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

- **Installation Issues**: [Troubleshooting guide](auth/troubleshooting.md)
- **Platform-Specific Problems**: [Platform guides](platforms/index.md)
- **Performance Issues**: [Optimization strategies](performance/optimization.md)
- **Bug Reports**: [GitHub Issues](https://github.com/twardoch/playwrightauthor/issues)

## Common Use Cases

1. **Automated Testing** - Reuse authenticated sessions for faster test runs
2. **Web Scraping** - Stay logged in across scraping jobs
3. **Process Automation** - Automate tasks that require login
4. **Multi-Account Management** - Switch between different authenticated profiles