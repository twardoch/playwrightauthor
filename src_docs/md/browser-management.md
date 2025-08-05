# Browser Management

PlaywrightAuthor handles the entire browser lifecycle automatically, from finding or installing Chrome to managing browser processes and connections. This chapter explains how browser management works under the hood.

## Browser Lifecycle

### 1. Browser Discovery

PlaywrightAuthor searches for Chrome installations in this order:

1. **Environment variable**: `PLAYWRIGHTAUTHOR_CHROME_PATH`
2. **System installations**: Standard Chrome/Chromium locations
3. **Downloaded instances**: Previously downloaded Chrome for Testing
4. **Fresh download**: Download latest Chrome for Testing

```python
from playwrightauthor.browser import finder

# Find Chrome executable
chrome_path = finder.find_chrome()
print(f"Found Chrome at: {chrome_path}")

# Search specific locations
locations = finder.get_chrome_locations()
for location in locations:
    print(f"Checking: {location}")
```

### 2. Chrome Installation

If no suitable Chrome is found, PlaywrightAuthor downloads Chrome for Testing:

```python
from playwrightauthor.browser import installer

# Download Chrome for Testing
chrome_path = installer.download_chrome()
print(f"Downloaded Chrome to: {chrome_path}")

# Check available versions
versions = installer.get_available_versions()
print(f"Available versions: {versions[:5]}")  # Latest 5 versions
```

### 3. Process Management

PlaywrightAuthor manages Chrome processes carefully:

```python
from playwrightauthor.browser import process

# Launch Chrome with debugging
proc = process.launch_chrome(
    executable_path="/path/to/chrome",
    debug_port=9222,
    user_data_dir="/path/to/profile"
)

# Check if Chrome is running with debugging
is_running = process.is_chrome_debug_running(port=9222)
print(f"Chrome debug running: {is_running}")

# Kill existing Chrome instances
process.kill_chrome_instances()
```

### 4. Connection Establishment

Finally, Playwright connects to the Chrome instance:

```python
from playwrightauthor.connection import connect_to_chrome

# Connect to debugging Chrome
browser = connect_to_chrome(debug_port=9222)
print(f"Connected to browser: {browser}")
```

## Browser Discovery Details

### Chrome Search Locations

PlaywrightAuthor searches over 20 locations per platform:

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

```python
from playwrightauthor import Browser, BrowserConfig

# Use specific Chrome installation
config = BrowserConfig(
    chrome_path="/opt/google/chrome/chrome"
)

with Browser(config=config) as browser:
    page = browser.new_page()
    page.goto("https://example.com")
```

## Chrome for Testing

### Automatic Downloads

Chrome for Testing provides stable builds for automation:

```python
from playwrightauthor.browser.installer import ChromeInstaller

installer = ChromeInstaller()

# Download specific version
chrome_path = installer.install_version("119.0.6045.105")

# Download latest stable
chrome_path = installer.install_latest()

# Download with progress callback
def progress_callback(downloaded: int, total: int):
    percent = (downloaded / total) * 100
    print(f"Download progress: {percent:.1f}%")

chrome_path = installer.install_latest(progress_callback=progress_callback)
```

### Version Management

```python
from playwrightauthor.browser.installer import get_chrome_versions

# Get all available versions
versions = get_chrome_versions()
print(f"Latest version: {versions[0]}")
print(f"Available versions: {len(versions)}")

# Filter by milestone
major_119 = [v for v in versions if v.startswith("119.")]
print(f"Chrome 119 versions: {major_119}")
```

### Cache Management

```python
from playwrightauthor.browser.installer import ChromeCache

cache = ChromeCache()

# List installed versions
installed = cache.list_installed()
print(f"Installed versions: {installed}")

# Remove old versions
cache.cleanup_old_versions(keep_count=3)

# Clear all cached Chrome
cache.clear_all()

# Get cache size
size_mb = cache.get_cache_size() / (1024 * 1024)
print(f"Cache size: {size_mb:.1f} MB")
```

## Process Management

### Launch Parameters

Chrome is launched with specific parameters for automation:

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

# Monitor Chrome processes
processes = manager.get_chrome_processes()
for proc in processes:
    print(f"PID: {proc.pid}, Command: {proc.cmdline()}")

