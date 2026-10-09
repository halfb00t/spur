---
phase: 18-trochoid-maths-proved
plan: 03
subsystem: gear-maths
tags: [trochoid, join-epsilon, z-min-double-root, generator-sweep, refusal-list, bench, stdlib-math, calc]

requires:
  - phase: 18-trochoid-maths-proved
    provides: "plan 02: root_mode with all six refusals, _waist, undercut_teeth/undercut_shift; plan 01: cutter, _junction, trochoid_root, the oracle"
provides:
  - "bench/trochoid.py: epsilon and sweep scenarios, GRID_A, GRID_B, CAP_REQUEST_MM, SWEEP_BAR, sweep_cases, rack, check_curve, check_case, junction_gaps, tuned_shift"
  - "TROCHOID_JOIN_EPS = 1e-4 measured in the repo (largest lost bracket 5.6e-6 rb), its comment quoting the run"
  - "the z_min double root pinned: one tooth step, one field step, the band's two sides, STACK's two points; bracket degenerate and curve invalid each reached by a test with a captured sentence"
  - "the generator sweep as a commit-time gate test over all 31,446 cases, tally pinned; the explicit grids pinned as the cross product the plan names"
  - "investigation/18-03-refusals.tsv: every generator refusal of the product, 8,228 rows"
affects: [18-04, 18-05, 19]

actuals:
  tokens: 11187   # chars/4 over the added lines of bench/trochoid.py, src and tests (44,747 chars)
  tasks: 2        # Task 3 (the checkpoint) was not reached
  commits: 4      # MEASURED: git rev-list --count 78f3b51..afe7212
plan_head_before: 78f3b51b3306b98155c9a480ac322849d7fca647
plan_head_after: afe72126174a14c8c899fc85c3caf82997c1a140
commits: 4

tech-stack:
  added: []
  patterns:
    - "a constant relative to a scale (rb) is measured at several scales and written with the run beside it"
    - "a sweep grid written as literals in the bench, pinned in a test as the cross product, run at commit when it prices under the budget"
    - "closed forms typed in the checker from the textbook rack, not read from the code under test; mutations of the code made the checker fail"
    - "xi is linear in the profile shift, so a gear is placed on its own z_min double root from one cutter (tuned_shift)"

key-files:
  created:
    - bench/trochoid.py
    - .planning/phases/18-trochoid-maths-proved/investigation/18-03-refusals.tsv
  modified:
    - src/spur/calc.py
    - tests/test_trochoid.py
    - tests/test_calc.py
    - tests/test_bench.py
    - bench/RESULTS.md

key-decisions:
  - "TROCHOID_JOIN_EPS stays 1e-4: the in-repo scan (400 seeded draws) lost the bracket at most at xi = -5.6e-6 rb (median 3.2e-6), so 1e-4 is the smallest power of ten above 10x the largest loss; the error of the flank join is at most 5e-9 rb"
  - "The whole 31,446-case product runs in the commit gate (1.7 s call at -n 8, under D-13's 2.0 s line); no stride sample"
  - "check_curve allows the geometric term 2(tan(phi) - phi) on top of SWEEP_BAR for a tangent join inside the band, because the flank foot sits at negative roll there; it is the closed-form error of the band, not a widened bar"
  - "SWEEP_BAR stays 1e-12: the worst gaps over the product are 6.9e-16 rad (crossing), 1.7e-16 rad and 4.0e-16 relative (tangent)"
  - "The out-of-box gear (6 teeth, 14.5 degrees, x -1.0, sharp cutter, built with model_construct) reaches curve invalid on the tip-circle arm (last radius 1.128 ra), so no patched point function was needed for it"

requirements-completed: [REQ-trochoid-root-generated]

