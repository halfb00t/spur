---
phase: 19-the-trochoid-in-the-part
plan: 01
subsystem: bench
tags: [cadquery, trochoid, tip-chamfer, build-time, spike, bench]

requires:
  - phase: 18-trochoid-maths-proved
    provides: RootCurve / root_mode / the swept-cutter oracle tests/trochoid_oracle.clearance
provides:
  - bench/trochoid_part.py (the spike: trochoid_outline, trochoid_blank, trochoid_cap, trochoid_part, root_edges, oracle_reading, chamfer_verdict, CHAMFER_ROWS, boundary, CORNER, corner_rows; subcommands chamfer and heaviest)
  - the gate's before-figure on this host (bench/RESULTS.md "Gate baseline (19-01)")
  - L29's chamfer law re-bisected across the spline-to-spline junction, 14 rows, verdict law holds
  - build time of the heaviest allowed low-tooth rows, radial and trochoid, all inside 30 s
affects: [19-02, 19-03, 19-04, 19-09, 19-10]

actuals:
  tokens: 13000
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - "spike before schema change: a bench script builds the part itself through the shipped pipeline steps (the L29 precedent)"
    - "a selector that selects nothing must fail: root_edges asserts 2 x teeth before any sample is read (L26)"

key-files:
  created:
    - bench/trochoid_part.py
    - .planning/phases/19-the-trochoid-in-the-part/investigation/19-01-gate-flake.log
  modified:
    - tests/test_bench.py
    - bench/RESULTS.md

key-decisions:
  - "TIP_CHAMFER_MARGIN (0.001 mm) stands under the trochoid: no optimistic row in 14, 8 rows within one bisection step (3.2e-6 mm) of ra - R_join, 6 conservative"
  - "ra - R_join is the binding chamfer cap only on the two 6-tooth rows of CHAMFER_ROWS (junction above the pitch circle)"
  - "No timing decision needed: the heaviest trochoid request at the corner is 16.61 s of 30 s, so no checkpoint was raised and no limit moves"

patterns-established:
  - "The spike's trochoid_outline is a copy: 19-04 moves it into model.py, 19-09 replaces the bench copy with the shipped one"

requirements-completed: []  # REQ-trochoid-composes-and-is-priced, REQ-outline-consumes-root-curve: declared by sibling plans with no SUMMARY yet, so requirements.ready-ids returned 0/2 ready (#2388 shared-ID gate); nothing marked

coverage:
  - id: D1
    description: "The gate's before-figure at the phase base on this host: three green make verify readings with result line, wall time, loads, host and kernel pair"
    requirement: REQ-trochoid-composes-and-is-priced
    verification:
      - kind: other
        ref: "bench/RESULTS.md ### Gate baseline (19-01) (runs 1, 3, 4 green; run 2 the known flake, log kept)"
        status: pass
    human_judgment: false
  - id: D2
    description: "L29's tip-chamfer kernel law across the spline-to-spline junction: 20-step bisection on 14 CHAMFER_ROWS, verdict law holds"
    requirement: REQ-outline-consumes-root-curve
    verification:
      - kind: unit
        ref: "tests/test_bench.py#test_the_chamfer_law_verdict_is_never_optimistic"
        status: pass
      - kind: unit
        ref: "tests/test_bench.py#test_the_chamfer_rows_are_fourteen_trochoid_gears"
        status: pass
      - kind: other
        ref: ".venv/bin/python -m bench.trochoid_part chamfer (exit 0, 'Verdict: law holds')"
        status: pass
    human_judgment: false
  - id: D3
    description: "The heaviest allowed low-tooth rows timed radial and trochoid, build plus the slower export, against SPUR_BUILD_TIMEOUT = 30 s"
    requirement: REQ-trochoid-composes-and-is-priced
    verification:
      - kind: unit
        ref: "tests/test_bench.py#test_the_corner_rows_are_the_composed_sweep_at_the_trochoid_corner"
        status: pass
      - kind: other
        ref: ".venv/bin/python -m bench.trochoid_part heaviest (exit 0, 17 pairs inside 30 s)"
        status: pass
    human_judgment: false
  - id: D4
    description: "Nothing a shared link produces changed: no product module and no fixture byte moved"
    verification:
      - kind: other
        ref: "SC1 check: git diff --quiet <phase base> over params/calc/model/cli/app.js/pre_v0_2.json, no numpy/scipy, 31 pins"
        status: pass
    human_judgment: false

