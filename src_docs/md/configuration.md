# Configuration

PlaywrightAuthor supports flexible configuration through environment variables, Python objects, and runtime parameters.

## Configuration Methods

### 1. Environment Variables

Set environment variables for default settings:

```bash
# Browser settings
export PLAYWRIGHTAUTHOR_HEADLESS=false
export PLAYWRIGHTAUTHOR_TIMEOUT=30000
export PLAYWRIGHTAUTHOR_USER_DATA_DIR=/custom/profile

# Chrome settings
export PLAYWRIGHTAUTHOR_CHROME_PATH=/opt/chrome/chrome
export PLAYWRIGHTAUTHOR_DEBUG_PORT=9222

# Logging
export PLAYWRIGHTAUTHOR_LOG_LEVEL=DEBUG
export PLAYWRIGHTAUTHOR_LOG_FILE=/var/log/playwright.log
```

### 2. Configuration Objects

Use `BrowserConfig` for programmatic control:

```python
from playwrightauthor import Browser, BrowserConfig

config = BrowserConfig(
    headless=False,
    timeout=30000,
    user_data_dir="./my_profile",
    debug_port=9223,
    chrome_args=["--disable-web-security"]
)

with Browser(config=config) as browser:
    page = browser.new_page()
    page.goto("https://example.com")
```

### 3. Runtime Parameters

Override any setting at runtime:

```python
with Browser(headless=True, timeout=60000) as browser:
    page = browser.new_page()
    page.goto("https://example.com")
```

## Browser Configuration

### BrowserConfig Class

```python
from playwrightauthor import BrowserConfig

config = BrowserConfig(
    # Display
    headless=False,              # Show browser window
    viewport={"width": 1920, "height": 1080},  # Window size
    
    # Timing
    timeout=30000,               # Operation timeout (ms)
    navigation_timeout=30000,    # Navigation timeout (ms)
    
    # Chrome
    chrome_path=None,           # Custom Chrome path
    chrome_args=[],             # Additional Chrome flags
    user_data_dir=None,         # Profile directory
    debug_port=9222,            # Remote debugging port
    
    # Features
    ignore_https_errors=False,  # Skip SSL validation
    bypass_csp=False,           # Ignore Content Security Policy
    
    # Logging
    log_level="INFO",           # Log verbosity
    log_file=None,              # Log output file
)
```

### Common Chrome Arguments

```python
config = BrowserConfig(
    chrome_args=[
        "--disable-web-security",      # Skip CORS checks
        "--disable-features=VizDisplayCompositor",  # Fix rendering bugs
        "--disable-background-timer-throttling",    # Keep timers active
        "--disable-renderer-backgrounding",         # Prevent tab slowdown
        "--disable-backgrounding-occluded-windows", # Prevent window slowdown
        "--disable-blink-features=AutomationControlled",  # Hide bot detection
        "--no-sandbox",                 # Required in containers
        "--disable-dev-shm-usage",      # Use disk instead of memory
        "--disable-gpu",                # Skip GPU acceleration
        "--user-agent=Custom User Agent",  # Fake browser identity
    ]
)
```

## Environment Variables Reference

### Core Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `PLAYWRIGHTAUTHOR_HEADLESS` | bool | `True` | Show/hide browser window |
| `PLAYWRIGHTAUTHOR_TIMEOUT` | int | `30000` | Timeout in milliseconds |
| `PLAYWRIGHTAUTHOR_USER_DATA_DIR` | str | `~/.cache/playwrightauthor/profile` | Profile storage path |
| `PLAYWRIGHTAUTHOR_DEBUG_PORT` | int | `9222` | Chrome debugging port |

### Chrome Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `PLAYWRIGHTAUTHOR_CHROME_PATH` | str | `auto` | Chrome executable path |
| `PLAYWRIGHTAUTHOR_CHROME_ARGS` | str | `""` | Comma-separated flags |
| `PLAYWRIGHTAUTHOR_INSTALL_DIR` | str | `~/.cache/playwrightauthor/chrome` | Chrome install path |

### Logging Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `PLAYWRIGHTAUTHOR_LOG_LEVEL` | str | `INFO` | Log level (DEBUG, INFO, WARNING, ERROR) |
| `PLAYWRIGHTAUTHOR_LOG_FILE` | str | `None` | Log file path (stdout if unset) |
| `PLAYWRIGHTAUTHOR_VERBOSE` | bool | `False` | Enable detailed logging |

### Network Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `HTTP_PROXY` | str | `None` | HTTP proxy address |
| `HTTPS_PROXY` | str | `None` | HTTPS proxy address |
| `NO_PROXY` | str | `None` | Proxy bypass list |

## Configuration Examples

### Development Environment

```python
# dev_config.py
from playwrightauthor import BrowserConfig

DEV_CONFIG = BrowserConfig(
    headless=False,              # Visible browser for debugging
    timeout=60000,               # Generous timeouts
    log_level="DEBUG",           # Full logging
    chrome_args=[
        "--auto-open-devtools-for-tabs",  # Auto-open DevTools
        "--disable-web-security",         # Skip CORS for local testing
    ]
)
```

