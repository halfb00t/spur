---
phase: 08-hex-bore
plan: 01
subsystem: docs
tags: [requirements, roadmap, planning, hex-bore, keyway-bore]

# Dependency graph
requires:
  - phase: 07-foundation
    provides: generalized edge selector and regression fixture this phase's plans build on
provides:
  - REQ-hex-bore amended: hex replaces bore_d and bore_flat (warned, never refused); the hex x keyway 422 moved to REQ-keyway-bore
  - REQ-keyway-bore amended: carries the hex x keyway 422 moved from REQ-hex-bore
  - ROADMAP Phase 8 SC2 restated per 08-CONTEXT.md D-01/D-02 (bore_flat ignored + warned, never a 422)
  - ROADMAP Phase 9 SC2 gains the hex x keyway 422 sentence
  - ROADMAP Phase 12 SC1 attributes the keyway x hex refusal to Phase 9
  - Three STATE.md Roadmap Evolution lines (phases 8, 9, 12)
affects: [08-02-PLAN.md, 08-03-PLAN.md, 08-04-PLAN.md, "Phase 9: Keyway Bore", "Phase 12: Composition Pass"]

# Actuals (#2632) — pairs with the plan's estimate to calibrate future estimates.
# Same estimateTokens scale (chars/4 over the realized diff), never a harness token count.
actuals:
  tokens: 1964
  tasks: 3
  commits: 1

# Tech tracking
tech-stack:
  added: []
  patterns: []

key-files:
  created: []
  modified:
    - .planning/REQUIREMENTS.md
    - .planning/ROADMAP.md
    - .planning/STATE.md

key-decisions:
  - "Human approved all four proposed texts (REQUIREMENTS REQ-hex-bore, REQUIREMENTS REQ-keyway-bore, ROADMAP Phase 8 SC2, ROADMAP Phase 9 SC2 + Phase 12 SC1) verbatim, with no wording changes, at the Task 2 checkpoint."
  - "ROADMAP.md was written only through the edit-phase workflow's write step (scoped Edit per phase section, milestone-scope check before/after), never a direct whole-file write — per D-01's 'roadmap edits through the phase tooling, never a direct write'."

patterns-established: []

requirements-completed: [REQ-hex-bore]

coverage:
  - id: D1
    description: "REQ-hex-bore and REQ-keyway-bore amended in REQUIREMENTS.md: the hexagon replaces the whole round profile (bore_d, bore_flat warned when non-zero, never refused); the hex x keyway 422 moved to REQ-keyway-bore"
    requirement: "REQ-hex-bore"
    verification:
      - kind: other
        ref: "grep -c 'Phase 8 D-01' .planning/REQUIREMENTS.md (prints 3, >= 2 required)"
        status: pass
      - kind: other
        ref: "sed -n '/^### Bore profiles/,/^### Body cutouts/p' .planning/REQUIREMENTS.md | grep -c 'or a keyway is a 422' (prints 0 — superseded sentence gone)"
        status: pass
      - kind: other
        ref: "grep -c 'REQ-keyway-bore, Phase 9' .planning/REQUIREMENTS.md (prints 1)"
        status: pass
    human_judgment: false
  - id: D2
    description: "ROADMAP Phase 8 SC2 restated per D-01/D-02 (bore_flat ignored + warned, never a 422); Phase 9 SC2 gains the hex x keyway 422 sentence; Phase 12 SC1 attributes the refusal to Phase 9 — all three written through edit-phase's write step with a milestone-scope check before/after"
    requirement: "REQ-hex-bore"
    verification:
      - kind: other
        ref: "sed -n '/^### Phase 8: Hex Bore/,/^### Phase 9/p' .planning/ROADMAP.md | grep -c '08-CONTEXT.md D-01/D-02' (prints 1)"
        status: pass
      - kind: other
        ref: "sed -n '/^### Phase 8: Hex Bore/,/^### Phase 9/p' .planning/ROADMAP.md | grep -c 'or a keyway field is a 422' (prints 0)"
        status: pass
      - kind: other
        ref: "sed -n '/^### Phase 9: Keyway Bore/,/^### Phase 10/p' .planning/ROADMAP.md | grep -c 'moved here from Phase 8 SC2' (prints 1)"
        status: pass
      - kind: other
        ref: "sed -n '/^### Phase 12: Composition Pass/,/^## Process Notes/p' .planning/ROADMAP.md | grep -c 'keyway × hex (Phase 9)' (prints 1)"
        status: pass
      - kind: other
        ref: "gsd-tools query roadmap.milestone-scope before and after the write (phases 7-12, count 6, unchanged)"
        status: pass
    human_judgment: false
  - id: D3
    description: "STATE.md records one Roadmap Evolution line per edited phase (8, 9, 12), written only after the human's approval at the Task 2 checkpoint"
    verification:
      - kind: other
        ref: "grep -cE '^- Phase (8|9|12) edited' .planning/STATE.md (prints 3)"
        status: pass
    human_judgment: false

# Metrics
duration: ~15min (Task 3, continuation from the approved Task 2 checkpoint)
completed: 2026-09-26
status: complete
---

# Phase 8 Plan 01: Amend REQ-hex-bore and Roadmap SC2 Before Any Code Summary

