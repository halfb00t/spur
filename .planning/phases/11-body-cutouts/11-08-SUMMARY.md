---
phase: 11-body-cutouts
plan: 08
subsystem: cad-kernel-proofs
tags: [cadquery, built-solid, derived-numbers, recess-fillet, tripwire]

# Dependency graph
requires:
  - phase: 11-03, 11-04, 11-05
    provides: "the three cutout patterns (holes, spokes, honeycomb), each with its own
      MIN_WALL rules, cutout_walls()/hex_cells() and model._cut_body's shared
      cut(*cutters) shape"
  - phase: 11-07
    provides: "the selector/tangency proofs and the kernel-boundary rows this plan's
      probes were re-verified against (spoke_fillet_effective, TOL, _build_checked
      usage pattern)"
provides:
  - "REQ-cutout-derived-numbers proven on the built solid: each pattern's cut is exactly
    what derive() prints -- face-type deltas, edge count, removed volume (the sharp
    spoke and honeycomb rows checked against a closed-form analytic formula, the
    filleted-spoke row against a pinned kernel measurement) -- and the printed
    cutout_hub_wall/cutout_rim_wall sit exactly where the solid's own walls are, probed
    at arm 0 / hole 0's +X position and the honeycomb's own -X-facing cell and farthest
    vertex"
  - "REQ-cutout-composes' counted proof: with both recesses, on every bore shape (D-flat,
    round, hex, keyed round) and every pattern, the recess floor fillet survives on
    every floor edge the cutout leaves -- no sharp floor-to-wall circle anywhere on the
    finished solid, TORUS counts pinned per row"
  - "Two tripwires (10-03's shape): _cut_body patched to a no-op shows the built-solid
    proof fail while derive() still prints the cutout's wall (L08's failure);
    recess_fillet patched to 0.0 shows the survival proof's own assert sharp == 0 catch
    the skip"
  - "Same-link-same-part (L05) for every cutout pattern"
affects: [11-09]

# Actuals (#2632)
actuals:
  tokens: 4035
  tasks: 2
  commits: 2
  plan_head_before: c3bd49fa3ba15b65ee2a644459f8e4a4d5435784
  plan_head_after: a84c800da34ee774d5d9dc8ebca010040566fda9

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "The built-solid proof reuses 10-03's shared-helper-plus-tripwire shape
      (_assert_the_cutout_is_what_derive_prints), extended with a probe-point pair per
      wall (material/void either side of cutout_hub_wall and cutout_rim_wall at a
      caller-supplied angle) so the printed wall is read back off the solid, not just
      the face/edge/volume deltas."
    - "A removed-volume claim is checked against a closed-form analytic formula wherever
      one exists (holes: N*pi*r^2*fw; sharp spokes: an annulus minus N bars, the bar
      area an antiderivative of the polar element 2r*asin(o/r)dr; honeycomb: N cells at
      sqrt(3)/2*size^2*fw) rather than a pinned literal -- the filleted-spoke row has no
      closed form and stays pinned, with a comment saying so."
    - "The fillet-survival tripwire demonstrates the failure through the proof's own
      assert (sharp == 0), not a raised BuildError: with no fillet the groove's sharp
      floor-to-wall corners survive the cutout and _groove_floor_edges matches them
      instead of raising -- the try/except around it exists so the tripwire's own
      failure mode is always an AssertionError, never pytest's unraised-exception
      Failed."

key-files:
  created: []
  modified:
    - tests/test_model.py

key-decisions:
  - "The sharp-spoke and honeycomb removed-volume figures are computed in the test from
    an analytic formula, not the plan's own pinned <interfaces> literals -- verified to
    agree with the built kernel volume to 1e-9 mm3 on the default gear's rows before
    being written in (2026-09-29). The filleted-spoke row has no closed form and stays a
    pinned kernel measurement (2934.725405 mm3), as the plan anticipated."
  - "The keyed-round SPOKES13 fillet-1 row's TORUS count (12) was not measured in
    planning (11-CONTEXT.md <interfaces> says so explicitly) -- measured here on the
    pinned kernel and recorded in the test and this summary, per the plan's own
    instruction (\"the keyed SPOKES13 count measured here and recorded\")."
  - "Every other TORUS count in the 13-row survival matrix matched the planning probe
    exactly on first measurement: D-flat HOLES 4, HOLES_ACROSS 14, SPOKES12 fillet-1 20,
    CELLS 14; round HOLES 4, SPOKES12 20, CELLS 14; hex HOLES 14, SPOKES12 12, CELLS 40;
    keyed HOLES 4, CELLS 4 -- no sharp floor-to-wall circle survived any of the 13 rows."
  - "SPOKES12 (hub_d 12) and SPOKES13 (hub_d 13.2, clears the keyed bore's 6.179 mm
    mouth) are new module-level row dicts, distinct from the existing SPOKES constant
    (hub_d 13.2, spoke_fillet baked in) 11-07's selector matrix already uses -- kept
    separate rather than reused, since this plan's own SPOKES12/SPOKES13 pair needed the
    fillet applied per-row, not baked into the base dict."

