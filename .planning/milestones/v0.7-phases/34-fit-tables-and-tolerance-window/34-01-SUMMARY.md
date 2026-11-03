---
phase: 34-fit-tables-and-tolerance-window
plan: 01
subsystem: testing
tags: [make-verify, gate-baseline, gitignore, dockerignore, poppler, private-table-file]

requires:
  - phase: 33-interfaces-and-parity
    provides: the tree (ddfb3ea) the gate baseline is taken on, and the 33-01 baseline shape in bench/RESULTS.md
provides:
  - "A logged make verify baseline on Phase 33's tree (2783 passed in 230.90s, real 232.23) that 34-17 subtracts from"
  - "/private/ in .gitignore and private in .dockerignore, in a commit of their own before any file exists there"
  - "The reading toolchain on record: poppler 26.10.0, 27 and 40 pages, 19 images on Part 1 p. 24, the Read tool displays 600 ppi crops"
affects: [34-02, 34-03, 34-08, 34-09, 34-10, 34-11, 34-12, 34-13, 34-14, 34-17]

actuals:
  tokens: 307943   # chars/4 over the diff plus the four committed logs (1,223,975 chars of logs + 7,796 of diff); the diff alone is 1,949
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "The private home is the main checkout's private/, named as $MAIN/private/... in every plan"
    - "A gate reading run under another project's load is kept as a contended reading, not deleted and not the baseline"

key-files:
  created:
    - .planning/phases/34-fit-tables-and-tolerance-window/investigation/34-01-verify.log
    - .planning/phases/34-fit-tables-and-tolerance-window/investigation/34-01-verify-meta.log
    - .planning/phases/34-fit-tables-and-tolerance-window/investigation/34-01-verify-contended.log
    - .planning/phases/34-fit-tables-and-tolerance-window/investigation/34-01-verify-contended-meta.log
    - .planning/phases/34-fit-tables-and-tolerance-window/investigation/34-01-toolchain.log
  modified:
    - bench/RESULTS.md
    - .gitignore
    - .dockerignore

key-decisions:
  - "The baseline of record is the second make verify run (230.90s, host quiet); the first, green but taken under a sibling project's load (338.98s), is kept as 34-01-verify-contended.log and disclosed in bench/RESULTS.md"
  - "A second crop of Part 1 p. 24 at y 1000 was added, because the plan's crop at y 0 is the page's blank top margin and proves only that an image displays"

patterns-established:
  - "Poll the host load (and sibling-project processes) before a timed gate run and record both readings"

requirements-completed: [REQ-gate-cost-recorded, REQ-tables-private-file]

coverage:
  - id: D1
    description: "make verify baseline on Phase 33's tree, logged and recorded in bench/RESULTS.md"
    requirement: REQ-gate-cost-recorded
    verification:
      - kind: other
        ref: "grep -E '^=+ [0-9]+ passed' investigation/34-01-verify.log (2783 passed in 230.90s); grep -c 'Required test coverage of 96.0% reached' prints 1"
        status: pass
    human_judgment: false
  - id: D2
    description: "private/ is ignored by git and by the Docker build context, in a commit that adds no file under private/"
    requirement: REQ-tables-private-file
    verification:
      - kind: other
        ref: "git check-ignore -q on private/din5480-tables.json, private/reads/part2-read1.json and private/renders/34-01/p1-24.png (all exit 0); git show --name-only HEAD of 4bc8080 lists .dockerignore and .gitignore only"
        status: pass
    human_judgment: false
  - id: D3
    description: "The reading toolchain is proved on the human's copy with no value of the standard recorded"
    requirement: REQ-tables-private-file
    verification: []
    human_judgment: true
    rationale: "That no digit string or clause text of the standard reached the log, RESULTS or this SUMMARY is a by-eye reading (the plan's own acceptance criterion); a grep cannot judge it"

duration: 22min
completed: 2026-10-30
status: complete
plan_head_before: 78d167dbff5258e1538d1cbef675d925d058bd36
plan_head_after: 48c61bdcaa6062d317a20f7caa2b9744ca352861
commits: 3
---

# Phase 34 Plan 01: The gate baseline, the private directory and the reading toolchain Summary

**A logged `make verify` baseline on Phase 33's tree (2783 passed in 230.90s, real 232.23), `/private/` ignored by git and by the Docker build context before any file exists there, and a poppler reading toolchain proved on the human's copy with no value of the standard recorded.**

## Performance

- **Duration:** 22 min
- **Started:** 2026-10-30T13:07:39Z (first gate run; the plan was read a few minutes earlier)
- **Completed:** 2026-10-30T13:29:00Z
- **Tasks:** 3
- **Files modified:** 3 (plus 5 logs under `investigation/`)

## Accomplishments

- Baseline: `======================= 2783 passed in 230.90s (0:03:50) =======================`, `/usr/bin/time -p` `real 232.23`, `user 784.29`, `sys 762.08`, coverage TOTAL `98.48 %`, 1-minute load `5.04` -> `8.15`, make's exit status 0. The precondition diff against `ddfb3ea` exited 0 before the run. It is 69.10 s (`pytest`) under L43's 300 s bar. Copied from the logs into `bench/RESULTS.md` `### The gate baseline (34-01)`.
- The ignore rules: `/private/` in `.gitignore` and `private` in `.dockerignore`, commit `4bc8080`, which lists those two files and nothing else. `git check-ignore -q` exits 0 on the three paths the plan names; `git ls-files private/` prints nothing. Before the commit `git check-ignore` returned 1 (Pitfall 9).
- Toolchain: `pdftotext`, `pdftoppm`, `pdfimages` and `pdfinfo` all `version 26.10.0`; Part 1 `Pages: 27`, Part 2 `Pages: 40`; Part 1 page 24 holds 19 images; the 600 ppi render (`4959 x 7017`) and two `3689 x 271` crops sit under `/Users/half/git/halfb00t/spur/private/renders/34-01/`; the Read tool displayed both crops (yes); `git status --porcelain` lists nothing under `private/`.
- `bench/RESULTS.md` has `## Fit tables and tolerance window (Phase 34)`, the baseline, the toolchain section and the empty `### Seen red once (Phase 34)` table (62 lines added, 0 deleted: `git diff --numstat 78d167d -- bench/RESULTS.md`).

