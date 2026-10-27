---
phase: 31-shaft-maths-parameters-and-designation
plan: 03
subsystem: shaft-maths
tags: [din5480, pin-measurement, pin-contact-guard, form-diameter, oracle, seen-red-once]

requires:
  - phase: 31-shaft-maths-parameters-and-designation
    provides: din5480 formulas and ShaftDimensions (31-01), the stdlib oracle and its vendor-row pattern (31-02)
provides:
  - din5480.theoretical_pin_diameter, measure_over_pins, form_diameter, with inv and _involute_angle copied from calc.py
  - shaft_calc.pin_measurement as a function of an explicit pin, pin_contact_window, PinReading, the three sentences
  - ShaftDimensions keys form_d, pin_d, measure_over_pins
  - oracle measure, contact_diameter, form_diameter by tangency search and line-of-action geometry
  - six more guards seen red once, recorded in bench/RESULTS.md
affects: [31-04, 31-05, 31-06, phase-33, phase-34]

plan_head_before: 3f6701c8d7d0618816a56c56d7f2a2c800844bdb
plan_head_after: a2bae21bbaf5dacc813269cac73b11e63ac89592

actuals:
  tokens: 7225    # chars/4 over the added src+tests lines (25151 chars) and the RESULTS rows (3752); the six red logs are evidence, not code
  tasks: 3
  commits: 3      # measured: git rev-list --count 3f6701c..HEAD, before this SUMMARY's own commit

tech-stack:
  added: []
  patterns:
    - "a guard written as a function of an explicit input (pin_measurement(p, pin_d)), so branches the production path cannot reach are covered by direct calls and the comment says when they go live"
    - "the oracle recomputes every pin quantity by geometry (tangency search, line of action), never by the closed form it checks"

key-files:
  created:
    - .planning/phases/31-shaft-maths-parameters-and-designation/investigation/31-03-red-odd-factor.log
    - .planning/phases/31-shaft-maths-parameters-and-designation/investigation/31-03-red-contact.log
    - .planning/phases/31-shaft-maths-parameters-and-designation/investigation/31-03-red-guard-swapped.log
    - .planning/phases/31-shaft-maths-parameters-and-designation/investigation/31-03-red-unrounded-pin.log
    - .planning/phases/31-shaft-maths-parameters-and-designation/investigation/31-03-red-odd-gate.log
    - .planning/phases/31-shaft-maths-parameters-and-designation/investigation/31-03-red-form-printed.log
  modified:
    - src/spur/din5480.py
    - src/spur/shaft_calc.py
    - tests/shaft_oracle.py
    - tests/test_din5480.py
    - tests/test_shaft_calc.py
    - bench/RESULTS.md

key-decisions:
  - "Gauge step 0.01 mm (PIN_DECIMALS = 2), D-11's default: 31-RESEARCH A4 found no documented series for a theoretical pin; the 31-05 checkpoint asks whether the copy names one"
  - "Guard margin 0.1*m on both ends (GUARD_MARGIN_FACTOR): 1.5 times the larger of the two observed gaps (Hexagon 0.030 mm = 0.01*m, KISSsoft 0.202 mm = 0.067*m, both at m 3); scaling with m is an assumption"
  - "form_d is None for every shaft; the construction exists only as the guard's lower bound and no ShaftDimensions value equals it"
  - "Odd z prints its pin and no M_Re (ODD_Z_UNCONFIRMED) until a DIN 5480 row confirms the cos(pi/(2z)) formula, which is built and oracle-tested"

requirements-completed: [REQ-mre-nominal, REQ-form-diameter-honest]

