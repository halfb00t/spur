---
phase: 18-trochoid-maths-proved
plan: 06
subsystem: gear-maths
tags: [trochoid, curve-invalid-guard, input-validation, mutation-check, gap-closure]

requires:
  - phase: 18-trochoid-maths-proved
    provides: "18-05: the T2/T3/T4 proofs; 18-REVIEW WR-01/WR-02 and 18-VERIFICATION item 1 that this plan closes"
provides:
  - "tests/test_trochoid.py: the fourth arm of _root_curve's curve-invalid guard fires under one test on the tracer gear, seen red with the arm replaced by False"
  - "calc.cutter(): refuses a tip radius that is not a finite, non-negative millimetre value with a ValueError naming it (root_mode propagates)"
  - "18-REVIEW-DISPOSITION.md WR-01/WR-02 fixed with shas; 18-UAT.md test 1 passed"
affects: [19]

actuals:
  tokens: 1620   # chars/4 over the added lines of src and tests (6,478 chars)
  tasks: 2
  commits: 3     # MEASURED: git rev-list --count 71c369f..ae88f23 (the SUMMARY commit follows)
plan_head_before: 71c369f325559f060af764fe191878ab53dcc017
plan_head_after: ae88f23ac466c92b99e9136666ea9bfaeef47d71
commits: 3

tech-stack:
  added: []
  patterns:
    - "a patch that must not disturb a shared helper wraps the real function and arms the bend only after it has run"
    - "an internal-contract input is guarded with a ValueError, not a user-facing RootReason, until a boundary field validates it"

key-files:
  created: []
  modified:
    - src/spur/calc.py
    - tests/test_trochoid.py
    - .planning/phases/18-trochoid-maths-proved/18-REVIEW-DISPOSITION.md
    - .planning/phases/18-trochoid-maths-proved/18-UAT.md

key-decisions:
  - "The fourth-arm test moves the last pre-junction sample to rb + 0.01 mm, not only its half-angle: on the tracer gear every sample before the junction is under rb (4.640 mm against 4.698 mm), so bending the half-angle alone cannot reach the arm"
  - "cutter() raises ValueError for a bad rho and not a RootReason: no user can reach the state in this phase, so no sentence is written for it (D-07)"

requirements-completed: [REQ-trochoid-root-generated, REQ-cutter-defined-once]

coverage:
  - id: D1
    description: "The fourth curve-invalid guard arm (a crossing curve with an early sample past rb and not inside the involute) is exercised by a test that makes it fire on the tracer gear, and that test is red when the arm is removed"
    requirement: REQ-trochoid-root-generated
    verification:
      - kind: unit
        ref: "tests/test_trochoid.py#test_a_crossing_curve_with_an_early_point_outside_the_involute_is_refused"
        status: pass
    human_judgment: false
  - id: D2
    description: "cutter() refuses NaN, inf, -inf and a negative tip radius with a ValueError naming the value; 0.0 and -0.0 stay the legal sharp cutter; root_mode propagates and never answers trochoid for a NaN"
    requirement: REQ-cutter-defined-once
    verification:
      - kind: unit
        ref: "tests/test_trochoid.py#test_a_tip_radius_that_is_not_a_finite_millimetre_value_is_refused_before_any_cap"
        status: pass
    human_judgment: false

duration: 9min
completed: 2026-10-08
status: complete
---

# Phase 18 Plan 06: The Untested Guard Arm and the Tip-Radius Guard Summary

**The fourth `curve invalid` arm now has a test that fires it on the tracer gear and goes red when the arm is removed, and `cutter()` raises a `ValueError` for a NaN, infinite or negative tip radius instead of silently trimming it to the cap.**

## Performance

- **Duration:** 9 min
- **Started:** ~2026-10-08T05:08Z (the commit ledger was written at 05:10:05Z after reading the plan)
- **Completed:** 2026-10-08T05:16Z
- **Tasks:** 2
- **Files modified:** 4 (`src/spur/calc.py`, `tests/test_trochoid.py`, `18-REVIEW-DISPOSITION.md`, `18-UAT.md`)

## Accomplishments

