# ruff: noqa -- throwaway kernel spike, kept verbatim as Phase 32 research evidence.
import resource, sys, time
from spur import model
from spur.params import GearParams
def rss():
    r = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return r / 1048576 if sys.platform == 'darwin' else r / 1024
base = rss()
p = GearParams(teeth=int(sys.argv[1]))
t = time.perf_counter()
d = model.export(p, "stl", "fine"); model.export(p, "step")
print(f"gear z={sys.argv[1]} base {base:.0f} MiB peak {rss():.0f} MiB wall {time.perf_counter()-t:.2f}s stl {len(d)}")
