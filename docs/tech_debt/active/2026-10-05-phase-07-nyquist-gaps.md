# Phase 7's Nyquist audit lists 3 tasks with no named automated command

Severity: nice
Status: active
Date: 2026-10-05
Source: `/gsd-validate-phase 7` at 16-02's checkpoint (Phase 16), last committed in `5ba02d2`;
the three rows are 16-02-SUMMARY.md's gap ledger, rows 1-3
Related files:
- .planning/milestones/v0.2-phases/07-foundation-generalized-edge-selection-regression-fixture/07-VALIDATION.md
- bench/RESULTS.md (section "Regression fixture cost (Phase 7, D-06)")
- tests/regression/capture.py
- tests/regression/test_pre_v0_2.py
- tests/test_model.py
- tests/test_calc.py

## Context

Phase 7 predates the Nyquist capability. The retroactive audit (run twice, `655583f` and
`5ba02d2`) reports 0 gaps and reads `nyquist_compliant: true` with all six per-task Status
cells green. Its `## Manual-Only Verifications` section lists three rows, and 16-02's ledger
counts every Manual-Only data row, whatever the audit called it, so each is filed here
(D-09: a task without a named automated command is `nice`; only a behaviour with no test at
all is `must`, and none of these is). Each behaviour runs under `make verify` today, or has
a committed measurement and a command that reproduces it.

## Gaps

| Task id | Gap (verbatim from 07-VALIDATION.md) | Proved today by |
|---------|--------------------------------------|-----------------|
| manual-only | D-06 cost gate: the fixture's `make verify` delta is measured and, above 15.0 s, decided by a human rather than trimmed silently | Committed record, not a behaviour: `bench/RESULTS.md` section "Regression fixture cost (Phase 7, D-06)" (mean(A) 32.10 s, mean(B) 48.37 s, delta 16.27 s, Option A accepted) and STATE.md Decisions "[Phase 07]: D-06 gate" |
| manual-only | Regeneration is byte-stable: two consecutive `make fixture.regen` runs on an unchanged tree write identical JSON | Committed record: `07-01-SUMMARY.md` coverage item "Regeneration is byte-stable" (cmp of two consecutive runs) and the row's own command in `07-VALIDATION.md`. Re-measured 2026-10-05 into the scratchpad, not committed: `capture.main()` run twice, outputs byte-identical. The replay `tests/regression/test_pre_v0_2.py` imports and runs capture's `derived` and `solid` helpers on every record (118 passed in 12.86s); no test runs the writer |
| manual-only | Tripwire: a silently vanished bore chamfer turns exactly the 32 chamfered-bore solid cases red and no derive case | Committed record: `07-VALIDATION.md` row (`32 failed, 53 passed in 13.81s`) and `07-VERIFICATION.md` (`32 failed, 53 passed in 13.64s`); re-run at HEAD 5ba02d2: `32 failed, 53 passed in 14.02s`, tree clean. The production path now raises instead: `tests/test_model.py::test_a_bore_chamfer_that_selects_no_rim_edges_is_a_build_error_not_a_bare_bore`, `tests/test_model.py::test_each_edge_selector_picks_exactly_its_own_edges`, `tests/test_model.py::test_a_recess_fillet_that_selects_no_floor_edges_is_a_build_error`, `tests/test_calc.py::test_the_bore_rim_limit_is_the_bore_radius_for_round_and_d_flat_bores` (118 passed in 12.86s, the cited ids as the plan's verify ran them) |

Row 2 is the closest call: the byte-stability of `capture.py`'s writer (sorted keys, indent 2,
trailing newline, deterministic kernel) has no test of its own. The writer produces a dev
file, not a number a user cuts metal to, so it stays `nice`; reclassify it if that changes.

## Why it matters

Low. These are missing named sampling commands, not unproven behaviours (`07-VERIFICATION.md`
reads `passed`). A change to a covered file has no named command to run first, so a
regression in the regeneration writer or the cost gate would be found by a human reading the
record rather than by the gate.

## Next step

When a covered file is next touched, name an automated command for its row and re-run
`/gsd-validate-phase 7`. For row 2 that is a test that runs `capture.main()` twice into a
temp path and compares the bytes.

Revisit when: the covered file is next touched (`tests/regression/capture.py`,
`tests/regression/test_pre_v0_2.py`, `src/spur/model.py` bore-rim selection, or `bench/RESULTS.md`'s fixture-cost section).

<!-- On resolve: set Status: resolved, add `Resolved in: <commit sha>`,
     git mv into resolved/, move the INDEX row to Resolved — same commit as the fix. -->
