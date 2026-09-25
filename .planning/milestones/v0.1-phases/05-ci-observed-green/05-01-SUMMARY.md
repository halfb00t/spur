---
phase: 05-ci-observed-green
plan: 01
subsystem: ci-merge-gate
tags: [pre-commit, git-hooks, github-actions, gh-cli, tech-debt, mypy-strict]

# Dependency graph
requires: []
provides:
  - "`scripts/skip_tokens.py`: `find_skip_tokens()` / `message_to_check()` (pure, no I/O)
    and `main()` (the commit-msg hook entry) -- the one definition of a GitHub Actions
    skip token, reused unmodified by Plan 05-02's `make pr.land`"
  - "The `no-skip-token` commit-msg hook in `.pre-commit-config.yaml`, installed by the
    documented `pre-commit install` via `default_install_hook_types`"
  - "The repository's squash-merge settings: `squash_merge_commit_title=PR_TITLE`,
    `squash_merge_commit_message=PR_BODY` (GitHub repo setting, not in git)"
  - "`docs/HOW_TO_DEVELOP.md` §6/§8: the manual ship-note step and the `gh api -X PATCH`
    command, in Russian"
  - "`docs/tech_debt/resolved/2026-09-25-ship-note-skip-token-leaks-into-squash-merge.md`,
    resolved and indexed"
affects: [05-02, 05-03]

# Actuals (#2632)
actuals:
  tokens: 5716
  tasks: 2
  commits: 2

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "A `repo: local` pre-commit hook scoped to `stages: [commit-msg]`, alongside the
      existing `verify` hook now pinned to `stages: [pre-commit]` -- an unpinned hook
      inherits every installed stage and runs twice per commit (confirmed live: 2 runs
      unpinned, 1 pinned)"
    - "Message-text matching stops at git's own scissors line
      (`# ------------------------ >8 ------------------------`, `git commit -v`'s cut
      marker) -- confirmed byte-for-byte against a real `git commit -v` editor buffer in
      a scratch repo, not assumed from the plan's prose description"

key-files:
  created:
    - scripts/__init__.py
    - scripts/skip_tokens.py
    - tests/test_skip_tokens.py
  modified:
    - .pre-commit-config.yaml
    - Makefile
    - docs/HOW_TO_DEVELOP.md
    - docs/tech_debt/INDEX.md
    - docs/tech_debt/active/2026-09-25-ship-note-skip-token-leaks-into-squash-merge.md (moved to resolved/)

key-decisions:
  - "Python, not bash, for the hook (departs from RESEARCH.md's bash/grep
    recommendation): Plan 05-02's `make pr.land` must apply the identical token test to
    the squash commit's subject and body, which a commit-msg-only bash script cannot be
    imported into. One importable `find_skip_tokens()` is the only way the two checks
    cannot drift apart; it also sits under mypy `--strict` and is tested by direct
    import, the way `bench` already is."
  - "The `verify` hook needed `stages: [pre-commit]` -- not stated in RESEARCH or
    CONTEXT, found by reading the installed `pre_commit/repository.py` (a hook with no
    `stages` gets the top-level `default_stages`, which defaults to every stage) and
    proven in a scratch repo: unpinned, `make verify` ran twice per commit once
    `commit-msg` joined `default_install_hook_types`; pinned, once."
  - "Git's scissors cut line is exactly `# ` + 24 dashes + ` >8 ` + 24 dashes -- verified
    byte-for-byte in a scratch repo this session (`git commit -v` with a fake
    `GIT_EDITOR` that copies the buffer out before the commit completes), not taken on
    faith from the plan's prose description."

patterns-established:
  - "Pure decision core (`find_skip_tokens`), thin I/O shell (`main`'s file read) -- same
    split `bench/memory.py`'s `_is_capped` already uses, now extended to a second
    top-level tooling package (`scripts/`)."

requirements-completed: [REQ-ci-verified]

