---
phase: 26-gate-fails-with-a-cause
plan: 02
subsystem: ci
tags: [ci, ubuntu-26.04, runner-image, spike, bench]

requires:
  - phase: 26-gate-fails-with-a-cause
    provides: plan 26-01, the Phase 26 section of bench/RESULTS.md and the investigation/ directory
provides:
  - "bench/RESULTS.md ### Ubuntu 26.04, pre-classified (26-02): the v0.5 tree on image ubuntu-26.04 20261012.163.1, all three jobs green"
  - "the three whole per-job logs of run 38724011970 under investigation/"
  - "a dated pointer in the still-active Ubuntu 26 debt item"
affects: [26-07, 29-*]

actuals:
  tokens: 1800    # chars/4 over the authored lines (RESULTS.md and the debt item, 7,234 B); the 340 KB of committed CI logs are not authored text and are excluded
  tasks: 3
  commits: 1
plan_head_before: 3d69e985a612377040107d4cb118903e5998ae77
plan_head_after: f30402f1c719b8666b9303ad60f2a7df6e61f57b
commits: 1

tech-stack:
  added: []
  patterns:
    - "A runner-image change is read before it lands: a throwaway draft PR cut from the shipped tag with only runs-on changed, whole logs kept, classified before any ci.yml edit"

key-files:
  created:
    - .planning/phases/26-gate-fails-with-a-cause/investigation/26-02-run-38724011970-test.log
    - .planning/phases/26-gate-fails-with-a-cause/investigation/26-02-run-38724011970-vendor-bundle.log
    - .planning/phases/26-gate-fails-with-a-cause/investigation/26-02-run-38724011970-image.log
  modified:
    - bench/RESULTS.md
    - docs/tech_debt/active/2026-10-10-ubuntu-latest-migrates-to-ubuntu-26-on-19-october.md

key-decisions:
  - "No ci.yml edit lands anywhere but the throwaway spike branch: the three jobs were green, so no pin to ubuntu-24.04 was proposed or made"
  - "The Ubuntu 26 debt item stays Status: active; Phase 29 resolves it against the first ubuntu-latest run that names 26.04"

requirements-completed: [REQ-ubuntu26-preclassified]

coverage:
  - id: D1
    description: "Branch spike/26-ubuntu-26 holds one commit on v0.5 whose diff is the three runs-on lines on ubuntu-26.04"
    requirement: REQ-ubuntu26-preclassified
    verification:
      - kind: integration
        ref: "git diff --numstat v0.5 spike/26-ubuntu-26 (3 added, 3 deleted, one file); parent 26ddd74"
        status: pass
    human_judgment: false
  - id: D2
    description: "Each of the three jobs has its whole log kept and is classified in bench/RESULTS.md before any ci.yml edit"
    requirement: REQ-ubuntu26-preclassified
    verification:
      - kind: integration
        ref: "grep -c '^### Ubuntu 26.04, pre-classified (26-02)$' bench/RESULTS.md prints 1; each log holds one Image: line; 0 deleted lines against v0.5"
        status: pass
    human_judgment: false
  - id: D3
    description: "PR #40 closed unmerged, branch kept, no ubuntu-24.04 pin, debt item still active with its pointer"
    requirement: REQ-ubuntu26-preclassified
    verification:
      - kind: integration
        ref: "gh pr view 40 reads CLOSED unmerged; git ls-remote --heads origin spike/26-ubuntu-26 lists 21c0346; git diff --exit-code v0.5 -- .github/workflows/ci.yml exits 0"
        status: pass
    human_judgment: false

duration: ~29min
completed: 2026-10-15
status: complete
---

# Phase 26 Plan 02: Ubuntu 26.04 pre-classification Summary

**The shipped v0.5 tree, with only its three `runs-on` lines on `ubuntu-26.04`, runs green on image `20261012.163.1` (1318 passed, 98.05 % coverage, browser install 14.44 s); recorded with the whole logs before the 2026-10-19 rollout, PR #40 closed unmerged.**

## Performance

