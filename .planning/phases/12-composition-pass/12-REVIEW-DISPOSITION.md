---
phase: 12
review: 12-REVIEW.md
titles: json
findings:
  - id: WR-01
    severity: warning
    disposition: fixed
    title: "`cli.md` \"Errors\" claims every parameter error prints `error: <field>: <message>` -- two of the three shapes it groups do not"
  - id: WR-02
    severity: warning
    disposition: fixed
    title: "`hole_count`'s comment still attributes the 14.87 s row to \"Phase 12 ... (re-measured in the same section)\" after this phase corrected the identical sentence on `spoke_count`"
  - id: WR-03
    severity: warning
    disposition: fixed
    title: "`bench.export_cost` exits 1 on its only failure path without saying why"
  - id: WR-04
    severity: warning
    disposition: fixed
    title: "A failing child process reports only \"returned non-zero exit status 1\" -- its `BuildError` text and traceback are captured and discarded"
  - id: WR-05
    severity: warning
    disposition: fixed
    title: "L31 attributes the \"schema, form source and CLI parser in one order\" proof to the wrong test"
  - id: WR-06
    severity: warning
    disposition: fixed
    title: "the \"level 9 compared against the currently-adopted level\" regression test can't actually distinguish that from the bug it names"
  - id: WR-07
    severity: warning
    disposition: fixed
    title: "decision-log and RESULTS.md prose calls two end-of-run load readings \"at-start loads\""
  - id: WR-08
    severity: warning
    disposition: fixed
    title: "L31 says every composed pattern measured below its arithmetic total; the honeycomb row it cites in the same sentence measured above it"
  - id: WR-09
    severity: warning
    disposition: fixed
    title: "\"L24's invariant held\" / \"identical mesh content\" overstates what the triangle-count comparison actually checks"
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
open: 5
total: 14
recorded: 2026-10-01T02:19:17.851Z
---

# Phase 12: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| WR-01 | warning | fixed | 12-REVIEW-FIX.md |
| WR-02 | warning | fixed | 12-REVIEW-FIX.md |
| WR-03 | warning | fixed | 12-REVIEW-FIX.md |
| WR-04 | warning | fixed | 12-REVIEW-FIX.md |
| WR-05 | warning | fixed | 12-REVIEW-FIX.md |
| WR-06 | warning | fixed | 12-REVIEW-FIX.md |
| WR-07 | warning | fixed | 12-REVIEW-FIX.md |
| WR-08 | warning | fixed | 12-REVIEW-FIX.md |
| WR-09 | warning | fixed | 12-REVIEW-FIX.md |
| IN-01 | info | open | - |
| IN-02 | info | open | - |
| IN-03 | info | open | - |
| IN-04 | info | open | - |
| IN-05 | info | open | - |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved. A `|` in the reason is kept as prose and escaped on the next run.
Re-running the gate keeps every row it can. A row the current review no longer reports is kept and its Source cell flagged, so a finding does not leave this record silently. ONE exception: when a finding id is REUSED by a different finding, the earlier decision cannot keep a row — the id is taken — and it is dropped. A RECORDED decision (anything but `open`) is named on the console when that happens; a row still at `open` is replaced silently, because `open` records no decision to lose.
