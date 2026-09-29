---
gsd_state_version: "1.0"
milestone: v0.2
milestone_name: Fit to Shaft
current_phase: 11
current_phase_name: Body Cutouts
status: verifying
stopped_at: Completed 11-09-PLAN.md
last_updated: "2026-09-29T10:41:15.514Z"
last_activity: 2026-09-29
last_activity_desc: Phase 11 execution started
state_head: 847af3f0a06caa6934f703c9b4f55783148f3f54
progress:
  total_phases: 6
  completed_phases: 1
  total_plans: 25
  completed_plans: 25
  percent: 17
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-09-28)

**Core value:** A number this tool prints is a number someone will cut metal to — every
dimension is computed honestly or reported as a warning, never guessed (L08).
**Current focus:** Phase 11 — Body Cutouts

## Current Position

Phase: 11 (Body Cutouts) — EXECUTING
Plan: 9 of 9
Status: Phase complete — ready for verification
Last activity: 2026-09-29 — Phase 11 execution started

## Performance Metrics

**Velocity:**

- Total plans completed via GSD: 37 (Phase 2: 5, Phase 3: 3, Phase 4: 3, Phase 5: 6, Phase 6: 4, Phase 7: 2, Phase 8: 4, Phase 9: 5, Phase 10: 5; v0 was built and verified
  directly against `make verify`, before this planning structure existed)
- Average duration: N/A
- Total execution time: N/A

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1. v0 Baseline | N/A | N/A | N/A |
| 2. CAD Off the Event Loop | 5 | ~3h50m | ~46min |
| 3. Structured Logging | 3 | ~1h12m | ~24min |
| 4. Typed Derived-Dimensions Contract | 3 | ~1h10m | ~23min |
| 5. CI Observed Green | 6 | ~1h38m | ~16min |
| 6. Address tech debt: merge gate + solid cache | 4 | ~56min | ~14min |
| 7. Foundation — edge selection + regression fixture | 2 | ~50min | ~25min |
| 8. Hex Bore | 4 | ~2h49m | ~42min |
| 07 | 2 | - | - |
| 9. Keyway Bore | 5 | ~2h10m | ~26min |
| 10. Tooth-Tip Chamfer | 5 | ~2h08m | ~26min |
| 10 | 5 | - | - |

**Recent Trend:** Phase 2's five plans took ~3h50m of executor time; 02-04 (~2h)
dominated because it waited on real benchmark runs, not on code. Phase 3's three plans
took ~1h12m; the post-review fix pass (CR-01/WR-01/WR-02, three commits) added ~10 min.
Phase 4's three plans took ~1h10m: 04-01 (~45 min — reconstructed, not measured) carried
the model and the three contract tests; 04-02 and 04-03 were 16 and 9 measured minutes.
Code review came back clean (1 info) and verification passed 4/4 with no fix pass.
Phase 5's six plans took ~1h38m: 05-02 (~35 min, the live `make pr.land` tracer) dominated;
the rest were 11–14 min each. Code review found CR-01 (pr.land's cut-line bypass) and
verification scored 4/5; gap-closure plan 05-06 (13 min) closed it, the re-review was clean
and re-verification passed 5/5.
Phase 6's four plans took ~56m: 06-01 (~20 min, estimated from commit timestamps — start time
was not captured) and 06-04 (17 min, the three-report tracer with a live `gh` read) dominated;
06-02 and 06-03 were 9 and 10 measured minutes. Code review came back clean (2 info),
verification passed 9/9, security 13/13 closed, Nyquist 11/11 green — no fix pass, no gap plan.
Phase 7's two plans took ~50m: 07-01 (39 min, spanning a D-06 decision checkpoint — the fixture's
16.27 s `make verify` cost crossed the 15.0 s line and the human accepted it) and 07-02 (11 min of
committed work; ~22 min wall including the tolerance probe and two benchmark runs). Verification
passed 4/4; `make verify` 289 tests; code review pending at transition time.
Phase 9's five plans took ~2h10m: 09-03 (~45 min — six refusal rules plus the D-12 boundary
re-measured by 20-step bisection on 12 configurations) dominated; 09-02 (27 min, the tracer plus the
kernel proofs) next; 09-01 (14 min, spanning the human-verify checkpoint on the amendment wording),
09-04 (~23 min, 32 sweep rows all inside 30 s on the first run) and 09-05 (~21 min) were routine.
Verification passed 12/12; `make verify` 396 tests; the two Rule-3 deviations were lint/type-only;
code review pending at transition time.
Phase 10's five plans took ~2h08m: 10-01 (~52 min — the measured spike: six 20-step bisections
and a 405-set grid, no code under `src/`) dominated; 10-02 (24 min, the tracer plus the cap
tests), 10-03 (19 min, proofs only), 10-04 (17 min, nine sweep rows all inside 30 s on the
first run) and 10-05 (16 min) were routine. Verification passed 5/5; `make verify` 453 tests,
wall time 81.6 s → 101.4 s across the phase; code review 0 critical / 1 warning (WR-01, open)
/ 2 info; four executor deviations, all lint- or wording-only.
**Per-Plan Metrics:**

