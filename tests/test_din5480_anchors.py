"""The DIN 5480 anchor values the human approved by name: one Part 1 row and four Part 2 rows,
and the Table 7 and d_Ff1 cells of three designations (34-15).

The 31-05 checkpoint ran on 2026-10-26. The human read DIN 5480-1:2006-03 in an unofficial
English translation marked as an uncontrolled copy and approved three values of one
designation, W 120x3x38x8f, from cl. 9.1, Fig. 6 (an example in the standard, not a
normative table). Each test below carries its part and clause, figure or table. No value of
the standard other than these, the Part 2 rows below and the 34-15 anchors at the end of the
file is in this repository (REQUIREMENTS "No licensed value in the public repo").

Agreement is to the copy's last printed digit: half a unit of that digit, never wider.
Part 1 holds no size tables. On 2026-10-26 the human supplied DIN 5480-2:2006-05 (an English
translation) and approved four rows by name, from Tables 12/13 (m = 1.25) and 18/19 (m = 2):
W 25x1.25x18 (the default shaft), W 26x1.25x19 (odd), W 30x2x14 (shift -0.05) and
W 30x2x13 (shift +0.45, also odd). Each row's x*m, s1, da1, df1, D_M and M1 are pinned below; no
other value of Part 2 is in this repository. This closes docs/tech_debt/resolved/2026-10-26-
din5480-anchor-rows-beyond-part-1-are-missing.md.

The 34-15 checkpoint ran on 2026-10-31, with the table file's sweeps in front of the human.
Three designations were approved by name: W 120x3x38x8f, W 25x1.25x18x8f and W 26x1.25x19x8f.
For each, `TABLE_7_ANCHORS` holds the Table 7 column, A_s of the letter f and the class 8
tolerance T_G, T_act and T_eff (DIN 5480-1:2006 cl. 10.9, Table 7, page 24); `TABLE_7_THICKNESS`
holds the three limit thicknesses those cells give (arithmetic on approved cells, no further
value of the copy); `PART_2_CONTACT` holds the Part 2 form diameter maximum d_Ff1 and the
gauge pin D_M. No other cell of any table is in this repository. 34-16 holds the private
table file to these constants exactly.
"""

import math

import pytest
import shaft_oracle

from spur import din5480
from spur.din5480 import parse_designation
from spur.din5480_tables import part_2_provenance
from spur.shaft_calc import GUARD_MARGIN_FACTOR, derive_shaft, pin_contact_window
from spur.shaft_params import ShaftParams

ROW = "W 120x3x38x8f"
# The page's worked example (DIN 5480-1:2006-03, cl. 9.1, Fig. 6): M1 minimum at the gauge pin
# 6.000. A name for the digits two tests below and 34-16's check of the table file compare to.
PAGE_EXAMPLE_M1_MIN = 125.956


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
    assert reading[0] == pytest.approx(PAGE_EXAMPLE_M1_MIN, abs=0.0005)
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
                         PART_2_ROWS, ids=[f"{r[0]}, {r[1]}" for r in PART_2_ROWS])
def test_anchor_part_2_basic_dimensions(row: str, tables: str, xm: float, xm_places: int,
                                        s1: float, da1: float, df1: float, pin: float,
                                        m1: float) -> None:
    """DIN 5480-2:2006-05, the nominal-dimensions table of the row's module: the shift x*m,
    tooth thickness s1, tip diameter da1 and theoretical root df1 (h_fP = 0.55*m, Part 2
    cl. 1) agree with the printed digits; x*m is compared unrounded at the table's digit and
    as printed at the tool's. W 30x2x14 and W 30x2x13 sit on the
    two edges of the shift range, -0.05 and +0.45, and are accepted, so both edges reach rows
    the standard prints."""
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
                         PART_2_ROWS, ids=[f"{r[0]}, {r[1]}" for r in PART_2_ROWS])
def test_anchor_part_2_measure_over_pins_at_the_tabulated_pin(row: str, tables: str, xm: float,
                                                              xm_places: int, s1: float,
                                                              da1: float, df1: float,
                                                              pin: float, m1: float) -> None:
    """DIN 5480-2:2006-05, the inspection-dimensions table of the row's module: M1 over two
    pins D_M at the nominal thickness, three decimals, so half a unit is 0.0005. The row is
    compared at the tabulated pin, not the tool's theoretical pin, which Part 2 does not
    print. W 26x1.25x19 and W 30x2x13 are odd tooth counts, the first rows behind the
    odd-count factor cos(pi/(2*z)); with a table file that lists them the shaft prints M_Re
    for them at the tabulated pin, and without one it stays null (ODD_Z_UNCONFIRMED, D-11)."""
    p = _params(row)
    x = din5480.profile_shift(p.reference_d, p.module, p.teeth)
    s = din5480.tooth_thickness(p.module, x * p.module)
    reading = din5480.measure_over_pins(p.module, p.teeth, s, pin)
    assert reading is not None
    assert reading[0] == pytest.approx(m1, abs=0.0005)
    assert shaft_oracle.measure(p.module, p.teeth, x, pin) == pytest.approx(reading[0], abs=1e-9)
    if p.teeth % 2:
        assert derive_shaft(p).measure_over_pins is None


