---
phase: 06-address-tech-debt-merge-gate-solid-cache
plan: 04
subsystem: ci-merge-gate
tags: [pr-land, gh-api, tdd, pytest, tech-debt, docs, decision-log]

# Dependency graph
requires:
  - phase: 06-address-tech-debt-merge-gate-solid-cache
    provides: "Plan 06-03's run-conclusion check and effective-job-name drift test (head_refusals, _effective_job_names)"
provides:
  - "no_run_report(pr_number, squash_sha, waited_s, last_error, run) -> str: the only place land's step 5 report text is built, naming exactly one of a last read error, an Actions link, or a skip token read from the squash commit's own message"
  - "land()'s poll loop keeps a local last_error, cleared on a successful read, passed to no_run_report on timeout"
  - "The module docstring and docs/HOW_TO_DEVELOP.md §8 say the read-to-merge window rests on the ruleset's strict up-to-date policy (--match-head-commit pins the head, not the base), not on anything pr.land itself reads"
  - "L25 amending L22: the hook's whole-buffer rule (D-02), the run-conclusion check (D-04), and the D-07 merged-tree correction, in one append-only entry"
  - "The fifth and last of this phase's tech-debt records retired; docs/tech_debt/INDEX.md's Active table holds none of this phase's five files"
  - "STATE.md's Blockers/Concerns names all five records this phase retired and cites Phase 5's own squash-commit run 36122394253"
affects: []

# Actuals (#2632) -- pairs with the plan's `estimate` to calibrate future estimates.
actuals:
  tokens: 7244
  tasks: 3
  commits: 3

# Commit ledger (#3968) -- measured, not narrated: git rev-list --count
# plan_head_before..HEAD at SUMMARY-write time.
commits: 3
plan_head_before: 55bc8b79451184cdac025ae41a5b7fa1f9009675

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "no_run_report reads the squash commit's own message exactly once, then reports exactly one of three things it observed -- never a cause it did not itself read (D-06); a token found in that message is reported first because it is the one cause the function can establish and it means GitHub will never start a run whatever the polls saw"
    - "land's poll loop keeps a local last_error string, set on a non-zero read or a ValueError from parse_runs and cleared on a successful parse -- the same 'read, then decide' shape check_head already uses, applied to the poll instead of the initial check"

key-files:
  created: []
  modified:
    - scripts/pr_land.py
    - tests/test_pr_land.py
    - docs/HOW_TO_DEVELOP.md
    - docs/architecture/decision_log.md
    - .planning/STATE.md
    - "docs/tech_debt/active/2026-09-25-pr-land-blames-a-skip-token-for-any-missed-post-merge-run.md -> docs/tech_debt/resolved/2026-09-25-pr-land-blames-a-skip-token-for-any-missed-post-merge-run.md (git mv)"
    - docs/tech_debt/INDEX.md

key-decisions:
  - "no_run_report's precedence when both a commit-read failure and a prior poll last_error exist (untested by any plan case): the commit-read failure's own text wins, since it is the most recent read attempted and directly explains why no token search could run -- the plan's flagged assumption 1 only specifies the token-first / then-last-error / then-nothing-appeared order, not this sub-case."
  - "The token report's wording avoids the literal phrase 'reached main' ('...in the squash commit's message -- a regression of L22') to satisfy the plan's own acceptance criterion that scripts/pr_land.py no longer contains that phrase, even though a token genuinely did reach main -- the old blanket-blame text and the new, read-after-the-fact text needed to read differently, not just trigger differently."

patterns-established: []

requirements-completed: [D-01, D-06, D-07, D-10, D-11]

