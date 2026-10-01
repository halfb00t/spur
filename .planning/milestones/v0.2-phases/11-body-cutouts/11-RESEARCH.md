# Phase 11: Body Cutouts - Research

**Researched:** 2026-09-29
**Domain:** OCCT boolean cutting (CadQuery 2.8.0) — multi-cutter body cutouts (spoke arms,
lightening holes, honeycomb web), analytic 2D fillet arcs, an analytically-derived,
measured build-time cap
**Confidence:** HIGH — every CadQuery/OCP claim below was checked against this repo's
installed `.venv` (`cadquery==2.8.0`, `cadquery-ocp==7.9.3.1.1`) this session, or against
code actually in the tree (`model.py`, `calc.py`, `params.py`, tests) read this session.
The honeycomb cell-count-vs-build-time cap itself is **not** determined here — 11-CONTEXT.md
D-24 assigns that measurement to the plan's first task (a dedicated spike), and this
research deliberately does not pre-empt it with an un-cited number.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**D-01 — Spoke arm geometry, the datum.** `hub_d` is the hub ring's outer diameter;
`rim_wall` is the rim ring's radial thickness measured inward from the root circle. Cut
sectors run from `hub_d / 2` to `rf − rim_wall`. Rejected: `hub_d` as the hub's radial wall
above the chamfered mouth; `rim_wall` from the tip circle. Reversibility: costly.

**D-02 — Arms are parallel-sided bars of constant width `spoke_width`.** The cutter set is
the annulus minus N bars — N sector solids in one compound, one `.cut` call. Rejected:
tapered angular sectors. Reversibility: costly.

**D-03 — Arm 0 and hole 0 are centred on +X; no angle field.** One fixed convention for
both patterns: the D-flat's side, the hex bore's flat, `polarArray`'s default start.
Rejected: +Y over the keyway; a rotation field now (deferred, additive-safe later).
Reversibility: costly.

**D-04 — Sector corners are filleted by a new field, `spoke_fillet` (mm, 0 = sharp)** —
the human's choice over the recommendation (sharp). A fifth spoke field on every
interface; REQ-spoke-cutout and ROADMAP Phase 11 SC2 name four, so the plan amends both
(D-21). Rejected: sharp corners; a fixed radius.

**D-05 — The fillet is built as analytic 2D tangent arcs in the cutter's sketch,
extruded** — L09's remedy for the fillet operator on many edges. Each sector is one
closed wire: hub arc, corner arc, bar side, corner arc, rim arc, corner arc, bar side,
corner arc; `_fillet_corner`'s maths (a line against an axis-centred circle) covers the
hub corners with the arc centre outside the hub circle at `hub_d/2 + ρ` and needs its
mirror for the rim corners (centre inside the rim circle at `rf − rim_wall − ρ`). No 3D
`.fillet()`, no new edge selector, no matrix column, no tripwire for a selector. Rejected:
the 3D operator on the 4N vertical corner edges; a spike timing both (the planner can
probe the analytic arcs on the pinned kernel in minutes).

**D-06 — `spoke_fillet` is capped to the sector, warned, and the applied value
reported:** `ρ ≤ 0.45 × min(the sector's opening at the hub ring between adjacent bar
sides, the annulus width rf − rim_wall − hub_d/2)` — `root_fillet`'s 0.45-of-the-shared-
dimension family. Trimmable: L03's cap branch, a `spoke_fillet_effective` derived field.
Rejected: a 422 when it does not fit; the applied value in the warning only.

**D-07 — Whole cells only, never clipped.** A cell is cut only if its entire hexagon —
corner reach `hex_cell / √3` from its centre — lies inside the web annulus; a cell
straddling the hub or rim boundary stays solid. No sliver faces at a boundary, every wall
at least the boundary by construction, an integer count of full cells. Rejected: cells
intersected with the annulus; a lattice stretched to fill. Reversibility: costly.

**D-08 — The lattice origin is the gear axis and the cells' flats face ±X.** The origin
cell lies inside the bore and is never cut; hexagons come from `polygon(6, hex_cell,
circumscribed=True)` exactly as the hex bore's does (flats on ±X, vertices on ±Y). Rows
run along the flat-to-flat direction. Rejected: an origin shifted so the first ring
touches the hub wall; a vertex facing +X. Reversibility: costly.

**D-09 — `hex_wall` is the wall everywhere, including both boundaries:** inner boundary
`bore_mouth_limit(p) + hex_wall`, outer `rf − hex_wall`. One wall number means one thing
between cells and at the edges. Rejected: `MIN_WALL` boundaries with `hex_wall` between
cells; separate boundary-wall fields. Reversibility: costly.

**D-10 — `0 < hex_wall < MIN_WALL` is a 422 naming `hex_wall`**, quoting 0.4 mm; 0 stays
"off". Rejected: raising to `MIN_WALL` with a warning; building it and warning like
`MIN_TIP_FDM`.

**D-11 — The honeycomb at its cap may cost at most a quarter of `SPUR_BUILD_TIMEOUT` —
≤ 7.5 s — on the bench host**, measured as `bench/build_time.py`'s `worst_request` for the
whole row, at 200 teeth, module 10, both recesses (the heaviest web, so the cap always
binds). 7.5 s is the quarter-of-timeout line Phase 10 already named; the tip chamfer alone
reads 14.87 s at 200 teeth. Rejected: half the timeout; whatever fits alone. Reversibility:
costly.

