---
phase: 34-fit-tables-and-tolerance-window
plan: 06
subsystem: shaft
tags: [din5480, pin-contact-guard, form-diameter, m-re-limits, odd-tooth-count, tabulated-floor]

requires:
  - phase: 34-fit-tables-and-tolerance-window
    provides: "34-04: limit_measurement, LimitReading, TABULATED_PIN, MEASURE_LIMITS_AT_FIT, the tier logic in derive_shaft; 34-02: SizeRow.form_d_max_mm, the synthetic fixture and the with_tables fixture"
provides:
  - "pin_contact_window(p, form_d_max=None): for a listed size the floor is the copy's d_Ff1 maximum plus GUARD_MARGIN_FACTOR*m; off the tables the internal construction plus the margin, as before"
  - "pin_measurement(p, pin_d, *, form_d_max=None, odd_confirmed=False) and limit_measurement(p, pin_d, s, which, *, form_d_max=None, odd_confirmed=False)"
  - "derive_shaft passes row.form_d_max_mm to the nominal reading and to each limit for a listed size, and lifts the odd-count gate exactly there"
  - "the form-diameter construction debt item resolved; the odd-count idea retired"
affects: [34-07, 34-15, 34-16]

actuals:
  tokens: 8643    # chars/4 over the diff of src, tests and docs (34,571 chars); the two red logs and this file are excluded
  tasks: 2
  commits: 3      # measured: git rev-list --count 5c506d9..8208de3 (the SUMMARY commit follows)

tech-stack:
  added: []
  patterns:
    - "A floor taken from the copy's own limit, not from our construction, for a listed size; the construction stays only where no table row exists"
    - "Each M_Re reading (nominal and both limits) is guarded on its own at that floor"
    - "A gate lifted by 'the row exists' (odd_confirmed=row is not None), so off-table and no-file builds read as before"

key-files:
  created:
    - .planning/phases/34-fit-tables-and-tolerance-window/investigation/34-06-red-guard.log
    - .planning/phases/34-fit-tables-and-tolerance-window/investigation/34-06-red-odd.log
  modified:
    - src/spur/shaft_calc.py
    - src/spur/din5480.py
    - tests/test_shaft_calc.py
    - tests/test_shaft_parity.py
    - tests/shaft_parity.py
    - tests/test_din5480_anchors.py
    - docs/tech_debt/INDEX.md
    - docs/tech_debt/resolved/2026-10-26-form-diameter-construction-exceeds-din5480-2-maximum.md
    - docs/ideas/INDEX.md
    - docs/ideas/retired/2026-10-26-print-odd-tooth-count-measure-over-pins.md

key-decisions:
  - "The odd-count gate and the form-diameter floor both key on the table row: row is None keeps today's behaviour byte for byte (no file, an unlisted size), row present uses the copy's d_Ff1 maximum and prints the odd count's M_Re and limits"
  - "limit_measurement takes odd_confirmed as pin_measurement does (the plan's Task 2 says 'the same way'); derive_shaft passes True there because the limits are only computed for a listed size"
  - "GUARD_MARGIN_FACTOR stays 0.1: a contact outside the tabulated window is a finding to surface, not a margin to widen (D-12; 34-15 sweeps the real file)"

requirements-completed: [REQ-mre-limits, REQ-off-table-builds]