coverage:
  - id: D1
    description: "The default shaft prints D_Re 2.73 and M_Re 27.999 with the theoretical-pin note, and d_Ff null with its sentence; W25x1.25x19 prints pin 2.36 and no M_Re"
    requirement: "REQ-mre-nominal"
    verification:
      - kind: unit
        ref: "tests/test_shaft_calc.py#test_the_default_shaft_prints_its_pin_and_measure_over_pins"
        status: pass
      - kind: unit
        ref: "tests/test_shaft_calc.py#test_an_odd_tooth_count_prints_the_pin_and_no_measure_over_pins"
        status: pass
      - kind: unit
        ref: "tests/test_shaft_calc.py#test_the_form_diameter_is_null_with_its_reason_for_every_shaft"
        status: pass
    human_judgment: true
    rationale: "The pin and M_Re formulas are ASSUMPTIONS agreeing with an independent geometric oracle and two vendor reports; whether DIN 5480 measures this way is the 31-05 checkpoint's question, and the odd-z formula has no copy row"
  - id: D2
    description: "M_Re and the contact diameter agree with the oracle over 72 even and odd cases (M at 1e-9, contact at 2e-6); the theoretical pin touches on m*z + 2*x*m; Hexagon and KISSsoft rows pass as labelled cross-checks"
    requirement: "REQ-mre-nominal"
    verification:
      - kind: unit
        ref: "tests/test_din5480.py#test_the_measure_over_pins_agrees_with_the_oracle_for_even_and_odd_teeth"
        status: pass
      - kind: unit
        ref: "tests/test_din5480.py#test_the_theoretical_pin_touches_on_the_shifted_reference_circle"
        status: pass
      - kind: unit
        ref: "tests/test_din5480.py#test_the_measure_over_pins_matches_the_vendor_cross_checks"
        status: pass
      - kind: unit
        ref: "tests/test_din5480.py#test_the_oracle_refuses_a_mutated_odd_z_factor"
        status: pass
    human_judgment: false
  - id: D3
    description: "The pin-contact guard is a function of an explicit pin; its closed window and its null branches are covered by direct calls; the internal form diameter agrees with the oracle and KISSsoft and its Hexagon gap is pinned at 0.030 mm"
    requirement: "REQ-form-diameter-honest"
    verification:
      - kind: unit
        ref: "tests/test_shaft_calc.py#test_the_pin_contact_guard_nulls_a_pin_off_the_flank"
        status: pass
      - kind: unit
        ref: "tests/test_shaft_calc.py#test_the_pin_contact_window_is_closed"
        status: pass
      - kind: unit
        ref: "tests/test_din5480.py#test_the_internal_form_diameter_agrees_with_the_oracle_and_the_vendors"
        status: pass
      - kind: unit
        ref: "tests/test_din5480.py#test_a_pin_that_cannot_touch_the_involute_has_no_measure"
        status: pass
    human_judgment: true
    rationale: "The margin is sized from two vendor gaps at one module (an assumption); the guard cannot fire from derive_shaft until Phase 34 passes the copy's D_Re"
  - id: D4
    description: "Six guards seen red once (odd-z factor, contact sign, guard bounds, pin rounding, odd-z gate, form diameter printed), reverted and recorded"
    verification:
      - kind: other
        ref: "bench/RESULTS.md ### Seen red once (Phase 31), six 31-03 rows; investigation/31-03-red-*.log"
        status: pass
    human_judgment: false

duration: 9min
completed: 2026-10-24
status: complete
---

# Phase 31 Plan 03: Pins, Measure Over Pins and an Honest Form Diameter Summary

**The default shaft prints D_Re 2.73 and M_Re 27.999 from a closed-form theoretical pin rounded to 0.01 mm, an odd tooth count prints its pin and no M_Re, d_Ff stays null, and a pin-contact guard over an explicit pin waits for Phase 34, with 72-case oracle agreement and six mutations seen red once**

## Performance

