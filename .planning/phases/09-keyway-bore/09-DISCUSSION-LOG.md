# Phase 9: Keyway Bore - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-27
**Phase:** 9-keyway-bore
**Areas discussed:** Placement and the D-flat rule; Chamfer with a keyway (SC4); Refusals:
recess, root, width, debt; Numbers, help text, L28 datum

Evidence presented before the areas were chosen: three probe runs on the pinned kernel
(default gear, DIN 6885 3 × 3 key, `t2` 1.4) — the corner 0.327 mm from the default recess
hub wall; the one-shot chamfer on a D-flat + keyway failing in every variant while
chamfer-then-keyway builds valid every time; chamfering the keyway's own edges valid on a
round bore only with recess clearance, invalid on a D-flat; and the ROADMAP/REQ datum
formula `bore_d/2 + bore_clearance` differing from the code's `(bore_d + bore_clearance)/2`.

---

## Placement and the D-flat rule

| Option | Description | Selected |
|--------|-------------|----------|
| +Y, 90° from the flat | One fixed position; SC2's 422 live; derived number `bore_effective + depth` regardless of the flat; defaults compose | ✓ |
| −X, opposite the flat | Never intersects; SC2's 422 unreachable; the opposite wall becomes the flat | |
| A `keyway_angle` field | A third parameter on every interface; angle-dependent rules; not in REQ | |

**User's choice:** +Y, 90° from the flat.

| Option | Description | Selected |
|--------|-------------|----------|
| `MIN_WALL` of bore wall must remain | Refuse when < 0.4 mm of bore wall is left between the flat's corner and the keyway's side; boundary measured, one step either side tested | ✓ |
| Geometric overlap only | Refuse only when the keyway's side lies in the flat's removed region; near-tangent slivers reach the kernel | |

**User's choice:** `MIN_WALL` of bore wall must remain.

| Option | Description | Selected |
|--------|-------------|----------|
| 422 naming both fields | A half-set keyway (one field zero, the other not) cannot exist; no link carries it | ✓ |
| Treat as off, warn | 08 D-02's ignore-and-warn; builds a part with no keyway from a link that asked for one | |

**User's choice:** 422 naming both fields.

| Option | Description | Selected |
|--------|-------------|----------|
| Yes — flat stays, keyway added | L05; REQ-keyway-composes-with-d-flat; a plain keyed bore is `bore_flat=0` | ✓ |
| Keyway replaces the flat, warned | 08 D-01's pattern; contradicts the requirement as written | |

**User's choice:** Flat stays, keyway added.

**Notes:** At the continue gate the human proposed a bore-type dropdown in the web UI
("we have round, d-flat, hex and keyway"). Surfaced as a conflict with L27, 08 D-09 and
research Q3 with three options; the human chose **defer to Phase 12 and file as an idea**
over a UI-only select in Phase 9 and a model-level discriminator.

---

## Chamfer with a keyway (SC4)

| Option | Description | Selected |
|--------|-------------|----------|
| Sharp on every bore | Research Q2 option 2; the only behaviour the kernel delivers for D-flat + keyway; one rule | ✓ |
| Chamfered on round bores, sharp on D-flat | Two behaviours for one field; extra recess clearance; a warning naming the difference | |

**User's choice:** Sharp on every bore.

| Option | Description | Selected |
|--------|-------------|----------|
| Chamfer first, then cut the keyway | Unchanged `_cut_bore`; a new slot step after it; measured valid in every case | ✓ |
| Cut the keyway first, two-step chamfer | Selector excludes the keyway's edges; two kernel operations; measured valid; no behavioural gain | |

**User's choice:** Chamfer first, then cut the keyway.

| Option | Description | Selected |
|--------|-------------|----------|
| Pre-keyway count + built-solid proof; amend SC4 | Matrix counts unchanged; a built-solid test proves the chamfer survived the slot (4.15 vs 4.66 mm³; 178 vs 172 faces); SC4 wording amended via edit-phase tooling | ✓ |
| A post-build chamfer-face count | A second selector on the finished solid; new selector to prove; same evidence | |

**User's choice:** Pre-keyway count + built-solid proof; amend SC4.

| Option | Description | Selected |
|--------|-------------|----------|
| Through, flat floor, square corners | A rectangular prism from inside the bore to `r + depth`, full face width; DIN's floor radius not modelled, stated in README | ✓ |
| Filleted floor corners | DIN 6885's small radius; a fixed radius or a field; a new selector; kernel risk | |

**User's choice:** Through, flat floor, square corners.

---

## Refusals: recess, root, width, debt

