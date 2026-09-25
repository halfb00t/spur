---
phase: 05-ci-observed-green
verified: 2026-09-25T00:00:00Z
status: gaps_found
score: 4/5 must-haves verified
covered_files:
  - ".github/workflows/ci.yml"
  - ".github/workflows/required-jobs.txt"
  - ".planning/PROJECT.md"
  - ".planning/REQUIREMENTS.md"
  - ".planning/STATE.md"
  - ".planning/codebase/CONCERNS.md"
  - ".planning/codebase/CONVENTIONS.md"
  - ".planning/codebase/INTEGRATIONS.md"
  - ".planning/codebase/STACK.md"
  - ".planning/phases/05-ci-observed-green/05-01-PLAN.md"
  - ".planning/phases/05-ci-observed-green/05-01-SUMMARY.md"
  - ".planning/phases/05-ci-observed-green/05-02-PLAN.md"
  - ".planning/phases/05-ci-observed-green/05-02-SUMMARY.md"
  - ".planning/phases/05-ci-observed-green/05-03-PLAN.md"
  - ".planning/phases/05-ci-observed-green/05-03-SUMMARY.md"
  - ".planning/phases/05-ci-observed-green/05-04-PLAN.md"
  - ".planning/phases/05-ci-observed-green/05-04-SUMMARY.md"
  - ".planning/phases/05-ci-observed-green/05-05-PLAN.md"
  - ".planning/phases/05-ci-observed-green/05-05-SUMMARY.md"
  - ".planning/phases/05-ci-observed-green/05-CONTEXT.md"
  - ".planning/phases/05-ci-observed-green/05-REVIEW.md"
  - ".pre-commit-config.yaml"
  - "AGENTS.md"
  - "Makefile"
  - "README.md"
  - "docs/CODING_VALUES.md"
  - "docs/HOW_TO_DEVELOP.md"
  - "docs/architecture/decision_log.md"
  - "docs/architecture/overview.md"
  - "docs/architecture/packaging.md"
  - "docs/tech_debt/INDEX.md"
  - "docs/tech_debt/resolved/2026-09-25-ship-note-skip-token-leaks-into-squash-merge.md"
  - "pyproject.toml"
  - "scripts/pr_land.py"
  - "scripts/skip_tokens.py"
  - "src/spur/build_errors.py"
  - "src/spur/params.py"
  - "src/spur/pool.py"
  - "src/spur/records.py"
  - "tests/test_pool.py"
  - "tests/test_pr_land.py"
  - "tests/test_skip_tokens.py"
