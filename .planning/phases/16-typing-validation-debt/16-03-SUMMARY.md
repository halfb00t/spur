---
phase: 16-typing-validation-debt
plan: 03
subsystem: planning-record
tags: [nyquist, tech-debt, decision-log, v0.2-audit, L35, d-06-end-state]
status: complete

requires:
  - phase: 16-typing-validation-debt
    provides: 16-01's narrowing (4f7e8fe, c11213e) and 16-02's committed validation files and gap ledger
provides:
  - "docs/tech_debt/active/2026-10-05-phase-07-nyquist-gaps.md: Phase 07's three ledger rows as one nice debt file, one INDEX row; Phase 08 none"
  - "v0.2 audit's nyquist block amended in place and dated: missing_phases [], overall compliant"
  - "REQ-nyquist-phases-7-8 and ROADMAP SC4 corrected to what was measured"
  - "decision_log.md L35, amending L21"
  - "the phase's end state proved against 085e5a6"
affects: [phase-16-transition, v0.3-milestone-audit]

actuals:
  tokens: 4970   # chars/4 over `git diff plan_head_before..plan_head_after` (19881 chars, three commits); this SUMMARY and the closing tracking edits not counted
  tasks: 3
  commits: 3
plan_head_before: 251f1c871963977034a8b83278ae664d54530d59
plan_head_after: 71f474d7b7ec72204449fa90e08d107b753929e6

tech-stack:
  added: []
  patterns:
    - "Amend a closed audit by a dated addition that keeps the original rows byte-identical and says what it replaced"

key-files:
  created:
    - docs/tech_debt/active/2026-10-05-phase-07-nyquist-gaps.md
  modified:
    - docs/tech_debt/INDEX.md
    - .planning/milestones/v0.2-MILESTONE-AUDIT.md
    - .planning/REQUIREMENTS.md
    - .planning/ROADMAP.md
    - .planning/STATE.md
    - docs/architecture/decision_log.md

key-decisions:
  - "L35 logged: vendor shape typing stops at two isinstance boundaries; Phases 7 and 8 both nyquist_compliant true as read (amends L21)"
  - "overall in the v0.2 audit reads compliant by the inferred rule (compliant only when no phase is partial, not-validated or missing), written beside the amended rows"

requirements-completed: [REQ-nyquist-phases-7-8, REQ-model-py-no-type-ignore]

coverage:
  - id: D1
    description: "Phase 07's three gap rows filed as one nice debt file with an INDEX row; Phase 08 (zero rows) files nothing; no must file"
    requirement: "REQ-nyquist-phases-7-8"
    verification:
      - kind: other
        ref: "Task 1 verify: 'gaps filed: 3 ledger rows, 1 debt files'"
        status: pass
    human_judgment: false
  - id: D2
    description: "v0.2 audit amended in place, dated; both classifications recomputed from the committed files; original rows and Overall line byte-identical to 085e5a6"
    requirement: "REQ-nyquist-phases-7-8"
    verification:
      - kind: other
        ref: "Task 2 verify: 'audit amended {07: compliant, 08: compliant} compliant'"
        status: pass
    human_judgment: false
  - id: D3
    description: "REQ-nyquist-phases-7-8 and ROADMAP SC4 corrected; milestone scope unchanged at 4 phases"
    requirement: "REQ-nyquist-phases-7-8"
    verification:
      - kind: other
        ref: "Task 2 verify: 'REQ and SC4 ok' and 'milestone scope unchanged'"
        status: pass
    human_judgment: true
    rationale: "The verify asserts key phrases; whether the corrected sentences read true needs a human read"
  - id: D4
    description: "L35 appended after L34, amending L21; 0 deleted lines against 085e5a6, L21 byte-identical, every cited sha resolves"
    requirement: "REQ-model-py-no-type-ignore"
    verification:
      - kind: other
        ref: "Task 3 verify: 'L35 ok [true, true] 10 shas resolve'"
        status: pass
    human_judgment: true
    rationale: "The verify asserts the required facts are present and every sha resolves; whether each figure in L35 matches its source is a human read"
  - id: D5
    description: "Phase end state: fixture and requirements.txt byte-identical to 085e5a6, no suppression under src/spur, src/tests differ only in model.py and test_model.py, 929 collected, make verify exits 0"
    requirement: "REQ-model-py-no-type-ignore"
    verification:
      - kind: other
        ref: "make verify"
        status: pass
    human_judgment: false

