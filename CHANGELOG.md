# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added

#### 🚀 Chrome for Testing Exclusivity & Session Reuse ✅ MAJOR ENHANCEMENT

- **Exclusive Chrome for Testing Support**:
  - PlaywrightAuthor now exclusively uses Chrome for Testing (not regular Chrome)
  - Google has disabled CDP automation with user profiles in regular Chrome
  - Chrome for Testing is the official Google build designed for automation
  - Updated all browser discovery, installation, and launch logic to reject regular Chrome
  - Clear error messages explain why Chrome for Testing is required
  - Comprehensive permission fixes for Chrome for Testing on macOS (all helper executables)

- **Session Reuse Workflow**:
  - New `get_page()` method on Browser/AsyncBrowser classes for session reuse
  - Reuses existing browser contexts and pages instead of creating new ones
  - Maintains authenticated sessions across script runs without re-login
  - Intelligent page selection (skips extension pages, reuses existing tabs)
  - Perfect for workflows that require persistent authentication state

- **Developer Workflow Enhancement**:
  - New `playwrightauthor browse` CLI command launches Chrome for Testing in CDP mode
  - Browser stays running after command exits for other scripts to connect
  - Detects if Chrome is already running to avoid multiple instances
  - Enables manual login once, then automated scripts can reuse the session
  - Example workflow:
    1. Run `playwrightauthor browse` to launch browser
    2. Manually log into services (Gmail, GitHub, LinkedIn, etc.)
    3. Run automation scripts that use `browser.get_page()` to reuse sessions

### Fixed

- **Chrome Process Management** (2025-08-06):
  - Now automatically kills Chrome for Testing processes running without debug port and relaunches them
  - Removed the requirement for users to manually close Chrome when it's running without debugging
  - `ensure_browser()` now properly launches Chrome after killing non-debug instances
  - Fixed `launch_chrome()` and `launch_chrome_with_retry()` to properly return the Chrome process
  - This ensures automation always works without manual intervention and browser status can be verified

- **Chrome for Testing Installation**:
  - Fixed critical issue where Chrome for Testing lacked execute permissions after download
  - Added comprehensive permission setting for all executables in Chrome.app bundle
  - Fixed helper executables (chrome_crashpad_handler, etc.) permission issues
  - Resolved "GPU process isn't usable" crashes on macOS

### Changed

- **Browser Discovery**: Removed all regular Chrome paths from finder.py
- **Process Management**: Only accepts Chrome for Testing processes, rejects regular Chrome
- **Error Messages**: Updated throughout to explain Chrome for Testing requirement
- **Examples**: Updated to use `browser.get_page()` for session reuse

#### 📚 Documentation Quality Assurance ✅ COMPLETED

- **Doctest Integration**:
  - Complete doctest system for all code examples in docstrings
  - 29 passing doctests across author.py (6), config.py (23), cli.py (0), and repl modules
  - Safe, non-executing examples for browser automation code using code-block format
  - Automated example verification integrated with pytest test suite
  - Proper separation of executable tests vs documentation examples
  - Created dedicated `tests/test_doctests.py` with pytest integration
  - Configured doctest with proper flags for reliable example verification
  - Smart example management distinguishing executable tests from documentation

#### 🎯 Visual Documentation & Architecture Excellence ✅ COMPLETED

- **Comprehensive Authentication Guides**:
  - Step-by-step authentication guides for Gmail, GitHub, LinkedIn with detailed code examples
  - Service-specific troubleshooting with common issues and solutions
  - Interactive troubleshooting flowcharts using Mermaid diagrams
  - Security best practices and monitoring guidance for each service

- **Complete Architecture Documentation**:
  - Detailed browser lifecycle management flow diagrams with Mermaid
  - Component interaction architecture visualization with sequence diagrams
  - Error handling and recovery workflow charts
  - Complete visual documentation in `docs/architecture/` with enterprise-level detail

#### 🖥️ Platform-Specific Documentation Excellence ✅ COMPLETED