- **WR-01 / 18-VERIFICATION item 1.** `test_a_crossing_curve_with_an_early_point_outside_the_involute_is_refused` makes the arm fire: `_root_curve(c) == "curve invalid"`, `trochoid_root(c) is None`, `root_mode(...)` reads `("radial", "curve invalid")` with the sentence already captured in the file. The real `_junction` runs against the real point function (the wrapper asserts it found the junction read beforehand) and only then arms the bend; exactly one sample is bent, so an `any` turned into `all` would be seen as well.
- **WR-02.** `cutter(p, rho)` raises `ValueError("tip radius must be a finite, non-negative millimetre value, got ...")` before any arithmetic. Measured before the guard on 12 teeth, module 1, 20 degrees: `nan` gave mode `trochoid`, reason None, no sentence, `c.rho` 0.471 (trimmed to the cap silently); `-0.1` gave `trochoid` with no sentence; `-0.5` gave `curve invalid`; `-inf` gave `bracket degenerate`; `inf` capped with the cap sentence (left as the review noted, now refused too). `0.0` and `-0.0` still build the sharp cutter.
- Review ledger WR-01 and WR-02 read `fixed` (`8e96c2d`, `085aee7`); `18-UAT.md` test 1 reads passed, `passed: 1`, `pending: 0`, `status: complete`.

## Mutation result (WR-01, Task 1)

Run on a scratch copy of `src`, `tests` and `bench` (initialised as its own git repo so the two `test_bench` tests that call `git rev-parse` could run); the working tree was never touched and `git status --short src` is clean. The arm (`or (join == "crossing" and any(...))`) was replaced by `or False`.

```
mutant:   FAILED tests/test_trochoid.py::test_a_crossing_curve_with_an_early_point_outside_the_involute_is_refused
          1 failed, 503 passed in 17.52s     (tests/test_trochoid.py tests/test_calc.py tests/test_bench.py)
control:  504 passed in 16.32s               (the same scratch copy with calc.py restored)
```

Exactly the new test is red; nothing else.

## Task Commits

1. **Task 1: the fourth guard arm fires under one test** - `8e96c2d` (test). `src/spur/calc.py` byte-identical to HEAD in this commit.
2. **Task 2: `cutter()` refuses a non-finite or negative tip radius** - `085aee7` (fix)
3. **Task 2 records: ledger and UAT** - `ae88f23` (docs; needs the two shas above, so it follows them)

All three ran the pre-commit hook (`make verify.fast`); no `--no-verify`, no `SKIP=`.

**Plan metadata:** the commit that follows this SUMMARY.

## Verification

- `make verify`: ruff `All checks passed!`, mypy `--strict`, import contracts, unfinished-work scan, and **`1022 passed in 68.50s (0:01:08)`**, `Required test coverage of 96.0% reached. Total coverage: 97.68%`. Run on `085aee7` plus the two record edits (planning files only).
- SC5: `SC5 holds: fixture byte-identical, only calc.py under src/spur, 31 pins` (against `git merge-base HEAD origin/main`).
- Ledger check: `ledger: WR-01, WR-02 fixed`.
- `grep -n 'math.isfinite(rho)' src/spur/calc.py`: line 1291.
- `make test PYTEST_ARGS="tests/test_trochoid.py -q -n0 --no-cov -k 'finite_millimetre or outside_the_involute or curve_invalid'"`: `6 passed, 67 deselected`.

## TDD Gate Compliance

Both tasks are `tdd="true"` in a `type: execute` plan, so the `type: tdd` gate sequence does not apply. As in 18-01, the pre-commit hook runs `make verify.fast` and refuses a failing test, so there is no RED-only commit.

- Task 1 adds a test for code that already exists (a characterisation test). Its red evidence is the mutation above.
- Task 2: the four refusing rows were run before the guard existed and failed (`4 failed, 69 deselected`: nan, inf, minus-inf, negative; the sharp-cutter assertions sit in the same function), then the guard was added in the same commit as the test.

## Decisions Made

