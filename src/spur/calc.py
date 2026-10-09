"""Pure-math gear geometry (no CAD kernel): derived dimensions, measurement aids,
and feasibility checks. Fast enough to run on every keystroke in the UI."""

from __future__ import annotations

import math
from dataclasses import dataclass
from itertools import pairwise
from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from collections.abc import Callable

    from .params import GearParams

MIN_WALL = 0.4          # mm, thinnest wall allowed anywhere in the body
MIN_TIP_FDM = 0.4       # mm, below this a tip is roughly one extrusion line wide
MIN_RECESS_WIDTH = 1.0  # mm, below this a face groove is not worth cutting
ROOT_CONTACT = 1e-9     # mm, how close a chamfered round or D-flat bore mouth may sit
# to the root circle before it counts as touching it. Re-measured 2026-09-27 on the
# pinned kernel: a 20-step bisection over 12 configurations (8-200 teeth, module 0.5-10,
# chamfer 1-3 mm, round and D-flat) landed identically on every one -- last failing gap
# -3.8e-8 mm, first building gap 1.9e-8 mm, gap 0.0 failing on all 12 -- the boundary
# does not move with tooth count, unlike the hex corner (L27). 1e-9 sits above the
# 1.8e-15 mm float residue of a step-aligned contact (bore_d 26.325, chamfer 1.2 on the
# default gear) and below every measured building gap; a gap of exactly 0.0025 mm (the
# smallest non-zero step-aligned gap: bore_d, module, clearance, chamfer and profile
# shift each move on their own 0.05/0.01 mm step) built on all 12. One configuration
# (19 teeth, module 1.75, chamfer 2, round) failed to build at a gap of exactly 1e-9 mm
# even though check() would accept it (gap == ROOT_CONTACT is not < ROOT_CONTACT) --
# this sub-2e-8 mm residual band is orders of magnitude below the field's 0.05 mm step,
# so the UI's step buttons never land in it -- but nothing enforces the step: `step` in
# params.py's _f() is JSON-schema metadata only, not a pydantic `multiple_of`, and
# app.js forwards a typed value as-is, so a value typed into the field, a shared link
# or an API/CLI caller sending an 11-significant-figure bore_d can land inside this
# band (09-REVIEW.md WR-02) -- reproduced live at bore_d
# 24.724999998 (19T, m1.75, chamfer 2, round): check() accepts it (gap
# 1.000000082740371e-09 > ROOT_CONTACT) and the kernel still raises BuildError, pinned
# by test_model.py's test_the_kernel_can_fail_inside_the_root_contact_residual_band.
TIP_CHAMFER_MARGIN = 0.001  # mm, how far inside the start of the involute spline the
# tip chamfer's footprint stops. Measured 2026-09-28 (bench/RESULTS.md "Tooth-tip
# chamfer spike"): a 20-step bisection on six configurations (19/40 teeth, module 1,
# profile shifts and root fillets that push the spline start above the pitch circle)
# found the kernel's chamfer failing within about 2 microns of pred = ra - spline_start
# on five of six (last building 0.9-1.9e-6 mm inside pred, first failing 0.9-1.0e-6 mm
# past it), teeth-independent where compared; the sixth built 0.04 mm past pred, so the
# rule is conservative there, never optimistic. A 405-set grid had 0 failures at pred or
# 0.05 mm inside it. The margin is one printed step, not the contact itself, because
# tip_chamfer_effective rounds to 3 dp at construction and round() can move a value up
# by half a step (2.9365 mm rounds to 2.937 mm) -- a cap sitting exactly at the contact
# could round past it. Phase 19 re-bisected the law across the hob root's spline-to-spline
# junction (bench/RESULTS.md "Chamfer across the junction (19-01)", 2026-10-08, 14 rows,
# 20 steps): no row optimistic, 8 on the law (worst last-building minus pred -3.06e-6 mm)
# and 6 conservative, so the same margin holds under the trochoid.
HEX_CELL_CAP = 120  # cells, the most whole honeycomb cells one part may have. Measured
# 2026-09-29 (bench/RESULTS.md "Honeycomb cell-count spike (Phase 11, D-24)") on a
# 12-CPU arm64 host, load averages 8-9 (well above this project's own "quiet" bar):
# at 200 teeth, module 10, both recesses -- the largest web a honeycomb can sit on,
# so the cap always binds there (D-11) -- the 120-cell row (a 149.1 mm cell) read
# 7.15 s of the 7.5 s budget (a quarter of SPUR_BUILD_TIMEOUT); the next row (150
# cells) read 7.95 s, over budget. The module-1.75 confirmation at the same 120 cells
# read 7.25 s, 0.25 s of headroom -- narrower than the cap row's own 0.35 s but still
# inside budget, so the module-10 configuration still sets the cap. One constant, not
# a per-cell cost model (D-12): the same on every machine, conservative on smaller
# gears -- a quieter host would only raise what this measured, never lower it.

ROOT_CURVE_POINTS = 16  # points, how many the hob's trochoid root is sampled at. STACK's
# N = 16 uniform in roll measured 3.6-4.0e-5 mm against cq.Edge.makeSpline at module 1,
# z 8/10/14, tip radius 0.38 mm (re-run in the research with the pinned kernel pair:
# 3.58e-5, 3.89e-5, 3.98e-5 mm); the shipped flank is 16 points too. Phase 19 sets the
# kernel bar, not this phase.
TROCHOID_JOIN_EPS = 1e-4  # relative to rb, never millimetres: how close to zero the
# roll of the cutter's flank foot (Cutter.xi) may be before the junction with the
# involute is taken as tangent without a bracket. Measured in the repo 2026-10-08 (Apple
# M2 Max, Python 3.12.13, 1-minute load 1.7) by `bench/trochoid.py epsilon`: 400 seeded
# random allowed gears (module 0.2-10, pressure angle 14.5-30, backlash 0-0.5, tip radius
# 0-0.5 m), the shift tuned so xi = -t*rb for t from 1e-2 to 1e-12 at 4 steps per decade,
# the bracket lost (`_junction(c, 0.0)` is None) at largest t = 5.6e-6 and median 3.2e-6,
# so 1e-4 is the smallest power of ten above 10x the largest loss (5.6e-5). STACK's two
# points are its bracket: found at xi -2.9e-3 mm and lost at -2.9e-5 mm on the 10-tooth,
# 20 degree gear (rb 4.698 mm); here that gear's own edge is -2.64e-5 mm, the same place
# within one scan step, and 1e-4*rb is 4.7e-4 mm there, 16x STACK's loss point. Inside the
# band the flank join is the form point, off by at most (eps*rb)^2/(2*rb) = 5e-9*rb.
# bench/RESULTS.md "Join epsilon (18-03)" carries the run.


def inv(a: float) -> float:
    """Involute function."""
    return math.tan(a) - a


@dataclass(frozen=True)
class Profile:
    z: int
    m: float
    alpha: float    # pressure angle, radians
    r: float        # pitch radius
    rb: float       # base radius
    ra: float       # tip radius
    rf: float       # root radius
    psi_p: float    # half tooth-thickness angle at the pitch circle

    @property
    def r_start(self) -> float:
        """Radius where the involute flank starts (base circle, or root if above it)."""
        return max(self.rb, self.rf)

    def half_angle(self, rho: float) -> float:
        """Half tooth-thickness angle at radius rho (rho >= rb)."""
        phi = math.acos(min(1.0, self.rb / rho))
        return self.psi_p + inv(self.alpha) - inv(phi)


def _dedendum(m: float, x: float) -> float:
    """Depth of the root circle below the pitch circle, mm: the one definition both the
    root circle (`profile`) and the hob's tip (`cutter`) read, so the two can never
    disagree about `rf` (D-06, PITFALLS 22)."""
    return m * (1.25 - x)


def _pitch_thickness(m: float, alpha: float, x: float, bl: float) -> float:
    """Tooth thickness on the pitch circle, mm, backlash taken off: the one definition
    `profile` (half tooth-thickness angle) and `cutter` (cutter tooth width, backlash
    thickening it) both read (D-06, PITFALLS 3 and 22)."""
    return m * (math.pi / 2 + 2 * x * math.tan(alpha)) - bl


def profile(p: GearParams, backlash: float | None = None) -> Profile:
    a = math.radians(p.pressure_angle)
    m, z, x = p.module, p.teeth, p.profile_shift
    bl = p.backlash if backlash is None else backlash
    r = m * z / 2
    s = _pitch_thickness(m, a, x, bl)
    return Profile(z=z, m=m, alpha=a, r=r, rb=r * math.cos(a), ra=r + m * (1 + x),
                   rf=r - _dedendum(m, x), psi_p=s / (2 * r))


def bore_radius(p: GearParams) -> float:
    return (p.bore_d + p.bore_clearance) / 2 if p.bore_d > 0 else 0.0


def hex_across_flats(p: GearParams) -> float:
    """The hex bore's effective across-flats: clearance added across the flats
    (REQ-hex-bore) -- what calipers read between two flats. 0.0 with no hex bore."""
    return p.bore_hex + p.bore_clearance if p.bore_hex > 0 else 0.0


def keyway_width_effective(p: GearParams) -> float:
    """The keyway's effective width, clearance added as it is to the bore
    (REQ-keyway-bore) -- what calipers read across the slot. 0.0 with no keyway."""
    return p.keyway_width + p.bore_clearance if p.keyway_width > 0 else 0.0


def keyway_corner_radius(p: GearParams) -> float:
    """The keyway's farthest point from the axis: its floor corner, un-chamfered
    because the slot is cut after the rim chamfer (D-06). The floor sits at
    bore_radius(p) + keyway_depth, the as-cut wall plus the depth (D-14) -- a
    3 x 1.4 mm keyway on the default 9 mm bore puts the corner at 6.1791 mm. 0.0 with
    no keyway."""
    if p.keyway_width > 0 and p.keyway_depth > 0:
        return math.hypot(bore_radius(p) + p.keyway_depth, keyway_width_effective(p) / 2)
    return 0.0


def keyway_flat_wall(p: GearParams) -> float:
    """The round bore wall left between the D-flat's corner and the keyway's side,
    measured as an arc on the as-cut wall (D-02's chosen measure): with r = the as-cut
    bore wall and flat_x the flat's distance from the axis (the plane model._cut_bore
    cuts), the wall is the arc between the flat's corner angle and the keyway side's
    foot angle. 2.4956 mm for the default 3 mm keyway on the default D-flat, 0.4174 mm
    at keyway_width 6.45 mm (the widest the kernel still builds with MIN_WALL of wall),
    0.0 at keyway_width 7.0 mm (the side lands on the flat's corner) -- negative once
    the slot's side lies past the flat's corner. check() calls this only with a D-flat
    inside its range (bore_d/2 < bore_flat < bore_d) and a keyway narrower than the bore
    (keyway_width < bore_d), so both acos arguments stay inside [-1, 1]."""
    r = bore_radius(p)
    flat_x = p.bore_flat + p.bore_clearance - r
    return r * (math.acos(keyway_width_effective(p) / 2 / r) - math.acos(flat_x / r))


