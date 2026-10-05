import collections
import functools
import math
import struct
from collections.abc import Iterator, Sequence
from pathlib import Path

import cadquery as cq
import pytest

from spur.build_errors import BuildError
from spur.calc import (
    MIN_WALL,
    bore_mouth_limit,
    bore_radius,
    bore_rim_limit,
    derive,
    hex_cells,
    keyway_width_effective,
    profile,
    recess_radii,
    spoke_fillet_effective,
    tip_chamfer_effective,
)
from spur.model import (
    TESSELLATION,
    TOL,
    Quality,
    _body,
    _bore_rim_edges,
    _build_checked,
    _fillet_corner,
    _groove_floor_edges,
    _shape_of,
    _tip_edges,
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
    {"bore_hex": 6},
    {"bore_hex": 12.7, "bore_d": 0, "bore_flat": 0},
    {"keyway_width": 3, "keyway_depth": 1.4},
    {"keyway_width": 3, "keyway_depth": 1.4, "bore_flat": 0},
    {"keyway_width": 3, "keyway_depth": 1.4, "bore_chamfer": 0, "recess_sides": "none"},
    {"tip_chamfer": 0.4},
    {"tip_chamfer": 3},  # capped to 1.75 (pitch circle)
    # capped to 2.937 (involute flank, D-04) -- without that third cap term this link
    # would carry the analytic caps' c=3 straight to the kernel and fail (10-01).
    {"tip_chamfer": 3, "profile_shift": 1.0, "pressure_angle": 14.5},
    {"tip_chamfer": 0.4, "keyway_width": 3, "keyway_depth": 1.4, "bore_flat": 0},
    {"hole_count": 6, "hole_d": 4, "hole_circle_d": 20},
    {"spoke_count": 4, "spoke_width": 2, "hub_d": 12, "rim_wall": 1, "spoke_fillet": 1},
    # Sharp corners (spoke_fillet 0) and the N=1 "C-shaped sector" case (D-02, D-03).
    {"spoke_count": 4, "spoke_width": 2, "hub_d": 12, "rim_wall": 1},
    {"spoke_count": 1, "spoke_width": 2, "hub_d": 12, "rim_wall": 1, "spoke_fillet": 1},
    {"hex_cell": 3, "hex_wall": 1},
])
def test_builds_one_valid_solid(kw: dict[str, object]) -> None:
    p = GearParams.model_validate(kw)
    s = build(p)
    assert s.isValid()
    bb = s.BoundingBox()
    assert bb.zlen == pytest.approx(p.face_width)
    assert max(bb.xlen, bb.ylen) <= p.module * (p.teeth + 2 + 2 * p.profile_shift) + 1e-6


@pytest.mark.parametrize(("kw", "rim", "floor", "tip"), [
    pytest.param({}, collections.Counter({"CIRCLE": 2, "LINE": 2}), 4, 38, id="d-flat-both"),
    pytest.param({"recess_sides": "top"}, collections.Counter({"CIRCLE": 2, "LINE": 2}), 2, 38,
                 id="d-flat-top"),
    pytest.param({"recess_sides": "bottom"}, collections.Counter({"CIRCLE": 2, "LINE": 2}), 2, 38,
                 id="d-flat-bottom"),
    pytest.param({"recess_sides": "none"}, collections.Counter({"CIRCLE": 2, "LINE": 2}), None, 38,
                 id="d-flat-no-recess"),
    pytest.param({"bore_flat": 0}, collections.Counter({"CIRCLE": 2}), 4, 38, id="round-both"),
    pytest.param({"bore_flat": 0, "recess_sides": "top"}, collections.Counter({"CIRCLE": 2}), 2, 38,
                 id="round-top"),
    pytest.param({"bore_flat": 0, "recess_sides": "bottom"}, collections.Counter({"CIRCLE": 2}), 2,
                 38, id="round-bottom"),
    pytest.param({"bore_flat": 0, "recess_sides": "none"}, collections.Counter({"CIRCLE": 2}), None,
                 38, id="round-no-recess"),
    pytest.param({"bore_d": 0}, None, 4, 38, id="no-bore"),
    pytest.param({"recess_inner_d": 1.0}, collections.Counter({"CIRCLE": 2, "LINE": 2}), 4, 38,
                 id="d-flat-recess-at-hub-clearance"),
    pytest.param({"bore_hex": 6}, collections.Counter({"LINE": 12}), 4, 38, id="hex-both"),
    pytest.param({"bore_hex": 6, "recess_sides": "top"}, collections.Counter({"LINE": 12}), 2, 38,
                 id="hex-top"),
    pytest.param({"bore_hex": 6, "recess_sides": "bottom"}, collections.Counter({"LINE": 12}), 2,
                 38, id="hex-bottom"),
    pytest.param({"bore_hex": 6, "recess_sides": "none"}, collections.Counter({"LINE": 12}), None,
                 38, id="hex-no-recess"),
    pytest.param({"bore_hex": 6, "bore_d": 0}, collections.Counter({"LINE": 12}), 4, 38,
                 id="hex-no-round-bore"),
    pytest.param({"bore_hex": 6, "recess_inner_d": 1.0}, collections.Counter({"LINE": 12}), 4, 38,
                 id="hex-recess-at-hub-clearance"),
    pytest.param({"bore_hex": 12.7}, collections.Counter({"LINE": 12}), 4, 38,
                 id="hex-wider-than-round-bore"),
    pytest.param({"keyway_width": 3, "keyway_depth": 1.4},
                 collections.Counter({"CIRCLE": 2, "LINE": 2}), 4, 38, id="keyway-d-flat-both"),
    pytest.param({"keyway_width": 3, "keyway_depth": 1.4, "recess_sides": "top"},
                 collections.Counter({"CIRCLE": 2, "LINE": 2}), 2, 38, id="keyway-d-flat-top"),
    pytest.param({"keyway_width": 3, "keyway_depth": 1.4, "recess_sides": "bottom"},
                 collections.Counter({"CIRCLE": 2, "LINE": 2}), 2, 38, id="keyway-d-flat-bottom"),
    pytest.param({"keyway_width": 3, "keyway_depth": 1.4, "recess_sides": "none"},
                 collections.Counter({"CIRCLE": 2, "LINE": 2}), None, 38,
                 id="keyway-d-flat-no-recess"),
    pytest.param({"keyway_width": 3, "keyway_depth": 1.4, "bore_flat": 0},
                 collections.Counter({"CIRCLE": 2}), 4, 38, id="keyway-round-both"),
    pytest.param({"keyway_width": 3, "keyway_depth": 1.4, "bore_flat": 0,
                  "recess_sides": "top"}, collections.Counter({"CIRCLE": 2}), 2, 38,
                 id="keyway-round-top"),
    pytest.param({"keyway_width": 3, "keyway_depth": 1.4, "bore_flat": 0,
                  "recess_sides": "bottom"}, collections.Counter({"CIRCLE": 2}), 2, 38,
                 id="keyway-round-bottom"),
    pytest.param({"keyway_width": 3, "keyway_depth": 1.4, "bore_flat": 0,
                  "recess_sides": "none"}, collections.Counter({"CIRCLE": 2}), None, 38,
                 id="keyway-round-no-recess"),
    pytest.param({"keyway_width": 3, "keyway_depth": 1.4, "recess_inner_d": 1.0},
                 collections.Counter({"CIRCLE": 2, "LINE": 2}), 4, 38,
                 id="keyway-recess-at-hub-clearance"),
    pytest.param({"keyway_width": 3, "keyway_depth": 5},
                 collections.Counter({"CIRCLE": 2, "LINE": 2}), 4, 38,
                 id="keyway-deep-recess-narrowed"),
    pytest.param({"keyway_width": 3, "keyway_depth": 9},
                 collections.Counter({"CIRCLE": 2, "LINE": 2}), None, 38,
                 id="keyway-recess-dropped"),
    pytest.param({"teeth": 200}, collections.Counter({"CIRCLE": 2, "LINE": 2}), 4, 400,
                 id="teeth-200"),
    pytest.param({"teeth": 200, "module": 0.2, "backlash": 0.07},
                 collections.Counter({"CIRCLE": 2, "LINE": 2}), 4, 400, id="module-0.2"),
])
def test_each_edge_selector_picks_exactly_its_own_edges(
        monkeypatch: pytest.MonkeyPatch,
        kw: dict[str, object],
        rim: collections.Counter[str] | None,
        floor: int | None,
        tip: int) -> None:
    """The exact edges each selector sees before its operator runs (REQ-edge-selection-
    proven): the bore-rim chamfer and the recess-floor fillet each pick their own edges,
    never each other's, and never the wrong count. bare_p (bore_chamfer=0,
    recess_fillet=0) is the solid each selector sees in the pipeline just before its
    operator would run -- the chamfer is the last step before the keyway slot, and the
    recess fillet only adds faces away from the rim. Every selector argument comes from
    bare_p, not the as-requested params: bore_chamfer feeds recess_radii()'s hub
    clearance, so a hub-clamped recess moves when the chamfer is switched off, and radii
    taken from the chamfered params would miss the bare solid's floor circles.

    _cut_keyway is patched out (a no-op) and the solid is built with _build_checked,
    bypassing build()'s lru_cache, because the slot does not exist when the selector
    runs (D-06): on the finished keyed solid the slot splits each rim arc (planning read
    C4 L2 / C4 instead of C2 L2 / C2). For rows with no keyway the patched step is the
    real step's own no-op.

    d-flat-recess-at-hub-clearance is the boundary row: recess_inner_d 1.0 clamps the
    recess to its minimum hub clearance (bore_radius + MIN_WALL on the chamfer-off solid,
    4.975 mm) -- the closest a recess edge can come to the rim band -- and the rim
    selection stays exact. The hex rows are Phase 7's selector shown on real geometry
    (ROADMAP Phase 8 SC1). The keyway rows prove SC4 as amended, the pre-keyway count for
    round and D-flat with a keyway (D-07).

    The tip column is read on bare_p's solid (Phase 10, D-13). The tip arcs are
    _outline's own edges at ra, and the rim chamfer, the floor fillet and the keyway all
    sit inside the root circle, so the tip selector never overlaps them: every existing
    row gets 38 (2 x 19 teeth). teeth-200 and module-0.2 are D-13's extremes: 400 arcs
    in one selection, and the finest tips the model allows (backlash 0.07; 0.08 is
    refused). The real pipeline, with a chamfer, the fillets and a keyway all present, is
    observed in test_the_tip_chamfer_takes_exactly_the_tip_arcs_in_the_real_pipeline.
    """
    monkeypatch.setattr("spur.model._cut_keyway", lambda solid, _p: solid)
    bare_p = GearParams.model_validate({**kw, "bore_chamfer": 0, "recess_fillet": 0})
    bare = _build_checked(bare_p)

    # The gate reads the shape-independent rim extent, not the round diameter: a hex
    # with a zero round bore still has a bore.
    rim_counter = (collections.Counter(e.geomType() for e in _bore_rim_edges(bare, bare_p))
                   if bore_rim_limit(bare_p) > 0 else None)

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

    tips = _tip_edges(bare, profile(bare_p).ra, bare_p.face_width)
    for e in tips:
        assert e.geomType() == "CIRCLE"
        assert e.radius() == pytest.approx(profile(bare_p).ra, abs=TOL)
    assert (collections.Counter(round(e.startPoint().z / bare_p.face_width) for e in tips)
            == {0: bare_p.teeth, 1: bare_p.teeth})

    # One tuple assertion: a wrong floor or tip count never hides behind a wrong rim count.
    assert (rim_counter, floor_count, len(tips)) == (rim, floor, tip)

    if bore_rim_limit(bare_p) > 0:
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


def test_a_non_body_shape_in_the_build_pipeline_is_named_as_a_modelling_defect() -> None:
    """The message names the invariant, not a field, so a user never reads the catch-all's
    "try smaller fillets or chamfers" for a defect they did not cause (D-03). The whole
    string is compared with ==, not match=: match is a regex search, and a prefix cannot
    see a wrong suffix (10-REVIEW CR-01). A Face is a Shape without Mixin3D, so no kernel
    solid is built.
    """
    with pytest.raises(BuildError) as exc_info:
        _body(cq.Face.makePlane(1, 1))
    assert str(exc_info.value) == (
        "Geometry kernel returned a Face where a solid body was expected: "
        "a modelling defect in the build pipeline, not a parameter problem.")


def test_a_workplane_value_that_is_not_a_shape_is_named_as_a_modelling_defect() -> None:
    """Same message and same reasons as the _body test. An empty Workplane's val() is the
    plane's origin, a Vector, so no kernel solid is built to reach the refusal.
    """
    with pytest.raises(BuildError) as exc_info:
        _shape_of(cq.Workplane("XY"))
    assert str(exc_info.value) == (
        "Geometry kernel returned a Vector where a solid body was expected: "
        "a modelling defect in the build pipeline, not a parameter problem.")


