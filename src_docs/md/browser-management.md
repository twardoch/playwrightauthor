# Browser Management

PlaywrightAuthor automates the full browser lifecycle—from locating or installing Chrome to managing processes and connections. This chapter explains how it works under the hood.

## Browser Lifecycle

### 1. Browser Discovery

PlaywrightAuthor looks for Chrome in this order:

1. **Environment variable**: `PLAYWRIGHTAUTHOR_CHROME_PATH`
2. **System installations**: Standard Chrome/Chromium locations
3. **Downloaded instances**: Previously downloaded Chrome for Testing
4. **Fresh download**: Latest Chrome for Testing

```python
from playwrightauthor.browser import finder

# Find Chrome executable
chrome_path = finder.find_chrome()
print(f"Found Chrome at: {chrome_path}")

# List search locations
locations = finder.get_chrome_locations()
for location in locations:
    print(f"Checking: {location}")
```

### 2. Chrome Installation

If no suitable Chrome is found, PlaywrightAuthor downloads Chrome for Testing:

```python
from playwrightauthor.browser import installer

# Download latest Chrome for Testing
chrome_path = installer.download_chrome()
print(f"Downloaded Chrome to: {chrome_path}")

# Show available versions
versions = installer.get_available_versions()
print(f"Available versions: {versions[:5]}")  # Latest 5
```

### 3. Process Management

PlaywrightAuthor handles Chrome processes:

```python
from playwrightauthor.browser import process

# Launch Chrome with debugging enabled
proc = process.launch_chrome(
    executable_path="/path/to/chrome",
    debug_port=9222,
    user_data_dir="/path/to/profile"
)

# Check if Chrome is running on port
is_running = process.is_chrome_debug_running(port=9222)
print(f"Chrome debug running: {is_running}")

# Kill existing Chrome processes
process.kill_chrome_instances()
```

### 4. Connection Establishment

Playwright connects to the launched Chrome instance:

```python
from playwrightauthor.connection import connect_to_chrome

# Connect via debug port
browser = connect_to_chrome(debug_port=9222)
print(f"Connected to browser: {browser}")
```

## Browser Discovery Details

### Chrome Search Locations

PlaywrightAuthor checks over 20 locations per platform.

#### Windows
```
C:\Program Files\Google\Chrome\Application\chrome.exe
C:\Program Files (x86)\Google\Chrome\Application\chrome.exe
%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe
%PROGRAMFILES%\Google\Chrome\Application\chrome.exe
C:\Program Files\Chromium\Application\chrome.exe
```

#### macOS
```
/Applications/Google Chrome.app/Contents/MacOS/Google Chrome
/Applications/Chromium.app/Contents/MacOS/Chromium
~/Applications/Google Chrome.app/Contents/MacOS/Google Chrome
/usr/bin/google-chrome
/usr/local/bin/chrome
```

#### Linux
```
/usr/bin/google-chrome
/usr/bin/google-chrome-stable
/usr/bin/chromium
/usr/bin/chromium-browser
/snap/bin/chromium
/opt/google/chrome/chrome
```

### Custom Chrome Path

Specify a custom Chrome path using `BrowserConfig`:

```python
from playwrightauthor import Browser, BrowserConfig

config = BrowserConfig(
    chrome_path="/opt/google/chrome/chrome"
)

with Browser(config=config) as browser:
    page = browser.new_page()
    page.goto("https://example.com")
```

## Chrome for Testing

### Automatic Downloads

Chrome for Testing offers stable builds for automation:

```python
from playwrightauthor.browser.installer import ChromeInstaller

installer = ChromeInstaller()

# Install specific version
chrome_path = installer.install_version("119.0.6045.105")

# Install latest version
chrome_path = installer.install_latest()

# Install with progress callback
def progress(downloaded: int, total: int):
    percent = (downloaded / total) * 100
    print(f"Progress: {percent:.1f}%")

chrome_path = installer.install_latest(progress_callback=progress)
```

### Version Management

```python
from playwrightauthor.browser.installer import get_chrome_versions

# List all versions
versions = get_chrome_versions()
print(f"Latest version: {versions[0]}")
print(f"Total versions: {len(versions)}")

# Filter by milestone
v119 = [v for v in versions if v.startswith("119.")]
print(f"Chrome 119 builds: {v119}")
```

### Cache Management

```python
from playwrightauthor.browser.installer import ChromeCache

cache = ChromeCache()

# List installed versions
installed = cache.list_installed()
print(f"Installed versions: {installed}")

# Keep last 3, remove the rest
cache.cleanup_old_versions(keep_count=3)

# Clear entire cache
cache.clear_all()

# Show cache size in MB
size_mb = cache.get_cache_size() / (1024 * 1024)
print(f"Cache size: {size_mb:.1f} MB")
```

## Process Management

### Launch Parameters

Chrome starts with automation-friendly flags:

```python
DEFAULT_CHROME_ARGS = [
    "--remote-debugging-port=9222",
    "--no-first-run",
    "--no-default-browser-check",
    "--disable-background-networking",
    "--disable-background-timer-throttling",
    "--disable-renderer-backgrounding",
    "--disable-backgrounding-occluded-windows",
    "--disable-client-side-phishing-detection",
    "--disable-default-apps",
    "--disable-dev-shm-usage",
    "--disable-extensions",
    "--disable-features=TranslateUI",
    "--disable-hang-monitor",
    "--disable-ipc-flooding-protection",
    "--disable-popup-blocking",
    "--disable-prompt-on-repost",
    "--disable-sync",
    "--disable-web-resources",
    "--enable-automation",
    "--enable-logging",
    "--log-level=0",
    "--password-store=basic",
    "--use-mock-keychain",
]
```

