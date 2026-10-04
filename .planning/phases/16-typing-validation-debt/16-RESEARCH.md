# Phase 16: Typing & Validation Debt - Research

**Researched:** 2026-10-04
**Domain:** mypy `--strict` narrowing at a vendored-kernel (CadQuery) boundary; a process-only Nyquist retro-validation of two archived phases; planning-record corrections
**Confidence:** HIGH (the narrowing was prototyped end to end in a scratch copy; the gsd phase-resolution claim was run live; three CONTEXT sentences are corrected below)

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

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

### Deferred Ideas (OUT OF SCOPE)
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
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| REQ-model-py-no-type-ignore | `src/spur/model.py` carries zero `# type: ignore`; `make verify` green under `--strict` + `disallow_any_explicit`; fixture byte-unchanged; debt file retires with sha and corrected line refs | Prototype in a scratch copy: all five ignores removed with two `isinstance` helpers, `mypy src tests docker bench scripts` clean, `ruff check` clean, 289 model + regression tests green, fixture byte-identical (Findings 1-4). Mechanism, pitfalls (Findings 5-9) and the sha-follow-up correction (Finding 10) below. |
| REQ-nyquist-phases-7-8 | `VALIDATION.md` for Phases 7 and 8 under `milestones/v0.2-phases/`, produced by `/gsd-validate-phase`; discovery only | `init.phase-op 7` / `8` run live: both resolve to `.planning/milestones/v0.2-phases/...` with `has_plans: true` and no VALIDATION.md, so State B applies (Findings 11-13). The ASSUMPTION is now VERIFIED, with one residual (`nyquist_compliant` value after "Skip" is LLM-judged, not computed). |
</phase_requirements>

## Summary

Phase 16 is two small, independent debt items plus record-keeping. Neither needs a new library. The narrowing is feasible exactly as CONTEXT D-01/D-02 specify: I applied it to a scratch copy of the repo (the real tree was not touched). Two helpers (`_body`, `_shape_of`) removed all five `# type: ignore`s, and `mypy src tests docker bench scripts` read `Success: no issues found in 37 source files` under the project's `strict` + `disallow_any_explicit` config. `ruff check` passed. With the two proposed refusal tests added, `tests/test_model.py` + `tests/regression` ran 289 passed against the scratch `src/` (confirmed via `PYTHONPATH`, `spur.__file__` pointed at the scratch tree), and `pre_v0_2.json` was byte-identical. A negative control (un-narrowing one chamfer site) reproduced the original `attr-defined` error, so the green is real.

The research found four things CONTEXT does not say, and the planner must act on them. (a) `_gear_blank -> cq.Solid` is not free: it breaks `_build` with five `[assignment]` errors, because `solid` is inferred as `Solid` and every later step returns `cq.Shape`. Leave it `cq.Shape`. (b) The D-03 message, written as one f-string line in each helper, fails ruff E501 (174 > 100). Share one wrapped constant. (c) No helper comment or docstring under `src/spur/` may contain the literal text `type: ignore`, or D-05's new grep refuses it. (d) CONTEXT D-14 says the debt's sha is "recorded in the file in that commit as 14/15 did". git shows the opposite: a commit cannot embed its own sha, and 14/15 used a second small commit ("record the retiring commit's sha in the ... debt": `775ee6f`, `b00c44c`, `b8926e7`, `05668ef`). SC3's "retires with its sha" needs that follow-up commit.

The Nyquist half is process-only and now verified: gsd resolves archived phase dirs, `validate-phase` State B applies to both, and the Nyquist hook is active. The residual unknown is the `nyquist_compliant` value the skill writes after the human answers "Skip — mark manual-only". No code computes that field (`grep` over `~/.claude/gsd-core` finds it only in two workflow files and the template), so the orchestrating model decides it. Phase 13's VALIDATION has four Manual-Only rows and still reads `nyquist_compliant: true`, so either value is plausible. D-10's "record as read" wording is the right posture.

**Primary recommendation:** Implement D-01..D-07 as written with four amendments: keep `_gear_blank -> cq.Shape`, share one wrapped message constant, keep `type: ignore` out of `src/spur` comments, and plan a second one-line "record the retiring commit's sha" commit.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Narrowing the kernel's `Shape` typing | Build worker (`src/spur/model.py`, the only module allowed to import `cadquery`/`OCP`) | — | Vendor types stop at their boundary (CLAUDE.md "Code style"); the helpers live inside `model.py`, nothing escapes. |
| Invariant refusal on a non-body shape | Build worker (`model.py`, raises `BuildError`) | API (`app.py` maps `BuildError` to 422) and CLI (exit 1) | `BuildError` already crosses the serving boundary without importing the kernel (`build_errors.py`). The message reaches users through the existing mapping. |
| Pinning "no new `type: ignore` under `src/spur/`" | Gate (`Makefile` `no-fake-done`) | mypy `warn_unused_ignores` retires stale ones | The grep refuses a new coded ignore; mypy's `unused-ignore` refuses a stale one. |
| Mypy override for `OCP.*` | Gate config (`pyproject.toml`) | — | Only OCP lacks `py.typed`/stubs. |
| Phase 7/8 Nyquist validation | Human at an interactive skill (`/gsd-validate-phase`) | Executor verifies and records | The skill gates with `AskUserQuestion` and commits through a helper the hook outruns. |
| Record corrections (audit, ROADMAP, REQUIREMENTS, L35, debt) | Planning/docs tier | — | No runtime tier is involved. |

