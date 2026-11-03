---
phase: 34-fit-tables-and-tolerance-window
plan: 03
subsystem: shaft
tags: [din5480, tables, pdftotext, read-1, diff, assemble, developer-tools]

requires:
  - phase: 34-fit-tables-and-tolerance-window
    provides: "34-02: the Tables schema, parse/problems/canonical, part_2_provenance, the synthetic fixture"
provides:
  - "scripts/din5480_read1.py: normalise, parse_pages, ParseResult, ParseError, ensure_ignored, extract_pages, main; read 1 of DIN 5480-2 through pdftotext, holding no value of the standard"
  - "scripts/din5480_tables_tool.py: check, diff, join, assemble and EXPECTED_COUNTS; locations only unless diff --values"
  - "make tables.read1, tables.check, tables.diff, tables.join, tables.assemble"
  - "$MAIN/private/reads/part2-read1.json (ignored, never committed): 719 size rows over 16 modules, every row through the M1 identity"
affects: [34-04, 34-08, 34-09, 34-10, 34-11, 34-12, 34-13, 34-14]

actuals:
  tokens: 12230   # chars/4 over the files this plan changed (48,919 chars: two scripts 22,104, two test files 21,478, two logs 2,529, Makefile diff 2,808)
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - "Developer-time scripts take the licensed PDF as an argument and refuse an output path git does not ignore"
    - "Reads are diffed as parsed models keyed per row kind, so row order cannot matter and a missing row is a line, not silence"
    - "Output carries locations and counts; values appear only under an explicit flag whose output never goes in a committed file"

key-files:
  created:
    - scripts/din5480_read1.py
    - scripts/din5480_tables_tool.py
    - tests/test_din5480_read1.py
    - tests/test_din5480_tables_tool.py
    - .planning/phases/34-fit-tables-and-tolerance-window/investigation/34-03-read1.log
    - .planning/phases/34-fit-tables-and-tolerance-window/investigation/34-03-red-diff.log
  modified:
    - Makefile

key-decisions:
  - "The tool is scripts/din5480_tables_tool.py, not research's scripts/din5480_tables.py, so it cannot be confused with spur.din5480_tables"
  - "Completeness (EXPECTED_COUNTS) is a transcription-time check run by check --complete and by assemble, not a load-time one"
  - "diff reads with the schema only, so a read that fails an invariant can still be compared; assemble then runs the invariants on the union"

requirements-completed: [REQ-tables-transcribed-twice, REQ-tables-private-file]

coverage:
  - id: D1
    description: "Read 1 of DIN 5480-2 is a committed parser holding no value of the standard: comma, en dash, marks a and b, stamp and header lines handled; a key not printed exactly once on both pages is reported, not joined"
    requirement: REQ-tables-transcribed-twice
    verification:
      - kind: unit
        ref: "tests/test_din5480_read1.py (16 tests, invented page text)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Read 1 ran on the human's copy: 32 pages, 721 nominal and 721 inspection rows, 719 joined, the output loads through load_file (719 size rows, 16 modules); two report lines for the Table 12 and 13 pair wait for the human at 34-14"
    requirement: REQ-tables-transcribed-twice
    verification:
      - kind: other
        ref: "investigation/34-03-read1.log; din5480_tables.load_file on private/reads/part2-read1.json prints '719 16'; make tables.check prints ok"
        status: pass
    human_judgment: true
    rationale: "That the parser read the right number from the right column of the licensed page is proved only by the M1 identity per row and by read 2 agreeing at 34-14; the two ambiguous keys need the human's eye on the page"
  - id: D3
    description: "make tables.diff lists one location line per differing field and per one-sided row, prints no value by default, ignores row order, and was seen red with the comparison disabled"
    requirement: REQ-tables-transcribed-twice
    verification:
      - kind: unit
        ref: "tests/test_din5480_tables_tool.py -k diff (12 tests)"
        status: pass
      - kind: other
        ref: "investigation/34-03-red-diff.log: 6 failed with the comparison disabled"
        status: pass
    human_judgment: false
  - id: D4
    description: "assemble writes the table file only when both pairs of reads diff to zero, the union passes the loader and check --complete, and the output path is ignored by git; join refuses a duplicated key"
    requirement: REQ-tables-private-file
    verification:
      - kind: unit
        ref: "tests/test_din5480_tables_tool.py -k 'assemble or join'"
        status: pass
    human_judgment: false

duration: 15min
completed: 2026-10-30
status: complete
plan_head_before: 7c4d03f70715941d652d702b28a8d679f92c2785
plan_head_after: eaebc8480a07d8391f45e3994967f5b163a2377a
commits: 2
---

