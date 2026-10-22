---
this_file: issues/340-direct-review.md
---

# Issue 340 direct review — 2026-10-22

Reviewed the new session/options/optional-engine/CLI ownership paths and the
Poe manager/auth/export/pool integration directly. No reviewer agent was used.
The code-review skill stub references an unavailable get_skill_content tool;
that external methodology was not loaded or claimed as a completed skill gate.

## Findings fixed and verified

- Async cancellation could release a profile lease while its option-preparation
  thread continued writing profile data. A regression demonstrated the premature
  second lease acquisition. Shielded owned-task completion now keeps the lease
  through preparation and cleanup; cancellation still propagates afterwards.
- CLI status originally described an unowned active profile as stopped. It now
  reports profile_in_use and refuses to send it a stop request. Verified against
  the live Poe update profile and with a regression test.
- CLI owner files require a valid token and matching PID creation time. Stale or
  malformed tokens cannot create arbitrary stop paths. Stop requests are private
  files and are processed cooperatively by the session that owns that token.
- Root pytest collected live examples and repeatedly displayed native notices.
  Default discovery is now tests/, live examples require explicit opt-in, and
  offline tests intercept the real dialog entry point. All 31 live examples skip
  without opt-in; root unit tests finish without native UI.

## Current evidence and limits

159 PlaywrightAuthor tests pass with 24 skips; targeted session/options/CLI type
checks and changed-module Ruff pass. The paired installed wheel passes a real
async native session. Real CLI subprocess run/status/stop and optional headless
restart checks are recorded separately. Poe regression passes 228 tests.

The full forced headless Poe update completed: 497 valid unique bots, 476 scraped
prices, 20 undisclosed rates and one rendering timeout. A three-bot headless retry
succeeded on two bots and repeated that timeout. The user authorized traditional
headed fallback on failure; its incremental run completed successfully (492 valid bots, 473 prices, 19
undisclosed rates, no scraping failures). Catalogue discovery changed eight old
IDs and added three; the timeout ID is no longer in the discovered catalogue.
Controlled macOS arm64 attention testing now records 190 samples with the same
iTerm AXTextArea, no frontmost-app change, no new browser windows and no Spaces
notifications. The earlier uncontrolled FontLab focused-object change is kept.
No headed/headless full-dataset parity, Intel hardware, actual keystroke delivery,
Stage Manager layout, localized provider rejection or full Google/Apple/email-OTP/MFA
matrix is claimed.
Earlier focus failure is retained despite a later clean-wheel 122-sample pass.
The headed fallback terminal result and saved data have been audited. Final
delivery includes the explicitly authorized commit/push in both repositories.
Unmeasured hardware/provider cells remain explicitly outside the user-selected
sample acceptance, with no implied success.