# Row sets used below (11-CONTEXT.md <interfaces>): the same links 11-03/11-04/11-05's
# own tracer tests cut. SPOKES' hub_d 13.2 (not 12) is wide enough to clear the keyed
# round bore's mouth (the keyway floor corner, 6.179 mm) as well as the plain, D-flat
# and hex mouths, so one dict works on every bore shape (planning probe 2026-09-29).
HOLES: dict[str, float] = {"hole_count": 6, "hole_d": 4, "hole_circle_d": 20}
SPOKES = {"spoke_count": 4, "spoke_width": 2, "hub_d": 13.2, "rim_wall": 1, "spoke_fillet": 1}
CELLS: dict[str, float] = {"hex_cell": 3, "hex_wall": 1}


@pytest.mark.parametrize(("kw", "rim", "floor", "tip"), [
    # Each pattern on each bore shape, both recesses (12 rows): rim and floor keep the
    # no-cutout matrix's own counts (test_each_edge_selector_picks_exactly_its_own_edges)
    # because both selectors run inside _cut_bore/_cut_face_recesses, before _cut_body
    # in _build -- these rows prove it on the real pipeline with a cutout present,
    # rather than assume it from the no-cutout matrix.
    pytest.param({**HOLES}, collections.Counter({"CIRCLE": 2, "LINE": 2}), 4, 38,
                 id="d-flat-holes"),
    pytest.param({**SPOKES}, collections.Counter({"CIRCLE": 2, "LINE": 2}), 4, 38,
                 id="d-flat-spokes"),
    pytest.param({**CELLS}, collections.Counter({"CIRCLE": 2, "LINE": 2}), 4, 38,
                 id="d-flat-cells"),
    pytest.param({**HOLES, "bore_flat": 0}, collections.Counter({"CIRCLE": 2}), 4, 38,
                 id="round-holes"),
    pytest.param({**SPOKES, "bore_flat": 0}, collections.Counter({"CIRCLE": 2}), 4, 38,
                 id="round-spokes"),
    pytest.param({**CELLS, "bore_flat": 0}, collections.Counter({"CIRCLE": 2}), 4, 38,
                 id="round-cells"),
    pytest.param({**HOLES, "bore_hex": 6}, collections.Counter({"LINE": 12}), 4, 38,
                 id="hex-holes"),
    pytest.param({**SPOKES, "bore_hex": 6}, collections.Counter({"LINE": 12}), 4, 38,
                 id="hex-spokes"),
    pytest.param({**CELLS, "bore_hex": 6}, collections.Counter({"LINE": 12}), 4, 38,
                 id="hex-cells"),
    pytest.param({**HOLES, "keyway_width": 3, "keyway_depth": 1.4, "bore_flat": 0},
                 collections.Counter({"CIRCLE": 2}), 4, 38, id="keyway-holes"),
    pytest.param({**SPOKES, "keyway_width": 3, "keyway_depth": 1.4, "bore_flat": 0},
                 collections.Counter({"CIRCLE": 2}), 4, 38, id="keyway-spokes"),
    pytest.param({**CELLS, "keyway_width": 3, "keyway_depth": 1.4, "bore_flat": 0},
                 collections.Counter({"CIRCLE": 2}), 4, 38, id="keyway-cells"),
    # No recess (3 rows): the floor selector is never called at all.
    pytest.param({**HOLES, "recess_sides": "none"},
                 collections.Counter({"CIRCLE": 2, "LINE": 2}), None, 38,
                 id="no-recess-holes"),
    pytest.param({**SPOKES, "recess_sides": "none"},
                 collections.Counter({"CIRCLE": 2, "LINE": 2}), None, 38,
                 id="no-recess-spokes"),
    pytest.param({**CELLS, "recess_sides": "none"},
                 collections.Counter({"CIRCLE": 2, "LINE": 2}), None, 38,
                 id="no-recess-cells"),
    # Each pattern at its closest approach to the root circle (3 rows, D-17): the
    # cutter's outer wall sits exactly MIN_WALL inside rf -- the rim/floor/tip counts
    # are unaffected because neither selector reads the cutout geometry.
    pytest.param({**HOLES, "hole_circle_d": 24.075},
                 collections.Counter({"CIRCLE": 2, "LINE": 2}), 4, 38,
                 id="holes-at-rim-limit"),
    pytest.param({**SPOKES, "rim_wall": 0.4},
                 collections.Counter({"CIRCLE": 2, "LINE": 2}), 4, 38,
                 id="spokes-at-rim-limit"),
    pytest.param({**CELLS, "hex_wall": 0.4},
                 collections.Counter({"CIRCLE": 2, "LINE": 2}), 4, 38,
                 id="cells-at-rim-limit"),
    # 200 teeth (1 row, D-13's own extreme): the tip count scales with teeth; the
    # rim/floor counts do not, because neither depends on tooth count.
    pytest.param({**HOLES, "teeth": 200},
                 collections.Counter({"CIRCLE": 2, "LINE": 2}), 4, 400,
                 id="teeth-200-holes"),
])
def test_every_selector_takes_only_its_own_edges_with_a_body_cutout(
        monkeypatch: pytest.MonkeyPatch,
        kw: dict[str, object],
        rim: collections.Counter[str],
        floor: int | None,
        tip: int) -> None:
    """REQ-edge-selection-proven extended to cutouts (research PITFALLS.md Pitfall 1,
    Pitfall 5). The rim and floor selectors (_bore_rim_edges, _groove_floor_edges) run
    inside _cut_bore/_cut_face_recesses, both before _cut_body in _build, so a cutout
    present or not never changes what they see -- these rows prove it on the real
    pipeline (_build_checked, never build(): its lru_cache could skip the cutout step)
    rather than assume it from the no-cutout matrix
    (test_each_edge_selector_picks_exactly_its_own_edges).

    The tip selector (_tip_edges) runs after _cut_body (10 D-13), so it is called
    directly here on the finished solid -- exactly what _chamfer_tips would receive,
    the last step -- and no cutout edge reaches it: a hole's own circles have radius
    hole_d/2, a spoke's arcs are the fillet radius or the hub/rim radii (never ra), and
    a honeycomb cell has no CIRCLE edge at all, while every pattern's own D-17 wall
    rule keeps its cutter inside rf - MIN_WALL, strictly below ra.
    """
    real_rim = _bore_rim_edges
    real_floor = _groove_floor_edges
    rim_calls: list[collections.Counter[str]] = []
    floor_calls: list[int] = []

    def rim_spy(solid: cq.Shape, p: GearParams) -> list[cq.Edge]:
        edges = real_rim(solid, p)
        rim_calls.append(collections.Counter(e.geomType() for e in edges))
        return edges

    def floor_spy(solid: cq.Shape, radii: tuple[float, ...],
                  floor_z: list[float]) -> list[cq.Edge]:
        edges = real_floor(solid, radii, floor_z)
        floor_calls.append(len(edges))
        return edges

    monkeypatch.setattr("spur.model._bore_rim_edges", rim_spy)
    monkeypatch.setattr("spur.model._groove_floor_edges", floor_spy)
    p = GearParams.model_validate(kw)
    s = _build_checked(p)  # never build(): its cache could skip the cutout step

    assert len(rim_calls) == 1  # called exactly once, cutout or not
    assert len(floor_calls) == (1 if floor is not None else 0)  # not at all with no recess

    tips = _tip_edges(s, profile(p).ra, p.face_width)
    for e in tips:
        assert e.geomType() == "CIRCLE"
        assert e.radius() == pytest.approx(profile(p).ra, abs=TOL)
    assert (collections.Counter(round(e.startPoint().z / p.face_width) for e in tips)
            == {0: p.teeth, 1: p.teeth})

    # One tuple assertion: a wrong floor or tip count never hides behind a wrong rim
    # count (test_each_edge_selector_picks_exactly_its_own_edges' own pattern).
    assert (rim_calls[0], floor_calls[0] if floor_calls else None, len(tips)) == (rim, floor, tip)


@pytest.mark.parametrize(("kw", "faces"), [
    pytest.param({"tip_chamfer": 0.4}, 210, id="d-flat"),
    pytest.param({"tip_chamfer": 0.4, "keyway_width": 3, "keyway_depth": 1.4, "bore_flat": 0},
                 213, id="keyway-round"),
    pytest.param({"tip_chamfer": 0.4, "bore_hex": 6}, 222, id="hex"),
    # 11-07: a cutout composes with the tip chamfer -- _cut_body runs before
    # _chamfer_tips (D-13), so the selector still sees only the 2 x 19 tip arcs, none
    # of a cutout's own circles (a hole's radius hole_d/2, a spoke fillet's radius, a
    # honeycomb cell has no CIRCLE at all). 216/338 measured on the pinned kernel
    # 2026-09-29: 172 plain faces + the cutout's own faces + 38 tip cones each.
    pytest.param({"tip_chamfer": 0.4, "hole_count": 6, "hole_d": 4, "hole_circle_d": 20},
                 216, id="hole-cutout"),
    pytest.param({"tip_chamfer": 0.4, "spoke_count": 4, "spoke_width": 2, "hub_d": 13.2,
                  "rim_wall": 1, "spoke_fillet": 1}, 264, id="spoke-cutout"),
    pytest.param({"tip_chamfer": 0.4, "hex_cell": 3, "hex_wall": 1}, 338,
                 id="honeycomb-cutout"),
])
def test_the_tip_chamfer_takes_exactly_the_tip_arcs_in_the_real_pipeline(
        monkeypatch: pytest.MonkeyPatch, kw: dict[str, object], faces: int) -> None:
    """D-13 in the real pipeline. The chamfered bore's cones, the filleted floors and
    the keyway slot are all present, and the selector is called once and takes exactly
    the tip arcs."""
    real = _tip_edges
    calls: list[tuple[collections.Counter[str], collections.Counter[int]]] = []

    def spy(solid: cq.Shape, ra: float, face_width: float) -> list[cq.Edge]:
        edges = real(solid, ra, face_width)
        calls.append((collections.Counter(e.geomType() for e in edges),
                      collections.Counter(round(e.startPoint().z / face_width) for e in edges)))
        return edges

    monkeypatch.setattr("spur.model._tip_edges", spy)
    p = GearParams.model_validate(kw)
    s = _build_checked(p)  # never build(): its cache could skip the step
    assert calls == [(collections.Counter({"CIRCLE": 38}), collections.Counter({0: 19, 1: 19}))]
    assert len(s.Faces()) == faces


def test_a_tip_chamfer_that_selects_no_tip_arcs_is_a_build_error_not_a_sharp_tip(
        monkeypatch: pytest.MonkeyPatch) -> None:
    """D-14's guard, in the rim guard's words. Use _build_checked, never build()."""
    real = _tip_edges

    def wrapper(solid: cq.Shape, ra: float, face_width: float) -> list[cq.Edge]:
        return real(solid, ra + 1.0, face_width)  # a radius where no arc exists

    monkeypatch.setattr("spur.model._tip_edges", wrapper)
    with pytest.raises(BuildError, match="selected no tip-arc edges") as exc_info:
        _build_checked(GearParams(tip_chamfer=0.4))
    assert "try smaller" not in str(exc_info.value)


def test_a_hex_bore_measures_the_across_flats_and_corners_it_reports() -> None:
    """The printed numbers are what calipers read on the built part -- the Phase 8
    analogue of Phase 9's datum test."""
    p = GearParams(bore_hex=6, bore_chamfer=0, recess_sides="none")
    s = build(p)
    d = derive(p)
    rim = _bore_rim_edges(s, p)
    assert len(rim) == 12

    vertex_radii = [math.hypot(q.x, q.y)
                    for e in rim for q in (e.startPoint(), e.endPoint())]
    for r in vertex_radii:
        assert r == pytest.approx(bore_rim_limit(p), abs=TOL)

    assert d.hex_across_corners is not None
    assert 2 * max(vertex_radii) == pytest.approx(d.hex_across_corners, abs=5e-4)

    mids = [(e.positionAt(0.5), math.hypot(e.positionAt(0.5).x, e.positionAt(0.5).y))
            for e in rim]
    assert d.hex_across_flats is not None
    assert 2 * min(r for _, r in mids) == pytest.approx(d.hex_across_flats, abs=5e-4)

    # A flat faces +X (the orientation comment in _cut_bore): the rim-edge midpoint
    # with the largest x has x = half the across-flats, y = 0.
    flat_mid = max((m for m, _ in mids), key=lambda v: v.x)
    assert flat_mid.x == pytest.approx(d.hex_across_flats / 2, abs=1e-6)
    assert flat_mid.y == pytest.approx(0.0, abs=1e-6)


def test_the_same_hex_link_builds_the_same_solid_twice() -> None:
    """The same-link-same-part property (L05), for a hex bore: two independent builds
    of one parameter set agree on topology and volume. Uses _build_checked, bypassing
    the lru_cache, so both builds actually run the kernel."""
    p = GearParams(bore_hex=6)
    a = _build_checked(p)
    b = _build_checked(p)
    assert len(a.Faces()) == len(b.Faces())
    assert len(a.Edges()) == len(b.Edges())
    assert a.Volume() == pytest.approx(b.Volume(), rel=1e-9)


