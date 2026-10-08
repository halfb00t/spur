"""Measures the hob's trochoid root where the unit tests cannot afford to (Phase 18).

Scenarios, one subcommand each:

- `epsilon` (18-03): how close to the z_min double root the junction bracket survives, so
  `calc.TROCHOID_JOIN_EPS` is a measurement made in this repo and not a number carried
  over from a prototype (D-09).
- `sweep` (18-03): the generator over every gear the project allows, STACK's product with
  the field's real limits plus the box corners, each case checked against closed forms
  typed in this module (D-12); `--list` writes every refusal, `--stride K` runs the
  sample the commit-time gate test runs (D-13).
- `oracle` (18-04): the swept-cutter oracle over every trochoid curve of the sweep
  product, and over the one flank of every severed tooth, which must read a gouge (D-13:
  the full grid only here); `--serial-slice N` judges the first N in-process.
- `step` (18-05): the root-shape step between the hob's trochoid and the shipped analytic
  root (fillet arc plus lead-in line) at the undercut threshold and at the `rb = rf`
  crossover, judged against the comparison line `premise_holds` carries (D-05).

It is not part of `make verify`: the scans take seconds to minutes and their timings
depend on the host, and a timing assertion on shared hardware would flap
(`bench/build_time.py`'s stance). Run it as `.venv/bin/python -m bench.trochoid <scenario>`
from the repo root. It prints Markdown and exits 1 when the verdict fails.

This module never imports `cadquery` (18-05's `step` imports `spur.model` inside its own
function), so a test can import the grid without loading the kernel.
"""

from __future__ import annotations

import argparse
import csv
import itertools
import math
import multiprocessing
import os
import platform
import random
import statistics
import sys
import time
from collections import Counter
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from datetime import UTC, datetime
from importlib import metadata
from itertools import pairwise
from pathlib import Path

from pydantic import ValidationError

from bench import machine_facts
from spur.calc import (
    ROOT_CURVE_POINTS,
    TROCHOID_JOIN_EPS,
    Cutter,
    RootCurve,
    _junction,
    _trochoid_point,
    _waist,
    cutter,
    profile,
    root_fillet,
    root_mode,
    spline_start,
    trochoid_root,
)
from spur.params import GearParams

# --- the join epsilon (D-09) ---------------------------------------------------------

EPSILON_DRAWS = 400
EPSILON_SEED = 18
# xi = -t * rb for t from 1e-2 down to 1e-12 at 4 steps per decade (41 values): the scan
# resolution 18-RESEARCH F6 used, so the two measurements are comparable.
EPSILON_STEPS = [10 ** (-2 - k / 4) for k in range(41)]
# The constant above which the scan fails the task: a bracket lost at |xi| above 1e-4*rb
# is more than an order above STACK's loss point (6.2e-6*rb) and puts the flank-join error
# above 5e-7*rb, which is a solver problem and not a constant to write.
EPSILON_CEILING = 1e-3
STACK_FOUND_MM = 2.9e-3  # STACK: bracket found at xi = -2.9e-3 mm (10 teeth, 20 deg)
STACK_LOST_MM = 2.9e-5   # and lost at xi = -2.9e-5 mm


def tuned_shift(base: GearParams, rho: float, xi_target: float) -> float:
    """The profile shift at which the cutter's `xi` reads `xi_target` mm.

    xi is linear in the shift, xi(x) = xi(x0) + (x - x0) * m / sin(alpha), and rb does
    not depend on it, so a gear is put on its own z_min double root from one cutter
    (the interface the plan names). The value can leave the field's range; the caller
    decides what that means.
    """
    c = cutter(base, rho)
    return base.profile_shift + (xi_target - c.xi) * math.sin(c.pr.alpha) / base.module


def _gear(**fields: object) -> GearParams:
    """A gear with the bore and recesses off: the default 9 mm bore refuses small ones."""
    return GearParams.model_validate(
        {"bore_d": 0, "bore_flat": 0, "bore_chamfer": 0, "recess_sides": "none", **fields})


def _largest_loss(fields: dict[str, object], rho: float) -> float | None:
    """The largest t (xi = -t*rb) at which `_junction(c, 0.0)` loses the bracket for this
    gear, 0.0 when it never does, None when the draw is unusable (no tip land, or its
    own z_min double root is outside the field's profile-shift range)."""
    try:
        base = _gear(**fields, profile_shift=0.0)
    except ValidationError:
        return None
    c0 = cutter(base, rho)
    if c0.a0 < 0:
        return None
    rb = c0.pr.rb
    lost = 0.0
    for t in EPSILON_STEPS:
        x = tuned_shift(base, rho, -t * rb)
        if not -0.6 <= x <= 1.0:
            return None
        try:
            c = cutter(_gear(**fields, profile_shift=x), rho)
        except ValidationError:
            return None
        if c.xi >= 0:  # float rounding of x put the gear on the tangent side
            continue
        if _junction(c, 0.0) is None:
            lost = max(lost, t)
    return lost


def epsilon_scan() -> tuple[int, int, list[float]]:
    """(draws used, attempts skipped, the largest lost t of each usable draw that lost
    one). 400 usable seeded random allowed gears, drawn until that many are usable."""
    rng = random.Random(EPSILON_SEED)
    used = skipped = 0
    losses: list[float] = []
    while used < EPSILON_DRAWS and used + skipped < 20 * EPSILON_DRAWS:
        module = rng.choice([0.2, 0.5, 1.0, 1.75, 4.0, 10.0])
        fields: dict[str, object] = {
            "teeth": rng.randint(6, 40), "module": module,
            "pressure_angle": 14.5 + 0.5 * rng.randint(0, 31),
            "backlash": rng.choice([0.0, 0.1, 0.25, 0.5]), "root_fillet": 0.0}
        rho = rng.uniform(0.0, 0.5) * module
        loss = _largest_loss(fields, rho)
        if loss is None:
            skipped += 1
            continue
        used += 1
        if loss > 0:
            losses.append(loss)
    return used, skipped, losses


