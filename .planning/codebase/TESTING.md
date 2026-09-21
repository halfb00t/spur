---
last_mapped_commit: 5252bdcd6a11f893246f614da8e5f0d431d1ed2a
last_mapped_at: 2026-09-21
---
# Testing Patterns

**Analysis Date:** 2026-09-21

## Test Framework

**Runner:**

- pytest 8+ (`pytest>=8` in `pyproject.toml`)
- Config: `pyproject.toml`, `[tool.pytest.ini_options]`

**Assertion Library:**

- pytest built-in (`assert` statements)
- pytest.approx for floating-point: `assert d["pitch_d"] == pytest.approx(33.25)`

**Run Commands:**

```bash
make test              # Run the full test suite (requires venv)
pytest                 # Direct invocation with python -m pytest
pytest -k test_name    # Run specific test by name pattern
pytest -v             # Verbose output
pytest --tb=short     # Short traceback format
```

**Coverage:**

```bash
coverage run -m pytest    # Run with coverage measurement
coverage report           # Show coverage report
coverage html            # Generate HTML report to htmlcov/index.html
```

Configuration (in `pyproject.toml`):

```toml
[tool.coverage.run]
branch = true
source = ["src/spur"]

# No fail_under yet: a floor picked without measuring is a number, not a guarantee.

# See docs/tech_debt/active/2026-09-21-no-coverage-floor.md.

```

## Test File Organization

**Location:**

- `tests/` directory, co-located with source tree
- Test files parallel source structure: `src/spur/*.py` → `tests/test_*.py`

**Naming:**

- Test files: `test_*.py` (pytest convention)
- Test functions: `test_<what_it_verifies>` reading as a requirement
  - Good: `test_tooth_thickness_and_gap_are_measured_on_the_same_circle()`
  - Bad: `test_tooth_1()`, `test_fix_123()`
- Regression tests: name after property, not bug number
  - Good: `test_oversized_recess_is_narrowed_to_fit_and_says_so()`
  - Bad: `test_issue_456()`

**Directory Structure:**

```
tests/
├── test_calc.py         # Pure math, ~176 lines, 100+ assertions
├── test_model.py        # CAD kernel integration, ~92 lines
├── test_api.py          # HTTP contract, ~99 lines
└── test_cli.py          # Command-line interface, ~41 lines
```

## Test Structure

**Suite Organization - Unit Tests (Pure Math):**

File: `tests/test_calc.py`

```python
def test_default_dimensions() -> None:
    d = derive(GearParams())
    assert d["pitch_d"] == pytest.approx(33.25)
    assert d["tip_d"] == pytest.approx(36.75)
    # ...
```

**Characteristics:**

- No setup/teardown needed (pure functions)
- No mocking; test against real math directly
- Parametrized with `@pytest.mark.parametrize` for coverage:
  ```python
  @pytest.mark.parametrize(("m", "pa", "k", "w"), [
      (1.75, 20, 3, 13.381),
      (1.75, 25, 3, 13.360),
  ])
  def test_span_measurement(m: float, pa: float, k: int, w: float) -> None:
      p = GearParams(module=m, pressure_angle=pa, ...)
      kk, ww = span_measurement(p)
      assert kk == k
  ```

**Suite Organization - Integration Tests (CAD Kernel):**

File: `tests/test_model.py`

```python
def test_builds_one_valid_solid(kw: dict[str, Any]) -> None:
    p = GearParams(**kw)
    s = build(p)
    assert s.isValid()
    bb = s.BoundingBox()
    assert bb.zlen == pytest.approx(p.face_width)
```

**Characteristics:**

- **Do NOT mock OpenCascade**; a mock would test the mock
- Assert geometry properties, not snapshots: volume, topology (isValid), bounding box, mesh watertightness
- Example watertightness check in `test_exported_stl_is_a_closed_consistently_oriented_shell()`:
  ```python
  def vertex(p: Sequence[float]) -> tuple[int, ...]:
      return tuple(round(c * 1e5) for c in p)
  
  directed: collections.Counter[...] = collections.Counter()
  for a, b, c in _stl_triangles(export(GearParams(), "stl", "preview")):
      directed.update([(ka, kb), (kb, kc), (kc, ka)])
  
  assert all(n == 1 for n in directed.values()), "an edge is used twice"
  assert all((v, u) in directed for u, v in directed), "edge has no opposite"
  ```

