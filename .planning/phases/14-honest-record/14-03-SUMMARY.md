---
phase: 14-honest-record
plan: 03
subsystem: decision-log
tags: [decision-log, L33, root-lead-in, filleted-spoke, closed-form, tech-debt]

requires:
  - phase: 14-honest-record (14-01)
    provides: "the lead-in warning, its 15 rows, the README and _outline correction (13857e1, ac607d7, 825095f)"
  - phase: 14-honest-record (14-02)
    provides: "the filleted-spoke oracle, the abs=1e-9 bar, the tripwire (61e1bea, b00c44c)"
provides:
  - "decision log L33: the root lead-in warned, not re-cut, and the filleted-spoke cutout proved against a closed form, amending L09, L10 and L30 by appending"
  - "the phase's end-state gate recorded: make verify green, fixture and params.py byte-identical to 5d9e907, src/ scope calc.py + model.py (docstring only), both debts retired"
affects: [phase 14 verification, make pr.land]

actuals:
  tokens: 5600
  tasks: 2
  commits: 1
plan_head_before: 1b7888faa7973bebb1db12c462957956ed5a62d4
plan_head_after: 9fb667d5ae36dc5d53aef9b52949587facff38cf

tech-stack:
  added: []
  patterns:
    - "an amending entry appended under a fresh id, never an edit of the entry it corrects (L32's precedent)"

key-files:
  created: []
  modified:
    - docs/architecture/decision_log.md
    - .planning/phases/14-honest-record/14-02-SUMMARY.md

key-decisions:
  - "L33 states the composed-row exception exactly: 15 rows (12 tip-chamfer, 3 single-sided-recess) keep volume_rel=1e-6; the four cutout rows and the three skip-the-cutout tripwire rows run at abs=1e-9; the bar is not claimed for every caller of the shared assertion"
  - "The '0 of 44 fixture records' figure was recomputed on the committed code for this entry (it was a planning-time claim with no committed test behind it) and is recorded here"

requirements-completed: [REQ-root-lead-in-warned, REQ-readme-root-zone-states-the-limit, REQ-filleted-spoke-closed-form]

coverage:
  - id: D1
    description: "L33 is the last, unique entry, follows L32, names L09, L10 and L30 in its header, cites feat(14-01), test(14-01), docs(14-01) and test(14-02) by sha, and every e-notation figure in it occurs in tests/test_model.py"
    requirement: "REQ-filleted-spoke-closed-form"
    verification:
      - kind: other
        ref: "Task 1 python check: 'L33 ok' with figures 1.36e-12, 2.39e-12, 2.522e-4, 2.73e-12, 2.9e-3, 8.59e-8, 8.87e-12 all in tests/test_model.py"
        status: pass
    human_judgment: false
  - id: D2
    description: "The decision log is append-only against 5d9e907: 97 lines added, 0 deleted, so L09, L10, L30 and every earlier entry are untouched"
    requirement: "REQ-root-lead-in-warned"
    verification:
      - kind: other
        ref: "git diff --numstat 5d9e907 -- docs/architecture/decision_log.md prints 97 0"
        status: pass
    human_judgment: false
  - id: D3
    description: "The phase ends with the gate green, the part unchanged and both debts retired"
    requirement: "REQ-readme-root-zone-states-the-limit"
    verification:
      - kind: other
        ref: "make verify: 927 passed; src scope ok; contracts unchanged; ledger ok"
        status: pass
    human_judgment: false

duration: 22 min
completed: 2026-10-03
status: complete
---

# Phase 14 Plan 03: L33, the Honest Record Summary

**Decision log L33 records both corrections this phase made (the root lead-in warned rather than re-cut, the filleted-spoke cutout proved against a closed form at `abs=1e-9`), amends L09, L10 and L30 by appending, and states the 15 composed rows that stay at `rel=1e-6` instead of implying the bar covers every caller.**

## Performance

- **Duration:** 22 min
- **Completed:** 2026-10-03T03:49Z
- **Tasks:** 2
- **Files modified:** 2 (decision_log.md; a one-phrase fix in 14-02-SUMMARY.md)

## Accomplishments

