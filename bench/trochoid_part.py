"""Measures the hob's trochoid root in the kernel (19-CONTEXT order; 19-09 moved it onto the part).

ROADMAP "Order inside the phase" (PITFALLS 18) put two spikes ahead of any schema change,
the `bench/tip_chamfer_spike.py` precedent (L29 measured the chamfer before its field
existed): `chamfer` re-bisects L29's kernel law across the spline-to-spline junction of the
hob root, and `heaviest` times the heaviest low-tooth rows the composed sweep allows against
SPUR_BUILD_TIMEOUT. They ran on a trochoid outline this module built itself from the Phase
18 `RootCurve`. That copy moved into `spur.model` in 19-04, and since 19-09 this module keeps
no outline of its own: blanks are `model._gear_blank` / `model._outline`, parts are
`model._build_checked` with `root_shape="trochoid"`, so what is timed and bisected is the
part that ships (the 11-05 precedent: one definition by the phase's end).

It is not part of `make verify`: a run takes minutes and its timings depend on the host,
and a timing assertion on shared hardware would flap (`bench/build_time.py`'s stance). Run it
as `.venv/bin/python -m bench.trochoid_part <scenario>` from the repo root. It prints Markdown
and exits 1 when the verdict fails.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import os
import platform
import subprocess
import sys
import time
from bisect import bisect_right
from collections import Counter
from collections.abc import Callable, Sequence
from concurrent.futures import ProcessPoolExecutor
from contextlib import nullcontext
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from functools import partial
from importlib import metadata
from itertools import pairwise
from multiprocessing import get_context
from pathlib import Path
from statistics import median
from unittest.mock import patch

import cadquery as cq
from pydantic import ValidationError

from bench import machine_facts
from bench.build_time import DEFAULT_SWEEP, Timing, stl_size
from bench.tip_chamfer_spike import chamfered, tip_arcs
from bench.trochoid import OracleCase, _oracle_cases, sweep_cases
from spur import int_env, model
from spur.build_errors import BuildError
from spur.calc import (
    MIN_TIP_FDM,
    TIP_CHAMFER_MARGIN,
    TROCHOID_JOIN_EPS,
    Cutter,
    Profile,
    RootCurve,
    _junction,
    _trochoid_point,
    cutter,
    profile,
    root_fillet,
    root_mode,
    spline_start,
    trochoid_root,
)
from spur.params import GearParams

TOL = model.TOL
_TESTS = Path(__file__).resolve().parents[1] / "tests"


# --- the part -----------------------------------------------------------------------

Tooth = tuple[float, list[cq.Vector], list[cq.Vector], list[cq.Vector], list[cq.Vector]]


def outline_teeth(pr: Profile, curve: RootCurve) -> list[Tooth]:
    """Every tooth's points as (centre angle, root_l, root_r, flank_l, flank_r): the root
    spline up to the junction, the involute spline from it to the tip and their mirrors.

    A measuring helper, not an outline: it makes no edge. It keeps the points as the curve
    gives them, before `model._trochoid_teeth` applies ROOT_ARC_MIN, because the root-arc
    chord and the closed-form area are read from the unruled points (`arc`, `product`).

    The left involute spline starts with the SAME `Vector` object the root spline ends on,
    never a recomputed one: a gap of 1e-6 mm silently opens the wire (PITFALLS 7), and a
    shared object has none. Its other radii start from the curve's own last radius.
    """
    pitch = 2 * math.pi / pr.z
    r0 = curve.points[-1][0]
    radii = [r0 + (pr.ra - r0) * (i / (model.FLANK_POINTS - 1)) ** 1.5
             for i in range(model.FLANK_POINTS)]
    teeth: list[Tooth] = []
    for k in range(pr.z):
        c = k * pitch
        root_l = [model._polar(r, c - h) for r, h in curve.points]
        root_r = [model._polar(r, c + h) for r, h in reversed(curve.points)]
        flank_l = [root_l[-1]] + [model._polar(r, c - pr.half_angle(r)) for r in radii[1:]]
        flank_r = [model._polar(r, c + pr.half_angle(r)) for r in reversed(radii[1:])]
        flank_r.append(root_r[0])
        teeth.append((c, root_l, root_r, flank_l, flank_r))
    return teeth


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


def extrude_outline(p: GearParams, curve: RootCurve) -> cq.Solid:
    """The shipped outline of `curve` (`model._outline`, its guards included) as a face,
    extruded over the face width. For the hand-made curves of `arc`, `product` and `waist`,
    which have no `GearParams` that would produce them."""
    face = cq.Face.makeFromWires(model._outline(profile(p), 0.0, curve))
    return cq.Solid.extrudeLinear(face, cq.Vector(0, 0, p.face_width))


def trochoid_blank(p: GearParams, rho: float) -> tuple[cq.Shape, Cutter, RootCurve]:
    """The toothed disc with the trochoid root, before the recesses and the bore: the
    blank `model._build` starts from, area guard included."""
    cut, curve = trochoid_curve(p, rho)
    return model._gear_blank(profile(p), 0.0, p.face_width, curve), cut, curve


def _one_solid(shape: cq.Shape) -> cq.Solid:
    solids = shape.Solids()
    if len(solids) != 1:
        raise ValueError(f"the kernel produced {len(solids)} solids, not one")
    if not solids[0].isValid():
        raise ValueError("the kernel produced an invalid solid")
    return solids[0]


def trochoid_part(p: GearParams, rho: float, chamfer: float | None = None) -> cq.Solid:
    """The part as the product builds it, `model._build_checked` with `root_shape` trochoid
    and the tip radius `rho` as `root_fillet`: face recesses, bore, keyway, body cutout and
    the tip chamfer under the shipped cap. With `chamfer` given (the bisection asks for
    sizes the cap would refuse) the part is built with `tip_chamfer` 0 and chamfered here
    at that size, unless it is 0. Exactly one valid solid, or a BuildError / ValueError
    naming what failed."""
    asked = {**p.model_dump(), "root_shape": "trochoid", "root_fillet": rho}
    if chamfer is None:
        return model._build_checked(GearParams.model_validate(asked))
    part = model._build_checked(GearParams.model_validate({**asked, "tip_chamfer": 0.0}))
    if chamfer <= 0:
        return part
    arcs = tip_arcs(part, profile(p).ra, p.face_width)
    if not arcs:
        raise ValueError("the tip chamfer selected no tip-arc edges")
    chamfered_part, why = chamfered(part, chamfer, arcs)
    if chamfered_part is None:
        raise ValueError(f"the kernel refused a tip chamfer of {chamfer:g} mm: {why}")
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


def tooth0_root_edges(solid: cq.Shape, p: GearParams) -> list[cq.Edge]:
    """The two root splines of the tooth whose centre lies on the x axis."""
    edges = [e for e in root_edges(solid, profile(p), p.teeth)
             if abs(math.atan2(e.positionAt(0.5).y, e.positionAt(0.5).x)) < math.pi / p.teeth]
    if len(edges) != 2:
        raise ValueError(f"tooth 0 has {len(edges)} root edges, expected 2")
    return edges


def oracle_reading(solid: cq.Shape, p: GearParams, rho_used: float, samples: int = 40) -> float:
    """The largest |reading| in mm of the Phase 18 swept-cutter oracle over the two root
    edges of tooth 0, `samples` + 1 positions on each (41 by default), with the tip radius
    the cutter actually used. The oracle shares no code with `spur`, so this is the part's
    root judged independently of the maths that drew it."""
    if str(_TESTS) not in sys.path:
        sys.path.insert(0, str(_TESTS))
    from trochoid_oracle import clearance  # the tests/ root, put on the path just above

    worst = 0.0
    for e in tooth0_root_edges(solid, p):
        points = tuple((math.hypot(v.x, v.y), abs(math.atan2(v.y, v.x)))
                       for v in (e.positionAt(i / samples) for i in range(samples + 1)))
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


# --- the heaviest allowed low-tooth rows ----------------------------------------------

# The largest gear the trochoid can apply to at the field's most extreme pressure angle and
# shift: it needs rb > rf (`root_mode` ignores the request otherwise, 18 D-02), and with
# rb = r cos(alpha) and rf = r - m (1.25 - x) that reads z < 2 (1.25 - x) / (1 - cos(alpha)),
# which is 116.1 at 14.5 degrees and x -0.6. So 116 teeth is the heaviest part a
# `root_shape="trochoid"` request can change; the 200-tooth rows of the composed sweep are
# ignored-and-warned under a request, and L37's 29.42 s row is untouched by construction.
CORNER: dict[str, object] = {"teeth": 116, "pressure_angle": 14.5, "profile_shift": -0.6}


def corner_rows() -> list[dict[str, object]]:
    """Every row of `bench/sweeps/composed.json`, in file order, moved to CORNER."""
    raw: list[dict[str, object]] = json.loads(
        (DEFAULT_SWEEP.parent / "composed.json").read_text())
    return [{**row, **CORNER} for row in raw]


# Two light module-10 rows beside the heavy ones: the bare corner gear and the corner gear
# with the chamfer at its largest and both recesses (19-01).
LIGHTER_ROWS: list[dict[str, object]] = [
    {**CORNER, "module": 10},
    {**CORNER, "module": 10, "tip_chamfer": 3, "recess_sides": "both"},
]


def _label(fields: dict[str, object]) -> str:
    return " ".join(f"{k}={v}" for k, v in fields.items())


@dataclass(frozen=True)
class TimedRow:
    label: str
    mode: str                  # "radial" or "trochoid"
    timing: Timing | None      # None: the build failed, see `error`
    error: str
    oracle: float | None       # trochoid only: the Phase 18 oracle's worst reading, mm


def _time_row(label: str, mode: str, p: GearParams,
              build: Callable[[], cq.Solid]) -> tuple[TimedRow, cq.Solid | None]:
    """One request as a worker pays it: a cold build (no cache), then the fine STL and the
    STEP export, each timed with `time.perf_counter()`. A build the kernel or the outline
    refuses is a row with its reason, never a dropped row."""
    t0 = time.perf_counter()
    try:
        solid = build()
    except (BuildError, ValueError) as exc:
        return TimedRow(label, mode, None, f"{type(exc).__name__}: {exc}", None), None
    build_s = time.perf_counter() - t0
    t0 = time.perf_counter()
    stl = model._write_export(solid, p, "stl", "fine")
    stl_s = time.perf_counter() - t0
    t0 = time.perf_counter()
    model._write_export(solid, p, "step", "fine")
    step_s = time.perf_counter() - t0
    timing = Timing(label, build_s, stl_s, step_s, *stl_size(stl))
    return TimedRow(label, mode, timing, "", None), solid


def run_heaviest() -> int:
    """Time every corner row radial and trochoid, print them all, then judge. A row
    `GearParams` refuses is printed with its sentence, never silently dropped; nothing is
    trimmed, re-run or re-picked until it passes."""
    timeout = int_env("SPUR_BUILD_TIMEOUT", 30)
    start, load_before = datetime.now(UTC), os.getloadavg()

    refused: list[tuple[str, str]] = []
    timed: list[TimedRow] = []
    for fields in [*corner_rows(), *LIGHTER_ROWS]:
        label = _label(fields)
        try:
            p = GearParams.model_validate(fields)
        except ValidationError as exc:
            refused.append((label, str(exc.errors()[0]["msg"]).replace("\n", " ")))
            continue
        radial, _ = _time_row(label, "radial", p, partial(model._build_checked, p))
        timed.append(radial)
        trochoid, solid = _time_row(label, "trochoid", p,
                                    partial(trochoid_part, p, p.root_fillet))
        if solid is not None:
            rho_used = trochoid_curve(p, p.root_fillet)[0].rho
            trochoid = TimedRow(label, "trochoid", trochoid.timing, "",
                                oracle_reading(solid, p, rho_used))
        timed.append(trochoid)
    end, load_after = datetime.now(UTC), os.getloadavg()

    print("\n".join(_host_state(start, end, load_before, load_after)))
    print(f"SPUR_BUILD_TIMEOUT: {timeout} s; a cold request is one build plus the slower "
          "of the fine STL and the STEP export.")
    print()
    print("#### Timings")
    print()
    print("| Parameter set | Mode | Build (s) | Fine STL (s) | STEP (s) "
          f"| Build + slower export (s) | Trochoid / radial | Inside {timeout} s "
          "| Oracle, tooth 0 (mm) |")
    print("|---|---|---|---|---|---|---|---|---|")
    radial_of: dict[str, Timing] = {
        r.label: r.timing for r in timed if r.mode == "radial" and r.timing is not None}
    for r in timed:
        if r.timing is None:
            print(f"| {r.label} | {r.mode} | **FAILED** | | | | | **NO** | {r.error} |")
            continue
        t = r.timing
        base = radial_of.get(r.label)
        ratio = (f"{t.worst_request / base.worst_request:.2f}"
                 if r.mode == "trochoid" and base is not None else "--")
        oracle = f"{r.oracle:.2e}" if r.oracle is not None else "--"
        print(f"| {r.label} | {r.mode} | {t.build:.2f} | {t.stl:.2f} | {t.step:.2f} "
              f"| {t.worst_request:.2f} | {ratio} | "
              f"{'yes' if t.inside(timeout) else '**NO**'} | {oracle} |")
    print()
    if refused:
        print("Refused by `GearParams` at the corner, not timed:")
        print()
        for label, sentence in refused:
            print(f"- `{label}`: {sentence}")
        print()
    measured = [(r, r.timing) for r in timed if r.timing is not None]
    trochoid_only = [m for m in measured if m[0].mode == "trochoid"]
    for name, pool in (("Heaviest", measured), ("Heaviest trochoid", trochoid_only)):
        if pool:
            row, t = max(pool, key=lambda m: m[1].worst_request)  # first on a tie: file order
            print(f"**{name}:** {row.label} ({row.mode}) -- {t.worst_request:.2f} s "
                  f"of {timeout} s.")
    failed = [r for r in timed if r.timing is None or not r.timing.inside(timeout)]
    return 1 if failed else 0


# --- the two spline-deviation methods and the kernel bar (19-02) ----------------------

def _rising_radii(reference: Sequence[tuple[float, float]]) -> list[float]:
    radii = [math.hypot(x, y) for x, y in reference]
    if len(radii) < 2 or any(lo >= hi for lo, hi in pairwise(radii)):
        raise ValueError("the reference's distance from the origin must strictly rise "
                         "from vertex to vertex (every root curve and flank does)")
    return radii


def _worst_distance(samples: Sequence[tuple[float, float]],
                    reference: Sequence[tuple[float, float]], *, to_segments: bool) -> float:
    """The largest, over `samples`, of the distance to the nearest reference vertex or
    (`to_segments`) the nearest point of the reference polyline.

    The search starts at the item whose radius range holds the sample's radius and walks
    outward while an item's radius gap is still below the best distance found: the
    distance from the origin changes by at most the distance between two points, so no
    item with a larger gap can be nearer. That makes it exact and linear where a scan of
    the 20,001-point reference per sample would cost 4 million distances a gear, and it
    is why the reference must rise in radius.
    """
    radii = _rising_radii(reference)
    last = len(reference) - (2 if to_segments else 1)

    def distance(px: float, py: float, i: int) -> float:
        ax, ay = reference[i]
        if not to_segments:
            return math.hypot(px - ax, py - ay)
        ex, ey = reference[i + 1][0] - ax, reference[i + 1][1] - ay
        t = max(0.0, min(1.0, ((px - ax) * ex + (py - ay) * ey) / (ex * ex + ey * ey)))
        return math.hypot(px - (ax + t * ex), py - (ay + t * ey))

    worst = 0.0
    for px, py in samples:
        r = math.hypot(px, py)
        start = min(max(bisect_right(radii, r) - 1, 0), last)
        best = distance(px, py, start)
        for step in (-1, 1):
            i = start + step
            while 0 <= i <= last and max(radii[i] - r, r - radii[i + int(to_segments)], 0.0) < best:
                best = min(best, distance(px, py, i))
                i += step
        worst = max(worst, best)
    return worst


def deviation_a(samples: Sequence[tuple[float, float]],
                reference: Sequence[tuple[float, float]]) -> float:
    """Method A: the largest distance from a sample to the NEAREST VERTEX of the reference.
    STACK's shipped-flank figures (6.0e-5 and 1.0e-4 mm) are this, so they carry half the
    reference's own vertex spacing as a floor and are not a deviation (19-RESEARCH F2)."""
    return _worst_distance(samples, reference, to_segments=False)