@pytest.mark.parametrize(("kw", "rim"), [
    pytest.param({"keyway_width": 3, "keyway_depth": 1.4},
                 collections.Counter({"CIRCLE": 2, "LINE": 2}), id="d-flat"),
    pytest.param({"keyway_width": 3, "keyway_depth": 1.4, "bore_flat": 0},
                 collections.Counter({"CIRCLE": 2}), id="round"),
])
def test_the_rim_chamfer_on_a_keyed_bore_takes_the_pre_keyway_edges(
        monkeypatch: pytest.MonkeyPatch, kw: dict[str, object],
        rim: collections.Counter[str]) -> None:
    """D-06/D-07's ordering, observed in the real chamfered pipeline: the rim selector
    runs exactly once, on the pre-keyway rim, when a real keyed link is built end to
    end (default 0.4 mm chamfer, never a patched-out slot)."""
    real = _bore_rim_edges
    calls: list[collections.Counter[str]] = []

    def spy(solid: cq.Shape, p: GearParams) -> list[cq.Edge]:
        edges = real(solid, p)
        calls.append(collections.Counter(e.geomType() for e in edges))
        return edges

    monkeypatch.setattr("spur.model._bore_rim_edges", spy)
    _build_checked(GearParams.model_validate(kw))  # never build(): the cache would skip it
    assert calls == [rim]


@pytest.mark.parametrize("kw", [
    pytest.param({"keyway_width": 3, "keyway_depth": 1.4, "bore_chamfer": 0}, id="d-flat"),
    pytest.param({"keyway_width": 3, "keyway_depth": 1.4, "bore_chamfer": 0, "bore_flat": 0},
                 id="round"),
])
def test_a_keyway_floor_sits_keyway_depth_outside_the_as_cut_bore_wall(
        kw: dict[str, object]) -> None:
    """ROADMAP SC1's "measured against the stated datum by a test, not just the
    parameter round-tripping" -- the keyway analogue of the hex measurement test. The
    superseded text's datum would put this floor 0.075 mm further out (D-14)."""
    p = GearParams.model_validate(kw)
    s = build(p)
    d = derive(p)

    floors = [f for f in s.Faces()
              if f.geomType() == "PLANE" and abs(abs(f.normalAt().y) - 1) < 1e-9]
    assert len(floors) == 1  # planning: 1 in 9 configurations, research A3 widened
    bb = floors[0].BoundingBox()
    assert bb.ylen < TOL

    assert bb.ymin == pytest.approx(bore_radius(p) + p.keyway_depth, abs=TOL)
    assert bb.xlen == pytest.approx(keyway_width_effective(p), abs=TOL)

    # The bore wall's own radius, read back from the kernel -- chamfer 0, so the rim is
    # the as-cut wall itself.
    rim_radii = [e.radius() for e in _bore_rim_edges(s, p) if e.geomType() == "CIRCLE"]
    wall = rim_radii[0]
    assert all(r == pytest.approx(wall, abs=TOL) for r in rim_radii)
    assert bb.ymin - wall == pytest.approx(p.keyway_depth, abs=TOL)

    assert d.keyway_floor_to_wall is not None
    assert d.keyway_width_effective is not None
    assert bb.ymin + wall == pytest.approx(d.keyway_floor_to_wall, abs=5e-4)
    assert bb.xlen == pytest.approx(d.keyway_width_effective, abs=5e-4)

    if p.bore_flat > 0:
        # D-04: the D-flat stays when a keyway is added.
        flat_faces = [f for f in s.Faces()
                      if f.geomType() == "PLANE" and abs(abs(f.normalAt().x) - 1) < 1e-9]
        assert any(f.BoundingBox().xmin
                   == pytest.approx(p.bore_flat + p.bore_clearance - bore_radius(p), abs=TOL)
                   for f in flat_faces)


@pytest.mark.parametrize("kw", [
    pytest.param({"keyway_width": 3, "keyway_depth": 1.4}, id="d-flat"),
    pytest.param({"keyway_width": 3, "keyway_depth": 1.4, "bore_flat": 0}, id="round"),
])
def test_the_bore_chamfer_survives_the_keyway_and_the_slot_edges_stay_sharp(
        kw: dict[str, object]) -> None:
    """D-05/D-07's built-solid proof. A chamfered slot would move its end-face outline
    out by the chamfer, so no end-face edge would sit at the nominal width and floor;
    planning read 4 / 4 / 4 / 2 on both shapes."""
    p = GearParams.model_validate(kw)
    s = build(p)
    hw = keyway_width_effective(p) / 2
    floor = bore_radius(p) + p.keyway_depth

    def on_end_face(e: cq.Edge) -> bool:
        a, b = e.startPoint(), e.endPoint()
        if abs(a.z - b.z) > TOL:
            return False
        return abs(a.z) < TOL or abs(a.z - p.face_width) < TOL

    ends = [e for e in s.Edges() if on_end_face(e)]

    # Chamfer survived: 4 circles at the mouth radius, split by the slot on each face.
    mouths = [e for e in ends if e.geomType() == "CIRCLE"
             and e.radius() == pytest.approx(bore_radius(p) + p.bore_chamfer, abs=TOL)]
    assert len(mouths) == 4
    cones = [f for f in s.Faces() if f.geomType() == "CONE"]
    assert len(cones) == 4

    # Slot sharp: two vertical sides and one floor line per end face, at nominal size.
    lines = [e for e in ends if e.geomType() == "LINE"]
    sides = [e for e in lines
             if abs(e.startPoint().x - e.endPoint().x) < TOL
             and abs(abs(e.startPoint().x) - hw) < TOL]
    floor_lines = [e for e in lines
                  if abs(e.startPoint().y - floor) < TOL and abs(e.endPoint().y - floor) < TOL]
    assert len(sides) == 4
    assert len(floor_lines) == 2

    def faces_hit(es: Sequence[cq.Edge]) -> set[int]:
        return {round(e.startPoint().z / p.face_width) for e in es}

    assert faces_hit(sides) == {0, 1}
    assert faces_hit(floor_lines) == {0, 1}


def test_the_same_keyed_link_builds_the_same_solid_twice() -> None:
    """The same-link-same-part property (L05), for a keyway: two independent builds of
    one parameter set agree on topology and volume. Uses _build_checked, bypassing the
    lru_cache, so both builds actually run the kernel."""
    p = GearParams(keyway_width=3, keyway_depth=1.4)
    a = _build_checked(p)
    b = _build_checked(p)
    assert len(a.Faces()) == len(b.Faces())
    assert len(a.Edges()) == len(b.Edges())
    assert a.Volume() == pytest.approx(b.Volume(), rel=1e-9)


def test_the_pre_hex_rim_bound_would_have_chamfered_nothing_on_a_hex_wider_than_the_round_bore(
        monkeypatch: pytest.MonkeyPatch) -> None:
    """ROADMAP SC1's "the v0.1 selector would have selected zero edges here", reproduced
    on a hex whose corners (7.419 mm) lie outside the round bore's radius (4.575 mm) --
    a hex smaller than the round bore would still have been caught by the old band,
    which is why this row uses 12.7. Calls _build_checked, never build(): build()'s
    lru_cache would hand back a solid built before the patch, without running the
    selector at all.
    """
    assert _build_checked(GearParams(bore_hex=12.7)).isValid()

    monkeypatch.setattr("spur.model.bore_rim_limit", bore_radius)
    with pytest.raises(BuildError, match="selected no bore-rim edges"):
        _build_checked(GearParams(bore_hex=12.7))


@pytest.mark.parametrize("kw", [
    pytest.param({"bore_hex": 24.15, "bore_chamfer": 0}, id="corner-limit"),
    pytest.param({"bore_hex": 23.35}, id="chamfered-corner-limit"),
])
def test_the_largest_hex_each_root_rule_allows_builds(kw: dict[str, object]) -> None:
    """D-03: one step inside each root rule's boundary builds a valid solid; the step
    past it is test_calc.py's refusal."""
    s = _build_checked(GearParams.model_validate(kw))
    assert s.isValid()


@pytest.mark.parametrize("kw", [
    pytest.param({"keyway_width": 6.45, "keyway_depth": 1.4}, id="d-02-flat"),
    pytest.param({"keyway_width": 3, "keyway_depth": 9.35}, id="d-10-root"),
    pytest.param({"bore_flat": 0, "keyway_width": 8.95, "keyway_depth": 1.4}, id="d-11-bore"),
])
def test_the_largest_keyway_each_rule_allows_builds(kw: dict[str, object]) -> None:
    """D-02/D-10/D-11: one step inside each rule's boundary builds a valid solid; the
    step past it is test_calc.py's refusal."""
    s = _build_checked(GearParams.model_validate(kw))
    assert s.isValid()


@pytest.mark.parametrize("kw", [
    pytest.param({"keyway_width": 7.0, "keyway_depth": 1.4}, id="d-02-tangent"),
    pytest.param({"keyway_width": 7.5, "keyway_depth": 1.4}, id="d-02-notched"),
    pytest.param({"keyway_width": 3, "keyway_depth": 9.9}, id="d-10-past-root"),
    pytest.param({"bore_flat": 0, "keyway_width": 9.0, "keyway_depth": 1.4},
                 id="d-11-as-wide-as-the-bore"),
])
def test_the_kernel_cuts_one_valid_solid_past_each_keyway_rule(kw: dict[str, object]) -> None:
    """The rules are the part's, not the kernel's: validation bypassed
    (model_copy(), which -- like model_construct() -- never re-runs _feasible), the
    kernel still cuts one valid solid past every one of D-02/D-10/D-11's boundaries, the
    way 08-03 recorded the hex side probe as a test, so a kernel bump that changes it
    goes red."""
    s = _build_checked(GearParams().model_copy(update=kw))
    assert s.isValid()


def test_the_kernel_chamfers_a_hex_bore_far_past_its_side_length() -> None:
    """D-03's probe, recorded as a test: the side (0.375 mm) is 8x smaller than the
    3 mm chamfer and the kernel still cuts the exact mouth, which is why check() has no
    chamfer-against-side rule. Removed volume matches the analytic hex frustum within
    rel 1e-6; planning read 82.618824 mm3 both ways, 2026-09-26."""
    bare = _build_checked(GearParams(bore_hex=0.5, bore_chamfer=0, recess_sides="none"))
    cham = _build_checked(GearParams(bore_hex=0.5, bore_chamfer=3, recess_sides="none"))
    w, c = 0.65, 3.0  # effective across-flats (0.5 + 0.15 default clearance), chamfer
    a1 = math.sqrt(3) / 2 * w ** 2
    a2 = math.sqrt(3) / 2 * (w + 2 * c) ** 2
    expected = 2 * (c / 3 * (a1 + a2 + math.sqrt(a1 * a2)) - a1 * c)
    assert bare.Volume() - cham.Volume() == pytest.approx(expected, rel=1e-6)


@pytest.mark.parametrize("kw", [
    pytest.param({"bore_d": 24.7, "bore_chamfer": 2, "bore_flat": 0}, id="round-chamfer-2"),
    pytest.param({"bore_d": 24.7, "bore_chamfer": 2, "bore_flat": 22}, id="d-flat-chamfer-2"),
    pytest.param({"bore_d": 27.9, "bore_flat": 0}, id="round-default-chamfer"),
    pytest.param({"teeth": 40, "bore_d": 61.45, "bore_chamfer": 2, "bore_flat": 0},
                 id="round-40-teeth"),
])
def test_the_largest_round_bore_the_chamfer_rule_allows_builds(kw: dict[str, object]) -> None:
    """D-12: one step inside the measured contact boundary builds a valid solid; the
    step past it is test_calc.py's refusal."""
    s = _build_checked(GearParams.model_validate(kw))
    assert s.isValid()


@pytest.mark.parametrize("kw", [
    pytest.param({"bore_d": 24.725, "bore_chamfer": 2, "bore_flat": 0}, id="round"),
    pytest.param({"bore_d": 24.725, "bore_chamfer": 2, "bore_flat": 22}, id="d-flat"),
])
def test_the_kernel_fails_where_a_round_bore_chamfer_touches_the_root(
        kw: dict[str, object]) -> None:
    """D-12's measurement recorded as a test: the exact contact (validation bypassed via
    model_copy()) is where the kernel itself fails, not a margin short of it -- if a
    kernel bump makes this contact build, this goes red and the rule's premise must be
    re-measured."""
    with pytest.raises(BuildError, match="Geometry kernel failed"):
        _build_checked(GearParams().model_copy(update=kw))


