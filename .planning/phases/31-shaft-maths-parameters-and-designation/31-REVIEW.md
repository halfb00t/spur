---
phase: 31-shaft-maths-parameters-and-designation
reviewed: 2026-10-26T00:00:00Z
depth: standard
files_reviewed: 4
files_reviewed_list:
  - src/spur/din5480.py
  - src/spur/shaft_calc.py
  - tests/test_shaft_calc.py
  - tests/test_shaft_params.py
findings:
  critical: 0
  warning: 0
  info: 2
  total: 2
status: issues_found
---

# Phase 31: Code Review Report (re-review of the IN-07, IN-08, IN-09 fixes)

**Reviewed:** 2026-10-26
**Depth:** standard
**Files Reviewed:** 4
**Status:** issues_found

## Summary

Scope: diff `63172e7..HEAD` in the four listed files (commits 4ee29af, ae7bbfc, a2d125c). I ran `tests/test_shaft_calc.py tests/test_shaft_params.py tests/test_din5480.py`: `1007 passed in 6.87s`, one more than last round (the new module test). I did not run `make verify`.

IN-07, IN-08 and IN-09 hold, so they are not re-listed.

- **IN-07:** `THEORETICAL_PIN` ends at "tabulated D_Re." "M_Re is for this pin" now lives only in `MEASURE_AT_NOMINAL_THICKNESS`, which is gated on `reading.measure`. I checked z = 17, 18 and 19 at m 1.25 through `derive_shaft`:
  - Odd z: FORM, THEORETICAL_PIN, hobbed, ODD_Z_UNCONFIRMED. No "M_Re is for this pin".
  - Even z: FORM, THEORETICAL_PIN, hobbed, MEASURE_AT_NOMINAL_THICKNESS.
  - The list length and order are unchanged.
  - Odd and even wording now agree: the pin sentence says nothing about M_Re in either case. The M_Re sentence is either the measure qualifier or "not given".
  - No stale copy of the old strings is left in `src/`, `docs/` or the tests (grep).
- **IN-08:** `module=1.2499999` refuses with "module 1.2499999 and 18 teeth needs a profile shift of +0.450000800". The test would catch a revert to `{p.module:g}`, which prints "module 1.25 and". `_hobbed_warning` selects by content, and no test reads `warnings[2]` any more.
- **IN-09:** `H_FP_HOBBING = 0.60` sits in the `din5480.py` constants block. `HOBBED_ROOT_DROP` derives from both module constants. The test pins 0.60, 0.1 and `> 0`.

Project rules on the diff:

- **T-31-13:** no new table value or clause text. The new `din5480.py` comment cites "DIN 5480-1:2006, cl. 6, Table 3 and cl. 7.1", which is the same citation as `H_FP`'s existing comment. That comment already recorded "0.60 is hobbing". The `shaft_calc.py` comment keeps only the cl. 7.1 it cited before, plus the committed 0.60, 0.55 and 0.1. No other number was added.
- **L05:** no default or bound changed.
- **L08:** no printed number changed. The default hobbed root is still 22.125 and W 120x3x38x8f is still 113.100. The `root_d` description still prints `0.1*m`. Only warning text moved, and only to make it more accurate.

The two new items are Info. Both are comments left stale by the IN-07 and IN-09 fixes. Neither changes a number.

## Info

### IN-10: The null-pin test's docstring still gives the pre-IN-07 reason for withholding `THEORETICAL_PIN`

**File:** `tests/test_shaft_calc.py:155-166`
**Issue:** The docstring of `test_no_pin_sentence_is_printed_when_no_pin_is_given` still says the sentence is withheld because "M_Re is for this pin" beside "M_Re and D_Re not given" would contradict itself. After 4ee29af, `THEORETICAL_PIN` contains no "M_Re" at all; `test_the_pin_sentence_says_...` now asserts that. The real reason is that the sentence describes a D_Re that is not printed. 4ee29af updated the matching source comment at `src/spur/shaft_calc.py:225` to "THEORETICAL_PIN would contradict ... 'M_Re and D_Re not given'", but not this docstring. The test body is correct, so only the stated reason is wrong.
**Fix:** Reword the last sentence of the docstring. Optionally, also assert the M_Re sentence is absent, which covers both gates:
```python
    """... null reading is injected: it goes live in Phase 34. A sentence about the printed
    D_Re beside "M_Re and D_Re not given" would contradict itself."""
    ...
    assert THEORETICAL_PIN not in d.warnings
    assert MEASURE_AT_NOMINAL_THICKNESS not in d.warnings
```

### IN-11: `H_FP_HOBBING`'s comment says only the hobbed-root sentence reads it; the `root_d` field description reads it too

**File:** `src/spur/din5480.py:34-35`
**Issue:** The new comment says: "Only shaft_calc's hobbed-root sentence reads it; the root diameter itself uses H_FP." `HOBBED_ROOT_DROP` (`src/spur/shaft_calc.py:70`) feeds two places:
- `hobbed_root_warning`.
- The `ShaftDimensions.root_d` field description (`src/spur/shaft_calc.py:112-117`), which goes into the published JSON schema.

The `shaft_calc.py` comment at lines 64-69 and 31-REVIEW-FIX.md both name both readers. The constants-block comment names one. Someone who edits `H_FP_HOBBING` and trusts this comment will not expect the schema text to change.
**Fix:**
```python
# h_fP/m of hobbing, same source as H_FP above (DIN 5480-1:2006, cl. 6, Table 3 and cl. 7.1).
# Read only through shaft_calc.HOBBED_ROOT_DROP (the hobbed-root warning and the root_d field
# description); the root diameter itself uses H_FP.
```

---

_Reviewed: 2026-10-26_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
