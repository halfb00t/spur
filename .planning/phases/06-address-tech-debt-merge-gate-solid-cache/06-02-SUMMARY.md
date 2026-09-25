---
phase: 06-address-tech-debt-merge-gate-solid-cache
plan: 02
subsystem: ci-merge-gate
tags: [pre-commit, commit-msg-hook, skip-tokens, tdd, pytest, tech-debt, docs]

# Dependency graph
requires: []
provides:
  - "`scripts/skip_tokens.py::main` hands `find_skip_tokens` the whole commit-msg buffer git gives it, in every commit mode -- no cut, no read of `GIT_EDITOR`"
  - "Every refusal names each matched token with its 1-based buffer line, plus one sentence telling a `git commit -v` author to commit without `-v`"
  - "`tests/test_skip_tokens.py`'s regardless-of-`GIT_EDITOR` refusal, the `-v`-diff refusal with the caveat, and the both-lines-named case"
  - "`docs/HOW_TO_DEVELOP.md` §6 carries the same `-v` caveat in Russian"
  - "`docs/tech_debt/active/2026-09-25-commit-msg-hook-trusts-a-hand-typed-cut-line.md` retired to `resolved/`, INDEX row moved"
affects: []

# Actuals (#2632) -- pairs with the plan's `estimate` to calibrate future estimates.
actuals:
  tokens: 5529
  tasks: 2
  commits: 4

# Commit ledger (#3968) -- measured, not narrated: git rev-list --count
# plan_head_before..HEAD at SUMMARY-write time. 4, not 2 tasks, because the
# metadata commit itself needed two attempts (see "Issues Encountered").
commits: 4
plan_head_before: 528c64f451bf494541d1515780c87394b6a272b6

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "1-based buffer line for each matched token found by walking `raw` with `str.index` from the end of the previous match -- an earlier occurrence of the same token text is never mistaken for the current match's start, because `find_skip_tokens` already returns matches in order of appearance, non-overlapping"
    - "A scratch clone (`git clone .`, a symlinked `.venv`, a `GIT_EDITOR` script copying a prepared message) as the only way to prove an editor-session commit-msg hook behavior end to end -- pytest's `main([path])` calls exercise the function directly, never through git's own editor-invocation contract"

key-files:
  created: []
  modified:
    - scripts/skip_tokens.py
    - tests/test_skip_tokens.py
    - tests/test_pr_land.py
    - docs/HOW_TO_DEVELOP.md
    - "docs/tech_debt/active/2026-09-25-commit-msg-hook-trusts-a-hand-typed-cut-line.md -> docs/tech_debt/resolved/2026-09-25-commit-msg-hook-trusts-a-hand-typed-cut-line.md (git mv)"
    - docs/tech_debt/INDEX.md

key-decisions:
  - "Two of the renamed/new test fixtures were built with the cut line immediately after the subject line (no blank line) rather than literally reusing the prior test's blank-line spacing -- the plan's own `<behavior>` block specifies `line 4` for the D-02 case and `line 1`/`line 4` for the both-lines case; computed against the actual message text (verified with a throwaway Python snippet), the blank line pushes the second token to line 5, not line 4. Removing the blank line satisfies the plan's stated line numbers without changing what the test proves (a token above and a token below a cut line, both named)."

requirements-completed: [D-01, D-02, D-03]

