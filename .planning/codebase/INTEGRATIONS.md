---
last_mapped_commit: 5252bdcd6a11f893246f614da8e5f0d431d1ed2a
last_mapped_at: 2026-09-21
---
# External Integrations

**Analysis Date:** 2026-09-21

## Summary

This project has **no external network integrations by design**. It is a self-contained parametric gear generator intended for local or private-network deployment. The architecture enforces this: no HTTP client libraries are imported in the application code (`spur.app`, `spur.cli`, `spur.model`), and the import-linter contracts prevent them from being added without deliberate decision (L04).

## APIs & External Services

**None.** The application:

- Generates gears from parameters; computes no external data
- Produces STL and STEP files; uploads nowhere
- Has no user accounts, no API keys, no webhooks, no callbacks
- Exposes only a local HTTP API; does not call remote APIs

The only HTTP client dependency is `httpx 0.27+`, used in tests (`docker/smoke.py`) to test the ASGI application itself.

## Data Storage

**Databases:** None

**File Storage:** Local filesystem only

- Exports written to `/tmp` (within container; tmpfs, 256 MB bounded)
- STL and STEP files downloaded by the user's browser, not stored server-side

**Caching:** In-process, memory-bounded

- Solid models: `SPUR_SOLID_CACHE` entries (default 4) per worker
- Exported bytes: `SPUR_EXPORT_CACHE_MB` total (default 64 MB) per worker
- No persistent cache layer; no cache backend service

## Authentication & Identity

**None.** The application has no authentication.

**Security model:** Deploy behind a reverse proxy (Caddy, Traefik, nginx, Cloudflare Access, Tailscale serve, ...) that provides TLS, authentication, and authorization. See `README.md` for deployment guidance.

The compose file binds to `127.0.0.1:8000` on purpose (`compose.yaml` line 8).

## Monitoring & Observability

**Error Tracking:** None (no Sentry, Rollbar, or equivalent)

**Logs:** Standard output only

- uvicorn writes request/response logs to stdout
- Container logs captured by Docker compose (`make logs`)
- No centralized logging, no structured JSON logging format

**Metrics:** None (no Prometheus, StatsD, CloudWatch, Datadog, or equivalent)

**Distributed Tracing:** None

The application does not export observability signals. For production deployments, use the container's standard output stream and orchestration platform's native logging (Kubernetes logs, Docker compose logs, etc.).

## CI/CD & Deployment

**Hosting:** Docker container

- `.github/workflows/ci.yml` - GitHub Actions test matrix (Python 3.12)
- Builds for `linux/amd64` and `linux/arm64` (Apple Silicon, Graviton, Raspberry Pi 5 compatible)
- No dependency on external registries; image builds in CI

**CI Pipeline:** GitHub Actions (`.github/workflows/ci.yml`)

- **Job 1 (test):** `make verify` on Python 3.12
  - Runs ruff, mypy `--strict`, import-linter, unfinished-work scan, pytest
  - ~11 seconds warm (L13)
- **Job 2 (vendor-bundle):** Rebuilds three.js bundle; fails if it drifts from source (L11)
- **Job 3 (image):** Builds Docker image; runs smoke tests inside container
  - Exercises kernel, both STL/STEP exporters, ASGI stack, parameter validation
  - Detects incomplete dependency closures before push

No external CI services (no Travis, CircleCI, Buildkite, GitLab CI, etc.).

Runs are observed green — main push run
<https://github.com/halfb00t/spur/actions/runs/35963114939> — and merges to `main` go
through `make pr.land`, which requires every job in
`.github/workflows/required-jobs.txt` (L22), behind a ruleset on `main` that makes
GitHub refuse a merge without those jobs green on an up-to-date head (D-12).

## Environment Configuration

**Required env vars:** None (all have defaults)

**Secrets location:** N/A — no secrets, no API keys, no credentials stored

**Health check:** `GET /api/health` returns `{"status": "ok", "version": "0.1.0"}`

## Webhooks & Callbacks

**Incoming:** None

**Outgoing:** None

The application does not receive or send webhooks. All communication is request-response via HTTP `GET` (parameters and file exports).

## Third-Party Services & Dependencies

**Import boundaries enforce non-use of:**

- `fastapi` and `starlette` in `spur.cli` (no HTTP client needed for CLI) (L04)
- `cadquery` and `OCP` in `spur.calc` and `spur.params` (pure math, runs on keystroke) (L06)

No other external services are used or imported.

---

*Integration audit: 2026-09-21*
