# Basic Usage

## Core Concepts

PlaywrightAuthor provides two main classes for browser automation:

- **`Browser()`** - Synchronous context manager
- **`AsyncBrowser()`** - Asynchronous context manager

Both return authenticated Playwright browser objects ready for automation.

## Browser Context Manager

### Synchronous Usage

```python
from playwrightauthor import Browser

# Basic context manager
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
    # Open multiple tabs
    page1 = browser.new_page()
    page2 = browser.new_page()
    
    page1.goto("https://github.com")
    page2.goto("https://stackoverflow.com")
    
    # Work with both pages
    print(f"Page 1: {page1.title()}")
    print(f"Page 2: {page2.title()}")
```

### Form Interaction

```python
with Browser() as browser:
    page = browser.new_page()
    page.goto("https://example.com/login")
    
    # Fill form fields
    page.fill("#username", "your_username")
    page.fill("#password", "your_password")
    page.click("#login-button")
    
    # Wait for navigation
    page.wait_for_url("**/dashboard")
```

### Element Interaction

```python
with Browser() as browser:
    page = browser.new_page()
    page.goto("https://example.com")
    
    # Click elements
    page.click("button")
    page.click("text=Submit")
    page.click("#submit-btn")
    
    # Type text
    page.type("#search", "playwright automation")
    
    # Select options
    page.select_option("#dropdown", "option1")
```

### Screenshots and PDFs

```python
with Browser() as browser:
    page = browser.new_page()
    page.goto("https://example.com")
    
    # Take screenshot
    page.screenshot(path="screenshot.png")
    
    # Generate PDF
    page.pdf(path="page.pdf")
    
    # Full page screenshot
    page.screenshot(path="fullpage.png", full_page=True)
```

## Configuration Options

### Browser Configuration

```python
from playwrightauthor import Browser, BrowserConfig

config = BrowserConfig(
    headless=False,  # Show browser window
    timeout=30000,   # 30 second timeout
    user_data_dir="/custom/path"  # Custom profile location
)

with Browser(config=config) as browser:
    # Browser will use custom configuration
    page = browser.new_page()
    page.goto("https://example.com")
```

### Viewport and Device Emulation

```python
with Browser() as browser:
    # Set custom viewport
    page = browser.new_page(viewport={"width": 1920, "height": 1080})
    
    # Or emulate devices
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
        # Wait up to 5 seconds for element
        page.click("#slow-button", timeout=5000)
    except TimeoutError:
        print("Button not found within 5 seconds")
```

## Best Practices

### Resource Management

```python
# ✅ Always use context managers
with Browser() as browser:
    page = browser.new_page()
    # Automatic cleanup when exiting context

# ❌ Avoid manual management
browser = Browser()
# Risk of resource leaks
```

### Page Lifecycle

```python
with Browser() as browser:
    page = browser.new_page()
    
    # Navigate and wait for page load
    page.goto("https://example.com")
    page.wait_for_load_state("networkidle")
    
    # Perform actions
    page.click("button")
    
    # Clean up if needed
    page.close()
```

### Element Waiting

```python
with Browser() as browser:
    page = browser.new_page()
    page.goto("https://example.com")
    
    # Wait for element to be visible
    page.wait_for_selector("#content", state="visible")
    
    # Wait for element to be clickable
    page.wait_for_selector("button", state="attached")
    
    # Then interact
    page.click("button")
```

## Debugging Tips

### Enable Verbose Logging

```python
from playwrightauthor import Browser
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

with Browser() as browser:
    page = browser.new_page()
    page.goto("https://example.com")
```

### Slow Down Actions

```python
with Browser() as browser:
    # Add delays for debugging
    page = browser.new_page()
    page.goto("https://example.com")
    
    page.click("button")
    page.wait_for_timeout(2000)  # 2 second pause
    
    page.fill("#input", "text")
    page.wait_for_timeout(1000)  # 1 second pause
```

### Inspect Elements

```python
with Browser() as browser:
    page = browser.new_page()
    page.goto("https://example.com")
    
    # Pause for manual inspection
    page.pause()  # Opens Playwright Inspector
```

## Next Steps

- Learn about [Configuration](configuration.md) options
- Explore [Browser Management](browser-management.md) details
- Set up [Authentication](authentication.md) workflows
- Check [Advanced Features](advanced-features.md) for complex scenarios