# Phase 6: Address tech debt: merge gate + solid cache - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-25
**Phase:** 06-address-tech-debt-merge-gate-solid-cache
**Areas discussed:** Hand-typed cut line, pr.land's run verdict, pr.land's post-merge report, Solid cache invariant

---

## Hand-typed cut line

| Option | Description | Selected |
|--------|-------------|----------|
| Drop the cut entirely (Recommended) | The hook always searches the whole buffer; a `git commit -v` whose staged diff quotes a token is refused; nobody here uses `commit.verbose` | ✓ |
| Config-driven cut | Cut only when `commit.verbose`/`commit.cleanup=scissors` says git will truncate; `-v` on the command line still over-matches | |
| Accept the residual | Keep 05-06's editor-only cut; document the backstops; downgrade to nice | |

**User's choice:** Drop the cut entirely.

| Option | Description | Selected |
|--------|-------------|----------|
| Refusal message + HOW_TO_DEVELOP §6 (Recommended) | The refusal names the matched line and says to commit without `-v` if it came from the diff; §6 gets the same line | ✓ |
| Refusal message only | The message is the documentation | |
| You decide | Claude's discretion | |

**User's choice:** Refusal message + HOW_TO_DEVELOP §6.
**Notes:** None.

---

## pr.land's run verdict

| Option | Description | Selected |
|--------|-------------|----------|
| Run conclusion AND the named jobs (Recommended) | `run.conclusion == "success"` plus every listed job present and success; list stays the local file | ✓ |
| Both, plus read required-jobs.txt from the PR head | Also fetch the list at the PR head sha; one more network read | |
| Named jobs from the PR head only | Skip the run-conclusion check | |

**User's choice:** Run conclusion AND the named jobs.

| Option | Description | Selected |
|--------|-------------|----------|
| Resolve the effective name (Recommended) | `jobs.<id>.name` when present, else the id; parse scoped to the job block; regression case renaming `image` | ✓ |
| Reject any job-level name: | Assert none exists, with a message | |
| You decide | Claude's discretion | |

**User's choice:** Resolve the effective name.
**Notes:** None.

---

## pr.land's post-merge report

| Option | Description | Selected |
|--------|-------------|----------|
| Report what was observed; name a token only after reading the commit (Recommended) | Keep the last poll error; three outcomes; token named only after fetching the squash commit's message and running find_skip_tokens | ✓ |
| Observation only, never diagnose | Drop the token claim; print what was observed and the Actions URL | |
| You decide | Claude's discretion | |

**User's choice:** Report what was observed; name a token only after reading the commit.

| Option | Description | Selected |
|--------|-------------|----------|
| State the split explicitly (Recommended) | Docstring + §8: pr.land proves the run-appeared half; staleness between read and merge rests on the ruleset's strict policy | ✓ |
| Close the gap in code too | Re-read behind_by immediately before the merge as well | |
| You decide | Claude's discretion | |

**User's choice:** State the split explicitly.
**Notes:** None.

---

## Solid cache invariant

| Option | Description | Selected |
|--------|-------------|----------|
| A cached solid never carries a mesh (Recommended) | Export from a `.copy()` or strip the triangulation after export; chosen by measurement; proof is a post-export exact BoundingBox test | ✓ |
| Call-site discipline instead | Keep sharing; add an exact_bounds() helper and a grep-test that production never calls .BoundingBox() | |
| Both | The invariant plus the helper | |

**User's choice:** A cached solid never carries a mesh.

| Option | Description | Selected |
|--------|-------------|----------|
| Delete it in the fixing commit (Recommended) | The suite passing without `_reset_solid_cache` is the cross-test proof | ✓ |
| Keep it as a belt | Leave the isolation; the invariant test is the only proof | |
| You decide | Claude's discretion | |

**User's choice:** Delete it in the fixing commit.
**Notes:** None.

---

## Claude's Discretion

- Copy vs strip for the cache invariant (by measurement, numbers recorded).
- Whether `message_to_check` survives or is deleted with the cut.
- Refusal and report wording; test names.
- Decision-log entry count and numbering.
- Where the copy/strip timings are recorded.

## Deferred Ideas

- Reading `required-jobs.txt` from the PR head sha.
- A second `behind_by` read immediately before `gh pr merge`.
- The concurrent-latency investigation (own debt file, own trigger).
- The coverage floor (own debt file).
