# Phase 11: Body Cutouts - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-29
**Phase:** 11-body-cutouts
**Areas discussed:** Spoke arm geometry, Honeycomb lattice & walls, Honeycomb budget & cap, Refusals/bounds/numbers

---

## Spoke arm geometry

### What do `hub_d` and `rim_wall` bound?

| Option | Description | Selected |
|--------|-------------|----------|
| Hub OD + rim thickness from root | hub_d = outer diameter of the hub ring; rim_wall = radial thickness of the rim ring inward from the root circle | ✓ |
| Hub wall thickness, not OD | hub_d read as the hub ring's radial wall above the chamfered bore mouth | |
| rim_wall from the tip circle | Rim ring measured inward from ra | |

**User's choice:** Hub OD + rim thickness from root (the recommendation)

### Arm shape: what does `spoke_width` describe?

| Option | Description | Selected |
|--------|-------------|----------|
| Parallel-sided bars, constant width | Each arm a straight bar of width spoke_width; sectors = annulus minus N bars, one cut | ✓ |
| Tapered sectors (angular width) | Arms are angular sectors; spoke_width read at the hub | |
| Tapered, width at the rim | Same, read at the rim | |

**User's choice:** Parallel-sided bars (the recommendation)

### Where does arm 0 sit, and is that also hole 0's position?

| Option | Description | Selected |
|--------|-------------|----------|
| Arm 0 and hole 0 centred on +X, no angle field | One fixed convention for both patterns; matches the D-flat's side and polarArray's default | ✓ |
| Arm 0 on +Y, over the keyway | Only helps even counts; two conventions to explain | |
| Add a rotation field now | spoke_angle / hole_angle in degrees | |

**User's choice:** +X, no angle field (the recommendation)

### Sector corners: sharp or filleted?

| Option | Description | Selected |
|--------|-------------|----------|
| Sharp, no fillet | Keyway D-08's choice: no new selector, no kernel risk, no new field | |
| Filleted with a fixed radius | A constant on 4N vertical edges via .fillet() | |
| Filleted with a new field | spoke_fillet (mm, 0 = sharp), capped to fit; a 5th spoke field | ✓ |

**User's choice:** Filleted with a new field — **against the recommendation (sharp).**
**Notes:** Consequences recorded in CONTEXT.md D-04/D-21: REQ-spoke-cutout and ROADMAP SC2 amended through the edit-phase tooling; the field is capped, warned and reported.

### How is the spoke corner fillet built?

| Option | Description | Selected |
|--------|-------------|----------|
| Analytic 2D arcs in the cutter sketch | Tangent corner arcs computed in Python and extruded — L09's remedy; no selector | ✓ |
| 3D .fillet() on the built solid | A fourth position selector, matrix column, tripwire; vertical edges meet the recess floor's toroidal fillet | |
| Measure both, planner picks | A spike timing both routes | |

**User's choice:** Analytic 2D arcs (the recommendation)

### What bounds `spoke_fillet`, and how is the applied value reported?

| Option | Description | Selected |
|--------|-------------|----------|
| Cap to the sector, warn, report applied | ρ ≤ 0.45 × the sector's narrowest dimension; one warning; spoke_fillet_effective | ✓ |
| Refuse when it does not fit | 422 naming spoke_fillet and the sector fields | |
| Cap and warn, no derived field | Applied radius only in the warning sentence | |

**User's choice:** Cap, warn, report (the recommendation)

---

## Honeycomb lattice & walls

### Which cells get cut?

| Option | Description | Selected |
|--------|-------------|----------|
| Whole cells only, never clipped | A cell is cut only if its entire hexagon lies inside the web annulus | ✓ |
| Clipped cells, edge to edge | Every cell intersected with the annulus | |
| Whole cells, lattice scaled to fill | Pitch stretched so whole rings fit exactly | |

**User's choice:** Whole cells only (the recommendation)

### Where does the lattice sit, and which way do the cells face?

| Option | Description | Selected |
|--------|-------------|----------|
| Cell centred on the axis, flat facing +X | Origin on the axis; polygon(6, circumscribed=True) like the hex bore | ✓ |
| First ring of cells tangent to the hub wall | Origin shifted to pack the innermost ring | |
| Vertex facing +X | Lattice rotated 30° | |

**User's choice:** Axis-centred, flats on ±X (the recommendation)

### What are the honeycomb's hub and rim boundary walls?

| Option | Description | Selected |
|--------|-------------|----------|
| hex_wall on both boundaries | Inner = bore_mouth_limit + hex_wall, outer = rf − hex_wall | ✓ |
| MIN_WALL on the boundaries, hex_wall between cells | Maximal web regardless of hex_wall | |
| Separate fields for the boundary walls | hex_hub_wall / hex_rim_wall | |

**User's choice:** hex_wall on both boundaries (the recommendation)

### A `hex_wall` below MIN_WALL: refused or raised?

| Option | Description | Selected |
|--------|-------------|----------|
| 422 naming hex_wall | 0 < hex_wall < MIN_WALL refused before any CAD work | ✓ |
| Raise to MIN_WALL and warn | Caps go down everywhere else | |
| Build it as asked, warn like MIN_TIP_FDM | Contradicts the REQ's hub/rim rules | |

