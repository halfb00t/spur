# ruff: noqa -- throwaway kernel spike, kept verbatim as Phase 32 research evidence.
import json, subprocess, sys
PY = "/Users/half/git/halfb00t/spur/.venv/bin/python"
ROW = "/Users/half/git/halfb00t/spur/.planning/phases/32-the-shaft-solid/investigation/32-row.py"
def dB(m, z, x): return round(m * z + 2 * x * m + 1.1 * m, 6)
rows = [
 dict(label="default W25x1.25x18", d_b=25.0, m=1.25, z=18, Ls=30.0, c=1.0, shank_d=25.0, Lk=20.0),
 dict(label="z6 m10 x-0.05 Ls500 Lk500", d_b=dB(10,6,-0.05), m=10, z=6, Ls=500.0, c=10.0, shank_d=850.0, Lk=500.0),
 dict(label="z82 m0.5 Ls500 Lk500", d_b=dB(0.5,82,0.45), m=0.5, z=82, Ls=500.0, c=0.5, shank_d=42.0, Lk=500.0),
 dict(label="z82 m1 Ls500 Lk500", d_b=dB(1,82,0.45), m=1, z=82, Ls=500.0, c=1.0, shank_d=84.0, Lk=500.0),
 dict(label="z82 m5 Ls500 Lk500 shank850", d_b=dB(5,82,0.45), m=5, z=82, Ls=500.0, c=5.0, shank_d=850.0, Lk=500.0),
 dict(label="z82 m10 x0.45 Ls500 Lk500 shank850 c10", d_b=dB(10,82,0.45), m=10, z=82, Ls=500.0, c=10.0, shank_d=850.0, Lk=500.0),
 dict(label="z82 m10 x-0.05 Ls500 Lk500 shank=tip c10", d_b=dB(10,82,-0.05), m=10, z=82, Ls=500.0, c=10.0, shank_d=round(dB(10,82,-0.05)-2,3), Lk=500.0),
 dict(label="z82 m10 x0.45 Ls500 no shank c0", d_b=dB(10,82,0.45), m=10, z=82, Ls=500.0, c=0.0, shank_d=850.0, Lk=0.0),
 dict(label="z82 m10 x0.45 Ls1 Lk0 c1", d_b=dB(10,82,0.45), m=10, z=82, Ls=1.0, c=1.0, shank_d=850.0, Lk=0.0),
]
only = sys.argv[1:] 
for r in rows:
    if only and not any(o in r["label"] for o in only): continue
    p = subprocess.run([PY, ROW, json.dumps(r)], capture_output=True, text=True)
    print(p.stdout.strip() or p.stderr.strip()[-400:], flush=True)
