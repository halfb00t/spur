---
phase: 11-body-cutouts
plan: 05
subsystem: calc
tags: [honeycomb, cutout, hex-cell-cap, raise-to-fit, one-pattern, cadquery]

# Dependency graph
requires:
  - phase: 11-02
    provides: "bench/honeycomb_spike.py's whole_cells/cell_count_floor/cells_within
      (D-07..D-09, D-13's raise-to-fit), the measured HEX_CELL_CAP = 120 cells and
      the star cut spelling, bench/RESULTS.md's '## Honeycomb cell-count spike
      (Phase 11, D-24)' section"
  - phase: 11-04
    provides: "_cut_body(solid, p, pr)'s shared cut-call shape, cutout_walls,
      calc._under_min_wall/_listed, the one-pattern rule's chosen-tuple shape and
      the elif chain each cutout branch follows"
provides:
  - "GearParams.hex_cell/hex_wall (Honeycomb group, every default 0, L05), declared
    after Holes (D-19)"
  - "calc.HEX_CELL_CAP = 120, whole_cells/cell_count_floor/cells_within moved from
    the spike into calc.py unchanged (the spike imports them back), calc.hex_cells
    applying D-13's raise-to-fit"
  - "calc.cutout_walls' honeycomb branch (_hex_reach/_point_segment_distance): exact
    nearest-edge and farthest-vertex reach on the cut cells, not the whole-cell
    test's conservative circumradius"
  - "model._cell_cutters/_cut_body's honeycomb branch: hexagonal prisms at
    hex_cells(p, rf)'s applied size and centres, in the one shared cut call"
  - "DerivedDimensions.hex_cell_effective/hex_cell_count; check()'s honeycomb rules
    (D-10, D-14, D-15) and the one-pattern rule's third selector
    (REQ-one-cutout-pattern complete)"
affects: [11-06, 11-07, 11-08, 11-09]

# Actuals (#2632)
actuals:
  tokens: 12237
  tasks: 2
  commits: 2
  plan_head_before: 94e9793b27ea00c50808aa78a460ea03738ed3b4
  plan_head_after: baad230b6d69fcb7ff6a53ed3af2d47891d4aa5e

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "calc._point_segment_distance/_hex_reach: the exact minimum distance from the
      axis to a hexagon's nearest edge (a flat can be nearer than any corner) and
      its farthest vertex -- the honeycomb's own reading of the cap-function shape
      root_fillet/recess_fillet/tip_chamfer_limit already established, generalised
      from a circle-vs-line tangent to a polygon's own geometry."

key-files:
  created: []
  modified:
    - src/spur/params.py
    - src/spur/calc.py
    - src/spur/model.py
    - src/spur/static/app.js
    - bench/honeycomb_spike.py
    - tests/test_api.py
    - tests/test_model.py
    - tests/test_calc.py
    - tests/test_cli.py

key-decisions:
  - "HEX_CELL_CAP = 120, written from bench/RESULTS.md's '**Cap:** HEX_CELL_CAP =
    120 -- teeth=200 module=10 target=125 reads 7.15 s of 7.5 s; the next row
    (150 cells) reads 7.95 s.' line and nowhere else (D-12, D-24)."
  - "The tracer link (?hex_cell=3&hex_wall=1) cuts 18 whole cells (6 at 8 mm circle
    radius, 12 at 10.583 mm), walls 1.525/2.149 mm, +108 PLANE +10 CYLINDER
    +10 TORUS faces, +494 edges -- reproduced exactly on the pinned kernel,
    matching the plan's <interfaces> block to the last measured digit."
  - "The walls are computed exactly on the cut polygons (point-to-segment distance
    to each of a hexagon's six edges, not the whole-cell test's conservative
    circumradius): the naive centre_radius - corner_reach bound reads 6.268 mm on
    the tracer's inner ring, 0.232 mm short of the true 6.5 mm a cell's flat gives
    when it faces the axis (Flagged Assumption A3, L08)."
  - "A 200-tooth request (module 1.75, the field's default) is raised from 3 mm to
    25.25 mm across flats, cutting exactly 120 cells (the cap) -- matching
    bench/RESULTS.md's own module-1.75 confirmation row exactly."
  - "derive()'s measured cost (arm64, Python 3.12.13, 2026-09-29, the honeycomb
    spike's own host): 14.1 usec on GearParams() (no honeycomb, beside 09-05's
    11.5 usec baseline), 115 usec on the tracer link, 15.6 msec at the heaviest
    input (teeth=200, module=10, hex_cell=3, hex_wall=0.4) -- recorded in
    hex_cells' docstring; no cache added."
  - "Per-bore-shape honeycomb counts and walls measured and pinned: d-flat/round 18
    cells 1.525/2.149 mm, hex bore 24 cells 1.184/2.149 mm, keyed round 12 cells
    2.709/2.149 mm, no bore 30 cells 2.5/2.149 mm -- each reproduced exactly."

