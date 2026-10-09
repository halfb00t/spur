---
phase: 19-the-trochoid-in-the-part
plan: 05
subsystem: geometry
tags: [cadquery, trochoid, hob-root, dead-band, guards, build-error, solid-model-docs]

requires:
  - phase: 19-the-trochoid-in-the-part
    provides: 19-02's adopted bars (ROOT_ARC_MIN, junction, spacing, area, annulus TOL) and 19-04's _trochoid_outline, RootMode.curve and kernel-tier tests
provides:
  - "model.ROOT_ARC_MIN = 2e-6 mm and the short-arc rule: a root arc under it is left out and the two teeth share one Vector (5 side faces per tooth there, 6 elsewhere)"
  - "model._trochoid_teeth / _Tooth: the per-tooth point lists, read by both the outline and the area guard"
  - "model._guard_junction, _guard_spacing, _guard_annulus, _guard_area and ROOT_JUNCTION_BAR_RAD, ROOT_SPACING_RATIO_MAX, ROOT_AREA_REL_MAX, each BuildError naming a modelling defect in spur and root_shape radial as the remedy"
  - "docs/architecture/solid-model/ true for the hob-root outline, the short-arc rule, the guards and the kernel-tier tests"
affects: [19-06, 19-09, 19-10]

# Actuals (#2632): chars/4 over the added lines of src, tests and docs, a1ffd08..8924826.
actuals:
  tokens: 7839
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "float guards before any kernel call, the annulus guard on the splines just made, the area guard on the face: a defect in spur's own outline is refused with its own sentence instead of reaching _build_checked's wrong-remedy relabel"
    - "a constant's comment carries the last failing and first building value, the headroom, the host and the date (the ROOT_CONTACT shape)"

key-files:
  created: []
  modified:
    - src/spur/model.py
    - tests/test_model.py
    - docs/architecture/solid-model/tactics.md
    - docs/architecture/solid-model/implementation.md
    - docs/architecture/solid-model/errors_and_logging.md
    - docs/architecture/solid-model/tests.md

key-decisions:
  - "Every bar and ROOT_ARC_MIN is 19-02's adopted value, copied with its measurement, not re-decided: ROOT_ARC_MIN 2e-6 mm (10.0x the last failing chord), ROOT_JUNCTION_BAR_RAD 1e-11 rad (40.9x; 18-01's 1e-12 not reused), ROOT_SPACING_RATIO_MAX 1000 (75.0x), ROOT_AREA_REL_MAX 5e-2 on the arc-midpoint polygon (13.6x), annulus TOL 1e-6 mm (8.8e6x)"
  - "_gear_blank calls _trochoid_teeth a second time for the area check instead of _outline returning the points: _outline keeps returning a Wire (19-09 swaps the bench for it) and the check reads the same function as the outline; measured 1.4 ms at 41 teeth against a 118 ms build"
  - "The generator source test matches whole identifiers, because the plan-mandated name _guard_junction holds the generator's private _junction as a substring"

patterns-established:
  - "A hand-built defective curve for a guard test moves ONE interior or last point by a known amount and checks its own setup (the spacing test asserts the ratio exceeds the bar before it asserts the refusal)"
  - "A float guard's test patches the kernel's makeSpline to fail if reached, which proves the refusal comes before the kernel"

requirements-completed: [REQ-outline-consumes-root-curve]  # also declared by 19-04; ready-ids answered 1/1 ready

