# The concurrent latency bar was waived, not demonstrated

Severity: must
Status: resolved
Date: 2026-09-23
Resolved in: docs(13-07): log L32 and retire the concurrent latency-bar debt
Source: quick task 260923-qwr and its two re-runs (bench/RESULTS.md Runs 5-8); the human's
waiver of broken-windows ledger item 1 (.planning/WINDOWS.md)
Related files:
- bench/RESULTS.md ("Post-fix re-run (Runs 5-6)", "Idle-host re-run (Runs 7-8)")
- bench/latency.py (`scenario_concurrent`, `MIN_SAMPLES`, `_p95`)
- src/spur/app.py (`model()`, `_build_slot`, `_GZIP_LEVEL`)

## Context

`REQ-cad-off-event-loop`'s acceptance clause for the `concurrent` scenario is "under-load
p95 <= 2.00x idle p95". Eight runs over four sessions never met it on both runs of one
session: pre-fix 2.02x/2.45x and 2.32x/2.35x; post-fix (gzip level 1 from measurement,
model-body compression inside the admission slot and cached -- `2d47994`, `7a61fad`)
1.31x/2.10x and 1.86x/2.02x, the last pair on a host a watcher had held below the file's
own 1.5 idle bar. On 2026-09-23 the human waived ledger item 1 on that evidence rather
than re-run again or fix further.

Two things the record shows that nobody has explained:

1. Every second run of a pair -- the one inheriting the first run's `_EXPORTS` -- is
   worse than its first, before and after the fix (2.02 -> 2.45, 2.32 -> 2.35,
   1.31 -> 2.10, 1.86 -> 2.02). Post-fix those cache hits do no compression and take no
   slot (`tests/test_api.py::test_an_already_compressed_download_needs_no_slot_at_all`),
   so it is not the mechanism the fix removed. Candidates neither ruled in nor out: four
   instant ~2.6 MB sends from the loop thread at t=0; worker-side state after the first
   batch; a shorter load window (n=7719 vs n=10527) read at the floor.
2. The verdict sits at the harness's resolution floor: idle p95 is 0.6 ms in six of the
   eight runs, so the bar is about 1.2 ms of under-load p95, and passes and misses are
   separated by roughly 0.1 ms.

## Why it matters

The numbers 02-05 writes into L17/L18 and the container `HEALTHCHECK` timeout will cite a
bar that was accepted, not demonstrated; anyone reading "<= 2x" there as measured fact
would be reading the plausible-looking record L08 forbids. And near the bar,
`bench.latency`'s pass/fail is not reproducible on this machine, so the harness cannot
currently catch a regression of the size it was built to catch.

## Next step

A bounded investigation, no `src/` or `bench/` changes, in the shape of
`.planning/phases/02-cad-off-the-event-loop/02-LATENCY-INVESTIGATION.md`: run the pair
with a server restart between runs, and with the poller in its own process, and see which
of the three candidates above survives. If a warm-cache second run turns out to measure
something other than the event loop, change what the harness measures (restart between
runs, or a higher sample floor) as a logged decision, not a tune toward a pass.

Revisit when: 02-05 writes L17/L18 (carry this caveat verbatim), the harness or the
machine changes, or any run reads above 2.45x (the pre-fix worst), or the composed worst
row of bench/RESULTS.md "Composed build and export time (Phase 12)" is measured under ten
concurrent builds -- the question the tip-chamfer margin debt left open, re-homed here
when it was resolved (12-CONTEXT.md D-04).

## Resolution (2026-10-02)

Phase 13 ran the bounded investigation this file's "Next step" prescribed
(`.planning/phases/13-latency-bar/13-LATENCY-INVESTIGATION.md`) and the decisive bar
session this file's own acceptance clause needed. Observation 1 (every second run of a
pair reads worse) was **not reproduced in this environment**: Pair A split between its two
repetitions (A1 worse, A2 not worse), and the pre-registered rule states that when Pair A
does not point worse, no candidate is ruled in or out and Pairs B/C's own directions cannot
decide it (`13-LATENCY-INVESTIGATION.md` § Verdict § Observation 1). Observation 2 (the
verdict sits at the harness's resolution floor) was ruled to candidate (ii), "the floor is
real": four of twenty-four (run, source) verdict cells flip inside one percentile
(`13-LATENCY-INVESTIGATION.md` § Verdict § Observation 2). Neither finding is a server
defect, so neither was filed as debt (D-17).

The bar itself was then **demonstrated, not waived**: after two non-decisive attempts
(bar-1, bar-2) capped out on the quiet gate, bar-3 released after 320 s and both runs of
the `concurrent` scenario read under the 2.00x pass bar -- Run 13 printed 1.31x, Run 14
printed 1.42x (`bench/RESULTS.md` § "Bar session bar-3 (Runs 13-14)"). Outcome (a).

The composed worst row (29.42 s alone, re-homed here from the resolved tip-chamfer debt)
was then measured under ten concurrent builds, the question this file's "Revisit when"
named. It did not complete: 0 of 10 requests served, 6 of 10 refused by admission control,
4 of 10 admitted and all four exceeded `SPUR_BUILD_TIMEOUT` -- two via the documented
`BuildTimeout` path, two via an undocumented `500` from a same-slot timeout-cleanup race
(`bench/RESULTS.md` § "Composed worst row under ten concurrent builds (Phase 13)"). That
crash, and the worst row's own margin disappearing under this contention, are filed as
their own must-severity debt:
`docs/tech_debt/active/2026-10-02-same-slot-timeout-cleanup-race-produces-undocumented-500.md`.

All three findings are logged in `docs/architecture/decision_log.md` L32 (amends L18),
append-only.

<!-- On resolve: set Status: resolved, add `Resolved in: <commit sha>`,
     git mv into resolved/, move the INDEX row to Resolved — same commit as the fix. -->