**D-12 — The cap is one constant cell count in `calc.py`** (on the order of
`HEX_CELL_CAP`): the largest count whose sweep row at D-11's configuration reads ≤ 7.5 s,
measurement/date/host in the comment (L17's shape), cited in L30. Rejected: a per-cell
cost model; a teeth/module-dependent cap.

**D-13 — When the derived count exceeds the cap, `hex_cell` is stepped up by 0.05 mm from
the request** — the field's own step — **until the exact whole-cell count is ≤ the cap;**
an area estimate is used first so exact enumeration never runs for millions of cells. Two
derived fields: `hex_cell_effective` (`null` when off) and `hex_cell_count`. One warning
naming the requested size, the applied size and the cap. Rejected: the exact off-grid
minimum size; the count only.

**D-14 — A honeycomb in which no whole cell fits is a 422 naming `hex_cell` and
`hex_wall`**, quoting the web annulus's inner and outer radius. Rejected: building a solid
web with count 0 and a warning; lowering `hex_cell` until one fits.

**D-15 — A half-set pattern is a 422 naming the zero fields; dimensions set with the
count at 0 are inert and warned about.** `spoke_count > 0` with `spoke_width`, `hub_d` or
`rim_wall` at 0, or `hole_count > 0` with `hole_d` or `hole_circle_d` at 0, or `hex_cell >
0` with `hex_wall` at 0: refused before any CAD work. The reverse — a dimension set with
the count at 0 — builds without the pattern and one warning names the ignored fields with
their values; `spoke_fillet` with the count at 0 is in that ignored set. Rejected:
silently inert dimensions; treating a half-set pattern as off with a warning.

**D-16 — `MIN_WALL` between neighbours, both patterns.** Holes: `hole_circle_d · sin(π /
N) − hole_d ≥ MIN_WALL`. Spokes: the sector opening between adjacent bars at the hub ring
`≥ MIN_WALL`. The honeycomb is covered by D-10. 422 naming the count and size fields.
Rejected: overlap only; a floor for holes and overlap-only for spoke sectors.

**D-17 — The hub and rim breaches read the recess's datums:** hub wall
`bore_mouth_limit(p) + MIN_WALL`, rim wall `rf − MIN_WALL`. Spokes: `hub_d / 2 <
bore_mouth_limit(p) + MIN_WALL` → 422 naming `hub_d`; `rim_wall < MIN_WALL` → 422 naming
`rim_wall`; `rf − rim_wall − hub_d/2 < MIN_WALL` → 422 naming `hub_d` and `rim_wall`.
Holes: `hole_circle_d/2 − hole_d/2 < bore_mouth_limit(p) + MIN_WALL` or `hole_circle_d/2 +
hole_d/2 > rf − MIN_WALL` → 422 naming `hole_circle_d` and `hole_d`. Honeycomb: no breach
reachable — D-09/D-07 keep every cell inside by construction; D-14 covers the empty case.
Rules never stack (`elif`).

**D-18 — `spoke_count` and `hole_count` are integers 0–200, and 1 is allowed.** One
instance per tooth is the natural ceiling. Rejected: 24/48 (no source); a minimum of 2.

**D-19 — Three schema groups — Spokes, Holes, Honeycomb — declared after the Recess
group in that order,** selector field first in each (`spoke_count`, `hole_count`,
`hex_cell`). Rejected: one "Cutouts" fieldset; extending the Body group.

**D-20 — Five new `DerivedDimensions` fields**, names the planner's: thinnest remaining
wall on the hub side and on the rim side (`null` when no cutout set), `hex_cell_count`
(`int | None`), `hex_cell_effective` (`null` when honeycomb off), and
`spoke_fillet_effective` (`null` when spokes off or `spoke_fillet` 0). Rounded once at
construction, `unit: mm` on the lengths. Reversibility: costly.

**D-21 — Process: the plan's first task amends REQ-spoke-cutout and ROADMAP Phase 11 SC2**
to add `spoke_fillet`, through the edit-phase tooling with one human confirmation, never a
direct write.

**D-22 — Branch `gsd/phase-11-body-cutouts`**, cut from `origin/main` `b388cbd`, lands via
`make pr.land PR=N`.

**D-23 — Commits are plain `git commit` with explicitly staged files**, never `git add
-A`; pre-commit runs `make verify` (~100 s warm) which the gsd commit wrapper's 30 s
timeout kills — after any wrapper timeout, check for a pre-commit stash before
re-committing. Run `make verify` once at session start.

**D-24 — The honeycomb spike is a measurement-only plan** whose numbers exist before the
cap constant, the honeycomb field plan and the honeycomb proof plan are written; no field
needed — a probe path cutting N whole cells at D-11's configuration. Holes and spokes need
no spike. Order (holes, spokes, honeycomb) is the planner's to keep or parallelise, with
the constraint that the cap is written only from the sweep's numbers.

**D-25 — L30 is appended** to `docs/architecture/decision_log.md` (append-only): fields
and datums, the whole-cell rule and lattice, the cap methodology with the sweep's numbers,
the refusals, the analytic spoke fillet, each pattern's heaviest row — each cited to a
SUMMARY sha or `bench/RESULTS.md`, none re-estimated.

### Claude's Discretion

- **Names:** the cut step and cutter builders in `model.py`, the cap/count/wall functions
  in `calc.py` (siblings of `recess_radii`/`tip_chamfer_limit`), the five derived fields
  (D-20), the sweep files, the RESULTS.md section titles, the field titles and every
  refusal/warning sentence.
- **The thinnest-wall datum (D-20):** hub side from `bore_mouth_limit(p)` — exact for
  round/D-flat, a lower bound for hex/keyway unless the planner computes the exact minimum
  distance to the mouth polygon; the field description must say "from the farthest point
  of the bore mouth" if the bound is used. Rim side from `rf`. Spokes: hub ring and
  `rim_wall`; holes: nearest hole edge; honeycomb: nearest cut cell's corner, from the
  lattice.
- **Dimension bounds:** family bounds recommended — `spoke_width`, `hole_d`, `rim_wall`,
  `hex_cell`, `hex_wall` `le` 100; `hub_d`, `hole_circle_d` `le` 400; `spoke_fillet` `le`
  5; `ge` 0, step 0.05 (0.1 for diameters if preferred).
- **Cutter construction:** spokes as N closed 2D wires → faces → prisms → one
  `cut(*prisms)`; holes as N cylinders from one `polarArray` or N explicit centres;
  honeycomb as N hexagonal prisms at lattice centres. Whether N prisms are passed as
  `*cutters` or fused into one compound first is measured in the spike and the faster
  recorded.
- **Honeycomb enumeration in `calc.py`:** axial or offset lattice coordinates, area
  estimate bounding the search, exact test on each candidate; `derive()` runs on every
  keystroke, so measure its cost at the cap and record in the docstring.
- **`tol=`:** a hole or cell can legitimately sit tangent to a recess wall or to nothing.
  Probe the pinned kernel at tangent cases and ship `tol=` only with the measurement and
  its own comment; a 422 for coincidence is rejected.
- **The recess-fillet survival proof:** count the fillet's faces/edges on the built solid
  before and after each pattern; what a through-cut does to a toroidal fillet face is
  measured on the pinned kernel and pinned, not derived.
- **Selector matrix rows:** each pattern × {round, D-flat, hex, keyway} × recess settings,
  expected rim/floor counts unchanged, tip count `2 × teeth`; plus a real-pipeline spy.
- **Sweep rows:** per pattern, 200 teeth × module {1.75, 10} × recess {both, none} at the
  `le` count and at both a small and a large hole/sector size (09-04's lesson: heaviest row
  was not the largest feature); the honeycomb's confirmation sweep runs at the cap on the
  same grid.
- **The over-budget halt for holes and spokes:** first offer a lower `le`; second a
  count-dependent cap from the measured per-cutter cost. For the honeycomb the cap is the
  lever (D-12).
- **Help text:** purpose, datum, `0 = off`, no sizes, no standard; the honeycomb's says the
  count is derived and capped and the cell size may be raised.
- **README:** three feature bullets, ten parameter rows, five derived rows, one example
  link per pattern the tests run.
- **`bore_clearance`:** not added to any cutout dimension.

### Deferred Ideas (OUT OF SCOPE)

- A rotation/phase field for arms and holes (`spoke_angle`/`hole_angle`).
- Corner fillets on honeycomb cells or on holes.
- Lightening holes between spoke arms on one part (REQ-hole-spoke-combination, Future).
- A teeth/module-dependent honeycomb cap.
- Clipped boundary cells.
- Separate honeycomb boundary-wall fields.
- Conditional form fields ("disabled when").
- Analytic corner arcs as a general cutter helper (beyond this phase's spoke use).
- The composition matrix and combined heaviest measurement (Phase 12).
- More than one pattern per part.
- A rotation/phase field for arms or holes.
- Any sizing guidance in cutout help text (no standard exists).

</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| REQ-spoke-cutout | User can cut spoke arms via `spoke_count`/`spoke_width`/`hub_d`/`rim_wall` (+ `spoke_fillet`, D-21 amendment) — N straight arms between a hub ring and a rim ring, sectors cut through the full face width | `_fillet_corner` (model.py:96-113) generalizes to sector corners (mirrored for rim, see Pattern 2); `_ring`-style annulus construction (model.py:271-273) generalizes to the hub/rim annulus; datum verified via `bore_mouth_limit`/`recess_radii` (calc.py:151-197) |
| REQ-hole-cutout | User can cut lightening holes via `hole_count`/`hole_d`/`hole_circle_d` — N equal round holes on a bolt circle, through the full face width | `Workplane.polarArray` signature verified this session on installed cadquery 2.8.0; `Shape.cut(*toCut)` variadic signature verified this session |
| REQ-honeycomb-cutout | User can cut a honeycomb web via `hex_cell`/`hex_wall`; count derived, capped, reported; cell size raised when count exceeds the cap, never silently dropped, analytic (reproducible) cap | `Workplane.polygon(6, d, circumscribed=True)` orientation (flats ±X) verified numerically this session, matching the existing hex-bore code's own comment (model.py:202-205); no honeycomb library primitive exists in cadquery 2.8.0 (grep confirmed, prior STACK.md research) — plain lattice trigonometry is correct, not a library gap |
| REQ-one-cutout-pattern | Exactly one of `spoke_count`/`hole_count`/`hex_cell` may be non-zero — 422 naming both otherwise | `calc.check()`'s existing `("message", ("field", ...))` 422 shape (calc.py:283-420) is the pattern to extend |
| REQ-cutout-conflicts-refused-early | Hub/rim/neighbour breaches refused in `calc.py` before any CAD work — 422/exit 2, fields named | `check()`'s existing if/elif non-stacking shape and `bore_mouth_limit`/`recess_radii` datums (calc.py:151-197, 283-420) generalize directly; `GearParams._feasible` validator (params.py:103-113) is the enforcement point, unchanged |
| REQ-cutout-composes | Cuts through the recessed floor; floor fillet intact on surviving edges; composes with any bore profile | Architecture Q1 (cut order) confirms recess-fillet-first-then-cut-through is already the pipeline's behaviour (verified: `_cut_face_recesses` bakes fillet before any later `.cut()`, model.py:178-196); what a through-cut does to the toroidal fillet face is unverified — flagged for the plan's own kernel probe (Claude's Discretion, not assumed here) |
| REQ-cutout-derived-numbers | `DerivedDimensions` reports thinnest hub/rim wall, honeycomb cell count, `null` when off | `DerivedDimensions`'s existing frozen-pydantic-model + `unit: mm` + rounded-once-at-construction shape (calc.py:432-513, 615-652) is the pattern to extend |

</phase_requirements>

## Summary

Phase 11 is the third additive cut family and the first that subtracts **many** small
solids from the gear body in one boolean pass rather than one or two. Nothing in this
phase needs a new dependency: `cadquery==2.8.0` (already pinned) exposes every primitive
required — `Workplane.polygon(6, d, circumscribed=True)` for the honeycomb cells (the same
call the hex bore already uses, confirmed numerically this session to put flats on ±X),
`Workplane.polarArray` for the lightening-hole bolt circle, and `Shape.cut(*toCut)`
(variadic, confirmed on the installed library) to batch every cutter of one pattern into
one `BRepAlgoAPI_Cut`, never a loop. The spoke arm's rounded corners reuse
`_fillet_corner`'s exact tangent-arc maths already in `model.py` (a line against an
axis-centred circle) with a mirrored construction for the rim-side corners — an analytic
2D-wire fillet, not OCCT's 3D fillet operator, following L09's already-proven remedy for
per-edge fillet cost on a many-featured outline.

The architecturally significant fact this research adds to CONTEXT.md's already-locked
design: the existing pipeline's ordering guarantee (`_cut_face_recesses` bakes the recess
floor fillet as real OCCT geometry **before** `_cut_bore`, `_cut_keyway`, or any new
`_cut_body` step runs) already gives REQ-cutout-composes its "floor fillet survives" half
for free by construction — every downstream cut already subtracts from a solid whose
fillet is baked geometry, exactly as `_cut_bore`'s hole already does today. What is
**not** free, and not yet measured on the pinned kernel, is what a through-cut does to a
toroidal fillet face at the topological level (whether OCCT splits it into per-cutter
pieces or trims one face) — this is exactly the kind of "measured on the pinned kernel,
not derived" item CONTEXT.md's Claude's Discretion assigns to the plan, and this research
does not pre-empt it with an unverified claim.

The honeycomb's cell-count cap is the phase's one open, high-stakes number. CONTEXT.md
already assigns its measurement to the plan's first task (a dedicated, measurement-only
spike, D-24) — this research does not invent or estimate `HEX_CELL_CAP`. What this
research contributes instead: (1) confirmation that `cut(*cutters)` scales in the right
direction (a toy, non-representative probe run this session: 10/50/100/300 non-overlapping
cylinder cutters against a plain block took 0.04/0.12/0.21/0.57 s — illustrative only,
**not** a substitute for the phase's own spike against the real 200-tooth/module-10 gear
with recesses, which has far more baseline topology and a much larger single boolean
target); (2) the exact hexagon-lattice geometry (`hex_cell / √3` corner reach, pitch
`hex_cell + hex_wall`, flats on ±X) is dimensionally consistent with the existing hex-bore
construction, so no new orientation convention is introduced.

