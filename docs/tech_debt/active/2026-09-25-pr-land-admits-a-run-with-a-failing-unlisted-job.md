# `make pr.land` judges a run by the listed jobs only, never by the run's own conclusion

Severity: must
Status: active
Date: 2026-09-25
Source: Codex cross-CLI review of PR #4 (finding 1), 2026-09-25, per `docs/HOW_TO_DEVELOP.md`
  §7; confirmed against `scripts/pr_land.py` before filing.
Related files:
- scripts/pr_land.py (`check_head`, the `for name in sorted(required)` loop -- the only
  verdict on a completed run; `land`, its `check_head(pr.head_sha, run, required_jobs())`
  call)
- scripts/pr_land.py (`parse_runs` -- `conclusion` is parsed into the run record and then
  never read by the gate)
- .github/workflows/required-jobs.txt
- tests/test_pr_land.py

## Context

`check_head` refuses when the newest `ci.yml` run for the head is missing, still running,
or any job named in `required-jobs.txt` is absent from it or not `success`. It never reads
`run.conclusion`, although `parse_runs` already carries it. A run whose *unlisted* job
failed -- `conclusion: failure` on the run itself -- passes, as long as the listed jobs are
green.

The list is read from the checkout `pr.land` runs in, not from the PR head. So the case
the review reproduced: a PR adds a job to `ci.yml` and to `required-jobs.txt` (the drift
test forces both), the job fails on the PR head, and `pr.land` is run from a `main`
checkout whose `required-jobs.txt` predates the PR. The gate sees three green listed jobs
and reaches `gh pr merge`. The ruleset on `main` (D-12) has the same blind spot until its
own list is updated by hand (`docs/HOW_TO_DEVELOP.md` §8).

## Why it matters

"CI is green" and "the three jobs we knew about last week are green" are different
claims; L22 promises the first. The window is narrow -- it needs a PR that grows the job
set *and* a stale checkout -- but it is exactly the drift Phase 5 set out to make
structural rather than remembered.

## Next step

In `check_head`, refuse when `run.conclusion != "success"`, in addition to the per-job
check (keep the per-job check: it is what names a *missing* job, which a green run
conclusion cannot). One offline case in `tests/test_pr_land.py`: a run with `conclusion:
"failure"`, every listed job `success`, one unlisted job `failure` -> refused, naming the
run's conclusion. Second step, only if wanted: read `required-jobs.txt` from the PR head
(`gh api repos/halfb00t/spur/contents/...?ref=<sha>`) instead of the local checkout --
that closes the stale-checkout half but puts a network read in front of the pure core.

Revisit when: `ci.yml` gains a job, or `scripts/pr_land.py` is touched anyway.

<!-- On resolve: set Status: resolved, add `Resolved in: <commit sha>`,
     git mv into resolved/, move the INDEX row to Resolved — same commit as the fix. -->
