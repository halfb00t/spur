---
phase: 27-ledger-tests-and-harness
fixed_at: 2026-10-20T00:00:00Z
review_path: .planning/phases/27-ledger-tests-and-harness/27-REVIEW.md
iteration: 1
findings_in_scope: 3
fixed: 3
skipped: 0
status: all_fixed
---

# Phase 27: Code Review Fix Report

**Fixed at:** 2026-10-20
**Source review:** .planning/phases/27-ledger-tests-and-harness/27-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 3 (WR-01, WR-02, WR-03; fix_scope critical_warning, no Critical findings)
- Fixed: 3
- Skipped: 0

Edited and committed in the main checkout: `workflow.use_worktrees` is `false` in `.planning/config.json`, so no worktree, temp branch or recovery sentinel was created. Nothing under `src/` or `tests/regression/` was touched. Each commit ran the pre-commit hook `make verify.fast` (passed) without `--no-verify`.

## Fixed Issues

### WR-01: `_problems` environ allowance walks a compound statement's whole body, so the new "own statement" rule is bypassable

**Files modified:** `tests/test_browser_pins.py`
**Commit:** 5bf2a0f
**Applied fix:** The climb from the `environ` node now stops one level below the statement instead of at it. The loop ends when the parent is an `ast.stmt`, `ast.ExceptHandler` or `ast.match_case`, and the marker search walks only that expression. The reviewer's suggestion stopped at `ast.stmt`. The two extra stops cover an `except os.environ...:` header and a `case` guard, which would otherwise hit the same body-walk through a clause node that is not a statement. The docstring wording says "expression" where it said "statement". New tests:
- `test_a_marker_in_a_compound_statements_body_does_not_allow_a_header_read`, three rows: `if-header-marker-in-body`, `default-argument-marker-in-body` (both reviewer reproductions) and `except-header-marker-in-handler-body`.
- `test_an_environ_scrub_in_a_header_that_holds_its_own_marker_is_allowed`, which keeps the legitimate shape green.

Red against the unfixed code (`pytest tests/test_browser_pins.py`):
```
FAILED ...[if-header-marker-in-body]
FAILED ...[default-argument-marker-in-body]
FAILED ...[except-header-marker-in-handler-body]
3 failed, 5 passed in 0.08s
```
(`assert 0 == 1`, `_problems` returned `[]`.) Green after the fix: `8 passed in 0.07s`.

Status: fixed. The change is a logic rule in a test pin, so the reviewer may want to confirm the rule itself, although the rows above cover both reviewer reproductions and the allowed scrub.

### WR-02: Moving the teardown to `tests/process_group.py` took it out of the pin's scan set

**Files modified:** `tests/test_browser_pins.py`
**Commit:** 2e724cf
**Applied fix:** `_scan_set()` adds `tests/process_group.py` beside `capture_requests.py`. The `_scan_set` docstring and the module docstring name it. The scan-and-report comprehension became `_scan_problems()` so the main pin and the new test share one path. `test_the_browser_test_has_no_path_that_passes_without_the_browser` now asserts `process_group.py` is in the scan set. New test `test_a_skip_spelling_in_the_server_teardown_module_is_caught` points `REPO_ROOT` at a temp tree whose `tests/process_group.py` calls `pytest.skip(...)` and expects exactly one problem at `process_group.py:5:`. `bench/RESULTS.md` is append-only and was not edited for the docstring gap the reviewer noted.

Red against the unfixed code:
```
FAILED tests/test_browser_pins.py::test_a_skip_spelling_in_the_server_teardown_module_is_caught
FAILED tests/test_browser_pins.py::test_the_browser_test_has_no_path_that_passes_without_the_browser
2 failed, 7 passed in 0.25s
```
(`AssertionError: []` for the skip spelling; the scan set printed as `{'browser_session.py', 'capture_requests.py', 'test_browser.py'}`.) Green after the fix: `9 passed in 0.09s`. The real `process_group.py` is clean under the widened scan (the main pin passes).

### WR-03: `stop_group` still lets a failure in the reader skip SIGKILL and the reap

**Files modified:** `tests/process_group.py`, `tests/test_process_group.py`
**Commit:** 41212d5
**Applied fix:** The `except` in `stop_group` now covers `CalledProcessError`, `TimeoutExpired`, `OSError` and `ValueError`, so any failed read sets `survivors = None`, continues to SIGKILL, reaps the leader and fails as "survivors unknown". `group_members` runs `ps` with `timeout=PS_BOUND_S`; `PS_BOUND_S = 5.0` is a new constant with a comment saying why it is generous. The reviewer's alternative (`try/finally`) was not used. New tests:
- Two rows added to `test_a_failed_ps_fails_the_teardown_with_the_group_already_signalled`: `ps-hangs` (`TimeoutExpired`) and `ps-row-is-not-numbers` (`ValueError`). Each asserts the signals were SIGTERM then SIGKILL, that the leader is reaped, and the "survivors unknown" failure.
- `test_ps_is_run_with_a_timeout`: a fake `subprocess.run` records its keyword arguments and the test asserts `timeout` is set. It patches the shared `subprocess.run` for the one call (the process-wide caveat of IN-05, noted in a comment).

Red against the unfixed code:
```
FAILED ...test_a_failed_ps_fails_the_teardown_with_the_group_already_signalled[ps-hangs]
FAILED ...test_a_failed_ps_fails_the_teardown_with_the_group_already_signalled[ps-row-is-not-numbers]
FAILED ...test_ps_is_run_with_a_timeout
3 failed, 3 passed in 0.06s
assert None is not None   # seen == {'capture_output': True, 'text': True, 'check': True}
```
Green after the fix: `15 passed in 0.15s` (this file plus `test_browser_pins.py`).

Status: fixed. This changes the teardown's exception handling, a logic rule, so the reviewer may want to confirm it.

## Skipped Issues

None. All three in-scope findings were fixed. Info findings IN-01 to IN-06 are out of scope for this run and untouched.

## Verification

Where it ran: the main checkout (`/Users/half/git/halfb00t/spur`, branch `gsd/phase-27-ledger-tests-and-harness`), not an isolated worktree, so the numbers are reproducible from the tree you are looking at.

- Per-fix: the touched test files under pytest with `--no-cov` (red then green, above), `ruff check tests` (all checks passed), `mypy` on the touched files (no issues).
- After the last fix: `make verify` exited 0.
  - `ruff`: `All checks passed!`
  - `mypy`: `Success: no issues found in 51 source files`
  - import contracts: `Contracts: 5 kept, 0 broken.`
  - coverage: `Required test coverage of 96.0% reached. Total coverage: 97.99%`
  - result line: `======================= 1341 passed in 230.73s (0:03:50) =======================`

The browser test ran inside this `make verify`, so the new teardown handling was exercised against the real server group, not only the fakes.

Debt filed: none. `.planning/milestone.lock` was not touched.

---

_Fixed: 2026-10-20_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
