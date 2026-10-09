# solid-model — tactics

## Shape

**Build pipeline**, one decision per step, in `_build(p)`:

```
profile(p) ─▶ _gear_blank ─▶ _cut_face_recesses ─▶ _cut_bore ─▶ _cut_keyway ─▶ _cut_body ─▶ _chamfer_tips ─▶ one validated Solid
                (outline,       (annulus cut,          (circle, D or hex,   (slot, after      (one pattern's   (tip arcs,
                 extrude)        floor fillets)         rim chamfers)        the chamfer)      cutters, one      last)
                                                                                                cut(*cutters))
```

`_cut_body` subtracts every cutter of the one body-cutout pattern set (spoke sectors, holes
or honeycomb cells — never more than one, `REQ-one-cutout-pattern`) in a single boolean cut
call after the recess floor fillet and the bore-rim chamfer are already baked geometry, so
no selector before the tip step ever sees a cutout edge — only `_tip_edges`, run after it,
is shown (by a real-pipeline spy) to take exactly the tip arcs.

`_outline(pr, fillet, curve=None)` assembles the closed wire tooth by tooth, in one of two
roots. Without a `curve` (the default, and every gear whose `root_shape` is `radial`) it
builds the analytic root: a straight or filleted lead-in from the root circle, a B-spline on
each involute flank (16 points, biased toward the tip), a three-point arc across the tip,
and an arc along the root to the next tooth. Root fillet arcs come from `_fillet_corner()`,
which solves the tangency directly. The spline's start comes from `calc.spline_start`, so
the outline and the tip chamfer's cap (below) read the same radius. That body is untouched
by the hob root, float for float, which is why the pre-v0.2 fixture replays unchanged.

With a `curve` (`calc.RootMode.curve`, set exactly where `root_mode` answers trochoid for
`root_shape="trochoid"`) the whole outline is `_trochoid_outline`: per tooth one B-spline per
side through the `RootCurve`'s points, then the involute spline from the **same `Vector`
object** the root spline ends on (a recomputed point 1e-6 mm away silently opens the wire),
the tip arc, the mirror side, and the root arc to the next tooth: six side faces per tooth
where the radial outline has eight. `fillet` is not read; the tip chamfer's cap reads the
junction radius instead, through `calc.spline_start(pr, fillet, curve)`. `_trochoid_teeth`
makes the per-tooth point lists once, and the outline, and the area guard below, both read
them.

**The short-arc rule.** Where the chord from one tooth's last root point to the next tooth's
first is under `ROOT_ARC_MIN` (2e-6 mm), no root arc is made and the next tooth's root spline
starts from the previous tooth's own vertex object: five side faces per tooth there, not six.
The kernel's `makeThreePointArc` raises `GC_MakeArcOfCircle::Value() - no result` on chords
of 2e-9 to 2.0e-7 mm and silently drops the arc under 1e-10, and a gear a user can type
(`root_fillet` 3.0, which the cap floors to 3 dp, and a backlash that leaves a tip land of
1e-8 mm) lands in that band. Decided for every tooth before any edge exists, so the object
both splines receive is the same one.

**Four structural guards**, all on the trochoid branch only, none resting on `isValid()` (in
the spirit of L26, fail loud rather than ship: a wire that closes the wrong way round a tooth
is still a valid face): `_guard_junction`
(the curve's last point on the involute, bar `ROOT_JUNCTION_BAR_RAD`) and `_guard_spacing`
(largest over smallest chord of the 16 root points, bar `ROOT_SPACING_RATIO_MAX`) read floats
and run before any kernel call; `_guard_annulus` reads 81 positions of tooth 0's two root
splines the moment they are made and refuses a radius outside `[rf - TOL, ra + TOL]`;
`_guard_area` runs in `_gear_blank` on the face, against the shoelace area of the polygon
through the outline's own points with each arc taken through its midpoint
(`_trochoid_polygon`), bar `ROOT_AREA_REL_MAX`. An honest curve never trips one: each bar is
the whole-product measurement of 19-02 with its headroom in the code comment beside it. Each
raises `BuildError` that says it is a modelling defect in spur and to set `root_shape` to
`radial` (below), the way `_tip_edges` does for the chamfer.

**Edge re-selection** is separated out on purpose: `_groove_floor_edges()` matches
circles by radius and z; `_bore_rim_edges()` matches by position, sampling three interior
points, within `calc.bore_rim_limit(p)` (a hex bore's corners) plus `BORE_RIM_SLACK`,
because a D-bore rim is not one geometric type; `_tip_edges()` matches circles at `ra`
with both endpoints on an end face — the end-face test distinguishes the tip arcs from
the ones a chamfer moves onto the two faces, so a re-chamfer never re-selects itself.
All three selectors raise `BuildError` when they match nothing while their feature is on
(L26) — a selector never silently selects nothing. The keyway slot is cut after
`_bore_rim_edges` runs, so the selector never sees it and the keyway's edges stay sharp
(L28).

**Caching and export**: `build()` and `export()` both take `_LOCK`, then go through
`_build_cached` (an `lru_cache` on the parameter object) and `_EXPORTS` (an LRU bounded by
total bytes). `_BlobCache` needs no lock of its own — every caller already holds `_LOCK`,
and that is written down where it is defined.

## Contracts

**In:** `GearParams`, plus the effective fillets and radii it reads from `calc.py`.

**Out:**
- `build(p) -> cq.Solid` — used only by the tests. A CadQuery object crossing this line
  is a deliberate test affordance, not a public contract.
- `export(p, fmt, quality) -> bytes` — what `app.py` and `cli.py` use.
- `BuildError` — the only exception that leaves. `_build_checked()` wraps the assorted
  `Standard_Failure` subclasses OCCT raises into it with an actionable message; the edge
  selectors raise it themselves on an empty selection, and so do the four hob-root guards.

**Invariant, checked rather than assumed:** `_build()` asserts exactly one solid and that
it is valid before returning. This is also why the module can annotate intermediates
loosely where CadQuery's own signatures return a wide `Shape` — the narrow type is
re-established at the end, not hoped for.

**Configuration:** `SPUR_SOLID_CACHE` (entries, default 4) and `SPUR_EXPORT_CACHE_MB`
(megabytes, default 64), both read through `int_env()`, both per worker process.
