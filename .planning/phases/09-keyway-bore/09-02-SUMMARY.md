---
phase: 09-keyway-bore
plan: 02
subsystem: geometry
tags: [keyway, bore, cadquery, derived-dimensions, edge-selection]

# Dependency graph
requires:
  - phase: 09-keyway-bore
    provides: "09-01's amended datum (D-14), refusal shape (D-09/D-10) and SC4 wording the tests here implement against"
  - phase: 08-hex-bore
    provides: "bore_rim_limit/bore_mouth_limit as the shape-general pair this phase extends; check()'s if/elif branch shape; the additive DerivedDimensions replay rule"
provides:
  - "GearParams.keyway_width / .keyway_depth, declared between bore_flat and bore_hex (D-17), no standard size in help text (D-16)"
  - "calc.keyway_width_effective(p), calc.keyway_corner_radius(p); bore_mouth_limit(p) takes the max with the un-chamfered keyway corner so recess_radii() yields to it, never a 422 (D-09)"
  - "DerivedDimensions.keyway_floor_to_wall / .keyway_width_effective, null with no keyway (D-15)"
  - "model._cut_keyway(solid, p), a box cut after the chamfered _cut_bore (D-06), keeping the slot's own edges sharp (D-05)"
  - "two app.js DIMS rows"
  - "the keyway proven on the built solid: floor datum, chamfer-survives/sharp-slot, pre-keyway rim-selector counts (D-07), recess yield"
affects: [09-03-PLAN.md, 09-04-PLAN.md, 09-05-PLAN.md]

# Actuals (#2632)
actuals:
  tokens: 8103
  tasks: 2
  commits: 2

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "A new bore-composing cut goes in model._build strictly after the bore it composes with has been cut and chamfered, so the rim selector never sees the new feature's edges (D-06) -- keyway follows the hex/D-flat precedent of a shape-general bore_mouth_limit(p) every recess/refusal consumer reads"
    - "A selector-matrix test that must measure a pipeline stage before a later feature exists monkeypatches that later step to a no-op and builds with _build_checked (bypassing the lru_cache), rather than adding a second selector on the finished solid (D-07)"
    - "A composing feature's floor/width datum is read back from the kernel by geometry (PLANE face normal + BoundingBox), not re-derived from the parameters, and compared to the same calc.py functions derive() uses"

key-files:
  created: []
  modified:
    - src/spur/params.py
    - src/spur/calc.py
    - src/spur/model.py
    - src/spur/static/app.js
    - tests/test_api.py
    - tests/test_model.py
    - tests/test_calc.py

key-decisions:
  - "D-14's datum verified on the built solid: floor y = bore_radius(p) + keyway_depth (5.975 mm), x-extent = keyway_width_effective(p) (3.15 mm), and floor y minus the kernel-read bore-wall radius (4.575 mm) = keyway_depth (1.4 mm), all within TOL, for both a D-flat and a round bore"
  - "D-09's yield measured on the kernel: the default keyed link's recess moves out to 13.158/25.158 mm with no warning; a 3 x 5 mm keyway narrows it to 3.93 mm; a 3 x 9 mm keyway drops it -- never a ValidationError"
  - "D-07's amended proof taken exactly as amended in 09-01: the selector matrix keeps its pre-keyway rim/floor counts with _cut_keyway patched to a no-op (11 new rows), and a spy on the real chamfered pipeline proves the rim selector runs exactly once, on the pre-keyway rim, for both a keyed D-flat and a keyed round bore"
  - "D-05 proven on the built solid: the chamfer survives the slot (4 chamfer-mouth circles, 4 CONE faces, split by the slot on each end face) and the slot's own edges stay sharp (4 side lines at nominal half-width, 2 floor lines at the nominal floor, both end faces)"

patterns-established:
  - "keyway_width_effective/keyway_corner_radius follow hex_across_flats/bore_rim_limit's shape: a pure calc.py helper returning 0.0 when the feature is off, feeding both model.py's cut and calc.py's own bore_mouth_limit/derive()"

requirements-completed: []  # None marked complete: all five (REQ-keyway-bore, REQ-keyway-composes-with-d-flat, REQ-keyway-wall-refused, REQ-hex-rim-chamfer, REQ-bore-derived-numbers) are also declared by sibling plans 09-03..09-05, which have not yet produced a SUMMARY (shared-ID gate, requirements.ready-ids reported 0/5 ready)

