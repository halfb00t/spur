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

Reviewed `git diff 401d5ca..HEAD -- tests/test_browser_pins.py` (commits 75b93f6 and 8e65fbc):
two test renames (IN-09) and one new comment on the climb in `_problems` (IN-10). No code
changed, so no behavior regressed: `pytest tests/test_browser_pins.py` gives 15 passed, and
`ruff check` and `ruff format --check` are clean on the file. Prior findings WR-01..04 and
IN-01..10 stay closed.

**Names.** Both read as requirements and match their tables.
- `test_a_marker_outside_the_reads_own_expression_does_not_allow_it` covers all 7 rows
  (if-header, default-vs-body, except-header, sibling defaults, lambda defaults, lambda body,
  nested lambda). Every row is a marker outside the read's expression, and the old name's
  "compound statement body" claim was too narrow for the sibling-default and lambda rows.
- `test_an_environ_read_that_holds_its_own_marker_is_allowed` matches its three asserts
  (header, default, lambda body), and its docstring says so.

**Comment probe.** I ran `_problems` from a scratch script outside the repo. The three
examples hold. Each of these returns 0 problems, meaning the read is allowed:
- `f(os.environ["X"], "SPUR_")`
- `x = os.environ["X"] if c else "SPUR_"`
- `x = [k for k in os.environ if k.startswith("a")] + ["SPUR_"]`

The surrounding wording does not hold, though (IN-11).

## Info

### IN-11: The "per statement" comment misdescribes the unit the climb stops at

**File:** `tests/test_browser_pins.py:126-128`
**Issue:** The comment says "The allowance is per statement: `arguments` and `lambda` are the
only narrower units". The climb stops at the expression directly under a statement or clause
node (`while not (isinstance(expression, ast.stmt) or isinstance(parents[expression], clause))`),
not at the statement. Probes show the unit is narrower than a statement in more places than
the comment names. Each of these returns 1 problem, meaning the read is reported even though a
marker sits in the same statement:
- `d["SPUR_"] = os.environ["X"]` (marker in the assignment target, read in the value)
- `with a(os.environ["X"]), b("SPUR_"):` (marker in another with-item)
- `@d("SPUR_")` over `@e(os.environ["X"])` (another decorator)
- `def f(b="SPUR_") -> os.environ["X"]:` (return annotation)
- `match os.environ["X"]:` with `case "SPUR_":` (subject versus case)

The error is on the safe side: the scan gives false positives, never a missed read. It still
misleads the next person tuning the climb. It also now sits against the test names, which say
"the read's own expression", and `test_an_environ_read_is_allowed_by_its_statement_not_its_line`,
which says "statement".

**Fix:** Describe the real rule once, in one term, and use that term in the names and docstrings:

```python
# The allowance is per top-level expression of a statement: the climb stops under the
# statement (or clause), so a marker in an assignment's target, another with-item, a
# decorator or a return annotation does not allow this read. Inside that expression,
# only `arguments` and `lambda` split it further; a marker among a call's other
# arguments, in the other branch of a conditional or in a comprehension's iterable still
# allows the read (27-REVIEW IN-10).
```

### IN-12: The over-allowance the comment documents has no test pin

**File:** `tests/test_browser_pins.py:126-128`
**Issue:** The comment states three shapes that are allowed (another call argument, the other
conditional branch, a comprehension's iterable). It does so deliberately, as a known limit of the
tripwire. No test pins any of them. If the climb were later tightened or loosened, the comment
would go stale with no failing test. Every other behavior the climb comment describes (WR-01,
WR-04, IN-07, IN-08) has a row in the tests.

**Fix:** Add one parametrized test that pins the known over-allowance, so the limit is stated in
code and not only in prose:

```python
@pytest.mark.parametrize(
    "source",
    [
        'import os\nf(os.environ["X"], "SPUR_")\n',
        'import os\nx = os.environ["X"] if c else "SPUR_"\n',
        'import os\nx = [k for k in os.environ if k.startswith("a")] + ["SPUR_"]\n',
    ],
    ids=["other-call-argument", "other-conditional-branch", "comprehension-iterable"],
)
def test_a_marker_elsewhere_in_the_same_expression_still_allows_the_read(source: str) -> None:
    """Known limit (27-REVIEW IN-10): the allowance is not narrower than the expression."""
    assert _problems("f.py", source) == []
```

---

_Reviewed: 2026-10-21_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
