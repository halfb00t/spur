# Roadmap: spur

## Milestones

- ✅ **v0.1 Hardening** — Phases 1–6 (shipped 2026-09-25) — full detail in
  `milestones/v0.1-ROADMAP.md`, audit in `milestones/v0.1-MILESTONE-AUDIT.md`
- 🚧 **v0.2 Fit to Shaft** — Phases 7–12 (in progress)

## Phases

**Phase Numbering:**

- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)
- Numbering continues across milestones — the next milestone starts at Phase 7.

<details>
<summary>✅ v0.1 Hardening (Phases 1–6) — SHIPPED 2026-09-25</summary>

- [x] Phase 1: v0 Baseline (Shipped) (no plans — built and verified directly against `make verify` before GSD)
- [x] Phase 2: CAD Off the Event Loop (5/5 plans) — completed 2026-09-24
- [x] Phase 3: Structured Logging at the Composition Boundary (3/3 plans) — completed 2026-09-24
- [x] Phase 4: Typed Derived-Dimensions Contract (3/3 plans) — completed 2026-09-24
- [x] Phase 5: CI Observed Green (6/6 plans) — completed 2026-09-25
- [x] Phase 6: Address tech debt: merge gate + solid cache (4/4 plans) — completed 2026-09-25 (added 2026-09-25 after the Phase 5 review and the first milestone audit)

Goals, success criteria and plan lists: `milestones/v0.1-ROADMAP.md`. Phase artifacts:
`milestones/v0.1-phases/`. Quick tasks: `milestones/v0.1-quick/`.

</details>

### 🚧 v0.2 Fit to Shaft (In Progress)

**Milestone Goal:** A generated gear mounts on a real shaft and prints light — new bore
profiles, body cutouts and a tooth-tip chamfer, all additive on the shipped spur pipeline,
with tooth measurements untouched.

- [x] **Phase 7: Foundation — Generalized Edge Selection + Regression Fixture** - Fix the (completed 2026-09-26)
      bore-rim edge selector for any bore shape and lock a regression fixture every later
      phase extends
- [x] **Phase 8: Hex Bore** - A hexagonal bore profile, proving the generalized selector on (completed 2026-09-26)
      real geometry
- [x] **Phase 9: Keyway Bore** - A keyway cut into a round or D-flat bore, with an explicit, (completed 2026-09-27)
      documented depth datum
- [x] **Phase 10: Tooth-Tip Chamfer** - An edge-break chamfer on the tooth-tip arcs (completed 2026-09-28)
- [x] **Phase 11: Body Cutouts** - Lightening holes, spoke arms, or a honeycomb web — one (completed 2026-09-29)
      pattern per part
- [ ] **Phase 12: Composition Pass** - The full feature matrix, the heaviest-configuration
      build-time sweep, and three-interface parity

## Phase Details

### Phase 7: Foundation — Generalized Edge Selection + Regression Fixture

**Goal**: The bore-rim edge selector works correctly for any bore shape, and a regression
fixture proves every pre-v0.2 parameter set is unchanged — the foundation every later phase
extends.
**Depends on**: Nothing (first phase of v0.2; continues from v0.1 Phase 6)
**Requirements**: REQ-defaults-off-regression, REQ-edge-selection-proven
**Success Criteria** (what must be TRUE):

  1. `bore_rim_limit(p)` computes the correct edge-selection bound per bore shape (round and
     D-flat today; the function is shaped to extend to hex and keyway in Phases 8–9) — a
     unit test asserts `len(_bore_rim_edges(...)) > 0` whenever `bore_chamfer > 0`, for every
     bore shape that exists at this phase.
  2. A selector that finds zero edges while its feature is on raises a build error rather
     than shipping unchamfered or unfilleted geometry (no silent no-op).
  3. A regression fixture captures `derive()`'s full 19-field output plus `build()`'s solid
     volume and bounding box for the defaults, every existing test's parameter set, and the
     README's example links, and passes at HEAD — this fixture is what every later phase
     re-runs, not a new ad hoc check.
  4. `make verify` is green with the new fixture and selector tests included.

**Research flag**: No — the fix (compute the selection bound correctly per shape) is fully
specified by `research/ARCHITECTURE.md`'s Q2; no open questions (`research/SUMMARY.md`
"Phases with standard, well-documented patterns").
**Plans**: 2/2 plans executed

Plans:
**Wave 1**

