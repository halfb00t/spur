---
phase: 18-trochoid-maths-proved
plan: 02
subsystem: gear-maths
tags: [trochoid, root-mode, predicate, tooth-severed, waist, undercut-onset, swept-cutter-oracle, stdlib-math, calc]

requires:
  - phase: 18-trochoid-maths-proved
    provides: "plan 01: cutter(), _root_curve, root_mode/root_warnings with all six sentences, the swept-cutter oracle"
provides:
  - "calc.root_mode owns all six refusals in one fixed order: not requested, nothing radial to replace (rb <= rf), tip land gone, bracket degenerate, curve invalid, tooth severed"
  - "calc._waist and RootCurve.waist: the curve's narrowest point, refined by 60 golden-section steps between the smallest sample's neighbours"
  - "calc.undercut_teeth(c) and calc.undercut_shift(c): the cutter's own closed-form undercut onset and x_min, read from the cutter that cuts"
  - "tests: the 44 fixture records radial when nobody asks, the three undercuts pinned apart, the T1 closed-form tier over 3,657 gears"
affects: [18-03, 18-04, 18-05, 19]

actuals:
  tokens: 7621    # chars/4 over the added lines of src and tests (30,484 chars)
  tasks: 2
  commits: 2      # MEASURED: git rev-list --count 235c2e3..1902d52
plan_head_before: 235c2e3a8ba8693bf5fa6f2b186031c4e023ea2a
plan_head_after: 1902d5214630c6429a8f3bff7edf9e74a8533653
commits: 2

tech-stack:
  added: []
  patterns:
    - "one predicate, one fixed order of named refusals, cheapest first; every sentence from root_warnings"
    - "a fixed-step golden-section refinement (no data-dependent loop) where a coarse sample can miss a dip"
    - "closed forms in the test typed from the textbook rack, never from calc's expressions"
    - "captured tallies and sentences as literals with their capture date"

key-files:
  created: []
  modified:
    - src/spur/calc.py
    - tests/test_trochoid.py
    - tests/trochoid_oracle.py

key-decisions:
  - "rb <= rf is tested in root_mode before the generator runs: undercut implies rb > rf (F9), so the closed-form edge is never hidden behind a generator failure"
  - "A thin positive waist survives; no waist floor is chosen here (D-17, Phase 19's decision)"
  - "undercut_teeth / undercut_shift read c.d, c.rho and c.xi so a trimmed tip radius gives the trimmed cutter's onset (Pitfall 7); the constant 1.25 is not typed again"
  - "The severed-tooth agreement with the oracle is pinned as a sign (gouge on the severed rows, none on the whole one) on the tooth's mirror flank, because the neighbouring-teeth separation 18-RESEARCH described is not reproduced on the committed oracle"
  - "T1's wall time is printed, not asserted: a timing assert flakes under host load (load 5 to 8 while measuring)"

requirements-completed: [REQ-root-mode-single-predicate, REQ-trochoid-proved-independently]

coverage:
  - id: D1
    description: "root_mode is the single answer: six named reasons in one fixed order, nothing radial to replace where rb <= rf, every sentence captured from root_warnings"
    requirement: REQ-root-mode-single-predicate
    verification:
      - kind: unit
        ref: "tests/test_trochoid.py#test_root_mode_hands_back_where_the_involute_reaches_the_root_circle"
        status: pass
      - kind: unit
        ref: "tests/test_trochoid.py#test_root_mode_refuses_where_the_cutter_has_no_tip_land"
        status: pass
      - kind: unit
        ref: "tests/test_trochoid.py#test_a_gear_failing_two_tests_reports_the_first"
        status: pass
    human_judgment: false
  - id: D2
    description: "Nothing requested leaves all 44 pre-v0.2 records radial and silent; the three undercuts nest but are not the same set on the fixture"
    requirement: REQ-root-mode-single-predicate
    verification:
      - kind: unit
        ref: "tests/test_trochoid.py#test_every_pre_v0_2_record_reads_radial_because_nobody_asked"
        status: pass
      - kind: unit
        ref: "tests/test_trochoid.py#test_the_fixture_straddles_the_three_undercuts_without_mixing_them"
        status: pass
    human_judgment: false
  - id: D3
    description: "A tooth the trochoid cuts through is refused as tooth severed on the refined waist, never handed to a caller as a curve; a thin positive waist survives; the oracle reads a gouge exactly on the severed rows"
    requirement: REQ-trochoid-proved-independently
    verification:
      - kind: unit
        ref: "tests/test_trochoid.py#test_a_severed_tooth_is_refused_and_the_oracle_with_neighbours_agrees"
        status: pass
    human_judgment: false
  - id: D4
    description: "The cutter's closed-form undercut onset and x_min reproduce STACK's tables from the cutter that cuts; T1 pins when the root is a crossing; the cutter's undercut is provably not the shipped warning's"
    requirement: REQ-trochoid-proved-independently
    verification:
      - kind: unit
        ref: "tests/test_trochoid.py#test_the_undercut_onset_closed_forms_match_the_published_tables"
        status: pass
      - kind: unit
        ref: "tests/test_trochoid.py#test_the_cutter_s_undercut_is_not_the_shipped_warning_s_undercut"
        status: pass
      - kind: unit
        ref: "tests/test_trochoid.py#test_the_undercut_onset_flips_one_field_step_either_side_of_a_tuned_shift"
        status: pass
      - kind: unit
        ref: "tests/test_trochoid.py#test_t1_the_closed_form_onset_pins_when_the_root_is_a_crossing"
        status: pass
    human_judgment: false

