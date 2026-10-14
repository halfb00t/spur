---
name: reverify-phase
description: >-
  Re-verify a phase whose VERIFICATION.md went stale. Use when /gsd-ship refuses because
  the verification is stale, or after a fix landed on a verified phase (a code review, a
  cross-CLI review, a late bug) and the report must be regenerated before shipping.
---

# Re-verify a phase after post-verification fixes

## Why it happens

`VERIFICATION.md` carries `covered_files` and a `covered_digest`. Any later commit that
touches a covered file turns `verification.status` to `stale`, and `/gsd-ship` refuses.
That is correct. Only the `gsd-verifier` agent writes the digest -- never hand-write
`covered_digest` or a status: it would assert a check nobody ran.

## Steps

1. Read the state. `gsd_run` is `node "$HOME/.claude/gsd-core/bin/gsd-tools.cjs"`:
   `gsd_run query verification.status <phase_dir>` -- note `status` and `next_command`.
2. Run the `next_command` it names, `/gsd-execute-phase N`. Since GSD 1.16.0 (#4682) it
   resumes at the phase gates and re-runs the verifier. Phase 24 re-verified this way.
3. Fallback, only if step 2 refuses: dispatch `gsd-verifier`, with the model from
   `gsd_run query resolve-model gsd-verifier`. Give it the phase dir, the goal, the
   requirement ids, the exact delta `git diff --stat <old-report-sha>..HEAD -- <covered files>`
   and why it happened. Tell it not to commit. Then commit the report by hand as
   `docs(NN): re-verify phase N after <why>` (the pre-commit hook runs `make verify.fast`).
4. Ship: `/gsd-ship N`.

History: the loop hit five times (Phase 9 twice, 17, 23, 24) before it became this skill.
