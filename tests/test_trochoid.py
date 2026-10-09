"""The calc-tier proofs of Phase 18: the hob's cutter, the trochoid root generated from
it, the predicate that answers for a gear, and the swept-cutter oracle that reads the
curve as the cut boundary. The generator sweep over the allowed box lives in
tests/test_calc.py (D-13); the oracle itself is tests/trochoid_oracle.py, which shares
no code with spur.calc.
"""

import json
import math
import re
import time
from dataclasses import FrozenInstanceError, replace
from functools import cache
from itertools import pairwise
from pathlib import Path

import pytest
from pydantic import ValidationError
from trochoid_oracle import clearance

from bench.trochoid import ORACLE_BAR_MM as BENCH_ORACLE_BAR_MM
from bench.trochoid import tuned_shift
from spur.calc import (
    _ROOT_SENTENCES,
    PROFILE_SHIFT_MAX,
    ROOT_CURVE_POINTS,
    ROOT_WAIST_FLOOR,
    TROCHOID_JOIN_EPS,
    Cutter,
    Profile,
    _junction,
    _root_curve,
    _trochoid_point,
    _undercut_advice,
    _waist,
    cutter,
    derive,
    profile,
    root_mode,
    root_warnings,
    trochoid_root,
    undercut_shift,
    undercut_teeth,
)
from spur.params import GearParams

# mm, how far from zero the swept-cutter oracle may read a point of a correct curve. Two
# numbers set it, measured 2026-10-08 (Apple M2 Max, Python 3.12.13): the generator's worst
# gap from the oracle's reading, and the oracle's own resolution after golden-section
# refinement (about 1e-15 mm; 2e-16 to 2.7e-15 on the twelve gate rows).
#   - Over the twelve gate rows the worst reading is 9.8e-15 mm (module 10, 9.8e-16 per
#     module). Over all 10,326 curves of the sweep product (bench/trochoid.py oracle) it
#     is 2.99e-12 mm, at the one case of 26 teeth in the join band, where the curve ends at
#     the cutter's flank foot, 2*(tan(phi) - phi) = 2.44e-13 rad off the involute (18-03):
#     geometry, not noise; the next, 1.1e-12 mm, is the other band case; every other curve
#     reads 1.6e-13 mm or less (module 10, 116 teeth) and 15 read above 1e-13.
#   - Headroom of 1e-9 mm: 1.0e5 over the gate rows, 335 over the product's worst (the band
#     case) and 6.3e3 over its worst outside the band. The tripwire, the tracer curve
#     generated at tip radius + 1e-6 mm, reads 2.2e-7 mm: 220 times the bar.
# The oracle searches the roll over +-3 spans of 2 pi / z (tests/trochoid_oracle.py): at
# +-1 span, 3,244 curves of the product read up to 0.61 mm uncut.
ORACLE_BAR_MM = 1e-9

# rad, how far the cutter's last half-angle may sit from Profile.half_angle at its radius
# on a tangent junction. Measured 2026-10-08 (Apple M2 Max, Python 3.12.13, 1-minute load
# 1.9, four rows below): the largest gap is 4.2e-17 rad, 1.5 ulp of an angle near 0.2 rad
# (2.8e-17); 18-RESEARCH read 7.6e-17 and PITFALLS 4.9e-17. The bar is the 1e-12 floor
# for libm differences between this host (macOS arm64) and CI (ubuntu): 2.4e4 times the
# largest measured gap.
JUNCTION_BAR_RAD = 1e-12
# mm, the same for the radius against sqrt(rb^2 + xi^2). Largest measured gap 1.8e-15 mm,
# one ulp at R 15.3 mm (1.78e-15); the 1e-12 floor is 560 times that.
JUNCTION_BAR_MM = 1e-12
# rad, how far the unit tangents of the trochoid and the involute may differ at a tangent
# junction, measured on the secant over the last 1e-7 rad of contact-normal angle. The
# four rows read 1.1e-7 to 1.4e-7 rad, and that is the secant's own error, not noise: the
# angle is 1.39 * step and 1.16 * step at steps of 1e-4 down to 1e-6, so the tangents
# agree and only the chord differs. The bar is the smallest power of ten above 10x the
# largest reading (1.4e-6): headroom 72. The crossing row (17 teeth, 20 degrees, tip
# radius 0.38 mm, z_min 17.10) reads 3.1e-3 rad at its crossing, 308 times the bar.
DIRECTION_BAR_RAD = 1e-5
STEP = 1e-7  # rad, the contact-normal step the secants are taken over


def _gear(**fields: object) -> GearParams:
    """A test gear with the bore off: the default 9 mm bore refuses small gears."""
    return GearParams.model_validate(
        {"bore_d": 0, "bore_flat": 0, "bore_chamfer": 0, "recess_sides": "none", **fields})


def _swept(points: tuple[tuple[float, float], ...], p: GearParams, rho: float,
           *, neighbours: bool = True) -> list[float]:
    """The oracle's readings for `points` on gear `p` cut by tip radius `rho`."""
    return clearance(points, teeth=p.teeth, module=p.module, pressure_angle=p.pressure_angle,
                     profile_shift=p.profile_shift, backlash=p.backlash, rho=rho,
                     neighbours=neighbours)


def _tip_land(p: GearParams, rho: float) -> float:
    """Half-width of the cutter's flat tip, written out here from the textbook rack
    (dedendum 1.25 m, flank angle alpha, tooth width pi*m - s on the rolling line)
    without calc."""
    alpha = math.radians(p.pressure_angle)
    m, x = p.module, p.profile_shift
    space = math.pi * m - (m * (math.pi / 2 + 2 * x * math.tan(alpha)) - p.backlash)
    return space / 2 + (rho - m * (1.25 - x)) * math.tan(alpha) - rho / math.cos(alpha)


@pytest.mark.parametrize(("module", "pressure_angle", "backlash", "printed", "per_module"), [
    pytest.param(1.75, 25, 0.10, 0.63478, 0.36273, id="default-gear-backlash-0.10"),
    pytest.param(1.75, 25, 0.0, 0.55629, 0.31788, id="default-gear-backlash-0"),
    pytest.param(1.0, 20, 0.0, 0.47191, 0.47191, id="module-1-20-degrees"),
])
def test_the_cap_formula_reconciles_0_318_m_and_0_363_m_as_one_cap_at_two_backlashes(
        module: float, pressure_angle: float, backlash: float, printed: float,
        per_module: float) -> None:
    """REQ-cutter-defined-once, the phase's first test: two earlier research files
    disagreed about the largest cutter tip radius. PITFALLS gave 0.635 mm = 0.363 m (module
    1.75, 25 degrees), STACK and FEATURES gave 0.318 m. They are one formula,
    (pi*m/4 + backlash/2 - 1.25*m*tan(alpha)) / (1/cos(alpha) - tan(alpha)): PITFALLS' is
    the default gear's 0.10 mm backlash entering the tip land as backlash/2, STACK's is the
    same gear at backlash 0 (SUMMARY's inference, measured here 2026-10-08: 0.63478 mm =
    0.36273 m at backlash 0.10 and 0.55629 mm = 0.31788 m at 0). Module 1, 20 degrees,
    backlash 0 reads 0.47191 mm. The cap does not depend on the profile shift (the rack
    displaces, its tip land does not move), so three shifts are read."""
    alpha = math.radians(pressure_angle)
    closed = ((math.pi * module / 4 + backlash / 2 - 1.25 * module * math.tan(alpha))
              / (1 / math.cos(alpha) - math.tan(alpha)))
    for x in (-0.4, 0.0, 0.6):
        p = _gear(teeth=19, module=module, pressure_angle=pressure_angle, profile_shift=x,
                  backlash=backlash)
        c = cutter(p, 0.0)
        assert c.rho_max == pytest.approx(closed, rel=1e-12)
        assert c.rho_max == pytest.approx(printed, abs=5e-6)
        assert c.rho_max / module == pytest.approx(per_module, abs=5e-6)


def test_the_cap_is_floored_and_warned_one_print_step_either_side() -> None:
    """REQ-cutter-defined-once, precision (F3): at module 0.5, 15 degrees, 12 teeth,
    backlash 0 the unrounded cap is 0.29353 mm. 0.293 is under it and is used unchanged,
    silently; 0.294 is over it and is cut to the cap floored to 3 dp, 0.293, with the cap
    sentence naming 0.293 mm; a request exactly equal to the unrounded cap is not
    trimmed. round(cap, 3) would have given 0.294, a tip land of -3.6e-4 mm: a legal gear
    refused as having none. The used and the printed radius are one float. The expected
    sentence was captured from root_warnings on 2026-10-08, never typed (L33)."""
    p = _gear(teeth=12, module=0.5, pressure_angle=15, profile_shift=0, backlash=0)
    cap = cutter(p, 0.0).rho_max
    assert cap == pytest.approx(0.29353, abs=5e-6)
    sentence = ("root_fillet is the hob's tip radius here, and it was reduced to 0.293 mm, "
                "within 0.001 mm of the largest that keeps the cutter a tip land at this "
                "pressure angle and backlash.")

    for request, used, warns in [(0.293, 0.293, ()), (0.294, 0.293, (sentence,)),
                                 (cap, cap, ())]:
        rm = root_mode(p, profile(p), requested="trochoid", rho=request)
        assert (rm.mode, rm.reason) == ("trochoid", None)
        assert rm.cutter is not None
        assert rm.cutter.rho == used
        assert rm.cutter.rho_requested == request
        assert rm.cutter.a >= 0
        assert root_warnings(rm) == warns

    assert round(cap, 3) == 0.294
    assert _tip_land(p, round(cap, 3)) < 0


@pytest.mark.parametrize(("fields", "has_land", "sentence"), [
    pytest.param({"teeth": 12, "module": 1, "profile_shift": 0, "backlash": 0,
                  "pressure_angle": 32.0}, True, None, id="backlash-0-32.0-has-a-land"),
    pytest.param({"teeth": 12, "module": 1, "profile_shift": 0, "backlash": 0,
                  "pressure_angle": 32.5}, False,
                 "The cutter has no tip land at a 32.5 degree pressure angle with this module "
                 "and backlash: no trochoid root is computed and the analytic root is used.",
                 id="backlash-0-32.5-has-none"),
    pytest.param({"teeth": 19, "module": 1.75, "profile_shift": -0.4, "backlash": 0.10,
                  "pressure_angle": 33.0}, True, None, id="default-backlash-33.0-has-a-land"),
    pytest.param({"teeth": 19, "module": 1.75, "profile_shift": -0.4, "backlash": 0.10,
                  "pressure_angle": 33.5}, False,
                 "The cutter has no tip land at a 33.5 degree pressure angle with this module "
                 "and backlash: no trochoid root is computed and the analytic root is used.",
                 id="default-backlash-33.5-has-none"),
])
def test_the_tip_land_limit_moves_with_backlash_and_module_one_field_step_either_side(
        fields: dict[str, object], has_land: bool, sentence: str | None) -> None:
    """REQ-cutter-defined-once, boundary (F2): the pressure angle above which the 1.25 m
    rack has no tip land is tan(alpha) = (pi/4 + backlash/(2*module)) / 1.25, not a
    constant: 32.14 degrees at backlash 0, 33.07 at the default backlash and module 1.75
    (ROADMAP's "about 32.1" is the first). So it is pinned one pressure-angle field step
    (0.5 degree) either side at both: the sign of the sharp-corner land flips between
    32.0 and 32.5, and between 33.0 and 33.5. With no land trochoid_root returns None and
    root_mode names `tip land gone` with its sentence, captured from root_warnings on
    2026-10-08, never typed (L33)."""
    p = _gear(**fields)
    c = cutter(p, 0.0)
    rm = root_mode(p, profile(p), requested="trochoid", rho=0.0)
    if has_land:
        assert c.a0 > 0
        assert trochoid_root(c) is not None
        assert (rm.mode, rm.reason) == ("trochoid", None)
        assert root_warnings(rm) == ()
    else:
        assert c.a0 < 0
        assert trochoid_root(c) is None
        assert (rm.mode, rm.reason) == ("radial", "tip land gone")
        assert root_warnings(rm) == (sentence,)


def test_a_sharp_cutter_and_a_corner_centre_on_the_rolling_line_are_both_legal() -> None:
    """REQ-cutter-defined-once, empty and adjacency (F4): a tip radius of 0 is the
    sharp-corner trochoid; a tip radius equal to the tip depth puts the corner-arc centre
    exactly on the rolling line (w_c == 0.0 at 16 teeth, module 1, 14.5 degrees, shift 1.0:
    the depth is 0.25 exactly); above it the centre is above the line. The textbook
    C + rho(C - I)/|C - I| divides by zero at the second and gouges at the third; the
    contact-normal form is one expression through all three, and the oracle reads each
    curve as the cut boundary. A tip radius exactly at the unrounded cap leaves a tip land
    of zero: the two corner arcs touch on the space centreline, so the first half-angle
    is pi/z to float."""
    tracer = _gear(teeth=10, module=1, pressure_angle=20, profile_shift=0, backlash=0)
    shifted = _gear(teeth=16, module=1, pressure_angle=14.5, profile_shift=1.0, backlash=0)
    cap = cutter(tracer, 0.0).rho_max
    rows = [(tracer, 0.0, "tracer-sharp"), (shifted, 0.25, "centre-on-line"),
            (shifted, 0.5, "centre-above-line"), (tracer, cap, "land-of-zero")]
    for p, rho, label in rows:
        c = cutter(p, rho)
        curve = trochoid_root(c)
        assert curve is not None, label
        assert all(math.isfinite(v) for point in curve.points for v in point), label
        readings = _swept(curve.points, p, c.rho)
        assert all(abs(v) <= ORACLE_BAR_MM for v in readings), (label, max(readings))
        if label == "centre-on-line":
            assert c.w_c == 0.0
        if label == "centre-above-line":
            assert c.w_c > 0
        if label == "land-of-zero":
            assert c.a == 0.0
            assert curve.points[0][1] == pytest.approx(math.pi / 10, abs=1e-15)


@pytest.mark.parametrize("rho", [
    pytest.param(math.nan, id="nan"),
    pytest.param(math.inf, id="inf"),
    pytest.param(-math.inf, id="minus-inf"),
    pytest.param(-0.1, id="negative"),
])
def test_a_tip_radius_that_is_not_a_finite_millimetre_value_is_refused_before_any_cap(
        rho: float) -> None:
    """L05, L08, 18-REVIEW WR-02: `rho` is not a GearParams field in this phase (D-07), so
    nothing validates it once at the boundary and `cutter()` is the one guard. Measured on
    the 12-tooth, module 1, 20 degree gear before the guard: a NaN failed `rho <=
    rho_max`, so it was trimmed to the cap, and `rho < rho_requested` read `0.471 < nan`,
    False, so `root_mode` answered `trochoid` with no reason and no sentence: a part
    changed that nobody asked to change. A negative radius was used as it stood: -0.1
    answered `trochoid` with no sentence, -0.5 was refused as `curve invalid` and -inf as
    `bracket degenerate`, each blaming the geometry for an input. All four now raise a
    ValueError naming the value, through `root_mode` too; it is not a `RootReason`
    because no user can reach the state, and a sentence for it would be one nobody
    reads. Zero, either sign, is the legal sharp cutter."""
    p = _gear(teeth=12, module=1, pressure_angle=20, profile_shift=0, backlash=0)
    with pytest.raises(ValueError, match=re.escape(repr(rho))):
        cutter(p, rho)
    with pytest.raises(ValueError, match=re.escape(repr(rho))):
        root_mode(p, profile(p), requested="trochoid", rho=rho)
    for sharp in (0.0, -0.0):
        c = cutter(p, sharp)
        assert c.rho == 0.0
        assert c.rho_requested == 0.0


