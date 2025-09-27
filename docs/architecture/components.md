# Component Architecture

This document describes the components that make up PlaywrightAuthor's architecture.

## Core Components Overview

```mermaid
graph TB
    subgraph "Public API Layer"
        Browser[Browser Class]
        AsyncBrowser[AsyncBrowser Class]
        CLI[CLI Interface]
    end
    
    subgraph "Management Layer"
        BrowserManager[BrowserManager]
        ConnectionManager[ConnectionManager]
        StateManager[StateManager]
        ConfigManager[ConfigManager]
    end
    
    subgraph "Browser Operations"
        Finder[ChromeFinder]
        Installer[ChromeInstaller]
        Launcher[ChromeLauncher]
        Process[ProcessManager]
    end
    
    subgraph "Support Services"
        Monitor[BrowserMonitor]
        Logger[Logger]
        Paths[PathManager]
        Exceptions[Exception Classes]
    end
    
    Browser --> BrowserManager
    AsyncBrowser --> BrowserManager
    CLI --> Browser
    
    BrowserManager --> Finder
    BrowserManager --> Installer
    BrowserManager --> Launcher
    BrowserManager --> Process
    BrowserManager --> ConnectionManager
    
    Browser --> StateManager
    Browser --> ConfigManager
    Browser --> Monitor
    
    Process --> Logger
    Monitor --> Logger
    Launcher --> Paths
```

## Component Details

### 1. Browser & AsyncBrowser Classes
**Location**: `src/playwrightauthor/author.py`

Main entry points for users, implementing context managers for browser lifecycle management.

```python
# Sync API
class Browser:
    """Synchronous browser context manager."""
    
    def __init__(self, profile: str = "default", **kwargs):
        """Initialize with profile and optional config overrides."""
        
    def __enter__(self) -> PlaywrightBrowser:
        """Launch/connect browser and return Playwright Browser object."""
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cleanup resources but keep Chrome running."""

# Async API  
class AsyncBrowser:
    """Asynchronous browser context manager."""
    
    async def __aenter__(self) -> PlaywrightBrowser:
        """Async launch/connect browser."""
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async cleanup resources."""
```

**Features**:
- Profile-based session management
- Automatic Chrome installation
- Connection reuse
- Health monitoring integration
- Graceful error handling

### 2. BrowserManager
**Location**: `src/playwrightauthor/browser_manager.py`

Central orchestrator for browser operations.

```mermaid
sequenceDiagram
    participant User
    participant BrowserManager
    participant Finder
    participant Installer
    participant Launcher
    participant Connection
    
    User->>BrowserManager: ensure_browser()
    BrowserManager->>Finder: find_chrome()
    
    alt Chrome not found
        Finder-->>BrowserManager: None
        BrowserManager->>Installer: install_chrome()
        Installer-->>BrowserManager: chrome_path
    else Chrome found
        Finder-->>BrowserManager: chrome_path
    end
    
    BrowserManager->>Launcher: launch_chrome()
    Launcher-->>BrowserManager: process_info
    
    BrowserManager->>Connection: connect_playwright()
    Connection-->>BrowserManager: browser_instance
    
    BrowserManager-->>User: browser
```

**Responsibilities**:
- Orchestrates browser discovery, installation, and launch
- Manages Chrome process lifecycle
- Handles connection establishment
- Coordinates with state manager

### 3. Configuration System
**Location**: `src/playwrightauthor/config.py`

Hierarchical configuration with sensible defaults.

```mermaid
graph LR
    subgraph "Configuration Hierarchy"
        Default[Default Config]
        File[config.toml]
        Env[Environment Variables]
        Runtime[Runtime Overrides]
        Final[Final Config]
        
        Default --> File
        File --> Env
        Env --> Runtime
        Runtime --> Final
    end
    
    subgraph "Config Categories"
        Browser[BrowserConfig]
        Connection[ConnectionConfig]
        Monitoring[MonitoringConfig]
        Paths[PathConfig]
    end
    
    Final --> Browser
    Final --> Connection
    Final --> Monitoring
    Final --> Paths
```

**Configuration Classes**:

```python
@dataclass
class BrowserConfig:
    """Browser launch configuration."""
    headless: bool = False
    debug_port: int = 9222
    viewport_width: int = 1280
    viewport_height: int = 720
    args: list[str] = field(default_factory=list)

@dataclass
class ConnectionConfig:
    """Connection settings."""
    timeout: int = 30000
    retry_attempts: int = 3
    retry_delay: float = 1.0
    health_check_timeout: int = 5000

@dataclass
class MonitoringConfig:
    """Health monitoring settings."""
    enabled: bool = True
    check_interval: float = 30.0
    enable_crash_recovery: bool = True
    max_restart_attempts: int = 3
```