duration: 27min
completed: 2026-10-08
status: complete
plan_head_before: 29c742c7d8264d5f3a2753d8e84c087739ea2513
plan_head_after: abe318e717075a6a1046805135e398701872687b
commits: 2
---

# Phase 19 Plan 01: Spikes before any schema change Summary

**Tip-chamfer law (ra - R_join) re-bisected across the hob root's spline junction on 14 rows with no optimistic row, and the heaviest trochoid request at the 116-tooth corner measured at 16.61 s of 30 s, both from a bench-built trochoid outline and before any product module moved.**

## Performance

- **Duration:** about 27 min (including four `make verify` baseline runs, a 4 min 46 s chamfer run and a 5 min heaviest run)
- **Started:** 2026-10-08T16:09Z (approximate; the first baseline run began 16:10Z)
- **Completed:** 2026-10-08T16:36Z
- **Tasks:** 2
- **Files modified:** 3 (`bench/trochoid_part.py` created, `tests/test_bench.py` and `bench/RESULTS.md` extended), plus the flake log under `investigation/`

## Accomplishments

- **Gate baseline** (`### Gate baseline (19-01)`), phase base `df4749e`, HEAD `29c742c` (planning documents only), Apple M5 Max, 18 CPUs, Python 3.12.15, cadquery 2.8.0 / cadquery-ocp 7.9.3.1.1. Four runs, one flake:

  | Run | Result line | `real` s | 1-min load before -> after |
  |---|---|---|---|
  | 1 | `1023 passed in 53.89s` | 54.60 | 3.16 -> 16.71 |
  | 2 | `1 failed, 1022 passed in 53.61s` | 54.04 | 16.71 -> 22.09 |
  | 3 | `1023 passed in 52.10s` | 52.53 | 22.09 -> 24.94 |
  | 4 | `1023 passed in 51.09s` | 51.53 | 11.75 -> 24.80 |

  Mean of the three green runs, `real` 52.89 s. Run 2 failed `tests/test_pool.py::test_a_dying_worker_surfaces_as_broken_pool_and_is_replaced` on worker `gw0` with `ReentrantCallError` (the known flake); the log is kept at `investigation/19-01-gate-flake.log` for 19-03. No conclusion is drawn against L34's 63.555 s / 66 s bar (12-CPU M2 Max); 19-09 reads the delta.
