---
phase: 07-foundation-generalized-edge-selection-regression-fixture
plan: 02
subsystem: geometry
tags: [cadquery, edge-selection, build-error, decision-log, L05, L26]

# Dependency graph
requires:
  - phase: 07-01
    provides: "tests/regression/pre_v0_2.json (44 records) and make fixture.regen, the
      L05 proof this plan's selector change must leave byte-unchanged and green"
provides:
  - "calc.bore_rim_limit(p): the exact geometric rim bound per bore shape (bore_radius(p)
    for round and D-flat, 0.0 with no bore), the seam Phase 8's hex bore extends"
  - "model.BORE_RIM_SLACK (0.01 mm): the named, measured selection slack, replacing the
    inline `r_bore + 0.01`"
  - "Both position-based selectors (_bore_rim_edges, _groove_floor_edges) raise
    BuildError on an empty selection while their feature is on, instead of handing
    .chamfer()/.fillet() an empty list"
  - "A 10-row exact-count-and-identity test matrix proving the selected edges per bore
    shape, with and without recesses, with no bore, and at a recess's minimum hub
    clearance"
  - "L26 in the decision log: the fixture as the standing L05 proof plus its
    regeneration rule, and the selector-never-silently-no-ops rule, in one entry"
affects: ["08", "09", "10", "11", "12"]

# Actuals (#2632)
actuals:
  tokens: 6614
  tasks: 3
  commits: 3

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "A bound computed in calc.py (bore_rim_limit), a named slack constant in model.py
      (BORE_RIM_SLACK) that turns the exact bound into a matching band -- the pure-maths
      module states the fact, the kernel-facing module states the tolerance it needs"
    - "A position-based selector that finds zero edges while its feature is on raises
      BuildError before handing the empty list to .chamfer()/.fillet(), rather than
      letting cadquery accept it as a silent no-op"

key-files:
  created: []
  modified:
    - src/spur/calc.py
    - src/spur/model.py
    - tests/test_calc.py
    - tests/test_model.py
    - docs/architecture/decision_log.md
    - docs/architecture/solid-model/tactics.md
    - bench/RESULTS.md

key-decisions:
  - "BORE_RIM_SLACK's comment carries the measured kernel tolerance: 1e-7 mm, read from
    BRep_Tool.Tolerance_s over every Vertex and Edge on GearParams(bore_chamfer=0) and
    GearParams(bore_flat=0, bore_chamfer=0), matching planning's 2026-09-26 probe exactly."
  - "One L26 entry covers both D-03 (the fixture's regeneration rule) and D-15..D-18 (the
    selector guard), per 07-CONTEXT.md's Claude's Discretion recommendation."
  - "The zero-edge tests provoke the guard through the real build path rather than
    calling the selector in isolation: a monkeypatched bore_rim_limit (half the bore
    radius) through _build_checked for the bore-rim guard, and a bore-less-groove solid
    handed directly to _groove_floor_edges for the recess guard -- a bore-less solid was
    rejected for the bore-rim case because its stock recess rim circles fall inside the
    band (planning probe), so it is not a valid zero-edge provocation."

requirements-completed: [REQ-edge-selection-proven, REQ-defaults-off-regression]

