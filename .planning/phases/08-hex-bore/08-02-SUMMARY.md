---
phase: 08-hex-bore
plan: 02
subsystem: cad
tags: [hex-bore, cadquery, derived-dimensions, bore-rim, regression-fixture]

# Dependency graph
requires:
  - phase: 07-foundation
    provides: generalized edge selector (calc.bore_rim_limit as the designated seam) and the regression fixture this plan's replay change builds on
provides:
  - "bore_hex field in GearParams' Bore group, after bore_flat; CLI flag and /api/schema entry fall out of the schema (L02)"
  - "calc.hex_across_flats(p) and calc.bore_mouth_limit(p): the hex's effective across-flats and the chamfered mouth's farthest reach"
  - "calc.bore_rim_limit hex branch (circumradius); calc.recess_radii's hub clearance re-datumed to bore_mouth_limit(p) for every bore shape"
  - "DerivedDimensions.hex_across_flats / .hex_across_corners, both null off a hex bore; bore_effective null on a hex bore (D-04)"
  - "model._cut_bore hex replacement branch: a hexagonal prism cut in place of the round/D-flat profile, chamfered on both rims via the unchanged selector"
  - "app.js DIMS rows for both new fields"
  - "test_pre_v0_2.py's replay compares recorded fields exactly and requires every field added since the capture to be null (REQ-derived-dimensions-additive)"
  - "17-row edge-selector matrix (10 pre-Phase-8 + 7 hex), a built-solid measurement test, a determinism test, a pre-Phase-8-bound regression test, and a three-shape recess-wall invariant test"
affects: [08-03-PLAN.md, 08-04-PLAN.md]

# Actuals (#2632) — pairs with the plan's estimate to calibrate future estimates.
# Same estimateTokens scale (chars/4 over the realized diff), never a harness token count.
actuals:
  tokens: 6676
  tasks: 2
  commits: 3

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "bore_mouth_limit(p): the chamfered mouth's farthest reach, generalizing the round/D-flat 'rim + chamfer' idiom to a hex's corner-carried 2c/sqrt(3)"
    - "recess_radii()'s hub clearance reads from the shape-general bore_mouth_limit(p), not bore_radius(p) -- every future bore profile clears its own chamfered mouth by construction"

key-files:
  created: []
  modified:
    - src/spur/params.py
    - src/spur/calc.py
    - src/spur/model.py
    - src/spur/static/app.js
    - tests/regression/test_pre_v0_2.py
    - tests/test_api.py
    - tests/test_model.py
    - tests/test_calc.py

key-decisions:
  - "recess_radii()'s hub clearance is measured from bore_mouth_limit(p) (the chamfered mouth), not the chamfer added on top of bore_radius(p) -- a hex's chamfer reaches a corner at 2c/sqrt(3), not c, so the old formula would have undercounted by 0.155c and driven the recess into an invalid solid at a 3 mm chamfer on the default 6 mm hex (measured on the pinned kernel, research PITFALLS.md Pitfall 1). Round and D-flat compute the identical floats as before, in the same order, so the fixture stays byte-unchanged."
  - "The replay's comparison changed, not the fixture: DerivedDimensions gaining two fields turned the old got == record['derived'] red for all 44 records for a reason that is not a Phase 8 bug. The fixture's recorded fields still compare exactly (warning text included); every field added since the capture must additionally read null (REQ-derived-dimensions-additive)."
  - "The hex is a replacement branch in _cut_bore (if/elif/else), not an intersection layered on the round hole -- bore_d and bore_flat are ignored when bore_hex > 0 (D-01); the warning naming them is 08-03's task, not this plan's."

patterns-established:
  - "A shape-general 'farthest point' pair -- bore_rim_limit (exact) and bore_mouth_limit (chamfered) -- feeds every consumer that needs the bore's true extent, so a later bore profile (Phase 9's keyway) only has to extend these two functions, not every caller."

requirements-completed: [REQ-hex-bore, REQ-derived-dimensions-additive]