- **macOS Platform Guide**:
  - Complete M1/Intel architecture differences with detection and optimization
  - Comprehensive security permissions guide (Accessibility, Screen Recording, Full Disk Access)
  - Homebrew integration for both Intel and Apple Silicon architectures
  - Gatekeeper and code signing solutions with programmatic handling
  - Performance optimization with macOS-specific Chrome flags

- **Windows Platform Guide**:
  - UAC considerations with programmatic elevation and admin privilege checking
  - Comprehensive antivirus whitelisting (Windows Defender exclusions management)
  - PowerShell execution policies with script integration and policy management
  - Multi-monitor and high DPI support with Windows-specific optimizations
  - Corporate proxy configuration and Windows services integration

- **Linux Platform Guide**:
  - Distribution-specific Chrome installation for Ubuntu/Debian, Fedora/CentOS/RHEL, Arch, Alpine
  - Comprehensive Docker configuration with multi-stage builds and Kubernetes deployment
  - Display server configuration (X11, Wayland, Xvfb) with virtual display management
  - Security configuration (SELinux, AppArmor) with custom policies
  - Performance optimization with Linux-specific Chrome flags and resource management

#### ⚡ Performance Optimization Documentation ✅ COMPLETED

- **Comprehensive Performance Guide**:
  - Browser resource optimization strategies with memory, CPU, and network optimization
  - Advanced memory management with leak detection and monitoring systems
  - Connection pooling with browser pools and page recycling strategies
  - Real-time performance monitoring with dashboards and profiling tools
  - Performance debugging with memory leak detection and bottleneck analysis

#### 🔗 Documentation Link Checking System ✅ COMPLETED

- **Automated Link Validation**:
  - Comprehensive link checker script (`scripts/check_links.py`) with full markdown support
  - Validates both internal links (files and sections) and external URLs
  - Concurrent processing with configurable workers and timeout settings
  - Detailed reporting with line numbers and specific error messages
  - Found and catalogued 51 broken links across 18 documentation files

- **CI/CD Integration**:
  - GitHub Actions workflow (`.github/workflows/link-check.yml`) for automated checking
  - PR integration with intelligent commenting and result summaries
  - Weekly scheduled runs to catch external link rot
  - Automatic issue creation for broken links with actionable guidance
  - Artifact storage and professional reporting with truncation handling

- **Professional Features**:
  - HTTP retry logic with proper User-Agent headers
  - Caching system to avoid duplicate external URL checks
  - JSON output support for programmatic integration
  - Configurable failure behavior for different CI scenarios
  - Comprehensive error categorization and fix suggestions

#### ♿ Documentation Accessibility Testing System ✅ COMPLETED

- **Comprehensive Accessibility Validation**:
  - Advanced accessibility checker script (`scripts/check_accessibility.py`) with WCAG 2.1 compliance
  - Multi-category analysis: heading structure, image alt text, link quality, table accessibility
  - Language clarity checking and list structure validation
  - Professional reporting with specific WCAG guideline references
  - Found and catalogued 118 accessibility violations across 18 documentation files

- **WCAG 2.1 & Section 508 Compliance**:
  - Heading hierarchy validation (H1→H2→H3 structure enforcement)
  - Image alt text quality assessment with generic text detection
  - Link text accessibility validation (eliminates "click here" patterns)
  - Table header structure validation for screen reader compatibility
  - Language clarity analysis for cognitive accessibility

- **Enterprise CI/CD Integration**:
  - GitHub Actions workflow (`.github/workflows/accessibility-check.yml`) for automated testing
  - PR integration with detailed accessibility violation reports and remediation guidance
  - Weekly scheduled compliance monitoring with automatic issue creation
  - Configurable severity thresholds (error/warning/info levels)
  - Professional reporting with WCAG 2.1 Success Criteria mapping

- **Professional Quality Assurance**:
  - 6 major accessibility categories validated automatically
  - Severity-based issue classification with actionable recommendations
  - CI/CD artifact storage with 30-day retention
  - JSON output support for programmatic accessibility monitoring
  - Comprehensive remediation guidance with specific fix instructions

