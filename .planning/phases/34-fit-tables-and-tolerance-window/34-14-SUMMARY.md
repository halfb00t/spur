---
phase: 34-fit-tables-and-tolerance-window
plan: 14
subsystem: testing
tags: [din5480, private-file, assemble, two-reads, l08]

requires:
  - phase: 34-fit-tables-and-tolerance-window
    provides: both reads of Part 2 and of Table 7, make tables.join/diff/assemble/check (34-03, 34-08..34-13)
provides:
  - "the table file private/din5480-tables.json, assembled only from two pairs of reads that diff to 0 differences, loading with 720 size rows over 16 modules, 18 deviation rows, 8 class rows, 30 tolerance rows and 21 column rows"
  - "count-only logs of the disagreements (by location) and of the assembly"
  - "EXPECTED_COUNTS corrected twice on the human's evidence: tolerance_rows 24 -> 30 and sizes 721 -> 720"
  - "one tech-debt item for the Part 2 row our copy does not print"
affects: [34-15, 34-16]

actuals:
  tokens: 12000
  tasks: 3
  commits: 5
plan_head_before: bb72d8fdd3cfcf8003039b957b02da48d5114714
plan_head_after: 2e83822f54b5c34e70e09df841bf931129e28d4d

tech-stack:
  added: []
  patterns:
    - "a settlement is applied to both reads of a pair by one throwaway script kept under private/, which parses and copies cells and computes none"

key-files:
  created:
    - .planning/phases/34-fit-tables-and-tolerance-window/investigation/34-14-disagreements.log
    - .planning/phases/34-fit-tables-and-tolerance-window/investigation/34-14-assemble.log
    - docs/tech_debt/active/2026-10-31-table-12-m1-25-db19-z14-row-missing-from-our-copy.md
  modified:
    - scripts/din5480_tables_tool.py
    - tests/test_din5480_tables_tool.py
    - docs/tech_debt/INDEX.md

key-decisions:
  - "Table 7's tolerance table has 30 rows; EXPECTED_COUNTS says so (human, 072ddd2)"
  - "Table 12's m=1.25 d_B 19 z 14 nominal row is not printed in our copy and has no other source, so it stays out of the table file; EXPECTED_COUNTS[sizes] is 720 (human, 655a46a)"
  - "Table 12's m=1.25 d_B 20 z 14 takes the single printed row, in both reads alike"

requirements-completed: [REQ-tables-transcribed-twice, REQ-tables-private-file]

coverage:
  - id: D1
    description: "Both pairs of reads diff to 0 differences and the table file is written only after that"
    requirement: "REQ-tables-transcribed-twice"
    verification:
      - kind: other
        ref: "make tables.diff on both pairs: last line 0 differences, exit 0 (investigation/34-14-assemble.log)"
        status: pass
    human_judgment: false
  - id: D2
    description: "The table file loads through SPUR_DIN5480_TABLES and is complete against EXPECTED_COUNTS"
    requirement: "REQ-tables-private-file"
    verification:
      - kind: other
        ref: "make tables.check ARGS=--complete: ok; din5480_tables.active() counts 720 16 18 8 30 21"
        status: pass
      - kind: test
        ref: "tests/test_din5480_tables_tool.py::test_the_expected_counts_are_the_standards_shape"
        status: pass
    human_judgment: false
  - id: D3
    description: "A size the file does not list (W 19x1.25x14) gives the tier-2 refusal of the window, never a tolerance number"
    requirement: "REQ-tables-private-file"
    verification:
      - kind: test
        ref: "tests/test_shaft_calc.py::test_the_warnings_are_one_fixed_tuple_per_tier, ::test_off_table_neighbours_read_as_off_the_tables_field_for_field, ::test_the_size_sentence_prints_a_nudged_diameter_in_full_and_takes_no_nearest_row"
        status: pass
      - kind: other
        ref: "derive_shaft on W 19x1.25x14 with the real file loaded: size lookup none, five window rows null, size-not-tabulated sentence present (investigation/34-14-assemble.log)"
        status: pass
    human_judgment: true
    rationale: "The off-table tier still prints a nominal M_Re at the theoretical pin, with its warnings; whether that is acceptable for this one key is the human's call (see Deviations, item 4)"

duration: about 1 h across two sessions (the first ended at the Task 2 checkpoint)
completed: 2026-10-31
status: complete
---

# Phase 34 Plan 14: The two reads agree; the table file assembled Summary

**The two reads of DIN 5480-2 and the two reads of Table 7 were settled by the human, diffed to 0 differences, and assembled into the ignored `private/din5480-tables.json`, which loads with 720 sizes, 18 letters, 8 classes, 30 tolerance rows and 21 column rows. No table value is in the repository.**

## The table file

- **Path:** `/Users/half/git/halfb00t/spur/private/din5480-tables.json` (git-ignored; `git ls-files -- private` is empty).
- **Size and hash:** 201779 bytes, SHA-256 `ef4ef66bcc2f78e60395981cffbc1c915025f5dee984c3b07aec5a1a8d66b1c9`.
- **To use it:** `export SPUR_DIN5480_TABLES=/Users/half/git/halfb00t/spur/private/din5480-tables.json`
- **Load check, the way every process loads it:** `720 16 18 8 30 21` (sizes, modules, deviations, classes, tolerances, columns).

## Counts

