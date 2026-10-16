---
phase: 26-gate-fails-with-a-cause
plan: 03
subsystem: testing
tags: [playwright, browser-test, flake, xdist, tech-debt]

requires:
  - phase: 26-gate-fails-with-a-cause
    provides: plans 26-01 and 26-02, the Phase 26 section of bench/RESULTS.md and the investigation/ directory
provides:
  - "tests/test_browser.py twin step: baseline taken after the link's own /api/model.stl request and a DEBOUNCE_SETTLE_MS settle, zero-request assertion after a second settle, /api/info 200 precheck"
  - "_follow_link's /api/info wait bounded by BUILD_WAIT_MS (21 IN-04a)"
  - "the real-app arm table, the CX-05 control and 20 of 20 green runs at -n 8, recorded in bench/RESULTS.md"
  - "the twin-selectors must item retired; D-05's post-merge main read carried in an active must item; 21 IN-04b filed"
affects: [26-07, 28-*]

actuals:
  tokens: 4500    # chars/4 over the authored lines (test diff, two debt items, the retired item's Resolution, arms.md, RESULTS section); logs and diffs of throwaway arms excluded
  tasks: 3
  commits: 3
plan_head_before: f7eeb7075fe4ce689b001087711af538601a84a3
plan_head_after: 6d3702c946a97f0096b87b72940f4edbc0852089
commits: 3

tech-stack:
  added: []
  patterns:
    - "A race in a test is located on the real app before the fix: throwaway arms applied with git apply and reverted with git apply -R, three runs each, every log kept"
    - "A delay is a parked route released from the test, never a sleep in a handler"

key-files:
  created:
    - .planning/phases/26-gate-fails-with-a-cause/investigation/26-03-arms.md
    - .planning/phases/26-gate-fails-with-a-cause/investigation/26-03-arm1.diff
    - .planning/phases/26-gate-fails-with-a-cause/investigation/26-03-arm2.diff
    - .planning/phases/26-gate-fails-with-a-cause/investigation/26-03-arm3.diff
    - .planning/phases/26-gate-fails-with-a-cause/investigation/26-03-cx05-old.diff
    - .planning/phases/26-gate-fails-with-a-cause/investigation/26-03-cx05-new.diff
    - docs/tech_debt/active/2026-10-15-twin-selectors-fix-awaits-the-post-merge-main-read.md
    - docs/tech_debt/active/2026-10-15-wait-until-parked-spins-without-a-pause.md
  modified:
    - tests/test_browser.py
    - bench/RESULTS.md
    - docs/tech_debt/INDEX.md
    - docs/tech_debt/resolved/2026-10-15-twin-selectors-step-reds-main.md

key-decisions:
  - "The lever the old baseline races on is the /api/info response, not the STL route: SC2's 'a delayed STL route makes the old step red' is corrected on the record, with the real-app arms as the evidence"
  - "The control's stray update sends two requests (info, then the aborted STL), so the CX-05 red reads '2 request(s)', not the '1' the plan text quoted; the control was not bent to read 1"
  - "The 20 of 20 count is recorded as not separating the fix from a fast host (the old step was not run 20 times); the arms are the proof of the mechanism"

requirements-completed: [REQ-twin-selectors-race-fixed]

coverage:
  - id: D1
    description: "The old twin step run against the real app under three arms, 3 runs each, before any fix: parked STL route green, parked /api/info red, parked /api/info with the new baseline green"
    requirement: REQ-twin-selectors-race-fixed
    verification:
      - kind: integration
        ref: ".planning/phases/26-gate-fails-with-a-cause/investigation/26-03-arm{1,2,3}-run{1,2,3}.log (arm 2: 'twin selectors: 1 request(s) sent by two pending picks' x3; arms 1 and 3: '1 passed' x3)"
        status: pass
    human_judgment: false
  - id: D2
    description: "The committed step takes its baseline after the link's own /api/model.stl request and a settle past the 350 ms debounce, and settles again before the zero-request assertion"
    requirement: REQ-twin-selectors-race-fixed
    verification:
      - kind: integration
        ref: "make test PYTEST_ARGS=\"tests/test_browser.py tests/test_browser_pins.py --no-cov -q\" (5 passed); CX-05 control: old passes, settled step red (26-03-cx05-{old,new}.log)"
        status: pass
    human_judgment: false
  - id: D3
    description: "IN-04a: _follow_link bounded by BUILD_WAIT_MS; IN-04b filed, _wait_until_parked byte-identical to v0.5; src/ untouched"
    requirement: REQ-twin-selectors-race-fixed
    verification:
      - kind: integration
        ref: "region compare of _wait_until_parked against v0.5; git diff --exit-code v0.5 -- src/ tests/regression/ (exit 0)"
        status: pass
    human_judgment: false
  - id: D4
    description: "The browser files pass 20 of 20 local runs at -n 8 through make test, every log kept, no early stop and no retry"
    requirement: REQ-twin-selectors-race-fixed
    verification:
      - kind: integration
        ref: ".planning/phases/26-gate-fails-with-a-cause/investigation/26-03-repeat-{1..20}.log (5 passed, exit 0 each); bench/RESULTS.md '### Twin selectors (26-03)'"
        status: pass
    human_judgment: false
  - id: D5
    description: "The must item is retired in the fixing commit with a Resolution that separates proven from not proven, and D-05's post-merge main read is carried in an active must item"
    requirement: REQ-twin-selectors-race-fixed
    verification: []
    human_judgment: true
    rationale: "Prose and index bookkeeping; no test asserts the wording, the verifier reads the files. The post-merge main read itself cannot be performed inside the phase."