- [x] 07-01-PLAN.md — L05 regression fixture: 78-entry corpus → 44 records, `make fixture.regen`, replay test, measured cost (D-06 gate) (wave 1)

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 07-02-PLAN.md — `calc.bore_rim_limit(p)`, `BORE_RIM_SLACK`, both selectors raise `BuildError` on zero edges, exact count matrix, L26 (wave 2)

### Phase 8: Hex Bore

**Goal**: A user can request a hexagonal bore and get a correctly measured hex profile,
proving Phase 7's generalized selector against real geometry.
**Depends on**: Phase 7
**Requirements**: REQ-hex-bore, REQ-derived-dimensions-additive
**Success Criteria** (what must be TRUE):

  1. Setting `bore_hex` (across-flats, mm, 0 = off) cuts a regular hexagon bore with
     `bore_clearance` added across the flats; the hexagon replaces the round profile —
     `bore_d` does not apply, and a non-zero `bore_d` alongside `bore_hex` produces a
     `warnings` entry rather than being silently ignored; `bore_chamfer` chamfers all six
     rim edges on both faces, proven by an edge-count assertion — Phase 7's selector fix
     shown on real geometry (the v0.1 selector would have selected zero edges here).
  2. `bore_hex` with a non-zero `bore_flat` still builds. The hexagon replaces the
     whole round profile, so `bore_flat` is ignored like `bore_d`, and one `warnings`
     entry names each ignored non-zero field with its value. This is never a 422
     (08-CONTEXT.md D-01/D-02; this supersedes the criterion's earlier `bore_flat` 422,
     which `bore_flat`'s non-zero default would have fired on every link that only adds
     `bore_hex`). `bore_hex` together with a keyway field is a 422 naming the fields,
     delivered with the keyway fields in Phase 9.
  3. `DerivedDimensions` gains its first new field (hex corner-to-corner diameter), `null`
     when `bore_hex == 0`; the 19 existing fields keep their names, types and values; `make
     verify` stays green under `disallow_any_explicit` with no suppressions.
  4. Measured build time for a hex bore at the heaviest allowed configuration (max teeth,
     max `bore_hex`) is recorded in `bench/RESULTS.md`, inside `SPUR_BUILD_TIMEOUT=30s`.
  5. Phase 7's regression fixture still passes unmodified — hex bore defaults to off, and
     every pre-v0.2 parameter set is still identical in derived dimensions, volume and
     bounding box.
**Research flag**: No — `Workplane.polygon(circumscribed=True)` is numerically verified
against the installed `.venv`; a small, well-bounded feature (`research/SUMMARY.md`).
**Plans**: 4/4 plans executed

Plans:
**Wave 1**

- [x] 08-01-PLAN.md — D-01 first: amend REQ-hex-bore and SC2 (the hex replaces `bore_flat` too; the keyway 422 moves to Phase 9) through the edit-phase tooling, one human confirmation (wave 1)

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 08-02-PLAN.md — Tracer: `?bore_hex=6` end to end (field, cut, `bore_rim_limit`/`bore_mouth_limit`, two derived fields, UI rows, replay additive-field rule), then proof on the built solid: 12 rim edges, measured flats/corners, MIN_WALL to the recess (wave 2)

**Wave 3** *(blocked on Wave 2 completion)*

- [x] 08-03-PLAN.md — Refusals before CAD (corner and chamfered corner vs root, measured), the ignored-field warning, API/CLI parity, README and help text (wave 3)

**Wave 4** *(blocked on Wave 3 completion)*

- [x] 08-04-PLAN.md — `make bench.build` and the 16-row sweep at 200 teeth in `bench/RESULTS.md`, L27, round-bore chamfer-reach debt, final `make verify` (wave 4)

### Phase 9: Keyway Bore

