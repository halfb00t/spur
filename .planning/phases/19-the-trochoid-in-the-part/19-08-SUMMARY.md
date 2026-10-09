---
phase: 19-the-trochoid-in-the-part
plan: 08
subsystem: testing
tags: [trochoid, hob-root, composition, tier-1, tier-2, tip-chamfer, edge-selectors, kernel-boundary]

requires:
  - phase: 19-the-trochoid-in-the-part
    provides: 19-04's root_shape end to end and kernel-tier helpers; 19-05's guards; 19-06's root_form_d, root_waist and ROOT_WAIST_FLOOR; 19-01's chamfer-across-the-junction table
provides:
  - "tests/composition.py ROOTS, ROOT_FIELDS and TROCHOID_THICKNESS; ALWAYS without root_thickness and root_gap"
  - "the calc-tier composition matrix in both roots: 192 rows, every family's field set, warnings, 1.75 chamfer, 1.0 spoke fillet and 0.421 keyed-spokes hub wall unchanged by the root"
  - "the kernel-tier composition matrix in both roots: 24 rows, every trochoid row reads its radial twin's pinned deltas and its tooth-0 root within the kernel bar"
  - "trochoid-d-flat / trochoid-hex / trochoid-keyway selector twins reading the radial counts (rim, floor, tip 38)"
  - "the tip chamfer's cap pinned one 0.05 mm step either side of the hob-root junction on the 6-tooth row where it binds (L29's shape)"
  - "a bare trochoid gear builds one valid solid and prints tip_chamfer_effective null"
affects: [19-09, 19-10]

# Actuals (#2632): chars/4 over the added lines of the three changed files, 0122366..6607f69.
actuals:
  tokens: 2425
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - "a root axis added to a composition matrix as the outermost itertools.product factor, with the root-dependent field set in its own table beside ALWAYS"
    - "a pinned delta read against a same-root reference, so the root cancels out of the subtraction and the radial literals serve both modes"
    - "a boundary pair (builds at the printed cap, fails one 0.05 mm step past the kernel's limit) with a mutation run showing each half fails when its number moves"

key-files:
  created: []
  modified:
    - tests/composition.py
    - tests/test_calc.py
    - tests/test_model.py

key-decisions:
  - "No pinned delta, bar or oracle position count was changed: the hob root composes with every shipped feature on the radial row's own numbers (L08, L33); nothing reached the conditional checkpoint"
  - "The kernel-tier composed-solid oracle reading uses the same 401 positions per edge and KERNEL_BAR_PER_MODULE x module (2e-3 x 1.75) as the kernel-tier rows of 19-04; its cost is recorded for 19-09 to price, not trimmed here"
  - "The binding row is 6 teeth, module 1, 14.5 degrees, no shift, root_fillet 0 (19-01's on-the-law row); the printed cap is 0.9 mm, the 3-dp rounding of 0.89964 = ra - R_join - TIP_CHAMFER_MARGIN"

patterns-established:
  - "A test id with the root first (radial-..., trochoid-...) is made by putting the root parametrize decorator nearest the function, below the row table"

requirements-completed: []  # REQ-trochoid-composes-and-is-priced is also declared by 19-01, 19-03, 19-07, 19-09, 19-10 and 19-11; requirements.ready-ids (#2388) leaves it for the last declaring plan; this plan satisfies its composition half (SC4 in part)