**Primary recommendation:** build all three cutout patterns as pure-`calc.py` geometry
(cutter positions, the cap/count functions, all refusals) feeding a single new `model.py`
step (`_cut_body`, between `_cut_keyway` and `_chamfer_tips`) that constructs N cutter
solids per pattern and calls `solid.cut(*cutters)` exactly once per pattern — never a
per-cutter loop, never an OCCT fillet operator for the spoke corners.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Cutout field validation (spoke/hole/hex ranges, conflicts, half-set) | API/Backend (`calc.py`) | — | Pure math, no kernel; `calc.py` never imports cadquery (import-linter enforced); one validation at the `GearParams` boundary (`params.py` `_feasible`) |
| Hub/rim/neighbour clearance refusals (422) | API/Backend (`calc.py`) | — | Must run before any CAD work (REQ-cutout-conflicts-refused-early); mirrors `recess_radii()`'s existing datum-reading pattern |
| Honeycomb lattice enumeration + cap | API/Backend (`calc.py`) | — | Runs on every keystroke (`derive()`'s existing perf contract, ~11.5 µs today); must stay kernel-free so the same link yields the same count on every machine (D-13, analytic reproducibility) |
| Cutter solid construction (sector wires, hole cylinders, hex prisms) | CAD Kernel (`model.py`) | — | The only doorway to `cadquery`/OCP (module docstring); vendor types stop at this boundary |
| Boolean subtraction (`cut(*cutters)`) | CAD Kernel (`model.py`) | — | OCCT `BRepAlgoAPI_Cut`; batched per pattern, not looped |
| Derived numbers (thinnest wall, cell count, effective sizes) | API/Backend (`calc.py`) | — | `DerivedDimensions` is the one document `/api/info`, `spur info` and the web UI all print; part and printed number read the same function (L08) |
| Web form fieldsets, CLI flags, shareable-URL round-trip | Frontend Server (schema-driven) | Browser (`app.js` DIMS/group renderer) | Falls out of `GearParams`' field metadata automatically (L02); `app.js`'s existing group-keyed renderer (`static/app.js:45-56`) needs zero code change beyond `DIMS` rows |
| Build-time measurement (sweeps, cap derivation) | Database/Storage (bench artefacts) | API/Backend (`calc.py` constants informed by it) | `bench/build_time.py`'s `worst_request` against `SPUR_BUILD_TIMEOUT`; a measured constant lands in `calc.py`, never a live clock check (Pitfall 5) |

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| cadquery | 2.8.0 [VERIFIED: `.venv/lib/python3.12/site-packages/cadquery-2.8.0.dist-info`, checked this session] | Solid modeling (`Workplane`, `Shape`, `Mixin3D`) | Already the sole CAD layer (L01); `polygon`, `polarArray`, variadic `cut` cover every primitive this phase needs |
| cadquery-ocp | 7.9.3.1.1 [VERIFIED: same dist-info check] | OCCT kernel bindings | Boolean cut is an OCCT operator reached through `Shape.cut`; no direct OCP call needed |

### Supporting

No new supporting library. `math` (stdlib) is sufficient for the hexagonal lattice's
row/column offset arithmetic — the same idiom `_polar()` already uses in `model.py`.

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Plain-trig hexagonal lattice enumeration in `calc.py` | A geometry/tessellation library (`shapely`, etc.) | Not needed — the lattice is a fixed regular pattern, not arbitrary polygon packing; a new dependency for zero new capability |
| `cut(*cutters)` (variadic, one call) | A loop of `.cut()` calls, one per cutter | Never — confirmed variadic on installed `cadquery==2.8.0`; a loop rebuilds the growing solid N times for no benefit (Pitfall 2, prior research) |
| Analytic 2D tangent-arc fillet for spoke corners | `Mixin3D.fillet()` on the 4N vertical corner edges | Rejected by D-05: L09's ~50× cost family, a new selector, a new matrix column, a new tripwire — for geometry the 2D-wire approach already produces exactly |

**Installation:** none — no new package, no version bump, no `requirements.txt`
regeneration for anything in this phase.

**Version verification:**
```
$ .venv/bin/python -c "import cadquery; print(cadquery.__version__)"
2.8.0
```
Confirmed against the pinned `requirements.txt`/`pyproject.toml` range this session — not
stale training-data versions.

## Package Legitimacy Audit

**Not applicable this phase.** No new external package is introduced; `cadquery`/
`cadquery-ocp` are the pre-existing, already-audited pins from v0.1/v0.2 phases 8-10. No
`npm view`/`pip index versions`/registry check is needed because nothing new is installed.

## Architecture Patterns

### System Architecture Diagram

```
GearParams (params.py)
  Spokes group: spoke_count, spoke_width, hub_d, rim_wall, spoke_fillet   (all 0=off)
  Holes group:  hole_count, hole_d, hole_circle_d                         (all 0=off)
  Honeycomb group: hex_cell, hex_wall                                     (all 0=off)
        │  model_validator -> calc.check()
        ▼
calc.py  check(p)                              -- BEFORE any CAD work
  ├─ exactly-one-pattern rule (REQ-one-cutout-pattern)
  ├─ half-set rule per pattern (D-15)
  ├─ hub/rim breach rules, reading bore_mouth_limit(p) / rf (D-17)
  ├─ neighbour-spacing rule (holes: bolt-circle arc; spokes: hub opening) (D-16)
  ├─ hex_wall < MIN_WALL rule (D-10)
  └─ honeycomb-empty rule (D-14)
        │  (only if no errors)
        ▼
calc.py  derive(p)                              -- pure math, every keystroke
  ├─ hex lattice enumeration + HEX_CELL_CAP raise-to-fit (D-13)
  ├─ spoke_fillet cap (0.45 x shared dimension) (D-06)
  ├─ five new DerivedDimensions fields (D-20)
  └─ warnings: ignored-dimension, capped-fillet, raised-cell-size
        │
        ▼
model.py  _build(p):
    _gear_blank -> _cut_face_recesses (floor fillet BAKED as real geometry here)
      -> _cut_bore -> _cut_keyway
      -> _cut_body(solid, p)          <-- NEW, one step, one .cut(*cutters) per pattern
           ├─ spokes: N closed 2D wires (_fillet_corner + its rim mirror) -> faces -> prisms
           ├─ holes: N cylinders via polarArray or explicit centres
           └─ honeycomb: N hex prisms at lattice centres (from calc's enumeration)
      -> _chamfer_tips (last, unaffected by body cutouts)
        │
        ▼
bench/build_time.py  -- per-pattern sweep, worst_request vs SPUR_BUILD_TIMEOUT=30s
```

### Recommended Project Structure

No new files beyond bench sweeps and their own test module additions — this phase extends
the existing three-file shape:

```
src/spur/
├── params.py     # +3 field groups (Spokes, Holes, Honeycomb), after Recess (D-19)
├── calc.py       # +cap/count/wall functions (siblings of recess_radii/tip_chamfer_limit),
│                 #  +check() rules, +5 DerivedDimensions fields, +warnings
├── model.py      # +_cut_body() and its three cutter builders; _build() gains one line
└── static/app.js # +5 DIMS rows only (group renderer is schema-driven, no other change)
bench/
├── sweeps/hole_cutout.json / spoke_cutout.json / honeycomb.json   # new
└── build_time.py                                                  # reused unchanged
```

### Pattern 1: Batched boolean cut of many small cutters — never a loop

**What:** Build every cutter solid for one pattern into a Python list, then call
`solid.cut(*cutters)` exactly once.
**When to use:** Any pattern with N > 1 non-overlapping (by construction) cutters —
holes, spoke gaps, honeycomb cells.
**Verified this session** (installed `cadquery==2.8.0`):
```python
# Source: .venv/lib/python3.12/site-packages/cadquery/occ_impl/shapes.py, read via inspect
# Shape.cut(self, *toCut: 'Shape', tol: 'float | None' = None) -> 'Shape'
cutters = [cq.Workplane("XY").center(x, y).circle(r).extrude(face_width).val()
           for (x, y) in centres]
solid = solid.cut(*cutters)          # one BRepAlgoAPI_Cut, not N
```
A toy, non-representative timing probe run this session (10 CPU host, not the phase's
real geometry) against a plain block:

| Cutters | `cut(*cutters)` wall time |
|---|---|
| 10 | 0.041 s |
| 50 | 0.120 s |
| 100 | 0.214 s |
| 300 | 0.574 s |

`[VERIFIED: this session, .venv/bin/python probe against a bare box — illustrative
scaling shape only]`. This is **not** the phase's honeycomb spike: the real gear has a
far larger baseline topology (200+ teeth, root fillets, recesses) and the honeycomb's
worst case is capped in the hundreds, not 300 identical simple cylinders in empty space.
D-24's spike must run against the actual 200-tooth/module-10/both-recesses configuration.

### Pattern 2: Mirrored analytic tangent-arc fillet (spoke corners)

**What:** `_fillet_corner(p0, p1, rf, rho, gap_side)` (model.py:96-113) computes a tangent
arc between an axis-centred circle of radius `rf` and a line through `p0` (on that
circle) toward `p1`, returning `(on_root, mid, on_line)`. It is used today for the tooth
root fillet, where the arc centre sits **outside** the root circle (`centre = q + u*t`
with `|centre| = rf + rho`).
**When to use:** Any place a straight edge meets an axis-centred circular boundary and
needs a tangent arc, without OCCT's 3D fillet operator.
**Read this session** (verbatim, `model.py:96-113`):
```python
def _fillet_corner(p0: cq.Vector, p1: cq.Vector, rf: float, rho: float,
                   gap_side: int) -> tuple[cq.Vector, cq.Vector, cq.Vector]:
    """Fillet of radius rho between the root circle (radius rf, centred on the axis)
    and the flank line p0 -> p1, where p0 lies on the root circle. ...
    Returns (tangent point on root circle, arc midpoint, tangent point on line)."""
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
**D-05's stated mirror requirement** for the rim-side corners: the arc centre must sit
**inside** the rim circle (at `rf − rim_wall − ρ` rather than `hub_d/2 + ρ`), i.e.
`|centre| = R − rho` instead of `|centre| = R + rho` — a sign flip in the quadratic term
`(q.dot(q) - (R - rho) ** 2)` (or an equivalent `gap_side`/radius-offset inversion). This
was **not** built or timed on the pinned kernel this session (D-05 explicitly rejected
spending spike time on it — "the planner can probe the analytic arcs on the pinned kernel
in minutes"); flagged here as the one piece of new geometry math in this phase with no
prior in-tree precedent for the "centre inside the circle" case, so the plan's first
implementation pass should sanity-check the mirrored sign algebraically (e.g. against a
hand-computed 3-4-5 or similar tangent case) before trusting it at every sector.

### Pattern 3: Hexagon construction reused verbatim from the hex bore

**What:** `polygon(6, hex_cell, circumscribed=True)` — same call, same orientation
convention, as `_cut_bore`'s existing hex-bore construction.
**Verified numerically this session** (installed cadquery 2.8.0):
```
w = cq.Workplane("XY").polygon(6, 4.0, circumscribed=True)
bb = w.val().BoundingBox()
bb.xlen  # == 4.0   (across-flats, the diameter argument)
bb.ylen  # == 4.618802153517006  (across-corners, == 4.0 / sqrt(3) * 2)
```
Confirms `model.py`'s own comment (line 202-205, read this session): "circumscribed=True
makes the polygon's diameter argument the across-flats... the kernel's default puts a
flat facing +X... with a vertex on ±Y, and there is no rotation parameter." D-08's lattice
convention (flats on ±X) is the same orientation, so honeycomb cells need no new rotation
handling.

**Corner reach** (used by D-07's whole-cell test): for a regular hexagon built
`circumscribed=True` with across-flats `hex_cell`, the circumradius (centre-to-vertex,
i.e. the farthest a cell's material reaches from its own centre) is `hex_cell / sqrt(3)`
— the same formula `bore_rim_limit(p)`'s hex branch already uses and that this session's
numerical check confirms (`ylen / 2 == 4.618802.../2 == 2.309... == 4.0/sqrt(3)`).

### Anti-Patterns to Avoid

- **A loop of `.cut()` calls per cutter:** rebuilds the growing solid N times; use the
  variadic `cut(*cutters)` (Pattern 1).
- **OCCT's 3D `.fillet()` on the sector corner edges:** L09's ~50× cost family on a
  many-instance feature; use the 2D analytic-arc wire instead (Pattern 2, D-05).
- **A clock-based honeycomb cap** ("keep cutting cells until N seconds pass"):
  non-reproducible across machines, explicitly rejected by REQ-honeycomb-cutout and by
  the Out of Scope table; the cap must be one measured constant compared analytically,
  before any cell is cut (D-12).
- **Exact off-grid cell-size search** (e.g. bisecting to a value like `2.3417 mm`): D-13
  rejects this explicitly — the step is the field's own 0.05 mm, so the raised size is
  always a value the user could have typed.
- **A position selector for the cutout rim edges:** not needed this phase — the recess
  floor and bore rim selectors (`_groove_floor_edges`, `_bore_rim_edges`) already run
  *before* `_cut_body` in the pipeline and are unaffected by it (Q1's ordering argument);
  only `_tip_edges` runs after cutouts and its own selector logic (CIRCLE at `ra` on an
  end face) cannot be confused by any cutout edge, since no cutout reaches `ra` (D-17's
  bounds keep every cutout inside the rim wall).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|--------------|-----|
| Batching N boolean subtractions | A sequential `.cut()` loop, or a hand-written multi-tool OCCT call | `Shape.cut(*toCut)` (already variadic on the installed library) | Confirmed via `inspect.signature` this session; OCCT's own multi-argument boolean is documented as faster than N sequential calls (prior PITFALLS.md research, Pitfall 2) |
| Hexagonal lattice tiling | A geometry/tessellation library (`shapely`) or manual `rarray` offset-row hacking | Plain trigonometry in `calc.py` (row/column formula), same idiom as `_polar()` | No honeycomb primitive exists in cadquery 2.8.0 (confirmed by grep in prior STACK.md research); the lattice is a fixed regular pattern, not arbitrary packing |
| Rounded sector corners | OCCT's `Mixin3D.fillet()` on the built solid's vertical edges | Analytic 2D tangent-arc wire construction (`_fillet_corner` + its rim mirror), extruded | L09: OCCT's fillet operator measured ~50× slower on a many-featured outline; the fillet becomes baked 2D geometry before extrusion, at negligible marginal cost |
| Honeycomb cell-count cap | A live build-time clock check that stops cutting cells when a timer expires | One measured constant (`HEX_CELL_CAP`) compared analytically before any CAD call | A clock-based stop makes the same link produce a different part on different hardware — violates L05/L08's reproducibility guarantee; explicitly rejected in REQ-honeycomb-cutout and the Out of Scope table |

**Key insight:** every "don't hand-roll" item in this phase already has a working
precedent somewhere else in this exact codebase (`_fillet_corner` for tangent arcs,
`recess_radii`/`root_fillet` for the cap-and-warn contract, `_cut_bore`'s hex polygon for
orientation) — the phase is disciplined reuse of proven patterns at a larger cutter count,
not new invention.

## Common Pitfalls

### Pitfall 1: Position-based selectors must be re-proven, not assumed, after new topology

**What goes wrong:** `_groove_floor_edges`'s own docstring (read this session,
model.py:276-296) already states: "Phase 11's cutouts put new circles on the recessed
floor and must re-prove this separating invariant." A cutout's cutter can put new
`CIRCLE`-geometry edges at the recess floor's own radii (a hole tangent to `r_in`/`r_out`,
a honeycomb cell corner near the boundary) or at heights matching the floor `z`, which the
existing floor-edge filter (`radius within TOL of a groove radius` AND `z within TOL of a
floor height`) could then wrongly match.
**Why it happens:** The selector's separating invariant ("the only other edges near this
radius/height belong to a recess") was true when only bore + recess existed; it is a
claim about the *current* feature set, not a permanent property.
**How to avoid:** Re-run (or extend) the selector-matrix test with every cutout pattern
present, at boundary-adjacent sizes (a hole/cell one step either side of `r_in`/`r_out`),
and assert both the *count* and the *identity* (radius/z-band) of matched edges, not just
that the build succeeds — the matrix test pattern (`test_each_edge_selector_picks_exactly_
its_own_edges`, tests/test_model.py:134+) already does this for bore/recess; extend its
parametrization to include each cutout pattern.
**Warning signs:** A recess-floor-fillet survival test that passes only because the
cutout happens not to reach the boundary in the test fixture, not because the selector
was re-proven at the boundary.

### Pitfall 2: Tangent/coincident cutter faces are a reachable, legitimate case here — unlike Phases 8-10

**What goes wrong:** Unlike the bore/recess/keyway phases (where tangency was mostly
avoidable by construction), CONTEXT.md's own Claude's Discretion section names this
directly: "a hole or a cell can legitimately sit tangent to a recess wall... or to nothing
at all — unlike Phases 8-10, tangency is reachable here." A hole whose edge sits exactly
on `bore_mouth_limit(p) + MIN_WALL` (the D-17 boundary itself) or a honeycomb cell corner
exactly on the annulus boundary can produce a near-zero-thickness sliver for OCCT's
boolean solver.
**Why it happens:** The refusal rules in `check()` use `<` (strict), not `<=`, so a
parameter set exactly at the boundary is accepted, and "exactly at the boundary" is
precisely where a cutter face becomes tangent to the material it is cutting into.
**How to avoid:** Per CONTEXT.md's Claude's Discretion, probe the pinned kernel at the
tangent cases (a hole edge exactly on `r_in`/`r_out`, a cell corner on a boundary, a bar
side crossing a wall) before deciding whether `tol=` (confirmed present on the installed
`Shape.cut` this session: `tol: 'float | None' = None`) is needed, and ship it only with
the measurement and its own comment — never guessed.
**Warning signs:** `BuildError` from the catch-all on a parameter set that is not a
documented conflict; a solid that reports `isValid()` true but more than one piece in
`Solids()`.

### Pitfall 3: The honeycomb count must be enumerated cheaply — no exact search over millions of cells

**What goes wrong:** At the phase's own worked example (200 teeth, module 10, D-11's
config), the web annulus area is ~3.06 × 10⁶ mm² and a 3 mm cell with a 1 mm wall implies
roughly 2.2 × 10⁵ candidate cells before any cap is applied — enumerating each one
exactly (constructing its solid, testing containment) to find the count would itself be
slow enough to threaten the very budget the cap exists to protect.
**Why it happens:** The straightforward implementation of D-07's "whole cells only" rule
is to enumerate every lattice point and test it — correct, but with the wrong asymptotic
cost when the lattice is fine and the gear is large.
**How to avoid:** D-13 already specifies the fix: use an area estimate (annulus area /
pitch-hexagon area) to decide whether the exact enumeration would exceed the cap *before*
running it, and only enumerate exactly (fast, since the exact test is a single
radius-band containment check on each lattice point's centre) once the estimate is inside
a range the cap search can afford.
**Warning signs:** `derive()`'s own per-call cost (currently ~11.5 µs, measured 09-05)
growing enough to threaten its "fast enough for every keystroke" contract — CONTEXT.md's
Claude's Discretion explicitly asks for this to be measured and recorded in the docstring.

### Pitfall 4: `spoke_fillet`'s cap formula shares two different "shared dimensions" — get the hub-opening measure right

**What goes wrong:** D-06's cap is `0.45 × min(hub-ring opening between adjacent bars,
annulus width)`. The annulus width (`rf − rim_wall − hub_d/2`) is a simple subtraction,
already how `recess_radii`/`root_fillet` express their own caps. The **hub-ring opening**
is not a simple subtraction — it is either an arc length or a chord between the feet of
adjacent bar sides on the hub circle, and CONTEXT.md explicitly flags this as unresolved:
"the exact measure... is the planner's — `keyway_flat_wall`'s arc measure is the
precedent."
**Why it happens:** Unlike the annulus width (radial, one axis), the hub opening is a
circumferential measure between two bar feet on a circle of nonzero radius — getting the
formula wrong (using a chord where an arc was intended, or vice versa) changes the cap's
value at high `spoke_count`, where the two measures diverge most.
**How to avoid:** Follow the cited precedent — `keyway_flat_wall` (calc.py:117-130) is
the in-tree example of measuring an arc between two features' feet on a circle
(`r * (math.acos(...) - math.acos(...))`); the spoke hub-opening measure should follow
the same shape (an arc on the hub circle between adjacent bar-side feet), not a straight
chord, for consistency with the rest of the file's "what a caliper reads" philosophy
(chord for radial calipers, arc for a wrap-around measure) — though the exact choice is
explicitly left to the planner and should be recorded with its rationale, since no
existing test pins it.
**Warning signs:** A `spoke_fillet_effective` that looks "too generous" or "too
conservative" at `spoke_count` near 200 (where the hub-ring circumference is finely
divided) compared to `spoke_count` near 1.

### Pitfall 5: The `_cut_body` step's position in `_build()` interacts with `_bore_rim_edges` and `_tip_edges`, not just `_groove_floor_edges`

**What goes wrong:** CONTEXT.md places the new step between `_cut_keyway` and
`_chamfer_tips` — after every selector that runs *before* it (`_groove_floor_edges` inside
`_cut_face_recesses`, `_bore_rim_edges` inside `_cut_bore`) has already completed and
baked its operator's result into the solid, and before the one selector that runs *after*
it (`_tip_edges`, inside `_chamfer_tips`). Read this session, `_tip_edges` (model.py:332-
357) selects `CIRCLE` edges at radius `ra` with both endpoints on an end face — D-17's
own bounds (rim wall `rf − MIN_WALL`, always strictly inside `ra`) mean no cutout edge can
ever reach `ra`, so `_tip_edges` cannot be confused by a cutout's own edges. This is a
reassuring confirmation, not a new invariant to build — but it is exactly the kind of
claim Pitfall 4 (prior PITFALLS.md research) warns must be *re-checked*, not just assumed,
whenever new end-face topology is added, so the selector-matrix test (Claude's
Discretion) should include a row that asserts `_tip_edges` still returns exactly `2 x
teeth` edges with every cutout pattern active.
**Warning signs:** A cutout parameter set at the extreme allowed `rim_wall` (near
`MIN_WALL`, i.e. as close to `ra` as D-17 permits) is the boundary case to include in that
matrix row, not just a comfortable mid-range configuration.

## Code Examples

### The existing cap-and-warn contract (D-06/D-13 must follow this shape exactly)

```python
# Source: src/spur/calc.py:213-217, read this session
def root_fillet(p: GearParams) -> float:
    """Root fillet actually used: the requested radius, capped to what fits the gap."""
    _, _, gap = _tooth(profile(p))
    return round(min(p.root_fillet, 0.45 * gap), 3) if gap > 0 else 0.0
```
```python
# Source: src/spur/calc.py:540-542, read this session
rfil = root_fillet(p)
if rfil < p.root_fillet:
    warnings.append(f"Root fillet reduced to {rfil:.2f} mm to fit the tooth gap.")
```
`spoke_fillet_effective` and `hex_cell_effective`/`hex_cell_count` must follow this exact
"applied-value function in `calc.py`, `derive()` compares and warns" shape — never a
warning computed from a different code path than the one `model.py` actually cuts (L08:
"the part and the number cannot disagree").

### The existing 422-refusal shape (D-16/D-17 must follow this shape exactly)

```python
# Source: src/spur/calc.py:328-333, read this session (hex bore's own root-circle rule)
if bore_rim_limit(p) > pr.rf - MIN_WALL:
    errors.append((
        "Hex bore is too large for the root diameter: its corners "
        f"({2 * bore_rim_limit(p):.2f} mm across) must stay {MIN_WALL:g} mm "
        f"inside the root circle ({2 * pr.rf:.2f} mm); reduce bore_hex.",
        ("bore_hex",)))
```
Every cutout refusal (hub breach, rim breach, neighbour spacing, half-set, one-pattern)
should return the same `(message, (field, ...))` tuple shape into the same `errors` list
`check()` already accumulates and returns — no new error-reporting mechanism.

### The existing `DerivedDimensions` null-when-off field shape

```python
# Source: src/spur/calc.py:462-465, read this session
tip_chamfer_effective: float | None = Field(
    description="Tip chamfer actually cut on the tooth-tip edges at both faces, "
                "after the cap; null with no tip chamfer.",
    json_schema_extra={"unit": "mm"})
```
The five new fields (D-20) should each read this shape: `float | None` or `int | None`,
a `description` stating the null condition explicitly, `unit: mm` on lengths.

### The existing `_f()` field-metadata helper (params.py, D-19's group mechanism)

```python
# Source: src/spur/params.py:17-23, read this session
def _f[T](default: T, ge: float, le: float, *, title: str, group: str,
          unit: str = "", step: float | None = None, help: str = "") -> T:
    extra: JsonDict = {"group": group, "unit": unit}
    if step is not None:
        extra["step"] = step
    return Field(default, ge=ge, le=le, title=title, description=help,
                 json_schema_extra=extra)
```
Every new field in the three new groups is a call to this same helper with
`group="Spokes"` / `"Holes"` / `"Honeycomb"` — no new field-declaration mechanism, and
`app.js`'s group renderer (confirmed this session, `static/app.js:45-56`: `const group =
prop.group ?? 'Other'`) needs no code change to render a third/fourth/fifth fieldset.

### The existing built-solid proof + tripwire pattern

```python
# Source: tests/test_model.py:560-567, 630-645, 648-657, read this session
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
particular) should follow this exact shape: one shared assertion helper, one "proof"
test, one "tripwire" test that monkeypatches the new `_cut_body` step to a no-op and
shows the proof go red while `derive()`'s number still (wrongly) prints — the L08 failure
mode the tripwire exists to catch.