### Production Environment

```python
# prod_config.py
from playwrightauthor import BrowserConfig

PROD_CONFIG = BrowserConfig(
    headless=True,               # No GUI
    timeout=30000,               # Standard timeouts
    log_level="WARNING",         # Log only warnings and errors
    chrome_args=[
        "--no-sandbox",              # Required in containers
        "--disable-dev-shm-usage",   # Avoid memory issues
        "--disable-gpu",             # No GPU in headless mode
    ]
)
```

### Testing Environment

```python
# test_config.py
from playwrightauthor import BrowserConfig

TEST_CONFIG = BrowserConfig(
    headless=True,               # Headless for CI
    timeout=10000,               # Fast failure
    user_data_dir=None,          # Fresh profile per test
    chrome_args=[
        "--disable-extensions",      # No extensions
        "--disable-plugins",         # No plugins
        "--disable-images",          # Faster page loads
    ]
)
```

### Docker Environment

```python
# docker_config.py
from playwrightauthor import BrowserConfig

DOCKER_CONFIG = BrowserConfig(
    headless=True,
    chrome_args=[
        "--no-sandbox",                    # Required in containers
        "--disable-dev-shm-usage",         # Use /tmp instead of /dev/shm
        "--disable-gpu",                   # Skip GPU in containers
        "--disable-software-rasterizer",   # Disable software rendering
        "--remote-debugging-address=0.0.0.0",  # Allow external debugging
    ]
)
```

## Advanced Configuration

### Dynamic Configuration

```python
import os
from playwrightauthor import Browser, BrowserConfig

def get_config():
    """Load config based on environment"""
    if os.getenv("CI"):
        # CI/CD settings
        return BrowserConfig(
            headless=True,
            timeout=10000,
            chrome_args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
    elif os.getenv("DEBUG"):
        # Debug settings
        return BrowserConfig(
            headless=False,
            timeout=60000,
            log_level="DEBUG"
        )
    else:
        # Default settings
        return BrowserConfig()

with Browser(config=get_config()) as browser:
    page = browser.new_page()
    page.goto("https://example.com")
```

### Configuration Validation

```python
from playwrightauthor import BrowserConfig
from playwrightauthor.exceptions import ConfigurationError

def validate_config(config: BrowserConfig):
    """Sanity check configuration"""
    if config.timeout < 1000:
        raise ConfigurationError("Timeout must be at least 1000ms")
    
    if config.debug_port < 1024 or config.debug_port > 65535:
        raise ConfigurationError("Debug port must be between 1024-65535")
    
    return config

config = BrowserConfig(timeout=5000, debug_port=9222)
validated_config = validate_config(config)
```

### Profile Management

```python
import tempfile
from pathlib import Path
from playwrightauthor import Browser, BrowserConfig

def create_temp_profile():
    """Create isolated session profile"""
    temp_dir = tempfile.mkdtemp(prefix="playwright_profile_")
    return BrowserConfig(user_data_dir=temp_dir)

def create_named_profile(name: str):
    """Create persistent profile"""
    profile_dir = Path.home() / ".playwrightauthor" / "profiles" / name
    profile_dir.mkdir(parents=True, exist_ok=True)
    return BrowserConfig(user_data_dir=str(profile_dir))

# Isolated session
with Browser(config=create_temp_profile()) as browser:
    pass

# Persistent session
with Browser(config=create_named_profile("github_automation")) as browser:
    pass
```

## Configuration File Support

### YAML Configuration

```yaml
# playwrightauthor.yml
browser:
  headless: false
  timeout: 30000
  viewport:
    width: 1920
    height: 1080
  
chrome:
  debug_port: 9222
  args:
    - "--disable-web-security"
    - "--disable-features=VizDisplayCompositor"
  
logging:
  level: "INFO"
  file: "/var/log/playwright.log"
```

```python
import yaml
from playwrightauthor import Browser, BrowserConfig

def load_config_from_file(path: str) -> BrowserConfig:
    """Parse YAML config file"""
    with open(path, 'r') as f:
        data = yaml.safe_load(f)
    
    browser_config = data.get('browser', {})
    chrome_config = data.get('chrome', {})
    logging_config = data.get('logging', {})
    
    return BrowserConfig(
        headless=browser_config.get('headless', True),
        timeout=browser_config.get('timeout', 30000),
        viewport=browser_config.get('viewport'),
        debug_port=chrome_config.get('debug_port', 9222),
        chrome_args=chrome_config.get('args', []),
        log_level=logging_config.get('level', 'INFO'),
        log_file=logging_config.get('file'),
    )

config = load_config_from_file('playwrightauthor.yml')
with Browser(config=config) as browser:
    page = browser.new_page()
    page.goto("https://example.com")
```

## Next Steps

- [Browser Management](browser-management.md) internals
- [Authentication](authentication.md) workflows
- [Advanced Features](advanced-features.md) for complex scenarios
- [Troubleshooting](troubleshooting.md) configuration issues