"""The shaft's derived numbers: the default shaft end to end through `derive_shaft`.

Mirrors tests/test_calc.py. The tip, root, shift and thickness formulas cite their DIN 5480-1
clauses in din5480.py. The approved anchors (one DIN 5480-1 row, four DIN 5480-2 rows) are
pinned in tests/test_din5480_anchors.py, where M1 agrees at the standard's tabulated pin.
The printed pin D_Re is the tool's theoretical pin, not that tabulated one, and the form
diameter d_Ff has no construction in the standard, so the pin and M_Re numbers here pin what
the code does, not a table value.
"""

import json
import math
import re
from pathlib import Path
from typing import Literal

import din5480_tables_fixture
import pytest
import shaft_oracle
from pydantic import ValidationError
from shaft_parity import SHAFTS
from test_din5480 import M_GRID

from spur import din5480, din5480_tables, shaft_calc
from spur.din5480 import Designation, parse_designation
from spur.shaft_calc import (
    FORM_DIAMETER_UNPROVEN,
    MEASURE_AT_NOMINAL_THICKNESS,
    ODD_Z_UNCONFIRMED,
    ROOT_FORM_CONSTRUCTION,
    SHANK_STEP_NO_RELIEF,
    SPLINED_LENGTH_LIMIT,
    THEORETICAL_PIN,
    TOOTH_HEIGHT_LIMIT,
    PinReading,
    ShaftDimensions,
    chamfer_below_resolution_warning,
    chamfer_capped_warning,
    derive_shaft,
    floor_mm,
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


# 34-04, D-04, D-13: with no table file the default shaft prints today's numbers and says
# why the five window rows are null and what the solid carries.
def _no_file_warnings() -> tuple[str, ...]:
    return (FORM_DIAMETER_UNPROVEN, THEORETICAL_PIN, DEFAULT_HOBBED_ROOT_WARNING,
            MEASURE_AT_NOMINAL_THICKNESS, shaft_calc.NO_TABLE_FILE,
            shaft_calc.SOLID_AT_NOMINAL_THICKNESS, ROOT_FORM_CONSTRUCTION, SHANK_STEP_NO_RELIEF)


WINDOW_KEYS = ("max_effective_thickness", "max_actual_thickness", "min_actual_thickness",
               "measure_over_pins_max", "measure_over_pins_min")


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
    assert d.warnings == _no_file_warnings()


def test_the_default_shaft_is_designated_w_25x1_25x18x8f() -> None:
    """The designation is the standard's notation, and the default's parses back to the
    default (D-05): the codec and the parameter model name the same shaft."""
    designation = derive_shaft(ShaftParams()).designation
    assert designation == "W 25x1.25x18x8f"
    assert parse_designation(designation) == Designation(25.0, 1.25, 18, "8f")
    assert ShaftParams(**parse_designation(designation)._asdict()) == ShaftParams()


def test_the_shaft_dimensions_keys_are_fixed() -> None:
    """These keys become Phase 33's dims rows, in this order; renaming or moving one after
    Phase 33 changes the API document. The warnings are the same on every call. The five
    tolerance-window keys sit as one block after `measure_over_pins` (34-04, D-15);
    `end_chamfer_effective` was the 13th key before them (32-01 choice B1, L47)."""
    assert list(ShaftDimensions.model_fields) == [
        "reference_d", "profile_shift", "profile_shift_mm", "pitch_d", "tip_d", "root_d",
        "nominal_thickness", "form_d", "pin_d", "measure_over_pins",
        "max_effective_thickness", "max_actual_thickness", "min_actual_thickness",
        "measure_over_pins_max", "measure_over_pins_min",
        "end_chamfer_effective", "designation", "warnings",
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
    assert d.warnings == _no_file_warnings()
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


def test_an_odd_tooth_count_off_the_tables_prints_the_pin_and_no_measure_over_pins() -> None:
    """W25x1.25x19 with no table file: the pin is given, M_Re is not given while the odd-count
    gate stays off the tables (D-11), and the sentences say both."""
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
                        lambda _p, _pin_d, **_kw: PinReading(None, None, (reason,)))
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


def _chamfer_warnings(d: ShaftDimensions) -> list[str]:
    return [w for w in d.warnings if w.startswith("end_chamfer")]


def test_the_default_shaft_cuts_its_requested_end_chamfer() -> None:
    """D-06: the default W 25x1.25x18x8f asks for 1.0 mm, the tooth height is 1.25 and the
    splined length 30, so nothing binds: the 13th key prints 1.0 and no sentence names it."""
    d = derive_shaft(ShaftParams())
    assert d.end_chamfer_effective == 1.0
    assert _chamfer_warnings(d) == []


def test_a_chamfer_past_the_tooth_height_is_capped_and_warned_naming_the_field_and_the_limit(
) -> None:
    """D-05 (the L29/L45 precedent): W 10x0.5x18 has tooth height 0.5, so the default 1.0 mm
    is cut at 0.5 and the sentence names end_chamfer, the size and the limit; never a 422.
    (D-05's `module=0.5` alone cannot validate: it needs a shift of +15.45.)"""
    d = derive_shaft(ShaftParams(reference_d=10, module=0.5, teeth=18))
    assert d.end_chamfer_effective == 0.5
    assert _chamfer_warnings(d) == [chamfer_capped_warning(1.0, 0.5, (TOOTH_HEIGHT_LIMIT,))]
    sentence = _chamfer_warnings(d)[0]
    assert "end_chamfer" in sentence
    assert "0.5 mm" in sentence
    assert "tooth height" in sentence


@pytest.mark.parametrize(("length", "applied"), [(2.0006, 2.0), (1.0009, 1.0)])
def test_a_chamfer_past_the_splined_length_is_capped_down_never_up(
        length: float, applied: float) -> None:
    """32-RESEARCH Pitfall 3: round(v, 3) would read 2.001 for 2.0006 and 1.001 for 1.0009,
    above the length, and the kernel returned an empty shape that still says isValid() for
    that legal link (32-round-up.log). The floor reads 2.0 and 1.0."""
    p = ShaftParams(reference_d=70, module=3, teeth=22, splined_length=length, end_chamfer=5,
                    shank_length=0)
    d = derive_shaft(p)
    assert d.end_chamfer_effective == applied
    assert d.end_chamfer_effective <= p.splined_length
    assert _chamfer_warnings(d) == [
        chamfer_capped_warning(5.0, applied, (SPLINED_LENGTH_LIMIT,))]
    assert "splined_length" in _chamfer_warnings(d)[0]


def test_a_tie_between_the_two_caps_names_both() -> None:
    """W 70x3x22 has tooth height 3.0; with splined_length 3.0 both caps give 3.0. The
    sentence names tooth height first and is the same on every call."""
    p = ShaftParams(reference_d=70, module=3, teeth=22, splined_length=3.0, end_chamfer=5,
                    shank_length=0)
    d = derive_shaft(p)
    assert d.end_chamfer_effective == 3.0
    assert _chamfer_warnings(d) == [
        chamfer_capped_warning(5.0, 3.0, (TOOTH_HEIGHT_LIMIT, SPLINED_LENGTH_LIMIT))]
    assert _chamfer_warnings(d)[0].index("tooth height") < _chamfer_warnings(d)[0].index(
        "splined_length")
    assert derive_shaft(p).warnings == d.warnings


def test_a_chamfer_below_the_resolution_is_not_cut_and_prints_no_number() -> None:
    """L45, L08: 0.0004 mm floors to 0.000, so nothing is cut and no number is printed in
    place of the cut; the sentence says why."""
    d = derive_shaft(ShaftParams(end_chamfer=0.0004))
    assert d.end_chamfer_effective is None
    assert _chamfer_warnings(d) == [chamfer_below_resolution_warning(0.0004)]
    assert "below the 0.001 mm resolution" in _chamfer_warnings(d)[0]


def test_no_chamfer_asked_prints_no_number_and_no_warning() -> None:
    """end_chamfer 0 means none: null, and no sentence about a chamfer that was not asked."""
    d = derive_shaft(ShaftParams(end_chamfer=0))
    assert d.end_chamfer_effective is None
    assert _chamfer_warnings(d) == []


def test_the_millimetre_floor_keeps_every_typed_decimal() -> None:
    """A1 (32-01): a typed three-place decimal 0..500 keeps itself, and no four-place decimal
    0..50 floors above itself; 32-01-floor-grid.log ran the four-place grid to 500.0000 (0
    above). Without the 1e-9, 2957 three-place decimals lose a step, first 1.001, 1.003,
    1.005. A result above its input is possible only for an input within 1e-9 below a
    lattice point and then by at most 1.03e-12 mm (32-02-overshoot.log, up to 500 mm)."""
    # The first few offenders by name, so a failure says which decimal moved.
    moved = [f"{k / 1000:.3f}" for k in range(500001)
             if floor_mm(float(f"{k / 1000:.3f}")) != float(f"{k / 1000:.3f}")]
    assert moved[:3] == []
    above = [f"{k / 10000:.4f}" for k in range(500001)
             if floor_mm(float(f"{k / 10000:.4f}")) > float(f"{k / 10000:.4f}")]
    assert above[:3] == []


@pytest.mark.parametrize("p", [
    ShaftParams(),
    ShaftParams(shank_length=0),
    ShaftParams(**parse_designation("W 120x3x38x8f")._asdict()),
], ids=["default", "no-shank", "w120x3x38"])
def test_every_shaft_says_its_root_is_a_construction_and_gives_no_number(
        p: ShaftParams) -> None:
    """D-03: the solid's root is a construction, not the cut of a hob or broach. The sentence
    holds no digit, so it cannot imply a fillet radius, and never the word `hobbed`, which
    the root_d sentence's tests use to pick that sentence out."""
    assert ROOT_FORM_CONSTRUCTION in derive_shaft(p).warnings
    assert re.search(r"[0-9]", ROOT_FORM_CONSTRUCTION) is None
    assert "construction" in ROOT_FORM_CONSTRUCTION
    assert "root_d" in ROOT_FORM_CONSTRUCTION
    assert "hobbed" not in ROOT_FORM_CONSTRUCTION
    assert sum("hobbed" in w for w in derive_shaft(p).warnings) == 1


def test_a_shank_brings_the_no_relief_groove_sentence_and_no_shank_drops_it() -> None:
    """D-08: with a shank the spline steps straight into it, with no relief groove (DIN 509),
    no hob run-out and a full-form prism. The sentence gives no notch factor: its only source
    is a low-confidence workshop article. shank_length 0 has no step, so no sentence."""
    with_shank = derive_shaft(ShaftParams())
    assert with_shank.warnings[-1] == SHANK_STEP_NO_RELIEF
    assert "DIN 509" in SHANK_STEP_NO_RELIEF
    assert "full-form prism" in SHANK_STEP_NO_RELIEF
    assert "notch" not in SHANK_STEP_NO_RELIEF
    assert SHANK_STEP_NO_RELIEF not in derive_shaft(ShaftParams(shank_length=0)).warnings


# --- 34-04: the tooth-thickness window and the M_Re limits, with the tables loaded --------------


def _shift_for_thickness(m: float, s: float) -> float:
    """The profile shift whose nominal thickness is `s`: how the oracle is given a limit."""
    return (s - math.pi * m / 2) / (2 * m * math.tan(math.radians(30.0)))


def test_the_thickness_limits_are_table_6_over_table_7() -> None:
    """DIN 5480-1:2006, Table 6: s_vmax = s1 + A_s, s_max = s_vmax - T_eff, s_min = s_vmax - T_G.
    The deviations arrive in micrometres; the planning numbers are the default shaft's."""
    s_vmax, s_max, s_min = din5480.thickness_limits(2.613014, -21, 35, 14)
    assert s_vmax == pytest.approx(2.592014, abs=1e-12)
    assert s_max == pytest.approx(2.578014, abs=1e-12)
    assert s_min == pytest.approx(2.557014, abs=1e-12)
    assert "DIN 5480-1:2006, Table 6" in (din5480.thickness_limits.__doc__ or "")


@pytest.mark.usefixtures("with_tables")
def test_with_the_tables_the_default_shaft_prints_its_window_and_m_re_limits() -> None:
    d = derive_shaft(ShaftParams())
    assert d.nominal_thickness == 2.613
    assert d.max_effective_thickness == 2.592
    assert d.max_actual_thickness == 2.577
    assert d.min_actual_thickness == 2.556
    assert d.pin_d == 2.75                                           # the tabulated D_M
    assert d.measure_over_pins == 28.05                              # computed, not M1 copied
    assert d.measure_over_pins_max == 28.001
    assert d.measure_over_pins_min == 27.973


@pytest.mark.usefixtures("with_tables")
@pytest.mark.parametrize(("which", "thickness", "printed"), [
    ("max", 2.577014, 28.001), ("min", 2.556014, 27.973)], ids=["max", "min"])
def test_each_m_re_limit_agrees_with_the_oracle_at_the_thickness_written_as_the_shift(
        which: Literal["max", "min"], thickness: float, printed: float) -> None:
    p = ShaftParams()
    x = din5480.profile_shift(p.reference_d, p.module, p.teeth)
    s1 = din5480.tooth_thickness(p.module, x * p.module)
    s = {"max": s1 - 0.021 - 0.015, "min": s1 - 0.021 - 0.036}[which]
    assert s == pytest.approx(thickness, abs=1e-6)
    unrounded, warnings = shaft_calc.limit_measurement(p, 2.75, s, which)
    assert warnings == ()
    assert unrounded is not None
    oracle = shaft_oracle.measure(p.module, p.teeth, _shift_for_thickness(p.module, s), 2.75)
    assert unrounded == pytest.approx(oracle, abs=1e-9)
    assert round(unrounded, 3) == printed
    assert abs(printed - oracle) <= 0.0005 + 1e-9                    # the printed half unit


# --- 34-04: the tier matrix (no file, a size the tables do not list, a fit outside Table 7) -----


def _window(d: ShaftDimensions) -> list[float | None]:
    return [getattr(d, k) for k in WINDOW_KEYS]


def test_with_no_file_the_five_rows_are_null_and_the_sentence_names_the_variable_not_a_path(
) -> None:
    d = derive_shaft(ShaftParams())
    assert _window(d) == [None] * 5
    assert (d.pin_d, d.measure_over_pins, d.nominal_thickness) == (2.73, 27.999, 2.613)
    assert "SPUR_DIN5480_TABLES" in shaft_calc.NO_TABLE_FILE
    assert "/" not in shaft_calc.NO_TABLE_FILE
    assert "nominal tooth thickness" in shaft_calc.SOLID_AT_NOMINAL_THICKNESS


@pytest.mark.usefixtures("with_tables")
def test_the_warnings_are_one_fixed_tuple_per_tier() -> None:
    listed = derive_shaft(ShaftParams())
    assert listed.warnings == (FORM_DIAMETER_UNPROVEN, shaft_calc.TABULATED_PIN,
                               DEFAULT_HOBBED_ROOT_WARNING, shaft_calc.MEASURE_LIMITS_AT_FIT,
                               ROOT_FORM_CONSTRUCTION, SHANK_STEP_NO_RELIEF)
    assert MEASURE_AT_NOMINAL_THICKNESS not in listed.warnings
    assert THEORETICAL_PIN not in listed.warnings

    off = ShaftParams(reference_d=30.001, module=2, teeth=14)
    unlisted = derive_shaft(off)
    assert unlisted.warnings[3:5] == (
        MEASURE_AT_NOMINAL_THICKNESS, shaft_calc.size_not_tabulated_warning(off))
    assert unlisted.warnings[0] == FORM_DIAMETER_UNPROVEN
    assert unlisted.warnings[1] == THEORETICAL_PIN
    assert unlisted.warnings[5:] == (shaft_calc.SOLID_AT_NOMINAL_THICKNESS,
                                     ROOT_FORM_CONSTRUCTION, SHANK_STEP_NO_RELIEF)

    wrong_fit = derive_shaft(ShaftParams(fit="3z"))
    assert wrong_fit.warnings == (
        FORM_DIAMETER_UNPROVEN, shaft_calc.TABULATED_PIN, DEFAULT_HOBBED_ROOT_WARNING,
        MEASURE_AT_NOMINAL_THICKNESS,
        shaft_calc.fit_not_in_table_7_warning("3z", ("f", "h", "k"), (7, 8, 9)),
        shaft_calc.SOLID_AT_NOMINAL_THICKNESS, ROOT_FORM_CONSTRUCTION, SHANK_STEP_NO_RELIEF)


@pytest.mark.usefixtures("with_tables")
def test_the_size_sentence_prints_a_nudged_diameter_in_full_and_takes_no_nearest_row() -> None:
    p = ShaftParams(reference_d=30.001, module=2, teeth=14)
    sentence = shaft_calc.size_not_tabulated_warning(p)
    assert "W 30.001x2x14" in sentence
    assert "nearest" in sentence
    assert "interpolate" in sentence
    assert _window(derive_shaft(p)) == [None] * 5


@pytest.mark.parametrize("fit", ["3z", "13f", "8q"])
def test_a_fit_outside_table_7_names_the_files_letters_and_classes_and_nulls_the_window(
        fit: str, with_tables: din5480_tables.Tables) -> None:
    d = derive_shaft(ShaftParams(fit=fit))
    sentence = shaft_calc.fit_not_in_table_7_warning(
        fit, with_tables.letters, with_tables.tolerance_classes)
    assert sentence in d.warnings
    assert f"fit {fit}" in sentence
    assert "f, h and k" in sentence                       # the fixture's invented letters
    assert "7, 8 and 9" in sentence                       # the fixture's invented classes
    assert _window(d) == [None] * 5
    assert (d.pin_d, d.measure_over_pins) == (2.75, 28.05)  # tier 3 still prints the D_M pin
    assert shaft_calc.SOLID_AT_NOMINAL_THICKNESS in d.warnings


@pytest.mark.usefixtures("with_tables")
def test_off_table_neighbours_read_as_off_the_tables_field_for_field() -> None:
    """A d_B 0.001 above a listed row, a module step and a tooth step, each feasible, print
    the no-file document's numbers: no nearest row is taken (L08, T-34-14)."""
    neighbours = [
        ShaftParams(reference_d=30.001, module=2, teeth=14),
        ShaftParams(reference_d=25, module=1.3, teeth=18),
        ShaftParams(reference_d=25, module=1.25, teeth=19),
    ]
    assert len(neighbours) == 3
    for p in neighbours:
        with_file = derive_shaft(p)
        din5480_tables.install(None)
        try:
            without_file = derive_shaft(p)
        finally:
            din5480_tables.install(din5480_tables_fixture.build())
        numbers = {k: v for k, v in with_file.model_dump().items() if k != "warnings"}
        assert numbers == {k: v for k, v in without_file.model_dump().items() if k != "warnings"}
        assert shaft_calc.NO_TABLE_FILE in without_file.warnings
        assert shaft_calc.size_not_tabulated_warning(p) in with_file.warnings
        assert shaft_calc.NO_TABLE_FILE not in with_file.warnings


def test_a_size_is_on_the_tables_only_by_an_exact_key(
        with_tables: din5480_tables.Tables) -> None:
    assert with_tables.size(1.25, 25, 18) is with_tables.size(1.25, 25.0, 18)
    assert with_tables.size(1.25, 25, 18) is not None
    assert with_tables.size(1.25, 25.000001, 18) is None


@pytest.mark.usefixtures("with_tables")
def test_each_thickness_row_is_rounded_once_from_the_unrounded_sum() -> None:
    """Pitfall 8: the rows are round(s1 + A_s [- T], 3) of the unrounded s1, never of the
    rounded nominal row (2.613) plus micrometres: W 30x2x14 prints 3.009, 2.991 and 2.964."""
    d = derive_shaft(ShaftParams(reference_d=30, module=2, teeth=14))
    assert (d.max_effective_thickness, d.max_actual_thickness, d.min_actual_thickness) == (
        3.009, 2.991, 2.964)
    assert d.pin_d == 4.0
    assert (d.measure_over_pins_max, d.measure_over_pins_min) == (34.093, 34.053)


@pytest.mark.usefixtures("with_tables")
def test_a_limit_outside_the_contact_window_is_null_with_its_own_sentence_and_the_other_prints(
) -> None:
    """Direct calls (34-RESEARCH Pitfall 6): the pin that sits inside the window at one
    thickness can leave it at another; each limit is guarded alone."""
    p = ShaftParams()
    low, high = shaft_calc.pin_contact_window(p)
    s = 2.577014
    inside = shaft_calc.limit_measurement(p, 2.75, s, "max")
    assert inside.measure is not None
    assert inside.warnings == ()
    outside = shaft_calc.limit_measurement(p, 5.0, s, "min")
    assert outside.measure is None
    assert len(outside.warnings) == 1
    assert outside.warnings[0].startswith("M_Re min is not given")
    assert f"{low:.3f} to {high:.3f}" in outside.warnings[0]
    assert "s_min" in outside.warnings[0]


def test_a_pin_that_misses_the_flanks_at_a_limit_thickness_is_null_with_its_own_sentence() -> None:
    """A direct call, as the analog's: a pin that touches at the nominal thickness can miss the
    flanks altogether at a thinner limit. 0.1 mm is a pin `measure_over_pins` answers None for
    on this shaft at s = 2.577014 (checked at plan time), and that is a different sentence from
    the window's: there is no contact diameter to quote."""
    p = ShaftParams()
    reading = shaft_calc.limit_measurement(p, 0.1, 2.577014, "min")
    assert reading.measure is None
    assert len(reading.warnings) == 1
    assert reading.warnings[0].startswith(
        "M_Re min is not given: a pin of 0.1 mm does not touch the involute flanks")
    assert "s_min" in reading.warnings[0]


# --- 34-06: the guard starts at the tabulated d_Ff1 maximum (D-12) -----------------------

# Part 1 Fig. 6: W 120x3x38x8f, d_Ff1 max 113.91 (approved). The fixture's other rows carry
# invented maxima and are not anchors, so no claim about the bound's place is made for them.
APPROVED_FORM_D_MAX = {(3.0, 120.0, 38): 113.91}


def test_for_a_listed_size_the_guard_starts_at_the_tabulated_form_diameter_maximum(
        with_tables: din5480_tables.Tables) -> None:
    p = ShaftParams(reference_d=120, module=3, teeth=38)
    margin = shaft_calc.GUARD_MARGIN_FACTOR * p.module
    assert pin_contact_window(p, 113.91)[0] == pytest.approx(113.91 + 0.1 * 3, abs=1e-12)
    # No maximum: the internal construction plus the margin, as before (planning 114.1802).
    assert pin_contact_window(p)[0] == pytest.approx(114.1802, abs=1e-4)
    assert pin_contact_window(p, 113.91)[1] == pin_contact_window(p)[1]
    anchors = [r for r in with_tables.sizes
               if (r.module, r.reference_d, r.teeth) in APPROVED_FORM_D_MAX]
    assert len(anchors) == len(APPROVED_FORM_D_MAX)
    for row in anchors:
        row_p = ShaftParams(reference_d=row.reference_d, module=row.module, teeth=row.teeth)
        floor = pin_contact_window(row_p, row.form_d_max_mm)[0]
        assert floor - margin == pytest.approx(
            APPROVED_FORM_D_MAX[(row.module, row.reference_d, row.teeth)], abs=1e-12)


def test_the_tabulated_floor_is_closed() -> None:
    """The default shaft with a d_Ff1 maximum of 23.46: the floor is 23.585. The pin touching
    exactly there is found by bisection, then moved 1e-6 mm either way, as for the internal
    floor in test_the_pin_contact_window_is_closed."""
    p = ShaftParams()
    m, z = p.module, p.teeth
    s = din5480.tooth_thickness(m, din5480.profile_shift(p.reference_d, m, z) * m)

    def contact(pin: float) -> float:
        result = din5480.measure_over_pins(m, z, s, pin)
        assert result is not None
        return result[1]

    low, _ = pin_contact_window(p, 23.46)
    assert low == pytest.approx(23.585, abs=1e-12)
    lo, hi = 1.0, 5.0
    for _ in range(100):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if contact(mid) < low else (lo, mid)
    at_floor = 0.5 * (lo + hi)
    assert 0 < contact(at_floor + 1e-6) - low < 1e-5
    assert 0 < low - contact(at_floor - 1e-6) < 1e-5
    assert pin_measurement(p, at_floor + 1e-6, form_d_max=23.46).measure is not None
    below = pin_measurement(p, at_floor - 1e-6, form_d_max=23.46)
    assert below.measure is None
    assert below.pin_d is None
    assert below.warnings[0].startswith("M_Re and D_Re not given")
    # The same pin is inside the internal window, which sits lower for this row.
    assert pin_measurement(p, at_floor - 1e-6).measure is not None


def _install_default_row_with_form_d_max(form_d_max: float) -> None:
    document = json.loads(din5480_tables_fixture.text())
    rows = [r for r in document["sizes"]
            if (r["module"], r["reference_d"], r["teeth"]) == (1.25, 25.0, 18)]
    assert len(rows) == 1
    rows[0]["form_d_max_mm"] = form_d_max
    din5480_tables.install(din5480_tables.parse(json.dumps(document)))


@pytest.mark.usefixtures("with_tables")
def test_a_limit_thickness_below_the_floor_nulls_that_limit_only() -> None:
    """Pitfall 6, planning measurement 2026-10-30: the default row's contacts at pin 2.75 are
    23.6411 (nominal), 23.5977 (s_max) and 23.5723 (s_min). A d_Ff1 maximum of 23.46 puts the
    floor at 23.585, between the last two: M_Re and M_Re max print, M_Re min alone is null."""
    _install_default_row_with_form_d_max(23.46)
    d = derive_shaft(ShaftParams())
    assert (d.pin_d, d.measure_over_pins) == (2.75, 28.05)
    assert d.measure_over_pins_max == 28.001
    assert d.measure_over_pins_min is None
    sentences = [w for w in d.warnings if w.startswith(("M_Re max", "M_Re min"))]
    assert len(sentences) == 1
    assert sentences[0].startswith(
        "M_Re min is not given: a pin of 2.75 mm at the tooth thickness s_min")
    assert "23.572 mm, outside the window 23.585 to " in sentences[0]
    assert shaft_calc.MEASURE_LIMITS_AT_FIT in d.warnings
    # The window rows are the fit's, whatever the pin does.
    assert (d.max_effective_thickness, d.max_actual_thickness, d.min_actual_thickness) == (
        2.592, 2.577, 2.556)


@pytest.mark.usefixtures("with_tables")
def test_each_branch_of_the_floor_is_reached_by_its_own_thickness() -> None:
    """Floor 23.625 sits between the nominal and the s_max contact: M_Re prints, both limits
    are null with a sentence each. Floor 23.655 is above all three: no pin, no limits, and the
    pin's own sentence alone."""
    _install_default_row_with_form_d_max(23.50)
    d = derive_shaft(ShaftParams())
    assert (d.pin_d, d.measure_over_pins) == (2.75, 28.05)
    assert (d.measure_over_pins_max, d.measure_over_pins_min) == (None, None)
    sentences = [w for w in d.warnings if w.startswith(("M_Re max", "M_Re min"))]
    assert len(sentences) == 2
    assert sentences[0].startswith("M_Re max is not given")
    assert sentences[1].startswith("M_Re min is not given")
    assert shaft_calc.MEASURE_AT_NOMINAL_THICKNESS in d.warnings

    _install_default_row_with_form_d_max(23.53)
    d = derive_shaft(ShaftParams())
    assert (d.pin_d, d.measure_over_pins) == (None, None)
    assert (d.measure_over_pins_max, d.measure_over_pins_min) == (None, None)
    assert [w for w in d.warnings if w.startswith("M_Re")] == [
        next(w for w in d.warnings if w.startswith("M_Re and D_Re not given"))]
    assert shaft_calc.TABULATED_PIN not in d.warnings


# --- 34-06: an odd tooth count prints where the tables list it (D-11) --------------------------


@pytest.mark.usefixtures("with_tables")
def test_a_listed_odd_tooth_count_prints_m_re_at_the_tabulated_pin() -> None:
    """W 26x1.25x19x8f, column 2, A_s -17 (planning measurement 2026-10-30): at the tabulated
    pin 2.75 M_Re is 29.026, the approved M1 of DIN 5480-2 Tables 12 and 13, and the limits
    follow at s_max and s_min."""
    d = derive_shaft(ShaftParams(reference_d=26, module=1.25, teeth=19))
    assert d.pin_d == 2.75
    assert d.measure_over_pins == pytest.approx(29.026, abs=0.0005)
    assert (d.measure_over_pins, d.measure_over_pins_max, d.measure_over_pins_min) == (
        29.026, 28.978, 28.94)
    assert ODD_Z_UNCONFIRMED not in d.warnings
    assert shaft_calc.TABULATED_PIN in d.warnings
    assert shaft_calc.MEASURE_LIMITS_AT_FIT in d.warnings
    assert not [w for w in d.warnings if w.startswith(("M_Re max", "M_Re min"))]


@pytest.mark.usefixtures("with_tables")
def test_an_odd_tooth_count_the_tables_do_not_list_stays_null_with_its_sentence() -> None:
    """W 25x1.25x19 is feasible and not in the fixture: the gate stays (D-11, T-34-23)."""
    p = ShaftParams(reference_d=25, module=1.25, teeth=19)
    d = derive_shaft(p)
    assert d.pin_d == 2.36                                  # the theoretical pin
    assert (d.measure_over_pins, d.measure_over_pins_max, d.measure_over_pins_min) == (
        None, None, None)
    assert ODD_Z_UNCONFIRMED in d.warnings
    assert shaft_calc.size_not_tabulated_warning(p) in d.warnings


def test_no_warning_carries_the_table_files_path(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """T-34-15: warnings reach every API client, so the variable's name is the reference."""
    path = din5480_tables_fixture.write(tmp_path / "tables.json")
    monkeypatch.setenv(din5480_tables.ENV_VAR, str(path))
    din5480_tables.reset()
    shafts = [ShaftParams.model_validate(v) for v in SHAFTS.values()]
    shafts += [ShaftParams(fit="3z"), ShaftParams(reference_d=30.001, module=2, teeth=14)]
    for p in shafts:
        d = derive_shaft(p)
        assert not any(str(tmp_path) in w or str(path) in w for w in d.warnings)
    assert derive_shaft(ShaftParams()).max_effective_thickness == 2.592   # the file was read
