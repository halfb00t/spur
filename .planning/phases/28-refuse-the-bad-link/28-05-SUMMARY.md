---
phase: 28-refuse-the-bad-link
plan: 05
subsystem: review-triage
tags: [gap-closure, review-disposition, tech-debt, checkpoint-decision]
status: complete
gap_closure: true
gap_ids: [G-28-1, G-28-2]

requires:
  - phase: 28-refuse-the-bad-link
    provides: 28-REVIEW.md (WR-01, WR-02, WR-03, IN-01, IN-02) and the UAT gaps G-28-1 and G-28-2
provides:
  - D-19..D-23 in 28-CONTEXT.md, the human's dispositions, read by 28-06, 28-07 and 28-08
  - one debt item (WR-02, Severity must) with an event trigger and its INDEX row
affects: [28-06, 28-07, 28-08]

actuals:
  tokens: 2600
  tasks: 2
  commits: 2
plan_head_before: be72b4ede91c749d1399c057b673a4df2626b399
plan_head_after: eb78bb10015acc23ae2a92b595c10cc87ae918d4

tech-stack:
  added: []
  patterns: []

key-files:
  created:
    - docs/tech_debt/active/2026-10-21-an-accepted-link-token-builds-under-a-blank-box.md
  modified:
    - .planning/phases/28-refuse-the-bad-link/28-CONTEXT.md
    - docs/tech_debt/INDEX.md

key-decisions:
  - "D-19 WR-01 fix (28-07, under a dated amendment to L44)"
  - "D-20 WR-02 defer (debt item, Severity must, event trigger)"
  - "D-21 WR-03 / G-28-2 / 10 IN-02 fix (L45 to be logged by 28-06)"
  - "D-22 IN-01 fix, recording the human's reading that the replacement token tightens the SC2 readHash-end pin"
  - "D-23 IN-02 fix"

requirements-completed: [REQ-info-findings-triaged, REQ-old-info-findings-triaged]

duration: continuation run (Task 2 only; Task 1 was the human checkpoint)
completed: 2026-10-21
---

# Phase 28 Plan 05: The human disposes of Phase 28's review findings Summary

**The human chose a disposition for each of WR-01, WR-02, WR-03 (= G-28-2), IN-01 and IN-02 at a blocking-human checkpoint; they are recorded as D-19..D-23 and the one deferral (WR-02) is filed with an event trigger. No code moved.**

## The human's answer

Task 1 (`checkpoint:decision`, `gate="blocking-human"`, no `auto_select`), verbatim:

`WR-01 fix; WR-02 defer; WR-03 fix; IN-01 fix; IN-02 fix`

Every answer is inside its allowed set and nothing extra was given, so every offered default applied.

## Accomplishments

- **D-19..D-23 recorded** in `28-CONTEXT.md` under `### Gap-closure decisions (taken at the 28-05 checkpoint, 2026-10-21, UAT G-28-1 and G-28-2)`, directly before `### Claude's Discretion`, D-01..D-18 untouched. Commit `ad28848`, alone.
- **The five D lines:**
  - `D-19 (WR-01)`: `fix`. 28-07 carries it out under a dated amendment to L44.
  - `D-20 (WR-02)`: `defer`. Filed as `docs/tech_debt/active/2026-10-21-an-accepted-link-token-builds-under-a-blank-box.md`.
  - `D-21 (WR-03, G-28-2, 10 IN-02)`: `fix`. L45 is to be logged by 28-06.
  - `D-22 (IN-01)`: `fix`. Records the human's reading that the replacement token tightens the SC2 readHash-end pin.
  - `D-23 (IN-02)`: `fix`.
- **One debt item filed** for D-20: Severity must, trigger "the next edit of `refuse()` or `gearQuery()` in `src/spur/static/app.js`, or a report of a part that does not match a blank box" (an event, not a decision), with its INDEX `## Active` row. Commit `eb78bb1`, item and INDEX together. D-19 and D-22 are `fix`, so their debt files were not created.
- No fix, no Lxx and no `28-REVIEW-DISPOSITION.md` row were written here; 28-06..28-08 own them.

Facts re-measured from the tree before citing: `refuse()` at `src/spur/static/app.js:115-117`, `gearQuery()` at `135-142`, L44 **The server decides** at `docs/architecture/decision_log.md:2990`, `bench/RESULTS.md:6637` `### Tokens a control cannot hold (28-01)`, `tests/test_browser.py:122` `ACCEPTED_LINK = "face_width=5."`. The IN-01 pinned token is at `tests/test_api.py:262` (the plan said 263); 28-07 should use 262.

## Verification

- Plan Task 2 python check: printed `D-19..D-23 recorded; deferred items filed with event triggers`, exit 0.
- `make verify`: exit 0, result line `======================= 1348 passed in 222.95s (0:03:42) =======================`.
- `git diff --exit-code v0.5 -- tests/regression/`: empty.
- `git show --stat --format= ad28848` names only `28-CONTEXT.md`.

## Deviations from Plan

None - plan executed exactly as written.

## Known Stubs

None.

## Filed debt

One item filed: `docs/tech_debt/active/2026-10-21-an-accepted-link-token-builds-under-a-blank-box.md` (Severity must).

## Next Phase Readiness

Ready for 28-06 (D-21: gate `tip_chamfer_effective` on `tch`, log L45, retire the tip-chamfer debt item), then 28-07 (D-19, D-22, and D-20's disposition row) and 28-08 (IN-02 and the ledger).

## Self-Check: PASSED

- FOUND: `.planning/phases/28-refuse-the-bad-link/28-CONTEXT.md` (five D lines, one each)
- FOUND: `docs/tech_debt/active/2026-10-21-an-accepted-link-token-builds-under-a-blank-box.md`, one INDEX row
- FOUND commits: `ad28848`, `eb78bb1` (both ancestors of HEAD)
