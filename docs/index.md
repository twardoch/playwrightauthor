---
this_file: docs/index.md
layout: default
title: Home
nav_order: 1
---

# PlaywrightAuthor

PlaywrightAuthor gives Python Playwright scripts a persistent, authenticated Chrome for Testing browser.

Use it when automation should reuse a real signed-in browser profile instead of recreating login flows in code. It manages browser discovery, Chrome for Testing installation, profile directories, stable CDP ports, and connection retries, then returns a normal Playwright `Browser`.

## Current Model

- Chrome for Testing is the primary browser.
- Chrome is installed or discovered through the Puppeteer browser cache layout.
- Each profile has its own persistent user data directory.
- Non-default profiles receive stable CDP ports, so multiple profiles can run concurrently.
- Interactive browser tasks show a small `dialognano` notice unless suppressed.

{: .warning }
Older PlaywrightAuthor docs described a Playwright-managed browser install path. That is no longer the recommended workflow for persistent authenticated profiles. Use `npx @puppeteer/browsers install chrome@stable`.

## Documentation Map

- [Installation](installation.md): install Chrome for Testing and verify a profile.
- [Profiles](profiles.md): create, launch, inspect, and run concurrent profiles.
- [Python API](python-api.md): `Browser`, `AsyncBrowser`, dialogs, and examples.
- [CLI](cli.md): practical command reference.
- [Architecture](architecture.md): how launch, profile, state, and connection pieces fit.
- [Troubleshooting](troubleshooting.md): ports, profile state, permissions, and stale docs review.

## Minimal Example

```python
from playwrightauthor import Browser

with Browser(profile="google-primary", service="Gemini") as browser:
    page = browser.get_page()
    page.goto("https://gemini.google.com/")
    print(page.title())
```