coverage:
  - id: D1
    description: "A gear a user can type (12 teeth, module 1, 20 degrees, root_fillet 3.0, backlash 0.19898413579248878, tip land 1.000e-08 mm) builds through build(p) as one valid solid with 5 x 12 side faces and no kernel exception; the two teeth share one Vector object; below ROOT_ARC_MIN no root arc is made, at or above it every arc is kept (6 x teeth side faces at lands of 1e-5 and 1.5e-6 mm and on the default gear)"
    requirement: REQ-outline-consumes-root-curve
    verification:
      - kind: unit
        ref: "tests/test_model.py#test_a_root_arc_shorter_than_root_arc_min_is_left_out_and_the_teeth_share_a_vertex"
        status: pass
      - kind: unit
        ref: "tests/test_model.py#test_a_hand_built_curve_with_no_tip_land_builds_without_a_root_arc"
        status: pass
      - kind: unit
        ref: "tests/test_model.py#test_a_root_arc_above_root_arc_min_is_kept"
        status: pass
    human_judgment: false
  - id: D2
    description: "Four structural guards on every trochoid outline, none resting on isValid(): junction (1e-11 rad), point spacing (ratio 1000), root splines inside [rf - TOL, ra + TOL], face area against the arc-midpoint polygon (5e-2); each raises BuildError saying modelling defect in spur and root_shape radial, never 'try smaller'; each is reached by its own test and loosening its bar makes its test fail"
    requirement: REQ-outline-consumes-root-curve
    verification:
      - kind: unit
        ref: "tests/test_model.py#test_a_root_curve_that_leaves_the_involute_at_its_junction_is_a_build_error"
        status: pass
      - kind: unit
        ref: "tests/test_model.py#test_root_points_bunched_past_the_spacing_bar_are_a_build_error"
        status: pass
      - kind: unit
        ref: "tests/test_model.py#test_a_root_spline_outside_the_root_to_tip_annulus_is_a_build_error"
        status: pass
      - kind: unit
        ref: "tests/test_model.py#test_an_outline_whose_area_misses_its_polygon_is_a_build_error"
        status: pass
    human_judgment: false
  - id: D3
    description: "No guard fires on an honest curve: the default gear and the seven 19-02 kernel rows build through _build_checked with all four in place; the radial path calls none of them and the pre-v0.2 fixture replays byte-identically (86 regression tests)"
    requirement: REQ-outline-consumes-root-curve
    verification:
      - kind: unit
        ref: "tests/test_model.py#test_no_guard_fires_on_an_honest_curve"
        status: pass
      - kind: unit
        ref: "tests/regression (86 passed); git diff --exit-code tests/regression/pre_v0_2.json clean"
        status: pass
    human_judgment: false
  - id: D4
    description: "docs/architecture/solid-model/ describes the outline the code builds in both root modes: the trochoid branch, the shared junction vector, the short-arc rule, the four guards and their messages, the dead band and the _build_checked relabel as things that bite, and the kernel-tier tests"
    requirement: REQ-outline-consumes-root-curve
    verification:
      - kind: other
        ref: "the plan's docs check (prints 'solid-model docs brought true')"
        status: pass
    human_judgment: true
    rationale: "Whether the prose is true and readable is a reviewer's judgment; the check only proves the named terms are present. Numbers were copied from bench/RESULTS.md and the code, not re-estimated."

duration: "10 min"
completed: 2026-10-09
status: complete
plan_head_before: a1ffd082800885498333ba0320baa1f9d812f9e5
plan_head_after: 89248266a34e23a9a33009871075735f4cd6aba0
commits: 3
---

# Phase 19 Plan 05: Close the root-arc dead band and guard the hob-root outline Summary

**A backlash a user types can no longer put the hob root in the kernel's `makeThreePointArc` dead band (arcs under `ROOT_ARC_MIN` = 2e-6 mm share a vertex instead), and four structural guards (junction, spacing, annulus, area) refuse a broken trochoid outline as "a modelling defect in spur, set root_shape to radial" without resting on `isValid()`.**

## Performance

- **Duration:** about 10 min of wall time (04:11:58Z to 04:22:22Z), of which the one `make verify` is 131 s
- **Started:** 2026-10-09T04:11:58Z
- **Completed:** 2026-10-09T04:22:22Z
- **Tasks:** 3
- **Files modified:** 6 (`src/spur/model.py`, `tests/test_model.py`, four solid-model docs)

## Accomplishments