coverage:
  - id: D1
    description: "A keyed D-flat link builds end to end through the API, CLI and form schema and prints its floor-to-wall (10.55 mm) and width (3.15 mm), with the recess moved to 13.158/25.158 mm and no warnings"
    requirement: REQ-keyway-bore
    verification:
      - kind: integration
        ref: "tests/test_api.py::test_a_keyed_link_is_served_with_its_two_numbers"
        status: pass
      - kind: other
        ref: ".venv/bin/spur info --keyway-width 3 --keyway-depth 1.4"
        status: pass
    human_judgment: false
  - id: D2
    description: "The keyway floor sits at bore_radius(p) + keyway_depth, measured on the built solid against the kernel-read bore-wall radius, for both a D-flat and a round bore (D-14)"
    requirement: REQ-keyway-bore
    verification:
      - kind: integration
        ref: "tests/test_model.py::test_a_keyway_floor_sits_keyway_depth_outside_the_as_cut_bore_wall"
        status: pass
    human_judgment: false
  - id: D3
    description: "bore_flat stays when a keyway is added: the default keyed link still carries its D-flat face at the expected x"
    requirement: REQ-keyway-composes-with-d-flat
    verification:
      - kind: integration
        ref: "tests/test_model.py::test_a_keyway_floor_sits_keyway_depth_outside_the_as_cut_bore_wall[d-flat]"
        status: pass
      - kind: unit
        ref: "tests/test_api.py::test_a_keyed_link_is_served_with_its_two_numbers (bore_effective == 9.15)"
        status: pass
    human_judgment: false
  - id: D4
    description: "The bore chamfer survives the keyway slot and the slot's own edges stay sharp on both a D-flat and a round bore; the rim selector takes exactly the pre-keyway edges in the real chamfered pipeline; 11 matrix rows keep the pre-keyway counts"
    requirement: REQ-hex-rim-chamfer
    verification:
      - kind: integration
        ref: "tests/test_model.py::test_the_bore_chamfer_survives_the_keyway_and_the_slot_edges_stay_sharp"
        status: pass
      - kind: integration
        ref: "tests/test_model.py::test_the_rim_chamfer_on_a_keyed_bore_takes_the_pre_keyway_edges"
        status: pass
      - kind: integration
        ref: "tests/test_model.py::test_each_edge_selector_picks_exactly_its_own_edges[keyway-*] (11 rows)"
        status: pass
    human_judgment: false
  - id: D5
    description: "DerivedDimensions.keyway_floor_to_wall and .keyway_width_effective report the correct numbers and are null with no keyway; the recess yields to the keyway corner with the existing narrow/drop warnings, never a 422; the Phase 7 fixture stays byte-unchanged"
    requirement: REQ-bore-derived-numbers
    verification:
      - kind: unit
        ref: "tests/test_calc.py::test_a_keyway_reports_floor_to_wall_and_width_and_null_without_one"
        status: pass
      - kind: unit
        ref: "tests/test_calc.py::test_the_recess_yields_to_a_keyway_and_says_so_only_when_it_narrows_or_drops"
        status: pass
      - kind: integration
        ref: "tests/regression/test_pre_v0_2.py"
        status: pass
    human_judgment: false

# Metrics
duration: 27min
completed: 2026-09-27
status: complete
---

# Phase 9 Plan 2: Keyway bore, end to end and proven on the solid Summary

**A rectangular keyway slot, cut after the chamfered bore so the chamfer survives and the slot's own edges stay sharp, composes with a D-flat by default and prints floor-to-wall (10.55 mm) and width (3.15 mm) on the default link, with the recess yielding instead of ever refusing.**

## Performance

- **Duration:** 27 min
- **Started:** 2026-09-27T13:12:43Z
- **Completed:** 2026-09-27T13:40:21Z
- **Tasks:** 2
- **Files modified:** 7

## Accomplishments
- `keyway_width`/`keyway_depth` fields (0 = off, `ge` 0, `le` 200, step 0.05) declared between `bore_flat` and `bore_hex` (D-17); help text states the DIN 6885 / ISO R773 `t2` convention and the ANSI B17.1 warning, no standard size cited (D-16).
- `calc.keyway_width_effective(p)` and `calc.keyway_corner_radius(p)`; `bore_mouth_limit(p)` takes the max of the chamfered rim reach and the un-chamfered keyway corner, so `recess_radii()` yields to it with `MIN_WALL` (D-09) — the default keyed link's recess moves from `(6.506, 12.506)` to `(6.579, 12.579)` mm with no warning.
- `model._cut_keyway` cuts a rectangular box (`cq.Solid.makeBox`) after the chamfered `_cut_bore`, so the chamfer is notched and the slot's own three edges (two sides, floor) stay sharp on every bore shape (D-05, D-06).
- `DerivedDimensions.keyway_floor_to_wall` (`bore_effective + keyway_depth`) and `.keyway_width_effective` (`keyway_width + bore_clearance`), both `null` with no keyway (D-15); two `app.js` `DIMS` rows.
- The datum, the chamfer-survives/sharp-slot proof, the pre-keyway rim-selector spy, 11 matrix rows and a recess-corner row all measured on the built solid and matching the plan's planning-time probes exactly.

