---
phase: 10-tooth-tip-chamfer
plan: 04
subsystem: bench
tags: [cadquery, chamfer, benchmarking, build-time, tech-debt]

requires:
  - phase: 10-tooth-tip-chamfer
    provides: "10-02's tip_chamfer field and cap, 10-03's proven selector and cut --
      this plan measures the shipped feature's cost, not a probe path"
provides:
  - "bench/sweeps/tip_chamfer.json: D-06's 9-row sweep at 200 teeth, pinned by a
    cross-product test where each largest chamfer sits exactly on its limit"
  - "bench/RESULTS.md '## Tooth-tip chamfer build and export time (Phase 10)': all 9
    rows, host state with its load caveat, the named heaviest row, the
    SPUR_BUILD_TIMEOUT margin and the phase's make verify wall time"
  - "docs/tech_debt/active/2026-09-28-tip-chamfer-narrows-the-build-timeout-margin.md:
    must-severity debt recording the heaviest row leaves only ~2.0x of the 30s
    timeout's margin, half the 4x it was set by"
affects: [10-05]

actuals:
  tokens: 3447
  tasks: 2
  commits: 2
  plan_head_before: 834e764511f1c11217b7c49626182a3632faaa76
  plan_head_after: bbe888f2a715fcf09c99f737cefd37dde864fceb

tech-stack:
  added: []
  patterns:
    - "A sweep file plus one cross-product test is the whole deliverable -- no code
      changes; bench/build_time.py and the Makefile are reused unchanged (08 D-12),
      continuing Phase 8/9's shape."

key-files:
  created:
    - bench/sweeps/tip_chamfer.json
    - docs/tech_debt/active/2026-09-28-tip-chamfer-narrows-the-build-timeout-margin.md
  modified:
    - tests/test_bench.py
    - bench/RESULTS.md
    - docs/tech_debt/INDEX.md

key-decisions:
  - "The debt item's 7.5s trigger is not a new budget -- it is the 4x margin
    bench/RESULTS.md's own SPUR_BUILD_TIMEOUT section gave for the 30s default (A1,
    10-04-PLAN.md's Flagged Assumptions). The heaviest row (14.87s) crossed it, so the
    item was filed rather than treated as a judgment call."
  - "D-07's over-budget checkpoint never fired: all 9 rows stayed inside 30s on the
    first run (heaviest 14.87s), so no human decision was needed on the field's le or
    a teeth-dependent cap."

requirements-completed: []  # REQ-tip-chamfer-capped: shared with 10-05, which has not
# produced a SUMMARY yet. `requirements.ready-ids` reports 0/1 ready today -- marking
# it here would flip REQUIREMENTS.md complete while 10-05 (the decision-log entry and
# README rows) is still open. Left for 10-05 to mark.

coverage:
  - id: D1
    description: "The 9-row tip-chamfer sweep (D-06) is committed and pinned: every
      row validates, each largest chamfer is cut whole and one step more is trimmed
      or refused, and one chamfered set runs end to end through make bench.build"
    requirement: REQ-tip-chamfer-capped
    verification:
      - kind: unit
        ref: "tests/test_bench.py#test_the_tip_chamfer_sweep_is_every_combination_d_06_names"
        status: pass
      - kind: other
        ref: "make bench.build SWEEP=<one chamfered set> -- 1 Markdown row produced"
        status: pass
    human_judgment: false
  - id: D2
    description: "bench/RESULTS.md holds all 9 measured rows inside the 30s timeout,
      the host state and its caveat, the named heaviest row, the timeout margin and
      the phase's make verify wall time"
    requirement: REQ-tip-chamfer-capped
    verification:
      - kind: other
        ref: "grep -c '^## Tooth-tip chamfer build and export time (Phase 10)' == 1;
          grep -c teeth=200 rows == 9; grep -c '**NO**' rows == 0; git diff --numstat
          277a98f -- bench/RESULTS.md == 0 deletions"
        status: pass
    human_judgment: false
  - id: D3
    description: "The narrowed SPUR_BUILD_TIMEOUT margin is filed as must-severity
      debt with a measured trigger, since the heaviest row (14.87s) exceeds the 7.5s
      quarter-of-timeout threshold"
    requirement: REQ-tip-chamfer-capped
    verification:
      - kind: other
        ref: "docs/tech_debt/active/2026-09-28-tip-chamfer-narrows-the-build-timeout-margin.md
          (Severity: must); docs/tech_debt/INDEX.md Active row"
        status: pass
    human_judgment: false

duration: ~17min
completed: 2026-09-28
status: complete
---

# Phase 10 Plan 04: Tooth-Tip Chamfer Build and Export Time Summary

**Measured the tip chamfer's cost at 200 teeth across D-06's 9-row sweep: heaviest row
14.87s of 30s (module 1.75, c=1.75, both recesses), driven almost entirely by the
chamfer operator as 10-01 predicted -- filed as must-debt because it leaves only ~2.0x
of the timeout's margin, half of the 4x the default was set by.**

## Performance

- **Duration:** ~17 min (from 10-03's close-out commit to this plan's second task
  commit; session start time not separately captured)
