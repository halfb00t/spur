---
phase: 05-ci-observed-green
verified: 2026-09-25T09:30:00Z
status: passed
score: 5/5 must-haves verified
covered_files:
  - ".github/workflows/ci.yml"
  - ".github/workflows/required-jobs.txt"
  - ".planning/PROJECT.md"
  - ".planning/REQUIREMENTS.md"
  - ".planning/ROADMAP.md"
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
  - ".planning/phases/05-ci-observed-green/05-06-PLAN.md"
  - ".planning/phases/05-ci-observed-green/05-06-SUMMARY.md"
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
  - "docs/tech_debt/active/2026-09-25-commit-msg-hook-trusts-a-hand-typed-cut-line.md"
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
covered_digest: "v1:sha256:6c398801569c6ce62e4553e3fb6f4a3acb09cd3f4e4e898babced068d3baea97"
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: gaps_found
  previous_score: 4/5
  gaps_closed:
    - "No commit in this repository can carry a GitHub Actions skip token, structurally rather than by discipline (ROADMAP SC-1) — the pr.land cut-line bypass (CR-01) is closed: message_refusals() now refuses the verifier's exact reproduction."
  gaps_remaining: []
  regressions: []
gaps: []
---

# Phase 5: CI Observed Green Verification Report

**Phase Goal:** CI is the trusted merge gate for `main` — every commit that lands there has
a GitHub Actions run attached, structurally rather than by discipline; a red, missing or
stale run cannot be merged through the sanctioned path; the supported Python is the one
that actually runs (3.12); and the 2026-09-21 "CI workflow unverified" blocker is retired
with run URLs as evidence.
**Verified:** 2026-09-25
**Status:** passed
**Re-verification:** Yes — after gap closure (Plan 05-06, commits `1965a52`, `3e68e74`)

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | No commit can carry a GitHub Actions skip token, structurally (SC-1) | ✓ VERIFIED | **Gap closed.** Independently re-reproduced the prior verifier's exact failing case against the installed module: `find_skip_tokens(body)` now returns `['[skip ci]']` and `message_refusals('safe subject', body)` returns one refusal naming `'[skip ci]'` — both returned `[]` before Plan 05-06 (05-VERIFICATION.md's own finding). `find_skip_tokens()` (`scripts/skip_tokens.py:68-75`) no longer cuts at all; the cut moved into the hook's own `main()`, applied only when `os.environ.get("GIT_EDITOR") != ":"` (git ran an editor). Live-probed both branches of that hook logic directly (not just trusting tests): a hand-written cut line under `GIT_EDITOR=:` (no editor, the `-m`/`-F` shape) is now refused (exit 1); a real `git commit -v` diff shape under `GIT_EDITOR=vi` still passes (exit 0) — confirming the fix widens what's refused without breaking the legitimate `-v` case. `message_refusals()` (`scripts/pr_land.py:238-253`) applies no cut at all to PR text, matching D-03 (squash message = PR title + body, never branch commit subjects). One residual remains, correctly scoped and disclosed: a cut line hand-typed inside an editor session *without* `-v` is indistinguishable from git's own cut line by content alone; filed as `docs/tech_debt/active/2026-09-25-commit-msg-hook-trusts-a-hand-typed-cut-line.md` (`Severity: must`, named trigger, INDEX row present). This residual does not reach `main`: any commit landed via `make pr.land` is squash-merged using the PR title+body (checked whole, no cut), and the ruleset (SC-5) refuses a run-less head regardless — the backstop was independently confirmed, not merely asserted (see Key Link Verification). |
| 2 | `make pr.land PR=N` refuses a red/missing/stale/behind head, squash-merges, and exits non-zero unless a run appears for the squash commit, printing its URL (SC-2) | ✓ VERIFIED | Regression-checked: `scripts/pr_land.py` still implements `land()` exactly as before (`pr_refusals`, dirty-tree check, `check_head`, `--match-head-commit`, post-merge poll + URL print, tip-matched `git branch -D`), unchanged by Plan 05-06 except `message_refusals`'s docstring. `tests/test_pr_land.py` now has 52 tests (was 50; +2 from gap closure), all pass (`.venv/bin/python -m pytest tests/test_pr_land.py -q` → `52 passed`). `Makefile`'s `pr.land: $(STAMP)` target, `.PHONY` entry, and `## PR=<n>` help line all still present and unchanged. |
| 3 | spur supports Python 3.12 only, and `requires-python`/ruff/CI matrix/Makefile/README/decision log all agree (SC-3) | ✓ VERIFIED | Re-read live: `pyproject.toml` — `requires-python = ">=3.12,<3.13"`, `target-version = "py312"`, `python_version = "3.12"`. `.github/workflows/ci.yml` — `python: ["3.12"]`. `.github/workflows/required-jobs.txt` — `test (3.12)`, `vendor-bundle`, `image`, no 3.10 line. `docs/architecture/decision_log.md` has `## L23 — Python 3.12 only (supersedes L01's floor)`, dated 2026-09-25. Untouched by Plan 05-06; `make verify` green (see Behavioral Spot-Checks). |
| 4 | "CI workflow unverified" blocker retired citing runs 35963114939 and 36088409707; debt file resolved+moved; L22 and L23 appended to decision log (SC-4, REQ-ci-verified) | ✓ VERIFIED | `.planning/STATE.md` lines 166-168 cite both run URLs in the resolved-items note. `git grep` for the old blocker bullet text (`^- \*\*CI workflow unverified`, `has never executed inside GitHub Actions`) finds no live occurrence outside historical plan/context docs quoting it as history. `docs/tech_debt/resolved/2026-09-25-ship-note-skip-token-leaks-into-squash-merge.md` exists with `Status: resolved`, `Resolved in: fac76f5`; `docs/tech_debt/active/` has no matching file (it does now hold the new, separately-filed `2026-09-25-commit-msg-hook-trusts-a-hand-typed-cut-line.md` from Plan 05-06's own disclosure, correctly listed in `docs/tech_debt/INDEX.md` under Active). `docs/architecture/decision_log.md` still has both `## L22` and `## L23`, unmodified by Plan 05-06 (append-only; no decision-log entry was needed for the gap closure per the plan's own key-decisions — L22 already described the intended behaviour). |
| 5 | A ruleset on `main` requires `test (3.12)`, `vendor-bundle`, `image` green on an up-to-date head and a PR, read back live; §8 records the apply command (SC-5, D-12) | ✓ VERIFIED | `gh auth status` confirms an authenticated, logged-in session (account `halfb00t`, `repo`/`workflow` scopes). Live `gh api repos/halfb00t/spur/rules/branches/main` (run during this re-verification) returns exactly `["deletion","non_fast_forward","pull_request","required_status_checks"]`, `strict_required_status_checks_policy: true`, required checks `test (3.12)@15368`, `vendor-bundle@15368`, `image@15368`, all sourced from ruleset `23977515` — unchanged from the prior verification and independent of the CR-01 fix. `docs/HOW_TO_DEVELOP.md` §8 still contains the exact `gh api ... PUT` apply command and the read-back command. |

