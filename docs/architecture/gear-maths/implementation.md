# gear-maths — implementation

## Layout

`src/spur/calc.py` — the constants, the rules and the report; the classes `Profile`,
`Cutter`, `RootCurve`, `RootMode` and the frozen `DerivedDimensions` document `derive()`
returns.

| Piece | Does |
|---|---|
| `MIN_WALL`, `MIN_TIP_FDM`, `MIN_RECESS_WIDTH`, `ROOT_CONTACT`, `TIP_CHAMFER_MARGIN`, `HEX_CELL_CAP` | the physical constants the rules are written against, in mm — `ROOT_CONTACT` is the measured contact threshold for a chamfered round or D-flat bore mouth reaching the root circle; `TIP_CHAMFER_MARGIN` is how far inside the involute spline's start the tip chamfer's footprint stops, 0.001 mm; `HEX_CELL_CAP` is the largest honeycomb whole-cell count the build timeout can absorb, 120 cells, measured on `bench/honeycomb_spike.py` at 200 teeth/module 10/both recesses (`bench/RESULTS.md` "Honeycomb cell-count spike (Phase 11, D-24)") |
| `ROOT_CURVE_POINTS`, `TROCHOID_JOIN_EPS` | the trochoid root's constants — `ROOT_CURVE_POINTS` is how many points the curve is sampled at, 16 (3.6–4.0e-5 mm against a kernel spline at module 1, 8–14 teeth, tip radius 0.38 mm); `TROCHOID_JOIN_EPS` is the roll of the cutter's flank foot, relative to `rb`, inside which the join is taken as tangent without a bracket, 1e-4 (the bracket was lost at 5.6e-6 at worst over 400 seeded gears; `bench/RESULTS.md` "Join epsilon (18-03)") |
| `inv(a)` | the involute function, `tan(a) - a` |
| `Profile` + `profile(p)` | radii (`r`, `rb`, `ra`, `rf`), pitch half-angle, `r_start`, `half_angle(rho)` |
| `_dedendum(m, x)`, `_pitch_thickness(m, alpha, x, bl)` | the one definition each of the root circle's depth below the pitch circle and the pitch-circle tooth thickness with backlash off — `profile()` and `cutter()` both read them, so the root circle and the hob's tip can never disagree |
| `bore_radius(p)` | bore radius including print clearance, 0 when there is no bore |
| `hex_across_flats(p)` | the hex bore's effective across-flats including clearance, 0 with no hex |
| `keyway_width_effective(p)` | the keyway's width including print clearance, 0 with no keyway |
| `keyway_corner_radius(p)` | the keyway floor corner's radius from the axis, 0 with no keyway |
| `keyway_flat_wall(p)` | the round bore wall left between the D-flat's corner and the keyway's side |
| `bore_rim_limit(p)` | the farthest point of the bore wall: `bore_radius(p)`, or a hex's corners |
| `bore_mouth_limit(p)` | the chamfered mouth's farthest reach, or a keyway's floor corner, whichever is farther — the datum `recess_radii()` clears by `MIN_WALL`, and `check()` keeps `MIN_WALL` inside the root |
| `recess_radii(p, rf)` | the groove's effective `(inner, outer)` radius, or `None` |
| `root_fillet(p)`, `recess_fillet(p, rf)` | the fillet radii actually used, after capping |
| `spline_start(pr, fillet)` | the radius where the outline's involute spline begins, above the root fillet's straight lead-in; `model._outline` builds the flank from it |
| `tip_chamfer_limit(p)` | the smallest of the tip chamfer's three limits, and the reason the warning names |
| `tip_chamfer_effective(p)` | the tip chamfer actually cut, 3 dp, 0 when off |
| `_under_min_wall(wall)` | `round(wall, 6) < MIN_WALL` — the one comparison point every cutout wall rule uses, so a wall sized to exactly `MIN_WALL` is accepted despite step-aligned float residue |
| `_listed(items)` | the `"a"` / `"a and b"` / `"a, b and c"` join for every cutout sentence naming more than one field |
| `cutout_walls(p, rf)` | the thinnest remaining wall on the hub side and the rim side, for whichever body cutout pattern is set — the honeycomb branch reads the exact nearest-edge/farthest-vertex reach on the cut cells, not a conservative circumradius |
| `hole_gap(p)` | the material left between adjacent lightening holes on the bolt circle |
| `spoke_opening(p)` | the arc between the feet of adjacent spoke bars on the hub circle (`keyway_flat_wall`'s arc-measure precedent, not a chord) |
| `spoke_fillet_limit(p)` | the smallest of the sector's hub opening and annulus width, and the reason the warning names |
| `spoke_fillet_effective(p)` | the spoke fillet actually cut, 3 dp, 0 when off |
| `whole_cells(cell, wall, inner, outer)`, `cell_count_floor(cell, wall, inner, outer)`, `cells_within(cap, cell, wall, inner, outer)` | the honeycomb's whole-cell lattice, its area-based lower-bound floor, and `cells_within`'s raise-to-fit over `HEX_CELL_CAP` — moved from `bench/honeycomb_spike.py` unchanged, the spike imports them back |
| `hex_cells(p, rf)` | the honeycomb's applied across-flats and cell centres, `cells_within`'s raise-to-fit over the web annulus — the one result `check()`, `cutout_walls()`, `derive()` and `model._cell_cutters` all read |
| `_tooth(pr)` | tip thickness, root thickness and root gap — all measured on the root circle |
| `check(p)` | the refusals, each with the fields responsible |
| `span_measurement(p)` | Wildhaber span over *k* teeth |
| `derive(p, mate_teeth=None, mate_shift=0.0)` | the `DerivedDimensions` document: dimensions, warnings, and the mate when asked |
| `_involute_angle(target)` | bisection inverse of `inv` |
| `centre_distance(p, z2, x2=0)` | working centre distance, or `None` |
| `RootShape`, `RootReason` | the two root shapes, `"radial"` or `"trochoid"`, and the six reasons a requested trochoid stays radial (`not requested`, `nothing radial to replace`, `tip land gone`, `bracket degenerate`, `curve invalid`, `tooth severed`) |
| `Cutter` + `cutter(p, rho)` | the basic rack that cuts one gear, defined once: tip depth, tooth width (backlash thickens it), tip-land half-width, the tip radius asked for and the one used (capped at the largest that keeps a land, floored to 3 dp), and `xi`, the roll of the flank foot, negative where the gear is undercut |
| `undercut_teeth(c)`, `undercut_shift(c)` | the fewest teeth, and the smallest profile shift, at which this cutter does not undercut — read from the cutter that cuts, so a trimmed tip radius gives the trimmed cutter's onset; `derive()`'s own sentence is untouched until Phase 19 restates it |
| `RootCurve` | the hob's root below the junction with the involute: `ROOT_CURVE_POINTS` (radius, half-angle) points root circle first, the join kind (`tangent` or `crossing`) and the waist, the curve's narrowest point |
| `_trochoid_point(c, beta)` | the envelope of the cutter's tip arc at contact-normal angle `beta`, as (radius, half-angle), one closed expression for every tip radius |
| `_waist(c, betas, points)` | the point where the half-angle is smallest, refined by 60 golden-section steps between the smallest sample's neighbours |
| `_bisect(f, lo, hi)` | the root of a function that changes sign on `[lo, hi]`, 60 halvings, the way `_involute_angle` solves |
| `_junction(c, eps)` | where the trochoid hands over to the involute and how — tangent at the flank foot with no root-find, or the crossing found by two bisections; `None` when the bracket the geometry promises is missing |
| `_root_curve(c)` | the curve, or the named reason there is none, cheap checks first (`tip land gone`, `bracket degenerate`, `curve invalid`, `tooth severed`) |
| `trochoid_root(c)` | the hob's root for this cutter, or `None` when no honest curve exists — a refusal, never a clipped or partly sampled curve |
| `RootMode` + `root_mode(p, pr, *, requested, rho)` | the single answer to "does the trochoid root apply to this gear": the mode, the reason it stayed radial, and the cutter asked about; nothing requested is `radial` / `not requested` without building the cutter; `nothing radial to replace` (`rb <= rf`) is decided in closed form before the generator runs |
| `_ROOT_SENTENCES`, `root_warnings(rm)` | one sentence per refusal reason and one for a trimmed tip radius, and the function that returns them for a `RootMode` — the one place every trochoid sentence comes from |

`src/spur/params.py` — the `GearParams` model. Field metadata (`group`, `unit`, `step`)
travels through the JSON schema into the web form, so a new field appears in the UI and
the CLI without either being edited. `_feasible()` is the model validator that calls
`check()`; it imports `calc` locally to keep the module import graph one-directional.

## Entry points

Nothing here is an entry point. It is called by `model.py` (for the effective fillets,
the tip chamfer, the radii and the involute start), `app.py` (`/api/info`,
`/api/schema`) and `cli.py` (`spur info`).
