"""The part type the shared entry points name, instead of naming the gear.

pool, records, app and model take "a part", which today is a `GearParams`. Phase 31 widens
`Part` to `GearParams | ShaftParams` with a one-line edit here, in a file that is not a
gear file, so none of those signatures is touched again (D-08, L46).

A plain assignment on purpose: ruff's UP040 rewrites a `TypeAlias` annotation, and a
`type` statement makes a TypeAliasType, which isinstance cannot take (30-RESEARCH).
"""

from .params import GearParams

Part = GearParams
