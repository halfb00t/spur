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