### Planned Features
- Enhanced documentation with visual guides and workflow diagrams
- Plugin architecture for extensibility
- Advanced browser profile management with encryption
- Visual documentation and platform-specific guides

## [1.0.10] - 2025-08-04

### Added

#### 🔍 Production Monitoring & Automatic Recovery ✅ MAJOR MILESTONE

- **Browser Health Monitoring System**:
  - Continuous health monitoring with configurable check intervals (5-300 seconds)
  - Chrome DevTools Protocol (CDP) connection health checks
  - Browser process lifecycle monitoring with crash detection
  - Performance metrics collection (CPU, memory, response times)
  - Background monitoring threads for sync and async browser instances

- **Automatic Crash Recovery**:
  - Smart browser restart logic with configurable retry limits
  - Exponential backoff for restart attempts
  - Graceful connection cleanup before restart
  - Process-aware recovery that detects zombie processes
  - Maintains profile and authentication state across restarts

- **Comprehensive Monitoring Configuration**:
  - New `MonitoringConfig` class with full control over monitoring behavior
  - Enable/disable monitoring, crash recovery, and metrics collection
  - Configurable check intervals and restart limits
  - Environment variable support for all monitoring settings
  - Integration with existing configuration management system

- **Production Metrics & Diagnostics**:
  - Real-time performance metrics (memory usage, CPU usage, page count)
  - CDP response time tracking for connection health
  - Detailed crash and restart statistics
  - Metrics retention with configurable history limits
  - Session-end metrics summary in logs

### Changed

- **Enhanced Browser Classes**: Both `Browser` and `AsyncBrowser` now include automatic monitoring
- **Resource Management**: Improved cleanup during crash recovery scenarios
- **Configuration System**: Extended to support comprehensive monitoring settings

### Technical Improvements

- **Enterprise-Grade Reliability**: Automatic browser crash detection and recovery
- **Performance Observability**: Real-time metrics for production environments
- **Zero-Overhead Design**: Monitoring can be disabled for low-resource scenarios
- **Thread-Safe Architecture**: Proper threading and asyncio integration

## [1.0.9] - 2025-08-04

### Added

#### 🎯 Smart Error Recovery & User Guidance

- **Enhanced Exception System**:
  - Base `PlaywrightAuthorError` class now includes "Did you mean...?" suggestions
  - All exceptions provide actionable solutions with specific commands to run
  - Context-aware error messages with pattern matching for common issues
  - Help links to relevant documentation sections
  - Professional error formatting with emojis for better readability

- **New Exception Types**:
  - `ConnectionError` - Specific guidance for Chrome connection failures
  - `ProfileError` - Clear messages for profile management issues
  - `CLIError` - Command-line errors with fuzzy-matched suggestions

- **Improved Error Handling**:
  - `browser_manager.py` - Enhanced error messages with full context and suggestions
  - `connection.py` - Replaced generic errors with specific `ConnectionError` exceptions
  - Pattern-based error detection provides targeted troubleshooting guidance
  - Exponential backoff retry logic with detailed failure reporting

- **Enhanced CLI Interface**:
  - **Smart Command Suggestions**: Fuzzy matching for mistyped commands with "Did you mean...?" suggestions
  - **Health Check Command**: Comprehensive `health` command validates entire setup
    - Chrome installation verification
    - Connection health testing with response time monitoring
    - Profile setup validation
    - Browser automation capability testing
    - System compatibility checks
    - Actionable feedback with specific fix commands
  - **Interactive Setup Wizard**: New `setup` command provides guided first-time user setup
    - Step-by-step browser validation and configuration
    - Platform-specific setup recommendations (macOS, Windows, Linux)
    - Service-specific authentication guidance (Google, GitHub, LinkedIn, etc.)
    - Real-time issue detection and troubleshooting
    - Authentication completion validation with success indicators
  - **Professional Error Handling**: CLI errors use consistent formatting with helpful guidance

