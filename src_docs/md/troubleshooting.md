# Troubleshooting

This guide helps you diagnose and resolve common issues with PlaywrightAuthor. Problems are organized by category with practical solutions.

## Installation Issues

### Package Installation Problems

**Problem**: `pip install playwrightauthor` fails

**Solutions**:
```bash
# Update pip first
python -m pip install --upgrade pip

# Install with verbose output
pip install -v playwrightauthor

# Use alternative index
pip install -i https://pypi.org/simple/ playwrightauthor

# Install from source
pip install git+https://github.com/terragond/playwrightauthor.git
```

**Problem**: Import errors after installation

**Solutions**:
```python
# Verify installation
import sys
print(sys.path)

try:
    import playwrightauthor
    print(f"PlaywrightAuthor version: {playwrightauthor.__version__}")
except ImportError as e:
    print(f"Import error: {e}")

# Check dependencies
import playwright
print(f"Playwright version: {playwright.__version__}")
```

### Python Version Compatibility

**Problem**: PlaywrightAuthor doesn't work with your Python version

**Check Python version**:
```bash
python --version
# Requires 3.8 or higher
```

**Solutions**:
```bash
# Install compatible Python version
pyenv install 3.11
pyenv local 3.11

# Or use conda
conda create -n playwright python=3.11
conda activate playwright
pip install playwrightauthor
```

## Browser Download and Installation

### Chrome Download Failures

**Problem**: Chrome for Testing download fails

**Debugging**:
```python
from playwrightauthor.browser.installer import ChromeInstaller
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

installer = ChromeInstaller()
try:
    chrome_path = installer.install_latest()
    print(f"Chrome installed to: {chrome_path}")
except Exception as e:
    print(f"Download failed: {e}")
    # Check available versions
    versions = installer.get_available_versions()
    print(f"Available versions: {versions[:5]}")
```

**Solutions**:
```bash
# Manual Chrome installation
# Download from: https://googlechromelabs.github.io/chrome-for-testing/

# Set custom Chrome path
export PLAYWRIGHTAUTHOR_CHROME_PATH="/path/to/your/chrome"
```

**Problem**: Permission errors during download

**Solutions**:
```bash
# Linux/macOS: Fix permissions
chmod 755 ~/.cache/playwrightauthor/
chmod +x ~/.cache/playwrightauthor/chrome/*/chrome

# Windows: Run as administrator or change install directory
export PLAYWRIGHTAUTHOR_INSTALL_DIR="C:/Users/%USERNAME%/AppData/Local/PlaywrightAuthor"
```

### Network and Proxy Issues

**Problem**: Downloads fail behind corporate firewall

**Solutions**:
```bash
# Set proxy environment variables
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080
export NO_PROXY=localhost,127.0.0.1

# Or configure in Python
import os
os.environ['HTTP_PROXY'] = 'http://proxy.company.com:8080'
os.environ['HTTPS_PROXY'] = 'http://proxy.company.com:8080'
```

**Problem**: SSL certificate errors

**Solutions**:
```python
from playwrightauthor import BrowserConfig

# Disable SSL verification for downloads (security risk)
config = BrowserConfig(
    chrome_args=["--ignore-certificate-errors", "--ignore-ssl-errors"]
)
```

## Browser Launch Issues

### Port Conflicts

**Problem**: "Port 9222 already in use"

**Debugging**:
```python
from playwrightauthor.browser.process import get_chrome_processes

# Find what's using the port
processes = get_chrome_processes()
for proc in processes:
    print(f"PID: {proc.pid}, Command: {' '.join(proc.cmdline())}")
```

**Solutions**:
```python
from playwrightauthor import Browser, BrowserConfig

# Use different debug port
config = BrowserConfig(debug_port=9223)
with Browser(config=config) as browser:
    page = browser.new_page()
    page.goto("https://example.com")

# Or kill existing Chrome processes
from playwrightauthor.browser.process import kill_chrome_instances
kill_chrome_instances()
```

### Permission and Security Issues

**Problem**: Chrome won't start due to security restrictions

**Linux solutions**:
```bash
# Add Chrome to PATH
export PATH="/opt/google/chrome:$PATH"

# Fix sandbox issues
sudo sysctl kernel.unprivileged_userns_clone=1

# Or disable sandbox (less secure)
```

```python
config = BrowserConfig(
    chrome_args=["--no-sandbox", "--disable-setuid-sandbox"]
)
```

**Problem**: SELinux or AppArmor blocking Chrome

**Solutions**:
```bash
# Check SELinux status
sestatus

# Temporarily disable
sudo setenforce 0

# For AppArmor
sudo aa-complain /usr/bin/chromium-browser
```

### Docker and Container Issues

**Problem**: Chrome fails in Docker containers

**Solutions**:
```dockerfile
# Dockerfile additions
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libxkbcommon0 \
    libxss1
```

