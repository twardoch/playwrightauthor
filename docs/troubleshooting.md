---
this_file: docs/troubleshooting.md
layout: default
title: Troubleshooting
nav_order: 7
---

# Troubleshooting

## Stale Documentation Review

The older PlaywrightAuthor docs had three recurring problems:

- They recommended a Playwright-managed browser install path, which does not match the current Chrome for Testing profile workflow.
- They mixed service-specific auth advice with general browser-profile behavior, making it unclear which parts were package behavior and which parts were site behavior.
- They described performance and connection-pooling topics that were not the most practical first-line docs for this package.

The current docs focus on the behavior implemented in the package: Chrome for Testing, persistent profiles, profile-specific ports, CLI management, dialog prompts, and Playwright context managers.

## Chrome For Testing Not Found

Install it explicitly:

```bash
npx @puppeteer/browsers install chrome@stable
```

Then check:

```bash
playwrightauthor status --profile google-primary --verbose
```

## Wrong Profile Or Account

List profiles:

```bash
playwrightauthor profile list
```

Open the profile manually:

```bash
playwrightauthor run --profile google-primary --service "Manual check"
```

Inspect the visible browser. If it is signed into the wrong account for your task, sign out/in inside that profile or choose a different profile name.

## Port Conflicts

The default profile uses the base debug port. Non-default profiles get stable assigned ports. If `status` reports a port issue:

```bash
playwrightauthor profile list
playwrightauthor status --profile google-secondary
```

Close stale Chrome for Testing processes if needed, then retry.

## Dialog Appears In Automation

Suppress it:

```python
from playwrightauthor import Browser

with Browser(profile="google-primary", suppress_dialog=True) as browser:
    ...
```

CLI:

```bash
playwrightauthor run --profile google-primary --suppress-dialog
```

## macOS Dialog Or Browser Permission Issues

If automation cannot control the browser or windows do not behave as expected:

1. Open System Settings.
2. Check Privacy & Security permissions for your terminal or Python launcher.
3. Relaunch the terminal and browser profile.

## Profile State Looks Corrupt

Show the profile:

```bash
playwrightauthor profile show --name google-primary
```

If the profile is no longer useful:

```bash
playwrightauthor profile delete --name google-primary
playwrightauthor run --profile google-primary
```

This creates a clean profile and requires sign-in again.

## Tests

```bash
PYTHONDONTWRITEBYTECODE=1 uv run ruff check --fix src tests
PYTHONDONTWRITEBYTECODE=1 uv run ruff format src tests
PYTHONDONTWRITEBYTECODE=1 uv run pytest
```
