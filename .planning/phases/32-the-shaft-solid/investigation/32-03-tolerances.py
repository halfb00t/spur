"""Phase 32-03 tolerance measurements (evidence, not shipped).

Run:  .venv/bin/python -I <this file> angle
The path insertion below is needed because -I drops the script directory and the cwd.
"""

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "tests")]

import shaft_oracle  # noqa: E402
import test_shaft_model as kernel_tests  # noqa: E402
from test_din5480 import GRID  # noqa: E402

from spur import din5480  # noqa: E402
from spur.shaft_calc import derive_shaft  # noqa: E402
from spur.shaft_model import build_shaft  # noqa: E402
from spur.shaft_params import ShaftParams  # noqa: E402


def angle() -> None:
    """Worst |din5480.flank_half_angle - oracle.tooth_half_angle| over GRID, as the test."""
    worst, where = 0.0, ""
    for m, z, x in GRID:
        r_b = m * z * math.cos(math.radians(30.0)) / 2
        r_f = shaft_oracle.root_diameter(m, z, x, din5480.H_FP) / 2
        r_a = shaft_oracle.tip_diameter(m, z, x) / 2
        start = max(r_f, r_b)
        radii = [start + (r_a - start) * i / 8 for i in range(9)]
        if r_b > r_f:
            radii.append((r_f + r_b) / 2)
        for r in radii:
            gap = abs(din5480.flank_half_angle(m, z, x * m, r)
                      - shaft_oracle.tooth_half_angle(m, z, x, r))
            if gap > worst:
                worst, where = gap, f"m{m}-z{z}-x{x} r={r:.4f}"
    print(f"flank half-angle, din5480 vs oracle, {len(GRID)} cases: "
          f"worst {worst:.3e} rad at {where}")


def rows() -> None:
    """Per building row of tests/test_shaft_model.py: volume error against the closed form,
    the chamfer, tip and root read-backs, and for the flank rows the deviation per module."""
    named: dict[str, ShaftParams] = {
        "default": ShaftParams(),
        **kernel_tests.SHANK_ROWS,
        **kernel_tests.CHAMFER_ROWS,
        **{k: v for k, v in kernel_tests.FLANK_ROWS.items() if k != "default"},
    }
    worst_volume = 0.0
    worst_readback = 0.0
    for name, p in named.items():
        solid = build_shaft(p)
        volume = kernel_tests._volume_error(solid, p)
        chamfer = kernel_tests._chamfer_error(solid, p)
        # Section height (c + Ls)/2 is the junction itself when c == Ls: no tip or root there.
        applied = derive_shaft(p).end_chamfer_effective or 0.0
        tip_root = kernel_tests._tip_and_root_error(solid, p) if applied < p.splined_length else 0.0
        worst_volume = max(worst_volume, volume)
        worst_readback = max(worst_readback, chamfer, tip_root)
        flank = ""
        if name in kernel_tests.FLANK_ROWS:
            flank = f"  flank/m {kernel_tests._flank_error(solid, p) / p.module:.3e}"
        print(f"{name:26s} volume {volume:.3e}  chamfer {chamfer:.3e}  tip/root {tip_root:.3e}"
              f"{flank}")
    print(f"WORST volume {worst_volume:.3e}  readback {worst_readback:.3e}")


if __name__ == "__main__":
    {"angle": angle, "rows": rows}[sys.argv[1]]()
