"""CadQuery solid construction and STL/STEP export.

This module is the only doorway to `cadquery`/`OCP`, and it now runs inside a worker
process, not the serving process (D-02, D-05) -- `app.py` reaches `export()` only through
a spawned `BuildPool`, never by importing this module directly. OpenCascade isn't safe to
drive from several threads at once, so every kernel call goes through one lock; it stays
uncontended under one-task-per-worker (D-08). The solid built for a parameter set is
cached here, per worker (SPUR_SOLID_CACHE, entries) -- rebuilding it needs the kernel
that only a worker has, and D-07's affinity routing keeps the UI's repeat requests for
one gear (preview, then STL, then STEP) on this same worker. The exported-bytes cache
lives one level up, in the serving process (`app.py`'s `_BlobCache`, D-06): a repeat
download never wakes a worker at all.
"""

from __future__ import annotations

import ctypes
import math
import tempfile
import threading
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING, Literal

import cadquery as cq

if TYPE_CHECKING:
    from collections.abc import Callable

from . import int_env
from .build_errors import BuildError
from .calc import (
    Profile,
    RootCurve,
    bore_radius,
    bore_rim_limit,
    hex_across_flats,
    hex_cells,
    keyway_width_effective,
    profile,
    recess_fillet,
    recess_radii,
    root_fillet,
    root_mode,
    spline_start,
    spoke_fillet_effective,
    tip_chamfer_effective,
)
from .params import GearParams

Format = Literal["stl", "step"]
Quality = Literal["preview", "fine"]

# (linear deflection mm, angular deflection rad) for STL tessellation
TESSELLATION: dict[str, tuple[float, float]] = {"preview": (0.08, 0.5), "fine": (0.01, 0.1)}
FLANK_POINTS = 16
TOL = 1e-6              # mm, for matching kernel geometry back to the numbers we asked for
BORE_RIM_SLACK = 0.01   # mm, how far past bore_rim_limit() a rim point may read and still
# count. 10 microns, not TOL: it must clear the kernel's post-boolean vertex/edge
# tolerance -- measured 1e-7 mm on both GearParams(bore_chamfer=0) and
# GearParams(bore_flat=0, bore_chamfer=0), 2026-09-26 -- by five orders of magnitude,
# and stay far below MIN_WALL (0.4 mm), the least clearance recess_radii() keeps between
# the rim and the next end-face edge.

_LOCK = threading.RLock()


def _load_malloc_trim() -> Callable[[int], int] | None:
    try:
        fn = ctypes.CDLL("libc.so.6").malloc_trim
    except (OSError, AttributeError):
        return None          # musl or macOS: nothing to do
    fn.argtypes = [ctypes.c_size_t]
    return fn


_MALLOC_TRIM = _load_malloc_trim()


def _release_arenas() -> None:
    """Hand freed heap back to the operating system after a build.

    OpenCascade churns through enormous numbers of short-lived allocations. glibc keeps
    the freed arenas to reuse and never returns them, so a worker that has built a few
    large gears looks like it is leaking and eventually meets the container memory
    limit. Measured over 40 distinct 160-199 tooth gears: 1578 MiB resident without
    this, 360 MiB with it -- far more than cache sizing is worth. Called after every
    export(): the byte cache that used to make some calls here a "miss" now lives in the
    parent process (D-06), so every call that reaches a worker at all is one by
    construction -- there is no cache left in this module to miss.
    """
    if _MALLOC_TRIM is not None:
        _MALLOC_TRIM(0)


def _polar(r: float, t: float) -> cq.Vector:
    return cq.Vector(r * math.cos(t), r * math.sin(t), 0)


