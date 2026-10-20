# `make pr.land` merges the pushed PR head without checking the local branch is pushed

Severity: blocker
Status: resolved
Resolved in: fix(pr_land): refuse a local head branch the PR head does not carry
Date: 2026-10-20
Source: `/gsd-verify-work 26`, after `make pr.land PR=41`
Related files:
- `scripts/pr_land.py:419` (`land`: the pre-merge checks read `headRefOid` only)
- `scripts/pr_land.py:552` (the only local-tip comparison, after the merge)

## Context
`land()` refuses on PR state, a dirty working tree, the head's CI, the head being behind `main`, and the
squash message. It never compares the local branch with the PR's `headRefOid` before merging. The one
comparison, at line 552, runs after the merge and only prints `local branch ... differs from the merged
head ...; keeping it.`

PR #41 (Phase 26) was squash-merged at `6c0e57b`, the last pushed commit, as `1981d93`. The local
`gsd/phase-26-gate-fails-with-a-cause` held 13 more commits (`faf376b`..`ff9b2c0`) that were never
pushed. They include `faf376b fix(26): size faulthandler_timeout from CI's slowest test`, so `main` kept
`faulthandler_timeout = 120` while the verified tree had `170`. They also include the phase's
26-07 SUMMARY, REVIEW, SECURITY, VERIFICATION and UAT files and 72 lines of `bench/RESULTS.md`. Nothing
failed, and the land reported success apart from that one line.

## Why it matters
Silent partial success: the phase is called landed while part of its verified work, code included, is
not on `main`. The same thing happens on every phase whose last commits were not pushed before landing.

## Next step
Before the merge, when `refs/heads/<head branch>` exists and its tip differs from `headRefOid`, refuse
with both shas and "push, let CI run, retry"; nothing is merged. Pin it with a `tests/test_pr_land.py`
case beside the existing post-merge "keeping it" case. The 13 commits were re-landed through
`gsd/phase-26-remainder`.