| Plan | Duration | Tasks | Files |
|------|----------|-------|-------|
| Phase 02 P01 | 30min | 3 tasks | 8 files |
| Phase 02 P02 | 19min | 3 tasks | 6 files |
| Phase 02 P03 | ~25min | 4 tasks | 4 files |
| Phase 02 P04 | ~2h | 3 tasks | 9 files |
| Phase 02 P05 | 35min | 3 tasks | 5 files |
| Phase 03 P01 | 25min | 3 tasks | 8 files |
| Phase 03 P02 | 27min | 3 tasks | 5 files |
| Phase 03 P03 | 20min | 3 tasks | 9 files |
| Phase 04 P01 | ~45min | 3 tasks | 11 files |
| Phase 04 P02 | 16min | 3 tasks | 9 files |
| Phase 04 P03 | 9min | 3 tasks | 7 files |
| Phase 05 P01 | 12 min | 2 tasks | 8 files |
| Phase 05 P02 | ~35min | 2 tasks | 5 files |
| Phase 05 P03 | ~13min | 3 tasks | 3 files |
| Phase 05 P04 | 14 min | 3 tasks | 10 files |
| Phase 05 P05 | ~11min | 3 tasks | 13 files |
| Phase 05 P06 | 13min | 2 tasks | 5 files |
| Phase 06 P01 | ~20min | 2 tasks | 6 files |
| Phase 06 P02 | 9min | 2 tasks | 6 files |
| Phase 06 P03 | 10min | 3 tasks | 6 files |
| Phase 06 P04 | 17min | 3 tasks | 7 files |
| Phase 07 P01 | 39min | 3 tasks | 8 files |
| Phase 07 P02 | 11min | 3 tasks | 7 files |
| Phase 08 P01 | ~19min | 3 tasks | 3 files |
| Phase 08 P02 | 55min | 2 tasks | 8 files |
| Phase 08 P03 | 25min | 2 tasks | 7 files |
| Phase 08 P04 | 70min | 3 tasks | 11 files |
| Phase 08 P01 | 15 min | 3 tasks | 3 files |
| Phase 08 P02 | 55min | 2 tasks | 8 files |
| Phase 08 P03 | 25 min | 2 tasks | 7 files |
| Phase 08 P04 | 70 min | 3 tasks | 11 files |
| Phase 09 P01 | 14min | 3 tasks | 3 files |
| Phase 09 P02 | 27min | 2 tasks | 7 files |
| Phase 09 P03 | ~45min | 2 tasks | 8 files |
| Phase 09 P04 | ~23min | 2 tasks | 3 files |
| Phase 09 P05 | ~21min | 2 tasks | 5 files |
| Phase 09 P01 | 14min | 3 tasks | 3 files |
| Phase 09 P02 | 27min | 2 tasks | 7 files |
| Phase 09 P03 | 45min | 2 tasks | 7 files |
| Phase 09 P04 | 23min | 2 tasks | 3 files |
| Phase 09 P05 | ~21min | 2 tasks | 5 files |
| Phase 10 P01 | ~52min | 2 tasks | 2 files |
| Phase 10 P02 | ~24min | 2 tasks | 9 files |
| Phase 10 P03 | ~19min | 2 tasks | 3 files |
| Phase 10 P04 | ~17min | 2 tasks | 5 files |
| Phase 10 P05 | ~16min | 3 tasks | 8 files |
| Phase 10 P01 | 52min | 2 tasks | 2 files |
| Phase 10 P02 | ~24min | 2 tasks | 9 files |
| Phase 10 P03 | 19min | 2 tasks | 3 files |
| Phase 10 P04 | ~17min | 2 tasks | 5 files |
| Phase 10 P05 | 16min | 3 tasks | 8 files |
| Phase 11 P01 | ~15min | 3 tasks | 3 files |
| Phase 11 P02 | ~35min | 2 tasks | 2 files |
| Phase 11 P03 | ~55min | 2 tasks | 8 files |
| Phase 11 P04 | 37min | 2 tasks | 8 files |
| Phase 11-body-cutouts P05 | 50min | 2 tasks | 9 files |
| Phase 11 P06 | 45min (Task 3; Task 1 prior executor) | 3 tasks | 10 files |
| Phase 11 P07 | ~28min | 2 tasks | 2 files |
| Phase 11 P08 | ~35min | 2 tasks | 1 files |
| Phase 11 P09 | ~31min | 3 tasks | 10 files |

