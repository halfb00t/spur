# The commit-msg hook trusts a cut line typed by hand in an editor session

Severity: must
Status: active
Date: 2026-09-25
Source: 05-VERIFICATION.md gap bullet 3 and 05-REVIEW.md CR-01 point 1, narrowed by Plan
  05-06's "fix(05-06): trust git's cut line in the commit-msg hook only when git ran an
  editor" (this commit).
Related files:
- scripts/skip_tokens.py (`_SCISSORS`, `message_to_check`, `main`)
- tests/test_skip_tokens.py (the cut-line tests)

## Context

What git does with a line shaped like its own `commit -v` cut marker (`# ` + 24 dashes +
` >8 ` + 24 dashes), probed in a scratch repository during planning (git 2.54.0,
2026-09-25), for the message `safe subject`, a blank line, the cut line, `[skip ci]`:

| How the commit was made | Recorded message keeps the token? | `GIT_EDITOR` the hook saw |
|---|---|---|
| `git commit -m` | yes (the cut line too) | `:` |
| `git -c commit.verbose=true commit -m` | no -- truncated at the cut line | `:` |
| `git commit -v -m` | no -- truncated | `:` |
| `git commit -F file` | yes (the cut line too) | `:` |
| editor (`-e`), no `-v` | yes (only the `#` cut line stripped) | the caller's editor |
| editor (`-e`) with `-v` | no -- truncated | the caller's editor |

The parent shell had `GIT_EDITOR=true` for every row; git still handed the hook `:`
whenever no editor ran (githooks(5): "All the git commit hooks are invoked with the
environment variable `GIT_EDITOR=:` if the command will not bring up an editor").

What the hook does after Plan 05-06: `main()` cuts at the first line matching that
pattern only when `GIT_EDITOR` is not `:` -- i.e. only when git actually ran an editor.
With no editor (`-m`, `-F`), the whole message is searched, closing the two `-m`/`-F`
rows above.

The residual: in an editor session without `-v`, `commit.verbose`, or
`--cleanup=scissors`, a cut line the author types or pastes by hand still hides
everything below it from the hook, while git itself (`cleanup=strip`, the default for an
edited, non-verbose message) removes only the `#`-prefixed cut line and records the
token that follows verbatim. Content alone cannot tell that hand-typed line from git's
own -- both are byte-identical -- and the hook has no way to see whether `-v` was on the
command line; `GIT_EDITOR` distinguishes "no editor" from "editor", not "editor with
`-v`" from "editor without it".

## Why it matters

A commit made this way carries a skip token past the hook; as a PR head commit it gets
zero recorded checks (the `20b63e4` shape this phase's own docstring names). The
backstops that still catch its consequence: the ruleset on `main` (D-12) refuses to
merge a head without green `test (3.12)`, `vendor-bundle` and `image`; `make pr.land`
refuses a run-less head; and after D-03 a branch commit's message never becomes `main`'s
-- the squash message is the PR title and body, which `pr.land`'s `message_refusals`
checks whole, with no cut at all (Plan 05-06 Task 1). So no run-less commit reaches
`main` through the sanctioned path; the cost of this residual is a PR stuck at merge
time instead of a commit refused at commit time. The pasted-by-hand case is plausible
here specifically: this repository's own tests and docs quote the cut line verbatim.

## Next step

Two ways to close it, each with its cost:

1. **Drop the cut entirely.** Every `git commit -v` whose staged diff names a token
   (this repository's own tests and docs do) is refused, and the author rewords. `git
   config --get commit.verbose` reads empty on this machine (2026-09-25), so nobody here
   is opted into verbose commits today -- but the cost would land on anyone who is.
2. **In an editor session, cut only when `git config` says git will truncate**
   (`commit.verbose` resolves true, or `commit.cleanup` is `scissors`). A `-v` typed on
   the command line for one commit, with no matching config, stays invisible to this
   check -- so that path becomes the same over-match refusal as option 1 for that one
   commit, and a `--no-verbose` or `--cleanup=` override of the config stays invisible
   too.

Revisit when: a PR head with zero recorded checks is traced back to a commit the hook
passed, anyone in this repository adopts `commit.verbose`, or `scripts/skip_tokens.py`
is touched again for an unrelated reason.

<!-- On resolve: set Status: resolved, add `Resolved in: <commit sha>`,
     git mv into resolved/, move the INDEX row to Resolved — same commit as the fix. -->
