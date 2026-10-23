---
phase: 26-gate-fails-with-a-cause
plan: 07
subsystem: testing
tags: [ci, pytest, faulthandler, durations, twin-selectors, phase-close]

requires:
  - phase: 26-gate-fails-with-a-cause
    provides: plans 26-01 to 26-06, the Phase 26 section of bench/RESULTS.md, the carry item for D-05's post-merge read, and 26-05's -v and --durations flags
provides:
  - "investigation/26-07-verify-local.log: the phase-close gate on the final tree, make verify exit 0, 1321 passed, TOTAL 97.99%"
  - "investigation/26-07-run-38750065494-{test,vendor-bundle,image}.log: the whole job logs of the phase's first CI run, all green on ubuntu-24.04"
  - "pyproject.toml: faulthandler_timeout 120 -> 170, sized from CI's slowest phase (83.55 s) by D-07's rule, in its own fix(26) commit"
  - "bench/RESULTS.md: ### The phase's first CI run (26-07), appended"
affects: [ship, 27, 29]

actuals:
  tokens: 1420    # chars/4 over the added lines in pyproject.toml, bench/RESULTS.md and docs/ (5674 chars); logs excluded
  tasks: 3
  commits: 3
plan_head_before: 3b8ed4469260be0071c4a19f08f02fbb42e645be
plan_head_after: 577b494cf5129bb6138259c2b5114fcceaf5908c
commits: 3

tech-stack:
  added: []
  patterns:
    - "Size a timeout from the slowest measured phase on the slowest runner that runs it, then keep the reading's run id in the comment"

key-files:
  created:
    - .planning/phases/26-gate-fails-with-a-cause/investigation/26-07-verify-local.log
    - .planning/phases/26-gate-fails-with-a-cause/investigation/26-07-run-38750065494-test.log
    - .planning/phases/26-gate-fails-with-a-cause/investigation/26-07-run-38750065494-vendor-bundle.log
    - .planning/phases/26-gate-fails-with-a-cause/investigation/26-07-run-38750065494-image.log
    - .planning/phases/26-gate-fails-with-a-cause/investigation/26-07-verify-after-timeout.log
  modified:
    - pyproject.toml
    - bench/RESULTS.md
    - docs/tech_debt/active/2026-10-10-make-verify-hung-at-98-percent-with-no-failure.md

key-decisions:
  - "D-07 applied: S_ci = 83.55 s (test_model.py hob-root oracle test, -n 4, ubuntu-latest); 2 x S_ci = 167.1 s exceeds the committed 120 s, so faulthandler_timeout = 170"
  - "The hang item's runbook quotes the value and the dump header, so its two lines moved with the value in the same fix commit"

requirements-completed: [REQ-hang-leaves-evidence, REQ-twin-selectors-race-fixed, REQ-ubuntu26-preclassified]

coverage:
  - id: E1
    description: "The phase-close gate passes on the final tree and prints what CI prints: make verify exit 0, 1321 passed in 199.12s, TOTAL 97.99%, a slowest-25 block and -v ids; tests/regression/, src/spur/pool.py and .github/ are byte-identical to v0.5 and bench/RESULTS.md has 0 deleted lines"
    requirement: REQ-hang-leaves-evidence
    verification:
      - kind: integration
        ref: "investigation/26-07-verify-local.log; git diff --exit-code v0.5 -- tests/regression/ src/spur/pool.py .github/"
        status: pass
    human_judgment: false
  - id: E2
    description: "The phase's first CI run (38750065494, draft PR #41) was read whole: three green jobs, 4 workers [1321 items], 1321 passed in 754.03s, TOTAL 98.05%, no Timeout dump; D-07's rule applied to S_ci = 83.55 s and faulthandler_timeout raised 120 -> 170 in its own commit"
    requirement: REQ-hang-leaves-evidence
    verification:
      - kind: integration
        ref: "investigation/26-07-run-38750065494-test.log; the Task 3 verify script (2 x 83.55 = 167.1 <= 170)"
        status: pass
    human_judgment: false
  - id: E3
    description: "The twin-selectors test (test_the_shipped_viewer_in_a_real_browser) PASSED on ubuntu-latest on the first attempt. The step's own print lines are not in the log (no -s), so the reading is the PASS, supporting only; D-05's post-merge main read is carried, not claimed"
    requirement: REQ-twin-selectors-race-fixed
    verification:
      - kind: integration
        ref: "investigation/26-07-run-38750065494-test.log, [gw2] [ 50%] PASSED line; docs/tech_debt/active/2026-10-15-twin-selectors-fix-awaits-the-post-merge-main-read.md (still active)"
        status: pass
    human_judgment: false
  - id: E4
    description: "No Image: line names 26.04 (all three jobs ubuntu-24.04), so no migrated run exists to record for Phase 29; ci.yml is untouched and the PR is still an open draft"
    requirement: REQ-ubuntu26-preclassified
    verification:
      - kind: integration
        ref: "Image: lines in the three job logs; git diff --exit-code v0.5 -- .github/; gh pr view 41 -> OPEN true"
        status: pass
    human_judgment: false

