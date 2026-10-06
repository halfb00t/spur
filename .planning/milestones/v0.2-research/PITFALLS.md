# Pitfalls Research

**Domain:** Adding boolean body cutouts, polygonal bores and a tooth-tip chamfer to an
existing OCCT-based (CadQuery 2.8.0) involute spur gear generator — v0.2 "Fit to Shaft"
milestone, built on the shipped v0.1 pipeline (`src/spur/model.py`).
**Researched:** 2026-09-25
**Confidence:** MEDIUM-HIGH — every pitfall is grounded in this repo's own code
(`model.py`, `calc.py`, `params.py`), the decision log (L03/L05/L08/L09/L18/L24), or a
live check against the installed `cadquery==2.8.0` in `.venv`; the general OCCT boolean
behaviour claims are corroborated by OCCT's own documentation and public CadQuery/FreeCAD
issues (cited per pitfall) rather than verified against this project's own geometry, since
the new cuts do not exist in the tree yet.

## Critical Pitfalls

### Pitfall 1: Tangent/coincident cutter faces make OCCT booleans non-robust or silently wrong

**What goes wrong:**
A lightening hole circle tangent to the recess wall, a keyway flank made exactly
coincident with a D-bore flat, or a hex-bore/hex-cutout vertex touching the recess inner
wall gives the boolean solver a near-zero-thickness sliver instead of clean overlap or
clean separation. `BRepAlgoAPI_BooleanOperation` is documented as "fundamentally not
robust over the entire possible space of geometric objects" for exactly this class of
input — touching, near-coincident, misaligned entities are the named failure case, not an
edge case someone forgot to test. Symptoms range from a hard `StdFail_NotDone` (mirrors
CadQuery issue #346, where a fillet-then-chamfer sequence on adjacent edges throws `BRep_
API: command not done`) to something worse: a boolean that "succeeds" but leaves a sliver
face, a degenerate edge, or a solid `isValid()` still reports true for but that meshes
into a cracked STL.

**Why it happens:**
The parameters that create tangency in this milestone are exactly the ones a user is
likely to set on purpose: a keyway width chosen to just clear a D-flat, a bolt-circle Ø
picked so holes sit flush against a recess wall, a hex cell size that makes a honeycomb
vertex kiss the recess boundary. These are legitimate designs, not user error — the
milestone's own rule is "the only refusal is a direct dimensional conflict" (`PROJECT.md`
Target features), so *tangent* is a case that must build, not one that may be refused.

**How to avoid:**
1. Use CadQuery's `tol=` argument on `.cut()` / `.fuse()` / `.intersect()` (confirmed
   present on the installed `cadquery==2.8.0`: `Shape.cut(self, *toCut, tol=None)`,
   `Shape.fuse(self, *toFuse, glue=False, tol=None)`) — this is OCCT's "Fuzzy Boolean"
   option, which treats gaps/overlaps under a global tolerance as touching instead of
   intersecting, the documented robustness fix for exactly this class of near-coincident
   input (old.opencascade.com Boolean Operations guide).
2. Do not hand-pick `tol` per call; derive it once from the smallest clearance this
   milestone's parameters can legally produce (`MIN_WALL = 0.4` in `calc.py` is the
   existing floor other cuts already trust) and document the choice next to the constant,
   the way `TOL = 1e-6` in `model.py` is already documented as "for matching kernel
   geometry back to the numbers we asked for" — a new decision (`Lxx`), not an ad hoc
   number.
3. Push every geometric near-tangency case (hole tangent to recess wall inside 1 mm,
   0 mm, and overlapping by 0.1 mm) into the new cutout's test module as parametrized
   builds, not just its "obviously fine" middle case.

**Warning signs:**
`BuildError` from `_build_checked`'s catch-all (`model.py:249-256`) on a parameter set
that is not a documented conflict; `isValid()` true but `Solids()` returns more than one
piece (a sliver split off); STL export producing a triangle count far outside the
reference gear's ballpark for a similar tooth count.

**Phase to address:**
The phase that lands body cutouts and the phase that lands hex bore both need this — treat
it as a cross-cutting concern to solve once (a shared `_safe_cut`/`_safe_fuse` helper with
the tolerance baked in) rather than re-deriving `tol` per cutout type.

Sources: [Boolean Operations — old.opencascade.com](https://old.opencascade.com/doc/occt-6.9.1/overview/html/occt_user_guides__boolean_operations.html), [Boolean Operations 7.4 — dev.opencascade.org](https://dev.opencascade.org/doc/occt-7.4.0/overview/html/occt_user_guides__boolean_operations.html), [CadQuery issue #346](https://github.com/CadQuery/cadquery/issues/346), live check: `.venv/bin/python -c "import cadquery as cq, inspect; print(inspect.signature(cq.Shape.cut))"` → `tol: 'float | None' = None` confirmed on `cadquery==2.8.0`.

---

### Pitfall 2: Sequential `.cut()` per cutter instead of one multi-argument call

**What goes wrong:**
Body cutouts multiply a single cutter into many: spoke-arm gaps (one per arm), lightening
holes (one per hole on the bolt circle), honeycomb cells (potentially dozens). Writing
`for cutter in cutters: solid = solid.cut(cutter)` runs one full `BRepAlgoAPI_Cut`
(topology rebuild, face classification) per cutter — for N cutters that is N kernel
invocations against a growing intermediate shape, each one re-doing work the last one
already did on the untouched parts of the solid.

**Why it happens:**
A `for` loop is the natural way to write "cut N holes" and it is what the existing
recess/bore code does when there is only one or two cuts (`_cut_face_recesses` calls
`.cut()` twice, once per face — fine at N=2). Nobody reaches for the multi-argument form
until a cutout with N in the dozens exists to make the cost visible.

**How to avoid:**
`Shape.cut()` on the installed `cadquery==2.8.0` already accepts `*toCut: Shape` — build
every cutter for one cutout pass as a list of `cq.Shape` and issue **one** call,
`solid.cut(*cutters)`. OCCT's own comparison of its multi-argument Boolean operator
against the "old sequential two-argument approach" reports considerable performance
improvement from batching (dev.opencascade.org, "Boolean Operations With Multiple
Arguments"), and for non-overlapping cutters (the honeycomb/lightening-hole case, by
construction — holes on a bolt circle or a hex grid do not overlap each other) the cost is
one kernel call doing the equivalent work of N sequential ones, not N kernel calls.
Fusing the cutters into one compound first and cutting once is the same shape of fix and
is the more portable spelling if a `*args` form is not available in a pinned CadQuery
version later — measure both against this project's timeout budget before picking one,
since "faster" here is a claim `bench/`-style, not assumed (matches this project's own
measurement standard, `CONCERNS.md` "Measurement & Verification Standard").

**Warning signs:**
Body-cutout build time growing roughly linearly (or worse) with cutter count in a way that
threatens `SPUR_BUILD_TIMEOUT=30s` well before the honeycomb cell-count cap (Pitfall 5)
is even reached; a profiler/timer showing most of the cut time in repeated topology
re-classification rather than the geometry itself.

**Phase to address:**
Whichever phase lands the first multi-cutter feature (most likely lightening holes, the
simplest N-instance cutout) should establish the `cut(*cutters)` (or fuse-then-cut)
pattern and its measured build time; every later multi-cutter feature (honeycomb, spokes)
reuses it rather than re-deriving.

Sources: [Boolean Operations With Multiple Arguments — Forum Open Cascade Technology](https://dev.opencascade.org/index.php?q=node%2F1060); live check on `cadquery==2.8.0`: `Shape.cut(self, *toCut: 'Shape', tol=None)`, `Shape.fuse(self, *toFuse: 'Shape', glue=False, tol=None)`.

---

### Pitfall 3: A tooth-tip chamfer on a many-toothed outline repeats L09's fillet cost

**What goes wrong:**
L09 exists precisely because OCCT's fillet operator was ~50× slower than the analytic
alternative on a many-toothed outline (`docs/architecture/decision_log.md`). A tooth-tip
chamfer implemented the obvious way — `solid.chamfer(c, None, tip_edges)` using OCCT's
chamfer operator across every tooth-tip edge of a 200-tooth gear — is the same operator
family (`BRepFilletAPI_MakeChamfer`, built on the same fillet-propagation machinery as
`BRepFilletAPI_MakeFillet`) applied to the same shape of problem: one operator call
touching Z(teeth) edges around a closed, repeating outline. Left unaddressed, the
heaviest allowed configuration (200-tooth gear + tip chamfer + whatever else composes with
it) is exactly the kind of build the milestone's own success metric calls out by name
("recess + hex pattern is the unknown" — a tip chamfer at max tooth count is an equally
plausible second unknown) and can blow `SPUR_BUILD_TIMEOUT=30s`.

**Why it happens:**
`.chamfer()` is the CadQuery-idiomatic call, it is one line, and it works correctly on a
small tooth count in a quick manual test — the cost is invisible until someone builds the
same 200-tooth reference gear L09's own comment cites, or until CI/benchmarking sweeps
tooth count.

**How to avoid:**
Extend the existing analytic outline (`_outline()` in `model.py`) rather than reaching for
`Mixin3D.chamfer()` on the extruded solid: the tooth tip in `_outline()` is already a
`makeThreePointArc` between `left[-1]` and `right[0]` at radius `pr.ra` — a chamfer there
is a second, smaller geometric construction (two line segments cutting the corner) done in
the same 2D-outline pass that already replaces OCCT's fillet operator, at the same
per-tooth cost L09 already measured and accepted. This keeps the chamfer inside the "one
decision per step" pipeline shape `_gear_blank` documents and avoids introducing a second,
unmeasured slow path next to the one L09 already fixed. If an analytic tip chamfer turns
out not to be geometrically equivalent to a true 3D edge chamfer for a non-flat-topped
tooth, the fallback is `Mixin3D.chamfer()` on a *position-selected* rim edge set (see
Pitfall 4) — but only after measuring it against the timeout at 200 teeth, the same bar
L09 was held to, and logging the number the way L09's docstring does ("~50× faster ... for
identical geometry").

**Warning signs:**
Tooth-tip chamfer build time not logged/measured at max tooth count before the feature is
called done; a `.chamfer()` call anywhere in the tooth-outline path that has no
corresponding entry in `bench/` or a phase SUMMARY with a number next to it.

**Phase to address:**
The tooth-tip chamfer phase, gated the same way the milestone's own rule states: "every
new cut gets a measured build time at its heaviest allowed configuration ... against
`SPUR_BUILD_TIMEOUT=30s`" (`PROJECT.md`).

Sources: L09 (`docs/architecture/decision_log.md`); `src/spur/model.py:98-148` (`_outline`, the existing analytic-fillet pattern to extend).

---

### Pitfall 4: Position-based edge selectors silently pick the wrong edges once topology changes

**What goes wrong:**
`_bore_rim_edges()` and `_groove_floor_edges()` in `model.py` already select fillet/chamfer
edges by position (radius, z-height) rather than by CadQuery's type-string selectors,
because the type selectors CadQuery ships (`|Z`, `<Z`, etc.) cannot distinguish "the bore
rim" from "some other circular edge on the same face" once there is more than one feature
on that face. Every new cutout adds edges to that same end face: a keyway rim, a hex-bore
rim, spoke-arm cutout edges, lightening-hole rims, honeycomb cell rims. A selector written
and tested against v0.1's topology (bore + recess only) can start matching a *different*
edge once a new cutout exists on the same face — not by raising an exception, but by
quietly filleting/chamfering the wrong feature, or missing the new feature's own rim
entirely, and CadQuery/FreeCAD's own issue trackers document this exact failure mode:
edge references becoming invalid or ambiguous after a shape is modified, with the operator
sometimes throwing (`BRep_API: command not done`, CadQuery #346) and sometimes not
throwing at all — just filleting the wrong thing.

**Why it happens:**
`_bore_rim_edges`'s own docstring states its safety argument explicitly: "the only other
edges on an end face belong to a recess, and `recess_radii()` keeps at least `MIN_WALL`
plus the chamfer between that and the bore, so a radius test separates them." That
argument is true today and becomes false the moment a keyway rim, a hex-bore rim, or a
lightening-hole rim can sit at a radius inside `lim = r_bore + 0.01` or outside it in a way
the two-feature-only proof never considered. The selector's logic is correct for the
topology it was written against and silently wrong for topology it was not written
against — there is no assertion that fires when a new edge slips into its matched set.

**How to avoid:**
1. Every new position-based selector (a keyway rim selector, a hex-bore rim selector, a
   cutout-rim selector for a chamfer/fillet feature) states its separating invariant in a
   comment the same way `_bore_rim_edges` and `_groove_floor_edges` already do — and that
   invariant becomes a property re-checked whenever a *new* feature is added that could
   share the same face/radius band, not just documented once and trusted forever.
2. Re-verify `_bore_rim_edges` and `_groove_floor_edges` themselves whenever a cutout
   phase adds an end-face feature: their existing radius-band proof is a claim about the
   *current* set of end-face features, and a new one invalidates the proof, not just the
   selector reading it.
3. Test the *count* and the *identity* of the matched edge set, not just that the build
   succeeds: assert the number of edges a selector returns equals the expected count for a
   parameter set with every composable feature turned on at once (bore + recess + keyway +
   cutout), and assert each matched edge's radius/z falls in the band the selector's own
   comment claims — a test that would fail loudly the day the claim stops being true,
   rather than a build that quietly fillets the wrong rim.
4. Prefer positive identification (the exact wire/edge just constructed for a new cutter,
   captured *before* the boolean cut, and matched back by geometry the operation is known
   to preserve — center point, radius) over exclusion-by-radius-band once three or more
   features can share a face, since band-exclusion proofs get combinatorially harder to
   state correctly as feature count grows.

**Warning signs:**
A new cutout or bore feature ships and `make verify`'s existing fillet/chamfer tests still
pass (they test the old topology) while a *new* combination (this cutout + the bore
chamfer, this cutout + a recess) has never been exercised; a fillet/chamfer applied to a
visually wrong edge in a manual STL/STEP inspection that no automated test would have
caught, because the test suite only checks the feature in isolation.

**Phase to address:**
The composition phase (the milestone rule "features compose ... only refusal is a direct
dimensional conflict") is the one place all combinations get exercised together — but the
per-feature phases (keyway, hex bore, each cutout) must each re-audit `_bore_rim_edges`/
`_groove_floor_edges` and their own new selector's invariant *before* the composition
phase runs, because composition testing finds the symptom, not the root cause, if the
selectors themselves were never re-proven.

Sources: `src/spur/model.py:204-232` (`_groove_floor_edges`, `_bore_rim_edges`, both docstrings state the invariant this pitfall targets); [CadQuery issue #346](https://github.com/CadQuery/cadquery/issues/346); [CadQuery issue #1553 "Weird Fillets requires that edges be selected"](https://github.com/CadQuery/cadquery/issues/1553).

---

### Pitfall 5: Honeycomb cell count blows the 30 s timeout unless capped and warned, not silently dropped

**What goes wrong:**
The milestone's own target feature already names the risk: "the count follows from the
web area and is capped and warned when the build cannot fit the timeout" (`PROJECT.md`).
The mistake to avoid is not *whether* to cap — that is decided — it is capping by silently
reducing the cell count (or cell density) to whatever fits under a time budget without
reporting the reduction, which reintroduces the exact class of bug L03 exists to prevent
("silently shrinking a shaft bore would be worse than refusing" — a silently sparser
honeycomb is the cutout-body equivalent) and violates L08's "a number the tool prints is a
number someone will cut metal to" if the reported hole count in `DerivedDimensions` no
longer matches what got cut.

**Why it happens:**
Timeout-bounded generative patterns are naturally implemented as "keep adding cells until
either the pattern is full or the clock runs out" — a loop with a time check is the
easiest way to guarantee the 30 s bound is never crossed, and it is tempting to just stop
the loop quietly. That produces a part whose actual cell count depends on how fast the
machine that built it happened to be, which is exactly the non-reproducibility L05/L08
were written to rule out (a shareable link would not reproduce the same part on a slower
or faster machine).

**How to avoid:**
Compute the cap analytically, before cutting anything, the same way `recess_radii()`
computes a narrowed width analytically rather than discovering the limit by trial-and-
error against the kernel: derive an expected per-cell build-time cost from the *measured*
heaviest single-cutter cost (Pitfall 2's per-cutter multi-argument cut, measured once),
multiply by the geometric cell count the requested cell size and wall thickness imply for
the available web area, and if the product would exceed a documented safety margin under
`SPUR_BUILD_TIMEOUT`, cap the cell count to what the margin allows and report the applied
cap and the resulting cell count in `warnings` — never let the *build itself* be the thing
that discovers the limit by timing out or getting killed. This keeps the honeycomb cutout
inside the existing cap-and-warn contract (L03) instead of inventing a new "best effort"
category the error contract does not have.

**Warning signs:**
A honeycomb build's actual cell count varies between runs of the identical parameter set
on the same machine (non-determinism, a correctness bug on its own) or between different
machines (a reproducibility bug against L05's shareable-link guarantee); any code path
where the cut loop's exit condition is a clock read rather than a pre-computed count.

**Phase to address:**
The hexagonal-pattern cutout phase — its own success criterion should be "cell count is
computed before the first cut, and the cap (if applied) is asserted in a test with a
scripted heaviest-allowed configuration," matching the milestone's stated need for "a
measured number per cut ... including recess + cutout combined" (Success Metric #2).

Sources: L03, L05, L08 (`docs/architecture/decision_log.md`); `PROJECT.md` "Target features" (honeycomb cell-count cap requirement, as given).

---

### Pitfall 6: A new parameter with a non-off default silently changes every pre-v0.2 link

**What goes wrong:**
Every field in `GearParams` (`src/spur/params.py`) is a Pydantic `Field(default, ...)`
with an absolute-millimetre default per L05 — "every shareable link that omits a field
depends on them." A new field for keyway width/depth/clearance, hex across-flats, cutout
count, chamfer size, etc. that ships with any default other than "feature off" (0, or a
sentinel like `bore_flat`'s existing "0 = round" convention) changes the derived
dimensions and the exported geometry for every URL/CLI invocation that predates the field
and therefore never set it — silently, because the request looks identical on the wire.
This is the exact failure mode the milestone's own rule names outright: "New parameters
default to off ... proven by a regression test, not assumed" (`PROJECT.md`).

**Why it happens:**
It is natural to pick a "sensible" non-zero default for a new dimension (a keyway width
that matches a common shaft size, say) the same way `bore_d = 9` and `recess_width = 6`
were picked for the reference gear — but those two are *existing*, pre-v0.2 defaults
already covered by L05's guarantee; a *new* field added in v0.2 has no such grandfathering
and must default to inert, not to "reasonable."

**How to avoid:**
Every new field's default must be the value that reproduces v0.1 geometry exactly — 0 for
a depth/width/count, `"none"`/`"round"` for an enum-shaped choice (mirroring
`recess_sides: Literal[..., "none"]` and the existing round-vs-D-flat pattern in
`bore_flat`), and the model-level `_feasible()` / `check()` gate must not fire for the
all-defaults case regardless of what other new checks it grows. Write the regression test
first, not last: freeze `derive()`'s output and every export's decoded volume/triangle
count for a representative set of pre-v0.2 parameter sets (including at least one at the
stock defaults and one exercising the bore/recess features that already exist), assert
byte-for-byte-equivalent `DerivedDimensions` and content-equivalent exports (volume,
triangle count — see Pitfall 11 on why not raw bytes) after each new field lands, not once
at the end of the milestone.

**Warning signs:**
A new field's `Field(default=...)` in `params.py` is anything other than 0/`"none"`/
`False`; the regression test (milestone Active requirement: "Every pre-v0.2 parameter set
yields identical derived dimensions and an identical export") does not exist yet when the
first new field is added.

**Phase to address:**
Every phase that adds a `GearParams` field owns its own default and its own regression
assertion at merge time — do not defer the whole-milestone regression proof to a single
late "composition" phase, since that lets N fields' worth of default drift accumulate
before anyone checks.

Sources: L05 (`docs/architecture/decision_log.md`); `src/spur/params.py:26-90` (existing default pattern, `bore_flat`'s "0 = round" convention as the model to copy); `PROJECT.md` "Rules this milestone lives by."

---

### Pitfall 7: Assuming the solid cache needs a migration — the real risk is semantic, not mechanical

**What goes wrong:**
It is tempting to treat "the cache is keyed by a parameter hash" as a hazard that needs an
explicit migration step when new fields are added — worrying about a pre-v0.2 URL
"colliding" in the `lru_cache` with a differently-shaped v0.2 request, or needing a cache-
version bump. Spending phase time on that is solving a problem that (checked against this
codebase) does not exist, and it distracts from Pitfall 6, which is the real risk hiding
under the same words.

**Why it happens:**
`GearParams` is a frozen Pydantic model (`model_config = ConfigDict(frozen=True)`) and the
build/export caches key directly on the `GearParams` instance (`_build_cached =
lru_cache(...)(_build_checked)`, `model.py:259`; `_EXPORTS` keyed on `(params, fmt,
quality, encoding)`, L19) — Pydantic's generated `__hash__` for a frozen model hashes the
full tuple of field values by name, not a truncated digest, so two `GearParams` instances
that differ only in a field one of them lacks cannot exist in the same running process (the
class itself gained the field) and cannot collide (the hash input changed, not just its
output). Both caches are in-memory, per-worker, and never persisted across a deploy
(`SPUR_SOLID_CACHE`/`_BlobCache` are process-lifetime only) — a deploy restarts every
worker, so there is no stale on-disk cache to migrate either. Confirmed live: `.venv/bin/
python -c "import cadquery"`-style check against `params.py` shows no custom `__hash__`
or `__eq__` override — the frozen-model default is what is in use.

**How to avoid:**
Do not add cache-versioning machinery for this milestone; it is solving a non-problem and
adds a place for a real bug to hide. Instead, put the verification effort into Pitfall 6's
regression test (the actual place old links can silently change) and, if a `slug()`-based
export filename is touched (see Pitfall 8's cousin issue below), confirm `GearParams.
slug()` still returns a filename-safe string for the new field set — it currently encodes
only `teeth`/`module`/`pressure_angle` (`params.py:90-92`), so new bore/cutout fields will
*not* appear in the download filename even though they change the geometry; that is a
UX/collision-of-filenames issue (two different keyway/hex variants of the same z/m/pa
download as the same filename), not a cache-correctness issue.

**Warning signs:**
A phase plan proposing a cache-key version number, a cache-clearing migration step, or
`lru_cache.cache_clear()` calls tied to the v0.2 release — a sign the mechanical risk is
being solved instead of the semantic one.

**Phase to address:**
Any phase reviewing this milestone's caching story should confirm this conclusion against
the *actual* fields added (this research was written before those fields exist) rather
than re-deriving it from scratch, and should verify the `slug()` filename-collision point
if cutout parameters are exposed in a user-facing filename anywhere in the UI.

Sources: `src/spur/params.py:26-30, 90-92`; `src/spur/model.py:259, 291-295`; L02, L19 (`docs/architecture/decision_log.md`); live check: `.venv/bin/python` confirms `cadquery==2.8.0` installed, no custom hash/eq in `params.py` at time of research.

---

### Pitfall 8: Many-small-face solids change STL/STEP export characteristics inside the admission slot

**What goes wrong:**
A honeycomb pattern or a many-hole lightening cutout multiplies the face count of the
solid by the cell/hole count. STL tessellation cost, triangle count and file size do not
scale the way a single bore's did (L24's reference numbers — 9,066/46,278 triangles,
453,384–9,086,484 bytes — are for a solid with one bore and up to two recesses, not
dozens of small holes each contributing their own cylindrical/hex wall triangulation).
Two concrete risks: (1) tessellation and gzip-compression time (L19's measured
`compresslevel=1` numbers, 51.5–788 ms table) were measured against a *specific* STL byte
profile; a honeycomb gear's STL could be meaningfully larger or smaller per unit volume
and change where on that curve a real export lands, and (2) export happens **inside**
`_build_slot()`'s admission-controlled window (per L19, this is the only place a bound can
apply), so a heavier export is not just slower for one user — it holds an admission slot
longer for everyone else.

**Why it happens:**
L24's mesh-copy fix and L19's gzip-level choice were both measured against the v0.1
feature set. Nothing about those measurements automatically re-validates itself when the
solid's face topology changes shape (many small faces vs. few large ones) — tessellation
cost is a function of edge count and curvature, not just bounding volume, so "the solid is
roughly the same size" is not evidence the export is roughly the same cost.

**How to avoid:**
Re-run L19's gzip-level table and L24's mesh-copy timing against the heaviest allowed
cutout configuration (e.g. max honeycomb cell count at max tooth count, per Pitfall 5's
cap) before calling the export path done, the same way L19 and L24 were originally
measured — not assumed to still hold. If the numbers move meaningfully, that is new
evidence for a new decision entry (a revised gzip level, or a note that the existing level
1 choice still clears its 10%-size/1.5×-time bar), not silent inheritance of v0.1's table.

**Warning signs:**
No measured export-time/triangle-count/file-size number exists for the heaviest cutout
configuration when the phase is called done; `/api/health` p95 regressing under a cutout-
heavy export in a way the single-build latency bar (L18) was never re-measured against.

**Phase to address:**
The phase that lands whichever cutout produces the most new faces (most likely the
honeycomb pattern) should own a fresh export-cost measurement at its capped maximum,
reported the way L19/L24 report theirs (a table, a machine, a date).

Sources: L19, L24 (`docs/architecture/decision_log.md`); `src/spur/model.py:267-296` (`_write_export`, `export`).

---

### Pitfall 9: Keyway depth-datum ambiguity prints a number nobody can cut metal to

**What goes wrong:**
"Keyway depth" is not a self-evident datum on a real part. Machinists and shaft/keyway
standards (ANSI B17.1, DIN 6885, ISO 773) distinguish at least three different "depth"
conventions: (a) depth measured from the bore's nominal diameter/radius down to the
keyway floor, (b) depth measured from the bore's *actual cut* surface (after bore
clearance is applied) to the keyway floor, and (c) "over-bore" depth — the largest
diameter that circumscribes bore + keyway together, the number some shaft-and-keyseat
gauges actually use. The milestone explicitly refuses to look up a standard table ("no
standard-table lookup... a looked-up size is a number someone cuts metal to, and would
need the standard cited and its table verified," `PROJECT.md`) — which means *this
project* is the one place that datum gets defined, and if the implementation picks a
datum silently, `DerivedDimensions`' reported keyway depth is a plausible-looking number
that does not match what a machinist measuring the physical keyway floor would read.

**Why it happens:**
The keyway is a rectangular slot cut radially outward from the bore. "Depth" reads as an
obviously single number until the bore's own clearance (`bore_clearance`, already a
`GearParams` field — printing shrinkage) is factored in: is the requested keyway depth
measured from the *nominal* bore radius (what the user typed into `bore_d`) or from the
*actual* cut radius (`bore_radius()` = `(bore_d + bore_clearance) / 2`)? These two differ
by exactly `bore_clearance / 2`, which is small (fractions of a mm) but is precisely the
kind of small, silent, "close enough" error L08 exists to forbid — a number someone will
cut metal to being off by a fraction of a millimetre because two equally plausible
readings of "depth" were both implemented somewhere without either being chosen on
purpose.

**How to avoid:**
State the datum explicitly, once, the way `bore_radius()` and `recess_radii()` already
state theirs in a comment, and pick the one a hobbyist reading a keyway width/depth off
their own shaft with calipers would actually measure — almost certainly (c) or (a): depth
from the bore's nominal/cut surface outward, the number that appears on a keyway gauge or
a caliper depth-measurement, not (b), which requires the user to know their own printer's
shrinkage compensation to interpret the number correctly. Whichever is chosen, add it to
`DerivedDimensions` as its own explicit field (not folded into an existing bore field) and
name the datum in the field's help text the way every other field in `params.py` names its
own convention ("Added to bore and flat for print shrinkage," `bore_clearance`'s own help
string, is the pattern to match). Add a unit test that builds a keyway at a known depth and
asserts the *built solid's* measured floor-to-axis distance (read back from the kernel, the
same way `root_thickness`'s wrong-radius bug (F6, `CONCERNS.md`) was caught by measuring at
the actual radius) matches the documented datum to the tolerance the rest of the codebase
uses (`TOL = 1e-6` in `model.py`) — proving the printed number and the cut geometry agree,
not just that the parameter round-trips.

**Warning signs:**
A keyway "depth" field with no comment stating which surface it is measured from; a test
that asserts the *parameter* value appears somewhere in `DerivedDimensions` without ever
measuring the *built solid's* actual keyway floor position back out of the kernel.

**Phase to address:**
The keyway bore phase — this is the single highest-consequence pitfall in this list
because it is the one most likely to produce a confidently wrong, unflagged number (the
exact failure class L08 was written to eliminate), and it must be resolved before the
phase is called done, not deferred to composition testing.

Sources: L08 (`docs/architecture/decision_log.md`, "no number is better than a wrong
number"); `CONCERNS.md` F6 (`root_thickness` measured at the wrong radius — the precedent
for this exact class of bug in this codebase); `src/spur/calc.py:57-58` (`bore_radius()`,
the existing nominal-vs-clearance distinction the keyway depth must resolve against);
keyway/keyseat depth-convention ambiguity (ANSI B17.1 / DIN 6885 nominal-vs-cut-surface
depth datums) is domain background, unverified against a specific standard per this
milestone's own "no standard-table lookup" scope decision — flagged here as the reason the
datum must be *stated*, not looked up.

---

### Pitfall 10: A validation gap lets a geometric conflict reach OCCT instead of a 422

**What goes wrong:**
`check(p)` in `calc.py` is the single point `GearParams._feasible()` calls to turn a
direct parameter conflict into a 422 (`PydanticCustomError`, naming the fields) — it
already covers bore-vs-root-diameter and recess-web-thickness conflicts. If a new
cutout's cross-parameter conflicts (a lightening-hole bolt circle whose holes overlap the
bore, a hex-cutout cell whose boundary crosses into the recess, a keyway whose width plus
clearance eats past the opposite bore wall) are *not* added to `check()`, the request
passes validation, reaches `model.py`'s cut pipeline, and fails there instead — as a
generic `BuildError` from `_build_checked`'s catch-all ("Geometry kernel failed
(...); try smaller fillets or chamfers") rather than a 422 naming the actual conflicting
fields. That is a direct violation of the milestone's own rule: "the only refusal is a
direct dimensional conflict named by field" (`PROJECT.md`) — a `BuildError` is a refusal,
but not one that names the field, and it costs a full worker-process build (seconds, a
locked kernel) to discover what pure arithmetic in `calc.py` could have caught in
microseconds without ever touching CadQuery.

**Why it happens:**
`check()`'s existing conflicts (bore-vs-root, recess-web) were written when there were
only two features that could geometrically interfere. Every new cutout is a *new* source
and target of geometric conflict against the bore and the recess and each other, and it is
easy to implement the cutout's own cut correctly (it builds fine in isolation) while never
writing the corresponding overlap check into `check()`, because the isolated case never
exercises the gap.

**How to avoid:**
For every new cutout/bore feature, write its overlap checks as pure arithmetic in
`calc.py` (circle-circle overlap for lightening holes vs. bore/recess, point-in-polygon or
distance-to-line for keyway flank vs. bore wall, hex-cell-vertex-to-radius for honeycomb
vs. recess) *before* the corresponding cut is added to `model.py` — this also respects the
existing import-boundary contract (`calc.py` never imports `cadquery`, runs on every
keystroke) rather than tempting a "just try the cut and see if OCCT complains" shortcut
that would need the kernel to validate. Add a test per new conflict that asserts a 422
with the correct field names in `detail[].ctx.fields` (mirroring the existing pattern the
client already reads, per `CONCERNS.md`'s note that `app.js:130` reads `detail[].ctx.
fields` by name) for a parameter set at the boundary of the conflict, and a second test
one step inside the boundary that asserts the build succeeds.

**Warning signs:**
A new cutout's own tests all use "obviously fine" parameter combinations; no test in the
new feature's module asserts a 422 for a constructed overlap case; a manual/exploratory
build that takes a full `SPUR_BUILD_TIMEOUT` window to fail with a generic `BuildError`
for a combination that should have been rejected in microseconds.

**Phase to address:**
Each cutout/bore phase owns its own overlap checks in `check()` at the time it lands the
cut — deferring all overlap validation to the composition phase means every earlier phase
ships build-time failures instead of 422s, and the composition phase would need to retrofit
checks for combinations it did not itself introduce.

Sources: L03 (`docs/architecture/decision_log.md`); `src/spur/calc.py:116-155` (`check()`,
the existing pattern to extend); `src/spur/params.py:78-88` (`_feasible()`, the single
call site); `src/spur/model.py:249-256` (`_build_checked`'s generic catch-all — the
symptom this pitfall prevents from being the *only* signal); `CONCERNS.md` (client-side
`detail[].ctx.fields` contract).

---

### Pitfall 11: Testing against triangle counts, volumes or bounding boxes as if they were OCCT-version-portable constants

**What goes wrong:**
L24's own research explicitly measured that "OCCT export is not byte-reproducible across
independently built solids — matched byte-for-byte in only 8 of 20 reruns," and settled on
triangle count and decoded volume as the stable proof instead (`docs/architecture/
decision_log.md` L24). It is tempting for new cutout/bore tests to hard-code an *exact*
triangle count, an *exact* file size, or an *exact* bounding-box float (e.g. `zlen ==
7.500000200000001`) as a regression oracle. That value is not portable across a
`cadquery-ocp`/OCCT patch bump (a maintenance dependency update, not a code change in this
repo, could shift it) or, per the research already gathered for this same mesh, across a
parallel mesher that "is not deterministic" for a face without a stored triangulation
(re-meshing a local copy can disagree run-to-run on node numbering) — a brittleness this
project has already paid for once (L24's own multi-run measurement exists *because* naive
byte-equality failed).

**Why it happens:**
An exact number is the easiest assertion to write and the most satisfying to read in a
diff, and it will pass reliably on one pinned dependency set for a long time — until a
routine `requirements.txt` refresh (L12, generated by `docker/refresh-requirements.sh`)
bumps `cadquery-ocp` and every exact-value test in the new cutout/bore suite goes red at
once with no code change to explain it, exactly the kind of noise that erodes trust in
`make verify` as "the gate."

**How to avoid:**
Follow L24's own precedent, which the new tests are extending, not inventing: assert
content-equivalence properties the geometry *guarantees* rather than a value the kernel
merely *happened to produce* — decoded volume within a small tolerance, triangle count
within a documented band (not a single integer) if triangle count is asserted at all,
`Solids()` count and `isValid()`, and the specific field-value invariants Pitfall 9's
keyway-depth test needs (a measured distance against a stated datum, with `TOL`). Reserve
exact-value assertions for values this codebase computes itself in Python (radii, the
`DerivedDimensions` fields `derive()` returns) rather than values OCCT's mesher or STEP
writer produces.

**Warning signs:**
A test asserting `== <float>` or `== <int>` against anything read off `shape.exportStl()`
or `shape.exportStep()` output, a triangulation, or a raw byte count, rather than a
tolerance-bounded or "guaranteed by the geometry" property; a new cutout test suite that
has never been run against two different `cadquery-ocp` versions to see whether its
assertions survive the bump.

**Phase to address:**
Every phase that adds STL/STEP-level tests for a new cutout or bore should follow L24's
established pattern (content-equivalence, not byte/exact-value equivalence) from its first
test, not retrofit it after a dependency bump breaks a brittle one — flag this explicitly
in code review for each new test file the milestone adds.

Sources: L24 (`docs/architecture/decision_log.md`, "OCCT export is not byte-reproducible
... matched byte-for-byte in only 8 of 20 reruns"); [BRepMesh parallel mesher
non-determinism — OpenCascade tracker/forum research](https://tracker.dev.opencascade.org/view.php?id=27693); `tests/test_model.py::test_exporting_leaves_the_cached_solid_exact` (the existing test this pattern should be copied from, per L24's own description of its proof).

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|-----------------|-------------------|
| Sequential `for c in cutters: solid = solid.cut(c)` instead of `solid.cut(*cutters)` | Simpler diff, matches existing two-call recess pattern | Build time grows with cutter count faster than necessary, risks the 30 s budget on the honeycomb/lightening-hole cases | Only for a cutout whose N is fixed at 1-2 (never for honeycomb or many-hole lightening patterns) |
| `Mixin3D.chamfer()` on tooth-tip edges instead of an analytic outline chamfer | One line, reuses the existing `.chamfer()` idiom already used for the bore rim | Repeats the exact cost L09 paid OCCT's fillet operator to avoid; risks the timeout at max tooth count | Never for the tip chamfer at default (≤200) tooth counts, without a measured number proving it clears the timeout — if it clears, keep the number in a decision entry, not just a green test |
| Position-band edge selection (`_bore_rim_edges`-style) for a new feature instead of positive identification of the just-cut edges | Matches the existing codebase idiom, less new code | Each additional composable feature that can share a face makes every existing band-exclusion proof re-checkable, and a silent wrong-edge match is possible, not just a crash | Acceptable while the number of features sharing one face stays small (2-3) and every addition re-verifies the older selectors' invariants; reconsider positive identification once 4+ features can land on one face |
| Deferring a cutout's `check()` overlap validation to "the composition phase will catch it" | Ships the isolated feature faster | The isolated feature reaches OCCT with unvalidated conflicts in the interim, producing timeout-costly `BuildError`s instead of 422s, and the composition phase inherits validation debt it did not introduce | Never — L03's contract is per-feature, not per-milestone |

## Integration Gotchas

This milestone has no new external service integrations (it is additive on the existing
CadQuery/OCCT kernel, FastAPI/Pydantic model, and CLI) — the "integration" surface that
matters here is internal: the new cutout code integrating with the existing cut pipeline,
cache, and error contract.

| Integration | Common Mistake | Correct Approach |
|-------------|-----------------|-------------------|
| New cutout ↔ existing `_cut_face_recesses`/`_cut_bore` ordering | Cutting a new feature before the recess/bore, so its floor/rim edges get folded into a later selector's radius band unexpectedly | Cut new body cutouts *after* recesses and bore (per the milestone's own composition rule: "cutouts combine with face recesses... cut through the recessed floor, floor fillet intact") and re-verify every downstream edge selector against the new, later topology |
| New `GearParams` field ↔ the JSON-schema-driven web form | Assuming a new field "just shows up" correctly in the UI/CLI without checking its `group`/`unit`/`step` metadata matches the other fields in the same feature group (L02's whole point — one field, three surfaces) | Add the `_f(...)` metadata the same way every existing field does, and manually check the rendered form once per new field, since L02's promise is structural but the metadata is still hand-written |
| New cutout ↔ `DerivedDimensions` | Adding a new measured dimension as an optional field without the `null`-over-absent discipline L21 established | Every new `DerivedDimensions` field is present always, `null` when it does not apply (matching `mate_teeth`/`centre_distance`'s existing pattern) — not a conditionally-absent key |

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|-----------------|
| Honeycomb cell count scaling with web area at a fine cell size | Build time growing non-linearly as cell size shrinks toward the wall-thickness floor | Cap cell count analytically before cutting (Pitfall 5), derived from a measured per-cell cost | Any cell size/wall-thickness combination whose implied cell count times the measured per-cell cost approaches `SPUR_BUILD_TIMEOUT=30s` |
| Tooth-tip chamfer via OCCT's chamfer operator at max tooth count | Build time scaling with tooth count the way L09's fillet did pre-fix (~50× the analytic cost) | Analytic tip chamfer in `_outline()` (Pitfall 3) | 200-tooth gear, the same ceiling L09 was measured against |
| Sequential per-cutter `.cut()` calls | Build time scaling worse than linearly with cutter count | Multi-argument `.cut(*cutters)` or fuse-then-cut (Pitfall 2) | Any cutout with cutter count in the tens (lightening holes, honeycomb) |
| Export/gzip cost re-measured never after topology changes shape | `/api/health` p95 regressing under a cutout-heavy export, unnoticed because L18's latency bar was only ever measured against v0.1 solids | Re-run L19/L24's measurement tables against the heaviest v0.2 configuration (Pitfall 8) | The first cutout that meaningfully changes face count (most likely honeycomb) |

## Security Mistakes

No new external attack surface is added by this milestone (no auth model changes, no new
network calls) — the domain-specific risk here is compute-DOS shaped, already named in
`CONCERNS.md`'s "Authentication is Intentionally Absent" entry ("each ... build costs
seconds of CPU and hundreds of MB").

| Mistake | Risk | Prevention |
|---------|------|------------|
| A honeycomb/cutout parameter combination that is valid per `check()` but pathologically expensive (e.g. maximum cell count at maximum tooth count, every composable feature on at once) | Each such request costs a full worker for close to `SPUR_BUILD_TIMEOUT`, worse than any v0.1 request could — a bigger DOS primitive than the one already documented and accepted | Pitfall 5's analytic cap keeps the *worst* request bounded the same way the *typical* one already is; measure the worst composed configuration (recess + cutout + bore + chamfer, all at their allowed maxima) explicitly, not just each feature's own maximum in isolation |

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-------------------|
| Silent cell-count reduction in the honeycomb pattern (Pitfall 5) | User believes they got the pattern they asked for; the part they print has fewer/larger cells than requested, with no indication why | Report the applied cap and resulting count in `warnings`, matching the existing recess/fillet cap-and-warn pattern |
| Ambiguous keyway depth datum (Pitfall 9) | User cuts a keyway on their shaft to the printed depth and it does not match the printed part | State the datum explicitly in the field's help text and prove it against the built solid, not just the parameter |
| Download filename unaffected by new cutout/bore fields (`slug()` only encodes teeth/module/pressure_angle) | Two very different variants (same z/m/pa, different keyway/hex/cutout choices) download with the identical filename, so a browser silently appends `(1)`/`(2)` and the user loses track of which file is which | Not a correctness bug (Pitfall 7) but worth a UX decision: extend `slug()` or leave it and document the limitation — a decision either way, not silence |

## "Looks Done But Isn't" Checklist

- [ ] **Any new cutout/bore:** Often missing a `check()` overlap test against the bore and
      against the recess — verify a constructed-overlap parameter set returns 422 with the
      right field names, not just that "normal" parameters build.
- [ ] **Tooth-tip chamfer:** Often missing a measured build time at 200 teeth — verify a
      number exists in a phase SUMMARY or `bench/`, not just that `make verify` is green.
- [ ] **Any multi-instance cutout (holes, honeycomb, spokes):** Often missing the
      multi-argument-cut vs. sequential-cut choice being deliberate — verify the cut call
      is `solid.cut(*cutters)` (or an equivalent single-call batching), not a `for` loop,
      and that a build-time number exists at the heaviest allowed cutter count.
- [ ] **Keyway bore:** Often missing an explicit depth-datum statement and a solid-level
      measurement test — verify the comment states which surface depth is measured from
      and a test reads the built keyway floor back out of the kernel to confirm it.
- [ ] **Every new `GearParams` field:** Often missing the "defaults to off" regression
      check — verify a test asserts identical `DerivedDimensions` and export content for a
      representative pre-v0.2 parameter set after the field lands, not just that the field
      itself works when set.
- [ ] **Every new position-based edge selector:** Often missing a count/identity assertion
      — verify a test checks the matched edge set's size and radius/z band explicitly, not
      just that `.fillet()`/`.chamfer()` did not throw.
- [ ] **Composition (cutout + recess + bore together):** Often missing the *combined*
      heaviest-configuration build-time measurement the milestone's Success Metric #2
      explicitly names ("including recess + cutout combined") — verify it is measured, not
      inferred from each feature's own isolated number.

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|----------------|------------------|
| Tangent/coincident boolean failure (Pitfall 1) discovered late | LOW | Add `tol=` to the offending `.cut()`/`.fuse()` call; this is a local, one-line fix once diagnosed — the cost is in *diagnosing* which call needs it, not the fix itself |
| Position-based selector silently wrong (Pitfall 4) discovered late (wrong edge filleted/chamfered in a shipped release) | MEDIUM-HIGH | Re-derive the selector's invariant against the full current feature set, add the missing count/identity test, and audit every other existing position-based selector for the same gap — a single wrong-edge bug usually means the *proof shape*, not just one selector, needs revisiting |
| Non-off default silently changed pre-v0.2 links (Pitfall 6) shipped | HIGH | This is a shipped-metal-cutting-number regression (L08-class): revert the default to inert in a follow-up release, add the regression test that should have existed, and — because a real user may have already cut a part from a link that changed underneath them — this is exactly the class of bug that should stop and ask per `CLAUDE.md` rather than being silently patched forward |
| Keyway depth datum wrong (Pitfall 9) shipped | HIGH | Same class as Pitfall 6's recovery — a wrong depth number is L08's headline failure mode; requires a decision-log entry stating the correction, a migration note for anyone who already used the number, and cannot be treated as an ordinary bugfix |
| Exact-value test brittle against an OCCT bump (Pitfall 11) | LOW | Rewrite the assertion as a tolerance/content-equivalence check per L24's own pattern; no product code changes, purely a test-quality fix |

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|--------------------|-----------------|
| 1. Tangent/coincident boolean robustness | Whichever phase lands the first cutout that can be tangent to an existing wall (keyway or hex bore, most likely) | Parametrized build test at 0 mm, near-0 mm and small-overlap clearance between the new feature and the bore/recess wall it can touch |
| 2. Sequential cut vs. multi-argument cut | First multi-instance cutout phase (lightening holes) | Measured build time at max cutter count, `cut(*cutters)` in the diff, not a `for` loop |
| 3. Tip chamfer blowing L09's budget | Tooth-tip chamfer phase | Measured build time at 200 teeth, analytic outline chamfer in the diff |
| 4. Position-based selector silently wrong | Every phase adding an end-face feature; re-audited in the composition phase | Edge-set count/identity assertions per selector, re-run for every new feature combination |
| 5. Honeycomb cell-count cap | Hexagonal-pattern cutout phase | Analytic cap computed pre-cut, applied cap reported in `warnings`, deterministic cell count across repeated runs |
| 6. Non-off default changing old links | Every phase adding a `GearParams` field | Regression test on representative pre-v0.2 parameter sets, added in the same phase as the field |
| 7. Cache-key non-issue (verify, don't build machinery) | Any phase reviewing the caching story | Confirm no custom hash/eq exists once real fields are added; no cache-versioning code in the diff |
| 8. Export cost at many-small-face topology | Phase that most increases face count (honeycomb, most likely) | Fresh L19/L24-style measurement table at the heaviest configuration |
| 9. Keyway depth datum | Keyway bore phase | Comment states the datum; test measures the built solid's keyway floor against it within `TOL` |
| 10. Validation gap reaching OCCT instead of 422 | Every cutout/bore phase, at the time each `check()` extension lands | 422-with-correct-fields test at the conflict boundary, success test one step inside it |
| 11. Brittle exact-value OCCT tests | Every phase adding STL/STEP-level tests | Content-equivalence assertions (volume, triangle-count band) per L24's pattern, not exact-value assertions |

## Sources

- `docs/architecture/decision_log.md` — L03, L05, L08, L09, L12, L17-L21, L24, L25 (this
  project's own locked decisions, cited per pitfall above).
- `.planning/PROJECT.md` — v0.2 "Fit to Shaft" target features, rules, and success metrics
  (the milestone contract this research targets).
- `.planning/codebase/CONCERNS.md` — F3, F6 pitfall precedents (absolute-mm default
  infeasibility, wrong-radius measurement) already paid for once in this codebase.
- `src/spur/model.py`, `src/spur/calc.py`, `src/spur/params.py` — read in full for this
  research; line references above point at the exact functions each pitfall extends.
- Live check against the installed `cadquery==2.8.0` in this repo's `.venv`: `Shape.cut`/
  `Shape.fuse`/`Shape.intersect` signatures (`tol=`, `glue=`, `*args`) confirmed by
  `inspect.signature`.
- [Boolean Operations — old.opencascade.com (OCCT 6.9.1 user guide)](https://old.opencascade.com/doc/occt-6.9.1/overview/html/occt_user_guides__boolean_operations.html)
- [Boolean Operations — dev.opencascade.org (OCCT 7.4.0 user guide)](https://dev.opencascade.org/doc/occt-7.4.0/overview/html/occt_user_guides__boolean_operations.html)
- [Boolean Operations With Multiple Arguments — Forum Open Cascade Technology](https://dev.opencascade.org/index.php?q=node%2F1060)
- [CadQuery issue #346 — chamfer edge perpendicular to filleted edge](https://github.com/CadQuery/cadquery/issues/346)
- [CadQuery issue #1553 — "Fillets requires that edges be selected"](https://github.com/CadQuery/cadquery/issues/1553)
- [OpenCascade Mantis 0027693 — BRepMesh tessellation / parallel mesher determinism](https://tracker.dev.opencascade.org/view.php?id=27693)

---
*Pitfalls research for: spur v0.2 "Fit to Shaft" — boolean body cutouts, polygonal bores, tooth-tip chamfer on an OCCT/CadQuery gear generator*
*Researched: 2026-09-25*
