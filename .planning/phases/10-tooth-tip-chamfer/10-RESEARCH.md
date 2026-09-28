# Phase 10: Tooth-Tip Chamfer - Research

**Researched:** 2026-09-28
**Domain:** CadQuery/OCCT 3D edge chamfer on an extruded involute-gear solid; cost
measurement against `SPUR_BUILD_TIMEOUT`; a fourth position-based edge selector in the
Phase 7 selector family.
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

CONTEXT.md's decisions D-01 through D-17 are locked and are NOT re-litigated here. Full
text lives at
`.planning/phases/10-tooth-tip-chamfer/10-CONTEXT.md`; summarized below for the
planner's convenience. Read the CONTEXT.md file directly — this is a summary, not a
replacement.

### Locked decisions (D-01..D-17)
- **D-01:** Axial cap `c ≤ 0.45 × face_width` (both end faces chamfered; tip land keeps
  10% of face width).
- **D-02:** Radial cap `c ≤ ra − r` (addendum) — analytic, in `calc.py`, no kernel
  import; footprint stays above the pitch circle.
- **D-03:** Symmetric 45°, one field: `solid.chamfer(c, None, tip_edges)` —
  `bore_chamfer`'s exact call and meaning.
- **D-04:** The kernel is probed **inside** the analytic caps (D-01/D-02); if
  `Mixin3D.chamfer()` fails or yields an invalid solid inside that bound, the cap
  becomes the measured boundary one step inside, tested one step either side. Always a
  cap, never a 422.
- **D-05:** Plan 10-01 is a measurement-only spike — no field yet — that produces the
  numbers before the field/cap/selector/proof plans are written.
- **D-06:** A 9-row sweep at 200 teeth (08 D-11's shape: module × tip_chamfer ×
  recess_sides, 8 rows, plus one module-0.2 row) via a new `bench/sweeps/tip_chamfer.json`
  run by unchanged `bench/build_time.py`.
- **D-07:** A row over `SPUR_BUILD_TIMEOUT=30s` halts for a human decision; the
  pre-agreed first offer is lowering `tip_chamfer`'s `le`.
- **D-08:** One new `DerivedDimensions` field (`float | None`, on the order of
  `tip_chamfer_effective`), `null` when `tip_chamfer == 0`, rounded to 3dp.
- **D-09:** One warning sentence in the existing "reduced to X mm to …" family.
- **D-10:** `tip_chamfer` lives in the Teeth group, declared after `root_fillet`.
- **D-11:** Help text names the purpose and no size — the 0.1–0.2×module figure appears
  nowhere.
- **D-12:** SC1 is proven on the built solid by topology and bounding box (face count
  delta, volume, bounding box, unchanged selector counts elsewhere) — **the exact face
  and edge deltas are measured on the pinned kernel in the spike and pinned, not
  derived.**
- **D-13:** The tip selector is position-based (by radius `ra`), guarded, runs last
  (after `_cut_keyway`), gets a column on every existing selector-matrix row plus a
  200-tooth and a module-0.2 row.
- **D-14:** Tripwire (no-op patch, proves D-12's proof catches a vanished chamfer) plus
  guard (empty selection while `tip_chamfer > 0` is a `BuildError`).
- **D-15:** Defaults to 0 = off; pre-v0.2 fixture byte-unchanged; replay requires the new
  derived field null.
- **D-16:** L29 appended to `docs/architecture/decision_log.md`, append-only.
- **D-17:** Process — branch `gsd/phase-10-tooth-tip-chamfer`, cut from `origin/main`
  `277a98f`; `make pr.land PR=N`; plain `git commit`, explicitly staged files, never
  `git add -A`; run `make verify` once at session start.

### Claude's Discretion (research task: reduce these to concrete guidance below)
- Names: field title, derived field name, selector/step names in `model.py`, cap
  function name in `calc.py`, sweep file name, RESULTS.md section title.
- `tip_chamfer`'s `le`: **recommended 3, like `bore_chamfer`**.
- The selector's criterion: `_groove_floor_edges`'s shape (`geomType() == "CIRCLE"`,
  `radius()` within `TOL` of `ra`) vs `_bore_rim_edges`'s pure radial band — **this
  session's probe (see Code Examples) confirms the `_groove_floor_edges` shape is
  sufficient and simpler: no z-height filter is even needed.**
- The spike's probe path: a script under `bench/` or throwaway; must include the
  analytic-cap maximum at each (teeth, module) pair; D-04's boundary search should
  follow 09-03's bisection method (see Common Pitfalls / Code Examples below).
- Export time and the halt: recorded per row, not gated.
- Warning/help sentences, README example.
- Recess interaction: none expected — **confirmed by this session's probe** (see Code
  Examples).
- Sweep-row exactness: which bore/keyway the "default bore" rows carry, module-0.2
  recess.

### Deferred (OUT OF SCOPE — do not build)
- Analytic 2D tip-corner chamfer in `_outline()` — rejected reading; fallback ONLY if
  D-07's checkpoint finds no workable `le`, and only as a human-surfaced superseding
  decision.
- Chamfering the flank end-face edges (full end-face deburr).
- A second chamfer length or angle field.
- A teeth-dependent chamfer cap from measured per-edge cost (D-07's second option,
  checkpoint-only).
- Reporting the remaining tip land (`face_width − 2c`).
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| REQ-tip-chamfer | User can break the tooth-tip edges by setting `tip_chamfer` (mm, 0 = off): an edge-break chamfer on the tooth-tip arc edges at both end faces, selected by position; flanks, root fillets, bore and cutouts untouched, outside diameter unchanged. No sizing guidance in help text unless sourced. | `Mixin3D.chamfer()` semantics verified (Code Examples); tip-arc edges confirmed `CIRCLE` geomType at radius `ra`, exactly `2×teeth` per gear, both end faces (Code Examples probe); selector pattern from `_groove_floor_edges`/`_bore_rim_edges` (Architecture Patterns); build-order placement (Architecture Patterns "Tip chamfer last") |
| REQ-tip-chamfer-capped | A chamfer larger than the tip land allows is capped and reported in `warnings` (trimmable, L03). The chamfer operator's cost at the heaviest allowed configuration is measured against `SPUR_BUILD_TIMEOUT` and recorded; if it cannot fit, the cap is lowered and the number published. | Cap-function pattern from `root_fillet()`/`recess_fillet()` (Code Examples); `bench/build_time.py` + sweep-file mechanics (Architecture Patterns); Phase 8/9 `bench/RESULTS.md` section shape to copy (Code Examples) |
</phase_requirements>

