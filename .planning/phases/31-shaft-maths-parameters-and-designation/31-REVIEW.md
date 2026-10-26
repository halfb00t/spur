---
phase: 31-shaft-maths-parameters-and-designation
reviewed: 2026-10-26T00:00:00Z
depth: standard
files_reviewed: 5
files_reviewed_list:
  - src/spur/din5480.py
  - src/spur/shaft_calc.py
  - tests/test_din5480.py
  - tests/test_shaft_calc.py
  - tests/test_shaft_params.py
findings:
  critical: 0
  warning: 1
  info: 6
  total: 7
status: issues_found
---

# Phase 31: Code Review Report (re-review of the WR-01..WR-05 fixes)

**Reviewed:** 2026-10-26
**Depth:** standard
**Files Reviewed:** 5
**Status:** issues_found

## Summary

Scope: the diff from `95adafb` to HEAD in the five listed files (commits d523089, f41dada, 43e87f2, f8595ec, 8e4abe4). IN-01 concerns a debt doc outside the list. I also re-read `src/spur/shaft_params.py` for IN-05.

WR-02, WR-03, WR-04 and WR-05 hold.

- **WR-02:** `MEASURE_AT_NOMINAL_THICKNESS` is emitted exactly when `measure_over_pins` is non-null. The odd-count test pins its absence.
- **WR-03:** the added sentence names no other dedendum factor or depth, and the test pins the only numbers in it.
- **WR-04:** `args == (token, message)`, so `pickle`, `copy.copy` and `copy.deepcopy` rebuild the exception. The test round-trips all 25 refused rows.
- **WR-05:** I probed the new patterns. Leading zeros are refused in every number token. The lone `0` before the point still parses, as `W 3.75x0.5x6x8f` needs. A trailing newline or space is refused (`8f\n`, `8f `). `0f` is refused.

WR-01 is only partly fixed. Four decimals plus the side word cure the 0.001 case but not the smaller overshoots. I reproduced the message still contradicting itself (WR-06). That is a new id, because the fix is incomplete.

T-31-13: nothing in the diff adds a DIN 5480 table value or clause text. The new wording only cites "cl. 7.1" and says other processes exist. The test comment states the rule. No violation.

L05: no default or bound changed. L08: no new printed number. The one new sentence (`MEASURE_AT_NOMINAL_THICKNESS`) only qualifies an existing number.

## Warnings

### WR-06: The shift refusal still contradicts itself for an overshoot under 0.00005, and `{reference_d:g}` hides the nudge

**File:** `src/spur/shaft_calc.py:145-150`
**Issue:** The WR-01 fix prints `{x:+.4f}`. `check_shaft` refuses anything beyond the edge by more than `X_EPS = 1e-9`. So any overshoot in (1e-9, 5e-5) rounds to the edge digits. REVIEW-FIX.md records this residual and says the side word keeps the message honest. I reproduced it:

```
ShaftParams(reference_d=25.0001)
  -> "A reference diameter of 25.0001 mm ... needs a profile shift of +0.4500, above the allowed range -0.05 to +0.45."
ShaftParams(reference_d=25.00001)
  -> "A reference diameter of 25 mm ... needs a profile shift of +0.4500, above the allowed range -0.05 to +0.45."
```

The second is worse than the residual says. `{p.reference_d:g}` keeps six significant digits, so the message names "25 mm", the default, as the refused input. The user is told that 25 mm needs +0.4500 and that +0.4500 is above +0.45. Nothing says which way to move or by how much.

This is the same defect as WR-01 at a smaller scale. The refusal is the only explanation the L03 path gives. The default shaft sits on the edge, and the API and shareable links accept any float, not only the form's 0.05 steps. It is not Info. The side word does not rescue it, because the numbers beside it still read as equal. No wrong part is produced.

The new test cannot catch this. Its smallest nudge is 0.001 (shift +0.4504), so it passes while the 0.0001 and 0.00001 rows stay broken.
**Fix:** Print enough digits to separate the shift from the edge, and print the input as given.

```python
side = "above" if x > din5480.X_MAX else "below"
edge = din5480.X_MAX if side == "above" else din5480.X_MIN
shown = f"{x:+.4f}"
if float(shown) == edge:                 # rounds onto the edge: show the overshoot
    shown = f"{x:+.9f}"
...
f"A reference diameter of {p.reference_d!r} mm ..." # repr, not :g
```

Add rows to `test_a_refused_shift_is_printed_apart_from_the_edge_it_crossed_and_names_the_side` for `reference_d=25.0001` and `25.00001`, asserting the printed shift differs from the edge and that the printed reference diameter is not `25`.

## Info

### IN-01: Debt items point at stale line numbers

