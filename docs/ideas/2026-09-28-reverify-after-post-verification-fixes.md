# A recipe (or skill) for re-verifying a phase after post-verification fixes

Date: 2026-09-28
Source: shipping Phase 9 (PR #10) — `/gsd-ship` blocked twice on a stale `VERIFICATION.md`
Related files:
- `docs/HOW_TO_DEVELOP.md` §6 (the ship-note workaround lives there; this belongs next to it)
- `.ai_skills/README.md` (the candidate home if it repeats once more)
- `.planning/phases/09-keyway-bore/09-VERIFICATION.md` (re-written twice this way)

## Context
`VERIFICATION.md` carries `covered_files` and a `covered_digest`; any later commit that
touches a covered file (source, tests, README, bench results, the decision log) turns
`gsd_run query verification.status` to `stale`, and `/gsd-ship` refuses. That is correct.
What is not: ship's own unblock message says "re-run `/gsd-verify-work`", and verify-work's
completion step says the same thing back — verify-work runs UAT and never touches the
digest. Only the `gsd-verifier` agent writes it (`verification.fingerprint`, agent rule
#4155: never hand-write `covered_digest`), and nothing in the ship → verify loop dispatches
it. Upstream GSD behaviour (1.14.0), the same family as the STATE.md-fingerprint note in
`.planning/STATE.md`'s Blockers.

This session hit it twice: after the code-review fixes (`f4818a0`, `7a88d7a`), and again
after the Codex cross-review fix (`882dd76`). Each time the working recipe was: dispatch
`gsd-verifier` (model per `gsd_run query resolve-model gsd-verifier`) with the phase dir,
goal, requirement IDs and — the part that makes the re-run cheap and honest — the exact
delta since the last report (`git diff --stat <old-report-sha>..HEAD -- <covered files>`)
and why it happened; tell it not to commit; commit the report by hand (`docs(NN): re-verify
phase N after …`, the pre-commit hook runs `make verify.fast`; before L36 it ran `make verify`); then `/gsd-ship N`. Each run was
~4 min of agent time and re-ran the full gate (397 → 407 tests).

## Why it matters
Every cross-CLI review that finds something real produces a post-verification fix, so the
loop is the normal path, not an edge case. Without a recipe the next session re-derives it
(this one spent the first `/gsd-ship` attempt discovering that verify-work cannot help), or
worse, hand-writes the digest — which would assert a check nobody ran (L08's spirit applied
to planning artefacts).

## Next step
Add a short paragraph to `HOW_TO_DEVELOP.md` §6 next to the ship-note workaround: "a fix
after verification re-stales the report; re-dispatch `gsd-verifier` with the delta, commit,
re-ship". If it happens a third time, encode it as `.ai_skills/reverify-phase` per
`.ai_skills/README.md`'s "twice is a skill" rule. Revisit if a GSD update makes ship or
verify-work dispatch the verifier itself.
