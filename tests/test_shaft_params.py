"""The shaft's frozen link contract (L46, D-01..D-04) and its one validation boundary.

Names read as requirements. `ShaftParams.model_fields` is read at class level only: the
instance accessor is deprecated in pydantic 2.11 and `filterwarnings = ["error"]` is on
(tests/test_calc.py notes the same).
"""

import math
import re

import pytest
from pydantic import ValidationError

from spur import din5480
from spur.din5480 import X_MAX, X_MIN
from spur.shaft_params import ShaftParams

FLOAT_FIELDS = ("reference_d", "module", "splined_length", "end_chamfer", "shank_d",
                "shank_length")
ALL_FIELDS = ("reference_d", "module", "teeth", "fit", "splined_length", "end_chamfer",
              "shank_d", "shank_length")


def _errors(**kw: object) -> list[dict[str, object]]:
    """The pydantic errors for `kw`, or an empty list when it validates."""
    try:
        ShaftParams.model_validate(kw)
    except ValidationError as exc:
        return [dict(e) for e in exc.errors()]
    return []


def test_the_shaft_field_names_and_defaults_are_frozen() -> None:
    """A failure here means a published-link contract moved (L05, L46): a changed name,
    order or default needs a logged decision before Phase 33 publishes the first shaft
    link, and is a broken link after it."""
    assert list(ShaftParams.model_fields) == list(ALL_FIELDS)
    assert {n: f.default for n, f in ShaftParams.model_fields.items()} == {
        "reference_d": 25.0,
        "module": 1.25,
        "teeth": 18,
        "fit": "8f",
        "splined_length": 30.0,
        "end_chamfer": 1.0,
        "shank_d": 25.0,
        "shank_length": 20.0,
    }


def test_the_default_shaft_validates_and_sits_on_the_upper_shift_edge() -> None:
    """D-19: the default is W 25x1.25x18x8f and its shift is the range edge. It does not
    exercise the epsilon: under the pinned expression order it computes to
    0.44999999999999996, never above 0.45. The epsilon is proved by the three dedicated
    cases of test_the_shift_range_edges_are_accepted_through_the_epsilon."""
    ShaftParams()
    # A literal tolerance, not X_EPS: the default must read as the edge whatever the
    # epsilon is, which is what lets the epsilon-zero red leave this test green.
    assert abs(din5480.profile_shift(25.0, 1.25, 18) - X_MAX) <= 1e-9


def test_a_shaft_parameter_set_is_frozen_and_hashable() -> None:
    p = ShaftParams()
    for name in ALL_FIELDS:
        with pytest.raises(ValidationError, match="frozen"):
            setattr(p, name, None)
    assert hash(ShaftParams()) == hash(ShaftParams())


@pytest.mark.parametrize(("fit", "accepted"), [
    ("8f", True),
    ("9h", True),
    ("10f", True),
    ("f8", False),        # the ISO spelling is refused (REQUIREMENTS Out of Scope)
    ("08f", False),       # no leading zero
    ("8F", False),        # lower-case letter only
    ("8", False),         # the letter is required
    ("", False),
    ("8ff", False),       # one letter
    ("8f\n", False),      # a trailing newline is not a match
    ("\u0663f", False),   # Arabic-Indic digit three: ASCII classes only
    ("\uff18f", False),   # full-width digit eight
])
def test_the_fit_token_is_checked_for_shape_only(fit: str, accepted: bool) -> None:
    errors = _errors(fit=fit)
    if accepted:
        assert errors == []
        return
    assert errors
    assert errors[0]["loc"] == ("fit",)
    assert errors[0]["type"] in {"string_pattern_mismatch", "string_too_long"}


@pytest.mark.parametrize(("field", "ge", "le"), [
    ("reference_d", 3, 850),
    ("module", 0.5, 10),
    ("teeth", 6, 82),
    ("splined_length", 1, 500),
    ("end_chamfer", 0, 10),
    ("shank_d", 1, 850),
    ("shank_length", 0, 500),
])
def test_each_field_bound_is_inclusive_and_one_step_outside_is_refused(
        field: str, ge: float, le: float) -> None:
    step = 1 if field == "teeth" else 0.01
    for bound, outside, kind in ((ge, ge - step, "greater_than_equal"),
                                 (le, le + step, "less_than_equal")):
        # At the bound the field check passes; the only error that can remain is the
        # cross-field refusal of a shift the other defaults cannot carry.
        assert {e["type"] for e in _errors(**{field: bound})} <= {"infeasible"}
        refused = _errors(**{field: outside})
        assert [(e["loc"], e["type"]) for e in refused] == [((field,), kind)]
    # The extreme module and tooth count validate on a reference diameter that fits them.
    ShaftParams(reference_d=3.75, module=0.5, teeth=6)
    ShaftParams(reference_d=835, module=10, teeth=82)


@pytest.mark.parametrize("field", FLOAT_FIELDS)
@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf, 1e400])
def test_non_finite_numbers_are_refused(field: str, value: float) -> None:
    errors = _errors(**{field: value})
    assert errors
    assert errors[0]["loc"] == (field,)
    assert errors[0]["type"] != "infeasible"