- **Started:** 2026-09-28T13:08:37Z (previous commit on this branch, 10-03's close-out)
- **Completed:** 2026-09-28T13:23:10Z
- **Tasks:** 2
- **Files modified:** 5 (2 created, 3 modified)

## Accomplishments

- `bench/sweeps/tip_chamfer.json`: D-06's 9-row sweep at 200 teeth -- module {1.75, 10}
  x tip_chamfer {0.4, the largest each module allows: 1.75 at module 1.75, 3 at module
  10} x recess_sides {both, none}, on the default bore, plus one module-0.2 row at
  backlash 0.07 (the finest tips this model allows).
- `test_the_tip_chamfer_sweep_is_every_combination_d_06_names`: proves the 9-row cross
  product, the default-bore fields on every row, and that each largest chamfer is cut
  whole (`tip_chamfer_effective(p) == p.tip_chamfer`) while one step (0.05 mm) more is
  either refused (module 10, the field's own `le` = 3) or trimmed back to the same
  limit (module 1.75, the pitch circle). Also pins the module-0.2 row's backlash edge:
  0.07 builds, 0.08 raises `ValidationError` (check()'s 0.05 mm tip-thickness floor).
- One chamfered set (`teeth=19 tip_chamfer=0.4`) ran end to end through
  `make bench.build`, producing its timed Markdown row -- the tracer proof that
  `bench/build_time.py` and the Makefile need no changes for this phase (08 D-12).
- Ran the full 9-row sweep: **all rows inside 30s**, heaviest **teeth=200 module=1.75
  tip_chamfer=1.75 recess_sides=both -- 14.87s of 30s**, about 3x Phase 8's heaviest
  hex row (5.08s) and Phase 9's heaviest keyway row (4.85s), and about 2x the 7.39s
  worst single build on record. The chamfer operator dominates: 13-14s of bare build
  against 10-01's own 12.50-12.81s chamfer-only measurement on the same 400-edge case.
  D-07's over-budget checkpoint did not fire.
- `bench/RESULTS.md` "## Tooth-tip chamfer build and export time (Phase 10)": the
  intro, host state (with the >1.5 load caveat, L08), the 9-row table, the heaviest
  line, the `SPUR_BUILD_TIMEOUT margin` section (30 / 14.87 ~= 2.0x, half the 4x the
  default was sized against, one gear at a time -- nothing extrapolated to concurrent
  load) and the `make verify` wall time: **453 passed in 97.18s** / **98.17s** wall,
  against Phase 9's **396** / **78.21s**, a **+19.96s** delta from the phase's 57 new
  tests.
- Filed `docs/tech_debt/active/2026-09-28-tip-chamfer-narrows-the-build-timeout-margin.md`
  (must-severity) and its `docs/tech_debt/INDEX.md` Active row, since the heaviest row
  (14.87s) crosses the 7.5s quarter-of-timeout trigger the default's own rationale set.

## Task Commits

Each task was committed atomically:

1. **Task 1: Commit the tip-chamfer sweep, prove each largest chamfer sits on its
   limit, and run one chamfered set end to end** - `e63ae4c` (test)
2. **Task 2: Run the tip-chamfer sweep and record every row, the host state, the
   heaviest row, the timeout margin and make verify's wall time; file the debt item**
   - `bbe888f` (docs)

_Plan metadata (this SUMMARY, STATE.md, ROADMAP.md) is committed separately below._

## Files Created/Modified

- `bench/sweeps/tip_chamfer.json` - the 9-row sweep (D-06)
- `tests/test_bench.py` - `test_the_tip_chamfer_sweep_is_every_combination_d_06_names`,
  the `tip_chamfer_effective` import, one docstring sentence
- `bench/RESULTS.md` - the new "## Tooth-tip chamfer build and export time (Phase 10)"
  section (append-only, 112 lines added, 0 deleted)
- `docs/tech_debt/active/2026-09-28-tip-chamfer-narrows-the-build-timeout-margin.md` -
  new must-severity debt item
- `docs/tech_debt/INDEX.md` - one new Active row

## Decisions Made

See `key-decisions` in the frontmatter above: the debt trigger reuses the timeout's own
4x rationale rather than inventing a new budget, and D-07's checkpoint never fired
because every row measured comfortably inside 30s on the first run.

## Deviations from Plan

None - plan executed exactly as written. Every planned check (the cross-product test,
the on-the-limit trims and refusals, the module-0.2 backlash edge, the sweep gate, the
debt threshold) matched the code and the measurement on first run; nothing needed
reconciling against the plan's `<interfaces>` numbers.

## Issues Encountered

None. Host load (3.09-4.51 across the session) sat above this project's usual "quiet"
bar (>1.5) throughout, so the RESULTS.md section carries that caveat per L08 -- the
same caveat every prior sweep section in this file carries. `make verify`'s pre-commit
hook completed within its own ~98s window both times; the `gsd_run query commit` 30s
timeout noted in STATE.md was not hit this session (both commits used plain
`git commit` directly per 10-CONTEXT.md D-17's process note).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- 10-05 (the decision-log entry L29 and the README rows) is unblocked: this plan's
  numbers (the 9-row sweep, the heaviest row, the margin) are exactly what L29 needs
  to cite.
- REQ-tip-chamfer-capped stays unmarked in REQUIREMENTS.md until 10-05 finishes
  (shared-ID gate: `requirements.ready-ids` reports 0/1 ready today).
- No blockers. The filed debt item's own "Next step" (measure a tip-chamfered gear
  under `bench.latency`'s ten-concurrent scenario, or fold it into Phase 12's composed
  sweep) is deferred work, not a blocker to 10-05 or to shipping this phase.

---
*Phase: 10-tooth-tip-chamfer*
*Completed: 2026-09-28*

## Self-Check: PASSED

- FOUND: bench/sweeps/tip_chamfer.json
- FOUND: docs/tech_debt/active/2026-09-28-tip-chamfer-narrows-the-build-timeout-margin.md
- FOUND: .planning/phases/10-tooth-tip-chamfer/10-04-SUMMARY.md
- FOUND commit: e63ae4c
- FOUND commit: bbe888f
- Re-ran `make test PYTEST_ARGS="tests/test_bench.py -q"`: 7 passed
- Re-ran the RESULTS.md acceptance greps: section count 1, teeth=200 row count 9,
  debt file `Severity: must` count 1 -- all match
