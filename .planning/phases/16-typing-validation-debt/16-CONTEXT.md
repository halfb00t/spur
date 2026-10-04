# Phase 16: Typing & Validation Debt - Context

**Gathered:** 2026-10-04
**Status:** Ready for planning

<domain>
## Phase Boundary

Two debt items retired and the record made true; the last v0.3 phase. No geometry change,
no `GearParams` field, no `DerivedDimensions` field; `tests/regression/pre_v0_2.json` (44
records) byte-unchanged throughout — `git diff --exit-code 085e5a6 --
tests/regression/pre_v0_2.json` is the final pass (12 D-20 / 15 D-20 shape).

1. **The narrowing** (REQ-model-py-no-type-ignore, SC1–SC3). `src/spur/model.py` loses its
   five `# type: ignore`s (today lines 213, 237, 239, 411, 420) under mypy `--strict` +
   `disallow_any_explicit` with `RUF100` on, by two `isinstance`-narrowing helpers that
   raise `BuildError` on a shape the pipeline must never see (D-01–D-03); the
   `cadquery.*` entry leaves the mypy override and its false comment is corrected (D-04);
   `make no-fake-done` refuses a new `type: ignore` under `src/spur/` (D-05); two refusal
   tests plus the fixture diff are the proof (D-06); one code commit carries its record
   (D-07, D-14).
2. **Phases 7 and 8** (REQ-nyquist-phases-7-8, SC4). The human runs `/gsd-validate-phase
   7` and `8` at a `checkpoint:human-action` (the flagged ASSUMPTION is settled: gsd's
   `init.phase-op` resolves both to `.planning/milestones/v0.2-phases/…`); every gap is
   "manual-only" plus one `nice` debt file per phase, never a new test (D-08–D-10).
3. **The record.** The closed v0.2 milestone audit's `nyquist` block is amended in place
   with a date (D-11); four false planning sentences are corrected in the PR (D-12); L35
   amends L21 (D-13); the debt file retires in the fixing commit with its stale line
   references corrected and `docs/architecture/solid-model/implementation.md`'s
   "load-bearing ignores" bullet rewritten (D-14).

Not this phase: the remaining `must` row (`2026-10-02-same-slot-timeout-cleanup-race…`,
no Phase 16 REQ covers it — a milestone-audit question, see `<deferred>`); any test for
Phases 7–8 behaviour; refreshing `.planning/codebase/*.md`; the gsd commit-timeout debt.

**Facts measured 2026-10-04 that reshape the REQ text** (`.venv` cadquery 2.8.0 /
cadquery-ocp 7.9.3.1.1, `inspect.signature` and the package source):
- `Shape.cut(*toCut: Shape, tol) -> Shape` (`cadquery/occ_impl/shapes.py:1414`); only
  `Compound.cut() -> Compound` (4886); `Solid` does not override `cut`.
  `Mixin3D.fillet(self: Any, …) -> Any`, `Mixin3D.chamfer(self: Any, …) -> Any` (3972,
  3989); `Shape` does not carry `Mixin3D` — `Solid` and `Compound` do.
  `Workplane.val() -> Vector | Location | Shape | Sketch` (`cadquery/cq.py:411`).
  `Solid.extrudeLinear(...) -> Solid`.
- Runtime on the default gear: `Solid` after `_gear_blank`; `Compound` after
  `_cut_face_recesses` and after every later step; a step whose feature is off returns
  its input unchanged, so mid-pipeline the value is genuinely `Solid | Compound`.
  `Solid.cut(Solid)` on two primitives also returns `Compound`. `_ring()` returns `Solid`.
- **Consequence:** the debt file's and REQ's "cast once at the `.val()` boundary" reaches
  two of the five ignores (`_ring` `return-value`, the bore `hole.val()` `arg-type`); the
  three `attr-defined` sites need a `Mixin3D` narrowing after a `cut` whose static type is
  `Shape` whatever went in. D-12 corrects the sentence.
- cadquery ships `py.typed` (mypy reads its annotations — that is why the errors exist);
  `OCP` has 0 `.pyi` files and no `py.typed`. `pyproject.toml`'s override comment "The CAD
  kernel ships no type information" is false for cadquery (D-04).
- `gsd_run query init.phase-op 7` → `phase_found: true`, `phase_dir:
  .planning/milestones/v0.2-phases/07-foundation-generalized-edge-selection-regression-fixture`,
  `has_plans: true`, `has_verification: true`; `8` → `…/08-hex-bore` likewise. The
  Nyquist hook is active at `verify:post` (`workflow.nyquist_validation`).
- `.planning/milestones/v0.2-MILESTONE-AUDIT.md`: `nyquist.missing_phases: ["07","08"]`,
  `overall: partial`; table rows "MISSING (pre-capability)". A `VALIDATION.md` at
  `status: validated` + `nyquist_compliant: false` classifies PARTIAL (audit-milestone
  §5.5) — SC4's "no longer partial" and REQ's "discovery only" collide; D-10 resolves it.
