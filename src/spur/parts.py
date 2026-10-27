"""The part type the shared entry points name, instead of naming the gear.

pool, records, app and model take "a part": a `GearParams` or a `ShaftParams`. model
dispatches on it in `_build`, as its first statement, so the gear's build lines below stay
as they were; `_build_checked` and `_write_export` take `Part`, and records reads `slug()`
and `model_dump`, which both models have. A shaft has no route until Phase 33, so today
only model, pool and records can be handed one (L46).

A plain assignment on purpose: ruff's UP040 rewrites a `TypeAlias` annotation, and a
`type` statement makes a TypeAliasType, which isinstance cannot take (30-RESEARCH).
"""

from .params import GearParams
from .shaft_params import ShaftParams

Part = GearParams | ShaftParams
