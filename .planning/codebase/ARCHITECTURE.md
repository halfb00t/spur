---
last_mapped_commit: 41d23c70643108293120e36d6abd823739892ca8
last_mapped_at: 2026-10-02
---
<!-- refreshed: 2026-10-02 -->

# Architecture

**Analysis Date:** 2026-10-02

## System Overview

```text
┌────────────────────────────────────────────────────────────────────┐
│                  HTTP/CLI Request Entry                            │
│  `src/spur/app.py` (endpoints)  or  `src/spur/cli.py` (commands)   │
└──────────────────┬───────────────────────────────────────────────┘
                   │
         ┌─────────┴─────────┐
         ▼                   ▼
  ┌─────────────────┐  ┌──────────────┐
  │  Pure Maths     │  │ Parameters   │
  │  `calc.py`      │  │ `params.py`  │
  │ (kernel-free)   │  │ (validated)  │
  └─────────────────┘  └──────────────┘
         ▲
         │ (derive dimensions, feasibility)
         │
  ┌──────┴────────────────────────────────────┐
  │  Serving Process (kernel-free)             │
  │  `src/spur/app.py`                         │
  │  • Admission control (`_build_slot`)       │
  │  • Byte cache (`_BlobCache`, 64 MiB)       │
  │  • Worker pool management                  │
  └──────────┬─────────────────────────────────┘
             │ (spawn + route by affinity)
    ┌────────┴────────┬────────────┬─────────────┐
    ▼                 ▼            ▼             ▼
 ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐
 │Worker 1 │Worker 2 │Worker N │...   │  (each: ProcessPoolExecutor, 1-task)
 │ Pool    │ Pool    │ Pool    │      │  Initialized with _warm() → import cadquery
 └────┬────┘ └───┬────┘ └───┬────┘ └─────┘
      │          │          │
      ▼          ▼          ▼
   ┌─────────────────────────────────────┐
   │  CAD Kernel Layer (per worker)       │
   │  `src/spur/model.py`                 │
   │  • CadQuery/OpenCascade              │
   │  • One RLock per worker              │
   │  • Solid cache (4 entries per worker)│
   │  • STL/STEP export                   │
   └──────────────┬──────────────────────┘
                  │
                  ▼
          ┌───────────────────┐
          │  Exported bytes    │
          │  (STL or STEP)     │
          └───────────────────┘
```

## Component Responsibilities

| Component | Responsibility | File |
|-----------|----------------|------|
| Parameters | Validated, frozen, hashable model shared by all three interfaces (API, CLI, web UI) | `src/spur/params.py` |
| Gear maths | Pure-arithmetic derived dimensions, measurement aids, feasibility checks; runs on every keystroke | `src/spur/calc.py` |
| Build pool | N independent worker process lifecycle, affinity-based routing, timeouts, worker replacement | `src/spur/pool.py` |
| CAD kernel | CadQuery/OpenCascade solid construction, kernel lock, per-worker solid cache, STL/STEP export | `src/spur/model.py` |
| HTTP API + serving | FastAPI endpoints, admission control, byte cache, request logging, static file hosting | `src/spur/app.py` |
| CLI | `spur serve` / `spur info` / `spur export` command-line interface | `src/spur/cli.py` |
| Build errors | Exception types for validation failures, build errors, timeouts (shared across layers) | `src/spur/build_errors.py` |
| Structured logging | JSON log formatting, idempotent configuration, record vocabulary for observability | `src/spur/records.py` |
| Web UI | HTML form, three.js preview, shareable URLs | `src/spur/static/index.html`, `src/spur/static/app.js`, `web/` |

## Pattern Overview

**Overall:** Multi-process architecture with kernel isolation and layered responsibilities.

**Key Characteristics:**
- **One parameter model drives three entry points** — `GearParams` (Pydantic) is the single source of truth for all parameters; the JSON schema generates the web form, CLI flags and API query parameters
- **Kernel compartmentalization** — the CAD kernel runs in isolated worker processes only; the serving process is kernel-free and holds only high-level caches and routing logic
- **Admission-controlled concurrency** — a bounded build queue prevents a runaway stack of build requests; slots cover both build time and first gzip encode time
- **Parameter-hash affinity routing** — requests for the same gear (preview, fine, STEP) route to the same worker to reuse the cached solid
- **Two-tier caching** — byte cache (per gear, 64 MiB default) in the serving process; solid cache (4 entries per worker) in each worker process
- **Import-boundary contracts** — enforced by import-linter; prevent unintended dependencies (kernel off event loop, logging out of pure-maths layer, CLI away from web-specific policies)

## Layers

