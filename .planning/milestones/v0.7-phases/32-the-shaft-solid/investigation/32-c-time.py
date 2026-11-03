# ruff: noqa -- throwaway kernel spike, kept verbatim as Phase 32 research evidence.
import importlib.util, time
spec = importlib.util.spec_from_file_location("spike", "/Users/half/git/halfb00t/spur/.planning/phases/32-the-shaft-solid/investigation/32-spike.py")
sp = importlib.util.module_from_spec(spec); spec.loader.exec_module(sp)
for (m, z, x) in [(1.0, 82, 0.45), (10.0, 82, 0.45), (1.0, 82, -0.05)]:
    d_b = round(m * z + 2 * x * m + 1.1 * m, 6)
    _, xm, ra, rf, rb, psi_b = sp.basics(d_b, m, z)
    for c in (0.001, 0.01, 0.05, 0.2 * m, 0.5 * m, m):
        tm = {}
        s = sp.build(d_b, m, z, 30.0, round(c, 3), 2 * ra, 20.0, "fuse_cut", False, "spline", tm)
        print(f"m={m} z={z} x={x} c={c:.3f}: cut {tm['cut_last']:.2f}s fuse {tm['fuse']:.2f}s total {tm['total']:.2f}s valid={s.isValid()}")
