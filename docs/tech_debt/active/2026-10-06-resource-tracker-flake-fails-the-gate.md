# A reentrant `resource_tracker` cleanup warning sometimes fails `make verify`

Severity: must
Status: active
Date: 2026-10-06
Source: the pre-commit hook on the v0.4 start commit (`gsd/milestone-v0.4-start`), a run
whose only change was under `.planning/`
Related files:
- `pyproject.toml` (`[tool.pytest.ini_options] filterwarnings = ["error", ...]`, and
  `[tool.coverage.run] concurrency = ["multiprocessing", "thread"]`)
- `tests/test_pool.py`, `src/spur/pool.py` (the only spawned processes in the suite)
- `Makefile` (`test`: `pytest -n 8 --cov`)

## Context
One hook run of `make verify` (pytest `-n 8 --cov`, Python 3.12.13, homebrew, macOS,
2026-10-06) failed with an `ExceptionGroup` of at least four
`pytest.PytestUnraisableExceptionWarning: Exception ignored in: <Finalize object, dead>`,
each caused by `multiprocessing.resource_tracker.ReentrantCallError: Reentrant call into
the multiprocessing resource tracker` during `multiprocessing.synchronize._cleanup` ->
`resource_tracker.unregister(name, "semaphore")`, and the follow-up
`UserWarning: ResourceTracker called reentrantly for resource cleanup, which is
unsupported. The semaphore object '/mp-2ttnyn_k' might leak.` `filterwarnings = error`
turns the warning into a failure. The hook's output was truncated before the failing test
id; an immediate `make test` rerun on the identical tree read `934 passed in 67.84s`.

2026-10-06, second occurrence (17-04's second of three `make verify` proof runs, `-n 8 --cov`, host
1-min load 17.54): worker `gw2`, test
`tests/test_pool.py::test_three_same_tick_same_slot_timeouts_each_end_in_a_documented_refusal`;
its assertions had all passed and the `ExceptionGroup` of five reentrant-call warnings was
collected at the end of its call phase. 1 of 43 proof runs (40 loops over tests/test_pool.py and
tests/test_api.py at `-n 8`/`-n 4` with `--cov`, 3 full gates) printed it; the other 42 did not.
Whole log: `.planning/phases/17-debt-first-commit-gate-and-pool-race/investigation/17-04-resource-tracker.log`.

2026-10-06, third occurrence — the first on CI: GitHub Actions run 37460451701 (`ci`, job
`test (3.12)`, ubuntu-latest, Python 3.12.14, `make verify` at `-n 8 --cov`) on PR #27's head
`7af318d` failed `tests/test_pool.py::test_a_dying_worker_surfaces_as_broken_pool_and_is_replaced`
with `ExceptionGroup: multiple unraisable exception warnings (5 sub-exceptions)`, the same
`ReentrantCallError` chain at the end of the call phase — `1 failed, 943 passed in 210.98s`.
A re-run of the failed job on the same head was green, and run 37460192883 on the identical
code (`930c74c`, one `.planning/` commit earlier) read `944 passed in 128.16s`. The struck test
predates Phase 17.

## Why it matters
L13/L34 make `make verify` the one definition of "passing". A gate that fails on a
shutdown-order race in CPython's resource tracker, with no code change, costs a rerun per
occurrence and teaches people to retry — the habit the gate exists to prevent. Three
occurrences so far — the second inside a test Phase 17 added (17-04's `make verify` proof
runs read 2 of 3 green), the third on CI, where it turned PR #27's required `test (3.12)`
check red with no code change; cause unmeasured, and the `-n 0` / no-`--cov` isolation under Next
step has not been run. It is the `Finalize` of a semaphore (a
`ProcessPoolExecutor` or a coverage `multiprocessing` hook) running while the tracker is
already inside its own cleanup, which is an interpreter-shutdown ordering question, not a
`spur` bug as far as this one log shows.

## Next step
On the next occurrence capture the whole log (`make test 2>&1 | tee`), name the test and
the worker, and reproduce under `-n 0` and under `-n 8` without `--cov` to isolate xdist
from coverage's `multiprocessing` concurrency. Then either fix the shutdown order (an
explicit `shutdown(wait=True)` where a pool is left to the finalizer) or add the
narrowest `filterwarnings` entry that names this message, never a blanket
`ignore::pytest.PytestUnraisableExceptionWarning`.

## Revisit when
The "fails `make verify` a second time" trigger fired on 2026-10-06 (the second occurrence
above, commit `b8ef84a`); the "third time" trigger fired the same day on CI (run
37460451701). Escalated to `must` by the human on 2026-10-06 at the Phase 17 ship: a required
check that fails on its own is a merge-gate defect, not hygiene. Trigger set then: the next
`make verify` failure, or Phase 18 planning — whichever comes first — gets the isolation runs
under Next step and a fix plan.

Phase 18 planning trigger read on 2026-10-08, at the close of Phase 18 (plan 18-05): the phase
made four full `make verify` runs (18-01: 963 passed; 18-02: 981; 18-03: 996; 18-04: 1016), all
green, none printing the `ReentrantCallError` chain; `make verify.fast`, the pre-commit hook, runs
on every commit and excludes the process-spawning test files. Phase 18 added no process-spawning
test to the gate (`grep -nE 'multiprocessing|ProcessPool|subprocess' tests/test_trochoid.py
tests/trochoid_oracle.py` prints nothing; the pooled oracle lives in `bench/` and is not in the
gate). Nothing new was observed to isolate, and at about 1 in 43 runs the isolation loops would
most likely see nothing. Re-deferred by the human, who chose this over running the isolation or
adding a filter; Severity stays `must`, Status stays `active`.

New trigger: the next `make verify` failure, or Phase 19 planning — whichever comes first — gets
the isolation runs under Next step and a fix plan.

<!-- On resolve: set Status: resolved, add `Resolved in: <commit sha>`,
     git mv into resolved/, move the INDEX row to Resolved — same commit as the fix. -->