patterns-established:
  - "A pattern's own DerivedDimensions pair (hex_cell_effective/hex_cell_count)
    follows spoke_fillet_effective, completing the ten cutout fields D-20 named;
    the three cutout patterns (spokes, holes, honeycomb) now share one elif chain
    in both check() and cutout_walls()."

requirements-completed: [REQ-honeycomb-cutout, REQ-one-cutout-pattern,
  REQ-cutout-conflicts-refused-early, REQ-cutout-derived-numbers]

# Coverage metadata (#1602)
coverage:
  - id: D1
    description: "The honeycomb tracer (?hex_cell=3&hex_wall=1) cuts 18 whole
      hexagonal cells through the default gear in one cut call, through the API,
      CLI and form schema, with the cell count riding in the DIMS row's label"
    requirement: "REQ-honeycomb-cutout"
    verification:
      - kind: integration
        ref: "tests/test_model.py#test_the_honeycomb_link_cuts_eighteen_whole_cells"
        status: pass
      - kind: e2e
        ref: "tests/test_api.py#test_a_honeycomb_link_is_served_with_its_cells"
        status: pass
      - kind: e2e
        ref: "tests/test_cli.py#test_cli_and_api_print_the_same_honeycomb_document"
        status: pass
    human_judgment: false
  - id: D2
    description: "HEX_CELL_CAP is written exactly from bench/RESULTS.md's measured
      cap; whole_cells/cell_count_floor/cells_within moved into spur.calc
      unchanged and the spike imports them back (one definition, L08)"
    requirement: "REQ-honeycomb-cutout"
    verification:
      - kind: other
        ref: ".venv/bin/python -c \"import re, pathlib, bench.honeycomb_spike as s, spur.calc as c; cap = int(re.search(r'^\\*\\*Cap:\\*\\* HEX_CELL_CAP = ([0-9]+)', pathlib.Path('bench/RESULTS.md').read_text(), re.M).group(1)); assert c.HEX_CELL_CAP == cap and s.whole_cells is c.whole_cells and s.cells_within is c.cells_within and s.cell_count_floor is c.cell_count_floor\""
        status: pass
    human_judgment: false
  - id: D3
    description: "A 200-tooth request is raised in 0.05 mm steps to the first size
      whose exact whole-cell count fits the cap, with a warning naming the
      requested size, the applied size and the cap"
    requirement: "REQ-honeycomb-cutout"
    verification:
      - kind: unit
        ref: "tests/test_calc.py#test_a_honeycomb_over_the_cap_is_raised_in_field_steps_to_the_first_size_that_fits"
        status: pass
      - kind: unit
        ref: "tests/test_calc.py#test_a_count_exactly_at_the_cap_is_not_raised"
        status: pass
      - kind: unit
        ref: "tests/test_calc.py#test_the_count_floor_never_exceeds_the_exact_count"
        status: pass
    human_judgment: false
  - id: D4
    description: "Every honeycomb that cannot exist is refused before any CAD work
      (a wall under MIN_WALL, a missing wall, a cell that rounds to 0, no whole
      cell fitting), and the one-pattern rule now covers all three selectors"
    requirement: "REQ-cutout-conflicts-refused-early"
    verification:
      - kind: unit
        ref: "tests/test_calc.py#test_a_honeycomb_rule_refuses_one_step_past_it_and_names_its_fields"
        status: pass
      - kind: unit
        ref: "tests/test_calc.py#test_three_cutout_patterns_are_refused_naming_all_three"
        status: pass
      - kind: unit
        ref: "tests/test_calc.py#test_a_honeycomb_wall_without_a_cell_is_ignored_and_named"
        status: pass
      - kind: e2e
        ref: "tests/test_api.py#test_a_honeycomb_that_cannot_exist_is_422_naming_its_fields"
        status: pass
      - kind: e2e
        ref: "tests/test_cli.py#test_a_honeycomb_wall_under_min_wall_exits_2_and_names_it"
        status: pass
    human_judgment: false
  - id: D5
    description: "The honeycomb's two derived fields and its thinnest walls are
      exact on the cut cells themselves, per bore shape, and the DerivedDimensions
      key order follows the recess numbers as D-20 specifies"
    requirement: "REQ-cutout-derived-numbers"
    verification:
      - kind: unit
        ref: "tests/test_calc.py#test_the_honeycomb_walls_are_measured_on_the_cut_cells"
        status: pass
      - kind: unit
        ref: "tests/test_calc.py#test_the_cutout_numbers_follow_the_recess_numbers_in_order"
        status: pass
      - kind: unit
        ref: "tests/test_calc.py#test_a_honeycomb_cuts_whole_cells_only_on_an_axis_centred_lattice"
        status: pass
    human_judgment: false
  - id: D6
    description: "hex_cell/hex_wall are 0-100 mm fields; derive()'s measured cost
      at the default gear, the tracer link and the heaviest input is recorded"
    requirement: "REQ-honeycomb-cutout"
    verification:
      - kind: unit
        ref: "tests/test_calc.py#test_the_honeycomb_fields_are_bounded_zero_to_a_hundred"
        status: pass
      - kind: other
        ref: "grep -cE 'timeit|usec|.s| us ' src/spur/calc.py (>=1 line inside def hex_cells)"
        status: pass
    human_judgment: false

