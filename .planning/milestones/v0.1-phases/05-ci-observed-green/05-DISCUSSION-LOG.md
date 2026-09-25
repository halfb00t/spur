# Phase 5: CI Observed Green - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-09-25
**Phase:** 5-CI Observed Green
**Areas discussed:** Scope, Skip-token leak fix, Red-merge prevention, Evidence & bookkeeping, 3.10 floor locally (became: Python versions)

---

## Scope (pre-discussion finding)

The roadmap premise ("ci.yml has never executed in GitHub Actions") was checked against
`gh api` before any question was asked: 13 runs exist; main push run 35963114939 is green on
all four jobs; the two squash commits on `main` since Phase 2 have no run (skip token
inherited into the squash body); PR #2 was merged with `test (3.10)` red.

| Option | Description | Selected |
|--------|-------------|----------|
| Reframe: trusted gate | Every main commit gets a run structurally; red/missing runs can't merge; blocker retired with URLs; debt file resolved; roadmap text updated | ✓ |
| Bookkeeping only | Record existing run URLs, retire the blocker, leave the skip-token debt file active | |
| Edit roadmap first | Stop; human rewrites the Phase 5 entry, reruns discuss | |

**User's choice:** Reframe: trusted gate
**Notes:** All four proposed gray areas were selected for discussion.

---

## Skip-token leak fix

| Option | Description | Selected |
|--------|-------------|----------|
| commit-msg hook + squash setting | Repo-owned commit-msg hook rejects the six GitHub tokens; `gh api PATCH` sets squash_merge_commit_message=PR_BODY | ✓ |
| commit-msg hook only | Tokens never enter history; main keeps the concatenated-subjects body | |
| Squash setting only | One PATCH; PR head still skipped by ship's note, so every ship needs an empty trigger commit | |

**User's choice:** commit-msg hook + squash setting

| Option | Description | Selected |
|--------|-------------|----------|
| Manual step, documented | HOW_TO_DEVELOP §6: after `/gsd-ship N`, commit STATE.md as `docs(NN): ship phase N — PR #M` (no token) and push | ✓ |
| Project skill wraps ship | An `.ai_skills/ship` skill runs gsd-ship then commits the note without the token | |
| Ship note stays local-only | Record the ship in STATE.md on main after merge | |

**User's choice:** Manual step, documented

| Option | Description | Selected |
|--------|-------------|----------|
| PR title + PR body | squash_merge_commit_title=PR_TITLE, squash_merge_commit_message=PR_BODY | ✓ |
| PR title only | squash_merge_commit_message=BLANK | |
| Keep concatenated subjects | Leave COMMIT_MESSAGES; rely on the hook alone | |

**User's choice:** PR title + PR body
**Notes:** User chose "Next area" after three questions.

---

## Red-merge prevention

| Option | Description | Selected |
|--------|-------------|----------|
| Merge only via a checked make target | `make pr.land PR=N`: refuses unless checks green for the exact head sha, refuses on zero checks, squash-merges, verifies the squash commit has a run. A tool, not a wall | ✓ |
| Make the repo public | Unlocks branch protection + required checks + unlimited minutes; a visibility decision | |
| GitHub Pro | Branch protection on private repos for a fee | |
| Doc rule only | Keep §8 as is | |

**User's choice:** Merge only via a checked make target

| Option | Description | Selected |
|--------|-------------|----------|
| The four named jobs, all green | Exact job set must exist and be success for the head sha; a missing job is a refusal | ✓ |
| All existing checks green, count > 0 | Tolerant of workflow edits; a deleted job silently stops being required | |

**User's choice:** The four named jobs, all green (three jobs after the Python decision)

| Option | Description | Selected |
|--------|-------------|----------|
| Refuse if behind main | `behind_by > 0` → rebase, push, rerun CI, retry | ✓ |
| Merge anyway, warn | Proceed; the post-merge run is the first test of that tree | |

**User's choice:** Refuse if behind main