coverage:
  - id: D1
    description: "Calc tier: the 96-row bore x cutout x recess x tip-chamfer matrix runs in both roots (192 rows); every trochoid row derives exactly ALWAYS | root_form_d, root_waist | the four family sets, the hand-written thickness sentence first then its radial twin's warnings, the same 1.75 tip chamfer, 1.0 spoke fillet and 0.421 keyed-spokes hub wall"
    requirement: REQ-trochoid-composes-and-is-priced
    verification:
      - kind: unit
        ref: "tests/test_calc.py#test_every_bore_cutout_recess_and_tip_combination_derives_its_own_numbers (192 passed)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Kernel tier: each of the 12 tier-2 rows (each cutout on each bore, tip chamfer at 1.75, both recesses) builds in both roots with the radial row's pinned face-type, edge and volume deltas, 10-03's and 11-08's proofs unchanged, and under the hob root 2 x 19 root splines whose tooth 0 reads within 2e-3 x 1.75 mm of the oracle"
    requirement: REQ-trochoid-composes-and-is-priced
    verification:
      - kind: unit
        ref: "tests/test_model.py#test_every_feature_proof_holds_on_a_tip_chamfered_gear_with_each_cutout_on_each_bore (24 passed)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Probe boundary: on 6 teeth, module 1, 14.5 degrees, sharp hob, the printed tip chamfer 0.9 builds one valid solid with 12 new CONE faces; patched to 0.9506 (0.05 mm past ra - R_join) the kernel raises BuildError"
    requirement: REQ-trochoid-composes-and-is-priced
    verification:
      - kind: unit
        ref: "tests/test_model.py#test_the_largest_tip_chamfer_the_hob_root_junction_allows_builds"
        status: pass
      - kind: unit
        ref: "tests/test_model.py#test_the_kernel_fails_one_step_past_the_hob_root_junction"
        status: pass
    human_judgment: false
  - id: D4
    description: "Probe adjacency: the rim, floor and tip selectors read the same (rim, floor, tip) counts on trochoid d-flat, hex and keyway gears as on their radial twins, tip 38"
    requirement: REQ-trochoid-composes-and-is-priced
    verification:
      - kind: unit
        ref: "tests/test_model.py#test_each_edge_selector_picks_exactly_its_own_edges[trochoid-d-flat|trochoid-hex|trochoid-keyway]"
        status: pass
    human_judgment: false
  - id: D5
    description: "Probe empty: a bare trochoid gear (bore off, recess none, no tip chamfer, no cutout) builds one valid solid and prints tip_chamfer_effective null"
    requirement: REQ-trochoid-composes-and-is-priced
    verification:
      - kind: unit
        ref: "tests/test_model.py#test_a_bare_trochoid_gear_builds"
        status: pass
    human_judgment: false

duration: "about 25 min"
completed: 2026-10-09
status: complete
plan_head_before: 0122366
plan_head_after: 6607f69
commits: 2
---

# Phase 19 Plan 08: The hob root composes with every shipped feature Summary

**The calc-tier matrix (192 rows) and the kernel-tier matrix (24 rows) each gained a root axis and every trochoid row reads exactly its radial twin's numbers and pinned deltas; the tip chamfer's cap is pinned one 0.05 mm step either side of the hob-root junction on the 6-tooth row where it binds; no delta, bar or oracle position count moved.**

## Performance

- **Duration:** about 25 min of wall time (start not recorded to the second; the one `make verify` is 3 min 22 s)
- **Completed:** 2026-10-09T04:54Z (SUMMARY write)
- **Tasks:** 2
- **Files modified:** 3 (`tests/composition.py`, `tests/test_calc.py`, `tests/test_model.py`)

## Accomplishments

