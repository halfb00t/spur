---
phase: 11-body-cutouts
plan: 03
subsystem: calc
tags: [holes, lightening-holes, min-wall, cutout, tdd, cadquery]

# Dependency graph
requires:
  - phase: 11-02
    provides: "the measured cut spelling (star, cut(*cutters)) and HEX_CELL_CAP context this
      phase's cutters share"
provides:
  - "GearParams.hole_count/hole_d/hole_circle_d (Holes group, every default 0, L05)"
  - "model._hole_cutters/_cut_body: N cylinders through the full face width, hole 0 on +X
    (D-03), subtracted in one solid.cut(*cutters) call between _cut_keyway and _chamfer_tips"
  - "calc.cutout_walls(p, rf), calc._under_min_wall(wall), calc.hole_gap(p): the hub/rim/
    neighbour MIN_WALL rules 11-04 and 11-05 reuse for spokes and honeycomb"
  - "DerivedDimensions.cutout_hub_wall/cutout_rim_wall, null with no cutout"
  - "check()'s half-set, hub, rim and neighbour hole refusals; derive()'s ignored-dimensions
    warning"
affects: [11-04, 11-05, 11-06, 11-07, 11-08, 11-09]

# Actuals (#2632)
actuals:
  tokens: 7710
  tasks: 2
  commits: 2
  plan_head_before: 2c02c6e19216f49147860e2ac49113bc022dc71f
  plan_head_after: 5d8ae53487ca22eee4cfffd17b977ecd7beb42c3

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "_under_min_wall(wall): round(wall, 6) < MIN_WALL -- every cutout MIN_WALL rule from
      here on goes through it, so a wall sized to exactly MIN_WALL is accepted despite
      step-aligned float residue (measured: 0.39999999999999947 at the tracer's hub
      boundary). 11-04/11-05's spoke and honeycomb wall rules reuse it verbatim."

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
  - "Cut spelling measured in 11-02 (star, cut(*cutters)) applied unchanged: 11-03's
    _cut_body is the first cutter to use it against a real (non-honeycomb) pattern."
  - "RED and GREEN for Task 2 landed in one feat commit, not separate test(.../feat(...)
    commits -- CLAUDE.md's 'one concern per commit, not micro-commits' plus the Phase 8
    precedent (08-03-SUMMARY.md): workflow.tdd_mode is not enabled in config.json, so the
    mechanical RED/GREEN/REFACTOR commit-pattern gate does not apply; RED was still run and
    confirmed failing before GREEN was written (see TDD Gate Compliance)."
  - "The hub, rim and neighbour hole rules are independent (three ifs, not elif/chain): a
    hole wider than the web breaches both walls at once and must say so twice
    (REQ-cutout-conflicts-refused-early) -- proven by
    test_a_hole_wider_than_the_web_is_refused_at_both_walls."

patterns-established:
  - "_under_min_wall(wall) -- description above; the single comparison point for every
    cutout wall rule in this phase (11-04, 11-05, 11-07)."

requirements-completed: [REQ-hole-cutout, REQ-cutout-conflicts-refused-early,
  REQ-cutout-derived-numbers, REQ-cutout-composes]

