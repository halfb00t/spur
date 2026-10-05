---
phase: 16-typing-validation-debt
plan: 02
subsystem: planning-record
tags: [nyquist, validation, gap-ledger, v0.2-archive, discovery-only]

requires:
  - phase: 16-typing-validation-debt
    provides: 16-01's committed Shape narrowing (a clean product tree for the human's hook commits)
provides:
  - "07-VALIDATION.md and 08-VALIDATION.md committed at status validated, both nyquist_compliant true as read"
  - "Gap ledger: 3 rows for Phase 07, 0 for Phase 08, all nice; no behaviour without a test (D-09 exception not reached)"
affects: [16-03]

actuals:
  tokens: 9535   # chars/4 over the two VALIDATION files (21061 chars) plus this SUMMARY (17077 chars)
  tasks: 3
  commits: 3
plan_head_before: dcb35185bf410e987a72c9f27e939b2b9099416a
plan_head_after: 5ba02d25999df56de651ce50e95d313556a199b3

tech-stack:
  added: []
  patterns:
    - "Read a skill-written Nyquist file back from committed state; count gaps by the Status cell and Manual-Only table alone"

key-files:
  created:
    - .planning/milestones/v0.2-phases/07-foundation-generalized-edge-selection-regression-fixture/07-VALIDATION.md
    - .planning/milestones/v0.2-phases/08-hex-bore/08-VALIDATION.md
  modified: []

key-decisions:
  - "Ledger counts Phase 07's three Manual-Only rows although the skill's own audit reports 0 gaps: the plan's row rule counts every Manual-Only data row (over-counting is the safe direction)"
  - "Phase 08's 08-01-02 (a human-approval gate) is not a ledger row: its Status cell reads green, and the rule reads that cell alone"

requirements-completed: []

coverage:
  - id: D1
    description: "07-VALIDATION.md and 08-VALIDATION.md committed at status validated, each last commit carrying its file alone, no test written"
    requirement: "REQ-nyquist-phases-7-8"
    verification:
      - kind: other
        ref: "Task 1 verify: validated and committed {'07-VALIDATION.md': True, '08-VALIDATION.md': True}; no tests written by the skill"
        status: pass
    human_judgment: false
  - id: D2
    description: "Gap ledger: one row per Phase 07 Manual-Only row, none for Phase 08, each naming what proves it today"
    requirement: "REQ-nyquist-phases-7-8"
    verification:
      - kind: unit
        ref: "tests/regression tests/test_calc.py#test_the_bore_rim_limit_is_the_bore_radius_for_round_and_d_flat_bores tests/test_model.py#test_a_bore_chamfer_that_selects_no_rim_edges_is_a_build_error_not_a_bare_bore (118 passed)"
        status: pass
    human_judgment: false
  - id: D3
    description: "D-09 exception not reached: no behaviour without a test"
    requirement: "REQ-nyquist-phases-7-8"
    verification: []
    human_judgment: true
    rationale: "Whether the regeneration byte-stability row is a tool property with a named command (nice) or a behaviour without a test (must) is a judgment; the executor classified it nice and says why in the ledger section"

duration: 11min
completed: 2026-10-05
status: complete
---

# Phase 16 Plan 02: Phase 7 and 8 Nyquist pass Summary

**The human ran `/gsd-validate-phase 7` and `8` against the archived directories; both files read `status: validated` and `nyquist_compliant: true` from committed state, three Phase 07 Manual-Only rows became the gap ledger, every one is proved today, and no test was written.**

## Performance