coverage:
  - id: D1
    description: "calc.bore_rim_limit(p) returns the exact geometric bound (bore_radius(p)
      for round and D-flat bores, 0.0 with no bore), with no kernel import in calc.py"
    requirement: REQ-edge-selection-proven
    verification:
      - kind: unit
        ref: "tests/test_calc.py::test_the_bore_rim_limit_is_the_bore_radius_for_round_and_d_flat_bores"
        status: pass
      - kind: other
        ref: "make lint-imports -> 'The gear maths stays free of the CAD kernel KEPT'"
        status: pass
    human_judgment: false
  - id: D2
    description: "model.BORE_RIM_SLACK (0.01 mm) carries the measured kernel tolerance
      (1e-7 mm) and the MIN_WALL clearance (0.4 mm) it stays under, in TOL's comment shape"
    verification:
      - kind: other
        ref: "grep -c '^BORE_RIM_SLACK = 0\\.01 ' src/spur/model.py -> 1; comment states
          '1e-7 mm' and 'MIN_WALL (0.4 mm)'"
        status: pass
    human_judgment: false
  - id: D3
    description: "_bore_rim_edges(solid, p) bounds by calc.bore_rim_limit(p) +
      BORE_RIM_SLACK and raises BuildError on an empty selection; _groove_floor_edges
      raises BuildError on an empty selection; both messages ride the existing BuildError
      routing (422 / exit 2) unchanged"
    requirement: REQ-edge-selection-proven
    verification:
      - kind: unit
        ref: "tests/test_model.py::test_a_bore_chamfer_that_selects_no_rim_edges_is_a_build_error_not_a_bare_bore"
        status: pass
      - kind: unit
        ref: "tests/test_model.py::test_a_recess_fillet_that_selects_no_floor_edges_is_a_build_error"
        status: pass
      - kind: other
        ref: "git diff --quiet b3ca789 -- src/spur/app.py src/spur/cli.py src/spur/params.py -> exit 0"
        status: pass
    human_judgment: false
  - id: D4
    description: "10-row matrix proves the exact selected edges per bore shape (round,
      D-flat), with and without recesses, with no bore, and at a recess's minimum hub
      clearance, plus identity (z on an end face, CIRCLE radius equals bore_radius)"
    requirement: REQ-edge-selection-proven
    verification:
      - kind: unit
        ref: "tests/test_model.py::test_each_edge_selector_picks_exactly_its_own_edges (10
          parametrized rows, all pass)"
        status: pass
    human_judgment: false
  - id: D5
    description: "tests/regression/pre_v0_2.json is byte-unchanged by this plan and all
      85 of its cases pass after the selector change"
    requirement: REQ-defaults-off-regression
    verification:
      - kind: integration
        ref: "git diff --exit-code tests/regression/pre_v0_2.json (run after every task) -> exit 0"
        status: pass
      - kind: integration
        ref: "make test PYTEST_ARGS=\"tests/regression -q\" -> 85 passed"
        status: pass
    human_judgment: false
  - id: D6
    description: "L26 appended to the decision log (append-only), tactics.md describes
      the bound and the guard, bench/RESULTS.md holds this plan's measured make verify
      cost, and make verify is green"
    verification:
      - kind: other
        ref: "grep -c '^## L26 — ' docs/architecture/decision_log.md -> 1; git diff
          --numstat -- docs/architecture/decision_log.md -> 0 deleted lines"
        status: pass
      - kind: integration
        ref: "make verify -> 289 passed, exit 0"
        status: pass
    human_judgment: false

duration: ~11min (committed span; longer including reading, measurement and verify runs)
completed: 2026-09-26
status: complete
---

# Phase 7 Plan 2: Generalized Edge Selection Summary

**`calc.bore_rim_limit(p)` replaces the inline `r_bore + 0.01`, `model.BORE_RIM_SLACK`
(0.01 mm) carries the measured 1e-7 mm kernel tolerance behind it, both position-based
selectors now raise `BuildError` on an empty selection, a 10-row matrix proves the exact
selected edges per bore shape, and the 07-01 fixture stayed byte-unchanged and green
throughout — closed with decision-log entry L26.**

## Performance

- **Duration:** ~11 min of committed work (first commit `768470d` 12:43:20+06:00 to the
  metadata commit `c0dc811` 12:53:52+06:00); wall-clock session time was longer —
  reading the required files, measuring the kernel tolerance, and running `make verify`
  twice for the bench numbers all happened before/between commits and are not counted
  in the span above
- **Started:** 2026-09-26T12:43:20+06:00 (Task 1's commit)
- **Completed:** 2026-09-26T12:53:52+06:00
- **Tasks:** 3
- **Files modified:** 7 (0 created, 7 edited)

## Accomplishments

- `src/spur/calc.py::bore_rim_limit(p)`: the exact geometric rim bound, no slack --
  `bore_radius(p)` for round and D-flat bores, 0.0 with no bore, shaped for Phase 8's hex
  circumradius; no kernel import (`make lint-imports` confirms)
- `src/spur/model.py::BORE_RIM_SLACK = 0.01`: the selection slack, with a comment
  carrying the measured kernel tolerance -- 1e-7 mm, read via `BRep_Tool.Tolerance_s`
  over every `Vertex` and `Edge` on `GearParams(bore_chamfer=0)` and
  `GearParams(bore_flat=0, bore_chamfer=0)`, three orders of magnitude below the slack
  and forty times under `MIN_WALL` (0.4 mm)
- `_bore_rim_edges(solid, p)` bounds by `bore_rim_limit(p) + BORE_RIM_SLACK` and raises
  `BuildError("Bore chamfer selected no bore-rim edges: ...")` on an empty selection;
  `_groove_floor_edges` raises `BuildError("Recess fillet selected no groove-floor
  edges: ...")` the same way -- both ride the existing routing (422 / CLI exit 2)
  unchanged, and both messages stay distinct from `_build_checked`'s catch-all wording
- A 10-row parametrized matrix (`test_each_edge_selector_picks_exactly_its_own_edges`)
  proves the exact selected-edge count and identity per bore shape (round, D-flat), with
  and without recesses, with no bore, and at a recess's minimum hub clearance
  (`recess_inner_d=1.0`)
- Two refusal tests provoke each guard through the real build path: a monkeypatched
  `bore_rim_limit` (half the bore radius) through `_build_checked`, and a bore-less-groove
  solid handed directly to `_groove_floor_edges`
- L26 appended to the decision log: the fixture as the standing L05 proof plus its
  regeneration rule (D-03), and the selector-never-silently-selects-nothing rule
  (D-15..D-18), with the measured numbers behind each
- `tests/regression/pre_v0_2.json` never changed: `git diff --exit-code` checked after
  every task, and all 85 of its cases stayed green throughout
- `bench/RESULTS.md` records this plan's cost: 289 passed (13 new tests over 07-01's
  276), mean `make verify` 52.25s across two runs, against 07-01's 49.51s and the
  pre-Phase-7 baseline of 32.47s / 191 tests

