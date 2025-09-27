# Basic Usage

## Core Concepts

PlaywrightAuthor provides two classes for browser automation:

- **`Browser()`** - Synchronous context manager
- **`AsyncBrowser()`** - Asynchronous context manager

Both return authenticated Playwright browser objects ready for automation.

## Browser Context Manager

### Synchronous Usage

```python
from playwrightauthor import Browser

with Browser() as browser:
    page = browser.new_page()
    page.goto("https://github.com")
    print(page.title())
```

### Asynchronous Usage

```python
import asyncio
from playwrightauthor import AsyncBrowser

async def automate():
    async with AsyncBrowser() as browser:
        page = await browser.new_page()
        await page.goto("https://github.com")
        title = await page.title()
        print(title)

asyncio.run(automate())
```

## Common Patterns

### Multiple Pages

```python
with Browser() as browser:
    page1 = browser.new_page()
    page2 = browser.new_page()
    
    page1.goto("https://github.com")
    page2.goto("https://stackoverflow.com")
    
    print(f"Page 1: {page1.title()}")
    print(f"Page 2: {page2.title()}")
```

### Form Interaction

```python
with Browser() as browser:
    page = browser.new_page()
    page.goto("https://example.com/login")
    
    page.fill("#username", "your_username")
    page.fill("#password", "your_password")
    page.click("#login-button")
    
    page.wait_for_url("**/dashboard")
```

### Element Interaction

```python
with Browser() as browser:
    page = browser.new_page()
    page.goto("https://example.com")
    
    page.click("button")
    page.click("text=Submit")
    page.click("#submit-btn")
    
    page.type("#search", "playwright automation")
    page.select_option("#dropdown", "option1")
```

### Screenshots and PDFs

```python
with Browser() as browser:
    page = browser.new_page()
    page.goto("https://example.com")
    
    page.screenshot(path="screenshot.png")
    page.pdf(path="page.pdf")
    page.screenshot(path="fullpage.png", full_page=True)
```

## Configuration Options

### Browser Configuration

```python
from playwrightauthor import Browser, BrowserConfig

config = BrowserConfig(
    headless=False,
    timeout=30000,
    user_data_dir="/custom/path"
)

with Browser(config=config) as browser:
    page = browser.new_page()
    page.goto("https://example.com")
```

### Viewport and Device Emulation

```python
with Browser() as browser:
    # Custom viewport
    page = browser.new_page(viewport={"width": 1920, "height": 1080})
    
    # Device emulation
    iphone = browser.devices["iPhone 12"]
    page = browser.new_page(**iphone)
    
    page.goto("https://example.com")
```

## Error Handling

### Basic Error Handling

```python
from playwrightauthor import Browser
from playwrightauthor.exceptions import BrowserError

try:
    with Browser() as browser:
        page = browser.new_page()
        page.goto("https://example.com")
        page.click("#non-existent-button")
except BrowserError as e:
    print(f"Browser error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Timeout Handling

```python
from playwright.sync_api import TimeoutError

with Browser() as browser:
    page = browser.new_page()
    page.goto("https://example.com")
    
    try:
        page.click("#slow-button", timeout=5000)
    except TimeoutError:
        print("Button not found within 5 seconds")
```

## Best Practices

### Resource Management

```python
# ✅ Use context managers
with Browser() as browser:
    page = browser.new_page()
    # Automatic cleanup

# ❌ Avoid manual management
browser = Browser()
# Risk of resource leaks
```

### Page Lifecycle

```python
with Browser() as browser:
    page = browser.new_page()
    
    page.goto("https://example.com")
    page.wait_for_load_state("networkidle")
    
    page.click("button")
    page.close()
```

### Element Waiting

```python
with Browser() as browser:
    page = browser.new_page()
    page.goto("https://example.com")
    
    # Wait for element visibility
    page.wait_for_selector("#content", state="visible")
    
    # Wait for element attachment
    page.wait_for_selector("button", state="attached")
    
    page.click("button")
```

## Debugging Tips

### Enable Verbose Logging

```python
from playwrightauthor import Browser
import logging

logging.basicConfig(level=logging.DEBUG)

with Browser() as browser:
    page = browser.new_page()
    page.goto("https://example.com")
```

### Slow Down Actions

```python
with Browser() as browser:
    page = browser.new_page()
    page.goto("https://example.com")
    
    page.click("button")
    page.wait_for_timeout(2000)
    
    page.fill("#input", "text")
    page.wait_for_timeout(1000)
```

### Inspect Elements

```python
with Browser() as browser:
    page = browser.new_page()
    page.goto("https://example.com")
    
    page.pause()  # Opens Playwright Inspector
```

## Next Steps

- [Configuration](configuration.md) options
- [Browser Management](browser-management.md) details
- [Authentication](authentication.md) workflows
- [Advanced Features](advanced-features.md) for complex scenarios