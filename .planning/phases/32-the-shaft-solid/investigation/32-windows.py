# ruff: noqa -- throwaway kernel spike, kept verbatim as Phase 32 research evidence.
"""Map the near-coincidence hang windows. One build per subprocess, 25 s wall clock.
argv: kind(order:radial|axial) deltas...   radial: c = m + d (cone start vs root circle)
axial: Ls = c + d with c = 1.0 (cone end plane vs the splined section's end plane)"""
import subprocess, sys
PY = "/Users/half/git/halfb00t/spur/.venv/bin/python"
SP = "/Users/half/git/halfb00t/spur/.planning/phases/32-the-shaft-solid/investigation/32-spike.py"
CODE = '''
import importlib.util, sys, time
spec = importlib.util.spec_from_file_location("spike", %r)
sp = importlib.util.module_from_spec(spec); spec.loader.exec_module(sp)
order, kind, d, Lk = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
m = 1.25
if kind == "radial":
    c, Ls = m + d, 30.0
else:
    c = 1.0; Ls = 1.0 + d
t = time.perf_counter()
s = sp.build(25.0, m, 18, Ls, c, 25.0, Lk, order)
ref = sp.volume_closed(25.0, m, 18, Ls, min(c, m), 25.0, Lk)
print(f"valid={s.isValid()} n={len(s.Solids())} faces={len(s.Faces())} vol_rel={abs(s.Volume()/ref-1):.2e} t={time.perf_counter()-t:.2f}s")
''' % SP
order, kind, lk = sys.argv[1], sys.argv[2], sys.argv[3]
for d in sys.argv[4:]:
    try:
        r = subprocess.run([PY, "-c", CODE, order, kind, d, lk], capture_output=True, text=True, timeout=25)
        print(f"{order} {kind} Lk={lk} d={d}: {r.stdout.strip() or r.stderr.strip()[-100:]}", flush=True)
    except subprocess.TimeoutExpired:
        print(f"{order} {kind} Lk={lk} d={d}: HANG (>25 s)", flush=True)
