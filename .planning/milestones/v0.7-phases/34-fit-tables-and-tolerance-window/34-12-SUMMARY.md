---
phase: 34-fit-tables-and-tolerance-window
plan: 12
subsystem: din5480-tables
tags: [din-5480, table-7, blind-read, vision-read, private-data]

requires:
  - phase: 34-fit-tables-and-tolerance-window
    provides: "34-02's Table 7 models and TABLE_7_PROVENANCE; 34-03's `make tables.check`"
provides:
  - "read A of DIN 5480-1:2006 Table 7 in the ignored private/reads/table7-a.json: 18 deviation rows, 21 column rows, 8 class rows, 30 tolerance rows"
  - "the page's worked example reproduced through Tables.fit and thickness_limits"
  - "a count-only log of the read"
affects: [34-13, 34-14, 34-15]

actuals:
  tokens: 1800
  tasks: 2
  commits: 3
plan_head_before: f06596bdaf49b31f5d0b1c483ac1e3a93367110f
plan_head_after: 8d6736b143fb4df2ca0c2942f29de7542d7efba7

tech-stack:
  added: []
  patterns: ["a hand-typed read built by a script under private/ and written through canonical()"]

key-files:
  created:
    - .planning/phases/34-fit-tables-and-tolerance-window/investigation/34-12-table7.log
    - docs/tech_debt/active/2026-10-30-table-7-tolerance-table-has-30-rows-not-24.md
  modified:
    - docs/tech_debt/INDEX.md

key-decisions:
  - "Read A holds the 30 tolerance rows the page prints, not the 24 the plan and 34-RESEARCH expect; filed as must debt, nothing trimmed (L08, D-05)"

requirements-completed: [REQ-tables-transcribed-twice, REQ-fit-tolerance-window]

coverage:
  - id: D1
    description: "Read A of Table 7 exists in the ignored private/ directory, validates through the loader's models and invariants, and left only counts in the repository"
    requirement: REQ-tables-transcribed-twice
    verification:
      - kind: other
        ref: "make tables.check FILE=private/reads/table7-a.json -> ok"
        status: pass
      - kind: other
        ref: "git ls-files private/ and untracked-not-ignored under private/ -> empty"
        status: pass
    human_judgment: true
    rationale: "A vision reading of an image is only proven by the second blind read's zero diff (34-14) and the human's spot check; no test asserts the cells"
  - id: D2
    description: "The page's own worked example comes out of the read through Tables.fit and din5480.thickness_limits"
    requirement: REQ-fit-tolerance-window
    verification:
      - kind: other
        ref: "Tables.fit(3.0, 120.0, '8f') and thickness_limits at s1: A_s, T_G, T_act, T_eff exact; s1, s_vmax, s_max, s_min within 0.0005 of the page's box"
        status: pass
    human_judgment: true
    rationale: "One example checks one column, one letter and one class; the read's other cells rest on the second read"

duration: 7min
completed: 2026-10-30
status: complete
---

# Phase 34 Plan 12: Table 7 read A Summary

**Read A of DIN 5480-1 Table 7 (an image-only page) read from 600 ppi crops into the ignored private/ directory as 18 deviation, 21 column, 8 class and 30 tolerance rows, checked by the loader and by the page's own worked example W 120x3x38x8f; the printed tolerance table has 30 rows, not the 24 the plan expected.**

## Performance