def _fillet_corner(p0: cq.Vector, p1: cq.Vector, rf: float, rho: float,
                   gap_side: int, inside: bool = False) -> tuple[cq.Vector, cq.Vector, cq.Vector]:
    """Fillet of radius rho between an axis-centred circle of radius rf and the flank
    line p0 -> p1, where p0 lies on that circle.

    gap_side is -1 if the region being rounded lies clockwise of the line, +1 if
    anticlockwise. `inside=False` (the default, unchanged since Phase 7): the region
    lies outside the circle -- the tooth root fillet's case -- so the arc centre sits
    outside it, at |centre| = rf + rho. `inside=True` (D-05, added Phase 11 for a
    spoke sector's rim corners): the region lies inside the circle, so the centre sits
    inside it instead, at |centre| = rf - rho, and the near root of the quadratic is
    taken rather than the far one -- the mirror image of the outside case, both
    algebraically (a sign flip in the quadratic's constant term) and geometrically
    (hand-checked, 2026-09-29: R 10, line y = 1 inward, rho 1 gives centre
    (sqrt(77), 2), circle point (9.749960, 2.222222), line point (8.774964, 1.0)).
    The default path is float-for-float identical to before this parameter existed
    (rc = rf + rho is the same expression the old code built): the pre-v0.2 fixture
    replays byte-unchanged.

    Returns (tangent point on the circle, arc midpoint, tangent point on line).
    """
    u = (p1 - p0).normalized()
    n = cq.Vector(-u.y, u.x, 0) * gap_side
    q = p0 + n * rho                  # centre = q + t*u with |centre| = rc
    b = q.dot(u)
    rc = rf - rho if inside else rf + rho
    root = math.sqrt(max(0.0, b * b - (q.dot(q) - rc ** 2)))
    t = -b - root if inside else -b + root
    centre = q + u * t
    on_line = p0 + u * t
    on_root = centre * (rf / rc)
    mid = centre + ((on_line + on_root) * 0.5 - centre).normalized() * rho
    return on_root, mid, on_line


def _trochoid_outline(pr: Profile, curve: RootCurve) -> cq.Wire:
    """Closed gear outline whose root is the hob's trochoid: one spline per side through
    the `RootCurve`, then one involute spline from the same junction `Vector`, the tip
    arc, the mirror image, and the root arc to the next tooth. Six side faces per tooth
    where the radial outline has eight.

    The involute spline starts with the SAME `Vector` object the root spline ends on,
    never a recomputed one: a gap of 1e-6 mm silently opens a wire (PITFALLS 7), and a
    shared object has none. Its other radii run from the curve's own last radius, so
    the junction is one float (`calc.spline_start` returns it too). Built and read back
    through the oracle on 15,723 swept cases without a failure (19-RESEARCH F1), and on
    the 10,326 trochoid gears of the Phase 18 product by 19-02's `product` run.
    """
    pitch = 2 * math.pi / pr.z
    r0 = curve.points[-1][0]
    radii = [r0 + (pr.ra - r0) * (i / (FLANK_POINTS - 1)) ** 1.5 for i in range(FLANK_POINTS)]
    teeth = []
    for k in range(pr.z):
        c = k * pitch
        root_l = [_polar(r, c - h) for r, h in curve.points]
        root_r = [_polar(r, c + h) for r, h in reversed(curve.points)]
        flank_l = [root_l[-1]] + [_polar(r, c - pr.half_angle(r)) for r in radii[1:]]
        flank_r = [_polar(r, c + pr.half_angle(r)) for r in reversed(radii[1:])]
        flank_r.append(root_r[0])
        teeth.append((c, root_l, root_r, flank_l, flank_r))

    edges: list[cq.Edge] = []
    for k, (c, root_l, root_r, flank_l, flank_r) in enumerate(teeth):
        edges += [
            cq.Edge.makeSpline(root_l),
            cq.Edge.makeSpline(flank_l),
            cq.Edge.makeThreePointArc(flank_l[-1], _polar(pr.ra, c), flank_r[0]),
            cq.Edge.makeSpline(flank_r),
            cq.Edge.makeSpline(root_r),
        ]
        nxt = teeth[(k + 1) % pr.z]
        edges.append(cq.Edge.makeThreePointArc(
            root_r[-1], _polar(pr.rf, c + pitch / 2), nxt[1][0]))
    return cq.Wire.assembleEdges(edges)


