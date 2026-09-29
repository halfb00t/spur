# Phase 12: Composition Pass - Context

**Gathered:** 2026-09-29
**Status:** Ready for planning

<domain>
## Phase Boundary

The v0.2 close-out: no new cut, no new field. The phase proves that the four cut families
Phases 8–11 shipped compose on one gear, proves that every v0.2 field reaches all three
interfaces from the one `GearParams` model, measures the **real** composed build time
that Phases 10 and 11 could only add up, re-measures the two v0.1 export numbers on v0.2
topology, runs the pre-v0.2 fixture one last time, and records the milestone in L31.

1. **The composed sweep** (REQ-measured-build-time, SC3). A new sweep file run by the
   unchanged `bench/build_time.py` through `make bench.build SWEEP=…` (08 D-12): each
   cutout pattern's recorded heaviest row stacked with the tip chamfer at its cap and both
   recesses, on the heaviest bore its hub rule allows, at module 1.75 and 10 (~12 rows),
   plus the six single-feature heaviest rows re-run as baselines on the same host (D-01).
   Decisive readings come from a quiet host (D-02); a row over `SPUR_BUILD_TIMEOUT=30s`
   halts for a human decision whose first offer is a lower count `le` (D-03). One gear at
   a time — no concurrent-load run (D-04). The two must-debt files whose trigger is this
   sweep are resolved in the sweep's commit (D-05).
