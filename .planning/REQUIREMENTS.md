# Requirements: spur — milestone v0.4 True Root

**Defined:** 2026-10-06
**Core Value:** A number this tool prints is a number someone will cut metal to — every
dimension is computed honestly or reported as a warning, never guessed (L08).

Scope fixed in `PROJECT.md` ("Current Milestone: v0.4 True Root"). Research pass:
`.planning/research/SUMMARY.md` is the entry point; its "Corrections to the brief and
disagreements between files" table is authoritative over any single research file, and
every figure quoted below carries the file that measured it. The choices the human took at
kickoff (2026-10-06) are baked into the wording: the two `must` debt items **first**, the
hook decision **before** any geometry commit; the trochoid **landed dark or opt-in**, the
root mode **decided at discuss-phase with both options priced**; helical is v0.5.

REQ-IDs continue the project's `REQ-slug` convention (`milestones/v0.3-REQUIREMENTS.md`).

## Rules every requirement lives by

- **Same part until a logged flip.** `tests/regression/pre_v0_2.json` (44 records, 85 cases,
  `warnings` included) stays byte-unchanged and green through every commit of this
  milestone except one: if the human chooses an always-on root mode, exactly one flip
  commit carries the predicate change, the `make fixture.regen` output and a new `Lxx` that
  names the moving records in advance (L26 D-03). A feature commit never touches it; a
  red replay in a feature commit is a bug, not a reason to regenerate.
- **A parameter the user did not set never silently changes the part** (L05). Any new
  `GearParams` field defaults off, is a `Literal` or a number — never a `bool` on the CLI —
  and reaches the web form and the CLI from the one model.
- **Measured, never tuned** (L08). Every bar is set from two recorded numbers with the
  headroom stated; the oracle shares no code with the implementation; a tripwire proves
  each bar load-bearing. No external reference table exists (STACK), so the proof is built
  and its provenance recorded.
- **Retired in the fixing commit.** A debt file flips `Status: resolved`, gains the sha, is
  `git mv`'d into `docs/tech_debt/resolved/` and its INDEX row moves — in the same commit as
  the fix (CLAUDE.md). The race debt names two findings (the race and the margin): it
  retires on the commit that closes both.
- **Phases land as PRs** on `gsd/phase-NN-*` through `make pr.land PR=N` (L22/L25);
  `.planning/` rides the same PR. Until REQ-hook-and-commit-timeout-decided lands, every
  commit is a plain `git commit` with the hook allowed to finish: a killed SDK commit leaves
  the hook running as an orphan (PITFALLS 15).
- **No new dependency**, runtime or dev: stdlib `math` for the trochoid (STACK); scipy is
  pruned from the image and numpy costs +33 ms / +11 MiB in the kernel-free parent.

## v0.4 Requirements

### Debt — the two `must` items (first)

- [ ] **REQ-hook-and-commit-timeout-decided**: One logged `Lxx` settles how the pre-commit
  `make verify` hook (~64 s warm, L34) coexists with gsd's hard-coded 30 s commit timeout
  (`COMMIT_TIMEOUT_MS` in `gsd-core` 1.16.0 `commands.cjs`; no knob, no open upstream
  request — STACK). The options the human picks from at discuss-phase, each priced:
  (a) an upstream request, nothing shipped, commits stay by hand; (b) the full gate moves to
  a `pre-push` hook; (c) a sub-30 s pre-commit subset — static-only (`lint typecheck
  lint-imports no-fake-done`: 0.57 s warm / ≈9.5 s cold, ARCHITECTURE and PITFALLS) or with
  a pytest slice (617 tests `-n 8 --no-cov`: ≈12 s warm / ≈21 s cold, STACK); or (b)+(c).
  Whatever subset exists is a Makefile target that `verify` depends on, so it is a prefix of
  the gate by construction, never a second list. L13's "one definition of passing in three
  places" and L34 are amended by the `Lxx`, not contradicted. *Acceptance*: one live
  `gsd_run query commit` on this repository with the hooks installed returns
  `committed: true` and the commit exists; pre-push semantics (once per push, first ref,
  stash of unstaged changes, per-clone `pre-commit install`) verified in a scratch repo and
  recorded; every place that says "the pre-commit hook runs `make verify`" says the new
  truth (`.pre-commit-config.yaml` header, `docs/HOW_TO_DEVELOP.md` §0, `README.md`,
  `docs/architecture/packaging.md`, the `ci.yml` comment, `scripts/pr_land.py`'s stale
  "~42 s" comment); `docs/tech_debt/active/2026-09-25-gsd-commit-timeout-kills-cold-verify-hook.md`
  retires with the sha.
