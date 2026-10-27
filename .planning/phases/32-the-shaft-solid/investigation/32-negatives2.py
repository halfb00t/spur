# ruff: noqa -- throwaway kernel spike, kept verbatim as Phase 32 research evidence.
"""Fresh body per variant (32-negatives.py reused one body across booleans)."""
import importlib.util
spec = importlib.util.spec_from_file_location("spike", "/Users/half/git/halfb00t/spur/.planning/phases/32-the-shaft-solid/investigation/32-spike.py")
sp = importlib.util.module_from_spec(spec); spec.loader.exec_module(sp)
import cadquery as cq
d_b, m, z = 25.0, 1.25, 18
def fresh(): return cq.Solid.extrudeLinear(cq.Face.makeFromWires(sp.outline(d_b, m, z)), cq.Vector(0, 0, 30.0))
for label, sd in [("shank=tip 24.75", 24.75), ("shank=root 22.25", 22.25), ("between 23.5", 23.5), ("tip+1e-6", 24.750001), ("shank 25", 25.0)]:
    ref = sp.volume_closed(d_b, m, z, 30, 0, sd, 20)
    def sh(): return cq.Solid.makeCylinder(sd / 2, 20, cq.Vector(0, 0, 30))
    r1 = fresh().fuse(sh())
    r2 = fresh().fuse(sh()).clean()
    r3 = cq.Workplane("XY").add(fresh()).union(cq.Workplane("XY").add(sh())).clean().val()
    r4 = cq.Workplane("XY").add(fresh()).union(cq.Workplane("XY").add(sh()), clean=False).val()
    print(f"{label:18s} Shape.fuse valid={r1.isValid()} | fuse().clean() valid={r2.isValid()} | WP.union.clean valid={r3.isValid()} | WP.union(clean=False) valid={r4.isValid()}  (vol rel {abs(r1.Volume()/ref-1):.1e})")