duration: 11min
completed: 2026-10-08
status: complete
---

# Phase 18 Plan 02: The Predicate's Refusals, the Waist and the Onset Summary

**`root_mode` now answers for every gear in one fixed order of six named reasons (adding `nothing radial to replace` where `rb <= rf` and `tooth severed` on a stdlib golden-section-refined waist), and the cutter's own closed-form undercut onset and `x_min` exist, reproduce STACK's tables, and are pinned by a typed-in closed form over 3,657 gears.**

## Performance

- **Duration:** 11 min
- **Started:** 2026-10-08T01:38:06Z
- **Completed:** 2026-10-08T01:49Z
- **Tasks:** 2 (both TDD-flagged, both `type: execute` plan, so no separate RED commits; see judgement calls)
- **Files modified:** 3 (`src/spur/calc.py`, `tests/test_trochoid.py`, `tests/trochoid_oracle.py`)

## Accomplishments

- `root_mode` returns `nothing radial to replace` before the generator runs where `pr.rb <= pr.rf` (D-02), and `tooth severed` where the refined waist is at or below zero (D-17). The `noqa: ARG001` 18-01 left on `pr` is gone because `pr` is now read.
- `RootCurve.waist` is `(radius, half-angle)` at the narrowest point. `_waist` takes the smallest of the 16 samples and refines it by 60 fixed golden-section steps between its neighbours; the result is within 2.3e-10 rad of a 20,001-point scan.
- `undercut_teeth(c)` and `undercut_shift(c)` read `c.d`, `c.rho`, `c.xi`; neither types the rack depth again.
- Ten new tests (plus the test helper `_fixture_gears`), 37 in the file; `make verify` green.

## Measurements (2026-10-08, Apple M2 Max, Python 3.12.13, 1-minute load 5 to 8 while measuring)

**Fixture tallies (44 records, nothing requested):** all 44 read `RootMode("radial", "not requested", None)` with `root_warnings == ()`, with and without `rho=0.38` passed.

**Fixture tallies (trochoid requested):** 28 of 44 have `rb > rf`, 5 are undercut by the shipped line (all five among the 28).

| tip radius | trochoid | nothing radial to replace | tooth severed | cutter undercut (xi < 0) |
|---|---|---|---|---|
| 0 (sharp) | 24 | 16 | 4 | 8 (3 more than the shipped line) |
| each record's own `root_fillet` | 26 | 16 | 2 | 5 (equal to the shipped set, by coincidence) |

The severed records are the 6-tooth, module 1.75, 14.5 degree, backlash 0.10 gears at shift -0.6 and -0.5 that the API and calc tests build. Their `+mate=...` twins are the same gears.

**Severed rows (14.5 degrees, module 1, backlash 0, sharp cutter):**

| row | smallest sample (rad) | refined waist (rad) | waist radius (mm) | verdict | oracle, one flank, on / off (mm) | oracle, mirror flank, on / off (mm) | 18-RESEARCH |
|---|---|---|---|---|---|---|---|
| 6 teeth, x -0.6 | -0.047235 | -0.047395 | 1.8574 | tooth severed | -2.1e-15 / -2.1e-15 | -0.138979 / -0.138979 | gouge 0.141, waist -0.0474 |
| 6 teeth, x -0.5 | -0.005537 | -0.006559 | 1.9365 | tooth severed | -9.4e-16 / -9.4e-16 | -0.020103 / -0.020103 | gouge 0.0201, waist -0.0066 |
| 7 teeth, x -0.6 | +0.002042 | +0.001961 | 2.4031 | trochoid, thin | -4.5e-16 / -4.5e-16 | -4e-16 / +0.009424 | 4e-16 |

