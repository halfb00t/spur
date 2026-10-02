---
last_mapped_commit: 41d23c70643108293120e36d6abd823739892ca8
last_mapped_at: 2026-10-02
---
# Testing Patterns

**Analysis Date:** 2026-10-02

## Test Framework

**Runner:**
- pytest 8+ (`tests/test_*.py` collected automatically)
- Config: `pyproject.toml` `[tool.pytest.ini_options]`

**Test Discovery:**
- `testpaths = ["tests"]` — pytest searches `tests/` directory only
- `addopts = "--strict-markers --strict-config"` — all markers and config must be declared
- `xfail_strict = true` — expected failures that pass are treated as failures

**Assertion Library:**
- pytest native assertions (no explicit import needed): `assert`, `assert x == y`, `pytest.approx()` for float comparison
- Custom markers: none currently; tests use standard parametrize and fixture patterns

**Run Commands:**

```bash
make test                    # Run full test suite (pytest)
make verify                  # Gate: ruff, mypy, lint-imports, no-fake-done, pytest
make check                   # Everything CI runs locally (needs Docker)
.venv/bin/pytest             # Direct pytest invocation
.venv/bin/pytest tests/test_calc.py -v           # Single file with verbose output
.venv/bin/pytest -k test_name                    # Filter by test name
```

## Test File Organization

**Location:** `tests/` directory at repo root
- `tests/test_*.py` — collected test modules (11 files as of 2026-10-02)
- `tests/composition.py` — shared data module, NOT collected (no `test_` prefix)
- `tests/conftest.py` — pytest fixtures (autouse logger reset)
- `tests/regression/` — regression test suite with pre-recorded data

**Naming Convention:**
- Test files: `test_calc.py`, `test_model.py`, `test_api.py`, `test_cli.py`, `test_pool.py`, `test_records.py`, `test_bench.py`, `test_skip_tokens.py`, `test_pr_land.py`
- Data modules (non-collected): `composition.py`, `tests/regression/capture.py`, `tests/regression/corpus.py`
- Test functions: `test_<requirement_as_phrase>`: `test_default_dimensions()`, `test_a_derived_dimensions_result_cannot_be_changed()`, `test_caliper_reading_is_short_for_odd_tooth_counts()`

## Test Structure

**Autouse Fixture (conftest.py):**

```python
@pytest.fixture(autouse=True)
def _reset_root_logger() -> Iterator[None]:
    """Snapshot root logger handlers and level before test; restore after.
    
    Prevents test-to-test pollution when records.configure() is called.
    Each test sees a clean logger state regardless of execution order.
    """
    root = logging.getLogger()
    handlers_before = list(root.handlers)
    level_before = root.level
    yield
    # restore after test
```

**Test Families (composition.py):**
Shared, hand-written cross-product tables — NOT computed from code under test (avoids tautology, L08):

```python
BORES = {
    "round": {"bore_flat": 0},
    "d-flat": {},  # defaults: bore_d 9, bore_flat 8
    "keyed": {"bore_flat": 0, "keyway_width": 3, "keyway_depth": 1.4},
    "hex": {"bore_hex": 6},
}

CUTOUTS = {
    "none": {},
    "spokes": {"spoke_count": 4, "spoke_width": 2, "hub_d": 13.2, ...},
    "holes": {"hole_count": 6, "hole_d": 4, "hole_circle_d": 20},
    "cells": {"hex_cell": 3, "hex_wall": 1},
}

RECESSES = {"both": {}, "top": {"recess_sides": "top"}, "none": {"recess_sides": "none"}}
TIPS = {"off": {}, "on": {"tip_chamfer": 1.75}}

ALWAYS = frozenset({  # fields always present
    "pitch_d", "tip_d", "root_d", "base_d", "caliper_over_tips", ...
})

BORE_FIELDS = {  # fields added per bore type
    "round": frozenset({"bore_effective"}),
    "keyed": frozenset({"bore_effective", "keyway_floor_to_wall", ...}),
    ...
}
```

**Parametrize Pattern:**

