---
phase: 17-debt-first-commit-gate-and-pool-race
plan: 02
subsystem: infra
tags: [pre-commit, git-hooks, gsd-sdk, commit-timeout, upstream-issue, gate]

requires:
  - phase: 17-debt-first-commit-gate-and-pool-race
    provides: "17-01's hook commit c06749d: verify-fast at pre-commit, verify at pre-push, three installed hook types, L36"
provides:
  - "SC1: the first live gsd SDK commit on this repository returned committed: true in 13.57 s, with the hooks installed"
  - "the whole make verify proved as a real pre-push hook (937 passed, hook Passed, 63.97 s)"
  - "a fresh --depth 1 clone installs all three hook types (macOS only; the Linux CI read is carried to ship)"
  - "open-gsd/gsd-core#5231: the request for a configurable COMMIT_TIMEOUT_MS, posted from the text the human approved"
  - "the commit-timeout debt names its fixing commit's sha c06749d in Resolved in:, INDEX and L36's closing paragraph"
affects: [17-03, 17-04, 17-05, every later commit of the milestone, ship (A1/A3 CI read)]

actuals:
  tokens: 4600
  tasks: 3
  commits: 1

tech-stack:
  added: []
  patterns:
    - "A gate that outlives a tool's commit window is split: a sub-30 s prefix at commit, the whole gate at push"
    - "An external write in the user's name is posted from a file the human read, unchanged, and the file is kept as the record"

key-files:
  created:
    - .planning/phases/17-debt-first-commit-gate-and-pool-race/17-02-upstream-issue.md
    - .planning/phases/17-debt-first-commit-gate-and-pool-race/17-02-sdk-commit.json
  modified:
    - docs/architecture/decision_log.md
    - docs/tech_debt/resolved/2026-09-25-gsd-commit-timeout-kills-cold-verify-hook.md
    - docs/tech_debt/INDEX.md

key-decisions:
  - "The upstream request is a new issue, not a comment: no open issue asks for a configurable commit timeout (only #3886, closed)"
  - "The human approved the draft unchanged (answer: approved), so it was posted byte-identical"

requirements-completed: [REQ-hook-and-commit-timeout-decided]

plan_head_before: 91204d3b3f33d18792557d3eea48ec7617061c76
plan_head_after: 5a3332f15582bc891f7a28a7508eb884eb1bfc19

coverage:
  - id: D1
    description: "One live gsd SDK commit on this repository returned committed: true with a hash that is HEAD, inside 30 s, nobody committing by hand (SC1)"
    requirement: REQ-hook-and-commit-timeout-decided
    verification:
      - kind: other
        ref: "17-02-sdk-commit.json (committed true, hash 5a3332f) checked by Task 3's first automated python check against git log; real 13.57 s"
        status: pass
    human_judgment: false
  - id: D2
    description: "The whole make verify passed as a real pre-push hook (explicit make verify first, then a push to an empty scratch bare repo, no --no-verify, no SKIP)"
    requirement: REQ-hook-and-commit-timeout-decided
    verification:
      - kind: other
        ref: "git push to a scratch bare repo: 'make verify (ruff, mypy, import boundaries, unfinished-work scan, pytest)....Passed', '[new branch] HEAD -> probe', real 63.97"
        status: pass
    human_judgment: false
  - id: D3
    description: "pre-commit install in a fresh --depth 1 clone installs commit-msg, pre-commit and pre-push (macOS; Linux CI read left to ship)"
    requirement: REQ-hook-and-commit-timeout-decided
    verification: []
    human_judgment: true
    rationale: "Assumptions A1 and A3 are about GitHub's Linux runner; this host is macOS. The check on a shallow clone is evidence, not the proof; the first CI run read at ship closes it."
  - id: D4
    description: "The debt's Resolved in:, its INDEX cell and L36's closing paragraph carry the hook commit's short sha c06749d, the two proofs and the issue URL"
    requirement: REQ-hook-and-commit-timeout-decided
    verification:
      - kind: other
        ref: "Task 3's second automated python check: 'sha c06749d recorded in the debt, INDEX and L36'"
        status: pass
    human_judgment: false
  - id: D5
    description: "The upstream request was shown to the human, approved unchanged, and filed as open-gsd/gsd-core#5231"
    requirement: REQ-hook-and-commit-timeout-decided
    verification:
      - kind: other
        ref: "gh issue view 5231 --repo open-gsd/gsd-core -> OPEN, title equals the approved file's title line"
        status: pass
    human_judgment: false

duration: 10min
completed: 2026-10-06
status: complete
---

# Phase 17 Plan 02: Proofs after the hook commit Summary