def recommended_epsilon(largest_loss: float) -> float:
    """The smallest power of ten at least 10x the largest loss (the 10x rule applied to
    the constant itself)."""
    return 10.0 ** math.ceil(round(math.log10(10 * largest_loss), 9))


def _load() -> str:
    return ", ".join(f"{v:.2f}" for v in os.getloadavg())


def _stack_points() -> list[tuple[str, float, bool]]:
    """STACK's two points re-created on the 10-tooth, 20 degree, module 1, backlash 0,
    tip radius 0.38 mm gear: (label, xi mm, whether `_junction(c, 0.0)` finds a bracket)."""
    base = _gear(teeth=10, module=1.0, pressure_angle=20, profile_shift=0.0, backlash=0.0,
                 root_fillet=0.0)
    rows = []
    for label, mm in (("found", STACK_FOUND_MM), ("lost", STACK_LOST_MM)):
        c = cutter(_gear(teeth=10, module=1.0, pressure_angle=20, backlash=0.0,
                         root_fillet=0.0, profile_shift=tuned_shift(base, 0.38, -mm)), 0.38)
        rows.append((label, -c.xi, _junction(c, 0.0) is not None))
    return rows


def run_epsilon() -> int:
    started = datetime.now(UTC)
    load_before = _load()
    used, skipped, losses = epsilon_scan()
    load_after = _load()
    print("## Join epsilon scan (`bench.trochoid epsilon`)\n")
    print("#### Host state\n")
    print(f"- Machine: {machine_facts()}")
    print(f"- Python {platform.python_version()}")
    print(f"- Read {started:%Y-%m-%dT%H:%M:%SZ}; 1-minute load {load_before} before, "
          f"{load_after} after\n")
    print(f"Draws: {EPSILON_DRAWS} usable of seed {EPSILON_SEED} (teeth 6-40, module "
          "0.2/0.5/1/1.75/4/10, pressure angle 14.5-30 on the 0.5 degree grid, backlash "
          "0/0.1/0.25/0.5, tip radius a uniform 0-0.5 of the module); the profile shift is "
          f"tuned so xi = -t*rb for t from 1e-2 to 1e-12, {len(EPSILON_STEPS)} values.\n")
    print(f"- Draws used: {used}; attempts skipped (no tip land, or the z_min double root "
          f"outside the shift range -0.6..1.0, or the gear invalid): {skipped}")
    print(f"- Draws that lost the bracket at some t: {len(losses)}; never lost: "
          f"{used - len(losses)}")
    for label, mm, found in _stack_points():
        print(f"- STACK's point ({label}): xi = {-mm:.3e} mm, bracket "
              f"{'found' if found else 'LOST'} with the epsilon at 0")
    stack_fields: dict[str, object] = {"teeth": 10, "module": 1.0, "pressure_angle": 20.0,
                                       "backlash": 0.0, "root_fillet": 0.0}
    own = _largest_loss(stack_fields, 0.38)
    if own is not None:
        rb = profile(_gear(**stack_fields)).rb
        print(f"- That gear's own largest lost t in this scan: {own:.3e} "
              f"(xi = {-own * rb:.3e} mm at rb {rb:.4f} mm)")
    if used == 0 or not losses:
        print("\nverdict: FAIL, no usable draw or no loss to measure the edge from")
        return 1
    largest, median = max(losses), statistics.median(losses)
    print(f"- Largest loss: t = {largest:.3e}; median of the losses: {median:.3e}\n")
    print("| decade of the largest lost t | draws |")
    print("|---|---|")
    decades = Counter(math.floor(round(math.log10(loss), 9)) for loss in losses)
    for decade in sorted(decades, reverse=True):
        print(f"| 1e{decade} to 1e{decade + 1} | {decades[decade]} |")
    eps = recommended_epsilon(largest)
    print(f"\nrecommended TROCHOID_JOIN_EPS = {eps:g} (10x rule: the smallest power of ten at "
          f"least {10 * largest:.3e})")
    print(f"flank-join error bound (eps*rb)^2/(2*rb) = {eps ** 2 / 2:.3e} * rb")
    if eps > EPSILON_CEILING:
        print(f"\nverdict: FAIL, recommended {eps:g} is above {EPSILON_CEILING:g}: the bracket "
              "is lost far from the double root, a solver problem and not a constant")
        return 1
    print("\nverdict: ok")
    return 0


# --- the generator sweep over the allowed box (D-12) ----------------------------------
# Written out as literals, never computed from calc: a grid derived from the code under
# test would move with it. 18-RESEARCH F5: STACK's "7,296" is the 7,980-case product
# minus the 684 rows with w_c >= 0, counts 912 rows with a < 0 as solved and includes
# x = -1, which GearParams rejects; so grid A is the whole 7,980 product with the field's
# limit -0.6 in place of -1, and the x = 1 rows with rho >= d are kept.

CAP_REQUEST_MM = 3.0  # the root_fillet field's maximum: every cutter trims it to its own cap

