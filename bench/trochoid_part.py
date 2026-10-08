"""Measures the hob's trochoid root in the kernel before the field exists (19-CONTEXT order).

ROADMAP "Order inside the phase" (PITFALLS 18) puts two spikes ahead of any schema change,
the `bench/tip_chamfer_spike.py` precedent (L29 measured the chamfer before its field
existed): `chamfer` re-bisects L29's kernel law across the spline-to-spline junction of the
hob root, and `heaviest` times the heaviest low-tooth rows the composed sweep allows against
SPUR_BUILD_TIMEOUT. Both run on a trochoid outline this module builds itself from the Phase
18 `RootCurve`, through the shipped pipeline steps after the blank, so what is timed and
bisected is the part 19-04 will ship, not a stand-in.

It is not part of `make verify`: a run takes minutes and its timings depend on the host,
and a timing assertion on shared hardware would flap (`bench/build_time.py`'s stance). Run it
as `.venv/bin/python -m bench.trochoid_part <scenario>` from the repo root. It prints Markdown
and exits 1 when the verdict fails.
"""

from __future__ import annotations

import argparse
import math
import os
import platform
import subprocess
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from importlib import metadata
from pathlib import Path

import cadquery as cq

from bench import machine_facts
from bench.tip_chamfer_spike import chamfered, tip_arcs
from spur import model
from spur.calc import (
    TIP_CHAMFER_MARGIN,
    Cutter,
    Profile,
    RootCurve,
    profile,
    root_mode,
    trochoid_root,
)
from spur.params import GearParams

TOL = model.TOL
_TESTS = Path(__file__).resolve().parents[1] / "tests"


# --- the part -----------------------------------------------------------------------

def trochoid_outline(pr: Profile, curve: RootCurve) -> cq.Wire:
    """Closed gear outline whose root is the hob's trochoid, six edges per tooth (the
    radial path's `model._outline` has eight): the root spline up to the junction, the
    involute spline from it to the tip, the tip arc, the mirror involute and root splines,
    and the root arc to the next tooth.

    This is the spike's copy; 19-04 moves the builder into `model.py` and 19-09 replaces
    this one with it, so there is one definition by the phase's end (the 11-05 precedent).

    The left involute spline starts with the SAME `Vector` object the root spline ends on,
    never a recomputed one: a gap of 1e-6 mm silently opens the wire (PITFALLS 7), and a
    shared object has none. Its other radii start from the curve's own last radius.
    """
    pitch = 2 * math.pi / pr.z
    r0 = curve.points[-1][0]
    radii = [r0 + (pr.ra - r0) * (i / (model.FLANK_POINTS - 1)) ** 1.5
             for i in range(model.FLANK_POINTS)]
    teeth = []
    for k in range(pr.z):
        c = k * pitch
        root_l = [model._polar(r, c - h) for r, h in curve.points]
        root_r = [model._polar(r, c + h) for r, h in reversed(curve.points)]
        flank_l = [root_l[-1]] + [model._polar(r, c - pr.half_angle(r)) for r in radii[1:]]
        flank_r = [model._polar(r, c + pr.half_angle(r)) for r in reversed(radii[1:])]
        flank_r.append(root_r[0])
        teeth.append((c, root_l, root_r, flank_l, flank_r))

    edges: list[cq.Edge] = []
    for k, (c, root_l, root_r, flank_l, flank_r) in enumerate(teeth):
        edges += [
            cq.Edge.makeSpline(root_l),
            cq.Edge.makeSpline(flank_l),
            cq.Edge.makeThreePointArc(flank_l[-1], model._polar(pr.ra, c), flank_r[0]),
            cq.Edge.makeSpline(flank_r),
            cq.Edge.makeSpline(root_r),
        ]
        nxt = teeth[(k + 1) % pr.z]
        edges.append(cq.Edge.makeThreePointArc(
            root_r[-1], model._polar(pr.rf, c + pitch / 2), nxt[1][0]))
    return cq.Wire.assembleEdges(edges)