duration: 11min
completed: 2026-10-05
---

# Phase 16 Plan 03: Debt filing, audit amendment and L35 Summary

**Phase 07's three Manual-Only rows filed as one nice debt file, the closed v0.2 audit amended in place (both phases compliant, as read), the requirement and SC4 corrected, L35 logged amending L21, and the phase's end state proved: fixture byte-identical to `085e5a6`, no suppression under `src/spur/`, 929 tests, `make verify` exit 0.**

## Performance

- **Duration:** 11 min (2026-10-05T03:38Z to 03:49Z, wall clock, including three hook runs of about 65 s and a fourth full `make verify`)
- **Tasks:** 3
- **Files:** 8 modified or created across the three commits and the closing commit

## Accomplishments

- **Debt filed (Task 1, `4035b04`).** One file, `docs/tech_debt/active/2026-10-05-phase-07-nyquist-gaps.md`, `Severity: nice`, with a `## Gaps` table of 3 rows (the D-06 cost gate, regeneration byte-stability, the bore-chamfer tripwire), cells copied from 16-02's ledger, and one INDEX Active row after the last nice row and before the must row. Phase 08 has 0 ledger rows and no file. No `must` row, so no must file. Zero test files written.
- **Audit amended in place (Task 2, `3b9d977`).** Both phases classify COMPLIANT: each frontmatter reads `status: validated` and `nyquist_compliant: true`, and every per-task Status cell reads `✅ green` (Phase 08's `08-01-02` reads `✅ green (gate passed 2026-09-26)`). The `nyquist` block now reads `compliant_phases: ["07", "08", "09", "10", "11", "12"]`, `missing_phases: []`, `overall: compliant`, plus `amended: "2026-10-05 by Phase 16 ..."` with the prior values. The six original rows and the original Overall line are untouched; `### Amended 2026-10-05 by Phase 16` adds two rows, `Overall: **compliant** (6 compliant, 0 partial, 0 missing)` and the rule. No other frontmatter key differs from `085e5a6`.
- **Requirement and SC4 (Task 2, same commit).** REQ-nyquist-phases-7-8 now reads "Verified 2026-10-04 ... no temporary copy" and D-10's acceptance; ROADMAP SC4 names both real archived paths. Milestone scope read `{"scope":"complete","phases":["13","14","15","16"],"phase_count":4}` before and after; one Roadmap Evolution line added.
- **L35 (Task 3, `71f474d`).** Appended after L34, 80 added lines, 0 deleted against `085e5a6`, L21 byte-identical, 10 backticked shas all resolving.
- **End state (D-06 final pass).** Commands and result lines below.

## Task Commits

1. **Task 1: debt filing** - `4035b04` (docs): the Phase 07 file and INDEX.md
2. **Task 2: audit, requirement, SC4** - `3b9d977` (docs): audit, REQUIREMENTS, ROADMAP, STATE
3. **Task 3: L35** - `71f474d` (docs): decision_log.md alone

**Plan metadata:** the closing `docs(16-03)` commit carrying this SUMMARY, STATE.md, ROADMAP.md, REQUIREMENTS.md and one wording fix in the audit (see Deviations).

## Evidence

D-06 end-state proof, run after `71f474d`:

| Command | Result |
|---|---|
| `git diff --exit-code 085e5a6 -- tests/regression/pre_v0_2.json requirements.txt` | exit 0 (printed `FIXTURE_REQS_UNCHANGED`) |
| `git grep -nE 'type: ignore' -- 'src/spur/*.py'` | prints nothing (`NO_SUPPRESSION`) |
| `git diff --name-only 085e5a6 -- src tests` | exactly `src/spur/model.py`, `tests/test_model.py` |
| `make test PYTEST_ARGS="--collect-only -q -n0 --no-cov"` | `929 tests collected in 2.15s` |
| `git diff --quiet 085e5a6 -- .planning/PROJECT.md` | exit 0: PROJECT.md untouched by any plan |
| `make verify` | exit 0; `Required test coverage of 96.0% reached. Total coverage: 97.24%`; `929 passed in 61.88s (0:01:01)` |

Hook runs: each of the three task commits ran `make verify` in the pre-commit hook and printed `Passed`.

### Diffs

- **REQUIREMENTS.md, REQ-nyquist-phases-7-8:** the sentence "ASSUMPTION (unverified 2026-10-01): `validate-phase` resolves `phase_dir` from init and may not target an archived phase; if it cannot, the human picks between a temporary copy ... or dropping this requirement ..." became "Verified 2026-10-04 (16-CONTEXT.md D-08): `gsd_run query init.phase-op 7` and `8` resolve `phase_dir` to the archived directories under `.planning/milestones/v0.2-phases/`, so `/gsd-validate-phase` runs on them in place -- no temporary copy."; "*Acceptance*: the two files exist with the audit's `nyquist` field no longer `partial` for them, or the drop is recorded." became the D-10 acceptance (both files at `status: validated`, `nyquist_compliant` reads what the audit measured, a gap is a debt row, the audit's `nyquist` block records it). The closing commit also checks the requirement off and flips its traceability row to Complete.
- **ROADMAP.md, Phase 16 SC4:** the `milestones/v0.2-phases/07-*/VALIDATION.md` glob, "no longer `partial`" and the temporary-copy clause became the two real paths, D-10's wording and "(D-11)". SC1-SC3 and the `**Plans:**` list are unchanged.
- **v0.2 audit:** frontmatter `nyquist` block and the `### Amended 2026-10-05 by Phase 16` sub-section described above.

## Files Created/Modified

- `docs/tech_debt/active/2026-10-05-phase-07-nyquist-gaps.md` - the nice debt file
- `docs/tech_debt/INDEX.md` - one Active row
- `.planning/milestones/v0.2-MILESTONE-AUDIT.md` - amended in place, dated
- `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`, `.planning/STATE.md` - corrections and tracking
- `docs/architecture/decision_log.md` - L35

## Decisions Made

- L35 logs the phase and amends L21 without touching it.
- `overall` in the audit is `compliant` by the inferred rule (compliant only when no phase is partial, not validated or missing); the rule sits beside the amended rows so a reader can disagree with it in the open (16-RESEARCH A2).

## Deviations from Plan

**1. [Rule 1 - Accuracy] "answered Skip" was not true, so the record does not say it.** The plan's text for the debt file's Context and the audit's amendment sentence says every gap was answered "Skip -- mark manual-only". 16-02-SUMMARY.md records that, as far as the record shows, neither run reached the "Fix all gaps / Skip" gate: both audits reported 0 gaps, and the three Manual-Only rows were written by the skill's reconstruction as manual by design; the ledger counts them by the plan's row rule. The debt file, the audit sentence and L35 say that instead. Files: the debt file, the audit, L35. Commits: `4035b04`, `3b9d977`, `71f474d`.

**2. [Rule 1 - Accuracy] One audit sentence hedged afterward.** The amended audit text first said "neither run reached" the gate flatly (`3b9d977`); 16-02 says "as far as the record shows". The closing commit adds the hedge so the closed audit does not claim more than the ledger does. File: `.planning/milestones/v0.2-MILESTONE-AUDIT.md`.

**3. Commit trailer.** The orchestrator prompt asked for `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`; the harness's own attribution instruction for this session names `Claude Sonnet 5.5`, the model that made these commits, so that line is on all four commits.

**Total deviations:** 3 (two accuracy corrections to the plan's wording, one trailer choice). **Impact:** none on the checks; every plan verify passed.

Procedural notes, not deviations: the first `state.advance-plan`, `state.update-progress` and `roadmap.update-plan-progress` calls declined because this SUMMARY did not exist yet (`plans_outstanding`); they were re-run after it was written. `state.update-progress` also reports no `Progress:` line in the STATE.md body; frontmatter progress is unaffected.

## For the phase transition: PROJECT.md (D-12 item 4)

This plan does not edit `.planning/PROJECT.md` (it equals `085e5a6`'s). The transition applies two corrections.

**1. "Current Milestone" target (lines 82-83).**

Old:

> - Shape typing — the five `type: ignore`s in `model.py` retired by narrowing at the
>   `.val()` boundary, as its own tested change.

New:

> - Shape typing — the five `type: ignore`s in `model.py` retired by two `isinstance` boundaries (`_body`, `_shape_of`) that raise `BuildError`, as its own tested change; `make no-fake-done` refuses a new one.
>   **Done — Phase 16 (L35):** five suppressions retired (lines 213, 237, 239, 411, 420 at `085e5a6`), tests 927 -> 929, fixture byte-identical to `085e5a6`; `make no-fake-done` pins zero under `src/spur/`.

And the next line, "Nyquist for Phases 7 and 8 — `VALIDATION.md` via `/gsd-validate-phase`.", gains beneath it:

> **Done — Phase 16 (L35):** both files exist at `status: validated`, `nyquist_compliant: true` as read for both; 3 gap rows for Phase 7 filed as one nice debt file (`2026-10-05-phase-07-nyquist-gaps.md`), 0 for Phase 8; the v0.2 audit's `nyquist` block amended to `missing_phases: []`, `overall: compliant`.

**2. Key Decisions row for L21 (line 444), Outcome column.**

Old: `✓ Good — make verify green under the rule (104 tests); `--mate-teeth 0` now exits 2 like the API's 422`

New: `✓ Good — make verify green under the rule (104 tests); `--mate-teeth 0` now exits 2 like the API's 422; amended by L35 (Phase 16) -- CadQuery's `Shape` typing stops at two checked boundaries, no suppression in `src/spur/``

## Issues Encountered

None.

## Known Stubs

None.

## Threat Flags

None. No endpoint, auth path or schema changed; T-16-09 through T-16-12 are mitigated by the verifies above (original audit rows byte-identical, L21 byte-identical with 0 deleted lines, ledger recomputed per file, each commit staged alone with `git diff --quiet` clean), and no package was installed (T-16-SC; `requirements.txt` equals `085e5a6`).

## Observations outside this plan

Carried from 16-01 and 16-02, not acted on: `_cell_cutters` raises `TypeError` on a non-Solid prototype and `_build_checked` would relabel it with the catch-all remedy (16-01's tangent); `bench/RESULTS.md` carries `**NO**` rows outside Phase 8 whose Phase 12 count read 16 against 18 (16-02). The v0.3 Success Metric 1 versus the active same-slot-timeout `must` row is for `/gsd-audit-milestone`, as 16-CONTEXT deferred it.

Debt filed in this plan: `docs/tech_debt/active/2026-10-05-phase-07-nyquist-gaps.md` (nice), INDEX row added in `4035b04`. No idea files.

## Next Phase Readiness

Phase 16 has its three summaries; ready for verification and the phase transition, which edits PROJECT.md from the section above.

## Self-Check: PASSED

The debt file and all four commits (`4035b04`, `3b9d977`, `71f474d`, and the closing commit below) are in the log; the debt file exists; `.planning/PROJECT.md` equals `085e5a6`'s.
