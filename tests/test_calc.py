import itertools
import math

import pytest
from pydantic import ValidationError

from spur.calc import (
    MIN_WALL,
    TIP_CHAMFER_MARGIN,
    DerivedDimensions,
    bore_mouth_limit,
    bore_radius,
    bore_rim_limit,
    centre_distance,
    cutout_walls,
    derive,
    hex_across_flats,
    hole_gap,
    inv,
    keyway_corner_radius,
    keyway_flat_wall,
    keyway_width_effective,
    profile,
    recess_radii,
    root_fillet,
    span_measurement,
    spline_start,
    tip_chamfer_effective,
)
from spur.params import GearParams


def test_default_dimensions() -> None:
    d = derive(GearParams())
    assert d.pitch_d == pytest.approx(33.25)
    assert d.tip_d == pytest.approx(36.75)
    assert d.root_d == pytest.approx(28.875)
    assert d.base_d == pytest.approx(33.25 * math.cos(math.radians(25)), abs=1e-3)
    assert d.web == pytest.approx(3.5)
    # The recess capping added in the 2026-09-21 review must not move the stock gear:
    # every shareable link that omits these fields depends on them.
    assert d.recess_id == pytest.approx(13.013)
    assert d.recess_od == pytest.approx(25.013)
    assert d.recess_fillet == pytest.approx(0.5)
    assert d.warnings == ()
    # D-01, edge: empty -- no mate was asked about, so both mate fields are present
    # and null, never omitted.
    assert d.mate_teeth is None
    assert d.centre_distance is None


def test_a_derived_dimensions_result_cannot_be_changed() -> None:
    """A result shared between readers cannot change under them (D-09, edge:
    concurrency): DerivedDimensions is frozen, so every field assignment raises -- and
    its one collection field is a tuple, so it cannot be edited in place either."""
    d = derive(GearParams())
    for name in DerivedDimensions.model_fields:
        with pytest.raises(ValidationError, match="frozen"):
            setattr(d, name, None)
    # `frozen` is shallow: a `list` field would still take `.append()`/`.clear()` from
    # any holder of the object. The type is the guarantee, so assert the type.
    assert isinstance(d.warnings, tuple)


def test_caliper_reading_is_short_for_odd_tooth_counts() -> None:
    odd, even = derive(GearParams(teeth=19)), derive(GearParams(teeth=20))
    assert odd.caliper_over_tips < odd.tip_d
    assert even.caliper_over_tips == even.tip_d


@pytest.mark.parametrize(("m", "pa", "k", "w"), [
    (1.75, 20, 3, 13.381),   # hand-checked Wildhaber span
    (1.75, 25, 3, 13.360),
    (1.0, 20, 3, 7.646),
])
def test_span_measurement(m: float, pa: float, k: int, w: float) -> None:
    p = GearParams(module=m, pressure_angle=pa, bore_d=0, recess_sides="none")
    kk, ww = span_measurement(p)
    assert kk == k
    assert ww == pytest.approx(w, abs=2e-3)


def test_higher_pressure_angle_gives_finer_tips_and_thicker_roots() -> None:
    a, b = derive(GearParams(pressure_angle=20)), derive(GearParams(pressure_angle=25))
    assert b.tip_thickness < a.tip_thickness
    assert b.root_thickness > a.root_thickness


def test_centre_distance_unshifted_and_shifted() -> None:
    p = GearParams()
    assert centre_distance(p, 40) == pytest.approx(1.75 * 59 / 2)
    shifted = centre_distance(GearParams(profile_shift=0.3), 40)
    assert shifted is not None
    assert shifted > 1.75 * 59 / 2


def test_root_fillet_is_capped_with_a_warning() -> None:
    d = derive(GearParams(teeth=80, module=0.5, bore_d=5, bore_flat=0))
    assert d.root_fillet < 0.5
    assert any("Root fillet reduced" in w for w in d.warnings)


@pytest.mark.parametrize(("kw", "field"), [
    ({"bore_flat": 3}, "bore_flat"),
    ({"recess_depth": 3.6}, "recess_depth"),
    ({"pressure_angle": 35, "profile_shift": 1}, "pressure_angle"),
    ({"bore_d": 30}, "bore_d"),
])
def test_infeasible_parameters_name_their_fields(kw: dict[str, object], field: str) -> None:
    with pytest.raises(ValidationError) as exc:
        GearParams.model_validate(kw)
    err = exc.value.errors()[0]
    assert err["type"] == "infeasible"
    assert field in err["ctx"]["fields"]


def test_no_bore_ignores_d_flat() -> None:
    assert GearParams(bore_d=0).bore_flat == 8.0


def test_the_bore_rim_limit_is_the_bore_radius_for_round_and_d_flat_bores() -> None:
    """bore_rim_limit(p) is the exact geometric bound, no slack (D-18): round and D-flat
    both reduce to bore_radius(p), because the D-flat hole is the round hole intersected
    with a rectangle -- a strict subset of the circle."""
    for p in (GearParams(bore_flat=0), GearParams(), GearParams(bore_d=0)):
        assert bore_rim_limit(p) == bore_radius(p)
    assert bore_rim_limit(GearParams(bore_flat=0)) == pytest.approx(4.575)
    assert bore_rim_limit(GearParams()) == pytest.approx(4.575)
    assert bore_rim_limit(GearParams(bore_d=0)) == 0.0


def test_the_bore_rim_limit_is_a_hex_bores_circumradius() -> None:
    """bore_rim_limit(p) for a hex is the circumradius, across-flats over sqrt(3)
    (L26's seam); bore_mouth_limit(p) carries the chamfer to the corners at 2c/sqrt(3),
    not straight out at c (research PITFALLS.md Pitfall 1)."""
    assert bore_rim_limit(GearParams(bore_hex=6)) == pytest.approx(6.15 / math.sqrt(3))
    assert bore_rim_limit(GearParams(bore_hex=6, bore_d=0)) == pytest.approx(
        6.15 / math.sqrt(3))
    assert hex_across_flats(GearParams(bore_hex=6)) == pytest.approx(6.15)
    assert bore_mouth_limit(GearParams(bore_hex=6)) == pytest.approx(
        (6.15 + 2 * 0.4) / math.sqrt(3))
    assert bore_mouth_limit(GearParams(bore_flat=0)) == pytest.approx(4.975)
    assert bore_mouth_limit(GearParams(bore_d=0)) == 0.0


@pytest.mark.parametrize(("kw", "flats", "corners", "bore"), [
    ({"bore_hex": 6}, 6.15, 7.101, None),
    ({"bore_hex": 6, "bore_clearance": 0}, 6.0, 6.928, None),
    ({"bore_hex": 6, "bore_d": 0}, 6.15, 7.101, None),
    ({}, None, None, 9.15),
    ({"bore_d": 0}, None, None, None),
])
def test_a_hex_bore_reports_across_flats_and_corners_and_no_round_diameter(
        kw: dict[str, object], flats: float | None, corners: float | None,
        bore: float | None) -> None:
    """The three bore numbers derive() prints, compared with == because they are
    rounded once, at construction (D-10)."""
    d = derive(GearParams.model_validate(kw))
    assert d.hex_across_flats == flats
    assert d.hex_across_corners == corners
    assert d.bore_effective == bore