patterns-established:
  - "A removed-volume assertion is checked against a derived closed-form formula
    wherever the geometry admits one, falling back to a pinned kernel measurement (with
    a comment saying no closed form exists) only where it does not -- stronger than a
    pinned literal alone, because a future regression in the formula's own inputs
    (cutout_walls(), hex_cells()) would also have to break the geometry identically to
    stay silent."

requirements-completed: [REQ-cutout-composes, REQ-cutout-derived-numbers, REQ-hole-cutout,
  REQ-spoke-cutout, REQ-honeycomb-cutout]

# Coverage metadata (#1602)
coverage:
  - id: D1
    description: "Built-solid proof: each pattern's cut (holes, sharp spokes, filleted
      spokes, honeycomb) on a recess-less gear matches derive()'s printed face-type
      deltas, edge count and removed volume exactly, and cutout_hub_wall/cutout_rim_wall
      read back off the solid at arm 0 / hole 0's +X position or the honeycomb's own
      -X-facing cell and farthest vertex"
    requirement: REQ-cutout-derived-numbers
    verification:
      - kind: integration
        ref: "tests/test_model.py#test_each_cutout_is_exactly_what_derive_prints_on_the_built_solid"
        status: pass
    human_judgment: false
  - id: D2
    description: "Tripwire: _cut_body patched to a no-op shows the built-solid proof
      fail (the cut equals the plain solid) while derive() still prints a non-null
      cutout_hub_wall -- L08's failure, demonstrated"
    requirement: REQ-cutout-derived-numbers
    verification:
      - kind: integration
        ref: "tests/test_model.py#test_the_cutout_proof_fails_when_the_cutout_step_is_skipped"
        status: pass
    human_judgment: false
  - id: D3
    description: "Same-link-same-part (L05): two independent builds of one parameter set
      agree on faces, edges and volume, for holes, filleted spokes and honeycomb on the
      default (recessed) gear"
    requirement: REQ-cutout-derived-numbers
    verification:
      - kind: integration
        ref: "tests/test_model.py#test_the_same_cutout_link_builds_the_same_solid_twice"
        status: pass
    human_judgment: false
  - id: D4
    description: "Recess-fillet survival, counted: with both recesses, on every bore
      shape and every pattern (13 rows), no sharp floor-to-wall circle survives and the
      TORUS face count matches the pinned kernel -- the keyed-round SPOKES13 row
      measured here, not carried from planning"
    requirement: REQ-cutout-composes
    verification:
      - kind: integration
        ref: "tests/test_model.py#test_the_recess_floor_fillet_survives_every_cutout_on_every_bore"
        status: pass
    human_judgment: false
  - id: D5
    description: "Tripwire: recess_fillet patched to 0.0 leaves sharp floor-to-wall
      corners that survive the cutout, so the survival proof's own assert sharp == 0
      catches the skip -- demonstrated on two rows"
    requirement: REQ-cutout-composes
    verification:
      - kind: integration
        ref: "tests/test_model.py#test_the_fillet_survival_proof_fails_when_the_recess_fillet_is_skipped"
        status: pass
    human_judgment: false

# Metrics
duration: ~35min
completed: 2026-09-29
status: complete
---

# Phase 11 Plan 08: Body Cutout Built-Solid and Recess-Fillet Survival Proofs Summary

**Every cutout's built solid matches derive()'s printed faces, edges, volume and walls exactly (sharp spokes and honeycomb checked against a closed-form formula, not a pinned literal); the recess floor fillet survives on every floor edge across 13 pattern-x-bore-shape rows with zero sharp corners; two tripwires prove both proofs fail when their step is skipped.**

## Performance

