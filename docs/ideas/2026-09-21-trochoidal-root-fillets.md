# Trochoidal root fillets for undercut gears

Date: 2026-09-21
Source: README geometry notes; recorded as a deliberate approximation in L10
Related files:
- src/spur/model.py (`_outline`, `_fillet_corner`)
- src/spur/calc.py (`derive` — the undercut warning)

## Context

Below the base circle the flank is radial, as in most gear generators. A real hobbed gear
has a trochoidal root there, produced by the cutter's tip sweeping past. The difference
only shows up on gears with few enough teeth to be undercut; `derive()` already warns when
the parameters are in that region.

## Why it matters

For anyone matching an existing cut gear at a low tooth count, the root shape is visibly
different from the real part, and the root stress concentration differs too. It does not
affect meshing at nominal centre distance, which is why it has been acceptable so far.

## Next step

Revisit when someone reports a low-tooth-count gear that does not fit, or when a request
for a mating pair below the undercut limit shows up. Scope would be: generate the
trochoid from the cutter geometry, keep the analytic fillet path for the normal case
(L09), and add a test comparing root shape against a known-good profile.
