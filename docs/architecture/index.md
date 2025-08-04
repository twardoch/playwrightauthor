# PlaywrightAuthor Architecture

This section provides detailed insights into PlaywrightAuthor's internal architecture, component design, and system flows.

## 📐 Overview

PlaywrightAuthor is built on a modular architecture that separates concerns and provides flexibility:

```mermaid
graph TB
    subgraph "User Interface"
        CLI[CLI Commands]
        API[Python API]
        REPL[Interactive REPL]
    end
    
    subgraph "Core Layer"
        Browser[Browser Manager]
        Auth[Author Classes]
        Config[Configuration]
        State[State Manager]
    end
    
    subgraph "Browser Layer"
        Finder[Chrome Finder]
        Installer[Chrome Installer]
        Launcher[Process Launcher]
        Process[Process Manager]
    end
    
    subgraph "Support Layer"
        Monitor[Health Monitor]
        Error[Error Handler]
        Logger[Logger]
        Utils[Utilities]
    end
    
    CLI --> Auth
    API --> Auth
    REPL --> Auth
    
    Auth --> Browser
    Auth --> Config
    Auth --> State
    Auth --> Monitor
    
    Browser --> Finder
    Browser --> Installer
    Browser --> Launcher
    Browser --> Process
    
    Browser --> Error
    Monitor --> Logger
    Process --> Utils
```

## 🏗️ Core Components

### [Browser Lifecycle Management](browser-lifecycle.md)
Understanding how PlaywrightAuthor manages Chrome instances:
- Installation and discovery
- Process management
- Connection handling
- Session persistence

### [Component Architecture](components.md)
Detailed breakdown of each component:
- Author classes (Browser/AsyncBrowser)
- Configuration system
- State management
- Browser management modules

### [Error Handling & Recovery](error-handling.md)
How PlaywrightAuthor handles failures gracefully:
- Exception hierarchy
- Retry mechanisms
- User guidance system
- Crash recovery

### [Monitoring & Metrics](monitoring.md)
Production monitoring capabilities:
- Health checks
- Performance metrics
- Crash detection
- Resource tracking

## 🔄 System Flows

### Authentication Flow

```mermaid
sequenceDiagram
    participant User
    participant Browser
    participant Chrome
    participant Website
    participant Storage
    
    User->>Browser: with Browser() as browser
    Browser->>Chrome: Launch/Connect
    Chrome-->>Browser: CDP Connection
    Browser->>User: browser instance
    
    User->>Browser: page.goto("site.com")
    Browser->>Chrome: Navigate
    Chrome->>Website: HTTP Request
    Website-->>Chrome: Login Page
    
    User->>Chrome: Manual Login
    Chrome->>Website: Credentials
    Website-->>Chrome: Set Cookies
    Chrome->>Storage: Save Profile
    
    Note over Storage: Cookies, LocalStorage,<br/>SessionStorage persisted
    
    User->>Browser: exit context
    Browser->>Chrome: Keep Running
    Browser-->>User: Session Saved
```

### Connection Management

```mermaid
stateDiagram-v2
    [*] --> CheckRunning: Browser Request
    
    CheckRunning --> Connected: Already Running
    CheckRunning --> FindChrome: Not Running
    
    FindChrome --> InstallChrome: Not Found
    FindChrome --> LaunchChrome: Found
    
    InstallChrome --> LaunchChrome: Installed
    LaunchChrome --> WaitForCDP: Process Started
    
    WaitForCDP --> Connected: CDP Ready
    WaitForCDP --> Retry: Timeout
    
    Retry --> WaitForCDP: Attempt < Max
    Retry --> Error: Max Retries
    
    Connected --> [*]: Success
    Error --> [*]: Failure
```

## 🎯 Design Principles

### 1. **Separation of Concerns**
Each module has a single, well-defined responsibility:
- `browser_manager.py` - High-level orchestration
- `browser/*.py` - Specific browser operations
- `author.py` - User-facing API
- `config.py` - Configuration management