@pytest.mark.parametrize("fields", [
    pytest.param({"teeth": 10, "module": 1, "pressure_angle": 20, "profile_shift": 0,
                  "backlash": 0}, id="tracer"),
    pytest.param({}, id="default-gear"),
])
def test_the_cutter_reads_the_root_circle_from_the_same_expression_as_profile(
        fields: dict[str, object]) -> None:
    """D-06: the cutter's tip depth and the gear's root circle are one expression
    (PITFALLS 22), so they agree to the last bit -- == and never approx -- and the
    curve starts exactly on the root circle."""
    p = _gear(**fields)
    c = cutter(p, 0.38)
    assert c.pr == profile(p)
    assert c.pr.r - c.d == c.pr.rf
    curve = trochoid_root(c)
    assert curve is not None
    assert curve.points[0][0] == c.pr.rf


def _involute_half_angle(p: GearParams, radius: float) -> float:
    """The involute's half tooth-thickness angle at `radius`, written out here again."""
    alpha = math.radians(p.pressure_angle)
    r = p.module * p.teeth / 2
    s = p.module * (math.pi / 2 + 2 * p.profile_shift * math.tan(alpha)) - p.backlash
    phi = math.acos(r * math.cos(alpha) / radius)
    return s / (2 * r) + (math.tan(alpha) - alpha) - (math.tan(phi) - phi)


def _direction_gap(p: GearParams, c: Cutter) -> float:
    """The angle, rad, between the trochoid's and the involute's direction where the
    trochoid ends, both as chords over the last STEP of contact-normal angle (the
    involute's over the same two radii). The end is the junction `trochoid_root` stops
    at: the flank's foot on a tangent join, the solved crossing on an undercut gear
    (cross-review XR-02: the foot is 4.1e-3 rad off there, the crossing 3.1e-3)."""
    junction = _junction(c, TROCHOID_JOIN_EPS)
    assert junction is not None
    beta_end = junction[0]

    def plane(radius: float, half: float) -> tuple[float, float]:
        theta = math.pi / c.pr.z - half
        return radius * math.sin(theta), radius * math.cos(theta)

    r1, h1 = _trochoid_point(c, beta_end)
    r0, h0 = _trochoid_point(c, beta_end - STEP)
    (x1, y1), (x0, y0) = plane(r1, h1), plane(r0, h0)
    (i1, j1), (i0, j0) = (plane(r1, _involute_half_angle(p, r1)),
                          plane(r0, _involute_half_angle(p, r0)))
    t = (x1 - x0, y1 - y0)
    v = (i1 - i0, j1 - j0)
    return abs(math.atan2(t[0] * v[1] - t[1] * v[0], t[0] * v[0] + t[1] * v[1]))


@pytest.mark.parametrize("backlash", [0.0, 0.10])
@pytest.mark.parametrize(("fields", "rho"), [
    pytest.param({"teeth": 19, "module": 1.75, "pressure_angle": 25}, 0.5, id="19T-25deg"),
    pytest.param({"teeth": 30, "module": 1, "pressure_angle": 20}, 0.38, id="30T-20deg"),
])
def test_the_tangent_junction_equals_the_involute_at_backlash_0_and_0_10(
        fields: dict[str, object], rho: float, backlash: float) -> None:
    """SC1: where the gear is not undercut the trochoid hands over to the involute at the
    cutter flank's foot, with no root-find, and the end point IS the involute's: its
    half-angle equals Profile.half_angle at its radius, its radius equals
    sqrt(rb^2 + xi^2), and the two curves leave in the same direction -- at backlash 0
    and 0.10, because backlash thickens the cutter tooth (a cutter without it misses by
    0.046 mm, the next test). The bars and the gaps behind them are written beside the
    constants at the top of this file, measured 2026-10-08."""
    p = _gear(profile_shift=0, backlash=backlash, **fields)
    c = cutter(p, rho)
    curve = trochoid_root(c)
    assert curve is not None
    assert curve.join == "tangent"
    radius, half = curve.points[-1]
    pr = c.pr
    gap_rad = abs(half - pr.half_angle(radius))
    gap_mm = abs(radius - math.sqrt(pr.rb ** 2 + c.xi ** 2))
    print(f"junction gaps: {gap_rad:.2e} rad, {gap_mm:.2e} mm")
    assert gap_rad <= JUNCTION_BAR_RAD
    assert gap_mm <= JUNCTION_BAR_MM
    direction = _direction_gap(p, c)
    print(f"direction gap: {direction:.2e} rad")
    assert direction <= DIRECTION_BAR_RAD


def test_a_cutter_without_backlash_misses_the_involute_and_a_crossing_is_not_tangent() -> None:
    """The two tripwires that keep the junction bars honest. (1) A cutter built with
    backlash 0 for a gear with backlash 0.10 ends 3.0e-3 rad, 0.046 mm at its radius, off
    the gear's involute: PITFALLS 3's step on the default gear, 3e9 times the bar.
    (2) Tangency is asserted only for z >= z_min: the 17-tooth, 20 degree, tip radius
    0.38 mm gear is just undercut (z_min 17.10), its curve is cut off where it crosses
    the involute, and the directions differ by 3.1e-3 rad at that crossing, 308 times the
    direction bar."""
    gear = _gear(teeth=19, module=1.75, pressure_angle=25, profile_shift=0, backlash=0.10)
    wrong = cutter(_gear(teeth=19, module=1.75, pressure_angle=25, profile_shift=0,
                         backlash=0.0), 0.5)
    curve = trochoid_root(wrong)
    assert curve is not None
    radius, half = curve.points[-1]
    gap = abs(half - profile(gear).half_angle(radius))
    print(f"backlash tripwire: {gap:.3e} rad = {gap * radius:.4f} mm")
    assert gap > 1000 * JUNCTION_BAR_RAD
    assert gap * radius == pytest.approx(0.046, abs=5e-4)

    undercut = _gear(teeth=17, module=1, pressure_angle=20, profile_shift=0, backlash=0)
    c = cutter(undercut, 0.38)
    crossing = trochoid_root(c)
    assert crossing is not None
    assert crossing.join == "crossing"
    direction = _direction_gap(undercut, c)
    print(f"crossing direction gap: {direction:.2e} rad")
    assert direction > 10 * DIRECTION_BAR_RAD


def test_nothing_requested_leaves_the_root_radial_and_silent() -> None:
    """D-04: the default is radial, whatever the gear and whatever `rho` is, so every
    present caller and the pre-v0.2 fixture are untouched; the cutter is not even built."""
    p = _gear(teeth=10, module=1, pressure_angle=20, profile_shift=0, backlash=0)
    rm = root_mode(p, profile(p), rho=0.38)
    assert (rm.mode, rm.reason, rm.cutter) == ("radial", "not requested", None)
    assert root_warnings(rm) == ()


def test_a_curve_that_cannot_be_trusted_is_refused_with_a_reason_and_no_points() -> None:
    """L08, D-10, D-11: no honest curve is None plus a named reason, never a clipped or
    healed one. Out-of-box cutters built by hand reach the three arms the allowed box
    never does (the sweep of 18-03 shows zero cases there). A cutter whose roll says
    undercut on a gear with nothing below its base circle has no bracket; one on whose
    involute the trochoid is nowhere inside it has no crossing; a curve above the tip
    circle or past the space centreline is invalid."""
    tracer = cutter(_gear(teeth=10, module=1, pressure_angle=20, profile_shift=0,
                          backlash=0), 0.38)
    thin = cutter(_gear(teeth=100, module=1, pressure_angle=20, profile_shift=0,
                        backlash=0), 0.38)
    thick = replace(tracer, pr=replace(tracer.pr, psi_p=tracer.pr.psi_p + 0.5))
    tall = replace(tracer, pr=replace(tracer.pr, ra=4.0))
    tangent = cutter(_gear(teeth=30, module=1, pressure_angle=20, profile_shift=0,
                           backlash=0), 0.38)
    past_centre = replace(tangent, a=-0.5)
    assert _root_curve(replace(thin, xi=-1.0)) == "bracket degenerate"
    assert _root_curve(thick) == "bracket degenerate"
    assert _root_curve(tall) == "curve invalid"
    assert _root_curve(past_centre) == "curve invalid"
    for c in (replace(thin, xi=-1.0), thick, tall, past_centre):
        assert trochoid_root(c) is None


def test_the_tracer_gear_is_cut_by_its_cutter_and_nothing_else() -> None:
    """The architecture on one path: 10 teeth, module 1, 20 degrees, no shift, no
    backlash, tip radius 0.38 mm. Chosen because it is undercut (z_min is 21.4 for a
    1.25 m rack with a sharp tip), so it takes the crossing branch -- the hard one --
    and because the research measured its crossing radius, 4.725602 mm (STACK 4.72560,
    base radius 4.698463), and the oracle's 1.1e-15 mm on it.

    The oracle carries the neighbouring cutter teeth and reads every point of the curve
    as the cut boundary. The control is the involute halfway between the base circle and
    the crossing radius: it runs through the material the hob removes, so it must read
    as a gouge. An oracle that reads 0 everywhere proves nothing, and this is what lets
    it fail. Measured 2026-10-08: worst point 1.0e-15 mm, control -3.7e-3 mm."""
    p = _gear(teeth=10, module=1, pressure_angle=20, profile_shift=0, backlash=0)
    pr = profile(p)
    rm = root_mode(p, pr, requested="trochoid", rho=0.38)
    assert (rm.mode, rm.reason) == ("trochoid", None)
    assert rm.cutter is not None
    c = rm.cutter
    curve = trochoid_root(c)
    assert curve is not None
    assert curve.join == "crossing"
    assert len(curve.points) == 16
    assert curve.points[0] == (pr.rf, math.pi / 10 - c.a / pr.r)
    assert curve.points[-1][0] == pytest.approx(4.725602, abs=5e-7)

    readings = _swept(curve.points, p, c.rho)
    print(f"worst oracle reading on the tracer curve: {max(abs(v) for v in readings):.3e} mm")
    assert all(abs(v) <= ORACLE_BAR_MM for v in readings)

    radius = (pr.rb + curve.points[-1][0]) / 2
    control = _swept(((radius, _involute_half_angle(p, radius)),), p, c.rho)[0]
    print(f"involute control (a gouge): {control:.3e} mm")
    assert control < -1e-4


@cache
def _fixture_gears() -> tuple[tuple[str, GearParams], ...]:
    """The 44 pre-v0.2 regression records as gears, read-only: the fixture is Phase 20's
    to move, never this phase's (SC5), and its modules import siblings by bare name, so
    only the JSON is read."""
    path = Path(__file__).parent / "regression" / "pre_v0_2.json"
    records: dict[str, dict[str, object]] = json.loads(path.read_text())["records"]
    return tuple((name, GearParams.model_validate(record["params"]))
                 for name, record in records.items())


def test_every_pre_v0_2_record_reads_radial_because_nobody_asked() -> None:
    """REQ-root-mode-single-predicate, empty (D-04): the call every present consumer would
    make, root_mode(p, profile(p)), reads radial / "not requested" with no cutter and no
    warning on all 44 records of the pre-v0.2 fixture, whatever the gear and whatever rho
    is passed beside it, so wiring it in later cannot move a record that nobody asked to
    move. The call the consumers make since 19-04, with the record's own root_shape and
    root_fillet, reads the same (REQ-root-mode-decided: every record spells nothing, so
    the field defaults to radial and the part and the document are the shipped ones)."""
    gears = _fixture_gears()
    assert len(gears) == 44
    for name, p in gears:
        pr = profile(p)
        for rm in (root_mode(p, pr), root_mode(p, pr, rho=0.38),
                   root_mode(p, pr, requested=p.root_shape, rho=p.root_fillet)):
            assert (rm.mode, rm.reason, rm.cutter) == ("radial", "not requested", None), name
            assert rm.curve is None, name
            assert root_warnings(rm) == (), name


def test_the_default_gear_asked_for_the_hob_root_prints_its_numbers_and_no_radial_ones() -> None:
    """The tracer, calc tier (D-01, D-03, D-05; REQ-derived-numbers-honest-under-trochoid):
    the default gear with root_shape "trochoid" prints no tooth thickness or gap at the
    root, the tip radius the cutter used (0.5 mm, under its 0.6348 mm cap), and one
    sentence saying why the two are absent -- and every number that does not depend on the
    root's shape equal to the radial document's, because root_d is the same rf in both
    (probe precision). No straight-chord sentence: there is no chord. The sentence was
    captured from derive() on 2026-10-09, never composed here (L33)."""
    sentence = ("root_thickness and root_gap are not printed with the hob-cut root: the "
                "tooth's thickness changes too fast with radius near the root circle to "
                "give one honest number there.")
    hob, radial = derive(GearParams(root_shape="trochoid")), derive(GearParams())
    assert hob.root_thickness is None
    assert hob.root_gap is None
    assert hob.root_fillet == 0.5
    assert hob.warnings == (sentence,)
    shared = ("root_d", "pitch_d", "tip_d", "base_d", "caliper_over_tips", "tip_thickness",
              "span_teeth", "span")
    assert len(shared) == 8
    for name in shared:
        assert getattr(hob, name) == getattr(radial, name), name
    assert radial.root_thickness is not None
    assert radial.warnings == ()


def test_a_link_that_spells_the_default_root_shape_is_the_link_that_omits_it() -> None:
    """Probe adjacency (REQ-root-mode-decided, L05): "radial" is the default, so a link
    that writes it and one that leaves it out are one parameter object -- equal, equally
    hashed (the solid cache keys on it) and deriving the same document."""
    spelled, omitted = GearParams(root_shape="radial"), GearParams()
    assert spelled == omitted
    assert hash(spelled) == hash(omitted)
    assert derive(spelled) == derive(omitted)
    assert GearParams(root_shape="trochoid") != omitted


def test_a_trochoid_request_with_nothing_radial_to_replace_prints_the_radial_numbers_and_says_so(
) -> None:
    """Probe boundary (REQ-root-mode-decided), the derive tier of the 41/42 rows of
    test_root_mode_hands_back_where_the_involute_reaches_the_root_circle: module 1, 20
    degrees, no shift, no backlash, tip radius 0.38 mm. 41 teeth have a radial root to
    replace and print the hob's document (null thickness and gap). 42 do not: the request
    is refused, the root is the radial one, and the document is the radial request's
    thickness, gap and fillet with the sentence that explains the refusal -- never the
    hob's null. Both sentences were captured from derive() on 2026-10-09 (L33)."""
    thickness_sentence = (
        "root_thickness and root_gap are not printed with the hob-cut root: the tooth's "
        "thickness changes too fast with radius near the root circle to give one honest "
        "number there.")
    refusal = ("No radial root to replace on this gear (base circle 19.734 mm, root circle "
               "19.750 mm): the trochoid root request is ignored.")
    fields = {"module": 1, "pressure_angle": 20, "profile_shift": 0, "backlash": 0,
              "root_fillet": 0.38}
    hob41 = derive(_gear(teeth=41, root_shape="trochoid", **fields))
    assert (hob41.root_thickness, hob41.root_gap, hob41.root_fillet) == (None, None, 0.38)
    assert hob41.warnings == (thickness_sentence,)

    asked = derive(_gear(teeth=42, root_shape="trochoid", **fields))
    radial = derive(_gear(teeth=42, **fields))
    assert (asked.root_thickness, asked.root_gap, asked.root_fillet) == (2.065, 0.889, 0.38)
    assert (asked.root_thickness, asked.root_gap, asked.root_fillet) == (
        radial.root_thickness, radial.root_gap, radial.root_fillet)
    assert asked.warnings == (refusal,)
    assert asked.root_d == radial.root_d