@pytest.mark.parametrize("field", ALL_FIELDS)
def test_a_missing_or_null_field_is_refused_by_its_type(field: str) -> None:
    errors = _errors(**{field: None})
    assert errors
    assert errors[0]["loc"] == (field,)
    assert all(e["type"] != "infeasible" for e in errors)
    # Left out altogether, the field is the default shaft's value and the part validates.
    assert _errors() == []


@pytest.mark.parametrize(("reference_d", "teeth"), [(25.05, 18), (24.95, 19)])
def test_a_shift_outside_the_shaft_range_is_refused_naming_the_range_and_fields(
        reference_d: float, teeth: int) -> None:
    errors = _errors(reference_d=reference_d, module=1.25, teeth=teeth)
    assert errors[0]["type"] == "infeasible"
    ctx = errors[0]["ctx"]
    assert isinstance(ctx, dict)
    assert ctx["fields"] == ["module", "reference_d", "teeth"]
    assert "-0.05" in str(ctx["message"])
    assert "+0.45" in str(ctx["message"])
    # One tooth fewer puts 24.95 back inside the range: x 0.43.
    assert _errors(reference_d=24.95, module=1.25, teeth=18) == []


@pytest.mark.parametrize(("reference_d", "module", "teeth", "edge"), [
    pytest.param(17.6, 0.8, 20, X_MAX, id="upper-17.6x0.8x20"),
    pytest.param(30, 2, 14, X_MIN, id="lower-30x2x14"),
    pytest.param(25, 1.25, 19, X_MIN, id="lower-25x1.25x19"),
])
def test_the_shift_range_edges_are_accepted_through_the_epsilon(
        reference_d: float, module: float, teeth: int, edge: float) -> None:
    x = din5480.profile_shift(reference_d, module, teeth)
    # The case stops meaning anything the day the expression order changes: the raw shift
    # must sit outside the bare range, by less than the epsilon. If this line fails, the
    # case no longer proves the epsilon and needs another combination.
    # The tolerance is a literal, so that a zeroed epsilon fails on the refusal below and
    # not on this line.
    outside = x - edge if edge == X_MAX else edge - x
    assert 0 < outside <= 1e-9
    ShaftParams(reference_d=reference_d, module=module, teeth=teeth)


@pytest.mark.parametrize(("reference_d", "teeth", "side", "edge"), [
    pytest.param(25.05, 18, "above", X_MAX, id="upper-25.05"),
    pytest.param(25.001, 18, "above", X_MAX, id="upper-25.001-inside-the-rounding-of-the-edge"),
    pytest.param(24.95, 19, "below", X_MIN, id="lower-24.95"),
    pytest.param(24.999, 19, "below", X_MIN, id="lower-24.999-inside-the-rounding-of-the-edge"),
    pytest.param(25.0001, 18, "above", X_MAX, id="upper-25.0001-under-the-four-decimals"),
    pytest.param(25.00001, 18, "above", X_MAX, id="upper-25.00001-prints-as-the-default-25"),
    pytest.param(24.99999, 19, "below", X_MIN, id="lower-24.99999-under-the-four-decimals"),
])
def test_a_refused_shift_is_printed_apart_from_the_edge_it_crossed_and_names_the_side(
        reference_d: float, teeth: int, side: str, edge: float) -> None:
    """The default sits on the upper edge, so the form's first 0.05 step off it, or a nudge of
    0.001, lands just outside it, and an API caller may nudge it by far less. A shift printed
    to the same digits as the edge ("+0.450, outside +0.45") tells the user nothing about
    which way to move."""
    errors = _errors(reference_d=reference_d, module=1.25, teeth=teeth)
    assert errors[0]["type"] == "infeasible"
    ctx = errors[0]["ctx"]
    assert isinstance(ctx, dict)
    message = str(ctx["message"])
    printed = re.search(r"profile shift of ([+-][0-9.]+),", message)
    assert printed is not None, message
    assert float(printed.group(1)) != edge
    # The input is printed as given: six significant digits would name 25.00001 as the
    # default 25 (31-REVIEW WR-06).
    shown_d = re.search(r"reference diameter of ([0-9.]+) mm", message)
    assert shown_d is not None, message
    assert float(shown_d.group(1)) == reference_d
    assert f"{side} the allowed range {X_MIN:+.2f} to {X_MAX:+.2f}" in message


@pytest.mark.parametrize("field", ["reference_d", "module", "teeth"])
def test_the_three_fields_that_set_the_shift_say_which_shifts_are_refused(field: str) -> None:
    """The default sits exactly on the upper edge, so the first step off it refuses; the form
    must say so before the user finds out from a 422 (31-REVIEW IN-05)."""
    help_text = ShaftParams.model_fields[field].description or ""
    assert f"Shifts outside {X_MIN:+.2f}..{X_MAX:+.2f} are refused." in help_text
