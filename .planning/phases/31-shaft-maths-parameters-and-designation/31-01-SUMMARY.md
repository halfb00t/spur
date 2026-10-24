---
phase: 31-shaft-maths-parameters-and-designation
plan: 01
subsystem: shaft-maths
tags: [din5480, pydantic, profile-shift, frozen-contract, epsilon]

requires:
  - phase: 30-scope-seam-and-gear-safety-guard
    provides: the three shaft placeholders under import contracts C1-C5, make gear.unchanged, the Seen-red-once pattern
provides:
  - ShaftParams, the shaft's one frozen parameter model (eight fields, pinned names, order and defaults)
  - din5480 constants block (every constant an ASSUMPTION) and the shift, tip, root and thickness formulas
  - shaft_calc.ShaftDimensions, check_shaft (range refusal with X_EPS) and derive_shaft
  - a Phase 31 section in bench/RESULTS.md with five guards seen red once
affects: [31-02, 31-03, 31-04, 31-05, 31-06, phase-32, phase-33]

plan_head_before: 1e42c170dea905729be4b16de325b761d2c5c6da
plan_head_after: ac50062316f122a6a4cb47773a2e1b94a6e04dfc

actuals:
  tokens: 11650   # chars/4 over the changed files: 20581 source+tests, 6281 RESULTS diff, 19768 logs
  tasks: 3
  commits: 5      # measured: git rev-list --count 1e42c17..HEAD, before this SUMMARY's own commit

tech-stack:
  added: []
  patterns:
    - "ShaftParams copies GearParams' shape: frozen model, _f/_extra field builders imported from params, local-import model validator raising the gear's `infeasible` error"
    - "formulas as functions over plain floats in din5480, read at call time through the module (din5480.H_FP) so a changed constant reaches only its own quantity"
    - "a literal tolerance in tests that must not move with the production epsilon"

key-files:
  created:
    - tests/test_shaft_calc.py
    - tests/test_shaft_params.py
    - .planning/phases/31-shaft-maths-parameters-and-designation/investigation/31-01-green.log
    - .planning/phases/31-shaft-maths-parameters-and-designation/investigation/31-01-red-eps-zero.log
    - .planning/phases/31-shaft-maths-parameters-and-designation/investigation/31-01-red-default.log
    - .planning/phases/31-shaft-maths-parameters-and-designation/investigation/31-01-red-shared-constant.log
    - .planning/phases/31-shaft-maths-parameters-and-designation/investigation/31-01-red-range.log
    - .planning/phases/31-shaft-maths-parameters-and-designation/investigation/31-01-red-fit.log
  modified:
    - src/spur/din5480.py
    - src/spur/shaft_calc.py
    - src/spur/shaft_params.py
    - bench/RESULTS.md

key-decisions:
  - "Profile shift is x = (d_B - z*m)/(2*m) - SHIFT_TERM, pinned: the only one of four measured orders under which all three D-19 cases fall outside the bare range"
  - "SHIFT_TERM (0.55, derived from ADDENDUM_FACTOR and TIP_DIAMETER_OFFSET) and H_FP (0.55, provisional) are two named constants; changing H_FP moves root_d only"
  - "The range refusal lives in shaft_calc.check_shaft, reached from ShaftParams._feasible by a local import, so Phase 33 serves it as the gear's `infeasible` 422"
  - "Solid-only field names, defaults and provisional bounds chosen here for the human's review (below)"

patterns-established:
  - "Every constant and formula in din5480 carries ASSUMPTION (clause slot) until the 31-05 checkpoint"
  - "Red runs purge __pycache__ and set PYTHONDONTWRITEBYTECODE: a same-size edit reverted in the same second reuses stale bytecode"

requirements-completed: [REQ-shaft-params, REQ-profile-shift-from-dB, REQ-shaft-basic-dims]

