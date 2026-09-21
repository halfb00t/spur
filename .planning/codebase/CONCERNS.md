---
last_mapped_commit: 5252bdcd6a11f893246f614da8e5f0d431d1ed2a
last_mapped_at: 2026-09-21
---
# Codebase Concerns

**Analysis Date:** 2026-09-21

## Overview

This codebase maintains active tech debt in `docs/tech_debt/active/`. All findings from the 2026-09-21 review (F1–F8) have been implemented per `docs/plan-2026-09-21.md`, including fixes to the centre distance solver, cache bounding, recess capping, admission control, dependency pinning, and geometry measurement.

Active concerns are categorized by severity and tracked in dedicated files. Critical issues (`blocker`) must be fixed before proceeding; `must` issues are correctness or maintainability concerns to address; `nice` items are enhancements for later.

---

## Critical Issues (Blocker)

### None currently recorded

All blocking-severity debt has been resolved. The project passed the gate at commit 2026-09-21.

---

## Must-Fix Issues

### No Structured Logging

**File:** `docs/tech_debt/active/2026-09-21-no-structured-logging.md`
**Status:** active
**Impact:** Production observability is absent — no logs for build failures, cache evictions, queue decisions, or performance anomalies.

**Where it matters:**

- `src/spur/app.py` — serving layer produces no structured output beyond HTTP status codes
- `src/spur/model.py` — CAD build outcomes (success, failure, duration) are invisible
- `docker/smoke.py` — test harness has no logging

**Next step:** Configure a structured logger at the composition boundary (`cli.py:cmd_serve` and `app.py` startup), logging: build started with parameter slug, build failed with exception class, export served from cache vs. built, queue refused with `503`. See the tech debt file for details.

**Revisit when:** first production incident, or deploy beyond one person's machine.

---

### API Response Contract Lacks Type Safety

**File:** `docs/tech_debt/active/2026-09-21-untyped-info-contract.md`
**Status:** active
**Impact:** The `/api/info` response is `dict[str, Any]`, so renamed or dropped keys are runtime surprises.

**Where it matters:**

- `src/spur/calc.py:177-230` (`derive()`) — returns a JSON document whose keys vary with parameters
- `src/spur/app.py:39-45` (`info`) — serializes the response
- `src/spur/static/app.js:130` — client reads `detail[].ctx.fields` and `warnings` by name

**Current workaround:** `disallow_any_explicit` is disabled in `pyproject.toml` so the gate passes.

**Next step:** Model the response as a `DerivedDimensions` Pydantic model with explicit optional fields. This also improves the OpenAPI schema. Then enable `disallow_any_explicit` and delete the tech debt file.

**Revisit when:** a third consumer of `/api/info` appears, or the shape needs versioning.

---

### Event Loop Stalls Under CAD Work

**File:** `docs/tech_debt/active/2026-09-21-cad-builds-block-the-event-loop.md`
**Status:** active
**Impact:** OpenCascade holds the GIL; one 200-tooth fine build stalls `/api/health` for 2+ seconds. Large gears can trigger container restart loops on slower hardware.

**Where it matters:**

- `src/spur/model.py:36` (`_LOCK`) — serializes all builds
- `src/spur/app.py` (`_build_slot`) — admission control queues requests

**Mitigation in place:**

- Admission control (`_build_slot`) returns `503 + Retry-After` when queue saturates
- Docker `HEALTHCHECK` timeout raised to 10 s to accommodate legitimate stalls
- Both are temporal workarounds, not fixes

**Next step:** Move CAD work to a process pool so the kernel runs outside the event loop's process. This changes caching (per-process today) and memory ceiling calculations, so it is a phase of its own.

**Revisit when:** more than one concurrent user is real, or the health probe fails in an environment that matters.

---

## Nice-to-Fix Issues

### CadQuery's `Shape` Type Bypasses Mypy

**File:** `docs/tech_debt/active/2026-09-21-cadquery-shape-typing.md`
**Status:** active
**Severity:** low — type safety is partial
**Impact:** Four `type: ignore` comments in `src/spur/model.py` suppress mypy errors on correct code.

**Where it matters:**

- `src/spur/model.py:169, 183, 185, 192` — boolean operations return `Shape`, which lacks `fillet()` / `chamfer()` methods
- CadQuery declares `py.typed` but over-types results as `Shape` instead of the more specific `Solid` or `Compound`