- **Duration:** ~35 min
- **Started:** 2026-09-29
- **Completed:** 2026-09-29
- **Tasks:** 2 (both `type="auto"`)
- **Files modified:** 1 (`tests/test_model.py`)
- **`make verify`:** 621 tests, 179.08s wall (up from 596 at the phase's last full run,
  11-07-SUMMARY.md); `make lint typecheck` clean; import-boundary contracts kept (5/5);
  `no-fake-done` clean.

## Accomplishments

- `_assert_the_cutout_is_what_derive_prints`: the shared proof/tripwire helper, 10-03's
  shape, extended with a wall-probe pair (material just inside `cutout_hub_wall`, void
  just outside it, at the caller's own `hub_angle`; the mirror at `cutout_rim_wall`,
  `rim_angle`) so the printed walls are read back off the solid, not assumed.
- `test_each_cutout_is_exactly_what_derive_prints_on_the_built_solid` (4 rows,
  `recess_sides: "none"` so the recess's own faces never mix into the cutout's delta):
  HOLES (`+6 CYLINDER`, `+18` edges, `565.486678 mm3` -- `6 * pi * 2^2 * 7.5`); sharp
  SPOKES12 (`+8 PLANE +8 CYLINDER`, `+48` edges, `2959.086823 mm3` -- an analytic
  bar-area formula computed in the test, matching the kernel to `1e-9 mm3`); filleted
  SPOKES12 (`+8 PLANE +24 CYLINDER`, `+96` edges, `2934.725405 mm3` -- no closed form,
  pinned; plus 32 `CIRCLE` edges of radius `spoke_fillet_effective(p)` split 16/16
  across the end faces); CELLS (`+108 PLANE`, `+324` edges, `1052.220866 mm3` -- 18
  cells at `sqrt(3)/2 * 3^2 * 7.5`, matching the kernel to `1e-9 mm3`; the `PLANE` delta
  read from `6 * derive(p).hex_cell_count`, and the rim probe angle from the farthest
  vertex `hex_cells(p, rf)` itself returns).