## Summary

Tooth-tip chamfer is architecturally the simplest new cut in v0.2: it touches only the
tip-arc edges (radius `ra`, exactly `2 × teeth` of them, `CIRCLE` geomType, confirmed by
a probe this session — see Code Examples), it composes with nothing (it runs last,
after every other cut has already shaped the solid), and it reuses `bore_chamfer`'s
exact `Mixin3D.chamfer()` call and cap/warn contract verbatim. The only open technical
question — and the reason the phase carries a research flag — is cost: OCCT's chamfer
operator (`BRepFilletAPI_MakeChamfer`) is the same operator family L09 measured at ~50×
slower than the project's analytic-outline root fillet on a many-toothed profile. Phase
10 cannot reuse L09's analytic-outline remedy, because the locked reading (2026-09-25)
is a true 3D end-face edge break, not a 2D profile corner — so unlike root fillets, this
cost cannot be engineered away, only measured and capped if it proves too high (D-04,
D-07).

This session's probes (not the spike — a narrow feasibility check, see Code Examples)
confirm the approach works mechanically: chamfering the 38 tip edges of the default
19-tooth gear at `c = 1.0` mm succeeds, produces a valid solid, shrinks volume, leaves
`xlen`/`ylen` (and by extension `tip_d`) unchanged, and composes cleanly with an
already-present keyway + bore chamfer + recess. The face delta was exactly `+2×teeth`
(38) as D-12 expects; the edge delta was `+3×2×teeth` (114) — three new edges per
chamfer face (two flank-side tangent lines plus one reduced-radius tip arc), not one.
This 3:1 ratio should be re-confirmed at the spike's other configurations (200 teeth,
module 0.2) before D-12's proof test hard-codes it, since CONTEXT.md explicitly warns
the multiplier is not to be assumed.

The cost question remains genuinely open and is Plan 10-01's job, not this research's:
this session ran no 200-tooth chamfer timing (that is the spike). What this research
establishes is the *shape* the spike, the cap, the selector and the proof should take,
each backed by a working precedent already in the codebase (Phase 8's hex chamfer, Phase
9's keyway selector-matrix and built-solid proof, and 09-03's kernel-boundary bisection
method).

