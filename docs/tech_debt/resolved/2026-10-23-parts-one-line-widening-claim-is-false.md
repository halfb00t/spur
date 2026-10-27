# Widening `Part` to the shaft must type `model._build_checked`, `model._write_export` and `records._gear_fields` in the same change

Severity: must
Status: resolved
Resolved in: feat(model): build and export a shaft through the one kernel doorway (Part widens) (gsd/phase-32-the-shaft-solid)
Date: 2026-10-23
Source: Phase 30 code review, WR-03; confirmed by the Phase 30 verifier; docstring half corrected in Phase 31 (D-14)
Related files:
- src/spur/parts.py:3-8
- src/spur/model.py (`_build_checked`, `_write_export`, typed `GearParams`)
- src/spur/records.py:171 (`_gear_fields`)

## Context
The Phase 30 review (WR-03) found that the `parts.py` docstring called widening `Part` a one-line
edit, which was false. Phase 31 corrected the docstring: it now names Phase 32 and the three
internals. What remains is the widening itself: `model.build`/`model.export` take `Part` but pass
it straight to `_build_checked(p: GearParams)` and `_write_export(..., p: GearParams, ...)`, and
`records._gear_fields` reads gear-only attributes, so widening `Part` fails `mypy --strict` there.

## Why it matters
The phase that makes model build a shaft cannot widen `Part` by editing `parts.py` alone. No
Phase 31 success criterion depends on it: nothing passes a `ShaftParams` to pool, records or model
before Phase 32.

## Next step
Phase 32 (trigger): in the change that makes model build a shaft, widen `Part` and type or
dispatch `_build_checked`, `_write_export` and `_gear_fields`. Resolve in that commit.
