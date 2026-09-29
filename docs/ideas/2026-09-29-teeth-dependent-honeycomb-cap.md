# A teeth- or module-dependent honeycomb cell-count cap

Date: 2026-09-29
Source: Phase 11 discuss-phase (11-CONTEXT.md Deferred Ideas)
Related files:
- src/spur/calc.py (`HEX_CELL_CAP`)
- docs/architecture/decision_log.md (L30, D-12)
- bench/RESULTS.md ("Honeycomb cell-count spike (Phase 11, D-24)")

## Context

D-12 rejected a teeth- or module-dependent cap in favour of one constant,
`HEX_CELL_CAP = 120`, measured at the heaviest configuration a honeycomb can sit on
(200 teeth, module 10, both recesses — the largest web, so the cap always binds). That
constant is conservative everywhere else: a small gear's web is a fraction of the
200-tooth/module-10 web's area, so the same cell count costs far less to cut there, and a
per-gear cap could let a small gear have more cells than 120 without approaching the
build-timeout share D-11 sets.

## Why it matters

Engineering headroom on small gears, at the cost of a dimension-dependent limit — exactly
the "what we have seen" style of bound D-12 and 08 D-07 both rejected once already,
unless the sweep actually shows cost falling with gear size rather than being assumed to.

## Next step

Revisit only if a user with a small gear needs more cells than `HEX_CELL_CAP` allows, and
a sweep at that gear's size shows cost per cell genuinely falls with gear size (not
assumed — measured, per this project's own standing rule).
