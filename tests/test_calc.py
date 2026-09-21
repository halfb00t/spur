import math

import pytest
from pydantic import ValidationError

from spur.calc import centre_distance, derive, span_measurement
from spur.params import GearParams


def test_default_dimensions():
    d = derive(GearParams())
    assert d["pitch_d"] == pytest.approx(33.25)
    assert d["tip_d"] == pytest.approx(36.75)
    assert d["root_d"] == pytest.approx(28.875)
    assert d["base_d"] == pytest.approx(33.25 * math.cos(math.radians(25)), abs=1e-3)
    assert d["web"] == pytest.approx(3.5)
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
    ({"recess_width": 12}, "recess_width"),
])
def test_infeasible_parameters_name_their_fields(kw, field):
    with pytest.raises(ValidationError) as exc:
        GearParams(**kw)
    err = exc.value.errors()[0]
    assert err["type"] == "infeasible"
    assert field in err["ctx"]["fields"]


def test_no_bore_ignores_d_flat():
    assert GearParams(bore_d=0).bore_flat == 8.0
