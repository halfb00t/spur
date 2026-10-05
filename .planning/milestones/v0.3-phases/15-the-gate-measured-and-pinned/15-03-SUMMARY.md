---
phase: 15-the-gate-measured-and-pinned
plan: 03
subsystem: testing
tags: [make-verify, bench, profile-checkpoint, xdist, coverage, gate-decision]

requires:
  - phase: 15-the-gate-measured-and-pinned
    provides: "15-01's profile and sweep (K = 8), 15-02's D-05 verdict, D-12 cost row, coverage floor and C0"
provides:
  - "bench/RESULTS.md ### Heaviest contributors (4 files, 95.0 % of pytest's seconds, each with what it proves) and ### Proposed cuts (15 priced rows)"
  - "the D-01 checkpoint's answer, recorded verbatim in 15-CONTEXT.md (dated addendum under D-01) and bench/RESULTS.md ### Gate decision: bar 66 s, N = 8, no cut, Before = 244.59 s"
affects: [15-04, 15-05, 15-06]

actuals:
  tokens: 4950
  tasks: 3
  commits: 2
plan_head_before: 4b798ac941e920511d0ce505e37848d81ca14275
plan_head_after: df607f9566ec136c46fbf03dc29c7caea53286b4

tech-stack:
  added: []
  patterns:
    - "a human decision is written verbatim in the planning record and the measurement record in one commit, and the plan's verify checks the two copies match"

key-files:
  created: []
  modified:
    - bench/RESULTS.md
    - .planning/phases/15-the-gate-measured-and-pinned/15-CONTEXT.md

key-decisions:
  - "D-01 checkpoint answer: knee-headroom N=8 bar=66 cuts=none before=244.59 (bar = largest of B1-B3, 65.83 s, rounded up to the next whole second, read as mean(B) of the -n 8 --cov gate)"
  - "Every one of the 15 proposed cuts refused by name; 15-04 applies none and touches nothing in tests/"
  - "15-04's Before row is the serial --cov run C0 (244.59 s), not the no-coverage profile (224.28 s)"

requirements-completed: [REQ-verify-profiled, REQ-verify-at-the-bar]

coverage:
  - id: D1
    description: "Heaviest contributors named with seconds, share, items and what each proves (4 files at 5 % or more of pytest's seconds), and every proposed cut priced by measured serial seconds with its proof-value cost, into bench/RESULTS.md"
    requirement: REQ-verify-profiled
    verification:
      - kind: other
        ref: "Task 1 recomputed check (mean share from the P1/P2 seconds columns; the plan's own regex parses 0 files, see deviation 2) -> 'contributors and cuts ok', 15 rows"
        status: pass
    human_judgment: true
    rationale: "Whether each 'what it proves' cell and each proof-value cost is accurate and fair to the test is a reading of test bodies and Lxx records that no assertion covers"
  - id: D2
    description: "The D-01 checkpoint ran with the committed record in front of the human; nothing was written or applied before the answer"
    requirement: REQ-verify-at-the-bar
    verification:
      - kind: other
        ref: "Task 2 automated check before the answer: no '(profile checkpoint, 15-03' in 15-CONTEXT.md; git diff --quiet HEAD -- Makefile pyproject.toml tests src exit 0"
        status: pass
    human_judgment: false
  - id: D3
    description: "The human's answer verbatim in 15-CONTEXT.md under D-01 and in RESULTS ### Gate decision, with the bar in seconds, N, every cut ruled on by name and the Before row, in one commit"
    requirement: REQ-verify-at-the-bar
    verification:
      - kind: other
        ref: "Task 3 automated checks -> 'decision recorded: knee-headroom N=8 bar=66 cuts=none before=244.59' and 'decision committed'"
        status: pass
    human_judgment: false
  - id: D4
    description: "src/, tests/, Makefile and pyproject.toml unchanged by this plan"
    requirement: REQ-verify-at-the-bar
    verification:
      - kind: other
        ref: "git diff --quiet 4b798ac HEAD -- Makefile pyproject.toml tests src -> exit 0"
        status: pass
    human_judgment: false

duration: 22min
completed: 2026-10-04
status: complete
---

# Phase 15 Plan 03: The Profile Checkpoint Summary

**The gate's four heaviest test files named and fifteen cuts priced in measured serial seconds; the human set the bar at 66 s for `-n 8 --cov`, refused every cut and fixed 15-04's Before row at the serial `--cov` run C0, 244.59 s.**

