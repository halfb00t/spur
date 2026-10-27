"""The DIN 5480 formulas for the external shaft, as pure arithmetic over floats.

Like shaft_calc.py this file stays free of the CAD kernel, the solid, the logger and the
gear maths. A formula or constant carries a `DIN 5480-<part>:2006, <clause>` citation where
the human's copy of Part 1 (an unofficial translation, read at the 31-05 checkpoint)
confirmed it. One still marked as an assumption is one the copy did not confirm: it is reproduced
from two vendor reports (KISSsoft W70x3x22, Hexagon W120x3x38x8f) and checked against a
geometric oracle, and each is named in L47. A number printed from here is a number someone
will cut metal to (L08, D-06).
"""

from __future__ import annotations

import math
import re
from typing import NamedTuple

# One constants block. Each line carries unit, source and the slot the copy's clause fills.
ALPHA = math.radians(30.0)  # rad, pressure angle fixed at 30 deg; ASSUMPTION (clause slot)
# h_aP/m, DIN 5480-1:2006, cl. 6, Table 3; KISSsoft prints haP* 0.450.
ADDENDUM_FACTOR = 0.45
# d_B - d_a = 0.2*m, DIN 5480-1:2006, cl. 6, Table 3; the anchor is d_a1 119.40 of W 120x3x38x8f
# (cl. 9.1, Fig. 6, tests/test_din5480_anchors.py), and both vendor reports print the same.
TIP_DIAMETER_OFFSET = 0.2
# The 0.55 of the shift formula, exactly 0.55 in binary64 (checked): DIN 5480-1:2006, cl. 6,
# Table 3. It is a different quantity from H_FP below: the two read alike at 0.55 only
# (31-RESEARCH Pitfall 1).
SHIFT_TERM = ADDENDUM_FACTOR + TIP_DIAMETER_OFFSET / 2
# h_fP/m, DIN 5480-1:2006, cl. 6, Table 3 and cl. 7.1: 0.55 is the broaching and theoretical
# root, 0.60 is hobbing, and a hobbed root is the theoretical root less 0.1*m (the warning
# in shaft_calc says so). 0.55 reproduces Hexagon W120x3x38 d_f 113.40; KISSsoft hobbing uses
# 0.60 and gets 63.10 for W70x3x22. Not a user field.
H_FP = 0.55
# h_fP/m of hobbing, same source as H_FP above (DIN 5480-1:2006, cl. 6, Table 3 and cl. 7.1).
# shaft_calc's hobbed-root sentence and the root_d field description read it (through
# HOBBED_ROOT_DROP); the root diameter itself uses H_FP.
H_FP_HOBBING = 0.60
# rho_fP/m, both vendors; used only by the internal form diameter. ASSUMPTION (clause slot)
RHO_FP = 0.16
# The shaft's profile-shift range, DIN 5480-1:2006, cl. 4 and Table 3. The copy allows
# exceptions above X_MAX at larger tooth counts; refusing them is the honest side, filed as
# docs/tech_debt/active/2026-10-26-shaft-shift-range-narrower-than-din-5480-exceptions.md.
X_MIN = -0.05
X_MAX = 0.45
X_EPS = 1e-9  # comparison epsilon on both range edges (D-19)
# Shape only and ASCII only (D-02); the field and the designation codec share it.
FIT_PATTERN = r"^[1-9][0-9]?[a-z]$"


def inv(a: float) -> float:
    """The involute function, tan(a) - a.

    A copy of calc.py's `inv`, never an import, so gear and shaft numbers stay uncoupled
    (contract C5, the `_involute_angle` precedent). A mathematical definition, no clause.
    """
    return math.tan(a) - a


def _involute_angle(target: float) -> float:
    """Inverse of inv() on (0, pi/2): the angle whose involute function is `target`.

    A copy of calc.py's `_involute_angle` (C5: never imported). Bisection rather than Newton:
    inv is monotonic here, 60 halvings reach full double precision, and no starting guess
    can send it outside the bracket. Numerical, no clause.
    """
    lo, hi = 1e-12, math.radians(89.0)
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if inv(mid) < target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def profile_shift(reference_d: float, m: float, z: int) -> float:
    """The profile shift x that puts the reference diameter d_B on the shaft.

    d_B = m*z + 2*x*m + 2*SHIFT_TERM*m, so x = (d_B - m*z)/(2*m) - SHIFT_TERM.
    """
    # Four expression orders were measured at plan time. This is the only one under which
    # all three D-19 cases land outside the bare range: (17.6, 0.8, 20) gives
    # 0.45000000000000084, (30, 2, 14) and (25, 1.25, 19) give -0.050000000000000044. The
    # order x*m/m reads (25, 1.25, 19) as exactly -0.05, which a bare comparison accepts, so
    # the epsilon test for that case could not go red.
    return (reference_d - z * m) / (2 * m) - SHIFT_TERM  # DIN 5480-1:2006, cl. 6, Table 3


def tip_diameter(reference_d: float, m: float) -> float:
    """The tip diameter d_a = d_B - TIP_DIAMETER_OFFSET*m (DIN 5480-1:2006, cl. 6, Table 3)."""
    return reference_d - TIP_DIAMETER_OFFSET * m


