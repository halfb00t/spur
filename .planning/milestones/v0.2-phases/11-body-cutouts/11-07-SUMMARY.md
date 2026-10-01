---
phase: 11-body-cutouts
plan: 07
subsystem: cad-kernel-proofs
tags: [cadquery, edge-selection, min-wall, tangency, kernel-boundary, cutout]

# Dependency graph
requires:
  - phase: 11-03, 11-04, 11-05
    provides: "the three cutout patterns (holes, spokes, honeycomb), each with its own
      MIN_WALL rules in calc.check() and _cut_body's shared cut(*cutters) shape"
  - phase: 11-06
    provides: "the measured hole_count/spoke_count le (60/40) the boundary rows in this
      plan build at"
provides:
  - "REQ-edge-selection-proven extended to every cutout pattern, bore shape and recess
    setting on the real pipeline (not the bare-solid matrix): the bore-rim and
    groove-floor selectors run before _cut_body and never see a cutout edge; the tip
    selector runs after it and takes exactly 2 x teeth arcs"
  - "REQ-cutout-composes' selector and tangency half: a cutout composes with the tip
    chamfer (measured face counts) and every tangent cutter builds without a fuzzy
    boolean"
  - "D-16/D-17 measured one field-step either side of every cutout wall rule, on the
    pinned kernel, as tests"
  - "D-06's spoke_fillet cap measured buildable on the most awkward sectors the rules
    allow"
  - "_groove_floor_edges' docstring corrected: the cutouts never needed to re-prove the
    separating invariant, they run strictly after the selector by construction"
affects: [11-08, 11-09]

# Actuals (#2632)
actuals:
  tokens: 4643
  tasks: 2
  commits: 2
  plan_head_before: 7980b4d6cb14998c3d483a023194cdc7199ea7cd
  plan_head_after: eca02a9f4bbe5284f1f664c131a537eb4b8a9e07

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "A real-pipeline selector spy (monkeypatch the model-module function, call
      _build_checked, assert call count and returned Counter) proves an invariant on
      the actual build order rather than a hand-assembled bare solid -- 10-03's shape,
      now applied to two selectors at once across every cutout row."
    - "A kernel-boundary pair (accept-exactly / one-step-past via model_copy) reuses the
      exact numeric boundary test_calc.py's own refusal tests already pin, rather than
      re-deriving them -- so the two suites can never silently drift apart on the same
      rule."

key-files:
  created: []
  modified:
    - src/spur/model.py
    - tests/test_model.py

key-decisions:
  - "The real-pipeline spy reads the same rim/floor Counter values the no-cutout matrix
    (test_each_edge_selector_picks_exactly_its_own_edges) already established, because
    _bore_rim_edges and _groove_floor_edges are both called on the solid before their
    own operator (chamfer/fillet) runs, inside _cut_bore/_cut_face_recesses --
    independent of whether a cutout exists later in the pipeline. Verified by running
    the real spy against all 19 rows before writing the test: every row matched the
    no-cutout matrix's counts exactly (2026-09-29)."
  - "Every one-step-past row in test_the_kernel_cuts_one_valid_solid_past_each_cutout_rule
    reuses test_calc.py's own refused-at-this-value boundary exactly (e.g. spoke opening
    past-the-rule is spoke_width 2.72, not the plan's provisional 2.77 in
    11-CONTEXT.md/the PLAN's <interfaces> block) -- the shipped test_calc.py values are
    the ground truth the kernel test must match, not the planning-time estimate."
  - "No tol= was needed: all ten tangent-cutter rows (4 hole, 4 spoke sharp/filleted,
    1 spoke recess-less double-boundary, 1 honeycomb flat-tangent) built one valid
    solid with the plain cut(*cutters) on the pinned kernel, so _cut_body ships no
    fuzzy-boolean tolerance -- only a comment recording the measurement."
  - "The spoke fillet's cap (spoke_fillet 5, the field's own le) built on all four
    extreme-sector rows with the effective fillet measured under 5 in every case
    (3.347/0.202/0.18/2.22 mm) -- D-06's gate never fired, no checkpoint needed."

