# The required-jobs drift test reads job ids, so a `name:` override slips past it

Severity: nice
Status: active
Date: 2026-09-25
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

Make the parse honest about its own limits: assert that no `name:` key appears in the
`jobs:` section (three lines, next to the existing `assert "test" in job_ids`), with a
message saying `name:` overrides are unsupported until the derivation reads them. Or
derive the effective name -- the `name:` value under a job id when present, else the id.
Either way, one regression case with an in-memory `ci.yml` that renames `image`.

Revisit when: any job in `ci.yml` gets a `name:`, or the drift test is touched anyway.

<!-- On resolve: set Status: resolved, add `Resolved in: <commit sha>`,
     git mv into resolved/, move the INDEX row to Resolved — same commit as the fix. -->
