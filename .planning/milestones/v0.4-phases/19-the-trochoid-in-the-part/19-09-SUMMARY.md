---
phase: 19-the-trochoid-in-the-part
plan: 09
subsystem: testing
tags: [trochoid, hob-root, bench, build-time, gate-cost, derive, tip-chamfer, L34, L36, L37]

requires:
  - phase: 19-the-trochoid-in-the-part
    provides: 19-01's spike readings and gate baseline; 19-02's adopted bars; 19-04/19-05's shipped outline and guards; 19-07/19-08's parity and composition tests
provides:
  - "bench/trochoid_part.py builds through spur.model (_gear_blank, _build_checked, _outline): one outline definition, the spike copy deleted"
  - "chamfer law re-run on the shipped outline: law holds, 8 rows on the law, 6 conservative"
  - "root arc dead band re-run on the shipped outline: the 11 refused rows are refused by the shipped annulus guard, and build once the guard is lifted"
  - "bench/sweeps/trochoid.json: the 17 corner rows 19-01 timed, each in both root shapes, pinned by tests/test_bench.py"
  - "heaviest trochoid row 14.64 s of 30 s on the real build (radial twin 9.50 s); L37's revisit trigger answered"
  - "make verify priced: 192.94 s mean against L34's 66 s on the baseline's host, +140.05 s; make verify.fast 11.39 to 11.54 s against L36's 30 s"
  - "derive() per-call cost re-read: 10.3 usec default, 30 usec with root_shape trochoid"
affects: [19-10, 19-11]

# Actuals (#2632): chars/4 over the lines added to bench/, src/ and tests/ in 5f3df84..HEAD.
actuals:
  tokens: 13009
  tasks: 2
  commits: 2

plan_head_before: 5f3df847f44a71a9caa001d8c98231fc2f4fb909
plan_head_after: f810fb62cdffe61bf3be617d2d6342149d686ad6

tech-stack:
  added: []
  patterns:
    - "the bench measures the shipped code: no copy of the assembly in bench/ (the 11-05 precedent)"
    - "a sweep file derived in its pin from corner_rows() and the refusal rule, never typed twice"

key-files:
  created:
    - bench/sweeps/trochoid.json
  modified:
    - bench/trochoid_part.py
    - tests/test_bench.py
    - bench/RESULTS.md
    - src/spur/calc.py

key-decisions:
  - "accept-A (2026-10-09): the measured gate cost is accepted and recorded in L38 (Phase 12 D-10's precedent); no test moves out of the gate, L34's 66 s bar and the 401-position oracle count (19-02) are unchanged"
  - "The bench now measures the shipped outline; where the copy and the real build differ the table records it, nothing is smoothed"

requirements-completed: [REQ-trochoid-composes-and-is-priced]

coverage:
  - id: D1
    description: "bench/trochoid_part.py defines no outline of its own and builds through spur.model"
    requirement: "REQ-trochoid-composes-and-is-priced"
    verification:
      - kind: unit
        ref: "tests/test_bench.py#test_the_trochoid_sweep_is_the_corner_rows_in_both_root_shapes"
        status: pass
      - kind: other
        ref: ".venv/bin/python -c (ast scan: trochoid_outline absent, model._outline / model._gear_blank present)"
        status: pass
    human_judgment: false
  - id: D2
    description: "The chamfer law holds on the shipped outline and the dead band is reported as the shipped guards leave it"
    requirement: "REQ-trochoid-composes-and-is-priced"
    verification:
      - kind: other
        ref: ".venv/bin/python -m bench.trochoid_part chamfer (Verdict: law holds)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Every corner row, in both root shapes, reads inside SPUR_BUILD_TIMEOUT = 30 s (heaviest 14.64 s)"
    requirement: "REQ-trochoid-composes-and-is-priced"
    verification:
      - kind: other
        ref: "make bench.build SWEEP=bench/sweeps/trochoid.json (exit 0, 34 requests inside 30 s)"
        status: pass
    human_judgment: false
  - id: D4
    description: "The gate's cost and derive()'s per-call cost are recorded on the baseline's host, and the human accepted a gate cost over L34's bar"
    requirement: "REQ-trochoid-composes-and-is-priced"
    verification:
      - kind: other
        ref: "make verify (1210 passed in 166.25s, exit 0)"
        status: pass
    human_judgment: true
    rationale: "A mean 2.92 times L34's 66 s bar is a judgment the human made (accept-A); automation records the number, it does not decide it is acceptable"

