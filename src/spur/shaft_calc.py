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

import math
from collections.abc import Sequence
from typing import TYPE_CHECKING, Literal, NamedTuple

from pydantic import BaseModel, ConfigDict, Field

from . import din5480, din5480_tables

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
# least 0.62*m above the internal d_Ff and 0.886*m below d_a (D-20), so off the tables a wrong
# margin costs nothing. DIN 5480-2 puts the internal d_Ff above the standard's maximum by up
# to 0.174*m, which is why a listed size takes its lower bound from the copy's d_Ff1 maximum
# instead (resolved by the tabulated floor, D-12; the margin is unchanged): docs/tech_debt/
# resolved/2026-10-26-form-diameter-construction-exceeds-din5480-2-maximum.md.
GUARD_MARGIN_FACTOR = 0.1

FORM_DIAMETER_UNPROVEN = (
    "The form diameter d_Ff is not given: DIN 5480-1 prints it as a limit tied to the mating "
    "part's tip diameter and a minimum clearance, not as a construction, and no DIN 5480 row "
    "proves one."
)
THEORETICAL_PIN = (
    "The pin diameter D_Re is the theoretical pin that touches the flanks on the circle "
    "m*z + 2*x*m, rounded to 0.01 mm. DIN 5480-2 tabulates its own measuring pin D_M for the "
    "sizes it lists, and for most of them it differs from this pin."
)
# D-09: emitted instead of THEORETICAL_PIN when the loaded table file lists this size. The
# printed D_Re is then DIN 5480-2's D_M; M_Re and its limits are computed for that pin by the
# same formula as everywhere else, never copied from the table's M1 (D-10).
TABULATED_PIN = (
    "The pin diameter D_Re is the measuring pin D_M that DIN 5480-2 tabulates for this size. "
    "M_Re, and M_Re max and M_Re min where they are given, are computed for that pin, not "
    "copied from the table's M1."
)
# The designation prints a fit, but M_Re is computed at the nominal thickness. The copy's own
# M1 minimum for W 120x3x38x8f is taken 0.091 mm below it (tests/test_din5480_anchors.py), so
# a user who cut to the printed M_Re would miss the standard's band (31-REVIEW WR-02).
# Emitted when a printed M_Re has no printed limit beside it: off the tables, and for a listed
# size whose fit Table 7 does not hold. Where a limit prints, MEASURE_LIMITS_AT_FIT replaces it
# (D-10). "M_Re is for this pin" lives here and not in THEORETICAL_PIN, so it shares this
# gate: with no M_Re printed it would sit beside "M_Re is not given" (31-REVIEW IN-07).
MEASURE_AT_NOMINAL_THICKNESS = (
    "M_Re is for this pin and is the measure at the nominal tooth thickness; it carries no "
    "allowance or tolerance for the fit."
)
# D-10: replaces MEASURE_AT_NOMINAL_THICKNESS wherever at least one M_Re limit prints beside the
# nominal M_Re, i.e. for a size and a fit the table file holds. The limits are the measure at
# the fit's actual tooth-thickness limits (DIN 5480-1:2006, Table 6), the printed M_Re is still
# the nominal one, and the sentence keeps a reader from cutting to the wrong one.
MEASURE_LIMITS_AT_FIT = (
    "M_Re is for this pin at the nominal tooth thickness; M_Re max and M_Re min are for this "
    "pin at the fit's actual tooth-thickness limits s_max and s_min (DIN 5480-1 Table 6)."
)
# D-04, D-13, REQ-off-table-builds: the three sentences below say why the five window rows are
# null, one per tier. They share the opening that lists the rows, and each ends in the reason.
# The variable's name is the only reference to the file: warnings reach every API client and a
# path would leave the host (T-34-15).
_WINDOW_NOT_GIVEN = ("The tooth-thickness limits s_vmax, s_max and s_min and M_Re max and "
                     "M_Re min are not given: ")
# Tier 1, no table file named.
NO_TABLE_FILE = (_WINDOW_NOT_GIVEN + "no DIN 5480 table file is set (SPUR_DIN5480_TABLES "
                 "names it).")