def test_root_form_d_is_twice_the_junction_radius_and_null_when_radial() -> None:
    """REQ-derived-numbers-honest-under-trochoid (D-04): root_form_d is the cutter-envelope
    junction, twice the radius where the hob-cut root meets the involute, at 3 dp. On the
    default gear (a tangent join) that radius is sqrt(rb^2 + xi^2), written out here from
    the base radius and the cutter's flank-foot roll and not read from the curve: 30.558
    mm. On the 10-tooth, module 1, 20 degree, backlash 0, tip radius 0.38 mm gear (a
    crossing, no closed form) it is 9.451. Null where the part has the radial root: a
    gear nobody asked about, a request refused for a severed tooth (it builds the radial
    root, so its thickness is the radial one), and all 44 pre-v0.2 fixture records.
    Captured from derive() on 2026-10-09 (L33)."""
    default = GearParams(root_shape="trochoid")
    c = cutter(default, default.root_fillet)
    rb = default.module * default.teeth / 2 * math.cos(math.radians(default.pressure_angle))
    assert derive(default).root_form_d == round(2 * math.hypot(rb, c.xi), 3) == 30.558
    curve = trochoid_root(c)
    assert curve is not None
    assert derive(default).root_form_d == round(2 * curve.points[-1][0], 3)

    tracer = _gear(teeth=10, module=1, pressure_angle=20, profile_shift=0, backlash=0,
                   root_shape="trochoid", root_fillet=0.38)
    assert derive(tracer).root_form_d == 9.451

    assert derive(GearParams()).root_form_d is None
    severed = _gear(teeth=6, module=1, pressure_angle=14.5, profile_shift=-0.6,
                    root_fillet=0, root_shape="trochoid")
    asked = derive(severed)
    assert (asked.root_form_d, asked.root_waist) == (None, None)
    assert asked.root_thickness is not None
    assert all(derive(p).root_form_d is None for _, p in _fixture_gears())


def test_the_root_waist_is_printed_where_the_trochoid_applies_and_null_elsewhere() -> None:
    """REQ-derived-numbers-honest-under-trochoid (D-06): root_waist is the narrowest tooth
    in the hob-cut root, an arc on its own radius, 2 R h of RootCurve.waist (the smallest
    R h of the curve since 19-REVIEW CR-01, not the smallest h). On a tangent
    join the root leaves the involute with its direction, so the narrowest point is the
    junction and the waist is the involute's own thickness there: 3.303 mm on the default
    gear, checked through Profile.half_angle at sqrt(rb^2 + xi^2) and through this file's
    own involute half-angle, not through the curve. On the 10-tooth tracer gear (a
    crossing) the curve dips below the involute's thickness at its junction: 1.442 against
    1.622 (R = 4.7256 mm); it read 1.473 at the smallest half-angle, 0.031 too thick.
    Null in radial mode, on a refused request and on all 44 fixture records. Captured
    from derive() on 2026-10-09 (L33)."""
    default = GearParams(root_shape="trochoid")
    c = cutter(default, default.root_fillet)
    rb = profile(default).rb
    junction = math.hypot(rb, c.xi)
    waist = derive(default).root_waist
    assert waist == round(2 * junction * profile(default).half_angle(junction), 3)
    assert waist == round(2 * junction * _involute_half_angle(default, junction), 3)
    assert waist == 3.303

    tracer = _gear(teeth=10, module=1, pressure_angle=20, profile_shift=0, backlash=0,
                   root_shape="trochoid", root_fillet=0.38)
    rm = root_mode(tracer, profile(tracer), requested="trochoid", rho=0.38)
    assert rm.curve is not None
    assert rm.curve.join == "crossing"
    junction = rm.curve.points[-1][0]
    involute = 2 * junction * profile(tracer).half_angle(junction)
    assert derive(tracer).root_waist == 1.442
    assert 1.442 < round(involute, 3) == 1.622

    assert derive(GearParams()).root_waist is None
    assert all(derive(p).root_waist is None for _, p in _fixture_gears())


def _dense_waists(p: GearParams) -> tuple[float, float]:
    """(the smallest arc thickness 2 R h, 2 R h at the smallest half-angle), mm, of the
    hob-cut root of `p`, each the smallest of 20,001 samples from the root circle to the
    junction. The curve's own waist is not read: this is the independent check."""
    c = cutter(p, p.root_fillet)
    junction = _junction(c, TROCHOID_JOIN_EPS)
    assert junction is not None
    points = [_trochoid_point(c, junction[0] * i / 20000) for i in range(20001)]
    radius, half = min(points, key=lambda point: point[1])
    return min(2 * r * h for r, h in points), 2 * radius * half


@pytest.mark.parametrize("fields", [
    pytest.param({"teeth": 10, "module": 1, "pressure_angle": 20, "profile_shift": 0,
                  "backlash": 0, "root_fillet": 0.38}, id="10T-m1-20deg"),
    pytest.param({"teeth": 7, "module": 2, "pressure_angle": 25, "profile_shift": 0.27,
                  "root_fillet": 0}, id="7T-m2-25deg"),
    pytest.param({"teeth": 8, "module": 2, "pressure_angle": 25, "profile_shift": 0.24,
                  "root_fillet": 1}, id="8T-m2-25deg"),
])
def test_the_printed_waist_is_the_narrowest_arc_of_the_root_on_a_crossing_join(
        fields: dict[str, object]) -> None:
    """REQ-derived-numbers-honest-under-trochoid, precision (L08; 19-REVIEW CR-01): on a
    crossing join the arc thickness 2 R h is still falling below the radius where the
    half-angle is smallest, so a waist taken at the smallest half-angle prints too thick.
    Three crossing gears, the printed root_waist against the smallest of 20,001 samples
    of 2 R h to the junction. Measured 2026-10-09: printed 1.442 / 3.149 / 3.428 against
    dense 1.442 / 3.149 / 3.428, and the smallest-half-angle reading 1.473 / 3.269 /
    3.536 (2.1 %, 3.8 % and 3.1 % over). The bar is one print step, 0.001 mm; the old
    definition is 0.031 mm or more over on all three."""
    p = _hob(bore_d=0, **fields)
    assert derive(p).root_waist is not None
    rm = root_mode(p, profile(p), requested="trochoid", rho=p.root_fillet)
    assert rm.curve is not None
    assert rm.curve.join == "crossing"
    narrowest, at_smallest_angle = _dense_waists(p)
    printed = derive(p).root_waist
    assert printed is not None
    assert abs(printed - narrowest) <= 0.001
    assert at_smallest_angle - narrowest > 0.03


@pytest.mark.parametrize(("teeth", "shift", "narrowest"), [
    pytest.param(8, -0.5132, 0.395, id="8T-x-0.5132"),
    pytest.param(6, -0.3103, 0.391, id="6T-x-0.3103"),
])
def test_the_thin_waist_warning_fires_where_the_smallest_half_angle_read_over_the_floor(
        teeth: int, shift: float, narrowest: float) -> None:
    """REQ-derived-numbers-honest-under-trochoid, adjacency (D-06; 19-REVIEW CR-01): two
    crossing gears at module 1, 14.5 degrees, default backlash and tip radius 0.38 mm
    whose narrowest arc is under the 0.4 mm floor while 2 R h at the smallest half-angle
    reads 0.401 and stays silent. Measured 2026-10-09 by 20,001 samples: narrowest arc
    0.395 mm (8 teeth, shift -0.5132) and 0.391 mm (6 teeth, shift -0.3103); at the
    smallest half-angle 0.401 on both. The warning fires once and names the printed
    waist."""
    p = _hob(teeth=teeth, module=1, pressure_angle=14.5, profile_shift=shift, backlash=0.10,
             root_fillet=0.38, bore_d=0)
    dense, at_smallest_angle = _dense_waists(p)
    assert round(at_smallest_angle, 3) >= ROOT_WAIST_FLOOR
    assert round(dense, 3) == narrowest < ROOT_WAIST_FLOOR
    d = derive(p)
    assert d.root_waist == narrowest
    assert [w for w in d.warnings if "narrowest" in w] == [
        _ROOT_SENTENCES["waist thin"].format(waist=narrowest, floor=ROOT_WAIST_FLOOR)]


def _waist_at(fields: dict[str, object], shift: float) -> float:
    """The root waist, mm, of the hob-cut root at this profile shift, unrounded."""
    p = _gear(profile_shift=shift, root_shape="trochoid", **fields)
    rm = root_mode(p, profile(p), requested="trochoid", rho=p.root_fillet)
    assert rm.curve is not None
    return 2 * rm.curve.waist[0] * rm.curve.waist[1]


def _shift_for_waist(fields: dict[str, object], target: float, lo: float, hi: float) -> float:
    """The profile shift in [lo, hi] at which the waist reads `target` mm: 60 halvings,
    the waist rising with the shift (it gains about 0.015 mm per 0.01 of shift)."""
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if _waist_at(fields, mid) < target else (lo, mid)
    return (lo + hi) / 2


@pytest.mark.parametrize(("fields", "lo", "hi"), [
    pytest.param({"teeth": 8, "module": 1, "pressure_angle": 14.5, "backlash": 0.10,
                  "root_fillet": 0.38}, -0.6, 0.0, id="8T-14.5deg"),
    pytest.param({"teeth": 6, "module": 1, "pressure_angle": 14.5, "backlash": 0.10,
                  "root_fillet": 0.38}, -0.57, 0.0, id="6T-14.5deg"),
])
def test_the_waist_warning_fires_one_print_step_below_the_floor_and_not_at_it(
        fields: dict[str, object], lo: float, hi: float) -> None:
    """REQ-derived-numbers-honest-under-trochoid, boundary and adjacency (D-06, D-07): two
    of the 19-02 waist walk's series (6 and 8 teeth, module 1, 14.5 degrees, default
    backlash, tip radius 0.38 mm), the profile shift bisected until the waist reads the
    floor and then one 0.001 mm print step under it. The floor is 0.4 mm absolute. A
    waist that prints as 0.4 is silent; one that prints as 0.399 warns, once, naming the
    three fields that thicken it; the gear validates either way (nothing is refused for
    being thin). The comparison is round(waist, 3) < floor, the resolution the number
    prints at. The sentence was captured from derive() on 2026-10-09 (L33)."""
    assert ROOT_WAIST_FLOOR == 0.4
    sentence = ("The tooth is only 0.399 mm thick at its narrowest in the hob-cut root, under "
                "the 0.4 mm this design holds for a printable tooth; more teeth, a larger "
                "profile_shift or a larger pressure_angle thickens it.")
    at_floor = _shift_for_waist(fields, ROOT_WAIST_FLOOR, lo, hi)
    under = _shift_for_waist(fields, ROOT_WAIST_FLOOR - 0.001, lo, hi)
    assert under < at_floor
    on = derive(_gear(profile_shift=at_floor, root_shape="trochoid", **fields))
    below = derive(_gear(profile_shift=under, root_shape="trochoid", **fields))
    assert (on.root_waist, below.root_waist) == (0.4, 0.399)
    assert [w for w in on.warnings if "narrowest" in w] == []
    assert [w for w in below.warnings if "narrowest" in w] == [sentence]
    assert "undercut" not in sentence


def test_the_fixture_straddles_the_three_undercuts_without_mixing_them() -> None:
    """REQ-root-mode-single-predicate, adjacency (PITFALLS 1): three different things are
    called undercut. S is the shipped warning's `teeth < 2(1 - x)/sin^2(alpha)`, typed
    here from its own formula; B is the trochoid's region, `rb > rf`; U is the cutter's
    own, `c.xi < 0`. They nest (S in B, U in B: 18-RESEARCH F9) but are not the same set,
    so root_mode must decide from B and the generator and never read S.

    Captured 2026-10-08 on the 44 records: S 5, B 28, and U 8 with a sharp cutter (3
    records the shipped line calls clear, which the 1.25 m rack does undercut) or 5 with
    each record's own root fillet as the tip radius, where it coincides with S. With the
    trochoid requested the 16 records with rb <= rf read `nothing radial to replace` at
    either radius; the other 28, among them all 5 of S, split trochoid 24 / tooth severed 4
    at rho 0 and trochoid 26 / tooth severed 2 at the record's own root fillet (the
    severed ones are the 6-tooth, 14.5 degree, shift -0.6 and -0.5 gears of the API and
    calc tests)."""
    shipped, region = set(), set()
    cutter_undercut: dict[str, set[str]] = {"sharp": set(), "own": set()}
    tally: dict[str, dict[tuple[str, str | None], int]] = {"sharp": {}, "own": {}}
    for name, p in _fixture_gears():
        pr = profile(p)
        if p.teeth < 2 * (1 - p.profile_shift) / math.sin(math.radians(p.pressure_angle)) ** 2:
            shipped.add(name)
        if pr.rb > pr.rf:
            region.add(name)
        for label, rho in (("sharp", 0.0), ("own", p.root_fillet)):
            if cutter(p, rho).xi < 0:
                cutter_undercut[label].add(name)
            rm = root_mode(p, pr, requested="trochoid", rho=rho)
            key = (rm.mode, rm.reason)
            tally[label][key] = tally[label].get(key, 0) + 1
            if name in shipped:
                assert pr.rb > pr.rf
                assert rm.reason != "nothing radial to replace", name
    assert (len(shipped), len(region)) == (5, 28)
    assert shipped <= region
    assert {k: len(v) for k, v in cutter_undercut.items()} == {"sharp": 8, "own": 5}
    assert all(v <= region for v in cutter_undercut.values())
    assert cutter_undercut["sharp"] > shipped      # the cutter undercuts more than the line
    assert cutter_undercut["own"] == shipped       # and here, by coincidence, no more
    assert tally["sharp"] == {("trochoid", None): 24, ("radial", "nothing radial to replace"): 16,
                              ("radial", "tooth severed"): 4}
    assert tally["own"] == {("trochoid", None): 26, ("radial", "nothing radial to replace"): 16,
                            ("radial", "tooth severed"): 2}


def test_root_mode_hands_back_where_the_involute_reaches_the_root_circle() -> None:
    """REQ-root-mode-single-predicate, boundary (D-02): one tooth step either side of
    rb = rf at module 1, 20 degrees, shift 0, backlash 0, tip radius 0.38 mm. 41 teeth
    have rb - rf = +0.0137 mm and read trochoid; 42 have -0.0165 mm and read `nothing
    radial to replace`, with a sentence that prints both radii at 3 dp. rb == rf itself
    cannot be built from step values (the crossover is irrational in the parameters), so
    the `<=` in root_mode is pinned by these two rows and by its docstring. The sentence
    was captured from root_warnings on 2026-10-08, never typed (L33)."""
    sentence = ("No radial root to replace on this gear (base circle 19.734 mm, root circle "
                "19.750 mm): the trochoid root request is ignored.")
    for teeth, gap, mode, reason, warns in [
            (41, 0.0137, "trochoid", None, ()),
            (42, -0.0165, "radial", "nothing radial to replace", (sentence,))]:
        p = _gear(teeth=teeth, module=1, pressure_angle=20, profile_shift=0, backlash=0)
        pr = profile(p)
        assert pr.rb - pr.rf == pytest.approx(gap, abs=5e-5)
        rm = root_mode(p, pr, requested="trochoid", rho=0.38)
        assert (rm.mode, rm.reason) == (mode, reason)
        assert rm.cutter is not None
        assert rm.cutter.rho == 0.38
        assert root_warnings(rm) == warns


