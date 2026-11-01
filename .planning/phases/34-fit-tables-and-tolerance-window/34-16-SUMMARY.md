---
phase: 34-fit-tables-and-tolerance-window
plan: 16
subsystem: testing
tags: [din5480, real-file-check, anchors, range-edge, l08, private-file]

requires:
  - phase: 34-fit-tables-and-tolerance-window
    provides: the approved anchors TABLE_7_ANCHORS, TABLE_7_THICKNESS, PART_2_CONTACT and PART_2_ROWS (34-15); the checkpoint result, edge-upper with F1 and F2 accepted (34-15); the assembled private/din5480-tables.json (34-14)
provides:
  - "tests/din5480_real_tables_check.py: 22 checks of the human's table file, run only by `make tables.test FILE=<table file>`, never collected by the gate"
  - "the range-edge reading x < d_B <= y recorded as confirmed (comments), and pinned on both sides of every printed edge of the real file"
  - "ACCEPTED_REFUSED, ACCEPTED_GUARD, ACCEPTED_TOOTH: the 34-15 sweep findings the human accepted, as keys"
affects: [34-17]

actuals:
  tokens: 5100
  tasks: 2
  commits: 3
plan_head_before: 7d186270a537415d31228db47b35498b6a2b1feb
plan_head_after: a4b22362d21ffb70b3de4b80ab18b1ab404c33c3

tech-stack:
  added: []
  patterns:
    - "a real-file check that pytest does not collect (no `test_` prefix), so the gate neither runs nor skips it; a make target sets the environment variable from FILE and refuses an empty one"
    - "an approved anchor is held to the file with `==` on the constant the anchors file prints, so a change of one in the last digit fails the cell's own test"

key-files:
  created:
    - tests/din5480_real_tables_check.py
    - .planning/phases/34-fit-tables-and-tolerance-window/investigation/34-16-real-file.log
    - .planning/phases/34-fit-tables-and-tolerance-window/investigation/34-16-red-anchors.log
    - .planning/phases/34-fit-tables-and-tolerance-window/investigation/34-16-red-edge.log
  modified:
    - Makefile
    - src/spur/din5480_tables.py
    - tests/test_din5480_tables.py
    - tests/test_din5480_anchors.py

key-decisions:
  - "Option implemented: edge-upper. Tables.column_for and the loader's comparison are unchanged; only their comments changed (assumed -> confirmed by the human against page 24, 34-15 checkpoint, 2026-10-31)"
  - "No sweep response to implement: F1 (11 sizes refused by the shift range) and F2 were accepted as printed; both are pinned as accepted sets, so a twelfth refused size or any null at the guard fails the check"

requirements-completed: [REQ-off-table-builds, REQ-fit-tolerance-window, REQ-tables-private-file, REQ-mre-limits]

coverage:
  - id: D1
    description: "The real file holds every approved anchor exactly, is complete, and agrees with M1 at the tabulated pin for all 720 sizes"
    requirement: "REQ-tables-private-file"
    verification:
      - kind: other
        ref: "make tables.test FILE=<table file>: 22 passed in 5.37 s (investigation/34-16-real-file.log)"
        status: pass
      - kind: other
        ref: "investigation/34-16-red-anchors.log: one cell changed by one unit fails, for A_s, T_eff, T_G and d_Ff1 in the module's own tests; D_M and M1 refuse the file at load"
        status: pass
    human_judgment: false
  - id: D2
    description: "The guard and tip-land sweeps on the real file equal the findings the human accepted at 34-15"
    requirement: "REQ-mre-limits"
    verification:
      - kind: other
        ref: "tests/din5480_real_tables_check.py::test_the_guard_sweep_finds_the_accepted_findings_and_no_other, ::test_the_tip_land_and_overlap_sweep_finds_the_accepted_findings_and_no_other, ::test_the_tabulated_pin_touches_inside_the_window_at_every_thickness"
        status: pass
    human_judgment: false
  - id: D3
    description: "The range-edge reading is pinned on both sides of every printed edge, and a size on an edge is not off-table"
    requirement: "REQ-off-table-builds"
    verification:
      - kind: test
        ref: "tests/din5480_real_tables_check.py::test_every_printed_range_edge_reads_as_the_range_it_closes, ::test_a_tabulated_size_on_an_edge_is_not_off_table_and_one_float_step_off_is; the fixture's tests/test_din5480_tables.py -k edge"
        status: pass
    human_judgment: false
  - id: D4
    description: "The gate does not collect the real-file module; `make tables.test` without FILE fails with a sentence"
    requirement: "REQ-tables-private-file"
    verification:
      - kind: other
        ref: "`pytest --collect-only -q tests | grep -c din5480_real_tables_check` prints 0; `make tables.test` exits 2; the module with the variable unset errors with 'set FILE: make tables.test FILE=<the table file>'"
        status: pass
    human_judgment: false

