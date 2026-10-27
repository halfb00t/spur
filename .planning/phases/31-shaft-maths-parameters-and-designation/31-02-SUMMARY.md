---
phase: 31-shaft-maths-parameters-and-designation
plan: 02
subsystem: shaft-maths
tags: [din5480, oracle, independent-oracle, vendor-cross-check, seen-red-once]

requires:
  - phase: 31-shaft-maths-parameters-and-designation
    provides: din5480 constants and the shift, tip, root and thickness formulas (31-01)
provides:
  - tests/shaft_oracle.py, a not-collected stdlib oracle for d_B, tip, root and nominal thickness
  - tests/test_din5480.py, 581 cases: a 192-case grid at 1e-9, vendor cross-checks, constant pins, two durable mutation tests
  - five more guards seen red once, recorded in bench/RESULTS.md
affects: [31-03, 31-04, 31-05, 31-06]

plan_head_before: add8c1b2a0a535fcc6bbfd83573077b75614a5ff
plan_head_after: 579fdc423c127e44af71654a5b2d1fd97653431a

actuals:
  tokens: 3763    # chars/4 over the changed tests and bench diff (10723 + 4331 chars); the five red logs add 188074 more and are evidence, not code
  tasks: 3
  commits: 3      # measured: git rev-list --count add8c1b..HEAD, before this SUMMARY's own commit

tech-stack:
  added: []
  patterns:
    - "an oracle that rebuilds the part from textbook definitions (basic rack, parametric involute placed by the base-thickness identity), with an ast test that it imports only __future__ and math"
    - "vendor rows as module constants, each labelled `Vendor cross-check, not the standard (D-08)` with its URL, compared at the vendor's print precision"

key-files:
  created:
    - tests/shaft_oracle.py
    - tests/test_din5480.py
    - .planning/phases/31-shaft-maths-parameters-and-designation/investigation/31-02-red-shift-term.log
    - .planning/phases/31-shaft-maths-parameters-and-designation/investigation/31-02-red-thickness.log
    - .planning/phases/31-shaft-maths-parameters-and-designation/investigation/31-02-red-tip.log
    - .planning/phases/31-shaft-maths-parameters-and-designation/investigation/31-02-red-oracle-side.log
    - .planning/phases/31-shaft-maths-parameters-and-designation/investigation/31-02-red-oracle-import.log
  modified:
    - bench/RESULTS.md

key-decisions:
  - "The oracle places the involute with s_b = m*cos(a)*(pi/2 + z*(tan(a) - a)) + 2*x*m*sin(a) and reads the thickness at m*z/2 with atan2; no inv helper, no bisection, no closed-form pin lives in it"
  - "The two root formulas are the same definition written twice, so their comparison proves the transcription only; the oracle docstring and root_diameter say so"
  - "Vendor rows are compared at their own print precision (KISSsoft 5e-4, Hexagon 5e-3, thickness 5e-4, KISSsoft x*m 2e-4) and never loosen the oracle's 1e-9"

patterns-established:
  - "Grid cases carry no zero shift, because a sin-for-tan thickness cannot be seen at x = 0"

requirements-completed: [REQ-shaft-basic-dims, REQ-profile-shift-from-dB]

coverage:
  - id: D1
    description: "An independent stdlib oracle (basic rack plus a parametric involute) agrees with din5480 at 1e-9 over a 192-case grid for the shift, tip, both roots (h_fP 0.55 and 0.60) and the nominal thickness"
    requirement: "REQ-shaft-basic-dims"
    verification:
      - kind: unit
        ref: "tests/test_din5480.py#test_the_shift_inverts_the_oracle_reference_diameter"
        status: pass
      - kind: unit
        ref: "tests/test_din5480.py#test_the_basic_dims_agree_with_the_oracle"
        status: pass
      - kind: unit
        ref: "tests/test_din5480.py#test_the_basic_dims_order_root_below_pitch_below_tip"
        status: pass
      - kind: unit
        ref: "tests/test_din5480.py#test_the_shaft_oracle_imports_nothing_from_spur"
        status: pass
    human_judgment: true
    rationale: "The oracle proves the code computes what the assumed rack definition says; whether the assumed rack matches DIN 5480 is the 31-05 checkpoint's question. The root comparison proves transcription only."
  - id: D2
    description: "The vendor reports KISSsoft W70x3x22 and Hexagon W120x3x38 reproduce at print precision, labelled as cross-checks and never counted as anchor rows; SHIFT_TERM, ADDENDUM_FACTOR and TIP_DIAMETER_OFFSET are pinned apart from H_FP"
    requirement: "REQ-shaft-basic-dims"
    verification:
      - kind: unit
        ref: "tests/test_din5480.py#test_the_basic_dims_match_the_vendor_cross_checks"
        status: pass
      - kind: unit
        ref: "tests/test_din5480.py#test_the_shift_term_is_the_addendum_plus_half_the_tip_offset"
        status: pass
    human_judgment: true
    rationale: "Two vendor reports are not the standard (D-08); the anchor rows from the human's copy land in 31-06"
  - id: D3
    description: "Two durable tests show the oracle sees a shift term of 0.5 and a sin-for-tan thickness; each oracle comparison was seen red once against a mutated formula and recorded"
    requirement: "REQ-profile-shift-from-dB"
    verification:
      - kind: unit
        ref: "tests/test_din5480.py#test_the_oracle_refuses_a_mutated_shift_term"
        status: pass
      - kind: unit
        ref: "tests/test_din5480.py#test_the_oracle_refuses_a_mutated_thickness"
        status: pass
      - kind: other
        ref: "bench/RESULTS.md ### Seen red once (Phase 31), five 31-02 rows; investigation/31-02-red-*.log"
        status: pass
    human_judgment: false

