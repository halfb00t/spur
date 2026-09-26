# Phase 8: Hex Bore - Pattern Map

**Mapped:** 2026-09-26
**Files analyzed:** 13 (10 modified, 1 new, 2 confirmed no-change)
**Analogs found:** 13 / 13 (all in-repo; the new bench script leans on three siblings)

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `src/spur/params.py` | model | request-response (validated boundary) | itself — `bore_flat` field (same file, lines 56-57) | exact |
| `src/spur/calc.py` | utility (pure-math) | transform | itself — `bore_radius`/`bore_rim_limit`/`check`/`derive` (same file) | exact |
| `src/spur/model.py` | model (CAD boundary) | transform (kernel build) | itself — `_cut_bore`'s `bore_flat` branch (lines 200-203) | exact |
| `src/spur/static/app.js` | component (form/render) | request-response | itself — `DIMS` array (lines 13-28) | exact |
| `tests/test_model.py` | test | transform (kernel assertions) | itself — `test_each_edge_selector_picks_exactly_its_own_edges` (lines 45-116) | exact |
| `tests/test_calc.py` | test | transform | itself — `test_infeasible_parameters_name_their_fields` (lines 90-100), `test_the_bore_rim_limit_is_the_bore_radius_for_round_and_d_flat_bores` (107-116) | exact |
| `tests/test_api.py` | test | request-response | itself — `test_infeasible_is_422_with_fields` (132-136), `test_every_key_the_ui_reads_is_a_derived_dimensions_field` (104-121) | exact |
| `tests/test_cli.py` | test | request-response | itself — `test_readme_export_examples_run` (76-84), `test_infeasible_parameters_exit_2_and_name_the_problem` (87-91) | exact |
| `bench/build_time.py` | utility (bench script) | batch | `bench/latency.py` (argparse + Markdown report shape) and `bench/corpus.py` (parameter-set generator) | role-match (composite of two siblings) |
| `Makefile` | config | — | `bench.latency` / `bench.memory` targets (lines 112-118) | exact |
| `bench/RESULTS.md` | config (record) | — | "## Regression fixture cost (Phase 7, D-06)" section (lines 364-424+) | exact |
| `README.md` | config (docs) | — | the `bore_flat` bullet/table row/example (lines 11, 107, 150) | exact |
| `src/spur/app.py` / `src/spur/cli.py` | controller | request-response | no change needed — both are schema-generated (see "No Change Needed" below) | n/a |

## Pattern Assignments

### `src/spur/params.py` (model, request-response — validated boundary)

**Analog:** itself, the Bore group (lines 53-62)

**Imports pattern** (lines 1-14): already present, no new imports needed — `_f()` is the one field-builder every scalar field goes through.

**Core field pattern** (lines 56-57, the field to declare after):
```python
bore_flat: float = _f(8.0, 0, 200, title="D-flat", group="Bore", unit="mm", step=0.05,
                      help="Flat to opposite side of the bore. 0 = round bore.")
bore_clearance: float = _f(0.15, 0, 1, title="Bore clearance", group="Bore", unit="mm",
                           step=0.01,
                           help="Added to bore and flat for print shrinkage. 0 for resin/SLS.")
```
`bore_hex` is declared between `bore_flat` and `bore_clearance` per D-07 ("after `bore_flat`"), same `_f()` shape: `bore_hex: float = _f(0.0, 0, 200, title="<D-07 title>", group="Bore", unit="mm", step=0.05, help="<D-08 sentence>")`. `ge=0, le=200` matches `bore_d`/`bore_flat` exactly (D-07 — "one family, one bound").

**Validation/error wiring** (lines 78-88): unchanged — `_feasible` already calls `calc.check(self)` and turns every `(message, fields)` tuple into one `PydanticCustomError`. D-03's two new hex rules need no new plumbing here; they are added inside `calc.check()`.

**Error handling pattern**: none needed in this file — `check()` is the single error-producing function; this file only wires it.

---

### `src/spur/calc.py` (utility, pure-math — no cadquery import, CLAUDE.md boundary)

