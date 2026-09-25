---
phase: 05-ci-observed-green
plan: 06
subsystem: ci-merge-gate
tags: [skip-tokens, pr-land, commit-msg-hook, tdd, tech-debt]

# Dependency graph
requires:
  - phase: 05-01
    provides: "The commit-msg hook and `scripts/skip_tokens.py`'s `find_skip_tokens`/`message_to_check`/`main`, shared by both checks (D-02)"
  - phase: 05-02
    provides: "`make pr.land` and `scripts/pr_land.py`'s `message_refusals`, the squash-message check this plan closes the gap in"
provides:
  - "`find_skip_tokens` searches the whole text it is given, no cut -- the cut moved into the hook's own `main()`"
  - "`message_refusals` (code unchanged) now sees the whole PR title and body: a skip token behind a forged git cut line is refused"
  - "The commit-msg hook cuts at a line shaped like git's `commit -v` marker only when `GIT_EDITOR` is not `:` (i.e. git ran an editor) -- closing the `-m`/`-F` hole CR-01 found"
  - "The one residual no content check can see -- a hand-typed cut line inside an editor session without `-v` -- filed as `must` debt with its backstops and two closing options"
affects: []

# Actuals (#2632)
actuals:
  tokens: 5282
  tasks: 2
  commits: 2
plan_head_before: 175004e5f15977ddfce8a1e68b886ecdc091a2e7

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "A pure text-search function stays cut-free; the one caller whose text passed through an untrusted transport (git's editor buffer) applies its own domain-specific truncation before calling it, rather than the search assuming everyone's input needs the same cut"

key-files:
  created:
    - docs/tech_debt/active/2026-09-25-commit-msg-hook-trusts-a-hand-typed-cut-line.md
  modified:
    - scripts/skip_tokens.py
    - scripts/pr_land.py
    - tests/test_skip_tokens.py
    - tests/test_pr_land.py
    - docs/tech_debt/INDEX.md

key-decisions:
  - "The cut becomes the hook's own step (`main`), not the search's (`find_skip_tokens`) -- `pr_land.py`'s code does not change; only its `message_refusals` docstring explains why no cut applies to PR text (Decision (a), plan objective)"
  - "The hook trusts the cut line only when `GIT_EDITOR` is not `:` (git ran an editor), closing `-m`/`-F` while leaving `git commit -v`'s real diff shape untouched; verified live by a scratch-repo probe (this git version) before and after the fix, and by two real pre-commit hook runs (refused with no editor, passed with one) (Decision (b), plan objective)"
  - "The residual an editor session without `-v` in which the cut line is hand-typed is filed as `must` debt rather than closed here -- content alone cannot distinguish it from git's own cut line, and it is already backstopped by the ruleset on `main`, `make pr.land`'s run check, and D-03 (no branch commit's message ever becomes `main`'s)"

requirements-completed: [REQ-ci-verified]

coverage:
  - id: D1
    description: "`message_refusals` (and `find_skip_tokens`) refuse the verifier's exact reproduction -- a PR body carrying a line identical to git's cut line followed by a skip token -- which previously passed with zero refusals"
    requirement: "REQ-ci-verified"
    verification:
      - kind: unit
        ref: "tests/test_pr_land.py#test_message_refusals_checks_the_whole_body_even_below_a_git_cut_line"
        status: pass
      - kind: unit
        ref: "tests/test_skip_tokens.py#test_find_skip_tokens_searches_the_whole_text_it_is_given"
        status: pass
      - kind: other
        ref: ".venv/bin/python -c \"...find_skip_tokens/message_refusals reproduction...\" (exits 0, prints ['[skip ci]'] and the one-element refusal list)"
        status: pass
    human_judgment: false
  - id: D2
    description: "`land()` refuses that PR end to end -- prints the refusal and 'nothing was merged', returns 1, and makes no `gh pr merge` call"
    requirement: "REQ-ci-verified"
    verification:
      - kind: unit
        ref: "tests/test_pr_land.py#test_land_refuses_a_token_hidden_below_a_git_cut_line_in_the_pr_body"
        status: pass
    human_judgment: false
  - id: D3
    description: "The commit-msg hook cuts at git's marker only when git ran an editor -- a real `git commit -m` hiding a token below a hand-written cut line is refused and HEAD does not move; `git commit -v`'s real diff shape still passes in an editor session"
    requirement: "REQ-ci-verified"
    verification:
      - kind: unit
        ref: "tests/test_skip_tokens.py#test_hook_without_an_editor_refuses_a_token_below_a_cut_line"
        status: pass
      - kind: unit
        ref: "tests/test_skip_tokens.py#test_token_only_below_the_scissors_line_gives_no_tokens (parametrised git_editor=vi,None)"
        status: pass
      - kind: other
        ref: "GIT_EDITOR=: pre-commit run --hook-stage commit-msg (refused, prints '[skip ci]'); GIT_EDITOR=vi pre-commit run --hook-stage commit-msg (passed the real -v diff shape); a real `git commit --allow-empty -m` with a hand-written cut line, refused, HEAD unchanged"
        status: pass
    human_judgment: false
  - id: D4
    description: "The residual (a hand-typed cut line in a non--v editor session) is filed as `must` debt with its INDEX row, its backstops, and both closing options"
    requirement: "REQ-ci-verified"
    verification:
      - kind: other
        ref: "docs/tech_debt/active/2026-09-25-commit-msg-hook-trusts-a-hand-typed-cut-line.md exists, Severity: must, Status: active, has a Next step; docs/tech_debt/INDEX.md has its Active row"
        status: pass
    human_judgment: false

