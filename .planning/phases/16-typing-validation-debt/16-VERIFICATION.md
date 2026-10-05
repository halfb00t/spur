---
phase: 16-typing-validation-debt
verified: 2026-10-05T04:30:00Z
status: human_needed
score: 16/16 must-haves verified
covered_files:
  - .planning/phases/16-typing-validation-debt/16-01-PLAN.md
  - .planning/phases/16-typing-validation-debt/16-01-SUMMARY.md
  - .planning/phases/16-typing-validation-debt/16-02-PLAN.md
  - .planning/phases/16-typing-validation-debt/16-02-SUMMARY.md
  - .planning/phases/16-typing-validation-debt/16-03-PLAN.md
  - .planning/phases/16-typing-validation-debt/16-03-SUMMARY.md
  - Makefile
  - docs/architecture/decision_log.md
  - docs/architecture/solid-model/implementation.md
  - docs/tech_debt/INDEX.md
  - docs/tech_debt/active/2026-10-05-phase-07-nyquist-gaps.md
  - docs/tech_debt/resolved/2026-09-21-cadquery-shape-typing.md
  - pyproject.toml
  - src/spur/model.py
  - tests/test_model.py
covered_digest: "v2:sha256:4b2dc4dbbb6c9ca499d635b66ca1c632e3f3d1afb74b0b446d0a82a22bd2ac77"
behavior_unverified: 0
overrides_applied: 0
human_verification:
  - test: "Read L35 in docs/architecture/decision_log.md against its sources (judgment-tier prohibition from 16-03: 'MUST NOT put a number in L35 that was not measured')"
    expected: "Every figure (37 source files, 927 -> 929, 4446.54642 / 210 / 604, 0 gaps, 3 Manual-Only rows, the ten shas) matches 16-01-SUMMARY, 16-02-SUMMARY or 16-CONTEXT's dated domain facts"
    why_human: "unverified-prohibition, human review recommended. The verifier's LLM-judge verdict is NON-AUTHORITATIVE: it re-ran or re-read 929, the gear tuple, 37 source files, both nyquist_compliant values and resolved all ten shas, but 'no number was estimated' is a judgment, not a check."
  - test: "Decide whether to keep or add a standing gate for the 16-01 prohibition 'no typing.cast, no written Any, no mypy rule loosened'"
    expected: "Either accept that mypy strict + disallow_any_explicit (written Any) and the review of pyproject.toml (rules) are the standing enforcement, or file a debt item for a cast pin"
    why_human: "unverified-prohibition (test-tier, fails closed). The cast clause was proved only by a one-time AST check in plan 16-01 Task 1 and again by this verifier; no test or Makefile target keeps refusing a future typing.cast in src/spur/model.py. mypy strict forbids a written Any, but nothing forbids cast."
  - test: "Accept or reject the 16-02 record gap for Phase 7"
    expected: "16-02 truth 4 asked for the gap tables 'recorded verbatim from the human's resume message'. The resume message for Phase 7 was 'Unfortunately I didn't save the result.' The SUMMARY says so and reads the tables from the committed 07-VALIDATION.md instead; both audit runs report 0 gaps, so the 'Skip' gate (truth 2) was never reached."
    why_human: "A deviation from a must-have truth that the executor disclosed rather than hid. It does not change SC4 (files exist, validated, compliant as read, gaps filed) but is the human's call to accept."
---

# Phase 16: Typing & Validation Debt Verification Report

**Phase Goal:** `model.py` is clean under mypy `--strict` with zero `# type: ignore`, and Phases 7-8 (the two v0.2 phases that predate the Nyquist capability) get the validation pass they were built without.
**Verified:** 2026-10-05T04:30:00Z
**Status:** human_needed
**Re-verification:** No (initial verification)

Every must-have truth verified against the tree. No gaps, no blockers. Status is `human_needed` only because ADR-550 routes a judgment-tier prohibition and an unenforced test-tier prohibition to a human, and one executor-disclosed deviation needs the human's acceptance. None of the three item blocks the next phase on its own.

