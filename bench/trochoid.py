"""Measures the hob's trochoid root where the unit tests cannot afford to (Phase 18).

Scenarios, one subcommand each:

- `epsilon` (18-03): how close to the z_min double root the junction bracket survives, so
  `calc.TROCHOID_JOIN_EPS` is a measurement made in this repo and not a number carried
  over from a prototype (D-09).
- `sweep`, the full-grid swept-cutter oracle and the root-shape cost step arrive in the
  later plans of the phase.

It is not part of `make verify`: the scans take seconds to minutes and their timings
depend on the host, and a timing assertion on shared hardware would flap
(`bench/build_time.py`'s stance). Run it as `.venv/bin/python -m bench.trochoid <scenario>`
from the repo root. It prints Markdown and exits 1 when the verdict fails.

This module never imports `cadquery` (18-05's `step` imports `spur.model` inside its own
function), so a test can import the grid without loading the kernel.
"""

from __future__ import annotations

import argparse
import math
import os
import platform
import random
import statistics
import sys
from collections import Counter
from datetime import UTC, datetime

from pydantic import ValidationError

from bench import machine_facts
from spur.calc import _junction, cutter, profile
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m bench.trochoid", description=__doc__)
    sub = parser.add_subparsers(dest="scenario", required=True)
    sub.add_parser("epsilon", help="measure TROCHOID_JOIN_EPS (D-09)")
    args = parser.parse_args(argv)
    if args.scenario == "epsilon":
        return run_epsilon()
    return 2  # unreachable: argparse rejects an unknown scenario itself


if __name__ == "__main__":
    sys.exit(main())