### 4. State Management
**Location**: `src/playwrightauthor/state_manager.py`

Persistent state storage for browser information.

```mermaid
stateDiagram-v2
    [*] --> LoadState: Application Start
    
    LoadState --> CheckState: Read state.json
    CheckState --> ValidState: State exists & valid
    CheckState --> EmptyState: No state file
    
    ValidState --> UpdateState: Use cached data
    EmptyState --> UpdateState: Create new state
    
    UpdateState --> SaveState: State changed
    SaveState --> [*]: State persisted
    
    note right of ValidState
        Contains:
        - Chrome path
        - Chrome version
        - Profile info
        - Last check time
    end note
```

**State Structure**:
```json
{
    "version": 1,
    "chrome_path": "/path/to/chrome",
    "chrome_version": "120.0.6099.109",
    "last_check": "2024-01-20T10:30:00Z",
    "profiles": {
        "default": {
            "created": "2024-01-15T08:00:00Z",
            "last_used": "2024-01-20T10:30:00Z"
        }
    }
}
```

### 5. Browser Operations

#### ChromeFinder
**Location**: `src/playwrightauthor/browser/finder.py`

Platform-specific Chrome discovery logic.

```mermaid
graph TD
    subgraph "Platform Detection"
        Start[find_chrome_executable]
        OS{Operating System}
        
        Start --> OS
        OS -->|Windows| WinPaths[Windows Paths]
        OS -->|macOS| MacPaths[macOS Paths]
        OS -->|Linux| LinuxPaths[Linux Paths]
    end
    
    subgraph "Search Strategy"
        WinPaths --> WinSearch[Registry + Program Files]
        MacPaths --> MacSearch[Applications + Homebrew]
        LinuxPaths --> LinSearch[/usr/bin + Snap + Flatpak]
    end
    
    subgraph "Validation"
        WinSearch --> Validate[Verify Executable]
        MacSearch --> Validate
        LinSearch --> Validate
        
        Validate --> Found{Valid Chrome?}
        Found -->|Yes| Return[Return Path]
        Found -->|No| NotFound[Return None]
    end
```

**Search Locations**:
- **Windows**: Registry, Program Files, LocalAppData
- **macOS**: /Applications, ~/Applications, Homebrew
- **Linux**: /usr/bin, Snap packages, Flatpak, AppImage

#### ChromeInstaller
**Location**: `src/playwrightauthor/browser/installer.py`

Downloads and installs Chrome for Testing.

```mermaid
sequenceDiagram
    participant Installer
    participant LKGV as Chrome LKGV API
    participant Download
    participant FileSystem
    
    Installer->>LKGV: GET /last-known-good-version
    LKGV-->>Installer: {"channels": {"Stable": {...}}}
    
    Installer->>Installer: Select platform URL
    Installer->>Download: Download Chrome.zip
    
    loop Progress Updates
        Download-->>Installer: Progress %
        Installer-->>User: Update progress bar
    end
    
    Download-->>Installer: Complete
    
    Installer->>Installer: Verify SHA256
    Installer->>FileSystem: Extract archive
    FileSystem-->>Installer: Extraction complete
    
    alt Platform is macOS
        Installer->>FileSystem: Remove quarantine
        Installer->>FileSystem: Set permissions
    else Platform is Linux
        Installer->>FileSystem: Set executable
    end
    
    Installer-->>User: Installation complete
```

#### ChromeLauncher
**Location**: `src/playwrightauthor/browser/launcher.py`

Manages Chrome process launch with proper arguments.

**Launch Arguments**:
```python
CHROME_ARGS = [
    f"--remote-debugging-port={debug_port}",
    f"--user-data-dir={user_data_dir}",
    "--no-first-run",
    "--no-default-browser-check",
    "--disable-blink-features=AutomationControlled",
    "--disable-component-extensions-with-background-pages",
    "--disable-background-networking",
    "--disable-background-timer-throttling",
    "--disable-backgrounding-occluded-windows",
    "--disable-renderer-backgrounding",
    "--disable-features=TranslateUI",
    "--disable-ipc-flooding-protection",
    "--enable-features=NetworkService,NetworkServiceInProcess"
]
```

#### ProcessManager
**Location**: `src/playwrightauthor/browser/process.py`

Handles process lifecycle and monitoring.

