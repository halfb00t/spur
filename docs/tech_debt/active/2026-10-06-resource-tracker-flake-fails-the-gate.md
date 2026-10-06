# A reentrant `resource_tracker` cleanup warning sometimes fails `make verify`

Severity: nice
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

## Why it matters
L13/L34 make `make verify` the one definition of "passing". A gate that fails on a
shutdown-order race in CPython's resource tracker, with no code change, costs a rerun per
occurrence and teaches people to retry — the habit the gate exists to prevent. One
occurrence so far; cause unmeasured. It is the `Finalize` of a semaphore (a
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
The warning fails `make verify` a second time, or `tests/test_pool.py`'s shutdown path or
`[tool.coverage.run] concurrency` is next touched.

<!-- On resolve: set Status: resolved, add `Resolved in: <commit sha>`,
     git mv into resolved/, move the INDEX row to Resolved — same commit as the fix. -->