def test_a_hex_bore_is_refused_when_its_corners_reach_the_root_and_builds_one_step_inside() -> None:
    """D-03a: the corner rule ignores the chamfer (it fires with bore_chamfer=0), and
    refuses one step past the root -- boundary values measured on the pinned kernel,
    2026-09-26."""
    GearParams(bore_hex=24.15, bore_chamfer=0)  # one step inside: builds
    with pytest.raises(ValidationError) as exc:
        GearParams.model_validate({"bore_hex": 24.2, "bore_chamfer": 0})
    err = exc.value.errors()[0]
    assert err["type"] == "infeasible"
    assert err["ctx"]["fields"] == ["bore_hex"]
    assert err["msg"] == (
        "Hex bore is too large for the root diameter: its corners (28.12 mm across) "
        "must stay 0.4 mm inside the root circle (28.88 mm); reduce bore_hex.")

    # The default chamfer alone does not stack the chamfer rule onto the corner rule:
    # only bore_hex is named.
    with pytest.raises(ValidationError) as exc:
        GearParams.model_validate({"bore_hex": 24.2})
    assert exc.value.errors()[0]["ctx"]["fields"] == ["bore_hex"]


def test_a_hex_bore_chamfer_that_carries_the_corners_to_the_root_is_refused_naming_both() -> None:
    """D-03b: the chamfered-corner rule, bound measured on the pinned kernel,
    2026-09-26 -- boundary one step either side of 23.4."""
    GearParams(bore_hex=23.35)  # one step inside: builds
    with pytest.raises(ValidationError) as exc:
        GearParams.model_validate({"bore_hex": 23.4})
    err = exc.value.errors()[0]
    assert err["type"] == "infeasible"
    assert err["ctx"]["fields"] == ["bore_chamfer", "bore_hex"]
    assert err["msg"] == (
        "Bore chamfer is too large for this hex bore: at the corners it reaches "
        "28.12 mm across, which must stay 0.4 mm inside the root circle (28.88 mm); "
        "reduce bore_chamfer or bore_hex.")


def test_a_hex_bore_skips_the_round_bore_rules() -> None:
    """D-03: with bore_hex > 0 the round-profile rules do not run -- a bore_flat that
    would fail the D-flat range check and a bore_d that would fail the round
    root-diameter check both build under a hex. The shape-independent chamfer-vs-face-
    width rule still applies and names only bore_chamfer."""
    GearParams(bore_hex=6, bore_flat=3)   # round D-flat range would refuse bore_flat=3
    GearParams(bore_hex=6, bore_d=30)     # round root-diameter rule would refuse bore_d=30

    with pytest.raises(ValidationError) as exc:
        GearParams.model_validate({"bore_hex": 6, "face_width": 5, "bore_chamfer": 2.5})
    err = exc.value.errors()[0]
    assert err["type"] == "infeasible"
    assert err["ctx"]["fields"] == ["bore_chamfer"]


@pytest.mark.parametrize(("kw", "expected"), [
    ({"bore_hex": 6},
     "Hex bore replaces the round profile: bore_d (9 mm) and bore_flat (8 mm) are ignored."),
    ({"bore_hex": 6, "bore_flat": 0},
     "Hex bore replaces the round profile: bore_d (9 mm) is ignored."),
    ({"bore_hex": 6, "bore_d": 0},
     "Hex bore replaces the round profile: bore_flat (8 mm) is ignored."),
    ({"bore_hex": 6, "bore_d": 0, "bore_flat": 0}, None),
    ({"bore_hex": 6, "bore_d": 12.7, "bore_flat": 11.5},
     "Hex bore replaces the round profile: bore_d (12.7 mm) and bore_flat (11.5 mm) "
     "are ignored."),
])
def test_a_hex_bore_warns_about_each_round_field_it_ignores(
        kw: dict[str, object], expected: str | None) -> None:
    """D-02: one sentence, naming only the non-zero ignored fields with their values;
    no warning at all when both round fields are zero."""
    d = derive(GearParams.model_validate(kw))
    if expected is None:
        assert not any(w.startswith("Hex bore replaces") for w in d.warnings)
    else:
        assert expected in d.warnings


def test_a_keyway_reaches_its_floor_corner_and_the_recess_clears_it() -> None:
    """D-06/D-09/D-14: the keyway's own two helpers, bore_mouth_limit taking the max
    with the corner, and recess_radii() yielding to it -- all 0.0/unchanged with no
    keyway."""
    k = GearParams(keyway_width=3, keyway_depth=1.4)
    assert keyway_width_effective(k) == pytest.approx(3.15)
    c = keyway_corner_radius(k)
    assert c == pytest.approx(math.hypot(5.975, 1.575))
    assert bore_mouth_limit(k) == pytest.approx(c)
    # The chamfer dominates once it reaches past the (un-chamfered) keyway corner.
    assert bore_mouth_limit(GearParams(keyway_width=3, keyway_depth=1.4,
                                       bore_chamfer=3)) == pytest.approx(7.575)
    rr = recess_radii(k, profile(k).rf)
    assert rr == pytest.approx((c + MIN_WALL, c + MIN_WALL + 6))

    assert keyway_width_effective(GearParams()) == 0.0
    assert keyway_corner_radius(GearParams()) == 0.0
    assert bore_mouth_limit(GearParams()) == pytest.approx(4.975)


@pytest.mark.parametrize(("kw", "floor_to_wall", "width"), [
    ({"keyway_width": 3, "keyway_depth": 1.4}, 10.55, 3.15),
    ({"keyway_width": 3, "keyway_depth": 1.4, "bore_flat": 0}, 10.55, 3.15),
    ({"keyway_width": 3, "keyway_depth": 1.4, "bore_clearance": 0}, 10.4, 3.0),
    ({}, None, None),
    ({"bore_d": 0}, None, None),
    ({"bore_hex": 6}, None, None),
])
def test_a_keyway_reports_floor_to_wall_and_width_and_null_without_one(
        kw: dict[str, object], floor_to_wall: float | None, width: float | None) -> None:
    """The two printed numbers derive() adds (D-15), compared with == because they are
    rounded once, at construction (D-10): a D-flat coexists (D-04), bore_clearance moves
    both, and a keyway needs bore_d > 0 and no hex to exist at all."""
    d = derive(GearParams.model_validate(kw))
    assert d.keyway_floor_to_wall == floor_to_wall
    assert d.keyway_width_effective == width


def test_the_recess_yields_to_a_keyway_and_says_so_only_when_it_narrows_or_drops() -> None:
    """D-09 (supersedes SC3's "or a recess wall" clause): the recess narrows or drops
    with the existing warnings, never a ValidationError, as the keyway corner reaches
    farther out."""
    d = derive(GearParams(keyway_width=3, keyway_depth=1.4))
    assert d.recess_id == pytest.approx(13.158)
    assert d.recess_od == pytest.approx(25.158)
    assert d.warnings == ()

    d = derive(GearParams(keyway_width=3, keyway_depth=5))
    assert any("Recess narrowed to 3.93 mm to fit between the bore wall and the "
              "tooth rim." in w for w in d.warnings)

    d = derive(GearParams(keyway_width=3, keyway_depth=9))
    assert d.recess_id is None
    assert any("No room for a face recess between the bore wall and the tooth rim; "
              "it was left out." in w for w in d.warnings)