- `test_the_cutout_proof_fails_when_the_cutout_step_is_skipped` (3 rows: HOLES, SPOKES12
  fillet 1, CELLS): `spur.model._cut_body` patched to a no-op; `derive()` still prints
  `cutout_hub_wall` (the number that no longer matches the part -- L08's failure); the
  proof helper raises `AssertionError` on the first face-delta check (the cut equals the
  plain solid with the step skipped).
- `test_the_same_cutout_link_builds_the_same_solid_twice` (3 rows: HOLES, filleted
  SPOKES12, CELLS, default gear with its own recess): two independent
  `_build_checked` builds of one link agree on faces, edges and volume (rel `1e-9`).
- `_assert_the_recess_fillet_survives`: `_groove_floor_edges` called directly on the
  finished solid (a `try`/`except BuildError`, not `pytest.raises` -- every failure of
  this helper must read as an `AssertionError` for the tripwire below); the sharp-circle
  count must be `0`, and the `TORUS` face count must match the row's pinned value.
- `test_the_recess_floor_fillet_survives_every_cutout_on_every_bore` (13 rows: HOLES,
  HOLES_ACROSS, SPOKES12 fillet 1 and CELLS on D-flat, round and hex bores; HOLES,
  SPOKES13 fillet 1 and CELLS on the keyed round bore): both recesses (the field's own
  default), TORUS counts pinned per row. Twelve rows matched the planning probe in
  `11-CONTEXT.md <interfaces>` on first measurement; the keyed-round SPOKES13 row --
  explicitly flagged in the plan as not probed in planning -- measured `TORUS 12` here.
  No row left a sharp floor-to-wall circle.
- `test_the_fillet_survival_proof_fails_when_the_recess_fillet_is_skipped` (2 rows:
  D-flat HOLES_ACROSS, D-flat CELLS): `spur.model.recess_fillet` patched to
  `lambda _p, _rf: 0.0`; both rows leave 14 sharp floor-to-wall circles, so the
  survival proof's own `assert sharp == 0` fails -- the tripwire's failure mode is the
  proof's own assertion, not a raised `BuildError`, exactly as the plan specified.

## Task Commits

Each task was committed atomically:

1. **Task 1: Read each pattern back off the built solid against derive()'s numbers, and
   show the proof fail when the cut is skipped** -- `c50c61a` (test)
2. **Task 2: Count the recess floor fillet on every pattern and bore shape with both
   recesses, and show the count fail when the fillet is skipped** -- `a84c800` (test)

**Plan metadata:** this SUMMARY and the STATE.md/ROADMAP.md/REQUIREMENTS.md bookkeeping
are committed separately per `execute-plan.md`'s `git_commit_metadata` step.

## Files Created/Modified

- `tests/test_model.py` -- `HOLES_ACROSS`/`SPOKES12`/`SPOKES13` row dicts;
  `_spoke_bar_area`, `_honeycomb_farthest_vertex_angle`,
  `_assert_the_cutout_is_what_derive_prints` helpers (Task 1);
  `test_each_cutout_is_exactly_what_derive_prints_on_the_built_solid` (4 rows),
  `test_the_cutout_proof_fails_when_the_cutout_step_is_skipped` (3 rows),
  `test_the_same_cutout_link_builds_the_same_solid_twice` (3 rows) (Task 1);
  `_assert_the_recess_fillet_survives` helper,
  `test_the_recess_floor_fillet_survives_every_cutout_on_every_bore` (13 rows),
  `test_the_fillet_survival_proof_fails_when_the_recess_fillet_is_skipped` (2 rows)
  (Task 2). `bore_mouth_limit` and `hex_cells` added to the `spur.calc` import.

## Decisions Made

See `key-decisions` in the frontmatter for the analytic-formula-over-pinned-literal
choice, the keyed SPOKES13 measurement, the full 13-row TORUS reconciliation against
planning, and the SPOKES12/SPOKES13 naming decision.

## Deviations from Plan

None -- plan executed exactly as written. The one number the plan itself flagged as
unmeasured (the keyed-round SPOKES13 fillet-1 row's TORUS count) was measured here and
recorded, exactly as the plan instructed ("the keyed SPOKES13 count measured here and
recorded"); this is not a deviation, it is the plan's own Task 2 item 2 carried out.

## Issues Encountered

None.

## User Setup Required

None -- no external service configuration required.

## Next Phase Readiness

- REQ-cutout-derived-numbers and REQ-cutout-composes are both proven on the built solid
  for every pattern, bore shape and recess setting; REQ-cutout-composes was flipped to
  `Complete` in `REQUIREMENTS.md` this plan (the shared-ID gate found no other
  in-progress declaring plan). REQ-cutout-derived-numbers, REQ-hole-cutout,
  REQ-spoke-cutout and REQ-honeycomb-cutout are also declared by `11-09-PLAN.md`
  (phase close-out, no `SUMMARY.md` yet) and stay `Pending` in `REQUIREMENTS.md` until
  11-09 finishes -- expected, not a blocker (11-07-SUMMARY.md's own note on this gate).
- 11-09 (phase close-out, L30) can build directly on this plan's proofs: every
  built-solid and recess-survival number this phase needs is now measured and pinned.
- No blockers.

---
*Phase: 11-body-cutouts*
*Completed: 2026-09-29*

## Self-Check: PASSED

- `[ -f tests/test_model.py ]` -> FOUND
- `git log --oneline --all | grep c50c61a` -> FOUND (Task 1 commit)
- `git log --oneline --all | grep a84c800` -> FOUND (Task 2 commit)
- Plan-level `<verification>` re-run: `make test PYTEST_ARGS="tests/test_model.py
  tests/regression -q"` -- 271 passed; `git diff --exit-code
  tests/regression/pre_v0_2.json` -- fixture byte-unchanged; `make lint typecheck` --
  both clean; `make verify` (full suite, run before the two-commit split) -- 621 tests,
  ruff/mypy/import-contracts/no-fake-done all clean.
- All Task 1 and Task 2 acceptance-criteria greps and collect-only counts re-ran clean:
  `test_each_cutout_is_exactly_what_derive_prints_on_the_built_solid[...]` +
  `test_the_cutout_proof_fails_when_the_cutout_step_is_skipped[...]` +
  `test_the_same_cutout_link_builds_the_same_solid_twice[...]` collect 10 rows;
  `test_the_recess_floor_fillet_survives_every_cutout_on_every_bore[...]` +
  `test_the_fillet_survival_proof_fails_when_the_recess_fillet_is_skipped[...]` collect
  15 rows; `grep -c 'def _assert_the_cutout_is_what_derive_prints('` is 1; `grep -c
  'monkeypatch.setattr("spur.model._cut_body"'` is 1; `grep -c 'def
  _assert_the_recess_fillet_survives('` is 1; `grep -c
  'monkeypatch.setattr("spur.model.recess_fillet"'` is 1; `git show --format=
  --name-only` for both task commits lists only `tests/test_model.py`.
