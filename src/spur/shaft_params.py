"""The shaft's one parameter model: `ShaftParams`, validated once at its boundary.

It serves all three front ends under L46. Its field names and defaults are frozen by
tests/test_shaft_params.py, and may still change by a logged decision until Phase 33
publishes the first shaft link; from then on L05 applies to them in full, as it does to the
gear's. The default shaft is W 25x1.25x18x8f.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence

from pydantic import BaseModel, ConfigDict, Field, model_validator
from pydantic_core import PydanticCustomError

from .din5480 import FIT_PATTERN, X_MAX, X_MIN, parse_designation

# Intentional coupling (31-REVIEW IN-05): a shaft field is built with the gear's `_f` and
# `_extra`, underscore-private in params.py, so it carries the same schema metadata (group,
# unit, step, help) as a gear field. A rename there fails this import loudly (mypy, every
# test), but no import-linter contract names the pair; change the helpers with both
# modules in view.
from .params import _extra, _f, when

# The default shaft sits exactly on X_MAX, so a step off it in any of the three fields
# below can cross the range (31-REVIEW IN-05).
_SHIFT_RANGE_HELP = f" Shifts outside {X_MIN:+.2f}..{X_MAX:+.2f} are refused."


class ShaftParams(BaseModel):
    """A DIN 5480 external splined shaft: its spline and, for the solid, a shank."""

    # `dims` is the shaft's result rows, in ShaftDimensions order: the page prints them from
    # the schema because a second row table in app.js is forbidden by two pins, and the gear
    # schema's bytes are frozen (ROADMAP Phase 33 boundaries). Inline, as GearParams does for
    # `selectors`, so mypy sees a JSON value. A key or unit that drifts from ShaftDimensions
    # fails tests/test_shaft_interfaces.py, which keeps the rows complete.
    model_config = ConfigDict(frozen=True, json_schema_extra={"dims": [
        {"key": "reference_d", "label": "Reference Ø d_B", "unit": "mm"},
        {"key": "profile_shift", "label": "Profile shift x", "unit": ""},
        {"key": "profile_shift_mm", "label": "Profile shift x·m", "unit": "mm"},
        {"key": "pitch_d", "label": "Pitch Ø", "unit": "mm"},
        {"key": "tip_d", "label": "Tip Ø", "unit": "mm"},
        {"key": "root_d", "label": "Root Ø", "unit": "mm"},
        {"key": "nominal_thickness", "label": "Nominal tooth thickness", "unit": "mm"},
        {"key": "form_d", "label": "Form Ø d_Ff", "unit": "mm"},
        {"key": "pin_d", "label": "Pin Ø D_Re", "unit": "mm"},
        {"key": "measure_over_pins", "label": "Measurement over pins M_Re", "unit": "mm"},
        {"key": "end_chamfer_effective", "label": "End chamfer used", "unit": "mm"},
        {"key": "designation", "label": "Designation", "unit": ""},
    ]})

    # --- Spline ----------------------------------------------------------------
    # The field is reference_d; the form's title says d_B (D-01).
    reference_d: float = _f(25.0, 3, 850, title="Reference Ø d_B", group="Spline", unit="mm",
                            step=0.05,
                            help="Reference diameter of the spline. The profile shift is "
                                 "derived from it, the module and the tooth count."
                                 + _SHIFT_RANGE_HELP)
    module: float = _f(1.25, 0.5, 10, title="Module", group="Spline", unit="mm", step=0.05,
                       help="Reference circle diameter / teeth. Must match the hub."
                            + _SHIFT_RANGE_HELP)
    teeth: int = _f(18, 6, 82, title="Teeth", group="Spline", step=1,
                    help="Number of teeth." + _SHIFT_RANGE_HELP)
    # One string holding the designation's token (D-02). Only its shape is checked here;
    # whether the fit exists in the tables is Phase 34's.
    fit: str = Field("8f", pattern=FIT_PATTERN, max_length=3, title="Fit",
                     description="Tolerance token of the designation, such as 8f. Checked "
                                 "for shape only: one or two digits, then one lower-case "
                                 "letter. Whether the fit exists in the tables is not "
                                 "checked yet.",
                     json_schema_extra=_extra("Spline"))
    # The four fields below belong to the solid. No cross-field rule among them: every shank_d
    # is allowed against the spline (D-07), and end_chamfer is capped and warned in
    # derive_shaft, never refused (D-05). Their bounds were set by Phase 32's sweep (bench/
    # RESULTS.md `### The heaviest shaft (32-05)`): the heaviest allowed shaft builds and
    # exports in 2.23 s on macOS and 5.44 s in the Linux container, against 30 s (L37).
    splined_length: float = _f(30.0, 1, 500, title="Splined length", group="Spline",
                               unit="mm", step=0.5,
                               help="Length of the toothed part of the shaft, "
                                    "a full-form prism: the teeth keep their full form up "
                                    "to the shank, with no relief groove or hob run-out.")
    end_chamfer: float = _f(1.0, 0, 10, title="End chamfer", group="Spline", unit="mm",
                            step=0.05,
                            help="A 45 degree cone at the free end, sized at the tip diameter: "
                                 "it starts on the end face at tip_d - 2*end_chamfer and "
                                 "reaches tip_d at end_chamfer from the end. Capped at the "
                                 "tooth height and at the splined length, with a warning. "
                                 "0 = none.")

    # --- Shank -----------------------------------------------------------------
    # Dimmed without a shank (D-18): test_shank_d_changes_nothing_without_a_shank builds four
    # values at shank_length 0 and finds the solid bit-equal, so the dim claims nothing false.
    shank_d: float = _f(25.0, 1, 850, title="Shank Ø", group="Shank", unit="mm", step=0.05,
                        help="Diameter of the plain shaft behind the splined part.",
                        enabled_when=[when("shank_length", "gt", 0)])
    shank_length: float = _f(20.0, 0, 500, title="Shank length", group="Shank", unit="mm",
                             step=0.5,
                             help="Length of the plain shaft behind the splined part. "
                                  "0 = none.")

    @model_validator(mode="after")
    def _feasible(self) -> ShaftParams:
        from .shaft_calc import check_shaft  # local import: shaft_calc only needs the attributes

        problems = check_shaft(self)
        if problems:
            fields = sorted({f for _, fs in problems for f in fs})
            raise PydanticCustomError(
                "infeasible", "{message}",
                {"message": " ".join(m for m, _ in problems), "fields": fields})
        return self

    def slug(self) -> str:
        """The short, filename-safe name of the shaft, built from numbers only.

        Called for the worker's temporary export file, the `slug` field of every per-request
        record and the `Content-Disposition` of every shaft download. This is the frozen name
        of that download (L49, D-17): `spur_shaft_w25x1.25x18` for the default, changed only
        by a logged decision. No cache is keyed by it (L40). The fit is left out: it is a
        user-typed string and the solid does not depend on it. `:g` keeps six significant
        digits, so two `reference_d` of 123.4567 and 123.4571 at one module and tooth count
        share the stem `w123.457`, and 25.00004 reads `w25`: a second collision source beside
        the fit, accepted with the name's freeze (IN-05); a repr-exact name would supersede L49.
        """
        return f"spur_shaft_w{self.reference_d:g}x{self.module:g}x{self.teeth}"


# A designation names the four spline fields, so it replaces them (REQ-designation-input).
# Held in the codec's own order; tests/test_shaft_interfaces.py pins the two together.
SPLINE_KEYS: tuple[str, ...] = ("reference_d", "module", "teeth", "fit")


class DesignationConflict(ValueError):  # noqa: N818 -- the name 33-05's CLI imports
    """A designation was given beside a spline field; `fields` are the fields it clashes with."""

    def __init__(self, fields: Sequence[str]) -> None:
        super().__init__(clash_message(fields))
        self.fields = tuple(fields)


def designation_clash(keys: Iterable[str]) -> tuple[str, ...]:
    """The spline fields present among `keys`, in spline order.

    Key presence, not value (D-07): a value that equals the designation's is still a second
    statement of it, and judging equality across `25`, `25.0` and `25,0` would be a guess
    about what the user meant. Every front end calls this one function, on the keys as sent
    and before any value is parsed, so the API and the CLI refuse the same requests.
    """
    present = set(keys)
    return tuple(k for k in SPLINE_KEYS if k in present)


def clash_message(clash: Sequence[str]) -> str:
    """The sentence for a designation given beside `clash`."""
    named = " and ".join([", ".join(clash[:-1]), *clash[-1:]] if len(clash) > 1 else clash)
    return (f"The designation sets {', '.join(SPLINE_KEYS[:-1])} and {SPLINE_KEYS[-1]}, "
            f"so it cannot be given together with {named}.")


def resolve_shaft(designation: str, given: Mapping[str, object]) -> ShaftParams:
    """The shaft a designation and the solid's fields describe.

    `given` holds the solid's fields (splined_length, end_chamfer, shank_d, shank_length),
    which combine freely with a designation (D-08). A spline field in it is refused here
    too, so no caller can let a designation silently win (D-07). DesignationError and
    pydantic's ValidationError propagate: the first is text the codec cannot read, the
    second a shaft the model refuses. Pure: it reads its arguments only.
    """
    clash = designation_clash(given)
    if clash:
        raise DesignationConflict(clash)
    return ShaftParams.model_validate({**given, **parse_designation(designation)._asdict()})