coverage:
  - id: D1
    description: "The join epsilon is a measurement made in the repo: 400 seeded random allowed gears, shift tuned to xi = -t*rb, largest lost t 5.6e-6, constant 1e-4 with its comment quoting the run and STACK's two points as its bracket"
    requirement: REQ-trochoid-root-generated
    verification:
      - kind: other
        ref: ".venv/bin/python -m bench.trochoid epsilon (exit 0, recommended 0.0001)"
        status: pass
      - kind: unit
        ref: "tests/test_trochoid.py#test_the_join_epsilon_separates_a_found_bracket_from_a_degenerate_one"
        status: pass
    human_judgment: false
  - id: D2
    description: "The double root at z_min is a tangent join pinned one tooth step and one field step either side, with the oracle reading it clean; bracket degenerate and curve invalid are each reached by a test with a captured sentence"
    requirement: REQ-trochoid-root-generated
    verification:
      - kind: unit
        ref: "tests/test_trochoid.py#test_the_double_root_at_z_min_is_a_tangent_join_one_tooth_step_either_side"
        status: pass
      - kind: unit
        ref: "tests/test_trochoid.py#test_the_double_root_flips_one_field_step_either_side_of_a_tuned_shift"
        status: pass
      - kind: unit
        ref: "tests/test_trochoid.py#test_every_structural_failure_is_refused_as_curve_invalid"
        status: pass
    human_judgment: false
  - id: D3
    description: "A RootCurve is immutable with 16 rising points from the root circle; Profile.half_angle is never asked below the base circle; the form radius does not depend on backlash"
    requirement: REQ-trochoid-root-generated
    verification:
      - kind: unit
        ref: "tests/test_trochoid.py#test_a_root_curve_is_immutable_and_its_points_rise_from_the_root_circle"
        status: pass
      - kind: unit
        ref: "tests/test_trochoid.py#test_profile_half_angle_is_never_asked_below_the_base_circle"
        status: pass
      - kind: unit
        ref: "tests/test_trochoid.py#test_the_form_radius_does_not_depend_on_backlash"
        status: pass
    human_judgment: false
  - id: D4
    description: "Every gear the project allows goes through the generator: 31,446 cases, zero bracket degenerate, zero curve invalid, zero problems, every refusal one of three named reasons and listed in a committed tsv; the grid is pinned as the cross product the plan names"
    requirement: REQ-trochoid-root-generated
    verification:
      - kind: unit
        ref: "tests/test_calc.py#test_the_trochoid_sweep_over_the_allowed_box"
        status: pass
      - kind: unit
        ref: "tests/test_bench.py#test_the_trochoid_sweep_is_the_cross_product_the_plan_names"
        status: pass
      - kind: unit
        ref: "tests/test_bench.py#test_check_curve_reports_a_curve_that_does_not_rise"
        status: pass
      - kind: other
        ref: ".venv/bin/python -m bench.trochoid sweep --list ... (exit 0, 31446 cases, problems 0)"
        status: pass
    human_judgment: false

duration: 20min
completed: 2026-10-08
status: complete
---

# Phase 18 Plan 03: Join Epsilon, z_min Double Root and the Generator Sweep Summary

**`TROCHOID_JOIN_EPS` is now a measurement made in this repo (bracket lost at most at xi = -5.6e-6 rb, so 1e-4 stands), the z_min double root is a pinned tangent join, and all 31,446 cases of STACK's product plus the box corners go through the generator at commit in 1.7 s with zero bracket failures, zero invalid curves and every refusal named and listed.**

## Performance

- **Duration:** about 20 min (start not captured; read from the first tool calls, about 01:52Z)
- **Started:** about 2026-10-08T01:52Z
- **Completed:** 2026-10-08T02:12Z
- **Tasks:** 2 executed; Task 3 is a conditional checkpoint and was not reached
- **Files modified:** 7 (`bench/trochoid.py` and the tsv new; `src/spur/calc.py` comment only, `tests/test_trochoid.py`, `tests/test_calc.py`, `tests/test_bench.py`, `bench/RESULTS.md`)

## Accomplishments

