---
phase: 27-ledger-tests-and-harness
plan: 01
subsystem: testing
tags: [ps, process-group, multiprocessing, spawn, ci, ubuntu-24.04, macos, bench]

requires:
  - phase: 26-gate-fails-with-a-cause
    provides: the spike-branch shape (26-02) and the `server group members before the kill` floor line
provides:
  - the server group's members by command, observed with `ps` on macOS (3 runs) and on ubuntu-latest (1 run), with run id, image, version and date
  - whole per-job CI logs and the three macOS logs, kept under investigation/
affects: [27-06 MIN_GROUP_MEMBERS comment, 27-06 retirement of the group-floor debt item, Phase 29 ubuntu-latest rollout reading]

actuals:
  tokens: 26000
  tasks: 3
  commits: 1   # MEASURED on the phase branch: git rev-list --count 9943a7b..HEAD at write time; the spike commit 9c42559 lives only on spike/27-group-listing

plan_head_before: 9943a7bbf7078b420f5142a1bf60986d2e2cda5e
plan_head_after: 1ea663d115c9b0e0d99e1fb1ef9c21e64dbad5f2

tech-stack:
  added: []
  patterns:
    - "A throwaway spike branch (one commit, human pushes, draft PR, closed unmerged) is how a `-s` print reaches a CI log"

key-files:
  created:
    - .planning/phases/27-ledger-tests-and-harness/investigation/27-01-macos-host.log
    - .planning/phases/27-ledger-tests-and-harness/investigation/27-01-macos-run-1.log
    - .planning/phases/27-ledger-tests-and-harness/investigation/27-01-macos-run-2.log
    - .planning/phases/27-ledger-tests-and-harness/investigation/27-01-macos-run-3.log
    - .planning/phases/27-ledger-tests-and-harness/investigation/27-01-run-39428298442-test.log
    - .planning/phases/27-ledger-tests-and-harness/investigation/27-01-run-39428298442-vendor-bundle.log
    - .planning/phases/27-ledger-tests-and-harness/investigation/27-01-run-39428298442-image.log
  modified:
    - bench/RESULTS.md

key-decisions:
  - "The group is the server, its resource tracker and one or two spawned workers on both hosts; 3 vs 4 is a hash-salt outcome of `hash(p) % workers`, not a host property, so a floor above 3 would be wrong on either host"
  - "The run is on ubuntu-24.04 (image 20261012.334.1 for test and image, 20261018.339.1 for vendor-bundle): it is not the first 26.04 ubuntu-latest run, which stays Phase 29's to read"

requirements-completed: [REQ-group-floor-recorded-true]

coverage:
  - id: D1
    description: "macOS server-group listing: three runs, each live `ps` row count equal to its `server group members before the kill` line (4, 3, 4), members named by command"
    requirement: REQ-group-floor-recorded-true
    verification:
      - kind: other
        ref: "Task 1 automated check over 27-01-macos-run-{1,2,3}.log (re-run matching the marker with `in`): 4/4, 3/3, 4/4"
        status: pass
    human_judgment: false
  - id: D2
    description: "ubuntu-latest server-group listing from a green CI run of the spike branch: 4 live rows equal to the floor line 4, whole per-job logs kept, image and version recorded"
    requirement: REQ-group-floor-recorded-true
    verification:
      - kind: other
        ref: "Task 3 automated check over 27-01-run-39428298442-{test,vendor-bundle,image}.log: Image: present in all three, 4 listing rows, floor line 4"
        status: pass
    human_judgment: false
  - id: D3
    description: "bench/RESULTS.md section `### The server group, listed (27-01)` reads as an honest account of what the two listings do and do not show"
    requirement: REQ-group-floor-recorded-true
    verification:
      - kind: other
        ref: "heading count 1, `git diff --numstat v0.5 -- bench/RESULTS.md` deleted column 0 (653 added)"
        status: pass
    human_judgment: true
    rationale: "Whether the prose claims no more than the logs show (L08) is a reading, not a test"

duration: 25min
completed: 2026-10-20
status: complete
---

# Phase 27 Plan 01: The server group, listed Summary

