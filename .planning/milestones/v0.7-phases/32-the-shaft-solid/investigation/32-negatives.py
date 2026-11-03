# ruff: noqa -- throwaway kernel spike, kept verbatim as Phase 32 research evidence.
"""Re-prove the two negatives at real DIN proportions: Workplane.union+clean and Solid.chamfer."""
import importlib.util, math
spec = importlib.util.spec_from_file_location("spike", "/Users/half/git/halfb00t/spur/.planning/phases/32-the-shaft-solid/investigation/32-spike.py")
sp = importlib.util.module_from_spec(spec); spec.loader.exec_module(sp)
import cadquery as cq
d_b, m, z = 25.0, 1.25, 18
tip_d = 24.75
def spline(Ls=30.0):
    return cq.Solid.extrudeLinear(cq.Face.makeFromWires(sp.outline(d_b, m, z)), cq.Vector(0, 0, Ls))
for label, sd in [("shank=tip", tip_d), ("shank=tip+1e-6", tip_d + 1e-6), ("shank=between 23.5", 23.5), ("shank=25", 25.0), ("shank=root", 22.25)]:
    body = spline()
    shank = cq.Solid.makeCylinder(sd / 2, 20, cq.Vector(0, 0, 30))
    ref = sp.volume_closed(d_b, m, z, 30, 0, sd, 20)
    wp = cq.Workplane("XY").add(body).union(cq.Workplane("XY").add(shank)).clean()
    s = wp.val()
    print(f"{label:22s} Workplane.union.clean: valid={s.isValid()} nsolids={len(s.Solids())} rel={abs(s.Volume()/ref-1):.2e}")
    wp2 = cq.Workplane("XY").add(body).union(cq.Workplane("XY").add(shank), clean=False)
    s2 = wp2.val()
    print(f"{label:22s} Workplane.union(clean=False): valid={s2.isValid()} rel={abs(s2.Volume()/ref-1):.2e}")
    f = body.fuse(shank)
    print(f"{label:22s} Shape.fuse: valid={f.isValid()} rel={abs(f.Volume()/ref-1):.2e}  .clean() after: ", end="")
    try:
        g = f.clean(); print(f"valid={g.isValid()} rel={abs(g.Volume()/ref-1):.2e}")
    except Exception as e:
        print("EXC", e)
# Solid.chamfer on end-face outline edges, 1.0 (< m 1.25) and 1.5 (> m), 3.0
print("--- edge chamfer on the z=0 end face outline (no shank)")
for c in (0.5, 1.0, 1.2, 1.25, 1.3, 1.5, 3.0):
    body = spline()
    edges = [e for e in body.Edges() if abs(e.startPoint().z) < 1e-9 and abs(e.endPoint().z) < 1e-9]
    try:
        r = body.chamfer(c, None, edges)
        full = sp.volume_closed(d_b, m, z, 30, 0, 25, 0)
        print(f"c={c}: valid={r.isValid()} nsolids={len(r.Solids())} vol={r.Volume():.4f} full={full:.4f} removed={full-r.Volume():.4f}")
    except Exception as e:
        print(f"c={c}: EXC {type(e).__name__} {str(e)[:70]}")
# cone cut beyond the tooth height (cap), as a negative control
print("--- cone intersect past the cap (c > m): kernel result vs the capped closed form")
for c in (1.25, 1.5, 3.0, 12.0):
    s = sp.build(d_b, m, z, 30, c, 25.0, 20)
    ref_capped = sp.volume_closed(d_b, m, z, 30, min(c, m), 25.0, 20)
    print(f"c={c}: valid={s.isValid()} vol={s.Volume():.4f} closed-form-at-min(c,m)={ref_capped:.4f} rel={abs(s.Volume()/ref_capped-1):.2e}")