duration: ~13min
completed: 2026-09-25
status: complete
---

# Phase 5 Plan 6: Close the pr.land Cut-Line Skip-Token Bypass Summary

`find_skip_tokens` now searches the whole text it is given with no cut; the commit-msg
hook applies the cut itself, and only when git actually ran an editor -- closing the one
blocking gap (CR-01) the phase verifier found in `make pr.land`'s squash-message check.

## Performance

- **Duration:** ~13 min
- **Tasks:** 2/2 completed
- **Files modified:** 5 (1 created: the debt file; 4 modified: `scripts/skip_tokens.py`,
  `scripts/pr_land.py`, `tests/test_skip_tokens.py`, `tests/test_pr_land.py`, plus
  `docs/tech_debt/INDEX.md`)
- **Commits:** 2 task commits (measured: `git rev-list --count
  175004e..HEAD` = 2)

## Accomplishments

- `scripts/pr_land.py`'s `message_refusals()` now catches the verifier's exact
  reproduction: a PR body containing a line identical to git's `commit -v` cut line,
  followed by `[skip ci]`, is refused (one refusal naming the token) instead of passing
  silently. `pr_land.py`'s code did not change -- only its docstring.
- `land()` refuses that PR end to end, offline: prints the refusal and `nothing was
  merged`, returns 1, and makes zero `gh pr merge` calls -- proven by a new whole-path
  test built the same way the existing several-problems test is (values, not shape).
- The commit-msg hook now reads past a hand-written cut line whenever git ran no editor
  (`-m`, `-F`), closing the `-m`/`-F` half of CR-01, while still ignoring `git commit
  -v`'s real staged diff below the line in an editor session -- proven by a parametrised
  unit test and by two live `pre-commit run --hook-stage commit-msg` invocations (one
  refused, one passed) plus a real, refused `git commit -m` whose HEAD did not move.
- The one shape neither check can see -- a cut line typed by hand inside an editor
  session without `-v` -- is filed as `must` debt with the probe table, both ways to
  close it and their costs, and the backstops (the ruleset on `main`, `make pr.land`'s
  run check, and D-03) that already catch its consequence.

## Task Commits

