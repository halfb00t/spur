---
phase: 11
review: 11-REVIEW.md
titles: json
findings:
  - id: WR-01
    severity: warning
    disposition: open
    title: "Honeycomb spike can hide a failed trial and report `Verdict: held` regardless (external: codex)"
  - id: WR-02
    severity: warning
    disposition: open
    title: "L30 decision-log entry inverts its own test's conclusion (external: codex)"
  - id: WR-03
    severity: warning
    disposition: open
    title: "`implementation.md` documents `cell_count_floor` with a `cap` argument it does not take (external: codex)"
  - id: WR-04
    severity: warning
    disposition: open
    title: "README claims the \"reverse half-set\" cutout case is rejected; it is accepted and warned instead"
  - id: WR-05
    severity: warning
    disposition: open
    title: "The filleted-spoke removed-volume proof has no closed-form cross-check (external: codex, extended)"
  - id: IN-01
    severity: info
    disposition: open
    title: "`bench/RESULTS.md` and `test_bench.py` misstate the honeycomb field's default and legal range (external: codex)"
open: 6
total: 6
recorded: 2026-09-29T11:28:55.117Z
---

# Phase 11: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| WR-01 | warning | open | - |
| WR-02 | warning | open | - |
| WR-03 | warning | open | - |
| WR-04 | warning | open | - |
| WR-05 | warning | open | - |
| IN-01 | info | open | - |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved. A `|` in the reason is kept as prose and escaped on the next run.
Re-running the gate keeps every row it can. A row the current review no longer reports is kept and its Source cell flagged, so a finding does not leave this record silently. ONE exception: when a finding id is REUSED by a different finding, the earlier decision cannot keep a row — the id is taken — and it is dropped. A RECORDED decision (anything but `open`) is named on the console when that happens; a row still at `open` is replaced silently, because `open` records no decision to lose.
