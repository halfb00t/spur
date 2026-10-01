---
phase: 10-tooth-tip-chamfer
plan: 03
subsystem: testing
tags: [cadquery, chamfer, edge-selection, pytest, regression]

requires:
  - phase: 10-tooth-tip-chamfer
    provides: "10-02's tip_chamfer field, calc.tip_chamfer_limit/tip_chamfer_effective,
      model._tip_edges and model._chamfer_tips (the last _build step) -- this plan
      proves them against the boundary 10-01 measured"
provides:
  - "test_each_edge_selector_picks_exactly_its_own_edges: a tip Counter column on all
    28 existing matrix rows (38 arcs, 19/19 split) plus two new rows, teeth-200 and
    module-0.2 (400 arcs, 19/19 becoming 200/200), asserting exact identity (CIRCLE at
    ra) and per-face split, not just a count"
  - "test_the_tip_chamfer_takes_exactly_the_tip_arcs_in_the_real_pipeline: a spy on
    _tip_edges through the real chamfered/keyed/hex pipeline (3 bore shapes) -- called
    exactly once, 38 CIRCLE arcs split 19/19, matching 10-01's measured face counts
    (210/213/222)"
  - "The empty-selection guard proven as a BuildError (model), a 422 with
    detail[].type == build_error (API), and a stopped CLI export that writes nothing
    and exits 1, never argparse's exit 2 (D-14 as amended 2026-09-28)"
  - "_assert_only_the_tip_arcs_were_chamfered: the D-12 built-solid proof helper --
    +2 x teeth CONE faces, +6 x teeth edges, smaller volume, bounding box and tip_d
    unchanged, the rim/floor selectors' counts unchanged, no tip arc left on an end
    face, and the 45-degree geometry (moved circles at ra, sharp circles at ra - c on
    the end faces) -- shared by the proof and the tripwire that shows it fail on a
    skipped step (D-14)"
  - "The flank limit's kernel boundary tested one step either side (D-04): the cap
    (2.937 mm on {profile_shift 1.0, pressure_angle 14.5}) builds +38 faces; one 0.05
    mm step past the measured contact (2.9875 mm) the kernel returns an invalid solid"
affects: [10-04, 10-05]

actuals:
  tokens: 5734
  tasks: 2
  commits: 2
  plan_head_before: 835e2798907506f7b9d6a6d778ccb3f5e9722908
  plan_head_after: bd5f98c02b5a3fa1ff36b368aa5e3ca152cf0740

tech-stack:
  added: []
  patterns:
    - "The built-solid proof and its tripwire share one helper
      (_assert_only_the_tip_arcs_were_chamfered) that takes the chamfered and plain
      solids plus both GearParams, so the same checks run both times -- Phase 7's
      tripwire precedent, now a third instance alongside the matrix's own guard tests."

key-files:
  created: []
  modified:
    - tests/test_model.py
    - tests/test_api.py
    - tests/test_cli.py

key-decisions:
  - "Both proof rows are built with GearParams.model_validate (not model_copy) -- a
    1.0 mm tip chamfer sits comfortably inside every row's caps (D-flat, keyed round,
    hex), so no validation bypass is needed the way the kernel-boundary tests need one
    to reach a config check() would otherwise refuse."
  - "The kernel-boundary test patches spur.model.tip_chamfer_effective directly
    (2.9875, one step past the measured contact) rather than tip_chamfer alone,
    because the field's own cap would otherwise clamp any settable value back inside
    the boundary before it ever reached the kernel -- the same reason
    test_the_kernel_fails_where_a_round_bore_chamfer_touches_the_root bypasses
    validation with model_copy() instead."

requirements-completed: []  # REQ-tip-chamfer / REQ-tip-chamfer-capped: shared across
# 10-01/10-02/10-03/10-04/10-05 (all declare them in frontmatter); 10-04/10-05 have not
# produced a SUMMARY yet, so the shared-ID gate (requirements.ready-ids) still reports
# 0/2 ready -- marking them here would flip REQUIREMENTS.md complete while the cost
# sweep (10-04) and the decision-log entry (10-05) are still open. Left for whichever
# plan finishes last.

