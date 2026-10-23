---
status: complete
phase: 26-gate-fails-with-a-cause
source: [26-VERIFICATION.md]
started: 2026-10-15T14:57:07Z
updated: 2026-10-16T06:05:45.275Z
---

## Current Test

[testing complete]

## Tests

### 1. Twin-selectors step green on the first post-merge `main` CI run
After `make pr.land` lands Phase 26: `gh run list --branch main --workflow ci --limit 1 --json databaseId,headSha,conclusion`, then `gh run view {id} --log --job {test-job-id}` and confirm `tests/test_browser.py::test_the_shipped_viewer_in_a_real_browser` PASSED (no `twin selectors:` failure). Append the dated reading to bench/RESULTS.md on the next phase branch and retire docs/tech_debt/active/2026-10-15-twin-selectors-fix-awaits-the-post-merge-main-read.md.
expected: The `test (3.12)` job is green at the twin selectors step on a push-to-main run. Red at that step: stop, re-open the twin item, no patch.
result: pass
evidence: "main CI run 38858407163 on 1981d93 (PR #41 merge), job test (3.12) 116834933998 success: PASSED tests/test_browser.py::test_the_shipped_viewer_in_a_real_browser; no 'twin selectors' text in log; 1321 passed in 469.99s."

## Summary

total: 1
passed: 1
issues: 0
pending: 0
skipped: 0
blocked: 0

## Gaps
