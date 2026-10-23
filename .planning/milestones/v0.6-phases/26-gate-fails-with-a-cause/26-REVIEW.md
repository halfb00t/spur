---
phase: 26-gate-fails-with-a-cause
reviewed: 2026-10-15T00:00:00Z
depth: standard
files_reviewed: 17
files_reviewed_list:
  - Makefile
  - pyproject.toml
  - tests/test_browser.py
  - tests/test_hooks.py
  - tests/test_pool.py
  - bench/RESULTS.md
  - docs/tech_debt/INDEX.md
  - docs/tech_debt/active/2026-10-10-make-verify-hung-at-98-percent-with-no-failure.md
  - docs/tech_debt/active/2026-10-10-ubuntu-latest-migrates-to-ubuntu-26-on-19-october.md
  - docs/tech_debt/active/2026-10-15-twin-selectors-fix-awaits-the-post-merge-main-read.md
  - docs/tech_debt/active/2026-10-15-wait-until-parked-spins-without-a-pause.md
  - docs/tech_debt/resolved/2026-10-06-resource-tracker-flake-fails-the-gate.md
  - docs/tech_debt/resolved/2026-10-10-hook-pin-reads-the-callers-pytest-args.md
  - docs/tech_debt/resolved/2026-10-10-test-image-collects-tests-that-read-host-files.md
  - docs/tech_debt/resolved/2026-10-15-twin-selectors-step-reds-main.md
  - docs/ideas/2026-10-15-run-make-test-image-in-ci.md
  - docs/ideas/INDEX.md
findings:
  critical: 0
  warning: 2
  info: 5
  total: 7
status: issues_found
---

# Phase 26: Code Review Report

**Reviewed:** 2026-10-15
**Depth:** standard
**Files Reviewed:** 17
**Status:** issues_found

## Summary

The phase diff `ccef7d3..HEAD` was read file by file. What I ran, rather than read:

- `ruff check tests src bench scripts`: clean. `mypy tests/test_pool.py tests/test_hooks.py`: clean.
- `tests/test_hooks.py` alone: 9 passed, also with `PYTEST_ARGS=-k foo` in the environment.
- Forced-GC gate test alone: 1 passed (10.13 s).
- The forced-GC child script run against a copy of `tests/test_pool.py` with the autouse fixture and the three `del manager` lines removed (via `python -c`, as the test does): 3 of 3 red, `1 failed, 3 passed`. The failure is `test_a_closed_pool_never_builds_a_replacement_worker` (the victim), with `check_alive calls: 94`. This matches the Makefile, docstring, RESULTS and debt-record claims. The gate test is not vacuous, and `_check_alive` is confirmed to run under the tracker's `RLock` in this interpreter (CPython 3.12.15 `ensure_running`).
- GNU Make 4.4.1 on a throwaway Makefile: a command-line `PYTEST_ARGS=--foo` hands the recipe exactly `MAKEFLAGS`, `MAKELEVEL`, `MFLAGS` and `PYTEST_ARGS`. The test docstring's claim holds.
- `make -n test-image`: the recipe quoting and continuation parse as `test_hooks.py` expects.
- `-i` count for "resource_tracker|Traceback|rerun" in the CI log is 7, all test names, as RESULTS says. `Timeout (` count is 0. The 83.55 s figure, `-n 4` and `1321 passed in 754.03s` are in the kept CI log.
- Test counts (58 and 43 collected in `test_pr_land.py` and `test_bench.py`) agree with the 47 and 41 dropped by the whole-file ignores.
- Debt INDEX rows and files agree in both directions. Idea INDEX is complete.

No correctness bug, vacuous test or Makefile portability defect was found in the code. The findings are two record-versus-record contradictions and five minor items.

## Warnings

### WR-01: The hang item names two different `faulthandler_timeout` values

**File:** `docs/tech_debt/active/2026-10-10-make-verify-hung-at-98-percent-with-no-failure.md:51`
**Issue:** The 2026-10-15 (26-05) paragraph says `faulthandler_timeout = 120` dumps a stalled test's stack. Six lines later the Runbook (line 57) says `pyproject.toml` sets `faulthandler_timeout = 170`, and the "Timeout (0:02:50)" header. `pyproject.toml:133` is 170. RESULTS (lines 6457-6459) says the `fix(26)` commit updated "the two lines of the hang item's runbook"; it missed this paragraph. This is the item an operator reads when a gate stalls. A reader who trusts line 51 will expect a dump at 120 s and read a quiet log at 121-169 s as "the timer is broken".
**Fix:** Change line 51 to `faulthandler_timeout = 170` (or "the ini's `faulthandler_timeout`, see the runbook") so the value is stated once.

### WR-02: The two twin-selectors records disagree on whether the 20 local runs are proof