## Performance

- **Duration:** 22 min of active work (the first executor 04:37Z-04:53Z, this one about 05:21Z-05:27Z); the checkpoint sat with the human for about 28 min between them and is not folded into that figure. Elapsed wall time start to finish: about 50 min.
- **Started:** 2026-10-04T04:37:00Z (approximate, from the first executor's start)
- **Completed:** 2026-10-04T05:27:00Z
- **Tasks:** 3 (task 2 is the human checkpoint)
- **Files modified:** 2

## Accomplishments

- `### Heaviest contributors` in `bench/RESULTS.md`: the four files at 5 % or more of pytest's seconds over P1 and P2, together 95.0 %: `tests/test_model.py` (201 items, 73.7 %, L24, L26-L31, L33), `tests/test_pool.py` (16, 8.4 %, L17/L18), `tests/regression/test_pre_v0_2.py` (85, 7.8 %, L05/L26) and `tests/test_api.py` (54, 5.0 %, just over the line). `tests/test_cli.py` (4.5 %) is under the rule and left out.
- `### Proposed cuts`: 15 rows (3 `sample` rows in `tests/test_model.py`, `skip` for the pre-v0.2 solid replay (17.30 s) and for two `tests/test_pool.py` process tests, 6 `remove` rows in `tests/test_api.py`, 2 `dedup` rows), each priced by the serial seconds P1 and P2 already printed, with what it proves and what losing it costs in proof. All 71 items out at once still leave coverage at 96.40 %, 0.40 over the 96.00 trip point (scratch run U1). None was recommended.
- The D-01 answer, from the human: `knee-headroom N=8 bar=66 cuts=none before=244.59`. Recorded in both places (below).

## The decision (human's answer, verbatim)

> knee-headroom N=8 bar=66 cuts=none before=244.59

Option id `knee-headroom`. Four consequences, written into both records:

1. **Bar: 66 s.** The largest of B1-B3 (65.83 s) rounded up to the next whole second, read in 15-04 as mean(B) of the `-n 8 --cov` gate by the recipe in `bench/RESULTS.md` ### Method (alternating with A, load recorded, a miss recorded and sent to the human, never re-run). The six D-05/D-12 runs read mean(B) 64.12 s, spread 3.33 s.
2. **N = 8**, the apparent knee K, so D-05's six green runs at N = 8 stand and 15-04 runs no further tolerance runs. CI runs `-n 4` on its 4-vCPU runner (Open Question 4).
3. **Cuts: none.** Every row refused by name: `tier2-round-bore`, `selector-cutout-no-recess`, `selector-bottom-recess`, `pre-v0.2-solids`, `pool-same-slot-refusal`, `pool-wedged-build`, `api-honeycomb-link`, `api-spoke-link`, `api-tip-chamfer-link`, `api-gzip-after-identity`, `api-two-request-ids`, `api-small-gear-recess`, `api-repeat-download`, `dedup-g4-regression`, `dedup-g4-g5`.
4. **Before row = C0**, the serial `--cov` run, 244.59 s (15-02's item 3), not the no-`--cov` serial profile's 224.28 s.

## Task Commits

1. **Task 1: Name the heaviest tests and price every proposed cut** - `0a74eed` (docs)
2. **Task 2: The D-01 checkpoint** - no commit; answered by the human as above
3. **Task 3: Write the answer into CONTEXT and RESULTS' Gate decision** - `df607f9` (docs)

**Plan metadata:** the closing `.planning/` commit (`docs(15-03): summarise the profile checkpoint`)

## Files Created/Modified

- `bench/RESULTS.md` - `### Heaviest contributors`, `### Proposed cuts` (Task 1); `### Gate decision` (Task 3)
- `.planning/phases/15-the-gate-measured-and-pinned/15-CONTEXT.md` - dated addendum under D-01, `(profile checkpoint, 15-03; the human's answer)`

## Decisions Made

- The D-01 checkpoint's answer above. The recommendation in the checkpoint was `knee-headroom` with no cuts, and the human took it.
- No new Lxx: L34 is 15-06's.

## Deviations from Plan

### Instructed and plan-defect deviations

**1. [Orchestrator instruction] Task 1's pricing source**
- **Found during:** Task 1
- **Issue:** the plan called for one separate serial `--durations=0` pricing run over the heaviest files. P1 and P2 had already printed every test phase's duration.
- **Fix:** priced from P1 and P2's own lines (`make verify PYTEST_ARGS="--durations=0 --durations-min=0"`, loads 6.53 and 9.09, HEAD `862a807`; `src/`, `tests/` and `requirements.txt` identical to `4b798ac`). The method line in `### Proposed cuts` says so, so no separate pricing run's seconds exist and none are mixed in.
- **Committed in:** `0a74eed`

**2. [Plan defect] Task 1's verify regex**
- **Found during:** Task 1
- **Issue:** the check expects one numeric share column; 15-01's per-file table prints `74.1 / 73.3`, so the regex parses 0 files and fails on a correct table.
- **Fix:** an equivalent check recomputing each file's mean share from the P1 and P2 seconds columns was run instead: contributors and cuts ok, 15 rows.
- **Files modified:** none

**3. [Rule 2 - extra measurement] Scratch run U1 for the 96.00 trip point**
- **Found during:** Task 1
- **Issue:** 15-02 asked that each cut be checked against the coverage floor; no run showed what the worst case reads.
- **Fix:** one `make test PYTEST_ARGS="-n 8 -q --deselect=..."` run with all 71 cut items deselected: 856 passed in 53.67 s, wall 53.91 s, TOTAL 96.40 %, HEAD `4b798ac`, load 1.01. Recorded in `### Proposed cuts`; nothing committed from the run; it is a coverage reading, not a measure of what any cut saves.
- **Committed in:** `0a74eed` (the record of it)

---

**Total deviations:** 3 (1 instructed, 1 plan defect, 1 extra measurement)
**Impact on plan:** none on the outcome; the record is the same shape the plan asked for.

## Issues Encountered

None. Both commits ran the pre-commit hook (`make verify`, serial with coverage) to a pass with plain `git commit`.

## Known Stubs

None (records only).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

For 15-04, from the answer above:

- Insert `-n 8` into the `make test` recipe **after** `--cov --cov-report=term` (the recipe is `pytest --cov --cov-report=term $(PYTEST_ARGS)`; do not separate `--cov` from `--cov-report=term`). N = 8; CI gets `-n 4` (Open Question 4: a bare literal when N <= 4, else min(N, online CPUs)).
- The bar is 66 s, read as mean(B) of two B runs alternating with two A runs by the recipe in `### Method`; a miss is recorded and goes to the human, never re-run.
- Before row: C0, 244.59 s serial `--cov`. Say in `### Before and after` that it is that and not the 224.28 s no-`--cov` profile.
- Apply no cut; touch nothing in `tests/`. N equals K, so no extra D-05 tolerance runs.
- 15-04 also owns `.pre-commit-config.yaml:6`. 15-06 owns the four further "~11 s" prose sites: `README.md:282`, `docs/HOW_TO_DEVELOP.md:21`, `docs/architecture/packaging.md:41`, and lines 8 and 15 of `docs/tech_debt/active/2026-09-25-gsd-commit-timeout-kills-cold-verify-hook.md`.
- 15-02's four flagged items: the lost-worker-flush debt file exists (`docs/tech_debt/active/2026-10-04-worker-coverage-flush-is-sometimes-lost.md`); the cuts against 96.00 are checked (U1, 96.40 %) and moot; the Before row is answered (244.59); the Makefile recipe is as above.
- Carried decisions, cited not re-decided: the D-09/D-10 corrections, Open Question 2 (config-only `fail_under = 96`), Open Question 3 (no `bench/` script).

## Self-Check: PASSED

- Files FOUND: `bench/RESULTS.md` (with `### Heaviest contributors`, `### Proposed cuts`, `### Gate decision`), `.planning/phases/15-the-gate-measured-and-pinned/15-CONTEXT.md` (with the D-01 addendum)
- Commits FOUND: `0a74eed`, `df607f9`; `git rev-list --count 4b798ac..HEAD` was 2 before this SUMMARY
- Re-run: Task 3 checks -> `decision recorded: knee-headroom N=8 bar=66 cuts=none before=244.59`, `decision committed`; `git diff --quiet 4b798ac HEAD -- Makefile pyproject.toml tests src` exits 0

---
*Phase: 15-the-gate-measured-and-pinned*
*Completed: 2026-10-04*
