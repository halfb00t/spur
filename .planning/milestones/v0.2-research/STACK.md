# Stack Research

**Domain:** CadQuery/OpenCascade solid modeling additions for spur v0.2 "Fit to Shaft"
(keyway bore, hex bore, spoke/lightening-hole/honeycomb body cutouts, tooth-tip chamfer)
**Researched:** 2026-09-25
**Confidence:** HIGH — every claim below was checked against the code actually installed in
this repo's `.venv` (`cadquery==2.8.0`, `cadquery-ocp==7.9.3.1.1`), which matches
`requirements.txt` line for line (verified with `pip show`), not against memory or docs for
a different version.

## Answer

**No dependency change.** `requirements.txt`'s pinned `cadquery==2.8.0` /
`cadquery-ocp==7.9.3.1.1` already expose every primitive v0.2 needs: polygon construction
for the hex bore and honeycomb cells, circular/polar patterning for lightening holes and
spoke gaps, multi-tool boolean cut for compositing many small cuts, and the same
`Mixin3D.chamfer`/`fillet` edge-selection pattern `model.py` already uses for the bore rim
and recess floors, reusable verbatim for the tooth tip. v0.2 stays at 31/31 pinned packages,
same as v0.1 (`PROJECT.md` "Current State").

## Recommended Stack

### Core Technologies — unchanged

| Technology | Version (pinned) | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| cadquery | 2.8.0 | Solid modeling API (`Workplane`, `Shape`, `Mixin3D`) | Already the only CAD layer in the repo (L01); its `Workplane.polygon`/`polarArray` and `Shape.cut`/`Mixin3D.chamfer` cover every v0.2 primitive — verified against the installed copy, not docs |
| cadquery-ocp | 7.9.3.1.1 | OCCT kernel bindings (`BRepAlgoAPI_Cut`, `BRepFilletAPI_MakeChamfer`) | Boolean cut and chamfer are OCCT operators reached through cadquery's `Shape`/`Mixin3D` wrappers; no direct OCP call needed for any v0.2 feature |

### Supporting Libraries — none added

No new supporting library is needed. `math` (stdlib, already imported in `model.py` for
`_polar()`) is sufficient for the honeycomb grid's row/column arithmetic — see
"Honeycomb pattern" below.

### Development Tools — unchanged

No new dev tool. `make verify`'s existing ruff/mypy/import-linter/pytest gate covers the new
code the same way it covers the existing `model.py`.

## API Verification (checked against the installed `.venv`, cadquery 2.8.0)

All four items below were read from
`.venv/lib/python3.12/site-packages/cadquery/{cq.py,occ_impl/shapes.py}` in this repo, via
`inspect.signature`/`inspect.getsource`, and one (hex across-flats) was additionally proven
numerically with a `BoundingBox()` check. Not inferred from docs or memory.

### 1. Polygon construction — hex bore and honeycomb cells

`Workplane.polygon(nSides: int, diameter: float, forConstruction: bool = False,
circumscribed: bool = False) -> T` (source: `cadquery/cq.py`).

