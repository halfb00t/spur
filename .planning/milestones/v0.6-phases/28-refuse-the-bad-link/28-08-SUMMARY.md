---
phase: 28-refuse-the-bad-link
plan: 08
subsystem: docs
tags: [gap-closure, review-ledger, tech-debt, web-ui-doc]
status: complete
gap_closure: true
gap_ids: [G-28-1, G-28-2]

requires:
  - phase: 28-refuse-the-bad-link
    provides: D-19..D-23 (28-CONTEXT.md), the 28-06 and 28-07 fix commits, the deferred blank-box debt item
provides:
  - IN-02 fixed per D-23 - the web-ui.md Shape paragraph re-wrapped, no word changed
  - the tip-chamfer resolved item and its INDEX row lead with the retiring sha (6497c28)
  - 28-REVIEW-DISPOSITION.md closed - five rows, open 0, hand-triage stamp
affects: [28-verify-work, milestone-audit]

actuals:
  tokens: 1540          # chars/4 over the diff d1b38df..HEAD (docs 3359 + .planning 2789 chars)
  tasks: 3
  commits: 3
plan_head_before: d1b38df
plan_head_after: e33d2f6e44879f9cb45c81ecb2256eef4d62c53b

tech-stack:
  added: []
  patterns: []

key-files:
  created: []
  modified:
    - docs/architecture/web-ui.md
    - docs/tech_debt/resolved/2026-10-21-tip-chamfer-effective-gate-reads-the-request.md
    - docs/tech_debt/INDEX.md
    - .planning/phases/28-refuse-the-bad-link/28-REVIEW-DISPOSITION.md

key-decisions:
  - "Each fixed ledger cell leads with the short sha read from git log by exact subject (6497c28, 3224ec7, aede0fd, 2368718); WR-02 is deferred to the active blank-box item per D-20"
  - "The recorded: line keeps the gate's own stamp in the 9001695 comment shape so a gate re-run can tell hand triage from its own write"

requirements-completed: [REQ-info-findings-triaged]

coverage:
  - id: D1
    description: "IN-02 (D-23): the Shape paragraph of web-ui.md has no line over 90 characters and the re-wrap commit changes no word"
    requirement: "REQ-info-findings-triaged"
    verification:
      - kind: other
        ref: "Task 1 check (word lists of 2368718 and its parent equal; commit holds only docs/architecture/web-ui.md)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Tip-chamfer resolved item and INDEX Resolved row name sha 6497c28 (G-28-2)"
    requirement: "REQ-info-findings-triaged"
    verification:
      - kind: other
        ref: "Task 2 check (resolved item and INDEX row lead with the sha)"
        status: pass
    human_judgment: false
  - id: D3
    description: "All five Phase 28 review findings carry the disposition their D line records, in table and front matter, open 0"
    requirement: "REQ-info-findings-triaged"
    verification:
      - kind: other
        ref: "Task 2 check: Phase 28 ledger closed: 5 rows match D-19..D-23"
        status: pass
      - kind: other
        ref: "make verify (exit 0, 1348 passed); git diff --exit-code v0.5 -- tests/regression/ (empty); grep '| open |' over the ledger (prints nothing)"
        status: pass
    human_judgment: false

duration: 8min
completed: 2026-10-21
---

# Phase 28 Plan 08: Close the review ledger Summary

**Phase 28's own review ledger closed from the human's D-19..D-23 choices: four findings fixed with the sha of the commit whose subject fixed them, one deferred to a debt item that exists, `open: 0`, and the gate green.**

## Performance

- **Duration:** about 8 min (the `make verify` run took 3 min 18 s of it)
- **Started:** 2026-10-21T17:56Z
- **Completed:** 2026-10-21T18:05Z
- **Tasks:** 3
- **Files modified:** 4

## Accomplishments

- IN-02 (D-23 `fix`): re-wrapped lines 34-35 of web-ui.md's `## Shape` paragraph (161 and 145 characters) to at most 88; the paragraph's longest line is now 89. Line breaks only.
- G-28-2: the resolved tip-chamfer item's `Resolved in:` line and its INDEX Resolved cell now lead with `6497c28`.
- G-28-1: five rows written in both the table and the front matter, `open: 0`, `recorded:` in the 9001695 shape.

### The five rows as written

