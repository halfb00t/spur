# `make no-fake-done` matches nothing on macOS: `git grep -E` has no `\b`

Severity: must
Status: active
Date: 2026-10-05
Source: screw's scaffold run, proving its copy of this target with a staged probe file
Related files:
- Makefile:no-fake-done (the `git grep -nE '\b(TODO|FIXME|XXX|HACK|NotImplementedError)\b'` line)

## Context
The unfinished-work scan anchors its pattern with `\b`. git grep's `-E` uses the
system regex library, and on macOS (homebrew git 2.54.0, 2026-10-05) that library does
not implement `\b`: a staged file containing both `TODO` and `NotImplementedError` made
the `\b`-anchored scan exit 1 with no output, while the same pattern with `-w` in place
of `\b` (and `-P`) found the line. So on the dev host, where the pre-commit hook and
every agent's `make verify` run, the scan has always passed vacuously; only CI's Linux
git has ever enforced it. The `type: ignore` block below it is unaffected (no `\b`).

## Why it matters
L13/L34 say the gate is one definition of "passing" in three places. For this check it
is one place: a marker reaches the commit, the hook passes, and CI is the first to
refuse — after the branch is pushed, not before the commit. An agent that trusts the
local gate is told "done" by a check that did not run.

## Next step
Replace `\b(...)\b` with `-w '(...)'` in `Makefile`'s `no-fake-done` (screw's Makefile
has the spelling and the comment), prove it with a staged probe the way screw did, and
land it through the normal PR path. Consider a test that stages a probe and asserts the
target fails, so the proof survives the next edit.