- **Tier 1 in both roots (`2be041e`).** `tests/composition.py` gains `ROOTS` (`radial`, `trochoid`), `ROOT_FIELDS` (`root_thickness`, `root_gap` / `root_form_d`, `root_waist`) and `TROCHOID_THICKNESS`, the sentence captured from `derive(GearParams(root_shape="trochoid"))` on 2026-10-09 and typed in (L33); `ALWAYS` no longer lists the two root-circle fields (19-04's gap). `_TIER_1_ROWS` is `root x bore x cutout x recess x tip`: 192 passed. A scratch survey of all 96 trochoid rows against their radial twins before writing found the non-null sets differ by exactly the four fields, every other value is equal, and the warnings differ by exactly the one thickness sentence. Two mutations (a `root_gap` put back in `ALWAYS`; the thickness sentence dropped from the expectation) each failed 96 of 192 rows and were restored.
- **Tier 2 in both roots (`6607f69`).** `test_every_feature_proof_holds_on_a_tip_chamfered_gear_with_each_cutout_on_each_bore` runs 12 rows per root (24), ids `radial-...` / `trochoid-...`. `root_shape` is in the composed params and in both references (`_build_reference` keys on the whole parameter object, so a reference never serves the other root). The pinned deltas stayed the radial ones for both modes: **no trochoid delta differed from its twin, so the conditional checkpoint was not reached.** Under the hob root the test also asserts the 38 root splines and that tooth 0 reads within `KERNEL_BAR_PER_MODULE * 1.75` of the oracle on the composed solid.
- **Selector twins.** `trochoid-d-flat`, `trochoid-hex`, `trochoid-keyway` read `(CIRCLE 2 LINE 2, 4, 38)`, `(LINE 12, 4, 38)` and `(CIRCLE 2 LINE 2, 4, 38)`: the hob root's CIRCLE arcs sit at the root circle and its splines are BSPLINE, so `_tip_edges` (CIRCLE at ra) never takes them.
- **The chamfer boundary on the hob root (L29's shape).** Binding row, typed from 19-01's table: 6 teeth, module 1, 14.5 degrees, shift 0, `root_fillet` 0, bore off, recess none, `tip_chamfer` 3. The junction is at `R_join` 3.0994 mm, above the pitch circle (3.0), so `ra - R_join - TIP_CHAMFER_MARGIN` = 0.89964 mm binds (0.45 x face_width is 3.375, `ra - r` is 1.0) and the reason reads "to keep it on the involute flank, above its junction with the hob-cut root". The printed cap is **0.9 mm** (three-place rounding) and builds one valid solid with **12 new CONE faces** (2 x 6) over the unchamfered part and nothing else new. 19-01 measured the kernel's last-built size at 0.9006364 mm and first failure at 0.9006397, so 0.9 sits 0.0006 mm inside. With `spur.model.tip_chamfer_effective` patched to `0.9506` (`ra - R_join` + 0.05) the build raises `BuildError: Geometry kernel produced an invalid solid for these parameters.` Two mutations (stand-in 0.9; expected cap 0.95) each turned its test red and were restored.
- **Bare trochoid.** The default gear with `root_shape` trochoid, bore off, recess none, no chamfer is one valid solid and `tip_chamfer_effective` is `None`.

## Cost of the new rows (for 19-09 to price)

`make test PYTEST_ARGS="tests/test_model.py -q -n 8 --no-cov --durations=10 -k 'every_feature_proof_holds or each_edge_selector or hob_root_junction or bare_trochoid'"` read `60 passed in 49.02s` at a 1-minute load near 11.6 on this host. The ten slowest, all trochoid tier-2 rows:

```
20.75s trochoid-d-flat-spokes      19.23s trochoid-hex-spokes
20.28s trochoid-d-flat-holes       19.02s trochoid-round-holes
19.90s trochoid-round-spokes       18.27s trochoid-hex-holes
19.78s trochoid-round-cells        15.37s trochoid-keyed-holes
19.46s trochoid-d-flat-cells       15.08s trochoid-hex-cells
```

Serially (`-n 0`, same host, load about 12) `trochoid-d-flat-holes` took 10.53 s against 1.97 s for `radial-d-flat-holes`: the extra roughly 8.5 s per row is the 401-position-per-edge oracle reading (its own references and builds are cached or comparable), so the 12 trochoid rows add about 100 s of CPU. The 114 new test cases (96 calc rows, 12 trochoid tier-2 rows, 3 selector twins, 3 new tests) moved the full gate from 1081 to **1195 tests**. The oracle position count was not touched.

## Task Commits

1. **Task 1: the calc-tier matrix in both root modes** - `2be041e` (test)
2. **Task 2: the kernel-tier matrix, selector twins, chamfer boundary and bare build** - `6607f69` (test)

**Plan metadata:** the docs commit that carries this SUMMARY, STATE.md, ROADMAP.md and `.planning/state.json`.

`commits: 2` is measured from the ledger: `git rev-list --count 0122366..HEAD` read 2 at SUMMARY write.

## Decisions Made

See `key-decisions`: nothing was re-pinned or loosened; the oracle cost is recorded, not trimmed; the binding row is 19-01's on-the-law 6-tooth row at tip radius 0.

## Deviations from Plan

### Plan-literal items

**1. Both tasks are `tdd="true"` but the behaviour they test already existed.** The plan is `type: execute` and the code under test (19-04 to 19-06) was already committed, so no RED commit exists. Each test was shown to have teeth by mutation instead: tier 1 (a field put back in `ALWAYS`, the thickness sentence dropped) failed 96 of 192; the boundary pair (stand-in 0.9, expected cap 0.95) each failed. The tier-2 trochoid reading uses the oracle already shown to have teeth by 19-04's tripwire.

**2. Pytest ids put the root first only after reordering decorators.** First run gave `d-flat-holes-trochoid`; the root parametrize was moved below the row table so the ids read `trochoid-d-flat-holes` as the plan says.

**Total deviations:** 0 auto-fixed, 2 plan-literal items. **Impact on plan:** none on behaviour.

## Issues Encountered

- **Gate result:** `make verify` exit 0, **`1195 passed in 201.82s (0:03:21)`**, coverage **97.90 %** (floor 96); ruff, mypy `--strict` (43 source files), 5 import contracts kept, unfinished-work scan clean. Host load at the start was 11.6 (1-minute). That is 202 s against 95 s (19-06, load about 3) and 117 to 138 s (19-04, 19-05, 19-07's baseline): 19-08 adds about 100 s of CPU to the tier-2 oracle rows, and at this host load the wall time nearly doubled. L34's 66 s bar and the oracle position count stay 19-09's question; nothing was done about them here.
- **No `ReentrantCallError` or other flake appeared** in the full gate (the log was searched; zero matches) or in the two commit hooks, so the resource-tracker debt item's trigger did not fire and nothing was kept under `investigation/`.
- **Commit attribution line.** Commits end with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`, the line the session's attribution reminder gives (the dispatch text's CLAUDE.md note names a different model; `CLAUDE.md` itself names neither), as 19-05 and 19-06 did.
- **Scope.** Sibling 19-07's files (`tests/test_cli.py`, README, `src/spur/cli.py`, `docs/architecture/cli.md`) were not touched; `tests/test_cli.py` still imports `BORE_REFUSALS` and `CUTOUT_REFUSALS` from `tests/composition.py`, unchanged (23 refusal tests pass).

## Known Stubs

None. No placeholder values, empty data flows or TODO markers were added.

## Threat Flags

None. T-19-16 (a printed tip chamfer the kernel cannot cut) is mitigated: the cap reads the junction (19-04), and the boundary pair pins it either side on the binding row. T-19-17 (a selector taking a root arc, or nothing) is mitigated: the three trochoid selector twins assert the radial counts. No new network, auth or file surface.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- 19-09 prices the new rows (the figures above), owns the gate cost against L34 (95 to 202 s on this host, load dependent) and the bench swap of `trochoid_outline`.
- 19-10 can cite SC4 as met for the tip chamfer, both recesses and each cutout on each bore with the hob root: the composed deltas are root-independent.
- Files filed: no debt or idea item was filed by this plan.

## Self-Check: PASSED

- Files: `tests/composition.py`, `tests/test_calc.py`, `tests/test_model.py` exist and carry `ROOTS`, `ROOT_FIELDS`, `TROCHOID_THICKNESS`, the tier-1 `itertools.product(ROOTS, ...)` and `test_the_largest_tip_chamfer_the_hob_root_junction_allows_builds`; this SUMMARY is at `.planning/phases/19-the-trochoid-in-the-part/19-08-SUMMARY.md`.
- Commits `2be041e` and `6607f69` are ancestors of HEAD; `git rev-list --count 0122366..HEAD` read 2.
- Acceptance: 192 tier-1 passed; 23 `test_cli.py` refusal tests passed; the `compose tests present` and `SC1 holds` lines printed; 24 tier-2 rows, three selector twins, the boundary pair and the bare build pass; `make verify` exit 0, `1195 passed`.

---
*Phase: 19-the-trochoid-in-the-part*
*Completed: 2026-10-09*