# Metrics
duration: ~50min
completed: 2026-09-29
status: complete
---

# Phase 11 Plan 05: Honeycomb Cutout Pattern Summary

**The honeycomb's third cutout branch: whole-cell axis-centred lattice moved from the spike into `calc.py`, `HEX_CELL_CAP = 120` written from the measured spike, cell size raised in 0.05 mm steps above the cap, exact walls read off the cut hexagons, and all four honeycomb refusals plus the third one-pattern selector.**

## Performance

- **Duration:** ~50 min
- **Tasks:** 2 (both `type="auto" tdd="true"`)
- **Files modified:** 9 (`src/spur/params.py`, `src/spur/calc.py`, `src/spur/model.py`,
  `src/spur/static/app.js`, `bench/honeycomb_spike.py`, `tests/test_api.py`,
  `tests/test_model.py`, `tests/test_calc.py`, `tests/test_cli.py`)

## Accomplishments

- Two new `GearParams` fields (`hex_cell`, `hex_wall`) in a `Honeycomb` schema
  group, declared after `Holes`, every default 0 (D-19) -- the API, CLI and web
  form gained the pattern from one model change.
- `calc.HEX_CELL_CAP = 120`, written from `bench/RESULTS.md`'s measured
  `**Cap:**` line and nowhere else (D-12, D-24); `whole_cells`, `cell_count_floor`
  and `cells_within` moved from `bench/honeycomb_spike.py` into `calc.py`
  unchanged -- the spike now imports them back, so there is one definition of the
  lattice and the raise (L08).
- `calc.hex_cells(p, rf)`: the applied across-flats and the cell centres, D-13's
  raise-to-fit over the web annulus (`bore_mouth_limit(p) + hex_wall` to
  `rf - hex_wall`) -- the one result `check()`, `cutout_walls()`, `derive()` and
  `model._cell_cutters` all read (L08).
- `calc.cutout_walls`'s honeycomb branch (`_hex_reach`/`_point_segment_distance`):
  the exact nearest-edge and farthest-vertex reach on the cut polygons, not the
  whole-cell test's conservative circumradius -- the naive bound would have
  under-reported the tracer's hub wall by 0.232 mm (Flagged Assumption A3).
- `model._cell_cutters`/`_cut_body`'s honeycomb branch: hexagonal prisms at
  `hex_cells(p, rf)`'s applied size and centres, cut in the plan's one shared
  `cut(*cutters)` call alongside spokes and holes (`grep -c '\.cut('` stays 5).
- Two new `DerivedDimensions` fields (`hex_cell_effective`, `hex_cell_count`) and
  one `DIMS` row carrying the count in its label
  (`Honeycomb cell A/F (18 cells)`), `span_teeth`'s precedent.
