---
phase: 34-fit-tables-and-tolerance-window
plan: 17
subsystem: testing
tags: [din5480, gate-cost, decision-log, close-checks, leak-review, seen-red]

requires:
  - phase: 34-fit-tables-and-tolerance-window
    provides: plans 34-01..34-16 (the gate baseline, the loader, the window and limits, the solid, the two reads and the assembled private file, the approved anchors, the real-file check)
provides:
  - "bench/RESULTS.md `### The gate delta (34-17)`: one green make verify on the final tree against the 34-01 baseline and L43's 300 s bar"
  - "docs/architecture/decision_log.md `## L50`: every decision of Phase 34 in one entry, no table value"
  - "bench/RESULTS.md `### Phase close checks (34-17)` and the filled `### Seen red once (Phase 34)` (33 rows)"
  - "docs/tech_debt/active/2026-10-31-din5480-tables-loader-refusals-not-reached-by-a-test.md"
affects: []

actuals:
  tokens: 15800   # chars/4 over the added lines of RESULTS.md, the decision log, the debt item and its INDEX row, and the close-checks log (63100 chars); the 640 KB gate log is excluded
  tasks: 3
  commits: 4   # measured at write time; the docs commit that holds this file follows
plan_head_before: dc31539d4615074ae21243fe5d16df5ac8cb9682
plan_head_after: c5cc325

tech-stack:
  added: []
  patterns:
    - "a leak review that compares every number on an added line with every value of the private file and every value the tool derives from it, then reads the equal ones by eye (pass 1), and looks for two numbers of one record on one line (pass 2)"

key-files:
  created:
    - .planning/phases/34-fit-tables-and-tolerance-window/investigation/34-17-verify.log
    - .planning/phases/34-fit-tables-and-tolerance-window/investigation/34-17-verify-meta.log
    - .planning/phases/34-fit-tables-and-tolerance-window/investigation/34-17-close-checks.log
    - docs/tech_debt/active/2026-10-31-din5480-tables-loader-refusals-not-reached-by-a-test.md
  modified:
    - bench/RESULTS.md
    - docs/architecture/decision_log.md
    - docs/tech_debt/INDEX.md

key-decisions:
  - "L50 is one entry appended after L49 with 0 deleted lines; it logs D-01..D-15, the range edge (A1, edge-upper confirmed against page 24), the refusal of every subcommand on a broken file (A5), the tier-3 pin (A6), the private home (A7) and the human's settlements (30 tolerance rows, 720 sizes, D-13 keep, F1 and F2 accepted, the anchors by name)"
  - "The gate cost is the one quiet-host reading of this plan, 2934 passed in 213.54s and real 214.53, set against the 34-01 baseline (230.90s, 232.23); the difference is inside Phase 25's spread, so no speed claim is made"

requirements-completed: [REQ-gate-cost-recorded, REQ-tables-private-file, REQ-tables-transcribed-twice, REQ-fit-tolerance-window, REQ-mre-limits, REQ-solid-max-material, REQ-off-table-builds]

coverage:
  - id: D1
    description: "The phase's gate cost is one logged green reading, set against the phase's baseline and the 300 s bar"
    requirement: REQ-gate-cost-recorded
    verification:
      - kind: other
        ref: "34-17-verify.log: `2934 passed in 213.54s (0:03:33)`, `real 214.53`, make rc 0; real <= 300.0 by the plan's own check; bench/RESULTS.md `### The gate delta (34-17)`"
        status: pass
    human_judgment: false
  - id: D2
    description: "L50 is the last decision-log entry and no earlier line changed"
    requirement: REQ-tables-transcribed-twice
    verification:
      - kind: other
        ref: "git diff ddfb3ea -- docs/architecture/decision_log.md | grep -c '^-[^-]' prints 0; the last `## L` heading is `## L50`; D-01..D-15, A1, A5, A6 and A7 each appear"
        status: pass
    human_judgment: false
  - id: D3
    description: "The phase's boundaries held, and no value of the standard beyond the approved anchors is in the repository"
    requirement: REQ-tables-private-file
    verification:
      - kind: other
        ref: "investigation/34-17-close-checks.log: 15 PASS, 0 FAIL (private/ untracked, gear and CI byte-equal to v0.6, ten contracts, FIT_PATTERN and the slug unchanged, make tables.test 22 passed, the gate not collecting the real-file module, the leak review)"
        status: pass
    human_judgment: true
    rationale: "Whether a number equal to a private value is an approved anchor, an invented fixture value or a coincidence was read by eye; the log gives the method and its limit"
  - id: D4
    description: "Every seen-red row of the phase is in one table with its log"
    requirement: REQ-off-table-builds
    verification:
      - kind: other
        ref: "awk over bench/RESULTS.md `### Seen red once (Phase 34)` counts 33 rows starting `| 34-`"
        status: pass
    human_judgment: false