def bore_rim_limit(p: GearParams) -> float:
    """The farthest any point on the bore's rim can sit from the axis -- the exact
    geometric bound, no slack.

    Round and D-flat both reduce to bore_radius(p): the D-flat hole is the round hole
    intersected with a rectangle (model._cut_bore), a strict subset of the circle, so it
    adds no point farther out. A hex bore's rim reaches its corners, the circumradius --
    across-flats over sqrt(3): 6.15 mm across flats puts the corners at 3.5507 mm, and
    the built corners read the same within 4.4e-16 mm, 2026-09-26 (research
    ARCHITECTURE.md Q2's rejected anti-pattern was generalizing lim by widening it
    instead). calc.py knows no kernel tolerance; the selection slack that turns this
    exact bound into a matching band belongs to model.py, not here.
    """
    if p.bore_hex > 0:
        return hex_across_flats(p) / math.sqrt(3)
    return bore_radius(p)


def bore_mouth_limit(p: GearParams) -> float:
    """The farthest the chamfered bore mouth reaches on an end face.

    A round or D-flat rim carries the chamfer straight out (c). A hex carries it to the
    corners, where two chamfered sides meet, at c / cos(30 deg) = 2c/sqrt(3) -- measured
    exact on the pinned kernel at c = 0.4, 1 and 3 mm, 2026-09-26. R + c undercounts by
    0.155c: with it, a 3 mm chamfer on a 6 mm hex ran the recess into an invalid solid at
    2.586 mm and a kernel failure at 3 mm (research PITFALLS.md Pitfall 1). 0.0 with no
    bore at all.

    A keyway's floor corner is the farthest end-face point when it lies beyond the
    chamfered rim, and the recess yields to it as it yields to a hex corner
    (09-CONTEXT.md D-09): the 3 x 1.4 mm keyway on the default bore puts its corner
    0.327 mm from the default recess hub wall, under MIN_WALL. No fuzzy boolean (tol=)
    is needed here: the slot's faces lie inside the bore or inside material, so this
    clearance keeps MIN_WALL between the corner and the recess by construction (research
    Pitfall 3, 09-CONTEXT.md Claude's Discretion). recess_radii() itself is unchanged --
    it already reads bore_mouth_limit(p).
    """
    if p.bore_hex > 0:
        return bore_rim_limit(p) + 2 / math.sqrt(3) * p.bore_chamfer
    return max(bore_rim_limit(p) + (p.bore_chamfer if p.bore_d > 0 else 0.0),
               keyway_corner_radius(p))


def recess_radii(p: GearParams, rf: float) -> tuple[float, float] | None:
    """(inner, outer) radius of the face groove, narrowed to fit between the hub wall
    and the tooth rim, or None when there is no room for a groove at all.

    The requested width is a wish, not a constraint. The stock defaults are absolute
    millimetres sized for a 19-tooth m=1.75 gear, so a smaller gear would otherwise be
    refused over a parameter the user never touched. Same contract as root_fillet():
    cap silently here, warn about it in derive().
    """
    if p.recess_sides == "none" or p.recess_depth <= 0 or p.recess_width <= 0:
        return None
    r_bore = bore_rim_limit(p)            # the bore's farthest point (radius, or hex corners)
    hub = bore_mouth_limit(p) + MIN_WALL  # clear of the chamfered bore mouth
    rim = rf - MIN_WALL                   # clear of the tooth rim
    if rim - hub < MIN_RECESS_WIDTH:
        return None
    width = min(p.recess_width, rim - hub)
    # Default position: hub wall and rim wall come out equal, as before any capping.
    centred = r_bore + (rf - r_bore - p.recess_width) / 2
    r_in = p.recess_inner_d / 2 if p.recess_inner_d > 0 else centred
    r_in = min(max(r_in, hub), rim - width)
    return r_in, r_in + width


def _tooth(pr: Profile) -> tuple[float, float, float]:
    """(tip thickness, root thickness, root gap), arc lengths in mm.

    Thickness and gap are both measured on the root circle: below the base circle the
    flank is radial, so the half-angle down there is the one at r_start.
    """
    psi_root = pr.half_angle(pr.r_start)
    tip = 2 * pr.ra * pr.half_angle(pr.ra)
    root = 2 * pr.rf * psi_root
    gap = 2 * pr.rf * (math.pi / pr.z - psi_root)
    return tip, root, gap


def root_fillet(p: GearParams) -> float:
    """Root fillet actually used: the requested radius, capped to what fits the gap."""
    _, _, gap = _tooth(profile(p))
    return round(min(p.root_fillet, 0.45 * gap), 3) if gap > 0 else 0.0


def spline_start(pr: Profile, fillet: float, curve: RootCurve | None = None) -> float:
    """Radius where the outline's involute spline begins: the base circle (or the root
    circle, if larger), raised to make room for the root fillet's straight lead-in when
    one is needed, and never past halfway from root to tip.

    Under the hob's root (`curve` given) it is the junction radius, the curve's own last
    float, and the halfway clamp does not apply: 1,713 of 5,159 trochoid junctions sit
    beyond halfway (19-RESEARCH F6), and the chamfer bound that reads this
    (`tip_chamfer_limit`) was re-bisected on exactly that radius (bench/RESULTS.md
    "Chamfer across the junction (19-01)"). `fillet` is not read then.

    model._outline starts the flank spline here, and tip_chamfer_limit keeps the tip
    chamfer's footprint above it, because the kernel cannot carry an end-face chamfer
    from the involute spline across onto the straight lead-in (bench/RESULTS.md "Tooth-
    tip chamfer spike"). Not Profile.r_start: that is the theoretical involute start,
    this is where the modelled spline actually starts.
    """
    if curve is not None:
        return curve.points[-1][0]
    r_line = max(pr.rb, pr.rf + 2.0 * fillet) if fillet > 0 else pr.rb
    r_line = min(r_line, pr.rf + 0.5 * (pr.ra - pr.rf))
    return max(r_line, pr.r_start)


def recess_fillet(p: GearParams, rf: float) -> float:
    """Recess floor fillet actually used: the requested radius, capped to the groove.

    Both floor corners carry the fillet, so it cannot exceed half the groove width.
    """
    rr = recess_radii(p, rf)
    if not rr or p.recess_fillet <= 0:
        return 0.0
    width = rr[1] - rr[0]
    return round(min(p.recess_fillet, 0.45 * width, 0.45 * p.recess_depth), 3)


def tip_chamfer_limit(p: GearParams, rm: RootMode | None = None) -> tuple[float, str]:
    """(limit, reason): the smallest of three bounds on the tip chamfer, and which one
    binds. Compared as a tuple so a tie is broken by the reason text, deterministically.

    - 0.45 x face_width: the axial cap. Both end faces are chamfered, so the tip land
      between them is face_width - 2c; this is root_fillet's and recess_fillet's own
      0.45 family -- 10% of the dimension the cut eats always remains.
    - ra - r: the radial cap. The chamfer's footprint on the end face reaches inward
      from the tip circle to about ra - c and stays above the pitch circle, so the
      working flank is untouched at the faces.
    - ra - spline_start(...) - TIP_CHAMFER_MARGIN: the kernel's own limit, measured, not
      a design rule (bench/RESULTS.md "Tooth-tip chamfer spike") -- it binds only where
      the root fillet's straight lead-in reaches above the pitch circle (a large profile
      shift or root fillet for the module). Under the hob's root there is no lead-in:
      the bound reads the junction of the two splines instead.

    `rm` is the caller's one answer to "which root is built"; without it this asks
    `root_mode` itself, so the bound and the part cannot name different roots.
    """
    pr = profile(p)
    if rm is None:
        rm = root_mode(p, pr, requested=p.root_shape, rho=p.root_fillet)
    if rm.curve is not None:
        flank = (pr.ra - spline_start(pr, 0.0, rm.curve) - TIP_CHAMFER_MARGIN,
                 "to keep it on the involute flank, above its junction with the hob-cut "
                 "root")
    else:
        flank = (pr.ra - spline_start(pr, root_fillet(p)) - TIP_CHAMFER_MARGIN,
                 "to keep it on the involute flank, above the straight lead-in from the "
                 "root fillet")
    return min(
        (0.45 * p.face_width, "to leave a land on the tooth tip between the two faces' "
                              "chamfers"),
        (pr.ra - pr.r, "to keep it above the pitch circle"),
        flank,
    )


def tip_chamfer_effective(p: GearParams, rm: RootMode | None = None) -> float:
    """Tip chamfer actually cut on the tooth-tip edges at both faces: the requested
    size, trimmed to what the tooth allows and never refused (L03,
    REQ-tip-chamfer-capped). model.py cuts exactly this value, so the part and the
    printed number cannot disagree (L08)."""
    if p.tip_chamfer <= 0:
        return 0.0
    return round(min(p.tip_chamfer, tip_chamfer_limit(p, rm)[0]), 3)


def cutout_walls(p: GearParams, rf: float) -> tuple[float, float] | None:
    """(hub wall, rim wall) of the one body-cutout pattern set, unrounded, or None with
    no pattern set (D-20).

    The hub side is measured from the farthest point of the chamfered bore mouth,
    bore_mouth_limit(p), the same datum recess_radii() clears (D-17, L27/L28) -- exact
    for a round or D-flat bore, the corner's reach for a hex or keyed bore, and so a
    lower bound where a cutout faces a flat (L08). The rim side is measured from the
    root circle, rf. Spokes read hub_d and rim_wall directly (D-01): the rim corner
    arcs stay inside rf - rim_wall, so the rim wall is exactly rim_wall. The honeycomb
    reads the walls off the cut cells themselves -- exact on the polygons
    model._cell_cutters cuts, so the walls read at least hex_wall: the whole-cell
    test's circumradius (size / sqrt(3)) is a conservative bound for containment, not
    the true nearest point, which can be a flat closer to the axis than any corner
    (Flagged Assumption A3 -- the naive centre_radius - reach bound under-reports the
    tracer's inner-ring wall by 0.232 mm, 6.268 mm instead of the true 6.5 mm).
    """
    if p.spoke_count > 0:
        return p.hub_d / 2 - bore_mouth_limit(p), p.rim_wall
    if p.hole_count > 0:
        inner = p.hole_circle_d / 2 - p.hole_d / 2
        outer = p.hole_circle_d / 2 + p.hole_d / 2
        return inner - bore_mouth_limit(p), rf - outer
    if p.hex_cell > 0:
        size, cells = hex_cells(p, rf)
        reaches = [_hex_reach(cx, cy, size) for cx, cy in cells]
        nearest = min(r[0] for r in reaches)
        farthest = max(r[1] for r in reaches)
        return nearest - bore_mouth_limit(p), rf - farthest
    return None


def spoke_opening(p: GearParams) -> float:
    """The arc between the feet of adjacent bar sides on the hub circle (D-06):
    keyway_flat_wall's arc measure (research Pitfall 4, Open Q1), applied to two bar
    feet instead of a flat's corner and a keyway's side. This is the narrowest gap a
    sector has -- beyond the hub the bars diverge -- so both D-06's fillet cap and
    D-16's neighbour rule read this one number. 0.0 when spoke_width >= hub_d (the
    bars would meet or cross at the hub before reaching it). Callers pass
    spoke_count >= 1 and hub_d > 0 -- check()'s half-set rule (D-15) guarantees both
    before this is ever called.
    """
    if p.spoke_width >= p.hub_d:
        return 0.0
    r = p.hub_d / 2
    return r * (2 * math.pi / p.spoke_count - 2 * math.asin(p.spoke_width / p.hub_d))