duration: about 40 min
completed: 2026-10-31
status: complete
---

# Phase 34 Plan 16: The real-file check and the confirmed range edge Summary

**One command, `make tables.test FILE=<table file>`, proves the human's table file holds the approved anchors to the last digit, is complete, agrees with M1 at every tabulated pin, produces exactly the sweep findings accepted at 34-15, and reads every printed range edge as x < d_B <= y; the gate never touches it.**

## What was built

- `tests/din5480_real_tables_check.py` (22 tests), `make tables.test` (in `.PHONY`, with a help line, refusing an empty `FILE` with a sentence naming it).
- The check imports the approved constants from `tests/test_din5480_anchors.py` and holds no other value of the standard. What it holds are keys of accepted findings (module, d_B, z) and placeholder shaft arguments. The anchors file gained one name, `PAGE_EXAMPLE_M1_MIN`, for the digits it already printed twice.
- The real file, 720 16 18 8 30 21 counts, passes in about 5 s, so `make tables.test` is cheap enough to run after any change to the table or the loader.

## Option implemented

`edge-upper`, as the human answered at 34-15. The comparison in `_columns_selecting` (and so `Tables.column_for`) is untouched; the A1 comments now say confirmed against page 24 on 2026-10-31. Nothing else about the edge needed code: no fixture edge moved, no warning added, no http-api.md entry.

## How the exact digits are held

Every comparison to an approved anchor is `==`:

| Constant | Compared as |
|---|---|
| `TABLE_7_ANCHORS` column, A_s, T_G, T_act, T_eff | `column_for(...) == column` and `fit(...) == FitTolerance(...)` (whole micrometres, integers) |
| `TABLE_7_THICKNESS` | the three limits the file's cells give, each rounded to 3 decimals, `==` the printed tuple |
| `PART_2_CONTACT` d_Ff1 maximum, D_M, clause, tables, pages | `row.form_d_max_mm == d_ff1`, `row.pin_d_mm == pin`, provenance tuple `==` |
| `PART_2_ROWS` D_M, M1 | `size.pin_d_mm == pin`, `size.m1_mm == m1` |
| page example thicknesses, `PAGE_EXAMPLE_M1_MIN` | `derive_shaft` prints equal the constants |

The JSON number and the Python literal parse to the same double only if the digits are the same, so a one-digit change fails. Seen red on a copy of the file (investigation/34-16-red-anchors.log): A_s, T_eff, T_G and d_Ff1 (two designations) fail the module's own tests; D_M and M1 cannot reach it because the loader refuses the file first (its M1-at-the-printed-pin invariant), which is red at load for every test (20 errors when the module held 20 tests). This closes 34-15's deviation 1: the d_Ff1 cells, which the anchors file uses only as a bound, are held digit for digit here.

## Seen red

