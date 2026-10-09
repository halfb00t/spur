---
phase: 19-the-trochoid-in-the-part
plan: 02
subsystem: bench
tags: [cadquery, trochoid, spline-deviation, oracle, guard-bars, waist-floor, spike, bench]

requires:
  - phase: 18-trochoid-maths-proved
    provides: RootCurve / root_mode / the swept-cutter oracle tests/trochoid_oracle.clearance
  - phase: 19-the-trochoid-in-the-part
    provides: 19-01's bench/trochoid_part.py (trochoid_outline, trochoid_blank, root_edges, oracle_reading)
provides:
  - "bench/trochoid_part.py subcommands spline, arc, product, waist; pure helpers deviation_a, deviation_b, proposed_bar, product_row"
  - "the two research files' spline-deviation methods reconciled (SUMMARY correction 16 closed): method B is the deviation"
  - "the kernel bar, four guard bars, ROOT_ARC_MIN and the waist floor, each from two recorded numbers with the headroom beside it, over all 10,326 trochoid gears (no stride)"
  - "bench/RESULTS.md ### Bars adopted (19-02): the human's five answers, 19-04 / 19-05 / 19-06 read their constants from it"
affects: [19-04, 19-05, 19-06, 19-09, 19-10]

# Actuals (#2632): chars/4 over the added lines of the three files, d8abb23 against plan_head_before.
actuals:
  tokens: 24233
  tasks: 3
  commits: 4

tech-stack:
  added: []
  patterns:
    - "a bar is written from the whole product's maximum with the headroom beside it, never from a sample and never after seeing a pass (L08, L33 D-06, PITFALLS 8)"
    - "spawn-context process pool with a module-level worker for the whole-product bench runs (the bench/trochoid.py shape)"

key-files:
  created: []
  modified:
    - bench/trochoid_part.py
    - tests/test_bench.py
    - bench/RESULTS.md

key-decisions:
  - "Kernel bar 2e-3 x module (bar-proposed): 10.9x the worst whole-product spline error, 1.8431e-4 per module; the tripwire must sit on a module-1 row (5.5x over there, 0.66x of the bar on module 10)"
  - "Waist floor 0.4 mm absolute, MIN_TIP_FDM (floor-print): no failure signature exists in the walk, so the floor is a printability choice; warns on 771 of 10,326 product gears, 595 of them module-0.2"
  - "Waist field name root_waist (name-root_waist), a published key on /api/info and spur info from its first release"
  - "D-02 confirmed (d02-confirm): root_shape Literal radial/trochoid default radial, group Teeth after tip_chamfer, --root-shape, root_fillet read as the hob's tip radius; 19-04 is not blocked"
  - "Area guard 5e-2 on the polygon through the arcs' midpoints (area-midpoints), 13.6x; the plan's arcs-as-chords measure (bar 0.1, 8.2x) rejected for being under 10x"
  - "Planner's-call bars as measured: ROOT_SPACING_RATIO_MAX 1000 (75x), annulus TOL 1e-6 mm (8.8e6x), ROOT_JUNCTION_BAR_RAD 1e-11 rad (40.9x; 18-01's 1e-12 is only 4.1x here and must not be reused), ROOT_ARC_MIN 2e-6 mm (15.8x below the smallest real chord)"

patterns-established:
  - "Method B (distance to the reference polyline) is the spline deviation; method A (nearest vertex) is the vertex-spacing floor of its own reference and never a bar"
  - "An oracle reading at 41 positions can sit 28 % below the true spline error; a bar is read at 401 or more positions per root edge"

requirements-completed: []  # REQ-outline-consumes-root-curve, REQ-derived-numbers-honest-under-trochoid, REQ-root-mode-decided are declared here and by sibling plans with no SUMMARY yet: requirements.ready-ids returned 0/3 ready (#2388 shared-ID gate); this plan satisfies them in part; nothing marked