## Accumulated Context

### Decisions

Full decision log: PROJECT.md "Key Decisions" table (L01–L25, from
`docs/architecture/decision_log.md`). Flagged for revisit there: L10 (radial root
fillet — trochoidal is a tracked idea) and L18 (ten-concurrent latency bar accepted with
caveat). L14 was superseded by L21 in Phase 4 — the ratchet is on, not deferred again. L24 (a cached
solid never carries a mesh) and L25 (the merge gate reads the whole message and the run's own
verdict, amending L22) were appended in Phase 6. L26 (the pre-v0.2 fixture as the standing
L05 proof; a selector never silently selects nothing) was appended in Phase 7. L27 (a hex bore replaces the whole round profile; its limits are the chamfered corner's against the root circle, measured; the replay requires post-fixture fields null) was appended in Phase 8.

v0.1's roadmap-time and per-phase decisions (Phases 2–6) are archived with the milestone:
`milestones/v0.1-ROADMAP.md`, the `key-decisions` blocks of
`milestones/v0.1-phases/*/*-SUMMARY.md`, and decision-log entries L17–L25. Nothing here is
pending; the next milestone starts this list fresh.

- [Phase 07]: D-06 gate: measured make verify delta with the regression fixture was 16.27s, above the plan's 15.0s line. Human chose Option A: accept the cost, keep all 44 records built. — 16.27s is under the planner's ~20s ceiling; the cost is spread evenly across all 39 builds (no single outlier); Success Metric 3 stays literal rather than trimmed to a curated subset.
- [Phase 07]: L26 logged: the pre-v0.2 fixture (07-01) and the two edge-selector guards (07-02) as one standing rule -- a selector never silently selects nothing. — 07-CONTEXT.md's Claude's Discretion recommended one entry covering D-03 and D-15..D-18; follows L24/L25's paragraph shape.
- [Phase 08]: Human approved all four proposed texts (REQUIREMENTS REQ-hex-bore, REQ-keyway-bore; ROADMAP Phase 8 SC2, Phase 9 SC2 + Phase 12 SC1) verbatim at the Task 2 checkpoint, no wording changes. — ROADMAP.md was written only through edit-phase's write_updated_phase step (scoped Edit per phase section, milestone-scope check before/after), never a direct whole-file write, per D-01.
- [Phase 08]: recess_radii()'s hub clearance is measured from bore_mouth_limit(p) (the chamfered mouth), not bore_radius(p) + chamfer -- a hex's chamfer reaches its corner at 2c/sqrt(3), not c, and the old formula would have driven a 3 mm chamfer on a 6 mm hex into an invalid solid (research PITFALLS.md Pitfall 1); round and D-flat compute identical floats in identical order, so the fixture stayed byte-unchanged.
- [Phase 08]: The replay's comparison, not the fixture, absorbed the two new DerivedDimensions fields: recorded fields still compare exactly, every field added since the capture must read null (REQ-derived-dimensions-additive).
- [Phase 08]: The hex is a replacement branch in model._cut_bore, never an intersection with the round profile (D-01) -- bore_d/bore_flat stay live in the schema and are simply ignored when bore_hex > 0; the ignored-field warning is 08-03's task.
- [Phase 08]: D-03's chamfer bound sits on the root circle (bore_mouth_limit vs pr.rf - MIN_WALL), not the hex's side length -- the planning probe found the kernel copes with chamfer-vs-side at every allowed size (ratio 8, rel 1e-6 volume match), so no side rule was added and the probe became a test instead (Flagged Assumption A4).
- [Phase 08]: The corner rule and the chamfered-corner rule never stack (if/elif, not two independent ifs) -- with bore_chamfer 0 the mouth equals the corner, so exactly one hex refusal can fire (Flagged Assumption A5).
- [Phase 08]: L27 appended: hex bore field, replaces-never-refuses, derived numbers, D-03's measured root-circle bounds, and D-11's heaviest row (5.08s of 30s) -- decision_log.md stayed append-only. — One entry covering the whole phase, following L26's shape; the sweep never approached the 30s budget so no checkpoint:decision fired.
- [Phase 08]: The round bore's unchecked chamfer-reach gap was filed as must-severity debt, not fixed -- a fix would refuse round links that build today (L05). — Measured on 19 and 40 teeth at chamfers of 0.4, 1 and 2mm; out of Phase 8's scope (the hex got its own matching rule).
- [Phase 09]: Human approved all four proposed texts (REQUIREMENTS REQ-keyway-bore, REQ-keyway-wall-refused; ROADMAP Phase 9 Requirements line, SC1, SC3, SC4) verbatim at the Task 2 checkpoint, no wording changes. — ROADMAP.md was written only through edit-phase's write_updated_phase step (scoped Edit of the Phase 9 section, milestone-scope check before/after), never a direct whole-file write, per D-20.
- [Phase 09]: D-14's datum verified on the built solid; D-09's yield measured (recess narrows/drops, never a 422); D-07's amended proof (pre-keyway matrix + built-solid chamfer/sharp-slot); D-05 proven sharp on the finished solid.
- [Phase 09]: D-12 re-measured 2026-09-27 on the pinned kernel (not carried over unverified): a 20-step bisection over 12 configurations landed identically everywhere -- last failing gap -3.8e-8 mm, first building gap 1.9e-8 mm, gap 0.0 failing on all 12, teeth-independent unlike the hex corner (L27). ROOT_CONTACT = 1e-9 mm. One configuration failed to build at exactly 1e-9 mm despite check() accepting it there -- a sub-2e-8 mm residual band matching 09-RESEARCH.md's Flagged Assumption A1, unreachable by any settable field value; documented in the resolved debt file rather than treated as a fresh gate trigger.
- [Phase 09]: D-11's bound (keyway_width >= bore_d) is definitional, not kernel-measured -- re-confirmed the kernel never fails as keyway_width approaches bore_d, so no crash boundary exists to search for.
- [Phase 09]: 09-04's keyway sweep measured all 32 rows inside SPUR_BUILD_TIMEOUT=30s on the first run (heaviest 4.85s of 30s) -- the 08 D-11 gate never fired. — The heaviest row is a 3 x 1.4 mm keyway that keeps its face recess, not the largest keyway the rules allow, which pushes the recess out and builds in about half the time -- confirming the planning probe that the sweep must measure both keyway sizes to find the heaviest configuration.
- [Phase 09]: L28 appended after L27 (0 deleted lines): the keyway's fields, datum formula, build order, recess yield, every refusal, D-12's fix, the two derived numbers and the sweep's heaviest row (4.85s of 30s), each cited to its SUMMARY sha or measurement.
- [Phase 10]: The tip chamfer's cap is the smallest of three limits and the third is measured, not assumed: 10-01's spike found the kernel failing inside the two analytic caps wherever the root fillet's lead-in reaches above the pitch circle, and `ra - spline_start` predicted the boundary within ~2 µm on five of six configurations (the sixth conservative by 0.04 mm, never optimistic); the tests pin one step either side (2.937 mm builds, 2.9875 mm fails).
- [Phase 10]: `_chamfer_tips` runs last in `_build`, after `_cut_keyway`, and `_tip_edges` requires both endpoints on an end face — a radius-only test would re-select the moved arcs on a re-chamfer (D-03, D-13); the D-12 proof pins +38 CONE faces / +114 edges / −22.7557 mm³ and goes red when the step is skipped.
- [Phase 10]: 10-04's sweep measured all 9 rows inside `SPUR_BUILD_TIMEOUT=30s` on the first run (heaviest 14.87 s: 200 teeth × 1.75 mm chamfer with both recesses) — the D-07 over-budget checkpoint never fired, but 14.87 s crosses the quarter-of-timeout trigger, so the narrowed margin is filed as must-debt rather than hidden.
- [Phase 10]: L29 appended after L28 (0 deleted lines) and names no chamfer size: the research-era sizing figure has no source and appears nowhere in help text, README or docs (ROADMAP SC2); 10-05's first draft quoted it to reject it and tripped the plan's own grep — reworded to cite the research source without the number.
- [Phase 10]: The tip-arc selector tests both endpoints' z against {0, face_width} to distinguish original tip arcs from moved ones after a chamfer -- confirmed at 200 teeth and module 0.2/10, not just 19 teeth.
- [Phase 10]: pred = ra - spline_start is the measured D-04 kernel boundary, teeth-independent where compared (19/40 teeth agree to ~2 microns); one flagged set (module 1, x 1.0) is conservative by 0.04mm.
- [Phase 10]: Chamfer cost is dominated by edge count (38/80/400 edges), not c or module -- a lower tip_chamfer le would not reduce the heaviest 200-tooth row's cost; D-07's over-budget checkpoint never fires (heaviest 15.90s of 30s).
- [Phase 10]: 17 of 163 grid sets where pred sits inside the analytic cap also built at the (larger) analytic cap -- the pred-based rule is conservative, trims some buildable chamfers, never a 422.
- [Phase 10]: 10-02: tip_chamfer_limit(p) returns a 3-way min() over (limit, reason) tuples rather than three ifs, so an exact tie between two limits breaks on the reason text deterministically with no extra branching. — Continues root_fillet's/recess_fillet's cap-function shape; avoids writing and testing a fourth branch for the tie case.
- [Phase 10]: 10-02: model._chamfer_tips assigns the chamfer() result to the solid variable before returning it, matching _cut_bore's shape, instead of returning the call directly. — Mixin3D.chamfer's return type is untyped (Any); mypy's no-any-return check fires on a bare return of the chamfer call but not when the same expression is assigned to a cq.Shape-typed variable first.
- [Phase 10]: 10-03: the built-solid proof and its tripwire share one helper (_assert_only_the_tip_arcs_were_chamfered) so both use the same face/edge/volume/bounding-box/selector checks -- Phase 7's tripwire precedent, a third instance.
- [Phase 10]: 10-03: the kernel-boundary test patches spur.model.tip_chamfer_effective directly (2.9875) rather than the tip_chamfer field, because the field's own cap would clamp any settable value back inside the boundary before it reached the kernel.
- [Phase 10]: 10-04: the tooth-tip chamfer's heaviest 200-tooth row (14.87s of 30s) was filed as must-debt, since it crosses the 7.5s quarter-of-timeout trigger the SPUR_BUILD_TIMEOUT default's own 4x rationale set.
- [Phase 10]: 10-04: D-07's over-budget checkpoint never fired -- all 9 tip-chamfer sweep rows built inside 30s on the first run, heaviest 14.87s, so no human decision was needed on the field's le or a teeth-dependent cap.
- [Phase 10]: 10-05: The root fillet's straight lead-in issue is filed as must-debt, not fixed -- correcting it means either an outline change with its own Lxx and fixture regeneration, or a README correction, both outside this phase's feature (CLAUDE.md 'note the tangent').
- [Phase 10]: 10-05: L29 appended after L28 (0 deleted lines): the field, cut, three-limit cap with D-04's measured boundary, derived field/warning, spike/sweep cost, proof and reversibility, each cited to a SUMMARY sha or bench/RESULTS.md, none re-estimated.
- [Phase 11]: Human approved REQ-spoke-cutout's amended wording and the proposed Phase 11 SC2 wording exactly as drafted, no changes.
- [Phase 11]: Human kept the spoke-arm wall rule (Flagged Assumption A1): 0 < spoke_width < MIN_WALL is refused with a 422 naming spoke_width, like every other wall in the part. 11-04 implements this on the human's word.
- [Phase 11]: HEX_CELL_CAP measured at 120 cells (7.15s of 7.5s budget, next row 150 cells at 7.95s over) -- 11-02's honeycomb spike, verdict held on the first run
- [Phase 11]: Cut spelling measured: star (cut(*prisms)) -- all three spellings read within 0.03s at the cap's cell count, none cleared D-24's 10% bar
- [Phase 11]: 11-03: three independent hole rules (hub, rim, neighbour, D-16/D-17) via _under_min_wall(round(wall,6) < MIN_WALL), so a wall sized exactly to MIN_WALL is accepted despite step-aligned float residue (measured 0.39999999999999947 at the tracer's hub boundary); a hole wider than the web trips both wall sentences at once.
- [Phase 11]: 11-03: Task 2's RED and GREEN landed in one feat commit, not separate test(...)/feat(...) commits -- workflow.tdd_mode is not enabled in config.json, so the mechanical RED/GREEN/REFACTOR commit-pattern gate does not apply (Phase 8 precedent, 08-03-SUMMARY.md); RED was still run and confirmed failing before GREEN was written.
- [Phase 11]: The arm rule (11-01's human ruling): 0 < spoke_width < MIN_WALL is refused naming spoke_width, like every other wall in the part.
- [Phase 11]: The hub-ring opening between adjacent bar feet is measured as an arc, following keyway_flat_wall's arc precedent (research Pitfall 4), not a chord.
- [Phase 11]: _fillet_corner's rim-side mirror (inside=True, D-05) was hand-checked against a 3-4-5-style tangent case before trusting it at every sector corner; the built tracer's face/edge deltas match the planning probe exactly.
- [Phase 11]: 11-04: RED and GREEN for both tasks landed in one feat commit each -- workflow.tdd_mode is not enabled, so the mechanical RED/GREEN/REFACTOR commit-pattern gate does not apply (11-03's precedent).
- [Phase 11]: 11-05: HEX_CELL_CAP = 120 cells written from bench/RESULTS.md's measured Cap line and nowhere else (D-12, D-24); the tracer (?hex_cell=3&hex_wall=1) cuts 18 whole cells, walls 1.525/2.149 mm, reproduced exactly. — Whole-cell lattice and raise-to-fit moved from bench/honeycomb_spike.py into spur.calc unchanged, so there is one definition (L08); the spike imports them back.
- [Phase 11]: 11-05: cutout_walls' honeycomb branch reads the exact nearest-edge/farthest-vertex reach on the cut cells, not the whole-cell test's conservative circumradius -- the naive bound would have under-reported the tracer's hub wall by 0.232 mm (Flagged Assumption A3). — A cell's flat can face the axis and be closer than any corner; the circumradius used for containment is deliberately conservative, not the true wall (L08).
- [Phase 11]: 11-05: 11-05's own verify script's len(warnings)==1 assertion at teeth=200 fails as literally written -- the pre-existing root-fillet cap (present without any honeycomb field) also warns there, unrelated to this phase; documented as an Issue Encountered, nothing fixed in code. — Root-fillet capping at 200 teeth predates this phase and is correct; only the plan's own verify-script assumption of exactly one warning at that input was wrong.
- [Phase 11]: [Phase 11] D-18's gate fired: 200-count hole/spoke rows crossing a recess groove measured 41.85s and 65.70-68.70s of SPUR_BUILD_TIMEOUT=30s; the honeycomb cap row measured 8.65s against D-11's 7.5s share. Human accepted the recommendation: hole_count le 200->60, spoke_count le 200->40, HEX_CELL_CAP unchanged at 120 (the honeycomb over-share row accepted as measured). Re-run confirmed every row of both sweeps inside 30s at the new le (heaviest 11.79s holes, 18.52s spokes). — The recess-crossing cost is geometric and near-linear (~0.33s/sector, ~0.21s/hole on the worst rows, loaded host); 200 arms at 0.4mm is not a part anyone cuts; 40 spokes and 60 holes each stack on Phase 12's 14.87s tip-chamfer row with margin under the same load; a count-rule would reintroduce the field-dependent limit D-07/D-12 avoided for configurations nobody needs.
- [Phase 11]: [Phase 11] 11-06: the re-run's arithmetic total (heaviest spoke row 18.52s + Phase 10's 14.87s tip-chamfer row = 33.39s) crosses 30s under this run's exceptional host load (32.17) -- filed as must-severity debt rather than rounded to match the decision's ~2s margin expectation. — Task 3's own scope is the le, not a new build-time guarantee on an arithmetic sum Phase 12 measures for real; the reading is plausibly load-inflated but recorded honestly per L08, not silently accepted.
- [Phase 11]: 11-07: the real-pipeline spy reads the same rim/floor Counter values the no-cutout matrix already established, because both selectors run on the solid before their own operator applies, strictly before _cut_body -- verified against all 19 rows before writing the test.
- [Phase 11]: 11-07: every one-step-past cutout-rule row reuses test_calc.py's own refusal boundary exactly (spoke opening past-the-rule is spoke_width 2.72, not the plan's provisional 2.77) -- the shipped test_calc.py value is the ground truth, not the planning-time estimate.
- [Phase 11]: 11-07: no tol= was needed -- all ten tangent-cutter rows (holes, spoke hub/rim arcs sharp and filleted, a recess-less double-MIN_WALL spoke web, a honeycomb flat tangent to the recess wall) built one valid solid with the plain cut(*cutters) on the pinned kernel, so _cut_body ships none, only a comment recording the measurement.
- [Phase 11]: 11-08: sharp-spoke and honeycomb removed-volume checked against a closed-form analytic formula (matches the kernel to 1e-9 mm3), not a pinned literal; the filleted-spoke row has no closed form and stays pinned.
- [Phase 11]: 11-08: the keyed-round SPOKES13 fillet-1 recess-survival row (not probed in planning) measured TORUS 12 on the pinned kernel; every other row of the 13-row survival matrix matched the planning probe exactly, no sharp floor-to-wall circle survived any row.
- [Phase 11]: 11-09: L30 appended after L29 (0 deleted lines) in L29's paragraph shape -- fields, cut, honeycomb, cap, refusals, numbers, cost, proof and reversibility -- every number cited to a SUMMARY sha or bench/RESULTS.md section, none re-estimated (D-25).
- [Phase 11]: 11-09: make verify's wall time at the phase's end measured 621 passed in 177.62s -- 178.55s wall (host load 3.07-4.65), against Phase 10's 453 passed / 98.17s; the phase's 168 new tests add +80.38s to the gate.
- [Phase 11]: 11-09: three deferred ideas filed under docs/ideas/ with INDEX rows -- a spoke/hole rotation field, a teeth/module-dependent honeycomb cap, and conditional form fields -- verbatim from 11-CONTEXT.md's Deferred Ideas section.

### Pending Todos

None yet.

### Blockers/Concerns

- ℹ️ [Phase 10] Code review WR-01 (a nonzero `tip_chamfer` under 0.0005 mm was silently
  discarded) and CR-01 (its first fix attributed print-precision rounding to a geometric
  limit — found by the Codex lane, confirmed internally) are both fixed: `54fe020`,
  `60d02f7`. A request that rounds to nothing now warns with its true cause; sub-µm
  rounding of a nonzero request stays silent like every other 3-dp field (human decision
  2026-09-28). IN-01/IN-02 stay open (info) in `10-REVIEW-DISPOSITION.md`.
- ⚠️ [Phase 10] The tip chamfer's heaviest row (14.87 s) leaves ~2× of the 30 s
  `SPUR_BUILD_TIMEOUT` where the default was sized against ~4×; Phase 12 re-measures every
  feature combined. `docs/tech_debt/active/2026-09-28-tip-chamfer-narrows-the-build-timeout-margin.md` (must).
- ⚠️ [Phase 10] The root fillet's straight lead-in can reach above the pitch circle
  (pre-existing, exposed by 10-01's probe):
  `docs/tech_debt/active/2026-09-28-root-lead-in-can-reach-above-the-pitch-circle.md` (must).
- ⚠️ [Phase 10] `gsd_run query commit`'s 30 s timeout killed the `make verify` hook (~100 s
  warm at 453 tests) twice more this session — the phase-complete and the review-disposition
  commits — each recovered by a plain `git commit` with hooks after re-applying pre-commit's
  stash of `state.json`. The Phase 9 item below stands; a warm-up run no longer helps.
- ⚠️ [Phase 9] `gsd_run query commit`'s hard-coded 30 s timeout cannot complete this repo's
  `make verify` pre-commit hook, now ~78 s warm (396 tests): 09-04 and 09-05 each hit it and fell
  back to plain `git commit` with hooks running (never `--no-verify`). The filed must-debt
  `docs/tech_debt/active/2026-09-25-gsd-commit-timeout-kills-cold-verify-hook.md` now fires on a
  warm run too, not only cold — its trigger has widened.
- ℹ️ [Phase 9] The Phase 8 round-bore chamfer-reach gap is closed (09-03, `4b6a5b9`): the rule sits
  at the kernel's measured contact (`ROOT_CONTACT` 1e-9 mm) and refuses no link the pinned kernel
  built before. One residual float band (last failing gap −3.8e-8 mm, first building +1.9e-8 mm)
  is unreachable from any settable field value; recorded in the resolved debt file.
- ⚠️ [Phase 7] CI resolves `cadquery`/`cadquery-ocp` from an unpinned `pyproject.toml`
  range while `tests/regression/pre_v0_2.json` pins one resolved kernel's exact topology;
  a kernel bump turns the fixture red for reasons that are not a spur regression. The
  fixture's provenance header and one named version test localise it, but the pin itself
  is open: `docs/tech_debt/active/2026-09-26-ci-resolves-the-kernel-the-fixture-pins.md`
  (must).
- ⚠️ [Phase 2] The ten-concurrent `/api/health` latency bar (≤2.00x idle p95) was waived,
  not demonstrated: eight runs across four sessions read 1.31x–2.45x and never ≤2.00x on
  both runs of one session. The caveat and two uninvestigated observations (every second
  run of a pair is worse than its first; the verdict sits at the harness floor, ~0.1 ms of
  p95) live in `docs/tech_debt/active/2026-09-23-concurrent-latency-bar-waived.md`
  (must). Triggers: the harness or the machine changes, or any run reads above 2.45x.
  History: `bench/RESULTS.md`, `02-LATENCY-INVESTIGATION.md`, `02-04-SUMMARY.md`.
- Resolved during v0.1 (recorded in `MILESTONES.md`, `docs/tech_debt/resolved/` and the
  decision log): five Phase 6 records (L24, L25); "CI workflow unverified" (Phase 5 — runs
  35963114939, 36088409707, 36122394253); "Untyped info contract" (Phase 4, L21); "No
  structured logging" (Phase 3, L20); "CAD builds block the event loop" (Phase 2,
  L17/L18); and the v0.1-start "Forward scope undefined" / "Success metric not
  derivable" items, both set by the human.
- ℹ️ Milestone v0.1 closed as `override_closeout` (human decision 2026-09-25): Phase 1 has
  no phase directory (pre-GSD baseline), and Phases 2–6 read `stale` in `init.manager`
  because each VERIFICATION.md fingerprints `.planning/STATE.md`, which GSD's own
  phase-complete step rewrites — for Phase 6 the declared digest recomputes exactly on
  `110b827` and only STATE.md changed after. No code, test, plan or summary changed after
  any report. Upstream GSD behaviour, not a project defect.

### Quick Tasks Completed

| # | Description | Date | Commit | Directory |
|---|-------------|------|--------|-----------|

### Roadmap Evolution

- Phase 5 edited: edited fields: goal, success_criteria (reframed per 05-CONTEXT.md D-10), Phases-list one-liner
- Phase 6 added: Address tech debt: merge gate + solid cache
- Phase 8 edited: edited fields: success_criteria (per 08-CONTEXT.md D-01)
- Phase 9 edited: edited fields: success_criteria (per 08-CONTEXT.md D-01)
- Phase 12 edited: edited fields: success_criteria (per 08-CONTEXT.md D-01)
- Phase 9 edited: edited fields: requirements, success_criteria (per 09-CONTEXT.md D-20)
- Phase 11 edited: edited fields: success_criteria (per 11-CONTEXT.md D-21)

## Deferred Items

| Category | Item | Status | Deferred At | Milestone |
|----------|------|--------|-------------|-----------|
| *(none)* | | | | |

## Session Continuity

Last session: 2026-09-29T10:41:15.464Z
Stopped at: Completed 11-09-PLAN.md
Resume file: None

## Operator Next Steps

- `/gsd-code-review 10 --codex` — optional: a Codex pass over the CR-01 fix diff (`60d02f7`), the one phase-10 diff no second lane has read yet
- Open a PR for `gsd/phase-10-tooth-tip-chamfer` and land it with `make pr.land PR=N`
- `/gsd-map-codebase --paths bench` — the codebase-drift gate warned on every Phase 10 wave: the map predates `bench/`
- Then `/gsd-discuss-phase 11` on a `gsd/phase-11-*` branch cut from the squash commit (Phase 11 has no CONTEXT.md yet)
- Expect `gsd_run query commit` to time out on every commit (hook ~100 s > 30 s) and fall back to a plain `git commit` with hooks; check for a pre-commit stash patch after each timeout (docs/tech_debt/active/2026-09-25-gsd-commit-timeout-kills-cold-verify-hook.md)