**Suite Organization - Contract Tests (HTTP API):**

File: `tests/test_api.py`

```python
from fastapi.testclient import TestClient
from spur.app import app

client = TestClient(app)

def test_schema_drives_the_form() -> None:
    props = client.get("/api/schema").json()["properties"]
    assert props["teeth"]["group"] == "Teeth"
    assert props["module"]["unit"] == "mm"
```

**Characteristics:**

- Use `TestClient` from fastapi; no server spawning
- Test error shapes that the UI parses:
  ```python
  def test_infeasible_is_422_with_fields() -> None:
      r = client.get("/api/info", params={"bore_flat": 3})
      assert r.status_code == 422
      detail = r.json()["detail"][0]
      assert "D-flat" in detail["msg"]
      assert detail["ctx"]["fields"] == ["bore_flat"]
  ```
- Test admission control (queue saturation):
  ```python
  def test_a_saturated_service_refuses_instead_of_queueing() -> None:
      held = [app_module.BUILD_QUEUE.acquire(blocking=False)
              for _ in range(app_module.MAX_QUEUED_BUILDS)]
      try:
          r = client.get("/api/model.stl", params={"quality": "preview"})
          assert r.status_code == 503
          assert r.headers["retry-after"] == "5"
  ```

**Suite Organization - CLI Tests:**

File: `tests/test_cli.py`

```python
def test_info_reports_the_mate_it_was_asked_about(
        capsys: pytest.CaptureFixture[str]) -> None:
    cli.main(["info", "--teeth", "19", "--mate-teeth", "40"])
    out = json.loads(capsys.readouterr().out)
    assert out["mate_teeth"] == 40
    assert out["centre_distance"] == pytest.approx(51.625)
```

**Characteristics:**

- The README's own commands are tests: `test_readme_export_examples_run()`
- Capture stdout/stderr with `capsys` fixture
- Test actual CLI invocation via `cli.main(["cmd", "args"])`
- Verify exit codes: `pytest.raises(SystemExit)`

## Mocking

**Framework:** pytest mocking, not used for external dependencies; focused on testing real behavior

**Do NOT Mock:**

- OpenCascade/CadQuery: would test the mock, not the kernel
- Network services (if any were added)

**Example of What Is Tested Directly:**

```python
def test_recess_removes_expected_volume() -> None:
    solid = build(GearParams(recess_sides="none", recess_fillet=0)).Volume()
    # ...
    ring = math.pi * (r_out ** 2 - r_in ** 2) * p.recess_depth * 2
    assert solid - build(p).Volume() == pytest.approx(ring, rel=1e-3)
```

**What NOT to Test:**

- Private implementation details or internal call counts
- Snapshot/golden-file comparisons for geometry (too brittle; test properties instead)

## Fixtures and Factories

**Test Data:**

- Use `GearParams()` directly in tests; it is hashable and frozen (immutable)
- Parametrization over dedicated fixtures when testing combinations:
  ```python
  @pytest.mark.parametrize(("kw", "field"), [
      ({"bore_flat": 3}, "bore_flat"),
      ({"recess_depth": 3.6}, "recess_depth"),
  ])
  def test_infeasible_parameters_name_their_fields(kw, field):
      with pytest.raises(ValidationError) as exc:
          GearParams(**kw)
      err = exc.value.errors()[0]
      assert field in err["ctx"]["fields"]
  ```

**Location:**

- No shared fixture file (`conftest.py`); each test file is self-contained
- Reuse `GearParams` defaults or construct inline

**Fixture Markers:**

- Test argument names read as requirements: `capsys` for capturing stdout, `tmp_path` for temp files (built-in pytest)

## Coverage

**Requirements:** Coverage is configured but no floor enforced yet

Configuration (`pyproject.toml`):

```toml
[tool.coverage.run]
branch = true
source = ["src/spur"]

# No fail_under yet: docs/tech_debt/active/2026-09-21-no-coverage-floor.md

```

**View Coverage:**