def root_diameter(m: float, z: int, xm: float, h_fp: float) -> float:
    """The root diameter d_f = m*z + 2*xm - 2*h_fp*m.

    DIN 5480-1:2006, cl. 6, Table 3. The dedendum factor is an argument so each vendor row
    runs at its own h_fP.
    """
    return m * z + 2 * xm - 2 * h_fp * m


def tooth_thickness(m: float, xm: float) -> float:
    """The nominal tooth thickness s on the circle m*z: pi*m/2 + 2*xm*tan(ALPHA).

    DIN 5480-1:2006, cl. 6, Table 3.
    """
    return math.pi * m / 2 + 2 * xm * math.tan(ALPHA)


def theoretical_pin_diameter(m: float, z: int, xm: float) -> float:
    """The pin that touches both flanks on the circle m*z + 2*xm, in closed form.

    d = m*z, d_b = d*cos(ALPHA), contact circle d_c = d + 2*xm, a_c = acos(d_b/d_c),
    s = tooth_thickness(m, xm), a_m = tan(a_c) - s/d - inv(ALPHA) + pi/z, and the pin is
    d_b*(tan(a_m) - tan(a_c)). The pin diameter cancels out of the contact equation, so no
    solver is needed. Reproduces KISSsoft's theoretical pin 5.8253 for W70x3x22.
    ASSUMPTION (clause slot)
    """
    d = m * z
    d_b = d * math.cos(ALPHA)
    a_c = math.acos(d_b / (d + 2 * xm))
    s = tooth_thickness(m, xm)
    a_m = math.tan(a_c) - s / d - inv(ALPHA) + math.pi / z
    return d_b * (math.tan(a_m) - math.tan(a_c))


def measure_over_pins(m: float, z: int, s: float, pin_d: float) -> tuple[float, float] | None:
    """(measure over pins, contact diameter) for a tooth thickness s on the circle m*z.

    target = pin_d/d_b + s/d + inv(ALPHA) - pi/z is inv(a_m) at the pin centre; the pin
    touches where tan(a_c) = tan(a_m) - pin_d/d_b. The centre circle is d_b/cos(a_m), times
    cos(pi/(2*z)) for an odd count, where the two pins sit half a space apart; the measure
    is that plus pin_d. It takes the thickness, not the shift, so a vendor row runs at its
    actual thickness and Phase 34 can pass limit thicknesses unchanged.

    None when there is no honest root: the target outside (0, inv(89 deg)), or a pin that
    would touch at or below the base circle, where it is not on the involute and not a
    flank measurement (L08, 31-RESEARCH Pitfall 5).

    The even count reproduces M1 minimum of DIN 5480-1:2006-03, cl. 9.1, Fig. 6, at the
    gauge pin 6.000 and the row's own thickness (tests/test_din5480_anchors.py). The odd
    factor is DIN 5480-1:2006, cl. 4, eq. (1). Both counts reproduce M1 of DIN 5480-2:2006-05,
    Tables 13 and 19, at the tabulated pin and the nominal thickness (four approved rows, two
    odd, in the same test file). shaft_calc still prints no odd-count M_Re: the human kept the
    gate (D-13; docs/ideas/2026-10-26-print-odd-tooth-count-measure-over-pins.md).
    Part 1 names these D_M, M1 and M2 and points to DIN 5480-15, 5.2.4.3 for D_Re and
    M_Re; that clause has not been read. ASSUMPTION (clause: DIN 5480-15,
    5.2.4.3 unread)
    """
    d = m * z
    d_b = d * math.cos(ALPHA)
    target = pin_d / d_b + s / d + inv(ALPHA) - math.pi / z
    if not 0 < target < inv(math.radians(89.0)):
        return None
    a_m = _involute_angle(target)
    tangent = math.tan(a_m) - pin_d / d_b
    if tangent <= 0:
        return None
    contact = d_b * math.hypot(1, tangent)
    centre_circle = d_b / math.cos(a_m)
    if z % 2:
        centre_circle *= math.cos(math.pi / (2 * z))
    return centre_circle + pin_d, contact


def form_diameter(m: float, z: int, xm: float, h_fp: float, rho_fp: float) -> float:
    """The form diameter of the public construction: where the rack's flank meets its tip arc.

    That point lies h = h_fp*m - xm - rho_fp*m*(1 - sin(ALPHA)) below the shifted datum
    (xm in millimetres) and is generated at
    sqrt(d_b**2 + (d*sin(ALPHA) - 2*h/sin(ALPHA))**2), with d = m*z and d_b = d*cos(ALPHA).
    Valid where that point generates above the base circle, which holds over z 6 to 82 and
    x -0.05 to +0.45 for h_fP up to 0.65 (plan-time check; Part 1 names a larger cold-rolling
    factor, so repeat the check before any process above 0.65 is used).

    This is the pin-contact guard's internal lower bound and is never printed as d_Ff: the
    vendors print the standard's form diameter as a limit that depends on the mating hub,
    and no DIN 5480 row proves this construction yet (D-12, L08). DIN 5480-2 prints d_Ff1 as
    a maximum, and this construction exceeds it on most rows at h_fP 0.55: docs/tech_debt/
    active/2026-10-26-form-diameter-construction-exceeds-din5480-2-maximum.md.
    ASSUMPTION (clause slot)
    """
    d = m * z
    d_b = d * math.cos(ALPHA)
    h = h_fp * m - xm - rho_fp * m * (1 - math.sin(ALPHA))
    return math.hypot(d_b, d * math.sin(ALPHA) - 2 * h / math.sin(ALPHA))


