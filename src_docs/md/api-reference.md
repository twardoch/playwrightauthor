# API Reference

Documentation for PlaywrightAuthor classes, methods, and configuration options.

## Core Classes

### Browser

Synchronous browser context manager.

```python
class Browser:
    """Synchronous browser context manager for PlaywrightAuthor."""
    
    def __init__(self, config: BrowserConfig = None, **kwargs):
        """
        Initialize Browser instance.
        
        Args:
            config: Browser configuration object
            **kwargs: Configuration overrides (headless, timeout, etc.)
        """
    
    def __enter__(self) -> playwright.sync_api.Browser:
        """Enter context manager and return Playwright Browser object."""
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager and cleanup resources."""
```

**Example Usage**:
```python
from playwrightauthor import Browser, BrowserConfig

# Basic usage
with Browser() as browser:
    page = browser.new_page()
    page.goto("https://example.com")

# With configuration
config = BrowserConfig(headless=False, timeout=60000)
with Browser(config=config) as browser:
    page = browser.new_page()
    page.goto("https://example.com")

# With keyword arguments
with Browser(headless=True, debug_port=9223) as browser:
    page = browser.new_page()
    page.goto("https://example.com")
```

### AsyncBrowser

Asynchronous browser context manager.

```python
class AsyncBrowser:
    """Asynchronous browser context manager for PlaywrightAuthor."""
    
    def __init__(self, config: BrowserConfig = None, **kwargs):
        """
        Initialize AsyncBrowser instance.
        
        Args:
            config: Browser configuration object
            **kwargs: Configuration overrides
        """
    
    async def __aenter__(self) -> playwright.async_api.Browser:
        """Enter async context manager and return Playwright Browser object."""
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context manager and cleanup resources."""
```

**Example Usage**:
```python
import asyncio
from playwrightauthor import AsyncBrowser

async def main():
    async with AsyncBrowser() as browser:
        page = await browser.new_page()
        await page.goto("https://example.com")
        title = await page.title()
        print(title)

asyncio.run(main())
```

## Configuration

### BrowserConfig

Main configuration class for browser settings.

```python
class BrowserConfig:
    """Configuration class for browser settings."""
    
    def __init__(
        self,
        # Display settings
        headless: bool = True,
        viewport: dict = None,
        
        # Timing settings
        timeout: int = 30000,
        navigation_timeout: int = 30000,
        
        # Chrome settings
        chrome_path: str = None,
        chrome_args: list[str] = None,
        user_data_dir: str = None,
        debug_port: int = 9222,
        
        # Connection settings
        connect_timeout: int = 10000,
        connect_retries: int = 3,
        
        # Feature flags
        ignore_https_errors: bool = False,
        bypass_csp: bool = False,
        
        # Logging
        log_level: str = "INFO",
        log_file: str = None,
        verbose: bool = False,
        
        # Advanced settings
        download_timeout: int = 300,
        install_dir: str = None,
        auto_restart: bool = True,
        health_check_interval: int = 60
    ):
        """
        Initialize browser configuration.
        
        Args:
            headless: Run browser in headless mode
            viewport: Default viewport size {"width": int, "height": int}
            timeout: Default timeout for operations in milliseconds
            navigation_timeout: Timeout for page navigation in milliseconds
            chrome_path: Path to Chrome executable (auto-detected if None)
            chrome_args: Additional Chrome command line arguments
            user_data_dir: Chrome user data directory path
            debug_port: Chrome remote debugging port
            connect_timeout: Timeout for connecting to Chrome in milliseconds
            connect_retries: Number of connection retry attempts
            ignore_https_errors: Ignore SSL certificate errors
            bypass_csp: Bypass Content Security Policy
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
            log_file: Path to log file (stdout if None)
            verbose: Enable verbose logging
            download_timeout: Timeout for Chrome downloads in seconds
            install_dir: Directory for Chrome installation
            auto_restart: Automatically restart Chrome if it crashes
            health_check_interval: Health check interval in seconds
        """
```