@pytest.mark.parametrize(("fields", "mode", "reason", "sentence"), [
    pytest.param({"teeth": 12, "module": 1, "profile_shift": 0, "backlash": 0,
                  "pressure_angle": 32.0}, "trochoid", None, None, id="backlash-0-32.0"),
    pytest.param({"teeth": 12, "module": 1, "profile_shift": 0, "backlash": 0,
                  "pressure_angle": 32.5}, "radial", "tip land gone",
                 "The cutter has no tip land at a 32.5 degree pressure angle with this module "
                 "and backlash: no trochoid root is computed and the analytic root is used.",
                 id="backlash-0-32.5"),
    pytest.param({"teeth": 19, "module": 1.75, "profile_shift": -0.4, "backlash": 0.10,
                  "pressure_angle": 33.0}, "trochoid", None, None, id="default-backlash-33.0"),
    pytest.param({"teeth": 19, "module": 1.75, "profile_shift": -0.4, "backlash": 0.10,
                  "pressure_angle": 33.5}, "radial", "tip land gone",
                 "The cutter has no tip land at a 33.5 degree pressure angle with this module "
                 "and backlash: no trochoid root is computed and the analytic root is used.",
                 id="default-backlash-33.5"),
])
def test_root_mode_refuses_where_the_cutter_has_no_tip_land(
        fields: dict[str, object], mode: str, reason: str | None, sentence: str | None) -> None:
    """REQ-root-mode-single-predicate, boundary: one pressure-angle field step either side
    of the tip-land limit, asked through root_mode (the cutter-level pin of the same rows
    is in the tip-land test above): 32.0 / 32.5 degrees at backlash 0 and 33.0 / 33.5 at
    the default gear's backlash. All four rows have rb > rf, which is what makes them
    reach this refusal and not the earlier `nothing radial to replace`. The sentences were
    captured from root_warnings on 2026-10-08, never typed (L33)."""
    p = _gear(**fields)
    pr = profile(p)
    assert pr.rb > pr.rf
    rm = root_mode(p, pr, requested="trochoid", rho=0.0)
    assert (rm.mode, rm.reason) == (mode, reason)
    assert root_warnings(rm) == (() if sentence is None else (sentence,))


def test_a_gear_failing_two_tests_reports_the_first() -> None:
    """REQ-root-mode-single-predicate, ordering (D-10): 20 teeth, module 1, shift 0,
    33.0 degrees, backlash 0 has no radial root to replace (rb - rf = -0.3633 mm) and its
    cutter has no tip land (sharp-corner land -0.0264 mm). root_mode names the first in
    its fixed order, `nothing radial to replace`; the same gear at 12 teeth, which does
    have something to replace, names the second. The sentence was captured from
    root_warnings on 2026-10-08, never typed (L33)."""
    both = _gear(teeth=20, module=1, pressure_angle=33.0, profile_shift=0, backlash=0)
    pr = profile(both)
    rm = root_mode(both, pr, requested="trochoid", rho=0.38)
    assert rm.cutter is not None
    assert pr.rb - pr.rf == pytest.approx(-0.3633, abs=5e-5)
    assert rm.cutter.a0 == pytest.approx(-0.0264, abs=5e-5)
    assert (rm.mode, rm.reason) == ("radial", "nothing radial to replace")
    assert root_warnings(rm) == (
        "No radial root to replace on this gear (base circle 8.387 mm, root circle "
        "8.750 mm): the trochoid root request is ignored.",)

    second = _gear(teeth=12, module=1, pressure_angle=33.0, profile_shift=0, backlash=0)
    assert root_mode(second, profile(second), requested="trochoid",
                     rho=0.38).reason == "tip land gone"


def _flank_samples(c: Cutter) -> tuple[list[float], tuple[tuple[float, float], ...]]:
    """The 16 samples `_root_curve` takes, rebuilt from the generator's own pieces
    (uniform in tan(beta), the last at the junction), because `trochoid_root` rightly
    returns None for the gears this is used on."""
    junction = _junction(c, TROCHOID_JOIN_EPS)
    assert junction is not None
    beta_stop = junction[0]
    s_stop = math.tan(beta_stop)
    n = ROOT_CURVE_POINTS
    betas = [math.atan(s_stop * i / (n - 1)) for i in range(n - 1)] + [beta_stop]
    return betas, tuple(_trochoid_point(c, beta) for beta in betas)


@pytest.mark.parametrize(("teeth", "shift", "half_thickness", "sample", "gouge"), [
    pytest.param(6, -0.6, -0.089372, -0.086817, -0.141352, id="6T-x-0.6-severed"),
    pytest.param(6, -0.5, -0.012726, -0.010360, -0.020146, id="6T-x-0.5-severed"),
    pytest.param(7, -0.6, 0.004709, 0.004952, None, id="7T-x-0.6-thin-but-whole"),
])
def test_a_severed_tooth_is_refused_and_the_oracle_with_neighbours_agrees(
        teeth: int, shift: float, half_thickness: float, sample: float,
        gouge: float | None) -> None:
    """REQ-root-mode-single-predicate and REQ-trochoid-proved-independently, adjacency
    (D-17, 18-RESEARCH Pitfall 3): 14.5 degrees, module 1, backlash 0, sharp cutter. A
    curve whose refined waist (smallest R h, half the arc thickness) is at or below zero
    is `tooth severed`: trochoid_root is None and root_mode names it; a thin positive
    waist (7 teeth, +0.0047 mm of half-thickness) survives as a curve that carries it.
    Refinement matters: the smallest of the 16 samples reads -0.010360 mm on the second
    row, the refined waist -0.012726 (and +0.004952 against +0.004709 on the third). The
    refined waist is within 1.5e-9 mm below a 20,001-point scan (measured 2026-10-09, the
    worst of the three rows), so the bar is 1e-8 (6.7x). It was the smallest half-angle
    until 19-REVIEW CR-01; the sign is the same (R > 0), the point is not.

    The oracle is the independent check. Fed the one-flank curve with the neighbouring
    cutter teeth on, it reads the gouge the closed predicate predicts: -0.141352 and
    -0.020146 mm at the waist on the two severed rows (18-RESEARCH read 0.141 and 0.0201 on
    its 21-point sets; these were -0.138979 and -0.020103 at the smallest half-angle before
    19-REVIEW CR-01 moved the waist to the smallest arc thickness), and nothing below
    -5e-16 mm on the 7-tooth row; with the neighbours off it reads 2e-15 mm on all three,
    because one flank is a cut boundary even on a tooth the next space cuts through -- a
    single-tooth oracle cannot see severance, the tooth k = -1 or +1 does. The tooth's
    other flank, the mirror (radius, -half-angle), reads the same gouge with the
    neighbours on or off, being inside the cutter's own sweep.
    Measured 2026-10-08. 18-02 recorded the neighbours as making no difference on a
    committed oracle whose roll window was +-1 span; the window was too narrow (a trochoid
    point's contact roll reaches 2.13 spans over the sweep product) and 18-04 widened it
    to +-3 spans, which restores the separation the research described: a gouge exactly
    where the closed predicate says severed, found only with the neighbours."""

    p = _gear(teeth=teeth, module=1, pressure_angle=14.5, profile_shift=shift, backlash=0)
    pr = profile(p)
    c = cutter(p, 0.0)
    betas, samples = _flank_samples(c)
    refined = _waist(c, betas, samples)
    waist = refined[0] * refined[1]
    smallest = min(radius * half for radius, half in samples)
    dense = min((lambda q: q[0] * q[1])(_trochoid_point(c, betas[-1] * i / 20000))
                for i in range(20001))
    print(f"{teeth}T x {shift}: smallest sample {smallest:.6f}, waist {waist:.6f} "
          f"at R {refined[0]:.4f}, dense scan {dense:.9f} mm")
    assert smallest == pytest.approx(sample, abs=5e-7)
    assert waist == pytest.approx(half_thickness, abs=5e-7)
    assert waist <= smallest
    assert waist <= dense
    assert dense - waist < 1e-8

    rm = root_mode(p, pr, requested="trochoid", rho=0.0)
    curve = trochoid_root(c)
    both = (*samples, refined)
    mirror = tuple((radius, -half) for radius, half in both)
    flank = [_swept(both, p, 0.0), _swept(both, p, 0.0, neighbours=False)]
    other = [_swept(mirror, p, 0.0), _swept(mirror, p, 0.0, neighbours=False)]
    print(f"  one flank, neighbours on / off: {min(flank[0]):.3e} / {min(flank[1]):.3e} mm; "
          f"mirror flank on / off: {min(other[0]):.6f} / {min(other[1]):.6f} mm")
    assert all(abs(v) <= ORACLE_BAR_MM for v in flank[1])

    if gouge is None:
        assert all(abs(v) <= ORACLE_BAR_MM for v in flank[0])
        assert (rm.mode, rm.reason) == ("trochoid", None)
        assert curve is not None
        assert curve.waist == refined
        assert curve.waist[1] > 0
        assert root_warnings(rm) == ()
        assert min(other[0]) >= -ORACLE_BAR_MM
        assert min(other[1]) >= -ORACLE_BAR_MM
    else:
        assert (rm.mode, rm.reason) == ("radial", "tooth severed")
        assert curve is None
        assert root_warnings(rm) == (
            "The trochoid roots of the two neighbouring tooth spaces cut this tooth through: "
            "the analytic root is used.",)
        assert min(flank[0]) == pytest.approx(gouge, abs=5e-7)
        assert min(flank[0]) < -1e-3
        assert min(other[0]) == pytest.approx(gouge, abs=5e-7)
        assert min(other[1]) < -1e-3


def _onset_teeth(module: float, alpha_deg: float, shift: float, rho: float) -> float:
    """The cutter's undercut onset, tooth count, written out here from the textbook rack
    (tip depth 1.25 m - x m, tip radius rho): STACK's z_min = 2(1.25 - x - rho*(1 -
    sin(alpha)))/sin^2(alpha), with rho in modules."""
    sin_a = math.sin(math.radians(alpha_deg))
    return 2 * (1.25 - shift - (rho / module) * (1 - sin_a)) / sin_a ** 2


def _onset_shift(module: float, alpha_deg: float, teeth: int, rho: float) -> float:
    """The profile shift at which that onset equals `teeth`, again written out here:
    x_min = 1.25 - rho*(1 - sin(alpha)) - z*sin^2(alpha)/2, with rho in modules."""
    sin_a = math.sin(math.radians(alpha_deg))
    return 1.25 - (rho / module) * (1 - sin_a) - teeth * sin_a ** 2 / 2


def test_the_undercut_onset_closed_forms_match_the_published_tables() -> None:
    """REQ-undercut-warning-restated's inputs, from the cutter that cuts (18-RESEARCH
    Pitfall 7): at module 1, backlash 0.10, no shift and tip radius 0.38 mm the onset is
    30.7909 / 17.0967 / 11.5404 teeth at 14.5 / 20 / 25 degrees (STACK's table, 4 dp)
    where the shipped `2(1 - x)/sin^2(alpha)`, typed here from its own formula, reads
    31.9029 / 17.0973 / 11.1978: close at 20 degrees only, which is the rack it was
    written for. Backlash 0.10 keeps 0.38 mm untrimmed at 25 degrees (the cap is 0.396
    mm there; at backlash 0 it would be 0.318 and the onset would be a trimmed cutter's),
    and the onset does not depend on backlash. At 10 teeth, 20 degrees the smallest
    shift that avoids undercut is 0.41508 (5 dp). Both equal the test's own closed forms
    to 1e-12 relative over a grid of angle, shift and tip radius, including a row whose
    tip radius is trimmed, where the onset is the trimmed cutter's and not the
    requested one's. Reproduced 2026-10-08."""
    for alpha, onset, shipped in [(14.5, 30.7909, 31.9029), (20.0, 17.0967, 17.0973),
                                  (25.0, 11.5404, 11.1978)]:
        p = _gear(teeth=19, module=1, pressure_angle=alpha, profile_shift=0, backlash=0.10)
        c = cutter(p, 0.38)
        assert c.rho == 0.38
        assert undercut_teeth(c) == pytest.approx(onset, abs=5e-5)
        assert 2 * (1 - 0) / math.sin(math.radians(alpha)) ** 2 == pytest.approx(shipped, abs=5e-5)

    p = _gear(teeth=10, module=1, pressure_angle=20, profile_shift=0, backlash=0.10)
    assert undercut_shift(cutter(p, 0.38)) == pytest.approx(0.41508, abs=5e-6)

    trimmed = 0
    for alpha in (14.5, 20.0, 25.0, 30.0):
        for shift in (-0.4, 0.0, 0.5):
            for rho in (0.0, 0.25, 0.38):
                p = _gear(teeth=25, module=1, pressure_angle=alpha, profile_shift=shift,
                          backlash=0.10)
                c = cutter(p, rho)
                trimmed += c.rho < rho
                assert undercut_teeth(c) == pytest.approx(
                    _onset_teeth(1, alpha, shift, c.rho), rel=1e-12)
                assert undercut_shift(c) == pytest.approx(
                    _onset_shift(1, alpha, 25, c.rho), rel=1e-12, abs=1e-12)
    assert trimmed == 6     # 30 degrees, cap 0.197 mm: 0.25 and 0.38 mm, three shifts each
    p = _gear(teeth=25, module=1, pressure_angle=30, profile_shift=0, backlash=0.10)
    c = cutter(p, 0.38)
    assert c.rho < 0.38
    assert undercut_teeth(c) != pytest.approx(_onset_teeth(1, 30, 0, 0.38), rel=1e-6)


@pytest.mark.parametrize(("teeth", "rho", "join", "onset"), [
    pytest.param(17, 0.38, "crossing", 17.0967, id="17T-rho-0.38"),
    pytest.param(18, 0.38, "tangent", 17.0967, id="18T-rho-0.38"),
    pytest.param(17, 0.0, "crossing", 21.3716, id="17T-rho-0"),
    pytest.param(18, 0.0, "crossing", 21.3716, id="18T-rho-0"),
])
def test_the_cutter_s_undercut_is_not_the_shipped_warning_s_undercut(
        teeth: int, rho: float, join: str, onset: float) -> None:
    """REQ-root-mode-single-predicate, adjacency (PITFALLS 1): one tooth step either side
    of the shipped undercut line at module 1, 20 degrees, shift 0, backlash 0. The
    shipped warning, `2(1 - x)/sin^2(alpha)` = 17.097, calls 17 teeth undercut and 18
    clear, and derive() says so for 17 only (it is untouched here). The cutter at tip
    radius 0.38 mm agrees (17 crosses the involute, 18 is tangent; its own onset is
    17.0967) but the cutter with a sharp tip does not: its onset is 21.3716, so 17 AND 18
    teeth cross while the shipped line calls 18 clear. All four rows read mode trochoid,
    because rb > rf on each: the three undercuts touch but never merge, and none of them
    decides the mode. Measured 2026-10-08: xi at 0.38 mm is -0.01654 / +0.15447, at 0
    mm -0.7476 / -0.5766."""
    p = _gear(teeth=teeth, module=1, pressure_angle=20, profile_shift=0, backlash=0)
    pr = profile(p)
    rm = root_mode(p, pr, requested="trochoid", rho=rho)
    assert pr.rb > pr.rf
    assert (rm.mode, rm.reason) == ("trochoid", None)
    assert rm.cutter is not None
    curve = trochoid_root(rm.cutter)
    assert curve is not None
    assert curve.join == join
    assert undercut_teeth(rm.cutter) == pytest.approx(onset, abs=5e-5)
    assert (teeth < undercut_teeth(rm.cutter)) == (join == "crossing")
    shipped = [w for w in derive(p).warnings if "undercut" in w]
    assert bool(shipped) == (teeth == 17)