def trochoid_curve(p: GearParams, rho: float) -> tuple[Cutter, RootCurve]:
    """The cutter and the hob's root curve for `p` at tip radius `rho` mm, from the one
    predicate (`root_mode`). `RootMode.curve` does not exist until 19-04, so the curve is
    read back with `trochoid_root` -- the same call `root_mode` made and discarded
    (18-REVIEW IN-02). A gear the trochoid does not apply to raises, naming the reason."""
    rm = root_mode(p, profile(p), requested="trochoid", rho=rho)
    if rm.mode != "trochoid" or rm.cutter is None:
        raise ValueError(f"not a trochoid gear at tip radius {rho:g} mm: {rm.reason}")
    curve = trochoid_root(rm.cutter)
    if curve is None:
        raise ValueError(f"root_mode said trochoid but trochoid_root found no curve "
                         f"at tip radius {rho:g} mm")
    return rm.cutter, curve


def trochoid_blank(p: GearParams, rho: float) -> tuple[cq.Shape, Cutter, RootCurve]:
    """The toothed disc with the trochoid root, before the recesses and the bore."""
    cut, curve = trochoid_curve(p, rho)
    face = cq.Face.makeFromWires(trochoid_outline(profile(p), curve))
    return cq.Solid.extrudeLinear(face, cq.Vector(0, 0, p.face_width)), cut, curve


def trochoid_cap(p: GearParams, curve: RootCurve) -> float:
    """The tip chamfer cap 19-04 will ship (RESEARCH Pattern 8): the radial model's two
    bounds, and the kernel's own limit read from the junction of this curve."""
    pr = profile(p)
    return round(min(0.45 * p.face_width, pr.ra - pr.r,
                     pr.ra - curve.points[-1][0] - TIP_CHAMFER_MARGIN), 3)


def _one_solid(shape: cq.Shape) -> cq.Solid:
    solids = shape.Solids()
    if len(solids) != 1:
        raise ValueError(f"the kernel produced {len(solids)} solids, not one")
    if not solids[0].isValid():
        raise ValueError("the kernel produced an invalid solid")
    return solids[0]


def trochoid_part(p: GearParams, rho: float, chamfer: float | None = None) -> cq.Solid:
    """The part as `model._build` assembles it, with the trochoid blank in place of
    `_gear_blank`: face recesses, bore, keyway, body cutout, then the tip chamfer -- the
    requested `p.tip_chamfer` capped by `trochoid_cap`, or `chamfer` when given (the
    bisection asks for sizes the cap would refuse). Exactly one valid solid, or a
    ValueError naming what failed."""
    pr = profile(p)
    solid, _, curve = trochoid_blank(p, rho)
    solid = model._cut_face_recesses(solid, p, pr.rf)
    solid = model._cut_bore(solid, p)
    solid = model._cut_keyway(solid, p)
    solid = model._cut_body(solid, p, pr)
    part = _one_solid(solid)
    c = chamfer if chamfer is not None else min(p.tip_chamfer, trochoid_cap(p, curve))
    if c <= 0:
        return part
    arcs = tip_arcs(part, pr.ra, p.face_width)
    if not arcs:
        raise ValueError("the tip chamfer selected no tip-arc edges")
    chamfered_part, why = chamfered(part, c, arcs)
    if chamfered_part is None:
        raise ValueError(f"the kernel refused a tip chamfer of {c:g} mm: {why}")
    return chamfered_part


# --- reading the root back out of the solid -----------------------------------------

def root_edges(solid: cq.Shape, pr: Profile, teeth: int) -> list[cq.Edge]:
    """The hob-root splines on the z = 0 face: BSPLINE edges lying on that face with one
    end on the root circle. Two per tooth, and the count is asserted before any sample is
    read -- a selector that selects nothing must fail, not read zero (L26)."""
    def on_root(e: cq.Edge) -> bool:
        if e.geomType() != "BSPLINE":
            return False
        a, b = e.startPoint(), e.endPoint()
        return (abs(a.z) < TOL and abs(b.z) < TOL
                and any(abs(math.hypot(v.x, v.y) - pr.rf) < TOL for v in (a, b)))

    edges = [e for e in solid.Edges() if on_root(e)]
    if len(edges) != 2 * teeth:
        raise ValueError(f"selected {len(edges)} root edges, expected {2 * teeth}")
    return edges


