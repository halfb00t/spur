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

Pins and the form diameter (31-03) are built the same way, by geometry and not by the
closed forms. The measurement over pins and the contact diameter come from a tangency
search: the flank is the mirrored parametric involute rotated by the base half-thickness
angle, a pin centre sits on the space centreline, and the centre radius is bisected until
the least distance from the centre to the flank is half the pin. No involute-function
inverse, no closed-form pin. The form diameter is read off the line of action through the
pitch point instead of the closed-form hypotenuse. The hobbing tip radius and dedendum
arrive as arguments, so the oracle holds no provisional constant of din5480.
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


def _flank_point(r_b: float, psi_b: float, t: float) -> tuple[float, float]:
    """The upper flank of the tooth centred on +x: the mirrored involute, turned by psi_b.

    A straight tangent to the base circle is not an involute; the mirror and the rotation
    are what make this the flank of a tooth, not of a space.
    """
    qx, qy = _involute_point(r_b, t)
    qy = -qy
    return (math.cos(psi_b) * qx - math.sin(psi_b) * qy,
            math.sin(psi_b) * qx + math.cos(psi_b) * qy)


def _distance_to_flank(r_b: float, psi_b: float, t_max: float,
                       cx: float, cy: float) -> tuple[float, float]:
    """(least distance from (cx, cy) to the flank over t in [0, t_max], the t that gives it).

    A coarse grid finds the basin, a golden-section search inside its two neighbours
    refines it.
    """
    def dist(t: float) -> float:
        px, py = _flank_point(r_b, psi_b, t)
        return math.hypot(px - cx, py - cy)

    steps = 400
    best = min(range(steps + 1), key=lambda i: dist(t_max * i / steps))
    lo = t_max * max(best - 1, 0) / steps
    hi = t_max * min(best + 1, steps) / steps
    ratio = (math.sqrt(5) - 1) / 2
    for _ in range(80):
        a = hi - ratio * (hi - lo)
        b = lo + ratio * (hi - lo)
        if dist(a) < dist(b):
            hi = b
        else:
            lo = a
    t = 0.5 * (lo + hi)
    return dist(t), t


def _pin_search(m: float, z: int, x: float, pin_d: float) -> tuple[float, float, float]:
    """(pin centre radius, contact radius, base radius) of a pin of diameter pin_d.

    The centre sits on the space centreline at the polar angle pi/z; its radius is bisected
    on (r_b, r_a + pin_d) until the pin just touches the flank. The bracket reaches r_a +
    pin_d because the centre of a pin that touches near the tip sits outside the tip circle.
    """
    r = m * z / 2
    r_b = r * math.cos(_ALPHA)
    r_a = tip_diameter(m, z, x) / 2
    s_b = m * math.cos(_ALPHA) * (math.pi / 2 + z * (math.tan(_ALPHA) - _ALPHA)) + (
        2 * x * m * math.sin(_ALPHA)
    )
    psi_b = s_b / (2 * r_b)
    t_max = math.sqrt((r_a / r_b) ** 2 - 1)
    lo, hi = r_b, r_a + pin_d
    contact_t = 0.0
    for _ in range(60):
        rho = 0.5 * (lo + hi)
        least, contact_t = _distance_to_flank(
            r_b, psi_b, t_max, rho * math.cos(math.pi / z), rho * math.sin(math.pi / z))
        if least < pin_d / 2:
            lo = rho
        else:
            hi = rho
    rho = 0.5 * (lo + hi)
    px, py = _flank_point(r_b, psi_b, contact_t)
    return rho, math.hypot(px, py), r_b


def measure(m: float, z: int, x: float, pin_d: float) -> float:
    """The measurement over pins: two pins in opposite spaces, outer extent of both.

    Even z: the spaces are diametrically opposite, so it is 2*rho + pin_d. Odd z: the
    second pin sits in the space at the polar angle pi, and the measure is the distance
    between the two centres plus pin_d.
    """
    rho = _pin_search(m, z, x, pin_d)[0]
    if z % 2 == 0:
        return 2 * rho + pin_d
    first = (rho * math.cos(math.pi / z), rho * math.sin(math.pi / z))
    second = (-rho, 0.0)
    return math.hypot(first[0] - second[0], first[1] - second[1]) + pin_d


def contact_diameter(m: float, z: int, x: float, pin_d: float) -> float:
    """The diameter of the circle through the point where the pin touches the flank."""
    return 2 * _pin_search(m, z, x, pin_d)[1]


def form_diameter(m: float, z: int, x: float, h_fp: float, rho_fp: float) -> float:
    """Where the rack's straight flank meets its tip arc, generated onto the shaft.

    That rack point lies h = h_fp*m - rho_fp*m*(1 - sin a) below the shifted datum, so at
    the height y = r + x*m - h above the axis. The line of action through the pitch point
    (0, r) reaches that height at the horizontal offset (r - y)/tan a; the diameter is twice
    the hypotenuse of the offset and the height.
    """
    r = m * z / 2
    h = h_fp * m - rho_fp * m * (1 - math.sin(_ALPHA))
    y = r + x * m - h
    return 2 * math.hypot((r - y) / math.tan(_ALPHA), y)