- **The dead band is closed where a user can reach it.** `ROOT_ARC_MIN = 2e-6` mm with the 19-02 measurement in its comment (raises at every chord 2e-9 to 2.0e-7 mm and at exactly 0, silently drops the arc at 2e-12 and 2e-10 mm, builds from 4.0e-7 mm; 10.0x the last failing chord, 15.8x below the smallest real chord in the product, 3.1644e-5 mm). `_trochoid_teeth` decides the rule for every tooth before any edge is made, so the `Vector` both splines receive is one object.
- **Tuned backlash:** 12 teeth, module 1, 20 degrees, root_fillet 3.0, backlash found by 40 halvings over [0, 0.4] = **0.19898413579248878** (the same value 19-02's bench found), tip radius used 0.614 mm, **tip land 1.000e-08 mm**, chord about 2e-8 mm. Before the change `build(p)` raised `GC_MakeArcOfCircle::Value() - no result` (seen as the RED run); now it builds one valid solid with **62 faces = 5 x 12 + 2**. Lands of 1e-5 mm, 1.5e-6 mm (chord 3e-6, just over the constant) and the natural 0.38 mm tip radius keep every arc: 74 faces.
- **Four guards, bars as adopted at 19-02.** `_guard_junction` (`ROOT_JUNCTION_BAR_RAD` 1e-11 rad) and `_guard_spacing` (`ROOT_SPACING_RATIO_MAX` 1000) run on floats before any kernel call; `_guard_annulus` reads 81 positions of tooth 0's two root splines as soon as they are made, against `[rf - TOL, ra + TOL]`; `_guard_area` runs in `_gear_blank` on the face, against the shoelace area of the polygon through the outline's own points with each arc taken through its midpoint (`ROOT_AREA_REL_MAX` 5e-2). Readings on the default hob-root gear: junction gap 1.4e-17 rad, spacing ratio 1.399, area miss 9.8e-5.
- **Each guard is reached by a test and the tests have teeth.** The junction and spacing tests patch `cq.Edge.makeSpline` to fail if the kernel is reached, so they prove the refusal comes first; the spacing test asserts its own setup exceeds the bar. A mutation check (bars loosened to 1.0 rad, 1e12 and an annulus of +-1 mm, run once, then reverted) made all three of those tests fail. The area guard is reached on a real gear with its bar patched to 0. `test_no_guard_fires_on_an_honest_curve` builds the default gear and the seven kernel rows through `_build_checked`.
- **Docs.** `tactics.md`, `implementation.md`, `errors_and_logging.md` and `tests.md` now describe both `_outline` branches, the short-arc rule, the guards and their verbatim messages, the dead band and the `_build_checked` relabel as things that bite, and each hob-root test with what it proves. The stale test count in `tests.md` ("13 tests") is now 235 collected.

## Task Commits

1. **Task 1: close the root-arc dead band** - `4b2b03a` (fix)
2. **Task 2: the four structural guards** - `356682b` (feat)
3. **Task 3: solid-model docs** - `8924826` (docs)

**Plan metadata:** the docs commit that carries this SUMMARY, STATE.md, ROADMAP.md and REQUIREMENTS.md.

`commits: 3` is measured from the ledger: `git rev-list --count a1ffd08..HEAD` read 3 at SUMMARY write.

## Files Created/Modified

- `src/spur/model.py` - `ROOT_ARC_MIN` and the three bars with their comments, `_Tooth`, `_trochoid_teeth`, `_trochoid_polygon`, the four `_guard_*`, `_trochoid_outline` calling them, `_gear_blank` running the area guard. The radial `_outline` body is untouched.
- `tests/test_model.py` - three short-arc tests, five guard tests (one parametrized over 8 gears), `_tuned_backlash`, and the generator source test matching whole identifiers.
- `docs/architecture/solid-model/{tactics,implementation,errors_and_logging,tests}.md` - see Accomplishments.

## Decisions Made

- Bars and `ROOT_ARC_MIN` are 19-02's adopted values, written beside the measurement each rests on; none was set from what makes a test pass (the plan's integrity prohibition).
- The area check re-calls `_trochoid_teeth` in `_gear_blank` rather than changing `_outline`'s return type: `_outline` stays a `Wire` for 19-09's bench swap, and both callers read one function. Cost measured: 1.4 ms at 41 teeth, module 1, against a 118 ms build (Apple M5 Max, 2026-10-09), recorded in `_gear_blank`'s docstring.
- A guard's `BuildError` is raised by the guard itself, so `_build_checked`'s "try smaller fillets or chamfers" relabel never sees a defect in spur's own outline.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] The 19-04 generator source test flagged `_guard_junction`**
- **Found during:** Task 2 (first run of the generator test after the guards went in)
- **Issue:** `test_the_trochoid_generator_never_enters_the_model_module` matched its names as substrings, and `_guard_junction` (a name the plan mandates, and its AST check requires) holds the generator's private `_junction`.
- **Fix:** `_generator_names_in` now matches each name as a whole identifier (`(?<!\w)` before it); the test's own tripwire gained `spur.calc._junction(c)` -> flagged and `_guard_junction(pr, curve)` -> not flagged. The test still finds every name the generator can appear under.
- **Files modified:** `tests/test_model.py`
- **Verification:** the generator test and the rest of the file pass; `make verify` green.
- **Committed in:** `356682b`

### Plan-literal items that did not apply as written

