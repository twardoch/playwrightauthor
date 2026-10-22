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

## Owned sessions and additional engines

Use the additive session API when each job needs its own tab and controlled
browser shutdown. Install only the browser you need:

```bash
uv run playwright install chromium firefox
```

```python
from playwrightauthor import BrowserSession

with BrowserSession(engine="chromium", profile="work", mode="headless") as session:
    page = session.new_page()
    page.goto("https://example.com/")
    print(page.title())
```

`AsyncBrowserSession` provides the same operations with `async with` and `await`.
Sessions expose `context` and an optional `browser`; every `new_page()` or
`get_page()` creates a separate tab. Closing a session closes its owned context.
An exclusive OS-backed lease prevents concurrent writers to one engine/profile.
Different profiles remain independent; different engines never share browser data.

Modes are `headless` (default), `interactive` (explicit visible browser), and
`auto` (headless with a required service-specific `auth_probe(context) -> bool`,
async for async sessions). A rejected auto probe raises `AUTH_REQUIRED` and never
opens a login window. The generic library does not know whether a service login
has succeeded. Session state is private and should never be committed.

Engines: `chrome` uses Chrome for Testing (discoverable installation or an explicit
`executable_path`); `chromium` and `firefox` use Playwright's installed browsers.
Optional `cloak` requires its separate installation and has no provider acceptance
claim. Existing `Browser`/`AsyncBrowser` defaults and legacy CDP workflow remain.
New sessions use engine-specific directories; existing profiles are not migrated.

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

## Owned foreground sessions

```bash
playwrightauthor session run https://example.com --engine=chromium
playwrightauthor session login https://poe.com/login --profile=poe-primary
playwrightauthor session status --profile=poe-primary
playwrightauthor session stop --profile=poe-primary
```

`run` defaults to true headless and closes after navigation. Use
`--hold-seconds=60` to keep it running. `login` explicitly opens an interactive
profile for up to 300 seconds; finish sign-in and issue `session stop` in another
terminal. These commands suppress the extra modal notice. `stop` requests
cooperative cleanup by the owning CLI; it never kills or attaches to another
browser. `status` reads ownership without launching and reports `profile_in_use`
for an unowned live profile. Profile data survives close.

Results are JSON; failures use structured error codes and nonzero exit status.
Authorization stays unknown unless a service probe is supplied. For unattended
`--mode=auto`, provide both `--auth-url=https://SERVICE/protected-account-page`
and `--auth-selector=ACCOUNT_SPECIFIC_SELECTOR`. The fresh probe must receive
HTTP 200 at that endpoint and render the marker. A login redirect returns
AUTH_REQUIRED without opening a visible window. Select a genuinely protected
endpoint, not a public page. Override CfT discovery with `--executable-path=PATH`.

| Session engine | Current support |
| --- | --- |
| chrome | Chrome for Testing, persistent native context; primary |
| chromium / firefox | Playwright-managed browsers; install matching binaries |
| cloak | Optional CloakBrowser; headless persistence smoke verified |
| camoufox | Optional `playwrightauthor[camoufox]`; pinned 0.5.8 / Playwright <1.63 |
| msedge / webkit | Not exposed by this session API; BACKEND_UNSUPPORTED |
| lightpanda | Not exposed; no provider-login or screenshot support claimed |

For Camoufox, explicitly run `python -m camoufox fetch` after installing the extra.
Each profile retains its generated device configuration privately. Verified here:
macOS arm64 sync-to-async headless restart cookies and sampled device stability.
Provider authorization and interactive-mode device stability remain unverified.
Edge/WebKit are deferred to keep the tested engine matrix bounded; Playwright's
underlying support does not establish support by this package.

For a controlled macOS attention check, leave a text cursor stationary and run
`uv run scripts/verify_macos_attention.py -- .venv/bin/python scripts/verify_sessions.py --chrome-binary=PATH_TO_CFT`.
It observes the frontmost app, focused accessibility object, new browser windows
and Spaces notifications without reading text or sending keystrokes. Results
apply to that run; actual text delivery and Stage Manager layout are separate checks.
