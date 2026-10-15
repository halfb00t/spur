---
phase: 21-browser-test-of-the-viewer
plan: 06
subsystem: testing
tags: [playwright, make-verify, gate-admission, xdist, ci, pre-commit]

requires:
  - phase: 21-05
    provides: the scenario module in its final shape (golden sweep), tests/capture_requests.py, make golden.regen
  - phase: 21-02
    provides: the Linux runner reading (--with-deps needs no sudo line, 14.7 s)
  - phase: 21-01
    provides: the $(BROWSER) stamp, the pin, the fail-closed launch()
provides:
  - tests/test_browser_pins.py, three light pins the commit slice runs (no skip path, playwright exact and dev-only, default shell and no plugin)
  - tests/test_browser.py, the browser test admitted into make verify, the pre-push hook, make worktree.land and CI, never collected by make verify.fast or make test-image
  - test depends on $(BROWSER); --ignore by name in test.fast and test-image; HEAVY_TEST_FILES with test_browser; -o in _dry_run
  - two hook pins (the whole gate installs the browser and the commit slice never does; the image suite ignores the browser test)
  - CI passes BROWSER_INSTALL_ARGS --with-deps on the make verify step
  - bench/RESULTS.md Admission (21-06) and seven 21-06 rows in Seen red once
affects: [21-07, 21-08, 23, 24, 25]

actuals:
  tokens: 8700
  tasks: 3
  commits: 4

plan_head_before: 141a7b0f8367279b1909942e12aa3be7f61c2231
plan_head_after: 6f9ca669e4494a53aa7ef08060df15c73f419e84
commits: 4

tech-stack:
  added: []
  patterns:
    - a skip path is looked for in the syntax tree of the browser test's modules, so comments and docstrings never trip the pin
    - a dry run of a target that the commit slice shares with the whole gate passes -o for the stamp only the gate builds, which makes the two static prefixes byte-identical wherever the stamp stands
    - one commit admits a test into the gate together with every exclusion and the gate's own text

key-files:
  created:
    - tests/test_browser_pins.py
    - docs/tech_debt/active/2026-10-10-test-image-collects-tests-that-read-host-files.md
  modified:
    - tests/test_browser.py
    - tests/test_hooks.py
    - Makefile
    - .github/workflows/ci.yml
    - .pre-commit-config.yaml
    - docs/architecture/web-ui.md
    - .gitignore
    - bench/RESULTS.md
    - docs/tech_debt/INDEX.md
    - docs/tech_debt/active/2026-10-10-root-shape-bogus-loads-a-blank-select.md

key-decisions:
  - "The admission is one commit (d0f5474): the rename, test's prerequisite, both exclusions, the HEAVY_TEST_FILES entry, -o in the dry run, CI's --with-deps and the gate's text, so undoing it is a single revert (D-01)"
  - "No ignore entry was added to .gitignore: 21-01's git status --ignored reading found nothing outside .venv/, so only a why-comment beside .venv/ was added (PD-10)"
  - "ci.yml gets neither -rP nor a hardware step: both were spike-only (PD-14)"

patterns-established:
  - "A pin on existing state is proved by a deliberate break read red once and reverted, not by a missing implementation"
  - "Stamps are touched back to fresh only after a break has moved a file's mtime and git shows its content byte-identical"

requirements-completed: [REQ-browser-in-the-gate, REQ-browser-fails-closed, REQ-browser-stack-pinned, REQ-browser-server-fixture]

