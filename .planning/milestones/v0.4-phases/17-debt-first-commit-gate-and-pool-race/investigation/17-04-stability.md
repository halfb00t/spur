# 17-04 stability runs behind the same-slot timeout race fix

Date: 2026-10-06. Machine: 12 CPUs, arm64, 32.0 GiB RAM (`bench.machine_facts()`).

Commands, one log per run (each log opens with `load=` and `utc=` and closes with `exit=`):

- `.venv/bin/python -m pytest -n 8 --cov --cov-report=term --cov-fail-under=0 -q tests/test_pool.py tests/test_api.py` x 20
- the same at `-n 4` x 20
- `make verify` x 3 (the whole gate: ruff, mypy, contracts, unfinished-work scan, pytest at `-n 8 --cov`)

Code under test: src/spur/pool.py blob 2e2a9b6a91ce4b13615d24f3911fd8ddee95fbec, tests/test_pool.py blob 322107c7c556cd3ea3c5e9c46886f1f18a1b371c

| run | mode | 1-min load | exit | pytest summary | pool.py cover | reentrant tracker | log |
| --- | ---- | ---------- | ---- | -------------- | ------------- | ----------------- | --- |
| n8-01 | -n 8 --cov | 5.15 | 0 | 74 passed in 18.94s | 100.00% | no | - |
| n8-02 | -n 8 --cov | 7.84 | 0 | 74 passed in 18.65s | 100.00% | no | - |
| n8-03 | -n 8 --cov | 7.39 | 0 | 74 passed in 19.35s | 100.00% | no | - |
| n8-04 | -n 8 --cov | 8.94 | 0 | 74 passed in 18.32s | 100.00% | no | - |
| n8-05 | -n 8 --cov | 7.71 | 0 | 74 passed in 18.36s | 100.00% | no | - |
| n8-06 | -n 8 --cov | 9.45 | 0 | 74 passed in 18.24s | 100.00% | no | - |
| n8-07 | -n 8 --cov | 9.19 | 0 | 74 passed in 18.24s | 100.00% | no | - |
| n8-08 | -n 8 --cov | 10.99 | 0 | 74 passed in 19.26s | 100.00% | no | - |
| n8-09 | -n 8 --cov | 10.73 | 0 | 74 passed in 18.75s | 100.00% | no | - |
| n8-10 | -n 8 --cov | 12.92 | 0 | 74 passed in 19.98s | 100.00% | no | - |
| n8-11 | -n 8 --cov | 12.18 | 0 | 74 passed in 19.93s | 100.00% | no | - |
| n8-12 | -n 8 --cov | 11.02 | 0 | 74 passed in 19.07s | 100.00% | no | - |
| n8-13 | -n 8 --cov | 11.09 | 0 | 74 passed in 19.34s | 100.00% | no | - |
| n8-14 | -n 8 --cov | 11.45 | 0 | 74 passed in 18.69s | 100.00% | no | - |
| n8-15 | -n 8 --cov | 11.25 | 0 | 74 passed in 18.45s | 100.00% | no | - |
| n8-16 | -n 8 --cov | 10.94 | 0 | 74 passed in 18.32s | 100.00% | no | - |
| n8-17 | -n 8 --cov | 10.56 | 0 | 74 passed in 19.40s | 100.00% | no | - |
| n8-18 | -n 8 --cov | 9.31 | 0 | 74 passed in 19.38s | 100.00% | no | - |
| n8-19 | -n 8 --cov | 11.76 | 0 | 74 passed in 18.85s | 100.00% | no | - |
| n8-20 | -n 8 --cov | 11.00 | 0 | 74 passed in 19.93s | 100.00% | no | - |
| n4-01 | -n 4 --cov | 10.29 | 0 | 74 passed in 17.36s | 100.00% | no | - |
| n4-02 | -n 4 --cov | 10.15 | 0 | 74 passed in 17.28s | 100.00% | no | - |
| n4-03 | -n 4 --cov | 9.63 | 0 | 74 passed in 17.68s | 100.00% | no | - |
| n4-04 | -n 4 --cov | 11.75 | 0 | 74 passed in 17.54s | 100.00% | no | - |
| n4-05 | -n 4 --cov | 11.44 | 0 | 74 passed in 17.98s | 100.00% | no | - |
| n4-06 | -n 4 --cov | 14.71 | 0 | 74 passed in 17.26s | 100.00% | no | - |
| n4-07 | -n 4 --cov | 13.27 | 0 | 74 passed in 17.11s | 100.00% | no | - |
| n4-08 | -n 4 --cov | 14.00 | 0 | 74 passed in 17.24s | 100.00% | no | - |
| n4-09 | -n 4 --cov | 13.60 | 0 | 74 passed in 17.46s | 100.00% | no | - |
| n4-10 | -n 4 --cov | 11.97 | 0 | 74 passed in 17.64s | 100.00% | no | - |
| n4-11 | -n 4 --cov | 12.81 | 0 | 74 passed in 17.35s | 100.00% | no | - |
| n4-12 | -n 4 --cov | 12.42 | 0 | 74 passed in 17.54s | 100.00% | no | - |
| n4-13 | -n 4 --cov | 11.09 | 0 | 74 passed in 17.47s | 100.00% | no | - |
| n4-14 | -n 4 --cov | 10.02 | 0 | 74 passed in 17.67s | 100.00% | no | - |
| n4-15 | -n 4 --cov | 9.56 | 0 | 74 passed in 17.55s | 100.00% | no | - |
| n4-16 | -n 4 --cov | 10.17 | 0 | 74 passed in 17.31s | 100.00% | no | - |
| n4-17 | -n 4 --cov | 9.79 | 0 | 74 passed in 17.39s | 100.00% | no | - |
| n4-18 | -n 4 --cov | 10.28 | 0 | 74 passed in 17.44s | 100.00% | no | - |
| n4-19 | -n 4 --cov | 10.18 | 0 | 74 passed in 17.36s | 100.00% | no | - |
| n4-20 | -n 4 --cov | 10.07 | 0 | 74 passed in 17.29s | 100.00% | no | - |
| verify-1 | make verify | 8.69 | 0 | 943 passed in 70.64s (0:01:10) | 100.00% | no | - |
| verify-2 | make verify | 17.54 | 2 | 1 failed, 942 passed in 76.50s (0:01:16) | 100.00% | yes | 17-04-verify-2.log |
| verify-3 | make verify | 19.45 | 0 | 943 passed in 61.39s (0:01:01) | 100.00% | no | - |

