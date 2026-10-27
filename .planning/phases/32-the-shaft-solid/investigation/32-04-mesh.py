"""Phase 32-04 mesh measurements (evidence, not shipped).

Run:  .venv/bin/python -I <this file>
The path insertion below is needed because -I drops the script directory and the cwd.

For the default shaft and W 14x2x6, at both qualities, through model.export (the path the
shipped tests use): the closed-shell mesh volume against the closed form, and the largest
vertex radius on z = 0 against ra - end_chamfer_effective.
"""

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "tests")]

import test_model  # noqa: E402
import test_shaft_model as kernel_tests  # noqa: E402

from spur import model  # noqa: E402
from spur.shaft_calc import derive_shaft  # noqa: E402
from spur.shaft_params import ShaftParams  # noqa: E402

ROWS = {
    "default": ShaftParams(),
    "W14x2x6": ShaftParams(reference_d=14.0, module=2.0, teeth=6),
}

for name, p in ROWS.items():
    dims = derive_shaft(p)
    expected = dims.tip_d / 2 - (dims.end_chamfer_effective or 0.0)
    for quality in ("preview", "fine"):
        data = model.export(p, "stl", quality)
        volume = test_model._closed_shell_volume(data)
        rel = volume / kernel_tests._closed_form(p) - 1
        end_radius = max(math.hypot(v[0], v[1]) for tri in test_model._stl_triangles(data)
                         for v in tri if abs(v[2]) < 1e-6)
        print(f"{name:8s} {quality:8s} triangles {(len(data) - 84) // 50:7d}  "
              f"volume rel {rel:+.3e}  end-face radius {end_radius:.7f} "
              f"expected {expected:.7f}  gap {abs(end_radius - expected):.3e}")
