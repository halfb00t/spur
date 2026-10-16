---
phase: 26-gate-fails-with-a-cause
plan: 01
subsystem: testing
tags: [pytest, make, hooks, gate, tech-debt]

requires:
  - phase: 21-browser-test-of-the-viewer
    provides: the debt item 2026-10-10-hook-pin-reads-the-callers-pytest-args (21-07 arm A)
provides:
  - "tests/test_hooks.py strips PYTEST_ARGS from the child environment of every make it starts"
  - "two caller-form guard tests, each seen red against the unfixed _make_env() first"
  - "the Phase 26 record section in bench/RESULTS.md and the investigation/ directory"
affects: [26-02, 26-03, 26-04, 26-05, 26-06, 26-07, 27-*, 28-*]

actuals:
  tokens: 3400
  tasks: 2
  commits: 1
plan_head_before: 73cbdddef3fa9e1a1aff901589696a8761211846
plan_head_after: 5d5472a8c730d4c3fe87877cd86a515eeee9141e
commits: 1

tech-stack:
  added: []
  patterns:
    - "A caller's flags are stripped with make's own in _make_env(), one place for every make a hook test starts"

key-files:
  created:
    - .planning/phases/26-gate-fails-with-a-cause/investigation/26-01-*.log
  modified:
    - tests/test_hooks.py
    - bench/RESULTS.md
    - docs/tech_debt/INDEX.md
    - docs/tech_debt/resolved/2026-10-10-hook-pin-reads-the-callers-pytest-args.md

key-decisions:
  - "Strip PYTEST_ARGS in _make_env() rather than passing PYTEST_ARGS= on each dry run: one place covers _dry_run, the two -W dry runs and _clean_git_env"
  - "The empty-PYTEST_ARGS edge is a recorded run, not a committed test: it reads the same recipe before and after and cannot be red"

requirements-completed: [REQ-hook-pin-ignores-caller-args]

coverage:
  - id: D1
    description: "The shared-recipe hook pin passes with PYTEST_ARGS set in the environment"
    requirement: REQ-hook-pin-ignores-caller-args
    verification:
      - kind: unit
        ref: "tests/test_hooks.py#test_the_pin_ignores_pytest_args_set_in_the_environment"
        status: pass
    human_judgment: false
  - id: D2
    description: "The pin passes with PYTEST_ARGS handed down from the make command line"
    requirement: REQ-hook-pin-ignores-caller-args
    verification:
      - kind: unit
        ref: "tests/test_hooks.py#test_the_pin_ignores_pytest_args_handed_down_from_the_make_command_line"
        status: pass
      - kind: integration
        ref: "make test PYTEST_ARGS=\"--ignore=tests/test_browser.py tests/test_hooks.py -n0 --no-cov -q -p no:cacheprovider\" (9 passed, exit 0)"
        status: pass
    human_judgment: false
  - id: D3
    description: "The nice debt item is retired in the fixing commit and the reading opens the Phase 26 section of bench/RESULTS.md"
    requirement: REQ-hook-pin-ignores-caller-args
    verification: []
    human_judgment: true
    rationale: "Prose and index bookkeeping; no test asserts the wording, the verifier reads the files"

duration: ~8min
completed: 2026-10-15
status: complete
---

# Phase 26 Plan 01: The hook pin stops reading the caller's PYTEST_ARGS Summary

**`_make_env()` drops `PYTEST_ARGS` with make's own flags, so a narrowed `make verify PYTEST_ARGS="--ignore=..."` no longer reds the shared-recipe pin; both caller forms were seen red first, and the nice debt item is retired in the same commit.**

## Performance

- **Duration:** ~8 min wall (start time not captured; estimated from the first command at 10:42Z to the commit), of which `make verify` took 194.64 s
- **Completed:** 2026-10-15
- **Tasks:** 2 (Task 1 a tracer, Task 2 auto), one commit by the plan's design: one concern
- **Files modified:** 12 (4 source or doc files, 8 logs)

## Accomplishments

- `_MAKE_VARIABLES` in `tests/test_hooks.py` now reads `("MAKEFLAGS", "MFLAGS", "MAKELEVEL", "PYTEST_ARGS")`; the `_make_env` docstring says why. `Makefile` is untouched (`git diff --exit-code v0.5 -- Makefile tests/regression/` exits 0).
- Two new tests, `test_the_pin_ignores_pytest_args_set_in_the_environment` and `test_the_pin_ignores_pytest_args_handed_down_from_the_make_command_line`, call the unchanged pin with the variables set the way GNU Make 4.4.1 hands them to a recipe. The file holds 9 `def test_` (7 kept, 2 new); none of the seven pins was touched.
- The five readings, each with its whole log under `.planning/phases/26-gate-fails-with-a-cause/investigation/`:

| Form | Before | After |
|---|---|---|
| environment | `1 failed in 0.03s`, exit 1 | `1 passed in 0.03s`, exit 0 |
| make command line | `1 failed, 6 passed in 0.59s`, `make: *** [Makefile:177: test] Error 1` | `9 passed in 0.48s`, exit 0 |
| empty `PYTEST_ARGS=` | `1 passed in 0.02s`, exit 0 | `1 passed in 0.03s`, exit 0 |
| new test, environment | red | passes (`9 passed`) |
| new test, make command line | red | passes (`9 passed`) |

- The red of both new tests, `26-01-tests-red.log`, `2 failed, 7 deselected in 0.06s`, on the assertion the debt item named:
  `AssertionError: assert '--ignore=' not in '.venv/bin/p...t_browser.py'` / `'--ignore=' is contained here: port=term --ignore=tests/test_browser.py` (`tests/test_hooks.py:122` before the fix).
- The debt item moved to `docs/tech_debt/resolved/` with `Status: resolved`, `Resolved in: test(26): the hook pins read the Makefile, not the caller's PYTEST_ARGS`, refreshed line references and a dated Resolution; the INDEX row moved from Active to the head of Resolved.
- `bench/RESULTS.md` gained `## Gate fails with a cause (Phase 26)` and `### The hook pin and the caller's PYTEST_ARGS (26-01)`: 46 lines added, 0 deleted against `v0.5`.
- The gate: `make verify` exit 0, `1320 passed in 194.64s (0:03:14)`, `TOTAL 1358 22 386 13 97.99%`, `Required test coverage of 96.0% reached` (`26-01-verify.log`).

## Task Commits

1. **Task 1: both caller forms red end to end, `_make_env()` strips PYTEST_ARGS, both green** and
2. **Task 2: open the phase's record, retire the hook-pin item, gate, commit** - `5d5472a` (test). One commit carries both tasks: the plan's own Task 2 step 4 names a single commit with the tests, the record, the moved debt item, the INDEX and the logs, and CLAUDE.md requires the retire in the fixing commit.

**Plan metadata:** the docs commit that carries this SUMMARY (below).

## Files Created/Modified

- `tests/test_hooks.py` - `import pytest`, `PYTEST_ARGS` in `_MAKE_VARIABLES`, the two caller-form tests
- `bench/RESULTS.md` - the Phase 26 section and the 26-01 reading, appended
- `docs/tech_debt/resolved/2026-10-10-hook-pin-reads-the-callers-pytest-args.md` - the retired item (moved from `active/`)
- `docs/tech_debt/INDEX.md` - row moved from Active to Resolved
- `.planning/phases/26-gate-fails-with-a-cause/investigation/26-01-*.log` - eight logs: env, make, empty before and after, tests-red, verify

## Decisions Made

- Strip in `_make_env()`, not per dry run: one place covers every `make` the hook tests start, where `PYTEST_ARGS=` on the command line would repeat at each call site (the plan's measured fix shape).
- The empty-`PYTEST_ARGS` edge stays a recorded run: `PYTEST_ARGS ?=` treats empty as unset, so no test of it can be red.
- The commit trailer follows the session's attribution (`Claude Sonnet 5.5`), not the plan's `Claude Opus 5.5` text.

## Deviations from Plan

None - plan executed exactly as written. Two small notes, neither a deviation: `26-01-verify.log` (the `make verify` output) was added to the investigation directory and committed with the others, matching the earlier phases' `*-verify.log` convention; and the RESULTS reading says in one sentence what it does not show (a narrowed full `make verify PYTEST_ARGS=...` was not run end to end; the make-command-line row is `make test` over the file that holds the pin).

## Issues Encountered

None. The defect reproduced on the first run in both forms, so the stop-and-report branch of Task 1 step 2 was not reached.

## Debt and ideas filed

None filed. One item retired: `2026-10-10-hook-pin-reads-the-callers-pytest-args` (nice).

## Known Stubs

None.

## Threat Flags

None. T-26-01 (a caller's flags entering the recipe a pin reads) is mitigated by `PYTEST_ARGS` in `_MAKE_VARIABLES`, pinned by both new tests; T-26-SC accepted, no package installed.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `investigation/` exists for the rest of the phase's logs, and `bench/RESULTS.md` has the Phase 26 section for later plans to append their `### ... (26-NN)` readings under.
- Later gate readings can narrow the gate with `PYTEST_ARGS` without the pin going red.

## Self-Check: PASSED

- FOUND: tests/test_hooks.py, bench/RESULTS.md, docs/tech_debt/resolved/2026-10-10-hook-pin-reads-the-callers-pytest-args.md, all eight `26-01-*.log`
- FOUND: commit `5d5472a` (ancestor of HEAD; subject and `tests/test_hooks.py` in its stat), `commits: 1` measured from the ledger base `73cbddd`
- Task 1 and Task 2 acceptance criteria re-run: all pass (`grep -c` counts 1 / 9 / 2, log contents, `exit 0` on every after-log, `Makefile` and `tests/regression/` unchanged, 0 deleted lines in `bench/RESULTS.md`)

---
*Phase: 26-gate-fails-with-a-cause*
*Completed: 2026-10-15*