- `check()`'s honeycomb rules, an if/elif chain each presupposing the one before
  it: no `hex_wall` (D-15), `hex_wall` under `MIN_WALL` (D-10), a `hex_cell` that
  rounds to 0 at 3 dp, and no whole cell fitting the web annulus (D-14, quoting
  its inner/outer radius) -- no hub/rim breach rule exists, because D-09's
  boundaries and D-07's whole-cell test keep every cell inside by construction
  (D-17). `derive()` warns when `hex_wall` is set with `hex_cell` 0 (D-15's
  reverse).
- `REQ-one-cutout-pattern`'s third selector: `hex_cell` joins `spoke_count` and
  `hole_count` in the one-pattern tuple -- all three set is one sentence naming
  all three, any two still name just those two.
- `derive()`'s measured cost (arm64, Python 3.12.13, 2026-09-29, the honeycomb
  spike's own host) recorded in `hex_cells`' docstring: 14.1 usec on
  `GearParams()` (beside 09-05's 11.5 usec baseline), 115 usec on the tracer
  link, 15.6 msec at the heaviest input (`teeth=200, module=10, hex_cell=3,
  hex_wall=0.4`) -- naming the three `hex_cells` calls one request makes
  (`check()`, `cutout_walls()`, `derive()` itself); no cache added.

## Task Commits

Each task was committed atomically:

1. **Task 1: One honeycomb link end to end** - `d6bfe0e` (feat)
2. **Task 2: Refuse the honeycombs that cannot exist and record derive()'s
   measured cost** - `baad230` (feat)

**Plan metadata:** `.planning/` bookkeeping is committed separately, per
`execute-plan.md`'s `git_commit_metadata` step.

## Files Created/Modified

- `src/spur/params.py` - `Honeycomb` group: `hex_cell`, `hex_wall` (Task 1).
- `src/spur/calc.py` - `HEX_CELL_CAP`, `whole_cells`/`cell_count_floor`/
  `cells_within` (moved), `hex_cells`, `_point_segment_distance`/`_hex_reach`,
  `cutout_walls`'s honeycomb branch, `DerivedDimensions.hex_cell_effective`/
  `hex_cell_count`, the raise-to-fit warning (Task 1); the one-pattern rule's
  third selector, `check()`'s four honeycomb rules, the ignored-`hex_wall`
  warning, `hex_cells`' cost docstring (Task 2).
- `src/spur/model.py` - `_cell_cutters`, `_cut_body`'s honeycomb branch (Task 1).
- `src/spur/static/app.js` - one `DIMS` row, `hex_cell_effective` (Task 1).
- `bench/honeycomb_spike.py` - the three lattice functions replaced with an
  import from `spur.calc` (Task 1).
- `tests/test_api.py` - the honeycomb link's schema/`/api/info`/export tests,
  the 29-field openapi contract, the `.hex_cell_count` read-form assertion
  (Task 1); the honeycomb 422 test (Task 2).
- `tests/test_model.py` - a new `test_builds_one_valid_solid` row, the tracer's
  built-solid proof (Task 1).
- `tests/test_calc.py` - the lattice/order/per-bore-count test, the raise-to-fit
  tests, the count-floor grid test (Task 1); the refusal/three-pattern/ignored/
  walls/ordering/bounds tests (Task 2).
- `tests/test_cli.py` - CLI/API parity for a honeycomb link, the wall-refusal
  exit-2 test (Task 2).

## Decisions Made

See `key-decisions` in the frontmatter for `HEX_CELL_CAP`'s source line, the
tracer's exact cell count and walls, the exact-vs-conservative wall measurement
(Flagged Assumption A3), the 200-tooth raise-to-fit, the measured `derive()`
costs, and the per-bore-shape counts/walls.

## Deviations from Plan

None - plan executed exactly as written. Every formula, boundary value, warning
sentence and cap given in the plan's `<interfaces>`/`<behavior>`/`<action>` blocks
was implemented and verified numerically before being written into a test; no
number differed from the planning probe's own measurements (18/24/12/30 cells per
bore shape, walls 1.525/2.149, 1.184/2.149, 2.709/2.149, 2.5/2.149, the 5.05/5.1
boundary, the 5.98/13.44 mm quoted annulus, the 25.25 mm/120-cell raise at 200
teeth) -- all reproduced exactly on this pinned kernel.

## Issues Encountered

