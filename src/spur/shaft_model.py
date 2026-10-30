"""The shaft solid: the only shaft module that touches the CAD kernel.

Like model.py for the gear it is a doorway to cadquery and OCP, and it is reached only
through model (32-04 wires that), never imported by app, cli, pool, records or parts, so the
serving process stays free of OpenCascade (L17). It imports nothing from spur.model: model
imports it, and the reverse edge would be a cycle.

`build_shaft` reads every number from `derive_shaft` (the printed tip and root diameters
and the applied end chamfer) and the flank from `din5480.flank_half_angle`, and re-derives
none of them, so the part and the numbers printed for it cannot name different shafts (L08).
The solid is the nominal one; Phase 34 switches the thickness (ROADMAP Phase 32).

The walls are tested against an independent closed form (tests/shaft_oracle.py), never
against isValid() alone: the kernel returns an empty shape and a 3-face remnant that both
say valid, and the guards below turn each silent failure into a BuildError.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

import cadquery as cq

from . import din5480
from .build_errors import BuildError
from .shaft_calc import derive_shaft

if TYPE_CHECKING:
    from .shaft_params import ShaftParams

# Points on each flank, spaced as the gear's: a 16-point polyline read 1.2e-5 volume error
# against 4e-9 for a spline through the same points, and 599 faces against 95 on the
# default shaft (32-RESEARCH Alternatives). The r^1.5 spacing is the gear's, so the points
# bunch where the involute curves most.
FLANK_POINTS = 16
# mm, the repo's match tolerance: a copy, never model's, so shaft and gear stay uncoupled.
TOL = 1e-6
_SHAFT_DEFECT = "a modelling defect in spur, not a conflict in these parameters."
# mm. A cone start 3e-7 mm from the root circle hung the kernel for over 40 s in both
# operation orders (8.5 CPU-minutes and 2.1 GiB before it was killed), while about 70 other
# offsets from 1e-8 to 1e-3 built in 0.6 s (32-nearcap.log, 32-windows-radial*.log). It is a
# point, not a band, and 32-RESEARCH A3 says others may exist off the lattice, so the guard
# refuses the whole band around it. On the 0.001 lattice, with tip_d/2 and root_d/2 on
# 0.0005, the offset is 0 to float noise or a multiple of 0.0005 (32-01-floor-grid.log), so
# derive_shaft never reaches the band; tests/test_shaft_model.py proves it over the grid.
# The guard is a defect guard and not the pool's timeout because the CLI calls model.export
# in-process with no timeout (cli.py), so nothing else ends a hang there.
CONE_ROOT_BAND_LOW = 1e-9
CONE_ROOT_BAND_HIGH = 1e-4
# Relative slack on the volume bracket. The worst honest excursion outside it over the 22
# building rows of tests/test_shaft_model.py is 4.5e-9, at the two uncut rows, where the
# bracket has no width and it is the face area's own error (32-03-tolerances.log); every cut
# row lands inside. 1e-4 is 22000x over it. The 3-face remnant that said isValid() read 4.1e-2
# off (32-windows-axial.log), 410x over the slack; a cone past the tooth height reads 6.0e-4
# or more off the capped form (32-negatives.log).
VOLUME_BRACKET_SLACK = 1e-4


def _polar(r: float, t: float) -> cq.Vector:
    return cq.Vector(r * math.cos(t), r * math.sin(t), 0)


def _outline(m: float, z: int, xm: float, ra: float, rf: float) -> cq.Wire:
    """The closed end-face outline of the splined section, in the XY plane.

    Per tooth: a radial line where the base circle lies above the root (r_b > r_f, tooth
    counts up to 9 at real proportions), a spline through FLANK_POINTS points up the left
    flank, a three-point arc across the tip on the tip circle, the mirror flank, the mirror
    radial line, and one three-point arc on the root circle to the next tooth. The tip land
    is sharp and the root has no fillet: the solid says so in its warnings (D-01).
    """
    pitch = 2 * math.pi / z
    r_b = m * z * math.cos(din5480.ALPHA) / 2
    rs = max(rf, r_b)
    radii = [rs + (ra - rs) * (i / (FLANK_POINTS - 1)) ** 1.5 for i in range(FLANK_POINTS)]
    half_angles = [din5480.flank_half_angle(m, z, xm, r) for r in radii]
    h_root = half_angles[0]
    edges: list[cq.Edge] = []
    for k in range(z):
        c = k * pitch
        left = [_polar(r, c - h) for r, h in zip(radii, half_angles, strict=True)]
        right = [_polar(r, c + h) for r, h in zip(reversed(radii), reversed(half_angles),
                                                  strict=True)]
        if r_b > rf:
            edges.append(cq.Edge.makeLine(_polar(rf, c - h_root), left[0]))
        edges.append(cq.Edge.makeSpline(left))
        edges.append(cq.Edge.makeThreePointArc(left[-1], _polar(ra, c), right[0]))
        edges.append(cq.Edge.makeSpline(right))
        if r_b > rf:
            edges.append(cq.Edge.makeLine(right[-1], _polar(rf, c + h_root)))
        # The next tooth's first point is `(k + 1) * pitch - h_root`, spelled the same way
        # here, so the wire closes on bit-identical points.
        edges.append(cq.Edge.makeThreePointArc(
            _polar(rf, c + h_root), _polar(rf, c + pitch / 2),
            _polar(rf, (k + 1) * pitch - h_root)))
    return cq.Wire.assembleEdges(edges)


def _cone(ra: float, c: float, length: float, shank_length: float, shank_d: float) -> cq.Solid:
    """The cutter the end chamfer is intersected with: a revolved profile in the XZ plane.

    From the axis out along the end face to ra - c, up the 45 degree cone to (ra, c), then
    flat out past the widest radius and up past the far end. The flat top is what leaves a
    fused shank alone, and the cone starts on the end face at tip_d - 2*c and reaches tip_d
    at height c (32-RESEARCH Pattern 2).
    """
    big = max(ra, shank_d / 2) + 1.0
    top = length + shank_length
    points = [cq.Vector(0, 0, 0), cq.Vector(ra - c, 0, 0), cq.Vector(ra, 0, c),
              cq.Vector(big, 0, c), cq.Vector(big, 0, top), cq.Vector(0, 0, top)]
    wire = cq.Wire.makePolygon([*points, points[0]])
    return cq.Solid.revolve(wire, [], 360, cq.Vector(0, 0, 0), cq.Vector(0, 0, 1))


def _guard_cone_start(ra: float, rf: float, c: float) -> None:
    """Refuse a chamfer whose cone starts within the band around the root circle, before any
    kernel call: the kernel can hang there (see CONE_ROOT_BAND_LOW)."""
    offset = abs(ra - c - rf)
    if c > 0 and CONE_ROOT_BAND_LOW < offset < CONE_ROOT_BAND_HIGH:
        raise BuildError(f"The end chamfer's cone would start {offset:.1e} mm from the root "
                         f"circle, where the kernel can hang: {_SHAFT_DEFECT}")


def _guard_volume(solid: cq.Solid, area: float, ra: float, rf: float, c: float,
                  length: float, shank_length: float, shank_d: float) -> None:
    """Refuse a solid whose volume, length or end chamfer is not the shape that was asked for.

    isValid() is True for a 3-face remnant 4 percent off and for a cone that ate the root
    core, so the volume is bracketed from numbers the kernel did not produce here. The upper
    bound is the uncut prism and shank, from the face's own area. The cone removes at most c
    times the tooth area, because the disc of radius rf lies inside every cone section while
    c is at most the tooth height; past it the cone eats the core and the volume leaves the
    bracket (32-RESEARCH Pitfalls 3 and 5, L26).

    The bracket cannot see a missing chamfer: an uncut solid sits on its upper edge, and at
    0.001 mm the cut is smaller than the face area's own error (the heaviest shaft reads
    upper - volume = -0.215 mm^3, so refusing upper - volume <= 0 would refuse an honest
    part; 33-02-cut-probe.log). So the end face is read back, the same reading the tests use
    (`_end_face_radius`): its largest vertex radius must be ra - c, or ra with no chamfer.
    The probe reads it within 2e-13 mm of that on every honest row, and an uncut face is off
    by the whole chamfer, at least 0.001 mm, which is 1000 x TOL.
    """
    upper = area * length + math.pi * (shank_d / 2) ** 2 * shank_length
    lower = upper - c * (area - math.pi * rf ** 2)
    volume = solid.Volume()
    box = solid.BoundingBox()
    if (not lower * (1 - VOLUME_BRACKET_SLACK) <= volume <= upper * (1 + VOLUME_BRACKET_SLACK)
            or abs(box.zmax - box.zmin - (length + shank_length)) > TOL):
        raise BuildError(f"The shaft solid is not the shape that was asked for (volume "
                         f"{volume:.6g} mm^3 outside {lower:.6g} to {upper:.6g}): "
                         f"{_SHAFT_DEFECT}")
    ends = [f for f in solid.Faces() if f.geomType() == "PLANE"
            and abs(f.BoundingBox().zmax) <= TOL]
    radius = max((math.hypot(v.X, v.Y) for f in ends for v in f.Vertices()), default=0.0)
    if len(ends) != 1 or abs(radius - (ra - c)) > TOL:
        raise BuildError(f"The shaft's end face reaches {radius:.6g} mm, not the "
                         f"{ra - c:.6g} mm the end chamfer leaves: {_SHAFT_DEFECT}")


def build_shaft(p: ShaftParams) -> cq.Solid:
    """One valid solid for a validated shaft: the splined prism, the shank, the end chamfer.

    The free end sits at z = 0, the shank behind the splined length. The order is fixed:
    extrude, fuse the shank, intersect with the chamfer cone, and nothing cleans up after
    the fuse.
    - Fuse before intersect, because the reverse order returned a 3-face solid 4.1 percent
      off at splined_length = c + 5e-7 with a shank (32-windows-axial.log).
    - No cleaning step after the fuse, because it made shank_d == tip_d and shank_d ==
      root_d invalid while the volume still agreed to 4e-9 (32-negatives2.log).
    - No glue: it is 2x faster on the default but its semantics for a shank wider than the
      tip are unproven (32-RESEARCH A1).
    - No Solid.chamfer: it raised Standard_Failure for c >= 1.2 on the default
      (32-negatives.log); the cone is one boolean with no edge selector to come back empty
      (L26).
    """
    dims = derive_shaft(p)
    ra, rf = dims.tip_d / 2, dims.root_d / 2
    c = dims.end_chamfer_effective or 0.0
    xm = din5480.profile_shift(p.reference_d, p.module, p.teeth) * p.module
    _guard_cone_start(ra, rf, c)
    try:
        face = cq.Face.makeFromWires(_outline(p.module, p.teeth, xm, ra, rf))
        area = face.Area()
        body: cq.Shape = cq.Solid.extrudeLinear(face, cq.Vector(0, 0, p.splined_length))
        if p.shank_length > 0:
            shank = cq.Solid.makeCylinder(p.shank_d / 2, p.shank_length,
                                          cq.Vector(0, 0, p.splined_length))
            body = body.fuse(shank)
        if c > 0:
            body = body.intersect(_cone(ra, c, p.splined_length, p.shank_length, p.shank_d))
    except Exception as exc:  # OCCT raises assorted Standard_Failure subclasses
        # Never the gear's "try smaller fillets or chamfers": a shaft has no fillets, and
        # the same parameters fail the same way, so retrying or trimming changes nothing.
        raise BuildError(f"The shaft solid could not be built ({type(exc).__name__}): "
                         f"{_SHAFT_DEFECT}") from exc
    solids = body.Solids()
    if len(solids) != 1 or not solids[0].isValid():
        raise BuildError(f"The shaft solid is not one valid solid: {_SHAFT_DEFECT}")
    _guard_volume(solids[0], area, ra, rf, c, p.splined_length, p.shank_length, p.shank_d)
    return solids[0]
