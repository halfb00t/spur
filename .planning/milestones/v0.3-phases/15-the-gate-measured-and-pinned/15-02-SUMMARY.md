---
phase: 15-the-gate-measured-and-pinned
plan: 02
subsystem: testing
tags: [coverage, pytest-cov, pytest-xdist, fail_under, make-verify, bench]

requires:
  - phase: 15-the-gate-measured-and-pinned
    provides: "plan 01's run recipe R1-R5, the apparent knee K = 8, pytest-cov and pytest-xdist in [dev]"
provides:
  - "coverage config that counts BuildPool's spawned-worker lines (concurrency multiprocessing + thread, parallel, sigterm), precision = 2, .coverage data files ignored"
  - "fail_under = 96 by D-10's rule (L = 96.99, S = 0.00), read from [tool.coverage.report] alone"
  - "make test runs pytest --cov --cov-report=term; partial runs need --no-cov"
  - "bench/RESULTS.md: Coverage baseline, Tolerance and coverage cost, Coverage floor, Red on the floor"
  - "D-05 verdict at N = 8 (adopted, 6 of 6 green) and D-12's cost row (3.51 s at -n 8) for 15-03's checkpoint"
affects: [15-03, 15-04, 15-05, 15-06]

actuals:
  tokens: 5400
  tasks: 3
  commits: 5
plan_head_before: b8b0effdfeae441d131ee8a5bcddf3da98a1c8a0
plan_head_after: 4fef83d716c5463cddbf2758cbe50a8cba8d6b9d

tech-stack:
  added: []
  patterns:
    - "a config literal cites the RESULTS table it came from, and the plan's verify recomputes it from the table's own totals"
    - "--cov-report=term right after --cov, so --cov's optional value cannot swallow a path in PYTEST_ARGS"

key-files:
  created:
    - docs/tech_debt/active/2026-10-04-worker-coverage-flush-is-sometimes-lost.md
  modified:
    - .gitignore
    - pyproject.toml
    - Makefile
    - bench/RESULTS.md
    - docs/tech_debt/INDEX.md
    - docs/tech_debt/resolved/2026-09-21-no-coverage-floor.md
    - .planning/REQUIREMENTS.md
    - .planning/ROADMAP.md
    - .planning/STATE.md

key-decisions:
  - "fail_under = 96: floor(L - max(0.25, S)) with L = 96.99 (serial C0, the lowest of four totals) and S = 0.00 (three -n 8 totals at 97.21)"
  - "xdist adopted at N = 8: six alternating runs, 927 passed each; no D-08 xdist_group needed, tests/ untouched"
  - "make test recipe is pytest --cov --cov-report=term $(PYTEST_ARGS), not the plan's bare --cov: a bare --cov swallows a leading path in PYTEST_ARGS as its coverage source and runs the whole suite"

requirements-completed: [REQ-coverage-floor, REQ-verify-profiled]

coverage:
  - id: D1
    description: "BuildPool's spawned-worker lines are counted: concurrency multiprocessing + thread, parallel, sigterm; tests/test_pool.py reads pool.py at 100.00 % serially and at -n 2"
    requirement: REQ-coverage-floor
    verification:
      - kind: other
        ref: "make test PYTEST_ARGS='tests/test_pool.py --cov --cov-report=term-missing -q --no-header [-n 2]' | grep pool.py row -> 54 0 6 0 100.00% (both, re-run at self-check)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Baseline C0 (96.99 %), six alternating runs at -n 8 (all 927 passed, B totals 97.21 x3), D-05 verdict adopted, coverage cost 3.51 s, and the floor line recorded in bench/RESULTS.md"
    requirement: REQ-coverage-floor
    verification:
      - kind: other
        ref: "Task 2 automated check (python recomputes L, S and F from the RESULTS tables) -> 'floor ok 96'"
        status: pass
    human_judgment: false
  - id: D3
    description: "fail_under = 96 and precision = 2 in [tool.coverage.report]; make test runs --cov with the floor read from config; a test_calc-only run fails the floor and the same with --no-cov exits 0; adjacency probe (96 passes, 95.99 fails)"
    requirement: REQ-coverage-floor
    verification:
      - kind: other
        ref: "Task 3 automated checks -> 'floor wired 96', make -n test count 1, 'partial-run rule ok'"
        status: pass
    human_judgment: false
  - id: D4
    description: "Red on the floor: a full run without tests/test_cli.py read 90.24 % against 96 and failed; recorded in RESULTS, tree untouched, nothing committed"
    requirement: REQ-coverage-floor
    verification:
      - kind: other
        ref: "make verify PYTEST_ARGS='-n 8 --ignore=tests/test_cli.py' (R1ed) -> ERROR: Coverage failure: total of 90.24 is less than fail-under=96.00; Task 3 check 'red run recorded' + 'tree untouched by the red run'"
        status: pass
    human_judgment: false
  - id: D5
    description: "The coverage-floor debt retired with its sha (2aadcea), pytest-cov sentence corrected, INDEX row moved; REQ-coverage-floor and ROADMAP SC3 say fail_under is where the floor is read and state the settled worker mechanism"
    requirement: REQ-coverage-floor
    verification:
      - kind: other
        ref: "Task 3 automated checks -> 'debt ok', 'Q2 sentences ok', 'D-20 ok'; roadmap milestone-scope identical before and after"
        status: pass
    human_judgment: false
  - id: D6
    description: "The Makefile recipe departs from the plan's literal text (--cov-report=term after --cov) to stop --cov swallowing a path in PYTEST_ARGS"
    verification: []
    human_judgment: true
    rationale: "A Rule 1 fix to a plan-specified recipe; whether the spelled-out default report option is the right guard (rather than --cov=src/spur or moving --cov after PYTEST_ARGS) is a maintainability call, and 15-04 builds on it."