## Task Commits

Each task was committed atomically:

1. **Task 1: One keyed link end to end** - `122c86b` (feat)
2. **Task 2: Prove the keyway on the built solid** - `863772e` (test)

**Plan metadata:** committed separately after this SUMMARY (docs).

## Files Created/Modified
- `src/spur/params.py` - `keyway_width`/`keyway_depth` fields; class docstring and `bore_clearance` help text updated
- `src/spur/calc.py` - `keyway_width_effective`, `keyway_corner_radius`; `bore_mouth_limit`'s keyway branch; two `DerivedDimensions` fields; `derive()`'s two new values
- `src/spur/model.py` - `_cut_keyway`; `_build`'s new step; `_bore_rim_edges`'s docstring note
- `src/spur/static/app.js` - two `DIMS` rows
- `tests/test_api.py` - the 23-field contract, the reordered hex-link assertion, `test_a_keyed_link_is_served_with_its_two_numbers`
- `tests/test_model.py` - 3 build rows, 11 keyway matrix rows (`_cut_keyway` patched out), the pre-keyway rim spy, the floor-datum test, the chamfer-survives/sharp-slot test, a recess-corner row, a determinism test
- `tests/test_calc.py` - `keyway_width_effective`/`keyway_corner_radius`/`bore_mouth_limit` and the recess it feeds; the floor-to-wall/width table; the recess narrow/drop warnings

## Measured Numbers (built-solid proof, both D-flat and round shapes agree)

- Floor: `ymin` 5.975 mm, `xlen` 3.150 mm, kernel-read bore-wall radius 4.575 mm, `ymin - wall` 1.4 mm (== `keyway_depth`), `ymin + wall` 10.55 mm (== `derive()`'s `keyway_floor_to_wall`, within 5e-4 mm).
- Chamfer survives the slot: 4 `CIRCLE` edges at the chamfer-mouth radius (4.975 mm), split by the slot on each end face; 4 `CONE` faces.
- Slot edges stay sharp: 4 `LINE` sides at `x = ±1.575` mm, 2 `LINE` floor lines at `y = 5.975` mm, both end faces hit in each set.
- Pre-keyway rim spy: exactly one call each, `Counter({"CIRCLE": 2, "LINE": 2})` (D-flat) and `Counter({"CIRCLE": 2})` (round).
- Recess-corner row (`keyway_depth=5`, `bore_chamfer=3`, `recess_inner_d=1.0`): measured mouth == the keyway corner (9.7037 mm), `r_in - mouth` = 0.4 mm exactly (`MIN_WALL`).
- `tests/regression/pre_v0_2.json` never changed (`git diff --exit-code` after both tasks and again after the full suite).

## Decisions Made
- No deviations from the plan's arithmetic or geometry: every planning-time probe number in `09-RESEARCH.md`/`09-CONTEXT.md`'s `<specifics>` reproduced exactly against the pinned kernel this session, including the 11-row matrix counts, the chamfer/sharp-slot counts (4/4/4/2), and the recess-corner clearance (0.4 mm exactly).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Renamed an unused lambda parameter to satisfy ruff's ARG005**
- **Found during:** Task 2 (the matrix's `_cut_keyway` patch)
- **Issue:** The plan's literal `lambda solid, p: solid` leaves `p` unused, which ruff's `ARG005` (enabled project-wide) flags as an error, failing `make lint`/`make verify`.
- **Fix:** Renamed the unused parameter to `_p` (ruff's default dummy-variable pattern), matching the project's existing convention for unused lambda/function arguments.
- **Files modified:** `tests/test_model.py`
- **Verification:** `make lint` clean; the monkeypatch still shadows `_cut_keyway` correctly (11 keyway matrix rows pass).
- **Committed in:** `863772e` (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 blocking — a lint-only rename, no behaviour change).
**Impact on plan:** None on the measured geometry or reported numbers; a required fix to keep `make verify` green.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
Ready for 09-03-PLAN.md (the refusals: D-02/D-03/D-10/D-11/D-12/D-13's `check()` rules, on this proven slice). `bore_mouth_limit(p)`'s keyway branch and `_cut_keyway` are in place and unchanged by refusal rules that only gate what reaches them. No blockers.

---
*Phase: 09-keyway-bore*
*Completed: 2026-09-27*

## Self-Check: PASSED
