# The root fillet's straight lead-in can reach above the pitch circle

Severity: must
Status: resolved
Date: 2026-09-28
Resolved in: docs(14-01): state where the root lead-in really ends and retire its debt
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

## Resolution (2026-10-03)

Phase 14 took the second path of "Next step": warned and corrected the record, did not
re-cut the outline (the kickoff choice; REQUIREMENTS.md "Out of Scope" keeps the outline
change under "Future Requirements -> Precision"). `calc.derive` now warns when the chord
ends above the pitch circle (13857e1, `feat(14-01)`), naming the height at 3 dp; the
warning is proven at each step either side of the crossing on `profile_shift`,
`root_fillet` and `module`, at the mid-tooth floor, with no fillet and at the print
resolution (ac607d7, `test(14-01)`). README's root-fillets bullet and `_outline`'s
docstring no longer call the chord non-working: README states the condition (the root
fillet exceeds half the dedendum, `(1.25 - x)*m/2`, and the profile shift exceeds 0.125)
and the default gear's 1.188 mm below the pitch circle, and cites `warnings`.

The heights the tests assert are the three this file measured: -1.1875 mm on the default
gear, +0.5625 mm at `{profile_shift 1.0, pressure_angle 14.5}` (prints 0.562: Python
rounds the binary 0.5625 half-to-even) and +0.125 mm at `{profile_shift 0.75,
pressure_angle 20}`. The chord-to-involute deviation figures in "Context" (35.29, 32.28,
31.73 um) stay what they were, planning-time numbers no script in the repo produced: the
warning quotes none of them and README quotes none (14-CONTEXT.md D-02, D-12). Decision
log L33 records the choice.

<!-- On resolve: set Status: resolved, add `Resolved in: <commit sha>`,
     git mv into resolved/, move the INDEX row to Resolved — same commit as the fix. -->
