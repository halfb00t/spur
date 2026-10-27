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
from test_din5480 import GRID
from test_model import _closed_shell_volume, _stl_triangles

from spur import din5480, model, shaft_model
from spur.build_errors import BuildError
from spur.model import Quality
from spur.params import GearParams
from spur.shaft_calc import ShaftDimensions, derive_shaft, floor_mm
from spur.shaft_model import build_shaft
from spur.shaft_params import ShaftParams

# Relative volume bar against the closed form. This file's worst row reads 1.47e-6 (W 14x2x6,
# the spline's own approximation of the involute; 22 building rows, 32-03-tolerances.log), so
# the bar is 68x over it; the 864-row sweep read 6.5e-6 (32-RESEARCH), 15x under the bar, and
# a cone past the tooth height reads 6.0e-4 (32-negatives.log), 6x over it, so a silent
# modelling error lands outside.
VOLUME_REL = 1e-4
# mm, applied chamfer and root and tip radii read back from the solid. This file's worst:
# 1.0e-7 on the cone's bounding box, which carries a ~1e-7 tolerance, 2.8e-14 on the radii
# (32-03-tolerances.log); the radial chamfer alone read 1.42e-13 (32-readback.log). 10x the
# worst.
READBACK_TOL = 1e-6
# mm of flank deviation per mm of module. This file's worst row is W 9x1x8 at 4.35e-5 per
# module, so 5e-4 is 11.5x it (the smallest of 1e-4, 2e-4, 5e-4, 1e-3 that is at least 10x).
# 32-flank-dev.log read the same 4.35e-5 for m 1, z 8 and 2.58e-5 for m 10, z 9 on its own
# rows (32-03-tolerances.log).
FLANK_BAR_PER_MODULE = 5e-4
# Relative volume bar of the STL mesh against the closed form. The mesh is inscribed, so it
# reads low. Preview worsts, 32-04-mesh.log: -1.930e-3 (default), -3.691e-3 (W 14x2x6), the
# latter 0.615 of the bar. 32-RESEARCH's -3.3e-3 row ("z6 m2") used reference_d 14.2, not
# this file's 14.0, which is why the earlier 5e-3 bar was too tight for the row measured here
# (human decision, 32-04: 6e-3).
MESH_PREVIEW_REL = 6e-3
# Fine worsts: -3.092e-4 (default), -4.920e-4 (W 14x2x6), 0.49 of the bar.
MESH_FINE_REL = 1e-3
# mm, the largest vertex radius on z = 0 against ra - end_chamfer_effective. Vertices are
# float32 in the STL; the worst gap read 4.726e-7 (32-04-mesh.log), 212x under the bar, and a
# mesh that dropped the cone reads ra, the applied chamfer (1.0 mm and 1.0 mm on these rows) away.
MESH_VERTEX_TOL = 1e-4
MESH_BARS: dict[Quality, float] = {"preview": MESH_PREVIEW_REL, "fine": MESH_FINE_REL}
MESH_ROWS: dict[str, ShaftParams] = {
    "default": ShaftParams(),
    "W14x2x6": ShaftParams(reference_d=14.0, module=2.0, teeth=6),
}


def _closed_form(p: ShaftParams) -> float:
    dims = derive_shaft(p)
    return shaft_oracle.shaft_volume(
        p.module, p.teeth, din5480.profile_shift(p.reference_d, p.module, p.teeth),
        dims.root_d / 2, dims.tip_d / 2, p.splined_length, dims.end_chamfer_effective or 0.0,
        p.shank_d, p.shank_length)


def _volume_error(solid: cq.Solid, p: ShaftParams) -> float:
    return abs(solid.Volume() / _closed_form(p) - 1)


def _check(p: ShaftParams) -> cq.Solid:
    """Build, assert one valid solid whose volume is the closed form's within VOLUME_REL,
    and whose bounding box runs from the free end to the far end of the shank."""
    solid = build_shaft(p)
    assert len(solid.Solids()) == 1
    assert solid.isValid()
    assert _volume_error(solid, p) <= VOLUME_REL
    box = solid.BoundingBox()
    widest = derive_shaft(p).tip_d / 2
    if p.shank_length > 0:
        widest = max(widest, p.shank_d / 2)
    assert box.zmin == pytest.approx(0.0, abs=READBACK_TOL)
    assert box.zmax == pytest.approx(p.splined_length + p.shank_length, abs=READBACK_TOL)
    assert box.xmax == pytest.approx(widest, abs=READBACK_TOL)
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


