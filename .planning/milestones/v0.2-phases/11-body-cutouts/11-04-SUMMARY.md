---
phase: 11-body-cutouts
plan: 04
subsystem: calc
tags: [spokes, cutout, min-wall, one-pattern, analytic-fillet, tdd, cadquery]

# Dependency graph
requires:
  - phase: 11-03
    provides: "_cut_body(solid, p, pr)'s shared cut-call shape, cutout_walls, calc._under_min_wall, and the human's ruling (11-01-SUMMARY.md) that the spoke-arm wall rule ships"
provides:
  - "GearParams.spoke_count/spoke_width/hub_d/rim_wall/spoke_fillet (Spokes group, every default 0, L05), declared after Recess and before Holes (D-19)"
  - "model._spoke_sector/_spoke_cutters: N sector prisms with analytic tangent-arc corners baked into the 2D wire, never OCCT's 3D fillet operator (D-05); model._fillet_corner gains inside= for the rim-side mirror"
  - "calc.spoke_opening/spoke_fillet_limit/spoke_fillet_effective (D-06); cutout_walls' spoke branch; DerivedDimensions.spoke_fillet_effective"
  - "REQ-one-cutout-pattern's refusal in check() (spoke_count and hole_count both set); calc._listed; five independent spoke wall rules (arm, rim, hub, annulus, opening) plus the half-set and ignored-dimensions warnings"
affects: [11-05, 11-06, 11-07, 11-08, 11-09]

# Actuals (#2632)
actuals:
  tokens: 11785
  tasks: 2
  commits: 2
  plan_head_before: 0ee0512265e2f323882e3d1c1ed9acdef3266967
  plan_head_after: 69019484f2e15ffea35d589abfe6bf9342d980cb

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "model._fillet_corner(..., inside=False): the default path (outside the circle,
      the tooth root fillet's case) is float-for-float unchanged; inside=True mirrors it
      for a corner whose region lies inside the circle (rc = rf - rho, the near root of
      the quadratic) -- 11-05's honeycomb corners can reuse whichever side they need."
    - "calc._listed(items): the '\"a\", \"a and b\", \"a, b and c\"' join for every
      cutout sentence naming more than one field -- 11-05 reuses it for the honeycomb's
      own half-set and one-pattern sentences."

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
    - tests/test_cli.py

key-decisions:
  - "The arm rule (11-01-SUMMARY.md Flagged Assumption A1, human approved): 0 <
    spoke_width < MIN_WALL is refused with a 422 naming spoke_width, exactly like every
    other wall in the part. Shipped in Task 2, first in the rule order (arm, rim, hub,
    annulus, opening)."
  - "The hub-ring opening between adjacent bar feet is measured as an arc,
    hub_d/2 * (2*pi/N - 2*asin(spoke_width/hub_d)), following keyway_flat_wall's arc
    precedent (research Pitfall 4, Assumption A2) -- not a chord. Confirmed against the
    planning probe's own numbers (opening 7.415401 mm on the tracer, N=12/hub_d=12
    boundary at spoke_width ~2.717804 mm) to the last measured digit."
  - "_fillet_corner's rim-side mirror (inside=True, D-05) was hand-checked before
    trusting it at every sector corner: R 10, line y = 1 inward, rho 1 gives the circle
    tangent point (9.749960, 2.222222) and the line tangent point (8.774964, 1.0) --
    matches the planning probe's own hand-computed case to 1e-6 mm, and the built
    tracer solid's face/edge deltas (+14 PLANE, +40 CYLINDER, +16 TORUS, +240 edges)
    match the probe's counts exactly."
  - "RED and GREEN for both tasks landed in one feat commit each, not separate
    test(...)/feat(...) commits -- workflow.tdd_mode is not enabled in config.json, so
    the mechanical RED/GREEN/REFACTOR commit-pattern gate does not apply (11-03's
    precedent, itself citing 08-03). See TDD Gate Compliance below for how RED was
    established without a separate commit."
  - "The one-pattern rule (REQ-one-cutout-pattern) sits before both per-pattern
    branches in check()'s cutout block, as an elif chain: with two or more of
    spoke_count/hole_count set, neither pattern's own rules run at all -- a half-set
    hole pattern set beside a complete spoke pattern still produces only the
    one-pattern sentence, never the half-set-hole sentence too (verified by test)."

patterns-established:
  - "Pattern 2's mirrored analytic tangent-arc fillet (research 11-RESEARCH.md): a
    straight bar side against an axis-centred circle, filleted in the 2D sketch on
    either the outside (hub, root-fillet-precedent) or the inside (rim, new) of the
    circle -- both through one function, one boolean flag."

requirements-completed: [REQ-spoke-cutout, REQ-one-cutout-pattern,
  REQ-cutout-conflicts-refused-early, REQ-cutout-derived-numbers]

