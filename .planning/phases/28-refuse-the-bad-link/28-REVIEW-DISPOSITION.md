---
phase: 28
review: 28-REVIEW.md
titles: json
findings:
  - id: WR-01
    severity: warning
    disposition: open
    title: "A selector pick that writes a rejected field leaves the page sending the old token"
  - id: WR-02
    severity: warning
    disposition: open
    title: "A token the box blanks but the API accepts builds a non-default part under a blank box"
  - id: WR-03
    severity: warning
    disposition: open
    title: "A printed value the project's own rule forbids is filed `must` with no trigger other than a decision"
  - id: IN-01
    severity: info
    disposition: open
    title: "`readHash()` assigns the mate box twice only to keep an old test pin adjacent"
  - id: IN-02
    severity: info
    disposition: open
    title: "`web-ui.md` has a 190-character line inserted mid-paragraph"
open: 5
total: 5
recorded: 2026-10-21T13:18:24.966Z
---

# Phase 28: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| WR-01 | warning | open | - |
| WR-02 | warning | open | - |
| WR-03 | warning | open | - |
| IN-01 | info | open | - |
| IN-02 | info | open | - |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved. A `|` in the reason is kept as prose and escaped on the next run.
Re-running the gate keeps every row it can. A row the current review no longer reports is kept and its Source cell flagged, so a finding does not leave this record silently. ONE exception: when a finding id is REUSED by a different finding, the earlier decision cannot keep a row — the id is taken — and it is dropped. A RECORDED decision (anything but `open`) is named on the console when that happens; a row still at `open` is replaced silently, because `open` records no decision to lose.