coverage:
  - id: D1
    description: "The tip selector's exact count on every bore profile and recess
      setting (30 matrix rows), including the tooth-count and module extremes"
    requirement: REQ-edge-selection-proven
    verification:
      - kind: unit
        ref: "tests/test_model.py#test_each_edge_selector_picks_exactly_its_own_edges[30 rows]"
        status: pass
    human_judgment: false
  - id: D2
    description: "The same exact count observed in the real pipeline with the bore
      chamfer, the recess fillets and a keyway all present, on three bore shapes"
    requirement: REQ-edge-selection-proven
    verification:
      - kind: unit
        ref: "tests/test_model.py#test_the_tip_chamfer_takes_exactly_the_tip_arcs_in_the_real_pipeline[3 rows]"
        status: pass
    human_judgment: false
  - id: D3
    description: "An empty tip-arc selection is a BuildError, a 422 naming the defect,
      and a stopped CLI export that writes nothing and exits 1"
    requirement: REQ-tip-chamfer
    verification:
      - kind: unit
        ref: "tests/test_model.py#test_a_tip_chamfer_that_selects_no_tip_arcs_is_a_build_error_not_a_sharp_tip"
        status: pass
      - kind: integration
        ref: "tests/test_api.py#test_a_tip_chamfer_that_selects_no_tip_arcs_is_a_422_naming_the_defect"
        status: pass
      - kind: integration
        ref: "tests/test_cli.py#test_a_tip_chamfer_that_selects_no_tip_arcs_stops_the_export_and_writes_nothing"
        status: pass
    human_judgment: false
  - id: D4
    description: "On the built solid, the chamfer changes only the tooth-tip arcs:
      flanks, root fillets, bore, recess and keyway untouched, outside diameter
      unchanged, on three bore shapes (D-flat, keyed round, hex)"
    requirement: REQ-tip-chamfer
    verification:
      - kind: unit
        ref: "tests/test_model.py#test_the_tip_chamfer_breaks_only_the_tip_arcs_on_the_built_solid[3 rows]"
        status: pass
    human_judgment: false
  - id: D5
    description: "The built-solid proof is shown to fail when the chamfer step is
      silently skipped, while derive() still prints the chamfer as applied (L08)"
    requirement: REQ-tip-chamfer
    verification:
      - kind: unit
        ref: "tests/test_model.py#test_the_tip_chamfer_proof_fails_when_the_tip_step_is_skipped"
        status: pass
    human_judgment: false
  - id: D6
    description: "The flank limit's kernel boundary (D-04) holds one step either side:
      the cap builds, one 0.05 mm step past the measured contact fails"
    requirement: REQ-tip-chamfer-capped
    verification:
      - kind: unit
        ref: "tests/test_model.py#test_the_largest_tip_chamfer_the_flank_limit_allows_builds"
        status: pass
      - kind: unit
        ref: "tests/test_model.py#test_the_kernel_fails_one_step_past_the_start_of_the_involute"
        status: pass
    human_judgment: false

duration: ~19min
completed: 2026-09-28
status: complete
---

# Phase 10 Plan 03: Tooth-Tip Chamfer Proof Summary

**Proved the tip chamfer selects and cuts exactly the `2 x teeth` tooth-tip arcs: 30
matrix rows, a real-pipeline spy on three bore shapes, the empty-selection guard as a
`BuildError`/422/exit-1, and the built-solid proof (`+38` CONE faces, `+114` edges,
`-22.7557` mm3) with its tripwire and the kernel boundary tested one step either side.**

## Performance

- **Duration:** ~19 min (estimated from commit timestamps; session start time not
  captured)
