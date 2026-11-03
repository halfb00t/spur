---
phase: 34-fit-tables-and-tolerance-window
plan: 04
subsystem: shaft
tags: [din5480, tolerance-window, m-re-limits, tiers, warnings, fit-table-7]

requires:
  - phase: 34-fit-tables-and-tolerance-window
    provides: "34-02: din5480_tables.active, Tables.size, Tables.fit, Tables.letters, Tables.tolerance_classes, the synthetic fixture and the with_tables fixture"
provides:
  - "din5480.thickness_limits(s1, a_s_um, t_g_um, t_eff_um) -> (s_vmax, s_max, s_min), DIN 5480-1:2006 Table 6 over Table 7"
  - "five ShaftDimensions keys after measure_over_pins, and the same five in ShaftParams dims, so the page, the API and the CLI print them"
  - "shaft_calc: limit_measurement, LimitReading, TABULATED_PIN, MEASURE_LIMITS_AT_FIT, NO_TABLE_FILE, SOLID_AT_NOMINAL_THICKNESS, size_not_tabulated_warning, fit_not_in_table_7_warning, the tier logic in derive_shaft"
  - "the fit-pattern debt item resolved by the warning (D-14)"
affects: [34-05, 34-06, 34-07, 34-16]

actuals:
  tokens: 11660   # chars/4 over the diff of src, tests and docs (46,642 chars); the two red logs and this file are excluded
  tasks: 3
  commits: 4

tech-stack:
  added: []
  patterns:
    - "One warning tuple per tier, asserted by equality; each tier's sentence shares one opening that lists the five rows it nulls"
    - "A sentence that names table values (the fit's letters and classes) reads them from the loaded file, never a constant"
    - "Each M_Re limit is guarded by the pin-contact window on its own"

key-files:
  created:
    - .planning/phases/34-fit-tables-and-tolerance-window/investigation/34-04-red-window.log
    - .planning/phases/34-fit-tables-and-tolerance-window/investigation/34-04-red-tiers.log
  modified:
    - src/spur/din5480.py
    - src/spur/shaft_calc.py
    - src/spur/shaft_params.py
    - tests/test_shaft_calc.py
    - tests/test_shaft_parity.py
    - tests/test_shaft_interfaces.py
    - docs/architecture/http-api.md
    - docs/tech_debt/INDEX.md
    - docs/tech_debt/resolved/2026-10-26-fit-pattern-accepts-fits-outside-the-standards-set.md

key-decisions:
  - "No sixth row for the thickness the solid carries: max_effective_thickness is that row (printed means the solid carries it, null means nominal and SOLID_AT_NOMINAL_THICKNESS says so). This is the plan's D-13 reading, restated for the human below."
  - "Tier 3 (size listed, fit not in Table 7) still prints the tabulated pin and the nominal M_Re for it (D-09 reads 'for a size in the tables', independent of the fit)."
  - "A limit whose pin does not touch the flanks at all (no root) says so in its own sentence instead of staying silent; only the odd-count gate is silent, because the nominal reading already states it."

requirements-completed: [REQ-fit-tolerance-window, REQ-mre-limits, REQ-off-table-builds, REQ-tables-private-file]

