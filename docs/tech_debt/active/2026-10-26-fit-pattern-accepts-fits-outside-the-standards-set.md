# FIT_PATTERN accepts deviation letters and tolerance classes outside DIN 5480-1 Table 7/9

Severity: nice
Status: active
Date: 2026-10-26
Source: Phase 31 plan 31-05 checkpoint, divergence D5 (the human's reading of DIN 5480-1:2006-03 Table 7 and Table 9).
Related files:
- src/spur/din5480.py:37 (FIT_PATTERN)
- .planning/phases/31-shaft-maths-parameters-and-designation/31-05-SUMMARY.md (`## Checkpoint result`, D5)

## Context
`FIT_PATTERN` checks shape only (digit(s) plus one lowercase letter). The standard's deviation letters and
tolerance classes are a bounded set (Table 7; Table 9 lists the common combinations), so
`W 25x1.25x18x3z` parses and is echoed in the designation.

## Why it matters
Low. `fit` feeds no computed number, so nothing wrong is printed as a measurement; only the designation
text can name a fit the standard does not have.

## Next step
Revisit when Phase 34 takes the fit tables: validate against the bounded set there, citing Table 7/9.

<!-- On resolve: set Status: resolved, add `Resolved in: <commit sha>`,
     git mv into resolved/, move the INDEX row to Resolved — same commit as the fix. -->
