---
phase: 33-interfaces-and-parity
plan: 09
subsystem: testing
tags: [bench, latency, contention, gate-cost, close-checks, decision-log, shaft]

requires:
  - phase: 33-interfaces-and-parity
    provides: "33-04 /api/shaft/model.{stl,step}; 33-01 gate baseline and decision C1; 33-03 the WR-02 fixing commit 69c1aa3; 33-08 the page agrees"
provides:
  - "bench.latency scenarios `shaft` and `shaft-identical` (path= keyword on _fetch and run_composed), pinned in tests/test_bench.py"
  - "bench/RESULTS.md: the heaviest shaft under ten concurrent requests, the gate delta against 33-01, the twelve phase close checks"
  - "the shaft contention debt item retired (3ee9a0a)"
  - "L49 closing paragraph `What Phase 33 closed on`"
  - "the C1 reading of SC4 beside ROADMAP criterion 4 and REQ-wr02-fixed"
affects: [phase-33-verification, verify-work]

actuals:
  tokens: 5765   # chars/4 over the added lines of bench/latency.py, tests/test_bench.py, bench/RESULTS.md, docs/ and the ROADMAP and REQUIREMENTS notes (logs excluded)
  tasks: 3
  commits: 5
plan_head_before: 439c65a06bbc93a023eb9043b3a4ea8cf2058336
plan_head_after: 5c256c1c08e038202c12344f159dc3bd4e83ef08

tech-stack:
  added: []
  patterns:
    - "A route-specific contention run reuses the gear's firing rule through a path= keyword whose default reproduces every gear run"

key-files:
  created:
    - .planning/phases/33-interfaces-and-parity/investigation/33-09-serve.log
    - .planning/phases/33-interfaces-and-parity/investigation/33-09-shaft.log
    - .planning/phases/33-interfaces-and-parity/investigation/33-09-shaft-identical.log
    - .planning/phases/33-interfaces-and-parity/investigation/33-09-verify.log
    - .planning/phases/33-interfaces-and-parity/investigation/33-09-verify-meta.log
    - .planning/phases/33-interfaces-and-parity/investigation/33-09-close-checks.log
  modified:
    - bench/latency.py
    - tests/test_bench.py
    - bench/RESULTS.md
    - docs/architecture/decision_log.md
    - docs/tech_debt/INDEX.md
    - docs/tech_debt/resolved/2026-10-27-shaft-contention-row.md
    - .planning/ROADMAP.md
    - .planning/REQUIREMENTS.md

key-decisions:
  - "The two shaft scenarios stay out of DEFAULT_SCENARIOS and out of the bar's baseline/2.00x lines (they time out and replace workers by design, as composed and identical do)"
  - "Each contention run gets its own fresh server (run_composed's rule); the two server logs share one file, a separator line between them"

requirements-completed: [REQ-shaft-api, REQ-gate-cost-recorded, REQ-shaft-web, REQ-shaft-cli, REQ-shaft-parity, REQ-designation-input, REQ-wr02-fixed]

coverage:
  - id: D1
    description: "bench.latency gains the `shaft` and `shaft-identical` scenarios and a path keyword on _fetch/run_composed; the default run and DEFAULT_SCENARIOS are unchanged"
    requirement: "REQ-gate-cost-recorded"
    verification:
      - kind: unit
        ref: "tests/test_bench.py#test_the_shaft_scenario_fires_the_heaviest_shaft_first_then_nine_distinct_neighbours"
        status: pass
      - kind: unit
        ref: "tests/test_bench.py#test_the_shaft_identical_scenario_fires_the_heaviest_shaft_ten_times"
        status: pass
      - kind: unit
        ref: "tests/test_bench.py#test_fetch_requests_the_path_it_is_given_and_defaults_to_the_gears"
        status: pass
    human_judgment: false
  - id: D2
    description: "The heaviest shaft measured under ten concurrent requests through the real server: 4 of 10 answered 200 and 6 refused 503 busy in each run, no timeout, pool_broken or 500, slowest 200 10.16 s of 30 s; the contention item retired"
    requirement: "REQ-gate-cost-recorded"
    verification:
      - kind: other
        ref: "33-09-shaft.log and 33-09-shaft-identical.log: ten outcome rows each, grep for 503 timeout|503 pool_broken|| 500 | counts 0"
        status: pass
    human_judgment: true
    rationale: "Whether a 10.16 s slowest build under contention is an acceptable margin to the 30 s timeout is a reading for the human; the plan's stop condition (any timeout, pool_broken or 500) did not fire"
  - id: D3
    description: "The gate delta recorded against 33-01 (2778 passed in 241.55 s, real 242.47, 134 tests and 12.38 s above the baseline, 58.45 s under the 300 s bar)"
    requirement: "REQ-gate-cost-recorded"
    verification:
      - kind: other
        ref: "33-09-verify.log: make verify rc 0, `2778 passed in 241.55s (0:04:01)`"
        status: pass
    human_judgment: false
  - id: D4
    description: "Twelve phase close checks all PASS and are logged; L49 closed with `What Phase 33 closed on`"
    verification:
      - kind: other
        ref: "33-09-close-checks.log: 12 PASS, 0 FAIL"
        status: pass
    human_judgment: false
  - id: D5
    description: "The C1 reading of SC4 recorded beside ROADMAP criterion 4 and REQ-wr02-fixed, naming 69c1aa3 and close check 8, the approved words unchanged"
    requirement: "REQ-wr02-fixed"
    verification:
      - kind: other
        ref: "grep -c 'Reading (C1, 33-01 Decision result; L49):' .planning/ROADMAP.md .planning/REQUIREMENTS.md prints 1 and 1; git cat-file -e 69c1aa3 passes; 5 and 4 added lines, 0 deleted"
        status: pass
    human_judgment: true
    rationale: "Whether the phase verifier accepts a switch that edits neither function as meeting the criterion's words is the human's reading, which 33-01's C1 already recorded"

