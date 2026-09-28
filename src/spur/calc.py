"""Pure-math gear geometry (no CAD kernel): derived dimensions, measurement aids,
and feasibility checks. Fast enough to run on every keystroke in the UI."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
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
# this sub-2e-8 mm residual band is orders of magnitude below the field's 0.05 mm step
# and unreachable through the UI's own stepped widgets. It is NOT proven unreachable in
# general: `step` in params.py's _f() is JSON-schema metadata only, not a pydantic
# `multiple_of`, so an API/CLI caller sending an ordinary 8-9 significant-figure bore_d
# can land inside this band (09-REVIEW.md WR-02) -- reproduced live at bore_d
# 24.724999998 (19T, m1.75, chamfer 2, round): check() accepts it (gap
# 1.000000082740371e-09 > ROOT_CONTACT) and the kernel still raises BuildError, pinned
# by test_model.py's test_the_kernel_can_fail_inside_the_root_contact_residual_band.


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


def profile(p: GearParams, backlash: float | None = None) -> Profile:
    a = math.radians(p.pressure_angle)
    m, z, x = p.module, p.teeth, p.profile_shift
    bl = p.backlash if backlash is None else backlash
    r = m * z / 2
    s = m * (math.pi / 2 + 2 * x * math.tan(a)) - bl
    return Profile(z=z, m=m, alpha=a, r=r, rb=r * math.cos(a), ra=r + m * (1 + x),
                   rf=r - m * (1.25 - x), psi_p=s / (2 * r))


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


def recess_fillet(p: GearParams, rf: float) -> float:
    """Recess floor fillet actually used: the requested radius, capped to the groove.

    Both floor corners carry the fillet, so it cannot exceed half the groove width.
    """
    rr = recess_radii(p, rf)
    if not rr or p.recess_fillet <= 0:
        return 0.0
    width = rr[1] - rr[0]
    return round(min(p.recess_fillet, 0.45 * width, 0.45 * p.recess_depth), 3)


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
    root_thickness: float = Field(description="Tooth thickness on the root circle, as an arc.",
                                  json_schema_extra={"unit": "mm"})
    root_gap: float = Field(description="Gap between teeth on the root circle, as an arc.",
                            json_schema_extra={"unit": "mm"})
    root_fillet: float = Field(
        description="Root fillet radius actually used, after capping to the gap.",
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

    Measured per call (`.venv/bin/python -m timeit`, best of 5, default GearParams,
    arm64, Python 3.12.13): 9.19 usec before this model, 11.5 usec after --
    validating the frozen model on construction costs about 2.3 usec, negligible next
    to an HTTP round trip and well inside the module docstring's "fast enough to run
    on every keystroke" claim (measured, not assumed -- CLAUDE.md).
    """
    pr = profile(p)
    tip, root, gap = _tooth(pr)
    k, w = span_measurement(p)
    odd = p.teeth % 2 == 1
    over_tips = 2 * pr.ra * (math.cos(math.pi / (2 * p.teeth)) if odd else 1.0)

    warnings: list[str] = []
    if tip < MIN_TIP_FDM:
        warnings.append(f"Tip is only {tip:.2f} mm wide; FDM needs about {MIN_TIP_FDM} mm.")
    rfil = root_fillet(p)
    if rfil < p.root_fillet:
        warnings.append(f"Root fillet reduced to {rfil:.2f} mm to fit the tooth gap.")
    z_min = 2 * (1 - p.profile_shift) / math.sin(pr.alpha) ** 2
    if p.teeth < z_min:
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
        root_thickness=r3(root),
        root_gap=r3(gap),
        # rfil and rec_fil already round(..., 3) internally (root_fillet(),
        # recess_fillet()), so this changes no value on the wire today -- but every
        # length is rounded once, at construction (D-10), so the rule stays true if
        # either helper's rounding ever changes.
        root_fillet=r3(rfil),
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
