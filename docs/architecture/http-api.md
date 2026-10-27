# http-api

`src/spur/app.py`. One file; promote to a directory when it stops holding it.

## Responsibility

Serve the gear over HTTP — the parameter schema, the derived dimensions, the STL and
STEP downloads — and, under `/api/shaft/`, the same three for the DIN 5480 shaft, and serve the
web UI's static files. It owns exactly one policy of its
own: how much work it is willing to accept at once.

## Boundaries

- Calls `calc` directly, and `model` only indirectly: `app.py` no longer imports
  `model.py` (Phase 2, D-02). It calls `pool.py`'s `BuildPool`, which routes each build
  to one of `SPUR_BUILD_WORKERS` spawned worker processes; only the worker imports
  `model.py`, at runtime, via `importlib`. Enforced by contract, not just reviewed: the
  import-linter contract `The serving process never imports the CAD kernel`
  (`allow_indirect_imports = false`, scoped to `spur.app`) fails `make verify` if a
  future change puts `cadquery`/`OCP` back in the serving process's import graph.
- **Admission control lives here, not in `model.py`** (L04). A bounded, non-blocking
  semaphore (`SPUR_MAX_QUEUED_BUILDS`, derived from `SPUR_BUILD_WORKERS` as ~2×N, D-09)
  guards the model endpoints. Full → `503` with `Retry-After: 5`. Queueing past that
  buys latency and memory, not throughput — the pool has only `SPUR_BUILD_WORKERS`
  processes to actually run a build on. The claim that every build serialises on one
  kernel lock (L06) no longer holds: builds now run in `SPUR_BUILD_WORKERS` independent
  worker processes, routed by parameter-hash affinity (D-07) — a hot gear still
  serialises against itself (same worker, one task at a time), but different gears no
  longer queue behind each other.
- A per-build timeout (`SPUR_BUILD_TIMEOUT`) bounds how long any one build may run
  (D-10). A build that overruns has its worker process terminated — not merely
  abandoned — and that hash slot's executor is replaced before the next request for it
  is served.
- Enforced by contract: `spur.cli` may not import `spur.app`, `fastapi` or `starlette`.

## Shape

| Endpoint | Returns |
|---|---|
| `GET /` | the UI (`static/index.html`) |
| `GET /api/health` | a `HealthReport`: `{"status": "ok", "version": ..., "pool": {"workers": N, "queue_available": M, "workers_replaced": R}}`, with `pool` `null` only when the app runs without its lifespan |
| `GET /api/schema` | `GearParams.model_json_schema()` — the form is built from this; a field's `enabled_when` is a list of `{field, op, value}` conditions (`op` `eq` or `gt`, all must hold) under which it does anything — display metadata, not validation (`L41`); a top-level `selectors` list, each `{title, group, options: [{label, when}]}` with `when` in the same `{field, op, value}` vocabulary, is display metadata too, and is not in `/openapi.json` (`L42`) |
| `GET /api/info?…[&mate_teeth=N]` | `derive(params, mate_teeth=…)` → a `DerivedDimensions` document; every key always present, `null` where a value does not apply |
| `GET /api/model.{stl,step}?…` | the bytes, with `Content-Disposition` from `params.slug()`: `spur_z{teeth}_m{module}_pa{pressure_angle}`, with `_trochoid` appended exactly when the hob root is what the part is built with (`L40`); a radial part, and a `root_shape=trochoid` request `calc.root_mode` ignores or refuses, keep the plain name |

| `GET /api/shaft/schema` | `ShaftParams.model_json_schema()`, with a top-level `dims` list of `{key, label, unit}`, one row per `ShaftDimensions` key but `warnings`, in its order: the result rows ride the schema so the page needs no second row table (`L49`) |
| `GET /api/shaft/info?…` | `derive_shaft(params)` → a `ShaftDimensions` document, every key always present, `null` where a value does not apply |
| `GET /api/shaft/model.{stl,step}?…` | the shaft's bytes through the same `_serve_model` as the gear's, named by `ShaftParams.slug()`: `spur_shaft_w{reference_d}x{module}x{teeth}`, frozen (`L49`); `spur_shaft_w25x1.25x18.stl` for the default |