coverage:
  - id: D1
    description: "The default shaft W 25x1.25x18x8f derives profile shift 0.45, pitch 22.5, tip 24.75, root 22.25 and nominal thickness 2.613 through ShaftParams, check_shaft and derive_shaft"
    requirement: "REQ-shaft-basic-dims"
    verification:
      - kind: unit
        ref: "tests/test_shaft_calc.py#test_the_default_shaft_derives_its_basic_dimensions"
        status: pass
    human_judgment: true
    rationale: "The formulas are ASSUMPTIONS reproduced from two vendor reports until the 31-05 checkpoint records their clauses from the human's DIN 5480 copy; a passing test proves the code does what was planned, not that the standard says so"
  - id: D2
    description: "ShaftParams is frozen and hashable with eight pinned fields (names, order, defaults); the fit token is shape-checked only; every bound is inclusive; non-finite and null input is refused"
    requirement: "REQ-shaft-params"
    verification:
      - kind: unit
        ref: "tests/test_shaft_params.py#test_the_shaft_field_names_and_defaults_are_frozen"
        status: pass
      - kind: unit
        ref: "tests/test_shaft_params.py#test_a_shaft_parameter_set_is_frozen_and_hashable"
        status: pass
      - kind: unit
        ref: "tests/test_shaft_params.py#test_the_fit_token_is_checked_for_shape_only"
        status: pass
      - kind: unit
        ref: "tests/test_shaft_params.py#test_each_field_bound_is_inclusive_and_one_step_outside_is_refused"
        status: pass
      - kind: unit
        ref: "tests/test_shaft_params.py#test_non_finite_numbers_are_refused"
        status: pass
      - kind: unit
        ref: "tests/test_shaft_params.py#test_a_missing_or_null_field_is_refused_by_its_type"
        status: pass
    human_judgment: false
  - id: D3
    description: "A profile shift outside -0.05 to +0.45 is refused as `infeasible` naming the range and the fields module, reference_d, teeth; the three float-edge cases are accepted through X_EPS and each was seen red with X_EPS = 0"
    requirement: "REQ-profile-shift-from-dB"
    verification:
      - kind: unit
        ref: "tests/test_shaft_params.py#test_a_shift_outside_the_shaft_range_is_refused_naming_the_range_and_fields"
        status: pass
      - kind: unit
        ref: "tests/test_shaft_params.py#test_the_shift_range_edges_are_accepted_through_the_epsilon"
        status: pass
      - kind: unit
        ref: "tests/test_shaft_params.py#test_the_default_shaft_validates_and_sits_on_the_upper_shift_edge"
        status: pass
    human_judgment: false
  - id: D4
    description: "H_FP is a separate constant from SHIFT_TERM: setting it to 0.60 moves root_d of W70x3x22 from 63.4 to 63.1 and nothing else"
    requirement: "REQ-shaft-basic-dims"
    verification:
      - kind: unit
        ref: "tests/test_shaft_calc.py#test_the_dedendum_constant_moves_the_root_and_not_the_shift"
        status: pass
    human_judgment: false
  - id: D5
    description: "Gear untouched: params.py, calc.py, tests/regression/, ci.yml, requirements.txt byte-equal to v0.6; ten import contracts kept"
    verification:
      - kind: other
        ref: "make gear.unchanged; make lint-imports; git diff --exit-code v0.6 -- src/spur/params.py src/spur/calc.py tests/regression/ .github/workflows/ci.yml requirements.txt"
        status: pass
    human_judgment: false

duration: 14min
completed: 2026-10-24
status: complete
---

# Phase 31 Plan 01: Shaft Parameters and Basic Dimensions Summary

**Frozen ShaftParams (eight pinned fields) through check_shaft and derive_shaft into a typed ShaftDimensions for the default W 25x1.25x18x8f, with the profile shift derived from d_B in one pinned expression order and accepted through X_EPS at the float edges**

## Performance

- **Duration:** 14 min (start taken from the creation time of the `investigation/` folder; the start-time step was not run at spawn)
- **Started:** 2026-10-24T10:50:57Z
- **Completed:** 2026-10-24T11:05Z (approximate)
- **Tasks:** 3
- **Files modified:** 12 (3 source, 2 test, `bench/RESULTS.md`, 6 logs)

## Accomplishments

- `derive_shaft(ShaftParams())` returns reference_d 25.0, profile_shift 0.45, profile_shift_mm 0.562, pitch_d 22.5, tip_d 24.75, root_d 22.25, nominal_thickness 2.613, warnings `()`.
- A shift outside -0.05 to +0.45 is refused at the `ShaftParams` boundary as the gear's `infeasible` error, naming the range and the fields `["module", "reference_d", "teeth"]`; never clamped.
- The names, order and defaults of all eight fields are pinned by a test whose docstring says a failure means a published-link contract moved.
- Five guards (epsilon, pinned defaults, the two-0.55 split, the range refusal, the fit shape) were seen red once, reverted, and recorded in `bench/RESULTS.md`.

