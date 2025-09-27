# Advanced Features

PlaywrightAuthor provides advanced features for complex automation scenarios, including async operations, performance monitoring, custom configurations, and browser management.

## Asynchronous Operations

### Basic Async Usage

```python
import asyncio
from playwrightauthor import AsyncBrowser

async def async_automation():
    async with AsyncBrowser() as browser:
        page = await browser.new_page()
        await page.goto("https://example.com")
        title = await page.title()
        print(f"Page title: {title}")

# Run async automation
asyncio.run(async_automation())
```

### Concurrent Page Operations

```python
import asyncio
from playwrightauthor import AsyncBrowser

async def process_page(browser, url: str):
    """Process a single page"""
    page = await browser.new_page()
    await page.goto(url)
    title = await page.title()
    await page.close()
    return {"url": url, "title": title}

async def concurrent_automation():
    """Process multiple pages concurrently"""
    urls = [
        "https://github.com",
        "https://stackoverflow.com",
        "https://python.org",
        "https://playwright.dev"
    ]
    
    async with AsyncBrowser() as browser:
        # Process all URLs concurrently
        tasks = [process_page(browser, url) for url in urls]
        results = await asyncio.gather(*tasks)
        
        for result in results:
            print(f"{result['url']}: {result['title']}")

asyncio.run(concurrent_automation())
```

### Async Context Managers

```python
from playwrightauthor import AsyncBrowser
from contextlib import asynccontextmanager

@asynccontextmanager
async def managed_page(browser):
    """Custom async context manager for pages"""
    page = await browser.new_page()
    try:
        yield page
    finally:
        await page.close()

async def advanced_async():
    async with AsyncBrowser() as browser:
        async with managed_page(browser) as page:
            await page.goto("https://example.com")
            # Page automatically closed when exiting context

asyncio.run(advanced_async())
```

## Performance Monitoring

### Built-in Monitoring

```python
from playwrightauthor import Browser
from playwrightauthor.monitoring import PerformanceMonitor

with Browser() as browser:
    monitor = PerformanceMonitor(browser)
    
    # Start monitoring
    monitor.start()
    
    page = browser.new_page()
    page.goto("https://example.com")
    
    # Get performance metrics
    metrics = monitor.get_metrics()
    print(f"Page load time: {metrics['navigation_time']}ms")
    print(f"Memory usage: {metrics['memory_usage']}MB")
    print(f"CPU usage: {metrics['cpu_usage']}%")
    
    monitor.stop()
```

### Custom Performance Tracking

```python
from playwrightauthor import Browser
import time
from typing import Dict, Any

class CustomPerformanceTracker:
    def __init__(self):
        self.metrics: Dict[str, Any] = {}
        self.start_time = None
    
    def start_tracking(self):
        """Start performance tracking"""
        self.start_time = time.time()
        self.metrics = {
            "operations": [],
            "errors": [],
            "timings": {}
        }
    
    def track_operation(self, name: str, duration: float):
        """Track individual operation"""
        self.metrics["operations"].append({
            "name": name,
            "duration": duration,
            "timestamp": time.time()
        })
    
    def track_error(self, error: Exception, context: str):
        """Track errors with context"""
        self.metrics["errors"].append({
            "error": str(error),
            "context": context,
            "timestamp": time.time()
        })
    
    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        total_time = time.time() - self.start_time
        operations = self.metrics["operations"]
        
        return {
            "total_time": total_time,
            "operation_count": len(operations),
            "error_count": len(self.metrics["errors"]),
            "avg_operation_time": sum(op["duration"] for op in operations) / len(operations) if operations else 0,
            "slowest_operation": max(operations, key=lambda x: x["duration"]) if operations else None
        }

# Usage
tracker = CustomPerformanceTracker()
tracker.start_tracking()

with Browser() as browser:
    page = browser.new_page()
    
    # Track page navigation
    start = time.time()
    page.goto("https://example.com")
    tracker.track_operation("navigation", time.time() - start)
    
    # Track form interaction
    start = time.time()
    try:
        page.fill("#search", "playwright")
        page.click("#submit")
        tracker.track_operation("form_submit", time.time() - start)
    except Exception as e:
        tracker.track_error(e, "form_interaction")

summary = tracker.get_summary()
print(f"Performance Summary: {summary}")
```

## Advanced Browser Configuration

### Custom Browser Factory