def _outline(pr: Profile, fillet: float, curve: RootCurve | None = None) -> cq.Wire:
    """Closed gear outline with analytic root fillets.

    Each flank starts with a straight segment from the root circle: radial up to the
    base circle when the root lies inside it, extended as a short chord onto the
    involute when the fillet needs room (below the pitch circle on the default gear;
    calc.derive warns when the chord ends above it, naming the height). Fillet arcs are
    computed here rather than with OCCT's fillet operator, which is ~50x slower on a
    many-toothed outline.

    calc.spline_start places the spline's start, so the tip chamfer's cap reads the
    same radius the outline is built from.

    With a `curve` (calc.RootMode.curve, set only where the hob's root applies) the root
    is that curve instead and `fillet` is not read: the whole outline is
    `_trochoid_outline`. The radial body below is untouched, float for float, for every
    caller that passes none.
    """
    if curve is not None:
        return _trochoid_outline(pr, curve)
    r0 = spline_start(pr, fillet)  # where the involute spline starts
    straight = r0 > pr.rf + 1e-6
    radii = [r0 + (pr.ra - r0) * (i / (FLANK_POINTS - 1)) ** 1.5 for i in range(FLANK_POINTS)]
    pitch = 2 * math.pi / pr.z
    psi_root = pr.half_angle(pr.r_start)          # tooth half-angle where it meets the root

    teeth = []
    for k in range(pr.z):
        c = k * pitch
        left = [_polar(rho, c - pr.half_angle(rho)) for rho in radii]
        right = [_polar(rho, c + pr.half_angle(rho)) for rho in reversed(radii)]
        root_l, root_r = _polar(pr.rf, c - psi_root), _polar(pr.rf, c + psi_root)
        fl = fr = None
        if straight and fillet > 0:
            fl = _fillet_corner(root_l, left[0], pr.rf, fillet, -1)
            fr = _fillet_corner(root_r, right[-1], pr.rf, fillet, +1)
        teeth.append((c, left, right, root_l, root_r, fl, fr))

    edges: list[cq.Edge] = []
    for k, (c, left, right, root_l, root_r, fl, fr) in enumerate(teeth):
        if fl:
            edges.append(cq.Edge.makeThreePointArc(fl[0], fl[1], fl[2]))
            edges.append(cq.Edge.makeLine(fl[2], left[0]))
        elif straight:
            edges.append(cq.Edge.makeLine(root_l, left[0]))
        edges.append(cq.Edge.makeSpline(left))
        edges.append(cq.Edge.makeThreePointArc(left[-1], _polar(pr.ra, c), right[0]))
        edges.append(cq.Edge.makeSpline(right))
        if fr:
            edges.append(cq.Edge.makeLine(right[-1], fr[2]))
            edges.append(cq.Edge.makeThreePointArc(fr[2], fr[1], fr[0]))
            start = fr[0]
        else:
            if straight:
                edges.append(cq.Edge.makeLine(right[-1], root_r))
            start = root_r
        nxt = teeth[(k + 1) % pr.z]
        end = nxt[5][0] if nxt[5] else nxt[3]
        edges.append(cq.Edge.makeThreePointArc(start, _polar(pr.rf, c + pitch / 2), end))
    return cq.Wire.assembleEdges(edges)


# --- the part, one decision per step -------------------------------------------------

def _gear_blank(pr: Profile, fillet: float, face_width: float,
                curve: RootCurve | None = None) -> cq.Shape:
    """The toothed disc, before the face recesses and the bore."""
    face = cq.Face.makeFromWires(_outline(pr, fillet, curve))
    return cq.Solid.extrudeLinear(face, cq.Vector(0, 0, face_width))


def _cut_face_recesses(solid: cq.Shape, p: GearParams, rf: float) -> cq.Shape:
    """Annular groove in one or both faces, with filleted floors."""
    rr = recess_radii(p, rf)
    if not rr:
        return solid
    r_in, r_out = rr
    floor_z: list[float] = []
    if p.recess_sides in ("both", "bottom"):
        floor_z.append(p.recess_depth)
        solid = solid.cut(_ring(r_in, r_out, 0.0, p.recess_depth))
    if p.recess_sides in ("both", "top"):
        floor_z.append(p.face_width - p.recess_depth)
        solid = solid.cut(_ring(r_in, r_out, p.face_width - p.recess_depth, p.recess_depth))
    fillet = recess_fillet(p, rf)
    if fillet > 0:
        solid = _body(solid).fillet(fillet, _groove_floor_edges(solid, (r_in, r_out), floor_z))
    return solid


