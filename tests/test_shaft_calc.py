"""The shaft's derived numbers: the default shaft end to end through `derive_shaft`.

Mirrors tests/test_calc.py. The formulas are ASSUMPTIONS until the 31-05 checkpoint
records their clauses, so these numbers pin what the code does, not what the standard says.
"""

import pytest
from pydantic import ValidationError

from spur import din5480
from spur.shaft_calc import ShaftDimensions, derive_shaft
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


def test_a_shaft_dimensions_result_cannot_be_changed() -> None:
    """A result shared between readers cannot change under them: ShaftDimensions is frozen,
    so every field assignment raises, and its one collection field is a tuple."""
    d = derive_shaft(ShaftParams())
    for name in ShaftDimensions.model_fields:
        with pytest.raises(ValidationError, match="frozen"):
            setattr(d, name, None)
    assert isinstance(d.warnings, tuple)


def test_the_dedendum_constant_moves_the_root_and_not_the_shift(
        monkeypatch: pytest.MonkeyPatch) -> None:
    """The shift term and the dedendum factor are two quantities that read 0.55 today
    (31-RESEARCH Pitfall 1). If the copy's h_fP is 0.60, only the root may move."""
    p = ShaftParams(reference_d=70, module=3, teeth=22)
    before = derive_shaft(p)
    assert before.root_d == 63.4
    monkeypatch.setattr(din5480, "H_FP", 0.60)
    after = derive_shaft(p)
    # 63.1 is KISSsoft's hobbing value for W70x3x22: a vendor cross-check, not the standard.
    assert after.root_d == 63.1
    for name in ("profile_shift", "profile_shift_mm", "pitch_d", "tip_d", "nominal_thickness"):
        assert getattr(after, name) == getattr(before, name), name
