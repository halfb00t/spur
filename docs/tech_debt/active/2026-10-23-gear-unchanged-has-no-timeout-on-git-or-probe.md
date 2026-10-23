# `gear.unchanged` runs git and the schema probe with no timeout, inside the pre-commit hook

Severity: must
Status: active
Date: 2026-10-23
Source: Phase 30 code review, WR-01 (`.planning/phases/30-scope-seam-and-gear-safety-guard/30-REVIEW.md`)
Related files:
- scripts/gear_unchanged.py:73-77 (`_git`)
- scripts/gear_unchanged.py:89 (`ensure_tag` fetch)
- scripts/gear_unchanged.py:111-115 (`schema_of`)

## Context
`_git()` and `schema_of()` call `subprocess.run` with no `timeout`. When the `v0.6` tag is not
local, `ensure_tag` runs `git fetch origin tag v0.6` with stdin and the tty attached and
`GIT_TERMINAL_PROMPT` unset, so git can block on a credential prompt or a dead network.

## Why it matters
The check runs in `verify.static`, so in the pre-commit hook, whose budget is the 30 s cap of
gsd's SDK commit (L36). D-05 says a failed fetch fails the gate; a hung fetch neither passes nor
fails. It cannot produce a false green, which is why this is not a blocker. The repo already
carries a `make verify` hang item (`2026-10-10-make-verify-hung-at-98-percent-with-no-failure.md`),
and an unbounded subprocess here would look the same.

## Next step
Add a `timeout=` to every `subprocess.run` in the script, set `GIT_TERMINAL_PROMPT=0` and
`stdin=subprocess.DEVNULL` for git, turn `TimeoutExpired` into a `SystemExit` naming the
command, and add a scratch-repo test with an unreachable origin that must fail within the
bound. Revisit when the hook next stalls, or when `scripts/gear_unchanged.py` is next touched.