duration: 41 min
completed: 2026-10-04
status: complete
---

# Phase 15 Plan 02: The Coverage Floor Summary

**`make test` now runs `--cov` against `fail_under = 96` (L = 96.99 from the serial baseline, S = 0.00 from three `-n 8` totals), counting BuildPool's spawned-worker lines; losing `tests/test_cli.py` reads 90.24 % and goes red, xdist is tolerated at N = 8 (6 of 6 green), and coverage costs 3.51 s there.**

## Performance

- **Duration:** 41 min
- **Started:** 2026-10-04T03:47:29Z
- **Completed:** 2026-10-04T04:29Z
- **Tasks:** 3
- **Files modified:** 10 (plus one debt file created)

## Accomplishments

- Worker lines are counted. `[tool.coverage.run]` gained `concurrency = ["multiprocessing", "thread"]`, `parallel = true`, `sigterm = true` under a comment that says why; `[tool.coverage.report]` has `precision = 2` and `fail_under = 96`. `tests/test_pool.py` alone with `--cov` reads (re-run at self-check, serial and `-n 2`, 16 passed each):

  ```
  src/spur/pool.py              54      0      6      0 100.00%
  ```

- C0, the serial baseline (load 8.37, 927 passed in 243.54s, wall 244.59 s, peak RSS 1407 MiB in 5 processes). Its rows, verbatim:

  ```
  src/spur/pool.py              54      3      6      0  95.00%   63-67, 222
  TOTAL                       1069     26    294     15  96.99%
  ```

  One point is 13.63 units (1,069 statements + 294 branches = 1,363); one missed statement is 0.073 points. C0's pool.py lost the one real worker build's lines (63-67 and 222, three statements, 0.22 points): this is 15-RESEARCH Pitfall 13 occurring on a serial run, not only under xdist. It is recorded as measured, is the lowest total, and sets L. Cause unproven; filed as debt.
- Six alternating runs at K = 8, order A1 B1 A2 B2 A3 B3 fixed before the first (A = `-n 8`, B = `-n 8 --cov`), HEAD `f771c5e`:

  | Run | Args | Load | pytest | Wall (s) | Peak RSS (MiB, procs) | Exit | Coverage |
  |---|---|---|---|---|---|---|---|
  | A1 | `-n 8` | 7.94 | 927 passed in 60.86s | 61.60 | 6829 (17) | 0 | none |
  | B1 | `-n 8 --cov` | 22.37 | 927 passed in 63.23s | 64.03 | 6596 (16) | 0 | 97.21% |
  | A2 | `-n 8` | 23.15 | 927 passed in 59.14s | 59.88 | 6968 (18) | 0 | none |
  | B2 | `-n 8 --cov` | 28.31 | 927 passed in 65.03s | 65.83 | 6614 (15) | 0 | 97.21% |
  | A3 | `-n 8` | 28.25 | 927 passed in 59.61s | 60.35 | 6911 (17) | 0 | none |
  | B3 | `-n 8 --cov` | 30.02 | 927 passed in 61.94s | 62.50 | 6673 (16) | 0 | 97.21% |

  mean(A) = 60.61 s, mean(B) = 64.12 s -> **coverage cost = 3.51 s at -n 8** (5.8 %). **D-05 tolerance at N = 8: adopted -- 6 of 6 green, 927 passed each.** No shared-state module failed, so D-08's `xdist_group` response did not fire and `tests/` is untouched. B totals 97.21 % x3, same 23 missed statements and 15 partial branches, spread 0.00: the combined total did not depend on data-file order (ordering probe, backstop). Largest peak RSS of the set: 6968 MiB (A2). Loads are as read; they climb because the rows ran back to back (D-04).