# Coverage metadata (#1602) -- one entry per shipped deliverable.
coverage:
  - id: D1
    description: "After a merge with no observed ci.yml run, no_run_report reports exactly one of three things: the last read error, an Actions link to check, or a named skip token read from the squash commit's message -- one offline case per branch"
    requirement: D-06
    verification:
      - kind: unit
        ref: "tests/test_pr_land.py#test_land_reports_the_last_read_error_when_every_poll_failed"
        status: pass
      - kind: unit
        ref: "tests/test_pr_land.py#test_land_reports_no_run_observed_with_the_actions_url_when_reads_succeeded"
        status: pass
      - kind: unit
        ref: "tests/test_pr_land.py#test_land_names_a_skip_token_only_after_reading_it_from_the_squash_commit"
        status: pass
      - kind: unit
        ref: "tests/test_pr_land.py#test_no_run_report_a_failed_commit_read_is_the_last_error"
        status: pass
      - kind: unit
        ref: "tests/test_pr_land.py#test_land_happy_path_returns_0_and_prints_the_run_url"
        status: pass
    human_judgment: false
  - id: D2
    description: "The live gh api commits/<sha> read, against two real commits: b72b0e1 (clean message) returns the Actions link with no last error and no token; 20b63e4 (carries a skip token) names it, with no last error"
    requirement: D-06
    verification:
      - kind: other
        ref: "live probe: no_run_report(4, 'b72b0e1...', 60.0, None, r) and no_run_report(2, '20b63e4...', 60.0, None, r) through the real gh -- recorded verbatim below in 'Live Probe'"
        status: pass
    human_judgment: false
  - id: D3
    description: "The module docstring and docs/HOW_TO_DEVELOP.md section 8 say pr.land proves the run-appeared half and check_head refuses a head it saw behind main, while the read-to-merge window rests on the ruleset's strict up-to-date policy (--match-head-commit pins the head, not the base) -- no behaviour change"
    requirement: D-07
    verification:
      - kind: other
        ref: "shell probe: grep -qF 'pins the head, not the base' scripts/pr_land.py && test \"$(grep -c 'proven here' scripts/pr_land.py)\" = 0 && grep -qF -- '--match-head-commit' docs/HOW_TO_DEVELOP.md && test \"$(grep -c 'никогда не опирается' docs/HOW_TO_DEVELOP.md)\" = 0"
        status: pass
      - kind: other
        ref: "AST probe: the last commit touching scripts/pr_land.py changed only its module docstring (ast.dump equality on the rest of the module, body[0] popped on both sides)"
        status: pass
    human_judgment: false
  - id: D4
    description: "L25 amends L22 (append-only, no existing line removed) with the hook's whole-buffer rule, the run-conclusion check, and the D-07 merged-tree correction, in that order after L22, L23, L24"
    requirement: D-10
    verification:
      - kind: other
        ref: "shell probe: exactly one '## L25 -- The merge gate reads the whole commit message' heading; '^## L2[2-5] ' headings appear in order L22, L23, L24, L25; git show --numstat on the decision-log-touching commit shows zero deletions"
        status: pass
    human_judgment: false
  - id: D5
    description: "The fifth debt file (pr-land-blames-a-skip-token) is Status: resolved, Resolved in: names Task 1's commit, git mv'd into resolved/ in the commit that also carries the docstring/section-8 change and L25, and docs/tech_debt/INDEX.md's Active table holds none of this phase's five files"
    requirement: D-01
    verification:
      - kind: other
        ref: "shell probe (this plan's own <verify> block, Task 2): Status/Resolved-in/ancestor/ls-files/INDEX-link checks -- recorded in 'Verification' below"
        status: pass
    human_judgment: false
  - id: D6
    description: "STATE.md's Blockers/Concerns names all five debt records this phase retired (each with its own Resolved in sha) and cites Phase 5's own squash-commit run 36122394253 (test (3.12), vendor-bundle, image, all green); only the Phase 2 latency waiver remains as an open concern"
    requirement: D-11
    verification:
      - kind: other
        ref: "shell probe: grep -qF the run URL and 'Resolved in Phase 6', exactly one '- ⚠' bullet naming Phase 2, all five debt-file names present"
        status: pass
    human_judgment: false

# Metrics
duration: 17min
completed: 2026-09-25
status: complete
---

# Phase 6 Plan 4: `pr.land` reports only what it observed; the merge-gate record is written Summary

**`land`'s step 5 no longer blames a skip token for every unobserved post-merge run — `no_run_report` names a read error, an Actions link, or a token read from the squash commit's own message, proven offline per branch and live against two real commits; the module docstring, §8 and new decision-log entry L25 say the read-to-merge window rests on the ruleset, not on anything `pr.land` itself reads; the fifth and last debt file this phase closes is retired; STATE.md cites the phase's evidence.**

## Performance

- **Duration:** 17 min
- **Started:** 2026-09-25T12:57:13Z
- **Completed:** 2026-09-25T13:14:16Z
- **Tasks:** 3
- **Files modified:** 7 (one via `git mv`)

## Accomplishments

- `no_run_report(pr_number, squash_sha, waited_s, last_error, run)` is the only place
  `land`'s step-5 unobserved-run text is built. It reads the squash commit's own message
  once (`gh api repos/{owner}/{repo}/commits/<sha> --jq '.html_url, .commit.message'`) and
  reports exactly one of three things: a token found in that message (checked first, the
  one cause it can actually establish); the last read error (a failed poll or a failed
  commit read) when reads did not work; or an Actions link to check when the reads worked
  and nothing appeared. It never names a cause it did not itself read.