**gsd's own SDK commit returned `committed: true` in 13.57 s under the new hook (SC1), after the whole gate passed as a real pre-push hook, a shallow clone installed all three hooks, and the upstream request for a configurable `COMMIT_TIMEOUT_MS` was filed as open-gsd/gsd-core#5231 from text the human approved.**

## Performance

- **Duration:** about 10 min across two executor sessions (checkpoint between them); `.git/gsd-plan-head-before-17-02` written 09:06Z
- **Started:** 2026-10-06T09:06:11Z
- **Completed:** 2026-10-06T09:16Z
- **Tasks:** 3 (Task 1 commits nothing; Task 2 is the human checkpoint; Task 3 is the one SDK commit)
- **Files modified:** 3 tracked docs paths in the SDK commit, plus 2 new `.planning/` records

## Accomplishments

- SC1 met. `node "$HOME/.claude/gsd-core/bin/gsd-tools.cjs" query commit ...` on this repository, hooks installed, returned `{"committed": true, "hash": "5a3332f", "reason": "committed"}`; `git log -1` is `5a3332f15582bc891f7a28a7508eb884eb1bfc19`. Nobody committed by hand.
- The pre-push stage proved on the real gate (readings below); the three-hook install proved on a fresh shallow clone.
- Upstream request filed; the debt names `c06749d`; L36 ends with the dated closing paragraph.

### Task 1 readings (taken by the previous executor, carried verbatim)

- `make verify` before the push: exit 0, `937 passed in 61.19s`, `Required test coverage of 96.0% reached. Total coverage: 97.24%`, `real 61.97`.
- Real pre-push hook, push to an empty scratch bare repo (no `--no-verify`, no `SKIP=`): `make verify (ruff, mypy, import boundaries, unfinished-work scan, pytest).......................Passed`, ` * [new branch]      HEAD -> probe`, `real 63.97`. Scratch directory removed.
- `--depth 1` clone of this branch at `91204d3`: `pre-commit install` printed `pre-commit installed at .git/hooks/pre-commit`, `.../commit-msg`, `.../pre-push`; `ls .git/hooks` showed all three. This is a macOS shallow clone, not GitHub's Linux runner: assumptions A1 and A3 stay open until the phase's first CI run, whose `make verify` step log is read at ship and carried into 17-05's SUMMARY. Clone removed.
- `gh search issues "COMMIT_TIMEOUT_MS"` in open-gsd/gsd-core (open and closed): `[]`. `gh search issues "commit timeout"`: only #3886 (closed, "query commit: git commit timeout misreported as commit_failed, leaves stale .git/index.lock"). No open issue asks for a configurable timeout, so a new issue rather than a comment. Installed gsd-core 1.16.0 has `const COMMIT_TIMEOUT_MS = 30_000;` shared by three commit sites and no config key reads it.
- The plan's automated check on the draft passed (names `COMMIT_TIMEOUT_MS`, `commands.cjs`, #3886, `commit_timeout`, PID 1, 1.16.0; no local path, user name, line number or token).

### Task 2: the human's answer, verbatim

`approved`

Per the plan's resume options that means: post `17-02-upstream-issue.md` unchanged. Before the answer, `git diff --quiet HEAD -- docs` was clean and nothing was posted or committed.

### Task 3: the request, the record, SC1

