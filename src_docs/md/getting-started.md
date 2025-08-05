# Getting Started

## Installation

PlaywrightAuthor requires Python 3.8+ and can be installed via pip:

```bash
pip install playwrightauthor
```

### Prerequisites

- **Python 3.8+** - Required for modern type hints and async support
- **Chrome or Chromium** - Automatically managed by PlaywrightAuthor
- **Network access** - For downloading Chrome for Testing if needed

### System Requirements

| Platform | Requirements |
|----------|-------------|
| **Windows** | Windows 10+ (x64) |
| **macOS** | macOS 10.15+ (Intel/Apple Silicon) |
| **Linux** | Ubuntu 18.04+, CentOS 7+, or equivalent |

## Quick Start

### Your First Script

Create a simple automation script:

```python
# my_first_script.py
from playwrightauthor import Browser

def main():
    with Browser() as browser:
        page = browser.new_page()
        page.goto("https://example.com")
        title = page.title()
        print(f"Page title: {title}")

if __name__ == "__main__":
    main()
```

Run it:

```bash
python my_first_script.py
```

### What Happens Behind the Scenes

1. **Chrome Detection**: PlaywrightAuthor checks for existing Chrome installations
2. **Installation**: Downloads Chrome for Testing if needed (one-time setup)
3. **Process Management**: Launches Chrome with remote debugging enabled
4. **Connection**: Connects Playwright to the Chrome instance
5. **Authentication**: Uses persistent user profile for authenticated sessions

### Async Version

For async/await patterns:

```python
import asyncio
from playwrightauthor import AsyncBrowser

async def main():
    async with AsyncBrowser() as browser:
        page = await browser.new_page()
        await page.goto("https://example.com")
        title = await page.title()
        print(f"Page title: {title}")

if __name__ == "__main__":
    asyncio.run(main())
```

## First Steps Checklist

- [ ] Install PlaywrightAuthor: `pip install playwrightauthor`
- [ ] Run the example script above
- [ ] Verify Chrome is downloaded and launched automatically
- [ ] Check that you can navigate to web pages
- [ ] Explore the [Basic Usage](basic-usage.md) guide for more examples

## Common First-Time Issues

### Permission Errors
If you encounter permission errors on Linux/macOS:
```bash
chmod +x ~/.cache/playwrightauthor/chrome/*/chrome
```

### Network Restrictions
If behind a corporate firewall, set proxy environment variables:
```bash
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080
```

### Antivirus Software
Some antivirus software may block Chrome downloads. Add exclusions for:
- `~/.cache/playwrightauthor/` (Linux/macOS)
- `%APPDATA%/playwrightauthor/` (Windows)

## Next Steps

- Read [Basic Usage](basic-usage.md) for core concepts
- Configure settings in [Configuration](configuration.md)
- Learn about authentication in [Authentication](authentication.md)
- Explore advanced features in [Advanced Features](advanced-features.md)