# Coverage metadata (#1602)
coverage:
  - id: D1
    description: "The tracer link (?hole_count=6&hole_d=4&hole_circle_d=20) cuts six holes
      through the default gear's recessed floor in one cut call, through the API, CLI and
      form schema, printing the two thinnest walls (3.025/2.438 mm)"
    requirement: "REQ-hole-cutout"
    verification:
      - kind: integration
        ref: "tests/test_model.py#test_the_hole_link_cuts_six_holes_through_the_recessed_floor"
        status: pass
      - kind: e2e
        ref: "tests/test_api.py#test_a_hole_link_is_served_with_its_walls"
        status: pass
      - kind: e2e
        ref: "tests/test_cli.py#test_cli_and_api_print_the_same_hole_document"
        status: pass
    human_judgment: false
  - id: D2
    description: "Every hole rule refuses one step past its wall and accepts it exactly,
      comparing round(wall, 6): hub, rim and neighbour, each independent"
    requirement: "REQ-cutout-conflicts-refused-early"
    verification:
      - kind: unit
        ref: "tests/test_calc.py#test_a_hole_rule_refuses_one_step_past_its_wall_and_accepts_it_exactly"
        status: pass
      - kind: unit
        ref: "tests/test_calc.py#test_a_hole_wider_than_the_web_is_refused_at_both_walls"
        status: pass
      - kind: integration
        ref: "tests/test_api.py#test_a_hole_conflict_is_422_naming_its_fields"
        status: pass
      - kind: integration
        ref: "tests/test_cli.py#test_a_hole_too_close_to_the_bore_exits_2_and_names_it"
        status: pass
    human_judgment: false
  - id: D3
    description: "A half-set hole pattern (hole_count > 0, one or both dimensions still 0)
      is a 422 naming only its zero fields; hole_d/hole_circle_d set with hole_count 0
      warns naming only the fields set, without building anything"
    requirement: "REQ-cutout-conflicts-refused-early"
    verification:
      - kind: unit
        ref: "tests/test_calc.py#test_a_half_set_hole_pattern_names_only_its_zero_fields"
        status: pass
      - kind: unit
        ref: "tests/test_calc.py#test_hole_dimensions_without_a_count_are_ignored_and_named"
        status: pass
    human_judgment: false
  - id: D4
    description: "cutout_hub_wall/cutout_rim_wall report the correct thinnest walls per
      bore shape (round/D-flat, hex, keyed round, no bore) and are null with no cutout;
      the pre-v0.2 fixture stays byte-unchanged"
    requirement: "REQ-cutout-derived-numbers"
    verification:
      - kind: unit
        ref: "tests/test_calc.py#test_a_cutout_reports_its_thinnest_walls_and_null_without_one"
        status: pass
      - kind: other
        ref: "git diff --exit-code tests/regression/pre_v0_2.json"
        status: pass
    human_judgment: false
  - id: D5
    description: "Holes compose with a face recess: the tracer's model test proves the
      holes cut through the recessed floor (a 3.5 mm web between the recesses), not just
      through the solid blank"
    requirement: "REQ-cutout-composes"
    verification:
      - kind: integration
        ref: "tests/test_model.py#test_the_hole_link_cuts_six_holes_through_the_recessed_floor"
        status: pass
    human_judgment: false

# Metrics
duration: ~55min (Task 1 committed in a prior session terminated by a network error before
  Task 2 started; this session investigated the inherited state, wrote Task 2's RED tests,
  implemented GREEN, and closed out the plan)
completed: 2026-09-29
status: complete
---

# Phase 11 Plan 03: Lightening Holes Summary

**Six round holes on a bolt circle, cut through the recessed floor in one `solid.cut(*cutters)` call and reported with the two thinnest walls (3.025/2.438 mm on the tracer link); every hole that breaches the hub, the rim or its neighbour is a 422/exit-2 before any CAD work, at a measured MIN_WALL boundary that survives float residue.**

## Performance

- **Duration:** ~55 min total across two sessions (Task 1's tracer, commit `8405e18`, ran to
  completion and passed its tracer feedback gate in a prior session that then ended on a
  network error before Task 2 started; this session verified that inherited state, then
  wrote and closed out Task 2)
- **Completed:** 2026-09-29
- **Tasks:** 2 (1 tracer, 1 auto/tdd)
- **Files modified:** 8 (`src/spur/params.py`, `src/spur/calc.py`, `src/spur/model.py`,
  `src/spur/static/app.js`, `tests/test_api.py`, `tests/test_model.py`, `tests/test_calc.py`,
  `tests/test_cli.py`)

## Accomplishments

- Three new `GearParams` fields (`hole_count`, `hole_d`, `hole_circle_d`) in a `Holes`
  schema group, every default 0 (L05) — the API, CLI and web form gained the pattern from
  one model change, no `app.py`/`cli.py` edits.
- `model._cut_body`/`_hole_cutters`: N cylinders through the full face width, hole 0 centred
  on +X (D-03), subtracted in exactly one `solid.cut(*cutters)` call (the `star` spelling
  11-02 measured) between `_cut_keyway` and `_chamfer_tips` — the recess floor fillet and
  the bore-rim chamfer are already baked geometry, so their selectors never see a cutout
  edge.
