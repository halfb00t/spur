"""The part type the shared entry points name, instead of naming the gear.

pool, records, app and model take "a part", which today is a `GearParams`. Phase 32 widens
`Part` to `GearParams | ShaftParams`, in the same change that makes model build a shaft.
That change also types or dispatches `model._build_checked` and `model._write_export`, both
typed `GearParams`, and `records._gear_fields`, which reads gear-only attributes, so it is
more than an edit of this file. Phase 31 has no solid and no route, so nothing passes a
`ShaftParams` to pool, records or model yet, and widening earlier would put an unreachable
shaft branch into the model internals (30-CONTEXT D-10; D-08, L46).

A plain assignment on purpose: ruff's UP040 rewrites a `TypeAlias` annotation, and a
`type` statement makes a TypeAliasType, which isinstance cannot take (30-RESEARCH).
"""

from .params import GearParams

Part = GearParams
