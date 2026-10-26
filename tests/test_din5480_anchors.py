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

import pytest

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
