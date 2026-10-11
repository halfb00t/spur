---
phase: 21-browser-test-of-the-viewer
plan: 08
subsystem: testing
tags: [ci, ubuntu-latest, playwright, decision-log, l39, idea-retirement, sc5]

requires:
  - phase: 21-07
    provides: the browser test priced in isolation and under the full gate, and the human's answer "accept"
  - phase: 21-06
    provides: tests/test_browser.py admitted into make verify and CI, excluded from the commit slice
  - phase: 21-02
    provides: the Linux runner spike (run 38044109910) the real run is compared with
provides:
  - "bench/RESULTS.md ### The Linux path on the real runner (21-08): run 38059369744 green on the phase branch, SC5 met"
  - the whole CI log kept under investigation/21-08-run-38059369744.log
  - "L39 in the decision log: the admission, amending L13 and L36 and restating L11 unchanged"
  - the browser-test idea retired to docs/ideas/retired/ with a Retired table in the ideas index
  - a must-debt item for ubuntu-latest becoming Ubuntu 26 on 2026-10-19
affects: [23, 24, 25]

actuals:
  tokens: 8057
  tasks: 3
  commits: 3

plan_head_before: 88df5cf9610e199203b56b9ae6f18a9dc0125953
plan_head_after: ac8762ba3102f7909940ea627210f2b036386948
commits: 3

tech-stack:
  added: []
  patterns:
    - a real-runner reading is recorded by run id, head sha, job timestamps from gh and the whole log, never from a prediction
    - an idea that ships moves to docs/ideas/retired/ in the commit that ships it, with a Retired table (PD-13)

key-files:
  created:
    - .planning/phases/21-browser-test-of-the-viewer/investigation/21-08-run-38059369744.log
    - docs/tech_debt/active/2026-10-10-ubuntu-latest-migrates-to-ubuntu-26-on-19-october.md
  modified:
    - bench/RESULTS.md
    - docs/architecture/decision_log.md
    - docs/ideas/INDEX.md
    - docs/tech_debt/INDEX.md
    - docs/ideas/retired/2026-09-21-browser-test-for-the-viewer.md (renamed from docs/ideas/)

key-decisions:
  - "L39 locks the admission: a headless browser inside make verify and CI, out of the commit slice (five heavy files), at a price the human accepted"
  - "SC5 is recorded from the phase branch's own run (38059369744, head 88df5cf), not from the spike or a container"

patterns-established:
  - "Pin the head sha of the pushed commit and the passed count of the local B arm, then read the run against both"

requirements-completed: [REQ-browser-in-the-gate, REQ-browser-stack-pinned]

coverage:
  - id: D1
    description: "SC5: tests/test_browser.py inside make verify green on a real ubuntu-latest run of the phase branch, run id, head sha, job wall time, install lines and result count recorded"
    requirement: REQ-browser-stack-pinned
    verification:
      - kind: e2e
        ref: "gh run view 38059369744 --json jobs: test (3.12) success, 1226 passed in 887.92s, head 88df5cf9610e199203b56b9ae6f18a9dc0125953"
        status: pass
      - kind: other
        ref: "Task 2 automated verify: SC5 recorded; spike unmerged ok"
        status: pass
    human_judgment: false
  - id: D2
    description: "L39 records the admission (amends L13 and L36, restates L11) with every figure cited"
    requirement: REQ-browser-in-the-gate
    verification:
      - kind: other
        ref: "Task 3 automated verify: L39 ok, run 38059369744"
        status: pass
      - kind: integration
        ref: "make verify: 1226 passed in 142.96s"
        status: pass
    human_judgment: false
  - id: D3
    description: "The browser-test idea is retired in the commit that closes the phase"
    requirement: REQ-browser-in-the-gate
    verification:
      - kind: other
        ref: "Task 3 automated verify: task3 verify 2 ok (git mv, Status: retired, Retired in equals the commit subject, ## Retired row)"
        status: pass
    human_judgment: false

duration: 25 min
completed: 2026-10-10
status: complete
---

# Phase 21 Plan 08: The Linux Path Proved and L39 Logged Summary