coverage:
  - id: D1
    description: "An editor-session commit hiding a skip token below a hand-typed cut line is refused at `git commit`, in every commit mode (`vi`, unset, `:`), and HEAD does not move"
    requirement: D-02
    verification:
      - kind: unit
        ref: "tests/test_skip_tokens.py#test_hook_refuses_a_token_below_a_git_cut_line_whatever_git_editor_says"
        status: pass
      - kind: integration
        ref: "scratch-clone probe (mktemp -d clone, GIT_EDITOR script, `SKIP=verify git commit --allow-empty`) -- refused, HEAD unmoved, recorded live in this file's Task 1 verification section"
        status: pass
    human_judgment: false
  - id: D2
    description: "A `git commit -v`-shaped buffer whose appended diff names a token is refused, naming the line and telling the author to commit without `-v`"
    requirement: D-03
    verification:
      - kind: unit
        ref: "tests/test_skip_tokens.py#test_hook_refuses_a_token_in_the_appended_commit_v_diff_and_says_to_commit_without_v"
        status: pass
      - kind: integration
        ref: "real `pre-commit run --hook-stage commit-msg` against a `-v`-shaped buffer -- refused, `line 6: '[skip ci]'` and `commit without -v` both in stdout"
        status: pass
    human_judgment: false
  - id: D3
    description: "docs/HOW_TO_DEVELOP.md §6 documents the same `-v` caveat in Russian, containing the literal `git commit -v` and `без \\`-v\\``"
    requirement: D-03
    verification:
      - kind: other
        ref: "grep -qF 'git commit -v' and grep -qF 'без \\`-v\\`' docs/HOW_TO_DEVELOP.md, both confined to §6 by an awk section scan"
        status: pass
    human_judgment: false
  - id: D4
    description: "The hand-typed-cut-line debt file is retired (Status: resolved, Resolved in: Task 1's commit) and moved to resolved/ in the commit that adds §6's line; INDEX.md's row moves with it"
    requirement: D-01
    verification:
      - kind: other
        ref: "shell probe: Status/Resolved-in fields, git-history ancestor check (Task 1's commit is an ancestor of the moving commit's parent), ls-files shows only the resolved path tracked, INDEX.md links resolved/ and not active/"
        status: pass
    human_judgment: false

duration: 9min
completed: 2026-09-25
status: complete
---

# Phase 6 Plan 2: Commit-msg hook trusts no cut line, in any commit mode Summary

**The `no-skip-token` hook now searches the whole buffer git hands a commit-msg hook in every commit mode -- no cut, no `GIT_EDITOR` read -- naming each refused token's line and telling a `git commit -v` author to commit without it; the residual debt filed in Phase 5 is retired in the same commit that documents the caveat in `docs/HOW_TO_DEVELOP.md`.**

## Performance

- **Duration:** 9 min
- **Started:** 2026-09-25T12:22:31Z
- **Completed:** 2026-09-25T12:31:50Z
- **Tasks:** 2
- **Files modified:** 6 (one via `git mv`)

## Accomplishments

- `scripts/skip_tokens.py::main` drops the `_SCISSORS` regex, `message_to_check`, and the
  `os.environ.get("GIT_EDITOR")` read entirely -- `find_skip_tokens(raw)` runs against the
  whole buffer, unconditionally, in every commit mode.
- Every refusal now names each matched token together with its 1-based buffer line
  (`line N: '<token>'`), and adds a sentence telling a `git commit -v` author whose
  appended staged diff names a token to commit without `-v`.
- A scratch-clone probe reproduced the exact editor-session shape that used to slip a
  token past the hook before this plan (commit succeeded, HEAD moved, token recorded) and
  confirmed the fix live: the same command is now refused and HEAD does not move.
- `docs/HOW_TO_DEVELOP.md` §6 carries the same `-v` caveat in Russian, immediately after
  the existing ship-note paragraph.
- `docs/tech_debt/active/2026-09-25-commit-msg-hook-trusts-a-hand-typed-cut-line.md` is
  retired (`Status: resolved`, `Resolved in: e46ed34`), `git mv`'d to `resolved/`, and
  `docs/tech_debt/INDEX.md`'s row moved -- in the commit that adds §6's line, per D-01.

## Task Commits

Each task was committed atomically:

1. **Task 1: End to end -- an editor-session commit that hides a skip token below a
   hand-typed cut line is refused at `git commit`, and every refusal names the line and
   the `-v` way out (D-02, D-03)** - `e46ed34` (fix, tracer -- RED and GREEN folded into
   one commit; the pre-commit hook runs `make verify` with no bypass, so a RED-only commit
   whose tests fail cannot land)
2. **Task 2: §6 carries the `-v` caveat in Russian, and the hand-typed-cut-line debt is
   retired in that commit (D-03, D-01)** - `d0c43ee` (docs)

**Plan metadata:** committed below, alongside this SUMMARY.

_Note: Task 1 is `type="tracer" tdd="true"` -- RED and GREEN are one commit, not two,
because the repository's own pre-commit hook runs the full `make verify` on every commit
with no bypass (documented in the plan's own action text, matching wave 1's 06-01 pattern)._

## RED Evidence (Task 1)

Before the `scripts/skip_tokens.py` change, `make test PYTEST_ARGS="tests/test_skip_tokens.py -q"`
failed 6 of 27 tests -- the three new/renamed cases against the unchanged hook, and one
existing subprocess case extended with a new assertion:

