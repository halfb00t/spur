---
phase: 26-gate-fails-with-a-cause
plan: 04
subsystem: testing
tags: [resource-tracker, flake, gc, pytest, tech-debt, forced-gc]

requires:
  - phase: 26-gate-fails-with-a-cause
    provides: plans 26-01 to 26-03, the Phase 26 section of bench/RESULTS.md and the investigation/ directory
provides:
  - "tests/test_pool.py: autouse fixture _collect_cycles_outside_the_resource_tracker_lock, three del manager, and the forced-GC gate test with its python -c script"
  - "bench/RESULTS.md: the pre-registered rule, the reproduction readings, the forced-GC table and the 10 + 10 table"
  - "the resource-tracker flake must item retired, quoting both tables, as 'located and fixed from a reproduction'"
affects: [26-07]

actuals:
  tokens: 6000    # chars/4 over the authored lines (test diff, RESULTS sections, the item's Resolution, accept.sh); logs and frozen copies excluded
  tasks: 3
  commits: 2
plan_head_before: 653fe133e538416bb1ca49c510b4389340d5fa53
plan_head_after: 21b46f817cef52402aa9280b5890a7b23c00f6d6
commits: 2

tech-stack:
  added: []
  patterns:
    - "A race is proved by forcing the window (a gc.collect() inside the tracker's lock, in a fresh python -c interpreter), not by waiting for the natural rate"
    - "An acceptance rule is committed alone, its arms pinned by sha256, before the first run"

key-files:
  created:
    - .planning/phases/26-gate-fails-with-a-cause/investigation/26-04-accept.sh
    - .planning/phases/26-gate-fails-with-a-cause/investigation/26-04-repro.log
    - .planning/phases/26-gate-fails-with-a-cause/investigation/26-04-arm-B.diff
    - .planning/phases/26-gate-fails-with-a-cause/investigation/26-04-arm-C.diff
    - .planning/phases/26-gate-fails-with-a-cause/investigation/26-04-arm-before.test_pool.py.txt
    - .planning/phases/26-gate-fails-with-a-cause/investigation/26-04-arm-after.test_pool.py.txt
  modified:
    - tests/test_pool.py
    - bench/RESULTS.md
    - docs/tech_debt/INDEX.md
    - docs/tech_debt/resolved/2026-10-06-resource-tracker-flake-fails-the-gate.md

key-decisions:
  - "Path taken: HOLDS. The reproduction held on this host, so the fix (arms B + C) landed and the item was retired, not re-deferred"
  - "The 10 + 10 is recorded as consistent, not conclusive: the before arm did not reproduce the flake naturally either (0 of 10), so the table does not separate the arms; the forced-GC test is the proof"
  - "The fix commit trailer follows the session's attribution (Claude Sonnet 5.5), not the plan text, as in 26-01 to 26-03"

requirements-completed: [REQ-tracker-flake-fixed-from-repro]

