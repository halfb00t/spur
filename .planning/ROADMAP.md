# Roadmap: spur

## Milestones

- ✅ **v0.1 Hardening** — Phases 1–6 (shipped 2026-09-25) — full detail in
  `milestones/v0.1-ROADMAP.md`, audit in `milestones/v0.1-MILESTONE-AUDIT.md`
- ✅ **v0.2 Fit to Shaft** — Phases 7–12 (shipped 2026-10-01) — full detail in
  `milestones/v0.2-ROADMAP.md`, audit in `milestones/v0.2-MILESTONE-AUDIT.md`
- 🚧 **v0.3 Clean Ledger** — Phases 13–16 (in progress)

## Phases

**Phase Numbering:**

- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)
- Numbering continues across milestones — the next milestone starts at Phase 17.

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

### 🚧 v0.3 Clean Ledger (In Progress)

**Milestone Goal:** Every `must` debt item retired by measurement or a logged decision,
every false claim in the record made true or warned, and the gate itself measured — no new
user-facing geometry, no new `GearParams` field, the 44-record pre-v0.2 fixture
byte-unchanged throughout.

- [ ] **Phase 13: Latency Bar** - The two unexplained concurrent-latency observations get
      a ruled cause, and the ten-concurrent bar is demonstrated on both runs of one session
      or superseded by a logged decision
- [ ] **Phase 14: Honest Record** - The root lead-in warns when it rises above the pitch
      circle, README states the real limit, and the filleted-spoke removed-volume proof
      gets an independent closed form
- [ ] **Phase 15: The Gate, Measured and Pinned** - `make verify`'s wall time, its bar and
      its coverage floor become measured numbers in `bench/RESULTS.md`, and CI installs the
      exact kernel pair the regression fixture pins
- [ ] **Phase 16: Typing & Validation Debt** - `model.py` carries no `type: ignore`, and
      Phases 7–8 get the Nyquist validation pass they predate

## Phase Details

### Phase 13: Latency Bar

**Goal**: The ten-concurrent latency bar is either demonstrated on both runs of one session
or superseded by a logged decision with the measurement — the two previously unexplained
observations each get a cause ruled in or out, and the `must` debt file retires.
**Depends on**: Nothing new — builds on the shipped v0.1–v0.2 pipeline (Phases 1–12);
independent of the other v0.3 phases.
**Requirements**: REQ-latency-observations-explained, REQ-latency-bar-demonstrated-or-superseded
**Success Criteria** (what must be TRUE):

  1. A write-up in the shape of `milestones/v0.1-phases/02-*/02-LATENCY-INVESTIGATION.md`
     names, for each of the two observations (the second run of a pair always reads worse;
     idle p95 sits at the harness's ~0.1 ms resolution floor), the candidate that survived
     the pair re-run (a server restart between runs, the poller in its own process) and the
     measurement that ruled the others out. No `src/` or `bench/` change accompanies it.
  2. `bench/RESULTS.md` records `scenario_concurrent` reading ≤2.00× idle p95 on both runs
     of one session on the harness as it stands, OR a new `Lxx` records a changed harness or
     bar (a restart between runs, a higher `MIN_SAMPLES`, an absolute threshold the harness
     can resolve) with the measured reason, re-measured on both runs of one session on the
     changed harness — never a third outcome.
  3. The composed worst row (Phase 12, 29.42 s) is measured once under ten concurrent builds
     and the number recorded in `bench/RESULTS.md`, whatever it reads (the question
     12-CONTEXT.md D-04 re-homed here).
  4. `docs/tech_debt/active/2026-09-23-concurrent-latency-bar-waived.md` retires
     (`Status: resolved`, commit sha, `git mv` to `resolved/`, INDEX row moved) in the commit
     that demonstrates or supersedes the bar; L18's text and the container `HEALTHCHECK` (if
     it cites the bar) say what was measured, not what was accepted.

**Research flag**: No — v0.3 skipped research (REQUIREMENTS.md, 2026-10-01); the debt file
already states the bounded investigation's shape.
**Plans:** 4/7 plans executed (strictly serial: one host, sessions never overlap)

Plans:
**Wave 1**
- [x] 13-01-PLAN.md — the investigation harness, tracer first: split poller, per-run harness, quiet-gated session driver, tabulator

**Wave 2** *(blocked on Wave 1 completion)*
- [x] 13-02-PLAN.md — D-08 order checkpoint, pre-registered method and predictions, the human stops fleet-user

**Wave 3** *(blocked on Wave 2 completion)*
- [x] 13-03-PLAN.md — the six pair sessions (A/B/C twice) and the write-up's verdict per observation

**Wave 4** *(blocked on Wave 3 completion)*
- [x] 13-04-PLAN.md — the decisive bar session on the unmodified harness; D-09 checkpoint on outcome (b)

**Wave 5** *(blocked on Wave 4 completion)*
- [ ] 13-05-PLAN.md — outcome (b) only: the chosen change, the re-measure, D-11 halt on a miss