## Standard Stack

No new packages. Versions below are what the repo runs today.

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| cadquery | 2.8.0 | the kernel whose `Shape`/`Mixin3D`/`Workplane.val()` annotations are being narrowed | pinned by the fixture and `requirements.txt` (L34) [VERIFIED: `.venv` `pip list`] |
| mypy | 2.3.1 | `--strict` + `disallow_any_explicit` gate | the gate (L21) [VERIFIED: `mypy --version`] |
| ruff | 0.16.8 | lint incl. E501 and RUF; `isinstance(x, A \| B)` form passed `ruff check` | the gate [VERIFIED: `ruff --version`] |
| pytest / pytest-xdist / pytest-cov | 9.1.1 / 3.8.0 / 7.1.0 | the two new tests; `fail_under = 96` | existing [VERIFIED: `pytest --version`, `pip list`] |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `isinstance` helpers (D-01) | `typing.cast` | rejected in D-01; `cast` cannot be wrong at runtime in a way anything notices |
| `isinstance` helpers | local `.pyi` for cadquery | rejected in D-02 (stronger claim than the library makes) |

**Installation:** none.

**Version verification:** read from the project `.venv` this session; nothing is installed.

## Package Legitimacy Audit

Not applicable: this phase installs no external package. Step 1-3 of the legitimacy gate were not run because there is nothing to check. `requirements.txt` and `[dev]` extras are unchanged by every decision in CONTEXT.

