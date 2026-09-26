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
    bore_radius,
    bore_rim_limit,
    profile,
    recess_fillet,
    recess_radii,
    root_fillet,
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
# GearParams(bore_flat=0, bore_chamfer=0), 2026-09-26 -- by three orders of magnitude,
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
                   gap_side: int) -> tuple[cq.Vector, cq.Vector, cq.Vector]:
    """Fillet of radius rho between the root circle (radius rf, centred on the axis)
    and the flank line p0 -> p1, where p0 lies on the root circle.

    gap_side is -1 if the tooth gap is clockwise of the line, +1 if anticlockwise.
    Returns (tangent point on root circle, arc midpoint, tangent point on line).
    """
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


def _outline(pr: Profile, fillet: float) -> cq.Wire:
    """Closed gear outline with analytic root fillets.

    Each flank starts with a straight segment from the root circle: radial up to the
    base circle when the root lies inside it, extended as a short chord onto the
    involute when the fillet needs room (the chord sits in the non-working root zone
    and deviates from the involute by microns). Fillet arcs are computed here rather
    than with OCCT's fillet operator, which is ~50x slower on a many-toothed outline.
    """
    r_line = max(pr.rb, pr.rf + 2.0 * fillet) if fillet > 0 else pr.rb
    r_line = min(r_line, pr.rf + 0.5 * (pr.ra - pr.rf))
    r0 = max(r_line, pr.r_start)                  # where the involute spline starts
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

def _gear_blank(pr: Profile, fillet: float, face_width: float) -> cq.Shape:
    """The toothed disc, before the face recesses and the bore."""
    face = cq.Face.makeFromWires(_outline(pr, fillet))
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
        # Shape declares no fillet/chamfer: they are on Mixin3D, which every Solid and
        # Compound carries. _build() re-checks we still have exactly one valid solid.
        solid = solid.fillet(fillet, _groove_floor_edges(solid, (r_in, r_out), floor_z))  # type: ignore[attr-defined]
    return solid


def _cut_bore(solid: cq.Shape, p: GearParams) -> cq.Shape:
    """Round or D-shaped bore, chamfered on both rims."""
    if p.bore_d <= 0:
        return solid
    r_bore = bore_radius(p)
    hole = cq.Workplane("XY").circle(r_bore).extrude(p.face_width)
    if p.bore_flat > 0:
        flat = p.bore_flat + p.bore_clearance          # flat to opposite side
        keep = cq.Workplane("XY").center(flat - 2 * r_bore, 0).rect(2 * r_bore, 2 * r_bore + 2)
        hole = hole.intersect(keep.extrude(p.face_width))
    solid = solid.cut(hole.val())  # type: ignore[arg-type]  # .val() is typed as a 4-way union
    if p.bore_chamfer > 0:
        solid = solid.chamfer(  # type: ignore[attr-defined]  # see _cut_face_recesses
            p.bore_chamfer, None, _bore_rim_edges(solid, p))
    return solid


# --- picking kernel geometry back out ------------------------------------------------

def _ring(r_in: float, r_out: float, z0: float, height: float) -> cq.Shape:
    return (cq.Workplane("XY").workplane(offset=z0)
            .circle(r_out).circle(r_in).extrude(height).val())  # type: ignore[return-value]


def _groove_floor_edges(solid: cq.Shape, radii: tuple[float, ...],
                        floor_z: list[float]) -> list[cq.Edge]:
    """The circles where a groove wall meets its floor: a CIRCLE whose radius is within
    TOL of a groove radius and whose start point sits within TOL of a floor height.

    Runs only when the recess fillet is above zero, so an empty result here is a
    modelling defect, never an answer (D-15) -- a fillet that silently selects nothing
    must never ship an unfilleted floor. Phase 11's cutouts put new circles on the
    recessed floor and must re-prove this separating invariant (research PITFALLS.md
    Pitfall 4).
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

    Selected by position, not by type: a D-bore rim is an arc plus a straight line. The
    only other edges on an end face belong to a recess, and recess_radii() keeps at
    least MIN_WALL plus the chamfer between that and the bore, so a radius test
    separates them. The band comes from calc.bore_rim_limit(p), the exact geometric
    bound, plus BORE_RIM_SLACK's measured margin. This selector runs only when
    p.bore_chamfer > 0, so an empty result here is a modelling defect, never an answer
    (D-15): a chamfer that silently selects nothing must never ship an unchamfered part.
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


# --- build and export ----------------------------------------------------------------

def _build(p: GearParams) -> cq.Solid:
    pr = profile(p)
    solid = _gear_blank(pr, root_fillet(p), p.face_width)
    solid = _cut_face_recesses(solid, p, pr.rf)
    solid = _cut_bore(solid, p)

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
