# Phase 9: Keyway Bore - Context

**Gathered:** 2026-09-27
**Status:** Ready for planning

<domain>
## Phase Boundary

The second shaft-fit profile of v0.2, and the first feature that composes with an
existing bore shape instead of replacing it.

1. **The fields.** `keyway_width: float = 0` and `keyway_depth: float = 0` (mm, `0 = no
   keyway`, `ge` 0, `le` 200, step 0.05) join `GearParams`' Bore group, declared after
   `bore_flat` and before `bore_hex` (D-17). Flat additive fields like `bore_flat`, not a
   `bore_type` discriminator (research ARCHITECTURE.md Q3). There is no `keyway_clearance`
   field: `bore_clearance` is added to the keyway width, as it already is to the bore
   (REQ-keyway-bore). The CLI flags `--keyway-width`/`--keyway-depth`, the `/api/schema`
   entries and the form fields fall out of the generators (L02); the shareable URL carries
   them like any other field.
2. **The cut.** When both fields are `> 0` on a round or D-flat bore, `_build` cuts a
   rectangular slot **after** `_cut_bore` has cut and chamfered the bore (D-06): width
   `keyway_width + bore_clearance`, from inside the bore radially out to a flat floor at
   `bore_radius(p) + keyway_depth`, square floor corners, through the full face width
   (D-08), centred on **+Y** — 90° from the D-flat, which sits on +X (D-01). The bore's
   own chamfer is notched by the slot; **the keyway's three rim edges are sharp on every
   bore** (D-05). `_cut_bore`, `_bore_rim_edges` and `calc.bore_rim_limit` are untouched.
3. **The datum.** The keyway floor sits at radius `bore_radius(p) + keyway_depth` — the
   depth is measured from the **as-cut** bore wall, `(bore_d + bore_clearance) / 2`, the
   DIN 6885 / ISO R773 `t2` convention (D-14; decided by the human 2026-09-25 and confirmed
   2026-09-27). ROADMAP SC1 and REQ-keyway-bore currently write that wall as `bore_d/2 +
   bore_clearance`, off by `bore_clearance/2` (research PITFALLS.md Pitfall 9); the plan's
   first task amends the text (D-20). A new decision-log entry (L28) states the datum with
   its formula. A test measures the built solid's floor position against it.