coverage:
  - id: D1
    description: "With the tables loaded, the default shaft prints s_vmax 2.592, s_max [retired fixture value], s_min [retired fixture value], M_Re 28.05 and its limits [retired fixture value] and [retired fixture value] at the tabulated pin 2.75; each limit agrees with the independent oracle within 1e-9 before rounding"
    requirement: REQ-mre-limits
    verification:
      - kind: unit
        ref: "tests/test_shaft_calc.py#test_with_the_tables_the_default_shaft_prints_its_window_and_m_re_limits, #test_each_m_re_limit_agrees_with_the_oracle_at_the_thickness_written_as_the_shift"
        status: pass
    human_judgment: false
  - id: D2
    description: "The window and the limits are computed from the synthetic Table 6/7 values: the numbers prove the arithmetic and the plumbing, not the standard's own values"
    requirement: REQ-fit-tolerance-window
    verification:
      - kind: unit
        ref: "tests/test_shaft_calc.py#test_the_thickness_limits_are_table_6_over_table_7, #test_each_thickness_row_is_rounded_once_from_the_unrounded_sum"
        status: pass
    human_judgment: true
    rationale: "The fixture's Table 7 is invented. That the printed window equals the standard's for a real size is proved only by 34-16's worked-example anchor and by the human at 34-14/34-15."
  - id: D3
    description: "Off the tables every number is today's and the five rows are null with a sentence: no file, a size the file does not list (three feasible neighbours equal the no-file document field for field), and a fit outside Table 7 (a 200, f8 still a 422)"
    requirement: REQ-off-table-builds
    verification:
      - kind: unit
        ref: "tests/test_shaft_calc.py#test_off_table_neighbours_read_as_off_the_tables_field_for_field, #test_the_warnings_are_one_fixed_tuple_per_tier, #test_a_fit_outside_table_7_names_the_files_letters_and_classes_and_nulls_the_window"
        status: pass
      - kind: integration
        ref: "tests/test_shaft_interfaces.py#test_a_fit_outside_table_7_is_a_warning_and_null_not_a_422, #test_an_iso_style_fit_alias_is_still_refused"
        status: pass
    human_judgment: false
  - id: D4
    description: "No warning of any tier carries the table file's path; the API and the CLI print one document with the tables loaded as without them"
    requirement: REQ-tables-private-file
    verification:
      - kind: unit
        ref: "tests/test_shaft_calc.py#test_no_warning_carries_the_table_files_path"
        status: pass
      - kind: integration
        ref: "tests/test_shaft_parity.py#test_the_api_and_the_cli_print_one_shaft_document_with_the_tables"
        status: pass
    human_judgment: false

duration: 11min
completed: 2026-10-30
status: complete
plan_head_before: 1ab3f7c7b0ef70732eb9679e4901e90915b3a871
plan_head_after: 77dd42f1d2cd8fb4044900a3ea8297541b821509
commits: 4
---

# Phase 34 Plan 04: The tolerance window and the M_Re limits, by tier Summary

**With a table file loaded, a listed size and fit print s_vmax, s_max and s_min (DIN 5480-1 Table 6 over Table 7) and M_Re max and min at the tabulated pin, each agreeing with the independent oracle within 1e-9; with no file, an unlisted size or a fit outside Table 7, today's numbers stand, the five rows are null and one fixed sentence says why.**

## Performance

- **Duration:** about 11 min (20:18 to 20:29 local), of which `make verify` took 3 min 47 s
- **Tasks:** 3 of 3
- **Files:** 2 created (red logs), 9 modified, 1 debt item moved
- **Host load:** 6.6 to 9.7 at the start of `make verify`; no wall-clock figure besides the one above is claimed

## Accomplishments

- **The five keys as shipped**, one block after `measure_over_pins`, all `mm`, in `ShaftDimensions` and in the `dims` list:

  | key | label |
  |---|---|
  | `max_effective_thickness` | Max effective tooth thickness s_vmax |
  | `max_actual_thickness` | Max actual tooth thickness s_max |
  | `min_actual_thickness` | Min actual tooth thickness s_min |
  | `measure_over_pins_max` | Measurement over pins M_Re max |
  | `measure_over_pins_min` | Measurement over pins M_Re min |

  `app.js` is not edited (`git diff ddfb3ea -- src/spur/static/app.js` is empty); the page renders them from the schema.
