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


def bore_rim_limit(p: GearParams) -> float:
    """The farthest any point on the bore's rim can sit from the axis -- the exact
    geometric bound, no slack.

    Round and D-flat both reduce to bore_radius(p): the D-flat hole is the round hole
    intersected with a rectangle (model._cut_bore), a strict subset of the circle, so it
    adds no point farther out. That stops being true once a bore shape has a vertex
    outside the circle -- Phase 8's hex bore adds its circumradius (across-flats over
    sqrt 3) here instead of widening this bound (research ARCHITECTURE.md Q2's rejected
    anti-pattern: generalizing lim by widening it). calc.py knows no kernel tolerance;
    the selection slack that turns this exact bound into a matching band belongs to
    model.py, not here.
    """
    return bore_radius(p)


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
    r_bore = bore_radius(p)
    hub = r_bore + (p.bore_chamfer if p.bore_d > 0 else 0.0) + MIN_WALL  # clear of the hub wall
    rim = rf - MIN_WALL                                                  # clear of the tooth rim
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

    r_bore = bore_radius(p)
    if p.bore_d > 0 and r_bore > pr.rf - MIN_WALL:
        errors.append(("Bore is too large for the root diameter.", ("bore_d",)))
    if p.bore_d > 0 and p.bore_flat > 0 and not p.bore_d / 2 < p.bore_flat < p.bore_d:
        errors.append((f"D-flat must be between {p.bore_d / 2:g} and {p.bore_d:g} mm "
                       "(flat to opposite side).", ("bore_flat",)))
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
        description="Bore diameter including print clearance; null with no bore.",
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
        bore_effective=r3(2 * bore_radius(p)) if p.bore_d > 0 else None,
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