def deviation_b(samples: Sequence[tuple[float, float]],
                reference: Sequence[tuple[float, float]]) -> float:
    """Method B: the largest distance from a sample to the reference POLYLINE (segment-wise,
    projection clamped). STACK's trochoid figures (3.6 to 4.0e-5 mm) are this, and it is
    the one a bar rests on: it has no floor from the reference's spacing beyond the
    polyline's own sagitta (about 1e-10 mm at 20,001 points)."""
    return _worst_distance(samples, reference, to_segments=True)


# The bars L33 D-06 allows the kernel tier, as multiples of the module (mm per mm of module).
LISTED_BARS = (1e-3, 2e-3, 5e-3, 1e-2)


def proposed_bar(worst_per_module: float) -> float:
    """The smallest listed bar (per module) that is at least 10x `worst_per_module`, the
    worst spline error per module: the L33 D-06 rule, "put to the human if under about
    10x". None qualifying is a question for the human and not a default, so it raises."""
    for bar in LISTED_BARS:
        if bar >= 10 * worst_per_module:
            return bar
    raise ValueError(f"no listed bar {LISTED_BARS} has 10x headroom over the worst spline "
                     f"error per module {worst_per_module:g}")


def third_digit_units(value: float, quoted: float) -> float:
    """|value - quoted| in units of the third significant digit of `quoted`: 1.0 means the
    two differ by one in the third digit (3.98e-5 against a quoted 3.99e-5)."""
    return abs(value - quoted) / 10.0 ** (math.floor(math.log10(quoted)) - 2)