- **The formula.** `din5480.thickness_limits` takes the deviations in micrometres and returns `(s_vmax, s_max, s_min)` unrounded; `derive_shaft` rounds each row once with `round(…, 3)` from the unrounded `s1`. The default prints 2.592, [retired fixture value], [retired fixture value], pin 2.75, M_Re 28.05, limits [retired fixture value] and [retired fixture value]; W 30x2x14x8f prints 3.009, 2.991, 2.964 and limits 34.093, 34.053 (the planning measurements, typed into the tests).
- **The tier tuples** (asserted by equality in `test_the_warnings_are_one_fixed_tuple_per_tier` and, for no file, in the two Pitfall 11 tests):
  - listed size and fit: `(FORM_DIAMETER_UNPROVEN, TABULATED_PIN, hobbed root, MEASURE_LIMITS_AT_FIT, ROOT_FORM_CONSTRUCTION, SHANK_STEP_NO_RELIEF)`
  - no file: `(FORM_DIAMETER_UNPROVEN, THEORETICAL_PIN, hobbed root, MEASURE_AT_NOMINAL_THICKNESS, NO_TABLE_FILE, SOLID_AT_NOMINAL_THICKNESS, ROOT_FORM_CONSTRUCTION, SHANK_STEP_NO_RELIEF)`
  - size not listed: the same with `size_not_tabulated_warning(p)` in place of `NO_TABLE_FILE`
  - fit outside Table 7: `(FORM_DIAMETER_UNPROVEN, TABULATED_PIN, hobbed root, MEASURE_AT_NOMINAL_THICKNESS, fit_not_in_table_7_warning(...), SOLID_AT_NOMINAL_THICKNESS, ROOT_FORM_CONSTRUCTION, SHANK_STEP_NO_RELIEF)`
  - in `derive_shaft` the slots between the pin reading's own sentences and `SOLID_AT_NOMINAL_THICKNESS` are the tier sentence, then each limit's guard sentence.
- **Honest nulls.** A size is on the tables by an exact float key only (`25` and `25.0` find the default row, `25.000001` does not, no nearest row). Three feasible neighbours (d_B 30.001 on W 30x2x14, module 1.3, 19 teeth at d_B 25) print numbers equal to the no-file document's, field for field. `3z`, `13f` and `8q` are 200s whose warning names the fixture's letters `f, h and k` and classes `7, 8 and 9`, read from the file; `f8` is still a 422 and `FIT_PATTERN` is untouched.
- **No path leaks.** `test_no_warning_carries_the_table_files_path` loads the fixture from `tmp_path` through the variable and checks the four parity shafts, a fit-outside shaft and an unlisted shaft.
- **Debt resolved.** The fit-pattern item moved to `docs/tech_debt/resolved/` with `Resolved in: 51d5e63 docs(shaft): say what the fit tables change; resolve the fit-pattern item (D-14) (gsd/phase-34-fit-tables-and-tolerance-window)`.
- **D-13, restated for the human.** There is no sixth row for "the thickness the solid carries". `max_effective_thickness` is that row: printed means the solid is to carry it (34-07 reads it back); null means the solid carries `nominal_thickness` and `SOLID_AT_NOMINAL_THICKNESS` says so. If you want a separate always-present thickness row, it is one more key in `ShaftDimensions` and `dims` here and one line in 34-07.
- **Gate.** `make verify`: `2897 passed in 226.92s (0:03:46)`, rc 0. Each of the four code and docs commits passed the hook's `make verify.fast`. `make lint-imports` prints `Contracts: 10 kept, 0 broken.`; `make no-fake-done` and `make gear.unchanged` (the gear `/api/schema`, 8723 bytes, byte-equal to v0.6) pass.

## Seen red

