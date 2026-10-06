# A wedged worker holds process exit until it finishes or is killed

Severity: nice
Status: active
Date: 2026-10-06
Source: Phase 17 incremental code review (`17-REVIEW.md` WR-01, second pass) — measured while correcting the `pool.py` closed-pool comment
Related files:
- `src/spur/pool.py` — `BuildPool.shutdown` and the closed-pool branch of `_run_with_timeout`

## Context
After `BuildPool.shutdown()` sets `_closed`, a request whose build times out raises
`BuildTimeout` (the documented 503) but does not terminate its worker: the guard skips the
terminate-and-replace block because the slot's `_processes` is already `None`. Measured on
Python 3.12.13: with an 8 s task running and `shutdown(wait=False)` called at 1.5 s, the
interpreter did not exit until 8.10 s — process exit waits for the worker rather than
reaping it. A build that never returns would hold the process until a SIGKILL.

## Why it matters
Old behaviour, not a Phase 17 regression, and in the container a process-group exit ends
it. Under uvicorn's graceful shutdown a truly wedged build would stall the exit for as long
as the supervisor's kill timeout allows. Whether that path is reachable at all is
unmeasured (17-04 PLAN Flagged Assumption A4).

## Next step
Revisit when `BuildPool.shutdown` is next touched, or when a graceful shutdown is observed
to hang. The fix shape, if wanted: terminate the slot's live process on the closed-pool
path before raising, so shutdown never waits on a build the request already gave up on.