**HTTP API and Serving (`src/spur/app.py`):**
- Purpose: FastAPI application entry point, admission control, byte cache, request routing
- Location: `src/spur/app.py`
- Contains: FastAPI app definition, lifespan startup/shutdown, endpoints (`/`, `/api/health`, `/api/schema`, `/api/info`, `/api/model.{fmt}`), `_BlobCache`, admission control via `_build_slot`, error handling
- Depends on: `params.GearParams`, `calc.derive`, `pool.BuildPool`, `records` logging module, `build_errors` exception types
- Used by: uvicorn (FastAPI's ASGI server), web UI (static files served here)
- **Does NOT directly import:** `cadquery`, `OCP` (L17, enforced by import-linter contract with `allow_indirect_imports=false`)

**Pure Mathematics (`src/spur/calc.py`):**
- Purpose: Fast, keystroke-response-time calculation of derived dimensions and feasibility checks
- Location: `src/spur/calc.py`
- Contains: `derive()` function, `DerivedDimensions` Pydantic model, involute geometry, measurement aids, profile computation, bore/keyway/recess math
- Depends on: `params.GearParams` (TYPE_CHECKING only, lazy import)
- Used by: CLI (info command), web API (info endpoint), tests
- **Does NOT directly import:** `cadquery`, `OCP`, `logging`, `records` (L04, L07, enforced by import-linter)

**CAD Kernel and Export (`src/spur/model.py`):**
- Purpose: CadQuery/OpenCascade solid construction, mesh export, per-worker solid caching
- Location: `src/spur/model.py`
- Contains: `build()` (solid construction), `export()` (STL/STEP writer), `_build_cached()` LRU cache, `_LOCK` (RLock for kernel serialization), `_release_arenas()` (malloc_trim)
- Depends on: `calc.py` geometry helpers, `params.GearParams`
- Used by: Worker processes only, via dynamic import in `pool.py`
- **Handles:** CadQuery/OCP native objects; kernel is only ever accessed through `_LOCK`

**Worker Pool Management (`src/spur/pool.py`):**
- Purpose: N independent single-worker ProcessPoolExecutor instances, parameter-hash routing, worker lifecycle
- Location: `src/spur/pool.py`
- Contains: `BuildPool` class, `build_export()` function (submittable across process boundary), worker warm-up (`_warm()`), timeout handling, worker replacement
- Depends on: `params.GearParams`, `build_errors` exception types, `records` logging
- Used by: FastAPI app (via `Depends(build_backend)` injectable)
- **Key mechanism:** Runtime dynamic import of `model.py` inside worker, never a static import in `app.py`

**CLI Interface (`src/spur/cli.py`):**
- Purpose: Command-line interface for three commands: `serve`, `info`, `export`
- Location: `src/spur/cli.py`
- Contains: argument parsing, `_add_gear_args()`, command handlers (`cmd_serve`, `cmd_info`, `cmd_export`)
- Depends on: `params.GearParams`, `calc.derive`, `records.configure`
- Used by: Entry point `spur = "spur.cli:main"` (pyproject.toml)
- **Does NOT import:** `app`, `fastapi`, `starlette` (L04, enforced by import-linter)

**Structured Logging (`src/spur/records.py`):**
- Purpose: JSON log formatting and idempotent configuration
- Location: `src/spur/records.py`
- Contains: `_JsonFormatter`, `_JsonHandler`, `configure()`, event helpers (`build_started()`, `build_failed()`, `export_served()`, `queue_refused()`, `worker_replaced()`)
- Depends on: `params.GearParams`, `build_errors` exception types
- Used by: `app.py` and `pool.py` (for event logging), `cli.py` (for setup)
- **Configuration:** Called from both `cli.cmd_serve` (before uvicorn) and `app.py` lifespan (to catch spawned workers)

**Build Error Types (`src/spur/build_errors.py`):**
- Purpose: Shared exception hierarchy used across all layers
- Location: `src/spur/build_errors.py`
- Contains: `BuildError` (validation failure), `BuildTimeout` (build overrunning wall clock)
- Used by: `app.py` (exception handling), `model.py` (raised), `records.py` (logged), `pool.py` (logged)

**Web UI (`src/spur/static/` and `web/`):**
- Purpose: HTML form, three.js 3D preview, shareable model links
- Location: `src/spur/static/index.html`, `src/spur/static/app.js`, `web/` (esbuild source)
- Served by: FastAPI static file mounting at `/static`, index at `/`
- Bundle: `src/spur/static/vendor/three.bundle.min.js` (vendored esbuild output of `web/`, committed to repo, byte-checked by CI)

## Data Flow

### Primary Request Path: Build and Export a Gear Model

1. **HTTP GET /api/model.stl?teeth=30&module=2.0** → `app.model()` (`src/spur/app.py:381`)
2. **Parameter parsing** → Pydantic `GearParams` validation via `ModelQuery` class
3. **Cache lookup** → Check `_EXPORTS` (byte cache, 64 MiB, in serving process) for `(params, fmt, quality, encoding)` key
4. **If cache miss:**
   - **Admission control** → `_build_slot()` acquires `BUILD_QUEUE` semaphore (bounded to `MAX_QUEUED_BUILDS`, default 4)
   - **Worker selection** → `BuildPool.executor_for(params)` routes by `hash(params) % N` (affinity)
   - **Build request** → `backend(params, fmt, quality)` submits `build_export()` task to worker via `ProcessPoolExecutor`
   - **Worker execution** → Inside worker process: `build_export()` → dynamic import of `model.py` → `model.export()` → `_build_cached(params)` (LRU cache, 4 entries, per worker) → `build()` solid construction under `_LOCK` → tessellate and export
   - **Solid cache check** → If solid already cached in this worker, reuse; else build from scratch
   - **Result:** Raw STL/STEP bytes returned to serving process
5. **Gzip encoding** (if client sent `Accept-Encoding: gzip`) → inside `_build_slot()` via `run_in_threadpool(_gzip, raw)`, result cached under `(params, fmt, quality, "gzip")` key
6. **Response** → Set `Content-Disposition: attachment`, media type, `Content-Encoding` header if gzip, return bytes

### Secondary Request Path: Derived Dimensions

1. **HTTP GET /api/info?teeth=30** → `app.info()` (`src/spur/app.py:374`)
2. **Parameter parsing** → `InfoQuery` class (extends `GearParams`, adds optional `mate_teeth` field)
3. **Calculation** → `calc.derive(params, mate_teeth=q.mate_teeth)` → pure arithmetic, no kernel, no cache
4. **Return** → Pydantic model `DerivedDimensions` serialized as JSON

### CLI Request Path

1. **`spur info` command** → `cmd_info()` → parses arguments → `derive(params)` → JSON to stdout
2. **`spur export` command** → `cmd_export()` → `model.export(params, fmt, quality)` → writes file directly (no pool, no serving process)
3. **`spur serve` command** → `cmd_serve()` → calls `configure()` (logging setup) → `uvicorn.run(app)` (starts FastAPI)

**State Management:**
- **Parameter set** — immutable, hashable `GearParams` (frozen Pydantic model)
- **Solid cache** — per-worker `@lru_cache(maxsize=SPUR_SOLID_CACHE)`, keyed on `params`; accessible only inside worker process via `_build_cached()`
- **Byte cache** — in serving process, `_BlobCache` instance `_EXPORTS`, keyed on `(params, fmt, quality, encoding)`
- **Build queue** — `threading.BoundedSemaphore(MAX_QUEUED_BUILDS)`, in serving process only
- **Worker lifecycle** — `BuildPool._executors` list of `ProcessPoolExecutor` instances; warm-up happens in `lifespan()` startup

## Key Abstractions

**GearParams (`src/spur/params.py`):**
- Purpose: Single, validated, frozen parameter model for all interfaces
- Used as: cache key (hashable), JSON schema source (drives web form), CLI argument definitions
- Properties: Frozen (immutable), hashable (cache-friendly), JSON schema export (metadata-driven form generation)

**DerivedDimensions (`src/spur/calc.py`):**
- Purpose: Published response model for `/api/info` and `spur info` command
- Properties: Frozen Pydantic model; includes `None` for inapplicable values (e.g., `centre_distance` when no `mate_teeth` provided)

**BuildPool (`src/spur/pool.py`):**
- Purpose: Manages N independent worker processes, routes by parameter-hash affinity
- Mechanism: One `ProcessPoolExecutor(max_workers=1)` per worker; `executor_for()` selects by `hash(params) % N`
- Lifecycle: Warm-up on startup (import cadquery), torn down on shutdown

**_BlobCache (`src/spur/app.py`):**
- Purpose: LRU cache for exported bytes, bounded by total size (not entry count)
- Implementation: Maintains insertion order, evicts oldest entries when budget exceeded
- Keyed by: `(params, fmt, quality, encoding)` to allow both raw and gzip variants to coexist

**Profile (`src/spur/calc.py`):**
- Purpose: Geometric profile data structure for involute geometry calculations
- Fields: tooth count, module, pressure angle (radians), pitch/base/tip/root radii, half tooth-thickness angle
- Computed once per keystroke (in `profile()` function), reused by derived dimensions and later by CAD kernel

## Entry Points

**HTTP API (FastAPI `app.py`):**
- Location: `src/spur/app.py:app` (FastAPI instance)
- Triggers: `GET /`, `/api/health`, `/api/schema`, `/api/info`, `/api/model.{fmt}` requests
- Responsibilities: Routing, parameter validation, caching, admission control, error mapping to HTTP status codes

**CLI (`cli.py`):**
- Location: Entry point `spur = "spur.cli:main"` defined in `pyproject.toml`
- Triggers: Command-line invocation (`spur serve`, `spur info`, `spur export`)
- Responsibilities: Argument parsing, command dispatch, stdout/stderr management

**Worker Process (`pool.py`):**
- Location: `src/spur/pool.py:build_export()` (function submitted to `ProcessPoolExecutor`)
- Triggers: Task submitted from serving process via `executor.submit(build_export, ...)`
- Responsibilities: Runtime import of `model.py`, call `model.export()`, return bytes

## Architectural Constraints

- **Threading:** Single-threaded event loop in serving process (uvicorn with `workers=1` by default); worker processes are isolated, one task per worker under `max_workers=1`
- **Global state:** One `RLock` in `model.py` per worker (protects all OpenCascade calls); one `BoundedSemaphore` in `app.py` (admission control); `_EXPORTS` cache and `_in_flight_builds` counter in serving process only
- **Circular imports:** Prevented by design: `app.py` never statically imports `model.py`; `calc.py` imports `params.py` only in `TYPE_CHECKING` block; `cli.py` never imports `app.py`
- **Process boundary:** `pool.py`'s `build_export()` function is pickleable and submittable to worker via `ProcessPoolExecutor`; only `params.GearParams` and Pydantic-serializable values cross the boundary
- **CAD kernel access:** Only inside worker processes; served-process lifespan never loads `cadquery`/`OCP` (L17, enforced by import-linter contract with `allow_indirect_imports=false`)

## Anti-Patterns

### Direct CAD Kernel Calls in the Serving Process

**What happens:** A future change adds a call to `cadquery.Solid()` or similar inside `app.py`.

**Why it's wrong:** Violates L17 (memory ceiling measurement), makes the memory model depend on N independently-measured process footprints, adds blocking I/O to the event loop, contradicts the admission-control design.

**Do this instead:** Route through `pool.export()` or a new worker-side function. The serving process must never load `cadquery` or `OCP`.

### Caching Based on Gear Identity Rather than Parameter Hash

**What happens:** Cache uses a generator ID or user-assigned name as the key instead of `hash(params)`.

**Why it's wrong:** Breaks shareable links (L05 — parameters in URL are the source of truth, not a database ID) and affinity routing (same gear to the same worker).

**Do this instead:** Cache keys must be derived from `GearParams` hash only. A URL like `/api/model.stl?teeth=30` is the canonical identity.

### Unbounded Build Queue

**What happens:** Admission control (`_build_slot`) is removed or the queue size made unbounded.

**Why it's wrong:** Latency explodes (L09 — bounded queue prevents latency-with-no-payoff), pool replacement gets starved, the 503 + Retry-After signal to clients disappears.

**Do this instead:** Keep `MAX_QUEUED_BUILDS` and the `BoundedSemaphore`; if capacity is insufficient, increase `SPUR_BUILD_WORKERS` and re-measure memory (L17).

### Printing Values Without Measurement

**What happens:** A performance or memory claim is made in a commit message without a corresponding entry in `bench/RESULTS.md`.

**Why it's wrong:** Violates L08 (no guesses, only measured numbers). A claim like "this is 2x faster" that is never re-verified becomes debt.

**Do this instead:** Measure with `bench/latency.py`, `bench/memory.py` or a custom benchmark. Record the result in `bench/RESULTS.md` with date, machine, and method. Ground claims in evidence.

## Error Handling

**Strategy:** Distinguish user-correctable errors (parameters invalid) from system errors (worker died, timeout).

**Patterns:**
- **Parameter validation failure** → `BuildError` → HTTP 422 (Unprocessable Entity) with detailed field-level error in response body
- **Build timeout** → `BuildTimeout` → HTTP 503 (Service Unavailable) with `Retry-After: 5` header
- **Worker pool broken** → `BrokenProcessPool` → HTTP 503 with descriptive message about worker replacement
- **Admission queue full** → HTTPException(503) in `_build_slot()` → `queue_refused()` log record, `Retry-After: 5` header
- **Genuine exception from worker** → `BrokenProcessPool` (future regressions) → HTTP 500, log a `build.failed` record with traceback

## Cross-Cutting Concerns

**Logging:** Structured JSON via `records.py`; every build/export outcome is logged (started, served, failed, queued, replaced). Logs are on stderr, JSON-formatted, one object per line, readable via `jq`.

**Validation:** Parameters validated once at boundary (`GearParams` constructor in `app.py` query parsing, `cli.py` arg handling). Validation errors name the field and say what to change (e.g., "D-flat must be between 4.5 and 9 mm").

**Authentication:** None (no auth system in this version). Every public endpoint is readable and every format is downloadable. Deployment is assumed to be behind network access control (not exposed to the internet without additional auth layer).

**Performance Observability:** Every build logs its duration; every export logs source (cache / compressed / built). `health()` endpoint reports queue depth and worker count in real time.

---

*Architecture analysis: 2026-10-02*
