---
phase: 21-browser-test-of-the-viewer
plan: 02
subsystem: testing
tags: [playwright, ubuntu-latest, github-actions, webgl2, swiftshader, spike]

requires:
  - phase: 21-01
    provides: the tracer, the $(BROWSER) stamp, PNG_RATIO_BAR 4.9 from the macOS reading
provides:
  - the tracer green inside make verify on a real ubuntu-latest runner, headless shell installed with --with-deps through sudo
  - PNG_RATIO_BAR and BUILD_WAIT_MS confirmed from the lower of two hosts (4.9 and 45000 ms, neither moved)
  - the runner's host state, install cost, renderer and step times in bench/RESULTS.md
  - the whole log of run 38044109910 kept under investigation/
affects: [21-03, 21-04, 21-05, 21-06, 21-07, 21-08, 25]

actuals:
  tokens: 3400
  tasks: 3
  commits: 1

plan_head_before: e5deff82659ad4ec22ada2c38d0165a821c047ed
plan_head_after: be40b0f74e50ae1bf7a7039e6109f26c7b9d5906
commits: 1

tech-stack:
  added: []
  patterns:
    - a throwaway spike branch carries the admission wiring and a diagnostic CI step; only readings return to the phase
    - a bar is set by a rule written before the reading and recorded beside both hosts' numbers

key-files:
  created:
    - .planning/phases/21-browser-test-of-the-viewer/investigation/21-02-run-38044109910.log
  modified:
    - tests/browser_session.py
    - bench/RESULTS.md

key-decisions:
  - "PNG_RATIO_BAR stays 4.9: PD-03 on the lower of macOS 9.933 and ubuntu-latest 10.446 is 4.966, rounded down to 4.9"
  - "BUILD_WAIT_MS stays 45000 ms: the slowest build-bound step read 2.53 s on macOS and 4.75 s on Linux, under PD-04's 15 s"
  - "--with-deps needs no sudo line in the workflow: Playwright switches to root itself on the runner"

patterns-established:
  - "The Linux half of a spike is read from a draft do-not-merge PR; a fix the runner forces is ported to the phase as its own commit (none was needed)"

requirements-completed: [REQ-browser-stack-pinned, REQ-browser-first-build-drawn, REQ-browser-server-fixture]

coverage:
  - id: D1
    description: "The headless shell installs with --with-deps (sudo, apt) on ubuntu-latest and the tracer runs green inside make verify"
    requirement: REQ-browser-stack-pinned
    verification:
      - kind: other
        ref: "GitHub Actions run 38044109910, job test (3.12): conclusion success, 1221 passed in 906.71s, tracer in the -rP PASSES section"
        status: pass
    human_judgment: false
  - id: D2
    description: "The first build is drawn on the runner above the canvas bar, with data-triangles equal to the STL header, and the server group floor of 3 holds on the runner's procps"
    requirement: REQ-browser-first-build-drawn
    verification:
      - kind: other
        ref: "run 38044109910 log: ratio 10.45 (bar 4.9); data-triangles 9066, STL header 9066; server group members before the kill: 3"
        status: pass
    human_judgment: false
  - id: D3
    description: "PNG_RATIO_BAR and BUILD_WAIT_MS follow PD-03 and PD-04 from both hosts' readings and the phase branch still passes"
    requirement: REQ-browser-server-fixture
    verification:
      - kind: integration
        ref: "make test PYTEST_ARGS='tests/browser_scenarios.py -n0 --no-cov -q' -> 1 passed in 3.37s; make verify -> 1220 passed in 204.54s"
        status: pass
    human_judgment: false

duration: 43min
completed: 2026-10-10
status: complete
---

# Phase 21 Plan 02: The Linux Runner Spike Summary

**The browser tracer ran green inside `make verify` on ubuntu-latest (shell installed with `--with-deps`, drawn at 10.45x blank on SwiftShader Subzero), and the canvas bar (4.9) and build wait (45 s) were confirmed from the lower of the two hosts without moving**

## Performance

- **Duration:** 43 min (09:52:44Z to 10:35Z; most of it waiting for the human's push and the 16 min 25 s CI job)
- **Tasks:** 3 (Task 2 a human-action checkpoint, answered before this agent began)
- **Files modified:** 2 on the phase branch, 1 log added; 4 on the throwaway spike branch

## Accomplishments

- The Linux path works as first pushed: one run, green, no red run to classify. `playwright install --with-deps --only-shell chromium` switched to root by itself and took 14.7 s; no `sudo` line is needed in the workflow.
- The tracer's readings on the runner: renderer `SwiftShader Device (Subzero)`, canvas PNG blank 3,654 B and drawn 38,168 B (ratio 10.45), `data-triangles` 9066 against the header's 9066, 3 server group members before the kill, steps 0.04 / 0.16 / 4.75 / 0.25 s.
- The bars hold on both hosts: the lower ratio is macOS's 9.933, so PD-03 gives 4.966, rounded down to 4.9, unchanged. The slowest build-bound step (4.75 s on Linux, 2.53 s on macOS) is under PD-04's 15 s, so 45 s stays.

## Task Commits

1. **Task 1: the throwaway branch** - `a6a4fc5` on `spike/21-linux-runner` only, never on the phase branch, by design (`test(spike): run the browser tracer on ubuntu-latest -- throwaway branch, never merged (21-02)`)
2. **Task 2: push and draft PR** - no commit (remote only)
3. **Task 3: readings, constants, log** - `be40b0f` (`test(21-02): set the canvas bar and the build wait from the macOS and ubuntu-latest readings`)

**Plan metadata:** the commit that carries this file (docs: complete plan)

## Task 2 response (verbatim)

The human's response to the blocking `checkpoint:human-action` was: `pushed, PR #32`.

The orchestrator, at the human's instruction, ran `git push -u origin spike/21-linux-runner` (the pre-push hook's `make verify` passed on the spike branch) and opened the draft PR. `gh pr view 32` read `isDraft: true`, `headRefName: spike/21-linux-runner`, `state: OPEN`, title `spike(21): browser tracer on ubuntu-latest -- DO NOT MERGE`.

