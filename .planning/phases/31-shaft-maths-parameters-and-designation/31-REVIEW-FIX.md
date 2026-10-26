---
phase: 31-shaft-maths-parameters-and-designation
fixed_at: 2026-10-26T12:00:00Z
review_path: .planning/phases/31-shaft-maths-parameters-and-designation/31-REVIEW.md
iteration: 1
findings_in_scope: 3
fixed: 3
skipped: 0
status: all_fixed
---

# Phase 31: Code Review Fix Report

**Fixed at:** 2026-10-26T12:00:00Z
**Source review:** .planning/phases/31-shaft-maths-parameters-and-designation/31-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 3 (IN-07, IN-08, IN-09; no critical, no warning)
- Fixed: 3
- Skipped: 0

Each changed test was run against the unfixed code first and failed (red): IN-07 failed 3 tests (default shaft, odd count, pin sentence), IN-08 failed on a temporary revert of `_exact(p.module)` to `{p.module:g}` (message read "module 1.25 and 18 teeth"), IN-09 failed with an AttributeError on `din5480.H_FP_HOBBING`. The IN-08 revert was undone with `git checkout --` before the commit.

Verification ran in the main checkout (`workflow.use_worktrees` is false), so the numbers below are reproducible from the tree as it stands.

- `make verify`: exit status 0, final pytest line `2379 passed in 211.21s (0:03:31)`.
- `make gear.unchanged`: exit status 0, `tests/regression/, .github/workflows/ci.yml and /api/schema (8723 bytes) are byte-equal to v0.6`.

T-31-13: no DIN 5480 table value or clause text was added. The only dedendum values touched are the committed 0.55 and 0.60, and 0.60 moved from `shaft_calc.py` into `din5480.py` next to `H_FP`. L05: no default changed. L08: no printed number changed. The W 120x3x38x8f hobbed root is still 113.100 (root_d 113.4) and the default's is still 22.125, checked by running `derive_shaft` after the last commit.

## Fixed Issues

### IN-07: `THEORETICAL_PIN` still says "M_Re is for this pin" for an odd tooth count, where no M_Re is printed

**Files modified:** `src/spur/shaft_calc.py`, `tests/test_shaft_calc.py`
**Commit:** 4ee29af
**Applied fix:** Took the clause out of `THEORETICAL_PIN` and folded it into `MEASURE_AT_NOMINAL_THICKNESS`, which is already gated on `reading.measure`. It now reads "M_Re is for this pin and is the measure at the nominal tooth thickness; ...". Folding kept the warning list the same length and order, so no other test or consumer moved. The odd-count test asserts "M_Re is for this pin" is absent from every warning, the default (even) test asserts it is present, and the pin-sentence test asserts `THEORETICAL_PIN` ends at "tabulated D_Re." and holds no "M_Re". Warning text only.

### IN-08: The `module` branch of `_exact` has no test, and the hobbed-root test indexes `warnings[2]`

**Files modified:** `tests/test_shaft_params.py`, `tests/test_shaft_calc.py`
**Commit:** ae7bbfc
**Applied fix:** Added `test_a_refused_module_is_printed_in_full_and_not_as_the_default_1_25` (`module=1.2499999`, `teeth=18`, `reference_d=25`): it asserts "module 1.2499999 " is in the message and that the printed shift differs from `X_MAX`. The three hobbed-root tests now take the sentence from a `_hobbed_warning(p)` helper that picks the warning containing "hobbed", so no test reads `warnings[2]` any more. Test-only change.

### IN-09: `H_FP_HOBBING` is a second hand-copied 0.60, outside the constants block

**Files modified:** `src/spur/din5480.py`, `src/spur/shaft_calc.py`, `tests/test_shaft_calc.py`
**Commit:** a2d125c
**Applied fix:** Moved `H_FP_HOBBING = 0.60` into the `din5480.py` constants block right after `H_FP`, with the same source line (DIN 5480-1:2006, cl. 6, Table 3 and cl. 7.1). `shaft_calc.HOBBED_ROOT_DROP` is now `round(2 * (din5480.H_FP_HOBBING - din5480.H_FP), 3)`. The drop test asserts `din5480.H_FP_HOBBING == 0.60` and `HOBBED_ROOT_DROP > 0`, so a sentence reading "0*m smaller" cannot ship. The root diameter still uses `H_FP`; the new constant is read only by the hobbed-root sentence and the `root_d` description.

---

_Fixed: 2026-10-26T12:00:00Z_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