**2. Backlash search over [0, 0.4], not [0, 1].** The plan says 40 halvings over [0, 1]. `GearParams` refuses this gear above about 0.49 mm of backlash ("Teeth come to a point"), which 19-02's bench already found; the helper uses 0.4 and reproduces 19-02's backlash to every digit.

**3. The "hand-built curve with the first point at pi / z" cannot start from the default curve.** Moving the first point of a real curve by the whole tip land (about 0.1 mm at tip radius 0.38) swings the spline 1.5e-3 mm below the root circle, and the annulus guard, correctly, refuses it (seen when the first draft of two tests failed with that error). The two tests that need a land-free curve start from the tuned gear's curve instead, where the move is the last 1e-8 mm. The "above ROOT_ARC_MIN" test uses real tuned gears (lands of 1e-5 and 1.5e-6 mm) and the default gear, not a hand-built move.

**4. Task 2 (tdd="true") was code-first.** The plan is `type: execute`, so the plan-level gate does not apply. Task 1 had a seen RED (all three tests failing before the code: the missing constant, and the kernel's own `GC_MakeArcOfCircle` exception on the hand-built curve). Task 2's guards were written before their tests; their ability to fail is shown by the mutation check above rather than a RED commit.

**Total deviations:** 1 auto-fixed (Rule 3) and 3 plan-literal items. **Impact on plan:** none on behaviour; the one extra change is in a test file the plan already lists.

## Issues Encountered

- **Gate result:** `make verify` exit 0, **`1069 passed in 131.36s (0:02:11)`**, coverage **97.64 %** (floor 96); ruff, mypy `--strict`, 5 import contracts kept, unfinished-work scan clean. Model.py is 98.17 % with the four lines and four branches it misses all in code this plan did not touch (`_load_malloc_trim`, `_release_arenas`, two radial-outline branches, `_body`). The gate is 131 s against L34's 66 s bar, as 19-04 found (117 to 129 s); the 16 tests this plan added (the guard builds are small) are not the cause and nothing was done about L34 here: 19-09 owns it.
- **No `ReentrantCallError` or other flake appeared**, in the full gate or in the three pre-commit hooks, so the resource-tracker debt item's trigger did not fire and no log was kept.
- **Shared requirement ID.** `REQ-outline-consumes-root-curve` was declared by 19-04 as well; `requirements.ready-ids` (#2388) answered 1/1 ready after this plan's SUMMARY, and it was marked complete.
- **Commit attribution line.** Commits end with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`, the line the session's attribution reminder gives. The dispatch text named `Claude Fable 5.1`; `CLAUDE.md` itself names neither, so the reminder was followed.

## Known Stubs

None. No placeholder values, empty data flows or TODO markers were added.

## Threat Flags

None. T-19-10 (a wire that opens or a spline that swings) is mitigated by the four guards and their tests; T-19-11 (a typed backlash in the kernel's dead band, relabelled with the wrong remedy) by the `ROOT_ARC_MIN` branch and the tuned-backlash test through `build(p)`. No new network, auth or file surface.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- 19-06 can add `root_form_d`, `root_waist` and the restated undercut sentence: `model.py` reads only `root_mode`, `RootMode.curve` and `spline_start`, none of which 19-06 changes.
- 19-09 still owns the gate cost (131 s on this host) and the swap of the bench's `trochoid_outline` for `spur.model._outline(pr, 0.0, curve=...)`; the guards then run in the bench's builds too.
- 19-10 should cite the guard bars and `ROOT_ARC_MIN` from `bench/RESULTS.md` "Bars adopted (19-02)" when it writes L38.
- Files filed: no debt or idea item was filed by this plan.

## Self-Check: PASSED

- Files: `src/spur/model.py`, `tests/test_model.py` and the four `docs/architecture/solid-model/` files exist; `.planning/phases/19-the-trochoid-in-the-part/19-05-SUMMARY.md` written.
- Commits `4b2b03a`, `356682b` and `8924826` are ancestors of HEAD; `git rev-list --count a1ffd08..HEAD` read 3.
- Acceptance: the three `root_arc` tests print `3 passed`; the `ROOT_ARC_MIN 2e-06 with its measurement` line, the `four guards and their bars present` line, the `SC1 holds` line and the `solid-model docs brought true` line all printed; the 86 regression tests passed and `git diff --exit-code tests/regression/pre_v0_2.json` is clean.

---
*Phase: 19-the-trochoid-in-the-part*
*Completed: 2026-10-09*
