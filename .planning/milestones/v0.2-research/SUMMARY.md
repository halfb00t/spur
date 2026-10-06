# Project Research Summary

**Project:** spur — v0.2 "Fit to Shaft"
**Domain:** Parametric CAD (CadQuery/OpenCascade solid modeling), additive milestone on a shipped FastAPI+CLI+web-UI product
**Researched:** 2026-09-25
**Confidence:** MEDIUM-HIGH overall — stack and architecture findings are HIGH (verified against the installed `.venv` and the actual tree, not memory); feature/dimensional-standard findings are MEDIUM-LOW by nature of the domain (several of the milestone's own numbers have no citable standard, and the research says so rather than inventing one).

## Executive Summary

v0.2 adds five cuts — keyway bore, hex bore, three body-cutout patterns (spoke arms, lightening holes, hexagonal pattern), and a tooth-tip chamfer — to a four-step CadQuery pipeline that already composes recess -> bore -> chamfer by construction order. No new dependency is needed: the pinned `cadquery==2.8.0`/`cadquery-ocp==7.9.3.1.1` already exposes every primitive required (`Workplane.polygon(circumscribed=True)` for hex shapes, `polarArray`/`rarray` for patterning, variadic `Shape.cut(*toCut)` for batched boolean cuts, `Mixin3D.chamfer()` reused from the existing bore-rim pattern). The architecture generalizes almost entirely by adding more of the same shape that already exists in the tree (`bore_flat`, `recess_sides`, `recess_radii()`) — flat additive `GearParams` fields defaulting to off, not a discriminated-union redesign.

The one piece of v0.1 architecture that does **not** generalize for free is position-based edge selection: `_bore_rim_edges()`'s radial cutoff assumes every rim point lies within the bore's characteristic radius, which is true for round/D-flat bores but false for a hex bore (whose vertices sit at the circumradius, `w/sqrt(3) ~= 0.577w`, not the across-flats/2 apothem). Left unfixed, a hex bore's chamfer selector matches **zero edges silently** — no crash, no warning, just an unchamfered bore on every hex-bore request. This is the single highest-value catch across all four research files and must be phase-one work, ahead of any user-facing hex-bore feature. The second-highest-consequence finding is that "keyway depth" is not a self-evident datum: DIN 6885/ISO R773 and ANSI B17.1 define genuinely different quantities (a radial cut depth vs. a diametral gauge dimension), and the milestone's own rejection of standard-table lookups means `spur` itself must pick and document one convention, not infer it from a table.

Three more classes of risk recur across the pitfall and architecture research: (1) OCCT booleans are documented as non-robust for tangent/near-coincident cutter geometry, which is exactly the geometry legitimate user parameters will produce (a keyway sized to just clear a D-flat, a hole tangent to a recess wall) — the fix is `tol=` on `.cut()`, derived once from `MIN_WALL`, not per-call; (2) the hexagonal-pattern cutout's cell count is the one new number in this milestone that cannot be capped by a dimensional formula — its real constraint is wall-clock build time under `SPUR_BUILD_TIMEOUT=30s`, so the cap must come from a measured build-time sweep (mirroring how L17's memory ceiling was swept, not derived) and be reported in `warnings`, never discovered by the build itself timing out; (3) every new `GearParams` field must default to 0/off and prove it with a regression test comparing pre-v0.2 parameter sets' derived dimensions and export content before and after each phase — not asserted once at the end of the milestone, but at the time each field lands.

## Key Findings

### Recommended Stack

