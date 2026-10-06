---
phase: 16
review: 16-REVIEW.md
titles: json
findings:
  - id: WR-01
    severity: warning
    disposition: fixed
    title: "A third `.val()` narrowing survives in `_cell_cutters`; it raises the wrong exception, carries a stale comment, and the docs say there are only two boundaries"
  - id: WR-02
    severity: warning
    disposition: fixed
    title: "The `no-fake-done` pin misses the spellings and files mypy accepts"
  - id: IN-01
    severity: info
    disposition: fixed
    title: "`_body`'s comment overstates what it asserts"
  - id: IN-02
    severity: info
    disposition: fixed
    title: "The mypy comparison behind D-04 covers only the pinned kernel, while `pyproject.toml` declares `cadquery>=2.5`"
  - id: IN-03
    severity: info
    disposition: skipped
    title: "The refusal tests prove the helpers in isolation, not that the call sites reach them"
open: 0
total: 5
recorded: 2026-10-06T00:00:00Z  # triage by hand; the gate's own stamp was 2026-10-05T04:01:07.917Z
---

# Phase 16: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| WR-01 | warning | fixed | 12daf63 fix(model): shared guard in _cell_cutters; dated amendment to L35 (fix/review-findings-v0.3) |
| WR-02 | warning | fixed | build(make): widen the mypy-suppression pin (fix/review-findings-v0.3, after #23 landed) |
| IN-01 | info | fixed | 12daf63 (fix/review-findings-v0.3) |
| IN-02 | info | fixed | 12daf63 (fix/review-findings-v0.3) |
| IN-03 | info | skipped | D-06 stands; reviewer: no change needed; 2026-10-06 triage |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved. A `|` in the reason is kept as prose and escaped on the next run.
Re-running the gate keeps every row it can. A row the current review no longer reports is kept and its Source cell flagged, so a finding does not leave this record silently. ONE exception: when a finding id is REUSED by a different finding, the earlier decision cannot keep a row — the id is taken — and it is dropped. A RECORDED decision (anything but `open`) is named on the console when that happens; a row still at `open` is replaced silently, because `open` records no decision to lose.
