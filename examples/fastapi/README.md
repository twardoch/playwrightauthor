# PlaywrightAuthor + FastAPI Integration

This example shows how to build a web scraping API using PlaywrightAuthor and FastAPI.

## Features

- **Async API Endpoints**: Non-blocking scraping operations
- **Browser Pool Management**: Reuse browser instances for efficiency
- **Error Handling**: Proper HTTP error responses
- **Rate Limiting**: Throttle requests per minute
- **Data Extraction**: Extract titles, links, text, or custom elements
- **Authentication Handling**: Scrape pages that require login
- **Caching**: Cache results to reduce redundant work

## Installation

```bash
pip install playwrightauthor fastapi uvicorn python-multipart
```

## Running the API

```bash
# Development
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

### Basic Scraping
- `GET /scrape?url={url}` - Scrape a single page
- `POST /scrape/batch` - Scrape multiple URLs
- `GET /scrape/screenshot?url={url}` - Take a screenshot

### Content Extraction
- `GET /extract/title?url={url}` - Get page title
- `GET /extract/links?url={url}` - Get all links
- `GET /extract/text?url={url}` - Get visible text
- `POST /extract/custom` - Extract using CSS selectors

### Advanced Features
- `GET /scrape/authenticated?url={url}&profile={profile}` - Scrape with login
- `GET /scrape/wait?url={url}&selector={selector}` - Wait for an element
- `GET /health` - Health check endpoint

## Example Usage

```bash
# Basic scraping
curl "http://localhost:8000/scrape?url=https://example.com"

# Extract title
curl "http://localhost:8000/extract/title?url=https://github.com"

# Custom extraction
curl -X POST "http://localhost:8000/extract/custom" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://github.com",
    "selectors": {
      "title": "h1",
      "description": "meta[name=description]"
    }
  }'

# Batch scraping
curl -X POST "http://localhost:8000/scrape/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": ["https://example.com", "https://github.com"],
    "extract": ["title", "url"]
  }'
```

## Configuration

Environment variables:
- `BROWSER_POOL_SIZE`: Number of browser instances (default: 3)
- `REQUEST_TIMEOUT`: Timeout in seconds (default: 30)
- `RATE_LIMIT_REQUESTS`: Requests per minute (default: 60)
- `CACHE_TTL`: Cache expiry in seconds (default: 300)