- **Issue:** https://github.com/open-gsd/gsd-core/issues/5231, filed 2026-10-06 (`date -u +%F`) with `gh issue create --repo open-gsd/gsd-core --title <line 1 after "Title: "> --body-file <the file from line 3>`. The draft's sha1 before posting was `d4c6a67d9e7c55923912724733bc0d38f151df27` (`shasum`, unchanged file). `gh issue view 5231` reads OPEN with the same title.
- **Record:** L36 gains `**Recorded after this entry's commit (2026-10-06).**` (hook sha `c06749d`, its 12.33 s real through its own commit stage, the pre-push proof, the shallow-clone install and its macOS caveat, the issue URL and date, and that the paragraph rides gsd's own SDK commit). The debt file's `Resolved in:` is now `c06749d`; its INDEX cell is `` `c06749d` — see the file's own `Resolved in:` field ``.
- **SC1 command:** `/usr/bin/time -p node "$HOME/.claude/gsd-core/bin/gsd-tools.cjs" query commit "docs(17-02): record the hook commit's sha, the pre-push proof and the upstream request" --files docs/architecture/decision_log.md docs/tech_debt/resolved/2026-09-25-gsd-commit-timeout-kills-cold-verify-hook.md docs/tech_debt/INDEX.md`
- **SDK JSON** (stored byte for byte in `17-02-sdk-commit.json`): `{"committed": true, "hash": "5a3332f", "reason": "committed"}`
- **Timing:** `real 13.57`, `user 48.31`, `sys 27.74` (stderr). Under the SDK's 30 s kill with 16 s of headroom; 17-01's warm `verify.fast` readings were 11.3 s.
- **Hook output:** the SDK returns only its JSON, so the hook's own `Passed` lines were not surfaced for this commit. That the commit stage ran is shown by the timing (13.57 s real, 48 s of user CPU, consistent with `pytest -n 8` over the 620-test slice, against well under 1 s for a hook-less commit) and by the commit existing: a red hook would have aborted it. `pgrep -fl 'pre_commit hook-impl|pytest|mypy'` printed nothing before the commit. This is inference, not a captured line; no additional measurement was made.
- **Verification:** both automated checks of Task 3 printed `SC1: the SDK committed 5a3332f` and `sha c06749d recorded in the debt, INDEX and L36`. The commit carries exactly the three docs paths.

## Task Commits

1. **Task 1: pre-push proof, shallow-clone install, upstream draft** - nothing committed by design
2. **Task 2: human reads the upstream text** - checkpoint, no commit
3. **Task 3: issue filed, sha and proofs recorded** - `5a3332f` (docs), the phase's first SDK commit

**Plan metadata:** the closing `docs(17-02)` commit of SUMMARY, the draft, the SDK JSON, STATE.md and ROADMAP.md (made after this file; not counted in `commits:` above, which was measured before it).

## Files Created/Modified

- `docs/architecture/decision_log.md` - L36's closing paragraph (append-only)
- `docs/tech_debt/resolved/2026-09-25-gsd-commit-timeout-kills-cold-verify-hook.md` - `Resolved in: c06749d`
- `docs/tech_debt/INDEX.md` - the Resolved row's sha cell
- `.planning/phases/17-debt-first-commit-gate-and-pool-race/17-02-upstream-issue.md` - the approved and posted text
- `.planning/phases/17-debt-first-commit-gate-and-pool-race/17-02-sdk-commit.json` - the SDK's own result

## Decisions Made

None beyond the plan: new issue not a comment (search result above), approved text posted unchanged. No new `Lxx`.

## Deviations from Plan

**1. [Rule 3 - Blocking] `gsd_run` is not on PATH**
- **Found during:** the continuation start
- **Issue:** the plan and agent text call `gsd_run`; it is not on PATH in the executor shell (same as 17-01).
- **Fix:** every gsd-tools call used `node "$HOME/.claude/gsd-core/bin/gsd-tools.cjs"` directly, as the dispatcher instructed. The SC1 command itself is the plan's own `node` form.
- **Files modified:** none.

**Total deviations:** 1 (blocking, tooling path only). **Impact on plan:** none; SC1 was met on the first attempt, so D-07's recovery never ran. No `committed: false` occurred, no hand commit was made, and 17-03 may start.

## Issues Encountered

- The SDK commit does not surface the hook's output (see Task 3), so the SUMMARY carries the hook's pass as inference from timing and the commit's existence, labelled as such.
- A1 and A3 (GitHub's Linux runner installs and runs the hooks as expected) are not closed by this plan: the shallow clone ran on macOS. Carried to the phase's first CI run, read at ship, recorded in 17-05's SUMMARY.
- Stale prose, for the phase transition (the plan asks this be noted, not edited here): the ROADMAP "Process Notes" sentence and STATE.md's "Operator Next Steps" line that say every commit must be a plain `git commit` are stale from `5a3332f` on. From here every commit of the phase may use `node "$HOME/.claude/gsd-core/bin/gsd-tools.cjs" query commit`, with D-07 as the only recovery.
- `.planning/state.json` and `.planning/milestone.lock` were already modified or untracked at the start (tooling artifacts) and are deliberately not staged.

## User Setup Required

None - no external service configuration required.

## Known Stubs

None.

## Threat Flags

None. T-17-05 (disclosure in the public issue): the verify refused local paths, the user name, line numbers and token prefixes, the human read the text, and it was posted unchanged. T-17-06 (blind retry): not triggered, the SDK commit succeeded first time. T-17-07 (faked SC1): the JSON's hash `5a3332f` is the commit that last touched INDEX, with the planned subject and exactly the three paths.

## Next Phase Readiness

Ready for 17-03 (the ten-identical-worst-row scenario). SC1 is met, so the phase's later commits may use the SDK commit. Open for ship: the Linux CI read of A1/A3, and issue #5231 stays open upstream (cited, never depended on).

## Self-Check: PASSED

- FOUND: 17-02-upstream-issue.md, 17-02-sdk-commit.json, docs/architecture/decision_log.md (closing paragraph), the resolved debt file
- FOUND: commit 5a3332f (ancestor of HEAD); `git rev-list --count 91204d3..HEAD` = 1 at write time
- FOUND: https://github.com/open-gsd/gsd-core/issues/5231 (OPEN)

---
*Phase: 17-debt-first-commit-gate-and-pool-race*
*Completed: 2026-10-06*
