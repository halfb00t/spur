---
last_mapped_commit: 41d23c70643108293120e36d6abd823739892ca8
last_mapped_at: 2026-10-02
---
# Codebase Structure

**Analysis Date:** 2026-10-02

## Directory Layout

```
spur/
├── src/spur/                      # Main Python package
│   ├── __init__.py                # Version, int_env() helper
│   ├── __main__.py                # CLI entry point
│   ├── params.py                  # GearParams model + field metadata (181 lines)
│   ├── calc.py                    # Pure gear math, DerivedDimensions (1179 lines)
│   ├── model.py                   # CadQuery kernel, solid building, export (570 lines)
│   ├── pool.py                    # Worker process pool, build routing (226 lines)
│   ├── app.py                     # FastAPI app, endpoints, caching (499 lines)
│   ├── cli.py                     # Command-line interface (153 lines)
│   ├── build_errors.py            # BuildError, BuildTimeout exception types (25 lines)
│   ├── records.py                 # JSON logging, event record vocabulary (282 lines)
│   ├── static/                    # Served web UI files
│   │   ├── index.html             # HTML page shell
│   │   ├── app.js                 # Form, preview, event handling (12 KB)
│   │   ├── style.css              # Gear form styling
│   │   └── vendor/                # Vendored esbuild bundle
│   │       └── three.bundle.min.js # Tree-shaken three.js (~570 KB)
│   └── py.typed                   # PEP 561 marker for type stubs
│
├── web/                           # Web UI source (esbuild input)
│   ├── entry.js                   # Esbuild entry point
│   ├── package.json               # three.js only dependency
│   ├── package-lock.json
│   └── node_modules/
│
├── tests/                         # pytest test suite
│   ├── conftest.py                # pytest fixtures, autouse cache reset
│   ├── composition.py             # Test helpers (backend injection, etc.)
│   ├── test_calc.py               # calc.py unit tests
│   ├── test_model.py              # model.py solid building tests
│   ├── test_pool.py               # pool.py worker lifecycle tests
│   ├── test_api.py                # app.py endpoint tests
│   ├── test_cli.py                # cli.py command tests
│   ├── test_records.py            # records.py JSON logging tests
│   ├── test_bench.py              # bench/ module tests
│   ├── test_skip_tokens.py        # CI skip token validation tests
│   ├── test_pr_land.py            # PR merge validation tests
│   └── regression/                # Regression test suite
│       ├── test_pre_v0_2.py       # Pre-v0.2 parameter fixture replay
│       ├── test_corpus.py         # Corpus build sweep validation
│       ├── pre_v0_2.json          # Pinned 44 parameter sets with measurements
│       ├── capture.py             # JSON capture utility
│       └── corpus.py              # 40-gear corpus generation
│
├── bench/                         # Microbenchmarks and performance analysis
│   ├── __init__.py
│   ├── latency.py                 # Latency sweep (single/concurrent scenarios)
│   ├── memory.py                  # Memory usage sweep (N workers)
│   ├── build_time.py              # Per-gear build time analysis
│   ├── export_cost.py             # Export (STL/STEP/gzip) cost breakdown
│   ├── tip_chamfer_spike.py       # Tip chamfer kernel spike test
│   ├── honeycomb_spike.py         # Honeycomb cell-count kernel spike test
│   ├── corpus.py                  # 40-gear test corpus (160–199 teeth)
│   ├── README.md                  # How to run benchmarks
│   ├── RESULTS.md                 # Measured results from all phases
│   └── sweeps/                    # Generated sweep data files
│       ├── memory_N_1/            # Memory sweep output, N=1
│       ├── memory_N_2/            # Memory sweep output, N=2
│       ├── memory_N_4/            # Memory sweep output, N=4
│       ├── latency_single/        # Latency single-request sweep
│       └── latency_concurrent/    # Latency concurrent-requests sweep
│
├── docker/                        # Container build and runtime
│   ├── Dockerfile                 # Multi-stage build, Python 3.12
│   ├── compose.yaml               # Docker Compose orchestration
│   ├── refresh-requirements.sh    # Generate pinned requirements.txt
│   ├── smoke.py                   # Smoke test run inside image
│   └── healthcheck.sh             # HEALTHCHECK curl test
│
├── scripts/                       # Utility scripts
│   ├── pr_land.py                 # PR merge validation and landing tool
│   ├── skip_tokens.py             # CI skip token parsing
│   └── gzip_bench.py              # Gzip compression level microbench
│
├── docs/                          # Project documentation
│   ├── architecture/              # Architecture documentation
│   │   ├── overview.md            # One-page system map
│   │   ├── decision_log.md        # Locked decisions (L01–L26+)
│   │   ├── http-api.md            # API endpoint contract
│   │   ├── cli.md                 # CLI command reference
│   │   ├── web-ui.md              # Web form and viewer
│   │   ├── packaging.md           # Container build and release
│   │   ├── gear-maths/            # Pure math layer design
│   │   │   ├── strategy.md        # Involute geometry strategy
│   │   │   ├── implementation.md  # Math implementation notes
│   │   │   ├── errors_and_logging.md
│   │   │   ├── tests.md
│   │   │   └── tactics.md
│   │   └── solid-model/           # CAD kernel design
│   │       ├── strategy.md        # CAD approach and trade-offs
│   │       ├── implementation.md  # CadQuery usage notes
│   │       ├── errors_and_logging.md
│   │       ├── tests.md
│   │       └── tactics.md
│   │
│   ├── requirements/              # Requirements by subsystem
│   │   ├── REQ-measured-memory-ceiling.md
│   │   └── REQ-cad-off-event-loop.md
│   │
│   ├── guides/                    # User/developer guides
│   │   └── HOW_TO_DEVELOP.md     # Development setup, verification, merge gate
│   │
│   ├── ideas/                     # Future work, not for now
│   │   └── [dated proposal files]
│   │
│   └── tech_debt/                 # Known-bad code, deferred fixes
│       ├── active/                # Items blocking future work
│       │   └── [dated files, Severity: blocker/must/nice]
│       └── resolved/              # Fixed items, with commit SHAs
│           └── [dated files with resolution]
│
├── .github/                       # GitHub Actions CI
│   └── workflows/
│       ├── ci.yml                 # Test matrix (3.12 only), docker image build, bundle check
│       └── required-jobs.txt      # List of jobs that must pass to merge to main
│
├── .pre-commit-config.yaml        # Pre-commit hooks (verify, commit-msg token check)
├── pyproject.toml                 # Project metadata, build config, tool settings (ruff, mypy, pytest, import-linter)
├── requirements.txt               # Pinned full dependency closure (31 packages, L12)
├── Makefile                       # make verify, make serve, make bench, etc.
├── Dockerfile                     # Production image build
├── compose.yaml                   # docker-compose for local serving
├── README.md                      # User-facing project overview
├── AGENTS.md                      # Standing brief for AI agents in this repo
├── CLAUDE.md                      # Symlink to AGENTS.md
└── .planning/                     # GSD project orchestration (generated)
    └── codebase/                  # This maps (ARCHITECTURE.md, STRUCTURE.md, etc.)
```