4. **The rules**, all in `calc.check()` before any CAD work (08-03's if/elif chain): a
   keyway with `bore_hex > 0` is a 422 naming the fields; with `bore_d = 0` a 422 naming
   both (REQ-keyway-bore, D-13); a half-set keyway (one field zero, the other not) is a
   422 naming both (D-03); a keyway that leaves less than `MIN_WALL` of bore wall between
   the D-flat's corner and its own side is a 422 naming `keyway_width` and `bore_flat`
   (D-02); a keyway whose floor **corner** comes within `MIN_WALL` of the root circle is a
   422 naming `keyway_depth` and `keyway_width` (D-10); a keyway wider than the bore can
   carry is a 422 naming `keyway_width` and `bore_d`, at a bound measured on the kernel
   (D-11). **The face recess yields to the keyway** the way it yields to the hex corner:
   `calc.bore_mouth_limit(p)` learns the keyway's floor corner, `recess_radii()` keeps
   `MIN_WALL` from it and narrows or drops the recess with the existing warnings — never a
   422 (D-09; supersedes SC3's "or a recess wall" clause). The must-severity debt on the
   round bore's unchecked chamfer reach is folded in: refused past the measured failure
   point, naming `bore_d` and `bore_chamfer` (D-12).
5. **The numbers.** `DerivedDimensions` gains two fields — the keyway floor-to-opposite-
   wall distance (`bore_effective + keyway_depth`, what a pin-and-caliper check reads) and
   the effective keyway width (`keyway_width + bore_clearance`, what calipers read across
   the slot) — both `null` with no keyway (D-15); both land as web-UI rows and README rows
   this phase. The hex corner-to-corner diameter (REQ-bore-derived-numbers) and the hex rim
   chamfer (REQ-hex-rim-chamfer) were delivered by Phase 8 and are re-confirmed by the
   existing tests, not rebuilt.
6. **The measurement.** `make bench.build` runs a committed sweep file for the heaviest
   keyway configuration (L27 D-11/D-12's shape), recorded in a new `bench/RESULTS.md`
   section, every row inside `SPUR_BUILD_TIMEOUT=30s`.
7. **The fixture.** `tests/regression/pre_v0_2.json` passes unmodified — `git diff
   --exit-code` on it after every task (07 D-03, L26); 08-02's replay rule requires the two
   new derived fields to read `null` on every pre-v0.2 record.

Requirements: REQ-keyway-bore, REQ-keyway-composes-with-d-flat, REQ-keyway-wall-refused,
REQ-hex-rim-chamfer, REQ-bore-derived-numbers (the last two: hex edge shipped in Phase 8,
keyway edge here — REQUIREMENTS.md "Notes on bundled requirements").

**Not in scope:** a keyway on a hex bore (refused); a `keyway_angle` field (D-01); a
`keyway_clearance` field (REQ); chamfering the keyway's own edges (D-05, research Q2
option 1 — a named follow-up); filleted floor corners (D-08); a blind keyway; a bore-shape
selector in the web form (deferred to Phase 12's UI pass, idea filed — see Deferred
Ideas); standard-table keyway sizing (rejected, PROJECT.md); DIN example numbers in help
text (D-16); the composition matrix (Phase 12).

</domain>

<decisions>
## Implementation Decisions

### Placement and the D-flat
- **D-01:** **The keyway sits on +Y, 90° from the D-flat, one fixed position stated in a
  comment.** SC2's "intersects the flat" 422 is live; the opposite wall is always the
  round wall, so the derived floor-to-wall number is `bore_effective + keyway_depth`
  whether or not a flat exists; the default D-flat link composes (flat-to-axis 3.575 mm
  against a 1.575 mm half-width for a 3 mm key). Rejected: −X, opposite the flat (the 422
  becomes unreachable and the opposite wall becomes the flat — a second formula); a
  `keyway_angle` field (a third parameter on every interface, angle-dependent rules,
  not in REQ-keyway-bore). — **Reversibility:** costly — moving the position later changes
  the part every published keyway link produces (L05); the only safe undo is an additive
  angle field defaulting to 90°.
- **D-02:** **"Intersects the flat" means less than `MIN_WALL` of bore wall would remain
  between the D-flat's corner and the keyway's side** — a 422 naming `keyway_width` and
  `bore_flat`. The planner picks the exact measure (the distance along the bore wall from
  the flat's corner point to the foot of the keyway's side on the bore circle is the
  obvious one), probes the kernel's real boundary as 08 D-03 did, writes the measurement
  next to the rule and tests one step either side. Rejected: refusing only on geometric
  overlap (`w_eff/2 ≥ flat_eff − r_bore`) — a near-tangent sliver reaches the kernel after
  a timed build (research PITFALLS.md Pitfall 1).
- **D-03:** **A half-set keyway is a 422 naming both fields**: `keyway_width > 0` with
  `keyway_depth = 0`, or the reverse. The user asked for a keyway and gave one that cannot
  exist; no shareable link carries it (both default to 0). Rejected: treating it as off
  with a warning (08 D-02's pattern — it would build a part with no keyway from a link
  that asked for one).
- **D-04:** **`bore_flat` stays when a keyway is added.** `?keyway_width=3&keyway_depth=1.4`
  on the default parameters is a D-flat bore with a keyway (L05, REQ-keyway-composes-with-
  d-flat); a plain keyed round bore is `bore_flat=0`. Rejected: the keyway replacing the
  flat with a warning (08 D-01's pattern — contradicts the requirement as written).

### Chamfer and build order
- **D-05:** **The keyway's own three rim edges (two sides, floor) stay sharp on every
  bore; `bore_chamfer` applies to the round part's rim only** — research ARCHITECTURE.md
  Q2 option 2, and the only behaviour the pinned kernel delivers for the D-flat + keyway
  composition: chamfering the keyway's edges built an invalid solid on a D-flat bore in
  every variant tried, and on a round bore only when the recess hub cleared the corner by
  more than the chamfer plus `MIN_WALL` (`<specifics>`). Stated in the field help and
  README. Rejected: chamfered on round bores and sharp on D-flat (two behaviours for one
  field, its own measured bound, a warning naming the difference).
- **D-06:** **Build order: the rim is chamfered first, then the keyway slot is cut through
  it.** `_build` calls the unchanged `_cut_bore` (bore + chamfer through the shipped
  selector) and then a new step (e.g. `_cut_keyway`) that subtracts the slot. Measured
  valid for D-flat and round bores, at +Y and −X, with and without recesses; the one-shot
  chamfer on a keyway-first solid fails on a D-flat bore in every variant. Consequences:
  `calc.bore_rim_limit(p)` stays `bore_radius(p)` for a keyway bore (the selector runs
  before the keyway exists); `calc.bore_mouth_limit(p)` gains the keyway's floor corner,
  `sqrt((r_bore + keyway_depth)² + (w_eff/2)²)`, un-chamfered, as the farthest point the
  recess hub must clear (D-09). Rejected: cutting the keyway first and chamfering the arcs
  and the flat line in two separate operations (measured valid too, but a selector that
  must exclude the keyway's edges plus two kernel operations, for no behavioural gain).
- **D-07:** **SC4's proof is the pre-keyway selector count plus a built-solid test; SC4's
  wording is amended.** The matrix rows for round and D-flat × recess settings keep their
  exact counts with a keyway set (the keyway does not exist when the selector runs); a
  built-solid test proves the chamfer survived the slot and the keyway's edges are sharp
  (measured: 4.15 mm³ removed by the chamfer with the keyway vs 4.66 without; 178 faces /
  508 edges vs 172 / 490 on the default gear). 07 measured that a position selector on a
  *finished* solid finds 0 edges, so "an edge-count assertion … with and without a keyway"
  on the finished part is not a proof that can exist; the sentence is amended through the
  edit-phase tooling (D-20). Rejected: a second selector that identifies chamfer faces on
  the finished solid (a new selector to prove, research PITFALLS.md Pitfall 4, same
  evidence).
- **D-08:** **The slot runs the full face width, with a flat floor and square floor
  corners** — a rectangular prism from inside the bore to `r_bore + keyway_depth`, what
  the probes built. DIN 6885's small floor-corner radius is not modelled; the README says
  so. Rejected: filleted floor corners (a fixed radius or a new field, a new edge selector
  to prove, kernel risk, fit-irrelevant on a printed part).

### Refusals
- **D-09:** **The face recess yields to the keyway, as it yields to the hex corner (L27):**
  `bore_mouth_limit(p)` includes the keyway's floor corner, so `recess_radii()` keeps
  `MIN_WALL` from it and narrows or drops the recess with the existing warnings
  (cap-and-warn, L03). Measured reason: the DIN-6885-correct 3 × 3 key (`t2` 1.4) on the
  default 9 mm bore puts its corner 0.327 mm from the default recess hub wall — under
  `MIN_WALL` — so SC3 as written refuses the default gear with its own correct key. **This
  supersedes the "or a recess wall" clause of ROADMAP SC3 and REQ-keyway-wall-refused**;
  the root-circle refusal stands. Rejected: the 422 as written (naming `keyway_depth` and
  `recess_inner_d`/`recess_width`); a hybrid that yields when `recess_inner_d` is 0 and
  refuses when set (a new distinction — `recess_radii()` clamps an explicit
  `recess_inner_d` silently today for every bore shape). — **Reversibility:** costly — a
  keyway link that builds with a narrowed recess cannot become a refusal later without
  breaking it (L05).
- **D-10:** **Keyway vs the root circle: the floor corner, not the floor centreline.** A
  422 naming `keyway_depth` and `keyway_width` when
  `sqrt((r_bore + keyway_depth)² + (w_eff/2)²) + MIN_WALL > rf` — both fields set the
  corner, which is the nearest keyway point to the root. Never capped (REQ-keyway-wall-
  refused: a shallower keyway is a part the key does not fit). The planner measures the
  kernel's real boundary and tests one step either side (08 D-03). Rejected: the floor
  centreline `r_bore + keyway_depth` naming `keyway_depth` alone (under-counts the
  corner's reach).
- **D-11:** **A keyway wider than the bore can carry is a 422 naming `keyway_width` and
  `bore_d`, at a bound measured on the kernel** — the planner probes widths toward
  `bore_effective` on a small and a large bore and writes the failing ratio next to the
  rule with its measurement (08 D-03's method). Rejected: a fixed ratio such as
  `w_eff ≤ bore_effective / 2` (an opinion; no standard states a hard limit — ANSI's
  `w ≈ d/4` is a sizing rule of thumb).
- **D-12:** **The must-severity debt `docs/tech_debt/active/2026-09-26-round-bore-chamfer-
  reach-is-not-checked.md` is folded in** (its trigger — "when Phase 9 edits `check()`'s
  round branch" — fires here). One narrow task: measure where the kernel actually fails
  for a round and a D-flat bore near the root with its chamfer, refuse one step past that
  boundary naming `bore_d` and `bore_chamfer`, test one step either side. The rule sits
  at the measured failure point, **not** at `bore_mouth_limit(p) > rf − MIN_WALL`, so no
  link that builds today is refused (L05). If the boundary moves with tooth count such
  that no single rule keeps every building link building (L27 saw the hex fail 0.05 mm
  past the root at 19 teeth and build 0.30 mm past at 40), the planner surfaces that
  rather than choosing. Logged in L28 or its own entry; the debt file flips to resolved
  and moves to `docs/tech_debt/resolved/` in the same commit as the fix. Rejected:
  refusing at `rf − MIN_WALL` (refuses round links that build today with a thin wall);
  deferring again to Phase 12.
- **D-13:** Pre-decided by REQ-keyway-bore and 08 D-01, recorded here so the plan carries
  them: **a keyway with `bore_hex > 0` is a 422 naming `bore_hex` and the keyway fields;
  a keyway with `bore_d = 0` is a 422 naming `bore_d` and the keyway fields.** Both live
  in `check()` before the per-shape branches (they decide which branch applies). Which
  keyway fields each sentence names when only one is non-zero is the planner's.

### Numbers, help text, the datum
- **D-14:** **The datum is the as-cut bore wall, `bore_radius(p) = (bore_d +
  bore_clearance) / 2`; the keyway floor is at `bore_radius(p) + keyway_depth`.** ROADMAP
  SC1 and REQ-keyway-bore write the wall as `bore_d/2 + bore_clearance` — a point
  `bore_clearance/2` outside the wall that exists on the part; the plan amends both texts
  (D-20) and L28 states the formula. The built-solid test reads the slot's floor back from
  the kernel and asserts its radius against the formula within `TOL`, and the slot's width
  against `keyway_width + bore_clearance`. Rejected: keeping the text's formula literally
  (nobody can measure it). — **Reversibility:** costly — the datum is the published
  meaning of `keyway_depth`; changing it later re-cuts every keyed part from every
  existing link (L05).
- **D-15:** **Two new `DerivedDimensions` fields**, both `float | None`, `null` with no
  keyway, rounded to 3 dp at construction (Phase 4 D-10), `unit: mm`: the **floor-to-
  opposite-wall distance** (`bore_effective + keyway_depth` — the pin-and-caliper number,
  ROADMAP SC5, REQ-bore-derived-numbers) and the **effective keyway width**
  (`keyway_width + bore_clearance` — the fit number, 08 D-05's rule that the fit dimension
  must appear in the response). Names are the planner's. Both land as `DIMS` rows in the
  web UI and as README rows this phase (08 D-06/D-10). The 21 existing fields keep their
  names, types and values; `disallow_any_explicit` stays on with no suppressions. Rejected:
  the floor-to-wall number alone (the as-cut slot width would appear nowhere).
  — **Reversibility:** costly — published `/api/info` fields under L21's typed contract.
- **D-16:** **Help text states the convention and names no numbers.** `keyway_depth`: the
  depth from the as-cut bore wall (clearance included) to the keyway floor — the DIN 6885
  / ISO R773 `t2` convention — with the warning that ANSI B17.1's "T" is measured across
  the bore and is a different quantity; `keyway_width`: `bore_clearance` is added; both:
  `0 = no keyway`. The CLI prints the same sentences; exact wording is the planner's
  (L15). Rejected: citing one DIN 6885 example row ("8–10 mm shaft: 3 mm wide, t2 1.4")
  even as an example — a looked-up number someone cuts metal to (L08); the hex's stock
  sizes (08 D-08) were not standard values.
- **D-17:** **`keyway_width` and `keyway_depth` are declared after `bore_flat` and before
  `bore_hex`**, so the round-profile modifiers stay together (`bore_d`, `bore_flat`,
  keyway), then the replacing profile (`bore_hex`), then `bore_clearance` and
  `bore_chamfer`; form and CLI order follow (L02). `ge` 0, **`le` 200 like the rest of the
  bore family** (08 D-07: one family, one bound; the measured rules refuse anything too
  large), step 0.05, titles the planner's. Rejected: appending after `bore_hex`.

### Process
- **D-18:** The phase runs on **`gsd/phase-09-keyway-bore`**, cut this session from
  `origin/main` `b522044` (PR #9's squash), and lands via `make pr.land PR=N` (L22/L25).
  `.planning/` rides the same PR.
- **D-19:** Commits are plain `git commit` with explicitly staged files, never `git add
  -A`: the pre-commit hook runs `make verify` and the gsd SDK commit wrapper kills it at
  30 s (`docs/tech_debt/active/2026-09-25-gsd-commit-timeout-kills-cold-verify-hook.md`).
  Run `make verify` once at session start to warm the page cache.
- **D-20:** **The plan's first task amends the phase texts through the edit-phase tooling
  with one human confirmation** (08-01's pattern), never a direct write: ROADMAP SC1 and
  REQ-keyway-bore's `bore_d/2 + bore_clearance` → the as-cut wall `(bore_d +
  bore_clearance)/2` (D-14); ROADMAP SC3 and REQ-keyway-wall-refused lose "or a recess
  wall" (D-09); ROADMAP SC4's "proven by an edge-count assertion for every bore shape,
  with and without a keyway" → the pre-keyway count plus a built-solid proof (D-07). The
  verifier then checks against these decisions, not the superseded sentences.

### Claude's Discretion
- **Names:** the field titles (D-17), the two derived fields (D-15), the slot step in
  `model.py` (D-06), the sweep file, and whether D-12's rule shares L28 or gets its own
  entry — shapes locked, names and sentences are the planner's and are the product (L15).
- **The flat-rule measure (D-02)** and the exact kernel boundary for it, D-10 and D-11 —
  all measured, written next to the rule, tested one step either side.
- **Refusal and warning sentences**, and which keyway field each of D-13's two sentences
  names when only one is non-zero.
- **`bore_mouth_limit(p)`'s keyway branch:** the farthest end-face point of a keyway bore
  is the un-chamfered floor corner; whether the function takes the maximum of the
  chamfered rim reach and the corner, or the planner introduces a sibling helper, is open
  — the constraint is that `recess_radii()` clears the corner plus `MIN_WALL` and that the
  round and D-flat floats without a keyway are unchanged (the fixture stays byte-
  identical).
- **Selector matrix rows:** keyway × {round, D-flat} × recess settings added to
  `test_each_edge_selector_picks_exactly_its_own_edges`, expecting the unchanged pre-
  keyway counts (`Counter({"CIRCLE": 2})` / `Counter({"CIRCLE": 2, "LINE": 2})` for the
  rim; unchanged floor counts) — the keyway does not exist when the selector runs. Note
  that a keyway row that narrows the recess also moves `r_in`, which the existing
  invariant test already covers per shape.
- **The built-solid tests (D-07, D-14):** exact form. Read the slot's floor face or its
  rim vertices back from the kernel; assert floor radius `= bore_radius(p) + keyway_depth`
  and slot width `= keyway_width + bore_clearance` within `TOL`; assert the chamfer
  survived (face/edge count or the volume delta) and the keyway edges are sharp.
- **Sweep rows (L27 D-11/D-12's shape, reused unchanged):** 200 teeth × module {1.75,
  10} × recess {both, none} × chamfer {0.4, the maximum D-12's rule allows} × the
  heaviest keyway the rules allow on the largest `bore_d` they allow — the planner
  decides the rows; every row inside `SPUR_BUILD_TIMEOUT=30s`; a row over budget halts
  for a human decision, never a silent narrowing (08 D-11).
- **Fuzzy booleans (`tol=`):** not needed — the slot's faces sit inside the bore or
  inside material, and `recess_radii()` keeps `MIN_WALL` between the corner and the
  recess by construction (the same reasoning L27 recorded); the planner confirms this in
  the plan rather than adding a `tol=` nobody measured.
- **Hex re-confirmation (REQ-hex-rim-chamfer, REQ-bore-derived-numbers):** the existing
  hex matrix rows and `test_a_hex_bore_measures_the_across_flats_and_corners_it_reports`
  are the proof; no new hex work — the plan cites them.
- **README:** the feature bullet, two parameter rows carrying D-16's sentences, a keyed
  example (`spur export … --keyway-width 3 --keyway-depth 1.4`) that the tests run, and
  one sentence each on the datum, the sharp slot edges and the unmodelled floor radius.
  The new example is a post-v0.2 set and stays out of the regression corpus (07 D-05).
- **`bore_clearance`'s help text** — recommend extending "Added to bore, flat and hex
  across-flats" with the keyway width (a description change touches `/api/schema`, nothing
  the fixture pins).
- **ROADMAP's `**Requirements**:` line for Phase 9** wraps onto a second line, and
  `init.plan-phase` reads only the first (3 of 5 IDs). Unwrapping it is a one-line edit
  the D-20 task can carry; the planner and checker are handed all five IDs regardless.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and requirements
- `.planning/ROADMAP.md` — "### Phase 9: Keyway Bore" (goal, the five success criteria;
  SC1's datum parenthetical, SC3's recess clause and SC4's edge-count sentence are
  superseded by D-14, D-09 and D-07 — amended by D-20); "### Phase 12" SC1 (keyway × hex
  attributed here); "## Process Notes (v0.2)"
- `.planning/REQUIREMENTS.md` — REQ-keyway-bore (the hex × keyway 422 sentence; the datum
  parenthetical D-20 amends), REQ-keyway-composes-with-d-flat, REQ-keyway-wall-refused
  (the recess clause D-20 amends), REQ-hex-rim-chamfer and REQ-bore-derived-numbers
  ("Notes on bundled requirements": hex edge shipped in Phase 8), REQ-hex-bore (the
  relocated 422), REQ-three-interfaces-extended and REQ-measured-build-time (Phase 12's
  bar met early, as 08 D-06/D-10/D-11 did), "## Out of Scope"
- `.planning/PROJECT.md` — "Current Milestone: v0.2" (keyway: explicit width, depth and
  clearance; no standard-table lookup), "Rules this milestone lives by", "Success Metric
  (Milestone v0.2)"

### The research behind the datum, the chamfer question and the rules
- `.planning/research/ARCHITECTURE.md` — **Q2** (the keyway paragraph: options 1 and 2,
  option 2 chosen by D-05; `_groove_floor_edges` is unaffected), **Q3** (flat additive
  fields — keyway composes with the base shape), **Q4** (the rules table: `keyway_width`
  range and `keyway_depth` vs the root as refusals)
- `.planning/research/FEATURES.md` — "## Standards Cited — Keyway" (the DIN 6885 / ISO
  R773 `t2` table and why ANSI B17.1's T is a different quantity; D-16 cites the
  convention and none of the numbers), "Feature Dependencies" (keyway requires
  `bore_d > 0`, conflicts with hex)
- `.planning/research/PITFALLS.md` — **Pitfall 1** (tangency: why D-02 keeps `MIN_WALL`
  and why no `tol=` is needed), **Pitfall 4** (position-based selectors: D-06 keeps the
  selector ahead of the keyway), **Pitfall 9** (the datum: nominal vs as-cut wall — D-14
  picks the as-cut wall and the text is corrected)
- `.planning/research/SUMMARY.md` — Known Conflict #3 (the consolidated datum decision),
  "Phase 3: Keyway bore" (the built-solid floor test)

### The foundation this phase stands on
- `.planning/phases/08-hex-bore/08-CONTEXT.md` — D-01 (the keyway 422 moved here), D-03
  (measured bounds, refuse-vs-cap), D-05/D-06 (derived fields and UI rows), D-07/D-08
  (field placement, help text with no standard), D-09 (no conditional form behaviour —
  why the bore-shape selector is deferred), D-11/D-12 (the sweep), D-13/D-14 (process),
  "Deferred Ideas" (conditional form fields — the trigger this phase's deferral names)
- `.planning/phases/08-hex-bore/08-01-SUMMARY.md` — the amendment task's shape D-20 copies
  (edit-phase tooling, one human confirmation, milestone-scope check before/after)
- `.planning/phases/08-hex-bore/08-02-SUMMARY.md`, `08-03-SUMMARY.md`, `08-04-SUMMARY.md`
  — frontmatter `provides` / `patterns-established`: `bore_rim_limit`/`bore_mouth_limit`
  as the shape-general pair every consumer reads; `check()`'s if/elif shape-branch; the
  additive replay rule; `bench/build_time.py`'s report shape
- `.planning/phases/07-foundation-generalized-edge-selection-regression-fixture/07-CONTEXT.md`
  — D-03 (fixture regeneration rule), D-05 (closed corpus), D-15–D-18 (guard contract,
  exact counts in tests, the seam), `<specifics>` ("on the finished solid the same
  selectors find 0" — why D-07 counts before the keyway)
- `docs/architecture/decision_log.md` — L02 (one model, three interfaces), **L03** (cap
  vs refuse — D-09's branch), **L05** (defaults never rescale — D-04, D-12's line), L08
  (no plausible number — D-16), L15 (sentences are the product), L21 (typed responses),
  **L26** (the fixture and the selector rule), **L27** (the hex: replaces, measured root
  limits, `bore_mouth_limit`, the sweep). Append-only; L28 is this phase's.
- `CLAUDE.md` — the two standing rules, the gate, "measured, not estimated", the debt
  lifecycle D-12 follows, `make` command surface
- `docs/CODING_VALUES.md` — comments carry the measurement; `calc.py` never imports the
  kernel; vendor types stop at `model.py`; validate once at the `GearParams` boundary

### Code this phase edits or reads
- `src/spur/params.py` — the Bore group (54–68: `bore_d`, `bore_flat`, `bore_hex`,
  `bore_clearance`, `bore_chamfer` — the keyway fields go between `bore_flat` and
  `bore_hex`), `_f()` (17–23), `_feasible` (84–94)
- `src/spur/calc.py` — `bore_radius` (57, the datum), `bore_rim_limit` (67–82, unchanged
  for a keyway), `bore_mouth_limit` (85–97, gains the keyway corner), `recess_radii`
  (100–121, reads `bore_mouth_limit`), `check` (155–219: the hex branch 176–201, the
  round branch 202–208 where D-02/D-10/D-11/D-12 join, the shape-independent chamfer rule
  209–211), `DerivedDimensions` (231–299), `derive` (302–397: the hex warning 334–342,
  the optional fields 387–389), `MIN_WALL` (15)
- `src/spur/model.py` — `_cut_bore` (195–219, untouched), `_bore_rim_edges` (252–281,
  untouched), `_build` (286–295, the keyway step goes after `_cut_bore`), `BORE_RIM_SLACK`
  (51), `TOL` (50), `_cut_face_recesses` (174–192)
- `src/spur/static/app.js` — `DIMS` (13–30, two rows), `gearQuery` (only non-default
  fields are sent), `renderInfo` (`null` rows are skipped)
- `src/spur/app.py`, `src/spur/cli.py` — need no edits: fields fall out of the schema
  (08-02 proved it)
- `tests/test_model.py` — `test_each_edge_selector_picks_exactly_its_own_edges` (47–125;
  rows 50–78 are the shape the keyway rows copy),
  `test_a_hex_bore_measures_the_across_flats_and_corners_it_reports` (159, the built-
  solid measurement pattern D-14's test copies), `test_the_largest_hex_each_root_rule_
  allows_builds` (217–225, the one-step-inside pattern), `test_a_recess_at_its_hub_
  clearance_keeps_min_wall_from_the_chamfered_bore_mouth` (242–264, gains a keyway row)
- `tests/test_calc.py` — `test_infeasible_parameters_name_their_fields` (98, the 422
  shape every new refusal joins), the hex tests (121–221: the refuse-one-step-past /
  build-one-step-inside pattern), `test_default_dimensions` (22, the L05 tripwire)
- `tests/test_api.py`, `tests/test_cli.py` — a keyed link through each interface; the
  422s naming the fields; the README example as a test
- `tests/regression/` — `pre_v0_2.json` (byte-unchanged), `test_pre_v0_2.py` (the
  additive-null rule from 08-02)
- `bench/build_time.py`, `bench/sweeps/hex_bore.json` (the sweep file shape), `bench/
  RESULTS.md` "Hex bore build and export time (Phase 8, D-11)" (the section shape);
  `Makefile` `bench.build` (121–124, `SWEEP=`), `fixture.regen` (138)
- `README.md` — line 11 (feature bullet), 107–108 (examples), 130–136 (refusals and
  warnings prose), 151–155 (bore parameter rows)
- `docs/tech_debt/active/2026-09-26-round-bore-chamfer-reach-is-not-checked.md` — D-12
  folds it in; `docs/tech_debt/INDEX.md` — the row moves to Resolved in the fix commit
- `docs/ideas/2026-09-27-bore-shape-selector-in-the-web-form.md` — the deferral filed
  this session (not for this phase)

### Process
- `docs/HOW_TO_DEVELOP.md` §6/§8 — phase branch, PR, `make pr.land`
- `docs/tech_debt/active/2026-09-25-gsd-commit-timeout-kills-cold-verify-hook.md` — D-19
- `docs/tech_debt/active/2026-09-26-ci-resolves-the-kernel-the-fixture-pins.md` — what a
  red fixture can mean besides a Phase 9 bug

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `_build`'s step order (blank → recesses → bore) and `_cut_bore`'s chamfer through
  `_bore_rim_edges` — the keyway is one more step after them; nothing in the selector
  path changes (D-06).
- `calc.bore_mouth_limit(p)` — already the one place `recess_radii()` reads the bore's
  farthest end-face reach; the keyway corner joins it (08-02's pattern: "a later bore
  profile only has to extend these two functions, not every caller").
- `calc.check()`'s `("message", ("field", ...))` tuples, `params._feasible`, and
  `test_infeasible_parameters_name_their_fields` — every D-02/D-03/D-10/D-11/D-12/D-13
  rule is one more tuple; the wire shape is proven.
- `derive()`'s `r3()` and the `x if cond else None` idiom for optional fields (D-15);
  08-02's replay rule already requires new fields to read `null` on old records.
- `app.js` `DIMS` — a two-line addition per field; `renderInfo` skips `null`.
- `bench/build_time.py` + `SWEEP=` — the sweep is a JSON file and a `make` invocation.
- `tests/test_model.py`'s matrix and the hex built-solid measurement test — the row and
  test shapes the keyway copies.
- The 08-01 amendment task (edit-phase tooling, one confirmation, scope check) — D-20's
  template.

### Established Patterns
- A bound is measured on the pinned kernel and written next to the rule before the rule
  is written; the rule is tested one step either side (L27, 08 D-03) — D-02, D-10, D-11,
  D-12 all follow it.
- Refuse a direct conflict naming the fields; cap and warn a trimmable wish; never a
  plausible number (L03, L08) — D-09 sorts the recess into "wish", D-10 the keyway into
  "conflict".
- A per-shape rule lives in its own `check()` branch; shape-independent rules stay
  outside (08-03).
- Numbers the fixture pins never move in a feature commit; `git diff --exit-code
  tests/regression/pre_v0_2.json` after every task (L26).
- Sentences (help, warnings, refusals) are the product; the planner writes them (L15).
- One phase = one branch = one PR = one squash; plain `git commit`, explicit files.

### Integration Points
- `src/spur/params.py` → two fields between `bore_flat` and `bore_hex`.
- `src/spur/calc.py` → the keyway corner in `bore_mouth_limit`; D-02/D-03/D-10/D-11/D-12/
  D-13 in `check()`; two fields in `DerivedDimensions` and `derive()`.
- `src/spur/model.py` → the slot step after `_cut_bore` in `_build`; nothing else.
- `src/spur/static/app.js` → two `DIMS` rows.
- `tests/` → matrix rows, the built-solid datum/chamfer test, calc unit tests per rule,
  API/CLI links and 422s, the README example as a test.
- `bench/` → the sweep file; `bench/RESULTS.md` → the section.
- `README.md` → bullet, rows, example, three sentences; `.planning/REQUIREMENTS.md` and
  ROADMAP SC1/SC3/SC4 → D-20's amendments; `docs/architecture/decision_log.md` → L28;
  `docs/tech_debt/` → D-12's resolution.

</code_context>

<specifics>
## Specific Ideas

Probed on the pinned kernel (`cadquery==2.8.0`, `cadquery-ocp==7.9.3.1.1`, `.venv`
Python 3.12, 2026-09-27, at `b522044`) — planning evidence, to be re-measured in the plan.
The slot was a rectangular prism from the axis to `r_bore + depth`, width `w + 0.15`,
through the face width, rotated to the stated angle; the DIN 6885 8–10 mm row (3 × 3 key,
`t2` 1.4) was used because the default bore is 9 mm.

- **Default gear:** `r_bore` 4.575, `rf` 14.4375, recess `(r_in, r_out)` = (6.506,
  12.506), flat-to-axis `flat_eff − r_bore` = 3.575. Keyway 3 × 1.4: floor at 5.975,
  **corner at 6.179, 0.327 mm from the recess hub wall** (`MIN_WALL` 0.4); floor-to-
  opposite-wall 10.550; corner + `MIN_WALL` = 6.579 against `rf − MIN_WALL` = 14.037. A
  4 × 1.8 key: corner 6.704, **inside** the default recess by 0.198 mm.
- **One-shot chamfer after the keyway, D-flat bore, arcs + flat line selected (6
  edges: 4 `CIRCLE`, 2 `LINE`): `BRep_API: command not done`** in every variant — recess
  on or off, depth 1.4 or 0.5, chamfer 0.4 or 0.2, keyway at +Y or −Y, `recess_inner_d`
  moved to 14.4. Arcs only (4 edges): valid. Flat line only (2 edges): valid. The
  unchamfered D-flat + keyway solid: valid (172 faces / 494 edges).
- **One-shot chamfer after the keyway, round bore, arcs only (4 `CIRCLE`): valid.**
- **Chamfering the keyway's own edges too** (round: 10 edges, 4 `CIRCLE` + 6 `LINE`):
  valid with no recess, and with the recess when the corner sat 1.192 mm from the hub
  wall (depth 0.5); **failed at 0.327 mm** (depth 1.4). D-flat (12 edges): an invalid
  solid with no exception, at depth 0.5 and 1.4, with the recess moved or not.
- **Chamfer first, then cut the keyway** (the shipped `_cut_bore`, then the slot):
  **valid every time** — D-flat at +Y and −X (178 faces / 508 edges, volume 4416.521
  mm³ against 4420.668 unchamfered — the chamfer removed 4.15 mm³, vs 4.66 mm³ on the
  default gear without a keyway), round at +Y and −X (175 / 501, 4387.212), D-flat with no
  recess (166 / 488). Two separate chamfer operations after the keyway (arcs, then the
  flat line) were also valid (182 / 520) — rejected in D-06 as the more complex route.
- **Rim-edge counts the matrix keeps with a keyway** (the selector runs before the
  slot): round 2 (`CIRCLE`), D-flat 4 (`CIRCLE` + `LINE` per face), hex 12 (`LINE`) —
  unchanged from L26/L27.
- Build times through the probe path: 0.40–0.58 s per default-size gear with the
  keyway; the 200-tooth heavy rows are the sweep's job.
- Phase 8's numbers this phase builds on: heaviest hex row 5.08 s of 30 s at 200 teeth;
  `make verify` warm with the fixture ~48 s (08 D-14).

</specifics>

<deferred>
## Deferred Ideas

- **A bore-shape selector (dropdown) in the web form** — raised by the human this
  session ("we have round, D-flat, hex and keyway; a dropdown to select the bore type").
  Deferred to Phase 12's UI pass (`UI hint: yes`), where the full v0.2 form — four bore
  shapes and three cutout patterns — can be judged at once; it conflicts with L27's flat
  `bore_hex` field, 08 D-09's schema-driven form and research Q3's no-discriminator rule,
  and the keyway is not a fourth type but a modifier of round and D-flat. Filed as
  `docs/ideas/2026-09-27-bore-shape-selector-in-the-web-form.md`; the viable shape if it
  is taken is a UI-only select that still sends the flat fields (superseding D-09 with an
  `Lxx`), not a model discriminator (an L05 contract change).
- **A `keyway_angle` field** — rejected for this phase in D-01 (scope); the L05-safe route
  if a real shaft needs it is an additive field defaulting to 90°.
- **Chamfering the keyway's own edges** (research Q2 option 1) — D-05 keeps them sharp;
  the kernel evidence says it is deliverable on a round bore only, with extra recess
  clearance, and not on a D-flat bore with a one-shot chamfer.
- **Filleted keyway floor corners** (DIN 6885's radius) — D-08; a fixed radius or a
  field, if a real key ever needs it.
- **A DIN 6885 example row in help text** — rejected in D-16, recorded so it is not
  re-derived.
- **A hybrid recess rule** (yield when `recess_inner_d` is 0, 422 when set) — rejected in
  D-09; revisit only if the recess's own contract changes for every shape.
- **A blind keyway** (not through the full face width) — nobody asked; D-08.

</deferred>

---

*Phase: 09-keyway-bore*
*Context gathered: 2026-09-27*
