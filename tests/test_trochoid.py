"""The calc-tier proofs of Phase 18: the hob's cutter, the trochoid root generated from
it, the predicate that answers for a gear, and the swept-cutter oracle that reads the
curve as the cut boundary. The generator sweep over the allowed box lives in
tests/test_calc.py (D-13); the oracle itself is tests/trochoid_oracle.py, which shares
no code with spur.calc.
"""

import math

import pytest
from trochoid_oracle import clearance

from spur.calc import (
    profile,
    root_mode,
    trochoid_root,
)
from spur.params import GearParams

# mm, how far from zero the swept-cutter oracle may read a point of a correct curve.
# Two numbers set it: 18-RESEARCH's prototype noise floor, 6.7e-15 * module over 500
# allowed-box cases (so at most 6.7e-14 mm at module 10), and the oracle's own
# resolution after golden-section refinement, about 1e-15 mm. 1e-9 mm is at least
# 1.5e4 times the noise floor at module <= 10; 18-04 re-measures it over the gate rows
# and restates the headroom.
ORACLE_BAR_MM = 1e-9


def _gear(**fields: object) -> GearParams:
    """A test gear with the bore off: the default 9 mm bore refuses small gears."""
    return GearParams.model_validate(
        {"bore_d": 0, "bore_flat": 0, "bore_chamfer": 0, "recess_sides": "none", **fields})


def _swept(points: tuple[tuple[float, float], ...], p: GearParams, rho: float,
           *, neighbours: bool = True) -> list[float]:
    """The oracle's readings for `points` on gear `p` cut by tip radius `rho`."""
    return clearance(points, teeth=p.teeth, module=p.module, pressure_angle=p.pressure_angle,
                     profile_shift=p.profile_shift, backlash=p.backlash, rho=rho,
                     neighbours=neighbours)


def test_the_tracer_gear_is_cut_by_its_cutter_and_nothing_else() -> None:
    """The architecture on one path: 10 teeth, module 1, 20 degrees, no shift, no
    backlash, tip radius 0.38 mm. Chosen because it is undercut (z_min is 21.4 for a
    1.25 m rack with a sharp tip), so it takes the crossing branch -- the hard one --
    and because the research measured its crossing radius, 4.725602 mm (STACK 4.72560,
    base radius 4.698463), and the oracle's 1.1e-15 mm on it.

    The oracle carries the neighbouring cutter teeth and reads every point of the curve
    as the cut boundary. The control is the involute halfway between the base circle and
    the crossing radius: it runs through the material the hob removes, so it must read
    as a gouge. An oracle that reads 0 everywhere proves nothing, and this is what lets
    it fail.
    """
    p = _gear(teeth=10, module=1, pressure_angle=20, profile_shift=0, backlash=0)
    pr = profile(p)
    rm = root_mode(p, pr, requested="trochoid", rho=0.38)
    assert (rm.mode, rm.reason) == ("trochoid", None)
    assert rm.cutter is not None
    c = rm.cutter
    curve = trochoid_root(c)
    assert curve is not None
    assert curve.join == "crossing"
    assert len(curve.points) == 16
    assert curve.points[0] == (pr.rf, math.pi / 10 - c.a / pr.r)
    assert curve.points[-1][0] == pytest.approx(4.725602, abs=5e-7)

    readings = _swept(curve.points, p, c.rho)
    print(f"worst oracle reading on the tracer curve: {max(abs(v) for v in readings):.3e} mm")
    assert all(abs(v) <= ORACLE_BAR_MM for v in readings)

    # The involute formula is written out here again: the control must not borrow the
    # code under test.
    a = math.radians(20)
    r = 5.0
    psi_p = (math.pi / 2 - 0.0) / (2 * r)
    radius = (pr.rb + curve.points[-1][0]) / 2
    half = psi_p + (math.tan(a) - a) - (math.tan(math.acos(pr.rb / radius))
                                        - math.acos(pr.rb / radius))
    control = _swept(((radius, half),), p, c.rho)[0]
    print(f"involute control (a gouge): {control:.3e} mm")
    assert control < -1e-4
