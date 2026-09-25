# API Coverage — GitHub (REST, through the `gh` CLI)

> Full coverage by default. Opt-outs are explicit, reasoned decisions.

Scope: the same GitHub surface Phase 5 decided for the merge gate on `main`
(`.planning/phases/05-ci-observed-green/COVERAGE.md`), as Phase 6 changes it. Phase 6 uses
it from `scripts/pr_land.py` only (`make pr.land`): Plan 06-03 reads the run's own
`conclusion` from the runs response it already fetched (D-04), and Plan 06-04 adds one read
of the squash commit (D-06). No write call is added. Rows marked "unchanged" keep Phase 5's
decision and reason; every row was re-decided while planning Phase 6, on 2026-09-25.
`repos.get-commit` is read only when no run is observed for the squash commit
(Plan 06-04, `no_run_report`); the head-ref content read stays deferred until a PR that
grows the job set is refused for the wrong reason (06-CONTEXT.md Deferred).

| capability | decision | reason |
|---|---|---|
| pulls.get (state, base, head sha, head branch, title, body) | INTEGRATE | |
| repos.compare-commits (ahead_by, behind_by), read once per land | INTEGRATE | |
| actions.list-workflow-runs (ci.yml by head_sha; `conclusion` now read, D-04) | INTEGRATE | |
| actions.list-jobs-for-workflow-run | INTEGRATE | |
| pulls.merge (squash, match-head-commit, commit title and body) | INTEGRATE | |
| pulls.get merge commit (the squash sha) | INTEGRATE | |
| repos.get-commit (squash commit URL and message; D-06) | INTEGRATE | |
| repos.update (squash_merge_commit_title, squash_merge_commit_message) | INTEGRATE | unchanged: applied once in Phase 5; Phase 6 does not call it |
| repos.get (visibility, permissions, merge settings; read-only) | INTEGRATE | unchanged |
| rules.get-branch-rules (rules on main; read-only) | INTEGRATE | unchanged: the documented read-back in docs/HOW_TO_DEVELOP.md section 8 |
| repos.get-repo-ruleset / repos.update-repo-ruleset (ruleset 23977515) | INTEGRATE | unchanged: Phase 6 changes no required-check name, so the documented apply command is not re-run |
| repos.get-content at the PR head ref (`required-jobs.txt`) | OPT-OUT | not needed yet: D-04 rejected a network read in front of the pure core for a case the run-conclusion check already refuses; deferred in 06-CONTEXT.md |
| a second repos.compare-commits read immediately before pulls.merge | OPT-OUT | not needed yet: D-07 rejected it (narrows the read-to-merge window without closing it; the ruleset's strict up-to-date policy closes it); deferred in 06-CONTEXT.md |
| repos.create-repo-ruleset / repos.delete-repo-ruleset | OPT-OUT | unchanged: one ruleset exists; removal is the documented reversal in docs/HOW_TO_DEVELOP.md section 8 |
| classic branch protection (PUT branches/main/protection) | OPT-OUT | unchanged: the ruleset carries the same rules |
| pulls.merge with merge or rebase methods | OPT-OUT | unchanged: explicitly out of scope, one phase lands as one squash commit |
| pull-request auto-merge / merge queue | OPT-OUT | unchanged: explicitly out of scope, both land without make pr.land's post-merge run check |
| checks API and GraphQL statusCheckRollup | OPT-OUT | unchanged: the REST jobs endpoint and the run's own `conclusion` are the sources of the verdict |
| commit statuses API | OPT-OUT | unchanged: ci.yml reports through Actions jobs, not commit statuses |
| git refs delete (remote branch deletion, gh pr merge --delete-branch) | OPT-OUT | unchanged: the repository's delete_branch_on_merge setting governs remote branches |
| actions re-run and workflow_dispatch | OPT-OUT | unchanged: pr.land observes runs and never triggers them; D-06 reports a missing run, it does not start one |
| actions billing and usage | OPT-OUT | unchanged: not needed yet, needs the user token scope |
| pull-request reviews and required approvals | OPT-OUT | unchanged: cross-CLI review is a procedure (docs/HOW_TO_DEVELOP.md section 7), not an API gate |
