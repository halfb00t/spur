# `make pr.land` reports "a skip token reached main" for any run it failed to observe

Severity: nice
Status: resolved
Date: 2026-09-25
Resolved in: e4345a4
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

## Resolution (2026-09-25)

`Resolved in: e4345a4` is Plan 06-04 Task 1's commit
(`fix(06-04): pr.land reports only what it observed after the merge`) -- not the present
commit, which states the split in the docstring and §8 (the other half of this same
file), records L25 and moves this file, completing the fix (a file cannot carry its own
commit's sha).

"Next step" was taken as written: the poll keeps its last error; `land`'s unobserved-run
message is now `no_run_report(...)`, which reports exactly one of three things --
`; last error: ...` when the reads failed, an Actions link when they succeeded and
nothing appeared, or a named token only after fetching the squash commit's message and
finding one. The module docstring and `docs/HOW_TO_DEVELOP.md` §8 were rewritten to say
which half of the merged-tree claim rests on the ruleset (D-07).

What now exists: `no_run_report(pr_number, squash_sha, waited_s, last_error, run)` in
`scripts/pr_land.py`, and four new test names in `tests/test_pr_land.py` --
`test_land_reports_the_last_read_error_when_every_poll_failed`,
`test_land_reports_no_run_observed_with_the_actions_url_when_reads_succeeded`,
`test_land_names_a_skip_token_only_after_reading_it_from_the_squash_commit`, and
`test_no_run_report_a_failed_commit_read_is_the_last_error`.

Evidence: the live probe against two real commits, run during this plan's own execution
(`06-04-SUMMARY.md`) -- `no_run_report(4, 'b72b0e1f1e31e06b9dd8bef964725b11f30e0c51', ...)`
returned the Actions link with no last error and no token; `no_run_report(2,
'20b63e453a3cd0c72e5d0f995a107a238c652a90', ...)` named `'[ci skip]'`, read from that
commit's own message, with no last error.