SPLINE_SAMPLES = 2000     # positionAt(i / 2000): `spline` prints the 14-tooth row at 200, 2,000
# and 20,000 positions; 200 under-reads and 2,000 has converged
KERNEL_SAMPLES = 400      # per root edge for the independent oracle: 41 positions read 0.72
# of the converged figure on the module-10 row (`spline`'s kernel table); 401 read it to 4
# digits, and the whole seven-row `spline` run takes about 70 s
REFERENCE_POINTS = 20_001  # STACK's dense reference
CONVERGENCE_POSITIONS = (200, 2000, 20000)


def dense_root(cut: Cutter) -> list[tuple[float, float]]:
    """The hob's trochoid at 20,001 contact-normal angles, uniform in tan(beta) like the
    16 points of `RootCurve` (the roll angle is linear in it), from the root circle to the
    junction, as folded Cartesian points: x = R cos h, y = R sin h with h the half-angle
    from the tooth centre, so a sample taken from either flank folds onto it."""
    junction = _junction(cut, TROCHOID_JOIN_EPS)
    if junction is None:
        raise ValueError("no junction for this cutter")
    beta_stop = junction[0]
    s_stop = math.tan(beta_stop)
    n = REFERENCE_POINTS
    betas = [math.atan(s_stop * i / (n - 1)) for i in range(n - 1)] + [beta_stop]
    points = [_trochoid_point(cut, beta) for beta in betas]
    return [(r * math.cos(h), r * math.sin(h)) for r, h in points]


def edge_samples(e: cq.Edge, n: int) -> list[tuple[float, float]]:
    """n + 1 positions along an edge on the z = 0 face, folded onto y >= 0 (the right
    flank's mirror image) so left and right root splines read against one reference."""
    return [(v.x, abs(v.y)) for v in (e.positionAt(i / n) for i in range(n + 1))]


def spline_deviation(edges: Sequence[cq.Edge], reference: Sequence[tuple[float, float]],
                     n: int = SPLINE_SAMPLES) -> float:
    """Method B over the given root edges: the kernel spline's own error against the
    dense curve it interpolates, mm."""
    return max(deviation_b(edge_samples(e, n), reference) for e in edges)


def vertex_gap(reference: Sequence[tuple[float, float]]) -> float:
    """The largest distance between neighbouring reference vertices: method A cannot read
    below half of it."""
    return max(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in pairwise(reference))


@dataclass(frozen=True)
class KernelRow:
    label: str
    fields: dict[str, object]
    rho: float                 # tip radius asked for, mm


# Typed out, never generated from calc. 19-RESEARCH F3's seven rows; the module-0.2 row is
# the worst per module that research saw, the module-10 row the worst in mm. Default
# backlash 0.10 throughout: the deviation does not move with it (0.0 and 0.1 read the
# same to 1e-12 on rows 2 to 4, 19-02 exploration).
KERNEL_ROWS: list[KernelRow] = [
    KernelRow("default 19 teeth, m 1.75, 25 deg, x 0", {}, 0.5),
    KernelRow("8 teeth, m 1, 20 deg, x 0",
              {**_M1, "teeth": 8, "pressure_angle": 20, "profile_shift": 0}, 0.38),
    KernelRow("10 teeth, m 1, 20 deg, x 0",
              {**_M1, "teeth": 10, "pressure_angle": 20, "profile_shift": 0}, 0.38),
    KernelRow("14 teeth, m 1, 20 deg, x 0",
              {**_M1, "teeth": 14, "pressure_angle": 20, "profile_shift": 0}, 0.38),
    KernelRow("6 teeth, m 1, 14.5 deg, x 0",
              {**_M1, "teeth": 6, "pressure_angle": 14.5, "profile_shift": 0}, 0.0),
    KernelRow("30 teeth, m 0.2, 14.5 deg, x -0.6",
              {**_M1, "module": 0.2, "teeth": 30, "pressure_angle": 14.5,
               "profile_shift": -0.6}, 0.5),
    KernelRow("30 teeth, m 10, 14.5 deg, x -0.6",
              {**_M1, "module": 10, "teeth": 30, "pressure_angle": 14.5,
               "profile_shift": -0.6}, 0.5),
]
STACK_TROCHOID_ROWS = (1, 2, 3)         # KERNEL_ROWS the three STACK figures belong to
STACK_TROCHOID_MM = (3.58e-5, 3.89e-5, 3.99e-5)   # 19-RESEARCH F2 quoting STACK, module 1
# Where the tripwire sits: a module-1 row (a 0.05 mm shift reads 0.011 mm, which a bar
# scaling with the module passes at module 10) and the module-10 row to show it.
TRIPWIRE_ROWS = (2, 6)
TRIPWIRE_SHIFT_MM = 0.05


@dataclass(frozen=True)
class KernelReading:
    row: KernelRow
    module: float
    rho_used: float
    join: str
    oracle_41: float       # the 19-01 reading: 41 positions per edge
    oracle: float          # KERNEL_SAMPLES + 1 positions per edge
    b_same: float          # method B on those same positions
    b_converged: float     # method B at SPLINE_SAMPLES + 1 positions
    a_converged: float     # method A at SPLINE_SAMPLES + 1 positions
    spacing_floor: float   # half the reference's largest vertex gap, mm
    tripwire: float | None


def read_kernel_row(index: int) -> KernelReading:
    row = KERNEL_ROWS[index]
    p = GearParams.model_validate(row.fields)
    solid, cut, curve = trochoid_blank(p, row.rho)
    reference = dense_root(cut)
    edges = tooth0_root_edges(solid, p)
    return KernelReading(
        row, p.module, cut.rho, curve.join,
        oracle_reading(solid, p, cut.rho),
        oracle_reading(solid, p, cut.rho, KERNEL_SAMPLES),
        spline_deviation(edges, reference, KERNEL_SAMPLES),
        spline_deviation(edges, reference),
        max(deviation_a(edge_samples(e, SPLINE_SAMPLES), reference) for e in edges),
        vertex_gap(reference) / 2,
        oracle_reading(solid, p, cut.rho + TRIPWIRE_SHIFT_MM, KERNEL_SAMPLES)
        if index in TRIPWIRE_ROWS else None)


# (teeth, module, STACK's quoted figure in mm); STACK does not state the pressure angle
def convergence(index: int) -> list[tuple[int, float]]:
    """Method B on one kernel row at CONVERGENCE_POSITIONS positions per root edge."""
    row = KERNEL_ROWS[index]
    p = GearParams.model_validate(row.fields)
    solid, cut, _ = trochoid_blank(p, row.rho)
    reference, edges = dense_root(cut), tooth0_root_edges(solid, p)
    return [(n, spline_deviation(edges, reference, n)) for n in CONVERGENCE_POSITIONS]


STACK_FLANK_MM = ((12, 1.0, 6.0e-5), (19, 1.75, 1.0e-4))


def flank_deviation(p: GearParams, exponent: float) -> tuple[float, float, float]:
    """(method A, method B, half the reference's largest vertex gap) for the radial path's
    tooth-0 left involute spline against a 20,001-point reference whose radii are
    r0 + (ra - r0) (i / 20,000) ** exponent. 1.5 is the shipped spline's own spacing, 1.0
    is uniform in radius: STACK does not say which its reference used."""
    pr = profile(p)
    r0 = spline_start(pr, root_fillet(p))
    radii = [r0 + (pr.ra - r0) * (i / (model.FLANK_POINTS - 1)) ** 1.5
             for i in range(model.FLANK_POINTS)]
    spline = cq.Edge.makeSpline([model._polar(r, -pr.half_angle(r)) for r in radii])
    reference = [(r * math.cos(pr.half_angle(r)), r * math.sin(pr.half_angle(r)))
                 for r in (r0 + (pr.ra - r0) * (i / (REFERENCE_POINTS - 1)) ** exponent
                           for i in range(REFERENCE_POINTS))]
    samples = edge_samples(spline, SPLINE_SAMPLES)
    return (deviation_a(samples, reference), deviation_b(samples, reference),
            vertex_gap(reference) / 2)


