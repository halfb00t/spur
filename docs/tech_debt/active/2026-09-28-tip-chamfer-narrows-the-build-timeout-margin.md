# A 200-tooth tip chamfer narrows SPUR_BUILD_TIMEOUT's margin

Severity: must
Status: active
Date: 2026-09-28
Source: 10-04's sweep
Related files:
- src/spur/app.py (the `SPUR_BUILD_TIMEOUT` line)
- src/spur/model.py (`_chamfer_tips`)
- bench/RESULTS.md ("### `SPUR_BUILD_TIMEOUT`", "## Tooth-tip chamfer build and export
  time (Phase 10)")

## Context
`bench/RESULTS.md`'s `SPUR_BUILD_TIMEOUT` section set the 30 s default at about 4x the
7.39 s worst single build already on record (200 teeth, ten concurrent requests). 10-04's
9-row sweep measured the heaviest 200-tooth tip-chamfer configuration (module 1.75, `c`
1.75 mm, both recesses) at **14.87 s of 30 s** -- Build + slower export -- driven almost
entirely by the chamfer operator itself, exactly as 10-01's spike found (12.50-12.81 s of
chamfer time on the same 400-edge case). That leaves the timeout only `30 / 14.87 ~= 2.0x`
of margin, half of the 4x the default was originally sized against. The sweep builds one
gear at a time; nothing here measures the chamfer under concurrent load.

## Why it matters
A request that runs past `SPUR_BUILD_TIMEOUT` is a 503, not a part (L08's flip side: no
number is better than the wrong number, and no part is better than a stalled worker). The
worst plain 200-tooth build already ran 7.39 s under ten concurrent requests before this
phase; a tip-chamfered 200-tooth gear -- now the single most expensive operation this
project has measured -- has never been measured under that same concurrent load. A host
slower than this M2 Max, or a few concurrent tip-chamfered requests stacking kernel work,
could plausibly cross 30 s where the single-gear sweep here still reads comfortably
inside it.

## Next step
Measure a 200-tooth tip-chamfered gear under `bench.latency`'s ten-concurrent scenario, or
fold it into Phase 12's composed sweep (module x every Phase 8-11 feature). Then choose
between raising `SPUR_BUILD_TIMEOUT`'s default with a new `Lxx` backed by that
measurement, or D-07's second offer -- a teeth-dependent analytic cap derived from the
measured per-edge cost, warned per request.

## Revisit when
Phase 12's composed sweep runs, a `BuildTimeout` is logged in production for a gear with
`tip_chamfer` above 0, or the service is deployed on hardware slower than this host.