| Step | Result |
|---|---|
| Part 2 read 1 against read 2, before settlement | 0 differences on 719 rows; 2 keys left out by both reads |
| Table 7 read A against read B | 0 differences (18 / 8 / 30 / 21) |
| Settlements applied | 1 row added to both Part 2 reads; 1 key left out of both; 0 for Table 7 |
| Part 2 reads after settlement | 720 rows each; `make tables.diff`: 0 differences, exit 0 |
| Table 7 reads | `make tables.diff`: 0 differences, exit 0 |
| `make tables.assemble` | wrote the file |
| `make tables.check ARGS=--complete` | ok |
| `make verify` | 2924 passed in 354.38s, exit 0 |

## The settlement (Task 2, answered by the human)

Both locations were Part 2, module 1.25, Tables 12 and 13 (pages 18 and 19):

- **d_B 19 z 14:** the nominal row is not printed in the human's copy and there is no other source. It stays out of both reads. A size row needs both pages' columns, so no row was built from page 19 alone and no value was supplied from anywhere. `EXPECTED_COUNTS["sizes"]` is 720 with that reason in the comment beside it.
- **d_B 20 z 14:** the single printed row, applied to both reads by one script (`private/reads/apply_settlements.py`, ignored) that parses the settlements file and copies cells.

## Task Commits

1. **Pre-task authorization, Table 7 tolerance rows 24 -> 30** - `072ddd2` (fix), debt sha `a957897`
2. **Task 1 tracer: the disagreements by location** - `cd1deb4` (docs)
3. **Task 3a: sizes 721 -> 720 and the debt item** - `655a46a` (fix)
4. **Task 3b: the assemble log, counts only** - `2e83822` (docs)

## Deviations from Plan

**1. [Human-authorized] Tolerance rows 30, not 24.** Both Table 7 reads counted 30; the human authorized it before the tracer (`072ddd2`). The plan's `721 16 18 8 24 21` acceptance line is superseded.

**2. [Human-authorized] Sizes 720, not 721.** The plan said that a settlement leaving a read short of `EXPECTED_COUNTS` is the human's call; the human made it. `EXPECTED_COUNTS["sizes"]` and `test_the_expected_counts_are_the_standards_shape` say 720 (`655a46a`), the acceptance load check is `720 16 18 8 30 21`. The tech-debt item `docs/tech_debt/active/2026-10-31-table-12-m1-25-db19-z14-row-missing-from-our-copy.md` (Severity: must; revisit when a second copy or the publisher's corrigendum is available) has its INDEX row in the same commit.

**3. [Plan expectation not met, not a defect] Both Table 7 diffs exited 0 from the start**, where the plan expected exit 1 while the reads differ. The two reads had no disagreement. The same held for Part 2 read 1 against read 2 on the 719 rows both held. The only open points were the two keys both reads had left out.

**4. [For the human, L08] What the tool does for a size the file does not list.** W 19x1.25x14 with the real file loaded: the size lookup returns none, all five tolerance-window rows (max effective thickness, max and min actual thickness, M_Re max and min) are null, and the size-not-tabulated sentence, the theoretical-pin sentence and the nominal-thickness sentence are in the warnings. It never crashes and never prints a tolerance number. It does still print the nominal M_Re at the theoretical pin (the same document the tool prints with no file), because the tooth count is even; for an odd count the existing gate withholds it. That is the existing tier-2 design, so it was not changed. If "never a number" was meant to include the nominal M_Re, that is a change to tier 2, not to this plan.

Tests that prove the tier: `tests/test_shaft_calc.py::test_the_warnings_are_one_fixed_tuple_per_tier`, `::test_off_table_neighbours_read_as_off_the_tables_field_for_field`, `::test_the_size_sentence_prints_a_nudged_diameter_in_full_and_takes_no_nearest_row`, `::test_an_odd_tooth_count_the_tables_do_not_list_stays_null_with_its_sentence`. They use the invented fixture, not this key; the real-file run above is the key-specific evidence.

**5. [Noted, not fixed] Older text still says 721.** `docs/architecture/decision_log.md` (line 3188) and `docs/tech_debt/resolved/2026-10-26-din5480-anchor-rows-beyond-part-1-are-missing.md` record an earlier scratch comparison that met the same Table 12 page (720 nominal rows, 721 inspection rows, one nominal row printed twice). Comments at `src/spur/din5480_tables.py:39` and `:254` say "721 of 721". They are history of a measurement and were left alone.

**Total deviations:** 2 human-authorized count changes, 1 unmet expectation, 1 finding for the human, 1 note.

## Issues Encountered

None. No limit (`MAX_FILE_BYTES`, `UM_LIMIT`) refused the file.

## Known Stubs

None.

## Threat Flags

None. The values (`disagreements.txt`, `settlements.tsv`, both reads, the settlement script, the table file) stay under the ignored `private/`. The logs, the debt item, this SUMMARY and the commit messages carry counts, locations, a byte size and a hash only (read by eye before each commit). T-34-39 is mitigated as planned.

## Debt and idea items

Filed one: `docs/tech_debt/active/2026-10-31-table-12-m1-25-db19-z14-row-missing-from-our-copy.md`.

## Next Phase Readiness

The table file exists. Plans that load it set `SPUR_DIN5480_TABLES` as above. W 19x1.25x14 is the one Part 2 size the file does not list.

## Verification run

- `make verify`: `2924 passed in 354.38s (0:05:54)`, exit 0 (this run included the browser test; it passed, so no rerun was needed).
- Both commits that changed tracked files ran the pre-commit `make verify.fast`: Passed.

## Self-Check: PASSED

- `private/din5480-tables.json` exists, is git-ignored, and `git ls-files -- private` is empty.
- Commits `072ddd2`, `cd1deb4`, `a957897`, `655a46a`, `2e83822` are on the branch.
- `investigation/34-14-disagreements.log`, `investigation/34-14-assemble.log` and the debt file exist.
