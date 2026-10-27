# ruff: noqa -- throwaway kernel spike, kept verbatim as Phase 32 research evidence.
"""Phase 32 kernel spike at real DIN 5480 proportions (research only, not shipped).

Run:  .venv/bin/python .planning/phases/32-the-shaft-solid/investigation/32-spike.py <mode>
Closed form is stdlib-only (own involute); the build reads only plain floats.
"""
from __future__ import annotations

import math
import sys
import time

import cadquery as cq

A = math.radians(30.0)


def inv(a: float) -> float:
    return math.tan(a) - a


def basics(d_b: float, m: float, z: int):
    x = (d_b - z * m) / (2 * m) - 0.55
    xm = x * m
    ra = round(d_b - 0.2 * m, 3) / 2
    rf = round(m * z + 2 * xm - 2 * 0.55 * m, 3) / 2
    rb = m * z * math.cos(A) / 2
    s_b = m * math.cos(A) * (math.pi / 2 + z * inv(A)) + 2 * xm * math.sin(A)
    psi_b = s_b / (2 * rb)
    return x, xm, ra, rf, rb, psi_b


def half(r: float, rb: float, psi_b: float) -> float:
    """tooth half-angle at radius r (r >= rb)"""
    return psi_b - inv(math.acos(min(1.0, rb / r)))


def polar(r, t):
    return cq.Vector(r * math.cos(t), r * math.sin(t), 0)


def outline(d_b, m, z, flank="spline", npts=16):
    x, xm, ra, rf, rb, psi_b = basics(d_b, m, z)
    rs = max(rf, rb)
    pitch = 2 * math.pi / z
    radii = [rs + (ra - rs) * (i / (npts - 1)) ** 1.5 for i in range(npts)]
    hs = [half(r, rb, psi_b) for r in radii]
    h_root = hs[0]  # half-angle where the flank meets root / radial line
    edges = []
    mk = cq.Edge.makeSpline if flank == "spline" else (lambda pts: cq.Wire.makePolygon(pts).Edges()[0] if False else None)
    for k in range(z):
        c = k * pitch
        left = [polar(r, c - h) for r, h in zip(radii, hs)]
        right = [polar(r, c + h) for r, h in zip(reversed(radii), reversed(hs))]
        if rb > rf:
            edges.append(cq.Edge.makeLine(polar(rf, c - h_root), left[0]))
        if flank == "spline":
            edges.append(cq.Edge.makeSpline(left))
        else:
            edges += [cq.Edge.makeLine(a, b) for a, b in zip(left, left[1:])]
        edges.append(cq.Edge.makeThreePointArc(left[-1], polar(ra, c), right[0]))
        if flank == "spline":
            edges.append(cq.Edge.makeSpline(right))
        else:
            edges += [cq.Edge.makeLine(a, b) for a, b in zip(right, right[1:])]
        if rb > rf:
            edges.append(cq.Edge.makeLine(right[-1], polar(rf, c + h_root)))
        end = polar(rf, (k + 1) * pitch - h_root)
        start = polar(rf, c + h_root)
        edges.append(cq.Edge.makeThreePointArc(start, polar(rf, c + pitch / 2), end))
    return cq.Wire.assembleEdges(edges)


# ---- closed form --------------------------------------------------------------
def simpson(f, a, b, n=2000):
    if b <= a:
        return 0.0
    n += n % 2
    h = (b - a) / n
    s = f(a) + f(b)
    for i in range(1, n):
        s += f(a + i * h) * (4 if i % 2 else 2)
    return s * h / 3


def tooth_area_above(d_b, m, z, rho):
    """z * int_{rf}^{rho} 2 h(r) r dr (radial line below rb: h = h(rb))"""
    x, xm, ra, rf, rb, psi_b = basics(d_b, m, z)
    def f(r):
        return 2 * half(max(r, rb), rb, psi_b) * r
    hi = min(rho, ra)
    # split at rb so the integrand is smooth on each side
    if rb > rf:
        lo_part = simpson(f, rf, min(hi, rb))
        up = simpson(f, rb, hi) if hi > rb else 0.0
        return z * (lo_part + up)
    return z * simpson(f, rf, hi)


