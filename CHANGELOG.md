# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added

#### Phase 3: Elegance and Performance ✅ MAJOR PROGRESS
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