- **Duration:** 11 min for this continuation (2026-10-05T03:23Z to 03:34Z, from the last validation commit to the SUMMARY write); Task 1 was the human's wall time and is not measured here
- **Tasks:** 3 (Task 1 the human's; Task 2 the ledger; Task 3 not presented, no `must` row)
- **Files:** 2 skill-written planning files (committed by the human) plus this SUMMARY

## Pre-state

Captured by the first executor before the human acted (reported inline then; written here from its report):

- HEAD `dcb3518` on `gsd/phase-16-typing-validation-debt`; `git status --porcelain --untracked-files=no` empty; the only untracked path was `.planning/milestone.lock` (never staged).
- Both archived directories were State B: PLAN and SUMMARY files and a `*-VERIFICATION.md`, no `*-VALIDATION.md`. Phase 7: 07-01 and 07-02 PLAN/SUMMARY, CONTEXT, DISCUSSION-LOG, PATTERNS, REVIEW, REVIEW-FIX, SECURITY, VERIFICATION. Phase 8: 08-01 to 08-04 PLAN/SUMMARY, CONTEXT, DISCUSSION-LOG, PATTERNS, REVIEW, SECURITY, VERIFICATION.
- `init.phase-op 7` phase_dir: `/Users/halfb00t/git/halfb00t/spur/.planning/milestones/v0.2-phases/07-foundation-generalized-edge-selection-regression-fixture`
- `init.phase-op 8` phase_dir: `/Users/halfb00t/git/halfb00t/spur/.planning/milestones/v0.2-phases/08-hex-bore`
- `loop render-hooks verify:post --raw` listed `capId: nyquist`, `skill: validate-phase` (active). No pre-commit hook was running.

## Validation runs

**Phase 7: the human's resume message carried no gap table; the tables below are read from the committed 07-VALIDATION.md at 5ba02d2 (two audit runs).** The human wrote "Unfortunately I didn't save the result. But I ran it in this branch." Nothing was invented to fill the gap.

The human's resume message, verbatim:

> phase 7:
> Unfortunately I didn't save the result. But I ran it in this branch.
>
> phase 8:
>
> All requirements have automated verification. 0 gaps, no auditor spawned, no test files generated.
>
> Written: .planning/milestones/v0.2-phases/08-hex-bore/08-VALIDATION.md (State B reconstruction). Committed 8ae468e docs(phase-08): add validation strategy; pre-commit make verify passed in the hook.
>
> Measured 2026-10-05, HEAD 655583f:
> - make test: 929 passed in 66.87s, coverage 97.24 %, exit 0
> - hex subset: 110 passed, 619 deselected in 23.12s; 7 hex edge-selector rows collected
> - fixture pre_v0_2.json byte-unchanged (git diff --exit-code 0)
> - CLI live: --bore-hex 6 → 6.15 / 7.101 / null + one warning; --bore-hex 25 exit 2 with the root sentence; --bore-hex 23.4 the chamfer sentence
> - one-set make bench.build: row printed, 0.40 s of 30 s, exit 0
>
> Drift noted in the doc, none weakening coverage:
> - 08-01 doc greps now target the archived .planning/milestones/v0.2-REQUIREMENTS.md / v0.2-ROADMAP.md (2 cites, 0 superseded sentences, 5 evolution lines)
> - 08-04 Task 2's sed … ,$p verify overruns into later sections of bench/RESULTS.md; bounded to the Phase 8 section: 16 rows, 0 **NO**
> - bore_hex sits after keyway_depth since Phase 9; test asserts the new position
> - round-bore chamfer debt resolved in 4b6a5b9
>
> Outside phase 8, flagged for you: bench/RESULTS.md carries 20 **NO** (over-SPUR_BUILD_TIMEOUT) rows — 16 in "Composed build and export time (Phase 12)", 4 in "Body cutout build and export time (Phase 11)". Not touched.
>
> Tooling note: gsd_run query commit timed out at 30 s against the ~70 s pre-commit hook and orphaned a make verify; committed with plain git commit. No stale lock remained.

**Values as read from committed frontmatter** (`grep -E '^(status|nyquist_compliant):'` at HEAD `5ba02d2`):

| Phase | status | nyquist_compliant | last commit of the file |
|-------|--------|-------------------|-------------------------|
| 07 | validated | true | `5ba02d2` docs(phase-07): re-audit validation strategy, correct quick-run command |
| 08 | validated | true | `8ae468e` docs(phase-08): add validation strategy |

Both files also carry `wave_0_complete: true`, `reconstructed: true`, `created: "2026-10-05"`.

**Commits, and who made them.** `655583f` docs(phase-07): add validation strategy (Phase 7's first run); `8ae468e` docs(phase-08): add validation strategy; `5ba02d2` docs(phase-07): re-audit validation strategy, correct quick-run command (Phase 7's second run). Each carries exactly one VALIDATION.md. The human's tooling note says gsd's commit helper timed out at 30 s and the commit was a plain `git commit` with the hook running; the note is stated once and names no phase, and Phase 8's message names `8ae468e` as passing its hook. For the two Phase 7 commits the message does not say whether the helper or a plain commit made them. Git authorship (Andrew S on all three) does not distinguish the two routes. No `--no-verify` is claimed anywhere.

**Phase 7 ran twice.** The first run wrote the file (`655583f`, "Validation Audit 2026-10-05": gaps found 0, resolved 0, escalated 0). The second ran as State A at HEAD `8ae468e` (`5ba02d2`, "re-run": gaps found 0, 0, 0) and corrected one row: the quick-run command had listed all of `tests/test_calc.py tests/test_model.py` (693 cases, 182.35 s serial) while quoting the 119-case ~35 s figure; it now names the eight tests that figure was measured on.

**Post-checks from committed state** (Task 1's two verify commands, run at HEAD `5ba02d2`): "validated and committed {'07-VALIDATION.md': True, '08-VALIDATION.md': True}" and "no tests written by the skill". `git log --grep '^test(phase-0?[78])' 085e5a6..HEAD` is empty; `git diff --name-only 085e5a6 -- tests src` lists exactly `src/spur/model.py` and `tests/test_model.py` (16-01's two files).

**Human versus committed files.** Phase 8: the human's text agrees with 08-VALIDATION.md on every point checked: 0 gaps, `929 passed in 66.87s`, 97.24 %, `110 passed, 619 deselected in 23.12s`, 7 hex rows, fixture byte-unchanged, the three CLI readings, `0.40 s of 30 s`, and the four drift notes (the file's "Reconstruction Notes" carries all four; the file adds a fifth, `test_each_edge_selector_picks_exactly_its_own_edges` growing to 30 rows, and "suite size went from 330 to 929"). No disagreement. Phase 7: nothing to compare. Neither run reached the skill's "Fix all gaps / Skip" gate as far as the record shows: both audits report 0 gaps found, so no "Skip" answer was ever needed, and the three Manual-Only rows below were written by the skill's own State B reconstruction as manual by design rather than as skipped gaps.