## Goal Achievement

### Observable Truths

| #  | Truth | Status | Evidence |
|----|-------|--------|----------|
| 1  | SC1: `src/spur/model.py` carries zero mypy suppressions; five retired at 213, 237, 239, 411, 420 | VERIFIED | `git grep -nE 'type: ignore' -- 'src/spur/*.py'` prints nothing (exit 1). Same grep at `085e5a6` prints exactly lines 213, 237, 239, 411, 420. |
| 2  | Narrowing is two `isinstance` helpers raising `BuildError`, never `cast` / `TypeIs` / `Any` | VERIFIED | `model.py:428` `_body(shape: cq.Shape) -> cq.Solid \| cq.Compound`, `:437` `_shape_of(wp: cq.Workplane) -> cq.Shape`. AST walk: `_body` called 3x, `_shape_of` 2x, no `cast`/`Any`/`TypeIs` name or attribute anywhere in the module. |
| 3  | `_gear_blank` keeps `-> cq.Shape` (D-02 by measurement) | VERIFIED | The function is among the 18 AST-identical to `085e5a6`; signature unchanged. |
| 4  | One `_NOT_A_BODY` message, names the invariant, never a field, no "try smaller fillets" remedy | VERIFIED | `model.py:414-416`; run live: `_body(Face)` and `_shape_of(Workplane("XY"))` both raise `BuildError("Geometry kernel returned a Face/Vector where a solid body was expected: a modelling defect in the build pipeline, not a parameter problem.")`. |
| 5  | Two refusal tests assert the full message with `==`; 927 -> 929 | VERIFIED | `tests/test_model.py:250` and `:264`; both use `==` on the whole string. `make verify`: `929 passed in 62.60s`. |
| 6  | Boundary: `_body` passes Solid and Compound, refuses Face; `_shape_of` refuses Vector | VERIFIED | Live probe: `_body(box.val())` -> Solid, `_body(Compound.makeCompound([...]))` -> Compound, Face and empty-Workplane refused. Behavior is exercised by the two passing tests plus the whole build suite (Solid/Compound pass through all five sites). |
| 7  | SC2: `make verify` green under `--strict` + `disallow_any_explicit`; mypy clean | VERIFIED | `make verify` exit 0 (ruff, mypy, import contracts, no-fake-done, pytest). Independent run with a fresh cache dir: `Success: no issues found in 37 source files`. |
| 8  | No geometry change: fixture byte-identical, five-site gear unchanged, 18 untouched functions AST-identical | VERIFIED | `git diff --quiet 085e5a6 HEAD -- tests/regression/pre_v0_2.json` exit 0; `build(GearParams(tip_chamfer=0.5))` -> `('Solid', True, 4446.54642, 210, 604)`; AST comparison of 18 named functions to `085e5a6`: identical. `git diff --name-only 085e5a6 HEAD -- src tests` = `src/spur/model.py`, `tests/test_model.py` only. |
| 9  | `make no-fake-done` refuses a suppression under `src/spur/` only; tests keep theirs | VERIFIED | `Makefile` second `git grep -nE 'type: ignore' -- 'src/spur/*.py'` block with the why-comment; `make verify` includes it and passed. RED against `085e5a6` is demonstrated by the five-line grep above. |
| 10 | D-04: `cadquery.*` left the override, `OCP.*` stays | VERIFIED | `pyproject.toml` override is `module = ["OCP.*"]`; diff shows no other mypy key moved. `cadquery/py.typed` exists in the venv; OCP has no `py.typed` or `.pyi`. Fresh-cache mypy is green. |
| 11 | `implementation.md` bullet rewritten to the two checked boundaries | VERIFIED | Lines 29-35 name `_body()`, `_shape_of()`, `isinstance`, `BuildError`, `Shape.cut -> Shape`, `no-fake-done` and the resolved-debt path; "load-bearing" bullet is gone. |
| 12 | SC3: debt retired with its sha and corrected line refs | VERIFIED | `docs/tech_debt/active/2026-09-21-cadquery-shape-typing.md` absent; resolved file has `Status: resolved`, `Resolved in: 4f7e8fe`, `src/spur/model.py:213, 237, 239, 411, 420`, a `## Resolution (2026-10-04)`; INDEX Resolved row names `4f7e8fe`. `4f7e8fe` is the `refactor(16-01)` commit and carries exactly the eight planned paths; `c11213e` carries the debt file and INDEX only. |
| 13 | REQ-model-py-no-type-ignore, SC1, SC2 say what was built (two helpers, why a cast reaches two of five, `warn_unused_ignores` vs `RUF100`, "no geometry change") | VERIFIED | Read in `.planning/REQUIREMENTS.md:152-166` and `.planning/ROADMAP.md` Phase 16 SC1/SC2. The `**Plans:**` list is intact (3/3). |
| 14 | SC4: `07-VALIDATION.md` and `08-VALIDATION.md` exist, tracked, `status: validated`, `nyquist_compliant` as read | VERIFIED | Both tracked, clean against HEAD. 07: `status: validated`, `nyquist_compliant: true`, last commit `5ba02d2` (file alone). 08: same values, last commit `8ae468e` (file alone). Per-task Status cells all green (6 for 07, 10 for 08). No `test(phase-0[78])` commit exists in `085e5a6..HEAD`. |
| 15 | SC4: a gap is a debt row; the v0.2 audit's `nyquist` block records the measurement | VERIFIED | 07 has 3 Manual-Only data rows, 08 has none (matches the 16-02 ledger). `docs/tech_debt/active/2026-10-05-phase-07-nyquist-gaps.md` has a 3-row `## Gaps` table, `Severity: nice`, `Revisit when:`, one INDEX Active row (line 25); no Phase 8 file. Audit frontmatter: `missing_phases: []`, 07 and 08 in `compliant_phases`, `overall: compliant`, `amended:` names Phase 16 and the prior values. Original six rows and original Overall line byte-identical; dated `### Amended 2026-10-05 by Phase 16` section added. |
| 16 | L35 appended, amends L21 without touching it | VERIFIED | `decision_log.md:1761` is the only `## L35`; `git diff --numstat 085e5a6 HEAD` = 80 added, 0 deleted; L21 section byte-identical; all ten backticked shas resolve to commits; both `nyquist_compliant: true` phrases match the files. `.planning/PROJECT.md` untouched (the transition note is in 16-03-SUMMARY, as planned). |

