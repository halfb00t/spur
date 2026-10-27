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
from test_din5480 import GRID  # noqa: E402

from spur import din5480  # noqa: E402


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


if __name__ == "__main__":
    {"angle": angle}[sys.argv[1]]()
