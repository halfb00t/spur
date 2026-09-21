import math

import pytest
from pydantic import ValidationError

from spur.calc import (
    MIN_WALL, bore_radius, centre_distance, derive, inv, profile, recess_radii,
    span_measurement, with_mate,
)
from spur.params import GearParams


def test_default_dimensions():
    d = derive(GearParams())
    assert d["pitch_d"] == pytest.approx(33.25)
    assert d["tip_d"] == pytest.approx(36.75)
    assert d["root_d"] == pytest.approx(28.875)
    assert d["base_d"] == pytest.approx(33.25 * math.cos(math.radians(25)), abs=1e-3)
    assert d["web"] == pytest.approx(3.5)
    # The recess capping added in the 2026-09-21 review must not move the stock gear:
    # every shareable link that omits these fields depends on them.
    assert d["recess_id"] == pytest.approx(13.013)
    assert d["recess_od"] == pytest.approx(25.013)
    assert d["recess_fillet"] == pytest.approx(0.5)
    assert d["warnings"] == []


def test_caliper_reading_is_short_for_odd_tooth_counts():
    odd, even = derive(GearParams(teeth=19)), derive(GearParams(teeth=20))
    assert odd["caliper_over_tips"] < odd["tip_d"]
    assert even["caliper_over_tips"] == even["tip_d"]


@pytest.mark.parametrize(("m", "pa", "k", "w"), [
    (1.75, 20, 3, 13.381),   # hand-checked Wildhaber span
    (1.75, 25, 3, 13.360),
    (1.0, 20, 3, 7.646),
])
def test_span_measurement(m, pa, k, w):
    p = GearParams(module=m, pressure_angle=pa, bore_d=0, recess_sides="none")
    kk, ww = span_measurement(p)
    assert kk == k
    assert ww == pytest.approx(w, abs=2e-3)


def test_higher_pressure_angle_gives_finer_tips_and_thicker_roots():
    a, b = derive(GearParams(pressure_angle=20)), derive(GearParams(pressure_angle=25))
    assert b["tip_thickness"] < a["tip_thickness"]
    assert b["root_thickness"] > a["root_thickness"]


def test_centre_distance_unshifted_and_shifted():
    p = GearParams()
    assert centre_distance(p, 40) == pytest.approx(1.75 * 59 / 2)
    assert centre_distance(GearParams(profile_shift=0.3), 40) > 1.75 * 59 / 2


def test_root_fillet_is_capped_with_a_warning():
    d = derive(GearParams(teeth=80, module=0.5, bore_d=5, bore_flat=0))
    assert d["root_fillet"] < 0.5
    assert any("Root fillet reduced" in w for w in d["warnings"])


@pytest.mark.parametrize(("kw", "field"), [
    ({"bore_flat": 3}, "bore_flat"),
    ({"recess_depth": 3.6}, "recess_depth"),
    ({"pressure_angle": 35, "profile_shift": 1}, "pressure_angle"),
    ({"bore_d": 30}, "bore_d"),
])
def test_infeasible_parameters_name_their_fields(kw, field):
    with pytest.raises(ValidationError) as exc:
        GearParams(**kw)
    err = exc.value.errors()[0]
    assert err["type"] == "infeasible"
    assert field in err["ctx"]["fields"]


def test_no_bore_ignores_d_flat():
    assert GearParams(bore_d=0).bore_flat == 8.0


def test_tooth_thickness_and_gap_are_measured_on_the_same_circle():
    """Thickness + gap must add up to the pitch on the root circle.

    They did not when the base circle sat outside the root circle, which is the case for
    the default 19-tooth gear: the thickness was read at the base circle instead.
    """
    for teeth in (19, 40):  # 19 -> rb > rf (the broken case), 40 -> rf > rb
        p = GearParams(teeth=teeth)
        d, pr = derive(p), profile(GearParams(teeth=teeth))
        assert d["root_thickness"] + d["root_gap"] == pytest.approx(
            2 * math.pi * pr.rf / teeth, abs=2e-3)


def test_oversized_recess_is_narrowed_to_fit_and_says_so():
    d = derive(GearParams(recess_width=12))
    assert any("Recess narrowed" in w for w in d["warnings"])
    assert (d["recess_od"] - d["recess_id"]) / 2 < 12  # radial width, capped
    p = GearParams(recess_width=12)
    assert d["recess_id"] / 2 >= bore_radius(p) + p.bore_chamfer + MIN_WALL - 1e-9
    assert d["recess_od"] / 2 <= profile(p).rf - MIN_WALL + 1e-9


def test_small_gear_keeps_the_stock_bore_and_recess():
    """The README's own example: defaults sized for a 19-tooth m=1.75 gear must not
    refuse a 24-tooth m=1 one over a parameter the user never touched."""
    d = derive(GearParams(teeth=24, module=1, pressure_angle=20, bore_flat=0))
    assert any("Recess narrowed" in w for w in d["warnings"])
    assert d["recess_id"] is not None


def test_recess_is_dropped_when_there_is_no_room_at_all():
    d = derive(GearParams(teeth=16, module=1, bore_d=9, bore_flat=8))
    assert d["recess_id"] is None
    assert any("No room for a face recess" in w for w in d["warnings"])


def test_recess_fillet_is_capped_to_the_narrowed_groove():
    d = derive(GearParams(recess_width=12, recess_fillet=3))
    assert d["recess_fillet"] < 3
    assert any("Recess fillet reduced" in w for w in d["warnings"])


@pytest.mark.parametrize(("kw", "mate"), [
    ({"teeth": 6, "pressure_angle": 14.5, "profile_shift": -0.6}, 40),
    ({"teeth": 6, "pressure_angle": 14.5, "profile_shift": -0.5}, 12),
])
def test_impossible_pairs_have_no_centre_distance(kw, mate):
    """inv(aw) = inv(a) + 2 tan(a) x / z has no root when the right-hand side is
    negative: the pair cannot mesh at any distance. It used to return garbage -- 39.4 mm
    where the nominal is 70, and negative numbers elsewhere."""
    p = GearParams(bore_d=0, bore_flat=0, bore_chamfer=0, recess_sides="none", **kw)
    assert centre_distance(p, mate) is None
    out = with_mate(derive(p), p, mate)
    assert out["centre_distance"] is None
    assert any("cannot mesh" in w for w in out["warnings"])


def test_centre_distance_matches_an_independent_solver():
    def bisect(p, z2):
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
