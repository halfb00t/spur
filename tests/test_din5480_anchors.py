"""The DIN 5480 anchor values the human approved by name at the 31-05 checkpoint.

The checkpoint ran on 2026-10-26. The human read DIN 5480-1:2006-03 in an unofficial English
translation marked as an uncontrolled copy and approved three values of one designation,
W 120x3x38x8f, from cl. 9.1, Fig. 6 (an example in the standard, not a normative table).
Each test below carries its part, clause and figure. No other value of the standard is in
this repository (REQUIREMENTS "No licensed value in the public repo").

Agreement is to the copy's last printed digit: half a unit of that digit, never wider.
Part 1 holds no size tables. On 2026-10-26 the human supplied DIN 5480-2:2006-05 (an English
translation) and approved four rows by name, from Tables 12/13 (m = 1.25) and 18/19 (m = 2):
W 25x1.25x18 (the default shaft), W 26x1.25x19 (an odd tooth count), W 30x2x14 (shift -0.05)
and W 30x2x13 (shift +0.45). Each row's x*m, s1, da1, df1, D_M and M1 are pinned below; no
other value of Part 2 is in this repository. This closes docs/tech_debt/resolved/2026-10-26-
din5480-anchor-rows-beyond-part-1-are-missing.md.
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


# DIN 5480-2:2006-05, approved by name on 2026-10-26. Per row: (designation, tables, x*m,
# s1, da1, df1, D_M, M1). Part 2 prints x*m to 4 decimals for m = 1.25 and to 1 for m = 2,
# s1 and M1 to 3, da1 and df1 to 2, and the half unit of each printed digit is the tolerance.
PART_2_ROWS = [
    ("W 25x1.25x18x8f", "Tables 12 and 13", 0.5625, 4, 2.613, 24.75, 22.25, 2.75, 28.050),
    ("W 26x1.25x19x8f", "Tables 12 and 13", 0.4375, 4, 2.469, 25.75, 23.25, 2.75, 29.026),
    ("W 30x2x14x8f", "Tables 18 and 19", -0.1, 1, 3.026, 29.6, 25.60, 4.0, 34.144),
    ("W 30x2x13x8f", "Tables 18 and 19", 0.9, 1, 4.181, 29.6, 25.60, 5.0, 35.984),
]


def _params(designation: str) -> ShaftParams:
    d = parse_designation(designation)
    return ShaftParams(reference_d=d.reference_d, module=d.module, teeth=d.teeth, fit=d.fit)


@pytest.mark.parametrize(("row", "tables", "xm", "xm_places", "s1", "da1", "df1", "pin", "m1"),
                         PART_2_ROWS, ids=[r[0] for r in PART_2_ROWS])
def test_anchor_part_2_basic_dimensions(row: str, tables: str, xm: float, xm_places: int,
                                        s1: float, da1: float, df1: float, pin: float,
                                        m1: float) -> None:
    """DIN 5480-2:2006-05, the nominal-dimensions table of the row's module: the shift x*m,
    tooth thickness s1, tip diameter da1 and theoretical root df1 (h_fP = 0.55*m, Part 2
    cl. 1) agree with the printed digits; x*m is compared unrounded at the table's digit and
    as printed at the tool's. W 30x2x14 and W 30x2x13 sit on the
    two edges of the shift range, -0.05 and +0.45, so the range is the standard's at m = 2."""
    p = _params(row)
    dims = derive_shaft(p)
    computed_xm = din5480.profile_shift(p.reference_d, p.module, p.teeth) * p.module
    assert computed_xm == pytest.approx(xm, abs=0.5 * 10 ** -xm_places)
    # The tool prints x*m to 3 decimals, so 0.5625 prints as 0.562: half a unit of the
    # tool's own digit, plus float noise on the tie.
    assert dims.profile_shift_mm == pytest.approx(xm, abs=0.0005 + 1e-9)
    assert dims.nominal_thickness == pytest.approx(s1, abs=0.0005)
    assert dims.tip_d == pytest.approx(da1, abs=0.005)
    assert dims.root_d == pytest.approx(df1, abs=0.005)


@pytest.mark.parametrize(("row", "tables", "xm", "xm_places", "s1", "da1", "df1", "pin", "m1"),
                         PART_2_ROWS, ids=[r[0] for r in PART_2_ROWS])
def test_anchor_part_2_measure_over_pins_at_the_tabulated_pin(row: str, tables: str, xm: float,
                                                              xm_places: int, s1: float,
                                                              da1: float, df1: float,
                                                              pin: float, m1: float) -> None:
    """DIN 5480-2:2006-05, the inspection-dimensions table of the row's module: M1 over two
    pins D_M at the nominal thickness, three decimals, so half a unit is 0.0005. The row is
    compared at the tabulated pin, not the tool's theoretical pin, which Part 2 does not
    print. W 26x1.25x19 is an odd tooth count, so this is the first row behind the odd-count
    factor cos(pi/(2*z)); the shaft still prints no M_Re for it (ODD_Z_UNCONFIRMED, D-13)."""
    p = _params(row)
    x = din5480.profile_shift(p.reference_d, p.module, p.teeth)
    s = din5480.tooth_thickness(p.module, x * p.module)
    reading = din5480.measure_over_pins(p.module, p.teeth, s, pin)
    assert reading is not None
    assert reading[0] == pytest.approx(m1, abs=0.0005)
    assert shaft_oracle.measure(p.module, p.teeth, x, pin) == pytest.approx(reading[0], abs=1e-9)
    if p.teeth % 2:
        assert derive_shaft(p).measure_over_pins is None