**Primary recommendation:** Build `_tip_edges(solid, pr)` in `model.py` using the
`_groove_floor_edges` shape (`geomType() == "CIRCLE"`, `radius()` within `TOL` of
`pr.ra`) — simpler than `_bore_rim_edges`'s radial-band test, and this session confirmed
no z-height filter is even necessary because no other geometry ever sits exactly at
`ra`. Wire the chamfer step onto the end of `_build()` after `_cut_keyway`. Cap `c` in
one new `calc.py` function (`tip_chamfer_effective(p)` or similar, planner's name)
mirroring `root_fillet()`'s three-line shape exactly. Run the D-05 spike first, before
writing the field.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| `tip_chamfer` field, schema, form, CLI flag | `params.py` (parameter model) | Web form / CLI (generated from schema) | One `Field()` declaration drives all three interfaces automatically (established pattern, L02) |
| Axial/radial cap arithmetic (D-01, D-02) | `calc.py` (pure math) | — | No kernel import allowed here (CLAUDE.md, import-boundary contract); the cap must be knowable without building |
| Kernel-measured boundary (D-04) | `calc.py` (constant + comment) | `model.py` (proven by test) | Same split as `ROOT_CONTACT`/L27's hex-corner bound: the number lives in `calc.py`, the kernel probe that produced it is a script/test, never a runtime call |
| Tip-arc edge selection and the chamfer cut | `model.py` (CAD kernel boundary) | — | The only module that imports `cadquery`; vendor types never escape it (CLAUDE.md) |
| Applied-value reporting + warning | `calc.py` `derive()` | — | Mirrors `root_fillet`/`recess_fillet`'s existing cap-then-report contract |
| Cost measurement (spike + sweep) | `bench/` (measurement, not the gate) | — | `bench/build_time.py`, unchanged, per 08 D-12; never part of `make verify` (D-16 in `bench/latency.py`'s stance) |

## Standard Stack

### Core

No new dependency. `cadquery==2.8.0` / `cadquery-ocp==7.9.3.1.1` are already pinned and
already expose everything this phase needs.

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| cadquery | 2.8.0 [VERIFIED: `.venv/lib/python3.12/site-packages`, `importlib.metadata.version('cadquery')` run this session] | `Mixin3D.chamfer()`, the exact call this phase reuses | Already the project's only CAD layer (L01); `bore_chamfer` already proves the call works in production |
| cadquery-ocp | 7.9.3.1.1 [VERIFIED: same command, this session] | `BRepFilletAPI_MakeChamfer`, the OCCT operator behind `Mixin3D.chamfer()` | Reached only through cadquery's wrapper; no direct OCP call needed |

### Supporting

None. No new pip package, no new JS dependency, no new file format.

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `Mixin3D.chamfer()` on the extruded solid (locked reading) | Analytic 2D tip-corner chamfer in `_outline()` (L09's remedy pattern) | Rejected 2026-09-25 as the wrong reading of "tip chamfer" — it changes the meshing profile (REQUIREMENTS "Out of Scope"). Not a technical fallback except via D-07's checkpoint, and only as a human-surfaced superseding decision, never silently. |

**Installation:** none — no `pip install` step this phase.

**Version verification:** confirmed this session via
`.venv/bin/python -c "from importlib import metadata; print(metadata.version('cadquery'))"`
→ `2.8.0`; `metadata.version('cadquery-ocp')` → `7.9.3.1.1`. Matches
`docs/research/STACK.md`'s prior finding and the versions Phase 8/9's `bench/RESULTS.md`
host-state headers record — no drift since Phase 9.

## Package Legitimacy Audit

**Not applicable this phase.** No new external package is installed; `cadquery` /
`cadquery-ocp` are pre-existing pinned dependencies (L01, L23), already audited in prior
phases. `bench/sweeps/tip_chamfer.json` is a data file, not a package.

## Architecture Patterns

### System Architecture Diagram

```
GearParams (params.py)
  tip_chamfer: float = 0  (Teeth group, after root_fillet)
        │
        ▼
GearParams._feasible() ── calc.check() ── no new refusal rule (D-04: always capped, never 422)
        │
        ▼
derive(p) [calc.py]
        │
        ├─▶ tip_chamfer_effective(p)  ── min(0.45×face_width, ra−r, measured_boundary)
        │        │
        │        ├─▶ DerivedDimensions.tip_chamfer_effective  (null when tip_chamfer==0)
        │        └─▶ warnings: "Tip chamfer reduced to X mm to …" (D-09, only if capped)
        │
        ▼
build(p) [model.py, worker process only]
   _build(p):
     _gear_blank(pr, root_fillet(p), face_width)   # tooth outline extruded
     _cut_face_recesses(solid, p, rf)                # existing
     _cut_bore(solid, p)                              # existing: hole + rim chamfer
     _cut_keyway(solid, p)                             # existing
     ── NEW: if tip_chamfer_effective(p) > 0:
              solid = solid.chamfer(c, None, _tip_edges(solid, pr))
     (appended last — the tip band is farthest from every other cut,
      and the selector can assume the final outline exists)
        │
        ▼
_build_checked(p)  ── one valid Solid, or BuildError
        │
        ▼
export(p, fmt, quality)  ── STL / STEP, unaffected code path
```

### Recommended Project Structure

No new files in `src/spur/`. Modified: `src/spur/params.py` (one field),
`src/spur/calc.py` (one cap function, one `derive()` warning branch, one
`DerivedDimensions` field), `src/spur/model.py` (one selector, one `_build()` append).
New: `bench/sweeps/tip_chamfer.json` (data), a probe script under `bench/` or throwaway
(D-05, planner's discretion on whether it is committed).

### Pattern 1: Cap function returns the applied value (not a bool, not a warning)

**What:** A pure `calc.py` function takes `GearParams` (plus whatever geometry it needs)
and returns the actually-usable value, already capped and rounded. `derive()` compares
requested vs. returned to decide whether to warn. `model.py` calls the *same* function,
never re-derives the cap — so the built part and the printed number cannot disagree
(L08).

**When to use:** Any dimension that is trimmed rather than refused (L03).

**Example — the existing precedent this phase's cap function should copy exactly:**
```python
# Source: src/spur/calc.py:201-206 (read this session)
def root_fillet(p: GearParams) -> float:
    """Root fillet actually used: the requested radius, capped to what fits the gap."""
    _, _, gap = _tooth(profile(p))
    return round(min(p.root_fillet, 0.45 * gap), 3) if gap > 0 else 0.0
```
A `tip_chamfer_effective(p)` function follows the identical shape: `round(min(p.tip_chamfer,
0.45 * p.face_width, pr.ra - pr.r), 3)`, with D-04's measured-boundary term folded in as
a third argument to `min(...)` only if the spike finds the kernel fails inside the
analytic caps.

### Pattern 2: Position-based selector, guarded, raising `BuildError` on empty selection

**What:** A `model.py` function takes the built solid (and whatever `calc.py` inputs it
needs) and returns exactly the edges one cut should touch, selected by geometric
position — never by insertion order or by type alone. Runs only when its feature is on.
Empty selection is *always* a `BuildError`, never a silent no-op (`Mixin3D.chamfer()`
with an empty edge list does nothing and raises nothing — SUMMARY.md's Known Conflict
#6 default-hex silent-failure story, the reason this guard exists at all).

**When to use:** Any chamfer/fillet edge set derived from the solid's own topology.

**Example — the simpler of the two existing selector shapes, and the one this phase's
selector should copy (confirmed sufficient by this session's probe — see Code
Examples):**
```python
# Source: src/spur/model.py:254-275 (read this session)
def _groove_floor_edges(solid: cq.Shape, radii: tuple[float, ...],
                        floor_z: list[float]) -> list[cq.Edge]:
    edges = [e for e in solid.Edges()
             if e.geomType() == "CIRCLE"
             and min(abs(e.radius() - r) for r in radii) < TOL
             and any(abs(e.startPoint().z - z) < TOL for z in floor_z)]
    if not edges:
        raise BuildError(
            "Recess fillet selected no groove-floor edges: a modelling defect in spur, "
            "not a conflict in these parameters. Set recess_fillet to 0 to build this "
            "gear without it.")
    return edges
```
A `_tip_edges(solid, pr)` selector needs only the `geomType() == "CIRCLE"` and
`radius()` test — this session's probe (Code Examples) found no other edge in the
built solid ever sits at radius `ra`, on either end face or anywhere else, so the
`floor_z`-style height filter `_groove_floor_edges` needs is not required here (both end
faces are wanted anyway, unlike a groove floor which is per-side). Match `_bore_rim_edges`'s
and `_groove_floor_edges`'s exact `BuildError` message shape (name the defect, name the
fix: "Set tip_chamfer to 0 to build this gear without it.").

### Pattern 3: Append the new cut last in `_build()`

**What:** `_build()` is currently four steps, "one decision per step" (CONTEXT.md's own
characterization). A new cut is added as a fifth line, never inserted between existing
steps, when its selector can assume the final topology and its edges don't overlap any
earlier cut's edges.

**Example:**
```python
# Source: src/spur/model.py:312-322 (read this session)
def _build(p: GearParams) -> cq.Solid:
    pr = profile(p)
    solid = _gear_blank(pr, root_fillet(p), p.face_width)
    solid = _cut_face_recesses(solid, p, pr.rf)
    solid = _cut_bore(solid, p)
    solid = _cut_keyway(solid, p)
    # NEW: solid = _chamfer_tips(solid, p, pr)   # last: farthest from every other cut

    solids = solid.Solids()
    if len(solids) != 1 or not solids[0].isValid():
        raise BuildError("Geometry kernel produced an invalid solid for these parameters.")
    return solids[0]
```
research/ARCHITECTURE.md's own reasoning for this placement: "It selects edges on the
tooth tip circle (`ra`), the region farthest from the axis and untouched by any
bore/recess/body cut — order relative to the other four cuts does not matter
geometrically, but placing it last keeps the new selector simple (it can assume the
full, final tooth outline is present)."

### Anti-Patterns to Avoid

- **Deriving the cap inside `model.py` from kernel geometry:** `calc.py` must compute
  the cap with no `cadquery` import (import-boundary contract, enforced by
  `lint-imports`); the cap has to be knowable on every keystroke, before any build runs.
- **A selector that trusts edge order or count alone:** must select by geometric
  position (radius test), the way every other Phase 7-generation selector does — never
  "the last N edges added."
- **Silently accepting an empty selection:** `Mixin3D.chamfer()` with `edgeList=[]` is a
  silent no-op in cadquery (confirmed by SUMMARY.md's hex-bore precedent) — always guard
  with `BuildError`.
- **Combining the axial cap and radial cap into a single opaque formula:** D-01 and D-02
  are two independently-reasoned geometric limits (tip-land / pitch-circle); keep them
  as two named terms inside one `min(...)` so the warning (D-09) can name which one
  bound the result.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| 3D edge chamfer on a solid | A custom mesh-edge-beveling routine | `Mixin3D.chamfer(length, length2, edgeList)` [VERIFIED this session: `inspect.getsource(Mixin3D.chamfer)` in the pinned `cadquery==2.8.0`] | Already proven correct and fast enough for the analogous `bore_chamfer` cut; OCCT's `BRepFilletAPI_MakeChamfer` handles the face-adjacency bookkeeping a hand-rolled version would have to reimplement |
| Kernel-boundary measurement | Guessing a safe margin | Bisection over the gap between last-failing and first-building configurations (09-03's method, see Common Pitfalls) | A guessed margin either refuses buildable links (against L05) or lets an unbuildable one reach a 500 |
| Cost measurement | A clock-based cap ("stop cutting when time runs out") | `bench/build_time.py` + a committed sweep file, `make bench.build SWEEP=…` | Explicitly rejected elsewhere in REQUIREMENTS.md ("A clock-based honeycomb cap … Non-reproducible across machines — violates L05/L08"); the same reasoning applies here — the cap must be the same value on every machine |

**Key insight:** every mechanism this phase needs already has a working, tested
precedent in the codebase (`bore_chamfer` for the cut, `root_fillet`/`recess_fillet` for
the cap, `_groove_floor_edges`/`_bore_rim_edges` for the selector, `ROOT_CONTACT`/L27's
hex-corner bound for the measured-boundary pattern, `bench/sweeps/hex_bore.json` /
`keyway_bore.json` for the sweep file). The phase's only genuine unknown is a number
(the cost), not a design.

## Runtime State Inventory

Not applicable — this is a greenfield additive feature (a new field, a new cut, a new
derived value), not a rename/refactor/migration. No stored data, live service config,
OS-registered state, secrets, or build artifacts carry the string `tip_chamfer` today.

## Common Pitfalls

### Pitfall 1: The chamfer operator's cost is genuinely unmeasured at 200 teeth

**What goes wrong:** `Mixin3D.chamfer()` and OCCT's fillet operator share
`BRepFilletAPI_Make*` machinery; L09 measured the fillet side of that family at ~50×
slower than the analytic-outline construction on a many-toothed profile. Phase 10 cannot
apply L09's remedy (the locked reading forbids the analytic 2D corner), so this cost, if
it is bad, cannot be engineered away — only capped.

**Why it happens:** OCCT's chamfer/fillet propagation logic scales with the number of
edges being chamfered simultaneously in one call, and this phase's call chamfers up to
`2 × 200 = 400` edges in one `solid.chamfer(c, None, tip_edges)`.

**How to avoid:** D-05's spike measures this *before* any field, cap, selector or proof
plan is written — exactly the order CONTEXT.md locks. Do not skip the spike or treat
Phase 8/9's hex/keyway numbers (5.08s, 4.85s of 30s) as a stand-in: those chamfer at most
12 edges, two orders of magnitude fewer than the 400 this phase's heaviest row chamfers.

**Warning signs:** A sweep row that crosses `SPUR_BUILD_TIMEOUT=30s` — D-07's pre-agreed
first response is lowering `tip_chamfer`'s `le`, not silently narrowing anything else.

### Pitfall 2: A chamfer set spanning mixed edge types can fail where a single-type set succeeds

**What goes wrong:** 09-CONTEXT.md's `<specifics>` records (from Phase 9's own
investigation) that "a one-shot chamfer on mixed arc + line edge sets failed
(`BRep_API: command not done`) where arcs alone were valid; edges of one type on one face
chamfer cleanly." The tip-arc edge set is homogeneous (every tip edge is a `CIRCLE`
segment, this session's probe confirmed 38/38 at 19 teeth), which CONTEXT.md already
flags as "the benign case, to be confirmed at 200 teeth" — the spike should not assume
this generalizes to 200 teeth without checking.

**Why it happens:** OCCT's chamfer builder walks each edge's adjacent-face topology
independently; a chamfer set with mixed curve types at differing tangency conditions can
produce a topology the propagation step cannot close.

**How to avoid:** The spike's probe (D-05) should explicitly confirm the tip-edge set
stays homogeneous and valid at 200 teeth and module 0.2 (the finest-tip case), not just
at 19/40 teeth.

**Warning signs:** `BRep_API: command not done` surfacing from `_build_checked`'s
catch-all as `"Geometry kernel failed (...); try smaller fillets or chamfers."` — this
message is the pre-existing catch-all wrapping *any* OCCT `Standard_Failure`, so it will
not distinguish a cost timeout from a genuine kernel rejection; the spike's own script
should catch and report the distinction explicitly (a wall-clock stopwatch vs. an
exception).

### Pitfall 3: A kernel-measured boundary requires re-measurement on the pinned kernel, not reuse of a stale number

**What goes wrong:** 09-CONTEXT.md's own precedent: the planning-time single-configuration
probe found a boundary of `7.6e-8 mm`; the session's own 12-configuration re-measurement
on the pinned kernel found `1.9e-8 mm` — nearly 4× tighter. A number carried forward
unverified from a different session or a different probe scope is not trustworthy.

**Why it happens:** The exact float-level boundary where OCCT's Boolean/chamfer
machinery starts failing is a property of the specific kernel build, the specific
configuration, and (per `ROOT_CONTACT`'s own comment) can vary with tooth count in ways
that are not obvious in advance (contrast: `ROOT_CONTACT` is teeth-independent; L27's hex
corner is not).

**How to avoid:** 09-03's method — bisect the gap between a known-failing and a
known-building configuration, 20 steps (enough for float precision at this scale, per
`_involute_angle`'s own 60-halving precedent for full double precision — 20 steps is what
09-03 actually used and recorded), across every (teeth, module) pair the spike samples,
not just one. Record the last-failing and first-building gaps explicitly, and whether
the boundary moved with tooth count/module (D-04 requires this comparison explicitly: "if
the boundary moves with tooth count or module such that no single rule keeps every
buildable chamfer buildable, the planner surfaces that as a checkpoint rather than
choosing").

**Warning signs:** A cap chosen from inspection or a single configuration's probe,
without the bisection step count and per-configuration results recorded next to the rule
(the way `ROOT_CONTACT`'s comment in `calc.py:16-32` records its own).

### Pitfall 4: `DerivedDimensions`' field set is checked as a literal enumerated string set in `tests/test_api.py`

**What goes wrong:** `test_openapi_documents_the_typed_contracts`
(`tests/test_api.py:62-88`, read this session) hard-codes the full set of
`DerivedDimensions` field names as a Python literal `{"pitch_d", "tip_d", ...}`, on
purpose — "The field names are written out literally here, not derived from
`DerivedDimensions.model_fields` — a renamed field, or a route that lost its typed
return annotation, must fail this test rather than pass tautologically." Adding
`tip_chamfer_effective` (or whatever name is chosen) without updating this literal
breaks `make verify` immediately, which is intentional.

**Why it happens:** By design (D-08/D-12 additive contract, L21) — this is not a bug to
route around, but a required edit the planner's task list must include explicitly.

**How to avoid:** Add the plan task: "add the new field name to the literal set in
`test_openapi_documents_the_typed_contracts`" alongside the `DerivedDimensions` field
addition itself. Also check `tests/test_api.py:110-126`
(`test_every_key_the_ui_reads_is_a_derived_dimensions_field`) and `app.js`'s `DIMS` array
(`src/spur/static/app.js:13-31`) — a `DIMS` row is required per D-08.

### Pitfall 5: A selector matrix row addition changes what `bare_p` means for every existing row

**What goes wrong:** `test_each_edge_selector_picks_exactly_its_own_edges`
(`tests/test_model.py:122-190`, read this session) builds every row with `bore_chamfer=0,
recess_fillet=0` ("the solid each selector sees in the pipeline just before its operator
would run") and monkeypatches `_cut_keyway` to a no-op. Adding a tip-selector column
means every existing row's `_tip_edges` count must also be computed on that same
`bare_p`/no-keyway solid — which is fine, since the tip chamfer runs after the keyway
cut and unconditionally on the tooth tips, so `tip_chamfer > 0` isn't gated by
`bore_chamfer` or `recess_fillet` being zero. But the new `tip_chamfer` value itself must
be added to every row's `kw`, or the added column reads a constant `2×teeth` for every
row regardless of teeth count — losing the coverage the 200-tooth and module-0.2 rows are
meant to add.

**Why it happens:** The matrix's existing rows vary `teeth` implicitly (default 19) plus
bore/hex/keyway/recess shape, not module — a 200-tooth or module-0.2 row is new
territory for this specific test, not a copy of an existing row with one field flipped.

**How to avoid:** D-13 already specifies "a tip `Counter` column on every existing row …
plus a 200-tooth row and a module-0.2 row" — treat this as literal: every existing
`pytest.param` in the parametrize table (see `tests/test_model.py:75-121`, e.g.
`no-bore`, `hex-both`, `keyway-d-flat-both`, …) needs its tip-edge count computed and
added as a new expected value, and two wholly new rows are added for the tooth-count and
module extremes.

## Code Examples

Verified patterns from the installed kernel and the current tree, plus two feasibility
probes run this session (not the D-05 spike — narrow architecture-confirming checks
only, no 200-tooth timing).

### `Mixin3D.chamfer()`'s real signature and behavior

```python
# Source: .venv/lib/python3.12/site-packages/cadquery/occ_impl/shapes.py,
# inspect.getsource(Mixin3D.chamfer), cadquery==2.8.0, read this session [VERIFIED]
def chamfer(
    self: Any, length: float, length2: float | None, edgeList: Iterable[Edge]
) -> Any:
    """
    Chamfers the specified edges of this solid.
    :param length: length > 0, the length (length) of the chamfer
    :param length2: length2 > 0, optional parameter for asymmetrical chamfer.
        Should be `None` if not required.
    :param edgeList:  a list of Edge objects, which must belong to this solid
    :return: Chamfered solid
    """
    # symmetric when length2 is falsy: d1 = d2 = length — the exact D-03 semantics
```
`length2=None` (falsy) makes `d1 = d2 = length`, i.e. a symmetric 45° chamfer —
confirms D-03's "symmetric 45°, one field" is exactly what passing `None` as the second
argument produces, matching `_cut_bore`'s existing call.

### Tip-arc edges are confirmed `CIRCLE`-type at radius `ra`, `2×teeth` total, both end faces

```python
# Probe run this session against the pinned kernel, default GearParams() (19 teeth):
from spur.params import GearParams
from spur.model import _build_checked
from spur.calc import profile

p = GearParams()
pr = profile(p)
s = _build_checked(p)
TOL = 1e-6
tip_edges = [e for e in s.Edges()
             if e.geomType() == "CIRCLE" and abs(e.radius() - pr.ra) < TOL]
# len(tip_edges) == 38 == 2 * p.teeth   [VERIFIED this session]
# Counter(round(e.startPoint().z, 3) for e in tip_edges) == {0.0: 19, 7.5: 19}
#   -- exactly teeth edges per end face   [VERIFIED this session]
```
Result observed this session: **38 CIRCLE edges, split 19/19 across z=0.0 and z=7.5**
(the default `face_width`), on the default 19-tooth gear. Edges near `ra` that are
*not* the tip arc (flank splines, fillet chords) are `BSPLINE`/`LINE` type, so the
`geomType() == "CIRCLE"` test alone separates them — **no z-height filter is needed**,
unlike `_groove_floor_edges` (which must distinguish top-face from bottom-face floors).

### Chamfer feasibility + face/edge delta, confirmed this session (not the spike's timing numbers)

```python
# Probe run this session, default GearParams(), c = 1.0 mm (well inside the 1.75 mm
# D-02 cap for this configuration):
bare = _build_checked(GearParams())          # 172 faces, 490 edges
ch = bare.chamfer(1.0, None, tip_edges)       # tip_edges from the probe above
# ch.isValid() == True                                          [VERIFIED this session]
# len(ch.Faces()) - len(bare.Faces()) == 38 == 2 * teeth         [VERIFIED this session]
# len(ch.Edges()) - len(bare.Edges()) == 114 == 3 * 2 * teeth    [VERIFIED this session]
# ch.Volume() < bare.Volume()                                    [VERIFIED this session]
# BoundingBox().xlen / .ylen unchanged (36.5589.../36.6802...)   [VERIFIED this session]
```
**Face delta is exactly `+2×teeth`**, matching D-12's stated expectation. **Edge delta is
`+3×(2×teeth)`, not `+1×(2×teeth)`** — each new chamfer face contributes three new edges
(two tangent lines to the untouched flank vertices, one new smaller-radius arc at the
chamfer's inner edge), confirming CONTEXT.md's warning that "a chamfer terminating at
unchamfered flank vertices may add more edges than faces" and that this delta "is
measured … in the spike and pinned, not derived." **This 3:1 ratio held at 19 teeth
in this probe; the spike must re-confirm it at 40/200 teeth and module 0.2/10 before
D-12's proof test hard-codes it** — a different tooth/module combination could in
principle produce a different per-face edge count if the flank-vertex tangency
resolves differently (untested here).

Also confirmed this session: chamfering the tip edges of a gear that **already has** a
bore chamfer, a keyway, and a face recess (`GearParams(keyway_width=3,
keyway_depth=1.4)`, the default gear's bore + `bore_chamfer=0.4` + `recess_sides=both`)
produces the identical `+38 / +114` delta with no failure — confirming CONTEXT.md's
"Claude's Discretion" expectation that "no interaction is expected" between the tip
chamfer and the recess/keyway/bore-chamfer edges.

### The cap-function shape to copy

```python
# Source: src/spur/calc.py:201-206, read this session [VERIFIED]
def root_fillet(p: GearParams) -> float:
    """Root fillet actually used: the requested radius, capped to what fits the gap."""
    _, _, gap = _tooth(profile(p))
    return round(min(p.root_fillet, 0.45 * gap), 3) if gap > 0 else 0.0
```

### The bore-chamfer call this phase's chamfer step reuses verbatim

```python
# Source: src/spur/model.py:218-219, read this session [VERIFIED]
solid = solid.chamfer(  # type: ignore[attr-defined]  # see _cut_face_recesses
    p.bore_chamfer, None, _bore_rim_edges(solid, p))
```

### `bench/build_time.py`'s sweep-file contract

```python
# Source: bench/build_time.py:56-72, read this session [VERIFIED]
def load_sweep(path: Path) -> list[tuple[str, GearParams]]:
    """Read a JSON list of shareable-link parameter sets, each validated into a
    GearParams. Label is the set's own key=value pairs, in file order.
    A set that fails validation ... cannot be timed and must not be silently skipped."""
```
A sweep file is a flat JSON array of objects, each a partial `GearParams` kwarg dict
(unset fields take their model default) — see `bench/sweeps/hex_bore.json` /
`keyway_bore.json` (both read this session) for the exact shape
`bench/sweeps/tip_chamfer.json` should follow. Run via:
```bash
# Source: Makefile:122-123, read this session [VERIFIED]
make bench.build SWEEP=bench/sweeps/tip_chamfer.json
```

## State of the Art

No prior-approach-to-current-approach shift within this phase's scope — this is the
first tip-chamfer implementation, not a replacement of an earlier one. The relevant
historical shift is L09 itself (root fillets moved from OCCT's fillet operator to an
analytic outline construction for a ~50× speedup) — Phase 10 is the one v0.2 feature
that *cannot* take that same remedy, because the locked reading requires a true 3D
end-face edge operation, not a profile-wire construction. This is stated explicitly in
CONTEXT.md and in `research/PITFALLS.md` Pitfall 3, and is why the phase opens with a
cost spike rather than assuming L09's fix generalizes.

**Deprecated/outdated:** N/A.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The `+3×(2×teeth)` edge-delta ratio observed at 19 teeth (default module 1.75) generalizes to 200 teeth and module 0.2/10 | Code Examples, Common Pitfalls Pitfall 1 | D-12's proof test would hard-code a wrong edge-count expectation; low risk of silent failure since a wrong count fails the test loudly, but costs a re-measurement cycle in the spike if not checked there first — CONTEXT.md already anticipates this and requires the spike to measure it, so this is flagged rather than assumed away |
| A2 | 20 bisection steps (09-03's precedent) is enough resolution for a tip-chamfer kernel boundary the way it was for `ROOT_CONTACT` | Common Pitfalls Pitfall 3 | If the true boundary needs finer resolution, the cap could land inside an unbuildable band the way `ROOT_CONTACT`'s own residual band did (09-CONTEXT.md's documented, accepted gap) — same risk profile as the accepted precedent, not a new one |
| A3 | No standard sizing rule exists for a gear tooth-tip chamfer (0.1–0.2×module has no source) | User Constraints, D-11 | Already locked by the human 2026-09-25 (research SUMMARY.md Known Conflict #2); not re-verified this session beyond re-reading the prior research's citation trail — carried forward as locked, not re-researched |

**If this table is empty:** N/A — see above.

## Open Questions

1. **Does the kernel boundary (D-04) move with tooth count or module the way the hex
   corner (L27) does, or stay fixed the way `ROOT_CONTACT` does?**
   - What we know: two precedents exist with opposite behavior — `ROOT_CONTACT` is
     teeth-independent (12-configuration bisection landed identically everywhere);
     L27's hex-corner bound is not (it moved between 19 and 40 teeth).
   - What's unclear: which pattern the tip-chamfer boundary follows, since it has not
     been probed at all this session (that probe is D-05's job).
   - Recommendation: the spike samples 19/40/200 teeth × module 0.2/1.75/10 specifically
     to answer this before the cap rule is finalized (D-04 already requires this); if
     the boundary moves in a way no single rule can capture, D-04 says surface it as a
     checkpoint rather than choosing.

2. **Does the D-07 over-budget checkpoint fire, and if so what `le` value clears it?**
   - What we know: Phase 8's heaviest hex row was 5.08s of 30s chamfering ≤12 edges;
     Phase 9's heaviest keyway row was 4.85s of 30s chamfering ≤2 edges. This phase's
     heaviest row chamfers up to 400 edges in one call — two orders of magnitude more.
   - What's unclear: whether OCCT's chamfer cost scales linearly, worse, or plateaus
     with edge count in one call — genuinely unmeasured, no proxy in this codebase gets
     close to 400 simultaneous chamfered edges.
   - Recommendation: this is exactly what the D-05 spike exists to answer; do not guess
     at a number here.

## Environment Availability

Not applicable — no new external tool, service, runtime, or CLI dependency. The phase
uses only the already-pinned `cadquery`/`cadquery-ocp` (confirmed installed and
importable this session) and the existing `bench/` tooling.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 9.1.1 [VERIFIED this session: `importlib.metadata.version('pytest')`] |
| Config file | `pyproject.toml` `[tool.pytest.ini_options]` — `testpaths = ["tests"]`, `--strict-markers --strict-config`, `xfail_strict = true` |
| Quick run command | `make test` (`$(PY) -m pytest $(PYTEST_ARGS)`) |
| Full suite command | `make verify` (lint + typecheck + import-lint + no-fake-done + test) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| REQ-tip-chamfer | Tip chamfer selects only the `2×teeth` tip-arc edges; flanks/root/bore/cutouts untouched | unit (selector matrix column) | `pytest tests/test_model.py::test_each_edge_selector_picks_exactly_its_own_edges -x` | ✅ (extend existing test, D-13) |
| REQ-tip-chamfer | Chamfer proven on built solid (face/edge delta, volume, bbox, `tip_d`) | unit (built-solid proof) | new test in `tests/test_model.py`, shape of `test_the_bore_chamfer_survives_the_keyway_and_the_slot_edges_stay_sharp` (D-12) | ❌ Wave 0 — new test |
| REQ-tip-chamfer | No-op tripwire (D-14) | unit | new test, shape of the existing tripwire precedent (monkeypatch the tip step to a no-op, assert D-12's proof fails) | ❌ Wave 0 — new test |
| REQ-tip-chamfer | Empty tip selection is a `BuildError`, routed 422/exit 2 | unit + integration | new test, shape of `test_a_bore_chamfer_that_selects_no_rim_edges_is_a_build_error_not_a_bare_bore` | ❌ Wave 0 — new test |
| REQ-tip-chamfer-capped | Cap applied and warned (D-01/D-02/D-04, D-09) | unit | new tests in `tests/test_calc.py`, shape of `test_a_bore_chamfer_under_min_wall_from_the_root_warns_with_the_measured_gap` | ❌ Wave 0 — new tests |
| REQ-tip-chamfer-capped | Kernel boundary tested one step either side (D-04) | unit | new tests, shape of `test_the_largest_round_bore_the_chamfer_rule_allows_builds` / `test_the_kernel_fails_where_a_round_bore_chamfer_touches_the_root` | ❌ Wave 0 — new tests, values from the spike |
| REQ-tip-chamfer-capped | Heaviest configuration measured against `SPUR_BUILD_TIMEOUT` | manual/bench (not `make verify`) | `make bench.build SWEEP=bench/sweeps/tip_chamfer.json` | ❌ Wave 0 — new sweep file |
| REQ-defaults-off-regression (standing) | Pre-v0.2 fixture byte-unchanged, replay requires new field null | unit | `pytest tests/regression/` (existing replay harness) | ✅ (no new file; replay's comparison already handles additive fields, D-15) |

### Sampling Rate

- **Per task commit:** `make test` (or a targeted `pytest tests/test_model.py -k tip` /
  `pytest tests/test_calc.py -k chamfer` during iteration)
- **Per wave merge:** `make verify` (full gate: lint, mypy --strict, import-linter,
  no-fake-done, full pytest — ~78s warm per Phase 9's last recorded number)
- **Phase gate:** Full suite green before `/gsd-verify-work`; `make bench.build
  SWEEP=bench/sweeps/tip_chamfer.json` green (every row inside `SPUR_BUILD_TIMEOUT`) as a
  separate, deliberate, non-gate measurement (D-16 stance in `bench/latency.py`'s
  docstring — never part of `make verify`).

### Wave 0 Gaps

- [ ] `tests/test_model.py` — a tip-selector column on the existing edge-selector
      matrix, plus a 200-tooth row and a module-0.2 row (D-13)
- [ ] `tests/test_model.py` — a built-solid proof test (D-12's shape)
- [ ] `tests/test_model.py` — a no-op tripwire test (D-14)
- [ ] `tests/test_model.py` — an empty-selection `BuildError` guard test (D-14)
- [ ] `tests/test_calc.py` — cap tests at D-01/D-02's limits, one step either side of
      D-04's measured boundary (values come from the spike, not invented here)
- [ ] `tests/test_calc.py` — the warning-sentence test (D-09)
- [ ] `tests/test_api.py` — update the literal `DerivedDimensions` field-name set in
      `test_openapi_documents_the_typed_contracts` (Pitfall 4 — easy to miss)
- [ ] `bench/sweeps/tip_chamfer.json` — new sweep file (D-06, 9 rows)
- [ ] A probe script under `bench/` or throwaway for D-05's spike (not necessarily
      committed — planner's discretion)

## Security Domain

`security_enforcement` is not present in `.planning/config.json`, so per the default it
is treated as enabled. This phase adds one bounded numeric field to an already-typed,
already-validated model; no new attack surface beyond the existing pattern.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | This project has no auth layer (unchanged by this phase) |
| V3 Session Management | no | No session state anywhere in `spur` |
| V4 Access Control | no | No access-control surface |
| V5 Input Validation | yes | `pydantic` `Field(ge=0, le=...)` bounds on `tip_chamfer`, the same mechanism every other `GearParams` field already uses (`params.py` `_f()` helper) — no new validation *mechanism*, just one more bounded field |
| V6 Cryptography | no | Not applicable to this feature |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Unbounded numeric input driving an expensive kernel operation (a build-time DoS vector already documented for this project, e.g. the ten-concurrent latency work) | Denial of Service | `le` bound on `tip_chamfer` (recommended 3, matching `bore_chamfer`), plus `SPUR_BUILD_TIMEOUT` wrapping every worker call regardless of which feature caused the cost — this phase's D-04/D-07 cap-and-measure discipline is exactly this mitigation applied to a new field |
| A parameter combination that individually validates but jointly produces an expensive or invalid build (composed-feature cost blowup, `research/PITFALLS.md`'s "worst composed configuration" risk) | Denial of Service | D-06's sweep explicitly varies `recess_sides` and module alongside `tip_chamfer`, not `tip_chamfer` in isolation — the standard mitigation already built into this phase's plan |

## Sources

### Primary (HIGH confidence)
- `.venv/lib/python3.12/site-packages/cadquery/occ_impl/shapes.py`,
  `inspect.getsource(Mixin3D.chamfer)` — read directly this session against the pinned
  `cadquery==2.8.0`
- `src/spur/model.py` (full file, 371 lines) — read this session
- `src/spur/calc.py` (full file, 598 lines) — read this session
- `src/spur/params.py` (full file, 112 lines) — read this session
- `bench/build_time.py` (full file, 154 lines) — read this session
- `bench/RESULTS.md` "Hex bore build and export time (Phase 8, D-11)" and "Keyway bore
  build and export time (Phase 9)" sections — read this session
- `bench/sweeps/hex_bore.json`, `bench/sweeps/keyway_bore.json` — read this session
- `Makefile` (full file) — read this session
- `tests/test_model.py` (defs listed, key tests read in full) — read this session
- `tests/test_calc.py` (cap/warning test section) — read this session
- `tests/test_api.py` (schema/DIMS parity tests) — read this session
- `src/spur/static/app.js` (`DIMS` array) — read this session
- `README.md` (parameter table, geometry notes) — read this session
- `docs/architecture/decision_log.md` L09, L27, L28 — read this session
- Two feasibility probes run this session against the pinned kernel (tip-edge
  selection, chamfer feasibility + delta, composed-feature interaction) — see Code
  Examples

### Secondary (MEDIUM confidence)
- `.planning/research/STACK.md` §4, `.planning/research/ARCHITECTURE.md` ("Tip chamfer
  last", Q4), `.planning/research/PITFALLS.md` Pitfall 3/4, `.planning/research/
  FEATURES.md` "Standards Cited — Tooth-Tip Chamfer" — v0.2-kickoff research, read this
  session, cross-referenced against this session's own kernel reads (all consistent, no
  drift found)

### Tertiary (LOW confidence)
- None used as a basis for any claim in this document beyond what CONTEXT.md already
  locks (the 0.1–0.2×module figure, explicitly excluded from help text per D-11 — not
  cited here as a value, only as a historical fact about what NOT to write).

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — no new dependency, versions confirmed installed this session
- Architecture: HIGH — every pattern has a working precedent read in full this session,
  plus two confirming kernel probes
- Cost/pitfalls: MEDIUM — the mechanism and prior-precedent cost family are HIGH
  confidence; the actual 200-tooth number is explicitly unmeasured here (that is Plan
  10-01's job, by design, per D-05)

**Research date:** 2026-09-28
**Valid until:** 30 days, or immediately upon a `cadquery`/`cadquery-ocp` version bump
(the pinned versions' exact chamfer cost and failure behavior are kernel-build-specific,
per 09-03's own re-measurement precedent finding a 4× different boundary from a stale
number)