**Workaround:** Each ignore is narrow and coded: `attr-defined`, `arg-type`, `return-value` with justification.

**Next step:** Narrow the type through the geometry pipeline (`_gear_blank` → `_cut_face_recesses` → `_cut_bore`), casting once at `.val()` rather than ignoring at four call sites.

**Revisit when:** CadQuery narrows its own return types, or that pipeline is being refactored.

---

### No Coverage Floor in the Gate

**File:** `docs/tech_debt/active/2026-09-21-no-coverage-floor.md`
**Status:** active
**Severity:** low — current coverage is reasonable
**Impact:** Test regression risk — new code could land untested and not trigger the gate.

**Where it matters:**

- `pyproject.toml` — `[tool.coverage.run]` has no `fail_under`
- `Makefile:test` target — does not run `pytest --cov`

**Current state:** 50 tests cover geometry, API, CLI, and STL topology; the suite was written against the review measurements.

**Next step:** Run `pytest --cov`, read the real coverage number, set `fail_under` just under it, then add `--cov --cov-fail-under` to the `test` target. This is a ten-minute item.

**Revisit when:** immediately after one measured baseline run.

---

### No Server-Side Cancellation on Client Abort

**File:** `docs/tech_debt/active/2026-09-21-no-server-side-cancellation.md`
**Status:** active
**Severity:** low — current impact is minimal
**Impact:** When a browser aborts a request, the server finishes the build anyway, wasting the serialised kernel.

**Where it matters:**

- `src/spur/static/app.js:174` — aborts fetches on parameter change
- `src/spur/app.py` (`model` route) — does not check `request.is_disconnected()`

**Current workaround:** UI debounce and sequence counter prevent out-of-order responses.

**Next step:** Check `await request.is_disconnected()` before taking a build slot and again before export. This catches the cheap case.

**Revisit when:** slider-dragging actually saturates the queue in practice.

---

### Authentication is Intentionally Absent

**File:** `docs/tech_debt/active/2026-09-21-no-authentication.md`
**Status:** active
**Severity:** low — deployment decision, not a bug
**Context:** The service has no authentication, authorization, or rate limiting beyond the build queue. This is documented and intentional.

**Where it matters:**

- `compose.yaml` — binds to `127.0.0.1:8000` on purpose
- `src/spur/app.py` — no auth checks
- Container runs non-root with read-only filesystem, no capabilities, no-new-privileges

**Risk surface:**

- Changing port mapping to `0.0.0.0:8000` or deploying without compose exposes a DOS primitive (each 200-tooth build costs seconds of CPU and hundreds of MB).

**Next step:** If ever exposed, use a reverse proxy with auth (Caddy, Traefik, Cloudflare Access, Tailscale) and add client rate-limiting to the model endpoints. Do nothing now.

**Revisit when:** port mapping changes, or service is deployed beyond one person's machine.

---

### Enji Guard Integration Not Connected

**File:** `docs/tech_debt/active/2026-09-21-enji-guard-not-connected.md`
**Status:** active
**Severity:** low — coverage is partial
**Impact:** No continuous AI-driven security or dependency audit.

**Where it matters:** Repository integration, not code-level concern.

**Current coverage:**

- Full gate runs on Python 3.10 and 3.12 via CI (`.github/workflows/ci.yml`)
- Dependency closure is fully pinned (31 of 31 packages) in `requirements.txt`
- Documented review history in `docs/`

**Gap:** No ongoing CVE alerting for the 31 pinned packages.

**Next step:** Either connect Enji Guard (GitHub App at `https://guard.enji.ai/app`), or enable Dependabot alerts and security updates on the repository (free, no third party).

**Revisit when:** owner decides on continuous AI audit, or at next dependency bump.

---

## Resolved Issues (From 2026-09-21 Review)

All eight findings from `docs/review-2026-09-21.md` (F1–F8) have been implemented per `docs/plan-2026-09-21.md`:

