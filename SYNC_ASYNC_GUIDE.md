# Sync/Async API Strategy Guide

## Overview

PlaywrightAuthor provides both synchronous and asynchronous APIs for browser automation. This guide explains when to use each, how they're implemented, and the decision-making framework for new utilities.

## Core Principles

1. **Match the I/O model**: If a function performs I/O (network, file, browser), provide async versions
2. **Keep it simple**: If a function is pure computation, prefer sync-only
3. **Playwright alignment**: Follow Playwright's own sync/async distinction
4. **Explicit is better**: Never use sync wrappers around async code (creates hidden event loops)

## Decision Matrix

Use this matrix to determine which API(s) to provide for new utilities:

| Characteristic | Sync Only | Async Only | Both APIs |
|---------------|-----------|------------|-----------|
| **I/O operations** | ❌ No | ✅ Yes | ✅ Yes if used in both contexts |
| **Pure computation** | ✅ Yes | ❌ No | ❌ No |
| **Playwright page interaction** | Depends on context | ✅ Preferred | ✅ If supporting both Browser types |
| **State management** | ✅ Yes | ❌ No | ❌ No |
| **Configuration** | ✅ Yes | ❌ No | ❌ No |

## Current Utility Classification

### Sync-Only Utilities

#### AdaptiveTimingController (`helpers/timing.py`)
**Why sync-only:** Pure state tracking dataclass with no I/O operations.

```python
from playwrightauthor.helpers.timing import AdaptiveTimingController

timing = AdaptiveTimingController()
timing.on_success()  # No I/O, just state update
wait, timeout = timing.get_timings()
```

**Risk of async version:** None needed - would add complexity without benefit.

#### html_to_markdown (`utils/html.py`)
**Why sync-only:** Pure string processing using html2text library (sync-only).

```python
from playwrightauthor.utils.html import html_to_markdown

html = "<p><strong>Hello</strong> world!</p>"
markdown = html_to_markdown(html)  # Pure function, no I/O
```

**Risk of async version:** html2text library is synchronous, async wrapper would be misleading.

#### scroll_page_incremental (`helpers/interaction.py`)
**Why sync-only:** Uses Playwright's sync `Page.evaluate()` method.

```python
from playwrightauthor import Browser
from playwrightauthor.helpers.interaction import scroll_page_incremental

with Browser() as browser:
    page = browser.page
    page.goto("https://example.com")
    scroll_page_incremental(page, scroll_distance=800)
```

**Note:** If async version needed, would need to be implemented separately using `await page.evaluate()`.

### Async-Only Utilities (Phase 3)

#### with_timeout, with_retries (`utils/timeout.py` - not yet migrated)
**Why async-only:** Built on top of asyncio primitives (asyncio.wait_for, asyncio.sleep).

```python
from playwrightauthor.utils.timeout import with_timeout, with_retries

# Wrap async operations with timeout
result = await with_timeout(
    page.wait_for_selector(".content"),
    timeout_seconds=10,
    operation_name="wait for content"
)

# Retry async operations with backoff
result = await with_retries(
    async_function,
    max_retries=3,
    backoff_multiplier=2.0
)
```

**Risk of sync version:** Would require separate event loop - not recommended.

#### BrowserPool (`pool.py` - not yet migrated)
**Why async-only:** Manages async browser connections using AsyncBrowser.

```python
from playwrightauthor.pool import BrowserPool

pool = BrowserPool(max_size=5)
await pool.start()

async with pool.acquire_page() as page:
    await page.goto("https://example.com")
    # Use page...

await pool.close()
```

**Risk of sync version:** Would hide complexity of async resource management.

### Dual API Utilities

#### extract_with_fallbacks (`helpers/extraction.py`)
**Why both:** Used in both sync (Browser) and async (AsyncBrowser) contexts.

**Sync version:**
```python
from playwrightauthor import Browser
from playwrightauthor.helpers.extraction import extract_with_fallbacks

with Browser() as browser:
    page = browser.page
    page.goto("https://example.com")

    content = extract_with_fallbacks(
        page,  # Sync Page
        selectors=['.main-content', '#content', 'article'],
        validate_fn=lambda text: len(text) > 100
    )
```

**Async version:**
```python
from playwrightauthor import AsyncBrowser
from playwrightauthor.helpers.extraction import async_extract_with_fallbacks

async with AsyncBrowser() as browser:
    page = browser.page
    await page.goto("https://example.com")

    content = await async_extract_with_fallbacks(
        page,  # Async Page
        selectors=['.main-content', '#content', 'article'],
        validate_fn=lambda text: len(text) > 100
    )
```

**Implementation pattern:**
```python
from playwright.sync_api import Page as SyncPage
from playwright.async_api import Page as AsyncPage

def extract_with_fallbacks(page: SyncPage, ...) -> str | None:
    """Sync version - no await keywords."""
    for selector in selectors:
        try:
            element = page.locator(selector).first
            if element.count() > 0:  # Sync call
                text = element.inner_text()  # Sync call
                return text
        except Exception:
            continue
    return None

async def async_extract_with_fallbacks(page: AsyncPage, ...) -> str | None:
    """Async version - all I/O uses await."""
    for selector in selectors:
        try:
            element = page.locator(selector).first
            if await element.count() > 0:  # Async call
                text = await element.inner_text()  # Async call
                return text
        except Exception:
            continue
    return None
```

