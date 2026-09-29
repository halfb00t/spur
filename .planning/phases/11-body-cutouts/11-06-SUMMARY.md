---
phase: 11-body-cutouts
plan: 06
subsystem: validation
tags: [pydantic, cadquery, bench, tdd, build-timeout]

# Dependency graph
requires:
  - phase: 11-03, 11-04, 11-05
    provides: hole cutout, spoke cutout and honeycomb cutout patterns, each with its own
      check() rules and HEX_CELL_CAP (11-05)
provides:
  - Measured build/export time for every body cutout pattern at its heaviest allowed
    configuration (ROADMAP SC5)
  - D-18's over-budget gate exercised for real: four rows (one hole, three spoke) and one
    honeycomb over-share row measured over budget, recorded verbatim, never re-picked
  - The human's decision applied: spoke_count le 200 -> 40, hole_count le 200 -> 60,
    HEX_CELL_CAP unchanged at 120
  - Both sweeps re-run at the new le, every row inside SPUR_BUILD_TIMEOUT=30s
affects: [12-composed-sweep]

# Actuals (#2632)
actuals:
  tokens: 10400
  tasks: 3
  commits: 4

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "A count field's le is a measured bound, re-derived from a bench sweep and a
      human decision at D-18's gate, not picked by inspection (08 D-07's precedent
      continued into Phase 11)"

key-files:
  created:
    - bench/sweeps/hole_cutout.json
    - bench/sweeps/spoke_cutout.json
    - bench/sweeps/honeycomb.json
    - docs/tech_debt/active/2026-09-29-spoke-le-arithmetic-total-crosses-30s-under-load.md
  modified:
    - src/spur/params.py
    - tests/test_calc.py
    - tests/test_api.py
    - tests/test_bench.py
    - bench/RESULTS.md
    - docs/tech_debt/INDEX.md

key-decisions:
  - "D-18's gate fired: 200-count hole and spoke rows crossing a recess groove measured
    41.85 s and 65.70-68.70 s of SPUR_BUILD_TIMEOUT=30 s; the honeycomb's cap-row measured
    8.65 s against D-11's own 7.5 s share (inside the 30 s absolute timeout)."
  - "Human decision (verbatim, accepting the orchestrator's recommendation): lower-le --
    spoke_count le 200->40, hole_count le 200->60 (D-18's first offer, one published bound
    per count, same on every gear); honeycomb 'none needed' -- HEX_CELL_CAP stays 120, the
    8.65 s reading accepted as measured under host load 5-10, comparable to 11-02's own
    7.25 s reading under similar load. Rationale: the recess-crossing cost is geometric
    and near-linear (~0.33 s/sector, ~0.21 s/hole on the worst rows, loaded host); 200
    arms at 0.4 mm is not a part anyone cuts; 40 spokes and 60 holes each stack on Phase
    12's 14.87 s tip-chamfer row with margin under the same load; a count-rule would
    reintroduce the field-dependent limit D-07/D-12 avoided for configurations nobody
    needs."
  - "The sweep JSON files were committed in the feat commit alongside params.py and the
    tests, not in the docs commit the plan named -- the pre-commit make verify hook reads
    the sweeps through load_sweep, so splitting them from the le change leaves an
    intermediate commit where the sweep does not validate (Rule 3 deviation)."
  - "The re-run's arithmetic total (heaviest spoke row + Phase 10's tip-chamfer row) reads
    33.39 s, over 30 s, measured under this run's exceptional load (32.17) -- filed as
    must-severity debt rather than rounded away or silently accepted, since it does not
    match the decision's ~2 s margin expectation exactly."

patterns-established:
  - "Pattern: a bench sweep's field-boundary pin (row sits exactly one step from a
    refusal) is re-verified live after a count-field bound changes -- some boundaries are
    count-independent (a fixed wall) and survive; others are count-dependent (a
    neighbour/hub-opening gap) and do not. Checked by measurement, not assumed either way."

requirements-completed: [REQ-hole-cutout, REQ-spoke-cutout, REQ-honeycomb-cutout]

