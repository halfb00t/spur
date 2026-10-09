# 19-03 -- the resource-tracker isolation runs

Date: 2026-10-09 local (+06); the loops ran 2026-10-08T18:11Z to 18:49Z (38 min 48 s).
Debt: `docs/tech_debt/active/2026-10-06-resource-tracker-flake-fails-the-gate.md` (Severity: must).
Trigger honoured: "the next `make verify` failure, or Phase 19 planning -- whichever comes first --
gets the isolation runs under Next step and a fix plan" (19-01's baseline run 2 also failed on it).

## Host

Apple M5 Max, 18 CPUs (`sysctl -n machdep.cpu.brand_string`, `sysctl -n hw.ncpu`), macOS 27.0.0 (darwin),
Python 3.12.15, pytest 9.1.1, pytest-xdist 3.8.0, pytest-cov 7.1.0, coverage 7.16.2. The host was not idle:
1-minute load read 13.53 before the first loop with none of this plan's processes running (other
applications), and 19-02 was paused, not running.

## The three command lines (verbatim, run from the repo root)

```
A  .venv/bin/python -m pytest tests/test_pool.py tests/test_api.py -q -p no:cacheprovider -n 8 --cov --cov-fail-under=0
B  .venv/bin/python -m pytest tests/test_pool.py tests/test_api.py -q -p no:cacheprovider -n 8 --no-cov
C  .venv/bin/python -m pytest tests/test_pool.py tests/test_api.py -q -p no:cacheprovider -n0 --cov --cov-fail-under=0
```

`[tool.pytest.ini_options]` was as committed (`filterwarnings = ["error", ...]`), so a reentrant-call
warning would have failed the loop exactly as it fails the gate. `-n0` was checked to run serially
(`-n0 -v` on one test creates no workers; `-n2` prints `created: 2/2 workers`). Each loop took the
whole log to a scratch directory outside the repo and recorded `uptime` before and after; a loop's
"occurrence" is `grep -c ReentrantCallError` over its whole log.

Deviation from the plan's wording: the 60 loops were interleaved A, B, C, round by round (20 rounds),
not 20 of A then 20 of B then 20 of C, so that the host's load drift (8 to 24 below) lands on all three
configurations alike. Same 20 loops per configuration.

## Counts

| Config | Loops run | Loops failed | Loops whose log contains `ReentrantCallError` | 1-min load range (before and after, all loops) | Loop wall s (mean / max) |
|---|---|---|---|---|---|
| A `-n 8 --cov` | 20 | 0 | 0 | 8.43 - 22.57 | 38.35 / 39 |
| B `-n 8 --no-cov` | 20 | 0 | 0 | 8.43 - 24.02 | 38.20 / 39 |
| C `-n0 --cov` | 20 | 0 | 0 | 8.84 - 24.02 | 38.35 / 39 |

All 60 loops read `74 passed`. No log contains `ReentrantCallError`, `PytestUnraisableExceptionWarning` or
`ResourceTracker`.

## Occurrences

None in the 60 loops. There is no per-occurrence log to copy beside this file (`19-03-occurrence-<config>-<i>.log`
files do not exist because no occurrence exists).

The fourth line, read in from 19-01: the gate baseline's run 2 (`make verify`, `-n 8 --cov`, whole suite,
`1 failed, 1022 passed in 53.61s`, 1-minute load 16.71 -> 22.09) failed
`tests/test_pool.py::test_a_dying_worker_surfaces_as_broken_pool_and_is_replaced` on worker `gw0` with the same
five-exception `ReentrantCallError` chain at the end of the call phase. Whole log:
`.planning/phases/19-the-trochoid-in-the-part/investigation/19-01-gate-flake.log`.

## Every loop

Load is the 1-minute load average before -> after the loop; the "after" of one loop is, to a second or two, the
"before" of the next, and the load includes the loop's own eight workers.