```python
@pytest.mark.parametrize("kw", [
    {},
    {"pressure_angle": 20},
    {"bore_flat": 0},
    ...
])
def test_builds_one_valid_solid(kw: dict[str, object]) -> None:
    p = GearParams.model_validate(kw)
    s = build(p)
    assert s.isValid()
```

## Test Types

**Unit Tests** (`tests/test_calc.py`)
- **Scope:** Pure arithmetic in `calc.py` (no CAD kernel)
- **Approach:** Exhaustive on mathematical rules; parametrized
- **Fixtures:** composition families from `composition.py`, hand-checked values (e.g., Wildhaber span measurements)
- **Assertions:** `pytest.approx()` for floats, exact equality for integers
- **Size:** 73,421 bytes (largest test file as of 2026-10-02)
- **Examples:**
  - `test_default_dimensions()` — verify all derived fields against hand-calculated values
  - `test_span_measurement()` — parametrized against known span values (`m=1.75, pa=20, k=3, w=13.381`)
  - `test_root_fillet_is_capped_with_a_warning()` — assert cap + warning tuple

**Integration Tests** (`tests/test_model.py`)
- **Scope:** `model.py` against the real CadQuery/OpenCascade kernel
- **Approach:** Assert geometry properties (volume, topology, watertightness), NOT snapshots
- **Fixtures:** `composition.py` families, parametrized cross products
- **Assertions:** `solid.isValid()`, bounding box checks, facet/edge/vertex topology
- **Mocking:** None — test the real kernel, not a mock (mocking would test the mock, not the code)
- **Size:** 87,732 bytes
- **Examples:**
  - `test_builds_one_valid_solid()` — parametrized over 96 combinations (4 bores × 6 cutouts × 2 recesses × 2 tip states)
  - `test_every_rim_point_stays_in_bound()` — geometry constraint: BoundingBox.xlen/ylen match parameter-derived limits
  - `test_topology_counts_for_hex_bore()` — edge/vertex counts match expected topology

**Contract Tests** (`tests/test_api.py`)
- **Scope:** `app.py` API through FastAPI TestClient (no lifespan, no pool)
- **Approach:** Request/response contracts, error shapes the UI parses, schema correctness
- **Fixtures:** Dependency override: `app.dependency_overrides[build_backend] = lambda: _inline_backend`
  - Runs builds in-process (same code path as CLI, per D-15)
  - Avoids pool-state dependencies
  - Allows testing exact error responses
- **Assertions:** Status codes, response schema, field presence/absence, unit metadata in OpenAPI schema
- **Size:** 49,877 bytes
- **Examples:**
  - `test_health()` — `/api/health` returns `{"status": "ok", "pool": null/obj}`
  - `test_schema_drives_the_form()` — `/api/schema` has `group`, `unit`, `step` metadata for UI
  - `test_openapi_documents_the_typed_contracts()` — DerivedDimensions fields exactly match OpenAPI schema

**CLI Contract Tests** (`tests/test_cli.py`)
- **Scope:** Command-line interface (`cli.py`)
- **Approach:** CLI parity with API (same document serialized), README examples must work
- **Fixtures:** Composition families, `capsys` pytest fixture to capture stdout/stderr
- **Assertions:** `json.loads()` roundtrip, error codes, flag parsing
- **Size:** 22,875 bytes
- **Examples:**
  - `test_cli_and_api_print_the_same_document()` — `cli info --teeth 21` == `GET /api/info?teeth=21`
  - `test_readme_export_examples_run()` — README's documented export commands actually work
  - `test_info_rejects_a_mate_the_api_would_reject()` — CLI bounds match `InfoQuery` schema

**Logging Tests** (`tests/test_records.py`)
- **Scope:** Structured logger (`records.py`): formatter, configuration, per-request vocabulary
- **Approach:** End-to-end: configure → call → capture stderr → `json.loads()`
- **Fixtures:** Dependency override same as `test_api.py`; `caplog`/`capsys` pytest fixtures
- **Assertions:** JSON payload round-trips through `json.loads()`, exact field names
- **Size:** 12,312 bytes
- **Examples:**
  - `test_a_model_request_emits_one_export_served_line_that_json_loads_round_trips()` — real stderr output parses as JSON
  - `test_configure_called_twice_installs_exactly_one_handler()` — idempotent configuration
  - `test_the_formatter_round_trips_every_application_field_through_json_loads()` — `extra=` dict preserved