```mermaid
stateDiagram-v2
    [*] --> FindProcess: Check existing Chrome
    
    FindProcess --> DebugProcess: Found with debug port
    FindProcess --> NormalProcess: Found without debug
    FindProcess --> NoProcess: Not found
    
    DebugProcess --> UseExisting: Reuse connection
    NormalProcess --> KillProcess: Terminate
    KillProcess --> LaunchNew: Start fresh
    NoProcess --> LaunchNew: Start fresh
    
    LaunchNew --> MonitorProcess: Process started
    UseExisting --> MonitorProcess: Process running
    
    MonitorProcess --> HealthCheck: Periodic checks
    HealthCheck --> Healthy: Process responsive
    HealthCheck --> Unhealthy: Process hung/crashed
    
    Healthy --> MonitorProcess: Continue
    Unhealthy --> RestartProcess: Recovery
    RestartProcess --> LaunchNew: Restart
```

### 6. Connection Management
**Location**: `src/playwrightauthor/connection.py`

Handles CDP connection establishment and health checks.

```python
class ConnectionManager:
    """Manages Chrome DevTools Protocol connections."""
    
    def connect_playwright(self, endpoint_url: str) -> Browser:
        """Establish Playwright connection to Chrome."""
        
    def check_health(self) -> ConnectionHealth:
        """Verify CDP endpoint is responsive."""
        
    def wait_for_ready(self, timeout: int) -> bool:
        """Wait for Chrome to be ready for connections."""
```

**Health Check Flow**:
```mermaid
graph LR
    Start[Health Check] --> Request[GET /json/version]
    Request --> Response{Response?}
    
    Response -->|200 OK| Parse[Parse JSON]
    Response -->|Timeout| Unhealthy[Mark Unhealthy]
    Response -->|Error| Unhealthy
    
    Parse --> Validate{Valid CDP?}
    Validate -->|Yes| Healthy[Mark Healthy]
    Validate -->|No| Unhealthy
    
    Healthy --> Metrics[Update Metrics]
    Unhealthy --> Retry{Retry?}
    
    Retry -->|Yes| Start
    Retry -->|No| Alert[Trigger Recovery]
```

### 7. Monitoring System
**Location**: `src/playwrightauthor/monitoring.py`

Production-grade health monitoring and recovery.

```mermaid
graph TB
    subgraph "Monitoring Components"
        Monitor[BrowserMonitor]
        Metrics[BrowserMetrics]
        HealthCheck[Health Checker]
        Recovery[Recovery Handler]
    end
    
    subgraph "Metrics Collection"
        CPU[CPU Usage]
        Memory[Memory Usage]
        Response[Response Time]
        Crashes[Crash Count]
    end
    
    subgraph "Recovery Actions"
        Restart[Restart Browser]
        Reconnect[Reconnect CDP]
        Alert[Alert User]
        Fallback[Fallback Mode]
    end
    
    Monitor --> Metrics
    Monitor --> HealthCheck
    HealthCheck --> Recovery
    
    Metrics --> CPU & Memory & Response & Crashes
    
    Recovery --> Restart
    Recovery --> Reconnect
    Recovery --> Alert
    Recovery --> Fallback
```

**Monitoring Features**:
- Periodic health checks
- Resource usage tracking
- Crash detection and recovery
- Performance metrics collection
- Configurable thresholds
- Automatic restart with backoff

### 8. CLI Interface
**Location**: `src/playwrightauthor/cli.py`

Fire-powered command-line interface.

```mermaid
graph LR
    CLI[playwrightauthor] --> Status[status]
    CLI --> ClearCache[clear-cache]
    CLI --> Login[login]
    CLI --> Profile[profile]
    CLI --> Health[health]
    
    Profile --> List[list]
    Profile --> Create[create]
    Profile --> Delete[delete]
    Profile --> Export[export]
    Profile --> Import[import]
```

**Command Examples**:
```bash
# Check browser status
playwrightauthor status

# Clear cache but keep profiles
playwrightauthor clear-cache --keep-profiles

# Manage profiles
playwrightauthor profile list
playwrightauthor profile create work
playwrightauthor profile export default backup.zip

# Interactive login
playwrightauthor login github
```

### 9. Exception Hierarchy
**Location**: `src/playwrightauthor/exceptions.py`

Structured exception handling with user guidance.

```mermaid
graph TD
    BaseException[PlaywrightAuthorError]
    
    BaseException --> BrowserError[BrowserError]
    BaseException --> ConfigError[ConfigurationError]
    BaseException --> StateError[StateError]
    
    BrowserError --> LaunchError[BrowserLaunchError]
    BrowserError --> ConnectError[BrowserConnectionError]
    BrowserError --> InstallError[BrowserInstallationError]
    
    LaunchError --> ProcessError[ProcessStartError]
    LaunchError --> PortError[PortInUseError]
    
    ConnectError --> TimeoutError[ConnectionTimeoutError]
    ConnectError --> CDPError[CDPError]
```