**File:** `docs/tech_debt/active/2026-10-15-twin-selectors-fix-awaits-the-post-merge-main-read.md:17-18` (against `docs/tech_debt/resolved/2026-10-15-twin-selectors-step-reds-main.md`, "Not proven by this commit" paragraph, and `bench/RESULTS.md:6123-6126`)
**Issue:** The active item's Context says the fix "was proved on the real app (the `/api/info` response arms, the CX-05 control, 20 local runs at `-n 8`)". `bench/RESULTS.md` says the opposite about the third item: "The old step was not run 20 times here, so this count alone does not separate the fix from the host being fast ... The proof of the mechanism is the arms above". The resolved item files the same 20 runs under "Not proven by this commit". The 20 green runs are consistent with the fix; they would also be green with no fix, since the old step was not run 20 times on this host. This item is the only thing carrying D-05, so it should not list the weakest evidence as proof. The project's standing rule is that a claim must not exceed what the log proves.
**Fix:** In the active item, name only the three-run arms and the CX-05 control as the proof. Reword the 20 runs as "20 of 20 green, consistent with the fix, not separating it from a fast host (`RESULTS.md` 'Twin selectors (26-03)')".

## Info

### IN-01: The second new hook-pin test adds no discrimination over the first

**File:** `tests/test_hooks.py:166-177`
**Issue:** `test_the_pin_ignores_pytest_args_handed_down_from_the_make_command_line` sets `PYTEST_ARGS` (identical to the first test) plus `MAKEFLAGS`, `MAKELEVEL` and `MFLAGS`. `_make_env` already stripped those three before this phase, so the unfixed code was red on the second test only because of `PYTEST_ARGS`. The test cannot catch a regression that the first test misses. Its docstring says it "documents the shape", which is honest, but RESULTS and the resolved item count it as a second pin ("2 failed" without the fix).
**Fix:** Keep it as documentation, or drop it and move the Make 4.4.1 measurement into the first test's docstring. Do not cite it as independent coverage.

### IN-02: The image-recipe pin keeps a name that no longer says what it pins

**File:** `tests/test_hooks.py:229`
**Issue:** `test_the_image_suite_ignores_the_browser_test` now pins five mounts, `PYTHONPATH`, four pip tools and six ignored files. Its docstring says "Pins the `test-image` recipe as exact sets". CODING_VALUES asks for test names that read as requirements, and RESULTS records "(same name)" as deliberate. A red run will say "browser test" when `pytest-xdist` was dropped.
**Fix:** Rename to something like `test_the_image_suite_recipe_mounts_installs_and_ignores_exactly_what_it_should`. This is a rename only.

### IN-03: The browser test cites the wrong line range for the info-then-STL fetch

**File:** `tests/test_browser.py:1584`
**Issue:** The comment says "/api/info and, after that response, /api/model.stl (app.js:262-272)". In `src/spur/static/app.js` the info fetch is line 266 and the STL fetch is line 274, outside the cited range. RESULTS cites 262-274. The `350` debounce (line 289) and `643-644` citations are right.
**Fix:** Cite `app.js:266-274`, or `update()` by name, which will not drift.

### IN-04: New source comments cite phase-scoped planning paths that move at milestone close

**File:** `Makefile:226`; `docs/tech_debt/active/2026-10-10-make-verify-hung-at-98-percent-with-no-failure.md:65` (and the pre-existing `Source:` line 7)
**Issue:** The Makefile cites `.planning/phases/26-gate-fails-with-a-cause/investigation/26-06-redset.md`, and the runbook cites `.../26-05-stall.log`. Earlier phases were archived: phase 21 now lives under `.planning/milestones/v0.5-phases/`, so the hang item's existing `Source:` path (`.planning/phases/21-browser-test-of-the-viewer/investigation/...log`) already dangles. These new references will dangle the same way when v0.6 closes.
**Fix:** Cite the durable record (`bench/RESULTS.md` "make test-image (26-06)" and "Hang evidence (26-05)", which hold the red-set table and the stall proof), and keep the `.planning` path only as a secondary pointer.

### IN-05: The autouse fixture's cost is an unmeasured figure from another host

**File:** `tests/test_pool.py:58-59`
**Issue:** The fixture adds a `gc.collect()` after every test in this file. Its docstring says "Its cost was not re-measured here; the research read about 10 ms per test (the file 19.7 s -> 19.9 s, on another host)". That is flagged, so it is not a false claim. CODING_VALUES asks for measured numbers, and the nearby 26-04 section measured everything else about the fix on this host. The 19.7 s to 19.9 s file figure also predates the forced-GC test, so it is not comparable with the 31-33 s now quoted for the file.
**Fix:** Time `tests/test_pool.py -k 'not forced_gc' -n0 --no-cov` with and without the fixture on the dev host and replace the sentence with the reading. Or drop the number and keep "not measured".

---

_Reviewed: 2026-10-15_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
