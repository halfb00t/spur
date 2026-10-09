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

Phase 19 trigger read on 2026-10-09 (plan 19-03), with the isolation run. 19-01's gate baseline run 2
(`make verify`, `-n 8 --cov`, `1 failed, 1022 passed in 53.61s`) printed the chain in
`tests/test_pool.py::test_a_dying_worker_surfaces_as_broken_pool_and_is_replaced` on worker `gw0` (fourth
occurrence; whole log `.planning/phases/19-the-trochoid-in-the-part/investigation/19-01-gate-flake.log`). The
isolation under Next step was then run: 60 loops of `tests/test_pool.py` and `tests/test_api.py`, 20 each at
`-n 8 --cov`, `-n 8 --no-cov` and `-n0 --cov`, interleaved round by round. All 60 read `74 passed`; none
contained `ReentrantCallError`. 0 of 20 per configuration puts the 95 % upper bound on a per-loop rate at about
14 %; with 17-04's 40 two-file loops (also silent) it is 0 of 100, about 3 %. So the isolation did not separate
xdist from coverage's `multiprocessing` concurrency: no configuration reproduced it. Every one of the four
recorded occurrences came from a whole-suite run, none from the two process-spawning files alone, and the local
whole-suite rate is 2 in 12 (17-04 1 in 3, Phase 18 0 in 4, 19-01 1 in 5); the two-file loops probably do not
sample the same population as the gate. ASSUMPTION, not measured: what the whole suite adds is other test files
on the same worker, or the longer life of the run. Counts, per-loop table and host state:
`.planning/phases/19-the-trochoid-in-the-part/investigation/19-03-isolation.md`.

A separate observation, verified on 2026-10-09 by the orchestrator (not re-measured here): 12 macOS crash
reports since 2026-10-08 16:46 show a pytest-xdist worker dying at interpreter exit in
`BRepAlgoAPI_BuilderAlgo::~BRepAlgoAPI_BuilderAlgo()` under `Py_FinalizeEx -> finalize_modules ->
_PyModule_ClearDict -> list_dealloc -> tupledealloc -> OCP`, after the worker's tests had reported, so it cannot
fail a test. No mechanical link to the `ReentrantCallError` chain is established; the only shared trait is that
both appear in whole-suite runs only. Three whole-suite runs that day (`make test` 1034 passed in 58.74 s, one
probed `-n 8 --cov` run, `make verify.fast` 713 passed in 11.07 s) produced no crash report.

Re-deferred on 2026-10-09 by the human, who answered `take the recommendations` to the choice between fixing the
shutdown order, adding the narrowest filter and re-deferring. The orchestrator mapped those words to
`debt-redefer`, the course the executor had stated as its recommendation (the mapping is the orchestrator's, not
the human's). No `shutdown(wait=True)` was added: no occurrence was localised to a pool a test leaves to its
finalizer, so a fix would be a guess. No `filterwarnings` entry was added: a filter would hide the symptom of a
failure whose cause is unlocated. Severity stays `must`, Status stays `active`.

New trigger: the next `make verify` failure, with its whole log kept (as 19-01 did) so the test and worker
localise the fix; or, if none by Phase 20 planning or the next milestone's start, whole-suite loops of
`make test` at `-n 8 --cov` and `-n 8 --no-cov`.

<!-- On resolve: set Status: resolved, add `Resolved in: <commit sha>`,
     git mv into resolved/, move the INDEX row to Resolved — same commit as the fix. -->
