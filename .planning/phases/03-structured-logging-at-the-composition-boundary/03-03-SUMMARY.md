---
phase: 03-structured-logging-at-the-composition-boundary
plan: 03
subsystem: observability
tags: [decision-log, documentation, tech-debt-lifecycle, structured-logging]

# Dependency graph
requires:
  - phase: 03-structured-logging-at-the-composition-boundary
    provides: "Plans 03-01 and 03-02's records.py module and its five per-event helpers, wired into app.py/pool.py/cli.py and proven by tests"
provides:
  - "L20 in docs/architecture/decision_log.md -- the locked logging decision, dated, with D-01 through D-04, D-06 and D-14's rationale, including the two-call-site correction"
  - "Four corrected §Logging sections (CODING_VALUES.md, http-api.md, solid-model/errors_and_logging.md, gear-maths/errors_and_logging.md's pointer sentence) that describe the shipped logger instead of its absence"
  - "A SPUR_LOG_LEVEL row in README.md's environment-variable table"
  - "docs/architecture/cli.md recording that spur serve configures the logger and spur info/export deliberately do not"
  - "docs/tech_debt/active/2026-09-21-no-structured-logging.md retired: Status: resolved, Resolved in: 21b8fe4, git mv'd into resolved/, INDEX.md row moved"
affects: [any later phase reading L20 as the settled logging decision, any agent tempted to remove the app.py lifespan() configure() call as redundant]

# Actuals (#2632)
actuals:
  tokens: 4458
  tasks: 2
  commits: 2

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Decision-log entries recording a research-falsified assumption state the falsified premise and the corrected design explicitly, not just the final design, so a later reader cannot mistake the correction for defensive belt-and-braces"

key-files:
  created: []
  modified:
    - docs/architecture/decision_log.md
    - docs/CODING_VALUES.md
    - docs/architecture/http-api.md
    - docs/architecture/solid-model/errors_and_logging.md
    - docs/architecture/gear-maths/errors_and_logging.md
    - docs/architecture/cli.md
    - README.md
    - docs/tech_debt/INDEX.md
    - docs/tech_debt/resolved/2026-09-21-no-structured-logging.md

key-decisions:
  - "Task 1's checkpoint:decision resolved as option A: append L20 recording D-01 through D-04, D-06 and D-14 with their rationale in full, including the two-call-site correction, rather than the shorter pointer-to-CONTEXT.md variant (option B) or a scope adjustment (option C). The human's stated reason: the single most likely future regression is someone reading cli.cmd_serve's configure() call, finding lifespan()'s, concluding it is redundant, and deleting it -- silently blinding every worker above the first for any SPUR_WORKERS>1 deployment. A decision-log entry that says why there are two is the cheapest guard against that."
  - "Resolved-in sha for the retired debt file is 21b8fe4 (Plan 03-02's worker.replaced commit, the last code-changing commit of this phase), not this plan's own documentation commit -- a file cannot carry its own commit's sha (flagged assumption 1)."

requirements-completed: [REQ-structured-logging]

coverage:
  - id: D1
    description: "L20 is appended to the decision log, dated, recording the library/format/stream/configuration-points/default-level choice with its rationale, including the two-call-site correction -- and nothing earlier in the file is edited"
    requirement: "REQ-structured-logging"
    verification:
      - kind: other
        ref: "grep -nE '^## L20 ' docs/architecture/decision_log.md"
        status: pass
      - kind: other
        ref: "git diff --stat HEAD~1 -- docs/architecture/decision_log.md (68 insertions, 0 deletions)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Every documentation section that said this project has no structured logging now says what it has, except gear-maths's deliberate boundary"
    requirement: "REQ-structured-logging"
    verification:
      - kind: other
        ref: "grep -n L20 docs/architecture/solid-model/errors_and_logging.md"
        status: pass
      - kind: other
        ref: "grep -nE 'export\\.served|build\\.failed|queue\\.refused' docs/architecture/http-api.md"
        status: pass
    human_judgment: false
  - id: D3
    description: "The no-structured-logging debt file is retired per CLAUDE.md's lifecycle: Status: resolved, a resolvable Resolved in sha, git mv'd (not deleted+recreated) into resolved/, INDEX.md row moved -- in the same commit as the documentation fix"
    requirement: "REQ-structured-logging"
    verification:
      - kind: other
        ref: "git status --porcelain docs/tech_debt/ (rename, not delete+add)"
        status: pass
      - kind: other
        ref: "git cat-file -e 21b8fe4"
        status: pass
    human_judgment: false
  - id: D4
    description: "make verify passes after every change in this plan"
    requirement: "REQ-structured-logging"
    verification:
      - kind: other
        ref: "make verify (96 passed)"
        status: pass
    human_judgment: false

duration: 20min
completed: 2026-09-24
status: complete
---

# Phase 3 Plan 3: Decision Recorded, Documentation True, Debt Retired Summary

**`L20` locks the structured-logging decision (including why there are two idempotent `configure()` call sites, not one); four `§Logging` sections now describe what ships instead of its absence; `docs/tech_debt/active/2026-09-21-no-structured-logging.md` is `Status: resolved`, `git mv`'d into `resolved/`, in the same commit as the documentation change.**

## Performance

- **Duration:** ~20 min (continuation after a resolved decision checkpoint)
- **Completed:** 2026-09-24T10:21:51Z
- **Tasks:** 3 (Task 1 a decision checkpoint with no commit; Tasks 2 and 3 executed as `type="auto"`)
- **Files modified:** 9