coverage:
  - id: D1
    description: "Three committed sweep files (hole, spoke, honeycomb) run through
      bench/build_time.py unchanged, pinned in tests/test_bench.py"
    requirement: REQ-hole-cutout
    verification:
      - kind: unit
        ref: "tests/test_bench.py#test_the_hole_cutout_sweep_is_every_combination_the_plan_names"
        status: pass
      - kind: unit
        ref: "tests/test_bench.py#test_the_spoke_cutout_sweep_is_every_combination_the_plan_names"
        status: pass
      - kind: unit
        ref: "tests/test_bench.py#test_the_honeycomb_sweep_runs_at_the_cap"
        status: pass
    human_judgment: false
  - id: D2
    description: "bench/RESULTS.md records all 24 first-run rows, the heaviest per
      pattern, the SPUR_BUILD_TIMEOUT margin and the Gate's list, exactly as measured"
    requirement: REQ-measured-build-time
    verification:
      - kind: other
        ref: "sed -n '/^## Body cutout build and export time/,$p' bench/RESULTS.md | grep -c '^\\*\\*Heaviest:\\*\\*'"
        status: pass
    human_judgment: false
  - id: D3
    description: "D-18's gate decision recorded verbatim and applied: hole_count/
      spoke_count le lowered to 60/40 with field comments citing the measured row;
      bound tests, schema-maximum tests and the sweep pins updated to match"
    requirement: REQ-spoke-cutout
    verification:
      - kind: unit
        ref: "tests/test_calc.py#test_the_hole_count_is_an_integer_from_0_to_60"
        status: pass
      - kind: unit
        ref: "tests/test_calc.py#test_the_spoke_count_is_an_integer_from_0_to_40"
        status: pass
      - kind: integration
        ref: "tests/test_api.py#test_a_hole_link_is_served_with_its_walls"
        status: pass
      - kind: integration
        ref: "tests/test_api.py#test_a_spoke_link_is_served_with_the_fillet_it_cut"
        status: pass
    human_judgment: false
  - id: D4
    description: "Both affected sweeps re-run at the new le on a live host; every row
      reads inside SPUR_BUILD_TIMEOUT=30 s; the re-run appended below the first run
      without overwriting it"
    requirement: REQ-spoke-cutout
    verification:
      - kind: other
        ref: "make bench.build SWEEP=bench/sweeps/hole_cutout.json (exit 0, all rows yes)"
        status: pass
      - kind: other
        ref: "make bench.build SWEEP=bench/sweeps/spoke_cutout.json (exit 0, all rows yes)"
        status: pass
    human_judgment: false
  - id: D5
    description: "The re-run's arithmetic total against Phase 10's tip-chamfer row
      (33.39 s) is honestly recorded as over 30 s under this run's load, not rounded to
      match the decision's ~2 s margin expectation, and filed as debt for Phase 12"
    verification: []
    human_judgment: true
    rationale: "Whether a single loaded-host arithmetic reading warrants revisiting the
      le decision, versus waiting for Phase 12's real composed measurement, is a project
      priority call, not something a test can settle."

