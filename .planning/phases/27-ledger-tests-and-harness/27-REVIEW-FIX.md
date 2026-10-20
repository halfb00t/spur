---
phase: 27-ledger-tests-and-harness
fixed_at: 2026-10-20T00:00:00Z
review_path: .planning/phases/27-ledger-tests-and-harness/27-REVIEW.md
iteration: 1
findings_in_scope: 2
fixed: 1
skipped: 1
status: partial
---

# Phase 27: Code Review Fix Report

**Fixed at:** 2026-10-20
**Source review:** .planning/phases/27-ledger-tests-and-harness/27-REVIEW.md
**Iteration:** 1 (this is the second Info-scope pass, `fix_scope: all`; only the two findings still open in the re-review, IN-04 and IN-08, were in scope. IN-01 to IN-03 and IN-05 to IN-07 were fixed by the earlier pass and are not repeated here; their commits are c22742e, d7426e0, d91ce2f, c8cf8b4, 0fd2b98 and 782fe9f.)

**Summary:**
- Findings in scope: 2 (IN-04, IN-08; no Critical or Warning findings open)
- Fixed: 1 (IN-08)
- Skipped: 1 (IN-04, filed as a `nice` tech-debt item)

**Verification ran in the main checkout** (`workflow.use_worktrees` is `false`, so no worktree was created). Final gate, run once after the last commit landed:

```
make verify
======================= 1348 passed in 212.34s (0:03:32) =======================
Required test coverage of 96.0% reached. Total coverage: 97.99%
```

Exit status 0. Each commit also passed the commit hook (`make verify.fast`).

## Fixed Issues

### IN-08: A lambda's parameter-list marker still allows a read in the lambda's body

**Files modified:** `tests/test_browser_pins.py`
**Commit:** 39cf27d
**Applied fix:** `ast.Lambda` joins the node types the environ pin's climb stops under. A lambda's parameter list and body are siblings under one expression node, so a read in the body used to climb to the whole lambda and take in the defaults' marker. With the stop, the body is its own unit and the defaults stay a separate unit (`arguments`). Chose the code change over the docstring-only option because it is one token, closes the gap instead of documenting it, and is simpler than the review's suggested condition: the `expression is not parents[expression].args` clause is not needed, because the climb never reaches the `arguments` node itself (it already stops one step below it).

- Two rows added to the existing compound-statement test: `g = lambda a="SPUR_": os.environ["SKIP"]` and `def f(a=lambda b="SPUR_": os.environ["SKIP"])`. With the token removed (reverted in place after backing the fixed file up to the scratchpad, then restored), exactly those two rows fail and the other 13 tests pass; with it, all 15 pass.
- Two allowed shapes added to the existing "own marker" test so the stop cannot turn into a false positive: `def f(a=os.environ.get("PLAYWRIGHT_BROWSERS_PATH"))` and `lambda: any(k.startswith("SPUR_") for k in os.environ)` both report nothing.
- Probe with `.venv/bin/python -I`: `_scan_problems()` over the real scan set returns `[]`.
- `ruff check` and `mypy --strict` on the file: clean.

**Status note:** a logic change to the pin's own scan, so it carries "fixed: requires human verification" in the strict reading of the fixer rules. The scan is a test helper only; nothing printed to users depends on it.

## Skipped Issues

### IN-04: Nothing pins that `_build` passes its own `rm` to `_chamfer_tips`

**File:** `tests/test_model.py:899, 926, 976` (with `src/spur/model.py:640, 783`)
**Reason:** Both suggested tests assert an internal call: a counting wrapper on `spur.model.root_mode` is an internal call count, and a stand-in on `tip_chamfer_effective` that checks its `rm` argument asserts a private argument. `docs/CODING_VALUES.md` (Testing) bans both. The result is identical either way, because `tip_chamfer_effective(p)` re-derives the same `rm`; only the cost differs, and a cost claim is measured, not asserted. No test was forced. The skip is now a decision on file, as the review asked: a `nice` tech-debt item with a named trigger (`_build` or `_chamfer_tips` next touched, or a public per-build cost counter appearing), committed with its INDEX row in 2012d5e.
**Debt item:** `docs/tech_debt/active/2026-10-20-nothing-pins-that-build-passes-its-own-rm-to-chamfer-tips.md`
**Original issue:** The updated monkeypatches accept either calling shape, so reverting `_chamfer_tips` to `tip_chamfer_effective(p)` would leave every test green.

## Notes for the orchestrator

- Filed one tech-debt item (IN-04): the path above, `Severity: nice`, INDEX row added in the same commit.
- `src/` was not touched.
- The red check for IN-08 used a backup copy in the scratchpad and a restore with `cp`; no `git checkout --` was used, and the fix was never lost.
- `git status` is clean apart from this report, which the orchestrator commits.

---

_Fixed: 2026-10-20_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