| Option | Description | Selected |
|--------|-------------|----------|
| Wait until the run exists, print its URL | Poll ~60 s for a run on the squash sha; none → non-zero; don't wait for green | ✓ |
| Wait for green | Block ~3 min until the main run completes | |
| Just merge | No post-merge check | |

**User's choice:** Wait until the run exists, print its URL
**Notes:** User chose "Next area" after four questions.

---

## Evidence & bookkeeping

| Option | Description | Selected |
|--------|-------------|----------|
| Record what exists now + pr.land prints Phase 5's own | Blocker retired citing runs 35963114939 and 36088409707; Phase 5's own squash run URL printed at merge, recorded on the next STATE.md touch | ✓ |
| Only Phase 5's own post-merge run counts | Blocker stays open until merge; docs-only commit on main | |

**User's choice:** Record what exists now + pr.land prints Phase 5's own

| Option | Description | Selected |
|--------|-------------|----------|
| New L22 | Dated, appended merge-gate entry citing the runs and PR #2's red merge | ✓ |
| No log entry | HOW_TO_DEVELOP carries the rule | |

**User's choice:** New L22 (a second entry, L23, was added later for the Python decision)

| Option | Description | Selected |
|--------|-------------|----------|
| Now, before planning | `/gsd-phase --edit 5` right after this discussion | ✓ |
| At phase completion | Correct the roadmap when the phase closes | |

**User's choice:** Now, before planning

| Option | Description | Selected |
|--------|-------------|----------|
| In the fix commit, per CLAUDE.md | Status: resolved + sha in the same commit as hook + setting | ✓ |
| After the merge is observed | Stays active until the squash commit's run is seen | |

**User's choice:** In the fix commit, per CLAUDE.md
**Notes:** User chose "Next area" after four questions.

---

## 3.10 floor locally → Python versions

The prepared question ("How is the 3.10 floor checked before code reaches main?" — CI only /
also document a local floor run / 3.10 in the pre-commit hook) was not answered. The user
asked for the problem to be described, then asked "Do we really need 3.10? Why do we use it
at all?". Answer given: L01 says "detected, not chosen" — the range is what `cadquery-ocp`
publishes wheels for; the ceiling is real, the floor is not a requirement anyone stated; the
image, dev machine and hook are all 3.12; CI's leg is the only 3.10 execution ever; mypy
cannot hold a floor below 3.12 (numpy stubs). The question was reformulated:

| Option | Description | Selected |
|--------|-------------|----------|
| 3.12 only | Supersede L01's floor: requires-python >=3.12,<3.13, ruff py312, matrix ["3.12"], README/L01 updated; mypy version == runtime | ✓ |
| Keep 3.10–3.12 | L01 stands; CI's `test (3.10)` leg is the only floor check, made binding by pr.land | |
| 3.11–3.12 | Drop only 3.10; keeps a floor mypy cannot hold | |

**User's choice:** 3.12 only
**Notes:** Done in Phase 5 because it edits the same ci.yml and the pr.land job list.

---

## Done check

| Option | Description | Selected |
|--------|-------------|----------|
| I'm ready for context | Write CONTEXT.md and DISCUSSION-LOG.md, commit | ✓ |
| Explore more gray areas | Candidates offered: how pr.land is tested; whether `make check` asserts the hook + setting; the stale remote branches | |

## Claude's Discretion

- Hook install mechanics (`default_install_hook_types`), hook language/location and its test.
- `pr.land` implementation (shell vs Python), pure decision logic tested against recorded `gh` JSON; folding §8's local git steps into it.
- One-entry matrix vs bare `test` job; explicit `<3.13` upper bound; mypy comment rewrite.
- Whether `make check` asserts the repo squash setting (leaning no).
- L22/L23 numbering order; wording of the Russian HOW_TO_DEVELOP edits.

## Deferred Ideas

- Branch protection / required checks (public repo or GitHub Pro) — the only true wall.
- Actions minutes budget on the private free plan — unmeasured.
- Deleting the three stale remote branches.
- `make check` asserting repository settings.
- A local 3.10 floor run — moot after the 3.12-only decision.
