---
phase: 18
review: 18-REVIEW.md
titles: json
findings:
  - id: IN-01
    severity: info
    disposition: fixed
    title: "The cap sentence says \"the largest\", but prints a value floored to 3 dp, and prints `0.000` for a cap under 1 micrometre"
  - id: IN-02
    severity: info
    disposition: skipped
    title: "Two public entry points give different answers for the same gear, and `root_mode` discards the curve it computed"
  - id: IN-03
    severity: info
    disposition: deferred
    title: "The epsilon bench cannot fail on the shipped constant"
  - id: IN-04
    severity: info
    disposition: deferred
    title: "Small bench hygiene items"
  - id: IN-05
    severity: info
    disposition: deferred
    title: "The `ROOT_CURVE_POINTS` evidence is not reproducible in the repo and omits the research's own counter-measurement"
  - id: IN-06
    severity: info
    disposition: skipped
    title: "The flake debt's trigger was rolled forward on evidence that cannot discriminate"
  - id: IN-07
    severity: info
    disposition: fixed
    title: "The new `ValueError` is documented on `cutter()` only; `root_mode()` can now raise and does not say so, and `+inf` went from an honest cap to a refusal"
  - id: IN-08
    severity: info
    disposition: deferred
    title: "The `-0.0` row cannot tell `-0.0` from `0.0`, and the sign is carried into `Cutter`"
  - id: WR-01
    severity: warning
    disposition: fixed
    title: "One of the four `curve invalid` guard arms is untested, and the test claims all of them"
  - id: WR-02
    severity: warning
    disposition: fixed
    title: "`cutter()` and `root_mode()` take an unvalidated tip radius; NaN is silently capped, negative gets the wrong reason"
  - id: XR-01
    severity: warning
    disposition: fixed
    title: "`check_curve` applies the join-band allowance to every undercut crossing, masking junction errors"
  - id: XR-02
    severity: info
    disposition: fixed
    title: "The crossing-direction tripwire samples the cutter's flank foot instead of the solved crossing"
open: 0
total: 12
recorded: 2026-10-21T00:00:00Z  # triage by hand; the gate's own stamp was 2026-10-08T05:22:23.839Z
---

# Phase 18: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| IN-01 | info | fixed | 767317b Phase 19: The Trochoid in the Part (#29) (the cap sentence in calc.py reads "within 0.001 mm of the largest") |
| IN-02 | info | skipped | overtaken: RootMode.curve carries the curve root_mode computes (calc.py), so neither entry point discards it |
| IN-03 | info | deferred | docs/tech_debt/active/2026-10-21-phase-18-review-info-findings-deferred.md (trigger: the next phase that changes the trochoid / hob-root maths in calc.py or its tests, D-12) |
| IN-04 | info | deferred | docs/tech_debt/active/2026-10-21-phase-18-review-info-findings-deferred.md (trigger: the next phase that changes the trochoid / hob-root maths in calc.py or its tests, D-12) |
| IN-05 | info | deferred | docs/tech_debt/active/2026-10-21-phase-18-review-info-findings-deferred.md (trigger: the next phase that changes the trochoid / hob-root maths in calc.py or its tests, D-12) |
| IN-06 | info | skipped | overtaken: the flake item is resolved, docs/tech_debt/resolved/2026-10-06-resource-tracker-flake-fails-the-gate.md |
| IN-07 | info | fixed | 9092802 docs(28): say root_mode raises for a bad tip radius once the trochoid is requested (18 IN-07) (gsd/phase-28-refuse-the-bad-link) |
| IN-08 | info | deferred | docs/tech_debt/active/2026-10-21-phase-18-review-info-findings-deferred.md (trigger: the next phase that changes the trochoid / hob-root maths in calc.py or its tests, D-12) |
| WR-01 | warning | fixed | 8e96c2d (18-06) (not in the current review) |
| WR-02 | warning | fixed | 085aee7 (18-06) (not in the current review) |
| XR-01 | warning | fixed | 398d1e2 (external: codex, cross-CLI review of PR #28) |
| XR-02 | info | fixed | 13df7d5 (external: codex, cross-CLI review of PR #28) |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved. A `|` in the reason is kept as prose and escaped on the next run.
Re-running the gate keeps every row it can. A row the current review no longer reports is kept and its Source cell flagged, so a finding does not leave this record silently. ONE exception: when a finding id is REUSED by a different finding, the earlier decision cannot keep a row — the id is taken — and it is dropped. A RECORDED decision (anything but `open`) is named on the console when that happens; a row still at `open` is replaced silently, because `open` records no decision to lose.