coverage:
  - id: D1
    description: "The browser test has no path that passes or is skipped without the browser, launch() fails with the install command, playwright is pinned exactly in dev and absent from the runtime closure, no pytest-playwright and no channel=; each pin seen red once"
    requirement: REQ-browser-fails-closed
    verification:
      - kind: unit
        ref: "tests/test_browser_pins.py (3 passed)"
        status: pass
    human_judgment: false
  - id: D2
    description: "tests/test_browser.py runs inside make verify and is excluded by name from make verify.fast and make test-image; the commit slice reads 834 passed in about 10 s"
    requirement: REQ-browser-in-the-gate
    verification:
      - kind: unit
        ref: "tests/test_hooks.py#test_verify_and_verify_fast_share_one_static_prefix_and_one_pytest_recipe, #test_the_whole_gate_installs_the_browser_and_the_commit_slice_never_does, #test_the_image_suite_ignores_the_browser_test"
        status: pass
      - kind: other
        ref: "make verify -> 1226 passed in 192.08s, coverage 97.92 % against 96.0 %"
        status: pass
    human_judgment: false
  - id: D3
    description: "The file passes ten of ten at -n 8, and a missing shell at the final path reads 1 failed with the install command in the output"
    requirement: REQ-browser-server-fixture
    verification:
      - kind: integration
        ref: "make test PYTEST_ARGS='tests/test_browser.py -n 8 --no-cov -q' x10 -> 10 of 10 passed; PLAYWRIGHT_BROWSERS_PATH=<empty dir> pytest tests/test_browser.py -> 1 failed in 0.61s"
        status: pass
    human_judgment: false

duration: 25min
completed: 2026-10-10
status: complete
---

# Phase 21 Plan 06: Gate admission Summary

**The browser test now runs inside `make verify`, the pre-push hook, `make worktree.land` and CI, excluded by name from the 10 s commit slice and the image suite, with pins that go red if it ever gains a skip path, a loose pin, a plugin or a channel.**

## Performance

- **Duration:** about 25 min (13:24Z to 13:41Z of wall clock plus the gate runs)
- **Tasks:** 3
- **Commits:** 4 (3 task commits, 1 debt filing)
- **Files modified:** 12 (2 created, 1 renamed)

## Accomplishments

- `tests/test_browser_pins.py` (`2b83400`): three light pins read from the syntax tree, so they run at commit and import neither playwright nor the kernel. Each seen red once.
- The admission (`d0f5474`): one commit carrying the rename, `test: $(STAMP) $(BROWSER)`, both `--ignore` flags, `HEAVY_TEST_FILES`, `-o` in the dry run, two hook pins, `BROWSER_INSTALL_ARGS: --with-deps` in CI and the gate's text. Four guards seen red once before it.
- The readings (`1943f8e`): `make verify.fast` 10.14, 10.31 and 10.41 s with 834 passed; ten of ten `-n 8` passes at about 4.1 s; the missing shell reads `1 failed`; a fresh stamp schedules no install; `make verify` reads 1226 passed, 97.92 %.

## Task Commits

1. **Task 1: pins the commit slice runs** - `2b83400` (test)
2. **Task 2: the admission commit** - `d0f5474` (build)
3. **Task 3: the admission readings** - `1943f8e` (docs)
4. **Debt filed** - `6f9ca66` (docs), see Debt filed

**Plan metadata:** the commit that carries this file.

## TDD record (Task 1)

The pins check state that already holds, so there is no missing implementation to be red on. Each pin was instead shown red by a deliberate break, each reverted with `git checkout` and `git diff --exit-code` clean. The classifier `gsd_run check tdd-red-evidence` was not run: the plan type is `execute`, `workflow.tdd_mode` is not set, and pytest's console output is not one of the formats it reads.

| Pin | Break | First failure line |
|---|---|---|
| no path that passes without the browser | `pytest.importorskip("playwright")` at the top of `tests/browser_session.py` | `AssertionError: a path that passes without the browser (D-02): browser_session.py:35: importorskip in pytest.importorskip("playwright")` |
| exact and dev-only | `playwright==1.63.0` to `playwright>=1.63.0` | `AssertionError: 'playwright>=1.63.0' is not an exact pin: the headless-shell revision, and with it the canvas bar, moves with the release` |
| default shell, no plugin | `pw.chromium.launch(channel="chromium")` | `AssertionError: channel= selects a shell other than the default one (D-03): ['browser_session.py:214']` |

## Admission guards seen red once (Task 2, before the one commit)