def test_the_undercut_onset_flips_one_field_step_either_side_of_a_tuned_shift() -> None:
    """REQ-root-mode-single-predicate, boundary: at 10 teeth, module 1, 20 degrees,
    backlash 0 and tip radius 0.38 mm the smallest shift that avoids undercut is
    0.41508, so the profile-shift field's step (0.05) puts 0.40 on the undercut side
    (the join is a crossing, xi -0.04409) and 0.45 on the other (tangent, xi +0.10210).
    The onset is the same number from either gear. Measured 2026-10-08."""
    joins = []
    for shift in (0.40, 0.45):
        p = _gear(teeth=10, module=1, pressure_angle=20, profile_shift=shift, backlash=0)
        c = cutter(p, 0.38)
        curve = trochoid_root(c)
        assert curve is not None
        joins.append(curve.join)
        assert 0.40 < undercut_shift(c) < 0.45
        assert undercut_shift(c) == pytest.approx(0.41508, abs=5e-6)
    assert joins == ["crossing", "tangent"]


def test_t1_the_closed_form_onset_pins_when_the_root_is_a_crossing() -> None:
    """SC3, the T1 tier: a closed form typed in this test, independent of calc's
    expressions, pins *when* the root is a crossing over a grid of gears. Module 1; teeth
    6-40; 14.5 / 20 / 25 / 30 degrees; shift -0.6 / -0.2 / 0 / 0.4 / 1.0; tip radius 0 /
    0.25 / 0.38 mm; backlash 0 / 0.10 -- 4,200 combinations. For every curve the join is
    a crossing exactly when the test's xi, (m/sin(alpha))((z/2)sin^2(alpha) - (1.25 - x -
    rho*(1 - sin(alpha)))), is below -TROCHOID_JOIN_EPS * rb; outside that band
    `teeth < undercut_teeth(c)` says the same, and undercut_teeth equals the test's own
    onset to 1e-12 relative on every curve.

    Captured 2026-10-08 (Apple M2 Max, Python 3.12.13, 1-minute load 5 to 8): 3,657 valid
    gears, 543 refused by GearParams and skipped, 8 valid gears without a curve, 1,318
    crossings, 2,331 tangents, of which 2 sit inside the band (undercut by the closed
    form but too close to the double root to bracket, joined tangent by D-09), 0.23 s."""
    started = time.perf_counter()
    invalid = refused = crossing = tangent = in_band = 0
    for teeth in range(6, 41):
        for alpha in (14.5, 20.0, 25.0, 30.0):
            for shift in (-0.6, -0.2, 0.0, 0.4, 1.0):
                for rho in (0.0, 0.25, 0.38):
                    for backlash in (0.0, 0.10):
                        try:
                            p = _gear(teeth=teeth, module=1, pressure_angle=alpha,
                                      profile_shift=shift, backlash=backlash)
                        except ValidationError:
                            invalid += 1
                            continue
                        c = cutter(p, rho)
                        curve = trochoid_root(c)
                        if curve is None:
                            refused += 1
                            continue
                        sin_a = math.sin(math.radians(alpha))
                        xi = (1 / sin_a) * ((teeth / 2) * sin_a ** 2
                                            - (1.25 - shift - c.rho * (1 - sin_a)))
                        rb = teeth * math.cos(math.radians(alpha)) / 2
                        is_crossing = xi < -TROCHOID_JOIN_EPS * rb
                        assert (curve.join == "crossing") == is_crossing, (teeth, alpha, shift)
                        assert undercut_teeth(c) == pytest.approx(
                            _onset_teeth(1, alpha, shift, c.rho), rel=1e-12)
                        if xi < 0 and not is_crossing:
                            in_band += 1
                        else:
                            assert (teeth < undercut_teeth(c)) == is_crossing, (teeth, alpha)
                        crossing += is_crossing
                        tangent += not is_crossing
    elapsed = time.perf_counter() - started
    print(f"T1: {crossing + tangent + refused} gears, {invalid} refused by GearParams, "
          f"{refused} without a curve, {crossing} crossing, {tangent} tangent, "
          f"{in_band} inside the band, {elapsed:.2f} s")
    assert (invalid, refused, crossing, tangent, in_band) == (543, 8, 1318, 2331, 2)


def _on_the_double_root(xi_over_rb: float | None = None, *, xi_mm: float | None = None,
                        rho: float = 0.38) -> GearParams:
    """The 10-tooth, 20 degree, module 1, backlash 0 gear with its profile shift tuned so
    the cutter's xi reads `xi_over_rb * rb` (or `xi_mm`): xi is linear in the shift, so
    one cutter at shift 0 places the gear on its own z_min double root (STACK's gear)."""
    fields = {"teeth": 10, "module": 1, "pressure_angle": 20, "backlash": 0}
    base = _gear(profile_shift=0, **fields)
    target = xi_mm if xi_mm is not None else (xi_over_rb or 0.0) * profile(base).rb
    return _gear(profile_shift=tuned_shift(base, rho, target), **fields)


def test_the_double_root_at_z_min_is_a_tangent_join_one_tooth_step_either_side() -> None:
    """REQ-trochoid-root-generated, adjacency (D-09): 10 teeth, module 1, 30 degrees, no
    shift, no backlash, sharp cutter is exactly on z_min, 2 * 1.25 / sin^2(30) = 10, with
    a float xi of -8.9e-16 (measured 2026-10-08). The double root is a tangent join, not a
    refusal and not a failed bracket, and the oracle reads the curve as the cut boundary.
    One tooth step either side: 9 teeth are undercut by 0.25 mm of roll and cross; 11 are
    not and join tangent."""
    xi: dict[int, float] = {}
    joins: dict[int, str] = {}
    for teeth in (9, 10, 11):
        p = _gear(teeth=teeth, module=1, pressure_angle=30, profile_shift=0, backlash=0)
        c = cutter(p, 0.0)
        curve = trochoid_root(c)
        assert curve is not None
        assert root_mode(p, profile(p), requested="trochoid", rho=0.0).mode == "trochoid"
        xi[teeth], joins[teeth] = c.xi, curve.join
        if teeth == 10:
            assert abs(c.xi) < 1e-12
            swept = _swept(curve.points, p, c.rho)
            assert all(abs(v) <= ORACLE_BAR_MM for v in swept), max(swept)
    assert [joins[z] for z in (9, 10, 11)] == ["crossing", "tangent", "tangent"]
    assert xi[9] == pytest.approx(-0.25, abs=1e-12)
    assert xi[11] == pytest.approx(0.25, abs=1e-12)


def test_the_double_root_flips_one_field_step_either_side_of_a_tuned_shift() -> None:
    """D-09, boundary: the 10-tooth, 30 degree, sharp-cutter gear has x_min = 0 exactly
    (undercut_shift reads 0 to 1e-12), so the profile-shift field's own step (0.05) puts
    x -0.05 on the undercut side, xi -0.10 mm, a crossing, and x 0.05 on the other, xi
    +0.10 mm, a tangent join: the L33 pattern, one field step either side."""
    for x, join in ((-0.05, "crossing"), (0.05, "tangent")):
        p = _gear(teeth=10, module=1, pressure_angle=30, profile_shift=x, backlash=0)
        c = cutter(p, 0.0)
        assert abs(undercut_shift(c)) < 1e-12
        assert c.xi == pytest.approx(2 * x, abs=1e-12)
        curve = trochoid_root(c)
        assert curve is not None
        assert curve.join == join


def test_the_join_epsilon_separates_a_found_bracket_from_a_degenerate_one(
        monkeypatch: pytest.MonkeyPatch) -> None:
    """D-09, D-10: where the bracket works the answer is a crossing, inside the band the
    flank join is the form point, and where the bracket is lost outside the band the
    answer is a named refusal, never a number.

    STACK's two points on the 10-tooth, 20 degree gear (rb 4.698 mm): xi -2.9e-3 mm
    (bracket found) is a crossing, xi -2.9e-5 mm (bracket lost in the prototype) is inside
    the band (eps * rb = 4.7e-4 mm) and joins tangent. At xi = -10 * eps * rb the bracket
    is found and the last point is on Profile.half_angle to the junction bar; at xi =
    -eps * rb / 10 it is the flank join, sqrt(rb^2 + xi^2). Patching the constant to 0
    at xi = -1e-9 * rb loses the bracket (measured 2026-10-08, the scan of
    `bench/trochoid.py epsilon` loses it up to 5.6e-6 * rb), and root_mode names it. The
    sentence was captured from root_warnings on 2026-10-08, never typed (L33)."""
    for xi_mm, join in ((-2.9e-3, "crossing"), (-2.9e-5, "tangent")):
        p = _on_the_double_root(xi_mm=xi_mm)
        curve = trochoid_root(cutter(p, 0.38))
        assert curve is not None
        assert curve.join == join, xi_mm

    p = _on_the_double_root(-10 * TROCHOID_JOIN_EPS)
    c = cutter(p, 0.38)
    curve = trochoid_root(c)
    assert curve is not None
    assert curve.join == "crossing"
    radius, half = curve.points[-1]
    assert abs(half - c.pr.half_angle(radius)) <= JUNCTION_BAR_RAD

    p = _on_the_double_root(-TROCHOID_JOIN_EPS / 10)
    c = cutter(p, 0.38)
    curve = trochoid_root(c)
    assert curve is not None
    assert curve.join == "tangent"
    assert curve.points[-1][0] == pytest.approx(math.hypot(c.pr.rb, c.xi),
                                                abs=JUNCTION_BAR_MM)

    monkeypatch.setattr("spur.calc.TROCHOID_JOIN_EPS", 0.0)
    p = _on_the_double_root(-1e-9)
    c = cutter(p, 0.38)
    assert -1e-9 * 1.001 < c.xi / c.pr.rb < -1e-9 * 0.999
    assert trochoid_root(c) is None
    rm = root_mode(p, profile(p), requested="trochoid", rho=0.38)
    assert (rm.mode, rm.reason) == ("radial", "bracket degenerate")
    assert root_warnings(rm) == (
        "The trochoid root's junction with the involute could not be solved for this "
        "gear: the analytic root is used.",)


def test_every_structural_failure_is_refused_as_curve_invalid(
        monkeypatch: pytest.MonkeyPatch) -> None:
    """D-10, D-11, L08: a curve that is not a single honest graph over the radius is
    refused as `curve invalid`, with no points and no clipping to the centreline. Two
    ways in. (1) A gear outside the allowed box, built with `model_construct` (profile
    shift -1.0, which GearParams rejects): 6 teeth, 14.5 degrees, sharp cutter. Measured
    2026-10-08 it reaches the tip-circle arm: its radius rises and its half-angle stays
    inside the tooth space, but its last radius is 1.128 * ra, the 1.13 * ra 18-RESEARCH
    saw on the x = -1 rows. (2) A tangent gear whose point function is patched to a
    falling radius, the arm no gear reaches. That is two of the guard's four arms; the
    centreline arm is reached in `test_a_curve_that_cannot_be_trusted_is_refused_...` and
    the fourth, a point that is not inside the involute, in the next test. The sentence
    was captured from root_warnings on 2026-10-08, never typed (L33)."""
    sentence = ("The trochoid root for this gear loops, leaves the tooth space or runs past "
                "its junction with the involute: the analytic root is used.")
    outside = GearParams.model_construct(teeth=6, module=1.0, pressure_angle=14.5,
                                         profile_shift=-1.0, backlash=0.0)
    c = cutter(outside, 0.0)
    assert c.pr.rb > c.pr.rf  # past F9's nesting: the closed-form tests do not refuse it
    assert _root_curve(c) == "curve invalid"
    assert trochoid_root(c) is None
    rm = root_mode(outside, profile(outside), requested="trochoid", rho=0.0)
    assert (rm.mode, rm.reason) == ("radial", "curve invalid")
    assert root_warnings(rm) == (sentence,)

    tangent = _gear(teeth=30, module=1, pressure_angle=20, profile_shift=0, backlash=0)
    monkeypatch.setattr("spur.calc._trochoid_point",
                        lambda c, beta: (c.pr.ra - beta, 0.1))
    falling = cutter(tangent, 0.38)
    assert _root_curve(falling) == "curve invalid"
    rm = root_mode(tangent, profile(tangent), requested="trochoid", rho=0.38)
    assert (rm.mode, rm.reason) == ("radial", "curve invalid")
    assert root_warnings(rm) == (sentence,)


def test_a_crossing_curve_with_an_early_point_outside_the_involute_is_refused(
        monkeypatch: pytest.MonkeyPatch) -> None:
    """L08, 18-REVIEW WR-01: the fourth arm of the `curve invalid` guard is what stops a
    bisection that landed on a later root from shipping as a healed curve, and it is the
    one arm no gear reaches. On the tracer gear (10 teeth, crossing join, tip radius 0.38
    mm) every sample before the junction is under the base circle (the last one reads
    4.640 mm against rb 4.698 mm, measured 2026-10-08), so the arm cannot be reached by
    bending a half-angle alone. The last sample before the junction is moved to rb + 0.01
    mm, between its neighbours' radii so the radius still rises, with a half-angle 1e-3
    rad above the involute's at that radius: past the base circle and not inside the
    involute, a curve that has already crossed it and runs on.

    The patch must leave the junction solve alone, because `_junction` calls the same
    point function. So the real `_junction` is read first, and wrapped rather than
    replaced: it runs against the real point function and only then arms the bend, and
    the wrapper asserts it found the junction read beforehand. Exactly one sample is bent
    (the fifteenth call after arming, `_root_curve` samples in order), so an `all(...)` in
    place of the guard's `any(...)` is seen too. The other three arms stay quiet: the
    radius still rises and stays under the tip circle, and the half-angle (0.17 rad) is
    far inside the tooth space (pi/z = 0.31 rad). The sentence is the one captured above
    from root_warnings (L33). Seen red with the arm replaced by `False`: 18-06-SUMMARY."""
    sentence = ("The trochoid root for this gear loops, leaves the tooth space or runs past "
                "its junction with the involute: the analytic root is used.")
    p = _gear(teeth=10, module=1, pressure_angle=20, profile_shift=0, backlash=0)
    c = cutter(p, 0.38)
    found = _junction(c, TROCHOID_JOIN_EPS)
    assert found is not None
    assert found[1] == "crossing"
    honest = trochoid_root(c)
    assert honest is not None
    assert honest.points[-2][0] < c.pr.rb  # the premise: no early sample is past rb

    state = {"calls": -1, "bent": False}  # -1: not armed, the junction solve is running

    def junction_then_arm(cc: Cutter, eps: float) -> tuple[float, str] | None:
        state["calls"] = -1
        assert _junction(cc, eps) == found
        state["calls"], state["bent"] = 0, False
        return found

    def bent_last_early_sample(cc: Cutter, beta: float) -> tuple[float, float]:
        point = _trochoid_point(cc, beta)
        if state["calls"] < 0:
            return point
        state["calls"] += 1
        if state["calls"] != ROOT_CURVE_POINTS - 1:
            return point
        state["bent"] = True
        radius = cc.pr.rb + 0.01
        assert honest.points[-2][0] < radius < honest.points[-1][0]  # still rising
        return radius, cc.pr.half_angle(radius) + 1e-3

    monkeypatch.setattr("spur.calc._junction", junction_then_arm)
    monkeypatch.setattr("spur.calc._trochoid_point", bent_last_early_sample)
    assert _root_curve(c) == "curve invalid"
    assert state["bent"]  # the sample the arm refuses was reached, not skipped
    assert trochoid_root(c) is None
    rm = root_mode(p, profile(p), requested="trochoid", rho=0.38)
    assert (rm.mode, rm.reason) == ("radial", "curve invalid")
    assert root_warnings(rm) == (sentence,)