| Config | Loop | Exit | `ReentrantCallError` count | Load | Wall s | Result line |
|---|---|---|---|---|---|---|
| A | 1 | 0 | 0 | 13.14 -> 15.82 | 38 | 74 passed in 38.24s |
| A | 2 | 0 | 0 | 18.38 -> 17.54 | 39 | 74 passed in 38.14s |
| A | 3 | 0 | 0 | 14.28 -> 17.06 | 39 | 74 passed in 38.05s |
| A | 4 | 0 | 0 | 17.09 -> 14.01 | 38 | 74 passed in 37.72s |
| A | 5 | 0 | 0 | 12.31 -> 11.94 | 39 | 74 passed in 37.93s |
| A | 6 | 0 | 0 | 12.45 -> 11.30 | 38 | 74 passed in 37.50s |
| A | 7 | 0 | 0 | 11.96 -> 10.61 | 37 | 74 passed in 37.51s |
| A | 8 | 0 | 0 | 8.85 -> 8.43 | 38 | 74 passed in 38.23s |
| A | 9 | 0 | 0 | 10.49 -> 13.07 | 38 | 74 passed in 37.56s |
| A | 10 | 0 | 0 | 12.69 -> 15.26 | 38 | 74 passed in 37.60s |
| A | 11 | 0 | 0 | 21.63 -> 18.92 | 39 | 74 passed in 38.16s |
| A | 12 | 0 | 0 | 15.39 -> 14.57 | 39 | 74 passed in 38.58s |
| A | 13 | 0 | 0 | 20.94 -> 22.39 | 39 | 74 passed in 38.71s |
| A | 14 | 0 | 0 | 19.01 -> 22.57 | 39 | 74 passed in 38.41s |
| A | 15 | 0 | 0 | 21.21 -> 21.40 | 38 | 74 passed in 37.22s |
| A | 16 | 0 | 0 | 15.81 -> 14.37 | 38 | 74 passed in 37.83s |
| A | 17 | 0 | 0 | 9.93 -> 10.67 | 38 | 74 passed in 37.49s |
| A | 18 | 0 | 0 | 14.65 -> 16.50 | 39 | 74 passed in 38.14s |
| A | 19 | 0 | 0 | 11.37 -> 10.09 | 38 | 74 passed in 37.95s |
| A | 20 | 0 | 0 | 15.02 -> 13.78 | 38 | 74 passed in 37.73s |
| B | 1 | 0 | 0 | 15.82 -> 18.61 | 39 | 74 passed in 37.97s |
| B | 2 | 0 | 0 | 17.54 -> 20.92 | 38 | 74 passed in 38.03s |
| B | 3 | 0 | 0 | 17.06 -> 16.41 | 37 | 74 passed in 37.08s |
| B | 4 | 0 | 0 | 14.01 -> 10.92 | 38 | 74 passed in 38.21s |
| B | 5 | 0 | 0 | 11.94 -> 13.52 | 38 | 74 passed in 37.27s |
| B | 6 | 0 | 0 | 11.30 -> 12.97 | 39 | 74 passed in 38.58s |
| B | 7 | 0 | 0 | 10.61 -> 10.74 | 38 | 74 passed in 37.72s |
| B | 8 | 0 | 0 | 8.43 -> 8.84 | 39 | 74 passed in 37.79s |
| B | 9 | 0 | 0 | 13.07 -> 13.37 | 38 | 74 passed in 37.68s |
| B | 10 | 0 | 0 | 15.26 -> 18.03 | 39 | 74 passed in 38.62s |
| B | 11 | 0 | 0 | 18.92 -> 18.59 | 39 | 74 passed in 38.83s |
| B | 12 | 0 | 0 | 14.57 -> 16.34 | 38 | 74 passed in 37.86s |
| B | 13 | 0 | 0 | 22.39 -> 18.98 | 38 | 74 passed in 37.55s |
| B | 14 | 0 | 0 | 22.57 -> 24.02 | 38 | 74 passed in 37.74s |
| B | 15 | 0 | 0 | 21.40 -> 21.33 | 38 | 74 passed in 37.88s |
| B | 16 | 0 | 0 | 14.37 -> 12.37 | 38 | 74 passed in 37.96s |
| B | 17 | 0 | 0 | 10.67 -> 13.23 | 38 | 74 passed in 37.96s |
| B | 18 | 0 | 0 | 16.50 -> 12.40 | 38 | 74 passed in 37.34s |
| B | 19 | 0 | 0 | 10.09 -> 12.63 | 39 | 74 passed in 38.08s |
| B | 20 | 0 | 0 | 13.78 -> 14.63 | 37 | 74 passed in 36.77s |
| C | 1 | 0 | 0 | 18.61 -> 18.38 | 39 | 74 passed in 39.10s |
| C | 2 | 0 | 0 | 20.92 -> 14.28 | 37 | 74 passed in 36.95s |
| C | 3 | 0 | 0 | 16.41 -> 17.09 | 39 | 74 passed in 37.91s |
| C | 4 | 0 | 0 | 10.92 -> 12.31 | 38 | 74 passed in 37.58s |
| C | 5 | 0 | 0 | 13.52 -> 12.45 | 38 | 74 passed in 38.14s |
| C | 6 | 0 | 0 | 12.97 -> 11.96 | 38 | 74 passed in 37.24s |
| C | 7 | 0 | 0 | 10.74 -> 8.85 | 38 | 74 passed in 37.06s |
| C | 8 | 0 | 0 | 8.84 -> 10.49 | 38 | 74 passed in 38.10s |
| C | 9 | 0 | 0 | 13.37 -> 12.69 | 39 | 74 passed in 38.20s |
| C | 10 | 0 | 0 | 18.03 -> 21.63 | 38 | 74 passed in 38.03s |
| C | 11 | 0 | 0 | 18.59 -> 15.39 | 39 | 74 passed in 38.60s |
| C | 12 | 0 | 0 | 16.34 -> 20.94 | 39 | 74 passed in 38.13s |
| C | 13 | 0 | 0 | 18.98 -> 19.01 | 39 | 74 passed in 38.49s |
| C | 14 | 0 | 0 | 24.02 -> 21.21 | 38 | 74 passed in 37.86s |
| C | 15 | 0 | 0 | 21.33 -> 15.81 | 39 | 74 passed in 38.22s |
| C | 16 | 0 | 0 | 12.37 -> 9.93 | 39 | 74 passed in 38.26s |
| C | 17 | 0 | 0 | 13.23 -> 14.65 | 37 | 74 passed in 37.04s |
| C | 18 | 0 | 0 | 12.40 -> 11.37 | 38 | 74 passed in 37.79s |
| C | 19 | 0 | 0 | 12.63 -> 15.02 | 38 | 74 passed in 37.92s |
| C | 20 | 0 | 0 | 14.63 -> 14.64 | 39 | 74 passed in 37.91s |

