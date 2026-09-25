# `test_a_wedged_build_is_terminated_and_its_worker_replaced` flakes on the GitHub runner

Severity: must
Status: resolved
Date: 2026-09-25
Resolved in: ae052f8, 3c096de
Source: PR #4's CI during `/gsd-ship 5`, 2026-09-25: runs 36116930241 (head `73535a2`) and
  36117030280 attempt 1 (head `107c714`) failed `test (3.12)` on this one test; the
  re-run of that job on the same `107c714` passed.
  After filing: run 36118554588 (head `e8e15b0`) failed the same test on both of its
  attempts -- 4 of 5 runs that day.
Related files:
- tests/test_pool.py (`test_a_wedged_build_is_terminated_and_its_worker_replaced`, the
  `proc.join(timeout=5)` / `assert not proc.is_alive()` pair)
- src/spur/pool.py (`_run_with_timeout`: `proc.terminate()`, then `recreate_for` ->
  `executor.shutdown(wait=False)`)

## Context

What failed, both times: `tests/test_pool.py:161: assert not proc.is_alive()` --
`AssertionError: assert not True` after `proc.join(timeout=5)`; the `worker.replaced`
record was logged, so the timeout branch ran (`terminate()`, then `recreate_for`).
`1 failed, 182 passed`.

Ruled out on 2026-09-25, each by a real check:

- The Phase 5 diff. `pool.py`'s `except TimeoutError` names the same class as
  `asyncio.TimeoutError` on 3.12; `test_pool.py` changed only a docstring. The test
  dates from Phase 2 (`4fb7037`) and was green on Linux in runs 35963114939 and
  36088409707.
- The runner. Same image (`ubuntu-24.04`, `20260920.314.1`), same CPython (3.12.14)
  and identical package versions on the green run 36088409707 (PR #3 head, a day
  earlier) and the red run 36116930241. The one difference, uvicorn 0.53.0 -> 0.54.0,
  is not in the worker's import chain and leaves `SIGTERM` untouched at import
  (checked in `python:3.12.14-slim`).
- The mechanism. In a cadquery-warmed spawn worker `signal.getsignal(SIGTERM)` is
  `SIG_DFL` and the process is dead 0.03 s (macOS, 3.12.13) / 0.05 s (Linux, the
  project image `spur:latest`, 3.12.14) after `terminate()`; `make test-image
  PYTEST_ARGS="tests/test_pool.py -k wedged"` passes in the image. A dependency-free
  probe (spawn `ProcessPoolExecutor`, terminate while sleeping, join) exits `-15` on
  `python:3.12.13-slim` and `3.12.14-slim`.

Not reproduced outside the runner; two red then one green on the runner with nothing
changed in between. A flake.

The one mechanism found that makes the assertion lie -- inferred from CPython 3.12's
source this session, not observed (ASSUMPTION): `multiprocessing.popen_fork.Popen.poll`
swallows `OSError` from `os.waitpid` and returns `None`, and `Process.is_alive()` treats
`None` as alive. After `terminate()` + `shutdown(wait=False)` the executor's
`_ExecutorManagerThread` joins the dead worker on its own thread (`run` ->
`terminate_broken` / `join_executor_internals` -> `p.join()`) while the test's main
thread joins the same `Process` object; both go through `Popen.wait` -> `os.waitpid(pid,
0)`. If the manager thread's `waitpid` reaps the child between the test thread's
`wait([sentinel])` returning and its own `waitpid`, the test thread gets `ECHILD` ->
`poll` returns `None` -> `join` returns -> `is_alive()` calls `poll(WNOHANG)` -> `ECHILD`
again -> `True`, for a process that is dead. Whether the manager thread has assigned
`returncode` by then decides it, and that assignment needs the GIL the test thread is
holding. A slow 2-vCPU runner widens the window; it explains "dead worker reported
alive" with no `SIGTERM` failure, which is what every probe showed.

## Why it matters

`test (3.12)` is a required check on `main` (L22) and `make pr.land` refuses a red head:
a flake here randomly stalls the sanctioned merge path and invites re-running until
green -- the habit Phase 5 exists to end. Two of three runs failed on the day the gate
went live.

## Next step

Make the death check race-free and stronger. After `_run_with_timeout` raises, join the
executor's manager thread first (`executor._executor_manager_thread.join(timeout=5)` --
private, like `_processes`, so guard it the way
`test_executor_processes_attribute_still_exists` guards that one), then assert
`proc.exitcode == -signal.SIGTERM`: it proves the worker died *by our signal*, and
`exitcode` is the `returncode` the manager's own join already recorded, so no second
`waitpid` races it. If the hypothesis is wrong, the first failure after this change
prints an exit code instead of `assert not True` -- the evidence this filing lacks.
Done in ae052f8: the test captures the manager thread before the timeout, joins it, and
asserts `proc.exitcode == -signal.SIGTERM`; the private-attribute guard test covers
`_executor_manager_thread` too. Whether the race was the cause is proven by the next
runner failure printing an exit code instead of `assert not True` -- or by there being
none.

`ae052f8` left a residual race, found by a Codex re-review of that commit and closed in
`3c096de`: a timed `manager.join(timeout=5)` gives no guarantee the manager thread
finished, and reading `proc.exitcode` while it is still running calls `Popen.poll` --
the same concurrent `waitpid` this fix set out to remove. Reproduced by pausing the
manager thread before its `returncode` assignment: the join returned at 5.0s with the
thread still alive, and `exitcode` read `None` (errno `ECHILD`). `3c096de` closes it
with `assert not manager.is_alive()` between the join and the `exitcode` read, so the
liveness check happens before the value it gates is trusted.

Revisit when: this test fails again on any run, or `tests/test_pool.py` is touched anyway.

<!-- On resolve: set Status: resolved, add `Resolved in: <commit sha>`,
     git mv into resolved/, move the INDEX row to Resolved — same commit as the fix. -->
