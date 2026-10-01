# Phase 11: Body Cutouts - Context

**Gathered:** 2026-09-29
**Status:** Ready for planning

<domain>
## Phase Boundary

The third v0.2 cut family, and the first whose cut is many cutters at once: three explicit
body-cutout patterns, exactly one per part, each a through-cut of the web between the bore
and the tooth rim, composing with any bore profile and with the face recesses.

1. **The fields.** Ten new `GearParams` fields in three new schema groups declared after
   the Recess group, the pattern's selector first in each (D-19): **Spokes** —
   `spoke_count: int = 0` (0 = off, 1–200), `spoke_width`, `hub_d`, `rim_wall`,
   `spoke_fillet` (mm, 0 = sharp — the one field the requirement did not name, amended in
   by D-21); **Holes** — `hole_count: int = 0`, `hole_d`, `hole_circle_d`; **Honeycomb** —
   `hex_cell`, `hex_wall` (mm, 0 = off). Every default is 0/off (L05); the CLI flags,
   `/api/schema` entries, form fieldsets and the shareable-URL round-trip fall out of the
   model (L02). The field names other than `spoke_fillet` are REQUIREMENTS.md's.
2. **The cuts.** One new `_build` step (name the planner's, on the order of `_cut_body`)
   between `_cut_keyway` and `_chamfer_tips` — research ARCHITECTURE.md Q1's order; 10
   D-13 keeps the tip step last. Each pattern builds its cutters and subtracts them in
   **one** `solid.cut(*cutters)` call (ROADMAP SC1, research PITFALLS.md Pitfall 2), through
   the full face width — through the recessed floor wherever the recess sits
   (REQ-cutout-composes).
   - **Spokes:** the annular web from `hub_d / 2` out to `rf − rim_wall`, minus N
     parallel-sided bars of width `spoke_width`, arm 0 centred on +X; each sector's four
     corners rounded by analytic tangent arcs drawn in the cutter's 2D sketch, radius
     `spoke_fillet` capped to the sector (D-01…D-06).
   - **Holes:** N circles of diameter `hole_d` with centres on the circle `hole_circle_d`,
     evenly spaced, hole 0 on +X (D-03).
   - **Honeycomb:** the whole hexagonal cells of an axis-centred lattice — across-flats
     `hex_cell`, pitch `hex_cell + hex_wall`, flats on ±X — that lie entirely inside the
     annulus `bore_mouth_limit(p) + hex_wall … rf − hex_wall` (D-07…D-09); the count is
     derived, capped at a measured constant, and the cell size raised in 0.05 mm steps
     until the count fits (D-11…D-13).
3. **The rules**, all in `calc.check()` before any CAD work (REQ-cutout-conflicts-refused-
   early): two or three non-zero selectors → 422 naming them (REQ-one-cutout-pattern); a
   half-set pattern → 422 naming the zero fields; a hub-wall breach
   (`bore_mouth_limit(p) + MIN_WALL`) or a rim-wall breach (`rf − MIN_WALL`) → 422;
   neighbours closer than `MIN_WALL` → 422; `hex_wall` under `MIN_WALL` → 422; a honeycomb
   with no whole cell fitting → 422 (D-10, D-14…D-17). Nothing about a cutout is capped
   except the two trimmable sizes: `spoke_fillet` (D-06) and the honeycomb's raised cell
   size (D-13).
4. **The numbers.** `DerivedDimensions` gains the thinnest remaining wall on the hub side
   and on the rim side (REQ-cutout-derived-numbers), the honeycomb cell count cut and the
   cell size cut, and the spoke fillet cut (D-20) — all `float | None` / `int | None`,
   `null` when their feature is off, rounded once at construction. `DIMS` and README rows
   land this phase (08 D-06/D-10). The 24 existing fields keep their names, types and
   values; `disallow_any_explicit` stays on (L21).
5. **The measurement.** A measurement-only plan first for the honeycomb (10 D-05's
   shape): build, fine-STL and STEP time versus cell count at 200 teeth, module 10, both
   recesses, **before** any cap constant is written (ROADMAP SC3, the research flag);
   `HEX_CELL_CAP` is the largest count whose row stays inside a 7.5 s share of the 30 s
   timeout (D-11, D-12). Then one sweep per pattern at its heaviest allowed configuration
   through `bench/build_time.py` and a new sweep file; every row inside
   `SPUR_BUILD_TIMEOUT=30s`; a row over budget halts for a human decision whose first
   offer is a lower `le` (08 D-11, 10 D-07, D-18).
6. **The proof.** Selector-matrix rows for each pattern × bore shape × recess setting
   (REQ-edge-selection-proven — `_tip_edges` is the one selector that runs after the
   cutouts; the rim and floor selectors run before them and keep their counts); a
   built-solid test per pattern; the recess floor fillet's survival proven by counting the
   fillet's faces/edges on the built solid (REQ-cutout-composes); a tripwire per proof; the
   pre-v0.2 fixture byte-unchanged and the replay requiring every new derived field null
   (07 D-03, 08's additive rule, L26).
7. **The record.** L30 appended: the honeycomb cap methodology (ROADMAP's process note
   names it), the field semantics and datums, the refusals, the heaviest rows.

Requirements: REQ-spoke-cutout (amended for `spoke_fillet`, D-21), REQ-hole-cutout,
REQ-honeycomb-cutout, REQ-one-cutout-pattern, REQ-cutout-conflicts-refused-early,
REQ-cutout-composes, REQ-cutout-derived-numbers.

**Out of this phase:** the composition matrix and the combined heaviest measurement
(Phase 12); more than one pattern per part (REQ-hole-spoke-combination, Future); a
rotation/phase field for arms or holes (deferred); corner fillets on honeycomb cells or on
holes (not asked); clipped boundary cells (rejected, D-07); separate honeycomb boundary-wall
fields (rejected, D-09); a `tol=` fuzzy boolean without a measurement (Claude's
Discretion); any sizing guidance in help text (no standard exists — research FEATURES.md).

</domain>

<decisions>
## Implementation Decisions

### Spoke arm geometry
- **D-01:** **`hub_d` is the hub ring's outer diameter; `rim_wall` is the rim ring's
  radial thickness measured inward from the root circle.** The cut sectors run from
  `hub_d / 2` to `rf − rim_wall`. Both are caliper numbers on the part; the root-circle
  datum is the one REQ-cutout-conflicts-refused-early and `recess_radii()`'s rim clamp
  already use. Rejected: `hub_d` as the hub's radial wall above the chamfered mouth (the
  same value would give a different part on a hex and a round bore, and contradicts the
  `_d` name); `rim_wall` from the tip circle (module-dependent, contradicts the REQ's
  datum). — **Reversibility:** costly — the published meaning of two fields; changing
  either later re-cuts every spoked link (L05).
- **D-02:** **Arms are parallel-sided bars of constant width `spoke_width`.** The cutter
  set is the annulus minus N bars — N sector solids in one compound, one `.cut` call. A
  width in mm is one number a caliper reads anywhere along the arm. Rejected: tapered
  angular sectors with the width read at the hub or at the rim (the width is not one
  number; a second datum to explain). — **Reversibility:** costly — same reason as D-01.
- **D-03:** **Arm 0 and hole 0 are centred on +X; no angle field.** One fixed convention
  for both patterns, stated in a comment and in help text: the D-flat's side, the hex
  bore's flat, `polarArray`'s default start. Rejected: +Y over the keyway (only helps
  even counts; the hub ring already keeps `MIN_WALL` past the keyway corner; two
  conventions to explain); a rotation field now (a third parameter on every interface,
  nobody asked — deferred). — **Reversibility:** costly — an additive angle field
  defaulting to the +X position is the only safe undo (L05).
- **D-04:** **Sector corners are filleted by a new field, `spoke_fillet` (mm, 0 =
  sharp)** — the human's choice over the recommendation (sharp, keyway D-08's shape). A
  fifth spoke field on every interface; REQ-spoke-cutout and ROADMAP Phase 11 SC2 name
  four, so the plan amends both (D-21). Rejected: sharp corners; a fixed radius (an
  opinion about the user's part, and a fillet the user cannot turn off).
- **D-05:** **The fillet is built as analytic 2D tangent arcs in the cutter's sketch,
  extruded** — L09's remedy for the fillet operator on many edges. Each sector is one
  closed wire: hub arc, corner arc, bar side, corner arc, rim arc, corner arc, bar side,
  corner arc; `_fillet_corner`'s maths (a line against an axis-centred circle) covers the
  hub corners with the arc centre outside the hub circle at `hub_d/2 + ρ` and needs its
  mirror for the rim corners (centre inside the rim circle at `rf − rim_wall − ρ`). No
  3D `.fillet()`, no new edge selector, no matrix column, no tripwire for a selector; the
  cutter crosses the filleted recess floor as any prism does. Rejected: the 3D operator on
  the 4N vertical corner edges (a fourth position selector to prove, vertical edges
  meeting the recess floor's toroidal fillet — a kernel case nobody has measured, and
  L09's ~50× cost); a spike timing both (the planner can probe the analytic arcs on the
  pinned kernel in minutes).
- **D-06:** **`spoke_fillet` is capped to the sector, warned, and the applied value
  reported:** `ρ ≤ 0.45 × min(the sector's opening at the hub ring between adjacent bar
  sides, the annulus width rf − rim_wall − hub_d/2)` — `root_fillet`'s 0.45-of-the-shared-
  dimension family (two arcs share each dimension; 10 % stays). Trimmable, so L03's cap
  branch: one warning in the "reduced to X mm to fit …" family and a
  `spoke_fillet_effective` derived field (10 D-08/D-09). The exact measure of the hub
  opening (arc or chord between the feet of adjacent bar sides on the hub circle —
  `keyway_flat_wall`'s arc measure is the precedent) is the planner's. Rejected: a 422
  when it does not fit (a smaller fillet contradicts nothing the user asked for); the
  applied value in the warning only (08 D-05: a cut number is in the response).

### Honeycomb lattice & walls
- **D-07:** **Whole cells only, never clipped.** A cell is cut only if its entire hexagon
  — corner reach `hex_cell / √3` from its centre — lies inside the web annulus; a cell
  straddling the hub or rim boundary stays solid. No sliver faces at a boundary (research
  PITFALLS.md Pitfall 1), every wall at least the boundary by construction, an integer
  count of full cells, and the thinnest-wall numbers read straight off the lattice. The
  web's edge is a ring of full cells, not a smooth circle — accepted. Rejected: cells
  intersected with the annulus (partial cells with near-tangent edges, a sub-`MIN_WALL`
  sliver against the bore mouth, an ambiguous count); a lattice stretched to fill
  (`hex_cell` and `hex_wall` would not be the numbers cut). — **Reversibility:** costly —
  adding clipped cells later changes the cell set of every published honeycomb link (L05).
- **D-08:** **The lattice origin is the gear axis and the cells' flats face ±X.** The
  origin cell lies inside the bore and is never cut; hexagons come from
  `polygon(6, hex_cell, circumscribed=True)` exactly as the hex bore's does (flats on ±X,
  vertices on ±Y); rows run along the flat-to-flat direction. Symmetric about the axis,
  one fixed convention stated in a comment; the same link gives the same cells anywhere.
  Rejected: an origin shifted so the first ring touches the hub wall (loses the symmetry,
  and the offset would depend on bore shape and chamfer — a hidden parameter); a vertex
  facing +X (a different convention from the hex bore's for no reason). —
  **Reversibility:** costly — same reason as D-07.
- **D-09:** **`hex_wall` is the wall everywhere, including both boundaries:** the inner
  boundary is `bore_mouth_limit(p) + hex_wall`, the outer `rf − hex_wall`. One wall number
  means one thing between cells and at the edges; a thicker `hex_wall` gives a thicker rim
  ring, as anyone expects. Rejected: `MIN_WALL` boundaries with `hex_wall` between cells
  (two wall numbers on one part, one of them not the user's); separate boundary-wall
  fields (two more fields, a REQ amendment, nobody asked). — **Reversibility:** costly —
  the published meaning of `hex_wall`.
- **D-10:** **`0 < hex_wall < MIN_WALL` is a 422 naming `hex_wall`**, the sentence quoting
  0.4 mm; 0 stays "off". Every other `MIN_WALL` breach in the tool is a refusal (bore vs
  root, keyway corner, hex corner); a wall thinner than the design floor conflicts with the
  tool's own rule, not with a trimmable wish. Rejected: raising to `MIN_WALL` with a
  warning (caps go down everywhere else; the honeycomb already raises `hex_cell`, and two
  adjustments on one pattern is one too many); building it and warning like
  `MIN_TIP_FDM` (contradicts the REQ's hub/rim rules, which refuse at `MIN_WALL`).

### Honeycomb budget & cap
- **D-11:** **The honeycomb at its cap may cost at most a quarter of `SPUR_BUILD_TIMEOUT`
  — ≤ 7.5 s — on the bench host**, measured as `bench/build_time.py`'s `worst_request`
  (build plus the slower of fine-STL and STEP) for the whole row, at the heaviest gear a
  honeycomb can sit on: 200 teeth, module 10 (the largest web, so the cap always binds),
  both recesses. 7.5 s is the quarter-of-timeout line Phase 10 already named; the tip
  chamfer alone reads 14.87 s at 200 teeth, and 14.87 + 7.5 leaves about 7.5 s for
  composition effects when Phase 12 stacks the two — if that stack still overruns, the cap
  is lowered before any honeycomb link exists in the wild. Rejected: half (a 200-tooth
  gear with both features composes to ~30 s on this host, so Phase 12 would lower the cap
  after links exist or raise the timeout); whatever fits alone (composition guaranteed
  over budget). — **Reversibility:** costly — a lower cap later changes the cell size of
  published links; a higher one is additive.
- **D-12:** **The cap is one constant cell count in `calc.py`** (on the order of
  `HEX_CELL_CAP`): the largest count whose sweep row at D-11's configuration reads
  ≤ 7.5 s, the measurement, date and host in the comment (L17's shape), cited in L30.
  Conservative on small gears, identical on every machine, one number a user can reason
  about in the warning; the sweep may show whether cost is linear in count without the cap
  having to model it. Rejected: a per-cell cost model (`budget / per-cell seconds` — only
  honest if the sweep shows cost linear and independent of recess and tooth count, and
  still one constant in the end); a teeth/module-dependent cap (10 D-07's second offer, a
  dimension that depends on the gear's other fields).
- **D-13:** **When the derived count exceeds the cap, `hex_cell` is stepped up by
  0.05 mm from the request** — the field's own step — **until the exact whole-cell count is
  ≤ the cap;** an area estimate (annulus area over the pitch hexagon's area) is used first
  so the exact enumeration is never run for millions of cells. Two derived fields:
  `hex_cell_effective` (the across-flats cut, `null` when off) and `hex_cell_count` (cells
  cut); one warning naming the requested size, the applied size and the cap, in the
  "reduced to …" family. Deterministic on every machine; the same link yields the same
  cells (REQ-honeycomb-cutout). Rejected: the exact off-grid minimum size (numbers like
  2.3417 mm nothing else in the tool reports); the count only (08 D-05).
- **D-14:** **A honeycomb in which no whole cell fits is a 422 naming `hex_cell` and
  `hex_wall`**, the sentence quoting the web annulus's inner and outer radius so the user
  can size the cell. The user asked for a honeycomb (both fields default to 0) and gave one
  that cannot exist — keyway D-03's reasoning, and the REQ's own breach refusal applied to
  the first cell. Rejected: building a solid web with `hex_cell_count` 0 and a warning
  (the recess's drop-and-warn exists because the recess defaults on — L05 forbids refusing
  a default; here the link asked); lowering `hex_cell` until one fits (the cap raises the
  size; shrinking it too is two opposite adjustments to one field).

### Refusals, bounds, numbers
- **D-15:** **A half-set pattern is a 422 naming the zero fields; dimensions set with
  the count at 0 are inert and warned about.** `spoke_count > 0` with `spoke_width`,
  `hub_d` or `rim_wall` at 0, or `hole_count > 0` with `hole_d` or `hole_circle_d` at 0,
  or `hex_cell > 0` with `hex_wall` at 0: refused before any CAD work (keyway D-03 — the
  user asked for a pattern that cannot exist; no default link carries it). The reverse —
  `spoke_width` set with `spoke_count` 0, `hex_wall` set with `hex_cell` 0 — builds
  without the pattern and one warning names the ignored fields with their values (hex
  D-02's sentence shape): a value the user typed never vanishes silently. `spoke_fillet`
  with the count at 0 is in that ignored set. Rejected: silently inert dimensions (the
  only place in the tool a set field would be ignored without a sentence); treating a
  half-set pattern as off with a warning (09 D-03 rejected it: a link that asked for a
  pattern would ship without it).
- **D-16:** **`MIN_WALL` between neighbours, both patterns.** Holes: the material between
  adjacent holes on the bolt circle — `hole_circle_d · sin(π / N) − hole_d` — must be
  ≥ `MIN_WALL`; it is a wall. Spokes: the sector opening between adjacent bars at the hub
  ring must be ≥ `MIN_WALL` — no cut thinner than the thinnest wall, so a sliver cutter
  never reaches the kernel (Pitfall 1). The honeycomb is covered by D-10. 422 naming the
  count and size fields (`hole_count`, `hole_d`, `hole_circle_d`; `spoke_count`,
  `spoke_width`, `hub_d`). The planner measures the pinned kernel one step either side of
  each rule (08 D-03) and records it. Rejected: overlap only (touching cutters are the
  documented OCCT failure class; a 0.05 mm wall prints as nothing); a floor for holes and
  overlap-only for spoke sectors (two rules; a 0.1 mm sector slot untested).
- **D-17:** **The hub and rim breaches, as REQ-cutout-conflicts-refused-early states
  them, read the recess's datums:** the hub wall is `bore_mouth_limit(p) + MIN_WALL` (the
  chamfered round rim, the chamfered hex corner, or the keyway's floor corner — whichever
  is farthest, exactly what `recess_radii()` clears) and the rim wall `rf − MIN_WALL`.
  Spokes: `hub_d / 2 < bore_mouth_limit(p) + MIN_WALL` → 422 naming `hub_d` (and the
  bore field the planner deems responsible); `rim_wall < MIN_WALL` → 422 naming
  `rim_wall`; a cut annulus narrower than `MIN_WALL` (`rf − rim_wall − hub_d/2 <
  MIN_WALL`, D-16's symmetric reading) → 422 naming `hub_d` and `rim_wall`. Holes:
  `hole_circle_d/2 − hole_d/2 < bore_mouth_limit(p) + MIN_WALL` or `hole_circle_d/2 +
  hole_d/2 > rf − MIN_WALL` → 422 naming `hole_circle_d` and `hole_d`. Honeycomb: no
  breach is reachable — D-09's boundaries and D-07's whole-cell rule keep every cell
  inside by construction; D-14 covers the empty case. The rules never stack where one
  implies the other (`elif`, 08's shape).
- **D-18:** **`spoke_count` and `hole_count` are integers 0–200, and 1 is allowed.** One
  instance per tooth is the natural ceiling — `teeth`'s family bound, not a number picked
  by inspection (08 D-07's objection to "what we have seen"). The sweep runs at the `le`;
  a row over 30 s halts for a human decision whose first offer is a lower `le` (10 D-07).
  One arm or one hole builds; the tool does not judge balance. Rejected: research's 24 /
  48 (no source; a 200-tooth module-10 gear has a ~2 m root diameter and can carry far
  more); a minimum of 2 (an opinion about the user's part; a single hole is a valid index
  feature).
- **D-19:** **Three schema groups — Spokes, Holes, Honeycomb — declared after the Recess
  group in that order,** the selector field first in each (`spoke_count`, `hole_count`,
  `hex_cell`), so the form shows three fieldsets and the CLI's flag order follows (L02;
  08 D-07's reading of "in its own group"). No `app.js` change beyond `DIMS` rows — the
  group renderer reads the schema's `group` key. Rejected: one "Cutouts" fieldset of ten
  rows where a third ever applies; extending the Body group (its name would stop meaning
  the blank's dimensions).
- **D-20:** **Five new `DerivedDimensions` fields**, names the planner's: the thinnest
  remaining wall on the hub side and on the rim side (REQ-cutout-derived-numbers; `null`
  when no pattern is set), `hex_cell_count` (`int | None`) and `hex_cell_effective` (D-13;
  `null` when the honeycomb is off), and `spoke_fillet_effective` (D-06; `null` when
  spokes are off or `spoke_fillet` is 0 — the planner picks, mirroring
  `tip_chamfer_effective`'s `null` when the request is 0). Rounded once at construction
  (Phase 4 D-10), `unit: mm` on the lengths, `DIMS` rows and README rows this phase (08
  D-06/D-10). The 24 existing fields keep their names, types and values; the replay
  requires every new field `null` on every fixture record; `disallow_any_explicit` stays
  on with no suppressions (L21). — **Reversibility:** costly — published `/api/info`
  fields under L21's typed contract.

### Process
- **D-21:** **The plan's first task amends the phase texts through the edit-phase
  tooling with one human confirmation** (08-01's pattern, 09 D-20), never a direct write:
  REQ-spoke-cutout and ROADMAP Phase 11 SC2 gain `spoke_fillet` (D-04) — "N straight
  arms … the sectors between the arms cut through the full face width, their corners
  rounded by `spoke_fillet` (0 = sharp), capped to fit". No other sentence is known to
  need it: D-09's boundary walls are a reading of REQ-honeycomb-cutout's "between the hub
  wall and the rim wall"; D-13's 0.05 mm steps are a reading of "the smallest size that
  fits"; D-17's `bore_mouth_limit` is the "bore + bore chamfer" datum generalised the way
  L27/L28 already did for the recess.
- **D-22:** The phase runs on **`gsd/phase-11-body-cutouts`**, cut this session from
  `origin/main` `b388cbd` (PR #11's squash), and lands via `make pr.land PR=N` (L22/L25);
  `.planning/` rides the same PR.
- **D-23:** Commits are plain `git commit` with explicitly staged files, never
  `git add -A`: the pre-commit hook runs `make verify` (~100 s warm at 453 tests) and the
  gsd SDK commit wrapper kills it at 30 s
  (`docs/tech_debt/active/2026-09-25-gsd-commit-timeout-kills-cold-verify-hook.md`); after
  any wrapper timeout, check for a pre-commit stash before re-committing. Run `make
  verify` once at session start.
- **D-24:** **The honeycomb spike is a measurement-only plan** (10 D-05's shape) whose
  numbers exist before the cap constant, the honeycomb field plan and the honeycomb proof
  plan are written; it needs no field — a probe path cutting N whole cells at D-11's
  configuration. Holes and spokes need no spike (ROADMAP's research flag: "well-documented
  patterns"); research Q6's order — holes, then spokes, then honeycomb — is the planner's
  to keep or to parallelise, with the one constraint that the cap is written only from the
  sweep's numbers. If even a modest count overruns the 7.5 s share, the checkpoint offers
  the number and asks; it never picks a cap by inspection.
- **D-25:** **L30 is appended** to `docs/architecture/decision_log.md` (append-only, 0
  deleted lines) in L29's shape: the fields and datums (D-01, D-09), the whole-cell rule
  and lattice (D-07, D-08), the cap methodology with the sweep's numbers (D-11…D-13), the
  refusals (D-10, D-14…D-17), the analytic spoke fillet (D-05) and each pattern's heaviest
  row — each cited to a SUMMARY sha or `bench/RESULTS.md`, none re-estimated.

### Claude's Discretion
- **Names:** the cut step and cutter builders in `model.py`, the cap/count/wall functions
  in `calc.py` (siblings of `recess_radii` / `tip_chamfer_limit`, returning applied values
  the part and the numbers both read — L08), the five derived fields (D-20), the sweep
  files, the RESULTS.md section titles, the field titles and every refusal and warning
  sentence (L15: the sentences are the product).
- **The thinnest-wall datum (D-20):** hub side measured from `bore_mouth_limit(p)` — exact
  for a round or D-flat bore; for a hex or keyed bore that is the corner's reach, exact
  where a cutout sits in the corner's direction and a lower bound elsewhere — the field
  description must say "from the farthest point of the bore mouth" so the number is never
  read as more than it is (L08); the planner may instead compute the exact minimum
  distance to the mouth polygon if it is cheap and honest, and describes whichever it
  ships. Rim side from `rf`. Spokes: the hub ring (`hub_d/2 − bore_mouth_limit`) and
  `rim_wall`; holes: the nearest hole edge; honeycomb: the nearest cut cell's corner, from
  the lattice.
- **Dimension bounds:** family bounds recommended — `spoke_width`, `hole_d`, `rim_wall`,
  `hex_cell`, `hex_wall` `le` 100 (`recess_width`'s), `hub_d`, `hole_circle_d` `le` 400
  (`recess_inner_d`'s), `spoke_fillet` `le` 5 (`recess_fillet`'s); `ge` 0, step 0.05 (0.1
  for the diameters if the planner prefers `recess_inner_d`'s). The refusals bound anything
  too large; a smaller `le` by inspection would be a guess.
- **Cutter construction:** spokes as N closed 2D wires (D-05) → faces → prisms through the
  face width → one `cut(*prisms)`; holes as N cylinders from one `polarArray` or N explicit
  centres; honeycomb as N hexagonal prisms at the lattice centres. Whether the N prisms are
  passed as `*cutters` or fused into one compound first is measured in the spike (Pitfall
  2 names both spellings) and the faster one recorded.
- **Honeycomb enumeration in `calc.py`:** axial or offset lattice coordinates, the area
  estimate bounding the search (D-13), the exact test `hub + corner reach ≤ r_centre ≤
  rim − corner reach` on each candidate; `derive()` runs on every keystroke (11.5 µs
  today), so the planner measures its cost at the cap and records it in the docstring.
- **`tol=` (research Pitfall 1):** a hole or a cell can legitimately sit tangent to a
  recess wall (`r_in`, `r_out`) or to nothing at all — unlike Phases 8–10, tangency is
  reachable here. The planner probes the pinned kernel at the tangent cases (a hole edge
  exactly on `r_in` and on `r_out`, a cell corner on `r_in`, a bar side crossing a wall)
  and ships a `tol=` only with the measurement and its own comment; a 422 for coincidence
  (research ARCHITECTURE.md Q1's suggestion) is rejected — a user cannot be told their
  hole is placed "too exactly".
- **The recess-fillet survival proof (REQ-cutout-composes):** count the fillet's faces or
  edges on the built solid before and after each pattern (09 D-07's built-solid shape);
  what a through-cut does to a toroidal fillet face (split into N pieces, or trimmed) is
  measured on the pinned kernel and pinned, not derived; the tripwire skips the recess
  fillet and shows the count go red.
- **Selector matrix rows:** each pattern × {round, D-flat, hex, keyway} × recess settings
  with the expected rim and floor counts unchanged (they run before the cutouts) and the
  tip count `2 × teeth`; plus a real-pipeline spy as 10-03's. Any pattern whose cutters
  put a `CIRCLE` at `ra` or on an end face at the rim's radius is impossible by D-17's
  bounds — the rows prove it rather than assume it.
- **Sweep rows:** per pattern, 200 teeth × module {1.75, 10} × recess {both, none} at the
  `le` count and at both a small and a large hole/sector size — 09-04's lesson: the
  heaviest row was not the largest feature, so both sizes are measured; the honeycomb's
  confirmation sweep runs at the cap on the same grid. Export time recorded per row for
  Phase 12's REQ-measured-build-time; fine-STL at many small faces (Pitfall 8) may be the
  slower export — `worst_request` already takes the slower one.
- **The over-budget halt for holes and spokes (10 D-07):** first offer a lower `le` on
  the count; second a count-dependent cap from the measured per-cutter cost. For the
  honeycomb the cap is the lever (D-12).
- **Help text:** the purpose, the datum, `0 = off`, no sizes and no standard (research
  FEATURES.md found none; 10 D-11); the honeycomb's says the count is derived and capped
  and the cell size may be raised. The CLI prints the same sentences.
- **README:** three feature bullets, ten parameter rows, five derived rows, one example
  link per pattern that the tests run — post-v0.2 sets, out of the regression corpus
  (07 D-05).
- **`bore_clearance`:** not added to any cutout dimension — cutouts are not fit
  features; a sentence in the help text if the planner thinks a user would expect it.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements and roadmap
- `.planning/REQUIREMENTS.md` — REQ-spoke-cutout (D-21 amends it), REQ-hole-cutout,
  REQ-honeycomb-cutout, REQ-one-cutout-pattern, REQ-cutout-conflicts-refused-early,
  REQ-cutout-composes, REQ-cutout-derived-numbers (this phase); REQ-three-interfaces-
  extended, REQ-measured-build-time (Phase 12's bar this phase feeds);
  REQ-derived-dimensions-additive, REQ-edge-selection-proven, REQ-defaults-off-regression
  (standing contracts); "## Out of Scope" (auto-derived proportions, more than one pattern,
  a clock-based honeycomb cap); "### Bore and cutout follow-ups" (REQ-hole-spoke-
  combination — deferred).
- `.planning/ROADMAP.md` "### Phase 11: Body Cutouts" — goal, SC1–SC5 (SC2 amended by
  D-21), the research flag that makes the honeycomb spike measurement-only; "### Phase 12"
  SC1/SC3 (what the composition pass expects of this phase); "## Process Notes (v0.2)"
  (L30 is required).
- `.planning/PROJECT.md` — "Current Milestone: v0.2" (cutouts with explicit count and
  dimensions; the honeycomb count derived, capped and warned; features compose), "Rules
  this milestone lives by", Key Decisions L01–L29.

### Decisions
- `docs/architecture/decision_log.md` — L02 (one model, three interfaces), **L03** (cap
  vs refuse — D-06/D-13 cap, everything else refuses), **L05** (defaults never rescale),
  **L08** (no plausible number — the thinnest-wall datum), **L09** (analytic fillets over
  the operator — D-05), L15 (sentences are the product), **L17** (a measured ceiling, the
  cap's methodology), L21 (typed contract), **L26** (fixture; a selector never silently
  selects nothing), L27/L28 (`bore_mouth_limit` as the shape-general datum; the sweep and
  the measured-bound method), **L29** (the entry shape L30 follows; the 14.87 s row D-11
  budgets against). Append-only; L30 is this phase's.
- `.planning/phases/10-tooth-tip-chamfer/10-CONTEXT.md` — D-05 (measurement-only spike),
  D-06/D-07 (sweep shape; over-budget halt and its first offer), D-08/D-09 (applied-value
  field and warning), D-12…D-14 (built-solid proof, matrix column, tripwire + guard),
  D-13 (the tip step stays last).
- `.planning/phases/09-keyway-bore/09-CONTEXT.md` — D-03 (half-set → 422), D-07 (built-
  solid proof shape), D-09 (the recess yields via `bore_mouth_limit`), D-10/D-12 (measured
  boundaries, one step either side), D-20 (text amendments through the tooling), its
  `<specifics>` (kernel behaviour on end-face edges).
- `.planning/phases/08-hex-bore/08-CONTEXT.md` — D-02 (ignored-field warning shape),
  D-03 (measure the kernel boundary, cap one step inside), D-05/D-06 (fit numbers in the
  response; `DIMS` rows this phase), D-07 ("in its own group"), D-10 (README), D-11/D-12
  (the sweep and `make bench.build`), "Deferred Ideas" (conditional form fields — its
  trigger is now live, see Deferred below).
- `.planning/phases/07-foundation-generalized-edge-selection-regression-fixture/07-CONTEXT.md`
  — D-03/D-05 (fixture policy, closed corpus), D-15–D-18 (guard contract, exact counts).

### Research (v0.2 kickoff)
- `.planning/research/ARCHITECTURE.md` — **Q1** (cut order; the recess fillet is baked
  geometry before any cutout; the coincidence-check suggestion — rejected in favour of a
  probe), Q3 (additive fields; the cutout-family conflict — resolved by REQ-one-cutout-
  pattern), **Q4** (the derived-fields table; `hex_cell_count` cannot be a dimensional
  formula), Q6 (holes → spokes → honeycomb), "Anti-Patterns" (the honeycomb cap as a
  dimensional formula).
- `.planning/research/PITFALLS.md` — **Pitfall 1** (tangent cutters — the `tol=`
  probe), **Pitfall 2** (`cut(*cutters)`, fuse-then-cut as the alternative to measure),
  Pitfall 4 (position selectors after new topology — the matrix rows), **Pitfall 5**
  (analytic cap, never a clock), Pitfall 8 (many small faces change export cost), Pitfall
  10 (every conflict a 422 in `calc.py`, never a `BuildError` after a timed build).
- `.planning/research/FEATURES.md` — "Feature Dependencies" (cutouts need the hub and
  rim `recess_radii()` already reasons about), "## Standards Cited — Body Cutouts" (no
  standard exists; help text cites none).
- `.planning/research/STACK.md` §4 — `Workplane.polygon(circumscribed=True)`,
  `polarArray`, variadic `Shape.cut(*toCut, tol=None)` verified on `cadquery==2.8.0`.
- `.planning/research/SUMMARY.md` — Known Conflict #4 (composition of patterns — closed by
  REQ-one-cutout-pattern), "Research Flags" (the honeycomb sweep).

### Measurement and process
- `bench/RESULTS.md` — the Phase 8/9/10 sections (host-state header, table, named heaviest
  row) the new sections copy; "Tooth-tip chamfer build and export time (Phase 10)" (the
  14.87 s row D-11 budgets against); the `SPUR_BUILD_TIMEOUT` section (the 4× rationale).
- `bench/build_time.py` (`Timing.worst_request` is the number D-11 bounds),
  `bench/sweeps/tip_chamfer.json`, `Makefile` `bench.build` (`SWEEP=`) — reused unchanged.
- `docs/tech_debt/active/2026-09-28-tip-chamfer-narrows-the-build-timeout-margin.md` —
  why the honeycomb gets a quarter, not a half.
- `docs/HOW_TO_DEVELOP.md` §2/§4 — the phase branch is cut before discuss-phase and reused
  by execute-phase; `main` only via `make pr.land`.
- `docs/CODING_VALUES.md`, `CLAUDE.md` — comments carry the measurement; `calc.py` never
  imports the kernel; one validation at the `GearParams` boundary.
- `docs/tech_debt/active/2026-09-25-gsd-commit-timeout-kills-cold-verify-hook.md` — D-23.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/spur/model.py` `_ring(r_in, r_out, z0, height)` (271–273) and
  `_cut_face_recesses` (178–196): the annulus cutter and the two-call cut pattern SC1
  generalises to `cut(*cutters)`; `_cut_bore` (199–223): the `polygon(6, af,
  circumscribed=True)` call the honeycomb cell reuses, with its orientation comment;
  `_fillet_corner` (96–113): the line-vs-axis-centred-circle tangent-arc maths D-05 reuses
  for the hub corners and mirrors for the rim corners; `_outline` (116–167): how a closed
  wire of arcs and lines becomes a face (`makeThreePointArc`, `makeLine`,
  `Wire.assembleEdges`, `Face.makeFromWires`); `_build` (362–373): five steps, the cutout
  step is one insertion before `_chamfer_tips`; `_build_checked` (376–383): the catch-all
  every D-14…D-17 refusal must keep cutouts away from.
- `src/spur/model.py` `_tip_edges` (332–357), `_bore_rim_edges` (299–329),
  `_groove_floor_edges` (276–296): the three guarded position selectors; the matrix's
  expected counts are theirs.
- `src/spur/calc.py` `bore_mouth_limit(p)` (151–173): the shape-general hub datum D-09
  and D-17 read; `recess_radii(p, rf)` (176–197): the hub/rim clamp pattern and the
  `MIN_WALL` constants; `check(p)` (283–420): the `("message", ("field", …))` tuple shape,
  the if/elif non-stacking rules, the per-shape branch; `root_fillet` / `recess_fillet` /
  `tip_chamfer_limit` (213–281): the cap-function shape (request in, applied value out,
  3 dp, a `(limit, reason)` tuple when several limits compete); `derive()` (516–653): the
  warning list and the "reduced to … to fit …" / "… is ignored." sentence families;
  `DerivedDimensions` (432–513): `float | None` fields with `description` and `unit`.
- `src/spur/params.py` `_f(default, ge, le, title=, group=, unit=, step=, help=)`
  (17–23): integer fields work as `teeth` shows (33); the Recess group (89–101) is the
  insertion point for the three new groups; `_feasible` (103–113): no new plumbing for
  new refusals.
- `src/spur/static/app.js` `DIMS` (13–) and the schema-driven group renderer (45–85): a
  new group appears from the schema; five `DIMS` rows are the only UI change.
- `tests/test_model.py` `test_each_edge_selector_picks_exactly_its_own_edges` (134–):
  the matrix new rows join; `test_the_bore_chamfer_survives_the_keyway_and_the_slot_edges_stay_sharp`
  (392–) and `test_the_tip_chamfer_breaks_only_the_tip_arcs_on_the_built_solid` (630–):
  the built-solid proof shape; `test_the_tip_chamfer_proof_fails_when_the_tip_step_is_skipped`
  (648–): the tripwire shape; `test_a_recess_at_its_hub_clearance_keeps_min_wall_from_the_chamfered_bore_mouth`
  (690–): the hub-datum test each pattern's hub rule copies; `test_the_largest_keyway_each_rule_allows_builds`
  / `test_the_kernel_cuts_one_valid_solid_past_each_keyway_rule` (478–, 492–): the
  one-step-either-side pattern D-16/D-17 copy.
- `tests/test_calc.py` `test_infeasible_parameters_name_their_fields` (107) and the
  keyway refusal tests (315–395): the 422-naming-fields shape;
  `test_a_tip_chamfer_is_capped_to_whichever_limit_binds_first` (616): the cap-and-warn
  test shape for D-06/D-13.
- `tests/regression/pre_v0_2.json` + `test_pre_v0_2.py`: byte-unchanged; new derived
  fields required `null`.
- `bench/build_time.py` + `bench/sweeps/*.json` + `make bench.build SWEEP=`: the spike and
  the sweeps add files, not code.

### Established Patterns
- A cap lives in one `calc.py` function returning the applied value; `derive()` warns when
  it differs from the request; `model.py` calls the same function — the part and the number
  cannot disagree (L08). D-06 and D-13 follow it.
- Every `MIN_WALL` breach is a 422 naming the fields, in `calc.py`, never a `BuildError`
  after a timed build (L03, Pitfall 10); a kernel boundary is measured by bisection, the
  rule sits one step inside, the comment carries the numbers and the date, tests sit one
  step either side (08 D-03, 09 D-12).
- A selector runs only while its feature is on, is position-based, and raises
  `BuildError` naming the defect when empty (L26); tests pin exact counts per shape and a
  tripwire shows each proof going red.
- New numbers are measured on the pinned kernel through a committed script and `make`
  target, recorded in `bench/RESULTS.md` with host state, cited in the `Lxx` entry — before
  the rule that depends on them is written (L17, 10 D-05).
- `calc.py` never imports `cadquery` (import-linter); vendor objects stop at `model.py`;
  one validation at the `GearParams` boundary.
- One phase = one branch = one PR = one squash; plain `git commit`, explicit files.

### Integration Points
- `src/spur/params.py` — three groups, ten fields, after the Recess group.
- `src/spur/calc.py` — the web-annulus datums (hub from `bore_mouth_limit`, rim from
  `rf`), the spoke sector geometry and fillet cap, the hole geometry, the honeycomb lattice
  enumeration, `HEX_CELL_CAP`, the raise-to-fit function, the D-10/D-14…D-17 rules in
  `check()`, five `DerivedDimensions` fields, the D-06/D-13/D-15 warnings.
- `src/spur/model.py` — the cutout step and three cutter builders; `_build` gains one
  line.
- `tests/test_model.py` — matrix rows, three built-solid proofs, the recess-fillet
  survival count, tripwires, one-step-either-side kernel tests. `tests/test_calc.py` —
  every refusal and cap. `tests/test_api.py` / `tests/test_cli.py` — a link per pattern
  through each interface; the 422s naming the fields; the `DIMS`-subset test picks up the
  fields.
- `bench/sweeps/*.json` (a spike sweep and per-pattern sweeps), `bench/RESULTS.md` — the
  honeycomb spike section and the per-pattern sections.
- `src/spur/static/app.js` `DIMS`, `README.md` — five rows, ten rows, three examples.
- `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md` — D-21's amendment;
  `docs/architecture/decision_log.md` — L30.

</code_context>

<specifics>
## Specific Ideas

Arithmetic on the parameter model only — **no kernel probe was run this session**; the
spike (D-24) measures every cost below.

- **Default gear** (19 teeth, m 1.75, α 25°, x 0, face 7.5): `rf` 14.4375, `r_bore`
  4.575, chamfered mouth `bore_mouth_limit` 4.975; the recess today runs 5.375 … 14.0375.
  The cutout web annulus at `MIN_WALL` is the same 5.375 … 14.0375 (8.66 mm radial). A
  honeycomb with `hex_cell` 3 and `hex_wall` 1: annulus 5.975 … 13.4375, pitch 4, corner
  reach 1.732, so a cell's centre must sit between 7.71 and 11.71 mm — roughly one ring of
  cells (an estimate, not an enumeration). Four 2 mm bars on a `hub_d` 12 / `rim_wall` 1
  spoke web: hub opening between bars ≈ 7.4 mm, so a 3 mm `spoke_fillet` caps at about
  0.45 × 7.4 ≈ 3.3 mm on the opening and 0.45 × 7.4 ≈ 3.3 mm on the annulus width
  (13.44 − 6 = 7.44) — binds only above that.
- **200 teeth, module 10** (D-11's configuration): `rf` 987.5 mm, `ra` 1010 mm. With the
  default 9 mm bore the web annulus is ~5.4 … 987 mm, area ≈ 3.06 × 10⁶ mm². A 3 mm
  cell with a 1 mm wall (pitch 4, pitch-hexagon area ≈ 13.9 mm²) implies ~2.2 × 10⁵
  cells; at a cap in the hundreds D-13 raises the cell to tens of millimetres (≈ 94 mm
  pitch for 400 cells). That is the honest outcome REQ-honeycomb-cutout asks for, and the
  reason D-13's area estimate must run before any enumeration.
- **Baselines the spike compares against** (`bench/RESULTS.md`): a plain 200-tooth build
  2.3 s (Phase 7); Phase 8's heaviest 5.08 s and Phase 9's 4.85 s (recess both, 200
  teeth, module 1.75); the tip chamfer's 14.87 s (module 1.75, `c` 1.75, recess both) and
  15.90 s (module 0.2). Nothing has measured module 10 at 200 teeth with a recess — the
  spike's first row is that gear with 0 cells.
- **Kernel facts already recorded:** `polygon(6, d, circumscribed=True)` puts a flat on
  +X and vertices on ±Y (08 `<specifics>`); a one-shot chamfer on mixed arc + line edge
  sets failed where arcs alone were fine (09 `<specifics>`) — irrelevant to a boolean cut,
  relevant if anyone reaches for the 3D fillet D-05 rejected.
- **Pitfall 2's two spellings** — `cut(*cutters)` versus fuse-then-cut — are both to be
  timed in the spike at the same cell count; the faster is the pattern all three cutters
  use.

</specifics>

<deferred>
## Deferred Ideas

- **A rotation/phase field for arms and holes** (`spoke_angle` / `hole_angle`) — D-03
  fixes +X; an additive field defaulting to that position is the safe undo if a real part
  needs it.
- **Corner fillets on honeycomb cells or on holes** — not asked; D-04's fillet is the
  spoke sectors' only. A cell's 120° corners and a hole's round edge have no corner to
  break.
- **Lightening holes between spoke arms on one part** — REQ-hole-spoke-combination,
  already in REQUIREMENTS.md "Future Requirements"; REQ-one-cutout-pattern rules it out
  here.
- **A teeth/module-dependent honeycomb cap** — D-12's rejected option; revisit only if a
  user with a small gear needs more cells than the constant allows and the sweep shows
  cost per cell falls with gear size.
- **Clipped boundary cells** — rejected by D-07; recorded so it is not re-derived.
- **Separate honeycomb boundary-wall fields** — rejected by D-09.
- **Conditional form fields ("disabled when")** — 08's deferred idea named "Phase 9 or
  11 accumulates more ignored-when relations than a warning sentence carries well" as its
  trigger; D-15 adds three more (dimensions ignored while the count is 0). Phase 12's UI
  hint should weigh it; not built here.
- **Analytic corner arcs as a general cutter helper** — if D-05's sketch fillet proves
  reusable, the same helper could round a keyway's floor corners (09 D-08 rejected a 3D
  fillet there); a separate idea, not this phase.

No scope creep beyond `spoke_fillet` (D-04, taken into scope with its amendment) surfaced
during discussion.

</deferred>

---

*Phase: 11-body-cutouts*
*Context gathered: 2026-09-29*
