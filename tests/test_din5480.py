"""din5480's formulas against the independent oracle and the vendor reports.

The oracle is tests/shaft_oracle.py: the basic rack and a parametric involute, no code
shared with src/spur/din5480.py (L08). The vendors are cross-checks, not the standard
(D-08); anchor rows from the copy arrive in 31-06, in their own file.
"""

import ast
import copy
import itertools
import math
import pickle
from pathlib import Path

import pytest
import shaft_oracle

from spur import din5480

# 6 modules x 8 tooth counts x 4 shifts. No shift is zero: the thickness has a term in
# x*m*tan(alpha) that a zero shift hides, so the grid carries shifts away from it.
GRID: list[tuple[float, int, float]] = list(
    itertools.product(
        (0.5, 0.8, 1.25, 2, 3, 10),
        (6, 7, 14, 18, 19, 22, 38, 82),
        (-0.05, 0.1, 0.25, 0.45),
    )
)
# 4 modules x 6 tooth counts x 3 shifts = 72 pin cases; both parities, the smallest and the
# largest count, and the whole shift range. Each oracle call is a tangency search (about
# 8 ms), so the sweep stays in the low hundreds (31-RESEARCH Pitfall 10).
M_GRID: list[tuple[float, int, float]] = list(
    itertools.product((0.5, 1.25, 3, 10), (6, 7, 18, 19, 38, 82), (-0.05, 0.2, 0.45))
)
# Worst contact-diameter disagreement over M_GRID, din5480 against the oracle: 5.14e-7 mm
# at the rounded pin and 6.97e-7 mm at the unrounded theoretical pin (the oracle's golden
# section finds the touching point to about the square root of machine epsilon). 2e-6
# leaves a factor of 2.9 over the larger; the measure itself agrees to 2.3e-13, so it keeps
# 1e-9.
CONTACT_ABS = 2e-6
H_FP_BOTH = (0.55, 0.60)  # the provisional value and hobbing's, so both stay covered

# Vendor cross-check, not the standard (D-08): KISSsoft report 12 Spline (DIN 5480),
# W 70.00x3.00x22x6f, https://www.kadkraft.com/wp-content/uploads/2022/11/12-Spline-DIN-5480.pdf
# Read: reference 70.00, [x*m] 0.3501, [da] 69.400, [df] 63.100 with the profile line
# 0.60 / 0.16 / 0.45 Hobbing, so this row runs at h_fP 0.60.
KISSSOFT_W70: dict[str, float] = {
    "reference_d": 70.00,
    "m": 3.0,
    "z": 22,
    "h_fp": 0.60,
    "xm": 0.3501,
    "d_a": 69.400,
    "d_f": 63.100,
}

# Vendor cross-check, not the standard (D-08): Hexagon WN2 brochure, page 2 (an embedded
# image), https://www.hexagon.de/pdf/wn2_d.pdf, W 120 x 3 x 38 x 8f.
# Read: hfp/m 0.55, da1 119,40, df1 113,40, evmin = e2 = s1 = 6,271 (the nominal thickness).
HEXAGON_W120: dict[str, float] = {
    "reference_d": 120.0,
    "m": 3.0,
    "z": 38,
    "h_fp": 0.55,
    "s": 6.271,
    "d_a": 119.40,
    "d_f": 113.40,
}


def _case_id(case: tuple[float, int, float]) -> str:
    m, z, x = case
    return f"m{m}-z{z}-x{x}"


def test_the_shaft_oracle_imports_nothing_from_spur() -> None:
    """The oracle's value is that it computes by another road, so it may import only the
    standard library maths and the future annotations marker."""
    tree = ast.parse((Path(__file__).parent / "shaft_oracle.py").read_text())
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            imported.add(node.module)
    assert imported <= {"__future__", "math"}


@pytest.mark.parametrize("case", GRID, ids=_case_id)
def test_the_shift_inverts_the_oracle_reference_diameter(
    case: tuple[float, int, float],
) -> None:
    m, z, x = case
    reference_d = shaft_oracle.reference_diameter(m, z, x)
    assert din5480.profile_shift(reference_d, m, z) == pytest.approx(x, abs=1e-9)