coverage:
  - id: D1
    description: "The two spline-deviation methods reconciled: method B reproduces STACK's three trochoid figures (3.5807, 3.8933, 3.9847e-5 mm against 3.58, 3.89, 3.99e-5) and the oracle agrees with method B to 0.01 of a unit of the third digit on seven kernel-tier rows"
    requirement: REQ-outline-consumes-root-curve
    verification:
      - kind: unit
        ref: "tests/test_bench.py#test_deviation_b_reads_the_distance_to_the_polyline_not_to_its_vertices"
        status: pass
      - kind: unit
        ref: "tests/test_bench.py#test_the_kernel_tier_rows_are_seven_trochoid_gears_and_three_carry_stacks_figures"
        status: pass
      - kind: other
        ref: ".venv/bin/python -m bench.trochoid_part spline (exit 0, 'Verdict: reconciled')"
        status: pass
    human_judgment: false
  - id: D2
    description: "The kernel bar and the four guard bars measured over every trochoid gear of the sweep product, no stride: 10,326 gears built, 0 kernel exceptions, each maximum printed with its gear and each proposal with its headroom"
    requirement: REQ-derived-numbers-honest-under-trochoid
    verification:
      - kind: unit
        ref: "tests/test_bench.py#test_the_proposed_bar_is_the_smallest_listed_value_ten_times_over_the_worst"
        status: pass
      - kind: unit
        ref: "tests/test_bench.py#test_the_junction_bar_is_the_smallest_power_of_ten_over_the_gap_and_the_libm_floor"
        status: pass
      - kind: other
        ref: ".venv/bin/python -m bench.trochoid_part product (exit 0, 10,326 of 10,326 built)"
        status: pass
    human_judgment: false
  - id: D3
    description: "The root arc's dead band has two measured edges (silent drop at chords 2e-12 and 2e-10 mm, kernel exception up to 2.0e-7 mm, first building chord 4.0e-7 mm) and ROOT_ARC_MIN = 2e-6 mm sits 15.8x below the smallest real chord"
    requirement: REQ-outline-consumes-root-curve
    verification:
      - kind: other
        ref: ".venv/bin/python -m bench.trochoid_part arc (exit 0, 'ROOT_ARC_MIN proposal' line)"
        status: pass
    human_judgment: false
  - id: D4
    description: "D-07's waist walk run as written (6, 7, 8 teeth, module 1, 14.5 degrees, x -0.6 to 0, tip radius 0 / 0.38 / 3.0, backlash 0.1 and 0): 1,061 trochoid gears built one valid solid each, thinnest built waist 3.2325e-3 mm, no failure signature, three floor candidates with firing counts"
    requirement: REQ-derived-numbers-honest-under-trochoid
    verification:
      - kind: unit
        ref: "tests/test_bench.py#test_the_waist_walk_is_d07s_grid_at_both_backlashes"
        status: pass
      - kind: other
        ref: ".venv/bin/python -m bench.trochoid_part waist (exit 0, 'thinnest built waist' line)"
        status: pass
    human_judgment: false
  - id: D5
    description: "The kernel bar, the waist floor, the waist field's name, D-02's one-way door and the area guard bar are the human's, recorded with the human's words in bench/RESULTS.md ### Bars adopted (19-02)"
    requirement: REQ-root-mode-decided
    verification:
      - kind: other
        ref: "bench/RESULTS.md ### Bars adopted (19-02) (committed d8abb23; section check prints 'bars section ok')"
        status: pass
    human_judgment: true
    rationale: "Each value is a human choice made on recorded numbers; automation can check that the section exists and carries the words and ids, not that the choice is right"
  - id: D6
    description: "Nothing a shared link produces moved: params.py, calc.py, model.py, cli.py, app.js and tests/regression/pre_v0_2.json are byte-identical to the phase base"
    verification:
      - kind: other
        ref: "SC1 check: git diff --quiet <phase base> over the six paths (prints 'SC1 holds' after d8abb23)"
        status: pass
    human_judgment: false

duration: "1h 45m"
completed: 2026-10-09
status: complete
plan_head_before: 88c5ec52b37be9a1fb73dc7862a015f22dabeff4
plan_head_after: d8abb23dcb9d7332bb196f7021ac80b81ad83940
# MEASURED from the ledger: git rev-list --count plan_head_before..HEAD reads 5 because 19-03's f2f4f47 (investigation/19-03-isolation.md only) landed between af53e4f and d8abb23; the 4 below are the commits titled (19-02), counted with --grep.
commits: 4
---

# Phase 19 Plan 02: Reconcile the bars, measure the guards, walk the waist Summary

**Spline deviation reconciled to one method (distance to the polyline), then a 2e-3 x module kernel bar, four guard bars, a 2e-6 mm root-arc minimum and a 0.4 mm waist floor set from all 10,326 trochoid gears of the sweep product, with the human's answers and the headroom beside every value.**

## Performance