## Directory Purposes

**`src/spur/` — Main Package:**
All production code lives here. The package structure mirrors the architectural layers:
- **Parameters** (`params.py`): One validated model, shared by all three interfaces
- **Pure math** (`calc.py`): Keystroke-fast, kernel-free geometry and derived dimensions
- **CAD kernel** (`model.py`): Only module that touches CadQuery/OpenCascade
- **Worker pool** (`pool.py`): Process lifecycle and affinity-based routing
- **HTTP API** (`app.py`): FastAPI application and request handling
- **CLI** (`cli.py`): Command-line interface
- **Cross-cutting** (`build_errors.py`, `records.py`): Shared exception types and logging

**`tests/` — Test Suite:**
Mirrors the production package structure with `test_` prefix. Contains:
- **Unit tests** — Most tests are unit tests for individual modules (`test_calc.py`, `test_model.py`, etc.)
- **Integration tests** — `test_api.py` tests HTTP endpoints end-to-end
- **Regression tests** — `regression/test_pre_v0_2.py` pins 44 hand-crafted parameter sets and replays them to detect geometry regressions

**`bench/` — Performance Characterization:**
Benchmarks are part of the repository and run manually to measure:
- **Latency** (`latency.py`): Single and concurrent build scenarios; measures p95 under-load/idle ratio
- **Memory** (`memory.py`): Peak RSS for N=1, 2, 4 workers; feeds L17 decision
- **Build time** (`build_time.py`): Per-gear construction time
- **Export cost** (`export_cost.py`): STL vs STEP vs gzip encoding costs
- **Spikes** (`tip_chamfer_spike.py`, `honeycomb_spike.py`): Kernel performance edges that constrain defaults
- **Results** (`RESULTS.md`): Every measured number, machine, date, and method

