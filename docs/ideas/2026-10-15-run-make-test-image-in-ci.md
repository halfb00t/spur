# Run `make test-image` in CI

Date: 2026-10-15
Source: Phase 26, 26-06 -- CONTEXT Deferred Ideas
Related files:
- `Makefile` -- `test-image`
- `.github/workflows/ci.yml`
- `.github/workflows/required-jobs.txt`

## Context
The image suite went red unseen: no job runs it. CI's `image` job builds the container and smoke-tests it, not the
suite. 26-06 ran `make test-image` for the first time and read 29 failures and 5 collection errors (the host-file
reads the image does not hold, and one test needing two pytest plugins the image lacked), all since fixed or ignored
by name in the recipe.

## Why it matters
Without a run it can rot red again, and the documented no-local-Python path (`docs/HOW_TO_DEVELOP.md`) stops telling
the truth. The one run cost 14 minutes serial under amd64 emulation on an arm64 host, so a job is not free either.

## Next step
A CI job running `make test-image`. It joins `required-jobs.txt` and every PR's required checks, which is a cost on
every PR. Revisit when the image suite is next found red or CI time is next budgeted.
