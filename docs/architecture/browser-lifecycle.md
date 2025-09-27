# Browser Lifecycle Management

This document details how PlaywrightAuthor manages the Chrome browser lifecycle from installation to connection management.

## Lifecycle Overview

```mermaid
graph TD
    Start([User: with Browser...]) --> Check{Chrome Running?}
    
    Check -->|Yes| Connect[Connect to Existing]
    Check -->|No| Find{Chrome Installed?}
    
    Find -->|Yes| Launch[Launch Chrome]
    Find -->|No| Install[Install Chrome]
    
    Install --> Launch
    Launch --> Wait[Wait for CDP]
    Wait --> Connect
    
    Connect --> Ready[Browser Ready]
    Ready --> Use[User Operations]
    Use --> Exit{Exit Context?}
    
    Exit -->|No| Use
    Exit -->|Yes| Cleanup[Cleanup Resources]
    Cleanup --> KeepAlive[Chrome Stays Running]
    
    style Start fill:#e1f5e1
    style Ready fill:#a5d6a5
    style KeepAlive fill:#66bb6a
```

## Phase 1: Discovery & Installation

### Chrome Discovery Process

```mermaid
flowchart LR
    subgraph "Platform Detection"
        OS{Operating System}
        OS -->|Windows| Win[Windows Paths]
        OS -->|macOS| Mac[macOS Paths]
        OS -->|Linux| Lin[Linux Paths]
    end
    
    subgraph "Search Strategy"
        Win --> WinPaths[Program Files<br/>LocalAppData<br/>Registry]
        Mac --> MacPaths[Applications<br/>User Applications<br/>Homebrew]
        Lin --> LinPaths[usr/bin<br/>Snap<br/>Flatpak]
    end
    
    subgraph "Validation"
        WinPaths --> Check[Verify Executable]
        MacPaths --> Check
        LinPaths --> Check
        Check --> Found{Valid Chrome?}
    end
    
    Found -->|Yes| Cache[Cache Path]
    Found -->|No| Download[Download Chrome]
```

**Implementation**: `src/playwrightauthor/browser/finder.py`

The finder module:
1. Generates platform-specific search paths
2. Checks common installation locations
3. Validates executable permissions
4. Caches successful finds for performance

### Chrome Installation Process

```mermaid
sequenceDiagram
    participant User
    participant Installer
    participant LKGV as Chrome LKGV API
    participant Download
    participant FileSystem
    
    User->>Installer: Chrome not found
    Installer->>LKGV: GET last-known-good-version
    LKGV-->>Installer: Version & URLs
    
    Installer->>Download: Download Chrome.zip
    Note over Download: Progress bar shown
    Download-->>Installer: Chrome binary
    
    Installer->>Installer: Verify SHA256
    Installer->>FileSystem: Extract to install_dir
    FileSystem-->>Installer: Installation complete
    Installer-->>User: Chrome ready
```

**Implementation**: `src/playwrightauthor/browser/installer.py`

Key features:
- Downloads from Google's official LKGV endpoint
- SHA256 integrity verification
- Progress reporting during download
- Atomic installation (no partial installs)

## Phase 2: Process Management

### Chrome Launch Sequence

```mermaid
stateDiagram-v2
    [*] --> CheckExisting: Launch Request
    
    state CheckExisting {
        [*] --> SearchDebugPort
        SearchDebugPort --> FoundDebug: Port 9222 Active
        SearchDebugPort --> SearchNormal: No Debug Port
        SearchNormal --> FoundNormal: Regular Chrome
        SearchNormal --> NoneFound: No Chrome
    }
    
    FoundDebug --> UseExisting: Already Perfect
    FoundNormal --> KillNormal: Kill Non-Debug
    NoneFound --> LaunchNew: Fresh Start
    
    KillNormal --> LaunchNew: Terminated
    
    state LaunchNew {
        [*] --> StartProcess
        StartProcess --> WaitForPort
        WaitForPort --> VerifyCDP
        VerifyCDP --> Success
        WaitForPort --> Retry: Timeout
        Retry --> StartProcess: Attempt < 3
        Retry --> Failed: Max Attempts
    }
    
    UseExisting --> [*]: Connected
    Success --> [*]: Connected
    Failed --> [*]: Error
```

**Implementation**: `src/playwrightauthor/browser/launcher.py`