```python
from playwrightauthor import BrowserConfig
from playwrightauthor.browser_manager import BrowserManager
from typing import Optional

class AdvancedBrowserFactory:
    """Factory for creating specialized browser configurations"""
    
    @staticmethod
    def create_headless_config() -> BrowserConfig:
        """Optimized headless configuration"""
        return BrowserConfig(
            headless=True,
            chrome_args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-extensions",
                "--disable-plugins",
                "--disable-images",  # Faster loading
                "--disable-javascript",  # If JS not needed
            ]
        )
    
    @staticmethod
    def create_mobile_config(device: str = "iPhone 12") -> BrowserConfig:
        """Mobile device emulation configuration"""
        mobile_args = [
            "--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X)",
            "--window-size=390,844",
            "--device-scale-factor=3"
        ]
        
        return BrowserConfig(
            headless=False,
            chrome_args=mobile_args,
            viewport={"width": 390, "height": 844}
        )
    
    @staticmethod
    def create_debug_config() -> BrowserConfig:
        """Development and debugging configuration"""
        return BrowserConfig(
            headless=False,
            timeout=60000,
            chrome_args=[
                "--auto-open-devtools-for-tabs",
                "--disable-web-security",
                "--allow-running-insecure-content",
                "--remote-debugging-port=9223"  # Different port for debugging
            ]
        )
    
    @staticmethod
    def create_stealth_config() -> BrowserConfig:
        """Stealth configuration to avoid detection"""
        return BrowserConfig(
            headless=True,
            chrome_args=[
                "--disable-blink-features=AutomationControlled",
                "--exclude-switches=enable-automation",
                "--disable-extensions-except=",
                "--disable-plugins-discovery",
                "--no-first-run",
                "--no-service-autorun",
                "--password-store=basic",
                "--use-mock-keychain"
            ]
        )

# Usage
from playwrightauthor import Browser

# Use mobile configuration
mobile_config = AdvancedBrowserFactory.create_mobile_config()
with Browser(config=mobile_config) as browser:
    page = browser.new_page()
    page.goto("https://example.com")

# Use stealth configuration
stealth_config = AdvancedBrowserFactory.create_stealth_config()
with Browser(config=stealth_config) as browser:
    page = browser.new_page()
    page.goto("https://example.com")
```

### Dynamic Configuration

```python
import os
from playwrightauthor import BrowserConfig

class DynamicConfig:
    """Dynamic configuration based on environment and runtime conditions"""
    
    def __init__(self):
        self.base_config = BrowserConfig()
    
    def get_config(self) -> BrowserConfig:
        """Get configuration based on current environment"""
        config = self.base_config
        
        # CI/CD environment
        if os.getenv("CI"):
            config = self._apply_ci_settings(config)
        
        # Docker environment
        if os.path.exists("/.dockerenv"):
            config = self._apply_docker_settings(config)
        
        # Development environment
        if os.getenv("NODE_ENV") == "development":
            config = self._apply_dev_settings(config)
        
        # Production environment
        if os.getenv("NODE_ENV") == "production":
            config = self._apply_prod_settings(config)
        
        return config
    
    def _apply_ci_settings(self, config: BrowserConfig) -> BrowserConfig:
        """Apply CI-specific settings"""
        config.headless = True
        config.timeout = 15000  # Faster timeouts in CI
        config.chrome_args.extend([
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu"
        ])
        return config
    
    def _apply_docker_settings(self, config: BrowserConfig) -> BrowserConfig:
        """Apply Docker-specific settings"""
        config.chrome_args.extend([
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-setuid-sandbox"
        ])
        return config
    
    def _apply_dev_settings(self, config: BrowserConfig) -> BrowserConfig:
        """Apply development settings"""
        config.headless = False
        config.timeout = 60000  # Longer timeouts for debugging
        config.chrome_args.append("--auto-open-devtools-for-tabs")
        return config
    
    def _apply_prod_settings(self, config: BrowserConfig) -> BrowserConfig:
        """Apply production settings"""
        config.headless = True
        config.timeout = 30000
        config.chrome_args.extend([
            "--disable-logging",
            "--silent",
            "--no-default-browser-check"
        ])
        return config

# Usage
dynamic_config = DynamicConfig()
config = dynamic_config.get_config()

with Browser(config=config) as browser:
    page = browser.new_page()
    page.goto("https://example.com")
```

## Custom Extension System

### Plugin Architecture

