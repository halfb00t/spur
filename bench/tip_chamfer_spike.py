"""Measures the tooth-tip chamfer before the field exists (10-CONTEXT.md D-05).

Three parts: (1) the cost of the chamfer operator per (teeth, module, c); (2) the
kernel's own boundary against the analytic caps (D-04); (3) the flank rule over a
grid. It is not part of `make verify`: it takes about 8 minutes, and a timing
assertion on shared hardware would flap (build_time.py's stance).

Run it as `.venv/bin/python -m bench.tip_chamfer_spike` from the repo root. It
prints Markdown and exits 1 when the verdict fails.
"""

from __future__ import annotations

import itertools
import os
import platform
import subprocess
import sys
import time
from collections import Counter
from dataclasses import dataclass
from importlib import metadata

import cadquery as cq
from pydantic import ValidationError

from bench import machine_facts
from spur import int_env, model
from spur.calc import Profile, profile, root_fillet
from spur.params import GearParams

TOL = model.TOL


def spline_start(pr: Profile, fillet: float) -> float:
    """Radius where model._outline's involute spline begins.

    Mirrors model.py:123-125 exactly -- not imported, because the field this radius
    belongs to does not exist yet. 10-02 moves these three lines into spur.calc, after
    which this module imports that function instead of duplicating it.
    """
    r_line = max(pr.rb, pr.rf + 2.0 * fillet) if fillet > 0 else pr.rb
    r_line = min(r_line, pr.rf + 0.5 * (pr.ra - pr.rf))
    return max(r_line, pr.r_start)


def tip_arcs(solid: cq.Shape, ra: float, face_width: float) -> list[cq.Edge]:
    """The CIRCLE edges at radius ra whose two endpoints both sit on an end face (z=0
    or z=face_width) -- the selector 10-02 ships as model._tip_edges.

    A radius test alone would re-select the moved arcs after a chamfer (the tip land's
    new edges sit at z = c and z = face_width - c, still at radius ra - c, not ra) --
    testing both endpoints' z against the *original* face positions is what makes "at
    both end faces, on the unchamfered solid" true.
    """
    edges = []
    for e in solid.Edges():
        if e.geomType() != "CIRCLE" or abs(e.radius() - ra) >= TOL:
            continue
        a, b = e.startPoint(), e.endPoint()
        on_face = (any(abs(a.z - z) < TOL for z in (0.0, face_width))
                   and any(abs(b.z - z) < TOL for z in (0.0, face_width)))
        if on_face:
            edges.append(e)
    return edges


def chamfered(solid: cq.Solid, c: float,
             edges: list[cq.Edge]) -> tuple[cq.Solid | None, str]:
    """One valid chamfered solid, or None and the reason it is not: `solids=N` (not
    exactly one solid), `invalid`, or the exception class name.

    Catches Exception -- the same breadth as model._build_checked's catch-all, since
    OCCT raises assorted Standard_Failure subclasses this module has no name for.
    """
    try:
        result: cq.Shape = solid.chamfer(c, None, edges)
    except Exception as exc:  # mirrors _build_checked's catch-all
        return None, type(exc).__name__
    solids = result.Solids()
    if len(solids) != 1:
        return None, f"solids={len(solids)}"
    if not solids[0].isValid():
        return None, "invalid"
    return solids[0], ""


@dataclass(frozen=True)
class CostRow:
    label: str
    teeth: int
    arcs: int
    per_face: tuple[int, int]
    bare_s: float
    chamfer_s: float
    stl_s: float
    step_s: float
    d_faces: int
    d_cone: int
    d_edges: int
    d_volume: float
    bbox_moved: float
    why: str

    @property
    def request_s(self) -> float:
        """The cold request SPUR_BUILD_TIMEOUT wraps: one build, one chamfer, then the
        slower of the two exports -- Timing.worst_request's reasoning in
        bench/build_time.py, extended with the chamfer step this phase adds.
        """
        return self.bare_s + self.chamfer_s + max(self.stl_s, self.step_s)

    def ok(self) -> bool:
        return (not self.why
                and self.arcs == 2 * self.teeth
                and self.per_face == (self.teeth, self.teeth)
                and self.d_faces == self.d_cone == 2 * self.teeth
                and self.d_edges == 6 * self.teeth
                and self.d_volume < 0
                and self.bbox_moved < TOL)

    def line(self) -> str:
        return (f"| {self.label} | {self.arcs} | {self.per_face[0]}/{self.per_face[1]} "
                f"| {self.bare_s:.2f} | {self.chamfer_s:.2f} | {self.stl_s:.2f} | "
                f"{self.step_s:.2f} | {self.request_s:.2f} | {self.d_faces} | "
                f"{self.d_cone} | {self.d_edges} | {self.d_volume:.2f} | "
                f"{self.bbox_moved:.2e} | {self.why or 'ok'} |")


