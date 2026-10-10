# A whole-suite `make verify` hung near the end with no failure, no crash report and no survivor

Severity: must
Status: active
Date: 2026-10-10
Source: the Phase 21 orchestrator's post-wave gate after plan 21-03 (`HEAD` `bf0650b`), run by
the harness with a 600 s limit; the whole log is kept at
`.planning/phases/21-browser-test-of-the-viewer/investigation/2026-10-10-wave3-make-verify-hang-at-600s.log`
Related files:
- `Makefile:170` (the `test` target: `pytest -n 8 --cov`)
- `docs/tech_debt/active/2026-10-06-wedged-worker-holds-process-exit.md` (a wedged `BuildPool`
  worker holds process exit — the one known way a pytest-xdist worker could fail to exit)
- `docs/tech_debt/active/2026-10-06-resource-tracker-flake-fails-the-gate.md` (fails loudly;
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
