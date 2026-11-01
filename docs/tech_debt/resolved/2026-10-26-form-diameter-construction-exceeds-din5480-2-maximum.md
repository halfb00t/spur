# The internal form-diameter construction sits above DIN 5480-2's d_Ff1 maximum on most rows

Severity: must
Status: resolved
Resolved in: 1fa8deb feat(shaft): the pin-contact guard starts at DIN 5480-2's d_Ff1 maximum (D-12) (gsd/phase-34-fit-tables-and-tolerance-window)
Date: 2026-10-26
Source: The Phase 31 follow-up that compared every size table of DIN 5480-2:2006-05 with `spur.din5480`. This was a scratch comparison; no Part 2 value beyond the four approved rows is committed.
Related files:
- src/spur/din5480.py (`form_diameter`, `RHO_FP`)
- src/spur/shaft_calc.py (`pin_contact_window`)
- tests/test_din5480_anchors.py (`test_anchor_w120x3x38x8f_form_diameter_is_a_limit_not_a_construction`)
- docs/architecture/decision_log.md (L47, **The guard**)

## Context
`din5480.form_diameter` is the pin-contact guard's internal lower bound. It is never printed: `form_d` is null for every shaft. L47 states that it stays at or below the standard's form-diameter maximum, but that was checked on one Part 1 row only. Against the 719 Part 2 nominal rows whose own columns agree with each other:
- At h_fP 0.55 and rho_fP 0.16, the construction exceeds the printed d_Ff1 maximum by more than the printed half unit on 483 rows.
- At h_fP 0.60 (hobbing), it does so on 44 rows.
- (construction - maximum)/m runs from -0.031 to +0.174, median +0.019. The largest gaps are at small tooth counts.

L47's guard margin was sized from two gaps of at most 0.202 mm at m 3 (0.067*m). The new largest gap is 0.174*m.

## Why it matters
Nothing printed is wrong today. `form_d` is null, and the guard cannot fire from `derive_shaft`, because the theoretical pin touches at least 0.62*m above the construction (L47).

In Phase 34 the tabulated pin replaces the computed one and the guard goes live. A lower bound that sits above the standard's own form-circle limit narrows the window from below. The guard could then refuse a pin the standard tabulates, because its contact point sits below the construction.

## Next step
Revisit when Phase 34 makes the pin-contact guard live. Choose the guard's lower bound from the standard's d_Ff1 maximum (which needs the mating part's tip, Part 1 Tables 3 and 4) or from a construction that stays below it on every Part 2 row. Add a test over the approved rows that the bound stays at or below the maximum.

## Resolution
For a size the tables list, the guard's floor is the copy's own d_Ff1 maximum plus the margin, so the internal construction no longer narrows the window there. Off the tables the internal construction stays the floor and cannot fire (31 D-20). The margin is unchanged. 34-15 sweeps the real file and surfaces any row where a limit still leaves the window.
