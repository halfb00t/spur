# ruff: noqa -- throwaway kernel spike, kept verbatim as Phase 32 research evidence.
"""Prototype read-backs on the built solid and a validity matrix. Prints measured tolerances."""
import importlib.util, itertools, math, sys
spec = importlib.util.spec_from_file_location("spike", "/Users/half/git/halfb00t/spur/.planning/phases/32-the-shaft-solid/investigation/32-spike.py")
sp = importlib.util.module_from_spec(spec); spec.loader.exec_module(sp)
import cadquery as cq

def readback(s, Ls):
    """(chamfer from end-face max radius, chamfer from cone z-extent, root r, tip r, n cone faces)"""
    end = [f for f in s.Faces() if f.geomType() == "PLANE" and abs(f.BoundingBox().zmin) < 1e-6 and abs(f.BoundingBox().zmax) < 1e-6]
    assert len(end) == 1, len(end)
    rs = []
    for e in end[0].Edges():
        for i in range(0, 21):
            v = e.positionAt(i / 20)
            rs.append(math.hypot(v.x, v.y))
    rmax_end, rmin_end = max(rs), min(rs)
    cones = [f for f in s.Faces() if f.geomType() == "CONE"]
    zc = max((f.BoundingBox().zmax for f in cones), default=0.0)
    circ = {round(e.radius(), 6) for e in s.Edges() if e.geomType() == "CIRCLE"}
    return rmax_end, rmin_end, zc, len(cones), circ

worst = {"c_end": 0.0, "c_cone": 0.0, "root": 0.0, "vol": 0.0}
rows = 0
cases = []
for (m, z, x) in [(1.25, 18, 0.45), (2, 6, 0.0), (0.5, 6, 0.45), (3, 22, 0.2), (1, 82, 0.1), (10, 30, -0.05), (0.5, 40, 0.3), (5, 14, 0.0)]:
    d_b = round(m * z + 2 * x * m + 1.1 * m, 6)
    cases.append((d_b, m, z))
for d_b, m, z in cases:
    _, xm, ra, rf, rb, psi_b = sp.basics(d_b, m, z)
    for cfrac in (0.01, 0.1, 0.5, 0.9, 1.0):
        c = round(m * cfrac, 3)
        if c <= 0: continue
        for Lk in (0.0, 15.0):
            Ls = max(c, 12.0)
            s = sp.build(d_b, m, z, Ls, c, 2 * ra, Lk)
            assert s.isValid() and len(s.Solids()) == 1
            ref = sp.volume_closed(d_b, m, z, Ls, c, 2 * ra, Lk)
            rmax_end, rmin_end, zc, ncone, circ = readback(s, Ls)
            worst["c_end"] = max(worst["c_end"], abs((ra - rmax_end) - c))
            worst["c_cone"] = max(worst["c_cone"], abs(zc - c))
            worst["root"] = max(worst["root"], abs(rmin_end - rf))
            worst["vol"] = max(worst["vol"], abs(s.Volume() / ref - 1))
            rows += 1
print("rows", rows, {k: f"{v:.2e}" for k, v in worst.items()})
# tiny chamfers
print("--- tiny chamfers on the default")
for c in (1e-2, 1e-3, 5e-4, 1e-4, 1e-5, 1e-6, 1e-7, 1e-8):
    try:
        s = sp.build(25.0, 1.25, 18, 30.0, c, 25.0, 20.0)
        ref = sp.volume_closed(25.0, 1.25, 18, 30.0, c, 25.0, 20.0)
        r = readback(s, 30.0)
        print(f"c={c:g}: valid={s.isValid()} n={len(s.Solids())} vol rel={abs(s.Volume()/ref-1):.2e} read c(end)={24.75/2 - r[0]:.3e} cone z={r[2]:.3e} ncone={r[3]}")
    except Exception as e:
        print(f"c={c:g}: EXC {type(e).__name__} {str(e)[:60]}")
