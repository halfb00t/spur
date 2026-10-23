---
phase: 27-ledger-tests-and-harness
plan: 04
subsystem: testing
tags: [model, tip-chamfer, root-mode, bench, host-state, tech-debt]

requires:
  - phase: 27-ledger-tests-and-harness
    provides: 27-03 left docs/tech_debt/INDEX.md and the investigation/ directory free (one writer per wave)
provides:
  - _chamfer_tips takes the build's one root answer, so the tip chamfer limit reads the curve the part was cut from
  - trochoid_curve in the bench reads rm.curve instead of solving it again
  - _host_state prints HEAD unknown where git cannot name one
  - the Phase 19 debt item reduced to the Phase 28 root_fillet label
affects: [27-06 triage table (IN-02 near-copies skipped, D-07), Phase 28 (REQ-root-fillet-label-follows-root)]

actuals:
  tokens: 3200
  tasks: 2
  commits: 2   # MEASURED: git rev-list --count efbbbe0..HEAD at write time (before the SUMMARY commit)

plan_head_before: efbbbe075fa065454a8e5a1009e79b65811f6804
plan_head_after: 9c62faca7a39da35f16b05ce0d9883f2f1d06216

tech-stack:
  added: []
  patterns:
    - "A bench helper reads the answer root_mode already holds (RootMode.curve) instead of re-solving it"
    - "A host block that cannot read a fact says unknown, never a guess (L08)"

key-files:
  created:
    - .planning/phases/27-ledger-tests-and-harness/investigation/27-04-red-host-state.log
    - .planning/phases/27-ledger-tests-and-harness/investigation/27-04-curve-equal.log
  modified:
    - src/spur/model.py
    - tests/test_model.py
    - bench/trochoid_part.py
    - tests/test_bench.py
    - docs/tech_debt/active/2026-10-09-phase-19-review-info-findings-deferred.md
    - docs/tech_debt/INDEX.md

key-decisions:
  - "D-03 is behaviour-free by proof, not by argument: the fixture diff against v0.5 is empty, the 86-record regression replay and the 55 chamfer tests pass, and no call-count test was added (D-04)"
  - "The Phase 19 item stays active and is edited in place; only the root_fillet label (Phase 28) remains"

patterns-established:
  - "Tracer slice for a one-file src/ change: prove the fixture and the src/ diff first, then expand into the bench"

requirements-completed: []  # empty on purpose: the plan's requirements field is empty (human's 2026-10-20 plan-phase choice); REQ-info-findings-triaged is Phase 28's and is not marked

contributes_to: [REQ-info-findings-triaged]

coverage:
  - id: D1
    description: "The tip chamfer limit reads the build's one root answer; the part, the printed numbers and the 44-record fixture do not move"
    requirement: REQ-info-findings-triaged
    verification:
      - kind: integration
        ref: "pytest tests/regression -n 8 (86 passed), pytest tests/test_model.py -k chamfer (55 passed), git diff --exit-code v0.5 -- tests/regression/ (exit 0)"
        status: pass
    human_judgment: false
  - id: D2
    description: "src/spur/model.py is the only file under src/ that differs from v0.5"
    verification:
      - kind: other
        ref: "git diff --name-only v0.5 -- src/ prints src/spur/model.py"
        status: pass
    human_judgment: false
  - id: D3
    description: "_host_state prints HEAD unknown where git rev-parse raises CalledProcessError or FileNotFoundError, seen red first"
    requirement: REQ-info-findings-triaged
    verification:
      - kind: unit
        ref: "tests/test_bench.py#test_the_host_state_reads_unknown_where_git_cannot_name_head_[no-git-binary,not-a-checkout] (red log 2 failed, green 2 passed)"
        status: pass
    human_judgment: false
  - id: D4
    description: "trochoid_curve reads rm.curve and the stale 19-04 paragraph is gone; the curve equals trochoid_root(rm.cutter) on all CHAMFER_ROWS"
    requirement: REQ-info-findings-triaged
    verification:
      - kind: other
        ref: "investigation/27-04-curve-equal.log (14 of 14 equal)"
        status: pass
    human_judgment: false
  - id: D5
    description: "The Phase 19 debt item and its INDEX row say exactly what remains"
    verification:
      - kind: other
        ref: "Task 2 automated grep over the item and INDEX.md"
        status: pass
    human_judgment: true
    rationale: "Whether the Update paragraph and the rewritten Next step read as the ledger's convention is a reading, not a test"

duration: 7min
completed: 2026-10-20
status: complete
---

# Phase 27 Plan 04: the tip chamfer reads the build's root answer Summary

**`_chamfer_tips` now takes `_build`'s one `RootMode` so a chamfered trochoid build no longer solves the curve twice (the only `src/` change in the milestone, fixture byte-identical), and the trochoid bench reads `rm.curve` and prints `HEAD: unknown` where git cannot name one.**

## Performance

- **Duration:** 7 min
- **Started:** 2026-10-20T13:41:18Z
- **Completed:** 2026-10-20T13:48:10Z
- **Tasks:** 2
- **Files modified:** 8 in the two task commits (4 code and test files, the debt item, INDEX, 2 logs)

## Accomplishments

