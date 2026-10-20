# The environ pin raises `KeyError` on a module-level `from os import environ`

Severity: must
Status: resolved
Resolved in: fix(27): stop the environ pin's climb at a statement so a module-level import is reported
Date: 2026-10-20
Source: Phase 27 code re-review after the WR-01..WR-03 fixes (`.planning/phases/27-ledger-tests-and-harness/27-REVIEW.md` WR-04)
Related files:
- tests/test_browser_pins.py:119-122

## Context
The WR-01 fix (5bf2a0f) made `_problems` climb from an `environ` node until its parent is a
statement, `except` clause or `case` clause. `ast.ImportFrom` is itself a statement, so for a
module-level `from os import environ` the loop climbs to the `ast.Module`, then reads
`parents[Module]` and raises `KeyError`. Reproduced 2026-10-20:
`_problems("m.py", "from os import environ\n")` raises `KeyError <ast.Module ...>`; before the fix
(a4091f9) it returned one problem. The same import inside a function still reports one problem.
No scanned module has such an import today, so the real scan returns `[]` and `make verify` passes.

## Why it matters
The pin still fails, so nothing passes silently. But the scan aborts on the first such file and
hides every other problem in the scan set, and the failure is a bare `KeyError`, not the D-02
"a path that passes without the browser" report. A top-level `from os import environ` is the most
natural way a future edit would introduce the read. No self-test row covers an `ImportFrom`.

## Next step
Stop the climb at a node that is already a statement
(`while not isinstance(expression, ast.stmt) and not isinstance(parents[expression], clause):`)
and add a self-test row `'from os import environ\n'` expecting one problem. Revisit by Phase 28,
or when `tests/test_browser_pins.py` is next touched.
