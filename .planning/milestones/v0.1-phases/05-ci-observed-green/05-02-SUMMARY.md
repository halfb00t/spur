---
phase: 05-ci-observed-green
plan: 02
subsystem: ci-merge-gate
tags: [github-cli, github-actions, gh-api, merge-gate, mypy-strict, tdd]

# Dependency graph
requires:
  - phase: 05-01
    provides: "scripts/skip_tokens.py's find_skip_tokens() -- reused unmodified by
      message_refusals() to check the squash commit's subject and body"
provides:
  - "`scripts/pr_land.py`: `land()`, `check_head()`, `head_refusals()`,
    `message_refusals()`, `pr_refusals()`, `required_jobs()`, and the parsers
    (`parse_pull_request`, `parse_runs`, `parse_jobs`, `parse_compare`) -- the pure
    decision core plus the thin gh/git shell behind `make pr.land PR=N`"
  - "`.github/workflows/required-jobs.txt`: the job names `make pr.land` requires
    green, next to `ci.yml`, held equal to it by a test"
  - "`make pr.land PR=<n>` Makefile target"
affects: [05-03, 05-05]

# Actuals (#2632)
actuals:
  tokens: 13715
  tasks: 2
  commits: 2
plan_head_before: 00625ef

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Pure decision core / thin network shell for an external system with no
      offline test (bench/memory.py's _is_capped/sweep() split, applied to the
      GitHub API): head_refusals/pr_refusals/message_refusals are plain functions
      over parsed gh JSON, tested with 50 offline cases against recorded/derived
      fixtures; check_head/land are the thin shell around them, exercised live
      read-only against real PRs"
    - "A Runner = Callable[[list[str]], subprocess.CompletedProcess[str]] seam
      threaded through every gh/git call -- a FakeRunner in tests answers by argv
      substring, so the whole merge path (refusals, the poll loop, the local
      follow-up) is provable offline with no network"
    - "A drift test derives the required job set from ci.yml's own text (regex over
      the 'jobs:' section, the test matrix expanded per version) and asserts it
      equals required_jobs() -- required-jobs.txt cannot silently diverge from what
      CI actually runs"

key-files:
  created:
    - scripts/pr_land.py
    - tests/test_pr_land.py
    - .github/workflows/required-jobs.txt
  modified:
    - .github/workflows/ci.yml
    - Makefile

