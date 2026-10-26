# The shaft profile-shift cap refuses shifts DIN 5480-1 allows as exceptions at larger tooth counts

Severity: must
Status: active
Date: 2026-10-26
Source: Phase 31 plan 31-05 checkpoint, divergence D3 (the human's reading of DIN 5480-1:2006-03 cl. 4 and Table 3).
Related files:
- src/spur/din5480.py:34 (X_MAX)
- src/spur/shaft_calc.py:105 (check_shaft)
- .planning/phases/31-shaft-maths-parameters-and-designation/31-05-SUMMARY.md (`## Checkpoint result`, D3)

## Context
`X_MAX = 0.45` is enforced by `check_shaft`, which answers `422` for a larger shift. DIN 5480-1 cl. 4 /
Table 3 allows exceptions at larger z1. The z-dependent limits are not in the repo and are not quoted here.

## Why it matters
A valid standard shaft is turned away. No wrong number is printed: the refusal errs on the honest side
(L08, L03).

## Next step
Revisit when Part 2, or the copy's exception table, gives the z-dependent limits. Then replace the
constant with a function of the tooth count, citing the clause, and update the `form_diameter` validity comment.

<!-- On resolve: set Status: resolved, add `Resolved in: <commit sha>`,
     git mv into resolved/, move the INDEX row to Resolved — same commit as the fix. -->