def spoke_fillet_limit(p: GearParams) -> tuple[float, str]:
    """(limit, reason): the smaller of the two dimensions a sector's corner fillets
    share -- root_fillet's 0.45-of-the-shared-dimension family (two corner arcs share
    each dimension, so 10% of it always stays). Compared as a tuple, tip_chamfer_limit's
    shape, so a tie is broken by the reason text, deterministically.
    """
    pr = profile(p)
    return min(
        (0.45 * spoke_opening(p), "to fit the opening between the arms at the hub"),
        (0.45 * (pr.rf - p.rim_wall - p.hub_d / 2),
         "to fit between the hub and the rim wall"),
    )


def spoke_fillet_effective(p: GearParams) -> float:
    """Spoke fillet actually cut at the corners of each cut-out sector: the requested
    radius, capped to what fits the sector, and never refused (L03) -- always a cap,
    never a 422. model.py cuts exactly this value, so the part and the printed number
    cannot disagree (L08). 0.0 with no spokes or spoke_fillet 0 (sharp corners)."""
    if p.spoke_count == 0 or p.spoke_fillet <= 0:
        return 0.0
    return round(min(p.spoke_fillet, spoke_fillet_limit(p)[0]), 3)


def _under_min_wall(wall: float) -> bool:
    """True when a cutout wall is thinner than MIN_WALL, comparing at 1e-6 mm rather
    than the raw float.

    Step-aligned inputs carry float residue (bore_mouth_limit(p) reads
    4.9750000000000005 on the default gear, math.sin(math.pi / 6) reads
    0.49999999999999994), so a wall sized to exactly MIN_WALL can compute as
    0.39999999999999947 -- comparing the raw float would refuse a wall the user sized
    exactly to the rule. 1e-6 mm is far below the 0.05 mm field step (so no settable
    wall lands in the rounding band) and far above the ~1e-15 mm residue (so it never
    accepts a wall that is genuinely thinner). Every cutout MIN_WALL rule added from
    here on goes through this; the pre-existing bore/keyway rules are untouched.
    """
    return round(wall, 6) < MIN_WALL


def _listed(items: list[str]) -> str:
    """"a", "a and b", "a, b and c" -- the joining every cutout sentence with more than
    one named field uses, so a two-field list still reads exactly as the existing hole
    sentences did (D-15's half-set rule, D-17's hub/rim/annulus rules)."""
    if len(items) <= 1:
        return "".join(items)
    return ", ".join(items[:-1]) + f" and {items[-1]}"


def hole_gap(p: GearParams) -> float:
    """Wall left between two neighbouring holes, measured on the line joining their
    centres (D-16): the chord between adjacent centres, hole_circle_d * sin(pi /
    hole_count), less one hole diameter. Callers pass hole_count >= 2 -- with one hole
    there is no neighbour."""
    return p.hole_circle_d * math.sin(math.pi / p.hole_count) - p.hole_d


def whole_cells(cell: float, wall: float, inner: float, outer: float,
                ) -> tuple[tuple[float, float], ...]:
    """The centres of every whole hexagonal cell on the axis-centred lattice whose
    flats face +-X and vertices +-Y -- model._cut_bore's own convention (D-08): pitch
    `cell + wall`, rows spaced `pitch * sqrt(3) / 2` along Y, centres
    `x = pitch * (a + b / 2)`, `y = pitch * b * sqrt(3) / 2`. A centre is kept when its
    hexagon -- corner reach `cell / sqrt(3)` -- lies entirely inside `[inner, outer]`:
    `inner + cell / sqrt(3) <= hypot(x, y) <= outer - cell / sqrt(3)` (D-07, inclusive).
    The origin cell (a = b = 0) always fails this test because inner > 0, so it is
    never cut -- it sits inside the bore. Returns `()` when the band is empty. Rows
    iterate b ascending then a ascending, so the same arguments return the same tuple
    every time (D-24's spelling comparison and the cap search both rely on this
    order). Lives here so check(), cutout_walls(), derive() and model._cell_cutters
    all read the one enumeration (L08); bench/honeycomb_spike.py imports it back.
    """
    if outer <= inner:
        return ()
    pitch = cell + wall
    row_h = pitch * math.sqrt(3) / 2
    reach = cell / math.sqrt(3)
    lo, hi = inner + reach, outer - reach
    if hi < lo:
        return ()
    # |y| <= outer bounds b; a row or two of rounding slack is harmless -- the hypot
    # test below is the exact filter, this just keeps the search off the unbounded
    # plane (D-07's "no candidate outside the square is visited").
    b_max = int(outer / row_h) + 1
    cells: list[tuple[float, float]] = []
    for b in range(-b_max, b_max + 1):
        y = pitch * b * math.sqrt(3) / 2
        if abs(y) > outer:
            continue
        a_span = outer / pitch
        a_lo = math.floor(-a_span - b / 2)
        a_hi = math.ceil(a_span - b / 2)
        for a in range(a_lo, a_hi + 1):
            x = pitch * (a + b / 2)
            if abs(x) > outer:
                continue
            r = math.hypot(x, y)
            if lo <= r <= hi:
                cells.append((x, y))
    return tuple(cells)


def cell_count_floor(cell: float, wall: float, inner: float, outer: float) -> float:
    """A guaranteed lower bound on `len(whole_cells(cell, wall, inner, outer))` --
    D-13's area estimate, taken as a floor rather than an approximation: the centre
    band `[inner + cell/sqrt(3), outer - cell/sqrt(3)]` eroded by the pitch hexagon's
    own circumradius (`pitch / sqrt(3)`) leaves a band where every point lies in the
    Voronoi cell of a lattice point that is itself inside the original band -- so the
    eroded band's area over one Voronoi cell's area (`sqrt(3)/2 * pitch**2`, a regular
    hexagon of across-flats `pitch`) never overcounts. Planning checked 1920 (cell,
    wall, inner, outer) sets against the exact `whole_cells()` count: 0 violations.
    0.0 when the eroded band is empty (`hi2 <= lo2`).
    """
    pitch = cell + wall
    reach = cell / math.sqrt(3)
    erosion = pitch / math.sqrt(3)
    lo2 = inner + reach + erosion
    hi2 = outer - reach - erosion
    if hi2 <= lo2:
        return 0.0
    return math.pi * (hi2**2 - lo2**2) / (math.sqrt(3) / 2 * pitch**2)


def cells_within(cap: int, cell: float, wall: float, inner: float, outer: float,
                 ) -> tuple[float, tuple[tuple[float, float], ...]]:
    """D-13's raise-to-fit: steps `cell` up by 0.05 mm (the field's own step) from the
    request until the exact whole-cell count is `<= cap`. `cell_count_floor`'s
    guaranteed lower bound is checked first at each step -- a size whose floor already
    exceeds `cap` can never have fitted, so the exact enumeration (`whole_cells`) never
    runs for a size that was going to be skipped anyway; this is what keeps the search
    cheap even where the unconstrained count would be in the millions (D-13's own
    example: a 200-tooth module-10 web at cell 3 / wall 1 implies roughly 2.2e5 cells).
    """
    k = 0
    while True:
        s = round(cell + 0.05 * k, 3)
        if cell_count_floor(s, wall, inner, outer) <= cap:
            found = whole_cells(s, wall, inner, outer)
            if len(found) <= cap:
                return s, found
        k += 1


def hex_cells(p: GearParams, rf: float) -> tuple[float, tuple[tuple[float, float], ...]]:
    """The honeycomb actually cut: (across-flats applied, cell centres) -- the one
    result model._cell_cutters cuts, check() counts and derive() reports (L08).
    `(0.0, ())` with `hex_cell <= 0` -- no honeycomb. Otherwise `cells_within`'s
    raise-to-fit over the web annulus (D-09): `hex_wall` outside the chamfered bore
    mouth (`bore_mouth_limit(p)`, the recess's own datum) and `hex_wall` inside the
    root circle (`rf`).

    Measured (`.venv/bin/python -m timeit`, best of 5, arm64, Python 3.12.13,
    2026-09-29, the same 12-CPU host the honeycomb spike ran on): `derive()` alone
    costs 14.1 usec on `GearParams()` (no honeycomb, beside 09-05's 11.5 usec
    baseline), 115 usec on the tracer link (`hex_cell=3, hex_wall=1`, 18 cells), and
    15.6 msec at the heaviest input (`teeth=200, module=10, hex_cell=3, hex_wall=0.4`
    -- the smallest allowed wall, the most candidate cells to search). One full
    request makes three `hex_cells` calls: `check()` at construction, then
    `cutout_walls()` and `derive()` itself each call it once more -- `derive()`'s own
    two calls are what these numbers measure; `check()`'s third call costs the same
    again. No cache is added: this is what it costs.
    """
    if p.hex_cell <= 0:
        return 0.0, ()
    return cells_within(HEX_CELL_CAP, p.hex_cell, p.hex_wall,
                        bore_mouth_limit(p) + p.hex_wall, rf - p.hex_wall)


def _point_segment_distance(px: float, py: float, ax: float, ay: float,
                            bx: float, by: float) -> float:
    """Distance from (px, py) to the segment (ax, ay)-(bx, by), the exact minimum over
    the whole edge rather than just its two endpoints -- a hexagon's flat can be the
    nearest point to the axis, not either of its corners (D-08)."""
    dx, dy = bx - ax, by - ay
    length_sq = dx * dx + dy * dy
    if length_sq == 0:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / length_sq))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def _hex_reach(cx: float, cy: float, size: float) -> tuple[float, float]:
    """(nearest point to the axis, farthest vertex from the axis) of one honeycomb
    hexagon centred at (cx, cy), across-flats size, flats on +-X and vertices on +-Y
    (D-08) -- the same `polygon(6, size, circumscribed=True)` `model._cell_cutters`
    cuts. The nearest point can be a flat (the tracer's inner ring faces the axis with
    a flat, 6.5 mm, not the 6.268 mm a circumradius test would read -- Flagged
    Assumption A3) or a vertex, so this walks all six edges rather than assuming
    either.
    """
    r = size / math.sqrt(3)
    verts = [(cx + r * math.cos(math.radians(30 + 60 * i)),
             cy + r * math.sin(math.radians(30 + 60 * i))) for i in range(6)]
    farthest = max(math.hypot(vx, vy) for vx, vy in verts)
    nearest = min(_point_segment_distance(0.0, 0.0, *verts[i], *verts[(i + 1) % 6])
                 for i in range(6))
    return nearest, farthest


