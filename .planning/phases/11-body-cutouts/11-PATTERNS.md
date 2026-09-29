# Phase 11: Body Cutouts - Pattern Map

**Mapped:** 2026-09-29
**Files analyzed:** 9 (3 modified source, 1 static asset, 4 test modules, bench sweeps/docs)
**Analogs found:** 9 / 9 (all files touch existing modules; no wholly new files except bench sweep JSONs and a spike script, which copy an existing shape verbatim)

All analog paths below were checked with `git ls-files` this session; every one is
git-tracked source (no `.gsd/capabilities` mirrors involved in this repo).

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `src/spur/params.py` (+3 field groups, 10 fields) | model/config | CRUD (declarative field addition) | same file, Recess group (lines 89-101) + `_f()` helper (17-23) | exact |
| `src/spur/calc.py` (+cap/count/wall fns, +check() rules, +5 DerivedDimensions fields, +warnings) | service (pure maths) | transform (request → validated/derived numbers) | same file: `root_fillet`/`recess_fillet`/`tip_chamfer_limit` (213-281), `check()` (283-420), `DerivedDimensions` (432-513), `derive()` (516-653) | exact |
| `src/spur/model.py` (+`_cut_body` step, +3 cutter builders, +mirrored `_fillet_corner`) | service (CAD kernel boundary) | transform (params → solid, batched boolean cut) | same file: `_cut_face_recesses` (178-196), `_cut_bore` (199-223), `_fillet_corner` (96-113), `_ring` (271-273), `_build` (362-373) | exact |
| `tests/test_model.py` (+matrix rows, +3 built-solid proofs, +tripwires, +kernel boundary tests) | test | request-response (build → assert on solid) | same file: `test_each_edge_selector_picks_exactly_its_own_edges` (134-), `test_the_tip_chamfer_breaks_only_the_tip_arcs_on_the_built_solid` (630-), `test_the_tip_chamfer_proof_fails_when_the_tip_step_is_skipped` (648-), `test_a_recess_at_its_hub_clearance_keeps_min_wall_from_the_chamfered_bore_mouth` (690-) | exact |
| `tests/test_calc.py` (+422 refusal tests, +cap/warn tests) | test | request-response | same file: `test_infeasible_parameters_name_their_fields` (107), keyway refusal tests (315-395), `test_a_tip_chamfer_is_capped_to_whichever_limit_binds_first` (616) | exact |
| `tests/test_api.py` / `tests/test_cli.py` (+one link per pattern, +422 assertions) | test | request-response | existing Phase 8-10 hex-bore/keyway/tip-chamfer link tests in the same files | role-match |
| `tests/regression/pre_v0_2.json` + `test_pre_v0_2.py` | test/fixture | batch (byte-unchanged replay) | same files, unchanged this phase except new derived fields asserted `null` | exact |
| `bench/sweeps/*.json` (new: honeycomb spike + one sweep per pattern) + `bench/RESULTS.md` (+sections) | config/bench artefact | batch (measurement sweep) | `bench/sweeps/tip_chamfer.json`, `bench/build_time.py` (unchanged), `bench/RESULTS.md` "Tooth-tip chamfer build and export time (Phase 10)" section | exact |
| `src/spur/static/app.js` (`DIMS` array, +5 rows) | component (schema-driven form/derived-value list) | request-response (fetch schema, render) | same file: `DIMS` (13-32), schema-driven group renderer (45-56) | exact |

## Pattern Assignments

### `src/spur/params.py` (three new field groups)

**Analog:** same file, Recess group (lines 89-101), `_f()` helper (17-23)