- PR #18 squash-merged as `085e5a6`; the local phase-15 branch has no file beyond it.

</domain>

<decisions>
## Implementation Decisions

### The narrowing (REQ-model-py-no-type-ignore)
- **D-01:** **`isinstance` + `BuildError`, not `typing.cast`, not a `TypeIs` guard.** A
  narrowing is a claim; the one tool that can make mypy green while being wrong is
  `cast`. `_build` already asserts positively at the end ("exactly one valid solid",
  `model.py:519–522`); the helpers assert the same invariant where `Mixin3D` and `.val()`
  are needed. Cost: nanoseconds per build step against seconds of OCCT. SC2's
  "annotations only" parenthetical widens to "no geometry change": the fixture pins
  outputs (derive fields, volume, bbox, face/edge counts), none of which a check that
  cannot fire on a valid build can move. Rejected: `cast` (zero runtime, literally
  annotations-only, unverifiable, nothing to test); `TypeIs` (same runtime check behind
  more ceremony for five sites). — **Reversibility:** reversible — five call sites and two
  helpers.
- **D-02:** **Two helpers, five call sites; the pipeline's own annotations stay
  `cq.Shape`.** `_body(shape: cq.Shape) -> cq.Solid | cq.Compound` at the three
  fillet/chamfer sites (`_cut_face_recesses` 213, `_cut_bore` 239, `_chamfer_tips` 411:
  `solid = _body(solid).fillet(...)` / `.chamfer(...)`), and `_shape_of(wp: cq.Workplane)
  -> cq.Shape` at the two `.val()` sites (`_cut_bore` 237, `_ring` 420). Names are
  Claude's discretion; one narrowing per concept; the measured runtime types (domain
  facts above) and the date sit once in each helper's comment, replacing the three
  "see `_cut_face_recesses`" comments. `_cut_face_recesses` → `_chamfer_tips` keep
  `cq.Shape` in and out — that is what `Shape.cut` promises, and a step with its feature
  off returns a `Solid` unchanged, so `Solid | Compound` would be the honest runtime type
  but not the static one. `_gear_blank -> cq.Solid` (true: `extrudeLinear -> Solid`) is
  Claude's discretion. The `Any` that `Mixin3D.fillet/chamfer` return is assigned to the
  `cq.Shape`-typed `solid` before any `return` (10-02's measured `warn_return_any` rule).
  Rejected: operation wrappers `_fillet`/`_chamfer`/`_shape_of` (hide `Mixin3D` fully,
  three helpers for the same narrowing); inline `isinstance` at each site (the debt
  file's "ignoring at each call site" by another name); re-typing the pipeline as
  `cq.Compound` by wrapping `_gear_blank`'s solid in `Compound.makeCompound` (a runtime
  geometry-path change in the most delicate file for a typing reason — not measured, not
  taken); a local `.pyi` overriding cadquery's own `Shape.cut` annotation (a stronger
  claim than the library makes).
- **D-03:** **The `BuildError` names the invariant, not a parameter.** Working draft:
  `Geometry kernel returned a {type(shape).__name__} where a solid body was expected: a
  modelling defect in the build pipeline, not a parameter problem.` The planner may tune
  the words, not the content; the test asserts the full string (10-REVIEW CR-01: a prefix
  cannot see a wrong suffix). Why `BuildError` and not `TypeError`: `_build_checked`
  wraps any other exception as "Geometry kernel failed (TypeError); try smaller fillets or
  chamfers" — a wrong remedy on the user's screen for a defect they did not cause.
  Rejected: reusing "Geometry kernel produced an invalid solid for these parameters" (it
  blames the input). This error cannot fire from any settable field today (every boolean
  returns `Solid` or `Compound`; `extrude().val()` is a `Shape`) — it is D-15-shaped: a
  guard against a modelling defect, "never an answer".
- **D-04:** **`cadquery.*` leaves `[[tool.mypy.overrides]]`; `OCP.*` stays; the comment
  says why.** cadquery ships `py.typed`, so `ignore_missing_imports` is inert for it and
  the comment "The CAD kernel ships no type information" is false for the package that
  matters; OCP (0 `.pyi`, no `py.typed`) is what the entry is for. **Gated:** `make
  typecheck` output is captured before and after the edit; byte-identical → land it in
  the narrowing commit; any difference → stop and ask (it would mean mypy was finding
  cadquery through that entry after all). Rejected: correct the comment only (a config
  line documented as doing nothing); leave it (a false sentence in the gate's own config
  in a milestone named Clean Ledger). — **Reversibility:** reversible — one list entry.