The refined waist is below the smallest sample on every row, and it is what flips nothing here but is the difference between -0.005537 and -0.006559 on the second row.

**T1 (SC3), grid of 4,200 combinations:** 3,657 valid gears, 543 refused by `GearParams` and skipped, 8 valid without a curve, 1,318 crossings, 2,331 tangents, of which 2 sit inside the junction band (undercut by the closed form, joined tangent by D-09). Wall time 0.22 s to 0.23 s over three runs.

**STACK's tables, reproduced:** onset 30.7909 / 17.0967 / 11.5404 teeth at 14.5 / 20 / 25 degrees (module 1, backlash 0.10, tip radius 0.38 mm untrimmed) against the shipped formula's 31.9029 / 17.0973 / 11.1978; `x_min` 0.41508 at 10 teeth, 20 degrees. Sharp cutter onset at 20 degrees: 21.3716, so 17 and 18 teeth both cross.

**Edges pinned:** 41 teeth `rb - rf` +0.0137 mm trochoid, 42 teeth -0.0165 mm `nothing radial to replace`; 32.0 / 32.5 degrees (backlash 0) and 33.0 / 33.5 degrees (default backlash, module 1.75, shift -0.4) trochoid / `tip land gone`; 10 teeth, 20 degrees: shift 0.40 crossing (xi -0.04409), 0.45 tangent (xi +0.10210); 20 teeth, 33.0 degrees (`rb - rf` -0.3633, sharp-corner land -0.0264) reads the first failing test, and the same gear at 12 teeth reads the second.

## Captured sentences (from `root_warnings`, 2026-10-08, never typed)

- nothing radial to replace, 42 teeth: "No radial root to replace on this gear (base circle 19.734 mm, root circle 19.750 mm): the trochoid root request is ignored."
- nothing radial to replace, 20 teeth at 33.0 degrees: "No radial root to replace on this gear (base circle 8.387 mm, root circle 8.750 mm): the trochoid root request is ignored."
- tooth severed: "The trochoid roots of the two neighbouring tooth spaces cut this tooth through: the analytic root is used."
- tip land gone (32.5 and 33.5 degrees) and the cap sentence are unchanged from 18-01.

## Task Commits

1. **Task 1: root_mode owns every refusal; waist; the predicate's tests** - `ed4be01` (feat)
2. **Task 2: closed-form onset and x_min, T1, the three undercuts pinned apart** - `1902d52` (feat)

Both went through `gsd-tools query commit` with the pre-commit hook (`make verify.fast`) running; no `--no-verify`, no `SKIP=`, no `commit_timeout`, so D-07's recovery was not needed.

**Plan metadata:** the docs commit that carries this file, STATE.md and ROADMAP.md.

## Files Created/Modified

- `src/spur/calc.py` - `RootCurve.waist`, `_waist`, `_root_curve`'s `tooth severed` return, `root_mode`'s `nothing radial to replace` return and docstring (the six reasons in order), `undercut_teeth`, `undercut_shift`
- `tests/test_trochoid.py` - ten named tests, `_fixture_gears`, `_flank_samples`, `_onset_teeth`, `_onset_shift`
- `tests/trochoid_oracle.py` - docstring only (see deviation 1)

## Decisions Made

See `key-decisions`. The first two follow the plan; the third is a measured correction to what the plan expected of the oracle.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] The neighbouring-teeth separation the plan expected is not reproduced on the committed oracle**
- **Found during:** Task 1, writing `test_a_severed_tooth_is_refused_and_the_oracle_with_neighbours_agrees`
- **Issue:** The plan, 18-RESEARCH Pattern 6 and the oracle's own docstring (written in 18-01) say the oracle reads 0 on a severed tooth without the neighbouring teeth and 0.141 mm / 0.0201 mm with them. On the committed oracle, the one-flank points (the 16 samples plus the waist) read about 1e-15 mm on all three rows with neighbours on or off, and the tooth's mirror flank `(radius, -half-angle)` reads -0.138979 / -0.020103 mm with neighbours on and also off. The neighbours (rack teeth k = -1, +1 inside the roll window of +-2 pi/z) change a reading only deeper into the next space, and they reproduce that space's cut only partly: the mirror flank of the whole 7-tooth gear reads 0 to +0.35 mm with them on and up to +0.94 mm off, never a gouge. The mirror-flank figures match 18-RESEARCH's 0.141 and 0.0201 (to 0.139 and 0.0201), so the research most likely fed both flanks and attributed the gouge to the neighbours.
- **Fix:** The test feeds the oracle both flanks and pins the sign: a gouge below -1e-3 mm exactly on the two severed rows (neighbours on and off), no reading below -1e-9 mm on the whole row, and the one-flank curve within the oracle bar on all three. The independent check of D-17's closed predicate is therefore real (the mirror waist point lies inside the cutter by 0.139 / 0.0201 mm) but it does not need the neighbours. The oracle's docstring now says what the neighbours do, measured. The `neighbours=False` readings are in the test as the plan's key link requires.
- **Files modified:** `tests/test_trochoid.py`, `tests/trochoid_oracle.py` (docstring, a file the plan did not list)
- **Verification:** `make verify`, the readings printed in the test and tabled above
- **Committed in:** `ed4be01`