### 2. **Fail-Safe Design**
Multiple layers of error handling:
- Try graceful operations first
- Fall back to forceful methods
- Always provide user guidance
- Never leave system in bad state

### 3. **Cross-Platform Compatibility**
Platform-specific code isolated:
- `finder.py` - Platform-specific paths
- `process.py` - OS-specific process handling
- `paths.py` - Platform directory resolution

### 4. **Performance Optimization**
Lazy loading and caching throughout:
- Playwright imported only when needed
- Chrome path cached after discovery
- Connection reused when possible
- Minimal startup overhead

### 5. **User Experience First**
Every error includes:
- Clear explanation
- Suggested solution
- Exact commands to run
- Links to documentation

## 🔌 Extension Points

### Plugin Architecture (Future)

```mermaid
graph LR
    subgraph "PlaywrightAuthor Core"
        Core[Core Engine]
        Hooks[Hook System]
    end
    
    subgraph "Plugin Types"
        Auth[Auth Plugins]
        Monitor[Monitor Plugins]
        Network[Network Plugins]
    end
    
    Core --> Hooks
    Hooks --> Auth
    Hooks --> Monitor
    Hooks --> Network
    
    Auth --> OAuth[OAuth Helper]
    Auth --> SAML[SAML Helper]
    Monitor --> Metrics[Metrics Export]
    Network --> Proxy[Proxy Manager]
```

### Configuration Layers

```mermaid
graph TD
    Default[Default Config] --> File[File Config]
    File --> Env[Environment Vars]
    Env --> Runtime[Runtime Override]
    Runtime --> Final[Final Config]
    
    style Default fill:#f9f,stroke:#333
    style Final fill:#9f9,stroke:#333
```

## 📊 Performance Characteristics

### Startup Performance
- First run: ~2-5s (includes Chrome launch)
- Subsequent runs: ~0.5-1s (connection only)
- With monitoring: +0.1s overhead
- REPL mode: +0.2s for prompt toolkit

### Memory Usage
- Base: ~50MB (Python + PlaywrightAuthor)
- Per browser: ~200MB (Chrome process)
- Per page: ~50-100MB (depending on content)
- Monitoring: ~10MB (metrics storage)

### Scalability
- Profiles: Unlimited (filesystem bound)
- Concurrent browsers: System resource limited
- Pages per browser: ~50-100 recommended
- Monitoring check interval: 5-300s configurable

## 🛡️ Security Architecture

### Profile Isolation

```mermaid
graph TB
    subgraph "Profile Storage"
        Default[Default Profile]
        Work[Work Profile]
        Personal[Personal Profile]
    end
    
    subgraph "Isolation"
        Cookies1[Cookies]
        Storage1[LocalStorage]
        Cache1[Cache]
        
        Cookies2[Cookies]
        Storage2[LocalStorage]
        Cache2[Cache]
        
        Cookies3[Cookies]
        Storage3[LocalStorage]
        Cache3[Cache]
    end
    
    Default --> Cookies1 & Storage1 & Cache1
    Work --> Cookies2 & Storage2 & Cache2
    Personal --> Cookies3 & Storage3 & Cache3
    
    style Default fill:#f99
    style Work fill:#99f
    style Personal fill:#9f9
```

### Future: Encryption

```mermaid
sequenceDiagram
    participant User
    participant PA as PlaywrightAuthor
    participant KDF
    participant Storage
    
    User->>PA: Create Profile
    PA->>User: Request Password
    User->>PA: Password
    
    PA->>KDF: Derive Key
    KDF-->>PA: Encryption Key
    
    PA->>PA: Encrypt Profile Data
    PA->>Storage: Store Encrypted
    
    Note over Storage: Encrypted cookies,<br/>tokens, session data
```

## 📚 Additional Resources

- [Component Details](components.md)
- [Browser Lifecycle](browser-lifecycle.md)
- [Error Handling](error-handling.md)
- [Performance Guide](../performance/index.md)
- [API Reference](../../api/index.md)