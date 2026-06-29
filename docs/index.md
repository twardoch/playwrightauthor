---
this_file: docs/index.md
layout: default
title: Home
nav_order: 1
---

# PlaywrightAuthor

**The problem it solves in one sentence:** most browser automation tools log you in from scratch on every run — PlaywrightAuthor lets your Python script open a Chrome that is already signed in, just like your everyday browser.

## What does "authenticated browser automation" mean?

When you visit Gmail or GitHub in your personal Chrome, you stay signed in because Chrome saves a *session* — cookies, local storage, and other tiny files that prove who you are. Normal automation frameworks (Playwright, Selenium) open a clean, blank browser with no sessions. They can't reuse your real sign-in.

PlaywrightAuthor bridges that gap. It:

1. Installs **Chrome for Testing** — a special Chrome build made for automation, kept separate from your everyday Chrome so it never interferes.
2. Stores browser sessions in **named profiles** (e.g. `google-primary`, `work`, `research`) so each can hold different sign-ins at the same time.
3. Returns a **standard Playwright `Browser`** object, so any existing Playwright code works without changes.

## Five-minute quick start

### 1. Install the package

```bash
uv add playwrightauthor
```

### 2. Install Chrome for Testing

```bash
npx @puppeteer/browsers install chrome@stable
```

(You need [Node.js](https://nodejs.org/) for `npx`. If you do not have it, the [installation guide](installation.md) has alternatives.)

### 3. Sign in to a service once

```bash
playwrightauthor run --profile google-primary --service Gmail
```

A visible Chrome window opens. Sign in normally. Close it when done.

### 4. Automate with your saved session

```python
from playwrightauthor import Browser

with Browser(profile="google-primary", service="Gmail") as browser:
    page = browser.get_page()
    page.goto("https://mail.google.com/")
    print(page.title())   # → "Inbox - …@gmail.com"
```

That's it. The script runs headlessly with your cookies already in place.

## Documentation map

| Guide | What it covers |
|---|---|
| [Installation](installation.md) | Installing Python package, Chrome, and verifying everything works |
| [Profiles](profiles.md) | Creating multiple sign-in profiles, running them in parallel |
| [Python API](python-api.md) | `Browser`, `AsyncBrowser`, helper methods, full examples |
| [CLI](cli.md) | All command-line commands with examples |
| [Architecture](architecture.md) | How Chrome, profiles, state, and connections fit together |
| [Troubleshooting](troubleshooting.md) | Port conflicts, stuck profiles, permission errors, and more |

## Minimal working example

```python
from playwrightauthor import Browser

with Browser(profile="google-primary", service="Gemini") as browser:
    page = browser.get_page()
    page.goto("https://gemini.google.com/")
    print(page.title())
```

`get_page()` reuses an already-open tab when possible, which keeps you signed in between script runs.