**File:** `docs/tech_debt/active/2026-10-26-shaft-shift-range-narrower-than-din-5480-exceptions.md:8-9` (Related files)
**Issue:** Still stale, and worse than before. It cites `src/spur/din5480.py:34 (X_MAX)` and `src/spur/shaft_calc.py:105 (check_shaft)`. Now `X_MAX` is at `din5480.py:40` and `check_shaft` is at `shaft_calc.py:132` (it was 119 at the last review; the fix commits moved it again). The line numbers drift on every edit to these files.
**Fix:** Cite by symbol (`din5480.X_MAX`, `shaft_calc.check_shaft`), not by line.

### IN-02: Stale module docstring in `tests/test_shaft_calc.py`

**File:** `tests/test_shaft_calc.py:3-4`
**Issue:** Unchanged. It still says "The formulas are ASSUMPTIONS until the 31-05 checkpoint records their clauses". The checkpoint has run and `din5480.py` cites clauses for the tip, root, shift and thickness. The docstring understates what the tests pin.
**Fix:** Reword to name what is still unconfirmed (pin, M_Re, form diameter) and point at `tests/test_din5480_anchors.py`.

### IN-03: `THEORETICAL_PIN` makes a claim no seen page supports, and stays when the pin is null

**File:** `src/spur/shaft_calc.py:43-47, 215`
**Issue:**
1. The text says "It is not the D_Re that DIN 5480 tabulates." The 31-05 checkpoint (D4) records that Part 1 shows no such tabulation, so the claim is unverified against any page the project has seen.
2. `derive_shaft` appends `THEORETICAL_PIN` unconditionally (line 215), even when `reading.pin_d` is None and `pin_measurement` has already said "M_Re and D_Re not given". After the WR-02 fix this is inconsistent inside one tuple. `MEASURE_AT_NOMINAL_THICKNESS` is gated on `reading.measure`, while `THEORETICAL_PIN` ("M_Re is for this pin") is not gated on anything. Unreachable today, reachable in Phase 34.
**Fix:** Say "the tool computes this pin; it has not been compared with a tabulated D_Re". Gate it the same way: `pin_warnings = () if reading.pin_d is None else (THEORETICAL_PIN,)`.

### IN-04: The 0.1*m drop is written twice and `HOBBED_ROOT_DROP` is not tied to `H_FP`

**File:** `src/spur/shaft_calc.py:63, 69-72, 104-108`
**Issue:** `HOBBED_ROOT_DROP = 0.1` feeds the computed value, but the sentence hard-codes "0.1*m" twice (lines 70-71). The `root_d` field description (lines 105-106) now says it a third time. The constant is also independent of `H_FP = 0.55` and the 0.60 in `din5480.py`. The new WR-03 test hard-codes `["0.1", "0.1", "22.125"]`, so a change to the constant fails the test in a way that looks like a regression. Changing one place leaves the others wrong.
**Fix:** Format the factor into the sentence and the field description from `HOBBED_ROOT_DROP`. Or state the coupling in a comment next to the constant.

### IN-05: The default shaft sits on the range edge, and `shaft_params` imports the gear's private helpers

**File:** `src/spur/shaft_params.py:14-15, 25-31`
**Issue:** Unchanged.
- (a) D-19 put the default exactly on X_MAX. `reference_d` 25.05, `teeth` 17 and `module` 1.2 each refuse, and none of the `reference_d`/`module`/`teeth` `help` strings says so. WR-06 shows how the first nudge off the default reads.
- (b) `from .params import _extra, _f` pulls underscore-private names from the gear module. A rename there would break the shaft with no import-linter signal.
**Fix:** (a) Add "Shifts outside -0.05..+0.45 are refused" to the three `help` strings. (b) Promote `_f` and `_extra` to a shared public helper, or note the coupling in a comment.

### IN-06: The leading-zero comment promises "one spelling per shaft", but five other spellings parse

**File:** `src/spur/din5480.py:188-191`
**Issue:** The comment justifies WR-05's rule with "one spelling per shaft, so a link or a cache key built from the designation text cannot see 25 and 0025 as two shafts". The parser still accepts trailing zeros (`25.0`, `1.250`, `0.50`), `,` for the decimal mark, an upper-case `X` and a missing space after `W`. Each is a deliberate variant, and the docstring and a test row say so. But the comment overstates the guarantee. A Phase 33 author who reads it could key a cache on the raw text. Only `format_designation(*parse_designation(text))` is canonical.
**Fix:** Reword the comment to say that leading zeros are refused so no numeric token has two integer-part spellings, and that a key must be built from `format_designation`, not from the input text.

---

_Reviewed: 2026-10-26_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
