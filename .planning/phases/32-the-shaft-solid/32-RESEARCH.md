# Phase 32: The Shaft Solid - Research

**Researched:** 2026-10-27
**Domain:** CadQuery 2.8.0 / OpenCascade solid construction for a DIN 5480 external spline shaft (splined prism, plain shank, 45-degree end cone), inside spur's existing kernel seam (`model._build`, one lock, one pool, shared caches)
**Confidence:** HIGH for kernel behaviour (measured today in the repo `.venv`, scripts and logs kept under `investigation/`), HIGH for repo-integration facts (files read this session), MEDIUM for Linux-container timings (taken at host load 30-46, inflated; re-measure in the plan).

All measurements below: Apple M5 Max, 18 CPUs, 64 GiB, macOS, Python 3.12.15, cadquery 2.8.0, cadquery-ocp 7.9.3.1.1, HEAD `b847c6b`, 2026-10-27, unless a row says Linux. Host load was not idle (1-minute load 4 to 46 across the session, other sessions active), so every time is "indicative"; memory and validity results do not depend on load. Whole logs: `.planning/phases/32-the-shaft-solid/investigation/` (`32-*.log`, scripts `32-*.py`; nothing under `src/` or `tests/` was touched).

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Carried forward (locked before this discussion)**
- The solid carries the nominal tooth thickness (ROADMAP Phase 32 "Depends on").
- The shank joins by `Shape.fuse`, never `Workplane.union` + `.clean()`. The end chamfer is a revolved-cone `intersect`, never `Solid.chamfer` or an edge chamfer (ROADMAP Boundaries; research PITFALLS 13). Re-prove both at real DIN proportions in a kernel spike first (research flag).
- `Part` widens to `GearParams | ShaftParams` in the change that makes model build a shaft (L47 Handoffs, `parts.py` docstring). The same change types or dispatches `model._build_checked`, `model._write_export` and `records._gear_fields`, and resolves `docs/tech_debt/active/2026-10-23-parts-one-line-widening-claim-is-false.md` (git mv, INDEX row, same commit).
- When `model.py` first imports `shaft_model` statically, the contract "The kernel doorways are model and shaft_model" gains `ignore_imports = ["spur.model -> spur.shaft_model"]` in that same commit (30-RESEARCH Pitfall 4).
- The edits to `model._build` and `pool._warm` are additive. `make gear.unchanged` stays green. `calc.py`, `params.py`, `tests/regression/` and `ci.yml` are not edited.
- `cadquery` objects do not escape `model.py` / `shaft_model.py`. An edge selector that selects nothing raises `BuildError` (L26).
- The checks are a closed-form volume on every kernel test, not `isValid()` alone and not a pinned literal (research PITFALLS 13).

**Root form in the solid**
- **D-01:** The tooth-to-root shape is **radial plus a root arc**. The involute runs down as far as the geometry allows, then a short radial line and an arc that sits on the printed `root_d` (the theoretical root, h_fP 0.55). This is the same idea as the gear's default `root_shape="radial"`. No trochoid and no `root_shape` field: `RHO_FP` is unconfirmed, and the rack construction sits above the DIN 5480-2 d_Ff1 maximum on 483 of 719 rows (`docs/tech_debt/active/2026-10-26-form-diameter-construction-exceeds-din5480-2-maximum.md`). The radial form starts the flank as low as possible, so a standard hub's tip does not reach the fillet.
- **D-02:** The solid's root circle equals the printed `root_d`, and its tip circle equals `tip_d`. A z-section of the built solid reads both back within a tolerance set from a measurement (L26 method).
- **D-03:** Every shaft's `warnings` gain one sentence: the solid's root fillet is a construction, not the hob's cut. It follows the pattern of the hobbed-root sentence from Phase 31. The wording is the planner's; it must not imply a number.

**End chamfer**
- **D-04:** `end_chamfer` is a **45 degree cone** at the free end of the splined section. The value is the chamfer size at the tip diameter. At 45 degrees the axial length equals the radial depth, so the field has one meaning. The cone starts on the end face at `tip_d - 2*c` and reaches `tip_d` at axial distance `c`. `0` means no chamfer. The field help says this.
- **D-05:** **Cap and warn**, never 422 (the L29 and L45 precedent). The applied chamfer is capped at the tooth height (`(tip_d - root_d)/2`, which is exactly `module` because the shift cancels) and at `splined_length`. When the request exceeds the cap, a warning names `end_chamfer`, the cap and which limit set it. At m 0.5 the default 1.0 mm exceeds the tooth height (0.5 mm), so a link that sets only `module` still builds.
- **D-06:** New output key **`end_chamfer_effective`** on `ShaftDimensions`: the applied size, `null` when nothing is cut (requested 0, L45 pattern). `derive_shaft` computes it (pure maths). A kernel test reads the cut back from the built solid and agrees within a measured tolerance. This is the 13th key. L47 says "twelve keys", so log an L47 amendment in the same change. It is an output, so L05 does not apply. Phase 33 puts it on the wire with the others. Reversibility: costly - once Phase 33 publishes the shaft's info response, removing or renaming the key breaks API consumers.

