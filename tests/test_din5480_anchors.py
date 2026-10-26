"""The DIN 5480 anchor values the human approved by name at the 31-05 checkpoint.

The checkpoint ran on 2026-10-26. The human read DIN 5480-1:2006-03 in an unofficial English
translation marked as an uncontrolled copy and approved three values of one designation,
W 120x3x38x8f, from cl. 9.1, Fig. 6 (an example in the standard, not a normative table).
Each test below carries its part, clause and figure. No other value of the standard is in
this repository (REQUIREMENTS "No licensed value in the public repo").

Agreement is to the copy's last printed digit: half a unit of that digit, never wider.
Part 1 holds no size tables, so the plan's minimum of two basic-dimension rows is not met;
the missing rows are filed as docs/tech_debt/active/2026-10-26-din5480-anchor-rows-beyond-
part-1-are-missing.md and are not replaced here by vendor numbers (D-06, D-08).
"""

import math

import pytest
import shaft_oracle

from spur import din5480
from spur.din5480 import parse_designation
from spur.shaft_calc import derive_shaft
from spur.shaft_params import ShaftParams

ROW = "W 120x3x38x8f"


def _row_params() -> ShaftParams:
    d = parse_designation(ROW)
    return ShaftParams(reference_d=d.reference_d, module=d.module, teeth=d.teeth, fit=d.fit)


def test_anchor_w120x3x38x8f_tip_diameter() -> None:
    """DIN 5480-1:2006-03, cl. 9.1, Fig. 6 (read from an unofficial translation): the tip
    diameter d_a1 of W 120x3x38x8f is 119.40, two decimals, so half a unit is 0.005."""
    p = _row_params()
    assert din5480.tip_diameter(p.reference_d, p.module) == pytest.approx(119.40, abs=0.005)
    assert derive_shaft(p).tip_d == pytest.approx(119.40, abs=0.005)


def test_anchor_w120x3x38x8f_form_diameter_is_a_limit_not_a_construction() -> None:
    """DIN 5480-1:2006-03, cl. 9.1, Fig. 6 (unofficial translation): the form diameter
    d_Ff1 of the shaft is printed as a maximum, 113.91. The copy's Tables 3 and 4 tie it to
    the mating part's tip diameter and a minimum clearance, so it is not a construction the
    tool can reproduce: the internal construction must stay at or below the maximum, at
    either dedendum, and `form_d` stays null (D-12, L08).
    """
    p = _row_params()
    x = din5480.profile_shift(p.reference_d, p.module, p.teeth)
    for h_fp in (0.55, 0.60):
        internal = din5480.form_diameter(p.module, p.teeth, x * p.module, h_fp, din5480.RHO_FP)
        assert internal <= 113.91
        assert shaft_oracle.form_diameter(p.module, p.teeth, x, h_fp, din5480.RHO_FP) <= 113.91
    assert derive_shaft(p).form_d is None


def test_anchor_w120x3x38x8f_measure_over_pins_at_the_rows_own_thickness_and_pin() -> None:
    """DIN 5480-1:2006-03, cl. 9.1, Fig. 6 (unofficial translation): M1 minimum is 125.956 at
    the gauge pin D_M 6.000 and the row's own thickness s 6.180, three decimals, so half a
    unit is 0.0005. Part 1 names these D_M, M1 and M2; M_Re and D_Re are the later parts'
    names (DIN 5480-15, 5.2.4.3), and the row is compared at its own inputs, not at the
    printed pin 5.93 or the nominal thickness. The oracle agrees at 1e-9 once the row's
    thickness is written as the shift that gives it.
    """
    p = _row_params()
    s, pin = 6.180, 6.000
    reading = din5480.measure_over_pins(p.module, p.teeth, s, pin)
    assert reading is not None
    assert reading[0] == pytest.approx(125.956, abs=0.0005)
    x = (s - math.pi * p.module / 2) / (2 * p.module * math.tan(math.radians(30.0)))
    assert shaft_oracle.measure(p.module, p.teeth, x, pin) == pytest.approx(reading[0], abs=1e-9)
