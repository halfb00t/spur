# The two relations calc does not back: recess_* under recess_sides=none, bore_flat at bore_d=0

Date: 2026-10-11
Source: Phase 23 kickoff decision 8 (REQUIREMENTS.md "Form follow-ups (v0.5.x)") and PITFALLS CF-2
Related files:
- src/spur/params.py
- src/spur/calc.py (`derive()` warns about neither case)
- tests/regression/pre_v0_2.json

## Context
MEASURED (CF-2): `recess_sides=none` with `recess_depth=3` answers 200 with no warning, and
`bore_d=0` with `bore_flat=5` answers 200 with no warning and no D-flat cut. L41 declares
only relations calc backs, so the form leaves these fields live. 14 fixture records sit on
these defaults (10 recess, 4 `bore_d=0`, READ at kickoff).

ASSUMPTION: filed as an idea per kickoff decision 8; PITFALLS CF-2 calls the bore_flat
silence a pre-existing L08-shaped gap, which the human may prefer to carry as debt.

## Why it matters
Two more states where a set value does nothing and neither the server nor the form says so.
The `bore_flat` case is an L08-shaped silence.

## Next step
The warning first: a `calc` warning per case, in a commit and an `Lxx` of its own with the
fixture regenerated (L26 D-03), since it rewrites `warnings` for those 14 records. Only then
a relation each. Neither fits L41's grammar as it stands: `recess_*` would be gated on a
`Literal` (D-03 says a `Literal` gate arrives with its own op and decision), and
`bore_flat <- bore_d gt 0` would make `bore_d` both a dependent and a driver (depth 1).
Revisit when a user reports a recess or D-flat value that did nothing, or when a fixture
regen is planned for another reason.
