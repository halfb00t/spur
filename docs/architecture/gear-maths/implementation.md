# gear-maths — implementation

## Layout

`src/spur/calc.py` — the constants, the rules and the report; the classes `Profile`,
`Cutter`, `RootCurve`, `RootMode` and the frozen `DerivedDimensions` document `derive()`
returns.

| Piece | Does |
|---|---|
| `MIN_WALL`, `MIN_TIP_FDM`, `MIN_RECESS_WIDTH`, `ROOT_CONTACT`, `TIP_CHAMFER_MARGIN`, `HEX_CELL_CAP` | the physical constants the rules are written against, in mm — `ROOT_CONTACT` is the measured contact threshold for a chamfered round or D-flat bore mouth reaching the root circle; `TIP_CHAMFER_MARGIN` is how far inside the involute spline's start the tip chamfer's footprint stops, 0.001 mm; `HEX_CELL_CAP` is the largest honeycomb whole-cell count the build timeout can absorb, 120 cells, measured on `bench/honeycomb_spike.py` at 200 teeth/module 10/both recesses (`bench/RESULTS.md` "Honeycomb cell-count spike (Phase 11, D-24)") |
| `ROOT_CURVE_POINTS`, `TROCHOID_JOIN_EPS` | the trochoid root's constants — `ROOT_CURVE_POINTS` is how many points the curve is sampled at, 16 (3.6–4.0e-5 mm against a kernel spline at module 1, 8–14 teeth, tip radius 0.38 mm; the bar the built root is held to is `tests/test_model.py` `KERNEL_BAR_PER_MODULE`, 2e-3 x module, in `bench/RESULTS.md` "Bars adopted (19-02)"); `TROCHOID_JOIN_EPS` is the roll of the cutter's flank foot, relative to `rb`, inside which the join is taken as tangent without a bracket, 1e-4 (the bracket was lost at 5.6e-6 at worst over 400 seeded gears; `bench/RESULTS.md` "Join epsilon (18-03)") |
| `ROOT_WAIST_FLOOR`, `PROFILE_SHIFT_MAX` | `ROOT_WAIST_FLOOR` is 0.4 mm, absolute: below it (compared at the 3 dp it prints) `derive()` adds the `waist thin` sentence and nothing else, never a refusal. Chosen after the 19-02 waist walk (1,061 hob-cut gears, none failed, thinnest built waist 3.2325e-3 mm), so it is a printability floor and not a kernel limit; it warns on 771 of the 10,326 gears of the Phase 18 sweep product, **595 of the 616 module-0.2 gears** among them (`bench/RESULTS.md` "Waist walk (19-02, D-07)", "Bars adopted (19-02)"). `PROFILE_SHIFT_MAX` is the `profile_shift` field's `le`, 1.0, written once here because `calc.py` imports `params` for typing only; a test reads the schema to keep the two equal |
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
| `spline_start(pr, fillet, curve=None)` | the radius where the outline's involute spline begins: above the root fillet's straight lead-in, capped halfway up the tooth, with the radial root; with a `RootCurve` it is the curve's junction radius, `curve.points[-1][0]`, with no halfway clamp. `model._outline` builds the flank from it |
| `tip_chamfer_limit(p, rm=None)` | the smallest of the tip chamfer's three limits, and the reason the warning names. With no `rm` it asks `root_mode` itself; under the hob-cut root its third bound is `ra` minus the junction radius minus `TIP_CHAMFER_MARGIN`, with a reason that does not mention a lead-in |
| `tip_chamfer_effective(p, rm=None)` | the tip chamfer actually cut, 3 dp, 0 when off; `rm` as above |
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
| `undercut_teeth(c)`, `undercut_shift(c)` | the fewest teeth, and the smallest profile shift, at which this cutter does not undercut — read from the cutter that cuts, so a trimmed tip radius gives the trimmed cutter's onset |
| `_undercut_advice(c)` | the undercut sentence `derive()` prints where the hob-cut root's join is a crossing: the onset rounded **up** to 0.1 teeth and the shift rounded **up** to 0.001 (after `round(v * 10**k, 9)` removes float residue, so 0.41508 prints 0.416, where the cutter's roll is non-negative, and not 0.415, where it is -7.9e-5 mm); above `PROFILE_SHIFT_MAX` it says no shift in range avoids the undercut and prints none (6 teeth, 14.5 degrees, sharp cutter needs 1.0619) |
| `RootCurve` | the hob's root below the junction with the involute: `ROOT_CURVE_POINTS` (radius, half-angle) points root circle first, the join kind (`tangent` or `crossing`) and the waist, the curve's narrowest point (smallest arc thickness `2 R h`) |
| `_trochoid_point(c, beta)` | the envelope of the cutter's tip arc at contact-normal angle `beta`, as (radius, half-angle), one closed expression for every tip radius |
| `_waist(c, betas, points)` | the point where the arc thickness `2 R h` is smallest (not the half-angle `h`: on a crossing join the thickness is still falling below the radius where `h` is smallest, 19-REVIEW CR-01), refined by 60 golden-section steps between the smallest sample's neighbours; `h <= 0` there is `tooth severed` |
| `_bisect(f, lo, hi)` | the root of a function that changes sign on `[lo, hi]`, 60 halvings, the way `_involute_angle` solves |
| `_junction(c, eps)` | where the trochoid hands over to the involute and how — tangent at the flank foot with no root-find, or the crossing found by two bisections; `None` when the bracket the geometry promises is missing |
| `_root_curve(c)` | the curve, or the named reason there is none, cheap checks first (`tip land gone`, `bracket degenerate`, `curve invalid`, `tooth severed`) |
| `trochoid_root(c)` | the hob's root for this cutter, or `None` when no honest curve exists — a refusal, never a clipped or partly sampled curve |
| `RootMode` + `root_mode(p, pr, *, requested, rho)` | the single answer to "does the trochoid root apply to this gear": the mode, the reason it stayed radial, the cutter asked about and `RootMode.curve`, the `RootCurve` the part is built from and every hob-root number is read from (set exactly when the mode is `trochoid`, solved once). Nothing requested is `radial` / `not requested` without building the cutter; `nothing radial to replace` (`rb <= rf`) is decided in closed form before the generator runs. `derive`, `model._build` and `tip_chamfer_limit` each call it once, with `requested=p.root_shape, rho=p.root_fillet`, so they cannot name different roots |
| `_ROOT_SENTENCES`, `root_warnings(rm)` | the sentences, and the function that returns the refusal and cap ones for a `RootMode` — the one place every trochoid sentence comes from. Keys: the five refusal reasons, `rho capped` (names `root_fillet`; the printed radius is within 0.001 mm of the largest that keeps a tip land, because the cap is floored to 3 dp), `thickness not printed` (`derive()` prints it on every hob-cut gear, where `root_thickness` and `root_gap` are null), `undercut` and `undercut out of range` (from `_undercut_advice`), `waist thin` (placeholders `{waist}` and `{floor}`; names `teeth`, `profile_shift` and `pressure_angle`, never the word undercut) |
| `DerivedDimensions` | the frozen document, every key always present. Since Phase 19: `root_thickness` and `root_gap` are `float | None`, null under the hob-cut root (one sentence says why); `root_fillet` is the radius cut (`rm.cutter.rho`) under it; and two new fields, directly after `root_fillet`, both mm and both null unless the hob-cut root applies — `root_form_d`, `round(2 * R_join, 3)` from `RootMode.curve`, the cutter-envelope junction and **not** an ISO 21771 form diameter, and `root_waist`, `round(2 * R_w * h_w, 3)` from `RootCurve.waist`, an arc on its own radius (equal to the involute's thickness at the junction on a tangent join, below it on a crossing). A refused request builds the radial root and prints the radial numbers, both new fields null |
| `derive()`'s warning order | fixed: the tip FDM sentence; radial only, the root-fillet cap and lead-in chord sentences; the root-mode sentence from `root_warnings`; trochoid only, the thickness sentence; the tip chamfer; the undercut sentence (the shipped one while the radial root is built, a refused request included, byte for byte; `_undercut_advice` where the hob-cut join is a crossing); the waist sentence; then the bore, recess and cutout sentences |

`src/spur/params.py` — the `GearParams` model. Field metadata (`group`, `unit`, `step`)
travels through the JSON schema into the web form, so a new field appears in the UI and
the CLI without either being edited. `_feasible()` is the model validator that calls
`check()`; it imports `calc` locally to keep the module import graph one-directional.

## Entry points

Nothing here is an entry point. It is called by `model.py` (for the effective fillets,
the tip chamfer, the radii and the involute start), `app.py` (`/api/info`,
`/api/schema`) and `cli.py` (`spur info`).
