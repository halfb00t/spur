---
gsd_state_version: "1.0"
milestone: v0.3
milestone_name: Clean Ledger
current_phase: 16
current_phase_name: Typing & Validation Debt
status: executing
stopped_at: Completed 16-02-PLAN.md
last_updated: "2026-10-05T03:36:21.181Z"
last_activity: 2026-10-04
last_activity_desc: Phase 16 execution started
state_head: 5ba02d25999df56de651ce50e95d313556a199b3
progress:
  total_phases: 4
  completed_phases: 5
  total_plans: 20
  completed_plans: 19
  percent: 95
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-10-04)

**Core value:** A number this tool prints is a number someone will cut metal to — every
dimension is computed honestly or reported as a warning, never guessed (L08).
**Current focus:** Phase 16 — Typing & Validation Debt

## Current Position

Phase: 16 (Typing & Validation Debt) — EXECUTING
Plan: 3 of 3
Status: Ready to execute
Last activity: 2026-10-04 — Phase 16 execution started

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
| 11 | 9 | - | - |
| 12 | 9 | - | - |
| 13 | 7 | - | - |
| 14 | 4 | - | - |
| 15 | 6 | - | - |

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
| Phase 12 P02 | 52min | 3 tasks | 4 files |
| Phase 12 P03 | ~40 min (continuation session, Task 3 only) | 3 tasks | 12 files |
| Phase 12 P04 | ~30min | 2 tasks | 5 files |
| Phase 12 P05 | ~45min | 2 tasks | 2 files |
| Phase 12 P06 | ~23min | 2 tasks | 1 files |
| Phase 12 P07 | ~55min | 3 tasks | 3 files |
| Phase 12 P08 | ~35min | 2 tasks | 9 files |
| Phase 12-composition-pass P09 | ~20min | 3 tasks | 2 files |
| Phase 13-latency-bar P01 | ~22min | 2 tasks | 24 files |
| Phase 13 P02 | ~5min (continuation, Task 3 only) | 3 tasks | 2 files |
| Phase 13 P03 | ~50min | 2 tasks | 81 files |
| Phase 13 P04 | 8min | 1 tasks | 6 files |
| Phase 13 P05 | 2min | 0 tasks | 0 files |
| Phase 13 P06 | ~69min total (continuation: Task 2 close-out + Task 3, ~45min) | 3 tasks | 13 files |
| Phase 13 P07 | ~25min (continuation; Task 1 prior session) | 2 tasks | 8 files |
| Phase 14 P01 | 22 min | 3 tasks | 6 files |
| Phase 14 P02 | 25 min | 3 tasks | 7 files |
| Phase 14 P03 | 22 min | 2 tasks | 2 files |
| Phase 14 P04 | 70 min | 3 tasks | 5 files |
| Phase 15 P01 | 10h 41m | 3 tasks | 5 files |
| Phase 15 P02 | 41 min | 3 tasks | 11 files |
| Phase 15 P03 | 22 min | 3 tasks | 2 files |
| Phase 15 P04 | 23 min | 2 tasks | 3 files |
| Phase 15 P05 | 10min | 3 tasks | 8 files |
| Phase 15 P06 | 8 min | 3 tasks | 6 files |
| Phase 16 P01 | 7 min | 3 tasks | 14 files |
| Phase 16 P02 | 11min (continuation; Task 1 was the human's) | 3 tasks | 3 files |

## Accumulated Context

### Decisions

Full decision log: PROJECT.md "Key Decisions" table (L01–L25, from
`docs/architecture/decision_log.md`). Flagged for revisit there: L10 (radial root
fillet — trochoidal is a tracked idea) and L18 (ten-concurrent latency bar accepted with
caveat). L14 was superseded by L21 in Phase 4 — the ratchet is on, not deferred again. L24 (a cached
solid never carries a mesh) and L25 (the merge gate reads the whole message and the run's own
verdict, amending L22) were appended in Phase 6. L26 (the pre-v0.2 fixture as the standing
L05 proof; a selector never silently selects nothing) was appended in Phase 7. L27 (a hex bore replaces the whole round profile; its limits are the chamfered corner's against the root circle, measured; the replay requires post-fixture fields null) was appended in Phase 8. L30 (body cutouts: one pattern per part, cut in one boolean, the honeycomb's cell count capped at a measured constant) was appended in Phase 11. L31 (v0.2 composes: the composed sweep measured, `spoke_count` `le` 32, the matrix and the three-interface parity proven, export bytes explicitly not compared) was appended in Phase 12. L33 (the root lead-in warned, not re-cut; the filleted-spoke cutout proved against a closed form at `abs=1e-9`; the 15 composed cutout rows named — four hole-through-web rows on the web formula, the three tip-chamfer rows at `abs=1e-8` by the human's 14-04 checkpoint answer over measured ~6e-10 mm³ gaps, eleven still at a 6 dp literal because their closed form is not derived here; amends L09, L10 and L30) was appended in Phase 14 and corrected in place by gap plan 14-04. L34 (the gate measured: 63.555 s at `-n 8` with coverage against the human's 66 s bar, `fail_under = 96` from a 96.99 % serial baseline, CI's `make verify` under `PIP_CONSTRAINT: requirements.txt` printing the fixture's kernel pair; amends L12 and L13) was appended in Phase 15.

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
- [Phase 12]: Human approved Phase 12 SC3/SC5 wording as proposed; resolved D-11 evidence conflict as 'seven' groups (schema-matching); resolved D-18 evidence conflict as 'comment + L31' (append row to _GZIP_LEVEL comment table, record in L31, L19 text untouched)
- [Phase 12]: [Phase 12] 12-02: bench/build_time.py's own report() reads os.getloadavg() only after every sweep row has already built, so its printed 'Load averages at start' is really an end-of-run reading -- both composed-sweep runs read well above D-02's 1.5 bar there despite launching on an independently-confirmed-quiet host, so neither run is decisive; recorded exactly as measured, le/timeout decision deferred to 12-03. — The composed sweep's four spoke rows (both bore shapes, both moduli) read 31.16-31.98s of SPUR_BUILD_TIMEOUT=30s in both non-decisive runs, within 0.7s of each other -- consistent enough to flag for 12-03's checkpoint without deciding anything here (D-02's prohibition on resting a decision on a non-quiet reading).
- [Phase 12]: [Phase 12] 12-03: D-02 superseded for this one gate (human decision, Task 2 third ask): four composed-sweep runs at at-start loads 12.66, 7.04, 2.74, 1.54 all found the same four spoke_count=40 rows over budget within a ~2s band that did not track load; Run 4 (load 1.54) named the reference run rather than waiting on a fifth quiet run.
- [Phase 12]: [Phase 12] 12-03: Human chose D-03's first offer, "lower-le: spoke_count 32" -- the probe measured on Run 4's heaviest composed row (module=10, keyed bore, tip_chamfer=3): 32 the largest count inside 30s (29.41s), 33 over again (30.11s). spoke_count's le lowered 40->32 (547214e); the whole composed sweep re-run confirms every row now inside 30s (heaviest 29.42s).
- [Phase 12]: [Phase 12] 12-03: Both build-timeout debts this sweep triggered (tip-chamfer margin, spoke-le arithmetic total) resolved with the composed row's measured number and the decision, moved to docs/tech_debt/resolved/ (89304e2); the tip-chamfer debt's own concurrent-load question re-homed, not dropped, into docs/tech_debt/active/2026-09-23-concurrent-latency-bar-waived.md's trigger (D-04).
- [Phase 12]: D-16's row confirmed by the number across five recorded composed-sweep runs; D-18's rule re-applied on the re-measured table selects level 1 again, _GZIP_LEVEL unchanged; the re-measured table landed as a dated comment addition per 12-01's binding answer (comment + L31), decision_log.md untouched by this plan
- [Phase 12]: 12-05: D-08's 114/6/18 refusal-composition split re-derived from check() and matched the planning probe exactly, no difference recorded; alone/composed entries matched by fields tuple, not list position (needed for spoke-annulus-keyed/spoke-opening-keyed where the keyed bore's own rule fires first); REFUSAL_HEX uses bore_hex 8, not tier-1's 6, so hub/rim refusals keep firing when composed with a hex bore.
- [Phase 12]: [Phase 12] 12-06: 15 new kernel-level rows (12 tip-chamfer+cutout+bore, 3 single-sided-recess+cutout) prove D-07 tier 2/D-09 on the pairs no earlier phase built; every measured delta matches the planning probe exactly; a new probe-location helper _honeycomb_nearest_point_angle finds the hub probe on whichever honeycomb cell is actually nearest the axis. The 15 rows measured 30.66-30.73s of pytest time, over the plan's own ~25s advisory share and close to D-10's phase-wide 30s ceiling before 12-07/12-08's own tests land -- recorded honestly for 12-09's gate.
- [Phase 12]: D-11's group count pinned as seven (Teeth, Body, Bore, Recess, Spokes, Holes, Honeycomb), re-verified live against /api/schema in 12-07
- [Phase 12]: 12-07: the byte-for-byte CLI/API document claim reads as the API's JSON re-indented (json.dumps(indent=2, ensure_ascii=False)) equalling the CLI's own model_dump_json(indent=2) -- verified equal, not assumed
- [Phase 12]: 12-08: docs/architecture/cli.md's Errors section rewritten to the real 2/1/1 exit contract (parameter errors exit 2, unknown extension and every BuildError exit 1); src/spur/cli.py byte-unchanged (the doc moved to the code, 10 D-14 stands); pinned by a test that runs the real process, closing must-debt 2026-09-28-cli-md-claims-exit-2-where-cmd-export-exits-1.md
- [Phase 12]: 12-08: both deferred UI ideas (conditional form fields, bore-shape selector) judged 'not taken' per D-12 -- 08 D-09's schema-driven form stands; new trigger is a browser test existing or a user reporting the ignored-field warnings insufficient; the browser-test idea records 12-07's cheaper-first-step taken
- [Phase 12-composition-pass]: D-10's gate: human accepted the measured +28.28s make-verify cost delta against the 30.0s line; no tier-2 test row trimmed
- [Phase 12-composition-pass]: L31 appended to docs/architecture/decision_log.md closing out Phase 12, citing every number to a SUMMARY sha or bench/RESULTS.md section (D-19)
- [Phase 13]: 13-01: Order default kept concurrent,single (bench.latency.main()'s own sorted() order), not D-08's literal 'single then concurrent' -- both scripts take --order so 13-02's checkpoint settles A1 without a code change either way.
- [Phase 13]: 13-01: Fixed a Rule-1 bug found during Task 2's own proof -- session.py's existing-files preflight overwrote its own prior status.json via abort(); fixed to print-and-exit without touching any file for the label, matching run_experiment.py/poller.py's refuse-not-overwrite behavior (E7).
- [Phase 13]: D-08's run order settled by the human: harness order (concurrent, then single), not D-08's literal single-then-concurrent text -- matches Runs 1-8 and the decisive D-07 session; --order concurrent,single, the scripts' existing default.
- [Phase 13]: Host prepared per D-06 for the campaign: fleet-user already read Exited (2) before the checkpoint (no docker stop needed); the human confirmed the host quiet for the campaign window ('approved'); spur-spur-1 stayed Up throughout, untouched.
- [Phase 13]: Pair A split (A1 worse, A2 not worse) triggers the pre-registered escape clause: observation 1 is 'not reproduced in this environment', not forced onto Pair B/C's own directions
- [Phase 13]: Observation 2 ruled to candidate (ii) 'the floor is real' (four of twenty-four verdict cells flip inside one percentile); candidate (iii)'s exact claim checked and found false
- [Phase 13]: The measured smallest sample gap (2.328e-10 s) is reported as a float64-precision artifact below the declared clock resolution, not used to set D-10's M; the one-percentile spreads (0.090-0.296 ms) are 100-700x the clock resolution, flagged for the human before M is fixed in L32
- [Phase 13]: No debt file filed: observation 1 not reproduced and observation 2's cause is harness/measurement-floor, not a server defect -- D-17 reserves filing for a server-side cause ruled in
- [Phase 13]: bar-3's D-05 gate released after 320 s; both concurrent runs passed (1.31x, 1.42x) -- outcome (a): the bar is demonstrated on the unmodified harness
- [Phase 13]: Task 2 (D-09 checkpoint) not reached -- outcome (a) means 13-05 (outcome (b) only) is not executed
- [Phase 13]: 13-05: not executed -- outcome (a) (13-04's bar-3 decisive session, both concurrent runs <=1.99x). The plan's own Task 1/2/3 outcome-(a) clauses fired before any harness, test or doc change; D-11 not reached.
- [Phase 13]: 13-06: scenario_composed added to bench/latency.py as a third, tested scenario registered in _SCENARIOS; DEFAULT_SCENARIOS keeps the no-argument run at (concurrent, single) so the bar's own run is unchanged; scenario_single/scenario_concurrent verified byte-identical to 9f26052.
- [Phase 13]: 13-06: SC3 (the composed worst row under ten concurrent builds) ran once on a fresh server behind the D-05 gate (900s cap, non-decisive) and aborted after every request was sent: 0 of 10 served, 6 of 10 refused (503 busy), 4 of 10 admitted and all four exceeded SPUR_BUILD_TIMEOUT -- two via the documented BuildTimeout path, two via an undocumented 500. Human's checkpoint decision: record it as-is, file the behaviour as debt, no retry, no src/ change (D-16, D-17).
- [Phase 13]: 13-06: filed must-severity debt (docs/tech_debt/active/2026-10-02-same-slot-timeout-cleanup-race-produces-undocumented-500.md): two same-slot timed-out requests race _run_with_timeout's cleanup -- the second caller's `executor` local still points at the object the first caller's recreate_for already shut down, so `executor._processes` reads None and raises AttributeError, surfacing as an undocumented 500. The worst row's own 0.58s margin (Phase 12's re-run) also disappeared under this contention, folded into the same debt file as a related finding.
- [Phase 13]: 13-06: bench/RESULTS.md's SC3 section is built entirely from the committed server records (sc3.server1.records.jsonl), not a client-side latency table -- the harness's own requests tuple was never built (it crashed mid-comprehension) and no client wall-time exists for any of the ten rows; in-process/split-poller idle/under-load ratios are reported as absent with reason, never estimated from a substitute boundary (L08).
- [Phase 13]: L32 appended (amends L18, append-only): the bar demonstrated outright on bar-3 (outcome a, Run 13 1.31x / Run 14 1.42x) -- 13-05's outcome-(b) path and D-09/D-11 were never reached
- [Phase 13]: The 2026-09-23 waived-latency debt retired in 6709953 (sha recorded in follow-up 05668ef, since a file cannot carry its own commit's sha); Dockerfile's measured-p95 comment updated (eight -> fifteen runs), no ratio bar cited
- [Phase 13]: fleet-user's pre-phase state was already Exited -- the phase never started it, so 13-07's host-restore step confirmed it unchanged (Exited) rather than running docker start; spur-spur-1 stayed Up throughout; make verify green (910 passed) at phase close
- [Phase 14]: 14-01: the root lead-in warning fires at round(h, 3) > 0 and sits after 'Root fillet reduced'; README states the condition with one clause beyond D-12's draft (profile shift above 0.125) because the chord is capped halfway up the tooth below it, proven by the mid-tooth rows; expected strings captured from derive() (debt-x1.0-pa14.5 prints 0.562, not CONTEXT's 0.563) — D-01/D-02/D-12 content kept; 0.125 clause proven by the mid-tooth-silent/touch/warns rows
- [Phase 14]: 14-02: the filleted-spoke volume oracle is a polar closed form independent of _fillet_corner; the tripwire shifts the rim-corner root by 1e-6 mm, not 0.01 mm
- [Phase 14]: 14-02: the shared cutout assertion defaults to abs=1e-9; composed-solid rows with 6 dp literals keep rel=1e-6 via volume_rel (debt filed)
- [Phase 14]: L33 states the composed-row exception exactly: 15 rows (12 tip-chamfer, 3 single-sided-recess) keep volume_rel=1e-6; the four cutout rows and the three tripwire rows run at abs=1e-9
- [Phase 14]: 14-04 Task 2: noise-multiple 1e-8 -- the three tip-chamfer holes rows assert the web formula at abs=1e-8 (about 15x their largest measured gap 6.55e-10), the single-sided holes row at abs=1e-9; logged in L33
- [Phase 15]: 15-01: apparent xdist knee is N = 8 (68.93 s, all four sweep rows green); human picks N at 15-03 — Pre-registered rule: smallest N within 1.10x of the fastest green wall; S12 (75.47 s) is within the band but larger and slower than S8
- [Phase 15]: fail_under = 96 from D-10's rule: L = 96.99 (serial C0, lowest of four totals), S = 0.00 (three -n 8 totals at 97.21); precision = 2 — bench/RESULTS.md Phase 15 Coverage floor; red on the floor without tests/test_cli.py read 90.24 against 96
- [Phase 15]: xdist tolerance at N = 8 adopted: six alternating runs 927 passed each; coverage costs 3.51 s at -n 8 (60.61 s -> 64.12 s) — D-05 verdict and D-12 cost row in bench/RESULTS.md Tolerance and coverage cost; no D-08 xdist_group needed
- [Phase 15]: make test runs 'pytest --cov --cov-report=term $(PYTEST_ARGS)': the option after --cov stops it taking a path in PYTEST_ARGS as its source — measured: bare --cov plus tests/test_calc.py ran 927 tests, not 404, --no-cov no help; 15-04 must keep --cov-report=term right after --cov when it inserts -n
- [Phase 15]: D-01 checkpoint answer: knee-headroom N=8 bar=66 cuts=none before=244.59 (bar = largest of B1-B3 rounded up, read as mean(B) of the -n 8 --cov gate; all 15 proposed cuts refused by name; 15-04 Before row = serial --cov run C0 244.59 s) — The human set the bar from the profile at the 15-03 checkpoint; N equals K so no extra tolerance runs; CI runs -n 4 on 4 vCPUs.
- [Phase 15]: 15-04: N = 8 goes into the Makefile as PYTEST_WORKERS, one literal clamped to the online CPUs; the gate read mean(B) 63.555 s against the 66 s bar (met), serial --cov mean(A) 228.99 s; the pre-commit hook comment '~11 s' stays for 15-06
- [Phase 15]: 15-05: CI's kernel pin is PIP_CONSTRAINT=requirements.txt as step-level env on make verify, plus an always-run step printing the resolved pair; run 37181871926 on draft PR #18 printed cadquery 2.8.0 cadquery-ocp 7.9.3.1.1 — D-13: one env line reaches pip's self-upgrade and the editable install inside the venv recipe; neither named REQ option was taken
- [Phase 15]: 15-05: phase PR #18 is a draft; at ship update it with gh pr edit and gh pr ready, not gh pr create — gh pr create would refuse a second PR for the branch (D-16 addendum)
- [Phase 15]: L34 appended after L33 amends L12 and L13: the gate is measured (mean(B) 63.555 s at -n 8 with coverage, bar 66 s met), floored (fail_under 96) and CI installs the pinned kernel; every '~11 s' site now states the measured figure — Phase 15 plan 06; the figure is the gate as committed on the 12-core dev host (bench/RESULTS.md Before and after); the commit-timeout debt stays active
- [Phase 16]: 16-01: the Shape narrowing is two isinstance helpers raising BuildError (_body at three fillet/chamfer sites, _shape_of at two .val() sites), never a cast; _gear_blank stays -> cq.Shape — Shape.cut returns Shape whatever goes in, so a cast at .val() reaches two of five; -> cq.Solid makes mypy flag five [assignment] errors in _build (16-RESEARCH Pitfall 1)
- [Phase 16]: 16-01: mypy's override dropped cadquery.* (OCP.* stays); D-04's gate passed -- mypy output over src tests docker bench scripts byte-identical with the cache cleared before and after — cadquery ships py.typed, OCP ships no type information; cmp of the two captures, both 'Success: no issues found in 37 source files'
- [Phase 16]: 16-01: make no-fake-done refuses a mypy suppression under src/spur/ (seen red against the five lines at 085e5a6); tests/ keeps its two deliberate ones — mypy's warn_unused_ignores refuses a stale suppression but nothing refused a new one (the fifth arrived unnoticed in 10-02)
- [Phase 16]: 16-02: Phase 07 and 08 VALIDATION.md read back from committed state, both nyquist_compliant true; gap ledger 3 nice rows (Phase 07 Manual-Only), 0 for Phase 08, D-09 exception not reached — Counted by the Status-cell and Manual-Only rule, not the skill's own 0-gaps audit; row 2 (regeneration byte-stability, no test of the writer) classified nice because it has a named command and a committed measurement

### Pending Todos

None yet.

### Blockers/Concerns

- ℹ️ [Phase 14] Code review (`14-REVIEW-DISPOSITION.md`, 4 open): WR-01 — the shared cutout
  assertion's `volume_rel` silently wins over the new `volume_abs` when both are passed (no
  caller does; an at-most-one assert closes it); IN-01 — three `tests/test_model.py` comments
  cite `14-REVIEW WR-02`/`WR-03`, ids the re-review renumbered; IN-02 — L33 credits the
  tip-row `1e-8` bar to D-06, whose trigger (a gap above 1e-9) was not met — the bar was set
  over thin headroom, and L33 should say so; IN-03 carried. The prior review's WR-01 (the
  `abs=1e-9`/`1e-8` volume bars are calibrated only on macOS arm64 while CI runs
  ubuntu-latest) is no longer in the ledger — its id was reused and the reviewer did not
  re-file it; the text lives in `8cfbc16`'s `14-REVIEW.md`. It still applies to the four
  moved rows.
- ℹ️ [Phase 14] `test_the_hole_link_cuts_six_holes_through_the_recessed_floor` asserts the same
  web formula at `rel=1e-6` on the default gear — outside G-14-5's four rows; 14-04 left the
  decision to the human. `14-SECURITY.md` exists (verified 2026-10-03, `threats_open: 0`).
- ⚠️ [Phase 13] `src/spur/pool.py:204` (`_run_with_timeout`): two timed-out requests on one
  worker slot race each other's cleanup — the second still holds the executor the first's
  `recreate_for` already shut down, reads `executor._processes` as `None`, and the request
  returns an undocumented 500 instead of a contracted 503. Found by SC3 (request ids
  `912cd2d4`, `0fc30d53` in `investigation/sc3.server1.records.jsonl`). Filed
  `docs/tech_debt/active/2026-10-02-same-slot-timeout-cleanup-race-produces-undocumented-500.md`
  (must); no `src/` change in Phase 13 by D-17; trigger named in the file.
- ⚠️ [Phase 13] D-05's quiet bar (1-min load under 1.5 for three consecutive 30 s samples,
  900 s cap) was reached in 2 of 5 measurement sessions on this host; `bar-1`, `bar-2` and
  SC3 capped out, and the idle floor with a Claude Code session active read ~2.0. Phase 15's
  `make verify` profiling and any future re-measurement need an idle machine or a recorded
  D-05 amendment, not a fourth attempt.
- ℹ️ [Phase 13] Code review (`13-REVIEW-DISPOSITION.md`, both `open`): CR-01 — the Dockerfile
  `HEALTHCHECK` comment counts the SC3 run among the "fifteen" runs behind the 0.7–2.3 ms
  p95 range, but SC3 produced no p95 (fourteen did); WR-01 — `_report_markdown` prints the
  single/concurrent `RECORDED_BASELINE` under a `composed` heading. CR-01 is a one-word fix.
- ℹ️ [Phase 13] `/gsd-map-codebase --paths bench` is still owed: `.planning/codebase/`
  predates `bench/`, and the drift gate advised on every wave of Phase 13.
- ℹ️ [Phase 12] All 14 code-review findings (WR-01…WR-09, IN-01…IN-05) are `fixed` per
  `milestones/v0.2-phases/12-composition-pass/12-REVIEW-DISPOSITION.md` (`open: 0`, recorded
  2026-10-01). An earlier version of this entry said ten were still `open` — stale, corrected
  at the v0.3 start.
- ℹ️ [Phase 12] The two build-timeout debts (Phase 10's tip-chamfer margin, Phase 11's spoke
  arithmetic total) are resolved by the composed sweep's measured numbers (`89304e2`); the
  tip-chamfer debt's concurrent-load question was re-homed into the Phase 2 latency debt's
  trigger set (12-03). Phase 11's six review findings were all fixed in `11-REVIEW-FIX.md`
  before that branch landed.
- ⚠️ [Phase 15] The pre-commit `make verify` hook is now ~64 s warm at 927 tests (`-n 8`
  with coverage, L34) — still over `gsd_run query commit`'s 30 s. This session's UAT commit
  was killed at 30 s mid-hook (no stash was taken; the orphaned hook finished on its own) and
  every Phase 15 close-out commit was a plain `git commit` with the hook running, never
  `--no-verify`. The debt stays active (`nice`) and now carries the ~64 s figure; review
  WR-03 (`15-REVIEW-DISPOSITION.md`) says its recovery argument and trigger contradict it.
- ⚠️ [Phase 12] The pre-commit `make verify` hook now runs ~3.5 min at 907 tests (D-10's
  measured +28.28 s on top of Phase 11's 178 s); `gsd_run query commit`'s 30 s timeout cannot
  complete it (the Phase 9–11 items below stand) — every Phase 12 close-out commit was a plain
  `git commit` with the hook running, never `--no-verify`.
- ⚠️ [Phase 11] `gsd_run query commit`'s 30 s timeout killed the `make verify` hook on the UAT
  commit this session (~3 min cold at 621 tests, pytest at ~9 cores) — and the orphaned
  pre-commit process kept running with `state.json` stashed; waited for it to exit and restore
  the stash, then a plain `git commit` with hooks (hook passed, ~3 min). The Phase 9/10 items
  below stand; the debt's trigger now covers a cold run of three minutes.
- ℹ️ [Phase 10] Code review WR-01 (a nonzero `tip_chamfer` under 0.0005 mm was silently
  discarded) and CR-01 (its first fix attributed print-precision rounding to a geometric
  limit — found by the Codex lane, confirmed internally) are both fixed: `54fe020`,
  `60d02f7`. A request that rounds to nothing now warns with its true cause; sub-µm
  rounding of a nonzero request stays silent like every other 3-dp field (human decision
  2026-09-28). IN-01/IN-02 stay open (info) in `10-REVIEW-DISPOSITION.md`.
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
- ℹ️ [Phase 7 → 15] CI now resolves the kernel pair the fixture pins: `PIP_CONSTRAINT:
  requirements.txt` on CI's `make verify` step (L34, 15-CONTEXT D-13); run 37181871926
  printed `cadquery 2.8.0 cadquery-ocp 7.9.3.1.1`; the `must` debt retired in `839dfea`
  (`docs/tech_debt/resolved/2026-09-26-ci-resolves-the-kernel-the-fixture-pins.md`). What
  the green run cannot show — the constraint vs. cadquery 2.8.0's own `cadquery-ocp<8.0`
  cap — rests on the local fail-closed dry run (`ResolutionImpossible`; UAT test 7, accepted).
- ℹ️ [Phase 2 → 13] The ten-concurrent latency bar is demonstrated on the unmodified harness
  (L32: `bar-3` Runs 13–14 at 1.31×/1.42× idle p95 on both concurrent runs of one decisive
  session) and `2026-09-23-concurrent-latency-bar-waived.md` retired in `6709953`; the two
  observations are ruled — the second-run-worse effect not reproduced in this environment
  (Pair A split; `fleet-user` stopped where Runs 1–8 had it restart-looping), the floor real
  (4 of 24 verdict cells flip inside one percentile). History: `bench/RESULTS.md`,
  `13-LATENCY-INVESTIGATION.md`, `milestones/v0.1-phases/02-*/02-LATENCY-INVESTIGATION.md`.
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
- Phase 12 edited: edited fields: success_criteria SC3, SC5 (per 12-CONTEXT.md D-06/D-15)
- v0.3 roadmap created: Phases 13–16 (Latency Bar; Honest Record; The Gate, Measured and Pinned; Typing & Validation Debt) — 11/11 v0.3 requirements mapped, 0 orphans, numbering continues from Phase 12
- Phase 15 edited: edited fields: depends_on, success_criteria SC2, research flag (per 15-CONTEXT.md D-01)
- Phase 15 edited: edited fields: success_criteria SC3 (per 15-RESEARCH Open Question 2 and the 15-CONTEXT.md D-09 addendum, decided in 15-02)
- Phase 15 edited: edited fields: success_criteria SC4 (per 15-CONTEXT.md D-13)
- Phase 16 edited: edited fields: success_criteria SC1, SC2 (per 16-CONTEXT.md D-01, D-12 and 16-RESEARCH Finding 7)

## Deferred Items

| Category | Item | Status | Deferred At | Milestone |
|----------|------|--------|-------------|-----------|
| *(none)* | | | | |

## Session Continuity

Last session: 2026-10-05T03:36:21.142Z
Stopped at: Completed 16-02-PLAN.md
Resume file: None

## Operator Next Steps

- Next: `/gsd-discuss-phase 16` then `/gsd-plan-phase 16` — Typing & Validation Debt.
  Phase 15 is complete on `gsd/phase-15-the-gate-measured-and-pinned`; its PR #18 is still a
  draft — at ship, `gh pr edit` + `gh pr ready` (never `gh pr create`, 15-05 D-16 addendum),
  then `make pr.land PR=18` per ROADMAP.md's Process Notes before starting 16's branch.
- `/gsd-validate-phase 15` — `15-VALIDATION.md` is still `draft` (`nyquist_compliant: false`;
  14's is too, 13's is validated). Not dispatched at the Phase 15 transition: the Nyquist
  auditor may add tests, and Phase 15's record pins `tests/` unchanged at 927 — run it as its
  own change.
- Triage `15-REVIEW-DISPOSITION.md` (8 open: WR-01 the CI datapoint without the `-n 4`
  baseline, WR-02 a false statement and two dangling links left by the two retirements, WR-03
  the commit-timeout debt contradicting its own trigger, WR-04 the "five runs" undercount,
  IN-01…IN-04).
- Triage `14-REVIEW-DISPOSITION.md`: WR-01 (one assert in the shared cutout assertion), IN-01
  (three stale finding-id citations in `tests/test_model.py`), IN-02 (L33's D-06 attribution
  for the `1e-8` bar), and decide whether the hole-link test's `rel=1e-6` row moves to the web
  formula. Re-file the macOS-only calibration finding if it is to stay tracked.
- Fix CR-01 (one word in the Dockerfile comment) and triage WR-01 from `13-REVIEW-DISPOSITION.md`.
- Phase 16's REQ-nyquist-phases-7-8 carries a flagged ASSUMPTION (`/gsd-validate-phase` may
  not resolve `phase_dir` for an archived phase) — resolve at that phase's discuss-phase
- `/gsd-map-codebase` — `.planning/codebase/TESTING.md` still says "Warm run ~11 seconds"
  and predates coverage and xdist; `--paths bench` is also owed (Phase 13).
- Expect `gsd_run query commit` to time out on every commit (hook ~64 s warm at 927 tests,
  `-n 8` with coverage — L34); commit with plain `git commit` and wait for any orphaned
  `pre_commit hook-impl` to exit before writing to the tree
  (docs/tech_debt/active/2026-09-25-gsd-commit-timeout-kills-cold-verify-hook.md)