## Task Commits

1. **Task 1: Tracer, the default shaft goes in as ShaftParams and comes out as its basic dimensions** - `1e120ce` (feat)
2. **Task 2: The frozen contract, the fit shape and the range refusal** - `dbaac98` (test), then `62941d4` and `1080c65` (test, see Deviations)
3. **Task 3: Each guard seen red once, reverted, recorded** - `ac50062` (docs)

**Plan metadata:** the commit that carries this file (docs: complete plan)

The tracer gate: the tracer's `<verify>` is automated-only and `human_verify_mode` is `end-of-phase`, so it was re-run before Task 2 (the three checks of Task 1 passed again, the same results); `Tracer verified end-to-end` and expansion went ahead.

## Files Created/Modified

- `src/spur/din5480.py` - constants block (ALPHA, ADDENDUM_FACTOR, TIP_DIAMETER_OFFSET, SHIFT_TERM, H_FP, RHO_FP, X_MIN, X_MAX, X_EPS, FIT_PATTERN), `profile_shift`, `tip_diameter`, `root_diameter`, `tooth_thickness`; docstring rewritten to say the formulas are assumptions until the checkpoint
- `src/spur/shaft_calc.py` - `ShaftDimensions`, `check_shaft`, `derive_shaft`
- `src/spur/shaft_params.py` - `ShaftParams` and its `_feasible` validator
- `tests/test_shaft_params.py` - 9 test functions (59 cases): pinned contract, frozen, fit, bounds, non-finite, null, range refusal, epsilon edges
- `tests/test_shaft_calc.py` - 3 tests: default dimensions, frozen result, H_FP moves only the root
- `bench/RESULTS.md` - new section `## Shaft maths, parameters and designation (Phase 31)` with `### Seen red once (Phase 31)`, 16 lines added, none removed
- `.planning/phases/31-shaft-maths-parameters-and-designation/investigation/31-01-*.log` - green lint-imports log and five red logs

## Decisions Made

- **Corrected D-04/D-19 wording.** Under the pinned expression order the default W 25x1.25x18 computes to `0.44999999999999996`, never above 0.45, so the default does not exercise the epsilon. D-19 quoted `0.4500000000000008` for the upper case; the value under the pinned order is `0.45000000000000084` for `(17.6, 0.8, 20)`. The epsilon is proved by three dedicated cases, each accepted, each with its raw shift outside the bare range by less than 1e-9, each seen red with `X_EPS = 0.0`:
  - `(17.6, 0.8, 20)` -> `0.45000000000000084` (upper edge)
  - `(30, 2, 14)` -> `-0.050000000000000044` (lower edge)
  - `(25, 1.25, 19)` -> `-0.050000000000000044` (lower edge)
  The `x*m/m` order was rejected because it reads `(25, 1.25, 19)` as exactly -0.05, which a bare comparison accepts.
- **Solid-only names, defaults and provisional bounds, for the human's review.** Phase 32's sweep may revise them by logged decision until Phase 33 publishes the first shaft link (30-CONTEXT D-18):

  | Field | Default | Bounds | Group |
  |---|---|---|---|
  | `splined_length` | 30.0 | 1 to 500 | Spline |
  | `end_chamfer` | 1.0 (below the 1.25 mm tooth height at h_fP 0.55) | 0 to 10, 0 = none | Spline |
  | `shank_d` | 25.0 (= reference_d, a shoulder above the 24.75 mm tip) | 1 to 850 | Shank |
  | `shank_length` | 20.0 | 0 to 500, 0 = none | Shank |

  The spline fields are `reference_d` 3 to 850, `module` 0.5 to 10, `teeth` 6 to 82 (research A3, provisional).