| Plan | Test id | Deliberate break | First failure line | Restored |
|---|---|---|---|---|
| 34-04 | `test_with_the_tables_the_default_shaft_prints_its_window_and_m_re_limits`, `test_the_thickness_limits_are_table_6_over_table_7`, `test_each_m_re_limit_agrees_with_the_oracle_at_the_thickness_written_as_the_shift[max/min]`, `test_the_shaft_dimensions_keys_are_fixed`, the four `..._with_the_tables[...]` parity cases and the four no-table parity cases | none: the tests ran against the unchanged code | `AttributeError` for the missing fields and function (13 failed, `investigation/34-04-red-window.log`) | n/a, then implemented |
| 34-04 | `test_the_warnings_are_one_fixed_tuple_per_tier`, `test_a_fit_outside_table_7_names_the_files_letters_and_classes_and_nulls_the_window[3z/13f/8q]`, `test_off_table_neighbours_read_as_off_the_tables_field_for_field`, `test_the_size_sentence_prints_a_nudged_diameter_in_full_and_takes_no_nearest_row`, `test_with_no_file_the_five_rows_are_null_...`, the two updated no-file tuples, `test_an_odd_count_nulls_both_limits_without_a_sentence_of_their_own`, `test_a_fit_outside_table_7_is_a_warning_and_null_not_a_422` | none: the tests ran against Task 1's code | `AttributeError: module 'spur.shaft_calc' has no attribute ...` and the missing sentence (11 failed, `investigation/34-04-red-tiers.log`) | n/a, then implemented |

Not seen red: `test_a_limit_outside_the_contact_window_is_null_with_its_own_sentence_and_the_other_prints`, `test_a_size_is_on_the_tables_only_by_an_exact_key`, `test_an_iso_style_fit_alias_is_still_refused` and `test_no_warning_carries_the_table_files_path` passed on the first run, because the code they pin (`limit_measurement` from Task 1, the exact-key lookup and `FIT_PATTERN` from earlier plans, no path in a warning) already held. The first Task 2 run also hit a collection error (a module-level tuple naming a missing constant) before the tests were rebuilt to fail one by one; the log holds the second run.

## Task Commits

1. **Task 1 (tracer): the tooth-thickness window and M_Re limits from the DIN 5480 tables** - `18bf9a8`
2. **Task 2: null and warn every table number off the tables, by tier** - `900e699`
3. **Task 3: say what the fit tables change; resolve the fit-pattern item (D-14)** - `51d5e63`, then `77dd42f` writing the sha into the item and its INDEX row

**Tracer gate:** the tracer's `<verify>` carries only `<automated>` commands. After its commit they were green (280 tests in the four named files, ruff, mypy, 10 contracts kept, `make no-fake-done`, `make gear.unchanged`, the hook's `make verify.fast`), so the plan expanded without a checkpoint: Tracer verified end-to-end.

## Files Created/Modified

- `src/spur/din5480.py` - `thickness_limits`
- `src/spur/shaft_calc.py` - five fields, `LimitReading`, `limit_measurement`, the four constants, two warning functions, the tier logic
- `src/spur/shaft_params.py` - five `dims` rows, the `fit` description and its comment
- `tests/test_shaft_calc.py`, `tests/test_shaft_parity.py`, `tests/test_shaft_interfaces.py` - 24 new cases, two exact tuples updated
- `docs/architecture/http-api.md` - the shaft info row names the five keys, the tiers and `SPUR_DIN5480_TABLES`
- `docs/tech_debt/INDEX.md` and the resolved item

## Decisions Made