@pytest.mark.parametrize(("kw", "msg", "fields"), [
    pytest.param(
        {"bore_hex": 6, "keyway_width": 3, "keyway_depth": 1.4},
        "A keyway cannot be cut into a hex bore: set bore_hex to 0 for a keyed round "
        "or D-flat bore, or set keyway_width and keyway_depth to 0.",
        ["bore_hex", "keyway_depth", "keyway_width"], id="hex"),
    pytest.param(
        {"bore_d": 0, "keyway_width": 3, "keyway_depth": 1.4},
        "A keyway needs a round bore to cut into: set bore_d, or set keyway_width and "
        "keyway_depth to 0.",
        ["bore_d", "keyway_depth", "keyway_width"], id="no-bore"),
    pytest.param(
        {"keyway_width": 3},
        "A keyway needs both keyway_width and keyway_depth: set both above 0, or both "
        "to 0.",
        ["keyway_depth", "keyway_width"], id="half-set-width"),
    pytest.param(
        {"keyway_depth": 1.4},
        "A keyway needs both keyway_width and keyway_depth: set both above 0, or both "
        "to 0.",
        ["keyway_depth", "keyway_width"], id="half-set-depth"),
])
def test_a_keyway_needs_a_round_bore_and_both_of_its_fields(
        kw: dict[str, object], msg: str, fields: list[str]) -> None:
    """D-13 (before the shape branches) and D-03: exact sentence and fields."""
    with pytest.raises(ValidationError) as exc:
        GearParams.model_validate(kw)
    err = exc.value.errors()[0]
    assert err["type"] == "infeasible"
    assert err["msg"] == msg
    assert err["ctx"]["fields"] == fields


def test_a_keyway_on_a_hex_bore_with_only_one_field_set_names_both_sentences_hex_first() -> None:
    """D-13 and D-03 can both fire on one set: the hex sentence comes first (the order
    check() appends them), and the merged, sorted fields cover all three names."""
    with pytest.raises(ValidationError) as exc:
        GearParams.model_validate({"bore_hex": 6, "keyway_width": 3})
    err = exc.value.errors()[0]
    assert err["type"] == "infeasible"
    assert err["msg"].startswith("A keyway cannot be cut into a hex bore")
    assert "A keyway needs both keyway_width and keyway_depth" in err["msg"]
    assert err["ctx"]["fields"] == ["bore_hex", "keyway_depth", "keyway_width"]


def test_a_keyway_as_wide_as_the_bore_is_refused_and_one_step_narrower_is_accepted() -> None:
    """D-11: no kernel boundary exists (research pushed to 166% of bore_d without a
    failure); the bound is definitional, one step either side of keyway_width == bore_d."""
    GearParams(bore_flat=0, keyway_width=8.95, keyway_depth=1.4)
    with pytest.raises(ValidationError) as exc:
        GearParams.model_validate({"bore_flat": 0, "keyway_width": 9, "keyway_depth": 1.4})
    err = exc.value.errors()[0]
    assert err["type"] == "infeasible"
    assert err["ctx"]["fields"] == ["bore_d", "keyway_width"]
    assert err["msg"] == (
        "Keyway is too wide for the bore: keyway_width (9 mm) must be less than "
        "bore_d (9 mm), or its sides no longer meet the bore wall; reduce keyway_width.")


def test_a_keyway_that_leaves_less_than_min_wall_to_the_d_flat_is_refused_naming_both() -> None:
    """D-02: the arc of round wall between the D-flat's corner and the keyway's side,
    one step either side of the boundary the kernel builds every width up to."""
    GearParams(keyway_width=6.45, keyway_depth=1.4)
    with pytest.raises(ValidationError) as exc:
        GearParams.model_validate({"keyway_width": 6.5, "keyway_depth": 1.4})
    err = exc.value.errors()[0]
    assert err["type"] == "infeasible"
    assert err["ctx"]["fields"] == ["bore_flat", "keyway_width"]
    assert err["msg"] == (
        "Keyway runs too close to the D-flat: it leaves 0.381 mm of round bore wall "
        "between the flat and the keyway's side, which must be at least 0.4 mm; "
        "reduce keyway_width or increase bore_flat.")

    # Past the flat's corner the wall is negative; the message never prints that.
    with pytest.raises(ValidationError) as exc:
        GearParams.model_validate({"keyway_width": 7.5, "keyway_depth": 1.4})
    assert "it leaves 0.000 mm of round bore wall" in exc.value.errors()[0]["msg"]

    # A round bore (no D-flat) has no wall to run into.
    GearParams(keyway_width=6.5, keyway_depth=1.4, bore_flat=0)

    assert keyway_flat_wall(GearParams(keyway_width=3, keyway_depth=1.4)) == pytest.approx(
        2.4956, abs=1e-4)
    assert keyway_flat_wall(GearParams(keyway_width=6.45, keyway_depth=1.4)) == pytest.approx(
        0.4174, abs=1e-4)


def test_a_keyway_whose_floor_corner_nears_the_root_is_refused_naming_both() -> None:
    """D-10: the floor corner, not the centreline; never capped -- the accepted depth is
    honoured in full (REQ-keyway-wall-refused)."""
    assert derive(GearParams(keyway_width=3, keyway_depth=9.35)).keyway_floor_to_wall == 18.5
    with pytest.raises(ValidationError) as exc:
        GearParams.model_validate({"keyway_width": 3, "keyway_depth": 9.4})
    err = exc.value.errors()[0]
    assert err["type"] == "infeasible"
    assert err["ctx"]["fields"] == ["keyway_depth", "keyway_width"]
    assert err["msg"] == (
        "Keyway is too deep for the root diameter: its floor corners reach 28.13 mm "
        "across, which must stay 0.4 mm inside the root circle (28.88 mm); reduce "
        "keyway_depth or keyway_width.")


def test_a_round_bore_chamfer_that_touches_the_root_is_refused_naming_both() -> None:
    """D-12: the fold-in of the round-bore-chamfer-reach debt, at the measured contact
    point (ROOT_CONTACT), never at bore_mouth_limit(p) > rf - MIN_WALL (L05)."""
    GearParams(bore_d=24.7, bore_chamfer=2, bore_flat=0)
    with pytest.raises(ValidationError) as exc:
        GearParams.model_validate({"bore_d": 24.75, "bore_chamfer": 2, "bore_flat": 0})
    err = exc.value.errors()[0]
    assert err["type"] == "infeasible"
    assert err["ctx"]["fields"] == ["bore_chamfer", "bore_d"]
    assert err["msg"] == (
        "Bore chamfer reaches the root circle: the chamfered bore mouth is 28.900 mm "
        "across and the root circle 28.875 mm, and the mouth must stay inside it; "
        "reduce bore_chamfer or bore_d.")

    # The exact contacts: a plain kwarg, the default chamfer (the round rule does not
    # fire), and a step-aligned pair whose gap is +1.8e-15 mm in floats.
    for kw in (
        {"bore_d": 24.725, "bore_chamfer": 2, "bore_flat": 0},
        {"bore_d": 27.925, "bore_flat": 0},
        {"bore_d": 26.325, "bore_chamfer": 1.2, "bore_flat": 0},
    ):
        with pytest.raises(ValidationError) as exc:
            GearParams.model_validate(kw)
        assert exc.value.errors()[0]["ctx"]["fields"] == ["bore_chamfer", "bore_d"]
    with pytest.raises(ValidationError) as exc:
        GearParams.model_validate({"bore_d": 24.725, "bore_chamfer": 2, "bore_flat": 0})
    assert exc.value.errors()[0]["msg"] == (
        "Bore chamfer reaches the root circle: the chamfered bore mouth is 28.875 mm "
        "across and the root circle 28.875 mm, and the mouth must stay inside it; "
        "reduce bore_chamfer or bore_d.")

    GearParams(bore_d=27.9, bore_flat=0)
    GearParams(teeth=40, bore_d=61.45, bore_chamfer=2, bore_flat=0)
    with pytest.raises(ValidationError) as exc:
        GearParams.model_validate({"teeth": 40, "bore_d": 61.5, "bore_chamfer": 2,
                                   "bore_flat": 0})
    assert exc.value.errors()[0]["ctx"]["fields"] == ["bore_chamfer", "bore_d"]

    GearParams(bore_d=24.7, bore_chamfer=2, bore_flat=22)
    with pytest.raises(ValidationError) as exc:
        GearParams.model_validate({"bore_d": 24.75, "bore_chamfer": 2, "bore_flat": 22})
    assert exc.value.errors()[0]["ctx"]["fields"] == ["bore_chamfer", "bore_d"]


