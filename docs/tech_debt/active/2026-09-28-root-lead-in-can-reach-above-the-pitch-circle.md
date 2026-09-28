# The root fillet's straight lead-in can reach above the pitch circle

Severity: must
Status: active
Date: 2026-09-28
Source: 10-01's tip-chamfer spike
Related files:
- src/spur/calc.py (spline_start)
- src/spur/model.py (_outline)
- README.md (the Geometry notes root-fillets bullet)

## Context

`spline_start` lifts the involute spline's start to `rf + 2 x root_fillet` (capped
halfway up the tooth) when the fillet needs room, and `_outline` runs a straight chord
from the root up to it. Measured planning-time (pinned code, 2026-09-28): the chord
deviates from the true involute by up to 35.29 um on the default gear, 32.28 um at
`{profile_shift 1.0, pressure_angle 14.5}` and 31.73 um at `{profile_shift 0.75,
pressure_angle 20}`. The spline's start sits 1.1875 mm *below* the pitch circle on the
default gear (with its 0.5 mm root fillet) — the "non-working root zone" README
describes — but 0.5625 mm *above* it at `{profile_shift 1.0, pressure_angle 14.5}` and
0.125 mm above at `{profile_shift 0.75, pressure_angle 20}`.

So README's "in the non-working root zone" is false for a gear with a large profile
shift and the default root fillet: part of what README calls non-working is, on those
configurations, above the pitch circle — the working flank. This predates Phase 10;
10-01 found it only because the tip chamfer's kernel boundary (`ra - spline_start`)
turned out to be the same radius.

## Why it matters

On a large profile shift with a root fillet that is large for the module, part of the
working flank is a chord up to about 35 um off the true involute, while README says the
chord sits in the non-working zone (L08: a claim the tool makes about the part must be
true, or reported as a warning, never left standing as false).

## Next step

Decide between keeping the lead-in below the active profile's start (a change to every
such gear's outline: a fixture regeneration with its own `Lxx`, per L05) and correcting
the README sentence to state the limit accurately. Revisit when a profile-shifted
gear's flank is measured, L10's trochoidal-root idea is taken up, or `_outline` is next
touched.
