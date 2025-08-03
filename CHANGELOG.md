# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added

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