- **Duration:** about 1h 45m of executor time: the first executor 16:37Z to 18:07Z on 2026-10-08 (the waist walk alone ran 713 s, `product` 150 s), then this continuation after the human's answer. The wait at the checkpoint is not counted. 19-03 ran in the same wave and its commit sits between this plan's.
- **Started:** 2026-10-08T16:37Z (approximate; the commit before it is `88c5ec5`, 22:37 +06:00)
- **Completed:** 2026-10-09T03:50Z (approximate)
- **Tasks:** 3 (two auto, one blocking-human decision)
- **Files modified:** 3 (`bench/trochoid_part.py` +1064/-24, `tests/test_bench.py` +132/-1, `bench/RESULTS.md` +480)

## The human's answers (Task 3)

The reply, verbatim: **`take the recommendations`**. The human named no option id. The orchestrator mapped those words to the ids the first executor recommended in its own checkpoint report; the mapping is the orchestrator's, from the executor's stated recommendations, and is recorded as such.

| Decision | Adopted id (mapped) | Value | The numbers it rests on |
|---|---|---|---|
| Kernel bar | `bar-proposed` | 2e-3 x module | worst whole-product spline error 1.8431e-4 per module, so 10.9x headroom; module-1 tripwire (tip radius +0.05 mm) reads 1.1039e-2 mm = 5.5x over the bar; on module 10 the same shift reads 0.66x of it, so the tripwire must sit on a module-1 row |
| Waist floor | `floor-print` | 0.4 mm absolute (`MIN_TIP_FDM`) | thinnest built waist 3.2325e-3 mm; warns on 294 of 1,061 walk gears and 771 of 10,326 product gears; small-module caveat: 595 of 616 module-0.2 gears (195 on tangent joins) against 176 of 9,710 gears of module 1 and above |
| Waist field name | `name-root_waist` | `root_waist` | the tooth's narrowest thickness in the hob-cut root, printed for every trochoid gear, true on tangent and crossing joins; sits beside `root_d`, `root_fillet`, `root_form_d` |
| D-02's one-way door | `d02-confirm` | `root_shape` and the `root_fillet` reinterpretation stand | 10,326 of 10,326 gears built; **19-04 is NOT blocked** |
| Area guard bar | `area-midpoints` | 5e-2 on the polygon through the arcs' midpoints | max 3.6791e-3, 13.6x; the plan's arcs-as-chords measure (max 1.2162e-2, bar 0.1, 8.2x) rejected for being under 10x |

The planner's-call guard bars (none under 10x, no human answer needed) are recorded as measured in `### Bars adopted (19-02)`: spacing ratio 1000 (75x; the kernel fails 729x above it), annulus [rf - TOL, ra + TOL] with TOL 1e-6 mm (8.8e6x), junction gap 1e-11 rad (40.9x; 18-01's 1e-12 rad is only 4.1x over this product's tangent maximum, so 19-05 must not reuse it), root arc 2e-6 mm (15.8x below the smallest real chord).

## Accomplishments

