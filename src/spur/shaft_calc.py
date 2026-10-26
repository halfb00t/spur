"""The pure shaft maths behind the numbers the tool prints for a shaft.

It copies calc.py's patterns (one function per quantity; a value that cannot be computed
honestly comes back as None and a warning, never a plausible number, L08) and never takes
anything out of calc.py: gear and shaft numbers stay uncoupled, the way `_involute_angle` was
copied rather than shared.

Like calc.py it runs on every keystroke, so it must stay free of the CAD kernel, the solid
and the logger. The formulas live in din5480.py; this file orders them into the document
the front ends print and into the one refusal the parameter model raises.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple

from pydantic import BaseModel, ConfigDict, Field

from . import din5480

if TYPE_CHECKING:
    from .shaft_params import ShaftParams


# D-11 gauge step 0.01 mm. 31-RESEARCH A4 found no documented series for a theoretical
# pin (the vendors' effective pins are round values, 6.000 and 5.500), so 0.01 mm is D-11's
# default. The 31-05 checkpoint found no series in DIN 5480-1:2006 (Fig. 6's gauge pin 6.000
# is an example, not a series). ASSUMPTION (no series in the copy)
PIN_DECIMALS = 2
# D-12 margin, times m, on both ends of the pin-contact window. The two observed gaps
# between a constructed and a published form diameter are 0.030 mm (Hexagon, 0.01*m at m 3)
# and 0.202 mm (KISSsoft, 0.067*m); 1.5 times the larger is 0.1*m. Scaling with m is an
# assumption, both gaps are at m 3. Over 7,392 cases the theoretical pin's contact sits at
# least 0.62*m above the internal d_Ff and 0.886*m below d_a (D-20), so a wrong margin
# costs nothing until Phase 34.
GUARD_MARGIN_FACTOR = 0.1

FORM_DIAMETER_UNPROVEN = (
    "The form diameter d_Ff is not given: DIN 5480-1 prints it as a limit tied to the mating "
    "part's tip diameter and a minimum clearance, not as a construction, and no DIN 5480 row "
    "proves one."
)
THEORETICAL_PIN = (
    "The pin diameter D_Re is the theoretical pin that touches the flanks on the circle "
    "m*z + 2*x*m, rounded to 0.01 mm. The tool computes this pin; it has not been compared "
    "with a tabulated D_Re."
)
# The designation prints a fit, but M_Re is computed at the nominal thickness. The copy's own
# M1 minimum for W 120x3x38x8f is taken 0.091 mm below it (tests/test_din5480_anchors.py), so
# a user who cut to the printed M_Re would miss the standard's band (31-REVIEW WR-02).
# Emitted whenever measure_over_pins is non-null; Phase 34 removes it when it passes limit
# thicknesses. "M_Re is for this pin" lives here and not in THEORETICAL_PIN, so it shares
# this gate: with no M_Re printed it would sit beside "M_Re is not given" (31-REVIEW IN-07).
MEASURE_AT_NOMINAL_THICKNESS = (
    "M_Re is for this pin and is the measure at the nominal tooth thickness; it carries no "
    "allowance or tolerance for the fit."
)
ODD_Z_UNCONFIRMED = (
    "The measurement over pins M_Re is not given for an odd tooth count yet; the pin "
    "diameter is still given."
)


# h_fP is a radial depth and root_d a diameter, so the hobbed root is the theoretical root
# less 2 * (0.60 - 0.55) = 0.1 times m (cl. 7.1). Rounded, because 0.60 - 0.55 is not exact
# in binary64. The sentence below and the root_d field description print this constant, so
# one edit moves the number and the words together (31-REVIEW IN-04). The two depths are in
# din5480's constants block (31-REVIEW IN-09); tests/test_shaft_calc.py asserts the drop
# stays above 0, so a sentence reading "0*m smaller" cannot ship.
HOBBED_ROOT_DROP = round(2 * (din5480.H_FP_HOBBING - din5480.H_FP), 3)


def hobbed_root_warning(root_d: float, module: float) -> str:
    """The root_d sentence, with the hobbed value from the same rounded root_d it sits beside."""
    hobbed = round(root_d - HOBBED_ROOT_DROP * module, 3)
    return (f"The root diameter is the theoretical (broaching) root. A hobbed shaft's root is "
            f"{HOBBED_ROOT_DROP:g}*m smaller (DIN 5480-1 cl. 7.1): hobbed: root_d - "
            f"{HOBBED_ROOT_DROP:g}*m = {hobbed:.3f} mm. "
            f"That is not the whole list: the standard names root depths for other processes "
            f"too (DIN 5480-1 cl. 7.1), and this tool gives none of them.")


class PinReading(NamedTuple):
    """A pin and its measurement over pins, or None for what cannot be said honestly."""

    pin_d: float | None
    measure: float | None
    warnings: tuple[str, ...]


class ShaftDimensions(BaseModel):
    """The one document a shaft's dimensions are printed from.

    Every key is always present. `None` means a value does not apply or cannot be
    computed honestly -- never a plausible number in its place (L08).
    """

    model_config = ConfigDict(frozen=True)

    reference_d: float = Field(description="Reference diameter d_B, as given.",
                               json_schema_extra={"unit": "mm"})
    profile_shift: float = Field(description="Profile shift x, derived from the reference "
                                             "diameter, module and tooth count.",
                                 json_schema_extra={"unit": ""})
    profile_shift_mm: float = Field(description="Profile shift in millimetres, x times the "
                                                "module.",
                                    json_schema_extra={"unit": "mm"})
    pitch_d: float = Field(description="Reference circle diameter, module times teeth.",
                           json_schema_extra={"unit": "mm"})
    tip_d: float = Field(description="Tip (outside) diameter.",
                         json_schema_extra={"unit": "mm"})
    root_d: float = Field(description="Theoretical (broaching) root diameter, h_fP = 0.55*m, "
                                      "per DIN 5480-1 cl. 7.1. A hobbed shaft's root is "
                                      f"{HOBBED_ROOT_DROP:g}*m smaller (the warnings give "
                                      "it); the standard names "
                                      "other processes too, so that list is incomplete "
                                      "(DIN 5480-1 cl. 7.1).",
                          json_schema_extra={"unit": "mm"})
    nominal_thickness: float = Field(
        description="Nominal tooth thickness, as an arc on the reference circle.",
        json_schema_extra={"unit": "mm"})
    form_d: float | None = Field(
        description="Form diameter d_Ff. Null for every shaft: DIN 5480-1 prints it as a "
                    "limit tied to the mating part, not a construction (the warnings say so).",
        json_schema_extra={"unit": "mm"})
    pin_d: float | None = Field(
        description="Pin diameter D_Re: the theoretical pin rounded to 0.01 mm. Null when "
                    "the pin does not touch the involute flanks within the contact window.",
        json_schema_extra={"unit": "mm"})
    measure_over_pins: float | None = Field(
        description="Measurement over pins M_Re at nominal thickness, for the printed pin. "
                    "Null for an odd tooth count (unconfirmed) and when the pin does not "
                    "touch the flanks within the contact window.",
        json_schema_extra={"unit": "mm"})
    designation: str = Field(description="The DIN 5480 designation of these parameters, as "
                                         "the codec prints it.")
    warnings: tuple[str, ...] = Field(description="Sentences about values that were capped "
                                                  "or cannot be computed honestly.")


def _exact(v: float) -> str:
    """`v` as %g prints it, unless that is a different number: then its full repr."""
    short = f"{v:g}"
    return short if float(short) == v else repr(v)


def check_shaft(p: ShaftParams) -> list[tuple[str, tuple[str, ...]]]:
    """One (sentence, field names) per problem; empty when the shaft is feasible.

    A profile shift outside the shaft range is refused, never clamped to the edge and built
    as a nearby shaft (L03). The comparison carries X_EPS on both edges because the shift
    is a float quotient: three standard combinations land a few ulp outside the range they
    sit on (see din5480.profile_shift).
    """
    x = din5480.profile_shift(p.reference_d, p.module, p.teeth)
    if x < din5480.X_MIN - din5480.X_EPS or x > din5480.X_MAX + din5480.X_EPS:
        # Four decimals, and the side: the default sits on X_MAX, so a 0.001 mm nudge of
        # reference_d refuses at +0.4504, and three decimals printed it as "+0.450, outside
        # +0.45" (31-REVIEW WR-01). A nudge under 0.0001 mm still rounds onto the edge at
        # four decimals, so the shift then gets nine, enough to show any overshoot past the
        # 1e-9 epsilon. The inputs print in full when six significant digits would hide the
        # nudge, or 25.00001 reads as the default 25 (31-REVIEW WR-06).
        side = "above" if x > din5480.X_MAX else "below"
        edge = din5480.X_MAX if side == "above" else din5480.X_MIN
        shown = f"{x:+.4f}"
        if float(shown) == edge:
            shown = f"{x:+.9f}"
        return [(f"A reference diameter of {_exact(p.reference_d)} mm with module "
                 f"{_exact(p.module)} and {p.teeth} teeth needs a profile shift of {shown}, "
                 f"{side} the allowed range {din5480.X_MIN:+.2f} to {din5480.X_MAX:+.2f}. "
                 f"Pick another reference diameter, module or tooth count.",
                 ("module", "reference_d", "teeth"))]
    return []


def pin_contact_window(p: ShaftParams) -> tuple[float, float]:
    """The contact diameters a pin may touch at: the internal form diameter plus the margin,
    up to the tip diameter minus the margin. Closed on both ends."""
    xm = din5480.profile_shift(p.reference_d, p.module, p.teeth) * p.module
    margin = GUARD_MARGIN_FACTOR * p.module
    form = din5480.form_diameter(p.module, p.teeth, xm, din5480.H_FP, din5480.RHO_FP)
    return form + margin, din5480.tip_diameter(p.reference_d, p.module) - margin


def pin_measurement(p: ShaftParams, pin_d: float) -> PinReading:
    """The reading for an explicit pin: its measure, or nothing and the reason (L08).

    From derive_shaft at the theoretical pin the two null branches below cannot be reached:
    that pin's contact sits well inside the window (D-20, 31-RESEARCH Pitfall 4). They go
    live in Phase 34, when the copy's tabulated D_Re replaces the computed pin, and are
    covered by direct calls until then. The odd-count gate stays although DIN 5480-2 rows now
    confirm the odd formula: printing it is a separate decision (D-13; docs/ideas/2026-10-26-
    print-odd-tooth-count-measure-over-pins.md).
    """
    xm = din5480.profile_shift(p.reference_d, p.module, p.teeth) * p.module
    s = din5480.tooth_thickness(p.module, xm)
    result = din5480.measure_over_pins(p.module, p.teeth, s, pin_d)
    if result is None:
        return PinReading(None, None, (
            f"M_Re and D_Re not given: a pin of {pin_d:g} mm does not touch the involute "
            f"flanks of this shaft.",))
    measure, contact = result
    low, high = pin_contact_window(p)
    if not low <= contact <= high:
        return PinReading(None, None, (
            f"M_Re and D_Re not given: a pin of {pin_d:g} mm touches at a diameter of "
            f"{contact:.3f} mm, outside the window {low:.3f} to {high:.3f} mm in which the "
            f"flank is measured.",))
    if p.teeth % 2:
        return PinReading(pin_d, None, (ODD_Z_UNCONFIRMED,))
    return PinReading(pin_d, measure, ())


def derive_shaft(p: ShaftParams) -> ShaftDimensions:
    """The basic dimensions of a validated shaft."""

    def r3(v: float) -> float:
        return round(v, 3)

    x = din5480.profile_shift(p.reference_d, p.module, p.teeth)
    xm = x * p.module
    pin = round(din5480.theoretical_pin_diameter(p.module, p.teeth, xm), PIN_DECIMALS)
    reading = pin_measurement(p, pin)
    root_d = r3(din5480.root_diameter(p.module, p.teeth, xm, din5480.H_FP))
    measure_warnings = () if reading.measure is None else (MEASURE_AT_NOMINAL_THICKNESS,)
    # THEORETICAL_PIN would contradict pin_measurement's "M_Re and D_Re not given".
    pin_warnings = () if reading.pin_d is None else (THEORETICAL_PIN,)
    return ShaftDimensions(
        reference_d=p.reference_d,
        profile_shift=r3(x),
        profile_shift_mm=r3(xm),
        pitch_d=r3(p.module * p.teeth),
        tip_d=r3(din5480.tip_diameter(p.reference_d, p.module)),
        root_d=root_d,
        nominal_thickness=r3(din5480.tooth_thickness(p.module, xm)),
        form_d=None,
        pin_d=reading.pin_d,
        measure_over_pins=None if reading.measure is None else r3(reading.measure),
        designation=din5480.format_designation(p.reference_d, p.module, p.teeth, p.fit),
        warnings=(FORM_DIAMETER_UNPROVEN, *pin_warnings, hobbed_root_warning(root_d, p.module),
                  *measure_warnings, *reading.warnings),
    )
