---
phase: 34-fit-tables-and-tolerance-window
plan: 13
subsystem: testing
tags: [din5480, table-7, blind-read, vision-read, private-file]

requires:
  - phase: 34-fit-tables-and-tolerance-window
    provides: the Table 7 models, TABLE_7_PROVENANCE, canonical() and make tables.check (34-02, 34-03)
provides:
  - "read B of Table 7 in the ignored private/reads/table7-b.json: 18 deviation rows, 21 column rows, 8 class rows, 30 tolerance rows, validating through the loader and passing tables.check"
  - "a count-only log of the read and of the worked-example self-check"
  - "one disagreement with the plan's expected count, for the human at 34-14: the page prints 30 tolerance rows, not 24"
affects: [34-14, 34-15, 34-16]

actuals:
  tokens: 3000
  tasks: 2
  commits: 2
plan_head_before: 9f28d7b4e197a5c76f77c2f80be9aa307f529d62
plan_head_after: 9e7054711491bc058eea4a386de1a3929bd159a5

tech-stack:
  added: []
  patterns:
    - "a vision read keeps its aids (row and column numbers drawn on a private copy of the render) and its scripts inside private/"

key-files:
  created:
    - .planning/phases/34-fit-tables-and-tolerance-window/investigation/34-13-table7.log
  modified: []

key-decisions:
  - "Read B records 30 tolerance rows because the page prints 30; nothing was trimmed to the plan's 24 (D-05, D-08)"
  - "The nomogram has one family of 8 class diagonals; the shaft's class 5..12 rows are read on it, the hub's use the same family"

requirements-completed: [REQ-tables-transcribed-twice, REQ-fit-tolerance-window]

coverage:
  - id: D1
    description: "Read B of Table 7 exists in the ignored directory and validates with 18, 21, 8 and 30 rows over nine columns"
    requirement: "REQ-tables-transcribed-twice"
    verification:
      - kind: other
        ref: "make tables.check FILE=private/reads/table7-b.json (ok)"
        status: pass
    human_judgment: true
    rationale: "A vision read is only evidence once it diffs to zero against read A at 34-14; the human settles every disagreement from the page (D-08)"
  - id: D2
    description: "The page's own worked example comes out of read B through the loader's lookup and Table 6"
    requirement: "REQ-fit-tolerance-window"
    verification:
      - kind: other
        ref: "private/reads/table7-b-example.py (yes/no output): fit lookup, T-values and the three thickness limits all match the box"
        status: pass
    human_judgment: false

duration: 25min
completed: 2026-10-30
status: complete
---

# Phase 34 Plan 13: Table 7 read B Summary

**Blind vision read B of DIN 5480-1 Table 7 (page 24) from 600 ppi crops into the loader's schema, checked by the T_G sum, the structural invariants and the page's own W 120x3x38x8f example; the page prints 30 tolerance rows where the plan and the tooling expect 24.**

## Performance

- **Duration:** about 25 min (start time not captured at the top of the run; estimate)
- **Tasks:** 2 of 2
- **Files in the repo changed:** 1 log (plus this SUMMARY)

## Counts (no value of the standard)

| Block | Rows read | Plan expected | Cells per row |
|---|---|---|---|
| Shaft deviations (a..v, h expanded) | 18 | 18 | 9 |
| Column map (3 module groups x 7 d_B ranges) | 21 | 21 | 1 column number |
| Tolerance classes (5..12) | 8 | 8 | 9 tolerance-row numbers |
| Tolerance rows (T_G, T_act, T_eff) | 30 | 24 | 3 |

- **Cells re-read after a first look:** none. Each cell was written once from its 600 ppi crop. The only repeat was cutting the first tolerance crops again because I mis-aimed their windows (layout, no cell changed).
- **`make tables.check FILE=private/reads/table7-b.json`:** last line `ok`.
- **`--complete`, run once for the count:** `tolerance_rows: 30, expected 24` (and the 721 sizes and 16 modules, which are not part of this read).
- **Invariants run as checks, never as targets (34-RESEARCH A2, A3):** classes affine in (class, column): yes; shaft signs by letter: yes; magnitudes not increasing left to right on every row: yes.
- **Worked example reproduced: yes.** `Tables.fit(3.0, 120.0, "8f")` returns a result; the lookup's column for that size is the one the page's arrow marks; its A_s, T_G, T_act and T_eff equal the page's box; `din5480.thickness_limits` at W 120x3x38's s1 gives s_vmax, s_max and s_min each within 0.0005 of the box. No cell was edited toward the example.

## Disagreement with the plan, for the human at 34-14

The page prints **30** tolerance rows (contiguous, T_G = T_act + T_eff on all 30). The plan's objective and verify, the `EXPECTED_COUNTS["tolerance_rows"]` constant in `scripts/din5480_tables_tool.py` and the research's "24 rows" all expect 24. Nothing was trimmed or padded to match.