- Floor: `Floor: L = 96.99, S = 0.00, slack = max(0.25, S) = 0.25 -> fail_under = 96`. With `precision = 2` 96.00 passes and 95.99 fails (`should_fail_under(96, 96, 2)` False, `(95.99, 96, 2)` True); the trip point is 0.99 points under C0 and 1.21 under the xdist totals, so the 0.22-point flush loss cannot trip it alone.
- Red on the floor, attempt 1 of 2 (so no second): `make verify PYTEST_ARGS="-n 8 --ignore=tests/test_cli.py"` read `883 passed in 59.03s`, `TOTAL 1069 105 294 14 90.24%`, pytest exit 1 / make exit 2, and printed `ERROR: Coverage failure: total of 90.24 is less than fail-under=96.00` and `FAIL Required test coverage of 96.0% not reached. Total coverage: 90.24%`. Scratch run, not committed; `git diff --quiet HEAD -- tests` exits 0.
- The coverage-floor debt is retired at `2aadcea` (follow-up `b8926e7` records the sha): `Status: resolved`, the false "pytest-cov is installed" sentence corrected, a Resolution section citing each RESULTS subsection, file `git mv`ed to `resolved/`, INDEX row moved.
- REQ-coverage-floor and ROADMAP Phase 15 SC3 now say `make verify`'s test target runs `--cov` with the floor read from `fail_under`, and state the worker mechanism as settled (multiprocessing + thread, parallel, sigterm; D-09 addendum). ROADMAP went through edit-phase's write step: `roadmap milestone-scope` identical before and after (scope complete, phases 13-16), one Roadmap Evolution line.

## Task Commits

1. **Task 1: coverage config, thread tracing kept, data files ignored, pool.py proved at 100 %** - `f771c5e` (test)
2. **Task 2: baseline, six alternating runs at K, the floor by D-10's rule** - `6599677` (docs)
3. **Task 3: fail_under in config, --cov in make test, red on the floor shown, debt retired** - `2aadcea` (test); follow-up `b8926e7` (docs) records that sha in the debt file and the INDEX cell (D-18)
4. **Not in the plan:** `4fef83d` (docs) files the lost worker coverage flush as debt

**Plan metadata:** the closing `docs(15-02): read the coverage floor from fail_under in the requirement and SC3` commit (this SUMMARY, REQUIREMENTS.md, ROADMAP.md, STATE.md, state.json). `commits: 5` in the frontmatter is measured from the plan ledger (`b8b0eff..4fef83d`) and excludes the closing commit.

## Files Created/Modified

- `.gitignore` - `.coverage` and `.coverage.*` (not a bare `.coverage*`)
- `pyproject.toml` - coverage run keys with their comment; `[tool.coverage.report]` with `fail_under = 96` (cites the RESULTS table) and `precision = 2`; the old "no fail_under yet" lines removed
- `Makefile` - `test` recipe `$(PY) -m pytest --cov --cov-report=term $(PYTEST_ARGS)` and its comment (`--no-cov` for partial runs)
- `bench/RESULTS.md` - four subsections after `### xdist sweep`
- `docs/tech_debt/resolved/2026-09-21-no-coverage-floor.md`, `docs/tech_debt/INDEX.md` - the retired debt and its row
- `docs/tech_debt/active/2026-10-04-worker-coverage-flush-is-sometimes-lost.md` - new, severity nice
- `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`, `.planning/STATE.md` - Open Question 2's sentences, progress, decisions, session

## Decisions Made

- `fail_under = 96`, from the plan's rule applied to the measured totals; the human sees it with the other rows at 15-03.
- xdist adopted at N = 8 for the tolerance question (D-05); the human still picks N at 15-03.
- Debt filed rather than a retry for C0's lost worker flush (`nice`, trigger: a `make verify` reads under the floor with no code change, or `BuildPool.shutdown`/`_run_with_timeout` is touched).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `--cov` swallowed the first path in PYTEST_ARGS and ran the whole suite**
- **Found during:** Task 3 (the partial-run edge check)
- **Issue:** the plan's recipe `pytest --cov $(PYTEST_ARGS)` is wrong: `--cov` takes an optional value, so `make test PYTEST_ARGS="tests/test_calc.py -q"` read `tests/test_calc.py` as the coverage source and ran all 927 tests (225 s, total 15.92 %). The escape hatch the plan documents, `PYTEST_ARGS="tests/regression -q --no-cov"`, would have silently run the whole suite too. The plan's automated check for the partial run passed on the wrong behaviour (it exits non-zero either way).
- **Fix:** recipe is `$(PY) -m pytest --cov --cov-report=term $(PYTEST_ARGS)`; `--cov-report=term` is pytest-cov's default report, spelled out so an option, not a path, follows `--cov`. A later `--cov-report=term-missing` in PYTEST_ARGS still gives one table with the Missing column. Measured after: `tests/test_calc.py` runs 404 tests, reads 45.93 %, fails the floor; with `--no-cov` it exits 0 (404 passed in 0.25 s). The plan's `make -n test | grep -c -e '-m pytest --cov'` check still prints 1. The comment above `test:` carries the measurement; RESULTS "Red on the floor" records it.
- **Files modified:** Makefile, bench/RESULTS.md
- **Verification:** the partial-run check, `make -n test`, and the red run (which used the fixed recipe)
- **Committed in:** `2aadcea`

