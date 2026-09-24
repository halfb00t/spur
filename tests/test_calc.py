import math
from typing import Any

import pytest
from pydantic import ValidationError

from spur.calc import (
    MIN_WALL,
    DerivedDimensions,
    bore_radius,
    centre_distance,
    derive,
    inv,
    profile,
    span_measurement,
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
    assert d.warnings == []
    # D-01, edge: empty -- no mate was asked about, so both mate fields are present
    # and null, never omitted.
    assert d.mate_teeth is None
    assert d.centre_distance is None


def test_a_derived_dimensions_result_cannot_be_changed() -> None:
    """A result shared between readers cannot change under them (D-09, edge:
    concurrency): DerivedDimensions is frozen, so every field assignment raises."""
    d = derive(GearParams())
    for name in DerivedDimensions.model_fields:
        with pytest.raises(ValidationError, match="frozen"):
            setattr(d, name, None)


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
def test_infeasible_parameters_name_their_fields(kw: dict[str, Any], field: str) -> None:
    with pytest.raises(ValidationError) as exc:
        GearParams(**kw)
    err = exc.value.errors()[0]
    assert err["type"] == "infeasible"
    assert field in err["ctx"]["fields"]


def test_no_bore_ignores_d_flat() -> None:
    assert GearParams(bore_d=0).bore_flat == 8.0


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
def test_impossible_pairs_have_no_centre_distance(kw: dict[str, Any], mate: int) -> None:
    """inv(aw) = inv(a) + 2 tan(a) x / z has no root when the right-hand side is
    negative: the pair cannot mesh at any distance. It used to return garbage -- 39.4 mm
    where the nominal is 70, and negative numbers elsewhere."""
    p = GearParams(bore_d=0, bore_flat=0, bore_chamfer=0, recess_sides="none", **kw)
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
