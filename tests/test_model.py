import collections
import math
import struct
from collections.abc import Iterator, Sequence
from pathlib import Path

import pytest

from spur.build_errors import BuildError
from spur.calc import bore_radius, profile, recess_radii
from spur.model import (
    TESSELLATION,
    TOL,
    Quality,
    _bore_rim_edges,
    _build_checked,
    _groove_floor_edges,
    build,
    export,
)
from spur.params import GearParams

Facet = tuple[tuple[float, ...], tuple[float, ...], tuple[float, ...]]


@pytest.mark.parametrize("kw", [
    {},
    {"pressure_angle": 20},
    {"bore_flat": 0},
    {"bore_d": 0},
    {"recess_sides": "none"},
    {"recess_sides": "top"},
    {"root_fillet": 0, "recess_fillet": 0, "bore_chamfer": 0},
    {"teeth": 8, "module": 1.5, "bore_d": 3, "bore_flat": 0, "recess_sides": "none"},
    {"teeth": 40, "module": 2, "profile_shift": 0.4, "pressure_angle": 20,
     "face_width": 12, "bore_d": 12, "bore_flat": 11, "recess_depth": 4},
])
def test_builds_one_valid_solid(kw: dict[str, object]) -> None:
    p = GearParams.model_validate(kw)
    s = build(p)
    assert s.isValid()
    bb = s.BoundingBox()
    assert bb.zlen == pytest.approx(p.face_width)
    assert max(bb.xlen, bb.ylen) <= p.module * (p.teeth + 2 + 2 * p.profile_shift) + 1e-6


@pytest.mark.parametrize(("kw", "rim", "floor"), [
    pytest.param({}, collections.Counter({"CIRCLE": 2, "LINE": 2}), 4, id="d-flat-both"),
    pytest.param({"recess_sides": "top"}, collections.Counter({"CIRCLE": 2, "LINE": 2}), 2,
                 id="d-flat-top"),
    pytest.param({"recess_sides": "bottom"}, collections.Counter({"CIRCLE": 2, "LINE": 2}), 2,
                 id="d-flat-bottom"),
    pytest.param({"recess_sides": "none"}, collections.Counter({"CIRCLE": 2, "LINE": 2}), None,
                 id="d-flat-no-recess"),
    pytest.param({"bore_flat": 0}, collections.Counter({"CIRCLE": 2}), 4, id="round-both"),
    pytest.param({"bore_flat": 0, "recess_sides": "top"}, collections.Counter({"CIRCLE": 2}), 2,
                 id="round-top"),
    pytest.param({"bore_flat": 0, "recess_sides": "bottom"}, collections.Counter({"CIRCLE": 2}), 2,
                 id="round-bottom"),
    pytest.param({"bore_flat": 0, "recess_sides": "none"}, collections.Counter({"CIRCLE": 2}), None,
                 id="round-no-recess"),
    pytest.param({"bore_d": 0}, None, 4, id="no-bore"),
    pytest.param({"recess_inner_d": 1.0}, collections.Counter({"CIRCLE": 2, "LINE": 2}), 4,
                 id="d-flat-recess-at-hub-clearance"),
])
def test_each_edge_selector_picks_exactly_its_own_edges(
        kw: dict[str, object],
        rim: collections.Counter[str] | None,
        floor: int | None) -> None:
    """The exact edges each selector sees before its operator runs (REQ-edge-selection-
    proven): the bore-rim chamfer and the recess-floor fillet each pick their own edges,
    never each other's, and never the wrong count. bare_p (bore_chamfer=0,
    recess_fillet=0) is the solid each selector sees in the pipeline just before its
    operator would run -- the chamfer is the last build step, and the recess fillet only
    adds faces away from the rim. Every selector argument comes from bare_p, not the
    as-requested params: bore_chamfer feeds recess_radii()'s hub clearance, so a
    hub-clamped recess moves when the chamfer is switched off, and radii taken from the
    chamfered params would miss the bare solid's floor circles.

    d-flat-recess-at-hub-clearance is the boundary row: recess_inner_d 1.0 clamps the
    recess to its minimum hub clearance (bore_radius + MIN_WALL on the chamfer-off solid,
    4.975 mm) -- the closest a recess edge can come to the rim band -- and the rim
    selection stays exact.
    """
    bare_p = GearParams.model_validate({**kw, "bore_chamfer": 0, "recess_fillet": 0})
    bare = build(bare_p)

    rim_counter = (collections.Counter(e.geomType() for e in _bore_rim_edges(bare, bare_p))
                   if bare_p.bore_d > 0 else None)

    rr = recess_radii(bare_p, profile(bare_p).rf)
    floor_count: int | None = None
    if rr is not None:
        heights: list[float] = []
        if bare_p.recess_sides in ("both", "bottom"):
            heights.append(bare_p.recess_depth)
        if bare_p.recess_sides in ("both", "top"):
            heights.append(bare_p.face_width - bare_p.recess_depth)
        floor_edges = _groove_floor_edges(bare, rr, heights)
        floor_count = len(floor_edges)
        # Identity, not just count: a selector matching the same number of wrong-but-
        # coincidentally-equal-count edges (e.g. groove-mouth circles, which share the
        # floor circles' radii by construction) must still be caught.
        for e in floor_edges:
            assert min(abs(e.radius() - r) for r in rr) < TOL
            assert min(abs(e.startPoint().z - z) for z in heights) < TOL

    # One tuple assertion: a wrong floor count never hides behind a wrong rim count.
    assert (rim_counter, floor_count) == (rim, floor)

    if bare_p.bore_d > 0:
        rim_edges = _bore_rim_edges(bare, bare_p)
        for e in rim_edges:
            a, b = e.startPoint(), e.endPoint()
            assert min(abs(a.z), abs(a.z - bare_p.face_width)) < TOL
            assert min(abs(b.z), abs(b.z - bare_p.face_width)) < TOL
            if e.geomType() == "CIRCLE":
                assert e.radius() == pytest.approx(bore_radius(bare_p), abs=TOL)
        # Both end faces, not just "an" end face: a selector that returned both rim
        # circles from z=0 and missed z=face_width entirely would still satisfy every
        # per-edge check above. 0 for a z=0 edge, 1 for a z=face_width edge.
        faces_hit = {round(e.startPoint().z / bare_p.face_width) for e in rim_edges}
        assert faces_hit == {0, 1}