duration: continuation about 25 min (Tasks 1 and 2 ran earlier)
completed: 2026-10-15
status: complete
---

# Phase 26 Plan 07: The phase close and its first CI run Summary

**The phase's tree passes its own gate locally (`1321 passed in 199.12s`) and on CI (run 38750065494, all three jobs green on `ubuntu-24.04`, `1321 passed in 754.03s`); CI's slowest phase was 83.55 s, so D-07's rule raised `faulthandler_timeout` from 120 to 170.**

## Performance

- **Duration:** this continuation about 25 min, most of it waiting on the CI run (14 min wall for `test (3.12)`); Tasks 1 and 2 ran earlier
- **Completed:** 2026-10-15
- **Tasks:** 3 (Task 1 a tracer, Task 2 the human's push, Task 3 auto)
- **Files modified:** 3 source, record or debt files, 5 logs under `investigation/`

## Accomplishments

- **The close gate (Task 1, `6c0e57b`).** `make verify` exit 0, `1321 passed in 199.12s (0:03:19)`, coverage `TOTAL 97.99%`, slowest local phase 29.74 s, no `Timeout (` line. `tests/regression/`, `src/spur/pool.py` and `.github/` are byte-identical to `v0.5`; `bench/RESULTS.md` has 0 deleted lines (`git diff --numstat v0.5`: 552 added, 0 deleted).
- **The push (Task 2, by the human).** Branch `gsd/phase-26-gate-fails-with-a-cause` pushed, the pre-push `make verify` passed, draft PR [#41](https://github.com/halfb00t/spur/pull/41) opened. The run is `38750065494`, event `pull_request`, head sha `6c0e57b6324ec2a9574aa2425eefcbaee439026c`, which equals the HEAD of Task 1.
- **The CI reading (Task 3).** All three jobs `success`:

  | Job | `Image:` | Wall |
  |---|---|---|
  | `test (3.12)` | `ubuntu-24.04` (runner `20261002.596`) | 13 m 59 s |
  | `vendor-bundle` | `ubuntu-24.04` | 10 s |
  | `image` | `ubuntu-24.04` (runner `20261012.601`) | 1 m 56 s |

  `test (3.12)`: `4 workers [1321 items]`, `1321 passed in 754.03s (0:12:34)`, `TOTAL 98.05%` (floor 96.0%), `cadquery 2.8.0 / cadquery-ocp 7.9.3.1.1`, no `Timeout (` dump. The `-v` ids and the 25-line durations block are in the log; the 25th is 19.94 s.
- **D-07's rule.** **S_ci = 83.55 s**, the `call` of `tests/test_model.py::test_the_default_gear_asked_for_the_hob_root_builds_the_oracle_s_root` under `-n 4 --cov`. The committed 120 s came from the local slowest phase (32.33 s, a different test, `test_browser.py`, on an M5 Max). 2 x 83.55 = 167.1 s exceeds 120 s, so the value is **170** (rounded up to the next 10 s), in `faf376b`. The comment names S_ci, the test, the run id and the date. `make venv` was run once after the ini edit. CI's run itself used 120 and no phase reached it.
- **The twin step.** `test_the_shipped_viewer_in_a_real_browser` (which holds the `twin selectors` step) PASSED on `gw2` at 50 %, 47.67 s, first attempt. The step's own print lines are not in the log because the workflow has no `-s`; the reading is the PASS. It is supporting only (a `pull_request` run; both red `main` trees were green on their PR runs).
- **The record.** `### The phase's first CI run (26-07)` appended to `bench/RESULTS.md` in `577b494`: run, jobs, `Image:` lines, durations top 10, S_ci, the rule's outcome, the twin reading and the carried post-merge commands.
- **The gate after the change:** `make verify`, exit 0, `1321 passed in 200.81s (0:03:20)`, `TOTAL 97.99%` (log `26-07-verify-after-timeout.log`).

## Task Commits

1. **Task 1: the phase-close gate on the final tree** - `6c0e57b` (docs)
2. **Task 2: push and draft PR** - done by the human; no commit
3. **Task 3: D-07's timeout change** - `faf376b` (fix); **the CI record and logs** - `577b494` (docs)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] The hang item's runbook quoted the old timeout**
- **Found during:** Task 3, after the value changed
- **Issue:** `docs/tech_debt/active/2026-10-10-make-verify-hung-at-98-percent-with-no-failure.md` states `faulthandler_timeout = 120`, `After 120 s` and `Timeout (0:02:00)` as current state (lines 57 and 64). Left alone, the runbook would tell an operator the wrong dump header.
- **Fix:** updated those two lines to 170, 170 s and `Timeout (0:02:50)`. The dated note at line 51 is history and stays at 120.
- **Files modified:** `docs/tech_debt/active/2026-10-10-make-verify-hung-at-98-percent-with-no-failure.md`
- **Commit:** `faf376b` (the plan said `pyproject.toml` only; the doc is the same concern, one number)

### Process notes

- **The commit trailer follows the session's attribution (Claude Sonnet 5.5)**, not the plan text, as in 26-01 to 26-06.
- **The twin step's printed line `step twin selectors: N.NN s` the plan expected does not exist in the log.** The test never prints it, and the workflow has no `-s`. The plan's wording assumed it; the record says so and rests on the PASS line.
- **`26-07-verify-after-timeout.log` is an extra log** (the plan's step 7 asked for a result line only); kept because it is the evidence for the `make verify` the plan requires after the ini change.
- **The new value is not on the remote.** The pushed run used 120. The PR needs one more push before ship; that push is the human's.

**Total deviations:** 1 auto-fixed (Rule 1), 4 process notes. **Impact:** none on the plan's result.

## Issues Encountered

- `gh run watch` was not used; polling `gh run view --json status` every 10 s worked without API timeouts.
- The test job is about 3.8x slower on CI than the local gate (754.03 s of pytest against 199.12 s, `-n 4` against `-n 8` on a faster host); the 300 s bar of L43 is a local-host bar, so this is a note, not a finding.

## Known Stubs

None. No placeholder, hardcoded empty value or unwired data in the files this plan touched.

## Threat Flags

None. No new network endpoint, auth path or file access at a trust boundary. T-26-17: PR #41 is still `OPEN true` (a draft) and was not marked ready or merged. T-26-18: the timeout changed only under D-07's rule, from recorded durations, in its own commit with the run id in its comment. `.github/` is unchanged from `v0.5`.

## Debt and ideas

- **Still active, as required:** `docs/tech_debt/active/2026-10-15-twin-selectors-fix-awaits-the-post-merge-main-read.md` (`Status: active`, `must`, Active INDEX row present, named in the record). It holds D-05's post-merge read, which cannot happen before `make pr.land`.
- **Edited, not filed:** the hang item's runbook (the number above).
- No new item filed; no idea filed.

## Carried to land time

After `make pr.land PR=41`, on the next phase branch: `gh run list --branch main --workflow ci --limit 1 --json databaseId,headSha,conclusion`, then `gh run view {id} --log --job {test-job-id}`, grep for `PASSED tests/test_browser.py::test_the_shipped_viewer_in_a_real_browser`, and append the run id, head sha and result to `bench/RESULTS.md`; that append retires the carry item. `/gsd-ship` must update PR #41 (`gh pr edit`, `gh pr ready`) rather than create a second one, and the branch needs one more push first so CI carries the 170 s value.

## Next Phase Readiness

The phase is ready for verification and `/gsd-ship`. Requirements: `REQ-hang-leaves-evidence` and `REQ-ubuntu26-preclassified` are fully evidenced. `REQ-twin-selectors-race-fixed` is marked complete on its acceptance (the baseline fix, the parked-`/api/info` proof, the debt retired in the fixing commit) but its outcome clause "no longer reds on `main`" is read only after the land, which the active carry item holds.

## Self-Check: PASSED

- Files exist: `26-07-verify-local.log`, the three `26-07-run-38750065494-*.log`, `26-07-verify-after-timeout.log`, `bench/RESULTS.md` (heading present once), the carry item under `docs/tech_debt/active/`.
- Commits exist on the branch: `6c0e57b`, `faf376b`, `577b494`.
- `make verify`: exit 0, `1321 passed in 200.81s (0:03:20)`; `git diff --exit-code v0.5 -- .github/ tests/regression/ src/spur/pool.py` exits 0; `gh pr view 41` reads `OPEN true`.
