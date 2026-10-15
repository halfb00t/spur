---
phase: 22-download-name-carries-the-root
plan: 01
subsystem: api
tags: [slug, content-disposition, root-mode, trochoid, playwright, decision-log]

requires:
  - phase: 19-hob-cut-trochoid-root
    provides: "root_mode(), the one predicate for whether the hob root applies (L38)"
  - phase: 21-browser-test-of-the-viewer
    provides: "the headless-shell scenario, step(), BUILD_WAIT_MS and serve_stl_from (L39)"
provides:
  - "GearParams.slug() ends _trochoid exactly when root_mode builds the hob root"
  - "whole-header pins for STL and STEP at 23 and 40 teeth, six pure slug rows, two build.failed name rows"
  - "a browser step that clicks #dl-stl and reads suggested_filename"
  - "L40 with every consumer of the old names read at the parent commit"
affects: [22-02, download-name, records, http-api]

plan_head_before: 5769ac02891af42071248a01dfca1a5c8c74f1c8
plan_head_after: e3b1181deab3f6b09c36a771026899e24ab0b0e5
actuals:
  tokens: 6093
  tasks: 3
  commits: 1

tech-stack:
  added: []
  patterns:
    - "one definition, many callers: the suffix reaches the header, the records and the temp stem through slug() alone"
    - "local import of calc inside a GearParams method (the _feasible pattern)"

key-files:
  created:
    - docs/ideas/retired/2026-10-08-download-name-carries-the-root-shape.md
  modified:
    - src/spur/params.py
    - src/spur/calc.py
    - tests/test_api.py
    - tests/test_browser.py
    - tests/browser_session.py
    - tests/test_trochoid.py
    - docs/architecture/http-api.md
    - docs/architecture/decision_log.md
    - docs/ideas/INDEX.md
    - .planning/REQUIREMENTS.md
    - .planning/ROADMAP.md

key-decisions:
  - "L40: the download name follows the root root_mode builds, not the root asked for; a refused or ignored request keeps the plain name"
  - "slug() has no guard around root_mode; totality is shown by rows and a 17,567-case sweep, not by a fallback"
  - "docs/http-api.md in REQUIREMENTS and the roadmap is docs/architecture/http-api.md; corrected in the same commit"

patterns-established:
  - "A filename pin is a literal, written with the whole Content-Disposition value"

requirements-completed: [REQ-slug-carries-effective-root, REQ-slug-consumers-read-first]

coverage:
  - id: D1
    description: "A 23-tooth root_shape=trochoid part downloads as spur_z23_m1.75_pa25_trochoid in STL and STEP headers"
    requirement: REQ-slug-carries-effective-root
    verification:
      - kind: integration
        ref: "tests/test_api.py#test_the_download_name_carries_the_root_the_part_has"
        status: pass
    human_judgment: false
  - id: D2
    description: "A real click on #dl-stl in the headless shell saves spur_z23_m1.75_pa25_trochoid.stl"
    requirement: REQ-slug-carries-effective-root
    verification:
      - kind: automated_ui
        ref: "tests/test_browser.py#test_the_shipped_viewer_in_a_real_browser (step download name)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Ignored (27, 40 teeth) and refused (tip land gone) requests keep today's plain name, and slug() never raises"
    requirement: REQ-slug-carries-effective-root
    verification:
      - kind: unit
        ref: "tests/test_trochoid.py#test_the_download_name_follows_the_root_root_mode_builds"
        status: pass
      - kind: integration
        ref: "tests/test_api.py#test_a_failed_build_records_the_name_of_the_part_it_would_have_been"
        status: pass
    human_judgment: false
  - id: D4
    description: "L40 lists every consumer of the old names, shows no cache is keyed by slug, and the idea is retired in the same commit"
    requirement: REQ-slug-consumers-read-first
    verification:
      - kind: other
        ref: "Task 3 verify commands (L40 item check, retirement check, commit slice check)"
        status: pass
    human_judgment: true
    rationale: "Whether L40 reads as an adequate decision record is a reviewer's call; the checks prove the cited items are present"

duration: 12min
completed: 2026-10-11
status: complete
---

# Phase 22 Plan 01: Download Name Carries the Root Summary

