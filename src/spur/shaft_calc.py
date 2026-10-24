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

from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

from . import din5480

if TYPE_CHECKING:
    from .shaft_params import ShaftParams


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
    root_d: float = Field(description="Root diameter.",
                          json_schema_extra={"unit": "mm"})
    nominal_thickness: float = Field(
        description="Nominal tooth thickness, as an arc on the reference circle.",
        json_schema_extra={"unit": "mm"})
    warnings: tuple[str, ...] = Field(description="Sentences about values that were capped "
                                                  "or cannot be computed honestly.")


def check_shaft(p: ShaftParams) -> list[tuple[str, tuple[str, ...]]]:
    """One (sentence, field names) per problem; empty when the shaft is feasible.

    A profile shift outside the shaft range is refused, never clamped to the edge and built
    as a nearby shaft (L03). The comparison carries X_EPS on both edges because the shift
    is a float quotient: three standard combinations land a few ulp outside the range they
    sit on (see din5480.profile_shift).
    """
    x = din5480.profile_shift(p.reference_d, p.module, p.teeth)
    if x < din5480.X_MIN - din5480.X_EPS or x > din5480.X_MAX + din5480.X_EPS:
        return [(f"A reference diameter of {p.reference_d:g} mm with module {p.module:g} and "
                 f"{p.teeth} teeth needs a profile shift of {x:+.3f}, outside the range "
                 f"{din5480.X_MIN:+.2f} to {din5480.X_MAX:+.2f}. Pick another reference "
                 f"diameter, module or tooth count.",
                 ("module", "reference_d", "teeth"))]
    return []


def derive_shaft(p: ShaftParams) -> ShaftDimensions:
    """The basic dimensions of a validated shaft."""

    def r3(v: float) -> float:
        return round(v, 3)

    x = din5480.profile_shift(p.reference_d, p.module, p.teeth)
    xm = x * p.module
    return ShaftDimensions(
        reference_d=p.reference_d,
        profile_shift=r3(x),
        profile_shift_mm=r3(xm),
        pitch_d=r3(p.module * p.teeth),
        tip_d=r3(din5480.tip_diameter(p.reference_d, p.module)),
        root_d=r3(din5480.root_diameter(p.module, p.teeth, xm, din5480.H_FP)),
        nominal_thickness=r3(din5480.tooth_thickness(p.module, xm)),
        warnings=(),
    )
