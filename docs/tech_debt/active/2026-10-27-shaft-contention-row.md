# The shaft has no contention row: its heaviest build is measured alone, never under concurrent requests

Severity: nice
Status: active
Date: 2026-10-27
Source: Phase 32 plan 32-01, checkpoint decision D (picked by the human: D1, single-build rows only)
Related files:
- bench/build_time.py
- bench/RESULTS.md (`### The heaviest shaft (32-05)`, added by plan 32-05)
- src/spur/pool.py

## Context
L37 recorded the gear's heaviest row under ten concurrent builds. Phase 32 measures the
heaviest allowed shaft only as single builds, each in a fresh process on macOS and in a
Linux container, beside the 199-tooth gear (REQ-shaft-build-measured). No shaft route
exists before Phase 33, so a server-driven run cannot happen in Phase 32, and a pool-level
row (ten distinct heaviest shaft rows at once to `BuildPool(workers=2, timeout=30)`) was
declined at the checkpoint. The research measured about 5.5x margin to the 30 s timeout at
load 30+, which is the only evidence about the shaft under load.

## Why it matters
A shaft build that fits 30 s alone could still time out when a queue of them shares two
workers. Until a row says otherwise, the margin under contention is an estimate, not a
measurement.

## Next step
Revisit when Phase 33 adds `/api/shaft/model.{fmt}`: record the heaviest shaft row under
ten concurrent requests the way L37 did for the gear, then resolve this item.
