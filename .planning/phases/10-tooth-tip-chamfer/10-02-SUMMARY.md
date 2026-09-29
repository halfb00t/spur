---
phase: 10-tooth-tip-chamfer
plan: 02
subsystem: cad-model
tags: [cadquery, chamfer, pydantic, tip-chamfer, derived-dimensions]

requires:
  - phase: 10-tooth-tip-chamfer
    provides: "10-01's measured kernel boundary (pred = ra - spline_start), the
      edge-count-driven cost finding, and the 405-set grid this plan's tests reuse"
provides:
  - "GearParams.tip_chamfer (Teeth group, after root_fillet, mm, 0-3, step 0.05,
    default 0): reaches /api/schema, the CLI flag and the web form from the model
    alone -- app.py and cli.py untouched"
  - "calc.spline_start(pr, fillet): the involute-spline-start radius moved out of
    model._outline unchanged (D-15), now the single source both the outline and the
    cap read"
  - "calc.tip_chamfer_limit(p) / calc.tip_chamfer_effective(p): the three-limit cap
    (tip land, pitch circle, measured involute-flank boundary) and its applied value,
    rounded once, never refused"
  - "DerivedDimensions.tip_chamfer_effective and derive()'s one warning sentence,
    naming whichever limit bound"
  - "model._tip_edges (position selector, guarded BuildError) and model._chamfer_tips
    (the last _build step, bore_chamfer's exact chamfer call)"
  - "app.js DIMS row; tests pinning the cap at each limit, the field bound, the
    no-other-number claim, spline_start's three cases and the 405-set grid"
affects: [10-03, 10-04, 10-05]

actuals:
  tokens: 7078
  tasks: 2
  commits: 2
  plan_head_before: 787694370632f88a747971ba266f5ca52670f1b1
  plan_head_after: 92382751746f3e30e106f7abae68f8b0bdf9a9b7

tech-stack:
  added: []
  patterns:
    - "A cap lives in one calc.py function returning the applied value (tuple-compared
      min() of (limit, reason) pairs, so a tie breaks on the reason text
      deterministically); derive() warns once when it differs from the request;
      model.py calls the same function -- the part and the printed number cannot
      disagree (L08), continuing root_fillet's and recess_fillet's shape."

key-files:
  created: []
  modified:
    - src/spur/params.py
    - src/spur/calc.py
    - src/spur/model.py
    - src/spur/static/app.js
    - tests/test_api.py
    - tests/test_calc.py
    - tests/test_model.py
    - tests/test_cli.py
    - bench/tip_chamfer_spike.py

key-decisions:
  - "tip_chamfer_limit(p) returns (limit, reason) as a 3-way min() over tuples rather
    than three separate ifs -- Python compares tuples lexicographically, so an exact
    tie between two limits breaks on the reason string deterministically, with no
    extra branching to write or test."
  - "_chamfer_tips assigns the chamfer result back to the solid variable before
    returning it (matching _cut_bore's shape) rather than returning the chamfer call
    directly -- Mixin3D.chamfer's return type is untyped (Any), and mypy's
    no-any-return check fires on a bare `return solid.chamfer(...)` even though the
    exact same expression assigned to a cq.Shape-typed variable and then returned is
    accepted (the variable's declared type narrows it back at the assignment, not the
    return)."

requirements-completed: []  # REQ-tip-chamfer / REQ-tip-chamfer-capped: shared across
# 10-01/10-02/10-03/10-04/10-05 (all declare them in frontmatter); 10-03/10-04/10-05
# have not produced a SUMMARY yet, so the shared-ID gate (requirements.ready-ids)
# reports 0/2 ready -- marking them here would flip REQUIREMENTS.md complete while
# the built-solid proof (10-03) and the cost sweep (10-04) are still open. Left for
# whichever plan finishes last.

coverage:
  - id: D1
    description: "tip_chamfer breaks through GearParams, /api/schema, the CLI flag and
      the web form, positioned right after root_fillet, with help text naming purpose
      and no size"
    requirement: REQ-tip-chamfer
    verification:
      - kind: integration
        ref: "tests/test_api.py#test_a_tip_chamfer_link_is_served_with_the_chamfer_it_cut"
        status: pass
      - kind: unit
        ref: "tests/test_calc.py#test_the_tip_chamfer_field_is_bounded_zero_to_three"
        status: pass
    human_judgment: false
  - id: D2
    description: "The applied chamfer is the smallest of the tip-land (0.45 x
      face_width), pitch-circle (ra - r) and measured involute-flank (ra -
      spline_start - TIP_CHAMFER_MARGIN) limits, capped and never refused, with one
      warning naming whichever bound"
    requirement: REQ-tip-chamfer-capped
    verification:
      - kind: unit
        ref: "tests/test_calc.py#test_a_tip_chamfer_is_capped_to_whichever_limit_binds_first[15 rows]"
        status: pass
      - kind: unit
        ref: "tests/test_calc.py#test_a_rounded_tip_chamfer_cap_stays_inside_the_measured_kernel_boundary (405 sets)"
        status: pass
      - kind: integration
        ref: "tests/test_cli.py#test_cli_and_api_print_the_same_tip_chamfer_document"
        status: pass
    human_judgment: false
  - id: D3
    description: "model._chamfer_tips cuts exactly tip_chamfer_effective(p), last in
      _build after _cut_keyway, via the guarded position selector _tip_edges; a
      flank-capped link (profile_shift 1.0, pressure_angle 14.5, tip_chamfer 3) that
      the analytic caps alone would pass builds one valid solid instead of failing"
    requirement: REQ-tip-chamfer
    verification:
      - kind: unit
        ref: "tests/test_model.py#test_builds_one_valid_solid[4 new tip-chamfer rows]"
        status: pass
    human_judgment: true
    rationale: "This plan proves the cut builds one valid solid; the full topology
      proof (face/edge deltas, bounding box, untouched selector counts on other
      features -- D-12/D-13) is 10-03's job per the phase's own task split. The
      numbers below are measured here for the SUMMARY record but not yet pinned by a
      built-solid test."
  - id: D4
    description: "The pre-v0.2 regression fixture stays byte-unchanged through both
      tasks; every record replays with tip_chamfer_effective null (L26, D-15)"
    requirement: REQ-derived-dimensions-additive
    verification:
      - kind: other
        ref: "git diff --exit-code tests/regression/pre_v0_2.json (0 diff, run after each task)"
        status: pass
      - kind: integration
        ref: "tests/regression/test_pre_v0_2.py (86 cases, unmodified)"
        status: pass
    human_judgment: false
  - id: D5
    description: "A tip chamfer changes no other derived number: for {}, {teeth 200},
      {profile_shift 1.0, pressure_angle 14.5}, {bore_hex 6} and a 3x1.4 keyway,
      derive() with tip_chamfer 1 differs from tip_chamfer 0 only in
      tip_chamfer_effective and its one warning"
    requirement: REQ-derived-dimensions-additive
    verification:
      - kind: unit
        ref: "tests/test_calc.py#test_the_tip_chamfer_changes_no_other_number[5 rows]"
        status: pass
    human_judgment: false

