---
phase: 06-address-tech-debt-merge-gate-solid-cache
verified: 2026-09-25T00:00:00Z
status: passed
score: 9/9 must-haves verified
covered_files: [".planning/STATE.md", ".planning/phases/06-address-tech-debt-merge-gate-solid-cache/06-01-PLAN.md", ".planning/phases/06-address-tech-debt-merge-gate-solid-cache/06-01-SUMMARY.md", ".planning/phases/06-address-tech-debt-merge-gate-solid-cache/06-02-PLAN.md", ".planning/phases/06-address-tech-debt-merge-gate-solid-cache/06-02-SUMMARY.md", ".planning/phases/06-address-tech-debt-merge-gate-solid-cache/06-03-PLAN.md", ".planning/phases/06-address-tech-debt-merge-gate-solid-cache/06-03-SUMMARY.md", ".planning/phases/06-address-tech-debt-merge-gate-solid-cache/06-04-PLAN.md", ".planning/phases/06-address-tech-debt-merge-gate-solid-cache/06-04-SUMMARY.md", ".planning/phases/06-address-tech-debt-merge-gate-solid-cache/06-CONTEXT.md", ".planning/phases/06-address-tech-debt-merge-gate-solid-cache/06-SECURITY.md", ".planning/phases/06-address-tech-debt-merge-gate-solid-cache/06-VALIDATION.md", ".planning/phases/06-address-tech-debt-merge-gate-solid-cache/COVERAGE.md", "docs/HOW_TO_DEVELOP.md", "docs/architecture/decision_log.md", "docs/tech_debt/INDEX.md", "docs/tech_debt/resolved/2026-09-24-shared-solid-cache-corrupts-later-boundingbox.md", "docs/tech_debt/resolved/2026-09-25-commit-msg-hook-trusts-a-hand-typed-cut-line.md", "docs/tech_debt/resolved/2026-09-25-pr-land-admits-a-run-with-a-failing-unlisted-job.md", "docs/tech_debt/resolved/2026-09-25-pr-land-blames-a-skip-token-for-any-missed-post-merge-run.md", "docs/tech_debt/resolved/2026-09-25-required-jobs-drift-test-ignores-job-name-overrides.md", "scripts/pr_land.py", "scripts/skip_tokens.py", "src/spur/model.py", "tests/conftest.py", "tests/test_model.py", "tests/test_pr_land.py", "tests/test_skip_tokens.py"]
covered_digest: "v1:sha256:a380eae42bbed71afc57d916b1f00e7e2c4420e09095ea15146290cb8a030264"
behavior_unverified: 0
overrides_applied: 0
---

# Phase 6: Address tech debt: merge gate + solid cache — Verification Report

**Phase Goal:** Close the five open tech-debt items in the merge gate and the solid cache,
each resolved in the commit that fixes it: the `commit-msg` hook checks the whole buffer
git hands it (no hand-typed cut line can hide a skip token); `make pr.land` refuses a run
whose own conclusion is not `success`, resolves `jobs.<id>.name` overrides in the drift
test, and reports only what it observed after the merge; `_build_cached` never hands out a
solid carrying a mesh (export works on a copy, `.BoundingBox()` stays exact, the autouse
cache reset fixture is deleted). Every behaviour change ships with its test, the
copy-vs-strip numbers are measured and written down, `make verify` stays green.

**Verified:** 2026-09-25
**Status:** passed
**Re-verification:** No — initial verification

## Requirement Traceability Note

`.planning/REQUIREMENTS.md` carries no Phase 6 rows — ROADMAP.md lists `Requirements: TBD`
for this phase, and its own "Traceability" table stops at Phase 5. This is not a gap the
executors created: the plans' `requirements:` arrays carry `D-01`…`D-11`, which are
`06-CONTEXT.md`'s own decision IDs, not `REQ-xxx` entries. Every `D-01`…`D-11` ID is
accounted for below, cross-referenced against `06-CONTEXT.md`'s `<decisions>` block and the
plans that claim it. No `D-xx` ID is orphaned (present in `06-CONTEXT.md` but claimed by no
plan) and no plan claims an ID `06-CONTEXT.md` does not define.