def _chamfer_error(solid: cq.Solid, p: ShaftParams) -> float:
    """How far the chamfer read off the solid is from the one derive_shaft prints, radially
    and axially (D-06, L28). With none printed there is no CONE face and the end face
    reaches the tip circle."""
    dims = derive_shaft(p)
    applied = dims.end_chamfer_effective or 0.0
    error = abs(dims.tip_d / 2 - _end_face_radius(solid) - applied)
    tops = _cone_tops(solid)
    if applied > 0:
        return max(error, abs(max(tops) - applied))
    assert tops == []
    return error


def _tip_and_root_error(solid: cq.Solid, p: ShaftParams) -> float:
    """The section between the cone and the shank against the printed tip and root radii."""
    dims = derive_shaft(p)
    smallest, largest = _section_radii(
        solid, ((dims.end_chamfer_effective or 0.0) + p.splined_length) / 2)
    return max(abs(smallest - dims.root_d / 2), abs(largest - dims.tip_d / 2))


def _flank_error(solid: cq.Solid, p: ShaftParams) -> float:
    """The worst distance in mm of the solid's flank from the oracle's involute.

    Every BSPLINE edge of the section between the cone and the shank, at 201 positions: a
    point's polar angle from the nearest tooth centre line against the oracle's half angle
    at its radius, times the radius. 21 positions per edge read 5x less on W 14x2x6 (7.4e-6
    per module against 3.9e-5): the spline's error peaks between its 16 interpolation points
    and a sparse sample steps over the peak (investigation/32-03-tolerances.log).
    """
    dims = derive_shaft(p)
    x = din5480.profile_shift(p.reference_d, p.module, p.teeth)
    pitch = 2 * math.pi / p.teeth
    section = cq.Workplane("XY").add(solid).section(
        ((dims.end_chamfer_effective or 0.0) + p.splined_length) / 2)
    worst = 0.0
    for edge in cast(cq.Shape, section.val()).Edges():
        if edge.geomType() != "BSPLINE":
            continue
        for i in range(201):
            v = edge.positionAt(i / 200)
            r, theta = math.hypot(v.x, v.y), math.atan2(v.y, v.x)
            off_centre = abs(theta - round(theta / pitch) * pitch)
            worst = max(worst, r * abs(off_centre - shaft_oracle.tooth_half_angle(
                p.module, p.teeth, x, r)))
    return worst


def test_the_default_shaft_is_one_valid_solid_with_the_closed_form_volume() -> None:
    _check(ShaftParams())


def test_the_default_shaft_reads_back_its_root_and_tip_from_a_section() -> None:
    """D-02: a z-section between the cone and the shank holds the printed tip and root."""
    p = ShaftParams()
    assert _tip_and_root_error(_check(p), p) <= READBACK_TOL


def test_the_default_shaft_reads_back_its_applied_chamfer() -> None:
    """D-06, L28: the chamfer printed is the one on the solid, radially and axially."""
    p = ShaftParams()
    assert derive_shaft(p).end_chamfer_effective == 1.0
    assert _chamfer_error(_check(p), p) <= READBACK_TOL


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


# The default spline (tip_d 24.75, root_d 22.25) with each shank diameter the plan names:
# equal to the tip, equal to the root, between them, a hair either side of the tip, one ulp
# above it, below the root, the bound, above the tip (the default), and no shank at all.
SHANK_ROWS: dict[str, ShaftParams] = {
    "shank-eq-tip": ShaftParams(shank_d=24.75),
    "shank-eq-root": ShaftParams(shank_d=22.25),
    "shank-between": ShaftParams(shank_d=23.5),
    "shank-tip-plus-1e-6": ShaftParams(shank_d=24.750001),
    "shank-tip-plus-1e-3": ShaftParams(shank_d=24.751),
    "shank-tip-minus-1e-9": ShaftParams(shank_d=24.749999999),
    "shank-one-ulp-above-tip": ShaftParams(shank_d=math.nextafter(24.75, math.inf)),
    "shank-below-root": ShaftParams(shank_d=20.0),
    "shank-at-the-bound": ShaftParams(shank_d=850.0),
    "shank-above-tip": ShaftParams(shank_d=25.0),
    "no-shank": ShaftParams(shank_length=0.0),
}

# Each cap of the applied chamfer (D-05, D-06), and the two ways of asking for none.
CHAMFER_ROWS: dict[str, ShaftParams] = {
    "tooth-height-cap": ShaftParams(reference_d=10.0, module=0.5, teeth=18),
    "length-cap-no-shank": ShaftParams(reference_d=70.0, module=3.0, teeth=22,
                                       splined_length=2.0006, end_chamfer=5.0,
                                       shank_length=0.0),
    "length-cap-shank": ShaftParams(reference_d=70.0, module=3.0, teeth=22,
                                    splined_length=2.0006, end_chamfer=5.0,
                                    shank_length=20.0),
    "both-caps-tie": ShaftParams(reference_d=70.0, module=3.0, teeth=22,
                                 splined_length=3.0, end_chamfer=5.0),
    "below-resolution": ShaftParams(end_chamfer=0.0004),
    "none-asked": ShaftParams(end_chamfer=0.0),
}
ENDS_ON_ROOT = {"tooth-height-cap"}


