---
last_mapped_commit: 41d23c70643108293120e36d6abd823739892ca8
last_mapped_at: 2026-10-02
---
# External Integrations

**Analysis Date:** 2026-10-02

## APIs & External Services

**Not applicable** — This is a standalone parametric CAD tool with no external API dependencies or third-party integrations.

All gear generation, validation, and export is self-contained within the application. The only external interaction is:
- **Browser HTTP client** → OpenAPI endpoints on localhost (web UI making fetch requests to its own backend)
- **CLI tool** → Direct Python API (no network)

## Data Storage

**Databases:** Not used
- The application is stateless. No persistent data model beyond request parameters.
- Outputs (STL/STEP files) are generated on-demand and returned to the client; not stored server-side.

**File Storage:** Temporary filesystem only
- Exports written to `tmpfs` at `/tmp` inside container (bounded 256 MB, `compose.yaml:30-31`)
- Temporary solids and intermediate files created during CAD operations use Python's `tempfile` module
- No persistent file storage, S3, cloud storage, or CDN integrations

**Caching:**
- **In-process solid cache**: Built solids cached per worker process (`SPUR_SOLID_CACHE` per-worker count, `README.md:73`)
  - Located: `src/spur/model.py` — LRU cache keyed by parameter hash (D-07)
  - Tuning: Benchmarked in `bench/memory.py` for memory sweep validation
- **In-process export bytes cache**: STL/STEP bytes cached in serving process only (`SPUR_EXPORT_CACHE_MB` total budget)
  - Located: `src/spur/app.py:41-60` — `_BlobCache` class, LRU by total bytes
  - Single instance, single-threaded (D-06, moved from per-worker), never persisted

No Redis, Memcached, or distributed caching. All caching is in-memory.

## Authentication & Identity

**Not applicable** — No authentication system.

The application has no user accounts, logins, tokens, or access control. All endpoints are public:
- `/` — Web UI
- `/api/health` — Health check (used by Docker HEALTHCHECK)
- `/api/schema` — Parameter JSON schema (drives UI form generation)
- `/api/info` — Derived dimensions and warnings
- `/api/model.stl` — Binary STL export
- `/api/model.step` — STEP AP214 solid export

**Access Policy:** When deployed, the user is responsible for:
- If exposed on a network (not localhost), place an authenticating reverse proxy in front (noted in `compose.yaml:5-8` comment)
- No authentication logic in application itself

## Monitoring & Observability

**Error Tracking:** Not integrated
- No Sentry, Rollbar, or error reporting service
- Application logs errors via structured JSON logging to stderr (see `records.py` below)

**Logging:**
- **Framework:** Python stdlib `logging` module
- **Configuration:** `src/spur/records.py:85-130` sets up structured JSON logging
- **Log level:** Controlled by `SPUR_LOG_LEVEL` env var (default `INFO`, `README.md:76`)
- **Output:** JSON to stderr (container logs captured by Docker)
- **Instrumentation:**
  - Build lifecycle events: `build_started()`, `build_failed()`, `export_served()`, `queue_refused()` (see `src/spur/records.py:31-83`)
  - Timing: Request start/end with duration and outcome
  - No performance profiling or metrics exports

**Benchmarking:** Measurement, not monitoring
- Ad-hoc performance testing via `make bench.*` commands (not production monitoring)
  - Latency: `bench/latency.py` — health endpoint p95 under load (measured 0.7-2.3 ms)
  - Memory: `bench/memory.py` — container memory sweep over 40-gear corpus (tuned to 4g limit)
  - Build times: `bench/build_time.py` — per-gear STL/STEP time
  - Export cost: `bench/export_cost.py` — gzip and mesh-copy overhead
- Results recorded manually in `bench/RESULTS.md` (Phase 2 through 13)

## CI/CD & Deployment

**Hosting:** Docker containers
- Base image: `python:3.12-slim-bookworm`
- Registries: Not configured (images built locally in development and CI)
- Multi-arch: linux/amd64 and linux/arm64 (`Dockerfile` uses `docker buildx`)
- Orchestration: `docker-compose up` for local dev; bare Docker in CI tests

