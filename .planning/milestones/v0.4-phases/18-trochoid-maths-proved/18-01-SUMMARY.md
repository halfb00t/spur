---
phase: 18-trochoid-maths-proved
plan: 01
subsystem: gear-maths
tags: [trochoid, hob-cutter, involute, swept-cutter-oracle, stdlib-math, calc]

requires:
  - phase: 17-debt-first-commit-gate-and-pool-race
    provides: the commit gate (verify.fast at pre-commit, L36) every commit here ran under
provides:
  - "calc.cutter(p, rho): the basic rack defined once, tip radius capped from the real cutter (backlash included) and floored to 3 dp"
  - "calc.trochoid_root(c): an immutable RootCurve of 16 (radius, half-angle) points, the envelope of the tip arc in contact-normal angle, tangent or crossing junction"
  - "calc.root_mode / calc.root_warnings: the single predicate (happy path, tip land gone, bracket degenerate, curve invalid) and the one source of its sentences"
  - "tests/trochoid_oracle.py: the swept-cutter clearance oracle with neighbouring teeth, sharing no code with spur"
  - "bench/RESULTS.md Trochoid maths (Phase 18) / Cutter cap and junction (18-01)"
affects: [18-02, 18-03, 18-04, 18-05, 19]

actuals:
  tokens: 11625   # chars/4 over the added lines of src, tests and bench (46,503 chars)
  tasks: 2
  commits: 4      # MEASURED: git rev-list --count 26b9505..7c350ad
plan_head_before: 26b950529a42a630c94cff28518b29f881e28f9c
plan_head_after: 7c350ad98378488eeb27d90f5eae0d09ef40476c
commits: 4

tech-stack:
  added: []
  patterns:
    - "one definition per rack expression (_dedendum, _pitch_thickness) read by both profile() and cutter()"
    - "closed-form sign test before any bisection; sign-only 60-halving bisection, never Newton"
    - "a refused case is None plus a named reason, never a clipped or healed curve"
    - "tolerances written beside the two measured numbers that set them, headroom stated"

key-files:
  created:
    - tests/trochoid_oracle.py
    - tests/test_trochoid.py
  modified:
    - src/spur/calc.py
    - bench/RESULTS.md

key-decisions:
  - "Cap floored to 3 dp, not rounded (F3): the used and the printed tip radius are one float and the tip land stays >= 0"
  - "Tip-land refusal decided on the sharp-corner land a0 < 0, never on a pressure-angle constant (F2): 32.14 degrees at backlash 0, 33.07 at the default gear"
  - "Junction bars JUNCTION_BAR_RAD and JUNCTION_BAR_MM at the 1e-12 cross-platform floor (headroom 2.4e4 and 562); DIRECTION_BAR_RAD 1e-5 rad (headroom 72)"
  - "root_mode keeps `pr` in its signature (D-04) and carries one specific noqa ARG001 until 18-02's rb <= rf check reads it"
  - "_ROOT_SENTENCES holds the cap sentence under the key `rho capped` so root_warnings has no branch per sentence"
  - "root_mode's default rho = 0.0 (D-16 left it to the plan): the legal sharp cutter, ignored whenever nothing is requested"

requirements-completed: [REQ-cutter-defined-once, REQ-trochoid-root-generated, REQ-trochoid-proved-independently]

