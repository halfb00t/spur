"""The DIN 5480 formulas for the external shaft, as pure arithmetic over floats.

Like shaft_calc.py this file stays free of the CAD kernel, the solid, the logger and the
gear maths. Every formula and constant below is an ASSUMPTION: it is reproduced from two
vendor reports (KISSsoft W70x3x22, Hexagon W120x3x38x8f) and checked against a geometric
oracle, not read from the standard. The 31-05 checkpoint records each clause from the
human's 2006 copy, and a marker still present at the phase close is a deliberate, logged
state, not an accident (L08, D-06). A number printed from here is a number someone will cut
metal to.
"""

from __future__ import annotations

import math

# One constants block. Each line carries unit, source and the slot the copy's clause fills.
ALPHA = math.radians(30.0)  # rad, pressure angle fixed at 30 deg; ASSUMPTION (clause slot)
ADDENDUM_FACTOR = 0.45  # h_aP/m, KISSsoft prints haP* 0.450; ASSUMPTION (clause slot)
# d_B - d_a = 0.2*m: 69.400 and 119.40 in both vendor reports. ASSUMPTION (clause slot)
TIP_DIAMETER_OFFSET = 0.2
# The 0.55 of the shift formula, exactly 0.55 in binary64 (checked). It is a different
# quantity from H_FP below: the two read alike only at their provisional values
# (31-RESEARCH Pitfall 1). ASSUMPTION (clause slot)
SHIFT_TERM = ADDENDUM_FACTOR + TIP_DIAMETER_OFFSET / 2
# h_fP/m, provisional per D-07: 0.55 reproduces Hexagon W120x3x38 d_f 113.40 while KISSsoft
# hobbing uses 0.60 and gets 63.10 for W70x3x22; the copy decides. Not a user field.
# ASSUMPTION (clause slot)
H_FP = 0.55
# rho_fP/m, both vendors; used only by the internal form diameter. ASSUMPTION (clause slot)
RHO_FP = 0.16
X_MIN = -0.05  # lowest profile shift of the shaft range; ASSUMPTION (clause slot)
X_MAX = 0.45  # highest profile shift of the shaft range; ASSUMPTION (clause slot)
X_EPS = 1e-9  # comparison epsilon on both range edges (D-19)
# Shape only and ASCII only (D-02); the field and the designation codec share it.
FIT_PATTERN = r"^[1-9][0-9]?[a-z]$"


def inv(a: float) -> float:
    """The involute function, tan(a) - a.

    A copy of calc.py's `inv`, never an import, so gear and shaft numbers stay uncoupled
    (contract C5, the `_involute_angle` precedent). ASSUMPTION (clause slot)
    """
    return math.tan(a) - a


def _involute_angle(target: float) -> float:
    """Inverse of inv() on (0, pi/2): the angle whose involute function is `target`.

    A copy of calc.py's `_involute_angle` (C5: never imported). Bisection rather than Newton:
    inv is monotonic here, 60 halvings reach full double precision, and no starting guess
    can send it outside the bracket. ASSUMPTION (clause slot)
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
    # the epsilon test for that case could not go red. ASSUMPTION (clause slot)
    return (reference_d - z * m) / (2 * m) - SHIFT_TERM


def tip_diameter(reference_d: float, m: float) -> float:
    """The tip diameter d_a = d_B - TIP_DIAMETER_OFFSET*m."""
    return reference_d - TIP_DIAMETER_OFFSET * m  # ASSUMPTION (clause slot)


def root_diameter(m: float, z: int, xm: float, h_fp: float) -> float:
    """The root diameter d_f = m*z + 2*xm - 2*h_fp*m.

    The dedendum factor is an argument so each vendor row runs at its own h_fP.
    """
    return m * z + 2 * xm - 2 * h_fp * m  # ASSUMPTION (clause slot)


def tooth_thickness(m: float, xm: float) -> float:
    """The nominal tooth thickness s on the circle m*z: pi*m/2 + 2*xm*tan(ALPHA)."""
    return math.pi * m / 2 + 2 * xm * math.tan(ALPHA)  # ASSUMPTION (clause slot)


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
    flank measurement (L08, 31-RESEARCH Pitfall 5). ASSUMPTION (clause slot)
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
    x -0.05 to +0.45 for h_fP up to 0.65 (plan-time check).

    This is the pin-contact guard's internal lower bound and is never printed as d_Ff: the
    vendors print the standard's form diameter as a limit that depends on the mating hub,
    and no DIN 5480 row proves this construction yet (D-12, L08). ASSUMPTION (clause slot)
    """
    d = m * z
    d_b = d * math.cos(ALPHA)
    h = h_fp * m - xm - rho_fp * m * (1 - math.sin(ALPHA))
    return math.hypot(d_b, d * math.sin(ALPHA) - 2 * h / math.sin(ALPHA))
