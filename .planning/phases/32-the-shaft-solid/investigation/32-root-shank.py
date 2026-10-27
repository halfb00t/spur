# ruff: noqa -- throwaway kernel spike, kept verbatim as Phase 32 research evidence.
"""shank_d == root_d: Shape.fuse gives an invalid solid when no cone cut follows. Find what holds."""
import importlib.util, math, sys
spec = importlib.util.spec_from_file_location("spike", "/Users/half/git/halfb00t/spur/.planning/phases/32-the-shaft-solid/investigation/32-spike.py")
sp = importlib.util.module_from_spec(spec); spec.loader.exec_module(sp)
import cadquery as cq
from OCP.BRepCheck import BRepCheck_Analyzer
d_b, m, z = 25.0, 1.25, 18
root_d, tip_d = 22.25, 24.75

def body(Ls=30.0, dB=d_b, mm=m, zz=z):
    return cq.Solid.extrudeLinear(cq.Face.makeFromWires(sp.outline(dB, mm, zz)), cq.Vector(0, 0, Ls))

def trial(label, sd, fn, Ls=30.0, Lk=20.0, dB=d_b, mm=m, zz=z):
    b = body(Ls, dB, mm, zz)
    sh = cq.Solid.makeCylinder(sd / 2, Lk, cq.Vector(0, 0, Ls))
    ref = sp.volume_closed(dB, mm, zz, Ls, 0, sd, Lk)
    try:
        r = fn(b, sh)
        print(f"{label:34s} sd={sd!r:22} valid={r.isValid()!s:5} n={len(r.Solids())} rel={abs(r.Volume()/ref-1):.2e}")
    except Exception as e:
        print(f"{label:34s} sd={sd!r:22} EXC {type(e).__name__}")

variants = {
  "fuse": lambda b, s: b.fuse(s),
  "fuse(shank, body)": lambda b, s: s.fuse(b),
  "fuse glue": lambda b, s: b.fuse(s, glue=True),
  "fuse tol=1e-7": lambda b, s: b.fuse(s, tol=1e-7),
  "fuse tol=1e-6": lambda b, s: b.fuse(s, tol=1e-6),
  "fuse tol=1e-5": lambda b, s: b.fuse(s, tol=1e-5),
  "fuse + fix()": lambda b, s: b.fuse(s).fix(),
}
for sd in (root_d, math.nextafter(root_d, 0), math.nextafter(root_d, 99), root_d - 1e-9, root_d + 1e-9, root_d - 1e-6, root_d + 1e-6, tip_d):
    for k, fn in variants.items():
        if k in ("fuse",) or sd == root_d:
            trial(k, sd, fn)
    print()