coverage:
  - id: D1
    description: "bore_hex builds through the API, the CLI (schema-generated) and the form; /api/info prints hex_across_flats 6.15 and hex_across_corners 7.101 with bore_effective null on ?bore_hex=6; app.py and cli.py needed no edits"
    requirement: "REQ-hex-bore"
    verification:
      - kind: integration
        ref: "tests/test_api.py::test_a_hex_bore_link_is_served_with_its_two_numbers"
        status: pass
      - kind: other
        ref: ".venv/bin/spur info --bore-hex 6 (hex_across_flats 6.15, hex_across_corners 7.101, bore_effective null)"
        status: pass
    human_judgment: false
  - id: D2
    description: "The hex prism cuts through 12 chamfered rim edges (6 LINE per face) via the unchanged selector, across every recess configuration, no round bore, a recess at its hub clearance, and a hex wider than the round bore; the pre-Phase-8 bound (bore_radius) would have chamfered nothing on that last case"
    requirement: "REQ-hex-bore"
    verification:
      - kind: integration
        ref: "tests/test_model.py::test_each_edge_selector_picks_exactly_its_own_edges[hex-*] (7 rows)"
        status: pass
      - kind: integration
        ref: "tests/test_model.py::test_the_pre_hex_rim_bound_would_have_chamfered_nothing_on_a_hex_wider_than_the_round_bore"
        status: pass
    human_judgment: false
  - id: D3
    description: "The built hex measures the printed across-flats and across-corners within 5e-4 mm, every corner sits at bore_rim_limit(p) within TOL, and a flat faces +X; one hex link builds identically twice (topology and volume, L05)"
    requirement: "REQ-hex-bore"
    verification:
      - kind: integration
        ref: "tests/test_model.py::test_a_hex_bore_measures_the_across_flats_and_corners_it_reports"
        status: pass
      - kind: integration
        ref: "tests/test_model.py::test_the_same_hex_link_builds_the_same_solid_twice"
        status: pass
    human_judgment: false
  - id: D4
    description: "The recess keeps exactly MIN_WALL (0.4000 mm) from the chamfered bore mouth for round, D-flat and hex bores alike at a 3 mm chamfer -- the assumption-delta invariant recess_radii()'s change rests on"
    requirement: "REQ-hex-bore"
    verification:
      - kind: integration
        ref: "tests/test_model.py::test_a_recess_at_its_hub_clearance_keeps_min_wall_from_the_chamfered_bore_mouth[round|d-flat|hex]"
        status: pass
    human_judgment: false
  - id: D5
    description: "The 19 pre-v0.2 DerivedDimensions fields keep their names, types and values across all 44 records; the two fields added this phase read null for every pre-v0.2 set; tests/regression/pre_v0_2.json stayed byte-unchanged through both commits"
    requirement: "REQ-derived-dimensions-additive"
    verification:
      - kind: integration
        ref: "tests/regression/test_pre_v0_2.py::test_a_pre_v0_2_parameter_set_derives_the_same_dimensions (44 records)"
        status: pass
      - kind: other
        ref: "git diff --exit-code tests/regression/pre_v0_2.json"
        status: pass
    human_judgment: false

# Metrics
duration: 55min
completed: 2026-09-26
status: complete
---

# Phase 8 Plan 2: Hex Bore End to End and Proven on the Solid Summary

**A hex bore replaces the round/D-flat profile on `?bore_hex=6`, chamfers 12 rim edges through the unchanged Phase 7 selector, and measures 6.15 mm across flats / 7.101 mm across corners on the built solid -- with the 44-record regression fixture byte-unchanged.**

## Performance

