---
phase: 34-fit-tables-and-tolerance-window
plan: 08
subsystem: shaft
tags: [din5480, tables, read-2, page-render, private-table-file]

requires:
  - phase: 34-fit-tables-and-tolerance-window
    provides: "34-02 schema and part_2_provenance; 34-03 make tables.check; 34-01 ignored private/ and the poppler toolchain"
provides:
  - "$MAIN/private/reads/part2-read2-a.json (ignored, never committed): 161 size rows over modules 0.5, 0.6, 0.75 and 0.8, read from the rendered pages 8 to 15, every row through make tables.check"
  - "investigation/34-08-read2.log: counts and locations only"
affects: [34-14]

actuals:
  tokens: 2500   # chars/4 over the one tracked file (1,423 chars of log) plus the two private working files (6,659 TSV + 1,915 converter): 9,997 chars. Images read are not counted on this scale
  tasks: 2
  commits: 2

key-files:
  created:
    - .planning/phases/34-fit-tables-and-tolerance-window/investigation/34-08-read2.log
  modified: []

key-decisions:
  - "Read 2 part a is a typed TSV (one N line per nominal row, one I line per inspection row) plus a throwaway converter in private/reads/ that parses it into SizeRow and writes canonical(); the join on (d_B, z) and the exactly-once rule live in the converter, not in my head"

requirements-completed: [REQ-tables-transcribed-twice]

coverage:
  - id: D1
    description: "Read 2, part a, of DIN 5480-2 exists in the ignored directory: modules 0.5 to 0.8, 161 rows, validates as a Tables document and passes make tables.check"
    requirement: REQ-tables-transcribed-twice
    verification:
      - kind: other
        ref: "Tables.model_validate_json on private/reads/part2-read2-a.json prints modules [0.5, 0.6, 0.75, 0.8] and 161; make tables.check prints ok"
        status: pass
    human_judgment: false
  - id: D2
    description: "That each digit typed from a page is the digit the page prints, and that the read was independent of read 1"
    requirement: REQ-tables-transcribed-twice
    verification: []
    human_judgment: true
    rationale: "Only the diff against read 1 at 34-14 (zero differences) and the human's look at any difference prove the transcription; the M1 identity passing on all 161 rows is a partial check on D_M and M1 only, and the independence rests on the list of files opened below, which includes one disclosed departure"

duration: about 30 min (not timed at start)
completed: 2026-10-30
status: complete
plan_head_before: e5e435b06569a82b121eb8a6e73fe8dfd46e7c9a
plan_head_after: 31a2061fe693bc8b5a5de94497b0806e0df43e1c
commits: 2
---

# Phase 34 Plan 08: Read 2 of DIN 5480-2, part a (modules 0.5 to 0.8) Summary

**161 size rows of DIN 5480-2 read by eye from 300 ppi band crops of pages 8 to 15 into the ignored directory, every one through the loader's M1 identity on the first try, with no key left out and no row re-read; only counts reached the repository.**

## Performance

- **Duration:** about 30 min (start time was not recorded; this is an estimate)
- **Tasks:** 2 of 2
- **Files:** 1 tracked file created (the log); 5 private working files (TSV, converter, JSON, renders under `private/renders/34-08/`), all ignored

## Accomplishments

- Task 1 (tracer): module 0.5, pages 8 and 9, 35 nominal and 35 inspection rows, 35 joined, `make tables.check` printed `ok`, the verify printed modules `[0.5]` and 35 rows, and `git ls-files private` plus untracked-ignored listing was empty. Committed `b3ec7ad`. The tracer's `<verify>` is automated only, so the plan expanded without a checkpoint.
- Task 2: modules 0.6 (pages 10 and 11, 39 rows), 0.75 (pages 12 and 13, 42 rows) and 0.8 (pages 14 and 15, 45 rows). The whole part: `Tables.model_validate_json` printed modules `[0.5, 0.6, 0.75, 0.8]` and 161; `make tables.check` printed `ok`. Committed `31a2061`.
- Counts per module and page are in `investigation/34-08-read2.log`: nominal and inspection line counts equal the row count for every module.
- Keys left out: 0. Rows the check refused and that were re-read from a 600 ppi crop: 0 (the 600 ppi path was never needed). Keys for the human at 34-14 from this read: none.
- One shape worth knowing for 34-14: module 0.8 prints d_B 20 on two rows of each page (two different tooth counts); the keys differ in z, so both are rows, and the log says so by location.

## Task Commits

