---
phase: 25-gate-bar-re-set-venv-probe-ledger-close
plan: 05
subsystem: docs
tags: [readme, pi5, ai-skills, reverify, ideas-ledger]

requires:
  - phase: 25
    provides: "25-04's L43 and the swept README / HOW_TO_DEVELOP text this plan edits on top of"
provides:
  - "README Docker paragraph: built for, not measured on, amd64/arm64; names the 12-CPU Apple M2 Max and 18-CPU Apple M5 Max"
  - ".ai_skills/reverify-phase/SKILL.md (31 lines), reachable through .claude/skills"
  - "docs/HOW_TO_DEVELOP.md section 6 pointer to the skill"
  - "Two ideas retired (Pi 5 claim, reverify recipe) with their INDEX rows moved"
affects: [phase-25-close, ship]

actuals:
  tokens: 4260       # chars/4 over `git diff 12a97a0 HEAD` (17040 chars, kept logs included)
  tasks: 2
  commits: 2         # measured: git rev-list --count 12a97a0..HEAD at SUMMARY write (the metadata commit comes after)
plan_head_before: 12a97a046acd35260b25d39d3dd457912a7a35b3
plan_head_after: ac129dc236e33beb39a7939e23639766aec3963f

tech-stack:
  added: []
  patterns:
    - "A repeated process loop becomes a project skill whose idea retires with the count read from the record"

key-files:
  created:
    - ".ai_skills/reverify-phase/SKILL.md"
    - "docs/ideas/retired/2026-09-22-measure-or-soften-the-pi5-claim.md (git mv)"
    - "docs/ideas/retired/2026-09-28-reverify-after-post-verification-fixes.md (git mv)"
    - ".planning/phases/25-gate-bar-re-set-venv-probe-ledger-close/investigation/25-05-readme.log"
    - ".planning/phases/25-gate-bar-re-set-venv-probe-ledger-close/investigation/25-05-skill-dry-read.log"
    - ".planning/phases/25-gate-bar-re-set-venv-probe-ledger-close/investigation/25-05-verify.log"
  modified:
    - "README.md"
    - "docs/HOW_TO_DEVELOP.md"
    - "docs/ideas/INDEX.md"

key-decisions:
  - "The Pi 5 stays only as a build target; no Pi figure and no 'works' claim without a measurement"
  - "The skill leads with the #4682 route (/gsd-execute-phase N) and keeps the hand-dispatched verifier as the fallback; it never hand-writes covered_digest"

requirements-completed: [REQ-pi5-claim-softened, REQ-reverify-recipe]

coverage:
  - id: D1
    description: "README states the hardware behind its numbers and makes no Raspberry Pi 5 claim"
    requirement: "REQ-pi5-claim-softened"
    verification:
      - kind: unit
        ref: "tests/test_cli.py::test_readme_export_examples_run and the root_form_d test in tests/test_api.py (make test exit 0, investigation/25-05-readme.log) plus the Task 1 verify script"
        status: pass
    human_judgment: false
  - id: D2
    description: "reverify-phase skill exists, resolves through .claude/skills, #4682 route first, no hand-written digest"
    requirement: "REQ-reverify-recipe"
    verification:
      - kind: other
        ref: "Task 2 verify script and investigation/25-05-skill-dry-read.log"
        status: pass
    human_judgment: true
    rationale: "The skill fires only when a review finds something; its behaviour is proved by a dry read (D-18), not a test, and whether its steps are right is a reader's judgment."
  - id: D3
    description: "The phase ends on a green make verify"
    verification:
      - kind: integration
        ref: "make verify (investigation/25-05-verify.log)"
        status: pass
    human_judgment: false

duration: 45min
completed: 2026-10-14
status: complete
---

# Phase 25 Plan 05: README hardware, no Pi 5 claim, and the reverify-phase skill Summary

**The README says the image is built for, not measured on, amd64/arm64 and names the two dev hosts behind every number; the five-hit reverify loop is now `.ai_skills/reverify-phase`, and both ideas are retired.**

## Performance

- **Tasks:** 2
- **Files modified:** 9 (7 outside `.planning/`, counting the two idea renames and the new skill)
- **`make verify` wall:** 185 s

## Accomplishments