def cost_row(kw: dict[str, object], c: float) -> CostRow:
    """Build, chamfer, and export one (parameter set, c) row.

    A failed chamfer returns a row with its `why` and zero deltas -- the row is still
    recorded, never dropped (must_haves prohibition: no re-picking to green).
    """
    label = " ".join(f"{k}={v}" for k, v in kw.items()) + f" c={c:g}"
    p = GearParams.model_validate(kw)
    pr = profile(p)

    t0 = time.perf_counter()
    bare = model._build_checked(p)
    bare_s = time.perf_counter() - t0

    arcs = tip_arcs(bare, pr.ra, p.face_width)
    per_face = (
        sum(1 for e in arcs if abs(e.startPoint().z) < TOL),
        sum(1 for e in arcs if abs(e.startPoint().z - p.face_width) < TOL),
    )

    t0 = time.perf_counter()
    solid, why = chamfered(bare, c, arcs)
    chamfer_s = time.perf_counter() - t0
    if solid is None:
        return CostRow(label, p.teeth, len(arcs), per_face, bare_s, chamfer_s,
                        0.0, 0.0, 0, 0, 0, 0.0, 0.0, why)

    faces_before, faces_after = bare.Faces(), solid.Faces()
    d_faces = len(faces_after) - len(faces_before)
    d_cone = (Counter(f.geomType() for f in faces_after)["CONE"]
             - Counter(f.geomType() for f in faces_before)["CONE"])
    d_edges = len(solid.Edges()) - len(bare.Edges())
    d_volume = solid.Volume() - bare.Volume()

    bb_before, bb_after = bare.BoundingBox(), solid.BoundingBox()
    bbox_moved = max(
        abs(bb_after.xmin - bb_before.xmin), abs(bb_after.xmax - bb_before.xmax),
        abs(bb_after.ymin - bb_before.ymin), abs(bb_after.ymax - bb_before.ymax),
        abs(bb_after.zmin - bb_before.zmin), abs(bb_after.zmax - bb_before.zmax),
    )

    t0 = time.perf_counter()
    model._write_export(solid, p, "stl", "fine")
    stl_s = time.perf_counter() - t0
    t0 = time.perf_counter()
    model._write_export(solid, p, "step", "fine")
    step_s = time.perf_counter() - t0

    return CostRow(label, p.teeth, len(arcs), per_face, bare_s, chamfer_s, stl_s, step_s,
                   d_faces, d_cone, d_edges, d_volume, bbox_moved, "")


# 19/40/200 teeth at the default module (c at 0.4 and the analytic cap 1.75), the same
# three at module 10 (c at 0.4 and the analytic cap 3.375), and 19/40/200 teeth at
# module 0.2 -- the finest tips, the cap biting hardest (c at 0.05 and the analytic cap
# 0.2). Module-0.2 needs backlash 0 (19/40 teeth: check() also refuses the default bore
# there) or 0.07 (200 teeth: the finest tip check() allows) -- the default backlash
# 0.1 mm makes every module-0.2 gear a 422 ("Teeth come to a point"), see A1.
COST_SETS: list[tuple[dict[str, object], tuple[float, float]]] = [
    ({"teeth": 19}, (0.4, 1.75)),
    ({"teeth": 40}, (0.4, 1.75)),
    ({"teeth": 200}, (0.4, 1.75)),
    ({"teeth": 19, "module": 10}, (0.4, 3.375)),
    ({"teeth": 40, "module": 10}, (0.4, 3.375)),
    ({"teeth": 200, "module": 10}, (0.4, 3.375)),
    ({"teeth": 19, "module": 0.2, "backlash": 0, "bore_d": 0}, (0.05, 0.2)),
    ({"teeth": 40, "module": 0.2, "backlash": 0, "bore_d": 0}, (0.05, 0.2)),
    ({"teeth": 200, "module": 0.2, "backlash": 0.07}, (0.05, 0.2)),
]


