---
phase: 18
review: 18-REVIEW.md
titles: json
findings:
  - id: IN-01
    severity: info
    disposition: open
    title: "The cap sentence says \"the largest\", but prints a value floored to 3 dp, and prints `0.000` for a cap under 1 micrometre"
  - id: IN-02
    severity: info
    disposition: open
    title: "Two public entry points give different answers for the same gear, and `root_mode` discards the curve it computed"
  - id: IN-03
    severity: info
    disposition: open
    title: "The epsilon bench cannot fail on the shipped constant"
  - id: IN-04
    severity: info
    disposition: open
    title: "Small bench hygiene items"
  - id: IN-05
    severity: info
    disposition: open
    title: "The `ROOT_CURVE_POINTS` evidence is not reproducible in the repo and omits the research's own counter-measurement"
  - id: IN-06
    severity: info
    disposition: open
    title: "The flake debt's trigger was rolled forward on evidence that cannot discriminate"
  - id: IN-07
    severity: info
    disposition: open
    title: "The new `ValueError` is documented on `cutter()` only; `root_mode()` can now raise and does not say so, and `+inf` went from an honest cap to a refusal"
  - id: IN-08
    severity: info
    disposition: open
    title: "The `-0.0` row cannot tell `-0.0` from `0.0`, and the sign is carried into `Cutter`"
  - id: WR-01
    severity: warning
    disposition: fixed
    title: "One of the four `curve invalid` guard arms is untested, and the test claims all of them"
  - id: WR-02
    severity: warning
    disposition: fixed
    title: "`cutter()` and `root_mode()` take an unvalidated tip radius; NaN is silently capped, negative gets the wrong reason"
open: 8
total: 10
recorded: 2026-10-08T05:22:23.839Z
---

# Phase 18: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| IN-01 | info | open | - |
| IN-02 | info | open | - |
| IN-03 | info | open | - |
| IN-04 | info | open | - |
| IN-05 | info | open | - |
| IN-06 | info | open | - |
| IN-07 | info | open | - |
| IN-08 | info | open | - |
| WR-01 | warning | fixed | 8e96c2d (18-06) (not in the current review) |
| WR-02 | warning | fixed | 085aee7 (18-06) (not in the current review) |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved. A `|` in the reason is kept as prose and escaped on the next run.
Re-running the gate keeps every row it can. A row the current review no longer reports is kept and its Source cell flagged, so a finding does not leave this record silently. ONE exception: when a finding id is REUSED by a different finding, the earlier decision cannot keep a row — the id is taken — and it is dropped. A RECORDED decision (anything but `open`) is named on the console when that happens; a row still at `open` is replaced silently, because `open` records no decision to lose.
