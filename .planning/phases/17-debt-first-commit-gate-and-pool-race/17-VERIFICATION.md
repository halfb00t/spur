---
phase: 17-debt-first-commit-gate-and-pool-race
verified: 2026-10-06T11:55:31Z
status: passed
score: 5/5 must-haves verified
covered_files:
  - .planning/phases/17-debt-first-commit-gate-and-pool-race/17-01-PLAN.md
  - .planning/phases/17-debt-first-commit-gate-and-pool-race/17-01-SUMMARY.md
  - .planning/phases/17-debt-first-commit-gate-and-pool-race/17-02-PLAN.md
  - .planning/phases/17-debt-first-commit-gate-and-pool-race/17-02-SUMMARY.md
  - .planning/phases/17-debt-first-commit-gate-and-pool-race/17-03-PLAN.md
  - .planning/phases/17-debt-first-commit-gate-and-pool-race/17-03-SUMMARY.md
  - .planning/phases/17-debt-first-commit-gate-and-pool-race/17-04-PLAN.md
  - .planning/phases/17-debt-first-commit-gate-and-pool-race/17-04-SUMMARY.md
  - .planning/phases/17-debt-first-commit-gate-and-pool-race/17-05-PLAN.md
  - .planning/phases/17-debt-first-commit-gate-and-pool-race/17-05-SUMMARY.md
  - .pre-commit-config.yaml
  - Makefile
  - bench/latency.py
  - src/spur/app.py
  - src/spur/pool.py
  - tests/test_bench.py
  - tests/test_hooks.py
  - tests/test_pool.py
covered_digest: "v3:sha256:bb25cebf930fc0b55abda7faa62c383bb0f7aa1a293832f1a0f853b364e7497a"
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: passed
  previous_score: 5/5
  gaps_closed: []
  gaps_remaining: []
  regressions: []
---

# Phase 17: Debt First — Commit Gate and Pool Race Verification Report

**Phase Goal:** The two `must` debt items are closed by a decision and a measurement, not by a workaround — an SDK commit completes on this repository, a second same-slot timeout ends as the documented `503 timeout` instead of an undocumented `500`, and the worst composed row's margin under contention has a logged answer — so every later commit of the milestone runs under a settled hook.
**Verified:** 2026-10-06T11:55:31Z
**Status:** passed
**Re-verification:** Yes — the previous report (`0380345`, passed 5/5) went stale because 16 code-review fix commits (`9927f3c` … `90307d4`) changed covered source. No gap was open; this pass re-checks the truths against the post-review tree and refreshes the covered-input fingerprint.

## What changed since the previous report, and whether it moved a truth

`git diff 0380345..HEAD` outside `.planning/`: 15 files, +154/-49.

| Change | Files | Effect on a truth |
|--------|-------|-------------------|
| `core.hooksPath` skip branch in `$(HOOKS)` (WR-03), stamp touched only on a real install or the worktree branch | `Makefile`, `tests/test_hooks.py` | Truth 1. `git config --get core.hooksPath` is empty in this repo, so the skip branch is dormant here and the three hooks are still in `.git/hooks` (`commit-msg`, `pre-commit`, `pre-push`). The new test (`test_the_hook_stamp_skips_loudly_when_core_hooks_path_is_set`) runs the recipe with a shim `pre-commit` and asserts no install and no stamp. It passes. |
| Exact `--ignore` set pinned (WR-02) | `tests/test_hooks.py` | Truth 1 hardened: the commit slice cannot shrink silently. |
| Makefile comment: "four by share" ranking corrected, 620-count flagged as a snapshot (IN-06) | `Makefile` | Comment only. |
| `bench/latency.py` drops the `2.00x` pass bar under `composed`/`identical`; pool size and `attempted` come from `len(rows)` (IN-02, IN-03) | `bench/latency.py`, `tests/test_bench.py` | Truth 3. `identical` is still in `_SCENARIOS` and out of `DEFAULT_SCENARIOS`; for the 10-row scenarios `len(rows)` is 10, the value it replaced, so the recorded tables are not invalidated. Both new assertions pass. |
| Await-tripwire widened to `async with` / `async for` / async comprehension, seeded from the AST (IN-01, IN-04) | `tests/test_pool.py` | Truth 4. Tests only: the `0.5 s`-gap test and the stale-executor test are untouched (diff is confined to the `_timeout_handler` / `_suspensions_in_timeout_handler` helpers and the tripwire test). |
| "bigger host" -> "slower or busier host" (WR-01 earlier review) | `README.md`, `decision_log.md` L37, resolved race debt | Truth 5. `grep -rn -i "bigger host" README.md docs src bench Makefile` prints nothing. The L37 decision (30 s stays, `le` 32 stays) is unchanged; only the remedy's direction is corrected. |
| Comment-only edits in `app.py` (citations to the two RESULTS.md sections) and `pool.py` (closed-pool path measured at 8.10 s exit) | `src/spur/app.py`, `src/spur/pool.py` | None: see the locked-shape check below. |
| Docs/debt records (WR-04, WR-05, IN-05, ci.yml comment, HOW_TO_DEVELOP, INDEX, STATE/PROJECT) | docs only | Wording; no must-have depends on the changed clauses. |

