# PlaywrightAuthor Examples

This directory contains example scripts demonstrating how to use PlaywrightAuthor for various automation tasks.

## Scraping Examples

### GitHub Notifications Scraper
**File:** `scrape_github_notifications.py`

Scrapes your GitHub notifications after a single login.

```bash
python examples/scrape_github_notifications.py
```

**Features:**
- Automatic session persistence (log in once, stay logged in)
- Extracts notification titles and repository names
- Handles logout states without crashing

### LinkedIn Feed Scraper
**File:** `scrape_linkedin_feed.py`

Scrapes posts from your LinkedIn feed, including infinite scroll support.

```bash
python examples/scrape_linkedin_feed.py
```

**Features:**
- Extracts post headlines, authors, and timestamps
- Loads additional posts via infinite scroll
- Prevents duplicate posts during scrolling
- Adjustable post count limit

## First Time Setup

1. Install PlaywrightAuthor:
   ```bash
   pip install playwrightauthor
   ```

2. Run any example:
   ```bash
   python examples/scrape_github_notifications.py
   ```

3. **First run:** A browser window opens. Log into the service manually.

4. **Future runs:** The script uses your saved session automatically.

## Tips

- Use `Browser(verbose=True)` to troubleshoot connection problems
- Sessions save locally and persist across executions
- Create separate profiles for different accounts: `Browser(profile="work")`
- Session storage location varies by platform (typically `~/.playwrightauthor/` on macOS/Linux)

## Test Examples

The `pytest/` directory contains examples of automated tests using PlaywrightAuthor with pytest.

## FastAPI Integration

The `fastapi/` directory shows how to build web scraping APIs with PlaywrightAuthor and FastAPI.