- **Enhanced Onboarding System**:
  - **Intelligent Issue Detection**: Auto-detects common authentication and setup problems
    - JavaScript errors that block authentication flows
    - Cookie restrictions and browser permission issues
    - Popup blockers interfering with OAuth processes
    - Network connectivity and third-party cookie problems
    - Platform-specific permission requirements
  - **Service-Specific Guidance**: Contextual help for popular authentication services
    - Gmail/Google with 2FA setup instructions
    - GitHub with personal access token recommendations
    - LinkedIn, Microsoft Office 365, Facebook, Twitter/X
    - Real-time service detection based on current page URL
  - **Enhanced Monitoring**: Proactive setup guidance with periodic health checks
    - Real-time authentication activity detection
    - Contextual troubleshooting based on detected issues
    - Service-specific guidance when users navigate to login pages
    - Comprehensive setup reports with actionable recommendations

### Changed

- **Error Message Quality**: Transformed from technical errors to user-friendly guidance
- **Connection Handling**: All connection failures now provide specific troubleshooting steps
- **Developer Experience**: Error messages guide users to exact commands for resolution
- **CLI Usability**: Enhanced command-line interface with intelligent error recovery and comprehensive health validation

## [1.0.8] - 2025-08-04

### Added

#### 📚 Comprehensive Documentation Excellence ✅ MAJOR MILESTONE

- **World-Class API Documentation**:
  - Complete `Browser` class documentation (3,000+ chars) with comprehensive usage examples
  - Realistic authentication workflows showing login persistence across script runs
  - Common issues troubleshooting section with macOS permissions and connection problems
  - Context manager behavior documentation with resource cleanup explanations
  - Multiple profile management examples for work/personal account separation

- **Complete `AsyncBrowser` Documentation**:
  - Detailed async patterns documentation (3,800+ chars) with concurrent automation examples
  - Performance considerations and best practices for high-throughput scenarios
  - FastAPI integration example for web scraping services
  - Async vs sync decision guide with use case recommendations
  - Concurrent profile management for multiple account automation

- **Professional CLI Documentation**:
  - Enhanced CLI class with comprehensive usage overview and command examples
  - Detailed `status()` command documentation with troubleshooting output examples
  - Complete `clear_cache()` documentation with safety warnings and use cases
  - Comprehensive `profile()` command documentation with table/JSON output examples
  - Example outputs for all commands showing success and error scenarios

#### 🎯 Essential Usage Patterns & User Experience

- **"Common Patterns" Section in README**:
  - Authentication workflow demonstrating persistent login sessions
  - Production-ready error handling with exponential backoff retry patterns
  - Multi-account profile management with practical email checking example
  - Interactive REPL development workflow with live debugging examples
  - High-performance async automation with concurrent page processing
  - Comprehensive quick reference guide with most common commands and patterns

- **Real-World Integration Examples**:
  - Authentication persistence across script runs (first-time setup vs subsequent runs)
  - Robust error handling for production automation with timeout management
  - Multiple account management with profile isolation
  - Concurrent scraping with rate limiting and resource management
  - CLI command integration within REPL for seamless development

### Changed

- **Documentation Quality**: Transformed from basic API references to comprehensive user guides
- **Developer Experience**: Added practical examples for every major use case and common issue
- **Onboarding**: New users can now master PlaywrightAuthor in minutes with guided examples
- **Error Resolution**: Clear troubleshooting guidance integrated throughout documentation

### Technical Improvements

- **Self-Documenting Code**: All public APIs now include realistic usage examples
- **User-Centric Design**: Documentation focuses on practical use cases rather than technical details
- **Production Readiness**: Error handling patterns and best practices prominently featured
- **Interactive Development**: REPL usage patterns clearly documented for rapid prototyping

## [1.0.7] - 2025-08-04

### Added

#### 🚀 Interactive REPL System ✅ MAJOR MILESTONE
- **Complete REPL Workbench Implementation**:
  - Interactive REPL mode accessible via `playwrightauthor repl` command
  - Advanced tab completion for Playwright APIs, CLI commands, and Python keywords
  - Persistent command history across sessions stored in user config directory
  - Rich syntax highlighting and error handling with traceback display
  - Seamless CLI command integration within REPL using `!` prefix
  - Real-time Python code evaluation with browser context management
  - Professional welcome banner and contextual help system

