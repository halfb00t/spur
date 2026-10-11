---
phase: 23
review: 23-REVIEW.md
titles: json
findings:
  - id: WR-01
    severity: warning
    disposition: fixed
    title: "An unknown `enabled_when` op freezes the UI silently and leaves a stale part, dimensions and download links on screen"
  - id: WR-02
    severity: warning
    disposition: fixed
    title: "The \"never disables, hides or clears a field\" guard is narrower than the contract it claims, and has a false-positive hole"
  - id: WR-03
    severity: warning
    disposition: open
    title: "The calc parity proof cannot tell a right driver from a wrong one for the seven cutout dependents (external: codex)"
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
  - id: IN-06
    severity: info
    disposition: open
    title: "The browser oracle resolves a repeated parameter last-wins where the page resolves it first-wins (external: codex)"
  - id: IN-07
    severity: info
    disposition: open
    title: "The refused-pair step does not require both keyway fields to be marked invalid (external: codex)"
open: 8
total: 10
recorded: 2026-10-11T16:15:40.927Z
---

# Phase 23: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| WR-01 | warning | fixed | 23-REVIEW-FIX.md |
| WR-02 | warning | fixed | 23-REVIEW-FIX.md |
| WR-03 | warning | open | - |
| IN-01 | info | open | - |
| IN-02 | info | open | - |
| IN-03 | info | open | - |
| IN-04 | info | open | - |
| IN-05 | info | open | - |
| IN-06 | info | open | - |
| IN-07 | info | open | - |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved. A `|` in the reason is kept as prose and escaped on the next run.
Re-running the gate keeps every row it can. A row the current review no longer reports is kept and its Source cell flagged, so a finding does not leave this record silently. ONE exception: when a finding id is REUSED by a different finding, the earlier decision cannot keep a row — the id is taken — and it is dropped. A RECORDED decision (anything but `open`) is named on the console when that happens; a row still at `open` is replaced silently, because `open` records no decision to lose.
