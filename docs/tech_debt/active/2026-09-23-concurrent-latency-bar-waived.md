# The concurrent latency bar was waived, not demonstrated

Severity: must
Status: active
Date: 2026-09-23
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
machine changes, or any run reads above 2.45x (the pre-fix worst).

<!-- On resolve: set Status: resolved, add `Resolved in: <commit sha>`,
     git mv into resolved/, move the INDEX row to Resolved — same commit as the fix. -->