def test_the_kernel_can_fail_inside_the_root_contact_residual_band() -> None:
    """09-REVIEW.md WR-02: check() only guarantees gap > ROOT_CONTACT (1e-9 mm), but the
    bisection behind ROOT_CONTACT only proved the kernel builds reliably from
    gap >= 1.9e-8 mm up. bore_d 24.724999998 (19T, m1.75, chamfer 2, round -- the debt
    file's own configuration) lands at gap 1.000000082740371e-09, inside that unproven
    band: check() accepts it (no ValidationError, no model_copy() bypass needed -- an
    11-significant-figure bore_d that a typed UI value, a shared link or an API/CLI
    caller can send, not adversarial bit-manipulation), and the kernel still raises
    BuildError. Pinned so a
    future cadquery/cadquery-ocp bump that changes behaviour in this band goes red here
    instead of silently."""
    p = GearParams(bore_d=24.724999998, bore_chamfer=2, bore_flat=0)
    with pytest.raises(BuildError, match="Geometry kernel produced an invalid solid"):
        _build_checked(p)


def _assert_only_the_tip_arcs_were_chamfered(cut: cq.Solid, plain: cq.Solid,
                                             p: GearParams, p0: GearParams) -> None:
    """D-12 and ROADMAP SC1 on the built solid: flanks, roots, bore, recess and keyway
    untouched, outside diameter unchanged. p sets tip_chamfer; p0 is the same gear
    without it. Shared by the proof
    (test_the_tip_chamfer_breaks_only_the_tip_arcs_on_the_built_solid) and the tripwire
    (test_the_tip_chamfer_proof_fails_when_the_tip_step_is_skipped), which shows this
    proof fail on a silently vanished chamfer (D-14).
    """
    c = tip_chamfer_effective(p)
    pr = profile(p)
    n = p.teeth
    fw = p.face_width

    d_faces = (collections.Counter(f.geomType() for f in cut.Faces())
              - collections.Counter(f.geomType() for f in plain.Faces()))
    assert d_faces == collections.Counter({"CONE": 2 * n})
    d_faces_reverse = (collections.Counter(f.geomType() for f in plain.Faces())
                      - collections.Counter(f.geomType() for f in cut.Faces()))
    assert not d_faces_reverse

    assert len(cut.Edges()) - len(plain.Edges()) == 6 * n
    assert cut.Volume() < plain.Volume()

    bb_cut, bb_plain = cut.BoundingBox(), plain.BoundingBox()
    for attr in ("xmin", "xmax", "ymin", "ymax", "zmin", "zmax"):
        assert getattr(bb_cut, attr) == pytest.approx(getattr(bb_plain, attr), abs=TOL)
    assert derive(p).tip_d == derive(p0).tip_d

    if bore_rim_limit(p0) > 0:
        assert (collections.Counter(e.geomType() for e in _bore_rim_edges(cut, p0))
                == collections.Counter(e.geomType() for e in _bore_rim_edges(plain, p0)))

    rr = recess_radii(p0, pr.rf)
    if rr is not None:
        heights: list[float] = []
        if p0.recess_sides in ("both", "bottom"):
            heights.append(p0.recess_depth)
        if p0.recess_sides in ("both", "top"):
            heights.append(p0.face_width - p0.recess_depth)
        assert (len(_groove_floor_edges(cut, rr, heights))
                == len(_groove_floor_edges(plain, rr, heights)))

    # No tip arc left on an end face.
    with pytest.raises(BuildError, match="selected no tip-arc edges"):
        _tip_edges(cut, pr.ra, fw)

    # 45 degrees, c off the face and c off the tip: the tip circle at radius ra moved
    # from z in {0, fw} to z in {c, fw - c} (n arcs each), and a new sharp circle at the
    # reduced radius ra - c sits exactly on each end face (n arcs each).
    moved = [e for e in cut.Edges() if e.geomType() == "CIRCLE" and abs(e.radius() - pr.ra) < TOL]
    assert (collections.Counter(round(e.startPoint().z, 6) for e in moved)
            == {round(c, 6): n, round(fw - c, 6): n})

    def on_end_face(e: cq.Edge) -> bool:
        a, b = e.startPoint(), e.endPoint()
        return (any(abs(a.z - z) < TOL for z in (0.0, fw))
                and any(abs(b.z - z) < TOL for z in (0.0, fw)))

    sharp = [e for e in cut.Edges()
            if e.geomType() == "CIRCLE" and abs(e.radius() - (pr.ra - c)) < TOL
            and on_end_face(e)]
    assert (collections.Counter(round(e.startPoint().z / fw) for e in sharp) == {0: n, 1: n})


@pytest.mark.parametrize("kw", [
    pytest.param({}, id="d-flat"),
    pytest.param({"keyway_width": 3, "keyway_depth": 1.4, "bore_flat": 0}, id="keyway-round"),
    pytest.param({"bore_hex": 6}, id="hex"),
])
def test_the_tip_chamfer_breaks_only_the_tip_arcs_on_the_built_solid(
        kw: dict[str, object]) -> None:
    """D-12 and ROADMAP SC1 on the built solid: flanks, roots, bore, recess and keyway
    untouched, outside diameter unchanged.

    The rows carry bore_chamfer 0 and recess_fillet 0 so that the rim and floor
    selectors still have sharp edges to count on both solids. On a chamfered rim the
    selector finds none (09's amended SC4). The real pipeline with those features is
    Task 1's spy test.

    Planning read +38 CONE faces, +114 edges and -22.7557 mm3 on all three rows.
    """
    p0 = GearParams.model_validate({**kw, "bore_chamfer": 0, "recess_fillet": 0})
    p = GearParams.model_validate({**kw, "bore_chamfer": 0, "recess_fillet": 0,
                                   "tip_chamfer": 1.0})
    _assert_only_the_tip_arcs_were_chamfered(_build_checked(p), _build_checked(p0), p, p0)


def test_the_tip_chamfer_proof_fails_when_the_tip_step_is_skipped(
        monkeypatch: pytest.MonkeyPatch) -> None:
    """D-14's tripwire, Phase 7's precedent: the proof demonstrably catches a silently
    vanished chamfer."""
    monkeypatch.setattr("spur.model._chamfer_tips", lambda solid, _p, _pr: solid)
    p0 = GearParams(bore_chamfer=0, recess_fillet=0)
    p = GearParams(bore_chamfer=0, recess_fillet=0, tip_chamfer=1.0)
    assert derive(p).tip_chamfer_effective == 1.0  # the number still prints -- L08's failure
    with pytest.raises(AssertionError):
        _assert_only_the_tip_arcs_were_chamfered(_build_checked(p), _build_checked(p0), p, p0)


def test_the_largest_tip_chamfer_the_flank_limit_allows_builds() -> None:
    """D-04, one step inside the measured contact builds."""
    p = GearParams(profile_shift=1.0, pressure_angle=14.5, tip_chamfer=3)
    pr = profile(p)
    assert min(0.45 * p.face_width, pr.ra - pr.r, 3.0) == 3.0  # D-01/D-02 alone allow 3.0
    assert tip_chamfer_effective(p) == 2.937
    s = _build_checked(p)
    assert s.isValid()
    baseline = _build_checked(GearParams(profile_shift=1.0, pressure_angle=14.5))
    assert len(s.Faces()) == len(baseline.Faces()) + 38


def test_the_kernel_fails_one_step_past_the_start_of_the_involute(
        monkeypatch: pytest.MonkeyPatch) -> None:
    """D-04's measurement recorded as a test, in the ROOT_CONTACT test's shape. The
    contact is ra - spline_start = 2.9375, the top of the root fillet's straight lead-in
    under the involute spline. One 0.05 mm step past it, the kernel returns one solid
    that is not valid. If a kernel bump makes this build, this test goes red and the
    flank limit's premise must be re-measured (bench/tip_chamfer_spike.py)."""
    monkeypatch.setattr("spur.model.tip_chamfer_effective", lambda _p: 2.9875)
    with pytest.raises(BuildError, match="Geometry kernel produced an invalid solid"):
        _build_checked(GearParams(profile_shift=1.0, pressure_angle=14.5, tip_chamfer=3))


@pytest.mark.parametrize("kw", [
    pytest.param({"bore_flat": 0}, id="round"),
    pytest.param({}, id="d-flat"),
    pytest.param({"bore_hex": 6}, id="hex"),
    pytest.param({"keyway_width": 3, "keyway_depth": 5}, id="keyway-corner"),
])
def test_a_recess_at_its_hub_clearance_keeps_min_wall_from_the_chamfered_bore_mouth(
        kw: dict[str, object]) -> None:
    """The assumption-delta invariant (08-02-PLAN.md): recess_radii() clears every bore
    shape's chamfered mouth by MIN_WALL. With the hub at R + c (the plain chamfer,
    not the corner-carried 2c/sqrt(3)) the hex row goes invalid at 2.586 mm and fails
    at 3 mm (planning probe, research PITFALLS.md Pitfall 1). The keyway row is D-09's
    yield, measured: with bore_chamfer 3 the corner (9.7037 mm) still lies beyond the
    chamfered mouth (7.575 mm), so the measured mouth is the keyway corner."""
    p = GearParams.model_validate({**kw, "bore_chamfer": 3, "recess_inner_d": 1.0})
    s = build(p)
    assert s.isValid()
    assert len(s.Solids()) == 1

    rr = recess_radii(p, profile(p).rf)
    assert rr is not None
    r_in = rr[0]

    mouth = max(math.hypot(v.X, v.Y) for v in s.Vertices()
                if abs(v.Z - p.face_width) < TOL and math.hypot(v.X, v.Y) < r_in - TOL)
    assert r_in - mouth == pytest.approx(MIN_WALL, abs=1e-6)


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


def test_the_hole_link_cuts_six_holes_through_the_recessed_floor() -> None:
    """?hole_count=6&hole_d=4&hole_circle_d=20 on the default gear (REQ-cutout-composes):
    six holes cut through the recessed floor in one cut call, hole 0 on +X (D-03), the
    recess floor fillet's four TORUS faces untouched. _build_checked, not build(): the
    lru_cache on build() would hand back a solid built by an earlier test's GearParams()
    call for a "bare" GearParams() here, instead of a freshly built one.
    """
    p0 = GearParams()
    p = GearParams(hole_count=6, hole_d=4, hole_circle_d=20)
    plain = _build_checked(p0)
    cut = _build_checked(p)

    d_faces = (collections.Counter(f.geomType() for f in cut.Faces())
              - collections.Counter(f.geomType() for f in plain.Faces()))
    assert d_faces == collections.Counter({"CYLINDER": 6})
    r_faces = (collections.Counter(f.geomType() for f in plain.Faces())
              - collections.Counter(f.geomType() for f in cut.Faces()))
    assert not r_faces

    assert len(cut.Edges()) - len(plain.Edges()) == 18

    web = p.face_width - 2 * p.recess_depth  # the 3.5 mm web between the two recesses
    assert plain.Volume() - cut.Volume() == pytest.approx(
        6 * math.pi * (p.hole_d / 2) ** 2 * web, rel=1e-6)

    assert sum(1 for f in cut.Faces() if f.geomType() == "TORUS") == 4
    assert sum(1 for f in plain.Faces() if f.geomType() == "TORUS") == 4

    mid = p.face_width / 2
    assert cut.isInside(cq.Vector(10, 0, mid)) is False  # hole 0, centred on +X (D-03)
    assert cut.isInside(cq.Vector(10 * math.cos(math.pi / 6), 10 * math.sin(math.pi / 6),
                                  mid)) is True  # between holes 0 and 1


def test_the_spoke_link_cuts_four_filleted_sectors() -> None:
    """?spoke_count=4&spoke_width=2&hub_d=12&rim_wall=1&spoke_fillet=1 on the default
    gear (D-01...D-05): four filleted sectors cut through the full face width in one
    cut call, arm 0 centred on +X (D-03), the recess floor fillet's four TORUS faces
    split into 16 under the arms (research Pattern 2, planning probe 2026-09-29).
    _build_checked, not build(): the lru_cache on build() would hand back a solid built
    by an earlier test's GearParams() call for a "bare" GearParams() here.
    """
    p0 = GearParams()
    p = GearParams(spoke_count=4, spoke_width=2, hub_d=12, rim_wall=1, spoke_fillet=1)
    plain = _build_checked(p0)
    cut = _build_checked(p)

    d_faces = (collections.Counter(f.geomType() for f in cut.Faces())
              - collections.Counter(f.geomType() for f in plain.Faces()))
    assert d_faces == collections.Counter({"PLANE": 14, "CYLINDER": 40, "TORUS": 16})
    assert len(cut.Edges()) - len(plain.Edges()) == 240

    mid = p.face_width / 2
    assert cut.isInside(cq.Vector(10, 0, mid)) is True     # arm 0, centred on +X (D-03)
    assert cut.isInside(cq.Vector(10 * math.cos(math.radians(45)),
                                  10 * math.sin(math.radians(45)), mid)) is False