coverage:
  - id: D1
    description: "For a listed size the guard's lower bound is the tabulated d_Ff1 maximum plus 0.1*m; for the approved W 120x3x38 row (113.91) the floor minus the margin equals that maximum; off the tables the internal floor is unchanged"
    requirement: REQ-mre-limits
    verification:
      - kind: unit
        ref: "tests/test_shaft_calc.py#test_for_a_listed_size_the_guard_starts_at_the_tabulated_form_diameter_maximum, #test_the_pin_contact_window_is_closed"
        status: pass
    human_judgment: false
  - id: D2
    description: "The window is closed at the tabulated floor (bisection, 1e-6 mm either side), and each M_Re reading is guarded on its own: with a d_Ff1 maximum of 23.46 M_Re 28.05 and M_Re max [retired fixture value] print and M_Re min is null with its own sentence; two higher floors null both limits, then the pin"
    requirement: REQ-mre-limits
    verification:
      - kind: unit
        ref: "tests/test_shaft_calc.py#test_the_tabulated_floor_is_closed, #test_a_limit_thickness_below_the_floor_nulls_that_limit_only, #test_each_branch_of_the_floor_is_reached_by_its_own_thickness"
        status: pass
    human_judgment: false
  - id: D3
    description: "A listed odd tooth count prints M_Re and both limits at the tabulated pin (W 26x1.25x19x8f: pin 2.75, 29.026, 28.978, 28.94); an unlisted odd size and no file stay null with ODD_Z_UNCONFIRMED"
    requirement: REQ-off-table-builds
    verification:
      - kind: unit
        ref: "tests/test_shaft_calc.py#test_a_listed_odd_tooth_count_prints_m_re_at_the_tabulated_pin, #test_an_odd_tooth_count_the_tables_do_not_list_stays_null_with_its_sentence, #test_an_odd_tooth_count_off_the_tables_prints_the_pin_and_no_measure_over_pins"
        status: pass
      - kind: integration
        ref: "tests/test_shaft_parity.py#test_the_api_and_the_cli_print_one_shaft_document_with_the_tables[odd-z]"
        status: pass
    human_judgment: false
  - id: D4
    description: "That the tabulated floor never refuses a row the real DIN 5480-2 file lists is not proved here: the fixture's d_Ff1 maxima (apart from W 120x3x38's) are invented, so the real-file sweep is 34-15's"
    requirement: REQ-mre-limits
    verification: []
    human_judgment: true
    rationale: "Only the private table file holds the standard's d_Ff1 maxima and pins; 34-15 sweeps it and surfaces any row where a limit still leaves the window."

duration: 10min
completed: 2026-10-30
status: complete
plan_head_before: 5c506d964d2d248e42274475ad5856843cd04db0
plan_head_after: 8208de304c33eefe5ddf4ec0b005790910f1cb97
commits: 3
---

# Phase 34 Plan 06: The tabulated guard floor and the odd tooth count Summary

**For a size the tables list, the pin-contact guard now starts at DIN 5480-2's own d_Ff1 maximum plus 0.1*m for M_Re and for each limit on its own, and an odd tooth count prints M_Re and both limits at the tabulated pin; off the tables and with no file the internal floor and the odd-count gate stand as before.**

## Performance

- **Duration:** about 10 min (14:48 to 14:57 UTC), of which `make verify` took 5 min 18 s
- **Tasks:** 2 of 2
- **Files:** 2 red logs created, 10 modified (one debt item and one idea moved)
- **Host load:** 11.03 at the start of `make verify`, 6.88 at its end (shared machine); `make verify.fast` 14.31 s at 6.2 to 8.2

## Accomplishments

- **The signatures as shipped** (`src/spur/shaft_calc.py`):
  - `pin_contact_window(p, form_d_max: float | None = None) -> tuple[float, float]`
  - `pin_measurement(p, pin_d, *, form_d_max: float | None = None, odd_confirmed: bool = False) -> PinReading`
  - `limit_measurement(p, pin_d, s, which, *, form_d_max: float | None = None, odd_confirmed: bool = False) -> LimitReading`
  - `derive_shaft` calls the nominal reading with `form_d_max=None if row is None else row.form_d_max_mm, odd_confirmed=row is not None`, and each limit with `form_d_max=row.form_d_max_mm, odd_confirmed=True` inside the `row is not None and tolerance is not None` block.