duration: ~22min
completed: 2026-10-15
status: complete
---

# Phase 26 Plan 03: The twin-selectors step stops reding main Summary

**The twin step takes its request baseline only after the page's own `/api/model.stl` request and a 1 000 ms settle, because the real app showed the race is the `/api/info` response arriving late, not a delayed STL route; 20 of 20 local runs at `-n 8`, the must item retired.**

## Performance

- **Duration:** ~22 min wall (start time not captured; estimated from the first command at 11:20Z to the last commit at 11:41Z), of which the 20 runs took about 8 min and `make verify` 216.88 s
- **Completed:** 2026-10-15
- **Tasks:** 3 (Task 1 a tracer, Tasks 2 and 3 auto)
- **Files modified:** 38 under this plan (4 source, doc or record files changed, 2 debt items created, the rest logs and throwaway-arm diffs)

## Accomplishments

- **The mechanism, on the real app, before any edit (Task 1).** Three throwaway arms, 3 runs each, every log kept in `investigation/`:

| Arm | Result |
|---|---|
| 1, delayed (parked) STL route, old step | green 3 of 3 (`1 passed`) |
| 2, parked `/api/info` released after the old baseline, old step | red 3 of 3: `AssertionError: twin selectors: 1 request(s) sent by two pending picks` (`assert 279 == 278`) |
| 3, the same parked `/api/info`, new baseline | green 3 of 3 |

  The real app agreed with the stand-in on every arm, so the decision gate did not trip and no checkpoint was returned. SC2's wording ("a delayed STL route makes the old step red") does not hold: `app.js` issues the STL request only after the `/api/info` response (`app.js:262-272`), so the info response is the lever. Stated plainly in the plan, in `26-03-arms.md`, in the code comment, in the retired item and in `bench/RESULTS.md`.
- **The fix (Task 2, `6ff1269`).** `DEBOUNCE_SETTLE_MS = 1_000` at module level; the twin step first asserts `/api/info` answers 200 for the link (the page sends no STL otherwise), waits for `/api/model.stl` around `goto` (`BUILD_WAIT_MS`), settles, takes the baseline, and settles again before the zero-request assertion. `_follow_link`'s wait carries `timeout=BUILD_WAIT_MS`. `_wait_until_parked` is byte-identical to `v0.5`; `git diff --exit-code v0.5 -- src/ tests/regression/` exits 0.
- **The CX-05 control.** After the two picks a throwaway patch dispatches a stray bubbling `input` event. The old assert-at-once step passes (`1 passed in 22.66s`, the vacuous pass); the settled step is red, and the stray `/api/info` request event arrived **354 ms** after the dispatch (`CX05-STRAY-INFO-MS 354`, one run), which the constant's comment records.
- **20 of 20 green (Task 3, `37ffdf3`).** `make test PYTEST_ARGS="tests/test_browser.py tests/test_browser_pins.py --no-cov -q"`, sequential, no early stop, no retry: `5 passed` and exit 0 in each of 20 runs (22.22 s to 24.90 s), effective `-n 8`, load 3.6 to 6.8 on the one-minute figure. Recorded in `bench/RESULTS.md` `### Twin selectors (26-03)` (73 lines added, 0 deleted against `v0.5`) with the caveat that the count alone does not separate the fix from a fast host.
- **The gate:** `make verify`, exit 0, `1320 passed in 216.88s (0:03:36)`, `TOTAL 1358 25 386 13 97.82%`, `Required test coverage of 96.0% reached` (`26-03-verify.log`).

## Task Commits

1. **Task 1: the old step against the real app** - no commit, by the plan's design; the arm diffs, logs and `26-03-arms.md` are committed with Task 2.
2. **Task 2: baseline after the link's own STL request, settle past the debounce, bound `_follow_link`, CX-05 control, retire the item, file the carry item** - `6ff1269` (fix)
3. **Task 3: the record and the 20 runs** - `37ffdf3` (docs); **IN-04b filed** - `6d3702c` (docs(debt))

`commits: 3` is measured from the ledger base `f7eeb70`.

**Plan metadata:** the docs commit that carries this SUMMARY (below).

## Files Created/Modified

