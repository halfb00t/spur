---
phase: 26
review: 26-REVIEW.md
titles: json
findings:
  - id: WR-01
    severity: warning
    disposition: fixed
    title: "The hang item names two different `faulthandler_timeout` values"
  - id: WR-02
    severity: warning
    disposition: fixed
    title: "The two twin-selectors records disagree on whether the 20 local runs are proof"
  - id: IN-01
    severity: info
    disposition: open
    title: "The second new hook-pin test adds no discrimination over the first"
  - id: IN-02
    severity: info
    disposition: open
    title: "The image-recipe pin keeps a name that no longer says what it pins"
  - id: IN-03
    severity: info
    disposition: open
    title: "The browser test cites the wrong line range for the info-then-STL fetch"
  - id: IN-04
    severity: info
    disposition: open
    title: "New source comments cite phase-scoped planning paths that move at milestone close"
  - id: IN-05
    severity: info
    disposition: open
    title: "The autouse fixture's cost is an unmeasured figure from another host"
open: 5
total: 7
recorded: 2026-10-16T05:34:05.220Z
---

# Phase 26: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| WR-01 | warning | fixed | 26-REVIEW-FIX.md |
| WR-02 | warning | fixed | 26-REVIEW-FIX.md |
| IN-01 | info | open | - |
| IN-02 | info | open | - |
| IN-03 | info | open | - |
| IN-04 | info | open | - |
| IN-05 | info | open | - |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved. A `|` in the reason is kept as prose and escaped on the next run.
Re-running the gate keeps every row it can. A row the current review no longer reports is kept and its Source cell flagged, so a finding does not leave this record silently. ONE exception: when a finding id is REUSED by a different finding, the earlier decision cannot keep a row — the id is taken — and it is dropped. A RECORDED decision (anything but `open`) is named on the console when that happens; a row still at `open` is replaced silently, because `open` records no decision to lose.
