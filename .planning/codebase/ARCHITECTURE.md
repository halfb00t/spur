---
last_mapped_commit: 5252bdcd6a11f893246f614da8e5f0d431d1ed2a
last_mapped_at: 2026-09-21
---
<!-- refreshed: 2026-09-21 -->

# Architecture

**Analysis Date:** 2026-09-21

## System Overview

```text
┌────────────────────────────────────────────────────────────────────┐
│                         Three Entry Points                          │
├────────────────────┬──────────────────┬───────────────────────────┤
│   Web UI + API     │       CLI        │   Admission Control       │
│  `src/spur/app.py` │  `src/spur/cli`  │   Build Queue (L04)      │
└────────┬───────────┴──────────┬───────┴───────────────┬───────────┘
         │                      │                       │
         └──────────────────────┼───────────────────────┘
                                │ GearParams (L02)
                                ▼
┌────────────────────────────────────────────────────────────────────┐
│                    Calculation & Validation Layer                   │
│   `src/spur/params.py` - GearParams (frozen, hashable, validated)   │
│   `src/spur/calc.py` - Pure math (no CAD kernel, L08)              │
│     - profile(), derive(), check(), centre_distance()              │
│     - root_fillet(), recess_radii(), span_measurement()            │
└────────┬───────────────────────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────────────────────────────┐
│                         Model Layer                                 │
│         `src/spur/model.py` - Only path to CadQuery (L06)          │
│   - Kernel lock (_LOCK, RLock) - OCCT not thread-safe              │
│   - Build cache: LRU by entry count (SPUR_SOLID_CACHE, default 4)  │
│   - Export cache: LRU by size (SPUR_EXPORT_CACHE_MB, default 64MB) │
│   - malloc_trim() after cache miss (L07)                           │
└────────┬───────────────────────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────────────────────────────┐
│                      Binary Output (File Storage)                   │
│              STL (binary, preview or fine quality)                  │
│           STEP (AP214, exportable from OpenCascade)                 │
└────────────────────────────────────────────────────────────────────┘
```

## Component Responsibilities

| Component | Responsibility | File | Constraints |
|-----------|----------------|------|-------------|
| **GearParams** | Single validated model for all interfaces; JSON schema drives UI form and CLI flags | `src/spur/params.py` | Frozen, hashable; defaults are absolute mm (L05); validated once (L02) |
| **Calculation** | Pure math: involute geometry, measurement aids, feasibility checks; runs on every keystroke | `src/spur/calc.py` | Cannot import cadquery/OCP (L08); uses only params attributes; returns None for impossible values (L08) |
| **Solid Building** | CadQuery solid construction: toothed blank, recesses, bore, chamfers; all OCCT calls through lock | `src/spur/model.py` | Sole gateway to cadquery/OCP; thread-safe (L06); cached per params (L07) |
| **Export** | STL and STEP generation; bounded byte cache; arena release after miss | `src/spur/model.py` | Size-bounded, not entry-bounded (L07); malloc_trim after miss |
| **HTTP API** | REST endpoints, admission control (bounded build queue), static hosting | `src/spur/app.py` | Queue policy lives here, not in model (L04); cannot import cli, FastAPI policy is transport, not business logic |
| **CLI** | Command-line interface: `serve` (uvicorn wrapper), `info` (JSON output), `export` (STL/STEP file write) | `src/spur/cli.py` | Cannot import app/fastapi/starlette (L04); builds directly without queue (immediate export) |
| **Web UI** | Browser form and 3D preview; three.js vendored in bundle; communicates via REST queries | `src/spur/static/`, `web/` | Vanilla JS, no runtime Node dependency (L11); bundle is build artifact (CI byte-checks) |

## Pattern Overview

**Overall:** Layered with strict boundaries enforced by import-linter contracts in `pyproject.toml`.

**Key Characteristics:**

- **One model, three interfaces** — GearParams is the single source of truth (L02); adding a field makes it appear in web, API, and CLI automatically.
- **Pure math free of the kernel** — `calc.py` runs on every keystroke in the UI with no access to OpenCascade; the moment it can reach the kernel, that property is gone (L08).
- **Thread-safe by lock, not by design** — OpenCascade demands serialization (L06); every build goes through `_LOCK` in `model.py`; concurrency buys latency, not throughput (L04 consequence).
- **Caches are transparent optimizations** — safe to lose at any moment; nothing becomes correct only because something was cached (L07).
- **Cap and warn, never guess** — dimensions that can be trimmed without contradicting an explicit choice are capped and warned (L03); a direct conflict is a 422 refusal (L03).
- **No number is better than a wrong number** — `centre_distance()` returns `None` when the solver has no solution, and the API reports a warning instead of a plausible lie (L08).

