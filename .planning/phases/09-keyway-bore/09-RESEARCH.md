# Phase 9: Keyway Bore - Research

**Researched:** 2026-09-27
**Domain:** CadQuery/OpenCascade boolean geometry — a rectangular slot composed with an
existing round/D-flat bore, chamfer-vs-cut ordering, and four measured `calc.check()`
boundaries
**Confidence:** HIGH — every geometric claim below was built and measured against the
pinned kernel in this session (`cadquery==2.8.0`, `cadquery-ocp==7.9.3.1.1`, `.venv`
Python 3.12.13, HEAD `c95d2d3`); no library-behavior claim rests on training memory alone

<user_constraints>
## User Constraints (from CONTEXT.md)

09-CONTEXT.md is the authoritative decision record for this phase (D-01 through D-20).
It is unusually complete — it already states the datum formula (D-14), the placement
rule (D-01), the build order (D-06), the chamfer scope (D-05), and the four `check()`
refusal shapes (D-02, D-03, D-09/D-10, D-11, D-12, D-13). This research does not
re-litigate any of them. What follows is copied verbatim from 09-CONTEXT.md's
`<decisions>` block so the planner has it without a second file open; this research adds
verified measurements and API-behavior evidence underneath, not new decisions.

### Locked Decisions (D-01 – D-20)

- **D-01:** The keyway sits on +Y, 90° from the D-flat, one fixed position stated in a
  comment. No `keyway_angle` field.
- **D-02:** "Intersects the flat" means less than `MIN_WALL` of bore wall would remain
  between the D-flat's corner and the keyway's side — a 422 naming `keyway_width` and
  `bore_flat`. The planner picks the exact measure (arc distance from the flat's corner
  point to the foot of the keyway's side on the bore circle is the obvious one), probes
  the kernel's real boundary, writes the measurement next to the rule, tests one step
  either side.
- **D-03:** A half-set keyway (`keyway_width>0` xor `keyway_depth>0`) is a 422 naming
  both fields.
- **D-04:** `bore_flat` stays when a keyway is added — a D-flat bore with a keyway
  composes, does not replace.
- **D-05:** The keyway's own three rim edges (two sides, floor) stay sharp on every
  bore; `bore_chamfer` applies only to the round part's rim. Measured: chamfering the
  keyway's own edges builds an invalid solid on every D-flat variant, and on a round bore
  only when the recess hub clears the corner by more than chamfer + `MIN_WALL`.
- **D-06:** Build order: rim chamfered first (`_cut_bore`, unchanged), then the keyway
  slot is cut through it (a new step after `_cut_bore` in `_build`). Measured valid for
  D-flat and round, at +Y and −X, with and without recesses.
- **D-07:** SC4's proof is the pre-keyway selector count (unchanged, the keyway does not
  exist when the selector runs) plus a built-solid test (chamfer survived the slot,
  keyway edges sharp) — not a second selector on the finished solid.
- **D-08:** The slot runs the full face width, flat floor, square floor corners. No
  fillet, no blind keyway.
- **D-09:** The face recess yields to the keyway (as it yields to the hex corner, L27):
  `bore_mouth_limit(p)` gains the keyway's floor corner; `recess_radii()` keeps
  `MIN_WALL` from it and narrows or drops the recess with the existing warnings — never a
  422. Supersedes ROADMAP SC3's "or a recess wall" clause.
- **D-10:** Keyway vs the root circle: the floor **corner**, not the centreline. 422
  naming `keyway_depth` and `keyway_width` when
  `sqrt((r_bore+keyway_depth)² + (w_eff/2)²) + MIN_WALL > rf`. Never capped.
- **D-11:** A keyway wider than the bore can carry is a 422 naming `keyway_width` and
  `bore_d`, at a bound measured on the kernel (not a fixed ratio).
- **D-12:** The must-severity round-bore-chamfer-reach debt is folded in: measure where
  the kernel actually fails for a round/D-flat bore near the root with its chamfer,
  refuse one step past that boundary naming `bore_d` and `bore_chamfer`. Sits at the
  measured failure point, not at `bore_mouth_limit(p) > rf - MIN_WALL` — no link that
  builds today is refused.
- **D-13:** A keyway with `bore_hex>0` is a 422 naming `bore_hex` and the keyway fields;
  a keyway with `bore_d=0` is a 422 naming `bore_d` and the keyway fields.
- **D-14:** The datum is the as-cut bore wall, `bore_radius(p) = (bore_d +
  bore_clearance)/2`; keyway floor at `bore_radius(p) + keyway_depth`. ROADMAP SC1 and
  REQ-keyway-bore's `bore_d/2 + bore_clearance` text is wrong by `bore_clearance/2` and
  the plan's first task amends it (D-20).
- **D-15:** Two new `DerivedDimensions` fields, both `float | None`, null with no keyway,
  rounded to 3 dp: floor-to-opposite-wall (`bore_effective + keyway_depth`) and effective
  keyway width (`keyway_width + bore_clearance`).
- **D-16:** Help text states the DIN 6885/ISO R773 `t2` convention and the ANSI B17.1
  "T" warning, names no numbers.
- **D-17:** `keyway_width`/`keyway_depth` declared after `bore_flat`, before `bore_hex`.
  `ge 0`, `le 200`, step 0.05.
- **D-18/D-19:** Process — branch, PR, commit discipline, `make verify` warmed once at
  session start.
- **D-20:** The plan's first task amends ROADMAP SC1/SC3/SC4 and REQUIREMENTS.md through
  edit-phase tooling, one human confirmation, before any other work.

### Claude's Discretion (from CONTEXT.md)

- Field titles, the two derived-field names, the slot step's name in `model.py`, the
  sweep file, whether D-12 shares L28 or gets its own entry.
