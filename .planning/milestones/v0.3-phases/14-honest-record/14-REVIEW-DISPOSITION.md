---
phase: 14
review: 14-REVIEW.md
titles: json
findings:
  - id: WR-01
    severity: warning
    disposition: open
    title: "`volume_rel` silently shadows `volume_abs` when both are passed"
  - id: IN-01
    severity: info
    disposition: open
    title: "Test docstrings cite `14-REVIEW WR-02` / `WR-03`, a file this review replaces"
  - id: IN-02
    severity: info
    disposition: open
    title: "L33 attributes the tip-row bar to D-06, whose stated trigger was not met"
  - id: WR-02
    severity: warning
    disposition: fixed
    title: "skip-the-cutout tripwire: holes and cells literals (6 dp) fail abs=1e-9 on a correct build, so pytest.raises cannot tell the patched build from the unpatched one; L33's claim that all three rows exercise the bar is vacuous for them (corroborated by codex)"
  - id: WR-03
    severity: warning
    disposition: fixed
    title: "'no closed form exists after an arbitrary boolean' is false for 4 of the 15 composed rows (web formula matches them to 6 dp); claim appears in the debt file, L33 (twice) and three test docstrings (external: codex)"
  - id: IN-03
    severity: info
    disposition: open
    title: "lead-in warning omits the x > 0.125 clause README states (correct as a cause statement)"
open: 4
total: 6
recorded: 2026-10-03T08:06:02.670Z
---

# Phase 14: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| WR-01 | warning | open | - |
| IN-01 | info | open | - |
| IN-02 | info | open | - |
| WR-02 | warning | fixed | 14-REVIEW.md (corroborated by codex lane) (not in the current review) |
| WR-03 | warning | fixed | 14-REVIEW.md (external: codex lane, verified by gsd-code-reviewer) (not in the current review) |
| IN-03 | info | open | 14-REVIEW.md (not in the current review) |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved. A `|` in the reason is kept as prose and escaped on the next run.
Re-running the gate keeps every row it can. A row the current review no longer reports is kept and its Source cell flagged, so a finding does not leave this record silently. ONE exception: when a finding id is REUSED by a different finding, the earlier decision cannot keep a row — the id is taken — and it is dropped. A RECORDED decision (anything but `open`) is named on the console when that happens; a row still at `open` is replaced silently, because `open` records no decision to lose.
