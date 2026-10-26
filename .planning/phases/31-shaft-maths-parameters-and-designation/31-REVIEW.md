---
phase: 31-shaft-maths-parameters-and-designation
reviewed: 2026-10-26T00:00:00Z
depth: standard
files_reviewed: 6
files_reviewed_list:
  - docs/tech_debt/active/2026-10-26-shaft-shift-range-narrower-than-din-5480-exceptions.md
  - src/spur/din5480.py
  - src/spur/shaft_calc.py
  - src/spur/shaft_params.py
  - tests/test_shaft_calc.py
  - tests/test_shaft_params.py
findings:
  critical: 0
  warning: 0
  info: 3
  total: 3
status: issues_found
---

# Phase 31: Code Review Report (re-review of the WR-06, IN-01..IN-06 fixes)

**Reviewed:** 2026-10-26
**Depth:** standard
**Files Reviewed:** 6
**Status:** issues_found

## Summary

Scope: diff `0100a12..HEAD` in the six listed files (fix commits 8c6a11b..36ec101). I ran `tests/test_shaft_calc.py`, `tests/test_shaft_params.py` and `tests/test_din5480.py`: 1006 passed. I did not re-run `make verify`.

WR-06 and IN-01..IN-06 hold, so they are not re-listed. I probed the WR-06 fix directly:

- `reference_d` 25.000001 refuses at `+0.450000400`.
- `reference_d` 24.99999999 with 19 teeth refuses at `-0.050000004`.
- `module` 1.2499999 prints as `1.2499999`, not `1.25`.
- Nudges inside the 1e-9 epsilon are accepted.
- Every refusal names the side, and the shift never prints as the edge.

T-31-13: the diff adds no DIN 5480 table value or clause text. The only new number is 0.60, which `din5480.py` already records, and the code derives 0.1 from it. L05: no default or bound changed. L08: no printed number changed. The `root_d` description prints "0.1*m" from the constant, as before.

The three new items are Info. They are leftovers of the IN-03, IN-04 and WR-06 fixes, and none produces a wrong number.

## Info

### IN-07: `THEORETICAL_PIN` still says "M_Re is for this pin" for an odd tooth count, where no M_Re is printed

**File:** `src/spur/shaft_calc.py:43-47, 224-225`
**Issue:** The IN-03 fix gates the sentence on `reading.pin_d is None`. Its comment says the sentence "would contradict" `pin_measurement`'s "M_Re and D_Re not given". The same contradiction remains for an odd tooth count. There `pin_measurement` returns `PinReading(pin_d, None, (ODD_Z_UNCONFIRMED,))`. `measure_over_pins` is null, `ODD_Z_UNCONFIRMED` says "M_Re is not given", and `THEORETICAL_PIN` still ends "and M_Re is for this pin". `tests/test_shaft_calc.py::test_an_odd_tooth_count_prints_the_pin_and_no_measure_over_pins` asserts both sentences are present, so a test now pins the contradiction. `MEASURE_AT_NOMINAL_THICKNESS` is already gated on `reading.measure`, so the two sentences use different gates for the same fact.
**Fix:** Split the clause out of `THEORETICAL_PIN` and gate it on the measure:
```python
THEORETICAL_PIN = ("... The tool computes this pin; it has not been compared with a "
                   "tabulated D_Re.")
M_RE_FOR_THIS_PIN = "M_Re is for this pin."
...
*(() if reading.measure is None else (MEASURE_AT_NOMINAL_THICKNESS, M_RE_FOR_THIS_PIN))
```
Or fold "M_Re is for this pin" into `MEASURE_AT_NOMINAL_THICKNESS`. Update the odd-count test to assert it is absent.

### IN-08: The `module` branch of `_exact` has no test, and the hobbed-root test indexes `warnings[2]`

**File:** `tests/test_shaft_params.py:168-193`, `tests/test_shaft_calc.py:261-269`
**Issue:**
1. The WR-06 rows vary only `reference_d`, and the regex checks only the reference diameter. `_exact(p.module)` is the same code path, but nothing fails if it is reverted to `{p.module:g}`. I confirmed `module=1.2499999` refuses with "module 1.2499999" today. Only the diameter is covered.
2. `test_the_root_warning_prints_the_factor_the_value_is_computed_from` reads `derive_shaft(...).warnings[2]`. That is the root warning only while `FORM_DIAMETER_UNPROVEN` and `THEORETICAL_PIN` stay first. After IN-07 or any reordering it would silently assert on another sentence, and `warning.count("0.2*m") == 2` would then fail with a misleading message.
**Fix:**
1. Add a row, or a small separate test, with `module=1.2499999`, `teeth=18`, `reference_d=25`, asserting `"module 1.2499999 "` is in the message and the printed shift differs from `X_MAX`.
2. Select by content: `next(w for w in warnings if "hobbed" in w)`.

### IN-09: `H_FP_HOBBING` is a second hand-copied 0.60, outside the constants block

**File:** `src/spur/shaft_calc.py:63-69`
**Issue:** The IN-04 fix derives `HOBBED_ROOT_DROP` from `H_FP_HOBBING = 0.60`. That 0.60 lives in `shaft_calc.py`, while `din5480.py` holds only a comment that says 0.60 ("One constants block. Each line carries unit, source ..."; formulas live in `din5480.py`). Nothing ties the two. `din5480.H_FP` is a live constant and `H_FP_HOBBING` is a copy of a comment, so editing the comment moves nothing. The `== 0.1` test anchors the result, which is the real protection. Also, if `din5480.H_FP` is ever set to 0.60, `HOBBED_ROOT_DROP` becomes 0 and the sentence reads "0*m smaller ... root_d - 0*m". That reads as a bug and not as "the root now is the hobbed root".
**Fix:** Move `H_FP_HOBBING = 0.60` into the `din5480.py` constants block next to `H_FP`, with the same source line, and import it. Or add a comment in `shaft_calc.py` saying that a change to `din5480.H_FP` must revisit this constant.

---

_Reviewed: 2026-10-26_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