- **Started:** 2026-09-28T12:41:32Z (previous commit on this branch, 10-02's close-out)
- **Completed:** 2026-09-28T13:00:25Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments

- `test_each_edge_selector_picks_exactly_its_own_edges` carries a tip column on all 30
  rows: **38 arcs (2 x 19)**, split 19/19 across the end faces, on the 28 existing
  rows; **400 arcs**, split 200/200, on the two new rows (`teeth-200`, and `module-0.2`
  at 200 teeth/module 0.2/backlash 0.07 -- D-13's finest-tip extreme). Every returned
  edge is checked for identity (CIRCLE, radius `ra`), not just counted.
- `test_the_tip_chamfer_takes_exactly_the_tip_arcs_in_the_real_pipeline` spies on
  `_tip_edges` through `_build_checked` with the 0.4 mm bore chamfer, the filleted
  recess floors and (on two of three rows) a keyway slot all present: called **exactly
  once**, returning `Counter({"CIRCLE": 38})` split `{0: 19, 1: 19}`, on a D-flat (210
  faces), a keyed round bore (213 faces) and a hex bore (222 faces) -- matching 10-01's
  measured face counts exactly.
- The empty-selection guard (a radius-shifted `_tip_edges` wrapper picking no arcs) is
  a `BuildError` matching `"selected no tip-arc edges"`, never relabelled "try smaller"
  by the catch-all; a 422 over HTTP with `detail[0]["type"] == "build_error"`; and a
  stopped CLI export that writes no file and exits with the error string as its code
  (verified live: `SystemExit('error: Tip chamfer selected no tip-arc edges: ...')`,
  which exits process status 1, matching every other `BuildError` on the CLI -- D-14 as
  amended 2026-09-28).
- `_assert_only_the_tip_arcs_were_chamfered` (the D-12 proof helper, shared by the
  proof and the tripwire) measured, on all three bore shapes (D-flat, keyed round,
  hex), with `bore_chamfer=0`/`recess_fillet=0` and `tip_chamfer=1.0`:
  - faces **164->202 / 167->205 / 168->206**, each **+38** and each entirely `CONE`
    (`Counter({"CONE": 38})`, no other face-type delta either direction);
  - edges **+114** on all three (`6 x teeth`);
  - volume delta **-22.7557 mm3** on all three;
  - bounding box and `derive().tip_d` unchanged within `TOL`; the rim and groove-floor
    selectors' counts unchanged on the chamfered solid;
  - no tip arc left on an end face (`_tip_edges` raises on the chamfered solid);
  - the 45-degree geometry: 19 `CIRCLE` arcs of radius `ra` at `z=1.0` and 19 at
    `z=6.5` (`c` and `face_width - c`), and 19 sharp `CIRCLE` arcs of radius `ra - c`
    on each end face (`z=0` and `z=7.5`) -- all matching 10-01's measured deltas
    exactly.
- `test_the_tip_chamfer_proof_fails_when_the_tip_step_is_skipped`: with
  `_chamfer_tips` patched to a no-op, `derive(GearParams(tip_chamfer=1.0)).
  tip_chamfer_effective` still reads `1.0` (the number keeps printing -- the L08
  failure this catches) while `_assert_only_the_tip_arcs_were_chamfered` raises
  `AssertionError` on the first check (the face-type delta is empty, not
  `Counter({"CONE": 38})`).
- The flank limit's kernel boundary (D-04), tested one step either side: on
  `{profile_shift 1.0, pressure_angle 14.5, tip_chamfer 3}`, `min(0.45 x face_width,
  ra - r, 3.0) == 3.0` (D-01/D-02 alone would allow the full 3.0 mm), the cap resolves
  to `tip_chamfer_effective(p) == 2.937`, and that builds one valid solid with exactly
  `+38` faces over the unchamfered baseline. Forcing `tip_chamfer_effective` to
  `2.9875` (one 0.05 mm step past the measured contact, `ra - spline_start = 2.9375`)
  makes the kernel raise `BuildError("Geometry kernel produced an invalid solid ...")`.
- `tests/regression/pre_v0_2.json` stayed byte-unchanged through both tasks (`git diff
  --exit-code`, checked after each).

## Task Commits

Each task was committed atomically:

1. **Task 1: The tip selector end to end** - `afbd734` (test)
2. **Task 2: Prove the cut on the built solid** - `bd5f98c` (test)

_Plan metadata (this SUMMARY, STATE.md, ROADMAP.md) is committed separately below._

## Files Created/Modified

- `tests/test_model.py` - matrix tip column (30 rows); the real-pipeline spy test; the
  empty-selection guard test; `_tip_edges` import; `_assert_only_the_tip_arcs_were_
  chamfered` helper; the built-solid proof (3 rows); the tripwire; the two flank-limit
  kernel-boundary tests
- `tests/test_api.py` - the 422 empty-selection guard test; `cadquery`/`spur.model`
  imports
- `tests/test_cli.py` - the CLI empty-selection guard test (exit 1, writes nothing);
  `cadquery`/`spur.model` imports

## Decisions Made

See `key-decisions` in the frontmatter: the proof rows use `GearParams.model_validate`
(no bypass needed, 1.0 mm sits inside every cap), and the kernel-boundary test patches
`tip_chamfer_effective` directly rather than the `tip_chamfer` field, because the
field's own cap would otherwise clamp any settable value back inside the boundary
before it reached the kernel.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Split an over-length parametrize line**
- **Found during:** Task 1
- **Issue:** Adding the `tip` column widened one `pytest.param(...)` line (the
  `hex-bottom` row) past ruff's 100-column limit (`E501`).
- **Fix:** Wrapped the line at the existing continuation style used by every other
  multi-line row in the same list.
- **Files modified:** `tests/test_model.py`
- **Verification:** `make lint` passes clean.
- **Committed in:** `afbd734` (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (1 blocking, lint-only). **Impact on plan:** no
behavior change; the fix was necessary for `make lint` to pass. No scope creep.

## Issues Encountered

None. Both tasks' verification commands (matrix collection count, targeted `-k` runs,
the full `tests/test_model.py tests/test_api.py tests/test_cli.py tests/test_calc.py
tests/regression` suite, `make lint typecheck`) passed on the first try after the one
lint fix above.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- 10-04's cost sweep and 10-05's decision-log entry (L29) and README rows are
  unblocked; nothing in this plan's `<interfaces>` needs revisiting -- every measured
  number (face/edge/CONE/volume deltas, the spy's face counts, the boundary readings)
  matched the plan's planning-time readings exactly.
- REQ-tip-chamfer and REQ-tip-chamfer-capped stay unmarked in REQUIREMENTS.md until
  the last of 10-01..10-05 finishes (shared-ID gate: `requirements.ready-ids` reports
  0/2 ready today; 10-01/10-02/10-03 done, 10-04/10-05 still open).
- No blockers.

---
*Phase: 10-tooth-tip-chamfer*
*Completed: 2026-09-28*

## Self-Check: PASSED

- FOUND: tests/test_model.py
- FOUND: tests/test_api.py
- FOUND: tests/test_cli.py
- FOUND: .planning/phases/10-tooth-tip-chamfer/10-03-SUMMARY.md
- FOUND commit: afbd734
- FOUND commit: bd5f98c
- Re-ran `make test PYTEST_ARGS="tests/test_model.py tests/test_api.py tests/test_cli.py tests/test_calc.py tests/regression -q"`: 332 passed
- Re-ran `git diff --exit-code tests/regression/pre_v0_2.json`: exit 0 (byte-unchanged)
- Re-ran `make lint typecheck`: both clean
