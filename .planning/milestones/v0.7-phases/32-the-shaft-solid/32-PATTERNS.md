# Phase 32: The Shaft Solid - Pattern Map

**Mapped:** 2026-10-27
**Files analyzed:** 15 new/modified
**Analogs found:** 14 / 15 (all analog paths verified git-tracked)

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `src/spur/shaft_model.py` (fill) | kernel builder | transform (params -> solid) | `src/spur/model.py` (`_outline`, `_build`, guards) | exact (role), no shared code |
| `src/spur/model.py` (dispatch, Part typing) | kernel doorway | request-response | itself, `_build`/`_build_checked`/`_write_export` (L773-838) | exact |
| `src/spur/parts.py` (widen `Part`) | config/type alias | n/a | itself | exact |
| `src/spur/records.py` (`_gear_fields`) | logging helper | request-response | itself (L171-180) | exact |
| `src/spur/din5480.py` (+`flank_half_angle`) | pure maths | transform | `din5480.tooth_thickness` (L103-108), `root_diameter` | exact |
| `src/spur/shaft_calc.py` (+`end_chamfer_effective`, 3 warnings) | pure maths / model | transform | itself: `hobbed_root_warning`, `ShaftDimensions`, `derive_shaft` | exact |
| `src/spur/shaft_params.py` (help text, bounds) | parameter model | validation | itself (L53-70) | exact |
| `pyproject.toml` (`ignore_imports`) | config | n/a | doorway contract (L~245-258) | exact |
| `tests/shaft_oracle.py` (+closed-form area/volume) | test oracle | transform | itself (`tooth_thickness`, `_involute_point`) | exact |
| `tests/test_shaft_model.py` (new) | test (kernel) | request-response | `tests/test_model.py` (`_closed_shell_volume`, L1984-2031) | role-match |
| `tests/test_shaft_calc.py` (key list, warnings) | test | transform | itself L76-87 | exact |
| `tests/test_shaft_params.py` (bounds pin) | test | validation | itself L93-103 | exact |
| `tests/test_pool.py` (shaft row), `tests/test_seam.py` | test | request-response | existing rows in those files | role-match |
| `bench/sweeps/shaft.json`, `bench/build_time.py` (part switch), `bench/RESULTS.md` | bench | batch | `bench/sweeps/trochoid.json`, `bench/build_time.py` | role-match |
| `docs/tech_debt/.../2026-10-23-parts-one-line-widening-claim-is-false.md` | docs | n/a | tech-debt resolve protocol (CLAUDE.md) | process |

## Pattern Assignments

### `src/spur/shaft_model.py` (kernel builder, transform)

**Analog:** `src/spur/model.py`. The file today is a docstring only (tracked). Must NOT import `spur.model` (cycle: model imports shaft_model).

**Imports pattern** (model.py L15-52): `from __future__ import annotations`, `import math`, `import cadquery as cq`, `from .build_errors import BuildError`; shaft side adds `from . import din5480`, `from .shaft_calc import derive_shaft`, `from .shaft_params import ShaftParams`. Reuse `TOL = 1e-6` convention (model.py); define a local copy, do not import it from model.

**Spacing and polar helper** (model.py L134-135, L201, L365):
```python
def _polar(r: float, t: float) -> cq.Vector:
    return cq.Vector(r * math.cos(t), r * math.sin(t), 0)
FLANK_POINTS = 16
radii = [r0 + (pr.ra - r0) * (i / (FLANK_POINTS - 1)) ** 1.5 for i in range(FLANK_POINTS)]
```

