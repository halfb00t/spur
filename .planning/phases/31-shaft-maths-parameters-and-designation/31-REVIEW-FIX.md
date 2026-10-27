---
phase: 31-shaft-maths-parameters-and-designation
fixed_at: 2026-10-26T00:00:00Z
review_path: .planning/phases/31-shaft-maths-parameters-and-designation/31-REVIEW.md
iteration: 2
findings_in_scope: 5
fixed: 5
skipped: 0
status: all_fixed
---

# Phase 31: Code Review Fix Report (Part 2 follow-up, second pass)

**Source review:** .planning/phases/31-shaft-maths-parameters-and-designation/31-REVIEW.md

The orchestrator applied these fixes. They are docs and docstrings, plus re-run red logs; no code behaviour changed. Every commit passed `make verify.fast` in the pre-commit hook.

## Fixed Issues

### IN-18: "A break that reaches it alone" is false for the shift and thickness runs

**Commit:** a863df1
**Applied fix:** The L47 amendment, the resolved item and 31-VALIDATION now say each value assertion was seen red once "as the first failure of its test".

### IN-19: 8c77302's logs and RESULTS rows cite line numbers of a later commit, and no log carries revert proof

**Commit:** dd2c813
**Applied fix:** All eight reds were re-run on the committed head a863df1, with `PYTHONDONTWRITEBYTECODE=1`, `__pycache__` purged and `-p no:cacheprovider`. Each fails at the same line as before. Each log ends with `git checkout -- <file>` and an empty `git status --porcelain -- src tests`, and the RESULTS rows carry the same proof.

### IN-20: `test_shaft_calc.py`'s module docstring still describes the anchor file before Part 2

**Commit:** a863df1
**Applied fix:** The `tests/test_shaft_calc.py` module docstring now names the Part 1 and Part 2 anchors, and says the pin and M_Re numbers there pin the code's theoretical pin, not a table value.

### IN-21: The idea's Related files still points to one odd anchor row (WR-07 residue)

**Commit:** a863df1
**Applied fix:** The idea's related-files line names both odd anchor rows.

### IN-22: The cause given for the 706/700 gap ("misses a few rows at page breaks") has no evidence in the repo

**Commit:** a863df1
**Applied fix:** Investigated instead of marked `ASSUMPTION:`. The page-break explanation was wrong: the parser dropped rows whose tooth count or k column carries the copy's footnote mark ("12 a", "11 a", "8a"). With the mark stripped it reads 720 nominal and 721 inspection rows. The two tables pair up except one row that Table 12 prints twice (d_B 20 for d_B 19, seen on the rendered PDF page 18). Every count was restated: 719/720, 510/510, 211/211, 483/719 (44 at hobbing), 16/721.
