# Technology Stack

**Project:** spur v0.7 "Splined Shaft" (DIN 5480 external splined shaft, second part type)
**Researched:** 2026-10-23
**Scope:** only what the NEW feature needs. The involute maths (`calc.py`), the solid build (`model.py`), STL/STEP export, the `BuildPool`, the schema-driven form and the golden-link fixture are validated and not re-researched.
**Overall confidence:** HIGH on "add nothing" and on the CadQuery recipe (both measured in this repo's `.venv`, Python 3.12.15, cadquery 2.8.0, cadquery-ocp 7.9.3.1.1). LOW on any statement about DIN 5480 content or about third-party tools (web search only, no licensed copy read; see the marked ASSUMPTIONs).

## Verdict

**Add no runtime dependency. Add no dev dependency.** `requirements.txt` stays byte-identical (31 pinned packages, unchanged since v0). Everything the feature needs is stdlib `math` and `re`, the already-pinned `pydantic`, and the already-pinned `cadquery`. The one piece the question worried about (inverting `inv(alpha)` for measurement over pins) is already solved in the tree.

## Recommended Stack

### Core (all existing, versions as pinned in `requirements.txt` and read from the venv)

| Technology | Version | Purpose for v0.7 | Why |
|------------|---------|------------------|-----|
| Python | 3.12.x only | Everything | L23. No change. |
| stdlib `math` | -- | d_B, d_a, d_f, tooth thickness, M_Re, `inv()` | `calc.py` is stdlib-only and import-linter forbids the kernel; the shaft's maths must live in the same kind of module (see Integration). |
| stdlib `re` | -- | Parse `W 25x1.25x18x8f` | One anchored regex. No parsing library is warranted for a four-field grammar. |
| Pydantic | 2.13.5 | A sibling frozen model for the shaft (validated once at its boundary) | Already the one validation boundary (L02, CLAUDE.md "validated once"). A second `BaseModel` with the same `Field`/`json_schema_extra` pattern drives `/api/schema`, the CLI flags and the cache key exactly as `GearParams` does. |
| CadQuery | 2.8.0 | Splined prism + shank + end chamfer | Same kernel the gear uses; the recipe below was measured here. |
| cadquery-ocp | 7.9.3.1.1 | (under CadQuery) | No new OCP imports are needed; do not reach for `OCP.*` directly (vendor types stop at the `model.py` boundary). |

### Database / Infrastructure

None. No change to `Dockerfile`, `compose.yaml`, `ci.yml` or `docker/refresh-requirements.sh`. (`tests/regression/` and `ci.yml` byte-identical to the tag is a v0.6 rule worth keeping.)

### Supporting libraries

| Library | Version | Purpose | When to use |
|---------|---------|---------|-------------|
| none | -- | -- | -- |

## Question 1: inverting inv(alpha) for measurement over pins -- reuse `calc._involute_angle`

**Do not add scipy. Do not write a Newton loop. Reuse the bisection that is already in `calc.py`.**

`calc._involute_angle(target)` (calc.py:1327) is a 60-halving bisection on (1e-12, 89 deg), written under L08 precisely because an unguarded Newton loop "returned confident garbage for 138 parameter sets". Measured on this machine (2026-10-23, 20,000 random angles in 5-70 deg, round trip `alpha -> inv -> _involute_angle`):

| Quantity | Reading |
|----------|---------|
| Worst absolute angle error | 2.9e-15 rad |
| Cost | 2.8 microseconds per call |
| Error at 1, 5, 30, 60, 85 deg | 2.4e-15, 2.1e-15, 3.3e-16, 2.2e-16, 0 rad |

That is full double precision, orders of magnitude inside any tolerance a printed M_Re needs (microns). Newton would be faster in iteration count but buys nothing at 2.8 microseconds and re-opens the exact failure L08 closed.

Why not scipy: `scipy` 1.18.1 happens to be installed in the dev `.venv`, but it is **not in `requirements.txt`**, and `docker/refresh-requirements.sh` line 19 names it among the packages it deliberately prunes from the image. A `src/` import of it would pass `make verify` locally and fail in the container. Do not import it in `src/`, `tests/` or `bench/` either: it is not declared in `[project.optional-dependencies].dev`, so CI would fail on it too.

Integration notes (design inputs, not new stack):

- **Guard the domain, as `centre_distance` does.** The target `inv(alpha_Re)` has no solution when it is `<= 0` or `>= inv(89 deg)`; the function's bracket would silently return an end of the bracket for an out-of-range target. Copy `centre_distance`'s `if not 0 < target < inv(radians(89)): return None` pattern, and let `None` mean "warning, no number" (L08).
- **The closed form is textbook; the inversion is the only iterative step.** ASSUMPTION (derived by hand from involute geometry, cross-checked against the standard external-gear over-pins formula, NOT yet read from DIN 5480-1 or -15; confirm against the human's copy): with `d_b = d_B cos(alpha_P)`, `alpha_P = 30 deg`, tooth thickness `s` on the reference circle, pin diameter `D_Re`: `inv(alpha_Re) = inv(alpha_P) + D_Re/d_b - (pi/z - s/d_B)`; `M_Re = d_b/cos(alpha_Re) + D_Re` for even z, `M_Re = d_b*cos(pi/(2z))/cos(alpha_Re) + D_Re` for odd z. Also warn (no number) when the pin's contact point falls outside the usable involute (below the form diameter or above the tip diameter), tangent contact at `tan(alpha_k) = tan(alpha_Re) - D_Re/d_b`.
- **The pin diameter D_Re is a standard-supplied value (ASSUMPTION: tabulated by module in the standard). It is a table value. Do not invent it;** it comes from the human's copy with a clause/table citation like every other table value.
- Promote `_involute_angle` from underscore-private only if the shaft module imports it from another module; ruff's selected rules do not flag a cross-module private import, so leaving it and importing it is the smaller diff. Either is a surgical edit; the choice is the planner's.

## Question 2: open-source DIN 5480 / ISO 4156 calculators as a test oracle -- none is usable; build the oracle in-repo

Searched 2026-10-23 (GitHub API repository search for `DIN 5480`, `din5480`, "involute spline", README search; PyPI JSON probes for `din5480`, `din-5480`, `involute-spline`, `cq_gears`; web search). Findings, all **LOW confidence** (single-source web/GitHub reads, no `--verified` cross-check available):

| Candidate | Standard | License | Measurement over pins | Verdict |
|-----------|----------|---------|-----------------------|---------|
| `ivanokhotnikov/splines` (Python; last push 2023-06-16; 0 stars) | ISO 4156-1/-2 and ANSI B92, **not DIN 5480** | **None stated** (GitHub API: no license) | not documented | Reject. No license means all rights reserved: cannot be vendored, copied from, or relied on as a committed test oracle. Wrong standard's tables anyway. |
| `Iv/DIN_5480_ezdxf` (Python 3.10+; last push 2026-05-26; 0 stars) | DIN 5480 external W profile, 2D DXF | MIT per README (GitHub API lists none) | **No** (README says so) | Reject. Geometry only; README says it was "verified visually" against a third-party calculator and "not a certified manufacturing calculation tool". |
| `NeoTech/Fusion360-Splinegenerator` (Python; last push 2026-09-29; 0 stars) | DIN 5480 (module-driven, 30 deg), ANSI B92.1, SAE/DIN 9611 | MIT | not documented | Reject as an oracle: no M_Re, no tests tied to the standard, Fusion-360-API project (its `core/` maths is separable but unvalidated against the standard). Low-maturity, recent, unverified: do not trust its tables or constants. |
| `kevenyay1/DIN-Gear-Generator` | DIN 5480-1 DXF | none | not documented | Reject (no license). |
| Hexagon WN5/WN10/WNXE, frenco, KISSsoft | DIN 5480 / ISO 4156 | Commercial | Yes | Not a dependency. Usable only as a **manual anchor** (below). |
| "DIN 5480 Spline Calc: Online Tool" pages (appbase.io, ekuep.com, codeless.io mirrors) | -- | -- | -- | Search-engine spam duplicates; ignore. |

No PyPI package for DIN 5480 exists (the `din5480`, `din-5480`, `involute-spline` names return 404; `splines` on PyPI is an unrelated curve library). `cq_warehouse`-style libraries do not ship DIN 5480.

**Recommendation: follow the repo's own oracle precedent, which already works.** `tests/trochoid_oracle.py` is a plain-float, stdlib-only file with no `test_` prefix that "imports nothing from `spur`", rebuilt from textbook definitions so "a wrong sign, side or root in `spur.calc` disagrees with it instead of moving both sides together" (L08). Do the same for M_Re, in three independent layers, none needing a dependency:

1. **Geometric pin oracle (new file, e.g. `tests/spline_oracle.py`, stdlib only, no `spur` imports).** Seat a pin of diameter D_Re in a gap by bisection on its centre radius until its distance to the left and right flank polylines equals D/2, sampled from the involute parametric equations written out again in the oracle (not from `calc.profile`). Then `M = 2*R_centre + D` (even z) or the cos(pi/2z) form (odd z). This shares only the tooth thickness input with the code under test, not the over-pins closed form or the `inv` inversion.
2. **Kernel pin oracle (optional, `bench/` or a marked slow test).** Build the splined solid, place a pin cylinder in opposite gaps, and measure with the built solid's own geometry (`Shape.distance`/bounding box in `model.py`-adjacent test code). This proves the printed M_Re against the *built part*, the same standard as the trochoid root's "built root reads within 2e-3 x module of the independent oracle". ASSUMPTION: needs a spike to confirm `cq.Shape.distance` exists and is fast enough at 18 teeth; not run.
3. **Human-supplied anchors (the T4 KISSsoft precedent).** Ask the human for 2-3 rows of tooth thickness / d_a / d_f / M_Re from the licensed standard's own tables or a vendor calculator they own (KISSsoft, WN), for 2-3 sizes including one odd z. Assert agreement to the table's printed precision. These are the only layer that proves the *standard's* conventions rather than the maths; layers 1-2 prove internal consistency. Mark the source and clause on each row; no value ships uncited.

## Question 3: CadQuery operations for the splined prism, shank and end chamfer (measured)

All timings: this repo's `.venv`, CadQuery 2.8.0, macOS arm64, 2026-10-23, single run each. **The tooth proportions in the spike were illustrative placeholders (ra = r + 0.45 m, rf = r - 0.7 m, s = 0.49 pi m, root fillet 0.2 m), not DIN 5480 values.** They prove the kernel behaviour, not the standard. Real DIN dimensions come from the human's copy.

### Recipe

1. **Outline: reuse `model._outline(pr, fillet)` unchanged.** It takes a `calc.Profile` (z, m, alpha, r, rb, ra, rf, psi_p), not `GearParams`. A shaft builds a `Profile` with `alpha = 30 deg` and its own `ra`/`rf`/`psi_p` from the standard; `_outline` already produces involute flanks as `makeSpline`, the tip arc, the root arc and the analytic root fillet. Measured: 4.0 ms at z=18, 12 ms at z=40, 28 ms at z=82, 36 ms at z=100. No new outline code is needed for the radial (non-trochoid) root. (The hob-root path, `_trochoid_outline`, is wired to `GearParams` through `cutter(p, rho)` and `root_mode`; whether DIN 5480's root form needs it is an architecture question, flagged below.)
2. **Prism:** `cq.Solid.extrudeLinear(cq.Face.makeFromWires(wire), cq.Vector(0, 0, L))`, the gear's own call. 1.5-5.7 ms.
3. **Shank:** `cq.Solid.makeCylinder(R, S, cq.Vector(0, 0, -S), cq.Vector(0, 0, 1))`.
4. **Join: `prism.fuse(shank)` at the `Shape` level. Never `Workplane.union()` and never `.clean()` afterwards.** Measured, with the common case shank diameter == tip diameter (coincident cylindrical surfaces):

   | z (m) | plain `fuse` | `fuse` then `.clean()` | `fuse(glue=True)` |
   |-------|--------------|-------------------------|--------------------|
   | 18 (1.25) | valid, 215 ms | **invalid** | valid, 39 ms |
   | 40 (1.25) | valid, 529 ms | **invalid** | valid, 86 ms |
   | 82 (1.0) | valid, 1387 ms | **invalid** | valid, 192 ms |

   `Workplane.union(clean=True)` is CadQuery's default and runs `.clean()` (UnifySameDomain), which produced `isValid() == False` in every row where the shank diameter equals the tip diameter. This is the single most likely silent failure of the feature, because a shank equal to the nominal (tip) diameter is the ordinary design. Use `Shape.fuse`. `glue=True` (OCCT `BOPAlgo_GlueShift`, sound only when the two solids touch on a shared planar face and do not overlap) is 5-7x faster and valid here, but plain `fuse` already fits the 30 s `SPUR_BUILD_TIMEOUT` by a wide margin; adopt `glue` only if a measured worst case needs it, and then only with the prism and shank meeting at a plane. Shank radius above, below or at the tip, or below the root, all built valid with plain `fuse`.
5. **End chamfer: intersect with a revolved envelope; do not chamfer the tip-arc edges.** Measured at z=18, chamfer c measured from the tip:

   | c (mm) | 3D `Solid.chamfer` on the end-face tip arcs | `intersect` with revolved cone envelope |
   |--------|----------------------------------------------|------------------------------------------|
   | 0.5 | valid, volume 14384.6306 | valid, volume 14384.6306 (agree to 2.4e-8 mm3 at z=18; 1.3e-8 to 1.5e-7 mm3 at z=40..100) |
   | 1.4 | **invalid**, volume 12144.25 (wrong) | valid, 14356.26 |
   | 2.0 | **invalid**, volume 13988.46 (wrong) | valid, 14314.69 |

   The edge chamfer is correct only while c stays within the tip land (it is the gear's `tip_chamfer` mechanism, L29, which caps c at the tip land); a shaft's end chamfer is a lathe cone that cuts through the whole tooth, so c exceeds the tooth height routinely. The envelope form stays valid and is the physically right operation. Cost: 360 ms at z=18, 630 ms at z=40, 1.37 s at z=82, 1.69 s at z=100 (edge chamfer: 96 ms, 252 ms, 791 ms, 1065 ms). Build the envelope in the `XZ` workplane (local y is global Z) and revolve about local Y:

   ```python
   env = (cq.Workplane("XZ")
          .polyline([(0, -S - 1), (ra + 1, -S - 1), (ra + 1, L - (c + 1)),
                     (ra - c, L), (0, L)])      # 45 deg cone; use the standard's angle
          .close().revolve(360, (0, 0, 0), (0, 1, 0))).val()
   shaft = prism_and_shank.intersect(env)
   ```
   Use the 3D edge chamfer as an *independent test cross-check* of the cone for c within the tip land (the two agreed to better than 2e-7 mm3), the same "second route to the same number" pattern as `_filleted_spoke_volume`.
6. **Validity guard stays the existing one.** `_build`'s `len(solids) != 1 or not solids[0].isValid()` is what caught the invalid cases above; the shaft's build must keep an equivalent, and a sibling must not skip it. Also in the spike: an over-thick outline (placeholder proportions with ra = r + m, rf = r - 1.3 m) made `makeFromWires` + extrude produce an **invalid prism** at z=40 and z=82 (root gap narrower than twice the root fillet, so adjacent fillet arcs overlap). That is a refusal/cap case for the validation layer (L03), not something the kernel reports as an error.

## Integration points (what changes, no new library)

| Integration point | Fact | Consequence |
|-------------------|------|-------------|
| `calc.py` stays stdlib-only | import-linter contract forbids `cadquery`/`OCP`/`logging` in `spur.calc` | Shaft maths goes in a sibling pure module (e.g. `spline.py`) added to the same `source_modules` list in `pyproject.toml`. This is a config line, not a dependency. |
| `model.py` is the only kernel importer | contract; `cadquery` objects do not escape it | Shaft solid build lives in `model.py` (or a second kernel module added to the same allow rule). `_outline`, `_body`, `_shape_of`, `_write_export` are reusable. |
| Parameter model | `GearParams` is frozen/hashable; `_build_cached = lru_cache(...)` keys on it; `pool.build_export`, `BuildPool.executor_for/_run_with_timeout`, `app.py` `BuildBackend`, `_gear()`, `/api/schema` and `/api/info` are typed to `GearParams` | A sibling `ShaftParams` model is cheap in Pydantic, but these call sites need a part-type dispatch (a union or a small protocol). That is an architecture decision for the roadmap, not a dependency. Flag for ARCHITECTURE.md. |
| Designation parse/print | stdlib `re`, pure function | Accept `.` and `,` decimals, `x` and the multiplication sign, optional `DIN 5480` prefix and surrounding whitespace (ASSUMPTION: the standard prints a decimal comma in German text; verify against the copy); print one canonical form with a dot. Test round trip as a property over the table's valid rows. |
| Fixture rule | `tests/regression/pre_v0_2.json` byte-identical to `v0.6` (L26); `requirements.txt` byte-identical | Adding no dependency makes the second half free. |
| Vendored viewer | STL goes through the same `exportStl` path | No viewer change expected for a shaft; ASSUMPTION: the existing `/api/model.stl` consumer handles any solid. Not tested. |

## Alternatives Considered

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| `inv(alpha)` inversion | Existing 60-step bisection (`calc._involute_angle`) | `scipy.optimize.brentq`/`newton` | scipy is pruned from the image and absent from the pinned closure; the existing routine is already 2.9e-15 rad accurate and was written under L08 specifically to avoid Newton's failure mode. |
| `inv(alpha)` inversion | Existing bisection | Series/closed-form approximation of the inverse involute | Approximations carry 1e-4..1e-6 rad error; M_Re is a number someone cuts metal to (L08). The exact bisection costs 2.8 microseconds. |
| Test oracle | In-repo stdlib oracle + human-supplied anchors | `ivanokhotnikov/splines`, `Iv/DIN_5480_ezdxf`, `NeoTech/Fusion360-Splinegenerator` | No license / wrong standard / no M_Re / unvalidated; none ships standard test vectors. |
| Join | `Shape.fuse` (no `.clean()`) | `Workplane.union` | `union` cleans by default, which invalidated the solid in every coincident-diameter row measured. |
| End chamfer | Revolved-envelope `intersect` | `Solid.chamfer` on tip-arc edges | Invalid solid with a wrong volume once c exceeds the tooth height, without raising. |
| Designation parsing | `re` | `lark`, `pyparsing` | Four-field grammar. (`pyparsing` is in the closure only as a transitive dependency; importing it from `src/` would make an undeclared direct use.) |
| Part-type model | Sibling `ShaftParams` Pydantic model | New fields on `GearParams` | Out of scope per the milestone rules: no new `GearParams` field (L05/L26). |
| Geometry engine | CadQuery 2.8.0 as pinned | build123d | Would change the kernel wrapper under a 17,664-line suite; migration is out of scope (L01). |

## What NOT to Add

- **scipy, numpy (as a direct import), sympy, mpmath, shapely:** none is needed; `numpy` is in the closure only as a CadQuery transitive and `casadi`/`nlopt`/`vtk` likewise. Do not import any of them from `src/`.
- **Any third-party DIN 5480 / ISO 4156 package or vendored third-party code:** none is licensed for it (above), and the human's licensed copy is the only authority on tables (L08).
- **A table or lookup library (pandas, a YAML/CSV loader):** the transcribed fit tables are a small, cited Python literal (or a JSON checked in beside it) read by stdlib; every row carries its clause/table citation and a second-read check. `PyYAML` is in the closure transitively; do not take a direct dependency on it for this.
- **Node/JS tooling changes:** the viewer bundle and `web/` are untouched.

## Installation

```bash
# Nothing to install. requirements.txt and pyproject.toml dependencies are unchanged.
make verify   # the gate; state the command and result line in the reply
```

## Gaps / ASSUMPTIONs to settle at discuss-phase or phase research

1. **DIN 5480 formulas and conventions are not read from the standard.** Every formula above that mentions DIN content is textbook-derived or recalled, flagged ASSUMPTION. The tables phase is blocked on the human's copy (milestone rule); the over-pins formula, the pin-diameter table, the root-form radius, the tip/root diameter rules and the designation grammar must each be confirmed against a cited clause before they ship.
2. **Does DIN 5480's external root form need the trochoid machinery?** `_outline` (radial root + analytic fillet) was exercised here; the v0.4 hob-root path (`cutter`, `root_mode`) is `GearParams`-coupled. Which one the shaft needs is decided by the standard's root form, then by an architecture call on whether to generalise `cutter()` to accept a bare `Profile`. Not researched here.
3. **Kernel pin oracle** (layer 2 above) needs a small spike.
4. **Build-time ceiling for the shaft** was measured at up to z=100 (about 1.7 s worst) with placeholder proportions and without a shank-side undercut, a spline run-out or a fillet at the shoulder; re-measure with real DIN rows before committing a cap (CLAUDE.md: performance claims are measured, not estimated).
5. Third-party tool findings (Section "Question 2") come from web search and the GitHub API at a single point in time; confidence LOW, not cross-verified.

## Sources

- Local measurements (HIGH, reproducible): `.venv` Python 3.12.15, cadquery 2.8.0, cadquery-ocp 7.9.3.1.1, pydantic 2.13.5, fastapi 0.141.1; `inspect.getsource(cq.Shape.fuse)` (signature `fuse(*toFuse, glue=False, tol=None)`; `glue` sets `BOPAlgo_GlueShift`); spike scripts run in the session scratchpad against `spur.model._outline` and `spur.calc.Profile`.
- Repo: `/Users/half/git/halfb00t/spur/src/spur/calc.py` (`inv`, `_involute_angle`, `_bisect`, `centre_distance`), `src/spur/model.py` (`_outline`, `_build`, `_tip_edges`, `_write_export`), `pyproject.toml` (import-linter contracts, dev extras), `requirements.txt`, `docker/refresh-requirements.sh:19` (scipy pruned), `tests/trochoid_oracle.py` (oracle precedent), `docs/architecture/decision_log.md` L05, L08, L23, L26, L29.
- GitHub (LOW; fetched 2026-10-23): https://github.com/ivanokhotnikov/splines (no license; ISO 4156/ANSI B92), https://github.com/Iv/DIN_5480_ezdxf, https://github.com/NeoTech/Fusion360-Splinegenerator, https://github.com/kevenyay1/DIN-Gear-Generator; GitHub REST API repository search.
- Vendor pages (LOW, commercial, not fetchable as text): https://www.hexagon.de/pdf/wn10_e.pdf, https://www.hexagon.de/pdf/wnxe_e.pdf, https://www.hexagon.de/pdf/wn5_e.pdf (confirm the products compute DIN 5480 dimension over pins; no numbers extracted).
