---
phase: 26
review: 26-REVIEW.md
titles: json
findings:
  - id: WR-01
    severity: warning
    disposition: fixed
    title: "The hang item names two different `faulthandler_timeout` values"
  - id: WR-02
    severity: warning
    disposition: fixed
    title: "The two twin-selectors records disagree on whether the 20 local runs are proof"
  - id: IN-01
    severity: info
    disposition: skipped
    title: "The second new hook-pin test adds no discrimination over the first"
  - id: IN-02
    severity: info
    disposition: skipped
    title: "The image-recipe pin keeps a name that no longer says what it pins"
  - id: IN-03
    severity: info
    disposition: fixed
    title: "The browser test cites the wrong line range for the info-then-STL fetch"
  - id: IN-04
    severity: info
    disposition: fixed
    title: "New source comments cite phase-scoped planning paths that move at milestone close"
  - id: IN-05
    severity: info
    disposition: skipped
    title: "The autouse fixture's cost is an unmeasured figure from another host"
open: 0
total: 7
recorded: 2026-10-21T00:00:00Z  # triage by hand; the gate's own stamp was 2026-10-16T05:34:05.220Z
---

# Phase 26: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| WR-01 | warning | fixed | 26-REVIEW-FIX.md |
| WR-02 | warning | fixed | 26-REVIEW-FIX.md |
| IN-01 | info | skipped | kept as documentation, not cited as independent coverage; tests/test_hooks.py not edited in Phase 28 |
| IN-02 | info | skipped | a rename only, of a file Phase 28 does not edit |
| IN-03 | info | fixed | cb93d4e fix(28): send a link value its control cannot hold, so the 422 refuses it -- log L44 (the `app.js` line citations in `tests/test_browser.py` became function names; gsd/phase-28-refuse-the-bad-link) |
| IN-04 | info | fixed | 54f3b53 docs(28): cite the bench record, not a phase planning path, for the image ignores and the hang runbook (26 IN-04) (gsd/phase-28-refuse-the-bad-link) |
| IN-05 | info | skipped | already flagged as not measured in the docstring; tests/test_pool.py not edited in Phase 28 |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved. A `|` in the reason is kept as prose and escaped on the next run.
Re-running the gate keeps every row it can. A row the current review no longer reports is kept and its Source cell flagged, so a finding does not leave this record silently. ONE exception: when a finding id is REUSED by a different finding, the earlier decision cannot keep a row — the id is taken — and it is dropped. A RECORDED decision (anything but `open`) is named on the console when that happens; a row still at `open` is replaced silently, because `open` records no decision to lose.
