---
phase: 09-keyway-bore
plan: 01
subsystem: planning-docs
tags: [requirements, roadmap, keyway, documentation, edit-phase]

# Dependency graph
requires:
  - phase: 08-hex-bore
    provides: "08-01's amendment-task shape (edit-phase tooling, one human confirmation, milestone-scope check before/after) and bore_mouth_limit/bore_rim_limit as the shape-general pair Phase 9's rules extend"
provides:
  - "REQ-keyway-bore amended: datum is the as-cut bore wall (bore_d + bore_clearance)/2 (D-14)"
  - "REQ-keyway-wall-refused amended: 422 only at the floor corner vs the root circle, naming keyway_depth and keyway_width; the face recess yields to the corner instead, never a 422 (D-09/D-10)"
  - "ROADMAP Phase 9 Requirements line unwrapped onto one line (all five REQ-IDs readable by init.plan-phase)"
  - "ROADMAP Phase 9 SC1, SC3, SC4 amended to match D-14, D-09/D-10, D-05/D-07"
  - "STATE.md Roadmap Evolution line recording the Phase 9 edit"
affects: [09-02-PLAN.md, 09-03-PLAN.md, 09-04-PLAN.md, 09-05-PLAN.md]

# Actuals (#2632)
actuals:
  tokens: 2599
  tasks: 3
  commits: 1

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Phase-section amendment through edit-phase's write_updated_phase step only: scoped Edit of the phase section, milestone-scope check before and after, one STATE.md Roadmap Evolution line — never a direct whole-file ROADMAP.md write (08-01's precedent, D-20)"
    - "REQUIREMENTS.md has no gsd verb that edits requirement text; amended by scoped Edit of the named bullets only, shown to the human in the same checkpoint as the ROADMAP diff"

key-files:
  created: []
  modified:
    - .planning/REQUIREMENTS.md
    - .planning/ROADMAP.md
    - .planning/STATE.md

key-decisions:
  - "Human approved all proposed texts verbatim at the Task 2 checkpoint — no wording changes"
  - "D-14: the keyway depth datum is the as-cut bore wall (bore_d + bore_clearance)/2, not bore_d/2 + bore_clearance"
  - "D-09/D-10: a keyway is refused only at the floor corner vs the root circle; a face recess yields to the corner instead of ever being refused"
  - "D-07: SC4's proof is the pre-keyway rim-selector count plus a built-solid chamfer/sharp-edge test, since a selector on a finished, chamfered solid finds no edges"

patterns-established:
  - "A phase's ROADMAP section is never rewritten wholesale mid-milestone; only the named lines change, verified by a milestone-scope check before and after the write"

requirements-completed: []  # None marked complete: REQ-keyway-bore, REQ-keyway-wall-refused and REQ-hex-rim-chamfer are also declared by sibling plans 09-02..09-05 which have not yet produced a SUMMARY (shared-ID gate, requirements.ready-ids reported 0/3 ready)

coverage:
  - id: D1
    description: "REQUIREMENTS.md REQ-keyway-bore and REQ-keyway-wall-refused amended to match D-14 and D-09/D-10; footer updated"
    verification:
      - kind: other
        ref: "grep -c '(bore_d + bore_clearance)/2' .planning/REQUIREMENTS.md; grep -c 'Phase 9 D-14' .planning/REQUIREMENTS.md; grep -c 'Phase 9 D-09/D-10' .planning/REQUIREMENTS.md; sed -n '/REQ-keyway-wall-refused\\*\\*/,/REQ-hex-bore\\*\\*/p' .planning/REQUIREMENTS.md | grep -cF 'naming \\`keyway_depth\\` and \\`keyway_width\\`'"
        status: pass
    human_judgment: false
  - id: D2
    description: "ROADMAP Phase 9 Requirements line unwrapped; SC1, SC3, SC4 amended to match D-14, D-09/D-10, D-05/D-07; SC2, SC5, Goal, Depends on, Research flag and Plans lines untouched"
    requirement: REQ-hex-rim-chamfer
    verification:
      - kind: other
        ref: "sed -n '/^### Phase 9: Keyway Bore/,/^### Phase 10/p' .planning/ROADMAP.md | grep -cF -e '(bore_d + bore_clearance)/2' -e '09-CONTEXT.md D-09/D-10' -e '09-CONTEXT.md D-05/D-07' (=3); same with the superseded phrases (=0); git show HEAD -- .planning/ROADMAP.md diff scope"
        status: pass
    human_judgment: false
  - id: D3
    description: "STATE.md carries one new Roadmap Evolution line for the Phase 9 edit; ROADMAP.md written only through edit-phase's write step with the milestone-scope check unchanged before/after (phases 7-12)"
    verification:
      - kind: other
        ref: "grep -c 'per 09-CONTEXT.md D-20' .planning/STATE.md; gsd_run query roadmap.milestone-scope before/after comparison"
        status: pass
    human_judgment: false

duration: 14min
completed: 2026-09-27
status: complete
---

# Phase 9 Plan 1: Amend Phase 9's requirements and roadmap criteria Summary

