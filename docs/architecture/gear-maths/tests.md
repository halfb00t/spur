# gear-maths — tests

## Coverage

`tests/test_calc.py` — 21 tests, all unit-tier and pure. They read as requirements:

- `test_default_dimensions` — the stock gear's numbers, pinned.
- `test_caliper_reading_is_short_for_odd_tooth_counts` — the odd-tooth caliper
  correction, which is the measurement aid users trust most.
- `test_span_measurement` — three hand-checked Wildhaber spans.
- `test_tooth_thickness_and_gap_are_measured_on_the_same_circle` — the F6 regression:
  `root_thickness + root_gap` must equal the root-circle pitch, checked for both
  `rb > rf` (z=19) and `rf > rb` (z=40).
- `test_centre_distance_matches_an_independent_solver` — sweeps a grid of teeth,
  pressure angles, shifts and mates and compares against a bisection reference written
  in the test itself. This is the guard on L08.
- `test_impossible_pairs_have_no_centre_distance` — the two F1 reproductions.
- The cap-and-warn contract (L03): root fillet capped, recess narrowed, recess dropped,
  recess fillet capped to the narrowed groove, small gear still buildable at stock
  defaults — each asserting the *warning text*, not just the number.
- `test_infeasible_parameters_name_their_fields` — every refusal names the field the
  user has to change.

## Gaps

- No property-based test over the whole feasible parameter space; the centre-distance
  sweep is the closest thing and it is hand-rolled.
- The module has no coverage floor in the gate yet (L14 note, and
  `docs/tech_debt/active/2026-09-21-no-coverage-floor.md`).

## Run

```
make verify          # the whole gate
make test            # just pytest
.venv/bin/python -m pytest tests/test_calc.py -q
```
