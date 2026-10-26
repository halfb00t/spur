# DIN 5480 anchor rows beyond Part 1 are missing: the Phase 31 checkpoint passed only partly

Severity: must
Status: active
Date: 2026-10-26
Source: Phase 31 plan 31-05, the D-06 checkpoint. The human read an unofficial English translation of DIN 5480-1:2006-03 and found that Part 1 holds no basic-dimension size tables, so the plan's anchor minimum (two basic-dimension rows, W30x2x14 ideally) could not be met. The human decided: partial pass, plus this item.
Related files:
- .planning/phases/31-shaft-maths-parameters-and-designation/31-05-SUMMARY.md (`## Checkpoint result`)
- src/spur/din5480.py:30 (H_FP), :34 (X_MAX), :143 (form_diameter)
- src/spur/shaft_calc.py:46 (ODD_Z_UNCONFIRMED), :105 (check_shaft)
- .planning/ROADMAP.md (Phase 34, the human's private fit tables)

## Context
Only one designation, W 120x3x38x8f, has rows from the copy (three values, approved by name, cited to
DIN 5480-1:2006-03 cl. 9.1, Fig. 6; Fig. 6 is an example, not normative). The other designations the
code is predicted for have no copy row behind them: W 25x1.25x18, W 25x1.25x19 (odd z), W 30x2x14 and
W 70x3x22. The clause source for the measurement over pins (the copy's Part 1 points to DIN 5480-15
cl. 5.2.4.3 and to Part 2) and for the gauge pin series is also outside Part 1, and no Part 2 row
shows whether the standard prints a construction value for the form diameter d_Ff or only a limit.

## Why it matters
A number the tool prints is a number someone will cut metal to (L08). Until a second size and an odd
tooth count are checked against the standard, the formulas are proven at one point of the size range:
the odd-z measurement over pins stays unprinted (D-13), the form diameter stays unprinted (D-12),
and the pin diameter stays the computed theoretical pin, not the standard's tabulated one.

## Next step
Revisit when pages of DIN 5480 Part 2 or Part 15 become available. Then, with the human approving
each value by name (nothing else of the copy enters the repo):
- anchor rows for W25x1.25x18, W30x2x14 and an odd-z designation (W25x1.25x19), each with part, clause and table;
- the clause source of D_Re / M_Re (Part 15, 5.2.4.3 as Part 1 points to it) and any gauge pin series;
- a construction d_Ff value if Part 2 prints one (otherwise d_Ff stays a limit, checked as predicted <= printed max for shafts);
- then remove the odd-z gate and the unproven-form warning only if the rows agree to the last printed digit.

<!-- On resolve: set Status: resolved, add `Resolved in: <commit sha>`,
     git mv into resolved/, move the INDEX row to Resolved — same commit as the fix. -->