| Test | How | Result |
|---|---|---|
| anchor cells | a copy of the table file with one approved cell changed by one unit (investigation/34-16-red-anchors.log) | A_s, T_eff, T_G: 2 failed (Table 7 cells, limit thicknesses); d_Ff1 of W 120x3x38 and of W 26x1.25x19: 1 failed (form diameter and pin); D_M, M1: load refusal, 20 errors |
| range edge, real file | `Tables.column_for` comparison flipped in place to over <= d_B < upto, restored after (investigation/34-16-red-edge.log) | `test_every_printed_range_edge_reads_as_the_range_it_closes` failed; the same flip fails the fixture's two edge tests |
| `test_a_tabulated_size_on_an_edge_...` | passes under the flip | by design: it pins the exact float key and that every tabulated size has a column, whichever way the edge reads |

## Sweep responses

| Finding | Answer at 34-15 | Here |
|---|---|---|
| F1: 11 sizes refused by the shift range | accepted as printed | `ACCEPTED_REFUSED` holds their 11 keys; the guard sweep fails if the set grows or shrinks |
| F2 | accepted | `ACCEPTED_GUARD` and `ACCEPTED_TOOTH` are empty frozensets; any size with a null M_Re at the guard, or any closed tip land or tooth space, fails |

No sweep response commit exists because none was asked for.

## Task Commits

1. **Task 1 tracer: the real-file checks and `make tables.test`** - `706dd73` (test). Tracer gate: the check re-run green on the real file after the commit (20 passed).
2. **Task 2: the confirmed range-edge reading pinned on the real file** - `8a8258b` (test)
3. **The logs** - `a4b2236` (docs)

Plan docs commit follows this SUMMARY.

## Verification

- `make verify`: `2934 passed in 342.72s (0:05:42)`, exit 0; the browser test did not flake.
- `make tables.test FILE=<table file>`: `22 passed in 5.37s`.
- `make gear.unchanged` exits 0; `git diff ddfb3ea -- src/spur/static/` is empty.
- `grep -c ASSUMED src/spur/din5480_tables.py` prints 0.

## Deviations from Plan

**1. [Note] `spur.model._build_cached` is not cleared.** The plan has the fixture clear it. No test in the module builds a solid (the extreme builds of 34-15 are not restated), so importing `spur.model`, and with it the kernel, would be dead weight. The fixture installs the file and resets the loader after.

**2. [Rule 3] One name added to `tests/test_din5480_anchors.py`.** `PAGE_EXAMPLE_M1_MIN` replaces the two literal copies of the page example's M1 minimum, so the check imports the digits instead of retyping them (the plan forbids a literal of the standard in the check). Same value, two asserts now read the name.

**3. [Note] Two checks restate the plan more weakly than they read.** "The guard's form term equals each row's d_Ff1 maximum" is true by construction of `pin_contact_window`, so it pins the wiring of the argument, not the arithmetic; what binds the file's d_Ff1 to the guard's behaviour is `test_the_tabulated_pin_touches_inside_the_window_at_every_thickness` (all 720 sizes x 144 fits x 3 thicknesses against the window) and the guard sweep, and those are what would go red.

**4. [Note] The null set is any M_Re null, not only "at the guard".** `ACCEPTED_GUARD` is compared with the sizes where nominal, maximum or minimum M_Re is null for any fit the tool builds, whatever the reason. Stricter than the plan, and empty today.

## Issues Encountered

None.

## Known Stubs

None.

## Threat Flags

None. No new surface. T-34-45: the module holds keys and placeholder arguments, checked by grep for decimal literals. T-34-46: edge-upper pinned on both sides of every printed edge.

## Debt and ideas filed

None.

## Self-Check: PASSED

- `tests/din5480_real_tables_check.py`, the three 34-16 logs, `Makefile` target `tables.test` found; `706dd73`, `8a8258b` and `a4b2236` are ancestors of HEAD.
- `git ls-files -- private` is empty; no value of the standard is in the SUMMARY or the logs (node names, counts and times only).