**`ps` listings of the browser test's server group on macOS (4, 3, 4 members) and on ubuntu-latest 24.04 (4 members): the server, its resource tracker and one or two spawned workers, recorded by command in `bench/RESULTS.md` from whole CI logs.**

## Performance

- **Duration:** about 25 min of executor time plus the CI wait (the run itself took 1 min 45 s)
- **Started:** 2026-10-20T12:55Z (ASSUMPTION: approximate; the macOS host log is stamped 12:58:04Z)
- **Completed:** 2026-10-20T13:20Z
- **Tasks:** 3 (one of them the human's push)
- **Files modified:** 8 on the phase branch (`bench/RESULTS.md` plus 7 logs); 2 on the spike branch only

## Accomplishments

- Cut `spike/27-group-listing` from BASE `9943a7bbf7078b420f5142a1bf60986d2e2cda5e` with one commit, `9c42559` (`9c4255967bddab853820aa9f534dc83a8e5414d5`), through the hooks: the `test` job runs only `tests/test_browser.py -s -n0 --no-cov`, and `serve()` prints the group's `ps -ww -A -o pid=,pgid=,stat=,command=` rows. Proved on macOS three times before any push, then switched back.
- Read CI run [39428298442](https://github.com/halfb00t/spur/actions/runs/39428298442) (attempt 1, event `pull_request`, head = the spike commit, created 2026-10-20T13:11:31Z): all three jobs green. `test (3.12)` printed 4 listing rows and `server group members before the kill: 4`, `2 passed in 30.01s`.
- Recorded both listings in `bench/RESULTS.md` under `## Ledger tests and harness (Phase 27)` / `### The server group, listed (27-01)`: host state, a readings table by command, the `pool.py` mechanism for 3 vs 4, and what the listings do not show. 653 lines added, 0 deleted against `v0.5`.
- Closed draft PR #43 unmerged; the remote branch and the local branch are left in place for the human.

## Findings

| Host | Run | Members | By command |
|---|---|---|---|
| macOS M5 Max, 18 CPUs, 64 GiB, macOS 27.0.1, Python 3.12.15, playwright 1.63.0, 2026-10-20 ~12:58Z | 1 | 4 | uvicorn, resource tracker, 2 spawned workers |
| macOS | 2 | 3 | uvicorn, resource tracker, 1 spawned worker |
| macOS | 3 | 4 | uvicorn, resource tracker, 2 spawned workers |
| ubuntu-latest, `Image: ubuntu-24.04`, `Version: 20261012.334.1` (test, image jobs), Ubuntu 24.04.5 LTS, runner 2.337.0, Python 3.12.15, 2026-10-20 13:11Z | 1 | 4 | uvicorn (`Ssl`), resource tracker, 2 spawned workers (`Sl`) |

- No job ran on ubuntu-26.04: `Image:` is `ubuntu-24.04` in all three jobs (`vendor-bundle` landed on the later image `20261018.339.1`). So this is not a 26.04 run and Phase 29's ordering is untouched; no job was red, so Phase 29's stop-and-ask did not arise.
- No `Z` rows and no unexpected command on either host; live rows equal the floor line in every run.
- Per-job results: `test (3.12)` success 13:11:34Z-13:13:19Z, `image` success 13:11:34Z-13:13:13Z, `vendor-bundle` success 13:11:34Z-13:11:43Z; one attempt, no re-run.
- `make verify` on the phase branch before the record commit: `1322 passed in 194.46s (0:03:14)`, exit 0.

## Task Commits

1. **Task 1: spike branch, print proven on macOS, switch back** - `9c42559` on `spike/27-group-listing` only (not on the phase branch); the macOS logs are untracked until Task 3
2. **Task 2: human push and draft PR** - no commit. The orchestrator pushed on the human's explicit instruction (not the executor): `git push -u origin spike/27-group-listing` started 2026-10-20T13:07:31Z, the pre-push `make verify` passed, new branch created on origin; draft PR #43 (https://github.com/halfb00t/spur/pull/43, `isDraft` true, title `spike(27): list the browser test's server group on ubuntu-latest -- DO NOT MERGE`); CI run 39428298442, headSha `9c4255967bddab853820aa9f534dc83a8e5414d5`, created 13:11:31Z
3. **Task 3: record both listings** - `1ea663d` (docs)

**Plan metadata:** the commit that adds this SUMMARY, STATE.md and ROADMAP.md (docs: complete plan)

## Files Created/Modified

- `bench/RESULTS.md` - new section for Phase 27 and the 27-01 record
- `.planning/phases/27-ledger-tests-and-harness/investigation/27-01-macos-host.log`, `27-01-macos-run-{1,2,3}.log` - the local listings and host facts
- `.planning/phases/27-ledger-tests-and-harness/investigation/27-01-run-39428298442-{test,vendor-bundle,image}.log` - whole per-job logs from `gh run view --log --job`

## Decisions Made

- Recorded the 3-vs-4 spread as a hash-salt outcome (`src/spur/pool.py` lines 95-101), read from the code, not observed; the logs show only the commands. 27-06 writes the `MIN_GROUP_MEMBERS` comment from this record.
- Left the remote spike branch and PR-closing as the plan says: closed with a comment, no `--delete-branch`, no merge, no force-push.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Task 1's automated check under-counted listing rows by one**
- **Found during:** Task 1 (macOS runs)
- **Issue:** the check filtered rows with `r.startswith('spur-group-listing: ')`. With `-s -v`, pytest prints `PASSED` without a newline, so the first listing row lands as `PASSEDspur-group-listing: ...` and the filter missed it: 3 vs 4, 2 vs 3, 3 vs 4.
- **Fix:** re-ran the check matching the marker with `in` and slicing from it. All three runs pass: 4/4, 3/3, 4/4. The CI log has the same glued first row (line 774 of the test log); Task 3's check already uses `in`, and the record says so.
- **Files modified:** none (check only)
- **Verification:** the re-run above; Task 3's Linux check prints `linux listing rows 4, floor line 4`
- **Committed in:** n/a (no file change)

**2. [Process] A shell loop in Task 3 wrote one log under an empty slug**
- **Found during:** Task 3 step 3. A zsh `for pair in "id slug"` did not word-split, so the first `gh run view --log --job` call wrote `27-01-run-39428298442-.log`.
- **Fix:** deleted that untracked scratch file and fetched the three logs with explicit commands; all three kept files are from `gh run view --log --job`, whole. Never committed.

---

**Total deviations:** 1 auto-fixed (Rule 3), 1 process slip with no effect on the record
**Impact on plan:** none on scope; the first only corrected a check's filter.

## Issues Encountered

- `.planning/milestone.lock` is an untracked file that predates this plan; it was left alone and not committed.

## Known Stubs

None. The listing print and the workflow edit exist only on the spike branch; `git grep spur-group-listing HEAD -- tests .github` finds nothing and `git diff --exit-code v0.5 -- .github/workflows/ci.yml` exits 0 on the phase branch.

## Debt filed

None filed. The group-floor debt item `docs/tech_debt/active/2026-10-10-group-floor-of-3-is-not-two-pool-workers.md` is retired in 27-06, not here.

## Authentication Gates

None.

## User Setup Required

None - no external service configuration required. The human still owns deleting `spike/27-group-listing` (local and `origin`) when they choose.

## Next Phase Readiness

- 27-06 can cite this record's run id (39428298442), image (`ubuntu-24.04`, `20261012.334.1`) and date (2026-10-20) in the `MIN_GROUP_MEMBERS` comment without an assumption. Floor stays 3: macOS printed 3 once, Linux printed 4 once.
- The shared working tree is back on `gsd/phase-27-ledger-tests-and-harness`, so 27-02 onward may proceed.

---
*Phase: 27-ledger-tests-and-harness*
*Completed: 2026-10-20*

## Self-Check: PASSED

Verified: `bench/RESULTS.md`, `27-01-macos-host.log`, `27-01-macos-run-{1,2,3}.log` and the three `27-01-run-39428298442-*.log` files exist; `1ea663d` is an ancestor of HEAD; `9c42559` is on `spike/27-group-listing` (remote branch present, not an ancestor of HEAD); PR #43 reads `CLOSED unmerged`; branch is `gsd/phase-27-ledger-tests-and-harness`.