def check(p: GearParams) -> list[tuple[str, tuple[str, ...]]]:
    """Reasons the parameters can't produce a sound part, each with the fields involved.

    Only conflicts the user has to resolve themselves land here. Dimensions that can be
    trimmed to fit without contradicting an explicit choice — the root fillet, the face
    recess — are capped in their own functions and reported as warnings instead.
    """
    errors: list[tuple[str, tuple[str, ...]]] = []
    pr = profile(p)
    if pr.rf <= MIN_WALL:
        return [("Root diameter is too small; increase teeth or module.", ("teeth", "module"))]

    tip, _, gap = _tooth(pr)
    if tip <= 0.05:
        errors.append((f"Teeth come to a point (tip {tip:.2f} mm); "
                       "lower the pressure angle or profile shift.",
                       ("pressure_angle", "profile_shift")))
    if gap <= 0.05:
        errors.append(("Neighbouring teeth merge at the root; lower the profile shift.",
                       ("profile_shift",)))

    # D-13/D-03 decide which branch below even applies, so they run first and name
    # both keyway fields -- a keyway is the pair, and a half-set one also trips D-03,
    # which names both anyway (09-CONTEXT.md D-13).
    has_keyway = p.keyway_width > 0 or p.keyway_depth > 0
    if has_keyway and p.bore_hex > 0:
        errors.append((
            "A keyway cannot be cut into a hex bore: set bore_hex to 0 for a keyed "
            "round or D-flat bore, or set keyway_width and keyway_depth to 0.",
            ("bore_hex", "keyway_depth", "keyway_width")))
    elif has_keyway and p.bore_d == 0:
        errors.append((
            "A keyway needs a round bore to cut into: set bore_d, or set "
            "keyway_width and keyway_depth to 0.",
            ("bore_d", "keyway_depth", "keyway_width")))
    if (p.keyway_width > 0) != (p.keyway_depth > 0):
        errors.append((
            "A keyway needs both keyway_width and keyway_depth: set both above 0, "
            "or both to 0.",
            ("keyway_depth", "keyway_width")))

    if p.bore_hex > 0:
        # The hexagon replaces the round profile (D-01), so bore_d and bore_flat are
        # not checked here -- derive() reports them as ignored, and a 422 naming a
        # field the response calls ignored would contradict it (D-03).
        if bore_rim_limit(p) > pr.rf - MIN_WALL:
            errors.append((
                "Hex bore is too large for the root diameter: its corners "
                f"({2 * bore_rim_limit(p):.2f} mm across) must stay {MIN_WALL:g} mm "
                f"inside the root circle ({2 * pr.rf:.2f} mm); reduce bore_hex.",
                ("bore_hex",)))
        # No rule compares the chamfer with the hex's side: measured 2026-09-26 on the
        # pinned kernel, a 0.375 mm side took every chamfer up to the field's 3 mm
        # bound (ratio 8), removed volume matching the analytic hex frustum within
        # 1e-9. What fails is the chamfered corner crossing the root circle --
        # "BRep_API: command not done" 0.05 mm past it where a corner meets a tooth
        # gap (19 teeth), while it built 0.30 mm past where a corner meets a tooth
        # (40 teeth). So the rule sits on the root circle, with MIN_WALL, wherever the
        # corners land, not on the side. With bore_chamfer 0 the mouth is the corner,
        # so only the rule above can fire.
        elif bore_mouth_limit(p) > pr.rf - MIN_WALL:
            errors.append((
                "Bore chamfer is too large for this hex bore: at the corners it "
                f"reaches {2 * bore_mouth_limit(p):.2f} mm across, which must stay "
                f"{MIN_WALL:g} mm inside the root circle ({2 * pr.rf:.2f} mm); reduce "
                "bore_chamfer or bore_hex.",
                ("bore_chamfer", "bore_hex")))
    else:
        r_bore = bore_radius(p)
        if p.bore_d > 0 and r_bore > pr.rf - MIN_WALL:
            errors.append(("Bore is too large for the root diameter.", ("bore_d",)))
        # D-12: the rule sits at the measured contact point, not at bore_mouth_limit(p) >
        # rf - MIN_WALL like the hex (L27), so no round or D-flat link that builds today
        # is refused (09-CONTEXT.md D-12, L05); it reads the chamfered rim, not
        # bore_mouth_limit, because a keyway corner has its own rule (D-10). The two
        # round rules never stack (elif): past the too-large rule the mouth is past the
        # root anyway.
        elif p.bore_d > 0 and r_bore + p.bore_chamfer > pr.rf - ROOT_CONTACT:
            mouth = r_bore + p.bore_chamfer
            errors.append((
                "Bore chamfer reaches the root circle: the chamfered bore mouth is "
                f"{2 * mouth:.3f} mm across and the root circle {2 * pr.rf:.3f} mm, and "
                "the mouth must stay inside it; reduce bore_chamfer or bore_d.",
                ("bore_chamfer", "bore_d")))
        if p.bore_d > 0 and p.bore_flat > 0 and not p.bore_d / 2 < p.bore_flat < p.bore_d:
            errors.append((f"D-flat must be between {p.bore_d / 2:g} and {p.bore_d:g} mm "
                           "(flat to opposite side).", ("bore_flat",)))
        # D-11: no kernel limit exists here -- research cut slots to 166% of bore_d on a
        # 9.15 and a 30.15 mm bore and every cut was one valid solid; planning built
        # keyway_width equal to bore_d (sides tangent to the bore) valid too. The bound
        # is definitional (09-CONTEXT.md D-11, resolved 2026-09-27): at keyway_width +
        # bore_clearance >= bore_d + bore_clearance the slot's sides stop meeting the
        # bore wall and the part is no longer a keyed bore. bore_clearance is on both
        # sides, so the comparison drops it.
        keyed = p.bore_d > 0 and keyway_corner_radius(p) > 0
        if keyed and p.keyway_width >= p.bore_d:
            errors.append((
                f"Keyway is too wide for the bore: keyway_width ({p.keyway_width:g} mm) "
                f"must be less than bore_d ({p.bore_d:g} mm), or its sides no longer "
                "meet the bore wall; reduce keyway_width.",
                ("bore_d", "keyway_width")))
        # D-02: the kernel built the default D-flat with a keyway at every width tried
        # (0.417 mm of wall at 6.45, 0.381 at 6.5, 0 at 7.0 where the side lands on the
        # flat's corner, and 7.5 notching the flat), so MIN_WALL is the part's rule: it
        # keeps a near-tangent sliver of round wall from reaching the kernel (research
        # PITFALLS.md Pitfall 1). The measure is the arc on the as-cut wall from the
        # flat's corner to the foot of the keyway's side.
        elif (keyed and p.bore_flat > 0 and p.bore_d / 2 < p.bore_flat < p.bore_d
              and keyway_flat_wall(p) < MIN_WALL):
            errors.append((
                "Keyway runs too close to the D-flat: it leaves "
                f"{max(keyway_flat_wall(p), 0.0):.3f} mm of round bore wall between the "
                f"flat and the keyway's side, which must be at least {MIN_WALL:g} mm; "
                "reduce keyway_width or increase bore_flat.",
                ("bore_flat", "keyway_width")))
        # D-10: the floor corner, not the floor centreline, is the keyway's nearest
        # point to the root (09-CONTEXT.md D-10). The kernel built floors past the root
        # (depth 9.9 on the default gear puts the corners 0.12 mm past it and opens the
        # slot into a tooth gap), so MIN_WALL is the part's rule. Never capped: a
        # shallower keyway is a part the key does not fit (REQ-keyway-wall-refused, L03).
        if keyed and keyway_corner_radius(p) + MIN_WALL > pr.rf:
            errors.append((
                "Keyway is too deep for the root diameter: its floor corners reach "
                f"{2 * keyway_corner_radius(p):.2f} mm across, which must stay "
                f"{MIN_WALL:g} mm inside the root circle ({2 * pr.rf:.2f} mm); reduce "
                "keyway_depth or keyway_width.",
                ("keyway_depth", "keyway_width")))
    if p.bore_chamfer > 0 and p.bore_chamfer >= p.face_width / 2:
        errors.append(("Bore chamfer must be less than half the face width.",
                       ("bore_chamfer",)))

    if recess_radii(p, pr.rf):
        sides = 2 if p.recess_sides == "both" else 1
        web = p.face_width - sides * p.recess_depth
        if web < MIN_WALL:
            errors.append((f"Recesses leave a {web:.2f} mm web; reduce the depth.",
                           ("recess_depth",)))

    # --- body cutout ---
    # With two or more patterns set, neither pattern's own rules below run: the part
    # cannot exist as drawn (REQ-one-cutout-pattern), and one sentence says why instead
    # of every per-pattern rule firing on fields that make no sense set together.
    chosen = [(name, value) for name, value in
              (("spoke_count", p.spoke_count), ("hole_count", p.hole_count),
               ("hex_cell", p.hex_cell))
              if value > 0]
    if len(chosen) >= 2:
        errors.append((
            "Only one body cutout pattern per part: "
            f"{_listed([f'{n} ({v:g})' for n, v in chosen])} are "
            f"{'both' if len(chosen) == 2 else 'all'} set; keep one and set the "
            "others to 0.",
            tuple(n for n, _ in chosen)))
    elif p.spoke_count > 0:
        # D-15: the half-set rule runs first -- with a dimension still 0 there is no
        # geometry to measure a wall against, so the rules below never fire on a
        # half-set pattern (they would misname the zero field as a wall breach).
        zero = [f for f in ("hub_d", "rim_wall", "spoke_width") if getattr(p, f) == 0]
        if zero:
            errors.append((
                f"Spoke arms need {_listed(zero)}: set "
                f"{'it' if len(zero) == 1 else 'them'} above 0, or set spoke_count "
                "to 0.",
                tuple(zero)))
        else:
            # 11-01-SUMMARY.md: the human kept the spoke-arm wall rule (Flagged
            # Assumption A1) -- 0 < spoke_width < MIN_WALL is refused like every other
            # wall in the part, not silently accepted as thin-but-printable.
            if _under_min_wall(p.spoke_width):
                errors.append((
                    f"Spoke arms {p.spoke_width:g} mm wide are thinner than the "
                    f"{MIN_WALL:g} mm every wall in the part keeps; increase "
                    "spoke_width.",
                    ("spoke_width",)))
            if _under_min_wall(p.rim_wall):
                errors.append((
                    f"The rim wall ({p.rim_wall:g} mm) is thinner than {MIN_WALL:g} "
                    "mm; increase rim_wall.",
                    ("rim_wall",)))
            # D-17: naming only the cutout's own field -- the bore is the fit to the
            # shaft, and the sentence quotes the mouth so the cause stays visible.
            mouth = bore_mouth_limit(p)
            if _under_min_wall(p.hub_d / 2 - mouth):
                errors.append((
                    f"The spoke hub is too small for the bore: hub_d ({p.hub_d:g} mm) "
                    f"must be at least {2 * (mouth + MIN_WALL):.2f} mm, {MIN_WALL:g} "
                    f"mm outside the bore mouth ({2 * mouth:.2f} mm across); increase "
                    "hub_d.",
                    ("hub_d",)))
            ann = pr.rf - p.rim_wall - p.hub_d / 2
            if _under_min_wall(ann):
                errors.append((
                    f"Spokes leave no room to cut: between the hub ({p.hub_d:g} mm) "
                    f"and the rim wall ({2 * (pr.rf - p.rim_wall):.2f} mm across) "
                    f"there is {max(ann, 0.0):.3f} mm, which must be at least "
                    f"{MIN_WALL:g} mm; reduce hub_d or rim_wall.",
                    ("hub_d", "rim_wall")))
            # D-16: the opening exists only where the annulus does; the planning probe
            # built openings down to 0.01 mm, so this is the part's own MIN_WALL rule,
            # not a kernel limit.
            elif _under_min_wall(spoke_opening(p)):
                errors.append((
                    "Spoke arms leave too little room between them at the hub: "
                    f"{p.spoke_count} arms of {p.spoke_width:g} mm on a "
                    f"{p.hub_d:g} mm hub leave {max(spoke_opening(p), 0.0):.3f} mm, "
                    f"which must be at least {MIN_WALL:g} mm; reduce spoke_count or "
                    "spoke_width, or increase hub_d.",
                    ("hub_d", "spoke_count", "spoke_width")))
    elif p.hole_count > 0:
        # D-15: the half-set rule runs first -- with a dimension still 0 there is no
        # geometry to measure a wall against, so the three rules below never fire on a
        # half-set pattern (they would misname the zero field as a wall breach).
        zero = [f for f in ("hole_circle_d", "hole_d") if getattr(p, f) == 0]
        if zero:
            errors.append((
                f"Lightening holes need {' and '.join(zero)}: set "
                f"{'it' if len(zero) == 1 else 'them'} above 0, or set hole_count to 0.",
                tuple(zero)))
        else:
            # None of the three implies another: a hole can be too close to the bore, to
            # the root, or to its neighbour independently, so all three run every time
            # (not elif) -- a hole wider than the web breaches both the hub and rim at
            # once and must say so twice (REQ-cutout-conflicts-refused-early).
            inner = p.hole_circle_d / 2 - p.hole_d / 2
            outer = p.hole_circle_d / 2 + p.hole_d / 2
            if _under_min_wall(inner - bore_mouth_limit(p)):
                errors.append((
                    "Lightening holes come too close to the bore: their inner edges "
                    f"are {2 * inner:.2f} mm across and must stay {MIN_WALL:g} mm "
                    f"outside the bore mouth ({2 * bore_mouth_limit(p):.2f} mm "
                    "across); increase hole_circle_d or reduce hole_d.",
                    ("hole_circle_d", "hole_d")))
            if _under_min_wall(pr.rf - outer):
                errors.append((
                    "Lightening holes come too close to the root circle: their outer "
                    f"edges are {2 * outer:.2f} mm across and must stay {MIN_WALL:g} "
                    f"mm inside the root circle ({2 * pr.rf:.2f} mm); reduce "
                    "hole_circle_d or hole_d.",
                    ("hole_circle_d", "hole_d")))
            # D-16: the planning probe built holes 0.001 mm apart, and tangent to the
            # recess walls, and every one was one valid solid -- these rules are the
            # part's own MIN_WALL, not a kernel limit (11-07 pins it against the kernel).
            if p.hole_count >= 2 and _under_min_wall(hole_gap(p)):
                errors.append((
                    "Lightening holes are too close to each other: "
                    f"{p.hole_count} holes of {p.hole_d:g} mm on a {p.hole_circle_d:g} "
                    f"mm circle leave {max(hole_gap(p), 0.0):.3f} mm between "
                    f"neighbours, which must be at least {MIN_WALL:g} mm; reduce "
                    "hole_count or hole_d, or increase hole_circle_d.",
                    ("hole_circle_d", "hole_count", "hole_d")))
    elif p.hex_cell > 0:
        # D-15: the half-set rule runs first -- with hex_wall still 0 there is no wall
        # to size a lattice against, so the rules below never fire on a half-set
        # honeycomb; each presupposes the one before it, so this is an if/elif chain
        # rather than three independent rules (08's shape).
        if p.hex_wall == 0:
            errors.append((
                "A honeycomb needs hex_wall: set it to at least 0.4 mm, or set "
                "hex_cell to 0.",
                ("hex_wall",)))
        elif _under_min_wall(p.hex_wall):
            errors.append((
                f"The honeycomb wall ({p.hex_wall:g} mm) is thinner than "
                f"{MIN_WALL:g} mm; increase hex_wall.",
                ("hex_wall",)))
        elif round(p.hex_cell, 3) == 0:
            errors.append((
                f"Honeycomb cell {p.hex_cell:g} mm "
                "is below the 0.001 mm resolution cells are cut at: set hex_cell to "
                "0 for no honeycomb, or larger.",
                ("hex_cell",)))
        else:
            size, cells = hex_cells(p, pr.rf)
            if not cells:
                inner = bore_mouth_limit(p) + p.hex_wall
                outer = pr.rf - p.hex_wall
                errors.append((
                    f"No whole honeycomb cell fits between {inner:.2f} and "
                    f"{outer:.2f} mm from the axis (hex_wall outside the bore mouth "
                    f"and inside the root circle): a {size:g} mm cell reaches "
                    f"{size / math.sqrt(3):.2f} mm from its centre; reduce hex_cell "
                    "or hex_wall.",
                    ("hex_cell", "hex_wall")))
        # No hub or rim breach rule exists here: D-09's boundaries (hex_wall outside
        # the bore mouth, inside the root circle) and D-07's whole-cell test keep
        # every cell inside by construction -- a cell that would breach either is
        # simply never cut (D-17).
    return errors