@pytest.mark.parametrize(("fields", "rho"), [
    pytest.param({"teeth": 10, "module": 1, "pressure_angle": 20, "profile_shift": 0,
                  "backlash": 0}, 0.38, id="crossing-10T"),
    pytest.param({"teeth": 30, "module": 1, "pressure_angle": 20, "profile_shift": 0,
                  "backlash": 0.10}, 0.38, id="tangent-30T"),
])
def test_a_root_curve_is_immutable_and_its_points_rise_from_the_root_circle(
        fields: dict[str, object], rho: float) -> None:
    """REQ-trochoid-root-generated, ordering and empty: a RootCurve is frozen with its
    points a tuple of tuples, exactly ROOT_CURVE_POINTS of them (never an empty curve),
    the first on the root circle bit for bit, the radius strictly rising so no two
    points share one. The mirrored flank and the other teeth are the consumer's
    (Phase 19). A refused cutter gives None, never an empty curve."""
    p = _gear(**fields)
    c = cutter(p, rho)
    curve = trochoid_root(c)
    assert curve is not None
    with pytest.raises(FrozenInstanceError):
        curve.points = ()  # type: ignore[misc]
    assert isinstance(curve.points, tuple)
    assert all(type(point) is tuple and len(point) == 2 for point in curve.points)
    assert len(curve.points) == ROOT_CURVE_POINTS
    assert curve.points[0][0] == c.pr.rf
    radii = [radius for radius, _ in curve.points]
    assert all(lo < hi for lo, hi in pairwise(radii))
    assert len(set(radii)) == ROOT_CURVE_POINTS

    no_land = cutter(_gear(teeth=12, module=1, pressure_angle=33.5, profile_shift=0,
                           backlash=0), 0.0)
    assert trochoid_root(no_land) is None


@pytest.mark.parametrize(("fields", "rho"), [
    pytest.param({"teeth": 10, "module": 1, "pressure_angle": 20, "profile_shift": 0,
                  "backlash": 0}, 0.38, id="tracer"),
    pytest.param({"teeth": 17, "module": 1, "pressure_angle": 20, "profile_shift": 0,
                  "backlash": 0}, 0.38, id="just-undercut-17T"),
    pytest.param({"teeth": 6, "module": 1, "pressure_angle": 14.5, "profile_shift": -0.6,
                  "backlash": 0}, 3.0, id="6T-14.5-x-0.6-cap-request"),
])
def test_profile_half_angle_is_never_asked_below_the_base_circle(
        monkeypatch: pytest.MonkeyPatch, fields: dict[str, object], rho: float) -> None:
    """The junction code calls Profile.half_angle only at R >= rb: below the base circle
    `min(1.0, rb/R)` would clamp and quietly return the wrong involute (18-RESEARCH). A
    spy over three crossing gears, the 6-tooth one asked for the cap (3.0 mm, trimmed),
    records every radius it is asked and none is under rb * (1 - 1e-15), the last-ulp
    excursion the clamp is there to absorb. The assertion is the smallest radius, not a
    call count."""
    asked: list[float] = []
    original = Profile.half_angle

    def spy(self: Profile, radius: float) -> float:
        asked.append(radius / self.rb)
        return original(self, radius)

    monkeypatch.setattr(Profile, "half_angle", spy)
    p = _gear(**fields)
    c = cutter(p, rho)
    junction = _junction(c, TROCHOID_JOIN_EPS)
    assert junction is not None
    assert junction[1] == "crossing"
    _root_curve(c)
    assert asked
    assert min(asked) >= 1 - 1e-15


@pytest.mark.parametrize("teeth", [
    pytest.param(10, id="crossing-10T"),
    pytest.param(8, id="crossing-8T"),
    pytest.param(35, id="tangent-35T"),
])
def test_the_form_radius_does_not_depend_on_backlash(teeth: int) -> None:
    """The radius where the root hands over to the involute depends on the rack and the
    tooth count, not on how thick the tooth is cut: Zhang, "Tooth thickness is not needed
    in either method A or B", and 18-RESEARCH's measured spread over backlash 0, 0.05,
    0.1 and 0.3 at fixed x of 1.8e-15 mm (10 teeth), 0 (8) and 0 (35). The cutter widens
    by the backlash (D-07) but its flank foot does not move. Re-measured 2026-10-08 at
    1.8e-15, 0 and 0 mm on 20 degrees and tip radius 0.38 mm."""
    last = []
    for backlash in (0.0, 0.05, 0.10, 0.30):
        p = _gear(teeth=teeth, module=1, pressure_angle=20, profile_shift=0,
                  backlash=backlash)
        curve = trochoid_root(cutter(p, 0.38))
        assert curve is not None
        last.append(curve.points[-1][0])
    assert max(last) - min(last) <= 1e-12


# --- T2: the swept-cutter oracle at the gate (18-04) ---------------------------------------
# (fields, tip radius requested in mm, the join, whether the cutter trims it). Twelve
# gears: crossing and tangent; tip radius 0, w_c == 0 (tip radius = tip depth), w_c > 0 and
# a tip land nearly gone; module 0.2, 1, 1.75 and 10; backlash 0 to 1.0. The bore is off.
GATE_ROWS = [
    pytest.param({"teeth": 10, "module": 1, "pressure_angle": 20, "profile_shift": 0,
                  "backlash": 0}, 0.38, "crossing", False, id="tracer-crossing"),
    pytest.param({"teeth": 19, "module": 1.75, "pressure_angle": 25, "profile_shift": 0,
                  "backlash": 0.10}, 0.5, "tangent", False, id="default-gear-tangent"),
    pytest.param({"teeth": 17, "module": 1, "pressure_angle": 20, "profile_shift": 0,
                  "backlash": 0}, 0.38, "crossing", False, id="17-teeth-just-undercut"),
    pytest.param({"teeth": 18, "module": 1, "pressure_angle": 20, "profile_shift": 0,
                  "backlash": 0}, 0.38, "tangent", False, id="18-teeth-just-not-undercut"),
    pytest.param({"teeth": 7, "module": 1, "pressure_angle": 14.5, "profile_shift": -0.6,
                  "backlash": 0}, 0.0, "crossing", False, id="thin-positive-waist-sharp"),
    pytest.param({"teeth": 6, "module": 1, "pressure_angle": 14.5, "profile_shift": -0.6,
                  "backlash": 0}, 3.0, "crossing", True, id="6-teeth-cap-request-3.0"),
    pytest.param({"teeth": 16, "module": 1, "pressure_angle": 14.5, "profile_shift": 1.0,
                  "backlash": 0}, 0.25, "tangent", False, id="w_c-equals-zero"),
    pytest.param({"teeth": 16, "module": 1, "pressure_angle": 14.5, "profile_shift": 1.0,
                  "backlash": 0}, 0.5, "tangent", False, id="w_c-above-zero"),
    pytest.param({"teeth": 12, "module": 1, "pressure_angle": 32.0, "profile_shift": 0,
                  "backlash": 0}, 3.0, "tangent", True, id="tip-land-nearly-gone"),
    pytest.param({"teeth": 10, "module": 0.2, "pressure_angle": 20, "profile_shift": 0,
                  "backlash": 0}, 0.05, "crossing", False, id="tracer-at-module-0.2"),
    pytest.param({"teeth": 12, "module": 10, "pressure_angle": 25, "profile_shift": 0.2,
                  "backlash": 1.0}, 0.5, "tangent", False, id="module-10-backlash-1.0"),
    pytest.param({"teeth": 30, "module": 1, "pressure_angle": 20, "profile_shift": 0,
                  "backlash": 0.10}, 0.38, "tangent", False, id="30-teeth-tangent"),
]


@pytest.mark.parametrize(("fields", "rho", "join", "trimmed"), GATE_ROWS)
def test_t2_the_oracle_reads_every_gate_row_as_the_cut_boundary(
        fields: dict[str, object], rho: float, join: str, trimmed: bool) -> None:
    """REQ-trochoid-proved-independently, T2 (SC3): the stdlib swept-cutter oracle, with
    its neighbouring cutter teeth and no code shared with calc, reads every point of the
    generator's curve as the boundary the hob cuts, within ORACLE_BAR_MM, on twelve gears
    chosen to cover crossing and tangent, rho 0 / w_c == 0 / w_c > 0 / a tip land nearly
    gone, module 0.2 to 10 and backlash 0 to 1.0. Measured 2026-10-08 (Apple M2 Max,
    Python 3.12.13): the worst reading over the twelve rows is 9.8e-15 mm (module 10,
    9.8e-16 per module), 1.0e5 times under the bar; the other eleven read 1.9e-16 to
    2.7e-15 mm. The row asserts its curve has 16 points before it reads one, and the
    oracle judges each point on its own, so the reversed curve reads the reversed
    readings, exactly."""
    p = _gear(**fields)
    c = cutter(p, rho)
    curve = trochoid_root(c)
    assert curve is not None
    assert len(curve.points) == ROOT_CURVE_POINTS == 16
    assert curve.join == join
    assert (c.rho < c.rho_requested) is trimmed
    readings = _swept(curve.points, p, c.rho)
    worst = max(abs(v) for v in readings)
    print(f"worst oracle reading: {worst:.3e} mm = {worst / p.module:.3e} per module")
    assert worst <= ORACLE_BAR_MM
    assert _swept(curve.points[::-1], p, c.rho) == readings[::-1]


def test_t2_the_oracle_sees_a_gouge_where_one_exists() -> None:
    """REQ-trochoid-proved-independently, T2's negative controls: an oracle that reads
    zero everywhere proves nothing, so three curves that must not read zero. Measured
    2026-10-08, module 1, backlash 0:

    1. The tracer gear's involute between the base circle (4.6985 mm) and the crossing
       radius (4.7256 mm), a quarter, half and three quarters of the way: -5.3e-3,
       -3.7e-3 and -1.9e-3 mm. The involute runs through material the hob removes there.
    2. The tracer's trochoid carried past its crossing, to a quarter, half and all of the
       way to the flank foot: -9.6e-3, -2.2e-2 and -5.19e-2 mm (18-RESEARCH: 5.19e-2 at
       the foot), the penetration a curve left running past the form point would have.
    3. A severed tooth (6 teeth, 14.5 degrees, x -0.6, sharp cutter): trochoid_root is
       None, and its one-flank points read -0.141352 mm at the waist with the neighbouring
       cutter teeth on and 2e-15 mm with them off -- the next space's cutter is what cuts
       this tooth through, so a single-tooth oracle cannot see it. This is the separation
       18-RESEARCH described (0.141 mm on its 21-point set); 18-02 could not reproduce it on
       an oracle whose roll window was +-1 span, and 18-04 widened the window to +-3 spans
       (see tests/trochoid_oracle.py). The tooth's mirror flank reads -0.141352 mm either way.
    """
    p = _gear(teeth=10, module=1, pressure_angle=20, profile_shift=0, backlash=0)
    c = cutter(p, 0.38)
    curve = trochoid_root(c)
    assert curve is not None
    for share in (0.25, 0.5, 0.75):
        radius = c.pr.rb + share * (curve.points[-1][0] - c.pr.rb)
        reading = _swept(((radius, _involute_half_angle(p, radius)),), p, c.rho)[0]
        print(f"involute at {share} of the way to the crossing: {reading:.3e} mm")
        assert reading < -1e-4

    junction = _junction(c, TROCHOID_JOIN_EPS)
    assert junction is not None
    beta_end = math.pi / 2 - c.pr.alpha
    for share in (0.25, 0.5, 1.0):
        point = _trochoid_point(c, junction[0] + share * (beta_end - junction[0]))
        reading = _swept((point,), p, c.rho)[0]
        print(f"trochoid {share} of the way from the crossing to the foot: {reading:.3e} mm")
        assert reading < -1e-4

    severed = _gear(teeth=6, module=1, pressure_angle=14.5, profile_shift=-0.6, backlash=0)
    sc = cutter(severed, 0.0)
    assert trochoid_root(sc) is None
    betas, samples = _flank_samples(sc)
    both = (*samples, _waist(sc, betas, samples))
    mirror = tuple((radius, -half) for radius, half in both)
    on = _swept(both, severed, 0.0)
    off = _swept(both, severed, 0.0, neighbours=False)
    other = _swept(mirror, severed, 0.0)
    print(f"severed, one flank: neighbours on {min(on):.6f}, off {min(off):.3e} mm; "
          f"mirror flank on {min(other):.6f} mm")
    assert min(on) < -1e-3
    assert all(abs(v) <= ORACLE_BAR_MM for v in off)
    assert min(other) < -1e-3


def test_t2_moving_rho_by_1e_6_mm_breaks_the_oracle_bar() -> None:
    """REQ-trochoid-proved-independently, T2's tripwire (SC3): the tracer gear's curve
    generated at tip radius 0.38 mm + 1e-6 mm and judged against the cutter at 0.38 mm
    must read beyond the bar, or the bar would pass a generator that mis-sets rho by a
    millionth of a millimetre. Measured 2026-10-08: the worst reading moves 0.2205 per mm
    of rho (2.2e-10 at 1e-9, 2.2e-8 at 1e-7, 2.2e-7 at 1e-6, 2.2e-5 at 1e-4 mm), so 1e-6
    reads 2.20e-7 mm, 220 times ORACLE_BAR_MM, against 1.0e-15 mm unmoved. 18-RESEARCH
    predicted 2.2e-7 and 220x."""
    p = _gear(teeth=10, module=1, pressure_angle=20, profile_shift=0, backlash=0)
    moved = trochoid_root(cutter(p, 0.38 + 1e-6))
    assert moved is not None
    reading = max(abs(v) for v in _swept(moved.points, p, 0.38))
    print(f"tripwire reading: {reading:.3e} mm = {reading / ORACLE_BAR_MM:.0f} x the bar")
    assert reading > 10 * ORACLE_BAR_MM


def test_t2_the_bench_oracle_uses_the_gate_s_bar() -> None:
    """The whole-product run in bench/trochoid.py judges against its own copy of the bar
    (the bench cannot import this module); one number, pinned equal here."""
    assert ORACLE_BAR_MM == BENCH_ORACLE_BAR_MM


