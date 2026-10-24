"""The DIN 5480 shaft oracle (Phase 31): basic dimensions rebuilt from the rack.

Not collected: no `test_` prefix, the `tests/trochoid_oracle.py` shape. It takes plain
floats and imports nothing of `spur`, so a wrong sign, constant or side in `spur.din5480`
disagrees with it instead of moving both sides together (L08).

What it rebuilds, and from where. The basic rack of the shaft has a 30 degree flank, its
tip addendum is 0.45*m above the shifted datum line, and the reference diameter d_B sits
0.2*m above the tip circle. The nominal tooth thickness is not read from din5480's
closed form: it is measured on a parametric involute, placed on the base circle by the
textbook base-thickness identity, at the radius m*z/2. A thickness built on another road
is the point; the textbook identity is s_b = s*cos(alpha) + d_b*inv(alpha), written here
with inv expanded to tan(alpha) - alpha so no involute helper lives in this file.

The two root formulas are the same definition written twice, so their comparison proves
the transcription and nothing more. The oracle proves the shift term, the tip and the
thickness, which are computed by different roads.

31-03 adds the pins, the contact and the form diameter to this file.
"""

from __future__ import annotations

import math

# Written here on purpose, never read from spur: a shared constant would move both sides.
_ALPHA = math.radians(30.0)
_ADDENDUM = 0.45  # h_aP/m of the basic rack
_TIP_CLEARANCE = 0.2  # d_B - d_a, in modules


def reference_diameter(m: float, z: int, x: float) -> float:
    """d_B from the rack: the tip circle plus the tip clearance, `_TIP_CLEARANCE*m`."""
    return tip_diameter(m, z, x) + _TIP_CLEARANCE * m


def tip_diameter(m: float, z: int, x: float) -> float:
    """The rack's tip circle: m*z + 2*x*m + 2*_ADDENDUM*m."""
    return m * z + 2 * x * m + 2 * _ADDENDUM * m


def root_diameter(m: float, z: int, x: float, h_fp: float) -> float:
    """The rack's root circle: m*z + 2*x*m - 2*h_fp*m.

    The same definition din5480 uses, so comparing the two proves the transcription only.
    """
    return m * z + 2 * x * m - 2 * h_fp * m


def _involute_point(r_b: float, t: float) -> tuple[float, float]:
    """The parametric involute of a base circle r_b that starts at (r_b, 0).

    x = r_b*(cos t + t*sin t), y = r_b*(sin t - t*cos t); t is the unrolled angle.
    """
    return r_b * (math.cos(t) + t * math.sin(t)), r_b * (math.sin(t) - t * math.cos(t))


def tooth_thickness(m: float, z: int, x: float) -> float:
    """The arc thickness on the circle of radius m*z/2, measured on the involute flank.

    The base thickness is s_b = m*cos(a)*(pi/2 + z*(tan(a) - a)) + 2*x*m*sin(a), which
    puts the flank at the half angle s_b/(2*r_b) from the tooth centre on the base circle.
    The involute point that reaches radius r has t = sqrt((r/r_b)**2 - 1); its polar angle,
    read with atan2 from its coordinates, is how far the flank has turned back by there.
    The thickness is 2*r times what is left of the half angle.
    """
    r = m * z / 2
    r_b = r * math.cos(_ALPHA)
    s_b = m * math.cos(_ALPHA) * (math.pi / 2 + z * (math.tan(_ALPHA) - _ALPHA)) + (
        2 * x * m * math.sin(_ALPHA)
    )
    half_angle_at_base = s_b / (2 * r_b)
    px, py = _involute_point(r_b, math.sqrt((r / r_b) ** 2 - 1))
    return 2 * r * (half_angle_at_base - math.atan2(py, px))