def area_spline(d_b, m, z):
    x, xm, ra, rf, rb, psi_b = basics(d_b, m, z)
    return math.pi * rf * rf + tooth_area_above(d_b, m, z, ra)


def area_within(d_b, m, z, rho):
    """area of (spline section cross-section) intersect (disc of radius rho)"""
    x, xm, ra, rf, rb, psi_b = basics(d_b, m, z)
    if rho <= rf:
        return math.pi * rho * rho
    return math.pi * rf * rf + tooth_area_above(d_b, m, z, rho)


def volume_closed(d_b, m, z, Ls, c, shank_d, Lk):
    x, xm, ra, rf, rb, psi_b = basics(d_b, m, z)
    v = area_spline(d_b, m, z) * Ls + math.pi * (shank_d / 2) ** 2 * Lk
    if c > 0:
        full = area_spline(d_b, m, z)
        def removed(t):
            return full - area_within(d_b, m, z, ra - c + t)
        v -= simpson(removed, 0, c, 200)
    return v


# ---- build --------------------------------------------------------------------
def cone_cutter(ra, c, Ls, Lk, shank_d, flat=True):
    """flat=True: cone to (ra, c), then a flat annulus out to `big` (covers a fused shank).
    flat=False: the 45-degree cone carried on to height Ls + 1, no flat (spline prism only)."""
    total = Ls + Lk
    if flat:
        big = max(ra, shank_d / 2) + 1.0
        pts = [cq.Vector(0, 0, 0), cq.Vector(ra - c, 0, 0), cq.Vector(ra, 0, c),
               cq.Vector(big, 0, c), cq.Vector(big, 0, total), cq.Vector(0, 0, total)]
    else:
        h = Ls + 1.0
        pts = [cq.Vector(0, 0, 0), cq.Vector(ra - c, 0, 0), cq.Vector(ra - c + h, 0, h), cq.Vector(0, 0, h)]
    wire = cq.Wire.makePolygon(pts + [pts[0]])
    return cq.Solid.revolve(wire, [], 360, cq.Vector(0, 0, 0), cq.Vector(0, 0, 1))


def build(d_b, m, z, Ls=30.0, c=1.0, shank_d=25.0, Lk=20.0, order="fuse_cut", glue=False,
          flank="spline", timing=None):
    t0 = time.perf_counter()
    x, xm, ra, rf, rb, psi_b = basics(d_b, m, z)
    wire = outline(d_b, m, z, flank)
    face = cq.Face.makeFromWires(wire)
    body = cq.Solid.extrudeLinear(face, cq.Vector(0, 0, Ls))
    t1 = time.perf_counter()
    cutter = (cone_cutter(ra, c, Ls, Lk, shank_d, True) if order == "fuse_cut" else cone_cutter(ra, c, Ls, 0, shank_d, False)) if c > 0 else None
    if order == "cut_fuse":
        if cutter is not None:
            body = body.intersect(cutter)
    t2 = time.perf_counter()
    if Lk > 0:
        shank = cq.Solid.makeCylinder(shank_d / 2, Lk, cq.Vector(0, 0, Ls))
        body = body.fuse(shank, glue=glue)
    t3 = time.perf_counter()
    if order == "fuse_cut" and cutter is not None:
        body = body.intersect(cutter)
    t4 = time.perf_counter()
    if timing is not None:
        timing.update(extrude=t1 - t0, cut_first=t2 - t1, fuse=t3 - t2, cut_last=t4 - t3, total=t4 - t0)
    return body


def report(label, solid, vol_ref):
    sols = solid.Solids()
    v = solid.Volume()
    print(f"{label}: valid={solid.isValid()} nsolids={len(sols)} vol={v:.6f} ref={vol_ref:.6f} "
          f"rel={abs(v / vol_ref - 1):.3e} faces={len(solid.Faces())}")


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "default":
        d_b, m, z = 25.0, 1.25, 18
        for order in ("fuse_cut", "cut_fuse"):
            tm = {}
            s = build(d_b, m, z, order=order, timing=tm)
            report(order, s, volume_closed(d_b, m, z, 30, 1.0, 25.0, 20))
            print({k: round(v, 3) for k, v in tm.items()})
