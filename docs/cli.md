---
this_file: docs/cli.md
layout: default
title: CLI
nav_order: 5
---

# CLI

The `playwrightauthor` command manages browser installation, profile state, and local troubleshooting.

## Browser Commands

Launch a browser profile and leave it running:

```bash
playwrightauthor run --profile google-primary --service Gemini
```

Alias:

```bash
playwrightauthor browse --profile google-primary
```

Check one profile:

```bash
playwrightauthor status --profile google-primary
playwrightauthor status --profile google-primary --format json
```

Run diagnostics:

```bash
playwrightauthor diagnose
playwrightauthor health
```

Clear browser cache and local state:

```bash
playwrightauthor clear-cache
```

{: .warning }
`clear-cache` removes browser installations and profile/session data managed by PlaywrightAuthor. You will need to sign in again.

## Profile Commands

```bash
playwrightauthor profile list
playwrightauthor profile list --format json
playwrightauthor profile show --name google-primary
playwrightauthor profile create --name google-primary
playwrightauthor profile delete --name old-profile
```

## Dialog Control

Show task context:

```bash
playwrightauthor run \
  --profile google-primary \
  --service Gemini \
  --task "Finish sign-in and consent for Gemini automation."
```

Suppress the dialog:

```bash
playwrightauthor run --profile google-primary --suppress-dialog
```

## Configuration Commands

Inspect or modify config:

```bash
playwrightauthor config show
playwrightauthor config set browser.debug_port 9222
```

Use config changes carefully: profile-specific port assignment is managed by state, so most users should not change the base debug port unless `9222` conflicts with another local service.