**Properties**:
```python
@property
def chrome_executable(self) -> str:
    """Get the Chrome executable path."""

@property
def profile_directory(self) -> str:
    """Get the user profile directory path."""

@property
def cache_directory(self) -> str:
    """Get the cache directory path."""

def to_dict(self) -> dict:
    """Convert configuration to dictionary."""

def update(self, **kwargs) -> 'BrowserConfig':
    """Update configuration with new values."""

def validate(self) -> bool:
    """Validate configuration settings."""
```

**Example Usage**:
```python
from playwrightauthor import BrowserConfig

# Basic configuration
config = BrowserConfig(
    headless=False,
    timeout=60000,
    viewport={"width": 1920, "height": 1080}
)

# Mobile device emulation
mobile_config = BrowserConfig(
    headless=False,
    viewport={"width": 390, "height": 844},
    chrome_args=[
        "--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X)"
    ]
)

# Development configuration
dev_config = BrowserConfig(
    headless=False,
    timeout=120000,
    log_level="DEBUG",
    chrome_args=["--auto-open-devtools-for-tabs"]
)

# Production configuration
prod_config = BrowserConfig(
    headless=True,
    timeout=30000,
    chrome_args=[
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu"
    ]
)
```

## Browser Management

### BrowserManager

Core browser management functionality.

```python
class BrowserManager:
    """Manages Chrome browser lifecycle and connections."""
    
    def __init__(self, config: BrowserConfig):
        """Initialize browser manager with configuration."""
    
    def ensure_browser_available(self) -> str:
        """Ensure Chrome is available and return executable path."""
    
    def launch_browser(self) -> subprocess.Popen:
        """Launch Chrome with debugging enabled."""
    
    def connect_to_browser(self) -> playwright.sync_api.Browser:
        """Connect to Chrome via Playwright."""
    
    def cleanup(self):
        """Cleanup browser resources."""
    
    def is_browser_running(self) -> bool:
        """Check if browser is currently running."""
    
    def restart_browser(self):
        """Restart the browser process."""
```

### ChromeFinder

Chrome installation discovery.

```python
class ChromeFinder:
    """Finds Chrome installations across platforms."""
    
    @staticmethod
    def find_chrome() -> str:
        """Find Chrome executable path."""
    
    @staticmethod
    def get_chrome_locations() -> list[str]:
        """Get list of possible Chrome locations for current platform."""
    
    @staticmethod
    def is_chrome_executable(path: str) -> bool:
        """Check if path is a valid Chrome executable."""
    
    @staticmethod
    def get_chrome_version(path: str) -> str:
        """Get Chrome version from executable."""
```

**Platform-specific locations**:
```python
# Windows locations
WINDOWS_CHROME_PATHS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe",
    # ... more paths
]

# macOS locations  
MACOS_CHROME_PATHS = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "~/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    # ... more paths
]

# Linux locations
LINUX_CHROME_PATHS = [
    "/usr/bin/google-chrome",
    "/usr/bin/google-chrome-stable", 
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
    # ... more paths
]
```

### ChromeInstaller

Chrome for Testing download and installation.

```python
class ChromeInstaller:
    """Downloads and installs Chrome for Testing."""
    
    def __init__(self, install_dir: str = None):
        """Initialize installer with optional install directory."""
    
    def install_latest(self, progress_callback: callable = None) -> str:
        """Download and install latest Chrome for Testing."""
    
    def install_version(self, version: str, progress_callback: callable = None) -> str:
        """Download and install specific Chrome version."""
    
    def get_available_versions(self) -> list[str]:
        """Get list of available Chrome for Testing versions."""
    
    def get_installed_versions(self) -> list[str]:
        """Get list of locally installed Chrome versions."""
    
    def uninstall_version(self, version: str):
        """Remove installed Chrome version."""
    
    def cleanup_old_versions(self, keep_count: int = 3):
        """Remove old Chrome installations, keeping specified count."""
```

**Example Usage**:
```python
from playwrightauthor.browser.installer import ChromeInstaller

installer = ChromeInstaller()

# Install latest Chrome
def progress(downloaded: int, total: int):
    percent = (downloaded / total) * 100
    print(f"Download progress: {percent:.1f}%")

chrome_path = installer.install_latest(progress_callback=progress)
print(f"Chrome installed to: {chrome_path}")

# Install specific version
chrome_path = installer.install_version("119.0.6045.105")

# List available versions
versions = installer.get_available_versions()
print(f"Available versions: {versions[:10]}")  # Show first 10

# Cleanup old installations
installer.cleanup_old_versions(keep_count=2)
```