- [ ] **REQ-same-slot-timeout-race-reproduced**: Phase 13's deferred ten-identical-worst-row
  scenario lands in `bench/latency.py`'s `_SCENARIOS` (not the default set), reading the
  composed worst row, with a `record_500` keyword so the default `_fetch` and the test that
  pins its 500-raising stay as they are; `tests/test_bench.py`'s registry assertion updated.
  Run once against a fresh server with shipping defaults **before** the fix. *Acceptance*:
  `bench/RESULTS.md` records the per-request table (parameters, outcome, wall time) with the
  undocumented 500 visible, host state and load as every section has.
- [ ] **REQ-same-slot-timeout-race-fixed**: `_run_with_timeout`'s `except TimeoutError`
  branch terminates and replaces an executor only when **both** hold: its `executor` local
  is still the live slot's (`self.executor_for(p) is executor`) **and** `_processes is not
  None`; `BuildPool.shutdown()` sets a `_closed` flag that `recreate_for` honours, closing
  the second route PITFALLS 9 found. A second same-slot timeout raises `BuildTimeout` — the
  documented `503 timeout` — never `AttributeError`. No `await` is added inside the
  terminate-and-replace block (`BuildPool` holds no lock; atomicity rests on the one
  event-loop thread); when the timeout clock starts, `SPUR_BUILD_TIMEOUT` and
  `MAX_QUEUED_BUILDS` are untouched. *Acceptance*: a deterministic stale-executor test in
  `tests/test_pool.py` seen red before the fix and green after; a same-tick sibling test
  accepting `BuildTimeout` or `BrokenProcessPool` for the sibling (both documented 503s);
  the existing 0.5 s-gap test unchanged; both new tests run repeatedly under `-n 8 --cov`
  and `-n 4` with the counts recorded; the scenario re-run after the fix shows zero 500s;
  the debt file retires in the commit that also closes REQ-worst-row-margin-decided.
- [ ] **REQ-worst-row-margin-decided**: The composed worst row (29.42 s alone, Phase 12)
  not finishing inside 30 s under ten concurrent builds gets a logged `Lxx`: raise
  `SPUR_BUILD_TIMEOUT`, lower a cap (`spoke_count`'s `le`, say), or record the limit as a
  documented behaviour — chosen from a measurement, never tuned toward a pass. *Acceptance*:
  `bench/RESULTS.md` and the resolved tip-chamfer debt file's "~1.02x" headline are
  amended by a dated note; the choice names the number that set it.

### Trochoid maths — `calc.py` only, no kernel, no field, no fixture contact

- [ ] **REQ-cutter-defined-once**: One pure `calc` function defines the basic rack cutter —
  dedendum 1.25·m (what `rf = r − m(1.25 − x)` already encodes), tip radius ρ, backlash as
  cutter-tooth thickening, profile shift — and every other function reads it. ρ is capped
  to the pressure angle's geometric maximum **with backlash included** (ISO 53's 0.38·m fits
  only to ≈23.2°; at the default 25° the cap is ≈0.318·m at zero backlash — STACK, FEATURES;
  PITFALLS' 0.363·m at m 1.75 is to be reconciled by the first test), warned when trimmed
  (L03); `ρ = 0` is legal (sharp cutter, deepest cusp). Above the pressure angle where the
  1.25·m rack has no tip land (≈32.1°, `tan α = π/(4·1.25)`) the trochoid is not computed:
  a warning and the shipped analytic root as the explicit fallback (L08). *Acceptance*: the
  cutter's junction with the involute equals `Profile.half_angle` at backlash 0 and 0.10
  (PITFALLS measured 4.9e-17 rad; the bar is re-measured in the phase); the cap and the
  domain limit each tested one step either side.
- [ ] **REQ-trochoid-root-generated**: `calc.trochoid_root` returns an immutable `RootCurve`
  of `(radius, half_angle)` pairs — the envelope of the cutter tip arc, not its centre path —
  or `None` with a warning when it cannot be computed honestly. The junction with the
  involute is tangent when not undercut and a crossing when undercut, found by bisection on a
  monotone bracket only after a closed-form sign test says a crossing exists (STACK: the
  radius bracket collapses within ≈1e-7 mm of roll of the base circle); the double root at
  `z_min` has an explicit rule; `Profile.half_angle` is never reused below `rb`. Pure stdlib
  `math`; no numpy or scipy anywhere under `src/spur/`. *Acceptance*: the generator's own
  sweep over the allowed parameter space (STACK's 7,296 cases as the floor) reports zero
  bracket failures and monotone radius on every curve; `derive()`'s per-call cost is
  re-measured and its docstring figure corrected (PITFALLS: 73 µs with a 60-step bisection
  vs 20.4 µs today, host load ≈6.8; the 11.5 µs in the docstring is stale).
- [ ] **REQ-root-mode-single-predicate**: One predicate, `calc.root_mode(p, pr)`, decides
  whether the trochoid applies to a given gear, and `_outline`, `root_fillet`,
  `spline_start`, `tip_chamfer_limit` and `derive` all read it — the three things called
  "undercut" today (`teeth < z_min`: 5 of 44 fixture records; `rb > rf`: 28 of 44, the
  default gear included; the cutter's form circle) are never mixed. *Acceptance*: the
  predicate is tested one tooth step either side and, at a tuned profile shift, one field
  step either side (the L33 pattern); the step discontinuity at the undercut threshold
  (FEATURES: ≈0.14·m of root shape between 17 and 18 teeth at 20°) is measured and shown to
  the human with the root-mode options.
- [ ] **REQ-trochoid-proved-independently**: The proof lives in `tests/`, shares no code with
  the implementation (the L33 `_filleted_spoke_volume` precedent), and runs at the calc
  tier: T1 the closed-form undercut onset pins *when* the root is a trochoid; T2 a
  swept-cutter no-gouge oracle pins *where* it is — every surviving point clears the cutter
  at every other rolling angle (STACK: −1.6e-11 mm on the genuine segment vs +3.9e-3 mm past
  the form point); T3 a one-off cross-check against freecad.gears at ρ = 0, recorded with
  source file, commit and licence (GPL-3.0, never imported, never vendored). A tripwire
  moves ρ by a stated amount and proves the assertion goes red. *Acceptance*: each bar is
  set from two recorded numbers (the model's own spline error and the reference's stated
  resolution) with the headroom stated, and goes to the human if under about 10× (the L33
  D-06 rule); a published or tool-generated reference, if the human can supply one, is
  added as T4 with its stated precision and cutter assumptions.
- [ ] **REQ-undercut-warning-restated**: `derive()`'s undercut warning comes from the same
  cutter constants as the geometry (the shipped `z_min = 2(1−x)/sin²α` matches the rack
  model only at 20° — STACK: 31.903 vs 30.791 at 14.5°, 11.198 vs 11.540 at 25°), no longer
  says "radial root", and prints `x_min`, the profile shift that avoids undercut (closed
  form), beside it. *Acceptance*: in radial mode the five fixture records that carry the old
  text (`pre_v0_2.json:582,632,948,996,1588`) stay byte-identical — the restated sentence
  applies only where the predicate says the trochoid does; the new onset is proved against
  the cutter actually used, or the old sentence stays.

### Trochoid in the part — kernel integration, landed dark or opt-in

- [ ] **REQ-root-mode-decided**: The human's root-mode choice is logged as an `Lxx` that
  supersedes L10 and amends L09 and L33, picked from the priced table: O1 always-on when
  undercut (5 of 44 records move, discontinuous at the threshold); O2 always-on wherever
  `rb > rf` (28 of 44 move, the default gear by up to ≈0.30 mm of root material — FEATURES
  simulation); O3 a new default-off `Literal` field (0 move; name decided at discuss-phase);
  O4 O3 now, the flip later under its own `Lxx`. Under O3/O4 the field is a `Literal`, never
  a `bool` (`cli.py` reads `--flag false` as true), reaches the web form and the CLI from
  the model, and the enum exemption in the field-walk test is generalised. *Acceptance*:
  `git diff --exit-code tests/regression/pre_v0_2.json` after every task of every phase,
  except the one flip commit (O1/O2/O4-flip) that carries the predicate change, the
  regeneration and the `Lxx` listing the moving records in advance (ARCHITECTURE under O1:
  5 `derived` blocks, 3 `solid` blocks, one added null field in the other 39); any other
  record moving is a bug.
- [ ] **REQ-outline-consumes-root-curve**: `model._outline` replaces the fillet arc plus
  lead-in line, per tooth side, with one `makeSpline` through `RootCurve`, and the involute
  spline starts at the junction radius taken from the same float (a 1e-6 mm gap silently
  opens the wire — PITFALLS). Structural guards that do not depend on `isValid()`:
  coincident junction vectors, a spacing-ratio check, annulus bounds, a closed-form area
  check (PITFALLS: a valid face with volume 347.9 against 21.4 from a 538 mm spline swing).
  *Acceptance*: `root_d == 2·rf` asserted in both root modes; a kernel-tier proof compares
  `Edge.positionAt` samples of the built solid's root edge to the oracle at a bar set from
  the measured gap (STACK's N = 16 uniform-in-roll sampling, 3.6–4.0e-5 mm, is the starting
  point; the two files' spline-deviation methods are reconciled before a bar is set); the
  trochoid generator never enters `model.py`.
- [ ] **REQ-derived-numbers-honest-under-trochoid**: Where the trochoid applies,
  `root_thickness` and `root_gap` are either null with a warning or redefined at the form
  circle with that circle printed (decided at discuss-phase; FEATURES: the default gear's
  printed 3.253 mm against a true 4.68 mm at rf + 0.001·m); `root_form_d` is printed only if
  the oracle proves it, labelled as the cutter-envelope junction and never as ISO 21771
  parity; the undercut waist thickness is printed with a floor — a `422` (L03) or a warning,
  decided at discuss-phase (FEATURES: 0.021·m at 6 teeth, 14.5°, x = −0.6); the L33 lead-in
  warning does not fire when no chord exists. *Acceptance*: `DerivedDimensions` grows
  additively, new fields null on fixture replay; every printed number has a proof or a
  warning, none a plausible value (L08).
- [ ] **REQ-cutter-tip-radius-settable**: The cutter tip radius is an explicit, printed,
  capped input — either `root_fillet` reinterpreted as ρ in trochoid mode (its changed
  meaning documented, and where it is ignored a warning, the L27 hex-bore precedent) or a
  new default-off field — the human's call at discuss-phase; the default stays absolute
  millimetres (L05; 0.5 mm is 0.286·m at m 1.75 but 0.05·m at m 10 — FEATURES). *Acceptance*:
  the value actually used is in `DerivedDimensions` at 3 dp; the web form and the CLI expose
  it from the model; a trimmed value warns with the cap.
- [ ] **REQ-trochoid-composes-and-is-priced**: The trochoid root composes with the tip
  chamfer (`tip_chamfer_limit` follows the form radius; L29's kernel boundary re-bisected
  across the spline-to-spline junction, which is spiked before any schema change), face
  recesses and each cutout pattern; build time is measured at the heaviest allowed low-tooth
  row against `SPUR_BUILD_TIMEOUT` and recorded in `bench/`; `make verify`'s cost is
  recorded against the 66 s bar (L34) with the kernel-tier rows priced; three-interface
  parity is proved the way Phase 12 did (model-driven field walk, byte-identical composed
  document, identically routed refusals). *Acceptance*: every composed row inside the
  timeout; README's geometry notes, `docs/architecture/gear-maths/`, the solid-model docs
  and `docs/ideas/2026-09-21-trochoidal-root-fillets.md` brought true in the same change.

## Future Requirements

Deferred deliberately; recorded so they survive this session.

### Gear family (v0.5 candidate, one type per phase)

- Helical first — re-derives module, span and centre distance, the riskiest surface in
  the product; needs its own research pass.
- Internal / ring gears; rack (a second parameter model).
- Bevel — needs a product-scope decision first (contradicts "involute spur gear generator").

### Trochoid follow-ups (v0.4.x)

- Flipping the default root mode to the hob root, if O3 is chosen now (own `Lxx`, own
  commit, the moving records named in advance).
- Mate interference checked against the form diameter; ISO 6336-3 critical section
  (geometry only, no stress numbers); an editable dedendum (needs an L05 decision).

### Deferred `nice` debt (external triggers, not fired)

- Server-side request cancellation; no built-in authentication; Enji Guard / CVE alerting;
  the eleven composed cutout literals at `rel=1e-6`; the sometimes-lost worker-coverage
  flush and the resource-tracker flake (both fire a *read* when `pool.py` is edited — the
  race phase schedules it); Phase 7's Manual-Only Nyquist rows; `Resolved in:` shas on
  squashed branches; the English-throughout check.

## Out of Scope

| Feature | Reason |
|---------|--------|
| Helical / internal / rack / bevel | Deferred at v0.2, v0.3 and again here; v0.5 candidates, bevel needs a product-scope decision |
| Automatic profile shift (BOSL2's default) | Anti-feature: an unset parameter would change the part (L05) |
| A circular-arc root sold as a trochoid | Anti-feature: the number printed would not be the number cut (L08) |
| Bending-stress or ISO 6336 strength numbers | Geometry generator, not a rating tool; every such number would need the standard cited and verified |
| Vendoring or importing freecad.gears | GPL-3.0; used once as a recorded cross-check, never a dependency |
| numpy or scipy in `src/spur/` | scipy is pruned from the image; numpy costs +33 ms / +11 MiB in the kernel-free parent with no measured gain (STACK) |
| Patching `~/.claude/gsd-core` for the commit timeout | Outside the repo and overwritten by `gsd-update`; the upstream request is filed in parallel, not depended on |
| Changing when the build timeout clock starts, `SPUR_BUILD_TIMEOUT`'s meaning or `MAX_QUEUED_BUILDS` in the race fix | The fix is the two-fact guard plus `_closed`; the margin is its own logged decision |
| An outline change that keeps the root lead-in below the active profile's start | The path L33 did not take; revisit only if that warning fires on gears people cut |
| Widening the fixture's bars to absorb a root change | A flip is one logged commit that names what moved, never a loosened tolerance (L26) |

## Traceability

Filled by the roadmap, 2026-10-06 (`ROADMAP.md`: Phases 17–20). Each requirement sits in
the phase where its acceptance can be read.

| Requirement | Phase | Status |
|-------------|-------|--------|
| REQ-hook-and-commit-timeout-decided | Phase 17 | Pending |
| REQ-same-slot-timeout-race-reproduced | Phase 17 | Pending |
| REQ-same-slot-timeout-race-fixed | Phase 17 | Pending |
| REQ-worst-row-margin-decided | Phase 17 | Pending |
| REQ-cutter-defined-once | Phase 18 | Pending |
| REQ-trochoid-root-generated | Phase 18 | Pending |
| REQ-root-mode-single-predicate | Phase 18 | Pending |
| REQ-trochoid-proved-independently | Phase 18 | Pending |
| REQ-undercut-warning-restated | Phase 19 | Pending |
| REQ-root-mode-decided | Phase 19 | Pending |
| REQ-outline-consumes-root-curve | Phase 19 | Pending |
| REQ-derived-numbers-honest-under-trochoid | Phase 19 | Pending |
| REQ-cutter-tip-radius-settable | Phase 19 | Pending |
| REQ-trochoid-composes-and-is-priced | Phase 19 | Pending |

**Placement notes** (where a requirement's phase is not the one its text first suggests):
- REQ-root-mode-decided: the choice is *taken* at Phase 18's discuss-phase (it fixes the
  predicate's body), but the requirement sits in Phase 19, where its `Lxx`, the field on the
  form and CLI, and the fixture `git diff --exit-code` can be read. It is not in conditional
  Phase 20, so skipping that phase orphans nothing; Phase 20 (the flip) carries only the flip
  clause of this requirement and has none of its own.
- REQ-undercut-warning-restated: Phase 18 supplies the closed-form onset and `x_min`; the
  requirement sits in Phase 19 because the restated sentence applies only where the predicate
  says the trochoid does, and nothing can ask for the trochoid before Phase 19.
- REQ-root-mode-single-predicate: written and tested in Phase 18; its consumers (`_outline`,
  `root_fillet`, `spline_start`, `tip_chamfer_limit`, `derive`) are wired to it in Phase 19.

**Coverage:**
- v0.4 requirements: 14 total
- Mapped to phases: 14 (Phase 17: 4, Phase 18: 4, Phase 19: 6, Phase 20: none of its own)
- Unmapped: 0 ✓
- Duplicates: 0 ✓ (each requirement appears in exactly one phase)

---
*Requirements defined: 2026-10-06*
*Last updated: 2026-10-06 after the roadmap filled the traceability table*