2. **The composition matrix** (SC1). Two tiers: a 96-row cross product in `calc.py`
   (bore × cutout × recess × tip chamfer — every row either derives with the expected
   fields and warnings or refuses naming the expected fields), and ~18 kernel rows for
   the pairs no existing test builds, each re-running the feature's own built-solid proof
   helper on the composed solid (D-07…D-09). Every locked refusal is exercised with every
   other family switched on (D-08). The phase's new tests may add at most 30 s to `make
   verify`, measured (D-10).
3. **Interface parity** (REQ-three-interfaces-extended, SC2). One model-driven test walks
   `GearParams.model_fields` across `/api/schema`, the CLI parser and one composed link
   through `spur info` / `/api/info`; the shareable-URL round-trip is proven statically
   from `app.js`; the browser is checked by hand at verify-work (D-11). The form stays
   schema-driven — the UI pass's verdict on the two deferred UI ideas is "not taken",
   recorded in their files (D-12). The `cli.md` exit-code must-debt is folded in and
   resolved (D-13). One composed README example link, run by the tests (D-14).
4. **The re-measurements** (SC4). L19's gzip-level table and L24's mesh-copy cost are
   re-measured on the composed-sweep row with the largest measured fine STL (D-16),
   through a committed `bench/` script and `make` target (D-17); L19's selection rule is
   applied as written (D-18).
5. **The fixture and the record** (SC5). The pre-v0.2 fixture replays unchanged one final
   time; SC3 and SC5 are amended through the edit-phase tooling to match the locked
   decisions they contradict (D-06, D-15); one L31 records the phase (D-19).

**Out of this phase:** any new field or cut; conditional form fields and the bore-shape
selector (D-12, deferred with new triggers); a headless-browser test (deferred idea
stands); the ten-concurrent scenario for the composed worst row (D-04); L17's `mem_limit`
re-sweep on v0.2 topology (its own trigger); milestone close-out bookkeeping
(`MILESTONES.md`, the audit) — `gsd-complete-milestone`'s.

</domain>

<decisions>
## Implementation Decisions

### The composed sweep
- **D-01:** **Stacks on each cutout's heaviest row, at both modules, plus six baselines.**
  Rows (200 teeth, `recess_sides=both`, exact parameters the planner's, taken from the
  recorded heaviest rows in `bench/RESULTS.md`): spokes at `le` 40 (module 10,
  `spoke_width` 0.4, `hub_d` 52, `rim_wall` 0.4, `spoke_fillet` 5 — 18.52 s alone), holes
  at `le` 60 (11.79 s alone), honeycomb at the cap (`hex_cell` 3, `hex_wall` 0.4 — 8.65 s
  alone) — each stacked with `tip_chamfer` at its cap on that gear (1.75 mm at module
  1.75; the three-limit cap at module 10) and with the heaviest bore the row's hub rule
  allows (the largest `bore_hex` that clears `bore_mouth_limit + MIN_WALL` against the
  cutout's hub datum, and separately a keyed round bore), at module 1.75 and 10 — about 12
  rows. Plus the six single-feature heaviest rows (hex 5.08 s, keyway 4.85 s, tip chamfer
  14.87 s, holes, spokes, honeycomb) re-run unchanged on the same host in the same
  session, so every composed number has a same-host baseline. 09-04's lesson stands: the
  heaviest row was not the largest feature, so both modules are measured rather than
  assumed. A new sweep file under `bench/sweeps/` (name the planner's), a `test_bench` row
  test in the shape of the Phase 8–11 ones, a `bench/RESULTS.md` section with the
  host-state header, the table and the named heaviest row. Rejected: the full 48-row cross
  product (20–30 min for numbers nobody will decide on); SC3's literal "recess + hex
  pattern" only (ignores the spokes + tip chamfer arithmetic total the debt file names as
  the actual risk).
- **D-02:** **Decisive readings come from a quiet host: load average < 1.5 at the run's
  start** (the spoke debt file's own bar). A row read under higher load is recorded with
  its load figure — never dropped or re-run to green (11-06's rule) — but no `le` or
  timeout decision rests on it; the decisive run is re-run quiet. Rejected: accepting any
  load as measured (Phase 11's UAT precedent) — the 18.52 s spoke row was read under load
  32.17 and the whole point of this sweep is to separate load inflation from a real
  margin problem.
- **D-03:** **A composed row over `SPUR_BUILD_TIMEOUT=30s` halts for a human decision
  with the number; the first offer is a lower count `le` on the pattern's selector,
  the second is a higher `SPUR_BUILD_TIMEOUT` default recorded in L31 with the
  measurement.** The honeycomb's lever stays `HEX_CELL_CAP` (11 D-11: "lowered before any
  honeycomb link exists in the wild"). A lower `le` is D-07/D-18's precedent — a
  schema-visible maximum, the same on every machine, published in `bench/RESULTS.md` and
  L31 — and it is lowered only to the largest count whose composed row builds inside the
  timeout, so no link that ever returned a part is refused. A teeth-dependent cap from a
  measured per-cutter cost is not offered (rejected twice: 10 D-07, 11 D-12). Rejected as
  the first offer: raising the timeout (no part changes, but the "4× the worst build"
  rationale is rewritten and a stalled worker blocks longer on a bad request — kept as the
  second offer, taken only if a lower `le` would refuse a configuration someone
  plausibly cuts). — **Reversibility:** costly — a lowered `le` is a published schema
  maximum; raising it back later is additive but a link written against the lower bound
  reads differently in help and `/api/schema`.
- **D-04:** **Single-gear sweep only.** Success Metric 2 asks for a measured number per
  cut at its heaviest configuration; every v0.2 sweep built one gear at a time and this
  one does too. The ten-concurrent scenario the tip-chamfer debt file also asks for is
  not run here; when that file is resolved (D-05) its concurrent-load question is
  re-homed as one added trigger sentence in the existing waived-latency-bar must-debt
  (`docs/tech_debt/active/2026-09-23-concurrent-latency-bar-waived.md`), in the same
  commit, so the question survives (CLAUDE.md: ideas and debt live in files). Rejected:
  one `bench.latency` run with the composed worst row in flight (a second protocol and
  RESULTS.md section for a scenario the milestone did not scope).
- **D-05:** **The two must-debt files whose trigger is this sweep are resolved in the
  sweep's commit:** `2026-09-28-tip-chamfer-narrows-the-build-timeout-margin.md` and
  `2026-09-29-spoke-le-arithmetic-total-crosses-30s-under-load.md` flip to
  `Status: resolved` with the composed row's number and the decision taken (a lowered
  `le`, a raised timeout, or "margin recorded, nothing changed"), carry the commit sha,
  are `git mv`'d to `docs/tech_debt/resolved/` and their `INDEX.md` rows move — per
  CLAUDE.md. If D-03's checkpoint defers a decision, the file stays active with the new
  number and a new trigger instead. Rejected: keeping both active until
  `gsd-complete-milestone` (a second pass over the same numbers).
- **D-06:** **SC3 is amended through the edit-phase tooling in the plan's first task with
  one human confirmation** (08 D-01 / 09 D-20 / 11 D-21's pattern, never a direct write):
  "recess + hex pattern, per the milestone's Success Metric 2" becomes, on the order of,
  "the heaviest combined configuration the composed sweep measures — each cutout pattern
  stacked with the tip chamfer and a recess on the heaviest bore its rules allow — and
  each individual feature". The sentence names no winner before the number exists (L08).
  D-15's SC5 amendment rides the same task.

### The composition matrix
- **D-07:** **Two tiers.** Tier 1, `calc.py` only (microseconds per row, no kernel): the
  full cross product bore {round + chamfer, D-flat, keyed round, hex} × cutout {none,
  spokes, holes, honeycomb} × recess {both, top, none} × tip chamfer {0, on} = 96 rows,
  each asserting either `derive()`'s expected non-null derived fields and warning
  sentences or the expected 422 `ctx.fields`. Tier 2, the kernel: the pairs no existing
  test builds — the tip chamfer **applied** × 3 cutouts × 4 bores (12 rows) and a
  single-sided recess × 3 cutouts (3–6 rows) — about 18 new built rows at 19 teeth on the
  11-08 parameter sets. Rejected: all 96 rows on the kernel (est. +100–150 s on a 178 s
  gate); a kernel matrix outside `make verify` (the gate would not prove composition —
  L13).
- **D-08:** **Every locked refusal × every other family, at the `calc` level.** For each
  refusal (hex × keyway; two cutout patterns; a half-set pattern; the keyway's floor,
  D-flat-wall and width rules; the cutouts' hub, rim and neighbour walls; the hex corner
  and chamfered-mouth rules; the round bore's chamfer reach; the no-cell honeycomb) one
  row per other family switched on, asserting the same sentence and the same `ctx.fields`
  as the refusal alone, plus the order of sentences when two refusals fire on one
  parameter set (Phase 9's "hex first" precedent) — about 40 parametrized rows. One API
  row and one CLI row per refusal prove the 422 / exit-2 routing carries the composed
  sentence through unchanged. Rejected: one composed row per refusal, planner's choice
  (does not prove the sentence is invariant across families, and `calc` rows are free).
- **D-09:** **Each tier-2 row re-runs the feature's own proof helper on the one composed
  solid:** 10-03's `_assert_only_the_tip_arcs_were_chamfered` (CONE faces `+2 × teeth`,
  volume down, `tip_d` unchanged), 11-08's `_assert_the_cutout_is_what_derive_prints` and
  `_assert_the_recess_fillet_survives`, and the selector `Counter`s. "Composes correctly"
  means every single-feature proof still holds when the features share a solid; no new
  proof shape. TORUS / CONE / edge counts on composed rows are **measured on the pinned
  kernel and pinned**, as 11-08 did (no closed form after an arbitrary boolean). Rejected:
  validity and `derive()` parity only (a feature that silently vanished on a composed gear
  would pass).
- **D-10:** **The phase's new tests may add at most 30 s to `make verify`, measured** (07
  D-06's shape: the delta between the phase's start and end on the same host, two
  alternating runs, load recorded, in `bench/RESULTS.md`'s "make verify wall time"
  section). Over the line is a checkpoint with the number — the pre-agreed first offer is
  trimming tier-2 rows to one bore per cutout, never dropping tier 1 or a refusal row.
  Rejected: no line (the gate drifts past four minutes with nobody deciding it); a hard
  ceiling on the whole gate (forces trimming tests outside this phase's scope).

### Interface parity and the UI pass
- **D-11:** **One model-driven parity test plus manual browser UAT.** The test walks
  `GearParams.model_fields` and asserts, for every field: a `group`, `title`, `unit` and
  `step` in `/api/schema` and the group set equal to the eight names {Teeth, Body, Bore,
  Recess, Spokes, Holes, Honeycomb} plus `recess_sides`'s; a `--{name-with-dashes}` flag
  in `cli.py`'s parser; and, on one composed link with every v0.2 family on, `spur info`
  printing `/api/info`'s document byte-for-byte in `DerivedDimensions` key order, and each
  refusal's sentence identical on the API's 422 and the CLI's exit 2. The shareable-URL
  round-trip is proven **statically**: a test reads `static/app.js` and asserts the
  hash → form → query path handles schema properties generically (no per-field code) — the
  browser-test idea's own "cheaper first step". The browser itself is checked by hand at
  `gsd-verify-work` with a recorded checklist (eight fieldsets, the composed link loads
  into the form, the copied link reproduces it). The existing per-feature
  `cli_and_api_print_the_same_*` tests stay. Rejected: funding the first headless-browser
  test now (Node at test time, a new CI job, a slower gate — the idea's open cost
  question, not this phase's); per-feature tests only (a field with a missing group or
  flag is not caught generically).
- **D-12:** **The form stays schema-driven; 08 D-09 stands; the UI pass's verdict on both
  deferred UI ideas is "not taken".** No `app.js` logic beyond `DIMS` rows. Reason: a
  proof-and-measurement phase must not ship the first bore-specific UI logic with no UI
  test. `docs/ideas/2026-09-29-conditional-form-fields.md` and
  `docs/ideas/2026-09-27-bore-shape-selector-in-the-web-form.md` each get a "Judged at
  Phase 12" paragraph and a new trigger: a browser test exists, or a user reports the
  ignored-field warnings as insufficient. If conditional fields are ever taken, the
  schema-driven route is a `json_schema_extra` key (on the order of `enabled_when`) on the
  model, not relations hard-coded in `app.js`. Rejected: conditional form fields now
  (supersedes 08 D-09 with untested UI behaviour); the bore-shape selector (the largest UI
  change of the three; the keyway is a modifier, so it is four-plus-one shapes).
- **D-13:** **The `cli.md` exit-code must-debt is folded in and resolved.**
  `docs/architecture/cli.md` "Errors" is rewritten to the real contract — argparse
  parameter errors exit 2; an unknown output extension and every `BuildError` exit 1
  (`SystemExit` with a string) — and `exc.value.code` asserts land on the extension and
  `BuildError` CLI tests so the doc cannot drift again;
  `docs/tech_debt/active/2026-09-28-cli-md-claims-exit-2-where-cmd-export-exits-1.md`
  is resolved and moved in the same commit. Its trigger ("the Errors section or the
  tests are next touched") fires in this phase. The exit statuses themselves do not
  change (10 D-14's human decision, 2026-09-28). Rejected: leaving it active while the
  parity test asserts statuses the doc contradicts.
- **D-14:** **One composed README example link that the tests run** — every v0.2 family
  on one 19-tooth gear (keyed round bore, one cutout, recess, tip chamfer; exact values
  the planner's, must build) as the "everything on" example and the parity test's input.
  A post-v0.2 set, out of the regression corpus (07 D-05). Rejected: no README change
  (each phase added its own example; the composed one is the point of this phase).

### SC4/SC5 and the close-out record
- **D-15:** **SC5 is amended (with SC3, D-06) to the fixture's real contract:** "every
  pre-v0.2 parameter set still yields identical `DerivedDimensions` and an identical
  solid — volume, bounding box, face and edge counts — after all of v0.2; export bytes
  are not compared (L26)". PROJECT.md Success Metric 3's "identical export" is read the
  same way and L31 says so explicitly. Rejected: leaving SC5 (the roadmap keeps
  contradicting L26 and REQ-defaults-off-regression); pinning export bytes (L24 measured
  OCCT export as not byte-reproducible; the fixture would go red for non-regressions).
- **D-16:** **"The heaviest v0.2 face topology" is the composed-sweep row with the
  largest measured fine STL.** `bench/build_time.py` records fine-STL bytes and triangle
  count per row (a small bench change with a `test_bench` row; the runner stays the same
  for every earlier sweep file), and the largest row is the one L19 and L24 are
  re-measured on. Chosen by a number, not by inspection. Rejected: honeycomb-at-cap by
  inspection (a guess presented as the heaviest if a spoke row's split recess fillet —
  Pitfall 8 — produces more triangles); re-measuring on every composed row (three gzip
  levels and the copy on ~18 rows for one decision).
- **D-17:** **The re-measurement is a committed `bench/` script behind a `make` target**
  (on the order of `bench/export_cost.py`, `make bench.export SET=…`; names the
  planner's): for one parameter set, `gzip.compress` time and output bytes at levels
  1/6/9 single-threaded and under ten concurrent calls (L19's table shape), and fine-STL
  export on `shape.copy()` versus in place with wall time and peak RSS (L24's numbers),
  host state printed, results into a `bench/RESULTS.md` section; a `test_bench` row.
  08 D-12's shape — repeatable; the v0.1 numbers came from one-offs nobody can re-run.
  Rejected: one-off numbers with the command recorded (the next milestone re-derives the
  script).
- **D-18:** **L19's selection rule is applied as written:** adopt a higher gzip level
  only if it shrinks output by ≥ 10 % **and** costs ≤ 1.5× the 10-concurrent wall of the
  level below. If the re-measured table flips it, `_GZIP_LEVEL` changes and L31 cites the
  table (a level change alters no part and no number, only bytes on the wire); if not,
  L19 is annotated with the new row. L24's copy cost is **recorded only** — the copy is a
  correctness decision (a cached solid never carries a mesh), not a cost trade. Rejected:
  record-only regardless (leaves a measured better choice unapplied).
- **D-19:** **One L31, append-only, in L27–L30's shape:** the composed sweep's numbers
  and any `le` or timeout decision, the matrix and its measured verify cost, the parity
  proof, the L19/L24 re-measurement and any `_GZIP_LEVEL` change, the UI-pass verdict
  (08 D-09 stands), the SC3/SC5 amendments and the Success Metric 3 reading — each cited
  to a SUMMARY sha or a `bench/RESULTS.md` section, none re-estimated. Milestone
  bookkeeping (`MILESTONES.md`, the audit) stays `gsd-complete-milestone`'s. Rejected:
  two entries (no precedent in L26–L30).

### Contract and process (carried forward; recorded so the plan carries them)
- **D-20:** **The final fixture pass (SC5):** `tests/regression/pre_v0_2.json` is
  byte-unchanged through the phase and the replay runs unmodified; a new
  `DerivedDimensions` field is not expected this phase, and if one appears the replay's
  null rule covers it (08's rule, L26). The phase-end `make verify` wall time and the
  fixture's share are recorded (D-10).
- **D-21:** **Process.** The phase runs on **`gsd/phase-12-composition-pass`**, cut this
  session from `origin/main` `c9a169d` (PR #12's squash), and lands via
  `make pr.land PR=N` (L22/L25); `.planning/` rides the same PR. Commits are plain
  `git commit` with explicitly staged files, never `git add -A`: the pre-commit hook runs
  `make verify` (~178 s at 621 tests, ~3 min cold) and the gsd SDK commit wrapper kills
  it at 30 s (`docs/tech_debt/active/2026-09-25-gsd-commit-timeout-kills-cold-verify-hook.md`);
  after any wrapper timeout, wait for the orphaned `pre_commit hook-impl` process to
  exit and restore its `state.json` stash before touching tracked files. Run `make
  verify` once at session start. Every ROADMAP/REQUIREMENTS sentence a decision
  supersedes is amended through the edit-phase tooling with one human confirmation
  (D-06, D-15); REQ-measured-build-time and REQ-three-interfaces-extended match D-01…D-14
  as written.

### Claude's Discretion
- **Names:** the composed sweep file, the RESULTS.md section titles, the parity test's
  and matrix tests' names (requirement-shaped, `docs/CODING_VALUES.md`), the export-cost
  script and its `make` target (D-17), the tier-1 table's construction
  (`itertools.product` or written out — whichever reads as a requirement).
- **Sweep-row exactness (D-01):** each row's exact bore — the largest `bore_hex` the
  row's hub rule allows is computed from `bore_mouth_limit` against the cutout's hub
  datum (see `<specifics>`: `bore_hex` 200 conflicts with the recorded spoke and hole
  rows' hub datums); where the heaviest bore forces a different cutout dimension, the
  adjusted row is recorded as its own row beside the unchanged one, never in its place.
  Whether the module-10 spoke row keeps `spoke_fillet` 5. `tip_chamfer` at module 10 is
  whatever `tip_chamfer_limit` returns at that gear.
- **Tier-2 row parameters (D-07):** the 11-08 sets (`HOLES`, `SPOKES12`/`SPOKES13`,
  `CELLS`, `HOLES_ACROSS`) at 19-tooth defaults with `tip_chamfer` at the default gear's
  cap (1.75 mm); whether the keyed D-flat bore (keyway + D-flat + cutout + tip) gets a
  row; whether a composed tripwire (one step patched to a no-op showing the composed
  proof go red) is added beyond the per-feature tripwires that already exist.
- **The parity test's strictness (D-11):** whether it also pins field declaration order
  = form order = CLI order (10 D-10) and the eight group names literally, so a moved
  field fails the test. Recommend yes — the order is a published contract.
- **The composed README link's values (D-14)** and the manual UAT checklist's wording.
- **The idea files' verdict paragraphs and trigger sentences (D-12).**
- **Peak-RSS reading and concurrency harness for D-17** (`resource.getrusage` in a
  subprocess, as `bench/memory.py` reads containers; ten threads as the L19 measurement
  did).
- **Whether `bench/build_time.py`'s new STL columns (D-16) also print the triangle count
  for every earlier sweep file** — they should, since the runner is shared; the earlier
  RESULTS.md sections are not rewritten.
- **The order of plans:** the SC3/SC5 amendment first (D-06, D-15); the sweep before the
  re-measurement (D-16 depends on the sweep's STL sizes); the matrix, parity and `cli.md`
  work independent of both; L31 and the debt resolutions last, citing shas.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements and roadmap
- `.planning/REQUIREMENTS.md` — REQ-measured-build-time, REQ-three-interfaces-extended
  (this phase); REQ-defaults-off-regression, REQ-derived-dimensions-additive,
  REQ-edge-selection-proven, REQ-cutout-composes, REQ-one-cutout-pattern,
  REQ-cutout-conflicts-refused-early, REQ-tip-chamfer-capped (the contracts the matrix
  exercises); "Out of Scope" (the clock-based honeycomb cap, more than one pattern).
- `.planning/ROADMAP.md` "### Phase 12: Composition Pass" — goal, SC1–SC5 (SC3 and SC5
  amended by D-06/D-15), "UI hint: yes", the v0.2 Process Notes.
- `.planning/PROJECT.md` — v0.2 goal and rules; Success Metrics 1–3 (Metric 3 read per
  D-15); Key Decisions L01–L30.

### Decisions
- `docs/architecture/decision_log.md` — L03 (cap vs refuse), L05 (defaults), L08 (no
  plausible numbers), L13 (`make verify` is the gate), L17 (`mem_limit`, its own
  trigger), L18 (the waived concurrent bar — D-04 re-homes a trigger there), **L19** (the
  gzip table and its selection rule — D-17/D-18 re-measure and apply it), L21 (typed
  contract), L22/L25 (merge gate), **L24** (the mesh copy and its measured cost — D-17),
  **L26** (fixture; export bytes not pinned — D-15), L27–L30 (the shape L31 follows; the
  sweep and cap methodology). Append-only; L31 is this phase's.
- `.planning/phases/07-foundation-generalized-edge-selection-regression-fixture/07-CONTEXT.md`
  — D-03/D-05 (fixture policy, corpus sources, post-v0.2 sets stay out), D-06 (the
  measured-cost gate shape D-10 copies), D-15/D-16 (selector guard contract).
- `.planning/phases/08-hex-bore/08-CONTEXT.md` — D-01 (the phase-text amendment pattern),
  D-07 ("in its own group"), **D-09** (schema-driven form, no conditional behaviour —
  stands per D-12), D-11/D-12 (the sweep, `make bench.build`, the over-budget halt).
- `.planning/phases/09-keyway-bore/09-CONTEXT.md` — D-20 (edit-phase tooling for
  amendments), the refusal order precedent ("hex first"), the keyed-bore datums.
- `.planning/phases/10-tooth-tip-chamfer/10-CONTEXT.md` — D-07 (the over-budget
  checkpoint and its first offer), D-12/D-13 (the tip proof helper and the tip column on
  every matrix row), D-14 (exit codes: `BuildError` → exit 1 on the CLI — D-13's
  contract), D-17 (process).
- `.planning/phases/11-body-cutouts/11-CONTEXT.md` — D-11 (the honeycomb's 7.5 s share
  and its lever), D-15…D-17 (the refusals D-08 composes), D-18 (the `le` gate and its
  first offer), D-22/D-23 (process), Claude's Discretion "Sweep rows" (export time
  recorded for this phase), `<deferred>` (the UI ideas, "Phase 12's UI hint should weigh
  it" — D-12's verdict).

### Measurement and its record
- `bench/RESULTS.md` — "### `SPUR_BUILD_TIMEOUT`" (the 4× rationale), the Phase 8–11
  sweep sections (host-state header, table, named heaviest row — D-01's section copies
  them), "Body cutout build and export time (Phase 11)" → "### SPUR_BUILD_TIMEOUT
  margin", "### Gate", "#### Room beside Phase 10's tip-chamfer row" (the arithmetic
  totals this sweep replaces), "### make verify wall time" (D-10's baseline: 621 passed,
  178.55 s wall), "### Post-fix re-run (Runs 5-6)" (L19's provenance).
- `bench/build_time.py`, `bench/sweeps/*.json`, `Makefile` `bench.build` — the runner and
  file shape (D-01, extended per D-16); `bench/latency.py` (the ten-concurrent harness
  D-04 does not run; its host-state conventions), `bench/memory.py` (peak-RSS reading
  precedent for D-17); `tests/test_bench.py` (the sweep-row test shape).
- `src/spur/app.py` lines 167–191 — L19's table and selection rule in the comment above
  `_GZIP_LEVEL = 1`; `_gzip()` at 231.
- `docs/tech_debt/active/2026-09-28-tip-chamfer-narrows-the-build-timeout-margin.md`,
  `docs/tech_debt/active/2026-09-29-spoke-le-arithmetic-total-crosses-30s-under-load.md`
  — the two files D-05 resolves; their "Next step" sections are D-01/D-02's brief.
- `docs/tech_debt/active/2026-09-28-cli-md-claims-exit-2-where-cmd-export-exits-1.md`
  — D-13's brief; `docs/architecture/cli.md` "Errors" (lines 33–36) — the paragraph it
  rewrites.
- `docs/tech_debt/active/2026-09-23-concurrent-latency-bar-waived.md` — receives D-04's
  re-homed trigger.
- `docs/tech_debt/INDEX.md` — rows 27, 28, 30 move to the resolved table.

### UI pass
- `docs/ideas/2026-09-29-conditional-form-fields.md`,
  `docs/ideas/2026-09-27-bore-shape-selector-in-the-web-form.md` — D-12's verdict lands
  in each; `docs/ideas/2026-09-21-browser-test-for-the-viewer.md` — its "cheaper first
  step" is D-11's static check; `docs/ideas/INDEX.md`.
- `src/spur/static/app.js` — the schema-driven group renderer (49–89), the hash read
  (95), query build (102), `history.replaceState` (180), the copy-link path (351–355).

### Process
- `docs/HOW_TO_DEVELOP.md` §2/§4 — the phase branch is cut before discuss-phase and
  reused by execute-phase; `main` only via `make pr.land`.
- `docs/CODING_VALUES.md`, `CLAUDE.md` — comments carry the measurement; `calc.py`
  never imports the kernel; test names read as requirements; debt lifecycle.
- `docs/tech_debt/active/2026-09-25-gsd-commit-timeout-kills-cold-verify-hook.md` — why
  commits are plain `git commit`.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `tests/test_model.py` proof helpers, reused unchanged by D-09:
  `_assert_only_the_tip_arcs_were_chamfered(cut, plain, p, p0)` (705),
  `_assert_the_cutout_is_what_derive_prints(...)` (1142),
  `_assert_the_recess_fillet_survives(cut, p, torus)` (1302); the parameter sets `HOLES`
  / `SPOKES` / `CELLS` (251–253), `HOLES_ACROSS` / `SPOKES12` / `SPOKES13` (1105–1107);
  the matrices `test_every_selector_takes_only_its_own_edges_with_a_body_cutout` (314,
  19 rows) and `test_the_recess_floor_fillet_survives_every_cutout_on_every_bore` (1352,
  13 rows) — the rows tier 2 does **not** repeat; `_stl_triangles` (1403) for D-16's
  triangle count; `_export_in_place` (1441) for D-17's copy-vs-in-place comparison.
- `tests/test_cli.py` `test_cli_and_api_print_the_same_document` (47) and its five
  per-feature siblings (145–277) — the composed-link parity assertion's shape;
  `test_unknown_output_extension_is_refused` (288) and
  `test_a_tip_chamfer_that_selects_no_tip_arcs_stops_the_export_and_writes_nothing`
  (294) — where D-13's `exc.value.code` asserts land.
- `tests/test_api.py` `test_schema_drives_the_form` (58, three properties — D-11
  generalises it), `test_every_key_the_ui_reads_is_a_derived_dimensions_field` (120 —
  the static `app.js` read D-11's round-trip check copies),
  `test_two_cutout_patterns_are_422_naming_both` (467) and the per-feature 422 tests —
  D-08's API routing rows' shape.
- `tests/test_calc.py` refusal tests (e.g. 333 — the "hex first" order test; 888 — two
  patterns) — D-08's calc rows extend them.
- `tests/test_bench.py` (63–269): one test per sweep file asserting the rows are every
  combination the plan names — D-01's sweep gets the same.
- `bench/build_time.py`: `Timing` with `worst_request` (build + slower export),
  `time_set(p)` (76–86: build, `export(p, "stl", "fine")`, `export(p, "step")` — D-16
  adds the STL byte and triangle columns here), `load_sweep`, `main` (123).
- `src/spur/cli.py` 43–60: flags generated from `GearParams.model_fields` — D-11's CLI
  walk reads the same parser; 107/111: the string `SystemExit`s that exit 1 (D-13).
- `src/spur/params.py` `_f(...)` (17) and the 30 fields in eight groups (29 `_f` fields +
  `recess_sides`) — D-11's walk.
- `tests/regression/test_pre_v0_2.py` (42–61) — the replay D-20 runs unchanged.

### Established Patterns
- A number is measured on the pinned kernel via a committed script and `make` target,
  recorded in `bench/RESULTS.md` with host state and load, cited in the `Lxx` entry — never
  re-estimated (08 D-12, L27–L30). Rows over budget are recorded as measured, never
  dropped or re-run to green (11-06).
- A gate cost is measured as a same-host delta with alternating runs and a pre-agreed
  line; over the line is a human checkpoint (07 D-06).
- Phase texts are amended only through the edit-phase tooling with one human
  confirmation (08 D-01, 09 D-20, 11 D-21).
- Debt is resolved in the fixing commit: status flipped, sha recorded, `git mv`, INDEX
  row moved (CLAUDE.md).
- A proof reuses the feature's own helper; a tripwire shows it going red (Phases 7, 10,
  11).
- `calc.py` never imports `cadquery`; `derive()` runs on every keystroke — tier 1 is free.

### Integration Points
- `bench/sweeps/<composed>.json`, `bench/build_time.py` (STL columns),
  `bench/<export_cost>.py`, `Makefile` (`bench.export`), `bench/RESULTS.md` (two new
  sections + the verify wall-time row), `tests/test_bench.py`.
- `tests/test_calc.py` (tier 1 + refusal composition), `tests/test_model.py` (tier 2),
  `tests/test_api.py` / `tests/test_cli.py` (parity test, routing rows, status asserts).
- `src/spur/app.py` `_GZIP_LEVEL` — only if D-18's rule flips.
- `docs/architecture/cli.md` "Errors"; `README.md` (one composed link);
  `docs/architecture/decision_log.md` (L31); `docs/tech_debt/{active,resolved}/`, its
  `INDEX.md`; `docs/ideas/` (two verdict paragraphs).
- `.planning/ROADMAP.md` Phase 12 SC3/SC5 via edit-phase tooling.

</code_context>

<specifics>
## Specific Ideas

Numbers on record (single-feature, one gear at a time, `bench/RESULTS.md`): hex 5.08 s;
keyway 4.85 s; tip chamfer 14.87 s (200 teeth, module 1.75, `c` 1.75, recess both);
holes at `le` 60 11.79 s; spokes at `le` 40 18.52 s (module 10, `spoke_width` 0.4,
`hub_d` 52, `rim_wall` 0.4, `spoke_fillet` 5, recess both, load 32.17); honeycomb at the
cap 8.65 s (module 1.75, `hex_cell` 3, `hex_wall` 0.4, recess both). Arithmetic totals
with the tip-chamfer row: spokes 33.39 s, holes 26.66 s, honeycomb 23.52 s — sums, not
builds; this sweep replaces them.

Arithmetic on the parameter model only — **no kernel probe was run this session**:

- **`bore_hex` 200 does not fit the recorded spoke or hole rows' hub datums.** A hex of
  200 mm A/F has its corner at 115.47 mm radius (`bore_mouth_limit` ≈ 115.9 mm with the
  0.4 mm chamfer); the spoke row's `hub_d` 52 puts the hub ring at 26 mm and the module-
  1.75 hole row's inner hole edge (`hole_circle_d` 183.4, `hole_d` 1) at 91.2 mm — both
  a 422 naming the hub field. "The heaviest bore the row's hub rule allows" (D-01) is
  therefore computed per row: the largest `bore_hex` whose `bore_mouth_limit + MIN_WALL`
  clears the cutout's hub datum, or the cutout re-sized to clear a large hex, recorded as
  a separate row (Claude's Discretion). At module 10 and 200 teeth the root radius is
  ~987.5 mm, so a 200 mm hex and a 52 mm hub coexist only if the hub moves out.
- **The keyed round bore** composes with every cutout at the recorded rows unchanged
  (`bore_d` 9 default; the keyway's floor corner is the hub datum, ~6.2 mm on the
  default bore).
- **Tier-2 rows at 19 teeth:** the default gear's tip cap is 1.75 mm (D-02 of Phase 10);
  the 11-08 sets already clear every wall rule on the D-flat, round, hex-6 and keyed
  bores. Expected CONE faces `+38`, TORUS counts as pinned in 11-08's matrix (4 / 14 /
  20 / 40 / 12 by row) — **to be re-measured with the tip chamfer applied and pinned**,
  not assumed to hold.
- **L19's table** was measured on a 9,062,784-byte fine STL (`teeth=199`, no v0.2
  feature; 2,632,467 bytes at level 1 in 51.5 ms). The composed rows' fine STLs are
  expected larger (the split recess fillet, many small cutout faces) — the size D-16
  reads decides which row, not this expectation.
- **L24's copy cost** was +1.4 to +17.6 ms and +3.2 to +7.7 MiB peak RSS on a 200-tooth
  fine export (planning measurement, load 3.5–5.0).
- **`make verify` baseline:** 621 passed, 177.62 s pytest, 178.55 s wall at Phase 11's
  end (load 3.07–4.65). D-10's line is +30 s over the phase-start reading on the same
  host, not over this figure.

</specifics>

<deferred>
## Deferred Ideas

- **A headless-browser test for the form and viewer** — the idea stands
  (`docs/ideas/2026-09-21-browser-test-for-the-viewer.md`); D-11 takes its "cheaper
  first step" (a static schema→form contract check) and leaves the cost question open.
  Its trigger gains: "either UI idea below is taken".
- **Conditional form fields ("disabled when")** and **a bore-shape selector in the web
  form** — judged at this phase's UI pass and not taken (D-12); their files record the
  verdict and the new trigger. If taken later, the schema-driven route is a
  `json_schema_extra` key on the model, superseding 08 D-09 with a new `Lxx`.
- **The composed worst row under ten concurrent builds** — not run (D-04); the question
  moves into `2026-09-23-concurrent-latency-bar-waived.md`'s triggers when the
  tip-chamfer debt file is resolved.
- **L17's `mem_limit: 4g` re-swept on v0.2 topology** — the N=2 sweep ran on v0.1
  topology; a composed 200-tooth gear's peak RSS is unmeasured. Not this phase's (SC4
  names L19 and L24 only); a candidate for the milestone audit's debt list, with
  D-17's peak-RSS reading as the cheap first look.
- **Refreshing `.planning/codebase/*.md`** — the maps are dated 2026-09-21 and predate
  `bench/` and Phases 7–11 (`STATE.md` "Operator Next Steps" carries
  `/gsd-map-codebase --paths bench`). Process, not product; recommended before
  `gsd-plan-phase 12` so the pattern mapper reads current files.
- **Adding STL triangle counts to the earlier sweep sections** — D-16's columns print for
  every sweep file; the earlier RESULTS.md sections are not rewritten (history).

No scope creep surfaced during discussion — nothing else deferred.

</deferred>

---

*Phase: 12-composition-pass*
*Context gathered: 2026-09-29*