**`docker/` — Container Build:**
Production image definition and utilities:
- **Dockerfile:** Multi-stage build, Python 3.12, pinned closure, health check
- **compose.yaml:** Local development via Docker Compose
- **refresh-requirements.sh:** Script to regenerate pinned `requirements.txt` inside a container
- **smoke.py:** Quick smoke test to verify image is working

**`scripts/` — Utilities:**
CLI utilities that live outside the main package:
- **pr_land.py:** Merge gate for PRs to `main`; checks CI passes, no skip tokens, head is recent
- **skip_tokens.py:** Parsing for GitHub Actions skip tokens
- **gzip_bench.py:** Microbenchmark for gzip compression levels

**`docs/` — Project Documentation:**
- **architecture/:** System design, decisions (decision_log.md is the locked-decision source of truth)
- **requirements/:** REQ-prefixed measurable constraints
- **guides/:** HOW_TO_DEVELOP.md explains setup, verification, and merge procedure
- **ideas/:** Future improvements, not for this milestone
- **tech_debt/:** Known-bad code; active items are blocker/must/nice severity; resolved items record the fix commit

**`.github/workflows/` — CI:**
- **ci.yml:** Test matrix (3.12 only, after L23), `vendor-bundle` byte-check, Docker image build
- **required-jobs.txt:** The exact set of jobs that must pass to merge to main; kept in sync with ci.yml by a test

## Key File Locations

**Entry Points:**
- `src/spur/__main__.py`: CLI entry point
- `src/spur/app.py`: FastAPI app instance
- `src/spur/cli.py`: CLI command functions

**Configuration:**
- `pyproject.toml`: Package metadata, ruff/mypy/pytest/import-linter config, tool.hatch build settings
- `requirements.txt`: Pinned dependency closure for Docker image (generated, do not edit by hand)
- `.pre-commit-config.yaml`: Hooks run before commit (verify gate, commit-msg token check)

**Core Logic:**
- `src/spur/params.py`: Parameter validation and JSON schema source
- `src/spur/calc.py`: Involute geometry, derived dimensions, feasibility
- `src/spur/model.py`: CadQuery solid building, STL/STEP export
- `src/spur/pool.py`: Worker process pool and build routing
- `src/spur/app.py`: HTTP endpoints, caching, admission control

**Testing:**
- `tests/conftest.py`: pytest fixtures
- `tests/regression/pre_v0_2.json`: Pinned 44 parameter sets for regression testing
- `tests/regression/test_pre_v0_2.py`: Replay fixture, check geometry invariants

**Performance:**
- `bench/RESULTS.md`: Measured numbers (latency, memory, build time)
- `bench/latency.py`: Latency measurement under single and concurrent load
- `bench/memory.py`: Peak RSS measurement for different worker counts

## Naming Conventions

**Files:**
- Python modules: `snake_case.py` (e.g., `build_errors.py`, `test_api.py`)
- Test files: `test_*.py` (e.g., `test_calc.py`)
- Regression tests: `tests/regression/test_*.py`
- Documentation: `SCREAMING_SNAKE_CASE.md` or prose (e.g., `RESULTS.md`, `overview.md`)
- JSON fixtures: `snake_case.json` (e.g., `pre_v0_2.json`)
- Dated items: `YYYY-MM-DD-short-slug.md` (e.g., `2026-09-21-no-structured-logging.md`)