coverage:
  - id: D1
    description: "A commit whose message carries any of the six GitHub Actions skip
      tokens is refused at `git commit` on a clone with the hook installed; the match
      covers subject and body, is case-insensitive, and stops at git's scissors line."
    requirement: "REQ-ci-verified"
    verification:
      - kind: unit
        ref: "tests/test_skip_tokens.py (24 tests: all 6 token forms, case variants, the
          no-space trailer, the body-paragraph case, first-text/no-trailing-newline
          edges, empty/clean-message cases, near-misses, scissors-line cases, and the
          hook-entry subprocess cases including invalid UTF-8)"
        status: pass
      - kind: other
        ref: "real `git commit --allow-empty -m 'probe: [ci skip] must be refused'`,
          refused by git with HEAD unchanged"
        status: pass
    human_judgment: false
  - id: D2
    description: "`make verify` runs once per commit, not twice, after the commit-msg
      hook joins the same `.pre-commit-config.yaml`."
    requirement: "REQ-ci-verified"
    verification:
      - kind: other
        ref: "`.venv/bin/pre-commit run --hook-stage commit-msg` on a clean message:
          only `no-skip-token` runs, `verify` does not appear in the output"
        status: pass
    human_judgment: false
  - id: D3
    description: "`scripts/` is under `make typecheck` (mypy `--strict`,
      `disallow_any_explicit`), like `src`, `tests`, `docker`, `bench`."
    requirement: "REQ-ci-verified"
    verification:
      - kind: unit
        ref: "make verify (mypy src tests docker bench scripts) -- 128 tests passed, 0
          type errors"
        status: pass
    human_judgment: false
  - id: D4
    description: "The repository's squash-merge settings are
      `squash_merge_commit_title=PR_TITLE`, `squash_merge_commit_message=PR_BODY`,
      applied by one `gh api -X PATCH` and read back."
    requirement: "REQ-ci-verified"
    verification:
      - kind: other
        ref: "`gh api repos/halfb00t/spur` read back after the PATCH: before
          `COMMIT_OR_PR_TITLE`/`COMMIT_MESSAGES`, after `PR_TITLE`/`PR_BODY`"
        status: pass
    human_judgment: false
  - id: D5
    description: "`docs/HOW_TO_DEVELOP.md` §8 records the exact PATCH command and why it
      lives there; §6 documents the manual ship-note step the hook now forces, in
      Russian, matching the doc's existing style."
    verification:
      - kind: other
        ref: "grep for the exact PATCH command and the ship-note subject shape in
          docs/HOW_TO_DEVELOP.md"
        status: pass
    human_judgment: true
    rationale: "The automated grep confirms the required strings are present; whether
      the added Russian prose reads naturally and matches the doc's existing terse,
      imperative style is a judgment call for a Russian-fluent reader."
  - id: D6
    description: "The skip-token debt file is `Status: resolved`, carries `Resolved in:`
      equal to Task 1's commit, is `git mv`'d into `resolved/`, and its INDEX.md row
      moved -- in the commit that completes the fix (D-11)."
    requirement: "REQ-ci-verified"
    verification:
      - kind: other
        ref: "grep/sed check: Status: resolved, Resolved in: sha resolves to Task 1's
          commit, file tracked only under resolved/, INDEX.md links it once under
          Resolved"
        status: pass
    human_judgment: false

# Metrics
duration: ~12min
completed: 2026-09-25
status: complete
---

# Phase 5 Plan 1: Commit-Time Skip-Token Hook + Curated Squash Message Summary

**A repo-owned `commit-msg` hook refuses all six GitHub Actions skip tokens anywhere in a
commit message, and the repository's squash-merge message is now the PR title and body
instead of the concatenated branch-commit subjects that carried a token onto `main` twice.**

## Performance

- **Duration:** ~12 min (reconstructed from the prior session's STATE.md timestamp,
  05:58:31Z, to the final task commit, 06:08:48+06:00/06:08:48Z-equivalent -- not a
  precisely captured `PLAN_START_TIME`; see Issues Encountered)
- **Tasks:** 2 completed
- **Files modified:** 8 (3 created, 5 modified/moved)

## Accomplishments

- `scripts/skip_tokens.py`: `find_skip_tokens()`, `message_to_check()`, `main()` -- one
  importable definition of a GitHub Actions skip token, covering all six forms
  (`[skip ci]`, `[ci skip]`, `[no ci]`, `[skip actions]`, `[actions skip]`,
  `skip-checks: true`), case-insensitive, subject and body, stopping at git's scissors
  line -- proven by 24 tests and a real refused `git commit`.
- The `no-skip-token` commit-msg hook is installed by the already-documented
  `pre-commit install`; the existing `verify` hook is pinned to `stages: [pre-commit]`
  so it still runs exactly once per commit.
- `scripts` joined `make typecheck`'s directory list -- mypy `--strict`,
  `disallow_any_explicit`, no suppressions.
- The repository's squash-merge settings are now `PR_TITLE`/`PR_BODY` (read back live),
  and the exact `gh api -X PATCH` command is recorded in `docs/HOW_TO_DEVELOP.md` §8.
