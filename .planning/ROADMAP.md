# Roadmap: spur

## Milestones

- ✅ **v0.1 Hardening** — Phases 1–6 (shipped 2026-09-25) — full detail in
  `milestones/v0.1-ROADMAP.md`, audit in `milestones/v0.1-MILESTONE-AUDIT.md`
- ✅ **v0.2 Fit to Shaft** — Phases 7–12 (shipped 2026-10-01) — full detail in
  `milestones/v0.2-ROADMAP.md`, audit in `milestones/v0.2-MILESTONE-AUDIT.md`
- ✅ **v0.3 Clean Ledger** — Phases 13–16 (shipped 2026-10-05) — full detail in
  `milestones/v0.3-ROADMAP.md`, audit in `milestones/v0.3-MILESTONE-AUDIT.md`
- 🚧 **v0.4 True Root** — Phases 17–20 (in progress; Phase 20 is conditional on the
  root-mode decision)

## Phases

**Phase Numbering:**

- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)
- Numbering continues across milestones — the next milestone starts at Phase 21 (Phase 20
  keeps its number even if it is skipped).

<details>
<summary>✅ v0.1 Hardening (Phases 1–6) — SHIPPED 2026-09-25</summary>

- [x] Phase 1: v0 Baseline (Shipped) (no plans — built and verified directly against `make verify` before GSD)
- [x] Phase 2: CAD Off the Event Loop (5/5 plans) — completed 2026-09-24
- [x] Phase 3: Structured Logging at the Composition Boundary (3/3 plans) — completed 2026-09-24
- [x] Phase 4: Typed Derived-Dimensions Contract (3/3 plans) — completed 2026-09-24
- [x] Phase 5: CI Observed Green (6/6 plans) — completed 2026-09-25
- [x] Phase 6: Address tech debt: merge gate + solid cache (4/4 plans) — completed 2026-09-25 (added 2026-09-25 after the Phase 5 review and the first milestone audit)

Goals, success criteria and plan lists: `milestones/v0.1-ROADMAP.md`. Phase artifacts:
`milestones/v0.1-phases/`. Quick tasks: `milestones/v0.1-quick/`.

</details>

<details>
<summary>✅ v0.2 Fit to Shaft (Phases 7–12) — SHIPPED 2026-10-01</summary>

**Milestone Goal:** A generated gear mounts on a real shaft and prints light — new bore
profiles, body cutouts and a tooth-tip chamfer, all additive on the shipped spur pipeline,
with tooth measurements untouched.

- [x] Phase 7: Foundation — Generalized Edge Selection + Regression Fixture (2/2 plans) — completed 2026-09-26
- [x] Phase 8: Hex Bore (4/4 plans) — completed 2026-09-26
- [x] Phase 9: Keyway Bore (5/5 plans) — completed 2026-09-27
- [x] Phase 10: Tooth-Tip Chamfer (5/5 plans) — completed 2026-09-28
- [x] Phase 11: Body Cutouts (9/9 plans) — completed 2026-09-29
- [x] Phase 12: Composition Pass (9/9 plans) — completed 2026-09-30 (re-verified 2026-10-01 after the review fixes)

Goals, success criteria and plan lists: `milestones/v0.2-ROADMAP.md`. Phase artifacts:
`milestones/v0.2-phases/`. Decisions: L26–L31 in `docs/architecture/decision_log.md`.
Landed as PRs #7–#13 through `make pr.land`; the close is its own PR.

</details>

<details>
<summary>✅ v0.3 Clean Ledger (Phases 13–16) — SHIPPED 2026-10-05</summary>

**Milestone Goal:** Every `must` debt item retired by measurement or a logged decision,
every false claim in the record made true or warned, and the gate itself measured — no new
user-facing geometry, no new `GearParams` field, the 44-record pre-v0.2 fixture
byte-unchanged throughout.

- [x] Phase 13: Latency Bar (7/7 plans; 13-05 not executed by design — outcome (a)) — completed 2026-10-02
- [x] Phase 14: Honest Record (4/4 plans; 14-04 a gap-closure plan after UAT) — completed 2026-10-03
- [x] Phase 15: The Gate, Measured and Pinned (6/6 plans) — completed 2026-10-04
- [x] Phase 16: Typing & Validation Debt (3/3 plans) — completed 2026-10-05

