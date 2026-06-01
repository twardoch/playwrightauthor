---
this_file: docs/python-api.md
layout: default
title: Python API
nav_order: 4
---

# Python API

PlaywrightAuthor exports synchronous and asynchronous context managers:

```python
from playwrightauthor import Browser, AsyncBrowser
```

Both return normal Playwright browser objects connected over CDP.

## Sync Browser

```python
from playwrightauthor import Browser

with Browser(
    profile="google-primary",
    service="Gemini",
    task="Sign in or complete any provider consent prompt.",
) as browser:
    page = browser.get_page()
    page.goto("https://gemini.google.com/")
    print(page.title())
```

## Async Browser

```python
import asyncio

from playwrightauthor import AsyncBrowser


async def main() -> None:
    async with AsyncBrowser(profile="google-primary", service="Gemini") as browser:
        page = await browser.new_page()
        await page.goto("https://gemini.google.com/")
        print(await page.title())


asyncio.run(main())
```

## Constructor Arguments

| Argument | Meaning |
| --- | --- |
| `profile` | Persistent profile name. Defaults to `default`. |
| `service` | Human-readable service name for the interactive dialog. |
| `task` | Task text shown in the interactive dialog. |
| `suppress_dialog` | If `True`, skip the interactive dialog. |
| `verbose` | Enable detailed log output. |

## Interactive Dialogs

By default, opening a browser through `Browser`, `AsyncBrowser`, or `playwrightauthor run` calls `dialognano.notify_interactive_task()`.

The dialog explains:

- why the browser opened;
- which profile is being used;
- which service is expected;
- what manual step the user should complete.

Suppress it when running unattended:

```python
with Browser(profile="google-primary", suppress_dialog=True) as browser:
    page = browser.get_page()
```

Suppression is handled inside `dialognano.py`, so callers only pass a boolean.

## Reusing Existing Pages

The sync browser object receives a convenience `get_page()` method:

```python
with Browser(profile="google-primary") as browser:
    page = browser.get_page()
```

It prefers an existing non-extension page in the persistent context. If none exists, it creates a new page.

## Error Handling

Use normal Playwright exceptions for page-level failures. Browser setup failures are raised as PlaywrightAuthor exceptions from `playwrightauthor.exceptions`.

```python
from playwright.sync_api import TimeoutError
from playwrightauthor import Browser

try:
    with Browser(profile="google-primary", verbose=True) as browser:
        page = browser.get_page()
        page.goto("https://example.com", timeout=30_000)
except TimeoutError:
    print("The page did not load in time.")
```
