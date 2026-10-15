# A whole-suite `make verify` hung near the end with no failure, no crash report and no survivor

Severity: must
Status: active
Date: 2026-10-10
Source: the Phase 21 orchestrator's post-wave gate after plan 21-03 (`HEAD` `bf0650b`), run by
the harness with a 600 s limit; the whole log is kept at
`.planning/phases/21-browser-test-of-the-viewer/investigation/2026-10-10-wave3-make-verify-hang-at-600s.log`
Related files:
- `Makefile:185` (the `test` recipe: `pytest -n 8 --cov -v --durations=25`; was line 170 when the run hung)
- `docs/tech_debt/active/2026-10-06-wedged-worker-holds-process-exit.md` (a wedged `BuildPool`
  worker holds process exit — the one known way a pytest-xdist worker could fail to exit)
- `docs/tech_debt/resolved/2026-10-06-resource-tracker-flake-fails-the-gate.md` (fails loudly;
  not this symptom)
- `docs/tech_debt/active/2026-10-09-xdist-worker-segfaults-in-occt-at-exit.md` (crashes after
  reporting; not this symptom)

## Context
One run of `make verify` on 2026-10-10 (~11:21Z, Apple M5 Max, macOS, Python 3.12.15, pytest
9.1.1, xdist 3.8.0, `-n 8 --cov`, 1220 items) passed ruff and mypy, then printed progress dots
through the `94%` line plus fifty more dots (about 1200 of 1220 items reported, no `F`, no `E`)
and produced nothing further until the harness sent SIGTERM at 600 s
(`make: *** [Makefile:170: test] Terminated: 15`). No `pytest`, `uvicorn` or headless-shell
process survived the kill, and no macOS crash report was written in that window. The gates
immediately before it read 172.56 s, 163.53 s and 152.97 s; the re-run on the identical tree,
started about 20 minutes later, read `1220 passed in 175.80s`, coverage 97.75 %.

What is known: the run stalled after almost every test had reported and before the final
summary, which is the window in which xdist workers finish their last items and exit, and in
which `tests/test_pool.py`'s spawned `BuildPool` workers shut down. What is not known: which
worker or test stalled (progress dots carry no ids), whether a `BuildPool` child was wedged
(the wedged-worker item's symptom), or whether the stall was in pytest-cov's
`multiprocessing` data flush. The log has no per-test timing because the gate runs without
`--durations` or `-v`.

## Why it matters
L13/L34 make `make verify` the one definition of "passing". A gate that neither passes nor
fails costs a re-run plus the time to notice (10 minutes here, and a harness that kills at a
fixed limit; a human waiting on a terminal would lose more). One occurrence with no cause
cannot be fixed, only watched; two with the same shape would justify running the gate with
`--timeout` per test or `-v` so the next hang names its test.

## Next step
Revisit at the next hang: keep its whole log, note the host load, and run
`make test PYTEST_ARGS="-v --durations=20"` on the same tree right after it to get test ids
and timings next to the stall. Also revisit when `BuildPool.shutdown` is next touched (the
wedged-worker item's trigger), since a wedged pool worker holding a pytest process's exit is
the one mechanism already on file that produces exactly this shape.

2026-10-15 (26-05): the evidence is now on for every `make verify`: `-v` names each test and
`faulthandler_timeout = 120` dumps a stalled test's stack (see the runbook below). The item
stays active until a stall is captured; no cause is claimed.

## Runbook (Phase 26)

The gate now runs `pytest -n 8 --cov --cov-report=term -v --durations=25`, and
`pyproject.toml` sets `faulthandler_timeout = 170`, dump-only (the run carries on). Proved
once with a throwaway 30 s test at `-n 8 --cov` and a 5 s timeout
(`.planning/phases/26-gate-fails-with-a-cause/investigation/26-05-stall.log`).

### What a stalled gate prints
- Each test's start line from `-v`, `path::test_name`, with no worker id.
- Each finish line as `[gwN] [ NN%] PASSED <id>`; they arrive out of order across workers.
- After 170 s inside one test item, a `Timeout (0:02:50)!` dump from the stalled worker on
  stderr: every thread's stack, with `File ".../test_x.py", line N in test_name`. It names
  the function, not the parametrize id, and it may begin mid-line, glued to a controller line
  that was being written.
- On a run that ends, the 25 slowest phases under `slowest 25 durations`.

### How to read it
1. In flight = started minus finished: take the ids of the start lines and drop those with a
   finish line.
2. Pair the dump's function with the in-flight ids of that function; a parametrized test has
   one in-flight id per running case, so the dump narrows it to the function and the
   in-flight set names the cases.
3. Keep the whole log and the host's 1-minute load (`uptime`).

### What it cannot see
The timer is armed per test item. A stall after a worker's last test, in xdist's worker
shutdown or in pytest-cov's combine, leaves no dump: `-v` then shows every test finished and
the run still waiting. The 2026-10-10 hang had about 20 of 1220 items unreported, so it may
have been inside a test (now covered) or after the last one (not covered); the log cannot
say which.

### Operator step for that window
Note the time, keep the whole log, and list the processes:
`ps -Ao pid,ppid,etime,command | grep -E 'pytest|xdist'`. On macOS, `kill -ABRT <pid>` of the
stalled worker writes a crash report with native stacks (UNVERIFIED here, 26-RESEARCH A6; on
CI none is kept).
