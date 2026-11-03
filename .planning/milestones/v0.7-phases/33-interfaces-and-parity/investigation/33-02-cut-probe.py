"""What the shaft's chamfer guard can see: the volume bracket against an end-face read-back (33-02).

D-16 asks for a guard that refuses a chamfer the kernel never cut, so `end_chamfer_effective`
is never printed for a part that does not carry it (L08). The debt item's own next step was
`upper - volume <= 0`; this prints why the volume cannot carry that on the heaviest shaft, and
that the largest vertex radius of the one planar face at z = 0 can: it must equal
`tip_d/2 - c`, and an uncut face reaches `tip_d/2`.

Per row: the applied chamfer, `upper - volume` (the cut the volume shows) and its ratio to
`upper`, the end-face reading minus `tip_d/2 - c`, the CONE face count and the build time.
Then the debt's reproduction: the solid of `end_chamfer=0` read against the default's
`c = 1.0`.

Run from the repository root: `.venv/bin/python <this file>`.
"""

from __future__ import annotations

import math
import time

import cadquery as cq

from spur import din5480, shaft_model
from spur.shaft_calc import derive_shaft
from spur.shaft_params import ShaftParams

HEAVIEST = {"reference_d": 830.0, "module": 10.0, "teeth": 82, "splined_length": 500.0,
            "shank_d": 828.0, "shank_length": 500.0}
ROWS: dict[str, dict[str, float]] = {
    "default": {},
    "c=0.001": {"end_chamfer": 0.001},
    "c=0.01": {"end_chamfer": 0.01},
    "c=0.05": {"end_chamfer": 0.05},
    "c=0.0001": {"end_chamfer": 0.0001},
    "W6x0.5x10 c=0.001": {"reference_d": 6.0, "module": 0.5, "teeth": 10,
                          "end_chamfer": 0.001},
    "heaviest c=0.001": {**HEAVIEST, "end_chamfer": 0.001},
}


def end_face_radius(solid: cq.Solid) -> float:
    """The largest vertex radius of the one planar face lying at z = 0."""
    ends = [f for f in solid.Faces() if f.geomType() == "PLANE"
            and abs(f.BoundingBox().zmax) <= shaft_model.TOL]
    assert len(ends) == 1, len(ends)
    return max(math.hypot(v.X, v.Y) for v in ends[0].Vertices())


def face_area(p: ShaftParams) -> float:
    """The face area as build_shaft rebuilds it."""
    dims = derive_shaft(p)
    xm = din5480.profile_shift(p.reference_d, p.module, p.teeth) * p.module
    outline = shaft_model._outline(p.module, p.teeth, xm, dims.tip_d / 2, dims.root_d / 2)
    return cq.Face.makeFromWires(outline).Area()


def main() -> int:
    print(f"{'row':<20} {'c':>8} {'upper-volume mm^3':>18} {'/upper':>11} "
          f"{'end-face err mm':>16} {'CONE':>5} {'build s':>8}")
    for name, fields in ROWS.items():
        p = ShaftParams(**fields)
        dims = derive_shaft(p)
        c = dims.end_chamfer_effective or 0.0
        started = time.perf_counter()
        solid = shaft_model.build_shaft(p)
        elapsed = time.perf_counter() - started
        upper = (face_area(p) * p.splined_length
                 + math.pi * (p.shank_d / 2) ** 2 * p.shank_length)
        cones = sum(1 for f in solid.Faces() if f.geomType() == "CONE")
        err = end_face_radius(solid) - (dims.tip_d / 2 - c)
        print(f"{name:<20} {c:>8.4g} {upper - solid.Volume():>18.6g} "
              f"{(upper - solid.Volume()) / upper:>11.3e} {err:>16.3e} {cones:>5} "
              f"{elapsed:>8.2f}")
    p = ShaftParams(end_chamfer=0.0)
    dims = derive_shaft(p)
    uncut = end_face_radius(shaft_model.build_shaft(p)) - (dims.tip_d / 2 - 1.0)
    print(f"uncut reproduction: end_chamfer=0 solid read against c=1.0 -> end-face radius "
          f"minus (tip_d/2 - 1.0) = {uncut:.6g} mm")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