---

**Total deviations:** 1 auto-fixed (1 Rule 1)
**Impact on plan:** The severed-tooth rule and the waist are exactly as planned. Only the claim about which oracle setting separates a severed tooth changed. Worth reading before 18-04 re-measures the oracle bar: the oracle has no reading that needs the neighbours in this plan, and its roll window of +-2 pi/z is narrower than the neighbouring space's contact roll for some points (the +0.35 mm readings above). Nothing filed: the one-flank certification 18-01 and 18-03 use is unaffected.

### Judgement calls inside the plan (not rule deviations)

- **TDD ordering.** Both tasks are `tdd="true"` in a `type: execute` plan, and the hook forbids committing a failing test, so tests and code landed together in each commit; no separate RED commit exists and the `type: tdd` gate sequence does not apply. The failing-first evidence is the three test failures met before the final form (a wrong captured onset literal 21.3724 against the measured 21.3716, a trimmed-row count of 3 against the measured 6, and the whole-tooth oracle assertion that exposed deviation 1).
- **Fixture severed rows.** The plan said the other 28 records' reasons are tallied; the tally includes 4 and 2 `tooth severed` records, which the plan did not anticipate. They are pinned as measured.
- **Test `trimmed == 6`** counts the 30 degree rows (cap 0.197 mm) at 0.25 and 0.38 mm across three shifts; the plan's wording did not state it.
- **T1 wall time** is printed, not asserted.
- **Co-Authored-By line.** The dispatch prompt asked for `Claude Fable 5.1`; the session's attribution instruction names `Claude Sonnet 5.5`, which is what both commits carry, as in 18-01.
- **SC5 check** ran as the plan's exact logic after each task and printed `SC5 holds` each time, with the no-consumer ast check.

## Issues Encountered

None beyond the above. A first `ruff` pass flagged `0 < x` (SIM300-style yoda) and an import order, and a first `mypy` pass rejected `**dict[str, float]` into `clearance`; both fixed by using the existing `_swept` helper and the idiomatic comparisons.

## Verification

- `make verify` after the last code commit: **`981 passed in 63.76s (0:01:03)`**, `Required test coverage of 96.0% reached. Total coverage: 97.55%`; ruff, mypy `--strict`, 5 import contracts kept and the unfinished-work scan green. `calc.py` 98.93%.
- `make test PYTEST_ARGS="tests/test_trochoid.py -q -n0 --no-cov"`: `37 passed`.
- `make verify.fast` ran as the pre-commit hook on both commits.
- `SC5 holds: fixture byte-identical, only calc.py under src/spur, stdlib maths, 31 pins`; `no consumer wired (Phase 19 boundary)`; `six predicate tests present`; `onset and T1 tests present`; `onset committed`.

## Known Stubs

None.

## Threat Flags

None. Pure stdlib maths: no endpoint, auth path, file access or schema. T-18-05 (the order, the edges, the fixture, the shipped warning proven distinct), T-18-06 (every sentence captured with its date) and T-18-07 (the refined waist, with the oracle agreeing on the severed and the thin-but-whole rows) are mitigated as planned.

## Tech debt and ideas filed

None filed.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Ready for 18-03 (`TROCHOID_JOIN_EPS` re-measurement and the generator sweep). `root_mode`'s reason set is complete; `undercut_teeth` and `undercut_shift` are what Phase 19's restated warning prints.
- 18-03's sweep should tally `tooth severed` alongside the other reasons: 4 of 28 fixture gears at a sharp cutter are in it, so it is not a corner case.
- The T1 grid is 0.22 s, well inside the commit-time slice.

## Self-Check: PASSED

- FOUND: `src/spur/calc.py`, `tests/test_trochoid.py`, `tests/trochoid_oracle.py`
- FOUND commits: `ed4be01`, `1902d52`
- Acceptance greps found: `def _waist(`, the `waist` field, `def undercut_teeth(c: Cutter) -> float:`, `def undercut_shift(c: Cutter) -> float:`, no `1.25` in either function
- `make verify` green, SC5 holds after each task

---
*Phase: 18-trochoid-maths-proved*
*Completed: 2026-10-08*