coverage:
  - id: D1
    description: "STACK's stdlib reproduction and both controls re-run on this host before any fix"
    requirement: REQ-tracker-flake-fixed-from-repro
    verification:
      - kind: integration
        ref: ".planning/phases/26-gate-fails-with-a-cause/investigation/26-04-repro.log (stdout 5 in 5 of 5 runs; both controls 0 in 3 of 3)"
        status: pass
    human_judgment: false
  - id: D2
    description: "The forced-GC gate test is red 3 of 3 against the unfixed file (victim named, 'reentrantly' text, check_alive calls 94) and green 3 of 3 after the fix; arms B and C alone are each green 3 of 3"
    requirement: REQ-tracker-flake-fixed-from-repro
    verification:
      - kind: integration
        ref: "tests/test_pool.py::test_forced_gc_inside_the_resource_tracker_lock_finds_no_reentrant_cleanup; investigation/26-04-gate-{A,B,C,BC}-{1,2,3}.log"
        status: pass
    human_judgment: false
  - id: D3
    description: "The 10 + 10 interleaved acceptance run under a rule committed before run A1: 0 of 10 flake reds in each arm, no other red, order and arm hashes checked"
    requirement: REQ-tracker-flake-fixed-from-repro
    verification:
      - kind: integration
        ref: "investigation/26-04-accept-{A,B}-{1..10}.log; the Task 3 verify script (20 run-records in order, rule commit before A1)"
        status: pass
    human_judgment: false
  - id: D4
    description: "src/spur/pool.py, pyproject.toml, requirements.txt and tests/regression/ unchanged against v0.5; no shutdown call added to the test file"
    requirement: REQ-tracker-flake-fixed-from-repro
    verification:
      - kind: integration
        ref: "git diff --exit-code v0.5 -- src/spur/pool.py pyproject.toml requirements.txt tests/regression/ (exit 0)"
        status: pass
    human_judgment: false
  - id: D5
    description: "The must item retired in the fixing commit with a Resolution that says 'located and fixed from a reproduction', quotes both tables, and states what is not proven"
    requirement: REQ-tracker-flake-fixed-from-repro
    verification: []
    human_judgment: true
    rationale: "Wording and index bookkeeping; no test asserts it. The verifier reads the item and the RESULTS section."

duration: ~19min
completed: 2026-10-15
status: complete
---

# Phase 26 Plan 04: The resource-tracker flake, located and fixed from a reproduction Summary

**A `gc.collect()` forced inside `ResourceTracker`'s lock reproduces the flake on demand: red 3 of 3 against the unfixed `tests/test_pool.py`, green 3 of 3 after an autouse teardown-collect fixture plus `del manager` in the three producers; the 10 + 10 natural run read 0 of 10 flake reds in each arm, which is consistent, not conclusive.**

## Performance

- **Duration:** ~19 min wall (start 11:42Z, last commit about 12:01Z); the 20 acceptance runs took 5 min (13 to 15 s each), `make verify` 185.61 s
- **Completed:** 2026-10-15
- **Tasks:** 3 (Task 1 a tracer, Tasks 2 and 3 auto)
- **Files modified:** 4 source, record or debt files; the rest logs, frozen arms and diffs under `investigation/26-04-*` (41 files)

## Path taken: HOLDS

The pre-written threshold (stdlib script prints a non-zero count in all 5 runs with both controls at 0, AND the gate test red 3 of 3 against the unfixed file) was met on every part, so Tasks 2 and 3 ran and the item was retired. The re-defer path was not taken.

## Accomplishments

- **Reproduction re-run before any fix (D-03).** STACK's `rt_repro.py`: stdout `5` in 5 of 5 runs; control 1 (`gc.collect()` before the patch) `0` in 3 of 3; control 2 (no `ex.me = ex` cycle) `0` in 3 of 3 (`26-04-repro.log`). Until then every STACK figure was read, not measured.
- **The forced-GC gate test (D-02).** `test_forced_gc_inside_the_resource_tracker_lock_finds_no_reentrant_cleanup` runs the three producers then the victim in a fresh `python -c` interpreter with `_check_alive` wrapped to call `gc.collect()` under the tracker's lock, and asserts exit 0 and a call count above 0.

| Arm | Change | Forced-GC red (this host, 3 runs) | STACK |
|---|---|---|---|
| A | none | **3 of 3** | 3 of 3 |
| B | autouse fixture only | 0 of 3 | 0 of 3 |
| C | three `del manager` only | 0 of 3 | 0 of 3 |
| B + C | both (committed) | 0 of 3 | not run |

  The red text (`26-04-gate-A-1.log`): `FAILED tests/test_pool.py::test_a_closed_pool_never_builds_a_replacement_worker` (the victim), `ReentrantCallError: Reentrant call into the multiprocessing resource tracker`, `UserWarning: ResourceTracker called reentrantly for resource cleanup`, `1 failed, 3 passed in 10.11s`, `check_alive calls: 94` in all three.