**Pool Tests** (`tests/test_pool.py`)
- **Scope:** Worker process pool (`pool.py`)
- **Approach:** Subprocess lifecycle, build queueing, timeout handling
- **Fixtures:** None mock the pool; tests drive it live
- **Size:** 27,111 bytes

**Benchmark Tests** (`tests/test_bench.py`)
- **Scope:** Measurement assertions from `bench/` scripts
- **Approach:** Verify recorded data (Phase 8 hex-bore sweep, Phase 10 tip-chamfer, Phase 11 body-cutouts, etc.)
- **Assertions:** Sweep contents match expected cross products, budget predicates work, STL file format
- **Size:** 37,037 bytes
- **Examples:**
  - `test_the_hex_bore_sweep_is_every_combination_d_11_names()` — 16 rows = 200 teeth × {1.75, 10} module × {200, 12.7} hex × {both, none} recess × {0.4, 3} chamfer
  - `test_the_report_names_the_largest_fine_stl_and_breaks_a_tie_by_file_order()` — report formatting

**Regression Tests** (`tests/regression/`)
- **Scope:** Pre-recorded v0.2 parameter sets
- **Fixtures:** `tests/regression/pre_v0_2.json` (L05 fixture: absolute defaults stay frozen)
- **Approach:** Replay corpus against current code; detect silent changes
- **Size:** Separate directory with `test_pre_v0_2.py`, `test_corpus.py`, `capture.py`

## Patterns

**Setup:**

```python
def test_something() -> None:
    p = GearParams()  # or with overrides: GearParams(teeth=25, ...)
    d = derive(p)     # -> DerivedDimensions
    s = build(p)      # -> cq.Workplane (solid)
```

**Parametrize with Composition:**

```python
@pytest.mark.parametrize(("bore_type", "cutout_type"), [
    ("round", "none"), ("d-flat", "spokes"), ("hex", "cells"), ...
])
def test_each_combination(bore_type: str, cutout_type: str) -> None:
    p = GearParams.model_validate({**BORES[bore_type], **CUTOUTS[cutout_type]})
    # test logic
```

**Teardown with Dependency Override:**

```python
@pytest.fixture(autouse=True, scope="module")
def _inline_build_backend() -> Iterator[None]:
    app.dependency_overrides[build_backend] = lambda: _inline_backend
    yield
    app.dependency_overrides.pop(build_backend, None)
```

**Async Testing:**
Not used in this project — all tests are synchronous; async code in `app.py` is tested via TestClient (which runs the event loop internally).

**Error Testing:**

```python
def test_infeasible_parameters_name_their_fields(kw: dict[str, object], field: str) -> None:
    with pytest.raises(ValidationError) as exc:
        GearParams.model_validate(kw)
    assert field in str(exc.value)
```

## Mocking

**Framework:** unittest.mock (pytest does not bundle a mocking library; unittest is in stdlib)

**What to Mock:**
- External API calls (if any) — none currently in codebase
- Subprocess/process calls (mocked in `pool.py` tests where needed)
- Time (`unittest.mock.patch("time.time")` when testing timeouts)

**What NOT to Mock:**
- CadQuery/OpenCascade kernel — test the real thing; a mock would only test the mock
- Pydantic validators — test through real `GearParams` construction
- Logging — capture and inspect real log output (see `conftest.py` logger reset, `test_records.py`)

**Dependency Injection Pattern:**

```python

# Override a FastAPI Depends() at test time

app.dependency_overrides[build_backend] = lambda: test_implementation

# Clean up after

app.dependency_overrides.pop(build_backend, None)
```

## Fixtures and Factories

**Composition Data Families (composition.py):**

```python

# Hand-written cross product — never computed from code under test

BORES: dict[str, dict[str, object]]
CUTOUTS: dict[str, dict[str, object]]
RECESSES: dict[str, dict[str, object]]
TIPS: dict[str, dict[str, object]]

# Field presence tables — what `DerivedDimensions` fields are non-null in each family

BORE_FIELDS: dict[str, frozenset[str]]
CUTOUT_FIELDS: dict[str, frozenset[str]]
RECESS_FIELDS: dict[str, frozenset[str]]
TIP_FIELDS: dict[str, frozenset[str]]
```