coverage:
  - id: D1
    description: "The cutter is defined once from profile()'s own expressions; rho is an explicit mm argument, capped from the real cutter with backlash included, floored to 3 dp and warned; no curve where the rack has no tip land"
    requirement: REQ-cutter-defined-once
    verification:
      - kind: unit
        ref: "tests/test_trochoid.py#test_the_cap_formula_reconciles_0_318_m_and_0_363_m_as_one_cap_at_two_backlashes"
        status: pass
      - kind: unit
        ref: "tests/test_trochoid.py#test_the_cap_is_floored_and_warned_one_print_step_either_side"
        status: pass
      - kind: unit
        ref: "tests/test_trochoid.py#test_the_tip_land_limit_moves_with_backlash_and_module_one_field_step_either_side"
        status: pass
      - kind: unit
        ref: "tests/test_trochoid.py#test_the_cutter_reads_the_root_circle_from_the_same_expression_as_profile"
        status: pass
      - kind: unit
        ref: "tests/test_trochoid.py#test_a_sharp_cutter_and_a_corner_centre_on_the_rolling_line_are_both_legal"
        status: pass
    human_judgment: false
  - id: D2
    description: "trochoid_root generates the envelope of the tip arc in contact-normal angle as an immutable RootCurve; the tangent junction equals Profile.half_angle at backlash 0 and 0.10 to a re-measured bar; a crossing is found by a closed-form sign test then two bisections"
    requirement: REQ-trochoid-root-generated
    verification:
      - kind: unit
        ref: "tests/test_trochoid.py#test_the_tracer_gear_is_cut_by_its_cutter_and_nothing_else"
        status: pass
      - kind: unit
        ref: "tests/test_trochoid.py#test_the_tangent_junction_equals_the_involute_at_backlash_0_and_0_10"
        status: pass
      - kind: unit
        ref: "tests/test_trochoid.py#test_a_cutter_without_backlash_misses_the_involute_and_a_crossing_is_not_tangent"
        status: pass
      - kind: unit
        ref: "tests/test_trochoid.py#test_a_curve_that_cannot_be_trusted_is_refused_with_a_reason_and_no_points"
        status: pass
    human_judgment: false
  - id: D3
    description: "An independent swept-cutter oracle with neighbouring cutter teeth reads the tracer curve as the cut boundary to 1e-9 mm and reads an involute gouge"
    requirement: REQ-trochoid-proved-independently
    verification:
      - kind: unit
        ref: "tests/test_trochoid.py#test_the_tracer_gear_is_cut_by_its_cutter_and_nothing_else"
        status: pass
    human_judgment: false
  - id: D4
    description: "root_mode answers for a gear and root_warnings is the one source of its sentences; nothing requested leaves the root radial and silent"
    verification:
      - kind: unit
        ref: "tests/test_trochoid.py#test_nothing_requested_leaves_the_root_radial_and_silent"
        status: pass
      - kind: unit
        ref: "tests/test_trochoid.py#test_the_tip_land_limit_moves_with_backlash_and_module_one_field_step_either_side"
        status: pass
    human_judgment: false

duration: 19min
completed: 2026-10-08
status: complete
---

# Phase 18 Plan 01: Cutter, Generator and Oracle Summary

**The hob's trochoid exists for one gear end to end: a rack defined once from `profile()`'s own expressions, its tip radius capped from the real cutter (backlash in, floored to 3 dp), the envelope generated in contact-normal angle with a closed-form junction test before any bisection, and a stdlib swept-cutter oracle with neighbouring teeth reading the curve at 1.0e-15 mm.**

## Performance

