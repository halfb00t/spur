# A round bore's chamfer reach is not checked against the root circle

Severity: must
Status: resolved
Date: 2026-09-26
Resolved in: fix(09-03): refuse a round or D-flat bore whose chamfered mouth reaches the
  root circle (D-12)
Source: Phase 8 planning probe (08-03-PLAN.md `<interfaces>`)
Related files:
- src/spur/calc.py (check()'s round branch; bore_mouth_limit)

## Context

`check()` refuses a round or D-flat bore past `rf - MIN_WALL`, but that rule ignores the
chamfer entirely — it compares `bore_radius(p)`, not `bore_mouth_limit(p)`. At that limit
the default 0.4 mm `bore_chamfer` puts the chamfered mouth on the root circle, and the
kernel fails after a timed build with "Geometry kernel failed (Standard_Failure); try
smaller fillets or chamfers." Measured 2026-09-26 on 19 and 40 teeth at chamfers of 0.4, 1
and 2 mm (`bore_d` 27.925 and 64.675, `bore_flat` 0). Phase 8 gave the hex bore the
matching rule (`bore_mouth_limit(p) > pr.rf - MIN_WALL`, naming `bore_chamfer` and
`bore_hex`); the round bore's equivalent gap was found in passing and left open, per L05
(a fix here would refuse links that build today).

## Why it matters

A direct dimensional conflict between `bore_d`/`bore_chamfer` and the root circle reaches
the CAD kernel instead of a 422 naming the offending fields (research PITFALLS.md
Pitfall 10). It costs a worker slot and minutes of build time before failing, and the
resulting message names no field the caller can act on.

## Next step

Decide, with a new `Lxx`, between refusing at `bore_mouth_limit(p) > rf - MIN_WALL`
(consistent with the hex rule, but it would refuse round links that build today with less
than `MIN_WALL` of wall — an L05 concern) and refusing only past the measured failure
point, then test one step either side of whichever boundary is chosen. Revisit when Phase
9 edits `check()`'s round branch for the keyway, or when a user reports the kernel error
at a bore near its root limit.

## Resolution (2026-09-27)

Phase 9 D-12 chose the measured failure point over `rf - MIN_WALL`: refusing at the hex's
margin would have refused round or D-flat links that build today with less than
`MIN_WALL` of wall (the L05 concern this file's "Next step" named).

`check()`'s round branch gained `elif p.bore_d > 0 and r_bore + p.bore_chamfer > pr.rf -
ROOT_CONTACT:`, an `elif` on the existing too-large rule so the two round rules never
stack, naming `bore_chamfer` and `bore_d`. `calc.ROOT_CONTACT` (1e-9 mm) is the new
constant: a chamfered round or D-flat bore mouth this close to the root circle counts as
touching it.

Re-measured 2026-09-27 on the pinned kernel (a 20-step bisection over 12 configurations —
8 to 200 teeth, module 0.5 to 10, chamfer 1 to 3 mm, round and D-flat): every one landed
identically — last failing gap -3.8e-8 mm, first building gap 1.9e-8 mm, a gap of exactly
0.0 mm failing on all 12, teeth-independent (unlike the hex corner, L27). `ROOT_CONTACT`
sits above the 1.8e-15 mm float residue of a step-aligned contact (`bore_d` 26.325,
`bore_chamfer` 1.2 on the default gear) and below every measured building gap; the
smallest non-zero step-aligned gap (0.0025 mm) built on all 12. One configuration (19
teeth, module 1.75, chamfer 2, round) failed to build at a gap of exactly 1e-9 mm even
though `check()` would accept it (`gap == ROOT_CONTACT` is not `< ROOT_CONTACT`) — a
sub-2e-8 mm residual band, orders of magnitude below the field's 0.05 mm step and
unreachable by any value a user or the API can set.

No link that built before is refused: the fixture's smallest round/D-flat gap
(`tests/regression/pre_v0_2.json`) is 1.775 mm, and the fixture stayed byte-unchanged
through the fix. `docs/architecture/decision_log.md` L28 records this decision.

<!-- On resolve: set Status: resolved, add `Resolved in: <commit sha>`,
     git mv into resolved/, move the INDEX row to Resolved — same commit as the fix. -->