## Process Management

### ChromeProcessManager

Chrome process lifecycle management.

```python
class ChromeProcessManager:
    """Manages Chrome process lifecycle."""
    
    def __init__(self):
        """Initialize process manager."""
    
    def get_chrome_processes(self) -> list[psutil.Process]:
        """Get list of running Chrome processes."""
    
    def is_chrome_debug_running(self, port: int = 9222) -> bool:
        """Check if Chrome is running with debugging enabled on port."""
    
    def kill_chrome_instances(self, graceful: bool = True):
        """Kill Chrome instances."""
    
    def launch_chrome(
        self, 
        executable_path: str,
        debug_port: int = 9222,
        user_data_dir: str = None,
        args: list[str] = None
    ) -> subprocess.Popen:
        """Launch Chrome with specified parameters."""
    
    def wait_for_chrome_ready(self, port: int = 9222, timeout: int = 30):
        """Wait for Chrome debug server to be ready."""
    
    def is_port_available(self, port: int) -> bool:
        """Check if port is available for use."""
    
    def find_available_port(self, start_port: int = 9222) -> int:
        """Find next available port starting from start_port."""
```

**Example Usage**:
```python
from playwrightauthor.browser.process import ChromeProcessManager

manager = ChromeProcessManager()

# Check running Chrome processes
processes = manager.get_chrome_processes()
for proc in processes:
    print(f"Chrome PID: {proc.pid}")

# Check if debug Chrome is running
if manager.is_chrome_debug_running():
    print("Chrome debug server is running")
else:
    print("No Chrome debug server found")

# Launch Chrome
proc = manager.launch_chrome(
    executable_path="/path/to/chrome",
    debug_port=9222,
    user_data_dir="/path/to/profile"
)

# Wait for Chrome to be ready
manager.wait_for_chrome_ready(port=9222, timeout=30)
```

## Authentication

### Authentication Base Classes

```python
class BaseAuth:
    """Base class for authentication handlers."""
    
    def __init__(self, browser: Browser):
        """Initialize with browser instance."""
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        raise NotImplementedError
    
    def authenticate(self) -> bool:
        """Perform authentication workflow."""
        raise NotImplementedError
    
    def logout(self) -> bool:
        """Perform logout workflow."""
        raise NotImplementedError
```

### Site-Specific Authentication

```python
class GitHubAuth(BaseAuth):
    """GitHub authentication handler."""
    
    def is_authenticated(self) -> bool:
        """Check GitHub authentication status."""
    
    def authenticate(self) -> bool:
        """Guide through GitHub authentication."""
    
    def get_user_info(self) -> dict:
        """Get authenticated user information."""

class GmailAuth(BaseAuth):
    """Gmail authentication handler."""
    
    def is_authenticated(self) -> bool:
        """Check Gmail authentication status."""
    
    def authenticate(self) -> bool:
        """Guide through Gmail authentication."""

class LinkedInAuth(BaseAuth):
    """LinkedIn authentication handler."""
    
    def is_authenticated(self) -> bool:
        """Check LinkedIn authentication status."""
    
    def authenticate(self) -> bool:
        """Guide through LinkedIn authentication."""
```

**Example Usage**:
```python
from playwrightauthor import Browser
from playwrightauthor.auth import GitHubAuth

with Browser() as browser:
    github_auth = GitHubAuth(browser)
    
    if not github_auth.is_authenticated():
        success = github_auth.authenticate()
        if success:
            print("Successfully authenticated with GitHub")
    
    # Use authenticated session
    page = browser.new_page()
    page.goto("https://github.com/settings")
```

### OnboardingManager

Interactive authentication guidance.

