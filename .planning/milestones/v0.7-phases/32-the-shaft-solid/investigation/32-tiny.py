# ruff: noqa -- throwaway kernel spike, kept verbatim as Phase 32 research evidence.
import importlib.util, math
spec = importlib.util.spec_from_file_location("spike", "/Users/half/git/halfb00t/spur/.planning/phases/32-the-shaft-solid/investigation/32-spike.py")
sp = importlib.util.module_from_spec(spec); spec.loader.exec_module(sp)
for c in (1e-5, 5e-6, 2e-6, 1e-6, 5e-7, 2e-7, 1e-7):
    s = sp.build(25.0, 1.25, 18, 30.0, c, 25.0, 20.0)
    ends = [f for f in s.Faces() if f.geomType() == "PLANE" and abs(f.BoundingBox().zmax) < 1e-6 and abs(f.BoundingBox().zmin) < 1e-6]
    cones = [f for f in s.Faces() if f.geomType() == "CONE"]
    ref = sp.volume_closed(25.0, 1.25, 18, 30.0, c, 25.0, 20.0)
    print(f"c={c:g}: valid={s.isValid()} nsolids={len(s.Solids())} end faces={len(ends)} cones={len(cones)} faces={len(s.Faces())} vol rel={abs(s.Volume()/ref-1):.2e}")