**REQ-keyway-bore, REQ-keyway-wall-refused, and ROADMAP SC1/SC3/SC4 now state the as-cut-wall datum (D-14) and the corner-vs-root refusal with a yielding recess (D-09/D-10), replacing the superseded formulas — through edit-phase's tooling with one human confirmation (D-20).**

## Performance

- **Duration:** 14 min (spanning a Task 2 human-verify checkpoint)
- **Started:** 2026-09-27T12:57:00Z
- **Completed:** 2026-09-27T13:11:24Z
- **Tasks:** 3
- **Files modified:** 3

## Accomplishments
- REQ-keyway-bore's datum parenthetical corrected from `bore_d/2 + bore_clearance` to `(bore_d + bore_clearance)/2` (Phase 9 D-14), the as-cut bore wall this phase's keyway floor is measured from.
- REQ-keyway-wall-refused rewritten: the 422 fires only at the floor corner vs the root circle, naming `keyway_depth` and `keyway_width`; the earlier "or of a recess wall" clause is gone — a face recess now yields to the keyway corner instead, per D-09/D-10.
- ROADMAP Phase 9's Requirements line unwrapped onto one line so `init.plan-phase 9` reads all five requirement IDs (previously only 3 of 5 were visible on the wrapped first line).
- ROADMAP SC1, SC3 and SC4 amended to match D-14, D-09/D-10 and D-05/D-07 respectively; SC2, SC5, the Goal, Depends on, Research flag and Plans lines are byte-identical to before.
- One STATE.md Roadmap Evolution line records the edit, citing 09-CONTEXT.md D-20.

## Task Commits

Each task was committed atomically per the plan's design (D-20's amendment-task shape has all three files land in one commit, not per-task):

1. **Task 1: Amend REQ-keyway-bore and REQ-keyway-wall-refused, build the Phase 9 section edit diff** - no commit (plan defers all commits to Task 3; REQUIREMENTS.md edit applied to the working tree, the ROADMAP diff built to the session scratchpad)
2. **Task 2: Human confirms the amendment wording before the roadmap is written** - checkpoint, no commit (human answered "approved" verbatim)
3. **Task 3: Write the approved Phase 9 edit through edit-phase's write step and commit the amendment** - `69948df` (docs)

**Plan metadata:** captured in this same commit — `69948df` (`docs(09-01): ...`) already carries REQUIREMENTS.md, ROADMAP.md and STATE.md per the plan's D-19/D-20-driven single-commit design; no separate metadata commit follows.

## Files Created/Modified
- `.planning/REQUIREMENTS.md` - REQ-keyway-bore datum, REQ-keyway-wall-refused body, footer line
- `.planning/ROADMAP.md` - Phase 9 Requirements line, SC1, SC3, SC4
- `.planning/STATE.md` - one new Roadmap Evolution line for Phase 9 (plus the orchestrator's own phase-begin tracking fields, already present before this plan's task ran)

## Decisions Made
- Human approved all four proposed texts (REQUIREMENTS.md's two amended bullets, ROADMAP's Requirements line plus SC1/SC3/SC4) verbatim at the Task 2 checkpoint — no wording changes requested.
- ROADMAP.md was written only through edit-phase's `write_updated_phase` step (scoped Edit of the Phase 9 section only), with `gsd_run query roadmap.milestone-scope` compared before and after the write and found unchanged (phases 7-12, scope "complete") — never a direct whole-file write, per D-20.

## Deviations from Plan

None - plan executed exactly as written. This continuation picked up at Task 3 after the human resolved the Task 2 checkpoint with "approved"; Task 1's and Task 2's prior work (verified intact before any write: REQUIREMENTS.md diff present and touching only the two named bullets plus the footer, `.planning/ROADMAP.md` unmodified, the three scratchpad artifacts present and matching what Task 3 needed to write) required no rework.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
Ready for 09-02-PLAN.md (the tracer: `?keyway_width=3&keyway_depth=1.4` end to end). The phase verifier and every later plan in this phase now read D-07/D-09/D-10/D-14 in SC1, SC3, SC4 and the two amended requirements, not the superseded sentences. `init.plan-phase 9` reports all five requirement IDs (`REQ-bore-derived-numbers` confirmed present via `grep -c`). No blockers.

---
*Phase: 09-keyway-bore*
*Completed: 2026-09-27*

## Self-Check: PASSED

- `[ -f .planning/REQUIREMENTS.md ]` → FOUND
- `[ -f .planning/ROADMAP.md ]` → FOUND
- `[ -f .planning/STATE.md ]` → FOUND
- `git log --oneline --all --grep="09-01"` → FOUND `69948df docs(09-01): amend the keyway datum, the recess clause and SC4's proof to match D-07/D-09/D-14 (D-20)`
- All plan-level `<verification>` and `<success_criteria>` re-run and passing (see task-level verify output above): REQUIREMENTS.md datum/refusal text present (1/1/2/1 counts), ROADMAP.md amended-text count = 3, superseded-text count = 0, commit touches exactly the three named files, Requirements line matches exactly, `init.plan-phase 9` carries `REQ-bore-derived-numbers`, STATE.md carries the D-20 citation, `gsd_run query roadmap.milestone-scope` phase set unchanged (7-12), pre-commit `make verify` passed (330 tests, ~68s warm).