```python
class OnboardingManager:
    """Manages user onboarding and authentication guidance."""
    
    def __init__(self, browser: Browser):
        """Initialize with browser instance."""
    
    def guide_authentication(
        self, 
        site: str, 
        target_url: str = None,
        timeout: int = 300
    ) -> bool:
        """Guide user through authentication process."""
    
    def serve_guidance_page(self, port: int = 8080):
        """Serve local guidance HTML page."""
    
    def wait_for_authentication(self, page, timeout: int = 300) -> bool:
        """Wait for user to complete authentication."""
```

## Monitoring and Performance

### PerformanceMonitor

Browser performance monitoring.

```python
class PerformanceMonitor:
    """Monitors browser performance metrics."""
    
    def __init__(self, browser: Browser):
        """Initialize with browser instance."""
    
    def start(self):
        """Start performance monitoring."""
    
    def stop(self):
        """Stop performance monitoring."""
    
    def get_metrics(self) -> dict:
        """Get current performance metrics."""
    
    def get_summary(self) -> dict:
        """Get performance summary since monitoring started."""
    
    def reset(self):
        """Reset performance counters."""
```

**Metrics returned**:
```python
{
    "memory_usage": 150.5,  # MB
    "cpu_usage": 12.3,      # Percentage
    "navigation_time": 1250, # Milliseconds
    "dom_content_loaded": 800, # Milliseconds
    "page_load_time": 1500,  # Milliseconds
    "network_requests": 45,   # Count
    "failed_requests": 2,     # Count
    "cache_hits": 23,        # Count
    "total_bytes": 1024000   # Bytes downloaded
}
```

### ConnectionMonitor

Browser connection health monitoring.

```python
class ConnectionMonitor:
    """Monitors browser connection health."""
    
    def __init__(self, browser: Browser):
        """Initialize with browser instance."""
    
    def start_monitoring(self, interval: int = 30):
        """Start connection health monitoring."""
    
    def stop_monitoring(self):
        """Stop connection monitoring."""
    
    def is_healthy(self) -> bool:
        """Check if connection is healthy."""
    
    def get_connection_stats(self) -> dict:
        """Get connection statistics."""
    
    def on_connection_lost(self, callback: callable):
        """Register callback for connection loss events."""
    
    def on_connection_restored(self, callback: callable):
        """Register callback for connection restoration events."""
```

## State Management

### StateManager

Browser state persistence.

```python
class StateManager:
    """Manages browser state persistence."""
    
    def __init__(self, state_file: str = None):
        """Initialize with optional state file path."""
    
    def save_state(self, state: dict):
        """Save browser state to disk."""
    
    def load_state(self) -> dict:
        """Load browser state from disk."""
    
    def clear_state(self):
        """Clear saved state."""
    
    def is_state_valid(self, state: dict) -> bool:
        """Validate state data."""
```

**State structure**:
```python
{
    "chrome_path": "/path/to/chrome",
    "chrome_version": "119.0.6045.105",
    "profile_path": "/path/to/profile", 
    "debug_port": 9222,
    "last_used": "2024-01-15T10:30:00Z",
    "process_id": 12345,
    "health_status": "healthy"
}
```

## Utilities

### Logger

Logging utilities with structured logging support.

```python
class Logger:
    """Structured logging for PlaywrightAuthor."""
    
    def __init__(self, name: str, level: str = "INFO"):
        """Initialize logger with name and level."""
    
    def debug(self, message: str, **kwargs):
        """Log debug message with optional context."""
    
    def info(self, message: str, **kwargs):
        """Log info message with optional context."""
    
    def warning(self, message: str, **kwargs):
        """Log warning message with optional context."""
    
    def error(self, message: str, **kwargs):
        """Log error message with optional context."""
    
    def set_level(self, level: str):
        """Set logging level."""
    
    def add_handler(self, handler):
        """Add custom log handler."""
```

### PathUtils

Cross-platform path utilities.

```python
class PathUtils:
    """Cross-platform path utilities."""
    
    @staticmethod
    def get_cache_dir() -> Path:
        """Get platform-specific cache directory."""
    
    @staticmethod
    def get_config_dir() -> Path:
        """Get platform-specific config directory."""
    
    @staticmethod
    def get_data_dir() -> Path:
        """Get platform-specific data directory."""
    
    @staticmethod
    def ensure_dir(path: Path) -> Path:
        """Ensure directory exists and return path."""
    
    @staticmethod
    def safe_path(path: str) -> Path:
        """Convert string to safe Path object."""
```

