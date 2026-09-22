# Measure the Raspberry Pi 5 claim, or soften it

Date: 2026-09-22
Source: Phase 2 discussion (`.planning/phases/02-cad-off-the-event-loop/02-CONTEXT.md`)
Related files:
- README.md
- docs/tech_debt/active/2026-09-21-cad-builds-block-the-event-loop.md

## Context
The README advertises that this runs on a Raspberry Pi 5. Every performance number in the
tree comes from a 12-core development machine: the event-loop stall (0.22 s -> 0.76 s ->
2.00 s), the memory plateau behind L07, and whatever Phase 2 measures for the process pool.
Nothing here has ever been run on a Pi 5, or on any arm64 board.

## Why it matters
The debt file's own argument is that the stall is proportionally worse on slower hardware,
and the Pi 5 is the example it names. That makes the Pi the case the numbers matter most
for, and the only case with no numbers. Advertising hardware whose behaviour is unmeasured
is the shape of claim L08 exists to prevent - the difference being that this one is about
the tool rather than a dimension it prints.

## Next step
Revisit when someone actually has a Pi 5 (or another arm64 SBC) in hand: run the committed
bench harness on it, record the numbers next to the dev-machine ones, and either keep the
claim with evidence or soften the README to state the hardware the numbers came from.
Roughly a one-line README edit if nobody ever runs one.