# STACK's product, module 1. The tip radius is a multiple of the module.
GRID_A: dict[str, tuple[float, ...]] = {
    "module": (1.0,),
    "teeth": (*range(6, 41), 60, 100, 200),
    "pressure_angle": (14.5, 20.0, 25.0),
    "profile_shift": (-0.6, -0.5, -0.2, 0.0, 0.2, 0.5, 1.0),
    "backlash": (0.0, 0.10),
    "rho_times_module": (0.0, 0.1, 0.25, 0.38, 0.5),
}
# The box corners: both module limits and the middle, the tooth counts around every
# edge (undercut onset, rb = rf at 41-42 teeth at module 1, the 116/117 box limit), the
# pressure angles one field step either side of the tip-land limit, backlash up to the
# field's maximum. The tip radius is 0, 0.25 m, 0.5 m and 0.5 mm (each case's own
# root_fillet default).
GRID_B: dict[str, tuple[float, ...]] = {
    "module": (0.2, 1.75, 10.0),
    "teeth": (6, 7, 8, 9, 10, 12, 14, 17, 18, 20, 25, 30, 40, 60, 100, 116, 117, 200),
    "pressure_angle": (14.5, 20.0, 25.0, 30.0, 32.0, 32.5, 33.0, 33.5, 35.0),
    "profile_shift": (-0.6, 0.0, 1.0),
    "backlash": (0.0, 0.10, 1.0),
}
GRID_B_RHO_TIMES_MODULE = (0.0, 0.25, 0.5)
GRID_B_RHO_MM = 0.5

# The generator's own consistency bar: the junction radius relative and the last
# half-angle in rad, both against closed forms typed in this module. 18-01 measured the
# same agreement at 4.2e-17 rad and 1.8e-15 mm (1 ulp at R 15 mm) on four rows; 1e-12 is
# the cross-platform libm floor those bars sit on. If any case of the product exceeds it
# the worst measured gap is recorded in bench/RESULTS.md and the bar is re-derived from it
# with 10x headroom -- never widened silently (18-03 plan, SWEEP_BAR).
SWEEP_BAR = 1e-12

_FIXED: dict[str, object] = {"bore_d": 0, "bore_flat": 0, "bore_chamfer": 0,
                             "recess_sides": "none"}


def _gears(grid: dict[str, tuple[float, ...]]) -> Iterator[dict[str, object]]:
    axes = ("module", "teeth", "pressure_angle", "profile_shift", "backlash")
    for module, teeth, angle, shift, backlash in itertools.product(*(grid[a] for a in axes)):
        yield {**_FIXED, "teeth": int(teeth), "module": module, "pressure_angle": angle,
               "profile_shift": shift, "backlash": backlash}


def sweep_cases() -> Iterator[tuple[str, dict[str, object], float]]:
    """Every (grid, GearParams fields, tip radius requested in mm) of the whole product,
    in a fixed order: gear by gear, each with its tip radii, the cap request last."""
    for kwargs in _gears(GRID_A):
        module = float(str(kwargs["module"]))
        for times in GRID_A["rho_times_module"]:
            yield "A", kwargs, times * module
        yield "A", kwargs, CAP_REQUEST_MM
    for kwargs in _gears(GRID_B):
        module = float(str(kwargs["module"]))
        for times in GRID_B_RHO_TIMES_MODULE:
            yield "B", kwargs, times * module
        yield "B", kwargs, GRID_B_RHO_MM
        yield "B", kwargs, CAP_REQUEST_MM


@dataclass(frozen=True)
class Rack:
    """The closed forms a curve is checked against, typed here from the textbook rack
    (dedendum 1.25 m, flank angle alpha, cutter tooth width pi*m minus the tooth
    thickness on the pitch circle), sharing no expression with `calc`."""
    z: int
    m: float
    alpha: float
    rb: float
    rf: float
    ra: float
    psi_p: float    # half tooth-thickness angle on the pitch circle
    a0: float       # sharp-corner tip-land half-width, mm
    rho: float      # tip radius used: the request, or the cap floored to 3 dp
    xi: float       # roll of the flank foot, mm; the gear is undercut where negative


def rack(p: GearParams, rho_requested: float) -> Rack:
    z, m, x, bl = p.teeth, p.module, p.profile_shift, p.backlash
    alpha = math.radians(p.pressure_angle)
    r = m * z / 2
    s = m * (math.pi / 2 + 2 * x * math.tan(alpha)) - bl
    d = m * (1.25 - x)
    a0 = (math.pi * m - s) / 2 - d * math.tan(alpha)
    cap = a0 / (1 / math.cos(alpha) - math.tan(alpha))
    rho = rho_requested if rho_requested <= cap else max(0.0, math.floor(cap * 1000) / 1000)
    xi = r * math.sin(alpha) - (d - rho * (1 - math.sin(alpha))) / math.sin(alpha)
    return Rack(z=z, m=m, alpha=alpha, rb=r * math.cos(alpha), rf=r - d,
                ra=r + m * (1 + x), psi_p=s / (2 * r), a0=a0, rho=rho, xi=xi)


def _involute_half(rk: Rack, radius: float) -> float:
    """The involute's half tooth-thickness angle at `radius`, written out again."""
    phi = math.acos(min(1.0, rk.rb / radius))
    return rk.psi_p + (math.tan(rk.alpha) - rk.alpha) - (math.tan(phi) - phi)


def junction_gaps(curve: RootCurve, rk: Rack) -> tuple[float, float | None]:
    """How far the curve's last point is from the involute: (the half-angle gap against
    the involute at its radius, rad; and, on a tangent junction, the radius gap against
    sqrt(rb^2 + xi^2) relative to the radius)."""
    radius, half = curve.points[-1]
    angle_gap = abs(half - _involute_half(rk, radius))
    if curve.join == "crossing":
        return angle_gap, None
    return angle_gap, abs(radius - math.hypot(rk.rb, rk.xi)) / radius


