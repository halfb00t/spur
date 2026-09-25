# The ship-note's CI skip token leaks into the squash-merge commit and skips CI on `main`

Severity: must
Status: active
Date: 2026-09-25
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