duration: about 50 min
completed: 2026-10-31
status: complete
---

# Phase 34 Plan 17: The gate delta, L50, the close checks and the seen-red table Summary

**Phase 34 is closed with evidence: one green `make verify` on the final tree (`2934 passed in 213.54s`, `real 214.53`, 85.47 s under L43's bar by `real`), one decision entry (L50) that holds every decision of the phase and no table value, fifteen close checks that all read PASS, and 33 seen-red rows from the plans' SUMMARYs in one table.**

## The gate reading and its delta

| | Tests | pytest `passed in` | `real` | Load before -> after | Coverage TOTAL | Browser call time |
|---|---|---|---|---|---|---|
| Phase 34 start (34-01), `HEAD 78d167d` | 2783 | 230.90 s | 232.23 s | 5.04 -> 8.15 | 98.48 % | 74.97 s |
| Phase 34 close (this plan), `HEAD dc31539` | 2934 | 213.54 s | 214.53 s | 3.43 -> 11.64 | 97.80 % | 74.16 s |
| difference | +151 | -17.36 s (-7.52 %) | -17.70 s (-7.62 %) | | 1822 -> 2132 statements | -0.81 s |

The bar is inclusive and was read as printed: `real 214.53` is under 300.00 by 85.47 s, `passed in 213.54s` by 86.46 s. The difference from the baseline is inside Phase 25's run-to-run spread (about 8 %, 18.47 s of 230.90 s), so no speed claim is made. The browser test passed in the run; no rerun was needed. The plans' own readings during the phase were not all under the bar (34-03 `381.37 s`, 34-06 `317.83 s`, 34-07 `364.29 s`, 34-14 `354.38 s`, 34-15 `300.62 s`, 34-16 `342.72 s`, on loads their SUMMARYs mostly do not record); `bench/RESULTS.md` lists them as spread only, and the reading of record is the one quiet-host run of this plan.

`src/spur/din5480_tables.py` reads `93.48 %` (13 lines and 8 branch parts missed) and `src/spur/shaft_calc.py` `98.02 %` (2 lines); the three other shaft modules and `pool.py` read 100 %. The total (`97.80 %`) is over the 96.0 % floor, so the gate is green. Filed as debt (below).

## L50

Appended after L49: **The private file**, **Two reads, zero diff**, **The anchors**, **The window and the limits**, **The guard and odd counts**, **The solid**, **Off the tables**, **The range edge**, **A broken file at startup**, then **Reversibility** and **Reason**. 0 lines of the log deleted; `## L50` is the last `## L` heading; D-01..D-15, A1, A5, A6 and A7 each appear. It records the human's settlements by name (30 tolerance rows, 720 sizes, D-13 keep, the range edge confirmed, F1 and F2 accepted, the d_Ff1 bounds and the derived limit thicknesses accepted, the three anchors) and the known behaviour for a size off the table (W 19x1.25x14: window rows null, tier-2 nominal M_Re still printed for an even count). It holds no table value.

## The close checks

15 PASS, 0 FAIL (`investigation/34-17-close-checks.log`): `private/` has no tracked file and is ignored by git and Docker; `tests/regression/` and `ci.yml` are byte-equal to `v0.6`; `requirements.txt`, `params.py` and `calc.py` are unchanged since `ddfb3ea`; `make gear.unchanged` green; `Contracts: 10 kept, 0 broken.`; `FIT_PATTERN` reads `r"^[1-9][0-9]?[a-z]$"`; `ShaftParams().slug()` is `spur_shaft_w25x1.25x18` with and without the variable; `make verify.fast` `real 14.75`; `make no-fake-done` green; the two debt items and the idea are moved with shas that exist; `make tables.test` on the real file `22 passed`; `tests/test_din5480_tables.py` `53 passed`; the gate collects nothing from the real-file module; and the leak review.

The leak review (check 15) read 117 files, 34632 added lines and 27539 numbers. Every number that equals a value of the private file, or a value the tool derives from it, is an approved anchor, an invented fixture value or arithmetic on one, a count, a location key, a measurement of this repository's code or a page, table or clause number: 0 outside the six. The synthetic fixture was compared with the real file cell by cell and agrees only on the approved pin and M1 and on the letter h (0 by definition). One coincidence is recorded in the log, and disclosed here: an invented fixture value pair matched a real derived pair. The human ruled `change fixture`; `282f264` moved the fixture, and the old values are retired from the tracked files.

## Seen red

33 rows in `### Seen red once (Phase 34)`, plan order, each with its log (34-02: 14 rows for 4 deliberate breaks; 34-03: 3; 34-04: 2; 34-05: 2; 34-06: 2; 34-07: 3; 34-15: 4; 34-16: 3). Plans 34-01 and 34-08 add no guard; 34-09 to 34-14 have no `## Seen red` section. The 34-07 worker row has no log of its own (the SUMMARY quotes the run), which the table says. The d_Ff1 cells of 34-15 and the edge-by-design row of 34-16 are in the table as not red, with the reason.

## Task Commits

1. **Task 1: the gate delta** - `d73aae7` (docs: RESULTS section, the verify log, the meta log), preceded by `3ae4f38` (docs: the debt item the coverage reading found)
2. **Task 2: L50** - `d7c09b8` (docs)
3. **Task 3: the close checks and the seen-red table** - `c5cc325` (docs)

## Deviations from Plan

**1. [Process] The plan commit ledger was written after the first commit.** `gsd-plan-head-before-34-17` holds `dc31539`, the parent of `3ae4f38`, which was the plan's HEAD at start; I created it from that parent, so the measured `commits:` is right, but the protocol asks for it before the first commit.

**2. [Rule 2] A debt item was filed from the coverage reading** (`3ae4f38`): the gate delta's coverage rows show twelve loader refusal lines and two `LimitReading` returns that no test reaches. It was filed rather than fixed because this plan changes no `src` or `tests` file; Severity `must`.

**3. [Method] The leak review is a comparison, not a hand classification of every number.** The plan reads "classify each number into six classes". 27539 numbers were compared with every value of the standard the tool can produce, and the 527 + 68 lines that matched were read and classified by eye; a number that equals no value of the standard is not a value of the standard, and the log counts those and does not sort them into the five harmless classes one by one. The log states the method and its limit (a small integer equal to an anchor number is counted as the anchor; pass 2 covers records).

**4. [Note] The seen-red table's 34-02 "same" cells were written out** (the checker's break and its failure line) so that each row reads alone.

