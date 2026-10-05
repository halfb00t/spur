---
phase: 16
review: 16-REVIEW.md
titles: json
findings:
  - id: WR-01
    severity: warning
    disposition: open
    title: "A third `.val()` narrowing survives in `_cell_cutters`; it raises the wrong exception, carries a stale comment, and the docs say there are only two boundaries"
  - id: WR-02
    severity: warning
    disposition: open
    title: "The `no-fake-done` pin misses the spellings and files mypy accepts"
  - id: IN-01
    severity: info
    disposition: open
    title: "`_body`'s comment overstates what it asserts"
  - id: IN-02
    severity: info
    disposition: open
    title: "The mypy comparison behind D-04 covers only the pinned kernel, while `pyproject.toml` declares `cadquery>=2.5`"
  - id: IN-03
    severity: info
    disposition: open
    title: "The refusal tests prove the helpers in isolation, not that the call sites reach them"
open: 5
total: 5
recorded: 2026-10-05T04:01:07.917Z
---

# Phase 16: Code Review Disposition

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