**Analog:** itself — `bore_radius`, `bore_rim_limit`, `check`, `DerivedDimensions`, `derive`

**Imports pattern** (lines 1-13): unchanged. `TYPE_CHECKING`-gated `from .params import GearParams` stays the only params import; **never add `import cadquery`** — this is the one boundary CLAUDE.md and the import-linter contracts (`pyproject.toml`) enforce.

**Core "additive helper" pattern** (`bore_radius`, lines 57-58 and `bore_rim_limit`'s docstring, lines 61-74):
```python
def bore_radius(p: GearParams) -> float:
    return (p.bore_d + p.bore_clearance) / 2 if p.bore_d > 0 else 0.0

def bore_rim_limit(p: GearParams) -> float:
    """... Phase 8's hex bore adds its circumradius (across-flats over sqrt 3) here
    instead of widening this bound ..."""
    return bore_radius(p)
```
The hex extent is a sibling helper in this same shape — e.g. `_hex_circumradius(p) -> float` returning `(p.bore_hex + p.bore_clearance) / math.sqrt(3)` when `p.bore_hex > 0`, else the round/D-flat path stays `bore_radius(p)`. `bore_rim_limit(p)` becomes `max`/branch between the two per D-01 ("hex replaces the round profile" — it is `if p.bore_hex > 0: hex path else: bore_radius(p)`, not a max of both, since the profiles are mutually exclusive).

**Core "cap or refuse" pattern** (`recess_radii`, lines 77-98; `root_fillet`, lines 114-117): the hub-clearance line to extend for the hex —
```python
hub = r_bore + (p.bore_chamfer if p.bore_d > 0 else 0.0) + MIN_WALL  # clear of the hub wall
```
must become "clear of the corner" when `bore_hex > 0` (Claude's Discretion note: "`recess_radii()` clears the **corner** plus chamfer plus `MIN_WALL`").

**`check()` rule pattern** (lines 132-169), the exact tuple shape every new D-03 rule follows:
```python
r_bore = bore_radius(p)
if p.bore_d > 0 and r_bore > pr.rf - MIN_WALL:
    errors.append(("Bore is too large for the root diameter.", ("bore_d",)))
if p.bore_chamfer > 0 and p.bore_chamfer >= p.face_width / 2:
    errors.append(("Bore chamfer must be less than half the face width.",
                   ("bore_chamfer",)))
```
D-03(a) "corner vs. root" and D-03(b) "chamfer vs. side" are two more `errors.append((f"<message naming the field(s)>", ("bore_hex",)))` / `(..., ("bore_chamfer", "bore_hex"))` lines, gated behind `if p.bore_hex > 0:` and placed so the round-profile checks (`bore_d`, `bore_flat` — lines 154-158) are skipped entirely when the hex is active (D-03: "the round-profile checks do not run").

**Warning pattern** (D-02, `derive()`'s warning-building idiom, lines 264-287):
```python
if tip < MIN_TIP_FDM:
    warnings.append(f"Tip is only {tip:.2f} mm wide; FDM needs about {MIN_TIP_FDM} mm.")
```
One `if p.bore_hex > 0:` block builds the D-02 sentence, naming only the non-zero ignored fields with their values (mirrors the `f"Recess narrowed to {rr[1] - rr[0]:.2f} mm..."` value-in-sentence convention at line 281).

**`DerivedDimensions` field pattern** (lines 215-217, `bore_effective`):
```python
bore_effective: float | None = Field(
    description="Bore diameter including print clearance; null with no bore.",
    json_schema_extra={"unit": "mm"})
```
Two new `float | None` fields follow this exact shape (D-05): description states what calipers read and says "null when `bore_hex == 0`"/"null with no hex bore".

**`derive()` construction pattern** (`r3()` idiom and `x if cond else None`, lines 299-322):
```python
bore_effective=r3(2 * bore_radius(p)) if p.bore_d > 0 else None,
```
The two new fields are `r3(<effective across-flats or corner-to-corner>) if p.bore_hex > 0 else None`; `bore_effective` itself changes to `r3(2 * bore_radius(p)) if p.bore_d > 0 and p.bore_hex == 0 else None` per D-04 ("`bore_effective` is `null` on a hex bore").

**Error handling pattern**: `check()` returns a list of tuples, never raises — the raise happens once, in `params.py`'s `_feasible`. New hex rules follow the same non-raising, tuple-returning contract.

---

### `src/spur/model.py` (model/CAD boundary — cadquery objects never escape this file)

**Analog:** itself — `_cut_bore`'s `bore_flat` branch (lines 194-208)

**Imports pattern** (lines 30-41): add `bore_hex`'s calc-side helper (whatever name Discretion picks, e.g. alongside `bore_radius, bore_rim_limit`) to the existing `from .calc import (...)` block — same alphabetized-ish list, no new top-level import needed since `cq` is already imported.

**Core "second profile" pattern** (lines 194-208, the exact branch to add a sibling to):
```python
def _cut_bore(solid: cq.Shape, p: GearParams) -> cq.Shape:
    """Round or D-shaped bore, chamfered on both rims."""
    if p.bore_d <= 0:
        return solid
    r_bore = bore_radius(p)
    hole = cq.Workplane("XY").circle(r_bore).extrude(p.face_width)
    if p.bore_flat > 0:
        flat = p.bore_flat + p.bore_clearance          # flat to opposite side
        keep = cq.Workplane("XY").center(flat - 2 * r_bore, 0).rect(2 * r_bore, 2 * r_bore + 2)
        hole = hole.intersect(keep.extrude(p.face_width))
    solid = solid.cut(hole.val())  # type: ignore[arg-type]  # .val() is typed as a 4-way union
    if p.bore_chamfer > 0:
        solid = solid.chamfer(
            p.bore_chamfer, None, _bore_rim_edges(solid, p))
    return solid
```
Per D-01/spec item 2, the hex is a **replacement branch**, not an `intersect` on top of the round hole: `if p.bore_hex > 0:` builds `hole = cq.Workplane("XY").polygon(6, effective_af, circumscribed=True).extrude(p.face_width)` instead of the circle+intersect path, then falls through to the same `solid.cut(hole.val())` / chamfer tail unchanged. One comment states the flat-faces-+X orientation (Claude's Discretion — "flat facing +X ... a vertex on ±Y").

**`_bore_rim_edges` selector — no change needed** (lines 241-269): confirmed by CONTEXT code_context — it already accepts any straight/curved edge within `bore_rim_limit(p) + BORE_RIM_SLACK` of the axis with no `geomType()` filter, so once `calc.bore_rim_limit` returns the hex circumradius the twelve `LINE` edges are selected with zero changes here.

**Error handling pattern** (lines 264-269, the D-15 zero-edge guard — copy verbatim, no new instance needed): the existing `if not edges: raise BuildError(...)` in `_bore_rim_edges` already covers the hex case; Phase 7's `test_a_bore_chamfer_that_selects_no_rim_edges_is_a_build_error_not_a_bare_bore` (`tests/test_model.py` lines 128-138) is the direct analog for a hex-specific regression test if the planner wants one, but no new guard code is required.

---

### `src/spur/static/app.js` (component, request-response — schema-driven form)

**Analog:** itself — `DIMS` array (lines 13-28)

**Core pattern** (lines 13-28, the exact two-line-per-field shape D-06 copies):
```javascript
const DIMS = [
  ['pitch_d', 'Pitch Ø'],
  ...
  ['bore_effective', 'Bore Ø incl. clearance'],
  ['recess_id', 'Recess inner Ø'],
  ...
];
```
Two new rows: `['<effective-af-field>', 'Hex across flats incl. clearance']` and `['<corner-to-corner-field>', 'Hex across corners']` (D-06 label wording), inserted anywhere in the array — order is display order only, not wired to anything else.

**Render/null-skip pattern** (lines 124-142, `renderInfo`):
```javascript
for (const [key, label] of DIMS) {
    const v = info[key];
    if (v === null || v === undefined) continue;
    ...
}
```
Already generic — the two new keys are skipped automatically when `null` (hex off); no changes needed beyond the `DIMS` array itself.

**Form generation — no change needed** (`buildForm`, lines 35-82) and **query building — no change needed** (`gearQuery`, lines 92-98): both iterate `schema.properties`/`fields` generically, so `bore_hex` gets a form field and only rides the URL when non-default, purely from `params.py`'s field declaration (D-09: "no conditional form behaviour").

---

### `tests/test_model.py` (test, transform — kernel assertions)

**Analog:** itself — the parametrized matrix (lines 45-64) and per-row assertions (65-116)

**Core matrix-row pattern** (lines 51-64):
```python
pytest.param({"bore_flat": 0}, collections.Counter({"CIRCLE": 2}), 4, id="round-both"),
pytest.param({"bore_flat": 0, "recess_sides": "top"}, collections.Counter({"CIRCLE": 2}), 2,
             id="round-top"),
```
Hex rows follow the same three-tuple shape: `pytest.param({"bore_hex": <af>}, collections.Counter({"LINE": 12}), 4, id="hex-both")` etc. across `recess_sides ∈ {both, top, bottom, none}` (Claude's Discretion — "expecting `Counter({"LINE": 12})`").

**`test_builds_one_valid_solid` pattern** (lines 26-45): one more `{"bore_hex": <value>, ...}` entry in the `kw` parametrize list, same `assert s.isValid()` / bounding-box shape.

**Solid-measurement pattern to write new** (Discretion — "measuring the built solid, not only `derive()`"): closest existing analog is `test_recess_removes_expected_volume` (lines 154-160, reads real kernel output and compares to the `calc.py` formula) — read the rim-edge vertices' `math.hypot(x, y)` for radius and flat-to-flat distance, compare to `corner-to-corner/2` and the effective across-flats within `TOL` (imported at line 12).

**Error handling / zero-edge guard pattern** (lines 118-138): `test_a_bore_chamfer_that_selects_no_rim_edges_is_a_build_error_not_a_bare_bore` is the template if a hex-specific zero-edge regression is added; uses `monkeypatch.setattr("spur.model.bore_rim_limit", ...)` and `pytest.raises(BuildError, match=...)`.

---

### `tests/test_calc.py` (test, transform)

**Analog:** itself — `test_infeasible_parameters_name_their_fields` (90-100) and `test_the_bore_rim_limit_is_the_bore_radius_for_round_and_d_flat_bores` (107-116)

**422-naming-fields pattern** (lines 90-100):
```python
@pytest.mark.parametrize(("kw", "field"), [
    ({"bore_flat": 3}, "bore_flat"),
    ...
])
def test_infeasible_parameters_name_their_fields(kw, field):
    with pytest.raises(ValidationError) as exc:
        GearParams.model_validate(kw)
    err = exc.value.errors()[0]
    assert err["type"] == "infeasible"
    assert field in err["ctx"]["fields"]
```
D-03(a)/(b) each get one row here (a hex too large for the root; a hex whose side can't carry the requested chamfer, asserting both `bore_chamfer` and `bore_hex` land in `ctx["fields"]`).

**Bound-measurement unit-test pattern** (lines 107-116, the direct analog for D-05's two new fields and D-03's measured bound):
```python
def test_the_bore_rim_limit_is_the_bore_radius_for_round_and_d_flat_bores() -> None:
    for p in (GearParams(bore_flat=0), GearParams(), GearParams(bore_d=0)):
        assert bore_rim_limit(p) == bore_radius(p)
    assert bore_rim_limit(GearParams(bore_flat=0)) == pytest.approx(4.575)
```
A hex sibling: `bore_rim_limit(GearParams(bore_hex=6)) == pytest.approx(6.15 / math.sqrt(3))` (worked example in CONTEXT specifics: corner-to-corner 7.101 mm → circumradius 3.5505 mm), plus D-05's `derive()` values against the same worked numbers (effective across-flats 6.15, corner-to-corner 7.101).

**D-02 warning-text pattern** (`test_root_fillet_is_capped_with_a_warning`, lines 82-85; `test_oversized_recess_is_narrowed_to_fit_and_says_so`, lines 128-138):
```python
def test_root_fillet_is_capped_with_a_warning() -> None:
    d = derive(GearParams(teeth=80, module=0.5, bore_d=5, bore_flat=0))
    assert d.root_fillet < 0.5
    assert any("Root fillet reduced" in w for w in d.warnings)
```
D-02's test: `derive(GearParams(bore_hex=6))` → `any("ignored" in w for w in d.warnings)`, and a `bore_flat=0` case asserting only `bore_d` is named (no warning when both round fields are zero).

---

### `tests/test_api.py` (test, request-response)

**Analog:** itself — `test_infeasible_is_422_with_fields` (132-136) and `test_every_key_the_ui_reads_is_a_derived_dimensions_field` (104-121)

**422-shape pattern** (lines 132-136):
```python
def test_infeasible_is_422_with_fields() -> None:
    r = client.get("/api/info", params={"bore_flat": 3})
    assert r.status_code == 422
    detail = r.json()["detail"][0]
    assert "D-flat" in detail["msg"]
    assert detail["ctx"]["fields"] == ["bore_flat"]
```
D-03's two refusals get the same shape over `/api/info?bore_hex=...`.

**DIMS-subset guard — already covers new fields with zero changes** (lines 104-121): `dims_keys` is re-derived from `app.js`'s live `DIMS` array and checked `<= model_fields`; adding the two `DIMS` rows in `app.js` and the two `DerivedDimensions` fields in `calc.py` keeps this test green automatically — no edit needed here unless the `len(dims_keys) >= 15` floor should be bumped (cosmetic, optional).

**Hex-builds pattern to add**: `test_info_reports_the_mate` (lines 124-127) is the template for a plain successful `client.get("/api/info", params={"bore_hex": 6})` assertion (`bore_effective is None`, the two new fields present and numeric).

---

### `tests/test_cli.py` (test, request-response)

**Analog:** itself — `test_readme_export_examples_run` (76-84) and `test_infeasible_parameters_exit_2_and_name_the_problem` (87-91)

**Interface-parity export pattern** (lines 76-84):
```python
def test_readme_export_examples_run(tmp_path, capsys) -> None:
    step = tmp_path / "gear.step"
    cli.main(["export", "-o", str(step)])
    assert step.read_bytes().startswith(b"ISO-10303-21;")

    stl = tmp_path / "gear.stl"
    cli.main(["export", "-o", str(stl), "--teeth", "24", "--module", "1",
              "--pressure-angle", "20", "--bore-flat", "0"])
    assert stl.stat().st_size > 1000
    assert "Recess narrowed" in capsys.readouterr().err
```
D-10's new README example (`spur export … --bore-hex 6`) gets its own `cli.main([..., "--bore-hex", "6"])` assertion here, mirroring this shape exactly (CLI flags are schema-generated per `cli.py` lines 39-52, so `--bore-hex` needs no code change, only the test).

**422-on-CLI pattern** (lines 87-91):
```python
def test_infeasible_parameters_exit_2_and_name_the_problem(capsys) -> None:
    with pytest.raises(SystemExit) as exc:
        cli.main(["info", "--bore-flat", "3"])
    assert exc.value.code == 2
    assert "D-flat" in capsys.readouterr().err
```
Template for asserting D-03's refusal sentence surfaces through the CLI too (same `calc.check()` source, so this is largely a parity confirmation, not new logic).

---

### `bench/build_time.py` (new file — utility, batch)

**Analogs:** `bench/latency.py` (argparse entrypoint + Markdown report string) and `bench/corpus.py` (parameter-set generator); `bench/__init__.py`'s `machine_facts()`.

**Module docstring pattern** (`bench/corpus.py` lines 1-12, `bench/latency.py` lines 1-12): state what it measures, why it is not in `make verify` (D-16's existing reasoning: needs minutes, not shared-hardware-flaky here — the real reason for `build_time.py` is per-row timing, not load-flakiness, so state that honestly), and how to run it (`make bench.build`).

**Imports pattern** (`bench/latency.py` lines 14-26):
```python
from __future__ import annotations
import argparse
import statistics  # not needed here — this is a small parametrized sweep, not a percentile harness
import sys
import time
from dataclasses import dataclass
from bench import machine_facts
```
`build_time.py` additionally imports directly from `spur` (in-process, no HTTP — unlike `latency.py`/`memory.py` which drive a running server/container, this sweep times `spur.model.build`/`export` directly): `from spur.model import build, export, _build_cached` and `from spur.params import GearParams`.

**Parameter-set generator pattern** (`bench/corpus.py` lines 17-26):
```python
def corpus() -> list[dict[str, object]]:
    return [{"teeth": teeth} for teeth in range(160, 200)]
```
D-11's 8-row sweep (`bore_hex ∈ {200, 12.7} × recess_sides ∈ {both, none} × bore_chamfer ∈ {0.4, max}` at `teeth=200`) is a same-shaped list-of-dicts function, e.g. `def sweep_rows() -> list[dict[str, object]]`.

**Timing + cache-clearing pattern**: no direct analog exists (both `latency.py`/`memory.py` measure over HTTP/containers). Nearest in-repo precedent for "clear the cache between rows" is `model._build_cached` itself being an `lru_cache` (`src/spur/model.py` line 296) — call `model._build_cached.cache_clear()` before each row's `time.perf_counter()` bracket (D-11: "solid cache cleared between rows"), following `bench/latency.py`'s `t0 = time.perf_counter(); ...; time.perf_counter() - t0` idiom (lines 64-66, 96-102).

**Markdown report pattern** (`bench/latency.py`'s `_report_markdown`, lines 168-184):
```python
def _report_markdown(name, idle_p95, idle_n, load_p95, load_n, slowest_build, attempted,
                     refused) -> str:
    return (
        f"## Latency: {name}\n\n"
        f"- Machine: {machine_facts()}\n"
        ...
    )
```
`build_time.py`'s report follows the "## <section>\n\n- Machine: {machine_facts()}\n" header shape, then a Markdown table (one row per sweep configuration, columns build/fine-STL/STEP wall time), matching `bench/RESULTS.md`'s "Regression fixture cost" table shape (see below) rather than `latency.py`'s prose-plus-ratio shape — the planner picks whichever of the two committed shapes fits a per-row table better (RESULTS.md's is table-based and is the shape D-11 explicitly asks to copy).

**CLI entrypoint pattern** (`bench/latency.py` lines 200-223):
```python
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="bench.latency", description="...")
    ...
    return 0 if all(results) else 1

if __name__ == "__main__":
    sys.exit(main())
```
Copy verbatim shape; `build_time.py` likely needs no `argv` scenario selector at all (D-12 — "takes parameter sets, times build/STL/STEP per set, prints the Markdown table") — a bare `main() -> int` that runs the fixed sweep and returns 0 is the simplest fit (CLAUDE.md — "simplest solution that actually works").

**Timeout guard** (D-11: "every row must sit inside `SPUR_BUILD_TIMEOUT=30s`; a row that does not is a halt for a human decision"): no direct analog in `bench/` — nearest precedent is `bench/latency.py`'s `_p95_or_warn` refuse-rather-than-guess pattern (lines 155-165: warn to stderr and return `None`/skip rather than print a number that isn't real) — a row exceeding the timeout should warn and halt (`sys.exit` or a non-zero return), not print a number, mirroring L08's contract that this whole codebase already applies to `bench/latency.py`.

---

### `Makefile` (config)

**Analog:** `bench.latency` / `bench.memory` targets (lines 112-118) and the `bench:` umbrella (line 112), and `.PHONY`/help-line conventions (lines 19-21, 23).

**Core pattern** (lines 112-118):
```makefile
bench: bench.latency bench.memory  ## everything this phase's success criteria need

bench.latency: $(STAMP)  ## /api/health under load, on the host -- run `make serve` first (D-17)
	$(PY) -m bench.latency

bench.memory: $(STAMP)  ## container memory sweep over the 40-gear corpus; manages its own containers
	$(PY) -m bench.memory sweep
```
New target: `bench.build: $(STAMP)  ## <D-12's help text — the 8-row hex-bore sweep at 200 teeth>` running `$(PY) -m bench.build_time`; `bench: bench.latency bench.memory bench.build` extends the umbrella; `.PHONY` line 21's list (`bench bench.latency bench.memory`) gains `bench.build`.

**Directory-list pattern to extend**: `typecheck` (line 54, `$(PY) -m mypy src tests docker bench scripts`) already covers the whole `bench` package, so `bench/build_time.py` needs no `Makefile` change there — CONTEXT's "it joins `make typecheck`'s scope (`bench` already is) and ruff's" is already true by construction (ruff runs `ruff check .` at line 47, also already whole-repo).

---

### `bench/RESULTS.md` (config, record)

**Analog:** "## Regression fixture cost (Phase 7, D-06)" section (lines 364-424+)

**Section shape to copy exactly**:
```markdown
## Regression fixture cost (Phase 7, D-06)

The committed measurement record for ... (D-06). ...

### Host state

- CPU: Apple M2 Max, 12 cores
- RAM: 32.0 GiB
- Python: 3.12.13 (`.venv`)
- Date: 2026-09-26, ~12:20-12:26 UTC
- HEAD: `<sha>` (`<commit subject>`)
- `uptime` load averages at the start of this session: ... — above/below this project's
  usual "quiet" bar ...; the numbers below carry that caveat rather than being presented
  as clean (L08).

### <sweep description>

| ... | ... | ... |
|---|---|---|
| ... |

**<named heaviest row>**
```
A new "## Hex bore heaviest configuration (Phase 8, D-11)" section follows this exact skeleton: intro sentence citing D-11 and the requirement, a "### Host state" block with the same five bullets plus the load-average caveat sentence verbatim in shape, then the 8-row table (columns: `bore_hex`, `recess_sides`, `bore_chamfer`, build time, fine-STL time, STEP time), and a closing sentence naming the heaviest row explicitly (mirrors line 406's "**Decision: ...**" bolded-lead-in convention, here "**Heaviest: ...**").

---

### `README.md` (config, docs)

**Analog:** the `bore_flat`/D-flat lines this phase's edits sit beside.

**Feature bullet pattern** (line 11):
```markdown
- Backlash, root fillets, D-flat or round bore with print clearance and chamfer
```
→ gains ", or hex bore" (D-10) in the same sentence shape, no new bullet.

**Parameter table row pattern** (lines 149-152):
```markdown
| `bore_d` | 9 | Round part of the bore. 0 = no bore |
| `bore_flat` | 8 | Flat to opposite side of the bore. 0 = round bore |
```
New row `| `bore_hex` | 0 | <D-08's help sentence, trimmed to table width> |` inserted after the `bore_flat` row (matches field declaration order in `params.py`, D-07).

**Example pattern** (line 107):
```sh
spur export -o gear.stl --teeth 24 --module 1 --pressure-angle 20 --bore-flat 0
```
New example line in the same code block, e.g. `spur export -o gear.step --teeth 24 --bore-hex 6` (D-10's own example, "post-v0.2 set... stays out of the regression corpus" — `tests/test_cli.py`'s `test_readme_export_examples_run` is the test that exercises whichever example is added, per that test's pattern above).

---

## Shared Patterns

### The `check()` tuple contract (calc.py)
**Source:** `src/spur/calc.py` lines 132-169, `("message naming the field(s)", ("field", ...))`
**Apply to:** every new D-03 refusal rule; `params.py`'s `_feasible` (lines 78-88) turns the list into one `PydanticCustomError` with `ctx.fields` sorted and deduplicated — new rules need no changes there, only new `errors.append(...)` lines in `check()`.

### Cap-and-warn vs. refuse (L03/L08)
**Source:** `recess_radii()`/`root_fillet()` (cap silently, warn in `derive()`) vs. `check()` (refuse, name the fields) — `src/spur/calc.py` lines 77-169.
**Apply to:** D-01/D-02 (bore_d/bore_flat ignored → cap-and-warn, `derive()`'s warning-list idiom) and D-03 (corner-vs-root, chamfer-vs-side → refuse, `check()`'s tuple idiom). Every hex case in this phase sorts into exactly one of these two functions, never a third path.

### `r3()` / rounded-once-at-construction (D-10, Phase 4)
**Source:** `derive()`'s `r3()` closure, `src/spur/calc.py` lines 299-300, applied to every `DerivedDimensions` field at construction.
**Apply to:** the two new D-05 fields — round with `r3()` at the same call site, not inside a helper.

### Schema-driven interfaces need no per-field wiring (L02)
**Source:** `src/spur/cli.py` `_add_gear_args` (lines 39-52, generates a flag per `GearParams.model_fields`); `src/spur/static/app.js` `buildForm` (lines 35-82, generates a form field per `schema.properties`); `src/spur/app.py` `_gear()` (lines 220-227, strips per-endpoint extras back to `GearParams`).
**Apply to:** confirms `bore_hex` needs zero changes in `cli.py` and `app.py` — declaring it in `params.py` is sufficient for the CLI flag, the `/api/schema` entry and the form field. Only the two files that carry *new derived output* (`calc.py`'s `DerivedDimensions`/`derive()` and `app.js`'s `DIMS`) need edits beyond `params.py` and `model.py`.

### Zero-edge selector guard (07 D-15, L26)
**Source:** `src/spur/model.py` `_bore_rim_edges` (lines 264-269) and `_groove_floor_edges` (lines 233-238), each `if not edges: raise BuildError(...)`.
**Apply to:** already covers the hex automatically — no new guard code — but is the pattern behind `test_a_bore_chamfer_that_selects_no_rim_edges_is_a_build_error_not_a_bare_bore` (`tests/test_model.py` 118-138) if the planner adds a hex-specific zero-edge regression test.

### Fixture-immutability guard (07 D-03, L26)
**Source:** `tests/regression/pre_v0_2.json`, `tests/regression/test_pre_v0_2.py`, `tests/regression/corpus.py` (closed set, never touched by a feature commit).
**Apply to:** every task in this phase — `git diff --exit-code tests/regression/pre_v0_2.json` must pass after each one; this phase never edits `tests/regression/` at all (no row in the classification table above touches it).

### Measured-not-assumed constants carry their measurement in a comment (L17/L19/L24/L26)
**Source:** `src/spur/model.py`'s `BORE_RIM_SLACK` comment (lines 50-55) and `bench/RESULTS.md`'s "Regression fixture cost" section (lines 364-424).
**Apply to:** D-03's measured chamfer-vs-side bound (wherever it lands as a constant or inline check in `calc.py`) and D-11's sweep numbers in `bench/RESULTS.md` — both need the same "how it was measured, on what, when" comment shape.

## No Analog Found

None — every file this phase touches has an exact or role-match analog in the current tree (the codebase already shipped one full "additive bore feature" cycle in `bore_flat`, which this phase's hex bore mirrors end-to-end).

## Metadata

**Analog search scope:** `src/spur/`, `tests/`, `bench/`, `Makefile`, `README.md`, `docs/architecture/decision_log.md` (read-only, for L26 precedent).
**Files scanned:** `src/spur/params.py`, `src/spur/calc.py`, `src/spur/model.py`, `src/spur/app.py`, `src/spur/cli.py`, `src/spur/static/app.js`, `tests/test_model.py`, `tests/test_calc.py`, `tests/test_api.py`, `tests/test_cli.py`, `bench/__init__.py`, `bench/latency.py`, `bench/memory.py`, `bench/corpus.py`, `bench/RESULTS.md`, `Makefile`, `README.md`, `docs/architecture/decision_log.md` (L26 section).
**Pattern extraction date:** 2026-09-26
**Tracked-source gate:** all 20 files above confirmed via `git ls-files` (see command output in the mapping session) — no gitignored mirror paths involved.