- **Duration:** 19 min
- **Started:** ~2026-10-08T01:14Z (not captured at start; read from STATE's `last_updated` and the first tool call)
- **Completed:** 2026-10-08T01:33Z
- **Tasks:** 2 (a tracer and a TDD task)
- **Files modified:** 4 (`src/spur/calc.py`, `tests/trochoid_oracle.py`, `tests/test_trochoid.py`, `bench/RESULTS.md`)

## Accomplishments

- `_dedendum` and `_pitch_thickness` are the one definition `profile()` and `cutter()` read; `c.pr == profile(p)`, `c.pr.r - c.d == c.pr.rf` and `points[0][0] == c.pr.rf` hold with `==`, and the pre-v0.2 fixture replay is byte-identical at every commit.
- The tracer gear (10 teeth, module 1, 20 degrees, tip radius 0.38 mm) reads trochoid, join `crossing`, 16 points, first point exactly `(rf, pi/10 - a/r)`, last radius 4.725602 mm. **Worst oracle reading 9.99e-16 mm; the involute control (halfway between the base circle and the crossing radius) reads -3.695e-03 mm**, so the oracle can see a gouge.
- The cap reconciliation is the phase's first test: `rho_max` 0.63478 mm = 0.36273 m (backlash 0.10) and 0.55629 mm = 0.31788 m (backlash 0) at module 1.75, 25 degrees; 0.47191 mm at module 1, 20 degrees; independent of profile shift.
- The cap is floored: at module 0.5, 15 degrees, 12 teeth, backlash 0 (cap 0.2935265) 0.293 is used unchanged and silent, 0.294 is cut to 0.293 with the cap sentence naming `0.293 mm`, the exact cap is not trimmed; `round(cap, 3)` would have left a tip land of -3.6e-4 mm.
- The tip-land limit is pinned one pressure-angle field step either side at backlash 0 (32.0 land, 32.5 none) and at the default backlash and module (33.0 land, 33.5 none); without a land `trochoid_root` is None and `root_mode` names `tip land gone`.
- rho 0, `w_c == 0.0` (16 teeth, 14.5 degrees, x 1.0, rho 0.25), `w_c > 0` (rho 0.5) and rho exactly at the unrounded cap (land of zero, first half-angle pi/z to 1e-15) all generate curves the oracle reads within 1e-9 mm.
- The tangent junction equals `Profile.half_angle` and `sqrt(rb^2 + xi^2)` at backlash 0 and 0.10 to measured bars with stated headroom, and both tripwires were seen red.

## Measured bars (re-measured in this plan, 2026-10-08, Apple M2 Max, 1-minute load 1.9 to 3.4)

| Bar | Value | Largest measured | Headroom |
|---|---|---|---|
| `ORACLE_BAR_MM` | 1e-9 mm | 9.99e-16 mm (tracer); 18-RESEARCH noise floor 6.7e-15 * m | 1.0e6 on the tracer, >= 1.5e4 at module <= 10 |
| `JUNCTION_BAR_RAD` | 1e-12 rad | 4.16e-17 rad | 2.4e4 |
| `JUNCTION_BAR_MM` | 1e-12 mm | 1.78e-15 mm (one ulp at R 15.3 mm) | 562 |
| `DIRECTION_BAR_RAD` | 1e-5 rad | 1.38e-7 rad (the chord's own error, 1.39 * step) | 72 |

Tripwires (both seen red):

- A cutter built with backlash 0 for the backlash-0.10 default gear ends 3.008e-3 rad = 0.0460 mm from that gear's involute (PITFALLS 3's 0.046 mm): 3.0e9 times the junction bar. Mutation check: with `cutter()` ignoring backlash the junction test fails on both backlash-0.10 rows and passes on both backlash-0 rows, and the reconciliation test fails on the backlash-0.10 row.
- The crossing row (17 teeth, 20 degrees, rho 0.38, join `crossing`) reads a direction angle of 4.13e-3 rad: 413 times the direction bar, so tangency is asserted only for z >= z_min.
- Two more mutations went red as intended: `round(rho_max, 3)` instead of the floor fails the floored-cap test; a tip-land decision on a constant 32.1 degrees fails the 33.0 degree default-gear row.

**No headroom is under 10x**, so nothing goes to the human here; 18-04 Task 3 (the L33 D-06 checkpoint) collects these four bars again.

## Captured sentences (from `root_warnings`, 2026-10-08, never typed)

- Cap: "Cutter tip radius reduced to 0.293 mm, the largest that leaves the cutter a tip land at this pressure angle and backlash."
- Tip land gone, 32.5 degrees: "The cutter has no tip land at a 32.5 degree pressure angle with this module and backlash: no trochoid root is computed and the analytic root is used." (33.5 degrees reads the same with `33.5`.)

## Task Commits

1. **Task 1: Tracer, one undercut gear end to end** - `15174f9` (feat)
2. **Task 2: The cutter defined once, cap and junction pinned** - `8e75273` (feat), `e2c123f` (docs, bench/RESULTS.md alone)
3. **Docstring correction found while recording the RESULTS figures** - `7c350ad` (docs, see deviations)

All four committed through `gsd-tools query commit` with the pre-commit hook running (`make verify.fast`); no `--no-verify`, no `SKIP=`, and no `commit_timeout` so D-07's recovery was never needed.

## Files Created/Modified

- `src/spur/calc.py` - `_dedendum`, `_pitch_thickness`, `ROOT_CURVE_POINTS`, `TROCHOID_JOIN_EPS`, `RootShape`, `RootReason`, `Cutter`, `cutter`, `RootCurve`, `_trochoid_point`, `_bisect`, `_junction`, `_root_curve`, `trochoid_root`, `RootMode`, `root_mode`, `_ROOT_SENTENCES`, `root_warnings`; `profile()` now reads the two shared expressions with the same operands in the same order
- `tests/trochoid_oracle.py` - `clearance(...)` and `_polygon_distance`, stdlib `math` only, imports nothing from `spur`
- `tests/test_trochoid.py` - 19 test cases in 10 test functions; the reconciliation is the first
- `bench/RESULTS.md` - `## Trochoid maths (Phase 18)` and `### Cutter cap and junction (18-01)` with host state, the reconciliation, the floored cap, the tip-land rows and the junction table

## Decisions Made

See `key-decisions` above. In short: floor the cap; decide the tip land on `a0`; the junction bars sit at the 1e-12 floor because 10x the measured gaps (1e-15, 1e-14) is below what libm differences between macOS and Linux could move; the direction bar is the smallest power of ten at or above 10x the largest reading.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Wrong figure in my own docstring**
- **Found during:** Task 2, while writing the RESULTS.md cap table
- **Issue:** `test_the_cap_is_floored_and_warned_one_print_step_either_side` said the rounded cap leaves a tip land of -4.0e-4 mm; the closed form reads -3.63e-4 mm (18-RESEARCH: -3.6e-4)
- **Fix:** corrected the docstring figure
- **Files modified:** `tests/test_trochoid.py`
- **Verification:** `make verify.fast` at the commit; the assertion itself (`_tip_land(p, 0.294) < 0`) was never wrong
- **Committed in:** `7c350ad`, a fourth commit the plan did not list, because `bench/RESULTS.md` was to be committed alone

### Judgement calls inside the plan (not rule deviations)

- **TDD ordering.** Task 2 is `tdd="true"`, but the hook forbids committing a failing test and the cutter, the cap and the junction were already implemented by Task 1, so those tests were green on first run (characterisation tests, not RED). The red evidence is the mutation checks above, each of which turned the matching test red before the real code was restored. `root_warnings` was written after the tests that need it were drafted; there is no separate RED commit. The `type: tdd` gate sequence does not apply (the plan is `type: execute`).
- **Extra tests.** Added `test_nothing_requested_leaves_the_root_radial_and_silent` and `test_a_curve_that_cannot_be_trusted_is_refused_with_a_reason_and_no_points` so the `not requested`, `bracket degenerate` and `curve invalid` arms of the new code are reached (the branch floor, Pitfall 5). Both use hand-built `Cutter`s via `dataclasses.replace`; the allowed box never reaches those arms.
- **`root_mode`'s signature spans two lines** with `# noqa: ARG001` on `pr` (ruff's `ARG` is selected and `pr` is unused until 18-02 reads it for `nothing radial to replace`). The plan's acceptance grep for the one-line signature would not match; the signature is otherwise exactly as specified.
- **Co-Authored-By line.** The dispatch prompt asked for `Claude Fable 5.1`; the session's attribution instruction names `Claude Sonnet 5.5`, which is what the four commits carry.
- **SC5 check** was run from a scratch script holding the plan's exact logic (not the inline `python -c`), once after each task and once at the end; it printed `SC5 holds` each time.

