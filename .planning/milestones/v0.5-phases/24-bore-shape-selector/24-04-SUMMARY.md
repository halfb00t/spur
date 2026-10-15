---
phase: 24-bore-shape-selector
plan: 04
subsystem: testing
tags: [bench, playwright, make-verify, gate-cost, readings, seen-red]

requires:
  - phase: 24-bore-shape-selector
    provides: "plans 24-01 to 24-03: the selector (470b78a), tests/test_selector.py (505999e), the golden sweep and recorder (f489d3d), the sixteen-pick matrix and keyed bore (3a8028b), and their kept logs"
  - phase: 23-conditional-form-fields
    provides: "the shape of the priced-step section in bench/RESULTS.md (23-04)"
provides:
  - "bench/RESULTS.md section Bore-shape selector (Phase 24): host state, three browser readings, three commit-slice readings and a thirteen-row Seen red once table, every figure copied from a kept log"
  - "The 31 kept logs and notes of plans 24-01 to 24-04 committed under .planning/phases/24-bore-shape-selector/investigation/"
  - "L42's forward citation of the Phase 24 readings resolved"
affects: [25]

actuals:
  tokens: 3905   # chars/4 over the added lines of bench/RESULTS.md (15,618 chars), the plan's estimate scale; the kept logs are raw output and not counted
  tasks: 2
  commits: 1
plan_head_before: 917e306c2ff5e106ad1f0bda54214b0bbda8ed0e
plan_head_after: c0675b9ad550fdea5a0db028d681b28a48428986

tech-stack:
  added: []
  patterns:
    - "A gate cost is priced by the step's own three foreground readings with host state and load, kept as raw logs and checked cell by cell against the table by script; no bar is set"
    - "A reading that is an outlier is recorded as read and described, not dropped or re-taken"

key-files:
  created:
    - .planning/phases/24-bore-shape-selector/investigation/24-04-reading-1.log
    - .planning/phases/24-bore-shape-selector/investigation/24-04-reading-2.log
    - .planning/phases/24-bore-shape-selector/investigation/24-04-reading-3.log
    - .planning/phases/24-bore-shape-selector/investigation/24-04-slice-1.log
    - .planning/phases/24-bore-shape-selector/investigation/24-04-slice-2.log
    - .planning/phases/24-bore-shape-selector/investigation/24-04-slice-3.log
    - .planning/phases/24-bore-shape-selector/investigation/24-04-verify.log
  modified:
    - bench/RESULTS.md

key-decisions:
  - "No bar is set: the readings are this host's, Phase 25 re-sets the gate bar on its final HEAD and absorbs the bore shape step (D-15)"
  - "The step is priced by its own timing over a full-gate A/B, following 22 D-06 and 23-04"
  - "The run-2 unknown relation op reading (2.11 s against 4.11 and 4.12 s) is recorded as read, with the one difference the logs show (3 server group members at the kill against 4), and its cause is stated as not investigated"
  - "The two working notes in investigation/ (BASE.txt, draft-notes.txt) and the flake log 24-01-red-1.log were committed with the logs, because the plan says to stage every file under that directory"

requirements-completed: [REQ-selector-derives-and-writes-through, REQ-selector-round-trips-per-state]