duration: 14min
completed: 2026-10-27
status: complete
---

# Phase 33 Plan 09: Phase close Summary

**The heaviest DIN 5480 shaft held ten concurrent requests through the real server with no timeout (slowest 200 10.16 s of 30 s), the phase's gate cost 2778 tests in 241.55 s against 2644 in 229.17 s, and twelve close checks passed.**

## Performance

- **Duration:** 14 min
- **Started:** about 2026-10-27T18:08:30Z (not recorded at spawn; the previous plan's last commit is 18:08:12Z)
- **Completed:** 2026-10-27T18:22Z
- **Tasks:** 3
- **Files modified:** 8 tracked files, 6 new logs

## Accomplishments

- **Contention (D-19).** `bench.latency shaft` (row 5 of `bench/sweeps/shaft.json` first, then `shank_length` 499 to 491) and `shaft-identical` (row 5 ten times), each on a fresh `spur serve` at the shipping defaults (2 workers, 4 queued builds, 30 s). Both runs: 4 of 10 admitted and answered 200, 6 refused 503 `busy`, no `503 timeout`, no `503 pool_broken`, no 500, `workers_replaced` 0 to 0. `shaft`: 200s of 3.67, 5.75, 10.16 and 7.95 s (slowest 10.16 s, 34 % of 30 s, 4.6 times 32-05's 2.23 s alone); `shaft-identical`: 3.67 to 3.75 s each. `/api/health` p95 0.5 ms idle and 1.5 ms under load in both. One run per scenario at loads 5.79 to 8.38 and 6.97 to 6.60, so a single reading, not a distribution.
- **Gate delta (criterion 5).** `make verify`: `2778 passed in 241.55s (0:04:01)`, `real 242.47`, rc 0, load 5.30 to 7.21, coverage 98.48 %. Against 33-01's `2644 passed in 229.17s`, `real 230.70`, load 4.62 to 7.15: +134 tests, +12.38 s (+5.40 %) pytest, +11.77 s (+5.10 %) real, inside Phase 25's 8 % spread (18.33 s), so no speed claim. 58.45 s under L43's 300 s bar. The browser test's call time went 39.22 s to 61.24 s; not apportioned.
- **Close checks.** All twelve PASS in `33-09-close-checks.log`: `gear.unchanged`; `tests/regression/` and `ci.yml` equal to `v0.6`; the browser test passed with 44 golden records; `verify.fast` real 13.57 s (`2311 passed in 12.68s`); `Contracts: 10 kept, 0 broken.`; `import spur.cli` loads nothing web or kernel; frozen files equal to `6800769`; `refuse()` and `gearQuery()` byte-identical to `6800769` (C1); seam tests 8 passed; `no-fake-done`; the four debt items resolved with resolving shas (`3e1eded`, `49021f5`, `69c1aa3`, `3ee9a0a`); `decision_log.md` appended only, `## L49` last.
- **L49 closed** with the paragraph `What Phase 33 closed on`.
- **SC4 reading.** `Reading (C1, 33-01 Decision result; L49):` placed under ROADMAP Phase 33 criterion 4 and under the REQ-wr02-fixed bullet, naming `69c1aa3` (33-03's fixing commit) and close check 8; the criterion's and the requirement's own words and the requirement's unticked checkbox are unchanged.

## Task Commits

1. **Task 1: Tracer, ten concurrent heaviest shafts, contention item retired**
   - `2f1e230` feat(bench): fire ten heaviest shafts at /api/shaft/model.stl (tests written first and seen to fail on the missing import, then green)
   - `3ee9a0a` docs(bench): the heaviest shaft under ten concurrent requests (D-19), the fix commit naming the item's subject
   - `603031a` docs(33-09): record the sha that retired the shaft contention debt item
2. **Task 2: Gate delta, close checks, L49 closed** - `0f20d90` docs(bench): Phase 33's gate delta and close checks
3. **Task 3: SC4's C1 reading** - `5c256c1` docs(roadmap): record SC4's C1 reading beside the criterion and REQ-wr02-fixed

**Plan metadata:** the `docs(33-09): complete ...` commit that adds this file.

## Files Created/Modified

- `bench/latency.py` - `path=` on `_fetch` and `run_composed`; `SHAFT_SWEEP`, `SHAFT_HEAVIEST_ROW`, `_shaft_rows()`, `_shaft_identical_rows()`, `scenario_shaft`, `scenario_shaft_identical`
- `tests/test_bench.py` - the three new pins, the `_SCENARIOS` pin, the report test extended to the shaft names
- `bench/RESULTS.md` - the three 33-09 sections
- `docs/architecture/decision_log.md` - L49 closing paragraph
- `docs/tech_debt/INDEX.md`, `docs/tech_debt/resolved/2026-10-27-shaft-contention-row.md` - the item retired
- `.planning/ROADMAP.md`, `.planning/REQUIREMENTS.md` - the C1 reading
- `.planning/phases/33-interfaces-and-parity/investigation/33-09-*.log` - serve, shaft, shaft-identical, verify, verify-meta, close-checks

## Decisions Made

The two shaft scenarios are outside `DEFAULT_SCENARIOS` and outside the report's baseline and 2.00x lines, for the reason `composed` and `identical` are. Otherwise the plan was followed as written.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `_report_markdown` would have printed the gear's recorded baseline and the 2.00x bar under the shaft headings**
- **Found during:** Task 1 (reading `_report_markdown`'s `has_bar` rule before adding the scenarios)
- **Issue:** `has_bar` excluded only `composed` and `identical`; a `shaft` or `shaft-identical` report would have carried a baseline measured for a different scenario and a pass bar that RESULTS reads neither run against.
- **Fix:** the two shaft names added to the exclusion, comments updated, and the existing report test extended to the two names.
- **Files modified:** bench/latency.py, tests/test_bench.py
- **Verification:** `pytest --no-cov -n0 -q tests/test_bench.py` 54 passed; the shaft logs print no baseline or bar line.
- **Committed in:** 2f1e230

**2. [Rule 3 - Blocking] First commit attempt failed the pre-commit `verify.fast` on two comment lines over 100 characters**
- **Found during:** Task 1 commit
- **Fix:** the two comments rewrapped; commit retried once and passed.
- **Files modified:** bench/latency.py
- **Committed in:** 2f1e230

---

**Total deviations:** 2 auto-fixed (1 bug, 1 blocking)
**Impact on plan:** none on the measurements; the first keeps the shaft reports honest.

## Issues Encountered

- The plan commit ledger (`gsd-plan-head-before-33-09`) was written after the first commit from `2f1e230^`, which is the head before the plan's first commit, so the measured count is unaffected.
- The two servers' logs share `33-09-serve.log` (the plan names one file); a `--- run 2 ---` line separates them. The file is 4.4 MB, most of it the harness's `/api/health` access lines.
- No gate run was red or hung; no figure was dropped. Gate timings seen this phase are in `### The gate delta (33-09)` with the load beside each.

## Known Stubs

None.

## Threat Flags

None. The bench client is a local measurement harness; no new network surface in the product.

## Debt and ideas

No debt or idea item was filed. One was retired: `docs/tech_debt/resolved/2026-10-27-shaft-contention-row.md` (`3ee9a0a`).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Phase 33 has all nine plans' summaries once this is committed; ready for phase verification. Nothing blocks it: the contention run did not trip the stop rule, the gate is 57.53 s (real) under L43's bar, and SC4 reads as met beside the criterion.

## Self-Check: PASSED

All created files exist, the five task commits are ancestors of HEAD, the contention item is absent from `active/`, and `git status --porcelain -- src tests bench` prints nothing.

---
*Phase: 33-interfaces-and-parity*
*Completed: 2026-10-27*