## Exceptions

### Custom Exceptions

```python
class PlaywrightAuthorError(Exception):
    """Base exception for PlaywrightAuthor."""

class BrowserError(PlaywrightAuthorError):
    """Browser-related errors."""

class ConnectionError(PlaywrightAuthorError):
    """Connection-related errors."""

class InstallationError(PlaywrightAuthorError):
    """Installation-related errors."""

class ConfigurationError(PlaywrightAuthorError):
    """Configuration-related errors."""

class AuthenticationError(PlaywrightAuthorError):
    """Authentication-related errors."""

class TimeoutError(PlaywrightAuthorError):
    """Timeout-related errors."""
```

**Exception handling**:
```python
from playwrightauthor import Browser
from playwrightauthor.exceptions import BrowserError, ConnectionError

try:
    with Browser() as browser:
        page = browser.new_page()
        page.goto("https://example.com")
except BrowserError as e:
    print(f"Browser error: {e}")
except ConnectionError as e:
    print(f"Connection error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Environment Variables

### Configuration Environment Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `PLAYWRIGHTAUTHOR_HEADLESS` | bool | `True` | Run browser in headless mode |
| `PLAYWRIGHTAUTHOR_TIMEOUT` | int | `30000` | Default timeout in milliseconds |
| `PLAYWRIGHTAUTHOR_USER_DATA_DIR` | str | `~/.cache/playwrightauthor/profile` | Browser profile directory |
| `PLAYWRIGHTAUTHOR_CHROME_PATH` | str | `auto` | Custom Chrome executable path |
| `PLAYWRIGHTAUTHOR_DEBUG_PORT` | int | `9222` | Chrome remote debugging port |
| `PLAYWRIGHTAUTHOR_LOG_LEVEL` | str | `INFO` | Logging level |
| `PLAYWRIGHTAUTHOR_LOG_FILE` | str | `None` | Log file path |
| `PLAYWRIGHTAUTHOR_INSTALL_DIR` | str | `~/.cache/playwrightauthor/chrome` | Chrome installation directory |

### Development Environment Variables

| Variable | Description |
|----------|-------------|
| `DEBUG` | Enable Playwright debug logging |
| `PWDEBUG` | Enable Playwright debug mode |
| `HTTP_PROXY` | HTTP proxy server |
| `HTTPS_PROXY` | HTTPS proxy server |
| `NO_PROXY` | Hosts to bypass proxy |

## Type Definitions

### TypeScript-style Type Definitions

```python
from typing import Dict, List, Optional, Union, Callable
from pathlib import Path

# Basic types
URL = str
FilePath = Union[str, Path]
Timeout = int  # milliseconds
Port = int

# Configuration types
ViewportDict = Dict[str, int]  # {"width": int, "height": int}
ChromeArgs = List[str]
LogLevel = str  # "DEBUG" | "INFO" | "WARNING" | "ERROR"

# Callback types
ProgressCallback = Callable[[int, int], None]  # (downloaded, total)
ErrorCallback = Callable[[Exception], None]
ConnectionCallback = Callable[[], None]

# Browser types (from Playwright)
BrowserType = Union[
    'playwright.sync_api.Browser',
    'playwright.async_api.Browser'
]

PageType = Union[
    'playwright.sync_api.Page', 
    'playwright.async_api.Page'
]

ContextType = Union[
    'playwright.sync_api.BrowserContext',
    'playwright.async_api.BrowserContext'  
]
```

## Version Information

```python
# Version access
from playwrightauthor import __version__
print(f"PlaywrightAuthor version: {__version__}")

# Dependency versions
from playwrightauthor.version import get_version_info
version_info = get_version_info()
print(version_info)
# {
#     "playwrightauthor": "1.0.0",
#     "playwright": "1.40.0", 
#     "python": "3.11.0",
#     "chrome": "119.0.6045.105"
# }
```

## Next Steps

- Check [Troubleshooting](troubleshooting.md) for common issues
- Review [Contributing](contributing.md) to extend the API
- Explore examples in the project repository
- Join community discussions for API questions