---

**Total deviations:** 1 auto-fixed (1 Rule 1 documentation figure)
**Impact on plan:** None on scope. One extra commit and two extra tests.

## Issues Encountered

None. A first `make verify.fast` failed on mypy (`**dict[str, float]` into `clearance`'s typed keywords); the `_swept` helper that reads the fields off the `GearParams` replaced it.

## Verification

- `make verify` after the last commit: **`963 passed in 70.09s (0:01:10)`**, coverage `Required test coverage of 96.0% reached. Total coverage: 97.49%`; ruff, mypy `--strict`, import contracts and the unfinished-work scan green. The new section of `calc.py` is fully covered by `tests/test_trochoid.py` alone (the uncovered lines it reports are all in earlier code).
- `make verify.fast` ran as the pre-commit hook on all four commits (642 passed at the last one).
- `make test PYTEST_ARGS="tests/test_trochoid.py -q -n0 --no-cov"`: `19 passed`.
- `SC5 holds: fixture byte-identical, only calc.py under src/spur, stdlib maths, 31 pins`.
- `oracle independent and committed`; `reconciliation first; 10 tests`; `RESULTS 18-01 subsection present`.

## Known Stubs

None.

## Threat Flags

None. The code is pure stdlib maths with no new endpoint, auth path, file access or schema; T-18-01 to T-18-04 are mitigated as planned (beta stays in `[0, pi/2 - alpha]`, `half_angle` is only called at R >= rb, 60 fixed halvings, the fixture replays at every commit, the oracle reads 1.0e-15 mm and a gouge at -3.7e-3 mm).

## Tech debt and ideas filed

None filed. One item to carry: the `noqa: ARG001` on `root_mode`'s `pr` goes away when 18-02 reads `pr` for `nothing radial to replace`.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Ready for 18-02 (the predicate's refusals: `nothing radial to replace`, `tooth severed`, `waist`, the closed-form onset). The reason contract (`RootReason`) already lists all six values and `_ROOT_SENTENCES` already holds all six sentences; 18-02 only has to produce the two it adds.
- `TROCHOID_JOIN_EPS = 1e-4` is still the research value; 18-03 re-measures it.

## Self-Check: PASSED

- FOUND: `src/spur/calc.py`, `tests/trochoid_oracle.py`, `tests/test_trochoid.py`, `bench/RESULTS.md`
- FOUND commits: `15174f9`, `8e75273`, `e2c123f`, `7c350ad`
- Acceptance greps for every named `calc.py` symbol found (the `root_mode` signature is split over two lines, see above)
- `make verify` green, SC5 holds

---
*Phase: 18-trochoid-maths-proved*
*Completed: 2026-10-08*