```python
from abc import ABC, abstractmethod
from playwrightauthor import Browser
from typing import Any, Dict

class BrowserPlugin(ABC):
    """Base class for browser plugins"""
    
    def __init__(self, browser: Browser):
        self.browser = browser
    
    @abstractmethod
    def setup(self) -> None:
        """Setup plugin"""
        pass
    
    @abstractmethod
    def teardown(self) -> None:
        """Cleanup plugin"""
        pass

class ScreenshotPlugin(BrowserPlugin):
    """Plugin for automatic screenshot capture"""
    
    def __init__(self, browser: Browser, output_dir: str = "screenshots"):
        super().__init__(browser)
        self.output_dir = Path(output_dir)
        self.screenshot_count = 0
    
    def setup(self):
        """Setup screenshot directory"""
        self.output_dir.mkdir(exist_ok=True)
    
    def capture_screenshot(self, name: str = None) -> str:
        """Capture screenshot with auto-naming"""
        if not name:
            name = f"screenshot_{self.screenshot_count:04d}"
        
        screenshot_path = self.output_dir / f"{name}.png"
        
        # Get active page
        pages = self.browser.contexts[0].pages
        if pages:
            pages[0].screenshot(path=str(screenshot_path))
            self.screenshot_count += 1
            return str(screenshot_path)
        
        return None
    
    def teardown(self):
        """Cleanup if needed"""
        pass

class NetworkMonitorPlugin(BrowserPlugin):
    """Plugin for network request monitoring"""
    
    def __init__(self, browser: Browser):
        super().__init__(browser)
        self.requests = []
        self.responses = []
    
    def setup(self):
        """Setup network monitoring"""
        def handle_request(request):
            self.requests.append({
                "url": request.url,
                "method": request.method,
                "headers": request.headers,
                "timestamp": time.time()
            })
        
        def handle_response(response):
            self.responses.append({
                "url": response.url,
                "status": response.status,
                "headers": response.headers,
                "timestamp": time.time()
            })
        
        # Attach listeners to all contexts
        for context in self.browser.contexts:
            context.on("request", handle_request)
            context.on("response", handle_response)
    
    def get_network_summary(self) -> Dict[str, Any]:
        """Get network activity summary"""
        return {
            "total_requests": len(self.requests),
            "total_responses": len(self.responses),
            "failed_requests": len([r for r in self.responses if r["status"] >= 400]),
            "domains": list(set(urllib.parse.urlparse(r["url"]).netloc for r in self.requests))
        }
    
    def teardown(self):
        """Cleanup listeners"""
        pass

# Plugin Manager
class PluginManager:
    def __init__(self, browser: Browser):
        self.browser = browser
        self.plugins: Dict[str, BrowserPlugin] = {}
    
    def register_plugin(self, name: str, plugin: BrowserPlugin):
        """Register a plugin"""
        self.plugins[name] = plugin
        plugin.setup()
    
    def get_plugin(self, name: str) -> BrowserPlugin:
        """Get plugin by name"""
        return self.plugins.get(name)
    
    def teardown_all(self):
        """Teardown all plugins"""
        for plugin in self.plugins.values():
            plugin.teardown()

# Usage
with Browser() as browser:
    plugin_manager = PluginManager(browser)
    
    # Register plugins
    plugin_manager.register_plugin("screenshots", ScreenshotPlugin(browser))
    plugin_manager.register_plugin("network", NetworkMonitorPlugin(browser))
    
    # Use browser with plugins
    page = browser.new_page()
    page.goto("https://example.com")
    
    # Use screenshot plugin
    screenshot_plugin = plugin_manager.get_plugin("screenshots")
    screenshot_plugin.capture_screenshot("homepage")
    
    # Use network plugin
    network_plugin = plugin_manager.get_plugin("network")
    summary = network_plugin.get_network_summary()
    print(f"Network summary: {summary}")
    
    # Cleanup
    plugin_manager.teardown_all()
```

## Advanced Error Handling and Recovery

### Robust Error Recovery

```python
from playwrightauthor import Browser
from playwrightauthor.exceptions import BrowserError, ConnectionError
import time
from typing import Callable, Any

class RobustAutomation:
    """Automation class with advanced error handling and recovery"""
    
    def __init__(self, max_retries: int = 3, retry_delay: float = 2.0):
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    def with_retry(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with retry logic"""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                if attempt < self.max_retries:
                    print(f"Attempt {attempt + 1} failed: {e}")
                    print(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                    self.retry_delay *= 1.5  # Exponential backoff
                else:
                    print(f"All {self.max_retries + 1} attempts failed")
                    raise last_exception
    
    def safe_goto(self, page, url: str, timeout: int = 30000):
        """Navigate with error recovery"""
        def _goto():
            page.goto(url, timeout=timeout, wait_until="networkidle")
            return page.url
        
        return self.with_retry(_goto)
    
    def safe_click(self, page, selector: str, timeout: int = 10000):
        """Click with error recovery"""
        def _click():
            page.wait_for_selector(selector, timeout=timeout)
            page.click(selector)
            return True
        
        return self.with_retry(_click)
    
    def safe_fill(self, page, selector: str, text: str, timeout: int = 10000):
        """Fill form field with error recovery"""
        def _fill():
            page.wait_for_selector(selector, timeout=timeout)
            page.fill(selector, text)
            return True
        
        return self.with_retry(_fill)

# Usage
robust = RobustAutomation(max_retries=3)

with Browser() as browser:
    page = browser.new_page()
    
    # Robust navigation
    robust.safe_goto(page, "https://example.com")
    
    # Robust interactions
    robust.safe_click(page, "#submit-button")
    robust.safe_fill(page, "#search-input", "playwright automation")
```