| Finding | Disposition | Source |
|---------|-------------|--------|
| WR-01 | fixed | `3224ec7` fix(28): a selector pick that writes a field ends its rejected link token (28-REVIEW WR-01) |
| WR-02 | deferred | `docs/tech_debt/active/2026-10-21-an-accepted-link-token-builds-under-a-blank-box.md` (D-20) |
| WR-03 | fixed | `6497c28` fix(28): print no tip chamfer when none is cut -- log L45; L45; G-28-2; resolved item path |
| IN-01 | fixed | `aede0fd` refactor(28): assign the mate box once in readHash, its pin tightened through the read-back (28-REVIEW IN-01) |
| IN-02 | fixed | `2368718` docs(28): re-wrap web-ui.md's Shape paragraph (28-REVIEW IN-02) |

## Task Commits

1. **Task 1: IN-02 per D-23 (tracer)** - `2368718` (docs); its ledger row was left uncommitted for Task 2's single ledger commit, as planned
2. **Task 2: tip-chamfer sha, then the ledger** - `6873cb8` (docs, resolved item and INDEX) and `e33d2f6` (docs, the ledger)
3. **Task 3: the phase gate** - no commit (gate only)

**Plan metadata:** the commit that follows this file (docs: complete plan)

## Gate results (Task 3)

- `make verify` -> `======================= 1348 passed in 198.06s (0:03:18) =======================`, `exit 0`
- Coverage line: `Required test coverage of 96.0% reached. Total coverage: 97.99%`
- `git diff --exit-code v0.5 -- tests/regression/` -> empty (exit 0)
- `grep -n '| open |'` over 28-REVIEW-DISPOSITION.md -> prints nothing
- Task 1 check: `D-23 fix: IN-02 carried to its ledger row`; Task 2 check: `Phase 28 ledger closed: 5 rows match D-19..D-23`
- `git status --short`: only `.planning/state.json` and `.planning/milestone.lock`, as allowed

## Gap-closure commits (`d3566ec..HEAD`, at the ledger commit)

```
e33d2f6 docs(28): disposition Phase 28's own review findings (G-28-1)
6873cb8 docs(28): name the commit that retired the tip-chamfer item
2368718 docs(28): re-wrap web-ui.md's Shape paragraph (28-REVIEW IN-02)
d1b38df docs(28-07): complete the app.js review-findings plan
082cc64 docs(28-07): summarize the review-findings fixes in app.js
aede0fd refactor(28): assign the mate box once in readHash, its pin tightened through the read-back (28-REVIEW IN-01)
3224ec7 fix(28): a selector pick that writes a field ends its rejected link token (28-REVIEW WR-01)
947e051 docs(28-06): complete the D-21 tip-chamfer plan
600657b docs(28-06): summarize the D-21 tip-chamfer fix plan
6497c28 fix(28): print no tip chamfer when none is cut -- log L45
268fe72 docs(28-05): complete the review-findings disposition plan
5235858 docs(28-05): summarize the human's dispositions of the Phase 28 review findings
eb78bb1 docs(28): file the Phase 28 review findings deferred at the checkpoint
ad28848 docs(28): record the human's dispositions of the Phase 28 review findings (D-19..D-23)
be72b4e fix(28): revise gap-closure plans 28-05..28-07 on checker feedback
4ab503c docs(28): plan gap closure for UAT G-28-1 and G-28-2
```

## Files Created/Modified

- `docs/architecture/web-ui.md` - Shape paragraph re-wrapped
- `docs/tech_debt/resolved/2026-10-21-tip-chamfer-effective-gate-reads-the-request.md` - `Resolved in:` leads with `6497c28`
- `docs/tech_debt/INDEX.md` - Resolved cell is `` `6497c28` — see the file's own `Resolved in:` field ``
- `.planning/phases/28-refuse-the-bad-link/28-REVIEW-DISPOSITION.md` - five rows, `open: 0`, hand-triage stamp

## Decisions Made

- Shas read from `git log` by exact subject, never predicted; the ledger was written after every commit it cites.
- The plan's `plan-head` ledger file for this plan was not created before the first commit; `plan_head_before` is d1b38df (the HEAD before the first task commit), and `git rev-list --count d1b38df..HEAD` was 3 at the ledger commit.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None. Filed no tech-debt or idea item; the one deferred finding (WR-02) was already filed in eb78bb1.

## Known Stubs

None.

## Threat Flags

None.

## Next Phase Readiness

UAT G-28-1 and G-28-2 are ready for re-verification. Phase 28 has no open review row.

## Self-Check: PASSED

- FOUND: 2368718, 6873cb8, e33d2f6 (ancestors of HEAD)
- FOUND: all four modified files on disk; the ledger has no `| open |` row

---
*Phase: 28-refuse-the-bad-link*
*Completed: 2026-10-21*
