---
phase: 05-ci-observed-green
reviewed: 2026-09-25T08:41:41Z
depth: standard
files_reviewed: 6
files_reviewed_list:
  - docs/tech_debt/INDEX.md
  - docs/tech_debt/active/2026-09-25-commit-msg-hook-trusts-a-hand-typed-cut-line.md
  - scripts/pr_land.py
  - scripts/skip_tokens.py
  - tests/test_pr_land.py
  - tests/test_skip_tokens.py
findings:
  critical: 0
  warning: 0
  info: 0
  total: 0
status: clean
---

# Phase 05: Code Review Report (incremental — Plan 05-06 gap closure)

**Reviewed:** 2026-09-25T08:41:41Z
**Depth:** standard
**Files Reviewed:** 6
**Status:** clean

## Summary

This is a re-review of Plan 05-06, which was written to close CR-01 from the prior
`05-REVIEW.md` (commit `5ded6ad`): `message_refusals()` in `scripts/pr_land.py` reused
`find_skip_tokens()`'s internal cut at git's `commit -v` scissors line on PR title/body
text that git never truncates, so a PR body hiding a skip token below a hand-written
line identical to that cut line passed `pr.land` with zero refusals.

**CR-01 is closed.** Verified by re-reading both the diff and the resulting code at
HEAD, not just the plan's narrative:

- `find_skip_tokens()` (`scripts/skip_tokens.py:68-75`) no longer cuts at all — it is
  now a pure, unconditional scan of whatever text it is handed. The cut was moved
  entirely into the one caller that needs it.
- `message_refusals()` (`scripts/pr_land.py:238-253`) calls `find_skip_tokens()` on the
  whole `subject + "\n\n" + body`, with no cut applied anywhere on that path — this is
  exactly the text GitHub records verbatim into the squash commit, so there is nothing
  for a git cut line to mean there.
- `main()` (`scripts/skip_tokens.py:78-117`, the commit-msg hook entry) now applies the
  scissors cut only when `os.environ.get("GIT_EDITOR") != ":"` — i.e. only when git
  actually ran an editor for this commit (githooks(5): git itself forces
  `GIT_EDITOR=:` for every commit hook when no editor will run). For a plain `-m`/`-F`
  commit this is strictly *more* scanning than the pre-05-06 code did (the old
  `find_skip_tokens` cut unconditionally, including for `-m`/`-F`), so this is a
  widening of what gets refused, never a narrowing.
- Regression tests exist at both layers and pass: `test_find_skip_tokens_searches_the_
  whole_text_it_is_given`, `test_message_refusals_checks_the_whole_body_even_below_a_
  git_cut_line`, and the end-to-end `test_land_refuses_a_token_hidden_below_a_git_cut_
  line_in_the_pr_body` all reproduce the exact CR-01 shape and assert it is now
  refused. `test_hook_without_an_editor_refuses_a_token_below_a_cut_line` pins the
  hook's own `-m`/`-F` case the same way.
- Ran the two affected test files directly (not just trusted the plan's own claim):
  `.venv/bin/python -m pytest tests/test_skip_tokens.py tests/test_pr_land.py -q` →
  `79 passed`. `ruff check` and `mypy --strict` on all four source/test files under
  review → clean.

**Residual, correctly scoped and filed, not a new defect.** An editor session (`git
commit` with no `-m`/`-F`) in which the author hand-types or pastes a line
byte-identical to git's own scissors line, without `-v`, `commit.verbose`, or
`--cleanup=scissors`, still hides a token below it from the hook — content alone cannot
distinguish that from git's own cut, and `GIT_EDITOR` only distinguishes "no editor"
from "editor", not "editor with `-v`" from "editor without it". This is filed as `must`
severity in `docs/tech_debt/active/2026-09-25-commit-msg-hook-trusts-a-hand-typed-cut-
line.md` and linked from `docs/tech_debt/INDEX.md`, in the same commit as the fix, per
this project's own process. The doc's own "why it matters" argument was checked, not
just read: a commit made this way still cannot reach `main` silently, because its own
CI run never appears for that head (the token suppresses it), and `pr.land`'s
`check_head` refuses a run-less head unconditionally — the backstop is real, not
asserted. `must` (not `blocker`) is the right tier under this repo's own severity
definitions (`docs/tech_debt/INDEX.md`): the failure mode is a refused merge, not
silent data loss or a silent partial success.

**Lines chased and ruled out, worth recording for the next reviewer.** Because `main()`
now branches on `os.environ.get("GIT_EDITOR")`, and the commit-msg hook actually runs
through the `pre-commit` framework (`.pre-commit-config.yaml`'s `no-skip-token`
`language: system` entry), it was worth checking whether `pre-commit` sanitizes
`GIT_*` environment variables before invoking hook subprocesses — it has a
`no_git_env()` helper (`pre_commit/git.py`) that strips everything prefixed `GIT_`
except a narrow allowlist that does **not** include `GIT_EDITOR`. If that helper were
used on the path that spawns hook entries, `os.environ.get("GIT_EDITOR")` would always
read `None` under the real hook and `editor_ran` would always evaluate `True`,
silently defeating the `-m`/`-F` branch this plan added. Traced the actual call path
(`unsupported_script.run_hook` → `lang_base.run_xargs` → `xargs.xargs` →
`cmd_output_p`): none of it passes an `env=` override, so hook subprocesses inherit
`os.environ` unmodified; `no_git_env()` is used only for `pre-commit`'s own internal
`git` invocations elsewhere in that package. No bug here — but this was not obvious
from reading `scripts/skip_tokens.py` alone, and is exactly the kind of assumption
`docs/tech_debt/active/2026-09-25-commit-msg-hook-trusts-a-hand-typed-cut-line.md`
itself flags as unverified-behavior risk. Recorded here rather than in `docs/tech_debt/`
because it resolved to "no defect," not to a decision or a deferred fix.

No other defect was found in the diff. `docs/tech_debt/INDEX.md`'s new row and the new
debt file's `Related files`/`Trigger` fields match what actually changed; no dangling
reference, no severity mismatch, no missing INDEX row.

All reviewed files meet quality standards for this change. No issues found.

---

_Reviewed: 2026-09-25T08:41:41Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