def span_measurement(p: GearParams) -> tuple[int, float]:
    """Base tangent length (Wildhaber span) over k teeth, nominal (zero backlash)."""
    a = math.radians(p.pressure_angle)
    z, m, x = p.teeth, p.module, p.profile_shift
    k = max(1, round(z * p.pressure_angle / 180 + 0.5 + 2 * x * math.tan(a) / math.pi))
    w = m * math.cos(a) * (math.pi * (k - 0.5) + z * inv(a)) + 2 * x * m * math.sin(a)
    return k, w


class DerivedDimensions(BaseModel):
    """The one document `/api/info`, `spur info` and the web UI all print.

    Every key is always present. `None` means a value does not apply (no bore, no
    recess, no mate asked about) or cannot be computed honestly (a pair that cannot
    mesh) -- never a plausible number in its place (L08).
    """

    model_config = ConfigDict(frozen=True)

    pitch_d: float = Field(description="Pitch circle diameter.",
                           json_schema_extra={"unit": "mm"})
    tip_d: float = Field(description="Tip (outside) diameter.",
                         json_schema_extra={"unit": "mm"})
    root_d: float = Field(description="Root diameter.",
                          json_schema_extra={"unit": "mm"})
    base_d: float = Field(description="Base circle diameter.",
                          json_schema_extra={"unit": "mm"})
    caliper_over_tips: float = Field(
        description="Caliper reading across the tips; short of tip_d for an odd tooth count.",
        json_schema_extra={"unit": "mm"})
    tip_thickness: float = Field(description="Tooth thickness at the tip, as an arc.",
                                 json_schema_extra={"unit": "mm"})
    root_thickness: float | None = Field(
        description="Tooth thickness on the root circle, as an arc; null where the "
                    "hob-cut (trochoid) root applies.",
        json_schema_extra={"unit": "mm"})
    root_gap: float | None = Field(
        description="Gap between teeth on the root circle, as an arc; null where the "
                    "hob-cut (trochoid) root applies.",
        json_schema_extra={"unit": "mm"})
    root_fillet: float = Field(
        description="Root fillet radius actually used: with the radial root, the request "
                    "capped to the tooth gap; with the trochoid root, the hob's tip "
                    "radius, capped to the largest that leaves the cutter a tip land.",
        json_schema_extra={"unit": "mm"})
    tip_chamfer_effective: float | None = Field(
        description="Tip chamfer actually cut on the tooth-tip edges at both faces, "
                    "after the cap; null with no tip chamfer.",
        json_schema_extra={"unit": "mm"})
    span_teeth: int = Field(description="Number of teeth the span measurement is taken over.")
    span: float = Field(
        description="Span (Wildhaber) measurement over span_teeth teeth, at zero backlash.",
        json_schema_extra={"unit": "mm"})
    bore_effective: float | None = Field(
        description="Bore diameter including print clearance; null with no bore or "
                    "with a hex bore.",
        json_schema_extra={"unit": "mm"})
    hex_across_flats: float | None = Field(
        description="Hex bore across flats including print clearance, what calipers "
                    "read between two flats; null with no hex bore.",
        json_schema_extra={"unit": "mm"})
    hex_across_corners: float | None = Field(
        description="Hex bore across corners including print clearance, what calipers "
                    "read between two opposite corners; null with no hex bore.",
        json_schema_extra={"unit": "mm"})
    keyway_floor_to_wall: float | None = Field(
        description="Keyway floor to the opposite bore wall, including print "
                    "clearance: what a pin and calipers read across the bore through "
                    "the keyway; null with no keyway.",
        json_schema_extra={"unit": "mm"})
    keyway_width_effective: float | None = Field(
        description="Keyway width including print clearance, what calipers read "
                    "across the slot; null with no keyway.",
        json_schema_extra={"unit": "mm"})
    recess_id: float | None = Field(
        description="Face recess inner diameter; null with no recess.",
        json_schema_extra={"unit": "mm"})
    recess_od: float | None = Field(
        description="Face recess outer diameter; null with no recess.",
        json_schema_extra={"unit": "mm"})
    recess_fillet: float | None = Field(
        description="Recess floor fillet radius actually used; null with no recess.",
        json_schema_extra={"unit": "mm"})
    web: float | None = Field(
        description="Thickness left between the recesses; null with no recess.",
        json_schema_extra={"unit": "mm"})
    cutout_hub_wall: float | None = Field(
        description="Thinnest wall left between the body cutout and the bore, measured "
                    "from the farthest point of the chamfered bore mouth (a hex bore's "
                    "corners, a keyway's floor corners): exact for a round or D-flat "
                    "bore, a lower bound where a cutout faces a flat; null with no "
                    "cutout.",
        json_schema_extra={"unit": "mm"})
    cutout_rim_wall: float | None = Field(
        description="Thinnest wall left between the body cutout and the root circle; "
                    "null with no cutout.",
        json_schema_extra={"unit": "mm"})
    spoke_fillet_effective: float | None = Field(
        description="Spoke fillet actually cut at the corners of each cut-out sector, "
                    "after the cap; null with no spokes or no spoke fillet.",
        json_schema_extra={"unit": "mm"})
    hex_cell_effective: float | None = Field(
        description="Honeycomb cell across-flats actually cut, raised from the "
                    "request when the whole-cell count would exceed the cap; null "
                    "with no honeycomb.",
        json_schema_extra={"unit": "mm"})
    hex_cell_count: int | None = Field(
        description="Whole honeycomb cells cut; null with no honeycomb.")
    # A tuple, not a list: pydantic's `frozen=True` locks the attributes, not the objects
    # they hold, so a list here could still be edited in place by any reader of a shared
    # result -- the one field that would make "frozen" a lie (04-REVIEW.md WR-01).
    warnings: tuple[str, ...] = Field(
        description="Sentences about values that were capped, dropped or cannot be computed.")
    mate_teeth: int | None = Field(
        description="Teeth on the mating gear asked about; null when none was.")
    centre_distance: float | None = Field(
        description="Working centre distance to the mate; null with no mate, or when the "
                    "pair cannot mesh.",
        json_schema_extra={"unit": "mm"})


