# Changelog

All notable changes to this project will be documented in this file.

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
