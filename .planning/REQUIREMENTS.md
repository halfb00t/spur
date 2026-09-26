# Requirements: spur — milestone v0.2 Fit to Shaft

**Defined:** 2026-09-25
**Core Value:** A number this tool prints is a number someone will cut metal to — every
dimension is computed honestly or reported as a warning, never guessed (L08).

Scope fixed in `PROJECT.md` ("Current Milestone: v0.2 Fit to Shaft") and refined by the
four research files under `.planning/research/` (`SUMMARY.md` is the entry point). The
four product decisions the research left open were taken by the human on 2026-09-25 and
are baked into the wording below: the tooth-tip chamfer is an end-face edge break on the
tip arcs; keyway depth is measured from the as-cut bore wall; exactly one cutout pattern
per part; a hex bore replaces the round profile.

REQ-IDs continue the project's `REQ-slug` convention (`milestones/v0.1-REQUIREMENTS.md`).

## v0.2 Requirements

### Bore profiles

- [ ] **REQ-keyway-bore**: User can cut a keyway into the bore by setting `keyway_width`
  and `keyway_depth` in mm (0 = no keyway). Depth is measured radially from the **as-cut
  bore wall** (`bore_d/2 + bore_clearance`) to the keyway floor — the DIN 6885 / ISO R773
  `t2` convention — and the field help states this and warns that ANSI B17.1's "T" is a
  gauge dimension across the bore, not a depth. `bore_clearance` is added to the keyway
  width as it already is to the bore. No standard-table sizing anywhere: help text may
  cite DIN 6885 ranges as examples but never fills a value. A keyway with `bore_d = 0` is
  a 422 naming both fields.
- [ ] **REQ-keyway-composes-with-d-flat**: A keyway and a D-flat can coexist on one bore
  (placement rule decided in the phase); a keyway that would intersect the flat is a 422
  naming both fields.
- [ ] **REQ-keyway-wall-refused**: A keyway whose floor would come within `MIN_WALL` of
  the root circle or of a recess wall is a 422 naming `keyway_depth` and the conflicting
  dimension — refused, not capped, because a shallower keyway is a part the key does not
  fit.
- [ ] **REQ-hex-bore**: User can make the bore a regular hexagon by setting `bore_hex`
  (across-flats, mm, 0 = off). The hexagon **replaces** the round profile: `bore_d` does
  not apply to a hex bore, and the response's `warnings` say so when `bore_d` is also
  non-zero (its default is non-zero, so a shareable link that only adds `bore_hex` still
  works). `bore_clearance` is added across the flats. `bore_hex` together with `bore_flat`
  or a keyway is a 422 naming the fields.
- [ ] **REQ-hex-rim-chamfer**: `bore_chamfer` chamfers all six rim edges of a hex bore on
  both faces, and both the arc and the straight rim edges of a keyway bore's round part.
  The rim edge selector is generalised per bore shape — today it selects by a scalar
  radius (`r_bore + 0.01`) and would silently select zero edges on a hex bore.
- [ ] **REQ-bore-derived-numbers**: `DerivedDimensions` reports the measurable numbers of
  the new profiles — the keyway floor-to-opposite-wall distance (what a pin-and-caliper
  check reads) and the hex corner-to-corner diameter — `null` when the feature is off.

### Body cutouts

- [ ] **REQ-spoke-cutout**: User can cut spoke arms by setting `spoke_count` (0 = off),
  `spoke_width`, `hub_d` and `rim_wall`: N straight arms between a hub ring and a rim
  ring, the sectors between the arms cut through the full face width.
- [ ] **REQ-hole-cutout**: User can cut lightening holes by setting `hole_count` (0 =
  off), `hole_d` and `hole_circle_d`: N equal round holes evenly spaced on a bolt circle,
  through the full face width.
- [ ] **REQ-honeycomb-cutout**: User can cut a honeycomb web by setting `hex_cell`
  (cell across-flats, mm, 0 = off) and `hex_wall`: hexagonal through-holes fill the web
  between the hub wall and the rim wall. The cell count is derived and reported. When the
  derived count exceeds the measured build-time cap, the cell size is raised to the
  smallest size that fits and a warning names the requested and the applied size; cells
  are never silently dropped, and the cap is analytic (from a measured per-cell cost), so
  the same link yields the same count on every machine.
- [ ] **REQ-one-cutout-pattern**: Exactly one cutout pattern per part. Two non-zero
  pattern selectors (`spoke_count`, `hole_count`, `hex_cell`) is a 422 naming both fields.