- **Reconciliation (SUMMARY correction 16 closed).** Method B (distance from a kernel-spline sample to the reference polyline) reproduces STACK's three trochoid figures: 3.5807, 3.8933 and 3.9847e-5 mm against the quoted 3.58, 3.89 and 3.99e-5, off by 0.07, 0.33 and 0.53 of a unit of the third digit. Method A (nearest vertex) reads 5.18 to 5.23e-5 on the same splines because it adds the reference's own vertex spacing. STACK's shipped-flank 6.0e-5 and 1.0e-4 mm are method A: every A reading is within 2.5 % of half the largest vertex gap of its own reference, so they are the vertex-spacing floor of a 20,001-point curve, not a deviation (method B on the same splines reads 1.5 to 3.3e-6 mm). PITFALLS' 0.13 micrometre is reproduced by neither. **Method B is the deviation, method A is the vertex-spacing floor, and the oracle agrees with method B to 0.01 of a unit of the third digit on all seven kernel-tier rows.** The 41-position oracle reading of 19-01 can sit 28 % low (module-10 row, 4.4785e-4 against 6.2097e-4 mm), so 19-04 reads at 401 or more positions per root edge.
- **Whole-product guard numbers (`product`).** 31,446 sweep cases, 10,326 trochoid gears, all built, 0 kernel exceptions, 150 s on 18 spawn workers, no stride (the 5,159-gear sample of RESEARCH is replaced). Worst spline error per module **1.8431e-4** (30 teeth, module 1.75, 14.5 degrees, x -0.6, backlash 1.0, tip radius capped from 3.0). Spacing ratio max 13.325, annulus worst excursion 1.137e-13 mm, junction gap 2.442e-13 rad (tangent, 4,303 gears) and 6.939e-16 rad (crossing, 6,023), smallest root-arc chord 3.1644e-5 mm. Bunching: the kernel builds a resampled curve up to a chord ratio of 7.3e4 and fails with an empty `Standard_Failure` at 7.3e5.
- **Root-arc dead band (`arc`).** Silent drop at chords 2e-12 and 2e-10 mm (valid solid, 62 faces where 74 are expected); `Standard_Failure: GC_MakeArcOfCircle::Value() - no result` from 2e-9 mm up to **2.0e-7 mm, the last failing chord**; **4.0e-7 mm is the first building chord** (74 faces, valid), monotone. Reachable from user input: backlash 0.19898413579248878 with the tip radius capped leaves a = 1.0e-8 mm and the same exception, which `_build_checked` would relabel with the wrong remedy ("try smaller fillets or chamfers"). `ROOT_ARC_MIN` 2e-6 mm is 10.0x the last failing chord and 15.8x below the smallest real chord.
- **D-07's waist walk (`waist`).** 1,098 gears (6, 7, 8 teeth, module 1, 14.5 degrees, x -0.6 to 0 in 0.01 steps, tip radius 0 / 0.38 / 3.0, backlash 0.1 and 0) in 713 s: 37 `tooth severed` (refused by `root_mode` before the kernel), 1,061 trochoid gears, **all 1,061 built one valid solid**, worst oracle reading 6.8995e-5 mm, 0 readings over even 1e-3 x module. **Thinnest built waist 3.2325e-3 mm** (6 teeth, x -0.57, backlash 0.1, tip radius 0.38; RESEARCH F8's scratch walk found 4.98e-3). No failure signature exists above the spline-error scale, so the floor is the human's choice on these numbers: the measured candidate does not exist, the spline-scale one warns on 0 gears, the printability one (0.4 mm) on 771 of 10,326.
- **Gate:** the first executor ran `make verify` on `af53e4f`: `1034 passed in 54.33s`, coverage 97.68 % (floor 96). This continuation changed only `bench/RESULTS.md`; its commit ran the pre-commit `make verify.fast` (Passed). SC1 check after `d8abb23`: `SC1 holds` (the six product paths byte-identical to the phase base).

## Task Commits

1. **Task 1: Reconcile the deviation methods, read the kernel tier on seven rows (`spline`), the root-arc dead band (`arc`)** - `01cd617` (feat)
2. **Task 2: Whole-product guard numbers (`product`) and D-07's waist walk (`waist`)** - `2dbf6f3` (feat)
3. **Task 2 follow-up (not in the plan): the floor candidates' product counts broken down by module** - `af53e4f` (feat)
4. **Task 3: Record the bars and the waist floor the human adopted** - `d8abb23` (docs)

**Plan metadata:** the docs commit that carries this SUMMARY, STATE.md and ROADMAP.md (hash in the STATE.md session line).

`commits: 4` is measured from the ledger and counts the commits titled `(19-02)`. The raw `git rev-list --count 88c5ec5..HEAD` reads 5 because 19-03's `f2f4f47` (`investigation/19-03-isolation.md` only, not this plan's) sits between `af53e4f` and `d8abb23`.

## Files Created/Modified

- `bench/trochoid_part.py` - subcommands `spline`, `arc`, `product`, `waist`; pure helpers `deviation_a`, `deviation_b`, `proposed_bar`, the junction-bar and shoelace helpers, `product_row`
- `tests/test_bench.py` - eight pins, no kernel build (the plan asked for two): the proposed bar, method B against the polyline, a non-outward reference refused by both methods, the seven kernel-tier rows, the junction bar, the listed-bar chooser, the shoelace area, D-07's grid at both backlashes
- `bench/RESULTS.md` - `### Spline deviation and the kernel bar (19-02)`, `### Root arc dead band (19-02)`, `### Guard numbers over the product (19-02)`, `### Waist walk (19-02, D-07)`, `### Bars adopted (19-02)`, each with its host state

## Decisions Made

The five answers in the table above, and:

