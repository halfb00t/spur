---
last_mapped_commit: 5252bdcd6a11f893246f614da8e5f0d431d1ed2a
last_mapped_at: 2026-09-21
---
# Codebase Structure

**Analysis Date:** 2026-09-21

## Directory Layout

```
spur/
├── src/spur/                          # Main Python package
│   ├── __init__.py                    # Version, int_env() helper
│   ├── __main__.py                    # Stub for `python -m spur`
│   ├── py.typed                       # PEP 561 marker (mypy sees real types)
│   │
│   ├── params.py                      # GearParams model (Pydantic, frozen)
│   ├── calc.py                        # Pure math: geometry, measurements, checks
│   ├── model.py                       # CAD kernel: build, export, caching
│   ├── app.py                         # FastAPI: HTTP routes, admission control
│   ├── cli.py                         # argparse: `spur` commands
│   │
│   └── static/                        # Served web UI (build artifact)
│       ├── index.html                 # HTML entry point
│       ├── app.js                     # Vanilla JS: form, preview, downloads
│       ├── style.css                  # Styles
│       └── vendor/                    # Build artifacts (never edit by hand)
│           └── three.bundle.min.js    # three.js tree-shaken by esbuild (L11)
│
├── web/                               # Source for three.js bundle
│   ├── package.json                   # esbuild, three.js
│   ├── package-lock.json
│   ├── node_modules/                  # Dev dependency (npm ci)
│   └── entry.js                       # Webpack entry; built to src/spur/static/vendor/
│
├── tests/                             # Test suite
│   ├── test_calc.py                   # Pure math: 7 KB, parametrized tests
│   ├── test_model.py                  # Solid building, exports, volume checks
│   ├── test_api.py                    # HTTP contract: FastAPI TestClient
│   └── test_cli.py                    # CLI: commands parse and run
│
├── docs/                              # Design documentation
│   ├── AGENTS.md                      # Standing brief (this repo's "CLAUDE.md")
│   ├── CODING_VALUES.md               # Full coding standard
│   ├── HOW_TO_DEVELOP.md              # Developer guide
│   ├── README.md                      # (in project root, symlinked?)
│   │
│   ├── architecture/                  # System design
│   │   ├── overview.md                # One-page system map
│   │   ├── decision_log.md            # Locked decisions (L01–L16)
│   │   ├── gear-maths/                # Involute geometry deep-dive
│   │   └── solid-model/               # CadQuery steps, fillet strategy
│   │
│   ├── requirements/                  # Functional & non-functional
│   │   ├── INDEX.md
│   │   └── YYYY-MM-DD-*.md            # Dated requirement docs
│   │
│   ├── tech_debt/                     # Known issues, deferred fixes
│   │   ├── INDEX.md
│   │   ├── active/                    # Open items
│   │   │   ├── 2026-09-21-no-structured-logging.md
│   │   │   ├── 2026-09-21-no-coverage-floor.md
│   │   │   └── 2026-09-21-untyped-info-contract.md
│   │   └── resolved/                  # Fixed with commit shas
│   │
│   ├── ideas/                         # Good ideas, not-for-now
│   │   ├── INDEX.md
│   │   └── YYYY-MM-DD-*.md
│   │
│   ├── guides/                        # How-to docs
│   │   └── INDEX.md
│   │
│   ├── review-2026-09-21.md           # Performance/memory review, measurements
│   ├── plan-2026-09-21.md             # Development plan
│   └── [other docs]
│
├── docker/                            # Container build
│   └── refresh-requirements.sh         # Regenerate requirements.txt (pinned closure, L12)
│
├── .github/                           # GitHub Actions CI
│   └── workflows/
│       └── ci.yaml                    # Lint, type-check, test, image smoke test
│
├── Dockerfile                         # Multi-platform (linux/amd64, linux/arm64)
├── compose.yaml                       # Local dev: uvicorn + optional postgres-for-testing
├── pyproject.toml                     # Build, deps, linting, types, testing, import contracts
├── requirements.txt                   # Pinned closure (generated, installed with --no-deps, L12)
├── Makefile                           # Commands: venv, verify, check, test, serve, lock, vendor
│
├── AGENTS.md                          # Standing brief (symlinked from CLAUDE.md)
└── CLAUDE.md                          # Symlink to AGENTS.md (for any agent)
```