**Test Data Construction:**

```python

# From composition

p = GearParams.model_validate({**BORES["round"], **CUTOUTS["spokes"]})

# Or direct

p = GearParams(teeth=25, module=2.0, bore_d=12)

# Or with parametrize IDs

@pytest.mark.parametrize(("kw", "expected"), [
    ({"teeth": 19}, "d-flat-both"),
    ({"teeth": 20}, "d-flat-top"),
])
```

**Regression Fixture:**
- `tests/regression/pre_v0_2.json` — recorded parameter sets and their outputs (L05 fixture)
- Regenerated with `make fixture.regen` → `tests/regression/capture.py`
- Used by `test_pre_v0_2.py` to detect silent changes to defaults

## Coverage

**Configuration:** `pyproject.toml` `[tool.coverage.run]`

```toml
branch = true
source = ["src/spur"]

# No fail_under yet: a floor picked without measuring is a number, not a guarantee.

```

**View Coverage:**

```bash
.venv/bin/pytest --cov=src/spur --cov-report=html
```

**Measured Baseline:** See `bench/RESULTS.md`
- No enforced floor (D-23, `docs/tech_debt/active/2026-09-21-no-coverage-floor.md`)
- Measured suite runtime ~11 seconds cold on a 12-core arm64 host (page cache for OpenCascade)

## Pre-Commit Hook

**Gate:** `.pre-commit-config.yaml` (installed with `pre-commit install`)

**Hooks:**
1. `make verify` — Runs ruff, mypy, lint-imports, unfinished-work scan, pytest (pre-commit stage)
   - Passes filenames: false, always_run: true
   - Staged: pre-commit only (not redundant with commit-msg)
2. `no-skip-token` — Rejects GitHub Actions skip tokens in commit message (commit-msg stage)
   - Ensures CI runs for every commit

**Timing:** Warm run ~11 seconds (CAD tests dominate); first run post-`make clean` pages in 1.4 GB OpenCascade, takes a couple of minutes.

## CI/CD

**GitHub Actions (.github/workflows/ci.yml):**

**Jobs (all required green on PR):**

1. **test** (`make verify PYTHON=python`)
   - Runs on ubuntu-latest, Python 3.12 only (L23)
   - Same gate as developer's local `make verify`
   - Required by `tests/test_pr_land.py` (checks `.github/workflows/required-jobs.txt`)

2. **vendor-bundle** (reproducibility check)
   - Builds `web/` JavaScript bundle
   - Compares built bundle against committed `src/spur/static/vendor/`
   - Ensures vendored three.js is reproducible from source

3. **image** (Docker smoke test)
   - Builds Docker image
   - Runs containerized smoke test: `/api/health`, model export (STL, STEP)
   - Validates dependency closure and entrypoint

**Required jobs file:** `.github/workflows/required-jobs.txt`
- Lists job names that must pass before merge
- Kept in sync with `ci.yml`
- Validated by `tests/test_pr_land.py`

## Measured Suite Statistics

(From `bench/RESULTS.md`, 2026-09-23, Machine: 12-core Apple M2 Max, arm64)

**Latency Benchmark (`make bench.latency`):**
- Single scenario (one 200-tooth fine build): idle p95 0.6 ms → under-load p95 0.7-1.2 ms (ratio 1.12x-1.68x, target ≤ 2.0x) ✓
- Concurrent scenario (ten concurrent fine builds): idle p95 0.6-1.0 ms → under-load p95 1.2-2.3 ms (ratio 2.02x-2.45x, target ≤ 2.0x) ✗

**Memory Benchmark** (`make bench.memory`):
- Recorded for N=1 (2052.1 MiB), N=2 (2878.5 MiB), N=3 (3095.8 MiB) worker processes

**Export Cost** (`make bench.export_cost`):
- Gzip compression levels measured; level 1 adopted (smaller CPU cost than level 9)

---

*Testing analysis: 2026-10-02*
