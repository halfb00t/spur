# http-api

`src/spur/app.py`. One file; promote to a directory when it stops holding it.

## Responsibility

Serve the gear over HTTP — the parameter schema, the derived dimensions, the STL and
STEP downloads — and serve the web UI's static files. It owns exactly one policy of its
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
| `GET /api/health` | `{"status": "ok", "version": ..., "pool": {"workers": N, "queue_available": M, "workers_replaced": R}}` |
| `GET /api/schema` | `GearParams.model_json_schema()` — the form is built from this |
| `GET /api/info?…[&mate_teeth=N]` | `derive()`, optionally `with_mate()` |
| `GET /api/model.{stl,step}?…` | the bytes, with `Content-Disposition` from `params.slug()` |

Two request models subclass `GearParams`: `InfoQuery` adds `mate_teeth`, `ModelQuery`
adds `quality`. `_gear(q)` strips them back to a plain `GearParams` before anything
downstream sees them — Pydantic equality includes the class, so without this a
`ModelQuery` and an `InfoQuery` describing the same gear would never share a cache entry.
That is the whole reason the function exists, and the code says so.

`GZipMiddleware` above 1024 bytes: STEP compresses ~6×, STL ~4×.

`/api/health`'s pool fields (D-13) nest under one `pool` key rather than sitting flat at
the top level next to `status`/`version` (02-03-PLAN.md Task 3 checkpoint decision,
option B): the health response is a published contract the web UI and Phase 4's typed
OpenAPI work both inherit, and every later pool field lands inside `pool` without
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
- `BuildError` from the kernel → `422` with the kernel's message (`detail[0].type ==
  "build_error"`).
- A build that exceeds `SPUR_BUILD_TIMEOUT` → `503` + `Retry-After`, **not** `422`
  (`detail[0].type == "timeout"`, D-12): the same gear succeeds on faster hardware or a
  less loaded moment, so overrunning is a property of this machine and this instant, not
  of the parameters — a `422` would wrongly tell the caller to change a gear that is fine.
- A build worker that dies unexpectedly (`BrokenProcessPool`) → `503` + `Retry-After`
  (`detail[0].type == "pool_broken"`, D-12). The dead executor is replaced before this
  reaches the client; the request itself can simply be retried.
- Queue full → `503` + `Retry-After` (`detail[0].type == "busy"`).
- The four `detail[0].type` values above (`build_error`, `timeout`, `pool_broken`,
  `busy`) are pairwise distinct and form a closed set the UI can switch on.
- There is **no authentication**. Deliberate, documented in the README, and the reason
  `compose.yaml` binds to `127.0.0.1`. Tracked as
  `docs/tech_debt/active/2026-09-21-no-authentication.md` with a trigger, so the decision
  is re-taken rather than inherited if this is ever exposed.

## Logging

None. See `docs/tech_debt/active/2026-09-21-no-structured-logging.md` — a `503`, a
`BuildError` and a slow build are all invisible in production today.

## Tests

`tests/test_api.py`, through `TestClient`, exercising the export inline (an autouse
fixture overrides the pool-backed `build_backend` dependency, D-15): health, index and
static, the schema actually carrying the form metadata, `info` with a mate, both
downloads with their media types and magic bytes, the `422` shapes, the impossible-mate
warning, the small-gear case, and `test_a_saturated_service_refuses_instead_of_queueing`
for L04.

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