patterns-established:
  - "A cutout wall rule's kernel-boundary test pair is generated from the refusal test's
    own parametrize values, not independently re-measured -- keeps the two suites
    provably in sync (this plan's Task 2 items 1-2)."

requirements-completed: [REQ-cutout-composes, REQ-cutout-conflicts-refused-early]

# Coverage metadata (#1602)
coverage:
  - id: D1
    description: "Real-pipeline spy: the bore-rim and groove-floor selectors are each
      called exactly once (or not at all with no recess) and take exactly the
      no-cutout matrix's own edges, for every pattern x every bore shape x recess
      setting, at the rim limit and at 200 teeth (19 rows); the tip selector, called
      directly on the finished solid, takes exactly 2 x teeth CIRCLE arcs at ra split
      evenly across both end faces in every row"
    requirement: REQ-edge-selection-proven
    verification:
      - kind: integration
        ref: "tests/test_model.py#test_every_selector_takes_only_its_own_edges_with_a_body_cutout"
        status: pass
    human_judgment: false
  - id: D2
    description: "The tip-chamfer real-pipeline spy gains one row per cutout pattern:
      tip_chamfer 0.4 with a cutout present still calls the tip selector once for
      exactly Counter({'CIRCLE': 38}) split 19/19, measured face counts 216 (holes),
      264 (spokes), 338 (honeycomb)"
    requirement: REQ-cutout-composes
    verification:
      - kind: integration
        ref: "tests/test_model.py#test_the_tip_chamfer_takes_exactly_the_tip_arcs_in_the_real_pipeline"
        status: pass
    human_judgment: false
  - id: D3
    description: "_groove_floor_edges' docstring no longer claims the cutouts must
      re-prove the separating invariant: it now cites _cut_body running strictly after
      this selector (_build's own step order) and the proof test by name"
    requirement: REQ-edge-selection-proven
    verification:
      - kind: other
        ref: "grep -c 'must re-prove this separating' src/spur/model.py (== 0)"
        status: pass
    human_judgment: false
  - id: D4
    description: "Every cutout MIN_WALL rule (hole hub/rim/neighbour, spoke
      arm/rim/hub/annulus/opening, honeycomb wall) builds one valid solid exactly at
      its boundary and one field-step past it (validation bypassed via model_copy) --
      the rules sit at the part's MIN_WALL, not a kernel limit"
    requirement: REQ-cutout-conflicts-refused-early
    verification:
      - kind: integration
        ref: "tests/test_model.py#test_the_largest_cutout_each_wall_rule_allows_builds"
        status: pass
      - kind: integration
        ref: "tests/test_model.py#test_the_kernel_cuts_one_valid_solid_past_each_cutout_rule"
        status: pass
    human_judgment: false
  - id: D5
    description: "Every tangent cutter (a hole edge on the recess's inner/outer radius,
      a spoke's hub/rim arcs tangent to each, sharp and filleted, a spoke web at
      MIN_WALL with no recess, a honeycomb cell's flat tangent to the recess wall)
      builds one valid solid with the plain cut(*cutters) -- no fuzzy-boolean tolerance
      needed, none shipped"
    requirement: REQ-cutout-composes
    verification:
      - kind: integration
        ref: "tests/test_model.py#test_a_cutter_tangent_to_a_recess_wall_or_fillet_builds_without_a_fuzzy_boolean"
        status: pass
    human_judgment: false
  - id: D6
    description: "The spoke fillet's cap (D-06) builds on the most awkward sectors the
      rules allow -- one arm, twelve arms at the opening boundary, an annulus at
      MIN_WALL, and 11 mm bars on a 12 mm hub -- each with the effective fillet capped
      below the field's le of 5"
    requirement: REQ-cutout-conflicts-refused-early
    verification:
      - kind: integration
        ref: "tests/test_model.py#test_a_spoke_fillet_at_its_cap_builds_on_extreme_sectors"
        status: pass
    human_judgment: false

# Metrics
duration: ~28min
completed: 2026-09-29
status: complete
---

# Phase 11 Plan 07: Body Cutout Selector, Tangency and Kernel-Boundary Proofs Summary

**A real-pipeline spy proves the bore-rim, groove-floor and tip selectors each still take exactly their own edges with every cutout pattern present; 18 kernel-boundary rows pin every MIN_WALL rule one field-step either side; 10 tangent-cutter rows build without a fuzzy boolean; the spoke fillet's cap builds on the most awkward sectors the rules allow — no `tol=` shipped, no checkpoint fired.**

## Performance

- **Duration:** ~28 min (from the prior plan's final commit, `7980b4d`, to this plan's
  second task commit, `eca02a9`)
- **Completed:** 2026-09-29
- **Tasks:** 2 (both `type="auto"`)
- **Files modified:** 2 (`src/spur/model.py`, `tests/test_model.py`)

## Accomplishments

- `test_every_selector_takes_only_its_own_edges_with_a_body_cutout`: 19 rows spying on
  `_bore_rim_edges` and `_groove_floor_edges` inside the real `_build_checked` pipeline
  (never `build()`, whose `lru_cache` could skip the cutout step) — every pattern
  (holes, spokes, honeycomb) x every bore shape (D-flat, round, hex, keyed round), both
  recesses (12 rows); no recess (3 rows, floor selector never called); each pattern at
  its closest approach to the root circle (3 rows); 200 teeth with holes (1 row, tip
  400). Every row's rim/floor Counters match the pre-cutout matrix's own values exactly
  — measured on the real pipeline before being written into the test, not assumed —
  because both selectors run on the solid before their own operator (chamfer/fillet)
  applies, inside `_cut_bore`/`_cut_face_recesses`, strictly before `_cut_body`. The
  tip selector, called directly on the finished solid, took exactly `2 x teeth` CIRCLE
  arcs at `ra` split evenly across both end faces in every row.
- `test_the_tip_chamfer_takes_exactly_the_tip_arcs_in_the_real_pipeline` gains three
  rows (`tip_chamfer: 0.4` with each pattern): the tip selector is still called once
  for exactly `Counter({'CIRCLE': 38})` split 19/19; measured face counts 216 (holes),
  264 (spokes, measured here as the plan anticipated), 338 (honeycomb — matching the
  planning estimate exactly).
- `_groove_floor_edges`' docstring corrected: no longer claims the cutouts "must
  re-prove" the separating invariant — `_cut_body` runs strictly after this selector by
  `_build`'s own step order, and the new spy test is cited as the proof.
- `test_the_largest_cutout_each_wall_rule_allows_builds` (9 rows) and
  `test_the_kernel_cuts_one_valid_solid_past_each_cutout_rule` (9 rows): every cutout
  MIN_WALL rule — hole hub/rim/neighbour, spoke arm/rim/hub/annulus/opening, honeycomb
  wall — builds one valid solid exactly at its boundary and one 0.05 mm field-step past
  it (validation bypassed via `model_copy`, never re-validated). Every boundary value
  is reused verbatim from `test_calc.py`'s own refusal tests
  (`test_a_hole_rule_refuses_one_step_past_its_wall_and_accepts_it_exactly`,
  `test_a_spoke_rule_refuses_one_step_past_its_wall_and_accepts_it_exactly`,
  `test_a_honeycomb_rule_refuses_one_step_past_it_and_names_its_fields`), so the two
  suites cannot silently drift apart on the same rule.
- `test_a_cutter_tangent_to_a_recess_wall_or_fillet_builds_without_a_fuzzy_boolean`
  (10 rows): a hole edge on the default recess's inner and outer radius and 0.5 mm
  either side; a spoke's analytic hub/rim arcs tangent to each, both sharp and with a
  1 mm fillet; a spoke web at exactly MIN_WALL on both sides with no recess at all
  (tangent to nothing); a honeycomb cell's own flat tangent to the recess wall
  (`recess_inner_d: 13`). Every row built one valid solid with the plain
  `cut(*cutters)` — no fuzzy-boolean tolerance was needed, so `_cut_body` ships none;
  a comment above the cut records the measurement instead (CONTEXT Claude's Discretion:
  `tol=` — a user cannot be told a hole is placed too exactly).
- `test_a_spoke_fillet_at_its_cap_builds_on_extreme_sectors` (4 rows, `spoke_fillet: 5`,
  always capped): one arm (a "C"-shaped sector), twelve arms at the opening boundary, an
  annulus exactly MIN_WALL wide, and 11 mm bars on a 12 mm hub. Each builds one valid
  solid with `spoke_fillet_effective(p)` measured under 5 (3.347/0.202/0.18/2.22 mm) —
  D-06's gate never fired, so no `checkpoint:decision` was needed.

## Task Commits

Each task was committed atomically:

1. **Task 1: Spy every selector in the real pipeline with each cutout pattern on each
   bore shape, and correct the floor selector's docstring** — `faf3616` (test)
2. **Task 2: Pin the kernel either side of every cutout wall rule, build every tangent
   cutter without a fuzzy boolean, and build the spoke fillet at its cap on extreme
   sectors** — `eca02a9` (test)

**Plan metadata:** this SUMMARY and the STATE.md/ROADMAP.md/REQUIREMENTS.md bookkeeping
are committed separately per `execute-plan.md`'s `git_commit_metadata` step.

## Files Created/Modified

- `src/spur/model.py` — `_groove_floor_edges`' docstring corrected (Task 1); the
  no-fuzzy-boolean-tolerance comment above `_cut_body`'s cut (Task 2). No behaviour
  changed in either task — both are proof-only.
- `tests/test_model.py` — `test_every_selector_takes_only_its_own_edges_with_a_body_cutout`
  (19 rows), three new rows on the tip-chamfer real-pipeline spy (Task 1);
  `test_the_largest_cutout_each_wall_rule_allows_builds` (9 rows),
  `test_the_kernel_cuts_one_valid_solid_past_each_cutout_rule` (9 rows),
  `test_a_cutter_tangent_to_a_recess_wall_or_fillet_builds_without_a_fuzzy_boolean`
  (10 rows), `test_a_spoke_fillet_at_its_cap_builds_on_extreme_sectors` (4 rows)
  (Task 2).

## Decisions Made

See `key-decisions` in the frontmatter for the real-pipeline spy's Counter reuse, the
one-step-past rows' exact reuse of `test_calc.py`'s own boundary values (over the plan's
provisional `<interfaces>` estimate), the no-`tol=` finding, and the spoke-fillet cap's
measured margin under 5.

## Deviations from Plan

None — plan executed exactly as written. Every planning probe recorded in the plan's
`<interfaces>` block (the tangent hole/spoke/honeycomb rows, the boundary and
past-the-rule rows, the fillet-cap rows) was re-verified on the pinned kernel before
being written into a test; the one numeric discrepancy found (the opening rule's
past-the-rule `spoke_width` — the plan's provisional interfaces text said 2.77, the
shipped `test_calc.py` boundary is 2.72) was resolved in favour of the already-shipped,
kernel-verified `test_calc.py` value rather than the planning-time estimate, since that
value is the ground truth this task's own rule states it must match ("the same rows one
0.05 mm step past"). This is not a deviation from the plan's intent — the plan named
`test_calc.py`'s own boundary tests as the source (11-03/11-04's own tests) — only from
one transcribed digit in the planning document.

