# The gear's result rows from its schema, not a JavaScript table

Date: 2026-10-27
Source: Phase 33 plan 33-01's assumption-delta decision, accepted add-alongside, shipped in 33-06
Related files:
- src/spur/static/app.js (`const DIMS = [`, `renderInfo`)
- src/spur/shaft_params.py (the shaft schema's `dims`)
- docs/architecture/decision_log.md (L49, **The part switch**)

## Context
The page reads the shaft's result rows from the `dims` list of `/api/shaft/schema`, and the
gear's from a table in `app.js`. The two sit side by side in `renderInfo` because the gear
`/api/schema` bytes are frozen (`make gear.unchanged`), so the gear schema cannot grow a `dims` key.

## Why it matters
A part added later would have to choose one of the two, and a row added to the gear needs an edit
in `app.js` where a shaft row needs none. One source of rows would remove the table and its key test.

## Next step
Revisit when a milestone lifts the byte equality of the gear `/api/schema`, or when a third part
type is added: then the gear's rows move into its schema as `dims`, the `DIMS` table and the pin
that reads it go, and `renderInfo` has one branch.
