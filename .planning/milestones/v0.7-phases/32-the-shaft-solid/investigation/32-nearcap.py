# ruff: noqa -- throwaway kernel spike, kept verbatim as Phase 32 research evidence.
"""One chamfer size per subprocess with a 40 s wall clock: which near-cap sizes hang?"""
import subprocess, sys, json
PY = "/Users/half/git/halfb00t/spur/.venv/bin/python"
SP = "/Users/half/git/halfb00t/spur/.planning/phases/32-the-shaft-solid/investigation/32-spike.py"
CODE = '''
import importlib.util, sys, time
spec = importlib.util.spec_from_file_location("spike", %r)
sp = importlib.util.module_from_spec(spec); spec.loader.exec_module(sp)
m = 1.25; c = m + float(sys.argv[1])
t = time.perf_counter()
s = sp.build(25.0, m, 18, 30.0, c, 25.0, 20.0)
ends = [f for f in s.Faces() if f.geomType() == "PLANE" and abs(f.BoundingBox().zmax) < 1e-6 and abs(f.BoundingBox().zmin) < 1e-6]
ref = sp.volume_closed(25.0, m, 18, 30.0, min(c, m), 25.0, 20.0)
print(f"valid={s.isValid()} n={len(s.Solids())} end_faces={len(ends)} faces={len(s.Faces())} vol_rel_vs_capped={abs(s.Volume()/ref-1):.2e} t={time.perf_counter()-t:.2f}s")
''' % SP
for off in sys.argv[1:]:
    try:
        r = subprocess.run([PY, "-c", CODE, off], capture_output=True, text=True, timeout=40)
        print(f"c=m{off}: {r.stdout.strip() or r.stderr.strip()[-120:]}", flush=True)
    except subprocess.TimeoutExpired:
        print(f"c=m{off}: HANG (> 40 s, killed)", flush=True)
