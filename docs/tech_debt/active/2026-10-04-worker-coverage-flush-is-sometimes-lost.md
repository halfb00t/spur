# A full run sometimes loses BuildPool's worker coverage, moving the total by 0.22 points

Severity: nice
Status: active
Date: 2026-10-04
Source: 15-02's baseline run C0 (bench/RESULTS.md, "The gate, measured and pinned
(Phase 15)", Coverage baseline), after 15-RESEARCH Pitfall 13
Related files:
- pyproject.toml (`[tool.coverage.run]` `concurrency`, `parallel`, `sigterm`)
- src/spur/pool.py (lines 63-67 `build_export`, 222 `export`)
- tests/test_pool.py (`test_a_real_worker_builds_and_downloads`)

## Context

With `concurrency = ["multiprocessing", "thread"]` and `parallel = true`, a full `--cov` run
usually counts the lines `BuildPool`'s spawned workers run, and `tests/test_pool.py` alone
reads `pool.py` at 100.00 % every time it was run (serially and at `-n 2`). On one full
serial run (C0) `pool.py` read 95.00 % with lines 63-67 and 222 missing -- the one real
worker build's data went unrecorded -- and the total read 96.99 % where the three `-n 8`
runs read 97.21 %, 23 missed statements each. 15-RESEARCH saw the same three lines lost
once in three full `-n 4` runs. The cause is not established: candidates are a worker's
data written after the controller's combine (workers are shut down with
`shutdown(wait=False)`) or a lost flush under load.

Tally after 15-04's before/after (bench/RESULTS.md, "Before and after"): all three serial
full `--cov` runs of the phase (C0, A1, A2) lost the three statements and read 96.99 %;
none of the six `-n 8 --cov` runs that printed `pool.py` did (15-02's B1-B3, B1 and B2 of
15-04, all 97.21 %, and the 71-item deselect run in RESULTS.md § "Proposed cuts", `pool.py`
100.00 %), nor did 15-05's CI run at `-n 4` (`pool.py` 100.00 %, run 37181871926). Ten
runs, no cause; the one loss at `-n 4` in 15-RESEARCH says it is not serial-only.

## Why it matters

The floor (`fail_under = 96`) was set with that loss inside its slack, 0.99 points under
the lowest total, so it cannot turn the gate red by itself. But a total that moves 0.22
points with no code change makes any tighter floor a coin toss, and the next re-pin from a
single reading could land on the wrong side of it.

## Next step

Revisit when a `make verify` reads under the floor with no code change, or when
`BuildPool.shutdown`/`_run_with_timeout` is next touched: run `tests/test_pool.py` with
`--cov` in a loop under load and see whether the three lines drop out, then try
`shutdown(wait=True)` in the test teardown only. Do not move the floor to chase it.

<!-- On resolve: set Status: resolved, add `Resolved in: <commit sha>`,
     git mv into resolved/, move the INDEX row to Resolved — same commit as the fix. -->