## Locked fix shape in `src/spur/pool.py`: unchanged

- `git diff 0380345..HEAD -- src/spur/pool.py` is a single hunk, comment lines only (the `+` lines are all `#` text).
- I parsed `pool.py` at the fix commit `0628182` and at HEAD with `ast.parse` and compared `ast.dump` byte for byte: **identical** (14 863 bytes each). The pre-fix blob `4bd384c` differs (14 135 bytes), so the comparison discriminates.
- Read in place: `_closed = False` in `__init__` (line 94); `recreate_for` returns early on `self._closed or self._executors[i] is not executor` (line 131); `shutdown()` sets `_closed = True` first (line 256); the timeout handler guards terminate + `recreate_for` with `if self.executor_for(p) is executor and executor._processes is not None:` and `raise BuildTimeout(...) from None` sits outside the guard; no `await` in the handler. That is the two-fact guard plus `_closed`, as locked.

## Goal Achievement

### Observable Truths (ROADMAP success criteria are the contract)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | One live `gsd_run query commit` with hooks installed returns `committed: true`, commit in `git log`, inside 30 s, nobody committing by hand; any subset is a Makefile target `verify` depends on | VERIFIED | `17-02-sdk-commit.json` = `{committed: true, hash: 5a3332f, reason: committed}`; `git log` holds `5a3332f docs(17-02): record the hook commit's sha...`. `.git/hooks` has `commit-msg`, `pre-commit`, `pre-push`. `core.hooksPath` unset here. `make verify.static` is the shared prefix, `verify` and `verify.fast` both depend on it, `test.fast` is the gate's recipe with the four `--ignore` flags and `--no-cov`, now pinned as an exact set by `tests/test_hooks.py`. The 30 s figure itself was measured by the previous pass (`make verify.fast`: 11.56 s wall) and by the plan's own record (13.57 s for the SDK commit); I did not re-time it this pass and I cannot re-run the SDK commit without creating one. The post-review Makefile change is confined to the `$(HOOKS)` recipe and comments; the recipe the commit stage runs is untouched. |
| 2 | One `Lxx` amends L13/L34; every site says the new truth; pre-push semantics verified in scratch repo and recorded; commit-timeout debt retires with sha in the fixing commit | VERIFIED | `decision_log.md` line 1869: L36 "(amends L13 and L34)". `c06749d` resolves (`git log -1`). Debt file `2026-09-25-gsd-commit-timeout-kills-cold-verify-hook.md` is in `docs/tech_debt/resolved/`; none of that name in `active/`. Review fixes made the sites more accurate (HOW_TO_DEVELOP no longer says the push cannot be red; ci.yml says "none is expected to fire in CI (L36 A1, open until the phase's first CI run is read)"), consistent with L36. |
| 3 | `bench/RESULTS.md` has the per-request table of the ten-identical-worst-row scenario, fresh server, shipping defaults, before the fix, undocumented `500` visible; scenario in `_SCENARIOS`, not default set | VERIFIED | `bench/RESULTS.md` line 2835 "## Same-slot timeout race (Phase 17)", line 2865 "### Attempt 1 (before the fix)", line 2938 verdict. Raw log `investigation/attempt-1.server.log` still holds 6 `AttributeError` mentions. `bench/latency.py` post-review diff is the `len(rows)` sizing and the pass-bar line only. `tests/test_bench.py` passes (in the gate run below). |
| 4 | After the fix a second same-slot timeout returns the documented `503`; scenario re-run shows zero 500s; stale-executor test red before / green after; same-tick test accepts `BuildTimeout`/`BrokenProcessPool`; 0.5 s-gap test unchanged; tests ran repeatedly under `-n 8 --cov` and `-n 4` | VERIFIED | Code: locked shape unchanged (AST-identical to `0628182`, above). "After the fix" table at `RESULTS.md` line 2949: 4x `503 timeout`, 6x `503 busy`, zero 500, `workers_replaced 0 -> 1`; `investigation/after-1.server.log` has 0 `AttributeError`, 0 `Traceback`, 4 `build.failed`. Red-before was reproduced in the previous pass (pre-fix `pool.py` in a scratch copy: stale-executor test FAILED with `AttributeError ... 'NoneType' ... .values` at `pool.py:204`); the code under test is AST-identical since, so that result stands. The only test-file change since is the tripwire widening, which now seeds four suspension forms and requires the helper to report each, so the check can fail. `investigation/17-04-stability.md`: 20/20 at `-n 8 --cov`, 20/20 at `-n 4`; those runs were against the `pool.py` blob `2e2a9b6`, which differs from HEAD only in comments. |
| 5 | Worst row's margin has a logged decision in an `Lxx` naming the measured number; `bench/RESULTS.md` and resolved tip-chamfer debt "~1.02x" headline carry a dated note; race debt retires in the commit closing both findings (`Status: resolved`, sha, `git mv`, INDEX row) | VERIFIED | L37 at line 1995 "(amends L31 and L32)": documented behaviour, `SPUR_BUILD_TIMEOUT` 30 s, `spoke_count` `le` 32, no default moved (L05), no figure tuned (L08), readings recorded with section and load and not converted to a ratio. The one post-review edit to L37 corrects the remedy to "a slower or busier host raises the variable"; it does not move the decision or any number. Race debt: `Status: resolved`, `Resolved in: 0628182 (the race); 7af75af (the margin)`, in `resolved/`, absent from `active/`; both shas exist. |

