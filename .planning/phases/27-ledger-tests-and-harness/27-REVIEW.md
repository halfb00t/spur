---
phase: 27-ledger-tests-and-harness
reviewed: 2026-10-21T00:00:00Z
depth: standard
files_reviewed: 1
files_reviewed_list:
  - tests/test_browser_pins.py
findings:
  critical: 0
  warning: 0
  info: 2
  total: 2
status: issues_found
---

# Phase 27: Code Review Report

**Reviewed:** 2026-10-21
**Depth:** standard
**Files Reviewed:** 1
**Status:** issues_found

## Summary

Scope: `git diff ada3126..HEAD -- tests/test_browser_pins.py` (commit 39cf27d). The `_problems` environ pin now adds `ast.Lambda` to the `clause` tuple, so the ancestor climb stops under a lambda.

The change is correct. Evidence:

- **Logic.** For a read in a lambda body, the climb stops with `expression` set to the body expression. A marker in the lambda's own defaults is no longer inside `ast.walk(expression)`, so the read is reported. For a read in a lambda default, `arguments` already stopped the climb, so `Lambda` adds nothing there and no behaviour changes.
- **No false positives on the real scan set.** `tests/test_browser_pins.py` run in the repo venv: 15 passed. That includes `test_the_browser_test_has_no_path_that_passes_without_the_browser`, which scans `*browser*`, `capture_requests.py` and `process_group.py`.
- **The new table rows fail without the change.** I copied the file to a scratch directory outside the repo and reverted only the `| ast.Lambda` on line 127 with `sed`. I ran the same-file tests with the venv python from the scratchpad. Result: 2 failed, 9 passed. The two failures are `lambda-default-marker-in-the-body-read` and `nested-lambda-default-marker-in-the-body-read`; both reported 0 problems where 1 was expected. With the change in place: 11 passed. The nested row is the sharper one. Without the change the climb ends at the outer `def`'s `arguments` node with the whole inner Lambda as `expression`, so the inner lambda's marker still allows the read.
- **The two new allowed-shape asserts are regression guards, not red-first proofs.** `own_default` and `own_body` pass both with and without the change. They guard against the change over-reporting a read that carries its own marker.
- Working tree untouched: no checkout, stash or write to the repo other than this file.

Two stale-wording items remain. Nothing is blocking.

## Info

### IN-09: Test name still says compound statement after the table gained lambda rows

**File:** `tests/test_browser_pins.py:181`
**Issue:** `test_a_marker_in_a_compound_statements_body_does_not_allow_a_header_read` is the name of the table that now also holds the sibling-default rows (IN-07) and the lambda-body rows (IN-08). A lambda is an expression, not a compound statement, and a lambda's parameter list is not a "header". The name no longer states the requirement the table pins. The docstring was updated in 39cf27d and the name was not. The sibling test at line 202, `test_an_environ_scrub_in_a_header_that_holds_its_own_marker_is_allowed`, has the same drift: its new `own_body` assert is a lambda body, not a header.
**Fix:** Rename for the property, for example `test_a_marker_outside_the_reads_own_expression_does_not_allow_it` and `test_an_environ_read_that_holds_its_own_marker_is_allowed`. The names are stable ledger titles for the tests, so rename once, in the same commit as any later change to the pin.

### IN-10: The lambda stop is narrower than the statement-level allowance around it

**File:** `tests/test_browser_pins.py:123-128`
**Issue:** The new comment justifies the stop with "one expression whose parameter list and body are siblings". The same is true of a call's arguments, a conditional expression and a comprehension, and the climb does not stop at any of those. I probed `_problems` with a scratch script (read-only):

| Source | Problems reported |
| --- | --- |
| `f(os.environ["SKIP"], "SPUR_")` | 0 |
| `x = os.environ["SKIP"] if "SPUR_" else 0` | 0 |
| `x = [os.environ["S"] for _ in ["SPUR_"]]` | 0 |
| `f(lambda: os.environ["S"], "SPUR_")` | 1 |

So the allowance is still "any marker constant in the same statement", with lambda and `arguments` as the only sub-statement exceptions. The module docstring already calls the pins a tripwire and says they see "an `environ` read whose own expression names neither marker". That wording is stronger than what is implemented, and the comment at 123-125 reads as if siblings are generally isolated. This is not a regression and no real scan-set file has the shape. It is a documentation gap that could mislead the next reviewer into thinking those cases are covered.
**Fix:** Either add one sentence to the comment or docstring that the allowance is per statement, with `arguments` and `lambda` as the only narrower units, and that sibling call arguments or conditional branches are not isolated. Or, if you want it closed, add a failing row first and narrow the climb to the enclosing `ast.Call` argument. Per the keep-it-small rule, the sentence is probably enough.

---

_Reviewed: 2026-10-21_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