def check_curve(curve: RootCurve, rk: Rack) -> list[str]:
    """The ways a generated curve disagrees with the closed forms; empty when none."""
    problems: list[str] = []
    points = curve.points
    if len(points) != ROOT_CURVE_POINTS:
        problems.append(f"{len(points)} points, not {ROOT_CURVE_POINTS}")
    if not all(math.isfinite(v) for point in points for v in point):
        problems.append("a point is not finite")
        return problems
    radii = [radius for radius, _ in points]
    if radii[0] != rk.rf:
        problems.append(f"first radius {radii[0]!r} is not the root circle {rk.rf!r}")
    if not all(lo < hi for lo, hi in pairwise(radii)):
        problems.append("radius does not strictly rise")
    if max(radii) > rk.ra:
        problems.append(f"radius {max(radii):.6g} above the tip circle {rk.ra:.6g}")
    undercut = rk.xi < -TROCHOID_JOIN_EPS * rk.rb
    if (curve.join == "crossing") != undercut:
        problems.append(f"join {curve.join} but xi is {rk.xi:.3e} mm")
    if curve.join == "crossing":
        if not rk.rb > rk.rf:
            problems.append("a crossing with rb <= rf (F9's nesting)")
        outside = [(radius, half) for radius, half in points[:-1]
                   if radius >= rk.rb and half >= _involute_half(rk, radius)]
        if outside:
            problems.append(f"{len(outside)} points before the junction are outside the involute")
    angle_gap, radius_gap = junction_gaps(curve, rk)
    # Inside the join band the flank join is the form point, not the involute's: the
    # cutter's flank foot sits at negative roll, on the involute's continuation through
    # the base circle, so its half-angle differs by 2*(tan(phi) - phi), tan(phi) =
    # |xi|/rb. That is geometry, at most 6.7e-13 rad at the band's edge for eps = 1e-4
    # (measured 2.4e-13 on the two gears of the product inside it), added to the bar.
    # Only on a tangent join: a crossing's end is the root the bisection put on the
    # involute itself, so it gets the bare bar. With the term applied to every negative
    # xi the 10-tooth, 20 degree gear (xi -1.21 mm) accepted a 1.1e-2 rad miss
    # (cross-review XR-01, 2026-10-08).
    phi = math.atan(max(-rk.xi, 0.0) / rk.rb) if curve.join == "tangent" else 0.0
    if angle_gap > SWEEP_BAR + 2 * (math.tan(phi) - phi):
        problems.append(f"last half-angle {angle_gap:.2e} rad off the involute")
    if radius_gap is not None and radius_gap > SWEEP_BAR:
        problems.append(f"last radius {radius_gap:.2e} (relative) off sqrt(rb^2 + xi^2)")
    return problems


_REFUSALS = ("nothing radial to replace", "tip land gone", "tooth severed")


def check_case(kwargs: dict[str, object], rho: float,
               *, worst: dict[str, float] | None = None) -> tuple[str, list[str]]:
    """Build one gear, ask `root_mode` and `trochoid_root` about it and compare both with
    the closed forms of `rack`: (the outcome label, the problems found).

    The label is `not a gear` when GearParams refuses the fields, the refusal's reason, or
    `trochoid/<join>` (with `/capped` when the cutter trimmed the tip radius). The
    refusals `rb <= rf` and `a0 < 0` are predicted here from the rack and must be the
    reason `root_mode` gives; for every other gear a curve or `tooth severed` is expected,
    and `bracket degenerate` or `curve invalid` is a problem. `worst`, when given, keeps
    the largest junction gaps seen per join.
    """
    try:
        p = GearParams.model_validate(kwargs)
    except ValidationError:
        return "not a gear", []
    rk = rack(p, rho)
    rm = root_mode(p, profile(p), requested="trochoid", rho=rho)
    problems: list[str] = []
    if rk.rb <= rk.rf:
        expected: str | None = "nothing radial to replace"
    elif rk.a0 < 0:
        expected = "tip land gone"
    else:
        expected = None
    if expected is not None:
        if rm.reason != expected:
            problems.append(f"expected {expected}, root_mode says {rm.reason}")
        return rm.reason or "trochoid", problems
    if rm.cutter is None:
        return "trochoid", ["no cutter although a trochoid was requested"]
    c = rm.cutter
    if abs(c.rho - rk.rho) > 1e-12 or abs(c.xi - rk.xi) > 1e-9 * max(1.0, rk.m):
        problems.append(f"cutter rho {c.rho!r} xi {c.xi!r} against rack {rk.rho!r} {rk.xi!r}")
    curve = trochoid_root(c)
    if rm.reason is not None:
        if rm.reason not in ("tooth severed", "bracket degenerate", "curve invalid"):
            problems.append(f"root_mode says {rm.reason} where the rack predicts a curve")
        if curve is not None:
            problems.append(f"{rm.reason} but trochoid_root returned a curve")
        return rm.reason, problems
    if curve is None:
        return "trochoid", ["root_mode says trochoid but trochoid_root returned none"]
    problems += check_curve(curve, rk)
    if worst is not None:
        angle_gap, radius_gap = junction_gaps(curve, rk)
        key = curve.join if rk.xi >= 0 or curve.join == "crossing" else "tangent in band"
        worst[f"{key} rad"] = max(worst.get(f"{key} rad", 0.0), angle_gap)
        if radius_gap is not None:
            worst["tangent radius"] = max(worst.get("tangent radius", 0.0), radius_gap)
    capped = "/capped" if c.rho < c.rho_requested else ""
    return f"trochoid/{curve.join}{capped}", problems


def _flank_points(c: Cutter) -> tuple[list[float], tuple[tuple[float, float], ...]] | None:
    """The 16 samples `calc._root_curve` takes along a cutter's flank (uniform in
    tan(beta), the last at the junction) with their contact-normal angles, rebuilt here
    because `trochoid_root` returns None for a severed tooth; None when no junction."""
    junction = _junction(c, TROCHOID_JOIN_EPS)
    if junction is None:
        return None
    s_stop = math.tan(junction[0])
    n = ROOT_CURVE_POINTS
    betas = [math.atan(s_stop * i / (n - 1)) for i in range(n - 1)] + [junction[0]]
    return betas, tuple(_trochoid_point(c, beta) for beta in betas)


