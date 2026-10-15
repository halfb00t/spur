# `_wait_until_parked` spins `page.evaluate("0")` with no pause until a route parks

Severity: nice
Status: active
Date: 2026-10-15
Source: 21-REVIEW IN-04 (its second half); unassigned in v0.6, Phase 26 folds only IN-04a (`_follow_link`'s unbounded wait)
Related files:
- `tests/test_browser.py` (`_wait_until_parked`)

## Context
`_wait_until_parked(page, parked)` loops `page.evaluate("0")` until a route handler has appended to `parked`, with no pause
between turns. The round trip is what lets a route handler run under the sync API (a sleep loop would never see it fire),
so the loop is correct, but each turn is a back-to-back round trip to the browser, a hot loop for up to `BUILD_WAIT_MS`
(45 s) when the page's request is slow to arrive.

## Why it matters
CPU spin on a loaded runner, the kind of load the gate's timing tests are sensitive to. It is a cost, not a wrong answer:
the helper's bound and its signal (the request itself, not elapsed time) are right.

## Next step
A short `page.wait_for_timeout(...)` per turn (a Playwright call, so route handlers still run). Revisit when
`_wait_until_parked` is next touched, or at Phase 28's info-finding triage.

<!-- On resolve: set Status: resolved, add `Resolved in: <commit sha>`,
     git mv into resolved/, move the INDEX row to Resolved — same commit as the fix. -->