def test_a_rim_corner_fillet_is_tangent_to_the_rim_circle_and_the_bar_side() -> None:
    """The hand-computed sanity case D-05's mirrored _fillet_corner needed before
    trusting it at every sector corner (research Pattern 2, Assumption A1): R 10, the
    bar side is the line y = 1 running inward, rho 1. The tangent point on the circle
    is R from the axis, the tangent point on the line lies exactly on y = 1, and both
    sit rho from the arc's own centre -- the general tangency properties, not just this
    one set of coordinates.
    """
    p0 = cq.Vector(math.sqrt(99), 1, 0)
    p1 = cq.Vector(0, 1, 0)
    on_root, mid, on_line = _fillet_corner(p0, p1, 10, 1, -1, inside=True)

    assert (on_root.x, on_root.y) == pytest.approx((9.749960, 2.222222), abs=1e-6)
    assert (on_line.x, on_line.y) == pytest.approx((8.774964, 1.0), abs=1e-6)

    centre = cq.Vector(math.sqrt(77), 2, 0)
    assert math.hypot(on_root.x, on_root.y) == pytest.approx(10.0, abs=1e-9)
    assert on_line.y == pytest.approx(1.0, abs=1e-9)
    assert math.hypot(on_root.x - centre.x, on_root.y - centre.y) == pytest.approx(1.0, abs=1e-9)
    assert math.hypot(on_line.x - centre.x, on_line.y - centre.y) == pytest.approx(1.0, abs=1e-9)
    assert math.hypot(mid.x - centre.x, mid.y - centre.y) == pytest.approx(1.0, abs=1e-9)


def test_the_honeycomb_link_cuts_eighteen_whole_cells() -> None:
    """?hex_cell=3&hex_wall=1 on the default gear (D-07...D-13): 18 whole hexagonal
    cells cut through the full face width in one cut call. _build_checked, not
    build(): the lru_cache on build() would hand back a solid built by an earlier
    test's GearParams() call for a "bare" GearParams() here.
    """
    p0 = GearParams()
    p = GearParams(hex_cell=3, hex_wall=1)
    plain = _build_checked(p0)
    cut = _build_checked(p)

    d_faces = (collections.Counter(f.geomType() for f in cut.Faces())
              - collections.Counter(f.geomType() for f in plain.Faces()))
    assert d_faces == collections.Counter({"PLANE": 108, "CYLINDER": 10, "TORUS": 10})
    assert len(cut.Edges()) - len(plain.Edges()) == 494

    mid = p.face_width / 2
    assert cut.isInside(cq.Vector(6.49, 0, mid)) is True    # a cell facing the axis
    assert cut.isInside(cq.Vector(6.51, 0, mid)) is False   # inside the cut cell


# tests/test_calc.py's own SPOKE base dict (the boundary rows below reuse its exact
# refusal-boundary values, measured for 11-03/11-04's own tests).
SPOKES_MIN = {"spoke_count": 4, "spoke_width": 2, "hub_d": 12, "rim_wall": 1}


@pytest.mark.parametrize("kw", [
    pytest.param({"hole_count": 6, "hole_d": 4, "hole_circle_d": 14.75}, id="hole-hub"),
    pytest.param({"hole_count": 6, "hole_d": 4, "hole_circle_d": 24.075}, id="hole-rim"),
    pytest.param({"teeth": 40, "hole_count": 6, "hole_d": 19.6, "hole_circle_d": 40},
                 id="hole-neighbour"),
    pytest.param({**SPOKES_MIN, "rim_wall": 0.4}, id="spoke-rim"),
    pytest.param({**SPOKES_MIN, "hub_d": 10.75}, id="spoke-hub"),
    pytest.param({**SPOKES_MIN, "rim_wall": 8.0375}, id="spoke-annulus"),
    pytest.param({"spoke_count": 12, "spoke_width": 2.67, "hub_d": 12, "rim_wall": 0.4},
                 id="spoke-opening"),
    pytest.param({**SPOKES_MIN, "spoke_width": 0.4}, id="spoke-arm"),
    pytest.param({"hex_cell": 3, "hex_wall": 0.4}, id="honeycomb-wall"),
])
def test_the_largest_cutout_each_wall_rule_allows_builds(kw: dict[str, object]) -> None:
    """D-16/D-17: one step inside each cutout wall rule's boundary builds a valid
    solid; the step past it is test_calc.py's own refusal
    (test_a_hole_rule_refuses_one_step_past_its_wall_and_accepts_it_exactly,
    test_a_spoke_rule_refuses_one_step_past_its_wall_and_accepts_it_exactly,
    test_a_honeycomb_rule_refuses_one_step_past_it_and_names_its_fields), whose own
    boundary values these rows reuse exactly -- the rules are the part's MIN_WALL, not
    a kernel boundary (08 D-03's precedent, applied here to every cutout rule at once).
    The arm rule (11-01's human ruling, kept by 11-04) is included.
    """
    s = _build_checked(GearParams.model_validate(kw))
    assert s.isValid()


@pytest.mark.parametrize("kw", [
    pytest.param({"hole_count": 6, "hole_d": 4, "hole_circle_d": 14.7}, id="hole-hub"),
    pytest.param({"hole_count": 6, "hole_d": 4, "hole_circle_d": 24.1}, id="hole-rim"),
    pytest.param({"teeth": 40, "hole_count": 6, "hole_d": 19.65, "hole_circle_d": 40},
                 id="hole-neighbour"),
    pytest.param({**SPOKES_MIN, "rim_wall": 0.35}, id="spoke-rim"),
    pytest.param({**SPOKES_MIN, "hub_d": 10.7}, id="spoke-hub"),
    pytest.param({**SPOKES_MIN, "rim_wall": 8.05}, id="spoke-annulus"),
    pytest.param({"spoke_count": 12, "spoke_width": 2.72, "hub_d": 12, "rim_wall": 0.4},
                 id="spoke-opening"),
    pytest.param({**SPOKES_MIN, "spoke_width": 0.35}, id="spoke-arm"),
    pytest.param({"hex_cell": 3, "hex_wall": 0.35}, id="honeycomb-wall"),
])
def test_the_kernel_cuts_one_valid_solid_past_each_cutout_rule(kw: dict[str, object]) -> None:
    """The rules are the part's MIN_WALL, not the kernel's (09's keyway test's own
    words): validation bypassed (model_copy(), which never re-runs _feasible), the
    kernel still cuts one valid solid one 0.05 mm field-step past every cutout wall
    rule -- the same rows test_calc.py's refusal tests pin as ValidationErrors, here
    built for real on the pinned kernel (planning probe 2026-09-29). A kernel bump that
    changes this goes red here, the way 08-03/09-03 already do for the bore and keyway
    rules.
    """
    s = _build_checked(GearParams().model_copy(update=kw))
    assert s.isValid()


@pytest.mark.parametrize("kw", [
    pytest.param({"hole_count": 6, "hole_d": 3, "hole_circle_d": 16.0125}, id="hole-on-r-in"),
    pytest.param({"hole_count": 6, "hole_d": 3, "hole_circle_d": 22.0125}, id="hole-on-r-out"),
    pytest.param({"hole_count": 6, "hole_d": 3, "hole_circle_d": 21.0125},
                 id="hole-inside-r-out"),
    pytest.param({"hole_count": 6, "hole_d": 3, "hole_circle_d": 17.0125},
                 id="hole-outside-r-in"),
    pytest.param({"spoke_count": 4, "spoke_width": 2, "hub_d": 13.0125, "rim_wall": 1},
                 id="spoke-hub-arc-on-r-in-sharp"),
    pytest.param({"spoke_count": 4, "spoke_width": 2, "hub_d": 13.0125, "rim_wall": 1,
                  "spoke_fillet": 1}, id="spoke-hub-arc-on-r-in-filleted"),
    pytest.param({"spoke_count": 4, "spoke_width": 2, "hub_d": 12, "rim_wall": 1.93125},
                 id="spoke-rim-arc-on-r-out-sharp"),
    pytest.param({"spoke_count": 4, "spoke_width": 2, "hub_d": 12, "rim_wall": 1.93125,
                  "spoke_fillet": 1}, id="spoke-rim-arc-on-r-out-filleted"),
    pytest.param({"spoke_count": 4, "spoke_width": 2, "hub_d": 10.75, "rim_wall": 0.4,
                  "recess_sides": "none"}, id="spoke-both-min-wall-no-recess"),
    pytest.param({"hex_cell": 3, "hex_wall": 1, "recess_inner_d": 13}, id="cell-flat-on-r-in"),
])
def test_a_cutter_tangent_to_a_recess_wall_or_fillet_builds_without_a_fuzzy_boolean(
        kw: dict[str, object]) -> None:
    """CONTEXT Claude's Discretion tol= (research PITFALLS.md Pitfall 1): a hole or a
    cell can legitimately sit tangent to a recess wall -- unlike Phases 8-10, tangency
    is reachable here, and a user cannot be told their hole is placed "too exactly". On
    the default gear's recess (r_in 6.50625, r_out 12.50625, measured 2026-09-29): a
    3 mm hole with an edge exactly on r_in, on r_out, and 0.5 mm either side of each; a
    spoke's hub arc tangent to r_in and its rim arc tangent to r_out, each sharp and
    with a 1 mm fillet (D-05's analytic arcs, not the 3D operator, so tangency to the
    recess wall is a 2D sketch condition, not a kernel fillet case); a spoke web with
    both the hub and the rim at exactly MIN_WALL on a recess-less gear (tangent to
    nothing at all); a honeycomb cell's -X flat tangent to r_in (recess_inner_d 13 puts
    r_in at 6.5 mm, matching the cell centred at (8, 0)'s flat-to-axis distance). Every
    row here built one valid solid with the plain cut(*cutters) -- no row needed a
    fuzzy boolean tolerance, so none is shipped (see the comment above _cut_body's cut).
    """
    s = _build_checked(GearParams.model_validate(kw))
    assert s.isValid()


@pytest.mark.parametrize("kw", [
    pytest.param({"spoke_count": 1, "spoke_width": 2, "hub_d": 12, "rim_wall": 1,
                  "spoke_fillet": 5}, id="one-arm"),
    pytest.param({"spoke_count": 12, "spoke_width": 2.67, "hub_d": 12, "rim_wall": 1,
                  "spoke_fillet": 5}, id="twelve-arms-at-the-opening-boundary"),
    pytest.param({"spoke_count": 4, "spoke_width": 2, "hub_d": 12, "rim_wall": 8.0375,
                  "spoke_fillet": 5}, id="annulus-at-min-wall"),
    pytest.param({"spoke_count": 2, "spoke_width": 11, "hub_d": 12, "rim_wall": 1,
                  "spoke_fillet": 5}, id="eleven-mm-bars-on-a-twelve-mm-hub"),
])
def test_a_spoke_fillet_at_its_cap_builds_on_extreme_sectors(kw: dict[str, object]) -> None:
    """D-06: spoke_fillet 5 (always capped, the field's own le) on the most awkward
    sectors the rules allow -- one arm (a "C"-shaped sector spanning almost the whole
    ring), twelve arms right at the opening boundary D-16 permits, an annulus exactly
    MIN_WALL wide, and 11 mm bars on a 12 mm hub. Each builds one valid solid with the
    fillet actually capped below the request (measured 2026-09-29: 3.347, 0.202, 0.18,
    2.22 mm respectively, all < 5)."""
    p = GearParams.model_validate(kw)
    s = _build_checked(p)
    assert s.isValid()
    assert spoke_fillet_effective(p) < 5


# Row sets for the built-solid proof below (11-CONTEXT.md <interfaces>). HOLES and CELLS
# (245-251 above) are the same dicts 11-05/11-07 already use; SPOKES12/SPOKES13/
# HOLES_ACROSS are new here -- SPOKES (246) is the selector matrix's own row (hub_d 13.2,
# spoke_fillet baked in), not this plan's SPOKES12/SPOKES13 pair.
HOLES_ACROSS = {"hole_count": 6, "hole_d": 3, "hole_circle_d": 24}
SPOKES12 = {"spoke_count": 4, "spoke_width": 2, "hub_d": 12, "rim_wall": 1}
SPOKES13 = {"spoke_count": 4, "spoke_width": 2, "hub_d": 13.2, "rim_wall": 1}


def _spoke_bar_area(rh: float, rr: float, o: float) -> float:
    """One spoke bar's area (D-01/D-02), analytic: model._spoke_sector's foot() puts
    every bar corner exactly on the hub/rim circle, so the bar's straight sides sit at
    theta = +-asin(o / r) on the circle of radius r for every r between rh and rr -- the
    bar's area is the polar integral of 2 * r * asin(o / r) dr from rh to rr, whose
    antiderivative is S(r) = r^2 * asin(o / r) + o * sqrt(r^2 - o^2). Used by the sharp-
    spoke row below to compute the removed volume from the parameters, matching the
    built solid (measured 2026-09-29: formula and kernel agree to 1e-9 mm3 on the
    default gear's SPOKES12 row) rather than a pinned literal.
    """
    def s(r: float) -> float:
        return r * r * math.asin(o / r) + o * math.sqrt(r * r - o * o)
    return s(rr) - s(rh)