| Finding | Fix | Verification |
|---------|-----|--------------|
| **F1** — centre_distance returns confidently wrong numbers | Replaced Newton iteration with bisection on `(0, 89°)` | 138 bad cases → 0; grid sweep matches reference to 1e-6 |
| **F2** — Caches unbounded by bytes | Bounded solid cache to 4 entries, export cache to 64 MB, added `malloc_trim()` | anon RSS reduced 3.0 GiB → 358 MiB for large sweeps |
| **F3** — Bore/recess defaults are absolute mm | Cap recess width to fit, warn instead of refuse | README example now runs; 83% → 94% of grid feasible |
| **F4** — No admission control; build stalls event loop | Admission queue returns `503 + Retry-After`; `HEALTHCHECK` timeout raised to 10 s | Health probes no longer timeout under 10 concurrent builds |
| **F5** — Only 6 of 56 packages pinned | Regenerated as full freeze of resolved set | 6 → 31 pinned; `docker/refresh-requirements.sh` documented |
| **F6** — root_thickness measured at wrong radius | Measure at `rf` like root gap already is | z=19: 4.9125 → 4.7744 (pitch match) |
| **F7** — 440 MB of image never imported | Uninstall verified-unused transitives; upgrade smoke test | 2.15 GB / 2.07 GB → 1.70 GB / 1.61 GB |
| **F8** — Structure and docs/CI gaps | Split `_build()` into named steps; add comments; full CI workflow | 34 → 50 tests; CI runs pytest, builds image, checks bundle |

---

## Dependency & Environment Notes

**Python:** pinned to 3.10–3.12 in `pyproject.toml` (cadquery-ocp publishes wheels for these versions only). `Dockerfile` uses 3.12-slim-bookworm.

**Vendored Bundle:** `src/spur/static/vendor/three.bundle.min.js` (555 KB) is byte-checked by CI (`npm run build` must match the committed version). SHA256: `1abe0e82acd7a9949063acb09693e5b938ec8b0eea365d649adf423d8bb5f2eb`.

**Docker:** `compose.yaml` sets memory limit to 2 GiB (measured from sweep workloads); HEALTHCHECK timeout is 10 s; container runs non-root with read-only root and capabilities dropped.

**CI:** `.github/workflows/ci.yml` runs `make verify` (lint, types, import boundaries, tests) on Python 3.10 and 3.12, builds the image, smoke-tests it, and verifies the vendored bundle matches. **Note:** The workflow has never executed in a GitHub Actions environment — it was hand-verified during setup but not yet proven in CI.

---

## Test Coverage Gaps

**No baseline floor:** `pytest --cov` has not been run to establish a number. Coverage is configured (`pyproject.toml`) but `fail_under` is not set in the gate. The 50 tests cover the main paths (geometry, API contract, CLI, STL topology), but drift is possible.

**CLI smoke tests added:** `tests/test_cli.py` now exercises the README's own examples, catching F3's "export" breakage.

**Topology verification:** STL/STEP geometry is validated for watertight surfaces and correct orientation, but the check runs outside the build pipeline (manual validation during review, not automated).

---

## Architectural Constraints & Trade-Offs

**Serialised kernel:** All CAD work holds a single `_LOCK` (`src/spur/model.py:36`). This is the root cause of F4 (event loop stalls) and makes concurrency a process-pool problem, not a threading one.

**Per-process caches:** Solid and export caches are per-process (Python `lru_cache`), so each of the 2 workers in compose has its own 4-entry solid cache and 64 MB export cache.

**No cancellation in CAD kernel:** OpenCascade work is not interruptible. Admission control (`_build_slot`) queues requests, but a saturated worker will still block other requests for the duration of one build.

**Defaults scale with user, not with gear:** Bore diameter (`bore_d = 9`) and recess width (`recess_width = 6`) are absolute mm, tuned for a 19-tooth m=1.75 reference gear. Smaller gears hit feasibility walls (F3 was the headline UX bug here; it is capped now, not rescaled, to preserve shareable links).

---

## Measurement & Verification Standard

Per `CLAUDE.md`: "A number the tool prints is a number someone will cut metal to." Claims about performance and memory are measured, not estimated. Before F2 and F4 fixes, container RSS was measured under sweep workloads; after, the same workloads were re-run to verify the improvement. The CI workflow and the measurements in `docs/review-2026-09-21.md` and `docs/plan-2026-09-21.md` establish this standard.

---

*Concerns audit: 2026-09-21*
