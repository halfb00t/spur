---
phase: 19
review: 19-REVIEW.md
titles: json
findings:
  - id: CR-01
    severity: critical
    disposition: fixed
    title: "`root_waist` is not the narrowest tooth, and the thin-waist warning goes silent on gears that are thinner than the floor"
  - id: WR-01
    severity: warning
    disposition: fixed
    title: "Unguarded kernel calls in the trochoid outline get the wrong remedy"
  - id: IN-01
    severity: info
    disposition: fixed
    title: "`_build`'s \"one answer\" comment is only partly true"
  - id: IN-02
    severity: info
    disposition: fixed
    title: "Stale docstring and duplicated code in `bench/trochoid_part.py`"
  - id: IN-03
    severity: info
    disposition: fixed
    title: "Gate-cost comments are now stale"
  - id: IN-04
    severity: info
    disposition: fixed
    title: "Minor label and robustness nits"
open: 0
total: 6
recorded: 2026-10-21T00:00:00Z  # triage by hand; the gate's own stamp was 2026-10-09T09:04:21.879Z
---

# Phase 19: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| CR-01 | critical | fixed | 19-REVIEW-FIX.md |
| WR-01 | warning | fixed | 19-REVIEW-FIX.md |
| IN-01 | info | fixed | f7d0366 refactor(model): pass the build's one root answer to the tip chamfer (Phase 27 branch, squashed into 1434a47) |
| IN-02 | info | fixed | 9c62fac fix(bench): read root_mode's curve and name an unknown HEAD in the trochoid bench (the bench half, `trochoid_curve` reads `rm.curve` and the stale paragraph is replaced; Phase 27 branch, squashed into 1434a47). The bench's near-copies (`root_edges`, `tooth0_root_edges`, `oracle_reading`) are kept: they differ from the test helpers in error type (the test helper asserts against `ValueError`), in sample count (a fixed 400 against a `samples` parameter) and in signature (27 D-07) |
| IN-03 | info | fixed | 34270c8 docs(25): log L43 -- the gate bar re-set on an idle host amends L34, stale gate figures rewritten, IN-03 closed (Phase 25 branch commit, landed as cbbe730, PR #38) |
| IN-04 | info | fixed | 9c62fac fix(bench): read root_mode's curve and name an unknown HEAD in the trochoid bench (`_host_state` reads `unknown` where git cannot name HEAD; Phase 27 branch, squashed into 1434a47) and 61154d1 fix(28): label the root_fillet row by the root the server built (the `root_fillet` label; gsd/phase-28-refuse-the-bad-link) |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved. A `|` in the reason is kept as prose and escaped on the next run.
Re-running the gate keeps every row it can. A row the current review no longer reports is kept and its Source cell flagged, so a finding does not leave this record silently. ONE exception: when a finding id is REUSED by a different finding, the earlier decision cannot keep a row — the id is taken — and it is dropped. A RECORDED decision (anything but `open`) is named on the console when that happens; a row still at `open` is replaced silently, because `open` records no decision to lose.
