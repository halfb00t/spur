# The shaft has no contention row: its heaviest build is measured alone, never under concurrent requests

Severity: nice
Status: resolved
Resolved in: docs(bench): the heaviest shaft under ten concurrent requests (D-19) (gsd/phase-33-interfaces-and-parity)
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
declined at the checkpoint. Plan 32-05's single builds are in `bench/RESULTS.md`
`### The heaviest shaft (32-05)`: the heaviest allowed shaft takes 2.23 s on macOS (13.5x
margin to the 30 s timeout) and 5.44 s in the Linux container (5.5x, amd64 emulated). The
research's earlier figure of about 5.5x at load 30+ is the only evidence about the shaft
under load.

## Why it matters
A shaft build that fits 30 s alone could still time out when a queue of them shares two
workers. Until a row says otherwise, the margin under contention is an estimate, not a
measurement.

## Next step
Revisit when Phase 33 adds `/api/shaft/model.{fmt}`: record the heaviest shaft row under
ten concurrent requests the way L37 did for the gear, then resolve this item.

## Resolution
`bench/RESULTS.md` `### The heaviest shaft under ten concurrent requests (33-09)`: the heaviest allowed
shaft through `/api/shaft/model.stl` on a fresh `spur serve` at the shipping defaults, ten distinct keys and
then one key ten times. Four of ten admitted and answered 200 in each run, six refused 503 `busy`, no
timeout, no `pool_broken`, no 500, no worker replaced. The slowest 200 was 10.16 s of the 30 s timeout.