def test_a_bore_chamfer_that_selects_no_rim_edges_is_a_build_error_not_a_bare_bore(
        monkeypatch: pytest.MonkeyPatch) -> None:
    """D-15: a bound too small for the bore shape (the Phase 8 hex failure in miniature)
    must raise, not ship an unchamfered part. Patches the calc-side rim-limit function
    on the model module to a bound inside the bore -- half the rim's farthest point,
    well short of any edge. Calls _build_checked, never build(): build()'s lru_cache
    would hand back a solid built before the patch, without running the selector at all.
    """
    monkeypatch.setattr("spur.model.bore_rim_limit", lambda p: bore_radius(p) / 2)
    with pytest.raises(BuildError, match="selected no bore-rim edges") as exc_info:
        _build_checked(GearParams())
    # the catch-all must not relabel this defect as "try smaller fillets or chamfers"
    assert "try smaller" not in str(exc_info.value)


def test_a_recess_fillet_that_selects_no_floor_edges_is_a_build_error() -> None:
    """D-15: a fillet call on a solid with no groove at all -- not provoked with a
    bore-less solid, whose stock recess rim circles would fall inside the bore-rim band
    instead (planning probe) and so is not a valid zero-edge case for this selector.
    """
    rr = recess_radii(GearParams(), profile(GearParams()).rf)
    assert rr is not None, "the stock gear must have a recess"
    no_groove = build(GearParams(recess_sides="none"))
    with pytest.raises(BuildError, match="selected no groove-floor edges"):
        _groove_floor_edges(no_groove, rr, [2.0, 5.5])


def test_recess_removes_expected_volume() -> None:
    solid = build(GearParams(recess_sides="none", recess_fillet=0)).Volume()
    p = GearParams(recess_fillet=0)
    rr = recess_radii(p, profile(p).rf)
    assert rr is not None, "the stock gear must have a recess"
    r_in, r_out = rr
    ring = math.pi * (r_out ** 2 - r_in ** 2) * p.recess_depth * 2
    assert solid - build(p).Volume() == pytest.approx(ring, rel=1e-3)


def test_exports() -> None:
    p = GearParams()
    stl = export(p, "stl", "preview")
    n_triangles = int.from_bytes(stl[80:84], "little")  # binary STL header
    assert n_triangles > 1000
    assert len(stl) == 84 + 50 * n_triangles
    step = export(p, "step")
    assert step.startswith(b"ISO-10303-21;")
    assert b"MANIFOLD_SOLID_BREP" in step


