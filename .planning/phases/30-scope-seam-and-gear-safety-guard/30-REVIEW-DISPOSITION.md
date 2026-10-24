---
phase: 30
review: 30-REVIEW.md
titles: json
findings:
  - id: WR-01
    severity: warning
    disposition: deferred
    title: "`gear.unchanged` runs git and a probe with no timeout and no prompt guard, in a hook that has hung before"
  - id: WR-02
    severity: warning
    disposition: open
    title: "`test_the_check_leaves_the_repository_as_it_found_it` can flake on racy index entries"
  - id: WR-03
    severity: warning
    disposition: deferred
    title: "`parts.py` promises a \"one-line edit\" widening; the gear-typed internals behind the seam make it false"
  - id: IN-01
    severity: info
    disposition: open
    title: "`_serve_model` docstring says \"Moved byte for byte\"; it was not"
  - id: IN-02
    severity: info
    disposition: deferred
    title: "`gear.unchanged` accepts any local `v0.6` tag, including a lightweight one made by mistake"
  - id: IN-03
    severity: info
    disposition: open
    title: "The docstring promises \"every failure is a SystemExit\"; four paths raise a traceback"
  - id: IN-04
    severity: info
    disposition: open
    title: "Both `shaft_model` belts are blind to a string import, the way `pool` already reaches the kernel"
open: 4
total: 7
recorded: 2026-10-23T17:00:12.340Z
---

# Phase 30: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| WR-01 | warning | deferred | filed as docs/tech_debt/active/2026-10-23-gear-unchanged-has-no-timeout-on-git-or-probe.md |
| WR-02 | warning | open | - |
| WR-03 | warning | deferred | filed as docs/tech_debt/active/2026-10-23-parts-one-line-widening-claim-is-false.md |
| IN-01 | info | open | - |
| IN-02 | info | deferred | filed as docs/tech_debt/active/2026-10-23-gear-unchanged-accepts-a-lightweight-or-moved-v0-6-tag.md |
| IN-03 | info | open | - |
| IN-04 | info | open | - |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved. A `|` in the reason is kept as prose and escaped on the next run.
Re-running the gate keeps every row it can. A row the current review no longer reports is kept and its Source cell flagged, so a finding does not leave this record silently. ONE exception: when a finding id is REUSED by a different finding, the earlier decision cannot keep a row — the id is taken — and it is dropped. A RECORDED decision (anything but `open`) is named on the console when that happens; a row still at `open` is replaced silently, because `open` records no decision to lose.
