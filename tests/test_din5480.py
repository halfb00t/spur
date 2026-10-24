"""din5480's formulas against the independent oracle and the vendor reports.

The oracle is tests/shaft_oracle.py: the basic rack and a parametric involute, no code
shared with src/spur/din5480.py (L08). The vendors are cross-checks, not the standard
(D-08); anchor rows from the copy arrive in 31-06, in their own file.
"""

import ast
import itertools
import math
from pathlib import Path

import pytest
import shaft_oracle

from spur import din5480

# 6 modules x 8 tooth counts x 4 shifts. No shift is zero: the thickness has a term in
# x*m*tan(alpha) that a zero shift hides, so the grid carries shifts away from it.
GRID: list[tuple[float, int, float]] = list(
    itertools.product(
        (0.5, 0.8, 1.25, 2, 3, 10),
        (6, 7, 14, 18, 19, 22, 38, 82),
        (-0.05, 0.1, 0.25, 0.45),
    )
)
H_FP_BOTH = (0.55, 0.60)  # the provisional value and hobbing's, so both stay covered

# Vendor cross-check, not the standard (D-08): KISSsoft report 12 Spline (DIN 5480),
# W 70.00x3.00x22x6f, https://www.kadkraft.com/wp-content/uploads/2022/11/12-Spline-DIN-5480.pdf
# Read: reference 70.00, [x*m] 0.3501, [da] 69.400, [df] 63.100 with the profile line
# 0.60 / 0.16 / 0.45 Hobbing, so this row runs at h_fP 0.60.
KISSSOFT_W70: dict[str, float] = {
    "reference_d": 70.00,
    "m": 3.0,
    "z": 22,
    "h_fp": 0.60,
    "xm": 0.3501,
    "d_a": 69.400,
    "d_f": 63.100,
}

# Vendor cross-check, not the standard (D-08): Hexagon WN2 brochure, page 2 (an embedded
# image), https://www.hexagon.de/pdf/wn2_d.pdf, W 120 x 3 x 38 x 8f.
# Read: hfp/m 0.55, da1 119,40, df1 113,40, evmin = e2 = s1 = 6,271 (the nominal thickness).
HEXAGON_W120: dict[str, float] = {
    "reference_d": 120.0,
    "m": 3.0,
    "z": 38,
    "h_fp": 0.55,
    "s": 6.271,
    "d_a": 119.40,
    "d_f": 113.40,
}


def _case_id(case: tuple[float, int, float]) -> str:
    m, z, x = case
    return f"m{m}-z{z}-x{x}"


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


@pytest.mark.parametrize("case", GRID, ids=_case_id)
def test_the_shift_inverts_the_oracle_reference_diameter(
    case: tuple[float, int, float],
) -> None:
    m, z, x = case
    reference_d = shaft_oracle.reference_diameter(m, z, x)
    assert din5480.profile_shift(reference_d, m, z) == pytest.approx(x, abs=1e-9)


@pytest.mark.parametrize("case", GRID, ids=_case_id)
def test_the_basic_dims_agree_with_the_oracle(case: tuple[float, int, float]) -> None:
    m, z, x = case
    reference_d = shaft_oracle.reference_diameter(m, z, x)
    assert din5480.tip_diameter(reference_d, m) == pytest.approx(
        shaft_oracle.tip_diameter(m, z, x), abs=1e-9
    )
    for h_fp in H_FP_BOTH:
        assert din5480.root_diameter(m, z, x * m, h_fp) == pytest.approx(
            shaft_oracle.root_diameter(m, z, x, h_fp), abs=1e-9
        )
    assert din5480.tooth_thickness(m, x * m) == pytest.approx(
        shaft_oracle.tooth_thickness(m, z, x), abs=1e-9
    )


