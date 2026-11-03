# Phase 32: The Shaft Solid - Context

**Gathered:** 2026-10-27
**Status:** Ready for planning

<domain>
## Phase Boundary

`shaft_model.build_shaft` turns a `ShaftParams` into one valid solid: a splined section, a plain
shank and a conical end chamfer. `model.build` and `model.export` dispatch to it, so it exports
STL and STEP through the existing pool and caches. Each kernel test proves the solid's volume
against a closed form computed without the kernel. The heaviest allowed shaft is measured against
L17's memory ceiling and L37's 30 s timeout, and the solid fields' bounds are set from that sweep.

Not in this phase:
- No `/api/shaft` route, CLI command or web page (Phase 33).
- No tolerance tables. The solid carries the **nominal** tooth thickness; Phase 34 switches it to
  the maximum-material thickness.

</domain>

<decisions>
## Implementation Decisions

### Carried forward (locked before this discussion)
- The solid carries the nominal tooth thickness (ROADMAP Phase 32 "Depends on").
- The shank joins by `Shape.fuse`, never `Workplane.union` + `.clean()`. The end chamfer is a
  revolved-cone `intersect`, never `Solid.chamfer` or an edge chamfer (ROADMAP Boundaries;
  research PITFALLS 13). Re-prove both at real DIN proportions in a kernel spike first (research
  flag).
- `Part` widens to `GearParams | ShaftParams` in the change that makes model build a shaft
  (L47 Handoffs, `parts.py` docstring). The same change types or dispatches
  `model._build_checked`, `model._write_export` and `records._gear_fields`, and resolves
  `docs/tech_debt/active/2026-10-23-parts-one-line-widening-claim-is-false.md` (git mv, INDEX
  row, same commit).
- When `model.py` first imports `shaft_model` statically, the contract "The kernel doorways are
  model and shaft_model" gains `ignore_imports = ["spur.model -> spur.shaft_model"]` in that same
  commit (30-RESEARCH Pitfall 4).
- The edits to `model._build` and `pool._warm` are additive. `make gear.unchanged` stays green.
  `calc.py`, `params.py`, `tests/regression/` and `ci.yml` are not edited.
- `cadquery` objects do not escape `model.py` / `shaft_model.py`. An edge selector that selects
  nothing raises `BuildError` (L26).
- The checks are a closed-form volume on every kernel test, not `isValid()` alone and not a
  pinned literal (research PITFALLS 13).

### Root form in the solid
- **D-01:** The tooth-to-root shape is **radial plus a root arc**. The involute runs down as far
  as the geometry allows, then a short radial line and an arc that sits on the printed `root_d`
  (the theoretical root, h_fP 0.55). This is the same idea as the gear's default
  `root_shape="radial"`. No trochoid and no `root_shape` field: `RHO_FP` is unconfirmed, and the
  rack construction sits above the DIN 5480-2 d_Ff1 maximum on 483 of 719 rows
  (`docs/tech_debt/active/2026-10-26-form-diameter-construction-exceeds-din5480-2-maximum.md`).
  The radial form starts the flank as low as possible, so a standard hub's tip does not reach the
  fillet.
- **D-02:** The solid's root circle equals the printed `root_d`, and its tip circle equals
  `tip_d`. A z-section of the built solid reads both back within a tolerance set from a
  measurement (L26 method).
- **D-03:** Every shaft's `warnings` gain one sentence: the solid's root fillet is a construction,
  not the hob's cut. It follows the pattern of the hobbed-root sentence from Phase 31. The wording
  is the planner's; it must not imply a number.

### End chamfer
- **D-04:** `end_chamfer` is a **45° cone** at the free end of the splined section. The value is
  the chamfer size at the tip diameter. At 45° the axial length equals the radial depth, so the
  field has one meaning. The cone starts on the end face at `tip_d - 2*c` and reaches `tip_d`
  at axial distance `c`. `0` means no chamfer. The field help says this.
