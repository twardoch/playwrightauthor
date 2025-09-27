# Getting Started

## Installation

PlaywrightAuthor requires Python 3.8+ and is installed via pip:

```bash
pip install playwrightauthor
```

### Prerequisites

- **Python 3.8+** – For type hints and async support  
- **Chrome or Chromium** – Managed automatically by PlaywrightAuthor  
- **Network access** – To download Chrome for Testing if not found locally  

### System Requirements

| Platform | Requirements |
|----------|-------------|
| **Windows** | Windows 10+ (x64) |
| **macOS** | macOS 10.15+ (Intel or Apple Silicon) |
| **Linux** | Ubuntu 18.04+, CentOS 7+, or similar |

## Quick Start

### Your First Script

Create a basic automation script:

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

1. **Chrome Detection** – Checks for existing installations  
2. **Installation** – Downloads Chrome for Testing if needed (once)  
3. **Process Management** – Launches Chrome with remote debugging enabled  
4. **Connection** – Attaches Playwright to the browser  
5. **Authentication** – Uses a persistent profile for logged-in sessions  

### Async Version

Use this version if you're working with async code:

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
- [ ] Run the example script  
- [ ] Confirm Chrome downloads and starts automatically  
- [ ] Navigate to a webpage successfully  
- [ ] Review the [Basic Usage](basic-usage.md) guide for more examples  

## Common First-Time Issues

### Permission Errors

On Linux/macOS, fix execution permissions for Chrome:

```bash
chmod +x ~/.cache/playwrightauthor/chrome/*/chrome
```

### Network Restrictions

If you're behind a proxy, configure environment variables:

```bash
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080
```

### Antivirus Software

Some antivirus tools may interfere with Chrome downloads. Add exceptions for:

- `~/.cache/playwrightauthor/` (Linux/macOS)  
- `%APPDATA%/playwrightauthor/` (Windows)  

## Next Steps

- [Basic Usage](basic-usage.md) – Core concepts and examples  
- [Configuration](configuration.md) – Settings and customization  
- [Authentication](authentication.md) – Login handling and sessions  
- [Advanced Features](advanced