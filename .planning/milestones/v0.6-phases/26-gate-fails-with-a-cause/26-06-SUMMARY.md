---
phase: 26-gate-fails-with-a-cause
plan: 06
subsystem: testing
tags: [docker, makefile, pytest, test-image, tech-debt, red-set]

requires:
  - phase: 26-gate-fails-with-a-cause
    provides: plans 26-01 to 26-05, the Phase 26 section of bench/RESULTS.md, the investigation/ directory, and 26-04's forced-GC test in tests/test_pool.py
provides:
  - "Makefile: the test-image recipe mounts src, tests, pyproject.toml, bench and scripts read-only, sets PYTHONPATH=/app/src:/app, installs pytest-cov and pytest-xdist, and ignores six files whole, each with its cause in a comment"
  - "tests/test_hooks.py: test_the_image_suite_ignores_the_browser_test (same name) pins exact sets of mounts, PYTHONPATH, pip tools and ignored files; seen red first"
  - "bench/RESULTS.md: make test-image (26-06) - the red set, the D-11 checkpoint, the fix, the after run, what the image suite does not run"
  - "docs/tech_debt/resolved/2026-10-10-test-image-collects-tests-that-read-host-files.md: the nice item, retired with a measured Resolution"
  - "docs/ideas/2026-10-15-run-make-test-image-in-ci.md: the deferred CI idea, captured only"
affects: [26-07]

actuals:
  tokens: 4160    # chars/4 over the added lines in Makefile, tests/, bench/ and docs/ (16645 chars); logs excluded
  tasks: 3
  commits: 2
plan_head_before: febe0b969b251d684ee36399fb45b195931fadf0
plan_head_after: d9904e41bf9a8b986f368dc0441f7b79beee8bbc
commits: 2

tech-stack:
  added: []
  patterns:
    - "A whole-file --ignore with its cause in a recipe comment, instead of per-test --deselect ids that go stale silently on a rename"
    - "A recipe pin that parses the dry-run docker run block with shlex into exact sets, not a substring check"

key-files:
  created:
    - docs/ideas/2026-10-15-run-make-test-image-in-ci.md
    - .planning/phases/26-gate-fails-with-a-cause/investigation/26-06-first.log
    - .planning/phases/26-gate-fails-with-a-cause/investigation/26-06-first-mounted.log
    - .planning/phases/26-gate-fails-with-a-cause/investigation/26-06-optB-probe.log
    - .planning/phases/26-gate-fails-with-a-cause/investigation/26-06-redset.md
    - .planning/phases/26-gate-fails-with-a-cause/investigation/26-06-pin-red.log
    - .planning/phases/26-gate-fails-with-a-cause/investigation/26-06-after.log
  modified:
    - Makefile
    - tests/test_hooks.py
    - bench/RESULTS.md
    - docs/tech_debt/INDEX.md
    - docs/ideas/INDEX.md
  moved:
    - docs/tech_debt/active/2026-10-10-test-image-collects-tests-that-read-host-files.md -> docs/tech_debt/resolved/

key-decisions:
  - "Option B at the D-11 checkpoint (human): add pytest-cov and pytest-xdist to the recipe's pip install so 26-04's forced-GC gate test runs in the image; tests/test_pool.py is not ignored"
  - "Whole-file ignores per D-11's text (human), not per-test --deselect: a stale --deselect id fails silently on a rename; the cost is 47 passing tests in test_pr_land.py and 41 in test_bench.py dropped from the image suite"
  - "The red set was read from a second, hand-mounted run because the plan's single unfixed run stopped at 5 collection errors before any test ran"

requirements-completed: [REQ-test-image-runs-what-it-claims]