- `## L33 — The root lead-in is warned, not re-cut, and the filleted-spoke cutout is proved against a closed form (amends L09, L10 and L30)` follows L32, in L32's shape: a bold-lead paragraph per topic, `**Reversibility.**`, `Reason:` and `Kernel:`.
- Part one states the kickoff choice "warned, not re-cut", the `round(h, 3) > 0` rule, the real condition (root fillet over `(1.25 - x)*m/2` and profile shift over 0.125), the 15 rows, the fixture unchanged and README and `_outline` corrected, citing `13857e1`, `ac607d7` and `825095f`. It quotes no deviation figure.
- Part two answers L30's "pinned for the filleted spoke, which has none" with `_filleted_spoke_volume`, the four measured gaps (holes 2.39e-12, spokes-sharp 1.36e-12, spokes-filleted 2.73e-12, cells 8.87e-12 mm3), the D-06 outcome (not reached), the tripwire's measured 2.522e-4 mm3 (relative 8.59e-8), citing `61e1bea` and `b00c44c`.
- The composed-row exception is stated as it is: 12 tip-chamfer rows and 3 single-sided-recess rows pass `volume_rel=1e-6`, filed as `docs/tech_debt/active/2026-10-03-composed-cutout-volume-literals-pinned-at-six-places.md`.

## Task Commits

1. **Task 1: append L33** - `9fb667d` (docs)
2. **Task 2: end-state confirmation** - no commit by plan design; results recorded below.

**Plan metadata:** the SUMMARY / STATE / ROADMAP / REQUIREMENTS commit that follows this file.

## End-of-phase checks (Task 2)

| Check | Command | Result |
|---|---|---|
| Gate | `make verify` (run after the L33 commit) | `927 passed in 215.08s (0:03:35)`, exit 0 |
| Pre-commit hook | the same gate on `9fb667d` | `make verify (...) Passed` |
| Fixture and params | `git diff --quiet 5d9e907 -- tests/regression/pre_v0_2.json src/spur/params.py && git diff --name-only 5d9e907 -- src` | `src scope ok` (src/ differs only in `src/spur/calc.py` and `src/spur/model.py`) |
| model.py docstring-only, DerivedDimensions | AST compare with docstrings blanked, against `5d9e907` | `contracts unchanged` |
| Debt ledger | both files absent from `active/`; each in INDEX.md's Resolved section exactly once, in Active zero times | `ledger ok` |
| Append-only | `git diff --numstat 5d9e907 -- docs/architecture/decision_log.md` | `97  0` (97 added, 0 deleted) |
| L33 record check | the plan's python check (last/unique heading, header names, four shas, e-notation figures) | `L33 ok` |
| Fixture records crossing | `tests/regression/corpus.py`'s `cases()` through `profile`, `root_fillet`, `spline_start` and `derive()`, run 2026-10-03 on the committed code | 44 records, 0 with `round(h, 3) > 0`, 0 carrying the lead-in warning |

The last row is the source of L33's "0 of 44" claim: it was in CONTEXT.md and RESEARCH.md but in no committed test or SUMMARY, so it was recomputed here before L33 stated it.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] 14-02-SUMMARY.md's "about 1e-4 of the bar" was wrong**
- **Found during:** Task 1, while copying the D-06 outcome into L33.
- **Issue:** 14-02-SUMMARY.md said the largest gap (8.87e-12 mm3) was "about 1e-4 of the bar"; 8.87e-12 / 1e-9 is about 9e-3, under 1%. L33 would have inherited the error as a number the record could not back (the plan's L08 prohibition).
- **Fix:** L33 says "under 1% of the bar"; 14-02-SUMMARY.md's phrase was corrected to the same words. No test or source file affected.
- **Files modified:** `docs/architecture/decision_log.md`, `.planning/phases/14-honest-record/14-02-SUMMARY.md`
- **Commit:** `9fb667d` (L33); the 14-02-SUMMARY.md fix rides the closing `.planning/` commit with this file.

**Total deviations:** 1 auto-fixed (1 bug in a prior planning record). **Impact:** none on code or tests; the record's number is now the true one.

## Authentication Gates

None.

## Known Stubs

None.

## Threat Flags

None. A documentation entry only; no `src/` file, endpoint, auth path or schema changed.

## Debt

None filed in this plan. Both retired files' Resolution sentences that said "Decision log L33 records ..." were forward references until `9fb667d`; they are now true. The one debt open from the phase is `docs/tech_debt/active/2026-10-03-composed-cutout-volume-literals-pinned-at-six-places.md` (nice), filed in 14-02.

## Next Phase Readiness

All three plans of Phase 14 have summaries; the phase is ready for verification. The phase lands through `make pr.land PR=N` (L22/L25, D-15), not this plan, and the PR's reviewer is not the CLI that wrote the diff (CLAUDE.md cross-CLI review).

## Self-Check: PASSED

`docs/architecture/decision_log.md` holds exactly one `## L33 ` heading, after `## L32`; `9fb667d` is in `git log`; the four cited shas (`13857e1`, `ac607d7`, `825095f`, `61e1bea`) and `b00c44c` are in `git log`.