## Accomplishments
- `L20` is on the record in `docs/architecture/decision_log.md`: stdlib `logging` with a project-owned JSON formatter (D-01/D-03, `structlog`/logfmt rejected and why), one stderr handler joined by uvicorn's own records via `log_config=None` (D-02/D-04), the two idempotent `configure()` call sites and the falsified single-call-site assumption that made the second one necessary (D-05, corrected), the parent-emits/worker-silent split and its accepted cost (D-06), and the `SPUR_LOG_LEVEL` knob with its INFO default (D-14) — appended only, nothing earlier in the 313-line file touched.
- `docs/CODING_VALUES.md`, `docs/architecture/http-api.md` and `docs/architecture/solid-model/errors_and_logging.md`'s `§Logging` sections now describe the shipped logger — the five event names, their levels and fields, and (for the solid model) the worker's silence as a decision rather than a gap. `docs/architecture/gear-maths/errors_and_logging.md` keeps its "none, deliberately" substance; only its pointer sentence changed, per flagged assumption 2.
- `README.md` gains a `SPUR_LOG_LEVEL` row and a sentence on where the JSON lines go; `docs/architecture/cli.md` now states that `spur serve` configures the logger and `spur info`/`spur export` deliberately do not, writing down the stdout/stderr convention D-04 relies on.
- `docs/tech_debt/active/2026-09-21-no-structured-logging.md` is retired: `Status: resolved`, `Resolved in: 21b8fe4` (Plan 03-02's `worker.replaced` commit — a file cannot carry its own commit's sha), a `## Resolution` section added, `git mv`'d into `resolved/` (git reports a rename, not a delete-plus-add), and its `docs/tech_debt/INDEX.md` row moved from Active to Resolved — all in the same commit as the documentation fix, per CLAUDE.md.
- `REQ-structured-logging` marked complete in `.planning/REQUIREMENTS.md` (the shared-ID gate held it pending until this, the last of the three plans declaring it, finished).

## Task Commits

1. **Task 1: Decision — append `L20` (checkpoint)** — resolved by the human as option A (append in full, including the two-call-site correction); no commit, no code change.
2. **Task 2: `L20` — appended, dated, never edited in place** - `c8b7fc8` (docs)
3. **Task 3: Make the documentation true, retire the debt in the same commit** - `013997a` (docs)

**Plan metadata:** commit to follow (docs: complete plan)

## Files Created/Modified
- `docs/architecture/decision_log.md` - Appends `L20` (68 lines added, 0 deleted)
- `docs/CODING_VALUES.md` - `§Logging` rewritten to describe the shipped logger and harden the `print()`-in-`src/` prohibition
- `docs/architecture/http-api.md` - `§Logging` rewritten with a table of the four per-request events, their levels and fields, plus `worker.replaced` and the uvicorn-record note
- `docs/architecture/solid-model/errors_and_logging.md` - `§Logging` rewritten: silence by decision (`L20`, D-06), the accepted cost named
- `docs/architecture/gear-maths/errors_and_logging.md` - Only the pointer sentence changed; substance ("none, deliberately") unchanged
- `docs/architecture/cli.md` - New `§Logging` section: `spur serve` configures, `spur info`/`spur export` do not
- `README.md` - `SPUR_LOG_LEVEL` row added to the environment-variable table, plus a sentence on `docker logs`/`jq`
- `docs/tech_debt/INDEX.md` - Structured-logging row moved from Active to Resolved
- `docs/tech_debt/resolved/2026-09-21-no-structured-logging.md` - `git mv`'d from `active/`; `Status: resolved`, `Resolved in: 21b8fe4`, `## Resolution` section added

## Decisions Made
See `key-decisions` in frontmatter: the human selected option A for the `L20` checkpoint (full text, including the two-call-site correction), and the debt file's `Resolved in:` sha names Plan 03-02's `worker.replaced` commit rather than this plan's own commit.

## Deviations from Plan

None - plan executed exactly as written. The checkpoint's resolved answer (option A, with the two-call-site correction explicitly included) matched the plan's own recommendation.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Phase 3 is complete: all three plans (03-01, 03-02, 03-03) have landed, `REQ-structured-logging` is marked complete, and `make verify` passes (96 tests). `docs/tech_debt/active/` now holds five items (the structured-logging debt retired this plan); `docs/tech_debt/resolved/` holds two. Ready for `/gsd-verify-work` on Phase 3, then `/gsd-plan-phase 4` (Typed Derived-Dimensions Contract).

---
*Phase: 03-structured-logging-at-the-composition-boundary*
*Completed: 2026-09-24*

## Self-Check: PASSED

- FOUND: docs/architecture/decision_log.md (`## L20` heading present, diffstat 68 insertions / 0 deletions against the pre-plan HEAD)
- FOUND: docs/tech_debt/resolved/2026-09-21-no-structured-logging.md (`Status: resolved`, `Resolved in: 21b8fe4`)
- CONFIRMED MISSING: docs/tech_debt/active/2026-09-21-no-structured-logging.md
- FOUND commits: c8b7fc8, 013997a
- `git status --porcelain docs/tech_debt/` at commit time showed a rename (`R`), not a delete-plus-add
- `git cat-file -e 21b8fe4` resolves
- Re-ran `make verify`: exits 0 (96 passed)
- Re-ran all Task 2 and Task 3 automated `<verify>` commands individually: all pass