## State of the Art

No externally-facing standard changed since Phase 10; this section is not applicable in
the usual "library upgraded" sense. The one in-project "state of the art" shift this
phase continues is the L09 lineage: OCCT's 3D fillet/chamfer operator is progressively
being replaced, feature by feature, with analytic 2D-wire construction wherever an
operator would touch many similar edges (root fillets → L09; spoke corners → this
phase's D-05). Phase 10's tip chamfer is the one exception in the tree (a 3D `.chamfer()`
call was kept because an analytic tip corner would have changed the meshing profile,
L29) — this phase's spoke fillet does **not** face that constraint (a cutter's corner has
no meshing role), so the analytic route applies cleanly.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | D-05's mirrored `_fillet_corner` construction (arc centre *inside* the rim circle, `\|centre\| = R - rho`) is algebraically sound as a sign-flip of the existing formula | Pattern 2 | If the sign flip is wrong, the rim-side sector corners could produce a self-intersecting or non-tangent wire, caught only at `Wire.assembleEdges`/`Face.makeFromWires` time or by a visibly wrong fillet radius on the built solid — the plan should sanity-check this against a hand-computed case before trusting it broadly |
| A2 | The hub-ring opening between adjacent spoke bars should be measured as an arc (following `keyway_flat_wall`'s precedent), not a chord | Pitfall 4 | If a chord is used where an arc was intended (or vice versa), `spoke_fillet_effective`'s cap diverges from the "true" fit at high `spoke_count`, producing an over- or under-filleted corner that is still capped-and-warned (never unsafe), but not exactly the value CONTEXT.md's Claude's Discretion anticipated |
| A3 | The toy `cut(*cutters)` timing probe (10/50/100/300 cutters against a bare block, 0.04-0.57s) is directionally representative of how boolean cut cost scales with cutter count, but is not a substitute for the phase's own spike against the real gear geometry | Pattern 1 / Summary | If real-geometry scaling is meaningfully worse (e.g. superlinear against a 200-tooth base solid's much larger existing topology), the honeycomb cap derived from an under-scoped extrapolation could be wrong — this is exactly why D-24 requires the spike to run against the actual 200-tooth/module-10/both-recesses configuration, not this toy probe |
| A4 | What OCCT does to a toroidal recess-floor fillet face when a through-cut crosses it (splits into per-cutter pieces vs. trims one face) was not measured this session | REQ-cutout-composes support row, Summary | If the fillet face is destroyed rather than split/trimmed cleanly, the "floor fillet intact on surviving edges" proof (REQ-cutout-composes) could fail in a way that needs a different cut ordering or a `tol=` adjustment — CONTEXT.md already assigns this measurement to the plan (Claude's Discretion), so the risk is scoped, not open-ended |

## Open Questions

1. **Exact hub-ring opening measure for `spoke_fillet`'s cap (D-06)**
   - What we know: `keyway_flat_wall` is the cited precedent for an arc-based measure
     between two features' feet on a circle; the annulus-width half of the cap is a
     simple radial subtraction.
   - What's unclear: whether an arc or a chord is the intended measure, and the exact
     formula for the feet of adjacent bar sides on the hub circle given `spoke_width` and
     `spoke_count`.
   - Recommendation: derive the arc formula analogous to `keyway_flat_wall`'s shape
     (`r * (acos(...) - acos(...))`), record the choice and its rationale in the
     function's docstring per this project's comment convention, and pin it with a test
     at a boundary `spoke_count` (e.g. 200) and a small one (e.g. 2).

2. **The mirrored `_fillet_corner` construction for rim-side corners (D-05)**
   - What we know: the existing function's arc centre sits *outside* the root circle
     (`|centre| = rf + rho`); D-05 states the rim mirror needs the centre *inside*
     (`|centre| = R - rho`).
   - What's unclear: whether this is a clean sign flip of the existing quadratic, or
     needs a structurally different `gap_side`/orientation convention to stay tangent
     correctly on the concave side of the boundary.
   - Recommendation: prototype both corner types (hub and rim) against a hand-picked
     simple case (e.g. a 90° sector) and confirm tangency numerically (arc endpoint
     matches line direction) before generalizing to N sectors — a small, cheap probe, not
     a timed spike (D-05 already rejects timing it).

3. **Honeycomb enumeration performance at the cap (Claude's Discretion, "measure
   `derive()`'s cost at the cap")**
   - What we know: `derive()` currently costs ~11.5 µs per call (09-05, "fast enough to
     run on every keystroke" contract); the area-estimate-then-exact-enumerate approach
     (D-13) should keep this cheap even at hundreds of cells.
   - What's unclear: the actual measured cost once the enumeration function exists.
   - Recommendation: measure with `.venv/bin/python -m timeit` the same way 09-05 already
     did, and record the number in the enumeration function's docstring — the project's
     own established convention for this class of claim.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| cadquery | All cutter construction and boolean cuts | ✓ [VERIFIED: this session] | 2.8.0 | — |
| cadquery-ocp | OCCT kernel bindings | ✓ [VERIFIED: this session] | 7.9.3.1.1 | — |
| Python | Runtime | ✓ [VERIFIED: this session, `.venv/bin/python --version` implied by dist-info paths] | 3.12 (L23 floor) | — |
| pytest | Test suite | ✓ [VERIFIED: pyproject.toml `[tool.pytest.ini_options]`, read this session] | ≥8 (pinned range) | — |

No missing dependencies. This phase adds no new external tool, service, or package —
every primitive is already installed and pinned.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest ≥8 [VERIFIED: pyproject.toml, read this session] |
| Config file | `pyproject.toml` `[tool.pytest.ini_options]` |
| Quick run command | `.venv/bin/python -m pytest tests/test_calc.py -x` (pure-math rules, no kernel — seconds) |
| Full suite command | `make verify` (ruff + mypy --strict + import-linter + no-fake-done + full pytest, ~100 s warm at 453 tests as of Phase 10) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| REQ-spoke-cutout | N spoke sectors cut, correct hub/rim/fillet geometry | unit + built-solid | `pytest tests/test_model.py -k spoke -x` | ❌ Wave 0 |
| REQ-hole-cutout | N holes on bolt circle, evenly spaced, hole 0 on +X | unit + built-solid | `pytest tests/test_model.py -k hole -x` | ❌ Wave 0 |
| REQ-honeycomb-cutout | Whole-cell lattice, count derived and capped, size raised when needed | unit (calc) + built-solid | `pytest tests/test_calc.py tests/test_model.py -k hex -x` | ❌ Wave 0 |
| REQ-one-cutout-pattern | Two/three non-zero selectors → 422 naming both | unit (422-naming shape) | `pytest tests/test_calc.py -k cutout_pattern -x` | ❌ Wave 0 |
| REQ-cutout-conflicts-refused-early | Hub/rim/neighbour breach → 422 before CAD | unit (calc-only, no kernel) | `pytest tests/test_calc.py -k cutout -x` | ❌ Wave 0 |
| REQ-cutout-composes | Fillet survives, composes with every bore shape | built-solid + selector matrix | `pytest tests/test_model.py -k "cutout and compose" -x` | ❌ Wave 0 |
| REQ-cutout-derived-numbers | Five new `DerivedDimensions` fields, `null` when off | unit (calc) | `pytest tests/test_calc.py -k derived -x` | ❌ Wave 0 |
| REQ-defaults-off-regression | Pre-v0.2 fixture byte-unchanged; new fields `null` | regression | `pytest tests/regression/test_pre_v0_2.py -x` | ✅ (existing, `tests/regression/`) |
| REQ-measured-build-time | Per-pattern sweep, honeycomb cap sweep, inside 30 s | bench (not `make verify`) | `make bench.build SWEEP=bench/sweeps/<pattern>.json` | ❌ Wave 0 (new sweep JSON files) |

### Sampling Rate

- **Per task commit:** `.venv/bin/python -m pytest tests/test_calc.py tests/test_model.py -x` (fast, kernel-touching but no bench sweep)
- **Per wave merge:** `make verify` (full gate)
- **Phase gate:** Full suite green before `/gsd-verify-work`; `make bench.build` sweeps run separately (not part of `make verify`, per `bench/build_time.py`'s own docstring: "a sweep at 200 teeth takes about a minute and a half... not part of `make verify`")

### Wave 0 Gaps

- [ ] New parametrized rows in `tests/test_model.py`'s selector matrix (`test_each_edge_
      selector_picks_exactly_its_own_edges`) for each cutout pattern × bore shape × recess
      setting
- [ ] New built-solid proof + tripwire pair per pattern (following `_assert_only_the_tip_
      arcs_were_chamfered`'s shape)
- [ ] New 422-naming tests per refusal rule (D-10, D-14 through D-17) in `tests/test_calc.py`
- [ ] New cap-and-warn tests per D-06/D-13 (following `test_a_tip_chamfer_is_capped_to_
      whichever_limit_binds_first`'s shape)
- [ ] `bench/sweeps/hole_cutout.json`, `spoke_cutout.json`, `honeycomb.json` — new sweep
      files (`bench/build_time.py` itself is reused unchanged)
- [ ] The honeycomb spike script (D-24, measurement-only, no field) — a probe path that
      cuts N whole cells at 200 teeth/module 10/both recesses and times it, producing the
      numbers `HEX_CELL_CAP` is derived from

*(No framework install needed — pytest and its plugins are already pinned and present.)*

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | This tool has no auth surface (single-user CAD generator) |
| V3 Session Management | no | Stateless request/response, no sessions |
| V4 Access Control | no | No access-control surface |
| V5 Input Validation | yes | Pydantic v2 `Field(ge=, le=)` bounds on every new field (existing `_f()` helper); `calc.check()`'s 422-refusal contract for cross-field conflicts; no user input reaches the CAD kernel unvalidated (`GearParams._feasible` model_validator is the single choke point, unchanged) |
| V6 Cryptography | no | No cryptographic operation anywhere in this tool |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Resource exhaustion via an unbounded/expensive cutout request (e.g. a huge `hex_cell_count`, or `spoke_count`/`hole_count` at 200 with tiny features) | Denial of Service | `SPUR_BUILD_TIMEOUT` (already enforced per worker request, `app.py`); the honeycomb's analytic cap (D-12) exists specifically to bound this class of request before any CAD call; `spoke_count`/`hole_count`'s `le=200` bound (D-18) is itself a DoS-shaped ceiling, not just a design ceiling |
| Malformed/adversarial float input landing in an unreachable float-residue band (precedent: `ROOT_CONTACT`'s documented residual band, calc.py:18-38) | Tampering (of derived numbers vs. built part) | Every new cap/refusal function rounds at 3 dp at construction and compares at that resolution (the existing `r3()` convention in `derive()`), following the precedent that already closed this class of bug for `tip_chamfer_effective` (10-REVIEW.md WR-01/CR-01) |
| A cutout parameter set that builds an `isValid()` solid with a hidden sliver/degenerate face (silent geometric corruption) | Tampering (silent) | The built-solid proof + tripwire pattern (REQ-cutout-composes) catches this class at the test level; `_build()`'s existing `len(solids) != 1 or not solids[0].isValid()` guard (model.py:370-372) catches it at the pipeline level, unchanged by this phase |

## Sources

### Primary (HIGH confidence)

- `.venv/lib/python3.12/site-packages/cadquery/cq.py`, `.venv/lib/python3.12/site-
  packages/cadquery/occ_impl/shapes.py` (installed cadquery 2.8.0) — `Workplane.polygon`,
  `.polarArray`, `.rarray`, `Solid.makeBox`, `Shape.cut` signatures, read via
  `inspect.signature` this session.
- Numeric checks run this session in this repo's `.venv`: hex polygon bounding-box
  (across-flats/across-corners), toy `cut(*cutters)` scaling probe (10/50/100/300
  cutters).
- `src/spur/model.py`, `src/spur/calc.py`, `src/spur/params.py` (full files read this
  session) — every cited line number and verbatim quote above is from this session's
  read, not from memory.
- `tests/test_model.py`, `tests/test_calc.py` (relevant sections read this session) —
  matrix test, built-solid proof + tripwire, 422-naming test, cap-and-warn test shapes.
- `src/spur/static/app.js` (relevant sections read this session) — `DIMS` array and
  group-keyed form renderer.
- `pyproject.toml`, `Makefile` (relevant sections read this session) — pytest config,
  `make verify`/`make bench.build` targets.

### Secondary (MEDIUM confidence)

- `.planning/research/STACK.md`, `.planning/research/PITFALLS.md`,
  `.planning/research/ARCHITECTURE.md` (v0.2-kickoff research, read this session) —
  prior-verified CadQuery API claims (variadic `cut`, `polarArray`, no honeycomb
  primitive in cadquery 2.8.0) and the pitfall taxonomy (tangent cutters, sequential-cut
  cost, position-selector fragility, clock-based caps) this phase's own pitfalls extend.
- `docs/architecture/decision_log.md` L27-L29 (read this session) — the cap-methodology
  precedent (L17-style measured constant), the analytic-vs-3D-fillet precedent (L09), the
  measured-boundary precedent (L28's `ROOT_CONTACT`, L29's `TIP_CHAMFER_MARGIN`).
- `bench/RESULTS.md` (relevant sections read this session) — Phase 10's tip-chamfer sweep
  numbers (14.87 s heaviest row) that D-11's 7.5 s honeycomb budget is computed against.

### Tertiary (LOW confidence)

None used for a load-bearing claim in this document. Every CadQuery API claim was
verified against the installed library this session; every architectural claim was
verified against code read this session; every unresolved question (fillet mirror
algebra, hub-opening measure, honeycomb enumeration cost) is flagged in Assumptions Log /
Open Questions rather than asserted.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — no new dependency; every API signature confirmed against the
  installed library this session.
- Architecture: HIGH — cut order, selector interactions and the batched-cut pattern are
  all read from code in the tree this session, not inferred.
- Pitfalls: MEDIUM-HIGH — the batching/tangency/selector-fragility pitfalls are grounded
  in this project's own prior research and code; the honeycomb enumeration-cost pitfall
  and the spoke-fillet mirror-algebra risk are judgment calls flagged explicitly as
  unresolved (Open Questions 1-3), not measured.

**Research date:** 2026-09-29
**Valid until:** 30 days (stable stack, no new dependency; the honeycomb cap constant
itself has its own much shorter validity — it must be re-derived if the kernel version or
the bench host ever changes, per L17's own methodology).
