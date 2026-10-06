# A same-slot timeout cleanup race produces an undocumented 500 instead of a 503

Severity: must
Status: resolved
Date: 2026-10-02
Resolved in: 0628182 (the race); 7af75af (the margin)
Source: 13-06's SC3 measurement (`.planning/milestones/v0.3-phases/13-latency-bar/investigation/sc3*`),
the composed worst row under ten concurrent builds — the question
`docs/tech_debt/resolved/2026-09-28-tip-chamfer-narrows-the-build-timeout-margin.md` left
open ("nothing here measures the chamfer under concurrent load"), re-homed into
`docs/tech_debt/active/2026-09-23-concurrent-latency-bar-waived.md`'s trigger (12-CONTEXT.md
D-04) and answered here (D-13..D-16).
Related files:
- `src/spur/pool.py` (`_run_with_timeout`'s `except TimeoutError` branch; `recreate_for`)
- `bench/latency.py` (`run_composed`, `_fetch`, `scenario_composed` — D-15's scenario that
  measured this)
- `bench/RESULTS.md` ("### Composed worst row under ten concurrent builds (Phase 13)")
- `.planning/milestones/v0.3-phases/13-latency-bar/investigation/sc3.server1.records.jsonl`,
  `sc3-run1.stderr.txt`

## Context

SC3 fired the composed sweep's worst row (29.42 s alone) plus the next nine heaviest rows
(D-13) at a fresh server with shipping defaults (2 workers, 4 queued builds, 30 s per-build
timeout). Admission control refused six (`503 busy`, as designed) and admitted four; D-07's
hash affinity (`executor_for`, `hash(p) % self.workers`) routed two of the four onto each of
the two worker slots — not controllable from the client, and not something SC3's ten
distinct keys were chosen to prevent (D-13's own point was to spread admitted builds over
both workers, not to guarantee one request per slot).

Both requests on a given slot timed out within the same incident (recorded `duration_ms`
30002-30004 for the pair on each slot). `_run_with_timeout`'s `except TimeoutError` branch
(`src/spur/pool.py` lines 183-210) is not re-entrant-safe against this: each request holds
its own `executor` local, captured once at the top of the method
(`executor = self.executor_for(p)`, line 169) — the same `ProcessPoolExecutor` object for
both requests on the same slot, since neither request has triggered a replacement yet when
both start. When the first request's timeout branch runs, it terminates every process of
that executor (line 204-205), then calls `self.recreate_for(p, executor, "timeout")`, which
(after the identity check passes, since nothing has replaced this slot's executor yet)
calls `self._executors[i].shutdown(wait=False)` on the *same* executor object and installs a
brand new one in its place (`recreate_for`, lines 151-153). The second request's own timeout
branch, running moments later against its own `executor` local — which still refers to the
now-shut-down object, not the new one `recreate_for` installed — then runs line 204's
`for proc in executor._processes.values():` against an executor whose `_processes` is `None`
post-shutdown, raising `AttributeError: 'NoneType' object has no attribute 'values'`. That
exception is unhandled (no FastAPI exception handler maps `AttributeError`), so uvicorn logs
"Exception in ASGI application" and the client receives a raw `500` — not one of the three
documented `503` `detail[0].type` values (`busy` | `timeout` | `pool_broken`,
`src/spur/app.py`). Measured twice in this one run, once per slot (requests `912cd2d4` and
`0fc30d53`; the clean-timeout requests on the same two slots were `51e80f35` and
`4b777b09`); never attribute the termination to `recreate_for` — `recreate_for`'s own
identity guard (the comment at lines 100-122) is working exactly as designed and is not the
site of the crash. The crash is in the *second* caller's own `_run_with_timeout` branch
reading a reference that `recreate_for`'s *first* caller already invalidated.

**Also observed: the worst row's own margin disappears under this contention.** The worst
row (`51e80f35`, 29.42 s alone, 0.58 s of margin per Phase 12's re-run) was recorded
`build.failed` with the documented `BuildTimeout` exception at `duration_ms: 30004` — it did
not finish inside the 30 s budget once run beside the other admitted requests, even though
it was the one request actually executing (not queued) on its slot. This is the same
"nothing measures the chamfer under concurrent load" question this phase was scoped to
answer, and the composition supplies its own answer: the single-build margin the resolved
debt file measured does not survive concurrent load on this host.

## Why it matters

A `500` is not one of this service's three documented failure modes; a client written
against `/api/model.stl`'s contract (busy / timeout / pool_broken, each with a `detail[0]`
body) has no branch for it and will surface a raw server error to whoever is waiting on a
part. The underlying mechanism — a queued request's timeout clock starting at submission,
so queue wait on a shared slot counts toward the 30 s (the `<specifics>` ASSUMPTION this
plan's CONTEXT.md flagged, now measured, not assumed) — means any two heavy, same-hash-slot
requests landing close together can reproduce this, not just SC3's specific ten rows. And
the margin finding means the resolved tip-chamfer debt's "~1.02x" headline number was never
true under load; a host slower than this M2 Max, or any contention at all, pushes the worst
composed row over its own budget.

## Next step

The deferred ten-identical-worst-row scenario (`13-CONTEXT.md` `<deferred>`) isolates queue
wait from kernel contention for a single hash slot, cleanly reproducing this crash without
relying on hash-affinity luck. Once that is run, the `src/` fix this debt implies is a
narrower scope than today's whole-executor swap: `_run_with_timeout`'s `except TimeoutError`
branch needs to detect that its own `executor` local has already been replaced (compare
identity against `self._executors[i]`, the same check `recreate_for` already does for its
own replacement, before touching `executor._processes`) and skip straight to raising
`BuildTimeout` without re-terminating or re-replacing an executor that is no longer live.

## Revisit when

The ten-identical-worst-row scenario is run, a `500` (as opposed to the documented `503`
types) is observed in production, `_run_with_timeout` or `recreate_for` is next touched, or
`SPUR_BUILD_TIMEOUT`'s default is reconsidered (the margin finding above).

## Resolution (2026-10-06)

**The race** fixed in `0628182` (17-04). `_run_with_timeout`'s `except TimeoutError` branch now
terminates and replaces the worker only when two facts hold: the slot still holds this request's
own executor, and that executor's `_processes` is not `None`. The `raise BuildTimeout` after it is
unconditional, so a same-slot sibling that lost the race gets the documented `503 timeout` where
it used to get an `AttributeError` and a raw `500`. Identity alone was not enough: `shutdown()`
leaves the slot holding the same executor object with `_processes` `None`, so `BuildPool._closed`
(set first in `shutdown()`, honoured by `recreate_for`) stops a closed pool building a
replacement nobody would shut down. Four tests: the stale executor
(`test_a_stale_executor_timeout_is_a_build_timeout_not_an_attribute_error`), three same-tick
siblings, the closed pool, and an ast check that the timeout branch never awaits. Red against
the unfixed pool, `3 failed, 1 passed` (the passing one is the ast check, which is meant to pass
on the old code and has a seeded await proving it can fail); green after, `74 passed` for
`tests/test_pool.py` and `tests/test_api.py`. Loops: 20 of 20 at `-n 8 --cov`, 20 of 20 at
`-n 4 --cov`, and 2 of 3 whole `make verify` runs, the third lost to the resource-tracker flake
and accepted by the human (`investigation/17-04-stability.md` under
`.planning/phases/17-debt-first-commit-gate-and-pool-race/`). The bench before and after:
`identical` reproduced three `500`s with three `AttributeError` records on `814f4f3` (attempt 1),
and on `0628182` four admitted requests all ended `503 timeout` with no `500` and no
`AttributeError` (`bench/RESULTS.md` "## Same-slot timeout race (Phase 17)"). The deterministic
test, not the bench, is the proof.

**The margin** decided in L37: recorded as documented behaviour, no default moved.
`SPUR_BUILD_TIMEOUT` stays 30 s and `spoke_count`'s `le` stays 32; the heaviest allowed composed
row reads 29.42 s alone (0.58 s of margin) and under load ended `BuildTimeout` at `duration_ms`
30004 with both workers busy (SC3) and `503 timeout` at 30003 ms with one worker busy and three
queued (Phase 17, at loads 5.48 to 5.88 and 18.94 to 15.30). `503 timeout` is its contract, a
slower or busier host raises the variable, and the limit is in `README.md`, in `src/spur/app.py`'s comment
and as dated notes in `bench/RESULTS.md` and the resolved tip-chamfer debt. Revisit at Phase 19's
composed re-measure or on any change to the default or an `le` cap.

<!-- On resolve: set Status: resolved, add `Resolved in: <commit sha>`,
     git mv into resolved/, move the INDEX row to Resolved — same commit as the fix. -->