# D-13: printed whenever max_effective_thickness is null, because then the solid is cut at the
# nominal thickness and the page must not read a limit into a part that has none.
SOLID_AT_NOMINAL_THICKNESS = (
    "The solid carries the nominal tooth thickness, not the maximum-material thickness "
    "s_vmax of the fit."
)
# D-11: still printed off the tables and with no file. For a size the tables list the gate is
# lifted: 211 of 211 odd DIN 5480-2 rows agree with `din5480.measure_over_pins` at the
# tabulated pin and the nominal thickness (research), and tests/test_din5480_anchors.py pins
# the two approved odd rows, W 26x1.25x19 and W 30x2x13. Off the tables the pin is the
# theoretical one and no row confirms the number at it.
ODD_Z_UNCONFIRMED = (
    "The measurement over pins M_Re is not given for an odd tooth count yet; the pin "
    "diameter is still given."
)
# D-03: the solid's root is built, not cut. No digit, so it cannot imply a fillet radius, and
# never the word `hobbed`: tests/test_shaft_calc.py picks the root_d sentence by that word and
# asserts it occurs once.
ROOT_FORM_CONSTRUCTION = (
    "The solid's tooth root is a construction, not the cut of a hob or broach: each flank "
    "follows the involute down to the root circle, radially below the base circle where that "
    "lies above the root, and the teeth are joined by an arc on root_d. Do not take a root "
    "fillet's shape or size from the solid."
)
# D-08: geometry only. The notch-factor source the research found is a low-confidence
# workshop article, so no factor is stated.
SHANK_STEP_NO_RELIEF = (
    "The spline steps straight into the shank: the solid has no relief groove (DIN 509) and "
    "no hob run-out, and splined_length is a full-form prism."
)
TOOTH_HEIGHT_LIMIT = "tooth height (tip_d - root_d)/2"
SPLINED_LENGTH_LIMIT = "splined_length"


def floor_mm(v: float) -> float:
    """`v` floored to the 0.001 mm the solid is cut at (32-01 choice A1).

    Floored, never rounded: half-even rounding of a splined_length of 2.0006 mm reads 2.001,
    above the length, and the kernel returned an empty shape that still says isValid() for
    that legal link (32-round-up.log). The 1e-9 keeps a typed decimal on itself: every
    three-place decimal 0..500 floors to itself, and without it 2957 of 500,001 lose a step
    (first 1.001, 1.003, 1.005; 32-01-floor-grid.log). No four-place decimal 0..500 floors
    above itself. An input within 1e-9 below a lattice point floors up onto it, by at most
    1.03e-12 mm up to 500 mm (32-02-overshoot.log).
    """
    return math.floor(v * 1000 + 1e-9) / 1000


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


class ChamferReading(NamedTuple):
    """The end chamfer the solid cuts, or None when nothing is cut, and what to say about it."""

    applied: float | None
    warnings: tuple[str, ...]


def size_not_tabulated_warning(p: ShaftParams) -> str:
    """Tier 2: the file is loaded and does not list this size. No nearest row, no
    interpolation (L08); the numbers print in full so a nudged diameter reads as itself."""
    return (_WINDOW_NOT_GIVEN + f"DIN 5480-2 does not list W {_exact(p.reference_d)}x"
            f"{_exact(p.module)}x{p.teeth} in its size tables, and the tool takes no nearest "
            "size and does not interpolate (L08).")


def fit_not_in_table_7_warning(fit: str, letters: Sequence[str],
                               classes: Sequence[int]) -> str:
    """Tier 3: the size is listed and Table 7 does not hold this fit (D-14: a warning, never
    a refusal, so every link that validated still does). The letters and classes are the
    loaded file's, never a constant here (T-34-17)."""
    return (_WINDOW_NOT_GIVEN + f"the fit {fit} is not in DIN 5480-1 Table 7, whose shaft "
            f"deviations are {_listed(letters)} and whose tolerance classes are "
            f"{_listed(classes)}.")


def _listed(items: Sequence[object]) -> str:
    """`a, b and c`."""
    names = [str(i) for i in items]
    return " and ".join([", ".join(names[:-1]), *names[-1:]] if len(names) > 1 else names)


def chamfer_capped_warning(requested: float, applied: float, limits: tuple[str, ...]) -> str:
    return (f"end_chamfer {_exact(requested)} mm is capped at {applied:g} mm, the "
            f"{' and the '.join(limits)}: the 45 degree cone cannot cut below the root circle "
            "or past the splined section.")