def test_the_round_bore_rules_never_stack() -> None:
    """The too-large rule and D-12's chamfer-reach rule are if/elif: past the root a
    bore is refused once, naming only bore_d."""
    with pytest.raises(ValidationError) as exc:
        GearParams.model_validate({"bore_d": 30, "bore_flat": 0})
    assert exc.value.errors()[0]["ctx"]["fields"] == ["bore_d"]


@pytest.mark.parametrize(("kw", "expected"), [
    # One step either side of MIN_WALL on the default gear (rf 14.4375 mm, chamfer 0.4):
    # bore_d 27.1 leaves 0.4125 mm of wall, 27.15 leaves 0.3875 mm.
    ({"bore_d": 27.1, "bore_flat": 0}, None),
    ({"bore_d": 27.15, "bore_flat": 0}, "0.39 mm"),
    ({"bore_d": 27.905, "bore_flat": 0}, "0.01 mm"),
    # A D-flat does not move the number: the chamfered mouth meets the root on the round
    # part of the wall either way.
    ({"bore_d": 27.525, "bore_flat": 27.4}, "0.20 mm"),
    # bore_clearance is part of the as-cut wall: the same bore_d warns with the default
    # 0.15 mm (0.3625 mm left) and not without it (0.4375 mm left).
    ({"bore_d": 27.2, "bore_flat": 0}, "0.36 mm"),
    ({"bore_d": 27.2, "bore_flat": 0, "bore_clearance": 0}, None),
    # A hex bore ignores bore_d, so a value that warns on a round bore says nothing here;
    # no bore has no mouth to measure from; the two default links stay silent.
    ({"bore_hex": 20, "bore_d": 27.525, "bore_flat": 0}, None),
    ({"bore_d": 0, "bore_flat": 0}, None),
    ({}, None),
    ({"keyway_width": 3, "keyway_depth": 1.4}, None),
])
def test_a_bore_chamfer_under_min_wall_from_the_root_warns_with_the_measured_gap(
        kw: dict[str, object], expected: str | None) -> None:
    """09-REVIEW.md WR-01: D-12 refuses only at ROOT_CONTACT, so a wall thinner than
    MIN_WALL is accepted (L05 -- the boundary stays put); derive() says so with the gap
    it measured, and only inside (0, MIN_WALL). One step further (bore_d 27.925, gap 0)
    is D-12's refusal, tested in
    test_a_round_bore_chamfer_that_touches_the_root_is_refused_naming_both."""
    d = derive(GearParams.model_validate(kw))
    thin = [w for w in d.warnings if w.startswith("Bore chamfer leaves only")]
    if expected is None:
        assert thin == []
    else:
        assert len(thin) == 1
        assert f"leaves only {expected} of wall to the root circle" in thin[0]
        assert "reduce bore_chamfer or bore_d for more margin" in thin[0]



def test_tooth_thickness_and_gap_are_measured_on_the_same_circle() -> None:
    """Thickness + gap must add up to the pitch on the root circle.

    They did not when the base circle sat outside the root circle, which is the case for
    the default 19-tooth gear: the thickness was read at the base circle instead.
    """
    for teeth in (19, 40):  # 19 -> rb > rf (the broken case), 40 -> rf > rb
        p = GearParams(teeth=teeth)
        d, pr = derive(p), profile(GearParams(teeth=teeth))
        assert d.root_thickness + d.root_gap == pytest.approx(
            2 * math.pi * pr.rf / teeth, abs=2e-3)


def test_oversized_recess_is_narrowed_to_fit_and_says_so() -> None:
    d = derive(GearParams(recess_width=12))
    assert any("Recess narrowed" in w for w in d.warnings)
    # Narrowing asserts, one per line: ruff's PT018 rejects `and`-joined asserts, and
    # mypy needs each on its own line to narrow recess_id/recess_od past `float | None`.
    assert d.recess_id is not None
    assert d.recess_od is not None
    assert (d.recess_od - d.recess_id) / 2 < 12  # radial width, capped
    p = GearParams(recess_width=12)
    assert d.recess_id / 2 >= bore_radius(p) + p.bore_chamfer + MIN_WALL - 1e-9
    assert d.recess_od / 2 <= profile(p).rf - MIN_WALL + 1e-9


def test_small_gear_keeps_the_stock_bore_and_recess() -> None:
    """The README's own example: defaults sized for a 19-tooth m=1.75 gear must not
    refuse a 24-tooth m=1 one over a parameter the user never touched."""
    d = derive(GearParams(teeth=24, module=1, pressure_angle=20, bore_flat=0))
    assert any("Recess narrowed" in w for w in d.warnings)
    assert d.recess_id is not None


def test_recess_is_dropped_when_there_is_no_room_at_all() -> None:
    d = derive(GearParams(teeth=16, module=1, bore_d=9, bore_flat=8))
    assert d.recess_id is None
    assert any("No room for a face recess" in w for w in d.warnings)


def test_recess_fillet_is_capped_to_the_narrowed_groove() -> None:
    d = derive(GearParams(recess_width=12, recess_fillet=3))
    assert d.recess_fillet is not None
    assert d.recess_fillet < 3
    assert any("Recess fillet reduced" in w for w in d.warnings)


@pytest.mark.parametrize(("kw", "mate"), [
    ({"teeth": 6, "pressure_angle": 14.5, "profile_shift": -0.6}, 40),
    ({"teeth": 6, "pressure_angle": 14.5, "profile_shift": -0.5}, 12),
])
def test_impossible_pairs_have_no_centre_distance(kw: dict[str, object], mate: int) -> None:
    """inv(aw) = inv(a) + 2 tan(a) x / z has no root when the right-hand side is
    negative: the pair cannot mesh at any distance. It used to return garbage -- 39.4 mm
    where the nominal is 70, and negative numbers elsewhere."""
    p = GearParams.model_validate(
        {"bore_d": 0, "bore_flat": 0, "bore_chamfer": 0, "recess_sides": "none", **kw})
    assert centre_distance(p, mate) is None
    out = derive(p, mate_teeth=mate)
    assert out.centre_distance is None
    assert any("cannot mesh" in w for w in out.warnings)