- Task 1 (`f7d0366`): `RootMode` joins the `.calc` import block; `_chamfer_tips(solid, p, pr, rm)` calls `tip_chamfer_effective(p, rm)`; `_build` passes its `rm`. The two `tests/test_model.py` patches keep their names and take the new shape (`lambda solid, _p, _pr, _rm: solid`, `lambda _p, _rm=None: 2.9875`).
- Nothing moved: `git diff --name-only v0.5 -- src/` prints `src/spur/model.py` alone; `git diff --exit-code v0.5 -- tests/regression/` exits 0; the regression replay reads `86 passed in 5.31s`; `-k chamfer` reads `55 passed in 40.06s`; `make verify.fast` reads `929 passed in 10.48s`.
- Task 2 (`9c62fac`): `_host_state` catches `CalledProcessError` and `FileNotFoundError` and writes `unknown`. The two-row test (`no-git-binary`, `not-a-checkout`) was red against the old code (`2 failed in 1.70s`, the error escaping) and green after (`2 passed in 1.56s`).
- `trochoid_curve` reads `rm.curve`, keeps the `None` check for mypy narrowing, and the stale "does not exist until 19-04" paragraph is replaced by one sentence. On all 14 `CHAMFER_ROWS`, `curve == trochoid_root(cut)`: `14 of 14 equal` (script and result in the log).
- The Phase 19 debt item is retitled `Phase 19 code review: the root_fillet label finding is still deferred`, carries a dated Update paragraph, and its Next step is the label alone; its INDEX row says Phase 28 or the `DIMS` table.

## Gate

`make verify` exited 0: `1331 passed in 205.23s (0:03:25)`, `Required test coverage of 96.0% reached. Total coverage: 97.99%`.

## Task Commits

1. **Task 1: `_chamfer_tips` takes the build's root answer** - `f7d0366` (refactor)
2. **Task 2: bench reads `rm.curve`, names an unknown HEAD, debt item edited** - `9c62fac` (fix)

**Plan metadata:** the commit that adds this SUMMARY, STATE.md and ROADMAP.md (docs: complete plan)

TDD note: `workflow.tdd_mode` is not enabled and the plan is `type: execute`, so the red run is kept in the log and RED and GREEN share the fix commit, as 27-02 and 27-03 did. Task 1 is a `type="tracer"` task; its feedback gate was the automated `<verify>` re-run (fixture and `src/` diff), which held before the bench work began.

## Files Created/Modified

- `src/spur/model.py` - `_chamfer_tips` takes `rm: RootMode`; `_build` passes it; one docstring sentence
- `tests/test_model.py` - the two patched lambdas take the new argument shape
- `bench/trochoid_part.py` - `trochoid_curve` reads `rm.curve`; `_host_state` catches the two git failures
- `tests/test_bench.py` - `test_the_host_state_reads_unknown_where_git_cannot_name_head`
- `docs/tech_debt/active/2026-10-09-phase-19-review-info-findings-deferred.md`, `docs/tech_debt/INDEX.md` - edited in place
- `.planning/phases/27-ledger-tests-and-harness/investigation/27-04-{red-host-state,curve-equal}.log`

## Decisions Made

- The bench's near-copies (`root_edges`, `tooth0_root_edges`, `oracle_reading`) stay unchanged. 27-06 records the replacement as `skipped` in the triage table (D-07): the test helpers differ in error type (assert against `ValueError`), in sample count (fixed 400 against a `samples` parameter) and in signature.
- The curve-equality check is a kept one-off log, not a test (plan step 3). It needs `PYTHONPATH=.` because `bench` is not installed; the log header says so.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- The first run of the curve-equality script failed with `ModuleNotFoundError: No module named 'bench'` because the script lives in the scratchpad, not the repo root. Re-run with `PYTHONPATH=.` (as `tests/test_bench.py`'s docstring explains for `bench`); the kept log holds the successful run.
- `.planning/milestone.lock` is untracked and predates this plan; left alone.

## Known Stubs

None.

## Debt filed

None filed. One item edited in place and still active: `docs/tech_debt/active/2026-10-09-phase-19-review-info-findings-deferred.md` (only the `root_fillet` label remains, Phase 28).

## Authentication Gates

None.

## User Setup Required

None - no external service configuration required.

## Threat Flags

None. No new endpoint, auth path or trust-boundary file access; T-27-14 and T-27-15 are mitigated as planned (fixture byte-identical and `src/` diff limited to `model.py`; `unknown` on both git failures, two-row test seen red first).

## Next Phase Readiness

- 27-06 should record IN-02's near-copy replacement as `skipped` with the reason above, and may cite `investigation/27-04-red-host-state.log` (2 failed) for a "Seen red once" row.
- `docs/tech_debt/INDEX.md` is free for the next wave.

---
*Phase: 27-ledger-tests-and-harness*
*Completed: 2026-10-20*

## Self-Check: PASSED

Verified: both `27-04-*.log` files exist; `f7d0366` and `9c62fac` are ancestors of HEAD; `git diff --name-only v0.5 -- src/` prints `src/spur/model.py`; `git diff --exit-code v0.5 -- tests/regression/` exits 0; `root_edges`, `tooth0_root_edges` and `oracle_reading` are still defined in `bench/trochoid_part.py`.