- `calc.cutout_walls(p, rf)`, two new `DerivedDimensions` fields (`cutout_hub_wall`,
  `cutout_rim_wall`), measured from `bore_mouth_limit(p)` and the root circle — 3.025/2.438
  on the tracer link, null with no cutout.
- `calc._under_min_wall(wall)` and `calc.hole_gap(p)`: the shared MIN_WALL comparison
  (`round(wall, 6) < MIN_WALL`) and the neighbour-gap formula every later cutout rule in
  this phase reuses.
- Four independent hole refusals in `check()` — half-set (D-15), hub (D-17), rim (D-17),
  neighbour (D-16) — each naming only its own fields, none implying another; a hole wider
  than the web trips both wall sentences at once.
- One `derive()` warning: `hole_d`/`hole_circle_d` set with `hole_count` 0 builds nothing
  and says so, naming only the fields actually set.
- The tracer link's built-solid proof: +6 CYLINDER faces, +18 edges, -263.893783 mm³ (the
  3.5 mm web between the recesses — REQ-cutout-composes), 4 TORUS faces untouched on both
  solids.

## Task Commits

Each task was committed atomically:

1. **Task 1: One lightening-hole link end to end (tracer)** — `8405e18` (feat) — completed
   and its tracer feedback gate resolved in a prior session (see Continuation notes below);
   verified again on HEAD at the start of this session (337 tests, fixture byte-unchanged,
   all five acceptance-criteria greps and both CLI/STEP `<verify>` commands re-ran clean)
   before Task 2 began.
2. **Task 2: Refuse every hole that breaches a wall before any CAD work** — `5d8ae53`
   (feat) — RED and GREEN in one commit per the Decisions Made note below; RED confirmed
   failing first (see TDD Gate Compliance).

**Plan metadata:** this SUMMARY and the STATE.md/ROADMAP.md/REQUIREMENTS.md bookkeeping are
committed separately per `execute-plan.md`'s `git_commit_metadata` step.

## Files Created/Modified

- `src/spur/params.py` — `Holes` group: `hole_count`, `hole_d`, `hole_circle_d` (Task 1).
- `src/spur/calc.py` — `cutout_walls`, `_under_min_wall`, `hole_gap`, the two derived
  fields, the four `check()` rules, the `derive()` warning (Tasks 1 and 2).
- `src/spur/model.py` — `_hole_cutters`, `_cut_body`; `_build` gains one line (Task 1).
- `src/spur/static/app.js` — two `DIMS` rows, `cutout_hub_wall`/`cutout_rim_wall` (Task 1).
- `tests/test_api.py` — the hole link's schema/`/api/info`/export tests, the 26-field
  contract, the hole 422 test (Tasks 1 and 2).
- `tests/test_model.py` — the tracer link's built-solid proof (Task 1).
- `tests/test_calc.py` — the boundary matrix, half-set, wider-than-the-web, ignored-warning,
  per-bore-shape wall, and hole-count-bound tests (Task 2).
- `tests/test_cli.py` — CLI/API parity and the exit-2 hub refusal (Task 2).

## Decisions Made

- **Cut spelling:** `star` (`solid.cut(*cutters)`), carried unchanged from 11-02's measured
  spike — `_cut_body` is the first real cutter (not a spike script) to use it.
- **RED/GREEN commit shape for Task 2:** landed as one `feat(11-03)` commit rather than
  separate `test(...)`/`feat(...)` commits. `.planning/config.json` does not set
  `workflow.tdd_mode`, so the mechanical RED/GREEN/REFACTOR *commit-pattern* gate from
  `tdd.md` does not apply to this project; CLAUDE.md's "one concern per commit, not
  micro-commits" and the plan's own `<action>` text ("Commit the four files by name:
  feat(11-03): ...") both call for a single commit. This mirrors 08-03's precedent exactly
  (`08-03-SUMMARY.md`'s "TDD Gate Compliance" section). The RED discipline itself — write
  tests, run them, confirm they fail for the right reason, only then implement — was
  followed in full; see below.
- **Independent hole rules, not elif:** the hub, rim and neighbour checks each run
  unconditionally (once past the half-set gate) because none implies another — confirmed
  by `test_a_hole_wider_than_the_web_is_refused_at_both_walls`, where a 10 mm hole on a
  19 mm circle breaches both the hub and the rim and the 422 carries both sentences.

## Deviations from Plan

None — plan executed exactly as written for both tasks. No Rule 1-4 auto-fixes were
needed; the implementation matched the plan's `<action>` text and `<behavior>` block
exactly, including every message wording and rounding rule.

## Issues Encountered

- **Network interruption between tasks.** The prior executor session ended on an `ENOTFOUND`
  network error after Task 1's commit and tracer-gate pass, before Task 2 started. This
  session (a fresh executor) verified the inherited state per the orchestrator's
  reconciliation before resuming: re-ran Task 1's `<verify>` block in full (337 tests,
  fixture diff clean, all acceptance-criteria greps, the CLI and STEP export commands) and
  confirmed `8405e18` intact on `HEAD` before writing a single line for Task 2. No repair
  was needed — Task 1 held exactly as committed.

