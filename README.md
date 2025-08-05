# PlaywrightAuthor

*Your personal, authenticated browser for Playwright, ready in one line of code.*

PlaywrightAuthor is a convenience package for **Microsoft Playwright**. It handles the tedious parts of browser automation: finding and launching a **Chrome for Testing** instance, keeping it authenticated with your user profile, and connecting Playwright to it. All you need to do is instantiate a class, and you get a ready-to-use `Browser` object. This lets you focus on writing your automation script, not on the boilerplate.

**Note**: PlaywrightAuthor exclusively uses Chrome for Testing (not regular Chrome) because Google has recently disabled CDP automation with user profiles in regular Chrome. Chrome for Testing is the official Google build specifically designed for automation.

The core idea is to let you do this:

```python
from playwrightauthor import Browser

with Browser() as browser:
    # you get a standard Playwright browser object
    # that is already connected to a logged-in browser
    page = browser.new_page()
    page.goto("https://github.com/me")
    print(f"Welcome, {page.locator('.user-profile-name').inner_text()}!")
```

---

## Contents

* [Features](#features)
* [Quick‑start](#quick-start)
* [Developer workflow](#developer-workflow)
* [Package layout](#package-layout) – **file tree, code snippet, explanation & rationale for every file**
* [Contributing](#contributing)
* [License](#license)

---

## Features

### ✨ **Zero-Configuration Browser Automation**
- **Automatic Chrome Management**: Discovers, installs, and launches Chrome for Testing with remote debugging enabled
- **Persistent Authentication**: Maintains user sessions across script runs using persistent browser profiles
- **Cross-Platform Support**: Works seamlessly on Windows, macOS, and Linux with optimized Chrome discovery

### 🚀 **Performance & Reliability**
- **Lazy Loading**: Optimized startup time with on-demand module imports
- **Connection Health Monitoring**: Comprehensive diagnostics and automatic retry logic
- **State Management**: Intelligent caching of browser paths and configuration for faster subsequent runs
- **Error Recovery**: Graceful handling of browser crashes with automatic restart capabilities

### 🛠 **Developer Experience**
- **Simple API**: Clean `Browser()` and `AsyncBrowser()` context managers
- **Rich CLI Interface**: Comprehensive command-line tools for browser and profile management
- **Type Safety**: 100% type-hinted codebase with full mypy compatibility
- **Comprehensive Testing**: Extensive test suite with CI/CD pipeline on multiple platforms

### 📋 **Advanced Management**
- **Profile System**: Create, manage, and switch between multiple browser profiles
- **Configuration Management**: Environment variable support and flexible configuration options
- **Diagnostic Tools**: Built-in troubleshooting and system health checks
- **JSON Output**: Machine-readable output formats for automation and scripting

---

## Installation

```bash
# Install PlaywrightAuthor
pip install playwrightauthor

# Install Playwright browsers (required)
playwright install chromium
```

## Quick start

```bash
# Create your script file
cat > example.py << 'EOF'
from playwrightauthor import Browser

with Browser() as browser:
    page = browser.new_page()
    page.goto("https://github.com")
    print(f"Page title: {page.title()}")
EOF

# Run your script
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

---

## Common Patterns

### Authentication Workflow

The most common use case is automating authenticated services. PlaywrightAuthor makes this seamless by maintaining persistent login sessions:

```python
from playwrightauthor import Browser

# First run: You'll need to manually log in
with Browser(profile="work") as browser:
    page = browser.new_page()
    page.goto("https://mail.google.com")
    
    # If not logged in, the page will show the login screen
    # Complete the login manually in the browser window
    # PlaywrightAuthor will save the session for future runs
    
    print(f"Logged in as: {page.locator('[data-testid=user-email]').inner_text()}")

# Subsequent runs: Automatic authentication
with Browser(profile="work") as browser:
    page = browser.new_page() 
    page.goto("https://mail.google.com")
    # You're automatically logged in!
    inbox_count = page.locator('[data-testid=inbox-count]').inner_text()
    print(f"You have {inbox_count} unread emails")
```

### Error Handling and Retry Pattern

For production automation, implement robust error handling:

```python
from playwrightauthor import Browser
from playwright.sync_api import TimeoutError
import time

def scrape_with_retry(url, max_retries=3):
    """Robust scraping with automatic retry and error handling."""
    
    for attempt in range(max_retries):
        try:
            with Browser(verbose=attempt > 0) as browser:  # Enable logging on retries
                page = browser.new_page()
                
                # Set reasonable timeouts
                page.set_default_timeout(30000)  # 30 seconds
                
                page.goto(url)
                
                # Wait for content to load
                page.wait_for_selector('[data-testid=content]', timeout=10000)
                
                title = page.title()
                content = page.locator('[data-testid=content]').inner_text()
                
                return {"title": title, "content": content}
                
        except TimeoutError:
            print(f"Attempt {attempt + 1} timed out, retrying...")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
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

### Profile Management for Multiple Accounts

Use profiles to manage multiple accounts or environments:

```python
from playwrightauthor import Browser

# Define your environments
profiles = {
    "work": "work@company.com",
    "personal": "me@gmail.com", 
    "testing": "test@example.com"
}

def check_email_for_all_accounts():
    """Check email counts across all accounts."""
    results = {}
    
    for profile_name, email in profiles.items():
        try:
            with Browser(profile=profile_name) as browser:
                page = browser.new_page()
                page.goto("https://mail.google.com")
                
                # Each profile maintains its own authentication
                unread_count = page.locator('[aria-label="Inbox"]').get_attribute('data-count')
                results[email] = int(unread_count or 0)
                
        except Exception as e:
            print(f"Failed to check {email}: {e}")
            results[email] = None
    
    return results

# Usage
email_counts = check_email_for_all_accounts()
for email, count in email_counts.items():
    if count is not None:
        print(f"{email}: {count} unread emails")
    else:
        print(f"{email}: Failed to check")
```

### Interactive Development with REPL

Use the interactive REPL for development and debugging:

```bash
# Start the interactive REPL
python -m playwrightauthor repl

# In the REPL, you can interactively explore:
>>> page = browser.new_page()
>>> page.goto("https://github.com")
>>> page.title()
'GitHub: Let's build from here · GitHub'

>>> # Test selectors interactively
>>> page.locator('h1').inner_text()
'Let's build from here'

>>> # Run CLI commands without leaving REPL
>>> !status
Browser is ready.
  - Path: /Users/user/.playwrightauthor/chrome/chrome
  - User Data: /Users/user/.playwrightauthor/profiles/default

>>> # Switch profiles on the fly
>>> exit()  # Exit current browser
>>> browser = Browser(profile="work").__enter__()
>>> page = browser.new_page()
>>> page.goto("https://mail.google.com")
```

### Async for High Performance

Use AsyncBrowser for concurrent operations:

```python
import asyncio
from playwrightauthor import AsyncBrowser

async def scrape_multiple_pages(urls):
    """Scrape multiple pages concurrently."""
    
    async def scrape_single_page(url):
        async with AsyncBrowser() as browser:
            page = await browser.new_page()
            await page.goto(url)
            title = await page.title()
            return {"url": url, "title": title}
    
    # Run up to 5 concurrent scraping tasks
    semaphore = asyncio.Semaphore(5)
    
    async def limited_scrape(url):
        async with semaphore:
            return await scrape_single_page(url)
    
    tasks = [limited_scrape(url) for url in urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    return results

# Usage
urls = [
    "https://github.com",
    "https://stackoverflow.com", 
    "https://python.org",
    "https://docs.python.org",
    "https://pypi.org"
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

**Most Common Commands:**
```bash
# Check if everything is working
python -m playwrightauthor status

# Start interactive development
python -m playwrightauthor repl

# Fix connection issues
python -m playwrightauthor diagnose

# Clean slate (removes all data)
python -m playwrightauthor clear-cache
```

**Most Common Code Patterns:**
```python
# Basic automation
with Browser() as browser:
    page = browser.new_page()
    page.goto("https://example.com")

# Multiple accounts
with Browser(profile="work") as browser:
    # Work automation

# High performance
async with AsyncBrowser() as browser:
    # Async automation
```

---

## Best Practices

### Resource Management and Cleanup

Always use context managers to ensure proper resource cleanup:

```python
from playwrightauthor import Browser

# ✅ GOOD: Context manager ensures cleanup
with Browser() as browser:
    page = browser.new_page()
    page.goto("https://example.com")
    # Browser automatically cleaned up

# ❌ BAD: Manual cleanup required
browser = Browser().__enter__()
page = browser.new_page()
page.goto("https://example.com")
# Memory leak! Browser not cleaned up
```

**Page Lifecycle Management:**
```python
with Browser() as browser:
    # Create pages as needed
    page1 = browser.new_page()
    page2 = browser.new_page()
    
    # Close pages when done to free memory
    page1.close()
    page2.close()
    
    # Or use page context managers
    page = browser.new_page()
    try:
        page.goto("https://example.com")
        # Work with page
    finally:
        page.close()
```

### Performance Optimization

**For Large-Scale Automation:**

```python
from playwrightauthor import AsyncBrowser
import asyncio

async def optimize_for_performance():
    """High-performance automation patterns."""
    
    # Use connection pooling for multiple operations
    async with AsyncBrowser() as browser:
        # Reuse browser context across multiple pages
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Your-Bot/1.0"
        )
        
        # Concurrent page processing with rate limiting
        semaphore = asyncio.Semaphore(5)  # Max 5 concurrent pages
        
        async def process_url(url):
            async with semaphore:
                page = await context.new_page()
                try:
                    await page.goto(url, wait_until="domcontentloaded")
                    # Process page content
                    title = await page.title()
                    return {"url": url, "title": title}
                finally:
                    await page.close()
        
        # Process multiple URLs concurrently
        urls = ["https://example1.com", "https://example2.com", "https://example3.com"]
        results = await asyncio.gather(*[process_url(url) for url in urls])
        
        await context.close()
        return results

# Run the optimized automation
results = asyncio.run(optimize_for_performance())
```

**Memory Management:**
```python
from playwrightauthor import Browser

def memory_efficient_scraping(urls):
    """Process many URLs without memory leaks."""
    
    results = []
    with Browser() as browser:
        # Process in batches to control memory usage
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
                    page.close()  # Critical: free page memory
    
    return results
```

### Security Considerations

**Profile and Credential Management:**

```python
from playwrightauthor import Browser
from pathlib import Path
import os

def secure_automation_setup():
    """Security best practices for browser automation."""
    
    # Use dedicated profiles for different security contexts
    profiles = {
        "production": "prod-automation",
        "staging": "staging-test", 
        "development": "dev-local"
    }
    
    environment = os.getenv("ENVIRONMENT", "development")
    profile_name = profiles.get(environment, "default")
    
    # Use environment-specific configuration
    with Browser(profile=profile_name, verbose=False) as browser:
        page = browser.new_page()
        
        # Set security headers if needed
        page.set_extra_http_headers({
            "User-Agent": "Company-Automation/1.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        })
        
        # Navigate to secure endpoints
        page.goto("https://secure-api.company.com")
        return page.content()

# Environment-based configuration
def get_secure_config():
    """Load configuration securely from environment."""
    return {
        "timeout": int(os.getenv("AUTOMATION_TIMEOUT", "30000")),
        "headless": os.getenv("AUTOMATION_HEADLESS", "false").lower() == "true",
        "profile": os.getenv("AUTOMATION_PROFILE", "default")
    }
```

**Sensitive Data Handling:**
```python
from playwrightauthor import Browser
import logging

# Configure logging to avoid sensitive data leaks
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/automation.log'),
        logging.StreamHandler()
    ]
)

def secure_login_automation():
    """Handle authentication securely."""
    
    with Browser(profile="secure-profile", verbose=False) as browser:
        page = browser.new_page()
        
        # Navigate to login page
        page.goto("https://app.example.com/login")
        
        # Use environment variables for credentials (never hardcode)
        username = os.getenv("APP_USERNAME")
        password = os.getenv("APP_PASSWORD")
        
        if not username or not password:
            raise ValueError("Credentials not found in environment variables")
        
        # Fill credentials (never log sensitive data)
        page.fill('[name="username"]', username)
        page.fill('[name="password"]', password)
        
        # Log non-sensitive information only
        logging.info("Attempting login for user authentication")
        
        page.click('[type="submit"]')
        page.wait_for_url("**/dashboard")
        
        logging.info("Authentication successful")
        
        return page
```

### Configuration Management

**Production Configuration:**
```python
from playwrightauthor.config import PlaywrightAuthorConfig, BrowserConfig, NetworkConfig, LoggingConfig
from pathlib import Path

def create_production_config():
    """Production-ready configuration."""
    
    return PlaywrightAuthorConfig(
        browser=BrowserConfig(
            headless=True,  # No UI in production
            timeout=45000,  # Longer timeout for stability
            viewport_width=1920,
            viewport_height=1080,
            args=[
                "--no-sandbox",  # Required in containers
                "--disable-dev-shm-usage",  # Prevent memory issues
                "--disable-gpu",  # Not needed in headless
            ]
        ),
        network=NetworkConfig(
            retry_attempts=5,  # More retries for reliability
            download_timeout=600,  # 10 minutes for large downloads
            exponential_backoff=True,
            proxy=os.getenv("HTTPS_PROXY")  # Corporate proxy support
        ),
        logging=LoggingConfig(
            verbose=False,  # Reduce log noise
            log_level="INFO",
            log_file=Path("/var/log/playwrightauthor.log"),
            log_format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
        ),
        enable_lazy_loading=True,  # Faster startup
        default_profile="production"
    )

# Apply production configuration
config = create_production_config()
from playwrightauthor.config import save_config
save_config(config)
```

**Environment Variables Setup:**
```bash
# Production environment setup
export PLAYWRIGHTAUTHOR_HEADLESS=true
export PLAYWRIGHTAUTHOR_TIMEOUT=45000
export PLAYWRIGHTAUTHOR_VERBOSE=false
export PLAYWRIGHTAUTHOR_LOG_LEVEL=INFO
export PLAYWRIGHTAUTHOR_RETRY_ATTEMPTS=5

# Credentials (never hardcode these)
export APP_USERNAME=your-automation-user
export APP_PASSWORD=secure-password-from-secrets-manager

# Network configuration
export HTTPS_PROXY=http://proxy.company.com:8080
export PLAYWRIGHTAUTHOR_PROXY=http://proxy.company.com:8080
```

### Error Handling Best Practices

**Comprehensive Error Handling:**
```python
from playwrightauthor import Browser
from playwright.sync_api import TimeoutError, Error as PlaywrightError
import logging
import time

def robust_automation_with_error_handling():
    """Production-grade error handling patterns."""
    
    max_retries = 3
    base_delay = 1.0
    
    for attempt in range(max_retries):
        try:
            with Browser(verbose=attempt > 0) as browser:  # Enable logging on retries
                page = browser.new_page()
                
                # Set reasonable timeouts
                page.set_default_timeout(30000)
                
                # Navigate with error handling
                try:
                    page.goto("https://example.com", wait_until="networkidle")
                except TimeoutError:
                    logging.warning(f"Page load timeout on attempt {attempt + 1}")
                    if attempt < max_retries - 1:
                        continue
                    raise
                
                # Wait for specific elements with error handling
                try:
                    page.wait_for_selector('[data-testid="content"]', timeout=10000)
                except TimeoutError:
                    logging.error("Required content not found on page")
                    # Take screenshot for debugging
                    page.screenshot(path=f"error-{int(time.time())}.png")
                    raise
                
                # Extract data with validation
                title = page.title()
                if not title:
                    raise ValueError("Page title is empty")
                
                content = page.locator('[data-testid="content"]').inner_text()
                if not content.strip():
                    raise ValueError("Page content is empty")
                
                return {"title": title, "content": content}
                
        except PlaywrightError as e:
            logging.error(f"Playwright error on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)  # Exponential backoff
                logging.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
                continue
            raise
        
        except Exception as e:
            logging.error(f"Unexpected error on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                time.sleep(base_delay)
                continue
            raise
    
    raise Exception(f"Failed after {max_retries} attempts")
```

---

## Command-Line Interface

PlaywrightAuthor comes with a comprehensive command-line interface for managing browsers, profiles, and diagnostics.

### Browser Management

```bash
# Check browser status and launch if needed
python -m playwrightauthor status

# Clear browser cache and user data
python -m playwrightauthor clear-cache

# Run comprehensive diagnostics
python -m playwrightauthor diagnose
```

### Profile Management

```bash
# List all browser profiles
python -m playwrightauthor profile list

# Create a new profile
python -m playwrightauthor profile create myprofile

# Show profile details
python -m playwrightauthor profile show myprofile

# Delete a profile
python -m playwrightauthor profile delete myprofile

# Clear all profiles
python -m playwrightauthor profile clear
```

### Configuration

```bash
# Show current configuration
python -m playwrightauthor config show

# Show version and system information
python -m playwrightauthor version
```

All commands support `--json` output format and `--verbose` for detailed logging.

---

## Developer workflow

1. **Read** `WORK.md` & `PLAN.md` before touching code.

2. **Iterate** in minimal, self‑contained commits.

3. After Python changes run:

   ```bash
   fd -e py -x uvx autoflake -i {}; \
   fd -e py -x uvx pyupgrade --py312-plus {}; \
   fd -e py -x uvx ruff check --output-format=github --fix --unsafe-fixes {}; \
   fd -e py -x uvx ruff format --respect-gitignore --target-version py312 {}; \
   python -m pytest
   ```

4. Update `CHANGELOG.md`, tick items in `TODO.md`, push.

5. Always finish a work session with **“Wait, but”** → reflect → refine → push again.

---

## Package Architecture

PlaywrightAuthor follows modern Python packaging standards with a clean `src/` layout and comprehensive testing.

```
src/playwrightauthor/
├── __init__.py              # Public API exports (Browser, AsyncBrowser)
├── __main__.py              # CLI entry point
├── author.py                # Core Browser context managers
├── browser_manager.py       # Legacy browser management (compatibility)
├── cli.py                   # Fire-powered CLI with rich output
├── config.py                # Configuration management system
├── connection.py            # Connection health and diagnostics
├── exceptions.py            # Custom exception classes
├── lazy_imports.py          # Performance optimization for imports
├── onboarding.py            # User authentication guidance
├── state_manager.py         # Persistent state management
├── typing.py                # Type definitions and protocols
├── browser/                 # Modular browser management
│   ├── __init__.py
│   ├── finder.py            # Cross-platform Chrome discovery
│   ├── installer.py         # Chrome for Testing installation
│   ├── launcher.py          # Browser process launching
│   └── process.py           # Process management and control
├── templates/
│   └── onboarding.html      # User guidance interface
└── utils/
    ├── logger.py            # Loguru-based logging configuration
    └── paths.py             # Cross-platform path management

tests/                       # Comprehensive test suite
├── test_author.py           # Core functionality tests
├── test_benchmark.py        # Performance benchmarks
├── test_integration.py      # Integration tests
├── test_platform_specific.py # Platform-specific tests
└── test_utils.py            # Utility function tests
```

## Key Components

### Core API
The library exposes a minimal, clean API through two main classes:
- `Browser()` - Synchronous context manager
- `AsyncBrowser()` - Asynchronous context manager

Both provide identical functionality and return standard Playwright browser objects.

### Browser Management
- **Automatic Discovery**: Finds Chrome installations across Windows, macOS, and Linux
- **Smart Installation**: Downloads Chrome for Testing when needed using official Google endpoints
- **Process Management**: Handles Chrome launching with debug port and graceful cleanup
- **Profile Persistence**: Maintains user authentication across sessions

### Configuration System
- **Environment Variables**: `PLAYWRIGHTAUTHOR_*` prefix for all settings
- **State Management**: Caches browser paths and configuration for performance
- **Profile Support**: Multiple named profiles for different use cases

---
## Troubleshooting

### `BrowserManagerError: Could not find Chrome executable...`

This error means that `playwrightauthor` could not find a Chrome for Testing executable on your system. PlaywrightAuthor requires Chrome for Testing (not regular Chrome) because Google has disabled CDP automation with user profiles in regular Chrome. You can:
- Let PlaywrightAuthor install it automatically (it will download on first run)
- Or install it manually using: `npx puppeteer browsers install chrome`

### `playwright._impl._api_types.Error: Target page, context or browser has been closed`

This error usually means that the browser was closed while your script was running. This can happen if you manually close the browser window, or if the browser crashes. If you are running into this issue, you can try running your script with the `--verbose` flag to get more information.

---

## Contributing

Pull‑requests are welcome! Please follow the **General Coding Principles** in the main `README.md`, keep every file’s `this_file` header accurate, and end each session with a short *“Wait, but”* reflection in your PR description.

---

## License

MIT – *see* `LICENSE`.

---

Wait, but…

**Reflection & tiny refinements**

* Refocused the entire project from a specific scraper to a general-purpose Playwright convenience library.
* The core API is now class-based (`Browser`, `AsyncBrowser`) for a more Pythonic feel.
* Updated the file layout (`author.py`) and CLI (`status` command) to match the new scope.
* Generalized the onboarding HTML to be site-agnostic.
* Ensured all snippets and explanations align with the new vision of providing a zero-setup, authenticated browser.

(End of iteration – ready for review.)