duration: 7min
completed: 2026-10-24
status: complete
---

# Phase 31 Plan 02: Independent Oracle for the Basic Dimensions Summary

**A not-collected stdlib oracle (basic rack plus a parametric involute placed by the base-thickness identity) agrees with din5480's shift, tip, both roots and thickness to 1e-9 over 192 cases, with KISSsoft and Hexagon rows as labelled cross-checks and five mutations seen red once**

## Performance

- **Duration:** 7 min
- **Started:** 2026-10-24T11:03:16Z
- **Completed:** 2026-10-24T11:10:46Z (before the full `make verify`, 221 s)
- **Tasks:** 3
- **Files modified:** 8 (2 test files, `bench/RESULTS.md`, 5 logs)

## Accomplishments

- `tests/shaft_oracle.py` computes d_B, tip, root and thickness by another road than din5480: no `spur` import (an `ast` test enforces it, seen red in R5), no involute-function helper, no bisection, no closed-form pin. 31-03 extends it.
- `tests/test_din5480.py` holds 581 cases: 192 shift inversions, 192 oracle comparisons, 192 ordering checks (root below `m*z` below tip at h_fP 0.55 and 0.60), the constant pin, the vendor cross-check, two mutation tests, the import test.
- KISSsoft W 70x3x22 (d_a 69.400, d_f 63.100 at h_fP 0.60, x*m 0.3501 against 0.35 at 2e-4) and Hexagon W 120x3x38 (d_a 119.40, d_f 113.40 at h_fP 0.55, s 6.271) reproduce; each row sits under `Vendor cross-check, not the standard (D-08)` with its URL and is not an anchor row.
- Five reds recorded in `bench/RESULTS.md`, five rows appended, none removed (`5 0` numstat).

## Measurements

- **Serial wall time of `tests/test_din5480.py`:** `/usr/bin/time -p`, `real 0.39` s with `--no-cov -n0` (0.24 s pytest-reported), against L36's 30 s slice and the plan's 10 s limit.
- **Worst grid disagreement (192 cases, din5480 against the oracle):**

  | Quantity | Worst abs difference |
  |---|---|
  | profile shift x | 7.06e-15 |
  | tip diameter | 1.78e-15 |
  | root diameter, h_fP 0.55 and 0.60 | 0 (same expression written twice; transcription proof only) |
  | nominal thickness | 4.97e-14 |

  The tolerance stays at 1e-9; the margin is more than four orders.
- **Gate:** `make verify`: `2012 passed in 220.13s (0:03:40)`, `real 221.11`, exit 0, at the final tree before this SUMMARY. 31-01's gate was `1431 passed`, `281.11s`; the 581 added cases are this plan's. Load at the end of the run was 18.5 on 1 minute (`uptime`), so the 61 s difference against 31-01 is not claimed as a saving.
- Plan-level checks: `tests/test_din5480.py tests/test_shaft_calc.py tests/test_shaft_params.py tests/test_seam.py` read `649 passed`; `make gear.unchanged` reads `gear.unchanged: tests/regression/, .github/workflows/ci.yml and /api/schema (8723 bytes) are byte-equal to v0.6`; `make verify.fast` passed at each of the three commits.

## Task Commits

1. **Task 1 (tracer): the oracle rebuilds the default shaft, din5480 agrees at 1e-9** - `5583f0f` (test)
2. **Task 2: the grid, the vendor rows, the constant pins, the mutation tests** - `092a17b` (test)
3. **Task 3: each oracle comparison seen red once, reverted, recorded** - `579fdc4` (docs)