**Score:** 5/5 truths verified (0 present, behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `Makefile` (`verify.static`, `verify`, `verify.fast`, `test.fast`, `$(HOOKS)`) | one shared prefix, no second list; install skips loudly under `core.hooksPath` | VERIFIED | `make verify` ran the whole gate green; hook recipe read and covered by `test_hooks.py` (three branches: main checkout, linked worktree, hooksPath) |
| `.pre-commit-config.yaml` | verify-fast at pre-commit, verify at pre-push | VERIFIED | unchanged since previous pass |
| `tests/test_hooks.py` | drift pin incl. exact `--ignore` set and hooksPath skip | VERIFIED | passes; WR-02 closed |
| `src/spur/pool.py` | two-fact guard + `_closed` | VERIFIED | AST-identical to `0628182` |
| `tests/test_pool.py` | stale-executor, same-tick, closed-pool, await-tripwire (4 forms) | VERIFIED | pass in the gate; `pool.py` at 100 % statements and branches |
| `bench/latency.py`, `tests/test_bench.py` | `identical` scenario, `record_500`, no pass bar under composed/identical | VERIFIED | pass in the gate |
| `bench/RESULTS.md` | before and after tables | VERIFIED | both present; raw logs under `investigation/` agree |
| `docs/architecture/decision_log.md` L36, L37 | decisions | VERIFIED | headings at lines 1869 and 1995 |
| `docs/tech_debt/resolved/*` x2 + INDEX | retirements | VERIFIED | in `resolved/`, `Status: resolved`, shas resolve |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `verify` / `verify.fast` | `verify.static` | Makefile prerequisite | WIRED | unchanged by review fixes |
| `.pre-commit-config.yaml` verify-fast | `make verify.fast` | hook entry | WIRED | hook files present; SDK commit `5a3332f` went through it |
| `_run_with_timeout` timeout branch | `recreate_for` / `_closed` | guard then call | WIRED | read; AST-identical to the fix commit |
| `shutdown()` | `recreate_for` | `_closed` flag | WIRED | `test_a_closed_pool_never_builds_a_replacement_worker` in the gate |
| `scenario_identical` | `run_composed(record_500=True)` -> `_fetch` | registry | WIRED | review diff touches only sizing and the report line |

### Data-Flow Trace (Level 4)

Not applicable: no rendered dynamic data in this phase (build tooling, pool control flow, docs).

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Whole gate on the post-review tree | `make verify` | exit 0; ruff "All checks passed!", mypy "no issues found in 39 source files", `lint-imports` "Contracts: 5 kept, 0 broken", pytest `-n 8 --cov`: **944 passed in 75.67s (0:01:15)**, coverage 97.25 % (floor 96), `src/spur/pool.py` 100 % | PASS |
| Locked fix unchanged | `ast.dump` of `pool.py` at `0628182` vs HEAD | byte-identical | PASS |
| "bigger host" remedy gone | `grep -rn -i "bigger host" README.md docs src bench Makefile` | no output | PASS |
| After-fix server log has no 500 | `grep -c AttributeError` / `Traceback` in `after-1.server.log` | 0 / 0 (before: 6 AttributeError) | PASS |

The live bench was not re-run, per the brief; its committed logs and `RESULTS.md` tables were cross-read instead. Previous pass counted 943 tests; the one added since is the `core.hooksPath` test.

### Probe Execution

SKIPPED: no `scripts/*/tests/probe-*.sh` and none declared in the plans.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| REQ-hook-and-commit-timeout-decided | 17-01, 17-02 | L36, subset target, sites corrected, live SDK commit, debt retired | SATISFIED | Truths 1 and 2; `[x]` and "Complete" in REQUIREMENTS.md lines 47 and 252 |
| REQ-same-slot-timeout-race-reproduced | 17-03 | scenario in `_SCENARIOS`, `record_500`, table with the 500 | SATISFIED | Truth 3; REQUIREMENTS.md lines 66 and 253 |
| REQ-same-slot-timeout-race-fixed | 17-04, 17-05 | two-fact guard, `_closed`, red/green tests, repeat runs, zero 500s on re-run | SATISFIED | Truth 4; REQUIREMENTS.md lines 73 and 254 |
| REQ-worst-row-margin-decided | 17-05 | L37, dated notes, debt retired on the closing commit | SATISFIED | Truth 5; REQUIREMENTS.md lines 87 and 255 |

All four IDs from the phase brief are checked `[x]` in REQUIREMENTS.md with traceability "Phase 17 / Complete". No ORPHANED requirement: REQUIREMENTS.md maps exactly these four to Phase 17.

### Anti-Patterns Found

`make verify`'s unfinished-work scan passed on this tree. The code review's 12 + 4 findings (no critical) are all `fixed` in `17-REVIEW-DISPOSITION.md` (`open: 0`, `total: 12`). The earlier report's five warnings are therefore closed, not carried:

| Earlier warning | Now |
|-----------------|-----|
| WR-01 "raise the variable on a bigger host" (README, L37, resolved race debt) | Fixed (`9927f3c`); grep finds no occurrence |
| WR-02 `--ignore` set not pinned | Fixed (`b863105`); exact-set assertion present and passing |
| WR-03 failing `pre-commit install` fails every gate run | Fixed (`bc1318f`); loud skip under `core.hooksPath`, tested |
| WR-04 "the push cannot be red" | Fixed (`15a3f51`); HOW_TO_DEVELOP now names `--no-verify`, `SKIP=`, other refs |
| WR-05 resource-tracker debt record | Fixed (`daa954a`, `dc7e72b`); INDEX trigger updated |

### Human Verification Required

None for this phase's goal. Carried by the phase's own record, not unverified truths of Phase 17:

- L36 assumptions A1/A3 (a Linux CI runner installs the hooks and fires none): verified on a macOS shallow clone only; ci.yml now states this as open until the first CI run is read at ship.
- Whether uvicorn's graceful shutdown can reach the closed-pool timeout path is recorded as unmeasured in the `pool.py` comment (PITFALLS 9, A4). It is a corner the REQ scopes to "never build a replacement" and does not affect the goal.

### Gaps Summary

No gaps. All five truths hold against the post-review tree. The fix in `pool.py` is byte-identical at AST level to the fix commit; the review's 16 commits changed comments, docs, test hardening, a Makefile install guard and bench reporting only; the whole gate is green (944 passed, 97.25 % coverage). L08 and L05 hold: no number moved, no default moved, and L37 records readings with their loads instead of a ratio.

---

_Verified: 2026-10-06T11:55:31Z_
_Verifier: Claude (gsd-verifier)_