### Process Monitoring

```python
from playwrightauthor.browser.process import ChromeProcessManager

manager = ChromeProcessManager()

# List Chrome processes
processes = manager.get_chrome_processes()
for proc in processes:
    print(f"PID: {proc.pid}, Command: {' '.join(proc.cmdline())}")

# Check if port is free
port_available = manager.is_port_available(9222)
print(f"Port 9222 available: {port_available}")

# Wait for Chrome to start
manager.wait_for_chrome_ready(port=9222, timeout=30)
```

### Graceful Shutdown

```python
from playwrightauthor.browser.process import shutdown_chrome

# Try clean shutdown
shutdown_chrome(graceful=True, timeout=10)

# Force kill if needed
shutdown_chrome(graceful=False)
```

## Connection Management

### WebSocket Connection

Playwright connects to Chrome over WebSocket:

```python
from playwrightauthor.connection import ChromeConnection

connection = ChromeConnection(debug_port=9222)

# Connect
browser = connection.connect()

# Check connection health
healthy = connection.is_healthy()
print(f"Connection healthy: {healthy}")

# Reconnect if broken
if not healthy:
    browser = connection.reconnect()
```

### Connection Pooling

```python
from playwrightauthor.connection import ConnectionPool

pool = ConnectionPool(max_connections=5)

# Get a connection
conn = pool.get_connection()

# Return it when done
pool.return_connection(conn)

# Close all connections
pool.close_all()
```

## Browser State Management

### Persistent State

```python
from playwrightauthor.state_manager import BrowserStateManager

state_manager = BrowserStateManager()

# Save browser state
state_manager.save_state({
    "chrome_path": "/path/to/chrome",
    "version": "119.0.6045.105",
    "profile_path": "/path/to/profile",
    "last_used": "2024-01-15T10:30:00Z"
})

# Load state
state = state_manager.load_state()
print(f"Last used Chrome: {state.get('chrome_path')}")

# Validate state
valid = state_manager.is_state_valid(state)
```

### Profile Management

```python
from playwrightauthor.browser.profile import ProfileManager

profile_manager = ProfileManager()

# Create profile
profile_path = profile_manager.create_profile("automation_profile")

# List profiles
profiles = profile_manager.list_profiles()
print(f"Available profiles: {profiles}")

# Clone profile
new_profile = profile_manager.clone_profile(
    source="automation_profile",
    target="backup_profile"
)

# Delete profile
profile_manager.delete_profile("old_profile")
```

## Advanced Browser Management

### Custom Browser Launcher

```python
from playwrightauthor.browser.launcher import BrowserLauncher

class CustomLauncher(BrowserLauncher):
    def get_launch_args(self) -> list[str]:
        args = super().get_launch_args()
        args.extend([
            "--custom-flag=value",
            "--another-custom-flag"
        ])
        return args
    
    def pre_launch_hook(self):
        print("Launching Chrome...")

    def post_launch_hook(self, process):
        print(f"Chrome PID: {process.pid}")

launcher = CustomLauncher()
browser = launcher.launch()
```

### Browser Health Monitoring

```python
from playwrightauthor.monitoring import BrowserMonitor

monitor = BrowserMonitor()

# Start periodic checks
monitor.start_monitoring(interval=30)

# Get health status
health = monitor.get_health_status()
print(f"Browser health: {health}")

# Get metrics
metrics = monitor.get_metrics()
print(f"Memory: {metrics['memory_mb']} MB")
print(f"CPU: {metrics['cpu_percent']}%")

# Stop monitoring
monitor.stop_monitoring()
```

### Error Recovery

```python
from playwrightauthor.browser.recovery import BrowserRecovery

recovery = BrowserRecovery()

# Try to recover browser
try:
    browser = recovery.recover_browser()
except Exception as e:
    print(f"Recovery failed: {e}")
    browser = recovery.create_fresh_browser()
```

## Configuration for Browser Management

### Browser Manager Configuration

```python
from playwrightauthor import BrowserConfig

config = BrowserConfig(
    # Installation
    install_dir="~/.cache/playwrightauthor/chrome",
    download_timeout=300,  # 5 minutes
    
    # Process
    launch_timeout=30,
    debug_port=9222,
    kill_existing=True,
    
    # Connection
    connect_timeout=10,
    connect_retries=3,
    
    # Monitoring
    health_check_interval=60,
    auto_restart=True,
)
```

## Troubleshooting Browser Management

### Common Issues

1. **Port already in use**:
```python
from playwrightauthor.browser.process import find_available_port

# Get an open port
port = find_available_port(start_port=9222)
config = BrowserConfig(debug_port=port)
```

2. **Permission errors**:
```bash
# Fix on Linux/macOS
chmod +x ~/.cache/playwrightauthor/chrome/*/chrome
```

3. **Download failures**:
```python
from playwrightauthor.browser.installer import ChromeInstaller

installer = ChromeInstaller()
# Use alternative download URL
installer.set_download_url("https://mirror.example.com/chrome/")
```

## Next Steps

- Set up [Authentication](authentication.md) for persistent sessions
- Learn about [Advanced Features](advanced-features.md)
- Review [Troubleshooting](troubleshooting.md) for browser errors
- Check [API Reference](api-reference.md) for method details