- The bar rests on the converged method-B maximum, never on a 41-position oracle reading, and it is applied to readings at 401 or more positions.
- The waist is printed for every trochoid gear and warned below the floor, never refused (D-06); the floor was chosen after the walk, not before (D-07).
- A bar under 10x joins the human's checkpoint; one at or over 10x is the planner's call. The area guard was the only guard under 10x, and only on the plan's own measure.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Sample count of 2,001 positions, not 201**
- **Found during:** Task 1 (`spline`)
- **Issue:** the plan reads the kernel spline at `positionAt(i / 200)`. On the 14-tooth row 201 positions read 3.9675e-5 mm, 2.2 units off STACK's third digit, so the reconciliation would have failed on the sampling and not on the methods.
- **Fix:** 2,001 positions for the deviation figures (3.9847e-5 mm at 2,001 and at 20,001, 0.5 units off); `product` uses the same. The oracle reads 401 positions per root edge.
- **Files modified:** `bench/trochoid_part.py`
- **Verification:** the "Method B against the number of positions" table in `bench/RESULTS.md`; `spline` exits 0.
- **Committed in:** `01cd617`

**2. [Rule 3 - Blocking] Backlash bracket [0, 0.4], not [0, 1]**
- **Found during:** Task 1 (`arc`, the tuned-backlash row)
- **Issue:** the plan bisects backlash over [0, 1], but `GearParams` refuses above about 0.49 ("Teeth come to a point"), so the upper half of the bracket cannot build a `GearParams` at all.
- **Fix:** 40 halvings over [0, 0.4]. Tuned backlash 0.19898413579248878 gives a = 1.0e-8 mm (target 1e-8, within the plan's factor 2) with the tip radius capped to 0.614 mm of a rho_max of 0.614000014 mm, and the bench outline raises `Standard_Failure: GC_MakeArcOfCircle::Value() - no result`.
- **Files modified:** `bench/trochoid_part.py`
- **Verification:** `arc` prints the tuned row and exits 0.
- **Committed in:** `01cd617`

**3. [Rule 2 - Missing Critical] A second area measure, through the arcs' midpoints**
- **Found during:** Task 2 (`product`)
- **Issue:** the plan's area guard takes the tip arc and the root arc as chords; over the whole product that reads a maximum of 1.2162e-2, and no listed bar (0.01 to 0.1) reaches 10x (0.1 is 8.2x). A guard bar picked at 8.2x, or a larger one invented to fit, is exactly what the phase prohibits (T-19-03).
- **Fix:** `product` prints the polygon through each arc's midpoint beside the plan's measure (max 3.6791e-3, 5e-2 at 13.6x); both are in the record and the human chose the midpoint measure.
- **Files modified:** `bench/trochoid_part.py`, `bench/RESULTS.md`
- **Verification:** both lines in `product`'s output and in `### Guard numbers over the product (19-02)`.
- **Committed in:** `2dbf6f3`

### Plan-literal items that did not apply as written, or went beyond it

**4. The waist walk also runs at backlash 0.** The plan's grid does not name a backlash; the default (0.1) is the shipped one and 0 is what RESEARCH F8's scratch walk used, so both are walked (1,098 gears, not 549) and the walk reproduces F8's 4.9794e-3 mm. `2dbf6f3`.

**5. `--bar-per-module` on `waist`, default 2e-3.** The walk needs the proposed bar to count readings over it; the flag defaults to the proposal `product` made and is recorded in the output. `2dbf6f3`.

**6. `ProcessPoolExecutor` with the spawn context, not `multiprocessing.Pool`.** `product` and `waist` use `concurrent.futures.ProcessPoolExecutor` with `multiprocessing.get_context("spawn")` and a module-level worker (`product_row`), the shape the plan asked for in effect; recorded because `bench/trochoid.py` names the pool differently. `2dbf6f3`.

**7. The dead band's first building chord is 4.0e-7 mm, not 6e-7.** The plan, from RESEARCH, says "3e-7 and up built" (a chord of 6e-7). The table also tries a = 2e-7 (chord 4.0e-7 mm), which builds with 74 faces; the last failing chord is 2.0e-7 mm. RESEARCH had not tried 2e-7. `01cd617`.

**8. [TDD ceremony] RED was a load failure and there is no separate `test(...)` commit.** Task 1 is `tdd="true"`; the tests were written first and failed with an `ImportError` at collection (the helpers did not exist yet), which by `tdd.md` is INVALID_RED, not a valid RED. No `test(19-02)` commit exists because the plan prescribes one `feat(19-02)` commit per task and the L36 pre-commit hook (`make verify.fast`) refuses a failing test. The plan is `type: execute`, so the plan-level gate sequence does not apply. GREEN: the new tests pass, then `1034 passed` on the gate.

**9. Refactors of 19-01's code, forced by this plan's needs.** `oracle_reading` gained a `samples` argument (default 40, so its 41-position behaviour and 19-01's callers are unchanged); `trochoid_outline` was split into `outline_teeth` plus the edge assembly, and `trochoid_blank` into `extrude_outline` plus the curve, so `arc` can replace the first point of a curve and `product` can measure the outline without building a solid. No product module was touched. `01cd617`, `2dbf6f3`.

**10. A follow-up commit not in the plan: `af53e4f`.** The first version of the floor candidates printed only the product-wide firing counts; the by-module breakdown (595 of 616 module-0.2 gears against 176 of 9,710 at module 1 and above) is what makes the small-module caveat visible, and the human's decision rests on it. A fourth commit in a plan that promised three.

---

**Total deviations:** 3 auto-fixed (1 Rule 1, 1 Rule 2, 1 Rule 3) and 7 plan-literal items or additions.
**Impact on plan:** none on the measurements' honesty; Rule 2's second area measure is the only item that changed what a human had to decide (it removed a question rather than adding one).

## Issues Encountered

- 19-03 ran in the same wave: its Task 1 commit `f2f4f47` landed between this plan's last two commits and is not counted above. Both plans loaded the host (1-minute load 49.6 at the end of the waist walk, 68.9 at the end of `product`); no figure here is a timing and none rests on a load reading.
- `product`'s and `waist`'s host-state loads are far above D-05's quiet bar; they are recorded in `bench/RESULTS.md`, and the spline errors, guard maxima and waists are geometric, not timed.

## Known Stubs

None. `bench/trochoid_part.py` carries no placeholder values; the typed kernel-tier rows are checked against the live `root_mode` by a test.

## Threat Flags

None. Bench scripts and a record only: no network, auth, file-access or trust-boundary surface was added. T-19-03 (a bar tuned toward a pass) is mitigated: each proposal is computed by a pure helper pinned in `tests/test_bench.py` from the recorded maximum, the kernel bar, the waist floor and the one guard under 10x went to the human at a blocking checkpoint, and `### Bars adopted (19-02)` records both numbers, the headroom and the human's words. T-19-04 (a stride-2 sample missing the tripping case) is mitigated: `product` ran every trochoid case, 10,326 of 10,326.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- **19-04 is not blocked.** D-02 is confirmed: `root_shape: Literal["radial", "trochoid"]` default `radial`, group Teeth after `tip_chamfer`, generated `--root-shape` flag, `root_fillet` read as the hob's tip radius. 19-04 reads the kernel bar as 2e-3 x module at 401 or more positions per root edge, with its tripwire on a module-1 row (the 10-tooth, 20 degrees, x 0 row reads 1.1039e-2 mm).
- **19-05** takes `ROOT_ARC_MIN` 2e-6 mm, `ROOT_SPACING_RATIO_MAX` 1000, the annulus at `model.TOL`, `ROOT_AREA_REL_MAX` 5e-2 on the arc-midpoint polygon and `ROOT_JUNCTION_BAR_RAD` 1e-11 rad. It must not reuse 18-01's 1e-12 rad (4.1x over this product's tangent maximum).
- **19-06** takes the `root_waist` key and `ROOT_WAIST_FLOOR` 0.4 mm absolute, with the small-module caveat in `### Bars adopted (19-02)`.
- **19-03** (resource-tracker isolation) is paused at its own checkpoint and untouched by this plan.
- The first executor ran `make verify` at `af53e4f`; 19-09 compares the end-of-phase gate with 19-01's baseline of 52.89 s.

## Self-Check: PASSED

- Files: `bench/trochoid_part.py`, `tests/test_bench.py`, `bench/RESULTS.md` (with `### Bars adopted (19-02)`) exist; this SUMMARY is at `.planning/phases/19-the-trochoid-in-the-part/19-02-SUMMARY.md`.
- Commits `01cd617`, `2dbf6f3`, `af53e4f` and `d8abb23` are ancestors of HEAD; `git rev-list --count --grep='(19-02)' 88c5ec5..HEAD` reads 4.
- The five answers, verbatim words and mapped ids are recorded here and in `### Bars adopted (19-02)`.

---
*Phase: 19-the-trochoid-in-the-part*
*Completed: 2026-10-09*
