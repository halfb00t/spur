# `make no-fake-done` matches nothing on macOS: `git grep -E` has no `\b`

Severity: must
Status: resolved
Date: 2026-10-05
Resolved in: fix(gate): match unfinished-work markers with -w so the scan runs on macOS
Source: screw's scaffold run, proving its copy of this target with a staged probe file
Related files:
- Makefile:no-fake-done (the `git grep -nE '\b(TODO|FIXME|XXX|HACK|NotImplementedError)\b'` line, before this fix)
- tests/test_no_fake_done.py (added by the fix)

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

## Resolution (2026-10-05)

- Mechanism: `\b(...)\b` became `-w '(...)'` in `Makefile`'s `no-fake-done`, the spelling
  screw's Makefile proved. `-w` is git's own whole-word match and does not depend on the
  system regex library, so the scan now means the same thing on the dev host and in CI.
- Proof on this host (homebrew git 2.54.0, 2026-10-05): in a scratch repo, one staged
  `p.py` holding `# TODO: later`, `TODOS`, `xTODO`, `raise NotImplementedError`,
  `class NotImplementedErrorish` and `HACKy` -- the `\b` form exits 1 with no output;
  the `-w` form names lines 1 and 4 and nothing else.
- The proof survives the next edit: `tests/test_no_fake_done.py` copies the Makefile into
  a throwaway git repo, stages that probe and runs `make -C <repo> no-fake-done` -- a
  marked probe is refused with both lines named, a near-miss probe (every marker inside a
  longer word) passes. The subprocesses run with every `GIT_*` variable dropped: the
  pre-commit hook that runs `make verify` exports `GIT_INDEX_FILE=.git/index` (relative)
  and `GIT_PREFIX` to its children (measured with a probe hook, 2026-10-05), and carried
  into the probe's `git add` they could aim it at this repository's own index.
- Nothing had slipped through: `make no-fake-done` with `-w` passes on the tree at
  `c871b61` -- CI's Linux git had enforced the check all along, as the context above
  predicted.
- Tests: 929 -> 931 collected.
