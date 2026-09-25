# `make pr.land` reports "a skip token reached main" for any run it failed to observe

Severity: nice
Status: active
Date: 2026-09-25
Source: Codex cross-CLI review of PR #4 (findings 5 and 4), 2026-09-25; confirmed
  against `scripts/pr_land.py` before filing.
Related files:
- scripts/pr_land.py (`land`, the `if found_run is None:` message after the poll loop)
- scripts/pr_land.py (module docstring, the "the merged tree is the checked tree -- that
  claim is proven here, not rested on a server setting" paragraph)
- docs/HOW_TO_DEVELOP.md §8 (the matching "merged, but no run appeared" guidance)

## Context

Step 5 of `land` polls for a `ci.yml` run on the squash commit and exits 1 with `... no
ci.yml run appeared within N s -- a skip token reached main (L22)` when none was seen.
The poll cannot tell that cause from the others that produce the same silence: `gh api`
failing on every attempt (the review reproduced it with HTTP 403 on each poll), a
malformed response, or GitHub scheduling the run later than the poll's deadline. After
D-03 and `message_refusals` a skip token is in fact the *least* likely of these -- the
squash text was checked whole before the merge.

Related over-claim, same file: the module docstring says the "merged tree is the checked
tree" claim is "proven here, not rested on a server setting". `gh pr merge
--match-head-commit` pins the PR *head*, not the base (cli/cli
`pkg/cmd/pr/merge/merge.go`): if `main` advances between `pr.land`'s `behind_by` read
and the merge call, the merge still goes through with the unchanged head, and only the
ruleset's strict up-to-date policy (D-12) stops it. The docstring and §8 should say the
ruleset carries that half.

## Why it matters

The message names a cause the tool has not observed, in a tool whose whole job is to say
only what it checked. A reader who trusts it hunts for a token that is not there instead
of re-running the poll; a reader who has seen it be wrong once stops trusting the
refusals that are right. Neither changes what gets merged -- hence nice.

## Next step

Keep the last poll error and report what was observed: `no run observed within N s (last
error: ...)` when the reads failed; `no run observed within N s` when they succeeded and
returned nothing; and name a token only after fetching the squash commit's message and
finding one. Rewrite the docstring paragraph and the §8 sentence to say which half rests
on the ruleset. One offline `FakeRunner` case per branch.

Revisit when: `pr.land` prints this message once for real, or `scripts/pr_land.py` is
touched anyway.

<!-- On resolve: set Status: resolved, add `Resolved in: <commit sha>`,
     git mv into resolved/, move the INDEX row to Resolved — same commit as the fix. -->