- **Technical Architecture**:
  - Complete `src/playwrightauthor/repl/` module with production-ready code
  - `engine.py`: Core REPL loop with prompt_toolkit integration (217 lines)
  - `completion.py`: Context-aware completion engine for Playwright objects
  - Integration with existing CLI infrastructure for seamless command execution
  - Support for both synchronous and asynchronous browser operations

### Changed
- **Dependencies**: Added `prompt_toolkit>=3.0.0` for advanced REPL functionality
- **CLI Interface**: Enhanced with interactive `repl` command for live browser automation
- **Type Annotations**: Improved forward reference handling in author.py for better compatibility

### Technical Improvements
- **Code Quality**: All REPL code passes ruff linting and formatting standards
- **Developer Experience**: Transformed PlaywrightAuthor into interactive development platform
- **Accessibility**: REPL provides immediate feedback and exploration capabilities for Playwright APIs

## [1.0.6] - 2025-08-04

### Added
- **Enhanced Documentation & User Experience**:
  - Modernized README.md with structured feature sections and emoji-based organization
  - Updated installation instructions with `pip install playwrightauthor` 
  - Comprehensive CLI documentation covering all available commands
  - Current package architecture overview with detailed module descriptions
  - Key components section explaining core API and browser management
  - Professional feature presentation showcasing performance and reliability

### Changed
- **Documentation Structure**: 
  - Replaced outdated file tree examples with current `src/` layout architecture
  - Streamlined README.md by removing extensive code examples in favor of practical key components
  - Updated PLAN.md and TODO.md with refined priorities for 100% package completion
  - Improved user-facing documentation for better adoption and onboarding

### Removed
- Detailed internal code examples from README.md (moved focus to practical usage)
- Outdated package layout documentation

## [1.0.5] - 2025-08-04

### Added

#### Phase 4: User Experience & CLI Enhancements ✅ COMPLETED
- **Enhanced CLI Interface**:
  - Complete profile management with `profile` command (list, show, create, delete, clear)
  - Configuration viewing and management with `config` command  
  - Comprehensive diagnostic checks with `diagnose` command including connection health
  - Version and system information with `version` command
  - Multiple output formats support (Rich tables, JSON)
  - Color-coded status messages and professional formatting

#### Phase 3: Elegance and Performance ✅ COMPLETED
- **Core Architecture Refactoring** (COMPLETED):
  - Complete state management system with `state_manager.py` and `BrowserState` TypedDict
  - JSON-based state persistence to user config directory with atomic writes
  - State validation and migration system for version compatibility
  - Comprehensive configuration management with `config.py` and dataclass-based structure
  - Environment variable support with `PLAYWRIGHTAUTHOR_*` prefix
  - Configuration validation with proper error handling
  - Browser module reorganization with proper `__all__` exports and typing
  
- **Performance Optimization** (COMPLETED):
  - Lazy loading system for Playwright imports with `lazy_imports.py`
  - Chrome executable path caching in state manager  
  - Lazy browser initialization patterns in context managers
  - Lazy loading for psutil and requests modules
  - Connection health checks with comprehensive CDP diagnostics
  - Connection retry logic with exponential backoff in Browser classes
  - Enhanced debugging info and error messages for connection issues
  - New `connection.py` module with `ConnectionHealthChecker` class

#### Phase 4: User Experience & CLI Enhancements ✅ MAJOR PROGRESS
- **Enhanced CLI Interface** (MOSTLY COMPLETED):
  - Complete profile management with `profile` command (list, show, create, delete, clear)
  - Configuration viewing and management with `config` command
  - Comprehensive diagnostic checks with `diagnose` command including connection health
  - Version and system information with `version` command
  - Multiple output formats support (Rich tables, JSON)
  - Color-coded status messages and professional formatting