- README Docker paragraph as written: "It builds for `linux/amd64` and `linux/arm64`, so Apple silicon, Graviton and a Raspberry Pi 5 are the targets, built for and not measured on: every performance number in this README and in `bench/RESULTS.md` was read on the dev hosts named there, a 12-CPU Apple M2 Max and an 18-CPU Apple M5 Max, and none on a Raspberry Pi or another arm64 board:" -- the `docker buildx` block, the 29.42 s line and the L43 line are untouched.
- `.ai_skills/reverify-phase/SKILL.md`, 31 lines: `verification.status` -> `/gsd-execute-phase N` (#4682) -> fallback `gsd-verifier` with the delta, told not to commit, report committed by hand -> `/gsd-ship N`; says never to hand-write `covered_digest`.
- `docs/HOW_TO_DEVELOP.md` section 6 carries one sentence after the ship-note paragraph naming the skill.
- Dry read: `resolve-model gsd-verifier` printed `"model": "sonnet"`; `verification.status` on Phase 24 printed `"status": "stale"` with `next_command: /gsd-execute-phase 24` (Phase 24's covered files have moved since its report; that is the state the skill's step 1 reads, not a fault of this plan).
- The reverify idea retired with the count read from the record: five hits across four phases (Phase 9 twice, 17 at `0f1209f`, 23, 24).

## Task Commits

1. **Task 1: README hardware sentence, Pi 5 idea retired** - `92953bb` (docs)
2. **Task 2: reverify-phase skill, section 6 pointer, reverify idea retired, last make verify** - `ac129dc` (docs)

**Plan metadata:** the commit that carries this file (docs: complete plan)

## make verify

`======================= 1317 passed in 184.95s (0:03:04) =======================`, then `make verify exit 0`; coverage `TOTAL 1358 22 386 13 97.99%` (`Required test coverage of 96.0% reached`). Run from the main checkout, log kept at `investigation/25-05-verify.log`.

## Files Created/Modified

- `README.md` - hardware sentence (4 lines replace 1)
- `.ai_skills/reverify-phase/SKILL.md` - new project skill
- `docs/HOW_TO_DEVELOP.md` - section 6 pointer sentence
- `docs/ideas/INDEX.md` - two rows moved from Open to Retired
- `docs/ideas/retired/2026-09-22-measure-or-soften-the-pi5-claim.md`, `docs/ideas/retired/2026-09-28-reverify-after-post-verification-fixes.md` - `git mv` from `docs/ideas/`, each with `Status: retired`, `Retired in:` and `## Outcome`

## Decisions Made

None - followed plan as specified.

## Deviations from Plan

None to the work. One verify line did not return clean:

The second `<automated>` of Task 2 (`git diff --exit-code -- tests/regression/... && test -z "$(git status --porcelain --untracked-files=no -- . ':!.planning/STATE.md' ':!.planning/state.json')"`) exited 1. Output of `git status --porcelain --untracked-files=no`:

```
 M .planning/milestone.lock
 M .planning/state.json
```

Reason: `.planning/milestone.lock` is rewritten by the GSD SDK on every run (pid and timestamp) and the script's exclusions name only STATE.md and state.json. The regression fixtures diff was empty (`git diff --exit-code` passed); no source or docs file is left modified. The lock is committed with the metadata commit.

## Issues Encountered

None.

## Debt and ideas

No debt or idea item was filed. Two ideas were moved, not filed: `docs/ideas/2026-09-22-measure-or-soften-the-pi5-claim.md` -> `docs/ideas/retired/2026-09-22-measure-or-soften-the-pi5-claim.md`, and `docs/ideas/2026-09-28-reverify-after-post-verification-fixes.md` -> `docs/ideas/retired/2026-09-28-reverify-after-post-verification-fixes.md`, each with its INDEX row moved in the same commit. The four-versus-five heavy-files drift (README:315, HOW_TO_DEVELOP:25-27) was left alone per the plan's prohibition.

## Known Stubs

None.

## Next Phase Readiness

Plan 25-05 is the last plan of Phase 25; the phase is ready for verification and ship.

## Self-Check: PASSED

- FOUND: `.ai_skills/reverify-phase/SKILL.md`, both retired idea files, the three `25-05-*.log` files
- FOUND commits: `92953bb`, `ac129dc`

---
*Phase: 25-gate-bar-re-set-venv-probe-ledger-close*
*Completed: 2026-10-14*
