---
phase: 23
review: 23-REVIEW.md
titles: json
findings:
  - id: WR-01
    severity: warning
    disposition: open
    title: "An unknown `enabled_when` op freezes the UI silently and leaves a stale part, dimensions and download links on screen"
  - id: WR-02
    severity: warning
    disposition: open
    title: "The \"never disables, hides or clears a field\" guard is narrower than the contract it claims, and has a false-positive hole"
  - id: IN-01
    severity: info
    disposition: open
    title: "The reason text is formatted differently in the two \"independent\" evaluators for non-trivial values"
  - id: IN-02
    severity: info
    disposition: open
    title: "A dimmed field's accessible name now contains its own reason, which `aria-describedby` repeats"
  - id: IN-03
    severity: info
    disposition: open
    title: "A stale line reference in the new tech-debt item"
  - id: IN-04
    severity: info
    disposition: open
    title: "A verdict that \"08 D-09 stands\" remains in the ideas index after L41 superseded it"
  - id: IN-05
    severity: info
    disposition: open
    title: "The L41 text is in two tenses about what the commit declares"
open: 7
total: 7
recorded: 2026-10-11T13:48:06.303Z
---

# Phase 23: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| WR-01 | warning | open | - |
| WR-02 | warning | open | - |
| IN-01 | info | open | - |
| IN-02 | info | open | - |
| IN-03 | info | open | - |
| IN-04 | info | open | - |
| IN-05 | info | open | - |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved. A `|` in the reason is kept as prose and escaped on the next run.
Re-running the gate keeps every row it can. A row the current review no longer reports is kept and its Source cell flagged, so a finding does not leave this record silently. ONE exception: when a finding id is REUSED by a different finding, the earlier decision cannot keep a row — the id is taken — and it is dropped. A RECORDED decision (anything but `open`) is named on the console when that happens; a row still at `open` is replaced silently, because `open` records no decision to lose.