- **The floor.** For a listed size the lower bound is `form_d_max + GUARD_MARGIN_FACTOR * m`. For W 120x3x38 that is 114.21 (113.91 + 0.3), against the internal 114.1802; the floor minus the margin equals the approved maximum. `GUARD_MARGIN_FACTOR` is still `0.1`.
- **Each reading alone.** On the default row with its d_Ff1 maximum set to 23.46 (floor 23.585), the contacts at pin 2.75 are 23.6411, 23.5989 and 23.5736 mm (planning measurement): M_Re 28.05 and M_Re max [retired fixture value] print, M_Re min is null with one sentence starting `M_Re min is not given: a pin of 2.75 mm at the tooth thickness s_min` and naming the contact 23.574 and the window. At 23.50 (floor 23.625) both limits are null with a sentence each and M_Re prints; at 23.53 (floor 23.655) the pin is null with its own sentence and no limit is tried.
- **Closed at the floor.** The pin touching exactly at 23.585 is found by bisection; the contact of that pin plus 1e-6 mm sits within 1e-5 mm above the floor and prints, the pin minus 1e-6 mm sits within 1e-5 mm below it and is null with "M_Re and D_Re not given". The same pin prints with no maximum (the internal window sits lower for that row).
- **The odd count.** With the fixture, W 26x1.25x19x8f prints pin 2.75, M_Re 29.026 (the approved M1 of Tables 12 and 13, within 0.0005), M_Re max 28.978, M_Re min 28.94, with `TABULATED_PIN` and `MEASURE_LIMITS_AT_FIT` and no `ODD_Z_UNCONFIRMED`. W 25x1.25x19 (feasible, not in the fixture) and the no-file build stay null with `ODD_Z_UNCONFIRMED`. `NULLS_WITH_TABLES["odd-z"]` is `{"form_d"}` and the API = CLI parity holds.
- **Debt resolved, idea retired.** The form-diameter item moved to `docs/tech_debt/resolved/` with `Resolved in: 1fa8deb feat(shaft): the pin-contact guard starts at DIN 5480-2's d_Ff1 maximum (D-12) (gsd/phase-34-fit-tables-and-tolerance-window)`. The odd-count idea moved to `docs/ideas/retired/` with `Retired in: feat(shaft): print an odd tooth count's M_Re at DIN 5480-2's pin (D-11)` (`8208de3`).
- **Gate.** `make verify`: `2917 passed in 317.83s (0:05:17)`, rc 0. Each code commit passed the hook's `make verify.fast`. The browser test did not flake.

## Seen red

| Plan | Test id | Deliberate break | First failure line | Restored |
|---|---|---|---|---|
| 34-06 | `test_for_a_listed_size_the_guard_starts_at_the_tabulated_form_diameter_maximum`, `test_the_tabulated_floor_is_closed`, `test_a_limit_thickness_below_the_floor_nulls_that_limit_only`, `test_each_branch_of_the_floor_is_reached_by_its_own_thickness` | none: the tests ran against 34-04's code | `TypeError` for the missing `form_d_max` argument; the variant tests `assert [retired fixture value] is None` and `assert ([retired fixture value], [retired fixture value]) == (None, None)` (4 failed, `investigation/34-06-red-guard.log`) | n/a, then implemented |
| 34-06 | `test_a_listed_odd_tooth_count_prints_m_re_at_the_tabulated_pin`, `test_the_api_and_the_cli_print_one_shaft_document_with_the_tables[odd-z]` | none: the tests ran against Task 1's code | the listed odd count printed no M_Re (`measure_over_pins`, `_max` and `_min` null where the parity set now expects them; 2 failed, `investigation/34-06-red-odd.log`) | n/a, then implemented |

Not seen red: `test_an_odd_tooth_count_the_tables_do_not_list_stays_null_with_its_sentence` and the renamed `test_an_odd_tooth_count_off_the_tables_prints_the_pin_and_no_measure_over_pins` passed on the first run, because the gate they pin already held off the tables (T-34-23 is held by them, not proved by a red). The first draft of `test_each_branch_of_the_floor_is_reached_by_its_own_thickness` had a slice off by two characters in its own assertion; it was fixed in the test before the implementation run, not in the code.

## Task Commits

1. **Task 1 (tracer): the pin-contact guard starts at DIN 5480-2's d_Ff1 maximum (D-12)** - `1fa8deb`, then `edc0307` writing the sha into the debt item and its INDEX row
2. **Task 2: print an odd tooth count's M_Re at DIN 5480-2's pin (D-11)** - `8208de3`

**Tracer gate:** the tracer's `<verify>` carries only `<automated>` commands. After its commit they were green (225 passed in the three named files, the red log's count 9, the item moved, the margin line unchanged, the hook's `make verify.fast`), so the plan expanded without a checkpoint: Tracer verified end-to-end.

## Files Created/Modified

- `src/spur/shaft_calc.py` - the three signatures, the margin comment (the debt pointer now says resolved), the `ODD_Z_UNCONFIRMED` comment (where it still applies and why a listed size prints), the two field descriptions
- `tests/test_shaft_calc.py` - 6 new cases, the odd test renamed, one stale odd-with-tables case replaced, one lambda given `**_kw`
- `tests/test_shaft_parity.py` - `NULLS_WITH_TABLES["odd-z"]`
- `docs/tech_debt/INDEX.md`, the resolved item; `docs/ideas/INDEX.md`, the retired idea
- comment-only: `src/spur/din5480.py`, `tests/shaft_parity.py`, `tests/test_din5480_anchors.py` (each said the shaft still prints no odd-count M_Re)

## Decisions Made