No dependency change for any part of v0.2. `STACK.md` verified all needed primitives directly against the installed `.venv` (via `inspect.signature`/`inspect.getsource`, not docs or memory): `Workplane.polygon(nSides, diameter, circumscribed=True)` for the hex bore and honeycomb cells (numerically confirmed `circumscribed=True`'s `diameter` argument is the across-flats distance); `Workplane.polarArray`/`rarray` for patterning lightening holes and spoke gaps (honeycomb needs an offset-row tiling built from two `rarray`/`polygon` passes plus `math` — there is no built-in honeycomb helper in cadquery 2.8.0, confirmed by `grep`); `Shape.cut(*toCut)` (variadic, one `BRepAlgoAPI_Cut` call, not a loop) for compositing many small cuts; `Mixin3D.chamfer()` reused verbatim from the existing bore-rim/recess-floor pattern for the tip chamfer, subject to the product decision noted in Known Conflict #1 below.

**Core technologies (unchanged):**
- `cadquery==2.8.0` — solid modeling API (`Workplane`, `Shape`, `Mixin3D`) — already the only CAD layer (L01); every v0.2 primitive is already exposed
- `cadquery-ocp==7.9.3.1.1` — OCCT kernel bindings — boolean cut and chamfer are OCCT operators reached through cadquery's wrappers, no direct OCP call needed
- `math` (stdlib) — sufficient for honeycomb row/column tiling arithmetic, no geometry library needed

**Explicitly rejected:** `build123d` (a second OCCT binding for zero new capability), any geometry/tessellation library for the honeycomb grid (it's a fixed lattice formula, not arbitrary polygon packing), and a standard keyway-size lookup table (`PROJECT.md` rejects this outright on Core Value grounds).

### Expected Features

`FEATURES.md` is MEDIUM confidence on keyway/hex dimensional data (cross-source-consistent) and explicitly LOW on body-cutout proportions and tip-chamfer sizing — correctly graded LOW because **no engineering standard governs spoke count, arm width, lightening-hole proportions, or tip-chamfer size**; treating a "sensible default" as if it were a standard is the specific trap this research flags.

**Must have (table stakes, already committed in PROJECT.md):**
- Keyway bore, explicit width/depth/clearance — the most common shaft-mount feature outside round/D-flat; every comparable tool offers some form of it
- Hex bore, across-flats + clearance — common for RC/robotics/DIY hex stock
- Tooth-tip chamfer — standard practice to break the sharp tip edge, both for metal-cut and FDM-printed gears
- Circular lightening holes on a bolt circle — the most common weight-reduction feature, closest analogue to the shipped `recess_radii()` fit logic

**Differentiators (no comparable tool offers this combination):**
- Explicit-parameter keyway with no standard-table lookup — nearly every comparable tool (Eng Bench, etc.) *derives* keyway size from bore Ø via a baked-in table; `spur`'s explicit-fields approach is a genuine, deliberate differentiator matching the Core Value
- Spoke-arm / hexagonal-honeycomb body cutouts — not offered by any researched comparable tool (FreeCAD FCGear/GearWorkBench, BOSL2 gears.scad, Fusion 360 add-ins) beyond simple lightening holes
- Composability — cutout + recess + bore on one part, none of the researched comparable tools advertise this; this is where the real implementation risk sits, not in any single new cut

**Defer (already out of scope per PROJECT.md, do not re-litigate):**
- Standard-table keyway sizing — rejected on Core Value grounds, not deferred
- Spline bores (DIN 5480 and kin) — "a standards surface, not a cut"
- Tip relief (meshing-load profile modification) — a different, heavier feature than an edge-break chamfer; don't conflate the two under one name

### Architecture Approach

`ARCHITECTURE.md` (HIGH confidence, grounded in file:line citations against the current tree) recommends extending the existing four-step pipeline additively: `_gear_blank -> _cut_face_recesses -> _cut_bore (generalized) -> _cut_body (new) -> _chamfer_tips (new)`. The recess step stays first because its `.fillet()` call bakes real filleted geometry into the solid before any other cut touches it — every downstream cut, including v0.2's new body cutouts, subtracts from a solid whose floor fillet already exists as baked geometry, not something a later selector re-derives. Bore comes before body cutouts so `_bore_rim_edges`'s radial-cutoff selector sees only the bore's own edges near the axis, not a nearby lightening hole's or spoke arm's edges competing for the same selection test. Tip chamfer goes last since it acts on the tooth-tip circle, untouched by anything else.

`GearParams` should stay flat additive fields (one group per feature, each gated by its own 0/off sentinel), not a `bore_type` discriminator — because keyway must compose with whichever base bore shape is chosen (round or hex), and a discriminator would wrongly force mutual exclusivity. This mirrors the existing `bore_flat: float = 0` ("0 = round") precedent exactly, and needs no new schema/CLI/form machinery.

**Major components:**
1. `params.py` — additive `_f(0, ...)` field groups for bore-hex/keyway, body cutouts, and tip chamfer; `check()` gains the conflict-refusal rules (422s naming fields)
2. `calc.py` — new derived fields (`bore_hex_flats_effective`, `keyway_effective_width/depth`, `spoke_arm_actual_width`, `hole_actual_d`, `hex_cell_count`, etc.), new cap-and-warn / refuse logic, and a new `bore_rim_limit(p)` function that computes the correct radial-selection bound per bore shape (circumradius for hex, not across-flats/2)
3. `model.py` — generalized `_cut_bore`/`_bore_rim_edges` (accepts straight edges as well as arcs, uses `bore_rim_limit()`), new `_cut_body()` and `_chamfer_tips()` cut steps appended to `_build()`
4. `app.py`/`pool.py`/`cli.py` — no code change needed; the cache key (value-equality on the frozen `GearParams`) and CLI flag generation already generalize automatically as new fields are added

### Critical Pitfalls

Top pitfalls from `PITFALLS.md` (11 total, MEDIUM-HIGH confidence, grounded in this repo's own code plus OCCT documentation and CadQuery issue trackers):

1. **Tangent/coincident cutter geometry makes OCCT booleans non-robust** — a keyway sized to just clear a D-flat, a hole tangent to a recess wall, are legitimate user designs (not edge cases) that can produce a hard failure or a silently cracked solid. Fix: `tol=` on every `.cut()`/`.fuse()` call, derived once from `MIN_WALL`, documented as a new `Lxx` decision, not picked ad hoc per call.
2. **Sequential `.cut()` per cutter instead of one multi-argument `.cut(*cutters)` call** — for dozens of holes/cells, a `for` loop re-does topology reclassification N times. `Shape.cut()` already accepts `*toCut`; batch every cutter for one cutout pass into one call.
3. **Position-based edge selectors (`_bore_rim_edges`, `_groove_floor_edges`) silently pick the wrong edges — or none — once new topology exists on the same face.** The hex-bore circumradius bug (see Known Conflicts #6) is the concrete instance; every new cutout adds edges to the same end faces, and a selector proven correct against v0.1's two-feature topology has no assertion that fires when a third feature invalidates its proof.
4. **A tooth-tip chamfer via `Mixin3D.chamfer()` on a many-toothed outline risks repeating L09's ~50x fillet-operator cost** — see Known Conflict #1 for the full product-decision framing.
5. **Honeycomb cell count must be capped analytically before cutting, not discovered by the build timing out** — deriving the cap from a measured per-cell cost, reporting the applied cap in `warnings`, never letting a clock-based loop exit silently (which would make cell count non-reproducible across machines, violating L05/L08).

## Implications for Roadmap

### Phase 1: Foundation — generalize bore-rim edge selection + lock the L05 regression fixture
**Rationale:** `ARCHITECTURE.md`'s Q6 and `PITFALLS.md`'s Pitfall 4 both independently identify this as the highest-value, lowest-risk first move: the hex-bore edge-selector bug (Known Conflict #6) is a silent failure with no error signal, and every later phase needs a proven "old links are unchanged" fixture to test against rather than inventing its own ad hoc check.
**Delivers:** `calc.py`'s `bore_rim_limit(p)` function (per-shape radial bound for edge selection); generalized `_bore_rim_edges` in `model.py` accepting straight edges; a new fixture-based regression test (`test_pre_v0_2_parameter_sets_are_unchanged` or similar) capturing `derive()` output and `build()`'s volume/bounding-box for a representative pre-v0.2 parameter matrix.
**Addresses:** No user-facing feature yet — pure foundation work per PROJECT.md's "old links unchanged" success metric.
**Avoids:** Pitfall 4 (silent wrong-edge/zero-edge selection) and Pitfall 6 (non-off default drift), before either has a feature to hide inside.

### Phase 2: Hex bore
**Rationale:** Smallest new shape (one polygon cut, one chamfer selection, no interaction with recesses or body cutouts) that exercises Phase 1's generalized selector end-to-end against real geometry, not just the theoretical argument.
**Delivers:** `bore_hex_flats` field, hex-bore cut in `_cut_bore`, `check()` conflict rule (`bore_flat > 0 and bore_hex_flats > 0`).
**Addresses:** Hex bore (FEATURES.md table stakes, LOW-MEDIUM complexity).
**Avoids:** Pitfall 1 (tol= on tangent hex-vertex-to-recess cases), re-verifies Pitfall 4's fix.

### Phase 3: Keyway bore
**Rationale:** Builds on Phase 2's generalized bore-shape plumbing; must resolve the depth-datum decision (Known Conflict #3) explicitly, since it is the one open product question no research file could resolve from docs alone.
**Delivers:** `keyway_width`/`keyway_depth`/`keyway_clearance` fields, keyway cut in `_cut_bore`, a new decision-log entry (`Lxx`) stating the depth datum, a solid-level test measuring the built keyway floor position against the stated datum (not just the parameter round-tripping).
**Addresses:** Keyway bore (FEATURES.md's highest-value differentiator: explicit parameters, no standard-table lookup).
**Avoids:** Pitfall 9 (depth-datum ambiguity) — the single highest-consequence pitfall in the whole research set.

### Phase 4: Tooth-tip chamfer
**Rationale:** Independent of bore and body work (different edges, different region of the solid) — can run in parallel with Phases 2-3 if the roadmap wants a parallel track. Must resolve Known Conflict #1 (which reading of "tip chamfer") as a product decision before implementation, since the two readings have very different cost profiles.
**Delivers:** `tip_chamfer` field; either an analytic 2D tip-corner chamfer extending `_outline()` (if the 2D-profile reading is chosen) or a measured `Mixin3D.chamfer()` implementation with a benchmark at 200 teeth proving it clears `SPUR_BUILD_TIMEOUT` (if the 3D-deburring reading is chosen).
**Addresses:** Tooth-tip chamfer (FEATURES.md table stakes, reuses the `bore_chamfer` convention).
**Avoids:** Pitfall 3 (repeating L09's ~50x fillet-operator cost).

### Phase 5: Body cutouts — lightening holes, then spoke arms, then hexagonal pattern
**Rationale:** Ordered by complexity per `ARCHITECTURE.md`'s Q6: holes are the simplest cut (a `polarArray` of circles, cheapest to benchmark) and establish the `cut(*cutters)` batching pattern every later multi-instance cutout reuses. Spoke arms need a recess-floor-overlap clearance rule that is angular, not just radial. The hexagonal pattern goes last because it is the only feature whose safe parameter range is not knowable without a build-time sweep — it should not gate phases that don't depend on it.
**Delivers:** `hole_count`/`hole_d`/`hole_bolt_circle_d`, `spoke_arms`/`spoke_arm_width`/`spoke_hub_d`/`spoke_rim_wall`, `hex_cell_size`/`hex_wall_thickness` field groups; `_cut_body()`; per-cutout `check()` overlap rules against bore and recess; the hex-pattern phase opens with a build-time-vs-cell-count benchmark sweep (mirroring L17's methodology) before any cap formula is written into `calc.py`, and its own `Lxx` decision entry citing the measured numbers.
**Addresses:** Spoke-arm, lightening-hole, hexagonal-pattern cutouts (FEATURES.md's stated differentiator — no comparable tool offers this combination).
**Avoids:** Pitfall 2 (sequential cuts), Pitfall 5 (honeycomb cell-count cap discovered by timeout instead of computed), Pitfall 10 (validation gaps reaching OCCT instead of a 422).

### Phase 6: Composition pass
**Rationale:** `ARCHITECTURE.md` Q6 and `PITFALLS.md` Pitfall 4 both flag that per-feature phases prove selectors in isolation; only a dedicated composition phase exercises the full matrix (recess + each bore shape, recess + each cutout "cut through the recessed floor," keyway + hex bore attempt — refused per Known Conflict #5, cutout + cutout pairs) and is where the still-open cutout-family conflict rules (Known Conflict #4: spoke vs. hex, spoke vs. holes) get decided and written into `check()`.
**Delivers:** Composition test matrix; final re-run of the Phase 1 regression fixture; the milestone's Success Metric 2 "heaviest allowed configuration" build-time measurement (recess + hex pattern combined, against `SPUR_BUILD_TIMEOUT`); a fresh export-cost (STL/STEP triangle-count, gzip time) measurement at the heaviest cutout configuration, re-validating L19/L24's tables which were measured against v0.1's face topology only.
**Addresses:** PROJECT.md's explicit composition rule and both remaining Active requirements (composition, and the combined build-time measurement).
**Avoids:** Pitfall 8 (export-cost tables measured against a different face topology), Pitfall 4 (selectors proven only in isolation).

### Phase Ordering Rationale

- Phase 1 exists because Pitfall 4/Known Conflict #6 is a silent, no-error failure mode — it must be fixed before any feature that depends on generalized edge selection ships, not discovered by a later phase's manual inspection.
- Phases 2-3 (bore shapes) precede Phase 5 (body cutouts) because `ARCHITECTURE.md` Q1 shows bore-before-body keeps `_bore_rim_edges`'s selection scope free of competing near-axis edges; reversing the order reopens the exact selector-collision risk Phase 1 fixed.
- Phase 5's internal ordering (holes -> spokes -> honeycomb) is cost-ordered: cheapest-to-benchmark first, most build-time-uncertain last, so the one feature needing its own research spike doesn't block everything behind it.
- Phase 6 is last by definition — it is the only place the full composition matrix and the milestone's own "combined heaviest configuration" success metric can be measured, since it requires every other feature to exist first.
- Every phase that adds a `GearParams` field owns its own regression assertion at merge time (Pitfall 6) — this is not deferred to Phase 6, to avoid accumulating undetected default-drift across five phases.

### Research Flags

Needs deeper research during planning (`--research-phase`):
- **Phase 5 (hexagonal pattern sub-phase):** cell-count-vs-build-time relationship is genuinely unknown; STACK.md, ARCHITECTURE.md, and PITFALLS.md all independently flag this as requiring a measurement sweep before any cap formula is written — treat as its own research/benchmark task, not a standard geometry phase.
- **Phase 3 (keyway):** the depth-datum decision (Known Conflict #3) needs to be made and logged as an `Lxx` before implementation proceeds; not blocked on external research, but needs an explicit human decision captured before the phase plan is written.
- **Phase 4 (tip chamfer):** the "which reading of tip chamfer" product decision (Known Conflict #1) changes the phase's entire implementation approach and cost profile; resolve before planning, not during.

Phases with standard, well-documented patterns (research-phase likely unnecessary):
- **Phase 1:** the fix (compute circumradius vs. apothem correctly) is fully specified by ARCHITECTURE.md's Q2; no open questions.
- **Phase 2 (hex bore):** `Workplane.polygon(circumscribed=True)` is numerically verified; a small, well-bounded feature.
- **Phase 5 (lightening holes, spoke arms sub-phases):** `polarArray` pattern and `cut(*cutters)` batching are both verified APIs with clear precedent (`_cut_face_recesses`'s existing two-call pattern generalizes directly).

## Known Conflicts Across Research Files — Reconciled, Not Papered Over

**1. Tooth-tip chamfer implementation approach — unresolved, product decision required.**
`STACK.md` recommends reusing `Mixin3D.chamfer()` on position-selected tip edges (the same pattern the shipped `bore_chamfer` already uses) — low code cost, established idiom. `PITFALLS.md` (Pitfall 3) counters that this is the same operator family (`BRepFilletAPI_MakeChamfer`, built on the same machinery as `BRepFilletAPI_MakeFillet`) that L09 already measured at ~50x slower than an analytic construction on a many-toothed outline, and recommends extending the analytic 2D `_outline()` instead. Part of the disagreement is that "tooth-tip chamfer" is genuinely ambiguous: a 2D tip-corner chamfer built into the profile wire (only doable analytically in `_outline()`, cheap, matches L09's precedent) versus a true 3D deburring chamfer on the tooth edges at the end faces (only doable as a `Mixin3D.chamfer()` 3D edge operation, the STACK.md reading, unmeasured cost). `FEATURES.md` independently flags "chamfer vs. tip relief" as an unresolved naming question (though that specific ambiguity — chamfer vs. meshing-load tip relief — is resolved: tip relief is explicitly out of scope). **This research does not pick between the two chamfer readings** — it is a product decision with a real cost implication either way, and Phase 4 above should surface it explicitly before implementation, with a measured build-time number at 200 teeth required before either implementation is called done (per PROJECT.md's own "every new cut gets a measured build time" rule).

**2. The 0.1-0.2 x module tip-chamfer sizing range is an unsourced guess, not a convention.** `FEATURES.md` states explicitly that this range — which originated in the orchestrator's research prompt, not in any source — "was not independently found in any source located during this research; it should be treated as a plausible engineering guess worth validating with the human, not as a sourced convention." Carry it forward only as a candidate default to confirm with the human, never as a cited standard in field help text or documentation.

**3. Keyway depth datum — the highest-consequence open decision, now consolidated into one required decision.** `FEATURES.md` documents that DIN 6885/ISO R773 defines depth (`t1`/`t2`) as a radial cut depth measured from each surface (shaft OD or bore ID) to the keyway floor, while ANSI B17.1's S/T values are diametral gauge/inspection dimensions (distance to the *opposite* wall) that require `(shaft OD - S)` arithmetic to convert to an actual cut depth — genuinely different quantities, not just different numbers for the same quantity. `PITFALLS.md` (Pitfall 9) independently identifies a second, narrower ambiguity within the DIN/ISO convention itself: whether `keyway_depth` is measured from the bore's *nominal* radius (what the user typed into `bore_d`) or its *actual, clearance-adjusted* cut radius (`bore_radius()` = `(bore_d + bore_clearance) / 2`) — these differ by `bore_clearance / 2`, small but exactly the kind of silent, "close enough" error L08 forbids. **Consolidated decision required in Phase 3:** adopt the DIN 6885/ISO R773 convention (radial depth from the bore's actual cut surface to the keyway floor — the number a hobbyist would measure with calipers on the real part), state it explicitly in `keyway_depth`'s help text, do not accept or convert ANSI B17.1 S/T values in the same field, and prove it with a test that measures the *built solid's* keyway floor position against the stated datum (not just that the parameter round-trips) — this must be logged as a new `Lxx` decision entry, not left as an implicit implementation choice.

**4. Which cutout patterns may compose with each other on one part — open, a requirements-step decision.** `ARCHITECTURE.md` Q3 judges that spoke arms and lightening holes are "plausibly fine" together (holes could cut into spokes or gaps) but that spoke arms and hexagonal pattern together are "very likely a genuine conflict" — both want exclusive use of the same hub-to-rim annulus. `FEATURES.md`'s Feature Dependencies section leaves this fully open: "treat 'more than one cutout type on one part' as an open question for requirements, not assumed in scope." Neither file resolves it. **This must be decided explicitly in Phase 6 (composition pass) and written into `check()`** as named conflict rules, not inferred or left to whichever combination happens to build without erroring.

**5. Hex bore as an additive profile vs. a separate/replacing profile — open, a requirements-step decision.** `ARCHITECTURE.md` Q3 recommends the additive-field pattern, generalizing the existing `bore_flat` precedent (`bore_hex_flats: float = 0`, refused in combination with `bore_flat > 0` via `check()`), reasoning from L02/L05's flat-field assumptions and the milestone's composability requirement. `FEATURES.md`'s Feature Dependencies section frames the same question as still open — "keyway and hex should follow the same shape (an addition to the round bore, not a replacement of it) *unless* the requirements step decides hex fully replaces the round profile the way D-flat does." The architecture recommendation is directionally clear (additive, mutually exclusive with D-flat via `check()`), but both files agree this is formally a requirements-step decision, not something to silently assume in a phase plan — Phase 2 should confirm it explicitly rather than inferring it from the architecture recommendation alone.

**6. Silent zero-edge selection for a hex bore — confirmed defect, foundation-phase item, not merely a "watch out for."** `ARCHITECTURE.md` Q2 proves this is a real, concrete bug: `_bore_rim_edges`'s `lim = r_bore + 0.01` cutoff is correct for round/D-flat bores (every rim point lies within `r_bore` of the axis) but wrong for hex bores, whose vertices sit at the circumradius `w/sqrt(3) ~= 0.577w` — strictly larger than the across-flats/2 apothem the bore's "size" is expressed in. Every hex-vertex point fails the `hypot <= lim` test, `on_rim()` returns zero edges for every face, and `.chamfer(chamfer, None, [])` is a silent no-op in cadquery — not an error. The bore builds correctly and ships with no chamfer, with no warning, for every hex-bore request with `bore_chamfer > 0`. `PITFALLS.md` independently names this exact failure class as Pitfall 4 ("position-based edge selectors silently pick the wrong edges once topology changes") and flags it as the general risk every new end-face feature reintroduces. **This is Phase 1 work** (see Implications for Roadmap above), not a note to remember during Phase 2 — the fix (`calc.py`'s `bore_rim_limit(p)`, computing circumradius for hex) must land before hex bore is implemented, with a unit test asserting `len(_bore_rim_edges(...)) > 0` whenever `bore_chamfer > 0`, for every bore shape — a test that does not exist yet in `tests/test_model.py` today.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Every API claim verified directly against the installed `.venv` (`cadquery==2.8.0`) via `inspect.signature`/`inspect.getsource`, plus one numeric `BoundingBox()` check — not from documentation or memory. No dependency change needed, low uncertainty. |
| Features | MEDIUM | Keyway/hex dimensional data cross-checked across 3+ independent sources (DIN 6885/ISO R773 tables, ANSI B17.1 gauge-value docs) — MEDIUM. Body-cutout proportions and tip-chamfer sizing are correctly graded LOW: no engineering standard exists for spoke/hole/honeycomb dimensions or chamfer-vs-module ratios, and the research says so explicitly rather than presenting a plausible default as sourced. |
| Architecture | HIGH for anything grounded in the current tree (file:line citations throughout); MEDIUM where cadquery 2.8.0's installed API was checked but not run inside a full build; explicitly flagged LOW/judgment-call where a claim needs a phase-level benchmark (hex-cell build-time cap) rather than being derivable from source reading alone. |
| Pitfalls | MEDIUM-HIGH | Grounded in this repo's own code, the decision log (L03/L05/L08/L09/L18/L24), and a live check against installed `cadquery==2.8.0`. General OCCT boolean-robustness claims are corroborated by OCCT's own documentation and public CadQuery/FreeCAD issue trackers rather than verified against this project's own new geometry, since the new cuts don't exist in the tree yet — appropriately caveated as such throughout. |

**Overall confidence:** MEDIUM-HIGH — the technical foundation (stack, architecture, silent-failure risks) is verified at HIGH confidence against the actual codebase; the dimensional/proportional questions are honestly graded lower because several of them have no engineering standard to source, which is itself the most important and consistent finding across all four files (do not let an invented "sensible default" pass as researched convention).

### Gaps to Address

- **Keyway depth datum (Known Conflict #3):** not a research gap so much as a decision this project must make and own — resolve in Phase 3, log as a new `Lxx`, do not defer to composition testing.
- **Tip-chamfer implementation reading (Known Conflict #1) and its 0.1-0.2x module sizing (Known Conflict #2):** both need a human decision before Phase 4 planning; the sizing range specifically must not be cited as a sourced convention anywhere in the shipped help text.
- **Cutout-family composition rules (Known Conflict #4) and hex-bore-as-additive-vs-replacing (Known Conflict #5):** both are open requirements-step decisions the roadmapper/requirements step should resolve explicitly, not infer from the architecture recommendation alone — Phase 6 (composition) and Phase 2 (hex bore) respectively are where they must be locked in.
- **Hexagonal-pattern build-time-vs-cell-count relationship:** genuinely unmeasured; requires a dedicated benchmark sweep at the start of the hex-pattern sub-phase before any cap formula is written into `calc.py` — flagged consistently across STACK.md, ARCHITECTURE.md, and PITFALLS.md as the one number this research could not produce from source-reading alone.
- **Export-cost re-measurement (Pitfall 8):** L19's gzip-level table and L24's mesh-copy timing were measured against v0.1's face topology (few large faces); a honeycomb or many-hole gear's STL could land differently on that curve. Needs a fresh measurement at the heaviest v0.2 configuration before that phase is called done, not assumed to still hold.

## Sources

### Primary (HIGH confidence)
- `.venv/lib/python3.12/site-packages/cadquery/{cq.py,occ_impl/shapes.py}` — installed copy, version-matched to `requirements.txt`, read directly via `inspect` for `Workplane.polygon/rect/polarArray/rarray/circle/each/eachpoint/extrude` and `Shape.cut/_bool_op`, `Mixin3D.chamfer/fillet` signatures and source
- `src/spur/model.py`, `src/spur/calc.py`, `src/spur/params.py` — read in full; existing build order, `_bore_rim_edges`/`_groove_floor_edges`/`_cut_bore`/`_cut_face_recesses` patterns, `recess_radii()`/`root_fillet()`/`check()` split
- `src/spur/app.py`, `src/spur/pool.py` — cache key and executor-affinity mechanics
- `docs/architecture/decision_log.md` — L01-L25, cited by ID throughout all four research files
- `.planning/PROJECT.md` — v0.2 milestone scope, rules, success metrics (the milestone contract all four files target)

### Secondary (MEDIUM confidence)
- DIN 6885/ISO R773 keyway dimension tables — cross-checked across engineeringhardware.com, JW Winco PDF, Ganter Norm catalog PDF, nexusseals.com
- ANSI B17.1 S/T diametral-gauge convention — cross-checked across engineersedge.com and amesweb.info
- OCCT Boolean Operations user guides (old.opencascade.com, dev.opencascade.org) and the multi-argument-boolean performance note
- CadQuery issue trackers (#346, #1553) — edge-selection and boolean-robustness failure precedents

### Tertiary (LOW confidence, flagged as such in source files)
- Hex-bore-for-gears sizing — no authoritative standard located, commodity hex-stock size charts only (REV Robotics, generic wrench-size references)
- Body-cutout (spoke/hole/honeycomb) proportions — no DIN/ISO/AGMA standard exists; one academic paper (AIAC-2019-155) confirms these are treated as free optimization variables in the literature, not standardized
- Tip-chamfer size-vs-module ratio (0.1-0.2x) — orchestrator-prompt-originated, could not be independently sourced; carry only as an unvalidated candidate

---
*Research completed: 2026-09-25*
*Ready for roadmap: yes*
