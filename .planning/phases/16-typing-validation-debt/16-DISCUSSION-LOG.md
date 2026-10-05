# Phase 16: Typing & Validation Debt - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-10-04
**Phase:** 16-typing-validation-debt
**Areas discussed:** Narrowing mechanism, Gap disposition (7/8), The record, Proof & commit shape

Facts put in front of the human before the areas were chosen: gsd's `init.phase-op`
resolves Phases 7 and 8 to their archived directories (the REQ's ASSUMPTION settled);
cadquery 2.8.0's `Shape.cut() -> Shape` means a `.val()` cast reaches two of the five
ignores; the v0.2 audit's `nyquist` block vs REQ's "discovery only"; PR #18 merged as
`085e5a6`; one `must` debt row stays with no Phase 16 REQ.

---

## Narrowing mechanism

| Option | Description | Selected |
|--------|-------------|----------|
| isinstance + BuildError | Runtime check; a non-body shape raises BuildError like `_build`'s "exactly one valid solid" does today. Honest: a wrong claim fails loud. Cost nanoseconds per build step. Widens SC2's "annotations only" to "no geometry change". | ✓ |
| typing.cast | Zero runtime; literally annotations only. A type-checker claim nothing verifies — the one tool that can make mypy green while wrong. Nothing to test. | |
| TypeIs guard function | Same runtime check behind a typed predicate. More ceremony for the same effect at five sites. | |

**User's choice:** isinstance + BuildError

| Option | Description | Selected |
|--------|-------------|----------|
| Two helpers | `_body(shape) -> Solid \| Compound` at the three fillet/chamfer sites; `_shape_of(workplane) -> cq.Shape` at the two `.val()` sites. One narrowing per concept; five call sites; the measured-types comment once per helper. | ✓ |
| Operation wrappers | `_fillet`/`_chamfer` returning `cq.Shape` plus `_shape_of()`. Hides Mixin3D fully; three helpers for the same narrowing. | |
| Inline at each site | `isinstance` + raise before each of the three calls plus one `_shape_of()`. Repeats the check and its comment — "ignoring at each call site" by another name. | |

**User's choice:** Two helpers

| Option | Description | Selected |
|--------|-------------|----------|
| Name the invariant | "Geometry kernel returned a {Face} where a solid body was expected — a modelling defect, not a parameter problem." Nothing tells the user to change a field they did not break. | ✓ |
| Reuse the existing sentence | "Geometry kernel produced an invalid solid for these parameters." Blames the input for a defect it did not cause. | |
| Not BuildError — raise TypeError | Marks a programming error, but `_build_checked` wraps it as "Geometry kernel failed (TypeError); try smaller fillets or chamfers" — a wrong remedy. | |

**User's choice:** Name the invariant

| Option | Description | Selected |
|--------|-------------|----------|
| Correct comment, drop cadquery.* | The entry is a no-op for a typed package (cadquery ships `py.typed`); keep `OCP.*` and say why. Gated on identical `make typecheck` output; any change stops and asks. Same commit as the narrowing. | ✓ |
| Correct the comment only | Leave both entries; fix the false sentence. A config line documented as doing nothing. | |
| Leave it | Out of the REQ text; file as nice debt or idea. | |

**User's choice:** Correct comment, drop cadquery.*
**Notes:** Checked this session: cadquery 2.8.0 has `py.typed`; `OCP` has 0 `.pyi` and no `py.typed`.

---

## Gap disposition (7/8)

| Option | Description | Selected |
|--------|-------------|----------|
| Manual-only + debt file | REQ as written: every gap one `docs/tech_debt` row with a trigger; no new test. SC4 corrected to "a VALIDATION.md at status: validated exists; a gap is a debt row"; the audit may honestly read PARTIAL. | ✓ |
| Fix all gaps via the auditor | SC4 literal (`nyquist_compliant: true`) but the scope expansion REQ forbids; tests land with no human-set acceptance for 2026-09 behaviour; `tests/` pinned at 927 by Phase 15. | |
| Decide per gap at the gate | Gap table as a checkpoint:decision. Honest but a scoping session mid-phase; the planner cannot write the outcome. | |

**User's choice:** Manual-only + debt file

| Option | Description | Selected |
|--------|-------------|----------|
| nice, trigger = file next touched | The behaviour is verified (VERIFICATION 4/4, 30/30); a Nyquist gap is a missing per-task mapping. Exception: a behaviour with NO test at all is `must`, decided at a checkpoint. | ✓ |
| must, always | CLAUDE.md's letter; files `must` rows in the last phase of a milestone whose SM1 is zero `must` rows. | |
| You rule per row at a checkpoint | Executor halts with the gap table; slower; plan cannot pre-state the outcome. | |

**User's choice:** nice, trigger = file next touched

| Option | Description | Selected |
|--------|-------------|----------|
| You, at a checkpoint:human-action | Fresh sessions, answer the gate per the rule, plain `git commit` when the helper times out; executor verifies the files and records the gap count. Phase 15's own note: "run it as its own change". | ✓ |
| Executor via the Skill tool | The skill's AskUserQuestion fires inside a subagent, the auditor spawn nests, the commit timeout lands on the executor. Untested path. | |
| You, before planning | Shortest, but the phase's record then documents work done outside its plans. | |

**User's choice:** You, at a checkpoint:human-action

| Option | Description | Selected |
|--------|-------------|----------|
| One file per phase | `…-phase-07-nyquist-gaps.md` listing each gap row with task id, what proves it today, the trigger; same for 08; zero gaps = no file. | ✓ |
| One file per gap | Literal "one item per file"; many near-identical nice rows for one cause. | |

**User's choice:** One file per phase

---

## The record

| Option | Description | Selected |
|--------|-------------|----------|
| Dated amendment in place | `missing_phases` → `[]`, 07/08 placed as measured, `overall` recomputed, an `amended: <date> by Phase 16` note and two table rows under a dated subheading; original rows stay. | ✓ |
| Leave it as history | True at close; VALIDATION.md files and the SUMMARY carry the fact; SC4's "no longer partial" never true anywhere. | |
| Re-run the milestone audit | Audits v0.3, not v0.2 — wrong tool. | |

**User's choice:** Dated amendment in place

| Option | Description | Selected |
|--------|-------------|----------|
| All four, in the PR | 14 D-07 / 15 D-01 precedent; ROADMAP via gsd tooling, REQUIREMENTS by scoped Edit. The record states the mechanism actually used. | ✓ |
| Only the two the work touches | Fix the "cast once" theory; leave the ASSUMPTION and SC4 path. Two sentences stay false. | |
| Leave all; L35 carries the corrections | Append-only purist; the text a reader opens first stays false. | |

**User's choice:** All four, in the PR
**Notes:** The four: REQ/SC1 "cast once at the .val() boundary" + line refs 212/236/238/410/419 → 213/237/239/411/420; REQ-nyquist "ASSUMPTION (unverified)"; SC4's path `milestones/v0.2-phases/07-*/VALIDATION.md` → `.planning/milestones/v0.2-phases/07-*/07-VALIDATION.md`; PROJECT.md's target text and L21 Outcome column at transition.

| Option | Description | Selected |
|--------|-------------|----------|
| L35, short, amends L21 | One paragraph: the two helpers, isinstance over cast and why, the measured runtime types, `Shape.cut -> Shape`, the override dropped, the 7/8 Nyquist outcome with gap count. Keeps one-entry-per-phase. | ✓ |
| No Lxx; the debt file's resolution carries it | Smaller; breaks the per-phase pattern; L21's lineage has no pointer to where vendor types now stop. | |

**User's choice:** L35, short, amends L21

---

## Proof & commit shape

| Option | Description | Selected |
|--------|-------------|----------|
| Helper refusal tests + fixture diff | Two unit tests, no kernel build: `_body()` on a `cq.Face`; `_shape_of()` on a Workplane whose `.val()` is a Vector/Location. Plus the 48 kernel tests and `git diff --exit-code 085e5a6 -- tests/regression/pre_v0_2.json`. | ✓ |
| Existing suite only | mypy + RUF100 + 927 tests + fixture diff. The new BuildError path at zero coverage. | |
| Refusal tests + a kernel row | Plus one kernel test pinning the measured runtime types. One more ~0.5 s build; pins cadquery behaviour the fixture pins indirectly. | |

**User's choice:** Helper refusal tests + fixture diff

| Option | Description | Selected |
|--------|-------------|----------|
| Pin in `make no-fake-done`, scoped to src/spur | One more `git grep` line: `type: ignore` under `src/spur/` is an unfinished-work marker. Tests/bench/scripts stay free. | ✓ |
| No pin | True at the sha; review catches a new suppression; the fifth ignore arrived unnoticed in 10-02. | |
| Repo-wide marker | Strongest; blocks a deliberate wrong library call in a test; not free today (two test sites). | |

**User's choice:** Pin in `make no-fake-done`, scoped to src/spur
**Notes:** Inventory: `tests/test_calc.py:1472`, `tests/test_cli.py:423`, `tests/test_records.py:115` (docstring), `.planning/phases/13-latency-bar/investigation/run_experiment.py:167`.

| Option | Description | Selected |
|--------|-------------|----------|
| Code + its record, planning separate | One commit: helpers, annotations, two tests, the no-fake-done pin, the override edit, implementation.md rewritten, debt retired + INDEX. REQ/ROADMAP SC1 corrections in the plan's `.planning` commit. VALIDATION.md are the human's commits; L35 + audit amendment + gap files close the phase. | ✓ |
| Code and tests only, record after | Cleaner diff; breaks "retired in the fixing commit". | |
| Everything in one | Mixes a product change with planning-record edits, which 14/15 kept apart. | |

**User's choice:** Code + its record, planning separate

---

## Claude's Discretion

- Plan order (suggested: narrowing → the human-action checkpoint for 7/8 → L35 and
  transition edits; the Nyquist plan is independent of the typing plan).
- Helper names, comment text, the BuildError wording within D-03's content, the
  no-fake-done refusal sentence, the L35 title.
- `_gear_blank -> cq.Solid` or stay `cq.Shape`; where the two refusal tests live.
- The human-action checkpoint's exact text and what the executor's post-check reads.
- Whether gap debt files and the audit amendment share a commit.

## Deferred Ideas

- v0.3 SM1 vs the active `must` row (same-slot race) — milestone-audit question.
- A kernel-level runtime-type test — not taken; L35 carries the measurement.
- A repo-wide `type: ignore` marker — not taken.
- Re-typing the pipeline as `cq.Compound` — rejected.
- Tests for Phase 7/8 gaps — debt rows by REQ.
- `/gsd-map-codebase` refresh; the gsd commit-timeout debt; open 13/14/15 review items.
