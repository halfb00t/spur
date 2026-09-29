# Phase 10: Tooth-Tip Chamfer - Pattern Map

**Mapped:** 2026-09-28
**Files analyzed:** 9 (modified) + 2 (new)
**Analogs found:** 11 / 11

All analog paths below were verified git-tracked (`git ls-files`) in this session.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `src/spur/params.py` (`tip_chamfer` field) | model/config | CRUD (field declaration) | same file, `root_fillet` field (line 46) | exact |
| `src/spur/calc.py` (cap function, e.g. `tip_chamfer_effective`) | utility (pure math) | transform | `root_fillet(p)` (calc.py:201-206) | exact |
| `src/spur/calc.py` (`derive()` warning branch) | transform | transform | `rfil = root_fillet(p)` warning block, `derive()` ~471-480 | exact |
| `src/spur/calc.py` (`DerivedDimensions.tip_chamfer_effective` field) | model | transform | `root_fillet: float` field, `DerivedDimensions` (calc.py:368-447) | exact |
| `src/spur/model.py` (`_tip_edges` selector) | utility (kernel edge selection) | transform | `_groove_floor_edges` (model.py:254-275); secondary `_bore_rim_edges` (277-310) | exact |
| `src/spur/model.py` (chamfer step in `_build`) | controller (orchestration) | transform | `_cut_bore`'s chamfer call (model.py:218-219); `_build` (model.py ~312-322) | exact |
| `tests/test_model.py` (matrix column + 2 rows) | test | request-response | `test_each_edge_selector_picks_exactly_its_own_edges` (60-190+) | exact |
| `tests/test_model.py` (built-solid proof test) | test | request-response | `test_the_bore_chamfer_survives_the_keyway_and_the_slot_edges_stay_sharp` | exact |
| `tests/test_model.py` (tripwire + guard tests) | test | request-response | existing tripwire precedent + `_bore_rim_edges`'s empty-selection `BuildError` test | exact |
| `tests/test_calc.py` (cap + boundary + warning tests) | test | request-response | root/bore-chamfer cap and warning tests (390-, 462-) | exact |
| `tests/test_api.py` (`DerivedDimensions` literal set + DIMS-subset test) | test | request-response | `test_openapi_documents_the_typed_contracts` (62-88) | exact |
| `bench/sweeps/tip_chamfer.json` (new) | config (data) | batch | `bench/sweeps/keyway_bore.json` (full 32-row file read) | exact |
| `bench/RESULTS.md` (new section) | doc | batch | Phase 9 "Keyway bore build and export time" section (tail of file) | exact |
| `src/spur/static/app.js` (`DIMS` row) | component/config | request-response | existing `DIMS` array entries (13-31) — not read this session, name confirmed by research | role-match |
| `README.md` (parameter row + derived-field row + feature bullet) | doc | — | existing parameter table (~150-165) — not read this session, shape confirmed by research | role-match |
| `docs/architecture/decision_log.md` (L29 entry) | doc | — | L27/L28 entries — not read this session, format confirmed by CONTEXT.md/RESEARCH.md | role-match |

## Pattern Assignments

### `src/spur/params.py` — `tip_chamfer` field

**Analog:** `src/spur/params.py:46-48` (`root_fillet`), and the `_f()` helper (lines 18-23).

**Helper signature** (lines 18-23):
```python
def _f[T](default: T, ge: float, le: float, *, title: str, group: str,
          unit: str = "", step: float | None = None, help: str = "") -> T:
    extra: JsonDict = {"group": group, "unit": unit}
    if step is not None:
        extra["step"] = step
    return Field(default, ge=ge, le=le, title=title, description=help,
                 json_schema_extra=extra)
```

