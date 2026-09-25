---
phase: 05-ci-observed-green
plan: 04
subsystem: ci-merge-gate
tags: [python-3.12, ruff, mypy, decision-log, ci-matrix, pep-695]

# Dependency graph
requires:
  - phase: 05-02
    provides: "`.github/workflows/required-jobs.txt` and the drift test in
      tests/test_pr_land.py that holds it equal to ci.yml -- this plan drops the
      test (3.10) line from both sides of that equality in one commit"
  - phase: 05-03
    provides: "The ruleset on `main`, already requiring exactly `test (3.12)`,
      `vendor-bundle`, `image` (the post-D-09 set applied ahead of this plan's
      matrix collapse) -- this plan's Task 3 reads it back and confirms it still
      equals the collapsed required-jobs.txt with no ruleset change needed"
provides:
  - "`## L23` in docs/architecture/decision_log.md, superseding L01's floor:
    Python 3.12 is the only supported interpreter"
  - "pyproject.toml: requires-python = \">=3.12,<3.13\", ruff target-version =
    \"py312\", the mypy python_version comment restated for one runtime"
  - "The three ruff UP-rule fixes py312 requires: params._f as a PEP 695 generic,
    pool.py's builtin TimeoutError catch, records.py's datetime.UTC"
  - "records._JsonHandler subclassing logging.StreamHandler[TextIO] directly, no
    TYPE_CHECKING indirection -- the construct that broke the retired 3.10 CI leg"
  - "Makefile's PYTHON loop and refusal message narrowed to python3.12 only"
  - ".github/workflows/ci.yml's matrix narrowed to [\"3.12\"]; required-jobs.txt
    loses test (3.10) in the same commit"
  - "Live confirmation that the ruleset on main already equals the collapsed
    required-jobs.txt with no ruleset-side change needed"
affects: [05-05]

# Actuals (#2632)
actuals:
  tokens: 4059
  tasks: 3
  commits: 3
