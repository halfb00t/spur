---
phase: 12-composition-pass
plan: 06
subsystem: testing
tags: [model, kernel-proof, composition-matrix, tip-chamfer, cutouts, recess, d-07, d-09]

# Dependency graph
requires:
  - phase: 12-composition-pass
    provides: "12-05-SUMMARY.md: tests/composition.py and the calc-level tier-1/refusal-composition rows (D-07 tier 1, D-08); 12-03-SUMMARY.md: spoke_count's le lowered 40 -> 32 (D-03 gate)"
provides:
  - "D-07 tier 2 proven on the kernel: the tip chamfer (1.75 mm, the default gear's own cap) applied together with each cutout (holes, spokes, honeycomb) on each bore (d-flat, round, hex 6, keyed round) -- 12 built rows, each re-running 10-03's _assert_only_the_tip_arcs_were_chamfered and 11-08's _assert_the_cutout_is_what_derive_prints unchanged on the one composed solid"
  - "The single-sided-recess x cutout pairing no earlier test built: 3 rows (holes, spokes, cells) x recess_sides=\"top\", re-running 11-08's _assert_the_recess_fillet_survives and _assert_the_cutout_is_what_derive_prints"
  - "_honeycomb_nearest_point_angle(p, rf) -> float: a new probe-location helper (sibling of 11-08's _honeycomb_farthest_vertex_angle) that walks a honeycomb cell's six edges and returns the angle of the point nearest the axis, so the hub probe always lands on the cell actually nearest -- not fixed at +X, which fails on the hex and keyed bores"
  - "Every face-type delta, edge delta, removed volume and TORUS count on all 15 new rows measured on the pinned kernel this session; all match the planning probe in 12-06-PLAN.md <interfaces> exactly, no difference to record"
affects: [12-09-milestone-record]

# Actuals (#2632)
actuals:
  tokens: 2700
  tasks: 2
  commits: 2
  plan_head_before: 1ede44ba1f773fff2d874c9920aaf0d5a2eb870d
  plan_head_after: ae53fead4efb66d365380f6651961e67913611e5

# Tech tracking
tech-stack:
  added: []
  patterns: ["functools.cache(_build_checked) as a module-level, session-scoped reference cache for the no-cutout baseline solid per bore -- only these composed tests call it and none of them monkeypatches the kernel, so the cache never goes stale under a patched build (12-06-PLAN.md <interfaces>, measured saving: 8 builds of ~0.8s)", "typing.cast(dict[str, float], ...) to narrow a pre-existing dict[str, int]-inferred module constant (HOLES, CELLS) into the dict[str, float] a merged-dict annotation needs, an established idiom already used in test_api.py/test_pool.py/test_records.py for the same class of mypy-strict friction"]

key-files:
  created: []
  modified:
    - tests/test_model.py

key-decisions:
  - "COMPOSED_BORES and COMPOSED_CUTOUTS both needed an explicit dict[str, dict[str, float]] annotation to satisfy mypy --strict: a dict literal assigned in annotated context allows int->float promotion per entry, but a dict literal referencing pre-existing module-level names (HOLES, CELLS, already inferred dict[str, int]) does not -- those two needed an explicit cast(dict[str, float], ...) instead of a second annotation (SPOKES needed no cast, already dict[str, float] via hub_d 13.2)."
  - "The cells branch of the composed test (hub_angle via the new _honeycomb_nearest_point_angle, rim_angle via the existing _honeycomb_farthest_vertex_angle) was added in Task 2's commit alongside the helper itself, not in Task 1 -- Task 1 only writes the keyed-spokes row (holes/spokes branches only), so referencing an as-yet-undefined helper in an unreached elif branch would still have been a real mypy NameError at Task-1-commit time; keeping the two-branch if/elif in Task 1 and extending it to three branches in Task 2, in the same commit as the helper, avoided that."
  - "No composed tripwire added, per 12-CONTEXT.md's Claude's Discretion and the plan's own instruction: the per-feature tripwires (test_the_tip_chamfer_proof_fails_when_the_tip_step_is_skipped, test_the_cutout_proof_fails_when_the_cutout_step_is_skipped, test_the_fillet_survival_proof_fails_when_the_recess_fillet_is_skipped) already show each helper failing when its own step is skipped, and every composed delta here is a pinned literal, so a vanished feature on a composed gear would change a pinned count and fail loudly without a dedicated tripwire."
  - "No keyed D-flat row added: 11-08's test_the_recess_floor_fillet_survives_every_cutout_on_every_bore (1352-ish) already covers every keyed-bore x cutout combination, and this plan's own 12 tip rows already put the keyed bore against every cutout -- a keyed D-flat row would repeat coverage the plan's own prohibition list forbids repeating."