def run_spline() -> int:
    """Reconcile the two research files' methods, then read the kernel tier on seven rows
    and the tripwire. Everything is computed before the verdict reads any of it."""
    start, load_before = datetime.now(UTC), os.getloadavg()
    readings = [read_kernel_row(i) for i in range(len(KERNEL_ROWS))]
    flank_gears = [GearParams.model_validate({**_M1, "teeth": 12, "pressure_angle": 20}),
                   GearParams.model_validate({**_M1, "teeth": 12, "pressure_angle": 25}),
                   GearParams.model_validate({**_M1, "teeth": 8, "pressure_angle": 25}),
                   GearParams()]
    flanks = [(p, exponent, flank_deviation(p, exponent))
              for p in flank_gears for exponent in (1.5, 1.0)]
    steps = convergence(STACK_TROCHOID_ROWS[-1])
    end, load_after = datetime.now(UTC), os.getloadavg()

    print("\n".join(_host_state(start, end, load_before, load_after)))
    print(f"Positions per spline: {SPLINE_SAMPLES + 1} for the deviation figures (method "
          f"B converges there, see the table below), {KERNEL_SAMPLES + 1} per root edge for the "
          "oracle against method B on the same positions, 41 for the 19-01 oracle reading. "
          f"Reference: {REFERENCE_POINTS:,} points.")
    print()
    print("#### Reconciliation: STACK's trochoid figures (module 1, mm)")
    print()
    print("| Gear | Join | STACK | Method B | B off by (units of the 3rd digit) "
          "| Method A | Half the reference's largest vertex gap |")
    print("|---|---|---|---|---|---|---|")
    misses = []
    for index, quoted in zip(STACK_TROCHOID_ROWS, STACK_TROCHOID_MM, strict=True):
        r = readings[index]
        units = third_digit_units(r.b_converged, quoted)
        if units > 1:
            misses.append(r.row.label)
        print(f"| {r.row.label}, tip radius {r.rho_used:g} | {r.join} | {quoted:.2e} "
              f"| {r.b_converged:.4e} | {units:.2f} | {r.a_converged:.4e} "
              f"| {r.spacing_floor:.2e} |")
    print()
    print("#### Reconciliation: STACK's shipped-flank figures (mm)")
    print()
    print("| Gear | STACK | Reference spacing | Method A | Half the largest vertex gap "
          "| Method B |")
    print("|---|---|---|---|---|---|")
    for p, exponent, (a, b, floor) in flanks:
        label = (f"z={p.teeth}, m={p.module:g}, {p.pressure_angle:g} deg"
                 + (" (default gear)" if p == GearParams() else ""))
        stack_mm = next((q for z, m, q in STACK_FLANK_MM if (z, m) == (p.teeth, p.module)),
                        None)
        spacing = "i^1.5 (the shipped spline's)" if exponent == 1.5 else "uniform in radius"
        print(f"| {label} | {f'{stack_mm:.1e}' if stack_mm else '--'} | {spacing} | {a:.3e} "
              f"| {floor:.3e} | {b:.3e} |")
    print()
    last_stack = KERNEL_ROWS[STACK_TROCHOID_ROWS[-1]].label
    print(f"#### Method B against the number of positions ({last_stack})")
    print()
    print("| Positions per root edge | Method B (mm) |")
    print("|---|---|")
    for n, value in steps:
        print(f"| {n + 1} | {value:.4e} |")
    print()
    print("#### Kernel tier on seven rows (mm unless stated)")
    print()
    print("| Row | Tip radius used | Join | Oracle, 41 positions | Oracle | Method B, same "
          "positions | Oracle vs B (units of the 3rd digit) | Method B, converged "
          "| Converged per module | 41-position reading / converged |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    disagreements = []
    for r in readings:
        units = third_digit_units(r.oracle, r.b_same)
        if units > 1:
            disagreements.append(r.row.label)
        print(f"| {r.row.label} | {r.rho_used:g} | {r.join} | {r.oracle_41:.4e} "
              f"| {r.oracle:.4e} | {r.b_same:.4e} | {units:.2f} | {r.b_converged:.4e} "
              f"| {r.b_converged / r.module:.4e} | {r.oracle_41 / r.b_converged:.2f} |")
    print()
    print(f"#### Tripwire: the tip radius read {TRIPWIRE_SHIFT_MM:g} mm above the one used")
    print()
    print("| Row | Reading (mm) | Reading per module | "
          + " | ".join(f"vs {bar:g} x module" for bar in LISTED_BARS) + " |")
    print("|---|---|---|" + "---|" * len(LISTED_BARS))
    for r in readings:
        if r.tripwire is None:
            continue
        cells = " | ".join(
            f"{r.tripwire / (bar * r.module):.2f}x, "
            f"{'over' if r.tripwire > bar * r.module else 'UNDER'}" for bar in LISTED_BARS)
        print(f"| {r.row.label} | {r.tripwire:.4e} | {r.tripwire / r.module:.4e} | {cells} |")
    print()
    for r in readings:
        if r.tripwire is not None:
            print(f"tripwire, {r.row.label}: {r.tripwire:.4e} mm, "
                  f"{r.tripwire / r.module:.4e} per module")
    print()
    if misses:
        print(f"Verdict: method B misses STACK's figure by more than one in the third "
              f"digit on {'; '.join(misses)}")
    if disagreements:
        print(f"Verdict: the kernel tier and method B disagree on {'; '.join(disagreements)}")
    if misses or disagreements:
        return 1
    print("Verdict: reconciled -- method B reproduces STACK's three trochoid figures to one "
          "in the third digit, and the oracle agrees with method B on all seven rows.")
    return 0


# --- the root arc's dead band (19-02) -------------------------------------------------

ARC_HALF_WIDTHS_MM = (0.0, 1e-12, 1e-10, 1e-9, 1e-8, 1e-7, 2e-7, 3e-7, 6e-7, 1e-6, 2e-6)
ARC_FIELDS: dict[str, object] = {**_M1, "teeth": 12, "pressure_angle": 20, "profile_shift": 0}
ARC_RHO_MM = 0.38
ARC_TARGET_HALF_WIDTH_MM = 1e-8
# GearParams refuses this gear above about 0.49 mm of backlash ("Teeth come to a point"), so
# the bisection runs over [0, 0.4] and not the plan's [0, 1]: rho_max spans 0.472 to 0.758
# mm there, which holds about 285 multiples of 0.001.
ARC_BACKLASH_CEILING = 0.4


@dataclass(frozen=True)
class ArcOutcome:
    half_width: float      # a, mm
    chord: float           # between root_r[-1] and the next tooth's root_l[0], mm
    outcome: str           # exception class and message, or what built
    builds: bool           # one valid solid with every face the shipped rule calls for


def arc_outcome(p: GearParams, curve: RootCurve, half_width: float,
                *, annulus: bool = True) -> ArcOutcome:
    """Build the shipped outline with the curve's first point moved along the root circle so
    the root arc between neighbours spans 2 x half_width, and say what it did. Under
    ROOT_ARC_MIN the neighbours share a vertex and no arc is made, so the faces expected are
    5 z + (arcs made) + 2, counted from the shipped rule (`model._trochoid_teeth`), not
    6 z + 2: a build counts only if it is one valid solid with exactly those faces.

    A moved first point is not a curve any cutter draws: the spline through it swings under
    the root circle (1.5e-3 mm on `ARC_FIELDS`), so the shipped annulus guard refuses every
    such outline before the kernel sees it. `annulus=False` lifts that one guard for this
    build, which leaves the question the table asks: what the kernel and ROOT_ARC_MIN do
    with a root arc of this width."""
    pr = profile(p)
    first = (curve.points[0][0], math.pi / p.teeth - half_width / pr.rf)
    variant = replace(curve, points=(first, *curve.points[1:]))
    teeth = outline_teeth(pr, variant)
    chord = (teeth[0][2][-1] - teeth[1][1][0]).Length
    arcs = sum(t.arc for t in model._trochoid_teeth(pr, variant))
    expected = 5 * p.teeth + arcs + 2
    try:
        with nullcontext() if annulus else patch.object(model, "_guard_annulus"):
            solid = extrude_outline(p, variant)
    except Exception as exc:  # OCCT raises assorted Standard_Failure subclasses
        return ArcOutcome(half_width, chord, f"{type(exc).__name__}: {exc}", False)
    faces, valid = len(solid.Faces()), solid.isValid()
    builds = valid and len(solid.Solids()) == 1 and faces == expected
    return ArcOutcome(half_width, chord,
                      f"builds, {faces} faces (expected {expected}: {arcs} of {p.teeth} "
                      f"root arcs made), {'valid' if valid else 'INVALID'}"
                      + ("" if builds else ", NOT the faces the shipped rule calls for"),
                      builds)


def tuned_backlash(fields: dict[str, object], rho_request: float) -> float:
    """The backlash at which the cutter's tip-land half-width `a` lands just above
    ARC_TARGET_HALF_WIDTH_MM, by 40 halvings over [0, ARC_BACKLASH_CEILING] (the
    `bench.trochoid.tuned_shift` precedent). rho_max rises with backlash and the used radius
    is rho_max floored to 3 dp, so a = (rho_max - used) (sec - tan) is a sawtooth that is
    tiny just above each multiple of 0.001: bisect rho_max to a point just above one."""
    def rho_max(backlash: float) -> float:
        return cutter(GearParams.model_validate({**fields, "backlash": backlash}),
                      rho_request).rho_max

    alpha = math.radians(float(str(fields["pressure_angle"])))
    delta = ARC_TARGET_HALF_WIDTH_MM / (1 / math.cos(alpha) - math.tan(alpha))
    target = math.floor(rho_max(ARC_BACKLASH_CEILING / 2) * 1000) / 1000 + delta
    lo, hi = 0.0, ARC_BACKLASH_CEILING
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        if rho_max(mid) < target:
            lo = mid
        else:
            hi = mid
    return hi


def dead_band(*, annulus: bool = True) -> tuple[GearParams, list[ArcOutcome]]:
    """The gear of ARC_FIELDS and what the shipped outline did at each ARC_HALF_WIDTHS_MM."""
    p = GearParams.model_validate(ARC_FIELDS)
    _, curve = trochoid_curve(p, ARC_RHO_MM)
    return p, [arc_outcome(p, curve, a, annulus=annulus) for a in ARC_HALF_WIDTHS_MM]


def run_arc() -> int:
    """The dead band of the root arc (19-RESEARCH F4) on the shipped outline: every width of
    ARC_HALF_WIDTHS_MM, and the tuned-backlash gear that reaches it from user input. 19-02
    measured the kernel failing at chords from 2e-9 to 2.0e-7 mm; `model.ROOT_ARC_MIN` is the
    rule that closes it, and this reads whether it does."""
    start, load_before = datetime.now(UTC), os.getloadavg()
    p, guarded = dead_band()
    _, lifted = dead_band(annulus=False)

    fields = {**ARC_FIELDS, "root_fillet": 3.0}
    backlash = tuned_backlash(fields, 3.0)
    tuned = GearParams.model_validate({**fields, "backlash": backlash})
    tuned_cut, tuned_curve = trochoid_curve(tuned, tuned.root_fillet)
    tuned_outcome = arc_outcome(tuned, tuned_curve, tuned_cut.a)
    try:
        trochoid_blank(tuned, tuned.root_fillet)
        shipped_blank = "builds"
    except Exception as exc:  # the blank as `_build` makes it, guards included
        shipped_blank = f"raises {type(exc).__name__}: {exc}"
    end, load_after = datetime.now(UTC), os.getloadavg()

    print("\n".join(_host_state(start, end, load_before, load_after)))
    print(f"Gear: {p.teeth} teeth, module {p.module:g}, {p.pressure_angle:g} degrees, shift "
          f"{p.profile_shift:g}, tip radius {ARC_RHO_MM:g} mm; the first point of the root "
          "curve moved along the root circle to half-angle pi / z - a / rf, so the root arc "
          "between neighbours spans about 2a. The outline is the shipped one "
          f"(`model._outline`, ROOT_ARC_MIN {model.ROOT_ARC_MIN:g} mm), read twice: with "
          "every guard on, and with the annulus guard lifted (a moved first point is not a "
          "curve any cutter draws, and its spline swings under the root circle). A build "
          "counts only if it is one valid solid with 5 z + (root arcs made) + 2 faces; "
          f"6 z + 2 = {6 * p.teeth + 2} when every arc is made.")
    print()
    print("#### Dead band")
    print()
    print("| a (mm) | chord, root_r[-1] to the next root_l[0] (mm) | all guards on "
          "| annulus guard lifted |")
    print("|---|---|---|---|")
    for g, o in zip(guarded, lifted, strict=True):
        print(f"| {o.half_width:g} | {o.chord:.3e} | {g.outcome} | {o.outcome} |")
    print()
    refused = [o for o in guarded if not o.builds]
    failing = [o for o in lifted if not o.builds]
    shared = [o for o in lifted if o.chord < model.ROOT_ARC_MIN]
    closed = not failing
    verdict = ("CLOSED: every row builds one valid solid" if closed else "OPEN: " + "; ".join(
        f"a = {o.half_width:g}: {o.outcome}" for o in failing))
    print(f"{len(guarded)} rows. All guards on: {len(guarded) - len(refused)} build, "
          f"{len(refused)} are refused before the kernel. Annulus guard lifted: "
          f"{len(shared)} rows are under ROOT_ARC_MIN (chord at most "
          f"{max((o.chord for o in shared), default=0.0):.3e} mm, the neighbours share a "
          f"vertex); the dead band is {verdict}.")
    print()
    print("#### Reachable from user input: the tuned-backlash gear")
    print()
    print(f"`GearParams` as above with root_fillet 3.0 (the cap applies) and backlash "
          f"bisected over [0, {ARC_BACKLASH_CEILING:g}] in 40 halvings: backlash "
          f"{backlash!r}, tip radius used "
          f"{tuned_cut.rho:g} mm of rho_max {tuned_cut.rho_max:.9f} mm, tip-land half-width "
          f"a = {tuned_cut.a:.3e} mm (target {ARC_TARGET_HALF_WIDTH_MM:g}), root-arc chord "
          f"{tuned_outcome.chord:.3e} mm: {tuned_outcome.outcome}. The shipped blank "
          f"{shipped_blank}.")
    return 0 if (closed and tuned_outcome.builds and shipped_blank == "builds"
                 and tuned_cut.a < 2 * ARC_TARGET_HALF_WIDTH_MM) else 1


# --- the whole product: spline error and the four guards (19-02, A7) -------------------

# The oracle's own resolution, per module: 18-04's twelve gate rows read 1.9e-16 to 2.6e-15
# (bench/RESULTS.md "Oracle bars (18-04)"), and its whole-product maximum was 1e-13 mm.
ORACLE_RESOLUTION_PER_MODULE = 1e-15
ANNULUS_POSITIONS = 80                 # 81 positions on each tooth-0 root edge
SPACING_CANDIDATES = (100.0, 1000.0, 10000.0)
AREA_CANDIDATES = (1e-2, 2e-2, 5e-2, 1e-1)
LIBM_FLOOR_RAD = 1e-12                 # 18-01's cross-platform libm floor (JUNCTION_BAR_RAD)
BUNCHING_RATIOS = (10.0, 1e2, 1e3, 1e4, 1e5, 1e6, 1e7)


def case_label(case: OracleCase) -> str:
    grid, fields, rho, _ = case
    return (f"grid {grid}: {fields['teeth']} teeth, m {fields['module']}, "
            f"{fields['pressure_angle']} deg, x {fields['profile_shift']}, "
            f"backlash {fields['backlash']}, tip radius asked {rho:g} mm")


@dataclass(frozen=True)
class ProductRow:
    gear: str
    module: float
    join: str
    spline_per_module: float   # method B, tooth-0 root splines, mm per mm of module
    spacing_ratio: float       # max / min chord of the 16 root points
    below_root: float          # min(R - rf) over the annulus positions, mm
    above_tip: float           # max(R - ra), mm
    area_rel: float            # |face area / shoelace area - 1|, both arcs taken as chords
    area_rel_arcs: float       # the same, the polygon through each arc's midpoint as well
    junction_gap: float        # |h_last - Profile.half_angle(R_last)|, rad
    arc_chord: float           # the root arc between neighbours, mm
    waist: float               # 2 R h at the narrowest point, mm
    error: str = ""            # the kernel exception, class and message; "" when none


def outline_polygon(pr: Profile, teeth: Sequence[Tooth], *,
                    arc_midpoints: bool) -> list[cq.Vector]:
    """The outline's own points in order: each tooth's root spline, flank, tip arc, mirror
    flank and root spline, then the root arc to the next tooth. The two arcs are taken as
    chords, or (`arc_midpoints`) through the midpoint the outline gives each three-point
    arc, which is what `model` can compute for free."""
    points: list[cq.Vector] = []
    for c, root_l, root_r, flank_l, flank_r in teeth:
        points += [*root_l, *flank_l[1:]]
        if arc_midpoints:
            points.append(model._polar(pr.ra, c))
        points += [*flank_r, *root_r[1:]]
        if arc_midpoints:
            points.append(model._polar(pr.rf, c + math.pi / pr.z))
    return points


def shoelace_area(points: Sequence[cq.Vector]) -> float:
    """Area of the closed polygon through `points`, mm^2."""
    return abs(0.5 * sum(a.x * b.y - b.x * a.y
                         for a, b in zip(points, [*points[1:], points[0]], strict=True)))


def _measure(case: OracleCase) -> ProductRow:
    _, fields, rho, _ = case
    p = GearParams.model_validate(fields)
    pr = profile(p)
    solid, cut, curve = trochoid_blank(p, rho)
    teeth = outline_teeth(pr, curve)
    edges = tooth0_root_edges(solid, p)
    radii = [math.hypot(v.x, v.y) for e in edges
             for v in (e.positionAt(i / ANNULUS_POSITIONS) for i in range(ANNULUS_POSITIONS + 1))]
    cartesian = [(r * math.cos(h), r * math.sin(h)) for r, h in curve.points]
    chords = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in pairwise(cartesian)]
    r_last, h_last = curve.points[-1]
    face_area = solid.Volume() / p.face_width
    return ProductRow(
        case_label(case), p.module, curve.join,
        spline_deviation(edges, dense_root(cut)) / p.module,
        max(chords) / min(chords),
        min(radii) - pr.rf, max(radii) - pr.ra,
        abs(face_area / shoelace_area(outline_polygon(pr, teeth, arc_midpoints=False)) - 1),
        abs(face_area / shoelace_area(outline_polygon(pr, teeth, arc_midpoints=True)) - 1),
        abs(h_last - pr.half_angle(r_last)),
        (teeth[0][2][-1] - teeth[1][1][0]).Length,
        2 * curve.waist[0] * curve.waist[1])