duration: ~24min
completed: 2026-09-28
status: complete
---

# Phase 10 Plan 02: Tooth-Tip Chamfer Field, Cap and Cut Summary

**`tip_chamfer` breaks the default gear's 38 tooth-tip arcs through the API, CLI and
form (172 to 210 faces, 490 to 604 edges at 0.4 mm), capped to whichever of the tip
land, pitch circle or measured involute-flank boundary binds first, and prints exactly
the chamfer it cut -- the pre-v0.2 fixture stays byte-unchanged throughout.**

## Performance

- **Duration:** ~24 min (estimated from commit timestamps; session start time not
  captured)
- **Started:** 2026-09-28T12:16:13Z (previous commit on this branch, 10-01's close-out)
- **Completed:** 2026-09-28T12:38:34Z
- **Tasks:** 2
- **Files modified:** 9

## Accomplishments

- `GearParams.tip_chamfer` (Teeth group, right after `root_fillet`, mm, 0-3, step
  0.05, default 0) reaches `/api/schema`, the CLI `--tip-chamfer` flag and the web
  form from the model alone -- `app.py` and `cli.py` are byte-unchanged since
  `25b2216` (verified by `git diff --quiet`).
- `calc.spline_start(pr, fillet)` moved the three involute-spline-start lines out of
  `model._outline` unchanged (D-15) -- the outline and the new cap now read the same
  radius from one function, not two copies.
- `calc.tip_chamfer_limit(p)` returns the smallest of three `(limit, reason)` pairs
  -- `0.45 x face_width` (the tip land), `ra - r` (the pitch circle), and `ra -
  spline_start(...) - TIP_CHAMFER_MARGIN` (10-01's measured kernel boundary) --
  compared as tuples so a tie breaks on the reason text. `tip_chamfer_effective(p)`
  applies it, rounded once; `derive()` warns exactly when the applied value differs
  from the (3-dp-rounded) request.
- `model._tip_edges` selects the `2 x teeth` tip-arc `CIRCLE` edges by radius `ra`
  and both endpoints on an end face (the test that survives a re-chamfer), guarded by
  a `BuildError` naming the defect on an empty selection. `model._chamfer_tips` is the
  last `_build` step, `bore_chamfer`'s exact `solid.chamfer(c, None, edges)` call.
  Default gear at 0.4 mm: **172 to 210 faces, 490 to 604 edges** -- matching 10-01's
  measured deltas exactly.
- The cap is pinned at each limit and one step either side, with its warning:
  - pitch circle (default gear): 1.75 mm -- "Tip chamfer reduced to 1.75 mm to keep
    it above the pitch circle."
  - tip land (face_width 1): 0.45 mm -- "Tip chamfer reduced to 0.45 mm to leave a
    land on the tooth tip between the two faces' chamfers."
  - involute flank ({profile_shift 1.0, pressure_angle 14.5}): 2.937 mm -- "Tip
    chamfer reduced to 2.937 mm to keep it on the involute flank, above the straight
    lead-in from the root fillet."
- The 405-set grid test (pure maths, no kernel) confirms the rounded cap stays at
  least `TIP_CHAMFER_MARGIN / 2` inside the measured boundary on every set: smallest
  margin **0.0004999999999999449 mm** (half of `TIP_CHAMFER_MARGIN`'s 0.001 mm, the
  precision edge the margin exists for).
- `bench/tip_chamfer_spike.py` now imports `spline_start` from `spur.calc` instead of
  carrying its own copy, exactly as 10-01's docstring promised; the spike still runs
  unchanged (not re-run this plan -- its own numbers are unaffected by an import
  swap).
- `grep -c 'type: ignore' src/spur/model.py` is **5** (was 4): one new suppression,
  the chamfer call on a `cq.Shape`, in `_cut_bore`'s exact shape.
- `tests/regression/pre_v0_2.json` never changed (`git diff --exit-code`, checked
  after each task); every record replays with `tip_chamfer_effective` null.

## Task Commits

Each task was committed atomically:

1. **Task 1: One tip-chamfer link end to end** - `b92ef7e` (feat)
2. **Task 2: Pin the cap at each limit, its warning and its rounding contract** -
   `9238275` (test)

_Plan metadata (this SUMMARY, STATE.md, ROADMAP.md) is committed separately below._

## Files Created/Modified

- `src/spur/params.py` - `tip_chamfer` field, class docstring
- `src/spur/calc.py` - `TIP_CHAMFER_MARGIN`, `spline_start`, `tip_chamfer_limit`,
  `tip_chamfer_effective`, `DerivedDimensions.tip_chamfer_effective`, the `derive()`
  warning and construction line
- `src/spur/model.py` - import list, `_outline` reads `spline_start`, `_tip_edges`,
  `_chamfer_tips`, `_build`'s new last step
- `src/spur/static/app.js` - one `DIMS` row
- `tests/test_api.py` - the 24-name typed-contract set, the end-to-end link test
- `tests/test_calc.py` - the 15-row cap test, the field-bound test, the
  no-other-number test (5 gears), `spline_start`'s three cases, the 405-set grid test
- `tests/test_model.py` - four `test_builds_one_valid_solid` rows
- `tests/test_cli.py` - CLI/API parity test for a capped tip chamfer
- `bench/tip_chamfer_spike.py` - imports `spline_start` from `spur.calc` instead of a
  local copy

## Decisions Made

See `key-decisions` in the frontmatter: `tip_chamfer_limit`'s tuple-`min()` shape, and
why `_chamfer_tips` assigns the chamfer result to a variable before returning it
(mypy's `no-any-return` check on `Mixin3D.chamfer`'s untyped return).

## Deviations from Plan

None - plan executed exactly as written. Every planned value (the three caps, the
warnings, `spline_start`'s three radii, the 405-set grid count, the face/edge deltas)
matched the code on first measurement; nothing needed reconciling against the plan's
`<interfaces>` numbers.

## Issues Encountered

None. `make verify` passed clean after both tasks (no lint, type or import-boundary
fixes needed); the 30 s `gsd_run query commit` timeout noted in STATE.md was not
tested this session (both commits used plain `git commit` directly, per 10-CONTEXT.md
D-17's process note, and completed inside the hook's own ~80 s warm budget).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- 10-03 proves the cut on the built solid (D-12/D-13's matrix column, built-solid
  proof, tripwire and empty-selection guard test) -- this plan's `_tip_edges` and
  `_chamfer_tips` are ready for that proof; the face/edge deltas recorded above
  (172→210, 490→604 at 0.4 mm) are 10-01's measured numbers confirmed again here on
  the shipped code.
- 10-04's cost sweep and 10-05's decision-log entry (L29) and README rows are
  unblocked; nothing in this plan's `<interfaces>` needs revisiting.
- REQ-tip-chamfer and REQ-tip-chamfer-capped stay unmarked in REQUIREMENTS.md until
  the last of 10-01..10-05 finishes (shared-ID gate: `requirements.ready-ids` reports
  0/2 ready today, 10-01 done, 10-03/10-04/10-05 still open).
- No blockers.

---
*Phase: 10-tooth-tip-chamfer*
*Completed: 2026-09-28*

## Self-Check: PASSED

- FOUND: src/spur/params.py
- FOUND: src/spur/calc.py
- FOUND: src/spur/model.py
- FOUND: .planning/phases/10-tooth-tip-chamfer/10-02-SUMMARY.md
- FOUND commit: b92ef7e
- FOUND commit: 9238275
- FOUND commit: 8f0a2b2 (metadata)