duration: ~2h wall across two executors and one checkpoint (approximate; the first executor's start was not recorded)
completed: 2026-10-09
status: complete
---

# Phase 19 Plan 09: The Hob Root Priced on the Code That Ships Summary

**The bench now builds through `spur.model` (one outline definition), the heaviest trochoid corner row reads 14.64 s of the 30 s timeout, and `make verify` reads 192.94 s mean against L34's 66 s bar, which the human accepted (`accept-A`) rather than trim.**

## Performance

- **Duration:** about 2 h wall across two executors and one checkpoint (approximate; the first executor's start time was not recorded)
- **Started:** 2026-10-09 (first dispatch at `5f3df84`)
- **Completed:** 2026-10-09T07:37Z (Task 2 commit `f810fb6`; SUMMARY follows)
- **Tasks:** 2
- **Files modified:** 5 (1 created)

## Accomplishments

- **One outline definition.** `bench/trochoid_part.py` lost `trochoid_outline`; blanks come from `model._gear_blank`, parts from `model._build_checked` with `root_shape="trochoid"`, and `run_arc` builds the hand-made curves through `model._outline`. `chamfer` re-run on the shipped outline: `Verdict: law holds -- 8 rows on the law, 6 conservative`.
- **The dead band, as shipped.** The 11 dead-band rows are refused by the shipped annulus guard (4.748526 mm against the 4.750000 mm bar with the guards on) and build once the guard is lifted; the table records what the shipped branch does with each curve.
- **SC4 on the real build.** `bench/sweeps/trochoid.json` holds the 17 corner rows `GearParams` accepts, each in both shapes, pinned by `tests/test_bench.py` (red first on `FileNotFoundError`). `make bench.build SWEEP=bench/sweeps/trochoid.json` exits 0: all 34 requests inside 30 s. **Heaviest: 14.64 s** (the 116-tooth, module-1.75, 60-hole, hex-bore row, trochoid), **15.36 s of margin**; its radial twin is 9.50 s (ratio 1.54, the largest of the 17 pairs; the other 16 read 0.98 to 1.19); 19-01's spike read 16.61 s on the same row. L37's 29.42 s row is the 200-tooth composition, where a trochoid request is ignored and warned, so it was not re-run and stands.
- **The gate priced on one host.** Three `make verify` runs: 208.01, 160.95 and 207.90 s of pytest, `real` mean **192.94 s** against L34's 66 s (2.92 times, 126.94 s over), **+140.05 s against 19-01's 52.89 s mean** on the same Apple M5 Max, with 187 more tests. 21 of the 25 slowest calls are this phase's kernel-tier rows in `tests/test_model.py`, 305.5 s of the run's 1,664 worker-seconds (18.4 %). `make verify.fast`: 11.46, 11.39, 11.54 s (824 tests) against L36's 30 s kill.
- **`derive()` per call.** 10.3 usec (default) and 30 usec (`root_shape="trochoid"`) at a 1-minute load of 2.55 to 2.67, best of 5; 10.2 and 29.8 usec at about 5.0 earlier that day. Both sit in the docstring with host, load and date, and in `bench/RESULTS.md`.

## Task Commits

1. **Task 1: One outline definition, the chamfer law and the dead band re-run, the corner rows timed in both shapes** - `4b08aa8` (perf). Its test, `test_the_trochoid_sweep_is_the_corner_rows_in_both_root_shapes`, was red on `FileNotFoundError` before the sweep file existed; there is no separate red commit because the pre-commit hook refuses a failing test.
2. **Task 2: The gate priced on one host, and `derive()`'s per-call cost** - `f810fb6` (perf)

**Plan metadata:** the SUMMARY commit that follows (docs: complete plan).

## Files Created/Modified

- `bench/trochoid_part.py` - the spike's outline copy deleted; the bench builds through `spur.model`
- `bench/sweeps/trochoid.json` - 17 corner rows, each followed by its trochoid twin (created)
- `tests/test_bench.py` - the pin: expected rows rebuilt from `corner_rows()` and the refusal rule, `load_sweep` validating each, every twin checked to be a trochoid build
- `bench/RESULTS.md` - `### Chamfer law on the real build (19-09)`, `### Composed build time on the real build (19-09)`, `### The gate, priced (19-09)`
- `src/spur/calc.py` - the `derive()` docstring's cost figure only

## Decisions Made

- **`accept-A`, the human's reply verbatim, 2026-10-09.** At the plan's step-2 gate the mean `make verify` wall (192.94 s) exceeded L34's 66.0 s bar, and the first executor stopped with three options: (A) accept the measured cost and record it in L38 (Phase 12 D-10's precedent); (B) move named kernel rows out of the gate into `bench/`; (C) raise the bar with a new decision. The human chose A directly. No test moves out of the gate, L34's 66 s is not changed, and the oracle's 401-position count (19-02) stays. The orchestrator's caveat, kept for the record: this leaves L34's 66 s on paper while the gate reads about 193 s; re-setting the bar from an idle-host measurement, or a measured revisit of the per-row position count, is a separate decision and is not part of this plan.
- **For 19-10's L38:** record (1) the gate cost: the three `make verify` runs (`1210 passed in 208.01s`, `160.95s`, `207.90s`; `real` mean 192.94 s against L34's 66 s), the +140.05 s delta against 19-01's 52.89 s on the same Apple M5 Max (L34's bar was set on an M2 Max with 12 CPUs), the wave table (52.89 s at 1026 tests, 112.79 s after wave 3, 137.76 s after wave 4, 206.05 s after wave 5 at 1209 tests), the kernel rows' 305.5 s share of the 25 slowest calls, and `make verify.fast` at 11.39 to 11.54 s, inside L36's 30 s; (2) that the human chose A, with no test moved and L34 and the position count untouched; (3) 19-07's SC5 and exit-code reading, `exit-documented`.
- The bench measures the shipped outline from here on; where the spike copy and the real build differ the table records it.