def product_row(case: OracleCase) -> ProductRow:
    """One trochoid case of the sweep product through the kernel and the four guards (a
    module-level function: spawn workers import it by name). A kernel exception is a row
    with its class and message, never a dropped case."""
    try:
        row = _measure(case)
    except Exception as exc:  # OCCT raises assorted Standard_Failure subclasses
        return ProductRow(case_label(case), 0.0, "", 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                          0.0, f"{type(exc).__name__}: {exc}")
    return row


@dataclass(frozen=True)
class BunchingRow:
    nominal: float        # largest / smallest step of the sampling parameter
    chord_ratio: float    # max / min chord of the 16 points as built
    deviation: float      # method B of the tooth-0 root splines, mm; nan when not built
    outcome: str
    builds: bool


def bunched_points(cut: Cutter, steps: int, ratio: float) -> tuple[tuple[float, float], ...]:
    """`steps` + 1 points of the cutter's own trochoid whose parameter steps grow
    geometrically, the largest `ratio` times the smallest, from the root circle to the
    junction."""
    junction = _junction(cut, TROCHOID_JOIN_EPS)
    if junction is None:
        raise ValueError("no junction for this cutter")
    q = ratio ** (1 / (steps - 1))
    weights = [q ** j for j in range(steps)]
    cumulative = [0.0]
    for w in weights:
        cumulative.append(cumulative[-1] + w / sum(weights))
    s_stop = math.tan(junction[0])
    betas = [math.atan(s_stop * u) for u in cumulative[:-1]] + [junction[0]]
    return tuple(_trochoid_point(cut, beta) for beta in betas)


