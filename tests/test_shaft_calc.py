"""The shaft's derived numbers: the default shaft end to end through `derive_shaft`.

Mirrors tests/test_calc.py. The tip, root, shift and thickness formulas cite their DIN 5480-1
clauses in din5480.py. The approved anchors (one DIN 5480-1 row, four DIN 5480-2 rows) are
pinned in tests/test_din5480_anchors.py, where M1 agrees at the standard's tabulated pin.
The printed pin D_Re is the tool's theoretical pin, not that tabulated one, and the form
diameter d_Ff has no construction in the standard, so the pin and M_Re numbers here pin what
the code does, not a table value.
"""

import re

import pytest
import shaft_oracle
from pydantic import ValidationError
from test_din5480 import M_GRID

from spur import din5480, shaft_calc
from spur.din5480 import Designation, parse_designation
from spur.shaft_calc import (
    FORM_DIAMETER_UNPROVEN,
    MEASURE_AT_NOMINAL_THICKNESS,
    ODD_Z_UNCONFIRMED,
    THEORETICAL_PIN,
    PinReading,
    ShaftDimensions,
    derive_shaft,
    pin_contact_window,
    pin_measurement,
)
from spur.shaft_params import ShaftParams

DEFAULT_HOBBED_ROOT_WARNING = (
    "The root diameter is the theoretical (broaching) root. A hobbed shaft's root is 0.1*m "
    "smaller (DIN 5480-1 cl. 7.1): hobbed: root_d - 0.1*m = 22.125 mm. That is not the whole "
    "list: the standard names root depths for other processes too (DIN 5480-1 cl. 7.1), and "
    "this tool gives none of them."
)


def _hobbed_warning(p: ShaftParams) -> str:
    """The root_d sentence, picked by its content so a reordering of the list cannot move it."""
    return next(w for w in derive_shaft(p).warnings if "hobbed" in w)


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
    assert d.warnings == (FORM_DIAMETER_UNPROVEN, THEORETICAL_PIN, DEFAULT_HOBBED_ROOT_WARNING,
                          MEASURE_AT_NOMINAL_THICKNESS)


def test_the_default_shaft_is_designated_w_25x1_25x18x8f() -> None:
    """The designation is the standard's notation, and the default's parses back to the
    default (D-05): the codec and the parameter model name the same shaft."""
    designation = derive_shaft(ShaftParams()).designation
    assert designation == "W 25x1.25x18x8f"
    assert parse_designation(designation) == Designation(25.0, 1.25, 18, "8f")
    assert ShaftParams(**parse_designation(designation)._asdict()) == ShaftParams()


def test_the_shaft_dimensions_keys_are_fixed() -> None:
    """These keys become Phase 33's dims rows, in this order; renaming or moving one after
    Phase 33 changes the API document. The warnings are the same on every call."""
    assert list(ShaftDimensions.model_fields) == [
        "reference_d", "profile_shift", "profile_shift_mm", "pitch_d", "tip_d", "root_d",
        "nominal_thickness", "form_d", "pin_d", "measure_over_pins", "designation",
        "warnings",
    ]
    assert derive_shaft(ShaftParams()).warnings == derive_shaft(ShaftParams()).warnings


def test_the_default_shaft_prints_its_pin_and_measure_over_pins() -> None:
    """D_Re 2.73 is the theoretical pin rounded to 0.01 mm; M_Re is for that pin. The form
    diameter stays null, with its reason, because no DIN 5480 row proves the construction.
    The designation names a fit, so a printed M_Re says in a warning that it is the measure
    at the nominal thickness and carries no allowance or tolerance for that fit."""
    d = derive_shaft(ShaftParams())
    assert d.pin_d == 2.73
    assert d.measure_over_pins == 27.999
    assert d.form_d is None
    assert d.warnings == (FORM_DIAMETER_UNPROVEN, THEORETICAL_PIN, DEFAULT_HOBBED_ROOT_WARNING,
                          MEASURE_AT_NOMINAL_THICKNESS)
    assert MEASURE_AT_NOMINAL_THICKNESS == (
        "M_Re is for this pin and is the measure at the nominal tooth thickness; it carries "
        "no allowance or tolerance for the fit.")
    assert any("M_Re is for this pin" in w for w in d.warnings)


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
    """W25x1.25x19: the pin is given, M_Re is not given while the odd-count gate stays
    (D-13), and the sentences say both."""
    d = derive_shaft(ShaftParams(teeth=19))
    assert d.pin_d == 2.36
    assert d.measure_over_pins is None
    assert ODD_Z_UNCONFIRMED in d.warnings
    assert THEORETICAL_PIN in d.warnings
    # No M_Re is printed, so there is no measure to qualify and no M_Re "for this pin": that
    # sentence would sit beside ODD_Z_UNCONFIRMED's "M_Re is not given" (31-REVIEW IN-07).
    assert MEASURE_AT_NOMINAL_THICKNESS not in d.warnings
    assert not any("M_Re is for this pin" in w for w in d.warnings)


