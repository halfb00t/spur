"""din5480's formulas against the independent oracle and the vendor reports.

The oracle is tests/shaft_oracle.py: the basic rack and a parametric involute, no code
shared with src/spur/din5480.py (L08). The vendors are cross-checks, not the standard
(D-08); anchor rows from the copy arrive in 31-06, in their own file.
"""

import ast
from pathlib import Path

import pytest
import shaft_oracle

from spur import din5480


def test_the_shaft_oracle_imports_nothing_from_spur() -> None:
    """The oracle's value is that it computes by another road, so it may import only the
    standard library maths and the future annotations marker."""
    tree = ast.parse((Path(__file__).parent / "shaft_oracle.py").read_text())
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            imported.add(node.module)
    assert imported <= {"__future__", "math"}


def test_the_basic_dims_agree_with_the_oracle() -> None:
    m, z, x = 1.25, 18, 0.45
    reference_d = shaft_oracle.reference_diameter(m, z, x)
    assert din5480.profile_shift(reference_d, m, z) == pytest.approx(x, abs=1e-9)
    assert din5480.tip_diameter(reference_d, m) == pytest.approx(
        shaft_oracle.tip_diameter(m, z, x), abs=1e-9
    )
    assert din5480.root_diameter(m, z, x * m, din5480.H_FP) == pytest.approx(
        shaft_oracle.root_diameter(m, z, x, din5480.H_FP), abs=1e-9
    )
    assert din5480.tooth_thickness(m, x * m) == pytest.approx(
        shaft_oracle.tooth_thickness(m, z, x), abs=1e-9
    )