**Shank versus spline**
- **D-07:** **Every `shank_d` in its range is allowed**, with no cross-field refusal: below `root_d`, between root and tip, equal to `tip_d`, and above it. Each regime gets a kernel row with the closed-form volume. The research rows are: shank equal to `d_a`, equal to `d_f`, between, and above `d_a` by 1e-6 and 1e-3. `shank_length` 0 means no shank and no fuse.
- **D-08:** When `shank_length > 0`, `warnings` gain one sentence: the spline steps straight into the shank, with no relief groove (DIN 509) and no hob run-out, and `splined_length` is a full-form prism. The sentence states geometry only, with no notch factor (the research's source for that is a low-confidence workshop article). The `splined_length` field help also says "full-form prism".

**Bounds sweep**
- **D-09:** If the heaviest allowed shaft breaks L37's 30 s timeout or L17's memory ceiling, **lower the bounds until it fits**. Do not document a 503. No shaft link exists until Phase 33, so a tightened bound breaks nobody (L47 D-18). Record the margin in `bench/RESULTS.md`, and pin the bounds with a test.
- **D-10:** The sweep sets the bounds of the **four solid fields** (`splined_length`, `end_chamfer`, `shank_d`, `shank_length`) freely. If a spline bound (`reference_d`, `module`, `teeth`) would have to move, **stop and ask**, because L47 did not hand those to Phase 32. Log the solid-field bounds as an L47 amendment. Reversibility: one-way after Phase 33 - once a shaft link is published, narrowing a bound turns valid links into 422s (L05, L44).

### Claude's Discretion
- How the flanks are represented: 16-point polylines like the gear's `FLANK_POINTS`, or `makeSpline`. Decide from the spike's timing and volume error.
- The size of the root arc, and how the involute meets the radial line when the base circle is below the root (small z).
- The tip corner shape (sharp tip land at `tip_d` unless the spike shows a reason otherwise).
- The tolerances for volume, root and tip and chamfer read-back, each set from a measurement and recorded beside its test.
- The rows of the heaviest-build sweep, and the gate delta against Phase 31's 2387 passed / 221.86 s on the same host.
- Whether the shank fields get `enabled_when` (L41 vocabulary, dimmed when `shank_length` is 0) now or in Phase 33's form work.
- How shaft and gear share the solid cache and `_EXPORTS`. If the sharing changes memory, measure it (L17; research PITFALLS "One shared lru_cache").

### Deferred Ideas (OUT OF SCOPE)
- A rack-generated (trochoid) root or a `root_shape` field on the shaft. Revisit with the form-diameter debt in Phase 34.
- An `end_chamfer_angle` field. Not asked for; 45 degrees is fixed.
- A relief groove or hob run-out zone in the solid. v0.7 states its absence in a warning (D-08).
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| REQ-shaft-solid | The user downloads a valid STL and STEP of the splined section, the plain shank and the end chamfer; volume matches a closed form and the applied chamfer is read back from the solid. | Spike construction (Pattern 1) builds a valid single solid for every probed row; closed form `A(rho)` integral (Pattern 3) matches the kernel to 4e-9 relative on the default and to 6.5e-6 worst over 864 swept rows; chamfer read-back from the z=0 end face agrees to 1.4e-13 mm (Pattern 4); STL is a closed shell, STEP carries MANIFOLD_SOLID_BREP (Validation Architecture). |
| REQ-shaft-build-measured | Build time, worker memory and STL size of the heaviest allowed shaft are measured and recorded in `bench/RESULTS.md` within L17's memory ceiling and L37's timeout; field bounds are set from that sweep. | Sweep (Section "Bounds sweep, measured"): heaviest allowed corner builds in 1.9-2.6 s on macOS, 4.0-5.0 s in a Linux container at load 30+; peak RSS 1047-1062 MiB macOS, 1217-1352 MiB Linux versus 1381 MiB for a 199-tooth gear in the same container; fine STL 1.0-3.3 MB. The four solid-field bounds do not need to move. |
</phase_requirements>

## Summary

The kernel route the roadmap locked (extrude one closed outline, `Shape.fuse` a cylinder, `Shape.intersect` a revolved 45-degree cone) works at real DIN 5480 proportions. Every row I built was a single valid solid whose volume matched a stdlib closed form (the profile area is `pi*rf^2 + z * integral(2*h(r)*r dr)`, the chamfer's removed volume is the integral of the same quantity over the cone). Built through the 16-point-spline flank the gear already uses, the relative volume error is 4e-9 on the default shaft and at worst 6.5e-6 over an 864-row sweep (small tooth counts are the worst). A 16-point polyline is 3000x worse in volume (1.2e-5) and 5x heavier in faces (2874 vs 578 at z 82), so `makeSpline` is the recommendation.

Two findings change the plan. First, `.clean()` after a fuse (and therefore `Workplane.union`, which cleans by default) returns `isValid() == False` when the shank diameter equals the tip diameter or the root diameter; plain `Shape.fuse` is valid in both. Second, the cone cut has pathological parameter points: a chamfer whose cone start circle sits 3e-7 mm from the root circle **hangs the kernel** (more than 8 CPU-minutes and 2 GiB, killed), and a chamfer within 5e-7 mm of the splined length returns an empty or 3-face solid that still says `isValid()`. All of these sit off the 0.001 mm lattice that `round(..., 3)` of a cap produces, but `round()` of the splined-length cap can land above `splined_length` (by up to 0.5 micron) and then the kernel returns an **empty shape** for a plain, legal link. The cap must round **down**, and a cheap post-build volume/bbox bracket should turn any remaining silent garbage into a `BuildError`.

The heaviest allowed shaft is cheap compared with the gear: build plus slower export is about 2.6 s on this host (z 82, shank equals tip, chamfer cut), against L37's 30 s, and peak worker RSS is 92 to 98 percent of the 199-tooth gear's in the same Linux container (the gear L17's ceiling was measured on). The sweep keeps every provisional bound; the work is recording it, pinning it, and writing the L47 amendment.

**Primary recommendation:** Build `shaft_model.build_shaft` as extrude (one spline-flank outline), `Shape.fuse` the shank, `Shape.intersect` the flat-topped cone, never call `.clean()`, take the chamfer from a new pure `derive_shaft` value rounded **down** to 0.001 mm, guard the result with a volume/bbox bracket, and prove every row against an independent closed form in `tests/shaft_oracle.py`.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Flank half-angle `h(r)`, tooth height, `end_chamfer_effective`, new warning sentences | Pure maths (`din5480.py`, `shaft_calc.py`) | - | Runs on every keystroke, must stay kernel-free (contract "The shaft maths stays free of the CAD kernel and the solid"); the printed number and the cut value must come from one function (L08) |
| Outline, extrude, shank fuse, cone intersect, one-valid-solid and bracket guards | Kernel (`shaft_model.py`) | - | The only shaft module allowed to touch `cadquery`; reached only through `model` |
| Dispatch on part type, `Part` widening, lock, solid cache, export/STL copy, `_release_arenas` | Kernel doorway (`model.py`) | - | One lock and one cache keep L06/L18/L24 literally true; dispatch inside `_build` guarantees it |
| Worker process, affinity routing, timeout and replacement | Pool (`pool.py`) | - | Reused untouched; routes by `hash(p) % workers`, which works for any frozen model |
| Field bounds, help text (full-form prism, 45 degree cone) | Parameter model (`shaft_params.py`) | - | Bounds are pinned by `tests/test_shaft_params.py`; the sweep result only confirms or lowers them |
| Heaviest-build sweep, RSS, STL size, gate delta | Bench (`bench/`, `bench/RESULTS.md`) | CI/local host | Measurement is outside `make verify` (D-16 stance of `bench/`) |
| Closed-form volume, flank deviation, chamfer read-back, hang/garbage windows | Tests (`tests/test_shaft_model.py`, `tests/shaft_oracle.py`) | - | Oracle shares no code with `spur` (31-02 rule) |

## Standard Stack

No new dependency. Everything below is already pinned in `requirements.txt` [VERIFIED: requirements.txt:14-16, `cadquery-ocp-proxy==7.9.3.1.1`, `cadquery-ocp==7.9.3.1.1`, `cadquery==2.8.0`].

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| cadquery | 2.8.0 | `Edge.makeSpline/makeLine/makeThreePointArc`, `Wire.assembleEdges`, `Face.makeFromWires`, `Solid.extrudeLinear/makeCylinder/revolve`, `Shape.fuse/intersect` | Already the kernel interface of `model.py`; `cq.Solid.revolve(outerWire, innerWires, angleDegrees, axisStart, axisEnd)`, `Shape.fuse(*toFuse, glue=False, tol=None)`, `Shape.intersect(*toIntersect, tol=None)` [VERIFIED: `inspect.signature` in `.venv`, this session] |
| cadquery-ocp | 7.9.3.1.1 | OpenCascade bindings | Pinned closure; a move needs `make fixture.regen` (requirements.txt comment) |
| pydantic | 2.13.5 | `ShaftParams` (frozen, hashable) | Already the boundary; `lru_cache` and pool affinity key on it |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| stdlib `math`, `resource` | 3.12 | Oracle integration (Simpson), `ru_maxrss` peak RSS in bench | Oracle and bench only; `ru_maxrss` is bytes on macOS and KiB on Linux (Pitfall 9) |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| 16-point `makeSpline` flank | 16-point polyline | Measured: volume error 1.2e-5 vs 4e-9 at default, 6.8e-7 vs 4.2e-10 at z 82; faces 599 vs 95 and 2874 vs 578. Polyline only if a spline ever fails to build |
| `fuse` then `intersect` | `intersect` the spline prism, then `fuse` the shank | Both pass 864 swept rows; `fuse`-first is faster on the default (0.55 s vs 0.68 s) and has no garbage window for `splined_length >= chamfer`; `intersect`-first returned a 3-face 4 percent-off solid at `splined_length = chamfer + 5e-7` with a shank. Keep the roadmap's order |
| Revolved cone `intersect` | `Solid.chamfer` on end-face edges | Measured not usable: `BRep_API: command not done` for c >= 1.2 on the default (Pitfall 6); locked out anyway |

**Installation:** none. **Version verification:** `.venv/bin/pip list` this session: cadquery 2.8.0, cadquery-ocp 7.9.3.1.1, pydantic 2.13.5 [VERIFIED: pip list].

## Package Legitimacy Audit

No external package is installed or added by this phase, so there is nothing to run through `package-legitimacy check`.

| Package | Registry | Age | Downloads | Source Repo | Verdict | Disposition |
|---------|----------|-----|-----------|-------------|---------|-------------|
| (none) | - | - | - | - | - | - |

**Packages removed due to [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** none

## Architecture Patterns

### System Architecture Diagram

```
ShaftParams (frozen, validated once)
   |
   |  derive_shaft(p)  [pure, kernel-free]   <-- din5480.flank_half_angle(r) (new, pure)
   |    tip_d, root_d (3 dp), end_chamfer_effective (new, floor 3 dp), warnings (+D-03, D-05, D-08)
   v
model.build(p) / model.export(p, fmt, quality)        [_LOCK, _build_cached(lru 4, shared with gear)]
   |  _build: if isinstance(p, ShaftParams): shaft_model.build_shaft(p)   (static import,
   |          ignore_imports added to the doorway contract in the same commit)
   v
shaft_model.build_shaft(p)  [kernel; reads ONLY derive_shaft numbers + din5480 half-angle]
   1 outline: per tooth  radial line (only if base circle > root) -> left flank spline (16 pts, r^1.5 spacing)
              -> tip arc at tip_d -> right flank spline -> radial line -> root arc at root_d (3-point arc)
   2 Solid.extrudeLinear(face, (0,0,Ls))                        z in [0, Ls], free end at z = 0
   3 if shank_length > 0:  body = body.fuse(Solid.makeCylinder(shank_d/2, Lk, (0,0,Ls)))   NEVER .clean()
   4 if c > 0:             body = body.intersect(cone)   cone = revolve of
                           (0,0)->(ra-c,0)->(ra,c)->(big,c)->(big,Ls+Lk)->(0,Ls+Lk), big = max(ra, shank_d/2)+1
   5 guards: len(Solids)==1, isValid, bbox z-extent, volume bracket  -> BuildError (never a plausible shape)
   v
export: STL (preview/fine) via shape.copy().exportStl (L24), STEP via shape.exportStep
   v
BuildPool worker (spawned, warmed by `import spur.model` which now pulls shaft_model) -> bytes -> parent _EXPORTS
```

### Recommended Project Structure
```
src/spur/
├── din5480.py        # + flank_half_angle(m, z, xm, r) (pure; thickness from tooth_thickness)
├── shaft_calc.py     # + end_chamfer_effective, ShaftDimensions.end_chamfer_effective, 3 warning constants
├── shaft_params.py   # help text for splined_length / end_chamfer; bounds unchanged unless the sweep says otherwise
├── shaft_model.py    # build_shaft(p) -> cq.Solid; imports NOTHING from spur.model (no cycle)
├── model.py          # Part widening, isinstance dispatch in _build, part-aware error text, slug stem
├── parts.py          # Part = GearParams | ShaftParams
└── records.py        # _gear_fields typed Part (slug() + model_dump already exist on both)
tests/
├── shaft_oracle.py   # + tooth_half_angle, profile_area_within(rho), section volume (stdlib only)
└── test_shaft_model.py   # kernel rows, read-backs, guards, windows
bench/sweeps/shaft.json   # heaviest-build rows; build_time.py gains a part switch
```

### Pattern 1: The outline (verified shape; 40 faces at z 6 up to 578 at z 82)
**What:** One closed wire of `z` repeats of: radial line (only when the base circle radius `rb` exceeds the root radius `rf`), left flank `makeSpline` through 16 points, tip `makeThreePointArc` centred on the tooth, right flank spline, radial line, root `makeThreePointArc` to the next tooth. Radii of the 16 points: `rs + (ra - rs) * (i/15)**1.5`, `rs = max(rf, rb)`, the gear's spacing (`model.py:201`).
**When to use:** always (D-01). When `rb <= rf` (all but 98 of 7,546 scanned parameter rows) there is no radial line and the flank starts on the root circle.
**Example:**
```python
# Source: .planning/phases/32-the-shaft-solid/investigation/32-spike.py (ran; 864 rows valid, closed form agrees)
# half-angle of the tooth at radius r >= rb:  h(r) = psi_b - inv(acos(rb / r))
# psi_b = s_b / (2 * rb), s_b = m*cos(a)*(pi/2 + z*inv(a)) + 2*xm*sin(a), a = 30 deg
radii = [rs + (ra - rs) * (i / 15) ** 1.5 for i in range(16)]
left  = [polar(r, c - h(r)) for r in radii]
right = [polar(r, c + h(r)) for r in reversed(radii)]
edges += [Edge.makeSpline(left), Edge.makeThreePointArc(left[-1], polar(ra, c), right[0]),
          Edge.makeSpline(right)]
# rb > rf only: Edge.makeLine(polar(rf, c - h(rb)), left[0]) before, Edge.makeLine(right[-1], polar(rf, c + h(rb))) after
edges.append(Edge.makeThreePointArc(polar(rf, c + h_root), polar(rf, c + pitch/2), polar(rf, c + pitch - h_root)))
```
`ra` and `rf` are the printed `tip_d/2` and `root_d/2` (3-dp diameters), `h` uses the **unrounded** thickness (`din5480.tooth_thickness`). Using the printed radii makes `shank_d == tip_d` an exact float tie, which is the best-tested case (Pitfall 1 shows why). Degeneracy scan over 7,546 valid (module, teeth, shift) rows [VERIFIED: `32-scan.py`]: smallest tip-land chord 0.9675*m (m 0.5, z 6, x +0.45), smallest root-arc chord 0.894*m (m 0.5, z 6, x +0.3), so the kernel's dead band for a short arc (`ROOT_ARC_MIN` 2e-6, `model.py:68`) is never reachable and no `ROOT_ARC_MIN` logic is needed.

### Pattern 2: Fuse, then intersect, no clean
**What:** `body = extrudeLinear(face, (0,0,Ls))`; `body = body.fuse(cylinder)` when `shank_length > 0`; `body = body.intersect(cone)` when the applied chamfer is above 0. Result `.Solids()[0]` after asserting exactly one.
**Measured:** default shaft 0.55 s total (extrude 8 ms, fuse 0.19 s, cone 0.35 s); z 82 m 1 shank equal tip, chamfer: about 2.4 s (fuse 1.04 s, cone 1.3 s). `glue=True` made the fuse 2x faster on the default but its partial-coincident-face semantics are unproven for the shank-larger-than-tip case, so do not use it [ASSUMED: OCCT glue semantics from training; the speed gain is measured, the safety is not].
**The cone profile** (verified): polygon in the XZ plane `(0,0), (ra-c,0), (ra,c), (big,c), (big,Ls+Lk), (0,Ls+Lk)` revolved 360 degrees about Z with `Solid.revolve(Wire.makePolygon(pts + [pts[0]]), [], 360, (0,0,0), (0,0,1))`.

### Pattern 3: The closed form (independent oracle, stdlib only)
With `h(r)` constant `= h(rb)` below `rb` (the radial line), the profile area inside a disc of radius `rho` is `pi*min(rho,rf)**2` for `rho <= rf` and `pi*rf**2 + z * integral_{rf}^{min(rho,ra)} 2*h(r)*r dr` otherwise. Then
`V = A(ra) * Ls + pi*(shank_d/2)**2 * Lk - integral_0^c [A(ra) - A(ra - c + t)] dt`.
The shank adds no overlap term: it starts at `z = Ls`. Simpson with 2000 panels and 200 panels for the chamfer integral reproduced the kernel to 4e-9 (default). Put `tooth_half_angle` and `profile_area_within` in `tests/shaft_oracle.py` using its own `_ALPHA`, never `spur.din5480` (its docstring rule, `tests/shaft_oracle.py:1-26`).

### Pattern 4: Read-backs from the built solid (all measured)
| Quantity | How | Worst agreement | Where |
|----------|-----|-----------------|-------|
| Applied chamfer | the single `PLANE` face with `BoundingBox().zmin == zmax == 0`; `c_read = ra - max radius` over sampled points of its edges | 1.42e-13 mm over 80 rows | `32-readback.py` |
| Axial chamfer (45 degrees) | max `BoundingBox().zmax` over `CONE` faces | 1.0e-7 mm (the box carries ~1e-7 tolerance); use the repo's `TOL = 1e-6` | same |
| Root radius | min radius over the z=0 face edges | 5.7e-14 mm | same |
| Flank position | polar angle of sampled points on z=0 `BSPLINE` edges vs oracle `h(r)` | 2.6e-4 mm worst (m 10, z 9); 8.7e-5 mm at m 2, z 6; 5.7e-9 at z 82 | `32-flank-dev.py` |
| Mesh | STL closed-shell check (`test_model.py::_closed_shell_volume` pattern) vs closed form | preview -1.9e-3 (default), -3.3e-3 (z 6); fine -3.1e-4, -6.1e-4 | `32-stl-volume.py` |

Do **not** pin the `CONE` face count: the revolve seam sits on +X, which is tooth 0's centre line, so the patch of tooth 0 is split (19 cone faces for 18 teeth). Count nothing; read radii.

### Anti-Patterns to Avoid
- **`.clean()` anywhere after the fuse** (see Pitfall 1). It also mutates shared sub-shapes: reusing an operand after a `clean()` made later booleans on it invalid in my first (contaminated) run.
- **`round(min(request, cap, Ls), 3)`** for the splined-length cap (Pitfall 3).
- **Counting faces or cone patches** in tests (topology moves with the seam and the tangent cases: 95 vs 112 faces for the same part).
- **Importing `spur.model` from `shaft_model`.** `model` imports `shaft_model` statically (contract handoff), so the reverse edge is a cycle. The solid needs no narrowers: `cq.Solid` and `Shape` methods cover it.
- **Fixing a hang with `signal.alarm`** in a test: OpenCascade runs in C++ and a Python signal handler cannot run until it returns. Windows tests need a subprocess with a wall clock (as `32-windows.py`).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Involute point/half-angle | A second involute solver in `shaft_model` | One pure `din5480.flank_half_angle(m, z, xm, r)` shared by the solid; the test oracle keeps its own copy | The part and the printed number cannot disagree (L08); the oracle must stay independent |
| Chamfer edge selection | A selector that finds tooth edges to chamfer | Revolved-cone `intersect` | One boolean, no selector to go empty; locked by ROADMAP |
| Flank interpolation | Many `makeLine` segments | `Edge.makeSpline` through 16 points | 3000x lower volume error, 5x fewer faces |
| Mesh validity | A new STL parser | The existing closed-shell/signed-volume helper pattern in `tests/test_model.py:1984-2006` | Already the repo's slicer-safety proof |
| Peak memory | psutil/tracemalloc | `resource.getrusage(RUSAGE_SELF).ru_maxrss` in a fresh process per row | No dependency; same quantity as the worker's resident peak; mind the unit |
| Process-level hang protection in tests | `signal.alarm`, threads | `subprocess.run(..., timeout=)` per kernel probe | OCCT does not return to Python to run the handler |

**Key insight:** the kernel is not the hard part of this phase; its silent failure modes are. Every check must be an independent number (closed form, read-back), because `isValid()` is `True` for an empty compound, for a 3-face solid 4 percent off, and for a mesh whose chamfer was dropped.

## Runtime State Inventory

Not applicable: this phase adds a part type; nothing is renamed or migrated. Verified by reading the contract list, `app.py`, `pool.py`, `records.py` and `parts.py`: no stored data, service config, OS registration, secret or build artifact carries a shaft name. (`Stored data`: none. `Live service config`: none. `OS-registered state`: none. `Secrets/env vars`: none; `SPUR_SOLID_CACHE` and `SPUR_BUILD_TIMEOUT` are read, not renamed. `Build artifacts`: none; `requirements.txt` is not edited.)

## Common Pitfalls

### Pitfall 1: `.clean()` makes the tangent shank invalid
**What goes wrong:** `body.fuse(shank).clean()` and `Workplane.union(...)` (which cleans) give `isValid() == False` when `shank_d == tip_d` (24.75) and when `shank_d == root_d` (22.25) on the default. Volume still agrees to 4e-9, so a volume-only test passes.
**Evidence:** fresh body per variant [VERIFIED: `32-negatives2.log`]: `shank=tip 24.75  Shape.fuse valid=True | fuse().clean() valid=False | WP.union.clean valid=False | WP.union(clean=False) valid=True`; same for `shank=root 22.25`; `between 23.5`, `tip+1e-6`, `25` are valid in all four.
**How to avoid:** never call `.clean()`; assert `isValid()`. Seen-red candidate for the guard test: swap in `.clean()` and watch `shank=tip` fail.
**Warning signs:** a test that checks volume but not `isValid()`; the same shank diameter passing on one row and failing after a refactor that touches the fuse call.

### Pitfall 2: A cone start circle on the root circle can hang the kernel
**What goes wrong:** `fuse` then `intersect` with `c = module + 3e-7` or `module - 3e-7` (default shaft, cone start `ra - c` is 3e-7 off `rf`) did not return in 25 s; a first run reached 8.5 CPU-minutes and 2.1 GiB before it was killed. Offsets of +-1e-8 to +-1e-3 around it, including 0, +2.5e-7, +3.1e-7, +3.5e-7, -2.5e-7 and -3.5e-7, all built in 0.6 s.
**Evidence:** [VERIFIED: `32-nearcap.log` (13 points), `32-windows-radial.log`, `32-windows-radial2.log` (both orders hang at exactly +-3e-7), `32-windows-radial-grid.log` (50 more offsets all fine)]. It is an isolated pathological point, not a band.
**Why it matters:** `SPUR_BUILD_TIMEOUT` (L37) rescues the server with a 503 and a replaced worker, but the CLI calls `model.export` in-process (`src/spur/cli.py:102`, no `timeout` or `BuildPool` in that file [VERIFIED: grep]), so nothing ends a hang there.
**How to avoid:** every chamfer the solid cuts lies on the 0.001 lattice (`end_chamfer_effective` rounded to 3 dp) and `ra`, `rf` are multiples of 0.0005, so `ra - c - rf` is a multiple of 0.0005 up to float noise (1e-15): the hang offset is unreachable. Make that explicit with a pre-build defect guard in `shaft_model`: `if 1e-9 < abs(ra - c - rf) < 1e-4: raise BuildError(...)`. It never fires on the lattice and costs two floats. The cap case `c == module` (offset 0, or +-5e-4 after rounding) is the **default behaviour for every module below 1.0**, so the sweep must cover it: 864 rows (9 modules x 8 teeth x 3 shifts x 4 shank regimes), `c` at the cap, **0 bad, 0 hangs** in both orders [VERIFIED: `32-cap-sweep-fuse_cut.log`, `32-cap-sweep-cut_fuse.log`].

### Pitfall 3: `round()` of the splined-length cap exceeds the splined length and the kernel returns an empty shape
**What goes wrong:** `splined_length = 2.0006`, request above it: `round(min(request, tooth, Ls), 3) = 2.001 > Ls`. The intersect returns `nsolids=0, faces=0` while `isValid()` is `True` (no shank). With a shank the solid is fine (2.95e-7 off).
**Evidence:** [VERIFIED: `32-round-up.log`: `Ls=2.0006 c=2.001 (d=-4.0e-04) Lk=0.0: valid=True nsolids=0 faces=0 vol rel=1.00e+00`; `Ls=5.0007 ... nsolids=0`; `Ls=2.0004 c=2.0 ... nsolids=1`]. `splined_length` has no step enforcement (`ShaftParams` accepts any float 1..500), so this is a legal link.
**How to avoid:** the cap must round **down**: `floor(x * 1000 + 1e-9) / 1000` (the epsilon stops `0.29` flooring to `0.289`; check the float behaviour of the helper with a test over a decimal grid). The same reasoning argues for flooring the tooth-height cap, but rounding it up by 0.5 micron is harmless (`c = module + 5e-4` built valid, volume 1e-6 off the capped form, `32-nearcap.log`); keep one rule and floor both so "capped at the tooth height" is literally true.
**Also:** `c` within 5e-7 of `Ls` is only dangerous **above** `Ls`. With `c <= Ls` (flooring guarantees it) the fuse-first order was clean at 42 offsets from 1e-9 to 1e-3 and with 0 and 20 mm shanks [VERIFIED: `32-windows-axial-pos.log`]. The intersect-first order is not: `Ls = c + 5e-7` with a 20 mm shank returned `valid=True n=1 faces=3 vol_rel=4.10e-02` [VERIFIED: `32-windows-axial.log`]. That is the strongest reason to keep fuse-first.

### Pitfall 4: A chamfer below about 1e-5 mm is silently not cut, or shatters the end face
**What goes wrong:** with c = 1e-5 the cone cuts (19 cone faces); at 5e-6 to 5e-7 the end face splits into 19 planar faces and no cone appears; at 2e-7 and below nothing is cut at all, and the solid is valid and 3.9e-9 off the **uncut** closed form [VERIFIED: `32-tiny.log`].
**How to avoid:** `end_chamfer_effective` rounds down to 0.001 mm (100x above the first anomaly) and is `None` when the result is 0, with a warning naming `end_chamfer` that the request was below the resolution (L45 pattern: asked and not cut prints no number).

### Pitfall 5: The chamfer cone silently eats the root core past the tooth height
**What goes wrong:** the cone is valid at any size. `c = 1.5` on the default (tooth height 1.25) gives `valid=True` and a volume 6.0e-4 off the capped form; `c = 3` 8.0e-3; `c = 12` 1.4e-1 [VERIFIED: `32-negatives.log`]. This, not `Solid.chamfer`, is the "wrong volume and no error" mode for this design, so the cap test must go red when the cap is removed.

### Pitfall 6: `Solid.chamfer` on the end-face outline is not the silent failure the research described
**What goes wrong:** it raised `Standard_Failure: BRep_API: command not done` for c >= 1.2 on the default and built valid for c <= 1.0 [VERIFIED: `32-negatives.log`]. The research's "silently invalid" was not reproduced at these proportions. The conclusion stands (locked: do not use it) but cite the measured behaviour, not the research's.

### Pitfall 7: Kernel exceptions are labelled with the gear's advice
**What goes wrong:** `_build_checked` converts any non-`BuildError` into `"Geometry kernel failed (...); try smaller fillets or chamfers."` (`model.py:798-799`). A shaft has no fillets; the advice is wrong and tells the user to change `end_chamfer` for an unrelated defect.
**How to avoid:** word the shaft's wrapper as a modelling defect (the `_NOT_A_PARAMETER_PROBLEM` pattern, `model.py:235-237`) or catch inside `build_shaft`. Test both texts.

### Pitfall 8: `tests/test_hooks.py` pins the heavy-file set, and a new kernel test file enters the 30 s commit slice
**What goes wrong:** `HEAVY_TEST_FILES = ("test_model", "test_pool", "test_api", "test_cli", "test_browser")` (`tests/test_hooks.py:39`) and `make test.fast` names exactly those five in `--ignore=` flags (`Makefile:223-226`). `tests/test_shaft_model.py` is collected by `verify.fast` unless the Makefile and the pin move together.
**How to avoid:** price the new file before deciding. 20 kernel rows at 0.3-2.4 s each is 10-30 s serial, 2-5 s over 8 workers. If the commit slice stays under L36's 30 s with it, leave it; if not, add it to both lists in one commit.

### Pitfall 9: `ru_maxrss` units
**What goes wrong:** macOS reports bytes, Linux KiB. My first Linux gear reading printed "1 MiB" because of it. Branch on `sys.platform` and record the host.

### Pitfall 10: A baseline that is not in the repo
**What goes wrong:** CONTEXT cites "Phase 31's 2387 passed / 221.86 s". `bench/RESULTS.md` holds Phase 31's `2355 passed in 243.23s`, `real 244.14` (`### The gate delta (31-06)`), and the string `221.86` appears in no committed file [VERIFIED: `grep -rn 221\.86` found only CONTEXT]; `2387 passed` appears only in `PROJECT.md:727`.
**How to avoid:** run `make verify` at the start of Phase 32 on the unmodified tree and record it with the load, then again at close, same host. Do not subtract against a number that has no log.

### Pitfall 11: `pool._warm` needs no edit
`_warm` does `importlib.import_module("spur.model")` (`pool.py:50`), and `model.py` will import `shaft_model` at module level, so a worker is warmed with the shaft code already. The roadmap's "additive `pool._warm` edit" has nothing to add. ARCHITECTURE.md's alternative (a function-local import in `_build`) also needs the `ignore_imports` line and leaves the shaft module cold in the worker until the first shaft request.

## Code Examples

### Closed form, stdlib only (the shape of the oracle addition)
```python
# Source: .planning/phases/32-the-shaft-solid/investigation/32-spike.py (ran against the kernel)
def tooth_half_angle(m, z, xm, r):
    rb = m * z * cos(A) / 2
    s_b = m * cos(A) * (pi / 2 + z * inv(A)) + 2 * xm * sin(A)
    return s_b / (2 * rb) - inv(acos(min(1.0, rb / max(r, rb))))      # radial below the base circle

def profile_area_within(m, z, xm, rf, ra, rho):
    if rho <= rf:
        return pi * rho * rho
    return pi * rf * rf + z * simpson(lambda r: 2 * tooth_half_angle(m, z, xm, r) * r, rf, min(rho, ra))

def volume(m, z, xm, rf, ra, Ls, c, shank_d, Lk):
    full = profile_area_within(m, z, xm, rf, ra, ra)
    removed = simpson(lambda t: full - profile_area_within(m, z, xm, rf, ra, ra - c + t), 0, c, 200) if c > 0 else 0
    return full * Ls + pi * (shank_d / 2) ** 2 * Lk - removed
```
Split the radial integral at `rb` when `rb > rf`, as the spike does.

### Applied chamfer read-back
```python
# Source: 32-readback.py (agreement 1.4e-13 mm over 80 rows)
end = [f for f in solid.Faces() if f.geomType() == "PLANE"
       and abs(f.BoundingBox().zmin) < 1e-6 and abs(f.BoundingBox().zmax) < 1e-6]
assert len(end) == 1
rmax = max(hypot(v.x, v.y) for e in end[0].Edges() for v in (e.positionAt(i / 20) for i in range(21)))
c_read = ra - rmax
```

### Guard turning silent garbage into a defect (to write in `shaft_model`)
```python
# Bracket from kernel-measured pieces only: face.Area() before the extrude. Removed volume by the cone
# is at most c * (A_full - pi*rf^2), because the disc of radius rf is inside every cone section (c <= tooth height).
upper = area * Ls + pi * (shank_d/2)**2 * Lk
lower = upper - c * (area - pi * rf**2)
if not (lower * (1 - 1e-4) <= solid.Volume() <= upper * (1 + 1e-4)) or abs(zlen - (Ls + Lk)) > 1e-6:
    raise BuildError("The shaft solid is not the shape that was asked for: a modelling defect in spur, "
                     "not a conflict in these parameters.")
```
The 3-face solid in Pitfall 3 is 4.1 percent off, so a 1e-4 slack catches it with 400x room; the empty shape is already caught by `len(solids) != 1`. Measure the slack on the sweep before fixing it (the worst honest row was 6.5e-6 off the closed form, but the bracket is looser than the closed form).

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Research prototype: crude hob root, placeholder proportions | Radial + root arc at real DIN proportions (`rb > rf` only for z <= 9) | This phase | Research timings (fuse 0.18-1.5 s, cone 0.34-1.6 s) were within 2x of the real-proportion numbers below, but not carried over |
| "`Solid.chamfer` silently invalid" (research) | `Standard_Failure` at c >= 1.2 (default), valid below | measured 2026-10-27 | Locked decision unchanged; evidence updated |

**Deprecated/outdated:** `Workplane.union(...).clean()` for this part (invalid on the tangent shank). Nothing else.

## Bounds sweep, measured

Rows run in a fresh process each (`32-row.py`: build, preview + fine STL through `shape.copy().exportStl`, STEP, `ru_maxrss`). macOS rows at load 8.5 (`32-sweep.log`) and again at load 4-6 for three rows (`32-sweep-rerun.log`); Linux rows in `python:3.12-slim-bookworm` (arm64, Docker VM 16 GB, `requirements.txt` closure, `32-sweep-linux.log` and `32-linux-gear.log`) at host load 30-46, so Linux times are inflated.

| Row | z | m | Ls | Lk | shank | c | build s (mac) | build s (Linux) | fine STL | STEP | peak RSS mac / Linux (MiB) |
|-----|---|---|----|----|-------|---|---------------|-----------------|----------|------|-----------------------------|
| default W25x1.25x18 | 18 | 1.25 | 30 | 20 | 25 | 1 | 0.54 | 1.98 | 283 KB (5,660 tri) | 716 KB | 583 / 917 |
| z6 m10 max length | 6 | 10 | 500 | 500 | 850 | 10 | 0.66 | 1.62 | **3.32 MB (66,454 tri)** | 511 KB | 546 / 870 |
| z82 m1 | 82 | 1 | 500 | 500 | 84 | 1 | 1.67-1.72 | 4.0-4.5 | 1.01 MB | 2.38 MB | 1062-1071 / **1266-1352** |
| z82 m10 x+0.45 all maxima | 82 | 10 | 500 | 500 | 850 | 10 | 1.89-1.92 | 4.2-4.8 | 1.68 MB (33,672 tri) | 2.57 MB | 1042-1047 / 1217-1257 |
| z82 m10 x-0.05 shank = tip | 82 | 10 | 500 | 500 | 828 | 10 | 2.07 (fuse 0.52, cone 1.51) | 4.8 | 1.67 MB | 2.70 MB | 1047 / 1132 |
| z82 m10 x+0.45 Ls 1, c 1, no shank | 82 | 10 | 1 | 0 | - | 1 | 2.13 (cone 2.10) | 5.2 | 1.06 MB | 2.73 MB | 973 / 1225 |
| z82 m10 prism only (c 0, no shank) | 82 | 10 | 500 | 0 | - | 0 | 0.04 | 0.15 | 1.04 MB | 2.58 MB | 534 / 788 |

- **Time** is driven by tooth count and by the cone cut (1.3-2.1 s at z 82), not by any of the four solid fields: Ls 1 vs 500 and c 0.001 vs module changed the cone cut by under 10 percent [VERIFIED: `32-c-time.log`, 18 rows, 2.33-2.62 s total at z 82]. Worst single request (build plus slower export) on macOS: 2.17 s; on Linux under load: 5.4 s, against `SPUR_BUILD_TIMEOUT` 30 s. Margin: 11x macOS, 5.5x loaded Linux.
- **Memory.** Same container, same measure, gear baseline: `gear z=82` peak 1028 MiB, `gear z=199` (the top of L17's 160-199 corpus) **1381 MiB** [VERIFIED: `32-linux-gear2.log`]. The heaviest shaft peaks at 1266-1352 MiB, i.e. 92 to 98 percent of the gear L17's ceiling was earned on. On macOS: gear z 199 1350 MiB, shaft 1042-1071. The peak is the cone intersect at z 82, not the cached solid (retained solid size was not measured separately; L17 sized 4 entries at about 280 MiB for a 199-tooth gear).
- **STL size** is largest for **few** teeth on a long shaft (3.3 MB, z 6 m 10 Ls 500), not for the most teeth (1.0-1.7 MB at z 82); the gear's 9.06 MB at z 199 is the larger case. Not close to anything that moves gzip level (L19).
- **Bounds.** `splined_length` 1..500, `end_chamfer` 0..10, `shank_d` 1..850, `shank_length` 0..500 hold: the corner with all four at their maxima is not the heaviest build, and the heaviest one is 5.5x inside the timeout under the worst conditions measured. No spline bound needs to move (D-10's stop-and-ask is not triggered). The record is "sweep run, provisional bounds confirmed", and the pin is the existing `tests/test_shaft_params.py::test_each_field_bound_is_inclusive_and_one_step_outside_is_refused` (`tests/test_shaft_params.py:93-103`), extended to cite the sweep rows.
- **Not measured:** L37's contention shapes (two workers busy, ten concurrent builds) for the shaft; one row through a real `BuildPool` worker with `ps` polling; Linux numbers on an idle host. These are plan-time tasks, listed under Open Questions.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `fuse(..., glue=True)` is unsafe to use because OCCT's glue option assumes only fully coincident faces (training knowledge); the speed gain (about 2x on the default) is measured, the safety claim is not | Pattern 2 | Low: the recommendation is "do not use it"; if wrong, a 0.2 s saving is forgone |
| A2 | Flooring both caps with `floor(x*1000 + 1e-9)/1000` is float-safe for all steps the UI and API can send | Pitfall 3 | Medium: a request of 0.29 could print 0.289. A test over a decimal grid (0.001 steps, 0..10) must exist; I did not run it |
| A3 | Hang points other than +-3e-7 around the root circle may exist off the lattice (I scanned about 70 offsets, not a continuum) | Pitfall 2 | Low on the lattice (unreachable) but it is why the pre-build defect guard is recommended, not optional |
| A4 | The volume-bracket slack of 1e-4 is wide enough that no honest row trips it | Code Examples | Medium: worst honest closed-form error was 6.5e-6 but the bracket's own slack for large chamfers on tiny teeth was not swept; measure before pinning |
| A5 | `hash(p) % workers` routes a `ShaftParams` correctly because the pydantic frozen model hashes by field values (ARCHITECTURE F4 says a probe showed `hash(GearParams()) != hash(ShaftParams())`) | Architecture | Low; the `test_pool.py` shaft row proves it end to end |
| A6 | A memory reading taken on a loaded host equals the idle-host reading (peak RSS does not depend on load; time does) | Bounds sweep | Low |

## Open Questions

1. **Where does the chamfer cap's rounding rule live, and is `end_chamfer_effective` keyed to rounded or exact tooth height?**
   - What we know: `tip_d` and `root_d` are 3-dp diameters; `(tip_d - root_d)/2` equals `module` to within 0.0005; flooring both caps keeps `ra - c - rf >= 0` on the 0.0005 lattice.
   - What's unclear: whether the planner prefers `cap = module` (exact, simple) or `cap = (tip_d - root_d)/2` (consistent with the radii the solid uses). Both are on the lattice.
   - Recommendation: use the radii the solid uses, floor to 3 dp, so the read-back test compares like with like.
2. **Does the human want the contention shapes measured for the shaft?**
   - What we know: L37 recorded SC3 (ten distinct rows, both workers busy) for the gear's worst row; a shaft request is 5.5x inside the timeout alone.
   - What's unclear: whether REQ-shaft-build-measured needs a contended row or the single-build row suffices.
   - Recommendation: record the single-build row as the requirement's evidence and file a `nice` debt item "shaft contention row" if not run; the heaviest build is far from the timeout.
3. **Position of `end_chamfer_effective` among the `ShaftDimensions` keys, and the shaft's `slug()`.**
   - What we know: `tests/test_shaft_calc.py:83-87` pins the list "in this order" and says the keys become Phase 33's dims rows; `_write_export` and `records._gear_fields` call `p.slug()`.
   - What's unclear: the key position and the download-name stem (Phase 33 owns the download name, L40 for the gear).
   - Recommendation: append `end_chamfer_effective` after `measure_over_pins` and before `designation` (it groups with the numbers, not the strings); give `ShaftParams.slug()` a plain filename-safe stem (for example `spur_shaft_w{reference_d:g}x{module:g}x{teeth}`) and mark it provisional for Phase 33. Surface both at plan review.
4. **Does a new kernel test file stay in the commit slice?** See Pitfall 8; decide from a `make verify.fast` reading after the file exists.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.12 (`.venv`) | all | yes | 3.12.15 | - |
| cadquery / OCP | kernel tests, bench | yes | 2.8.0 / 7.9.3.1.1 | - |
| make, ruff, mypy, import-linter, pytest-xdist | `make verify` | yes | ruff 0.16.10, mypy 2.4.0, import-linter 2.15, pytest 9.1.1, xdist 3.8.0 | - |
| Docker (OrbStack) | Linux memory/timing row | yes | Docker 29.8.2 | skip Linux row, record host only |
| `spur:latest` image | image-based sweeps | no | - | throwaway `python:3.12-slim-bookworm` plus `pip install --no-deps -r requirements.txt` (what I used; about 2 minutes) |
| git tag `v0.6` | `make gear.unchanged` | not re-checked this session | - | the script fetches it (30-01) |

**Missing dependencies with no fallback:** none.
**Missing dependencies with fallback:** the prebuilt image (rebuilding its apt layer took about 19 minutes in Phase 30).

## Validation Architecture

Nyquist validation is enabled (`.planning/config.json` has no `workflow.nyquist_validation` key, so it is treated as enabled).

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.1.1 with pytest-xdist 3.8.0 and pytest-cov 7.1.0; `--strict-markers --strict-config`, `filterwarnings = error`, `faulthandler_timeout = 170` [VERIFIED: pyproject.toml:122-133] |
| Config file | `pyproject.toml` `[tool.pytest.ini_options]`; coverage `fail_under = 96` (pyproject.toml:161) |
| Quick run command | `.venv/bin/python -m pytest tests/test_shaft_model.py tests/test_shaft_calc.py tests/test_shaft_params.py tests/test_seam.py -q -n0 --no-cov` |
| Full suite command | `make verify` (ruff, mypy `--strict`, import-linter, no-fake-done, gear.unchanged, pytest with coverage) |

### Phase Requirements -> Test Map
| Req ID / criterion | Behavior | Test Type | Automated Command | File Exists? |
|--------------------|----------|-----------|-------------------|-------------|
| REQ-shaft-solid / SC1 | Default shaft: one valid solid, volume = closed form (rel bar set from the 864-row sweep, 6.5e-6 worst; propose 1e-4 and record beside the test) | kernel | `pytest tests/test_shaft_model.py -k default -q -n0 --no-cov` | no, Wave 0 |
| SC1 | STL preview + fine: closed shell, mesh volume within the measured mesh bias (-3.3e-3 preview worst, -6.1e-4 fine); STEP starts `ISO-10303-21;` with `MANIFOLD_SOLID_BREP` | kernel | `-k export` | no, Wave 0 |
| SC1 | Splined section + shank + chamfer all present: bbox z-extent `Ls + Lk`, radial extent `max(ra, shank_d/2)`, root/tip read back (5.7e-14) | kernel | `-k section` | no, Wave 0 |
| SC2 | Shank rows: = `tip_d`, = `root_d`, between, +1e-6, +1e-3, -1e-9, 1 ulp, below root, 850, `shank_length` 0: valid and closed form | kernel (parametrised, ~12 rows) | `-k shank` | no, Wave 0 |
| SC2 | `.clean()` guard seen red once: `fuse().clean()` at `shank=tip` reproduces `valid=False` (`32-negatives2.log`) | kernel | `-k clean` | no, Wave 0 |
| SC2 | Chamfer read-back = `end_chamfer_effective` (1.4e-13 worst; bar at `TOL` 1e-6); cone axial extent equals c | kernel | `-k chamfer_readback` | no, Wave 0 |
| SC2 | Cap: request above tooth height (m 0.5 default 1.0) and above `splined_length` builds the capped size, closed form at the **effective** value, warning names `end_chamfer`, the cap and the limit; removing the cap goes red (6.0e-4 to 1.4e-1 off) | calc + kernel | `-k cap` | no, Wave 0 |
| SC2 | Splined-length cap rounds down: `Ls = 2.0006`, no shank, request 5 builds one solid (`round()` returned an empty shape) | kernel | `-k round_down` | no, Wave 0 |
| SC2 | Sub-resolution request (< 0.001) cuts nothing, `end_chamfer_effective` is `None`, warning present | calc | `pytest tests/test_shaft_calc.py -k chamfer -q -n0 --no-cov` | no, Wave 0 |
| SC2 | Defect guards: pre-build near-root offset (1e-7..1e-4) and post-build bracket raise `BuildError` naming a modelling defect; each seen red once by monkeypatching the cut | kernel | `-k guard` | no, Wave 0 |
| SC2 | Small-z (`rb > rf`: m 2 z 6; m 1 z 8 x -0.05) and z 82 rows build and match | kernel | `-k small_z -k z82` | no, Wave 0 |
| REQ-shaft-solid | `Part` widening: `mypy --strict` clean; `model.build(ShaftParams())` and `pool.build_export` return bytes; shaft and gear share the cache without eviction surprises (4 entries) | typecheck + pool | `make typecheck`; `pytest tests/test_pool.py -k shaft -q -n0 --no-cov` | partly (test_pool exists) |
| Seam | `ignore_imports` appears in the same commit as the static import; contracts `10 kept, 0 broken`; `test_only_model_may_import_the_shaft_solid` still passes; `shaft_model` imports no `spur.model` | lint + belt | `make lint-imports`; `pytest tests/test_seam.py -q -n0 --no-cov` | yes |
| Keys | `ShaftDimensions` has 13 keys, new key in the chosen position; warnings tuple pins updated (`tests/test_shaft_calc.py:67,100`) | unit | `pytest tests/test_shaft_calc.py -q -n0 --no-cov` | yes (edit) |
| REQ-shaft-build-measured / SC3 | Bounds pinned; sweep rows recorded in `bench/RESULTS.md` with host, command, load; margin vs 30 s and vs L17 stated | bench + pin | `make bench.build SWEEP=bench/sweeps/shaft.json`; `pytest tests/test_shaft_params.py -k bound -q -n0 --no-cov` | pin exists; sweep file no |
| SC4 | Gate delta: `make verify` result line before and after, same host, load recorded in `bench/RESULTS.md`; `make gear.unchanged` green; `git diff --exit-code v0.6 -- tests/regression/ .github/workflows/ci.yml` empty | gate | `/usr/bin/time -p make verify`; `make gear.unchanged` | yes |

### Sampling Rate
- **Per task commit:** the quick command above (kernel rows are 0.3-2.4 s each; the commit slice must stay under L36's 30 s - measure with `make verify.fast`).
- **Per wave merge:** `make verify` is 4 minutes; run the full file `-n 8` plus `make lint-imports typecheck`.
- **Phase gate:** full `make verify` green with its result line recorded, `make gear.unchanged`, the `git diff --exit-code v0.6 -- tests/regression/ .github/workflows/ci.yml` check.

### Wave 0 Gaps
- [ ] `tests/test_shaft_model.py` - all kernel rows above; each guard test seen red once with a log under `investigation/` and a row in `bench/RESULTS.md` (the Phase 30/31 pattern).
- [ ] `tests/shaft_oracle.py` - `tooth_half_angle`, `profile_area_within`, section/chamfer volume; extend `test_the_shaft_oracle_imports_nothing_from_spur` coverage unchanged.
- [ ] `bench/sweeps/shaft.json` and a part switch in `bench/build_time.py` (`load_sweep` builds `GearParams`; `time_set` is already part-agnostic) plus an RSS column; `tests/test_bench.py` row for the new loader.
- [ ] Decide whether `tests/test_shaft_model.py` joins `HEAVY_TEST_FILES` (Pitfall 8).
- [ ] Framework install: none.

## Security Domain

`security_enforcement` is not set in `.planning/config.json`, so it is treated as enabled.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | none in this project |
| V3 Session Management | no | none |
| V4 Access Control | no | none |
| V5 Input Validation | yes | pydantic bounds on `ShaftParams` (finite floats, inclusive `ge/le`, `_feasible` shift range); defect guards in `shaft_model` for kernel-boundary values |
| V6 Cryptography | no | none |
| V12 Resource / DoS (ASVS 12 files and resources, 11 business logic) | yes | `SPUR_BUILD_TIMEOUT` 30 s with worker termination (L37), `BUILD_QUEUE` admission, bounded `_EXPORTS` and solid caches; the field bounds from this sweep |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Request that wedges the kernel (cone start 3e-7 from the root circle) | Denial of service | Values on the 0.001 lattice by construction; pre-build `BuildError` for off-lattice near-coincidence; server timeout kills the worker; CLI has no timeout, so the guard matters there |
| Request that yields a wrong or empty solid with `isValid()` true | Tampering (silent wrong part) | Round caps down; post-build volume/bbox bracket; `len(Solids()) == 1`; closed-form tests |
| Unbounded geometry size (shank 850 x 500, Ls 500) | Denial of service | Bounds swept: worst build 2.2 s macOS, 5.4 s loaded Linux, STL <= 3.3 MB, RSS equal to the 199-tooth gear |
| Float strings (`nan`, `inf`, `1e400`) | Tampering | Already refused by `ShaftParams` (`tests/test_shaft_params.py:117-125`) |
| Path or stem injection through the download name | Tampering | `_write_export` writes into a `TemporaryDirectory` with a stem from `slug()`; keep `slug()` built from numbers only |

## Project Constraints (from CLAUDE.md)

- Python 3.12 only; CadQuery/OpenCascade for the solid; FastAPI + Pydantic v2; argparse; pytest; the runtime needs no Node.
- `make verify` is the gate (ruff, mypy `--strict`, import contracts, unfinished-work scan, pytest). State the command and the result line; do not predict. `make check` adds the Docker checks.
- Stop and ask first for: an architectural claim not in the decision log, a locked decision that looks wrong, an unverified library behaviour, conflicting evidence, a destructive operation, a stability-for-speed trade. This research raises three for the plan: the round-down rule (Pitfall 3, no logged decision names it), the `end_chamfer_effective` key position and `slug()` stem (Open Question 3), and the unsourced 221.86 s baseline (Pitfall 10).
- New non-trivial choices get 2-3 options and an `Lxx`. Phase 32 owes L47 amendments for the 13th key and the solid-field bounds (D-06, D-10).
- Two standing rules: a printed number is a number someone cuts metal to (an uncomputable value is a warning and no number, L08); a parameter the user did not set must never silently change the part (L05; a cap is warned, a direct conflict is 422, L03).
- Keep it small: surgical edits, one concern per commit, new behaviour ships with its tests. No `TODO`, `pass` or unreachable branches (`make verify` greps for markers: the unfinished-work scan also reads docstrings, 30-RESEARCH Pitfall 5).
- Measurements are measured and recorded (host, command, load), not estimated; `bench/RESULTS.md` is where they live; each guard test is seen red once.
- Comments carry the measurement or constraint that forced the choice. `calc.py` never imports `cadquery`; vendor types stop at `model.py` / `shaft_model.py`; a parameter is validated once at its boundary.
- English throughout. Capture non-blocking work in `docs/ideas/` or `docs/tech_debt/active/` (blocker: fix or stop), one file per item with an INDEX row; state at the end whether anything was filed.
- Tech debt to resolve in this phase: `docs/tech_debt/active/2026-10-23-parts-one-line-widening-claim-is-false.md` (git mv to `resolved/`, INDEX row, commit sha, same commit as the fix).

## Sources

### Primary (HIGH confidence)
- Repo files read this session: `src/spur/model.py` (whole), `pool.py` (whole), `parts.py`, `records.py:150-209`, `shaft_calc.py`, `shaft_params.py`, `din5480.py`, `shaft_model.py`, `app.py:233-501` (selected), `pyproject.toml:122-275`, `Makefile:113-260`, `tests/shaft_oracle.py`, `tests/test_seam.py:1-120`, `tests/test_hooks.py:39,135-172`, `tests/test_shaft_params.py:93-125`, `tests/test_shaft_calc.py:78-100`, `tests/test_model.py:636-700,1940-2060`, `bench/build_time.py:60-200`.
- `docs/architecture/decision_log.md` L17, L28, L29, L37, L45, L46, L47 (read in full or by section).
- `.planning/research/PITFALLS.md` Pitfall 13, 14, 15; `.planning/research/ARCHITECTURE.md` F3, F4 and the module and dependency tables; `.planning/phases/30-*/30-RESEARCH.md` Pitfall 4; `bench/RESULTS.md` Phase 30 and 31 gate sections.
- Kernel measurements, all with scripts and logs in `.planning/phases/32-the-shaft-solid/investigation/`: `32-spike.py` (construction + oracle), `32-battery.log`, `32-negatives2.log`, `32-readback.log`, `32-tiny.log`, `32-nearcap.log`, `32-windows-*.log`, `32-cap-sweep-*.log`, `32-round-up.log`, `32-flank-dev.log`, `32-stl-volume.log`, `32-sweep.log`, `32-sweep-linux.log`, `32-linux-gear2.log`, `32-c-time.log`, `32-scan.py`.
- `inspect.signature` of `cq.Solid.revolve`, `cq.Shape.fuse`, `cq.Shape.intersect`, `cq.Solid.makeCone/makeCylinder/extrudeLinear`, `cq.Shape.exportStl` in `.venv` (cadquery 2.8.0).

### Secondary (MEDIUM confidence)
- Linux container timings (host load 30-46, Docker VM 16 GB): memory valid, times inflated.

### Tertiary (LOW confidence)
- OCCT `glue` semantics (training knowledge, A1).

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - no new dependency; versions read from the venv and the pinned closure.
- Architecture: HIGH - construction built and measured; dispatch and contract handoffs read from source; `pool._warm` finding follows from reading `pool.py:41-50` and the static import.
- Pitfalls: HIGH for the five reproduced (`.clean()`, root hang, round-up empty shape, sub-resolution chamfer, cap past tooth height); MEDIUM for the claim that hang points are only the one found (A3).
- Bounds sweep: HIGH for validity, volume, memory and STL size; MEDIUM for times (load 4-46).

**Research date:** 2026-10-27
**Valid until:** 2026-11-26 for the kernel facts (cadquery 2.8.0 and cadquery-ocp 7.9.3.1.1 are pinned; any move of that pair invalidates the hang, window and timing results and needs a re-run of `32-cap-sweep.py`).
