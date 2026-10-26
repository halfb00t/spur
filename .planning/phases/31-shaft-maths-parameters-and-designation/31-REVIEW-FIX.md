---
phase: 31-shaft-maths-parameters-and-designation
fixed_at: 2026-10-26T00:00:00Z
review_path: .planning/phases/31-shaft-maths-parameters-and-designation/31-REVIEW.md
iteration: 1
findings_in_scope: 13
fixed: 13
skipped: 0
status: all_fixed
---

# Phase 31: Code Review Fix Report (the DIN 5480-2 anchor follow-up)

**Source review:** .planning/phases/31-shaft-maths-parameters-and-designation/31-REVIEW.md

The orchestrator applied the fixes, because it wrote the diff under review. They are re-reviewed independently before re-verification.

- **WR-11:** this changed warning text, and the review asked for the human's decision. The orchestrator took option 1, the review's recommendation, because the old sentence is false. It is reversible and no number moved.
- **Numbers:** no printed number, default or bound changed. T-31-13: no DIN 5480 value was added beyond the 24 approved ones.
- **Tests:** `tests/test_din5480_anchors.py tests/test_shaft_calc.py tests/test_din5480.py tests/test_shaft_params.py` gave `1018 passed`. Every commit passed `make verify.fast` in the pre-commit hook.

## Fixed Issues

### WR-07: Two of the four approved rows have an odd tooth count, but every new text says one

**Commit:** 195e38c, c4fc1ac
**Applied fix:** The L47 amendment, the resolved debt item, the idea, the `measure_over_pins` docstring and the anchor test docstrings now name two odd rows: W 26x1.25x19 and W 30x2x13.

### WR-08: "Each assertion was seen red once" is false for da1, for the odd-row null, and for the oracle cross-check

**Commit:** 8c77302
**Applied fix:** Eight mutation runs, each reaching one assertion alone: lines 108, 111, 112, 113, 114, 134, 135 and 137 of `tests/test_din5480_anchors.py`. The logs carry the failing line (`--tb=line`). The misleading `31-part2-red-tip.log` is replaced by `31-part2-red-tip-only.log`, and the runs join `bench/RESULTS.md` `### Seen red once (Phase 31)`. The docs now say "each value assertion": the `reading is not None` precondition has no break of its own.

### WR-09: The amendment quotes the guard margin as 0.067*m; the margin is 0.1*m

**Commit:** 195e38c
**Applied fix:** The amendment now says the margin is 0.1*m, sized from gaps of at most 0.067*m.

### WR-10: The published `measure_over_pins` description still says an odd count is "unconfirmed"

**Commit:** 3bedcc7
**Applied fix:** The field description now says "Null for an odd tooth count (not given yet)". The constant name `ODD_Z_UNCONFIRMED` is kept: renaming it is churn, and the idea file names it as the thing to retire.

### WR-11: The printed pin sentence says the pin "has not been compared with a tabulated D_Re"; this diff compares it, and it differs for the default shaft

**Commit:** ee75aae
**Applied fix:** Option 1. `THEORETICAL_PIN` now ends: "DIN 5480-2 tabulates its own measuring pin D_M for the sizes it lists, and for most of them it differs from this pin." (684 of 700 rows read.) The test pins the new ending. Warning text only.

### IN-10: The null-pin test's docstring still gives the pre-IN-07 reason for withholding `THEORETICAL_PIN`

**Commit:** c4fc1ac
**Applied fix:** The docstring now says THEORETICAL_PIN describes a D_Re that is not printed.

### IN-11: `H_FP_HOBBING`'s comment says only the hobbed-root sentence reads it; the `root_d` field description reads it too

**Commit:** c4fc1ac
**Applied fix:** The comment names both readers: the hobbed-root sentence and the `root_d` description, through `HOBBED_ROOT_DROP`.

### IN-12: The basic-dimensions docstring claims more about the shift range than the test proves

**Commit:** c4fc1ac
**Applied fix:** The docstring now says both edges are accepted and reach rows the standard prints.

### IN-13: 706 nominal rows but 700 M1 rows, and the amendment says "all"

**Commit:** 195e38c
**Applied fix:** The amendment, the resolved item and the idea say the parser read 706 nominal and 700 inspection rows and misses a few at page breaks, in both tables. The difference is a parser artifact, not a property of the standard.

### IN-14: The anchor module docstring's first paragraph is now stale, and `tables` is never read

**Commit:** c4fc1ac
**Applied fix:** The module docstring covers both approvals. The `tables` column now goes into the test ids.

### IN-15: The L47 amendment spans five paragraphs, and one of them opens like an original section

**Commit:** 195e38c
**Applied fix:** The amendment is split into two labelled `**Amendment (...)**` paragraphs, and the bold on "The guard" is gone from the body.

### IN-16: Resolving the anchor item drops the gauge-series bullet and leaves REQ-shaft-basic-dims "can close" untracked

**Commit:** 195e38c
**Applied fix:** The resolved item has the gauge-series bullet and says REQ-shaft-basic-dims closes with the re-verification. REQUIREMENTS.md is updated at re-verification.

### IN-17: The code that the new form-diameter debt item is about does not point to it

**Commit:** c4fc1ac
**Applied fix:** The `form_diameter` docstring and the `GUARD_MARGIN_FACTOR` comment point to the form-diameter debt item.
