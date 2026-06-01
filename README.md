---
this_file: README.md
---

# PlaywrightAuthor

PlaywrightAuthor gives Python Playwright scripts a persistent, authenticated Chrome for Testing browser.

It finds or installs Chrome for Testing, launches it with a persistent user profile and Chrome DevTools Protocol port, and returns a normal Playwright `Browser`. You log in once in the visible browser; later scripts reuse the same cookies and local browser state.

```python
from playwrightauthor import Browser

with Browser(profile="google-primary", service="Gemini") as browser:
    page = browser.get_page()
    page.goto("https://gemini.google.com/")
    print(page.title())
```

## Install

```bash
uv add playwrightauthor
npx @puppeteer/browsers install chrome@stable
```

The package uses Chrome for Testing, not a normal Chrome user profile. Multiple profiles can run at the same time because each profile receives a stable CDP debug port.

## CLI

```bash
playwrightauthor run --profile google-primary --service Gemini
playwrightauthor run --profile google-secondary --service NotebookLM
playwrightauthor status --profile google-primary
playwrightauthor profile list
playwrightauthor profile show --name google-primary
```

When a browser opens for sign-in, consent, captcha, or another manual step, PlaywrightAuthor shows a small `dialognano` prompt describing the service, profile, and task. Suppress it from Python with `suppress_dialog=True` or from the CLI with `--suppress-dialog`.

## Python API

```python
from playwrightauthor import Browser, AsyncBrowser

with Browser(profile="work", suppress_dialog=True) as browser:
    page = browser.get_page()
    page.goto("https://github.com/")
```

`Browser` and `AsyncBrowser` accept `profile`, `service`, `task`, `verbose`, and `suppress_dialog`.

## Documentation

Practical setup, CLI, profile, API, architecture, and troubleshooting guides live in [docs/](docs/).

Local docs preview:

```bash
cd docs
bundle install
bundle exec jekyll serve
```

## Development

```bash
PYTHONDONTWRITEBYTECODE=1 uv run ruff check --fix src tests
PYTHONDONTWRITEBYTECODE=1 uv run ruff format src tests
PYTHONDONTWRITEBYTECODE=1 uv run pytest
```
