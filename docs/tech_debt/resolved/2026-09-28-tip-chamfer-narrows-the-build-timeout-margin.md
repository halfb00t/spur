# A 200-tooth tip chamfer narrows SPUR_BUILD_TIMEOUT's margin

Severity: must
Status: resolved
Date: 2026-09-28
Resolved in: 89304e2
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

## Resolution (2026-09-30)

Phase 12's composed sweep (`bench/RESULTS.md` "Composed build and export time
(Phase 12)") folded the tip chamfer into the sweep this file's own "Next step" named --
every composed row stacks `tip_chamfer` at that gear's own cap with the pattern being
measured. The four rows that read over `SPUR_BUILD_TIMEOUT` in all four runs taken were
exactly the `spoke_count=40` rows (module 1.75 and 10, hex and keyed bore, each with
`tip_chamfer` at its cap): 31.16-33.32 s across loads from 12.66 down to 1.54. D-02 was
superseded for this gate (`### Gate`): the human found that four-run agreement -- not
tracking the load figure -- sufficient and treated Run 4 (load 1.54, the reference run) as
decisive rather than waiting on a fifth quiet run. D-03's probe (`### Gate probe`) found
`spoke_count` 32 the largest count that keeps the module=10 keyed-bore spokes+tip_chamfer=3
row inside budget (29.41 s of 30 s; 33 read 30.11 s, over again).

The human chose that offer (12-03-SUMMARY.md, Task 2, verbatim: "lower-le: spoke_count 32
(Recommended)"). `spoke_count`'s `le` moved from 40 to 32 (`547214e`), and the re-run
(`bench/RESULTS.md` "### Re-run after the gate (lower-le: spoke_count 32)") confirms every
row of the composed sweep, including every tip-chamfer-bearing one, now reads inside 30 s
-- heaviest 29.42 s of 30 s, 0.58 s of margin (~1.02x), the same pattern that was over
budget at `spoke_count=40`.

Decision: a lowered `le` on the co-occurring feature (`spoke_count` 40 -> 32), not a
raised `SPUR_BUILD_TIMEOUT` default or a teeth-dependent cap on the chamfer itself --
D-03 rejected the latter twice (10 D-07, 11 D-12). This file's own "Next step" second
option (raising the timeout with a new `Lxx`) was not taken; the composed measurement
showed a lower `le` on the feature it stacks with was enough.

This file's own concurrent-load question ("nothing here measures the chamfer under
concurrent load") was not run here either (D-04): the composed sweep builds one gear at a
time. That question now lives in
`docs/tech_debt/active/2026-09-23-concurrent-latency-bar-waived.md`, whose "Revisit when"
trigger gained a sentence naming this resolution.
