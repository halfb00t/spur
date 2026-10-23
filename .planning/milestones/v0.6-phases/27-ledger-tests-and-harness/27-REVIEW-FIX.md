---
phase: 27-ledger-tests-and-harness
fixed_at: 2026-10-21T00:00:00Z
review_path: .planning/phases/27-ledger-tests-and-harness/27-REVIEW.md
iteration: 1
findings_in_scope: 2
fixed: 2
skipped: 0
status: all_fixed
---

# Phase 27: Code Review Fix Report

**Fixed at:** 2026-10-21
**Source review:** .planning/phases/27-ledger-tests-and-harness/27-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 2
- Fixed: 2
- Skipped: 0

Edits and commits were made in the main checkout: `workflow.use_worktrees` is `false` in `.planning/config.json`, so no worktree or temp branch was created.

## Fixed Issues

### IN-09: Test name still says compound statement after the table gained lambda rows

**Files modified:** `tests/test_browser_pins.py`
**Commit:** 75b93f6
**Applied fix:** Renamed `test_a_marker_in_a_compound_statements_body_does_not_allow_a_header_read` to `test_a_marker_outside_the_reads_own_expression_does_not_allow_it`, and `test_an_environ_scrub_in_a_header_that_holds_its_own_marker_is_allowed` to `test_an_environ_read_that_holds_its_own_marker_is_allowed`. The second docstring now says the read's expression may sit in a header, a default or a lambda body. The old names appeared only in the test file, the review and `27-VERIFICATION.md` (a historical finding record, left as written). No logic change.

### IN-10: The lambda stop is narrower than the statement-level allowance around it

**Files modified:** `tests/test_browser_pins.py`
**Commit:** 8e65fbc
**Applied fix:** Added a three-line comment in `_problems` after the IN-08 note. It says the allowance is per statement, that `arguments` and `lambda` are the only narrower units, and that a marker among a call's other arguments, in the other branch of a conditional or in a comprehension's iterable still allows the read. Comment only. The pin's logic is unchanged, as instructed, so the review's optional "narrow the climb to the enclosing call argument" route was not taken.

## Verification

Gate ran in the main checkout (no worktree).

- `.venv/bin/python -m pytest tests/test_browser_pins.py -q`: `15 passed in 0.16s` (after each commit)
- `ruff check` and `ruff format --check` on `tests/test_browser_pins.py`: passed
- `make verify` (final, after both commits): `======================= 1348 passed in 238.87s (0:03:58) =======================`

Debt filed: none.

---

_Fixed: 2026-10-21_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