- `LimitReading(measure, warnings)` is a NamedTuple rather than a bare tuple (the file already uses `PinReading` and `ChamferReading`), and `which` is `Literal["max", "min"]` so mypy catches a typo.
- `fit_not_in_table_7_warning` says "the fit is not in DIN 5480-1 Table 7, whose shaft deviations are ... and tolerance classes are ...". It also covers a listed letter and class with no column for the size, which `Tables.fit` also answers with None; the real file selects every size by exactly one column (34-02's invariant), so that case is a bad file's, not a user's.

## Deviations from Plan

**1. [Rule 3 - Blocking] The five keys had to be added to `NULLS` in Task 1, not Task 2**
- **Found during:** Task 1
- **Issue:** adding the fields to `ShaftDimensions` turns the existing no-table parity test red until `NULLS` holds them, and Task 1's verify runs that file.
- **Fix:** `NULLS` gained the five keys (as one `_WINDOW` set) in Task 1; Task 2 had nothing left to add there.
- **Files modified:** tests/test_shaft_parity.py
- **Committed in:** `18bf9a8`

**2. [Rule 2 - Missing critical] A limit with no root says so**
- **Found during:** Task 1
- **Issue:** the plan returns `(None, ())` for a limit whose pin does not touch the flanks at all. A printed nominal M_Re beside two silent nulls would hide the reason (L08).
- **Fix:** `limit_measurement` returns a sentence for that case; only the odd-count gate stays silent.
- **Files modified:** src/spur/shaft_calc.py
- **Committed in:** `18bf9a8`

**3. [Rule 1 - Bug] `TABULATED_PIN` wording tested by the wrong substring**
- **Found during:** Task 2
- **Issue:** my odd-count test counted any warning containing "M_Re max", which `TABULATED_PIN` itself contains.
- **Fix:** the test checks sentences that start with "M_Re max" or "M_Re min".
- **Files modified:** tests/test_shaft_calc.py
- **Committed in:** `900e699`

**Also:** the docstring of `pin_measurement` said its null branches go live "in Phase 34, until then covered by direct calls"; they are live now for a tabulated pin, so the sentence was edited (comment only).

**Total deviations:** 3 auto-fixed (1 blocking, 1 missing critical, 1 test bug). **Impact:** none on scope; the plan's artifacts, keys and tuples are as specified.

## Issues Encountered

- The commit hook stashes unstaged files while it runs; the user's uncommitted `.planning/state.json` change and the untracked `.planning/milestone.lock` and `.planning/ui-reviews/` were restored each time and never staged.
- `tests/test_browser.py` did not flake in `make verify` this time.
- Not reachable on the synthetic fixture: the in-`derive_shaft` path where one limit leaves the contact window while the nominal reading stays inside it (every fixture contact sits inside its window, planning measurement). The guard is tested by direct `limit_measurement` calls and its slot in the warning tuple by the code order only. 34-06 adds the tabulated floor and the real-size cases.

## Authentication Gates

None.

## Known Stubs

None.

## Threat Flags

None beyond the plan's threat model. T-34-14 to T-34-17 are mitigated and tested: no nearest row (exact key, three neighbours equal the no-file document), no path in any warning, a fit outside Table 7 nulls the window on three fits, and the fit sentence's letters and classes come from the loaded file.

## Debt and ideas

Filed none. Resolved one: `docs/tech_debt/resolved/2026-10-26-fit-pattern-accepts-fits-outside-the-standards-set.md` (sha `51d5e63`).

## User Setup Required

None.

## Next Phase Readiness

34-05 can refuse a broken table file at startup (`derive_shaft` still lets `active()`'s TablesError propagate, which is why that plan exists). 34-06 lifts the odd-count gate for a tabulated size and adds the guard's tabulated floor; `limit_measurement` already returns the odd gate as a silent null for it to change. 34-07 reads `max_effective_thickness` back from the solid. The page's `dims` rows are in place for its browser step. No blocker.

## Self-Check: PASSED

- FOUND: `src/spur/din5480.py`, `src/spur/shaft_calc.py`, `src/spur/shaft_params.py`, both red logs, the resolved debt item; the active item is gone
- FOUND: commits `18bf9a8`, `900e699`, `51d5e63`, `77dd42f` (`git merge-base --is-ancestor` exit 0); `git rev-list --count 1ab3f7c..HEAD` prints 4
- `grep -c 'def thickness_limits' src/spur/din5480.py` prints 1; the key-order one-liner prints the five keys; `git diff ddfb3ea -- src/spur/static/app.js` is empty; `grep -c 'Phase 34 removes it' src/spur/shaft_calc.py` prints 0
- `make verify`: 2897 passed

---
*Phase: 34-fit-tables-and-tolerance-window*
*Completed: 2026-10-30*