# Check debug port availability
port_available = manager.is_port_available(9222)
print(f"Port 9222 available: {port_available}")

# Wait for Chrome to be ready
manager.wait_for_chrome_ready(port=9222, timeout=30)
```

### Graceful Shutdown

```python
from playwrightauthor.browser.process import shutdown_chrome

# Attempt graceful shutdown first
shutdown_chrome(graceful=True, timeout=10)

# Force kill if needed
shutdown_chrome(graceful=False)
```

## Connection Management

### WebSocket Connection

Playwright connects to Chrome via WebSocket:

```python
from playwrightauthor.connection import ChromeConnection

connection = ChromeConnection(debug_port=9222)

# Establish connection
browser = connection.connect()

# Connection health check
is_healthy = connection.is_healthy()
print(f"Connection healthy: {is_healthy}")

# Reconnect if needed
if not is_healthy:
    browser = connection.reconnect()
```

### Connection Pooling

```python
from playwrightauthor.connection import ConnectionPool

pool = ConnectionPool(max_connections=5)

# Get connection from pool
connection = pool.get_connection()

# Return to pool when done
pool.return_connection(connection)

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

# Load browser state
state = state_manager.load_state()
print(f"Last used Chrome: {state.get('chrome_path')}")

# Check if state is valid
is_valid = state_manager.is_state_valid(state)
```

### Profile Management

```python
from playwrightauthor.browser.profile import ProfileManager

profile_manager = ProfileManager()

# Create new profile
profile_path = profile_manager.create_profile("automation_profile")

# List existing profiles
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
        print("Preparing to launch Chrome...")
    
    def post_launch_hook(self, process):
        print(f"Chrome launched with PID: {process.pid}")

launcher = CustomLauncher()
browser = launcher.launch()
```

### Browser Health Monitoring

```python
from playwrightauthor.monitoring import BrowserMonitor

monitor = BrowserMonitor()

# Start monitoring
monitor.start_monitoring(interval=30)  # Check every 30 seconds

# Check browser health
health = monitor.get_health_status()
print(f"Browser health: {health}")

# Get performance metrics
metrics = monitor.get_metrics()
print(f"Memory usage: {metrics['memory_mb']} MB")
print(f"CPU usage: {metrics['cpu_percent']}%")

# Stop monitoring
monitor.stop_monitoring()
```

### Error Recovery

```python
from playwrightauthor.browser.recovery import BrowserRecovery

recovery = BrowserRecovery()

# Attempt to recover from browser failure
try:
    browser = recovery.recover_browser()
except Exception as e:
    print(f"Recovery failed: {e}")
    # Fallback to fresh browser instance
    browser = recovery.create_fresh_browser()
```

## Configuration for Browser Management

### Browser Manager Configuration

```python
from playwrightauthor import BrowserConfig

config = BrowserConfig(
    # Installation settings
    install_dir="~/.cache/playwrightauthor/chrome",
    download_timeout=300,  # 5 minutes
    
    # Process settings
    launch_timeout=30,
    debug_port=9222,
    kill_existing=True,
    
    # Connection settings
    connect_timeout=10,
    connect_retries=3,
    
    # Health monitoring
    health_check_interval=60,
    auto_restart=True,
)
```

## Troubleshooting Browser Management

### Common Issues

1. **Port already in use**:
```python
from playwrightauthor.browser.process import find_available_port

# Find alternative port
port = find_available_port(start_port=9222)
config = BrowserConfig(debug_port=port)
```

2. **Permission errors**:
```bash
# Fix Chrome permissions on Linux/macOS
chmod +x ~/.cache/playwrightauthor/chrome/*/chrome
```

3. **Download failures**:
```python
from playwrightauthor.browser.installer import ChromeInstaller

installer = ChromeInstaller()
# Use mirror or specific endpoint
installer.set_download_url("https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/")
```

## Next Steps

- Configure [Authentication](authentication.md) for persistent sessions
- Explore [Advanced Features](advanced-features.md) for complex scenarios
- Check [Troubleshooting](troubleshooting.md) for browser-specific issues
- Review [API Reference](api-reference.md) for detailed method documentation