def test_the_pin_sentence_says_the_standard_tabulates_a_different_pin() -> None:
    """DIN 5480-2 tabulates a measuring pin D_M per size, and it differs from the theoretical
    pin for most sizes (the default shaft: D_M 2.75, theoretical 2.73; tests/
    test_din5480_anchors.py), so the sentence says so (31-REVIEW IN-03, WR-11)."""
    assert THEORETICAL_PIN.endswith(
        "DIN 5480-2 tabulates its own measuring pin D_M for the sizes it lists, and for most "
        "of them it differs from this pin.")
    assert "M_Re" not in THEORETICAL_PIN
    assert "It is not the D_Re that DIN 5480 tabulates" not in THEORETICAL_PIN


def test_no_pin_sentence_is_printed_when_no_pin_is_given(
        monkeypatch: pytest.MonkeyPatch) -> None:
    """pin_measurement cannot return a null pin for the theoretical pin today (D-20), so the
    null reading is injected: it goes live in Phase 34. THEORETICAL_PIN describes a D_Re,
    and none is printed here, so it would sit beside "M_Re and D_Re not given"."""
    reason = "M_Re and D_Re not given: injected."
    monkeypatch.setattr(shaft_calc, "pin_measurement",
                        lambda _p, _pin_d: PinReading(None, None, (reason,)))
    d = derive_shaft(ShaftParams())
    assert d.pin_d is None
    assert reason in d.warnings
    assert THEORETICAL_PIN not in d.warnings


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


def test_every_shaft_warns_that_a_hobbed_root_is_smaller_than_root_d() -> None:
    """DIN 5480-1 cl. 7.1: root_d is the theoretical (broaching) root; hobbing takes 0.1*m
    off it. The default shaft says 22.125 = 22.250 - 0.125."""
    d = derive_shaft(ShaftParams())
    assert DEFAULT_HOBBED_ROOT_WARNING in d.warnings
    assert d.root_d == 22.25


def test_the_hobbed_root_of_w_120x3x38x8f_is_113_100_below_root_d_113_400() -> None:
    """The human's reading of cl. 7.1 for this designation: 113.400 - 0.3 = 113.100."""
    p = ShaftParams(**parse_designation("W 120x3x38x8f")._asdict())
    d = derive_shaft(p)
    assert d.root_d == 113.4
    assert ("hobbed: root_d - 0.1*m = 113.100 mm.") in _hobbed_warning(p)
    assert sum("hobbed" in w for w in d.warnings) == 1


def test_the_root_warning_prints_the_factor_the_value_is_computed_from(
        monkeypatch: pytest.MonkeyPatch) -> None:
    """One factor feeds both the number and the words beside it, so they cannot disagree
    (31-REVIEW IN-04). A drop of 0.2*m takes the default 22.250 to 22.000."""
    monkeypatch.setattr(shaft_calc, "HOBBED_ROOT_DROP", 0.2)
    warning = _hobbed_warning(ShaftParams())
    assert warning.count("0.2*m") == 2
    assert "0.1" not in warning
    assert "= 22.000 mm" in warning


def test_the_hobbed_root_drop_is_twice_the_gap_between_the_hobbing_and_broaching_depths() -> None:
    """h_fP is a radial depth and root_d a diameter: 2 * (0.60 - 0.55) = 0.1 times m."""
    assert din5480.H_FP_HOBBING == 0.60
    assert shaft_calc.HOBBED_ROOT_DROP == 0.1
    # A drop of 0 would make the sentence read "0*m smaller": H_FP moving onto the hobbing
    # depth is a decision for a person, not a sentence to ship (31-REVIEW IN-09).
    assert shaft_calc.HOBBED_ROOT_DROP > 0
    assert f"{shaft_calc.HOBBED_ROOT_DROP}*m" in (
        ShaftDimensions.model_fields["root_d"].description or "")


def test_the_root_diameter_field_says_it_is_the_theoretical_broaching_root() -> None:
    description = ShaftDimensions.model_fields["root_d"].description or ""
    assert "broaching" in description
    assert "cl. 7.1" in description
    assert "incomplete" in description


def test_the_root_warning_says_its_process_list_is_incomplete_and_names_no_other_depth() -> None:
    """Only the hobbed 0.1*m is given. Every other number in the sentence is the printed root
    (22.125 here); a dedendum factor or depth for another process would be a copy value the
    project has not been shown (T-31-13), so the sentence points at the clause instead."""
    warning = _hobbed_warning(ShaftParams())
    assert "not the whole list" in warning
    assert warning.count("DIN 5480-1 cl. 7.1") == 2
    numbers = re.findall(r"[0-9]+\.[0-9]+", warning.replace("cl. 7.1", "cl."))
    assert numbers == ["0.1", "0.1", "22.125"]
