---
phase: 05-ci-observed-green
plan: 05
subsystem: ci-merge-gate
tags: [documentation, decision-log, requirements, state-tracking]

# Dependency graph
requires:
  - phase: 05-01
    provides: "The commit-msg hook and squash-message setting (D-02, D-03) this plan cites in HOW_TO_DEVELOP.md section 0 and the decision-log-consistent L22 citations"
  - phase: 05-02
    provides: "make pr.land, named throughout the corrected docs as the merge path (D-05)"
  - phase: 05-03
    provides: "The ruleset on main and L22, cited by name in every corrected CI note (D-12)"
  - phase: 05-04
    provides: "Python 3.12 only and L23, which every corrected document now cites instead of L01's 3.10-3.12 floor (D-09)"
provides:
  - "Thirteen files corrected to say Python 3.12 only, citing L23: README.md, AGENTS.md,
    docs/CODING_VALUES.md, docs/HOW_TO_DEVELOP.md, docs/architecture/overview.md,
    docs/architecture/packaging.md, .planning/codebase/{STACK,CONVENTIONS,INTEGRATIONS,CONCERNS}.md,
    .planning/REQUIREMENTS.md, .planning/PROJECT.md, .planning/STATE.md"
  - "HOW_TO_DEVELOP.md section 0 names the three new guarantees (commit-msg hook, ruleset
    on main, make pr.land), in Russian"
  - "CONCERNS.md and INTEGRATIONS.md's 'never executed' claims replaced with the observed
    evidence: main push run 35963114939 and PR #3 head run 36088409707 (D-07)"
  - "STATE.md's 'CI workflow unverified' blocker retired; the resolved-items note extended
    with both run URLs"
affects: []

# Actuals (#2632)
actuals:
  tokens: 4716
  tasks: 3
  commits: 3
plan_head_before: 0b2e1ca

# Tech tracking
tech-stack:
  added: []
  patterns: []

key-files:
  created: []
  modified:
    - README.md
    - AGENTS.md
    - docs/CODING_VALUES.md
    - docs/HOW_TO_DEVELOP.md
    - docs/architecture/overview.md
    - docs/architecture/packaging.md
    - .planning/codebase/STACK.md
    - .planning/codebase/CONVENTIONS.md
    - .planning/codebase/INTEGRATIONS.md
    - .planning/codebase/CONCERNS.md
    - .planning/REQUIREMENTS.md
    - .planning/PROJECT.md
    - .planning/STATE.md

key-decisions:
  - "The STATE.md blocker was removed with one scoped edit inside Blockers/Concerns
    (deleting the four-line bullet, extending the existing italic resolved-items note),
    not with `gsd_run query state.resolve-blocker` -- that command filters single `- `
    lines and would have orphaned the bullet's three continuation lines (plan's flagged
    assumption 3)."
  - "REQ-ci-verified's checkbox and traceability row were left untouched -- the
    execute-phase/phase-completion tooling flips those, as it did for
    REQ-typed-derived-dimensions in Phase 4 (plan's flagged assumption 4)."
  - "PROJECT.md's Key Decisions table (the L01 row) was left byte-identical -- it mirrors
    the append-only decision log, which is history, not a live claim to correct (plan's
    flagged assumption 2)."

patterns-established: []

requirements-completed: [REQ-ci-verified]

coverage:
  - id: D1
    description: "The five documents a contributor or agent reads first (README, AGENTS.md,
      CODING_VALUES.md, HOW_TO_DEVELOP.md section 0, overview.md) say Python 3.12 only,
      each citing L23 where it previously cited L01's 3.10-3.12 floor; section 0 names the
      commit-msg hook, the ruleset on main and make pr.land, in Russian."
    requirement: "REQ-ci-verified"
    verification:
      - kind: other
        ref: "Task 1 <verify>: grep -q 'Python 3.12'/'L23' across the five files, section 0
          extracted and grepped for 'make pr.land'/'ruleset'/'commit-msg', residual grep for
          every 3.10 phrasing across the five files (exit 1 -- none found)"
        status: pass
      - kind: unit
        ref: "make verify (178 tests) after the task commit"
        status: pass
    human_judgment: false
  - id: D2
    description: "The architecture docs and codebase map (packaging.md plus the four
      .planning/codebase/ files) say 3.12 only; the 'never executed' claim is replaced with
      the observed evidence -- main push run 35963114939 and PR #3 head run 36088409707 --
      and both CI notes name the ruleset on main and make pr.land."
    requirement: "REQ-ci-verified"
    verification:
      - kind: other
        ref: "Task 2 <verify>: grep for both run ids plus 'ruleset'/'make pr.land' in
          CONCERNS.md/INTEGRATIONS.md; residual grep for 'never executed', every 3.10
          phrasing and py310 across the five files (exit 1 -- none found)"
        status: pass
      - kind: unit
        ref: "make verify (178 tests) after the task commit"
        status: pass
    human_judgment: false
  - id: D3
    description: "REQ-ci-verified reads 'on the supported Python version (3.12, L23)';
      PROJECT.md's Runtime constraint says 3.12 only citing L23; the STATE.md blocker is
      gone with the resolved-items note citing both run URLs; a repository-wide residue
      grep for stale 3.10/never-executed/free-plan claims outside history prints nothing."
    requirement: "REQ-ci-verified"
    verification:
      - kind: other
        ref: "Task 3 <verify>: grep for the corrected phrases in REQUIREMENTS.md/PROJECT.md,
          grep for both run URLs and absence of the blocker bullet in STATE.md, the full
          phase-wide git grep residue command re-run after all three task commits (prints
          nothing but the exempted L01 history row)"
        status: pass
      - kind: unit
        ref: "make verify (178 tests) after the task commit"
        status: pass
    human_judgment: false

