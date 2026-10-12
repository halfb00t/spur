---
phase: 24
review: 24-REVIEW.md
titles: json
findings:
  - id: WR-01
    severity: warning
    disposition: open
    title: "A pending pick steals focus on every arrow-key step, so a keyboard user cannot walk the select, and the next arrow press edits a number nobody chose (confirms the unverified UI-review concern, with a platform caveat)"
  - id: IN-01
    severity: info
    disposition: open
    title: "The stash can restore a number older than what the user last typed, and the comment calls it \"the user's own string\" while it also holds page defaults"
  - id: IN-02
    severity: info
    disposition: open
    title: "A selector that names a group no field has fails with a message about the schema fetch and leaves a built but empty form"
  - id: IN-03
    severity: info
    disposition: open
    title: "The OpenAPI pin is a substring test on the whole document"
  - id: IN-04
    severity: info
    disposition: open
    title: "Every selector-made Hex part prints a warning in snake_case field names the form does not show (already filed)"
open: 5
total: 5
recorded: 2026-10-12T16:43:17.717Z
---

# Phase 24: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| WR-01 | warning | open | - |
| IN-01 | info | open | - |
| IN-02 | info | open | - |
| IN-03 | info | open | - |
| IN-04 | info | open | - |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved. A `|` in the reason is kept as prose and escaped on the next run.
Re-running the gate keeps every row it can. A row the current review no longer reports is kept and its Source cell flagged, so a finding does not leave this record silently. ONE exception: when a finding id is REUSED by a different finding, the earlier decision cannot keep a row — the id is taken — and it is dropped. A RECORDED decision (anything but `open`) is named on the console when that happens; a row still at `open` is replaced silently, because `open` records no decision to lose.