With `circumscribed=True`, `diameter` is the across-flats distance (the polygon
circumscribes a circle of that diameter, so the circle touches each edge's midpoint) — the
exact spec unit the hex-bore parameter uses. Verified numerically:

```python
w = cq.Workplane("XY").polygon(6, 10.0, circumscribed=True)
w.val().BoundingBox().xlen  # == 10.0, the across-flats value passed in
```

Use `cq.Workplane("XY").polygon(6, across_flats, circumscribed=True).extrude(face_width)`
for the hex bore, mirroring `_cut_bore`'s existing `circle().extrude()` shape for the round
bore, then `.cut()` it the same way. No `rect`/manual vertex math needed for the hex itself;
`rect(xLen, yLen, centered, forConstruction)` (also on `Workplane`, confirmed present) stays
available for anything rectangular (e.g. a keyway's D-flat-style notch, following the same
`intersect()`-a-keep-shape pattern `_cut_bore` already uses for the D-flat) but is not
needed for the hex bore itself.

Honeycomb cells use the same `polygon(6, cell_size, circumscribed=True)` call per cell,
positioned by the tiling math below — not a different construction primitive.

### 2. Patterning — lightening holes, spoke gaps, honeycomb grid

`Workplane.polarArray(radius, startAngle, angle, count, fill=True, rotate=True) -> T`
(source: `cadquery/cq.py`) pushes `count` `Location`s evenly around a circle onto the
stack; the existing `_polar()` helper in `model.py` already does this by hand for the tooth
outline, so `polarArray` is optional polish, not a new capability — either is fine, and
`polarArray` is less code for a bolt-circle of holes.

- **Lightening holes:** `cq.Workplane("XY").polarArray(bolt_circle_r, 0, 360, count).circle(hole_r).extrude(face_width)`, then `.vals()` to get the list of `Solid`s for one `cut()` call (see "Boolean cut" below).
- **Spoke gaps:** the cutout is the material *between* arms, not the arms themselves — build one gap wedge with `Edge.makeLine`/`Edge.makeThreePointArc` between the hub and rim radii (the same primitives `_outline()` already uses for the tooth profile) and pattern it with `polarArray`, or compute the `arm_count` wedge angles directly with `_polar()`-style trig, matching the existing code's own idiom rather than introducing a new construction style.
- **Honeycomb grid:** `rarray(xSpacing, ySpacing, xCount, yCount, center)` (source: `cadquery/cq.py`, confirmed present) tiles a *rectangular* grid; a true hex/honeycomb tiling needs the offset-row trick (odd rows shifted by half `xSpacing`) that `rarray` does not do by itself. Checked the installed package for a built-in honeycomb helper: `grep -ril "honeycomb" .venv/lib/python3.12/site-packages/cadquery/` — **no matches**. There is no honeycomb primitive in cadquery 2.8.0. Build the grid as two `rarray`/`polygon` passes (even rows, then odd rows offset by half a cell pitch) or as one `each()`/`eachpoint()` callback computing row/column position with `math` — plain trigonometry, same tool the file already uses for `_polar()`, not a new dependency.

### 3. Boolean cut of many small solids — one call, not a loop

`Shape.cut(self, *toCut: Shape, tol: float | None = None) -> Shape` (source:
`cadquery/occ_impl/shapes.py`) is variadic: every tool shape passed goes into one
`BRepAlgoAPI_Cut` via `_bool_op()`, which builds a single `TopTools_ListOfShape` for the
tools and calls `op.SetRunParallel(True)` before `op.Build()` — one boolean operation over
all tools at once, with OCCT's own parallel execution, not N sequential single-tool cuts.
Confirmed by reading `_bool_op()`'s source directly.

**Implication for lightening holes / honeycomb cells:** collect every hole/cell `Solid`
(e.g. via `Workplane.vals()` after a `polarArray`/`rarray`+`extrude`) into one list and call
`solid.cut(*hole_solids)` once — matching how `_cut_bore` and `_cut_face_recesses` already
call `.cut()` a small, fixed number of times per feature, not per-instance. No pre-fusing
into a `Compound` is needed; `_bool_op` already flattens whatever iterable of `Shape`s is
passed into `toCut` into the tool list itself.

**Caveat, not verified — flag for measurement, not for a stack decision:** whether a single
`cut(*toCut)` with a few hundred tool solids (the honeycomb's worst case, capped by the
30s `SPUR_BUILD_TIMEOUT`) is fast enough was not benchmarked here — that is exactly the
"measured build time per feature at its heaviest allowed configuration" the milestone
already requires (`PROJECT.md`, Success Metric 2), not a library gap. No alternative library
would change this: the cost lives in OCCT's boolean algorithm, not in which Python wrapper
calls it.

### 4. Chamfer on tooth-tip edges — reuse the existing `Mixin3D` pattern, not a new API

`Mixin3D.chamfer(self, length: float, length2: float | None, edgeList: Iterable[Edge]) ->
Any` (source: `cadquery/occ_impl/shapes.py`) is exactly what `_cut_bore` already calls for
the bore rim (`solid.chamfer(p.bore_chamfer, None, _bore_rim_edges(...))  # type:
ignore[attr-defined]`) — same `# type: ignore[attr-defined]` will be needed again, for the
same reason the comment above `_cut_face_recesses` already documents: `Shape` declares no
`fillet`/`chamfer`; they live on `Mixin3D`, which every `Solid`/`Compound` carries, and
mypy strict cannot see that without the suppression. No new selector API is needed: write a
`_tip_edges()` alongside `_bore_rim_edges()`/`_groove_floor_edges()`, selecting by position
(edges near radius `pr.ra` on the `z=0`/`z=face_width` end faces) exactly like the other two
selectors already do — `solid.Edges()` filtered by geometry, not by OCCT edge type, is the
file's established idiom (see the comment on `_bore_rim_edges`: "Selected by position, not
by type").

**Caveat, not verified — flag for measurement:** `_outline()`'s own comment records that
OCCT's fillet/chamfer operator is "~50x slower" than the analytic root-fillet construction
on a many-toothed outline (L09) — that finding was about *root* fillets built into the 2D
wire before extrusion, a different code path from `Mixin3D.chamfer()` on already-built
solid edges, which is what the bore rim already uses successfully today. Whether a tip
chamfer scales acceptably to a high tooth count (the file elsewhere tests up to 200 teeth)
through `BRepFilletAPI_MakeChamfer` was not benchmarked here. Same conclusion as the cut
caveat above: this is the milestone's own required per-feature build-time measurement, not
a reason to reach for a different library — if it doesn't fit the timeout, the fix is
analytic edge-bevel geometry in `_outline()` (following L09's precedent), not a new
dependency.

## Installation

None. No new package, no version bump, no `requirements.txt` regeneration
(`docker/refresh-requirements.sh`) needed for anything in this milestone's target-feature
list.

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|--------------------------|
| `cadquery.Workplane.polygon(..., circumscribed=True)` for hex bore/cells | Hand-rolled hexagon vertices via `_polar()` (as `_outline()` does for the tooth wire) | Only if the hex needs to be built directly into a 2D wire alongside other wire-level construction (e.g. fused into the bore profile before a single extrude) rather than cut as its own extruded solid — not the case here; the existing bore/recess cuts are all separate solids cut into the blank, so `polygon()` is the smaller change |
| `Shape.cut(*many_solids)` in one call | A loop of `.cut()` calls, one per hole/cell | Never for a fixed-shape pattern of many small cuts — the variadic call is already one `BRepAlgoAPI_Cut` with parallel execution built in; a loop would rebuild the growing solid N times for no benefit |
| Reuse `Mixin3D.chamfer()` + a `_tip_edges()` position selector | A third-party CAD/geometry library, or `build123d` | Never — `build123d` is a different, unrelated project (a CadQuery-inspired fork with its own API and its own OCP binding); introducing it alongside cadquery would mean two CAD kernels' worth of native deps in the image for a feature the pinned cadquery already exposes |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|--------------|
| `build123d` | A separate, differently-versioned CadQuery-family project; adding it means a second OCCT binding in the dependency closure (the image is already ~1.5 GB of `cadquery-ocp`, L01/STACK.md) for zero new capability — everything asked for in v0.2 is already in the pinned `cadquery==2.8.0` | `cadquery.Workplane`/`cadquery.occ_impl.shapes.Shape`, already imported in `model.py` |
| A standalone geometry/tessellation library (e.g. `shapely`, `numpy`-based polygon packing) for the honeycomb grid | The grid is a fixed hexagonal-lattice offset-row formula — plain trigonometry, the same kind `_polar()` already does inline; a geometry library would be solving a problem this file doesn't have (arbitrary polygon packing) for a problem it does have (a regular lattice) | `math` (stdlib), following `_polar()`'s existing style |
| Building the hex bore or honeycomb cells with OCCT's fillet/chamfer or boolean operators for corner-rounding beyond what the milestone asks for | Out of scope — v0.2's hex bore and honeycomb cells are plain flats, no rounded corners specified in `PROJECT.md`'s target features | `Workplane.polygon(..., circumscribed=True)` as specified above |
| A standard keyway-size lookup table (DIN 6885 / ANSI B17.1 etc.) | `PROJECT.md` explicitly rejects this for v0.2: "no standard-table lookup...a looked-up size is a number someone cuts metal to, and would need the standard cited and its table verified" | Explicit width/depth/clearance parameters, per the target feature list |

## Stack Patterns by Variant

**If the hex bore needs a chamfer on its rim (mirroring the round bore's `bore_chamfer`):**
- Reuse `_bore_rim_edges`'s position-selection idiom, generalized to match either a circular
  or a hexagonal rim (arcs vs. six straight edges at the same radius/height test), rather
  than writing a second, hex-specific selector from scratch.
- Because the existing selector already separates "on the bore rim" from "on a recess"
  purely by radius and z-position (not by edge type), extending it to accept straight edges
  as well as arcs is a small predicate change, not new geometry.

**If the honeycomb cell count would blow the 30s `SPUR_BUILD_TIMEOUT` at the smallest
allowed cell size:**
- Cap the row/column count from the lattice formula before building any cell solids (the
  same "capped and warned" contract `PROJECT.md` already specifies for this feature), not
  after a slow build — computing the grid dimensions is pure `calc.py`-side arithmetic and
  can bound the count before any `cadquery` call happens.
- Because `calc.py` never imports the CAD kernel (import-linter contract, `AGENTS.md`),
  the cap must be computed there and passed down as a count, keeping the "no number the
  tool cannot back" rule (L08) intact for the warning message.

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| `cadquery==2.8.0` | `cadquery-ocp==7.9.3.1.1` | Exact pins already in `requirements.txt`; both installed and import-checked in this repo's `.venv` during this research (`pip show cadquery cadquery-ocp` matches the lockfile exactly) |
| `cadquery==2.8.0`'s `Workplane.polygon`/`polarArray`/`rarray`/`Shape.cut`/`Mixin3D.chamfer` | Python 3.12 only | Same floor the rest of the stack is already locked to (L23); no separate compatibility constraint from these specific calls |

## Sources

- `.venv/lib/python3.12/site-packages/cadquery/cq.py` (installed copy, version-matched to
  `requirements.txt` by `pip show`) — `Workplane.polygon`, `.rect`, `.polarArray`,
  `.rarray`, `.circle`, `.each`, `.eachpoint`, `.extrude` signatures and source, read
  directly via `inspect`.
- `.venv/lib/python3.12/site-packages/cadquery/occ_impl/shapes.py` (same installed copy) —
  `Shape.cut`, `Shape._bool_op`, `Mixin3D.chamfer`, `Mixin3D.fillet` signatures and source,
  read directly via `inspect`.
- Numeric check run in this repo's `.venv`: `Workplane.polygon(6, 10.0,
  circumscribed=True)` → `BoundingBox().xlen == 10.0`, confirming `circumscribed=True`'s
  `diameter` argument is the across-flats distance. HIGH confidence — reproducible,
  version-pinned, not a documentation claim.
- `grep -ril "honeycomb"` / `grep -ril "hex"` over the installed `cadquery/` package tree —
  confirms no built-in honeycomb helper and no hex-specific helper beyond
  `Workplane.polygon(nSides=6, ...)`.
- `/Users/halfb00t/git/halfb00t/spur/src/spur/model.py` — existing build order and the
  `_bore_rim_edges`/`_groove_floor_edges`/`_cut_bore`/`_cut_face_recesses` patterns v0.2's
  new cuts should extend, not replace.
- `/Users/halfb00t/git/halfb00t/spur/requirements.txt` — pin source of truth, cross-checked
  against the installed `.venv`.
- `/Users/halfb00t/git/halfb00t/spur/.planning/PROJECT.md` — v0.2 target features, "no
  standard-table lookup" and "cap and warn, don't refuse" rules that shape which API choice
  is idiomatic for this codebase.

---
*Stack research for: spur v0.2 "Fit to Shaft" (keyway bore, hex bore, body cutouts, tooth-tip chamfer)*
*Researched: 2026-09-25*
