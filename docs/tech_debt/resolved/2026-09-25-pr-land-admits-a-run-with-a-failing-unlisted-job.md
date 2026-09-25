# `make pr.land` judges a run by the listed jobs only, never by the run's own conclusion

Severity: must
Status: resolved
Date: 2026-09-25
Resolved in: 9ca8320
Source: Codex cross-CLI review of PR #4 (finding 1), 2026-09-25, per `docs/HOW_TO_DEVELOP.md`
  §7; confirmed against `scripts/pr_land.py` before filing.
Related files:
- scripts/pr_land.py (`head_refusals`, the `for name in sorted(required)` loop -- the
  only verdict on a completed run; `check_head`, which calls `head_refusals` at its end;
  `land`, its `check_head(pr.head_sha, run, required_jobs())` call)
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

In `head_refusals`, alongside the per-job loop, refuse when `run.conclusion !=
"success"` (`run` here is the `WorkflowRun`, not the `Runner` callable `check_head`
takes), in addition to the per-job check (keep the per-job check: it is what names a
*missing* job, which a green run conclusion cannot). One offline case in
`tests/test_pr_land.py`: a run with `conclusion: "failure"`, every listed job
`success`, one unlisted job `failure` -> refused, naming the run's conclusion. Second step, only if wanted: read `required-jobs.txt` from the PR head
(`gh api repos/halfb00t/spur/contents/...?ref=<sha>`) instead of the local checkout --
that closes the stale-checkout half but puts a network read in front of the pure core.

Revisit when: `ci.yml` gains a job, or `scripts/pr_land.py` is touched anyway.

## Resolution (2026-09-25)

`Resolved in: 9ca8320` is Plan 06-03 Task 1's commit
(`fix(06-03): pr.land refuses a run whose own conclusion is not success`) -- not the
present commit, which adds §8's rule and moves this file, completing the fix (a file
cannot carry its own commit's sha).

The first step of "Next step" was taken: `head_refusals` refuses when
`run.conclusion != "success"`, naming the conclusion and the run's `html_url`,
alongside the unchanged per-job loop. The second step -- reading `required-jobs.txt`
from the PR head over the network -- was not taken; that half of the stale-checkout
gap is closed by rule instead, via `docs/HOW_TO_DEVELOP.md` §8's new paragraph: run
`make pr.land` from an up-to-date `main` (`git switch main && git pull --ff-only`),
which `pr.land`'s own step 6 leaves you on anyway.

Evidence: the new offline test
`test_head_refusals_a_failed_run_is_refused_even_when_every_listed_job_is_green` (the
debt file's own case -- a run failed on an unlisted `lint` job, every `required-jobs.txt`
job green, refused naming the conclusion and the run URL); the recorded real run
36116930241 through `check_head` in
`test_check_head_names_the_run_conclusion_of_recorded_run_36116930241`; and the live
probe on that same run in Task 1's `<verify>` block, run against the real `gh`: two
refusals before this fix (`behind`, `test (3.12)` failure), three after (adding the
run's own `concluded 'failure'` line).
