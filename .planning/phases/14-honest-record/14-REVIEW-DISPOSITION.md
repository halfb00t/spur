---
phase: 14
review: 14-REVIEW.md
titles: json
findings:
  - id: WR-01
    severity: warning
    disposition: open
    title: "abs=1e-9 volume bars calibrated only on macOS arm64; CI runs ubuntu-latest"
  - id: WR-02
    severity: warning
    disposition: open
    title: "skip-the-cutout tripwire: holes and cells rows pass 6 dp literals at abs=1e-9, so L33's claim that all three rows exercise the bar is vacuous for them"
  - id: IN-01
    severity: info
    disposition: open
    title: "resolved root-lead-in debt file still carries the template's On-resolve comment"
  - id: IN-02
    severity: info
    disposition: open
    title: "closed-form spoke oracle checked at one configuration; tripwire's perturbed() is a hand copy of _fillet_corner"
  - id: IN-03
    severity: info
    disposition: open
    title: "lead-in warning omits the x > 0.125 clause README states (correct as a cause statement)"
open: 5
total: 5
recorded: 2026-10-03T00:00:00.000Z
---

# Phase 14: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| WR-01 | warning | open | 14-REVIEW.md |
| WR-02 | warning | open | 14-REVIEW.md |
| IN-01 | info | open | 14-REVIEW.md |
| IN-02 | info | open | 14-REVIEW.md |
| IN-03 | info | open | 14-REVIEW.md |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