- **Duration:** 9 min
- **Started:** 2026-10-24T11:13:31Z
- **Completed:** 2026-10-24T11:22Z (before this SUMMARY's own commit)
- **Tasks:** 3
- **Files modified:** 12 (2 source, 3 test, `bench/RESULTS.md`, 6 logs)

## Accomplishments

- `derive_shaft(ShaftParams())` returns `pin_d` 2.73, `measure_over_pins` 27.999, `form_d` None and warnings `(FORM_DIAMETER_UNPROVEN, THEORETICAL_PIN)`; `derive_shaft(ShaftParams(teeth=19))` returns pin 2.36, no M_Re and `ODD_Z_UNCONFIRMED` as well.
- `pin_measurement(p, pin_d)` nulls a pin that does not touch the involute and a pin whose contact leaves the closed window `[internal d_Ff + 0.1*m, d_a - 0.1*m]`; it is reached only by direct calls until Phase 34, and its comment says so.
- `tests/shaft_oracle.py` (still `math` only, two import lines) rebuilds the measure and the contact by tangency search against the mirrored parametric involute, and the form diameter by the line of action. Six guards were seen red once.

## Measurements

- **Gauge step:** 0.01 mm (`PIN_DECIMALS = 2`), D-11's default. Source: 31-RESEARCH A4 found no documented series for a theoretical pin (the vendors' effective pins are round values, 6.000 and 5.500). A change after the 31-05 checkpoint is a decision, not an edit.
- **Guard margin:** `GUARD_MARGIN_FACTOR = 0.1`, times m, on both ends. Sizing: Hexagon's printed 113.91 sits 0.030 mm above the construction's 113.880 (0.01*m at m 3; measured in the test, 0.0298), KISSsoft's two values for one shaft differ by 0.202 mm (0.067*m); 1.5 times the larger is 0.1*m. Scaling with m is an assumption, both gaps are at m 3. D-20's reading: the theoretical pin's contact sits at least 0.62*m above the internal d_Ff and 0.886*m below d_a, so the margin costs nothing until Phase 34.
- **Worst disagreement over the 72-case grid (din5480 against the oracle):**

  | Quantity | Worst abs difference | Tolerance set |
  |---|---|---|
  | M_Re at the rounded pin | 2.27e-13 | 1e-9 |
  | contact diameter at the rounded pin | 5.14e-7 | 2e-6 (`CONTACT_ABS`) |
  | oracle contact at the unrounded theoretical pin against `m*z + 2*x*m` | 6.97e-7 | 2e-6 |
  | internal form diameter, h_fP 0.55 and 0.60 | 1.14e-13 | 1e-9 |

  The contact figure is limited by the oracle's golden-section search, which finds the touching point to about the square root of machine epsilon; 2e-6 is 2.9 times the larger reading and under the plan's 1e-5 stop line.
- **Serial wall time of `tests/test_din5480.py`:** `/usr/bin/time -p`, `real 2.19` s with `--no-cov -n0` (729 passed), against the plan's 10 s limit.
- **Branch coverage** of `din5480.py`, `shaft_calc.py` and `shaft_params.py`: 100.00 % each.
- **Gate:** `make verify`: `2308 passed in 204.62s (0:03:24)`, `real 3:25.84`, exit 0, at the final tree before this SUMMARY. 31-02's gate was `2012 passed`, `220.13s`; load at the end of this run was 10.1 on 1 minute (`uptime`), against 18.5 for 31-02, so the 16 s difference is not claimed as a saving. 31-06 prices the phase's gate delta.
- Plan-level checks: `make lint-imports` reads `Contracts: 10 kept, 0 broken.`; `make gear.unchanged` reads `gear.unchanged: tests/regression/, .github/workflows/ci.yml and /api/schema (8723 bytes) are byte-equal to v0.6`; `make verify.fast` passed at each of the three commits; `git status --porcelain -- src tests` is empty; the `bench/RESULTS.md` commit deletes 0 lines (`6 0`).

## Task Commits

1. **Task 1 (tracer): the pin, the measurement over pins and an honest form diameter** - `9729178` (feat)
2. **Task 2: pins, contact and form diameter against the oracle; the guard by direct call** - `0951b63` (test)
3. **Task 3: the pin and form-diameter guards seen red once** - `a2bae21` (docs)

The tracer gate: the tracer's `<verify>` is automated-only and `human_verify_mode` is `end-of-phase`; its checks (pytest `650 passed`, mypy, ruff, `make no-fake-done`, contracts) had passed at the commit and the same suite ran green again (`880 passed`) with Task 2's edits before they were committed. `Tracer verified end-to-end` and expansion went ahead.

## Files Created/Modified

