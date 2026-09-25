# The ship-note's CI skip token leaks into the squash-merge commit and skips CI on `main`

Severity: must
Status: resolved
Date: 2026-09-25
Resolved in: fac76f5
Source: /gsd-ship 4 (PR #3) — observed on PR #2's history while shipping Phase 4
Related files:
- .github/workflows/ci.yml (`on: push: branches: [main]`, `pull_request`)
- docs/HOW_TO_DEVELOP.md (§6 "PR", §8 "Влить" — squash-merge)
- ~/.claude/gsd-core/workflows/ship.md (`track_shipping`: the `[ci skip]` ship note)

## Context

GSD's ship workflow commits a STATE.md "ship note" onto the PR branch with `[ci skip]`
in its subject, so the push does not start a redundant pipeline. Two things follow on
this repository, both observed on 2026-09-24/25:

1. The ship note becomes the PR head. GitHub honours the token anywhere in a commit
   message, so the head commit gets no run. This repo is private on a free plan — no
   branch protection, no required checks — so the workflow's "BLOCKED with zero checks
   → push an empty commit" recovery never fires. PR #2's head (`docs(03): ship phase 3
   — PR #2 [ci skip]`) shows zero checks.
2. GitHub's squash-merge message defaults to the PR's commit subjects, so the token
   rides into the squash commit on `main`. `main`'s HEAD after PR #2 (`538d26f`) has no
   CI run at all; the last green `main` run is `59f02c3`, from before Phase 3 landed.

Meanwhile the last real run on the Phase 3 branch (`35993984796`) had already failed
`test (3.10)` — `src/spur/records.py` subscripted `logging.StreamHandler` in a class
statement, a 3.11-only construct — and the PR was merged anyway. `main` claimed 3.10
support (pyproject.toml, the CI matrix) while being unimportable on 3.10, and nothing
said so. Fixed on the Phase 4 branch in the commit that precedes this file.

## Why it matters

"Green CI before merge" (HOW_TO_DEVELOP.md §6/§8) is the project's only check that the
local `make verify` (one interpreter, the developer's) matches the supported floor. A
skip token on the PR head makes the PR look clean with no run; a skip token in the
squash message makes `main` look clean with no run. Both defeat Phase 5's success
criterion ("a real run URL, not a prediction") silently, and the second is invisible
from the PR page.

## Next step

Phase 5 (CI Observed Green) should decide one of:

- Stop putting the token on the ship note (Phase 4 shipped without it — the PR head
  then gets a real run; cost is one extra pipeline per ship), and strip commit-subject
  lists from the squash-merge message (repository setting "Default to PR title" for
  squash merges), or
- keep the token but make the squash message never inherit subjects.

Either way, verify by reading `gh run list --branch main` after the next merge: the
squash commit must have a run. Trigger to revisit: the next `/gsd-ship`.

## Resolution (2026-09-25)

`Resolved in: fac76f5` is Plan 05-01 Task 1's commit
(`feat(05-01): refuse GitHub Actions skip tokens at commit time`), which added the
`no-skip-token` commit-msg hook — not the present commit, which applies and records D-03
and moves this file, completing the fix (a file cannot carry its own commit's sha).

What now exists: the `no-skip-token` commit-msg hook (`scripts/skip_tokens.py`,
`.pre-commit-config.yaml`) rejects all six tokens anywhere in a commit message, proven by
`tests/test_skip_tokens.py` (D-02); the repository's squash-merge settings are
`squash_merge_commit_title=PR_TITLE`, `squash_merge_commit_message=PR_BODY`, applied by
`gh api -X PATCH` and read back on 2026-09-25 (D-03); `docs/HOW_TO_DEVELOP.md` §6 gains
the manual ship-note step the hook now forces, since `gsd-ship`'s own ship-note commit
carries `[ci skip]` and is refused (D-04).

The option this file's own "Next step" took: not "keep the token but make the squash
message never inherit subjects" — the token cannot reach a commit at all, on either the
PR head or the branch, and the squash message no longer inherits commit subjects
regardless of what a branch commit says.

Evidence: PR #3's head run
<https://github.com/halfb00t/spur/actions/runs/36088409707> (`2c4b544`) is green on all
four jobs (`test (3.10)`, `test (3.12)`, `vendor-bundle`, `image`).

The standing verification this file's "Next step" asked for — "the squash commit must
have a run" — is `make pr.land`'s post-merge check (D-05 step 5), built in Plan 05-02;
it is not re-implemented here.

This file's own "Context" section recorded the repository as private on a free plan, with
no branch protection and no required checks. That premise no longer holds: the repository
is public (read live during Phase 5 planning, 2026-09-25), and D-12 adds a ruleset on
`main` requiring green CI, applied in Plan 05-03. The "Context" section above stays as
written — the history it was when this file was filed, not edited to match what is true
now.
