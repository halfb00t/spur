# Phase 9: Keyway Bore - Pattern Map

**Mapped:** 2026-09-27
**Files analyzed:** 15 (12 modified, 1 new sweep file, 2 confirmed no-change)
**Analogs found:** 15 / 15 (all in-repo; every analog is Phase 8's hex-bore work on the
same files, or the files' own existing D-flat/hex branches)

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `src/spur/params.py` | model (validated boundary) | request-response | itself — `bore_flat`/`bore_hex` fields (lines 56-65) | exact |
| `src/spur/calc.py` | utility (pure-math) | transform | itself — `bore_mouth_limit`, `check()`'s hex/round branches, `DerivedDimensions`, `derive()` | exact |
| `src/spur/model.py` | model (CAD boundary) | transform (kernel build) | itself — `_cut_bore`, `_build`'s step order (lines 195-219, 286-295) | exact |
| `src/spur/static/app.js` | component (form/render) | request-response | itself — `DIMS` array (lines 13-30) | exact |
| `tests/test_model.py` | test | transform (kernel assertions) | itself — `test_each_edge_selector_picks_exactly_its_own_edges`, `test_a_hex_bore_measures_the_across_flats_and_corners_it_reports`, `test_the_largest_hex_each_root_rule_allows_builds`, `test_a_recess_at_its_hub_clearance_keeps_min_wall_from_the_chamfered_bore_mouth` | exact |
| `tests/test_calc.py` | test | transform | itself — `test_infeasible_parameters_name_their_fields`, the hex boundary tests (121-221), `test_default_dimensions` | exact |
| `tests/test_api.py` | test | request-response | itself — the hex `/api/info` block (lines 143-220) | exact |
| `tests/test_cli.py` | test | request-response | itself — the hex CLI block (lines 91-124) | exact |
| `tests/regression/test_pre_v0_2.py` | test | batch (replay) | itself — unchanged, additive-null contract already generic | exact (no edit expected) |
| `bench/sweeps/keyway_bore.json` | config (bench data) | batch | `bench/sweeps/hex_bore.json` | exact |
| `bench/RESULTS.md` | config (record) | — | "## Hex bore build and export time (Phase 8, D-11)" section (lines 515-528+) | exact |
| `README.md` | config (docs) | — | the `bore_hex` bullet/table row/example (lines 11, 32, 107, 130-136, 151-155) | exact |
| `docs/architecture/decision_log.md` | config (docs) | — | L27 (lines 826-905, the hex bore's measured-limits entry) | exact |
| `.planning/ROADMAP.md`, `.planning/REQUIREMENTS.md` | config (docs) | — | 08-01-SUMMARY.md's amendment task (edit-phase tooling, one human confirmation) | exact |
| `src/spur/app.py`, `src/spur/cli.py` | controller | request-response | no change needed — both are schema-generated (confirmed by 08-02, re-cited in RESEARCH.md) | n/a |

## Pattern Assignments

### `src/spur/params.py` (model, request-response — validated boundary)

**Analog:** itself, the Bore group (lines 54-65)

**Imports pattern** (lines 1-14): unchanged, no new imports — `_f()` is the one
field-builder every scalar bore field already goes through.

**Core field pattern** (lines 56-65, the exact slot to insert between per D-17):
```python
bore_flat: float = _f(8.0, 0, 200, title="D-flat", group="Bore", unit="mm", step=0.05,
                      help="Flat to opposite side of the bore. 0 = round bore.")
# [NEW: keyway_width, keyway_depth go here, per D-17]
bore_hex: float = _f(0.0, 0, 200, title="Hex bore A/F", group="Bore", unit="mm",
                     step=0.05,
                     help="Across-flats of a hex bore; replaces the round bore and "
                          "D-flat. Common hex stock: 5, 6, 8, 10, 12.7 mm. "
                          "0 = round bore.")
```
Two new fields, same `_f()` shape as every sibling: `keyway_width: float = _f(0.0, 0, 200,
title="<planner's>", group="Bore", unit="mm", step=0.05, help="<D-16 sentence>")` and
`keyway_depth` identically — `ge=0, le=200, step=0.05` matches `bore_d`/`bore_flat`/
`bore_hex` exactly (D-17: "one family, one bound", 08 D-07's own rule reused verbatim).

**Validation/error wiring** (lines 84-94): unchanged — `_feasible` already calls
`calc.check(self)` and turns every `(message, fields)` tuple into one
`PydanticCustomError`. Every D-02/D-03/D-09/D-10/D-11/D-12/D-13 rule needs no new
plumbing here, only new `errors.append(...)` lines inside `calc.check()`.

**Error handling pattern**: none needed in this file — `check()` is the single
error-producing function; this file only wires it, exactly as it did for the hex bore.

---

### `src/spur/calc.py` (utility, pure-math — no cadquery import, CLAUDE.md boundary)

**Analog:** itself — `bore_radius`, `bore_mouth_limit`, `check()`'s hex/round branches,
`DerivedDimensions`, `derive()`

**Imports pattern** (lines 1-13): unchanged. `math` is already imported; `TYPE_CHECKING`-
gated `from .params import GearParams` stays the only params import — **never add
`import cadquery`** (the import-linter contract CLAUDE.md names).

**Datum pattern** (line 57-58, `bore_radius` — D-14's own datum, untouched):
```python
def bore_radius(p: GearParams) -> float:
    return (p.bore_d + p.bore_clearance) / 2 if p.bore_d > 0 else 0.0
```
The keyway floor radius is `bore_radius(p) + p.keyway_depth` wherever it's needed — a
one-line expression at each call site, not a new named helper unless the planner wants
one for the two derived fields (D-15).

**`bore_mouth_limit`'s "extend, don't widen" pattern** (lines 85-97 — the exact function
D-09 extends per RESEARCH.md Pattern 3):
```python
def bore_mouth_limit(p: GearParams) -> float:
    if p.bore_hex > 0:
        return bore_rim_limit(p) + 2 / math.sqrt(3) * p.bore_chamfer
    return bore_rim_limit(p) + (p.bore_chamfer if p.bore_d > 0 else 0.0)
```
D-09's fix is a `max(...)` wrapped around the existing round/D-flat branch: when a keyway
is set, take `max(bore_rim_limit(p) + (p.bore_chamfer if p.bore_d > 0 else 0.0),
math.hypot(bore_radius(p) + p.keyway_depth, (p.keyway_width + p.bore_clearance) / 2))` —
this is the exact "a later bore profile only has to extend these two functions" pattern
08-02 established and this phase's own code_context cites. `bore_rim_limit` (lines 67-82)
is explicitly **untouched** (D-06: "the selector runs before the keyway exists").

**`check()`'s if/elif shape-branch pattern** (lines 176-211 — the hex branch 176-201, the
round branch 202-208, the tuple shape every rule follows):
```python
if p.bore_hex > 0:
    ...
    elif bore_mouth_limit(p) > pr.rf - MIN_WALL:
        errors.append((
            "Bore chamfer is too large for this hex bore: at the corners it "
            f"reaches {2 * bore_mouth_limit(p):.2f} mm across, which must stay "
            f"{MIN_WALL:g} mm inside the root circle ({2 * pr.rf:.2f} mm); reduce "
            "bore_chamfer or bore_hex.",
            ("bore_chamfer", "bore_hex")))
else:
    r_bore = bore_radius(p)
    if p.bore_d > 0 and r_bore > pr.rf - MIN_WALL:
        errors.append(("Bore is too large for the root diameter.", ("bore_d",)))
    if p.bore_d > 0 and p.bore_flat > 0 and not p.bore_d / 2 < p.bore_flat < p.bore_d:
        errors.append((f"D-flat must be between {p.bore_d / 2:g} and {p.bore_d:g} mm "
                       "(flat to opposite side).", ("bore_flat",)))
```
Every new rule is one more `errors.append((f"<message naming the field(s)>",
("field", ...)))` line:
- **D-13** (both sentences) sit **before** the `if p.bore_hex > 0: / else:` split —
  they decide which branch even applies (code_context: "before the per-shape branches").
- **D-03** (half-set keyway) is a plain `if (p.keyway_width > 0) != (p.keyway_depth > 0):`
  guard, independent of shape.
- **D-02, D-10, D-11** join the `else:` (round/D-flat) branch, alongside the existing
  `bore_flat` range check — same tuple shape, new measured constants next to each rule
  (comment states what was measured, on what, when — the `BORE_RIM_SLACK` comment shape
  at `model.py` lines 51-56 is the project's template for this).
- **D-12** (the folded-in debt) is a new line in the same `else:` branch:
  `if p.bore_d > 0 and bore_mouth_limit(p) > <measured bound>: errors.append((..., ("bore_d", "bore_chamfer")))` —
  RESEARCH.md's Code Examples section gives the measured starting formula
  (`bore_mouth_limit(p) > pr.rf`, refine with a finer step per D-12/Open Question 2).

**`DerivedDimensions` field pattern** (lines 265-268, `bore_effective` — the exact shape
the two D-15 fields copy):
```python
bore_effective: float | None = Field(
    description="Bore diameter including print clearance; null with no bore or "
                "with a hex bore.",
    json_schema_extra={"unit": "mm"})
```
Two new `float | None` fields, same shape: description states what a caliper/pin-and-
caliper check reads and says "null with no keyway" (D-15).

**`derive()` construction pattern** (`r3()` idiom and `x if cond else None`, lines
368-397):
```python
bore_effective=r3(2 * bore_radius(p)) if p.bore_d > 0 and p.bore_hex == 0 else None,
```
The two new fields are `r3(bore_effective_value + p.keyway_depth) if p.keyway_depth > 0
else None` and `r3(p.keyway_width + p.bore_clearance) if p.keyway_width > 0 else None` —
same `r3()` call site, no new helper (D-15's "rounded to 3 dp at construction").

**Warning pattern** (D-02/hex-ignored idiom, lines 334-342 — the template if any keyway
warning sentence is needed, though D-09's yield is silent per its own "never a 422" and
`recess_radii()`'s existing cap-and-warn already covers the recess narrowing with no new
warning text required):
```python
ignored = [f"{name} ({value:g} mm)" for name, value in
          (("bore_d", p.bore_d), ("bore_flat", p.bore_flat)) if value > 0]
if ignored:
    warnings.append(f"Hex bore replaces the round profile: ...")
```

**Error handling pattern**: `check()` returns a list of tuples, never raises — the raise
happens once, in `params.py`'s `_feasible`. Every new keyway rule follows the same
non-raising, tuple-returning contract, unchanged from the hex bore.

---

### `src/spur/model.py` (model/CAD boundary — cadquery objects never escape this file)

**Analog:** itself — `_cut_bore` (lines 195-219, **untouched** per D-06) and `_build`'s
step order (lines 286-295, the exact insertion point)

**Imports pattern** (lines 30-41): add whatever calc-side helper the keyway floor needs
(likely just `bore_radius`, already imported) to the existing
`from .calc import (...)` block — same list, no new top-level import since `cq` and
`math` are already imported.

**Core "one more step after `_cut_bore`" pattern** (lines 286-295, the exact function
and insertion point D-06 names):
```python
def _build(p: GearParams) -> cq.Solid:
    pr = profile(p)
    solid = _gear_blank(pr, root_fillet(p), p.face_width)
    solid = _cut_face_recesses(solid, p, pr.rf)
    solid = _cut_bore(solid, p)
    # [NEW] solid = _cut_keyway(solid, p)   -- after the chamfer, per D-06

    solids = solid.Solids()
    if len(solids) != 1 or not solids[0].isValid():
        raise BuildError("Geometry kernel produced an invalid solid for these parameters.")
    return solids[0]
```
`_cut_bore` and `_bore_rim_edges` are explicitly **untouched** (D-06, code_context) — the
new step is a sibling function, not an edit inside either. RESEARCH.md's verified
`cut_keyway()` probe is the concrete shape:
```python
def _cut_keyway(solid: cq.Shape, p: GearParams) -> cq.Shape:
    if p.keyway_width <= 0:
        return solid
    r_bore = bore_radius(p)
    w_eff = p.keyway_width + p.bore_clearance
    floor = r_bore + p.keyway_depth
    slot = (cq.Workplane("XY").center(0, floor / 2)   # centred +Y (D-01)
            .rect(w_eff, floor).extrude(p.face_width).val())
    return solid.cut(slot)
```
This matches `_ring()`'s existing idiom (lines 224-226, `Workplane.rect().extrude()`) —
no new CAD primitive to learn, only a new arrangement (RESEARCH.md "Don't Hand-Roll").

**Existing selector — no change needed** (`_bore_rim_edges`, lines 252-281): confirmed
by both CONTEXT.md D-06 and RESEARCH.md Pattern 1/Pitfall 4 — it runs *before* the
keyway is cut, so its edge counts (2 `CIRCLE` round, 4 `CIRCLE`+`LINE` D-flat) are
unaffected. `_groove_floor_edges` (lines 229-249) is likewise unaffected.

**Error handling pattern** (lines 244-249, 276-281 — the D-15/07 zero-edge guard,
already-established, copy verbatim if the keyway ever needs its own selector — it does
not, per D-05 keeping its edges unchamfered): no new guard code required for this
phase's own cut, since `_cut_keyway` never calls `.chamfer()`/`.fillet()` on its own
edges.

---

### `src/spur/static/app.js` (component, request-response — schema-driven form)

**Analog:** itself — `DIMS` array (lines 13-30)

**Core pattern** (lines 13-30, the exact two-item-per-field shape D-15's UI rows copy):
```javascript
const DIMS = [
  ['pitch_d', 'Pitch Ø'],
  ...
  ['bore_effective', 'Bore Ø incl. clearance'],
  ['hex_across_flats', 'Hex across flats incl. clearance'],
  ['hex_across_corners', 'Hex across corners'],
  ...
];
```
Two new rows, e.g. `['<floor-to-wall field>', 'Keyway floor to opposite wall']` and
`['<effective-width field>', 'Keyway width incl. clearance']` (naming is the planner's,
D-15) — inserted anywhere in the array; order is display order only.

**Render/null-skip pattern — no change needed**: `renderInfo` already skips `null`/
`undefined` values generically (code_context: "`renderInfo` skips `null` rows"); the two
new keys read `null` with no keyway and are skipped automatically.

**Form generation / query building — no change needed** (`buildForm`, `gearQuery`):
both iterate `schema.properties`/non-default fields generically, so `keyway_width`/
`keyway_depth` get a form field and only ride the shareable URL when non-default, purely
from `params.py`'s field declaration (08 D-09: "no conditional form behaviour" —
explicitly why the bore-shape selector is deferred to Phase 12, not built here).

---

### `tests/test_model.py` (test, transform — kernel assertions)

**Analog:** itself — the parametrized matrix (lines 47-78), the hex built-solid
measurement test (159-184), the one-step-inside pattern (217-225), and the recess-yields
test (242-264)

**Matrix-row pattern** (lines 50-78, the exact three-tuple shape keyway rows copy —
"the keyway does not exist when the selector runs" per D-06/D-07):
```python
pytest.param({"bore_flat": 0}, collections.Counter({"CIRCLE": 2}), 4, id="round-both"),
pytest.param({}, collections.Counter({"CIRCLE": 2, "LINE": 2}), 4, id="d-flat-both"),
```
Keyway rows use `GearParams.model_validate({**kw, "keyway_width": <w>, "keyway_depth":
<d>, "bore_chamfer": 0, "recess_fillet": 0})` in the same `bare_p` idiom (lines 96-97:
"bore_chamfer feeds recess_radii()'s hub clearance"), expecting the **unchanged**
pre-keyway rim/floor counts (Discretion: "expecting the unchanged pre-keyway counts").

**Built-solid measurement pattern** (lines 159-184, `test_a_hex_bore_measures_...` — the
direct analog D-14's datum test copies):
```python
def test_a_hex_bore_measures_the_across_flats_and_corners_it_reports() -> None:
    p = GearParams(bore_hex=6, bore_chamfer=0, recess_sides="none")
    s = build(p)
    d = derive(p)
    rim = _bore_rim_edges(s, p)
    ...
    assert 2 * max(vertex_radii) == pytest.approx(d.hex_across_corners, abs=5e-4)
```
D-14's test reads the keyway floor back via RESEARCH.md's verified `Face.normalAt()` +
`BoundingBox()` selector (Pattern 2 — normal `(0, ±1, 0)`, `bb.ymin ==
bore_radius(p) + p.keyway_depth` within `TOL`, `bb.xlen == p.keyway_width +
p.bore_clearance` within `TOL`), or the edge-based alternative (`LINE` edges at
`y == floor_expected` filtered by `z ∈ {0, face_width}`) if the planner prefers matching
`_groove_floor_edges`'s existing idiom.

**One-step-inside pattern** (lines 217-225, `test_the_largest_hex_each_root_rule_
allows_builds` — the direct analog for D-10/D-11/D-12's "builds one step inside"):
```python
@pytest.mark.parametrize("kw", [...])
def test_the_largest_hex_each_root_rule_allows_builds(kw: dict[str, object]) -> None:
    s = _build_checked(GearParams.model_validate(kw))
    assert s.isValid()
```
Each of D-10/D-11/D-12's boundaries gets one row here (builds), paired with
`test_calc.py`'s refusal one step past it — the exact "refuse-one-step-past /
build-one-step-inside" pattern this phase's own code_context cites.

**Recess-yields pattern** (lines 242-264, `test_a_recess_at_its_hub_clearance_keeps_
min_wall_from_the_chamfered_bore_mouth` — the direct analog D-09 extends per its own
Discretion note "gains a keyway row"):
```python
def test_a_recess_at_its_hub_clearance_keeps_min_wall_from_the_chamfered_bore_mouth(
        kw: dict[str, object]) -> None:
    p = GearParams.model_validate({**kw, "bore_chamfer": 3, "recess_inner_d": 1.0})
    s = build(p)
    ...
    assert r_in - mouth == pytest.approx(MIN_WALL, abs=1e-6)
```
A keyway row (`{"keyway_width": ..., "keyway_depth": ...}`) added to this parametrize
list proves `recess_radii()`'s narrowing clears the keyway corner by exactly `MIN_WALL`,
the same invariant the hex row already proves for the corner case.

**Chamfer-survives-the-slot pattern to write new** (D-07's proof, no direct row-based
analog — nearest precedent is `test_the_kernel_chamfers_a_hex_bore_far_past_its_side_
length`'s volume-delta idiom, lines 189-197): build with and without a keyway on the
same D-flat/round params, assert the chamfer's removed volume survives (4.15 mm³ with
keyway vs 4.66 mm³ without, per RESEARCH.md's reproduced numbers) and the keyway's own
three rim edges are sharp (no edge at the slot's rim carries a chamfer face — the
simplest check is the face/edge count match RESEARCH.md's reproduced 178/508).

---

### `tests/test_calc.py` (test, transform)

**Analog:** itself — `test_infeasible_parameters_name_their_fields` (90-100), the hex
boundary tests (`test_a_hex_bore_is_refused_when_its_corners_reach_the_root_and_builds_
one_step_inside`, 138-159; `test_a_hex_bore_chamfer_that_carries_the_corners_to_the_
root_is_refused_naming_both`, 162-174), and `test_default_dimensions` (22-36)

**422-naming-fields pattern** (lines 90-100):
```python
@pytest.mark.parametrize(("kw", "field"), [
    ({"bore_flat": 3}, "bore_flat"),
    ({"bore_d": 30}, "bore_d"),
])
def test_infeasible_parameters_name_their_fields(kw: dict[str, object], field: str) -> None:
    with pytest.raises(ValidationError) as exc:
        GearParams.model_validate(kw)
    err = exc.value.errors()[0]
    assert err["type"] == "infeasible"
    assert field in err["ctx"]["fields"]
```
D-13's two sentences (hex×keyway, `bore_d=0`×keyway) get rows here directly. D-03
(half-set keyway) gets a row naming both `keyway_width` and `keyway_depth`.

**Measured-boundary refuse/build pattern** (lines 138-174, the exact shape D-02/D-10/
D-11/D-12 each need a pair of):
```python
def test_a_hex_bore_is_refused_when_its_corners_reach_the_root_and_builds_one_step_inside() -> None:
    GearParams(bore_hex=24.15, bore_chamfer=0)  # one step inside: builds
    with pytest.raises(ValidationError) as exc:
        GearParams.model_validate({"bore_hex": 24.2, "bore_chamfer": 0})
    err = exc.value.errors()[0]
    assert err["type"] == "infeasible"
    assert err["ctx"]["fields"] == ["bore_hex"]
    assert err["msg"] == ("Hex bore is too large for the root diameter: its corners "
        f"({2 * bore_rim_limit(p):.2f} mm across) must stay {MIN_WALL:g} mm ...")
```
Each of D-02/D-10/D-11/D-12 follows this exact two-part shape: one assertion that the
boundary-minus-a-step builds (plain `GearParams(...)` construction, no `pytest.raises`),
one that the boundary itself 422s with the exact `ctx["fields"]` list and message text.
RESEARCH.md's Code Examples section gives the starting numbers for D-12 (fails at
`bore_mouth_limit(p) == rf`, teeth-independent) and confirms D-11 has no kernel-crash
boundary at all (use the geometric-sanity bound `keyway_width <= bore_d` instead, stated
in the rule's own comment as RESEARCH.md's Pitfall 1 recommends).

**Derived-fields test pattern** (lines 22-36, `test_default_dimensions` — the L05
tripwire, and lines 175-192, `test_a_hex_bore_reports_across_flats_and_corners_and_
no_round_diameter` — the direct analog for D-15's two fields):
```python
@pytest.mark.parametrize(("kw", "flats", "corners", "bore"), [
    ({"bore_hex": 6}, 6.15, 7.101, None),
    ({}, None, None, 9.15),
])
def test_a_hex_bore_reports_across_flats_and_corners_and_no_round_diameter(...):
    d = derive(GearParams.model_validate(kw))
    assert d.hex_across_flats == flats
```
D-15's two fields get the same table-driven test: null with no keyway, the worked
numbers with one set (e.g. default bore + `keyway_width=3, keyway_depth=1.4` →
floor-to-wall 10.550, effective width 3.15, per CONTEXT.md's `<specifics>`).
`test_default_dimensions` itself needs **no new assertion** — the default `GearParams`
has no keyway, so both new fields must read `None` there, confirming L05.

---

### `tests/test_api.py` (test, request-response)

**Analog:** itself — the hex `/api/info` block (lines 143-220, especially
`test_a_hex_bore_reports_its_derived_fields_through_the_schema_and_info_endpoint`-shaped
assertions at 143-165, the 422 pattern at 182-193, and the ignored-field warning at
209-218)

**Schema-and-info pattern** (lines 143-165):
```python
def test_...() -> None:
    props = client.get("/api/schema").json()["properties"]
    assert props["bore_hex"]["group"] == "Bore"
    assert props["bore_hex"]["unit"] == "mm"
    assert props["bore_hex"]["maximum"] == 200
    assert props["bore_hex"]["default"] == 0
    names = list(props)
    assert names.index("bore_hex") == names.index("bore_flat") + 1

    r = client.get("/api/info", params={"bore_hex": 6})
    body = r.json()
    assert body["hex_across_flats"] == pytest.approx(6.15)
```
A keyway analog asserts `keyway_width`/`keyway_depth` schema entries (group, unit, max
200, default 0, declared between `bore_flat` and `bore_hex` per D-17), then a plain
`?keyway_width=3&keyway_depth=1.4` request asserting the two new derived fields.

**422-shape pattern** (lines 182-193):
```python
r = client.get("/api/info", params={"bore_hex": 24.2, "bore_chamfer": 0})
assert r.status_code == 422
detail = r.json()["detail"][0]
assert detail["ctx"]["fields"] == ["bore_hex"]
```
Every D-02/D-03/D-09-adjacent/D-10/D-11/D-12/D-13 refusal gets the same shape over
`/api/info`.

**D-04 coexistence pattern** (lines 209-218, the hex-ignores-round-fields warning test —
the direct analog for proving `bore_flat` stays with a keyway, D-04): a
`?keyway_width=3&keyway_depth=1.4` request on default params (which has `bore_flat=8`)
must build (200, not 422) and must **not** carry any "ignored" warning — the inverse of
the hex test's assertion.

**STL/STEP smoke pattern** (lines 172-180): a plain
`client.get("/api/model.stl", params={"keyway_width": 3, "keyway_depth": 1.4})` returning
200, mirroring the hex bore's own smoke test exactly.

---

### `tests/test_cli.py` (test, request-response)

**Analog:** itself — the hex CLI block (`export --bore-hex 6`, lines 91-95; the 422
pattern, lines 106-113; the info-matches-API pattern, lines 118-124)

**Export pattern** (lines 91-95):
```python
cli.main(["export", "-o", str(hexgear), "--bore-hex", "6"])
assert ("warning: Hex bore replaces the round profile: ..." in capsys.readouterr().err)
```
The README's keyed example (`spur export … --keyway-width 3 --keyway-depth 1.4`) gets its
own `cli.main([..., "--keyway-width", "3", "--keyway-depth", "1.4"])` call in this exact
shape — `--keyway-width`/`--keyway-depth` need no `cli.py` code change, only the test
(schema-generated per L02, confirmed by 08-02).

**422-on-CLI pattern** (lines 106-113):
```python
with pytest.raises(SystemExit) as exc:
    cli.main(["info", "--bore-hex", "25"])
assert "reduce bore_hex" in err
```
Template for asserting each keyway refusal sentence surfaces through the CLI too — parity
confirmation, not new logic (same `calc.check()` source).

**Info-matches-API pattern** (lines 118-124): `cli.main(["info", "--keyway-width", "3",
"--keyway-depth", "1.4"])`'s stdout JSON compared field-for-field against the equivalent
`/api/info` call, exactly as the hex bore's own parity test does.

---

### `tests/regression/test_pre_v0_2.py` (test, batch — replay)

**Analog:** itself — no edit expected. The additive-null contract (`assert all(v is None
for k, v in got.items() if k not in recorded)`) is already generic over every field added
since capture; the two new D-15 fields are covered automatically once
`DerivedDimensions` gains them. The only obligation this phase carries is `git diff
--exit-code tests/regression/pre_v0_2.json` after every task (07 D-03, L26) — the fixture
itself is never edited by this phase.

---

### `bench/sweeps/keyway_bore.json` (new file — config, bench data)

**Analog:** `bench/sweeps/hex_bore.json` (114 lines, 16 rows — the exact JSON-array-of-
objects shape)

**Row shape to copy exactly**:
```json
{
  "teeth": 200,
  "module": 1.75,
  "bore_hex": 200,
  "recess_sides": "both",
  "bore_chamfer": 0.4
}
```
Per Claude's Discretion, rows are `teeth=200 × module ∈ {1.75, 10} × recess_sides ∈
{both, none} × bore_chamfer ∈ {0.4, D-12's max} × the heaviest keyway the rules allow on
the largest `bore_d` they allow` — same flat-object-per-row array, `bore_d`/`keyway_width`/
`keyway_depth` keys added alongside the existing `teeth`/`module`/`recess_sides`/
`bore_chamfer` keys, no `bore_hex` key (mutually exclusive with a keyway per D-13).

---

### `bench/RESULTS.md` (config, record)

**Analog:** "## Hex bore build and export time (Phase 8, D-11)" section (lines 515-528+)

**Section shape to copy exactly**:
```markdown
## Hex bore build and export time (Phase 8, D-11)

The committed measurement record for the hex bore's heaviest allowed configuration
(ROADMAP Phase 8 SC4, D-11). ... The runner is `make bench.build` (D-12,
`bench/build_time.py`), over the committed sweep `bench/sweeps/hex_bore.json`. ...

### Host state

- Machine: 12 CPUs, arm64, 32.0 GiB RAM
- Python: 3.12.13
- Kernel: cadquery 2.8.0, cadquery-ocp 7.9.3.1.1
- HEAD: `<sha>`
- Sweep: `bench/sweeps/hex_bore.json`
- Load averages at start (script's own `os.getloadavg()`): ...
- `uptime` at the same time: ...
- SPUR_BUILD_TIMEOUT: 30 s, a cold request is one build plus one export
- Both readings sit above/below this project's usual "quiet" bar ... (L08).

### Sweep

| Parameter set | Build (s) | Fine STL (s) | STEP (s) | Build + slower export (s) | Inside 30 s |
|---|---|---|---|---|---|
| ... | ... | ... | ... | ... | yes |
```
A new "## Keyway bore build and export time (Phase 9, L27/L28's sibling)" section
follows this exact skeleton — same "### Host state" bullet list (machine facts, kernel
pin, HEAD sha, sweep filename, load-average caveat sentence verbatim in shape), same
sweep table columns, closing on the heaviest row inside 30 s (`make bench.build
SWEEP=bench/sweeps/keyway_bore.json` — D-06 of the "Process" section, the phase's own
gate).

---

### `README.md` (config, docs)

**Analog:** the `bore_hex` bullet/table row/example this phase's edits sit beside
(lines 11, 32, 107, 130-136, 151-155)

**Feature bullet pattern** (line 11):
```markdown
- Backlash, root fillets, D-flat, round or hex bore with print clearance and chamfer
```
Gains ", keyed with a rectangular slot" (or similar, planner's wording) in the same
sentence shape, no new bullet.

**Example pattern** (line 32/107, the hex bore's own example line):
```sh
spur export -o hexgear.stl --bore-hex 6                   # 6 mm hex bore
```
New example line in the same code block: `spur export -o keyedgear.step --keyway-width 3
--keyway-depth 1.4` (D-20's Discretion note: "a keyed example ... that the tests run" —
`tests/test_cli.py`'s `test_readme_export_examples_run`-shaped test exercises it).

**Refusals-and-warnings prose pattern** (lines 130-136): one sentence on the recess
yielding to the keyway corner (D-09, "never a 422"), matching the existing "A hex bore
replaces the round bore and D-flat" sentence's shape and position.

**Parameter table row pattern** (lines 151-155):
```markdown
| `bore_flat` | 8 | Flat to opposite side of the bore. 0 = round bore |
| `bore_hex` | 0 | Across-flats of a hex bore; ... |
```
Two new rows inserted between `bore_flat` and `bore_hex` (matches `params.py`'s
declaration order, D-17), carrying D-16's help sentences trimmed to table width, plus
one sentence each on the datum, the sharp slot edges and the unmodelled floor radius
(D-08, per Claude's Discretion).

---

### `docs/architecture/decision_log.md` (config, docs)

**Analog:** L27 (lines 826-905, "A hex bore replaces the whole round profile, and its
limits are the chamfered corner's, measured")

**Section shape to copy exactly** — L27's own structure is the template for L28:
```markdown
## L27 — A hex bore replaces the whole round profile, and its limits are the chamfered corner's, measured

Date: 2026-09-26.

**The field** (D-07, D-08). ...
**Replaces, never refuses** (D-01, D-02). ...
**The numbers** (D-04, D-05, D-06). ...
**The limits, measured** (D-03). ...
**The measurement** (D-11, D-12). ...
**Reversibility.** Costly: ... Reversible: ...
**Reason:** ...
```
L28 follows the same bolded-lead-in section shape: **The fields** (D-17), **The
placement and composition** (D-01, D-04), **The chamfer and build order, measured**
(D-05, D-06, D-07, D-08), **The datum** (D-14, with the corrected formula ROADMAP SC1
used to get wrong), **The refusals, measured** (D-02, D-03, D-09/D-10/D-11, D-13), **The
folded-in debt** (D-12, whether it shares this entry or gets its own `Lxx` is Claude's
Discretion), **The numbers** (D-15), **The measurement** (the sweep), **Reversibility**,
**Reason**.

---

### `.planning/ROADMAP.md`, `.planning/REQUIREMENTS.md` (config, docs — the D-20 amendment)

**Analog:** `.planning/phases/08-hex-bore/08-01-PLAN.md`/`08-01-SUMMARY.md` — the exact
"amend through edit-phase tooling, one human confirmation, before any other code" task
shape D-20 copies verbatim.

**Task shape** (08-01-SUMMARY.md in full): amend ROADMAP SC1's datum parenthetical
(`bore_d/2 + bore_clearance` → `(bore_d + bore_clearance)/2`, D-14), SC3's "or a recess
wall" clause (drop it, D-09), SC4's edge-count sentence (pre-keyway count + built-solid
proof, D-07), and REQUIREMENTS.md's matching text — every write goes through the
edit-phase workflow's scoped write step with a milestone-scope check before/after
(08-01-SUMMARY.md: "written only through the edit-phase tooling's write step ..., never
a direct whole-file write"), with one human checkpoint presenting the diffs before they
land, then a single commit covering all three files (`.planning/ROADMAP.md`,
`.planning/REQUIREMENTS.md`, `.planning/STATE.md`) per D-19's "plain `git commit`,
explicitly staged files."

---

## Shared Patterns

### The `check()` tuple contract (calc.py)
**Source:** `src/spur/calc.py` lines 155-219, `("message naming the field(s)",
("field", ...))`
**Apply to:** every new D-02/D-03/D-10/D-11/D-12/D-13 refusal rule; `params.py`'s
`_feasible` (lines 84-94) turns the list into one `PydanticCustomError` with
`ctx.fields` sorted and deduplicated — new rules need no changes there, only new
`errors.append(...)` lines in `check()`.

### Cap-and-warn vs. refuse (L03/L08)
**Source:** `recess_radii()`/`root_fillet()` (cap silently, warn in `derive()`) vs.
`check()` (refuse, name the fields) — `src/spur/calc.py` lines 100-121, 137-141, 155-219.
**Apply to:** D-09 sorts the recess-vs-keyway-corner case into "wish" (cap-and-warn, via
`bore_mouth_limit`'s extension feeding the existing `recess_radii()` unchanged); D-10
sorts the keyway-vs-root-circle case into "conflict" (refuse, `check()`'s tuple idiom).
Every keyway rule in this phase sorts into exactly one of these two functions, never a
third path — the same split the hex bore's D-01 (replace, cap-and-warn) vs. D-03 (refuse)
already established.

### `r3()` / rounded-once-at-construction (D-10, Phase 4)
**Source:** `derive()`'s `r3()` closure, `src/spur/calc.py` lines 368-369, applied to
every `DerivedDimensions` field at construction.
**Apply to:** the two new D-15 fields — round with `r3()` at the same call site inside
`derive()`'s `return DerivedDimensions(...)`, not inside a helper.

### Schema-driven interfaces need no per-field wiring (L02)
**Source:** `src/spur/cli.py`'s flag generator, `src/spur/static/app.js`'s `buildForm`,
`src/spur/app.py`'s query-to-`GearParams` binding — all iterate `GearParams.model_
fields`/`schema.properties` generically (confirmed unchanged by 08-02, re-confirmed by
this phase's own RESEARCH.md).
**Apply to:** confirms `keyway_width`/`keyway_depth` need zero changes in `cli.py` and
`app.py` — declaring them in `params.py` is sufficient for the CLI flags, the
`/api/schema` entries and the form fields. Only the two files that carry *new derived
output* (`calc.py`'s `DerivedDimensions`/`derive()` and `app.js`'s `DIMS`) need edits
beyond `params.py` and `model.py`.

### `bore_mouth_limit(p)` as the one seam every later bore profile extends (08-02's
pattern, re-confirmed this phase)
**Source:** `src/spur/calc.py` `bore_mouth_limit` (lines 85-97) and its own docstring's
"measured exact on the pinned kernel" convention; `recess_radii()` (lines 100-121) reads
it as the sole hub-clearance input.
**Apply to:** D-09's fix is the whole mechanism — extend `bore_mouth_limit`, and every
downstream reader (`recess_radii()`, `check()`'s shape-independent chamfer rule) picks up
the keyway corner with zero changes of its own, exactly as the hex corner did in Phase 8.

### Measured-not-assumed constants carry their measurement in a comment (L17/L19/L24/
L26/L27)
**Source:** `src/spur/model.py`'s `BORE_RIM_SLACK` comment (lines 51-56) and
`docs/architecture/decision_log.md`'s L27 ("The limits, measured" paragraph, lines
861-883).
**Apply to:** every D-02/D-10/D-11/D-12 boundary constant in `calc.py` — each needs the
same "how it was measured, on what, when, why not a rounder number" comment shape next
to the rule, and D-12's comment must explicitly say "no kernel failure exists at this
bound" for D-11 per RESEARCH.md's own Pitfall 1 warning.

### Zero-edge selector guard (07 D-15, L26) — confirmed unaffected, not extended
**Source:** `src/spur/model.py` `_bore_rim_edges` (lines 264-281) and
`_groove_floor_edges` (lines 229-249), each `if not edges: raise BuildError(...)`.
**Apply to:** neither selector is touched by this phase (D-06: the keyway does not exist
when either runs); no new guard code is needed for the keyway's own edges because D-05
never calls `.chamfer()`/`.fillet()` on them.

### Fixture-immutability guard (07 D-03, L26)
**Source:** `tests/regression/pre_v0_2.json`, `tests/regression/test_pre_v0_2.py` (its
additive-null contract, lines 39-46).
**Apply to:** every task in this phase — `git diff --exit-code
tests/regression/pre_v0_2.json` must pass after each one; this phase never edits
`tests/regression/` at all, and both new `DerivedDimensions` fields must read `null` on
every pre-v0.2 record automatically (the additive-null test is already generic — no
edit needed there either).

### Edit-phase-tooling amendment task (08-01's pattern)
**Source:** `.planning/phases/08-hex-bore/08-01-PLAN.md`/`08-01-SUMMARY.md` in full.
**Apply to:** D-20 — the plan's first task, amending ROADMAP SC1/SC3/SC4 and
REQUIREMENTS.md through the same scoped-write-plus-milestone-scope-check-plus-one-human-
confirmation workflow, before any code task begins.

## No Analog Found

None — every file this phase touches has an exact analog either in its own existing
D-flat/hex branches or in Phase 8's parallel "additive bore feature" cycle, which this
phase's keyway (a composing modifier, not a replacing shape) mirrors end-to-end at the
file level even though the composition itself is new.

## Metadata

**Analog search scope:** `src/spur/`, `tests/`, `tests/regression/`, `bench/`,
`docs/architecture/decision_log.md`, `docs/tech_debt/active/`, `README.md`,
`.planning/phases/08-hex-bore/` (read-only, for the D-20 amendment-task precedent).
**Files scanned:** `src/spur/params.py`, `src/spur/calc.py`, `src/spur/model.py`,
`src/spur/static/app.js`, `tests/test_model.py`, `tests/test_calc.py`,
`tests/test_api.py`, `tests/test_cli.py`, `tests/regression/test_pre_v0_2.py`,
`bench/build_time.py`, `bench/sweeps/hex_bore.json`, `bench/RESULTS.md`, `README.md`,
`docs/architecture/decision_log.md` (L27 section in full), `Makefile`,
`docs/tech_debt/active/2026-09-26-round-bore-chamfer-reach-is-not-checked.md`,
`.planning/phases/08-hex-bore/08-01-PLAN.md`, `.planning/phases/08-hex-bore/
08-01-SUMMARY.md`.
**Pattern extraction date:** 2026-09-27
**Tracked-source gate:** every path named above confirmed via `git ls-files` this
session (all print non-empty) — no gitignored mirror path (`.gsd/capabilities/...` or
similar) is involved anywhere in this phase's file set.
