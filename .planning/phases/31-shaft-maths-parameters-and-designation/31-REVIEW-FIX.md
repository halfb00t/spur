---
phase: 31-shaft-maths-parameters-and-designation
fixed_at: 2026-10-26T00:00:00Z
review_path: .planning/phases/31-shaft-maths-parameters-and-designation/31-REVIEW.md
iteration: 1
findings_in_scope: 5
fixed: 5
skipped: 0
status: all_fixed
---

# Phase 31: Code Review Fix Report

**Fixed at:** 2026-10-26
**Source review:** .planning/phases/31-shaft-maths-parameters-and-designation/31-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 5 (WR-01..WR-05; no critical; IN-01..IN-05 out of scope)
- Fixed: 5
- Skipped: 0

Every fix ships with its test in the same commit. Each new or changed test was run against the unfixed code first and failed (red), and passed after the fix. `PYTHONDONTWRITEBYTECODE=1` was set and `__pycache__` purged before each red/green run.

## Fixed Issues

### WR-01: The refusal message contradicts itself near the range edges

**Files modified:** `src/spur/shaft_calc.py`, `tests/test_shaft_params.py`
**Commit:** d523089
**Applied fix:** `check_shaft` prints the shift with `{x:+.4f}` and says "above" or "below" the allowed range. `X_MIN`, `X_MAX` and `X_EPS` are unchanged. The new test has four rows: 25.05 and 24.95 (the ordinary cases) plus 25.001 (upper) and 24.999 with 19 teeth (lower). Each asserts the printed shift is a different number from the edge and that the side is named. Red: 4 failed. Green: 4 passed.
**Residual:** an overshoot smaller than 0.00005 (for example reference_d 25.00001) still prints as `+0.4500` with the word "above". The side word keeps the message honest. I did not add adaptive precision, to stay inside the brief.

### WR-02: `measure_over_pins` is printed next to a fit designation but is the nominal-thickness measure, and no warning says so

**Files modified:** `src/spur/shaft_calc.py`, `tests/test_shaft_calc.py`
**Commit:** f41dada
**Applied fix:** New `MEASURE_AT_NOMINAL_THICKNESS` warning ("M_Re is the measure at the nominal tooth thickness; it carries no allowance or tolerance for the fit."), emitted whenever `measure_over_pins` is non-null and absent when it is null (the odd-count test pins the absence). It is pinned in `test_the_default_shaft_prints_its_pin_and_measure_over_pins`, and in the default-dimensions test whose warnings tuple had to change. The comment cites the 0.091 mm gap, checked against `tests/test_din5480_anchors.py` (nominal 6.271 against the row's 6.180). Red: 2 failed. Green: all pass. No number changes.
**Status note:** this is a wording and warning change with no logic branch beyond "measure is not None", so it is not flagged for human verification.

### WR-03: The `root_d` warning names only hobbing; the copy names more processes

**Files modified:** `src/spur/shaft_calc.py`, `tests/test_shaft_calc.py`
**Commit:** 43e87f2
**Applied fix:** Wording only. The existing hobbed 0.1*m sentence and its computed value are kept. A sentence is appended that says the list is not complete, that the standard names root depths for other processes (DIN 5480-1 cl. 7.1), and that this tool gives none of them. The `root_d` field description says the same. No other dedendum factor or depth appears in code, comments, warnings or tests (T-31-13). A new test pins that the only numbers in the warning are the hobbed 0.1*m and the printed hobbed root. Red: 5 failed. Green: all pass.

### WR-04: `DesignationError` cannot be pickled, copied or re-raised across a process boundary

**Files modified:** `src/spur/din5480.py`, `tests/test_din5480.py`
**Commit:** f8595ec
**Applied fix:** `super().__init__(token, message)`, plus `self.message` and `__str__` returning the message, as the review suggested. The existing refusal test now round-trips every refused designation (25 rows) through `pickle`, `copy.copy` and `copy.deepcopy`, asserting the type, the token and the text. Red: 25 failed. Green: all pass. The text a caller sees is unchanged.

### WR-05: `parse_designation` accepts leading zeros in the number tokens but refuses them in the fit; its docstring says otherwise

**Files modified:** `src/spur/din5480.py`, `tests/test_din5480.py`
**Commit:** 8e4abe4
**Applied fix:** Chose "exactly the canonical form". `_TEETH = [1-9][0-9]*` and `_NUMBER = (?:0|[1-9][0-9]*)(?:[.,][0-9]+)?`. A lone `0` integer part stays valid because ShaftParams allows module 0.5 (`W 3.75x0.5x6x8f` is pinned as accepted). The tooth count `0` is now refused by the parser rather than by the bound check, and the three refusal messages say "without leading zeros". Trailing zeros after the point (`25.0`, `1.250`) remain accepted, and the docstring and a new accepted-variant row say so. Six refused rows were added (leading zeros in reference diameter, module, both before the point, and teeth; zero teeth; the fit's `08f`). Red: 5 failed (the fit row was already green). Green: all pass.
**Status note:** the review classes this as a rule decision, not a logic bug, and the rule was chosen by the brief. It is reported as fixed.

## Verification

Gates ran in the **main checkout** (`use_worktrees` is false in `.planning/config.json`), not an isolated worktree, so the numbers are reproducible from this tree.

- `make verify`: exit status 0. Ruff "All checks passed!", mypy "Success: no issues found in 65 source files", import contracts, the unfinished-work scan and `gear.unchanged` ran inside it. pytest result line: `======================= 2368 passed in 202.37s (0:03:22) =======================`
- `make gear.unchanged` (run again alone): exit status 0. `gear.unchanged: tests/regression/, .github/workflows/ci.yml and /api/schema (8723 bytes) are byte-equal to v0.6`
- No default changed (L05). Each commit also passed the repo's `make verify.fast` pre-commit hook.

---

_Fixed: 2026-10-26_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
