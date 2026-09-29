# A rotation field for spoke arms and lightening holes

Date: 2026-09-29
Source: Phase 11 discuss-phase (11-CONTEXT.md Deferred Ideas)
Related files:
- src/spur/params.py (Spokes, Holes groups)
- src/spur/model.py (`_spoke_cutters`, `_hole_cutters`)
- docs/architecture/decision_log.md (L30, D-03)

## Context

D-03 fixes arm 0 and hole 0 on +X, one convention for both patterns, with no angle field
— nobody asked for one, and a third parameter on every interface for a case nobody has
is exactly the speculative flexibility CLAUDE.md's "keep it small" rejects. But a real
part can have a reason an arm or a hole needs to sit somewhere other than +X (clearing a
fastener, aligning with a mating feature), and that reason cannot be worked around today
except by re-exporting with the whole pattern rotated in a slicer or CAD tool after the
fact.

## Why it matters

Engineering flexibility for a real use case, at the cost of one more field per pattern
(`spoke_angle`, `hole_angle`) on every interface (UI, API, CLI) once it ships.

## Next step

Revisit when a real part needs an arm or hole elsewhere than +X. The safe undo is an
additive field defaulting to the +X position D-03 already ships, so no existing
shareable link changes meaning (L05) when it lands.