## TDD Gate Compliance

Task 2 (`type="auto" tdd="true"`) followed the RED → GREEN cycle:

- **RED:** `tests/test_calc.py`, `tests/test_cli.py` and `tests/test_api.py` were extended
  first and run against the pre-implementation `calc.py`. `tests/test_calc.py` failed to
  *collect* (`ImportError: cannot import name 'hole_gap' from 'spur.calc'`) — the direct,
  expected symptom of the not-yet-written function the plan's own `<action>` text names,
  not an unrelated defect. `tests/test_cli.py::test_a_hole_too_close_to_the_bore_exits_2_and_names_it`
  and `tests/test_api.py::test_a_hole_conflict_is_422_naming_its_fields` both ran and failed
  on their assertion (`DID NOT RAISE SystemExit`; `assert 200 == 422`) — a genuine RED,
  since no refusal rule existed yet to reject the link. `tests/test_cli.py::test_cli_and_api_print_the_same_hole_document`
  passed immediately in RED because it only asserts CLI/API parity, which held even before
  the refusal rules existed.
- **GREEN:** `calc._under_min_wall`, `calc.hole_gap`, the four `check()` rules and the
  `derive()` warning were implemented; all hole-scoped tests (22) and the full
  `tests/test_calc.py tests/test_cli.py tests/test_api.py tests/test_model.py
  tests/regression` scope (361 tests) passed. `make verify` (482 tests, ruff, mypy
  `--strict`, `lint-imports`, `no-fake-done`) passed clean.
- **Commit shape:** RED and GREEN landed in a single commit (`5d8ae53`), per the plan's
  explicit `<action>` instruction and CLAUDE.md's "one concern per commit" — see Decisions
  Made above. `workflow.tdd_mode` is not enabled in `.planning/config.json`, so the
  mechanical RED/GREEN/REFACTOR commit-pattern gate does not apply to this plan.
- **No REFACTOR commit** — the implementation needed no follow-up cleanup after GREEN.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- 11-04 (spokes) and 11-05 (honeycomb field + functions) can build on `cutout_walls`,
  `_under_min_wall` and the `_cut_body`/`_hole_cutters` shape directly — the pattern this
  plan established (one `_build` step, one cut call, independent MIN_WALL rules, an
  ignored-fields warning when the count is 0) is meant to be the template both reuse.
- `bench/honeycomb_spike.py`'s spelling and cap (11-02) are already in use here unchanged.
- No blockers.

---
*Phase: 11-body-cutouts*
*Completed: 2026-09-29*

## Self-Check: PASSED

- `[ -f src/spur/calc.py ]` → FOUND
- `[ -f tests/test_calc.py ]` → FOUND
- `[ -f tests/test_cli.py ]` → FOUND
- `[ -f tests/test_api.py ]` → FOUND
- `git log --oneline --all | grep 8405e18` → FOUND (Task 1 commit)
- `git log --oneline --all | grep 5d8ae53` → FOUND (Task 2 commit)
- Plan-level `<verification>` re-run: `make lint typecheck lint-imports` clean; 361 tests
  passed across `tests/test_calc.py tests/test_cli.py tests/test_api.py tests/test_model.py
  tests/regression`; `git diff --exit-code tests/regression/pre_v0_2.json` clean; full
  `make verify` (482 tests) passed
- All five Task 1 acceptance-criteria greps and both Task 2 acceptance-criteria commands
  re-ran clean (see Task Commits and the `_under_min_wall`/sentence/exit-2/warning checks
  above)