def _cut_bore(solid: cq.Shape, p: GearParams) -> cq.Shape:
    """Round, D-shaped or hexagonal bore, chamfered on both rims."""
    if p.bore_hex > 0:
        # circumscribed=True makes the polygon's diameter argument the across-flats (the
        # hexagon is drawn around that circle). The kernel's default puts a flat facing
        # +X -- the D-flat's side -- with a vertex on +-Y, and there is no rotation
        # parameter (planning probe, 2026-09-26).
        hole = (cq.Workplane("XY")
                .polygon(6, hex_across_flats(p), circumscribed=True)
                .extrude(p.face_width))
    elif p.bore_d > 0:
        r_bore = bore_radius(p)
        hole = cq.Workplane("XY").circle(r_bore).extrude(p.face_width)
        if p.bore_flat > 0:
            flat = p.bore_flat + p.bore_clearance          # flat to opposite side
            keep = cq.Workplane("XY").center(
                flat - 2 * r_bore, 0).rect(2 * r_bore, 2 * r_bore + 2)
            hole = hole.intersect(keep.extrude(p.face_width))
    else:
        return solid
    solid = solid.cut(_shape_of(hole))
    if p.bore_chamfer > 0:
        solid = _body(solid).chamfer(p.bore_chamfer, None, _bore_rim_edges(solid, p))
    return solid


def _cut_keyway(solid: cq.Shape, p: GearParams) -> cq.Shape:
    """A rectangular keyway slot through the full face width, flat floor, square floor
    corners (D-08) -- cut after _cut_bore has chamfered the rim, so the chamfer is
    notched and the keyway's own edges (two sides, floor) stay sharp (D-05).

    +Y is a quarter turn from the D-flat on +X, one fixed position stated here, not a
    field (D-01): the wall opposite the keyway is always the round wall, so the floor-
    to-wall distance derive() prints is bore_effective + keyway_depth whether or not a
    flat exists. The box starts on the axis, inside the bore, and ends at the floor.

    The order is not a style choice: chamfering the rim after the slot failed with
    "BRep_API: command not done" on a D-flat bore in every variant probed this session,
    while chamfer-then-cut built every time (178 faces / 508 edges on the default keyed
    D-flat link, research Pattern 1, 2026-09-27) -- D-06.
    """
    if not (p.keyway_width > 0 and p.keyway_depth > 0):
        # A keyway exists only with both fields set; 09-03's check() refuses a
        # half-set one before this ever runs.
        return solid
    w = keyway_width_effective(p)
    floor = bore_radius(p) + p.keyway_depth
    return solid.cut(cq.Solid.makeBox(w, floor, p.face_width, pnt=cq.Vector(-w / 2, 0, 0)))


def _hole_cutters(p: GearParams) -> list[cq.Solid]:
    """N cylinders of diameter hole_d, centred on the circle hole_circle_d, hole 0
    centred on +X (D-03: the D-flat's side, and polarArray's own default start).
    Through the full face width from z = 0. bore_clearance is not added -- a cutout is
    not a fit feature (Claude's Discretion, 11-CONTEXT.md)."""
    return [cq.Solid.makeCylinder(
                p.hole_d / 2, p.face_width,
                _polar(p.hole_circle_d / 2, 2 * math.pi * k / p.hole_count))
            for k in range(p.hole_count)]