def chamfer_below_resolution_warning(requested: float) -> str:
    """The gear's sentence for its tip chamfer (calc.py), for the same print resolution."""
    return (f"end_chamfer {_exact(requested)} mm is below the 0.001 mm resolution it is cut "
            "at and was not cut.")


class PinReading(NamedTuple):
    """A pin and its measurement over pins, or None for what cannot be said honestly."""

    pin_d: float | None
    measure: float | None
    warnings: tuple[str, ...]


class LimitReading(NamedTuple):
    """One M_Re limit, or None and the sentence that says why.

    `LimitReading(None, ())` is a limit `derive_shaft` did not ask for; its tier warning says why.
    """

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
        description="Pin diameter D_Re: DIN 5480-2's tabulated measuring pin D_M for a size "
                    "the table file lists, and otherwise the theoretical pin rounded to 0.01 "
                    "mm. Null when the pin does not touch the involute flanks within the "
                    "contact window.",
        json_schema_extra={"unit": "mm"})
    measure_over_pins: float | None = Field(
        description="Measurement over pins M_Re at nominal thickness, for the printed pin; "
                    "the fit's tooth-thickness window and M_Re limits are the five rows that "
                    "follow. Null for an odd tooth count off the tables (not given there) and when "
                    "the pin does not touch the flanks within the contact window.",
        json_schema_extra={"unit": "mm"})
    max_effective_thickness: float | None = Field(
        description="Maximum effective tooth thickness s_vmax = s1 + A_s (DIN 5480-1:2006, "
                    "Table 6, A_s from Table 7), for a size and a fit the table file lists. "
                    "The solid carries this thickness; when it is null the solid carries the "
                    "nominal thickness (the warnings say so).",
        json_schema_extra={"unit": "mm"})
    max_actual_thickness: float | None = Field(
        description="Maximum actual tooth thickness s_max = s_vmax - T_eff (DIN 5480-1:2006, "
                    "Table 6). Null unless the table file lists the size and the fit.",
        json_schema_extra={"unit": "mm"})
    min_actual_thickness: float | None = Field(
        description="Minimum actual tooth thickness s_min = s_vmax - T_G (DIN 5480-1:2006, "
                    "Table 6). Null unless the table file lists the size and the fit.",
        json_schema_extra={"unit": "mm"})
    measure_over_pins_max: float | None = Field(
        description="Measurement over pins M_Re max: M_Re for the printed pin at the maximum "
                    "actual tooth thickness s_max. Null unless the table file lists the size "
                    "and the fit, and when the pin does not touch the flanks within the "
                    "contact window at s_max.",
        json_schema_extra={"unit": "mm"})
    measure_over_pins_min: float | None = Field(
        description="Measurement over pins M_Re min: M_Re for the printed pin at the minimum "
                    "actual tooth thickness s_min. Null for the same reasons as M_Re max, "
                    "with s_min.",
        json_schema_extra={"unit": "mm"})
    end_chamfer_effective: float | None = Field(
        description="End chamfer actually cut: a 45 degree cone at the free end, sized at the "
                    "tip diameter, floored to 0.001 mm and capped at the tooth height "
                    "(tip_d - root_d)/2 and at splined_length (the warnings say when). Null "
                    "when no chamfer is cut.",
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


def pin_contact_window(p: ShaftParams, form_d_max: float | None = None) -> tuple[float, float]:
    """The contact diameters a pin may touch at, closed on both ends: from the form diameter
    plus the margin up to the tip diameter minus the margin.

    For a size the tables list, `form_d_max` is the copy's d_Ff1 maximum. The copy prints it as
    a maximum and the real form circle lies at or below it, so a contact above it plus the
    margin is on the flank (D-12). The internal construction sat above that maximum on most
    rows and would have narrowed the window from below. Off the tables the internal
    construction stays the floor: the theoretical pin never reaches it (31 D-20).
    """
    margin = GUARD_MARGIN_FACTOR * p.module
    if form_d_max is None:
        xm = din5480.profile_shift(p.reference_d, p.module, p.teeth) * p.module
        form = din5480.form_diameter(p.module, p.teeth, xm, din5480.H_FP, din5480.RHO_FP)
    else:
        form = form_d_max
    return form + margin, din5480.tip_diameter(p.reference_d, p.module) - margin


def pin_measurement(p: ShaftParams, pin_d: float, *, form_d_max: float | None = None,
                    odd_confirmed: bool = False) -> PinReading:
    """The reading for an explicit pin: its measure, or nothing and the reason (L08).

    From derive_shaft at the theoretical pin the two null branches below cannot be reached:
    that pin's contact sits well inside the window (D-20, 31-RESEARCH Pitfall 4). They are live
    for a tabulated pin, which is the standard's and not ours to move.
    The odd-count gate stays unless `odd_confirmed` (D-11, set for a size the tables list).
    """
    xm = din5480.profile_shift(p.reference_d, p.module, p.teeth) * p.module
    s = din5480.tooth_thickness(p.module, xm)
    result = din5480.measure_over_pins(p.module, p.teeth, s, pin_d)
    if result is None:
        return PinReading(None, None, (
            f"M_Re and D_Re not given: a pin of {pin_d:g} mm does not touch the involute "
            f"flanks of this shaft.",))
    measure, contact = result
    low, high = pin_contact_window(p, form_d_max)
    if not low <= contact <= high:
        return PinReading(None, None, (
            f"M_Re and D_Re not given: a pin of {pin_d:g} mm touches at a diameter of "
            f"{contact:.3f} mm, outside the window {low:.3f} to {high:.3f} mm in which the "
            f"flank is measured.",))
    if p.teeth % 2 and not odd_confirmed:
        return PinReading(pin_d, None, (ODD_Z_UNCONFIRMED,))
    return PinReading(pin_d, measure, ())


def limit_measurement(p: ShaftParams, pin_d: float, s: float, which: Literal["max", "min"],
                      *, form_d_max: float | None = None) -> LimitReading:
    """M_Re for `pin_d` at the tooth thickness `s`, unrounded, or nothing and the reason (L08).

    Each limit goes through the pin-contact window on its own: a thinner tooth moves the
    contact, by up to about 0.08*m per 0.05*m of thickness, so a pin that sits inside the
    window at the nominal thickness can leave it at s_min, and that limit alone is then null
    (34-RESEARCH Pitfall 6; D-12 calls it a finding to surface, not something to widen).
    There is no odd-count gate here: `derive_shaft` asks for a limit only for a size the tables
    list, where D-11 confirms the odd formula at the tabulated pin. The nominal reading's gate
    stays in `pin_measurement`.
    """
    result = din5480.measure_over_pins(p.module, p.teeth, s, pin_d)
    if result is None:
        return LimitReading(None, (
            f"M_Re {which} is not given: a pin of {pin_d:g} mm does not touch the involute "
            f"flanks at the tooth thickness s_{which}.",))
    measure, contact = result
    low, high = pin_contact_window(p, form_d_max)
    if not low <= contact <= high:
        return LimitReading(None, (
            f"M_Re {which} is not given: a pin of {pin_d:g} mm at the tooth thickness "
            f"s_{which} touches at a diameter of {contact:.3f} mm, outside the window "
            f"{low:.3f} to {high:.3f} mm in which the flank is measured.",))
    return LimitReading(measure, ())


def end_chamfer_reading(p: ShaftParams, tip_d: float, root_d: float) -> ChamferReading:
    """The end chamfer the solid cuts (L08), from the printed diameters (the radii the solid
    uses), capped and warned, never refused (D-05, L03).

    The smallest of the request, the tooth height and splined_length, each floored to 0.001
    mm. A limit is named only when it binds at that resolution: 1.0004 cut at 1.0 is the
    print resolution, not a cap (the gear's 10-REVIEW CR-01 rule).
    """
    if p.end_chamfer <= 0:
        return ChamferReading(None, ())
    requested = floor_mm(p.end_chamfer)
    tooth = floor_mm((tip_d - root_d) / 2)
    length = floor_mm(p.splined_length)
    applied = min(requested, tooth, length)
    if applied <= 0:
        return ChamferReading(None, (chamfer_below_resolution_warning(p.end_chamfer),))
    if requested <= applied:
        return ChamferReading(applied, ())
    limits = tuple(name for name, cap in ((TOOTH_HEIGHT_LIMIT, tooth),
                                          (SPLINED_LENGTH_LIMIT, length)) if cap == applied)
    return ChamferReading(applied, (chamfer_capped_warning(p.end_chamfer, applied, limits),))


def derive_shaft(p: ShaftParams) -> ShaftDimensions:
    """The basic dimensions of a validated shaft."""

    def r3(v: float) -> float:
        return round(v, 3)

    def rounded(v: float | None) -> float | None:
        return None if v is None else r3(v)

    x = din5480.profile_shift(p.reference_d, p.module, p.teeth)
    xm = x * p.module
    tables = din5480_tables.active()
    row = None if tables is None else tables.size(p.module, p.reference_d, p.teeth)
    tolerance = None if tables is None or row is None else tables.fit(
        p.module, p.reference_d, p.fit)
    pin = (round(din5480.theoretical_pin_diameter(p.module, p.teeth, xm), PIN_DECIMALS)
           if row is None else row.pin_d_mm)
    # D-11: a listed size confirms the odd formula at the tabulated pin; off the tables it stays
    # gated.
    reading = pin_measurement(p, pin, form_d_max=None if row is None else row.form_d_max_mm,
                              odd_confirmed=row is not None)
    root_d = r3(din5480.root_diameter(p.module, p.teeth, xm, din5480.H_FP))
    tip_d = r3(din5480.tip_diameter(p.reference_d, p.module))
    chamfer = end_chamfer_reading(p, tip_d, root_d)
    s1 = din5480.tooth_thickness(p.module, xm)
    s_vmax = s_max = s_min = None
    limit_max = limit_min = LimitReading(None, ())
    if row is not None and tolerance is not None:
        s_vmax, s_max, s_min = din5480.thickness_limits(
            s1, tolerance.a_s_um, tolerance.t_g_um, tolerance.t_eff_um)
        if reading.pin_d is not None:
            limit_max = limit_measurement(p, reading.pin_d, s_max, "max",
                                          form_d_max=row.form_d_max_mm)
            limit_min = limit_measurement(p, reading.pin_d, s_min, "min",
                                          form_d_max=row.form_d_max_mm)
    if reading.measure is None:
        measure_warnings: tuple[str, ...] = ()
    elif limit_max.measure is None and limit_min.measure is None:
        measure_warnings = (MEASURE_AT_NOMINAL_THICKNESS,)
    else:
        measure_warnings = (MEASURE_LIMITS_AT_FIT,)
    if tables is None:
        tier_warnings: tuple[str, ...] = (NO_TABLE_FILE,)
    elif row is None:
        tier_warnings = (size_not_tabulated_warning(p),)
    elif tolerance is None:
        tier_warnings = (fit_not_in_table_7_warning(p.fit, tables.letters,
                                                    tables.tolerance_classes),)
    else:
        tier_warnings = ()
    solid_warnings = (SOLID_AT_NOMINAL_THICKNESS,) if s_vmax is None else ()
    # THEORETICAL_PIN would contradict pin_measurement's "M_Re and D_Re not given".
    pin_warnings = () if reading.pin_d is None else (
        (THEORETICAL_PIN,) if row is None else (TABULATED_PIN,))
    shank_warnings = (SHANK_STEP_NO_RELIEF,) if p.shank_length > 0 else ()
    return ShaftDimensions(
        reference_d=p.reference_d,
        profile_shift=r3(x),
        profile_shift_mm=r3(xm),
        pitch_d=r3(p.module * p.teeth),
        tip_d=tip_d,
        root_d=root_d,
        nominal_thickness=r3(s1),
        form_d=None,
        pin_d=reading.pin_d,
        measure_over_pins=rounded(reading.measure),
        max_effective_thickness=rounded(s_vmax),
        max_actual_thickness=rounded(s_max),
        min_actual_thickness=rounded(s_min),
        measure_over_pins_max=rounded(limit_max.measure),
        measure_over_pins_min=rounded(limit_min.measure),
        end_chamfer_effective=chamfer.applied,
        designation=din5480.format_designation(p.reference_d, p.module, p.teeth, p.fit),
        warnings=(FORM_DIAMETER_UNPROVEN, *pin_warnings, hobbed_root_warning(root_d, p.module),
                  *measure_warnings, *reading.warnings, *tier_warnings, *limit_max.warnings,
                  *limit_min.warnings, *solid_warnings, ROOT_FORM_CONSTRUCTION,
                  *chamfer.warnings, *shank_warnings),
    )