## Directory Purposes

**`src/spur/`:**

- **Purpose:** Main Python package (installed as `spur` entry point)
- **Contains:** Models, logic layers, HTTP API, CLI, web UI static
- **Key files:** `params.py` (the model), `calc.py` (pure math), `model.py` (CAD kernel), `app.py` (HTTP), `cli.py` (CLI)

**`web/`:**

- **Purpose:** Source code for three.js bundle
- **Contains:** esbuild config, entry.js, Node dependencies
- **Build output:** `src/spur/static/vendor/three.bundle.min.js` (committed, byte-checked by CI, L11)

**`tests/`:**

- **Purpose:** Pytest test suite
- **Contains:** Unit (calc), integration (model + OCCT), contract (API + CLI), behavior tests
- **Test types:** Pure math, solid geometry (volume, topology), HTTP responses, CLI commands

**`docs/`:**

- **Purpose:** Durable design decisions, requirements, known issues, how-tos
- **Structure:** 
  - `architecture/` — locked decisions (L01–L16), design details (gear math, solid building)
  - `requirements/` — functional and non-functional specs
  - `tech_debt/active/` — known issues with triggers and fixes; blocker items get fixed immediately
  - `tech_debt/resolved/` — fixed issues with commit sha
  - `ideas/` — good ideas deferred
  - `guides/` — how-to docs for developers
- **Key pattern:** One file per item, `YYYY-MM-DD-short-slug.md`, with INDEX.md in each dir

**`docker/`:**

- **Purpose:** Container build tooling
- **Contains:** `refresh-requirements.sh` (regenerates `requirements.txt` via pip-compile, L12)

**`.github/`:**

- **Purpose:** CI/CD pipelines
- **Contains:** GitHub Actions workflows (lint, type-check, import-lint, test, image build smoke test)

**`.planning/codebase/`:**

- **Purpose:** Live codebase maps (written by gsd-map-codebase)
- **Contains:** ARCHITECTURE.md, STRUCTURE.md, CONVENTIONS.md, TESTING.md, CONCERNS.md (as applicable)
- **Updated:** After major code changes or architectural shifts

## Key File Locations

**Entry Points:**

- **Web UI:** `src/spur/static/index.html` (GET /)
  - Vanilla HTML; loaded by FastAPI's StaticFiles mount
  - Form built by app.js from /api/schema
  - 3D preview via three.js canvas

- **HTTP API:** `src/spur/app.py` (FastAPI instance `app`)
  - Run: `make serve` or `spur serve`
  - Endpoints: GET /, /api/health, /api/schema, /api/info, /api/model.{stl|step}
  - Mounted at / (no prefix by default; SPUR_ROOT_PATH for reverse proxy)

- **CLI:** `src/spur/cli.py` (main() function)
  - Entry point: `spur` (installed by pyproject.toml:30)
  - Commands: `spur serve`, `spur info`, `spur export`

**Configuration:**

- **Build & packaging:** `pyproject.toml`
  - Project metadata, dependencies, entry points, hatch build config
  - Ruff (linter), mypy (type-checker), pytest (test runner), import-linter (contracts)
  - Three import-linter contracts enforcing layer boundaries (lines 117–146)

- **Pinned dependencies:** `requirements.txt` (generated, never hand-edit)
  - Run `make lock` to regenerate (calls docker/refresh-requirements.sh)
  - Installed in Dockerfile with `--no-deps` (L12)

- **Environment vars:** Read at `src/spur/__init__.py` (int_env helper)
  - SPUR_SOLID_CACHE (default 4) — build cache entry count
  - SPUR_EXPORT_CACHE_MB (default 64) — export cache size limit
  - SPUR_MAX_QUEUED_BUILDS (default 4) — HTTP admission control
  - SPUR_HOST, SPUR_PORT, SPUR_WORKERS, SPUR_ROOT_PATH — serve command

- **Makefile:** Development commands
  - `make` lists all targets
  - `make verify` is the gate (lint, types, import contracts, no-fake-done scan, pytest)
  - `make check` adds container tests (requires Docker)

