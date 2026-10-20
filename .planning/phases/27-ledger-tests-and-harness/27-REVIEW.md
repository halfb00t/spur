---
phase: 27-ledger-tests-and-harness
reviewed: 2026-10-20T00:00:00Z
depth: standard
files_reviewed: 10
files_reviewed_list:
  - docs/tech_debt/INDEX.md
  - docs/tech_debt/resolved/2026-10-10-group-floor-of-3-is-not-two-pool-workers.md
  - docs/tech_debt/resolved/2026-10-10-launch-failure-message-names-a-stamp-that-skips-the-install.md
  - docs/tech_debt/resolved/2026-10-10-stop-group-reads-ps-before-it-signals.md
  - docs/tech_debt/resolved/2026-10-15-failed-build-name-test-depends-on-cache-order.md
  - docs/tech_debt/resolved/2026-10-15-slug-totality-is-not-guarded-in-the-gate.md
  - tests/test_bench.py
  - tests/test_browser_pins.py
  - tests/test_process_group.py
  - tests/test_selector.py
findings:
  critical: 0
  warning: 0
  info: 2
  total: 2
status: issues_found
---

# Phase 27: Code Review Report

**Reviewed:** 2026-10-20
**Depth:** standard
**Files Reviewed:** 10
**Status:** issues_found

## Summary

Incremental re-review of `git diff 130aa9e..HEAD` on the ten files: the Info-scope fix commits c22742e (IN-01), d7426e0 (IN-02), d91ce2f (IN-03), c8cf8b4 (IN-05), 782fe9f (IN-07) and 0fd2b98 (IN-06).

Ran `.venv/bin/python -m pytest tests/test_browser_pins.py tests/test_process_group.py tests/test_selector.py tests/test_bench.py --no-cov -q`: **81 passed in 2.68s**. Also `ruff check` and `mypy --strict` on the four test files: clean. (`ruff format --check` flags two files; the project does not use `ruff format`, L16, so that is not a finding.) `git status` is clean.

Disposition of the prior findings:

| Id | Status |
|---|---|
| IN-01 | Closed |
| IN-02 | Closed |
| IN-03 | Closed (the optional `isfinite` message change was declined; see below) |
| IN-04 | **Open, skipped on purpose, carried forward** |
| IN-05 | Closed |
| IN-06 | Closed |
| IN-07 | Closed for the `def` and `lambda` default-argument shapes it named; one adjacent lambda-body shape remains, filed as IN-08 |

- **IN-01 closed.** The `killpg` now runs only while `proc.returncode is None`. `returncode` is set by the instrumented `wait`, which calls the real `Popen.wait`, so a reaped leader is never signalled again. A leader that was killed but not yet reaped still has `returncode None`; its pid is still held by the kernel as a zombie, so the `killpg` is safe there. The final `Popen.wait(proc, timeout=5)` returns at once when already reaped. Comment states the why.
- **IN-02 closed.** The `poll` wrapper, its `setattr` and the word in the docstring are gone. `grep poll` over `tests/process_group.py` and `tests/test_process_group.py` finds only a `time.sleep` comment, so nothing asserts or produces a `poll` event.
- **IN-03 closed.** `test_the_page_string_reads_a_number_as_the_page_does` carries the rows that pin the original (`-0.0`, `1.0`, `0.05`, `1e-6`, `1e16`, and the `1e21` and `1e-7` raises). The rows match `tests/test_browser.py:623-636` and the values match the copy's documented contract. The `nan`/`inf` message is still misleading, but no caller passes either, and the fix report says why it was not touched; I accept that.
- **IN-05 closed.** `bench/trochoid_part.py` references `subprocess` in exactly three places: the import (27), `subprocess.run` (333) and `subprocess.CalledProcessError` (335). The `SimpleNamespace(run=no_head, CalledProcessError=subprocess.CalledProcessError)` exposes both. `machine_facts()` is not defined through that module's `subprocess` name, and the `grep` shows no other use. The stand-in is installed through `monkeypatch.setattr`, so it is undone at teardown, and both parametrized rows pass.
- **IN-06 closed.** Each new sha resolves with `git show --name-status` to the commit that renames the item from `active/` to `resolved/`: `99e2b7d` (group floor), `a393e50` (launch failure message), `a7c5f78` (`stop_group` order), `c47bfc4` (failed-build name), `345ee08` (`slug()` totality). Each file's `Resolved in:` line and its INDEX row hold the same sha; no old subject is left in the five files (grep). The shas are branch commits, `git branch --contains` lists only this branch, so they will stop being ancestors of `main` after a squash merge. The active item `2026-10-05-resolved-in-shas-point-at-squashed-branch-commits.md` already tracks this (L22, L25); not re-filed.
- **IN-07 closed for its named shapes; probe below.** The committed `tests/test_browser_pins.py` is coherent: it has the `ast.arguments` stop on line 125, the extended comment, the two new rows and the widened docstring; it is byte-identical between 782fe9f and HEAD, the tree is clean, the 13 tests in the file pass. The `git checkout --` slip left no trace.

