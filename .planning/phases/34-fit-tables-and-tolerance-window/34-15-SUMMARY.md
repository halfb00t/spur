---
phase: 34-fit-tables-and-tolerance-window
plan: 15
subsystem: testing
tags: [din5480, sweeps, anchors, checkpoint, l08, private-file]

requires:
  - phase: 34-fit-tables-and-tolerance-window
    provides: the assembled table file private/din5480-tables.json, 720 16 18 8 30 21 (34-14); derive_shaft and the guard (34-04, 34-06); the thickness-written solid (34-07)
provides:
  - "count-only sweeps of the guard and of the tooth's buildability over the real table file, with the page's own worked example checked through the whole stack"
  - "the human's range-edge reading (edge-upper) and an answer to each sweep finding"
  - "three designations approved by name and committed as tests: TABLE_7_ANCHORS, TABLE_7_THICKNESS, PART_2_CONTACT in tests/test_din5480_anchors.py, each seen red"
affects: [34-16, 34-17]

actuals:
  tokens: 9200
  tasks: 3
  commits: 2
plan_head_before: a6a374c5aa99eb5926764a7dab8aef9f8c3276ad
plan_head_after: f0bb198d523a5720be69d84a551a36f7079f26c4

tech-stack:
  added: []
  patterns:
    - "an approved anchor is split into cells (TABLE_7_ANCHORS), the limit thicknesses they give (TABLE_7_THICKNESS) and the Part 2 bound on the guard (PART_2_CONTACT), so the real-file check in 34-16 can hold the file to each constant exactly"

key-files:
  created:
    - .planning/phases/34-fit-tables-and-tolerance-window/investigation/34-15-sweeps.py
    - .planning/phases/34-fit-tables-and-tolerance-window/investigation/34-15-sweeps.log
    - .planning/phases/34-fit-tables-and-tolerance-window/investigation/34-15-red-anchors.log
  modified:
    - tests/test_din5480_anchors.py
    - bench/RESULTS.md

key-decisions:
  - "Range edge reads x < d_B <= y (edge-upper), confirmed by the human against page 24; Tables.column_for does not change and the default shaft takes its column by that reading"
  - "F1 accepted as printed: the 11 sizes the shift range refuses keep the honest 422 under the existing debt item; no new behaviour"
  - "F2 accepted: no action"

requirements-completed: [REQ-mre-limits, REQ-solid-max-material, REQ-fit-tolerance-window, REQ-tables-private-file]

coverage:
  - id: D1
    description: "The page's worked example comes out of the whole stack on the real file"
    requirement: "REQ-fit-tolerance-window"
    verification:
      - kind: other
        ref: "investigation/34-15-sweeps.log section 4: all four values PASS"
        status: pass
      - kind: test
        ref: "tests/test_din5480_anchors.py::test_anchor_table_7_cells_give_the_limit_thicknesses[W 120x3x38x8f], ::test_anchor_w120x3x38x8f_page_example_measure_over_pins_at_the_smallest_thickness"
        status: pass
    human_judgment: false
  - id: D2
    description: "The guard and the tooth's buildability swept over every tabulated size and fit or letter, extremes built"
    requirement: "REQ-mre-limits"
    verification:
      - kind: other
        ref: "investigation/34-15-sweeps.log sections 1, 1b, 2, 3: 0 nulls, 0 closed tips, 0 closed spaces, both extreme builds PASS"
        status: pass
    human_judgment: false
  - id: D3
    description: "Only approved values are committed, each seen red once"
    requirement: "REQ-tables-private-file"
    verification:
      - kind: other
        ref: "investigation/34-15-red-anchors.log: a failing run for A_s, T_G, T_act, T_eff and the thickness of every approved designation"
        status: pass
    human_judgment: true
    rationale: "The d_Ff1 cells are bounds and stay green under a last-digit change (see Deviations, item 1); the human judges whether 34-16's real-file check is enough for them"

duration: about 1 h across two sessions (the first ended at the Task 2 checkpoint)
completed: 2026-10-31
status: complete
---

# Phase 34 Plan 15: The sweeps on the real file, the human's anchors Summary

**The real table file was swept through the guard and the tooth's buildability with nothing null and nothing closed; the human settled the range edge as `x < d_B <= y`, accepted both sweep findings as printed, and approved three designations, which now stand as tests, each seen red.**

## Checkpoint result

Date: 2026-10-31. The human's reply, verbatim: "edge-upper; approve W 120x3x38x8f, W 25x1.25x18x8f, W 26x1.25x19x8f; F1 accept; F2 accept".

- **Option chosen:** `edge-upper`. "über x bis y" reads as x < d_B <= y, the DIN ISO 286 reading, confirmed by the human against page 24. The loader already reads it so, so `Tables.column_for` does not change and the default shaft W 25x1.25x18 takes its column by that reading. **34-16 needs no edge-reversal work**; it pins the reading with a test on each side of an edge.
- **Approved by name:** W 120x3x38x8f, W 25x1.25x18x8f, W 26x1.25x19x8f. No candidate was rejected.
- **F1 (11 sizes refused by the shift range), accepted as printed:** they keep the 422 under `docs/tech_debt/active/2026-10-26-shaft-shift-range-narrower-than-din-5480-exceptions.md`. Locations (module, d_B, z): 0.6/40/64, 0.6/47/76, 0.75/47/60, 0.75/50/64, 0.8/50/60, 0.8/55/66, 0.8/58/70, 1.25/78/60, 1.5/100/64, 1.75/110/60, 1.75/120/66. No new behaviour.
- **F2, accepted:** no action.