def boundary(kw: dict[str, object]) -> tuple[float, float, float, str]:
    """(last_ok, first_fail, pred, why): 20-step bisection (09-03's count) between 0
    and hi = min(3.0, 0.45 x face_width) -- hi deliberately sits past D-01/D-02's
    analytic caps on purpose, to find the kernel's own limit, not stop at theirs.

    pred = ra - spline_start(pr, root_fillet(p)): the radius where the outline's
    involute spline begins, subtracted from the tip radius -- the planning-time
    hypothesis this bisection tests (10-01's <interfaces> block).
    """
    p = GearParams.model_validate(kw)
    pr = profile(p)
    pred = pr.ra - spline_start(pr, root_fillet(p))
    hi = min(3.0, 0.45 * p.face_width)

    bare = model._build_checked(p)
    arcs = tip_arcs(bare, pr.ra, p.face_width)

    solid, why = chamfered(bare, hi, arcs)
    if solid is not None:
        return hi, float("inf"), pred, "builds at the top"

    lo, first_fail, last_why = 0.0, hi, why
    for _ in range(20):
        mid = 0.5 * (lo + first_fail)
        s, w = chamfered(bare, mid, arcs)
        if s is not None:
            lo = mid
        else:
            first_fail, last_why = mid, w
    return lo, first_fail, pred, last_why


# Six sets differing in teeth, pressure angle, backlash, profile shift and root fillet
# -- if pred (ra - spline_start) is teeth-independent the way ROOT_CONTACT is, these
# should bisect to the same gap regardless of teeth; if it moves with tooth count the
# way the hex corner does (L27), the 19- and 40-tooth rows will disagree.
BOUNDARY_SETS: list[dict[str, object]] = [
    {"profile_shift": 1.0, "pressure_angle": 14.5},
    {"profile_shift": 1.0, "pressure_angle": 14.5, "teeth": 40},
    {"profile_shift": 0.8, "pressure_angle": 20},
    {"profile_shift": 1.0, "pressure_angle": 14.5, "root_fillet": 1.0},
    {"root_fillet": 1.0},
    {"profile_shift": 1.0, "pressure_angle": 14.5, "module": 1, "bore_d": 5,
     "bore_flat": 0},
]


def edge_of_200(kw: dict[str, object]) -> tuple[str, str]:
    """Two direct chamfer calls (no bisection -- each takes about 13 s), bracketing
    pred on the 200-tooth boundary set: one 0.001 mm inside it, one 0.05 mm past it.
    Returns ("builds", why) for each call -- "builds" when it built a valid solid.
    """
    p = GearParams.model_validate(kw)
    pr = profile(p)
    pred = pr.ra - spline_start(pr, root_fillet(p))
    bare = model._build_checked(p)
    arcs = tip_arcs(bare, pr.ra, p.face_width)
    _, why_in = chamfered(bare, pred - 0.001, arcs)
    _, why_out = chamfered(bare, pred + 0.05, arcs)
    return why_in or "builds", why_out or "builds"


# 19 teeth, no bore, no recess: the flank rule (pred vs the analytic caps) tested clean
# of any other feature. 7 x 4 x 3 x 3 x 2 = 405 sets.
GRID = list(itertools.product(
    (0.2, 0.5, 1, 1.25, 1.75, 2.5, 4),  # module
    (0.25, 0.5, 0.75, 1.0),             # profile_shift
    (14.5, 20, 25),                     # pressure_angle
    (0.5, 1.0, 3.0),                    # root_fillet
    (0, 0.1),                           # backlash
))


def grid_check() -> tuple[int, int, list[str], int]:
    """(sets validated, sets where pred < the analytic cap, labels that failed at pred
    or 0.05 mm inside it, count that also built at the analytic cap).

    A set that fails GearParams validation (check()'s own refusals) is skipped, not
    counted as validated or failed -- it never became a gear to chamfer.
    """
    validated = 0
    conservative = 0
    failed: list[str] = []
    also_at_cap = 0
    for module, shift, alpha, fillet, backlash in GRID:
        kw: dict[str, object] = {
            "teeth": 19, "module": module, "profile_shift": shift,
            "pressure_angle": alpha, "root_fillet": fillet, "backlash": backlash,
            "bore_d": 0, "recess_sides": "none",
        }
        try:
            p = GearParams.model_validate(kw)
        except ValidationError:
            continue
        validated += 1
        pr = profile(p)
        pred = pr.ra - spline_start(pr, root_fillet(p))
        cap = min(0.45 * p.face_width, pr.ra - pr.r, 3.0)
        if pred >= cap:
            continue
        conservative += 1
        label = " ".join(f"{k}={v}" for k, v in kw.items())
        bare = model._build_checked(p)
        arcs = tip_arcs(bare, pr.ra, p.face_width)
        probe = pred / 2 if pred <= 0.06 else pred - 0.05
        at_pred, _ = chamfered(bare, pred, arcs)
        inside_pred, _ = chamfered(bare, probe, arcs)
        if at_pred is None or inside_pred is None:
            failed.append(label)
        at_cap, _ = chamfered(bare, cap, arcs)
        if at_cap is not None:
            also_at_cap += 1
    return validated, conservative, failed, also_at_cap