@pytest.mark.parametrize("case", GRID, ids=_case_id)
def test_the_basic_dims_agree_with_the_oracle(case: tuple[float, int, float]) -> None:
    m, z, x = case
    reference_d = shaft_oracle.reference_diameter(m, z, x)
    assert din5480.tip_diameter(reference_d, m) == pytest.approx(
        shaft_oracle.tip_diameter(m, z, x), abs=1e-9
    )
    for h_fp in H_FP_BOTH:
        assert din5480.root_diameter(m, z, x * m, h_fp) == pytest.approx(
            shaft_oracle.root_diameter(m, z, x, h_fp), abs=1e-9
        )
    assert din5480.tooth_thickness(m, x * m) == pytest.approx(
        shaft_oracle.tooth_thickness(m, z, x), abs=1e-9
    )


@pytest.mark.parametrize("case", GRID, ids=_case_id)
def test_the_basic_dims_order_root_below_pitch_below_tip(
    case: tuple[float, int, float],
) -> None:
    """The root circle never touches the pitch circle and the tip never falls inside it."""
    m, z, x = case
    reference_d = shaft_oracle.reference_diameter(m, z, x)
    tip = din5480.tip_diameter(reference_d, m)
    for h_fp in H_FP_BOTH:
        assert din5480.root_diameter(m, z, x * m, h_fp) < m * z < tip


