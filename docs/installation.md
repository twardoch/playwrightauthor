---
this_file: docs/installation.md
layout: default
title: Installation
nav_order: 2
---

# Installation

## Prerequisites

You need three things before PlaywrightAuthor can work:

| Requirement | Why | Minimum version |
|---|---|---|
| **Python** | Runs your automation scripts | 3.12 |
| **Node.js** (`npx`) | Installs Chrome for Testing | Any recent LTS |
| **Chrome for Testing** | The browser PlaywrightAuthor controls | Stable channel |

> **Why "Chrome for Testing" and not my regular Chrome?**
> Regular Chrome has restrictions that make it unreliable for persistent CDP
> automation. Chrome for Testing is an identical build — same rendering engine,
> same JavaScript — but distributed specifically for automated use.  It lives in
> its own folder and never interferes with your everyday browser.

---

## Step 1 — Install the Python package

In your project:

```bash
uv add playwrightauthor
```

Without `uv`, using pip:

```bash
pip install playwrightauthor
```

---

## Step 2 — Install Chrome for Testing

### Option A — via Puppeteer browsers CLI (recommended)

```bash
npx @puppeteer/browsers install chrome@stable
```

This downloads Chrome for Testing into `~/.cache/puppeteer/`.
PlaywrightAuthor looks there first, so it finds the browser automatically.

### Option B — let PlaywrightAuthor install it for you

If `npx` is not available, run any PlaywrightAuthor command and it will
attempt to install Chrome itself:

```bash
playwrightauthor status
```

---

## Step 3 — Verify the installation

```bash
playwrightauthor status --profile google-primary
```

Expected output:

```
Profile: google-primary
Debug Port: 9223
Chrome: /Users/you/.cache/puppeteer/chrome/…/Google Chrome for Testing
Data dir: /Users/you/Library/Caches/playwrightauthor/profiles/google-primary
```

If `Chrome:` shows `None`, Chrome for Testing was not found — re-run Step 2.

---

## Step 4 — First sign-in (one time per profile)

```bash
playwrightauthor run --profile google-primary --service Gmail
```

A visible Chrome window opens. Sign in as you would normally. When you are
done, you can close the window or leave it running — PlaywrightAuthor will
reconnect to it on the next script run.

You only need to do this once per profile. The session is saved in the profile
directory and reused every time.

---

## Step 5 — Run your first script

```python
from playwrightauthor import Browser

with Browser(profile="google-primary", service="Gmail") as browser:
    page = browser.get_page()
    page.goto("https://mail.google.com/")
    print(page.title())
```

If the title starts with "Inbox", you are authenticated and ready to automate.

---

## Development installation (for contributors)

```bash
git clone https://github.com/twardoch/playwrightauthor
cd playwrightauthor
uv sync
uv run playwrightauthor --help
```

Run the test suite:

```bash
uvx hatch test
```

The test suite runs offline in under one second — no Chrome required.
