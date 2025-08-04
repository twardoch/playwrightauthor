# PlaywrightAuthor + FastAPI Integration

This example demonstrates how to build a web scraping API service using PlaywrightAuthor with FastAPI.

## Features Demonstrated

- **Async API Endpoints**: High-performance async web scraping endpoints
- **Browser Pool Management**: Efficient browser resource management
- **Error Handling**: Robust error handling and response formatting
- **Rate Limiting**: Basic rate limiting for API protection
- **Data Extraction**: Common web scraping patterns and data extraction
- **Authentication Handling**: Managing authenticated scraping scenarios
- **Caching**: Response caching for improved performance

## Installation

```bash
pip install playwrightauthor fastapi uvicorn python-multipart
```

## Running the API

```bash
# Development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production server
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

### Basic Scraping
- `GET /scrape?url={url}` - Basic page scraping
- `POST /scrape/batch` - Batch scraping multiple URLs
- `GET /scrape/screenshot?url={url}` - Page screenshot generation

### Content Extraction
- `GET /extract/title?url={url}` - Extract page title
- `GET /extract/links?url={url}` - Extract all links
- `GET /extract/text?url={url}` - Extract page text content
- `POST /extract/custom` - Custom CSS selector extraction

### Advanced Features
- `GET /scrape/authenticated?url={url}&profile={profile}` - Authenticated scraping
- `GET /scrape/wait?url={url}&selector={selector}` - Wait for element scraping
- `GET /health` - API health check

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

Set environment variables:
- `BROWSER_POOL_SIZE`: Number of browser instances (default: 3)
- `REQUEST_TIMEOUT`: Request timeout in seconds (default: 30)
- `RATE_LIMIT_REQUESTS`: Requests per minute (default: 60)
- `CACHE_TTL`: Cache time-to-live in seconds (default: 300)