Tally: -n 8 --cov 20/20 green; -n 4 --cov 20/20 green; make verify 2/3 green.

Wall time of each `make verify` (`/usr/bin/time -p`): verify-1 71.44 s, verify-2 77.34 s, verify-3 62.18 s.

Coverage flush read: `src/spur/pool.py` read 100.00% in 43 of 43 runs; no run lost lines.

## The one non-green run

`verify-2` failed `tests/test_pool.py::test_three_same_tick_same_slot_timeouts_each_end_in_a_documented_refusal` at 1-min load 17.54, worker `gw2`. Every assertion in the test passed. The failure is an `ExceptionGroup` of five `PytestUnraisableExceptionWarning`s at the end of the call phase: `ReentrantCallError` / `ResourceTracker called reentrantly` inside `multiprocessing.synchronize._cleanup`, and `filterwarnings = ["error"]` turns them into a failure. It is the known flake in `docs/tech_debt/active/2026-10-06-resource-tracker-flake-fails-the-gate.md`, whose first occurrence predates these tests (it hit a run that touched only `.planning/`). The occurrence was recorded in `b8ef84a`; its whole log is `17-04-resource-tracker.log`, and `17-04-verify-2.log` is the same file under the name this table's column names. The human decided `proceed-as-known-flake`: the fix stands as-is and a second occurrence is a trigger for a later plan through the debt item, not for this one.

Of the 43 runs, 1 printed the reentrant-tracker text (`verify-2`); the 40 loop runs and the other two gates did not.
