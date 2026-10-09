# gear-maths — tests

## Coverage

`tests/test_calc.py` — 70 test functions (405 collected cases), all unit-tier and pure.
They read as requirements:

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

`tests/test_trochoid.py` — 87 collected cases, calc-tier, no kernel build. Phase 18's
tiers (the cutter, the generator, the swept-cutter oracle, T1 to T4) and, from Phase 19,
the proofs of what `derive()` prints for the hob-cut root. Sentences are captured from
`derive()` on the day and typed in after, never composed in a test (L33); the radial one
is read from the pre-v0.2 fixture's JSON for the byte comparison.

From 19-04 (the root as a field, `root_shape`):

- `test_the_default_gear_asked_for_the_hob_root_prints_its_numbers_and_no_radial_ones` —
  `root_thickness` and `root_gap` null, `root_fillet` the radius cut, one sentence saying
  why, and the eight root-independent numbers equal to the radial document's.
- `test_a_trochoid_request_with_nothing_radial_to_replace_prints_the_radial_numbers_and_says_so`
  — 41 and 42 teeth either side of `rb = rf`: the refused request prints the radial
  thickness, gap and fillet with its refusal sentence, never the hob's nulls.
- `test_a_link_that_spells_the_default_root_shape_is_the_link_that_omits_it` — equal,
  equally hashed, deriving the same document (L05).
- `test_every_pre_v0_2_record_reads_radial_because_nobody_asked` — all 44 fixture records
  read `radial` / `not requested` with no cutter, curve or warning, through the call every
  consumer makes.

From 19-06 (the numbers and sentences beside it):

- `test_root_form_d_is_twice_the_junction_radius_and_null_when_radial` — 30.558 on the
  default gear, checked against `sqrt(rb^2 + xi^2)` written out in the test; 9.451 on the
  10-tooth crossing; null in radial mode, on a refused request and on all 44 records.
- `test_the_root_waist_is_printed_where_the_trochoid_applies_and_null_elsewhere` — 3.303
  on the default gear, equal to the involute's own thickness at the junction through
  `Profile.half_angle` (an independent check, not the curve); 1.442 on the crossing,
  below the involute's 1.622 there.
- `test_the_printed_waist_is_the_narrowest_arc_of_the_root_on_a_crossing_join` — three
  crossing gears, the printed waist within one print step of the smallest of 20,001
  samples of `2 R h`, and the smallest-half-angle reading at least 0.03 mm over it.
- `test_the_thin_waist_warning_fires_where_the_smallest_half_angle_read_over_the_floor` —
  8 teeth at shift -0.5132 and 6 teeth at -0.3103 (module 1, 14.5 degrees): 0.395 and
  0.391 mm warn where the smallest-half-angle reading, 0.401, was silent.
- `test_the_waist_warning_fires_one_print_step_below_the_floor_and_not_at_it` — two
  series of the 19-02 walk, the profile shift bisected until the printed waist is 0.4 and
  then 0.399: silent at the floor, one sentence one step under, the gear valid either way.
- `test_the_restated_undercut_sentence_fires_at_17_teeth_and_not_18` — the cutter's onset
  and shift in the sentence, no radial-root wording, a tangent join silent; rows where the
  join and the shipped line disagree (a sharp cutter at 18 teeth, 14.5 degrees at 30 and
  31 teeth).
- `test_the_advised_shift_is_rounded_up_and_flips_the_gear_out_of_undercut` — the cutter's
  roll at the printed shift is non-negative and at one step below it negative; a bound
  that is an exact multiple does not climb a step (float residue removed first).
- `test_a_shift_above_the_field_s_range_is_never_advised` — no shift printed above the
  field's 1.0 (8 teeth at 14.5 degrees prints 1.000, 7 teeth at 15.5 degrees none), and
  `PROFILE_SHIFT_MAX` equal to the schema's maximum.
- `test_the_onset_is_the_trimmed_cutter_s` — a request of 3.0 mm is cut at 0.471 and the
  sentence is that cutter's.
- `test_a_refused_trochoid_request_keeps_the_shipped_undercut_sentence` — the severed
  tooth beside the shipped sentence, byte for byte the fixture's.
- `test_the_trimmed_tip_radius_is_printed_and_warned_one_step_either_side_of_the_cap` —
  0.471 silent, 0.472 trimmed to 0.471 with the cap sentence, 0.4715 used as given and
  silent, 0 a legal sharp hob.
- `test_every_root_sentence_is_ascii_and_in_a_fixed_order` — one gear firing five
  sentences, its whole warnings tuple in order, every sentence ASCII.

`tests/test_api.py` pins the 31-name `DerivedDimensions` set and the units of
`root_form_d` and `root_waist` (mm), and
`test_root_form_d_is_never_labelled_an_iso_form_diameter_where_a_user_reads_it` keeps the
phrase out of the UI label and the field description (D-04).

## Gaps

- No property-based test over the whole feasible parameter space; the centre-distance
  sweep is the closest thing and it is hand-rolled.
- The gate holds one coverage floor over the whole package, `fail_under = 96` (L34);
  `calc.py` has no floor of its own.

## Run

```
make verify          # the whole gate
make test            # just pytest
.venv/bin/python -m pytest tests/test_calc.py -q
```
