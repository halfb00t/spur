# ruff: noqa -- throwaway kernel spike, kept verbatim as Phase 32 research evidence.
"""Spike battery: shank regimes, chamfer caps, small z, flank representation."""
import importlib.util, math, sys, time
spec = importlib.util.spec_from_file_location("spike", "/Users/half/git/halfb00t/spur/.planning/phases/32-the-shaft-solid/investigation/32-spike.py")
sp = importlib.util.module_from_spec(spec); spec.loader.exec_module(sp)

def row(label, d_b, m, z, Ls=30.0, c=1.0, shank_d=25.0, Lk=20.0, order="fuse_cut", glue=False, flank="spline"):
    tm = {}
    try:
        s = sp.build(d_b, m, z, Ls, c, shank_d, Lk, order, glue, flank, tm)
    except Exception as e:
        print(f"{label:46s} EXC {type(e).__name__}: {str(e)[:80]}"); return
    ref = sp.volume_closed(d_b, m, z, Ls, c, shank_d, Lk)
    v = s.Volume()
    print(f"{label:46s} valid={s.isValid()!s:5} n={len(s.Solids())} faces={len(s.Faces()):4d} rel={abs(v/ref-1):.2e} t={tm['total']:.3f}s")

which = sys.argv[1]
d_b, m, z = 25.0, 1.25, 18
tip_d, root_d = 24.75, 22.25
if which == "shank":
    for order in ("fuse_cut", "cut_fuse"):
        print("order", order)
        for lab, sd in [("shank=tip", tip_d), ("shank=root", root_d), ("between", 23.5),
                        ("tip+1e-9", tip_d + 1e-9), ("tip-1e-9", tip_d - 1e-9), ("tip+1ulp", math.nextafter(tip_d, 99)),
                        ("tip-1ulp", math.nextafter(tip_d, 0)), ("tip+1e-6", tip_d + 1e-6), ("tip+1e-3", tip_d + 1e-3),
                        ("root+1e-9", root_d + 1e-9), ("root-1e-9", root_d - 1e-9), ("root-1e-3", root_d - 1e-3),
                        ("below root 10", 10.0), ("shank 1.0", 1.0), ("shank 25", 25.0), ("shank 850", 850.0)]:
            row(lab, d_b, m, z, shank_d=sd, order=order)
        row("no shank (Lk=0)", d_b, m, z, Lk=0.0, order=order)
        row("no chamfer, shank=tip", d_b, m, z, c=0.0, shank_d=tip_d, order=order)
    print("glue=True fuse_cut")
    for lab, sd in [("shank=tip", tip_d), ("tip+1e-6", tip_d + 1e-6), ("between", 23.5)]:
        row(lab, d_b, m, z, shank_d=sd, glue=True)
elif which == "chamfer":
    for lab, c in [("c=0", 0), ("c=0.05", 0.05), ("c=0.5", 0.5), ("c=1.0 (default)", 1.0), ("c=m-1e-9", m - 1e-9), ("c=m", m),
                   ("c=m-1ulp", math.nextafter(m, 0)), ("c=m+1e-9 (above cap)", m + 1e-9)]:
        row(lab, d_b, m, z, c=c)
    print("splined_length 1.0 with c=1.0 (c == Ls), shank on")
    row("Ls=1 c=1", d_b, m, z, Ls=1.0, c=1.0)
    row("Ls=1 c=1 no shank", d_b, m, z, Ls=1.0, c=1.0, Lk=0.0)
    row("Ls=1.25 c=1.25 (c=m=Ls)", d_b, m, z, Ls=1.25, c=1.25)
    row("Ls=2 c=1.25 order cut_fuse", d_b, m, z, Ls=2.0, c=1.25, order="cut_fuse")
elif which == "smallz":
    # rb above rf rows: z=6, 7, 8
    for (mm, zz, x) in [(2, 6, 0.0), (2, 6, -0.05), (3, 6, -0.05), (10, 6, -0.05), (0.5, 6, 0.45), (1, 8, -0.05), (10, 9, -0.05)]:
        d = round(mm * zz + 2 * x * mm + 1.1 * mm, 6)
        _, xm, ra, rf, rb, psi_b = sp.basics(d, mm, zz)
        row(f"m{mm} z{zz} x{x} d_B{d} rb>rf={rb>rf}", d, mm, zz, c=min(1.0, mm), shank_d=2 * ra, Ls=20.0, Lk=10.0)
elif which == "flank":
    for fl in ("spline", "poly"):
        row(f"flank={fl} default", d_b, m, z, flank=fl)
        row(f"flank={fl} z=82 m=1", 83.1, 1.0, 82, flank=fl, shank_d=82.0)
