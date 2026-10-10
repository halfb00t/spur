---
phase: 21
review: 21-REVIEW.md
titles: json
findings:
  - id: WR-01
    severity: warning
    disposition: open
    title: "`stop_group` can leak the whole server group if `ps` fails"
  - id: WR-02
    severity: warning
    disposition: open
    title: "`MIN_GROUP_MEMBERS` is documented as \"uvicorn plus 2 workers\"; the 3 members are uvicorn, the resource tracker and ONE worker"
  - id: WR-03
    severity: warning
    disposition: open
    title: "A missing-shell failure tells the reader `make test` will fix it, but a current `$(BROWSER)` stamp makes `make test` do nothing"
  - id: IN-01
    severity: info
    disposition: open
    title: "Dead assignment and misleading bound in the survivor failure message"
  - id: IN-02
    severity: info
    disposition: open
    title: "`fixture_hash` accepts non-string scalars it would encode wrongly"
  - id: IN-03
    severity: info
    disposition: open
    title: "The \"no path that passes without the browser\" scan is line-based and spelling-based"
  - id: IN-04
    severity: info
    disposition: open
    title: "Inconsistent waits and a hot loop in `test_browser.py`"
open: 7
total: 7
recorded: 2026-10-10T15:02:32.792Z
---

# Phase 21: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| WR-01 | warning | open | - |
| WR-02 | warning | open | - |
| WR-03 | warning | open | - |
| IN-01 | info | open | - |
| IN-02 | info | open | - |
| IN-03 | info | open | - |
| IN-04 | info | open | - |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved. A `|` in the reason is kept as prose and escaped on the next run.
Re-running the gate keeps every row it can. A row the current review no longer reports is kept and its Source cell flagged, so a finding does not leave this record silently. ONE exception: when a finding id is REUSED by a different finding, the earlier decision cannot keep a row — the id is taken — and it is dropped. A RECORDED decision (anything but `open`) is named on the console when that happens; a row still at `open` is replaced silently, because `open` records no decision to lose.
