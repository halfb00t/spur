# The browser test's 5 s wait for the shaft schema flakes under host load

Severity: must
Status: active
Date: 2026-10-30
Source: Phase 34 execution, post-wave-2 gate (`make verify` after 34-02)
Related files:
- tests/test_browser.py:2844

## Context
The step "old form edited while a link's form loads" sets a `part=shaft` hash and then
polls for the shaft schema request: `for _ in range(100): ... wait_for_timeout(50)`. That
is a fixed 5 s budget, measured in wall time on the host.

The post-wave-2 `make verify` failed only this test: `1 failed, 2835 passed in 544.20s`,
with `AssertionError: the shaft's schema was never asked for`. The host load average was
54–61 because another project's jobs were sharing the machine, and the suite took 9:04
against a 3:50 baseline (34-01). The same test, rerun alone on the same tree under the
same load (`PLAYWRIGHT_BROWSERS_PATH=.venv/ms-playwright`, `-n0`), passed in 77.13 s.
34-02 changed nothing on the viewer or schema path.

## Why it matters
A red gate that is not a regression teaches people to rerun until green, which hides a
real red later. The gate is the project's definition of done.

## Next step
Replace the fixed poll with a wait on the request itself (e.g. `page.expect_request` on
`/api/shaft/schema` with a generous timeout), so the step waits for the event rather
than a wall-clock budget. Revisit when this test next goes red under load, or when the
browser test is next edited.

<!-- On resolve: set Status: resolved, add `Resolved in: <commit sha>`,
     git mv into resolved/, move the INDEX row to Resolved — same commit as the fix. -->