- [ ] **REQ-cutout-conflicts-refused-early**: A cutout that would breach the hub wall
  (bore + bore chamfer + `MIN_WALL`) or the rim wall (root circle − `MIN_WALL`), or whose
  holes or arms overlap each other, is refused **before any CAD work starts**: 422 on the
  API, exit 2 on the CLI, the same message naming the fields — validated in `calc.py`,
  never a build error after a timed build.
- [ ] **REQ-cutout-composes**: Any cutout composes with face recesses (it cuts through the
  recessed floor, and the floor fillet remains on the floor edges that survive — proven
  by a test that counts the filleted edges) and with any bore profile (round, D-flat,
  keyway, hex).
- [ ] **REQ-cutout-derived-numbers**: `DerivedDimensions` reports the thinnest remaining
  wall on the hub side and on the rim side, and the honeycomb cell count actually cut —
  `null` when no cutout is set.

### Tooth-tip chamfer

- [ ] **REQ-tip-chamfer**: User can break the tooth-tip edges by setting `tip_chamfer`
  (mm, 0 = off): an edge-break chamfer on the tooth-tip arc edges at both end faces,
  selected by position; flanks, root fillets, bore and cutouts are untouched and the
  outside diameter is unchanged. No sizing guidance in help text unless it is sourced
  (the "0.1–0.2 × module" figure floated during research has no source).
- [ ] **REQ-tip-chamfer-capped**: A chamfer larger than the tip land allows is capped and
  reported in `warnings` (trimmable, L03). The chamfer operator's cost at the heaviest
  allowed configuration (maximum teeth × maximum chamfer) is measured against
  `SPUR_BUILD_TIMEOUT` and recorded; if it cannot fit, the cap is lowered and the number
  published — the cost is never hidden.

### Contract (cross-cutting)

- [ ] **REQ-defaults-off-regression**: Every new parameter defaults to off. A regression
  fixture proves that every pre-v0.2 parameter set — the defaults, every existing test's
  parameters, and the README's example links — yields identical `DerivedDimensions` (all
  19 fields) and an identical solid volume and bounding box after **each** phase. Export
  bytes are not compared: OCCT export is not byte-reproducible (L24).
- [ ] **REQ-three-interfaces-extended**: Every new parameter is on the web form (in its
  own group), the API query and the CLI flags from the one `GearParams` model,
  round-trips through the shareable URL, appears in `/api/schema`, and `spur info` /
  `spur export` print the same numbers and errors as the API.
- [ ] **REQ-measured-build-time**: A recorded build time, plus fine-quality STL and STEP
  export time inside the admission slot, per feature at its heaviest allowed
  configuration — including a recess combined with each cutout pattern, and the honeycomb
  at its cap — in `bench/RESULTS.md`, inside `SPUR_BUILD_TIMEOUT`. The honeycomb cap and
  the tip-chamfer cap come from that sweep (L17-style), not from inspection.
- [ ] **REQ-derived-dimensions-additive**: The 19 existing `DerivedDimensions` fields keep
  their names, types and values; new fields are `null` when their feature is off; mypy
  `disallow_any_explicit` stays on with no suppressions (L21).
- [ ] **REQ-edge-selection-proven**: Chamfer and fillet edge selectors never silently
  select zero or the wrong edges. A test asserts the selected-edge count for every bore
  profile and every cutout pattern, with and without recesses; a selector that finds
  nothing while its feature is on raises a build error rather than shipping an
  unchamfered or unfilleted part.

## Future Requirements

Deferred to a later milestone. Tracked, not in this roadmap.

### Gear family (v0.3 candidates)

- **REQ-helical-gear**: helix angle; re-derives module (normal vs transverse), span,
  centre distance and the mate — one phase of its own, first of the family.
- **REQ-internal-gear**: inverted tooth profile; needs a between-pins measurement aid.
- **REQ-rack**: the infinite-radius special case; a second parameter model (no tooth
  count, bore or pitch diameter), not an extension of `GearParams`.
- Bevel gears need a product-scope decision before they are even a candidate — they
  contradict "involute spur gear generator".

### Bore and cutout follow-ups

- **REQ-hole-spoke-combination**: lightening holes between spoke arms on one part —
  plausible geometrically, adds a placement rule and a composition matrix; deferred by the
  v0.2 one-pattern decision.