# Metrics
duration: ~11min (reconstructed; see Issues Encountered)
completed: 2026-09-25
status: complete
---

# Phase 5 Plan 5: The Record Says What the Code Does Summary

**Thirteen files corrected from "Python 3.10-3.12" and "CI workflow... never executed" to
Python 3.12 only (L23) and the two observed green runs (35963114939, 36088409707), retiring
the STATE.md CI-unverified blocker and closing ROADMAP Phase 5's last two success criteria.**

## Performance

- **Duration:** ~11 min (reconstructed from STATE.md's prior session timestamp,
  07:07:30Z, to the third task commit's timestamp, 07:18:52Z-equivalent; `PLAN_START_TIME`
  was not captured via a standalone `date -u` call at the very start of this session, the
  same gap every other Phase 5 plan's summary recorded)
- **Tasks:** 3 completed
- **Files modified:** 13 (0 created)

## Accomplishments

- README, `AGENTS.md`, `docs/CODING_VALUES.md`, `docs/architecture/overview.md` and
  `docs/HOW_TO_DEVELOP.md` section 0 all say Python 3.12 only, citing `L23` where they
  previously cited `L01`'s 3.10-3.12 floor; `CLAUDE.md` stays a symlink to `AGENTS.md`.
- `docs/HOW_TO_DEVELOP.md` section 0 gains one bullet, in Russian, naming the three new
  guarantees: the `commit-msg` hook refusing GitHub Actions skip tokens, the ruleset on
  `main` (D-12), and `make pr.land PR=N` as the path into `main` (`L22`).
- `docs/architecture/packaging.md` and the four `.planning/codebase/` files
  (`STACK.md`, `CONVENTIONS.md`, `INTEGRATIONS.md`, `CONCERNS.md`) say 3.12 only; ruff's
  target, the CI matrix wording and the Makefile's interpreter description all agree.
- `CONCERNS.md`'s and `INTEGRATIONS.md`'s stale "the workflow has never executed" claims
  are replaced with the evidence: main push run `35963114939` (`59f02c3`, all four jobs
  green) and PR #3 head run `36088409707` (`2c4b544`, tree-identical to `bfc9110`), naming
  the ruleset on `main` and `make pr.land` as the merge gate (D-07, D-12).
- `REQUIREMENTS.md`'s `REQ-ci-verified` reads "on the supported Python version (3.12,
  L23)"; `PROJECT.md`'s Runtime constraint says Python 3.12 only, citing `L01`, `L12`,
  `L23`; both left their checkbox/table structure untouched.
- `STATE.md`'s "CI workflow unverified" blocker bullet is gone from Blockers/Concerns; the
  existing italic resolved-items note now opens with "Resolved in Phase 5" citing both run
  URLs and `L22`'s merge gate, with the other three blocker bullets byte-identical.
- The phase-wide residue check (a repository-wide `git grep` across every tracked file
  outside history) printed nothing but the one expected, exempted line: `PROJECT.md`'s
  `L01` Key Decisions table row, which mirrors the append-only decision log and is history,
  not a live claim.

## Task Commits

Each task was committed atomically:

1. **Task 1: What a contributor or agent reads first says Python 3.12 only, and section 0
   names the new guarantees (D-09)** - `5bf3363` (docs)
2. **Task 2: The architecture docs and the codebase map say 3.12, and the "never executed"
   note is retired with run URLs (D-07, D-09)** - `643ba1b` (docs)