- **Chamfer across the junction**: `python -m bench.trochoid_part chamfer` exits 0, `Verdict: law holds -- 8 rows on the law, 6 conservative`. The 8 rows on the law last built 0.5 to 3.1 microns inside `pred = ra - R_join` and first failed 0.1 to 2.7 microns past it (bracket 3.2e-6 mm = 3.375 / 2^20). **Worst `last ok - pred` on a row on the law: -3.06e-06 mm** (100 teeth, m 1, 14.5 deg, x -0.6, tip radius 0.5); no row is optimistic. The six conservative rows are the six RESEARCH F5 named: 30 teeth at both tip radii (+0.0149 and +1.40 mm), 10 teeth at 0 (+1.01), 8 teeth at both (+0.110 and +1.05), 6 teeth at 0.5 (+0.35). Three stopped at 2.25 mm, the whole tooth depth `ra - rf` (ASSUMPTION: the footprint reaching the root circle, not isolated). `ra - R_join` binds only on the two 6-tooth rows (R_join 3.0994 and 3.0183 mm against r 3.0); `ra - r` binds on the other twelve.
- **Heaviest low-tooth rows**: all 18 `composed.json` rows moved to 116 teeth / 14.5 deg / x -0.6 plus two module-10 light rows; 17 validated and timed as radial/trochoid pairs, 3 refused by `GearParams` (200 mm bores against a 196.53 mm root circle). `heaviest` exits 0, every request inside 30 s. **Heaviest trochoid row: module 1.75, 156.3 mm hex bore, 60 holes (1 mm on 183.4 mm), chamfer 1.75, both recesses: 16.61 s (build 16.20 + STL 0.41, STEP 0.27), 13.39 s of margin, 1.45x its radial row (11.48 s)**; it is also the heaviest row overall. Next: keyed 32-spoke module 10 at 14.98 s trochoid / 13.82 s radial (1.08x; RESEARCH F7's scratch read 12.24 / 11.12 s, ratio 1.10), hex-bore 32-spoke module 10 at 14.66 / 12.85 s. Trochoid over radial ranges 0.83 to 1.45 (14 of 17 pairs above 1). Host load 4.86 at start, 9.48 at end, so every figure is an upper bound for this host.
- **Oracle readings** on the built trochoid parts' tooth-0 root: chamfer rows worst **1.23e-04 mm** (30 teeth, module 1, tip radius 0.5); heaviest rows 1.12e-04 mm (module 1.75) and 2.79e-04 mm (module 10). No bar applied (19-02 sets it). The root-edge selector returned exactly 2 x teeth on all 14 + 17 parts.
- **`make verify`: `1026 passed in 67.85s (0:01:07)`, coverage 97.68 % (floor 96)**, ruff, mypy --strict (43 files, `bench` included), import contracts and the unfinished-work scan green, run before the second commit at 1-minute load 5.28.
- **SC1 check** (`SC1 holds: fixture and product modules as at the phase base, stdlib maths, 31 pins`) after both tasks: `params.py`, `calc.py`, `model.py`, `cli.py`, `app.js` and `tests/regression/pre_v0_2.json` are byte-identical to `git merge-base HEAD origin/main`.

## Task Commits

1. **Task 1: Gate before-figure, spike harness, chamfer law (20-step bisection on 14 rows)** - `7a0268f` (feat)
2. **Task 2: Heaviest allowed low-tooth rows, radial and trochoid, against SPUR_BUILD_TIMEOUT** - `abe318e` (feat)

**Plan metadata:** the docs commit that carries this SUMMARY, STATE.md, ROADMAP.md and the flake log (hash in the STATE.md session line).

## Files Created/Modified

- `bench/trochoid_part.py` - the Phase 19 kernel spike, `chamfer` and `heaviest` subcommands (new)
- `tests/test_bench.py` - three pins, no kernel build: the chamfer verdict is never optimistic, the rows are fourteen trochoid gears (scratch pred checked to 1e-4), the corner rows are the composed sweep at the corner
- `bench/RESULTS.md` - `## Trochoid in the part (Phase 19)` with `### Gate baseline (19-01)`, `### Chamfer across the junction (19-01)`, `### Heaviest low-tooth rows (19-01)`, each with its host state
- `.planning/phases/19-the-trochoid-in-the-part/investigation/19-01-gate-flake.log` - the failing run's whole log, evidence for 19-03

## Decisions Made

- `TIP_CHAMFER_MARGIN` stands at 0.001 mm under the trochoid; 19-04's cap rule `min(0.45 x face_width, ra - r, ra - R_join - TIP_CHAMFER_MARGIN)` (RESEARCH Pattern 8) is backed by 14 rows with no optimistic one.
- No checkpoint was raised: no row was optimistic and no row exceeded 30 s, so the plan's two blocking gates did not fire and nothing was trimmed, re-picked or re-run.
- The bench copy of `trochoid_outline` follows RESEARCH Pattern 2 exactly, so that 19-04 can move it into `model.py` without the measurements describing a different part (T-19-01).

## Deviations from Plan

### Plan-literal items that did not apply

**1. [Premise not met] No refused hole row, so no replacement hole rows were built**
- **Found during:** Task 2
- **Issue:** the plan's step 2 adds a replacement row (largest `hole_circle_d` `check()` accepts, 0.05 mm step search) for every refused hole row (RESEARCH A12). At the corner all five 60-hole rows of `composed.json` validate; the refusals are three bore rows (rows 9, 13 and 14 in 1-based file order: `bore_hex=200` with honeycomb, `bore_hex=200` alone, `bore_d=200` keyed), none a hole row.
- **Fix:** none written: a replacement search with no input would be a branch that never runs (CLAUDE.md "no unreachable branches"). The three refusals are printed with their sentences and every cutout family is timed on the other rows. If `composed.json` gains a refused hole row, `run_heaviest` prints it as a refusal, which is the plan's "never silently dropped".
- **Files modified:** none.

**2. [TDD ceremony] RED was a load failure, and there is no separate `test(...)` commit**
- **Found during:** Task 1 (`tdd="true"`)
- **Issue:** the tests were written first and run before the module existed: `ModuleNotFoundError: No module named 'bench.trochoid_part'` at collection. By `tdd.md` that is a load failure (INVALID_RED), not a valid RED, and no `test(19-01)` commit exists: the plan prescribes one `feat(19-01)` commit per task, and the L36 pre-commit hook (`make verify.fast`) refuses a commit with a failing test. This is a plan of `type: execute`, not `type: tdd`, so the plan-level gate sequence does not apply.
- **Fix:** none; recorded here so it is not read as a RED/GREEN pair. GREEN: `2 passed` then `3 passed` on the new tests, `1026 passed` on the gate.

---

**Total deviations:** 2 plan-literal items (0 auto-fixes under Rules 1-3).
**Impact on plan:** none on the measurements or the gates; both items remove ceremony that had nothing to act on.

## Issues Encountered

- **Run 2 of the baseline failed on the known resource-tracker flake** (`ReentrantCallError` in `test_a_dying_worker_surfaces_as_broken_pool_and_is_replaced`). The whole log is kept; a fourth run was taken so three green readings exist, as the plan asks.
- The baseline loads are not independent readings (each run's "after" is mostly the next run's "before", and the 1-minute load contains the run's own eight workers). Recorded in the RESULTS host state.

## Known Stubs

None. `bench/trochoid_part.py` carries no placeholder values; the typed `CHAMFER_ROWS` scratch preds are checked against the live `root_mode` to 1e-4 by a test.

## Threat Flags

None. No network, auth, file-access or trust-boundary surface was added; the only new import path is `tests/` onto `sys.path` inside `oracle_reading`, the way `bench/trochoid.py` already does it.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- 19-02 can set the oracle bar from these readings (worst 2.79e-04 mm at module 10, 1.23e-04 mm at module 1) and extend `bench/trochoid_part.py` with `spline`, `arc`, `product`, `waist`.
- 19-03 has the failing run's log (`investigation/19-01-gate-flake.log`) and the failing test's name.
- 19-04 builds the first task that touches `src/` (the phase's tracer); the spike left `src/spur/params.py`, `calc.py`, `model.py`, `cli.py`, `static/app.js` and the pre-v0.2 fixture byte-identical to the phase base.
- 19-09 compares its end-of-phase gate with the 52.89 s mean above, on this host.

## Self-Check: PASSED

- `bench/trochoid_part.py`, `.planning/phases/19-the-trochoid-in-the-part/investigation/19-01-gate-flake.log` and `bench/RESULTS.md` sections exist (checked below); commits `7a0268f` and `abe318e` are ancestors of HEAD.

---
*Phase: 19-the-trochoid-in-the-part*
*Completed: 2026-10-08*