# The designation codec. The notation is the standard's, `W <d_B>x<m>x<z>x<fit>`. Every
# character class below is ASCII on purpose: `\d` matches Unicode digits and `float("\u0663")`
# succeeds, so a permissive pattern would build a part from text nobody typed as a number
# (31-RESEARCH Pitfall 6).
# The longest real designation, W 835.000000x10.000000x82x11a, is 29 characters; the bound
# caps the input of every regex below.
DESIGNATION_MAX_LENGTH = 64

# No leading zero, as the fit's FIT_PATTERN has none, so no numeric token has two integer-part
# spellings (25 and 0025). That is not one spelling per shaft: trailing zeros after the point,
# `,` for the decimal mark, an upper-case X and a missing space after W are accepted too (see
# parse_designation). The canonical form is format_designation's output; a link or a cache
# key must be built from format_designation(*parse_designation(text)), never from the input
# text. A lone 0 integer part stays, because the module may be 0.5 (ShaftParams' lower
# bound).
_NUMBER = r"(?:0|[1-9][0-9]*)(?:[.,][0-9]+)?"
_TEETH = r"[1-9][0-9]*"


class Designation(NamedTuple):
    """The four fields a designation names; the names equal ShaftParams' own."""

    reference_d: float
    module: float
    teeth: int
    fit: str


class DesignationError(ValueError):
    """An unparseable designation; `token` is the text that was refused."""

    def __init__(self, token: str, message: str) -> None:
        # args carries both, because pickle and copy rebuild an exception as cls(*args): with
        # args == (message,) the rebuild raised a TypeError for the missing second argument.
        super().__init__(token, message)
        self.token = token
        self.message = message

    def __str__(self) -> str:
        return self.message


def _number(v: float) -> str:
    # repr is the shortest string that round-trips a float (`:g` keeps six significant
    # digits and loses 25.123456); the fields' bounds keep it out of exponent form.
    return repr(float(v)).removesuffix(".0")


def format_designation(reference_d: float, module: float, teeth: int, fit: str) -> str:
    """The one canonical form: `W 25x1.25x18x8f`."""
    return f"W {_number(reference_d)}x{_number(module)}x{teeth}x{fit}"


def parse_designation(text: str) -> Designation:
    """The four fields of a designation, or a DesignationError naming the bad token.

    Accepts the canonical form plus no space after W, an upper-case X, `,` for the decimal
    mark and trailing zeros after the point (25.0, 1.250). Nothing else is repaired: spaces
    around x, a multiplication sign, an upper-case fit letter, a leading zero in any number
    or the fit, or a fractional tooth count are refused, never read as a nearby shaft (D-05,
    D-21).
    """
    if len(text) > DESIGNATION_MAX_LENGTH:
        raise DesignationError(
            text[:DESIGNATION_MAX_LENGTH],
            f"The designation is {len(text)} characters long; the longest accepted is "
            f"{DESIGNATION_MAX_LENGTH}.")
    if not text.startswith("W"):
        word = text.split(" ", 1)[0]
        if word[:1] == "N" and not word[1:2].isalpha():
            raise DesignationError(
                "N", "The designation 'N' is for an internal spline (hub), which is not "
                     "supported; only the shaft, W, is.")
        raise DesignationError(
            word, f"The designation must start with the type letter W, not {word!r}.")
    rest = text[1:]
    if rest.startswith(" "):
        rest = rest[1:]
    tokens = re.split(r"[xX]", rest, maxsplit=3)  # maxsplit keeps an x inside the fit token
    if len(tokens) != 4:
        raise DesignationError(
            rest, f"The designation needs four parts, W <d_B>x<m>x<z>x<fit>; {rest!r} "
                  f"does not split into them.")
    d_b, m, z, fit = tokens
    if not re.fullmatch(_NUMBER, d_b):
        raise DesignationError(d_b, f"The reference diameter {d_b!r} is not a number such "
                                    f"as 25 or 25.5, written without leading zeros.")
    if not re.fullmatch(_NUMBER, m):
        raise DesignationError(m, f"The module {m!r} is not a number such as 1.25, written "
                                    f"without leading zeros.")
    if not re.fullmatch(_TEETH, z):
        raise DesignationError(z, f"The tooth count {z!r} is not a whole number such as "
                                    f"18, written without leading zeros.")
    if not re.fullmatch(FIT_PATTERN, fit):
        raise DesignationError(fit, f"The fit {fit!r} is not a fit such as 8f.")
    return Designation(float(d_b.replace(",", ".")), float(m.replace(",", ".")), int(z), fit)