The shaft takes its eight `ShaftParams` fields as query keys, plus `designation` on both `info` and `model`, and `quality`
on `model`. `designation` (`W 30x2x14x8f`) replaces `reference_d`, `module`, `teeth` and `fit`; it combines freely with
`splined_length`, `end_chamfer`, `shank_d` and `shank_length`. `ShaftInfoQuery` and `ShaftModelQuery` are the shaft's two
request models; `_shaft(q)` strips them to a plain `ShaftParams`, resolving a designation to the four spline fields, so a
designation link and its flat link are one cache entry.

```sh
curl -s 'http://localhost:8000/api/shaft/info?designation=W%2030x2x14x8f&shank_length=0' | jq .
curl -OJ 'http://localhost:8000/api/shaft/model.step?designation=W%2030x2x14x8f'
```

Two request models subclass `GearParams`: `InfoQuery` adds `mate_teeth`, `ModelQuery`
adds `quality`. `_gear(q)` strips them back to a plain `GearParams` before anything
downstream sees them — Pydantic equality includes the class, so without this a
`ModelQuery` and an `InfoQuery` describing the same gear would never share a cache entry.
That is the whole reason the function exists, and the code says so.

`GZipMiddleware` above 1024 bytes: STEP compresses ~6×, STL ~4×.

`/api/health`'s pool fields (D-13) nest under one `pool` key rather than sitting flat at
the top level next to `status`/`version` (02-03-PLAN.md Task 3 checkpoint decision,
option B): the health response is a published contract the web UI reads, and
`/openapi.json` documents it as `HealthReport` with `PoolState`, `pool` always present
(`null` without the lifespan, D-06). Every later pool field lands inside `pool` without
touching that published top level. All three values are parent-local, O(1) reads — worker
count and replacement count come straight off `BuildPool`, and remaining admission
capacity comes from a plain in-flight counter `app.py` keeps itself, not from
`threading.BoundedSemaphore`'s private `_value`. The handler is a synchronous `def`, not
`async def`: there is nothing here for FastAPI to await, and no worker is ever asked
anything, because this endpoint's p95 under load is Phase 2's headline success criterion
and has to measure the event loop, not the pool.

## Errors

- Parameters that cannot make a part → `422`, from `GearParams`'s own validator, with the
  offending fields in `detail[].ctx.fields` (L03).
- A number the page's number box would blank (`5.`, `+22`, ` 22`, `1_0`) → `422` before the
  query is read, one `detail` entry per offending key (`type == "number_as_written"`, `loc ==
  ["query", <field>]`), on `/api/info`, `/api/model.{fmt}` and the shaft's `info` and `model` routes. Every value of a repeated key
  is checked; an empty value and every other malformed token keep pydantic's own `422` (L49).
- A designation given with any of `reference_d`, `module`, `teeth` or `fit` → `422`, whatever the values, checked
  on key presence before any value is read (`type == "conflict"`, `loc == ["query", "designation"]`, `ctx.fields ==
  ["designation", <each present key in spline order>]`). An unreadable designation → `422` `type == "designation"`
  at the same `loc`, with the codec's sentence naming the bad token; an infeasible one (`W 6x0.5x6x8f`) → `422` there
  with the model's own `type` and sentence. No designation is a `500` (`L49`).