- **D-05:** **SC1 is pinned in `make no-fake-done`, scoped to `src/spur/`.** One more
  `git grep -nE` line in the existing target (`Makefile:63–68`): `type: ignore` under
  `src/spur/` is an unfinished-work marker — "finish it, or file it in `docs/tech_debt/`"
  is already the rule for a suppression, and nothing else in the gate refuses a *new*
  coded ignore (RUF100 catches only an unused one). `tests/`, `bench/`, `scripts/` stay
  free: `tests/test_calc.py:1472` and `tests/test_cli.py:423` suppress `arg-type` on a
  deliberate `model_construct(**kw)`, and a `.planning/` investigation script carries one
  — the repo-wide marker is not free today. The refusal message wording is Claude's.
  Rejected: no pin (the fifth ignore arrived unnoticed in 10-02); repo-wide (blocks a test
  that calls a library wrongly on purpose). — **Reversibility:** reversible — one Makefile
  line.

### The proof (SC1 "its own tested change", SC2)
- **D-06:** **Two refusal unit tests with no kernel build, the 48 existing kernel tests,
  and the fixture diff.** `_body()` raises D-03's error on a `cq.Face` (a `Shape` without
  `Mixin3D`); `_shape_of()` raises it on a `Workplane` whose `.val()` is a `Vector` or
  `Location`. Names read as requirements ("a non-body shape in the build pipeline is
  named as a modelling defect, not blamed on a parameter"). The 15 Phase 12 kernel rows
  and the 44-record replay stay green unchanged; `git diff --exit-code 085e5a6 --
  tests/regression/pre_v0_2.json` is the final pass. `tests/` grows by exactly these two
  (927 → 929 as items; the planner states the count). The two new `raise` lines are
  covered, so `fail_under = 96` is not disturbed by uncovered branches. Rejected: the
  existing suite only (the new path at zero coverage, SC1's "tested" read as "nothing
  regressed"); a kernel row pinning the measured runtime types (one more ~0.5 s build to
  pin cadquery behaviour the fixture already pins indirectly — L35 carries the
  measurement as a dated fact instead).
- **D-07:** **One code commit carries the change and its record; planning sentences ride
  that plan's own `.planning` commit.** The commit: `model.py` helpers and annotations,
  the two tests, the `no-fake-done` line (D-05), the `pyproject.toml` override edit
  (D-04), `docs/architecture/solid-model/implementation.md:29–33` rewritten (D-14), the
  debt file retired and its INDEX row moved (D-14). REQ-model-py-no-type-ignore's and
  ROADMAP SC1's sentence corrections (D-12) land in the same plan's `.planning` commit
  (15 D-01 shape). SC1's "never riding along with a geometry proof" holds: no proof row
  changes. Rejected: code and tests first, record after (the ledger lies for one commit —
  CLAUDE.md "retired in the fixing commit"); everything including planning in one (14/15
  kept product and planning-record edits apart).

### Phases 7 and 8 (REQ-nyquist-phases-7-8)
- **D-08:** **The human runs `/gsd-validate-phase 7` then `8` at a
  `checkpoint:human-action`; the ASSUMPTION is settled, no temporary copy.** gsd resolves
  both archived directories (domain facts). `validate-phase` is an interactive top-level
  skill — State B (SUMMARYs, no VALIDATION.md) reconstructs the per-task map, gates with
  its own `AskUserQuestion` at Step 4, spawns `gsd-nyquist-auditor` only on "Fix all
  gaps", writes `status: validated` at Step 6, and commits at Step 7 through `gsd_run
  query commit`, which the ~64 s hook kills. The plan's task halts with exact
  instructions: fresh session per phase; at the Step 4 gate answer **"Skip — mark
  manual-only"** for every gap (D-09); when the helper times out, plain `git commit` of
  `${PHASE_DIR}/0N-VALIDATION.md` with the hook running, and wait for any orphaned
  `pre_commit hook-impl` to exit. The executor then verifies: both files exist at
  `status: validated`, each `nyquist_compliant` value is recorded as read (never
  asserted `true`), and the gap count equals the debt rows filed (D-09). Rejected: the
  executor driving the skill through the Skill tool (its gate fires inside a subagent, the
  auditor nests, the commit timeout lands on the executor — an untested path); running
  both before planning (work outside the phase's plans — the v0.1-style record mismatch).
- **D-09:** **A gap is one `nice` debt file per phase, trigger "the covered file is next
  touched"; zero gaps = no file.** Phases 7 and 8 read VERIFICATION `passed` (4/4,
  30/30) and every behaviour they shipped runs under `make verify` today; a Nyquist gap is
  a task without a named automated command, not an unproven behaviour. One file per phase
  (`docs/tech_debt/active/2026-10-xx-phase-07-nyquist-gaps.md`, likewise 08) lists each
  gap row with its task id, what proves it today, and the trigger; one INDEX row each;
  `docs/tech_debt/TEMPLATE.md` shape. **Exception, stated in the plan:** a behaviour the
  audit finds with *no* test at all is `must`, and the executor halts at a
  `checkpoint:decision` with the row for the human to choose fix-in-phase (a scope
  expansion REQ forbids by default) or carry (v0.3 SM1 then reads honestly unmet).
  Rejected: `must` always (files `must` rows in the last phase of a milestone whose SM1
  is zero `must` rows); per-row severity at a checkpoint (turns a discovery pass into a
  scoping session); one file per gap (near-identical `nice` rows for one cause).
- **D-10:** **Discovery only, as REQ says; SC4 is corrected to what can be true.** The gate
  answer is manual-only for every gap (D-08); no `tests/` change under this requirement.
  ROADMAP SC4 and REQ-nyquist-phases-7-8's acceptance sentence are amended in the PR
  (D-12) to: "`07-VALIDATION.md` and `08-VALIDATION.md` exist at `status: validated`
  under `.planning/milestones/v0.2-phases/`; `nyquist_compliant` reads what the audit
  measured; a gap is a debt row; the v0.2 audit's `nyquist` block records the
  measurement (D-11)". Rejected: "Fix all gaps" via the auditor (SC4 literal, but the
  scope expansion REQ forbids, tests landing with no human-set acceptance for 2026-09
  behaviour, `tests/` pinned at 927 by Phase 15's record); deciding per gap at the gate
  (the planner cannot write the plan's outcome).

### The record
- **D-11:** **The closed v0.2 audit is amended in place, dated.** In
  `.planning/milestones/v0.2-MILESTONE-AUDIT.md`: `nyquist.missing_phases` → `[]`, `07`
  and `08` placed in `compliant_phases` or `partial_phases` as measured, `overall`
  recomputed, an `amended: 2026-10-xx by Phase 16 (16-0N-SUMMARY.md)` line beside the
  block; under "## Nyquist Compliance" the two original rows stay and two new rows sit
  under a dated sub-heading. The record says what changed and when (decision-log
  append-only spirit). Rejected: leave it as history (SC4's field is then never true
  anywhere); re-running `/gsd-audit-milestone` (audits v0.3, not v0.2).
- **D-12:** **Four false planning sentences are corrected in the PR** (14 D-07 / 15 D-01
  precedent; ROADMAP only through gsd's roadmap tooling, never a whole-file write;
  REQUIREMENTS by scoped Edit; each in the `.planning` commit of the plan that touches
  its subject):
  1. `REQUIREMENTS.md` REQ-model-py-no-type-ignore and ROADMAP Phase 16 SC1: "narrowing
     the pipeline's annotations … and casting once at the `.val()` boundary — not a `cast`
     at each call site" → the two `isinstance` helpers (D-01/D-02) with the reason
     (`Shape.cut -> Shape`); line refs 212/236/238/410/419 → 213/237/239/411/420.
  2. `REQUIREMENTS.md` REQ-nyquist-phases-7-8: the "ASSUMPTION (unverified 2026-10-01)"
     sentence → verified 2026-10-04, resolved as D-08.
  3. ROADMAP Phase 16 SC4: path `milestones/v0.2-phases/07-*/VALIDATION.md` →
     `.planning/milestones/v0.2-phases/07-*/07-VALIDATION.md` (and `08-hex-bore/
     08-VALIDATION.md`); "no longer `partial`" → D-10's wording.
  4. `.planning/PROJECT.md` "Current Milestone" target text "retired by narrowing at the
     `.val()` boundary" and Key Decisions L21's Outcome column — at the phase transition,
     where PROJECT.md is edited.
  Rejected: only the two the code touches; leaving all four for L35 to carry (the text a
  reader opens first stays false).
- **D-13:** **L35, short, amends L21; append-only.** One paragraph in L26–L34's shape:
  vendor `Shape` typing now stops at two `isinstance` boundaries (`_body`, `_shape_of`)
  that raise `BuildError`; `isinstance` over `cast` and why; the measured runtime types
  (`Solid` after extrude, `Compound` after every boolean, a feature-off step passes its
  input through) and `Shape.cut -> Shape` as the reason the debt file's plan could not
  hold; `cadquery.*` dropped from the override (cadquery ships `py.typed`, OCP does not);
  the `no-fake-done` pin; the Phase 7/8 Nyquist outcome with the measured gap count and
  `nyquist_compliant` values. L21's text untouched (L25 → L22, L32 → L18, L34 → L12/L13
  precedent). Every number cited to a SUMMARY sha or this file's domain facts, none
  re-estimated. Rejected: no `Lxx` (breaks one-entry-per-phase; L21's lineage has no
  pointer to where vendor types now stop).
- **D-14:** **Retirement and prose in the fixing commit.**
  `docs/tech_debt/active/2026-09-21-cadquery-shape-typing.md` → `Status: resolved`, the
  sha, `git mv` to `resolved/`, INDEX row 19 moved; its "Related files" line refs
  (195/219/221/264/273) corrected to 213/237/239/411/420 on the way out; its "Resolved
  in" records that "cast once at `.val()`" could not hold because `Shape.cut -> Shape`,
  and the mechanism taken. `docs/architecture/solid-model/implementation.md:29–33` ("the
  `type: ignore` comments are load-bearing") rewritten to describe the two boundaries and
  the pin. The `.pre-commit`/Makefile messages and `docs/HOW_TO_DEVELOP.md` carry no claim
  about the ignores (grep `type: ignore` across `docs/` found only these two files and the
  INDEX row).
- **D-15:** **Process (13 D-18, 14 D-15, 15 D-21, ROADMAP "Process Notes").** Branch
  `gsd/phase-16-typing-validation-debt` cut from `origin/main` `085e5a6` (PR #18 landed;
  the local phase-15 branch carries nothing beyond it — checked); plain `git commit` with
  explicitly staged files (the hook runs `make verify` ~64 s at `-n 8` with coverage;
  `gsd_run query commit`'s 30 s timeout cannot survive it); lands via `make pr.land PR=N`
  (L22/L25); `.planning/` rides the same PR; who wrote the diff does not review it
  (CLAUDE.md). The milestone close (`/gsd-audit-milestone`, `/gsd-complete-milestone`)
  follows this phase and is not part of it.
- **D-16:** **No behaviour change beyond the invariant check; `tests/` grows by two.** No
  `GearParams` or `DerivedDimensions` field; no change to any selector, cap, refusal or
  cut; the fixture byte-unchanged by construction and proven by the diff (D-06). If
  narrowing turns out to need anything the kernel's own types do not allow (a wrapper
  object, a changed boolean call), the executor stops and asks — it is outside what this
  phase promised.

### Claude's Discretion
- **Plan order.** Suggested: (1) the narrowing — helpers, annotations, two tests, the
  `no-fake-done` line, the override edit (gated), `implementation.md`, debt retired, then
  the REQ/SC1 corrections in the `.planning` commit; (2) the `checkpoint:human-action` for
  `/gsd-validate-phase 7` and `8`, the executor's verification, the gap debt file(s) if
  any, the audit amendment (D-11), SC4/REQ-nyquist corrections; (3) L35, PROJECT.md
  rows at transition. (2) does not depend on (1); a planner may run it first so the
  human's runs happen while (1) executes.
- Helper names (`_body`/`_shape_of` or kin), their comment text (carries the measured
  types and date), the `BuildError` wording within D-03's content, the `no-fake-done`
  refusal sentence, the L35 title.
- `_gear_blank -> cq.Solid` or leave `cq.Shape`; where the two refusal tests live
  (`tests/test_model.py` already imports `cq` and `BuildError`; no kernel build needed).
- The exact text of the human-action checkpoint (session hygiene, the gate answer, the
  plain-commit fallback) and what the executor's post-check reads from the two
  `VALIDATION.md` frontmatters.
- Whether the two gap debt files (if any) and the audit amendment share one commit.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements, roadmap, project
- `.planning/REQUIREMENTS.md` — "### The gate" REQ-model-py-no-type-ignore (lines
  152–162: the "casting once" sentence and line refs D-12 corrects) and
  REQ-nyquist-phases-7-8 (163–171: the ASSUMPTION sentence D-12 corrects; "Discovery only"
  — D-10's rule); "Rules every requirement lives by"; Traceability rows 226–227.
- `.planning/ROADMAP.md` "### Phase 16: Typing & Validation Debt" (255–282) — SC1 (the
  sentence D-12 corrects), SC2 ("annotations only" — D-01 widens it to "no geometry
  change"), SC3, SC4 (the path and "no longer partial" D-12/D-10 correct); "## Process
  Notes (carried forward)".
- `.planning/PROJECT.md` — "Current Milestone: v0.3 Clean Ledger" (the "Shape typing"
  target text — D-12 item 4), "Success Metric (Milestone v0.3)" 1–3 (SM1 and the active
  `must` row, see `<deferred>`), "Constraints → Module boundaries / Gate", Key Decisions
  L21 (Outcome column at transition).
- `CLAUDE.md` — "How to verify (the gate)", "Stop and ask first" (library behaviour
  verified — the domain facts), "Keep it simple", "Finishing work properly", "Capturing
  ideas and debt" (retirement mechanics, severity tags), "Code style" (vendor types stop
  at their boundary; comments carry the measurement).
- `docs/CODING_VALUES.md` — §Validation (89), §Failure handling (121), §Testing (152),
  §Tech debt and refactoring (168), §Project-specific (189).

### The debt and its history
- `docs/tech_debt/active/2026-09-21-cadquery-shape-typing.md` — the item D-14 retires:
  the `Mixin3D` reason, "casting once at the `.val()` boundary" (the plan D-12 corrects),
  "its own tested change", stale line refs 195/219/221/264/273.
- `docs/tech_debt/INDEX.md` — row 19 (`nice`, the typing item) moves to Resolved; new rows
  for D-09's files if any; severity definitions.
- `docs/tech_debt/TEMPLATE.md` — the shape for D-09's gap files and for `Status`/`Resolved
  in`.
- `docs/tech_debt/active/2026-09-25-gsd-commit-timeout-kills-cold-verify-hook.md` — why
  every commit is a plain `git commit` (D-08, D-15).
- `docs/tech_debt/active/2026-10-02-same-slot-timeout-cleanup-race-produces-undocumented-500.md`
  — the one `must` row left; not this phase's (see `<deferred>`).
- `docs/architecture/solid-model/implementation.md` lines 29–33 — the "load-bearing
  ignores" bullet D-14 rewrites.

### Decisions
- `docs/architecture/decision_log.md` — **L21** (`disallow_any_explicit` on; `Any` never
  written; the entry L35 amends), L08 (no plausible numbers — D-03's "never an answer"
  stance), L15 (`TRY003` off: error messages are the product — D-03's full-string test),
  L16 (no formatter — hand-align `pyproject.toml`/Makefile edits), L26 (fixture
  byte-unchanged; a selector never silently selects nothing — the guard precedent D-03
  follows), L29 (10-02's `warn_return_any` assignment rule), L32–L34 (the "amends Lxx"
  append-only shape).
- `.planning/phases/15-the-gate-measured-and-pinned/15-CONTEXT.md` — D-01 (correcting the
  planning record's own sentence in the PR), D-17–D-21 (record and process shape; D-20's
  fixture-diff final pass; D-21 branch/commit/land rules).
- `.planning/phases/14-honest-record/14-CONTEXT.md` — D-07 (the correction precedent),
  D-14/D-15 (retirement and process).
- `.planning/milestones/v0.2-phases/12-composition-pass/12-CONTEXT.md` — D-20 (the
  fixture `git diff --exit-code` final pass).
- `.planning/milestones/v0.2-phases/10-tooth-tip-chamfer/10-02-SUMMARY.md` — the fifth
  ignore's arrival and the `warn_return_any` assignment rule (STATE.md Phase 10 decisions).

### The Nyquist pass
- `$HOME/.claude/gsd-core/workflows/validate-phase.md` — Step 0 (`init.phase-op` resolves
  `phase_dir`), Step 1 (State B), Step 4 (the gate: "Skip — mark manual-only"), Step 6
  (`status: validated`), Step 7 (`gsd_run query commit` — the timeout), Step 8 (the
  partial routing).
- `$HOME/.claude/gsd-core/templates/VALIDATION.md` — frontmatter fields the executor
  reads back (`status`, `nyquist_compliant`).
- `.planning/phases/13-latency-bar/13-VALIDATION.md` and
  `15-the-gate-measured-and-pinned/15-VALIDATION.md` — the per-task map shape as this
  repo fills it.
- `.planning/milestones/v0.2-MILESTONE-AUDIT.md` — `nyquist` block (lines 37–41) and
  "## Nyquist Compliance" table (≈156–167): D-11's amendment site; informational note 4.
- `.planning/milestones/v0.2-phases/07-foundation-generalized-edge-selection-regression-fixture/`
  and `08-hex-bore/` — the PLAN/SUMMARY/VERIFICATION files the audit reconstructs from
  (07: 2 plans; 08: 4 plans; both `07-/08-VERIFICATION.md` `status: passed`).

### The code
- `src/spur/model.py` — `_gear_blank` (190–193, `extrudeLinear -> Solid`),
  `_cut_face_recesses` (196–214; ignore 213 and the comment 211–212), `_cut_bore`
  (217–241; ignores 237, 239), `_cut_keyway` (244–265, a `cut` with no ignore — `Solid`
  arg), `_cut_body` (365–394), `_chamfer_tips` (397–413; ignore 411), `_ring` (418–420;
  ignore 420), `_groove_floor_edges`/`_bore_rim_edges`/`_tip_edges` (423–505: the D-15
  guard messages D-03 echoes), `_build` (510–522: the end-of-pipeline `Solids()` assertion
  D-01 mirrors), `_build_checked` (525–532: the catch-all that would mis-render a
  `TypeError`).
- `src/spur/build_errors.py` — `BuildError`.
- `pyproject.toml` — `[tool.mypy]` (strict, `disallow_any_explicit`, the L21 comment),
  `[[tool.mypy.overrides]]` (≈111–115: D-04's edit), `[tool.ruff.lint]` `select` (RUF100
  stays), `[tool.coverage.report] fail_under = 96`.
- `Makefile` — `no-fake-done` (63–68: D-05's one new line), `typecheck` (D-04's gate
  reads its output), `test` (`-n 8 --cov`).
- `tests/test_model.py` — `BuildError` assertions at 242, 419, 604, 686, 702, 826, 866
  (the message-matching shape D-06 reuses); `tests/test_calc.py:1472`,
  `tests/test_cli.py:423` (the two test-side ignores that keep D-05 scoped).
- `tests/regression/pre_v0_2.json`, `tests/regression/test_pre_v0_2.py` — byte-unchanged;
  the replay stays green.
- `.venv/lib/python3.12/site-packages/cadquery/occ_impl/shapes.py` lines 426 (`Shape`),
  1414 (`Shape.cut -> Shape`), 3971–3989 (`Mixin3D.fillet/chamfer -> Any`), 4164
  (`Solid(Shape, Mixin3D)`), 4768/4886 (`Compound`, `Compound.cut -> Compound`);
  `cadquery/cq.py:411` (`val() -> CQObject`). Read, never edited.

### Process
- `docs/HOW_TO_DEVELOP.md` §4/§6/§7/§8 — branch per phase, PR, cross-CLI review, land.
- `.planning/STATE.md` "Operator Next Steps" — the PR #18 note is stale (merged as
  `085e5a6`); the commit-timeout rule stands.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `_build`'s `len(solids) != 1 or not solids[0].isValid()` → `BuildError` — the
  assert-positively precedent D-01's helpers follow; `_groove_floor_edges`/
  `_bore_rim_edges`/`_tip_edges` raise on an empty selection "never an answer" (D-15) —
  the message register D-03 matches.
- `tests/test_model.py`'s `pytest.raises(BuildError, match=...)` rows — the shape for the
  two refusal tests; `cq.Face`/`cq.Vector` constructors need no kernel build.
- 10-02's rule (STATE.md Phase 10): assign a `Mixin3D` call's `Any` result to a
  `cq.Shape` variable before returning — `_chamfer_tips` already does; `_body(solid)
  .chamfer(...)` slots into the same line.
- `make no-fake-done`'s `git grep -nE … -- '*.py' …` line — D-05 adds a sibling scoped to
  `src/spur/`.
- 13 D-09 / 15 D-01 checkpoint-with-the-numbers shape — D-09's `must` exception
  checkpoint; 15 D-16's "two-commit retirement when a file cannot carry its own sha" — not
  needed here (the debt sha is the code commit's own, recorded in the file in that
  commit as 14/15 did).
- `13-VALIDATION.md`/`15-VALIDATION.md` — what a filled per-task map looks like in this
  repo, for the executor's post-check of 07/08.

### Established Patterns
- Vendor objects stop at `model.py`; a vendor *type* quirk now stops at two named
  boundaries inside it (L21's "a library's own alias keeps the library's `Any`" — here the
  `Any` is absorbed at the helper and the pipeline sees `cq.Shape`).
- A claim is measured, dated and cited in a comment or `Lxx`, never re-estimated — the
  runtime-type measurement goes into the helper comment and L35.
- The planning record's own false sentence is corrected in the PR that discovers it
  (14 D-07, 15 D-01/D-13) — D-12.
- Debt retires in the fixing commit: status, sha, `git mv`, INDEX row — D-14.
- The decision log is append-only; an amendment is a new entry naming the old one — D-13.
- No formatter (L16): `pyproject.toml` and Makefile edits hand-aligned.
- A human-action checkpoint names the exact command, the expected observable, and the
  fallback (13 D-06's host-prep, 15-05's draft-PR step) — D-08.

### Integration Points
- `src/spur/model.py` — two helpers near "picking kernel geometry back out"; five call
  sites; three comments replaced.
- `tests/test_model.py` (or a sibling) — two tests.
- `Makefile` `no-fake-done`; `pyproject.toml` override.
- `docs/tech_debt/` → `resolved/` + INDEX; `docs/architecture/solid-model/implementation.md`;
  `docs/architecture/decision_log.md` (L35).
- `.planning/milestones/v0.2-phases/07-*/07-VALIDATION.md`, `08-hex-bore/08-VALIDATION.md`
  (written by `validate-phase`, committed by the human); `v0.2-MILESTONE-AUDIT.md` (D-11).
- `.planning/REQUIREMENTS.md`, `ROADMAP.md` (D-12 via tooling), `PROJECT.md` at transition.

</code_context>

<specifics>
## Specific Ideas

**The five sites today (`src/spur/model.py`, HEAD `085e5a6`):**

| Line | Call | Code | Why mypy objects |
|---|---|---|---|
| 213 | `solid.fillet(fillet, _groove_floor_edges(...))` | `attr-defined` | `solid: cq.Shape`; `fillet` is `Mixin3D`'s |
| 237 | `solid.cut(hole.val())` | `arg-type` | `val()` is `Vector \| Location \| Shape \| Sketch`; `cut` wants `Shape` |
| 239 | `solid.chamfer(p.bore_chamfer, None, _bore_rim_edges(solid, p))` | `attr-defined` | as 213 |
| 411 | `solid.chamfer(c, None, _tip_edges(...))` | `attr-defined` | as 213 |
| 420 | `return (… .extrude(height).val())` from `_ring -> cq.Shape` | `return-value` | as 237 |

**Measured runtime types (default `GearParams()`, 2026-10-04):** `_gear_blank` → `Solid`;
`_cut_face_recesses` → `Compound`; `_cut_bore` → `Compound`; `_cut_keyway` (off) →
`Compound` (input passed through); `_cut_body` (off) → `Compound`; `_chamfer_tips` (off) →
`Compound`. `cq.Solid.makeBox(...).cut(cq.Solid.makeCylinder(...))` → `Compound`. `_ring(5,
8, 0, 2)` → `Solid`. `inspect.signature(cq.Solid.extrudeLinear).return_annotation` →
`Solid`.

**D-03 draft message:** `Geometry kernel returned a {name} where a solid body was expected:
a modelling defect in the build pipeline, not a parameter problem.` — `{name}` is
`type(shape).__name__` (`Face`, `Vector`, …).

**D-05 draft line (sibling of `Makefile:64`):** a second `git grep -nE 'type: ignore' --
'src/spur/*.py'` guarded by the same `if … then … exit 1` shape, with its own sentence
("a suppression in `src/spur` is unfinished work: narrow the type, or file it in
`docs/tech_debt/`"). Wording Claude's.

**D-08 checkpoint text must include:** `/clear`; `/gsd-validate-phase 7`; at "Fix all
gaps / Skip — mark manual-only / Cancel" answer "Skip — mark manual-only"; if `gsd_run
query commit` is killed at 30 s, `git add .planning/milestones/v0.2-phases/07-*/07-VALIDATION.md
&& git commit -m "docs(phase-07): add validation strategy"` and wait for the hook; repeat
for 8; report both `nyquist_compliant` values and the gap tables verbatim.

**Test-side `type: ignore` inventory (D-05's scope evidence):** `tests/test_calc.py:1472`,
`tests/test_cli.py:423` (both `arg-type` on `GearParams.model_construct(**kw)`),
`tests/test_records.py:115` (a docstring mention), `.planning/phases/13-latency-bar/
investigation/run_experiment.py:167`. None under `src/`, `bench/`, `scripts/`, `docker/`.

**Host (discuss time):** `.venv` Python 3.12.13, cadquery 2.8.0, cadquery-ocp 7.9.3.1.1,
pytest 9.1.1; `make verify` 927 tests at ~64 s (`-n 8`, coverage 97.21 %, L34).

</specifics>

<deferred>
## Deferred Ideas

- **v0.3 Success Metric 1 vs the active `must` row.** `docs/tech_debt/INDEX.md` still has
  one `must` (`2026-10-02-same-slot-timeout-cleanup-race-produces-undocumented-500.md`,
  Phase 13 D-17, no `src/` change by decision, trigger named) and no v0.3 REQ covers it.
  SM1 ("zero `must` rows at close") cannot be met as scoped. Not Phase 16's; raised for
  `/gsd-audit-milestone` — fix in a gap phase, amend SM1 with the reason, or close as
  `tech_debt` like v0.1/v0.2.
- **A kernel-level test pinning the measured runtime types** (Solid → Compound) — not
  taken (D-06); L35 carries the dated measurement. Revisit if a cadquery bump changes what
  a boolean returns (the fixture replay would notice first).
- **A repo-wide `type: ignore` marker** — not taken (D-05); two deliberate test-side
  suppressions exist. Revisit if `tests/` loses them.
- **Re-typing the pipeline as `cq.Compound`** by wrapping `_gear_blank`'s solid — rejected,
  not deferred (D-02): a runtime geometry-path change for a typing reason, unmeasured.
- **Tests for Phase 7/8 gaps the audit may name** — by REQ, debt rows with triggers
  (D-09), not this milestone's work.
- **`/gsd-map-codebase` refresh** (`.planning/codebase/TESTING.md` "Warm run ~11 seconds",
  "No fail_under yet", `--paths bench`) — owed since Phase 13/15; process, not product.
- **The gsd commit-timeout debt** — upstream setting is the trigger; every commit here is a
  plain `git commit` (D-15).
- **Open review items from 13/14/15** (`*-REVIEW-DISPOSITION.md`) — carried in STATE.md;
  not folded into this phase.
- `.planning/STATE.md`'s "PR #18 is still a draft" note is stale (merged `085e5a6`) —
  corrected by the state update this session records.

</deferred>

---

*Phase: 16-typing-validation-debt*
*Context gathered: 2026-10-04*