- **Cost.** Alone 11.27 to 13.14 s (green runs, `-n0 --no-cov`); inside the gate 10.58 s (`--durations` block); the whole file 31 to 33 s at `-n0 --no-cov`. The file is in `HEAVY_TEST_FILES`, so none of it runs in the commit-time slice.
- **The rule, committed alone (`957539c`, 11:50:18Z) before run A1 (11:50:47Z).** Command, arms by sha256 (`d88ba80e...3b` before, `b56df869...5` after), order, cap, signature and reading.
- **The 10 + 10 (`26-04-accept.sh`, no retry, no drop).** 20 of 20 exit 0, `82 passed` each, `8 workers [82 items]` each, load 5.90 to 15.34; 0 of 10 flake reds before, 0 of 10 after, no other red, no killed run. pytest 9.1.1, pytest-xdist 3.8.0, pytest-cov 7.1.0, coverage 7.16.2. The before arm did not reproduce the flake either, so the table cannot separate the arms: **consistent, not conclusive** (0 of 10 by luck is 15 to 30 % at STACK's rate). The forced-GC test is the proof.
- **The fix (`21b46f8`).** `tests/test_pool.py` only: autouse fixture `_collect_cycles_outside_the_resource_tracker_lock` (`gc.collect()` after `yield`) and `del manager` after the last use in the three producers. No change to `src/spur/pool.py`, no warning filter, no rerun plugin, no explicit shutdown call, no dependency; `git diff --exit-code v0.5 -- src/spur/pool.py pyproject.toml requirements.txt tests/regression/` exits 0.
- **The item retired** in the fixing commit, `Resolution (2026-10-15)` opening "Located and fixed from a reproduction", with the mechanism, both tables, and what is not proven (no other path leaves semaphores to the cyclic GC; `ubuntu-latest` CI rate unread).
- **The gate:** `make verify PYTEST_ARGS="--durations=0 --durations-min=5.0"`, exit 0, `1321 passed in 185.61s (0:03:05)`, `TOTAL 1358 22 386 13 97.99%`, `Required test coverage of 96.0% reached` (`26-04-verify.log`).

## Task Commits

1. **Task 1: reproduce, write the gate test, see it red** - no commit, by the plan's design (red until the fix); logs committed with the fix.
2. **Task 2: fix B + C, freeze arms, pre-register the rule** - `957539c` (docs): the rule alone (`bench/RESULTS.md` only). The fix itself stayed uncommitted until Task 3, as planned.
3. **Task 3: the 10 + 10, readings, retire the item** - `21b46f8` (fix)

`commits: 2` is measured from the ledger base `653fe13`.

## Files Created/Modified

- `tests/test_pool.py` - imports `gc`, `re`, `subprocess`, `sys`, `Iterator`; the fixture; three `del manager`; `_FORCED_GC_IDS`, `_FORCED_GC`, the gate test (+111 lines)
- `bench/RESULTS.md` - `### The resource-tracker flake (26-04)`: `#### The rule (26-04)`, `#### Readings (26-04)` (0 deleted lines against `v0.5`)
- `docs/tech_debt/resolved/2026-10-06-resource-tracker-flake-fails-the-gate.md` - moved from `active/`, `Status: resolved`, Resolution added
- `docs/tech_debt/INDEX.md` - Active row removed, Resolved row added at the top
- `.planning/phases/26-gate-fails-with-a-cause/investigation/26-04-*` - repro log, 12 gate-test logs, arm diffs, frozen arms, `26-04-accept.sh`, 20 acceptance logs, tools and done logs, verify log

## Decisions Made

- Recorded the 10 + 10 as non-separating rather than as support for the fix, since the unfixed arm was also 0 of 10; the threshold and reading were pre-written in the rule and not reinterpreted.
- Left the fixture's own cost as "not re-measured here; the research read about 10 ms per test" rather than quote an estimate as a measurement.

## Deviations from Plan

### Plan text, not behaviour

**1. [Rule 1 - Expectation in the plan] `19 passed` is `21 passed`**
- **Found during:** Task 2 step 3
- **Issue:** the plan expects `tests/test_pool.py` to read `19 passed` (18 functions plus the gate test). The file has 19 test functions with the gate test, one parametrised three ways, so 21 collected items; 20 without the gate test.
- **Fix:** none to the code; the file reads `21 passed` (`-n0 --no-cov`, twice more at the end). Recorded in `bench/RESULTS.md`.
- **Files modified:** none
- **Commit:** n/a

**2. [Rule 3 - Blocking] `import re` added**
- **Found during:** Task 1 step 2
- **Issue:** the plan lists `subprocess` and `sys` as the new imports; the gate test parses `check_alive calls: (\d+)` with `re.search`, which needs `re`.
- **Fix:** `import re` added in the stdlib block. Files modified: `tests/test_pool.py`. Commit: `21b46f8`.

**3. [Rule 3 - Slip, repaired] First fix commit missed most of its files**
- **Found during:** Task 3 step 6
- **Issue:** a `git add` naming the already-moved `active/` path failed, the chain stopped, and the commit that ran next held only the moved item.
- **Fix:** staged the rest and amended that one local, unpushed commit (`git commit --amend --no-edit`); the final `21b46f8` carries the test, the record, the moved item, the INDEX row and the `26-04-*` files together, as the plan requires. No history was rewritten beyond that commit.
- **Commit:** `21b46f8`

**Total deviations:** 3 (one plan-text count, one added import, one commit-staging slip repaired). **Impact:** none on the fix or the proof.

## Issues Encountered

None beyond the deviations. The host was shared throughout (1-minute load 5.9 to 15.3 during the runs), recorded as a covariate in the table. `grep -n 'del manager' tests/test_pool.py` prints five lines: three statements (223, 611, 669) and two comment/docstring mentions.

## Debt and ideas filed

- Retired: `2026-10-06-resource-tracker-flake-fails-the-gate` (must), moved to `docs/tech_debt/resolved/` in `21b46f8`, with what it does not prove stated.
- Filed: none. The next `make verify` failure that prints the chain reopens the item with its whole log, as the Resolution says.

## Known Stubs

None.

## Threat Flags

None. T-26-08 mitigated (fixed argv list, no shell, `cwd` the repo root, env drops `PYTEST_ADDOPTS` and `PYTEST_ARGS`); T-26-09 mitigated (the `_check_alive` patch exists only in the `python -c` child); T-26-10 mitigated (red then green on record, the rule committed before its runs, `pool.py`, `pyproject.toml` and `requirements.txt` unchanged against `v0.5`); T-26-SC accepted, no package installed.

## User Setup Required

None.

## Next Phase Readiness

- 26-07 reads the draft phase PR's CI run (supporting only). The CI rate of this flake on `ubuntu-latest` is read from the next `make verify` failure, if any.

## Self-Check: PASSED

- FOUND: `tests/test_pool.py` (fixture `_collect_cycles_outside_the_resource_tracker_lock`, the gate test, three `del manager` statements), `bench/RESULTS.md` (`#### The rule (26-04)` and `#### Readings (26-04)`, 0 deleted lines against `v0.5`), the item under `resolved/` and absent from `active/`, all 20 `26-04-accept-*` logs with one `run-record` each
- FOUND: commits `957539c`, `21b46f8` (ancestors of HEAD); `commits: 2` measured from ledger base `653fe13`
- Acceptance re-run: the Task 1 verify (3 of 3 red), the Task 3 verify script (20 run-records in order, rule commit 11:50:18Z before A1 11:50:47Z), `git diff --exit-code v0.5 -- src/spur/pool.py pyproject.toml requirements.txt tests/regression/` exit 0, zero `shutdown(` additions, `Located and fixed from a reproduction` present, working `tests/test_pool.py` sha256 equals the rule's after-arm hash, `tests/test_pool.py` `21 passed`, `make verify` exit 0

---
*Phase: 26-gate-fails-with-a-cause*
*Completed: 2026-10-15*