```python
# Docker-optimized configuration
config = BrowserConfig(
    headless=True,
    chrome_args=[
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu",
        "--disable-software-rasterizer",
        "--remote-debugging-address=0.0.0.0"
    ]
)
```

## Connection and Communication Issues

### WebSocket Connection Failures

**Problem**: "Failed to connect to Chrome"

**Debugging**:
```python
import requests

# Test Chrome debug port
port = 9222
try:
    response = requests.get(f"http://localhost:{port}/json/version", timeout=5)
    print(f"Chrome debug info: {response.json()}")
except Exception as e:
    print(f"Connection test failed: {e}")
```

**Solutions**:
```python
from playwrightauthor import Browser, BrowserConfig
import time

# Increase connection timeout
config = BrowserConfig(
    connect_timeout=30,
    connect_retries=5
)

# Retry connection
def connect_with_retry():
    for attempt in range(3):
        try:
            with Browser(config=config) as browser:
                return browser
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(5)
    raise Exception("Failed to connect after retries")
```

### Browser Process Management

**Problem**: Chrome processes not terminating

**Debugging**:
```python
from playwrightauthor.browser.process import ChromeProcessManager
import psutil

manager = ChromeProcessManager()

# List Chrome processes
processes = manager.get_chrome_processes()
for proc in processes:
    try:
        print(f"PID: {proc.pid}, Status: {proc.status()}, Memory: {proc.memory_info().rss / 1024 / 1024:.1f}MB")
    except psutil.NoSuchProcess:
        print(f"Process {proc.pid} no longer exists")
```

**Solutions**:
```python
from playwrightauthor.browser.process import force_kill_chrome

# Force kill Chrome processes
force_kill_chrome()

# Or graceful shutdown
manager = ChromeProcessManager()
manager.shutdown_all_chrome(graceful=True, timeout=10)
```

## Authentication and Session Issues

### Session Not Persisting

**Problem**: Authentication doesn't persist between runs

**Debugging**:
```python
from pathlib import Path

# Check profile directory
profile_dir = Path.home() / ".cache" / "playwrightauthor" / "profile"
print(f"Profile directory: {profile_dir}")
print(f"Profile exists: {profile_dir.exists()}")

if profile_dir.exists():
    files = list(profile_dir.glob("**/*"))
    print(f"Profile files: {len(files)}")
```

**Solutions**:
```python
# Ensure profile directory is writable
import os
from pathlib import Path

profile_dir = Path.home() / ".playwrightauthor" / "profiles" / "main"
profile_dir.mkdir(parents=True, exist_ok=True)
os.chmod(profile_dir, 0o755)

config = BrowserConfig(user_data_dir=str(profile_dir))

with Browser(config=config) as browser:
    page = browser.new_page()
    page.goto("https://github.com/login")
    # Complete authentication
    input("Press Enter after logging in...")
    
    # Verify session
    cookies = page.context.cookies()
    print(f"Saved {len(cookies)} cookies")
```

### Cookie and Storage Issues

**Problem**: Cookies not being saved or loaded

**Debugging**:
```python
from playwrightauthor import Browser

with Browser() as browser:
    page = browser.new_page()
    page.goto("https://httpbin.org/cookies/set/test/value")
    
    # Check cookies
    cookies = page.context.cookies()
    print(f"Current cookies: {cookies}")
    
    # Test persistence
    page.goto("https://httpbin.org/cookies")
    response = page.text_content("body")
    print(f"Cookie response: {response}")
```

**Solutions**:
```python
# Manual cookie management
with Browser() as browser:
    context = browser.contexts[0]
    
    # Save cookies
    cookies = context.cookies()
    import json
    with open("cookies.json", "w") as f:
        json.dump(cookies, f)
    
    # Load cookies
    with open("cookies.json", "r") as f:
        saved_cookies = json.load(f)
    context.add_cookies(saved_cookies)
```

## Performance Issues

### Slow Browser Operations

**Problem**: Browser operations are slow

**Debugging**:
```python
import time
from playwrightauthor import Browser

with Browser() as browser:
    page = browser.new_page()
    
    start = time.time()
    page.goto("https://example.com")
    navigation_time = time.time() - start
    
    print(f"Navigation took: {navigation_time:.2f} seconds")
```

**Solutions**:
```python
# Optimize browser configuration
config = BrowserConfig(
    headless=True,
    chrome_args=[
        "--disable-images",
        "--disable-javascript",
        "--disable-plugins",
        "--disable-extensions",
        "--no-first-run",
        "--disable-default-apps"
    ]
)

# Optimize page loading
with Browser(config=config) as browser:
    page = browser.new_page()
    
    # Block unnecessary resources
    page.route("**/*.{png,jpg,jpeg,gif,svg}", lambda route: route.abort())
    page.route("**/*.{css}", lambda route: route.abort())
    
    page.goto("https://example.com", wait_until="domcontentloaded")
```

### Memory Issues

**Problem**: High memory usage