Launch arguments:
```python
args = [
    f"--remote-debugging-port={debug_port}",
    f"--user-data-dir={user_data_dir}",
    "--no-first-run",
    "--no-default-browser-check",
    "--disable-blink-features=AutomationControlled"
]
```

### Process Monitoring

```mermaid
graph TB
    subgraph "Health Monitoring"
        Monitor[Monitor Thread/Task]
        Monitor --> Check1[CDP Health Check]
        Monitor --> Check2[Process Alive Check]
        Monitor --> Check3[Resource Usage]
    end
    
    subgraph "Metrics Collection"
        Check1 --> M1[Response Time]
        Check2 --> M2[Process Status]
        Check3 --> M3[CPU/Memory]
    end
    
    subgraph "Failure Detection"
        M1 --> D1{Timeout?}
        M2 --> D2{Zombie?}
        M3 --> D3{OOM?}
    end
    
    subgraph "Recovery Actions"
        D1 -->|Yes| Restart
        D2 -->|Yes| Restart
        D3 -->|Yes| Restart
        Restart --> Limits{Under Limit?}
        Limits -->|Yes| LaunchNew
        Limits -->|No| Fail
    end
```

**Implementation**: `src/playwrightauthor/monitoring.py`

## Phase 3: Connection Management

### CDP Connection Flow

```mermaid
sequenceDiagram
    participant Browser as Browser Class
    participant Health as Health Checker
    participant CDP
    participant Playwright
    participant Monitor
    
    Browser->>Health: Check CDP Health
    Health->>CDP: GET /json/version
    
    alt CDP Healthy
        CDP-->>Health: 200 OK + Info
        Health-->>Browser: Healthy
        Browser->>Playwright: connect_over_cdp()
        Playwright->>CDP: WebSocket Connect
        CDP-->>Playwright: Connected
        Playwright-->>Browser: Browser Instance
        Browser->>Monitor: Start Monitoring
    else CDP Unhealthy
        CDP-->>Health: Error/Timeout
        Health-->>Browser: Unhealthy
        Browser->>Browser: Retry with Backoff
    end
```

### Connection Retry Strategy

```mermaid
graph LR
    subgraph "Retry Logic"
        Attempt1[Attempt 1<br/>Wait 1s] --> Fail1{Failed?}
        Fail1 -->|Yes| Attempt2[Attempt 2<br/>Wait 2s]
        Attempt2 --> Fail2{Failed?}
        Fail2 -->|Yes| Attempt3[Attempt 3<br/>Wait 4s]
        Attempt3 --> Fail3{Failed?}
        Fail3 -->|Yes| Error[Give Up]
        
        Fail1 -->|No| Success
        Fail2 -->|No| Success
        Fail3 -->|No| Success
    end
    
    style Attempt1 fill:#ffe0b2
    style Attempt2 fill:#ffcc80
    style Attempt3 fill:#ffb74d
    style Error fill:#ff7043
    style Success fill:#66bb6a
```

**Implementation**: `src/playwrightauthor/connection.py`

## Phase 4: State Persistence

### Profile Management

```mermaid
graph TB
    subgraph "Profile Structure"
        Root[playwrightauthor/]
        Profiles[profiles/]
        Default[default/]
        Work[work/]
        Personal[personal/]
        
        Root --> Profiles
        Profiles --> Default
        Profiles --> Work  
        Profiles --> Personal
    end
    
    subgraph "Chrome Profile Data"
        Default --> D1[Cookies]
        Default --> D2[Local Storage]
        Default --> D3[Session Storage]
        Default --> D4[IndexedDB]
        Default --> D5[Cache]
        
        Work --> W1[Cookies]
        Work --> W2[Local Storage]
        Work --> W3[Session Storage]
    end
    
    subgraph "State File"
        State[state.json]
        State --> ChromePath[chrome_path]
        State --> Profiles2[profiles]
        State --> Version[version]
        State --> LastCheck[last_check]
    end
```

### Session Persistence Flow

