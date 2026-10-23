---
phase: 28-refuse-the-bad-link
plan: 06
subsystem: calc
tags: [gap-closure, tip-chamfer, L08, decision-log, tech-debt]
status: complete
gap_closure: true
gap_ids: [G-28-2]

requires:
  - phase: 28-refuse-the-bad-link
    provides: D-21 (`fix`) in 28-CONTEXT.md, the human's pick at the 28-05 checkpoint
provides:
  - derive() prints tip_chamfer_effective only when a chamfer is cut (null otherwise)
  - L45, the last entry of docs/architecture/decision_log.md
  - the tip-chamfer debt item retired
affects: [28-07, 28-08]

actuals:
  tokens: 4500
  tasks: 2
  commits: 1
plan_head_before: 268fe72edeb9e21e70540af3298a51599fe06c5e
plan_head_after: 6497c2863cb49c905afe04bd55e39a75e4907121

tech-stack:
  added: []
  patterns: []

key-files:
  created:
    - .planning/phases/28-refuse-the-bad-link/investigation/28-06-red-tip-chamfer-null.log
    - .planning/phases/28-refuse-the-bad-link/investigation/28-06-fixture-check.log
  modified:
    - src/spur/calc.py
    - tests/test_calc.py
    - docs/architecture/decision_log.md
    - docs/tech_debt/INDEX.md
    - docs/tech_debt/resolved/2026-10-21-tip-chamfer-effective-gate-reads-the-request.md
    - bench/RESULTS.md

key-decisions:
  - "L45: a tip chamfer asked for and not cut prints no number; tip_chamfer_effective is gated on the applied tch (amends L29's number paragraph, applies L08)"

requirements-completed: [REQ-old-info-findings-triaged, REQ-info-findings-triaged]

duration: about 20 min
completed: 2026-10-21
---

# Phase 28 Plan 06: D-21, a tip chamfer not cut prints null Summary

**`derive()` now gates `tip_chamfer_effective` on the applied `tch`, so a request under 0.0005 mm prints `null` like no chamfer does, beside the unchanged "was not cut" warning; logged as L45 with the fixture check and the retired debt item in one commit.**

## D-21 branch

`fix` (read from `28-CONTEXT.md`). Commit `6497c28` (`fix(28): print no tip chamfer when none is cut -- log L45`). It names nothing under `tests/regression/`.

## What changed

- `src/spur/calc.py`: `tip_chamfer_effective=r3(tch) if tch > 0 else None` with a comment citing L45 and L08; the field's description says null when none is cut (none requested, or a request below the 0.001 mm resolution). `tip_chamfer_effective()`, the warning branches and `model.py` untouched.
- `tests/test_calc.py`: the sub-print test asserts `d.tip_chamfer_effective is None`; the capped-chamfer test states its rule on `applied > 0`.
- `docs/architecture/decision_log.md`: L45, last heading, cites D-21, G-28-2, L29, L08, with Reversibility and Reason.
- Debt item `git mv`ed to `resolved/` with `Status: resolved` and a `Resolved in:` line; INDEX Active row removed, Resolved row added on top (28-08 writes the sha).
- `bench/RESULTS.md`: a 28-06 row in `### Seen red once (Phase 28)`.

## RED (TDD)

- Target: `tests/test_calc.py::test_a_sub_print_precision_tip_chamfer_request_still_warns`, run with `.venv/bin/python -m pytest tests/test_calc.py -k "sub_print_precision or capped_to_whichever" -n0 --no-cov -q -p no:cacheprovider` on the unchanged `calc.py`.
- First failure line: `AssertionError: assert 0.0 is None` (`tests/test_calc.py:692`); `1 failed, 20 passed, 484 deselected in 0.16s`. Exactly the sub-print test failed, on the planned null assertion, for the intended reason (the old gate reads the request). Log: `investigation/28-06-red-tip-chamfer-null.log`.
- GREEN: same command after the fix, `21 passed`.
- The plan asks for one commit holding the red proof and the fix, so there is no separate `test(...)` commit; the red run is kept as a log and a RESULTS row instead.

## Fixture check

`make fixture.regen` ran on the fixed tree after `tests/regression/` was proven equal to HEAD. Last line: `fixture check: 44 records, no held field moved, tip_chamfer_effective null in all 44` (log `investigation/28-06-fixture-check.log`). The file was restored from HEAD by the EXIT trap and the explicit restore; `git status --porcelain --untracked-files=all -- tests/regression/` is empty and `git diff --exit-code v0.5 -- tests/regression/` is empty. No fixture commit was made (D-13).

## Verification

- Task 1 automated check: `D-21 fix: carried out`, exit 0.
- `.venv/bin/python -m pytest tests/test_calc.py -k tip_chamfer -n0 --no-cov -q -p no:cacheprovider`: `24 passed, 481 deselected`.
- Command `make verify`: exit 0, result line `======================= 1348 passed in 223.73s (0:03:43) =======================`, coverage `TOTAL 1358 22 386 13 97.99%`, `Required test coverage of 96.0% reached`. The pre-v0.2 replay is inside that run.
- `git diff --exit-code v0.5 -- tests/regression/`: empty. `git status --short` shows only `.planning/state.json` and `.planning/milestone.lock`.

## Deviations from Plan

None - plan executed exactly as written.

## Known Stubs

None.

## Filed debt

None filed. One item retired: `docs/tech_debt/resolved/2026-10-21-tip-chamfer-effective-gate-reads-the-request.md`.

## Threat Flags

None.

## Next Phase Readiness

Ready for 28-07 (D-19, D-22 and D-20's disposition row) and 28-08 (IN-02, the ledger, and the sha for this item's `Resolved in:`).

## Self-Check: PASSED

- FOUND: `.planning/phases/28-refuse-the-bad-link/investigation/28-06-red-tip-chamfer-null.log`
- FOUND: `.planning/phases/28-refuse-the-bad-link/investigation/28-06-fixture-check.log`
- FOUND: `docs/tech_debt/resolved/2026-10-21-tip-chamfer-effective-gate-reads-the-request.md`
- FOUND commit: `6497c28` (ancestor of HEAD)