def derive(p: GearParams, mate_teeth: int | None = None,
          mate_shift: float = 0.0) -> DerivedDimensions:
    """Derived dimensions plus the numbers you'd measure on a real gear to verify them.

    With `mate_teeth` it also reports the working centre distance to that gear, or a
    warning and `None` when the pair cannot mesh. Decided here, once, rather than in
    the API and the CLI separately: an impossible pair is a warning on an otherwise
    fine gear, not an error and not a number (L08).

    Per-call cost, re-measured 2026-10-08 (`.venv/bin/python -m timeit -r 5 -s "from
    spur.calc import derive; from spur.params import GearParams; p=GearParams()"
    "derive(p)"`, best of 5, default GearParams, Apple M2 Max, Python 3.12.13): 14.7
    usec at a 1-minute load of 14.4 (bench/RESULTS.md, "Trochoid maths (Phase 18)",
    "Per-call cost"). The figure moves with the host: the same call read 14.5 usec at
    load 14.3 on 2026-10-07 and 20.4 usec at about 6.8, so quote it with its load and
    date. History, when first measured: 9.19 usec before this model, 11.5 usec after --
    validating the frozen model on construction cost about 2.3 usec, negligible next
    to an HTTP round trip and well inside the module docstring's "fast enough to run
    on every keystroke" claim (measured, not assumed -- CLAUDE.md).

    With the `root_mode` call this function now makes (19-04), re-measured 2026-10-09 by
    the same command on an Apple M5 Max, Python 3.12.15, 1-minute load 2.75 (a different
    host from the figures above, so not a delta against them): 10.3 usec for the default
    gear and 29.6 usec with `root_shape="trochoid"`, which solves the curve once.
    """
    pr = profile(p)
    tip, root, gap = _tooth(pr)
    k, w = span_measurement(p)
    odd = p.teeth % 2 == 1
    over_tips = 2 * pr.ra * (math.cos(math.pi / (2 * p.teeth)) if odd else 1.0)

    # One answer to "which root is built", asked once and read below, exactly as
    # model._build reads it (19 D-01; PITFALLS 1: three predicates is how a number gets
    # printed for a part that was built another way).
    rm = root_mode(p, pr, requested=p.root_shape, rho=p.root_fillet)

    warnings: list[str] = []
    if tip < MIN_TIP_FDM:
        warnings.append(f"Tip is only {tip:.2f} mm wide; FDM needs about {MIN_TIP_FDM} mm.")
    if rm.curve is not None and rm.cutter is not None:
        # The hob's root: the printed tip radius is the one the cutter used, the cap
        # sentence comes from root_warnings below, and there is neither a gap to cap
        # to nor a straight lead-in chord to measure (L08).
        rfil = rm.cutter.rho
    else:
        rfil = root_fillet(p)
        if rfil < p.root_fillet:
            warnings.append(f"Root fillet reduced to {rfil:.2f} mm to fit the tooth gap.")
        h = spline_start(pr, rfil) - pr.r
        if round(h, 3) > 0:
            # Compared at the 3 dp it prints, never the raw float: a crossing can sit
            # arbitrarily close to zero and "0.000 mm above" must never print (the
            # tip-chamfer branch's rule below, 10-REVIEW.md CR-01). The cause clause is
            # true on every firing: the chord ends at r + 2*fillet - (1.25 - x)*m, capped
            # halfway up the tooth at r + (x - 0.125)*m, so a positive height needs the
            # fillet over half the dedendum. 0 of 44 pre-v0.2 fixture records cross
            # (counted 2026-10-02), so no pinned warnings tuple moves (L26).
            warnings.append(f"The flank starts with a straight chord reaching {h:.3f} mm "
                            "above the pitch circle, where it deviates from the involute: "
                            "the root fillet is larger than half the dedendum.")
    # Empty for every gear nobody asked about, so no fixture tuple moves; after the
    # radial sentences so a refused request reads the sentence that explains it next to
    # the radial root it fell back to.
    warnings.extend(root_warnings(rm))
    if rm.curve is not None:
        warnings.append(_ROOT_SENTENCES["thickness not printed"])
    tch = tip_chamfer_effective(p, rm)
    if tch < round(p.tip_chamfer, 3):
        # A limit only actually binds when it sits below the request at the 0.001 mm
        # resolution the chamfer is cut at (tip_chamfer_effective rounds to 3 dp;
        # model.py cuts exactly that value, L08) -- this is the original comparison
        # from before WR-01's fix, restored. It keeps a limit's own float residue
        # silent (0.1999999999999993 at 200 teeth, module 0.2 rounds to the same 0.2
        # the request carries) and it keeps an ordinary request like 0.1234 -> 0.123
        # silent too: that rounding is the model's print resolution, shared with
        # root_fillet, recess_fillet and bore_chamfer, not a reduction -- attributing
        # it to tip_chamfer_limit's reason text was a false cause (10-REVIEW.md CR-01).
        warnings.append(f"Tip chamfer reduced to {tch:g} mm {tip_chamfer_limit(p, rm)[1]}.")
    elif p.tip_chamfer > 0 and tch == 0.0:
        # The one rounding case where the built part actually differs from the
        # request: a chamfer was asked for and none was cut. A parameter the user set
        # must never silently change the part (CLAUDE.md), so this warns -- and names
        # the true cause (print resolution), never a limit that was nowhere close to
        # binding (10-REVIEW.md WR-01/CR-01). tch == 0.0 is exact: tip_chamfer_effective
        # already rounded it, so no tolerance is needed.
        warnings.append(f"Tip chamfer {p.tip_chamfer:g} mm is below the 0.001 mm resolution "
                        "it is cut at and was not cut.")
    z_min = 2 * (1 - p.profile_shift) / math.sin(pr.alpha) ** 2
    # True only while the part really has the radial root: a refused trochoid request
    # still builds it, so the sentence stays; a trochoid part gets no undercut sentence
    # until 19-06 restates it for the cutter that cut it.
    if rm.mode == "radial" and p.teeth < z_min:
        warnings.append(f"Below {z_min:.1f} teeth a cut gear would be undercut; "
                        "this model uses a radial root instead.")

    if p.bore_hex > 0:
        # D-02: a hex bore replaces the round profile (D-01); this is the one place
        # that says so, naming only the fields the user set away from 0.
        ignored = [f"{name} ({value:g} mm)" for name, value in
                  (("bore_d", p.bore_d), ("bore_flat", p.bore_flat)) if value > 0]
        if ignored:
            warnings.append(
                f"Hex bore replaces the round profile: {' and '.join(ignored)} "
                f"{'are' if len(ignored) > 1 else 'is'} ignored.")
    else:
        # D-12 refuses only at the measured kernel contact (ROOT_CONTACT), 400 million
        # times tighter than MIN_WALL, so a wall a few hundredths of a mm thick builds
        # with no error -- unlike every other bore-vs-root rule in this file, which
        # refuses at MIN_WALL itself. Warn instead of refusing: the boundary stays put
        # (09-REVIEW.md WR-01, L05), this only surfaces what check() already let through.
        wall_gap = pr.rf - (bore_radius(p) + p.bore_chamfer)
        if p.bore_d > 0 and 0 <= wall_gap < MIN_WALL:
            warnings.append(
                f"Bore chamfer leaves only {wall_gap:.2f} mm of wall to the root "
                f"circle, under the {MIN_WALL:g} mm this design holds everywhere else; "
                "reduce bore_chamfer or bore_d for more margin.")

    rr = recess_radii(p, pr.rf)
    sides = {"both": 2, "top": 1, "bottom": 1}.get(p.recess_sides, 0)
    wanted_recess = p.recess_sides != "none" and p.recess_depth > 0 and p.recess_width > 0
    rec_fil = recess_fillet(p, pr.rf)
    if rr:
        if rr[1] - rr[0] < p.recess_width - 1e-9:
            warnings.append(f"Recess narrowed to {rr[1] - rr[0]:.2f} mm to fit between "
                            "the bore wall and the tooth rim.")
        if rec_fil < p.recess_fillet:
            warnings.append(f"Recess fillet reduced to {rec_fil:.2f} mm to fit the groove.")
    elif wanted_recess:
        warnings.append("No room for a face recess between the bore wall and the tooth "
                        "rim; it was left out.")

    # D-06: only actually binds with spokes on and a fillet requested -- the same
    # shape as the tip-chamfer warning above, including the sub-print-precision branch
    # (10-REVIEW.md WR-01/CR-01's rule, applied here to the spoke fillet's own 0.001 mm
    # cut resolution).
    sfe = spoke_fillet_effective(p) if p.spoke_count > 0 and p.spoke_fillet > 0 else None
    if sfe is not None:
        if sfe < round(p.spoke_fillet, 3):
            warnings.append(f"Spoke fillet reduced to {sfe:g} mm {spoke_fillet_limit(p)[1]}.")
        elif sfe == 0.0:
            warnings.append(f"Spoke fillet {p.spoke_fillet:g} mm is below the 0.001 mm "
                            "resolution it is cut at and was not cut.")

    if p.spoke_count == 0:
        # D-15: spoke_count 0 (the default) builds nothing regardless of the other
        # four spoke fields, exactly like the hex bore ignoring bore_d/bore_flat above
        # -- the same sentence shape, naming only the fields the user actually set.
        ignored = [f"{name} ({value:g} mm)" for name, value in
                  (("spoke_width", p.spoke_width), ("hub_d", p.hub_d),
                   ("rim_wall", p.rim_wall), ("spoke_fillet", p.spoke_fillet))
                  if value > 0]
        if ignored:
            warnings.append(
                f"No spoke arms with spoke_count 0: {_listed(ignored)} "
                f"{'are' if len(ignored) > 1 else 'is'} ignored.")

    if p.hole_count == 0:
        # D-15: hole_count 0 (the default) builds nothing regardless of hole_d/
        # hole_circle_d, exactly like the hex bore ignoring bore_d/bore_flat above --
        # the same sentence shape, naming only the fields the user actually set.
        ignored = [f"{name} ({value:g} mm)" for name, value in
                  (("hole_d", p.hole_d), ("hole_circle_d", p.hole_circle_d)) if value > 0]
        if ignored:
            warnings.append(
                f"No lightening holes with hole_count 0: {' and '.join(ignored)} "
                f"{'are' if len(ignored) > 1 else 'is'} ignored.")

    if p.hex_cell > 0:
        size, cells = hex_cells(p, pr.rf)
        if size > round(p.hex_cell, 3):
            warnings.append(
                f"Honeycomb cells enlarged from {p.hex_cell:g} mm to {size:g} mm "
                f"across flats to keep the count within the {HEX_CELL_CAP}-cell "
                "limit.")
        hce, hcc = size, len(cells)
    else:
        hce, hcc = None, None
        if p.hex_wall > 0:
            # D-15: hex_wall set with hex_cell 0 (the default) builds no honeycomb --
            # the same sentence shape as the spoke/hole ignored-dimensions warnings
            # above, naming the one field the user set away from 0.
            warnings.append(
                f"No honeycomb with hex_cell 0: hex_wall ({p.hex_wall:g} mm) is "
                "ignored.")

    walls = cutout_walls(p, pr.rf)

    # The mate is folded into this one document rather than patched on afterward
    # (D-02): a single construction site means a derive() bug that produces the wrong
    # shape fails loudly instead of quietly matching dict[str, Any] (D-09).
    aw = centre_distance(p, mate_teeth, mate_shift) if mate_teeth is not None else None
    if mate_teeth is not None and aw is None:
        warnings.append(f"A {mate_teeth}-tooth gear cannot mesh with this one at any "
                        f"centre distance: a total profile shift of "
                        f"{p.profile_shift + mate_shift:+g} is too negative for "
                        f"{p.teeth + mate_teeth} teeth.")

    def r3(v: float) -> float:
        return round(v, 3)

    return DerivedDimensions(
        pitch_d=r3(2 * pr.r),
        tip_d=r3(2 * pr.ra),
        root_d=r3(2 * pr.rf),
        base_d=r3(2 * pr.rb),
        caliper_over_tips=r3(over_tips),
        tip_thickness=r3(tip),
        # Null under the hob's root: the tooth's thickness there changes too fast with
        # radius to give one number someone could cut to (D-03, L08).
        root_thickness=None if rm.curve is not None else r3(root),
        root_gap=None if rm.curve is not None else r3(gap),
        # rfil and rec_fil already round(..., 3) internally (root_fillet(),
        # recess_fillet()), so this changes no value on the wire today -- but every
        # length is rounded once, at construction (D-10), so the rule stays true if
        # either helper's rounding ever changes.
        root_fillet=r3(rfil),
        tip_chamfer_effective=r3(tch) if p.tip_chamfer > 0 else None,
        span_teeth=k,
        span=r3(w),
        bore_effective=r3(2 * bore_radius(p)) if p.bore_d > 0 and p.bore_hex == 0 else None,
        hex_across_flats=r3(hex_across_flats(p)) if p.bore_hex > 0 else None,
        hex_across_corners=r3(2 * bore_rim_limit(p)) if p.bore_hex > 0 else None,
        # The opposite wall is always the round wall, because the keyway sits a quarter
        # turn from the D-flat (D-01) -- floor-to-wall is bore_effective + keyway_depth
        # whether or not a flat exists.
        keyway_floor_to_wall=(r3(2 * bore_radius(p) + p.keyway_depth)
                              if keyway_corner_radius(p) > 0 else None),
        keyway_width_effective=(r3(keyway_width_effective(p))
                                if keyway_corner_radius(p) > 0 else None),
        recess_id=r3(2 * rr[0]) if rr else None,
        recess_od=r3(2 * rr[1]) if rr else None,
        recess_fillet=r3(rec_fil) if rr else None,
        web=r3(p.face_width - sides * p.recess_depth) if rr else None,
        cutout_hub_wall=r3(walls[0]) if walls else None,
        cutout_rim_wall=r3(walls[1]) if walls else None,
        spoke_fillet_effective=r3(sfe) if sfe is not None else None,
        hex_cell_effective=r3(hce) if hce is not None else None,
        hex_cell_count=hcc,
        warnings=tuple(warnings),
        mate_teeth=mate_teeth,
        centre_distance=None if aw is None else r3(aw),
    )