## Deviations from Plan

None - plan executed exactly as written. The step-2 stop (mean over 66.0 s) is the plan's own gate and its `checkpoint:decision`, not a deviation; it was answered `accept-A`, which is the plan's option A.

## Authentication Gates

None.

## Issues Encountered

- **The gate reads 2.92 times its bar.** Recorded, not fixed (see Decisions Made). The loads were between 4 and 9 during the three runs and rose with each run's own eight workers, so the figures are upper bounds for an idle host. The final `make verify` after Task 2 read lower, `1210 passed in 166.25s` (`real` 166.77 s, exit 0), at a quieter start (1-minute load 2.55); it is a fourth reading, not part of the three-run mean, and it is still 2.5 times the bar.
- No `ReentrantCallError` in any of the five full runs (three timed, one `--durations`, one final), so the resource-tracker debt item did not fire.

## Known Stubs

None. No stub, skipped test or unrun `<verify>` was left behind, so nothing was appended to `.planning/WINDOWS.md`.

## Threat Flags

None. The plan adds a bench sweep file, a pin and a docstring figure; no endpoint, auth path, file access or schema at a trust boundary.

## User Setup Required

None - no external service configuration required.

## Debt and Ideas Filed

None filed. One candidate for the human: L34's 66 s now sits against a gate that reads about 193 s on this host (about 167 s on the quietest reading). The orchestrator named the re-set of the bar as a separate decision; L38 (19-10) records the cost, and a debt item or a new Lxx is the human's call.

## Next Phase Readiness

- 19-10 (L38) has every figure it needs in `bench/RESULTS.md` `### The gate, priced (19-09)` and in the decision note above.
- 19-11 is not affected.
- Open: L34's bar against the measured gate, as above.

## Self-Check: PASSED

- FOUND: `bench/sweeps/trochoid.json`, `bench/trochoid_part.py`, `tests/test_bench.py`, `bench/RESULTS.md`, `src/spur/calc.py`
- FOUND commits `4b08aa8` and `f810fb6` (both ancestors of HEAD; `git rev-list --count 5f3df84..HEAD` was 2 before this SUMMARY)
- Task 2 verify: the gate subsection check printed `19-09 gate subsection present` (7 `passed in` lines), the `derive()` docstring check printed `derive docstring re-measured`, and `make verify` finished `1210 passed in 166.25s`, exit 0
- Nothing under `tests/` other than `tests/test_bench.py` (Task 1), the Makefile, `decision_log.md` or L34 was changed

---
*Phase: 19-the-trochoid-in-the-part*
*Completed: 2026-10-09*
