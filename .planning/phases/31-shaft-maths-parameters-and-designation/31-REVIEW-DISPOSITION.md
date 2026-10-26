---
phase: 31
review: 31-REVIEW.md
titles: json
findings:
  - id: WR-01
    severity: warning
    disposition: fixed
    title: "The refusal message contradicts itself near the range edges"
  - id: WR-02
    severity: warning
    disposition: open
    title: "`measure_over_pins` is printed next to a fit designation but is the nominal-thickness measure, and no warning says so"
  - id: WR-03
    severity: warning
    disposition: open
    title: "The `root_d` warning names only hobbing; the copy names more processes"
  - id: WR-04
    severity: warning
    disposition: fixed
    title: "`DesignationError` cannot be pickled, copied or re-raised across a process boundary"
  - id: WR-05
    severity: warning
    disposition: open
    title: "`parse_designation` accepts leading zeros in the number tokens but refuses them in the fit; its docstring says otherwise"
  - id: IN-01
    severity: info
    disposition: open
    title: "Debt items point at stale line numbers"
  - id: IN-02
    severity: info
    disposition: open
    title: "Stale module docstring in `tests/test_shaft_calc.py`"
  - id: IN-03
    severity: info
    disposition: open
    title: "`THEORETICAL_PIN` makes a claim no seen page supports, and stays when the pin is null"
  - id: IN-04
    severity: info
    disposition: open
    title: "The 0.1*m drop is written twice and `HOBBED_ROOT_DROP` is not tied to `H_FP`"
  - id: IN-05
    severity: info
    disposition: open
    title: "The default shaft sits on the range edge, and `shaft_params` imports the gear's private helpers"
open: 8
total: 10
recorded: 2026-10-26T09:55:31.583Z
---

# Phase 31: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| WR-01 | warning | fixed | 31-REVIEW-FIX.md |
| WR-02 | warning | open | - |
| WR-03 | warning | open | - |
| WR-04 | warning | fixed | 31-REVIEW-FIX.md |
| WR-05 | warning | open | - |
| IN-01 | info | open | - |
| IN-02 | info | open | - |
| IN-03 | info | open | - |
| IN-04 | info | open | - |
| IN-05 | info | open | - |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved. A `|` in the reason is kept as prose and escaped on the next run.
Re-running the gate keeps every row it can. A row the current review no longer reports is kept and its Source cell flagged, so a finding does not leave this record silently. ONE exception: when a finding id is REUSED by a different finding, the earlier decision cannot keep a row — the id is taken — and it is dropped. A RECORDED decision (anything but `open`) is named on the console when that happens; a row still at `open` is replaced silently, because `open` records no decision to lose.