**Directories:**
- Production code: `src/` (PEP 517 wheel layout)
- Tests: `tests/` (pytest convention)
- Benchmarks: `bench/` (manually run)
- Documentation: `docs/` with subdirs by type (architecture/, guides/, etc.)
- Infrastructure: `docker/`, `scripts/`, `.github/`

**Python Identifiers:**
- Functions: `snake_case` (e.g., `derive()`, `build_export()`, `_release_arenas()`)
- Classes: `PascalCase` (e.g., `GearParams`, `BuildPool`, `DerivedDimensions`)
- Constants: `SCREAMING_SNAKE_CASE` (e.g., `MIN_WALL`, `SPUR_SOLID_CACHE`)
- Private: `_leading_underscore` for module-level, `__double` is rare (only `__init__`, `__main__`)
- Type variables: `P`, `T` as single uppercase letters (e.g., `P = ParamSpec("P")`)

## Where to Add New Code

**New Feature (e.g., a new bore shape):**
- **Parameter definition:** Add field to `GearParams` in `src/spur/params.py`
- **Geometry calculation:** Add helper to `src/spur/calc.py` (pure math)
- **CAD building:** Add solid-building code to `src/spur/model.py` inside `build()` function
- **Tests:** 
  - Unit test for geometry helper in `tests/test_calc.py`
  - Integration test for CAD output in `tests/test_model.py`
  - Regression test: add parameter set(s) to `tests/regression/pre_v0_2.json` and re-run fixture
- **Documentation:** Add strategy notes to `docs/architecture/solid-model/strategy.md` if the approach is novel

**New API Endpoint (e.g., `/api/analysis`):**
- **Endpoint definition:** Add route handler to `src/spur/app.py` using `@app.get()` or `@app.post()`
- **Request/response models:** Define Pydantic model(s) in `src/spur/app.py` (close to the endpoint)
- **Logic:** If computation is heavy, route through pool via `backend()`; if lightweight, call `calc` directly
- **Tests:** Add test case to `tests/test_api.py`
- **Logging:** Call a helper from `records.py` (or add a new one if the event is novel)

**New CLI Command (e.g., `spur validate`):**
- **Command handler:** Add `cmd_validate()` function to `src/spur/cli.py`
- **Argument parsing:** Use `_add_gear_args()` and `argparse` like existing commands
- **Entry point:** Add subparser branch in `main()` (if not already present)
- **Tests:** Add test case to `tests/test_cli.py`
- **Note:** CLI must never import `app.py` (L04) — use `calc.derive()` or `model.export()` directly

**New Utility or Helper:**
- **Shared across modules:** `src/spur/` as a new module or add to an existing one
- **Test-only helpers:** `tests/composition.py` (already holds test fixtures and backend injection)
- **Build/script utilities:** `scripts/` directory (e.g., `scripts/new_tool.py`)

**New Documentation:**
- **Architecture decision:** Add entry to `docs/architecture/decision_log.md` (L-prefixed, append-only)
- **Known issue:** Create dated file in `docs/tech_debt/active/` with Severity tag; add row to `docs/tech_debt/active/INDEX.md`
- **Resolved issue:** Move from `active/` to `resolved/` in the same commit that fixes it; record commit SHA
- **Future idea:** Create dated file in `docs/ideas/`; no need to add to index unless it's blocking something

## Special Directories

**`.planning/`:**
- Purpose: GSD (Generalist System Designer) project orchestration state
- Generated: Automatically by GSD CLI commands
- Committed: No, added to `.gitignore`

**`web/node_modules/`:**
- Purpose: esbuild and three.js source for building the vendored bundle
- Generated: `npm install` (or not needed if not modifying web UI)
- Committed: No, listed in `.gitignore`

**`bench/sweeps/`:**
- Purpose: Intermediate and final data files from benchmark runs
- Generated: Created by `bench/latency.py`, `bench/memory.py`, etc. when run
- Committed: No, only human-readable `RESULTS.md` is committed

**`tests/regression/`:**
- Purpose: Regression testing — replays hand-crafted parameter sets to detect unintended geometry changes
- Committed: Yes
- Important: `pre_v0_2.json` is pinned; every commit that builds successfully must keep it unchanged (verified by `git diff --exit-code` after test runs)

---

*Structure analysis: 2026-10-02*