- **Duration:** 7 min
- **Started:** 2026-10-30T15:28:50Z (STATE's last update; the start time was not captured at the very first call)
- **Completed:** 2026-10-30T15:36Z
- **Tasks:** 2
- **Files modified:** 3 tracked (the log, one debt file, its INDEX row); the read and renders are untracked by design

## Accomplishments

- Counts per block: deviations 18 (a to v, nine columns each, the merged h cell expanded to nine entries), columns 21, classes 8 (nine tolerance rows each), tolerances 30.
- `make tables.check` on the read: `ok`. `--complete` refuses only the tolerance row count (30, expected 24) and the absent sizes and modules (Part 2 is another read).
- Worked example reproduced: yes. A_s, T_G, T_act and T_eff are the box's; s1, s_vmax, s_max and s_min are within 0.0005 of the box. No cell was edited to make it so.
- The classes pass the affine check of 34-RESEARCH A2 on all 72 entries; the deviations pass the sign and monotone checks of A3 (both from the read, not used to produce it).
- Cells re-read from a fresh crop: none. Rows the T_G sum refused: none.

## Task Commits

1. **Task 1: tracer, the tolerance rows** - `19de422` (docs, the log alone)
2. **Task 2: deviations, class diagonals, column map, worked example** - `21bd49c` (docs, the log alone)
3. **Debt filed** - `8d6736b` (docs, the 30-vs-24 item and its INDEX row)

**Plan metadata:** the SUMMARY commit that follows this file.

## Files Created/Modified

- `.planning/phases/34-fit-tables-and-tolerance-window/investigation/34-12-table7.log` - counts and locations only
- `docs/tech_debt/active/2026-10-30-table-7-tolerance-table-has-30-rows-not-24.md`, `docs/tech_debt/INDEX.md` - the debt item
- Untracked, ignored: `private/reads/table7-a.json`, `private/reads/t7a_build.py`, `private/reads/t7a_part2.py`, `private/renders/34-12/`

## Decisions Made

- Read A keeps the 30 tolerance rows the page prints. The count was made twice (100 ppi overview, 600 ppi crops ending on the bottom border of row 30), and the 8 classes by 9 columns of diagonals reach exactly rows 1 to 30. Trimming to 24 would have broken the T_G values the diagonals point at (L08).

## Deviations from Plan

### Plan expectations the page contradicts

**1. [Rule 1 - plan assertion wrong] Tolerance table has 30 rows, not 24**
- **Found during:** Task 1 (the 600 ppi crops; the 100 ppi overview shows it too)
- **Issue:** the plan, 34-RESEARCH "Table structure", `EXPECTED_COUNTS` in `scripts/din5480_tables_tool.py` and `tests/test_din5480_tables_tool.py` say 24. Task 1's verify (`24 True`) and Task 2's verify (`18 21 8 24 {9}`) therefore cannot pass as written; the same checks with 30 pass (`30 True` for rows 1 to 30, `18 21 8 30 {9}`). The tracer gate's re-run of `<verify>` fails on the count alone; the document it checks is valid, so expansion went on instead of halting, and this is the reason on record.
- **Fix:** none to the read. The tooling constant is shared with read B and 34-14, outside this plan's `files_modified`, so it was filed: `docs/tech_debt/active/2026-10-30-table-7-tolerance-table-has-30-rows-not-24.md` (severity must, trigger 34-14's assemble).
- **Commit:** 8d6736b

**2. [Structure] One family of 8 diagonals, not separate shaft and hub families**
- **Found during:** Task 2
- **Issue:** the plan says the shaft and the hub have separate diagonals and only the shaft's are read. The page draws one family of 8; the example's two arrows land on it at class 8 and class 9. The 8 ClassRows are that family.
- **Commit:** 21bd49c (log note)

**3. [Label] The example box names the fits the other way round**
- The box captions "shaft" with the N 9H designation and "hub" with the W 8f one; the diagram arrows mark class 8 for the 8f. The read keeps the 8f, as the plan asks. Logged only.

**Total deviations:** 3 recorded (1 count, 1 structure, 1 label), 0 auto-fixes to code. **Impact:** read B and 34-14's counts must expect 30 tolerance rows; if read B reads 24, that is the first disagreement to look at.

## Issues Encountered

None beyond the above. Pre-commit hooks passed on all three commits (`make verify.fast`, no `--no-verify`).

## Files opened (D-05 evidence)

Under `private/`:
- opened: `private/reads/table7-a.json`, `private/reads/t7a_build.py`, `private/reads/t7a_part2.py` (all this plan's own), and every image under `private/renders/34-12/` (this plan's own)
- listed by name only, never opened: the other files under `private/reads/` (Part 2 reads and their scripts) and the directories `private/renders/34-01`, `34-08` to `34-11`
- `private/reads/table7-b.json` and `private/renders/34-13/` did not exist at listing time, and were never opened

Under `.planning/` and elsewhere:
- opened: `34-12-PLAN.md`, `STATE.md` (first 376 lines), `config.json`, `34-RESEARCH.md` (lines 455 to 499, "Table structure" and the assumptions), `investigation/34-12-table7.log` (own), `src/spur/din5480_tables.py`, `src/spur/din5480.py` (`thickness_limits`, `profile_shift`, `tooth_thickness`), `scripts/din5480_tables_tool.py` and `tests/test_din5480_tables_tool.py` (a few lines each, for the count constant), `docs/tech_debt/TEMPLATE.md` and `INDEX.md`
- one grep over `34-13-PLAN.md` and `34-14-PLAN.md` (plan text, to see where the 24 recurs; no read content). Read B's output, its log and its SUMMARY were never opened: read B was never opened.

The edge claim "wrote only `table7-a.*` and `renders/34-12/`" holds: the only other files written are the log, the debt item and its INDEX row, and the scripts beside the read in the ignored `private/reads/`.

## Debt / ideas filed

One debt item: `docs/tech_debt/active/2026-10-30-table-7-tolerance-table-has-30-rows-not-24.md` (must). No idea item.

## Known Stubs

None.

## Threat Flags

None. Nothing under `private/` is tracked or unignored (checked before each commit); the log and this SUMMARY carry counts and locations, no value.

## Next Phase Readiness

Read B (34-13) can run on its own; 34-14 must settle the 30-vs-24 constant before `make tables.assemble`.

## Self-Check: PASSED

- `private/reads/table7-a.json` present, `make tables.check` prints `ok`, 18/21/8/30 rows and nine columns throughout
- commits 19de422, 21bd49c, 8d6736b are ancestors of HEAD
- `git ls-files private/` empty

---
*Phase: 34-fit-tables-and-tolerance-window*
*Completed: 2026-10-30*