def oracle_reading(solid: cq.Shape, p: GearParams, rho_used: float) -> float:
    """The largest |reading| in mm of the Phase 18 swept-cutter oracle over the two root
    edges of tooth 0, 41 samples each, with the tip radius the cutter actually used. The
    oracle shares no code with `spur`, so this is the part's root judged independently of
    the maths that drew it."""
    if str(_TESTS) not in sys.path:
        sys.path.insert(0, str(_TESTS))
    from trochoid_oracle import clearance  # the tests/ root, put on the path just above

    pr = profile(p)
    tooth0 = [e for e in root_edges(solid, pr, p.teeth)
              if abs(math.atan2(e.positionAt(0.5).y, e.positionAt(0.5).x)) < math.pi / p.teeth]
    if len(tooth0) != 2:
        raise ValueError(f"tooth 0 has {len(tooth0)} root edges, expected 2")
    worst = 0.0
    for e in tooth0:
        points = tuple((math.hypot(v.x, v.y), abs(math.atan2(v.y, v.x)))
                       for v in (e.positionAt(i / 40) for i in range(41)))
        readings = clearance(points, teeth=p.teeth, module=p.module,
                             pressure_angle=p.pressure_angle,
                             profile_shift=p.profile_shift, backlash=p.backlash,
                             rho=rho_used, neighbours=True)
        worst = max(worst, max(abs(v) for v in readings))
    return worst


# --- the chamfer law across the junction --------------------------------------------

def chamfer_verdict(last_building: float, predicted: float,
                    margin: float = TIP_CHAMFER_MARGIN) -> str:
    """"optimistic" when the largest chamfer the kernel built sits more than `margin`
    inside pred = ra - R_join, "conservative" when it built more than `margin` past it,
    else "on the law". Optimistic is the only failing verdict: the cap would let a user ask
    for a chamfer the kernel cannot cut (L03, L08). Conservative is allowed -- L29's sixth
    row built 0.04 mm past its prediction."""
    if last_building < predicted - margin:
        return "optimistic"
    if last_building > predicted + margin:
        return "conservative"
    return "on the law"


@dataclass(frozen=True)
class ChamferRow:
    label: str
    fields: dict[str, object]
    rho: float             # cutter tip radius asked for, mm
    scratch_pred: float    # ra - R_join as the planning-time scratch run read it, mm


# The switches bench.trochoid._gear sets: a bore the small gears cannot take, no recess.
_M1: dict[str, object] = {"module": 1, "bore_d": 0, "bore_flat": 0, "bore_chamfer": 0,
                          "recess_sides": "none"}
