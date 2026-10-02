# A same-slot timeout cleanup race produces an undocumented 500 instead of a 503

Severity: must
Status: active
Date: 2026-10-02
Source: 13-06's SC3 measurement (`.planning/phases/13-latency-bar/investigation/sc3*`),
the composed worst row under ten concurrent builds — the question
`docs/tech_debt/resolved/2026-09-28-tip-chamfer-narrows-the-build-timeout-margin.md` left
open ("nothing here measures the chamfer under concurrent load"), re-homed into
`docs/tech_debt/active/2026-09-23-concurrent-latency-bar-waived.md`'s trigger (12-CONTEXT.md
D-04) and answered here (D-13..D-16).
Related files:
- `src/spur/pool.py` (`_run_with_timeout`'s `except TimeoutError` branch, lines 183-210,
  specifically line 204; `recreate_for`, lines 99-155)
- `bench/latency.py` (`run_composed`, `_fetch`, `scenario_composed` — D-15's scenario that
  measured this)
- `bench/RESULTS.md` ("### Composed worst row under ten concurrent builds (Phase 13)")
- `.planning/phases/13-latency-bar/investigation/sc3.server1.records.jsonl`,
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

<!-- On resolve: set Status: resolved, add `Resolved in: <commit sha>`,
     git mv into resolved/, move the INDEX row to Resolved — same commit as the fix. -->