Structure on the page that supports 30: the 8 classes step 3 rows apiece and a class diagonal steps 1 row per column across 9 columns, so class 12 reaches the 30th row at column 1. A 24-row table would leave classes 11 and 12 pointing at rows that do not exist. The Task 1 verify, run as written, prints `30 False` (its `range(1, 25)` comparison); against `range(1, 31)` it is `True`. The count constant, the plan text and read A's count (if it differs) are for the human to settle at 34-14.

## Task Commits

1. **Task 1: tolerance rows** - `58d719e` (docs)
2. **Task 2: deviations, class diagonals, column map, self-check** - `9e70547` (docs)

Each commit holds only `investigation/34-13-table7.log`.

## Files opened (D-05 blindness evidence)

Under `.planning/`: `phases/34-fit-tables-and-tolerance-window/34-13-PLAN.md`, `34-CONTEXT.md`, `34-RESEARCH.md` (its headings, and the "Table structure" and assumptions part only), `config.json`, and this plan's own `investigation/34-13-table7.log`.

Under `private/`: **opened for reading: nothing of another read's.** I wrote and read only my own files: `reads/table7-b.json`, `reads/table7-b-tol.py`, `reads/table7-b-full.py`, `reads/table7-b-example.py`, and the renders and crops under `renders/34-13/` (the 600 ppi and 100 ppi page, crops, and annotated copies). I ran `ls` on `private/`, `private/reads/` and `private/renders/`, which printed the names of other reads' files and of the 34-12 render directory; I did not open any of them. Outside the repo: `~/Downloads/ISO standards/din-5480-1.pdf` page 24, `src/spur/din5480_tables.py`, `src/spur/din5480.py` (three function signatures), `scripts/din5480_tables_tool.py` (its first 80 lines).

**Read A's output, log, renders, script and summary were never opened**, nor 34-12's log or SUMMARY, nor anything under `docs/tech_debt/`, nor a `git log` beyond the status snapshot.

One exposure, disclosed: the git-status snapshot the harness attached to my context before I started listed recent commit subjects, one of which named a Table 7 tolerance row count that differs between the page and the tooling. I did not open it or act on it; my count of 30 comes from counting the rows on the 600 ppi crops, and the prior I held when I looked (24) was the plan's. The human should weigh read B's count with that in mind.

**Concurrency edge (backstop):** this read wrote only `table7-b.*`, its three scripts and `renders/34-13/`, and opened no other read's output.

## Deviations from Plan

### Recorded disagreement

**1. [Rule 1 - Expectation mismatch, recorded not fixed] Tolerance rows: 30 on the page, 24 expected**
- **Found during:** Task 1
- **Issue:** the plan's and the tooling's expected count differs from what the page shows.
- **Fix:** none by design. Recorded as read, per the orchestrator's instruction and D-05/D-08; reported above and in the log.
- **Files modified:** none (the constant in `scripts/din5480_tables_tool.py` was not touched; it is for the human at 34-14).
- **Commit:** `58d719e`, `9e70547`

**2. [Tracer gate] The Task 1 verify did not print `24 True`**
- It printed `30 False` because of deviation 1; the read itself validated, the T_G sum held on every row and `make tables.check` printed `ok`. I did not halt: halting would have withheld the evidence the human needs, and the orchestrator's instruction for this plan is to record what the page shows and continue.

**Total deviations:** 1 recorded disagreement (plus its effect on the tracer verify). **Impact:** none on this read's integrity; `make tables.check --complete` will not accept a file built from it until the expected count is settled at 34-14.

## Issues Encountered

None beyond the disagreement above.

## Known Stubs

None.

## Threat Flags

None. Renders, crops, scripts and the read stay under the ignored `private/`; `git ls-files private/` and the untracked-in-private check are empty; the log and this SUMMARY hold counts, locations and booleans only.

## Debt and idea items

None filed. The only candidate (the `tolerance_rows` count constant) is a decision for 34-14, and filing needs a row in `docs/tech_debt/INDEX.md`, which the blindness rules forbid me to open.

## Next Phase Readiness

34-14 diffs this read against read A (`make tables.diff`) and shows the human every disagreement, the 30-versus-24 count first.

## Verification run

- `make tables.check FILE=private/reads/table7-b.json`: `ok`.
- Plan verify 2, counts and widths: `18 21 8 30 {9}` (plan expected `18 21 8 24 {9}`; see the disagreement).
- `git ls-files -- private` and untracked-in-private: empty.
- Both commits ran the pre-commit hook `make verify.fast`: Passed. No source code changed, so `make verify` was not run.

## Self-Check: PASSED

- `investigation/34-13-table7.log` exists and holds no value of the standard (read by eye before each commit).
- Commits `58d719e` and `9e70547` are on the branch, each touching only that log.
- `private/reads/table7-b.json` exists, is git-ignored and untracked.