def bunching_table() -> list[BunchingRow]:
    """The kernel and the spline error on one gear (ARC_FIELDS) as its 16 root points are
    resampled with a growing chord ratio, to put the spacing guard below a measured failure.
    The shipped outline's spacing guard is lifted for these builds (it would answer first at
    every ratio over its bar), so the rows read the kernel and the spline, not the guard."""
    p = GearParams.model_validate(ARC_FIELDS)
    cut, curve = trochoid_curve(p, ARC_RHO_MM)
    reference = dense_root(cut)
    rows = []
    for ratio in BUNCHING_RATIOS:
        points = bunched_points(cut, len(curve.points) - 1, ratio)
        cartesian = [(r * math.cos(h), r * math.sin(h)) for r, h in points]
        chords = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in pairwise(cartesian)]
        try:
            with patch.object(model, "ROOT_SPACING_RATIO_MAX", math.inf):
                solid = extrude_outline(p, replace(curve, points=points))
            faces, valid = len(solid.Faces()), solid.isValid()
            deviation = spline_deviation(tooth0_root_edges(solid, p), reference)
        except Exception as exc:  # OCCT raises assorted Standard_Failure subclasses
            rows.append(BunchingRow(ratio, max(chords) / min(chords), math.nan,
                                    f"{type(exc).__name__}: {exc}", False))
            continue
        builds = valid and faces == 6 * p.teeth + 2
        rows.append(BunchingRow(ratio, max(chords) / min(chords), deviation,
                                f"builds, {faces} faces, {'valid' if valid else 'INVALID'}",
                                builds))
    return rows


def smallest_power_of_ten(at_least: float, floor: float) -> float:
    """The smallest 10 ** e (integer e) that is at least `at_least` and at least `floor`."""
    exponent = math.floor(math.log10(floor))
    while 10.0 ** exponent < at_least or 10.0 ** exponent < floor:
        exponent += 1
    return 10.0 ** exponent


def smallest_listed(candidates: Sequence[float], at_least: float) -> float | None:
    return next((c for c in candidates if c >= at_least), None)


def _where(row: ProductRow) -> str:
    return row.gear