def _filleted_spoke_volume(p: GearParams) -> float:
    """The removed volume of the filleted spoke cutout (D-08, D-09), closed form: the
    sharp sector's area -- the spokes-sharp row's own proven formula,
    pi * (rr^2 - rh^2) - n * _spoke_bar_area -- minus the four corner cut-offs the
    fillets of radius rho = spoke_fillet_effective(p) take off it, times face_width.

    The four corners are two mirror pairs about the sector's bisector, so one hub and
    one rim cut-off are derived and each counted twice. cut_off works in the frame
    where the bar side is the line y = o (x > 0) and the sector lies on y > o. The
    fillet centre is rho off the bar side, cy = o + rho, and rc from the axis, rc = R + rho
    at the hub (the void lies outside the hub circle) or R - rho at the rim (inside the
    rim circle), so cx = sqrt(rc^2 - cy^2). The tangent point on the bar side is
    (cx, o); on the circle it is the centre scaled to R. The sharp corner (the bar side
    meets the circle) is (sqrt(R^2 - o^2), o). The cut-off is the quadrilateral
    corner / bar tangent / centre / circle tangent, less the fillet's own sector
    0.5 * rho^2 * theta (theta = pi/2 -/+ phi, phi the centre's polar angle), then
    corrected for the circle's arc, which the quadrilateral's chord replaces: the
    segment 0.5 * R^2 * (delta - sin delta), delta = phi - asin(o / R), is
    material at the hub (subtract it) and void at the rim (add it) -- the same sign
    on both is off by about 1 mm3.

    It re-derives every centre and tangent point in this polar form and never touches
    model._fillet_corner's quadratic and root choice, so a wrong root, sign or side
    there disagrees with this function instead of moving both sides together (L08).
    Measured 2026-10-03 against the built solid (cadquery 2.8.0 / cadquery-ocp
    7.9.3.1.1): SPOKES12 + spoke_fillet 1 agrees to 2.73e-12 mm3.
    """
    n = p.spoke_count
    rh = p.hub_d / 2
    rr = profile(p).rf - p.rim_wall
    o = p.spoke_width / 2
    rho = spoke_fillet_effective(p)

    def cut_off(big_r: float, inside: bool) -> float:
        rc = big_r - rho if inside else big_r + rho
        cy = o + rho
        cx = math.sqrt(rc * rc - cy * cy)
        corner = (math.sqrt(big_r * big_r - o * o), o)
        on_bar = (cx, o)
        on_circle = (cx * big_r / rc, cy * big_r / rc)
        pts = [corner, on_bar, (cx, cy), on_circle]
        quad = abs(sum(pts[i][0] * pts[(i + 1) % 4][1] - pts[(i + 1) % 4][0] * pts[i][1]
                       for i in range(4))) / 2
        phi = math.atan2(cy, cx)
        theta = math.pi / 2 + phi if inside else math.pi / 2 - phi
        delta = phi - math.asin(o / big_r)
        segment = 0.5 * big_r * big_r * (delta - math.sin(delta))
        sector = 0.5 * rho * rho * theta
        return quad - sector + segment if inside else quad - sector - segment

    area = (math.pi * (rr * rr - rh * rh) - n * _spoke_bar_area(rh, rr, o)
            - 2 * n * (cut_off(rh, False) + cut_off(rr, True)))
    return area * p.face_width


def _holes_volume(p: GearParams, recesses: int) -> float:
    """The removed volume of the holes cutout, closed form: hole_count right cylinders of
    radius hole_d / 2, each through one material thickness -- the face width less
    recess_depth on every recessed side the hole passes through (recesses 0, 1 or 2).

    Exact only while every hole lies wholly inside the recess annulus, or there is no
    recess. The composed hex-holes row is the exception: its holes reach 12 mm, past the
    hex-shifted recess outer wall at 11.994 mm (14-REVIEW WR-03), so it does not use this.

    Measured 2026-10-03 against the built solid (cadquery 2.8.0 / cadquery-ocp
    7.9.3.1.1): HOLES with recess_sides "none" agrees to 2.39e-12 mm3 (14-02).
    """
    return (p.hole_count * math.pi * (p.hole_d / 2) ** 2
            * (p.face_width - recesses * p.recess_depth))


def _hex_cells_volume(p: GearParams) -> float:
    """The removed volume of the honeycomb cutout, closed form: a regular hexagon of
    across-flats size has area (sqrt(3) / 2) * size^2, and the cut is the whole-cell
    lattice hex_cells lays out, so the volume is that area times the cell count times
    face_width.

    Measured 2026-10-03 against the built solid (cadquery 2.8.0 / cadquery-ocp
    7.9.3.1.1): CELLS with recess_sides "none" agrees to 8.87e-12 mm3 (14-02).
    """
    size, cells = hex_cells(p, profile(p).rf)
    return len(cells) * (math.sqrt(3) / 2) * size * size * p.face_width


def _honeycomb_farthest_vertex_angle(p: GearParams, rf: float) -> float:
    """The angle (radians) of the farthest honeycomb-cell vertex from the axis (D-08:
    flats face +-X, vertices +-Y -- the same polygon(6, size, circumscribed=True) vertex
    layout calc._hex_reach uses internally). Read off hex_cells(p, rf)'s own cell
    centres rather than a hand-picked value, so the probe angle in the built-solid proof
    below always matches the cell the kernel actually cut.
    """
    size, cells = hex_cells(p, rf)
    r = size / math.sqrt(3)
    farthest = max(
        ((cx + r * math.cos(math.radians(30 + 60 * i)),
          cy + r * math.sin(math.radians(30 + 60 * i)))
         for cx, cy in cells for i in range(6)),
        key=lambda v: math.hypot(*v))
    return math.atan2(farthest[1], farthest[0])


def _honeycomb_nearest_point_angle(p: GearParams, rf: float) -> float:
    """The angle (radians) of the point nearest the axis on any honeycomb-cell edge --
    a probe location, not a proof. calc._hex_reach measures the same nearest distance
    per cell (the foot of the perpendicular from the axis, clamped to the edge, via
    calc._point_segment_distance) but only returns the distance; this walks the same
    six edges (the vertex layout _honeycomb_farthest_vertex_angle above uses: flats
    face +-X) and keeps the point itself, so the probe always lands on the cell whose
    flat or corner is actually nearest -- which is not on +X for the hex or keyed bore
    (planning: hub angle 0 failed there, since neither bore centres a cell on +X).
    """
    size, cells = hex_cells(p, rf)
    r = size / math.sqrt(3)
    best_dist = math.inf
    best_point = (0.0, 0.0)
    for cx, cy in cells:
        verts = [(cx + r * math.cos(math.radians(30 + 60 * i)),
                 cy + r * math.sin(math.radians(30 + 60 * i))) for i in range(6)]
        for i in range(6):
            ax, ay = verts[i]
            bx, by = verts[(i + 1) % 6]
            dx, dy = bx - ax, by - ay
            length_sq = dx * dx + dy * dy
            t = (0.0 if length_sq == 0
                else max(0.0, min(1.0, -(ax * dx + ay * dy) / length_sq)))
            px, py = ax + t * dx, ay + t * dy
            dist = math.hypot(px, py)
            if dist < best_dist:
                best_dist, best_point = dist, (px, py)
    return math.atan2(best_point[1], best_point[0])


def _assert_the_cutout_is_what_derive_prints(
        cut: cq.Solid, plain: cq.Solid, p: GearParams, p0: GearParams, *,
        d_faces: collections.Counter[str], d_edges: int, d_volume: float,
        hub_angle: float, rim_angle: float, volume_rel: float | None = None,
        volume_abs: float | None = None) -> None:
    """Shared by the proof
    (test_each_cutout_is_exactly_what_derive_prints_on_the_built_solid) and the tripwire
    (test_the_cutout_proof_fails_when_the_cutout_step_is_skipped) -- 10-03's shape. The
    cut is exactly what derive() describes: face-type deltas, edge count, removed
    volume, and the bounding box and tip diameter unchanged by a cutout. The printed
    walls (cutout_hub_wall, cutout_rim_wall) are read back off the solid at the caller's
    own hub_angle/rim_angle: the probe points come from the printed numbers, never a
    hand-picked location (L08) -- material just inside the hub wall and void just
    outside it, void just inside the rim wall and material just outside it.

    The removed volume is held to abs=1e-9 mm3, the bar for every row whose d_volume is
    a closed form. volume_rel is for the composed-solid rows whose d_volume is a 6 dp
    literal measured on the pinned kernel, because their closed form is not derived
    here: they pass a relative one part in a million, the bar they always had.
    volume_abs is for the composed tip-chamfer holes rows, whose closed form is derived
    but whose kernel volume difference is offset ~6e-10 mm3 by the tip chamfer (14-04):
    they pass an absolute bar of their own, one the human chose as a multiple of that
    measured offset (L33), not one the executor tuned.
    """
    faces_delta = (collections.Counter(f.geomType() for f in cut.Faces())
                  - collections.Counter(f.geomType() for f in plain.Faces()))
    assert faces_delta == d_faces
    faces_reverse = (collections.Counter(f.geomType() for f in plain.Faces())
                     - collections.Counter(f.geomType() for f in cut.Faces()))
    assert not faces_reverse

    assert len(cut.Edges()) - len(plain.Edges()) == d_edges
    removed = plain.Volume() - cut.Volume()
    if volume_rel is not None:
        assert removed == pytest.approx(d_volume, rel=volume_rel)
    elif volume_abs is not None:
        assert removed == pytest.approx(d_volume, abs=volume_abs)
    else:
        assert removed == pytest.approx(d_volume, abs=1e-9)

    bb_cut, bb_plain = cut.BoundingBox(), plain.BoundingBox()
    for attr in ("xmin", "xmax", "ymin", "ymax", "zmin", "zmax"):
        assert getattr(bb_cut, attr) == pytest.approx(getattr(bb_plain, attr), abs=TOL)
    assert derive(p).tip_d == derive(p0).tip_d

    d = derive(p)
    assert d.cutout_hub_wall is not None
    assert d.cutout_rim_wall is not None
    r_hub = bore_mouth_limit(p) + d.cutout_hub_wall
    r_rim = profile(p).rf - d.cutout_rim_wall
    z = p.face_width / 2

    def at(r: float, theta: float) -> cq.Vector:
        return cq.Vector(r * math.cos(theta), r * math.sin(theta), z)

    assert cut.isInside(at(r_hub - 0.01, hub_angle)) is True
    assert cut.isInside(at(r_hub + 0.01, hub_angle)) is False
    assert cut.isInside(at(r_rim - 0.01, rim_angle)) is False
    assert cut.isInside(at(r_rim + 0.01, rim_angle)) is True