coverage:
  - id: D1
    description: "make test-image was run once on the unfixed recipe and its whole red set recorded and classified before any fix: 5 collection errors (exit 2), then 29 failed / 1290 passed with the mounts applied by hand; 33 of 34 rows fit D-11, one was class other and went to the human"
    requirement: REQ-test-image-runs-what-it-claims
    verification:
      - kind: integration
        ref: "investigation/26-06-first.log, 26-06-first-mounted.log, 26-06-redset.md"
        status: pass
    human_judgment: false
  - id: D2
    description: "After the fix make test-image exits 0 with 1201 passed in 888.34s, no ERROR collecting line and no SKIPPED line; every file it does not run is a named --ignore with its cause in a recipe comment"
    requirement: REQ-test-image-runs-what-it-claims
    verification:
      - kind: integration
        ref: "investigation/26-06-after.log (make test-image exit 0); the Task 2 verify script"
        status: pass
    human_judgment: false
  - id: D3
    description: "The image pin keeps its name and asserts exact sets of the five :ro mounts, PYTHONPATH=/app/src:/app, the four pip-installed tools and the six ignored files; seen red (1 failed) against the old recipe first, green (9 passed) after"
    requirement: REQ-test-image-runs-what-it-claims
    verification:
      - kind: unit
        ref: "tests/test_hooks.py::test_the_image_suite_ignores_the_browser_test; investigation/26-06-pin-red.log"
        status: pass
    human_judgment: false
  - id: D4
    description: "tests/test_calc.py and tests/test_trochoid.py stay in the image suite, no skip marker was added to any test file, the nice item is retired in the fixing commit, and the CI idea is captured with nothing of it built (git diff v0.5 -- .github/ is empty)"
    requirement: REQ-test-image-runs-what-it-claims
    verification:
      - kind: integration
        ref: "Task 2 and Task 3 verify scripts; git diff --exit-code v0.5 -- .github/ tests/regression/ src/"
        status: pass
    human_judgment: false

duration: continuation about 40 min (Task 1 ran in an earlier session)
completed: 2026-10-15
status: complete
---

# Phase 26 Plan 06: `make test-image` runs what it claims Summary

**`make test-image` exits 0 with `1201 passed in 888.34s`: `bench/` and `scripts/` mounted read-only, `PYTHONPATH=/app/src:/app`, pytest-cov and pytest-xdist installed so 26-04's forced-GC test runs there, and six host-only files ignored whole by name with a cause each, all pinned as exact sets.**

## Performance

- **Duration:** this continuation about 40 min wall; Task 1 (the unfixed runs) was an earlier session
- **Completed:** 2026-10-15
- **Tasks:** 3 (Task 1 a tracer, done earlier; Tasks 2 and 3 auto)
- **Files modified:** 5 source, record or debt files, 1 moved, 1 new idea, 6 log and table files under `investigation/`

## Accomplishments

- **The first run, and a second reading (SC1, D-11).** `make test-image PYTEST_ARGS="-rs"` on the unfixed recipe exited 2, `5 errors in 4.20s`: `ModuleNotFoundError` for `bench` (test_bench, test_calc, test_trochoid) and `scripts` (test_pr_land, test_skip_tokens). A collection error stops the run, so no test-level red showed. The decisive reading is the same image and command with the mounts and `PYTHONPATH` applied by hand and only the browser test ignored: **`29 failed, 1290 passed in 863.84s (0:14:23)`**, exit 1. The image is linux/amd64 (`DOCKER_DEFAULT_PLATFORM`), emulated on this arm64 host; container pytest 9.1.1.
- **The red set (34 rows).** 5 `bench/scripts not mounted` (fixed by the mounts), 14 `make` (9 test_hooks, 5 test_no_fake_done), 11 `.github` (test_pr_land), 2 `git` (test_bench), 1 `Dockerfile` (test_browser_pins), 1 `other`. The research's guess of two `test_bench.py` exit-128 tests was wrong in kind: the two are `FileNotFoundError: 'git'`. Full table in `investigation/26-06-redset.md` and `bench/RESULTS.md`.
- **The D-11 checkpoint and its answer.** The `other` row was `tests/test_pool.py::test_forced_gc_inside_the_resource_tracker_lock_finds_no_reentrant_cleanup`: its subprocess `pytest --no-cov -n0` fails `unrecognized arguments` because the image holds neither pytest-cov nor pytest-xdist (a probe with both installed read `1 passed, 20 deselected in 24.28s`). The human chose option B (install the two plugins), and whole-file ignores per D-11's text.
- **Pin red, then the recipe (D-13).** The pin was rewritten to parse the dry-run `docker run` block with `shlex` into exact sets and run against the old recipe: `1 failed, 8 deselected` (`26-06-pin-red.log`). The recipe edit made it `9 passed`.
- **The recipe.** Five `:ro` mounts, `PYTHONPATH=/app/src:/app` (comment states the `/app` is redundant beside `python -m pytest` with `-w /app` and set because D-11 chose it), `pip install pytest httpx pytest-cov pytest-xdist`, and `--ignore` for `tests/test_browser.py`, `test_hooks.py`, `test_no_fake_done.py`, `test_browser_pins.py`, `test_pr_land.py`, `test_bench.py`, one comment line per file naming its cause. `tests/test_calc.py` and `tests/test_trochoid.py` are in the image suite; no skip marker was added anywhere.
- **The after run.** `make test-image PYTEST_ARGS="-rs"`: exit 0, `1201 passed in 888.34s (0:14:48)`, 938.98 s wall with the image layers cached, no `ERROR collecting`, no `SKIPPED`.
- **The gate:** `make verify`, exit 0, `1321 passed in 187.73s (0:03:07)`.

