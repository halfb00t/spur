# Phase 7: Foundation — Generalized Edge Selection + Regression Fixture - Context

**Gathered:** 2026-09-26
**Status:** Ready for planning

<domain>
## Phase Boundary

Two pieces of foundation, no user-facing feature. Every later v0.2 phase builds on both.

1. **Generalized bore-rim edge selection.** `calc.bore_rim_limit(p)` — pure maths — returns
   the farthest any point on the bore's rim can sit from the axis, per bore shape (round and
   D-flat today: `bore_radius(p)`; shaped so Phase 8 adds the hex circumradius and Phase 9
   decides the keyway). `model._bore_rim_edges` uses it instead of the inline
   `lim = r_bore + 0.01` (`src/spur/model.py:221`). Both position-based selectors —
   `_bore_rim_edges` (bore chamfer) and `_groove_floor_edges` (recess-floor fillet) — raise a
   `BuildError` when they match zero edges while their feature is on, instead of handing
   `.chamfer()`/`.fillet()` an empty list (a silent no-op in cadquery, research Q2). Unit
   tests assert the exact selected-edge count per shape, with and without recesses.
2. **The L05 regression fixture.** A checked-in JSON file pins, for every pre-v0.2 parameter
   set (the defaults, every hand-written parameter set in `tests/`, the README's examples):
   `derive()`'s 19 fields exactly, `build()`'s volume, six bounding-box corners, and face and
   edge counts. Captured at HEAD by a script behind a `make` target, replayed by one
   parametrized pytest case per record. Phases 8–12 re-run it unmodified; a red fixture in
   a later phase is a bug in that phase.
3. `make verify` green with both, and the fixture's measured cost recorded.

Requirements: REQ-defaults-off-regression, REQ-edge-selection-proven.

**Not in scope:** any new `GearParams` field or bore shape (hex is Phase 8, keyway Phase 9);
changing any `derive()` value or warning sentence (the fixture pins them as they are);
redesigning the selectors around positive identification (deferred); `docker/smoke.py` and
`bench/corpus.py` parameter sets; machine-generated parameter grids; export-byte comparison
(L24 rules it out).

</domain>

<decisions>
## Implementation Decisions

### Regression fixture — storage and regeneration
- **D-01:** The captured numbers live in a **checked-in JSON data file** (e.g.
  `tests/regression/pre_v0_2.json`; name and directory are the planner's). One record per
  parameter set. Rejected: Python literals in the test module (~1000 hand-aligned lines
  under L16); a generated Python module (machine-written source under mypy `--strict`).
- **D-02:** Regeneration is a **`make` target running a script** (e.g. `make fixture.regen`).
  The same script performs the first-time capture in this phase. Rejected: a pytest
  option/env flag (a test that rewrites its own oracle is one typo away from running under
  `make verify`); capture-by-hand with no tool.
- **D-03:** **Regeneration policy for v0.2:** the JSON changes only in **its own commit**
  whose message states what moved and why — a `cadquery`/`cadquery-ocp` pin bump under L12,
  or a deliberate contract change carrying a new `Lxx`. A feature commit never touches it.
  A red fixture in Phases 8–12 is, by definition, a bug in that phase. Rejected: frozen for
  the whole milestone (a routine pin refresh would block on it); regenerate whenever red
  (the oracle becomes a mirror of HEAD — recorded as rejected).
- **D-04:** A record stores **only the fields its source set**, exactly as written
  (`{"teeth": 24, "module": 1, ...}`), so a record *is* a shareable link that omits fields
  and the fixture proves the defaults too (L05). A **file-level provenance header** records
  the git sha, `cadquery` and `cadquery-ocp` versions, and the capture date (Pitfall 11:
  which kernel produced these numbers). Rejected: fully expanded params (a drifted default
  would rebuild the same part unnoticed here).

### Regression fixture — corpus and cost
- **D-05:** The corpus is a **hand-listed module with a source tag per entry** (e.g.
  `tests/regression/corpus.py`, tags like `test_model.py::test_builds_one_valid_solid[8]`,
  `README:curl`), deduplicated by `GearParams` equality (frozen, hashable). "Pre-v0.2" is a
  closed set — it never tracks later test edits. The regen script and the test both import
  it. Rejected: harvesting by instrumenting `GearParams` during a suite run (hidden,
  order-dependent, captures throwaway instances); importing the source tests' parametrize
  lists (the oracle would move with a test refactor).
- **D-06:** **Build every set.** `derive()` for all is microseconds; the `build()` side is
  the cost, unknown until measured: the plan measures the delta to `make verify`
  (32.47 s, 191 tests at `b3ca789`) and records it. If the delta exceeds **~15 s** the
  planner comes back with a trim proposal rather than silently subsetting. Rejected: a
  curated build subset (the milestone's Success Metric 3 says *every* pre-v0.2 set); a
  CI-only marker (`make verify` would stop meaning one thing everywhere, L13).
- **D-07:** Sets that appear **with a mate** (README `spur info --teeth 19 --mate-teeth 40`,
  `tests/test_cli.py` teeth 21 + mate 40, `tests/test_calc.py`'s impossible pairs) get
  **their own records** with `derive(p, mate_teeth)`: `mate_teeth` and `centre_distance`
  pinned, including the cannot-mesh `null` + warning cases. The solid is shared, so no extra
  `build()`.
- **D-08:** Sources are **`tests/` and `README.md` only**. `docker/smoke.py` (a `make check`
  container check) and `bench/corpus.py` (40 gears at 160–199 teeth, minutes of builds) stay
  out.
- **D-09:** **Hand-written sets only.** Literal kwargs/dicts in tests — parametrize lists,
  inline `GearParams(...)`, `TestClient` `params=`, `cli.main([...])` argument lists — and
  the README's four examples. Machine-generated grids are excluded; concretely
  `tests/test_calc.py::test_centre_distance_matches_an_independent_solver`'s
  teeth × pressure-angle × shift loop (~100 sets, ~20 at 200 teeth, 2.3 s per build,
  measured 2026-09-26) is a solver cross-check with its own oracle, not a shareable link.
  Sets that fail validation (the 422 cases) cannot enter by construction.

### Regression fixture — what "unchanged" means
- **D-10:** `DerivedDimensions`: **exact equality on all 19 fields, warnings text
  included.** `derive()` is Python-computed and rounded to 3 dp at construction (Phase 4
  D-10), so exact is honest; the warning sentences are the product (L15) — a reworded
  warning is a contract change and must show up as a red fixture and a D-03 regeneration.
- **D-11:** `build().Volume()`: **`pytest.approx(rel=1e-6)`.** `Volume()` read identical
  (max diff 0.0) over three independent builds of `GearParams()` on the pinned kernel
  (2026-09-26 probe; L24 measured the same for decoded STL volume). The default 0.4 mm bore
  chamfer is 1.05e-3 of the volume and the 0.5 mm recess fillets 2.9e-3 (measured
  2026-09-26), so `rel=1e-3` — `test_recess_removes_expected_volume`'s tolerance, chosen
  there against an analytic ring — would let a vanished chamfer through; recorded as
  rejected. Exact float equality rejected as brittleness without gain.
- **D-12:** Bounding box: **six corner values** (`xmin/xmax/ymin/ymax/zmin/zmax`),
  **`abs=1e-6`** each. OCCT enlarges the box by its tolerance (`z[-1e-7, 7.5000001]` for a
  7.5 mm face width, probe 2026-09-26), and a translated part must fail, not only a resized
  one. Rejected: three extents (misses a shift); relative tolerance (degenerates to exact at
  a 0.0 coordinate).
- **D-13:** **B-rep topology pinned exactly:** `len(solid.Faces())` and `len(solid.Edges())`.
  The sharpest cheap tripwire for a silently vanished chamfer or fillet (the default gear:
  172 faces / 490 edges with the chamfer, 168 / 482 without) and for a new cut step touching
  an old part. Pitfall 11 targets mesh-derived constants; a kernel bump that re-splits faces
  is a D-03 regeneration with the reason stated. Rejected: volume and bbox only.
- **D-14:** **One parametrized pytest case per record, id = its source tag**, so a Phase 8
  red reads `[test_model.py::test_builds_one_valid_solid[8]]`, not `record 37`, and one
  mismatch never hides the rest. Rejected: one test looping over records.

### Selector guard contract
- **D-15:** A selector that matches **zero edges while its feature is on raises
  `BuildError`** with a message that names the selector/feature and says it is a modelling
  defect, not a parameter conflict (wording is the planner's). It rides the existing routing
  (`app.py` → 422, `cli.py` → exit 2 — `BuildError` is the only exception `model.py` lets
  out) and tests match on the text. Rejected: letting a `RuntimeError` reach
  `_build_checked`'s catch-all (it would relabel the defect as "try smaller fillets or
  chamfers"); an `EdgeSelectionError(BuildError)` subclass (one more name for a failure that
  should never reach a user — deferred, not refused); an internal error → HTTP 500 (needs the
  catch-all and an `app.py` branch changed — beyond foundation scope).
- **D-16:** **Runtime guard: non-empty only. Tests: exact count per shape.** Verified on
  the pinned kernel 2026-09-26, before the chamfer/fillet runs: round bore **2** rim edges
  (one `CIRCLE` per face), D-flat **4** (`CIRCLE` + `LINE` per face), recess floor **2**
  circles per filleted floor (2 for `top`/`bottom`, 4 for `both`); with and without
  recesses (REQ-edge-selection-proven). An expected-count rule at runtime (a per-shape
  `bore_rim_edge_count(p)`) was rejected as a second geometry model every bore phase would
  have to keep in step.
- **D-17:** **Both selectors are guarded and count-tested in this phase** —
  `_bore_rim_edges` and `_groove_floor_edges`. REQ-edge-selection-proven names "chamfer and
  fillet edge selectors"; Phase 11 composes cutouts with recesses and re-audits the floor
  selector's invariant, so its tripwire exists before then. Rejected: bore rim only.
- **D-18:** **`calc.bore_rim_limit(p)` returns the exact geometric bound** — the farthest
  rim point from the axis, no slack (round/D-flat: `bore_radius(p)`; the D-flat rim is a
  strict subset of the circle). **`model.py` adds a named slack constant, kept at today's
  0.01 mm**, with a comment stating why 10 µm rather than `TOL` (1e-6): it must exceed the
  kernel's post-boolean vertex tolerances and stay far below `MIN_WALL` (0.4 mm). `calc.py`
  knows no kernel tolerances. `_bore_rim_edges` takes whatever the planner prefers (`p` or the
  limit) — the decision is where the bound is computed, not the signature. Rejected:
  slack inside `bore_rim_limit` (a `model.py` secret leaking into the pure-maths module);
  replacing the radial band with positive identification (a selector redesign — deferred).

### Process
- **D-19:** The phase runs on
  `gsd/phase-07-foundation-generalized-edge-selection-regression-fixture`, cut from
  `origin/main` `b3ca789` (PR #7's squash) during this session, and lands via
  `make pr.land PR=N` (L22/L25). `.planning/` rides the same PR.
- **D-20:** Commits are made with plain `git commit` and explicitly staged files (never
  `git add -A`): the pre-commit hook runs `make verify` (~32 s warm, minutes cold) and the
  gsd SDK commit wrapper kills it at 30 s
  (`docs/tech_debt/active/2026-09-25-gsd-commit-timeout-kills-cold-verify-hook.md`). Run
  `make verify` once at session start to warm the cache.

### Claude's Discretion
- File and directory names: the JSON, the corpus module, the regression test module
  (`tests/test_regression.py` vs a `tests/regression/` package), the regen script, the
  `make` target. Anything new in Python must join `make typecheck`'s `src tests docker bench`
  scope and ruff's — or live inside `tests/`.
- JSON layout for minimal diffs (sorted keys, `indent=2`, trailing newline) and how records
  are keyed (source tag as the key is the obvious choice).
- How the zero-edge test provokes D-15's guard — e.g. calling the selector on a bore-less
  solid, or monkeypatching `bore_rim_limit` to a wrong bound — and the exact refusal wording.
- `_bore_rim_edges`'s signature after D-18; the slack constant's name.
- Whether the measured `make verify` delta (D-06) is recorded in `bench/RESULTS.md` or the
  plan SUMMARY (Phase 6 left the same choice to the planner; `bench/RESULTS.md` is the
  precedent for numbers that outlive a phase).
- Whether D-03 (fixture-as-the-standing-L05-proof plus its regeneration rule) and D-15 (a
  selector never silently no-ops) get **one appended decision-log entry (L26)**. The
  roadmap's process note requires an `Lxx` "at minimum" for Phases 9–11; Phase 7's rule is
  one every later phase obeys, so the recommendation is yes, one entry — the planner
  decides and, if yes, the count and numbering.
- Test names (they read as requirements) and the corpus module's docstring, which should
  carry `bench/corpus.py`'s "do not narrow or re-pick" stance.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and requirements
- `.planning/ROADMAP.md` — "### Phase 7" (goal, the four success criteria, "Research flag: No");
  "## Process Notes (v0.2)" (phase branches, `Lxx` rule, the fixture is re-run not re-derived)
- `.planning/REQUIREMENTS.md` — REQ-defaults-off-regression, REQ-edge-selection-proven (the
  two this phase owns); REQ-hex-rim-chamfer (what Phase 8/9 will ask of the selector)
- `.planning/PROJECT.md` — "Current Milestone: v0.2", "Rules this milestone lives by",
  "Success Metric (Milestone v0.2)" #3 (old links unchanged)

### The research that specified the fix and the fixture
- `.planning/research/ARCHITECTURE.md` — **Q2** (why `lim = r_bore + 0.01` fails a hex
  rim silently; `bore_rim_limit(p)` in `calc.py`; the keyway question left to Phase 9),
  **Q5** (the regression test: derive + volume/bbox, not bytes; extend
  `test_builds_one_valid_solid`'s matrix), Q6 (why this is phase one), "Anti-Pattern:
  generalizing `lim` by widening it"
- `.planning/research/SUMMARY.md` — Known Conflict #6 (the confirmed silent zero-edge
  defect), "Phase 1: Foundation", Research Flags (Phase 7 needs no research)
- `.planning/research/PITFALLS.md` — **Pitfall 4** (position-based selectors: state the
  invariant, test count and identity), **Pitfall 6** (non-off defaults; write the regression
  test first), **Pitfall 11** (no exact OCCT-produced constants — D-11/D-12/D-13 take a
  measured position on it), "Pitfall-to-Phase Mapping"

### Locked decisions and standards
- `docs/architecture/decision_log.md` — L03 (cap vs refuse), **L05** (defaults never
  rescale — the fixture is its proof), L08 (no plausible number — the selector guard is the
  geometry analogue), L12 (`requirements.txt` is a generated pinned closure — the only
  legitimate kernel bump), L13 (`make verify` is the gate), L15 (error messages are the
  product), L16 (no formatter), **L24** (export is not byte-reproducible; content
  equivalence; `Volume()`/`BoundingBox()` exact on a mesh-free cached solid). Append-only.
- `CLAUDE.md` / `AGENTS.md` — the two standing rules, the gate, "measured, not estimated",
  debt lifecycle, `make` command surface
- `docs/CODING_VALUES.md` — comments carry the measurement or constraint; `calc.py` never
  imports the kernel; vendor types stop at `model.py`

### Code this phase edits or reads
- `src/spur/model.py` — `_cut_bore` (180–194), `_cut_face_recesses` (159–177),
  `_groove_floor_edges` (204–210), `_bore_rim_edges` (213–232, the inline `lim` and the
  docstring's separating invariant), `_build` (237–246), `TOL` (41)
- `src/spur/calc.py` — `bore_radius` (57), `recess_radii` (61), `derive` /
  `DerivedDimensions` (165–310), `MIN_WALL` (15); the `TYPE_CHECKING` import of
  `GearParams`
- `src/spur/build_errors.py` — `BuildError`, the one exception that leaves `model.py`
- `src/spur/params.py` — the 17 fields and their defaults (what a record may omit)
- `tests/test_model.py` — `test_builds_one_valid_solid`'s `kw` matrix (the corpus seed),
  `_closed_shell_volume`, the L24 tests (content-equivalence precedent)
- `tests/test_calc.py` — `test_default_dimensions` (the existing L05 tripwire; its pinned
  numbers must not move), every inline `GearParams(...)`, the solver grid D-09 excludes
- `tests/test_api.py`, `tests/test_cli.py`, `tests/test_pool.py` — `params=` dicts and
  `cli.main([...])` argument lists that join the corpus
- `README.md` lines 106–108, 126 — the four examples: `spur export -o gear.step`
  (defaults), `--teeth 24 --module 1 --pressure-angle 20 --bore-flat 0`,
  `spur info --teeth 19 --mate-teeth 40`, `curl .../api/model.step?teeth=19&module=1.75&pressure_angle=25`
- `bench/corpus.py` — the "deterministic corpus, do not re-pick" docstring stance D-05
  copies; `bench/RESULTS.md` — where measured numbers live
- `Makefile` — target conventions (`## help` lines; `verify`; `typecheck`'s directory
  list); `pyproject.toml` — `[tool.pytest.ini_options]` (`filterwarnings = error`,
  `--strict-markers`), `[tool.importlinter]` (contracts `calc.py` must keep)

### Process
- `docs/HOW_TO_DEVELOP.md` §6/§8 — phase branch, PR, `make pr.land`
- `docs/tech_debt/active/2026-09-25-gsd-commit-timeout-kills-cold-verify-hook.md` — D-20
- `.planning/milestones/v0.1-phases/06-address-tech-debt-merge-gate-solid-cache/06-CONTEXT.md`
  — D-08 (content equivalence over bytes; the measurement-decides pattern), "Established
  Patterns" (plain `git commit`)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `model._bore_rim_edges` already accepts straight edges (no `geomType()` filter) — the only
  change is where `lim` comes from (D-18) plus the guard (D-15). `_groove_floor_edges`
  filters on `CIRCLE` and radius, unaffected by bore shape.
- `calc.bore_radius(p)` — the shape `bore_rim_limit(p)` sits beside; `recess_radii()` /
  `root_fillet()` are the precedent for "a bound computed in `calc.py`, consumed in
  `model.py`".
- `build_errors.BuildError` and its routing in `app.py:414` / `cli.py:111` — D-15 needs no
  new plumbing.
- `tests/test_model.py::test_builds_one_valid_solid` — nine `kw` dicts, the corpus seed;
  `test_exporting_leaves_the_cached_solid_exact` — reads `BoundingBox()` on the cached solid
  (exact, L24).
- `GearParams` is frozen and hashable — corpus dedupe is a `set`; `model_validate(kw)` is
  the way to build one from a dict under `disallow_any_explicit` (Phase 4 D-08).
- `bench/corpus.py` — a deterministic, source-tagged corpus with a "do not narrow" docstring.
- `_build_cached` (`lru_cache`, `SPUR_SOLID_CACHE` = 4) — the fixture test rebuilds most
  sets; cache hits are incidental, not something the test may rely on.

### Established Patterns
- Numbers are measured and written down before a choice is made (L17, L19, L24; Phase 6
  D-08). D-06's cost and D-11's tolerances follow it — the 2026-09-26 probe numbers in
  `<specifics>` are the starting evidence, to be re-measured in the plan.
- Content equivalence over byte equality for anything the kernel produces (L24); exact
  equality for anything Python computes (`derive()`).
- Tests read as requirements; no OCCT mocking; `filterwarnings = error`.
- Every deliberate constant carries its reason in a comment (the slack constant, the
  tolerances, the topology counts).
- Debt is filed in `docs/tech_debt/active/` with an INDEX row in the same commit; the
  decision log is append-only.
- One phase = one branch = one PR = one squash commit; plain `git commit`, explicit files.

### Integration Points
- `src/spur/calc.py` → new `bore_rim_limit(p)`; `src/spur/model.py` → `_cut_bore`'s call,
  `_bore_rim_edges`'s bound and guard, `_cut_face_recesses`'s guard on
  `_groove_floor_edges`.
- `tests/` → the corpus module, the JSON, the regression test, the selector count tests
  (`tests/test_model.py` is the natural home for the latter).
- `Makefile` → the regen target (and `typecheck`'s directory list if the script lives
  outside `tests/`).
- `docs/architecture/decision_log.md` → L26 if the planner takes the discretion item.
- `bench/RESULTS.md` or the plan SUMMARY → the measured `make verify` delta.

</code_context>

<specifics>
## Specific Ideas

Measured on the pinned kernel (`cadquery==2.8.0`, `cadquery-ocp==7.9.3.1.1`, `.venv`
Python 3.12, 2026-09-26, at `b3ca789`) — planning evidence, to be re-measured in the plan:

- `make verify` at HEAD: **191 passed in 32.47 s**, exit 0 (first run of the session).
- `build()` wall time: default gear 452 ms; round bore 399 ms; no recess 100–121 ms;
  one-sided recess 292 ms; **200 teeth 2.3 s**.
- Default gear `Volume()` 4451.2562338579555 mm³, identical over three independent builds
  (max diff 0.0). Without the bore chamfer 4455.9177 → the chamfer is **1.05e-3** of the
  volume; the recess fillets **2.9e-3** (a concave fillet adds material).
- Topology, default gear: 172 faces / 490 edges; without the chamfer 168 / 482.
- `BoundingBox()` on a fresh solid: `z[-1.0e-7, 7.5000001]`, `x[-18.183944, 18.375]` —
  the kernel's tolerance enlargement is ~1e-7 per side.
- Selected-edge counts on the pre-chamfer / pre-fillet solid: round bore 2 (`CIRCLE` ×2),
  D-flat 4 (`CIRCLE`, `LINE` per face), recess floor 2 circles per filleted floor. On the
  *finished* solid the same selectors find 0 — the guard must sit where the selector is
  called today, before the operator runs, not as a post-build check.
- Corpus size, rough count of hand-written sets (D-09): `test_model.py` 9 + 4 inline,
  `test_calc.py` ~12 inline + 2 parametrized dicts, `test_api.py` up to 29 `params=` dicts
  (many info-only, some 422), `test_cli.py` 3, `test_pool.py` ~9 (teeth 21/22/43/44), README
  4 — expect ~40–50 distinct `GearParams` after dedupe, mostly ≤ 0.5 s builds. At ~0.4 s
  each the build side is ~20 s before cache effects — D-06's 15 s line will likely be
  tested; the planner measures, not guesses.

</specifics>

<deferred>
## Deferred Ideas

- **Positive-identification edge selection** (capture the cutter wire before the boolean,
  match its edges back by centre/radius — Pitfall 4 §4) if radial-band proofs get hard once
  three or more features share an end face. Phase 11/12 territory; not this phase.
- **`EdgeSelectionError(BuildError)` subclass** — revisit if a later phase needs to catch
  the guard by type rather than by text.
- **Runtime exact-count guard** (`bore_rim_edge_count(p)`) — revisit if a "wrong edges, not
  zero edges" failure is ever observed in production geometry.
- **`docker/smoke.py` and `bench/corpus.py` sets in the fixture** — excluded by D-08;
  revisit if `make check` ever diverges from `make verify` on a pre-v0.2 gear.
- **derive()-only records for the solver grid** — excluded by D-09; the grid keeps its own
  oracle in `test_centre_distance_matches_an_independent_solver`.

None of these came from the user as scope requests — discussion stayed within the phase.

</deferred>

---

*Phase: 07-foundation-generalized-edge-selection-regression-fixture*
*Context gathered: 2026-09-26*
