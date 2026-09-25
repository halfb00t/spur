"""Gear parameters: one validated, hashable model shared by the API, web UI and CLI.

All lengths are millimetres, angles are degrees. Field metadata (group, unit, step)
is exported through the JSON schema and drives the web form, so a new field added
here shows up in the UI and CLI automatically.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator
from pydantic.config import JsonDict
from pydantic_core import PydanticCustomError


def _f[T](default: T, ge: float, le: float, *, title: str, group: str,
          unit: str = "", step: float | None = None, help: str = "") -> T:
    extra: JsonDict = {"group": group, "unit": unit}
    if step is not None:
        extra["step"] = step
    return Field(default, ge=ge, le=le, title=title, description=help,
                 json_schema_extra=extra)


class GearParams(BaseModel):
    """Involute spur gear with optional D-bore and annular face recesses."""

    model_config = ConfigDict(frozen=True)

    # --- Teeth -----------------------------------------------------------------
    teeth: int = _f(19, 6, 200, title="Teeth", group="Teeth", step=1,
                    help="Number of teeth.")
    module: float = _f(1.75, 0.2, 10, title="Module", group="Teeth", unit="mm", step=0.05,
                       help="Pitch diameter / teeth. Must match the mating gear.")
    pressure_angle: float = _f(25.0, 14.5, 35, title="Pressure angle", group="Teeth",
                               unit="°", step=0.5,
                               help="Higher gives thinner tips and thicker roots. "
                                    "Must match the mating gear.")
    profile_shift: float = _f(0.0, -0.6, 1.0, title="Profile shift (x)", group="Teeth",
                              step=0.05,
                              help="Positive x thickens the root and moves the tip outward.")
    backlash: float = _f(0.10, 0, 1, title="Backlash", group="Teeth", unit="mm", step=0.01,
                         help="Removed from the circular tooth thickness (printing clearance).")
    root_fillet: float = _f(0.5, 0, 3, title="Root fillet", group="Teeth", unit="mm",
                            step=0.05,
                            help="Fillet radius at the tooth roots, capped to fit. 0 = sharp.")

    # --- Body ------------------------------------------------------------------
    face_width: float = _f(7.5, 1, 100, title="Face width", group="Body", unit="mm",
                           step=0.1, help="Overall thickness of the gear.")

    # --- Bore ------------------------------------------------------------------
    bore_d: float = _f(9.0, 0, 200, title="Bore Ø", group="Bore", unit="mm", step=0.05,
                       help="Round part of the bore. 0 = solid, no bore.")
    bore_flat: float = _f(8.0, 0, 200, title="D-flat", group="Bore", unit="mm", step=0.05,
                          help="Flat to opposite side of the bore. 0 = round bore.")
    bore_clearance: float = _f(0.15, 0, 1, title="Bore clearance", group="Bore", unit="mm",
                               step=0.01,
                               help="Added to bore and flat for print shrinkage. 0 for resin/SLS.")
    bore_chamfer: float = _f(0.4, 0, 3, title="Bore chamfer", group="Bore", unit="mm",
                             step=0.05, help="Chamfer on both bore edges. 0 = none.")

    # --- Recess ----------------------------------------------------------------
    recess_sides: Literal["both", "top", "bottom", "none"] = Field(
        "both", title="Recess sides", description="Which faces get an annular groove.",
        json_schema_extra={"group": "Recess", "unit": ""})
    recess_depth: float = _f(2.0, 0, 50, title="Recess depth", group="Recess", unit="mm",
                             step=0.1, help="Depth of each groove.")
    recess_width: float = _f(6.0, 0, 100, title="Recess width", group="Recess", unit="mm",
                             step=0.1, help="Radial width of the groove.")
    recess_inner_d: float = _f(0.0, 0, 400, title="Recess inner Ø", group="Recess",
                               unit="mm", step=0.1,
                               help="0 = centred so the hub wall equals the rim wall.")
    recess_fillet: float = _f(0.5, 0, 5, title="Recess fillet", group="Recess", unit="mm",
                              step=0.05, help="Fillet at the groove floor corners.")

    @model_validator(mode="after")
    def _feasible(self) -> GearParams:
        from .calc import check  # local import: calc only needs the attributes

        problems = check(self)
        if problems:
            fields = sorted({f for _, fs in problems for f in fs})
            raise PydanticCustomError(
                "infeasible", "{message}",
                {"message": " ".join(m for m, _ in problems), "fields": fields})
        return self

    def slug(self) -> str:
        """Short, filename-safe identifier."""
        return f"spur_z{self.teeth}_m{self.module:g}_pa{self.pressure_angle:g}"