## Layers

**Parameters:**

- **Purpose:** Single validated model; JSON schema generator for UI and CLI flags
- **Location:** `src/spur/params.py`
- **Contains:** `GearParams` (Pydantic BaseModel, frozen), field metadata (group, unit, step, help)
- **Depends on:** `calc.check()` for cross-field validation (called from model validator)
- **Used by:** All three entry points; every cached operation

**Calculation:**

- **Purpose:** Pure geometry and measurement: involutes, tooth profiles, derived dimensions, feasibility rules, measurement aids (span, caliper)
- **Location:** `src/spur/calc.py`
- **Contains:** `profile()`, `derive()`, `check()`, `centre_distance()`, `with_mate()`, `root_fillet()`, `recess_radii()`, `span_measurement()`, involute solver
- **Depends on:** GearParams attributes only; no imports of CAD kernel (enforced, L08)
- **Used by:** `app.py` (/api/info), `cli.py` (info and export commands), UI form validation

**Solid Model:**

- **Purpose:** CAD kernel gateway: solid construction, tessellation, export, caching, garbage collection
- **Location:** `src/spur/model.py`
- **Contains:** `_outline()` (analytic fillets), `_gear_blank()`, `_cut_face_recesses()`, `_cut_bore()`, `_build()`, `build()` (cached), `export()` (cached)
- **Depends on:** `calc.Profile`, `GearParams`, CadQuery/OpenCascade (direct imports only here)
- **Used by:** `app.py` (/api/model.stl, /api/model.step), `cli.py` (export command)
- **Threading:** All kernel calls serialized by `_LOCK` (RLock, L06); cache miss triggers `malloc_trim(0)` (L07)

**HTTP API + Web:**

- **Purpose:** REST endpoints, static hosting, admission control, HTML/CSS/JS serving
- **Location:** `src/spur/app.py`, `src/spur/static/`, `web/`
- **Contains:** FastAPI routes (/api/info, /api/model.*, /api/schema, /api/health), build queue (BoundedSemaphore, L04), static mount
- **Depends on:** `GearParams`, `calc.derive()`, `calc.with_mate()`, `model.export()`, FastAPI, Pydantic v2
- **Used by:** Browser clients; the UI (index.html, app.js) queries /api/schema for the form, /api/info for numbers, /api/model.* for downloads
- **Admission control:** `BUILD_QUEUE` (max SPUR_MAX_QUEUED_BUILDS, default 4); 503 + Retry-After if full (L04)

**CLI:**

- **Purpose:** Command-line commands: `spur serve` (uvicorn wrapper), `spur info` (JSON), `spur export` (file write)
- **Location:** `src/spur/cli.py`
- **Contains:** Argument parser (generated from GearParams fields), three commands, validation, error handling
- **Depends on:** GearParams, `calc.derive()`, `calc.with_mate()`, `model.export()`, argparse
- **Used by:** End users, scripts, CI
- **No queue:** Direct export, no admission control (L04 enforcement)

## Data Flow

### Primary Request Path: Build and Export

1. **User sets parameters** (web form, API query, CLI args) → `GearParams(**values)` validated at boundary
   - File: `src/spur/params.py` (model validator calls `calc.check()`)
   - Validation happens once; after this, trust the types

2. **Fetch derived dimensions** (UI calls /api/info, CLI calls `info` command) → `calc.derive(params)`
   - File: `src/spur/calc.py`
   - Pure math; runs on every keystroke in the UI; no side effects
   - Returns `dict[str, Any]` with pitch_d, tip_d, root_d, base_d, span, warnings, etc.

3. **Build the solid** (UI preview, STL/STEP download) → `model.build(params)` under `_LOCK`
   - File: `src/spur/model.py`, lines 260–262 (entry point)
   - `_LOCK.acquire()` → `_build_cached(p)` (LRU, default 4 entries) → `_build_checked()` → `_build()`
   - Steps: `_gear_blank()` (extruded outline with analytic fillets) → `_cut_face_recesses()` (annular grooves) → `_cut_bore()` (D-bore, chamfer)
   - Validates: exactly one valid solid out

4. **Export to binary** → `model.export(params, format, quality)` under `_LOCK`
   - File: `src/spur/model.py`, lines 309–317
   - Checks `_EXPORTS` cache (LRU by size, default 64 MB)
   - Cache miss: `_write_export()` (temporary file, STL or STEP) → `_release_arenas()` (malloc_trim)
   - Returns bytes; HTTP layer adds Content-Disposition header