covered_digest: "v1:sha256:16cca1bdfe8ee812103072ce27528e3324033c3ff5e2682981f88555ae1f8f16"
behavior_unverified: 0
overrides_applied: 0
gaps:
  - truth: "No commit in this repository can carry a GitHub Actions skip token, structurally rather than by discipline (ROADMAP SC-1)"
    status: failed
    reason: >
      The code review's CR-01 finding is correct and independently reproduced. `find_skip_tokens()`
      (via `message_to_check()`/`_SCISSORS`) truncates the text it scans at the first line matching
      git's `commit -v` scissors marker, on the assumption that everything past it is diff text git
      already discarded. That assumption holds only for `git commit -v`'s auto-selected
      `cleanup=scissors` mode. `scripts/pr_land.py`'s `message_refusals()` applies the exact same
      truncation to a GitHub PR title/body (`subject + "\n\n" + body`) -- text that never passes
      through git's editor or any cleanup mode at all, so the scissors convention has no meaning
      there. A PR body containing the literal 51-character scissors line followed by a skip token
      passes `message_refusals()` with zero refusals, and `land()` then squash-merges with
      `--body pr.body` (the full, untruncated body) as the literal squash commit message on `main`
      -- reproducing exactly the failure this phase exists to close (a skip-token-carrying commit
      reaching `main`, silently skipped by GitHub Actions), through the one checker built to catch
      it at the last gate before merge. Reproduced directly against the installed module:
      `find_skip_tokens('A normal PR description.\n\n# ------------------------ >8 ------------------------\n[skip ci]\n')`
      returns `[]`, and `message_refusals('safe subject', <same body>)` also returns `[]` (no
      refusal), confirmed 2026-09-25 against this checkout. No test in `tests/test_pr_land.py`
      exercises a scissors line in the PR body -- `tests/test_skip_tokens.py`'s
      `test_token_only_below_the_scissors_line_gives_no_tokens` encodes the truncation as intended
      behavior for a git commit message, but `pr_land.py` reuses it unmodified for text that has no
      git cleanup semantics at all.
    artifacts:
      - path: "scripts/skip_tokens.py"
        issue: "`message_to_check()` (lines 52-55) / `_SCISSORS` (line 49) truncate on a content-pattern match with no way to confirm the text actually passed through git's `cleanup=scissors` mode -- correct only for the commit-msg hook's own caller, not for `pr_land.py`'s reuse."
      - path: "scripts/pr_land.py"
        issue: "`message_refusals()` (lines 238-249) calls `find_skip_tokens(subject + \"\\n\\n\" + body)` where `body` is `pr.body`, a GitHub PR body with no scissors semantics; `land()` (line 402) calls it before merging, then (lines 408-421) passes the same untruncated `pr.body` as `--body` to `gh pr merge`, so a token past a forged scissors line reaches `main`'s real commit message unchecked."
    missing:
      - "`pr_land.py`'s `message_refusals()` must not apply the scissors cut at all -- a PR title/body has no git scissors semantics to respect. Either call the raw pattern search directly (bypassing `message_to_check`), or add a `cut: bool` parameter / a `find_skip_tokens_raw()` that `pr_land.py` calls with the cut disabled."
      - "A regression test in `tests/test_pr_land.py` asserting a PR body containing the scissors line followed by a token is refused by `message_refusals()`."
      - "Separately (the commit-msg hook side, lower severity because `-m`/`-F` commits use `cleanup=strip` by default, not `cleanup=scissors`): either drop the truncation in `scripts/skip_tokens.py` and accept the stated over-match preference, or verify `git config --get commit.cleanup` resolves to `scissors` before trusting the cut, since content alone cannot prove which cleanup mode produced a message."
---

# Phase 5: CI Observed Green Verification Report