plan_head_before: bae4328e22e7afc7c21e9422abbd91a7951856f7

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "PEP 695 type parameters (`def _f[T](...)`) replace a module-level
      `TypeVar` once the floor is 3.12 -- the first use of this syntax in the
      codebase, available at py312 target."
    - "A retired-floor comment names the incident and the runs it broke on
      (\"the retired 3.10 floor (L23)\", runs 35993984796/36028253714) rather
      than describing current CI behaviour -- keeps history legible without
      restating it as a live support claim."

key-files:
  created: []
  modified:
    - docs/architecture/decision_log.md
    - pyproject.toml
    - src/spur/params.py
    - src/spur/pool.py
    - src/spur/records.py
    - Makefile
    - .github/workflows/ci.yml
    - .github/workflows/required-jobs.txt
    - src/spur/build_errors.py
    - tests/test_pool.py

key-decisions:
  - "L23 keeps the one-entry CI matrix (`test (3.12)`) rather than collapsing to
    a bare `test` job -- the job name required-jobs.txt and the live ruleset
    both already name stays reachable, and widening later is a one-line matrix
    change instead of a rename that would also need a ruleset update (this
    plan's flagged assumption 3, confirmed against the live ruleset read-back
    in Task 3)."
  - "The ruleset on `main` needed no change in this plan: Plan 05-03 already
    applied the post-D-09 required-check set (`test (3.12)`, `vendor-bundle`,
    `image`), so Task 3's live read-back is read-only evidence that the wall,
    required-jobs.txt and ci.yml now all agree -- not a write."
  - "records._JsonHandler's TYPE_CHECKING-gated base class is removed entirely
    rather than kept as defensive style -- its whole reason (surviving a 3.10
    floor where runtime subscripting of StreamHandler raised TypeError) is
    gone, and CODING_VALUES treats a comment that no longer states a true
    constraint as worse than none."

requirements-completed: [REQ-ci-verified]

coverage:
  - id: D1
    description: "L23 appended after L22 in docs/architecture/decision_log.md,
      dated 2026-09-25, superseding L01's floor: quotes 'detected, not chosen',
      keeps the ceiling reasoning, cites the incident (StreamHandler[TextIO],
      runs 35993984796/36028253714/36028759311, fixed 990d1fe), and lists the
      3.12-only unwind list. L01 stays byte-identical; the commit removes no
      line from the log."
    requirement: "REQ-ci-verified"
    verification:
      - kind: other
        ref: "grep -nE '^## L23 .*supersedes L01' docs/architecture/decision_log.md
          (heading present); a 10-string evidence loop (detected not chosen,
          990d1fe, the three run ids, UP047/UP041/UP017, the requires-python
          string, the date) all present in L23's body; git show --format= <commit>
          -- decision_log.md has zero lines matching ^-[^-] (append-only proven)"
        status: pass
      - kind: unit
        ref: "make verify (178 tests) after the commit"
        status: pass
    human_judgment: false
  - id: D2
    description: "pyproject.toml, params.py, pool.py, records.py all agree on
      Python 3.12: requires-python's upper bound, ruff's target-version, and
      the three ruff-forced UP-rule fixes (PEP 695 type parameter, builtin
      TimeoutError, datetime.UTC) are in place; records._JsonHandler subclasses
      logging.StreamHandler[TextIO] directly with no TYPE_CHECKING split;
      _parse_level's docstring states the true reason getLevelNamesMapping()
      is unused."
    requirement: "REQ-ci-verified"
    verification:
      - kind: other
        ref: ".venv/bin/ruff check . -- 'All checks passed!' (was exactly the
          three UP047/UP041/UP017 findings before the fix, confirmed at
          planning and re-confirmed live before fixing)"
        status: pass
      - kind: unit
        ref: ".venv/bin/mypy src tests docker bench scripts -- 'Success: no
          issues found in 28 source files'"
        status: pass
      - kind: unit
        ref: "make test PYTEST_ARGS='tests/test_records.py tests/test_pool.py
          tests/test_calc.py tests/test_api.py -q' -- 82 passed"
        status: pass
    human_judgment: false
  - id: D3
    description: "The build and CI surfaces agree on 3.12 only: Makefile's
      PYTHON loop tries python3.12 alone and refuses with the exact message
      'make: no python3.12 on PATH.'; ci.yml's matrix is ['3.12']; required-
      jobs.txt lists exactly test (3.12), vendor-bundle, image; the live
      ruleset on main, read back, requires exactly the same three checks;
      build_errors.py and test_pool.py's docstrings no longer claim CI runs a
      second Python version."
    requirement: "REQ-ci-verified"
    verification:
      - kind: other
        ref: "grep -q 'python: [\"3.12\"]' ci.yml && grep -q 'for p in python3.12;
          do' Makefile; test over required-jobs.txt's exact sorted contents
          ('image;test (3.12);vendor-bundle;'); live gh api
          repos/halfb00t/spur/rules/branches/main read-back equals
          required-jobs.txt byte-for-byte (both printed: 'image;test
          (3.12);vendor-bundle' on each side)"
        status: pass
      - kind: unit
        ref: "make test PYTEST_ARGS='tests/test_pr_land.py tests/test_pool.py
          -q' -- 66 passed (the drift test included)"
        status: pass
      - kind: other
        ref: "make VENV=<tmp> PYTHON= venv (no interpreter forced) -- exits
          non-zero, prints 'make: no python3.12 on PATH.'"
        status: pass
      - kind: other
        ref: "git grep for residual second-interpreter/dual-version-CI phrases
          across Makefile pyproject.toml .github src tests docker bench
          scripts -- zero matches (exit 1)"
        status: pass
      - kind: unit
        ref: "make verify -- 178 passed, 5/5 import-linter contracts kept"
        status: pass
    human_judgment: false

# Metrics
duration: ~14min (reconstructed; see Issues Encountered)
completed: 2026-09-25
status: complete
---

# Phase 5 Plan 4: Python 3.12 Only -- Decision, Package, Build and CI Agreement Summary

**`requires-python`, ruff's target, the CI matrix, the Makefile's interpreter choice, and
a new decision-log entry (L23) all now agree spur supports Python 3.12 only, closing the
structural gap that let a 3.11-only construct reach `main` unimportable on 3.10 (`make
verify` green, 178 tests, live ruleset read-back confirmed unchanged).**

## Performance

- **Duration:** ~14 min (reconstructed -- see Issues Encountered)
- **Started:** ~2026-09-25T06:51:34Z (reconstructed, from STATE.md's prior session
  timestamp)
- **Completed:** 2026-09-25T07:05:55Z
- **Tasks:** 3 completed
- **Files modified:** 10

## Accomplishments

- `docs/architecture/decision_log.md` gains `## L23 -- Python 3.12 only (supersedes
  L01's floor)`, appended after L22, dated 2026-09-25: quotes L01's own "detected, not
  chosen", keeps the ceiling reasoning (`cadquery-ocp` has no wheels past 3.12), cites the
  incident (`logging.StreamHandler[TextIO]`, runs 35993984796/36028253714/36028759311,
  fixed `990d1fe`), and lists the 3.12-only unwind list for a future widening. The commit
  removes no line from the log -- L01 stays byte-identical.
- `pyproject.toml`: `requires-python = ">=3.12,<3.13"` (pip now refuses an install on
  3.10/3.11 instead of spending minutes building OpenCascade); `[tool.ruff]
  target-version = "py312"`; the mypy `python_version` comment restated for one runtime
  instead of "floor checked by CI's 3.10 execution"; `disallow_any_explicit`'s directory
  list gains `scripts` (already in `make typecheck` since Plan 05-01).
- The three findings `ruff check --target-version py312` reported at planning, fixed
  exactly as planned, nothing extra in `scripts/`: `params._f` redeclared with a PEP 695
  type parameter (`def _f[T](...)`, no module-level `TypeVar`); `pool.py` catches the
  builtin `TimeoutError` (aliased to `asyncio.TimeoutError` since 3.11); `records.py` uses
  `datetime.UTC`.
- `records._JsonHandler` now subclasses `logging.StreamHandler[TextIO]` directly in the
  class statement -- the `TYPE_CHECKING`/`else` split that gave the type checker and the
  interpreter different base classes existed only to survive a floor below 3.11, and that
  floor is gone. `_parse_level`'s docstring states the true reason
  `getLevelNamesMapping()` is unused (it is 3.11+, and `getLevelName` already answers the
  same question) rather than citing the retired floor.
- `Makefile`'s `PYTHON` loop tries `python3.12` alone; `$(STAMP)`'s refusal is now exactly
  `make: no python3.12 on PATH.`, citing L23. `.github/workflows/ci.yml`'s matrix narrows
  to `["3.12"]` -- the job still reports as `test (3.12)`, so `pr.land`'s required-check
  name is unaffected. `.github/workflows/required-jobs.txt` loses the `test (3.10)` line
  in the same commit as the matrix, per the file's own header and L22.
- Live read-back (`gh api repos/halfb00t/spur/rules/branches/main`) confirms the ruleset
  on `main` already requires exactly `image`, `test (3.12)`, `vendor-bundle` -- the
  post-D-09 set Plan 05-03 applied ahead of this plan's collapse -- so nothing on the
  ruleset itself needed to change. `src/spur/build_errors.py`'s `BuildTimeout` docstring
  and `tests/test_pool.py`'s `test_executor_processes_attribute_still_exists` docstring no
  longer claim CI runs a second Python version; both state the true reason instead.

## Task Commits

Each task was committed atomically:

1. **Task 1: `L23` appended -- Python 3.12 only (supersedes L01's floor) (D-08, D-09)**
   - `980f343` (docs)
2. **Task 2: The package targets Python 3.12 -- `pyproject.toml`, and what ruff now
   requires (D-09)** - `9ba4275` (build)
3. **Task 3: The build and CI run Python 3.12 only -- `make venv`, the matrix, the
   required list, and the comments that argued from two versions; the ruleset read back
   equal to the list (D-05, D-09, D-12)** - `5981c6f` (ci)

**Plan metadata:** committed separately by this workflow's final step.

## Files Created/Modified

- `docs/architecture/decision_log.md` - `## L23` appended (Task 1)
- `pyproject.toml` - `requires-python`, ruff `target-version`, mypy comment,
  `disallow_any_explicit`'s directory list (Task 2)
- `src/spur/params.py` - `_f` redeclared with a PEP 695 type parameter (Task 2)
- `src/spur/pool.py` - builtin `TimeoutError` catch, comment's first paragraph rewritten
  (Task 2)
- `src/spur/records.py` - `datetime.UTC`; `_JsonHandler`'s `TYPE_CHECKING` indirection
  removed; `_parse_level`'s docstring restated (Task 2)
- `Makefile` - `PYTHON` loop and refusal message narrowed to `python3.12` (Task 3)
- `.github/workflows/ci.yml` - matrix narrowed to `["3.12"]` (Task 3)
- `.github/workflows/required-jobs.txt` - `test (3.10)` line removed (Task 3)
- `src/spur/build_errors.py` - `BuildTimeout`'s docstring restated (Task 3)
- `tests/test_pool.py` - `test_executor_processes_attribute_still_exists`'s docstring
  restated (Task 3)

## Decisions Made

See `key-decisions` in the frontmatter: keeping the one-entry CI matrix (job name
`test (3.12)` stays reachable, widening later is one line) rather than collapsing to a
bare `test` job; confirming the ruleset on `main` needed no write in this plan (Plan
05-03 already applied the post-D-09 set); and removing `records._JsonHandler`'s
`TYPE_CHECKING` indirection entirely rather than keeping it as defensive style, since its
whole reason no longer exists.

## Deviations from Plan

None - plan executed exactly as written. The three ruff findings matched planning's
prediction exactly (UP047/UP041/UP017, the same three locations), with nothing additional
in `scripts/`. The live ruleset read-back matched `required-jobs.txt` with no drift,
confirming Plan 05-03's forward-looking application was correct and needed no follow-up
write here.

## Issues Encountered

- `PLAN_START_TIME` was not captured via an explicit `date -u` call at the very start of
  this session -- the same gap 05-01/05-02/05-03-SUMMARY.md all recorded. Duration above
  is reconstructed from STATE.md's prior session timestamp (06:51:34Z) to this summary's
  own completion timestamp (07:05:55Z), not a precisely measured figure. All three task
  commit timestamps (`980f343`, `9ba4275`, `5981c6f`) are exact and git-verifiable
  regardless.

## User Setup Required

None - no external service configuration required. `gh` was already authenticated with
the scopes Task 3's precondition needed (`repo`, `workflow`), verified read-only
(`gh auth status`) before the live ruleset read-back.

## Next Phase Readiness

- `pyproject.toml`, `Makefile`, `ci.yml` and `required-jobs.txt` all agree on Python 3.12
  only, and `docs/architecture/decision_log.md` records why (L23). `make verify` is green
  (178 tests, 5/5 import-linter contracts kept).
- Plan 05-05 (the phase-wide residue check and the phase's own ship/merge) can now update
  README, AGENTS.md, CODING_VALUES.md, HOW_TO_DEVELOP.md section 0, the architecture docs
  and `.planning/` to say "3.12" instead of "3.10-3.12" -- this plan deliberately left
  those documents untouched (flagged assumption 5), and used only "the retired 3.10 floor
  (L23)" or named run ids when a rewritten comment had to mention the old floor as
  history, per this plan's own instruction to Plan 05-05's phrase check.
- No blockers for 05-05.

## Self-Check: PASSED

All key-files modified (`docs/architecture/decision_log.md`, `pyproject.toml`,
`src/spur/params.py`, `src/spur/pool.py`, `src/spur/records.py`, `Makefile`,
`.github/workflows/ci.yml`, `.github/workflows/required-jobs.txt`,
`src/spur/build_errors.py`, `tests/test_pool.py`) confirmed present on disk with `[ -f ]`.
All three task commits (`980f343`, `9ba4275`, `5981c6f`) confirmed in `git log --oneline
--all`. Every plan-level `<verification>` item re-run and passing: L23 appended with L01
untouched; `pyproject.toml`/`Makefile`/`ci.yml`/`required-jobs.txt` agree on 3.12;
`.venv/bin/ruff check .` clean at py312 target; the targeted residual grep for a second
interpreter or a dual-version CI claim finds nothing (exit 1); the live ruleset on `main`
requires exactly the jobs `required-jobs.txt` lists (`image;test (3.12);vendor-bundle` on
both sides); `make verify` exits 0 (178 tests passed).

---
*Phase: 05-ci-observed-green*
*Completed: 2026-09-25*
