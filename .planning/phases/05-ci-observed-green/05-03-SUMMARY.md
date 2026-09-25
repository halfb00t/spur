---
phase: 05-ci-observed-green
plan: 03
subsystem: ci-merge-gate
tags: [github-rulesets, gh-api, branch-protection, decision-log, documentation]

# Dependency graph
requires:
  - phase: 05-01
    provides: "The commit-msg skip-token hook and the squash-message setting (D-02, D-03) this plan's L22 entry cites as prior art"
  - phase: 05-02
    provides: "scripts/pr_land.py, make pr.land PR=N, and .github/workflows/required-jobs.txt -- the sanctioned merge tool Section 8 now documents and L22 describes"
provides:
  - "GitHub repository ruleset `default` (id 23977515), retargeted from no branch to `refs/heads/main`: required status checks `test (3.12)`, `vendor-bundle`, `image` (GitHub Actions, integration 15368) on an up-to-date head, plus the existing pull-request/deletion/non-fast-forward rules (repository setting, not in git)"
  - "docs/HOW_TO_DEVELOP.md: Section 8 rewritten around `make pr.land PR=N` as the sanctioned merge path, with the ruleset's apply/read-back/removal commands; Section 2 and \"Параллельные циклы\" no longer instruct a direct push to `main`"
  - "docs/architecture/packaging.md: one paragraph naming `make pr.land` and the ruleset next to the existing `make verify` gate description"
  - "docs/architecture/decision_log.md: `## L22` recording the merge gate as one decision (D-02 through D-05, D-12), extending L13 without superseding it"
affects: [05-04, 05-05]

# Actuals (#2632)
actuals:
  tokens: 4536
  tasks: 3
  commits: 3
plan_head_before: dc83e63

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "A repository-level GitHub ruleset retargeted via `gh api <GET> --jq '{...}' | gh api -X PUT --input -` -- the PUT body is built from the live GET so every rule the human already set (pull_request's review/merge-method parameters, bypass_actors, enforcement) travels unchanged; only the `required_status_checks` rule is replaced, never appended as a duplicate"
    - "A GitHub repository setting that is not in git (a ruleset, like D-03's squash-message setting before it) gets its exact apply/read-back/removal commands recorded next to each other in docs/HOW_TO_DEVELOP.md, so the next reader can reproduce or undo it without re-deriving the `gh api` call"

key-files:
  created: []
  modified:
    - docs/HOW_TO_DEVELOP.md
    - docs/architecture/packaging.md
    - docs/architecture/decision_log.md

key-decisions:
  - "Retargeted the repository's existing `default` ruleset (id 23977515) rather than creating a second one -- planning's flagged assumption 1 confirmed live before the change: the ruleset's `conditions.ref_name.include` was still `[]` and its rules were exactly `deletion`, `non_fast_forward`, `pull_request`, matching the plan's precondition, so the PUT was applied as written with no deviation."
  - "The ruleset's required checks are the post-D-09 set (`test (3.12)`, `vendor-bundle`, `image`) applied now, before Plan 05-04 collapses the CI matrix -- confirmed safe because `main`'s `ci.yml` already reports all three names on every PR today, alongside `test (3.10)` which nothing requires."
  - "Section 8's old manual `git switch main && git pull --ff-only ... && git branch -D ...` block is removed entirely, not merged with the new pr.land description -- `make pr.land` does every one of those steps itself (confirmed against `scripts/pr_land.py`'s actual `land()` control flow, not just its module docstring), so keeping the manual block would have described a second, competing path."
  - "L22 is one entry covering D-02 through D-05 and D-12 (five decisions across three plans), not five separate entries -- per CONTEXT.md D-08 and this plan's flagged assumption 6, matching the log's own convention of one entry per coherent decision rather than one per sub-choice."

patterns-established:
  - "Repository-setting documentation pattern: apply command, read-back command, removal command, grouped together in HOW_TO_DEVELOP.md next to a one-sentence trigger for when to re-run the apply command (now used for both D-03's squash-message setting and D-12's ruleset)."

requirements-completed: []  # REQ-ci-verified is shared with 05-01/05-02/05-04/05-05;
# `gsd_run query requirements.ready-ids` reports 0/1 ready -- sibling plans 05-04/05-05
# have not produced a SUMMARY yet, so it stays unmarked until the last one does (the
# shared-ID gate, #2388).

