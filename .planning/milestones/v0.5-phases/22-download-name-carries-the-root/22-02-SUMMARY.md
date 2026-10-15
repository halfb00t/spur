---
phase: 22-download-name-carries-the-root
plan: 02
subsystem: testing
tags: [bench, playwright, browser-test, build-wait, readings, seen-red]

requires:
  - phase: 22-download-name-carries-the-root
    provides: "plan 01's download name browser step, L40, and the three kept 22-01 logs"
provides:
  - "three readings of the download name step with host state, copied from kept logs, in bench/RESULTS.md"
  - "Seen red once (Phase 22): 22-01's four red runs with commands and reverts"
  - "BUILD_WAIT_MS comment carrying the step's readings; the value stays 45_000"
affects: [phase-25-gate-bar, download-name]

plan_head_before: 5c6c02541df4da54af274a0ce8df93d17dbb0f8b
plan_head_after: f905a25e8e319a27dbb889b22ebfcc71bbc575ec
actuals:
  tokens: 1899
  tasks: 2
  commits: 1

tech-stack:
  added: []
  patterns:
    - "a gate cost is read from the step's own timing, three readings, each figure copied from a kept log"

key-files:
  created:
    - .planning/phases/22-download-name-carries-the-root/investigation/22-02-reading-1.log
    - .planning/phases/22-download-name-carries-the-root/investigation/22-02-reading-2.log
    - .planning/phases/22-download-name-carries-the-root/investigation/22-02-reading-3.log
    - .planning/phases/22-download-name-carries-the-root/investigation/22-02-verify.log
  modified:
    - bench/RESULTS.md
    - tests/browser_session.py

key-decisions:
  - "No bar is set from these readings; Phase 25 re-sets the gate bar on its final HEAD and absorbs the download name step (D-06)"
  - "BUILD_WAIT_MS stays 45_000: the slowest reading, 3.56 s, is far under 21 PD-04's 15 s"

patterns-established:
  - "A reading that varies 3x across three back-to-back runs is reported as read, with the cause marked unestablished"

requirements-completed: [REQ-slug-carries-effective-root]

coverage:
  - id: D1
    description: "Three readings of the download name step, with host state, are in bench/RESULTS.md and each figure equals its kept log"
    requirement: REQ-slug-carries-effective-root
    verification:
      - kind: other
        ref: "Task 2 first automated block (parses 22-02-reading-N.log and requires each step and click figure in the table)"
        status: pass
    human_judgment: false
  - id: D2
    description: "BUILD_WAIT_MS stays 45_000 and tests/browser_session.py changed only in comments"
    verification:
      - kind: other
        ref: "Task 2 second automated block (AST comparison with docstrings blanked, on the commit)"
        status: pass
    human_judgment: false
  - id: D3
    description: "22-01's four red runs are recorded in Seen red once (Phase 22)"
    verification:
      - kind: other
        ref: "Task 2 first automated block (at least four rows beginning | 22-01)"
        status: pass
    human_judgment: true
    rationale: "Whether each row's first failure line is a faithful copy of 22-01's record is a reviewer's check; the block only counts rows"
  - id: D4
    description: "make verify is green on the committed tree"
    verification:
      - kind: other
        ref: "make verify, investigation/22-02-verify.log ends make verify exit 0"
        status: pass
    human_judgment: false

duration: 6min
completed: 2026-10-11
status: complete
---

# Phase 22 Plan 02: Price the Download-Name Step Summary

**The `download name` browser step read 3.56, 3.20 and 1.13 s (mean 2.63 s) on an Apple M2 Max at load 6.5 to 7.0, all under 21 PD-04's 15 s, so `BUILD_WAIT_MS` stays at 45 s and no bar is set; the readings, 22-01's four red runs and the kept logs are in one commit**

## Performance

- **Duration:** 6 min
- **Started:** 2026-10-11T06:33:06Z
- **Completed:** 2026-10-11T06:39:18Z
- **Tasks:** 2
- **Files modified:** 2 tracked files edited (`bench/RESULTS.md`, `tests/browser_session.py`), 7 kept logs added

## Accomplishments

