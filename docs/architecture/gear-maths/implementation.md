# gear-maths — implementation

## Layout

`src/spur/calc.py` — the constants, the rules and the report; two classes, `Profile` and
the frozen `DerivedDimensions` document `derive()` returns.

| Piece | Does |
|---|---|
| `MIN_WALL`, `MIN_TIP_FDM`, `MIN_RECESS_WIDTH`, `ROOT_CONTACT`, `TIP_CHAMFER_MARGIN` | the physical constants the rules are written against, in mm — `ROOT_CONTACT` is the measured contact threshold for a chamfered round or D-flat bore mouth reaching the root circle; `TIP_CHAMFER_MARGIN` is how far inside the involute spline's start the tip chamfer's footprint stops, 0.001 mm |
| `inv(a)` | the involute function, `tan(a) - a` |
| `Profile` + `profile(p)` | radii (`r`, `rb`, `ra`, `rf`), pitch half-angle, `r_start`, `half_angle(rho)` |
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
| `_tooth(pr)` | tip thickness, root thickness and root gap — all measured on the root circle |
| `check(p)` | the refusals, each with the fields responsible |
| `span_measurement(p)` | Wildhaber span over *k* teeth |
| `derive(p, mate_teeth=None, mate_shift=0.0)` | the `DerivedDimensions` document: dimensions, warnings, and the mate when asked |
| `_involute_angle(target)` | bisection inverse of `inv` |
| `centre_distance(p, z2, x2=0)` | working centre distance, or `None` |

`src/spur/params.py` — the `GearParams` model. Field metadata (`group`, `unit`, `step`)
travels through the JSON schema into the web form, so a new field appears in the UI and
the CLI without either being edited. `_feasible()` is the model validator that calls
`check()`; it imports `calc` locally to keep the module import graph one-directional.

## Entry points

Nothing here is an entry point. It is called by `model.py` (for the effective fillets,
the tip chamfer, the radii and the involute start), `app.py` (`/api/info`,
`/api/schema`) and `cli.py` (`spur info`).