**Packages removed due to [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** none

## Architecture Patterns

### System Architecture Diagram

```
GearParams (validated once, at the boundary)
   |
   v
_build(p) -- model.py, worker process, under _LOCK
   |
   |  solid: cq.Shape  <--- pipeline annotation stays cq.Shape (what Shape.cut promises)
   v
_gear_blank -> _cut_face_recesses -> _cut_bore -> _cut_keyway -> _cut_body -> _chamfer_tips
 (Solid)        |  .cut(_ring)         |  .cut(hole)                              |
                |    ^                 |    ^                                     |
                |    |                 |    |                                     |
                |  _ring() ---- _shape_of(Workplane) -> cq.Shape  [boundary 2: .val() union -> Shape]
                |                      |                                          |
                v                      v                                          v
          _body(solid).fillet     _body(solid).chamfer                  _body(solid).chamfer
                \_______________________|_____________________________________/
                       [boundary 1: Shape -> Solid | Compound, the only types carrying Mixin3D]
   |
   |  each boundary: isinstance true -> narrowed value; false -> BuildError
   |  (names the invariant, "a modelling defect ... not a parameter problem")
   v
_build's end check: len(solid.Solids()) == 1 and isValid()  -> BuildError otherwise
   |
   v
BuildError  --> app.py: HTTP 422 (type "build_error"), WARNING log;  cli.py: exit 1
```

Record/validation flow (no code):

```
executor (plan 2) --halts--> HUMAN: /clear ; /gsd-validate-phase 7 ; Step 4 "Skip - mark manual-only"
   ; plain git commit if gsd_run commit is killed ; repeat for 8
        |
        v
executor post-check: 07-VALIDATION.md / 08-VALIDATION.md at status: validated;
nyquist_compliant read as written; gap count == debt rows filed (nice, one file per phase)
        |
        v
amend v0.2-MILESTONE-AUDIT.md nyquist block (dated) ; correct REQ/ROADMAP sentences ; L35
```

### Recommended Project Structure
```
src/spur/model.py            # + _body, _shape_of near "picking kernel geometry back out"; 5 sites edited
tests/test_model.py          # + 2 refusal tests (imports _body, _shape_of next to the existing private imports)
Makefile                     # no-fake-done: + one git grep for `type: ignore` under src/spur/*.py
pyproject.toml               # [[tool.mypy.overrides]] module = ["OCP.*"], comment corrected
docs/tech_debt/{active -> resolved}/2026-09-21-cadquery-shape-typing.md, INDEX.md
docs/architecture/solid-model/implementation.md:29-33
docs/architecture/decision_log.md   # L35 (plan 3)
.planning/milestones/v0.2-phases/07-*/07-VALIDATION.md, 08-hex-bore/08-VALIDATION.md  # written by the skill
```

### Pattern 1: isinstance narrowing helper that raises `BuildError`
**What:** One function per kernel-typing quirk; the helper's `isinstance` is both the narrowing mypy needs and the runtime assertion.
**When to use:** the three `fillet`/`chamfer` sites (need `Mixin3D`) and the two `.val()` sites (need `Shape`).
**Example (prototyped; mypy, ruff and 289 tests green in the scratch copy):**
```python
# Source: scratch prototype 2026-10-04, applied to a copy of src/spur/model.py
_NOT_A_BODY = ("Geometry kernel returned a {} where a solid body was expected: a modelling "
               "defect in the build pipeline, not a parameter problem.")


def _body(shape: cq.Shape) -> cq.Solid | cq.Compound:
    # comment here: measured runtime types + date; Mixin3D lives on Solid and Compound only
    if not isinstance(shape, cq.Solid | cq.Compound):
        raise BuildError(_NOT_A_BODY.format(type(shape).__name__))
    return shape


def _shape_of(wp: cq.Workplane) -> cq.Shape:
    value = wp.val()   # Vector | Location | Shape | Sketch
    if not isinstance(value, cq.Shape):
        raise BuildError(_NOT_A_BODY.format(type(value).__name__))
    return value
```
Call sites:
```python
solid = _body(solid).fillet(fillet, _groove_floor_edges(solid, (r_in, r_out), floor_z))
solid = solid.cut(_shape_of(hole))
solid = _body(solid).chamfer(p.bore_chamfer, None, _bore_rim_edges(solid, p))
solid = _body(solid).chamfer(c, None, _tip_edges(solid, pr.ra, p.face_width))
return _shape_of(cq.Workplane("XY").workplane(offset=z0)
                 .circle(r_out).circle(r_in).extrude(height))      # _ring
```
`Mixin3D.fillet/chamfer` return `Any`; assigning to the `cq.Shape`-typed `solid` before `return` satisfies `warn_return_any` (the three fillet/chamfer sites already do this).

### Anti-Patterns to Avoid
- **`_gear_blank -> cq.Solid` without touching `_build`:** `solid = _gear_blank(...)` makes mypy infer `Solid`, and every later `solid = _cut_...(...)` (returns `cq.Shape`) errors. See Pitfall 1.
- **Writing the phrase `type: ignore` in a helper comment under `src/spur/`:** D-05's grep refuses it. See Pitfall 3.
- **Committing the Makefile pin before the ignores are gone:** the pre-commit hook runs `make verify`, so the pin makes that commit red. This is why D-07's single commit is mandatory, not a style choice.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| "Is this a Solid/Compound?" | a type-name string compare | `isinstance(shape, cq.Solid \| cq.Compound)` | mypy narrows on it; subclass-safe |
| Retire a debt file | a custom script | the existing mechanics: `git mv`, `Status: resolved`, `Resolved in:`, INDEX row (TEMPLATE.md's trailing comment) | precedent in 13/14/15 |
| Phase directory lookup for the archived phases | a temporary copy under `.planning/phases/` | `gsd_run query init.phase-op N` already resolves it | verified live (Finding 11) |
| ROADMAP section edit | a whole-file write | scoped Edit + `gsd_run query roadmap milestone-scope` before/after (edit-phase's `write_updated_phase`) | the workflow rolls back if the milestone window changes |

**Key insight:** the "fix" here is a runtime assertion that mypy can read, not a bigger type system. The pipeline's own annotations deliberately stay at what the library promises (`Shape`).

## Runtime State Inventory

Not a rename/refactor/migration phase in the data sense: no stored data, live-service config, OS registration or secret carries any string this phase changes. Explicit answers per category:

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | None — verified: no field, key or schema is renamed (D-16 forbids a `GearParams`/`DerivedDimensions` change) | none |
| Live service config | None — no external service names a symbol this phase touches | none |
| OS-registered state | None — the pre-commit hook invokes `make verify`; its name and entry are unchanged | none |
| Secrets/env vars | None — no env var is added or renamed | none |
| Build artifacts / installed packages | `.mypy_cache` can mask the D-04 before/after comparison | clear the cache (or use `--no-incremental`) for both runs |

## Findings (verified this session)

**Findings 1-4 — the narrowing works as specified (prototype in a scratch copy; the repo was not edited)**

1. All five `# type: ignore` removed with the two helpers above; `mypy src tests docker bench scripts` → `Success: no issues found in 37 source files` [VERIFIED: scratch run, mypy 2.3.1]. Negative control: reverting only the `_chamfer_tips` site yields `src/spur/model.py:411: error: "Shape" has no attribute "chamfer"  [attr-defined]` [VERIFIED].
2. `ruff check src tests` → `All checks passed!` once the message lives in a wrapped constant [VERIFIED]. Before wrapping, two E501 hits (`Line too long (174 > 100)`), one per helper [VERIFIED].
3. Against the scratch `src/` (`spur.__file__` printed the scratch path): `tests/test_model.py tests/regression` → `289 passed`; `tests/regression/pre_v0_2.json` identical to the repo's (`diff -q`) [VERIFIED]. The full suite in the scratch copy showed 14 failures, all in `test_pr_land.py` (11), `test_bench.py` (2), `test_cli.py` (1). The `test_cli.py` failure was `FileNotFoundError: .../proto/README.md`, and a `test_bench.py` failure was `git rev-parse --short HEAD` exit 128 (scratch has no `.git`). Those are scratch-copy artefacts [VERIFIED for those two files; the 11 `test_pr_land.py` failures were not individually inspected, presumably they need `.github/`: ASSUMED]. The real gate (`make verify`) must still be run in the real tree by the executor.
4. Test shapes needing no kernel solid: `cq.Face.makePlane(1, 1)` returns a `Face`; `cq.Workplane("XY").val()` on an empty stack returns the plane origin, a `Vector` (`Workplane.val` source: `return self.objects[0] if self.objects else self.plane.origin`) [VERIFIED]. Both new tests ran green under `filterwarnings = error`.

**Finding 5 — kernel facts re-read this session** [VERIFIED: `inspect.signature` and source in `.venv`, cadquery 2.8.0]: `Shape.cut (self, *toCut: 'Shape', tol: 'float | None' = None) -> 'Shape'`; `Solid.cut is Shape.cut` is `True`; `Compound.cut(...) -> 'Compound'`; `Mixin3D.fillet (self: 'Any', radius: 'float', edgeList: 'Iterable[Edge]') -> 'Any'`; `Mixin3D.chamfer (self: 'Any', length: 'float', length2: 'float | None', edgeList: 'Iterable[Edge]') -> 'Any'`; `Workplane.val` returns `Union[Vector, Location, Shape, Sketch]` (source annotation `-> CQObject`); MROs `Solid -> Shape -> Mixin3D`, `Compound -> Shape -> Mixin3D`, `Face -> Shape` (no `Mixin3D`); `hasattr(cq.Shape, 'fillet')` is `False`; `cadquery/py.typed` exists. `Mixin3D.fillet` returns `self.__class__(fillet_builder.Shape())`, so a `Compound` stays a `Compound`: the runtime geometry is unchanged by the helper.

**Finding 6 — the five sites today** [VERIFIED: `grep -n "type: ignore" src tests` this session]: `src/spur/model.py:213, 237, 239, 411, 420`; test-side `tests/test_cli.py:423`, `tests/test_calc.py:1472` (and a docstring mention at `tests/test_records.py:115`). ROADMAP/REQUIREMENTS cite 212/236/238/410/419 (stale by one line each). Verbatim line 213: `solid = solid.fillet(fillet, _groove_floor_edges(solid, (r_in, r_out), floor_z))  # type: ignore[attr-defined]`.

**Finding 7 — `RUF100` does not govern `# type: ignore`.** It concerns `# noqa`. Probe: `ruff check --select RUF100` on a file with an unneeded `# type: ignore[assignment]` printed `All checks passed!`. What retires a stale `type: ignore` is mypy `--strict` (`warn_unused_ignores`): `error: Unused "type: ignore" comment  [unused-ignore]` [VERIFIED]. `enable_error_code = ["ignore-without-code", ...]` is in `pyproject.toml`. SC2's "with `RUF100` still on" is harmless (it stays on) but it is not the mechanism; the corrected REQ text can say so.

**Finding 8 — D-04 gate result in the scratch copy:** with `module = ["OCP.*"]` (cadquery dropped), `mypy src tests docker bench scripts` with the cache present and with `.mypy_cache` deleted both print `Success: no issues found in 37 source files`, the same line as before the edit [VERIFIED: scratch]. The comparison is only one line of output, so clear the cache for both runs or it proves little.

**Finding 9 — `ruff` E501 exemption.** Line 213 is 118 characters today and `ruff check` passes; after removal it is ≤100. Observed in the scratch run; the reason (E501 exempting a line whose length is caused by a trailing pragma comment) is ASSUMED from ruff behaviour, not read from its docs this session. Consequence: no re-wrapping of the five call sites is needed, but the two message lines are not exempt.

**Finding 10 — the debt's sha cannot ride in its own commit.** CONTEXT D-14 and "Reusable Assets" say the sha is "recorded in the file in that commit as 14/15 did". Git history shows the pattern was two commits [VERIFIED: `git show`/`git log`]: `825095f` retired the root lead-in debt with `Resolved in: docs(14-01): state where the root lead-in really ends and retire its debt` (the commit subject), then `775ee6f` ("docs(14-01): record the retiring commit's sha in the root lead-in debt") changed that line and the INDEX cell to `825095f`. Same for `2aadcea`/`b8926e7` (15-02) and `6709953`/`05668ef` (13-07). The INDEX cell form in the Resolved table is `` `<sha>` — see the file's own `Resolved in:` field``. Plan a second, docs-only commit after the code commit. (CLAUDE.md's "same commit as the fix" is satisfied in the sense the precedent satisfied it: the move and the status flip are in the fix commit, the sha follows.) This is a correction of a CONTEXT sentence, not of a locked decision's intent.

**Finding 11 — gsd resolves archived phases (the flagged ASSUMPTION is verified).** `node ~/.claude/gsd-core/bin/gsd-tools.cjs query init.phase-op 7` printed `"phase_found": true`, `"phase_dir": ".../.planning/milestones/v0.2-phases/07-foundation-generalized-edge-selection-regression-fixture"`, `"padded_phase": "07"`, `"has_plans": true`, `"plan_count": 2`, `"has_verification": true`; for `8`: `"phase_dir": ".../.planning/milestones/v0.2-phases/08-hex-bore"`, `"plan_count": 4`. gsd-core 1.15.0 (`runtime-identity` printed `{"packageName":"@opengsd/gsd-core","version":"1.15.0"}`) [VERIFIED]. `validate-phase.md` Step 0 takes `phase_dir` from this call; Step 1's State B is `VALIDATION_FILE` empty and `SUMMARY_FILES` non-empty: both dirs hold `*-SUMMARY.md` (07: `07-01`, `07-02`; 08: `08-01`..`08-04`) and no `*-VALIDATION.md` [VERIFIED: `ls`]. Step 6 writes `${PHASE_DIR}/${PADDED_PHASE}-VALIDATION.md`, so the files land at `07-VALIDATION.md` and `08-VALIDATION.md` inside the archived dirs. `gsd_run loop render-hooks verify:post` lists `capId: nyquist`, `ref.skill: validate-phase`, `when: workflow.nyquist_validation` among `activeHooks`; `.planning/config.json` has no `workflow.nyquist_validation` key (absent = enabled) [VERIFIED].

**Finding 12 — what the skill does at the gate.** Step 3: "No gaps → skip to Step 6, set `nyquist_compliant: true`." Step 4: `AskUserQuestion` with "Fix all gaps" / "Skip — mark manual-only" / "Cancel". Step 6 sets `status: validated`. Step 7: `gsd_run query commit "docs(phase-${PHASE}): add/update validation strategy" --files "${PHASE_DIR}/${PADDED_PHASE}-VALIDATION.md"`, preceded by a `git add {test_files}; git commit` only if tests were added [VERIFIED: `validate-phase.md` read in full]. The skill file's `allowed-tools` include `AskUserQuestion` and `Agent`, i.e. it is interactive. No code sets `nyquist_compliant` after a Skip: the only mentions in `~/.claude/gsd-core` are `workflows/validate-phase.md`, `workflows/audit-milestone.md` and `templates/VALIDATION.md` [VERIFIED: `grep -rln`]. Therefore the value after "Skip" is [ASSUMED] unpredictable; Phase 13's `13-VALIDATION.md` has four Manual-Only rows and reads `status: validated`, `nyquist_compliant: true`, so a Skip-everything run can plausibly read `true` or `false`.

**Finding 13 — how the audit classifies the result** (`audit-milestone.md` §5.5): COMPLIANT = `status: validated` + `nyquist_compliant: true` + all tasks green; PARTIAL = `status: validated` + (`nyquist_compliant: false` or red/pending); MISSING = no file. How `overall` is computed is not stated; the v0.2 audit wrote `overall: partial` for 4 compliant + 2 missing [VERIFIED: audit text]. For D-11, recompute by the same convention and say so in the amendment; the all-compliant value of `overall` is [ASSUMED] to be `compliant`.

**Finding 14 — `BuildError` surfaces as 422 + WARNING, even for a defect.** `app.py:430` maps `BuildError` to `HTTPException(422, ... "type": "build_error")`; `records.build_failed` logs `BuildError` at WARNING ("the user's gear"). The three existing D-15 guards (`_groove_floor_edges`, `_bore_rim_edges`, `_tip_edges`) share this: their messages already say "a modelling defect in spur, not a conflict in these parameters" [VERIFIED: model.py:501-504, app.py, records.py]. D-03's new error follows that precedent and cannot fire from any settable field today, so the status code is a known trade-off, not a new one. Record it in L35 rather than add a new exception class (not in scope).

**Finding 15 — ROADMAP edits.** `edit-phase.md` refuses to edit a phase whose disk status is `in_progress`/`completed` unless `--force` is passed (`check_phase_status`). Once Phase 16 has plans its status is `planned`/`partial`, so `/gsd-phase edit 16` needs `--force` (Phase 15 was edited the same way). Alternative the executor can use directly: a scoped `Edit` of the Phase 16 section, `gsd_run query roadmap milestone-scope` before and after (it currently returns `scope: complete`, phases `13,14,15,16`), then `gsd_run query state.add-roadmap-evolution --phase 16 --action edited --note "..."` [VERIFIED: workflow text + live `milestone-scope` call].

## Common Pitfalls

### Pitfall 1: `_gear_blank -> cq.Solid` breaks `_build`
**What goes wrong:** five `error: Incompatible types in assignment (expression has type "Shape", variable has type "Solid")  [assignment]` at `_build`'s `solid = _cut_...(...)` lines (532-536 in the scratch copy) [VERIFIED].
**Why it happens:** `solid = _gear_blank(...)` fixes the variable's type to `Solid`; each later step returns `cq.Shape`.
**How to avoid:** leave `_gear_blank -> cq.Shape` (CONTEXT lists it as discretion; choose this). If the planner wants `Solid`, `_build` must declare `solid: cq.Shape = _gear_blank(...)`, which is more edit for no gain.
**Warning signs:** `[assignment]` errors in `_build` after a one-word annotation change.

### Pitfall 2: the message line is too long
**What goes wrong:** `E501 Line too long (174 > 100)` twice [VERIFIED].
**How to avoid:** one module-level wrapped constant used by both helpers (D-03 asks for one message anyway). The test asserts the full string with `==` on `str(exc_info.value)`, not `match=`: `match` is a regex `search`, so `.` is a wildcard and a wrong prefix or suffix can pass (the 10-REVIEW CR-01 point). Existing tests use `match=` for prefixes; this one should not.

### Pitfall 3: `type: ignore` in a comment under `src/spur/`
**What goes wrong:** the new `no-fake-done` line greps `type: ignore` over `src/spur/*.py` and reports any comment that says it, e.g. a helper comment "this replaces a type: ignore". Today the five hits are all real ignores [VERIFIED: `git grep -nE 'type: ignore' -- 'src/spur/*.py'` → 5 lines].
**How to avoid:** word the helper comments without the literal phrase ("mypy suppression", "the old suppressions"). Check: the same grep must return nothing after the change.

### Pitfall 4: ordering inside the single code commit
**What goes wrong:** the hook runs `make verify` on every commit, including `no-fake-done`. A commit that has the Makefile pin but still has an ignore, or the reverse ordering with a split, fails the hook.
**How to avoid:** one commit (D-07). To show the pin is not decorative, run the new grep (or `make no-fake-done`) once against the unedited `model.py` (expect exit 1 and 5 hits: RED), then after the edit (GREEN). Record the RED output in the summary; do not commit it.

### Pitfall 5: a stale mypy cache hides the D-04 diff
**How to avoid:** `rm -rf .mypy_cache` (or `mypy --no-incremental`) before both the "before" and "after" runs of `make typecheck`.

### Pitfall 6: the retiring commit cannot name its own sha
See Finding 10. Plan the follow-up docs-only commit; its own hook run is ~64 s (plain `git commit`, never `gsd_run query commit`).

### Pitfall 7: the human's `/gsd-validate-phase` commit is killed at 30 s
**What goes wrong:** Step 7's `gsd_run query commit` times out against the ~64 s hook; an orphaned `pre_commit hook-impl` keeps running (STATE.md Blockers; the debt `2026-09-25-gsd-commit-timeout-kills-cold-verify-hook.md`).
**How to avoid:** the checkpoint tells the human the fallback (CONTEXT specifics): `git add <the 0N-VALIDATION.md>` then plain `git commit -m "docs(phase-07): add validation strategy"`, and wait for the orphaned hook before touching the tree. [CITED: STATE.md, debt file; not re-measured this session.]

### Pitfall 8: executor asserts `nyquist_compliant: true`
**What goes wrong:** the audit amendment (D-11) and L35 would state a value nobody measured.
**How to avoid:** read both frontmatters with `grep -E '^(status|nyquist_compliant):'`, write the audit block from what is read (`partial_phases` if `false`, `compliant_phases` if `true`), and keep SC4's corrected wording (D-10) value-neutral.

### Pitfall 9: ROADMAP edit refused or scope broken
See Finding 15: `--force` is required through the skill path; the new SC text must not contain a heading with a version token, a status emoji, or the word "Milestone" at heading level, or the scope check rolls the write back.

## Code Examples

### The `no-fake-done` sibling line (D-05; wording is Claude's discretion)
```make
# Source: Makefile:63-68 shape; the grep verified to return 5 hits on today's tree
	@if git grep -nE 'type: ignore' -- 'src/spur/*.py'; then \
	  echo "make: a suppression in src/spur is unfinished work. Narrow the type, or file it in docs/tech_debt/."; \
	  exit 1; \
	fi
```
Put it inside the existing `no-fake-done` target after the current `if ... fi` block, as a second `@if`. Hand-align (L16: no formatter). `git grep` pathspec `'src/spur/*.py'` matches nested files too (fnmatch without path-separator semantics), and only tracked files are scanned.

### The two refusal tests (no kernel solid built)
```python
# Source: scratch prototype, green under filterwarnings = error
def test_a_non_body_shape_in_the_build_pipeline_is_named_as_a_modelling_defect() -> None:
    with pytest.raises(BuildError) as exc_info:
        _body(cq.Face.makePlane(1, 1))
    assert str(exc_info.value) == (
        "Geometry kernel returned a Face where a solid body was expected: a modelling "
        "defect in the build pipeline, not a parameter problem.")


def test_a_workplane_value_that_is_not_a_shape_is_named_as_a_modelling_defect() -> None:
    with pytest.raises(BuildError) as exc_info:
        _shape_of(cq.Workplane("XY"))   # empty stack: val() returns the plane origin, a Vector
    assert str(exc_info.value) == (
        "Geometry kernel returned a Vector where a solid body was expected: a modelling "
        "defect in the build pipeline, not a parameter problem.")
```
Imports go in `tests/test_model.py`'s existing `from spur.model import (...)` block: `_body` before `_bore_rim_edges`, `_shape_of` between `_groove_floor_edges` and `_tip_edges` (isort order; ruff `I` passed in the scratch copy). Collected-test count today: `927 tests collected`; after: 929 [VERIFIED for 927; 929 follows from adding two].

### Post-check commands for plan 2 (read, never assert)
```bash
grep -E '^(status|nyquist_compliant):' \
  .planning/milestones/v0.2-phases/07-*/07-VALIDATION.md \
  .planning/milestones/v0.2-phases/08-hex-bore/08-VALIDATION.md
git diff --stat 085e5a6 -- tests/        # no tests/ change under this requirement (D-10)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| "Cast once at `.val()`" (debt file, REQ, ROADMAP SC1) | two `isinstance` helpers | CONTEXT D-01/D-02, 2026-10-04 | cast reaches only 2 of 5 sites because `Shape.cut -> Shape` returns the wide type whatever goes in |
| override `cadquery.*` + `OCP.*` | `OCP.*` only | D-04 | cadquery ships `py.typed` [VERIFIED]; OCP has no `.pyi`/`py.typed` (CONTEXT measurement: 0 `.pyi`) |

**Deprecated/outdated:** the debt file's "Related files" line refs (195/219/221/264/273), REQ/ROADMAP's 212/236/238/410/419, and `pyproject.toml`'s comment "The CAD kernel ships no type information".

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The `nyquist_compliant` value after "Skip — mark manual-only" is chosen by the model running the skill; either `true` or `false` is possible. (Confirmed that no code computes it; the resulting value is unknown until the human runs it.) | Findings 12, Pitfall 8 | If the plan or SC4 text presumes `true`/`false`, the audit amendment and L35 state something unmeasured. Mitigated by D-10's "reads what the audit measured". |
| A2 | `overall` in the v0.2 audit's `nyquist` block becomes `compliant` when all six phases are compliant (the workflow never defines `overall`) | Finding 13 | Wrong word in an archived record; low. The amendment should say how it was derived. |
| A3 | The reason a 118-char line with a trailing pragma passes E501 is ruff's pragma exemption | Finding 9 | None for planning: the observed behaviour (line passes today, wrapped message needed) is verified; only the explanation is assumed. |
| A4 | The 11 `test_pr_land.py` failures in the scratch full-suite run are scratch artefacts (missing `.github/` or similar), not related to the narrowing | Finding 3 | If wrong, the real `make verify` would show it; the executor runs the real gate anyway. |
| A5 | The 30 s `gsd_run query commit` timeout and ~64 s hook figures are carried from STATE.md/debt file, not re-measured here | Pitfall 7 | Low; the fallback is the same either way. |

## Open Questions

1. **How is the debt's sha recorded?**
   - What we know: a commit cannot contain its own sha; 13/14/15 used a follow-up docs-only commit (Finding 10).
   - What's unclear: CONTEXT D-14 says otherwise in one sentence.
   - Recommendation: plan the follow-up commit ("docs(16-01): record the retiring commit's sha in the Shape-typing debt"), with `Resolved in:` holding the commit subject in the fix commit, like 14-01 did. Note the correction in the plan's summary.
2. **Helper-message sharing vs two literals.**
   - Recommendation: one `_NOT_A_BODY` constant (Pitfall 2). It stays inside D-03's "tune the words, not the content".
3. **`nyquist_compliant` outcome for 7 and 8.**
   - What's unclear: see A1.
   - Recommendation: no plan text depends on it; the executor reads and records.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `.venv` Python 3.12 + cadquery | tests, mypy | ✓ | Python 3.12.13, cadquery 2.8.0 | — |
| mypy / ruff / pytest (+xdist, cov) | `make verify` | ✓ | 2.3.1 / 0.16.8 / 9.1.1 (+3.8.0, 7.1.0) | — |
| gsd-core tools | `init.phase-op`, `roadmap milestone-scope` | ✓ | 1.15.0 | — |
| `/gsd-validate-phase` skill | plan 2 (human action) | ✓ (skill file present, `allowed-tools` incl. `AskUserQuestion`, `Agent`) | — | none; dropping the requirement is outside D-08 |
| Docker | `make check` only | not probed | — | `make verify` needs none |

**Missing dependencies with no fallback:** none found.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.1.1 with pytest-xdist 3.8.0 and pytest-cov 7.1.0 |
| Config file | `pyproject.toml` (`[tool.pytest.ini_options]`, `[tool.coverage.*]`, `fail_under = 96`) |
| Quick run command | `make test PYTEST_ARGS="tests/test_model.py -k 'non_body or not_a_shape or modelling_defect' -q -n0 --no-cov"` |
| Full suite command | `make verify` (ruff, mypy, lint-imports, no-fake-done, pytest `-n 8 --cov`; ~64 s, 927 tests today, 929 after) |

`PYTEST_ARGS` comes last in the Makefile recipe, so `-n0 --no-cov` win (Makefile comment lines 70-77).

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| REQ-model-py-no-type-ignore (SC1) | zero `type: ignore` in `src/spur/` | gate (grep) | `! git grep -nE 'type: ignore' -- 'src/spur/*.py'` and `make no-fake-done` | ❌ Wave 0: the Makefile line is part of the change |
| REQ-model-py-no-type-ignore (SC1) | `_body` refuses a `Face` with the D-03 string | unit | `make test PYTEST_ARGS="tests/test_model.py -k non_body -q -n0 --no-cov"` | ❌ Wave 0 (new test) |
| REQ-model-py-no-type-ignore (SC1) | `_shape_of` refuses a `Vector` with the D-03 string | unit | `make test PYTEST_ARGS="tests/test_model.py -k not_a_shape -q -n0 --no-cov"` | ❌ Wave 0 (new test) |
| REQ-model-py-no-type-ignore (SC2) | strict + `disallow_any_explicit` stays green | static | `rm -rf .mypy_cache && make typecheck` (expect `Success: no issues found in 37 source files`) | ✅ |
| REQ-model-py-no-type-ignore (SC2) | geometry unchanged | integration | `make test PYTEST_ARGS="tests/regression tests/test_model.py -q --no-cov"` then `git diff --exit-code 085e5a6 -- tests/regression/pre_v0_2.json` | ✅ |
| REQ-model-py-no-type-ignore (D-04) | removing `cadquery.*` from the override changes no mypy output | static | `make typecheck` captured before and after, cache cleared both times | ✅ |
| REQ-model-py-no-type-ignore (SC3) | debt file in `resolved/`, `Status: resolved`, `Resolved in: <sha>`, line refs 213/237/239/411/420, INDEX row moved | structural | `test -f docs/tech_debt/resolved/2026-09-21-cadquery-shape-typing.md && ! test -e docs/tech_debt/active/2026-09-21-cadquery-shape-typing.md && grep -E '^(Status|Resolved in):' docs/tech_debt/resolved/2026-09-21-cadquery-shape-typing.md`; `grep -n 'cadquery-shape-typing' docs/tech_debt/INDEX.md` | manual-structural (no test) |
| REQ-nyquist-phases-7-8 (SC4) | both files exist at `status: validated` | structural | `grep -E '^(status\|nyquist_compliant):' .planning/milestones/v0.2-phases/07-*/07-VALIDATION.md .planning/milestones/v0.2-phases/08-hex-bore/08-VALIDATION.md` | ❌ produced by the human-run skill |
| REQ-nyquist-phases-7-8 (D-09) | gap count equals debt rows filed; no `tests/` change | structural | count the gap rows in each VALIDATION.md; `ls docs/tech_debt/active/*phase-0[78]-nyquist*`; `git diff --stat 085e5a6 -- tests/` limited to `tests/test_model.py` | manual-structural |
| REQ-nyquist-phases-7-8 (D-11) | audit block amended, dated | structural | `grep -n 'missing_phases\|amended' .planning/milestones/v0.2-MILESTONE-AUDIT.md` (expect `missing_phases: []`) | manual-structural |

Manual-only items and why: the `/gsd-validate-phase` runs (interactive gate by design, D-08); the content of the audit amendment and of L35 (prose; checked by reading against the two frontmatters).

### Sampling Rate
- **Per task commit:** the quick command above plus `make lint typecheck` where Python changed; the pre-commit hook runs the full `make verify` on every real commit anyway.
- **Per wave merge:** `make verify`.
- **Phase gate:** `make verify` green, `git diff --exit-code 085e5a6 -- tests/regression/pre_v0_2.json` exits 0, `git grep -nE 'type: ignore' -- 'src/spur/*.py'` prints nothing, test count 929.

### Wave 0 Gaps
- [ ] two refusal tests in `tests/test_model.py` (covers SC1) — the only new test files/rows
- [ ] the `no-fake-done` Makefile line (covers the SC1 pin)
- No framework install, no new fixture, no conftest change: existing infrastructure covers the rest.

## Security Domain

`security_enforcement` is absent from `.planning/config.json` (treated as enabled). The change adds no input, route, dependency or secret.

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | none (no auth in the service, L04 / debt `no-authentication`) |
| V3 Session Management | no | none |
| V4 Access Control | no | none |
| V5 Input Validation | no change | parameters are still validated once at `GearParams`; the new error echoes a kernel class name (`type(shape).__name__`), never a parameter or user text |
| V6 Cryptography | no | none |
| V7 Error handling / logging | yes (minor) | the new message is deterministic text; `BuildError` is already logged at WARNING without a traceback (`records.build_failed`) |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Error text leaking internals | Information disclosure | message names only a vendor class (`Face`, `Vector`), consistent with existing guard messages; no path or traceback rides on the record |
| Gate erosion (a new suppression slips in unnoticed, as the fifth did in 10-02) | Tampering with the control | D-05's grep pin plus mypy `unused-ignore` |

## Sources

### Primary (HIGH confidence)
- Project files read this session: `src/spur/model.py` (lines 1-60, 185-290, 360-430, 500-550), `src/spur/build_errors.py`, `pyproject.toml`, `Makefile`, `.pre-commit-config.yaml`, `tests/test_model.py` (header, BuildError rows), `docs/tech_debt/active/2026-09-21-cadquery-shape-typing.md`, `docs/tech_debt/INDEX.md`, `docs/tech_debt/TEMPLATE.md`, `docs/architecture/solid-model/implementation.md`, `.planning/milestones/v0.2-MILESTONE-AUDIT.md`, `.planning/ROADMAP.md` (Phase 16 section), `.planning/REQUIREMENTS.md`, `.planning/STATE.md`, `13-/15-VALIDATION.md`, `09-VALIDATION.md` frontmatter.
- Installed packages in `.venv`: cadquery 2.8.0 (`inspect.signature`, `cq.py`/`shapes.py` source, `py.typed`), mypy 2.3.1, ruff 0.16.8.
- gsd-core 1.15.0 sources: `workflows/validate-phase.md`, `workflows/audit-milestone.md` §5.5, `workflows/edit-phase.md`, `templates/VALIDATION.md`, `skills/gsd-validate-phase/SKILL.md`; live `gsd-tools.cjs query init.phase-op 7|8`, `loop render-hooks verify:post`, `roadmap milestone-scope`.
- Git history: `825095f`/`775ee6f`, `2aadcea`/`b8926e7`, `6709953`/`05668ef`.

### Secondary (MEDIUM confidence)
- STATE.md and the commit-timeout debt file for the 30 s / ~64 s figures (not re-measured).

### Tertiary (LOW confidence)
- none. No web or Context7 lookup was needed: every claim is about this repo, the installed packages, or the installed gsd tooling, and was checked against them directly. The research-plan seam was therefore not used.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH, nothing new; versions read from `.venv`.
- Architecture (the narrowing): HIGH, prototyped and run green with a negative control.
- Nyquist mechanics: HIGH for resolution and flow (run live, workflow read in full); LOW-MEDIUM for the resulting `nyquist_compliant` value (A1).
- Pitfalls: HIGH, each reproduced or read this session except the three items in the Assumptions Log.

**Research date:** 2026-10-04
**Valid until:** 2026-11-03 (a cadquery or mypy bump would change the verified outputs; the fixture tripwire would notice a cadquery change first)
