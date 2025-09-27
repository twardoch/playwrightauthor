# PlaywrightAuthor

Your personal, authenticated browser for Playwright, ready in one line of code.

PlaywrightAuthor is a convenience package for **Microsoft Playwright**. It handles browser automation setup: finding and launching Chrome for Testing, keeping it authenticated with your user profile, and connecting Playwright to it. Instantiate a class, get a ready-to-use `Browser` object, and focus on writing automation scripts instead of boilerplate.

**Note**: PlaywrightAuthor uses Chrome for Testing (not regular Chrome) because Google disabled CDP automation with user profiles in regular Chrome. Chrome for Testing is Google's official build designed for automation, ensuring persistent login sessions and reusable browser profiles.

The core idea:

```python
from playwrightauthor import Browser

with Browser() as browser:
    # Standard Playwright browser object
    # Already connected to logged-in browser
    page = browser.new_page()
    page.goto("https://github.com/me")
    print(f"Welcome, {page.locator('.user-profile-name').inner_text()}!")
```

## Contents

* [Features](#features)
* [Installation](#installation)
* [Quick start](#quick-start)
* [Common patterns](#common-patterns)
* [Best practices](#best-practices)
* [CLI](#command-line-interface)
* [Developer workflow](#developer-workflow)
* [Architecture](#package-architecture)
* [Troubleshooting](#troubleshooting)
* [Contributing](#contributing)
* [License](#license)

## Features

### Zero-Configuration Automation
- **Automatic Chrome Management**: Discovers, installs, and launches Chrome for Testing with remote debugging enabled
- **Persistent Authentication**: Maintains user sessions across script runs using persistent browser profiles
- **Cross-Platform Support**: Works on Windows, macOS, and Linux

### Performance & Reliability
- **Lazy Loading**: Optimized startup with on-demand imports
- **Connection Health Monitoring**: Diagnostics and automatic retry logic
- **State Management**: Caches browser paths for faster subsequent runs
- **Error Recovery**: Graceful handling of browser crashes

### Developer Experience
- **Simple API**: Clean `Browser()` and `AsyncBrowser()` context managers
- **CLI Tools**: Command-line interface for browser and profile management
- **Type Safety**: 100% type-hinted codebase
- **Testing**: Extensive test suite with CI/CD

### Advanced Management
- **Profile System**: Create and switch between multiple browser profiles
- **Configuration Management**: Environment variable support
- **Diagnostic Tools**: Built-in troubleshooting
- **JSON Output**: Machine-readable formats

## Installation

```bash
# Install PlaywrightAuthor
pip install playwrightauthor

# Install Playwright browsers
playwright install chromium
```

## Quick start

```bash
# Create script file
cat > example.py << 'EOF'
from playwrightauthor import Browser

with Browser() as browser:
    page = browser.new_page()
    page.goto("https://github.com")
    print(f"Page title: {page.title()}")
EOF

# Run script
python example.py
```

Example `myscript.py`:
```python
from playwrightauthor import Browser, AsyncBrowser
import asyncio

# Synchronous API
print("--- Running Sync Example ---")
with Browser(verbose=True) as browser:
    page = browser.new_page()
    page.goto("https://github.com")
    print(f"Page title: {page.title()}")

# Asynchronous API
async def main():
    print("\n--- Running Async Example ---")
    async with AsyncBrowser(verbose=True) as browser:
        page = await browser.new_page()
        await page.goto("https://duckduckgo.com")
        print(f"Page title: {await page.title()}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Common patterns

### Pre-Authorized Sessions (Recommended)

PlaywrightAuthor reuses existing browser sessions. Recommended workflow:

```bash
# Step 1: Launch Chrome for Testing in CDP mode
playwrightauthor browse

# Step 2: Manually log into services
# Browser stays running after command exits

# Step 3: Run automation scripts
python your_script.py
```

Scripts should use `get_page()` to reuse contexts:

```python
from playwrightauthor import Browser

with Browser() as browser:
    # get_page() reuses existing contexts
    page = browser.get_page()
    page.goto("https://github.com/notifications")
    notifications = page.locator(".notification-list-item").count()
    print(f"You have {notifications} GitHub notifications")
```

Benefits:
- **One-time authentication**: Log in once, all scripts use session
- **Session persistence**: Authentication persists across runs
- **Development efficiency**: No login flows in automation code
- **Multi-service support**: Multiple services logged in simultaneously

### Authentication Workflow

For programmatic authentication:

```python
from playwrightauthor import Browser

# First run: Manual login required
with Browser(profile="work") as browser:
    page = browser.new_page()
    page.goto("https://mail.google.com")
    # Complete login manually
    print(f"Logged in as: {page.locator('[data-testid=user-email]').inner_text()}")

# Subsequent runs: Automatic authentication
with Browser(profile="work") as browser:
    page = browser.new_page() 
    page.goto("https://mail.google.com")
    inbox_count = page.locator('[data-testid=inbox-count]').inner_text()
    print(f"You have {inbox_count} unread emails")
```

### Error Handling

Production automation with retry logic:

```python
from playwrightauthor import Browser
from playwright.sync_api import TimeoutError
import time

def scrape_with_retry(url, max_retries=3):
    """Robust scraping with automatic retry."""
    
    for attempt in range(max_retries):
        try:
            with Browser(verbose=attempt > 0) as browser:
                page = browser.new_page()
                page.set_default_timeout(30000)
                page.goto(url)
                page.wait_for_selector('[data-testid=content]', timeout=10000)
                
                title = page.title()
                content = page.locator('[data-testid=content]').inner_text()
                return {"title": title, "content": content}
                
        except TimeoutError:
            print(f"Attempt {attempt + 1} timed out, retrying...")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            continue
            
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            continue
    
    raise Exception(f"Failed to scrape {url} after {max_retries} attempts")

# Usage
try:
    data = scrape_with_retry("https://example.com")
    print(f"Successfully scraped: {data['title']}")
except Exception as e:
    print(f"Scraping failed: {e}")
```

### Profile Management

Multiple accounts or environments:

```python
from playwrightauthor import Browser

profiles = {
    "work": "work@company.com",
    "personal": "me@gmail.com", 
    "testing": "test@example.com"
}

def check_email_for_all_accounts():
    """Check email counts across accounts."""
    results = {}
    
    for profile_name, email in profiles.items():
        try:
            with Browser(profile=profile_name) as browser:
                page = browser.new_page()
                page.goto("https://mail.google.com")
                unread_count = page.locator('[aria-label="Inbox"]').get_attribute('data-count')
                results[email] = int(unread_count or 0)
                
        except Exception as e:
            print(f"Failed to check {email}: {e}")
            results[email] = None
    
    return results

email_counts = check_email_for_all_accounts()
for email, count in email_counts.items():
    if count is not None:
        print(f"{email}: {count} unread emails")
    else:
        print(f"{email}: Failed to check")
```

### Interactive Development

Use REPL for development:

```bash
# Start interactive REPL
python -m playwrightauthor repl

# In REPL:
>>> page = browser.new_page()
>>> page.goto("https://github.com")
>>> page.title()
'GitHub: Let's build from here · GitHub'

>>> page.locator('h1').inner_text()
'Let's build from here'

>>> !status
Browser is ready.
  - Path: /Users/user/.playwrightauthor/chrome/chrome
  - User Data: /Users/user/.playwrightauthor/profiles/default

>>> exit()
>>> browser = Browser(profile="work").__enter__()
>>> page = browser.new_page()
>>> page.goto("https://mail.google.com")
```

### Async Performance

High-performance concurrent operations:

```python
import asyncio
from playwrightauthor import AsyncBrowser

async def scrape_multiple_pages(urls):
    """Scrape pages concurrently."""
    
    async def scrape_single_page(url):
        async with AsyncBrowser() as browser:
            page = await browser.new_page()
            await page.goto(url)
            title = await page.title()
            return {"url": url, "title": title}
    
    semaphore = asyncio.Semaphore(5)
    
    async def limited_scrape(url):
        async with semaphore:
            return await scrape_single_page(url)
    
    tasks = [limited_scrape(url) for url in urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results

urls = [
    "https://github.com",
    "https://stackoverflow.com", 
    "https://python.org"
]

async def main():
    results = await scrape_multiple_pages(urls)
    for result in results:
        if isinstance(result, dict):
            print(f"{result['url']}: {result['title']}")
        else:
            print(f"Error: {result}")

asyncio.run(main())
```

### Quick Reference

**Common commands:**
```bash
# Launch browser for manual login
python -m playwrightauthor browse

# Check status
python -m playwrightauthor status

# Start REPL
python -m playwrightauthor repl

# Diagnose issues
python -m playwrightauthor diagnose

# Clear cache
python -m playwrightauthor clear-cache
```

**Common patterns:**
```python
# Reuse existing session
with Browser() as browser:
    page = browser.get_page()
    page.goto("https://example.com")

# Create new page
with Browser() as browser:
    page = browser.new_page()
    page.goto("https://example.com")

# Multiple accounts
with Browser(profile="work") as browser:
    page = browser.get_page()

# High performance
async with AsyncBrowser() as browser:
    page = await browser.get_page()
```

## Best practices

### Resource Management

Always use context managers:

```python
from playwrightauthor import Browser

# ✅ GOOD
with Browser() as browser:
    page = browser.new_page()
    page.goto("https://example.com")

# ❌ BAD
browser = Browser().__enter__()
page = browser.new_page()
page.goto("https://example.com")
```

Page lifecycle management:
```python
with Browser() as browser:
    page1 = browser.new_page()
    page2 = browser.new_page()
    
    page1.close()
    page2.close()
    
    # Or use page context managers
    page = browser.new_page()
    try:
        page.goto("https://example.com")
    finally:
        page.close()
```

### Performance Optimization

Large-scale automation:
```python
from playwrightauthor import AsyncBrowser
import asyncio

async def optimize_for_performance():
    async with AsyncBrowser() as browser:
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720}
        )
        
        semaphore = asyncio.Semaphore(5)
        
        async def process_url(url):
            async with semaphore:
                page = await context.new_page()
                try:
                    await page.goto(url, wait_until="domcontentloaded")
                    title = await page.title()
                    return {"url": url, "title": title}
                finally:
                    await page.close()
        
        urls = ["https://example1.com", "https://example2.com"]
        results = await asyncio.gather(*[process_url(url) for url in urls])
        
        await context.close()
        return results

results = asyncio.run(optimize_for_performance())
```

Memory management:
```python
from playwrightauthor import Browser

def memory_efficient_scraping(urls):
    results = []
    with Browser() as browser:
        batch_size = 10
        for i in range(0, len(urls), batch_size):
            batch = urls[i:i + batch_size]
            
            for url in batch:
                page = browser.new_page()
                try:
                    page.goto(url, timeout=30000)
                    results.append({
                        "url": url,
                        "title": page.title(),
                        "status": "success"
                    })
                except Exception as e:
                    results.append({
                        "url": url, 
                        "error": str(e),
                        "status": "failed"
                    })
                finally:
                    page.close()
    
    return results
```

### Security

Profile and credential management:
```python
from playwrightauthor import Browser
import os

def secure_automation_setup():
    profiles = {
        "production": "prod-automation",
        "staging": "staging-test", 
        "development": "dev-local"
    }
    
    environment = os.getenv("ENVIRONMENT", "development")
    profile_name = profiles.get(environment, "default")
    
    with Browser(profile=profile_name, verbose=False) as browser:
        page = browser.new_page()
        page.set_extra_http_headers({
            "User-Agent": "Company-Automation/1.0"
        })
        page.goto("https://secure-api.company.com")
        return page.content()
```

Sensitive data handling:
```python
from playwrightauthor import Browser
import logging

logging.basicConfig(level=logging.INFO)

def secure_login_automation():
    with Browser(profile="secure-profile", verbose=False) as browser:
        page = browser.new_page()
        page.goto("https://app.example.com/login")
        
        username = os.getenv("APP_USERNAME")
        password = os.getenv("APP_PASSWORD")
        
        if not username or not password:
            raise ValueError("Credentials missing")
        
        page.fill('[name="username"]', username)
        page.fill('[name="password"]', password)
        
        logging.info("Attempting login")
        page.click('[type="submit"]')
        page.wait_for_url("**/dashboard")
        logging.info("Authentication successful")
        
        return page
```

### Configuration

Production configuration:
```python
from playwrightauthor.config import PlaywrightAuthorConfig, BrowserConfig, NetworkConfig, LoggingConfig
from pathlib import Path

def create_production_config():
    return PlaywrightAuthorConfig(
        browser=BrowserConfig(
            headless=True,
            timeout=45000,
            viewport_width=1920,
            viewport_height=1080,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
            ]
        ),
        network=NetworkConfig(
            retry_attempts=5,
            download_timeout=600,
            exponential_backoff=True,
            proxy=os.getenv("HTTPS_PROXY")
        ),
        logging=LoggingConfig(
            verbose=False,
            log_level="INFO",
            log_file=Path("/var/log/playwrightauthor.log")
        ),
        enable_lazy_loading=True,
        default_profile="production"
    )

config = create_production_config()
from playwrightauthor.config import save_config
save_config(config)
```

Environment variables:
```bash
export PLAYWRIGHTAUTHOR_HEADLESS=true
export PLAYWRIGHTAUTHOR_TIMEOUT=45000
export PLAYWRIGHTAUTHOR_VERBOSE=false
export PLAYWRIGHTAUTHOR_LOG_LEVEL=INFO
export PLAYWRIGHTAUTHOR_RETRY_ATTEMPTS=5

# Never hardcode credentials
export APP_USERNAME=your-automation-user
export APP_PASSWORD=secure-password-from-secrets-manager

export HTTPS_PROXY=http://proxy.company.com:8080
```

### Error Handling

Production-grade error handling:
```python
from playwrightauthor import Browser
from playwright.sync_api import TimeoutError
import logging
import time

def robust_automation_with_error_handling():
    max_retries = 3
    base_delay = 1.0
    
    for attempt in range(max_retries):
        try:
            with Browser(verbose=attempt > 0) as browser:
                page = browser.new_page()
                page.set_default_timeout(30000)
                
                try:
                    page.goto("https://example.com", wait_until="networkidle")
                except TimeoutError:
                    logging.warning(f"Page load timeout on attempt {attempt + 1}")
                    if attempt < max_retries - 1:
                        continue
                    raise
                
                try:
                    page.wait_for_selector('[data-testid="content"]', timeout=10000)
                except TimeoutError:
                    logging.error("Required content not found")
                    page.screenshot(path=f"error-{int(time.time())}.png")
                    raise
                
                title = page.title()
                if not title:
                    raise ValueError("Page title is empty")
                
                content = page.locator('[data-testid="content"]').inner_text()
                if not content.strip():
                    raise ValueError("Page content is empty")
                
                return {"title": title, "content": content}
                
        except Exception as e:
            logging.error(f"Error on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)
                logging.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
                continue
            raise
    
    raise Exception(f"Failed after {max_retries} attempts")
```

## Command-Line Interface

### Browser Management

```bash
# Check browser status
python -m playwrightauthor status

# Clear browser cache
python -m playwrightauthor clear-cache

# Run diagnostics
python -m playwrightauthor diagnose
```

### Profile Management

```bash
# List profiles
python -m playwrightauthor profile list

# Create profile
python -m playwrightauthor profile create myprofile

# Show profile details
python -m playwrightauthor profile show myprofile

# Delete profile
python -m playwrightauthor profile delete myprofile

# Clear all profiles
python -m playwrightauthor profile clear
```

### Configuration

```bash
# Show current configuration
python -m playwrightauthor config show

# Show version info
python -m playwrightauthor version
```

All commands support `--json` output and `--verbose` logging.

## Developer workflow

1. **Read** `WORK.md` & `PLAN.md` before coding.

2. **Iterate** in minimal, self-contained commits.

3. After Python changes run:

   ```bash
   fd -e py -x uvx autoflake -i {}; \
   fd -e py -x uvx pyupgrade --py312-plus {}; \
   fd -e py -x uvx ruff check --output-format=github --fix --unsafe-fixes {}; \
   fd -e py -x uvx ruff format --respect-gitignore --target-version py312 {}; \
   python -m pytest
   ```

4. Update `CHANGELOG.md`, tick items in `TODO.md`, push.

5. End sessions with **"Wait, but"** → reflect → refine → push again.

## Package Architecture

```
src/playwrightauthor/
├── __init__.py              # Public API exports (Browser, AsyncBrowser)
├── __main__.py              # CLI entry point
├── author.py                # Core Browser context managers
├── browser_manager.py       # Legacy browser management
├── cli.py                   # CLI with rich output
├── config.py                # Configuration management
├── connection.py            # Connection health and diagnostics
├── exceptions.py           # Custom exceptions
├── lazy_imports.py         # Performance optimization
├── onboarding.py           # User authentication guidance
├── state_manager.py        # Persistent state management
├── typing.py               # Type definitions
├── browser/                # Modular browser management
│   ├── __init__.py
│   ├── finder.py           # Chrome discovery
│   ├── installer.py        # Chrome installation
│   ├── launcher.py         # Browser launching
│   └── process.py          # Process management
├── templates/
│   └── onboarding.html     # User guidance interface
└── utils/
    ├── logger.py           # Logging configuration
    └── paths.py            # Path management

tests/
├── test_author.py          # Core functionality tests
├── test_benchmark.py       # Performance benchmarks
├── test_integration.py     # Integration tests
├── test_platform_specific.py # Platform-specific tests
└── test_utils.py           # Utility function tests
```

## Key Components

### Core API
- `Browser()` - Synchronous context manager
- `AsyncBrowser()` - Asynchronous context manager

Both return standard Playwright browser objects.

### Browser Management
- **Automatic Discovery**: Cross-platform Chrome detection
- **Smart Installation**: Downloads Chrome for Testing from official endpoints
- **Process Management**: Handles browser launching and cleanup
- **Profile Persistence**: Maintains authentication across sessions

### Configuration System
- **Environment Variables**: `PLAYWRIGHTAUTHOR_*` prefix
- **State Management**: Caches browser paths
- **Profile Support**: Multiple named profiles

## Troubleshooting

### `BrowserManagerError: Could not find Chrome executable...`

PlaywrightAuthor couldn't find Chrome for Testing. Solutions:
- Let it install automatically (downloads on first run)
- Install manually: `npx puppeteer browsers install chrome`

### `playwright._impl._api_types.Error: Target page, context or browser has been closed`

Browser closed during script execution. Happens when:
- You manually close the browser window
- Browser crashes

Run script with `--verbose` flag for more information.

## Contributing

Pull requests welcome. Follow coding principles in `README.md`, keep file headers accurate, and end PRs with a "Wait, but" reflection.

## License

MIT – see `LICENSE`.

## Wait, but…

**Reflection & refinements**

* Refocused from specific scraper to general-purpose Playwright convenience library
* Class-based core API (`Browser`, `AsyncBrowser`) for Pythonic feel
* Updated file layout and CLI to match new scope
* Generalized onboarding HTML to be site-agnostic
* All snippets align with providing zero-setup, authenticated browser access

(End of iteration – ready for review.)