```bash
make test           # Runs pytest; capture coverage with: pytest --cov=src.spur --cov-report=html
pytest --cov=src.spur --cov-report=html
open htmlcov/index.html
```

**Coverage Gaps:**

- Not currently enforced via CI
- Tracked gap: `docs/tech_debt/active/2026-09-21-no-coverage-floor.md` (fix pending decision on floor value)

## Test Types

**Unit Tests — Pure Math (`test_calc.py`):**

- Scope: `calc.py` functions (`derive()`, `centre_distance()`, `span_measurement()`, etc.)
- Speed: All 100+ assertions complete in < 1s
- Approach: Exhaustive on the rules; test names read as requirements
- No mocking; pure functions with no side effects
- Assertions use `pytest.approx()` for floating-point tolerance

**Integration Tests — CAD Kernel (`test_model.py`):**

- Scope: `model.py` functions (`build()`, `export()`)
- Assert geometry properties: volume, topology (valid solid), bounding box, mesh watertightness
- Do NOT mock OpenCascade
- Example: test that exported STL is watertight (every edge has exactly one opposite, consistent orientation)

**Contract Tests — HTTP API (`test_api.py`):**

- Scope: All endpoints through `TestClient`
- Assert response codes, error shapes, header values
- Test admission control (queue saturation → 503)
- Test edge cases: impossible mesh pairs, undersized gears, saturated queue

**CLI Tests (`test_cli.py`):**

- Scope: Command-line interface via `cli.main()`
- Verify documented examples run: README commands are tests
- Test error exit codes and stderr messages
- Example: `test_readme_export_examples_run()` exports both STL and STEP formats

## Common Patterns

**Async Testing:**

- Not used; project is synchronous (no async/await)

**Error Testing:**

```python
def test_infeasible_parameters_name_their_fields(
        kw: dict[str, Any], field: str) -> None:
    with pytest.raises(ValidationError) as exc:
        GearParams(**kw)
    err = exc.value.errors()[0]
    assert err["type"] == "infeasible"
    assert field in err["ctx"]["fields"]
```

**Parametrization:**

```python
@pytest.mark.parametrize(("m", "pa", "k", "w"), [
    (1.75, 20, 3, 13.381),
    (1.75, 25, 3, 13.360),
])
def test_span_measurement(m: float, pa: float, k: int, w: float) -> None:
    p = GearParams(module=m, pressure_angle=pa, bore_d=0, recess_sides="none")
    kk, ww = span_measurement(p)
    assert kk == k
```

**Floating-Point Assertions:**

```python
assert d["pitch_d"] == pytest.approx(33.25)           # absolute tolerance default
assert shifted > 1.75 * 59 / 2                         # exact comparison where exact
assert got == pytest.approx(expected, rel=1e-12)      # relative tolerance
assert ww == pytest.approx(w, abs=2e-3)               # absolute tolerance explicit
```

**Capture Output:**

```python
def test_readme_export_examples_run(tmp_path, capsys):
    stl = tmp_path / "gear.stl"
    cli.main(["export", "-o", str(stl), ...])
    assert "Recess narrowed" in capsys.readouterr().err  # stderr capture
```

## Verification Gate

The `make verify` command (defined in `Makefile:47`) runs all these checks in sequence:

```bash
make verify                # The gate all changes must pass
```

Runs:

1. **`make lint`** — `ruff check .` (correctness rules, no reformatting)
2. **`make typecheck`** — `mypy src tests docker` (strict mode comes from `strict = true` in `[tool.mypy]` in `pyproject.toml`, not a CLI flag)
3. **`make lint-imports`** — `lint-imports` (import boundary contracts from `pyproject.toml`)
4. **`make no-fake-done`** — Scan for `TODO|FIXME|XXX|HACK|NotImplementedError` markers (unfinished work)
5. **`make test`** — `pytest $(PYTEST_ARGS)` (full test suite)

**Additional checks in `make check` (needs Docker):**

- `make smoke` — Exercise kernel, exporters, and ASGI app inside the container (`docker/smoke.py`)
- `make vendor-check` — Verify committed three.js bundle matches web/ build output

---

*Testing analysis: 2026-09-21*