**Moved the hex-bore requirement's wording from "hex + bore_flat is a 422" to "hex replaces bore_flat, warned not refused," and relocated the hex x keyway 422 to Phase 9's requirement — all through the edit-phase tooling with one human confirmation.**

## Performance

- **Duration:** ~15 min for this continuation (Task 3 only; Tasks 1-2 ran in a prior session ending at the human checkpoint)
- **Completed:** 2026-09-26T15:00:17Z
- **Tasks:** 3 (Task 1: amend + build diffs, Task 2: human checkpoint, Task 3: write + commit)
- **Files modified:** 3 (.planning/REQUIREMENTS.md, .planning/ROADMAP.md, .planning/STATE.md)

## Accomplishments
- REQ-hex-bore now says the hexagon replaces the whole round profile: `bore_d` and `bore_flat` are ignored and named in `warnings` when non-zero, never refused; the hex x keyway 422 points to REQ-keyway-bore, Phase 9
- REQ-keyway-bore gained the hex x keyway 422 sentence, moved from REQ-hex-bore
- ROADMAP Phase 8 SC2 restated per 08-CONTEXT.md D-01/D-02 (cites the decision, not the superseded sentence); Phase 8 SC1, SC3, SC4, SC5 are byte-identical to before this plan
- ROADMAP Phase 9 SC2 and Phase 12 SC1 updated to carry/attribute the relocated refusal
- Three ROADMAP writes went through edit-phase's `write_updated_phase` step (scoped Edit per section, milestone-scope check before and after — scope stayed `complete`, phases 7-12, count 6)
- Three STATE.md Roadmap Evolution lines recorded, one per edited phase

## Task Commits

Tasks 1 and 2 produced no commit by the plan's own design — Task 3 commits all three files together as one concern, after the human's approval at the Task 2 checkpoint:

1. **Task 1: Amend REQ-hex-bore/REQ-keyway-bore, build the three ROADMAP diffs** - no commit (uncommitted working-tree edit + scratchpad diffs, per plan)
2. **Task 2: Human confirms the amendment wording** - no commit (checkpoint; human answered "approved")
3. **Task 3: Write the approved roadmap edits and commit** - `fddf9b8` (docs)

**Plan metadata:** commit `fddf9b8` also carries this plan's metadata (STATE.md); a separate metadata commit was not created because Task 3's commit already includes STATE.md by design (D-14: plain `git commit`, explicit file list, no `-A`).

## Files Created/Modified
- `.planning/REQUIREMENTS.md` - REQ-hex-bore and REQ-keyway-bore amended per D-01; footer line updated
- `.planning/ROADMAP.md` - Phase 8 SC2, Phase 9 SC2, Phase 12 SC1 amended via edit-phase's write step
- `.planning/STATE.md` - three Roadmap Evolution lines added (phases 8, 9, 12)

## Decisions Made
- The human approved all four proposed texts verbatim at the Task 2 checkpoint — no wording changes requested.
- ROADMAP.md was written only through edit-phase's `write_updated_phase` step (scoped Edit, milestone-scope check before/after with rollback on mismatch), never a direct whole-file write, per D-01's "roadmap edits through the phase tooling, never a direct write."
- Committed with a plain `git commit` and an explicit file list (D-14), not the gsd commit wrapper, because the wrapper's timeout kills the pre-commit `make verify` hook on a cold cache; `make verify` was run once first to warm the cache (290 tests passed, ~53s).

## Deviations from Plan

None - plan executed exactly as written.

## Human Checkpoint

**Task 2 (checkpoint:human-verify, gate=blocking):** Presented the applied REQUIREMENTS.md diff and the three proposed ROADMAP diffs (phases 8, 9, 12) built by Task 1. The human answered **"approved"** — all four proposed texts accepted verbatim, no wording changes.

## Issues Encountered

None. Prior-state verification at the start of this continuation confirmed: `.planning/REQUIREMENTS.md` modified and `.planning/ROADMAP.md` unmodified in the working tree, and all three `.diff` files present in the session scratchpad — matching the expected post-Task-2 state exactly.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `.planning/phases/08-hex-bore/08-02-PLAN.md` (the tracer plan) can now be planned/executed against the amended REQ-hex-bore text and ROADMAP Phase 8 SC2 — the phase verifier reads D-01's behaviour, not the superseded `bore_flat` 422.
- `REQ-hex-bore` is not yet marked complete in REQUIREMENTS.md/traceability: `requirements.ready-ids` reports 0/1 ready because sibling plans 08-02 and 08-03 also declare it and have no SUMMARY yet (shared-ID gate, #2388). It will flip complete once the last plan declaring it finishes.
- No blockers for Phase 9 or Phase 12 planning — their amended criteria are committed and consistent with D-01.

## Self-Check: PASSED

- `.planning/phases/08-hex-bore/08-01-SUMMARY.md` exists on disk
- Commit `fddf9b8` found in `git log --oneline --all`
- `.planning/REQUIREMENTS.md` contains "Phase 8 D-01" (3 occurrences)
- `.planning/ROADMAP.md` contains "08-CONTEXT.md D-01/D-02"
- `.planning/STATE.md` contains exactly 3 lines matching `^- Phase (8|9|12) edited`

---
*Phase: 08-hex-bore*
*Completed: 2026-09-26*