# Phase 34 Plan 03: Read 1 of DIN 5480-2 and the check, diff, join, assemble tool Summary

**A `pdftotext -layout` parser that read 719 of the 721 DIN 5480-2 size rows from the human's copy into the ignored directory (every row through the M1 identity) and reported the two keys it would not guess, plus a locations-only diff and an assemble step that writes the table file only when both pairs of reads agree.**

## Performance

- **Duration:** about 15 min (2026-10-30T14:01Z to 14:16Z)
- **Tasks:** 2 of 2
- **Files:** 6 created, 1 modified (Makefile)
- **Host load:** 50 to 75 on a shared machine (read 1 ran at load average 74.90, 68.79, 57.54); no wall-clock figure is claimed

## Accomplishments

- **Read 1.** `make tables.read1` read pages 8 to 39: 32 pages, 721 nominal rows, 721 inspection rows, 719 joined, 2 report lines. `load_file` on the output prints 719 size rows over 16 modules, so every joined row passed the M1 identity. `make tables.check` on it prints `ok`.
- **The report lines (locations only).** Module 1.25, tables 12 and 13, pages 18 and 19: d_B 20 z 14 is printed twice on the nominal page and once on the inspection page; d_B 19 z 14 is printed once on the inspection page and not at all on the nominal page. Exactly the Table 12 shape research predicted; the parser did not guess, and the human settles it from the page at 34-14 (D-08).
- **The diff.** Rows are keyed per kind before comparing, so reversing every tuple changes nothing; a row only one read holds is `only in A` or `only in B` with its key; a key printed twice inside one read is a `duplicate key` line. Every cell is a field: tuple cells are located by 1-based column (`a_s_um[2]`), provenance fields are compared too. The default output is `<kind> <key>, <field>: part <p>, table <t>, page(s) <pages>` and `<n> differences`; `--values` appends both values and must stay in the conversation.
- **Join and assemble.** `join` concatenates the parts of one read and refuses a key present twice. `assemble OUT --part2 A B --table7 C D` refuses a Part 2 input that holds anything but sizes, a Table 7 input that holds sizes, either pair differing, a union the loader refuses, and a union short of `EXPECTED_COUNTS`; it writes only to an ignored path and prints the byte size and SHA-256.
- **Command surface.** Five `tables.*` targets, each with a `##` help line and in `.PHONY`.
- **Gate.** `make verify`: `2875 passed in 381.37s (0:06:21)`, rc 0 (load average about 50 to 60, so the time is contended). `make verify.fast`: `2406 passed in 14.77s`. The commit hook ran `make verify.fast` on both commits and passed.

## Seen red

| Plan | Test id | Deliberate break | First failure line | Restored |
|---|---|---|---|---|
| 34-03 | `test_diff_one_changed_cell_gives_one_location_line_and_no_value` | the cell comparison in `diff_lines` replaced by `if False` | `assert 0 == 1` (tests/test_din5480_tables_tool.py:123) | yes |
| 34-03 | `test_diff_prints_values_only_on_request`, `test_diff_compares_provenance_too`, `test_diff_locates_a_tuple_cell_by_its_column` | same | `assert 0 == 1` | yes |
| 34-03 | `test_assemble_refuses_while_the_part_2_reads_differ`, `..._table_7_reads_differ` | same | `assert 0 == 1` (:264, :281) | yes |

With the comparison disabled, 6 of the 12 `-k diff` tests fail; the 6 that pass are the row-presence, order, equality and duplicate-key cases that do not depend on the cell comparison. The log is `investigation/34-03-red-diff.log`.

Read 1's parser tests went green on the first run after the parser was written (the first run failed on two defects in the parser itself, a trailing space in `normalise` and a title regex that did not allow for the comma becoming a point); they were not separately seen red against a disabled parser. The tool's cases other than the diff are not seen red either; the plan named the diff as the one to show.

## Task Commits

1. **Task 1 (tracer): read 1 of DIN 5480-2, a pdftotext parser that guesses nothing** - `5823392`
2. **Task 2: check, diff, join and assemble the two reads of the DIN 5480 tables** - `eaebc84`

**Tracer gate:** the tracer's `<verify>` carries only `<automated>` commands. After its commit they were green (16 parser tests, the real read loads as `719 16`, ruff, mypy, `make no-fake-done`, and the hook's `make verify.fast`), so the plan expanded without a checkpoint: Tracer verified end-to-end.

## Files Created/Modified