- The plan's own `<verify>` `<automated>` command for Task 1 (`spur info --teeth
  200 --hex-cell 3 --hex-wall 1 | ... assert ... len(d['warnings']) == 1 ...`)
  fails as literally written: at 200 teeth with every other field at its default
  (module 1.75, `root_fillet` 0.5), the pre-existing root-fillet cap already
  warns ("Root fillet reduced to 0.39 mm to fit the tooth gap.") -- present with
  or without any honeycomb field, reproduced on a bare `GearParams(teeth=200)`.
  This is a plan-authoring gap (the verify script assumed a single warning at
  this input without checking for the pre-existing root-fillet interaction), not
  a code defect: nothing needed fixing, since root-fillet capping at 200 teeth
  predates this phase and is correct, unrelated behaviour. All the substantive
  claims that command makes -- `0 < n <= HEX_CELL_CAP`, `s > 3`, the size on the
  0.05 mm grid, and the honeycomb warning's exact text -- hold; only the literal
  `len(warnings) == 1` and `warnings[0].startswith(...)` fail because the
  honeycomb warning is `warnings[1]`, not `warnings[0]`. My own tests
  (`test_a_honeycomb_over_the_cap_is_raised_in_field_steps_to_the_first_size_that_fits`,
  `test_cli_and_api_print_the_same_honeycomb_document`) check the honeycomb
  warning by substring/`any()` rather than exact single-length tuple equality, so
  they are not fragile to this pre-existing interaction.

## User Setup Required

None - no external service configuration required.

## TDD Gate Compliance

Both tasks (`type="auto" tdd="true"`) landed RED+GREEN in one `feat(11-05)`
commit each -- `workflow.tdd_mode` is not enabled in `.planning/config.json`, so
the mechanical RED/GREEN/REFACTOR commit-pattern gate from `tdd.md` does not
apply to this project (11-03's and 11-04's precedent). RED discipline was still
followed in substance: every formula (`whole_cells`'s lattice, `cell_count_floor`'s
guaranteed bound, `_hex_reach`'s exact nearest/farthest reach, each `check()`
rule's boundary) was worked out and verified against the plan's own hand-computed
values with ad-hoc scripts against the real, unmodified kernel *before* the
corresponding pytest test was written -- so each test was written already known
to assert a true, kernel-verified fact. Before either commit, the full scope from
the plan's `<verify>` blocks (`tests/test_api.py tests/test_model.py
tests/test_calc.py tests/test_cli.py tests/regression`) was run against the
isolated per-task file set and again against the full final state: 311 passed
after Task 1, 418 passed after Task 2, 539 in the whole suite via `make verify`
-- all green, fixture byte-unchanged throughout.

## Next Phase Readiness

- 11-06 (honeycomb sweep) can build directly on `HEX_CELL_CAP`, the tracer's
  measured face/edge deltas, and this plan's raise-to-fit numbers.
- 11-07 through 11-09 (selector-matrix re-proof, built-solid proofs, cost) can
  build on the tracer and the per-bore-shape counts/walls measured here.
- No blockers.

---
*Phase: 11-body-cutouts*
*Completed: 2026-09-29*

## Self-Check: PASSED

- `[ -f src/spur/params.py ]` -> FOUND
- `[ -f src/spur/calc.py ]` -> FOUND
- `[ -f src/spur/model.py ]` -> FOUND
- `[ -f src/spur/static/app.js ]` -> FOUND
- `[ -f bench/honeycomb_spike.py ]` -> FOUND
- `[ -f tests/test_api.py ]` -> FOUND
- `[ -f tests/test_model.py ]` -> FOUND
- `[ -f tests/test_calc.py ]` -> FOUND
- `[ -f tests/test_cli.py ]` -> FOUND
- `git log --oneline --all | grep d6bfe0e` -> FOUND (Task 1 commit)
- `git log --oneline --all | grep baad230` -> FOUND (Task 2 commit)
- Plan-level `<verification>` re-run: `make lint typecheck lint-imports` clean;
  539 tests passed via `make verify`; `git diff --exit-code
  tests/regression/pre_v0_2.json` clean; the tracer builds 18 cells with exact
  walls through the API, CLI and form; `HEX_CELL_CAP` equals the spike's recorded
  cap and the spike imports the shipped lattice; the 200-tooth request raises to
  120 cells at 25.25 mm; every honeycomb refusal and the three-selector rule
  pinned; `derive()`'s cost recorded in `hex_cells`' docstring.
</content>