# Coverage metadata (#1602)
coverage:
  - id: D1
    description: "The spoke tracer link (?spoke_count=4&spoke_width=2&hub_d=12&rim_wall=1&spoke_fillet=1)
      cuts four filleted sectors through the default gear in one cut call, through the
      API, CLI and form schema, with arm 0 centred on +X"
    requirement: "REQ-spoke-cutout"
    verification:
      - kind: integration
        ref: "tests/test_model.py#test_the_spoke_link_cuts_four_filleted_sectors"
        status: pass
      - kind: e2e
        ref: "tests/test_api.py#test_a_spoke_link_is_served_with_the_fillet_it_cut"
        status: pass
      - kind: e2e
        ref: "tests/test_cli.py#test_cli_and_api_print_the_same_spoke_document"
        status: pass
    human_judgment: false
  - id: D2
    description: "spoke_fillet_effective caps to the smaller of the hub opening and
      the annulus width, warns with the binding reason, and reports the sub-0.001 mm
      resolution case; model.py cuts exactly the value derive() prints"
    requirement: "REQ-cutout-derived-numbers"
    verification:
      - kind: unit
        ref: "tests/test_calc.py#test_a_spoke_fillet_is_capped_to_whichever_limit_binds_first"
        status: pass
      - kind: unit
        ref: "tests/test_calc.py#test_a_sub_print_precision_spoke_fillet_request_still_warns"
        status: pass
    human_judgment: false
  - id: D3
    description: "The rim-side mirrored _fillet_corner is tangent to both the rim
      circle and the bar side, matching a hand-computed sanity case"
    requirement: "REQ-spoke-cutout"
    verification:
      - kind: unit
        ref: "tests/test_model.py#test_a_rim_corner_fillet_is_tangent_to_the_rim_circle_and_the_bar_side"
        status: pass
    human_judgment: false
  - id: D4
    description: "Two or more body-cutout patterns set on one part (spoke_count and
      hole_count) is refused with one 422 naming every chosen selector, before any
      per-pattern rule runs"
    requirement: "REQ-one-cutout-pattern"
    verification:
      - kind: unit
        ref: "tests/test_calc.py#test_two_cutout_patterns_on_one_part_are_refused_naming_both"
        status: pass
      - kind: e2e
        ref: "tests/test_api.py#test_two_cutout_patterns_are_422_naming_both"
        status: pass
    human_judgment: false
  - id: D5
    description: "Every spoke wall rule (arm, rim, hub, annulus, opening) refuses one
      step past MIN_WALL and accepts it exactly, in check()'s fixed order, naming its
      own fields; a keyway's floor corner is read as the hub datum"
    requirement: "REQ-cutout-conflicts-refused-early"
    verification:
      - kind: unit
        ref: "tests/test_calc.py#test_a_spoke_rule_refuses_one_step_past_its_wall_and_accepts_it_exactly"
        status: pass
      - kind: unit
        ref: "tests/test_calc.py#test_a_spoke_hub_inside_a_keyway_corner_is_refused"
        status: pass
      - kind: unit
        ref: "tests/test_calc.py#test_multiple_refusals_come_in_check_order_and_name_each_field_once"
        status: pass
      - kind: e2e
        ref: "tests/test_cli.py#test_a_rim_wall_under_min_wall_exits_2_and_names_it"
        status: pass
    human_judgment: false
  - id: D6
    description: "A half-set spoke pattern is a 422 naming only its zero fields;
      spoke dimensions set with spoke_count 0 build nothing and warn naming only the
      fields set"
    requirement: "REQ-cutout-conflicts-refused-early"
    verification:
      - kind: unit
        ref: "tests/test_calc.py#test_a_half_set_spoke_pattern_names_only_its_zero_fields"
        status: pass
      - kind: unit
        ref: "tests/test_calc.py#test_spoke_dimensions_without_a_count_are_ignored_and_named"
        status: pass
    human_judgment: false
  - id: D7
    description: "spoke_count is an integer field 0-200, field-level errors outside
      the range; the pre-v0.2 fixture stays byte-unchanged"
    requirement: "REQ-spoke-cutout"
    verification:
      - kind: unit
        ref: "tests/test_calc.py#test_the_spoke_count_is_an_integer_from_0_to_200"
        status: pass
      - kind: other
        ref: "git diff --exit-code tests/regression/pre_v0_2.json"
        status: pass
    human_judgment: false

# Metrics
duration: ~37min
completed: 2026-09-29
status: complete
---

# Phase 11 Plan 04: Spoke Cutout Pattern Summary

