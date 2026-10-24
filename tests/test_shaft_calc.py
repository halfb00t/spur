"""The shaft's derived numbers: the default shaft end to end through `derive_shaft`.

Mirrors tests/test_calc.py. The formulas are ASSUMPTIONS until the 31-05 checkpoint
records their clauses, so these numbers pin what the code does, not what the standard says.
"""

import pytest
import shaft_oracle
from pydantic import ValidationError
from test_din5480 import M_GRID

from spur import din5480
from spur.shaft_calc import (
    FORM_DIAMETER_UNPROVEN,
    ODD_Z_UNCONFIRMED,
    THEORETICAL_PIN,
    ShaftDimensions,
    derive_shaft,
    pin_contact_window,
    pin_measurement,
)
from spur.shaft_params import ShaftParams


def _grid_shaft(case: tuple[float, int, float]) -> ShaftParams:
    m, z, x = case
    return ShaftParams(reference_d=shaft_oracle.reference_diameter(m, z, x), module=m, teeth=z)


def _case_id(case: tuple[float, int, float]) -> str:
    m, z, x = case
    return f"m{m}-z{z}-x{x}"


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
    assert d.warnings == (FORM_DIAMETER_UNPROVEN, THEORETICAL_PIN)


def test_the_default_shaft_prints_its_pin_and_measure_over_pins() -> None:
    """D_Re 2.73 is the theoretical pin rounded to 0.01 mm; M_Re is for that pin. The form
    diameter stays null, with its reason, because no DIN 5480 row proves the construction."""
    d = derive_shaft(ShaftParams())
    assert d.pin_d == 2.73
    assert d.measure_over_pins == 27.999
    assert d.form_d is None
    assert d.warnings == (FORM_DIAMETER_UNPROVEN, THEORETICAL_PIN)


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


def test_an_odd_tooth_count_prints_the_pin_and_no_measure_over_pins() -> None:
    """W25x1.25x19: the pin is given, M_Re waits for a DIN 5480 row that confirms the odd
    formula (D-13), and the sentences say both."""
    d = derive_shaft(ShaftParams(teeth=19))
    assert d.pin_d == 2.36
    assert d.measure_over_pins is None
    assert ODD_Z_UNCONFIRMED in d.warnings
    assert THEORETICAL_PIN in d.warnings


@pytest.mark.parametrize("case", M_GRID, ids=_case_id)
def test_the_form_diameter_is_null_with_its_reason_for_every_shaft(
    case: tuple[float, int, float],
) -> None:
    """d_Ff is never printed: none of the shaft's numbers equals the internal construction,
    which exists only as the guard's lower bound (D-12)."""
    m, z, x = case
    d = derive_shaft(_grid_shaft(case))
    assert d.form_d is None
    assert FORM_DIAMETER_UNPROVEN in d.warnings
    internal = round(din5480.form_diameter(m, z, x * m, din5480.H_FP, din5480.RHO_FP), 3)
    printed = [v for v in d.model_dump().values() if isinstance(v, float)]
    assert internal not in printed


def test_the_pin_contact_guard_nulls_a_pin_off_the_flank() -> None:
    """Direct calls, not through derive_shaft: at the theoretical pin the guard cannot fire
    (31-RESEARCH Pitfall 4, D-20); it goes live when Phase 34 passes the copy's D_Re."""
    p = ShaftParams()
    for pin in (1.0, 5.0, 0.01):
        reading = pin_measurement(p, pin)
        assert reading.pin_d is None
        assert reading.measure is None
        assert len(reading.warnings) == 1
        assert reading.warnings[0].startswith("M_Re and D_Re not given")
    ok = pin_measurement(p, 2.73)
    assert ok.pin_d == 2.73
    assert ok.measure is not None
    assert ok.warnings == ()


def test_the_pin_contact_window_is_closed() -> None:
    """The window's two ends are inside it. The pins that touch exactly on each end are
    found by bisection, then moved 1e-6 mm either way. The calls are direct because the
    theoretical pin never reaches an end (31-RESEARCH Pitfall 4, D-20)."""
    p = ShaftParams()
    m, z = p.module, p.teeth
    s = din5480.tooth_thickness(m, din5480.profile_shift(p.reference_d, m, z) * m)

    def contact(pin: float) -> float:
        result = din5480.measure_over_pins(m, z, s, pin)
        assert result is not None
        return result[1]

    def pin_touching_at(bound: float) -> float:
        lo, hi = 1.0, 5.0  # contact 21.756 below the low end, 25.144 above the high end
        for _ in range(100):
            mid = 0.5 * (lo + hi)
            if contact(mid) < bound:
                lo = mid
            else:
                hi = mid
        return 0.5 * (lo + hi)

    low, high = pin_contact_window(p)
    at_low, at_high = pin_touching_at(low), pin_touching_at(high)
    assert at_low == pytest.approx(1.6379, abs=1e-3)
    assert at_high == pytest.approx(4.1180, abs=1e-3)
    assert pin_measurement(p, at_low + 1e-6).measure is not None
    assert pin_measurement(p, at_low - 1e-6).measure is None
    assert pin_measurement(p, at_high - 1e-6).measure is not None
    assert pin_measurement(p, at_high + 1e-6).measure is None
    assert pin_measurement(p, at_low - 1e-6).warnings[0].startswith("M_Re and D_Re not given")


@pytest.mark.parametrize("case", M_GRID, ids=_case_id)
def test_the_printed_pin_is_on_the_gauge_step_and_the_measure_is_for_that_pin(
    case: tuple[float, int, float],
) -> None:
    m, z, x = case
    d = derive_shaft(_grid_shaft(case))
    theoretical = din5480.theoretical_pin_diameter(m, z, x * m)
    assert d.pin_d is not None
    assert round(d.pin_d, 2) == d.pin_d
    assert abs(d.pin_d - theoretical) <= 0.005
    if z % 2:
        assert d.measure_over_pins is None
    else:
        result = din5480.measure_over_pins(
            m, z, din5480.tooth_thickness(m, x * m), d.pin_d)
        assert result is not None
        assert d.measure_over_pins == round(result[0], 3)