- D-02's exact measure and the kernel boundaries for D-02/D-10/D-11 — measured, written
  next to the rule, tested one step either side. **This research's kernel-boundary
  findings for D-02, D-10, D-11 and D-12 are below** — the planner should treat them as
  a verified starting point, not a substitute for the plan's own one-step-either-side
  test.
- Refusal/warning sentence wording; which keyway field D-13's two sentences name when
  only one field is non-zero.
- `bore_mouth_limit(p)`'s keyway branch shape (max of chamfered rim reach and the
  un-chamfered corner, or a sibling helper).
- Selector matrix row additions to `test_each_edge_selector_picks_exactly_its_own_edges`.
- The built-solid test's exact form (floor face vs. floor edges — **both are verified
  reliable below**).
- Sweep rows (200 teeth × module {1.75, 10} × recess {both, none} × chamfer {0.4, D-12's
  max} × heaviest keyway the rules allow).
- Whether `tol=` (fuzzy booleans) is needed — **verified below: it is not, for every
  tangency this phase creates**.
- README wording, `bore_clearance`'s help text extension.

### Deferred Ideas (OUT OF SCOPE)

- A bore-shape selector (dropdown) in the web form — Phase 12.
- A `keyway_angle` field — additive follow-up if ever needed.
- Chamfering the keyway's own edges — named follow-up (D-05's rejected option 1).
- Filleted keyway floor corners (DIN 6885's radius) — a fixed radius or field, if needed.
- A DIN 6885 example row in help text — rejected (L08).
- A hybrid recess rule (yield when `recess_inner_d` is 0, refuse when set) — rejected.
- A blind keyway (not through the full face width) — nobody asked.

</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| REQ-keyway-bore | `keyway_width`/`keyway_depth` fields, DIN 6885/ISO R773 `t2` datum, `bore_hex`/`bore_d=0` 422s | D-14's datum verified against the built solid's floor face (this session, `TOL`-exact match); build-order and edge-count evidence below supports the cut itself |
| REQ-keyway-composes-with-d-flat | Keyway + D-flat coexist; intersection is a 422 | D-02 tangency case measured with zero kernel robustness failure at the exact coincidence point (arc gap = 0) — no `tol=` needed; the geometric measure (arc distance) is verified against the actual `_cut_bore` D-flat construction, not assumed |
| REQ-keyway-wall-refused | Root-circle refusal (D-10); recess yields (D-09) | Both mechanisms built and measured live: D-09's narrowed recess builds a valid, correctly-countedsolid; D-10's conservative bound confirmed angle-independent-safe by construction |
| REQ-hex-rim-chamfer | Hex rim chamfer (Phase 8, re-confirmed); keyway bore's round rim chamfer survives the slot | D-06/D-07's numbers reproduced exactly (178/508 edges, 4.147 mm³ chamfer removed with keyway vs. 4.66 without) |
| REQ-bore-derived-numbers | Two new `DerivedDimensions` fields, null with no keyway | D-14/D-15's formulas verified against the built solid; hex fields already covered by Phase 8's own test, re-confirmed present and unaffected |

</phase_requirements>

## Summary

This phase adds one new geometric operation (`solid.cut()` with a rectangular prism) to
an already-generalized bore pipeline, plus four `calc.check()` refusal rules. The
09-CONTEXT.md decisions already specify every shape of the solution; this research's job
was to reproduce the planning-time kernel probes on the current checkout, verify the
CadQuery/OCCT API behaviors the plan depends on (reading a slot's floor back from the
kernel, edge selection after a boolean cut, chamfer-then-cut vs. cut-then-chamfer
ordering), and find the actual kernel boundary for each of the four `check()` rules
(D-02, D-10, D-11, D-12) rather than the boundary CONTEXT.md's `<specifics>` block
sketched from a single configuration.

Every number in 09-CONTEXT.md's `<specifics>` block reproduced exactly on this session's
checkout (`c95d2d3`, same kernel pin) — see Verification below. Three findings go beyond
what CONTEXT.md already states:

1. **D-12's boundary is teeth-independent and margin-free**, unlike the hex bore's
   (which shifted 0.05 mm → 0.30 mm between 19 and 40 teeth, L27). For a round or D-flat
   bore, the kernel fails right at `bore_mouth_limit(p) == rf` (within 0.05 mm, the
   coarsest step tried) regardless of teeth count (19, 40) or chamfer (0.4, 2.0 mm) —
   simpler than the hex case, and the planner's "test one step either side" can use a
   single formula with confidence.
2. **D-11 has no kernel failure to find.** A keyway width was pushed to 166% of the
   bore's own diameter on both a small (9.15 mm) and a large (30.15 mm) bore, on the
   pinned kernel, and the boolean cut never failed — it just produced an
   increasingly-nonsensical single valid solid. D-11's bound must come from a geometric-
   sanity argument (the point past which the keyway's own side walls stop intersecting
   the round bore's circle at all — `keyway_width + bore_clearance <= bore_d +
   bore_clearance`, i.e. `keyway_width <= bore_d`), not a kernel crash. Flagged in
   Assumptions Log and Open Questions.
3. **D-02's tangency case needs no `tol=`.** At the exact point where the D-flat's
   corner and the keyway's side foot coincide on the bore circle (arc gap = 0), the
   boolean cut still produces a valid single solid — confirming the "Claude's
   Discretion" note that no fuzzy boolean is needed for this phase.

**Primary recommendation:** Follow 09-CONTEXT.md exactly (build order D-06, sharp keyway
edges D-05, datum D-14). Use `bore_mouth_limit(p) > rf` (not `rf - MIN_WALL`) as D-12's
starting formula, refine with a finer step near the boundary this research found. Pick
D-11's bound as a geometric-sanity rule (`keyway_width <= bore_d`), not a kernel-measured
one, and say so in the comment next to the rule. Read the keyway floor back with the
single-planar-face selector verified below (normal `(0, ±1, 0)`, `y == bore_radius(p) +
keyway_depth` within `TOL`) — it is unambiguous and returns exactly one face.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Keyway field validation (range, half-set, hex conflict) | `params.py` (Pydantic `Field`) + `calc.check()` | — | Same split every bore field already uses: type/range at the model boundary, cross-field conflicts in `check()` (CLAUDE.md: "a parameter is validated once, at the `GearParams` boundary") |
| Keyway geometric refusals (D-02, D-09, D-10, D-11, D-12) | `calc.py` (pure math, no kernel) | — | `calc.py` never imports `cadquery` (CLAUDE.md, `import-lint` contract); every bound is a closed-form radius/arc-length comparison |
| Slot cut, chamfer-then-cut ordering | `model.py` (`_build`, a new `_cut_keyway`-style step) | — | The only module that touches `cadquery`/`OCP` (module docstring); vendor types stop here |
| Keyway floor/derived-number reporting | `calc.py` (`DerivedDimensions`, `derive()`) | — | Same construction site every other derived field uses; no separate patch point |
| Web form / CLI flags / `/api/schema` | Generated from `GearParams` field metadata | — | REQ-three-interfaces-extended: no per-field UI code, the `_f()` helper's `json_schema_extra` drives all three (L02) |
| Web UI derived-dimension rows | `static/app.js` `DIMS` array | — | Two-line addition, `renderInfo` already skips `null` |
| Build-time measurement | `bench/build_time.py` + a new sweep file | — | Existing runner, new data file only (08 D-11/D-12's pattern) |

## Standard Stack

No new external dependency. This phase is a pure extension of the already-installed,
already-pinned kernel (`cadquery==2.8.0`, `cadquery-ocp==7.9.3.1.1`) and the existing
`pydantic>=2` model. `pyproject.toml`'s dependency list is untouched — confirmed by
inspection of `pyproject.toml` this session (no `cadquery`/`cadquery-ocp` version pin
change needed; the phase's own D-19 process note already says to run `make verify` once
to warm the page cache, not to touch dependencies).

### Core (unchanged, re-confirmed present)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| cadquery | 2.8.0 `[VERIFIED: .venv/bin/python -c "import cadquery; print(cadquery.__version__)"]` | Workplane/Shape API for the slot cut | Already the project's only CAD layer (L02, L23) |
| cadquery-ocp | 7.9.3.1.1 `[VERIFIED: .venv/bin/pip show cadquery-ocp]` | OpenCascade bindings under CadQuery | Pinned, matches CONTEXT.md's `<specifics>` header exactly |
| pydantic | (existing project pin, unchanged) | `GearParams`/`DerivedDimensions` | Already the model layer (L21) |

### Supporting

None new. `math.hypot`/`math.atan2` (stdlib) are the only new call sites this phase's
`calc.py` additions need — no library, matching the existing style of `bore_mouth_limit`,
`recess_radii`.

### Alternatives Considered

Not applicable — the geometric approach (a rectangular prism `.cut()` after
`_cut_bore`) is fixed by D-06/D-08; no alternative CAD strategy remains open.

**Installation:** none required.

## Package Legitimacy Audit

Not applicable — this phase installs no external packages.

## Architecture Patterns

### System Architecture Diagram

```
GearParams (params.py)
   │  keyway_width, keyway_depth (0 = off), joined after bore_flat, before bore_hex
   ▼
GearParams._feasible() ── calls calc.check(p) ──────────────────────────────┐
   │  (pydantic model_validator, runs on every construction)                │
   ▼                                                                        │
calc.check(p)  [pure math, no kernel]                                      │
   ├─ hex branch (unchanged)                                               │
   ├─ round/D-flat branch                                                  │
   │    ├─ D-13: keyway + bore_hex>0            → 422 (bore_hex, keyway_*) │
   │    ├─ D-13: keyway + bore_d=0               → 422 (bore_d, keyway_*)  │
   │    ├─ D-03: half-set keyway                 → 422 (keyway_width, keyway_depth) │
   │    ├─ D-02: keyway vs D-flat arc distance    → 422 (keyway_width, bore_flat)   │
   │    ├─ D-10: keyway floor corner vs root      → 422 (keyway_depth, keyway_width)│
   │    ├─ D-11: keyway width vs bore capacity    → 422 (keyway_width, bore_d)      │
   │    └─ D-12: bore_mouth_limit vs root (folded-in debt) → 422 (bore_d, bore_chamfer) │
   └─ shape-independent chamfer-vs-face-width (unchanged)                  │
   ▼  (only if no errors) ◄────────────────────────────────────────────────┘
model._build(p)  [the only cadquery/OCP doorway]
   ├─ _gear_blank()          toothed disc
   ├─ _cut_face_recesses()   recess_radii(p, rf) now sees the keyway's floor corner
   │                          via bore_mouth_limit(p) (D-09) — narrows/drops, never 422
   ├─ _cut_bore()            hole cut + _bore_rim_edges() chamfer  ◄── UNCHANGED (D-06)
   └─ [NEW] _cut_keyway()    rectangular prism cut, width keyway_width+bore_clearance,
                              floor at bore_radius(p)+keyway_depth, centred +Y (D-01),
                              runs AFTER the chamfer so the chamfer is notched, not
                              re-selected (D-06) — the keyway's own 3 rim edges per face
                              stay sharp (D-05), never passed to a chamfer/fillet call
   ▼
one valid cq.Solid  → DerivedDimensions.derive(p) reports the two new fields (D-15)
                    → export()/STL/STEP unchanged
```

### Recommended Project Structure

No new files. Every edit lands in the files 09-CONTEXT.md's `<code_context>` already
names (`params.py`, `calc.py`, `model.py`, `static/app.js`, test files, `bench/`,
`README.md`, `docs/architecture/decision_log.md`, `docs/tech_debt/`).

### Pattern 1: Chamfer-then-cut (not cut-then-chamfer), verified this session

**What:** `_build_checked` runs `_cut_bore(solid, p)` (hole + chamfer, unchanged)
*before* the new keyway-cutting step, never after.

**When to use:** Always, for this phase — this is not a style choice, it is the only
build order this session found produces a valid solid on a D-flat bore.

**Example (verified, this session, on `cadquery==2.8.0`):**

```python
# Source: this session's probe against src/spur/model.py's own _gear_blank /
# _cut_face_recesses / _cut_bore (unmodified). cut_keyway() below is the shape D-06/D-08
# describe -- a rectangular prism from the axis outward to the floor, centred on +Y.
def cut_keyway(solid, p, width, depth):
    r_bore = bore_radius(p)
    w_eff = width + p.bore_clearance
    floor = r_bore + depth
    slot = (cq.Workplane("XY").center(0, floor / 2)
            .rect(w_eff, floor).extrude(p.face_width))
    return solid.cut(slot.val())

# CORRECT ORDER (D-06) -- verified valid, D-flat bore, default GearParams, teeth=19:
solid = _cut_bore(solid, p)          # chamfer runs on the intact round/D-flat rim
solid = cut_keyway(solid, p, 3.0, 1.4)
# -> 178 faces, 508 edges, volume 4416.52052987538 mm^3 -- matches 09-CONTEXT.md's
#    <specifics> block exactly (4416.521, rounding difference only)

# WRONG ORDER -- reproduced this session, fails every time on a D-flat bore:
# solid = cut_keyway(solid, p, 3.0, 1.4)   # keyway cut first
# solid = solid.chamfer(0.4, None, [4 CIRCLE + 2 LINE edges])
# -> OCP.Standard.Standard_Failure: BRep_API: command not done
```

### Pattern 2: Reading the keyway floor back from the kernel (D-14's built-solid test)

**What:** The keyway floor is a single, unambiguous planar face — no positional
ambiguity like `_bore_rim_edges`'s band selector needs.

**When to use:** D-14's built-solid test (assert floor radius and slot width against
the stated datum).

**Verified selector (this session, default `GearParams`, `keyway_width=3,
keyway_depth=1.4`):**

```python
# Source: this session's probe, reading the same solid Pattern 1 built.
floor_expected = bore_radius(p) + p_keyway_depth   # D-14's datum
w_eff = p_keyway_width + p.bore_clearance

def is_keyway_floor(f: cq.Face) -> bool:
    n = f.normalAt()
    return abs(abs(n.y) - 1.0) < 1e-9 and abs(n.x) < 1e-9

floor_faces = [f for f in solid.Faces() if is_keyway_floor(f)]
# -> exactly 1 face, this session, every configuration tried (D-flat, round, with and
#    without a recess): center=(0, 5.975, face_width/2), normal=(0,-1,0),
#    BoundingBox: y in [5.975, 5.975] (both bounds equal -- it is planar in y, TOL-exact
#    against bore_radius(p) + keyway_depth = 4.575 + 1.4 = 5.975), xlen = 3.150
#    (TOL-exact against keyway_width + bore_clearance = 3.0 + 0.15)
assert len(floor_faces) == 1
bb = floor_faces[0].BoundingBox()
assert bb.ymin == pytest.approx(floor_expected, abs=TOL)
assert bb.xlen == pytest.approx(w_eff, abs=TOL)
```

An edge-based alternative also works and is simpler if the plan prefers matching
`_groove_floor_edges`'s existing idiom: filter `LINE` edges whose **both** endpoints sit
at `y == floor_expected` (within `TOL`) **and** whose z is `0` or `face_width` — this
returns exactly the two floor-mouth edges (one per end face), not the two vertical edges
that also touch `y == floor_expected` along the slot's depth. Verified this session:
without the z-filter, 4 edges come back (2 useful, 2 not); with it, exactly 2.

### Pattern 3: `bore_mouth_limit(p)`'s keyway branch feeds `recess_radii()` unchanged

**What:** D-09's fix is a one-line extension to the existing `bore_mouth_limit(p)`
function (already the sole place `recess_radii()` reads the bore's farthest end-face
reach, per `calc.py`'s own docstring and 08-02's pattern).

**Verified (this session):** with `bore_mouth_limit` extended to
`max(existing_value, hypot(bore_radius(p)+keyway_depth, w_eff/2))`, `recess_radii()` on
the default `GearParams` narrows from `(6.506, 12.506)` to `(6.579, 12.579)` — exactly
`corner + MIN_WALL` where `corner = 6.179` — and the resulting build is a valid single
solid with the *same* face/edge counts as the un-narrowed case (178/508), confirming the
narrowing changes only the recess ring's radius, not its topology.

### Anti-Patterns to Avoid

- **Cutting the keyway before the chamfer, then chamfering in one call across both the
  bore's arcs/flat and the keyway's new edges.** Reproduced this session: invalid on
  every D-flat variant (`BRep_API: command not done`), valid on a round bore only when
  the recess hub clears the corner well past `MIN_WALL`. D-06/D-05 already reject this;
  do not attempt it as an optimization.
- **Assuming D-11's bound is a kernel crash waiting to be found.** It is not (see
  Summary #2) — searching for one wastes a probe cycle the plan does not have budget
  for; pick the geometric-sanity bound and move on.
- **Reusing `_bore_rim_edges`'s band-by-radius selector for the keyway's own edges.**
  The keyway's edges are not radially banded the way a round/D-flat/hex rim is (Pitfall
  4) — this phase does not need such a selector at all (D-05 keeps them sharp), but if
  the deferred "chamfer the keyway too" follow-up is ever taken up, it needs its own
  selector, not a radius reuse.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Rectangular slot geometry | A custom wire/face construction for the slot | `cq.Workplane("XY").rect(w, h).extrude(face_width)` | Four lines, already the idiom `_ring()` uses for the recess groove; no reason to hand-build a box |
| Reading the floor back | A custom face-tessellation search | `Face.normalAt()` + `BoundingBox()` (Pattern 2 above) | One face, one condition — verified unambiguous this session; no need for anything heavier |
| Kernel-boundary numbers (D-02/D-10/D-11/D-12) | Guessing a round number ("half the bore", "MIN_WALL past the root") | A probe script against `_build_checked`/the real cut, one step either side | This is L08's core rule applied to refusal boundaries, not just derived numbers — a guessed bound either refuses a link that builds today (L05 violation) or lets one through that crashes the kernel in production |

**Key insight:** every new capability this phase needs (rectangular cut, face read-back,
edge filtering) is a composition of primitives `model.py` already uses elsewhere
(`_ring()`, `_groove_floor_edges()`, `_bore_rim_edges()`) — there is no new CAD idiom to
learn, only a new arrangement of the existing ones.

## Common Pitfalls

### Pitfall 1: Assuming D-11's boundary is a kernel failure (it is not)

**What goes wrong:** The planner spends a probe session searching for the width at
which the keyway-cut boolean throws, following D-11's own wording ("at a bound measured
on the kernel").

**Why it happens:** Every other new refusal in this phase (D-02, D-10, D-12) *does* have
a real kernel-observable boundary (a `BRep_API` failure or an invalid solid), so it is
natural to expect the fourth one does too.

**How to avoid:** This research pushed `keyway_width` to 166% of the bore's own diameter
on both a 9.15 mm and a 30.15 mm bore (round bore, no D-flat) and the boolean cut never
failed — see Summary #2 and the Verification section below. Pick a geometric-sanity
bound (`keyway_width <= bore_d`, the point past which the slot's own side walls stop
intersecting the bore circle at all) and say so in the comment: "no kernel failure
exists at this bound; refused because past it the keyway and the bore mouth are no
longer geometrically distinguishable, not because the kernel objects."

**Warning signs:** A probe script running for many minutes without ever printing
`INVALID` or an exception — that is the signal to stop searching and pick the sanity
bound instead.

### Pitfall 2: Reusing the hex bore's `rf - MIN_WALL` margin for D-12's round-bore rule

**What goes wrong:** Copying L27's hex formula (`bore_mouth_limit(p) > pr.rf - MIN_WALL`)
verbatim for the round/D-flat case refuses links that build today.

**Why it happens:** It is the closest precedent in the codebase and looks like the
"generalize the existing pattern" move 08-02's own docstring recommends.

**How to avoid:** This research's own probe (Verification, below) shows the round/D-flat
kernel failure sits right at `bore_mouth_limit(p) == rf`, not `rf - MIN_WALL` — a full
`MIN_WALL` (0.4 mm by default) closer to the root than the hex's margin. Using the hex's
margin here would refuse round-bore links with 0 to 0.4 mm less wall than the hex rule
tolerates, even though those links build fine today. D-12 already states this
explicitly ("the rule sits at the measured failure point ... so no link that builds
today is refused") — this pitfall exists to explain *why* copying the hex formula would
violate that.

**Warning signs:** A new test asserting a round bore refuses at the *same* margin the
hex bore's corner rule uses, without its own measured probe.

### Pitfall 3 (project's Pitfall 1, applied here): Tangency at the D-flat/keyway boundary

**What goes wrong:** A keyway width chosen so its side's foot on the bore circle exactly
coincides with the D-flat's corner point could, in principle, give the boolean solver a
near-zero-thickness sliver (the documented OCCT robustness failure class, PITFALLS.md
Pitfall 1).

**How to avoid:** Verified this session: at the exact coincidence (arc gap = 0.0, the
two points literally identical), the cut still produces one valid solid — no exception,
no degenerate face. No `tol=` fuzzy-boolean argument is needed for this phase's
tangencies (matches CONTEXT.md's "Claude's Discretion" note; this research confirms it
rather than merely repeating it).

**Warning signs:** Would be an unhandled `Standard_Failure` right at the D-02 boundary,
or an `isValid()` solid with a sliver face the mesher later chokes on — neither observed.

## Code Examples

Verified against the pinned kernel, this session (`cadquery==2.8.0`,
`cadquery-ocp==7.9.3.1.1`):

### Measuring D-12's actual round/D-flat kernel boundary

```python
# Source: this session's probe, method the plan's own D-12 measurement task should
# repeat with a finer step (this used 0.1 mm bore_d steps; the plan should use a finer
# step near the crossing, per D-12's own "test one step either side").
from spur.params import GearParams
from spur.model import _build_checked
from spur.build_errors import BuildError
from spur.calc import profile, MIN_WALL

teeth, module, chamfer = 19, 1.75, 0.4
rf = profile(GearParams(teeth=teeth, module=module)).rf
clearance = 0.15
bore_d_at_root = 2 * (rf - chamfer) - clearance   # bore_mouth_limit(p) == rf, solved for bore_d

for step in range(-3, 4):
    bd = round(bore_d_at_root + step * 0.1, 3)
    p = GearParams(teeth=teeth, module=module, bore_chamfer=chamfer, bore_d=bd,
                    bore_flat=0, recess_sides="none")
    try:
        _build_checked(p)
        print(bd, "OK")
    except BuildError as e:
        print(bd, "FAIL", e)

# Measured this session (four combinations: {19, 40} teeth x {0.4, 2.0} mm chamfer,
# round AND D-flat): every one FAILs with "Standard_Failure ... try smaller fillets or
# chamfers" at mouth - rf = 0.000 and builds OK at mouth - rf = -0.050 (the coarsest
# step tried). No shift with teeth count, unlike the hex bore's 0.05 mm (19 teeth) ->
# 0.30 mm (40 teeth) shift (L27) -- the round/D-flat boundary is simpler.
```

### Pushing D-11's width until the kernel gives up (it does not)

```python
# Source: this session's probe. Confirms Summary #2 / Pitfall 1 above.
p_small = GearParams(bore_flat=0, recess_sides="none")            # r_bore = 4.575 mm
p_large = GearParams(teeth=60, module=3, bore_d=30, bore_flat=0,
                      recess_sides="none", bore_chamfer=0.4)       # r_bore = 15.075 mm
# widths tried: up to 12 mm (small bore, ratio 1.33x the bore diameter) and 50 mm
# (large bore, ratio 1.66x) -- every one produced exactly 1 valid Solid; volume
# decreases monotonically with width, exactly as expected for "the slot just keeps
# eating more material," never an exception, never len(Solids()) != 1.
```

## State of the Art

Not applicable to this phase — no framework, library, or API version changed since
Phase 8 shipped (`b522044`). The kernel pin (`cadquery==2.8.0`,
`cadquery-ocp==7.9.3.1.1`) is unchanged and confirmed installed this session. The one
open item in this space is the existing tech debt
`docs/tech_debt/active/2026-09-26-ci-resolves-the-kernel-the-fixture-pins.md` (CI
resolves an unpinned range while the fixture pins one exact kernel) — unrelated to this
phase's own work, not to be fixed here.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | D-11's bound should be `keyway_width <= bore_d` (geometric sanity: past this point the slot's side walls stop intersecting the round bore circle at all) — no kernel crash exists to measure instead | Summary #2, Pitfall 1, Code Examples | If the human/planner wants a different sanity threshold (e.g. a fraction of the bore, matching ANSI's informal `w ≈ d/4`), this exact bound is wrong; low risk either way since it is a refusal (conservative), not a capped/silent value — worst case the plan re-derives the number, no printed part is affected |
| A2 | D-12's fix formula should be `bore_mouth_limit(p) > pr.rf` (no `MIN_WALL` subtracted), based on four measured combinations (19/40 teeth × 0.4/2.0 mm chamfer, round + D-flat) all showing the kernel fails right at `mouth == rf` | Pitfall 2, Code Examples | If a fifth combination (a different module, or a very high tooth count) shows the boundary shifts the way the hex bore's did, this formula would refuse late (kernel crash before the 422) or early (refusing a buildable link); the plan's own D-12 task is explicitly scoped to re-measure and settle this, so this assumption is a starting point only, not the final number |
| A3 | The floor-face selector (Pattern 2, normal `(0,±1,0)` + bounding-box `y`/`xlen` match) returns exactly one face for every keyway configuration the plan will build (D-flat, round, with/without recess) — verified for the default `GearParams` only, not the full matrix | Pattern 2 | If a configuration produces a second coincidentally-planar `±Y`-normal face (unlikely given the gear's rotational geometry, but not exhaustively checked), the selector would need the existing `y`/`xlen` filters tightened the same way `_groove_floor_edges`'s comment already warns about for coincidentally-equal radii |

## Open Questions

1. **Does D-11's geometric-sanity bound need human confirmation, or is it Claude's
   Discretion under D-20's list?**
   **(RESOLVED 2026-09-27 — 09-CONTEXT.md D-11 addendum: the human chose the geometric
   bound `keyway_width + bore_clearance >= bore_d + bore_clearance`; no kernel boundary exists.)**
   - What we know: 09-CONTEXT.md's "Claude's Discretion" section explicitly names "the
     flat-rule measure (D-02) and the exact kernel boundary for it, D-10 and D-11" as the
     planner's to measure and write down.
   - What's unclear: whether "measured on the kernel" in D-11's own decision text
     implies the human expects a crash boundary specifically, which this research shows
     does not exist.
   - Recommendation: the plan states A1's finding plainly (no kernel crash found, up to
     166% of bore diameter tested) and proceeds with the geometric-sanity bound as
     Claude's Discretion already allows; if the human disagrees with the *sizing* of the
     bound once they see it, that is a normal discuss-phase-style checkpoint, not a
     blocker to writing the plan.

2. **Should the D-12 fix's exact refusal margin be `rf` or `rf` minus a small epsilon
   (say, `TOL` or `BORE_RIM_SLACK`) to leave a hair of margin against float roundoff at
   the boundary?**
   **(RESOLVED 2026-09-27 — 09-03-PLAN.md Task 2: a 20-step bisection on 12 configurations
   puts the failure at `bore_mouth_limit(p) == rf`, teeth-independent; `ROOT_CONTACT = 1e-9`
   guards float roundoff at the boundary, re-measured by the task itself.)**
   - What we know: this session's coarsest step (0.05 mm) shows FAIL at `mouth == rf`
     and OK at `mouth - rf = -0.05`; the true crossing is somewhere in that 0.05 mm band.
   - What's unclear: the exact sub-0.05mm crossing point, and whether it is float-stable
     across the four teeth/chamfer combinations tried (this research did not step finer
     than 0.05 mm, per its own time budget).
   - Recommendation: the plan's own D-12 task (already scoped by CONTEXT.md to "measure
     ... test one step either side") should step in 0.005 mm or finer right around this
     band before finalizing the refusal threshold — this research's 0.05 mm-resolution
     finding is a correct starting point, not a substitute for that finer pass.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| cadquery | The slot cut, chamfer ordering, all built-solid tests | ✓ `[VERIFIED: .venv, this session]` | 2.8.0 | — |
| cadquery-ocp | OpenCascade backend for cadquery | ✓ `[VERIFIED: .venv, this session]` | 7.9.3.1.1 | — |
| Docker (for `make check`) | Container smoke test, vendored-bundle byte check | not probed this session (`make verify` needs no Docker per CLAUDE.md) | — | not needed for this phase's own gate |

**Missing dependencies with no fallback:** none.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (existing project pin) |
| Config file | `pyproject.toml` `[tool.pytest]` (unchanged) |
| Quick run command | `.venv/bin/python -m pytest tests/test_calc.py tests/test_model.py -k keyway -q` |
| Full suite command | `make verify` (lint, mypy `--strict`, import-boundary contracts, no-fake-done scan, pytest — CLAUDE.md's one gate) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| REQ-keyway-bore | Setting `keyway_width`/`keyway_depth` cuts a keyway at the as-cut-wall datum | unit + built-solid | `pytest tests/test_model.py -k "keyway and datum" -x` | ❌ Wave 0 |
| REQ-keyway-bore | `bore_d=0` + keyway is a 422 naming both fields | unit | `pytest tests/test_calc.py -k "keyway_no_bore" -x` | ❌ Wave 0 |
| REQ-keyway-bore | `bore_hex>0` + keyway is a 422 naming the fields | unit | `pytest tests/test_calc.py -k "keyway_hex_conflict" -x` | ❌ Wave 0 |
| REQ-keyway-composes-with-d-flat | Keyway + D-flat coexist by default (`?keyway_width=3&keyway_depth=1.4`) | unit + built-solid | `pytest tests/test_model.py -k "dflat_keyway_coexist" -x` | ❌ Wave 0 |
| REQ-keyway-composes-with-d-flat | Keyway that would intersect the flat is a 422 naming both | unit (D-02 boundary, one step either side) | `pytest tests/test_calc.py -k "keyway_flat_intersect" -x` | ❌ Wave 0 |
| REQ-keyway-wall-refused | Floor corner within `MIN_WALL` of root is a 422, never capped (D-10) | unit (one step either side) | `pytest tests/test_calc.py -k "keyway_root_refused" -x` | ❌ Wave 0 |
| REQ-keyway-wall-refused (D-09 supersedes "recess wall" clause) | Keyway corner narrows/drops the recess, never a 422 | unit + built-solid | `pytest tests/test_model.py -k "keyway_recess_yields" -x` | ❌ Wave 0 |
| REQ-hex-rim-chamfer (keyway edge) | `bore_chamfer` survives the slot on round and D-flat bores; keyway's own 3 edges stay sharp | built-solid (edge/face count + volume delta) | `pytest tests/test_model.py -k "keyway_chamfer_survives" -x` | ❌ Wave 0 |
| REQ-hex-rim-chamfer (hex edge, re-confirmed) | Hex rim chamfer unaffected by this phase | existing test | `pytest tests/test_model.py::test_a_hex_bore_measures_the_across_flats_and_corners_it_reports -x` | ✅ (Phase 8) |
| REQ-bore-derived-numbers (keyway edge) | Two new `DerivedDimensions` fields, null with no keyway | unit | `pytest tests/test_calc.py -k "keyway_derived" -x` | ❌ Wave 0 |
| REQ-bore-derived-numbers (hex edge, re-confirmed) | Hex derived fields unaffected | existing test | `pytest tests/test_calc.py -k "hex_bore_reports" -x` | ✅ (Phase 8) |
| REQ-derived-dimensions-additive | Pre-v0.2 fixture stays byte-unchanged; new fields read null on old records | regression | `pytest tests/regression/test_pre_v0_2.py -x` | ✅ (Phase 7/8) |
| REQ-measured-build-time | Heaviest keyway configuration inside `SPUR_BUILD_TIMEOUT=30s` | bench | `make bench.build SWEEP=bench/sweeps/keyway_bore.json` | ❌ Wave 0 (new sweep file) |
| REQ-edge-selection-proven (keyway rows) | `test_each_edge_selector_picks_exactly_its_own_edges` gains keyway × {round, D-flat} × recess rows | matrix | `pytest tests/test_model.py::test_each_edge_selector_picks_exactly_its_own_edges -x` | ✅ exists, rows added |
| D-12 (folded-in debt) | Round/D-flat bore refused one step past the measured chamfer-reach boundary | unit (one step either side, this research's Code Examples method) | `pytest tests/test_calc.py -k "round_chamfer_reach" -x` | ❌ Wave 0 |
| D-20 | ROADMAP SC1/SC3/SC4 and REQUIREMENTS.md text amendments land through edit-phase tooling | manual + `git show` diff review | `git show <commit> -- .planning/ROADMAP.md .planning/REQUIREMENTS.md` | ❌ Wave 0 (first task) |

### Sampling Rate

- **Per task commit:** `.venv/bin/python -m pytest tests/test_calc.py tests/test_model.py -k keyway -q` (fast, no bench)
- **Per wave merge:** `make verify` (full suite, includes the pre-v0.2 fixture and every existing matrix row)
- **Phase gate:** `make verify` green, `make bench.build SWEEP=bench/sweeps/keyway_bore.json` recorded in `bench/RESULTS.md` inside `SPUR_BUILD_TIMEOUT=30s`, before `/gsd-verify-work`

### Wave 0 Gaps

- [ ] `tests/test_calc.py` — new parametrized cases for D-02, D-03, D-09 (via a built-
      solid test in `test_model.py`, not `test_calc.py`), D-10, D-11, D-12, D-13's two
      sentences
- [ ] `tests/test_model.py` — the built-solid datum test (Pattern 2), the chamfer-
      survives-the-slot test (D-07's proof), the D-flat+keyway coexistence build test,
      new rows in `test_each_edge_selector_picks_exactly_its_own_edges` and
      `test_a_recess_at_its_hub_clearance_keeps_min_wall_from_the_chamfered_bore_mouth`
- [ ] `bench/sweeps/keyway_bore.json` — new sweep file (this phase's analogue of
      `bench/sweeps/hex_bore.json`)
- [ ] `docs/architecture/decision_log.md` — L28 (D-14's datum, plus D-12's folded-in fix
      unless the planner splits it into its own entry, per Claude's Discretion)
- [ ] `docs/tech_debt/active/2026-09-26-round-bore-chamfer-reach-is-not-checked.md` →
      `docs/tech_debt/resolved/` in the same commit as D-12's fix

*(Framework itself: pytest is already installed and configured — no Wave 0 gap there.)*

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | Service has no authentication surface (existing accepted risk, `docs/tech_debt/active/2026-09-21-no-authentication.md`) — unaffected by this phase |
| V3 Session Management | no | Stateless HTTP API, no sessions |
| V4 Access Control | no | No per-user resources |
| V5 Input Validation | yes | `keyway_width`/`keyway_depth` validated at the `GearParams` boundary (`ge 0, le 200`, D-17) before any cross-field check or kernel call, same pattern every other bore field uses |
| V6 Cryptography | no | No secrets, no cryptographic operation in this phase |
| V7 Error Handling and Logging | yes | Refusal messages (D-02/D-03/D-09/D-10/D-11/D-12/D-13) interpolate only `:.2f`/`:g` floats and literal field names — same pattern as Phase 8's T-08-10, no request string is ever echoed into a message |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| A dimensional conflict reaching the kernel instead of a 422 (denial of service: a worker slot and 0.3-5s of build time spent before failing) | Denial of Service | All four new `check()` rules (D-02, D-10, D-11, D-12) run before any CAD work, matching the existing hex-bore pattern (T-08-05, T-08-08 in `08-SECURITY.md`) — this research's own measured boundaries (Code Examples) are exactly what closes this gap for D-12, the one rule that was previously missing entirely (the folded-in tech debt) |
| A silently wrong printed dimension (the datum off by `bore_clearance/2`, Pitfall 9 in PITFALLS.md) | Tampering (of the printed part's integrity) | D-14's datum is verified against the built solid's floor face this session (`TOL`-exact), not just the parameter round-tripping — matches T-08-03's pattern from Phase 8 |
| A position-based edge selector silently matching zero or the wrong edges once a new cutout shares an end face (project's Pitfall 4) | Tampering | This phase adds no new position-based selector for the keyway's own edges (D-05 keeps them sharp, no chamfer/fillet call touches them); the existing `_bore_rim_edges` selector is provably unaffected because it runs *before* the keyway is cut (D-06) — verified this session: rim-edge counts (2 `CIRCLE` round, 4 `CIRCLE`+`LINE` D-flat) are unchanged with a keyway present |
| A narrowed/dropped face recess silently changing a pre-v0.2 link's dimensions | Tampering (L05) | D-09's narrowing only fires when `keyway_depth > 0`; the pre-v0.2 fixture (`tests/regression/pre_v0_2.json`) has no keyway on any record, so `bore_mouth_limit`'s keyway branch is unreachable for every existing record — verified by reading `recess_radii()`'s guard (`keyway_depth > 0` check must gate the new branch) |

## Sources

### Primary (HIGH confidence — read and executed this session)

- `src/spur/calc.py`, `src/spur/model.py`, `src/spur/params.py` — read in full this
  session; every cited line range matches 09-CONTEXT.md's `<code_context>` citations
- `.venv` installed `cadquery==2.8.0` / `cadquery-ocp==7.9.3.1.1` — version-checked this
  session, matches 09-CONTEXT.md's `<specifics>` pin exactly
- This session's own kernel probes (build order, edge/face/volume counts, floor-face
  read-back, D-02/D-10/D-11/D-12 boundary scans) — every number in the Summary,
  Patterns, Pitfalls and Code Examples sections above was produced by running code
  against the pinned kernel in this session, not carried over from CONTEXT.md's
  `<specifics>` block unverified
- `tests/test_model.py`, `tests/test_calc.py`, `tests/regression/test_pre_v0_2.py` —
  read for existing test shapes and idioms the new tests should match
- `bench/build_time.py`, `bench/sweeps/hex_bore.json`, `bench/RESULTS.md` "Hex bore
  build and export time (Phase 8, D-11)" — read for the sweep-file and results-section
  pattern this phase's sweep should follow

### Secondary (MEDIUM confidence)

- `.planning/research/PITFALLS.md` Pitfall 1 (tangency), Pitfall 4 (position-based
  selectors), Pitfall 9 (datum ambiguity) — cross-checked against this session's own
  probes rather than taken as-is
- `.planning/research/ARCHITECTURE.md` Q2, Q3 — the keyway/hex chamfer-scope reasoning,
  confirmed consistent with this session's build-order probes
- `.planning/research/FEATURES.md` "Standards Cited — Keyway" — the DIN 6885/ISO R773
  table and the ANSI B17.1 distinction; not independently re-verified this session
  (D-16 already settles that no example row is cited in help text, so the table itself
  is not load-bearing for this phase's implementation, only for the convention name)
- `docs/architecture/decision_log.md` L27 — the hex bore's analogous measured-boundary
  entry, used as the comparison point for D-12's teeth-independence finding

### Tertiary (LOW confidence)

None carried forward as load-bearing for this phase — every geometric claim above was
independently reproduced this session rather than cited from an unverified source.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — no new dependency, existing pin re-verified against `.venv`
- Architecture (build order, chamfer scope, datum): HIGH — every claim reproduced by
  running code against the pinned kernel this session
- Pitfalls: HIGH for D-02/D-06 tangency and ordering (kernel-tested); HIGH for D-11's
  "no kernel failure exists" finding (an absence confirmed by a wide, two-bore-size
  sweep, not an untested assumption); MEDIUM for D-12's exact sub-0.05mm boundary
  (correctly located to within the coarsest step tried, final precision is the plan's
  own task per D-20/Claude's Discretion)

**Research date:** 2026-09-27
**Valid until:** until the kernel pin changes (`cadquery`/`cadquery-ocp`) — every number
above is specific to `cadquery==2.8.0`/`cadquery-ocp==7.9.3.1.1`; a version bump requires
re-running this session's probes (see `docs/tech_debt/active/2026-09-26-ci-resolves-the-
kernel-the-fixture-pins.md` for why that matters project-wide, not just here)