- **Phase 32 handoff.** Cross-field rules among the solid fields (chamfer against tooth height, shank against tip) are Phase 32's, with the solid (31-RESEARCH Open Question 5). This plan enforces ranges only, and a comment above the four fields says so.
- **Filed items:** no debt or idea item was filed.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] The default's edge test and the edge cases compared against X_EPS, so zeroing the epsilon failed the wrong things**
- **Found during:** Task 3 (R1, `X_EPS = 0.0`)
- **Issue:** the plan specifies `abs(profile_shift(25.0, 1.25, 18) - X_MAX) <= X_EPS` for the default's test and asks R1 to leave it green. With the epsilon at 0 the default's raw shift (5.5e-17 off the edge) fails that line, contradicting the plan's own D-19 expectation and acceptance criterion. The three edge cases had the same coupling: they failed on their own `0 < outside <= X_EPS` line before the production refusal ran.
- **Fix:** both comparisons use a literal `1e-9`, with comments saying why. The R1 red now shows the three edge cases failing on the `infeasible` refusal and the default's test passing.
- **Files modified:** `tests/test_shaft_params.py`
- **Verification:** `31-01-red-eps-zero.log` holds 3 `edges_are_accepted ... FAILED` and 1 `sits_on_the_upper_shift_edge PASSED`; 59 passed on the final tree.
- **Committed in:** `62941d4`, `1080c65`

**2. [Rule 3 - Blocking] Stale bytecode corrupted the first red logs**
- **Found during:** Task 3 (R3 to R5)
- **Issue:** R2's edit (`18` to `19`) keeps the file size; the revert landed in the same second, so Python reused the stale compiled `shaft_params`, and R3 to R5 read `teeth` 19 and failed the pinned-defaults test they had nothing to do with.
- **Fix:** every red runs with `PYTHONDONTWRITEBYTECODE=1` and `__pycache__` deleted before the run and after each revert; all five logs were regenerated. The method is recorded in the RESULTS section.
- **Files modified:** none in `src/` or `tests/` (logs and RESULTS only)
- **Verification:** the final logs show each red failing only its own test (`1 failed` for R3 and R5, `2 failed` for R2 and R4); `git status --porcelain -- src tests` empty after each revert.
- **Committed in:** `ac50062`

**3. [Plan wording] Two tests carry a wording choice the plan did not fix**
- `31-01-green.log` (a Task 1 verify output) was committed with Task 1 rather than with Task 3, since Task 1 produces it. No effect on any check.
- The plan's `fit` parametrised test is one function with an accepted flag, so `-k "fit_token"` reports 12 passed and the file has exactly 9 `test_` functions, as the acceptance criteria require.

---

**Total deviations:** 2 auto-fixed (1 Rule 1, 1 Rule 3), 1 wording note
**Impact on plan:** both fixes were needed for the reds to prove what the plan says they prove. No change to production behavior and no scope creep.

## Issues Encountered

None beyond the two deviations.

## Gate

`make verify`: `1431 passed in 281.11s (0:04:41)`, `real 4:42.34` (exit 0), at the final tree before this SUMMARY. Phase 30's baseline was `1369 passed`, `233.18 s`; no load reading was taken for this run, so the 48 s difference is not claimed as a cost of this plan. 31-06 prices the phase's gate delta with load recorded.

Other checks, all at the final tree: `make lint-imports` reads `Contracts: 10 kept, 0 broken.`; `make gear.unchanged` reads `gear.unchanged: tests/regression/, .github/workflows/ci.yml and /api/schema (8723 bytes) are byte-equal to v0.6`; `git diff --exit-code v0.6 -- src/spur/params.py src/spur/calc.py tests/regression/ .github/workflows/ci.yml requirements.txt` is empty; ruff and `mypy --strict` clean.

## Known Stubs

None. Every constant and formula in `din5480.py` is marked `ASSUMPTION (clause slot)` on purpose until the 31-05 checkpoint; that is the plan's stated state (D-06, D-07), not a stub.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- 31-02 can build the independent oracle (`tests/shaft_oracle.py`) and cross-check the four formulas against the vendor rows; `H_FP` is a module attribute and `root_diameter` takes the factor as an argument, so each vendor row can run at its own h_fP.
- 31-03 and 31-04 insert keys into `ShaftDimensions` before `warnings`.
- Open for the human at 31-05: the clause for every `ASSUMPTION`, h_fP (0.55 or 0.60), and the fit notation behind `FIT_PATTERN`.

## Self-Check: PASSED

Files found: `src/spur/din5480.py`, `src/spur/shaft_calc.py`, `src/spur/shaft_params.py`, `tests/test_shaft_calc.py`, `tests/test_shaft_params.py`, `bench/RESULTS.md`, the six logs. Commits found: `1e120ce`, `dbaac98`, `62941d4`, `1080c65`, `ac50062`.

---
*Phase: 31-shaft-maths-parameters-and-designation*
*Completed: 2026-10-24*