### IN-07 probe (`.venv/bin/python -I`, `_problems` and `_scan_problems`)

Counts are problems reported; `0` means allowed.

| Source | Result | Reading |
|---|---|---|
| `def f(a=os.environ.get("S"), b="SPUR_")` | 1 | sibling default no longer allows it |
| `async def` and `*, a=..., b="SPUR_"` and `a=..., /, b="SPUR_"` | 1 each | the three parameter kinds are covered |
| `lambda a=os.environ["S"], b="SPUR_": 0` | 1 | |
| `def f(a: os.environ["S"] = "SPUR_")` | 1 | annotation sits under `ast.arg`, a separate unit |
| `def f(a=os.environ.get("PLAYWRIGHT_BROWSERS_PATH"), b=1)` | 0 | a default that holds its own marker is still allowed |
| `def f(*, a=any(k.startswith("SPUR_") for k in os.environ))` | 0 | the real scrub shape in a default is still allowed |
| `def f(a: os.environ["SPUR_"] = 1)` | 0 | own-marker annotation allowed |
| `from os import environ` / `def f(a=environ)` | 2 | import and bare-name default both reported, no crash |
| `def f(a=os.environ.get("SPUR_X"))` | 1 | not a bypass: the rule is equality with a whole marker, as before |
| `_scan_problems()` over the real scan set (`browser_session.py`, `capture_requests.py`, `process_group.py`, `test_browser.py`) | `[]` | no false positive on the shipped code |

The `arguments` stop cannot open a new bypass: it only ends the climb earlier, so the searched subtree can only shrink. It cannot add a false positive on a legitimate shape either: a default holding its own marker has the marker inside the same default expression and is still allowed, and the two real reads (`browser_session.py:128` and `:171`) are not defaults.

## Info

### IN-04: Nothing pins that `_build` passes its own `rm` to `_chamfer_tips`

**File:** `tests/test_model.py:899, 926, 976` (with `src/spur/model.py:640, 783`)
**Issue:** The point of 19-REVIEW IN-01 is that the chamfer limit reads the curve the part was cut from and does not solve it again. The updated monkeypatches (`lambda solid, _p, _pr, _rm: solid`, `lambda _p, _rm=None: ...`) accept either calling shape, so reverting `_chamfer_tips` to `tip_chamfer_effective(p)` would leave every test green. The change is correct today but unguarded. The fixer skipped it because both suggested tests assert an internal call, which `docs/CODING_VALUES.md` (Testing) bans, and because the revert changes cost (a second root solve) and not any observable result. That reasoning is sound for the two suggested fixes, so this stays an Info item and not something to force; it is not resolved in substance, so it is carried forward under the same id. (File not in this diff.)
**Fix:** Either record it as a `nice` item in `docs/tech_debt/active/` with an INDEX row, so the skip is a decision on file and not only a line in a fix report, or add a behavior-level check: measure the `_build` time or the number of root solves through a public counter if one exists. Failing both, close it as accepted in the phase disposition.

### IN-08: A lambda's parameter-list marker still allows a read in the lambda's body

**File:** `tests/test_browser_pins.py:124-131`
**Issue:** Found while probing the IN-07 fix. The `arguments` stop ends the climb under a lambda's parameter list, but a read in the lambda's body does not climb through `arguments`: the body is a sibling of it, under the `Lambda` node. The climb therefore ends at the whole `Lambda` expression, and `ast.walk` of it takes in the parameter defaults. Reproduced: `g = lambda a="SPUR_": os.environ["S"]` and `def f(a=lambda b="SPUR_": os.environ["S"]): pass` both return `[]`. So a marker in a lambda's defaults allows a read in its body, while a marker in a `def`'s defaults does not allow a read in its body (the `def` is a statement and the body statements are their own units). This is the same class as the dict/call sibling case the module docstring already accepts as inherent to a marker-in-expression rule, and it is not newly opened by 782fe9f (the old code allowed it too); it only means the IN-07 comment's claim, "one default's marker must not allow another default's read", is accurate but the wider "a header marker must not allow a body read" does not hold for `lambda`. No lambda in the scan set reads `environ`, and it takes a deliberate construction.
**Fix:** Optional. Add `ast.Lambda` to the stop set, so a lambda body's climb ends at the body expression: `while not (isinstance(expression, ast.stmt) or isinstance(parents[expression], clause) or isinstance(parents[expression], ast.Lambda) and expression is not parents[expression].args)`. That is more machinery than the gap earns; the simpler option is to leave the code and add a sentence to the module docstring that a lambda is one expression, parameter list included.

---

_Reviewed: 2026-10-20_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