def test_centre_distance_matches_an_independent_solver() -> None:
    def bisect(p: GearParams, z2: int) -> float | None:
        a = math.radians(p.pressure_angle)
        target = inv(a) + 2 * math.tan(a) * p.profile_shift / (p.teeth + z2)
        if target <= 0:
            return None
        lo, hi = 1e-12, math.radians(89.0)
        for _ in range(200):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if inv(mid) < target else (lo, mid)
        return p.module * (p.teeth + z2) / 2 * math.cos(a) / math.cos((lo + hi) / 2)

    checked = 0
    for teeth in (6, 12, 19, 60, 200):
        for pa in (14.5, 20.0, 25.0, 35.0):
            for x in (-0.6, -0.3, 0.0, 0.5, 1.0):
                try:
                    p = GearParams(teeth=teeth, pressure_angle=pa, profile_shift=x,
                                   bore_d=0, bore_flat=0, bore_chamfer=0,
                                   recess_sides="none")
                except ValidationError:
                    continue  # not a gear; centre distance is moot
                for z2 in (6, 40, 1000):
                    expected, got = bisect(p, z2), centre_distance(p, z2)
                    assert (got is None) == (expected is None), (teeth, pa, x, z2)
                    if expected is not None:
                        assert got == pytest.approx(expected, rel=1e-12)
                    checked += 1
    assert checked > 200


@pytest.mark.parametrize(("kw", "applied", "warning"), [
    pytest.param({"tip_chamfer": 0.4}, 0.4, None, id="inside"),
    pytest.param({"tip_chamfer": 1.7}, 1.7, None, id="pitch-step-inside"),
    pytest.param({"tip_chamfer": 1.75}, 1.75, None, id="pitch-exactly"),
    pytest.param({"tip_chamfer": 1.8}, 1.75,
                 "Tip chamfer reduced to 1.75 mm to keep it above the pitch circle.",
                 id="pitch-step-past"),
    pytest.param({"tip_chamfer": 3}, 1.75,
                 "Tip chamfer reduced to 1.75 mm to keep it above the pitch circle.",
                 id="pitch-field-max"),
    pytest.param({"face_width": 1, "recess_sides": "none", "tip_chamfer": 0.4}, 0.4, None,
                 id="land-step-inside"),
    pytest.param({"face_width": 1, "recess_sides": "none", "tip_chamfer": 0.45}, 0.45, None,
                 id="land-exactly"),
    pytest.param({"face_width": 1, "recess_sides": "none", "tip_chamfer": 0.5}, 0.45,
                 "Tip chamfer reduced to 0.45 mm to leave a land on the tooth tip "
                 "between the two faces' chamfers.",
                 id="land-step-past"),
    pytest.param({"profile_shift": 1.0, "pressure_angle": 14.5, "tip_chamfer": 2.9}, 2.9,
                 None, id="flank-step-inside"),
    pytest.param({"profile_shift": 1.0, "pressure_angle": 14.5, "tip_chamfer": 2.95}, 2.937,
                 "Tip chamfer reduced to 2.937 mm to keep it on the involute flank, "
                 "above the straight lead-in from the root fillet.",
                 id="flank-step-past"),
    pytest.param({"profile_shift": 1.0, "pressure_angle": 14.5, "tip_chamfer": 3}, 2.937,
                 "Tip chamfer reduced to 2.937 mm to keep it on the involute flank, "
                 "above the straight lead-in from the root fillet.",
                 id="flank-field-max"),
    pytest.param({"module": 10, "tip_chamfer": 3}, 3, None, id="le-binds"),
    pytest.param({"teeth": 200, "module": 0.2, "backlash": 0.07, "tip_chamfer": 0.2}, 0.2,
                 None, id="finest-tips-exactly"),
    pytest.param({"teeth": 200, "module": 0.2, "backlash": 0.07, "tip_chamfer": 0.25}, 0.2,
                 "Tip chamfer reduced to 0.2 mm to keep it above the pitch circle.",
                 id="finest-tips-step-past"),
    pytest.param({"tip_chamfer": 0.1234}, 0.123, None, id="print-precision-inside"),
    pytest.param({}, 0.0, None, id="off"),
])
def test_a_tip_chamfer_is_capped_to_whichever_limit_binds_first(
        kw: dict[str, object], applied: float, warning: str | None) -> None:
    """D-01 (tip land), D-02 (pitch circle) and D-04 (the measured involute-flank
    boundary): one step either side of each limit, never a ValidationError (L03). The
    finest-tips rows are the precision edge: the pitch-circle limit at 200 teeth,
    module 0.2 is 0.1999999999999993, a float residue that must not warn on a request
    of exactly 0.2 -- derive() compares at the printed 3-dp resolution, not the raw
    float."""
    p = GearParams.model_validate(kw)
    d = derive(p)
    assert tip_chamfer_effective(p) == pytest.approx(applied)
    assert d.tip_chamfer_effective == (pytest.approx(applied) if p.tip_chamfer > 0 else None)
    tip_warnings = [w for w in d.warnings if w.startswith("Tip chamfer")]
    assert tip_warnings == ([warning] if warning else [])


def test_a_sub_print_precision_tip_chamfer_request_still_warns() -> None:
    """10-REVIEW.md WR-01: a request under 0.0005 mm rounds to 0.0, so no limit ever
    binds and the request would be silently dropped without this branch -- the part
    built is the unchamfered default, not what was asked for, so it must still warn.

    10-REVIEW.md CR-01: the WR-01 fix's first attempt reused tip_chamfer_limit(p)[1]
    as the reason, which is only true when a limit actually bound the value -- here
    none did (tip_chamfer_limit's pitch-circle bound for the default gear is 1.75 mm,
    nowhere near 0.0004). The message must state the true cause (print resolution),
    and asserting only a prefix (startswith) cannot see a wrong suffix -- that is
    exactly how CR-01 slipped through the first fix's own test. Assert the full
    string."""
    p = GearParams(tip_chamfer=0.0004)
    d = derive(p)
    assert tip_chamfer_effective(p) == 0.0
    tip_warnings = [w for w in d.warnings if w.startswith("Tip chamfer")]
    assert tip_warnings == [
        "Tip chamfer 0.0004 mm is below the 0.001 mm resolution it is cut at and was "
        "not cut."
    ]
    assert not any(w.startswith("Tip chamfer reduced to") for w in tip_warnings)


def test_the_tip_chamfer_field_is_bounded_zero_to_three() -> None:
    with pytest.raises(ValidationError):
        GearParams(tip_chamfer=3.05)
    with pytest.raises(ValidationError):
        GearParams(tip_chamfer=-0.05)
    GearParams(tip_chamfer=3)  # does not raise


@pytest.mark.parametrize("kw", [
    {},
    {"teeth": 200},
    {"profile_shift": 1.0, "pressure_angle": 14.5},
    {"bore_hex": 6},
    {"keyway_width": 3, "keyway_depth": 1.4},
])
def test_the_tip_chamfer_changes_no_other_number(kw: dict[str, object]) -> None:
    """D-15, the empty edge: a tip chamfer changes only tip_chamfer_effective and the
    one tip-chamfer warning it can add. Every other derived field, and every other
    warning, is untouched."""
    p0 = GearParams.model_validate(kw)
    p1 = GearParams.model_validate({**kw, "tip_chamfer": 1})
    d0 = derive(p0).model_dump()
    d1 = derive(p1).model_dump()
    del d0["tip_chamfer_effective"], d1["tip_chamfer_effective"]
    d0["warnings"] = tuple(w for w in d0["warnings"] if not w.startswith("Tip chamfer"))
    d1["warnings"] = tuple(w for w in d1["warnings"] if not w.startswith("Tip chamfer"))
    assert d0 == d1