#### Phase 1: Robustness and Error Handling ✅
- **Enhanced Exception System**: Added specialized exception classes (`BrowserInstallationError`, `BrowserLaunchError`, `ProcessKillError`, `NetworkError`, `TimeoutError`)
- **Retry Mechanisms**: Implemented configurable retry logic for network requests and browser operations
- **Process Management**: Enhanced process killing with graceful termination → force kill fallback
- **Launch Verification**: Added `wait_for_process_start()` to ensure Chrome debug port availability
- **Download Progress**: Real-time progress reporting with SHA256 integrity checking
- **Smart Login Detection**: Detects authentication via cookies, localStorage, and sessionStorage
- **Enhanced Onboarding UI**: Professional step-by-step interface with animated status indicators
- **Comprehensive Utils Tests**: 17 new test cases for paths and logging modules

#### Phase 2: Cross-Platform Compatibility ✅
- **Enhanced Chrome Finder**: Platform-specific Chrome discovery with 20+ locations per platform
  - Windows: 32/64-bit support, registry lookup, user installations
  - Linux: Snap, Flatpak, distribution-specific paths
  - macOS: ARM64/x64 support, Homebrew, user applications
- **CI/CD Pipeline**: GitHub Actions workflow for multi-platform testing
  - Matrix testing on Ubuntu, Windows, macOS (latest + macOS-13)
  - Automated linting, type checking, and coverage reporting
  - Build and release automation with PyPI publishing
- **Platform-Specific Tests**: 15+ test cases with mock system calls
- **Integration Tests**: 25+ comprehensive tests covering all major scenarios
- **Chrome Version Detection**: `get_chrome_version()` function for compatibility checks

### Changed

- **Project Structure**: Migrated to modern `src/` layout
- **Build System**: Switched from setuptools to hatch + hatch-vcs for git-tagged versioning
- **Error Handling**: All operations now have proper timeout and retry logic
- **Browser Management**: Refactored into separate modules (finder, installer, launcher, process)
- **Logging**: Enhanced debug logging throughout with detailed path checking

### Fixed

- **Process Management**: Fixed unreliable process killing across platforms
- **Network Operations**: Added proper timeout handling for all HTTP requests
- **Path Detection**: Fixed Chrome executable finding on all platforms
- **Error Messages**: Improved user-facing error messages with actionable guidance

### Technical Improvements

- **Code Quality**: Configured ruff for linting and formatting
- **Type Safety**: Added type hints throughout the codebase
- **Test Coverage**: Significantly improved with unit, integration, and platform tests
- **Performance**: Optimized Chrome discovery with lazy path generation
- **Documentation**: Updated all file path references for new structure

## [1.0.4] - 2025-08-04

### Added
- Enhanced project documentation with AI assistant integration guides
- Comprehensive codebase analysis tools (`llms.txt`, `llms_tldr.txt`)
- Multi-assistant development workflows (CLAUDE.md, GEMINI.md, AGENTS.md)

## [1.0.3] - 2025-08-04

### Added
- Production-ready browser management system
- Comprehensive test suite with platform-specific testing
- Enhanced error handling and retry mechanisms

## [1.0.2] - 2025-08-04

### Added
- State management and configuration systems
- Lazy loading optimizations for improved performance
- Connection health monitoring and diagnostics

## [1.0.1] - 2025-08-04

### Added
- Complete migration to `src/` project layout
- Enhanced browser module organization
- Cross-platform compatibility improvements

## [1.0.0] - 2025-08-04

### Added
- First stable release of PlaywrightAuthor
- Complete implementation of all planned Phase 1-3 features
- Production-ready browser automation with authentication

## [0.1.0] - 2025-08-03

### Added

- Initial implementation of the `playwrightauthor` library.
- `Browser` and `AsyncBrowser` context managers to provide authenticated Playwright browser instances.
- `browser_manager.py` to handle the automatic installation and launching of Chrome for Testing.
- `cli.py` with a `status` command to check the browser's state.
- `onboarding.py` and `templates/onboarding.html` for first-time user guidance.
- Utility modules for logging (`logger.py`) and path management (`paths.py`).
- `pyproject.toml` for project metadata and dependency management.
- Basic smoke tests for the `Browser` and `AsyncBrowser` classes.
- Comprehensive `PLAN.md` and `TODO.md` for development tracking.