def _severed_waist(c: Cutter) -> float:
    """The half-angle at the narrowest point of a severed tooth's curve, rad, to list it
    in the refusals."""
    flank = _flank_points(c)
    return math.nan if flank is None else _waist(c, *flank)[1]


_LIST_HEADER = ("grid", "teeth", "module", "pressure_angle", "profile_shift", "backlash",
                "rho_requested", "rho_used", "reason", "waist_half_angle")


def _refusal_row(grid: str, kwargs: dict[str, object], rho: float, reason: str) -> list[str]:
    c = cutter(GearParams.model_validate(kwargs), rho)
    waist = f"{_severed_waist(c):.6g}" if reason == "tooth severed" else ""
    return [grid, str(kwargs["teeth"]), f"{kwargs['module']:g}", f"{kwargs['pressure_angle']:g}",
            f"{kwargs['profile_shift']:g}", f"{kwargs['backlash']:g}", f"{rho:g}",
            f"{c.rho:g}", reason, waist]


def run_sweep(list_path: Path | None, stride: int) -> int:
    started = datetime.now(UTC)
    load_before = _load()
    cases = itertools.islice(sweep_cases(), 0, None, stride)
    tally: Counter[str] = Counter()
    by_module: Counter[tuple[float, str]] = Counter()
    problems: list[tuple[str, dict[str, object], float, list[str]]] = []
    worst: dict[str, float] = {}
    rows: list[list[str]] = []
    total = 0
    t0 = time.perf_counter()
    for grid, kwargs, rho in cases:
        total += 1
        outcome, found = check_case(kwargs, rho, worst=worst)
        tally[outcome] += 1
        by_module[(float(str(kwargs["module"])), outcome.split("/")[0])] += 1
        if found:
            problems.append((grid, kwargs, rho, found))
        if outcome in _REFUSALS:
            rows.append(_refusal_row(grid, kwargs, rho, outcome))
    wall = time.perf_counter() - t0
    load_after = _load()
    if list_path is not None:
        with list_path.open("w", newline="") as handle:
            writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
            writer.writerow(_LIST_HEADER)
            writer.writerows(rows)
    print("## Generator sweep (`bench.trochoid sweep`)\n")
    print("#### Host state\n")
    print(f"- Machine: {machine_facts()}")
    print(f"- Python {platform.python_version()}")
    print(f"- Read {started:%Y-%m-%dT%H:%M:%SZ}; 1-minute load {load_before} before, "
          f"{load_after} after")
    print(f"- {total} cases (stride {stride}) in {wall:.2f} s wall\n")
    print("| outcome | cases |")
    print("|---|---|")
    for outcome, count in sorted(tally.items()):
        print(f"| {outcome} | {count} |")
    print("\n| module | " + " | ".join(sorted({o for _, o in by_module})) + " |")
    print("|---|" + "---|" * len({o for _, o in by_module}))
    for module in sorted({m for m, _ in by_module}):
        print(f"| {module:g} | " + " | ".join(
            str(by_module[(module, o)]) for o in sorted({o for _, o in by_module})) + " |")
    print(f"\nWorst junction gaps (bar {SWEEP_BAR:g}): "
          + "; ".join(f"{k} {v:.2e}" for k, v in sorted(worst.items())))
    numeric = tally["bracket degenerate"] + tally["curve invalid"]
    print(f"\nproblems: {len(problems)}; bracket degenerate: {tally['bracket degenerate']}; "
          f"curve invalid: {tally['curve invalid']}")
    for grid, kwargs, rho, found in problems[:20]:
        print(f"- {grid} {kwargs} rho {rho}: {'; '.join(found)}")
    if problems or numeric:
        print("\nverdict: FAIL")
        return 1
    print("\nverdict: ok")
    return 0


# --- the swept-cutter oracle over the whole product (D-13, 18-04) -------------------------
# The gate reads twelve rows (tests/test_trochoid.py); here every trochoid curve of the
# sweep product is read the same way, and every severed tooth must read a gouge.

# mm, the same number as tests/test_trochoid.py's ORACLE_BAR_MM, which carries the two
# measured numbers it rests on; a test pins the two equal (this module cannot import that
# one: it imports this).
ORACLE_BAR_MM = 1e-9
# The pooled run also prints the worst reading over its first SERIAL_SLICE trochoid cases,
# which `--serial-slice` judges in-process, so the two are comparable.
SERIAL_SLICE = 200
_TESTS = Path(__file__).resolve().parents[1] / "tests"

OracleCase = tuple[str, dict[str, object], float, str]
_GEAR_FIELDS = ("teeth", "module", "pressure_angle", "profile_shift", "backlash")


def _oracle_cases() -> list[OracleCase]:
    """The cases of `sweep_cases()` the oracle can judge, in order: (grid, fields, tip
    radius requested, `trochoid` where a curve exists, `severed` where the tooth is cut
    through). Every other case is a refusal the sweep already lists."""
    cases: list[OracleCase] = []
    for grid, kwargs, rho in sweep_cases():
        try:
            p = GearParams.model_validate(kwargs)
        except ValidationError:
            continue
        reason = root_mode(p, profile(p), requested="trochoid", rho=rho)
        if reason.mode == "trochoid":
            cases.append((grid, kwargs, rho, "trochoid"))
        elif reason.reason == "tooth severed":
            cases.append((grid, kwargs, rho, "severed"))
    return cases


