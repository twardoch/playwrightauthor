---
this_file: docs/architecture.md
layout: default
title: Architecture
nav_order: 6
---

# Architecture

PlaywrightAuthor is intentionally small. It wraps Playwright setup around a persistent Chrome for Testing process.

## Main Flow

1. Resolve configuration from defaults, config files, and environment.
2. Resolve the requested profile.
3. Resolve the profile's stable debug port.
4. Find Chrome for Testing.
5. Install Chrome for Testing with `@puppeteer/browsers` if needed.
6. Launch Chrome with `--remote-debugging-port` and the profile user data directory.
7. Start Playwright.
8. Connect Playwright to the running browser over CDP.
9. Return a normal Playwright `Browser`.

## Key Modules

| Module | Role |
| --- | --- |
| `author.py` | `Browser` and `AsyncBrowser` context managers |
| `browser_manager.py` | Ensures a browser profile is running |
| `browser/finder.py` | Locates Chrome for Testing, including Puppeteer cache paths |
| `browser/installer.py` | Installs Chrome through `npx @puppeteer/browsers` |
| `browser/launcher.py` | Starts Chrome with CDP and profile arguments |
| `state_manager.py` | Stores profile metadata and stable debug ports |
| `dialognano.py` | Native/tkinter/terminal dialog helper |
| `connection.py` | CDP health and retry connection helpers |
| `engines/chrome.py` | Chrome engine adapter |

## State

State is stored in platform-appropriate app data directories through `platformdirs`. Each profile has:

- metadata in `browser_state.json`;
- a persistent user data directory;
- a stable debug port.

## Browser Engine Boundary

The default engine is Chrome for Testing. A CloakBrowser adapter exists in the codebase, but the documented path is Chrome for Testing because it is the supported and tested default for persistent authenticated Playwright automation.

## Why Chrome For Testing

Regular Chrome user profiles are not a reliable target for this workflow. Chrome for Testing is the automation-oriented browser build, and installing it through Puppeteer's browser manager gives a predictable cache layout that PlaywrightAuthor can discover.

## Dialog Boundary

All suppression behavior lives in `dialognano.notify_interactive_task()`. Higher-level code passes only:

```python
notify_interactive_task(
    task="Complete sign-in.",
    profile="google-primary",
    service="Gemini",
    suppress=True,
)
```

This keeps callers simple and ensures one place controls fallback dialog behavior.