Both tasks landed RED and GREEN in one commit each -- this project's pre-commit hook
runs the full `make verify` with no bypass, so a separate failing-only commit cannot
land (the same constraint Phase 3 documented: `03-02-SUMMARY.md`'s "Issues Encountered").
Each commit message states the RED-then-GREEN sequence it followed in prose.

1. **Task 1: End to end -- `make pr.land` refuses a PR body that hides a skip token
   below a line identical to git's cut line** - `1965a52` (fix)
2. **Task 2: The commit-msg hook trusts git's cut line only when git ran an editor;
   the residual is filed as debt** - `3e68e74` (fix)

**Plan metadata:** commit follows this SUMMARY.

## TDD Gate Compliance

Both tasks carried `tdd="true"`. RED evidence was captured and verified before each
GREEN implementation, but landed in the same commit as GREEN (no standalone
`test(05-06): ...` commit exists in the git log) -- the pre-commit hook's `make verify`
with no bypass makes a separate, intentionally-failing commit impossible in this
project, exactly as Phase 3 and Phase 5's own prior plans (05-01) established. This is a
project-wide, previously documented deviation from the RED-commit/GREEN-commit split,
not new to this plan.

- **Task 1 RED** (`make test PYTEST_ARGS="tests/test_pr_land.py tests/test_skip_tokens.py -q"`,
  before the fix): `3 failed, 74 passed` --
  `test_message_refusals_checks_the_whole_body_even_below_a_git_cut_line` (`assert 0 == 1`),
  `test_land_refuses_a_token_hidden_below_a_git_cut_line_in_the_pr_body`
  (`AssertionError: FakeRunner: no handler registered for ['gh', 'pr', 'merge', ...]` --
  it merged instead of refusing), `test_find_skip_tokens_searches_the_whole_text_it_is_given`
  (`assert [] == ['[skip ci]']`). The two re-pointed hook tests
  (`test_token_only_below_the_scissors_line_gives_no_tokens`,
  `test_token_above_and_below_the_scissors_line_is_found_once`) passed unmodified before
  the fix, as intended -- they pin behaviour that must not change.
  Reproduction before the fix: `find_skip_tokens(body)` returned `[]`;
  `message_refusals('safe subject', body)` returned `[]` (05-VERIFICATION.md's own
  `[] []` finding, re-confirmed live during planning).
- **Task 1 GREEN**: `make test PYTEST_ARGS="tests/test_pr_land.py tests/test_skip_tokens.py -q"`
  -> `77 passed`. Reproduction after the fix: `find_skip_tokens(body)` returns
  `['[skip ci]']`; `message_refusals('safe subject', body)` returns one refusal naming
  `'[skip ci]'`.
- **Task 2 RED** (`make test PYTEST_ARGS="tests/test_skip_tokens.py -q"`, before the fix):
  `1 failed, 26 passed` -- `test_hook_without_an_editor_refuses_a_token_below_a_cut_line`
  (`AssertionError: assert 0 == 1` -- the hook still cut unconditionally and let the
  `-m`-shaped token through).
- **Task 2 GREEN**: `make test PYTEST_ARGS="tests/test_skip_tokens.py tests/test_pr_land.py -q"`
  -> `79 passed`. `git --version` on the executing machine: `git version 2.54.0` (matches
  the planning probe). The scratch-repo probe (`<verify>` block 1) reconfirmed both rows
  live before trusting the new comment's facts: `git commit -m` with a hand-written cut
  line kept the token past it; `git -c commit.verbose=true commit -m` with the same
  message truncated at the line -> `PROBE-OK`.

## Files Created/Modified

- `scripts/skip_tokens.py` - `find_skip_tokens` searches the whole text (no cut);
  `main()` cuts via `message_to_check` only when `os.environ.get("GIT_EDITOR") != ":"`;
  module docstring and `_SCISSORS` comment rewritten to match
- `scripts/pr_land.py` - `message_refusals` docstring only (code unchanged): explains
  why no cut applies to PR text
- `tests/test_skip_tokens.py` - `test_find_skip_tokens_searches_the_whole_text_it_is_given`
  (new); `test_token_only_below_the_scissors_line_gives_no_tokens` and
  `test_token_above_and_below_the_scissors_line_is_found_once` re-pointed at `main([path])`
  and parametrised/set over `GIT_EDITOR`; `test_hook_without_an_editor_refuses_a_token_below_a_cut_line`
  (new)
- `tests/test_pr_land.py` - `CUT_LINE_BODY` constant (the verifier's reproduction);
  `test_message_refusals_checks_the_whole_body_even_below_a_git_cut_line` and
  `test_land_refuses_a_token_hidden_below_a_git_cut_line_in_the_pr_body` (new)
- `docs/tech_debt/active/2026-09-25-commit-msg-hook-trusts-a-hand-typed-cut-line.md` -
  new, `Severity: must`, `Status: active`
- `docs/tech_debt/INDEX.md` - one new row under `## Active`

## Decisions Made

See `key-decisions` in frontmatter. No decision-log entry was added: L22 already says
the hook refuses tokens "above git's `commit -v` scissors line" and that
`message_refusals` reuses `find_skip_tokens` "unmodified" -- both stay true after this
plan (the log is append-only; the implementation now does what L22 already said).

## Deviations from Plan

None - plan executed exactly as written. Both tasks' `<verify>` blocks, including the
live scratch-repo git probe and the two real pre-commit hook invocations, ran and passed
without needing any Rule 1-3 auto-fix.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Phase 5's one blocking gap (05-VERIFICATION.md, CR-01) is closed: `make pr.land`
refuses a skip token anywhere in the squash subject or body with no cut, and the
commit-msg hook reads the whole message whenever git ran no editor. `REQ-ci-verified`
is now satisfiable end to end on both paths onto `main`. One residual (a hand-typed cut
line inside an editor session without `-v`) is intentionally left open as `must` debt,
backstopped by the ruleset on `main`, `make pr.land`'s run check, and D-03 -- not a
blocker for phase completion. Phase 5 is ready for re-verification.

## Self-Check: PASSED

All six files created/modified this plan found on disk; both task commits (`1965a52`,
`3e68e74`) found in `git log --oneline --all`.

---
*Phase: 05-ci-observed-green*
*Completed: 2026-09-25*