def run_product() -> int:
    """Every trochoid case of the Phase 18 sweep product (no stride, A7) through the
    kernel, the spline-error measure and the four structural guards; the bars proposed
    from the whole-product maxima. Everything is computed before anything is judged."""
    start, load_before = datetime.now(UTC), os.getloadavg()
    cases = [c for c in _oracle_cases() if c[3] == "trochoid"]
    total = sum(1 for _ in sweep_cases())
    workers = os.cpu_count() or 1
    t0 = time.perf_counter()
    with ProcessPoolExecutor(workers, mp_context=get_context("spawn")) as pool:
        rows = list(pool.map(product_row, cases, chunksize=8))
    wall = time.perf_counter() - t0
    bunching = bunching_table()
    end, load_after = datetime.now(UTC), os.getloadavg()

    good = [r for r in rows if not r.error]
    errors = [r for r in rows if r.error]
    print("\n".join(_host_state(start, end, load_before, load_after)))
    print(f"- Sweep cases: {total:,}; trochoid gears (what `bench.trochoid._oracle_cases()` "
          f"lists as `trochoid`): {len(cases):,}; built without a kernel exception: "
          f"{len(good):,}; kernel exceptions: {len(errors)}.")
    print(f"- {wall:.0f} s wall on {workers} spawn workers, one pass, no stride.")
    for r in errors[:10]:
        print(f"- EXCEPTION on {r.gear}: {r.error}")
    print()
    if not good:
        print("Verdict: FAIL, no gear built")
        return 1

    worst_spline = max(good, key=lambda r: r.spline_per_module)
    worst_spacing = max(good, key=lambda r: r.spacing_ratio)
    low_root = min(good, key=lambda r: r.below_root)
    high_tip = max(good, key=lambda r: r.above_tip)
    worst_area = max(good, key=lambda r: r.area_rel)
    worst_area_arcs = max(good, key=lambda r: r.area_rel_arcs)
    tangent = [r for r in good if r.join == "tangent"]
    crossing = [r for r in good if r.join == "crossing"]
    worst_tangent = max(tangent, key=lambda r: r.junction_gap) if tangent else None
    worst_crossing = max(crossing, key=lambda r: r.junction_gap) if crossing else None
    shortest = min(good, key=lambda r: r.arc_chord)
    thinnest = min(good, key=lambda r: r.waist / r.module)

    print("#### Maxima over the whole product")
    print()
    print("| Measure | Worst over the product | Gear |")
    print("|---|---|---|")
    print(f"| Spline error per module (method B, mm per mm of module) "
          f"| {worst_spline.spline_per_module:.4e} | {_where(worst_spline)} |")
    print(f"| Spacing ratio, max / min chord of the 16 root points "
          f"| {worst_spacing.spacing_ratio:.3f} (median "
          f"{median(r.spacing_ratio for r in good):.3f}) | {_where(worst_spacing)} |")
    print(f"| Annulus, min(R - rf) over {2 * (ANNULUS_POSITIONS + 1)} positions "
          f"| {low_root.below_root:+.3e} mm | {_where(low_root)} |")
    print(f"| Annulus, max(R - ra) | {high_tip.above_tip:+.3e} mm | {_where(high_tip)} |")
    print(f"| Closed-form area, |face area / shoelace area - 1|, arcs as chords "
          f"| {worst_area.area_rel:.4e} | {_where(worst_area)} |")
    print(f"| Closed-form area, the polygon through each arc's midpoint too "
          f"| {worst_area_arcs.area_rel_arcs:.4e} | {_where(worst_area_arcs)} |")
    for label, row in (("tangent", worst_tangent), ("crossing", worst_crossing)):
        if row is not None:
            print(f"| Junction gap, {label} joins ({sum(r.join == label for r in good):,} "
                  f"gears), rad | {row.junction_gap:.3e} | {_where(row)} |")
    print(f"| Smallest root-arc chord | {shortest.arc_chord:.4e} mm | {_where(shortest)} |")
    print(f"| Thinnest waist per module (2 R h) | {thinnest.waist / thinnest.module:.4e} mm "
          f"| {_where(thinnest)} |")
    print()
    print("#### Bunching: one gear resampled with a growing chord ratio "
          f"({ARC_FIELDS['teeth']} teeth, module {ARC_FIELDS['module']}, "
          f"{ARC_FIELDS['pressure_angle']} degrees, tip radius {ARC_RHO_MM:g} mm)")
    print()
    print("| Nominal ratio | Chord ratio as built | Spline error, method B (mm) | Kernel |")
    print("|---|---|---|---|")
    for b in bunching:
        print(f"| {b.nominal:g} | {b.chord_ratio:.4g} | {b.deviation:.4e} | {b.outcome} |")
    print()

    # --- the proposals, each from the maximum above with its headroom beside it ---------
    def verdict(headroom: float) -> str:
        return ("at or over 10x: the planner's call" if headroom >= 10
                else "UNDER 10x: joins the checkpoint")

    print("#### Proposals (each from the maximum above)")
    print()
    worst = worst_spline.spline_per_module
    try:
        bar = proposed_bar(worst)
    except ValueError as exc:
        print(f"kernel bar proposal: NONE ({exc}); goes to the human")
    else:
        print(f"kernel bar proposal: {bar:g} x module -- the worst spline error per module is "
              f"{worst:.4e} and the oracle's own resolution about "
              f"{ORACLE_RESOLUTION_PER_MODULE:g} per module; headroom {bar / worst:.1f}x over "
              f"the worst, {bar / ORACLE_RESOLUTION_PER_MODULE:.3g}x over the resolution "
              f"({verdict(bar / worst)})")
    failing = [b.chord_ratio for b in bunching if not b.builds]
    ceiling = min(failing) if failing else math.inf
    spacing = smallest_listed(SPACING_CANDIDATES, 10 * worst_spacing.spacing_ratio)
    if spacing is None or spacing >= ceiling:
        print(f"ROOT_SPACING_RATIO_MAX proposal: NONE below the first bunching failure "
              f"({ceiling:g}) at 10x the maximum {worst_spacing.spacing_ratio:.3f}; goes to "
              "the human")
    else:
        room = spacing / worst_spacing.spacing_ratio
        print(f"ROOT_SPACING_RATIO_MAX proposal: {spacing:g} -- the maximum spacing ratio is "
              f"{worst_spacing.spacing_ratio:.3f}, headroom {room:.1f}x ({verdict(room)}); "
              f"the first chord ratio the kernel failed at is {ceiling:g}, "
              f"{ceiling / spacing:.3g}x over the bar")
    excursion = max(0.0, -low_root.below_root, high_tip.above_tip)
    headroom = model.TOL / excursion if excursion > 0 else math.inf
    print(f"annulus proposal: [rf - TOL, ra + TOL] with TOL = {model.TOL:g} mm -- the worst "
          f"excursion outside [rf, ra] is {excursion:.3e} mm, headroom {headroom:.3g}x "
          f"({verdict(headroom)})")
    for label, measured in (("arcs as chords", worst_area.area_rel),
                            ("arc midpoints in the polygon", worst_area_arcs.area_rel_arcs)):
        area = smallest_listed(AREA_CANDIDATES, 10 * measured)
        if area is None:
            print(f"ROOT_AREA_REL_MAX proposal ({label}): NONE of {AREA_CANDIDATES} has 10x "
                  f"headroom over {measured:.4e}; the largest listed value, "
                  f"{AREA_CANDIDATES[-1]:g}, is {AREA_CANDIDATES[-1] / measured:.1f}x; goes "
                  "to the human")
        else:
            print(f"ROOT_AREA_REL_MAX proposal ({label}): {area:g} -- the maximum is "
                  f"{measured:.4e}, headroom {area / measured:.1f}x ({verdict(area / measured)})")
    gap = max((r.junction_gap for r in good), default=0.0)
    junction = smallest_power_of_ten(10 * gap, LIBM_FLOOR_RAD)
    print(f"ROOT_JUNCTION_BAR_RAD proposal: {junction:g} rad -- the larger join maximum is "
          f"{gap:.3e} rad (tangent {worst_tangent.junction_gap if worst_tangent else 0:.3e}, "
          f"crossing {worst_crossing.junction_gap if worst_crossing else 0:.3e}), the libm "
          f"floor {LIBM_FLOOR_RAD:g}; headroom {junction / gap if gap else math.inf:.3g}x "
          f"({verdict(junction / gap if gap else math.inf)})")
    side = "below" if shortest.arc_chord > model.ROOT_ARC_MIN else "ABOVE"
    print(f"ROOT_ARC_MIN check: the shipped {model.ROOT_ARC_MIN:g} mm against the smallest "
          f"real root-arc chord {shortest.arc_chord:.4e} mm: the constant is {side} it, "
          f"which is {shortest.arc_chord / model.ROOT_ARC_MIN:.3g}x the constant")
    return 1 if errors else 0


# --- D-07's waist walk (19-02) ---------------------------------------------------------

WALK_TEETH = (6, 7, 8)
WALK_SHIFTS = tuple(round(-0.6 + 0.01 * k, 2) for k in range(61))     # -0.60 .. 0.00
WALK_RHO_MM = (0.0, 0.38, 3.0)     # sharp, 0.38 m, and the field's maximum (capped)
WALK_PRESSURE_ANGLE = 14.5
# 0.10 is the default backlash; 0.0 is what 19-RESEARCH F8's scratch walk used (it reads the
# 4.98e-3 mm waist at 6 teeth, x -0.48, sharp cutter that only backlash 0 builds), and
# backlash thins the waist, so the walk takes both.
WALK_BACKLASH = (0.10, 0.0)


@dataclass(frozen=True)
class WalkRow:
    teeth: int
    shift: float
    rho: float               # asked, mm
    backlash: float
    mode: str                # what root_mode answered
    reason: str              # why it stayed radial, "" when trochoid
    rho_used: float
    join: str
    waist: float | None      # 2 R h, mm; None unless the curve exists
    kernel: str              # the kernel's refusal, "" when it built one valid solid
    oracle: float | None     # the oracle's worst reading of tooth 0, mm


def walk_row(case: tuple[int, float, float, float]) -> WalkRow:
    """One gear of D-07's walk (a module-level function: spawn workers import it by name):
    the predicate's answer, and for a trochoid gear the waist, the blank and the oracle."""
    teeth, shift, rho, backlash = case
    try:
        p = GearParams.model_validate({**_M1, "teeth": teeth,
                                       "pressure_angle": WALK_PRESSURE_ANGLE,
                                       "profile_shift": shift, "backlash": backlash})
    except ValidationError as exc:
        return WalkRow(teeth, shift, rho, backlash, "refused", str(exc.errors()[0]["msg"]),
                       0.0, "", None, "", None)
    rm = root_mode(p, profile(p), requested="trochoid", rho=rho)
    cut = rm.cutter
    if cut is None:
        raise ValueError("a requested root mode always carries its cutter")
    curve = trochoid_root(cut) if rm.mode == "trochoid" else None
    if curve is None:
        return WalkRow(teeth, shift, rho, backlash, rm.mode, str(rm.reason), cut.rho, "", None,
                       "", None)
    waist = 2 * curve.waist[0] * curve.waist[1]
    try:
        solid = _one_solid(extrude_outline(p, curve))
        reading = oracle_reading(solid, p, cut.rho, KERNEL_SAMPLES)
    except Exception as exc:  # OCCT raises assorted Standard_Failure subclasses
        return WalkRow(teeth, shift, rho, backlash, "trochoid", "", cut.rho, curve.join, waist,
                       f"{type(exc).__name__}: {exc}", None)
    return WalkRow(teeth, shift, rho, backlash, "trochoid", "", cut.rho, curve.join, waist, "",
                   reading)


@dataclass(frozen=True)
class ProductWaist:
    waist: float     # 2 R h, mm
    module: float
    join: str
    label: str


def product_waists() -> list[ProductWaist]:
    """The waist of every trochoid gear of the sweep product, from the curve alone: no
    kernel."""
    out = []
    for case in _oracle_cases():
        if case[3] != "trochoid":
            continue
        p = GearParams.model_validate(case[1])
        _, curve = trochoid_curve(p, case[2])
        out.append(ProductWaist(2 * curve.waist[0] * curve.waist[1], p.module, curve.join,
                                case_label(case)))
    return out