- **REQ-keyway-mouth-chamfer**: chamfering the keyway's rim opening; v0.2 default is not
  to chamfer the keyway mouth.
- **REQ-hex-presets**: commodity hex sizes (5, 6, 8, 10, 12.7 mm) offered as UI presets —
  examples, not a standard.
- **REQ-spline-bore**: DIN 5480 and kin — a standards surface with many variants.

### Carried over

- Trochoidal root fillet below the base circle (would supersede L10) — `docs/ideas/`.
- A browser-driven test for the 3D viewer — `docs/ideas/`; the new form groups make it
  more valuable, the cost of the first one is still the question.
- The six active `docs/tech_debt/active/` items keep their own triggers.

## Out of Scope

Explicitly excluded from **milestone v0.2**, with reasoning.

| Feature | Reason |
|---------|--------|
| Standard-table keyway sizing (auto-fill width/depth from bore Ø per DIN 6885 / ANSI B17.1) | Rejected on Core Value grounds, not deferred: a looked-up number is a number someone cuts metal to, and DIN 6885 and ANSI B17.1 define different quantities for the same shaft |
| Tip relief (meshing-load profile modification) | A different, heavier feature than an edge-break chamfer (AGMA-class analysis); not asked for — never build it under the chamfer's name |
| A 2D corner chamfer in the tooth profile | Rejected 2026-09-25 in favour of the end-face edge break; it changes the meshing profile |
| Auto-derived spoke count / arm width / hole proportions | No standard exists to derive them from; a formula would be an opinion presented as a fact. Explicit fields, capped and warned |
| Hex bore as a union with the round bore (drill-then-broach) | Two numbers would define one bore and the small-hex case would silently do nothing; hex replaces round |
| More than one cutout pattern on one part | One pattern per part in v0.2; spokes + honeycomb is a real conflict over the same web, holes + spokes is a future requirement |
| Spline bores | A standards surface (DIN 5480 and kin), not a cut; keyway and hex cover the shafts a hobbyist has |
| Helical, internal/ring, rack, bevel gears | v0.3 candidates; bevel needs a product-scope decision first |
| A clock-based honeycomb cap (stop cutting when time runs out) | Non-reproducible across machines — violates L05/L08; the cap is analytic from a measured per-cell cost |

## Traceability

Each requirement maps to exactly one phase. Full phase detail (goals, success criteria,
research flags): `ROADMAP.md` "Phase Details".

| Requirement | Phase | Status |
|-------------|-------|--------|
| REQ-keyway-bore | Phase 9 | Pending |
| REQ-keyway-composes-with-d-flat | Phase 9 | Pending |
| REQ-keyway-wall-refused | Phase 9 | Pending |
| REQ-hex-bore | Phase 8 | Pending |
| REQ-hex-rim-chamfer | Phase 9 | Pending |
| REQ-bore-derived-numbers | Phase 9 | Pending |
| REQ-spoke-cutout | Phase 11 | Pending |
| REQ-hole-cutout | Phase 11 | Pending |
| REQ-honeycomb-cutout | Phase 11 | Pending |
| REQ-one-cutout-pattern | Phase 11 | Pending |
| REQ-cutout-conflicts-refused-early | Phase 11 | Pending |
| REQ-cutout-composes | Phase 11 | Pending |
| REQ-cutout-derived-numbers | Phase 11 | Pending |
| REQ-tip-chamfer | Phase 10 | Pending |
| REQ-tip-chamfer-capped | Phase 10 | Pending |
| REQ-defaults-off-regression | Phase 7 | Pending |
| REQ-three-interfaces-extended | Phase 12 | Pending |
| REQ-measured-build-time | Phase 12 | Pending |
| REQ-derived-dimensions-additive | Phase 8 | Pending |
| REQ-edge-selection-proven | Phase 7 | Pending |

**Coverage:**
- v0.2 requirements: 20 total
- Mapped to phases: 20
- Unmapped: 0 ✓

Notes on bundled requirements: REQ-hex-rim-chamfer and REQ-bore-derived-numbers each name
both new bore shapes (hex and keyway); both are owned by Phase 9 because that is the first
point at which both shapes exist and the full requirement text is testable end to end —
Phase 8 already delivers the hex-only edge of each (a chamfered hex bore, the hex
corner-to-corner field), which Phase 9's success criteria confirm still holds.

---
*Requirements defined: 2026-09-25*
*Last updated: 2026-09-25 after the v0.2 roadmap (Phases 7–12) — 20/20 requirements mapped*