@pytest.mark.parametrize("case", GRID, ids=_case_id)
def test_the_basic_dims_order_root_below_pitch_below_tip(
    case: tuple[float, int, float],
) -> None:
    """The root circle never touches the pitch circle and the tip never falls inside it."""
    m, z, x = case
    reference_d = shaft_oracle.reference_diameter(m, z, x)
    tip = din5480.tip_diameter(reference_d, m)
    for h_fp in H_FP_BOTH:
        assert din5480.root_diameter(m, z, x * m, h_fp) < m * z < tip


def test_the_shift_term_is_the_addendum_plus_half_the_tip_offset(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """SHIFT_TERM and H_FP read alike at 0.55 and are different quantities: the copy's
    h_fP, likely 0.60 for hobbing, must never move the shift (31-RESEARCH Pitfall 1)."""
    assert din5480.SHIFT_TERM == 0.55
    assert din5480.ADDENDUM_FACTOR == 0.45
    assert din5480.TIP_DIAMETER_OFFSET == 0.2
    before = din5480.profile_shift(25.0, 1.25, 18)
    monkeypatch.setattr(din5480, "H_FP", 0.60)
    assert din5480.SHIFT_TERM == 0.55
    assert din5480.profile_shift(25.0, 1.25, 18) == before


def test_the_basic_dims_match_the_vendor_cross_checks() -> None:
    """Vendor cross-checks, not the standard: each is compared at its own print precision,
    and the oracle's 1e-9 is never loosened to meet a vendor."""
    k = KISSSOFT_W70
    k_m, k_z = k["m"], int(k["z"])
    k_x = din5480.profile_shift(k["reference_d"], k_m, k_z)
    assert din5480.tip_diameter(k["reference_d"], k_m) == pytest.approx(k["d_a"], abs=5e-4)
    assert din5480.root_diameter(k_m, k_z, k_x * k_m, k["h_fp"]) == pytest.approx(
        k["d_f"], abs=5e-4
    )
    # The formula gives x*m = 0.35 exactly. KISSsoft prints 0.3501 because it rounds x to
    # 0.1167 before multiplying by m (31-RESEARCH Pitfall 7), a 1e-4 print artefact.
    assert k_x * k_m == pytest.approx(k["xm"], abs=2e-4)

    h = HEXAGON_W120
    h_m, h_z = h["m"], int(h["z"])
    h_x = din5480.profile_shift(h["reference_d"], h_m, h_z)
    assert din5480.tip_diameter(h["reference_d"], h_m) == pytest.approx(h["d_a"], abs=5e-3)
    assert din5480.root_diameter(h_m, h_z, h_x * h_m, h["h_fp"]) == pytest.approx(
        h["d_f"], abs=5e-3
    )
    assert din5480.tooth_thickness(h_m, h_x * h_m) == pytest.approx(h["s"], abs=5e-4)


def test_the_oracle_refuses_a_mutated_shift_term() -> None:
    """A shift term of 0.5 in place of 0.55 moves x by 0.05 on every grid case."""
    for m, z, x in GRID:
        reference_d = shaft_oracle.reference_diameter(m, z, x)
        mutated = (reference_d - z * m) / (2 * m) - 0.5
        assert abs(mutated - x) > 1e-3


def test_the_oracle_refuses_a_mutated_thickness() -> None:
    """A thickness built with sin in place of tan disagrees with the oracle somewhere.

    The two differ by 2*xm*(tan - sin), so every x = 0 case agrees and cannot see this
    mutation. That is why the grid carries shifts away from zero.
    """

    def with_sin(m: float, xm: float) -> float:
        return math.pi * m / 2 + 2 * xm * math.sin(din5480.ALPHA)

    assert with_sin(2.0, 0.0) == pytest.approx(
        shaft_oracle.tooth_thickness(2.0, 18, 0.0), abs=1e-9
    )
    assert any(
        abs(with_sin(m, x * m) - shaft_oracle.tooth_thickness(m, z, x)) > 1e-3
        for m, z, x in GRID
    )