| Guard | Break | First failure line |
|---|---|---|
| `--ignore` in `test.fast` | removed | `test_verify_and_verify_fast_share_one_static_prefix_and_one_pytest_recipe`: `Extra items in the right set: 'tests/test_browser.py'` |
| `--ignore` in `test-image` | removed | `test_the_image_suite_ignores_the_browser_test`: `AssertionError: && python -m pytest -q -p no:cacheprovider "` |
| `-o` in the dry run (RESEARCH Pitfall P2) | `.venv/.browser` moved to `.venv/.browser.off` and `-o` dropped | the shared-prefix test: `Left contains 2 more items, first extra item: '.venv/bin/python -m playwright install  --only-shell chromium'` |
| `$(BROWSER)` as `test`'s prerequisite | `test: $(STAMP)` | `test_the_whole_gate_installs_the_browser_and_the_commit_slice_never_does`: `AssertionError: []`, `assert 0 == 1` |

All four restored byte-identical (`cmp` against copies kept in the scratchpad). The same seven rows are in `bench/RESULTS.md`.

## Readings (Apple M5 Max, macOS, 2026-10-10, load 4 to 10, HEAD `d0f5474`)

| Reading | Value |
|---|---|
| `make verify.fast`, three warm runs | 834 passed; real 10.14, 10.31, 10.41 s (L36 kill: 30 s) |
| Slice count check | 1226 collected, 392 in the five heavy files, 1226 - 392 = 834 |
| `tests/test_browser.py` at `-n 8`, ten runs | 10 of 10 passed; pytest 3.93 to 4.01 s, real 4.06 to 4.14 s |
| Missing shell at the final path | `1 failed in 0.61s`, the install command in the message |
| `make -n test \| grep -c 'playwright install'` | 0 fresh; 1 with `-W .venv/.installed`; `test.fast` 0 |
| `make verify` | `1226 passed in 192.08s (0:03:12)`, TOTAL 97.92 % against 96.0 %, real 192.51 s, load 6.33 to 6.76 |
| `make verify` before the commit, same tree | `1226 passed in 148.39s (0:02:28)`, real 148.82 s, load 4.66 to 10.48 |
| Host cache `~/Library/Caches/ms-playwright` | `chromium_headless_shell-1228`, `chromium-1228`, `ffmpeg-1011`, same as 21-01 |

The two `make verify` readings differ by 44 s on the same code; that is host load, not a measurement of the browser test. 21-07 prices the gate. The ten `-n 8` runs have one test function, so one of the eight workers runs it each time: the figure shows stability under the gate's worker setting, not eight copies side by side.

## Files Created/Modified

- `tests/test_browser_pins.py` - the three pins
- `tests/test_browser.py` - renamed from `tests/browser_scenarios.py`; only its docstring changed
- `tests/test_hooks.py` - `HEAVY_TEST_FILES`, `BROWSER_STAMP`, `-o` in `_dry_run`, two new pins
- `Makefile` - `test` prerequisite, both exclusions, "five heavy ones" in help texts and the `test.fast` comment, the `$(BROWSER)` comment
- `.github/workflows/ci.yml` - `BROWSER_INSTALL_ARGS: --with-deps` with its why-comment
- `.pre-commit-config.yaml` - five files in the header and the hook name
- `docs/architecture/web-ui.md` - `## Tests` says what the browser test proves and where it runs
- `.gitignore` - a comment beside `.venv/`
- `docs/tech_debt/active/2026-10-10-root-shape-bogus-loads-a-blank-select.md` - its pointer follows the rename
- `bench/RESULTS.md` - `### Admission (21-06)` and seven rows

## Decisions Made

- One admission commit, as the plan requires; the debt file's path correction rode in it because the rename caused it.
- The `63.555 s` and `~64 s` sentences are untouched (Phase 25 owns them); `grep -c 63.555` is 1 in the Makefile and in `.pre-commit-config.yaml`, as before.
- The comment in the `test.fast` block that says "the four `--ignore` flags below" is a dated snapshot of a measurement and was left as written.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Stale path in a debt file after the rename**
- **Found during:** Task 2
- **Issue:** `docs/tech_debt/active/2026-10-10-root-shape-bogus-loads-a-blank-select.md` named `tests/browser_scenarios.py`, which no longer exists
- **Fix:** pointed it at `tests/test_browser.py`
- **Files modified:** that one file
- **Committed in:** `d0f5474`

