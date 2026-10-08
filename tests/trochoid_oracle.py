"""The swept-cutter clearance oracle for the hob's trochoid root (Phase 18, T2).

Not collected: no `test_` prefix, the `tests/composition.py` shape. It imports nothing
from `spur` and takes plain floats, so a wrong sign, side or root in `spur.calc`
disagrees with it instead of moving both sides together (L08) -- the
`_filleted_spoke_volume` precedent in `tests/test_model.py`. The cutter is rebuilt here
from the textbook rack definitions (half-width e/2 on the rolling line, flank angle,
flat tip at depth d, tip radius rho), never from the envelope formula the code under
test implements.

A point of a gear is on the boundary the hob cuts if, as the rack rolls on the pitch
circle, it touches the cutter at one rolling angle and is inside it at none. So the
reading for a point is the minimum, over rolling angles, of its signed distance to the
cutter (negative inside the cutter): about 0 on the cut boundary, negative where the
curve gouges, positive where it leaves material uncut.

It carries the neighbouring cutter teeth (k = -1 and +1 beside the tooth that cuts this
space) because the next space's cutter can cut a tooth through: a single-tooth oracle
reads 0 on such a tooth and cannot see it (18-RESEARCH Pattern 6, measured: 0 without
the neighbours, 0.141 mm with them at 6 teeth, 14.5 degrees, x -0.6, rho 0).
"""

from __future__ import annotations

import math

_GRID = 2001      # rolling angles tried before refining
_GOLDEN = (math.sqrt(5) - 1) / 2


def _polygon_distance(px: float, py: float, polygon: list[tuple[float, float]]) -> float:
    """Signed distance from (px, py) to a convex polygon given counter-clockwise,
    negative inside. A repeated vertex (a zero-length edge) is allowed."""
    best = math.inf
    inside = True
    for (x0, y0), (x1, y1) in zip(polygon, polygon[1:] + polygon[:1], strict=True):
        ex, ey = x1 - x0, y1 - y0
        length_sq = ex * ex + ey * ey
        along = 0.0 if length_sq == 0 else ((px - x0) * ex + (py - y0) * ey) / length_sq
        t = max(0.0, min(1.0, along))
        best = min(best, math.hypot(px - (x0 + t * ex), py - (y0 + t * ey)))
        if ex * (py - y0) - ey * (px - x0) < 0:
            inside = False
    return -best if inside else best


def clearance(points: tuple[tuple[float, float], ...], *, teeth: int, module: float,
              pressure_angle: float, profile_shift: float, backlash: float,
              rho: float, neighbours: bool = True) -> list[float]:
    """For each (radius mm, half-angle from the tooth centre rad) point, the minimum over
    rolling angles of its signed distance to the rack cutter, mm; negative inside it.

    `neighbours=False` keeps only the tooth that cuts this space (k = 0)."""
    z, m, x, bl = teeth, module, profile_shift, backlash
    alpha = math.radians(pressure_angle)
    r = m * z / 2
    s = m * (math.pi / 2 + 2 * x * math.tan(alpha)) - bl   # tooth thickness on the pitch circle
    e = math.pi * m - s                                    # space width = cutter tooth width
    d = m * (1.25 - x)                                     # cutter tip depth below the rolling line
    w_c = rho - d                                          # tip-arc centre height
    a = max(0.0, e / 2 + w_c * math.tan(alpha) - rho / math.cos(alpha))  # flat tip half-width
    top = 3 * m                                            # core height, well above any gear point
    reach = a + (top - w_c) * math.tan(alpha)
    core = [(-a, w_c), (a, w_c), (reach, top), (-reach, top)]
    ks = (-1, 0, 1) if neighbours else (0,)

    def reading(px: float, py: float, roll: float) -> float:
        n = (math.sin(roll), math.cos(roll))
        t = (math.cos(roll), -math.sin(roll))
        dx, dy = px - r * n[0], py - r * n[1]
        w = dx * n[0] + dy * n[1]
        u = r * roll + dx * t[0] + dy * t[1]
        return min(_polygon_distance(u - k * math.pi * m, w, core) - rho for k in ks)

    out = []
    for radius, half in points:
        theta = math.pi / z - half
        px, py = radius * math.sin(theta), radius * math.cos(theta)
        span = 2 * math.pi / z
        step = 2 * span / (_GRID - 1)
        rolls = [-span + i * step for i in range(_GRID)]
        values = [reading(px, py, roll) for roll in rolls]
        i = min(range(_GRID), key=values.__getitem__)
        lo, hi = rolls[max(i - 1, 0)], rolls[min(i + 1, _GRID - 1)]
        c1, c2 = hi - _GOLDEN * (hi - lo), lo + _GOLDEN * (hi - lo)
        f1, f2 = reading(px, py, c1), reading(px, py, c2)
        for _ in range(60):
            if f1 < f2:
                hi, c2, f2 = c2, c1, f1
                c1 = hi - _GOLDEN * (hi - lo)
                f1 = reading(px, py, c1)
            else:
                lo, c1, f1 = c1, c2, f2
                c2 = lo + _GOLDEN * (hi - lo)
                f2 = reading(px, py, c2)
        out.append(min(values[i], f1, f2))
    return out