def _oracle(case: OracleCase) -> float:
    """One case through the swept-cutter oracle (a module-level function: spawn workers
    import it by name). A trochoid case returns the largest |reading| over its 16 points,
    mm. A severed case returns the lowest reading over the 16 samples and the refined
    waist of its one flank, with the neighbouring cutter teeth on, mm: the oracle agrees
    with the refusal when that is a gouge (the next space's cutter is what cuts the
    tooth through, so the neighbours are what see it)."""
    sys.path.insert(0, str(_TESTS))
    from trochoid_oracle import clearance  # the tests/ root, put on the path just above

    _, kwargs, rho, kind = case
    p = GearParams.model_validate(kwargs)
    c = root_mode(p, profile(p), requested="trochoid", rho=rho).cutter
    if c is None:
        raise ValueError(f"no cutter for {kwargs} at tip radius {rho}")

    def read(points: tuple[tuple[float, float], ...]) -> list[float]:
        return clearance(points, teeth=p.teeth, module=p.module,
                         pressure_angle=p.pressure_angle, profile_shift=p.profile_shift,
                         backlash=p.backlash, rho=c.rho)

    if kind == "trochoid":
        curve = trochoid_root(c)
        if curve is None:
            raise ValueError(f"no curve for {kwargs} at tip radius {rho}")
        return max(abs(v) for v in read(curve.points))
    flank = _flank_points(c)
    if flank is None:
        raise ValueError(f"no junction for {kwargs} at tip radius {rho}")
    return min(read((*flank[1], _waist(c, *flank))))


def run_oracle(serial_slice: int) -> int:
    started = datetime.now(UTC)
    load_before = _load()
    cases = _oracle_cases()
    trochoid_idx = [i for i, case in enumerate(cases) if case[3] == "trochoid"]
    workers = 1 if serial_slice else (os.cpu_count() or 1)
    t0 = time.perf_counter()
    if serial_slice:
        picked = trochoid_idx[:serial_slice]
        readings = {i: _oracle(cases[i]) for i in picked}
    else:
        with multiprocessing.get_context("spawn").Pool(workers) as pool:
            readings = dict(enumerate(pool.imap(_oracle, cases, chunksize=8)))
    wall = time.perf_counter() - t0
    load_after = _load()

    judged = [i for i in trochoid_idx if i in readings]
    severed = [i for i, case in enumerate(cases) if case[3] == "severed" and i in readings]
    first = [i for i in trochoid_idx[:SERIAL_SLICE] if i in readings]
    print("## Swept-cutter oracle over the sweep product (`bench.trochoid oracle`)\n")
    print("#### Host state\n")
    print(f"- Machine: {machine_facts()}")
    print(f"- Python {platform.python_version()}")
    print(f"- Read {started:%Y-%m-%dT%H:%M:%SZ}; 1-minute load {load_before} before, "
          f"{load_after} after")
    print(f"- {len(readings)} cases judged in {wall:.1f} s wall on {workers} "
          f"worker{'s' if workers != 1 else ''} "
          f"({'serial slice, in this process' if serial_slice else 'spawn pool'})\n")
    bad = 0
    if judged:
        ranked = sorted(judged, key=lambda i: readings[i], reverse=True)
        per_m_i = max(judged, key=lambda i: readings[i] / float(str(cases[i][1]["module"])))
        for label, i in (("worst |reading|", ranked[0]), ("worst per module", per_m_i)):
            grid, kwargs, rho, _ = cases[i]
            module = float(str(kwargs["module"]))
            gear = {k: kwargs[k] for k in _GEAR_FIELDS}
            print(f"- {label}: {readings[i]:.3e} mm = {readings[i] / module:.3e} per module, "
                  f"grid {grid} {gear} at tip radius {rho:g} mm")
        print(f"- headroom of the bar over the worst reading: "
              f"{ORACLE_BAR_MM / max(readings[ranked[0]], 1e-300):.3g}x")
        print("- the five largest readings:")
        for i in ranked[:5]:
            grid, kwargs, rho, _ = cases[i]
            print(f"  - {readings[i]:.3e} mm: grid {grid} "
                  f"{ {k: kwargs[k] for k in _GEAR_FIELDS} } at tip radius {rho:g} mm")
        print(f"- readings above 1e-13 mm: {sum(readings[i] > 1e-13 for i in judged)} of "
              f"{len(judged)}")
        print(f"- trochoid cases judged: {len(judged)}; beyond the bar "
              f"({ORACLE_BAR_MM:g} mm): {sum(readings[i] > ORACLE_BAR_MM for i in judged)}")
        bad += sum(readings[i] > ORACLE_BAR_MM for i in judged)
        print(f"- worst |reading| over the first {len(first)} trochoid cases: "
              f"{max(readings[i] for i in first):.17e} mm")
    if severed:
        agreed = [i for i in severed if readings[i] < -ORACLE_BAR_MM]
        shallowest = max(readings[i] for i in severed)
        print(f"- tooth severed cases: {len(severed)}; the oracle reads a gouge (below "
              f"-{ORACLE_BAR_MM:g} mm) on {len(agreed)}; shallowest "
              f"{shallowest:.3e} mm, deepest {min(readings[i] for i in severed):.3e} mm")
        bad += len(severed) - len(agreed)
    if not judged and not severed:
        print("verdict: FAIL, no case judged")
        return 1
    print(f"\nverdict: {'FAIL' if bad else 'ok'}")
    return 1 if bad else 0


# --- the root-shape step at both boundaries (D-05, 18-05) --------------------------------
# The line a figure is judged by, written and pinned before any table is produced, so a
# contradiction is decided by a stated line and not afterwards (T-18-15).