- `scripts/din5480_read1.py` - read 1 parser, `ensure_ignored`, `extract_pages`, `main`
- `scripts/din5480_tables_tool.py` - `check`, `diff`, `join`, `assemble`, `EXPECTED_COUNTS`
- `tests/test_din5480_read1.py` - 16 tests on invented text in the copy's layout
- `tests/test_din5480_tables_tool.py` - 23 tests on the synthetic fixture
- `Makefile` - the five `tables.*` targets, `.PHONY`, and the `help` pattern
- `investigation/34-03-read1.log` - counts and the two report lines; `investigation/34-03-red-diff.log` - the red run

## Decisions Made

- The tool file is `din5480_tables_tool.py` (plan choice, kept) so it cannot be confused with `spur.din5480_tables`.
- `ensure_ignored` treats git exit 128 (not inside a repository) as passing, because nothing can be tracked there; this is what lets the tests write into `tmp_path`.
- `assemble` checks the shape of its inputs, then the diffs, then the loader, then completeness, and only then the output path, so a refusal creates no directory.

## Deviations from Plan

**1. [Rule 3 - Blocking] `make help` could not list a target with a digit in its name**
- **Found during:** Task 1
- **Issue:** the help pattern `^[a-z][a-z.-]*:.*##` does not match `tables.read1`, so the plan's `make help | grep -c '^tables\.'` could never reach 5.
- **Fix:** the pattern is now `^[a-z][a-z0-9.-]*:.*##`. No existing target changes; nothing in `tests/` pins the pattern.
- **Files modified:** Makefile
- **Verification:** `make help | grep -c '^tables\.'` prints 5
- **Committed in:** `5823392`

**2. [Rule 1 - Bug] Parser defects found by the first test run**
- **Found during:** Task 1
- **Issue:** `normalise` left a trailing space after a removed mark, and the title regex expected a comma after "dimensions" although `normalise` had already turned it into a point (the table title would never have matched on the real copy).
- **Fix:** `normalise` strips; the title regex accepts `[.,]`.
- **Committed in:** `5823392`

**3. Test shape, not behaviour: the one-cell diff test changes `t_g_um` alone**
- The plan's behaviour line says the one-cell case changes `t_g_um` and `t_act_um` "so both load". `diff` reads with the schema only (so an invariant-failing read stays comparable), so one changed field is the one-cell case and gives exactly one line. Both fields changing would give two lines, contradicting "exactly one".

**Total deviations:** 2 auto-fixed (1 blocking, 1 bug), 1 test-shape note. **Impact:** none on scope.

## Issues Encountered

- The commit hook stashes unstaged files while it runs; the user's uncommitted `.planning/state.json` change and the untracked `.planning/milestone.lock` and `.planning/ui-reviews/` were restored each time and never staged.
- `tests/test_browser.py` did not flake in `make verify` this time.

## Authentication Gates

None.

## Known Stubs

None.

## Threat Flags

None beyond the plan's threat model. T-34-10 to T-34-13 are mitigated and tested: no value in the diff by default or in the read-1 log, the Table 12 pair reported not joined, `ensure_ignored` before every write (refusal tested on `tests/x.json` and `tests/_tool_guard.json`), `assemble` refusing on any difference or shortfall.

## Debt and ideas

None filed.

## User Setup Required

None.

## Next Phase Readiness

34-04 and the read-2 plans (34-08 to 34-13) can write their reads in the schema `tables.diff` compares and `tables.join` concatenates; they must not open `private/reads/part2-read1.json`. At 34-14 the human settles the two Table 12 and 13 keys from page 18 and 19, and `make tables.assemble` writes the table file once both pairs diff to zero and the counts are complete (the Part 2 read must reach 721 size rows). No blocker.

## Self-Check: PASSED

- FOUND: both scripts, both test files, both logs, and `private/reads/part2-read1.json`
- FOUND: commits `5823392`, `eaebc84` (`git merge-base --is-ancestor` exit 0); `git rev-list --count 7c4d03f..HEAD` prints 2
- `git ls-files private` prints nothing; `git check-ignore -q private/reads/part2-read1.json` exits 0
- `make help | grep -c '^tables\.'` prints 5; `grep -cE '^tables\.(check|diff|join|assemble):' Makefile` prints 4; `grep -c EXPECTED_COUNTS scripts/din5480_tables_tool.py` prints 7
- `pytest tests/test_din5480_read1.py tests/test_din5480_tables_tool.py`: 39 passed; `make verify`: 2875 passed

---
*Phase: 34-fit-tables-and-tolerance-window*
*Completed: 2026-10-30*
