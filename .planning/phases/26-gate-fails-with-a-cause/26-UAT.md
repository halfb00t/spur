---
status: testing
phase: 26-gate-fails-with-a-cause
source: [26-VERIFICATION.md]
started: 2026-10-15T14:57:07Z
updated: 2026-10-15T14:57:07Z
---

## Current Test

number: 1
name: Twin-selectors step green on the first post-merge `main` CI run
expected: |
  The `test (3.12)` job is green at the twin selectors step on a push-to-main run.
  Red at that step: stop, re-open the twin item, no patch.
awaiting: user response

## Tests

### 1. Twin-selectors step green on the first post-merge `main` CI run
After `make pr.land` lands Phase 26: `gh run list --branch main --workflow ci --limit 1 --json databaseId,headSha,conclusion`, then `gh run view {id} --log --job {test-job-id}` and confirm `tests/test_browser.py::test_the_shipped_viewer_in_a_real_browser` PASSED (no `twin selectors:` failure). Append the dated reading to bench/RESULTS.md on the next phase branch and retire docs/tech_debt/active/2026-10-15-twin-selectors-fix-awaits-the-post-merge-main-read.md.
expected: The `test (3.12)` job is green at the twin selectors step on a push-to-main run. Red at that step: stop, re-open the twin item, no patch.
result: [pending]

## Summary

total: 1
passed: 0
issues: 0
pending: 1
skipped: 0
blocked: 0

## Gaps