@pytest.mark.parametrize("p", SHANK_ROWS.values(), ids=SHANK_ROWS.keys())
def test_every_shank_regime_builds_with_the_closed_form_volume(p: ShaftParams) -> None:
    """D-07: a shank against the spline never changes whether the solid builds, including
    the tangent cases the cleaning step broke (32-negatives2.log)."""
    _check(p)


@pytest.mark.parametrize("name", CHAMFER_ROWS, ids=CHAMFER_ROWS.keys())
def test_every_chamfer_cap_builds_at_the_applied_size(name: str) -> None:
    """D-05, D-06: at each cap the solid carries the size derive_shaft prints, with the
    closed-form volume at that size; below the resolution it carries none."""
    p = CHAMFER_ROWS[name]
    solid = _check(p)
    assert _chamfer_error(solid, p) <= READBACK_TOL
    if name in ENDS_ON_ROOT:
        assert _end_face_radius(solid) == pytest.approx(derive_shaft(p).root_d / 2,
                                                        abs=READBACK_TOL)


@pytest.mark.parametrize("p", [ShaftParams(reference_d=14.0, module=2.0, teeth=6),
                               ShaftParams(reference_d=9.0, module=1.0, teeth=8)],
                         ids=["W14x2x6", "W9x1x8"])
def test_a_shaft_whose_base_circle_lies_above_the_root_builds(p: ShaftParams) -> None:
    """The radial line below the base circle is built only here (D-01); the row proves the
    base circle really is above the root, so it cannot silently lose the line."""
    base_radius = p.module * p.teeth * math.cos(din5480.ALPHA) / 2
    assert base_radius > derive_shaft(p).root_d / 2
    _check(p)


def test_an_82_tooth_shaft_builds_with_the_closed_form_volume() -> None:
    _check(ShaftParams(reference_d=84.0, module=1.0, teeth=82))


FLANK_ROWS: dict[str, ShaftParams] = {
    "default": ShaftParams(),
    "W14x2x6": ShaftParams(reference_d=14.0, module=2.0, teeth=6),
    "W9x1x8": ShaftParams(reference_d=9.0, module=1.0, teeth=8),
    "W105x10x9": ShaftParams(reference_d=105.0, module=10.0, teeth=9),
    "W84x1x82": ShaftParams(reference_d=84.0, module=1.0, teeth=82),
}


@pytest.mark.parametrize("p", FLANK_ROWS.values(), ids=FLANK_ROWS.keys())
def test_the_flanks_follow_the_involute_within_the_measured_bar(p: ShaftParams) -> None:
    """A spline through 16 points is not the involute; this is how far off it lands, per
    module, against the oracle's own involute."""
    assert _flank_error(_check(p), p) <= FLANK_BAR_PER_MODULE * p.module


def _with_applied_chamfer(monkeypatch: pytest.MonkeyPatch, chamfer: float) -> None:
    """Make shaft_model read `chamfer` as the applied end chamfer, whatever derive_shaft
    would print: the only way to reach a size the 0.001 lattice never produces."""
    real = derive_shaft

    def forced(p: ShaftParams) -> ShaftDimensions:
        return real(p).model_copy(update={"end_chamfer_effective": chamfer})

    monkeypatch.setattr(shaft_model, "derive_shaft", forced)


def test_a_cone_start_inside_the_root_band_is_refused_before_the_kernel_runs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A cone start 3e-7 mm off the root circle hung the kernel for over 40 s, and the CLI has
    no timeout (32-RESEARCH Pitfall 2). The offset here is 1e-5, which built in 0.65 s
    (32-nearcap.log): a missing guard fails this test instead of hanging it."""
    _with_applied_chamfer(monkeypatch, 1.25 - 1e-5)
    outlines: list[tuple[float, int]] = []
    real_outline = shaft_model._outline

    def spy(m: float, z: int, xm: float, ra: float, rf: float) -> cq.Wire:
        outlines.append((m, z))
        return real_outline(m, z, xm, ra, rf)

    monkeypatch.setattr(shaft_model, "_outline", spy)
    with pytest.raises(BuildError, match="root circle"):
        build_shaft(ShaftParams())
    assert outlines == []


def test_a_cone_past_the_tooth_height_is_refused_by_the_volume_bracket(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The cone is a valid solid at any size, so a size that eats the root core reads valid
    with a wrong volume (32-RESEARCH Pitfall 5): 10 mm on a 1.25 mm tooth, offset -8.75 from
    the root circle and so outside the band."""
    _with_applied_chamfer(monkeypatch, 10.0)
    with pytest.raises(BuildError, match="not the shape that was asked for"):
        build_shaft(ShaftParams())


