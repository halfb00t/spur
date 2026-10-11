---
phase: 23-conditional-form-fields
plan: 04
subsystem: testing
tags: [bench, browser-test, commit-slice, playwright, measurement, kept-logs]

requires:
  - phase: 23-conditional-form-fields
    provides: "the inert fields step, the extended golden sweep, tests/test_relations.py and the kept investigation logs (plans 23-01 to 23-03)"
provides:
  - "bench/RESULTS.md ## Conditional form fields (Phase 23): the inert-fields step priced (three readings), the commit slice with the proof module priced (three readings), ### Seen red once (Phase 23) with ten rows"
  - "Every kept log of the phase committed under investigation/ (25 files), the six readings and the green make verify beside them"
  - "L41's forward citation of the readings resolved"
affects: [25-gate-bar, 24-bore-selector]


actuals:
  tokens: 3388
  tasks: 2
  commits: 2
plan_head_before: b013c27cc96ed431c6b5550e6277f5a0b1b3b38e
plan_head_after: 1e348a5a7d77d6df2516824468900ab11fb1ba59
commits: 2

tech-stack:
  added: []
  patterns:
    - "A step is priced by its own timing, three foreground readings with host state and a kept log each, every table figure copied from its log and checked by a script"

key-files:
  created:
    - .planning/phases/23-conditional-form-fields/investigation/23-04-reading-1.log
    - .planning/phases/23-conditional-form-fields/investigation/23-04-reading-2.log
    - .planning/phases/23-conditional-form-fields/investigation/23-04-reading-3.log
    - .planning/phases/23-conditional-form-fields/investigation/23-04-slice-1.log
    - .planning/phases/23-conditional-form-fields/investigation/23-04-slice-2.log
    - .planning/phases/23-conditional-form-fields/investigation/23-04-slice-3.log
    - .planning/phases/23-conditional-form-fields/investigation/23-04-red-1.log
    - .planning/phases/23-conditional-form-fields/investigation/23-04-verify.log
  modified:
    - bench/RESULTS.md
    - docs/tech_debt/active/2026-10-06-resource-tracker-flake-fails-the-gate.md

key-decisions:
  - "A first make verify red on the resource-tracker flake was classified against the open debt, its log kept as 23-04-red-1.log, and re-run once on the identical tree; the occurrence is recorded on the debt, the fix and isolation runs are left to the human"

requirements-completed: [REQ-form-walk-proves-relations, REQ-dim-and-editable]

coverage:
  - id: D1
    description: "Three browser readings on the committed tree, each kept as 23-04-reading-N.log, recorded with host state in bench/RESULTS.md; step inert fields 1.31, 1.33, 1.33 s, step golden sweep 0.37, 0.32, 0.30 s"
    requirement: REQ-dim-and-editable
    verification:
      - kind: other
        ref: "Task 1 verify script (reading 1..3 lines) and Task 2 verify script (figures in the table)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Three make verify.fast readings with tests/test_relations.py in the slice, each under L36's 30 s: 15.05, 15.24, 15.14 s wall"
    requirement: REQ-form-walk-proves-relations
    verification:
      - kind: other
        ref: "investigation/23-04-slice-{1,2,3}.log ending make verify.fast exit 0"
        status: pass
    human_judgment: false
  - id: D3
    description: "Seen red once (Phase 23): ten rows, one per first-failure line the 23-01, 23-02 and 23-03 SUMMARYs recorded, each with command, kept log and revert"
    requirement: REQ-form-walk-proves-relations
    verification:
      - kind: other
        ref: "Task 2 verify script (10 red rows)"
        status: pass
    human_judgment: false
  - id: D4
    description: "make verify green on the tree the commit holds, log kept; one commit holding bench/RESULTS.md and the kept logs and nothing under src/ or tests/"
    requirement: REQ-form-walk-proves-relations
    verification:
      - kind: other
        ref: "investigation/23-04-verify.log ending make verify exit 0; the Task 2 commit-shape script: one commit: bench/RESULTS.md and 25 kept logs"
        status: pass
    human_judgment: false

duration: 15min
completed: 2026-10-11
status: complete
---

# Phase 23 Plan 04: Price the inert-fields step and the commit slice Summary