```
FAILED tests/test_skip_tokens.py::test_hook_refuses_a_token_below_a_git_cut_line_whatever_git_editor_says[vi]
FAILED tests/test_skip_tokens.py::test_hook_refuses_a_token_below_a_git_cut_line_whatever_git_editor_says[None]
FAILED tests/test_skip_tokens.py::test_hook_refuses_a_token_below_a_git_cut_line_whatever_git_editor_says[:]
FAILED tests/test_skip_tokens.py::test_hook_refuses_a_token_in_the_appended_commit_v_diff_and_says_to_commit_without_v
FAILED tests/test_skip_tokens.py::test_hook_names_a_token_above_and_below_a_cut_line_on_both_lines
FAILED tests/test_skip_tokens.py::test_hook_entry_exits_1_with_the_token_named_for_a_token_message
6 failed, 21 passed in 0.16s
```

Representative failure (the D-02 parametrized case, `vi`): `assert main([str(path)]) == 1`
raised `AssertionError: assert 0 == 1` -- the pre-fix hook cut at the hand-typed cut line
in an editor session and returned 0 (accepted) instead of refusing. The `-v`-diff case
failed the same way (`assert 0 == 1`); the both-lines case failed on
`assert out.count("'[skip ci]'") == 2` (`1 == 2`, only the above-cut-line token was
found); the subprocess case failed on the new `assert "line 1" in result.stdout` (no line
numbers existed yet). Each failure is the target assertion failing on real behavior, not
an import error, fixture crash, or unrelated test -- valid RED per `gsd-core/references/tdd.md`.

After the GREEN implementation, the same command passed all 27 (later confirmed at 185/185
under the full `make verify`).

## Scratch-Clone Probe (Task 1)

Recreated the exact shape from `docs/tech_debt/active/2026-09-25-commit-msg-hook-trusts-a-hand-typed-cut-line.md`'s
probe table (`safe subject`, blank line, git's cut line, `[skip ci]`, in an editor
session via a `GIT_EDITOR` script), against the working-tree fix, in a throwaway
`mktemp -d` clone:

```
H=b23fa70ffc74a4afec5b7f300619ede9b9fea11c
make verify (ruff, mypy, import boundaries, unfinished-work scan, pytest)......................Skipped
reject GitHub Actions skip tokens in the commit message.......................Failed
- hook id: no-skip-token
- exit code: 1

make: this commit message carries a GitHub Actions skip token:
      line 4: '[skip ci]'
      ...
      If a named line is in the diff `git commit -v` appends below the cut line, commit without -v -- this hook reads the whole message either way.
      See docs/tech_debt/resolved/2026-09-25-ship-note-skip-token-leaks-into-squash-merge.md.

commit rc=1
NEWH=b23fa70ffc74a4afec5b7f300619ede9b9fea11c
PROBE OK: HEAD unmoved
```

Before this plan's fix (per the debt record's own planning-time probe, run against the
same message and clone shape): the identical `SKIP=verify GIT_EDITOR="$E" git commit
--allow-empty` **succeeded**, the hook reported `Passed`, HEAD moved, and
`git log -1 --format=%B` kept the token. After: refused, `Failed`, HEAD unmoved -- the
exact reversal D-02 exists to produce.

The `-v`-shaped-buffer check ran through the real `pre-commit run --hook-stage commit-msg`
(not a scratch clone -- the message file alone is enough to exercise the hook stage):
refused, `line 6: '[skip ci]'` and `commit without -v` both present. A clean message still
passed (`Passed`, exit 0).

## Files Created/Modified

- `scripts/skip_tokens.py` - `main` no longer cuts; searches the whole buffer, names each
  token's line, adds the `-v` caveat sentence; `_SCISSORS`, `message_to_check`, and
  `import os` removed; `find_skip_tokens` and `SKIP_TOKEN` unchanged
- `tests/test_skip_tokens.py` - three cut-line/`-v`-diff tests new or renamed to assert
  refusal instead of acceptance; two obsolete cut-line tests and the `message_to_check`
  test deleted; two docstrings updated to say neither caller cuts
- `tests/test_pr_land.py` - one docstring updated to match the new shared premise (the
  hook no longer cuts either)