# --- T3: freecad.gears at a sharp cutter, recorded once (18-04) -----------------------------
# PROVENANCE. Source: https://github.com/looooo/freecad.gears, file pygears/involute_tooth.py,
# class InvoluteTooth, method undercut_points (with pygears/__init__.py and
# pygears/_functions.py, which it imports), at commit 4cc4b1a233c232e15c3fdfb8a35909aa0d828796
# (2026-09-15, "ruff refactoring", the last commit touching involute_tooth.py); the
# repository HEAD that day was 83ec154b1925347622b61812f75d2ed51e956b9f; package version
# 1.4.0; licence GPL-3.0 (GitHub's licence API says spdx_id GPL-3.0, the file header carries
# the GPL v3 notice). The code is NEVER imported, vendored or copied into this repository: the
# three files were fetched with `gh api` into a scratch directory outside it, run once on
# 2026-10-08 by a script that imports nothing from spur (`python -I run.py <dir>`, numpy only,
# from this project's .venv), and what is recorded below is the numbers it printed.
#
# What was printed. InvoluteTooth(m=1, num_teeth=z, pressure_angle=radians(20),
# clearance=0.25, shift=x, backlash=bl, undercut=True).undercut_points(num=200), for teeth
# 8, 10, 14, shift 0 and 0.3, backlash 0 and 0.10. Their clearance 0.25 and shift x give the
# root circle r - (1.25 - x) m, this project's; their curve is R = (df/2) / cos(psi) at
# polar angle psi - (df/dw) tan(psi) rotated by -undercut_rot - pi/z + backlash/(2 r). Each
# row is (teeth, shift, backlash, psi, radius, half-angle from the tooth centre): psi is the
# sample parameter the library itself steps (numpy.linspace(0, undercut_end, 200)), radius
# is the hypot of its returned point and the half-angle is minus the polar angle of that
# point (checked by hand: at psi = 0 it equals this project's pi/z - a/r). Five points per
# case, evenly spread over the samples that lie on the cutter flank (contact-normal angle
# at most pi/2 - alpha), root circle to flank foot. psi is not recovered from the radius as
# acos((df/2)/R): that inverse turns a rounding error of 1e-16 in R into 1.5e-8 rad at the
# first point.
#
# The mapping to this project is tan(psi) = (d/rf) * tan(beta) with d the cutter's tip depth
# and rf the root radius, so beta = atan((rf/d) * tan(psi)) and the point is
# _trochoid_point(cutter(p, 0.0), beta), compared row by row through its own psi, never by
# list index or sorted order.
#
# What T3 checks: the rolling convention, the depth, the tip land and the way backlash
# enters, for a sharp corner, against someone else's code. What it does not: the crossing
# (the library trims polylines), the junction, or a tip radius above zero (T2 and T4 do).
# The reference prints no resolution (float64 closed-form arithmetic on both sides), so
# the bars below rest on the measured gap and the cross-platform libm floor.
FREECAD_T3_POINTS: tuple[tuple[int, float, float, float, float, float], ...] = (
    (8, 0.0, 0.0, 0.0, 2.75, 0.3100902390575503),
    (8, 0.0, 0.0, 0.2098403654332923, 2.8116764289774343, 0.246670573421815),
    (8, 0.0, 0.0, 0.4196807308665846, 3.0113256095251284, 0.19716490001214956),
    (8, 0.0, 0.0, 0.6253242889912111, 3.391823432030306, 0.1811255849374326),
    (8, 0.0, 0.0, 0.8351646544245034, 4.0980209914101735, 0.2345009613254471),
    (8, 0.0, 0.1, 0.0, 2.7500000000000004, 0.2975902390575503),
    (8, 0.0, 0.1, 0.2098403654332923, 2.811676428977435, 0.2341705734218149),
    (8, 0.0, 0.1, 0.4196807308665846, 3.011325609525129, 0.1846649000121495),
    (8, 0.0, 0.1, 0.6253242889912111, 3.391823432030306, 0.16862558493743257),
    (8, 0.0, 0.1, 0.8351646544245034, 4.098020991410174, 0.22200096132544703),
    (8, 0.3, 0.0, 0.0, 3.0499999999999994, 0.31009023905755034),
    (8, 0.3, 0.0, 0.1767152406093852, 3.09825075327098, 0.2695407361871882),
    (8, 0.3, 0.0, 0.3534304812187704, 3.250937580256842, 0.23796199195786447),
    (8, 0.3, 0.0, 0.5301457218281557, 3.535275231974632, 0.22685550989273337),
    (8, 0.3, 0.0, 0.7068609624375408, 4.011024309287729, 0.2544692482173224),
    (8, 0.3, 0.1, 0.0, 3.05, 0.2975902390575503),
    (8, 0.3, 0.1, 0.1767152406093852, 3.09825075327098, 0.2570407361871882),
    (8, 0.3, 0.1, 0.3534304812187704, 3.2509375802568417, 0.22546199195786448),
    (8, 0.3, 0.1, 0.5301457218281557, 3.5352752319746323, 0.21435550989273333),
    (8, 0.3, 0.1, 0.7068609624375408, 4.011024309287729, 0.24196924821732238),
    (10, 0.0, 0.0, 0.0, 3.75, 0.24807219124604024),
    (10, 0.0, 0.0, 0.1843686595004552, 3.814649972004874, 0.20356838207143169),
    (10, 0.0, 0.0, 0.3687373190009104, 4.020226748415705, 0.16914329922247723),
    (10, 0.0, 0.0, 0.5570287159375454, 4.417847438515955, 0.15815699427372432),
    (10, 0.0, 0.0, 0.7413973754380007, 5.084569235553447, 0.1934162318049653),
    (10, 0.0, 0.1, 0.0, 3.7500000000000004, 0.2380721912460402),
    (10, 0.0, 0.1, 0.1843686595004552, 3.8146499720048745, 0.1935683820714316),
    (10, 0.0, 0.1, 0.3687373190009104, 4.020226748415704, 0.15914329922247722),
    (10, 0.0, 0.1, 0.5570287159375454, 4.417847438515956, 0.14815699427372428),
    (10, 0.0, 0.1, 0.7413973754380007, 5.084569235553446, 0.1834162318049653),
    (10, 0.3, 0.0, 0.0, 4.05, 0.24807219124604024),
    (10, 0.3, 0.0, 0.14241952473304145, 4.091423741949353, 0.22179882205623688),
    (10, 0.3, 0.0, 0.2848390494660829, 4.220038462719063, 0.200401826629224),
    (10, 0.3, 0.0, 0.4272585741991244, 4.450035236794679, 0.1896124027669495),
    (10, 0.3, 0.0, 0.5696780989321658, 4.809549901149882, 0.19721083266255793),
    (10, 0.3, 0.1, 0.0, 4.05, 0.23807219124604023),
    (10, 0.3, 0.1, 0.14241952473304145, 4.091423741949353, 0.2117988220562369),
    (10, 0.3, 0.1, 0.2848390494660829, 4.220038462719063, 0.190401826629224),
    (10, 0.3, 0.1, 0.4272585741991244, 4.45003523679468, 0.1796124027669494),
    (10, 0.3, 0.1, 0.5696780989321658, 4.809549901149882, 0.18721083266255792),
    (14, 0.0, 0.0, 0.0, 5.75, 0.17719442231860014),
    (14, 0.0, 0.0, 0.1327648598506447, 5.801051082864395, 0.15413172567492733),
    (14, 0.0, 0.0, 0.2690235318026222, 5.964539155334789, 0.13464462803571756),
    (14, 0.0, 0.0, 0.40528220375459967, 6.256861008576025, 0.124332702594173),
    (14, 0.0, 0.0, 0.5380470636052443, 6.69608191415659, 0.1293579132482911),
    (14, 0.0, 0.1, 0.0, 5.75, 0.170051565175743),
    (14, 0.0, 0.1, 0.1327648598506447, 5.801051082864395, 0.14698886853207016),
    (14, 0.0, 0.1, 0.2690235318026222, 5.96453915533479, 0.12750177089286044),
    (14, 0.0, 0.1, 0.40528220375459967, 6.256861008576025, 0.11718984545131583),
    (14, 0.0, 0.1, 0.5380470636052443, 6.69608191415659, 0.12221505610543397),
    (14, 0.3, 0.0, 0.0, 6.05, 0.17719442231860016),
    (14, 0.3, 0.0, 0.10320655828775342, 6.082364695383163, 0.1635058804187843),
    (14, 0.3, 0.0, 0.20297289796591506, 6.176799665447667, 0.15209754785279694),
    (14, 0.3, 0.0, 0.30273923764407673, 6.338241642358868, 0.1444063184585221),
    (14, 0.3, 0.0, 0.4059457959318301, 6.585182204048351, 0.14273556302404264),
    (14, 0.3, 0.1, 0.0, 6.05, 0.17005156517574302),
    (14, 0.3, 0.1, 0.10320655828775342, 6.082364695383163, 0.1563630232759271),
    (14, 0.3, 0.1, 0.20297289796591506, 6.176799665447667, 0.1449546907099398),
    (14, 0.3, 0.1, 0.30273923764407673, 6.338241642358869, 0.13726346131566494),
    (14, 0.3, 0.1, 0.4059457959318301, 6.585182204048351, 0.13559270588118552),
)

# mm and rad. Measured 2026-10-08 (Apple M2 Max, Python 3.12.13) over the 60 rows below:
# the largest radius gap is 1.78e-15 mm and the largest half-angle gap 1.94e-16 rad (the
# first prototype read 2.66e-15 and 3.05e-16 over 1,972 points). Ten times the larger is
# 1.8e-14, under the 1e-12 floor this phase uses for libm differences between this host
# (macOS arm64) and CI (ubuntu), so both bars are 1e-12: headroom 560 on the radius and
# 5.1e3 on the angle. The reference prints no resolution; both sides are float64.
T3_BAR_MM = 1e-12
T3_BAR_RAD = 1e-12


def _t3_gaps(rho: float) -> tuple[float, float]:
    """The largest radius gap (mm) and half-angle gap (rad) between the recorded freecad.gears
    points and this project's cutter of tip radius `rho`, each row matched through its psi."""
    worst_radius = worst_angle = 0.0
    for teeth, shift, backlash, psi, radius, half in FREECAD_T3_POINTS:
        p = _gear(teeth=teeth, module=1, pressure_angle=20, profile_shift=shift,
                  backlash=backlash)
        c = cutter(p, rho)
        beta = math.atan((c.pr.rf / c.d) * math.tan(psi))
        ours = _trochoid_point(c, beta)
        worst_radius = max(worst_radius, abs(ours[0] - radius))
        worst_angle = max(worst_angle, abs(ours[1] - half))
    return worst_radius, worst_angle


def test_t3_the_sharp_cutter_matches_freecad_gears_point_for_point() -> None:
    """REQ-trochoid-proved-independently, T3 (SC3): at a tip radius of 0, the generator's
    envelope is the freecad.gears undercut curve, point for point, on twelve gears (teeth 8,
    10, 14; shift 0, 0.3; backlash 0, 0.10; module 1, 20 degrees), five points each. This
    is the empty-tip-radius case: no rounded corner, so the whole curve is the sharp
    corner's trochoid. Measured 2026-10-08: 1.78e-15 mm and 1.94e-16 rad, bars 1e-12."""
    assert len(FREECAD_T3_POINTS) == 60
    cases = {row[:3] for row in FREECAD_T3_POINTS}
    assert len(cases) == 12
    assert all(sum(row[:3] == case for row in FREECAD_T3_POINTS) == 5 for case in cases)
    gap_mm, gap_rad = _t3_gaps(0.0)
    print(f"T3 gaps: {gap_mm:.3e} mm, {gap_rad:.3e} rad")
    assert gap_mm <= T3_BAR_MM
    assert gap_rad <= T3_BAR_RAD


def test_t3_a_1e_6_mm_tip_radius_breaks_the_freecad_bar() -> None:
    """The T3 tripwire: the same rows against a cutter of tip radius 1e-6 mm, a millionth
    of a millimetre of rounding, must read above both bars -- or the bars would pass a
    generator that rounds the corner. Measured 2026-10-08: the radius gap moves from 1.8e-15 to
    7.35e-7 mm (7.4e5 times the bar) and the half-angle gap from 1.9e-16 to 1.75e-7 rad (1.8e5
    times)."""
    gap_mm, gap_rad = _t3_gaps(1e-6)
    print(f"T3 tripwire gaps: {gap_mm:.3e} mm = {gap_mm / T3_BAR_MM:.1e} x the bar, "
          f"{gap_rad:.3e} rad = {gap_rad / T3_BAR_RAD:.1e} x the bar")
    assert gap_mm > T3_BAR_MM
    assert gap_rad > T3_BAR_RAD


# --- T4: the KISSsoft form diameter, one published number (D-15, 18-04) ---------------------
# Zhang, S., "Methods to Determine Form Diameter on Hobbed External Involute Gears", AGMA
# 18FTM02 (September 2018), Table 7 example 7, reproduced by Gear Solutions
# (https://gearsolutions.com/features/methods-to-determine-form-diameter-on-hobbed-external-involute-gears/)
# "with AGMA's permission"; one number is recorded here as a fact, with attribution, and
# nothing is fetched at test time. The example: 35 teeth, pressure angle 22.5 degrees, dedendum
# factor 1.3, hob without protuberance (delta0 = 0), hob tip radius 0.04, and the form diameter
# KISSsoft prints, 4.1530, to four decimals.
#
# INFERRED, not printed: the table gives no module or diametral pitch. The printed tooth
# count, angle, dedendum factor and tip radius reproduce 4.1530 +- 5e-5 only at a diametral
# pitch of 8 (module 25.4/8 = 3.175 mm) to within 1e-4, a relative 1.2e-5 -- and 8 is the
# round number in that window (18-RESEARCH A1; the last test below checks that 7.999 and
# 8.001 miss). The dedendum factor 1.3 is read as (r - rf)/m, so with this project's
# 1.25 m rack the profile shift is 1.25 - 1.3 = -0.05 (A2). Both readings are of a table
# image, and D-15 adopted the number knowing it.
#
# The junction compared is the cutter-envelope junction: where the generated root curve hands
# over to the involute (Zhang's definition, "the diameter of a circle at which the root fillet
# curve intersects or joins the involute"). One tool-generated number is not ISO 21771
# parity and is never called that (D-08, D-15, L08).
ZHANG_T4 = {
    "teeth": 35.0, "pressure_angle": 22.5, "dedendum_factor": 1.3, "protuberance": 0.0,
    "tip_radius_in": 0.04, "kisssoft_form_diameter_in": 4.1530, "diametral_pitch": 8.0,
}
# inches. Half of the last printed digit of 4.1530. The observed gap is 3.59e-5 in
# (4.153036 against 4.1530), so the headroom is 1.39: under the 10x rule by construction,
# because the reference is rounded to 4 decimals, not because the bar was tuned. The human
# accepted exactly this at planning (D-15); it is not escalated again. The tripwire below is
# what keeps it from passing anything.
T4_BAR_IN = 5e-5


def _zhang_form_diameter_in(diametral_pitch: float, tip_radius_in: float) -> float:
    """The tangent junction's diameter, inches, for the Table 7 example 7 gear. The curve
    comes from trochoid_root(cutter(p, rho)) directly: this gear has rb - rf of -0.102 mm,
    so root_mode would hand it back as `nothing radial to replace`; the junction is still
    tangent (xi 12.1 mm)."""
    module = 25.4 / diametral_pitch
    p = _gear(teeth=int(ZHANG_T4["teeth"]), module=module,
              pressure_angle=ZHANG_T4["pressure_angle"],
              profile_shift=round(1.25 - ZHANG_T4["dedendum_factor"], 6), backlash=0)
    curve = trochoid_root(cutter(p, tip_radius_in * 25.4))
    assert curve is not None
    assert curve.join == "tangent"
    return 2 * curve.points[-1][0] / 25.4


def test_t4_the_tangent_junction_matches_kisssoft_s_form_diameter() -> None:
    """REQ-trochoid-proved-independently, T4 (D-15): the cutter-envelope junction of the
    Zhang Table 7 example 7 gear, module 3.175 mm, tip radius 1.016 mm, backlash 0, is
    4.153036 in against KISSsoft's 4.1530: a gap of 3.59e-5 in, 0.72 of the bar of half the
    last printed digit, headroom 1.39 (accepted, D-15). It anchors the tangent branch only,
    and it is the cutter-envelope junction, not an ISO 21771 form diameter."""
    ours = _zhang_form_diameter_in(ZHANG_T4["diametral_pitch"], ZHANG_T4["tip_radius_in"])
    gap = abs(ours - ZHANG_T4["kisssoft_form_diameter_in"])
    print(f"T4: {ours:.6f} in against {ZHANG_T4['kisssoft_form_diameter_in']}: gap {gap:.3e} in "
          f"= {gap / T4_BAR_IN:.2f} of the bar, headroom {T4_BAR_IN / gap:.2f}x")
    assert gap <= T4_BAR_IN