3. **Task 3: REQ-ci-verified's wording, PROJECT.md's runtime, and the STATE.md blocker
   retired with run URLs; then the phase-wide residue check (D-07, D-09, D-10)** -
   `85b29cb` (docs)

**Plan metadata:** committed separately by this workflow's final step.

## Files Created/Modified

- `README.md` - "Without Docker" version line, `make venv` comment, the `make verify`
  CI sentence, the bold wheels sentence
- `AGENTS.md` - Stack line, one line, `L23` cited
- `docs/CODING_VALUES.md` - Stack bullet, Project-specific bullet
- `docs/HOW_TO_DEVELOP.md` - section 0's CI bullet plus one new bullet naming the three
  merge-gate guarantees
- `docs/architecture/overview.md` - Core/API bullet
- `docs/architecture/packaging.md` - the `make verify` CI sentence, the `make venv`
  platform note
- `.planning/codebase/STACK.md` - primary-language bullet, Runtime line, ruff config,
  Development platform requirement
- `.planning/codebase/CONVENTIONS.md` - ruff target, mypy version note
- `.planning/codebase/INTEGRATIONS.md` - workflow bullet, Job 1 description, one new line
  citing the observed run and the merge gate
- `.planning/codebase/CONCERNS.md` - Current-coverage bullet, Python note, CI note
  rewritten with both run URLs
- `.planning/REQUIREMENTS.md` - `REQ-ci-verified`'s main bullet wording
- `.planning/PROJECT.md` - Runtime constraint
- `.planning/STATE.md` - Blockers/Concerns: blocker bullet removed, resolved note extended

## Decisions Made

See `key-decisions` in the frontmatter: the STATE.md blocker retired with one scoped
section edit rather than `state.resolve-blocker` (would orphan the bullet's continuation
lines); REQ-ci-verified's checkbox/traceability row left for phase-completion tooling;
PROJECT.md's Key Decisions table left byte-identical (history, not a live claim).

## Deviations from Plan

None - plan executed exactly as written. All three tasks' automated `<verify>` blocks
passed on the first run; no fix pass was needed.

## Issues Encountered

- `PLAN_START_TIME` was not captured via an explicit `date -u` call at the very start of
  this session -- the same gap every other Phase 5 plan's summary recorded. Duration above
  is reconstructed from STATE.md's prior session timestamp (07:07:30Z) to the third task
  commit's own git timestamp (07:18:52Z), not a precisely measured figure. All three task
  commit timestamps (`5bf3363`, `643ba1b`, `85b29cb`) are exact and git-verifiable
  regardless.

## User Setup Required

None - no external service configuration required. This plan edited prose only; no
network calls or credentials were needed.

## Next Phase Readiness

- All five reframed ROADMAP Phase 5 success criteria are now met across Plans 05-01
  through 05-05: the skip-token hook and squash-message setting (SC-1), `make pr.land`
  (SC-2), Python 3.12 only (SC-3), the STATE.md blocker retired (SC-4), and the ruleset on
  `main` (SC-5, D-12).
- `make verify` is green (178 tests) after every one of this plan's three commits.
- This phase's own ship-and-land sequence is documented in this plan's `<output>` section,
  not executed as part of plan execution: `/gsd-ship 5`, then hand-committing
  `.planning/STATE.md` as the ship note (the hook refuses `gsd-ship`'s own `[ci skip]`
  commit, per D-04), a PR-body check for literal skip-token mentions, `make pr.land PR=M`
  as the first live exercise of both the ruleset and `pr.land` together, recording the
  resulting run URL and its poll latency on the next STATE.md touch, and only then
  `/gsd-complete-milestone` (v0.1 ends with this phase, landed as its own PR per D-12 --
  no bypass actors).
- No blockers for the phase's ship/land sequence.

## Self-Check: PASSED

All 13 key-files confirmed present on disk with `[ -f ]`. All three task commits
(`5bf3363`, `643ba1b`, `85b29cb`) confirmed in `git log --oneline --all`. All plan-level
`<verification>` items re-run and passing: the residue check across every current document
printed nothing but the one exempted `PROJECT.md` L01 history row; both CI notes cite runs
`35963114939` and `36088409707` and name the ruleset on `main`; `HOW_TO_DEVELOP.md`
section 0 names the hook, the ruleset and `make pr.land`; the STATE.md blocker is retired
with both URLs; `make verify` exits 0 (178 tests passed) after every task commit.

---
*Phase: 05-ci-observed-green*
*Completed: 2026-09-25*