5. **HTTP response** (app.py: 200 with bytes, 422 with error detail, 503 if queue full)
   - File: `src/spur/app.py`, lines 110–124
   - Admission control: `_build_slot()` tries to acquire from `BUILD_QUEUE`; on fail, 503 with Retry-After

### Secondary Flow: Mating Gear Centre Distance

1. User provides `mate_teeth` query parameter (or CLI flag)
2. `calc.centre_distance(params, mate_teeth)` solves involute solver for working pressure angle
3. Returns `float` or `None` (unsolvable pair); `calc.with_mate()` adds to derive() output
4. If `None`, adds a warning; no number reported (L08)
5. Web UI displays centre_distance or "—"

### Secondary Flow: Schema (UI Form Metadata)

1. Browser requests GET /api/schema
2. `GearParams.model_json_schema()` (Pydantic v2) returns JSON schema with field metadata
3. UI builds form from schema: title, description, unit, step, group, choices
4. Every field added to GearParams appears in schema automatically (L02)

**State Management:**

- **No persistent state.** Every answer is derived from `GearParams` on demand.
- **Caches are transparent.** Solid cache (LRU, entry-bounded) and export cache (LRU, size-bounded) speed up repeated requests; safe to lose at any moment (L07).
- **Kernel lock** — module-level RLock; one thread builds at a time; others queue in the build semaphore (app.py) or wait (CLI).
- **Build queue** — BoundedSemaphore in app.py; CLI bypasses it (L04).

## Key Abstractions

**GearParams:**

- **Purpose:** Parametric gear model; validation boundary; JSON schema source
- **Examples:** `src/spur/params.py`
- **Pattern:** Pydantic BaseModel (frozen, hashable, v2); field metadata drives UI and CLI

**Profile:**

- **Purpose:** Involute tooth geometry computed from GearParams; passed through calc.py as intermediate result
- **Examples:** `src/spur/calc.py`, line 24
- **Pattern:** Frozen dataclass with maths-friendly single-letter fields (z, m, alpha, r, rb, ra, rf, psi_p); defined once in calc.py

**BuildError:**

- **Purpose:** Exception raised when solid build fails; only exception that leaves model.py (L15 in CODING_VALUES)
- **Examples:** `src/spur/model.py`, line 42; caught in app.py and cli.py
- **Pattern:** Subclass of RuntimeError; carries actionable message

## Entry Points

**Web UI:**

- **Location:** `src/spur/static/index.html` (served at GET /)
- **Triggers:** Browser load, form change
- **Responsibilities:** 
  - Builds form from /api/schema
  - Queries /api/info on every keystroke (debounced)
  - Renders 3D preview (three.js canvas)
  - Downloads STL/STEP via /api/model.{fmt}

**HTTP API:**

- **Location:** `src/spur/app.py`
- **Entry:** `app = FastAPI(...)` (line 41)
- **Triggers:** HTTP requests
- **Routes:**
  - GET / → index.html
  - GET /api/health → `{"status": "ok", "version": "0.1.0"}`
  - GET /api/schema → JSON schema
  - GET /api/info → derive() output (± mating gear info)
  - GET /api/model.{stl|step} → binary export
- **Responsibilities:**
  - Parse and validate query parameters (GearParams)
  - Admission control (queue)
  - Error formatting (422 with field names)
  - Cache-busting via GearParams equality
  - Download headers (Content-Disposition, media-type)

**CLI:**

- **Location:** `src/spur/cli.py`, `main()` function
- **Entry:** `spur` command (installed as entry point in pyproject.toml)
- **Triggers:** Shell invocation
- **Commands:**
  - `spur serve` → uvicorn wrapper (no queue, direct OCCT lock)
  - `spur info [--mate-teeth N] [--teeth Z] ...` → JSON to stdout
  - `spur export -o file.stl [--quality preview|fine] [--teeth Z] ...` → write to file
- **Responsibilities:**
  - Generate argparse from GearParams (one flag per field)
  - Parse and validate arguments
  - Call calc/model functions directly
  - Write to stderr (stderr: progress, warnings; stdout: JSON for `info`)

## Architectural Constraints

