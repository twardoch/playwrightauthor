---
this_file: issues/340-session-verification.md
---

> Historical intermediate checkpoint. The final evidence and remaining matrix
> limits are recorded in [340-acceptance-matrix.md](340-acceptance-matrix.md).

# Issue 340 session verification — 2026-10-22

PA340-2 and PA340-3 are implemented. PA340-4's native engines pass the following
checks; its optional adapters and capability decisions remain open.

## Reproduce

Because these source checkouts lack usable VCS version metadata, use
`SETUPTOOLS_SCM_PRETEND_VERSION=0.0.0` for local development builds/tests only.

- `uvx hatch test`: 137 passed, 24 skipped.
- `uv run --with pytest-cov pytest tests/test_sessions.py tests/test_profile_ownership.py
  --cov=playwrightauthor.sessions --cov=playwrightauthor.profiles
  --cov=playwrightauthor.session_options --cov=playwrightauthor.session_runtime
  --cov-report=term-missing --cov-fail-under=80`: 34 passed, 92.14% coverage.
- Ruff lint/format on changed source/tests/scripts passes; targeted mypy for
  sessions/options/runtime/profiles passes. Full-tree mypy has 17 existing errors.
- `uv run playwright install chromium firefox` installs version-matched browsers.
- `uv run python scripts/verify_sessions.py --chrome-binary=PATH_TO_CFT`: real
  disposable-profile smoke outside pytest's browser mocks. See
  [runtime evidence](340-native-sessions.json). No provider credentials are used.
- `uv build --out-dir=TEMP_DIRECTORY`: build source archive then wheel. Verify
  runtime-data exclusions and exact shipped module bytes; see
  [payload audit](340-package-audit.json). Clean temporary-environment installation
  imports both public session APIs and constructs headless options successfully.

## What real runtime checks cover

Chrome for Testing 150.0.7871.24, Playwright Chromium 148.0.7778.96 and Firefox
150.0.2 each persist an expiring cookie and localStorage across context/browser
shutdown and a new async driver. A concurrent same-profile session raises
PROFILE_BUSY; a simultaneous different identity has no inherited cookies and
can close without affecting the first. Closing one task tab leaves another
usable. A separate killed Python process does not leave its file lease busy.

Two complete runs passed window/focus sampling (96 and 94 samples). Samples cover
startup, task navigation, new tabs, other profiles, restart and shutdown, reporting
only booleans/counts. The earlier legacy-launch smoke observed an unexplained
focus change once. Its cause remains unresolved; these later observations do not
prove typing-target or Spaces state or establish a universal no-interference claim.

## Iteration findings and limits

A real nested-profile test exposed Playwright's prohibition on nested sync drivers;
a per-thread shared driver fixes that while retaining isolated contexts. The
first persistence test used a session-only cookie; browsers correctly discarded
it on restart. The corrected test uses an explicit expiry and makes no promise
about session-only cookie restoration. Matching Playwright browser revisions
had to be installed; existing unrelated cached revisions were insufficient.

Cancellation originally released a lease before async context cleanup finished.
A failing test now guards cleanup shielding and re-entry rejection. A source
archive audit found local `.omc` records; explicit Hatch sdist selection excludes
them. No artifact was published.

No real Poe/provider sign-in, balance, complete update parity, Camoufox/Cloak
runtime, Intel hardware, keyboard target or Spaces acceptance has passed here.
Those remain open in both plans. Profile migrations, releases and pushes were
not performed. New contexts own their browser; legacy CDP clients attach only
after identity checks and retain their previous disconnected-process lifecycle.