**Core outline pattern** (model.py L368-404; copy the edge sequence, drop the fillet branch):
```python
for k in range(pr.z):
    c = k * pitch
    left = [_polar(rho, c - pr.half_angle(rho)) for rho in radii]
    right = [_polar(rho, c + pr.half_angle(rho)) for rho in reversed(radii)]
...
    if straight:
        edges.append(cq.Edge.makeLine(root_l, left[0]))
    edges.append(cq.Edge.makeSpline(left))
    edges.append(cq.Edge.makeThreePointArc(left[-1], _polar(pr.ra, c), right[0]))
    edges.append(cq.Edge.makeSpline(right))
    if straight:
        edges.append(cq.Edge.makeLine(right[-1], root_r))
    edges.append(cq.Edge.makeThreePointArc(start, _polar(pr.rf, c + pitch / 2), end))
return cq.Wire.assembleEdges(edges)
```
Shaft differences (RESEARCH Pattern 1): `rs = max(rf, rb)`, radial line only when `rb > rf`, `ra`/`rf` = printed `tip_d/2`, `root_d/2` from `derive_shaft`, half-angle from the new pure `din5480.flank_half_angle` using the unrounded thickness. No `spline_start`, no fillet, no `ROOT_ARC_MIN`.

**Guard + one-valid-solid pattern** (model.py L773-790, L288-298):
```python
solids = solid.Solids()
if len(solids) != 1 or not solids[0].isValid():
    raise BuildError("Geometry kernel produced an invalid solid for these parameters.")
return solids[0]
# guard style: raise BuildError(f"...: {_NOT_A_PARAMETER_PROBLEM}")
```
Add: pre-build `1e-9 < abs(ra - c - rf) < 1e-4` guard, post-build volume/bbox bracket (RESEARCH "Guard turning silent garbage"). Shaft needs its own `_NOT_A_PARAMETER_PROBLEM`-style text without "set root_shape" (model.py L235-237 wording is gear-specific).

**Narrowing pattern** (model.py L665-678): `_body`/`_shape_of` assert a type and raise `BuildError(_NOT_A_BODY...)`; use the same instead of `cast` for `Shape.fuse`/`intersect` results.

**Fuse/intersect:** no gear analog (gear uses Workplane cuts). Follow RESEARCH Pattern 2: `Solid.extrudeLinear`, `body.fuse(Solid.makeCylinder(...))`, `body.intersect(Solid.revolve(...cone...))`, never `.clean()`.

---

### `src/spur/model.py` (doorway dispatch)

**Analog:** itself. Additive edits only (`make gear.unchanged` stays green).

**Current shape to edit** (L773, L792-802, L805-838): `_build(p: GearParams)`, `_build_checked(p: GearParams)`, `_build_cached = lru_cache(maxsize=int_env("SPUR_SOLID_CACHE", 4))(_build_checked)`, `build(p: Part)`, `_write_export(shape, p: GearParams, ...)`.

Plan: add `if isinstance(p, ShaftParams): return shaft_model.build_shaft(p)` at the top of `_build`; retype `_build_checked`, `_write_export` to `Part`. `_build_checked`'s wrapper text (L798-799 "try smaller fillets or chamfers") is wrong for shafts (Pitfall 7): branch the message on part type, test both texts. `_write_export` uses `p.slug()`: `ShaftParams` has no `slug()` (verified: only `params.py:267` defines one), so add one to `shaft_params.py` (RESEARCH OQ3: `spur_shaft_w{reference_d:g}x{module:g}x{teeth}`, provisional). STL copy-then-export block (L810-832, L24) is reused unchanged.

`model.py` L51-52 already imports `from .params import GearParams` and `from .parts import Part`; add `from .shaft_params import ShaftParams` and `from . import shaft_model`. `pool._warm` (pool.py L41-50) needs no edit (it imports `spur.model`).

---

### `src/spur/parts.py` and `src/spur/records.py`

**parts.py** (L17): `Part = GearParams` becomes `Part = GearParams | ShaftParams` as a plain assignment (docstring explains why not `TypeAlias`/`type`). Update the docstring (it describes Phase 32 in future tense). Import `from .shaft_params import ShaftParams`; contract "gear maths does not know the shaft" already names parts as exempt.