def test_no_lattice_chamfer_reaches_the_root_band() -> None:
    """The guard never fires on a size derive_shaft can print: every chamfer on the 0.001 mm
    lattice, up to the tooth height, starts its cone on or a multiple of 0.0005 from the root
    circle. No kernel runs here."""
    for m, z, x in GRID:
        p = ShaftParams(reference_d=shaft_oracle.reference_diameter(m, z, x), module=m, teeth=z)
        dims = derive_shaft(p)
        ra, rf = dims.tip_d / 2, dims.root_d / 2
        steps = round(floor_mm((dims.tip_d - dims.root_d) / 2) * 1000)
        assert steps >= 1
        for k in range(1, steps + 1):
            offset = abs(ra - k / 1000 - rf)
            in_band = shaft_model.CONE_ROOT_BAND_LOW < offset < shaft_model.CONE_ROOT_BAND_HIGH
            assert not in_band, (m, z, x, k)


@pytest.mark.parametrize("p", MESH_ROWS.values(), ids=MESH_ROWS.keys())
def test_model_builds_and_exports_a_shaft_through_the_one_doorway(p: ShaftParams) -> None:
    """model.build and model.export take a ShaftParams through the one lock, solid cache and
    export path the gear uses: one valid solid with the closed-form volume, a closed STL
    shell at each quality within its bar of the closed form, and a STEP solid."""
    solid = model.build(p)
    assert len(solid.Solids()) == 1
    assert _volume_error(solid, p) <= VOLUME_REL
    for quality, bar in MESH_BARS.items():
        stl = model.export(p, "stl", quality)
        assert abs(_closed_shell_volume(stl) / _closed_form(p) - 1) <= bar, quality
    step = model.export(p, "step")
    assert step.startswith(b"ISO-10303-21;")
    assert b"MANIFOLD_SOLID_BREP" in step


@pytest.mark.parametrize("quality", MESH_BARS)
@pytest.mark.parametrize("p", MESH_ROWS.values(), ids=MESH_ROWS.keys())
def test_the_shaft_stl_carries_its_chamfer_at_the_end_face(
    p: ShaftParams, quality: Quality,
) -> None:
    """The largest vertex radius on z = 0 is the cone's small end, ra - the applied chamfer;
    a mesh that dropped the cone would read ra."""
    dims = derive_shaft(p)
    expected = dims.tip_d / 2 - (dims.end_chamfer_effective or 0.0)
    stl = model.export(p, "stl", quality)
    widest = max(math.hypot(v[0], v[1]) for tri in _stl_triangles(stl) for v in tri
                 if abs(v[2]) < 1e-6)
    assert widest == pytest.approx(expected, abs=MESH_VERTEX_TOL)


def test_exporting_leaves_the_cached_shaft_solid_exact() -> None:
    """L24, tests/test_model.py's shape: an export must not leave a mesh on the one cached
    object, or a later bounding box reads wrong."""
    p = ShaftParams()
    solid = model.build(p)
    model.export(p, "stl", "preview")
    model.export(p, "stl", "fine")
    model.export(p, "step")
    assert model.build(p) is solid, "the test measures the cached object, not a rebuild"
    assert solid.BoundingBox().zlen == pytest.approx(p.splined_length + p.shank_length)


def test_a_gear_and_a_shaft_share_the_solid_cache_as_two_entries() -> None:
    """The 4-entry bound (SPUR_SOLID_CACHE, L17) is shared by both parts; 32-05 measures
    whether a shaft entry retains more than a 199-tooth gear's."""
    model._build_cached.cache_clear()
    gear, shaft = GearParams(), ShaftParams()
    as_objects: tuple[object, object] = (gear, shaft)
    assert as_objects[0] != as_objects[1]
    built_gear, built_shaft = model.build(gear), model.build(shaft)
    assert model._build_cached.cache_info().currsize == 2
    assert model.build(gear) is built_gear
    assert model.build(shaft) is built_shaft


def test_a_shaft_kernel_failure_through_model_keeps_its_own_words(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The gear's wrapper blames the user's fillets and chamfers; a shaft reached through
    model.build must keep shaft_model's own wording."""
    def fail(*args: object, **kwargs: object) -> cq.Solid:
        raise RuntimeError("kernel exploded")

    monkeypatch.setattr(cq.Solid, "extrudeLinear", fail)
    model._build_cached.cache_clear()
    with pytest.raises(BuildError) as raised:
        model.build(ShaftParams(splined_length=31.0))
    assert "modelling defect" in str(raised.value)
    assert "fillet" not in str(raised.value)