def _spoke_sector(p: GearParams, rf: float, k: int, rho: float) -> cq.Face:
    """One sector of the spoke cutout, the gap between arm k and arm k + 1 (D-01,
    D-02): the annulus between the hub ring (radius rh) and the rim wall (radius rr),
    minus the two parallel-sided bars bounding it, each corner rounded by an analytic
    tangent arc baked into this 2D wire -- never OCCT's 3D fillet operator on the 4N
    vertical corner edges (D-05, L09's ~50x on a many-featured outline).

    Arm k sits at the nominal angle 2*pi*k/N (arm 0 on +X, D-03); k and k + 1 are
    never taken modulo N, so the last sector's angles run past 2*pi rather than
    wrapping back through 0 -- this is what keeps the hub arc anticlockwise and the
    rim arc clockwise for every sector, including the N = 1 case (one sector spanning
    the whole ring but for the single arm, a "C" shape).

    With rho > 0 the wire is: hub arc, hub corner arc, bar side, rim corner arc, rim
    arc, rim corner arc, bar side, hub corner arc -- eight edges, closing back to the
    start. With rho == 0 (sharp corners, no fillet field or one that rounds to 0) the
    four corner arcs collapse and the wire is just hub arc, bar side, rim arc, bar
    side -- the plain sector research's Pattern 2 describes before D-05's fillet.
    """
    n = p.spoke_count
    rh = p.hub_d / 2
    rr = rf - p.rim_wall
    o = p.spoke_width / 2
    th0 = 2 * math.pi * k / n
    th1 = 2 * math.pi * (k + 1) / n
    mid = (th0 + th1) / 2

    def foot(r: float, th: float, off: float) -> cq.Vector:
        # The point at radius r, offset `off` perpendicular to the radial direction
        # th: rotate (s, off) by th, s = sqrt(r^2 - off^2) so the point still lies on
        # the circle of radius r. off = +-spoke_width/2 places the two bar sides.
        s = math.sqrt(max(0.0, r * r - off * off))
        return cq.Vector(s * math.cos(th) - off * math.sin(th),
                         s * math.sin(th) + off * math.cos(th), 0)

    h0, r0 = foot(rh, th0, o), foot(rr, th0, o)     # arm k's +w/2 side
    h1, r1 = foot(rh, th1, -o), foot(rr, th1, -o)   # arm k+1's -w/2 side

    edges: list[cq.Edge] = []
    if rho > 0:
        hub_k = _fillet_corner(h0, r0, rh, rho, 1)
        hub_k1 = _fillet_corner(h1, r1, rh, rho, -1)
        rim_k1 = _fillet_corner(r1, h1, rr, rho, 1, inside=True)
        rim_k = _fillet_corner(r0, h0, rr, rho, -1, inside=True)
        edges.append(cq.Edge.makeThreePointArc(hub_k[0], _polar(rh, mid), hub_k1[0]))
        edges.append(cq.Edge.makeThreePointArc(hub_k1[0], hub_k1[1], hub_k1[2]))
        edges.append(cq.Edge.makeLine(hub_k1[2], rim_k1[2]))
        edges.append(cq.Edge.makeThreePointArc(rim_k1[2], rim_k1[1], rim_k1[0]))
        edges.append(cq.Edge.makeThreePointArc(rim_k1[0], _polar(rr, mid), rim_k[0]))
        edges.append(cq.Edge.makeThreePointArc(rim_k[0], rim_k[1], rim_k[2]))
        edges.append(cq.Edge.makeLine(rim_k[2], hub_k[2]))
        edges.append(cq.Edge.makeThreePointArc(hub_k[2], hub_k[1], hub_k[0]))
    else:
        edges.append(cq.Edge.makeThreePointArc(h0, _polar(rh, mid), h1))
        edges.append(cq.Edge.makeLine(h1, r1))
        edges.append(cq.Edge.makeThreePointArc(r1, _polar(rr, mid), r0))
        edges.append(cq.Edge.makeLine(r0, h0))
    return cq.Face.makeFromWires(cq.Wire.assembleEdges(edges))


def _spoke_cutters(p: GearParams, rf: float) -> list[cq.Solid]:
    """N sector prisms cut from the annular web between the hub ring and the rim wall
    (D-01), through the full face width. rho is spoke_fillet_effective(p), the value
    derive() prints -- model.py never recomputes the cap, so the part and the number
    cannot disagree (L08)."""
    rho = spoke_fillet_effective(p)
    return [cq.Solid.extrudeLinear(_spoke_sector(p, rf, k, rho), cq.Vector(0, 0, p.face_width))
            for k in range(p.spoke_count)]