```mermaid
sequenceDiagram
    participant User
    participant Chrome
    participant Website
    participant Profile as Profile Storage
    
    User->>Chrome: Login to Website
    Chrome->>Website: POST Credentials
    Website-->>Chrome: Set-Cookie Headers
    Chrome->>Chrome: Store in Memory
    
    Chrome->>Profile: Write Cookies DB
    Chrome->>Profile: Write Local Storage
    Chrome->>Profile: Write Session Data
    
    Note over Profile: Data persisted to disk
    
    User->>User: Close Script
    Note over Chrome: Chrome keeps running
    Note over Profile: Data remains on disk
    
    User->>Chrome: New Script Run
    Chrome->>Profile: Load Cookies DB
    Chrome->>Profile: Load Local Storage
    Profile-->>Chrome: Session Data
    
    Chrome->>Website: Request with Cookies
    Website-->>Chrome: Authenticated Content
```

## Phase 5: Cleanup & Recovery

### Graceful Shutdown

```mermaid
stateDiagram-v2
    [*] --> ExitContext: __exit__ called
    
    ExitContext --> StopMonitor: Stop Monitoring
    StopMonitor --> CollectMetrics: Get Final Metrics
    CollectMetrics --> LogMetrics: Log Performance
    
    LogMetrics --> CloseBrowser: browser.close()
    CloseBrowser --> StopPlaywright: playwright.stop()
    
    StopPlaywright --> KeepChrome: Chrome Stays Running
    KeepChrome --> [*]: Session Preserved
```

### Crash Recovery

```mermaid
flowchart TD
    Crash[Browser Crash Detected] --> Check{Recovery Enabled?}
    
    Check -->|No| Log[Log Error]
    Check -->|Yes| Count{Attempts < Max?}
    
    Count -->|No| Fail[Stop Recovery]
    Count -->|Yes| Clean[Cleanup Old Connection]
    
    Clean --> Relaunch[Launch New Chrome]
    Relaunch --> Reconnect[Connect Playwright]
    Reconnect --> Restore[Restore Monitoring]
    
    Restore --> Success{Success?}
    Success -->|Yes| Resume[Resume Operations]
    Success -->|No| Increment[Increment Counter]
    
    Increment --> Count
    
    style Crash fill:#ff7043
    style Resume fill:#66bb6a
    style Fail fill:#ff5252
```

## Performance Considerations

### Connection Pooling (Future)

```mermaid
graph TB
    subgraph "Connection Pool"
        Pool[Connection Pool Manager]
        C1[Connection 1<br/>Profile: default]
        C2[Connection 2<br/>Profile: work]
        C3[Connection 3<br/>Profile: personal]
        
        Pool --> C1
        Pool --> C2
        Pool --> C3
    end
    
    subgraph "Request Handling"
        Req1[Request Profile: default] --> Pool
        Req2[Request Profile: work] --> Pool
        Pool --> Check{Available?}
        Check -->|Yes| Reuse[Return Existing]
        Check -->|No| Create[Create New]
    end
```

### Resource Management

```mermaid
graph LR
    subgraph "Resource Monitoring"
        Monitor --> CPU[CPU Usage]
        Monitor --> Memory[Memory Usage]
        Monitor --> Handles[File Handles]
    end
    
    subgraph "Thresholds"
        CPU --> T1{> 80%?}
        Memory --> T2{> 2GB?}
        Handles --> T3{> 1000?}
    end
    
    subgraph "Actions"
        T1 -->|Yes| Throttle[Reduce Activity]
        T2 -->|Yes| GC[Force Garbage Collection]
        T3 -->|Yes| Close[Close Unused Pages]
    end
```

## Configuration Options

### Browser Launch Configuration

```python
# config.py settings that affect lifecycle
browser_config = {
    "debug_port": 9222,          # CDP port
    "headless": False,           # Show browser window
    "timeout": 30000,            # Launch timeout (ms)
    "viewport_width": 1280,      # Initial viewport
    "viewport_height": 720,
    "args": [],                  # Additional Chrome args
}

# Monitoring configuration  
monitoring_config = {
    "enabled": True,             # Enable health monitoring
    "check_interval": 30.0,      # Seconds between checks
    "enable_crash_recovery": True,
    "max_restart_attempts": 3,
}
```

### State Management Options

```python
# State persistence options
state_config = {
    "cache_chrome_path": True,   # Cache executable location
    "profile_isolation": True,   # Separate profile directories
    "state_version": 1,         # State schema version
}
```

## Additional Resources

- [Component Details](components.md)
- [Error Handling](error-handling.md)
- [Performance Guide](../performance/index.md)
- [Configuration Reference](../../api/config.md)