**User's choice:** 422 (the recommendation)

---

## Honeycomb budget & cap

### How much of SPUR_BUILD_TIMEOUT may the honeycomb at its cap cost on the bench host?

| Option | Description | Selected |
|--------|-------------|----------|
| A quarter: ≤ 7.5 s | The quarter-of-timeout line Phase 10 named; leaves room for Phase 12's composition with the 14.87 s chamfer | ✓ |
| Half: ≤ 15 s | Denser honeycombs; composes to ~30 s with the chamfer | |
| Whatever fits alone: ≤ 30 s | Composition guaranteed over budget | |

**User's choice:** A quarter (the recommendation)

### What form does the cap take in calc.py?

| Option | Description | Selected |
|--------|-------------|----------|
| One constant cell count, measured at the heaviest configuration | HEX_CELL_CAP = the largest count whose sweep row reads ≤ 7.5 s | ✓ |
| A cost model: cap = budget / per-cell cost | Only honest if the sweep shows linear cost | |
| Teeth/module-dependent cap | A bigger cap on small gears | |

**User's choice:** One constant (the recommendation)

### When the derived count exceeds the cap, how is the smallest fitting size found, and what does the response carry?

| Option | Description | Selected |
|--------|-------------|----------|
| Step up 0.05 mm from the request; report size, count, one warning | hex_cell raised in 0.05 mm steps; hex_cell_effective + hex_cell_count; one warning | ✓ |
| Exact minimum size, not on the step grid | Off-grid numbers like 2.3417 mm | |
| Report the count only | Applied size only in the sentence | |

**User's choice:** 0.05 mm steps, two fields, one warning (the recommendation)

### A honeycomb where no whole cell fits the web: refusal or warned no-op?

| Option | Description | Selected |
|--------|-------------|----------|
| 422 naming hex_cell and hex_wall | The user asked for a honeycomb that cannot exist; sentence quotes the annulus radii | ✓ |
| Build without cells, warn | The recess's drop-and-warn shape | |
| Lower hex_cell until one fits, warn | Two opposite adjustments to one field | |

**User's choice:** 422 (the recommendation)

---

## Refusals, bounds, numbers

### A half-set pattern, and dimensions set with the count at 0?

| Option | Description | Selected |
|--------|-------------|----------|
| Half-set is a 422; dims without a count are ignored and warned | Keyway D-03 refusal; hex D-02's ignored-field warning | ✓ |
| Half-set is a 422; dims without a count silently inert | A typed dimension says nothing | |
| Half-set treated as off with a warning | A link that asked for a pattern would ship without it | |

**User's choice:** 422 + ignored-dims warning (the recommendation)

### Neighbour rule — what counts as 'holes or arms overlap each other'?

| Option | Description | Selected |
|--------|-------------|----------|
| MIN_WALL between neighbours, both patterns | Material between holes ≥ MIN_WALL; sector opening at the hub ≥ MIN_WALL | ✓ |
| Overlap only (gap ≤ 0) | Touching cutters accepted | |
| MIN_WALL for holes, overlap-only for spoke sectors | Two rules | |

**User's choice:** MIN_WALL between neighbours (the recommendation)

### Bounds on the count fields and their minimum?

| Option | Description | Selected |
|--------|-------------|----------|
| le 200 like teeth, minimum 1; the sweep may lower it | One instance per tooth; a row over budget halts with a lower le as the first offer | ✓ |
| Research's 24 arms / 48 holes | No source | |
| le 200, minimum 2 | Refuse a single arm or hole | |

**User's choice:** 0–200, 1 allowed (the recommendation)

### Form layout for the new fields?

| Option | Description | Selected |
|--------|-------------|----------|
| Three groups: Spokes, Holes, Honeycomb | 5 + 3 + 2 fields after the Recess group | ✓ |
| One 'Cutouts' group | All ten fields in one fieldset | |
| Extend the Body group | face_width plus the cutout fields | |

**User's choice:** Three groups (the recommendation)
**Notes:** The question text said "12 new fields"; corrected to 10 (5 + 3 + 2) in the wrap-up question and in CONTEXT.md.

---

## Claude's Discretion

Names (cut step, cutter builders, calc functions, derived fields, sweep files, sentences);
the thinnest-wall datum's description (from `bore_mouth_limit`, or the exact mouth-polygon
distance if cheap); dimension `le`s (family bounds); cutter construction and the
`cut(*cutters)` vs fuse-then-cut measurement; honeycomb enumeration and its `derive()` cost;
the `tol=` probe at tangent cases; the recess-fillet survival count; selector matrix rows; sweep
rows; the over-budget halt's offers for holes/spokes; help text and README; `bore_clearance`
not applied to cutouts. Full list in CONTEXT.md.

## Deferred Ideas

- A rotation/phase field for arms and holes.
- Corner fillets on honeycomb cells or holes.
- Holes between spoke arms on one part (REQ-hole-spoke-combination, already in Future Requirements).
- A teeth/module-dependent honeycomb cap.
- Clipped boundary cells; separate honeycomb boundary-wall fields (both rejected).
- Conditional form fields — 08's trigger is now live for Phase 12's UI hint.
- The analytic corner-arc helper as a general cutter helper (e.g. keyway floor corners).