**A spoke pattern that cuts N filleted sectors between a hub ring and a rim wall in one boolean cut, with analytic tangent-arc corners baked into the 2D cutter wire, the fillet cap reported as `spoke_fillet_effective`, and a body-wide REQ-one-cutout-pattern refusal now that a second cutout pattern exists.**

## Performance

- **Duration:** ~37 min (reconstructed from STATE.md's prior session timestamp,
  06:28:18Z, to this session's completion, 07:05:52Z -- `record_start_time` was not
  captured as a separate marker at dispatch)
- **Completed:** 2026-09-29T07:05:52Z
- **Tasks:** 2 (both `type="auto" tdd="true"`)
- **Files modified:** 8 (`src/spur/params.py`, `src/spur/calc.py`, `src/spur/model.py`,
  `src/spur/static/app.js`, `tests/test_api.py`, `tests/test_model.py`,
  `tests/test_calc.py`, `tests/test_cli.py`)

## Accomplishments

- Five new `GearParams` fields (`spoke_count`, `spoke_width`, `hub_d`, `rim_wall`,
  `spoke_fillet`) in a `Spokes` schema group, declared after `Recess` and before
  `Holes`, every default 0 (D-19) -- the API, CLI and web form gained the pattern from
  one model change.
- `model._spoke_sector`/`_spoke_cutters`: N sector prisms between the hub ring and the
  rim wall, each corner rounded by an analytic tangent arc baked into the cutter's own
  2D wire (D-05) -- never OCCT's 3D fillet operator on the 4N vertical corner edges.
  `_cut_body` picks the spoke branch over the hole branch (only one ever runs, per
  REQ-one-cutout-pattern).
- `model._fillet_corner` gains `inside=` (D-05's mirror): the default path is
  float-for-float identical to before this parameter existed (the pre-v0.2 fixture
  replays byte-unchanged); `inside=True` puts the arc centre inside the circle for the
  sector's rim corners, hand-checked against a 3-4-5-style tangent case before trusting
  it broadly.
- `calc.spoke_opening` (the arc between adjacent bar feet on the hub circle,
  `keyway_flat_wall`'s arc-measure precedent), `calc.spoke_fillet_limit` and
  `calc.spoke_fillet_effective` (`root_fillet`'s 0.45-of-the-shared-dimension
  cap-and-warn family) -- the tracer's fillet caps to 3.337 mm "to fit the opening
  between the arms at the hub" exactly as the planning probe measured.
  `DerivedDimensions.spoke_fillet_effective`, null with no spokes or `spoke_fillet` 0.
- `REQ-one-cutout-pattern`'s refusal in `check()`: `spoke_count` and `hole_count` both
  set is one 422 naming every chosen selector, before any per-pattern rule runs.
- Five independent spoke wall refusals in `check()`'s fixed order -- arm (11-01's human
  ruling, kept), rim, hub (reads the keyway floor corner where one exists), annulus,
  and opening (only where the annulus exists) -- each pinned one step past `MIN_WALL`
  and accepted exactly via `_under_min_wall`, plus the half-set (D-15) and
  ignored-dimensions warnings.
- The tracer link's built-solid proof: `+14 PLANE`, `+40 CYLINDER`, `+16 TORUS` faces,
  `+240` edges against the plain default gear -- matching the planning probe's counts
  exactly; arm 0 at `(10, 0, 3.75)` is inside the solid, the 45° gap point is not.

## Task Commits

Each task was committed atomically:

1. **Task 1: One spoke link end to end** - `1650bdf` (feat)
2. **Task 2: Refuse two patterns and every spoke wall breach** - `6901948` (feat)

**Plan metadata:** commit for `.planning/` bookkeeping is separate, per
`execute-plan.md`'s `git_commit_metadata` step.

_Note: both tasks folded RED+GREEN into one commit each -- see Decisions Made and TDD
Gate Compliance below._

## Files Created/Modified

- `src/spur/params.py` - `Spokes` group: `spoke_count`, `spoke_width`, `hub_d`,
  `rim_wall`, `spoke_fillet` (Task 1).
- `src/spur/calc.py` - `spoke_opening`, `spoke_fillet_limit`, `spoke_fillet_effective`,
  `cutout_walls`' spoke branch, `DerivedDimensions.spoke_fillet_effective`, the fillet
  cap warning (Task 1); `_listed`, the one-pattern rule, five spoke wall rules, the
  ignored-dimensions warning (Task 2).
- `src/spur/model.py` - `_fillet_corner(..., inside=)`, `_spoke_sector`,
  `_spoke_cutters`, `_cut_body`'s spoke branch (Task 1).
- `src/spur/static/app.js` - one `DIMS` row, `spoke_fillet_effective` (Task 1).
- `tests/test_api.py` - the spoke link's schema/`/api/info`/export tests, the
  27-field openapi contract, the hole-order assertion (Task 1); the two-pattern 422
  test (Task 2).
- `tests/test_model.py` - three new `test_builds_one_valid_solid` rows, the tracer's
  built-solid proof, the hand-computed rim-corner tangency test (Task 1).
- `tests/test_calc.py` - the one-pattern, half-set, boundary, keyway-hub, fillet-cap,
  sub-resolution, ignored-dimensions, count-bound and ordering tests (Task 2).
- `tests/test_cli.py` - CLI/API parity for a spoke link, the rim-wall exit-2 test
  (Task 2).

## Decisions Made

See `key-decisions` in the frontmatter for the arm rule, the hub-opening arc measure,
the rim-fillet hand-check, the RED/GREEN commit shape, and the one-pattern ordering.

## Deviations from Plan

None - plan executed exactly as written. Every formula, boundary value, warning
sentence and cap given in the plan's `<interfaces>`/`<behavior>`/`<action>` blocks was
implemented and verified numerically before being written into a test; no number
differed from the planning probe's own measurements (opening 7.415401 mm, annulus
7.4375 mm, cap 3.337 mm, the +14/+40/+16/+240 face/edge deltas, the keyway boundary at
13.16 mm) -- all reproduced exactly on this pinned kernel.