coverage:
  - id: D1
    description: "A GitHub ruleset on `main` refuses a merge whose head lacks green `test (3.12)`, `vendor-bundle` and `image`, or is behind `main`, and requires a pull request -- read back from `rules/branches/main` as the evidence (D-12, ROADMAP SC-5)."
    requirement: "REQ-ci-verified"
    verification:
      - kind: other
        ref: "gh api repos/halfb00t/spur/rules/branches/main (live read-back after the PUT): rule types exactly deletion, non_fast_forward, pull_request, required_status_checks, all from ruleset 23977515; strict_required_status_checks_policy true; required checks exactly image@15368, test (3.12)@15368, vendor-bundle@15368 -- matches the task's <automated> assertion byte-for-byte"
        status: pass
    human_judgment: false
  - id: D2
    description: "docs/HOW_TO_DEVELOP.md Section 8 leads with `make pr.land PR=N` as the sanctioned merge path (replacing the GitHub button), lists its checks in scripts/pr_land.py's actual order, keeps \"инструмент, а не стена\" for pr.land describing the ruleset as the wall; Sections 2 and \"Параллельные циклы\" no longer instruct a direct push to `main`; docs/architecture/packaging.md names the merge gate."
    requirement: "REQ-ci-verified"
    verification:
      - kind: other
        ref: "grep assertions in the task's <verify> block: 'make pr.land PR=', 'required-jobs.txt', 'не стена' (case-insensitive), the D-03 and D-12 commands all present; 'Squash-merge PR на GitHub', 'Коммиты плана ложатся в', 'push origin main' all absent (grep exit 1); docs/architecture/packaging.md names 'make pr.land' and 'ruleset'"
        status: pass
    human_judgment: true
    rationale: "The automated greps confirm the required strings are present and the forbidden ones are absent, but whether the rewritten Russian prose reads naturally, matches the document's existing terse/imperative style, and accurately reflects what scripts/pr_land.py actually does (beyond string matching) is a judgment call for a Russian-fluent reader familiar with the code."
  - id: D3
    description: "`## L22` appended to docs/architecture/decision_log.md, dated 2026-09-25, citing the trigger (PR #2's red merge, the two run-less squash commits) and covering the commit-msg hook, the squash message, the ship-note step, make pr.land and the ruleset as one decision that extends L13 without superseding it; the log's earlier entries are untouched."
    requirement: "REQ-ci-verified"
    verification:
      - kind: other
        ref: "grep -nE '^## L22 ' (heading present, no '(supersedes' in it); the task's evidence-string loop over 13 required substrings (35993984796, 538d26f, bfc9110, 20b63e4, 6fce500, 'does not state a case rule', 'make pr.land', 'required-jobs.txt', 'match-head-commit', 23977515, 'rules/branches/main', D-12, 'Date: 2026-09-25') all present; git show --format= <commit> -- decision_log.md has zero lines matching ^-[^-] (append-only proven, not just claimed)"
        status: pass
    human_judgment: true
    rationale: "The automated checks prove the required facts are cited and no existing line was removed or altered, but whether the entry's narrative accurately represents the decisions it summarizes (D-02 through D-05, D-12) and reads as a faithful record rather than a plausible-sounding one is a judgment call for a human familiar with those decisions."

# Metrics
duration: ~13min
completed: 2026-09-25
status: complete
---

# Phase 5 Plan 3: The Merge Gate on `main` -- Ruleset, Documented Path, and L22 Summary