def test_t4_a_1e_3_in_tip_radius_moves_the_form_diameter_past_the_bar() -> None:
    """The T4 tripwire and the inference check. A tip radius 1e-3 in larger moves the form
    diameter by 7.78e-4 in (0.78 per unit of tip radius over that step; 18-RESEARCH's
    derivative at the point is 0.742), 15.6 times the bar; and the two pitches either side
    of the inferred 8 (7.999 and 8.001) miss 4.1530 by 5.5e-4 and 4.8e-4 in, 11.0 and 9.6
    times the bar, so the pitch that reproduces it is 8 to within 1e-4. Measured
    2026-10-08."""
    pitch, rho = ZHANG_T4["diametral_pitch"], ZHANG_T4["tip_radius_in"]
    moved = abs(_zhang_form_diameter_in(pitch, rho + 1e-3)
                - ZHANG_T4["kisssoft_form_diameter_in"])
    print(f"T4 tripwire: {moved:.3e} in = {moved / T4_BAR_IN:.1f} x the bar")
    assert moved > 10 * T4_BAR_IN
    for neighbour in (pitch - 0.001, pitch + 0.001):
        miss = abs(_zhang_form_diameter_in(neighbour, rho) - ZHANG_T4["kisssoft_form_diameter_in"])
        print(f"T4 pitch {neighbour}: misses by {miss:.3e} in = {miss / T4_BAR_IN:.1f} x the bar")
        assert miss > T4_BAR_IN


def _hob(**fields: object) -> GearParams:
    """A gear asked for the hob-cut root: `_gear` with root_shape set."""
    return _gear(root_shape="trochoid", **fields)


def _undercut_sentences(p: GearParams) -> list[str]:
    return [w for w in derive(p).warnings if "undercut" in w]


def test_the_restated_undercut_sentence_fires_at_17_teeth_and_not_18() -> None:
    """REQ-undercut-warning-restated, adjacency: one tooth step either side of the cutter's
    onset at module 1, 20 degrees, no shift, tip radius 0.38 mm. 17 teeth cross the
    involute (the hob undercuts them) and print one sentence with the onset rounded up to
    0.1 teeth (17.0967 -> 17.1) and the smallest avoiding shift rounded up to 0.001
    (0.00566 -> 0.006), and no radial-root wording; 18 teeth join tangent and print none. A
    gear nobody asked about still prints the shipped sentence (17 teeth, below its 17.1),
    and a tangent join prints no undercut sentence at all. Captured from derive() on
    2026-10-09 (L33)."""
    sentence = ("Below 17.1 teeth this cutter undercuts the gear, and the root is cut the way "
                "the hob cuts it; a profile shift of 0.006 or more avoids the undercut.")
    fields = {"module": 1, "pressure_angle": 20, "profile_shift": 0, "root_fillet": 0.38}
    assert _undercut_sentences(_hob(teeth=17, **fields)) == [sentence]
    assert _undercut_sentences(_hob(teeth=18, **fields)) == []
    assert "radial" not in sentence
    assert _undercut_sentences(_gear(teeth=17, **fields)) == [
        "Below 17.1 teeth a cut gear would be undercut; this model uses a radial root instead."]
    assert _undercut_sentences(_gear(teeth=18, **fields)) == []

    # The two lines disagree away from this gear, and the join decides (PITFALLS 1): a
    # sharp cutter undercuts 18 teeth (onset 21.4) where the shipped line calls it clear;
    # at 14.5 degrees (default backlash, tip radius 0.38 mm) 31 teeth are undercut by the
    # shipped line (31.9) and clear of the cutter's (30.79), and 30 are undercut by both.
    sharp = _undercut_sentences(_hob(teeth=18, module=1, pressure_angle=20, profile_shift=0,
                                     root_fillet=0))
    assert [s.startswith("Below 21.4 teeth this cutter") and s.endswith("0.198 or more "
            "avoids the undercut.") for s in sharp] == [True]
    shallow = {"module": 1, "pressure_angle": 14.5, "profile_shift": 0, "root_fillet": 0.38}
    assert _undercut_sentences(_hob(teeth=31, **shallow)) == []
    assert _undercut_sentences(_gear(teeth=31, **shallow)) == [
        "Below 31.9 teeth a cut gear would be undercut; this model uses a radial root instead."]
    assert [s.startswith("Below 30.8 teeth this cutter") for s in
            _undercut_sentences(_hob(teeth=30, **shallow))] == [True]


def test_the_advised_shift_is_rounded_up_and_flips_the_gear_out_of_undercut() -> None:
    """REQ-undercut-warning-restated, precision (F9; T-19-12): at 10 teeth, module 1, 20
    degrees, backlash 0, tip radius 0.38 mm the shift that avoids undercut is 0.41508.
    Rounded to nearest it would print 0.415, where the cutter's roll is still -7.9e-5 mm;
    the sentence prints 0.416, where it is +2.7e-3 mm. So the advice is read from the
    cutter's own xi one step either side, never from the join (0.415 sits inside the
    1e-4 rb join band and reads tangent). The 17-tooth row (0.00566 -> 0.006) flips the
    same way. A bound that is an exact multiple of its step must not climb one: the
    residue is removed before the ceiling, so 0.416 plus 1e-13 still prints 0.416.
    Reproduced 2026-10-09."""
    base = {"module": 1, "pressure_angle": 20, "root_fillet": 0.38}
    for teeth, backlash, printed in [(10, 0, 0.416), (17, 0.10, 0.006)]:
        fields = {"teeth": teeth, "backlash": backlash, **base}
        sentence = f"a profile shift of {printed:.3f} or more avoids the undercut."
        assert [s.endswith(sentence) for s in _undercut_sentences(
            _hob(profile_shift=0, **fields))] == [True]
        step = 0.001
        assert cutter(_gear(profile_shift=printed, **fields), 0.38).xi >= 0
        assert cutter(_gear(profile_shift=round(printed - step, 3), **fields), 0.38).xi < 0

    c = cutter(_gear(teeth=10, backlash=0, profile_shift=0, **base), 0.38)
    assert undercut_shift(c) == pytest.approx(0.41508, abs=5e-6)
    assert round(undercut_shift(c), 3) == 0.415      # nearest is the false answer
    on_the_step = replace(c, x=0.416, xi=0.0)
    off_by_residue = replace(c, x=0.416, xi=-1e-13 * c.pr.m / math.sin(c.pr.alpha))
    assert undercut_shift(off_by_residue) > 0.416
    for exact in (on_the_step, off_by_residue):
        assert _undercut_advice(exact).count("0.416 or more") == 1


def test_a_shift_above_the_field_s_range_is_never_advised() -> None:
    """REQ-undercut-warning-restated, boundary and safety (L08, F9; T-19-12): 6 teeth, 14.5
    degrees, module 1, no shift, sharp cutter needs a shift of 1.0619, above the
    profile_shift field's maximum, so the sentence says no shift in range avoids the
    undercut and prints none. One step either side of the field's maximum on the printed
    bound: 8 teeth at 14.5 degrees need 0.99924, rounded up to 1.000, which the field
    allows and the sentence prints; 7 teeth at 15.5 degrees need 1.00004, which rounds up
    to 1.001, above it, so none is printed. PROFILE_SHIFT_MAX is the field's own `le`, read
    from the schema, so the two cannot drift. Captured from derive() on 2026-10-09
    (L33)."""
    field_max = GearParams.model_json_schema()["properties"]["profile_shift"]["maximum"]
    assert field_max == PROFILE_SHIFT_MAX
    out_of_range = ("Below 39.9 teeth this cutter undercuts the gear, and the root is cut the "
                    "way the hob cuts it; no profile shift up to 1 avoids the undercut at this "
                    "pressure angle and tip radius.")
    base = {"module": 1, "profile_shift": 0, "backlash": 0, "root_fillet": 0}

    sharp = _hob(teeth=6, pressure_angle=14.5, **base)
    assert undercut_shift(cutter(sharp, 0.0)) == pytest.approx(1.06193, abs=5e-6)
    assert _undercut_sentences(sharp) == [out_of_range]
    assert "1.06" not in out_of_range

    inside = _undercut_sentences(_hob(teeth=8, pressure_angle=14.5, **base))
    assert undercut_shift(cutter(_hob(teeth=8, pressure_angle=14.5, **base), 0.0)) < 1.0
    assert len(inside) == 1
    assert inside[0].endswith("a profile shift of 1.000 or more avoids the undercut.")

    over = _hob(teeth=7, pressure_angle=15.5, **base)
    assert 1.0 < undercut_shift(cutter(over, 0.0)) < 1.001
    assert [s.endswith("avoids the undercut at this pressure angle and tip radius.")
            for s in _undercut_sentences(over)] == [True]
    assert not any("1.001" in s for s in _undercut_sentences(over))


def test_the_onset_is_the_trimmed_cutter_s() -> None:
    """REQ-undercut-warning-restated, precision: 12 teeth, module 1, 20 degrees, backlash 0
    has a tip radius cap of 0.47191 mm. A request of 3.0 is cut at 0.471, and the sentence
    carries that cutter's onset (16.07 -> 16.1) and shift (0.238 rounds up to 0.239), the
    same sentence a request for 0.471 itself prints. The 3.0 mm cutter, were it used, has
    no positive onset at all (2 (1.25 - 3 (1 - sin 20 degrees)) / sin^2 20 degrees < 0).
    Captured from derive() on 2026-10-09 (L33)."""
    sentence = ("Below 16.1 teeth this cutter undercuts the gear, and the root is cut the way "
                "the hob cuts it; a profile shift of 0.239 or more avoids the undercut.")
    base = {"teeth": 12, "module": 1, "pressure_angle": 20, "profile_shift": 0, "backlash": 0}
    trimmed = _hob(root_fillet=3.0, **base)
    assert _undercut_sentences(trimmed) == [sentence]
    assert _undercut_sentences(_hob(root_fillet=0.471, **base)) == [sentence]
    assert derive(trimmed).root_fillet == 0.471
    assert _onset_teeth(1, 20, 0, 3.0) < 0
    assert _onset_teeth(1, 20, 0, 0.471) == pytest.approx(16.073, abs=5e-4)


def test_a_refused_trochoid_request_keeps_the_shipped_undercut_sentence() -> None:
    """REQ-undercut-warning-restated, empty (Pitfall 6): 6 teeth, 14.5 degrees, shift -0.6,
    sharp cutter is refused as a severed tooth, so the radial root is built and the
    shipped sentence ("this model uses a radial root instead") is still true. It prints
    beside the refusal, byte for byte the string the pre-v0.2 fixture recorded for the
    same gear, read from the JSON and not retyped, and equal to what the same gear without
    the request prints. The refusal sentence was captured from derive() on 2026-10-09
    (L33)."""
    refusal = ("The trochoid roots of the two neighbouring tooth spaces cut this tooth "
               "through: the analytic root is used.")
    path = Path(__file__).parent / "regression" / "pre_v0_2.json"
    records: dict[str, dict[str, dict[str, list[str]]]] = json.loads(path.read_text())["records"]
    recorded = {w for r in records.values() for w in r["derived"]["warnings"]
                if w.startswith("Below 51.0 teeth")}
    assert len(recorded) == 1
    (shipped,) = recorded

    fields = {"teeth": 6, "module": 1, "pressure_angle": 14.5, "profile_shift": -0.6,
              "root_fillet": 0}
    asked = derive(_hob(**fields))
    assert asked.warnings == (refusal, shipped)
    assert derive(_gear(**fields)).warnings == (shipped,)
    assert (asked.root_thickness, asked.root_form_d, asked.root_waist) == (
        derive(_gear(**fields)).root_thickness, None, None)


def test_the_trimmed_tip_radius_is_printed_and_warned_one_step_either_side_of_the_cap() -> None:
    """REQ-cutter-tip-radius-settable, boundary and precision (D-01; 18-REVIEW IN-01): at
    module 1, 20 degrees, backlash 0 the largest tip radius that keeps a tip land is
    0.47191 mm. 0.471 is used and printed as 0.471 with no sentence; 0.472 is over it, so
    it is cut at the cap floored to 3 dp, 0.471, printed 0.471, with the cap sentence; 0.4715
    is under the unrounded cap, used as given, and prints at the shared 3 dp resolution as
    0.471 with no sentence (the used and the printed radius agree to the print). The
    sentence names root_fillet and says the radius is within 0.001 mm of the largest, and
    never the bare "the largest that leaves" it used to say. A sharp hob (0) is legal.
    Captured from derive() on 2026-10-09 (L33)."""
    sentence = ("root_fillet is the hob's tip radius here, and it was reduced to 0.471 mm, "
                "within 0.001 mm of the largest that keeps the cutter a tip land at this "
                "pressure angle and backlash.")
    base = {"teeth": 12, "module": 1, "pressure_angle": 20, "profile_shift": 0, "backlash": 0}
    assert cutter(_hob(root_fillet=0.0, **base), 0.0).rho_max == pytest.approx(0.47191, abs=5e-6)
    for asked, used, warns in [(0.471, 0.471, False), (0.472, 0.471, True),
                               (0.4715, 0.4715, False), (0.0, 0.0, False)]:
        p = _hob(root_fillet=asked, **base)
        d = derive(p)
        assert cutter(p, asked).rho == used
        assert d.root_fillet == round(used, 3)
        assert (sentence in d.warnings) == warns, asked
    assert [w for w in derive(_hob(root_fillet=0.472, **base)).warnings
            if "tip radius" in w or "root_fillet" in w] == [sentence]
    assert "the largest that leaves" not in sentence
    assert "root_fillet" in sentence
    assert "within 0.001 mm" in sentence


def test_every_root_sentence_is_ascii_and_in_a_fixed_order() -> None:
    """REQ-derived-numbers-honest-under-trochoid, ordering and encoding: the warnings come
    in one fixed order -- tip FDM; radial only, the L09 and lead-in sentences; the
    root-mode sentence (the cap here); trochoid only, the thickness sentence; the tip
    chamfer; the undercut sentence; the waist sentence; then bore, recess and cutout. One
    gear fires five of them: 6 teeth, module 1, 14.5 degrees, shift -0.5, default
    backlash, root_fillet 3.0 (cut at 0.661), a 3.0 mm tip chamfer (cut at 0.38) and a
    waist of 0.257 mm under the 0.4 mm floor. Its whole tuple is asserted in order, and
    every sentence of the table and every warning on the gear is ASCII (RUF001-003 in the
    source, str.isascii() on what a user reads). Captured from derive() on 2026-10-09
    (L33)."""
    p = _hob(teeth=6, module=1, pressure_angle=14.5, profile_shift=-0.5, backlash=0.10,
             root_fillet=3.0, tip_chamfer=3.0)
    d = derive(p)
    assert d.warnings == (
        "root_fillet is the hob's tip radius here, and it was reduced to 0.661 mm, within "
        "0.001 mm of the largest that keeps the cutter a tip land at this pressure angle "
        "and backlash.",
        "root_thickness and root_gap are not printed with the hob-cut root: the tooth's "
        "thickness changes too fast with radius near the root circle to give one honest "
        "number there.",
        "Tip chamfer reduced to 0.38 mm to keep it on the involute flank, above its "
        "junction with the hob-cut root.",
        "Below 40.1 teeth this cutter undercuts the gear, and the root is cut the way the "
        "hob cuts it; a profile shift of 0.567 or more avoids the undercut.",
        "The tooth is only 0.257 mm thick at its narrowest in the hob-cut root, under the "
        "0.4 mm this design holds for a printable tooth; more teeth, a larger profile_shift "
        "or a larger pressure_angle thickens it.")
    assert (d.root_fillet, d.tip_chamfer_effective, d.root_waist) == (0.661, 0.38, 0.257)
    assert all(w.isascii() for w in d.warnings)
    assert all(sentence.isascii() for sentence in _ROOT_SENTENCES.values())