For 34-17 to log: edge-upper confirmed by the human against page 24 (L50's range-edge reading), and F1 accepted as printed.

## Sweep counts (investigation/34-15-sweeps.log)

| Sweep | Result |
|---|---|
| Table file | 720 sizes, 18 letters, 8 classes, 30 tolerance rows, 21 columns |
| Guard, fits per size | 144 (8 classes x 18 letters); 102096 combinations with a valid `ShaftParams`; 1584 refused (11 sizes, "infeasible model") |
| M_Re nominal / max / min | 102096 printed each; 0 null at the guard; 0 null for another reason |
| Sizes whose nominal M_Re is null though the copy prints its M1 | 0 |
| Cross-check without `derive_shaft` | 311040 readings, 0 outside the window, 0 touching no flank |
| Tip land and overlap | 12960 size x letter combinations; 0 closed tips; 0 closed spaces; 0 sizes without a column |
| Extreme builds | thinnest tip land (m=0.5 d_B=6 z=10, letter a) and thickest tooth (m=0.5 d_B=40 z=78, letter v): both PASS, one valid solid, volume within `VOLUME_REL` |
| Page example W 120x3x38x8f | the three thicknesses and M_Re min: PASS |
| Wall clock | guard 4.6 s, tip 0.0 s, probe total 11.8 s |

## Tests added

All in `tests/test_din5480_anchors.py` (the file went from 11 to 21 tests):

- `test_anchor_table_7_actual_and_effective_tolerances_add_up_to_the_total` (3 designations)
- `test_anchor_table_7_cells_give_the_limit_thicknesses` (3)
- `test_anchor_w120x3x38x8f_page_example_measure_over_pins_at_the_smallest_thickness` (1)
- `test_anchor_part_2_form_diameter_maximum_bounds_the_guard_below` (3), which also checks `part_2_provenance` against the clause, tables and pages the docstring cites

## Seen red

One failing run per cell, in a copy of the test file restored after each run (investigation/34-15-red-anchors.log; no value is logged).

| Anchor | Changed in its last printed digit | Result |
|---|---|---|
| W 120x3x38x8f | A_s, T_G, T_act, T_eff, s_vmax | red each |
| W 25x1.25x18x8f | A_s, T_G, T_act, T_eff, s_vmax | red each |
| W 26x1.25x19x8f | A_s, T_G, T_act, T_eff, s_vmax | red each |
| the three d_Ff1 cells | last digit | green (21 passed); a change that crosses the pin's contact: red |

## Task Commits

1. **Task 1 tracer: the sweeps on the real table file, counts only** - `f38d31b` (docs)
2. **Task 2:** checkpoint, answered by the human (above)
3. **Task 3: the approved anchors as tests, each seen red** - `f0bb198` (test)

## Deviations from Plan

**1. [Plan expectation not met] The d_Ff1 cells are not red under a last-digit change.** The plan says each such test fails when its value's last digit is changed by one. The copy prints d_Ff1 as a maximum the tool cannot reproduce (Tables 3 and 4 tie it to the mating part), so the tests only use it as a bound: the tabulated pin touches well inside the window, and the construction itself sits above the maximum on two of the three rows. A change of one unit leaves the run green. The red log records that and the red run for a gross change. The exact digits are held by 34-16's check of the real file against these constants, which is what the plan's key link names. Raised for the human: if a last-digit-sensitive check of d_Ff1 is wanted before then, it needs a source for the form diameter that the tool does not have.

**2. [Note] `TABLE_7_THICKNESS` holds nine numbers beyond the cells.** The plan's behaviour asks the three thicknesses to be asserted for each approved designation. For W 120x3x38x8f they are the page's worked example; for the other two they are the approved s1 plus the approved cells, so they disclose nothing the approved set does not already give. They are what makes each Table 7 cell fail a test (without them the cell tests would restate the function they call). The comment in the file says so.

**3. [Rule 3] Module docstring edit.** The sentence saying no other value of the standard is in the repository named only the Part 2 rows; it would have been false after this commit, so it now names the 34-15 anchors as well. The Phase 31 anchors are unchanged. The diff against the plan's reference commit removes one import line (widened to add `GUARD_MARGIN_FACTOR` and `pin_contact_window`) and rewrites that sentence; the rest is additions.

**4. [Tooling] A seen-red driver bug, caught and fixed.** The first driver run mutated a same-size copy within one second, so Python read a stale `.pyc` and reported the previous run's failures. The driver now deletes the `.pyc` and sets `PYTHONDONTWRITEBYTECODE`; the committed log is from the second run. The first run's output was discarded.

**Total deviations:** 1 plan expectation not met (raised), 1 note, 1 docstring edit, 1 tooling fix.

## Issues Encountered

None. `make verify`: 2934 passed in 300.62s (0:05:00), exit 0; the browser test did not flake.

## Known Stubs

None.

## Threat Flags

None. No new surface; the only values added are the three approved designations' cells and what they give.

## Debt and ideas filed

None. F1 is already tracked by `docs/tech_debt/active/2026-10-26-shaft-shift-range-narrower-than-din-5480-exceptions.md`.

## Self-Check: PASSED

- `tests/test_din5480_anchors.py`, `investigation/34-15-sweeps.py`, `34-15-sweeps.log`, `34-15-red-anchors.log` found; `f38d31b` and `f0bb198` are ancestors of HEAD.
- `git ls-files -- private` is empty; no table value appears in a SUMMARY, RESULTS section or log (checked by grep for the approved d_Ff1 and M1 figures in the red log).