# Metrics
duration: ~45min (Task 3 this session; Task 1's sweeps and first run were a prior
  executor's ~15min, per the checkpoint continuation)
completed: 2026-09-29
status: complete
---

# Phase 11 Plan 06: Body Cutout Build-Time Gate Summary

**D-18's over-budget gate fired for real on 200-count hole and spoke rows crossing a
recess groove; the human lowered `hole_count`'s and `spoke_count`'s `le` to 60 and 40,
and the re-run measured every row of both sweeps back inside `SPUR_BUILD_TIMEOUT`.**

## Performance

- **Duration:** ~45 min this session (Task 3 only -- Task 1's sweeps, pins and first
  bench run were completed and committed by a prior executor before this session's
  checkpoint continuation)
- **Completed:** 2026-09-29T08:52Z
- **Tasks:** 3 (Task 1: sweeps + first run, by the prior executor; Task 2: human decision,
  a checkpoint with no code; Task 3: applied the decision + re-run, this session)
- **Files modified:** 6 modified, 4 created (3 sweep JSON files + 1 tech-debt item) across
  the plan's 4 commits

## Accomplishments

- Three sweep files (hole, spoke, honeycomb) measured 24 rows at their heaviest allowed
  configurations, all recorded in `bench/RESULTS.md` "## Body cutout build and export time
  (Phase 11)" -- the honest first run, including the four rows and one honeycomb row that
  overran, never dropped or re-picked
- D-18's gate ran for real: the human accepted the orchestrator's recommendation
  (`lower-le: spoke_count 40, hole_count 60`; honeycomb `none needed`, `HEX_CELL_CAP`
  unchanged at 120)
- `src/spur/params.py`'s `spoke_count` and `hole_count` `le` lowered from 200 to 40 and
  60, each with a field comment citing the measured row and D-18; every dependent test
  (bound tests, schema-maximum tests, sweep pins) updated to match, including two sweep
  pins whose refusal-boundary assertion no longer held at the lower count (measured, not
  assumed) and was dropped or narrowed accordingly
- Both affected sweeps re-generated at the new `le` and re-run through
  `make bench.build`: every row of both sweeps now reads inside 30 s, appended to
  `bench/RESULTS.md` below the first run without overwriting it

## Task Commits

Task 1 (prior executor, this session's inherited state):
1. **Task 1a: sweeps + pins** - `e908b29` (test)
2. **Task 1b: first bench run recorded** - `9d523b5` (docs)

Task 3 (this session):
3. **Task 3a: apply the decision (le lowered, tests updated, sweep files re-generated)** -
   `2224697` (feat)
4. **Task 3b: re-run recorded** - `f290860` (docs)

_Note: Task 3's own RED/GREEN cycle (rename the bound tests and schema-maximum
assertions to the new `le`, confirm the intentional failure, then lower `le` in
`params.py` to green) ran inside the `feat` commit -- workflow.tdd_mode is not enabled in
config.json (11-03/11-04/11-05's precedent), so the mechanical RED/GREEN/REFACTOR
commit-pattern gate does not apply; RED was still run and confirmed failing for the right
reason (schema maximum and field-level ValidationError assertions, not an unrelated
error) before GREEN was written._

## Files Created/Modified
- `bench/sweeps/hole_cutout.json` - 8 rows, `hole_count` now 60 (was 200)
- `bench/sweeps/spoke_cutout.json` - 8 rows, `spoke_count` now 40 (was 200)
- `bench/sweeps/honeycomb.json` - 8 rows at `HEX_CELL_CAP`, unchanged by this task
- `src/spur/params.py` - `hole_count` le 60, `spoke_count` le 40, each with a
  measurement-citing comment
- `tests/test_calc.py` - bound tests renamed and re-pinned to the new `le`
- `tests/test_api.py` - schema `maximum` assertions updated to 60/40
- `tests/test_bench.py` - sweep pins updated; refusal-boundary assertions re-verified
  live and adjusted where they no longer held
- `bench/RESULTS.md` - the Gate section's last line names the decision; a new
  "### Re-run after the gate (lower-le)" subsection with both re-run tables
- `docs/tech_debt/active/2026-09-29-spoke-le-arithmetic-total-crosses-30s-under-load.md` -
  new must-severity item (see Deviations)
- `docs/tech_debt/INDEX.md` - one row added

## Decisions Made

**The Gate list (first run, exactly as measured):**

| Row | Build + slower export | Inside 30 s / 7.5 s |
|---|---|---|
| module=1.75 hole_count=200 hole_d=1 hole_circle_d=183.4 recess=both | 41.85 s | **NO** (30 s) |
| module=1.75 spoke_count=200 spoke_width=0.4 hub_d=52 rim_wall=0.4 recess=both | 65.70 s | **NO** (30 s) |
| module=10 spoke_count=200 spoke_width=0.4 hub_d=52 rim_wall=0.4 recess=both | 68.70 s | **NO** (30 s) |
| module=10 spoke_count=200 spoke_width=5.85 hub_d=400 rim_wall=100 recess=both | 66.67 s | **NO** (30 s) |
| module=1.75 hex_cell=3 hex_wall=0.4 recess=both | 8.65 s | **NO** (7.5 s honeycomb share; inside the 30 s absolute) |

**The human's answer, verbatim:** "let's go with the recommendation" -- `lower-le:
spoke_count 40, hole_count 60`; honeycomb `none needed`.

**The re-run's heaviest row per affected pattern:**

| Pattern | Heaviest row | Time | Margin |
|---|---|---|---|
| Holes (le 60) | module=1.75 hole_count=60 hole_d=1 hole_circle_d=183.4 recess=both | 11.79 s | 2.54x of 30 s |
| Spokes (le 40) | module=10 spoke_count=40 spoke_width=0.4 hub_d=52 rim_wall=0.4 recess=both | 18.52 s | 1.62x of 30 s |

**Room beside Phase 10's 14.87 s tip-chamfer row (arithmetic only, Phase 12 measures the
real composition):** heaviest hole re-run + 14.87 s = 26.66 s (3.34 s inside 30 s).
Heaviest spoke re-run + 14.87 s = 33.39 s -- **3.39 s over 30 s**, not the ~2 s margin the
gate's decision anticipated from the planning estimate. This reading was taken under the
heaviest host load recorded anywhere in this project's bench history (32.17 at start, vs.
the first run's own 5-10) -- plausibly inflated, not proof the margin is actually negative
at a quiet load, but real enough at this reading to record rather than round away (L08).
Filed as `docs/tech_debt/active/2026-09-29-spoke-le-arithmetic-total-crosses-30s-under-load.md`
(must), not fixed here -- Task 3's own scope is the `le`, not a new build-time guarantee
on an arithmetic sum Phase 12 measures for real.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Sweep JSON files moved into the `feat` commit, not the `docs`
commit the plan named**
- **Found during:** Task 3, first commit attempt
- **Issue:** The plan's action text asks for two commits -- source+tests, then
  `bench/RESULTS.md` with the sweep files. Committing source+tests alone first triggers
  the pre-commit `make verify` hook's full `pytest` run, which stashes the still-unstaged
  sweep JSON files (still at `hole_count`/`spoke_count` 200) while `params.py`'s `le` is
  already lowered to 60/40 in the staged tree -- `load_sweep` then raises a
  `ValidationError` reading the stashed sweep, failing the hook and blocking the commit.
- **Fix:** Staged the two sweep JSON files alongside `params.py` and the three test files
  in the first (`feat`) commit instead. The second (`docs`) commit is `bench/RESULTS.md`
  plus the new tech-debt item and its INDEX row, as the plan named.
- **Files modified:** `bench/sweeps/hole_cutout.json`, `bench/sweeps/spoke_cutout.json`
  (moved from the intended second commit into the first)
- **Verification:** `git commit` succeeded with the pre-commit hook's `make verify`
  passing (304 tests, lint, mypy, import contracts) on the first attempt after the fix
- **Committed in:** `2224697`

**2. [Rule 2 - Missing Critical] Filed a must-severity tech-debt item for the re-run's
arithmetic-total gap against Phase 10's tip-chamfer row**
- **Found during:** Task 3, after the re-run
- **Issue:** The re-run's heaviest spoke row (18.52 s) plus Phase 10's 14.87 s tip-chamfer
  row totals 33.39 s, over `SPUR_BUILD_TIMEOUT`, not matching the accepted decision's ~2 s
  margin expectation -- CLAUDE.md's standing rule (a number the tool would print is a
  number someone cuts metal to) and CODING_VALUES.md's "measure before you claim" both
  require recording this rather than letting the "~2 s margin" rationale stand unverified
  in the SUMMARY without the actual reading beside it.
- **Fix:** Recorded the honest arithmetic (11.79 s hole re-run fits with margin; 18.52 s
  spoke re-run does not) in `bench/RESULTS.md`'s new subsection and filed
  `docs/tech_debt/active/2026-09-29-spoke-le-arithmetic-total-crosses-30s-under-load.md`
  (must, with the load caveat and a named trigger: Phase 12's composed sweep, or a
  quiet-host re-measurement), added its INDEX row.
- **Files modified:** `docs/tech_debt/active/2026-09-29-spoke-le-arithmetic-total-crosses-30s-under-load.md`
  (new), `docs/tech_debt/INDEX.md`
- **Verification:** File follows `docs/tech_debt/TEMPLATE.md`'s shape; INDEX row added in
  the same commit as the fix (CLAUDE.md's own rule for filing debt)
- **Committed in:** `f290860`

---

**Total deviations:** 2 auto-fixed (1 blocking commit-ordering fix, 1 missing-critical
debt filing). **Impact on plan:** Both are process/documentation fixes, not scope
creep -- neither changes the human's decision or the applied `le` values.

## Issues Encountered

None beyond the two deviations above, which are documented there rather than repeated
here.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Phase 11's three body cutout patterns (holes, spokes, honeycomb) are all measured,
  bounded and inside `SPUR_BUILD_TIMEOUT` on their own -- ready for whatever plan writes
  L30 (11-09, per bench/RESULTS.md's own cited key_link) and closes out the phase.
- Phase 12's composed sweep (module x every Phase 8-11 feature) should specifically
  include a spoke-heavy + tip-chamfer-heavy combination, given the arithmetic gap this
  plan surfaced (see the filed tech-debt item's Next step).
- `docs/tech_debt/active/2026-09-29-spoke-le-arithmetic-total-crosses-30s-under-load.md`
  is open (must); no other new blockers.

---
*Phase: 11-body-cutouts*
*Completed: 2026-09-29*

## Self-Check: PASSED

- Created files on disk: `bench/sweeps/hole_cutout.json`, `bench/sweeps/spoke_cutout.json`,
  `bench/sweeps/honeycomb.json`, `docs/tech_debt/active/2026-09-29-spoke-le-arithmetic-total-crosses-30s-under-load.md`
  — all `FOUND`
- Modified files on disk: `src/spur/params.py`, `bench/RESULTS.md` — both `FOUND`
- Commits present in `git log --oneline --all`: `e908b29`, `9d523b5`, `2224697`,
  `f290860` — all `FOUND`
- Acceptance criteria re-run: sweep row counts `[8, 8, 8]`; 40 measured-row lines and 5
  `**Heaviest:**` lines under the Phase 11 section (24 first-run + 16 re-run rows, 3
  first-run heaviest + 2 re-run heaviest); all six `###`-heading counts read 1 inside the
  section; `git diff --numstat b86a0e9 -- bench/RESULTS.md` reports 0 deleted lines;
  `git diff --quiet b86a0e9 -- bench/build_time.py Makefile` exits 0
- Plan-level verification re-run: `make test PYTEST_ARGS="tests/test_calc.py
  tests/test_api.py tests/test_bench.py tests/regression -q"` — 304 passed;
  `git diff --exit-code tests/regression/pre_v0_2.json` — fixture byte-unchanged;
  `make lint typecheck` — both clean