**Score:** 16/16 truths verified (0 present, behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/spur/model.py` | `_NOT_A_BODY`, `_body`, `_shape_of`, five narrowed sites | VERIFIED | Lines 211, 235, 237, 408, 445 call the helpers; helpers at 428 and 437. |
| `tests/test_model.py` | two refusal tests | VERIFIED | Lines 250 and 264. |
| `Makefile` | second `no-fake-done` block | VERIFIED | Present and wired into `verify`. |
| `pyproject.toml` | override scoped to `OCP.*` | VERIFIED | Present. |
| `docs/tech_debt/resolved/2026-09-21-cadquery-shape-typing.md` | retired debt with sha | VERIFIED | `Resolved in: 4f7e8fe`. |
| `docs/tech_debt/active/2026-10-05-phase-07-nyquist-gaps.md` | Phase 7 nice debt | VERIFIED | 3 rows, INDEX row. |
| `07-VALIDATION.md`, `08-VALIDATION.md` | validated, tracked | VERIFIED | See truth 14. |
| `docs/architecture/decision_log.md` `## L35` | amends L21 | VERIFIED | See truth 16. |
| `.planning/milestones/v0.2-MILESTONE-AUDIT.md` | amended nyquist block | VERIFIED | See truth 15. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `_cut_face_recesses` / `_cut_bore` / `_chamfer_tips` | `_body` | `solid = _body(solid).fillet/chamfer(...)` | WIRED | `model.py:211, 237, 408`. |
| `_cut_bore` / `_ring` | `_shape_of` | `solid.cut(_shape_of(hole))`; `return _shape_of(...)` | WIRED | `model.py:235, 445`. |
| `_body` / `_shape_of` `BuildError` | 422 / exit 1 | existing `except BuildError` path | WIRED | `BuildError` is the type `_build_checked` already re-raises without the catch-all remedy; the unchanged function is AST-identical to `085e5a6`. |
| `Makefile no-fake-done` | `make verify` | `verify: lint typecheck lint-imports no-fake-done test` | WIRED | Target still in the prerequisite list; `make verify` passed. |
| 07/08-VALIDATION.md frontmatter | audit `nyquist` block and L35 | `nyquist_compliant` as read | WIRED | Values identical in all three places. |
| 16-02 ledger | debt file and INDEX | one row per Manual-Only row | WIRED | 3 ledger rows = 3 debt rows; 0 = no file. |

### Data-Flow Trace (Level 4)

Not applicable: no artifact in this phase renders dynamic data. The only data-bearing path is the build pipeline, and the five-site gear tuple above shows it still produces the same solid (Solid, valid, 4446.54642 mm3, 210 faces, 604 edges).

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Gate green | `make verify` | exit 0; `929 passed in 62.60s`; coverage 97.24 % against the 96 floor | PASS |
| mypy strict, cold cache | `.venv/bin/python -m mypy --cache-dir <scratch> src tests docker bench scripts` | `Success: no issues found in 37 source files` | PASS |
| No suppression under `src/spur` | `git grep -nE 'type: ignore' -- 'src/spur/*.py'` | no output | PASS |
| Pin was red at baseline | `git grep -nE 'type: ignore' 085e5a6 -- 'src/spur/*.py'` | lines 213, 237, 239, 411, 420 | PASS |
| Five-site gear unchanged | `build(GearParams(tip_chamfer=0.5))` | `('Solid', True, 4446.54642, 210, 604)` | PASS |
| `_body` boundary | Solid, Compound pass; Face refused; `_shape_of(Workplane("XY"))` refused with full message | as stated | PASS |
| Fixture byte-identical | `git diff --quiet 085e5a6 HEAD -- tests/regression/pre_v0_2.json` | exit 0 | PASS |
| Only the narrowing touched `src`/`tests` | `git diff --name-only 085e5a6 HEAD -- src tests` | `src/spur/model.py`, `tests/test_model.py` | PASS |
| 18 untouched functions identical | AST dump vs `git show 085e5a6:src/spur/model.py` | identical | PASS |

### Probe Execution

Step 7c: SKIPPED. No PLAN or SUMMARY in this phase declares a `probe-*.sh`.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| REQ-model-py-no-type-ignore | 16-01 (also 16-03) | `model.py` zero `type: ignore`, no cast, no geometry change, debt retired | SATISFIED | Truths 1-13, 16. Checked `[x]` and `Complete` at REQUIREMENTS.md lines 152 and 232. |
| REQ-nyquist-phases-7-8 | 16-02 (also 16-03) | Phases 7 and 8 have a `VALIDATION.md` produced by `/gsd-validate-phase`; discovery only | SATISFIED | Truths 14-16. Checked `[x]` and `Complete` at lines 167 and 233. |

Both IDs in the phase's PLAN frontmatter (16-01: REQ-model-py-no-type-ignore; 16-02: REQ-nyquist-phases-7-8; 16-03: both) appear in REQUIREMENTS.md. No orphaned requirement: REQUIREMENTS.md maps exactly these two to Phase 16.

### Anti-Patterns Found

None. No TODO/FIXME/XXX/HACK in the edited files (the one Makefile hit is the pattern text of the gate itself). No stub, no hardcoded empty return added. `model.py:355`'s pre-existing "narrowed with isinstance for mypy only" comment is in `_cell_cutters`, which is unchanged since the baseline.

### Prohibitions (ADR-550)

| Prohibition | Tier | Verdict |
|-------------|------|---------|
| 16-01: MUST NOT change the part (fields, selectors, cuts, fixture byte-identical) | test | Enforced: fixture replay runs in `make verify`; fixture, 18 functions and the gear tuple checked by this verifier. |
| 16-01: MUST NOT blame the user's parameters; message names the invariant | test | Enforced: two `==` tests on the full message. |
| 16-01: MUST NOT make mypy green with `cast`, written `Any`, a loosened rule, or a local stub | test | Partly enforced: mypy strict + `disallow_any_explicit` forbids a written `Any`; the cast clause has no standing gate. Verified clean today by AST walk. FLAGGED, see human item 2. |
| 16-02: MUST NOT record a `nyquist_compliant` value or gap count nobody read | test | Enforced and checked: values read from committed frontmatter match the audit, L35 and the debt file; gap counts match the files' Manual-Only rows. |
| 16-02: MUST NOT turn discovery into scope (no test for 2026-09 behavior) | test | Enforced: no `test(phase-0[78])` commit; `src`/`tests` diff is the narrowing alone. |
| 16-03: MUST NOT rewrite the closed audit's history | test | Enforced: original six rows and Overall line byte-identical; non-`nyquist` frontmatter keys unchanged. |
| 16-03: MUST NOT put an unmeasured number in L35 | judgment | LLM-judge verdict (non-authoritative): every figure traced to a source and every sha resolves. `unverified-prohibition: human review recommended`, see human item 1. |

### Human Verification Required

1. **L35 figures** (judgment-tier prohibition). Read `docs/architecture/decision_log.md` L35 against 16-01-SUMMARY, 16-02-SUMMARY and 16-CONTEXT. Expected: each number matches its cited source. Why human: the verifier's check is a non-authoritative judge; "not estimated" is a judgment.
2. **Cast pin** (test-tier, fails closed). Decide whether mypy strict plus review is enough for "no `typing.cast` in `model.py`", or file a debt item. Why human: only a one-time AST check enforced it.
3. **Phase 7's unsaved gap table.** The human's resume message said "Unfortunately I didn't save the result." 16-02 records this and reads the table from committed `07-VALIDATION.md`. The "Skip - mark manual-only" gate was never reached because both audit runs report 0 gaps. Accept or reject that deviation from 16-02 truths 2 and 4.

### Gaps Summary

No gaps. Phase goal achieved: `model.py` has no suppression and is clean under strict mypy; Phases 7 and 8 each have a committed, validated `VALIDATION.md` with `nyquist_compliant: true` as read, Phase 7's three Manual-Only rows are filed as one nice debt file, and the v0.2 audit and L35 record the outcome.

Observations, none blocking:

- `.planning/phases/16-typing-validation-debt/16-REVIEW.md` is staged (`A`) but uncommitted in the index, and `.planning/milestone.lock` is untracked; neither belongs to this verification.
- 16-01's tangent stands: `_cell_cutters` raises a bare `TypeError` on a non-Solid prototype and `_build_checked` would relabel it with the catch-all remedy. Not filed as debt. Under CLAUDE.md the human should decide whether it gets a file under `docs/tech_debt/active/`.
- 16-02 noted `bench/RESULTS.md` `**NO**` row counts under Phase 12 (stated 16, read 18) that it did not resolve. Outside this phase.
- The audit's `overall: compliant` rests on a rule the plan inferred (audit-milestone section 5.5 does not define `overall`); the rule is written beside the amended rows.

---

_Verified: 2026-10-05T04:30:00Z_
_Verifier: Claude (gsd-verifier)_