### Circuit Breaker Pattern

```python
import time
from enum import Enum
from typing import Callable, Any

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, don't attempt
    HALF_OPEN = "half_open"  # Testing if recovered

class CircuitBreaker:
    """Circuit breaker for browser operations"""
    
    def __init__(self, failure_threshold: int = 5, timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function through circuit breaker"""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        return (time.time() - self.last_failure_time) >= self.timeout
    
    def _on_success(self):
        """Handle successful operation"""
        self.failure_count = 0
        self.state = CircuitState.CLOSED
    
    def _on_failure(self):
        """Handle failed operation"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN

# Usage
circuit_breaker = CircuitBreaker(failure_threshold=3, timeout=30.0)

def risky_browser_operation():
    """Some operation that might fail"""
    with Browser() as browser:
        page = browser.new_page()
        page.goto("https://unreliable-site.com")
        return page.title()

try:
    result = circuit_breaker.call(risky_browser_operation)
    print(f"Result: {result}")
except Exception as e:
    print(f"Operation failed: {e}")
```

## Advanced Scraping Patterns

### Pagination Handler

```python
from playwrightauthor import Browser
from typing import Generator, Dict, Any

class PaginationScraper:
    """Advanced pagination handling"""
    
    def __init__(self, browser: Browser):
        self.browser = browser
    
    def scrape_paginated_data(
        self,
        start_url: str,
        data_selector: str,
        next_button_selector: str,
        max_pages: int = None
    ) -> Generator[Dict[str, Any], None, None]:
        """Scrape data from paginated results"""
        page = self.browser.new_page()
        page.goto(start_url)
        
        page_count = 0
        
        while True:
            # Scrape current page
            elements = page.query_selector_all(data_selector)
            
            for element in elements:
                yield self._extract_data(element)
            
            page_count += 1
            
            # Check if we've reached max pages
            if max_pages and page_count >= max_pages:
                break
            
            # Try to navigate to next page
            next_button = page.query_selector(next_button_selector)
            if not next_button or not next_button.is_enabled():
                break
            
            # Click next button and wait for navigation
            next_button.click()
            page.wait_for_load_state("networkidle")
        
        page.close()
    
    def _extract_data(self, element) -> Dict[str, Any]:
        """Extract data from a single element"""
        return {
            "text": element.text_content(),
            "html": element.inner_html(),
            "attributes": element.evaluate("el => Object.fromEntries(Array.from(el.attributes).map(attr => [attr.name, attr.value]))")
        }

# Usage
with Browser() as browser:
    scraper = PaginationScraper(browser)
    
    for item in scraper.scrape_paginated_data(
        start_url="https://example.com/search?q=playwright",
        data_selector=".search-result",
        next_button_selector=".next-page",
        max_pages=5
    ):
        print(f"Item: {item}")
```

### Infinite Scroll Handler

```python
class InfiniteScrollScraper:
    """Handle infinite scroll pages"""
    
    def __init__(self, browser: Browser):
        self.browser = browser
    
    def scrape_infinite_scroll(
        self,
        url: str,
        item_selector: str,
        scroll_pause_time: float = 2.0,
        max_scrolls: int = None
    ) -> Generator[Dict[str, Any], None, None]:
        """Scrape data from infinite scroll page"""
        page = self.browser.new_page()
        page.goto(url)
        
        last_height = 0
        scroll_count = 0
        
        while True:
            # Get current items
            items = page.query_selector_all(item_selector)
            
            # Yield new items
            for item in items:
                yield self._extract_data(item)
            
            # Scroll to bottom
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            
            # Wait for new content to load
            time.sleep(scroll_pause_time)
            
            # Check if new content loaded
            new_height = page.evaluate("document.body.scrollHeight")
            
            if new_height == last_height:
                # No new content, we've reached the end
                break
            
            last_height = new_height
            scroll_count += 1
            
            # Check max scrolls limit
            if max_scrolls and scroll_count >= max_scrolls:
                break
        
        page.close()

# Usage
with Browser() as browser:
    scraper = InfiniteScrollScraper(browser)
    
    for item in scraper.scrape_infinite_scroll(
        url="https://example.com/infinite-feed",
        item_selector=".feed-item",
        max_scrolls=10
    ):
        print(f"Feed item: {item}")
```

## Next Steps

- Check [Troubleshooting](troubleshooting.md) for advanced debugging techniques
- Review [API Reference](api-reference.md) for detailed method documentation
- Learn about [Contributing](contributing.md) to extend PlaywrightAuthor
- Explore real-world examples in the project repository