## Task Commits

1. **Task 1: tracer, the gate baseline** - `309816c` (docs; also holds the four gate logs)
2. **Task 2: the private directory ignored** - `4bc8080` (chore; `.gitignore` and `.dockerignore` only)
3. **Task 3: the reading toolchain** - `48c61bd` (docs; `34-01-toolchain.log` and the RESULTS section)

**Tracer gate:** the tracer's `<verify>` (`grep -E '^=+ [0-9]+ passed'` on the log, and the three heading counts) was re-run after the commit and passed; its `<automated>` carries no human check, so the phase expanded without a checkpoint.

**Plan metadata:** the `docs(34-01)` commit that holds this file.

## Files Created/Modified

- `bench/RESULTS.md` - Phase 34 opener, `### The gate baseline (34-01)`, `### The reading toolchain (34-01)`, the empty seen-red table
- `.gitignore`, `.dockerignore` - the private directory
- `.planning/phases/34-fit-tables-and-tolerance-window/investigation/34-01-verify.log`, `34-01-verify-meta.log` - the baseline of record
- `.../34-01-verify-contended.log`, `34-01-verify-contended-meta.log` - the first, contended, green run
- `.../34-01-toolchain.log` - versions, counts, paths, yes/no

## Decisions Made

- The baseline of record is the second run. The first was green (`2783 passed in 338.98s`, `real 340.22`) but a sibling project's test jobs (the `halfb00t-screw` checkout, nine python processes, several above 150 % CPU each) shared the host: load `3.55` -> `26.16`, against about 7 after the Phase 33 baselines. A baseline taken under that load would make Phase 33's tree look over L43's 300 s bar and would shrink 34-17's delta. Both runs are in `bench/RESULTS.md`, with the cause, and neither is called a distribution.
- The private home stays the main checkout's `private/` (research A7); `MAIN` resolved to `/Users/half/git/halfb00t/spur` because this run is in the main working tree, not a worktree.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] A green gate run taken under another project's load was not a usable baseline**
- **Found during:** Task 1
- **Issue:** The plan discards only a red, hung or killed run, but this run's own reading (`338.98s`, load `26.16`) was dominated by processes outside this repo, which defeats the baseline's purpose (REQ-gate-cost-recorded, T-34-01).
- **Fix:** Renamed the log `34-01-verify-contended.log` with a meta log stating why, polled the host until the 1-minute load read `5.05`, re-ran `make verify`, and recorded both runs. The baseline is not the lower of two runs chosen by size: the cause (sibling jobs, load 26) was measured first.
- **Files modified:** `bench/RESULTS.md`, the two extra logs
- **Verification:** the second run's pytest line, coverage line and meta log match the figures in RESULTS
- **Committed in:** `309816c`

**2. [Rule 1 - Bug] The plan's crop is blank**
- **Found during:** Task 3
- **Issue:** `pdftoppm -x 0 -y 0 -W 3689 -H 271` on Part 1 page 24 is the page's top margin (3660 bytes, no ink; the page render's first non-white row is 304), so it proves only that an image displays, not that a table band can be read.
- **Fix:** Kept it, added a second crop at `-y 1000` that holds printed text, displayed it with the Read tool, and logged yes/no for both. Nothing the crop shows is recorded.
- **Files modified:** `34-01-toolchain.log`, `bench/RESULTS.md`
- **Committed in:** `48c61bd`

---

**Total deviations:** 2 auto-fixed (1 blocking, 1 bug). **Impact on plan:** no scope change; both make the two recorded facts mean what the plan wanted them to mean.

## Issues Encountered

- Host load from a sibling project is real and recurs: 34-17's gate delta should poll the load the same way before its run.
- `tests` count is `2783` here against 33-09's `2778`: the tree is `ddfb3ea`, not `603031a` (the merge `419aaed` changed 12 files, 652 insertions in `src tests bench scripts`).
- The meta log's "other heavy processes at end: 1" is one unidentified process matching `halfb00t-screw`; the log says nothing else is claimed from it.

## Seen red

None. This plan adds no guard test or step.

## User Setup Required

None - no external service configuration required.

## Debt and ideas

None filed.

## Known Stubs

None.

## Next Phase Readiness

34-02 can start (no file under `private/` exists yet; the rules are in). 34-03 and the read plans can write to `$MAIN/private/...`. The vision reads of 34-08..34-13 are possible at the 3689 x 271 strip size. No blocker.

## Self-Check: PASSED

- FOUND: the five logs under `investigation/`, `bench/RESULTS.md` sections (`grep -c` prints 1 for each of the four headings)
- FOUND: commits `309816c`, `4bc8080`, `48c61bd` (`git merge-base --is-ancestor` exit 0)
- `git ls-files private/` prints nothing; `git check-ignore -q` exits 0 on the three paths
- `grep -c 'Required test coverage of 96.0% reached' investigation/34-01-verify.log` prints 1; `git diff --numstat 78d167d -- bench/RESULTS.md` shows 0 deleted lines

---
*Phase: 34-fit-tables-and-tolerance-window*
*Completed: 2026-10-30*
