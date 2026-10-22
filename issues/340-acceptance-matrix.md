---
this_file: issues/340-acceptance-matrix.md
---

# Issue 340 acceptance matrix — 2026-10-22

This is an observed-result matrix, not a claim that all engines/providers/hardware
are accepted. Final delivery follows the user-selected headless sample with headed
fallback on failure. No package publication was performed.

| Hardware / engine | Native persistence and task isolation | Live Poe authorization | Full update |
| --- | --- | --- | --- |
| macOS arm64 / CfT 150.0.7871.24 | Pass, sync/async and real adapter/pool | User-completed manual sign-in; fresh headless probe and refreshed CLI balance pass | 497-bot headless run complete; headed incremental fallback passes with 492 current bots |
| macOS arm64 / Chromium | Pass; Playwright 1.54 and 1.64 browser builds recorded separately | Live anonymous identity returns AUTH_REQUIRED; signed-in case not run | Not run signed-in |
| macOS arm64 / patched Firefox | Pass; Playwright 1.54 and 1.64 browser builds recorded separately | Not tested signed-in | Not run signed-in |
| macOS arm64 / Camoufox 156.0.1-beta.36 | Pass, installed 0.5.8 / Playwright 1.62.0; sync-to-async cookie and sampled device restart checks | Not tested | Not run |
| macOS arm64 / Cloak 145.0.7632.109 | Pass, installed 0.6.3 / Playwright 1.62.0; sync-to-async restart checks | Not tested | Not run |
| macOS Intel / all engines | Hardware unavailable in this workspace; not tested | Not tested | Not tested |
| Edge / WebKit / Lightpanda | Explicit BACKEND_UNSUPPORTED in this session API | No support advertised | No support advertised |

Provider method for the completed manual Poe sign-in was not recorded. It does
not establish Google, Apple, direct email/OTP, MFA, WebAuthn or refusal-matrix
coverage. The provider-refusal detector and failed-login non-export are tested
with controlled fixtures; no live provider bypass or automated password handling
was attempted. Cookie expiry/identity filtering has unit coverage; real expired
provider sessions and device revalidation remain untested.

## Native attention observations

[Controlled result](340-macos-attention-controlled.json) records 190 observations
while the text cursor was left in iTerm's AXTextArea by the user. The same focused
AX object remained selected; no frontmost-app change, new on-screen browser-window
IDs or NSWorkspace active-Space notifications occurred. The child exercised real
CfT/Chromium/Firefox adapter sessions. No text values were read or keys sent.

[Earlier uncontrolled result](340-macos-attention.json) retained FontLab as the
frontmost app with no new browser windows or Space events, but its focused AX
control changed. Cause is not attributed to the browsers or to user activity.
The controlled pass does not erase this observation. Global AX focus queries
returned an error; per-application AX queries worked. No permissions were changed.
The Workspace observer received one synthetic local bootstrap notification before
measurement, then its count was reset; zero runtime notifications were observed.

Actual typed-text delivery, Stage Manager layout and other hardware remain
unverified. These are observations over the test interval, not universal promises.
AppKit's supported Spaces notification is documented by
[Apple](https://developer.apple.com/documentation/appkit/nsworkspace/activespacedidchangenotification).

A separate clean-wheel Playwright 1.64 focus/window recheck passes 122 samples.
Its earlier 114-sample focus failure is preserved in the Poe evidence; no causal
explanation is asserted from later passing checks.

## Other evidence and pending gates

- [Native sessions](340-native-sessions.json): restart persistence, profile locks,
  independent profiles and task tabs, ownership recovery after an owner exits.
- [Optional engines](340-optional-engines.json): explicit installed-wheel fixture
  checks, separate from real provider authorization.
- [CLI lifecycle](340-cli-session.json): real child run/status/cooperative stop.
- [Direct review](340-direct-review.md): fixes and current scope limits.
- Full headless update completed with 497 validated unique bots: 476 scraped
  prices, 20 undisclosed prices and one rendering timeout (`glm-5.3-zai`).
- The user selected a small headless sample and traditional headed fallback on
  failure, followed by commit/push. The sample updated Analyse-PDF and AnimagineXL;
  `glm-5.3-zai` timed out again. The authorized headed incremental fallback
  completed successfully; full forced parity was not requested.

## Final headed fallback result

The normal incremental update completed with 492 validated unique bots, 473
scraped prices, 19 undisclosed rates, zero scraping failures and no missing bot
information. Live catalogue discovery removed eight IDs and added three since
the headless run, including removal of `glm-5.3-zai`. All 470 previously priced
bots still present retain their scraped payload unchanged; all three added bots
have scraped prices. Counts describe different live catalogues and do not prove
full forced headed/headless parity. Both runs used temporary output and preserved
the original dataset. See the paired Poe issues/340-headed-update-summary.json.
