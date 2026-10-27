# ruff: noqa -- throwaway kernel spike, kept verbatim as Phase 32 research evidence.
"""Cap-case sweep: c = round(min(request, cap, Ls), 3) over m x z x x, with four shank regimes.
Each build runs in its own subprocess (a kernel hang cannot be interrupted in-process) with a
60 s wall clock; 8 at a time. Prints one line per failure and a summary."""
import concurrent.futures as cf, json, math, subprocess, sys, time
PY = "/Users/half/git/halfb00t/spur/.venv/bin/python"
SP = "/Users/half/git/halfb00t/spur/.planning/phases/32-the-shaft-solid/investigation/32-spike.py"
CODE = '''
import importlib.util, json, sys, time
spec = importlib.util.spec_from_file_location("spike", %r)
sp = importlib.util.module_from_spec(spec); spec.loader.exec_module(sp)
a = json.loads(sys.argv[1])
t = time.perf_counter()
s = sp.build(a["d_b"], a["m"], a["z"], a["Ls"], a["c"], a["shank_d"], a["Lk"], a.get("order", "fuse_cut"))
ref = sp.volume_closed(a["d_b"], a["m"], a["z"], a["Ls"], a["c"], a["shank_d"], a["Lk"])
print(json.dumps(dict(valid=s.isValid(), n=len(s.Solids()), rel=abs(s.Volume()/ref-1), t=time.perf_counter()-t)))
''' % SP
sys.path.insert(0, "/Users/half/git/halfb00t/spur/.planning/phases/32-the-shaft-solid/investigation")
import importlib.util
spec = importlib.util.spec_from_file_location("spike", SP); sp = importlib.util.module_from_spec(spec); spec.loader.exec_module(sp)

def cases(order):
    for m in (0.5, 0.8, 1.0, 1.25, 2.0, 3.0, 5.0, 8.0, 10.0):
        for z in (6, 7, 9, 14, 22, 40, 60, 82):
            for x in (-0.05, 0.1, 0.45):
                d_b = round(m * z + 2 * x * m + 1.1 * m, 6)
                if not 3 <= d_b <= 850: continue
                _, xm, ra, rf, rb, psi_b = sp.basics(d_b, m, z)
                cap = ra - rf
                for req in (10.0,):
                    Ls = 12.0
                    c = round(min(req, cap, Ls), 3)
                    for lab, sd, Lk in (("noshank", 25.0, 0.0), ("tip", 2 * ra, 8.0), ("root", 2 * rf, 8.0), ("big", 2 * ra + 5, 8.0)):
                        yield dict(label=f"m{m} z{z} x{x} {lab}", d_b=d_b, m=m, z=z, Ls=Ls, c=c, shank_d=sd, Lk=Lk, order=order,
                                   delta=ra - c - rf)

def run(a):
    try:
        r = subprocess.run([PY, "-c", CODE, json.dumps(a)], capture_output=True, text=True, timeout=60)
        return a, json.loads(r.stdout.strip().splitlines()[-1]) if r.stdout.strip() else {"err": r.stderr[-150:]}
    except subprocess.TimeoutExpired:
        return a, {"hang": True}

order = sys.argv[1]
rows = list(cases(order))
t0 = time.time(); bad = 0; worst = 0.0; worst_t = 0.0; neg = 0
with cf.ThreadPoolExecutor(8) as ex:
    for a, r in ex.map(run, rows):
        if "rel" in r:
            worst = max(worst, r["rel"]); worst_t = max(worst_t, r["t"])
            if a["delta"] < -1e-9: neg += 1
        if not r.get("valid", False) or r.get("n") != 1 or r.get("rel", 1) > 1e-4:
            bad += 1; print("BAD", a["label"], f"c={a['c']}", f"delta={a['delta']:.1e}", r, flush=True)
print(f"order={order} rows={len(rows)} bad={bad} worst_rel={worst:.2e} worst_t={worst_t:.2f}s rows_with_cone_start_inside_root={neg} wall={time.time()-t0:.0f}s")