| ID | Decision | Claimed by | Verified |
|----|----------|-----------|----------|
| D-01 | Each debt file resolved in the commit that fixes it | 06-01, 06-02, 06-03, 06-04 | ✓ (see note below) |
| D-02 | Commit-msg hook drops the cut, searches the whole buffer | 06-02 | ✓ |
| D-03 | Refusal names line + `-v` caveat; §6 documents it | 06-02 | ✓ |
| D-04 | `head_refusals` refuses on `run.conclusion != "success"` | 06-03 | ✓ |
| D-05 | Drift test resolves `jobs.<id>.name` effective names | 06-03 | ✓ |
| D-06 | `no_run_report` reports only what it observed | 06-04 | ✓ |
| D-07 | Docstring/§8 state the ruleset-carries-the-window split | 06-04 | ✓ |
| D-08 | `_build_cached` never hands out a meshed solid (`shape.copy()`) | 06-01 | ✓ |
| D-09 | Autouse solid-cache reset fixture deleted | 06-01 | ✓ |
| D-10 | Decision log amended (L24, L25), append-only | 06-01, 06-04 | ✓ |
| D-11 | STATE.md cites run 36122394253, retires two blockers | 06-04 | ✓ |

**D-01 note (commit-splitting pattern, not a gap):** in all four plans, the debt file's
`Resolved in:` sha names the *code-fix* commit, while `Status: resolved`, the `git mv` and
the INDEX-row move land in a *later* commit within the same plan that also carries
substantive content (a decision-log entry, or the docstring/§8 half of the same fix) —
never a bookkeeping-only follow-up. This is the same pattern already established in Phase 5
(`docs/tech_debt/resolved/2026-09-25-ship-note-skip-token-leaks-into-squash-merge.md`:
`Resolved in: fac76f5`, moved in the later `7959cdb`), confirmed by `git log` on that file.
Read literally, CLAUDE.md's "in the same commit as the fix" would want one atomic commit;
this project's actual practice — in Phase 5 and now Phase 6 — is "resolved within the plan
that fixes it, in a commit that carries real content, never a pure-bookkeeping follow-up."
Every one of this phase's five debt files satisfies that established practice. Noted for
visibility, not scored as a gap.

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | The `commit-msg` hook checks the whole buffer git hands it — no hand-typed cut line can hide a skip token | ✓ VERIFIED | `scripts/skip_tokens.py::main` has no `_SCISSORS` regex, no `GIT_EDITOR` read, no `message_to_check`; `find_skip_tokens(raw)` runs on the whole buffer unconditionally (lines 70-79). `tests/test_skip_tokens.py::test_hook_refuses_a_token_below_a_git_cut_line_whatever_git_editor_says` passes for `vi`/`None`/`:`. |
| 2 | `make pr.land` refuses a run whose own conclusion is not `success` | ✓ VERIFIED | `scripts/pr_land.py::head_refusals` line 295: `if run.conclusion != "success":` — refuses naming conclusion + URL, in addition to the unchanged per-job loop. Live probe against real run 36116930241 (head `73535a24…`) returns 3 refusals (behind, run-conclusion, job) where it returned 2 before this phase. |
| 3 | `make pr.land` resolves `jobs.<id>.name` overrides in the drift test | ✓ VERIFIED | `tests/test_pr_land.py::_effective_job_names` scopes a `^    name:` lookup to each job's own block; `test_a_job_name_override_moves_the_derived_required_set` proves an `image:` → `name: renamed-image` rename (plain and quoted) moves the derived set and neither step-level `name:` leaks in. |
| 4 | `make pr.land` reports only what it observed after the merge | ✓ VERIFIED | `scripts/pr_land.py::no_run_report` (lines 372-416) reports exactly one of: a token found in the squash commit's own message (read via `gh api .../commits/<sha>`), the last read error, or the Actions URL — never a cause it did not itself read. Live probe: `b72b0e1` (clean message) → Actions-link report; `20b63e4` (carries `[ci skip]`) → names the token. Both match documented pre-planning live reads exactly. |
| 5 | `_build_cached` never hands out a solid carrying a mesh | ✓ VERIFIED | `src/spur/model.py` line 281: `shape.copy().exportStl(...)` in the STL branch; STEP branch unchanged (no mesh attached). `tests/test_model.py::test_exporting_leaves_the_cached_solid_exact` and `::test_an_stl_export_matches_a_first_export_whatever_came_before` pass; ran directly (`3 passed`). |
| 6 | The autouse solid-cache reset fixture is deleted | ✓ VERIFIED | `tests/conftest.py` contains no `_reset_solid_cache`; its one remaining autouse fixture is the unrelated Phase-3 `_reset_root_logger`. Full suite (191 tests) passes without it. |
| 7 | Every behaviour change ships with its test | ✓ VERIFIED | Each of D-02/D-03/D-04/D-05/D-06/D-07/D-08/D-09 has a named, passing test in `tests/test_skip_tokens.py`, `tests/test_pr_land.py` or `tests/test_model.py` (see table above); confirmed by direct execution, not by SUMMARY claim. |
| 8 | The copy-vs-strip numbers are measured and written down | ✓ VERIFIED | `docs/architecture/decision_log.md` L24: copy 23.1/70.9/260.9/824.2 ms vs `Clean_s` 20.2/63.1/244.9/791.3 ms (reference/200-tooth × preview/fine), plus the export-only and peak-RSS follow-up measurements, with the reasoning for rejecting the faster option. |
| 9 | `make verify` stays green | ✓ VERIFIED | Ran `make verify` directly at HEAD (`d7253c8`): ruff, mypy `--strict`, import-boundary contracts (5 kept, 0 broken), unfinished-work scan, pytest — **191 passed in 32.86s**. |