@pytest.mark.parametrize(("kw", "expected"), [
    pytest.param({}, 15.4375, id="default"),
    pytest.param({"profile_shift": 1.0, "pressure_angle": 14.5}, 17.1875, id="flank"),
    pytest.param({"root_fillet": 0}, None, id="no-fillet"),
])
def test_spline_start_is_where_the_outline_starts_the_involute(
        kw: dict[str, object], expected: float | None) -> None:
    """Not Profile.r_start: that is the theoretical involute start, this is where
    model._outline actually starts the spline (calc.spline_start's docstring)."""
    p = GearParams.model_validate(kw)
    pr = profile(p)
    want = pr.rb if expected is None else expected  # root_fillet=0: no straight lead-in
    assert spline_start(pr, root_fillet(p)) == pytest.approx(want, abs=1e-9)


def test_a_rounded_tip_chamfer_cap_stays_inside_the_measured_kernel_boundary() -> None:
    """The precision edge (D-04): round() can move the cap up by half a printed step
    (2.9365 mm rounds to 2.937 mm), the margin is two half-steps, and the spike
    measured the kernel failing within about 2 microns of the contact
    (bench/RESULTS.md "Tooth-tip chamfer spike"). Pure maths, no kernel -- the same
    405-set grid the spike used (teeth 19, bore_d 0, no recess), all at tip_chamfer 3,
    a grid that silently shrank would fail the count assertion below."""
    checked = 0
    for module, shift, alpha, fillet, backlash in itertools.product(
            (0.2, 0.5, 1, 1.25, 1.75, 2.5, 4),
            (0.25, 0.5, 0.75, 1.0),
            (14.5, 20, 25),
            (0.5, 1.0, 3.0),
            (0, 0.1)):
        kw: dict[str, object] = {
            "teeth": 19, "module": module, "profile_shift": shift,
            "pressure_angle": alpha, "root_fillet": fillet, "backlash": backlash,
            "bore_d": 0, "recess_sides": "none", "tip_chamfer": 3,
        }
        try:
            p = GearParams.model_validate(kw)
        except ValidationError:
            continue
        checked += 1
        pr = profile(p)
        margin = pr.ra - spline_start(pr, root_fillet(p)) - tip_chamfer_effective(p)
        assert margin >= TIP_CHAMFER_MARGIN / 2 - 1e-12
        assert tip_chamfer_effective(p) > 0
    assert checked == 405


@pytest.mark.parametrize(("kw", "refused", "fields", "msg_start"), [
    pytest.param({"hole_count": 6, "hole_d": 4, "hole_circle_d": 14.75}, False, (), "",
                 id="hub-accept-exact"),
    pytest.param({"hole_count": 6, "hole_d": 4, "hole_circle_d": 14.7}, True,
                 ("hole_circle_d", "hole_d"),
                 "Lightening holes come too close to the bore", id="hub-refuse-one-step"),
    pytest.param({"hole_count": 6, "hole_d": 4, "hole_circle_d": 20}, False, (), "",
                 id="hub-accept-margin"),
    pytest.param({"hole_count": 6, "hole_d": 4, "hole_circle_d": 24.075}, False, (), "",
                 id="rim-accept-exact"),
    pytest.param({"hole_count": 6, "hole_d": 4, "hole_circle_d": 24.05}, False, (), "",
                 id="rim-accept-margin"),
    pytest.param({"hole_count": 6, "hole_d": 4, "hole_circle_d": 24.1}, True,
                 ("hole_circle_d", "hole_d"),
                 "Lightening holes come too close to the root circle", id="rim-refuse-one-step"),
    pytest.param({"teeth": 40, "hole_count": 6, "hole_d": 19.6, "hole_circle_d": 40},
                 False, (), "", id="neighbour-accept-exact"),
    pytest.param({"teeth": 40, "hole_count": 6, "hole_d": 19.65, "hole_circle_d": 40},
                 True, ("hole_circle_d", "hole_count", "hole_d"),
                 "Lightening holes are too close to each other", id="neighbour-refuse-one-step"),
])
def test_a_hole_rule_refuses_one_step_past_its_wall_and_accepts_it_exactly(
        kw: dict[str, object], refused: bool, fields: tuple[str, ...],
        msg_start: str) -> None:
    """D-15, D-16, D-17: each rule refuses one step past MIN_WALL and accepts it
    exactly, comparing round(wall, 6) so the step-aligned float residue (0.4 computing
    as 0.39999999999999947) does not refuse a wall the user sized to exactly MIN_WALL."""
    if not refused:
        GearParams.model_validate(kw)  # does not raise
        return
    with pytest.raises(ValidationError) as exc:
        GearParams.model_validate(kw)
    err = exc.value.errors()[0]
    assert err["type"] == "infeasible"
    assert err["ctx"]["fields"] == sorted(fields)
    assert err["msg"].startswith(msg_start)


def test_a_hole_wider_than_the_web_is_refused_at_both_walls() -> None:
    """A hole wider than the web breaches both the hub and the rim independently --
    neither rule implies the other, so both sentences appear and both fields are named
    once each, deduplicated by GearParams._feasible."""
    with pytest.raises(ValidationError) as exc:
        GearParams.model_validate({"hole_count": 1, "hole_d": 10, "hole_circle_d": 19})
    err = exc.value.errors()[0]
    assert err["type"] == "infeasible"
    assert err["ctx"]["fields"] == ["hole_circle_d", "hole_d"]
    assert "Lightening holes come too close to the bore" in err["msg"]
    assert "Lightening holes come too close to the root circle" in err["msg"]


@pytest.mark.parametrize(("kw", "fields", "msg"), [
    pytest.param({"hole_count": 6}, ["hole_circle_d", "hole_d"],
                 "Lightening holes need hole_circle_d and hole_d: set them above 0, "
                 "or set hole_count to 0.", id="both-zero"),
    pytest.param({"hole_count": 6, "hole_d": 4}, ["hole_circle_d"],
                 "Lightening holes need hole_circle_d: set it above 0, or set "
                 "hole_count to 0.", id="circle-zero"),
    pytest.param({"hole_count": 6, "hole_circle_d": 20}, ["hole_d"],
                 "Lightening holes need hole_d: set it above 0, or set hole_count to 0.",
                 id="d-zero"),
])
def test_a_half_set_hole_pattern_names_only_its_zero_fields(
        kw: dict[str, object], fields: list[str], msg: str) -> None:
    """D-15: hole_count above 0 with one or both dimensions still 0 is a 422 naming only
    the fields that are 0, before the wall rules ever run."""
    with pytest.raises(ValidationError) as exc:
        GearParams.model_validate(kw)
    err = exc.value.errors()[0]
    assert err["type"] == "infeasible"
    assert err["ctx"]["fields"] == fields
    assert err["msg"] == msg


@pytest.mark.parametrize(("kw", "warning"), [
    pytest.param({"hole_d": 4, "hole_circle_d": 20},
                 "No lightening holes with hole_count 0: hole_d (4 mm) and "
                 "hole_circle_d (20 mm) are ignored.", id="both-set"),
    pytest.param({"hole_d": 4},
                 "No lightening holes with hole_count 0: hole_d (4 mm) is ignored.",
                 id="d-only"),
    pytest.param({"hole_circle_d": 20},
                 "No lightening holes with hole_count 0: hole_circle_d (20 mm) is "
                 "ignored.", id="circle-only"),
])
def test_hole_dimensions_without_a_count_are_ignored_and_named(
        kw: dict[str, object], warning: str) -> None:
    """D-15: hole_count 0 (the default) builds nothing regardless of hole_d/
    hole_circle_d, and derive() says so naming only the fields the user set."""
    d = derive(GearParams.model_validate(kw))
    assert d.cutout_hub_wall is None
    assert d.cutout_rim_wall is None
    assert d.warnings == (warning,)