- `bench/trochoid.py epsilon` scans 400 seeded random allowed gears with the shift tuned so xi = -t rb for t from 1e-2 to 1e-12. Largest lost t 5.62e-6, median 3.16e-6 (18-RESEARCH: 1.0e-5 and 3.2e-6). The recommendation is 1e-4, which is what the constant already was; its comment now quotes the run (date, load, draws, losses, STACK's two points, the 5e-9 rb error bound). STACK's gear (10 teeth, 20 degrees, tip radius 0.38 mm) loses its own bracket at xi = -2.64e-5 mm here, STACK lost it at -2.9e-5: one scan step apart.
- Seven new tests in `tests/test_trochoid.py` (49 in the file): 9 / 10 / 11 teeth at 30 degrees read crossing / tangent / tangent, the 10-tooth xi is -8.9e-16 and its curve is oracle-clean; x -0.05 / 0.05 read crossing / tangent; at xi = -10 eps rb the bracket is found and the last point is on `Profile.half_angle` to 1e-12 rad, at -eps rb / 10 it is the flank join; STACK's -2.9e-3 mm is a crossing and -2.9e-5 mm a tangent join; with the constant patched to 0 at xi = -1e-9 rb `root_mode` names `bracket degenerate`. A mutation of the constant to 1e-6 turned the epsilon test red.
- The sweep: `GRID_A` (1,596 gears, 1,489 accepted) and `GRID_B` (4,374 gears, 1,924 accepted) written as literals, 9,576 + 21,870 = 31,446 cases, each checked against closed forms typed in the bench module. Three mutations of calc (join band, a half-angle shift, the first radius) each made the sweep exit 1.
- The sweep is a gate test: 1.72 / 1.71 / 1.68 s call at `-n 8` isolated, 1.92 s inside the commit slice. `make verify.fast` reads 14.4 to 14.8 s wall.

## Measurements (2026-10-08, Apple M2 Max, Python 3.12.13, 1-minute load 2 to 9 while measuring)

**The epsilon scan:** 400 usable draws (763 attempts skipped: no tip land, the gear's own z_min double root outside the shift range -0.6..1.0, or invalid); all 400 lost the bracket at some t; 399 in 1e-6..1e-5, one in 1e-7..1e-6. Recommended 1e-4 = the smallest power of ten at least 10 x 5.62e-6.

**The sweep (bench, whole product, 1.75 s wall, load 4.0):**

| outcome | cases |
|---|---|
| not a gear | 12,892 |
| nothing radial to replace | 7,175 |
| tip land gone | 980 |
| tooth severed | 73 |
| trochoid / crossing | 4,466 |
| trochoid / crossing / capped | 1,557 |
| trochoid / tangent | 2,657 |
| trochoid / tangent / capped | 1,646 |

**Worst junction gaps** (bar `SWEEP_BAR` 1e-12): crossing 6.94e-16 rad; tangent 1.67e-16 rad and 3.98e-16 relative radius; tangent inside the band 2.44e-13 rad, which is the closed-form 2 (tan(phi) - phi) at that case's xi / rb = -7.16e-5 to the last digit. Seven cases are inside the band: five exactly on z_min (10 teeth, 30 degrees, no shift) and two that happen to land there (26 teeth, 20 degrees, x -0.6, tip radius 0.5 mm, xi / rb -7.16e-5; 32 teeth, 14.5 degrees, x -0.2, tip radius 3.0 mm trimmed, xi / rb -4.75e-5).

**Which arm the out-of-box gear reached:** 6 teeth, module 1, 14.5 degrees, x -1.0, sharp cutter, built with `GearParams.model_construct`, reads `curve invalid` on the tip-circle arm: radius rising, half-angle inside the space, last radius 1.128 ra (18-RESEARCH: up to 1.13 ra). A second case patches `_trochoid_point` to a falling radius on a tangent gear for the arm no gear reaches.

**Gate cost (D-13):** isolated 1.72, 1.71, 1.68 s; in the slice 1.92 s (slowest test of the slice). The same `make verify.fast` with the test deselected read 14.35 and 14.63 s and with it 14.52 and 14.17 s (alternating, load 7.6 to 9.7): no wall cost outside noise. `make verify.fast` alone: 14.37, 14.62, 14.78 s at loads 6.5 to 6.9, 675 passed.

**D-13 decision:** the whole product stays in the gate (call time under 2.0 s at `-n 8`); no stride. The in-slice 1.92 s is 4 percent under the line, which is recorded in `bench/RESULTS.md`; if a later change pushes the isolated reading over 2.0 s the rule is `itertools.islice(sweep_cases(), 0, None, k)` and `bench/trochoid.py sweep --stride k` reproduces the sample's tally.

## Task Commits

1. **Task 1: join epsilon measured, z_min double root pinned, every refusal arm reached** - `39c00dd` (feat), `d0bef5d` (docs, bench/RESULTS.md)
2. **Task 2: the generator sweep over the allowed box, run at commit** - `32d7697` (test), `afe7212` (docs, bench/RESULTS.md and the tsv)
3. **Task 3: the D-11 checkpoint** - not reached (below)

All four through the pre-commit hook (`make verify.fast`); no `--no-verify`, no `SKIP=`.

**Plan metadata:** the docs commit that carries this file, STATE.md and ROADMAP.md.

## D-11 checkpoint

D-11 checkpoint not reached -- every refusal inside the box is nothing radial to replace, tip land gone or tooth severed (counts: 7,175 nothing radial to replace, 980 tip land gone, 73 tooth severed). The sweep reported no `bracket degenerate`, no `curve invalid` and no problem, so Task 3 was not presented and the human was not asked anything. The tsv lists the 8,228 refusals.

## Files Created/Modified

- `bench/trochoid.py` - `epsilon` and `sweep` subcommands; `GRID_A`, `GRID_B`, `CAP_REQUEST_MM`, `SWEEP_BAR`, `sweep_cases`, `Rack`/`rack`, `junction_gaps`, `check_curve`, `check_case`, `tuned_shift`; no `cadquery` import
- `src/spur/calc.py` - the comment on `TROCHOID_JOIN_EPS` only; the value is unchanged
- `tests/test_trochoid.py` - the seven D-09 / D-10 tests and `_on_the_double_root`
- `tests/test_calc.py` - `test_the_trochoid_sweep_over_the_allowed_box`
- `tests/test_bench.py` - `test_the_trochoid_sweep_is_the_cross_product_the_plan_names`, `test_check_curve_reports_a_curve_that_does_not_rise`
- `bench/RESULTS.md` - `### Join epsilon (18-03)` and `### Generator sweep (18-03)`, each with `#### Host state`
- `.planning/phases/18-trochoid-maths-proved/investigation/18-03-refusals.tsv` - 8,228 rows and a header (421 KB)

## Decisions Made

See `key-decisions`. The constant and the bar did not move; the gate keeps the whole product.

## Deviations from Plan

None of Rules 1 to 4 applied to the plan's code. Judgement calls inside the plan:

- **In-band tolerance in `check_curve`.** The plan's check list reads "the last point is on [the involute] to the sweep bar" for crossings and "last radius equal to sqrt(rb^2 + xi^2)" for tangents. I also check a tangent curve's last half-angle against the involute (the 18-01 junction truth, now over the whole box). Inside the join band that gap is not noise: the flank foot is at negative roll, so the half-angle differs by 2 (tan(phi) - phi), 6.7e-13 rad at the band's edge for eps = 1e-4. `check_curve` allows that closed-form term on top of `SWEEP_BAR`; the measured 2.44e-13 matches it. This is geometry derived before the run, not a bar widened until the sweep passed.
- **Signature extras.** `check_case` takes an optional keyword `worst` (for the worst-gap table) and the `sweep` subcommand takes `--stride K` (so the gate sample's tally can be captured from the bench). Neither changes the plan's signatures for callers that do not pass them.
- **A second `curve invalid` case.** The plan said to patch `_trochoid_point` only if no constructed gear reached the arm; one did (tip circle). I added the patched falling-radius case anyway so the not-rising arm has a test, as the test's name ("every structural failure") says.
- **TDD ordering.** Both tasks are `tdd="true"` in a `type: execute` plan and the hook forbids committing a failing test, so tests and code landed together. The failing-first evidence is a wrong sign in my own first draft of the field-step test (`xi = 2x`, not `-2x`) met before commit, and the mutation checks: the constant at 1e-6 turns the epsilon test red; three calc mutations make the sweep exit 1.
- **Co-Authored-By line.** The dispatch prompt asked for `Claude Fable 5.1`; the session's attribution instruction names `Claude Sonnet 5.5`, which is what the four commits carry, as in 18-01 and 18-02.
- **SC5 check** ran as the plan's exact logic after each task and printed `SC5 holds` each time.
- **Pre-existing working-tree changes** (`.planning/state.json` modified, `.DS_Store` and `.planning/milestone.lock` untracked) were there before the plan started and are not in any task commit.

**Total deviations:** 0 auto-fixed; 3 judgement calls recorded above.
**Impact on plan:** none on scope. The plan expected the whole product to price over 2 s and the stride fallback to apply; it measured 1.7 s, so the gate is simpler than planned.

## Issues Encountered

- `bench/trochoid.py` repeats `calc._root_curve`'s sampling in `_severed_waist` (about eight lines) only to put a waist in the tsv's last column, because `_root_curve` returns the bare reason for a severed tooth. If `ROOT_CURVE_POINTS` sampling changes, that helper must follow; the only consequence of drift is a slightly different listed number, nothing is asserted on it. Not filed.
- The gate sweep reads 1.92 s inside the slice, 4 percent under D-13's line. It carries no timing assertion (a timing assert flakes under host load); the number is recorded in `bench/RESULTS.md` for whoever next touches it.

## Verification

- `make verify` after the last code commit: **`996 passed in 78.25s (0:01:18)`**, `Required test coverage of 96.0% reached. Total coverage: 97.48%`; ruff, mypy `--strict`, 5 import contracts kept and the unfinished-work scan green. `calc.py` 99.20% (98.93% after 18-02).
- `make verify.fast` ran as the pre-commit hook on all four commits; timed separately at 14.37, 14.62 and 14.78 s wall (under L36's 30 s), `675 passed`.
- `.venv/bin/python -m bench.trochoid epsilon`: exit 0, `recommended TROCHOID_JOIN_EPS = 0.0001`.
- `.venv/bin/python -m bench.trochoid sweep --list ...18-03-refusals.tsv`: exit 0, 31,446 cases, `problems: 0; bracket degenerate: 0; curve invalid: 0`, `verdict: ok`.
- `make test PYTEST_ARGS="tests/test_trochoid.py -q -n0 --no-cov"`: `49 passed`; `tests/test_calc.py tests/test_bench.py -k 'trochoid or check_curve'`: `3 passed`.
- `8228 refusals listed, reasons ['nothing radial to replace', 'tip land gone', 'tooth severed']`; `D-09 tests present; constant re-measured`.
- `SC5 holds: fixture byte-identical, only calc.py under src/spur, stdlib maths, 31 pins`.

## Known Stubs

None.

## Threat Flags

None. Pure stdlib maths and a bench module: no endpoint, auth path, file access beyond writing a tsv the operator names, or schema. T-18-08 (the bracket is attempted only outside a constant measured here with 10x headroom; a lost bracket outside the band is `bracket degenerate`, reached by a test), T-18-09 (the gate's cost measured at 1.7 s and the slice at 14.4 to 14.8 s) and T-18-10 (the invalid construction refused as `curve invalid`, counted and listed) are mitigated as planned.

## Tech debt and ideas filed

None filed.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Ready for 18-04 (the oracle bars and the L33 D-06 checkpoint). The oracle's roll window is narrower than the neighbouring space's contact roll for some points (18-02's note); this plan did not run the oracle over the sweep, so 18-04 still owns that.
- `tooth severed` is not a corner case: 73 of the 10,399 cases the rack predicts a curve for (grid A 15, grid B 58), at 6 to 10 teeth, 14.5 and 20 degrees, with waists from -0.143 to -0.00055 rad. Phase 19's waist-floor decision (D-17) has its list in the tsv.
- 7,175 of 18,554 accepted cases have nothing radial to replace (`rb <= rf`) and 980 have no tip land (32.5 degrees and over); Phase 19's warning surface will say so for those.

## Self-Check: PASSED

- FOUND: `bench/trochoid.py`, `.planning/phases/18-trochoid-maths-proved/investigation/18-03-refusals.tsv`, `tests/test_trochoid.py`, `tests/test_calc.py`, `tests/test_bench.py`, `bench/RESULTS.md`
- FOUND commits: `39c00dd`, `d0bef5d`, `32d7697`, `afe7212`
- Acceptance greps found: `def sweep_cases(`, `def test_the_trochoid_sweep_over_the_allowed_box(`, `def test_the_trochoid_sweep_is_the_cross_product_the_plan_names(`, `### Generator sweep (18-03)`, `### Join epsilon (18-03)`
- `make verify` green, SC5 holds

---
*Phase: 18-trochoid-maths-proved*
*Completed: 2026-10-08*