def _involute_angle(target: float) -> float:
    """Inverse of inv() on (0, pi/2): the angle whose involute function is `target`.

    Bisection rather than Newton: inv is monotonic here, 60 halvings reach full double
    precision, and there is no starting guess that can send it outside the bracket.
    """
    lo, hi = 1e-12, math.radians(89.0)
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if inv(mid) < target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def centre_distance(p: GearParams, mate_teeth: int,
                    mate_shift: float = 0.0) -> float | None:
    """Working centre distance to a mating gear of the same module and pressure angle,
    or None when the pair cannot mesh at any centre distance.

    Solves inv(aw) = inv(a) + 2 tan(a) (x1 + x2) / (z1 + z2) for the working pressure
    angle aw. inv is non-negative on (0, pi/2), so a total profile shift negative enough
    drives the right-hand side below zero and no such angle exists -- the teeth would
    have to interfere. Saying so is the only honest answer; the number is not merely
    imprecise, it does not exist.
    """
    a = math.radians(p.pressure_angle)
    z1, z2 = p.teeth, mate_teeth
    target = inv(a) + 2 * math.tan(a) * (p.profile_shift + mate_shift) / (z1 + z2)
    if not 0 < target < inv(math.radians(89.0)):
        return None
    aw = _involute_angle(target)
    return p.module * (z1 + z2) / 2 * math.cos(a) / math.cos(aw)


# --- The hob's trochoid root (Phase 18) -------------------------------------------------
# Below the base circle a hobbed gear's root is not the radial lead-in plus fillet the
# model builds today (L09, L10) but the envelope of the hob's rounded tip as the rack
# rolls on the pitch circle. Everything here is pure maths over the rack; Phase 19's
# `root_shape` field reaches it only through `root_mode`, so a gear that does not ask
# for the hob's root sees no number move.

RootShape = Literal["radial", "trochoid"]
RootReason = Literal["not requested", "nothing radial to replace", "tip land gone",
                     "bracket degenerate", "curve invalid", "tooth severed"]
_Join = Literal["tangent", "crossing"]


@dataclass(frozen=True)
class Cutter:
    """The basic rack that cuts one gear, defined once (D-06): every function below reads
    this record, never `1.25` or `rf = r - d` again."""
    pr: Profile             # the gear it cuts
    x: float                # profile shift, modules: the rack's displacement
    d: float                # tip depth below the pitch circle, mm
    e: float                # cutter tooth width on the rolling line, mm; backlash thickens it
    a0: float               # tip-land half-width with a sharp corner, mm; negative: no land
    rho_max: float          # largest tip radius that keeps a land, mm, unrounded
    rho_requested: float    # tip radius asked for, mm
    rho: float              # tip radius used, mm: the request, or the cap floored to 3 dp
    w_c: float              # corner-centre height above the rolling line, mm; negative
    # for an ordinary cutter, zero when the tip radius equals the tip depth
    a: float                # tip-land half-width with the tip radius used, mm
    xi: float               # roll of the flank foot along the line of action, mm;
    # the gear is undercut where this is negative


def cutter(p: GearParams, rho: float) -> Cutter:
    """The basic rack for `p` with tip radius `rho` mm (D-06, D-07).

    The dedendum comes from `_dedendum`, the same expression that sets `rf`; the tip
    radius is an explicit millimetre argument (nothing here reads `p.root_fillet` as
    rho); backlash thickens the cutter tooth (a cutter without it leaves a 0.046 mm
    step against `Profile.half_angle` on the default gear, PITFALLS 3); profile shift
    displaces the rack, which is why the cap below does not depend on it.

    A tip radius above the largest that keeps a flat tip land is cut to that largest
    value floored to 3 dp. Floored, never rounded to nearest: at module 0.5, 15 degrees,
    12 teeth, backlash 0 the cap is 0.29353 mm, round() gives 0.294 and the land comes
    out 3.6e-4 mm negative -- a legal gear refused as "no tip land" (18-RESEARCH F3).
    Flooring also makes the used and the printed radius one number (L08).

    A tip radius that is not a finite, non-negative millimetre value raises ValueError.
    `rho` is not a `GearParams` field in this phase (D-07), so until Phase 19's field
    validates it once at the boundary this is the one place that guards the internal
    contract. It is a ValueError and not a new `RootReason`: no user can reach the state,
    so there is no sentence to write for it.
    """
    # Before any arithmetic: a NaN fails `rho <= rho_max` below, so it would be trimmed to
    # the cap, and `rho < rho_requested` in root_warnings reads False against NaN, so the
    # part would change with no sentence (measured on 12 teeth, module 1, 20 degrees:
    # mode "trochoid", reason None, no warning). L05, L08, 18-REVIEW WR-02.
    if not math.isfinite(rho) or rho < 0:
        raise ValueError(f"tip radius must be a finite, non-negative millimetre value, got {rho!r}")
    pr = profile(p)
    alpha, m, x = pr.alpha, p.module, p.profile_shift
    d = _dedendum(m, x)
    e = math.pi * m - _pitch_thickness(m, alpha, x, p.backlash)
    a0 = e / 2 - d * math.tan(alpha)
    rho_max = a0 / (1 / math.cos(alpha) - math.tan(alpha))
    used = rho if rho <= rho_max else max(0.0, math.floor(rho_max * 1000) / 1000)
    # The land half-width with the used radius is the same e/2 + w_c*tan(alpha) -
    # rho/cos(alpha), written from a0 so that a request exactly at the cap reads zero
    # and not -1e-17: the cap guarantees used <= rho_max, so the max only absorbs float
    # residue.
    land = max(0.0, a0 + used * (math.tan(alpha) - 1 / math.cos(alpha))) if a0 >= 0 else a0
    xi = pr.r * math.sin(alpha) - (d - used * (1 - math.sin(alpha))) / math.sin(alpha)
    return Cutter(pr=pr, x=x, d=d, e=e, a0=a0, rho_max=rho_max, rho_requested=rho,
                  rho=used, w_c=used - d, a=land, xi=xi)


def undercut_teeth(c: Cutter) -> float:
    """The fewest teeth this cutter generates without undercut, read from the cutter
    that actually cuts (a trimmed tip radius gives the onset of the trimmed cutter, not
    of the one asked for: the number printed must be the number that applies, L08).

    A gear is undercut where `c.xi < 0`, the same sign `_junction` tests first, and
    solving that for the tooth count gives this. It is the cutter's own onset, and a
    different number from the one `derive()` prints today, `2(1 - x)/sin^2(alpha)`: that
    one is the sharp-cornered rack with the full tip depth at 20 degrees only. At module
    1, tip radius 0.38 mm and no shift this reads 30.7909 / 17.0967 / 11.5404 teeth at
    14.5 / 20 / 25 degrees (STACK's table, reproduced 2026-10-08) where the shipped
    formula reads 31.9029 / 17.0973 / 11.1978. The shipped sentence is untouched until
    Phase 19 restates it (REQ-undercut-warning-restated).
    """
    sin_a = math.sin(c.pr.alpha)
    return 2 * (c.d - c.rho * (1 - sin_a)) / (c.pr.m * sin_a ** 2)


def undercut_shift(c: Cutter) -> float:
    """The smallest profile shift that avoids undercut at this cutter's tooth count: the
    shift at which `c.xi` is zero, read from the cutter that cuts like `undercut_teeth`.
    Reads 0.41508 at 10 teeth, module 1, 20 degrees, tip radius 0.38 mm (STACK,
    reproduced 2026-10-08), so a shift of 0.40 is undercut and 0.45 is not.
    """
    return c.x - c.xi * math.sin(c.pr.alpha) / c.pr.m


@dataclass(frozen=True)
class RootCurve:
    """The hob's root below the junction with the involute, root circle first."""
    points: tuple[tuple[float, float], ...]  # (radius mm, half-angle from the tooth
    # centre rad), strictly increasing radius, ROOT_CURVE_POINTS long
    join: _Join  # "tangent": it meets the involute with its direction; "crossing":
    # the gear is undercut and the curve is cut off where it meets the involute
    waist: tuple[float, float]  # (radius mm, half-angle rad) where the half-angle is
    # smallest, refined between the samples: the root's narrowest point, which is half
    # the tooth thickness there, so it is always above zero on a curve that survives


def _trochoid_point(c: Cutter, beta: float) -> tuple[float, float]:
    """The envelope of the cutter's tip arc at contact-normal angle `beta`: the point of
    the arc whose normal passes through the rolling pole, as (radius, half-angle from
    the tooth centre). beta 0 is the root circle, pi/2 - alpha the flank's foot.

    Parametrised by the angle itself, not by the centre path: the textbook
    C + rho*(C - I)/|C - I| gouges 0.70 mm where rho exceeds the tip depth and divides
    by zero where they are equal, and both cases lie inside the allowed box (393 of
    28,957 gears at rho 0.5 mm, 18-RESEARCH F4). This form is one closed expression for
    every rho. It reads `c.pr.rf` itself, never r - d, so the first point is the root
    circle bit for bit.
    """
    phi = (c.a + c.w_c * math.tan(beta)) / c.pr.r
    along_normal = c.pr.rf + c.rho * (1 - math.cos(beta))
    along_line = c.rho * math.sin(beta) - c.w_c * math.tan(beta)
    return (math.hypot(along_normal, along_line),
            math.pi / c.pr.z - (phi + math.atan2(along_line, along_normal)))