- **Duration:** 55 min
- **Started:** 2026-09-26T15:01:43Z (per STATE.md's prior session marker)
- **Completed:** 2026-09-26
- **Tasks:** 2 (Task 1: tracer, six files, two commits; Task 2: proof, two test files, one commit)
- **Files modified:** 8

## Accomplishments

- `bore_hex` lives in `GearParams`' Bore group, right after `bore_flat`, with `ge=0, le=200` and a help sentence naming commodity hex sizes as examples only (no standard cited). No edit to `app.py` or `cli.py` -- both are schema-generated (L02).
- `calc.hex_across_flats(p)` and `calc.bore_mouth_limit(p)` are new; `calc.bore_rim_limit(p)` grows a hex branch returning the circumradius (across-flats over sqrt(3), L26's designated seam). `_bore_rim_edges` needed zero selector changes to pick up the twelve `LINE` edges.
- `recess_radii()`'s hub clearance now reads `bore_mouth_limit(p) + MIN_WALL` instead of `bore_radius(p) + chamfer + MIN_WALL` -- a hex's chamfer reaches its corner at `2c/sqrt(3)`, not `c`, and the old formula would have driven a 3 mm chamfer on a 6 mm hex into an invalid solid (measured at 2.586 mm, kernel failure at 3 mm, research PITFALLS.md Pitfall 1). Round and D-flat compute identical floats, in identical order, so every pre-v0.2 record stayed unchanged.
- `DerivedDimensions` gains `hex_across_flats` and `hex_across_corners`, both `float | None`, null off a hex bore; `bore_effective` is null on a hex bore too (D-04) -- a hexagon has no diameter.
- `model._cut_bore` restructures into an `if/elif/else` with the hex as the first, replacing branch: `bore_d` and `bore_flat` are ignored (not refused) when `bore_hex > 0` (D-01); the ignored-field warning is 08-03's task.
- `app.js`'s `DIMS` array gains two rows; `renderInfo`'s null-skip already covers them.
- `tests/regression/test_pre_v0_2.py`'s replay now compares the fields a record holds exactly and asserts every field added to `DerivedDimensions` since the capture is null -- the mechanism that let two new fields land without touching the fixture or loosening any tolerance.
- Task 2 proves the geometry: a 17-row edge-selector matrix (10 pre-Phase-8 + 7 hex, all reading `Counter({"LINE": 12})` on the rim), a measurement test reading the built solid's own rim-edge vertices, a two-independent-builds determinism test, a regression test showing the pre-Phase-8 bound would have chamfered nothing on a hex wider than the round bore, and a three-shape (round/D-flat/hex) recess-wall invariant test at a 3 mm chamfer.

## Task Commits

Each task was committed atomically (two commits for Task 1 per the plan's explicit split, one for Task 2):

1. **Task 1a: the replay learns additive fields** - `89fad59` (test) -- `test_a_pre_v0_2_parameter_set_derives_the_same_dimensions` compares recorded fields exactly and requires added fields null.
2. **Task 1b: the hex bore, end to end** - `2eac59b` (feat) -- `bore_hex`, `hex_across_flats`, `bore_mouth_limit`, the hex branch of `bore_rim_limit`, the two new `DerivedDimensions` fields, `model._cut_bore`'s hex branch, and both `app.js` rows.
3. **Task 2: prove the hex on the built solid** - `a472215` (test) -- the 7 hex matrix rows, the measurement/determinism/regression/recess-wall tests, and `calc.py`'s two new unit tests.

**Plan metadata:** commit pending (this SUMMARY + STATE.md + ROADMAP.md + REQUIREMENTS.md).

## Files Created/Modified

- `src/spur/params.py` - `bore_hex` field declared between `bore_flat` and `bore_clearance`; class docstring names hex alongside D-flat
- `src/spur/calc.py` - `hex_across_flats`, `bore_mouth_limit`, `bore_rim_limit`'s hex branch, `recess_radii`'s re-datumed hub clearance, two new `DerivedDimensions` fields, `derive()`'s three bore numbers
- `src/spur/model.py` - `_cut_bore`'s hex replacement branch, `_bore_rim_edges`'s docstring extended, `hex_across_flats` import
- `src/spur/static/app.js` - two `DIMS` rows for the hex fields
- `tests/regression/test_pre_v0_2.py` - the additive-fields comparison contract
- `tests/test_api.py` - the openapi field-set/unit assertions and the new hex-link end-to-end test
- `tests/test_model.py` - 2 new `test_builds_one_valid_solid` rows, 7 hex matrix rows, the gate rewrite, and 4 new tests
- `tests/test_calc.py` - 2 new unit tests for the hex branch and `derive()`'s three bore numbers

## Decisions Made

- `recess_radii()`'s hub clearance is measured from `bore_mouth_limit(p)` (the chamfered mouth), never `bore_radius(p) + chamfer` -- see key-decisions above; this is Task 1's assumption-delta correction (CONTEXT's "the corner plus chamfer plus MIN_WALL" read as the *chamfered* corner, per the plan's `<assumption_delta_decision>` block), and Task 2's invariant test proves it holds for round and D-flat too.
- The replay's comparison, not the fixture, absorbed the two new `DerivedDimensions` fields (07-CONTEXT D-10's "exact equality on all 19 fields" read literally, plus REQ-derived-dimensions-additive's null rule).
- The hex is a replacement branch, never an intersection with the round profile (D-01) -- `bore_d`/`bore_flat` stay live in the schema and are simply ignored when `bore_hex > 0`.

## Deviations from Plan

None - plan executed exactly as written. The plan's own `<assumption_delta_decision>` and Flagged Assumptions (A1-A3) already anticipated and resolved the two non-trivial calls (the chamfered-corner correction to `recess_radii()`'s datum, and the replay's comparison-not-fixture edit) before execution began, so nothing needed a Rule 4 stop here.

## Issues Encountered

None. The hex hole construction (`cq.Workplane("XY").polygon(...).extrude(...)`) needed a multi-line chained-call layout, not the single-line form named in the acceptance criteria's literal `grep`, to fit under the project's 100-column limit (L16) while keeping the exact substring `polygon(6, hex_across_flats(p), circumscribed=True)` intact on one line for that check.

## Measured Numbers (for the record)

- Built-solid measurement (`bore_hex=6`, `bore_chamfer=0`): every rim-edge vertex hypot equals `bore_rim_limit(p)` within `TOL` (1e-6 mm); across-corners and across-flats matched the printed 6.15 / 7.101 mm within `5e-4` mm; the rim-edge midpoint with the largest x sits at `x = 3.075, y = 0.0` within `1e-6` mm -- a flat on +X, as `_cut_bore`'s orientation comment states.
- Recess-wall invariant at a 3 mm chamfer, `recess_inner_d=1.0`: `r_in - mouth == MIN_WALL` (0.4000 mm) within `1e-6` mm for round, D-flat and hex alike.
- `tests/regression/pre_v0_2.json`: `git diff --exit-code` passed after every commit -- never touched, byte-identical throughout.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `bore_hex`, `calc.bore_rim_limit`/`bore_mouth_limit`, and the re-datumed `recess_radii()` are in place for 08-03 to add the D-03 refusal rules (corner-vs-root, chamfer-vs-side) and the D-02 ignored-field warning on this proven slice.
- 08-04's build-time sweep can run against a working hex bore across the full parameter range up to `bore_hex=200`.
- No blockers.

## Self-Check: PASSED

All 8 key files found on disk; all 3 commit hashes (89fad59, 2eac59b, a472215) found in
`git log --oneline --all`; every plan-level `<verification>` command re-run and green;
`git diff --exit-code tests/regression/pre_v0_2.json` exits 0.

---
*Phase: 08-hex-bore*
*Completed: 2026-09-26*