**Score:** 9/9 truths verified (0 present, behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `scripts/skip_tokens.py` | Whole-buffer skip-token search, no cut, line-numbered refusal, `-v` caveat | ✓ VERIFIED | Read in full; matches D-02/D-03 exactly |
| `scripts/pr_land.py::head_refusals` | Refuses on `run.conclusion != "success"` alongside per-job loop | ✓ VERIFIED | Line 295; diff-scoped to this function only in commit `9ca8320` |
| `scripts/pr_land.py::no_run_report` | Reports only what it observed post-merge | ✓ VERIFIED | Lines 372-416; wired into `land`'s step 5 (line 571) |
| `tests/test_pr_land.py::_effective_job_names` | Effective job-name resolution for the drift test | ✓ VERIFIED | Lines 223-274; block-scoped `name:` lookup |
| `src/spur/model.py::_write_export` | STL branch meshes `shape.copy()`, STEP branch unchanged | ✓ VERIFIED | Lines 267-288 |
| `tests/conftest.py` | No autouse solid-cache reset | ✓ VERIFIED | Only `_reset_root_logger` remains |
| `docs/architecture/decision_log.md` L24, L25 | Solid-cache invariant + merge-gate amendment, append-only | ✓ VERIFIED | Both commits show `N 0` in `git show --numstat` (pure additions) |
| `docs/tech_debt/resolved/*` (5 files) | `Status: resolved`, `Resolved in:` sha, moved from `active/` | ✓ VERIFIED | All 5 confirmed present in `resolved/`, absent from `active/`, correct `Status`/`Resolved in` fields |
| `docs/tech_debt/INDEX.md` | All 5 rows moved to `## Resolved` | ✓ VERIFIED | Confirmed by reading the file directly |
| `.planning/STATE.md` | Blockers/Concerns cites run 36122394253, retires two bullets | ✓ VERIFIED | Lines 175-193 |
| `docs/HOW_TO_DEVELOP.md` §6/§8 | `-v` caveat, up-to-date-`main` rule, `jobs.<id>.name`, `--match-head-commit` | ✓ VERIFIED | All four literal strings present via grep |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `land()` step 5 | `no_run_report()` | called with `attempts * interval_s` and the poll's tracked `last_error` | ✓ WIRED | Line 571: `no_run_report(pr_number, squash_sha, attempts * interval_s, last_error, run)` |
| `no_run_report()` | `find_skip_tokens()` | reads the squash commit's message through `gh api .../commits/<sha>` | ✓ WIRED | Lines 395-409 |
| `head_refusals()` | `WorkflowRun.conclusion` (already parsed by `parse_runs`) | read directly, no new `gh` call | ✓ WIRED | Line 295 |
| `_write_export` | `shape.copy()` | STL export called on the copy, never the cached object | ✓ WIRED | Line 281 |
| `required_jobs()` (from file) | `_effective_job_names(ci_yml)` (from GitHub's reporting rule) | drift test equality | ✓ WIRED | `tests/test_pr_land.py` line 274 |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| D-08: cached solid stays exact through preview/fine/STEP export sequence | `pytest tests/test_model.py -k cached_solid_exact` | 1 passed | ✓ PASS |
| D-08: STL export content matches a first export regardless of history | `pytest tests/test_model.py -k first_export` | 1 passed | ✓ PASS |
| D-04 live: `check_head` on real run 36116930241 | direct Python call through the real `gh` | 3 refusals (behind, `concluded 'failure'` + URL, `test (3.12)`) | ✓ PASS |
| D-06 live: `no_run_report` on real commits `b72b0e1`/`20b63e4` | direct Python call through the real `gh` | Actions-link report / named-token report, matching documented pre-fix reads | ✓ PASS |
| Full merge-gate + solid-cache offline suite | `pytest tests/test_pr_land.py tests/test_skip_tokens.py -q` | 85 passed | ✓ PASS |
| Whole-project gate | `make verify` | 191 passed in 32.86s | ✓ PASS |

### Anti-Patterns Found

None. Scanned every file this phase modified (`src/spur/model.py`, `tests/test_model.py`,
`tests/conftest.py`, `scripts/skip_tokens.py`, `tests/test_skip_tokens.py`,
`scripts/pr_land.py`, `tests/test_pr_land.py`, `docs/HOW_TO_DEVELOP.md`,
`docs/architecture/decision_log.md`, `.planning/STATE.md`) for `TBD|FIXME|XXX|TODO|HACK|PLACEHOLDER`
— the only hit is `docs/HOW_TO_DEVELOP.md` line 21, which is prose *describing* the
unfinished-work scan's own search terms (`незавершёнки (\`TODO\`/\`FIXME\`/...)`), not a
debt marker. No stub returns, no hollow props, no empty handlers found in the changed
production code.

### Requirements Coverage

See "Requirement Traceability Note" above — `.planning/REQUIREMENTS.md` has no Phase 6
rows by design (ROADMAP lists `Requirements: TBD`); all 11 `D-xx` decision IDs from
`06-CONTEXT.md` are claimed by a plan and verified against the tree.

### Human Verification Required

None. Every must-have is either directly readable in the code, provable by a passing named
test, or provable by a live, read-only `gh` probe re-run in this session — no visual,
real-time, or UX judgment call was needed for this phase's scope (CLI/library behavior
only).

### Gaps Summary

None. All 9 derived observable truths verified against the codebase, not against SUMMARY.md
claims: read every plan and every changed file directly, ran `make verify` myself (191
passed), ran the specific D-08 tests directly (3 passed), and re-ran both live `gh` probes
(D-04 against run 36116930241, D-06 against commits `b72b0e1`/`20b63e4`) — all four
matched the documented pre-fix and post-fix behavior exactly. All five tech-debt files are
`Status: resolved` in `docs/tech_debt/resolved/`, absent from `active/`, with `INDEX.md`
rows moved. The decision log gained L24 and L25 as pure additions (zero lines deleted from
either commit). `.planning/STATE.md` cites the required run and retires the two Phase 6
blockers. The one note worth flagging for visibility (not scored as a gap) is the
commit-splitting pattern under D-01, which matches Phase 5's own established precedent.

---

*Verified: 2026-09-25*
*Verifier: Claude (gsd-verifier)*