## Reading the table against the debt's question

The debt asked whether the flake belongs to xdist or to coverage's `multiprocessing` concurrency. The isolation
did not separate them: none of the three configurations reproduced it, so there is no configuration in which it
is present and another in which it is absent. Nothing here says the cause is xdist, and nothing says it is
coverage. At 0 of 20 per configuration the 95 % upper bound on a per-loop rate is about 14 % (0 of 60 pooled:
about 5 %), so these loops could not have seen a 1-in-43 flake with any confidence either way; adding the 40
two-file loops 17-04 made (0 of 40, also silent) gives 0 of 100 two-file loops, about 3 % at the same bound.

What the counts do show is where it has not appeared. Every recorded occurrence (the pre-commit hook run, 17-04's
proof run 2, CI run 37460451701, 19-01's baseline run 2) came from a whole-suite run, a `make verify`, and none from
a run of the two process-spawning files alone. As the debt and 19-01 record them, the local whole-suite runs read 17-04
1 failure in 3, Phase 18 0 in 4, 19-01 1 in 5 (four baseline runs and the later `make verify`): 2 of 12. At that rate
100 silent two-file loops would be very unlikely (about 0.83^100), so the loops probably do not sample the same
population as the gate. ASSUMPTION, not measured: what the whole suite adds is other test files on the same worker
(`tests/test_model.py` builds with the CAD kernel, the largest share of the gate) before or around the pool tests, and
the longer life of the run, but the loops did not vary either, so which of these matters, if either, is open. The
failing test differs between the occurrences that logged one (`test_three_same_tick_same_slot_timeouts_each_end_in_a_documented_refusal`
on `gw2` in 17-04; `test_a_dying_worker_surfaces_as_broken_pool_and_is_replaced` in CI, worker not recorded in the
debt, and on `gw0` in 19-01), which fits a shutdown-order race at a worker's teardown more than a defect in one test, but that is a reading, not a count.

No occurrence was localised to a pool a test leaves to its finalizer, so a shutdown-order fix would have nothing in
this record to point at.