- `docs/HOW_TO_DEVELOP.md` - §6 gained one paragraph (Russian) documenting the `-v`
  caveat
- `docs/tech_debt/active/2026-09-25-commit-msg-hook-trusts-a-hand-typed-cut-line.md` ->
  `docs/tech_debt/resolved/...` - `git mv`'d, `Status: resolved`, `Resolved in: e46ed34`,
  `## Resolution (2026-09-25)` appended, the trailing on-resolve comment removed
- `docs/tech_debt/INDEX.md` - the row moved from `## Active` to `## Resolved`

## Decisions Made

- The both-lines test fixture (`test_hook_names_a_token_above_and_below_a_cut_line_on_both_lines`)
  and the D-02 parametrized fixture drop the blank line between the subject and the cut
  line that the prior test used -- computed (and confirmed with a throwaway Python
  snippet against the real regex) that keeping the blank line puts the second token on
  buffer line 5, not the line 4 the plan's own `<behavior>` block specifies. This is a
  Rule 1 fix to match the plan's stated, testable behavior spec rather than a literal
  byte-for-byte reuse of "same message" — the case shape (token above and below a cut
  line, both named) is unchanged.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Test fixture line numbers adjusted to match the plan's own `<behavior>` spec**
- **Found during:** Task 1 (writing the RED tests)
- **Issue:** The plan's action text said "same message" when renaming
  `test_token_above_and_below_the_scissors_line_is_found_once`, but that message (with its
  blank line after the subject) places the second `[skip ci]` on buffer line 5, not line 4
  as both the plan's `<behavior>` block and the new D-02 case's expected line require.
  Verified computationally (a throwaway `re.finditer` walk over the exact string) before
  writing the assertion.
- **Fix:** Removed the blank line between the subject and the cut line in both the
  renamed both-lines test and the new D-02 parametrized test, so the second token lands
  on line 4 as specified. No other change to either fixture's shape.
- **Files modified:** tests/test_skip_tokens.py
- **Verification:** `make test PYTEST_ARGS="tests/test_skip_tokens.py -q -k 'cut_line or commit_v'"` -- `5 passed`
- **Committed in:** e46ed34 (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (1 bug -- aligning a test fixture with the plan's own stated line numbers)
**Impact on plan:** No scope creep; the fix makes the RED/GREEN tests assert exactly what the plan's `<behavior>` block specifies.

## Issues Encountered

- `gsd_run query commit` (the SDK's own metadata-commit wrapper) failed the final
  `docs(06-02): complete commit-msg hook cut-line plan` commit twice with
  `reason: "commit_timeout"` -- its internal 30s budget for the `git commit` subprocess is
  shorter than this repository's pre-commit `verify` hook, which runs the full
  `make verify` (measured 32.10s-32.57s in this session, dominated by the CAD test suite).
  No `.git/index.lock` remained and no git process was still running after either
  timeout, so this was not a stuck lock -- it is a structural mismatch between the SDK's
  fixed timeout and this repository's own hook cost, unrelated to the two task commits
  (which used a plain `git commit` with the Bash tool's larger default timeout and
  succeeded immediately both times). Resolved by committing the same already-staged files
  with a direct `git commit` -- the same underlying operation the wrapper performs, run
  through the installed hooks with no bypass, just without the tool-level 30s cap.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- D-01, D-02, and D-03 are complete; the commit-msg hook merge-gate debt filed in Phase 5
  is fully retired. `docs/tech_debt/INDEX.md`'s `## Active` table now lists only the
  waived-latency-bar item and `pr-land`'s two unrelated `must` items (out of this plan's
  scope).
- `make verify` passes (185 tests) at HEAD (`d0c43ee`).
- Ready for the next plan in Phase 6 (solid-cache follow-on work, per `06-CONTEXT.md`).

---
*Phase: 06-address-tech-debt-merge-gate-solid-cache*
*Completed: 2026-09-25*

## Self-Check: PASSED

- `.planning/phases/06-address-tech-debt-merge-gate-solid-cache/06-02-SUMMARY.md` exists on disk.
- Commits `e46ed34` and `d0c43ee` found in `git log --oneline --all`.
- Both task commits' post-commit acceptance-criteria checks re-run and passed (documented above and in-session).
- `make verify` exits 0 at HEAD (`d0c43ee`), 185 tests passing.
