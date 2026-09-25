# The required-jobs drift test reads job ids, so a `name:` override slips past it

Severity: nice
Status: resolved
Date: 2026-09-25
Resolved in: 0573319
Source: Codex cross-CLI review of PR #4 (finding 3), 2026-09-25; confirmed against
  `tests/test_pr_land.py` before filing.
Related files:
- tests/test_pr_land.py (the drift test: the `job_ids = re.findall(r"^  ([a-zA-Z][\w-]*):\s*$", ...)`
  block and the `derived` set built from it)
- .github/workflows/ci.yml
- .github/workflows/required-jobs.txt

## Context

The drift test derives the job set GitHub will report from `ci.yml` by regexing the
two-space-indented keys under `jobs:` and expanding `test` over its `python: [...]`
matrix. GitHub reports a job by its `name:` when one is set, else by its id. Adding
`name: renamed-image` under `image:` keeps the test green while `required-jobs.txt` and
the ruleset still say `image` -- and nothing on any PR would report `image` again.

## Why it matters

It fails closed: `pr.land` refuses every head (`required job 'image' is missing from the
run`) and the ruleset blocks every merge until someone reads a run and fixes the names.
A stalled merge path, not a wrong merge -- hence nice. But it would surface as "CI is
broken", not as "the drift test caught a rename", which is the diagnosis the test exists
to give.

## Next step

Make the parse honest about its own limits: assert that no job-level `name:` key
appears in the `jobs:` section (three lines, next to the existing `assert "test" in
job_ids`) -- scoped to the same two-space job-id indent already used for `job_ids`,
e.g. `^  name:\s` immediately after a job-id line, not any `name:` in the whole
`jobs:` subtree (that would also match the step-level `name:` keys `ci.yml` already
has, at `bundle matches web/` and `the packaged entrypoint serves a gear`, and fail
against the current, correct workflow). Message: `name:` overrides are unsupported
until the derivation reads them. Or derive the effective name -- the `name:` value
under a job id when present, else the id. Either way, one regression case with an
in-memory `ci.yml` that renames `image`.

Revisit when: any job in `ci.yml` gets a `name:`, or the drift test is touched anyway.

## Resolution (2026-09-25)

`Resolved in: 0573319` is Plan 06-03 Task 2's commit
(`test(06-03): the drift test reads the job names GitHub reports`) -- not the present
commit, which adds §8's line about effective names and moves this file, completing the
fix (a file cannot carry its own commit's sha).

The second option in "Next step" was taken: derive the effective name (`jobs.<id>.name`
when a job sets one, else the id), not the first (assert no job-level `name:` key). The
new `_effective_job_names(ci_yml)` helper scopes the `^    name:` lookup to each job's
own block, so the two step-level `name:` keys this file's own "Next step" named
(`bundle matches web/`, `the packaged entrypoint serves a gear`) are never read.

Evidence: `test_required_jobs_file_matches_ci_yml_job_names` (renamed from
`..._job_ids`) compares `required_jobs()` against the effective names of the real
`ci.yml`; `test_a_job_name_override_moves_the_derived_required_set` is this file's own
`image` -> `renamed-image` regression case, plain and quoted, with both step names
asserted absent from the derived set.