- `land`'s poll loop keeps a local `last_error`, set on a non-zero read or a `ValueError`
  from `parse_runs`, cleared on a successful parse — the value `no_run_report` receives on
  timeout.
- The blanket "a skip token reached main" message is gone from `scripts/pr_land.py`,
  `tests/test_pr_land.py`, and `docs/HOW_TO_DEVELOP.md` §8 — all three greps for the old
  phrasing (`reached main`, `no ci.yml run appeared`, `no run appeared`) return zero.
- The module docstring's second paragraph and §8's «Стена и инструмент» paragraph now say
  the split (D-07): `pr.land` proves a run *appeared* for the squash commit and refuses a
  head it *saw* behind `main`; the window between that read and `gh pr merge` rests on the
  ruleset's strict up-to-date policy (D-12, no bypass actors) — `--match-head-commit` pins
  the head, not the base. No behaviour change; confirmed by an AST diff that the only
  change to `scripts/pr_land.py` in that commit is the module docstring.
- `docs/architecture/decision_log.md` gained `## L25 — The merge gate reads the whole
  commit message and the run's own verdict (amends L22)`, appended after L24 with zero
  lines removed from the file — L22's hook, run-verdict and merged-tree claims are each
  amended in one entry, citing Plans 06-02, 06-03 and this plan.
