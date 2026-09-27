# Phase 8: Hex Bore - Context

**Gathered:** 2026-09-26
**Status:** Ready for planning

<domain>
## Phase Boundary

The first user-facing feature of v0.2, and the first real geometry Phase 7's generalized
selector meets.

1. **The field.** `bore_hex: float = 0` (across-flats, mm, `0 = round bore`, `le` 200)
   joins `GearParams`' Bore group, declared after `bore_flat`. It is a flat additive field
   like `bore_flat`, not a `bore_type` discriminator (research ARCHITECTURE.md Q3). The
   CLI flag `--bore-hex`, the `/api/schema` entry and the form field fall out of the
   generators; the shareable URL carries it like any other field.
2. **The cut.** When `bore_hex > 0`, `_cut_bore` subtracts a regular hexagonal prism
   (`Workplane.polygon(6, effective_af, circumscribed=True)`, verified on the pinned
   kernel) where `effective_af = bore_hex + bore_clearance` — clearance added across the
   flats. The hexagon **replaces** the round/D-flat profile: `bore_d` and `bore_flat` do
   not apply and are reported as ignored (D-01/D-02), never refused. `bore_chamfer`
   chamfers all twelve rim edges (six `LINE` edges per face) through the existing
   `_bore_rim_edges`, with `calc.bore_rim_limit(p)` returning the circumradius
   `effective_af / sqrt(3)` for a hex (L26's designated seam) — Phase 7's guard would have
   raised on the v0.1 bound, and the exact-count matrix now proves 12.
3. **The rules.** `check()` skips the round-profile rules when the hex is on and applies
   the hex's own: the corner within `MIN_WALL` of the root circle is a 422 naming
   `bore_hex`; a `bore_chamfer` the hex's side cannot carry is a 422 naming `bore_chamfer`
   and `bore_hex`, its bound measured on the kernel (D-03). `recess_radii()`'s hub
   clearance is measured from the corner, so a recess narrows or drops out with the
   existing warnings (cap-and-warn, L03).
4. **The numbers.** `DerivedDimensions` gains two fields — the effective across-flats and
   the corner-to-corner diameter — both `null` when `bore_hex == 0`; `bore_effective` is
   `null` on a hex bore; the 19 existing fields keep name, type and value (D-04–D-06). The
   web UI shows both rows this phase; README documents the field this phase.
5. **The measurement.** A committed bench script and `make` target run an 8-row sweep at
   200 teeth (build, fine STL, STEP), recorded in `bench/RESULTS.md`, every row inside
   `SPUR_BUILD_TIMEOUT=30s` (D-11/D-12).
6. **The fixture.** `tests/regression/pre_v0_2.json` passes unmodified — `git diff
   --exit-code` on it after every task (07 D-03, L26).

Requirements: REQ-hex-bore, REQ-derived-dimensions-additive. Phase 8 also delivers the
hex-only edge of REQ-hex-rim-chamfer and REQ-bore-derived-numbers (both owned by Phase 9,
which re-confirms them once the keyway exists — REQUIREMENTS.md "Notes on bundled
requirements").

**Not in scope:** any keyway field, and therefore the hex × keyway 422 named in ROADMAP
SC2 — it lands in Phase 9 with the fields it names; UI presets for commodity hex sizes
(REQ-hex-presets, Future Requirements); conditional form behaviour (greying out ignored
fields, D-09); a hex as a union with the round bore (rejected in REQUIREMENTS.md "Out of
Scope"); user control of the hexagon's orientation; the composition matrix (Phase 12);
fuzzy-boolean `tol=` (research Pitfall 1 — no tangency is reachable here, see Claude's
Discretion).

</domain>

<decisions>
## Implementation Decisions

### Round-profile fields alongside the hex
- **D-01:** **The hex replaces the whole round/D-flat profile: `bore_d` and `bore_flat`
  are ignored and warned about, never refused.** `?bore_hex=6` alone builds on the web,
  the API and the CLI. This **supersedes the `bore_flat` half of REQ-hex-bore's 422
  sentence and ROADMAP Phase 8 SC2** ("`bore_hex` together with `bore_flat` … is a 422"):
  `bore_flat` defaults to **8.0**, so that 422 would fire on every link that only adds
  `bore_hex`, contradicting the same requirement's own "a shareable link that only adds
  `bore_hex` still works" and L05 (a default the user never set must not block the part).
  The hex × keyway 422 stands and is Phase 9's. The plan's first task amends the
  REQ-hex-bore wording and SC2 (roadmap edits through the phase tooling, never a direct
  write) so the verifier checks against this decision, not the superseded sentence.
  Rejected: a 422 gated on `GearParams.model_fields_set` (viable today — the form sends
  only non-default fields, the CLI only given flags — but a refusal that depends on
  whether a client echoes defaults; a script sending the full form would be refused for a
  value it never chose); keeping the 422 as written (every hex link must carry
  `bore_flat=0`). — **Reversibility:** costly — once `?bore_hex=6` builds, turning it into
  a refusal breaks every published link that relied on it (L05); the `bore_flat=0`
  requirement can only be added before the feature ships.
- **D-02:** **One warning sentence, naming the ignored fields that are non-zero, with
  their values** — e.g. "Hex bore replaces the round profile: bore_d (9 mm) and bore_flat
  (8 mm) are ignored." With `bore_flat=0` only `bore_d` is named; with both zero there is
  no warning. Every plain hex link carries it (`bore_d` defaults to 9) — accepted;
  REQ-hex-bore asks for exactly this. Exact wording is the planner's (the sentence is the
  product, L15). Rejected: one warning per field (two lines on the common case); warning
  only for non-default fields (`model_fields_set` again, and it contradicts REQ-hex-bore's
  "warns when `bore_d` is also non-zero").
- **D-03:** **With `bore_hex > 0` the round-profile checks do not run; the hex gets its
  own.** `?bore_hex=6&bore_flat=3` builds (with the D-02 warning) — a 422 about a field
  the response says is ignored would be a contradiction. The hex rules, all in
  `calc.check()` before any CAD work: (a) **corner vs. root** — the circumradius of the
  effective across-flats above `rf - MIN_WALL` is a 422 naming `bore_hex` (the mirror of
  "Bore is too large for the root diameter"); (b) **chamfer vs. side** — a `bore_chamfer`
  the hex's side (`effective_af / sqrt(3)`) cannot carry is a 422 naming `bore_chamfer`
  and `bore_hex`, refused early rather than left to the kernel (the principle Phase 11's
  REQ-cutout-conflicts-refused-early states). **The bound is measured, not assumed:** the
  planner probes the pinned kernel (chamfer stepped up toward the side length on a small
  and a large hex, with and without recesses) and writes the failing ratio next to the
  rule with its measurement; if the kernel copes at every allowed size, no rule is added
  and the probe result is recorded instead. The shape-independent "chamfer < half the face
  width" check stays. Rejected: letting `_build_checked`'s catch-all report it ("try
  smaller fillets or chamfers" — after a timed build in a worker slot, without naming
  `bore_hex`); capping the chamfer and warning (the user asked for that chamfer on that
  hex — a direct conflict, L03's refuse branch).

### What the numbers say for a hex bore
- **D-04:** **`bore_effective` is `null` on a hex bore.** Its description is "Bore diameter
  including print clearance" and the UI labels it "Bore Ø incl. clearance"; a hexagon has
  no diameter and `bore_d` is ignored. Rejected: repurposing it for the effective
  across-flats (the description and label become wrong; a consumer reading a diameter gets
  a number that is not one). — **Reversibility:** costly — a published `/api/info` field's
  meaning under L21's typed contract; changing it later is a contract change with its own
  `Lxx`.
- **D-05:** **Two new `DerivedDimensions` fields**, both `float | None`, `null` when
  `bore_hex == 0`, rounded to 3 dp at construction (Phase 4 D-10), `unit: mm`:
  the **effective across-flats** (`bore_hex + bore_clearance` — what calipers read across
  two flats, the fit number and the hex analogue of `bore_effective`) and the
  **corner-to-corner diameter** (effective across-flats × 2/√3 — what calipers read across
  two corners). Names are the planner's. ROADMAP SC3's "its first new field (hex
  corner-to-corner diameter)" is met and extended; REQ-derived-dimensions-additive allows
  it. The 19 existing fields keep their names, types and values; `disallow_any_explicit`
  stays on with no suppressions. Rejected: corner-to-corner only (with `bore_effective`
  null, the fit dimension would appear nowhere in the response).
- **D-06:** **Both rows land in the web UI this phase** — two `DIMS` entries in
  `src/spur/static/app.js` with labels (e.g. "Hex across flats incl. clearance", "Hex
  across corners"). Milestone Success Metric 1: UI, API and CLI ship in the same change;
  Phase 12 verifies parity, it does not build it. `tests/test_api.py`'s DIMS-subset test
  already guards the keys. Rejected: deferring the rows to Phase 12.

### Form placement, help text, README
- **D-07:** **`bore_hex` lives in the Bore group, declared after `bore_flat`** (field
  order is form order and CLI order), title on the order of "Hex bore A/F", unit mm, step
  0.05, `ge` 0, **`le` 200 like `bore_d` and `bore_flat`** (one family, one bound;
  anything larger than the root is refused by D-03 anyway; keeps "max `bore_hex`" in the
  sweep unambiguous). REQ-three-interfaces-extended's "in its own group" is read as "each
  feature's fields grouped" — the Bore group is that group, and Phase 9's keyway fields
  join it. Rejected: a one-field "Hex bore" fieldset (clearance and chamfer would live in a
  different box than the profile they apply to); a smaller `le` such as 50 (a bound
  meaning "what we have seen sold", a guess about the user's shaft).
- **D-08:** **Help text states the replacement and gives commodity sizes as examples, no
  standard named** — on the order of "Across-flats of a hex bore; replaces the round bore
  and D-flat. Common hex stock: 5, 6, 8, 10, 12.7 mm. 0 = round bore." FEATURES.md found
  no standard for gear hex bores; sizes are examples of stock, never a table that fills a
  value (REQ-hex-bore; L08). The CLI prints the same sentence. Rejected: no sizes at all
  (loses the 12.7 mm = ½″ hint); folding the clearance rule into this sentence
  (`bore_clearance`'s own help is the place — see Claude's Discretion).
- **D-09:** **No conditional form behaviour.** `bore_d` and `bore_flat` stay live when
  `bore_hex > 0`; the D-02 warning is the signal, and the existing invalid-field highlight
  covers 422s. The form stays purely schema-driven, which is what keeps L02 ("a field
  added once shows up everywhere") true. Rejected: greying out the two fields (the first
  "disabled when" relation in `app.js`, a mechanism the schema does not carry; Phase 9
  would need its own rule set).
- **D-10:** **README.md is updated in the same change**: the feature bullet ("D-flat or
  round bore", line 11) gains hex; the parameter table (lines 149–152) gains a `bore_hex`
  row carrying D-08's sentence; one example link (e.g. `spur export … --bore-hex 6`) joins
  the examples. The new example is a post-v0.2 set: it stays **out** of the regression
  corpus (07 D-05 — "pre-v0.2" is a closed set) and the fixture stays byte-unchanged.
  Rejected: deferring README to Phase 12.

### Heaviest configuration and the measurement
- **D-11:** **An 8-row sweep at 200 teeth, every row recorded, the worst row named
  "heaviest":** `bore_hex ∈ {200 (le), 12.7}` × `recess_sides ∈ {both, none}` ×
  `bore_chamfer ∈ {0.4, the maximum D-03 allows}`, module at its default 1.75 unless the
  planner's probe shows module drives export time (see Claude's Discretion). Per row:
  build wall time (solid cache cleared between rows), fine-STL export time and STEP
  export time. Recorded in a new `bench/RESULTS.md` section in the shape of "Regression
  fixture cost (Phase 7, D-06)" — host state header with the load-average caveat, the
  table, the named heaviest row. Every row must sit inside `SPUR_BUILD_TIMEOUT=30s`; a
  row that does not is a halt for a human decision, not a silent narrowing. Rejected: one
  configuration (assumes the default recess and chamfer are the heavy case rather than
  showing it); build time only (Phase 12's REQ-measured-build-time wants export time per
  feature, and Phases 9–11 repeat the same shape — Phase 12 still re-measures the
  combined heaviest configuration).
- **D-12:** **The sweep runs from a committed bench script behind a `make` target**
  (e.g. `bench/build_time.py`, `make bench.build`, beside `bench.latency`/`bench.memory`):
  it takes parameter sets, times build / fine STL / STEP per set, and prints the Markdown
  table `bench/RESULTS.md` records. Phases 9, 10, 11 and 12 reuse it unchanged; a re-run
  on another host is one command. It joins `make typecheck`'s scope (`bench` already is)
  and ruff's. Rejected: an ad hoc `python -c` / `pytest --durations` command pasted into
  RESULTS.md (each later phase re-derives it).

### Process
- **D-13:** The phase runs on **`gsd/phase-08-hex-bore`**, cut this session from
  `origin/main` `540f1a0` (PR #8's squash), and lands via `make pr.land PR=N` (L22/L25).
  `.planning/` rides the same PR.
- **D-14:** Commits are plain `git commit` with explicitly staged files, never `git add
  -A`: the pre-commit hook runs `make verify` (48.4 s warm with the fixture, Phase 7's
  measurement; minutes cold) and the gsd SDK commit wrapper kills it at 30 s
  (`docs/tech_debt/active/2026-09-25-gsd-commit-timeout-kills-cold-verify-hook.md`).
  Run `make verify` once at session start to warm the page cache.

### Claude's Discretion
- **Names:** the two derived fields (D-05); the bench script and target (D-12);
  `bore_hex`'s title (D-07); the exact warning (D-02) and refusal (D-03) sentences — the
  shapes are locked, the wording is the planner's and is the product (L15).
- **Hexagon orientation:** the kernel's default puts a flat facing +X (the D-flat's side)
  and a vertex on ±Y (probe below). Keep the default, no rotation parameter; one comment
  stating which way the flats face.
- **How the hex extent reaches its consumers:** `bore_rim_limit(p)` is the locked seam
  (L26). Whether `bore_radius(p)` learns the hex, or a sibling "bore extent" helper feeds
  `recess_radii()`'s hub clearance and `_cut_bore`, is the planner's — the constraint is
  that `recess_radii()` clears the **corner** plus chamfer plus `MIN_WALL`, and that
  `derive()` never reports a hex number through `bore_effective` (D-04).
- **`bore_clearance`'s help text** ("Added to bore and flat …") — recommend extending it to
  say it is added across the hex flats too; a description change touches `/api/schema`
  but nothing the fixture pins.
- **Selector matrix rows:** hex × `recess_sides ∈ {both, top, bottom, none}` added to
  `test_each_edge_selector_picks_exactly_its_own_edges`, expecting `Counter({"LINE": 12})`
  for the rim and the unchanged floor counts (07 D-16/D-17). `git diff --exit-code
  tests/regression/pre_v0_2.json` after every task (L26).
- **Measuring the built solid, not only the derive() number:** recommend a test that reads
  the rim-edge vertices of a built hex bore and asserts their radius equals
  corner-to-corner/2 within `TOL`, and the flat-to-flat distance equals the effective
  across-flats — the Phase 8 analogue of Phase 9's "floor position measured against the
  stated datum by a test". Planner decides the exact form.
- **The chamfer-vs-side probe (D-03):** sizes, step and which recess settings it covers;
  whether the small-hex default case (`bore_hex=0.5` with the default 0.4 chamfer, side
  0.38 mm) is the natural first failing point.
- **A max-module row in the sweep (D-11):** fine-STL tessellation is deflection-based
  (`TESSELLATION["fine"] = (0.01, 0.1)`), so export cost scales with size, not only
  tooth count; the planner probes whether `module=10` at 200 teeth belongs in the table.
- **An `Lxx` entry:** ROADMAP's process note requires one "at minimum" for Phases 9–11.
  Recommend one for Phase 8 too (L27), recording D-01 (hex replaces round; the `bore_flat`
  supersession and why), D-03's measured chamfer bound and D-11's heaviest row — the
  planner decides.
- **Fuzzy booleans (`tol=`, research Pitfall 1):** not needed in Phase 8 —
  `recess_radii()` keeps at least `MIN_WALL` between the corner and the recess wall by
  construction, so no tangency is reachable; the planner confirms this reasoning in the
  plan rather than adding a `tol=` nobody measured.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and requirements
- `.planning/ROADMAP.md` — "### Phase 8: Hex Bore" (goal, the five success criteria —
  SC2's `bore_flat` clause is superseded by D-01, its keyway clause is Phase 9's);
  "### Phase 9" SC4/SC5 (what Phase 9 asks of the hex); "## Process Notes (v0.2)"
- `.planning/REQUIREMENTS.md` — REQ-hex-bore (D-01 supersedes its `bore_flat` 422
  sentence; the rest stands), REQ-derived-dimensions-additive (this phase's second
  requirement), REQ-hex-rim-chamfer and REQ-bore-derived-numbers (Phase 9 owns them;
  Phase 8 delivers the hex edge — "Notes on bundled requirements"),
  REQ-three-interfaces-extended and REQ-measured-build-time (Phase 12's bar that D-06,
  D-10, D-11 meet early), "## Out of Scope" (hex as a union with the round bore —
  rejected), "### Bore and cutout follow-ups" (REQ-hex-presets — deferred)
- `.planning/PROJECT.md` — "Current Milestone: v0.2", "Rules this milestone lives by",
  "Success Metric (Milestone v0.2)" #1–#3

### The research behind the field, the bound and the numbers
- `.planning/research/ARCHITECTURE.md` — **Q2** (why `lim` fails a hex rim silently; the
  circumradius `w/√3`; `polygon(circumscribed=True)`'s `diameter` is the across-flats),
  **Q3** (additive flat fields, no discriminator; the `bore_flat` precedent), **Q4** (the
  new-derived-fields table and the cap-vs-refuse split)
- `.planning/research/FEATURES.md` — "## Standards Cited — Hex Bore" (no standard exists;
  commodity sizes as examples only), "Feature Dependencies" (hex vs. keyway)
- `.planning/research/PITFALLS.md` — Pitfall 1 (fuzzy booleans — why not needed here),
  **Pitfall 4** (position-based selectors: re-audit per feature), Pitfall 6 (defaults
  off, fixture first), Pitfall 11 (no OCCT-produced constants without a measurement)
- `.planning/research/SUMMARY.md` — Known Conflicts #5 (hex replaces vs. adds — decided
  "replaces") and #6 (the zero-edge defect Phase 7 closed and this phase proves)

### The foundation this phase stands on
- `.planning/phases/07-foundation-generalized-edge-selection-regression-fixture/07-CONTEXT.md`
  — D-03 (fixture regeneration rule), D-05 (closed pre-v0.2 corpus), D-15–D-18 (guard
  contract, exact counts in tests, `bore_rim_limit` is the seam, slack stays in
  `model.py`), D-19/D-20 (branch and commit process)
- `.planning/phases/07-foundation-generalized-edge-selection-regression-fixture/07-01-SUMMARY.md`
  and `07-02-SUMMARY.md` — what shipped, the measured numbers, the D-06 decision
- `docs/architecture/decision_log.md` — L02 (one model, three interfaces), **L03** (cap
  vs. refuse), **L05** (defaults never rescale — D-01's reason), L08 (no plausible
  number), L15 (error and warning sentences are the product), L16 (no formatter), L21
  (typed responses, no `Any`), L24 (content equivalence over bytes), **L26** (the fixture
  and the selector rule; "Phase 8 adds the hex circumradius here"). Append-only.
- `CLAUDE.md` — the two standing rules, the gate, "measured, not estimated", debt
  lifecycle, `make` command surface
- `docs/CODING_VALUES.md` — comments carry the measurement; `calc.py` never imports the
  kernel; vendor types stop at `model.py`; validate once at the `GearParams` boundary

### Code this phase edits or reads
- `src/spur/params.py` — the Bore group (54–62: `bore_d`, `bore_flat`, `bore_clearance`,
  `bore_chamfer`), `_f()` (17–23), `_feasible` (78–88), `slug()` (90–92)
- `src/spur/calc.py` — `bore_radius` (57), `bore_rim_limit` (61–74, the docstring names
  this phase), `recess_radii` (77–98, hub clearance), `check` (132–169, the round-profile
  rules D-03 skips), `DerivedDimensions` (181–240), `derive` (243–326), `MIN_WALL` (15)
- `src/spur/model.py` — `_cut_bore` (194–208), `_bore_rim_edges` (241–269),
  `BORE_RIM_SLACK` (50–55), `TOL` (49), `TESSELLATION` (47), `_build` (274–283),
  `_build_cached` (296)
- `src/spur/app.py` — `InfoQuery` / `ModelQuery` / `_gear` (211–228: new fields need no
  wiring), `info` route (357–360)
- `src/spur/cli.py` — the flag generator (43–56: `--bore-hex` falls out)
- `src/spur/static/app.js` — `DIMS` (13–29, D-06), `gearQuery` (92–98: only non-default
  fields are sent), `renderInfo` (124–142: `null` rows are skipped)
- `tests/test_model.py` — `test_each_edge_selector_picks_exactly_its_own_edges` (45–125,
  the matrix hex rows join), `test_builds_one_valid_solid` (26–45), the two zero-edge
  guard tests (126–152)
- `tests/test_api.py` — the DIMS-subset test (110–125), `test_infeasible_is_422_with_fields`
  (132–138: the 422 shape D-03's rules must match)
- `tests/test_calc.py` — `test_default_dimensions` (the L05 tripwire; its numbers must
  not move)
- `tests/regression/` — `corpus.py` (closed set), `pre_v0_2.json` (must stay
  byte-unchanged), `test_pre_v0_2.py`
- `bench/RESULTS.md` — "## Regression fixture cost (Phase 7, D-06)" (the section shape
  D-11 copies; the host-state and load-average caveat convention)
- `bench/corpus.py` — the existing bench module conventions; `Makefile` — `bench.*`
  targets (112–118), `fixture.regen` (132), `typecheck`'s directory list, `## help` lines
- `README.md` — line 11 (feature bullet), 106–108 and 126 (examples), 149–152 (bore
  parameter table)
- `pyproject.toml` — `[tool.importlinter]` (contracts `calc.py` keeps),
  `[tool.pytest.ini_options]` (`filterwarnings = error`, `--strict-markers`)

### Process and debt
- `docs/HOW_TO_DEVELOP.md` §6/§8 — phase branch, PR, `make pr.land`
- `docs/tech_debt/active/2026-09-25-gsd-commit-timeout-kills-cold-verify-hook.md` — D-14
- `docs/tech_debt/active/2026-09-26-ci-resolves-the-kernel-the-fixture-pins.md` — what a
  red fixture can mean besides a Phase 8 bug (a resolved kernel drifting in CI)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `model._bore_rim_edges` accepts straight edges already (no `geomType()` filter) and
  reads its band from `calc.bore_rim_limit(p) + BORE_RIM_SLACK` — the hex needs only the
  circumradius returned from `bore_rim_limit`, no selector change (L26).
- `calc.bore_rim_limit(p)` carries a docstring that already says where the hex goes.
- `Workplane.polygon(6, d, circumscribed=True)` on the pinned kernel: `d` is the
  across-flats; six `LINE` edges; apothem `d/2`, circumradius `d/√3` (probe below).
- `_cut_bore`'s `bore_flat` branch (`hole.intersect(keep)`) is the pattern for a second
  profile; the hex is a separate prism, not an intersection.
- `calc.check()`'s `("message", ("field", ...))` tuples and `params._feasible` — D-03's
  rules need no new plumbing; `test_infeasible_is_422_with_fields` shows the wire shape.
- `derive()`'s `r3()` and the `x if cond else None` idiom for optional fields (D-05).
- `app.js` `DIMS` — a two-line addition per field (D-06); `renderInfo` skips `null`.
- `bench/RESULTS.md`'s Phase 7 section — the host-state header and table shape D-11 copies.
- `GearParams.model_validate(kw)` under `disallow_any_explicit` (Phase 4 D-08) for
  building parameter sets in tests and the bench script.

### Established Patterns
- Numbers are measured and written down before a rule is written (L17, L19, L24, L26;
  07 D-06/D-11) — D-03's chamfer bound and D-11's heaviest row follow it.
- Refuse a direct conflict naming the fields; cap and warn a trimmable wish; report
  nothing rather than a plausible number (L03, L08) — D-01–D-04 sort every hex case into
  one of the three.
- Every deliberate constant carries its reason and its measurement in a comment; warning
  and refusal sentences name the field and say what to change (L15).
- Tests read as requirements; exact counts in tests, non-empty guard at runtime (07 D-16).
- Fixture never changes in a feature commit; `git diff --exit-code` guards it (07 D-03).
- One phase = one branch = one PR = one squash; plain `git commit`, explicit files.

### Integration Points
- `src/spur/params.py` → `bore_hex` in the Bore group after `bore_flat`.
- `src/spur/calc.py` → `bore_rim_limit` (circumradius), hex extent for `recess_radii`'s
  hub, the D-03 rules in `check()`, two fields in `DerivedDimensions` and `derive()`,
  `bore_effective` → `None` on hex, the D-02 warning.
- `src/spur/model.py` → the hex prism in `_cut_bore`; nothing else.
- `src/spur/static/app.js` → two `DIMS` rows.
- `tests/test_model.py` (matrix rows, a solid-measurement test), `tests/test_calc.py`
  (D-02/D-03/D-05 unit tests), `tests/test_api.py` / `tests/test_cli.py` (a hex link
  through each interface; the 422s naming the fields).
- `bench/` → the sweep script; `Makefile` → `bench.build`; `bench/RESULTS.md` → the
  section.
- `README.md` → bullet, table row, example; `.planning/REQUIREMENTS.md` and ROADMAP SC2
  → D-01's wording amendment; `docs/architecture/decision_log.md` → L27 if taken.

</code_context>

<specifics>
## Specific Ideas

Probed on the pinned kernel (`cadquery==2.8.0`, `cadquery-ocp==7.9.3.1.1`, `.venv`
Python 3.12, 2026-09-26, at `540f1a0`) — planning evidence, to be re-measured in the plan:

- `cq.Workplane("XY").polygon(6, 6.0, circumscribed=True)`: vertices at
  `(±3.0, ±1.7321)` and `(0, ±3.4641)`; max vertex radius **3.46413** (= 6/√3 =
  3.46410 to 4 dp); apothem (edge midpoint radius) **3.0** (= 6/2); six `LINE` edges.
  A **flat faces +X** — the same side the D-flat sits on (`_cut_bore`'s `keep` rectangle
  leaves the flat at `x = flat − r_bore`, on +X); vertices sit on ±Y.
- Rim-edge counts the matrix expects: round **2** (`CIRCLE`), D-flat **4** (`CIRCLE` +
  `LINE` per face), hex **12** (`LINE` × 6 per face).
- `gearQuery()` in `app.js` sends only fields that differ from their default; the CLI
  passes only given flags — why a `model_fields_set` gate was viable and was still
  rejected (D-01).
- At 200 teeth, `module=1.75`: `rf = 172.8125` mm (`root_d` 345.625); `bore_hex=200`
  with the default 0.15 clearance gives an effective across-flats 200.15, circumradius
  **115.56** mm, hub for `recess_radii` = 115.56 + chamfer + 0.4 — the default recess
  (width 6) still fits inside `rim = 172.41`. Hex sides at the `le` are 115.56 mm; at
  5 mm across-flats 2.89 mm; at 0.5 mm 0.29 mm — below the default 0.4 chamfer (D-03's
  probe starts here).
- Worked example for D-05: `bore_hex=6`, `bore_clearance=0.15` → effective across-flats
  6.15, corner-to-corner 6.15 × 2/√3 = **7.101** mm.
- Phase 7's numbers this phase builds on: a 200-tooth build 2.3 s; `make verify` 48.4 s
  with the fixture (276 tests then; 289 at `540f1a0`); the default gear 172 faces / 490
  edges.

</specifics>

<deferred>
## Deferred Ideas

- **Commodity hex sizes as UI presets** (5, 6, 8, 10, 12.7 mm) — already tracked as
  REQ-hex-presets in `.planning/REQUIREMENTS.md` "Future Requirements"; D-08 puts them
  in help text as examples only.
- **Conditional form fields** ("disabled when" relations carried by the schema) —
  rejected for one field (D-09); revisit if Phase 9 or 11 accumulates more
  ignored-when relations than a warning sentence carries well.
- **Rotating the hexagon relative to tooth 0** — nobody asked; the kernel default
  (flat on +X) ships with a comment. A parameter only if a real shaft needs it.
- **`model_fields_set`-aware refusals** (a 422 only for values the user explicitly
  sent) — rejected in D-01 as transport-coupled; recorded so it is not re-derived.
- **Chamfering the hex mouth to a different size than the round bore's** — not raised;
  `bore_chamfer` is one number for any profile.

None of these came from the user as scope requests — discussion stayed within the phase.

</deferred>

---

*Phase: 08-hex-bore*
*Context gathered: 2026-09-26*
