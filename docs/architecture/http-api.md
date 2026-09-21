# http-api

`src/spur/app.py`. One file; promote to a directory when it stops holding it.

## Responsibility

Serve the gear over HTTP — the parameter schema, the derived dimensions, the STL and
STEP downloads — and serve the web UI's static files. It owns exactly one policy of its
own: how much work it is willing to accept at once.

## Boundaries

- Calls `calc` and `model`; neither calls back.
- **Admission control lives here, not in `model.py`** (L04). A bounded, non-blocking
  semaphore (`SPUR_MAX_QUEUED_BUILDS`, default 4) guards the model endpoints. Full →
  `503` with `Retry-After: 5`. Queueing past that buys latency and memory, not
  throughput, because every build serialises on the kernel lock anyway (L06).
- Enforced by contract: `spur.cli` may not import `spur.app`, `fastapi` or `starlette`.

## Shape

| Endpoint | Returns |
|---|---|
| `GET /` | the UI (`static/index.html`) |
| `GET /api/health` | `{"status": "ok", "version": ...}` |
| `GET /api/schema` | `GearParams.model_json_schema()` — the form is built from this |
| `GET /api/info?…[&mate_teeth=N]` | `derive()`, optionally `with_mate()` |
| `GET /api/model.{stl,step}?…` | the bytes, with `Content-Disposition` from `params.slug()` |

Two request models subclass `GearParams`: `InfoQuery` adds `mate_teeth`, `ModelQuery`
adds `quality`. `_gear(q)` strips them back to a plain `GearParams` before anything
downstream sees them — Pydantic equality includes the class, so without this a
`ModelQuery` and an `InfoQuery` describing the same gear would never share a cache entry.
That is the whole reason the function exists, and the code says so.

`GZipMiddleware` above 1024 bytes: STEP compresses ~6×, STL ~4×.

## Errors

- Parameters that cannot make a part → `422`, from `GearParams`'s own validator, with the
  offending fields in `detail[].ctx.fields` (L03).
- `BuildError` from the kernel → `422` with the kernel's message.
- Queue full → `503` + `Retry-After`.
- There is **no authentication**. Deliberate, documented in the README, and the reason
  `compose.yaml` binds to `127.0.0.1`. Tracked as
  `docs/tech_debt/active/2026-09-21-no-authentication.md` with a trigger, so the decision
  is re-taken rather than inherited if this is ever exposed.

## Logging

None. See `docs/tech_debt/active/2026-09-21-no-structured-logging.md` — a `503`, a
`BuildError` and a slow build are all invisible in production today.

## Tests

`tests/test_api.py`, 12 tests through `TestClient`: health, index and static, the schema
actually carrying the form metadata, `info` with a mate, both downloads with their media
types and magic bytes, the `422` shapes, the impossible-mate warning, the small-gear
case, and `test_a_saturated_service_refuses_instead_of_queueing` for L04.

Run: `make verify`, or `.venv/bin/python -m pytest tests/test_api.py -q`.