See `key-decisions` above. The floor is the copy's maximum plus the unchanged margin; widening the margin or skipping the guard to make a tabulated row print is excluded (D-12), so 34-15 will read any real-file row that falls outside as a finding.

## Deviations from Plan

**1. [Rule 3 - Blocking] A monkeypatched `pin_measurement` lambda had to accept keywords**
- **Found during:** Task 1
- **Issue:** `test_no_pin_sentence_is_printed_when_no_pin_is_given` replaces `pin_measurement` with `lambda _p, _pin_d: ...`; `derive_shaft` now calls it with `form_d_max=` and `odd_confirmed=`.
- **Fix:** the lambda takes `**_kw`; its assertions are unchanged.
- **Files modified:** tests/test_shaft_calc.py
- **Committed in:** `1fa8deb`

**2. [Rule 1 - Bug] Three comments said the shaft still prints no odd-count M_Re**
- **Found during:** Task 2
- **Issue:** the `measure_over_pins` docstring in `din5480.py`, the anchors test's docstring and `tests/shaft_parity.py`'s docstring became false once a listed odd count prints.
- **Fix:** each now says it prints for a listed size and stays null otherwise (D-11). None of the three is in the plan's `files_modified`.
- **Files modified:** src/spur/din5480.py, tests/test_din5480_anchors.py, tests/shaft_parity.py
- **Committed in:** `8208de3`

**Also:** `limit_measurement` gained `odd_confirmed` (Task 2's action asks for it "the same way"; the Artifacts line lists only `form_d_max`), and `derive_shaft`'s limit block tests `row is not None and tolerance is not None` so `row.form_d_max_mm` narrows for mypy (the two are equivalent: `tolerance` is None whenever `row` is).

**Total deviations:** 2 auto-fixed (1 blocking, 1 stale comment). **Impact:** none on scope; the signatures, tests and moved files are as specified.

## Issues Encountered

- The commit hook stashes unstaged files while it runs; the user's uncommitted `.planning/state.json` change and the untracked `.planning/milestone.lock` and `.planning/ui-reviews/` came back each time and were never staged.
- `git mv` had already staged the debt item's rename, so naming the old path in `git add` failed once; the commit was made without it.

## Authentication Gates

None.

## Known Stubs

None.

## Threat Flags

None beyond the plan's threat model. T-34-22 is mitigated: each thickness is guarded alone at the tabulated floor (three floors, three branches, each red once), the margin is unchanged, and 34-15 sweeps the real file. T-34-23 is mitigated by `odd_confirmed=row is not None`, with the unlisted-odd and no-file cases tested null.

## Debt and ideas

Filed none. Resolved one: `docs/tech_debt/resolved/2026-10-26-form-diameter-construction-exceeds-din5480-2-maximum.md` (sha `1fa8deb`). Retired one: `docs/ideas/retired/2026-10-26-print-odd-tooth-count-measure-over-pins.md`.

## User Setup Required

None.

## Next Phase Readiness

34-07 reads `max_effective_thickness` back from the solid (unchanged by this plan). 34-15 sweeps the real file: the fixture's d_Ff1 maxima, apart from W 120x3x38's approved 113.91, are invented at 0.05*m below the internal construction, so on the fixture the tabulated floor is more permissive than the internal one for most rows. A real row whose tabulated pin touches below its own floor, or whose s_min contact does, will print null with a sentence; that is the finding to surface, not to widen. No blocker.

## Self-Check: PASSED

- FOUND: `src/spur/shaft_calc.py`, both red logs, the resolved debt item and the retired idea; the active item and the open idea are gone
- FOUND: commits `1fa8deb`, `edc0307`, `8208de3` (`git merge-base --is-ancestor` exit 0); `git rev-list --count 5c506d9..HEAD` prints 3 before this file's commit
- `grep -c '^GUARD_MARGIN_FACTOR = 0.1$'` prints 1; `grep -c 'form_d_max=row.form_d_max_mm'` prints 2; `grep -c 'odd_confirmed=row is not None'` prints 1; `grep -c '^Status: retired$'` on the idea prints 1; both INDEX rows sit below their `## Resolved` and `## Retired` headings
- `make verify`: 2917 passed; `.venv/bin/python -m ruff check src/spur tests` and `mypy src/spur tests/test_shaft_calc.py tests/test_shaft_parity.py` pass

---
*Phase: 34-fit-tables-and-tolerance-window*
*Completed: 2026-10-30*