**2. [Rule 3 - Blocking] Two type and lint fixes in the new pins module**
- **Found during:** Task 1
- **Issue:** a 104-column line, and mypy's `"AST" has no attribute "lineno"` on a walk over mixed node types
- **Fix:** narrowed the node type before reading `lineno`; split the line
- **Files modified:** tests/test_browser_pins.py
- **Committed in:** `2b83400`

**3. [Plan departure] The pyproject.toml break moved the stamps**
- **Found during:** Task 1
- **Issue:** reverting the loose-pin break with `git checkout` left `pyproject.toml` newer than `.venv/.installed`, which would have made the next `make` re-run pip (with a network call) for byte-identical content
- **Fix:** after `git diff --exit-code` showed the file clean, touched `.venv/.installed`, `.venv/.hooks-installed` and `.venv/.browser` in that order. No install was skipped that the content required.

---

**Total deviations:** 3 (1 bug, 1 blocking, 1 departure). **Impact:** none on the product or the plan's outcome.

## Issues Encountered

- A first `git add` for the admission named `tests/browser_scenarios.py`, which was already staged as a rename, and failed with `fatal: pathspec ... did not match`. Nothing was committed; the second attempt without the old path made the one commit.
- No red gate or test run occurred, so there are no failed logs under `investigation/` and none to classify against the resource-tracker signature. No `filterwarnings` entry was added; `git diff 592506f -- pyproject.toml` still shows only the pin line.

## Known Stubs

None.

## Threat Flags

None. T-21-16 and T-21-17 are mitigated by the pins and the three `verify.fast` readings, and T-21-18 by the image pin, all seen red. T-21-19: `BROWSER_INSTALL_ARGS` is a literal in `ci.yml`; local hosts leave it empty.

## Debt filed

- `docs/tech_debt/active/2026-10-10-test-image-collects-tests-that-read-host-files.md` (nice), INDEX row added in `6f9ca66`. `make test-image` collects test files that read files the image lacks (`Dockerfile` for the new pins, `Makefile` and `.pre-commit-config.yaml` for `test_hooks.py`). ASSUMPTION: the image suite is already red on `test_hooks.py`; Docker was down, so it was not run.

## Flagged assumption carried

REQ-browser-stack-pinned's drift case is handled by `$(BROWSER)` depending on `$(STAMP)` and by re-taking PD-03's bar when the pin moves; no automated check re-measures the bar on a bump. Unchanged from the plan.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Ready for 21-07 (price the browser test inside the gate) and 21-08 (the `Lxx`, the idea retirement, the real runner run on the phase head). `bench/RESULTS.md` carries the effect on the commit slice, the `-n 8` stability and the fail-closed reading. The first CI run of `test (3.12)` with the admission is 21-08's, and the human pushes it.

## Self-Check: PASSED

- FOUND: tests/test_browser_pins.py, tests/test_browser.py, tests/test_hooks.py, Makefile, .github/workflows/ci.yml, bench/RESULTS.md (`### Admission (21-06)`, seven `| 21-06` rows); tests/browser_scenarios.py is gone
- FOUND: commits `2b83400`, `d0f5474`, `1943f8e`, `6f9ca66` on `gsd/phase-21-browser-test-of-the-viewer`
- Task 2 acceptance criteria re-run: all pass. Task 3's RESULTS.md check script printed `admission recorded; verify.fast max 10.41`; `make -n test | grep -c 'playwright install'` prints 0; `git diff --exit-code 592506f` over the fixture, `tests/test_api.py` and the product modules exits 0

---
*Phase: 21-browser-test-of-the-viewer*
*Completed: 2026-10-10*