- `docs/HOW_TO_DEVELOP.md` §6 documents the manual ship-note step the hook now forces
  (`gsd-ship`'s own `[ci skip]` ship note is refused).
- The `must`-severity debt file this plan exists to close is `Status: resolved`, `git
  mv`'d into `docs/tech_debt/resolved/`, and its INDEX.md row moved -- in the commit
  that completes the fix (D-11).

## Task Commits

Each task was committed atomically:

1. **Task 1: End to end -- a commit whose message carries a GitHub Actions skip token is
   refused at `git commit` (D-02)** - `fac76f5` (feat, tdd -- RED and GREEN in one
   commit; see below)
2. **Task 2: The squash message is the PR title and body; the ship-note step is
   documented; the debt is retired (D-03, D-04, D-11)** - `7959cdb` (docs)

**Plan metadata:** committed separately by this workflow's final step.

_TDD note: this project's pre-commit hook runs the full `make verify` with no bypass
(~30-40s), so RED and GREEN land in one commit rather than two, matching the convention
Phase 3 already established (see STATE.md). RED evidence: before `scripts/skip_tokens.py`
existed, `.venv/bin/python -m pytest tests/test_skip_tokens.py -q` failed at collection
with `ModuleNotFoundError: No module named 'scripts.skip_tokens'` -- the intentional RED
this plan's own action text calls for ("watch it fail -- the module does not exist
yet")._

## Files Created/Modified

- `scripts/__init__.py` - package marker; repository tooling outside the `spur` wheel
- `scripts/skip_tokens.py` - the skip-token pattern, scissors cut, and hook entry
- `tests/test_skip_tokens.py` - 24 tests covering every token form, case variants, the
  body-paragraph and scissors-line edges, and the hook entry as a subprocess
- `.pre-commit-config.yaml` - `default_install_hook_types`, the `no-skip-token` hook,
  `verify` pinned to `stages: [pre-commit]`
- `Makefile` - `scripts` added to `make typecheck`'s directory list
- `docs/HOW_TO_DEVELOP.md` - §8 gains the PATCH command, §6 gains the manual ship-note
  step (both in Russian)
- `docs/tech_debt/INDEX.md` - the item's row moved from Active to Resolved
- `docs/tech_debt/active/2026-09-25-ship-note-skip-token-leaks-into-squash-merge.md` -
  `git mv`'d to `docs/tech_debt/resolved/`, `Status: resolved`, `Resolved in: fac76f5`, a
  new `## Resolution (2026-09-25)` section

## Decisions Made

See `key-decisions` in the frontmatter: Python over bash for the hook (Plan 05-02 reuse),
the `verify` hook's `stages: [pre-commit]` pin (a planning-probe finding), and the
scissors line's exact byte shape (also a planning-probe finding, re-verified this
session).

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- `PLAN_START_TIME` was not captured via an explicit `date -u` call at dispatch (the
  executor's own `record_start_time` step was not run as a standalone first action).
  Duration above is reconstructed from the prior session's `STATE.md`/`state.json`
  timestamp (05:58:31Z) to the final task commit, the same "reconstructed, not measured"
  caveat STATE.md already records for Phase 4 Plan 1's duration. Both task commits'
  timestamps (`fac76f5`, `7959cdb`) are exact and git-verifiable regardless.

## Tracer Feedback Gate

Task 1 is `type="tracer"`. Its `<verify>` block carries only `<automated>` checks (no
`<human-check>`), the run is interactive, and `workflow.human_verify_mode` is unset
(defaults to `end-of-phase`) -- per the tracer feedback gate's row 3, the tracer's
`<verify>` was re-run end to end before starting Task 2 (all six automated checks passed,
see Task 1's own verify output above), and execution continued straight to Task 2 with no
checkpoint synthesized.

## User Setup Required

None - no external service configuration required. `gh` was already authenticated with
the scopes Task 2's precondition needed (`repo`, `workflow`, `admin:org`), verified
read-only before any Task 2 work began.

## Next Phase Readiness

- `scripts/skip_tokens.py`'s `find_skip_tokens()` is ready for Plan 05-02's `make
  pr.land` to import and apply to a squash commit's subject and body -- no interface
  changes anticipated.
- The squash-merge setting and the ship-note doc step are live; the next real
  `/gsd-ship` on this repository will exercise the manual step for the first time.
- No blockers for Plan 05-02 (`make pr.land`, the required-jobs check) or Plan 05-03
  (the `main` ruleset, D-12).

## Self-Check: PASSED

All key-files (`scripts/__init__.py`, `scripts/skip_tokens.py`,
`tests/test_skip_tokens.py`, `docs/tech_debt/resolved/2026-09-25-ship-note-skip-token-leaks-into-squash-merge.md`)
confirmed present on disk with `[ -f ]`. Both task commits (`fac76f5`, `7959cdb`)
confirmed in `git log --oneline --all`. All plan-level `<verification>` and
`<acceptance_criteria>` re-run and passing (see Task Commits / Accomplishments above);
`make verify` exits 0.

---
*Phase: 05-ci-observed-green*
*Completed: 2026-09-25*