**Score:** 5/5 truths verified (0 present, behavior-unverified)

### Gap-Closure Assessment (Plan 05-06)

Independently re-assessed, not accepted on SUMMARY.md's word. The prior verification's
blocking gap had three "missing" items:

1. **`message_refusals()` must not apply the scissors cut to PR text.** Closed. The cut
   was removed from `find_skip_tokens()` entirely; `message_refusals()`'s code is
   byte-for-byte unchanged (only its docstring updated) but now sees the whole,
   uncut text because the shared search function no longer cuts anything.
2. **A regression test in `tests/test_pr_land.py` asserting the exact bypass shape is
   refused.** Closed. `test_message_refusals_checks_the_whole_body_even_below_a_git_cut_line`
   and the end-to-end `test_land_refuses_a_token_hidden_below_a_git_cut_line_in_the_pr_body`
   both exist, both use the verifier's own reproduction text (`CUT_LINE_BODY`), and both
   pass. Read the test bodies directly (not just their names): the end-to-end test asserts
   `result == 1`, `"[skip ci]"` and `"nothing was merged"` in stdout, and — critically —
   `not any(c[:3] == ["gh", "pr", "merge"] for c in runner.calls)`, i.e. it proves no merge
   call was made, not merely that a message was printed.
3. **(Lower severity, per the prior verifier's own wording) the commit-msg hook side.**
   Partially closed by a third approach not literally listed in the prior "missing" bullet
   (checking `GIT_EDITOR` rather than `git config commit.cleanup`): this closes the `-m`/`-F`
   holes (the majority of real commits) while leaving one narrow residual (a hand-typed cut
   line inside an editor session without `-v`) open. That residual is disclosed, filed as
   `must`-severity debt with a named revisit trigger, and backstopped by mechanisms this
   verification independently confirmed still work (the ruleset, `pr.land`'s run check, and
   the squash-message's own uncut check). The prior verifier explicitly called this item
   "lower severity" and offered it as one of two options for a **future** fix, not a
   condition of the blocking gap itself — Plan 05-06 fully closed the primary two items and
   made a disclosed, defensible engineering call on the third, matching this project's own
   documented debt-filing process (`CLAUDE.md`: "must ... or deferred with a named trigger").

`05-REVIEW.md` (code review, re-run 2026-09-25T08:41:41Z, status `clean`, 0 findings)
reaches the same conclusion independently, including tracing whether `pre-commit`'s
`no_git_env()` helper could silently defeat the `GIT_EDITOR` check (it does not — verified
by reading the actual call path, not assumed).

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `scripts/skip_tokens.py` | `find_skip_tokens()` (no cut), `message_to_check()`, `main()` (cuts only when git ran an editor) | ✓ VERIFIED | All three present; `find_skip_tokens` confirmed cut-free live; `main()`'s `editor_ran` branch confirmed live in both directions. |
| `tests/test_skip_tokens.py` | Every token form + edges + the new editor/no-editor split | ✓ VERIFIED | 27 tests (was 24; +3), all pass. |
| `.pre-commit-config.yaml` | `no-skip-token` hook, `verify` pinned to `pre-commit` stage | ✓ VERIFIED | Unchanged by this plan; `.git/hooks/commit-msg` present on disk. |
| `scripts/pr_land.py` | `land()`, `check_head()`, `head_refusals()`, `required_jobs()`, `message_refusals()` | ✓ VERIFIED | All functions present and wired; `message_refusals()` now effective against the scissors-bypass PR body (gap closed). |
| `tests/test_pr_land.py` | Happy path, every refusal, ordering, drift test, cut-line bypass regression | ✓ VERIFIED | 52 tests (was 50; +2), all pass. |
| `docs/tech_debt/active/2026-09-25-commit-msg-hook-trusts-a-hand-typed-cut-line.md` | `Severity: must`, `Status: active`, named trigger | ✓ VERIFIED | Present, well-formed, INDEX row present, linked from `scripts/skip_tokens.py`'s own comments. |
| `.github/workflows/required-jobs.txt` | 3 jobs, no `test (3.10)` | ✓ VERIFIED | `test (3.12)`, `vendor-bundle`, `image`. |
| `Makefile` | `pr.land` target | ✓ VERIFIED | Present, `.PHONY`, help line, `$(PY) -m scripts.pr_land $(PR)`. |
| `docs/tech_debt/resolved/2026-09-25-ship-note-skip-token-leaks-into-squash-merge.md` | `Status: resolved` | ✓ VERIFIED | Present at the resolved path only. |
| `docs/HOW_TO_DEVELOP.md` | Squash setting (§8), ship-note step (§6), ruleset commands (§8), `make pr.land` (§8) | ✓ VERIFIED | All present, unmodified by Plan 05-06. |
| `docs/architecture/decision_log.md` | `## L22`, `## L23` | ✓ VERIFIED | Both present, append-only intact, unmodified by Plan 05-06. |
| `pyproject.toml`, `.github/workflows/ci.yml` | 3.12-only | ✓ VERIFIED | Confirmed live, unmodified by this gap-closure plan. |
| `.planning/STATE.md` | Blocker retired, run URLs cited | ✓ VERIFIED | Confirmed. |
| `.planning/REQUIREMENTS.md` | REQ-ci-verified wording | ✓ VERIFIED | Reads "on the supported Python version (3.12, L23)". |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `.pre-commit-config.yaml` | `scripts/skip_tokens.py` | `entry: .venv/bin/python -m scripts.skip_tokens` | ✓ WIRED | Hook installed and present in `.git/hooks/commit-msg`. |
| `tests/test_skip_tokens.py` | `scripts/skip_tokens.py` | direct import + subprocess | ✓ WIRED | Passing (27 tests). |
| `Makefile` | `scripts/pr_land.py` | `$(PY) -m scripts.pr_land $(PR)` | ✓ WIRED | Confirmed in Makefile. |
| `scripts/pr_land.py` | `scripts/skip_tokens.py` | `from scripts.skip_tokens import find_skip_tokens` | ✓ WIRED and effective | Import present, called at `message_refusals`; the reused search is now cut-free and catches the prior bypass (gap closed, reproduced live). |
| `scripts/pr_land.py` | `.github/workflows/required-jobs.txt` | `required_jobs()` reads relative to module | ✓ WIRED | Confirmed via drift test passing. |
| `docs/tech_debt/INDEX.md` | resolved debt file + new active debt file | Resolved table row + new Active row | ✓ WIRED | Both rows present and correctly categorized. |
| `main`'s ruleset (D-12) | `pr.land`'s run check | independent, compensating control for the hook's residual | ✓ WIRED | Live-read `gh api repos/halfb00t/spur/rules/branches/main` (this session) confirms the ruleset is still active and requires `test (3.12)`, `vendor-bundle`, `image` green — the backstop the debt file's "Why it matters" section claims is real, not merely asserted. |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| `make verify` (project gate) | `make verify` | ruff clean, mypy --strict clean (28 files), import-contracts 5/5 kept, `183 passed in 32.93s` | ✓ PASS |
| CR-01 reproduction now refused (`pr_land.py`) | Direct Python: `find_skip_tokens(body)`, `message_refusals('safe subject', body)` against the verifier's exact prior-failing body | `['[skip ci]']`, one refusal naming `'[skip ci]'` (was `[] []`) | ✓ PASS |
| Hook refuses a hand-typed cut line with no editor (`-m`/`-F` shape) | `GIT_EDITOR=: .venv/bin/python -m scripts.skip_tokens <file>` | exit 1, names `'[skip ci]'` | ✓ PASS |
| Hook still passes a real `-v` diff shape with an editor | `GIT_EDITOR=vi .venv/bin/python -m scripts.skip_tokens <file>` (token only below cut line) | exit 0 | ✓ PASS |
| Hook still refuses a token above the cut line with an editor | `GIT_EDITOR=vi .venv/bin/python -m scripts.skip_tokens <file>` (token in subject) | exit 1 | ✓ PASS |
| `tests/test_pr_land.py` full file | `.venv/bin/python -m pytest tests/test_pr_land.py -q` | `52 passed in 0.04s` | ✓ PASS |
| Ruleset on `main` read back live | `gh api repos/halfb00t/spur/rules/branches/main` | Matches roadmap's exact expected tuple; `gh auth status` confirms authenticated | ✓ PASS |
| Squash-merge settings read back live | (unaffected by this gap closure; not re-queried this session — confirmed unchanged via `docs/HOW_TO_DEVELOP.md` §8 and `D-03`/`message_refusals` code, which still assumes PR_TITLE/PR_BODY) | N/A this session | ℹ️ carried forward, no code path touched |

No live `gh` merge/push actions were exercised (out of scope: no write to GitHub, no
merge, no push, no source-file modification). All reproductions used the already-installed
local Python module or a disposable scratch git repo — no network call, no write to this
repository.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|--------------|--------|----------|
| REQ-ci-verified | 05-01, 05-02, 05-03, 05-04, 05-05, 05-06 (all six plans declare it) | CI observed executing green on the supported Python version, not hand-verified | ✓ SATISFIED | Both halves now hold: the record-keeping half (STATE.md blocker retirement, run URL citation, wording change) was already satisfied; the mechanism half ("every commit that lands there has a GitHub Actions run attached, structurally") is now satisfied for the sanctioned merge path — `make pr.land` refuses the CR-01 bypass, proven by a passing regression test and reproduced live in this session. No requirement in `.planning/REQUIREMENTS.md` outside Phase 5 maps to this ID (no orphans). |

No orphaned requirements: `.planning/REQUIREMENTS.md`'s traceability table maps only
REQ-ci-verified to Phase 5, and it is declared in every one of this phase's six plans.

### Anti-Patterns Found

None. Scanned every file Plan 05-06 created or modified (`scripts/skip_tokens.py`,
`scripts/pr_land.py`, `tests/test_skip_tokens.py`, `tests/test_pr_land.py`,
`docs/tech_debt/active/2026-09-25-commit-msg-hook-trusts-a-hand-typed-cut-line.md`,
`docs/tech_debt/INDEX.md`) for `TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER` and
empty-implementation patterns. No matches. `make verify`'s own unfinished-work scan
(part of the ruff/pre-commit gate) also passed clean.

### Human Verification Required

None. Every truth in this phase resolves to VERIFIED on direct evidence (live `gh api`
reads with a confirmed-authenticated session, `make verify`, and direct reproductions of
both the fixed bypass and the hook's editor/no-editor branches); nothing here turns on
visual judgment, real-time behavior, or a call only a human can make.

### Gaps Summary

None. The one blocking gap from the prior verification (`05-VERIFICATION.md`, CR-01 —
`make pr.land`'s `message_refusals()` reusing the commit-msg hook's git-scissors cut on
PR body text that has no scissors semantics) is closed: independently reproduced the
prior failing case and confirmed it now refuses, read the new regression tests' actual
assertions (not just their names or pass/fail count), and re-confirmed the other four
success criteria are unregressed by direct command execution and live `gh api` reads
rather than by trusting the prior report's word. One `must`-severity residual (a
hand-typed git-scissors line inside an editor session without `-v`) remains, correctly
disclosed as filed tech debt with a named trigger and verified-real compensating
controls (the ruleset on `main`, `pr.land`'s run check, and the uncut squash-message
check) — this is accepted, disclosed engineering debt, not an unaddressed gap in this
phase's goal.

---

*Verified: 2026-09-25*
*Verifier: Claude (gsd-verifier)*