def _cell_cutters(p: GearParams, rf: float) -> list[cq.Solid]:
    """Whole honeycomb cells: hexagonal prisms at hex_cells(p, rf)'s applied size and
    centres (D-07...D-09), flats on +-X and vertices on +-Y -- the hex bore's own
    convention (_cut_bore's polygon(circumscribed=True) call above). Exactly the cells
    calc.py enumerates, at exactly the size derive() prints, so the part and the
    printed number cannot disagree (L08)."""
    size, centres = hex_cells(p, rf)
    proto = _shape_of(cq.Workplane("XY").polygon(6, size, circumscribed=True)
                      .extrude(p.face_width))
    # _shape_of narrows val() to a Shape; translate() below must return the Solid the
    # extrude made, so the same modelling-defect guard narrows once more. Before
    # 16-REVIEW WR-01 this raised a bare TypeError, which _build_checked relabelled as
    # "try smaller fillets or chamfers" -- the catch-all a pipeline defect must never
    # wear (L35).
    if not isinstance(proto, cq.Solid):
        raise BuildError(_NOT_A_BODY.format(type(proto).__name__))
    return [proto.translate(cq.Vector(x, y, 0)) for x, y in centres]


def _cut_body(solid: cq.Shape, p: GearParams, pr: Profile) -> cq.Shape:
    """The one body-cutout pattern, every cutter of it subtracted in a single boolean
    cut -- never a per-cutter loop (ROADMAP SC1, research PITFALLS.md Pitfall 2). Runs
    after _cut_keyway and before _chamfer_tips: the recess floor fillet and the
    bore-rim chamfer are already baked geometry, so their selectors never see a cutout
    edge (research ARCHITECTURE.md Q1), and the tip step stays last (10 D-13). The
    spelling is measured, not assumed: bench/RESULTS.md "Honeycomb cell-count spike"
    timed star (cut(*prisms)), compound and fuse within 0.03 s of each other at the
    cap's cell count -- inside the run's own noise, never clearing D-24's 10% bar, so
    the default cut(*prisms) spelling stands. Only one branch ever runs
    (REQ-one-cutout-pattern, calc.check()'s one-pattern rule), so the cutter lists
    never mix.
    """
    if p.spoke_count > 0:
        cutters: list[cq.Solid] = _spoke_cutters(p, pr.rf)
    elif p.hole_count > 0:
        cutters = _hole_cutters(p)
    elif p.hex_cell > 0:
        cutters = _cell_cutters(p, pr.rf)
    else:
        return solid
    # No fuzzy-boolean tolerance is passed to cut(): a hole, a spoke sector or a
    # honeycomb cell can legitimately sit tangent to a recess wall (research
    # PITFALLS.md Pitfall 1), and every tangent case probed on the pinned kernel built
    # with this plain call -- a hole edge exactly on the recess's inner and outer
    # radius, a spoke's analytic hub/rim arcs tangent to each, both sharp and filleted,
    # a spoke web at exactly MIN_WALL on both sides with no recess at all, and a
    # honeycomb cell's own flat tangent to the recess wall (2026-09-29, see
    # test_a_cutter_tangent_to_a_recess_wall_or_fillet_builds_without_a_fuzzy_boolean).
    return solid.cut(*cutters)


def _chamfer_tips(solid: cq.Shape, p: GearParams, pr: Profile) -> cq.Shape:
    """An end-face edge break on the tooth-tip arcs: bore_chamfer's exact call and
    meaning, symmetric 45 degrees, c off the end face and c off the tip (D-03).

    The reading decided 2026-09-25: a 3D edge operation on the built solid, not a
    corner in _outline and not tip relief. The last step (D-13): the tip band is the
    region farthest from every other cut, and the selector can assume the final
    outline. The cost (bench/RESULTS.md "Tooth-tip chamfer spike"): about 12 s at 200
    teeth (400 edges), the same at any c -- the one v0.2 cut in L09's cost family,
    where the analytic remedy is ruled out by the reading.
    """
    c = tip_chamfer_effective(p)
    if c <= 0:
        return solid
    solid = _body(solid).chamfer(c, None, _tip_edges(solid, pr.ra, p.face_width))
    return solid


# --- picking kernel geometry back out ------------------------------------------------

_NOT_A_BODY = (
    "Geometry kernel returned a {} where a solid body was expected: "
    "a modelling defect in the build pipeline, not a parameter problem.")