**Goal**: A user can cut a keyway into a round or D-flat bore with an explicit,
DIN-6885-convention depth a human can verify with calipers on the printed part.
**Depends on**: Phase 8
**Requirements**: REQ-keyway-bore, REQ-keyway-composes-with-d-flat, REQ-keyway-wall-refused, REQ-hex-rim-chamfer, REQ-bore-derived-numbers
**Success Criteria** (what must be TRUE):

  1. Setting `keyway_width`/`keyway_depth` (mm, 0 = off) cuts a keyway measured radially
     from the as-cut bore wall (`(bore_d + bore_clearance)/2`, 09-CONTEXT.md D-14) — the
     DIN 6885 / ISO R773 `t2` convention, stated in field help, with a warning that ANSI
     B17.1's "T" is a different (diametral gauge) quantity; `bore_clearance` is added to
     the keyway width; `bore_d = 0` with a keyway is a 422 naming both fields; the built
     solid's keyway floor position is measured against the stated datum by a test, not
     just the parameter round-tripping.
  2. A keyway and a D-flat coexist on one bore under this phase's placement rule; a keyway
     that would intersect the flat is a 422 naming both fields. A keyway field together
     with `bore_hex` is a 422 naming the fields (moved here from Phase 8 SC2 by
     08-CONTEXT.md D-01).
  3. A keyway whose floor corner would come within `MIN_WALL` of the root circle is
     refused — 422 naming `keyway_depth` and `keyway_width` — never capped; a face recess
     yields to the keyway corner instead, narrowed or dropped with the existing warnings,
     never a 422 (09-CONTEXT.md D-09/D-10; this supersedes the earlier recess-wall
     refusal).
  4. `bore_chamfer` correctly chamfers all six rim edges of a hex bore on both faces
     (extending Phase 8) and both the arc and the straight rim edges of a keyway bore's
     round part, proven by the exact edge count the rim selector takes before the keyway
     is cut, for every bore shape with and without a keyway, and by a built-solid test
     that the chamfer survives the slot and the keyway's own edges stay sharp
     (09-CONTEXT.md D-05/D-07; on a finished, chamfered solid the rim selector finds no
     edges, so a count taken there is not a proof).
  5. `DerivedDimensions` reports the keyway floor-to-opposite-wall distance and the hex
     corner-to-corner diameter (added in Phase 8), both `null` when their feature is off; a
     new `Lxx` decision-log entry states the keyway depth datum; measured build time at the
     heaviest keyway configuration is recorded in `bench/RESULTS.md` inside
     `SPUR_BUILD_TIMEOUT=30s`; Phase 7's regression fixture still passes.
**Research flag**: No — the depth datum was decided by the human on 2026-09-25 (as-cut
bore wall, DIN 6885 / ISO R773 `t2`; recorded in `REQUIREMENTS.md`, REQ-keyway-bore).
The phase logs it as a new `Lxx` and settles the keyway-vs-D-flat placement rule at
discuss time — a phase decision, not a research question.
**Plans**: 5/5 plans executed

Plans:
**Wave 1**

- [x] 09-01-PLAN.md — D-20 first: amend SC1 (as-cut wall datum), SC3 (recess yields; corner vs root), SC4 (pre-keyway count plus built-solid proof), REQ-keyway-bore and REQ-keyway-wall-refused through the edit-phase tooling, one human confirmation (wave 1)

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 09-02-PLAN.md — Tracer: `?keyway_width=3&keyway_depth=1.4` end to end (fields, slot cut after the chamfer, recess yields to the corner, two derived fields, UI rows), then proof on the built solid: datum, surviving chamfer, sharp slot, pre-keyway rim counts (wave 2)

**Wave 3** *(blocked on Wave 2 completion)*

- [x] 09-03-PLAN.md — Refusals before CAD (hex, no bore, half-set, wider than the bore, into the D-flat, corner vs root) with API/CLI parity; D-12's round chamfer reach refused at the measured contact, debt resolved (wave 3)

**Wave 4** *(blocked on Wave 3 completion)*

- [x] 09-04-PLAN.md — The 32-row keyway sweep at 200 teeth through `make bench.build`, recorded in `bench/RESULTS.md` (wave 4)

**Wave 5** *(blocked on Wave 4 completion)*

- [x] 09-05-PLAN.md — README (bullet, rows, keyed example run as a test, datum/sharp-slot/floor-radius notes), L28, architecture docs, final `make verify` (wave 5)

### Phase 10: Tooth-Tip Chamfer

**Goal**: A user can break the tooth-tip edges for a safer, more printable part, with
flanks, root fillets, bore and outside diameter untouched.
**Depends on**: Phase 7 (independent of the bore work in Phases 8–9)
**Requirements**: REQ-tip-chamfer, REQ-tip-chamfer-capped
**Success Criteria** (what must be TRUE):

  1. Setting `tip_chamfer` (mm, 0 = off) breaks the tooth-tip arc edges at both end faces;
     flanks, root fillets, bore and cutouts are untouched and the outside diameter is
     unchanged.
  2. The chamfer is the end-face edge break decided on 2026-09-25 (a 3D edge operation on
     the tip arcs — `REQUIREMENTS.md`, REQ-tip-chamfer; the 2D profile-corner reading is
     out of scope), recorded as a new `Lxx` with its measured cost; no sizing guidance is
     cited in help text as a sourced standard — the 0.1–0.2×module figure stays an
     unconfirmed candidate, never presented as a convention.
  3. A chamfer larger than the tip land allows is capped and reported in `warnings` (L03).
  4. The chamfer operator's cost at the heaviest allowed configuration (max teeth × max
     chamfer) is measured against `SPUR_BUILD_TIMEOUT=30s` and recorded in
     `bench/RESULTS.md`; if it cannot fit, the cap is lowered and the number published — the
     cost is never hidden.
  5. Phase 7's regression fixture still passes — tip chamfer defaults to off, every
     pre-v0.2 parameter set is unchanged.
