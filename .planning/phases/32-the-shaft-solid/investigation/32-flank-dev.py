# ruff: noqa -- throwaway kernel spike, kept verbatim as Phase 32 research evidence.
"""Flank position error of the 16-point spline, measured on the built solid's end-face edges."""
import importlib.util, math
spec = importlib.util.spec_from_file_location("spike", "/Users/half/git/halfb00t/spur/.planning/phases/32-the-shaft-solid/investigation/32-spike.py")
sp = importlib.util.module_from_spec(spec); spec.loader.exec_module(sp)
import cadquery as cq
worst = (0, None)
for (m, z, x) in [(1.25, 18, 0.45), (2, 6, 0.0), (2, 6, -0.05), (0.5, 6, 0.45), (3, 22, 0.2), (1, 82, 0.1), (10, 30, -0.05), (5, 14, 0.0), (1, 8, -0.05), (10, 9, -0.05)]:
    d_b = round(m * z + 2 * x * m + 1.1 * m, 6)
    _, xm, ra, rf, rb, psi_b = sp.basics(d_b, m, z)
    s = cq.Solid.extrudeLinear(cq.Face.makeFromWires(sp.outline(d_b, m, z)), cq.Vector(0, 0, 5.0))
    pitch = 2 * math.pi / z
    dev = 0.0; n = 0
    for e in s.Edges():
        if e.geomType() != "BSPLINE": continue
        if abs(e.startPoint().z) > 1e-9 or abs(e.endPoint().z) > 1e-9: continue
        for i in range(0, 201):
            v = e.positionAt(i / 200)
            r = math.hypot(v.x, v.y); th = math.atan2(v.y, v.x)
            k = round(th / pitch); c = k * pitch
            side = th - c
            ideal = sp.half(max(r, rb), rb, psi_b)
            d = abs(abs(side) - ideal) * r
            dev = max(dev, d); n += 1
    print(f"m={m} z={z} x={x}: max flank position error {dev:.3e} mm over {n} samples ({dev/m:.2e} m)")
    if dev/m > worst[0]: worst = (dev/m, (m, z, x))
print("worst relative to m:", worst)