**Core Logic:**

- **Parameters:** `src/spur/params.py` (GearParams model, ~90 lines)
  - Pydantic BaseModel (frozen, hashable)
  - Field metadata drives UI form (group, unit, step, help)
  - Model validator calls calc.check() for cross-field validation

- **Calculation:** `src/spur/calc.py` (~270 lines)
  - Pure functions: profile(), derive(), check(), centre_distance(), with_mate(), root_fillet(), recess_radii(), span_measurement()
  - No imports of cadquery/OCP (enforced)
  - Invokes bisection solver for involute angle (L08, safer than Newton)

- **Solid Building:** `src/spur/model.py` (~318 lines)
  - Gateway to CadQuery/OpenCascade (only place direct imports allowed)
  - Functions: _outline() (analytic fillets), _gear_blank(), _cut_face_recesses(), _cut_bore()
  - build() (cached, under lock), export() (cached by size, arena-trimmed on miss)
  - Thread-safe: _LOCK (RLock) around all OCCT calls

- **HTTP API:** `src/spur/app.py` (~125 lines)
  - FastAPI routes for schema, info, model export
  - Admission control: BUILD_QUEUE (BoundedSemaphore, max SPUR_MAX_QUEUED_BUILDS)
  - Error formatting: 422 for infeasible params (names the fields), 503 for queue full

- **CLI:** `src/spur/cli.py` (~115 lines)
  - argparse-based command parser
  - Generates flags from GearParams fields (one flag per field, alphabetically)
  - Commands: serve (uvicorn wrapper), info (JSON to stdout), export (file write)
  - No queue (L04 enforcement); direct model.export()

**Testing:**

- **Unit (pure math):** `tests/test_calc.py` (~110 lines, parameterized)
  - Fixtures: GearParams(teeth=..., module=..., etc.) for different configurations
  - Assertions: dimensions match expected values (e.g., pitch_d ≈ 33.25 for stock gear)
  - Pattern: one scenario per test; test names read as requirements

- **Integration (solid building):** `tests/test_model.py` (~60 lines)
  - Fixtures: GearParams for edge cases (minimal tooth count, maximum bore, etc.)
  - Assertions: isValid(), BoundingBox matches expected size, volume calculations
  - Pattern: no snapshots; assert geometry properties, not snapshots

- **Contract (HTTP API):** `tests/test_api.py` (~60 lines)
  - Fixture: FastAPI TestClient(app)
  - Assertions: status codes, content-type, error detail shape (fields list, message)
  - Pattern: test the contract the UI and scripts depend on

- **Behavior (CLI):** `tests/test_cli.py` (~50 lines)
  - Fixture: parse args and call command functions
  - Assertions: exit code, output format, file writes
  - Pattern: README examples are tests (L157 in CODING_VALUES)

**Static Files & Web Bundle:**

- **Entry point:** `src/spur/static/index.html` (hand-written HTML, never generated)
- **Styles:** `src/spur/static/style.css` (hand-written CSS, ~150 lines)
- **JavaScript:** `src/spur/static/app.js` (generated from web/entry.js by esbuild, ~12 KB minified)
  - Form building from /api/schema
  - Preview rendering with three.js
  - Download button handlers

- **three.js bundle:** `src/spur/static/vendor/three.bundle.min.js` (build artifact, ~500 KB)
  - Built from `web/entry.js` by esbuild (tree-shaken)
  - Committed to repo; CI byte-checks it matches rebuild (L11)
  - Never edit by hand; run `make vendor` to rebuild

## Naming Conventions

**Files:**

- **Module files:** `snake_case.py` (e.g., `calc.py`, `model.py`)
- **Test files:** `test_*.py` (e.g., `test_calc.py`, `test_api.py`)
- **Data/config files:** `lowercase.txt`, `lowercase.yaml` (e.g., `requirements.txt`, `compose.yaml`)
- **Docs:** `UPPERCASE.md` or `YYYY-MM-DD-slug.md` (e.g., `ARCHITECTURE.md`, `2026-09-21-no-structured-logging.md`)

**Directories:**