Goals, success criteria and plan lists: `milestones/v0.3-ROADMAP.md`. Phase artifacts:
`milestones/v0.3-phases/`. Decisions: L32–L35 in `docs/architecture/decision_log.md`.
Landed as PRs #16–#19 through `make pr.land` after the start PR #15; the close is its own
PR. Outcome against PROJECT.md's three success metrics: 2 and 3 met; 1 ("zero `must` rows")
not met as written — the four `must` rows the milestone was scoped on are retired, and the
one `must` Phase 13 itself filed (the same-slot timeout race, D-17) stays active with its
trigger (`milestones/v0.3-MILESTONE-AUDIT.md`).

</details>

### 🚧 v0.4 True Root (In Progress)

**Milestone Goal:** Retire the last two `must` items — the same-slot timeout race by a
measured reproduction and a narrow fix, the commit-timeout gap by a logged decision — then
replace the radial root below the base circle with the trochoid a hob cuts, proven against
an independent oracle, with the fixture rule (L26) honoured under its own `Lxx`, never
bypassed.

- [x] **Phase 17: Debt First — Commit Gate and Pool Race** - The hook-versus-commit-timeout (completed 2026-10-06)
      conflict gets a logged decision that a live SDK commit proves; the same-slot timeout
      race is reproduced, fixed and ends as a documented `503`; the worst composed row's
      margin gets a logged decision
- [x] **Phase 18: Trochoid Maths, Proved** - The hob's trochoid root exists as pure `calc.py` (completed 2026-10-08)
      maths — the cutter defined once, the curve generated or honestly refused, one
      predicate, an independent oracle — with no kernel, no field and no fixture contact
- [ ] **Phase 19: The Trochoid in the Part** - The outline consumes the proven curve, every
      number printed beside it is proved or warned, it composes with every shipped feature
      inside the timeout, and no part a shared link produces today changes
- [ ] **Phase 20: The Flip (conditional)** - Only if the root-mode decision makes the hob
      root a default: one commit carries the predicate change, the regenerated fixture and
      the `Lxx` that named the moving records first; otherwise recorded as skipped

## Phase Details

### Phase 17: Debt First — Commit Gate and Pool Race