patterns-established:
  - "A probe-location helper (not a proof) reads the actual built geometry to find where to probe, rather than a hand-picked angle -- _honeycomb_nearest_point_angle continues _honeycomb_farthest_vertex_angle's own precedent (11-08) one level further: both walk the six analytic cell-edge segments the kernel actually cuts and report where the interesting point is, so a probe never silently misses when the bore shape moves which cell is nearest or farthest."

requirements-completed: []  # REQ-three-interfaces-extended is shared with 12-01/12-05/12-07/12-08/12-09 per the shared-ID gate (#2388); marks complete only once the last declaring plan finishes.

coverage:
  - id: D1
    description: "D-07 tier 2 (12 rows): the tip chamfer applied together with each cutout (holes, spokes, honeycomb) on each bore (d-flat, round, hex 6, keyed round), both recesses, bore_chamfer 0 and recess_fillet 0 (10-03's own preconditions) -- on each composed solid, 10-03's _assert_only_the_tip_arcs_were_chamfered and 11-08's _assert_the_cutout_is_what_derive_prints both pass unchanged. The keyed-spokes row sits at the phase's tightest adjacency (hub wall 0.421 mm, 0.021 mm above MIN_WALL) and builds one valid solid that passes both proofs."
    requirement: "REQ-three-interfaces-extended"
    verification:
      - kind: unit
        ref: "tests/test_model.py#test_every_feature_proof_holds_on_a_tip_chamfered_gear_with_each_cutout_on_each_bore (12 rows)"
        status: pass
    human_judgment: false
  - id: D2
    description: "3 single-sided-recess rows (holes, spokes, cells x recess_sides=\"top\", default bore chamfer and recess fillet): 11-08's _assert_the_recess_fillet_survives and _assert_the_cutout_is_what_derive_prints both pass on each, proving the pairing no existing matrix built (11-08's own matrix is both-recesses only)."
    requirement: "REQ-three-interfaces-extended"
    verification:
      - kind: unit
        ref: "tests/test_model.py#test_the_recess_fillet_and_cutout_proofs_hold_with_a_single_sided_recess (3 rows)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Every face-type delta, edge delta, removed volume and TORUS count on all 15 rows is measured on the pinned kernel and pinned as a literal, exactly as 11-08 did -- no closed form claimed after an arbitrary boolean; the only new proof-shape addition is the probe-location helper _honeycomb_nearest_point_angle, never a new assertion shape (D-09)."
    verification:
      - kind: other
        ref: "grep -c 'def _honeycomb_nearest_point_angle(' tests/test_model.py (1); .venv/bin/python -m pytest tests/test_model.py --collect-only -q | grep -cE 'tip_chamfered_gear_with_each_cutout_on_each_bore\\[|cutout_proofs_hold_with_a_single_sided_recess\\[' (15); git diff c9a169d -- tests/test_model.py | grep -c '^-[^-]' (0, no existing line removed or changed)"
        status: pass
    human_judgment: false
  - id: D4
    description: "The phase's fixture and src/ contracts stay unmoved: the pre-v0.2 fixture is byte-unchanged, neither commit touches a src/ file, and the 15 new rows' measured pytest time is recorded honestly for 12-09's D-10 gate (this plan alone reads over the ~25s advisory share)."
    verification:
      - kind: other
        ref: "git diff --exit-code c9a169d -- tests/regression/pre_v0_2.json (exit 0); git show --name-only --format= <each commit> | grep -c '^src/' (0 for both); .venv/bin/python -m pytest tests/test_model.py -q -k 'tip_chamfered_gear or single_sided_recess' --durations=0 (15 passed, 30.66-30.73s across two runs, load 1.86-4.14 and 2.65-4.06)"
        status: pass
    human_judgment: false

# Metrics
duration: ~23min
completed: 2026-09-30
status: complete
---

# Phase 12 Plan 06: Composition Matrix (Built Solid) Summary