## When to Choose Sync vs Async

### Choose Sync API When:
- Running simple automation scripts
- Working in non-async environments (Jupyter notebooks, simple CLI tools)
- Performance is not critical (single browser instance)
- Easier debugging and simpler code is priority

### Choose Async API When:
- Running concurrent browser operations
- Need connection pooling (BrowserPool)
- Integrating with async frameworks (aiohttp, FastAPI, asyncio-based systems)
- Performance is critical (multiple concurrent tasks)
- Using timeout/retry utilities

## Migration Patterns

### From Sync to Async
```python
# Sync (old)
from playwrightauthor import Browser

with Browser() as browser:
    page = browser.page
    page.goto("https://example.com")
    content = page.locator(".content").inner_text()

# Async (new)
from playwrightauthor import AsyncBrowser

async with AsyncBrowser() as browser:
    page = browser.page
    await page.goto("https://example.com")
    content = await page.locator(".content").inner_text()
```

### From Async to Sync (Not Recommended)
**Anti-pattern:**
```python
import asyncio

def sync_wrapper(async_func):
    """DON'T DO THIS - creates hidden event loop issues."""
    return asyncio.run(async_func())
```

**Instead:** Provide proper sync implementation or keep async-only.

## Common Pitfalls

### ❌ Don't: Mix sync/async in the same function
```python
def bad_function(page):
    """Ambiguous - which Page type?"""
    result = page.locator(".content")  # Works for both, but...
    text = result.inner_text()  # Only works for sync Page!
    return text
```

### ✅ Do: Use explicit type hints
```python
from playwright.sync_api import Page as SyncPage

def good_sync_function(page: SyncPage) -> str:
    """Explicitly sync - type checker will catch errors."""
    return page.locator(".content").inner_text()
```

```python
from playwright.async_api import Page as AsyncPage

async def good_async_function(page: AsyncPage) -> str:
    """Explicitly async - type checker will catch errors."""
    return await page.locator(".content").inner_text()
```

### ❌ Don't: Use asyncio.run() in library code
```python
def bad_sync_wrapper(page: AsyncPage):
    """Hidden event loop - breaks in async contexts!"""
    return asyncio.run(page.locator(".content").inner_text())
```

### ✅ Do: Provide separate implementations
```python
# sync_version.py
def extract_content(page: SyncPage) -> str:
    return page.locator(".content").inner_text()

# async_version.py
async def async_extract_content(page: AsyncPage) -> str:
    return await page.locator(".content").inner_text()
```

## Testing Strategy

### Sync Utilities
```python
from playwrightauthor.helpers.timing import AdaptiveTimingController

def test_adaptive_timing_speeds_up_on_success():
    """Test sync utility - no async/await needed."""
    timing = AdaptiveTimingController()

    for _ in range(3):
        timing.on_success()

    wait, _ = timing.get_timings()
    assert wait < 1.0, "Should speed up after successes"
```

### Async Utilities
```python
import pytest
from playwrightauthor.utils.timeout import with_timeout

@pytest.mark.asyncio
async def test_with_timeout_raises_on_timeout():
    """Test async utility - uses pytest-asyncio."""
    async def slow_operation():
        await asyncio.sleep(10)

    with pytest.raises(asyncio.TimeoutError):
        await with_timeout(slow_operation(), timeout_seconds=0.1)
```

### Dual API Utilities
```python
from playwrightauthor import Browser
from playwrightauthor.helpers.extraction import extract_with_fallbacks

def test_extract_with_fallbacks_sync():
    """Test sync version with Browser."""
    with Browser() as browser:
        page = browser.page
        page.goto("https://example.com")

        content = extract_with_fallbacks(
            page,
            selectors=[".content", "body"]
        )
        assert content is not None
```

```python
import pytest
from playwrightauthor import AsyncBrowser
from playwrightauthor.helpers.extraction import async_extract_with_fallbacks

@pytest.mark.asyncio
async def test_async_extract_with_fallbacks():
    """Test async version with AsyncBrowser."""
    async with AsyncBrowser() as browser:
        page = browser.page
        await page.goto("https://example.com")

        content = await async_extract_with_fallbacks(
            page,
            selectors=[".content", "body"]
        )
        assert content is not None
```

## Future Considerations

### When Adding New Utilities

1. **Start with the simplest approach**:
   - Pure computation → Sync only
   - I/O operations → Async only
   - Playwright interaction → Match Playwright's API

2. **Only add dual APIs if**:
   - Utility is commonly used in both contexts
   - Implementation is straightforward (no complex logic differences)
   - Maintenance burden is acceptable

3. **Document the decision**:
   - Add rationale to docstring
   - Update this guide with new examples
   - Include usage examples for chosen API(s)

### Deprecation Strategy

If we need to deprecate sync versions in favor of async:

1. Add deprecation warnings (Python's `warnings.warn()`)
2. Provide migration guide with examples
3. Keep sync version for 2 major releases
4. Remove in major version bump with breaking changes note

## Resources

- [Playwright Python API Documentation](https://playwright.dev/python/docs/api/class-playwright)
- [Python asyncio Documentation](https://docs.python.org/3/library/asyncio.html)
- [PEP 492 - Coroutines with async/await](https://peps.python.org/pep-0492/)

---

**Last Updated:** 2025-10-03
**Status:** Living document - update as new utilities are added