- **D-05:** **Cap and warn**, never 422 (the L29 and L45 precedent). The applied chamfer is capped
  at the tooth height (`(tip_d - root_d)/2`, which is exactly `module` because the shift cancels) and at `splined_length`. When the request exceeds
  the cap, a warning names `end_chamfer`, the cap and which limit set it. At m 0.5 the default
  1.0 mm exceeds the tooth height (0.5 mm), so a link that sets only `module` still
  builds.
- **D-06:** New output key **`end_chamfer_effective`** on `ShaftDimensions`: the applied size,
  `null` when nothing is cut (requested 0, L45 pattern). `derive_shaft` computes it (pure maths).
  A kernel test reads the cut back from the built solid and agrees within a measured tolerance.
  This is the 13th key. L47 says "twelve keys", so log an L47 amendment in the same change. It is
  an output, so L05 does not apply. Phase 33 puts it on the wire with the others.
  — **Reversibility:** costly — once Phase 33 publishes the shaft's info response, removing or
  renaming the key breaks API consumers.

### Shank versus spline
- **D-07:** **Every `shank_d` in its range is allowed**, with no cross-field refusal: below
  `root_d`, between root and tip, equal to `tip_d`, and above it. Each regime gets a kernel row with
  the closed-form volume. The research rows are: shank equal to `d_a`, equal to `d_f`, between,
  and above `d_a` by 1e-6 and 1e-3. `shank_length` 0 means no shank and no fuse.
- **D-08:** When `shank_length > 0`, `warnings` gain one sentence: the spline steps straight into
  the shank, with no relief groove (DIN 509) and no hob run-out, and `splined_length` is a
  full-form prism. The sentence states geometry only, with no notch factor (the research's source
  for that is a low-confidence workshop article). The `splined_length` field help also says
  "full-form prism".

### Bounds sweep
- **D-09:** If the heaviest allowed shaft breaks L37's 30 s timeout or L17's memory ceiling,
  **lower the bounds until it fits**. Do not document a 503. No shaft link exists until Phase 33,
  so a tightened bound breaks nobody (L47 D-18). Record the margin in `bench/RESULTS.md`, and pin
  the bounds with a test.
- **D-10:** The sweep sets the bounds of the **four solid fields** (`splined_length`, `end_chamfer`,
  `shank_d`, `shank_length`) freely. If a spline bound (`reference_d`, `module`, `teeth`) would
  have to move, **stop and ask**, because L47 did not hand those to Phase 32. Log the solid-field
  bounds as an L47 amendment.
  — **Reversibility:** one-way after Phase 33 — once a shaft link is published, narrowing a bound
  turns valid links into 422s (L05, L44).

### Claude's Discretion
- How the flanks are represented: 16-point polylines like the gear's `FLANK_POINTS`, or
  `makeSpline`. Decide from the spike's timing and volume error.
- The size of the root arc, and how the involute meets the radial line when the base circle is
  below the root (small z).
- The tip corner shape (sharp tip land at `tip_d` unless the spike shows a reason otherwise).
- The tolerances for volume, root and tip and chamfer read-back, each set from a measurement and
  recorded beside its test.
- The rows of the heaviest-build sweep, and the gate delta against Phase 31's 2387 passed /
  221.86 s on the same host.
- Whether the shank fields get `enabled_when` (L41 vocabulary, dimmed when `shank_length` is 0)
  now or in Phase 33's form work.
- How shaft and gear share the solid cache and `_EXPORTS`. If the sharing changes memory, measure
  it (L17; research PITFALLS "One shared lru_cache").

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Scope and requirements
- `.planning/ROADMAP.md` § "Phase 32: The Shaft Solid": goal, success criteria, boundaries,
  research flag.
- `.planning/REQUIREMENTS.md`: REQ-shaft-solid, REQ-shaft-build-measured.

### Locked decisions
- `docs/architecture/decision_log.md` L47: shaft maths, frozen field set, Handoffs to Phase 32,
  and the two DIN 5480-2 amendments.
- `docs/architecture/decision_log.md` L46: part types, the second frozen link contract.
- `docs/architecture/decision_log.md` L17 (memory ceiling), L37 (30 s timeout, heaviest row), L24
  (a cached solid never carries a mesh), L26 (edge selectors never select nothing), L28 (read the
  cut back from the solid), L29 and L45 (chamfer capped and warned, null when not cut), L38
  (radial vs trochoid root), L41 (enabled_when), L43 (gate bar 300 s).