- `tests/test_browser.py` - `DEBOUNCE_SETTLE_MS`, the twin step's precheck, STL-request wait, two settles; `_follow_link`'s bounded wait
- `bench/RESULTS.md` - `### Twin selectors (26-03)`, appended
- `docs/tech_debt/resolved/2026-10-15-twin-selectors-step-reds-main.md` - the retired must item (moved from `active/`), Resolution in "Proven in this commit" / "Not proven by this commit" form
- `docs/tech_debt/active/2026-10-15-twin-selectors-fix-awaits-the-post-merge-main-read.md` - D-05's post-merge `main` read, with trigger and commands
- `docs/tech_debt/active/2026-10-15-wait-until-parked-spins-without-a-pause.md` - 21 IN-04b, nice
- `docs/tech_debt/INDEX.md` - twin row moved to Resolved, two Active rows added
- `.planning/phases/26-gate-fails-with-a-cause/investigation/26-03-*` - arm and control diffs, 9 arm logs, 2 control logs, 20 repeat logs, the verify log, `26-03-arms.md`

## Decisions Made

- Corrected SC2's lever on the record rather than building the fix around the roadmap's wording: the plan's evidence-conflict paragraph said Task 1 would measure it, and it did.
- Kept the CX-05 control honest: it reads `2 request(s)`, not `1`, and was not reshaped to match the plan's quoted text.
- The commit trailer follows the session's attribution (`Claude Sonnet 5.5`), not the plan's `Claude Opus 5.5` text, as in 26-01 and 26-02.

## Deviations from Plan

### Plan text, not behaviour

**1. [Rule 1 - Expectation in the plan] The CX-05 control's red reads `2 request(s)`, not `1`**
- **Found during:** Task 2 step 4
- **Issue:** the plan's acceptance criterion says `D/26-03-cx05-new.log` contains `1 request(s) sent by two pending picks`. The stray `scheduleUpdate()` sends `/api/info`, and after that response `/api/model.stl` (aborted by the step's route), and both are recorded in `seen`, so the count is 2. The assertion that went red is the same one, and the old step still passes; only the number differs.
- **Fix:** none to the code; the control was run once as written and the log kept as is. The count is explained in `bench/RESULTS.md` and here. That one acceptance line, read literally, does not hold; the intent (old green, settled step red on this assertion) does.
- **Files modified:** none
- **Commit:** n/a

**Total deviations:** 1 (a plan-text expectation, no code change). **Impact:** none on the fix or the proof.

## Issues Encountered

None. The `ruff format --check` run on `tests/test_browser.py` reports pre-existing differences in lines this plan did not touch (the gate runs `ruff check`, which passes); not fixed, out of scope.

## Debt and ideas filed

- Filed: `docs/tech_debt/active/2026-10-15-twin-selectors-fix-awaits-the-post-merge-main-read.md` (must, D-05's post-merge read; carried because no task inside the phase can perform it)
- Filed: `docs/tech_debt/active/2026-10-15-wait-until-parked-spins-without-a-pause.md` (nice, 21 IN-04b)
- Retired: `2026-10-15-twin-selectors-step-reds-main` (must), moved to `docs/tech_debt/resolved/` in `6ff1269`, with what it does not yet prove stated

## Known Stubs

None.

## Threat Flags

None. T-26-06 (route interception leaking to other steps) mitigated: every route is on `twins_page`, its own context, closed in `finally`; each throwaway arm reverted with `git apply -R` and the tree checked clean. T-26-07 (a fix landed on an unproved mechanism) mitigated: the arms were recorded before the first edit of the step. T-26-SC accepted, no package installed.

## User Setup Required

None.

## Next Phase Readiness

- 26-07 reads the draft phase PR's run of the twin step (supporting only); after `make pr.land`, the carry item's commands read the first `main` run.
- Phase 28's info-finding triage can pick up IN-04b.

## Self-Check: PASSED

- FOUND: `tests/test_browser.py` (`DEBOUNCE_SETTLE_MS = 1_000`, two settles, STL wait before the baseline, `_follow_link` bounded), `bench/RESULTS.md` (one `### Twin selectors (26-03)`, 0 deleted lines against `v0.5`), both new debt items, the retired item under `resolved/` and absent from `active/`, `26-03-arms.md`, all 20 `26-03-repeat-*.log`
- FOUND: commits `6ff1269`, `37ffdf3`, `6d3702c` (ancestors of HEAD); `commits: 3` measured from the ledger base `f7eeb70`
- Acceptance re-run: arms 3 x 3 as predicted, `5 passed`, `_wait_until_parked` region equal to `v0.5`, `git diff --exit-code v0.5 -- src/ tests/regression/` exits 0, `20 of 20` in the record equals the logs' count; one acceptance line (the control's `1 request(s)`) differs and is recorded above

---
*Phase: 26-gate-fails-with-a-cause*
*Completed: 2026-10-15*