**Phase Goal:** CI is the trusted merge gate for `main` -- every commit that lands there has
a GitHub Actions run attached, structurally rather than by discipline; a red, missing or
stale run cannot be merged through the sanctioned path; the supported Python is the one
that actually runs (3.12); and the 2026-09-21 "CI workflow unverified" blocker is retired
with run URLs as evidence.
**Verified:** 2026-09-25
**Status:** gaps_found
**Re-verification:** No -- initial verification

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | No commit can carry a GitHub Actions skip token, structurally (SC-1) | ✗ FAILED | See Gaps below. Commit-msg hook works for plain `git commit` (24 passing tests, live-installed hook, `default_install_hook_types` covers `commit-msg`); the squash-merge setting reads back `PR_TITLE`/`PR_BODY` live. But the mechanism meant to check the squash commit's own text (`message_refusals`, the only check covering `make pr.land`'s server-side squash merge) has a proven, reproduced bypass via a forged git-scissors line in the PR body. |
| 2 | `make pr.land PR=N` refuses a red/missing/stale/behind head, squash-merges, and exits non-zero unless a run appears for the squash commit, printing its URL (SC-2) | ✓ VERIFIED | `scripts/pr_land.py` implements `land()` exactly as described: `pr_refusals`, dirty-tree check, `check_head` (job + behind refusals), `--match-head-commit` binding, post-merge poll with URL print, local follow-up with tip-matched `git branch -D`. 50 tests in `tests/test_pr_land.py` cover the happy path, every refusal, both ordering directions, the drift test, and pass (`make verify`, 178/178). `Makefile` has `pr.land: $(STAMP)` target, `.PHONY` entry, `## PR=<n>` help line. (Skip-token refusal is part of this file's own must-haves, and is exactly the mechanism found broken in Truth 1 -- see Gaps; SC-2's literal roadmap wording does not itself name the token check, so this criterion's own five clauses hold as written.) |
| 3 | spur supports Python 3.12 only, and `requires-python`/ruff/CI matrix/Makefile/README/decision log all agree (SC-3) | ✓ VERIFIED | `pyproject.toml`: `requires-python = ">=3.12,<3.13"`, `target-version = "py312"`, `python_version = "3.12"`. `.github/workflows/ci.yml`: `python: ["3.12"]`. `.github/workflows/required-jobs.txt`: `test (3.12)`, `vendor-bundle`, `image` (no 3.10 line). `docs/architecture/decision_log.md` has `## L23 — Python 3.12 only (supersedes L01's floor)`. README.md, AGENTS.md, docs/CODING_VALUES.md, docs/architecture/overview.md all state 3.12 only, citing L23. `make verify` is green (178 tests, `.venv/bin/ruff check .` clean). |
| 4 | "CI workflow unverified" blocker retired citing runs 35963114939 and 36088409707; debt file resolved+moved; L22 and L23 appended to decision log (SC-4, REQ-ci-verified) | ✓ VERIFIED | `.planning/STATE.md` lines 164-166 cite both run URLs in the resolved-items note; `git grep` for the old blocker bullet text (`^- \*\*CI workflow unverified`, `has never executed inside GitHub Actions`) finds nothing. `docs/tech_debt/resolved/2026-09-25-ship-note-skip-token-leaks-into-squash-merge.md` exists with `Status: resolved`, `Resolved in: fac76f5` (confirmed = `git log -1 --format=%h -- scripts/skip_tokens.py`); `docs/tech_debt/active/` has no matching file; `docs/tech_debt/INDEX.md` lists it once, under Resolved. `docs/architecture/decision_log.md` has both `## L22` (CI merge gate) and `## L23` (Python 3.12), each dated 2026-09-25, with no removed lines in their commits (append-only intact, spot-checked by reading the full text). |
| 5 | A ruleset on `main` requires `test (3.12)`, `vendor-bundle`, `image` green on an up-to-date head and a PR, read back live; §8 records the apply command (SC-5, D-12) | ✓ VERIFIED | Live `gh api repos/halfb00t/spur/rules/branches/main` (run during this verification, read-only) returns exactly `["deletion","non_fast_forward","pull_request","required_status_checks"]`, strict policy `true`, required checks `image@15368`, `test (3.12)@15368`, `vendor-bundle@15368`, all from ruleset `23977515`. `docs/HOW_TO_DEVELOP.md` §8 contains the exact `gh api ... PUT` apply command, the read-back command, and the removal command, next to the D-03 squash-setting command. |

**Score:** 4/5 truths verified (0 present, behavior-unverified)

### Independent Assessment of Code Review CR-01

The task instructions asked me to independently assess whether CR-01 ("the scissors cut lets
a skip token survive in the exact text `pr.land` is checking") is correct. It is. I reproduced
it directly against the installed module (not by reading only):

```
>>> from scripts.skip_tokens import find_skip_tokens
>>> from scripts.pr_land import message_refusals
>>> body = 'A normal PR description.\n\n# ------------------------ >8 ------------------------\n[skip ci]\n'
>>> find_skip_tokens(body)
[]
>>> message_refusals('safe subject', body)
[]
```

`message_refusals` (`scripts/pr_land.py:238-249`) is called at `scripts/pr_land.py:402`,
before the merge, and returns no refusal for this body. `land()` then squash-merges
(`scripts/pr_land.py:408-421`) passing the same, untruncated `pr.body` as `gh pr merge`'s
`--body` -- so the literal `[skip ci]` reaches `main`'s real commit message, unchecked, and
GitHub Actions would skip the run for that commit. This is precisely the class of bug L22 /
D-02 / D-03 were written to close, reopened through the one checker meant to catch it at the
last gate before merge (`make pr.land`, the phase's own "sanctioned path"). Success criterion
1's "no commit in this repository can carry a GitHub Actions skip token ... structurally" does
not hold as stated: it holds for a plain `git commit`, but not for a squash commit landed
through `make pr.land` with a specially-crafted PR body -- and `make pr.land` is this phase's
own answer to "the sanctioned path" (ROADMAP goal text: "a red, missing or stale run cannot be
merged through the sanctioned path"). I record this as a gap rather than accepting the
SUMMARY.md/plan claim, per the phase instructions.

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `scripts/skip_tokens.py` | `find_skip_tokens()`, `message_to_check()`, `main()` | ✓ VERIFIED (with the CR-01 caveat) | All three functions present, tested, wired to the commit-msg hook. The scissors truncation is correct for its own caller; the bug is in how `pr_land.py` reuses it. |
| `tests/test_skip_tokens.py` | Every token form + edges | ✓ VERIFIED | 24 tests, all pass; covers every token, case variants, scissors edge, encoding edge, empty edge, adjacency edge, subprocess hook-entry cases. |
| `.pre-commit-config.yaml` | `no-skip-token` hook, `verify` pinned to `pre-commit` stage | ✓ VERIFIED | `default_install_hook_types: [pre-commit, commit-msg]`; `no-skip-token` at `stages: [commit-msg]`; `verify` at `stages: [pre-commit]`. Hook installed in `.git/hooks/commit-msg` (confirmed on disk). |
| `scripts/pr_land.py` | `land()`, `check_head()`, `head_refusals()`, `required_jobs()`, `message_refusals()` | ⚠️ VERIFIED but defective | All functions present and wired; `message_refusals()` exists and is called, but is ineffective against the scissors-bypass PR body (see gap). |
| `tests/test_pr_land.py` | Happy path, every refusal, ordering, drift test | ✓ VERIFIED | 50 tests, all pass. No test covers a scissors line in the PR body (the gap's blind spot). |
| `.github/workflows/required-jobs.txt` | 3 jobs, no `test (3.10)` | ✓ VERIFIED | `test (3.12)`, `vendor-bundle`, `image`. |
| `Makefile` | `pr.land` target | ✓ VERIFIED | Present, `.PHONY`, help line, `$(PY) -m scripts.pr_land $(PR)`. |
| `docs/tech_debt/resolved/2026-09-25-ship-note-skip-token-leaks-into-squash-merge.md` | `Status: resolved` | ✓ VERIFIED | Present at the resolved path only; `Resolved in: fac76f5` matches `scripts/skip_tokens.py`'s commit. |
| `docs/HOW_TO_DEVELOP.md` | Squash setting (§8), ship-note step (§6), ruleset commands (§8), `make pr.land` (§8) | ✓ VERIFIED | All present, in Russian, at the described sections. |
| `docs/architecture/decision_log.md` | `## L22`, `## L23` | ✓ VERIFIED | Both present, dated 2026-09-25, append-only intact. |
| `pyproject.toml`, `.github/workflows/ci.yml` | 3.12-only | ✓ VERIFIED | Confirmed live. |
| `.planning/STATE.md` | Blocker retired, run URLs cited | ✓ VERIFIED | Confirmed. |
| `.planning/REQUIREMENTS.md` | REQ-ci-verified wording | ✓ VERIFIED | Reads "on the supported Python version (3.12, L23)". |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `.pre-commit-config.yaml` | `scripts/skip_tokens.py` | `entry: .venv/bin/python -m scripts.skip_tokens` | ✓ WIRED | Hook installed and present in `.git/hooks/commit-msg`. |
| `tests/test_skip_tokens.py` | `scripts/skip_tokens.py` | direct import + subprocess | ✓ WIRED | `from scripts.skip_tokens import ...`; passing. |
| `Makefile` | `scripts/pr_land.py` | `$(PY) -m scripts.pr_land $(PR)` | ✓ WIRED | Confirmed in Makefile. |
| `scripts/pr_land.py` | `scripts/skip_tokens.py` | `from scripts.skip_tokens import find_skip_tokens` | ⚠️ WIRED but ineffective | Import present, called at `message_refusals`, but the reused truncation defeats the check for PR-body text (see gap). |
| `scripts/pr_land.py` | `.github/workflows/required-jobs.txt` | `required_jobs()` reads relative to module | ✓ WIRED | Confirmed via drift test passing and live content match. |
| `docs/tech_debt/INDEX.md` | resolved debt file | Resolved table row | ✓ WIRED | Confirmed link present, Active row absent. |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| `make verify` (project gate) | `make verify` | 178/178 tests passed, ruff/mypy/import-contracts clean | ✓ PASS |
| Squash-merge settings read back live | `gh api repos/halfb00t/spur --jq '{squash_merge_commit_title,squash_merge_commit_message}'` | `{"squash_merge_commit_message":"PR_BODY","squash_merge_commit_title":"PR_TITLE"}` | ✓ PASS |
| Ruleset on `main` read back live | `gh api repos/halfb00t/spur/rules/branches/main` (reduced) | Matches plan's exact expected tuple | ✓ PASS |
| CR-01 scissors-bypass reproduction | Direct Python invocation of `find_skip_tokens`/`message_refusals` against a forged scissors+token body | Both return `[]` (no refusal) for a body carrying a live skip token | ✗ FAIL -- confirms the gap |
| Commit-msg hook installed on this clone | `cat .git/hooks/commit-msg` | pre-commit-generated hook present | ✓ PASS |
| Debt file resolved-sha matches Task 1 commit | `git log -1 --format=%h -- scripts/skip_tokens.py` vs file's `Resolved in:` | Both `fac76f5` | ✓ PASS |

Live `gh api` merge/push actions were not exercised (out of scope per task instructions: no
write to GitHub, no merge, no push, no source-file modification). The CR-01 reproduction used
only the already-installed local Python module -- no network call, no git write.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|--------------|--------|----------|
| REQ-ci-verified | 05-01, 05-02, 05-03, 05-04, 05-05 (all five plans declare it) | CI observed executing green on the supported Python version, not hand-verified | ⚠️ PARTIAL | The record-keeping half (STATE.md blocker retirement, run URL citation, wording change) is fully satisfied. The mechanism half ("every commit that lands there has a GitHub Actions run attached, structurally") is undermined by the CR-01 gap: `make pr.land`, the sanctioned merge path this requirement's phase built, can land a skip-token-carrying commit through a crafted PR body. No requirement in `.planning/REQUIREMENTS.md` outside Phase 5 maps to this ID (no orphans). |

No orphaned requirements: `.planning/REQUIREMENTS.md`'s traceability table maps only
REQ-ci-verified to Phase 5, and it is declared in every one of this phase's five plans.

### Anti-Patterns Found

None. Scanned every file this phase created or modified (`scripts/skip_tokens.py`,
`scripts/pr_land.py`, their tests, `.pre-commit-config.yaml`, `Makefile`,
`.github/workflows/ci.yml`, `.github/workflows/required-jobs.txt`, `src/spur/build_errors.py`,
`src/spur/pool.py`, `src/spur/records.py`, `src/spur/params.py`, `tests/test_pool.py`) for
`TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER` and empty-implementation patterns. The only
match was the Makefile's own unfinished-work-scan rule definition (the debt-marker grep
pattern itself), not a marker.

### Human Verification Required

None. Every truth in this phase resolves to VERIFIED or FAILED on direct evidence (live `gh
api` reads, `make verify`, and a direct reproduction of the CR-01 bypass); nothing here turns
on visual judgment, real-time behavior, or a call only a human can make.

### Gaps Summary

One blocking gap, already detailed above under "Observable Truths" #1 and the frontmatter
`gaps:` entry: `scripts/pr_land.py`'s `message_refusals()` reuses `scripts/skip_tokens.py`'s
git-scissors truncation on GitHub PR body text, which has no scissors semantics at all. A PR
body carrying the literal scissors marker followed by a skip token passes the check silently,
and `make pr.land` then squash-merges that exact body as `main`'s commit message --
reproducing, through the phase's own sanctioned merge tool, the class of bug (a
skip-token-carrying commit reaching `main` with GitHub Actions silently skipping its run) that
this phase exists to close structurally.

This is not a cosmetic issue: it falsifies ROADMAP success criterion 1 as stated ("No commit
in this repository can carry a GitHub Actions skip token ... structurally rather than by
discipline") for the one merge path (`make pr.land`) this phase built to be that structural
guarantee. The fix is narrow and does not require replanning the phase's architecture: either
give `pr_land.py`'s `message_refusals()` a way to search the raw text without the scissors cut,
or gate the cut on a verified `commit.cleanup=scissors`. Both are within `scripts/skip_tokens.py`
and `scripts/pr_land.py` alone, with one new regression test in `tests/test_pr_land.py`.

Everything else this phase set out to build -- the commit-msg hook for plain git commits, the
squash-message setting, `make pr.land`'s stale/red/missing-run refusals and post-merge run
proof, the Python 3.12 collapse, the ruleset on `main`, and the record correction (STATE.md,
decision log, contributor docs) -- is present, wired, and independently confirmed live or by a
passing, non-trivial test suite (178 tests, `make verify` green).

---

*Verified: 2026-09-25*
*Verifier: Claude (gsd-verifier)*
