# Trochoidal root fillets for undercut gears

Date: 2026-09-21
Source: README geometry notes; recorded as a deliberate approximation in L10
Related files:
- src/spur/model.py (`_outline`, `_fillet_corner`)
- src/spur/calc.py (`derive` — the undercut warning; `root_mode`)
- docs/architecture/decision_log.md (L38)

## Context

Below the base circle the flank is radial, as in most gear generators. A real hobbed gear
has a trochoidal root there, produced by the cutter's tip sweeping past. The difference
only shows up on gears with few enough teeth to be undercut; `derive()` already warns when
the parameters are in that region.

Phase 19 shipped the hob root as an opt-in: `root_shape=trochoid` builds the root a hob
with tip radius `root_fillet` cuts, where the base circle lies above the root circle, with
every printed number beside it proved or warned (L38, which supersedes L10). The default
did not move: `root_shape` stays `radial`, so no shared link produces a different part.
What is still open is the default flip.

## Why it matters

For anyone matching an existing cut gear at a low tooth count, the root shape is visibly
different from the real part, and the root stress concentration differs too. It does not
affect meshing at nominal centre distance, which is why it has been acceptable so far.
Matching a hobbed gear is now possible by asking for the trochoid; flipping the default
would make it the answer without asking, at the price of moving the parts those links
build today.

## Next step

Revisit the default flip when someone reports a low-tooth-count gear that does not fit
(a real fit report), or when a request for a mating pair below the undercut limit shows
up (D-09 of Phase 19, recorded in L38). Not calendar-based. The flip is one commit under
its own `Lxx`: the predicate change, the `make fixture.regen` output, and the `Lxx` listing
the records that move before they move (L26 D-03). REQUIREMENTS.md "Trochoid follow-ups"
owns it; Phase 20 was recorded skipped for it.