# Typed out, never generated from calc (a row that moved with the code under test would
# agree with it). pred = ra - R_join from the planning-time scratch run, every row mode
# trochoid; "tangent" and "crossing" are the junction's join. Default backlash 0.10.
CHAMFER_ROWS: list[ChamferRow] = [
    ChamferRow("default 19 teeth, m 1.75, 25 deg, x 0", {}, 0.0, 3.1945),  # tangent
    ChamferRow("default 19 teeth, m 1.75, 25 deg, x 0", {}, 0.5, 3.0962),  # tangent
    ChamferRow("100 teeth, m 1, 14.5 deg, x -0.6",
               {**_M1, "teeth": 100, "pressure_angle": 14.5, "profile_shift": -0.6},
               0.0, 1.7215),   # tangent
    ChamferRow("100 teeth, m 1, 14.5 deg, x -0.6",
               {**_M1, "teeth": 100, "pressure_angle": 14.5, "profile_shift": -0.6},
               0.5, 1.5411),   # tangent
    ChamferRow("30 teeth, m 1, 14.5 deg, x -0.6",
               {**_M1, "teeth": 30, "pressure_angle": 14.5, "profile_shift": -0.6},
               0.0, 0.8084),   # crossing
    ChamferRow("30 teeth, m 1, 14.5 deg, x -0.6",
               {**_M1, "teeth": 30, "pressure_angle": 14.5, "profile_shift": -0.6},
               0.5, 0.8492),   # crossing
    ChamferRow("12 teeth, m 1, 20 deg, x 0",
               {**_M1, "teeth": 12, "pressure_angle": 20, "profile_shift": 0},
               0.0, 1.3244),   # crossing
    ChamferRow("12 teeth, m 1, 20 deg, x 0",
               {**_M1, "teeth": 12, "pressure_angle": 20, "profile_shift": 0},
               0.5, 1.3543),   # crossing
    ChamferRow("10 teeth, m 1, 20 deg, x 0",
               {**_M1, "teeth": 10, "pressure_angle": 20, "profile_shift": 0},
               0.0, 1.2433),   # crossing
    ChamferRow("10 teeth, m 1, 20 deg, x 0",
               {**_M1, "teeth": 10, "pressure_angle": 20, "profile_shift": 0},
               0.5, 1.2826),   # crossing
    ChamferRow("8 teeth, m 1, 20 deg, x 0",
               {**_M1, "teeth": 8, "pressure_angle": 20, "profile_shift": 0},
               0.0, 1.1552),   # crossing
    ChamferRow("8 teeth, m 1, 20 deg, x 0",
               {**_M1, "teeth": 8, "pressure_angle": 20, "profile_shift": 0},
               0.5, 1.2040),   # crossing
    # The two rows whose junction lies above the pitch circle (R_join 3.0994 and 3.0183 mm
    # against r 3.0, ra - r = 1.0): pred is the binding cap there and nowhere else.
    ChamferRow("6 teeth, m 1, 14.5 deg, x 0",
               {**_M1, "teeth": 6, "pressure_angle": 14.5, "profile_shift": 0},
               0.0, 0.9006),   # crossing
    ChamferRow("6 teeth, m 1, 14.5 deg, x 0",
               {**_M1, "teeth": 6, "pressure_angle": 14.5, "profile_shift": 0},
               0.5, 0.9817),   # crossing
]


def boundary(fields: dict[str, object], rho: float) -> tuple[float, float, float, str, float]:
    """(last_ok, first_fail, pred, why, worst_oracle): the 20-step bisection of
    `bench.tip_chamfer_spike.boundary` (L29's count) on the trochoid part, between 0 and
    hi = 0.45 x face_width, which sits past every row's pred on purpose -- the kernel's own
    limit, not the cap's. pred = ra - R_join read from the row's own curve; worst_oracle is
    the Phase 18 oracle's reading of the unchamfered part's tooth-0 root, mm.

    A chamfer that builds at hi returns first_fail = inf and why "builds at the top".
    """
    p = GearParams.model_validate(fields)
    pr = profile(p)
    cut, curve = trochoid_curve(p, rho)
    pred = pr.ra - curve.points[-1][0]
    hi = 0.45 * p.face_width

    bare = trochoid_part(p, rho, chamfer=0.0)
    worst_oracle = oracle_reading(bare, p, cut.rho)
    arcs = tip_arcs(bare, pr.ra, p.face_width)
    if not arcs:
        raise ValueError("no tip-arc edges to chamfer")

    solid, why = chamfered(bare, hi, arcs)
    if solid is not None:
        return hi, float("inf"), pred, "builds at the top", worst_oracle

    lo, first_fail, last_why = 0.0, hi, why
    for _ in range(20):
        mid = 0.5 * (lo + first_fail)
        built, reason = chamfered(bare, mid, arcs)
        if built is not None:
            lo = mid
        else:
            first_fail, last_why = mid, reason
    return lo, first_fail, pred, last_why, worst_oracle


