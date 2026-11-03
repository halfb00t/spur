---
status: complete
phase: 34-fit-tables-and-tolerance-window
source: [34-VERIFICATION.md]
started: 2026-10-31T17:34:49Z
updated: 2026-11-01T04:21:58.604Z
---

## Current Test

[testing complete]

## Tests

### 1. Decide the gate-cost reading against L43's 300 s bar (REQ-gate-cost-recorded, success criterion 5)
expected: The human accepts the recorded quiet-host close reading (213.54 s) as the milestone-close reading, or rules on the 308.61 s reading at HEAD 287f0f3, which is above the bar
result: pass
note: "Human accepted 213.54 s (real 214.53) as the milestone-close reading on 2026-11-01. The 308.61 s reading and the post-fix 235.27 s reading are recorded in bench/RESULTS.md (325fd37)."

### 2. Disposition of the four open code-review warnings (WR-01..WR-04) and seven info items
expected: Each is marked fix, defer-to-debt or accept in 34-REVIEW-DISPOSITION.md before the milestone releases as one unit
result: pass
note: "Human ruled fix. WR-01 9215f60, WR-02 d3f339b, WR-03 d299fe3, WR-04 e98638b, stale 721 comment e0708a7; IN-01..IN-07 filed as debt (504d5c5); remaining A_s bound filed (8082ed4). make verify after the fixes: 2940 passed in 235.27s, rc 0."

### 3. Leak review judgement (34-17 close check 15)
expected: The human spot-checks that no added file holds a table value beyond the three approved anchors, including the disclosed fixture coincidence
result: pass
note: "Human ruled change fixture. 282f264 moves the invented default-shaft limit pair off the real value; an in-process comparison against the private file printed coincidences: 0 over 144 fit/class combinations. Earlier commits on this unpushed branch still hold the old pair."

## Summary

total: 3
passed: 3
issues: 0
pending: 0
skipped: 0
blocked: 0

## Gaps