- **Package:** `lowercase` (e.g., `spur/`, `tests/`)
- **Categories:** `lowercase` (e.g., `docs/`, `docker/`, `ideas/`, `tech_debt/`)
- **Dates:** None in directory names; dates go in file names within INDEX.md

**Functions & Variables:**

- **Functions:** `snake_case` for public, `_snake_case` for private (e.g., `derive()`, `_build()`)
- **Classes:** `PascalCase` (e.g., `GearParams`, `Profile`, `BuildError`)
- **Constants:** `UPPER_CASE` (e.g., `MIN_WALL`, `FLANK_POINTS`, `TOL`, `TESSELLATION`)
- **Math symbols:** Single letters acceptable only in short routines (e.g., `z`, `m`, `alpha`, `r`, `rb`, `ra`, `rf` in Profile; defined once per file)

## Where to Add New Code

**New Feature (e.g., new bore type, new measurement):**

- **Math:** Add function to `src/spur/calc.py`, add field to GearParams if parametric
- **Solid:** Add geometry step to `src/spur/model.py` (e.g., `_cut_feature()`)
- **API:** Endpoint or response field in `src/spur/app.py`
- **CLI:** Flag (auto-generated from GearParams) or new command in `src/spur/cli.py`
- **UI:** Form group in HTML (auto-built from schema) and display in app.js
- **Tests:** Unit test in `tests/test_calc.py`, integration test in `tests/test_model.py`, contract test in `tests/test_api.py`, behavior test in `tests/test_cli.py`

**New Utility / Helper (e.g., math function shared by calc and model):**

- **If pure math:** `src/spur/calc.py` (no OCCT imports)
- **If using OCCT:** `src/spur/model.py` (only place OCCT imports are allowed)
- **If supporting tests:** `tests/conftest.py` if fixtures are needed (currently just test files)

**New Module (rare — only if a boundary broke):**

1. Add to `src/spur/` directory
2. Add import-linter contract in `pyproject.toml` to enforce its place in the layer stack
3. Update `CODING_VALUES.md` if adding a new layer

**New Doc:**

- **Decision:** `docs/architecture/decision_log.md` (edit existing, add new `Lxx` entry)
- **Idea:** `docs/ideas/YYYY-MM-DD-slug.md` + row in `docs/ideas/INDEX.md`
- **Tech debt:** `docs/tech_debt/active/YYYY-MM-DD-slug.md` + row in INDEX; move to resolved/ when fixed
- **Requirement:** `docs/requirements/YYYY-MM-DD-slug.md` + row in INDEX
- **How-to:** `docs/guides/YYYY-MM-DD-slug.md` + row in INDEX

## Special Directories

**`.venv/`:**

- **Purpose:** Virtual environment (created by `make venv`)
- **Generated:** Yes (pip install -e '.[dev]' from pyproject.toml)
- **Committed:** No (in .gitignore)
- **Gitignored:** Yes; do not commit

**`.mypy_cache/`, `.ruff_cache/`, `.pytest_cache/`, `.import_linter_cache/`:**

- **Purpose:** Tool caches
- **Generated:** Yes (by ruff, mypy, pytest, import-linter)
- **Committed:** No (in .gitignore)

**`src/spur/__pycache__/`, `tests/__pycache__/`:**

- **Purpose:** Python bytecode cache
- **Generated:** Yes (by Python)
- **Committed:** No (in .gitignore)

**`src/spur/static/vendor/`:**

- **Purpose:** Build artifact (three.js bundle from web/ build)
- **Generated:** Yes (by esbuild via `make vendor`)
- **Committed:** Yes (byte-checked by CI to prevent drift, L11)
- **Edit:** Never by hand; edit `web/entry.js`, run `make vendor`, commit the result

**`web/node_modules/`:**

- **Purpose:** npm dependencies for esbuild
- **Generated:** Yes (by npm ci)
- **Committed:** No (in .gitignore)

**`.planning/codebase/`:**

- **Purpose:** Live architecture maps
- **Generated:** Yes (by gsd-map-codebase skill)
- **Committed:** Yes (for reference and continuity)
- **Contents:** ARCHITECTURE.md, STRUCTURE.md, CONVENTIONS.md, TESTING.md, CONCERNS.md (as applicable)

---

*Structure analysis: 2026-09-21*
