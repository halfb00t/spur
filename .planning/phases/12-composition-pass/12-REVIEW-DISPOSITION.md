---
phase: 12
review: 12-REVIEW.md
titles: json
findings:
  - id: WR-01
    severity: warning
    disposition: open
    title: "`cli.md` \"Errors\" claims every parameter error prints `error: <field>: <message>` -- two of the three shapes it groups do not"
  - id: WR-02
    severity: warning
    disposition: open
    title: "`hole_count`'s comment still attributes the 14.87 s row to \"Phase 12 ... (re-measured in the same section)\" after this phase corrected the identical sentence on `spoke_count`"
  - id: WR-03
    severity: warning
    disposition: open
    title: "`bench.export_cost` exits 1 on its only failure path without saying why"
  - id: WR-04
    severity: warning
    disposition: open
    title: "A failing child process reports only \"returned non-zero exit status 1\" -- its `BuildError` text and traceback are captured and discarded"
  - id: WR-05
    severity: warning
    disposition: open
    title: "L31 attributes the \"schema, form source and CLI parser in one order\" proof to the wrong test"
  - id: IN-01
    severity: info
    disposition: open
    title: "`_decisions` docstring says integer arithmetic decides `adopted`; the wall clause is float"
  - id: IN-02
    severity: info
    disposition: open
    title: "`test_bench.py` docstring claims no `conftest.py` exists anywhere in the repo; `tests/conftest.py` does"
  - id: IN-03
    severity: info
    disposition: open
    title: "`cli.md` \"Tests\" still says \"4 tests\" beside a new section that names three others"
  - id: IN-04
    severity: info
    disposition: open
    title: "The shareable-link proof pins eight verbatim `app.js` source lines, so a whitespace-only edit fails a test named as a round-trip proof"
  - id: IN-05
    severity: info
    disposition: open
    title: "`cast(dict[str, float], HOLES)` asserts a type the value does not have"
open: 10
total: 10
recorded: 2026-09-30T14:28:45.212Z
---

# Phase 12: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| WR-01 | warning | open | - |
| WR-02 | warning | open | - |
| WR-03 | warning | open | - |
| WR-04 | warning | open | - |
| WR-05 | warning | open | - |
| IN-01 | info | open | - |
| IN-02 | info | open | - |
| IN-03 | info | open | - |
| IN-04 | info | open | - |
| IN-05 | info | open | - |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved. A `|` in the reason is kept as prose and escaped on the next run.
Re-running the gate keeps every row it can. A row the current review no longer reports is kept and its Source cell flagged, so a finding does not leave this record silently. ONE exception: when a finding id is REUSED by a different finding, the earlier decision cannot keep a row — the id is taken — and it is dropped. A RECORDED decision (anything but `open`) is named on the console when that happens; a row still at `open` is replaced silently, because `open` records no decision to lose.