PREMISE_STEP_PER_M = 0.14  # D-01's premise: about 0.14*m of root shape between 17 and 18
# teeth at 20 degrees (FEATURES' simulation, 18-RESEARCH Pattern 8)
PREMISE_TOLERANCE = 0.25   # either side: 18-RESEARCH measured 0.145*m, 3 % off the premise


def premise_holds(gap_mm: float, module: float) -> bool:
    """Whether a root-shape gap is within PREMISE_TOLERANCE either side of D-01's figure
    for this module; the sign of the gap does not matter, its size does."""
    nominal = PREMISE_STEP_PER_M * module
    return (1 - PREMISE_TOLERANCE) * nominal <= abs(gap_mm) <= (1 + PREMISE_TOLERANCE) * nominal


STEP_RADII = 2001  # radii the gap is read at, from the root circle to the higher junction
# 18-RESEARCH Pattern 8's two tables: (teeth, tip radius = root_fillet requested, mm).
# Module 1, 20 degrees, no shift, no backlash, so the figures per module read directly.
THRESHOLD_ROWS = [(z, rho) for rho in (0.38, 0.471) for z in range(16, 20)]
CROSSOVER_ROWS = [(z, rho) for rho in (0.0, 0.38, 0.471) for z in range(40, 44)]


@dataclass(frozen=True)
class StepRow:
    teeth: int
    rho: float          # tip radius asked for, mm: also the root_fillet requested
    fillet: float       # the shipped fillet actually used, mm (rounded, capped to the gap)
    mode: str           # root_mode's answer for this request
    reason: str         # and why it stayed radial, "-" when it did not
    join: str           # the curve's join, "-" when no curve exists
    rb_minus_rf: float  # mm
    step: float         # largest-magnitude same-radius arc gap, mm, sign kept
    radius: float       # where it sits, mm
    junction: float     # radius of the trochoid's own junction with the involute, mm
    spline: float       # radius where the shipped involute spline starts, mm


def _bisect_radius(radius_at: Callable[[float], float], target: float,
                   lo: float, hi: float) -> float:
    """The parameter in [lo, hi] at which a radius that rises with it reads `target`."""
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if radius_at(mid) < target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def step_row(teeth: int, rho: float) -> StepRow:
    """One row of a step table: the shipped root zone of one flank, rebuilt the way
    `model._outline` builds it, against the trochoid, at 2,001 radii from the root circle
    to the higher of the two outlines' junctions with the involute. The gap is
    `R * (h_trochoid(R) - h_shipped(R))`, h the half-angle from the tooth centre, so it is
    the arc length between the two outlines at one radius; positive where the trochoid
    lies deeper into the tooth space. The half-angle of the shipped outline comes from
    the fillet arc, the lead-in line or the involute, whichever holds that radius."""
    from spur.model import _fillet_corner, _polar  # loads the kernel: here only (18-05)

    p = _gear(teeth=teeth, module=1.0, pressure_angle=20.0, profile_shift=0.0,
              backlash=0.0, root_fillet=rho)
    pr = profile(p)
    fillet = root_fillet(p)
    rm = root_mode(p, pr, requested="trochoid", rho=rho)
    c = cutter(p, rho)
    curve = trochoid_root(c)
    junction = _junction(c, TROCHOID_JOIN_EPS)
    if curve is None or junction is None:
        return StepRow(teeth, rho, fillet, rm.mode, rm.reason or "-", "-", pr.rb - pr.rf,
                       math.nan, math.nan, math.nan, spline_start(pr, fillet))
    beta_stop = junction[0]
    r_junction = curve.points[-1][0]

    # The shipped root zone of the left flank of the tooth at angle 0, as _outline builds it.
    r0 = spline_start(pr, fillet)
    straight = r0 > pr.rf + 1e-6
    first = _polar(r0, -pr.half_angle(r0))
    pieces: list[tuple[float, float, Callable[[float], float]]] = []  # (r_lo, r_hi, h(R))
    if straight:
        root_l = _polar(pr.rf, -pr.half_angle(pr.r_start))
        if fillet > 0:
            on_root, mid, on_line = _fillet_corner(root_l, first, pr.rf, fillet, -1)
            # The arc through the three points, as a circle: centre from the perpendicular
            # bisectors, swept from on_root to on_line through mid.
            ax, ay, bx, by, cx, cy = (on_root.x, on_root.y, mid.x, mid.y, on_line.x,
                                      on_line.y)
            det = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
            ux = ((ax**2 + ay**2) * (by - cy) + (bx**2 + by**2) * (cy - ay)
                  + (cx**2 + cy**2) * (ay - by)) / det
            uy = ((ax**2 + ay**2) * (cx - bx) + (bx**2 + by**2) * (ax - cx)
                  + (cx**2 + cy**2) * (bx - ax)) / det
            t0, t1, t2 = (math.atan2(q.y - uy, q.x - ux) for q in (on_root, mid, on_line))
            sweep = (t2 - t0 + math.pi) % (2 * math.pi) - math.pi
            if ((t1 - t0 + math.pi) % (2 * math.pi) - math.pi) * sweep < 0:
                sweep -= math.copysign(2 * math.pi, sweep)

            def arc_point(u: float) -> tuple[float, float]:
                return (ux + fillet * math.cos(t0 + sweep * u),
                        uy + fillet * math.sin(t0 + sweep * u))

            def arc_radius(u: float) -> float:
                return math.hypot(*arc_point(u))

            def arc_half(radius: float) -> float:
                x, y = arc_point(_bisect_radius(arc_radius, radius, 0.0, 1.0))
                return -math.atan2(y, x)

            pieces.append((pr.rf, on_line.Length, arc_half))
            line_from = on_line
        else:
            line_from = root_l

        def line_point(u: float) -> tuple[float, float]:
            return (line_from.x + (first.x - line_from.x) * u,
                    line_from.y + (first.y - line_from.y) * u)

        def line_radius(u: float) -> float:
            return math.hypot(*line_point(u))

        def line_half(radius: float) -> float:
            x, y = line_point(_bisect_radius(line_radius, radius, 0.0, 1.0))
            return -math.atan2(y, x)

        pieces.append((line_from.Length, first.Length, line_half))
    pieces.append((r0, math.inf, pr.half_angle))  # the involute spline
    for lo, hi, _ in pieces:
        if not lo <= hi:
            raise ValueError(f"radius does not rise along a piece of the shipped root: "
                             f"{lo} to {hi} at {teeth} teeth, tip radius {rho}")

    def shipped(radius: float) -> float:
        for lo, hi, half in pieces:
            if lo <= radius <= hi:
                return half(radius)
        return pieces[-1][2](radius)

    def trochoid(radius: float) -> float:
        if radius >= r_junction:
            return pr.half_angle(radius)  # the involute above the junction
        beta = _bisect_radius(lambda b: _trochoid_point(c, b)[0], radius, 0.0, beta_stop)
        return _trochoid_point(c, beta)[1]

    top = max(r0, r_junction)
    radii = [pr.rf + (top - pr.rf) * i / (STEP_RADII - 1) for i in range(STEP_RADII)]
    gaps = [(r * (trochoid(r) - shipped(r)), r) for r in radii]
    step, radius = max(gaps, key=lambda g: abs(g[0]))
    return StepRow(teeth, rho, fillet, rm.mode, rm.reason or "-", curve.join, pr.rb - pr.rf,
                   step, radius, r_junction, r0)