@pytest.mark.parametrize(("kw", "hub", "rim"), [
    pytest.param({"hole_count": 6, "hole_d": 4, "hole_circle_d": 20}, 3.025, 2.438,
                 id="d-flat-and-round"),
    pytest.param({"hole_count": 6, "hole_d": 4, "hole_circle_d": 20, "bore_hex": 6,
                 "bore_flat": 0}, 3.987, 2.438, id="hex-bore"),
    pytest.param({"hole_count": 6, "hole_d": 4, "hole_circle_d": 20, "keyway_width": 3,
                 "keyway_depth": 1.4}, 1.821, 2.438, id="keyed-round"),
    pytest.param({"hole_count": 6, "hole_d": 4, "hole_circle_d": 20, "bore_d": 0,
                 "bore_flat": 0}, 8.0, 2.438, id="no-bore"),
])
def test_a_cutout_reports_its_thinnest_walls_and_null_without_one(
        kw: dict[str, object], hub: float, rim: float) -> None:
    """D-17, D-20: the tracer link's two walls per bore shape, rounded once at
    construction; None/None with no cutout (hole_count 0, the default)."""
    d = derive(GearParams.model_validate(kw))
    assert d.cutout_hub_wall == pytest.approx(hub)
    assert d.cutout_rim_wall == pytest.approx(rim)
    d0 = derive(GearParams())
    assert d0.cutout_hub_wall is None
    assert d0.cutout_rim_wall is None


def test_the_hole_count_is_an_integer_from_0_to_200() -> None:
    """D-18: field-level ValidationErrors (not the "infeasible" custom error) one step
    either side of the bound, and for the wrong type."""
    for bad in ({"hole_count": 201, "hole_d": 1, "hole_circle_d": 10},
               {"hole_count": -1, "hole_d": 1, "hole_circle_d": 10},
               {"hole_count": 2.5, "hole_d": 1, "hole_circle_d": 10}):
        with pytest.raises(ValidationError) as exc:
            GearParams.model_validate(bad)
        assert exc.value.errors()[0]["type"] != "infeasible"
    GearParams.model_validate({"hole_count": 1, "hole_d": 4, "hole_circle_d": 20})
    GearParams.model_validate({"teeth": 200, "hole_count": 200, "hole_d": 1,
                               "hole_circle_d": 183.4, "bore_flat": 0,
                               "recess_sides": "none"})


def test_the_hole_gap_and_walls_helpers_match_the_planning_probe() -> None:
    """hole_gap(p) is the wall between neighbouring hole centres (D-16); cutout_walls(p,
    rf) is unrounded, used directly by check() before derive() rounds it."""
    p = GearParams.model_validate({"teeth": 40, "hole_count": 6, "hole_d": 19.6,
                                   "hole_circle_d": 40})
    assert hole_gap(p) == pytest.approx(0.399999999999995)
    p2 = GearParams.model_validate({"hole_count": 6, "hole_d": 4, "hole_circle_d": 20})
    pr2 = profile(p2)
    walls = cutout_walls(p2, pr2.rf)
    assert walls is not None
    assert walls == pytest.approx((3.0249999999999995, 2.4375))


SPOKE = {"spoke_count": 4, "spoke_width": 2, "hub_d": 12, "rim_wall": 1}


def test_two_cutout_patterns_on_one_part_are_refused_naming_both() -> None:
    """REQ-one-cutout-pattern: two or more non-zero pattern selectors is one 422
    naming every chosen selector, before any per-pattern rule runs -- a half-set hole
    pattern beside a complete spoke pattern still gives only this one sentence, never
    the half-set hole sentence too."""
    with pytest.raises(ValidationError) as exc:
        GearParams.model_validate({**SPOKE, "hole_count": 6, "hole_d": 4,
                                   "hole_circle_d": 20})
    err = exc.value.errors()[0]
    assert err["type"] == "infeasible"
    assert err["ctx"]["fields"] == ["hole_count", "spoke_count"]
    assert err["msg"] == ("Only one body cutout pattern per part: spoke_count (4) and "
                          "hole_count (6) are both set; keep one and set the others "
                          "to 0.")

    with pytest.raises(ValidationError) as exc:
        GearParams.model_validate({**SPOKE, "hole_count": 6})  # half-set hole
    err = exc.value.errors()[0]
    assert err["type"] == "infeasible"
    assert err["ctx"]["fields"] == ["hole_count", "spoke_count"]
    assert "Only one body cutout pattern per part" in err["msg"]
    assert "Lightening holes need" not in err["msg"]


@pytest.mark.parametrize(("kw", "fields", "msg"), [
    pytest.param({"spoke_count": 4}, ["hub_d", "rim_wall", "spoke_width"],
                 "Spoke arms need hub_d, rim_wall and spoke_width: set them above 0, "
                 "or set spoke_count to 0.", id="all-zero"),
    pytest.param({"spoke_count": 4, "spoke_width": 2}, ["hub_d", "rim_wall"],
                 "Spoke arms need hub_d and rim_wall: set them above 0, or set "
                 "spoke_count to 0.", id="two-zero"),
    pytest.param({"spoke_count": 4, "hub_d": 12, "rim_wall": 1}, ["spoke_width"],
                 "Spoke arms need spoke_width: set it above 0, or set spoke_count "
                 "to 0.", id="one-zero"),
])
def test_a_half_set_spoke_pattern_names_only_its_zero_fields(
        kw: dict[str, object], fields: list[str], msg: str) -> None:
    """D-15: spoke_count above 0 with one or more of hub_d/rim_wall/spoke_width still
    0 is a 422 naming only the fields that are 0, before the wall rules ever run."""
    with pytest.raises(ValidationError) as exc:
        GearParams.model_validate(kw)
    err = exc.value.errors()[0]
    assert err["type"] == "infeasible"
    assert err["ctx"]["fields"] == fields
    assert err["msg"] == msg


@pytest.mark.parametrize(("kw", "refused", "fields", "msg_start"), [
    pytest.param({**SPOKE, "spoke_width": 0.4}, False, (), "", id="arm-accept-exact"),
    pytest.param({**SPOKE, "spoke_width": 0.35}, True, ("spoke_width",),
                 "Spoke arms 0.35 mm wide are thinner", id="arm-refuse-one-step"),
    pytest.param({**SPOKE, "rim_wall": 0.4}, False, (), "", id="rim-accept-exact"),
    pytest.param({**SPOKE, "rim_wall": 0.35}, True, ("rim_wall",),
                 "The rim wall (0.35 mm) is thinner", id="rim-refuse-one-step"),
    pytest.param({**SPOKE, "hub_d": 10.75}, False, (), "", id="hub-accept-exact"),
    pytest.param({**SPOKE, "hub_d": 10.7}, True, ("hub_d",),
                 "The spoke hub is too small for the bore", id="hub-refuse-one-step"),
    pytest.param({**SPOKE, "rim_wall": 8.0375}, False, (), "",
                 id="annulus-accept-exact"),
    pytest.param({**SPOKE, "rim_wall": 8.05}, True, ("hub_d", "rim_wall"),
                 "Spokes leave no room to cut", id="annulus-refuse-one-step"),
    pytest.param({"spoke_count": 12, "spoke_width": 2.67, "hub_d": 12, "rim_wall": 0.4},
                 False, (), "", id="opening-accept-exact"),
    pytest.param({"spoke_count": 12, "spoke_width": 2.72, "hub_d": 12, "rim_wall": 0.4},
                 True, ("hub_d", "spoke_count", "spoke_width"),
                 "Spoke arms leave too little room between them at the hub",
                 id="opening-refuse-one-step"),
])
def test_a_spoke_rule_refuses_one_step_past_its_wall_and_accepts_it_exactly(
        kw: dict[str, object], refused: bool, fields: tuple[str, ...],
        msg_start: str) -> None:
    """D-16, D-17: each spoke rule refuses one step past MIN_WALL and accepts it
    exactly, comparing round(wall, 6) so the step-aligned float residue does not
    refuse a wall the user sized to exactly MIN_WALL. The arm rule (11-01 A1: the
    human kept it) is included."""
    if not refused:
        GearParams.model_validate(kw)  # does not raise
        return
    with pytest.raises(ValidationError) as exc:
        GearParams.model_validate(kw)
    err = exc.value.errors()[0]
    assert err["type"] == "infeasible"
    assert err["ctx"]["fields"] == sorted(fields)
    assert err["msg"].startswith(msg_start)