**Research flag**: Yes, narrowly — the reading and the sizing question are decided
(end-face edge break; no unsourced guidance), but `Mixin3D.chamfer()` at maximum teeth is
the one v0.2 operator in L09's cost family, so the plan opens with a measured spike of its
cost before the cap is designed.
**Plans**: 5/5 plans complete

Plans:
**Wave 1**

- [x] 10-01-PLAN.md — D-05 spike, measurement only: the chamfer operator on the 2 x teeth tip arcs at 19/40/200 teeth and module 0.2/1.75/10, the kernel boundary bisected against the analytic caps, a 405-set grid, recorded in `bench/RESULTS.md` before any field exists (wave 1)

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 10-02-PLAN.md — Tracer: `?tip_chamfer=0.4` end to end (field, three-limit cap with D-04's measured involute-start term, `tip_chamfer_effective`, the guarded tip selector as the last build step, DIMS row), then the cap pinned one step either side of each limit (wave 2)

**Wave 3** *(blocked on Wave 2 completion)*

- [x] 10-03-PLAN.md — Proof: tip column on every selector-matrix row plus 200-tooth and module-0.2 rows, the real-pipeline spy, the empty-selection guard (model, API, CLI), the built-solid proof and its tripwire, the kernel boundary either side (wave 3)

**Wave 4** *(blocked on Wave 3 completion)*

- [x] 10-04-PLAN.md — The 9-row D-06 sweep at 200 teeth through `make bench.build`, recorded in `bench/RESULTS.md` with the timeout margin; D-07's over-budget gate (wave 4)

**Wave 5** *(blocked on Wave 4 completion)*

- [x] 10-05-PLAN.md — README (bullet, row, example run as a test, geometry note), L29, architecture docs, debt records, final `make verify` (wave 5)

### Phase 11: Body Cutouts

**Goal**: A user can lighten the gear body with exactly one of three explicit cutout
patterns — lightening holes, spoke arms, or a honeycomb web — each composing with any bore
profile and with face recesses.
**Depends on**: Phase 7 (edge-selector/regression foundation); Phases 8–9 exist by this
point so composition with hex and keyway bores can be tested, but the cutout cuts themselves
are independent of bore shape.
**Requirements**: REQ-spoke-cutout, REQ-hole-cutout, REQ-honeycomb-cutout,
REQ-one-cutout-pattern, REQ-cutout-conflicts-refused-early, REQ-cutout-composes,
REQ-cutout-derived-numbers
**Success Criteria** (what must be TRUE):

  1. Setting `hole_count`/`hole_d`/`hole_circle_d` (0 = off) cuts N equal round holes evenly
     spaced on a bolt circle through the full face width, batched in one `.cut(*cutters)`
     call, not a loop.
  2. Setting `spoke_count`/`spoke_width`/`hub_d`/`rim_wall` (0 = off) cuts N straight arms
     between a hub ring and a rim ring, the sectors between them cut through the full face
     width, their corners rounded by `spoke_fillet` (0 = sharp), capped to fit
     (11-CONTEXT.md D-04/D-06/D-21).
  3. Setting `hex_cell`/`hex_wall` (0 = off) cuts a honeycomb web whose cell count is derived
     and reported; a build-time-vs-cell-count sweep runs before any cap formula is written
     (mirroring L17's methodology) and is logged as a new `Lxx`; when the derived count
     exceeds the measured cap, cell size is raised to the smallest size that fits and a
     warning names both the requested and the applied size — cells are never silently
     dropped, and the cap is analytic so the same link yields the same count on every
     machine.
  4. Exactly one of `spoke_count`/`hole_count`/`hex_cell` may be non-zero (422 naming both
     fields otherwise); a cutout that would breach the hub wall, the rim wall, or overlap
     itself is refused in `calc.py` before any CAD work starts — 422 on the API, exit 2 on
     the CLI, the same message naming the fields.
  5. Any cutout composes with face recesses (cuts through the recessed floor, the floor
     fillet intact on the edges that survive — proven by a test that counts the filleted
     edges) and with any bore profile; `DerivedDimensions` reports the thinnest remaining
     wall on the hub side and on the rim side, and the honeycomb cell count actually cut,
     `null` when no cutout is set; measured build time for each pattern at its heaviest
     allowed configuration is recorded in `bench/RESULTS.md` inside
     `SPUR_BUILD_TIMEOUT=30s`; Phase 7's regression fixture still passes.
**Research flag**: Yes, for the honeycomb sub-phase specifically — the cell-count-vs-
build-time relationship needs a dedicated benchmark sweep before any cap formula is written
(`research/SUMMARY.md` "Research Flags"). Holes and spoke arms are well-documented patterns
(`polarArray`/`cut(*cutters)`, generalizing `_cut_face_recesses`'s existing two-call
pattern) — no research flag needed for those sub-parts.
**Plans**: 9/9 plans complete

Plans:
**Wave 1**

- [x] 11-01-PLAN.md — D-21 first: amend REQ-spoke-cutout and SC2 for `spoke_fillet` through the edit-phase tooling, one human confirmation (plus the spoke-arm wall rule) (wave 1)

**Wave 2** *(blocked on Wave 1 completion)*

- [x] 11-02-PLAN.md — D-24 spike, measurement only: whole-cell count vs build/export time at 200 teeth, module 10, both recesses; the cut spelling; the measured `HEX_CELL_CAP` and its module-1.75 confirmation in `bench/RESULTS.md` (wave 2)

**Wave 3** *(blocked on Wave 2 completion)*

- [x] 11-03-PLAN.md — Tracer: `?hole_count=6&hole_d=4&hole_circle_d=20` end to end (Holes group, `_cut_body` in one cut call, the two thinnest-wall numbers), then the hole refusals one step either side (wave 3)

**Wave 4** *(blocked on Wave 3 completion)*

- [x] 11-04-PLAN.md — Spokes: five fields, sector cutters with analytic corner arcs, the fillet cap, the spoke refusals and the one-pattern rule (wave 4)

**Wave 5** *(blocked on Wave 4 completion)*

- [x] 11-05-PLAN.md — Honeycomb: whole-cell lattice and raise-to-fit moved from the spike, the measured cap, count and size in the response, exact walls, the honeycomb refusals, derive()'s cost measured (wave 5)

**Wave 6** *(blocked on Wave 5 completion)*

- [x] 11-06-PLAN.md — The three per-pattern sweeps at 200 teeth through `make bench.build`, recorded; D-18's over-budget gate (predicted to fire) and the chosen limit applied and re-measured (wave 6)

**Wave 7** *(blocked on Wave 6 completion)*

- [x] 11-07-PLAN.md — Proof: every selector in the real pipeline with each cutout on each bore shape; the kernel either side of every wall rule; tangent cutters with no fuzzy boolean; the fillet cap on extreme sectors (wave 7)

**Wave 8** *(blocked on Wave 7 completion)*

- [x] 11-08-PLAN.md — Proof: each cutout read back off the built solid against the printed numbers, the recess fillet counted on every pattern and bore, both tripwires (wave 8)

**Wave 9** *(blocked on Wave 8 completion)*

- [x] 11-09-PLAN.md — README (bullet, ten rows, examples run as tests, geometry note), L30, architecture docs, three ideas filed, final `make verify` measured (wave 9)

### Phase 12: Composition Pass

**Goal**: Every v0.2 feature composes correctly across the full matrix, the milestone's
heaviest-configuration build time is measured, and all three interfaces stay in parity —
closing out v0.2.
**Depends on**: Phases 8, 9, 10, 11
**Requirements**: REQ-measured-build-time, REQ-three-interfaces-extended
**Success Criteria** (what must be TRUE):

  1. The full composition test matrix passes: recess × each bore shape, recess × each
     cutout pattern (cut through the recessed floor), each cutout pattern × each bore
     shape, and every refusal decided earlier — keyway × hex (Phase 9), two cutout patterns
     on one part (Phase 11, REQ-one-cutout-pattern) — is exercised across the matrix with
     the 422 naming the fields.
  2. Every new v0.2 parameter is on the web form (in its own group), the API query and the
     CLI flags from the one `GearParams` model, round-trips through the shareable URL, and
     appears in `/api/schema`; `spur info`/`spur export` print the same numbers and errors
     as the API for every new feature.
  3. `bench/RESULTS.md` records build time, plus fine-quality STL and STEP export time
     inside the admission slot, for the heaviest combined configuration (recess + hex
     pattern, per the milestone's Success Metric 2) and for each individual feature, all
     inside `SPUR_BUILD_TIMEOUT=30s`.
  4. L19's gzip-level table and L24's mesh-copy timing are re-measured against the heaviest
     v0.2 face topology, not assumed to still hold from v0.1's topology (Pitfall 8).
  5. Phase 7's regression fixture passes one final time across the whole matrix — every
     pre-v0.2 parameter set still yields identical `DerivedDimensions` and an identical
     export after all of v0.2.
**Research flag**: No — this phase measures and integrates against decisions already locked
in Phases 7–11; no open technical questions remain by this point.
**Plans**: 9 plans

Plans:
**Wave 1**

- [ ] 12-01-PLAN.md — D-06 first: amend SC3 (the composed sweep) and SC5 (the fixture's real contract) through the edit-phase tooling, one human confirmation (plus the "seven groups" and "where L19's row lands" questions) (wave 1)

**Wave 2** *(blocked on Wave 1 completion)*

- [ ] 12-02-PLAN.md — Tracer: fine-STL bytes and triangles per sweep row (D-16); the 18-row composed sweep and its pin; the sweep run one gear at a time on a quiet host and recorded (wave 2)

**Wave 3** *(blocked on Wave 2 completion)*

- [ ] 12-03-PLAN.md — D-03's gate on the decisive composed rows (probe, human decision, apply and re-run); the two build-timeout debts resolved and the concurrent question re-homed (wave 3)

**Wave 4** *(blocked on Wave 3 completion)*

- [ ] 12-04-PLAN.md — `bench/export_cost.py` and `make bench.export`: L19's gzip table and L24's copy cost re-measured on the largest composed fine STL, L19's rule applied (wave 4)

**Wave 5** *(blocked on Wave 4 completion)*

- [ ] 12-05-PLAN.md — Calc matrix: 96 bore x cutout x recess x tip rows, and every locked refusal with each other family on (138 rows) (wave 5)

**Wave 6** *(blocked on Wave 5 completion)*

- [ ] 12-06-PLAN.md — Kernel rows: the tip chamfer with each cutout on each bore, and a single-sided recess with each cutout, through the features' own proof helpers (wave 6)

**Wave 7** *(blocked on Wave 6 completion)*

- [ ] 12-07-PLAN.md — Parity: the composed README link byte for byte on CLI and API, the model-field walk, the static URL round trip, every refusal on 422 and exit 2 (wave 7)

**Wave 8** *(blocked on Wave 7 completion)*

- [ ] 12-08-PLAN.md — The CLI's real exit contract in cli.md, pinned by tests, its debt resolved; the UI pass's "not taken" verdict on both form ideas (wave 8)

**Wave 9** *(blocked on Wave 8 completion)*

- [ ] 12-09-PLAN.md — D-10's measured gate cost against the phase start and its checkpoint, the final fixture pass, L31 (wave 9)

**UI hint**: yes

## Process Notes (v0.2)

- Phases run on `gsd/phase-NN-*` branches cut from `origin/main` and land only through
  `make pr.land PR=N` (L22/L25); `.planning/` rides the same PR as the code, never a
  separate planning-only commit.
- `make verify` (ruff, mypy `--strict`, import-linter, unfinished-work scan, pytest) is the
  gate for every phase, no exceptions (L13).
- Every phase that adds a decision logs it as a new `Lxx` in
  `docs/architecture/decision_log.md` — at minimum Phase 9 (keyway depth datum), Phase 10
  (tip-chamfer implementation reading), and Phase 11 (honeycomb build-time-cap methodology).
- New parameters default to off (L05); Phase 7's regression fixture is the standing proof,
  re-run and extended by every later phase, not re-derived per phase.

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|-----------------|--------|-----------|
| 1–6 | v0.1 | 21/21 | Complete | 2026-09-25 |
| 7. Foundation | v0.2 | 2/2 | In Progress|  |
| 8. Hex Bore | v0.2 | 4/4 | In Progress|  |
| 9. Keyway Bore | v0.2 | 5/5 | In Progress|  |
| 10. Tooth-Tip Chamfer | v0.2 | 5/5 | In Progress|  |
| 11. Body Cutouts | v0.2 | 9/9 | In Progress|  |
| 12. Composition Pass | v0.2 | 0/? | Not started | - |