coverage:
  - id: D1
    description: "Three browser readings on the committed tree, one at a time, with host state, load before and after and UTC start, recorded in bench/RESULTS.md and equal to their kept logs"
    requirement: "REQ-selector-derives-and-writes-through"
    verification:
      - kind: other
        ref: "Task 1 and Task 2 verify scripts: every step figure in the table equals its line in investigation/24-04-reading-N.log (row-exact check also run); bore shape 8.58, 8.55 and 8.53 s, all under 15 s"
        status: pass
    human_judgment: false
  - id: D2
    description: "Three make verify.fast readings with tests/test_selector.py in the slice, each under L36's 30 s kill and recorded beside 24-RESEARCH's 16.16 s as another reading"
    requirement: "REQ-selector-round-trips-per-state"
    verification:
      - kind: other
        ref: "Task 1 verify script and the row-exact check: real 15.66, 15.57 and 15.57 s, each log ending make verify.fast exit 0"
        status: pass
    human_judgment: false
  - id: D3
    description: "Seen red once (Phase 24): thirteen rows, one per first-failure line the three earlier SUMMARYs recorded, each with command, kept log and how it was restored"
    requirement: "REQ-selector-round-trips-per-state"
    verification:
      - kind: other
        ref: "Task 2 verify script: 13 rows matching | 24-0[123] (at least ten required); first-failure lines re-read from the kept logs"
        status: pass
    human_judgment: false
  - id: D4
    description: "make verify passes on the tree this plan commits, and the commit holds bench/RESULTS.md and the kept logs and nothing under src/ or tests/"
    requirement: "REQ-selector-derives-and-writes-through"
    verification:
      - kind: other
        ref: "investigation/24-04-verify.log (1311 passed, make verify exit 0) and the Task 2 commit-content verify script (one commit, 31 kept logs plus bench/RESULTS.md, no src/ or tests/ path, tree clean)"
        status: pass
    human_judgment: false
  - id: D5
    description: "The prose of the Phase 24 section reads fairly: what is priced, why no bar is set, and the account of the 2.11 s outlier"
    verification: []
    human_judgment: true
    rationale: "The scripts check that every figure equals its log; whether the surrounding wording is accurate and fair is a person's call"

duration: 9min
completed: 2026-10-12
status: complete
---

# Phase 24 Plan 04: Gate and commit-slice cost of the bore-shape selector, and the phase's seen-red record Summary