| Option | Description | Selected |
|--------|-------------|----------|
| Recess yields, like the hex | `bore_mouth_limit(p)` learns the keyway corner; recess narrows/drops with existing warnings; SC3 and REQ-keyway-wall-refused lose "or a recess wall" | ✓ |
| 422 as written | Floor corner within `MIN_WALL` of the recess wall refused naming `keyway_depth` and the recess field; refuses the default gear with its correct key | |
| Hybrid | Yield when `recess_inner_d` is 0, 422 when set; a new distinction `recess_radii()` does not make today | |

**User's choice:** Recess yields, like the hex.

| Option | Description | Selected |
|--------|-------------|----------|
| Corner + `MIN_WALL` vs `rf`, naming `keyway_depth` and `keyway_width` | The floor corner is the nearest keyway point to the root; boundary measured, one step either side | ✓ |
| Floor centreline only, naming `keyway_depth` | Simpler; under-counts the corner's reach | |

**User's choice:** Corner + `MIN_WALL` vs `rf`, naming both.

| Option | Description | Selected |
|--------|-------------|----------|
| Bound measured on the kernel (08 D-03) | Probe widths toward `bore_effective` on a small and a large bore; the failing ratio written next to the rule; 422 names `keyway_width` and `bore_d` | ✓ |
| Fixed ratio (e.g. `w_eff ≤ bore_effective/2`) | Predictable but unsourced — no standard states a hard limit | |

**User's choice:** Bound measured on the kernel.

| Option | Description | Selected |
|--------|-------------|----------|
| Fold in, refuse past the measured failure point | Measure where the kernel fails for a round/D-flat bore near the root with its chamfer; refuse one step past it naming `bore_d` and `bore_chamfer`; links that build today keep building (L05); debt resolved in the same commit | ✓ |
| Fold in, refuse at `bore_mouth_limit > rf − MIN_WALL` | Consistent with the hex rule; refuses round links that build today with a thin wall | |
| Defer with a new trigger (Phase 12) | Leave the debt active one more phase | |

**User's choice:** Fold in, refuse past the measured failure point.

---

## Numbers, help text, L28 datum

| Option | Description | Selected |
|--------|-------------|----------|
| As-cut wall = `bore_radius(p)`; fix the text | Floor radius `bore_radius(p) + keyway_depth`; SC1 and REQ-keyway-bore's parenthetical amended; L28 states the formula | ✓ |
| Keep the text's formula literally | A datum `bore_clearance/2` outside the wall that exists on the part | |

**User's choice:** As-cut wall = `bore_radius(p)`; fix the text.

| Option | Description | Selected |
|--------|-------------|----------|
| Two: floor-to-opposite-wall and effective width | `bore_effective + keyway_depth` (SC5) and `keyway_width + bore_clearance` (08 D-05's fit-number rule); two UI rows | ✓ |
| One: floor-to-opposite-wall only | SC5 as written; the as-cut slot width appears nowhere | |

**User's choice:** Two fields.

| Option | Description | Selected |
|--------|-------------|----------|
| Convention only, no numbers | DIN 6885 / ISO R773 `t2` from the as-cut wall; ANSI B17.1's T is across the bore; clearance added to the width; 0 = off | ✓ |
| Also one DIN 6885 example row | "8–10 mm shaft: 3 mm wide, t2 1.4 — example only"; REQ allows it; MEDIUM-confidence table | |

**User's choice:** Convention only, no numbers.

| Option | Description | Selected |
|--------|-------------|----------|
| After `bore_flat`, before `bore_hex`; `le` 200; step 0.05 | Round-profile modifiers stay together, then the replacing profile, then clearance and chamfer; one bound for the bore family | ✓ |
| After `bore_hex`; `le` 200; step 0.05 | Append in arrival order | |

**User's choice:** After `bore_flat`, before `bore_hex`; `le` 200; step 0.05.

---

## Claude's Discretion

Names (field titles, derived fields, the slot step, the sweep file, L28 vs a separate
entry for the debt rule); the exact flat-rule measure and every measured boundary; refusal
and warning sentences; `bore_mouth_limit`'s keyway branch shape; the matrix rows and the
built-solid tests' exact form; the sweep rows; the fuzzy-boolean confirmation; the hex
re-confirmation citations; README wording; `bore_clearance`'s help text; unwrapping the
ROADMAP `**Requirements**:` line. Offered at the final gate and left to the planner by the
human: the heaviest sweep rows, the hex × keyway 422's exact field list.

## Deferred Ideas

A bore-shape selector in the web form (filed:
`docs/ideas/2026-09-27-bore-shape-selector-in-the-web-form.md`); a `keyway_angle` field;
chamfering the keyway's own edges; filleted floor corners; a DIN example row in help text;
the hybrid recess rule; a blind keyway.