**Field to copy the shape of** (line 46):
```python
root_fillet: float = _f(0.5, 0, 3, title="Root fillet", group="Teeth", unit="mm",
                        step=0.05,
                        help="Fillet radius at the tooth roots, capped to fit. 0 = sharp.")
```
`tip_chamfer` goes immediately after this line, same `group="Teeth"`, `ge=0`, `le=3`
(Claude's Discretion recommendation, D-03 family), `step=0.05`, help text naming purpose
only (D-11) — e.g. `help="Chamfer on the tooth-tip edges at both faces — an edge break "
"for handling and printing. 0 = none."`. Default `0` (D-15, off).

---

### `src/spur/calc.py` — cap function (`tip_chamfer_effective` or planner's name)

**Analog:** `root_fillet(p)`, `calc.py:201-206`.

**Pattern to copy exactly:**
```python
def root_fillet(p: GearParams) -> float:
    """Root fillet actually used: the requested radius, capped to what fits the gap."""
    _, _, gap = _tooth(profile(p))
    return round(min(p.root_fillet, 0.45 * gap), 3) if gap > 0 else 0.0
```
New function shape: `round(min(p.tip_chamfer, 0.45 * p.face_width, pr.ra - pr.r, <boundary if D-04 fires>), 3)`
where `pr = profile(p)`. No `cadquery` import (import-boundary contract). `recess_fillet`
(calc.py, adjacent) is the two-term-min sibling to copy if a third measured-boundary term
is needed — same file, same three-line shape, `min(p.recess_fillet, 0.45 * width, 0.45 * p.recess_depth)`.

**Constant-with-measurement-comment shape (if D-04's kernel boundary is folded in), analog `ROOT_CONTACT`** (calc.py:16-32):
```python
ROOT_CONTACT = 1e-9     # mm, how close a chamfered round or D-flat bore mouth may sit
# to the root circle before it counts as touching it. Re-measured 2026-09-27 on the
# pinned kernel: a 20-step bisection over 12 configurations ...
```
Any new boundary constant must carry the same shape: value, bisection step count,
configurations sampled, last-failing / first-building gaps, date.

---

### `src/spur/calc.py` — `derive()` warning branch

**Analog:** the `root_fillet` warning in `derive()`:
```python
rfil = root_fillet(p)
if rfil < p.root_fillet:
    warnings.append(f"Root fillet reduced to {rfil:.2f} mm to fit the tooth gap.")
```
Copy this two-line shape: call the cap function once, compare to the request, append one
sentence naming the applied value and (D-09) which limit bound it — e.g. "reduced to X mm
to keep the tip land" vs "... to stay above the pitch circle" vs "... at the kernel's
limit," picking whichever of the `min(...)` terms actually won.

---

### `src/spur/calc.py` — `DerivedDimensions` field

**Analog:** `root_fillet: float` field, `DerivedDimensions` class (calc.py:368-447), but
**nullable** — closer analog is `recess_fillet: float | None`:
```python
recess_fillet: float | None = Field(
    description="Recess floor fillet radius actually used; null with no recess.",
    json_schema_extra={"unit": "mm"})
```
New field: `tip_chamfer_effective: float | None = Field(description="Tip chamfer actually "
"cut after the cap; null when tip_chamfer is 0.", json_schema_extra={"unit": "mm"})`.
Populate it in `derive()`'s return construction with `rfil if ... else None`-style logic
mirroring how `recess_fillet`/`rec_fil` is wired (search `derive()`'s return statement,
not shown above — read the tail of `derive()` before wiring this).

---

### `src/spur/model.py` — `_tip_edges` selector

**Analog:** `_groove_floor_edges`, `model.py:254-275` (primary — confirmed by this
session's research probe as sufficient, no z-height filter needed).

```python
def _groove_floor_edges(solid: cq.Shape, radii: tuple[float, ...],
                        floor_z: list[float]) -> list[cq.Edge]:
    edges = [e for e in solid.Edges()
             if e.geomType() == "CIRCLE"
             and min(abs(e.radius() - r) for r in radii) < TOL
             and any(abs(e.startPoint().z - z) < TOL for z in floor_z)]
    if not edges:
        raise BuildError(
            "Recess fillet selected no groove-floor edges: a modelling defect in spur, "
            "not a conflict in these parameters. Set recess_fillet to 0 to build this "
            "gear without it.")
    return edges
```
`_tip_edges(solid, pr)` drops the `floor_z` filter entirely (RESEARCH.md confirmed no
other edge sits at radius `ra`): `[e for e in solid.Edges() if e.geomType() == "CIRCLE"
and abs(e.radius() - pr.ra) < TOL]`. Copy the same `BuildError` message shape, naming the
defect and the fix: `"Tip chamfer selected no tip-arc edges: a modelling defect in spur, "
"not a conflict in these parameters. Set tip_chamfer to 0 to build this gear without it."`

**Secondary analog** `_bore_rim_edges`, `model.py:277-310` — the `BuildError` message
family and the "runs only when the feature is on, empty selection is a modelling defect"
doc-comment shape to copy for the selector's own docstring.

---

### `src/spur/model.py` — chamfer step in `_build`

**Analog — the exact call to reuse**, `_cut_bore`, `model.py:218-219`:
```python
solid = solid.chamfer(  # type: ignore[attr-defined]  # see _cut_face_recesses
    p.bore_chamfer, None, _bore_rim_edges(solid, p))
```

**Analog — `_build`'s four-step shape**, `model.py` ~312-322:
```python
def _build(p: GearParams) -> cq.Solid:
    pr = profile(p)
    solid = _gear_blank(pr, root_fillet(p), p.face_width)
    solid = _cut_face_recesses(solid, p, pr.rf)
    solid = _cut_bore(solid, p)
    solid = _cut_keyway(solid, p)

    solids = solid.Solids()
    if len(solids) != 1 or not solids[0].isValid():
        raise BuildError("Geometry kernel produced an invalid solid for these parameters.")
    return solids[0]
```
Append a fifth line before the `solids = solid.Solids()` check: guard on
`tip_chamfer_effective(p) > 0`, then `solid = solid.chamfer(c, None, _tip_edges(solid, pr))`
with the same `# type: ignore[attr-defined]` comment. Last step per D-13/research
"Tip chamfer last."

---

### `tests/test_model.py` — selector matrix column

**Analog:** `test_each_edge_selector_picks_exactly_its_own_edges`, full parametrize table
and body (lines 60-190+). Every existing `pytest.param` row needs a new expected tip-edge
count (`2 * teeth`, i.e. 38 for every existing default-19-teeth row) added to its tuple/kw,
plus two brand-new rows (200 teeth, module 0.2) per D-13. Copy the exact-count + identity
assertion style already used for `floor_edges` (asserting radius and z of each returned
edge, not just `len()`):
```python
for e in floor_edges:
    assert min(abs(e.radius() - r) for r in rr) < TOL
    assert min(abs(e.startPoint().z - z) for z in heights) < TOL
```

**Analog:** the `_cut_keyway` monkeypatch and `bare_p`/`_build_checked` bypass-cache
pattern (same test, header): `monkeypatch.setattr("spur.model._cut_keyway", lambda solid,
_p: solid)`. The tip selector runs unconditionally after the keyway step, so unlike the
rim/floor selectors it does not need `tip_chamfer` zeroed in `bare_p` — it needs
`tip_chamfer` set to a nonzero probe value explicitly in every row's `kw` (Pitfall 5).

---

### `tests/test_model.py` — built-solid proof test

**Analog:** `test_the_bore_chamfer_survives_the_keyway_and_the_slot_edges_stay_sharp`
(not fully read this session — line ref from research/CONTEXT, ~323). Its shape per D-12:
face-count delta, volume, `BoundingBox()` x/y extents, unchanged selector counts on
untouched features. Face delta expected `+2 × teeth`; edge delta measured in the spike,
not assumed (`+3 × 2 × teeth` observed at 19 teeth per RESEARCH.md's probe, but the plan
must re-measure at 200 teeth / module 0.2 before hard-coding it).

---

### `tests/test_model.py` — tripwire + empty-selection guard

**Analog:** the no-op-patch tripwire precedent (Phase 7 shape) — monkeypatch the new tip
chamfer step to a no-op, assert the built-solid proof (D-12) then fails. **Analog:**
`test_a_bore_chamfer_that_selects_no_rim_edges_is_a_build_error_not_a_bare_bore` (named in
RESEARCH.md's test map) for the empty-selection `BuildError` guard, routed 422/exit 1.

---

### `tests/test_calc.py` — cap + boundary + warning tests

**Analog:** the root/bore-chamfer cap and warning tests at `tests/test_calc.py:390-`,
`462-` (not fully read this session; confirmed present by RESEARCH.md). Shape: one test
per binding limit (D-01 axial, D-02 radial, D-04 measured-boundary if it fires), one test
for the warning sentence naming the applied value and the limit, and — mirroring
`test_the_largest_round_bore_the_chamfer_rule_allows_builds` /
`test_the_kernel_fails_where_a_round_bore_chamfer_touches_the_root` — two tests bracketing
the measured kernel boundary one step either side.

---

### `tests/test_api.py` — `DerivedDimensions` literal field set

**Analog:** `test_openapi_documents_the_typed_contracts`, `tests/test_api.py:62-88` (not
read in full this session; confirmed present and its exact behavior described in
RESEARCH.md Pitfall 4 — it hard-codes the full `DerivedDimensions` field-name set as a
Python literal, on purpose, so a renamed/added field must fail this test until updated).
Add `"tip_chamfer_effective"` (or chosen name) to that literal set in the same commit as
the `DerivedDimensions` field. Also check `test_every_key_the_ui_reads_is_a_derived_dimensions_field`
(`tests/test_api.py:110-126`).

---

### `bench/sweeps/tip_chamfer.json` (new)

**Analog:** `bench/sweeps/keyway_bore.json` (full file read this session) — flat JSON
array of partial `GearParams` kwarg dicts, unset fields take model defaults:
```json
{
  "teeth": 200,
  "module": 1.75,
  "bore_d": 200,
  "bore_flat": 0,
  "keyway_width": 199.95,
  "keyway_depth": 40.3,
  "recess_sides": "both",
  "bore_chamfer": 0.4
}
```
D-06's 9-row shape: `module ∈ {1.75, 10}` × `tip_chamfer ∈ {0.4, cap's max}` ×
`recess_sides ∈ {both, none}` (8 rows) at 200 teeth default bore, plus 1 row at module 0.2
(finest tips). Run via `make bench.build SWEEP=bench/sweeps/tip_chamfer.json`
(`Makefile:122-123`, `bench/build_time.py` unchanged, `load_sweep()` at lines 56-72).

---

### `bench/RESULTS.md` (new section)

**Analog:** the "Keyway bore build and export time (Phase 9)" section, tail of
`bench/RESULTS.md` (read this session, full section). Copy the shape exactly:
- Host-state header: sweep file name, `os.getloadavg()` at start, `uptime` moments before
  the run, `SPUR_BUILD_TIMEOUT`, and the load-average caveat sentence if load is above the
  "quiet" bar (>1.5 on the 12-core host).
- Table: `| Parameter set | Build (s) | Fine STL (s) | STEP (s) | Build + slower export (s) | Inside 30 s |`
- A **"Heaviest:"** line naming the worst row and its time.
- One prose paragraph comparing the heaviest row to Phase 8/9's own heaviest rows and to
  the worst single build on record — matches:
```
**Heaviest:** teeth=200 module=1.75 bore_d=200 bore_flat=150 keyway_width=3 keyway_depth=1.4 recess_sides=both bore_chamfer=0.4 -- 4.85 s of 30 s.

The heaviest row (4.85 s) sits at about a sixth of the 30 s timeout, close to but lighter
than Phase 8's heaviest hex row (5.08 s), ...
```

## Shared Patterns

### Cap-function contract (L08's "the part and the number cannot disagree")
**Source:** `root_fillet(p)` / `recess_fillet(p, rf)`, `src/spur/calc.py:201-206` and
adjacent.
**Apply to:** the new `tip_chamfer_effective(p)` cap function AND `model.py`'s chamfer
step, which must call the same function rather than re-deriving the cap.
```python
def root_fillet(p: GearParams) -> float:
    _, _, gap = _tooth(profile(p))
    return round(min(p.root_fillet, 0.45 * gap), 3) if gap > 0 else 0.0
```

### Position-based selector + guarded `BuildError`
**Source:** `_groove_floor_edges` / `_bore_rim_edges`, `src/spur/model.py:254-310`.
**Apply to:** `_tip_edges`. Runs only while its feature is on; selects by geometric
position (`geomType()`, `radius()`), never by insertion order; empty selection is always
a `BuildError` naming the defect and the fix, never a silent no-op — `Mixin3D.chamfer()`
with an empty edge list silently does nothing otherwise.

### Chamfer call semantics
**Source:** `_cut_bore`, `src/spur/model.py:218-219`.
**Apply to:** the new tip-chamfer step.
```python
solid = solid.chamfer(  # type: ignore[attr-defined]  # see _cut_face_recesses
    p.bore_chamfer, None, _bore_rim_edges(solid, p))
```
`length2=None` produces the symmetric 45° chamfer (D-03) — same call shape, swap in `c`
and `_tip_edges(solid, pr)`.

### Warning sentence family
**Source:** `derive()`'s "reduced to X mm to …" sentences, `src/spur/calc.py` ~471-513.
**Apply to:** the new D-09 warning; one sentence, naming the applied value and the
binding limit.
```python
rfil = root_fillet(p)
if rfil < p.root_fillet:
    warnings.append(f"Root fillet reduced to {rfil:.2f} mm to fit the tooth gap.")
```

### Kernel-boundary-measured constant (only if D-04 fires)
**Source:** `ROOT_CONTACT`, `src/spur/calc.py:16-32`.
**Apply to:** any new measured-boundary constant — comment must carry the bisection step
count, configurations sampled, last-failing/first-building gaps, and the date.

## No Analog Found

None — every file in scope has a strong (exact or role-match) analog; this is explicitly
called out in RESEARCH.md's own "Key insight": every mechanism this phase needs already
has a working, tested precedent in the codebase.

## Metadata

**Analog search scope:** `src/spur/{params,calc,model}.py`, `tests/{test_model,test_calc,
test_api}.py`, `bench/{build_time.py,sweeps/*.json,RESULTS.md}`, `src/spur/static/app.js`,
`README.md`, `docs/architecture/decision_log.md` — all already identified by CONTEXT.md
and RESEARCH.md's own code reads this session; this pass verified them directly against
the tracked source and extracted line-numbered excerpts.
**Files scanned:** 9 read directly this session (params.py, calc.py, model.py,
test_model.py, keyway_bore.json, RESULTS.md); 5 confirmed present via RESEARCH.md's own
line citations, not re-read (app.js DIMS, README table, decision_log.md, test_api.py
literal test, test_calc.py cap tests) — re-read by the planner/executor before editing.
**Pattern extraction date:** 2026-09-28
