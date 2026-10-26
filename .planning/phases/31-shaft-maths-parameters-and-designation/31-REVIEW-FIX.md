---
phase: 31-shaft-maths-parameters-and-designation
fixed_at: 2026-10-26T11:11:45Z
review_path: .planning/phases/31-shaft-maths-parameters-and-designation/31-REVIEW.md
iteration: 1
findings_in_scope: 7
fixed: 7
skipped: 0
status: all_fixed
---

# Phase 31: Code Review Fix Report

**Fixed at:** 2026-10-26T11:11:45Z
**Source review:** .planning/phases/31-shaft-maths-parameters-and-designation/31-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 7 (WR-06, IN-01..IN-06; no critical)
- Fixed: 7
- Skipped: 0

Behaviour changes (WR-06, IN-03, IN-04, IN-05) ship with their tests in the same commit, and each new or changed test was run against the unfixed code first and failed (red). IN-01, IN-02 and IN-06 are wording or comment only and carry no test. `PYTHONDONTWRITEBYTECODE=1` was set and `__pycache__` purged before the red/green runs.

Verification ran in the main checkout (`workflow.use_worktrees` is false), so the numbers below are reproducible from the tree as it stands.

- `make verify`: exit status 0, final pytest line `2378 passed in 228.23s (0:03:48)`.
- `make gear.unchanged`: exit status 0, `tests/regression/, .github/workflows/ci.yml and /api/schema (8723 bytes) are byte-equal to v0.6`.

T-31-13: no DIN 5480 table value or clause text was added. The only dedendum values in the diff are the committed 0.55 and 0.60. L05: no default changed. Printed numbers did not change (the W 120x3x38x8f hobbed root stays 113.100, the default 22.125), and the `root_d` schema description is byte-equal before and after.

## Fixed Issues

### WR-06: The shift refusal still contradicts itself for an overshoot under 0.00005, and `{reference_d:g}` hides the nudge

**Files modified:** `src/spur/shaft_calc.py`, `tests/test_shaft_params.py`
**Commit:** 8c6a11b
**Applied fix:** The shift prints at four decimals, and at nine when four would round onto the edge, so any overshoot past the 1e-9 epsilon shows (25.00001 now refuses at +0.450004000). The reference diameter and module print as `:g` unless that is a different number, then as repr (new `_exact` helper), so 25.00001 no longer reads as the default 25. Existing messages are unchanged. `X_MIN`, `X_MAX` and the epsilon are untouched. The test gained rows for `reference_d` 25.0001, 25.00001 and 24.99999 (19 teeth), asserting the printed shift differs from the edge and the printed reference diameter equals the input. Three new rows failed before the fix. Logic fix: requires human verification of the wording.

### IN-01: Debt items point at stale line numbers

**Files modified:** `docs/tech_debt/active/2026-10-26-shaft-shift-range-narrower-than-din-5480-exceptions.md`
**Commit:** 570a791
**Applied fix:** The Related files cite `din5480.X_MAX` and `shaft_calc.check_shaft` by symbol, with no line numbers. The INDEX row text needed no change and was left alone.

### IN-02: Stale module docstring in `tests/test_shaft_calc.py`

**Files modified:** `tests/test_shaft_calc.py`
**Commit:** a67b674
**Applied fix:** The docstring now says the tip, root, shift and thickness formulas cite their clauses in `din5480.py`, points at `tests/test_din5480_anchors.py`, and names what is still unconfirmed: the pin diameter D_Re, M_Re and the form diameter d_Ff.

### IN-03: `THEORETICAL_PIN` makes a claim no seen page supports, and stays when the pin is null

**Files modified:** `src/spur/shaft_calc.py`, `tests/test_shaft_calc.py`
**Commit:** 895c4d6
**Applied fix:** The sentence now reads "The tool computes this pin; it has not been compared with a tabulated D_Re, and M_Re is for this pin." `derive_shaft` appends it only when `reading.pin_d` is not None. One test pins the wording and one injects a null `PinReading` (the branch is unreachable until Phase 34) and asserts the sentence is absent. Both failed before the fix. Logic fix: requires human verification of the gating.

### IN-04: The 0.1*m drop is written twice and `HOBBED_ROOT_DROP` is not tied to `H_FP`

**Files modified:** `src/spur/shaft_calc.py`, `tests/test_shaft_calc.py`
**Commit:** bb00e1a
**Applied fix:** Added `H_FP_HOBBING = 0.60` (the value already recorded in `din5480.py`) and derived `HOBBED_ROOT_DROP = round(2 * (H_FP_HOBBING - din5480.H_FP), 3)`, which is 0.1. The warning sentence and the `root_d` field description now format the factor from the constant instead of hard-coding it. A test sets the constant to 0.2 and asserts the sentence prints "0.2*m" twice, no "0.1", and 22.000. It failed before the fix.

### IN-05: The default shaft sits on the range edge, and `shaft_params` imports the gear's private helpers

**Files modified:** `src/spur/shaft_params.py`, `tests/test_shaft_params.py`
**Commit:** a839ffb
**Applied fix:** (a) The `reference_d`, `module` and `teeth` help strings end with "Shifts outside -0.05..+0.45 are refused.", formatted from `X_MIN` and `X_MAX`. A parametrized test over the three fields failed before the fix. (b) A comment marks the import of `_f` and `_extra` from `params.py` as intentional coupling. `src/spur/params.py` was not edited, and `make gear.unchanged` is green.

### IN-06: The leading-zero comment promises "one spelling per shaft", but five other spellings parse

**Files modified:** `src/spur/din5480.py`
**Commit:** 36ec101
**Applied fix:** The comment now says leading zeros are refused so no numeric token has two integer-part spellings, lists the other accepted spellings, says the canonical form is `format_designation`'s output, and says a key must be built from `format_designation(*parse_designation(text))`, never from the input text.

---

_Fixed: 2026-10-26T11:11:45Z_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
