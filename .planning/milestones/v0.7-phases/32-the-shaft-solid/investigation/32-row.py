# ruff: noqa -- throwaway kernel spike, kept verbatim as Phase 32 research evidence.
"""One sweep row in a fresh process: build, STL preview+fine, STEP, peak RSS. argv[1] = json."""
import importlib.util, json, math, resource, sys, tempfile, time
from pathlib import Path
spec = importlib.util.spec_from_file_location("spike", str(Path(__file__).with_name("32-spike.py")))
sp = importlib.util.module_from_spec(spec); spec.loader.exec_module(sp)

def rss_mib():
    r = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return r / 1048576 if sys.platform == "darwin" else r / 1024

a = json.loads(sys.argv[1])
base = rss_mib()
t0 = time.perf_counter()
tm = {}
s = sp.build(a["d_b"], a["m"], a["z"], a["Ls"], a["c"], a["shank_d"], a["Lk"], "fuse_cut", False, "spline", tm)
build = time.perf_counter() - t0
valid = s.isValid(); nsol = len(s.Solids())
ref = sp.volume_closed(a["d_b"], a["m"], a["z"], a["Ls"], a["c"], a["shank_d"], a["Lk"])
rel = abs(s.Volume() / ref - 1)
out = {"label": a["label"], "base_mib": round(base), "build_s": round(build, 3), **{k: round(v, 3) for k, v in tm.items() if k != "total"},
       "valid": valid, "nsolids": nsol, "faces": len(s.Faces()), "vol_rel": f"{rel:.2e}"}
with tempfile.TemporaryDirectory() as d:
    for q, (tol, ang) in {"preview": (0.08, 0.5), "fine": (0.01, 0.1)}.items():
        p = Path(d) / f"x_{q}.stl"
        t = time.perf_counter()
        s.copy().exportStl(str(p), tolerance=tol, angularTolerance=ang, ascii=False, relative=False)
        out[f"stl_{q}_s"] = round(time.perf_counter() - t, 3)
        b = p.stat().st_size
        out[f"stl_{q}_bytes"] = b
        out[f"stl_{q}_tris"] = (b - 84) // 50
    p = Path(d) / "x.step"
    t = time.perf_counter(); s.exportStep(str(p)); out["step_s"] = round(time.perf_counter() - t, 3)
    out["step_bytes"] = p.stat().st_size
out["worst_request_s"] = round(build + max(out["stl_fine_s"], out["step_s"]), 3)
out["peak_rss_mib"] = round(rss_mib())
print(json.dumps(out))
