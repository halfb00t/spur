# CAD builds block the event loop

Severity: must
Status: active
Date: 2026-09-21
Source: docs/review-2026-09-21.md F4, and its plan's "Deliberately not done"
Related files:
- src/spur/model.py:36 (`_LOCK`)
- src/spur/app.py (`_build_slot`)

## Context

OpenCascade holds the GIL while it works, and every build serialises on one lock (L06).
A single large gear therefore stalls the whole async event loop for a second or two.
Measured: with one 200-tooth fine build in flight, `/api/health` went `0.22 s → 0.76 s →
2.00 s` before recovering; with ten concurrent builds it repeatedly exceeded 5 s.

What was done instead of fixing it: admission control bounds the queue (L04, `503` +
`Retry-After`), and the Docker `HEALTHCHECK` timeout was raised to 10 s so a legitimate
stall no longer marks the container unhealthy. Both accommodate the problem; neither
removes it.

## Why it matters

The root cause is untouched. Liveness is coupled to how big a gear someone asked for. On
slower hardware than the 12-core machine these numbers came from — the README advertises
a Raspberry Pi 5 — the stall is proportionally worse, and the 10 s timeout is the only
thing between it and a restart loop.

## Next step

Move CAD work to a process pool so the kernel runs outside the event loop's process.
That changes the caching story (caches are per process today, L07) and the memory
ceiling formula, so it is a phase of its own, not a patch.

Revisit when: more than one concurrent user is real, or a health probe fails in an
environment that matters.