def main() -> int:
    timeout = int_env("SPUR_BUILD_TIMEOUT", 30)
    versions = ", ".join(f"{dist} {metadata.version(dist)}"
                         for dist in ("cadquery", "cadquery-ocp"))
    head = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    load1, load5, load15 = os.getloadavg()

    print("### Host state")
    print(f"- Machine: {machine_facts()}")
    print(f"- Python: {platform.python_version()}")
    print(f"- Kernel: {versions}")
    print(f"- HEAD: `{head}`")
    print(f"- Load averages at start: {load1:.2f}, {load5:.2f}, {load15:.2f}")
    print(f"- SPUR_BUILD_TIMEOUT: {timeout} s")
    print()

    # Time and print everything before deciding (bench/latency.py's rule): every row,
    # boundary set, the 200-tooth pair and the grid are computed here, before the
    # verdict below reads any of them.
    rows = [cost_row(kw, c) for kw, cs in COST_SETS for c in cs]
    boundaries = [(kw, boundary(kw)) for kw in BOUNDARY_SETS]
    edge = edge_of_200({"teeth": 200, "profile_shift": 1.0, "pressure_angle": 14.5})
    grid = grid_check()

    print("### Cost")
    print("| Set | Arcs | Per face | Bare (s) | Chamfer (s) | STL (s) | STEP (s) | "
         "Request (s) | dFaces | dCone | dEdges | dVolume | BBox moved | Why |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        print(r.line())
    print()

    print("### Kernel boundary")
    print("| Set | pred | last_ok | first_fail | last_ok - pred | Why |")
    print("|---|---|---|---|---|---|")
    for kw, (last_ok, first_fail, pred, why) in boundaries:
        label = " ".join(f"{k}={v}" for k, v in kw.items())
        ff = "inf" if first_fail == float("inf") else f"{first_fail:.7f}"
        print(f"| {label} | {pred:.7f} | {last_ok:.7f} | {ff} | "
             f"{last_ok - pred:.2e} | {why} |")
    print()
    print("200-tooth pair (`teeth=200 profile_shift=1.0 pressure_angle=14.5`): "
         f"pred - 0.001 -> {edge[0]}, pred + 0.05 -> {edge[1]}")
    print()

    validated, conservative, failed, also_at_cap = grid
    print("### Flank rule over the grid")
    print(f"{validated} sets validated, {conservative} conservative (pred < the "
         f"analytic cap), {len(failed)} failed, {also_at_cap} also built at the "
         "analytic cap.")
    print()

    reasons: list[str] = []
    if not all(r.ok() for r in rows):
        reasons.append("a cost row is not ok()")
    two_hundred = [r for r in rows if r.teeth == 200]
    if not all(r.request_s <= timeout for r in two_hundred):
        reasons.append("a 200-tooth row exceeds SPUR_BUILD_TIMEOUT")
    if not all(last_ok >= pred - 1e-5 for _, (last_ok, _, pred, _) in boundaries):
        reasons.append("a boundary set's last_ok fell short of pred")
    if not (edge[0] == "builds" and edge[1] != "builds"):
        reasons.append("the 200-tooth pair did not build inside and fail past")
    if failed:
        reasons.append("the grid flank rule failed on a configuration")

    print("### Verdict")
    if not reasons:
        heaviest = max(two_hundred, key=lambda r: r.request_s) if two_hundred else None
        heaviest_txt = (f"{heaviest.label} -- {heaviest.request_s:.2f} s of {timeout} s"
                        if heaviest is not None else "no 200-tooth row")
        print(f"**Verdict:** held -- {len(rows)} cost rows ok, {len(boundaries)} "
             f"boundary sets held, grid {conservative}/{validated} conservative with "
             f"0 failures, heaviest 200-tooth request {heaviest_txt}.")
        return 0
    print(f"**Verdict:** FAILED -- {'; '.join(reasons)}.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
