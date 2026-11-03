# ruff: noqa -- throwaway kernel spike, kept verbatim as Phase 32 research evidence.
"""Scan the whole ShaftParams spline space for outline degeneracy (stdlib only)."""
import math, sys
sys.path.insert(0, "/Users/half/git/halfb00t/spur/.planning/phases/32-the-shaft-solid/investigation")
import importlib.util
spec = importlib.util.spec_from_file_location("spike", "/Users/half/git/halfb00t/spur/.planning/phases/32-the-shaft-solid/investigation/32-spike.py")
sp = importlib.util.module_from_spec(spec); spec.loader.exec_module(sp)

mods = [0.5, 0.6, 0.8, 1, 1.25, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10]
worst_tip = (9e9, None); worst_root = (9e9, None); n = 0
worst_tip_rel = (9e9, None); worst_root_rel = (9e9, None); rb_above = 0
for m in mods:
    for z in range(6, 83):
        for x in (-0.05, 0.0, 0.1, 0.2, 0.3, 0.4, 0.45):
            d_b = round(m * z + 2 * x * m + 1.1 * m, 6)
            if not 3 <= d_b <= 850: continue
            n += 1
            _, xm, ra, rf, rb, psi_b = sp.basics(d_b, m, z)
            rs = max(rf, rb)
            if rb > rf: rb_above += 1
            h_tip = sp.half(ra, rb, psi_b)
            tip_chord = 2 * ra * math.sin(max(h_tip, 0))  # land chord
            h_root = sp.half(rs, rb, psi_b)
            gap = rf * (2 * math.pi / z - 2 * h_root)
            # root chord between neighbouring teeth's root points
            root_chord = 2 * rf * math.sin(max(math.pi / z - h_root, 0)) if rb <= rf else 2 * rf * math.sin(max(math.pi / z - h_root, 0))
            key = (m, z, x, d_b)
            if tip_chord / m < worst_tip_rel[0]: worst_tip_rel = (tip_chord / m, key)
            if root_chord / m < worst_root_rel[0]: worst_root_rel = (root_chord / m, key)
print("rows", n, "rows with base circle above root", rb_above)
print("min tip land chord / m", worst_tip_rel)
print("min root-arc chord / m", worst_root_rel)