The tracer gate: the tracer's `<verify>` is automated-only and `human_verify_mode` is `end-of-phase`; its three checks (pytest `2 passed`, mypy, ruff plus `make no-fake-done`) had passed at the commit and again before Task 2's edit. `Tracer verified end-to-end` and expansion went ahead.

## Files Created/Modified

- `tests/shaft_oracle.py` - `reference_diameter`, `tip_diameter`, `root_diameter`, `tooth_thickness` over plain floats; private `_ALPHA`, `_ADDENDUM`, `_TIP_CLEARANCE`, `_involute_point`
- `tests/test_din5480.py` - `GRID`, `KISSSOFT_W70`, `HEXAGON_W120` and eight test functions
- `bench/RESULTS.md` - five `31-02` rows appended to `### Seen red once (Phase 31)`
- `.planning/phases/31-shaft-maths-parameters-and-designation/investigation/31-02-red-*.log` - five whole red logs

## Decisions Made

- The red logs keep the 31-01 method: `PYTHONDONTWRITEBYTECODE=1`, `__pycache__` purged before each run and after each revert. R1 (`0.45` to `0.40`) keeps the file size, so this mattered. `git status --porcelain -- src tests` was empty after every revert.
- Vendor rows are stored as typed `dict[str, float]` constants, with the tooth count cast to `int` where used; the simplest shape that keeps the two rows' different printed extras (KISSsoft x*m, Hexagon s) apart.
- The mutation test for the thickness also asserts that the x = 0 case agrees, so its docstring claim is checked, not only stated.
- **Filed items:** no debt or idea item was filed.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] R1 does not turn the tip comparison red**
- **Found during:** Task 3 (R1, `ADDENDUM_FACTOR` 0.45 to 0.40)
- **Issue:** the plan expects the shift, tip and constant-pin tests to fail. din5480's tip is `d_B - TIP_DIAMETER_OFFSET*m` and never reads `ADDENDUM_FACTOR`, so only the shift inversions (192), the constant pin and the vendor row failed (`194 failed, 387 passed`).
- **Fix:** none to the code; the tip is seen red by its own break (R3, `193 failed`). The R1 row in `bench/RESULTS.md` states the expectation did not hold and why.
- **Files modified:** `bench/RESULTS.md`
- **Commit:** `579fdc4`

**2. [Rule 3 - Blocking] A collect-only acceptance criterion cannot print 0**
- **Found during:** Task 1 acceptance
- **Issue:** `pytest --collect-only -q tests | grep -c shaft_oracle` is required to print 0, but the plan's own required test name `test_the_shaft_oracle_imports_nothing_from_spur` contains that string, so it prints 1.
- **Fix:** read the criterion by its intent. The only match is that test's id; no `tests/shaft_oracle.py::` item is collected (checked by listing the match).
- **Commit:** `5583f0f`

**3. [Rule 1 - Bug] A docstring line starting with `from` broke a line-count criterion**
- **Found during:** Task 1 acceptance (`grep -cE '^(import|from) '` read 3, not 2)
- **Fix:** reflowed the oracle docstring so no prose line begins with `from` (the same hazard 31-RESEARCH Pitfall 3 names for `test_seam.py`'s regex). Count is now 2.
- **Commit:** `5583f0f`

**4. [Rule 3 - Blocking] Import order and `PT013`**
- **Found during:** Task 1 lint (`ruff` rejected `from pytest import approx`)
- **Fix:** `import pytest` and `pytest.approx(...)`, imports sorted.
- **Commit:** `5583f0f`

---

**Total deviations:** 4 auto-fixed (2 Rule 1, 2 Rule 3)
**Impact on plan:** none on production code; the first corrected a plan expectation, the others were wording and lint. All five reds show what the plan wants proved.

## Issues Encountered

None beyond the four deviations.

## Known Stubs

None. `tests/shaft_oracle.py` has no placeholder; din5480's `ASSUMPTION (clause slot)` markers are the stated state until the 31-05 checkpoint (D-06).

## Threat Flags

None. No new endpoint, file access or trust boundary; T-31-05 and T-31-06 are mitigated (R4, R5, and `0.39 s` serial time).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- 31-03 can extend `tests/shaft_oracle.py` with the pin measurement, contact diameter and form diameter, and add keys to `ShaftDimensions` before `warnings`.
- The anchor rows from the copy still do not exist in the repo; they arrive after the 31-05 checkpoint, in 31-06.

## Self-Check: PASSED

Files found: `tests/shaft_oracle.py`, `tests/test_din5480.py`, `bench/RESULTS.md`, the five `31-02-red-*.log` files. Commits found: `5583f0f`, `092a17b`, `579fdc4`.

---
*Phase: 31-shaft-maths-parameters-and-designation*
*Completed: 2026-10-24*