key-decisions:
  - "Task 1 imports find_skip_tokens and uses it inline in land() (an unnamed
    skip-token check on the squash subject/body); Task 2 extracts that into the
    named, independently-tested message_refusals(subject, body) pure function and
    wires land() to call it explicitly alongside check_head's refusals -- matches
    the plan's own staging (Task 1's acceptance criteria requires the import
    already present and used, not dormant; an unused import would fail ruff's
    F401 under make verify)."
  - "JSON parsing narrows with four small isinstance-based helpers
    (_as_object/_as_array/_as_int/_as_str) that raise TypeError, caught once per
    parser and re-raised as ValueError naming the field -- not `# type: ignore`
    comments. Chosen after mypy --strict flagged int(data['number']) (object has
    no int() overload) and after ruff's TRY004/TRY301/TRY300 flagged the first
    draft's inline isinstance-raise-ValueError-return pattern inside try blocks.
    Matches this project's own 'object narrowed at use' convention (L21,
    CODING_VALUES.md) more directly than a type:ignore would."
  - "head_refusals gained a required compare: tuple[int, int] parameter in Task 2
    (no default) rather than an optional one -- check_head always fetches compare
    now, so a default would be dead code the moment Task 2 landed; Task 1's own
    tests were updated in the same commit to pass a neutral NOT_BEHIND = (1, 0)."
  - "The live 'check_head on PR #3's head returns exactly the behind refusal' probe
    from Task 2's <verify> block is NOT a pytest test -- it needs network and an
    authenticated gh, which make verify/make test must never require (the module
    docstring's own D-16 pattern: needs network, runs only as make pr.land). Run
    once, standalone, as this task's own verification step instead."

patterns-established:
  - "A FakeRunner.on(substring, *responses) / .replace(prefix, *responses) test
    double for external-CLI-shaped systems: register handlers keyed on a
    distinctive argv substring, first match wins, a handler with more than one
    response pops in order (the poll-then-find shape) -- reusable for any future
    gh/git-shelling module."

requirements-completed: []  # REQ-ci-verified is shared with 05-01/05-03/05-04/05-05;
# `gsd_run query requirements.ready-ids` reports 0/1 ready -- sibling plans in this
# phase have not all produced a SUMMARY yet, so it stays unmarked until the last one
# does (the shared-ID gate, #2388).

coverage:
  - id: D1
    description: "`make pr.land PR=N` resolves a PR's head sha, refuses on a stale,
      dirty, red, missing or behind head, squash-merges with the exact checked
      subject and body (--match-head-commit, never --delete-branch), polls up to
      ~60s for a run on the squash commit and prints its URL, then does the local
      follow-up (switch/pull/branch -D) without ever deleting unmerged work."
    requirement: "REQ-ci-verified"
    verification:
      - kind: unit
        ref: "tests/test_pr_land.py -- happy path, poll timeout, local-tip-differs,
          local-branch-absent, PR-not-OPEN, dirty-tree, unparseable-read,
          gh-pr-merge-failure (30 tests added in Task 1's commit)"
        status: pass
      - kind: other
        ref: "make pr.land PR=3 (live): exits non-zero, names PR #3's real state
          MERGED, prints 'nothing was merged'"
        status: pass
      - kind: other
        ref: "make pr.land (no PR=) (live): exits non-zero, prints 'PR= required'"
        status: pass
    human_judgment: false
  - id: D2
    description: "Every way a PR can be stale, red, missing, behind or
      token-carrying is refused before anything merges (behind/identical compare,
      zero runs, in-progress run, missing/red/cancelled/skipped required job, a
      skip token in the squash title or a later body paragraph); several runs for
      one head sha are decided by the newest id regardless of API order; the
      required job set cannot drift from what ci.yml actually runs (drift test)."
    requirement: "REQ-ci-verified"
    verification:
      - kind: unit
        ref: "tests/test_pr_land.py -- behind/identical/ahead compare, both
          ordering directions, job-order shuffling, empty-jobs run, red/cancelled/
          skipped job, title- and body-paragraph skip tokens, empty body, several
          problems at once, the drift test (20 tests added in Task 2's commit, 50
          total in the file)"
        status: pass
      - kind: other
        ref: "check_head on PR #3's real head, live and read-only: returns exactly
          one refusal, naming 'behind' (main is one commit ahead of PR #3's real
          head; run 36088409707 is green on all four required jobs)"
        status: pass
    human_judgment: false

# Metrics
duration: ~35min (reconstructed; see Issues Encountered)
completed: 2026-09-25
status: complete
---

# Phase 5 Plan 2: `make pr.land` -- the Sanctioned Merge Gate Summary

**`make pr.land PR=N` squash-merges a PR only when its head is green on every named
job and current with `main`, proves a `ci.yml` run exists for the resulting squash
commit before claiming success, and refuses -- naming why, never merging -- a stale,
dirty, red, missing, behind or skip-token-carrying PR.**

## Performance

- **Duration:** ~35 min (reconstructed -- see Issues Encountered)
- **Tasks:** 2 completed
- **Files modified:** 5 (3 created, 2 modified)

## Accomplishments

- `scripts/pr_land.py`: `land()` runs the full path in order -- read/refuse on the
  PR's state and base, refuse a dirty tree, `check_head` (behind/identical, no run,
  unfinished run, missing/red job) plus `message_refusals` (a skip token in the
  squash subject or body), squash-merge with `--match-head-commit` and the exact
  checked subject/body, poll up to `POLL_ATTEMPTS * POLL_INTERVAL_S` (~60s) for a run
  on the squash commit and print its URL, then the local follow-up
  (`git switch`/`pull --ff-only`/`branch -D`, the last only when the local branch's
  tip equals the merged head).
- `.github/workflows/required-jobs.txt` lists the four jobs `ci.yml` runs today
  (`test (3.10)`, `test (3.12)`, `vendor-bundle`, `image`); a comment above `jobs:`
  in `ci.yml` points at it; a drift test derives the job ids from `ci.yml`'s own text
  (the `test` matrix expanded per Python version) and asserts equality with
  `required_jobs()` -- the two files cannot silently disagree without failing
  `make verify`.
- `make pr.land PR=<n>` Makefile target, under a new `# --- landing on main: the
  merge gate (L22) ---` banner, in `.PHONY`, with a `##` help line (`make` lists it).
- 50 offline tests against recorded/derived `gh` JSON (30 from Task 1, 20 from
  Task 2), plus two live, read-only network probes exercised directly against this
  repository: `make pr.land PR=3` refuses the already-merged PR #3, and `check_head`
  on PR #3's real head returns exactly one refusal, naming `behind`.
- The module docstring names D-12 (the ruleset `05-03` applies) and states which of
  `pr.land`'s pre-merge checks the ruleset duplicates (behind, required jobs) and
  why they stay (the squash-commit's own run must still be proven to appear; the
  list file is held equal to `ci.yml` by a test the ruleset's own copy cannot be),
  and which checks only `pr.land` makes (PR open/based on `main`, clean tree, no
  skip token in the squash text, the post-merge run, the local follow-up).

## Task Commits

Each task was committed atomically:

1. **Task 1: End to end -- `make pr.land PR=N` lands a green PR, prints the squash
   commit's run URL, and cleans up locally without losing work (D-05)** - `d982163`
   (feat, tdd -- RED and GREEN in one commit; see below)
2. **Task 2: Every stale, red, missing or token-carrying PR is refused before
   anything merges; the required list cannot drift from `ci.yml` (D-05 steps 2-3)**
   - `fa31fdb` (feat, tdd -- RED and GREEN in one commit)

**Plan metadata:** committed separately by this workflow's final step.

_TDD note: this project's pre-commit hook runs the full `make verify` (~30-40s) with
no bypass, so RED and GREEN land in one commit rather than two, matching the
convention Plan 05-01 already established. RED evidence, Task 1: before
`scripts/pr_land.py` existed, `.venv/bin/python -m pytest tests/test_pr_land.py -q`
failed at collection with `ModuleNotFoundError: No module named 'scripts.pr_land'`.
RED evidence, Task 2: before `message_refusals`/`parse_compare`/the compare-aware
`head_refusals` existed (Task 1's committed module, checked out over the Task 2
working tree), the same command failed at collection with
`ImportError: cannot import name 'message_refusals' from 'scripts.pr_land'`. Both
confirmed by temporarily reverting the module, capturing the failure, then restoring
it and re-running to GREEN before committing._

## Tracer Feedback Gate

Task 1 is `type="tracer"`. Its `<verify>` block carries only `<automated>` checks (no
`<human-check>`), the run is interactive, and `workflow.human_verify_mode` is unset
(defaults to `end-of-phase`) -- per the tracer feedback gate's row 3, the tracer's
`<verify>` (all four automated checks: the offline suite, `make pr.land` without
`PR=`, `make pr.land PR=3` live, `make verify`) was re-run end to end before starting
Task 2. All four passed; execution continued straight to Task 2 with no checkpoint
synthesized.

## Files Created/Modified

- `scripts/pr_land.py` - the merge gate: pure decision functions over parsed `gh`
  output, and a thin runner-driven shell (`check_head`, `land`, `main`)
- `tests/test_pr_land.py` - the whole path offline, every refusal, both ordering
  directions, the drift test, and (as comments only, run separately) the two live
  read-only verification commands
- `.github/workflows/required-jobs.txt` - the job names `make pr.land` requires
  green, next to `ci.yml`
- `.github/workflows/ci.yml` - a comment above `jobs:` pointing at
  `required-jobs.txt`; no behaviour change (`git show --format= HEAD -- ci.yml` on
  the Task 1 commit shows only added `#` lines)
- `Makefile` - the `pr.land` target and its `.PHONY`/banner additions

## Decisions Made

See `key-decisions` in the frontmatter: the Task-1-inline-then-Task-2-extracted
shape of the skip-token check (matches the plan's own staging and keeps
`find_skip_tokens` used, not dormant, from Task 1's first commit); the four
isinstance-narrowing helpers over `# type: ignore` comments for JSON parsing under
mypy `--strict`; `head_refusals` gaining a required (not optional) `compare`
parameter in Task 2; and keeping the live `behind`-refusal probe out of the pytest
suite entirely (it needs network, which `make verify` must never require).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] JSON-parsing helpers rewritten to satisfy mypy --strict and ruff**
- **Found during:** Task 1, first `make verify` run after the initial GREEN pass
- **Issue:** The first draft used `int(data["number"])  # type: ignore[arg-type]` to
  narrow JSON-decoded `object` fields. mypy reported an "Unused type: ignore" error
  (the actual mismatch is `call-overload`, not `arg-type`) and, separately, ruff's
  TRY004/TRY301/TRY300 flagged the inline `isinstance(...)`-raise-`ValueError`
  pattern inside `try` blocks (prefer `TypeError` for a type check; abstract the
  `raise` into a helper; move the trailing `return` out of the `try`).
- **Fix:** Replaced the `type: ignore` comments and inline checks with four small
  helpers (`_as_object`, `_as_array`, `_as_int`, `_as_str`) that raise `TypeError`,
  caught once per parser's own `except` clause and re-raised as `ValueError` naming
  the field. No suppressions of any kind remain.
- **Files modified:** scripts/pr_land.py (same commit as Task 1's feature code, not
  a separate fix commit -- caught before the first commit was made)
- **Verification:** `make verify` (mypy `--strict`, ruff) exits 0; `RED_RUN_JOBS_JSON`-based
  and every other parser test still passes
- **Committed in:** d982163 (Task 1 commit; the issue was caught and fixed before
  committing, so there is no separate fix commit)

---

**Total deviations:** 1 auto-fixed (1 blocking -- a lint/type-check failure that
would have failed `make verify`).
**Impact on plan:** No scope creep; the fix only changed *how* JSON fields are
narrowed, not what the module does or how it is tested.

## Issues Encountered

- `PLAN_START_TIME` was not captured via an explicit `date -u` call at the very
  start of this session (the same gap 05-01-SUMMARY.md recorded). Duration above is
  reconstructed: the two task commits (`d982163`, `fa31fdb`) are 7 minutes apart by
  their own timestamps, and the session's substantial live-research phase (recording
  fixtures via `gh api`/`gh pr view` against PR #2/#3, reading the seven `read_first`
  files, drafting both the module and the 50-test suite) preceded the first commit
  by a longer, unmeasured stretch -- ~35 min is a rough total, not a precise figure.
  Both task commit timestamps are exact and git-verifiable regardless.
- This plan's own live merge (the actual green-PR-lands-and-prints-a-run-URL path)
  is exercised only offline in this plan, by design (must_haves truth 9, this plan's
  `success_criteria`): "The first live landing is this phase's own merge, after ship
  (05-05's output section)." Nothing here is a gap -- it is the plan's own stated
  sequencing, restated so a reader of this summary alone does not mistake the
  offline happy-path tests for a live merge that has not happened yet.

## User Setup Required

None - no external service configuration required. `gh` was already authenticated
with the scopes this plan's preconditions needed (`repo`, `workflow`), verified
read-only before Task 1 began (`gh auth status`).

## Next Phase Readiness

- `scripts/pr_land.py` is ready for Plan 05-03 to apply the ruleset on `main` (D-12)
  that duplicates two of its checks (behind, required jobs) -- no interface changes
  anticipated; the module docstring already names which checks the ruleset
  duplicates and why `pr.land`'s own copies stay.
- Plan 05-04 (Python 3.12 only) can drop the `test (3.10)` line from
  `.github/workflows/required-jobs.txt` and the corresponding `ci.yml` matrix entry
  in one commit -- confirmed no test in `tests/test_pr_land.py` except the drift
  test depends on the file's current four-entry contents; the `land()`-level tests
  read `required_jobs()` from the real file but their job fixtures already include
  every current entry at `success`, so dropping one entry changes nothing they
  assert.
- Plan 05-05 (this phase's own ship/merge) is `pr.land`'s first live, non-refusal
  exercise: a real squash-merge, the ~60s poll for the resulting run, and the local
  follow-up on a real branch. The real observed lag from merge to run appearing
  should be recorded in STATE.md there, per this plan's flagged assumption 6.
- No blockers for 05-03, 05-04 or 05-05.

## Self-Check: PASSED

All key-files (`scripts/pr_land.py`, `tests/test_pr_land.py`,
`.github/workflows/required-jobs.txt`) confirmed present on disk with `[ -f ]`. Both
task commits (`d982163`, `fa31fdb`) confirmed in `git log --oneline --all`. All
plan-level `<verification>` items re-run and passing: `make test
PYTEST_ARGS="tests/test_pr_land.py -q"` (50 passed), `make pr.land` without `PR=`
refuses, `make pr.land PR=3` refuses live naming `MERGED`, `check_head` on PR #3's
head returns exactly the `behind` refusal live, `make verify` exits 0 (178 tests
passed).

---
*Phase: 05-ci-observed-green*
*Completed: 2026-09-25*