1. **Task 1 (tracer): module 0.5 read from its two rendered pages into a checked partial document** - `b3ec7ad`
2. **Task 2: modules 0.6, 0.75 and 0.8, the same way; the part checked whole** - `31a2061`

Each commit holds `investigation/34-08-read2.log` alone.

## Method (no value)

100 ppi page renders to find the columns, then 300 ppi full-width bands of 11 to 13 rows, each overlapping the previous by one row and the first of each page showing the header labels, read with the Read tool; the nominal column used is the one printed under the "max." label of the root form circle diameter (the 12th), the inspection columns the second D_M and the M1 beside it. Each row was typed as read into the TSV; the converter parses the TSV only and computes nothing. Two first-pass crops cut off the page's first or last row (page 8 rows at the top, page 14's last row); both were re-cropped before any value was typed from them.

## Files opened (independence record)

Under `private/`: only my own files: `reads/part2-read2-a.tsv`, `reads/part2-read2-a.json`, `reads/read2a_convert.py`, and the renders and crops under `renders/34-08/`. `ls` of `private/` and of `private/reads/` showed the name `part2-read1.json`; I did not open, run, read or recall its content. I did not run `scripts/din5480_read1.py` or `make tables.read1`, and did not open `investigation/34-03-read1.log` or any other read-2 part or its SUMMARY. I ran `make tables.check` (which executes `scripts/din5480_tables_tool.py`; I did not read the script).

Under `.planning/`: `phases/34-fit-tables-and-tolerance-window/34-08-PLAN.md`; `34-RESEARCH.md` lines 392 to 410 (Pitfall 10 and the start of Pitfalls 11 and 12) and 461 to 493 (Table structure, State of the art, the first assumption rows); `34-01-SUMMARY.md`; `34-03-SUMMARY.md`; `investigation/34-08-read2.log` (my own); this plan's SUMMARY and the STATE, ROADMAP and REQUIREMENTS files for the close-out. Also `src/spur/din5480_tables.py` (grep of `SizeRow`, `part_2_provenance`, `canonical`) and `Makefile` via `make -n`.

Read 1 was never opened.

## Deviations from Plan

**1. [Process - independence] `34-03-SUMMARY.md` was opened, which the plan forbids**
- **Found during:** start of execution
- **Issue:** the dispatch prompt's required-reading list named `34-03-SUMMARY.md` ("read-1 tooling") while the plan names it among the files read 2 must not open. I followed the dispatch list and read it before the plan's prohibition registered against it.
- **What it held:** counts for read 1 (rows read, rows joined, modules) and two report lines about module 1.25, Tables 12 and 13, pages 18 and 19. No table value and nothing about modules 0.5 to 0.8. Nothing from it was used while reading the pages, and my rows were typed from the band crops before any comparison was possible.
- **Impact:** low, but the plan's own acceptance line ("none of them is read 1 or another read-2 part") is about read 1's output and other read-2 parts; the 34-03 SUMMARY is neither, but it is on the plan's forbidden list, so it is disclosed here for the human at 34-14 to weigh. No fix is possible after the fact; the 34-14 diff is the real check.
- **Files modified:** none

**Total deviations:** 1 (process, disclosed, no code or data effect).

## Auth gates

None.

## Seen red

None. This plan adds no guard test or step.

## Known Stubs

None.

## Threat Flags

None. T-34-27 holds: nothing under `private/` is tracked or unignored (`git ls-files private` prints nothing, the ignored-others listing is empty), and the only committed file is the count-only log. T-34-28: the list above is the evidence, with the one disclosed departure.

## Debt and ideas

None filed.

## User Setup Required

None.

## Next Phase Readiness

`part2-read2-a.json` is ready for 34-14's `make tables.join` with the other read-2 parts and `make tables.diff` against read 1. No key from this part needs the human's eye; the by-eye reading of every digit is what the diff will test. No blocker.

## Self-Check: PASSED

- FOUND: `investigation/34-08-read2.log`; `private/reads/part2-read2-a.json` (validates, 161 rows, modules `[0.5, 0.6, 0.75, 0.8]`)
- FOUND: commits `b3ec7ad`, `31a2061` (`git rev-list --count e5e435b..HEAD` printed 2 before this SUMMARY)
- `git ls-files private` prints nothing; `git check-ignore -q` exits 0 on the TSV and a render; `make tables.check` prints `ok`
- `grep -c 'tables.check\|^ok$\|problem'` on the log printed 2

---
*Phase: 34-fit-tables-and-tolerance-window*
*Completed: 2026-10-30*