- The fifth and last of this phase's five tech-debt records —
  `2026-09-25-pr-land-blames-a-skip-token-for-any-missed-post-merge-run.md` — is
  `Status: resolved`, `Resolved in: e4345a4` (Task 1's commit), `git mv`'d into
  `resolved/`, with `docs/tech_debt/INDEX.md`'s row moved, all in the same commit that
  carries the docstring/§8 split and L25 (D-01). `INDEX.md`'s Active table now holds none
  of this phase's five files.
- `.planning/STATE.md`'s Blockers/Concerns names all five records this phase retired
  (each with its own `Resolved in:` sha) and cites Phase 5's own squash commit `b72b0e1`'s
  push run 36122394253 — `test (3.12)`, `vendor-bundle`, `image`, all green, read back live
  this plan's own execution. Only the Phase 2 latency waiver remains as an open concern.

## Task Commits

Each task was committed atomically:

1. **Task 1: End to end — after a merge with no observed run, `make pr.land` reports what
   it observed, naming a skip token only after reading it from the squash commit (D-06)**
   - `e4345a4` (fix, tracer/TDD — RED and GREEN folded into one commit; the pre-commit hook
     runs the full `make verify` with no bypass, so a RED-only commit whose tests fail
     cannot land)
2. **Task 2: The docstring and §8 say which half of the merge claim the ruleset carries;
   L25 amends L22; the blame debt is retired in that commit (D-07, D-10, D-01)** -
   `e91d7de` (docs)
3. **Task 3: STATE.md — the phase's retired blockers move into the resolved note, which
   now cites run 36122394253 (D-11)** - `9aa7a06` (docs)

**Plan metadata:** committed below, alongside this SUMMARY.

_Note: Task 1 is `type="tracer" tdd="true"` — RED and GREEN fold into one commit, not two,
because the repository's own pre-commit hook runs the full `make verify` on every commit
with no bypass (same pattern as 06-01, 06-02, 06-03)._

## RED Evidence

**Task 1** — before `no_run_report` existed, a temporary stub (`return "STUB"`) was added
so `tests/test_pr_land.py` could import successfully (a bare `ImportError` is a collection
crash, not valid RED evidence per `gsd-core/references/tdd.md`'s #3770 rule — the target
test must fail on a real assertion, not a load error). With the stub in place and `land()`
still printing its old blanket message, `make test PYTEST_ARGS="tests/test_pr_land.py -q"`
failed exactly the four new/target tests, all on real assertions against the *unchanged*
production behavior, with 54 other tests passing (no collection errors, no unrelated
failures):

```
FAILED tests/test_pr_land.py::test_land_reports_the_last_read_error_when_every_poll_failed
FAILED tests/test_pr_land.py::test_land_reports_no_run_observed_with_the_actions_url_when_reads_succeeded
FAILED tests/test_pr_land.py::test_land_names_a_skip_token_only_after_reading_it_from_the_squash_commit
FAILED tests/test_pr_land.py::test_no_run_report_a_failed_commit_read_is_the_last_error
4 failed, 54 passed in 0.08s
```

Representative failure:
`test_land_reports_the_last_read_error_when_every_poll_failed` asserted
`"no ci.yml run observed within 3 s" in out` and got the unchanged old message
(`'pr.land: PR #3 IS merged as deadbeef1234, but no ci.yml run appeared within 3 s -- a
skip token reached main (L22)\n'`) — the target assertion failing on real behavior of the
unchanged `land`, valid RED.

After the real `no_run_report` implementation and the `land()` poll-loop/print changes
(GREEN), `make test PYTEST_ARGS="tests/test_pr_land.py -q"` passed all 58 tests (later
confirmed at 191/191 under the full `make verify`).

## Live Probe (Task 1)

This plan's own execution, read-only, before any code change (`gh api
repos/{owner}/{repo}/commits/<sha> --jq '.html_url, .commit.message'`):

```
=== b72b0e1 ===
https://github.com/halfb00t/spur/commit/b72b0e1f1e31e06b9dd8bef964725b11f30e0c51
Phase 5: CI Observed Green (#4)
[... full PR body, no skip token present ...]

=== 20b63e4 ===
https://github.com/halfb00t/spur/commit/20b63e453a3cd0c72e5d0f995a107a238c652a90
docs(03): ship phase 3 — PR #2 [ci skip]
Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
```

After the GREEN implementation, the plan's own live `<verify>` command:

```
pr.land: PR #4 IS merged as b72b0e1f1e31e06b9dd8bef964725b11f30e0c51, but no ci.yml run observed within 60 s. Check https://github.com/halfb00t/spur/actions/workflows/ci.yml.
pr.land: PR #2 IS merged as 20b63e453a3cd0c72e5d0f995a107a238c652a90, but no ci.yml run observed within 60 s: '[ci skip]' in the squash commit's message -- a regression of L22.
```

Exit 0 — `b72b0e1`'s report carries the Actions URL, no `last error`, no token; `20b63e4`'s
report names `'[ci skip]'`, no `last error`.

## D-11 Live Verification (Task 3)

Before writing STATE.md's citation, run 36122394253 was read back live:

```
gh api repos/halfb00t/spur/actions/runs/36122394253 --jq '{head_sha, status, conclusion}'
{"conclusion":"success","head_sha":"b72b0e1f1e31e06b9dd8bef964725b11f30e0c51","status":"completed"}

gh api repos/halfb00t/spur/actions/runs/36122394253/jobs --jq '.jobs[] | {name, conclusion}'
{"conclusion":"success","name":"vendor-bundle"}
{"conclusion":"success","name":"test (3.12)"}
{"conclusion":"success","name":"image"}
```

Matches CONTEXT.md's D-11 specifics exactly: the push run of `b72b0e1`, three jobs, all
green.

## Verification

`make verify` (ruff, mypy `--strict`, import boundaries, unfinished-work scan, pytest):
191 passed in 32-37s, run after each task's commit and once more at plan end.

Plan-level `<verification>` checks, all passing:
- Each of the three offline reports produced by its own case; the commit-read failure
  reported as the last error; the happy path never reads the commit (asserted via
  `not any("commits/" in " ".join(c) for c in runner.calls)`).
- The live probe gets the Actions link for `b72b0e1` and names `[ci skip]` for `20b63e4`.
- `grep -c 'reached main' scripts/pr_land.py`, `grep -c 'no ci.yml run appeared'
  tests/test_pr_land.py`, `grep -c 'no run appeared' docs/HOW_TO_DEVELOP.md` all `0`.
- The docstring and §8 contain `pins the head, not the base` / `--match-head-commit`; the
  old over-claims (`proven here`, `никогда не опирается`) are gone; the AST probe confirms
  the docstring-only diff.
- L25 present exactly once, in order after L22/L23/L24, zero lines deleted from the file.
- The fifth debt file is `Status: resolved` with `Resolved in:` naming Task 1's commit
  (not the retiring commit); its move and the docstring/§8/L25 change share one commit;
  `INDEX.md`'s Active table has zero rows for any of this phase's five files.
- STATE.md: exactly one `- ⚠` bullet (Phase 2), all five records named, run 36122394253
  cited.

## Files Created/Modified

- `scripts/pr_land.py` — new `no_run_report`; `land`'s poll loop tracks `last_error`; the
  final unobserved-run print calls `no_run_report`; module docstring states the D-07 split
- `tests/test_pr_land.py` — `SQUASH_COMMIT_READ` constant; `_happy_runner` gains a
  `commits/deadbeef1234` handler; the happy-path test asserts no commit read; four new
  tests; the old poll-timeout test removed
- `docs/HOW_TO_DEVELOP.md` — §8's unobserved-run paragraph replaced with guidance for the
  three reports; the «Стена и инструмент» paragraph states the D-07 split
- `docs/architecture/decision_log.md` — new `## L25` appended after L24, amending L22
- `docs/tech_debt/active/2026-09-25-pr-land-blames-a-skip-token-for-any-missed-post-merge-run.md`
  → `docs/tech_debt/resolved/...` — `git mv`'d, `Status: resolved`,
  `Resolved in: e4345a4`, `## Resolution (2026-09-25)` appended, the trailing on-resolve
  comment removed
- `docs/tech_debt/INDEX.md` — the row moved from `## Active` to `## Resolved`
- `.planning/STATE.md` — Blockers/Concerns: the Phase 5 hook bullet retired, all five
  Phase 6 records named, run 36122394253 cited

## Decisions Made

- `no_run_report`'s precedence when a commit-read failure and a prior poll `last_error`
  could both apply (a case no plan test exercises): the commit-read failure's own text
  wins, since it is the read attempted most recently and directly explains why no token
  search could happen. See key-decisions in the frontmatter.
- The token report's wording deliberately avoids the literal phrase "reached main" (the
  plan's own acceptance criterion requires `grep -c 'reached main' scripts/pr_land.py` to
  print `0`) even though a token genuinely did reach `main` — chose "...in the squash
  commit's message -- a regression of L22" instead. See key-decisions in the frontmatter.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Task 2's commit initially landed with only the renamed debt file**
- **Found during:** Task 2 (staging before commit)
- **Issue:** `git add scripts/pr_land.py docs/HOW_TO_DEVELOP.md
  docs/architecture/decision_log.md docs/tech_debt/active/<old-path>
  docs/tech_debt/resolved/<new-path> docs/tech_debt/INDEX.md` included a stale
  `active/` pathspec left over from before `git mv` (the file had already moved to
  `resolved/`). Git's multi-pathspec `add` is all-or-nothing on a pathspec match failure:
  the whole invocation aborted with `fatal: pathspec ... did not match any files`, and
  none of the six paths were staged — only the rename `git mv` had already staged
  remained. The resulting commit had exactly 1 file changed instead of the 5 the plan's
  own acceptance criteria require in one commit.
- **Fix:** Re-staged the four missing files with valid pathspecs, then `git commit
  --amend` (the commit was local-only, unpushed, sole-authored, and the plan's own
  acceptance checks require these five changes in the single commit that moves the debt
  file — splitting into two commits would permanently break the `git log -1 --format=%H
  -- <resolved-file>` lookup those checks depend on).
- **Files modified:** none beyond what Task 2 already touched — the amend added the
  missing staged content, not new changes.
- **Verification:** `git show --stat --format= HEAD` after the amend lists all 5 expected
  files; all four of Task 2's `<verify>` shell probes re-run and passed; `make verify`
  green.
- **Committed in:** `e91d7de` (the corrected Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 blocking staging issue, caught before any push)
**Impact on plan:** No scope creep; the fix restores the single-commit shape the plan's
own acceptance criteria require.

## Issues Encountered

None beyond the staging issue documented above as a deviation.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- D-01, D-06, D-07, D-10, and D-11 are complete. Combined with Plans 06-01, 06-02, and
  06-03, all five of this phase's tech-debt records (three `must`, two `nice`) are
  `Status: resolved`, `git mv`'d into `docs/tech_debt/resolved/`, with `INDEX.md` rows
  moved — `docs/tech_debt/INDEX.md`'s `## Active` table now lists only the six items
  outside this phase's scope (the waived-latency-bar `must` and five unrelated `nice`
  items).
- `make verify` passes (191 tests) at HEAD (`9aa7a06`).
- This was the last plan in Phase 6 per `06-CONTEXT.md`'s wave structure (waves 1-4,
  plans 06-01 through 06-04) — ready for phase-level verification (`/gsd-verify-work 6`)
  and, if that passes, `/gsd-ship`.

---
*Phase: 06-address-tech-debt-merge-gate-solid-cache*
*Completed: 2026-09-25*

## Self-Check: PASSED

- `.planning/phases/06-address-tech-debt-merge-gate-solid-cache/06-04-SUMMARY.md` exists
  on disk (this file).
- Commits `e4345a4`, `e91d7de`, and `9aa7a06` found in `git log --oneline --all`.
- All three task commits' post-commit acceptance-criteria checks re-run and passed
  (documented above and in-session).
- `make verify` exits 0 at HEAD (`9aa7a06`), 191 tests passing.
