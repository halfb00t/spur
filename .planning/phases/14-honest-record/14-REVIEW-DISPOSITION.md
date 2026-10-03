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
    title: "skip-the-cutout tripwire: holes and cells literals (6 dp) fail abs=1e-9 on a correct build, so pytest.raises cannot tell the patched build from the unpatched one; L33's claim that all three rows exercise the bar is vacuous for them (corroborated by codex)"
  - id: WR-03
    severity: warning
    disposition: open
    title: "'no closed form exists after an arbitrary boolean' is false for 4 of the 15 composed rows (web formula matches them to 6 dp); claim appears in the debt file, L33 (twice) and three test docstrings (external: codex)"
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
open: 6
total: 6
recorded: 2026-10-03T10:40:00.000Z
---

# Phase 14: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| WR-01 | warning | open | 14-REVIEW.md |
| WR-02 | warning | open | 14-REVIEW.md (corroborated by codex lane) |
| WR-03 | warning | open | 14-REVIEW.md (external: codex lane, verified by gsd-code-reviewer) |
| IN-01 | info | open | 14-REVIEW.md |
| IN-02 | info | open | 14-REVIEW.md |
| IN-03 | info | open | 14-REVIEW.md |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
