---
this_file: docs/installation.md
layout: default
title: Installation
nav_order: 2
---

# Installation

## Requirements

- Python 3.12 or newer.
- Node.js with `npx`.
- Microsoft Playwright Python package, installed as a PlaywrightAuthor dependency.
- Chrome for Testing installed through `@puppeteer/browsers` or discoverable in the Puppeteer cache.

## Install The Package

In an application project:

```bash
uv add playwrightauthor
```

For local development in this repository:

```bash
uv sync
uv run playwrightauthor --help
```

## Install Chrome For Testing

```bash
npx @puppeteer/browsers install chrome@stable
```

PlaywrightAuthor looks for Chrome for Testing in the Puppeteer cache before falling back to other supported locations. If no executable is found, it can call the same Puppeteer browser installer internally.

{: .note }
Chrome for Testing is used instead of a regular Chrome user profile because current Chrome profile restrictions make regular user-profile CDP automation unreliable for this use case.

## Verify A Profile

```bash
playwrightauthor status --profile google-primary
```

Expected output includes:

- the selected profile name;
- the resolved debug port;
- the Chrome executable path;
- the profile user data directory.

## First Browser Launch

```bash
playwrightauthor run --profile google-primary --service Gemini
```

When the visible browser opens, complete the sign-in, consent, captcha, or other manual step. The session persists in that profile.

## Use From Python

```python
from playwrightauthor import Browser

with Browser(profile="google-primary", service="Gemini") as browser:
    page = browser.get_page()
    page.goto("https://gemini.google.com/")
```

`get_page()` reuses an existing page/context when possible, which preserves the signed-in browser session.