**Goal**: The two `must` debt items are closed by a decision and a measurement, not by a
workaround — an SDK commit completes on this repository, a second same-slot timeout ends as
the documented `503 timeout` instead of an undocumented `500`, and the worst composed row's
margin under contention has a logged answer — so every later commit of the milestone runs
under a settled hook.
**Depends on**: Nothing new — builds on the shipped v0.1–v0.3 pipeline (Phases 1–16). The
order inside the phase is fixed: the hook decision first (the human's "hook decision before
any geometry commit"), then the race reproduced and fixed, then the margin decision, which
closes the race debt file together with the fix.
**Requirements**: REQ-hook-and-commit-timeout-decided, REQ-same-slot-timeout-race-reproduced,
REQ-same-slot-timeout-race-fixed, REQ-worst-row-margin-decided
**Success Criteria** (what must be TRUE):

  1. One live `gsd_run query commit` on this repository, with the hooks installed, returns
     `committed: true` and the commit is in `git log` — inside the SDK's 30 s, with nobody
     committing by hand. If the choice includes a pre-commit subset, it is a Makefile target
     that `verify` depends on (visible in `make -n verify`), never a second list. Option (a)
     alone (an upstream request, nothing shipped) cannot meet this criterion: choosing it at
     discuss-phase means amending the criterion with the human, not passing it by
     hand-commit.
  2. The decision is one new `Lxx` that amends L13 and L34 by appending; every place that
     says the pre-commit hook runs `make verify` says the new truth (`.pre-commit-config.yaml`
     header, `docs/HOW_TO_DEVELOP.md` §0, `README.md`, `docs/architecture/packaging.md`, the
     `ci.yml` comment, `scripts/pr_land.py`'s stale "~42 s" comment); if a pre-push hook is
     part of the choice, its semantics (once per push, first ref, stash of unstaged changes,
     per-clone `pre-commit install`) were verified in a scratch repo and the result is
     recorded; `docs/tech_debt/active/2026-09-25-gsd-commit-timeout-kills-cold-verify-hook.md`
     retires with its sha in the fixing commit.
  3. `bench/RESULTS.md` records the per-request table (parameters, outcome, wall time, host
     state and load) of the ten-identical-worst-row scenario, run once on a fresh server with
     shipping defaults **before** the fix, with the undocumented `500` visible in it; the
     scenario sits in `bench/latency.py`'s `_SCENARIOS` and not the default set, so the
     no-argument run is unchanged. If the `500` does not reproduce, that is recorded as
     measured and the phase stops for the human — the fix is not written against a failure
     nobody saw (L08).
  4. After the fix, a second same-slot timeout in one incident returns the documented `503`
     `timeout`: the same scenario re-run shows zero `500`s (table appended to
     `bench/RESULTS.md`); the deterministic stale-executor test in `tests/test_pool.py` was
     seen red before the fix and green after; the same-tick sibling test accepts
     `BuildTimeout` or `BrokenProcessPool`; the existing 0.5 s-gap test is unchanged; the new
     tests ran repeatedly under `-n 8 --cov` and `-n 4` with the counts recorded.
  5. The worst composed row's margin (29.42 s alone, Phase 12; not finishing inside 30 s under
     ten concurrent builds, Phase 13) has a logged decision — raise `SPUR_BUILD_TIMEOUT`,
     lower a cap, or record the limit as documented behaviour — in an `Lxx` that names the
     measured number that set it; `bench/RESULTS.md` and the resolved tip-chamfer debt file's
     "~1.02x" headline carry a dated note; and
     `docs/tech_debt/active/2026-10-02-same-slot-timeout-cleanup-race-produces-undocumented-500.md`
     retires in the commit that closes both its findings (the race and the margin) with
     `Status: resolved`, the sha, `git mv` into `resolved/` and its INDEX row moved.

**Decisions the human takes at this phase's discuss-phase**: the hook — (a) upstream
request, (b) the full gate on `pre-push`, (c) a sub-30 s pre-commit subset (static-only
`lint typecheck lint-imports no-fake-done`, or with a pytest slice), or (b)+(c) — with each
priced from the research (REQUIREMENTS.md), and who owns the per-clone `pre-commit install`;
the margin — `SPUR_BUILD_TIMEOUT`, a cap such as `spoke_count`'s `le`, or a recorded limit.
**Boundaries**: the race fix is the two-fact guard (slot identity and `_processes is not
None`) plus a `_closed` flag that `recreate_for` honours; no `await` inside the
terminate-and-replace block; when the timeout clock starts, `SPUR_BUILD_TIMEOUT`'s meaning
and `MAX_QUEUED_BUILDS` are untouched by the fix (REQUIREMENTS.md, Out of Scope). Editing
`pool.py` fires the revisit triggers of two `nice` debts (the sometimes-lost worker-coverage
flush; the resource-tracker flake filed in `2403b91`): the plan schedules a read of each, not
necessarily a fix. Until the hook decision lands, every commit is a plain `git commit` with
the hook allowed to finish — a killed SDK commit leaves the hook running as an orphan
(PITFALLS 15).
**Research flag**: No — standard patterns. The race is diagnosed and reproduced three ways
(ARCHITECTURE) with a measured window table (PITFALLS 9–10); the hook options are priced
(STACK). One scratch-repo check of pre-push semantics (SUMMARY correction 11) is a plan task,
not a research phase.
**Plans**: 5/5 plans complete

Plans:
**Wave 1**
- [x] 17-01-PLAN.md — The hook decision in one commit: `verify.static`/`verify.fast`/`test.fast` and the gate-installed hooks (tracer), pre-push semantics measured, L36, eight sites corrected, the commit-timeout debt retired

**Wave 2** *(blocked on Wave 1 completion)*
- [x] 17-02-PLAN.md — Proofs after the hook commit: the whole gate as a real pre-push hook, the upstream request after a human read, and the first live SDK commit (SC1) recording the sha

**Wave 3** *(blocked on Wave 2 completion)*
- [x] 17-03-PLAN.md — The ten-identical-worst-row scenario (`identical`, `record_500`) and up to three fresh-server attempts before the fix, each recorded hit or miss

**Wave 4** *(blocked on Wave 3 completion)*
- [x] 17-04-PLAN.md — The race fixed: stale-executor/same-tick/closed-pool/ast tests seen red, the D-17 checkpoint on three misses, the two-fact guard and `_closed`, 20 + 20 loops

**Wave 5** *(blocked on Wave 4 completion)*
- [x] 17-05-PLAN.md — The scenario after the fix, L37 (the margin as documented behaviour, no default moved), and the race debt retired with both findings closed

### Phase 18: Trochoid Maths, Proved

**Goal**: The trochoid a hob cuts below the base circle can be computed — or honestly
refused — for every gear the project allows, and is proven against an independent oracle,
all as pure `calc.py` maths: no kernel, no `GearParams` field, nothing a user can see
changes.
**Depends on**: Phase 17 — every commit of this phase runs under its hook decision; no
technical dependency on the race fix.
**Requirements**: REQ-cutter-defined-once, REQ-trochoid-root-generated,
REQ-root-mode-single-predicate, REQ-trochoid-proved-independently
**Success Criteria** (what must be TRUE):

  1. The basic rack cutter is defined once in `calc` (dedendum 1.25·m, tip radius ρ, backlash
     as cutter-tooth thickening, profile shift), and its junction with the involute equals
     `Profile.half_angle` at backlash 0 and at 0.10 to a bar re-measured in the phase
     (PITFALLS measured 4.9e-17 rad at 19 teeth, 25°). A ρ above the geometric maximum —
     computed from the real cutter, backlash included, never from a constant — is capped and
     returns a warning naming the capped value at 3 dp (research: ≈0.318·m at 25° and zero
     backlash, STACK and FEATURES; PITFALLS' 0.363·m at m 1.75 is reconciled by the phase's
     first test and the reconciliation recorded); ρ = 0 stays legal. Above the pressure angle
     where the 1.25·m rack has no tip land (≈32.1°, STACK; FEATURES 32.14°) no curve is
     computed: a warning, and the shipped analytic root is the named fallback. The cap and
     the domain limit are each pinned one step either side.
  2. `calc.trochoid_root` returns an immutable `RootCurve` of `(radius, half_angle)` pairs —
     the envelope of the cutter tip arc — or `None` plus a warning when it cannot be computed
     honestly. A sweep over the allowed parameter space (STACK's 7,296 cases as the floor)
     reports zero bracket failures and a monotone radius on every curve; the double root at
     `z_min` has an explicit tested rule; and `derive()`'s per-call cost is re-measured with
     the host load beside it and the stale 11.5 µs docstring figure corrected (PITFALLS
     measured 73 µs with a 60-step bisection against 20.4 µs today, load ≈6.8).
  3. The proof lives in `tests/` and shares no code with the implementation: T1 a closed-form
     undercut onset pins when the root is a trochoid; T2 a swept-cutter no-gouge oracle pins
     where it is; T3 a one-off cross-check against freecad.gears at ρ = 0 is recorded with
     source file, commit and licence (GPL-3.0 — never imported, never vendored). Each bar is
     set from two recorded numbers (the model's own spline error and the reference's stated
     resolution) with the headroom written beside it, and goes to the human if under about
     10× (the L33 D-06 rule); a tripwire that moves ρ by a stated amount was seen red,
     proving the bar load-bearing.
  4. `calc.root_mode(p, pr)` is the single answer to "does the trochoid apply to this gear",
     and the three things now called "undercut" (`teeth < z_min`, `rb > rf`, the cutter's
     form circle) are never mixed; it is tested one tooth step either side of the threshold
     and, at a tuned profile shift, one field step either side (the L33 pattern). The phase
     measures the root-shape step at the threshold on its own generator (FEATURES' simulation:
     ≈0.14·m between 17 and 18 teeth at 20°) and records it in `bench/RESULTS.md`; a figure
     that contradicts the one the human chose on reopens the choice before Phase 19 is
     planned.
  5. Nothing a user can see moved: `git diff --exit-code tests/regression/pre_v0_2.json` is
     clean after every task; `git diff --stat` against the phase base names no file under
     `src/spur/` other than `calc.py`; `grep -rnE 'numpy|scipy' src/spur` prints nothing;
     `requirements.txt` is still 31 pins.

**Where the root-mode decision is taken**: here, at `/gsd-discuss-phase 18`, because it fixes
the predicate's body. The human sees O1 (always-on when undercut: 5 of 44 fixture records
move, discontinuous at the threshold), O2 (always-on wherever `rb > rf`: 28 of 44 move, the
default gear included, by up to ≈0.30 mm of root material), O3 (a new default-off `Literal`
field: 0 move) and O4 (O3 now, the flip later under its own `Lxx`) priced (counts: ARCHITECTURE,
FEATURES; the 0.30 mm: FEATURES' simulation), and chooses; the choice is recorded in
`18-CONTEXT.md`. Its `Lxx` (the root-mode requirement, mapped to Phase 19) is appended with the geometry
in Phase 19, where its acceptance can be read. Also taken here: whether the dedendum stays fixed at
1.25·m (assumed), and whether a published or tool-generated reference exists to add as a
fourth oracle tier (T4, with its stated precision and cutter assumptions).
**Boundary with Phase 19**: the predicate is written and tested here, but no fixture-visible
consumer reads it yet — nothing can ask for the trochoid until the field or the flip exists —
so `_outline`, `root_fillet`, `spline_start`, `tip_chamfer_limit` and `derive` are wired to
it in Phase 19. This phase also supplies the closed-form onset and `x_min` that Phase 19's
`derive()` sentence prints.
**Research flag**: Yes — a targeted `/gsd-plan-phase --research-phase`, not from scratch (the
maths is derived and cross-checked three ways, SUMMARY). Open items: ISO 21771 form-diameter
parity (clause unread — STACK, PITFALLS), the oracle's external anchor (no published table
found — STACK, LOW for the absence), the two-flank interaction at very low tooth counts or
large ρ (STACK's 7,296 cases solved one flank only), and the `z_min` double root.
**Plans**: 6/6 plans complete

Plans:
**Wave 1**
- [x] 18-01-PLAN.md — The cutter and its curve: one undercut gear end to end (tracer: the rack read from `profile()`'s own expressions, the contact-normal-angle envelope, the crossing solve, `root_mode`, the swept-cutter oracle with neighbouring teeth), then the cap reconciled as the first test, floored and warned, the tip-land limit and the junction bar pinned

**Wave 2** *(blocked on Wave 1 completion)*
- [x] 18-02-PLAN.md — `root_mode`, the single predicate: `nothing radial to replace` and `tooth severed` on the refined waist, one fixed order, the 44 fixture records radial when nobody asks, one tooth/field step either side, the cutter's closed-form onset and `x_min`, T1

**Wave 3** *(blocked on Wave 2 completion)*
- [x] 18-03-PLAN.md — The generator over the whole box: the join epsilon measured in-repo and the `z_min` double root pinned, every refusal arm reached, the explicit sweep at commit under D-13's measured budget, every refusal counted and listed (D-11 checkpoint if any is unnamed)

**Wave 4** *(blocked on Wave 3 completion)*
- [x] 18-04-PLAN.md — The independent proof: T2 at the gate and over the whole product with controls and a rho tripwire seen red, T3 freecad.gears literals with provenance, T4 KISSsoft (D-15), every bar's headroom (sub-10x checkpoint)

**Wave 5** *(blocked on Wave 4 completion)*
- [x] 18-05-PLAN.md — The records: the root-shape step at the threshold and the `rb = rf` crossover against a line written first, the per-call costs and `derive()`'s docstring, the human's two decisions (D-05, the resource-tracker debt), the layout rows, the final gate
- [x] 18-06-PLAN.md — Gap closure: the fourth `curve invalid` guard arm tested and seen red under mutation; `cutter()` refuses a non-finite or negative tip radius (18-VERIFICATION item 1, 18-REVIEW WR-01/WR-02; human decision 2026-10-08)

### Phase 19: The Trochoid in the Part

**Goal**: The trochoid root reaches the built solid, the printed numbers and all three
interfaces without changing any part a shared link produces today — the outline consumes the
proven curve, every number printed beside it is proved or warned, it composes with every
shipped feature inside `SPUR_BUILD_TIMEOUT`, and the pre-v0.2 fixture is byte-identical to
the milestone's start.
**Depends on**: Phase 18 (the proven maths and the root-mode choice it fixed); Phase 17.
**Requirements**: REQ-root-mode-decided, REQ-outline-consumes-root-curve,
REQ-derived-numbers-honest-under-trochoid, REQ-cutter-tip-radius-settable,
REQ-undercut-warning-restated, REQ-trochoid-composes-and-is-priced
**Success Criteria** (what must be TRUE):

  1. The part a shared link produces today did not change: every commit of the phase leaves
     `git diff --exit-code tests/regression/pre_v0_2.json` clean and the 85 replay cases pass
     unmodified; a link that omits every new field returns the same `derive()` document and
     the same solid as at the milestone's start, and each new `DerivedDimensions` field reads
     null on replay (L05, L26).
  2. The root in the solid is the oracle's root: `root_d == 2·rf` is asserted in both root
     modes; a kernel-tier proof compares `Edge.positionAt` samples of the built solid's root
     edge to the Phase 18 oracle at a bar set from the measured gap (STACK's N = 16 at
     3.6–4.0e-5 mm is the starting point, after the two research files' spline-deviation
     methods are reconciled — SUMMARY correction 16); a curve that would open the wire or
     swing is refused with a `BuildError` by guards that do not depend on `isValid()`
     (coincident junction vectors, a spacing-ratio check, annulus bounds, a closed-form area
     check); the trochoid generator never enters `model.py`.
  3. Where the trochoid applies, every number the user reads beside it has a proof or a
     warning: the cutter tip radius actually used, printed at 3 dp, with a warning naming the
     cap when it was trimmed; `root_thickness` and `root_gap` either null with a warning or
     redefined at a printed form circle — never the radial-flank values; the undercut waist
     with its floor (a `422` or a warning); the undercut sentence restated from the same
     cutter constants with `x_min` beside it and no "radial root" wording — the restated onset
     proved against the cutter actually used, or the old sentence stays; and no lead-in
     warning where no chord exists. In radial mode the five fixture records that carry the old
     sentence (`pre_v0_2.json:582,632,948,996,1588`) stay byte-identical.
  4. The trochoid composes and is priced: the tip chamfer (L29's kernel boundary re-bisected
     across the spline-to-spline junction), face recesses and each cutout pattern build with
     the trochoid on; the heaviest allowed low-tooth row is measured in `bench/RESULTS.md`
     against `SPUR_BUILD_TIMEOUT` with every composed row inside it; and `make verify`'s cost
     is recorded against the 66 s bar (L34) with the kernel-tier rows priced.
  5. All three interfaces agree from the one model and the record says what is true: the
     model-driven field walk covers every new field in one order across the schema, the web
     form and the CLI (a `Literal` or a number, never a `bool`; the enum exemption
     generalised), the composed document is byte-identical on `spur info` and `/api/info`,
     and every new refusal routes identically to a `422` and to exit 2; the new `Lxx` is
     appended (supersedes L10, amends L09 and L33); README's geometry notes,
     `docs/architecture/gear-maths/`, the solid-model docs and
     `docs/ideas/2026-09-21-trochoidal-root-fillets.md` are brought true in the same change.

**Placement of two requirements**: REQ-root-mode-decided is mapped here, not to Phase 18
where the choice is taken, because its acceptance (the `Lxx`, the field as a `Literal` on the
form and CLI under O3/O4, the fixture `git diff --exit-code` after every task) can only be
read once the geometry exists — and not to conditional Phase 20, so skipping that phase
orphans nothing. REQ-undercut-warning-restated is mapped here, not to Phase 18: its sentence
"applies only where the predicate says the trochoid does", and until this phase no
`GearParams` can ask for the trochoid, so the sentence would sit on a branch nothing reaches.
**Landing dark**: under O3/O4 the trochoid is reachable through the default-off field and
nothing else changes. Under O1/O2 it must land dark without a flag-guarded dead branch
presented as finished (CLAUDE.md; ARCHITECTURE 1.5, PITFALLS 2): how the kernel path is
driven before the flip is this phase's discuss-phase question; if no honest shape exists,
integration and flip become one change under the flip commit's rules and the phase list is
amended with the human before planning.
**Decisions the human takes at this phase's discuss-phase**: the source of ρ — `root_fillet`
reinterpreted (its changed meaning documented, ignored-and-warned where it does not apply,
the L27 precedent) or a new default-off field, the default staying absolute millimetres
(L05); `root_thickness`/`root_gap` null versus redefined at a form circle; the waist floor as
a `422` (L03) or a warning; whether `root_form_d` ships (printed only if the oracle proves it,
labelled as the cutter-envelope junction, never as ISO 21771 parity).
**Order inside the phase**: the spline-to-spline junction under the tip chamfer and the
build time on the heaviest allowed low-tooth row are spiked first, before any schema change
(PITFALLS 18).
**Research flag**: Needs a spike, not a research phase — the chamfer junction (L29's boundary
was bisected to ~2 µm on the old geometry) and the build time on the heaviest low-tooth row;
STACK's assumption that the spline leaves `make bench.build` timings unaffected is unmeasured.
**Plans**: 10 plans
**UI hint**: yes

Plans:
**Wave 1**
- [ ] 19-01-PLAN.md — Spike A, before any schema change: the gate's before-figure at the phase base, the bench's own trochoid outline, the tip chamfer's kernel limit re-bisected across the spline-to-spline junction (20 steps, 14 rows), the heaviest corner rows timed radial and trochoid against SPUR_BUILD_TIMEOUT

**Wave 2** *(blocked on Wave 1 completion)*
- [ ] 19-02-PLAN.md — Spike B: the two spline-deviation methods reconciled, the kernel tier on seven rows, the guard numbers and spline error over the whole product, the root-arc dead band, D-07's waist walk; the human sets the bar, the floor and the waist field's name and confirms D-02's door (checkpoint)
- [ ] 19-03-PLAN.md — The resource-tracker debt's "Phase 19 planning" trigger: 60 isolation loops, the human's fix-or-defer answer (checkpoint), the ledger updated

**Wave 3** *(blocked on Wave 2 completion)*
- [ ] 19-04-PLAN.md — Tracer: `root_shape` end to end on the default gear (field, `RootMode.curve`, the junction from one float, the trochoid outline in `model.py`, `derive()` printing only what is true), then the kernel-tier proof at the human's bar, `root_d == 2 rf` in both modes and the generator kept out of `model.py`

**Wave 4** *(blocked on Wave 3 completion)*
- [ ] 19-05-PLAN.md — The outline hardened: `ROOT_ARC_MIN` closes the dead band a typed backlash reaches, four structural guards that do not rest on `isValid()`, the solid-model docs
- [ ] 19-06-PLAN.md — The numbers: `root_form_d`, the root waist and its pinned floor, the undercut sentence restated from the cutter used with `x_min` rounded up, the cap sentence reworded, the gear-maths docs

**Wave 5** *(blocked on Wave 4 completion)*
- [ ] 19-07-PLAN.md — Three-interface parity: the human settles SC5's exit 2 against the documented CLI contract (checkpoint), the trochoid documents byte-identical, refusals routed identically, README rows and example
- [ ] 19-08-PLAN.md — Composition: the calc-tier (192 rows) and kernel-tier matrices in both root modes, the chamfer cap one step either side of the hob root's junction, the selector twins, a bare build

**Wave 6** *(blocked on Wave 5 completion)*
- [ ] 19-09-PLAN.md — The price on the real build: one outline definition, the chamfer law re-run, the corner rows through `make bench.build`, `make verify` against 66 s and `make verify.fast` against 30 s on the baseline's host, `derive()`'s per-call cost

**Wave 7** *(blocked on Wave 6 completion)*
- [ ] 19-10-PLAN.md — The record: L38 (supersedes L10, amends L09 and L33) with the deferred flip and D-09's trigger, README geometry notes, the strategy docs, the trochoid idea and the slug idea, Phase 20 recorded `Skipped (O4, flip deferred)`

### Phase 20: The Flip (conditional)

**Goal**: The gears the root-mode `Lxx` names get the hob root by default, in exactly one
commit that carries the predicate change, the `make fixture.regen` output and the `Lxx` that
listed the moving records before they moved — the only commit of the milestone allowed to
touch `tests/regression/pre_v0_2.json` (L26 D-03).
**Depends on**: Phase 19.
**Runs only if** the root-mode `Lxx` appended in Phase 19 makes the hob root a default inside
this milestone: O1, O2, or O4 with the flip scheduled in v0.4.
**Skip condition**: skipped — never deleted — when that `Lxx` is O3 (opt-in only; the default
never flips) or O4 with the flip deferred past this milestone (REQUIREMENTS.md "Trochoid
follow-ups" then owns it). A skipped phase keeps its number and its row: the Progress row
reads `Skipped (O3)` or `Skipped (O4, flip deferred)`, STATE.md's Roadmap Evolution gets a
dated line naming the `Lxx` that skipped it, and its criteria are marked not applicable.
**Requirements**: None of its own — it carries the flip clause of the root-mode requirement,
which is mapped to Phase 19 so that a skipped Phase 20 orphans nothing.
**Success Criteria** (what must be TRUE; not applicable when skipped):

  1. The fixture moves exactly once in the milestone: `git log --oneline --
     tests/regression/pre_v0_2.json` since the milestone start shows one commit, and that
     commit also carries the predicate change and the `Lxx`; every commit before and after it
     leaves the file untouched.
  2. The moving records were named first: the `Lxx` lists them before the regeneration, and
     the `make fixture.regen` diff matches the list exactly — any other record moving is a
     bug and the flip stops. The research counts to check against: O1 moves 5 `derived`
     blocks and 3 `solid` blocks and adds one null field to the other 39 (ARCHITECTURE); O2
     moves 28 of 44 records, the default gear included (FEATURES, ARCHITECTURE).
  3. No bar was loosened to absorb the change: the diff of the replay's comparison code and
     tolerances is empty, and the replay passes at the bars it had.
  4. A user can see the flip and nothing else: `spur info` on a named moving gear shows the
     hob-root numbers and warnings after the commit and the old ones before it, a gear the
     `Lxx` does not name is byte-identical (`derive()` and solid), `make verify` is green
     with its cost recorded against the 66 s bar (L34), and README names the new default.

**Research flag**: No — L26's own `make fixture.regen` flow; the priced options were put
before the human at Phase 18's discuss-phase.
**Plans**: TBD

## Process Notes (carried forward)

- Phases run on `gsd/phase-NN-*` branches cut from `origin/main` and land only through
  `make pr.land PR=N` (L22/L25); `.planning/` rides the same PR as the code, never a
  separate planning-only commit. The milestone close is itself a PR.
- `make verify` (ruff, mypy `--strict`, import-linter, unfinished-work scan, pytest on 8
  xdist workers under `fail_under = 96`) is the gate for every phase, no exceptions (L13,
  L34). Since Phase 17 (L36) it runs as the pre-push hook (62–73 s warm at 943 tests); the
  pre-commit hook runs `make verify.fast` (~11 s warm, under `gsd_run query commit`'s 30 s
  timeout — proved by SDK commit `5a3332f`). A killed SDK commit still leaves the hook running
  as an orphan: wait for it, then one plain `git commit`, never a blind retry (D-07).
- Every phase that adds a decision logs it as a new `Lxx` in
  `docs/architecture/decision_log.md`, append-only.
- New parameters default to off (L05); the pre-v0.2 regression fixture is the standing
  proof, re-run by every later phase. In v0.4 it changes only through `make fixture.regen`,
  in its own commit, under its own `Lxx` that says what moved and why (L26 D-03) — a feature
  commit never touches it.
- A debt item is retired only in the commit that fixes it: `Status: resolved`, the sha,
  `git mv` into `resolved/`, the INDEX row moved (CLAUDE.md).

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1–6 | v0.1 | 21/21 | Complete | 2026-09-25 |
| 7–12 | v0.2 | 34/34 | Complete | 2026-10-01 |
| 13–16 | v0.3 | 20/20 | Complete | 2026-10-05 |
| 17. Debt First — Commit Gate and Pool Race | v0.4 | 5/5 | Complete    | 2026-10-06 |
| 18. Trochoid Maths, Proved | v0.4 | 6/6 | Complete    | 2026-10-08 |
| 19. The Trochoid in the Part | v0.4 | 0/TBD | Not started | - |
| 20. The Flip (conditional) | v0.4 | 0/TBD | Not started (conditional on the root-mode Lxx) | - |
