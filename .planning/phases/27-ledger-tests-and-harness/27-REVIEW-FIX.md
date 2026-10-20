---
phase: 27-ledger-tests-and-harness
fixed_at: 2026-10-20T00:00:00Z
review_path: .planning/phases/27-ledger-tests-and-harness/27-REVIEW.md
iteration: 2
findings_in_scope: 1
fixed: 1
skipped: 0
status: all_fixed
---

# Phase 27: Code Review Fix Report

**Fixed at:** 2026-10-20
**Source review:** .planning/phases/27-ledger-tests-and-harness/27-REVIEW.md
**Iteration:** 2

**Summary:**
- Findings in scope: 1 (WR-04; no Critical; Info out of scope)
- Fixed: 1
- Skipped: 0

WR-01..WR-03 were fixed in iteration 1 and were not touched.

## Fixed Issues

### WR-04: The WR-01 fix makes `_problems` raise `KeyError` on a module-level `from os import environ`

**Files modified:** `tests/test_browser_pins.py`, `docs/tech_debt/resolved/2026-10-20-environ-pin-raises-keyerror-on-module-level-import.md` (git mv from `active/`), `docs/tech_debt/INDEX.md`
**Commit:** 27628ef (fix), b9755ad (follow-up docs commit naming the sha)
**Applied fix:** The climb now stops at a node that is already a statement:
`while not (isinstance(expression, ast.stmt) or isinstance(parents[expression], clause))`.
The review's two-`isinstance` form came to 103 columns and failed ruff E501, so the condition is
written as one negated `or`, which is logically identical. A comment records why. Added
`test_an_import_of_environ_is_reported_not_a_crash`, parametrized over the module-level and
in-function `from os import environ`, each expecting exactly one problem. It is a separate
test and not a row in the WR-01 parametrize, because that test's docstring is about markers in a
compound statement's body.

Evidence, with `.venv/bin/python -I`:
- Before: `_problems("x.py", "from os import environ\n")` raised `KeyError <ast.Module ...>`.
- After: it returns `['x.py:1: `environ` in `from os import environ`']`; the in-function form still reports one problem.
- `pytest tests/test_browser_pins.py --no-cov -q`: 11 passed.

Tech debt: the item `2026-10-20-environ-pin-raises-keyerror-on-module-level-import.md` was set to
`Status: resolved`, `git mv`d into `resolved/`, and its INDEX row moved from Active to Resolved,
all in the fix commit. A commit cannot hold its own sha, and amending would change it, so the fix
commit carried the commit subject in `Resolved in:` (precedent in the INDEX) and the follow-up
`docs(tech-debt)` commit b9755ad replaced it with `27628ef` in both the file and the INDEX row.

Status: fixed (not a logic-error classification beyond the loop condition; the new test pins both
the crash case and the unchanged in-function case).

## Verification

Gates ran in the main checkout (`workflow.use_worktrees` is `false` in `.planning/config.json`; no
worktree was created, so no cleanup tail was needed).

- `make verify`: `======================= 1343 passed in 206.46s (0:03:26) =======================`
  (ruff, mypy --strict, import contracts, unfinished-work scan and pytest all passed).
- Both commits also passed the pre-commit hooks (`make verify.fast`, skip-token reject), no `--no-verify`.

Filed items: none new; one existing item (the WR-04 debt file) resolved as above.

---

_Fixed: 2026-10-20_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 2_