**The phase branch's own suite is green on a real ubuntu-latest run (38059369744, `1226 passed in 887.92s`, job 16 min 8 s, shell installed in 13.97 s), and L39 locks the admission while the browser-test idea retires in the same closing commit.**

## Performance

- **Duration:** 25 min (this continuation agent: Task 2 and Task 3; Task 1 was the human's push)
- **Started:** 2026-10-10T14:23:54Z
- **Completed:** 2026-10-10T14:48:49Z
- **Tasks:** 3 (Task 1 a `checkpoint:human-action`, Tasks 2 and 3 auto)
- **Files modified:** 7 (plus the kept log)

## Task 1 response (verbatim)

The human's response to the blocking `checkpoint:human-action` was: `pushed, PR #33`.

The orchestrator, at the human's instruction, checked the preconditions and pushed. `bench/RESULTS.md` `#### Outcome` records `Human's answer: "accept"`; `git status --porcelain` showed no tracked change; `git merge-base --is-ancestor spike/21-linux-runner HEAD` exited non-zero. `git push -u origin gsd/phase-21-browser-test-of-the-viewer` succeeded, the pre-push hook's `make verify` (browser test included) passed, and the pushed sha is `88df5cf9610e199203b56b9ae6f18a9dc0125953`. Draft PR #33, `https://github.com/halfb00t/spur/pull/33`, base `main`, title `Phase 21: Browser Test of the Viewer`. The spike's draft PR #32 was already closed unmerged; `spike/21-linux-runner` is kept on `origin`. The agent pushed, opened and closed nothing.

## The real run

| | |
|---|---|
| PR | #33 (draft, base `main`) |
| Run | `ci` 38059369744, event `pull_request`, https://github.com/halfb00t/spur/actions/runs/38059369744 |
| Head sha | `88df5cf9610e199203b56b9ae6f18a9dc0125953`, equal to the pushed `HEAD` (verified by `gh run list ... --json headSha` against `git rev-parse HEAD`) |
| Conclusion | success: `test (3.12)`, `image` (2 min 13 s) and `vendor-bundle` (12 s) all green. First push, no red run, so nothing to classify: one run of the three allowed |
| `test (3.12)` wall time | 16 min 8 s (968 s): `startedAt` 14:22:50Z, `completedAt` 14:38:58Z, read from `gh run view --json jobs` |
| Runner image | `ubuntu-24.04` `20261004.327.1`, runner 2.337.0 (the same image as the spike) |
| Install | `.venv/bin/python -m playwright install --with-deps --only-shell chromium`, 13.97 s (14:23:52.993 to 14:24:06.962), under `/home/runner/work/spur/spur/.venv/ms-playwright` (`chromium_headless_shell-1243`, `ffmpeg-1011`); spike: 14.7 s |
| Result line | `1226 passed in 887.92s (0:14:47)`, `[1226 items]`, coverage TOTAL `1346 21 384 14 97.98%` against the 96.0 % floor |
| Against the local B arm (21-07) | 1226 against 1226, same test set (the diff between `45195ce` and `88df5cf` touches only `bench/RESULTS.md`, `docs/tech_debt/` and `.planning/`). Coverage: macOS read 22 missed statements, the runner 21; both above the floor, not investigated |
| Against the spike (21-02) | job 16 min 25 s and `1221 passed in 906.71s`; both within the band three no-browser `main` runs span (487.39 s to 924.02 s of pytest), so neither shows what the browser test adds. Phase 25 prices the gate |
| Spike stays unmerged | `gh pr list --head spike/21-linux-runner --state merged` prints 0; PR #32 `CLOSED`, `mergedAt` null; the branch is not an ancestor of `HEAD` |

The log does not name `tests/test_browser.py`: the workflow runs `make verify` without the spike's `-rP`, so no per-test or per-step line is printed. That it ran rests on the collected count (1226 is the A arm's 1225 plus this file's one test), the install stamp running in the same job and the file's fail-closed shape (no skip path). `bench/RESULTS.md` says so.

## Accomplishments

- SC5 met on the phase's own suite, not the spike's: the run id, head sha, job timestamps, runner image, install lines and path, result line and coverage are in `### The Linux path on the real runner (21-08)`, and the whole 2,713-line log is kept.
- `L39` written in L38's shape: the choice, what it amends (L13, L36) and restates (L11), the one production line, what the test proves with its seen-red counts, the install, the price and the human's `accept`, the Linux path with both run ids, what Phases 23-24 must do, reversibility, reason and Machine.
- The browser-test idea retired: `git mv` into `docs/ideas/retired/`, `Status: retired`, `Retired in:` equal to the closing commit's subject, an `## Outcome` paragraph, a new `## Retired` table in `docs/ideas/INDEX.md`, and the bore-selector (Phase 24) and conditional-fields (Phase 23) rows updated.
- A risk the run surfaced is filed rather than lost: `ubuntu-latest` becomes Ubuntu 26 on 2026-10-19 and the browser test's install has only run on 24.04.

## Task Commits

1. **Task 1: the human pushes and opens PR #33** - no commit (remote only; `pushed, PR #33`)
2. **Task 2: the real run read and recorded (SC5)** - `0144f38` (docs): `bench/RESULTS.md` and the kept log
3. **Debt filed during Task 2** - `fdc90c4` (docs): `ubuntu-latest` moves to Ubuntu 26 on 2026-10-19
4. **Task 3: the closing commit, L39 and the idea retirement** - `ac8762b` (docs), the subject identical to the idea's `Retired in:` line

**Plan metadata:** the commit that carries this SUMMARY, STATE.md, ROADMAP.md and REQUIREMENTS.md follows. `commits: 3` counts the plan's own commits and was measured with `git rev-list --count 88df5cf9610e199203b56b9ae6f18a9dc0125953..HEAD` before it.

## Verification

- `make verify` on the closing tree: `======================= 1226 passed in 142.96s (0:02:22) =======================`, coverage TOTAL 97.92 % (`Required test coverage of 96.0% reached`), `real 143.39`, 1-minute load 3.87 before, Apple M5 Max, macOS. Each commit also passed the commit stage (`make verify.fast ... Passed`, `reject GitHub Actions skip tokens ... Passed`).
- Task 2 verify: `SC5 recorded`; the kept log exists; `gh pr list --head spike/21-linux-runner --state merged ... length` is 0 and the spike is not an ancestor of `HEAD`.
- Task 3 verify: `L39 ok, run 38059369744`; the commit-shape check (`task3 verify 2 ok`: the idea moved, `Status: retired`, the `## Retired` row, `Retired in:` equal to the commit subject, `M` on the decision log and `R074` on the idea in one commit).
- Acceptance: `grep -n '^## L39 — '` prints one line (2299) and it is the last `## L` header; `git diff --exit-code 592506f -- tests/regression/pre_v0_2.json tests/test_api.py src/spur/params.py src/spur/calc.py src/spur/model.py src/spur/pool.py src/spur/app.py src/spur/cli.py` exits 0; `git diff 592506f --stat -- src/` lists only `src/spur/static/app.js`; `git merge-base --is-ancestor 88df5cf HEAD` exits 0.
- The closing commit itself reaches CI on the human's next push; no run of it exists yet, and L39 says so.

## Decisions Made

- L39 locks the placement D-01 chose, with its price as the human accepted it and its reversibility rated costly.
- SC5 is read from the phase branch's pull-request run only. The ubuntu:24.04 container and the spike are cited as the earlier proof, not as SC5.

## Deviations from Plan

### Auto-fixed Issues

None to fix in code. Three departures from the plan's text, none touching the product:

**1. [Rule 2 - Missing critical] Filed the Ubuntu 26 migration as debt**
- **Found during:** Task 2 (reading the run's annotations)
- **Issue:** the run carries "The ubuntu-latest label will migrate to Ubuntu 26 beginning October 19, 2026". The browser test fails closed, so a broken `--with-deps` install on the new image turns every pull request red, and no run of it exists there.
- **Fix:** one `must` debt file with a named trigger (the first CI run after 2026-10-19 that reads Ubuntu 26) and its INDEX row, per CLAUDE.md's debt rule. One static check was made and recorded as such: the pinned driver (`playwright` 1.63.0) names `ubuntu26.04-x64`; that is not a run, and the file flags it as an unverified assumption. Pinning `runs-on: ubuntu-24.04` is named as the fallback and left as the human's call.
- **Files modified:** `docs/tech_debt/active/2026-10-10-ubuntu-latest-migrates-to-ubuntu-26-on-19-october.md`, `docs/tech_debt/INDEX.md`
- **Committed in:** `fdc90c4`, its own commit (one concern per commit)

**2. [Plan text vs. tree] The `app.js` acceptance criterion reads two lines, not one**
- **Found during:** Task 3 acceptance
- **Issue:** the criterion says the diff against `592506f` "adds exactly one line, the `canvas.dataset.triangles` assignment". The diff adds two: the assignment and the one comment line above it that 21-01 wrote (`// The browser test's one scene observable; STLLoader is non-indexed: 3 vertices per triangle.`).
- **Fix:** none made. The production statement is one; the comment is the project's "comments carry the why" rule and is 21-01's reviewed work. L39 says "with one comment line above it" so the record matches the tree. Removing the comment would edit a product file this plan is bound not to touch.
- **Files modified:** none

**3. [Convention] Commit trailer**
- **Issue:** the orchestrator's rules name `Co-Authored-By: Claude Fable 5.1`; the harness attribution for commits created from here names `Claude Sonnet 5.5`, the model that made them. The three commits of this plan carry `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`; earlier plans' commits carry the Fable 5.1 line.

---

**Total deviations:** 1 auto-added (Rule 2), 2 recorded departures from plan text.
**Impact on plan:** none on the product or on SC4/SC5. The debt item is out-of-plan scope, small and named for a trigger.

## Issues Encountered

- `gh run watch --exit-status` returned early once, printing a sibling job's steps while `test (3.12)` was still running (the run read `in_progress`); the run was then polled in the foreground in 20 s steps until `completed`. No effect on the reading: every figure comes from the completed run.
- `.planning/PROJECT.md:75` and an earlier decision-log entry (`decision_log.md:1384`) still name the idea's old path `docs/ideas/2026-09-21-browser-test-for-the-viewer.md`. The log entry is locked prose and L39 says it stays as written; `PROJECT.md` is the milestone document and was not touched by this plan.

## Known Stubs

None. No code was added in this plan.

## Threat Flags

None. The plan changed documents and a kept log only; the one new surface it found (the runner image change) is filed as debt.

## Debt filed

Yes: `docs/tech_debt/active/2026-10-10-ubuntu-latest-migrates-to-ubuntu-26-on-19-october.md` (`must`), with its row in `docs/tech_debt/INDEX.md`, in `fdc90c4`. No idea filed beyond the retirement.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- All eight plans of Phase 21 have a SUMMARY; the phase is ready for verification (`/gsd-verify-work`).
- Phases 23-24 inherit L39's rule: "the same fields are sent" is an empty diff on `tests/regression/golden_requests.json`, or a `make golden.regen` commit of its own saying what moved and why.
- The branch holds two commits (and this plan's metadata commit) that are not on `origin`: `0144f38`, `fdc90c4`, `ac8762b`. They reach CI on the human's next push, which also tests the closing commit; the agent did not push.

## Self-Check: PASSED

- FOUND: `bench/RESULTS.md`, `docs/architecture/decision_log.md`, `docs/ideas/INDEX.md`, `docs/ideas/retired/2026-09-21-browser-test-for-the-viewer.md`, `docs/tech_debt/active/2026-10-10-ubuntu-latest-migrates-to-ubuntu-26-on-19-october.md`, `.planning/phases/21-browser-test-of-the-viewer/investigation/21-08-run-38059369744.log`
- FOUND commits (ancestors of `HEAD`): `0144f38`, `fdc90c4`, `ac8762b`
- Every `<acceptance_criteria>` line of Tasks 2 and 3 re-run; the one literal mismatch (the `app.js` line count) is deviation 2 above.

---
*Phase: 21-browser-test-of-the-viewer*
*Completed: 2026-10-10*
