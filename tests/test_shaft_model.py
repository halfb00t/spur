"""The shaft solid's kernel rows: build_shaft against an independent closed form.

Every test that builds compares the solid's volume with tests/shaft_oracle.py's closed form,
never isValid() alone (the kernel returns an empty shape and a 3-face remnant that both say
valid) and never a pinned literal. No face count or cone-patch count is pinned: the revolve
seam splits tooth 0's patch and the tangent shanks change the topology. No row reaches a
kernel hang: a hang is a C++ call a Python signal cannot interrupt, so the guard row uses an
offset that built in 0.65 s (32-nearcap.log).
"""

import math
from typing import cast

import cadquery as cq
import pytest
import shaft_oracle

from spur import din5480, shaft_model
from spur.build_errors import BuildError
from spur.shaft_calc import derive_shaft
from spur.shaft_model import build_shaft
from spur.shaft_params import ShaftParams

# Relative volume bar against the closed form: 15x over the 864-row worst of 6.5e-6
# (32-RESEARCH) and 6x under the 6.0e-4 that a cone past the tooth height reads (32-negatives.log),
# so a silent modelling error lands outside it.
VOLUME_REL = 1e-4
# mm, applied chamfer and root and tip radii read back from the solid: measured 1.42e-13
# chamfer, 5.7e-14 root and 1.0e-7 on the cone's bounding box, which carries a ~1e-7
# tolerance (32-readback.log).
READBACK_TOL = 1e-6


def _closed_form(p: ShaftParams) -> float:
    dims = derive_shaft(p)
    return shaft_oracle.shaft_volume(
        p.module, p.teeth, din5480.profile_shift(p.reference_d, p.module, p.teeth),
        dims.root_d / 2, dims.tip_d / 2, p.splined_length, dims.end_chamfer_effective or 0.0,
        p.shank_d, p.shank_length)


def _check(p: ShaftParams) -> cq.Solid:
    """Build, assert one valid solid whose volume is the closed form's within VOLUME_REL."""
    solid = build_shaft(p)
    assert len(solid.Solids()) == 1
    assert solid.isValid()
    assert abs(solid.Volume() / _closed_form(p) - 1) <= VOLUME_REL
    return solid


def _edge_radii(edges: list[cq.Edge]) -> list[float]:
    """The radius of 21 positions along each edge."""
    return [math.hypot(v.x, v.y) for e in edges
            for v in (e.positionAt(i / 20) for i in range(21))]


def _end_face_radius(solid: cq.Solid) -> float:
    """The largest radius of the one planar face lying at z = 0."""
    ends = [f for f in solid.Faces() if f.geomType() == "PLANE"
            and abs(f.BoundingBox().zmin) <= shaft_model.TOL
            and abs(f.BoundingBox().zmax) <= shaft_model.TOL]
    assert len(ends) == 1
    return max(_edge_radii(ends[0].Edges()))


def _section_radii(solid: cq.Solid, z: float) -> tuple[float, float]:
    """(smallest, largest) radius of the solid's section at height z."""
    section = cq.Workplane("XY").add(solid).section(z)
    radii = _edge_radii(cast(cq.Shape, section.val()).Edges())
    return min(radii), max(radii)


def _cone_tops(solid: cq.Solid) -> list[float]:
    return [f.BoundingBox().zmax for f in solid.Faces() if f.geomType() == "CONE"]


def test_the_default_shaft_is_one_valid_solid_with_the_closed_form_volume() -> None:
    p = ShaftParams()
    solid = _check(p)
    box = solid.BoundingBox()
    assert box.zmin == pytest.approx(0.0, abs=READBACK_TOL)
    assert box.zmax == pytest.approx(p.splined_length + p.shank_length, abs=READBACK_TOL)
    assert box.xmax == pytest.approx(max(derive_shaft(p).tip_d / 2, p.shank_d / 2),
                                     abs=READBACK_TOL)


def test_the_default_shaft_reads_back_its_root_and_tip_from_a_section() -> None:
    """D-02: a z-section between the cone and the shank holds the printed tip and root."""
    p = ShaftParams()
    dims = derive_shaft(p)
    assert dims.end_chamfer_effective is not None
    smallest, largest = _section_radii(
        _check(p), (dims.end_chamfer_effective + p.splined_length) / 2)
    assert smallest == pytest.approx(dims.root_d / 2, abs=READBACK_TOL)
    assert largest == pytest.approx(dims.tip_d / 2, abs=READBACK_TOL)


def test_the_default_shaft_reads_back_its_applied_chamfer() -> None:
    """D-06, L28: the chamfer printed is the one on the solid, radially and axially."""
    p = ShaftParams()
    dims = derive_shaft(p)
    assert dims.end_chamfer_effective is not None
    solid = _check(p)
    assert dims.tip_d / 2 - _end_face_radius(solid) == pytest.approx(
        dims.end_chamfer_effective, abs=READBACK_TOL)
    assert max(_cone_tops(solid)) == pytest.approx(dims.end_chamfer_effective,
                                                   abs=READBACK_TOL)


def test_a_kernel_failure_is_a_shaft_modelling_defect_and_never_fillet_advice(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The gear's wrapper blames the user's fillets; a shaft has none (32-RESEARCH
    Pitfall 7)."""
    def fail(*args: object, **kwargs: object) -> cq.Solid:
        raise RuntimeError("kernel exploded")

    monkeypatch.setattr(cq.Solid, "extrudeLinear", fail)
    with pytest.raises(BuildError) as raised:
        build_shaft(ShaftParams())
    assert "modelling defect" in str(raised.value)
    assert "fillet" not in str(raised.value)
