# gear-maths — implementation

## Layout

`src/spur/calc.py` — the constants, the rules and the report; two classes, `Profile` and
the frozen `DerivedDimensions` document `derive()` returns.

| Piece | Does |
|---|---|
| `MIN_WALL`, `MIN_TIP_FDM`, `MIN_RECESS_WIDTH` | the three physical constants the rules are written against, in mm |
| `inv(a)` | the involute function, `tan(a) - a` |
| `Profile` + `profile(p)` | radii (`r`, `rb`, `ra`, `rf`), pitch half-angle, `r_start`, `half_angle(rho)` |
| `bore_radius(p)` | bore radius including print clearance, 0 when there is no bore |
| `recess_radii(p, rf)` | the groove's effective `(inner, outer)` radius, or `None` |
| `root_fillet(p)`, `recess_fillet(p, rf)` | the fillet radii actually used, after capping |
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

Nothing here is an entry point. It is called by `model.py` (for the effective fillets and
radii), `app.py` (`/api/info`, `/api/schema`) and `cli.py` (`spur info`).