- `src/spur/din5480.py` - `inv`, `_involute_angle` (copies of calc.py's, never imported), `theoretical_pin_diameter`, `measure_over_pins`, `form_diameter`
- `src/spur/shaft_calc.py` - `PIN_DECIMALS`, `GUARD_MARGIN_FACTOR`, `FORM_DIAMETER_UNPROVEN`, `THEORETICAL_PIN`, `ODD_Z_UNCONFIRMED`, `PinReading`, `pin_contact_window`, `pin_measurement`, keys `form_d`, `pin_d`, `measure_over_pins`; `derive_shaft` copies the reading without a branch
- `tests/shaft_oracle.py` - `measure`, `contact_diameter`, `form_diameter` and their private flank and search helpers
- `tests/test_din5480.py` - `M_GRID`, `CONTACT_ABS` and six tests
- `tests/test_shaft_calc.py` - six new tests; the default-dimensions test reads the two new sentences
- `bench/RESULTS.md` - six `31-03` rows appended, none removed
- `.planning/phases/31-shaft-maths-parameters-and-designation/investigation/31-03-red-*.log` - six whole red logs

## Decisions Made

- The test count in each red run: odd-factor `24 failed, 856 passed` (the 24 odd grid cases fail, the 48 even ones pass); contact `150 failed`; guard-swapped `77 failed`; unrounded-pin `74 failed`; odd-gate `25 failed`; form-printed `73 failed`. Every run kept the 31-01 method: `PYTHONDONTWRITEBYTECODE=1`, `__pycache__` purged before the run and after each revert.
- The contact tolerance is a measured one, not a guess: the oracle's golden section limits it, and the measure, which does not depend on the touching point, keeps 1e-9.
- **Phase 34 handoff:** the copy's tabulated D_Re replaces the computed pin where the tables give one, and a warning says it changed; that is an output number, not a parameter, so L05 does not apply. The guard goes live then (the copy's 6.000 pin at m 3 touches at 116.78 against d_Ff 113.88 and d_a 119.40). `THEORETICAL_PIN` is replaced with it. The three `ShaftDimensions` keys are Phase 33's dims rows.
- **Filed items:** no debt or idea item was filed.

## Deviations from Plan

### Auto-fixed Issues

None - plan executed exactly as written, with these wording choices the plan did not fix:

- The sentence constants, the null-guard sentences and the window format (`{low:.3f} to {high:.3f} mm`) are mine; the facts the plan lists are all in them.
- `test_the_internal_form_diameter_agrees_with_the_oracle_and_the_vendors` loops the grid inside one test, as its single name implies, so `-k form` reports 73 passed (that test plus 72 null-form cases) and `-k mutat` reports exactly 3.
- `tests/test_shaft_calc.py` imports `M_GRID` from `test_din5480`, as the plan asks for M_GRID shafts there; `tests/` is on the path and mypy and ruff accept it.
- R3's first failure line is the default shaft's dimensions test (the inverted window nulls every pin and the sentence lands in `warnings`), not a guard test; the guard tests are in the same run.

**Total deviations:** 0 auto-fixed. **Impact on plan:** none.

## Issues Encountered

None.

## Known Stubs

None. The `ASSUMPTION (clause slot)` markers in `din5480.py` are the stated state until the 31-05 checkpoint (D-06); `pin_measurement`'s null branches are real, covered code that Phase 34 makes reachable, not placeholders.

## Threat Flags

None. No new endpoint, file access or trust boundary; T-31-07 (copied bracketed bisection, None outside `(0, inv(89 deg))` and below the base circle, 72-case oracle grid, R2 seen red) and T-31-08 (`form_d` always None, odd-z gate, M_Re recomputed for the printed pin; R4, R5, R6 seen red) are mitigated.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- 31-04 inserts the `designation` key before `warnings`, after the three keys added here.
- 31-05's checkpoint prediction table can read the pin, M_Re and contact columns from this plan's code; open for the human there: the gauge step, whether the odd-z formula and the form-diameter construction match a copy row, and h_fP.

## Self-Check: PASSED

Files found: `src/spur/din5480.py`, `src/spur/shaft_calc.py`, `tests/shaft_oracle.py`, `tests/test_din5480.py`, `tests/test_shaft_calc.py`, `bench/RESULTS.md`, the six `31-03-red-*.log` files. Commits found: `9729178`, `0951b63`, `a2bae21`.

---
*Phase: 31-shaft-maths-parameters-and-designation*
*Completed: 2026-10-24*