def test_a_gear_too_small_for_the_stock_recess_still_builds() -> None:
    """The README's own example. The recess is narrowed to fit rather than refused, so
    the kernel must still get a sane annulus out of it."""
    solid = build(GearParams(teeth=24, module=1, pressure_angle=20, bore_flat=0))
    assert solid.isValid()
    assert len(solid.Solids()) == 1


def _stl_triangles(data: bytes) -> Iterator[Facet]:
    n = int.from_bytes(data[80:84], "little")
    assert len(data) == 84 + 50 * n, "truncated binary STL"
    for i in range(n):
        v = struct.unpack("<12fH", data[84 + 50 * i:134 + 50 * i])
        yield v[3:6], v[6:9], v[9:12]


def _closed_shell_volume(data: bytes) -> float:
    """A slicer needs a watertight mesh. A missing or flipped facet is invisible in the
    3D preview and turns up as a broken print, so assert the topology directly: no
    degenerate facet, every directed edge used once, every edge paired with its
    opposite -- then return the signed volume those checks were computed alongside, so a
    caller can compare content between two exports without a byte diff (D-08)."""
    def vertex(p: Sequence[float]) -> tuple[int, ...]:
        return tuple(round(c * 1e5) for c in p)

    directed: collections.Counter[tuple[tuple[int, ...], tuple[int, ...]]] = collections.Counter()
    volume = 0.0
    for a, b, c in _stl_triangles(data):
        ka, kb, kc = vertex(a), vertex(b), vertex(c)
        assert len({ka, kb, kc}) == 3, "degenerate facet"
        directed.update([(ka, kb), (kb, kc), (kc, ka)])
        volume += (a[0] * (b[1] * c[2] - b[2] * c[1])
                   - a[1] * (b[0] * c[2] - b[2] * c[0])
                   + a[2] * (b[0] * c[1] - b[1] * c[0])) / 6

    assert all(n == 1 for n in directed.values()), "an edge is used twice the same way"
    assert all((v, u) in directed for u, v in directed), "an edge has no opposite facet"
    return volume


def test_exported_stl_is_a_closed_consistently_oriented_shell() -> None:
    """A slicer needs a watertight mesh. A missing or flipped facet is invisible in the
    3D preview and turns up as a broken print, so assert the topology directly."""
    assert _closed_shell_volume(export(GearParams(), "stl", "preview")) > 0, "normals point inward"


def _export_in_place(p: GearParams, quality: Quality, directory: Path) -> bytes:
    """What `_write_export` did before this plan: `exportStl` called in place on a solid
    the cache never handed out, so it has never been meshed. The reference an export
    through the cache must match in content, whatever was exported from the cache before
    (D-08's content-equivalence proof)."""
    shape = _build_checked(p)
    tol, ang = TESSELLATION[quality]
    path = directory / f"{p.slug()}.stl"
    shape.exportStl(str(path), tolerance=tol, angularTolerance=ang, ascii=False, relative=False)
    return path.read_bytes()


def test_exporting_leaves_the_cached_solid_exact() -> None:
    """`_build_cached` hands every caller one object; an export must not leave a mesh on
    it -- zlen read 7.519603716332508 here before the fix (debt file)."""
    p = GearParams()
    s = build(p)
    export(p, "stl", "preview")
    export(p, "stl", "fine")
    export(p, "step")
    assert build(p) is s, "the test measures the cached object, not a rebuild"
    assert s.BoundingBox().zlen == pytest.approx(p.face_width)


def test_an_stl_export_matches_a_first_export_whatever_came_before(tmp_path: Path) -> None:
    """Content, not bytes -- OCCT export is not byte-reproducible across independently
    built solids (8/20, 06-RESEARCH.md Pitfall 1); before the fix, a preview after a fine
    export returned the fine mesh (46,278 triangles, not 9,066)."""
    p = GearParams()
    fine = export(p, "stl", "fine")
    preview = export(p, "stl", "preview")
    pairs: list[tuple[bytes, Quality]] = [(preview, "preview"), (fine, "fine")]
    for data, quality in pairs:
        reference = _export_in_place(p, quality, tmp_path)
        assert int.from_bytes(data[80:84], "little") == int.from_bytes(reference[80:84], "little")
        assert (_closed_shell_volume(data)
                == pytest.approx(_closed_shell_volume(reference), rel=1e-6))
