# API Coverage — GitHub (REST, through the `gh` CLI)

> Full coverage by default. Opt-outs are explicit, reasoned decisions.

Scope: the GitHub capabilities that bear on a merge gate for `main` -- pull requests,
Actions runs and jobs, the repository's merge settings, and branch rules. Phase 5 uses
them from `scripts/pr_land.py` (`make pr.land`, Plan 05-02) and from one-off,
documented `gh api` calls (Plans 05-01, 05-03). GitHub's API outside this domain (issues,
releases, packages, …) is not something this phase touches. Every row below was
decided while planning Phase 5, on 2026-09-25; the ruleset rows were revised the same day
for D-12 (a ruleset on `main`, superseding D-06).

| capability | decision | reason |
|---|---|---|
| pulls.get (state, base, head sha, head branch, title, body) | INTEGRATE | |
| repos.compare-commits (ahead_by, behind_by) | INTEGRATE | |
| actions.list-workflow-runs (ci.yml, filtered by head_sha) | INTEGRATE | |
| actions.list-jobs-for-workflow-run | INTEGRATE | |
| pulls.merge (squash, match-head-commit, commit title and body) | INTEGRATE | |
| pulls.get merge commit (the squash sha) | INTEGRATE | |
| repos.update (squash_merge_commit_title, squash_merge_commit_message) | INTEGRATE | |
| repos.get (visibility, permissions, merge settings; read-only) | INTEGRATE | |
| rules.get-branch-rules (rules on main; read-only; the D-12 read-back, 05-03 and 05-04) | INTEGRATE | |
| repos.get-repo-ruleset (the existing `default` ruleset, id 23977515; read-only, before the change) | INTEGRATE | |
| repos.update-repo-ruleset (PUT: target main, add required status checks with the strict policy, keep the pull-request rule) | INTEGRATE | |
| repos.create-repo-ruleset (POST a second ruleset) | OPT-OUT | not needed: the repository already has a ruleset, `default` (id 23977515), holding the human's pull-request, deletion and force-push rules with no branch targeted; 05-03 retargets it instead of adding a second one beside it |
| repos.delete-repo-ruleset | OPT-OUT | not needed yet: removal is D-12's documented reversal (one call, recorded in docs/HOW_TO_DEVELOP.md section 8), not something this phase runs |
| classic branch protection (PUT branches/main/protection) | OPT-OUT | not needed: the ruleset carries the same rules (D-12), and one mechanism on main is simpler to read back than two |
| pulls.merge with merge or rebase methods | OPT-OUT | explicitly out of scope: one phase lands as one squash commit (docs/HOW_TO_DEVELOP.md) |
| pull-request auto-merge | OPT-OUT | explicitly out of scope: an auto-merge lands without make pr.land, so its post-merge run check (D-05 step 5) would never run |
| merge queue | OPT-OUT | explicitly out of scope: a queue lands PRs without make pr.land's post-merge run check, and one phase lands at a time |
| checks API and GraphQL statusCheckRollup | OPT-OUT | not needed: the REST jobs endpoint is the single source of job conclusions (RESEARCH anti-pattern: different casing and contents) |
| commit statuses API | OPT-OUT | not needed: ci.yml reports through Actions jobs, not commit statuses |
| git refs delete (remote branch deletion, gh pr merge --delete-branch) | OPT-OUT | not needed: the repository's delete_branch_on_merge setting governs remote branches; gh's behaviour with the flag is unverified (RESEARCH A3) |
| actions re-run and workflow_dispatch | OPT-OUT | not needed: pr.land observes runs and never triggers them |
| actions billing and usage | OPT-OUT | not needed yet: needs the user token scope; the minutes concern is deferred in CONTEXT.md |
| repos.get-commit (reading the squash message back) | OPT-OUT | not needed yet: pr.land sets the squash text itself; it is read back once by hand at this phase's merge (05-05 output, RESEARCH A2) |
| pull-request reviews and required approvals | OPT-OUT | explicitly out of scope: cross-CLI review is a procedure (docs/HOW_TO_DEVELOP.md section 7), not an API gate; the ruleset's pull-request rule keeps the human's zero required approvals |
