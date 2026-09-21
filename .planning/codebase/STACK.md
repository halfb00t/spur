---
last_mapped_commit: 5252bdcd6a11f893246f614da8e5f0d431d1ed2a
last_mapped_at: 2026-09-21
---
# Technology Stack

**Analysis Date:** 2026-09-21

## Languages

**Primary:**

- Python 3.10–3.12 - Backend: API server, CLI, CAD kernel integration
  - Floor set by `cadquery-ocp` wheel availability (no pre-built wheels for 3.13+)
  - Ruff targets 3.10 (L01); CI runs both 3.10 and 3.12

**Secondary:**

- JavaScript (ES2020) - Frontend: 3D viewer, parameter form, interactive UI
  - Vanilla (no framework), vendored as a tree-shaken three.js bundle
  - Runtime has no Node.js dependency; bundle served as static asset

## Runtime

**Environment:**

- CPython 3.10–3.12 (server and CLI)
- Browsers: modern ES2020 support (Chrome, Firefox, Safari, Edge)

**Package Manager:**

- pip for Python
- Lockfile: `requirements.txt` (full pinned closure; `pyproject.toml` keeps loose ranges for dev)
- Node package manager for build-time only: `web/package-lock.json` (three.js bundling during CI)

## Frameworks

**Core:**

- FastAPI 0.141.1 (`fastapi>=0.115`) - HTTP API, web server, parameter validation
- Pydantic v2.13.5 (`pydantic>=2.7`) - Parameter model, JSON schema generation, validation
- uvicorn 0.53.0 (`uvicorn>=0.30`) - ASGI application server

**CAD Kernel:**

- CadQuery 2.8.0 (`cadquery>=2.5`) - Parametric solid modeling, involute flank construction
- cadquery-ocp 7.9.3.1.1 (indirect via CadQuery) - Python bindings to OpenCascade kernel (OCCT)

**Frontend:**

- three.js 0.186.0 - 3D scene, mesh rendering, camera controls
  - Vendored and tree-shaken by esbuild to 555 KB (`src/spur/static/vendor/three.bundle.min.js`)
  - Committed to repo; CI rebuilds and byte-checks it daily (L11)

**Testing:**

- pytest 8+ - Test runner, fixtures, assertions
- httpx 0.27+ - HTTP test client for smoke tests (dev only)

**Build/Dev Tools:**

- hatchling 1.25+ - Python package builder
- ruff 0.14+ - Linting and import sorting (no formatter; see L16)
- mypy 1.18+ - Static type checking with `--strict` mode (L14)
- import-linter 2.3+ - Enforces module boundary contracts (L04, L06)
- pre-commit 4+ - Git hook framework

**CLI:**

- argparse (standard library) - Command-line interface (`spur serve`, `spur info`, `spur export`)

## Key Dependencies

**Critical (API/kernel):**

- cadquery-ocp 7.9.3.1.1 - OpenCascade OCCT kernel; ~1.5 GB of the 1.7 GB image
- starlette 1.6.0 (indirect via FastAPI) - ASGI framework, middleware, static file serving
- numpy 2.5.3 (transitive) - Numerical computations, matrix operations

**Infrastructure:**

- Click 8.5.0 (transitive via CadQuery) - CLI utilities
- PyYAML 6.0.3 (transitive) - Config parsing (likely Starlette/other)
- VTK 9.6.2 (indirect via cadquery-ocp) - Visualization (not used; present in build closure)

**Build artifacts:**

- esbuild 0.25.12 (Node, dev only) - JavaScript bundler for three.js
- three 0.186.0 (Node, dev only) - 3D graphics library source

**Numerical solvers (CadQuery transitive):**

- casadi 3.8.1 - Symbolic differentiation, solving (for gear calculations)
- nlopt 2.11.0 - Nonlinear optimization

## Configuration

**Environment Variables:**

- `SPUR_HOST` (default: `0.0.0.0` in image, `127.0.0.1` locally) - Server bind address
- `SPUR_PORT` (default: `8000`) - Server port
- `SPUR_WORKERS` (default: `1`) - Uvicorn worker processes (each serializes on CAD kernel lock)
- `SPUR_ROOT_PATH` (default: empty) - URL prefix for reverse proxy deployment
- `SPUR_SOLID_CACHE` (default: `4`) - Max solid objects cached per worker (memory-bounded)
- `SPUR_EXPORT_CACHE_MB` (default: `64`) - Max exported bytes cached per worker
- `SPUR_MAX_QUEUED_BUILDS` (default: `4`) - Build queue depth before returning `503`

See `compose.yaml` for production Docker environment setup.

**Build:**

- `Makefile` - Entry point for all development commands (`make verify`, `make serve`, etc.)
- `pyproject.toml` - Python project metadata, linter/type-checker/import-boundary rules
  - Ruff config: `target-version = py310`, line length 100, high-signal rule set (L16)
  - mypy config: strict mode, Python 3.12 for stubs (numpy reason), pydantic plugin (L14)
  - pytest config: `--strict-markers`, `--strict-config`, `xfail_strict`
  - import-linter contracts: CAD kernel isolation, CLI isolation from app (L04, L06)
- `requirements.txt` - Pinned closure (31 packages) for Docker image; auto-generated
- `.ruff.toml` (via `pyproject.toml`) - Linting rules; intentionally no formatter (L16)
- `.mypy.ini` (via `pyproject.toml`) - Type checking; `ignore_missing_imports` for `cadquery.*` and `OCP.*`

**Docker:**

- `Dockerfile` - Multi-stage build:
  - Base: `python:3.12-slim-bookworm`
  - Layer 1: System deps for OpenCascade (`libgl1 libx11-6 libexpat1`)
  - Layer 2: Pin dependencies via `requirements.txt` with `--no-deps` (L12)
  - Layer 3: App code, smoke test, run as uid 10001 (non-root)
  - Health check: `curl` to `/api/health` with 10 s timeout (OCCT holds GIL during large builds)
- `compose.yaml` - Service definition:
  - Memory limit: 2 GB (measured per L07)
  - Read-only root filesystem
  - tmpfs on `/tmp` (256 MB, for exports)
  - No capabilities (`cap_drop: ALL`)
  - Binds to `127.0.0.1:8000` (authentication-less app requires reverse proxy for exposure)

## Platform Requirements

**Development:**

- Python 3.10, 3.11, or 3.12 (one of these on PATH)
- macOS, Linux, or WSL2 (no Windows native OCCT wheels; Docker works everywhere)
- ~1.4 GB disk for `.venv` (vendor and headers for CAD kernel)
- Node.js 20+ (only to rebuild three.js bundle; not needed for normal development)

**Production:**

- Docker runtime (Linux amd64 or arm64)
- ~2 GB memory per container instance (compose sets `mem_limit: 2g`)
- Reverse proxy with TLS/auth (app has no built-in authentication; binds to 127.0.0.1 by default)

---

*Stack analysis: 2026-09-21*
