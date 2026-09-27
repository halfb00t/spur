# A round bore's chamfer reach is not checked against the root circle

Severity: must
Status: active
Date: 2026-09-26
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

<!-- On resolve: set Status: resolved, add `Resolved in: <commit sha>`,
     git mv into resolved/, move the INDEX row to Resolved — same commit as the fix. -->