@pytest.mark.parametrize("kind", ["holes", "spokes-sharp", "spokes-filleted", "cells"])
def test_each_cutout_is_exactly_what_derive_prints_on_the_built_solid(kind: str) -> None:
    """REQ-cutout-derived-numbers on the built solid, recess_sides "none" so the recess
    fillet's own faces never mix into the cutout's delta (Task 1). Measured 2026-09-29 on
    the pinned kernel (cadquery 2.8.0 / cadquery-ocp 7.9.3.1.1): HOLES +6 CYLINDER, +18
    edges, 565.486678 mm3; sharp SPOKES12 +8 PLANE +8 CYLINDER, +48 edges, 2959.086823
    mm3 (the analytic bar-area formula below matches to 1e-9 mm3); filleted SPOKES12 +8
    PLANE +24 CYLINDER, +96 edges, removed volume _filleted_spoke_volume(p)'s closed
    form (first measurement 2026-09-29 on cadquery 2.8.0 / cadquery-ocp 7.9.3.1.1:
    2934.725405 mm3) plus 32 CIRCLE edges of radius
    spoke_fillet_effective(p) split 16/16 across the end faces; CELLS +108 PLANE, +324
    edges, 1052.220866 mm3 (18 whole cells at the requested 3 mm size, matching the
    analytic hexagon-area formula to 1e-9 mm3). Arm 0 and hole 0 sit on +X (D-03); the
    (8, 0) cell's -X flat faces +X (D-08) -- hub_angle 0 for holes and cells, pi/4 for
    spokes (the middle of sector 0, since arm 0 itself is on +X).

    The removed volume is asserted at abs=1e-9 mm3 on all four rows. Kernel-formula gap
    per row, measured 2026-10-03 on cadquery 2.8.0 / cadquery-ocp 7.9.3.1.1: holes
    2.39e-12, spokes-sharp 1.36e-12, spokes-filleted 2.73e-12, cells 8.87e-12 mm3. Phase
    11 measured this agreement but asserted it only at rel=1e-6 (about 2.9e-3 mm3 on the
    filleted row) until Phase 14.
    """
    p0 = GearParams(recess_sides="none")
    plain = _build_checked(p0)

    if kind == "holes":
        p = GearParams.model_validate({**HOLES, "recess_sides": "none"})
        cut = _build_checked(p)
        _assert_the_cutout_is_what_derive_prints(
            cut, plain, p, p0,
            d_faces=collections.Counter({"CYLINDER": 6}), d_edges=18,
            d_volume=_holes_volume(p, 0),
            hub_angle=0.0, rim_angle=0.0)
    elif kind == "spokes-sharp":
        p = GearParams.model_validate({**SPOKES12, "recess_sides": "none"})
        cut = _build_checked(p)
        pr = profile(p)
        rh, rr, o = p.hub_d / 2, pr.rf - p.rim_wall, p.spoke_width / 2
        volume = (math.pi * (rr * rr - rh * rh)
                 - p.spoke_count * _spoke_bar_area(rh, rr, o)) * p.face_width
        _assert_the_cutout_is_what_derive_prints(
            cut, plain, p, p0,
            d_faces=collections.Counter({"PLANE": 8, "CYLINDER": 8}), d_edges=48,
            d_volume=volume, hub_angle=math.pi / 4, rim_angle=math.pi / 4)
    elif kind == "spokes-filleted":
        p = GearParams.model_validate({**SPOKES12, "spoke_fillet": 1, "recess_sides": "none"})
        cut = _build_checked(p)
        _assert_the_cutout_is_what_derive_prints(
            cut, plain, p, p0,
            d_faces=collections.Counter({"PLANE": 8, "CYLINDER": 24}), d_edges=96,
            d_volume=_filleted_spoke_volume(p),
            hub_angle=math.pi / 4, rim_angle=math.pi / 4)
        rho = spoke_fillet_effective(p)
        fillet_edges = [e for e in cut.Edges()
                        if e.geomType() == "CIRCLE" and abs(e.radius() - rho) < TOL]
        assert len(fillet_edges) == 32
        assert (collections.Counter(round(e.startPoint().z / p.face_width) for e in fillet_edges)
                == {0: 16, 1: 16})
    else:  # cells
        p = GearParams.model_validate({**CELLS, "recess_sides": "none"})
        cut = _build_checked(p)
        pr = profile(p)
        _, cells = hex_cells(p, pr.rf)
        d = derive(p)
        assert d.hex_cell_count == len(cells)
        volume = _hex_cells_volume(p)
        rim_angle = _honeycomb_farthest_vertex_angle(p, pr.rf)
        _assert_the_cutout_is_what_derive_prints(
            cut, plain, p, p0,
            d_faces=collections.Counter({"PLANE": 6 * d.hex_cell_count}), d_edges=324,
            d_volume=volume, hub_angle=0.0, rim_angle=rim_angle)


# The cells row's rim probe sits on the farthest cell vertex, as in the proof above: the
# angle 0.0 the other rows use is not on the rim wall of a honeycomb (14-04's control call
# failed there on the unpatched build).
_CELLS_NO_RECESS = GearParams.model_validate({**CELLS, "recess_sides": "none"})


@pytest.mark.parametrize(
    ("kw", "d_faces", "d_edges", "d_volume", "hub_angle", "rim_angle"), [
    pytest.param({**HOLES, "recess_sides": "none"},
                 collections.Counter({"CYLINDER": 6}), 18,
                 _holes_volume(GearParams.model_validate(
                     {**HOLES, "recess_sides": "none"}), 0),
                 0.0, 0.0, id="holes"),
    pytest.param({**SPOKES12, "spoke_fillet": 1, "recess_sides": "none"},
                 collections.Counter({"PLANE": 8, "CYLINDER": 24}), 96,
                 _filleted_spoke_volume(GearParams.model_validate(
                     {**SPOKES12, "spoke_fillet": 1, "recess_sides": "none"})),
                 math.pi / 4, math.pi / 4, id="spokes-filleted"),
    pytest.param({**CELLS, "recess_sides": "none"},
                 collections.Counter({"PLANE": 108}), 324,
                 _hex_cells_volume(_CELLS_NO_RECESS), 0.0,
                 _honeycomb_farthest_vertex_angle(
                     _CELLS_NO_RECESS, profile(_CELLS_NO_RECESS).rf), id="cells"),
])
def test_the_cutout_proof_fails_when_the_cutout_step_is_skipped(
        monkeypatch: pytest.MonkeyPatch, kw: dict[str, object],
        d_faces: collections.Counter[str], d_edges: int, d_volume: float,
        hub_angle: float, rim_angle: float) -> None:
    """L08's failure, 10-03's tripwire shape: patches _cut_body to a no-op -- the cut
    solid comes back identical to the plain one, so every delta the proof checks reads
    zero -- and shows the proof above fail while derive() still prints the cutout's
    wall, the number the part no longer matches.

    The same call runs first on the unpatched build and passes, so the raise below can
    only come from the skipped cutout. Before 14-04 the holes and cells rows passed 6 dp
    literals that sat +3.54e-7 and +4.02e-7 mm3 off their closed forms (14-REVIEW WR-02),
    so the abs=1e-9 volume line raised on a correct build too, and the raise could not
    tell the patched build from the unpatched one.
    """
    p0 = GearParams(recess_sides="none")
    p = GearParams.model_validate(kw)
    # p0 has no cutout pattern, so _cut_body's last branch returns the solid unchanged
    # whether or not it is patched: one plain build serves the control and the patched call.
    plain = _build_checked(p0)
    _assert_the_cutout_is_what_derive_prints(
        _build_checked(p), plain, p, p0,
        d_faces=d_faces, d_edges=d_edges, d_volume=d_volume,
        hub_angle=hub_angle, rim_angle=rim_angle)
    monkeypatch.setattr("spur.model._cut_body", lambda solid, _p, _pr: solid)
    assert derive(p).cutout_hub_wall is not None  # the number still prints -- L08's failure
    with pytest.raises(AssertionError):
        _assert_the_cutout_is_what_derive_prints(
            _build_checked(p), plain, p, p0,
            d_faces=d_faces, d_edges=d_edges, d_volume=d_volume,
            hub_angle=hub_angle, rim_angle=rim_angle)


def test_the_cutout_proof_fails_when_a_rim_corner_tangent_root_moves(
        monkeypatch: pytest.MonkeyPatch) -> None:
    """L08's failure, 10-03/11-08's tripwire shape, for the filleted spoke's rim corners:
    the inside=True tangent root of model._fillet_corner moves by 1e-6 mm. The part
    still builds, derive() still prints spoke_fillet_effective, the face and edge deltas
    are the right ones, and the removed volume still agrees with the closed form at the
    pre-phase rel=1e-6 bar -- only the abs=1e-9 assertion sees it.

    The shift is 1e-6 mm, not 0.01 mm: 0.01 mm moved the removed volume by 2.522 mm3
    (planning, 2026-10-02), which the old relative bar catches too, so it could not show
    the tightening is load-bearing. 1e-6 mm moves it by 2.522e-4 mm3 (measured
    2026-10-03, gap to the oracle 2.522e-4 mm3, relative 8.59e-8) -- inside the old bar
    and about 2.5e5 times the new one, so loosening the bar back turns this test red.
    """
    def perturbed(p0: cq.Vector, p1: cq.Vector, rf: float, rho: float, gap_side: int,
                  inside: bool = False) -> tuple[cq.Vector, cq.Vector, cq.Vector]:
        if not inside:  # tooth roots and hub corners stay byte-identical
            return _fillet_corner(p0, p1, rf, rho, gap_side)
        u = (p1 - p0).normalized()
        n = cq.Vector(-u.y, u.x, 0) * gap_side
        q = p0 + n * rho
        b = q.dot(u)
        rc = rf - rho
        root = math.sqrt(max(0.0, b * b - (q.dot(q) - rc ** 2)))
        t = -b - root + 1e-6
        centre = q + u * t
        on_line = p0 + u * t
        on_root = centre * (rf / rc)
        mid = centre + ((on_line + on_root) * 0.5 - centre).normalized() * rho
        return on_root, mid, on_line

    monkeypatch.setattr("spur.model._fillet_corner", perturbed)
    p0 = GearParams(recess_sides="none")
    p = GearParams.model_validate({**SPOKES12, "spoke_fillet": 1, "recess_sides": "none"})
    assert derive(p).spoke_fillet_effective is not None  # the number still prints
    plain, cut = _build_checked(p0), _build_checked(p)
    d_faces = collections.Counter({"PLANE": 8, "CYLINDER": 24})
    faces_delta = (collections.Counter(f.geomType() for f in cut.Faces())
                  - collections.Counter(f.geomType() for f in plain.Faces()))
    assert faces_delta == d_faces
    assert len(cut.Edges()) - len(plain.Edges()) == 96
    d_volume = _filleted_spoke_volume(p)
    assert plain.Volume() - cut.Volume() == pytest.approx(d_volume, rel=1e-6)
    with pytest.raises(AssertionError):
        _assert_the_cutout_is_what_derive_prints(
            cut, plain, p, p0, d_faces=d_faces, d_edges=96, d_volume=d_volume,
            hub_angle=math.pi / 4, rim_angle=math.pi / 4)


@pytest.mark.parametrize("kw", [
    pytest.param(HOLES, id="holes"),
    pytest.param({**SPOKES12, "spoke_fillet": 1}, id="spokes-filleted"),
    pytest.param(CELLS, id="cells"),
])
def test_the_same_cutout_link_builds_the_same_solid_twice(kw: dict[str, object]) -> None:
    """The same-link-same-part property (L05), for each body cutout pattern, on the
    default gear (its own recess intact): two independent builds of one parameter set
    agree on topology and volume. Uses _build_checked, bypassing the lru_cache, so both
    builds actually run the kernel."""
    p = GearParams.model_validate(kw)
    a = _build_checked(p)
    b = _build_checked(p)
    assert len(a.Faces()) == len(b.Faces())
    assert len(a.Edges()) == len(b.Edges())
    assert a.Volume() == pytest.approx(b.Volume(), rel=1e-9)


def _assert_the_recess_fillet_survives(cut: cq.Solid, p: GearParams, torus: int) -> None:
    """REQ-cutout-composes' counted proof (Task 2): with both recesses, the floor
    fillet survives on every floor edge each cutout pattern leaves -- no sharp
    floor-to-wall circle remains anywhere on the finished solid -- and the TORUS face
    count is the one the pinned kernel reads. What a through-cut does to a toroidal
    fillet face (split into pieces, never removed from a surviving edge) is measured on
    the pinned kernel and pinned here (research A4), not derived: no closed form gives
    the fragment count after an arbitrary boolean cut.
    """
    assert cut.isValid()
    assert len(cut.Solids()) == 1

    rr = recess_radii(p, profile(p).rf)
    assert rr is not None, "the row must carry a recess to prove the fillet survives"
    heights: list[float] = []
    if p.recess_sides in ("both", "bottom"):
        heights.append(p.recess_depth)
    if p.recess_sides in ("both", "top"):
        heights.append(p.face_width - p.recess_depth)

    try:
        sharp = len(_groove_floor_edges(cut, rr, heights))
    except BuildError:
        sharp = 0
    assert sharp == 0

    assert sum(1 for f in cut.Faces() if f.geomType() == "TORUS") == torus


@pytest.mark.parametrize(("kw", "torus"), [
    pytest.param(HOLES, 4, id="d-flat-holes"),
    pytest.param(HOLES_ACROSS, 14, id="d-flat-holes-across"),
    pytest.param({**SPOKES12, "spoke_fillet": 1}, 20, id="d-flat-spokes"),
    pytest.param(CELLS, 14, id="d-flat-cells"),
    pytest.param({**HOLES, "bore_flat": 0}, 4, id="round-holes"),
    pytest.param({**SPOKES12, "spoke_fillet": 1, "bore_flat": 0}, 20, id="round-spokes"),
    pytest.param({**CELLS, "bore_flat": 0}, 14, id="round-cells"),
    pytest.param({**HOLES, "bore_hex": 6}, 14, id="hex-holes"),
    pytest.param({**SPOKES12, "spoke_fillet": 1, "bore_hex": 6}, 12, id="hex-spokes"),
    pytest.param({**CELLS, "bore_hex": 6}, 40, id="hex-cells"),
    pytest.param({**HOLES, "keyway_width": 3, "keyway_depth": 1.4, "bore_flat": 0},
                 4, id="keyed-holes"),
    # SPOKES13 (hub_d 13.2, clears the keyed round bore's 6.179 mm mouth): not probed in
    # planning (11-CONTEXT.md <interfaces>) -- measured here on the pinned kernel,
    # 2026-09-29.
    pytest.param({**SPOKES13, "spoke_fillet": 1, "keyway_width": 3, "keyway_depth": 1.4,
                  "bore_flat": 0}, 12, id="keyed-spokes"),
    pytest.param({**CELLS, "keyway_width": 3, "keyway_depth": 1.4, "bore_flat": 0},
                 4, id="keyed-cells"),
])
def test_the_recess_floor_fillet_survives_every_cutout_on_every_bore(
        kw: dict[str, object], torus: int) -> None:
    """REQ-cutout-composes' counted proof: with both recesses (the field's own
    default), on every bore shape (D-flat, round, hex, keyed round) and every pattern,
    the recess floor fillet survives on every floor edge the cutout leaves -- no sharp
    floor-to-wall circle anywhere on the finished solid. TORUS counts are the pinned
    kernel's own, measured 2026-09-29; every one matches the planning probe in
    11-CONTEXT.md <interfaces> except keyed-spokes, which planning did not measure."""
    p = GearParams.model_validate(kw)
    cut = _build_checked(p)
    _assert_the_recess_fillet_survives(cut, p, torus)