## Issues Encountered

None.

## TDD Gate Compliance

Both tasks (`type="auto" tdd="true"`) implemented the geometry/rules and their tests
together, landing RED+GREEN in one `feat(11-04)` commit each -- `workflow.tdd_mode` is
not enabled in `.planning/config.json`, so the mechanical RED/GREEN/REFACTOR
commit-pattern gate from `tdd.md` does not apply to this project (11-03's precedent,
itself citing 08-03). RED discipline was still followed in substance rather than by a
separate commit: every formula (`spoke_opening`, `spoke_fillet_limit`, `_fillet_corner`
with `inside=True`, each check() rule's boundary) was worked out and verified against
the plan's own hand-computed values with ad-hoc scripts against the real, unmodified
kernel *before* the corresponding pytest test was written -- so each test was written
already known to assert a true, kernel-verified fact, and the formal test-suite run
that followed was a confirming GREEN, not a blind one. Before either commit, the full
scope from the plan's `<verify>` blocks (`tests/test_api.py tests/test_model.py
tests/test_calc.py tests/test_cli.py tests/regression`) was run against the isolated
per-task file set (Task 1's six files with Task 2's calc.py/test_calc.py/test_cli.py
additions temporarily reverted to HEAD, confirming Task 1 alone: 367 passed) and again
against the full final state (394 passed in the four-file scope, 515 in the whole
suite via `make verify`) -- both runs green, fixture byte-unchanged both times.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- 11-05 (honeycomb) can reuse `calc._listed` for its own half-set/one-pattern
  sentences, the mirrored `model._fillet_corner(inside=)` if its cells need a rounded
  edge, and must append `("hex_cell", p.hex_cell)` to the one-pattern rule's `chosen`
  tuple (already commented at the call site).
- 11-06 through 11-09 (sweep, selector-matrix re-proof, built-solid fillet-survival
  proof, cost) can build on the spoke tracer and its measured face/edge deltas
  directly.
- No blockers.

---
*Phase: 11-body-cutouts*
*Completed: 2026-09-29*

## Self-Check: PASSED

- `[ -f src/spur/params.py ]` -> FOUND
- `[ -f src/spur/calc.py ]` -> FOUND
- `[ -f src/spur/model.py ]` -> FOUND
- `[ -f src/spur/static/app.js ]` -> FOUND
- `[ -f tests/test_api.py ]` -> FOUND
- `[ -f tests/test_model.py ]` -> FOUND
- `[ -f tests/test_calc.py ]` -> FOUND
- `[ -f tests/test_cli.py ]` -> FOUND
- `git log --oneline --all | grep 1650bdf` -> FOUND (Task 1 commit)
- `git log --oneline --all | grep 6901948` -> FOUND (Task 2 commit)
- Plan-level `<verification>` re-run: `make lint typecheck lint-imports` clean; 394
  tests passed across `tests/test_calc.py tests/test_cli.py tests/test_api.py
  tests/test_model.py tests/regression`; `git diff --exit-code
  tests/regression/pre_v0_2.json` clean; full `make verify` (515 tests) passed
- All Task 1 and Task 2 acceptance-criteria greps and both `<automated>` CLI commands
  re-ran clean (spoke tracer's cap/walls/warnings match exactly; the two-pattern link
  exits 2; `group="Spokes"` x5, `.cut(` x5, `.fillet(` x1, `inside=True` x3,
  `Only one body cutout pattern per part` x1, `_listed` x1, the opening-refusal
  sentence x1, and the 10-row boundary parametrize all confirmed)