**`GearParams.slug()` appends `_trochoid` exactly when `calc.root_mode` builds the hob root, pinned by header, pure, record and real-browser tests, with L40 listing every consumer of the old names**

## Performance

- **Duration:** about 12 min (start taken from STATE.md's phase-start stamp 06:13Z; no start time was recorded by the executor)
- **Started:** approx. 2026-10-11T06:13Z
- **Completed:** 2026-10-11T06:26Z
- **Tasks:** 3
- **Files modified:** 12 in the feature commit (11 modified, 1 renamed)

## Accomplishments

- One method changed in production. `slug()` calls `root_mode(self, profile(self), requested=self.root_shape, rho=self.root_fillet)` through a local import and appends `_trochoid` when `.mode == "trochoid"`. `app.py`, `records.py`, `model.py`, `cli.py`, `pool.py` and `app.js` are byte-identical to the base.
- A 23-tooth hob-root part downloads as `spur_z23_m1.75_pa25_trochoid.{stl,step}`; 40 teeth (ignored) and the radial parts keep `spur_z40_m1.75_pa25` and `spur_z23_m1.75_pa25`. The radial-default pin (`spur_z21_m1.75_pa25.{fmt}`) is untouched.
- `slug()` stays total: no `try`, six pure rows (default, 23, 26, 27, 40, tip-land refused), two `build.failed` name rows, and a one-off sweep over the real function.
- The browser scenario gained a `download name` step that clicks `#dl-stl` on its own page and reads `suggested_filename`.
- L40 records the rule, totality, cost, all 33 grep lines at the parent commit, the cache keys, the browser proof, the doc-path correction, reversibility (costly) and a `Machine:` line. The idea is retired in the same commit.

## Task Commits

Per the plan's PD-01 and D-11, Tasks 1 and 2 built and verified the working tree and did not commit; Task 3 made the one commit.

1. **Tasks 1-3 (tracer, totality, record)** - `e3b1181` (feat): `feat(22): a hob-root part downloads as _trochoid -- log L40 and retire the download-name idea`

**BASE (parent of the commit, the tree the consumers were read from):** `5769ac0`
**Plan metadata:** the docs commit that carries this SUMMARY, STATE.md, ROADMAP.md and REQUIREMENTS.md

## TDD Gate Compliance

The plan is `type: execute` with `tdd="true"` on Task 2 only, and PD-01/D-11 require one commit, so there is no separate `test(22-01)` / `feat(22-01)` pair. Red-then-green was done in the working tree and each red is recorded below with its first failure line; the single commit holds tests and implementation together by the plan's own instruction.

## Seen red

Each pin was run red before the code it pins existed (or while the rejected rule was in place), then reverted or turned green. The first failure line of each:

1. **Header pins and the flipped root-shape test, against the unchanged `slug()`** (Task 1 step 4).
   Command: `make test PYTEST_ARGS="tests/test_api.py -n0 --no-cov -q --tb=line -k 'download_name or root_shape_link'"`.
   Result `3 failed, 2 passed` (the two 40-tooth rows pass). First failure line (`tests/test_api.py:414`, the root-shape test):
   `assert 'attachment; ....75_pa25.stl"' == 'attachment; ...trochoid.stl"'`. The other two are the 23-tooth STL and STEP rows at `:744` with the same shape, `.stl` and `.step`.
2. **Browser step, against the unchanged `slug()`** (Task 1 step 4).
   Command: `make test PYTEST_ARGS="tests/test_browser.py -n0 --no-cov -q -s"` (log: `investigation/22-01-browser-red.log`).
   `1 failed`; first failure line: `AssertionError: the download is named 'spur_z23_m1.75_pa25.stl', not the name the server gives this part`, note `step: download name`, `tests/test_browser.py:581`.
3. **Pure rows, under the rejected requested-root rule** (Task 2 step 3; the condition in `slug()` changed to `self.root_shape == "trochoid"` for one run, then restored).
   Command: `make test.fast PYTEST_ARGS="tests/test_trochoid.py -n0 -q --tb=line -k download_name_follows"`.
   `3 failed, 3 passed` (`27-ignored-first`, `40-ignored`, `tip-land-gone-refused`). First failure line (`tests/test_trochoid.py:234`): `AssertionError: assert ('nothing rad...a25_trochoid') == ('nothing rad...7_m1.75_pa25')`.
4. **`build.failed` name row, under the same rejected rule.**
   Command: `make test PYTEST_ARGS="tests/test_api.py -n0 --no-cov -q --tb=line -k failed_build_records_the_name"`.
   `1 failed, 1 passed` (`refused`). First failure line (`tests/test_api.py:1147`): `AssertionError: assert 'spur_z19_m1....33.5_trochoid' == 'spur_z19_m1.75_pa33.5'`.

After the restore, the AST check printed `slug(): local calc import, root_mode on the request, no guard`.

## Readings

All on Apple M2 Max, 12 CPUs, 32 GiB, macOS 27.0.1, Python 3.12.13, playwright 1.63.0, Chrome Headless Shell 153.0.8010.12, 2026-10-11, load average 5 to 6.5 (`uptime`).

**`slug()` cost** (timeit, best of 5 x 2000; `uptime` before and after read `load averages: 6.53 6.19 4.99`):

| Case | Name | us per call |
|---|---|---|
| radial default | `spur_z19_m1.75_pa25` | 2.3 |
| 40 teeth, ignored | `spur_z40_m1.75_pa25` | 5.0 |
| tip land gone, refused | `spur_z19_m1.75_pa33.5` | 5.2 |
| 23 teeth, hob root applies | `spur_z23_m1.75_pa25_trochoid` | 37.8 |

The old f-string alone: 0.32 us (best of 5 x 20000). These went into `slug()`'s docstring and L40.

**Totality sweep** (`bench.trochoid.sweep_cases()`, `root_shape="trochoid"`, each case's `root_fillet`):
`17567 valid trochoid requests named, 9954 of them _trochoid, none raised`.

**Browser step** (`investigation/22-01-browser-green.log`, `-n0 --no-cov -s`, `1 passed in 6.28s`):

```
step first build drawn: 2.93 s
download name: spur_z23_m1.75_pa25_trochoid.stl, click to download 0.12 s
step download name: 1.13 s
```

The red run read `step first build drawn: 3.03 s` and `step download name: 1.13 s`. Both are far under PD-11's 15 s. 22-02 takes the three readings on the committed head.

## Consumer grep (L40's list, PD-02)

`git grep -n -I -w -E 'slug|spur_z[0-9]+|[Cc]ontent-[Dd]isposition' 5769ac0 -- src bench docs tests README.md .github ':!docs/tech_debt/resolved'` returned 33 lines, exactly the planned list; none was new:

```
bench/export_cost.py:176          Path(d) / f"{params.slug()}.stl"
docs/HOW_TO_DEVELOP.md:62, 87, 256, 257   branch- and file-name templates (unrelated)
docs/architecture/http-api.md:43, 93      the header row; records paragraph (rewritten)
docs/ideas/2026-10-08-download-name-carries-the-root-shape.md:6, 7, 8, 12, 29, 30   the idea (retired)
docs/ideas/INDEX.md:4, 19         template text; the idea's row (moved)
docs/review-2026-09-21.md:13      frozen history
src/spur/app.py:496               the Content-Disposition header
src/spur/model.py:807             temp export stem
src/spur/params.py:190            the definition
src/spur/records.py:172, 180      _gear_fields
tests/test_api.py:376, 411, 412, 720, 797, 985, 1086, 1123
tests/test_model.py:2021          temp stem
tests/test_records.py:60, 89, 95  synthetic "spur_z19"
```

## Gate

- `make verify` on the tree as committed (nothing but the orchestrator's STATE.md and state.json differ from `HEAD`, and `git diff HEAD` over everything else is empty): **`1238 passed in 264.62s (0:04:24)`**, `TOTAL 1349 22 384 14 97.92%`, `Required test coverage of 96.0% reached. Total coverage: 97.92%`, `make verify exit 0`. Log: `.planning/phases/22-download-name-carries-the-root/investigation/22-01-verify.log`.
- The pre-commit hook ran `make verify.fast` and passed.
- `git diff --exit-code` on `tests/regression/pre_v0_2.json` and `tests/regression/golden_requests.json`: empty, both before and across the commit.
- Task 3's three verify blocks passed, with one deliberate exception: the final block's `test -z "$(git status --porcelain --untracked-files=no)"` cannot hold until the docs commit, because STATE.md and state.json carry the orchestrator's phase-start edits, which this plan does not own. Every other clause of that block passed.

## Files Created/Modified

- `src/spur/params.py` - `slug()` appends `_trochoid` from `root_mode`; docstring carries the four measured figures
- `src/spur/calc.py` - `root_mode`'s docstring names `GearParams.slug()` as a caller (docstring only, proved by AST comparison)
- `tests/test_api.py` - four header rows, the flipped root-shape pins, two `build.failed` name rows
- `tests/test_trochoid.py` - six pure `slug()` rows
- `tests/test_browser.py` - the `download name` step and a module-docstring line
- `tests/browser_session.py` - `serve_stl_from` docstring scoped to pages that carry the route
- `docs/architecture/http-api.md` - the rule at the `model.{stl,step}` row and in the records paragraph
- `docs/architecture/decision_log.md` - `## L40`
- `docs/ideas/INDEX.md`, `docs/ideas/retired/2026-10-08-download-name-carries-the-root-shape.md` - idea retired, row moved
- `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md` - `docs/http-api.md` corrected to `docs/architecture/http-api.md` (1 line and 2 lines)
- Kept logs, untracked, for 22-02 to commit: `investigation/22-01-browser-red.log`, `22-01-browser-green.log`, `22-01-verify.log`

## Decisions Made

None beyond the plan. L40 is the plan's decision recorded; PD-01 to PD-12 were followed as written.

## Deviations from Plan

### Precondition not met as written

**1. [Precondition] `git status --porcelain --untracked-files=no` was not empty at the start of Task 1**
- **Found during:** Task 1 precondition
- **Issue:** `.planning/STATE.md` and `.planning/state.json` carried the orchestrator's uncommitted phase-start bookkeeping (status `executing`, `state_head`, `last_activity`), and `.planning/milestone.lock` was untracked. The dispatch prompt named all three and said not to revert them.
- **Resolution:** I read `git diff` on both tracked files to confirm they hold only that bookkeeping, then went on. The precondition's purpose is that no stray work reaches the one commit; I staged files explicitly, and the commit holds exactly the 11 modified files and the rename the plan lists. The orchestrator's two files are committed in the docs commit that follows, and `milestone.lock` is not committed.
- **Note for review:** this is a judgement call on a literal reading of the precondition. The second half of the precondition (the headless shell) was met by running `make .venv/.browser` (14.8 s), as Task 1 step 0 directs.

### Auto-fixed Issues

None.

---

**Total deviations:** 1 (precondition interpreted, no code impact)
**Impact on plan:** none on the code or the commit slice.

## Issues Encountered

None. No red outside the planned reds, no resource-tracker flake, no hang in `make verify`.

## Known Stubs

None.

## Threat Flags

None. The new surface is the filename built from validated fields plus the literal `_trochoid`; T-22-01 to T-22-05 are covered as planned.

## Debt and ideas filed

No debt item was filed. No new idea was filed. One idea was retired (`docs/ideas/retired/2026-10-08-download-name-carries-the-root-shape.md`).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

22-02 starts from a clean commit `e3b1181` and takes D-06's three timed readings of the `download name` step, writes `bench/RESULTS.md` `## Download name carries the root (Phase 22)` (copying the four Seen red lines above into `### Seen red once (Phase 22)`), commits the `investigation/` logs, and edits the `BUILD_WAIT_MS` comment in `tests/browser_session.py`, which this plan left alone on purpose. L40 already cites that `bench/RESULTS.md` section. The step read 1.13 s here, so nothing suggests `BUILD_WAIT_MS` moves; ubuntu-latest (A2, A3) is read at the pull request's first CI run.

## Self-Check: PASSED

- FOUND: `src/spur/params.py`, `tests/test_trochoid.py`, `tests/test_browser.py`, `docs/ideas/retired/2026-10-08-download-name-carries-the-root-shape.md`, the three `investigation/22-01-*.log` files
- FOUND: commit `e3b1181` is an ancestor of HEAD, and `git rev-list --count 5769ac0..HEAD` read 1 before this docs commit

---
*Phase: 22-download-name-carries-the-root*
*Completed: 2026-10-11*