**15 new kernel-level rows prove D-07 tier 2 and D-09 on the pairs no earlier phase built -- the tip chamfer with each cutout on each bore (12 rows) and a single-sided recess with each cutout (3 rows) -- every count measured on the pinned kernel and matching the planning probe exactly, at a combined pytest cost of ~30.7s.**

## Performance

- **Duration:** ~23 min
- **Started:** 2026-09-30T11:26:00Z (approx, session's first `make verify` run)
- **Completed:** 2026-09-30T11:49:00Z (approx)
- **Tasks:** 2 (1 tracer, 1 auto)
- **Files modified:** 1 (`tests/test_model.py`)

## Accomplishments

- `test_every_feature_proof_holds_on_a_tip_chamfered_gear_with_each_cutout_on_each_bore` (12 rows): the tip chamfer (1.75 mm, the default gear's own pitch-circle cap) applied together with each cutout (holes, spokes, honeycomb) on each bore (d-flat, round, hex 6, keyed round), on one composed solid per row -- 10-03's `_assert_only_the_tip_arcs_were_chamfered` and 11-08's `_assert_the_cutout_is_what_derive_prints` both re-run unchanged on that solid. Task 1 wrote the tightest-adjacency row first (keyed round bore + spokes, hub wall 0.421 mm, 0.021 mm above `MIN_WALL`) as the tracer; Task 2 filled the remaining eleven.
- `test_the_recess_fillet_and_cutout_proofs_hold_with_a_single_sided_recess` (3 rows): each cutout composed with a top-only recess (default bore chamfer and recess fillet, no tip chamfer) -- 11-08's `_assert_the_recess_fillet_survives` and `_assert_the_cutout_is_what_derive_prints` both pass, proving the pairing no existing matrix built (11-08's own matrix is both-recesses only).
- `_honeycomb_nearest_point_angle(p, rf) -> float` added beside `_honeycomb_farthest_vertex_angle`: walks each honeycomb cell's six analytic edges and returns the angle of the point nearest the axis (the foot of the perpendicular, clamped to the edge -- the same measure `calc._hex_reach` uses internally, kept as a point instead of only a distance). A probe location, not a proof: the hub probe must land on whichever cell is actually nearest, which is not on +X for the hex or keyed bore (a fixed 0.0 hub angle fails there, as planning found).
- Every face-type delta, edge delta, removed volume and TORUS count on all 15 rows was measured on the pinned kernel this session (a scratch probe script run before writing the tests, then the real pytest rows) and matches the planning probe in `12-06-PLAN.md <interfaces>` exactly -- no single number needed adjusting. `d-flat` and `round` rows read identical deltas for every cutout, which is expected: the delta is against the same bore's own no-cutout reference, so whatever the bore itself contributes cancels out of the subtraction.
- No composed tripwire (the per-feature tripwires already show each helper failing when its own step is skipped, and every composed number here is a pinned literal); no keyed-D-flat row (11-08's own matrix and this plan's 12 tip rows already put the keyed bore against every cutout) -- both per `12-CONTEXT.md`'s Claude's Discretion and the plan's own instruction.
- Both commits touch zero `src/` files, keep `make lint typecheck lint-imports` clean, and leave the pre-v0.2 fixture byte-unchanged.

## Task Commits

Each task was committed atomically:

1. **Task 1: Tracer -- one composed solid, keyed round bore with spokes and the tip chamfer, through both proofs** - `9eaed6d` (test)
2. **Task 2: The other eleven tip rows and the three single-sided-recess rows, measured and pinned** - `ae53fea` (test)

**Plan metadata:** committed separately (see below)

## Files Created/Modified

- `tests/test_model.py` -- `TIPPED`, `COMPOSED_BORES`, `COMPOSED_CUTOUTS`, `_build_reference` module-level names; `_honeycomb_nearest_point_angle`; `test_every_feature_proof_holds_on_a_tip_chamfered_gear_with_each_cutout_on_each_bore` (12 rows); `test_the_recess_fillet_and_cutout_proofs_hold_with_a_single_sided_recess` (3 rows); `import functools`, `from typing import cast`

## Decisions Made

See `key-decisions` in the frontmatter: the `dict[str, dict[str, float]]` annotation plus two `cast()` calls needed to satisfy mypy strict on the merged-dict pattern; the cells branch (and its new helper) landing in Task 2's commit, not Task 1's, so Task 1's own commit never references an undefined name; no composed tripwire; no keyed-D-flat row.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] `COMPOSED_BORES`/`COMPOSED_CUTOUTS`'s merged-dict literal fails mypy strict**
- **Found during:** Task 1 (writing the keyed-spokes row's `kw = {**TIPPED, **COMPOSED_BORES[bore], **COMPOSED_CUTOUTS[cutout]}`)
- **Issue:** Without an explicit annotation, mypy infers `COMPOSED_BORES`'s value type as `dict[str, object]` (the empty `"d-flat": {}` entry forces the join), so unpacking it into another dict literal raised three `dict-item`/`arg-type`-shaped errors ("Unpacked dict entry ... incompatible type 'object'"). Annotating `COMPOSED_BORES: dict[str, dict[str, float]]` fixed it outright (a dict literal assigned in annotated context allows each entry's `int` values to promote to `float`), but the same annotation on `COMPOSED_CUTOUTS` still failed for the two entries referencing pre-existing module constants (`HOLES`, `CELLS` -- both already inferred `dict[str, int]` at their own declaration, which is invariant against `dict[str, float]`).
- **Fix:** Annotated `COMPOSED_BORES: dict[str, dict[str, float]]`; for `COMPOSED_CUTOUTS`, annotated the same way and wrapped the two int-only references in `cast(dict[str, float], HOLES)` / `cast(dict[str, float], CELLS)` (an established idiom already used in `test_api.py`, `test_pool.py`, `test_records.py` for the identical class of friction); `SPOKES` needed no cast, since its `hub_d: 13.2` already makes it `dict[str, float]`.
- **Files modified:** tests/test_model.py
- **Verification:** `make lint typecheck` clean; `.venv/bin/python -m mypy tests/test_model.py` reports "Success: no issues found"
- **Committed in:** `9eaed6d` (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (mechanical mypy-strict fix, no behavior change)
**Impact on plan:** No scope creep; `HOLES`/`SPOKES`/`CELLS` themselves were not touched (they are pre-existing 11-08 lines, out of this plan's edit scope) -- only the new merged dicts needed the cast.

## Issues Encountered

None beyond the deviation above.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `REQ-three-interfaces-extended` stays open in `REQUIREMENTS.md` (shared with 12-01/12-05/12-07/12-08/12-09 per the shared-ID gate, #2388) -- marks complete only once the last declaring plan finishes.
- D-10's phase-wide budget: this plan's 15 new rows measured **30.66-30.73s** of pytest time across two runs (`--durations=0`, load 1.86-4.14 and 2.65-4.06) -- over the ~25s advisory line the prior-wave facts flagged for this plan's own share, and by itself close to D-10's phase-wide 30s ceiling before 12-07/12-08's own new tests are added. Recorded honestly, not tuned: 12-09 reads this number first when it measures the phase's real `make verify` delta and decides whether trimming is needed (its own pre-agreed first offer is trimming tier-2 rows to one bore per cutout, never dropping tier 1 or a refusal row).
- `make verify`: 880 passed in 208.21s (full suite, this session, after both commits) -- green, no regressions; `make lint typecheck lint-imports` and the plan's own `<verification>` block all pass; the pre-v0.2 fixture is byte-unchanged.
- No blockers.

---
*Phase: 12-composition-pass*
*Completed: 2026-09-30*

## Self-Check: PASSED

- FOUND: `tests/test_model.py` (modified, two new parametrized tests + one new helper)
- FOUND: commit `9eaed6d` in `git log --oneline --all`
- FOUND: commit `ae53fea` in `git log --oneline --all`
- Re-ran all task acceptance criteria: keyed-spokes collect count = 1; both-tests collect count = 15; `_honeycomb_nearest_point_angle` def count = 1; `git diff c9a169d -- tests/test_model.py` removed-line count = 0 (both after Task 1 and after Task 2)
- Re-ran the plan's own `<verification>` block: `make test PYTEST_ARGS="tests/test_model.py -q -k 'tip_chamfered_gear or single_sided_recess'"` -- 15 passed; `git diff --exit-code c9a169d -- tests/regression/pre_v0_2.json` -- clean (exit 0); `make lint typecheck` -- both clean
- `git rev-list --count 1ede44b..HEAD` = 2, matching `commits: 2` above