**A GitHub ruleset on `main` (the repository's own `default` ruleset, retargeted) now requires green `test (3.12)`, `vendor-bundle` and `image` on an up-to-date head plus a pull request, `docs/HOW_TO_DEVELOP.md` documents `make pr.land PR=N` as the only sanctioned path through it, and `L22` records the whole merge gate as one decision.**

## Performance

- **Duration:** ~13 min (reconstructed from STATE.md's prior session timestamp,
  06:37:49Z, to the third task commit's timestamp, 06:48:44+06:00/06:48:44Z-equivalent;
  `PLAN_START_TIME` was not captured via a standalone `date -u` call before the first
  read, the same gap 05-01-SUMMARY.md and 05-02-SUMMARY.md recorded)
- **Started:** ~2026-09-25T06:37:49Z (reconstructed)
- **Completed:** 2026-09-25T06:50:09Z
- **Tasks:** 3 completed
- **Files modified:** 3

## Accomplishments

- The repository's own `default` ruleset (id 23977515) is retargeted from no branch to
  `refs/heads/main`: it now requires `test (3.12)`, `vendor-bundle` and `image` green
  from GitHub Actions, on a head that is up to date with `main`, plus a pull request for
  every change -- read back from `rules/branches/main` and matching the task's assertion
  byte-for-byte. GitHub itself now refuses a direct push to `main` and a merge behind or
  without those three checks.
- `docs/HOW_TO_DEVELOP.md` Section 8 ("Влить") leads with `make pr.land PR=N` (D-05) as
  the sanctioned merge path, listing every refusal `scripts/pr_land.py`'s `land()`
  actually performs, in order, and keeps "инструмент, а не стена" for `pr.land`
  describing the ruleset as the wall it goes through. It also carries the ruleset's
  apply, read-back and removal commands next to Plan 05-01's squash-setting command.
- Section 2 and "Параллельные циклы" no longer send anyone to push `main` directly: the
  phase branch is now described as cut from `origin/main` before discussion, and a
  `worktree.land` result reaches `main` only through a PR.
- `docs/architecture/packaging.md` gains one paragraph naming `make pr.land` and the
  ruleset next to its existing description of where `make verify` runs.
- `docs/architecture/decision_log.md` gains `## L22`, appended after `L21`: one entry
  covering the commit-msg hook, the squash-message setting, the ship-note step,
  `make pr.land` and the ruleset, citing the PR #2 red merge and the two run-less squash
  commits as its trigger. The commit that appended it removes no existing line.

## Task Commits

Each task was committed atomically:

1. **Task 1: The wall -- the repository's `default` ruleset retargeted to `main`,
   requiring green `test (3.12)`, `vendor-bundle` and `image` on an up-to-date head and
   a pull request; read back and recorded (D-12)** - `16c6736` (docs)
2. **Task 2: Section 8 is `make pr.land PR=N`, the sanctioned path through the wall --
   "a tool, not a wall"; no instruction to push to `main` survives (D-05, D-12)** -
   `f82311c` (docs)
3. **Task 3: `L22` appended -- CI is the merge gate for `main` (D-08, D-12)** -
   `a6c1114` (docs)

**Plan metadata:** committed separately by this workflow's final step.

## Files Created/Modified

- `docs/HOW_TO_DEVELOP.md` - Section 8 gains the ruleset apply/read-back/removal
  commands (Task 1) and is rewritten around `make pr.land PR=N` with the wall-and-tool
  paragraph (Task 2); Section 2 and "Параллельные циклы" no longer instruct a direct
  push to `main` (Task 2)
- `docs/architecture/packaging.md` - one paragraph naming the merge gate and the ruleset
  (Task 2)
- `docs/architecture/decision_log.md` - `## L22` appended (Task 3)

## Decisions Made

See `key-decisions` in the frontmatter: retargeting the existing `default` ruleset
rather than creating a second one (planning's flagged assumption 1, confirmed live
before the change); applying the post-D-09 required-check set now rather than waiting
for Plan 05-04's matrix collapse; removing the old manual local-follow-up block from
Section 8 entirely rather than merging it with `pr.land`'s description; and L22 as one
entry covering five decisions across three plans rather than five entries.

## Deviations from Plan

None - plan executed exactly as written. The Task 1 precondition (`gh auth status`,
admin permission, the ruleset's current rules) was verified before any write, and the
live ruleset matched planning's read exactly (empty `include`, exactly
`deletion`/`non_fast_forward`/`pull_request`), so the PUT was applied as the plan
specified with no reshaping.

## Issues Encountered

- `PLAN_START_TIME` was not captured via an explicit `date -u` call at the very start of
  this session -- the same gap 05-01-SUMMARY.md and 05-02-SUMMARY.md both recorded.
  Duration above is reconstructed from STATE.md's prior session timestamp to the last
  task commit's own git timestamp, not a precisely measured figure. All three task
  commit timestamps (`16c6736`, `f82311c`, `a6c1114`) are exact and git-verifiable
  regardless.

## User Setup Required

None - no external service configuration required. `gh` was already authenticated with
the scopes Task 1's precondition needed (`repo`, `workflow`, `admin:org`), and admin
permission on the repository was verified read-only (`gh api 'repos/{owner}/{repo}'
--jq .permissions.admin` printed `true`) before any write.

## Next Phase Readiness

- The ruleset on `main` is live and enforced (`enforcement: active`, no bypass actors):
  Plan 05-04 (Python 3.12 only) can collapse the CI matrix, and its own Task 3 must then
  re-read `rules/branches/main` and confirm the required checks still equal the
  collapsed `required-jobs.txt` -- this plan's required-check names never included
  `test (3.10)`, so nothing needs to change on the ruleset itself when that job is
  dropped from `ci.yml`, but the drift test and the ruleset's own copy should agree
  after the collapse too.
- Plan 05-05 (this phase's own ship/merge) is the first live, non-refusal exercise of
  both the ruleset and `make pr.land` together: the PR that lands this phase must now go
  through `make pr.land PR=N`, which will itself be walled by the ruleset applied here.
- No blockers for 05-04 or 05-05.

## Self-Check: PASSED

All key-files modified (`docs/HOW_TO_DEVELOP.md`, `docs/architecture/packaging.md`,
`docs/architecture/decision_log.md`) confirmed present on disk with `[ -f ]`. All three
task commits (`16c6736`, `f82311c`, `a6c1114`) confirmed in `git log --oneline --all`.
Every plan-level `<verification>` item re-run and passing: the ruleset read-back matches
the exact expected structure; Section 8 holds all required commands and leads with
`make pr.land PR=N`; the three forbidden phrases are absent from
`docs/HOW_TO_DEVELOP.md`; `packaging.md` names the merge gate; `L22` is appended with
all 13 required evidence strings and removes no existing line (git-diff-proven); each
task's `git show --stat --format= HEAD` lists exactly the files its acceptance criteria
named; `make verify` exits 0 (178 tests passed) after every task.

---
*Phase: 05-ci-observed-green*
*Completed: 2026-09-25*