**The `inert fields` step reads 1.32 s (1.31 to 1.33) and the commit slice with the proof module in it 15.14 s wall (15.05 to 15.24) against L36's 30 s kill, on three readings each; ten deliberate reds and every kept log of the phase are committed beside them, and no bar is set.**

## Performance

- **Duration:** about 15 min (first host-state read 13:04:34Z, SUMMARY 13:19Z; the two `make verify` runs were 293 s and 301 s of it)
- **Started:** 2026-10-11T13:04:34Z
- **Completed:** 2026-10-11T13:19:00Z
- **Tasks:** 2 (Task 1 takes the readings and commits nothing; Task 2 commits, per the plan's one-commit design, PD-11)
- **Files modified:** 2 tracked files changed, 25 logs added

## Accomplishments

- Three browser readings and three `make verify.fast` readings on HEAD `b013c27`, one at a time in the foreground, every figure in `bench/RESULTS.md` copied from its kept log and checked by script.
- `### Seen red once (Phase 23)` with ten rows (two `tests/test_api.py` pins, the `inert fields` step before the code, the input listener, three proof-module tests against one relation, `bore_chamfer` on the real model, the `readHash()` and `#reset` call sites), each with command, kept log and how it was reverted.
- All 25 logs under `investigation/` are tracked, so 23-01 to 23-03's evidence is no longer untracked.

## Task Commits

1. **Task 1: the six readings** - not committed, by design.
2. **Task 2: record the readings and the reds, make verify, one commit with the kept logs** - `f4f9774` (docs): `docs(23): price the inert-fields step and the commit slice -- three readings each, seen red once`. Files: `bench/RESULTS.md` (M) and 25 logs (A); nothing under `src/` or `tests/`.
3. **Unplanned, see Deviations:** `1e348a5` (docs) records the fifth resource-tracker occurrence on its open debt.

**Plan metadata:** the `docs(23-04)` commit that follows this SUMMARY.

## Host state

Apple M2 Max, `bench.machine_facts()` = `12 CPUs, arm64, 32.0 GiB RAM`, macOS 27.0.1, Darwin 27.0.0, Python 3.12.13, playwright 1.63.0, pytest 9.1.1, pytest-xdist 3.8.0, pytest-cov 7.1.0. HEAD `b013c27`; the phase's commits `e09f834`, `fb97ba2`, `d11af97`, `4c1eba3`, `e4f63ff`. Tracked tree clean (STATE.md and state.json excluded) before the runs and after.

Not an idle host: load averages 3.24 7.15 7.55 at 13:04:34Z, falling to 2.4 (1-minute) by the last browser run. `ps` listed `WindowServer` 28 % and an OrbStack helper 27 % at the start (38 % and 11 % at the end) and the `claude` session process at 15 %, none started by this plan. Every wall figure is an upper bound for an idle host and none is a bar.

## Readings

Browser (`make test PYTEST_ARGS="tests/test_browser.py -n0 --no-cov -q -s"`, logs `23-04-reading-N.log`, each `make test exit 0`):

| Run | Result line | inert fields (s) | golden sweep (s) | first build drawn (s) | 1-min load before -> after | UTC start |
|---|---|---|---|---|---|---|
| 1 | `1 passed in 8.08s` | 1.31 | 0.37 | 2.99 | 3.22 -> 3.11 | 13:04:41Z |
| 2 | `1 passed in 7.49s` | 1.33 | 0.32 | 2.90 | 2.86 -> 2.71 | 13:04:52Z |
| 3 | `1 passed in 7.45s` | 1.33 | 0.30 | 2.88 | 2.57 -> 2.45 | 13:05:03Z |

Mean `inert fields` 1.32 s, mean `golden sweep` 0.33 s. `first build drawn` is the slowest build-bound step in every run, far under 21 PD-04's 15 s, so `BUILD_WAIT_MS` stays at 45 s. The other steps' seconds per run are in `bench/RESULTS.md`.

Commit slice (`/usr/bin/time -p make verify.fast`, logs `23-04-slice-N.log`, each `make verify.fast exit 0`):

| Run | Result line | real (s) | 1-min load before -> after | UTC start |
|---|---|---|---|---|
| 1 | `850 passed in 14.44s` | 15.05 | 2.33 -> 2.38 | 13:05:13Z |
| 2 | `850 passed in 14.68s` | 15.24 | 2.38 -> 2.67 | 13:05:31Z |
| 3 | `850 passed in 14.59s` | 15.14 | 2.54 -> 4.39 | 13:05:49Z |

Mean 15.14 s wall, about 15 s under the 30 s kill. Quoted as other readings, not compared: 23-RESEARCH 17.06 s pytest / 17.866 s wall (840 tests, `fed44fe`), 23-02's 14.85 s before and 14.92 s after.

## Red runs

One run was not green: this plan's first `make verify` (`1 failed, 1247 passed in 293.27s`, `TOTAL 97.99 %`), `tests/test_pool.py::test_health_reports_pool_state` on worker `gw1`, an `ExceptionGroup` of five `ReentrantCallError` warnings from `multiprocessing.resource_tracker`. Class: the resource-tracker signature, the open debt `docs/tech_debt/active/2026-10-06-resource-tracker-flake-fails-the-gate.md` (a fifth occurrence, in a test the debt had not named). Whole log kept: `investigation/23-04-red-1.log`. One re-run of the identical tree read green. No browser or slice run was red.

## make verify

`make verify exit 0`: `1248 passed in 300.70s (0:05:00)`, `Required test coverage of 96.0% reached. Total coverage: 97.99%`, `TOTAL 1355 22 386 13 97.99%`. Log: `investigation/23-04-verify.log`. The commit hook ran `make verify.fast` and passed on both commits.

## Decisions Made

None beyond the plan. No bar is set: Phase 25 re-sets the gate bar on its final HEAD and absorbs these steps. The `ubuntu-latest` reading of the steps comes from the pull request's first CI run, not from this plan.

## Deviations from Plan

**1. [Rule 2 - Missing critical] Recorded the fifth resource-tracker occurrence on its debt**
- **Found during:** Task 2 (`make verify`)
- **Issue:** the debt's own trigger ("the next `make verify` failure, with its whole log kept") fired; leaving it unrecorded would lose the occurrence (CLAUDE.md: known-bad behaviour survives in files).
- **Fix:** a paragraph appended to the existing debt file, in a separate commit so `f4f9774` stays what the plan prescribes (RESULTS.md and logs). The debt's isolation runs and fix plan were not run: they are the human's decision, previously re-deferred by the human.
- **Files modified:** `docs/tech_debt/active/2026-10-06-resource-tracker-flake-fails-the-gate.md`
- **Committed in:** `1e348a5`

**Total deviations:** 1 (Rule 2). **Impact on plan:** one extra docs commit; the plan's commit is unchanged. The fixing itself is outside this plan (a `must` debt the human has re-deferred more than once).

## Issues Encountered

- The first `make verify` was red on the known flake; the re-run on the identical tree was green (see Red runs). A third occurrence in the future should not be re-run silently: the trigger on the debt now says the isolation runs and fix plan are due.

## Filed items

No new debt or idea file. One existing debt (`2026-10-06-resource-tracker-flake-fails-the-gate.md`) gained its fifth-occurrence paragraph; its INDEX row is unchanged.

## Known Stubs

None.

## Threat Flags

None. No source, test, endpoint or auth path changed (T-23-11 and T-23-12 mitigated: every figure is checked against its kept log, no wait, timeout or bar moved, no `src/` or `tests/` file in the commit).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Phase 23's four plans are complete; ready for phase verification. The dim visual in both themes (23-01 D4, 23-03 D5) is the human judgement left for end-of-phase verification. For the human: the resource-tracker debt's trigger has fired again and asks for a decision on isolation runs and a fix.

## Self-Check: PASSED

- Files: `bench/RESULTS.md` (one `## Conditional form fields (Phase 23)` heading), the six reading and slice logs, `23-04-red-1.log` and `23-04-verify.log` exist and are tracked (25 files under `investigation/`).
- Commits `f4f9774` and `1e348a5` are ancestors of HEAD; `git rev-list --count b013c27..HEAD` read 2 before this SUMMARY; `git show --name-status f4f9774` lists `bench/RESULTS.md` and 25 logs, nothing under `src/` or `tests/`.
- Both Task verify scripts printed their success lines; `make verify exit 0` with `1248 passed`.

---
*Phase: 23-conditional-form-fields*
*Completed: 2026-10-11*
