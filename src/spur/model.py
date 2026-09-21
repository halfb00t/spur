"""CadQuery solid construction and STL/STEP export.

OpenCascade isn't safe to drive from several threads at once, so every kernel call
goes through one lock. Results are cached per parameter set: the UI asks for the
same gear repeatedly (preview, then STL, then STEP).
"""

from __future__ import annotations

import math
import tempfile
import threading
from functools import lru_cache
from pathlib import Path
from typing import Literal

import cadquery as cq

from .calc import Profile, bore_radius, profile, recess_radii, root_fillet
from .params import GearParams

Format = Literal["stl", "step"]
Quality = Literal["preview", "fine"]

# (linear deflection mm, angular deflection rad) for STL tessellation
TESSELLATION: dict[str, tuple[float, float]] = {"preview": (0.08, 0.5), "fine": (0.01, 0.1)}
FLANK_POINTS = 16

_LOCK = threading.RLock()


class BuildError(RuntimeError):
    """The CAD kernel could not produce a valid solid for these parameters."""


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


def _build(p: GearParams) -> cq.Solid:
    pr = profile(p)
    rfil = root_fillet(p)
    face = cq.Face.makeFromWires(_outline(pr, rfil))
    solid: cq.Shape = cq.Solid.extrudeLinear(face, cq.Vector(0, 0, p.face_width))

    rr = recess_radii(p, pr.rf)
    if rr:
        r_in, r_out = rr
        floors = []
        if p.recess_sides in ("both", "bottom"):
            floors.append((0.0, p.recess_depth))
        if p.recess_sides in ("both", "top"):
            floors.append((p.face_width - p.recess_depth, p.face_width - p.recess_depth))
        for z0, _ in floors:
            ring = (cq.Workplane("XY").workplane(offset=z0)
                    .circle(r_out).circle(r_in).extrude(p.recess_depth).val())
            solid = solid.cut(ring)
        if p.recess_fillet > 0:
            zs = [f for _, f in floors]
            edges = [e for e in solid.Edges()
                     if e.geomType() == "CIRCLE"
                     and min(abs(e.radius() - r_in), abs(e.radius() - r_out)) < 1e-6
                     and any(abs(e.startPoint().z - z) < 1e-6 for z in zs)]
            solid = solid.fillet(p.recess_fillet, edges)

    if p.bore_d > 0:
        R = bore_radius(p)
        hole = cq.Workplane("XY").circle(R).extrude(p.face_width)
        if p.bore_flat > 0:
            flat = p.bore_flat + p.bore_clearance          # flat to opposite side
            keep = cq.Workplane("XY").center(flat - R - R, 0).rect(2 * R, 2 * R + 2)
            hole = hole.intersect(keep.extrude(p.face_width))
        solid = solid.cut(hole.val())
        if p.bore_chamfer > 0:
            lim = R + 0.01

            def on_bore_rim(e: cq.Edge) -> bool:
                a, b = e.startPoint(), e.endPoint()
                if abs(a.z - b.z) > 1e-6 or 1e-6 < a.z < p.face_width - 1e-6:
                    return False
                if max(math.hypot(a.x, a.y), math.hypot(b.x, b.y)) > lim:
                    return False
                return all(math.hypot(q.x, q.y) < lim
                           for q in (e.positionAt(s / 4) for s in range(1, 4)))

            edges = [e for e in solid.Edges() if on_bore_rim(e)]
            solid = solid.chamfer(p.bore_chamfer, None, edges)

    solids = solid.Solids()
    if len(solids) != 1 or not solids[0].isValid():
        raise BuildError("Geometry kernel produced an invalid solid for these parameters.")
    return solids[0]


@lru_cache(maxsize=32)
def _build_cached(p: GearParams) -> cq.Solid:
    try:
        return _build(p)
    except BuildError:
        raise
    except Exception as exc:  # OCCT raises assorted Standard_Failure subclasses
        raise BuildError(f"Geometry kernel failed ({type(exc).__name__}); "
                         "try smaller fillets or chamfers.") from exc


def build(p: GearParams) -> cq.Solid:
    with _LOCK:
        return _build_cached(p)


@lru_cache(maxsize=32)
def _export_cached(p: GearParams, fmt: Format, quality: Quality) -> bytes:
    shape = _build_cached(p)
    with tempfile.TemporaryDirectory(prefix="spur-") as d:
        path = Path(d) / f"{p.slug()}.{fmt}"
        if fmt == "stl":
            tol, ang = TESSELLATION[quality]
            shape.exportStl(str(path), tolerance=tol, angularTolerance=ang,
                            ascii=False, relative=False)
        else:
            shape.exportStep(str(path))
        return path.read_bytes()


def export(p: GearParams, fmt: Format, quality: Quality = "fine") -> bytes:
    with _LOCK:
        return _export_cached(p, fmt, quality)