def _waist(c: Cutter, betas: list[float],
           points: tuple[tuple[float, float], ...]) -> tuple[float, float]:
    """The point of the curve where the half-angle from the tooth centre is smallest:
    where the two neighbouring spaces' roots come closest to cutting the tooth through
    (D-17), as (radius mm, half-angle rad).

    The smallest sample is refined by 60 golden-section steps of the half-angle between
    that sample's neighbours (clamped to the curve's ends), because 16 samples can miss
    the dip: at 6 teeth, 14.5 degrees, shift -0.5, tip radius 0 the smallest sample reads
    -0.0055 rad and the refined waist -0.0066 (18-RESEARCH). A fixed step count, no
    data-dependent loop (T-18-02); whichever of the sample and the refined point is
    smaller is returned, so refining can only lower the answer.
    """
    i = min(range(len(points)), key=lambda k: points[k][1])
    lo, hi = betas[max(i - 1, 0)], betas[min(i + 1, len(betas) - 1)]
    golden = (math.sqrt(5) - 1) / 2

    def half(beta: float) -> float:
        return _trochoid_point(c, beta)[1]

    c1, c2 = hi - golden * (hi - lo), lo + golden * (hi - lo)
    f1, f2 = half(c1), half(c2)
    for _ in range(60):
        if f1 < f2:
            hi, c2, f2 = c2, c1, f1
            c1 = hi - golden * (hi - lo)
            f1 = half(c1)
        else:
            lo, c1, f1 = c1, c2, f2
            c2 = lo + golden * (hi - lo)
            f2 = half(c2)
    refined = _trochoid_point(c, 0.5 * (lo + hi))
    return min(points[i], refined, key=lambda point: point[1])


def _bisect(f: Callable[[float], float], lo: float, hi: float) -> float:
    """The root of `f` on [lo, hi], which must change sign there; the sign is taken
    from f(lo).

    Bisection, as in `_involute_angle`: `acos(min(1, rb/R))` has a square-root
    singularity at R = rb, so Newton can be thrown out of the bracket from any starting
    guess, while 60 halvings reach full double precision and cannot leave it (L08).
    """
    rising = f(lo) > 0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if (f(mid) > 0) == rising:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def _junction(c: Cutter, eps: float) -> tuple[float, _Join] | None:
    """Where the trochoid hands over to the involute: (the last contact-normal angle,
    how it joins), or None when a bracket the geometry promises cannot be found.

    A gear that is not undercut (xi >= -eps*rb) joins tangent at the flank's foot:
    no root-find at all, and the end point equals `Profile.half_angle` there to float.
    An undercut gear's curve crosses the involute earlier: one bisection finds where
    the curve reaches the base circle, a second where it meets the involute (positive
    gap while the trochoid is inside it). `half_angle` is only ever called at R >= rb.
    """
    beta_end = math.pi / 2 - c.pr.alpha
    if c.xi >= -eps * c.pr.rb:
        return beta_end, "tangent"

    def over_base(beta: float) -> float:
        return _trochoid_point(c, beta)[0] - c.pr.rb

    def inside_involute(beta: float) -> float:
        radius, half = _trochoid_point(c, beta)
        return c.pr.half_angle(radius) - half

    if not over_base(0.0) < 0 < over_base(beta_end):
        return None
    beta_base = _bisect(over_base, 0.0, beta_end)
    if not inside_involute(beta_base) > 0 > inside_involute(beta_end):
        return None
    return _bisect(inside_involute, beta_base, beta_end), "crossing"


def _root_curve(c: Cutter) -> RootCurve | RootReason:
    """The curve, or the named reason there is none; cheap checks first."""
    if c.a0 < 0:
        # Decided on the sharp-corner land, which moves with backlash and module
        # (32.14 degrees at backlash 0, 33.07 at the default gear, 18-RESEARCH F2),
        # never on a pressure-angle constant.
        return "tip land gone"
    junction = _junction(c, TROCHOID_JOIN_EPS)
    if junction is None:
        return "bracket degenerate"
    beta_stop, join = junction
    # Uniform in tan(beta): the roll angle phi is linear in it, which is STACK's
    # "uniform in phi" and stays defined where w_c is zero. The last angle is beta_stop
    # itself, not atan(tan(beta_stop)), so the end point comes from one call.
    s_stop = math.tan(beta_stop)
    n = ROOT_CURVE_POINTS
    betas = [math.atan(s_stop * i / (n - 1)) for i in range(n - 1)] + [beta_stop]
    points = tuple(_trochoid_point(c, beta) for beta in betas)
    pr = c.pr
    # One guard for four structural failures: a radius that stops rising (a loop), one
    # above the tip circle, one past the space centreline, and (undercut only) a point
    # that is not inside the involute before the junction (the bisection found a later
    # root, or the curve runs past it). L08: a refused case is a reason, never a curve
    # that was clipped or healed.
    invalid = (
        not all(lo < hi for (lo, _), (hi, _) in pairwise(points))
        or max(radius for radius, _ in points) > pr.ra
        or max(half for _, half in points) > math.pi / pr.z
        or (join == "crossing" and any(
            radius >= pr.rb and half >= pr.half_angle(radius)
            for radius, half in points[:-1])))
    if invalid:
        return "curve invalid"
    waist = _waist(c, betas, points)
    # A half-angle at or below zero means the neighbouring spaces' roots meet on the
    # tooth's centreline: the hob cuts the tooth through. The analytic root is the
    # fallback and no waist floor is chosen here; a thin positive waist survives and
    # Phase 19 decides how thin is too thin (D-17).
    return "tooth severed" if waist[1] <= 0 else RootCurve(points, join, waist)


def trochoid_root(c: Cutter) -> RootCurve | None:
    """The hob's root for this cutter, or None when no honest curve exists for it.

    None is a refusal, not a clipped or partly sampled curve (D-10, L08): `root_mode`
    is the one place that says why.
    """
    curve = _root_curve(c)
    return curve if isinstance(curve, RootCurve) else None


@dataclass(frozen=True)
class RootMode:
    mode: RootShape                 # what the root is built as
    reason: RootReason | None       # why it stayed radial; None exactly when trochoid
    cutter: Cutter | None           # the cutter asked about; None only when nothing
    # was requested
    curve: RootCurve | None = None  # set exactly when `mode` is "trochoid": the curve the
    # part is built from and the numbers are read from, solved once (18-REVIEW IN-02)


def root_mode(p: GearParams, pr: Profile,
              *, requested: RootShape = "radial", rho: float = 0.0) -> RootMode:
    """The single answer to "does the trochoid root apply to this gear" (D-10).

    `requested` is the user's choice (D-04, amended by D-16: keyword-only, with the
    tip radius `rho` beside it). It owns every refusal and decides them in one fixed
    order, cheapest first:

    1. `not requested`: nothing asked, so not even the cutter is built.
    2. `nothing radial to replace`: `pr.rb <= pr.rf` (D-02). The involute already
       reaches the root circle, so there is no radial lead-in to replace; `<=` because
       where they are equal `Profile.r_start` is the base circle either way. This is a
       closed-form test and goes before the generator because undercut implies
       `rb > rf` (18-RESEARCH F9: proved, and checked over 556,920 combinations), so
       the edge of the trochoid region is never hidden behind a generator failure.
    3. `tip land gone`: the cutter has no flat tip at this pressure angle.
    4. `bracket degenerate`: the junction with the involute cannot be solved.
    5. `curve invalid`: a loop, a point past the tip circle, past the space
       centreline or past the junction.
    6. `tooth severed`: the curve's narrowest half-angle is at or below zero (D-17).

    Every sentence for these comes from `root_warnings`. `derive()`, `model._build` and
    `tip_chamfer_limit` each call it once, with `requested=p.root_shape` and the tip
    radius `rho=p.root_fillet` (19 D-01), so a gear nobody asked about reads radial with
    "not requested" and the pre-v0.2 fixture cannot move. The default `rho = 0.0` is the
    sharp cutter, legal, and ignored whenever nothing is requested; it stays for callers
    that request nothing.
    """
    if requested != "trochoid":
        return RootMode("radial", "not requested", None)
    c = cutter(p, rho)
    if pr.rb <= pr.rf:
        return RootMode("radial", "nothing radial to replace", c)
    curve = _root_curve(c)
    if isinstance(curve, RootCurve):
        return RootMode("trochoid", None, c, curve)
    return RootMode("radial", curve, c)


# One sentence per refusal reason, plus the cap; all filled from the same keyword values
# so the lookup in root_warnings has no branches. These are the sentences `derive()` now
# carries; tests capture them from derive(), never type them (L33).
_ROOT_SENTENCES: dict[str, str] = {
    "nothing radial to replace":
        "No radial root to replace on this gear (base circle {rb:.3f} mm, root circle "
        "{rf:.3f} mm): the trochoid root request is ignored.",
    "tip land gone":
        "The cutter has no tip land at a {alpha:g} degree pressure angle with this module "
        "and backlash: no trochoid root is computed and the analytic root is used.",
    "bracket degenerate":
        "The trochoid root's junction with the involute could not be solved for this "
        "gear: the analytic root is used.",
    "curve invalid":
        "The trochoid root for this gear loops, leaves the tooth space or runs past its "
        "junction with the involute: the analytic root is used.",
    "tooth severed":
        "The trochoid roots of the two neighbouring tooth spaces cut this tooth through: "
        "the analytic root is used.",
    # Not a refusal and not placeholder-filled: derive() prints it on every trochoid gear,
    # where root_thickness and root_gap are null. Measured 2026-10-09 on the default gear
    # (tip radius 0.5 mm): the tooth is 4.532 mm thick on the arc at rf + 0.00175 mm and
    # 3.405 mm at rf + 0.525 mm (0.3 module), so any one radius would be a number somebody
    # cuts to by mistake. (FEATURES quoted 4.68 and 3.51; this is the reproduction.)
    "thickness not printed":
        "root_thickness and root_gap are not printed with the hob-cut root: the tooth's "
        "thickness changes too fast with radius near the root circle to give one honest "
        "number there.",
    "rho capped":
        "Cutter tip radius reduced to {rho:.3f} mm, the largest that leaves the cutter a "
        "tip land at this pressure angle and backlash.",
}


def root_warnings(rm: RootMode) -> tuple[str, ...]:
    """The warning sentences for a root-mode answer, from the one place every trochoid
    sentence comes from (D-10, L33): none when nothing was requested, the reason's
    sentence for a refusal, the cap sentence when a requested tip radius was trimmed.

    The cap sentence prints the radius the curve was generated with, which is already
    floored to 3 dp, so the printed and the used number are one float (L08).
    """
    c = rm.cutter
    if c is None:
        return ()
    values = {"rb": c.pr.rb, "rf": c.pr.rf, "alpha": math.degrees(c.pr.alpha), "rho": c.rho}
    if rm.reason is not None:
        return (_ROOT_SENTENCES[rm.reason].format(**values),)
    if c.rho < c.rho_requested:
        return (_ROOT_SENTENCES["rho capped"].format(**values),)
    return ()
