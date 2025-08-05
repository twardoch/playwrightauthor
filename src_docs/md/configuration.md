# Configuration

PlaywrightAuthor provides flexible configuration options through environment variables, configuration objects, and runtime parameters.

## Configuration Methods

### 1. Environment Variables

Set environment variables to configure default behavior:

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

Use configuration classes for programmatic control:

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

Override settings at runtime:

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
    # Display settings
    headless=False,              # Show/hide browser window
    viewport={"width": 1920, "height": 1080},  # Default viewport size
    
    # Timing settings
    timeout=30000,               # Default timeout in milliseconds
    navigation_timeout=30000,    # Page navigation timeout
    
    # Chrome settings
    chrome_path=None,           # Custom Chrome executable path
    chrome_args=[],             # Additional Chrome arguments
    user_data_dir=None,         # Profile directory path
    debug_port=9222,            # Remote debugging port
    
    # Feature flags
    ignore_https_errors=False,  # Ignore SSL certificate errors
    bypass_csp=False,           # Bypass Content Security Policy
    
    # Logging
    log_level="INFO",           # Logging verbosity
    log_file=None,              # Log file path
)
```

### Common Chrome Arguments

```python
config = BrowserConfig(
    chrome_args=[
        "--disable-web-security",      # Disable CORS
        "--disable-features=VizDisplayCompositor",  # Fix rendering issues
        "--disable-background-timer-throttling",    # Prevent tab throttling
        "--disable-renderer-backgrounding",         # Keep tabs active
        "--disable-backgrounding-occluded-windows", # Prevent window throttling
        "--disable-blink-features=AutomationControlled",  # Hide automation
        "--no-sandbox",                 # Linux containerized environments
        "--disable-dev-shm-usage",      # Overcome limited resource problems
        "--disable-gpu",                # Disable GPU acceleration
        "--user-agent=Custom User Agent",  # Custom user agent
    ]
)
```

## Environment Variables Reference

### Core Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `PLAYWRIGHTAUTHOR_HEADLESS` | bool | `True` | Run browser in headless mode |
| `PLAYWRIGHTAUTHOR_TIMEOUT` | int | `30000` | Default timeout in milliseconds |
| `PLAYWRIGHTAUTHOR_USER_DATA_DIR` | str | `~/.cache/playwrightauthor/profile` | Browser profile directory |
| `PLAYWRIGHTAUTHOR_DEBUG_PORT` | int | `9222` | Chrome remote debugging port |

### Chrome Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `PLAYWRIGHTAUTHOR_CHROME_PATH` | str | `auto` | Custom Chrome executable path |
| `PLAYWRIGHTAUTHOR_CHROME_ARGS` | str | `""` | Comma-separated Chrome arguments |
| `PLAYWRIGHTAUTHOR_INSTALL_DIR` | str | `~/.cache/playwrightauthor/chrome` | Chrome installation directory |

### Logging Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `PLAYWRIGHTAUTHOR_LOG_LEVEL` | str | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `PLAYWRIGHTAUTHOR_LOG_FILE` | str | `None` | Log file path (stdout if not set) |
| `PLAYWRIGHTAUTHOR_VERBOSE` | bool | `False` | Enable verbose logging |

### Network Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `HTTP_PROXY` | str | `None` | HTTP proxy server |
| `HTTPS_PROXY` | str | `None` | HTTPS proxy server |
| `NO_PROXY` | str | `None` | Hosts to bypass proxy |

## Configuration Examples

### Development Environment

```python
# dev_config.py
from playwrightauthor import BrowserConfig

DEV_CONFIG = BrowserConfig(
    headless=False,              # Show browser for debugging
    timeout=60000,               # Longer timeouts for debugging
    log_level="DEBUG",           # Verbose logging
    chrome_args=[
        "--auto-open-devtools-for-tabs",  # Open DevTools
        "--disable-web-security",         # Disable CORS for testing
    ]
)
```

### Production Environment

```python
# prod_config.py
from playwrightauthor import BrowserConfig

PROD_CONFIG = BrowserConfig(
    headless=True,               # No GUI in production
    timeout=30000,               # Standard timeouts
    log_level="WARNING",         # Minimal logging
    chrome_args=[
        "--no-sandbox",              # Required for containers
        "--disable-dev-shm-usage",   # Memory optimization
        "--disable-gpu",             # No GPU in headless
    ]
)
```

### Testing Environment

```python
# test_config.py
from playwrightauthor import BrowserConfig

TEST_CONFIG = BrowserConfig(
    headless=True,               # Headless for CI/CD
    timeout=10000,               # Fast timeouts for tests
    user_data_dir=None,          # Fresh profile each test
    chrome_args=[
        "--disable-extensions",      # No extensions in tests
        "--disable-plugins",         # No plugins in tests
        "--disable-images",          # Faster loading
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
        "--no-sandbox",                    # Required for Docker
        "--disable-dev-shm-usage",         # Use /tmp instead of /dev/shm
        "--disable-gpu",                   # No GPU in containers
        "--disable-software-rasterizer",   # Disable software rasterizer
        "--remote-debugging-address=0.0.0.0",  # Allow external connections
    ]
)
```

## Advanced Configuration

### Dynamic Configuration

```python
import os
from playwrightauthor import Browser, BrowserConfig

def get_config():
    """Dynamic configuration based on environment"""
    if os.getenv("CI"):
        # CI environment
        return BrowserConfig(
            headless=True,
            timeout=10000,
            chrome_args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
    elif os.getenv("DEBUG"):
        # Debug environment
        return BrowserConfig(
            headless=False,
            timeout=60000,
            log_level="DEBUG"
        )
    else:
        # Default configuration
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
    """Validate configuration settings"""
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
    """Create temporary profile for isolated sessions"""
    temp_dir = tempfile.mkdtemp(prefix="playwright_profile_")
    return BrowserConfig(user_data_dir=temp_dir)

def create_named_profile(name: str):
    """Create named profile for persistent sessions"""
    profile_dir = Path.home() / ".playwrightauthor" / "profiles" / name
    profile_dir.mkdir(parents=True, exist_ok=True)
    return BrowserConfig(user_data_dir=str(profile_dir))

# Use temporary profile
with Browser(config=create_temp_profile()) as browser:
    # Isolated session, no persistent data
    pass

# Use named profile
with Browser(config=create_named_profile("github_automation")) as browser:
    # Persistent session for GitHub automation
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
    """Load configuration from YAML file"""
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

- Learn about [Browser Management](browser-management.md) internals
- Set up [Authentication](authentication.md) workflows
- Explore [Advanced Features](advanced-features.md) for complex scenarios
- Check [Troubleshooting](troubleshooting.md) for configuration issues