**records.py** (L171-180): `_gear_fields(p: Part)` returns `{"slug": p.slug(), "params": p.model_dump(exclude_defaults=True)}`. Both types have `model_dump`; needs `ShaftParams.slug()`. Rename is out of scope (surgical).

---

### `src/spur/din5480.py` (pure maths, transform)

**Analog:** `tooth_thickness` and `root_diameter`:
```python
def tooth_thickness(m: float, xm: float) -> float:
    """... DIN 5480-1:2006, cl. 6, Table 3."""
    return math.pi * m / 2 + 2 * xm * math.tan(ALPHA)
```
Add `flank_half_angle(m, z, xm, r)` using `ALPHA`, `inv` (L50) and the base-thickness formula from RESEARCH Pattern 1; radial (constant) below `rb`. No kernel import (contract: shaft maths free of cadquery).

---

### `src/spur/shaft_calc.py` (model + warnings)

**Warning constants pattern** (L38-66, L69-82): module-level string constants with a comment on provenance, one function when the sentence carries a number:
```python
ODD_Z_UNCONFIRMED = ("The measurement over pins M_Re is not given ...")
def hobbed_root_warning(root_d: float, module: float) -> str: ...
```
Add: root-fillet-is-a-construction sentence (D-03, no number), shank-step sentence when `shank_length > 0` (D-08), chamfer-capped sentence naming `end_chamfer`, cap and limiting factor (D-05), sub-resolution sentence (Pitfall 4). Each asserted by a test.

**New field** (ShaftDimensions L88-135): append `end_chamfer_effective: float | None = Field(description=..., json_schema_extra={"unit": "mm"})` after `measure_over_pins`, before `designation` (RESEARCH OQ3). Style: nullable fields like `pin_d` (L119-123).

**derive_shaft** (L190-244): compute `end_chamfer_effective` with `r3`-style helper but flooring: `floor(x*1000 + 1e-9)/1000`; cap = `(tip_d - root_d)/2` and `splined_length`; `None` when result 0. Warnings tuple at L241-243 is the append point: `(FORM_DIAMETER_UNPROVEN, *pin_warnings, hobbed_root_warning(...), *measure_warnings, *reading.warnings)`.

---

### `src/spur/shaft_params.py`

**Analog:** itself L53-70. `_f(default, ge, le, title=, group=, unit=, step=, help=)`. Edit `help` of `splined_length` ("full-form prism", D-08) and `end_chamfer` ("45 degree cone, size at the tip diameter", D-04); bounds stay unless the sweep says otherwise. Update the stale comment L53-55 ("cross-field rules ... arrive with the solid" is now false: D-07 allows all shank_d, D-05 caps). Add `slug()` modelled on `params.py:267`.

---

### `pyproject.toml`

Contract "The kernel doorways are model and shaft_model" (L~245-258): add `ignore_imports = ["spur.model -> spur.shaft_model"]` in the same commit as the first static import. Comment already documents it (Handoff to Phase 32). `tests/test_seam.py` regex belts (`test_only_model_may_import_the_shaft_solid`) must stay green.

---

### `tests/shaft_oracle.py` (stdlib-only oracle)

**Analog:** itself. Rules: no `spur` import, own `_ALPHA = math.radians(30.0)` (L34), module docstring states independence.
```python
def tooth_thickness(m, z, x):   # L65-82: s_b = m*cos(a)*(pi/2 + z*(tan(a)-a)) + 2*x*m*sin(a); half_angle_at_base = s_b/(2*r_b)
```
Add `tooth_half_angle(m, z, xm, r)`, `profile_area_within(...)`, `volume(...)`, Simpson helper (RESEARCH Code Examples). Reuse `_involute_point` (L57) for inv-free angles where possible.

---

### `tests/test_shaft_model.py` (kernel test, new)