# CadQuery 2.8.0 types every boolean result as Shape (Shape.cut -> Shape), and Shape
# declares neither fillet nor chamfer: they are Mixin3D's, which Solid and Compound
# carry. Measured on the default gear 2026-10-04: _gear_blank returns a Solid, and
# _cut_face_recesses and every later step a Compound; a step whose feature is off
# returns its input unchanged. So the pipeline's static type stays cq.Shape and the
# narrowing happens here, where Mixin3D is needed. It asserts the type the pipeline
# already guarantees (a Solid after _gear_blank, a Compound after every boolean), with
# the 44-record fixture replay (tests/regression) as the evidence beyond the default
# gear; a modelling-defect guard, never an answer (L26). A cast would claim the same and
# check nothing; this replaces five mypy suppressions.
def _body(shape: cq.Shape) -> cq.Solid | cq.Compound:
    if not isinstance(shape, cq.Solid | cq.Compound):
        raise BuildError(_NOT_A_BODY.format(type(shape).__name__))
    return shape


# Workplane.val() is typed Vector | Location | Shape | Sketch. Every Workplane this
# module extrudes holds a Shape; an empty stack would hand back the plane's origin, a
# Vector.
def _shape_of(wp: cq.Workplane) -> cq.Shape:
    value = wp.val()
    if not isinstance(value, cq.Shape):
        raise BuildError(_NOT_A_BODY.format(type(value).__name__))
    return value


def _ring(r_in: float, r_out: float, z0: float, height: float) -> cq.Shape:
    return _shape_of(cq.Workplane("XY").workplane(offset=z0)
                     .circle(r_out).circle(r_in).extrude(height))


def _groove_floor_edges(solid: cq.Shape, radii: tuple[float, ...],
                        floor_z: list[float]) -> list[cq.Edge]:
    """The circles where a groove wall meets its floor: a CIRCLE whose radius is within
    TOL of a groove radius and whose start point sits within TOL of a floor height.

    Runs only when the recess fillet is above zero, so an empty result here is a
    modelling defect, never an answer (D-15) -- a fillet that silently selects nothing
    must never ship an unfilleted floor. The body cutouts (Phase 11) are cut after this
    selector runs -- _cut_body follows _cut_face_recesses in _build -- so it never sees
    a cutout edge, proven for every pattern and bore shape by
    test_every_selector_takes_only_its_own_edges_with_a_body_cutout.
    """
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


def _bore_rim_edges(solid: cq.Shape, p: GearParams) -> list[cq.Edge]:
    """The bore opening on the two end faces.

    Selected by position, not by type: a D-bore rim is an arc plus a straight line, a
    hex rim six lines per face. The only other edges on an end face belong to a recess,
    and recess_radii() keeps at least MIN_WALL between the chamfered bore mouth and the
    recess, so a radius test separates them. The band comes from calc.bore_rim_limit(p),
    the exact geometric bound, plus BORE_RIM_SLACK's measured margin. This selector runs
    only when p.bore_chamfer > 0, so an empty result here is a modelling defect, never an
    answer (D-15): a chamfer that silently selects nothing must never ship an unchamfered
    part. A keyway's slot is cut after this selector runs (D-06), so its edges are never
    candidates here either.
    """
    lim = bore_rim_limit(p) + BORE_RIM_SLACK

    def on_rim(e: cq.Edge) -> bool:
        a, b = e.startPoint(), e.endPoint()
        if abs(a.z - b.z) > TOL or TOL < a.z < p.face_width - TOL:
            return False
        if max(math.hypot(a.x, a.y), math.hypot(b.x, b.y)) > lim:
            return False
        return all(math.hypot(q.x, q.y) < lim
                   for q in (e.positionAt(s / 4) for s in range(1, 4)))

    edges = [e for e in solid.Edges() if on_rim(e)]
    if not edges:
        raise BuildError(
            "Bore chamfer selected no bore-rim edges: a modelling defect in spur, not a "
            "conflict in these parameters. Set bore_chamfer to 0 to build this gear "
            "without it.")
    return edges


