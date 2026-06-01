---
this_file: docs/profiles.md
layout: default
title: Profiles
nav_order: 3
---

# Profiles

A profile is a persistent Chrome user data directory plus a stable Chrome DevTools Protocol port.

Profiles let one machine keep separate signed-in browser sessions for different services, accounts, or projects.

## List Profiles

```bash
playwrightauthor profile list
playwrightauthor profile list --format json
```

The listing includes:

- profile name;
- creation and last-used timestamps;
- stable debug port;
- user data directory.

## Create Or Show A Profile

Profiles are created automatically when first used, but you can create one explicitly:

```bash
playwrightauthor profile create --name google-primary
playwrightauthor profile show --name google-primary
```

## Launch Concurrent Profiles

```bash
playwrightauthor run --profile google-primary --service Gemini
playwrightauthor run --profile google-secondary --service NotebookLM
```

The default profile uses the base debug port, usually `9222`. Non-default profiles receive the next available stable port and keep it in PlaywrightAuthor state.

## Check One Profile

```bash
playwrightauthor status --profile google-primary
```

This checks or launches that profile, not the default profile.

## Delete Profiles

```bash
playwrightauthor profile delete --name old-profile
```

The default profile cannot be deleted through the CLI.

## Naming Guidance

Use names that describe purpose, not secrets:

```text
google-primary
google-secondary
github-work
testing
```

Avoid putting email addresses, customer names, or tokens in profile names. Profile names can appear in logs, prompts, and config files.