def test_the_shift_term_is_the_addendum_plus_half_the_tip_offset(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """SHIFT_TERM and H_FP read alike at 0.55 and are different quantities: the copy's
    h_fP, likely 0.60 for hobbing, must never move the shift (31-RESEARCH Pitfall 1)."""
    assert din5480.SHIFT_TERM == 0.55
    assert din5480.ADDENDUM_FACTOR == 0.45
    assert din5480.TIP_DIAMETER_OFFSET == 0.2
    before = din5480.profile_shift(25.0, 1.25, 18)
    monkeypatch.setattr(din5480, "H_FP", 0.60)
    assert din5480.SHIFT_TERM == 0.55
    assert din5480.profile_shift(25.0, 1.25, 18) == before


def test_the_basic_dims_match_the_vendor_cross_checks() -> None:
    """Vendor cross-checks, not the standard: each is compared at its own print precision,
    and the oracle's 1e-9 is never loosened to meet a vendor."""
    k = KISSSOFT_W70
    k_m, k_z = k["m"], int(k["z"])
    k_x = din5480.profile_shift(k["reference_d"], k_m, k_z)
    assert din5480.tip_diameter(k["reference_d"], k_m) == pytest.approx(k["d_a"], abs=5e-4)
    assert din5480.root_diameter(k_m, k_z, k_x * k_m, k["h_fp"]) == pytest.approx(
        k["d_f"], abs=5e-4
    )
    # The formula gives x*m = 0.35 exactly. KISSsoft prints 0.3501 because it rounds x to
    # 0.1167 before multiplying by m (31-RESEARCH Pitfall 7), a 1e-4 print artefact.
    assert k_x * k_m == pytest.approx(k["xm"], abs=2e-4)

    h = HEXAGON_W120
    h_m, h_z = h["m"], int(h["z"])
    h_x = din5480.profile_shift(h["reference_d"], h_m, h_z)
    assert din5480.tip_diameter(h["reference_d"], h_m) == pytest.approx(h["d_a"], abs=5e-3)
    assert din5480.root_diameter(h_m, h_z, h_x * h_m, h["h_fp"]) == pytest.approx(
        h["d_f"], abs=5e-3
    )
    assert din5480.tooth_thickness(h_m, h_x * h_m) == pytest.approx(h["s"], abs=5e-4)


def test_the_oracle_refuses_a_mutated_shift_term() -> None:
    """A shift term of 0.5 in place of 0.55 moves x by 0.05 on every grid case."""
    for m, z, x in GRID:
        reference_d = shaft_oracle.reference_diameter(m, z, x)
        mutated = (reference_d - z * m) / (2 * m) - 0.5
        assert abs(mutated - x) > 1e-3


def test_the_oracle_refuses_a_mutated_thickness() -> None:
    """A thickness built with sin in place of tan disagrees with the oracle somewhere.

    The two differ by 2*xm*(tan - sin), so every x = 0 case agrees and cannot see this
    mutation. That is why the grid carries shifts away from zero.
    """

    def with_sin(m: float, xm: float) -> float:
        return math.pi * m / 2 + 2 * xm * math.sin(din5480.ALPHA)

    assert with_sin(2.0, 0.0) == pytest.approx(
        shaft_oracle.tooth_thickness(2.0, 18, 0.0), abs=1e-9
    )
    assert any(
        abs(with_sin(m, x * m) - shaft_oracle.tooth_thickness(m, z, x)) > 1e-3
        for m, z, x in GRID
    )


def _m_case(case: tuple[float, int, float]) -> tuple[float, int, float, float, float]:
    """(m, z, x, thickness s, rounded theoretical pin) of one M_GRID case."""
    m, z, x = case
    xm = x * m
    pin = round(din5480.theoretical_pin_diameter(m, z, xm), 2)
    return m, z, x, din5480.tooth_thickness(m, xm), pin


@pytest.mark.parametrize("case", M_GRID, ids=_case_id)
def test_the_measure_over_pins_agrees_with_the_oracle_for_even_and_odd_teeth(
    case: tuple[float, int, float],
) -> None:
    m, z, x, s, pin = _m_case(case)
    result = din5480.measure_over_pins(m, z, s, pin)
    assert result is not None
    measure, contact = result
    assert measure == pytest.approx(shaft_oracle.measure(m, z, x, pin), abs=1e-9)
    assert contact == pytest.approx(
        shaft_oracle.contact_diameter(m, z, x, pin), abs=CONTACT_ABS
    )


@pytest.mark.parametrize("case", M_GRID, ids=_case_id)
def test_the_theoretical_pin_touches_on_the_shifted_reference_circle(
    case: tuple[float, int, float],
) -> None:
    m, z, x = case
    pin = din5480.theoretical_pin_diameter(m, z, x * m)
    assert shaft_oracle.contact_diameter(m, z, x, pin) == pytest.approx(
        m * z + 2 * x * m, abs=CONTACT_ABS
    )


def test_the_measure_over_pins_matches_the_vendor_cross_checks() -> None:
    # Vendor cross-check, not the standard (D-08): Hexagon WN2 brochure, page 2,
    # https://www.hexagon.de/pdf/wn2_d.pdf, W 120x3x38x8f, pin 6.000. The M values are at the
    # vendor's actual thicknesses 6.220 and 6.180, not the nominal 6.271 (31-RESEARCH
    # Pitfall 7), so the thickness is passed in; compared at the print precision.
    for s, printed in ((6.220, 126.017), (6.180, 125.956)):
        result = din5480.measure_over_pins(3.0, 38, s, 6.000)
        assert result is not None
        assert result[0] == pytest.approx(printed, abs=5e-4)

    # Vendor cross-check, not the standard (D-08): KISSsoft report 12 Spline (DIN 5480),
    # W 70x3x22x6f, https://www.kadkraft.com/wp-content/uploads/2022/11/12-Spline-DIN-5480.pdf
    # Theoretical pin 5.8253, effective pin 6.0000, M 76.1835. KISSsoft prints x*m 0.3501
    # where the formula gives 0.35 (it rounds x first), so M at xm 0.35 is 76.18337, 1.3e-4
    # below the print, and xm 0.3501 gives 76.18354. The first is compared at abs 2e-4.
    assert din5480.theoretical_pin_diameter(3.0, 22, 0.35) == pytest.approx(5.8253, abs=1e-4)
    result = din5480.measure_over_pins(3.0, 22, din5480.tooth_thickness(3.0, 0.35), 6.000)
    assert result is not None
    assert result[0] == pytest.approx(76.1835, abs=2e-4)
    result = din5480.measure_over_pins(3.0, 22, din5480.tooth_thickness(3.0, 0.3501), 6.000)
    assert result is not None
    assert result[0] == pytest.approx(76.18354, abs=1e-5)


def test_a_pin_that_cannot_touch_the_involute_has_no_measure() -> None:
    """The default shaft's pin, undersize and then just over what its space allows."""
    m, z, xm = 1.25, 18, 0.5625
    s = din5480.tooth_thickness(m, xm)
    d = m * z
    assert din5480.measure_over_pins(m, z, s, 0.01) is None  # no root: target below zero
    # With eta = -(s/d + inv(a) - pi/z), a pin d_b*eta fits the space exactly at the base
    # circle; one more 1e-12 gives a root whose tangent point is at or below it.
    eta = -(s / d + din5480.inv(din5480.ALPHA) - math.pi / z)
    pin = d * math.cos(din5480.ALPHA) * (eta + 1e-12)
    assert din5480.measure_over_pins(m, z, s, pin) is None
    assert din5480.measure_over_pins(m, z, s, 2.73) is not None


def test_the_internal_form_diameter_agrees_with_the_oracle_and_the_vendors() -> None:
    for m, z, x in M_GRID:
        for h_fp in H_FP_BOTH:
            assert din5480.form_diameter(m, z, x * m, h_fp, 0.16) == pytest.approx(
                shaft_oracle.form_diameter(m, z, x, h_fp, 0.16), abs=1e-9
            )
    # Vendor cross-check, not the standard (D-08): KISSsoft report 12 Spline (DIN 5480),
    # https://www.kadkraft.com/wp-content/uploads/2022/11/12-Spline-DIN-5480.pdf: dFf 63.718
    # "calculated on the basis of the constructed involute" at h_fP 0.60, W 70x3x22.
    assert din5480.form_diameter(3.0, 22, 0.35, 0.60, 0.16) == pytest.approx(63.718, abs=5e-4)
    # Hexagon WN2, https://www.hexagon.de/pdf/wn2_d.pdf, W 120x3x38x8f prints dFf 113.91 max,
    # a limit. The public construction gives 113.880, 0.030 mm below it; that gap sized the
    # guard's margin (D-12, GUARD_MARGIN_FACTOR). It is recorded, never asserted equal.
    gap = 113.91 - din5480.form_diameter(3.0, 38, 1.35, 0.55, 0.16)
    assert gap == pytest.approx(0.030, abs=1e-3)


def test_the_oracle_refuses_a_mutated_odd_z_factor() -> None:
    """The even formula applied to an odd count (no cos(pi/(2z)) on the centre distance)
    disagrees with the oracle by more than 1e-3 mm on every odd grid case."""
    odd = [case for case in M_GRID if case[1] % 2]
    assert odd
    for case in odd:
        m, z, x, s, pin = _m_case(case)
        result = din5480.measure_over_pins(m, z, s, pin)
        assert result is not None
        even_formula = (result[0] - pin) / math.cos(math.pi / (2 * z)) + pin
        assert abs(even_formula - shaft_oracle.measure(m, z, x, pin)) > 1e-3


# (id, text, the token the refusal names). Non-ASCII rows are written as escapes so the
# file shows which character is meant: a no-break space is not a space.
REFUSED_DESIGNATIONS: list[tuple[str, str, str]] = [
    ("empty", "", ""),
    ("only-w", "W", ""),
    ("w-and-space", "W ", ""),
    ("empty-fit", "W 25x1.25x18x", ""),
    ("hub-n", "N 25x1.25x18x8f", "N"),
    ("din-prefix", "DIN 5480 W 25x1.25x18x8f", "DIN"),
    ("lower-case-w", "w 25x1.25x18x8f", "w"),
    ("spaced-catalogue-form", "W 25 x 1,25 x 18 x 8f", "25 "),
    ("double-space-after-w", "W  25x1.25x18x8f", " 25"),
    ("multiplication-sign", "W 25\u00d71.25\u00d718\u00d78f", "25\u00d71.25\u00d718\u00d78f"),
    ("full-width-x", "W 25\uff581.25\uff5818\uff588f", "25\uff581.25\uff5818\uff588f"),
    ("no-break-space-after-w", "W\u00a025x1.25x18x8f", "\u00a025"),
    ("fractional-teeth", "W 25x1.25x18.5x8f", "18.5"),
    ("upper-case-fit", "W 25x1.25x18x8F", "8F"),
    ("iso-spelling", "W 25x1.25x18xf8", "f8"),
    ("arabic-indic-digit", "W \u06625x1.25x18x8f", "\u06625"),
    ("trailing-newline", "W 25x1.25x18x8f\n", "8f\n"),
    ("trailing-space", "W 25x1.25x18x8f ", "8f "),
    ("inf", "W infx1.25x18x8f", "inf"),
    ("exponent", "W 1e3x1.25x18x8f", "1e3"),
    ("underscore", "W 2_5x1.25x18x8f", "2_5"),
    ("lone-decimal-mark", "W 25.x1.25x18x8f", "25."),
    ("leading-decimal-mark", "W 25x.5x18x8f", ".5"),
    ("extra-token", "W 25x1.25x18x8fx9", "8fx9"),
    ("three-tokens", "W 25x1.25x18", "25x1.25x18"),
    # One spelling per shaft: a leading zero is refused in every token, as `08f` is in the fit
    # (31-REVIEW WR-05). The integer part 0 of 0.5 is not a leading zero.
    ("leading-zeros-reference-d", "W 0025x1.25x18x8f", "0025"),
    ("leading-zero-module", "W 25x01.25x18x8f", "01.25"),
    ("leading-zeros-before-the-point", "W 25x00.5x18x8f", "00.5"),
    ("leading-zeros-teeth", "W 25x1.25x018x8f", "018"),
    ("zero-teeth", "W 25x1.25x0x8f", "0"),
    ("leading-zero-fit", "W 25x1.25x18x08f", "08f"),
]
ROUND_TRIPS: list[tuple[float, float, int, str]] = [
    (25.0, 1.25, 18, "8f"),
    (30.0, 2.0, 14, "9h"),
    (17.6, 0.8, 20, "10f"),
    (120.0, 3.0, 38, "8f"),
    (70.0, 3.0, 22, "6f"),
    (25.123456, 0.75, 31, "7e"),  # `:g` would print 25.1235 and lose this one
    (835.0, 10.0, 82, "11a"),
    (3.75, 0.5, 6, "8f"),
]


def test_the_designation_prints_in_one_canonical_form() -> None:
    assert din5480.format_designation(25.0, 1.25, 18, "8f") == "W 25x1.25x18x8f"
    assert din5480.format_designation(30.0, 2.0, 14, "9h") == "W 30x2x14x9h"
    assert din5480.format_designation(17.6, 0.8, 20, "10f") == "W 17.6x0.8x20x10f"


@pytest.mark.parametrize(
    "text",
    ["W25x1.25x18x8f", "W 25X1.25X18X8f", "W 25x1,25x18x8f", "W25X1,25X18X8f",
     "W 25.0x1.250x18x8f"],  # trailing zeros after the point are the same number
)
def test_the_designation_parser_accepts_the_listed_variants(text: str) -> None:
    """D-05's variants: no space after W, an upper-case X, a comma for the decimal mark; and
    trailing zeros after the point."""
    assert din5480.parse_designation(text) == din5480.Designation(25.0, 1.25, 18, "8f")


def test_the_designation_parser_accepts_a_module_below_one_with_its_zero_integer_part() -> None:
    """ShaftParams allows module 0.5, so `0.5` is the canonical spelling, not a leading zero."""
    assert din5480.parse_designation("W 3.75x0.5x6x8f") == din5480.Designation(3.75, 0.5, 6, "8f")


@pytest.mark.parametrize("values", ROUND_TRIPS, ids=lambda v: din5480.format_designation(*v))
def test_the_designation_round_trips(values: tuple[float, float, int, str]) -> None:
    assert din5480.parse_designation(din5480.format_designation(*values)) == values


@pytest.mark.parametrize(
    ("text", "token"),
    [pytest.param(text, token, id=name) for name, text, token in REFUSED_DESIGNATIONS],
)
def test_an_unparseable_designation_is_refused_naming_its_token(text: str, token: str) -> None:
    """Nothing is repaired (D-21): each refusal names the token it stopped at, and a Phase 33
    422 reads that token from the exception, not from its message."""
    with pytest.raises(din5480.DesignationError) as raised:
        din5480.parse_designation(text)
    assert isinstance(raised.value, ValueError)
    assert raised.value.token == token
    if token:
        assert repr(token) in str(raised.value)
    # The worker pool ships exceptions between processes and frameworks copy them: the clone
    # must be a DesignationError with the same token and message, not a TypeError.
    for clone in (pickle.loads(pickle.dumps(raised.value)), copy.copy(raised.value),
                  copy.deepcopy(raised.value)):
        assert isinstance(clone, din5480.DesignationError)
        assert clone.token == token
        assert str(clone) == str(raised.value)


def test_a_designation_longer_than_the_bound_is_refused_before_parsing() -> None:
    """The bound is checked first, so no regex sees more than 64 characters. 65 characters
    that would otherwise parse are refused with a message that does not echo them."""
    too_long = "W 25." + "0" * 48 + "1x1.25x18x8f"
    assert len(too_long) == din5480.DESIGNATION_MAX_LENGTH + 1
    with pytest.raises(din5480.DesignationError) as raised:
        din5480.parse_designation(too_long)
    assert raised.value.token == too_long[: din5480.DESIGNATION_MAX_LENGTH]
    assert too_long not in str(raised.value)
    assert "start with" not in str(raised.value)
    at_bound = "W 25." + "0" * 47 + "1x1.25x18x8f"
    assert len(at_bound) == din5480.DESIGNATION_MAX_LENGTH
    assert din5480.parse_designation(at_bound).teeth == 18
