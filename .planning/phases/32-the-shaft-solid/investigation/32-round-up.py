# ruff: noqa -- throwaway kernel spike, kept verbatim as Phase 32 research evidence.
"""c = round(Ls, 3) rounds above Ls: the realistic way to land at d = Ls - c < 0."""
import importlib.util
spec = importlib.util.spec_from_file_location("spike", "/Users/half/git/halfb00t/spur/.planning/phases/32-the-shaft-solid/investigation/32-spike.py")
sp = importlib.util.module_from_spec(spec); spec.loader.exec_module(sp)
for Ls in (2.0006, 2.0004, 5.0007, 1.2504):
    c = round(Ls, 3)
    for Lk in (0.0, 20.0):
        s = sp.build(25.0, 1.25, 18, Ls, min(c, 1.25), 25.0, Lk) if False else sp.build(25.0, 5.0, 18, Ls, c, 25.0, Lk) if False else None
for Ls in (2.0006, 5.0007, 2.0004):
    # module 10 so the tooth cap does not bind: d_B = 10*(18+1.1+0.9) = 200
    c = round(Ls, 3)
    for Lk in (0.0, 20.0):
        s = sp.build(200.0, 10.0, 18, Ls, c, 180.0, Lk)
        ref = sp.volume_closed(200.0, 10.0, 18, Ls, min(c, Ls), 180.0, Lk)
        print(f"Ls={Ls} c=round(Ls,3)={c} (d={Ls-c:+.1e}) Lk={Lk}: valid={s.isValid()} nsolids={len(s.Solids())} faces={len(s.Faces())} vol rel (vs c capped at Ls)={abs(s.Volume()/ref-1):.2e}")