**Total deviations:** 1 process, 1 rule-2 debt filing, 1 method note, 1 formatting note.

## Issues Encountered

None. The gate was green on the first run (no run was discarded). The pre-commit hook stashes unstaged files while it runs; `.planning/state.json` (the human's uncommitted change) was compared byte for byte with a copy taken at the start after every commit and was identical.

## Known Stubs

None.

## Threat Flags

None. No file this plan adds carries a table value beyond the approved anchors (check 15, T-34-47). The gate cost and the seen-red rows each name a log (T-34-48).

## Debt and idea items

Filed one: `docs/tech_debt/active/2026-10-31-din5480-tables-loader-refusals-not-reached-by-a-test.md` (Severity `must`, with its INDEX row). No idea item.

## Next Phase Readiness

Phase 34 is ready for verification. Open items for the human, all recorded: the loader-refusal debt item; the 11 sizes refused by the shift range (existing debt item); the missing Table 12 row (existing debt item); the browser-test flake (existing debt item); the in-phase gate readings above 300 s (spread only; a later quiet-host reading over the bar would be the human's to judge against L43).

## Self-Check: PASSED

- `bench/RESULTS.md` holds `### The gate delta (34-17)`, `### Phase close checks (34-17)` and 33 rows in `### Seen red once (Phase 34)`; `git diff --numstat ddfb3ea -- bench/RESULTS.md` shows 0 deleted lines.
- `docs/architecture/decision_log.md`: `## L50` is the last `## L` heading, 0 deleted lines against `ddfb3ea`.
- `investigation/34-17-verify.log`, `34-17-verify-meta.log` and `34-17-close-checks.log` exist; the close-checks log holds 15 `PASS` and 0 `FAIL`.
- Commits `3ae4f38`, `d73aae7`, `d7c09b8` and `c5cc325` are on the branch.
