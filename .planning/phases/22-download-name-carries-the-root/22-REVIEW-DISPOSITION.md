---
phase: 22
review: 22-REVIEW.md
titles: json
findings:
  - id: WR-01
    severity: warning
    disposition: open
    title: "`slug()` totality is unguarded in CI and the function now runs inside failure-record paths"
  - id: WR-02
    severity: warning
    disposition: open
    title: "`test_a_failed_build_records_the_name_of_the_part_it_would_have_been` depends on no other test requesting the same gear"
  - id: IN-01
    severity: info
    disposition: open
    title: "The bore-off field block is duplicated in two test files"
  - id: IN-02
    severity: info
    disposition: open
    title: "Ragged docstring reflow in `serve_stl_from`"
  - id: IN-03
    severity: info
    disposition: open
    title: "L40 quotes the best-case reading of the new step as its cost"
open: 5
total: 5
recorded: 2026-10-11T06:51:09.210Z
---

# Phase 22: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| WR-01 | warning | open | - |
| WR-02 | warning | open | - |
| IN-01 | info | open | - |
| IN-02 | info | open | - |
| IN-03 | info | open | - |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved. A `|` in the reason is kept as prose and escaped on the next run.
Re-running the gate keeps every row it can. A row the current review no longer reports is kept and its Source cell flagged, so a finding does not leave this record silently. ONE exception: when a finding id is REUSED by a different finding, the earlier decision cannot keep a row — the id is taken — and it is dropped. A RECORDED decision (anything but `open`) is named on the console when that happens; a row still at `open` is replaced silently, because `open` records no decision to lose.
