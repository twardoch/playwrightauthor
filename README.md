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

## First sign-in (once per profile)

```bash
playwrightauthor run --profile google-primary --service Gemini
```

A visible Chrome window opens. Sign in. The session is saved to the profile directory and reused on every subsequent script run.

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
uv run ruff check --fix src tests
uv run ruff format src tests
uvx hatch test          # runs offline in < 1 s, no Chrome needed
```

Run only the slow browser-integration tests (requires Chrome):

```bash
uv run pytest -m slow
```