**Exception Features**:
- User-friendly error messages
- Suggested solutions
- Diagnostic information
- Recovery actions

### 10. Utility Components

#### Logger
**Location**: `src/playwrightauthor/utils/logger.py`

Loguru-based logging with rich formatting.

```python
def configure(verbose: bool = False) -> Logger:
    """Configure application logger."""
    logger.remove()  # Remove default handler
    
    if verbose:
        level = "DEBUG"
        format = "<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    else:
        level = "INFO"
        format = "<green>{time:HH:mm:ss}</green> | <level>{message}</level>"
    
    logger.add(sys.stderr, format=format, level=level)
    return logger
```

#### PathManager
**Location**: `src/playwrightauthor/utils/paths.py`

Cross-platform path resolution using platformdirs.

```python
def data_dir() -> Path:
    """Get platform-specific data directory."""
    # Windows: %LOCALAPPDATA%\playwrightauthor
    # macOS: ~/Library/Application Support/playwrightauthor
    # Linux: ~/.local/share/playwrightauthor
    
def cache_dir() -> Path:
    """Get platform-specific cache directory."""
    # Windows: %LOCALAPPDATA%\playwrightauthor\Cache
    # macOS: ~/Library/Caches/playwrightauthor
    # Linux: ~/.cache/playwrightauthor
```

## Component Interactions

### Startup Sequence

```mermaid
sequenceDiagram
    participant User
    participant Browser
    participant Config
    participant State
    participant BrowserManager
    participant Monitor
    
    User->>Browser: with Browser() as browser
    Browser->>Config: Load configuration
    Config-->>Browser: Config object
    
    Browser->>State: Load state
    State-->>Browser: State data
    
    Browser->>BrowserManager: ensure_browser()
    BrowserManager-->>Browser: Chrome ready
    
    Browser->>BrowserManager: connect()
    BrowserManager-->>Browser: Playwright browser
    
    Browser->>Monitor: Start monitoring
    Monitor-->>Browser: Monitor started
    
    Browser-->>User: browser instance
```

### Error Recovery Flow

```mermaid
flowchart TD
    Error[Error Detected] --> Type{Error Type}
    
    Type -->|Connection| ConnRetry[Connection Retry]
    Type -->|Process| ProcRestart[Process Restart]
    Type -->|Installation| Install[Reinstall Chrome]
    
    ConnRetry --> Success1{Success?}
    Success1 -->|Yes| Resume[Resume Operation]
    Success1 -->|No| ProcRestart
    
    ProcRestart --> Success2{Success?}
    Success2 -->|Yes| Resume
    Success2 -->|No| UserGuide[Show User Guidance]
    
    Install --> Success3{Success?}
    Success3 -->|Yes| Resume
    Success3 -->|No| UserGuide
    
    UserGuide --> Manual[Manual Intervention]
```

## Design Patterns

### 1. **Context Manager Pattern**
Used for automatic resource management:
```python
with Browser() as browser:
    # Browser is ready
    pass
# Chrome keeps running after exit
```

### 2. **Factory Pattern**
BrowserManager acts as a factory for browser instances.

### 3. **Strategy Pattern**
Platform-specific implementations for Chrome discovery.

### 4. **Observer Pattern**
Health monitoring observes browser state changes.

### 5. **Singleton Pattern**
Configuration and state managers are singletons.

## Performance Characteristics

### Memory Usage
- Base library: ~50MB
- Per browser instance: ~200MB
- Per page: ~50-100MB
- Monitoring overhead: ~10MB

### Startup Times
- Cold start (with download): 30-60s
- Cold start (Chrome installed): 2-5s
- Warm start (Chrome running): 0.5-1s
- With monitoring: +0.1s

### Connection Reliability
- Retry attempts: 3 (configurable)
- Backoff strategy: Exponential
- Health check interval: 30s (configurable)
- Recovery time: <5s typical

## Security Considerations

### Profile Isolation
Each profile maintains separate:
- Cookies and session storage
- Cache and local storage
- Extension data
- Browsing history

### Process Security
- Chrome runs with minimal privileges
- Separate user data directories
- No shared state between profiles
- Secure IPC via CDP

### Future: Encryption
- Profile data encryption at rest
- Secure credential storage
- Key derivation from user password
- Automatic lock on idle

## Additional Resources

- [Browser Lifecycle](browser-lifecycle.md)
- [Error Handling](error-handling.md)
- [API Reference](../../api/index.md)
- [Configuration Guide](../configuration/index.md)
- [Performance Tuning](../performance/optimization.md)