@pytest.mark.parametrize(("kw", "torus"), [
    pytest.param({**HOLES_ACROSS}, 14, id="d-flat-holes-across"),
    pytest.param({**CELLS}, 14, id="d-flat-cells"),
])
def test_the_fillet_survival_proof_fails_when_the_recess_fillet_is_skipped(
        monkeypatch: pytest.MonkeyPatch, kw: dict[str, object], torus: int) -> None:
    """The survival proof's own tripwire: with recess_fillet patched to 0, the groove
    floor's sharp corners survive the cutout instead of being rounded away, so
    _groove_floor_edges matches them rather than raising -- the proof's own
    assert sharp == 0 is what catches a skipped fillet here, not a raised BuildError
    (measured 2026-09-29: both rows leave 14 sharp floor circles with the fillet
    skipped)."""
    monkeypatch.setattr("spur.model.recess_fillet", lambda _p, _rf: 0.0)
    p = GearParams.model_validate(kw)
    cut = _build_checked(p)
    with pytest.raises(AssertionError):
        _assert_the_recess_fillet_survives(cut, p, torus)


# --- Composition pass (12-06-PLAN.md): the tier-2 pairs no earlier test builds ---------

TIPPED = {"bore_chamfer": 0, "recess_fillet": 0, "tip_chamfer": 1.75}
# 10-03's proof preconditions (sharp bore-rim and groove-floor edges, so both selectors
# have something to count) plus the default gear's own pitch-circle cap (10 D-02).

COMPOSED_BORES: dict[str, dict[str, float]] = {
    "d-flat": {},
    "round": {"bore_flat": 0},
    "hex": {"bore_hex": 6},
    "keyed": {"bore_flat": 0, "keyway_width": 3, "keyway_depth": 1.4},
}
COMPOSED_CUTOUTS: dict[str, dict[str, float]] = {
    "holes": HOLES,
    "spokes": SPOKES,  # already dict[str, float] -- hub_d 13.2
    "cells": CELLS,
}
# SPOKES' 13.2 mm hub clears the keyed bore's 6.179 mm floor-corner mouth (11-08's own
# adjacency), so one cutout dict works on every bore shape here.

_build_reference = functools.cache(_build_checked)
# The no-cutout reference for each bore is built once per session (measured saving,
# planning: 8 builds of ~0.8 s each); only these tests use it and none of them
# monkeypatches the kernel, so a cached solid never goes stale under a patched build.


@pytest.mark.parametrize(("bore", "cutout", "d_faces", "d_edges", "d_volume"), [
    # Every delta below is measured on the pinned kernel this session and matches the
    # planning probe in 12-06-PLAN.md <interfaces> exactly -- no difference to record.
    # A cutout's own delta is bore-agnostic (d-flat and round read identical deltas):
    # it is a difference against the SAME bore's own no-cutout reference, so whatever
    # the bore itself contributes to face/edge/volume cancels out of the subtraction.
    # A None d_volume is not pinned: the test body derives it from _holes_volume and
    # asserts it at the bar the docstring names (14-04).
    pytest.param("d-flat", "holes", collections.Counter({"CYLINDER": 6}),
                 18, None, id="d-flat-holes"),
    pytest.param("d-flat", "spokes", collections.Counter({"PLANE": 8, "CYLINDER": 32}),
                 144, 1567.635231, id="d-flat-spokes"),
    pytest.param("d-flat", "cells", collections.Counter({"PLANE": 108, "CYLINDER": 10}),
                 390, 491.093432, id="d-flat-cells"),
    pytest.param("round", "holes", collections.Counter({"CYLINDER": 6}),
                 18, None, id="round-holes"),
    pytest.param("round", "spokes", collections.Counter({"PLANE": 8, "CYLINDER": 32}),
                 144, 1567.635231, id="round-spokes"),
    pytest.param("round", "cells", collections.Counter({"PLANE": 108, "CYLINDER": 10}),
                 390, 491.093432, id="round-cells"),
    pytest.param("hex", "holes", collections.Counter({"CYLINDER": 16}),
                 84, 263.92552, id="hex-holes"),
    pytest.param("hex", "spokes", collections.Counter({"PLANE": 8, "CYLINDER": 32}),
                 144, 1708.871909, id="hex-spokes"),
    pytest.param("hex", "cells", collections.Counter({"PLANE": 144, "CYLINDER": 36}),
                 648, 686.855148, id="hex-cells"),
    pytest.param("keyed", "holes", collections.Counter({"CYLINDER": 6}),
                 18, None, id="keyed-holes"),
    pytest.param("keyed", "spokes", collections.Counter({"PLANE": 8, "CYLINDER": 32}),
                 144, 1547.065402, id="keyed-spokes"),
    pytest.param("keyed", "cells", collections.Counter({"PLANE": 72}),
                 216, 327.357603, id="keyed-cells"),
])
def test_every_feature_proof_holds_on_a_tip_chamfered_gear_with_each_cutout_on_each_bore(
        bore: str, cutout: str, d_faces: collections.Counter[str],
        d_edges: int, d_volume: float | None) -> None:
    """D-07 tier 2, D-09, ROADMAP SC1 on the built solid: the tip chamfer (1.75 mm, the
    default gear's own cap) applied together with each cutout on each bore, on one
    composed solid -- the features' own built-solid proofs (10-03's
    _assert_only_the_tip_arcs_were_chamfered, 11-08's
    _assert_the_cutout_is_what_derive_prints) run unchanged on that one solid, never a
    new proof shape (D-09). Every face-type and edge delta below is measured on the
    pinned kernel and pinned. The removed volume of the d-flat, round and keyed holes
    rows (both recesses) is `_holes_volume(p, 2)`, the web formula, asserted at
    abs=1e-8 mm3 (14-04, the human's answer at its Task 2 checkpoint). Measured
    2026-10-03 on cadquery 2.8.0 / cadquery-ocp 7.9.3.1.1, the kernel-formula gaps are
    d-flat 5.85e-10, round 5.94e-10 and keyed 6.55e-10 mm3. The tip chamfer causes them:
    the d-flat row without it measured 1.36e-12 mm3. That is why those three rows do not
    run at abs=1e-9, which would leave them about 1.5x of headroom; 1e-8 is about 15x
    their largest gap. Every other row keeps a 6 dp literal at volume_rel=1e-6, because
    its closed form is not derived here: the spokes and cells rows straddle the recess
    walls (a polar or polygon-versus-circle integral split at the recess radii), and on
    the hex bore the holes' 12 mm reach crosses the recess outer wall, pulled to
    11.994 mm (14-REVIEW WR-03). See
    docs/tech_debt/active/2026-10-03-composed-cutout-volume-literals-pinned-at-six-places.md.

    The keyed-spokes row sits at the phase's own tightest adjacency: SPOKES' 13.2 mm
    hub wall clears the keyed bore's floor-corner mouth (6.179 mm) by only 0.021 mm
    above MIN_WALL, so a single valid solid there is the composition pass's own edge
    case, not the easy middle of the range.
    """
    kw = {**TIPPED, **COMPOSED_BORES[bore], **COMPOSED_CUTOUTS[cutout]}
    p = GearParams.model_validate(kw)
    p_no_tip = GearParams.model_validate({k: v for k, v in kw.items() if k != "tip_chamfer"})
    p_no_cut = GearParams.model_validate({**TIPPED, **COMPOSED_BORES[bore]})
    cut = _build_checked(p)

    _assert_only_the_tip_arcs_were_chamfered(cut, _build_checked(p_no_tip), p, p_no_tip)

    if cutout == "holes":
        hub_angle = rim_angle = 0.0
    elif cutout == "spokes":
        # The middle of sector 0 (arm 0 itself sits on +X, 11-08's own row).
        hub_angle = rim_angle = math.pi / 4
    else:  # cells -- the nearest cell is not on +X for the hex or keyed bore, so the
        # hub probe reads the nearest point of the nearest cell, never a fixed angle.
        pr = profile(p)
        hub_angle = _honeycomb_nearest_point_angle(p, pr.rf)
        rim_angle = _honeycomb_farthest_vertex_angle(p, pr.rf)

    volume_rel: float | None = 1e-6
    volume_abs: float | None = None
    if d_volume is None:
        # The six holes lie wholly inside the recess annulus, so the web formula is exact.
        d_volume, volume_rel, volume_abs = _holes_volume(p, 2), None, 1e-8
    _assert_the_cutout_is_what_derive_prints(
        cut, _build_reference(p_no_cut), p, p_no_cut,
        d_faces=d_faces, d_edges=d_edges, d_volume=d_volume,
        hub_angle=hub_angle, rim_angle=rim_angle,
        volume_rel=volume_rel, volume_abs=volume_abs)


@pytest.mark.parametrize(("cutout", "d_faces", "d_edges", "d_volume", "torus"), [
    # Measured on the pinned kernel this session, matching 12-06-PLAN.md <interfaces>
    # exactly -- no difference to record. d_faces/d_edges/d_volume are the cutout's own
    # delta against the same-recess no-cutout reference; torus is the finished solid's
    # own TORUS face count (_assert_the_recess_fillet_survives's own proof, 11-08). A None
    # d_volume is not pinned: the test body derives it from _holes_volume (14-04).
    pytest.param("holes", collections.Counter({"CYLINDER": 6}), 18, None, 2,
                 id="holes"),
    pytest.param("spokes", collections.Counter({"PLANE": 11, "CYLINDER": 28, "TORUS": 4}),
                 144, 2184.523725, 6, id="spokes"),
    pytest.param("cells", collections.Counter({"PLANE": 108, "CYLINDER": 5, "TORUS": 5}),
                 409, 772.209087, 7, id="cells"),
])
def test_the_recess_fillet_and_cutout_proofs_hold_with_a_single_sided_recess(
        cutout: str, d_faces: collections.Counter[str], d_edges: int,
        d_volume: float | None, torus: int) -> None:
    """D-09: the single-sided pairs no existing matrix builds (11-08's own matrix at
    test_the_recess_floor_fillet_survives_every_cutout_on_every_bore is both recesses
    only). Each cutout composed with a top-only recess, on the default bore, default
    bore chamfer (0.4 mm) and default recess fillet (0.5 mm), no tip chamfer.
    _assert_the_recess_fillet_survives (11-08) proves the floor fillet still rounds
    away every sharp corner the cutout leaves and reads the pinned kernel's own TORUS
    count on the finished solid; _assert_the_cutout_is_what_derive_prints (10-03/11-08)
    proves the cutout's own delta against the same-recess no-cutout reference. Every
    count below is measured on the pinned kernel and pinned. The holes row's removed
    volume is `_holes_volume(p, 1)`, the web formula with one recess, asserted at
    abs=1e-9 mm3; measured 2026-10-03 on cadquery 2.8.0 / cadquery-ocp 7.9.3.1.1, its
    kernel-formula gap is 2.79e-12 mm3. The spokes and cells rows keep a 6 dp literal at
    volume_rel=1e-6, because their closed form is not derived here: they straddle the
    recess walls, and the floor fillet's torus enters the integral. See
    docs/tech_debt/active/2026-10-03-composed-cutout-volume-literals-pinned-at-six-places.md.
    """
    p0 = GearParams(recess_sides="top")
    p = GearParams.model_validate({**COMPOSED_CUTOUTS[cutout], "recess_sides": "top"})
    cut = _build_checked(p)

    _assert_the_recess_fillet_survives(cut, p, torus)

    if cutout == "holes":
        hub_angle = rim_angle = 0.0
    elif cutout == "spokes":
        hub_angle = rim_angle = math.pi / 4
    else:  # cells
        pr = profile(p)
        hub_angle = _honeycomb_nearest_point_angle(p, pr.rf)
        rim_angle = _honeycomb_farthest_vertex_angle(p, pr.rf)

    volume_rel: float | None = 1e-6
    if d_volume is None:
        # The six holes lie wholly inside the top recess annulus, so the web formula is exact.
        d_volume, volume_rel = _holes_volume(p, 1), None
    _assert_the_cutout_is_what_derive_prints(
        cut, _build_reference(p0), p, p0,
        d_faces=d_faces, d_edges=d_edges, d_volume=d_volume,
        hub_angle=hub_angle, rim_angle=rim_angle, volume_rel=volume_rel)


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