def _tip_edges(solid: cq.Shape, ra: float, face_width: float) -> list[cq.Edge]:
    """The tooth-tip arcs on the two end faces, selected by position (D-13): the tip
    arc is _outline's three-point arc across each tooth at radius ra, one per tooth on
    each end face, and no other edge of the solid is a CIRCLE at ra (measured on the
    selector matrix, every bore shape, 200 teeth and module 0.2 included).

    The end-face test has a measured reason: after a chamfer of c the tip land keeps
    2 x teeth arcs at ra, now sitting at z = c and z = face_width - c -- a radius test
    alone would pick those moved arcs again on a re-chamfer. Runs only while the applied
    chamfer is above 0, so an empty result here is a modelling defect, never an answer
    (L26): a chamfer that silently selects nothing must never ship an unchamfered part.
    """
    def on_tip(e: cq.Edge) -> bool:
        if e.geomType() != "CIRCLE" or abs(e.radius() - ra) >= TOL:
            return False
        a, b = e.startPoint(), e.endPoint()
        return (any(abs(a.z - z) < TOL for z in (0.0, face_width))
                and any(abs(b.z - z) < TOL for z in (0.0, face_width)))

    edges = [e for e in solid.Edges() if on_tip(e)]
    if not edges:
        raise BuildError(
            "Tip chamfer selected no tip-arc edges: a modelling defect in spur, not a "
            "conflict in these parameters. Set tip_chamfer to 0 to build this gear "
            "without it.")
    return edges


# --- build and export ----------------------------------------------------------------

def _build(p: GearParams) -> cq.Solid:
    pr = profile(p)
    # The one answer to "which root", the same call derive() makes, so the part and the
    # numbers cannot name different roots (PITFALLS 1). Only the curve crosses into this
    # module: the generator stays in calc.
    rm = root_mode(p, pr, requested=p.root_shape, rho=p.root_fillet)
    solid = _gear_blank(pr, root_fillet(p), p.face_width, rm.curve)
    solid = _cut_face_recesses(solid, p, pr.rf)
    solid = _cut_bore(solid, p)
    solid = _cut_keyway(solid, p)
    solid = _cut_body(solid, p, pr)
    solid = _chamfer_tips(solid, p, pr)

    solids = solid.Solids()
    if len(solids) != 1 or not solids[0].isValid():
        raise BuildError("Geometry kernel produced an invalid solid for these parameters.")
    return solids[0]


def _build_checked(p: GearParams) -> cq.Solid:
    try:
        return _build(p)
    except BuildError:
        raise
    except Exception as exc:  # OCCT raises assorted Standard_Failure subclasses
        raise BuildError(f"Geometry kernel failed ({type(exc).__name__}); "
                         "try smaller fillets or chamfers.") from exc


_build_cached = lru_cache(maxsize=int_env("SPUR_SOLID_CACHE", 4))(_build_checked)


def build(p: GearParams) -> cq.Solid:
    with _LOCK:
        return _build_cached(p)


def _write_export(shape: cq.Solid, p: GearParams, fmt: Format, quality: Quality) -> bytes:
    with tempfile.TemporaryDirectory(prefix="spur-") as d:
        path = Path(d) / f"{p.slug()}.{fmt}"
        if fmt == "stl":
            tol, ang = TESSELLATION[quality]
            # exportStl() attaches a triangulation to the solid it is called on.
            # _build_cached hands the same object to every caller for one GearParams,
            # and build() returns it after releasing _LOCK -- meshing it in place left
            # .BoundingBox() reading the mesh (zlen 7.5000 -> 7.5877 mm after a preview
            # export, 7.5196 after fine, L24) and made a preview after a fine export
            # reuse the fine mesh (46,278 triangles instead of 9,066). A copy keeps the
            # cached solid mesh-free for its whole life, at 1.4-17.6 ms per export
            # (L24) -- no positional argument to copy(): its one parameter is mesh,
            # default False, and copy(mesh=True) would carry a mesh across.
            shape.copy().exportStl(str(path), tolerance=tol, angularTolerance=ang,
                                   ascii=False, relative=False)
        else:
            # STEP export attaches no mesh, so the cached solid stays exact (measured
            # at planning: zlen 7.500000200000001 after export(p, "step")). No copy
            # needed here.
            shape.exportStep(str(path))
        return path.read_bytes()


def export(p: GearParams, fmt: Format, quality: Quality = "fine") -> bytes:
    with _LOCK:
        data = _write_export(_build_cached(p), p, fmt, quality)
        _release_arenas()
        return data