**The `bore shape` step reads 8.55 s on average (8.53 to 8.58 s) and the commit slice 15.60 s real (15.57 to 15.66 s, under L36's 30 s kill), three readings each on HEAD `917e306` with host state and kept logs, recorded in `bench/RESULTS.md` beside a thirteen-row Seen red once table, behind a green `make verify` (1311 passed, coverage 97.99 %).**

## Performance

- **Duration:** 9 min
- **Started:** 2026-10-12T16:14:25Z
- **Completed:** 2026-10-12T16:24:24Z (the last verify; the SUMMARY and state commit follow)
- **Tasks:** 2
- **Files modified:** 1 (`bench/RESULTS.md`), plus 31 kept logs and notes added to the repository

## Accomplishments

- Three foreground readings of `make test PYTEST_ARGS="tests/test_browser.py -n0 --no-cov -q -s"` on the committed tree, each kept as `investigation/24-04-reading-N.log` ending `make test exit 0`, with `bench.machine_facts()`, chip, OS, Python, playwright and pytest versions, the UTC window and the background load recorded in the new section.
- Three readings of `/usr/bin/time -p make verify.fast` with `tests/test_selector.py` in the slice (`912 passed`), each kept as `investigation/24-04-slice-N.log` ending `make verify.fast exit 0`, all under L36's 30 s kill.
- `### Seen red once (Phase 24)`: thirteen rows with command, kept log, first-failure line (re-read from the log, with file and line) and the restore, plus a paragraph on the one non-deliberate red (24-01's resource-tracker flake, its log `24-01-red-1.log`).
- A row-exact script check that every table cell (result line, the four step seconds, `real`) equals its log, run beside the plan's own verify scripts.
- L42's forward citation of `Bore-shape selector (Phase 24)` now resolves: the heading occurs once in `bench/RESULTS.md`.

## Host state

`bench.machine_facts()` reads `12 CPUs, arm64, 32.0 GiB RAM`; Apple M2 Max, macOS 27.0.1, Darwin 27.0.0, Python 3.12.13, playwright 1.63.0, pytest 9.1.1; HEAD `917e306`; `uptime` at the start `22:14` local (16:14Z), load averages 2.76 6.12 7.62. `ps -A -o %cpu=,comm=` top five: `iTerm2` 31.8, `WindowServer` 28.3, `claude` 25.4 (the session driving this plan), `opencode` 3.0, `zsh` 2.8; nothing above 50 %. The 5-minute and 15-minute loads were high from the full test run made before dispatch, not from this plan.

## Readings

Browser file, `make test PYTEST_ARGS="tests/test_browser.py -n0 --no-cov -q -s"` (each log ends `make test exit 0`):

| Run | Result line | bore shape (s) | golden sweep (s) | unknown relation op (s) | first build drawn (s) | 1-min load before -> after | UTC start |
|---|---|---|---|---|---|---|---|
| 1 | `2 passed in 20.47s` | 8.58 | 0.36 | 4.11 | 2.96 | 2.60 -> 3.21 | 16:14:44Z |
| 2 | `2 passed in 18.56s` | 8.55 | 0.42 | 2.11 | 2.99 | 3.21 -> 3.58 | 16:15:09Z |
| 3 | `2 passed in 20.48s` | 8.53 | 0.38 | 4.12 | 2.99 | 3.37 -> 3.22 | 16:15:32Z |

Commit slice, `/usr/bin/time -p make verify.fast` (each log ends `make verify.fast exit 0`):

| Run | Result line | real (s) | 1-min load before -> after | UTC start |
|---|---|---|---|---|
| 1 | `912 passed in 15.02s` | 15.66 | 3.04 -> 3.88 | 16:15:56Z |
| 2 | `912 passed in 14.98s` | 15.57 | 3.81 -> 5.23 | 16:16:15Z |
| 3 | `912 passed in 14.99s` | 15.57 | 5.21 -> 6.30 | 16:16:36Z |

No run was red, so no `24-04-red-N.log` exists and no step-5 stop (`bore shape` over 15 s, slice over 25 s) was reached; the `checkpoint:decision` was not raised. The `unknown relation op` reading of run 2 (2.11 s against 4.11 s and 4.12 s, and 4.09 to 5.19 s in this phase's earlier logs) is about two seconds low. The only difference the logs show is `.server group members before the kill: 3` in run 2 against 4 in runs 1 and 3 (the floor is 3). The cause was not investigated; the reading is recorded as read, which is the safe direction for a figure that is not a bar.

## The gate

`make verify`, 600 s tool timeout, `investigation/24-04-verify.log`: `1311 passed in 288.08s (0:04:48)`, `make verify exit 0`, first run (the resource-tracker flake did not appear and no re-run was used). Coverage: `TOTAL 1358 22 386 13 97.99%`, `Required test coverage of 96.0% reached. Total coverage: 97.99%`. The test count equals 24-02 and 24-03 (1311), because this plan changes no test or source file. The commit hook ran `make verify.fast` and passed.

## Task Commits

Task 1 (the readings) commits nothing, as the plan says; Task 2 makes the one commit.

1. **Task 1: three browser and three commit-slice readings** - not committed on its own (logs staged in Task 2).
2. **Task 2: record the readings and every red run, make verify, one commit** - `c0675b9` (docs): `docs(24): price the bore-shape step and the commit slice -- three readings each, seen red once`

`git rev-list --count 917e306..HEAD` read 1 right after the commit. The commit adds `bench/RESULTS.md` (123 lines) and 31 files under `investigation/`, and nothing under `src/` or `tests/`; `git show --first-parent --diff-filter=D` listed no deletion.

**Plan metadata:** the SUMMARY commit and the STATE/ROADMAP/REQUIREMENTS commit follow this file.

## Files Created/Modified

- `bench/RESULTS.md` - the `## Bore-shape selector (Phase 24)` section: opening paragraph, `### The bore-shape step, priced (24-04)` (`#### Host state`, `#### Readings`), `### The commit slice with the selector proofs (24-04)`, `### Seen red once (Phase 24)`
- `.planning/phases/24-bore-shape-selector/investigation/24-04-reading-{1,2,3}.log`, `24-04-slice-{1,2,3}.log`, `24-04-verify.log` - the raw output behind this plan's figures
- The 24-01, 24-02 and 24-03 logs, `24-01-red-1.log`, `BASE.txt` and `draft-notes.txt` in the same directory, committed for the first time

## Decisions Made

- No bar is set (D-15); Phase 25 re-sets the gate bar on its final HEAD and absorbs the `bore shape` step, which adds about 8.5 s to one browser run.
- The first-failure lines in the Seen red table were re-read from the kept logs with file and line, not only copied from the SUMMARYs; where a SUMMARY gave no result line or wall time (the twin run read `1 failed, 1 passed in 19.87s`), the log's was used.
- The `ubuntu-latest` reading of the steps is left to the pull request's first CI run and is said so in the section.

## Deviations from Plan

### Other deviations

**1. [Added files] Three files beyond the plan's named list were committed.** The plan says to stage "every file under `.planning/phases/24-bore-shape-selector/investigation/`". Three of them are not in its `need` list: `24-01-red-1.log` (the flake run the Seen red section's closing paragraph cites), `BASE.txt` and `draft-notes.txt` (24-01's working notes: the recorded base and its red-run lines). The directory would otherwise stay partly untracked; they hold no secret and nothing outside the phase's own notes. The commit-content verify requires only that the listed files are present and no `src/` or `tests/` path is.

**2. [Wording] The plan's section text names a gate "near 290 s" in its model (23-04); this one says "near 300 s".** The phase's own full runs read 273 to 336 s (24-01 to 24-03) and this plan's 288 s, so 300 s is what was measured here.

---

**Total deviations:** 0 auto-fixed, 2 noted
**Impact on plan:** None changes a figure, a criterion or a file in `src/` or `tests/`.

## Issues Encountered

None. Every run was green on its first attempt, no reading was over its limit, and the tree was clean (tracked files) before the first run and after the last.

## Known Stubs

None.

## Threat Flags

None. The only surface is a Markdown record and kept logs; T-24-11 is mitigated as the register says (every run's output is kept and committed, the verify parses each log and requires its figures in the tables, the tree was checked clean before and after the runs) and T-24-12 as well (no `src/` or `tests/` file is in the commit, and no wait, timeout or bar moved).

## User Setup Required

None - no external service configuration required.

## Debt and ideas

No debt item and no idea was filed in this plan. The open hex-bore-warning debt (`docs/tech_debt/active/2026-10-11-hex-bore-warns-about-default-bore-fields.md`) keeps its restated trigger from 24-03: a `/gsd-quick` fix before Phase 25's reading.

## Next Phase Readiness

- Phase 25 can cite `## Bore-shape selector (Phase 24)` for the step's price (8.55 s on average here), the slice (15.60 s here) and the readings' host state; it re-sets the gate bar on its final HEAD.
- The `ubuntu-latest` reading of the `bore shape` step comes from the pull request's first CI run, not from this plan.
- Nothing is blocked. All Phase 24 plans now have a SUMMARY; the phase is ready for verification.

## Self-Check: PASSED

- `bench/RESULTS.md` exists and `grep -c '^## Bore-shape selector (Phase 24)$'` reads 1; the 31 files under `investigation/` are tracked (`git ls-files` lists 31, at least the 28 the verify needs).
- `git merge-base --is-ancestor c0675b9 HEAD` found the commit; `git rev-list --count 917e306..HEAD` read 1; exactly one commit carries the subject.
- The Task 1 verify script printed three `reading N:` lines; the Task 2 verify scripts printed `Phase 24 section: readings match their logs, 13 red rows` and `one commit: bench/RESULTS.md and 31 kept logs; make verify exit 0`, and the tree was clean; the row-exact cell check passed.

---
*Phase: 24-bore-shape-selector*
*Completed: 2026-10-12*
