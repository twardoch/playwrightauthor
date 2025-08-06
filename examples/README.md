# PlaywrightAuthor Examples

This directory contains example scripts demonstrating how to use PlaywrightAuthor for various automation tasks.

## Scraping Examples

### 🔔 GitHub Notifications Scraper
**File:** `scrape_github_notifications.py`

Demonstrates how to scrape your GitHub notifications after logging in once.

```bash
python examples/scrape_github_notifications.py
```

**Features:**
- Automatic session persistence (log in once, use forever)
- Extracts notification titles and repository names
- Handles logged-out state gracefully

### 💼 LinkedIn Feed Scraper
**File:** `scrape_linkedin_feed.py`

Shows how to scrape posts from your LinkedIn feed with infinite scroll support.

```bash
python examples/scrape_linkedin_feed.py
```

**Features:**
- Scrapes post headlines, authors, and timestamps
- Handles infinite scroll to load more posts
- Avoids duplicate posts during scrolling
- Configurable number of posts to scrape

## First Time Setup

1. Install PlaywrightAuthor:
   ```bash
   pip install playwrightauthor
   ```

2. Run any example script:
   ```bash
   python examples/scrape_github_notifications.py
   ```

3. **On first run:** A browser window will open. Log into the service (GitHub, LinkedIn, etc.) using your credentials.

4. **Subsequent runs:** The script will use your saved session automatically - no login required!

## Tips

- Use `Browser(verbose=True)` for debugging connection issues
- Your login sessions are stored locally and persist between runs
- Different profiles can be used for different accounts: `Browser(profile="work")`
- Sessions are stored in platform-specific locations (e.g., `~/.playwrightauthor/` on macOS/Linux)

## Test Examples

The `pytest/` subdirectory contains test examples showing how to write automated tests using PlaywrightAuthor with pytest.

## FastAPI Integration

The `fastapi/` subdirectory demonstrates how to build web scraping APIs using PlaywrightAuthor with FastAPI.