"""The shaft's derived numbers: the default shaft end to end through `derive_shaft`.

Mirrors tests/test_calc.py. The formulas are ASSUMPTIONS until the 31-05 checkpoint
records their clauses, so these numbers pin what the code does, not what the standard says.
"""

from spur.shaft_calc import derive_shaft
from spur.shaft_params import ShaftParams


def test_the_default_shaft_derives_its_basic_dimensions() -> None:
    d = derive_shaft(ShaftParams())
    assert d.reference_d == 25.0
    assert d.profile_shift == 0.45
    # 0.5625 is an exact tie in binary64 and round() sends it to the even digit: the same
    # behaviour as the gear's r3 in calc.py.
    assert d.profile_shift_mm == 0.562
    assert d.pitch_d == 22.5
    assert d.tip_d == 24.75
    assert d.root_d == 22.25
    assert d.nominal_thickness == 2.613
    assert d.warnings == ()