### Research
- `.planning/research/PITFALLS.md` Pitfall 13: kernel spike timings, tangent shank, the two
  meanings of "end chamfer", the closed-form volume guard, tessellation, splined length as a prism.
- `.planning/research/ARCHITECTURE.md`: the `shaft_model.py` role, part-type seam, cache and pool
  reuse.
- `.planning/research/SUMMARY.md`: CadQuery 2.8.0 construction rules.
- `.planning/phases/30-*/30-RESEARCH.md` Pitfall 4: the `ignore_imports` timing.

### Debt this phase touches
- `docs/tech_debt/active/2026-10-23-parts-one-line-widening-claim-is-false.md`: resolve here.
- `docs/tech_debt/active/2026-10-26-form-diameter-construction-exceeds-din5480-2-maximum.md`:
  context for D-01. It stays active (its trigger is Phase 34).
- `docs/tech_debt/active/2026-10-26-shaft-shift-range-narrower-than-din-5480-exceptions.md`:
  unchanged.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/spur/model.py`:
  - `_build` / `_build_checked` / `build` / `export` (lines ~773–834): the one-valid-solid
    assertion, `BuildError`, and the `TESSELLATION` presets (absolute mm: preview 0.08/0.5, fine
    0.01/0.1).
  - `FLANK_POINTS = 16` and the gear's flank radii spacing (`model.py:201`).
- `src/spur/shaft_calc.py`:
  - `derive_shaft`, `ShaftDimensions` (12 keys, frozen), the `warnings` tuple and the existing
    sentence constants (`FORM_DIAMETER_UNPROVEN`, `THEORETICAL_PIN`, `hobbed_root_warning`).
  - `check_shaft`, the cross-field problem list `ShaftParams._feasible` raises.
- `src/spur/din5480.py`: `tip_diameter`, `root_diameter`, `nominal_thickness`, `profile_shift`.
  The solid uses these numbers, never re-derived ones.
- `tests/shaft_oracle.py`: a stdlib-only involute and rack. A closed-form area integral can reuse
  its independence rule (no `calc`/`din5480` import).
- `src/spur/pool.py`: `_warm`, `BuildPool.export`. `src/spur/parts.py`: `Part = GearParams`.

### Established Patterns
- Each guard test is seen red once and recorded under `investigation/` and in `bench/RESULTS.md`.
- Measurements go to `bench/RESULTS.md` with host and command. Nothing is estimated.
- Each new warning sentence is a module constant asserted by a test.

### Integration Points
- `model.build(p: Part)` / `model.export` dispatch on `isinstance(p, ShaftParams)`, to
  `shaft_model.build_shaft`.
- The import-linter contracts in `pyproject.toml` (lines ~226–260) and `tests/test_seam.py` regex
  belts.
- `ShaftParams` field help for `splined_length` and `end_chamfer` (D-04, D-08), and their
  bounds (D-09, D-10).

</code_context>

<specifics>
## Specific Ideas

- The default shaft W 25x1.25x18x8f has `shank_d` 25.0 above `tip_d` 24.75. It exercises the
  shoulder regime and the default chamfer 1.0 under its tooth height (1.25 mm) on every
  default build.
- The research spike (placeholder proportions) measured: extrude 10–45 ms, fuse 0.18–1.5 s, cone
  cut 0.34–1.6 s, STL at most about 1 MB. Re-measure at real DIN proportions; do not carry the numbers
  over.

</specifics>

<deferred>
## Deferred Ideas

- A rack-generated (trochoid) root or a `root_shape` field on the shaft. Revisit with the
  form-diameter debt in Phase 34.
- An `end_chamfer_angle` field. Not asked for; 45° is fixed.
- A relief groove or hob run-out zone in the solid. v0.7 states its absence in a warning (D-08).

</deferred>

---

*Phase: 32-the-shaft-solid*
*Context gathered: 2026-10-27*