**Field-declaration pattern** (verbatim, lines 89-101):
```python
# --- Recess ----------------------------------------------------------------
recess_sides: Literal["both", "top", "bottom", "none"] = Field(
    "both", title="Recess sides", description="Which faces get an annular groove.",
    json_schema_extra={"group": "Recess", "unit": ""})
recess_depth: float = _f(2.0, 0, 50, title="Recess depth", group="Recess", unit="mm",
                         step=0.1, help="Depth of each groove.")
recess_width: float = _f(6.0, 0, 100, title="Recess width", group="Recess", unit="mm",
                         step=0.1, help="Radial width of the groove.")
recess_inner_d: float = _f(0.0, 0, 400, title="Recess inner Ø", group="Recess",
                           unit="mm", step=0.1,
                           help="0 = centred so the hub wall equals the rim wall.")
recess_fillet: float = _f(0.5, 0, 5, title="Recess fillet", group="Recess", unit="mm",
                          step=0.05, help="Fillet at the groove floor corners.")
```
Insert the three new groups (Spokes, Holes, Honeycomb, D-19's order) immediately after
this block, each field a call to `_f(default, ge, le, title=, group=, unit="mm", step=,
help=)`. Every default is 0 (L05, D-19); the selector field (`spoke_count`, `hole_count`,
`hex_cell`) goes first in its group. No changes to `_feasible()` (103-113) — it already
calls `calc.check(self)` generically.

**Validation hook** (unchanged, lines 103-113) — every new refusal in `calc.check()`
surfaces here automatically; no new plumbing.

---

### `src/spur/calc.py` (cap/count/wall functions, `check()` rules, `DerivedDimensions`, `derive()`)

**Analog:** same file — `bore_mouth_limit`/`recess_radii` (151-197) for datums,
`root_fillet`/`recess_fillet`/`tip_chamfer_limit` (213-281) for the cap-and-warn shape,
`check()` (283-420) for refusals, `DerivedDimensions` (432-513) + `derive()` (516-653)
for the derived-fields/warning shape.

**Datum-reading pattern** (verbatim, lines 176-197, `recess_radii`):
```python
def recess_radii(p: GearParams, rf: float) -> tuple[float, float] | None:
    """(inner, outer) radius of the face groove, narrowed to fit between the hub wall
    and the tooth rim, or None when there is no room for a groove at all.
    ...
    """
    if p.recess_sides == "none" or p.recess_depth <= 0 or p.recess_width <= 0:
        return None
    r_bore = bore_rim_limit(p)            # the bore's farthest point (radius, or hex corners)
    hub = bore_mouth_limit(p) + MIN_WALL  # clear of the chamfered bore mouth
    rim = rf - MIN_WALL                   # clear of the tooth rim
    if rim - hub < MIN_RECESS_WIDTH:
        return None
    width = min(p.recess_width, rim - hub)
    centred = r_bore + (rf - r_bore - p.recess_width) / 2
    r_in = p.recess_inner_d / 2 if p.recess_inner_d > 0 else centred
    r_in = min(max(r_in, hub), rim - width)
    return r_in, r_in + width
```
The spoke/hole/honeycomb web-annulus functions (D-01, D-09, D-17) read the exact same two
datums — `bore_mouth_limit(p) + MIN_WALL` for the hub side, `rf - MIN_WALL` for the rim
side — never a fresh derivation.

**Cap-and-warn pattern** (verbatim, lines 213-217 + 540-542, `root_fillet` and its
warning):
```python
def root_fillet(p: GearParams) -> float:
    """Root fillet actually used: the requested radius, capped to what fits the gap."""
    _, _, gap = _tooth(profile(p))
    return round(min(p.root_fillet, 0.45 * gap), 3) if gap > 0 else 0.0
```
```python
rfil = root_fillet(p)
if rfil < p.root_fillet:
    warnings.append(f"Root fillet reduced to {rfil:.2f} mm to fit the tooth gap.")
```
`spoke_fillet_effective` (D-06, `0.45 × min(hub-opening, annulus width)`) and
`hex_cell_effective`/`hex_cell_count` (D-13, step-up-by-0.05mm-until-fits) must follow
this exact "applied-value function, `derive()` compares and warns" shape — `model.py`
must call the same function `derive()` calls (L08: "the part and the number cannot
disagree").

**Arc-measure precedent for the spoke hub-opening** (D-06/Pitfall 4; verbatim, lines
117-130, `keyway_flat_wall`):
```python
def keyway_flat_wall(p: GearParams) -> float:
    """The round bore wall left between the D-flat's corner and the keyway's side,
    measured as an arc on the as-cut wall (D-02's chosen measure): ...
    """
    r = bore_radius(p)
    flat_x = p.bore_flat + p.bore_clearance - r
    return r * (math.acos(keyway_width_effective(p) / 2 / r) - math.acos(flat_x / r))
```
The spoke hub-opening between adjacent bar feet on the hub circle should be an
`r * (acos(...) - acos(...))` arc measure in this same shape, not a chord — cited by
RESEARCH.md Pitfall 4 as the precedent.

**422-refusal pattern** (verbatim, lines 328-333, hex bore's own rule):
```python
if bore_rim_limit(p) > pr.rf - MIN_WALL:
    errors.append((
        "Hex bore is too large for the root diameter: its corners "
        f"({2 * bore_rim_limit(p):.2f} mm across) must stay {MIN_WALL:g} mm "
        f"inside the root circle ({2 * pr.rf:.2f} mm); reduce bore_hex.",
        ("bore_hex",)))
```
Every cutout refusal (D-10, D-14…D-17) returns this exact `(message, (field, ...))` tuple
into the same `errors` list; the if/elif non-stacking discipline (lines 350-412, e.g. the
hex-bore-too-large vs. bore-chamfer-too-large `elif`) is the pattern for D-17's "rules
never stack" requirement. The half-set pattern (D-15) mirrors the keyway's own half-set
rule (lines 318-322):
```python
if (p.keyway_width > 0) != (p.keyway_depth > 0):
    errors.append((
        "A keyway needs both keyway_width and keyway_depth: set both above 0, "
        "or both to 0.",
        ("keyway_depth", "keyway_width")))
```

**`DerivedDimensions` null-when-off field shape** (verbatim, lines 462-465):
```python
tip_chamfer_effective: float | None = Field(
    description="Tip chamfer actually cut on the tooth-tip edges at both faces, "
                "after the cap; null with no tip chamfer.",
    json_schema_extra={"unit": "mm"})
```
The five new D-20 fields (thinnest hub wall, thinnest rim wall, `hex_cell_count`,
`hex_cell_effective`, `spoke_fillet_effective`) each follow this: `float | None` /
`int | None`, a `description` stating the null condition explicitly, `unit: mm` on
lengths, rounded once at construction (same as `derive()`'s existing `r3()` helper,
line 615).

**Constants block precedent** (lines 15-49) — `HEX_CELL_CAP` (D-12) belongs here, in the
same "measured, dated, hosted" comment shape as `TIP_CHAMFER_MARGIN` (lines 33-45) and
`ROOT_CONTACT` (lines 20-32): cite the sweep, the date, the host, the bisection/enumeration
method, never a bare number.

---

### `src/spur/model.py` (`_cut_body` step + three cutter builders + mirrored fillet)

**Analog:** same file — `_cut_face_recesses` (178-196) for the "annulus + one/two `.cut()`
calls" shape generalized to `cut(*cutters)`; `_cut_bore`'s hex branch (199-223) for the
`polygon(6, d, circumscribed=True)` call the honeycomb reuses; `_fillet_corner` (96-113)
for the tangent-arc maths the spoke corners reuse (and must mirror for the rim side);
`_ring` (271-273) for the annulus-cutter helper shape; `_build` (362-373) for the
insertion point.

**Annulus + batched cut pattern** (verbatim, `_ring` at 271-273 and its use in
`_cut_face_recesses` 178-196):
```python
def _ring(r_in: float, r_out: float, z0: float, height: float) -> cq.Shape:
    return (cq.Workplane("XY").workplane(offset=z0)
            .circle(r_out).circle(r_in).extrude(height).val())  # type: ignore[return-value]
```
```python
def _cut_face_recesses(solid: cq.Shape, p: GearParams, rf: float) -> cq.Shape:
    rr = recess_radii(p, rf)
    if not rr:
        return solid
    r_in, r_out = rr
    ...
    solid = solid.cut(_ring(r_in, r_out, 0.0, p.recess_depth))
    ...
```
`_cut_body`'s three branches (spokes, holes, honeycomb) each build a list of cutter
`cq.Shape`s and call `solid.cut(*cutters)` exactly once per pattern (SC1, Pitfall 2) —
never a per-cutter loop, and never mixing patterns in one call (REQ-one-cutout-pattern
guarantees only one branch ever runs).

**Hexagon construction reused verbatim** (`_cut_bore`'s hex branch, lines 199-208):
```python
if p.bore_hex > 0:
    # circumscribed=True makes the polygon's diameter argument the across-flats (the
    # hexagon is drawn around that circle). The kernel's default puts a flat facing
    # +X -- the D-flat's side -- with a vertex on +-Y, and there is no rotation
    # parameter (planning probe, 2026-09-26).
    hole = (cq.Workplane("XY")
            .polygon(6, hex_across_flats(p), circumscribed=True)
            .extrude(p.face_width))
```
Honeycomb cells use the same `polygon(6, hex_cell, circumscribed=True)` call, translated
to each lattice centre, D-08's flats-on-±X convention already matching this orientation.

**Tangent-arc fillet, hub side unchanged, rim side mirrored** (verbatim, 96-113):
```python
def _fillet_corner(p0: cq.Vector, p1: cq.Vector, rf: float, rho: float,
                   gap_side: int) -> tuple[cq.Vector, cq.Vector, cq.Vector]:
    u = (p1 - p0).normalized()
    n = cq.Vector(-u.y, u.x, 0) * gap_side
    q = p0 + n * rho                  # centre = q + t*u with |centre| = rf + rho
    b = q.dot(u)
    t = -b + math.sqrt(max(0.0, b * b - (q.dot(q) - (rf + rho) ** 2)))
    centre = q + u * t
    on_line = p0 + u * t
    on_root = centre * (rf / (rf + rho))
    mid = centre + ((on_line + on_root) * 0.5 - centre).normalized() * rho
    return on_root, mid, on_line
```
D-05's rim-side mirror needs `|centre| = R - rho` instead of `|centre| = rf + rho` — a
sign flip in the quadratic term `(q.dot(q) - (R - rho) ** 2)` (RESEARCH.md Pattern 2,
flagged A1 as needing a hand-checked sanity case — no in-tree precedent for "centre
inside the circle").

**Build-order insertion point** (verbatim, 362-373):
```python
def _build(p: GearParams) -> cq.Solid:
    pr = profile(p)
    solid = _gear_blank(pr, root_fillet(p), p.face_width)
    solid = _cut_face_recesses(solid, p, pr.rf)
    solid = _cut_bore(solid, p)
    solid = _cut_keyway(solid, p)
    solid = _chamfer_tips(solid, p, pr)
    ...
```
`_cut_body(solid, p)` is inserted between `_cut_keyway` and `_chamfer_tips` — one line.

**Selector docstring already flags this phase** (`_groove_floor_edges`, 276-296):
```python
"""... Phase 11's cutouts put new circles on the recessed floor and must re-prove this
separating invariant (research PITFALLS.md Pitfall 4)."""
```
No new selector is added by this phase (D-05 rejects a 3D fillet needing one); the
matrix-test extension re-proves `_groove_floor_edges`, `_bore_rim_edges`, `_tip_edges`
still pick exactly their own edges with every cutout pattern active.

---

### `tests/test_model.py` (matrix rows, built-solid proofs, tripwires)

**Analog:** same file — `test_each_edge_selector_picks_exactly_its_own_edges` (134-) for
matrix rows; `test_the_tip_chamfer_breaks_only_the_tip_arcs_on_the_built_solid` (630-) +
`test_the_tip_chamfer_proof_fails_when_the_tip_step_is_skipped` (648-) for the
proof/tripwire pair; `test_a_recess_at_its_hub_clearance_keeps_min_wall_from_the_chamfered_bore_mouth`
(690-) for the one-step-either-side hub-datum test shape.

**Proof + tripwire pattern** (from RESEARCH.md's own excerpt of this file, lines
560-567, 630-657):
```python
def _assert_only_the_tip_arcs_were_chamfered(cut, plain, p, p0):
    """... Shared by the proof ... and the tripwire ..., which shows this proof fail on
    a silently vanished chamfer (D-14)."""
    d_faces = (Counter(f.geomType() for f in cut.Faces())
              - Counter(f.geomType() for f in plain.Faces()))
    assert d_faces == Counter({"CONE": 2 * n})
    # ... edge count delta, volume delta, bounding-box unchanged, other selectors
    # unchanged ...

def test_the_tip_chamfer_breaks_only_the_tip_arcs_on_the_built_solid(kw):
    _assert_only_the_tip_arcs_were_chamfered(_build_checked(p), _build_checked(p0), p, p0)

def test_the_tip_chamfer_proof_fails_when_the_tip_step_is_skipped(monkeypatch):
    monkeypatch.setattr("spur.model._chamfer_tips", lambda solid, _p, _pr: solid)
    assert derive(p).tip_chamfer_effective == 1.0  # the number still prints -- L08's failure
    with pytest.raises(AssertionError):
        _assert_only_the_tip_arcs_were_chamfered(...)
```
Each cutout pattern's built-solid proof (REQ-cutout-composes' fillet-survival test in
particular) copies this exact shape: one shared assertion helper, one proof test, one
tripwire that monkeypatches `_cut_body` to a no-op and shows both the proof going red and
`derive()`'s number still (wrongly) printing.

---

### `tests/test_calc.py` (422 refusal tests, cap/warn tests)

**Analog:** `test_infeasible_parameters_name_their_fields` (107) and the keyway refusal
tests (315-395) for the 422-naming-fields shape; `test_a_tip_chamfer_is_capped_to_whichever_limit_binds_first`
(616) for the cap-and-warn test shape D-06/D-13 copy — same file, same test module.

---

### `tests/test_api.py` / `tests/test_cli.py`

**Analog:** existing Phase 8-10 hex-bore/keyway/tip-chamfer per-interface link tests in
the same files (role-match; not read verbatim this pass — same file, same test module,
copy the nearest existing per-feature test class/function for the new pattern's link, its
422, and the `DIMS`-subset assertion).

---

### `bench/sweeps/*.json` + `bench/RESULTS.md` sections

**Analog:** `bench/sweeps/tip_chamfer.json` (verbatim shape, 6 rows shown: 200 teeth,
module {1.75, 10}, tip_chamfer {0.4, 1.75}, recess_sides {both, none}); `bench/build_time.py`
(unchanged, reused via `make bench.build SWEEP=`); `bench/RESULTS.md`'s Phase 10 section
(host-state header, table, named heaviest row) is the section-shape template for the
honeycomb spike and the three per-pattern sweeps.

```json
[
  {"teeth": 200, "module": 1.75, "tip_chamfer": 0.4, "recess_sides": "both"},
  {"teeth": 200, "module": 1.75, "tip_chamfer": 0.4, "recess_sides": "none"},
  {"teeth": 200, "module": 1.75, "tip_chamfer": 1.75, "recess_sides": "both"},
  {"teeth": 200, "module": 1.75, "tip_chamfer": 1.75, "recess_sides": "none"},
  {"teeth": 200, "module": 10, "tip_chamfer": 0.4, "recess_sides": "both"}
]
```

---

### `src/spur/static/app.js` (`DIMS` rows)

**Analog:** same file, `DIMS` array (13-32) and the schema-driven group renderer
(45-56, verbatim):
```javascript
const DIMS = [
  ['pitch_d', 'Pitch Ø'],
  ...
  ['web', 'Web thickness'],
];
```
```javascript
const group = prop.group ?? 'Other';
if (!groups.has(group)) {
  const fs = document.createElement('fieldset');
  ...
}
```
Five new `DIMS` rows (D-20's fields) is the only change; the group renderer needs no
code change for the three new schema groups (D-19) — confirmed by this exact code this
session.

## Shared Patterns

### The cap-and-warn contract (L08)
**Source:** `src/spur/calc.py:213-217` (`root_fillet`) + `calc.py:540-542` (its warning)
**Apply to:** `spoke_fillet_effective`, `hex_cell_effective`/`hex_cell_count` — the applied
value is computed once, in `calc.py`, and both `model.py`'s cut and `derive()`'s warning
must call that same function; never two code paths computing "what got cut" differently.

### The 422-refusal contract (L03/Pitfall 10)
**Source:** `src/spur/calc.py:283-420` (`check()`, the `("message", ("field", ...))` tuple
shape, if/elif non-stacking)
**Apply to:** every D-10, D-14…D-17 refusal — always in `calc.py`, before any CAD work,
never a `BuildError` after a timed build.

### Datum reuse (`bore_mouth_limit` / `rf`)
**Source:** `src/spur/calc.py:151-197` (`bore_mouth_limit`, `recess_radii`)
**Apply to:** every hub-side and rim-side cutout boundary (D-01, D-09, D-17) — read these
exact functions, never re-derive the chamfered-mouth or rim datum.

### Position-based selector re-proof (Pitfall 1/4, already flagged in-tree)
**Source:** `src/spur/model.py:276-296` (`_groove_floor_edges` docstring, verbatim: "Phase
11's cutouts put new circles on the recessed floor and must re-prove this separating
invariant")
**Apply to:** `tests/test_model.py`'s selector matrix — extend
`test_each_edge_selector_picks_exactly_its_own_edges`'s parametrization to include each
cutout pattern, at boundary-adjacent sizes, asserting exact edge counts, not just build
success.

### Batched boolean cut, never a loop (SC1, Pitfall 2)
**Source:** `src/spur/model.py:178-196` (`_cut_face_recesses`)
**Apply to:** all three `_cut_body` branches — one `solid.cut(*cutters)` call per pattern.

## No Analog Found

None. Every file this phase touches is a modification of an existing module with a
directly reusable in-tree shape; the one piece of genuinely new geometry math (the
mirrored `_fillet_corner` for rim-side corners, D-05) has a *precedent function* to mirror
but no existing "centre inside the circle" case in the tree — flagged in Pattern
Assignments above as needing its own hand-checked sanity test before trusting it broadly
(RESEARCH.md Assumption A1).

## Metadata

**Analog search scope:** `src/spur/{params,calc,model,static/app.js}.py`,
`tests/test_{model,calc,api,cli}.py`, `tests/regression/`, `bench/{build_time.py,sweeps/,RESULTS.md}`
**Files scanned:** 9 source/test/bench files read directly this session (full or targeted
ranges), plus 11-CONTEXT.md and 11-RESEARCH.md (both read in full)
**Pattern extraction date:** 2026-09-29