# Approved by name at the 34-15 checkpoint, 2026-10-31. Per designation: (Table 7 column, A_s of
# f, T_G, T_act, T_eff), the deviations and tolerances in micrometres as printed.
TABLE_7_ANCHORS: dict[str, tuple[int, int, int, int, int]] = {
    "W 120x3x38x8f": (4, -28, 63, 40, 23),
    "W 25x1.25x18x8f": (8, -18, 40, 25, 15),
    "W 26x1.25x19x8f": (7, -20, 45, 28, 17),
}
# The limit thicknesses (s_vmax, s_max, s_min) in mm those cells give at the row's s1. The first
# is the standard's own worked example (DIN 5480-1:2006-03, cl. 9.1, Fig. 6); the other two are
# the cells added to s1 and carry no further value of the copy.
TABLE_7_THICKNESS: dict[str, tuple[float, float, float]] = {
    "W 120x3x38x8f": (6.243, 6.220, 6.180),
    "W 25x1.25x18x8f": (2.595, 2.580, 2.555),
    "W 26x1.25x19x8f": (2.449, 2.432, 2.404),
}
# DIN 5480-2:2006-05, per designation: (d_Ff1 maximum, gauge pin D_M, clause, tables, pages).
PART_2_CONTACT: dict[str, tuple[float, float, str, str, tuple[int, ...]]] = {
    "W 120x3x38x8f": (113.91, 6.0, "14", "22 and 23", (28, 29)),
    "W 25x1.25x18x8f": (22.44, 2.75, "9", "12 and 13", (18, 19)),
    "W 26x1.25x19x8f": (23.44, 2.75, "9", "12 and 13", (18, 19)),
}


@pytest.mark.parametrize("name", TABLE_7_ANCHORS)
def test_anchor_table_7_actual_and_effective_tolerances_add_up_to_the_total(name: str) -> None:
    """DIN 5480-1:2006, cl. 10.9, Table 7, page 24 (checkpoint 2026-10-31): the total tooth
    thickness tolerance T_G is the actual tolerance T_act plus the effective tolerance T_eff,
    whole micrometres, so there is no rounding to allow for."""
    _, _, t_g, t_act, t_eff = TABLE_7_ANCHORS[name]
    assert t_g == t_act + t_eff


@pytest.mark.parametrize("name", TABLE_7_ANCHORS)
def test_anchor_table_7_cells_give_the_limit_thicknesses(name: str) -> None:
    """DIN 5480-1:2006, cl. 10.9, Table 7, page 24, through Table 6 (checkpoint 2026-10-31):
    the cells of the designation's column and class 8, applied to the row's nominal thickness
    s1, give s_vmax, s_max and s_min. The three are compared to the third decimal, so half a
    unit is 0.0005; s1 is the tool's own, unrounded. W 120x3x38x8f is the standard's worked
    example."""
    _, a_s, t_g, _, t_eff = TABLE_7_ANCHORS[name]
    p = _params(name)
    xm = din5480.profile_shift(p.reference_d, p.module, p.teeth) * p.module
    s1 = din5480.tooth_thickness(p.module, xm)
    limits = din5480.thickness_limits(s1, a_s, t_g, t_eff)
    assert limits == pytest.approx(TABLE_7_THICKNESS[name], abs=0.0005)


def test_anchor_w120x3x38x8f_page_example_measure_over_pins_at_the_smallest_thickness() -> None:
    """DIN 5480-1:2006-03, cl. 9.1, Fig. 6, with Table 7 (checkpoint 2026-10-31): the worked
    example's M1 minimum, 125.956 at the gauge pin 6.000, three decimals, so half a unit is
    0.0005, comes out of the smallest actual thickness the Table 7 cells give, not only out of
    the page's rounded 6.180."""
    _, a_s, t_g, _, t_eff = TABLE_7_ANCHORS[ROW]
    p = _row_params()
    xm = din5480.profile_shift(p.reference_d, p.module, p.teeth) * p.module
    s_min = din5480.thickness_limits(din5480.tooth_thickness(p.module, xm), a_s, t_g, t_eff)[2]
    reading = din5480.measure_over_pins(p.module, p.teeth, s_min, 6.000)
    assert reading is not None
    assert reading[0] == pytest.approx(PAGE_EXAMPLE_M1_MIN, abs=0.0005)


@pytest.mark.parametrize("name", PART_2_CONTACT)
def test_anchor_part_2_form_diameter_maximum_bounds_the_guard_below(name: str) -> None:
    """DIN 5480-2:2006-05, the clause and tables of the row's module, named by
    `part_2_provenance` (checkpoint 2026-10-31): the guard's lower bound is the copy's d_Ff1
    maximum plus GUARD_MARGIN_FACTOR times the module (D-12), and the tabulated pin D_M touches
    at the nominal thickness inside the window, above that bound and below the tip diameter
    less the margin. The copy prints d_Ff1 to two decimals."""
    d_ff1, pin, clause, tables, pages = PART_2_CONTACT[name]
    p = _params(name)
    provenance = part_2_provenance(p.module)
    assert (provenance.part, provenance.clause, provenance.table, provenance.pages) == (
        2, clause, tables, pages)
    low, high = pin_contact_window(p, d_ff1)
    assert low == pytest.approx(d_ff1 + GUARD_MARGIN_FACTOR * p.module)
    xm = din5480.profile_shift(p.reference_d, p.module, p.teeth) * p.module
    reading = din5480.measure_over_pins(
        p.module, p.teeth, din5480.tooth_thickness(p.module, xm), pin)
    assert reading is not None
    assert low < reading[1] < high