**CI Pipeline:** GitHub Actions
- Runs on: Ubuntu latest (ubuntu-latest)
- Repository: Public GitHub (this repo)
- Workflow file: `.github/workflows/ci.yml`

**Jobs (all required green on PR before merge, L22):**
1. `test` — Local pytest + linting + type checking (runs `make verify`)
   - Python 3.12 only
2. `vendor-bundle` — Reproducibility check for three.js bundle
   - Node.js 22, npm
   - Compares built `src/spur/static/vendor/three.bundle.min.js` against `web/` source
3. `image` — Container build and smoke test
   - Builds image, starts container, runs `docker/smoke.py` (exercises kernel + ASGI app)
   - Tests HTTP endpoints: `/api/health`, `/api/model.stl?quality=preview`, `/api/model.step`

**Merge gate:** `make pr.land` enforces all jobs passing before squash-merge to main (`scripts/pr_land.py`)

**Local gate:** `make verify` (lint, type check, import contracts, unfinished-work scan, tests)

**Container validation:** `make check` (includes `make verify` + `make smoke` + `make vendor-check`)

## Environment Configuration

**Required env vars:** None (all have safe defaults, `README.md:67-76`)

**Recommended env vars (production tuning):**
- `SPUR_WORKERS` — Usually leave at 1 (D-01 limits HTTP serving to single process)
- `SPUR_BUILD_WORKERS` — Scale from 2 per CPUs available (benchmarked at 2, `compose.yaml:14`)
- `SPUR_BUILD_TIMEOUT` — Tune per gear complexity (default 30s, long enough for 200-tooth STEP, `README.md:71`)
- `SPUR_EXPORT_CACHE_MB` — Tune per available memory and common export sizes (default 64 MB)

**Secrets location:** No secrets used
- No API keys, tokens, credentials, or sensitive configuration
- `.env` files not used or required
- All configuration via environment variables with documented safe defaults

## Webhooks & Callbacks

**Incoming:** Not supported
- No webhook endpoint for external systems to push data
- API is request-only (GET endpoints for gear generation)

**Outgoing:** Not implemented
- No callbacks to external services after builds complete
- No event notifications or downstream integrations
- Exports returned immediately to client (synchronous HTTP response)

## Process Communication

**Worker pool communication:**
- **Method:** Python `concurrent.futures.ProcessPoolExecutor` (multiprocessing)
- **IPC:** Pickled objects over pipe (std multiprocessing serialization)
- **Location:** `src/spur/pool.py` — BuildPool manages N worker processes per parameter-hash affinity (D-07)
- **Modules involved:**
  - `src/spur/app.py` — Serving process, calls `pool.export()`
  - `src/spur/pool.py` — Process lifecycle, timeout handling, recreation on crash (D-10, D-12)
  - `src/spur/model.py` — Worker subprocess target, imports CAD kernel at runtime via importlib (D-02)
- **Synchronization:** No shared memory; each worker has its own Python interpreter and OpenCascade kernel instance
- **Timeout:** `SPUR_BUILD_TIMEOUT` (default 30s) — if exceeded, worker OS process killed and replaced

## Browser JavaScript

**Runtime:** Vanilla JavaScript (ES2022) in browser only
- No build step in production (no Node, no webpack, no bundler)
- Bundled three.js vendored at build time in `web/` and committed to `src/spur/static/vendor/three.bundle.min.js`

**Bundle source:** `web/entry.js` (7 lines, exports only what viewer uses from three)
- Tree-shaken by esbuild during `make vendor` build step
- Three.js 0.186.0 imported via npm, built into 568 KB minified bundle with license
- Minified and reproducible from `web/package.json` (Node 22, esbuild 0.25.12)

**Frontend API calls:**
- `fetch()` to local backend endpoints (same-origin, no CORS)
- Endpoints: `/api/schema`, `/api/info`, `/api/model.stl`, `/api/model.step`, `/api/health`
- No third-party analytics, trackers, or ad services

---

*Integration audit: 2026-10-02*