- `BuildError` from the kernel → `422` with the kernel's message (`detail[0].type ==
  "build_error"`).
- A build that exceeds `SPUR_BUILD_TIMEOUT` → `503` + `Retry-After`, **not** `422`
  (`detail[0].type == "timeout"`, D-12): the same gear succeeds on faster hardware or a
  less loaded moment, so overrunning is a property of this machine and this instant, not
  of the parameters — a `422` would wrongly tell the caller to change a gear that is fine.
- A build worker that is lost -- dies unexpectedly, or is terminated because another
  request on the same D-07 hash slot overran its timeout -- (`BrokenProcessPool`) →
  `503` + `Retry-After` (`detail[0].type == "pool_broken"`, D-12). The dead executor is
  replaced once per incident before this reaches the client (CR-01/WR-01 review fix);
  the request itself can simply be retried.
- Queue full → `503` + `Retry-After` (`detail[0].type == "busy"`).
- The four `detail[0].type` values above (`build_error`, `timeout`, `pool_broken`,
  `busy`) are pairwise distinct and form a closed set the UI can switch on.
- There is **no authentication**. Deliberate, documented in the README, and the reason
  `compose.yaml` binds to `127.0.0.1`. Tracked as
  `docs/tech_debt/active/2026-09-21-no-authentication.md` with a trigger, so the decision
  is re-taken rather than inherited if this is ever exposed.

## Logging

One JSON-lines logger, on stderr, configured at the composition boundary (`L20`,
`src/spur/records.py`). Every `/api/model` request emits exactly one of the following,
each carrying a per-request `request` id, the gear's `slug` (the same name as the download's, so a record for a hob-root gear carries `_trochoid`, `L40`) and non-default `params`:

| Event | Level | When | Fields beyond the shared envelope |
|---|---|---|---|
| `build.started` | INFO | Immediately before the backend call — the one place a build actually begins | `fmt`, `quality` |
| `export.served` | INFO | Every request that returns bytes, whichever of the three paths served it | `fmt`, `quality`, `encoding`, `source` (`cache` / `compressed` / `built`), `duration_ms` |
| `build.failed` | WARNING for `BuildError`, ERROR for everything else (`BuildTimeout`/`BrokenProcessPool`, or any other exception class `model()` didn't expect) | Any of `model()`'s `except` clauses, including the catch-all (WR-01, review fix) | `fmt`, `quality`, `exception` (the class name), `duration_ms` |
| `queue.refused` | WARNING | `_build_slot()`'s single admission refusal | `fmt`, `quality`, `in_flight`, `max_queued` |

`pool.recreate_for()` also emits `worker.replaced` at ERROR, with the hash slot and a
`cause` of `timeout` or `broken_pool` — the pool-recovery branch this file's own
"replaced once per incident" guarantee describes above. See `L20`.

uvicorn's own access and error records (`uvicorn`, `uvicorn.error`, `uvicorn.access`)
ride the same stream and the same JSON format: `cli.cmd_serve` passes `log_config=None`
to `uvicorn.run`, so uvicorn installs no `dictConfig` of its own and its loggers
propagate to the same root handler `records.configure()` installs (D-02). A record that
itself carries a real traceback -- concretely, uvicorn's own `"Exception in ASGI
application"` line for any exception `model()` doesn't classify -- gets one rendered
into a `traceback` field (CR-01, review fix); `spur`'s own `build_failed()` never sets
`exc_info` on the records it emits, so that field never appears on spur's own vocabulary
(D-06/T-03-05 still holds).

The incident question this answers, from the stderr stream alone, for one request: was
it refused, served from cache, compressed or built; if built, how long; if it failed,
which class; and was a worker replaced. Read locally with `make serve 2>&1 | jq`.

## Tests

`tests/test_api.py`, through `TestClient`, exercising the export inline (an autouse
fixture overrides the pool-backed `build_backend` dependency, D-15): health, index and
static, the schema actually carrying the form metadata, `info` with a mate, both
downloads with their media types and magic bytes, the `422` shapes, the impossible-mate
warning, the small-gear case, and `test_a_saturated_service_refuses_instead_of_queueing`
for L04.

`tests/test_shaft_interfaces.py` is the light file for the shaft's routes (rows, `info`, the as-written
rule, the download name, every designation case), with a stub backend; `tests/test_api.py` adds the real
shaft downloads, the busy refusal and the shared cache entry of a designation and its flat link.

`tests/test_pool.py` proves the actual process boundary and the pool-specific behaviour
`test_api.py`'s inline override can't: one real build routed to and downloaded from a
spawned worker, the parameter-hash affinity routing (same gear, same worker; preview/
fine/STEP share one worker), the private `ProcessPoolExecutor._processes` attribute this
phase's termination path depends on, the timeout-terminate-replace and
broken-pool-replace paths, the three `BuildError`/`BuildTimeout`/`BrokenProcessPool` to
`422`/`503`/`503` mappings and their pairwise-distinct `detail[0].type` values, admission
capacity being restored after every failure, and `/api/health`'s `pool` shape — including
that `queue_available` falls while a slot is held and `workers_replaced` increases after
a forced termination.

Run: `make verify`, or `.venv/bin/python -m pytest tests/test_api.py tests/test_pool.py -q`.
