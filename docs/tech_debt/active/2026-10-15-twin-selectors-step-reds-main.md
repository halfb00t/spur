# The browser step "twin selectors" reds `main` CI with one extra request

Severity: must
Status: active
Date: 2026-10-15
Source: v0.6 kickoff research (ARCHITECTURE.md, STACK.md); the two runs read by the orchestrator with `gh run view --log-failed`
Related files:
- tests/test_browser.py:1576 (`requests_before = len(seen)`, the baseline)
- tests/test_browser.py:1611 (the failing assert)
- `.planning/milestones/v0.5-phases/24-bore-shape-selector/` review finding CX-05 (same step)

## Context
`test_the_shipped_viewer_in_a_real_browser` failed on `main` twice, both at step
"twin selectors" with `AssertionError: twin selectors: 1 request(s) sent by two pending picks`:
run 38347283201 at `94dfc19` (Phase 24 squash, `assert 269 == 268`) and run 38680454993 at
`26ddd74` (the v0.5 close squash, carrying the `v0.5` tag, `assert 266 == 265`). The PR runs of
the same trees were green. Two of the last eight `main` runs are red on this step; no other
step failed in either run.

ASSUMPTION (ARCHITECTURE.md, from the two logs, no local reproduction): the baseline at
line 1576 is taken right after `goto()`, before the page's own STL request for the link has
arrived, so that request lands inside the window the assert counts. CI is ~2x slower than the
dev host, which would widen the gap.

## Why it matters
`main` CI is the record the `v0.5` tag points at, and it reads red on a defect in the test,
not the product. Every red that is "just the flake" trains readers to ignore red, which is
how a real regression gets merged.

## Next step
v0.6 REQ-twin-selectors-race-fixed: prove the mechanism with a delayed STL route (old step red),
take the baseline only after the link's own build request has been seen and the 350 ms
debounce has passed, fold in 24 CX-05 and 21 IN-04a, and retire this item in that commit.

<!-- On resolve: set Status: resolved, add `Resolved in: <commit sha>`,
     git mv into resolved/, move the INDEX row to Resolved — same commit as the fix. -->