## Task Commits

Each task was committed atomically:

1. **Task 1: One shape end-to-end -- calc.bore_rim_limit(p) bounds the bore-rim
   selector, an empty selection raises, proven on the D-flat gear and the unchanged
   fixture** - `768470d` (feat)
2. **Task 2: Both selectors guarded and count-tested for every bore shape, with and
   without recesses, plus the two zero-edge refusals** - `bd4e477` (feat)
3. **Task 3: Log L26, keep the tactics doc true, record the phase's measured cost, run
   the full gate** - `c0dc811` (docs)

**Plan metadata:** (this commit, following this SUMMARY)

## Files Created/Modified

- `src/spur/calc.py` - new `bore_rim_limit(p)` below `bore_radius`
- `src/spur/model.py` - `BORE_RIM_SLACK` beside `TOL`; `_bore_rim_edges` bounded by
  `bore_rim_limit(p)` and guarded; `_groove_floor_edges` guarded; `_cut_bore`'s chamfer
  call passes `p` instead of `r_bore, face_width`
- `tests/test_calc.py` - `test_the_bore_rim_limit_is_the_bore_radius_for_round_and_d_flat_bores`
- `tests/test_model.py` - the 10-row selector matrix and its identity checks, the two
  zero-edge `BuildError` tests
- `docs/architecture/decision_log.md` - L26 (append-only; 0 lines deleted)
- `docs/architecture/solid-model/tactics.md` - Edge re-selection paragraph names the
  bound and the guard; the `Out:` `BuildError` bullet extended
- `bench/RESULTS.md` - new `### After the selector change (07-02)` subsection

## Decisions Made

- BORE_RIM_SLACK's comment carries the freshly measured kernel tolerance (1e-7 mm) rather
  than reusing planning's number verbatim without re-checking -- it happened to match
  exactly, confirming the pinned kernel's tolerance is stable across sessions.
- One L26 entry covers both the fixture's regeneration rule and the selector guard
  (07-CONTEXT.md's Claude's Discretion recommendation), following L24/L25's paragraph
  shape (Date, bold-led sections, Rejected, Reversibility, Reason).
- The bore-rim zero-edge test provokes the guard via a monkeypatched `bore_rim_limit`
  through `_build_checked` rather than a bore-less solid, because a bore-less solid's
  stock recess rim circles fall inside the bore-rim band and are not a valid zero-edge
  case (confirmed by planning's probe and re-verified here).

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None. `make verify` was green on first run after each task; no fix pass needed.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `calc.bore_rim_limit(p)` is the seam Phase 8's hex bore extends (its circumradius
  replaces `bore_radius(p)` for that shape) without touching `model.py`'s selection
  logic or the slack constant.
- Both position-based selectors now refuse an empty selection loudly; any later phase
  reusing `_bore_rim_edges` or `_groove_floor_edges` inherits the guard for free.
- The L05 regression fixture is proven behaviour-neutral through this selector change
  and remains the standing proof for Phases 8-12; L26 documents both its regeneration
  rule and the selector rule in one place for future citation.

## Self-Check: PASSED

All 7 modified files found on disk. All 3 task commit hashes (`768470d`, `bd4e477`,
`c0dc811`) found in `git log --oneline --all`. `make verify` re-run clean: 289 passed.
`git diff --exit-code tests/regression/pre_v0_2.json` exits 0.

---
*Phase: 07-foundation-generalized-edge-selection-regression-fixture*
*Completed: 2026-09-26*