**Wave 6** *(blocked on Wave 5 completion)*
- [ ] 13-06-PLAN.md — SC3: the composed scenario (own commit) measured once on its own fresh server

**Wave 7** *(blocked on Wave 6 completion)*
- [ ] 13-07-PLAN.md — L32, the Dockerfile sentence, the debt retired (or re-triggered), fleet-user restored

### Phase 14: Honest Record

**Goal**: Every claim this tool or its docs make about geometry it already builds is either
true or flagged — the root lead-in warns when it rises above the pitch circle, README
states the real limit instead of the general "non-working root zone" claim, and the
filleted-spoke removed-volume proof is checked against an independent closed form instead
of a pinned literal.
**Depends on**: Nothing new — builds on the shipped v0.1–v0.2 pipeline (Phases 1–12);
independent of the other v0.3 phases.
**Requirements**: REQ-root-lead-in-warned, REQ-readme-root-zone-states-the-limit, REQ-filleted-spoke-closed-form
**Success Criteria** (what must be TRUE):

  1. `derive()`'s `warnings` carries the lead-in-above-pitch-circle sentence (naming the
     height in mm, 3 dp, and that the chord deviates from the involute there) at the three
     debt-file configurations — default gear: no warning, −1.1875 mm;
     `{profile_shift 1.0, pressure_angle 14.5}`: +0.5625 mm, warns; `{0.75, 20}`:
     +0.1250 mm, warns — plus one field-step either side of the crossing, proven by tests.
     Pure `calc.py`; no kernel import, no outline change.
  2. README's root-fillets bullet (lines ~227–228) states the real condition: below the
     pitch circle on the default gear, above it when profile shift and root fillet are
     large for the module, in which case `warnings` says so — citing the warning, with no
     number in README the phase did not itself measure.
  3. The filleted-spoke row of
     `test_each_cutout_is_exactly_what_derive_prints_on_the_built_solid` asserts the removed
     volume against the independent closed form (sharp sector-opening area minus four
     circular-segment corrections at `spoke_fillet_effective(p)`, × `face_width`) to the
     same 1e-9 mm³ bar the other three cutout rows meet; the pinned literal `2934.725405` is
     demoted to a comment recording the first measurement, and a tripwire proves the
     assertion goes red when `_fillet_corner`'s `inside=True` tangent root is perturbed.
  4. Both debt files — `2026-09-28-root-lead-in-can-reach-above-the-pitch-circle.md`
     (closed by this phase's first two requirements together) and
     `2026-09-29-filleted-spoke-volume-proof-pinned-not-derived.md` — retire with their sha
     in their fixing commits; `tests/regression/pre_v0_2.json` stays byte-unchanged (0 of 44
     records cross the new warning's threshold, confirmed at kickoff 2026-10-01); a new
     `Lxx` answers L30's "pinned, not derived" clause without touching L30's own text.

**Research flag**: No — v0.3 skipped research (REQUIREMENTS.md, 2026-10-01); both debt
files already state the next step.
**Plans**: TBD

### Phase 15: The Gate, Measured and Pinned

**Goal**: `make verify`'s wall time, the bar set from it, and a coverage floor are all
numbers in `bench/RESULTS.md`, not estimates — and CI installs the exact kernel pair the
regression fixture's provenance header names, so the fixture's exact-value assertions stay
honest.
**Depends on**: Nothing new — builds on the shipped v0.1–v0.2 pipeline (Phases 1–12);
independent of the other v0.3 phases. Internally: `REQ-verify-profiled`'s baseline lands
before `REQ-verify-at-the-bar` (the bar is set from it at this phase's discuss-phase) and
before `REQ-coverage-floor` (its wall-time cost is measured against the same baseline) —
sequential plans within this phase, the way 12-01 preceded the rest of Phase 12.
**Requirements**: REQ-verify-profiled, REQ-verify-at-the-bar, REQ-coverage-floor, REQ-ci-installs-the-pinned-kernel
**Success Criteria** (what must be TRUE):

  1. `bench/RESULTS.md` records `make verify`'s wall time per stage (ruff, mypy,
     import-linter, unfinished-work scan, pytest) and pytest's per-file and top-N
     `--durations`, measured the D-10 way (alternating full runs, same session, host load
     recorded); the heaviest contributors are named with what each proves, and whether the
     `BuildPool`/OCCT tests tolerate `pytest-xdist` workers is measured, not assumed
     (pytest runs serially today — no `-n`, `pytest-xdist` not a dev extra).
  2. The bar the human sets at this phase's discuss-phase from the profile (recorded in
     that phase's CONTEXT) is read at or under, measured the same way; the before/after rows
     sit in `bench/RESULTS.md`, the test count is unchanged or the difference is named, and
     the pre-commit hook's own "a warm run is ~11 s" comment is corrected to what it now
     measures.
  3. `pytest-cov` is added to the `dev` extras, one baseline `pytest --cov` run is recorded
     in `bench/RESULTS.md`, `fail_under` is set just under it in `[tool.coverage.report]`,
     and `make verify`'s test target runs `--cov --cov-fail-under`; a scratch run with one
     test file removed shows `make verify` going red on the floor (recorded, not committed);
     the ASSUMPTION about `BuildPool` worker coverage (`concurrency = ["multiprocessing"]`)
     is settled and stated.
  4. CI's `make verify PYTHON=python` resolves `cadquery==2.8.0`/`cadquery-ocp==7.9.3.1.1`
     by the mechanism the human picks at this phase's discuss-phase (install
     `requirements.txt` before the dev extras, or an upper bound in `pyproject.toml`),
     proven by a green CI run URL whose log shows the resolved pair, logged as a new `Lxx`
     against L12's rationale; `test_the_fixture_was_captured_on_the_kernel_this_run_uses`
     stays the named tripwire.
  5. `docs/tech_debt/active/2026-09-21-no-coverage-floor.md` and
     `docs/tech_debt/active/2026-09-26-ci-resolves-the-kernel-the-fixture-pins.md` both
     retire with their sha in their fixing commits; any new dev dependency lands only in
     the `[dev]` extra — `requirements.txt`'s 31 runtime pins are unchanged.

**Research flag**: No — v0.3 skipped research (REQUIREMENTS.md, 2026-10-01); the bar is set
from the profile at this phase's discuss-phase, not before.
**Plans**: TBD

### Phase 16: Typing & Validation Debt

**Goal**: `model.py` is clean under mypy `--strict` with zero `# type: ignore`, and
Phases 7–8 — the two v0.2 phases that predate the Nyquist capability — get the validation
pass they were built without.
**Depends on**: Nothing new — builds on the shipped v0.1–v0.2 pipeline (Phases 1–12);
independent of the other v0.3 phases.
**Requirements**: REQ-model-py-no-type-ignore, REQ-nyquist-phases-7-8
**Success Criteria** (what must be TRUE):

  1. `src/spur/model.py` carries zero `# type: ignore` (five retired: lines 212, 236, 238,
     410, 419 — `attr-defined` ×3 on `fillet`/`chamfer`, `arg-type` and `return-value` on
     `.val()`), achieved by narrowing the pipeline's annotations from `_gear_blank` →
     `_cut_face_recesses` → `_cut_bore` onward and casting once at the `.val()` boundary —
     its own tested change, in its own commit, never riding along with a geometry proof.
  2. `make verify` is green under `--strict` + `disallow_any_explicit` with `RUF100` still
     on; `tests/regression/pre_v0_2.json` stays byte-unchanged (annotations only — the 15
     kernel-level proof rows from Phase 12 stay green).
  3. `docs/tech_debt/active/2026-09-21-cadquery-shape-typing.md` retires with its sha and
     corrected stale line references.
  4. `milestones/v0.2-phases/07-*/VALIDATION.md` and `08-*/VALIDATION.md` exist with the
     Nyquist audit's `nyquist` field no longer `partial` for Phases 7 and 8, produced by
     `/gsd-validate-phase 7` and `8` — or, if `validate-phase` cannot target an archived
     phase directory (the flagged ASSUMPTION), the human's choice between a temporary copy
     under `.planning/phases/` moved afterward, or dropping the requirement, is recorded in
     this phase's record with the reason. Discovery only — any gap found becomes a debt
     file with a trigger, not a scope expansion.

**Research flag**: No — v0.3 skipped research (REQUIREMENTS.md, 2026-10-01); both items are
internal and one is process-only.
**Plans**: TBD

## Process Notes (carried forward)

- Phases run on `gsd/phase-NN-*` branches cut from `origin/main` and land only through
  `make pr.land PR=N` (L22/L25); `.planning/` rides the same PR as the code, never a
  separate planning-only commit. The milestone close is itself a PR.
- `make verify` (ruff, mypy `--strict`, import-linter, unfinished-work scan, pytest) is the
  gate for every phase, no exceptions (L13). It runs as the pre-commit hook (~3.5 min at
  907 tests); `gsd_run query commit`'s 30 s timeout cannot survive it — commit with plain
  `git commit` and let the hook finish.
- Every phase that adds a decision logs it as a new `Lxx` in
  `docs/architecture/decision_log.md`, append-only.
- New parameters default to off (L05); the pre-v0.2 regression fixture is the standing
  proof, re-run by every later phase.

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|-----------------|--------|-----------|
| 1–6 | v0.1 | 21/21 | Complete | 2026-09-25 |
| 7–12 | v0.2 | 34/34 | Complete | 2026-10-01 |
| 13. Latency Bar | v0.3 | 4/7 | In Progress|  |
| 14. Honest Record | v0.3 | 0/TBD | Not started | - |
| 15. The Gate, Measured and Pinned | v0.3 | 0/TBD | Not started | - |
| 16. Typing & Validation Debt | v0.3 | 0/TBD | Not started | - |
