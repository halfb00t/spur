# ruff: noqa -- throwaway kernel spike, kept verbatim as Phase 32 research evidence.
import importlib.util, struct, tempfile, collections
from pathlib import Path
spec = importlib.util.spec_from_file_location("spike", "/Users/half/git/halfb00t/spur/.planning/phases/32-the-shaft-solid/investigation/32-spike.py")
sp = importlib.util.module_from_spec(spec); spec.loader.exec_module(sp)
def shell(data):
    n = int.from_bytes(data[80:84], "little"); assert len(data) == 84 + 50 * n
    directed = collections.Counter(); vol = 0.0
    key = lambda p: tuple(round(c * 1e5) for c in p)
    for i in range(n):
        v = struct.unpack("<12fH", data[84 + 50 * i:134 + 50 * i]); a, b, c = v[3:6], v[6:9], v[9:12]
        ka, kb, kc = key(a), key(b), key(c)
        assert len({ka, kb, kc}) == 3, "degenerate"
        directed.update([(ka, kb), (kb, kc), (kc, ka)])
        vol += (a[0]*(b[1]*c[2]-b[2]*c[1]) - a[1]*(b[0]*c[2]-b[2]*c[0]) + a[2]*(b[0]*c[1]-b[1]*c[0])) / 6
    assert all(v == 1 for v in directed.values()) and all((v, u) in directed for u, v in directed)
    return vol
for label, args in [("default", (25.0, 1.25, 18, 30.0, 1.0, 25.0, 20.0)), ("z6 m2", (14.2, 2, 6, 20.0, 2.0, 2*(14.2-0.4)/2, 10.0)), ("z82 m1", (83.1, 1.0, 82, 30.0, 1.0, 84.0, 20.0))]:
    s = sp.build(*args)
    ref = sp.volume_closed(*args)
    for q, (tol, ang) in {"preview": (0.08, 0.5), "fine": (0.01, 0.1)}.items():
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "a.stl"; s.copy().exportStl(str(p), tolerance=tol, angularTolerance=ang, ascii=False, relative=False)
            v = shell(p.read_bytes())
        print(f"{label:8s} {q:8s} closed shell OK, mesh volume / closed form - 1 = {v/ref-1:+.3e}")