- The fourth-arm test cannot just add 1e-3 to an early half-angle as the plan and the review sketched. Measured on the tracer gear, the radii of the 16 samples run 3.750 to 4.640 mm and then 4.7256 mm; only the last (the junction) is at or past rb 4.698463, so no early sample satisfies `radius >= pr.rb`. The test therefore moves the last early sample to `rb + 0.01` (4.7085 mm, between its neighbours 4.640 and 4.7256 so the radius still rises, under `ra` 6) and sets its half-angle to the involute's plus 1e-3 (0.173 rad, inside pi/z = 0.314). That is the case the arm models: a curve that has already crossed the base circle and is not inside the involute.
- A `ValueError`, not a `RootReason`, for a bad `rho` (as the plan specified): no user can reach it until Phase 19's field.
- `-0.0` is accepted as it stands (`-0.0 < 0` is False and `Cutter.rho == 0.0` holds); it is not normalised, because nothing prints a zero radius.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] The planned patch shape could not reach the arm**
- **Found during:** Task 1
- **Issue:** The behavior block and review WR-01's sketch bend only the half-angle of an early point with `radius >= rb`. On the tracer gear no early point has `radius >= rb`, so the first run of the test returned a healthy `RootCurve`.
- **Fix:** Also moves the last early sample's radius to `rb + 0.01` (see Decisions Made); the docstring records the measured premise and the test asserts it (`honest.points[-2][0] < c.pr.rb`).
- **Files modified:** `tests/test_trochoid.py`
- **Verification:** the test passes on the tree and is the one red test under the `False` mutant.
- **Committed in:** `8e96c2d`

**2. [Rule 1 - Bug] The first draft of the WR-02 docstring misstated what a negative radius did**
- **Found during:** Task 2, measuring before adding the guard
- **Issue:** I had written that a negative radius was always refused as `curve invalid`; measured, -0.1 answers `trochoid` with no sentence, -0.5 `curve invalid`, -inf `bracket degenerate`.
- **Fix:** the docstring states the three measured outcomes.
- **Files modified:** `tests/test_trochoid.py`
- **Committed in:** `085aee7`

### Judgement calls (not rule deviations)

- **Extra commit.** The ledger and UAT edits are `ae88f23`, a third commit, because they name the shas of the two task commits and cannot be in them.
- **Existing test's docstring.** The plan said to write "three of the four arms"; the three-arm test actually reaches two (the tip circle through an out-of-box gear, the falling radius through a patch). The centreline and a second tip-circle case are in `test_a_curve_that_cannot_be_trusted_...`. The docstring says two of the four and points at both other tests. The test's name was left as it is: with the new test, every arm is reached somewhere in the file.
- **Co-Authored-By line.** The dispatch prompt names `Claude Fable 5.1`; the session's attribution instruction names `Claude Sonnet 5.5`, which the commits carry (as in 18-01).
- **Mutation check location.** Run on a scratch copy outside the repo rather than editing `calc.py` in place.

---

**Total deviations:** 2 auto-fixed (2 Rule 1, both in my own test text or patch shape). **Impact on plan:** none on scope.

## Issues Encountered

The two `tests/test_bench.py` tests that run `git rev-parse` failed on the first scratch-copy run because the scratch directory was not a git repository; initialising it as one removed them. Unrelated to the mutant.

## Known Stubs

None.

## Threat Flags

None. T-18-17 (the tip radius) and T-18-18 (the guard arm) are mitigated as planned; no new endpoint, file access or schema.

## Tech debt and ideas filed

None filed. The remaining review items IN-01 to IN-06 stay `open` in the ledger; they were out of this plan's scope.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- 18-VERIFICATION item 1 is closed and both warnings of the review are fixed, so the phase can be re-verified.
- Phase 19 must validate `rho` once at its `GearParams` field; the `ValueError` in `cutter()` is the interim guard and can stay as the internal contract.

## Self-Check: PASSED

- FOUND: `src/spur/calc.py`, `tests/test_trochoid.py`, `18-REVIEW-DISPOSITION.md`, `18-UAT.md`
- FOUND commits: `8e96c2d`, `085aee7`, `ae88f23`
- `make verify` green, SC5 holds

---
*Phase: 18-trochoid-maths-proved*
*Completed: 2026-10-08*