## Gap ledger

Phase 07: `nyquist_compliant` read as `true`; gap rows: 3 (three Manual-Only data rows; all six per-task Status cells read green).
Phase 08: `nyquist_compliant` read as `true`; gap rows: 0 (the Manual-Only section is the sentence "All phase behaviors have automated verification." with no table; all ten per-task Status cells read green).

| # | Phase | Task id | Gap (verbatim from 0N-VALIDATION.md) | Proved today by | Severity |
|---|-------|---------|--------------------------------------|-----------------|----------|
| 1 | 07 | manual-only | D-06 cost gate: the fixture's `make verify` delta is measured and, above 15.0 s, decided by a human rather than trimmed silently | Committed record, not a behaviour: `bench/RESULTS.md` section "Regression fixture cost (Phase 7, D-06)" (mean(A) 32.10 s, mean(B) 48.37 s, delta 16.27 s, Option A accepted) and STATE.md Decisions "[Phase 07]: D-06 gate" | nice |
| 2 | 07 | manual-only | Regeneration is byte-stable: two consecutive `make fixture.regen` runs on an unchanged tree write identical JSON | Committed record: `07-01-SUMMARY.md` coverage item "Regeneration is byte-stable" (cmp of two consecutive runs) and the row's own command in `07-VALIDATION.md`. Re-measured 2026-10-05 into the scratchpad, not committed: `capture.main()` run twice, outputs byte-identical. The replay `tests/regression/test_pre_v0_2.py` imports and runs capture's `derived` and `solid` helpers on every record (118 passed in 12.86s); no test runs the writer | nice |
| 3 | 07 | manual-only | Tripwire: a silently vanished bore chamfer turns exactly the 32 chamfered-bore solid cases red and no derive case | Committed record: `07-VALIDATION.md` row (`32 failed, 53 passed in 13.81s`) and `07-VERIFICATION.md` (`32 failed, 53 passed in 13.64s`); re-run at HEAD 5ba02d2: `32 failed, 53 passed in 14.02s`, tree clean. The production path now raises instead: `tests/test_model.py::test_a_bore_chamfer_that_selects_no_rim_edges_is_a_build_error_not_a_bare_bore`, `tests/test_model.py::test_each_edge_selector_picks_exactly_its_own_edges`, `tests/test_model.py::test_a_recess_fillet_that_selects_no_floor_edges_is_a_build_error`, `tests/test_calc.py::test_the_bore_rim_limit_is_the_bore_radius_for_round_and_d_flat_bores` (118 passed in 12.86s, the cited ids as the plan's verify ran them) | nice |

Notes the table cannot hold:

- **Row 2 is the closest call.** The byte-stability of `capture.py`'s writer (sorted keys, indent 2, trailing newline, deterministic kernel) has no test of its own; the row carries a named command and a committed measurement, and the writer produces a dev file, not a number a user cuts metal to, so it is `nice` by D-09's rule (a task without a named automated command is `nice`; only a behaviour with no test at all is `must`). The human can reclassify it when 16-03 files the debt. The scratch run also showed the regenerated records differ from the committed fixture in exactly ten `derived` fields added since the capture (`cutout_hub_wall`, `cutout_rim_wall`, `hex_across_corners`, `hex_across_flats`, `hex_cell_count`, `hex_cell_effective`, `keyway_floor_to_wall`, `keyway_width_effective`, `spoke_fillet_effective`, `tip_chamfer_effective`); no recorded field and no solid number moved, and `provenance` differs only in `captured` and `git_head`. That is the replay's designed behaviour (REQ-derived-dimensions-additive), not drift.
- **Zero audit gaps, three ledger rows.** Phase 07's audit tables say "Gaps found 0" while the ledger has three rows: the plan's row rule counts every Manual-Only data row, whatever the skill called it. 16-03 files the debt from this ledger, so its Phase 07 file will say three.
- **Phase 08's 08-01-02** is a human-approval gate (a process gate, not a behaviour; `08-VALIDATION.md` says the approval "is not re-runnable") but its Status cell reads `✅ green (gate passed 2026-09-26)`, so by the Status-cell rule it is not a gap and Phase 08 is zero rows. Surfaced here so 16-03's COMPLIANT classification is read with that fact.

## D-09 exception

D-09 exception not reached -- no behaviour without a test

No ledger row is `must`: three `nice` rows, each with a named command and a committed record, and the behaviours behind them run under `make verify`. No checkpoint:decision was presented, and the plan wrote no test.

## Accomplishments

- Read both skill-written files back from committed state: tracked, clean against HEAD, `status: validated`, `nyquist_compliant: true`, each last commit carrying its file alone.
- Built the gap ledger by the Status-cell rule: 3 rows for Phase 07, 0 for Phase 08, and ran the node ids it cites green (118 passed in 12.86s).
- Confirmed the discovery-only rule held: no `test(phase-07)`/`test(phase-08)` commit, and `tests/` and `src/` differ from 085e5a6 only by 16-01's two files.

## Deviations from Plan

None - plan executed exactly as written.

Procedural notes, not deviations: (1) the first executor reported the pre-state inline instead of writing it; it is written above from that report. (2) Task 1's `plan_head_before` ledger file was not created at plan start, so it was written at the continuation from the pre-state HEAD `dcb3518` the first executor reported; `commits: 3` counts the human's three validation commits, and the closing SUMMARY commit follows `plan_head_after` as in 16-01. (3) The scratch regeneration ran `capture.main()` with its output path pointed into the scratchpad, so no file under `tests/` was touched; `git diff --exit-code tests/regression/pre_v0_2.json` exited 0 afterwards.

## Observations outside this plan

Recorded, not acted on (the plan says so). The human flagged that `bench/RESULTS.md` carries `**NO**` (over-`SPUR_BUILD_TIMEOUT`) rows outside Phase 8: "16 in 'Composed build and export time (Phase 12)', 4 in 'Body cutout build and export time (Phase 11)'". A read-only count of table rows containing `**NO**` by section heading gives 18 under "Composed build and export time (Phase 12)" and 4 under "Body cutout build and export time (Phase 11)", 22 in all; the Phase 11 figure agrees, the Phase 12 figure does not (16 stated, 18 read), and the difference was not resolved. Phase 12's 12-03 lowered `spoke_count`'s `le` to 32 and recorded a re-run with every composed row inside 30 s, so the rows may be history from runs before that decision, but that was not checked here.

Tooling note, carried: `gsd_run query commit` cannot survive the ~64 to 70 s pre-commit hook (`docs/tech_debt/active/2026-09-25-gsd-commit-timeout-kills-cold-verify-hook.md` is still active); the human's note confirms it again on this plan.

## Issues Encountered

None.

## Known Stubs

None.

## Threat Flags

None. No network endpoint, auth path or schema changed; T-16-06 through T-16-08 are mitigated by the committed-state reads above, and no package was installed (T-16-SC).

## Next Phase Readiness

Ready for 16-03: it parses `## Pre-state`, `## Validation runs`, `## Gap ledger` and `## D-09 exception` from this file. Phase 07 has three `nice` gap rows to file (one debt file); Phase 08 has none (no file); no `must` row to carry. Both `nyquist_compliant` values read `true`, so 16-03's audit amendment lists both phases as compliant by what was read, not by what the requirement hoped for.

Filed no ideas or debt items in this plan; 16-03 files the Phase 07 debt from the ledger.

## Self-Check: PASSED
