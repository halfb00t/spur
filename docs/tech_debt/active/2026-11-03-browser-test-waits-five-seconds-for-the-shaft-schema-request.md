# The browser test waits five seconds for the shaft schema request and failed once on a slow CI runner

Severity: must
Status: active
Date: 2026-11-03
Source: CI on `main` after PR #56 (run 41649073887), found while validating Phase 30
Related files:
- tests/test_browser.py:2848
- tests/test_browser.py:2801
- tests/test_browser.py:2886
- tests/browser_session.py:53

## Context
Three steps of `test_the_shipped_viewer_in_a_real_browser` set `location.hash` to a shaft link
and then wait for the held `/api/shaft/schema` request with `for _ in range(100):
...wait_for_timeout(50)`, about 5 s, and assert `"the shaft's schema was never asked for"` if it
has not arrived. Every other wait in the file uses `BUILD_WAIT_MS` (45 s).

The `main` run for PR #56 failed there, at the step "old form edited while a link's form
loads": `1 failed, 2963 passed in 1129.14s`. That run took 20.5 min; the same tree passed CI on
the phase branch (15.5 min) and on the v0.7 close branch. Re-running only the failed job on the
same commit passed. So this is a timing flake on a slow runner, not a regression. The slow
runner as the cause is a reading of the durations, not a reproduced one.

## Why it matters
A red `main` for a reason that is not a defect teaches people to re-run, and hides the next real
failure in the same test. The gate is also the pre-push hook, so a local flake blocks a push.

## Next step
Replace the three 5 s loops with a wait bounded by `BUILD_WAIT_MS` (Playwright's
`page.wait_for_request` or a polling loop on that bound), seen red by delaying the request past
5 s. Revisit the first time this assertion fails again, or when `tests/test_browser.py` is next
edited.

<!-- On resolve: set Status: resolved, add `Resolved in: <commit sha>`,
     git mv into resolved/, move the INDEX row to Resolved — same commit as the fix. -->
