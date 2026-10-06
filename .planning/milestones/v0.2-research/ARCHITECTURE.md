# Architecture Research: v0.2 "Fit to Shaft" Integration

**Domain:** parametric CAD pipeline (CadQuery/OpenCascade), additive feature integration
**Researched:** 2026-09-25
**Confidence:** HIGH for everything grounded in the current tree (cited file:line); MEDIUM
where cadquery 2.8.0's installed API was checked but not run; LOW/flagged explicitly
where a claim is architectural judgement or needs a phase-level benchmark, per L03/L08.

## Summary

v0.2 is five additive cuts (keyway bore, hex bore, three body-cutout patterns, tip
chamfer) layered onto a four-step pipeline that already composes recess → bore → chamfer
by **construction order**, not by inspecting the kernel's output. The existing bore-rim
and recess-floor edge selectors are **position-based**, and that position logic is the one
piece of v0.1 architecture that does not generalize for free — it must change for a hex
or keyway rim, or it will silently select nothing (no crash, no warning — just an
unchamfered edge). Everything else (the flat-field `GearParams` model, the cache-key
mechanism, `calc.py`'s cap-vs-refuse split) generalizes by adding more of the same shape
that already exists (`bore_flat`, `recess_sides`, `recess_radii()`), not by inventing a
new pattern.

## Standard Architecture (as it stands today)

### System Overview

```
GearParams (params.py)                    -- flat fields, frozen+hashable, group=/unit=/step=
        │  model_validator -> calc.check()
        ▼
calc.py  profile() / derive() / check()    -- no cadquery import (import-linter enforced)
        │  DerivedDimensions (frozen pydantic model, 19 fields today)
        ▼
model.py  _build(p):
    _gear_blank(pr, fillet, face_width)          -- extruded outline, analytic root fillets
      -> _cut_face_recesses(solid, p, rf)         -- ring cut(s) + _groove_floor_edges() fillet
      -> _cut_bore(solid, p)                      -- hole cut + _bore_rim_edges() chamfer
    solids = solid.Solids(); assert len == 1
        │
        ▼
export()/build()  -- lru_cache(_build_checked) per worker, keyed by GearParams equality
        │
        ▼
app.py _EXPORTS (_BlobCache)  -- keyed by (params, fmt, quality, encoding)
pool.py BuildPool             -- executor_for(p) = hash(p) % workers  (affinity, not correctness)
```

Source: `src/spur/model.py:237-246` (`_build`), `:159-194` (`_cut_face_recesses`,
`_cut_bore`), `src/spur/app.py:387-411` (cache key), `src/spur/pool.py:97`
(`executor_for`).

### Component Responsibilities (unchanged by v0.2)

| Component | Responsibility | File | v0.2 touches it? |
|-----------|----------------|------|-------------------|
| `GearParams` | flat validated fields, JSON-schema-driven form/CLI | `params.py` | Yes — new field groups |
| `calc.py` | pure geometry, feasibility, `DerivedDimensions` | `calc.py` | Yes — new derived fields, new cap/refuse functions |
| `model.py` | sole cadquery/OCP doorway, cut pipeline, edge selection | `model.py` | Yes — new cut steps, generalized edge selectors |
| `app.py` / `pool.py` | admission control, cache keying, worker routing | `app.py`, `pool.py` | No code change expected — cache key already generalizes (Q5) |
| `cli.py` | argparse from `GearParams` fields | `cli.py` | No — flags appear automatically (L02) |

## Q1 — Cut order: where do the new cuts go, and does the recess floor fillet survive

### Recommended order

```
_gear_blank(pr, fillet, face_width)
  -> _cut_face_recesses(solid, p, rf)      # unchanged: ring cut, THEN fillet, before anything else touches the floor
  -> _cut_bore(solid, p)                   # generalized: round | d_flat | hex, THEN rim chamfer
  -> _cut_body(solid, p)                   # NEW: spoke arms | lightening holes | hex pattern
  -> _chamfer_tips(solid, p)               # NEW: tooth-tip edges, last
```

**Why recess stays first, and why that already answers the "floor fillet survives
cutouts" question.** `_cut_face_recesses` (`model.py:159-177`) cuts the ring and calls
`.fillet()` on `_groove_floor_edges()` in the *same function*, before `_cut_bore` (or
anything else) has touched the solid. `.fillet()` is not a symbolic annotation — it
bakes an actual filleted OCCT surface into the solid at that point in the pipeline. Every
downstream boolean cut in the current pipeline (`_cut_bore`'s hole, today; a body cutout,
in v0.2) subtracts from a solid that **already has that fillet as real geometry**. This
is not a new property v0.2 introduces — it is the same mechanism that already lets
`_cut_bore` cut close to a recess today without disturbing the recess fillet, and it is
directly observable in `_build()`'s existing order (`model.py:237-241`). So: **do not
move cutouts before `_cut_face_recesses`.** Keep the recess step first, and body cutouts
run after it, subtracting from a solid whose floor fillet is already solid geometry, not
something a later selector has to re-derive.

What this does *not* protect against: if a cutout's boolean actually **overlaps the
recess ring's inner or outer wall radius** (`r_in`/`r_out` from `recess_radii()`), the
subtraction will locally eat into the fillet surface at that overlap — correctly, since
the milestone explicitly wants cutouts to "cut through the recessed floor." The fillet
elsewhere on the ring is untouched by construction; only the region the cutout actually
occupies is affected, which is physically correct, not a defect. What calc.py needs to
add is a check that a cutout is **not positioned so its edge falls within `TOL` of
`r_in`/`r_out` by coincidence** (as opposed to deliberately spanning through the floor),
the same class of guard `recess_radii()` already applies with `MIN_WALL` — see Q4.

**Why bore comes before body cutouts, not after.** `_bore_rim_edges` (`model.py:213-232`)
selects "the bore opening on the two end faces" by a **radial distance cutoff from the
axis** (`lim = r_bore + 0.01`), scanning every edge on the two end faces. If body cutouts
(a lightening hole close to the bore, a spoke arm's inner corner) are cut *before* the
bore chamfer runs, their new edges also sit on the end faces and — depending on how close
their own points get to the axis — could satisfy `on_rim()`'s distance test and get
wrongly folded into the bore chamfer selection, or conversely inflate what "on rim"
means and pull in edges that were never meant to be chamfered. Cutting the bore (hole +
chamfer) while it is still the *only* near-axis feature on the solid, then adding body
cutouts afterward, keeps `_bore_rim_edges`'s selection scope exactly what it is today:
one shape, no competing edges near the axis, at the moment the chamfer runs.

**Tip chamfer last.** It selects edges on the tooth tip circle (`ra`), the region
farthest from the axis and untouched by any bore/recess/body cut — order relative to the
other four cuts does not matter geometrically, but placing it last keeps the new
`_chamfer_tips()` selector simple (it can assume the full, final tooth outline is
present) and keeps the diff to `_build()` a single append rather than an insertion
between existing steps.

### Concrete risk this ordering does NOT eliminate

A body cutout whose extent reaches all the way from the bore rim out past the recess
ring — e.g. a wide spoke arm, or a lightening hole placed close to both boundaries —
still needs its own calc.py-side clearance rule (MIN_WALL from both the bore and the
recess ring, analogous to `recess_radii()`'s `hub`/`rim` clamps) so that "compose with
any bore profile" and "cut through the recessed floor" do not degrade into "occasionally
eats the recess ring wall it was supposed to run inside of." This is a calc.py
responsibility (Q4), not a model.py ordering fix — ordering only decides which existing
selector sees which edges first, it does not bound where cutouts are allowed to sit.

## Q2 — Bore rim edge selection for keyway / hex bores

### Why the current selector breaks silently, not loudly

`_bore_rim_edges(solid, r_bore, face_width)` (`model.py:213-232`) does two things:
rejects edges not on an end face, and rejects edges whose points (sampled at 4 stations,
`positionAt(s/4)`) exceed `lim = r_bore + 0.01` from the axis. It does **not** filter on
`geomType()` — the docstring's "arc plus a straight line" is a description of what a
D-flat bore rim happens to be, not a type check the code enforces. That is good news: a
hex bore's rim (six `LINE` edges per face) does not need a new edge-type branch, `on_rim`
already accepts straight edges.

The one thing that must change is `lim`. Today `lim = r_bore + 0.01` is correct because
every point on a round or D-flat rim lies within `r_bore` of the axis (D-flat is a
circle-intersect-rectangle, so it is a strict subset of the circle — verified from
`_cut_bore`'s own construction, `model.py:186-189`). A **hex** bore's vertices sit
*outside* the inradius: for a regular hexagon with across-flats `w`, the circumradius
(vertex distance from centre) is `w/√3 ≈ 0.577w`, not `w/2`. Verified against the
installed cadquery 2.8.0: `Workplane.polygon(nSides, diameter, circumscribed=True)`
builds the polygon *circumscribed* about a circle of the given diameter — i.e. `diameter`
passed as the across-flats value already gives the right hex, but the code computing
`lim` for edge selection must use the **circumradius**, not the across-flats/2 apothem,
or every hex-vertex point will fail the `hypot <= lim` test and `on_rim()` will return
**zero edges for every face** — `.chamfer(chamfer, None, [])` is not an error in
cadquery, it is a silent no-op. The bore would build correctly and simply ship with no
chamfer, with no warning anywhere, for every hex-bore request. This is the single
highest-value catch in this research: it is exactly the kind of failure L08 exists to
prevent for *dimensions*, but the existing edge-selection code has no equivalent
guard for *geometry selection* — a selector that matches nothing fails silently today
(confirm with a unit test asserting `len(_bore_rim_edges(...)) > 0` whenever
`bore_chamfer > 0`, for every bore shape — this test does not exist yet, grep of
`tests/test_model.py` found only volume/bounding-box/triangle-count assertions, no edge-
count assertion).

**Recommended change.** Replace the inline `r_bore` scalar `_cut_bore` currently passes
to `_bore_rim_edges` with a single calc.py-computed **rim limit** per bore shape:

```python
# calc.py — new, pure math, no kernel
def bore_rim_limit(p: GearParams) -> float:
    """Farthest any point on the bore's rim wire can be from the axis, for edge
    selection — NOT the same as the bore's characteristic radius. Round and D-flat:
    the circle radius already bounds every point. Hex: the vertex (circumradius),
    which is larger than the across-flats/2 apothem the "size" of the bore is
    expressed in."""
```

`model.py` then calls `bore_rim_limit(p) + 0.01` instead of deriving `lim` from
`r_bore` inline — keeping the "what counts as the bore's extent" decision in calc.py
(pure math, testable without the kernel) and leaving model.py's selector unchanged in
shape (still a single radial cutoff test, still shape-agnostic on edge type).

**Keyway is a separate, harder case — flag for a phase-level decision, not a default
assumption.** A keyway slot's floor sits at `r_bore + keyway_depth`, which is *larger*
than the base bore's own rim limit by construction (the whole point of a keyway is that
it cuts outward past the round/hex bore's rim). Two honest options:

1. **Extend `bore_rim_limit()` to include the keyway** (`r_bore + keyway_depth +
   keyway_clearance`) so its two long side edges and floor edge get chamfered too. Risk:
   this pulls the radial cutoff outward, closer to (or past) wherever body cutouts or the
   recess ring sit, reopening the "cutout edges wrongly counted as bore rim" collision Q1
   avoided by ordering — it would need the same MIN_WALL-style clearance calc.py already
   enforces elsewhere (Q4) to stay safe.
2. **Do not chamfer the keyway's own edges in v0.2** — `bore_chamfer` continues to apply
   only to the round/hex bore's circular or hex rim, and the keyway slot mouth ships
   un-chamfered. Lower risk (no selector change beyond Q2's hex fix), smaller surface,
   and a keyway slot is functionally about fit, not about a printed edge needing a
   chamfer the way a round bore's press-fit lip does.

This research recommends **option 2** as the default for the first phase that ships
keyway (simplest thing that works, per CLAUDE.md's "keep it simple"), with option 1 left
as a named follow-up if the human wants keyway edges chamfered too. This is a product
call the plan for that phase should make explicit, not infer.

**Recess-floor selector (`_groove_floor_edges`) is not at risk from either bore
change.** It filters strictly on `e.geomType() == "CIRCLE"` (`model.py:207-208`) — a
hex or keyway bore introduces only `LINE` edges near the axis, which this filter already
excludes regardless of position. No change needed there for Q2; only Q1's body-cutout
interaction with the recess ring's own circular walls needs new calc.py guards.

## Q3 — `GearParams` shape: discriminator vs. additive groups

**Recommendation: additive flat-field groups, one per feature, each gated by its own
explicit "off" sentinel — not a `bore_type` discriminator.** Three reasons, all grounded
in what is already in the tree:

1. **The milestone requires composition, not selection.** PROJECT.md is explicit:
   cutouts "compose... with any bore profile, and with each other where geometry
   allows," and keyway is "explicit width, depth and clearance" layered on top of
   whichever base bore shape is in use. A keyway is additive to a round *or* hex bore,
   not an alternative to one — a `Literal["round", "d_flat", "hex", "keyway"]`
   discriminator would force keyway to be mutually exclusive with hex, which contradicts
   the stated requirement. The composable cases need independent on/off fields; only the
   base bore *shape* (round vs. D-flat vs. hex) is genuinely mutually exclusive, and that
   already has a precedent in the tree.

2. **The precedent already in the codebase is flat 0-sentinel fields, not a
   discriminator, for exactly this shape of choice.** `bore_flat: float = 0` (0 = round)
   already turns "round vs. D-flat" into an additive field rather than a
   `bore_type: Literal[...]`, and `check()` already validates it in place
   (`calc.py:140-142`). `recess_sides` is the one place the codebase *does* use a
   `Literal` discriminator — but it discriminates a genuinely small, closed, orthogonal
   choice (which faces), not a shape family that other fields need to layer on top of.
   Adding `bore_hex_flats: float = 0` (0 = off) alongside the existing `bore_flat`, with
   `check()` refusing `bore_flat > 0 and bore_hex_flats > 0` (422 naming both fields,
   same shape as the existing D-flat range check), is a two-line diff to `calc.check()`
   and zero new concepts — versus a discriminator, which would need new schema/form/CLI
   handling the `_f()` helper and JSON-schema-driven form do not have today (they assume
   every field is independently meaningful and independently defaultable).

3. **L02 and L05 both assume flat fields.** "A field added once shows up in all three"
   (L02) and "every shareable model link omits the fields it left at default" (L05) are
   both trivially true for a new `_f(0, ...)` field — the JSON schema, the CLI flag
   generator, and the URL query-string all already handle "any subset of fields present,
   rest at default" with no extra code. A discriminated union field would still appear
   as one flat field in the schema (fine), but the fields *conditional on* that
   discriminator would need either (a) all being present regardless, ignored unless the
   discriminator selects them — which is exactly the additive-groups model already, just
   with an extra unused field — or (b) a nested/conditional schema shape neither the web
   form nor argparse generation supports today. Additive groups get the "ignored unless
   its own value is non-default" behavior for free.

### Concrete field additions

```python
# --- Bore (extends the existing group) --------------------------------------------
bore_hex_flats: float = _f(0.0, 0, 200, ..., help="Across-flats for a hex bore. 0 = not hex.")
keyway_width:   float = _f(0.0, 0, 50,  ..., help="Keyway slot width. 0 = no keyway.")
keyway_depth:   float = _f(0.0, 0, 50,  ..., help="Keyway depth, measured outward from the bore surface.")
keyway_clearance: float = _f(0.0, 0, 1, ..., help="Added to width and depth for print shrinkage.")

# --- Body (new group) ---------------------------------------------------------------
spoke_arms:      int   = _f(0, 0, 24, ..., help="Spoke arm count. 0 = solid web.")
spoke_arm_width: float = _f(0.0, 0, 50, ...)
spoke_hub_d:     float = _f(0.0, 0, 400, ...)
spoke_rim_wall:  float = _f(0.0, 0, 50, ...)

hole_count:          int   = _f(0, 0, 48, ..., help="Lightening hole count. 0 = none.")
hole_d:              float = _f(0.0, 0, 50, ...)
hole_bolt_circle_d:  float = _f(0.0, 0, 400, ...)

hex_cell_size:      float = _f(0.0, 0, 20, ..., help="Hex honeycomb cell size. 0 = none.")
hex_wall_thickness: float = _f(0.0, 0, 5, ...)

# --- Teeth (extends existing group) --------------------------------------------------
tip_chamfer: float = _f(0.0, 0, 3, ..., help="Chamfer on the tooth tip edges. 0 = none.")
```

Every one of these defaults to 0 = off, satisfying L05 directly: a pre-v0.2 URL, which
never mentions any of these names, produces a `GearParams` identical in every new field
to a fresh v0.2 default, and the pipeline's new cut functions are no-ops whenever their
gating field is 0 (same idiom `_cut_face_recesses` and `_cut_bore` already use for
`recess_sides == "none"` and `bore_d <= 0`).

**Conflicts that belong in `check()` (422, naming fields), not a discriminator:**
`bore_flat > 0 and bore_hex_flats > 0`; `keyway_width > 0 and bore_d <= 0`; body-cutout
combinations that claim the same web area (spoke_arms and hex_cell_size both non-zero is
very likely a genuine conflict — both want exclusive use of the annulus between hub and
rim; spoke_arms and hole_count together is plausibly fine — holes cut into the spokes or
gaps — but this is a product-shape call, not something derivable from the docs read for
this research, and should be a named decision in whichever phase plans body cutouts,
not an assumption baked into a plan silently.**

## Q4 — New `DerivedDimensions` fields, and which validation moves to `calc.py`

**New fields (additive — existing 19 fields and their meanings stay exactly as they
are, per PROJECT.md's "`DerivedDimensions` grows additively; caliper, span and
centre-distance formulas are not touched"):**

| Field | Null when | Purpose |
|---|---|---|
| `bore_hex_flats_effective` | not a hex bore | across-flats + clearance, `bore_effective`'s hex analogue |
| `keyway_effective_width` / `keyway_effective_depth` | no keyway | requested + clearance, actual values used |
| `tip_chamfer` | `tip_chamfer == 0` | actual chamfer used, after capping to fit the tip land |
| `spoke_arm_actual_width` | `spoke_arms == 0` | requested width, capped to fit `spoke_arms` around the circumference without overlap |
| `spoke_web` | `spoke_arms == 0` | material left in the hub/rim walls the spokes connect, mirrors `web`'s recess role |
| `hole_actual_d` | `hole_count == 0` | requested hole Ø, capped to clear neighbours on the bolt circle |
| `hole_to_bore_wall` / `hole_to_rim_wall` | `hole_count == 0` | remaining wall between the hole circle (inner/outer edge) and the bore radius / root radius — the number `check()` and the capping functions both need to decide refuse-vs-cap |
| `hex_cell_count` | `hex_cell_size == 0` | cells that actually fit the available web annulus, after the build-time cap (see below) |

**Validation that moves to `calc.py` (mirrors the existing `recess_radii()` /
`root_fillet()` / `check()` split exactly):**

- *Cap-and-warn* (trimmable without contradicting an explicit choice, same test L03 uses
  for `root_fillet`/`recess_width` today): `tip_chamfer` capped to fit the tip land
  width; `hole_actual_d` capped to stop neighbouring holes overlapping on the bolt
  circle; `spoke_arm_actual_width` capped to stop neighbouring arms overlapping;
  `hex_cell_count` capped by the build-time budget (see below).
- *Refuse (422, naming fields)*, same test as the existing `bore_flat` range check and
  the existing `bore_d > pr.rf - MIN_WALL` check: `keyway_width` not between a sane
  fraction and the full bore diameter (mirrors the existing `bore_flat` range check
  verbatim); `keyway_depth` pushing the keyway floor past `rf - MIN_WALL` (mirrors the
  existing "bore too large for root" check); `bore_flat > 0 and bore_hex_flats > 0`
  together; `spoke_arms * spoke_arm_width` implying more than 360° of arc; the
  cutout-family conflicts named in Q3.

**`hex_cell_count` is the one new number that cannot be capped by a purely dimensional
rule the way everything else in this table can — flag prominently.** Every other cap in
`calc.py` today (`root_fillet`, `recess_width`, `recess_fillet`) bounds a *dimension*
against another *dimension*, computed once, cheaply, with no dependency on how long
OpenCascade will take to cut the result. A hex-honeycomb pattern's cost is not one
boolean cut, it is **N boolean cuts**, one hexagonal prism per cell, and N is exactly
`hex_cell_count` — the number whose only honest source is a build-time measurement, not
a formula. PROJECT.md already names this as "the unknown" ("recess + hex pattern is the
unknown," "every new cut gets a measured build time... against
`SPUR_BUILD_TIMEOUT=30s`"). This research's recommendation: `hex_cell_count`'s cap must
be produced the same way L17's memory ceiling was — **swept, not derived** — by a
phase-level benchmark that measures wall-clock build time as a function of cell count on
the heaviest allowed gear (large face width, small module, small cell size), and the cap
formula calc.py ships is the one that benchmark justifies, cited by a new `Lxx` decision
entry, not a number picked by inspection. Treat this as its own phase-level research
task, not something the roadmap should assume is a simple geometry formula.

## Q5 — Cache key and the L05 regression test

**The cache key already generalizes with zero code change, and this is verifiable from
what is already in the tree, not merely asserted.** Two mechanisms use `GearParams` as
(part of) a cache key:

- `app.py`'s `_EXPORTS`: `key = (params, fmt, q.quality, encoding)`
  (`app.py:387,398`), an `OrderedDict` keyed by **value equality**, not object identity —
  confirmed by the existing, passing test
  `test_a_second_identical_download_is_served_from_the_byte_cache`
  (`tests/test_api.py:272`), which only makes sense if two independently-constructed
  `GearParams` instances with the same field values compare equal and hash equal. Pydantic
  v2's frozen `BaseModel` derives `__hash__`/`__eq__` from every field, so adding new
  fields to `GearParams` changes *what counts as equal*, automatically, with no code
  edit anywhere in `app.py` or `model.py`.
- `pool.py`'s `BuildPool.executor_for`: `hash(p) % self.workers` (`pool.py:97`) — this is
  **routing affinity, not a correctness key** (the docstring already says so: "affinity,
  not load-balance"); a hash collision between two different parameter sets just means
  they share a worker, which is harmless. New fields changing `hash(p)`'s numeric value
  cannot break correctness here by construction.

**What this means for the L05 proof.** Because equality is field-value-based, a
"pre-v0.2 parameter set" *is* a `GearParams` constructed with only the pre-v0.2 field
names — every v0.2 field lands at its 0/off default. The claim to prove is not about the
cache at all; it is about the **build pipeline**: does `_build(p)` for such a `p`
produce the same solid it produced before v0.2's cut steps existed? Since every new cut
function is gated by its own field being non-default (`_cut_body` no-ops when
`spoke_arms == hole_count == hex_cell_size == 0`, `_chamfer_tips` no-ops when
`tip_chamfer == 0`, the generalized `_cut_bore` falls through to the existing round/
D-flat branch when `bore_hex_flats == keyway_width == 0`), the pipeline is unchanged in
behaviour for that input — but this needs to be a **test**, not an inference, per
CLAUDE.md ("Predicting that tests pass is not the same as running them").

**Recommended regression test**, extending the existing pattern
(`tests/test_model.py::test_builds_one_valid_solid`'s parametrized `kw` matrix, and
`tests/test_calc.py::test_default_dimensions`, `calc.py:266-272`'s Anti-Pattern entry
already names this exact test as the guard against defaults drifting):

1. Before starting v0.2 work, capture a fixture: for a representative matrix of
   pre-v0.2 `GearParams` (the same matrix `test_builds_one_valid_solid` already uses is
   a strong starting set), record `derive(p)` as a serialized `DerivedDimensions` and
   `build(p)`'s `.Volume()` / `.BoundingBox()` — **not** raw export bytes, because L24
   already established OCCT export is not byte-reproducible across independently built
   solids even for identical geometry (content equivalence — volume, bounding box,
   triangle count — is the standard this codebase already uses, not a byte diff).
2. After each v0.2 phase, re-run `derive(p)` and `build(p)` for the same matrix and
   assert equality against the captured fixture, field by field for
   `DerivedDimensions`, and `pytest.approx` for `Volume()`/`BoundingBox()` — same
   tolerance style `test_recess_removes_expected_volume` already uses
   (`tests/test_model.py:37-44`).
3. This is a new fixture-based test, not an extension of `test_default_dimensions`
   (which only checks the stock-default `GearParams()`, one point, not a matrix) — name
   it for what it proves, e.g. `test_pre_v0_2_parameter_sets_are_unchanged`, and cite
   L05 in its docstring the way `test_default_dimensions`'s Anti-Pattern entry already
   does in `ARCHITECTURE.md`'s own "Anti-Patterns" section.

## Q6 — Suggested build order across phases

Ordered by dependency, not by feature-list order in PROJECT.md:

1. **Foundation: generalize `_cut_bore`'s rim-edge selection (Q2) + add the L05
   regression fixture (Q5), with no new user-facing feature yet.** This is the
   riskiest silent-failure surface (Q2's "chamfer selects nothing") and the safety net
   (Q5's fixture) both phases 2-5 depend on to prove they changed nothing for old links.
   Doing this first means every subsequent phase's own tests run against a fixture that
   already exists, rather than each phase inventing its own ad hoc "did I break the old
   defaults" check.
2. **Hex bore.** Exercises the generalized `bore_rim_limit()` (Q2) end to end on the
   simplest new shape (one polygon cut, one chamfer selection, no interaction with
   recesses or body cutouts). Smallest surface that proves Q2's fix actually works
   against a real hex geometry, not just the theoretical circumradius argument above.
3. **Keyway bore.** Builds on (2)'s generalized bore-shape plumbing; decide and ship
   the Q2 "chamfer covers the keyway or not" call explicitly in this phase, since it is
   the one open product question this research could not resolve from the docs alone.
4. **Tip chamfer.** Independent of bore and body work (different edges, different
   region of the solid); can run in parallel with (2)/(3) if the roadmap wants a
   parallel track, since it touches neither `_cut_bore` nor the recess step.
5. **Body cutouts — lightening holes first, then spoke arms, then hex pattern last.**
   Holes are the simplest cut (a `polarArray` of circles — verified against installed
   cadquery 2.8.0, `Workplane.polarArray(radius, startAngle, angle, count, fill,
   rotate)` exists and pushes points for exactly this use) and the cheapest to
   benchmark. Spoke arms need the Q1 recess-floor-overlap clearance rule worked out
   for a shape that is not a simple circle-radius test (an arm's clearance from `r_in`/
   `r_out` is angular as well as radial). The hex honeycomb pattern goes last on
   purpose: it is the only feature in this milestone whose safe parameter range is not
   knowable without a build-time sweep (Q4), so it should not gate the phases that do
   not depend on it, and its own phase should open with the benchmark (mirroring how
   L17's memory ceiling was swept before `mem_limit` was set) before any cap formula is
   written into `calc.py`.
6. **Composition pass.** Once (2)-(5) each work in isolation, a dedicated phase (or
   phase-closing task set) exercises the stated composition matrix explicitly — recess +
   each bore shape, recess + each cutout type "cut through the recessed floor," keyway +
   hex bore, cutout + cutout pairs — and is where the Q3 cutout-family conflict rules
   (spoke vs. hex, etc.) get decided and written into `check()` rather than assumed.
   This phase is also the natural place to re-run the Q5 fixture one final time and to
   run the "heaviest allowed configuration" build-time measurement PROJECT.md's Success
   Metric 2 requires (recess + hex pattern combined against `SPUR_BUILD_TIMEOUT=30s`).

## Anti-Patterns to Avoid (specific to this integration)

### Anti-Pattern: generalizing `lim`/radius cutoffs by widening them "to be safe"

**What people do:** faced with a hex bore's vertices falling outside `r_bore`, widen
`lim` generously (e.g. `r_bore * 2`) so nothing gets missed.

**Why it's wrong:** a wide `lim` reopens exactly the collision Q1's cut ordering was
designed to avoid — nearby body-cutout or recess-ring edges get swept into the bore
chamfer selection. The fix is to compute the *exact* geometric bound per bore shape in
calc.py (Q2's `bore_rim_limit()`), not to pad an existing constant.

### Anti-Pattern: treating `hex_cell_count`'s cap as a dimensional formula

**What people do:** cap cell count with a formula like "web area / cell area," the same
shape as every other cap in `calc.py`.

**Why it's wrong:** every existing cap in `calc.py` bounds a dimension against another
dimension computed in microseconds; `hex_cell_count`'s real constraint is wall-clock
build time under `SPUR_BUILD_TIMEOUT`, which is not a function calc.py can derive
without a kernel measurement (Q4). A plausible-looking area-based formula is exactly the
"reported a warning and a plausible number instead of a measured one" shape L08 forbids
for dimensions — the same standard applies here to a count that gates build time.

### Anti-Pattern: a `bore_type` discriminator "for cleanliness"

**What people do:** since round/D-flat/hex bore shapes are mutually exclusive, wrap
them in one `Literal` field for a tidier schema.

**Why it's wrong:** keyway needs to compose with whichever shape is chosen (Q3), and the
milestone explicitly requires that composition. A discriminator that only covers the
shape triad still leaves keyway as an independent field, so nothing is actually saved,
and the codebase's own `_f()`/schema/CLI-generation machinery has no support for fields
conditional on a discriminator's value today — it would be new machinery for zero
benefit over `check()`'s existing conflict-refusal pattern.

## Integration Points (file-level)

| Point | File | Change |
|---|---|---|
| New field groups | `src/spur/params.py` | additive `_f(0, ...)` fields, Q3 |
| New cap/refuse logic | `src/spur/calc.py` `check()` | additive conflict checks, Q3/Q4 |
| New derived fields | `src/spur/calc.py` `DerivedDimensions`, `derive()` | additive fields, Q4 |
| Bore-shape generalization | `src/spur/model.py` `_cut_bore`, `_bore_rim_edges` | branch on shape, generalize `lim` via new `bore_rim_limit()` in calc.py, Q2 |
| New cut step | `src/spur/model.py` `_cut_body` (new function) | inserted after `_cut_bore`, before tip chamfer, Q1 |
| New cut step | `src/spur/model.py` `_chamfer_tips` (new function) | last step in `_build()`, Q1 |
| Pipeline order | `src/spur/model.py` `_build()` | append two calls, Q1 |
| Regression fixture | `tests/test_model.py` or new `tests/test_regression.py` | new fixture-based test, Q5 |
| No change needed | `src/spur/app.py`, `src/spur/pool.py`, `src/spur/cli.py` | cache key and CLI flag generation already generalize (Q5, L02) |

## Sources

- `src/spur/params.py` (read in full) — `GearParams`, `_f()` helper.
- `src/spur/model.py` (read in full) — `_build`, `_cut_face_recesses`,
  `_cut_bore`, `_groove_floor_edges`, `_bore_rim_edges`, cache/export mechanics.
- `src/spur/calc.py` (read in full) — `recess_radii`, `root_fillet`, `check`,
  `DerivedDimensions`, `derive`.
- `src/spur/app.py:41-90,355-420` — `_BlobCache`, `/api/model.{fmt}` cache key.
- `src/spur/pool.py` (read in full) — `BuildPool.executor_for`, affinity semantics.
- `docs/architecture/decision_log.md` — L02, L03, L05, L08, L09, L17, L19, L24
  specifically cited above.
- `.planning/PROJECT.md` — v0.2 milestone scope, Success Metrics, constraints.
- `.planning/codebase/ARCHITECTURE.md` — prior codebase map (2026-09-21), cross-checked
  against the current source rather than trusted standalone.
- `tests/test_model.py`, `tests/test_api.py`, `tests/test_calc.py` — existing test
  patterns cited as precedent for Q5's recommended regression test.
- cadquery 2.8.0, installed at `.venv/lib/python3.12/site-packages/cadquery/cq.py`
  (verified directly, not from memory): `Workplane.polarArray()` (line 1436),
  `Workplane.polygon(nSides, diameter, circumscribed=)` (line 2649) — confirms the hex
  bore's across-flats parameter maps directly to `polygon(..., circumscribed=True)`, and
  that a bolt-circle hole pattern has a direct one-call primitive.

---
*Architecture research for: spur v0.2 "Fit to Shaft"*
*Researched: 2026-09-25*