## Task Commits

1. **Task 1: the unfixed runs and the classified red set** - no commit of its own, by the plan's design (logs and the red-set table committed with Task 2)
2. **Task 2: pin red, mounts, PYTHONPATH, plugins, named ignores, record, item retired** - `64915f5` (fix)
3. **Task 3: the deferred CI idea** - `d9904e4` (docs)

## Deviations from Plan

### Human-approved deviation from D-11's literal text

**1. [Checkpoint decision] Install pytest-cov and pytest-xdist in the image**
- **Found during:** Task 1 (the red-set classification)
- **Issue:** one red was class `other`, outside D-11's five causes: the forced-GC test (26-04, D-02) needs two pytest plugins the image lacks.
- **Decision (human, option B):** add both plugins to the recipe's `pip install` line so the D-02 gate test runs in the image, rather than ignoring `tests/test_pool.py`. The pin asserts them and the recipe comment states the reason.
- **Files modified:** Makefile, tests/test_hooks.py
- **Commit:** `64915f5`

### Process notes

- **The red set came from a second reading.** The plan wrote one unfixed run; it stopped at 5 collection errors, so a second run with the mounts applied by hand (no Makefile edit, same image) was read to see the test-level reds. Both logs are kept; the table says which reading each row came from.
- **Whole-file ignores drop passing tests.** `tests/test_pr_land.py` loses 47 passing tests (11 of 58 fail) and `tests/test_bench.py` loses 41 (2 of 43 fail) from the image suite. Whole-file was the human's choice, as D-11 writes it: a per-test `--deselect` id goes stale silently on a rename. `make verify` still runs them all.
- **The plan's commit ledger (0c) was not created before the first commit** because Task 1 made no commit; the base is `febe0b9`, HEAD at the start of this plan, and `commits: 2` is measured with `git rev-list --count febe0b9..HEAD`.
- **The commit trailer follows the session's attribution (Claude Sonnet 5.5)**, not the plan text, as in 26-01 to 26-05.
- **`ruff format --check tests/test_hooks.py` reports pre-existing formatting differences** in unrelated blocks (a test near line 300); not touched, out of scope. `ruff check` (the gate's check) passes.

**Total deviations:** 1 human-approved (D-11 literal text), 5 process notes. **Impact:** none on the committed result.

## Issues Encountered

- The after run took 14:59 wall under amd64 emulation on an arm64 host; the first diagnostic run 14:23 of pytest. Neither is a figure for a native host.

## Known Stubs

None. No placeholder, hardcoded empty value or unwired data in the files this plan touched.

## Threat Flags

None. The new `bench/` and `scripts/` mounts are `:ro` and the pin asserts every mount's mode as an exact set (T-26-14); every ignore traces to a classified red and the maths files are not ignored (T-26-16). The two plugins join the unpinned `pip install` line already accepted as T-26-15 (throwaway `--rm` container, never in CI); the container's pytest version is on record.

## Debt and ideas

- **Resolved:** `docs/tech_debt/resolved/2026-10-10-test-image-collects-tests-that-read-host-files.md` (nice), in `64915f5`, INDEX row moved.
- **Filed:** `docs/ideas/2026-10-15-run-make-test-image-in-ci.md` (idea), in `d9904e4`, INDEX row added.
- No new debt filed. Open for later: the image suite takes about 15 minutes serial under emulation, a cost to weigh if the CI idea is taken up.

## Next Phase Readiness

Ready for 26-07 (phase close gate and the first CI run). Nothing in this plan touched `.github/`, `src/` or `tests/regression/`.

## Self-Check: PASSED

- Files exist: Makefile, tests/test_hooks.py, bench/RESULTS.md, the moved item under `docs/tech_debt/resolved/` (and absent from `active/`), `docs/ideas/2026-10-15-run-make-test-image-in-ci.md`, the six `26-06-*` files under `investigation/`.
- Commits exist on the branch: `64915f5`, `d9904e4`.
- `.venv/bin/python -m pytest tests/test_hooks.py -n0 --no-cov -q -p no:cacheprovider`: `9 passed`; `git diff --exit-code v0.5 -- .github/ tests/regression/ src/` exits 0.
- `make verify`: exit 0, `1321 passed in 187.73s (0:03:07)`.