- Three readings of `step download name` on the committed tree (HEAD `5c6c025`, which contains 22-01's `e3b1181`), one at a time in the foreground, each with `uptime` before and after and its raw output kept as a log.
- `bench/RESULTS.md` gained `## Download name carries the root (Phase 22)` with `### The download step, priced (22-02)` (`#### Host state`, `#### Readings`) and `### Seen red once (Phase 22)` with four `| 22-01 |` rows. L40's forward citation of this section now resolves.
- The `BUILD_WAIT_MS` comment in `tests/browser_session.py` carries the step's three readings, the host, the date and the slowest build-bound step. The value is untouched and the file differs only in comments (checked by AST on the commit).

## Task Commits

1. **Task 1: three readings** - no commit; the logs are committed by Task 2, as the plan directs.
2. **Task 2: record, comment, make verify, one commit** - `f905a25` (docs): `docs(22): price the download-name step -- three readings, seen red once and the build-wait comment`

**Plan metadata:** the docs commit that carries this SUMMARY, STATE.md and ROADMAP.md

## The readings

Host: Apple M2 Max, `bench.machine_facts()` = `12 CPUs, arm64, 32.0 GiB RAM`, macOS 27.0.1 (26A434), Python 3.12.13, playwright 1.63.0, pytest 9.1.1, Chrome Headless Shell 153.0.8010.12. Not an idle host: at the start `ps` listed `mediaanalysisd` at 98 % CPU, `WindowServer` 39 %, `trivy` 26 % and a Firefox plugin container 22 %, none started by this plan. Every figure is an upper bound for an idle host.

| Run | Result line | `step download name` | click to download | `step first build drawn` | 1-minute load before -> after | UTC start |
|---|---|---|---|---|---|---|
| 1 | `1 passed in 9.25s` | 3.56 s | 0.14 s | 2.98 s | 6.83 -> 6.47 | 06:33:24Z |
| 2 | `1 passed in 8.33s` | 3.20 s | 0.12 s | 2.92 s | 6.83 -> 7.00 | 06:33:36Z |
| 3 | `1 passed in 6.14s` | 1.13 s | 0.13 s | 2.91 s | 6.76 -> 6.62 | 06:33:48Z |

Mean 2.63 s, range 1.13 to 3.56 s. The spread is wide for three runs 12 s apart at a steady load and the logs do not say why run 3 is about 2 s under runs 1 and 2; `bench/RESULTS.md` reports it as read, not explained. The slowest build-bound step was `download name` in runs 1 and 2 and `first build drawn` in run 3. No reading is near 15 s, so the plan's `checkpoint:decision` was not triggered. All three runs were green; there was no red run and no `22-02-red-N.log`.

The Phase 21 host (Apple M5 Max, 18 CPUs) is not this host, so none of these figures is compared with Phase 21's. 22-01's own reading of the step was 1.13 s in both runs at load 5 to 6.5, and 22-RESEARCH's was 3.28 s; both are quoted in RESULTS, not compared.

The `ubuntu-latest` reading of the step (RESEARCH A2, A3) comes from the pull request's first CI run, not from this plan.

## Gate

- `make verify` on the tree as committed (`f905a25`'s content; the working tree held nothing else): **`1238 passed in 222.53s (0:03:42)`**, `TOTAL 1349 22 384 14 97.92%`, `Required test coverage of 96.0% reached. Total coverage: 97.92%`, `make verify exit 0`. Log: `.planning/phases/22-download-name-carries-the-root/investigation/22-02-verify.log`.
- The pre-commit hook ran `make verify.fast` and passed.
- Both automated blocks of Task 2 passed (the second after the commit): `Phase 22 section: 3 readings match their logs, 4 red rows, 22-01 at e3b1181` and `one commit: readings, comment-only browser_session.py, kept logs, make verify exit 0`.
- Acceptance greps: the section heading count is 1, `BUILD_WAIT_MS = 45_000` count is 1, and `git status --porcelain --untracked-files=no` printed nothing after the commit.

## Files Created/Modified

- `bench/RESULTS.md` - the Phase 22 section: readings, host state, 22-01's red rows
- `tests/browser_session.py` - five comment lines above `BUILD_WAIT_MS`; value unchanged
- `.planning/phases/22-download-name-carries-the-root/investigation/22-01-browser-red.log`, `22-01-browser-green.log`, `22-01-verify.log` - 22-01's logs, committed here as planned
- `.planning/phases/22-download-name-carries-the-root/investigation/22-02-reading-{1,2,3}.log`, `22-02-verify.log` - this plan's logs

## Decisions Made

None beyond the plan. D-06 (no bar set, Phase 25 absorbs the step) and PD-11 (no move of `BUILD_WAIT_MS` toward a pass) were followed as written.

## Deviations from Plan

None - plan executed exactly as written. The precondition held at both points: exactly one sha (`e3b1181`) for 22-01's subject, and `git status --porcelain --untracked-files=no` printed nothing. HEAD is `5c6c025`, the docs commit after `e3b1181`, which contains it.

## Issues Encountered

None. The host is shared and busy (see above), which RESULTS states; no run failed and `make verify` was green on the first run.

## Known Stubs

None.

## Threat Flags

None. This plan adds a record, five comment lines and logs; no new surface. T-22-06 is mitigated by the log-parsing verify (every figure in the table matched its log) and T-22-07 by the unchanged `45_000`, checked on the commit.

## Debt and ideas filed

No debt item was filed. No idea was filed.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Plan 02 is the last plan of Phase 22. The phase is ready for verification. Phase 25 re-sets the gate bar on its final HEAD and absorbs the `download name` step. The pull request's first CI run supplies the `ubuntu-latest` reading.

## Self-Check: PASSED

- FOUND: `bench/RESULTS.md`, `tests/browser_session.py`, `investigation/22-02-reading-1.log`, `22-02-reading-2.log`, `22-02-reading-3.log`, `22-02-verify.log`
- FOUND: commit `f905a25` is an ancestor of HEAD; `git rev-list --count 5c6c025..HEAD` read 1 before this docs commit

---
*Phase: 22-download-name-carries-the-root*
*Completed: 2026-10-11*