**Debugging**:
```python
import psutil
import os
from playwrightauthor import Browser

def get_memory_usage():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024

print(f"Initial memory: {get_memory_usage():.1f} MB")

with Browser() as browser:
    print(f"After browser creation: {get_memory_usage():.1f} MB")
    
    for i in range(10):
        page = browser.new_page()
        page.goto("https://example.com")
        page.close()
        print(f"After page {i+1}: {get_memory_usage():.1f} MB")
```

**Solutions**:
```python
# Proper resource cleanup
with Browser() as browser:
    for url in urls:
        page = browser.new_page()
        try:
            page.goto(url)
        finally:
            page.close()

# Limit concurrent pages
from playwrightauthor.utils import PagePool

pool = PagePool(max_pages=5)
with Browser() as browser:
    for url in urls:
        with pool.get_page(browser) as page:
            page.goto(url)
```

## Error Messages and Debugging

### Common Error Messages

**"TimeoutError: waiting for selector"**
```python
# Increase timeout
page.wait_for_selector("#element", timeout=60000)

# Use better selectors
page.wait_for_selector("text=Submit")
page.wait_for_selector("[data-testid='submit']")

# Check element exists
if page.query_selector("#element"):
    page.click("#element")
```

**"Browser has been closed"**
```python
# Check browser state
if browser.is_connected():
    page = browser.new_page()
```

**"Connection refused"**
```python
# Verify Chrome is running
from playwrightauthor.browser.process import is_chrome_debug_running

if not is_chrome_debug_running():
    print("Chrome debug server not running")
```

### Debug Logging

Enable logging:
```python
import logging
from playwrightauthor import Browser

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('playwright_debug.log'),
        logging.StreamHandler()
    ]
)

# Enable Playwright debug
import os
os.environ['DEBUG'] = 'pw:api,pw:browser'

with Browser() as browser:
    page = browser.new_page()
    page.goto("https://example.com")
```

### Visual Debugging

```python
from playwrightauthor import Browser, BrowserConfig

# Show browser for debugging
config = BrowserConfig(
    headless=False,
    chrome_args=["--auto-open-devtools-for-tabs"]
)

with Browser(config=config) as browser:
    page = browser.new_page()
    page.goto("https://example.com")
    
    # Pause for inspection
    page.pause()
    
    # Take screenshots
    page.screenshot(path="step1.png")
    page.click("button")
    page.screenshot(path="step2.png")
```

## Platform-Specific Issues

### Windows Issues

**Problem**: Chrome fails to start

**Solutions**:
```python
# Use Windows Chrome path
config = BrowserConfig(
    chrome_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe"
)

# Handle Windows path issues
import os
if os.name == 'nt':
    config.chrome_args.append("--disable-features=VizDisplayCompositor")
```

### macOS Issues

**Problem**: Permission denied

**Solutions**:
```bash
# Grant Chrome permissions
xattr -d com.apple.quarantine /Applications/Google\ Chrome.app

# Or install via Homebrew
brew install --cask google-chrome
```

### Linux Issues

**Problem**: Missing dependencies

**Solutions**:
```bash
# Install required packages
sudo apt-get update && sudo apt-get install -y \
    libnss3 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libxss1 \
    libasound2

# For headless systems
sudo apt-get install -y xvfb
export DISPLAY=:99
Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &
```

## Getting Help

### Diagnostic Information

```python
from playwrightauthor.diagnostics import collect_diagnostic_info

# Collect system info
info = collect_diagnostic_info()
print(info)
```

### Enable Debug Mode

```python
from playwrightauthor import Browser, BrowserConfig

config = BrowserConfig(
    log_level="DEBUG",
    verbose=True
)

with Browser(config=config) as browser:
    page = browser.new_page()
    page.goto("https://example.com")
```

### Creating Bug Reports

Include this information:
1. **System**: OS, Python version, PlaywrightAuthor version, Chrome version
2. **Configuration**: Browser config, environment variables, arguments
3. **Error**: Complete message, stack trace, debug logs
4. **Behavior**: Expected vs actual results, workarounds

```python
# Diagnostic script for bug reports
import sys
import platform
import playwrightauthor

print("=== System Information ===")
print(f"OS: {platform.system()} {platform.release()}")
print(f"Python: {sys.version}")
print(f"PlaywrightAuthor: {playwrightauthor.__version__}")

print("\n=== Chrome Information ===")
from playwrightauthor.browser.finder import find_chrome
try:
    chrome_path = find_chrome()
    print(f"Chrome path: {chrome_path}")
except Exception as e:
    print(f"Chrome not found: {e}")

print("\n=== Configuration ===")
import os
env_vars = [k for k in os.environ.keys() if k.startswith('PLAYWRIGHTAUTHOR_')]
for var in env_vars:
    print(f"{var}: {os.environ[var]}")
```

## Next Steps

- Review [API Reference](api-reference.md) for method documentation
- Check [Contributing](contributing.md) to report bugs
- Visit [GitHub Issues](https://github.com/terragond/playwrightauthor/issues) for known problems
- Join community discussions for support