def _host_state(start: datetime, end: datetime, load_before: tuple[float, float, float],
                load_after: tuple[float, float, float]) -> list[str]:
    versions = ", ".join(f"{dist} {metadata.version(dist)}"
                         for dist in ("cadquery", "cadquery-ocp"))
    head = subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                          capture_output=True, text=True, check=True).stdout.strip()
    stamp = "%Y-%m-%dT%H:%M:%SZ"
    return [
        "#### Host state",
        "",
        f"- Machine: {machine_facts()}",
        f"- Python: {platform.python_version()}",
        f"- Kernel: {versions}",
        f"- HEAD: `{head}`",
        f"- Read {start.strftime(stamp)} to {end.strftime(stamp)}",
        f"- Load averages at start: {load_before[0]:.2f}, {load_before[1]:.2f}, "
        f"{load_before[2]:.2f}; at end: {load_after[0]:.2f}, {load_after[1]:.2f}, "
        f"{load_after[2]:.2f}",
        "",
    ]


def run_chamfer() -> int:
    """Bisect every row of CHAMFER_ROWS, print them all, then judge. Everything is
    computed before the verdict reads any of it (bench/latency.py's rule)."""
    start, load_before = datetime.now(UTC), os.getloadavg()
    results = []
    for row in CHAMFER_ROWS:
        p = GearParams.model_validate(row.fields)
        pr = profile(p)
        _, curve = trochoid_curve(p, row.rho)
        last_ok, first_fail, pred, why, worst = boundary(row.fields, row.rho)
        caps = min((0.45 * p.face_width, "0.45 x face_width"),
                   (pr.ra - pr.r, "ra - r"),
                   (pred - TIP_CHAMFER_MARGIN, "ra - R_join"))
        results.append((row, curve, last_ok, first_fail, pred, why, worst, caps[1]))
    end, load_after = datetime.now(UTC), os.getloadavg()

    print("\n".join(_host_state(start, end, load_before, load_after)))
    print("#### Bisection (20 halvings between 0 and 0.45 x face_width)")
    print()
    print("| Gear | Tip radius (mm) | Join | R_join (mm) | pred = ra - R_join | last ok "
          "| first fail | last ok - pred | Verdict | Binding cap | Worst oracle (mm) |")
    print("|---|---|---|---|---|---|---|---|---|---|---|")
    verdicts = []
    for row, curve, last_ok, first_fail, pred, _, worst, binds in results:
        verdict = chamfer_verdict(last_ok, pred)
        verdicts.append((row, verdict))
        fail = "inf" if first_fail == float("inf") else f"{first_fail:.7f}"
        print(f"| {row.label} | {row.rho:g} | {curve.join} | {curve.points[-1][0]:.4f} "
              f"| {pred:.7f} | {last_ok:.7f} | {fail} | {last_ok - pred:+.2e} | {verdict} "
              f"| {binds} | {worst:.2e} |")
    print()
    print("First-failure reasons: " + "; ".join(
        f"{row.label} @ {row.rho:g}: {why}" for row, _, _, _, _, why, _, _ in results))
    print()

    optimistic = [f"{row.label} @ {row.rho:g}" for row, v in verdicts if v == "optimistic"]
    conservative = [f"{row.label} @ {row.rho:g}" for row, v in verdicts
                    if v == "conservative"]
    binding = [f"{row.label} @ {row.rho:g}" for row, *_, binds in results
               if binds == "ra - R_join"]
    print(f"Binding cap is ra - R_join on: {'; '.join(binding) or 'no row'}.")
    if optimistic:
        print(f"Verdict: law broken ({'; '.join(optimistic)})")
        return 1
    print(f"Verdict: law holds -- {len(verdicts) - len(conservative)} rows on the law, "
          f"{len(conservative)} conservative ({'; '.join(conservative) or 'none'}).")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m bench.trochoid_part",
                                     description=__doc__)
    sub = parser.add_subparsers(dest="scenario", required=True)
    sub.add_parser("chamfer", help="the tip chamfer's kernel limit across the junction")
    parser.parse_args(argv)
    return run_chamfer()


if __name__ == "__main__":
    sys.exit(main())