## Runs

| Run | Branch head | Conclusion | Classification |
|---|---|---|---|
| 38044109910 (`ci`) | `a6a4fc5` | success; `test (3.12)` 16 min 25 s, `vendor-bundle`, `image` green | none: no red run, one of the three allowed pushes used |

Log: `.planning/phases/21-browser-test-of-the-viewer/investigation/21-02-run-38044109910.log` (3,164 lines, the whole run).

## Local reading on the spike branch (Task 1)

`make verify PYTEST_ARGS="--durations=5"` on `spike/21-linux-runner`: `1221 passed in 181.07s (0:03:01)`, exit 0, coverage 97.92 %. Apple M5 Max, macOS, 1-minute load 5.53 at the start, 2026-10-10. The tracer was not among the five slowest durations (all `tests/test_model.py`, slowest 29.72 s). Not a bar.

## Constants before and after

| Constant | Before | After | Rule |
|---|---|---|---|
| `PNG_RATIO_BAR` | 4.9 | 4.9 | PD-03: `floor(10 * min(9.933, 10.446) / 2) / 10` = 4.9; not under 2.0 |
| `BUILD_WAIT_MS` | 45000 | 45000 | PD-04: slowest build-bound step 4.75 s, not over 15 s |

Only the comments changed: each now carries both hosts' readings, host, date and run id.

## Verification at the end of Task 3

- Quick run `make test PYTEST_ARGS="tests/browser_scenarios.py -n0 --no-cov -q"`: `1 passed in 3.37s`.
- `make verify PYTEST_ARGS="--durations=3"` on the phase branch: `1220 passed in 204.54s (0:03:24)`, coverage 97.92 % against the 96 % floor (the staging module is still uncollected).
- The RESULTS.md check script printed `Linux spike recorded, bar 4.9`.
- `git merge-base --is-ancestor spike/21-linux-runner HEAD` fails (not an ancestor); `git diff --exit-code 592506f` over the fixture, `tests/test_api.py` and the product modules exits 0.

## Files Created/Modified

- `tests/browser_session.py` - comments of `BUILD_WAIT_MS` and `PNG_RATIO_BAR` carry both hosts' readings; values unchanged
- `bench/RESULTS.md` - `### Linux runner spike (21-02)`: branch and sha, PR, run table, runner host state, readings, the two rules applied, answers to A1, A2, A4, A7, A8
- `.planning/phases/21-browser-test-of-the-viewer/investigation/21-02-run-38044109910.log` - the whole run log

## Decisions Made

- Both constants keep their values; the decision is the recorded rule application, not a change.
- The Linux install size was not measured (the diagnostic step ran `ls`, not `du`); recorded as not measured rather than borrowed from macOS.

## Deviations from Plan

None - plan executed exactly as written. The runner was green on the first push, so no spike or phase fix was needed and no ported commit exists.

## Issues Encountered

- The job wall time (16 min 25 s) and pytest wall (906.71 s) look slow beside macOS, but three earlier `main` runs of the same job read 8 min 54 s, 16 min 04 s and 16 min 35 s (pytest 487 to 924 s) with no browser test, so one sample cannot attribute any of it to the browser. The browser steps total about 5.2 s. Phase 25 owns pricing the gate.
- `free -m` was read after the run, so the A7 memory answer is "no OOM", not a peak.
- `gh run watch` exceeded the shell's 10 minute limit once and was re-issued, as the plan allows.

## Known Stubs

None.

## Threat Flags

None. The runner step reuses the pin 21-01's legitimacy check approved; `--with-deps` runs apt through sudo on GitHub's ephemeral runner only (T-21-09, accepted); local hosts never pass it.

## Action for the human

Draft PR #32 is still open. It must never be merged and `make pr.land` must never run on it. The readings are recorded, so it is safe to close it unmerged now; deleting the remote branch `spike/21-linux-runner` is the human's call. The throwaway branch `spike/21-linux-runner` (local) also stays out of the phase branch's history.

## Next Phase Readiness

21-03 onward can build scenarios on a Linux path that is known to install, draw and tear down cleanly. 21-06 lands the admission wiring for real from the spike's diff (`git show a6a4fc5`). SC5's own real run is 21-08's, on the phase's head.

## Self-Check: PASSED

- Files found: `tests/browser_session.py`, `bench/RESULTS.md`, `investigation/21-02-run-38044109910.log`
- Commit found on HEAD: `be40b0f`; spike commit `a6a4fc5` found on `spike/21-linux-runner` and absent from HEAD
- Plan checks re-run: quick run `1 passed`; `make verify` `1220 passed in 204.54s`; RESULTS.md script printed `Linux spike recorded, bar 4.9`; the not-an-ancestor and `git diff --exit-code 592506f` checks exit 0

---
*Phase: 21-browser-test-of-the-viewer*
*Completed: 2026-10-10*
