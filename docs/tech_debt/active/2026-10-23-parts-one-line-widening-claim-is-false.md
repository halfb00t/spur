# `parts.py` says widening `Part` is a one-line edit; the gear-typed internals behind it make that false

Severity: must
Status: active
Date: 2026-10-23
Source: Phase 30 code review, WR-03; confirmed by the Phase 30 verifier
Related files:
- src/spur/parts.py:3-5
- src/spur/model.py (`_build_checked`, `_write_export`, typed `GearParams`)
- src/spur/records.py:171 (`_gear_fields`)

## Context
The `parts.py` docstring says Phase 31 widens `Part` to `GearParams | ShaftParams` with a one-line
edit here, so that no signature behind the seam is touched again. `model.build`/`model.export`
take `Part` but pass it straight to `_build_checked(p: GearParams)` and
`_write_export(..., p: GearParams, ...)`, and `records._gear_fields` reads gear-only attributes.

## Why it matters
Under `mypy --strict` the widening fails at those call sites. The docstring sets a wrong
expectation for the phase that relies on it. No Phase 30 success criterion depends on the claim.

## Next step
Phase 31 (trigger): when `Part` is widened, either type or dispatch those internals in the same
change, or first correct the docstring to name them. Resolve in that commit.
