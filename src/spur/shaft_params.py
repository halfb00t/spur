"""The shaft's one parameter model: `ShaftParams`, validated once at its boundary.

It serves all three front ends under L46. Its field names and defaults are frozen by
tests/test_shaft_params.py, and may still change by a logged decision until Phase 33
publishes the first shaft link; from then on L05 applies to them in full, as it does to the
gear's. The default shaft is W 25x1.25x18x8f.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator
from pydantic_core import PydanticCustomError

from .din5480 import FIT_PATTERN, X_MAX, X_MIN

# Intentional coupling (31-REVIEW IN-05): a shaft field is built with the gear's `_f` and
# `_extra`, underscore-private in params.py, so it carries the same schema metadata (group,
# unit, step, help) as a gear field. A rename there fails this import loudly (mypy, every
# test), but no import-linter contract names the pair; change the helpers with both
# modules in view.
from .params import _extra, _f

# The default shaft sits exactly on X_MAX, so a step off it in any of the three fields
# below can cross the range (31-REVIEW IN-05).
_SHIFT_RANGE_HELP = f" Shifts outside {X_MIN:+.2f}..{X_MAX:+.2f} are refused."


class ShaftParams(BaseModel):
    """A DIN 5480 external splined shaft: its spline and, for the solid, a shank."""

    model_config = ConfigDict(frozen=True)

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
    # The four fields below belong to the solid. Their bounds are provisional until Phase
    # 32's sweep, and cross-field rules among them (chamfer against tooth height, shank
    # against tip) arrive with the solid: this model enforces ranges only.
    splined_length: float = _f(30.0, 1, 500, title="Splined length", group="Spline",
                               unit="mm", step=0.5,
                               help="Length of the toothed part of the shaft.")
    end_chamfer: float = _f(1.0, 0, 10, title="End chamfer", group="Spline", unit="mm",
                            step=0.05,
                            help="Chamfer on the tooth ends at the free end of the shaft. "
                                 "0 = none.")

    # --- Shank -----------------------------------------------------------------
    shank_d: float = _f(25.0, 1, 850, title="Shank Ø", group="Shank", unit="mm", step=0.05,
                        help="Diameter of the plain shaft behind the splined part.")
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
