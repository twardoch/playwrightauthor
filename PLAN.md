# this_file: PLAN.md

## Issue 340: decision and acceptance contract — 2026-10-22

Scope: run authenticated automation without interrupting macOS work, with explicit
human login and persistent identities shared between interactive and headless runs.

### Analysis of the three reports

Report 1 (lines 1–379) proposes Camoufox first and offscreen/windowless headed
Chromium. Its unconditional OAuth and Cloudflare success claims are unsupported;
offscreen placement and background tabs do not prove absence of focus changes.
Report 2 (380–698) correctly identifies destructive process discovery, dialogs,
missing async page helpers, profile locking and login interruption. Its hidden
LSUIElement app-copy/watchdog, automatic headed escalation, global headless default,
user-agent spoofing and mock keychain proposals add risk and are not adopted.
Report 3 (699–929) provides the strongest route: additive context-based sessions,
true headless Chrome, native Chromium/Firefox, explicit login and ownership checks.
Adopt that architecture while preserving legacy Browser/AsyncBrowser defaults.

Use existing Playwright persistent contexts, psutil and standard OS locking rather
than a custom browser framework. Chrome for Testing remains primary. Native
Chromium and Firefox are supported alternatives; Cloak keeps compatibility.
Camoufox stays optional with its own profile and compatibility tests. Edge/WebKit
and Lightpanda are evaluated separately; do not advertise Lightpanda for OAuth or
screenshots. Reject unsupported capabilities explicitly. Hidden/background modes
are deferred: true headless is the only default promising no visible UI.

Official API references consulted:
- https://developer.chrome.com/docs/automation-and-testing/headless
- https://playwright.dev/python/docs/api/class-browsertype
- https://playwright.dev/python/docs/auth

Authentication is a separate service-level decision, never inferred merely from
cookie names. Auto mode returns AUTH_REQUIRED without opening a window. Human
login must preserve redirects, popups, OTP and MFA; provider rejection is reported,
never bypassed. Profiles are engine/account-specific and never normal browser data.

### Ownership decision after implementation probes

New BrowserSession/AsyncBrowserSession use native persistent contexts for CfT
as well as Chromium and Firefox. This is the simpler safe route identified for
review in the first checkpoint: Playwright owns the browser lifetime and closes
it with the context, eliminating a new detached-process registry/refcount scheme.
Legacy Browser/AsyncBrowser keep CDP, with exact executable/profile/mode checks
and serialized startup. New profiles use profiles/<engine>/<identity>; Chrome's
legacy profiles remain in place. Nothing is automatically copied or migrated.
This preserves the full context/session goal while reducing custom lifecycle code.

### Verification gates

Offline tests prove argument propagation, prompts, ownership, locks, teardown,
page isolation, error codes and cancellation. Real browser tests must separately
prove persistence after restart, matching profile/mode, simultaneous jobs and
unrelated-process survival. macOS acceptance samples frontmost application and
visible browser windows across cold launch, navigation, new tab and shutdown.
Poe acceptance requires a fresh signed-in probe, balance and the user-selected live update sample;
provider/architecture matrix results must record observed failures and unavailable
hardware honestly. Mocks and a generic website cannot prove those gates.

Do not publish or migrate profiles implicitly. Move only freshly verified work
from the following implementation list into CHANGELOG.md; retain outstanding live
gates until evidence exists. Preserve earlier unrelated plans below.

### Final acceptance selected by the user (2026-10-22)

Use a small live headless pricing sample, including recovery of the full batch's
single rendering timeout. Run a traditional headed fallback only if that sample
fails. Complete direct regression, package, persistence, isolation and macOS
attention checks, then commit and push both repositories. Full headed/headless
parity, additional provider methods, Intel hardware, typed-text delivery and Stage
Manager remain documented follow-up coverage rather than inferred successes.
Verified issue 340 implementation tasks are recorded in CHANGELOG.md.

---

# Development Plan for PlaywrightAuthor

## Chrome for Testing Exclusivity & Session Reuse ✅ COMPLETED (2025-08-05)

### Goal
Make PlaywrightAuthor exclusively use Chrome for Testing due to Google's CDP restrictions on regular Chrome, and implement session reuse workflow for better developer experience.

### Completed Tasks
- [x] Updated browser finder to only search for Chrome for Testing paths
- [x] Modified process management to reject regular Chrome processes  
- [x] Added launch validation to ensure only Chrome for Testing is used
- [x] Fixed Chrome for Testing executable permissions issue on macOS
- [x] Implemented `get_page()` method for session reuse
- [x] Added `playwrightauthor browse` CLI command for persistent browser
- [x] Updated all examples to use session reuse workflow
- [x] Documented pre-authorized sessions workflow as recommended approach

### Original Requirements Verification ✅ COMPLETED
- [x] **Browser Management**: Chrome for Testing discovery, installation, launch, connection
- [x] **Authentication & Onboarding**: Profile persistence, onboarding UI, session reuse
- [x] **Playwright Integration**: Context managers returning standard Browser objects
- [x] **User Experience**: Simple API, comprehensive CLI, helpful error messages

## Remaining Development Tasks

### Pre-commit Hooks
- [ ] Configure pre-commit framework with ruff, mypy, bandit
- [ ] Add security scanning with bandit for sensitive code patterns
- [ ] Integrate with CI/CD pipeline for automated checks

### Semantic Versioning
- [ ] Note: Already using hatch-vcs for git-based versioning
- [ ] Document release process and version tagging strategy

## Selectable Browser Engine Support (Chrome & CloakBrowser) ✅ COMPLETED

### Goal
Implement selectable browser engines so users can use either Chrome for Testing (default) or CloakBrowser (for enhanced stealth/anti-bot protection) by setting `engine` in `BrowserConfig` or using the `PLAYWRIGHTAUTHOR_ENGINE` env variable.

### Tasks
- [x] Updated `src/playwrightauthor/browser/process.py` to correctly detect both Chrome for Testing and CloakBrowser (`chromium` / `cloakbrowser` / `chromium-` paths).
- [x] Updated `src/playwrightauthor/browser/launcher.py` to allow CloakBrowser's binary paths and accept optional extra launch arguments.
- [x] Refactored `src/playwrightauthor/author.py` to delegate the launch and connection steps to the corresponding engine adapter.
- [x] Implemented the `CloakEngineAdapter` in `src/playwrightauthor/engines/cloak.py` with lazy loading of the private `cloakbrowser` package.
- [x] Wrote tests for both Chrome and Cloak engine adapters.
- [x] Added CLI support for the `--engine` option and display engine information in `status` and `diagnose` commands.

