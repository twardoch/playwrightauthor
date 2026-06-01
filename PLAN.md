# Development Plan for PlaywrightAuthor

## Chrome for Testing Exclusivity & Session Reuse ✅ COMPLETED (2025-08-05)

### Goal
Make PlaywrightAuthor exclusively use Chrome for Testing due to Google's CDP restrictions on regular Chrome, and implement session reuse workflow for better developer experience.

### Completed Tasks
- [x] Updated browser finder to only search for Chrome for Testing paths
- [x] Modified process management to reject regular Chrome processes  
- [x] Added launch validation to ensure only Chrome for Testing is used
- [x] Fixed Chrome for Testing executable permissions issue on macOS
- [x] Implemented `get_page()` method for session reuse
- [x] Added `playwrightauthor browse` CLI command for persistent browser
- [x] Updated all examples to use session reuse workflow
- [x] Documented pre-authorized sessions workflow as recommended approach

### Original Requirements Verification ✅ COMPLETED
- [x] **Browser Management**: Chrome for Testing discovery, installation, launch, connection
- [x] **Authentication & Onboarding**: Profile persistence, onboarding UI, session reuse
- [x] **Playwright Integration**: Context managers returning standard Browser objects
- [x] **User Experience**: Simple API, comprehensive CLI, helpful error messages

## Remaining Development Tasks

### Pre-commit Hooks
- [ ] Configure pre-commit framework with ruff, mypy, bandit
- [ ] Add security scanning with bandit for sensitive code patterns
- [ ] Integrate with CI/CD pipeline for automated checks

### Semantic Versioning
- [ ] Note: Already using hatch-vcs for git-based versioning
- [ ] Document release process and version tagging strategy

## Selectable Browser Engine Support (Chrome & CloakBrowser)

### Goal
Implement selectable browser engines so users can use either Chrome for Testing (default) or CloakBrowser (for enhanced stealth/anti-bot protection) by setting `engine` in `BrowserConfig` or using the `PLAYWRIGHTAUTHOR_ENGINE` env variable.

### Tasks
- Update `src/playwrightauthor/browser/process.py` to correctly detect both Chrome for Testing and CloakBrowser (`chromium` / `cloakbrowser` / `chromium-` paths).
- Update `src/playwrightauthor/browser/launcher.py` to allow CloakBrowser's binary paths and accept optional extra launch arguments.
- Refactor `src/playwrightauthor/author.py` to delegate the launch and connection steps to the corresponding engine adapter.
- Implement the `CloakEngineAdapter` in `src/playwrightauthor/engines/cloak.py` with lazy loading of the private `cloakbrowser` package.
- Write tests for both Chrome and Cloak engine adapters.
- Add CLI support for the `--engine` option and display engine information in `status` and `diagnose` commands.