def test_a_spoke_hub_inside_a_keyway_corner_is_refused() -> None:
    """D-17: the spoke hub reads bore_mouth_limit(p), which for a keyed round bore is
    the keyway's own floor corner (D-10, L27/L28) -- a 3 x 1.4 mm keyway on the
    default bore puts the mouth at 6.179098, so hub_d 12 leaves -0.179 mm and is
    refused naming only hub_d; hub_d 13.2 builds."""
    with pytest.raises(ValidationError) as exc:
        GearParams.model_validate({**SPOKE, "hub_d": 12, "keyway_width": 3,
                                   "keyway_depth": 1.4})
    err = exc.value.errors()[0]
    assert err["type"] == "infeasible"
    assert err["ctx"]["fields"] == ["hub_d"]
    assert "13.16 mm" in err["msg"]

    GearParams.model_validate({**SPOKE, "hub_d": 13.2, "keyway_width": 3,
                               "keyway_depth": 1.4})  # does not raise


@pytest.mark.parametrize(("sf", "effective", "warning"), [
    pytest.param(3.3, 3.3, None, id="kept-no-warning"),
    pytest.param(3.35, 3.337,
                 "Spoke fillet reduced to 3.337 mm to fit the opening between the "
                 "arms at the hub.", id="capped-at-opening"),
    pytest.param(5, 3.337,
                 "Spoke fillet reduced to 3.337 mm to fit the opening between the "
                 "arms at the hub.", id="capped-at-field-max"),
])
def test_a_spoke_fillet_is_capped_to_whichever_limit_binds_first(
        sf: float, effective: float, warning: str | None) -> None:
    """D-06: spoke_fillet_effective is 0.45 x the smaller of the hub opening and the
    annulus width, capped and warned (L03), never refused."""
    d = derive(GearParams.model_validate({**SPOKE, "spoke_fillet": sf}))
    assert d.spoke_fillet_effective == pytest.approx(effective)
    assert d.warnings == ((warning,) if warning else ())

    # hub_d 12, rim_wall 6 narrows the annulus below the hub opening -- the other
    # limit binds, and the reason sentence names it.
    d2 = derive(GearParams.model_validate({"spoke_count": 4, "spoke_width": 2,
                                           "hub_d": 12, "rim_wall": 6,
                                           "spoke_fillet": 2}))
    assert d2.spoke_fillet_effective == pytest.approx(1.097)
    assert d2.warnings == (
        "Spoke fillet reduced to 1.097 mm to fit between the hub and the rim wall.",)


def test_a_sub_print_precision_spoke_fillet_request_still_warns() -> None:
    """10-REVIEW.md WR-01/CR-01's rule, applied to the spoke fillet's own 0.001 mm cut
    resolution: a nonzero request that rounds to 0 cuts no fillet and says so, naming
    the true cause (print resolution), not a limit nowhere close to binding."""
    d = derive(GearParams.model_validate({**SPOKE, "spoke_fillet": 0.0004}))
    assert d.spoke_fillet_effective == pytest.approx(0.0)
    assert d.warnings == (
        "Spoke fillet 0.0004 mm is below the 0.001 mm resolution it is cut at and "
        "was not cut.",)

    d0 = derive(GearParams.model_validate({**SPOKE, "spoke_fillet": 0}))
    assert d0.spoke_fillet_effective is None
    assert d0.warnings == ()


@pytest.mark.parametrize(("kw", "warning"), [
    pytest.param({"spoke_width": 2, "hub_d": 12, "rim_wall": 1, "spoke_fillet": 1},
                 "No spoke arms with spoke_count 0: spoke_width (2 mm), hub_d (12 mm), "
                 "rim_wall (1 mm) and spoke_fillet (1 mm) are ignored.", id="all-set"),
    pytest.param({"spoke_width": 2},
                 "No spoke arms with spoke_count 0: spoke_width (2 mm) is ignored.",
                 id="width-only"),
    pytest.param({"hub_d": 12},
                 "No spoke arms with spoke_count 0: hub_d (12 mm) is ignored.",
                 id="hub-only"),
])
def test_spoke_dimensions_without_a_count_are_ignored_and_named(
        kw: dict[str, object], warning: str) -> None:
    """D-15: spoke_count 0 (the default) builds nothing regardless of the other four
    spoke fields, and derive() says so naming only the fields the user set."""
    d = derive(GearParams.model_validate(kw))
    assert d.cutout_hub_wall is None
    assert d.cutout_rim_wall is None
    assert d.spoke_fillet_effective is None
    assert d.warnings == (warning,)


def test_the_spoke_count_is_an_integer_from_0_to_200() -> None:
    """D-18: field-level ValidationErrors (not the "infeasible" custom error) one step
    either side of the bound, and for the wrong type."""
    for bad in ({"spoke_count": 201, "spoke_width": 1, "hub_d": 10, "rim_wall": 1},
               {"spoke_count": -1, "spoke_width": 1, "hub_d": 10, "rim_wall": 1},
               {"spoke_count": 2.5, "spoke_width": 1, "hub_d": 10, "rim_wall": 1}):
        with pytest.raises(ValidationError) as exc:
            GearParams.model_validate(bad)
        assert exc.value.errors()[0]["type"] != "infeasible"
    GearParams.model_validate({"spoke_count": 1, "spoke_width": 1, "hub_d": 12,
                               "rim_wall": 1})
    GearParams.model_validate({"teeth": 200, "spoke_count": 200, "spoke_width": 0.4,
                               "hub_d": 52, "rim_wall": 0.4, "bore_flat": 0,
                               "recess_sides": "none"})


def test_multiple_refusals_come_in_check_order_and_name_each_field_once() -> None:
    """REQ-cutout-conflicts-refused-early: several breaches arrive as one message, the
    sentences in check()'s fixed order (arm, rim, hub), and ctx.fields lists each
    named field once, sorted."""
    with pytest.raises(ValidationError) as exc:
        GearParams.model_validate({"spoke_count": 4, "spoke_width": 0.3, "hub_d": 10,
                                   "rim_wall": 0.3})
    err = exc.value.errors()[0]
    assert err["type"] == "infeasible"
    assert err["ctx"]["fields"] == ["hub_d", "rim_wall", "spoke_width"]
    arm_at = err["msg"].index("Spoke arms 0.3 mm wide")
    rim_at = err["msg"].index("The rim wall (0.3 mm)")
    hub_at = err["msg"].index("The spoke hub is too small")
    assert arm_at < rim_at < hub_at
    assert cutout_walls(GearParams(), profile(GearParams()).rf) is None