**Analog:** `tests/test_model.py`.
- Closed shell + signed volume (L1984-2005, reuse by import or copy; `_stl_triangles` helper in the same file):
```python
def _closed_shell_volume(data: bytes) -> float:
    ... assert all(n == 1 for n in directed.values()) ...
    return volume
def test_exported_stl_is_a_closed_consistently_oriented_shell() -> None:
    assert _closed_shell_volume(export(GearParams(), "stl", "preview")) > 0
```
- Cache hygiene (L2026-2031): `build(p)`, export, assert the cached solid's `BoundingBox()` unchanged (L24).
Test header style from `tests/test_shaft_calc.py` L1-33 (`import shaft_oracle`, `from spur.shaft_params import ShaftParams`). Rows per RESEARCH Validation map; read-backs per Pattern 4; windows/hang probes in a `subprocess.run(..., timeout=)`. Tolerances recorded beside each test. Decide on `HEAVY_TEST_FILES` (`tests/test_hooks.py:39`, `Makefile:223-226`) after pricing (Pitfall 8).

### `tests/test_shaft_calc.py`, `tests/test_shaft_params.py`
- `test_the_shaft_dimensions_keys_are_fixed` (L81-87) lists 12 keys "in this order": update to 13 with `end_chamfer_effective` after `measure_over_pins`; log the L47 amendment.
- Bounds pin (test_shaft_params.py L93-103) parametrised `(field, ge, le)`; extend comment to cite the sweep rows; add a warning-sentence-is-constant test in the L47 style (`DEFAULT_HOBBED_ROOT_WARNING`, L~38).

### `bench/`
**Analog:** `bench/build_time.py` (L1-40: `Timing` dataclass, `from spur import int_env, model`, `DEFAULT_SWEEP` JSON, `make bench.build SWEEP=...`) and `bench/sweeps/trochoid.json`. It builds `GearParams` from JSON; add a part switch and `bench/sweeps/shaft.json` with the RESEARCH sweep rows. Record host, command, `ru_maxrss` units (macOS bytes, Linux KiB) in `bench/RESULTS.md`.

## Shared Patterns

### BuildError for modelling defects (L26)
**Source:** `src/spur/build_errors.py`, used at model.py L288-298, L665-678, L787.
**Apply to:** every guard in `shaft_model.py`. Never return a plausible shape; never let a selector select nothing.

### One kernel doorway, no cadquery leakage
**Source:** pyproject.toml contracts (L215-270). `shaft_model` public surface is `build_shaft(p) -> cq.Solid` only; `shaft_calc`/`din5480`/`shaft_params` stay kernel-free and logger-free.

### Numbers printed = numbers cut (L08)
**Source:** `derive_shaft` computes `tip_d`, `root_d`, `end_chamfer_effective`; `shaft_model` reads them from `derive_shaft`, never re-derives.

### Cache and mesh hygiene (L24)
**Source:** model.py `_write_export` (L810-832): `shape.copy().exportStl(...)`, STEP without copy, all under `_LOCK` then `_release_arenas()`.

### Every warning is a module constant asserted by a test; every guard seen red once
**Source:** `shaft_calc.py` constants, `investigation/` and `bench/RESULTS.md` convention (CONTEXT Established Patterns).

## No Analog Found

| File | Role | Data Flow | Reason |
|---|---|---|---|
| Fuse / revolved-cone intersect inside `shaft_model.py` | kernel op | transform | Gear uses Workplane cuts/extrudes, never `Shape.fuse`/`intersect`/`Solid.revolve`; use RESEARCH Pattern 2 and investigation scripts `.planning/phases/32-the-shaft-solid/investigation/32-spike.py` (verify tracked before citing) |
| `ShaftParams.slug()` | model method | n/a | Does not exist; copy the shape of `GearParams.slug` (`params.py:267`) |

## Metadata

**Analog search scope:** `src/spur/`, `tests/`, `bench/`, `pyproject.toml`
**Files scanned:** ~20 read or grepped; `git ls-files` confirmed all named analogs tracked
**Pattern extraction date:** 2026-10-27
