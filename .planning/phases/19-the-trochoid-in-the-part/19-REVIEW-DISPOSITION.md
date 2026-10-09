---
phase: 19
review: 19-REVIEW.md
titles: json
findings:
  - id: CR-01
    severity: critical
    disposition: fixed
    title: "`root_waist` is not the narrowest tooth, and the thin-waist warning goes silent on gears that are thinner than the floor"
  - id: WR-01
    severity: warning
    disposition: fixed
    title: "Unguarded kernel calls in the trochoid outline get the wrong remedy"
  - id: IN-01
    severity: info
    disposition: skipped
    title: "`_build`'s \"one answer\" comment is only partly true"
  - id: IN-02
    severity: info
    disposition: skipped
    title: "Stale docstring and duplicated code in `bench/trochoid_part.py`"
  - id: IN-03
    severity: info
    disposition: skipped
    title: "Gate-cost comments are now stale"
  - id: IN-04
    severity: info
    disposition: skipped
    title: "Minor label and robustness nits"
open: 0
total: 6
recorded: 2026-10-09T09:04:21.879Z
---

# Phase 19: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| CR-01 | critical | fixed | 19-REVIEW-FIX.md |
| WR-01 | warning | fixed | 19-REVIEW-FIX.md |
| IN-01 | info | skipped | 19-REVIEW-FIX.md |
| IN-02 | info | skipped | 19-REVIEW-FIX.md |
| IN-03 | info | skipped | 19-REVIEW-FIX.md |
| IN-04 | info | skipped | 19-REVIEW-FIX.md |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved. A `|` in the reason is kept as prose and escaped on the next run.
Re-running the gate keeps every row it can. A row the current review no longer reports is kept and its Source cell flagged, so a finding does not leave this record silently. ONE exception: when a finding id is REUSED by a different finding, the earlier decision cannot keep a row — the id is taken — and it is dropped. A RECORDED decision (anything but `open`) is named on the console when that happens; a row still at `open` is replaced silently, because `open` records no decision to lose.