- **Threading:** Single-threaded event loop (uvicorn); all OCCT calls go through one RLock in model.py (L06). Concurrency buys latency (better responsiveness), not throughput (still serialized on the lock).
- **Global state:** 
  - `_LOCK` (RLock) in model.py — kernel lock (L06)
  - `_build_cached` (lru_cache) in model.py — solid cache, entry-bounded (L07)
  - `_EXPORTS` (_BlobCache) in model.py — export cache, size-bounded (L07)
  - `BUILD_QUEUE` (BoundedSemaphore) in app.py — admission control (L04)
  - All module-level; all documented at the point of definition
- **Circular imports:** None enforced; import-linter contracts verify (pyproject.toml, lines 117–146)
- **Vendor types:** CadQuery/OpenCascade objects do not escape model.py (enforced by design; model exports only bytes and Solids for testing)

## Anti-Patterns

### Direct imports of OCCT outside model.py

**What happens:** Code in calc.py, app.py, or cli.py directly imports cadquery or OCP.

**Why it's wrong:** Calculation layer must run on every keystroke without the weight of OCCT; the moment calc.py can reach the kernel, that property is gone silently. App and CLI have different policies (queue vs. immediate) and should not inherit web transport decisions.

**Do this instead:** Import only from model.py. If a new operation needs OCCT, add it to model.py and export a function. The import-linter contract at `pyproject.toml:128–137` enforces this.

### Calling model.export or model.build from CLI's path

**What happens:** `src/spur/cli.py` acquires the kernel lock or checks the admission queue before exporting.

**Why it's wrong:** CLI exports must be immediate (no queue) and direct (no web-layer policy); the build queue is a property of serving HTTP, not of building a gear (L04).

**Do this instead:** CLI calls `model.export()` and `model.build()` directly, bypassing the BoundedSemaphore in app.py. The lock is fine (synchronization is necessary); the queue is the violation. Import-linter contract at `pyproject.toml:139–146` enforces this.

### Changing GearParams defaults without updating tests

**What happens:** A default value is changed to suit a use case (e.g., smaller bore for smaller gears).

**Why it's wrong:** Every shareable model link omits fields it left at default. Rescaling the defaults would silently rebuild a different part from an old URL (L05).

**Do this instead:** Use capping and warnings (L03) for out-of-range defaults. The test `test_default_dimensions()` in `tests/test_calc.py` asserts that stock dimensions stay put; it will fail if this is violated, and that is the point.

### Returning a plausible-sounding number when the calculation fails

**What happens:** `centre_distance()` uses Newton's method to solve inv(aw) = inv(a) + 2·tan(a)·Σx/Σz; the unguarded loop returns confident garbage for pairs that cannot mesh.

**Why it's wrong:** This is the tool's headline "match a real gear" number. A wrong one gets cut into a bracket. The unguarded Newton loop returned negative distances and other implausible values all while returning 200 OK (L08).

**Do this instead:** Return `None` when there is no solution (bisection solver, not Newton, is safer). Report a warning instead of a number.

## Error Handling

**Strategy:** Three responses, and picking the right one is the design work.

**Patterns:**

- **Refuse (422):** A direct conflict between two things the user set explicitly. Name the fields in the error detail. Example: `bore_flat` must be between `bore_d / 2` and `bore_d`, or it's a refusal. File: `src/spur/calc.py`, line 139.

- **Cap and warn (200 OK, warning in dict):** A requested dimension that can be trimmed without contradicting an explicit choice. The trim is reported in the `warnings` array. Example: `root_fillet` is capped to fit the tooth gap; derive() warns. File: `src/spur/calc.py`, line 175.

- **Report nothing (200 OK, value is None, warning):** A value that does not exist. A warning, not a number. Example: `centre_distance()` returns None when the pair cannot mesh; the warning explains why. File: `src/spur/calc.py`, line 266.

**Beyond user input:** Fail loud, once, with an actionable message. If the kernel fails, `BuildError` is raised (deterministic for the same parameters, so retrying only burns seconds). File: `src/spur/model.py`, line 252.

## Cross-Cutting Concerns

**Logging:** None today; a tracked gap (`docs/tech_debt/active/2026-09-21-no-structured-logging.md`). Until then, no print() for diagnostics in src/; cli.py printing to stderr is user-facing output, which is fine.

**Validation:** Happens once, at the GearParams boundary. After that, trust the types. No re-validation downstream.

**Authentication:** Not applicable; no users or sessions.

**Type Safety:** mypy strict mode with one exception: `dict[str, Any]` is the honest type for API responses whose keys vary with the parameters. File: `pyproject.toml:128–137` (disallow_any_explicit is OFF, ratcheted in tech_debt).

---

*Architecture analysis: 2026-09-21*