- **Duration:** ~29 min wall (Task 1 started 2026-10-15T10:49:11Z; record committed 11:17Z). The run itself took 13 min 54 s, and the wait on it was the bulk of the time.
- **Completed:** 2026-10-15
- **Tasks:** 3 (Task 1 a tracer, Task 2 the human's push, Task 3 auto)
- **Files modified:** 5 on the phase branch (`bench/RESULTS.md`, the debt item, three logs), plus `.github/workflows/ci.yml` on the spike branch only

## Accomplishments

- **Spike branch** `spike/26-ubuntu-26`: one commit `21c0346` (parent `26ddd74`, the `v0.5` commit), diff from `v0.5` is `.github/workflows/ci.yml`, 3 added and 3 deleted, lines 13, 61 and 77. Made with plain `git commit` through the hooks (`make verify.fast`, skip-token). The main checkout stayed on the phase branch.
- **Push and draft PR** (Task 2): the human said "push and open PR"; the orchestrator pushed `spike/26-ubuntu-26` (the pre-push `make verify` passed) and opened draft PR [#40](https://github.com/halfb00t/spur/pull/40), `spike(26): ubuntu-26.04 pre-classification -- DO NOT MERGE`, on that instruction. The CI run appeared at 2026-10-15 10:58:19Z.
- **Run 38724011970** (`ci`, `pull_request`, attempt 1, head `21c0346`, created 10:58:19Z), read whole:

| Job | Image line | Result | Start / finish (UTC) | Classification |
|---|---|---|---|---|
| `test (3.12)` | `Image: ubuntu-26.04`, `Version: 20261012.163.1` | success, 13 min 54 s | 10:58:23Z / 11:12:17Z | green |
| `vendor-bundle` | `Image: ubuntu-26.04`, `Version: 20261012.163.1` | success, 18 s | 10:58:23Z / 10:58:41Z | green |
| `image` | `Image: ubuntu-26.04`, `Version: 20261012.163.1` | success, 1 min 55 s | 10:58:23Z / 11:00:18Z | green |

- **Readings** (`test (3.12)`): Ubuntu 26.04.1 LTS (apt codename `resolute`), runner 2.337.0, Python 3.12.15, `pytest -n 4`, `1318 passed in 754.49s (0:12:34)`, coverage TOTAL `1358 21 386 13 98.05%` against the 96.0 % floor, `Contracts: 5 kept, 0 broken.`, `playwright install --with-deps --only-shell chromium` 14.44 s (9 packages newly installed, 21.9 MB archives, 80.2 MB disk; 24.04 read 13.97 s, 9 packages, 21.5 MB, 79.5 MB). `image` printed `smoke: kernel, exports, ASGI stack and validation all live`.
- **No red signature in any log:** the count of `FAILED`, `resource_tracker`, `ReentrantCall`, `ExceptionGroup`, `twin selectors`, `rerun`, `Traceback` is 0 on each of the three. One attempt, no re-run.
- **Record:** `bench/RESULTS.md` `### Ubuntu 26.04, pre-classified (26-02)`, 123 lines added, 0 deleted against `v0.5`: the run table, host state, readings with the 24.04 values of 21-08 beside them, the ordering against the rollout, what the log does and does not show, and the outcome.
- **Debt item** `2026-10-10-ubuntu-latest-migrates-to-ubuntu-26-on-19-october.md` stays `Status: active` and gained a dated pointer paragraph; the INDEX row is unchanged.
- **PR #40 closed unmerged** with the plan's comment: `gh pr view 40` reads `CLOSED unmerged`; the remote branch still lists `21c0346`; `git merge-base --is-ancestor spike/26-ubuntu-26 HEAD` exits 1.
- **SC5 is met.** The ordering check found no earlier `ubuntu-latest` run naming 26.04: the newest `ci` run before the spike, 38680454993 (`main`, 04:14Z), and four others read `Image: ubuntu-24.04`. So the D-16 missed-clock branch did not apply.
- **The gate:** `make verify` on the phase branch, exit 0, `1320 passed in 207.86s (0:03:27)`, `TOTAL 1358 22 386 13 97.99%`, `Required test coverage of 96.0% reached`.

## Task Commits

1. **Task 1: cut spike/26-ubuntu-26** - `21c0346` (on `spike/26-ubuntu-26` only; parent `26ddd74`). It is not on the phase branch and not a phase-plan commit.
2. **Task 2: the human pushes and opens the draft PR** - no commit; done on the human's explicit instruction, PR #40.
3. **Task 3: read, classify, record, close the PR** - `f30402f` (docs): `docs(26): pre-classify the v0.5 tree on ubuntu-26.04 from the spike run's whole logs`.

`commits: 1` is measured on the phase branch from the ledger base `3d69e98`; the spike commit is on its own branch.

**Plan metadata:** the docs commit that carries this SUMMARY (below).

## Files Created/Modified

- `bench/RESULTS.md` - the 26-02 subsection, appended
- `docs/tech_debt/active/2026-10-10-ubuntu-latest-migrates-to-ubuntu-26-on-19-october.md` - the dated pre-classification pointer, status unchanged
- `.planning/phases/26-gate-fails-with-a-cause/investigation/26-02-run-38724011970-{test,vendor-bundle,image}.log` - the three whole logs (786, 193 and 1,715 lines)

## Decisions Made

- Everything green, so there was no `red, new` job: no `checkpoint:decision` was returned and no `ubuntu-24.04` pin was proposed. The pin stays the human's call, and the debt item still names it as the fallback.
- The record states what one green run does not clear: the twin-selectors race and the resource-tracker flake are intermittent and not ranked by one run, the image is revised weekly, and the run was on the pinned label `ubuntu-26.04`, not on `ubuntu-latest`, so that the migrated label resolves to this image version is confirmed only by the first migrated run (Phase 29).
- The commit trailer follows the session's attribution (`Claude Sonnet 5.5`), not the plan's `Claude Opus 5.5` text, as in 26-01.

## Deviations from Plan

None - plan executed exactly as written. One note, not a deviation: the first `gh run watch` died after 10 minutes on `dial tcp 140.82.121.5:443: i/o timeout` (a network error reading the run, not a job result; the run was still `in_progress`). The wait was resumed by polling `gh run view`, and the run completed `success` at 11:12Z, well inside the 90-minute cap.

## Issues Encountered

None beyond the transient network timeout above.

## Debt and ideas filed

None filed. One existing item updated and kept active: `2026-10-10-ubuntu-latest-migrates-to-ubuntu-26-on-19-october` (must).

## Known Stubs

None.

## Threat Flags

None. T-26-02 (spike merged by mistake) mitigated: draft PR, title `-- DO NOT MERGE`, no `gh pr merge` or `make pr.land`, closed unmerged. T-26-04 mitigated: every job read from its whole log, one attempt recorded. T-26-03, T-26-05 and T-26-SC accepted as planned.

## User Setup Required

None. The remote branch `spike/26-ubuntu-26` is left for the human to delete (`spike/21-linux-runner` precedent).

## Next Phase Readiness

- 26-07 and Phase 29 have the baseline: image `ubuntu-26.04` `20261012.163.1`, install 14.44 s, 1318 passed, start and finish times for ordering. Phase 29 reads the first `ubuntu-latest` run whose `Set up job` names 26.04 against it and resolves the debt item.

## Self-Check: PASSED

- FOUND: `bench/RESULTS.md` (one `### Ubuntu 26.04, pre-classified (26-02)`, 0 deleted lines against `v0.5`), the debt item (`Status: active`, pointer present), all three `26-02-run-38724011970-*.log`, each with one `Image:` line
- FOUND: commit `f30402f` (ancestor of HEAD) and `21c0346` on `spike/26-ubuntu-26` (parent `26ddd74`, three-line diff); `commits: 1` measured from the ledger base `3d69e98`
- `git diff --exit-code v0.5 -- .github/workflows/ci.yml` exits 0 on the phase branch; PR #40 `CLOSED unmerged`; remote spike branch present; no `ubuntu-24.04` in any commit of this plan

---
*Phase: 26-gate-fails-with-a-cause*
*Completed: 2026-10-15*