**2. [Rule 2 - Missing critical] Filed the lost worker coverage flush as debt**
- **Found during:** Task 2 (C0's pool.py row)
- **Issue:** CLAUDE.md asks that known-bad behaviour survives in a file, not a reply; the plan did not list a debt item for Pitfall 13's occurrence on a serial run.
- **Fix:** `docs/tech_debt/active/2026-10-04-worker-coverage-flush-is-sometimes-lost.md` plus its INDEX row, separate commit.
- **Committed in:** `4fef83d`

---

**Total deviations:** 2 auto-fixed (1 bug, 1 missing critical)
**Impact on plan:** the first was necessary for the gate to do what the plan said (partial runs run partially); 15-04 must keep `--cov-report=term` right after `--cov` when it inserts `-n`. No scope creep; `src/`, the fixture and `requirements.txt` are byte-identical to `20cd484`.

## Issues Encountered

- C0 lost three worker statements (Pitfall 13) while the three `-n 8` runs did not; see above. It makes the B-family spread (0.00) understate the real one, which is why L takes C0.
- A scratch check of the broken recipe left a full-suite run going in the background; it was killed (my own process, nothing committed).
- Hook behaviour: Tasks 1-3 and the sha follow-up each ran the pre-commit `make verify` and passed; the Task 3 hook ran it with `--cov` and the floor. The docs-only debt commit skipped the pytest hook.

## Known Stubs

None.

## Threat Flags

None. No network endpoint, auth path or schema changed; the new files are config, docs and a debt note. T-15-03: `[tool.coverage.run] source` unchanged, no `omit` in either table, `src/` byte-identical to `20cd484` (no `pragma: no cover` possible). T-15-04: the Task 2 and Task 3 verifies recompute F from the table and tie the literal to the RESULTS line; `tests/` untouched by the red run.

## TDD Gate Compliance

Not applicable (plan type `execute`, not `tdd`).

## For 15-03 (in front of the human)

- D-05: xdist tolerated at N = 8, 6 of 6 green with and without coverage; D-12: coverage costs 3.51 s at -n 8 (60.61 s -> 64.12 s). Both are in `bench/RESULTS.md` "Tolerance and coverage cost".
- The floor is 96 against totals of 96.99 (serial) and 97.21 (`-n 8`); any cut that removes tests lowers the total, and a cut that moves it under 96.00 fails the gate. Check each priced cut against the floor.
- 15-04: `make test` is `pytest --cov --cov-report=term $(PYTEST_ARGS)`; insert `-n` without separating `--cov` from `--cov-report=term`.
- `make verify`'s wall time now includes coverage's cost; the "before" for 15-04's before/after should say whether it is the no-`--cov` serial profile (P1/P2, 224.28 s) or a `--cov` serial run (C0, 244.59 s).

## Self-Check: PASSED

- Files FOUND: `.gitignore`, `pyproject.toml`, `Makefile`, `bench/RESULTS.md`, `docs/tech_debt/resolved/2026-09-21-no-coverage-floor.md`, `docs/tech_debt/active/2026-10-04-worker-coverage-flush-is-sometimes-lost.md`
- Commits FOUND: `f771c5e`, `6599677`, `2aadcea`, `b8926e7`, `4fef83d`
- Re-run: pool.py 100.00 % serial and `-n 2`; Task 1 config check, Task 2 `floor ok 96`, Task 3 `floor wired 96`, `partial-run rule ok`, `red run recorded`, `tree untouched by the red run`, `debt ok`, `Q2 sentences ok`, `D-20 ok`; `git diff --quiet 20cd484 -- src tests requirements.txt` exits 0

---
*Phase: 15-the-gate-measured-and-pinned*
*Completed: 2026-10-04*