def _step_table(title: str, rows: list[StepRow]) -> None:
    print(f"{title}\n")
    print("| teeth | tip radius rho | shipped fillet | root_mode | join | rb - rf | step "
          "(mm) | step / m | at R (mm) | trochoid junction R | spline start R |")
    print("|---|---|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        mode = r.mode if r.reason == "-" else f"{r.mode} ({r.reason})"
        print(f"| {r.teeth} | {r.rho:g} | {r.fillet:g} | {mode} | {r.join} | "
              f"{r.rb_minus_rf:+.4f} | {r.step:+.4f} | {r.step:+.4f} | {r.radius:.4f} | "
              f"{r.junction:.4f} | {r.spline:.4f} |")
    print()


def run_step() -> int:
    started = datetime.now(UTC)
    load_before = _load()
    threshold = [step_row(z, rho) for z, rho in THRESHOLD_ROWS]
    crossover = [step_row(z, rho) for z, rho in CROSSOVER_ROWS]
    load_after = _load()
    print("## Root-shape step (`bench.trochoid step`)\n")
    print("#### Host state\n")
    print(f"- Machine: {machine_facts()}")
    print(f"- Python {platform.python_version()}, "
          + ", ".join(f"{d} {metadata.version(d)}" for d in ("cadquery", "cadquery-ocp")))
    print(f"- Read {started:%Y-%m-%dT%H:%M:%SZ}; 1-minute load {load_before} before, "
          f"{load_after} after\n")
    print("Module 1, 20 degrees, no shift, no backlash, bore and recesses off; the tip "
          "radius asked for is also the root fillet requested. The step is the "
          "largest-magnitude same-radius arc gap `R * (h_trochoid(R) - h_shipped(R))`, sign "
          "kept, from the root circle to the higher of the two junctions "
          f"({STEP_RADII} radii); `step / m` is the same figure per module.\n")
    _step_table("### Undercut threshold (teeth 16-19)", threshold)
    _step_table("### rb = rf crossover (teeth 40-43)", crossover)
    judged = [r for r in threshold if r.teeth in (17, 18)]
    offending = [r for r in judged
                 if not (math.isfinite(r.step) and premise_holds(r.step, 1.0))]
    low = (1 - PREMISE_TOLERANCE) * PREMISE_STEP_PER_M
    high = (1 + PREMISE_TOLERANCE) * PREMISE_STEP_PER_M
    print(f"Rule: D-01's premise holds when every 17- and 18-tooth row of the threshold "
          f"table has a gap within {PREMISE_TOLERANCE:.0%} either side of "
          f"{PREMISE_STEP_PER_M} m ({low:.4f} to {high:.4f} mm at module 1).\n")
    if offending:
        print("D-01 premise contradicted by: "
              + "; ".join(f"{r.teeth} teeth at tip radius {r.rho:g} ({r.step:+.4f} mm)"
                          for r in offending))
        return 1
    print("D-01 premise holds")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m bench.trochoid", description=__doc__)
    sub = parser.add_subparsers(dest="scenario", required=True)
    sub.add_parser("epsilon", help="measure TROCHOID_JOIN_EPS (D-09)")
    oracle = sub.add_parser("oracle", help="the swept-cutter oracle over the whole product")
    oracle.add_argument("--serial-slice", type=int, default=0, metavar="N",
                        help="judge the first N trochoid cases in this process instead of "
                             f"the pool (the pooled run prints the first {SERIAL_SLICE})")
    sub.add_parser("step", help="the root-shape step at both boundaries (D-05)")
    sweep = sub.add_parser("sweep", help="the generator over the allowed box (D-12)")
    sweep.add_argument("--list", type=Path, metavar="PATH",
                       help="write every generator refusal as a tab-separated file")
    sweep.add_argument("--stride", type=int, default=1,
                       help="run every STRIDE-th case (the gate test's sample)")
    args = parser.parse_args(argv)
    if args.scenario == "epsilon":
        return run_epsilon()
    if args.scenario == "oracle":
        return run_oracle(args.serial_slice)
    if args.scenario == "step":
        return run_step()
    return run_sweep(args.list, args.stride)


if __name__ == "__main__":
    sys.exit(main())