## Issues Encountered

None.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- REQ-edge-selection-proven and REQ-cutout-composes' selector/tangency half are proven
  for every pattern, bore shape and recess setting on the real pipeline; no `tol=`
  needed anywhere in `_cut_body`.
- 11-08 (the recess-fillet survival proof and any remaining built-solid proofs) and
  11-09 (phase close-out, L30) can build directly on this plan's spy pattern and
  boundary-row reuse convention.
- `REQ-cutout-composes` and `REQ-cutout-conflicts-refused-early` are declared by
  multiple plans in this phase (11-01/03/04/05/07/08); the shared-ID gate keeps both
  `Pending` in REQUIREMENTS.md until every declaring plan (11-08 still open) has its own
  SUMMARY — expected, not a blocker.
- No blockers.

---
*Phase: 11-body-cutouts*
*Completed: 2026-09-29*

## Self-Check: PASSED

- `[ -f src/spur/model.py ]` → FOUND
- `[ -f tests/test_model.py ]` → FOUND
- `git log --oneline --all | grep faf3616` → FOUND (Task 1 commit)
- `git log --oneline --all | grep eca02a9` → FOUND (Task 2 commit)
- Plan-level `<verification>` re-run: `make test PYTEST_ARGS="tests/test_model.py
  tests/regression -q"` — 246 passed; `git diff --exit-code
  tests/regression/pre_v0_2.json` — fixture byte-unchanged; `make lint typecheck` —
  both clean; `make verify` — 596 tests, ruff/mypy/import-contracts/no-fake-done all
  clean
- All Task 1 and Task 2 acceptance-criteria greps and collect-only counts re-ran clean:
  `test_every_selector_takes_only_its_own_edges_with_a_body_cutout` collects 19 rows;
  the four Task 2 test functions collect 32 rows combined (>= the 29 floor); `grep -c
  'must re-prove this separating'` is 0; `grep -c
  'test_every_selector_takes_only_its_own_edges_with_a_body_cutout'` in `model.py` is 1;
  `grep -c 'tol='` in `model.py` is 0; `grep -c 'fuzzy-boolean tolerance'` in `model.py`
  is 1