def _walk_label(r: WalkRow) -> str:
    return (f"{r.teeth} teeth, x {r.shift:g}, backlash {r.backlash:g}, tip radius asked "
            f"{r.rho:g} mm (used {r.rho_used:g})")


def run_waist(bar_per_module: float) -> int:
    """D-07's walk as written, the thinnest built waist, every kernel refusal and every
    oracle reading over the bar, and three floor candidates with the number of gears each
    would warn on in the walk and in the whole product."""
    start, load_before = datetime.now(UTC), os.getloadavg()
    cases = [(z, x, rho, bl) for z in WALK_TEETH for bl in WALK_BACKLASH
             for rho in WALK_RHO_MM for x in WALK_SHIFTS]
    workers = os.cpu_count() or 1
    t0 = time.perf_counter()
    with ProcessPoolExecutor(workers, mp_context=get_context("spawn")) as pool:
        rows = list(pool.map(walk_row, cases, chunksize=4))
    wall = time.perf_counter() - t0
    in_product = product_waists()
    end, load_after = datetime.now(UTC), os.getloadavg()

    built = [r for r in rows if r.mode == "trochoid" and not r.kernel]
    refused_by_kernel = [r for r in rows if r.mode == "trochoid" and r.kernel]
    print("\n".join(_host_state(start, end, load_before, load_after)))
    print(f"D-07's walk: teeth {WALK_TEETH}, module 1, {WALK_PRESSURE_ANGLE} degrees, "
          f"backlash {WALK_BACKLASH} mm, profile shift {WALK_SHIFTS[0]:g} to "
          f"{WALK_SHIFTS[-1]:g} in 0.01 steps, tip radius {WALK_RHO_MM} mm (3.0 is the "
          f"field's maximum, capped by the cutter). {len(rows)} gears in {wall:.0f} s on "
          f"{workers} spawn workers; oracle at {KERNEL_SAMPLES + 1} positions per root edge; "
          f"bar read as {bar_per_module:g} x module.")
    print()
    print("#### What `root_mode` answered")
    print()
    print("| Answer | Gears |")
    print("|---|---|")
    for label, count in sorted(Counter(
            f"{r.mode}" + (f" ({r.reason})" if r.reason else "") for r in rows).items()):
        print(f"| {label} | {count} |")
    print()
    print("#### The walk by series")
    print()
    print("| Teeth | Backlash | Tip radius asked (used) | Severed at x up to "
          "| First trochoid x | Thinnest built waist (mm) | at x | Worst oracle reading (mm) |")
    print("|---|---|---|---|---|---|---|---|")
    for z, bl, rho in itertools.product(WALK_TEETH, WALK_BACKLASH, WALK_RHO_MM):
        series = [r for r in rows if r.teeth == z and r.rho == rho and r.backlash == bl]
        severed = [r.shift for r in series if r.reason == "tooth severed"]
        trochoid = [r for r in series if r.mode == "trochoid"]
        ok = [r for r in trochoid if r.waist is not None and not r.kernel]
        used = sorted({r.rho_used for r in series})
        thin = min(ok, key=lambda r: r.waist or math.inf) if ok else None
        readings = [r.oracle for r in ok if r.oracle is not None]
        print(f"| {z} | {bl:g} | {rho:g} ({', '.join(f'{u:g}' for u in used)}) "
              f"| {max(severed) if severed else '--'} "
              f"| {min(r.shift for r in trochoid) if trochoid else '--'} "
              f"| {f'{thin.waist:.4e}' if thin and thin.waist is not None else '--'} "
              f"| {thin.shift if thin else '--'} "
              f"| {f'{max(readings):.3e}' if readings else '--'} |")
    print()
    if not built:
        print("Verdict: FAIL, no trochoid gear built in the walk")
        return 1

    ranked = sorted(built, key=lambda r: r.waist or math.inf)
    print("The thinnest built waist, then the next four:")
    print()
    for r in ranked[:5]:
        print(f"- {r.waist:.4e} mm: {_walk_label(r)}, {r.join} join")
    print()
    print(f"**Thinnest built waist: {ranked[0].waist:.4e} mm** ({_walk_label(ranked[0])}); "
          f"{len(built)} trochoid gears built of {len(rows)} walked.")
    print()
    if refused_by_kernel:
        print(f"Kernel refusals ({len(refused_by_kernel)}):")
        for r in refused_by_kernel:
            print(f"- {_walk_label(r)}, waist {r.waist:.4e} mm: {r.kernel}")
    else:
        print("Kernel refusals: none (every trochoid gear built one valid solid).")
    print()
    walk_readings = [(r.oracle, r) for r in built if r.oracle is not None]
    top_reading, top = max(walk_readings, key=lambda t: t[0])
    print(f"Worst oracle reading in the walk: {top_reading:.4e} mm ({_walk_label(top)}).")
    for bar in LISTED_BARS:
        print(f"- readings over {bar:g} x module (module 1): "
              f"{sum(v > bar for v, _ in walk_readings)} of {len(walk_readings)}")
    over = [(v, r) for v, r in walk_readings if v > bar_per_module]
    print(f"Oracle readings over the bar in use ({bar_per_module:g} mm): {len(over)}"
          + "".join(f"\n- {v:.4e} mm: {_walk_label(r)}" for v, r in over) + ".")
    print()

    failures = [r for r in built if r.oracle is not None and r.oracle > bar_per_module]
    failures += refused_by_kernel
    measured = 10 * max((r.waist or 0.0 for r in failures), default=0.0) or None
    candidates: list[tuple[str, float | None, bool]] = [
        ("measured: 10x the thickest waist where the kernel refused or the oracle left the "
         "bar", measured, True),
        ("spline scale: 10x the worst oracle reading in the walk", 10 * top_reading, True),
        ("printability: MIN_TIP_FDM, the tip warning's own number", MIN_TIP_FDM, False),
    ]
    print("#### Floor candidates")
    print()
    print("| Candidate | Floor | Walk gears warned (of "
          f"{len(built)} built) | Product gears warned (of {len(in_product):,}) |")
    print("|---|---|---|---|")
    by_module: list[str] = []
    totals = Counter(g.module for g in in_product)
    for name, floor, per_module in candidates:
        if floor is None:
            print(f"| {name} | none: no failure signature in the walk | -- | -- |")
            continue
        warned = [g for g in in_product
                  if g.waist < (floor * g.module if per_module else floor)]
        walk_hits = sum(1 for r in built if r.waist is not None and r.waist < floor)
        unit = "mm per mm of module" if per_module else "mm, absolute"
        print(f"| {name} | {floor:.4e} {unit} | {walk_hits} | {len(warned):,} |")
        hits = Counter(g.module for g in warned)
        tangent = Counter(g.module for g in warned if g.join == "tangent")
        by_module.append(f"- {name.split(':')[0]}: " + "; ".join(
            f"module {m:g}: {hits[m]:,} of {totals[m]:,} ({tangent[m]:,} on a tangent join)"
            for m in sorted(totals)))
    print()
    print("Product gears warned, by module:")
    print()
    print("\n".join(by_module))
    thinnest_product = min(in_product, key=lambda g: g.waist / g.module)
    print()
    print(f"Thinnest waist per module over the whole product: "
          f"{thinnest_product.waist / thinnest_product.module:.4e} mm "
          f"({thinnest_product.label}).")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m bench.trochoid_part",
                                     description=__doc__)
    sub = parser.add_subparsers(dest="scenario", required=True)
    sub.add_parser("chamfer", help="the tip chamfer's kernel limit across the junction")
    sub.add_parser("heaviest", help="the heaviest low-tooth rows against the build timeout")
    sub.add_parser("spline", help="reconcile the deviation methods; read the kernel tier")
    sub.add_parser("arc", help="the root arc's dead band and ROOT_ARC_MIN")
    sub.add_parser("product", help="the whole product's spline error and guard numbers")
    waist = sub.add_parser("waist", help="D-07's waist walk and the floor candidates")
    waist.add_argument("--bar-per-module", type=float, default=LISTED_BARS[1],
                       help="the kernel bar the walk judges the oracle by, mm per mm of "
                            "module (default 2e-3, 19-RESEARCH A2's proposal; pass the one "
                            "`product` proposes)")
    args = parser.parse_args(argv)
    if args.scenario == "waist":
        return run_waist(args.bar_per_module)
    scenarios: dict[str, Callable[[], int]] = {
        "chamfer": run_chamfer, "heaviest": run_heaviest, "spline": run_spline,
        "arc": run_arc, "product": run_product}
    return scenarios[args.scenario]()


if __name__ == "__main__":
    sys.exit(main())
