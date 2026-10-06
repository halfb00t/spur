---
phase: 17-debt-first-commit-gate-and-pool-race
verified: 2026-10-06T10:23:50Z
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
covered_digest: "v3:sha256:c4e9124904d0695d88ca22b702a989424ef7ea4c9ccb1907a8e7abe776db5567"
behavior_unverified: 0
overrides_applied: 0
re_verification: false
---

# Phase 17: Debt First — Commit Gate and Pool Race Verification Report

**Phase Goal:** The two `must` debt items are closed by a decision and a measurement, not by a workaround — an SDK commit completes on this repository, a second same-slot timeout ends as the documented `503 timeout` instead of an undocumented `500`, and the worst composed row's margin under contention has a logged answer — so every later commit of the milestone runs under a settled hook.
**Verified:** 2026-10-06T10:23:50Z
**Status:** passed (5 warnings carried from review, none blocking; one wording defect to fix before ship, see WR-01)
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (ROADMAP success criteria are the contract)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | One live `gsd_run query commit` with hooks installed returns `committed: true`, commit in `git log`, inside 30 s, nobody committing by hand; any subset is a Makefile target `verify` depends on | VERIFIED | `17-02-sdk-commit.json` = `{committed: true, hash: 5a3332f}`; `git log` holds `5a3332f docs(17-02)...`. `.git/hooks` has `commit-msg`, `pre-commit`, `pre-push`. SUMMARY records 13.57 s real. I re-ran `make verify.fast` here: 622 passed, 11.56 s wall (under the 30 s kill). `make -n verify` prints the four static recipes then exactly one pytest line; `make -n verify.fast` prints the same four static recipes then a narrower pytest line (`verify.static` shared prefix, `test.fast` = the gate's own recipe with `--ignore` x4, `--no-cov`). Option (a) alone was not chosen. I could not re-run the SDK commit itself (it would create a commit); the JSON + git object + hook files + the measured 11.56 s are the evidence. |
| 2 | One `Lxx` amends L13/L34; every site says the new truth; pre-push semantics verified in scratch repo and recorded; commit-timeout debt retires with sha in the fixing commit | VERIFIED | `decision_log.md` L36 (line 1869) "amends L13 and L34" by appending, with a 9-row pre-push scratch table (once per push, first ref, stash of unstaged, tag-only/delete/`--no-verify`/`SKIP`, per-clone install). Sites changed in `c06749d`: `.pre-commit-config.yaml` header, `docs/HOW_TO_DEVELOP.md`, `README.md`, `docs/architecture/packaging.md`, `ci.yml` comment, `scripts/pr_land.py` ("~42 s" gone: `git grep -n "~42"` outside `.planning` prints nothing). Debt file is in `resolved/` with `Status: resolved`, `Resolved in: c06749d`, INDEX row moved; `c06749d` exists. `tests/test_hooks.py` (new) passes and pins hook/target drift and the main-checkout-only stamp. |
| 3 | `bench/RESULTS.md` has the per-request table of the ten-identical-worst-row scenario, fresh server, shipping defaults, before the fix, undocumented `500` visible; scenario in `_SCENARIOS`, not default set | VERIFIED | `bench/RESULTS.md` "## Same-slot timeout race (Phase 17)" / "### Attempt 1 (before the fix)": 10-row client table with parameters, outcome, wall time; 1x `503 timeout`, 3x `500`, 6x `503 busy`; host state and load (5.48 -> 5.88) recorded; commit under test `814f4f3` (pre-fix). Independent cross-check of the raw log `investigation/attempt-1.server.log`: 6 `AttributeError` mentions, 4 `build.failed` (3 AttributeError + 1 BuildTimeout; each AttributeError appears in the record and its traceback). `bench/latency.py` diff: `identical` added to `_SCENARIOS`, `DEFAULT_SCENARIOS` untouched; `_fetch(..., record_500=False)` default keeps raising; `tests/test_bench.py` registry assertion updated to the four names and a new test pins the 500-raising default. |
| 4 | After the fix a second same-slot timeout returns the documented `503`; scenario re-run shows zero 500s; stale-executor test red before / green after; same-tick test accepts `BuildTimeout`/`BrokenProcessPool`; 0.5 s-gap test unchanged; tests ran repeatedly under `-n 8 --cov` and `-n 4` | VERIFIED | `src/spur/pool.py`: guard is `if self.executor_for(p) is executor and executor._processes is not None:` around terminate + `recreate_for`, `raise BuildTimeout` unconditional after it, no `await` in the handler (ast test pins it). `BuildPool._closed = False` set in `__init__`, `shutdown()` sets it first, `recreate_for` returns early on `self._closed or ...`. Exactly the locked two-fact shape; nothing else in `pool.py` moved. **Red-before check I ran myself:** copied the tree to the scratchpad, swapped in `git show 4bd384c:src/spur/pool.py`, ran `-k "stale_executor or closed_pool or same_tick or never_awaits"`: `test_a_stale_executor_timeout_is_a_build_timeout_not_an_attribute_error` FAILED with `AttributeError: 'NoneType' object has no attribute 'values'` at `pool.py:204`. **Green-after:** `pytest tests/test_pool.py tests/test_hooks.py tests/test_bench.py`: 49 passed. Same-tick test asserts `isinstance(sibling, (BuildTimeout, BrokenProcessPool))`. `git diff 4bd384c..HEAD -- tests/test_pool.py` has additions only, no deleted or changed line, so the 0.5 s-gap test is unchanged. `investigation/17-04-stability.md`: 20/20 at `-n 8 --cov`, 20/20 at `-n 4 --cov`, `make verify` 2/3 (run 2 = resource-tracker flake, full log kept, human answered proceed-as-known-flake). Bench after the fix: `after-1.server.log` has 0 `AttributeError`, 0 `Traceback`, 4 `build.failed` (all BuildTimeout), `workers_replaced 0 -> 1`; client table 4x `503 timeout`, 6x `503 busy`, zero 500; decisive (the double timeout did happen). |
| 5 | Worst row's margin has a logged decision in an `Lxx` naming the measured number; `bench/RESULTS.md` and resolved tip-chamfer debt "~1.02x" headline carry a dated note; race debt retires in the commit closing both findings (`Status: resolved`, sha, `git mv`, INDEX row) | VERIFIED | L37 (line 1995) "amends L31 and L32": the decision is documented behaviour, `SPUR_BUILD_TIMEOUT` stays 30 s, `spoke_count` `le` stays 32, no default moved (L05), no figure tuned (L08); it names the readings that set it with section, unit and load (29.42 s alone / 0.58 s margin; 29.41 vs 30.11 s at 32/33 spokes; SC3 `duration_ms` 30004; `identical` 30003 at two loads) and says plainly that none is converted to a ratio and that a timeout reading is the deadline firing. `7af75af` touches `bench/RESULTS.md` (+8), the resolved tip-chamfer debt (+6), `README.md`, `app.py` comment, INDEX, L37. Race debt is in `resolved/` with `Status: resolved`, `Resolved in: 0628182 (the race); 7af75af (the margin)`; INDEX row moved; no file with that name remains in `active/`. |

**Score:** 5/5 truths verified (0 present, behavior-unverified; behavior-dependent truth 4 has a passing named test that I saw red on the old code)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `Makefile` (`verify.static`, `verify`, `verify.fast`, `test.fast`, `$(HOOKS)`) | one shared prefix, no second list | VERIFIED | `make -n` output read for both targets; stamp installs only from the main checkout |
| `.pre-commit-config.yaml` | verify-fast at pre-commit, verify at pre-push, each pinned to one stage | VERIFIED | read in full; `default_install_hook_types: [pre-commit, commit-msg, pre-push]` |
| `tests/test_hooks.py` | drift pin | VERIFIED | passes; not exact on the `--ignore` set (see WR-02) |
| `src/spur/pool.py` | two-fact guard + `_closed` | VERIFIED | read in full, matches REQ wording |
| `tests/test_pool.py` | stale-executor, same-tick, closed-pool, ast tests | VERIFIED | red on pre-fix `pool.py` (stale-executor), green now |
| `bench/latency.py`, `tests/test_bench.py` | `identical` scenario, `record_500` | VERIFIED | diff read; default set unchanged |
| `bench/RESULTS.md` | before and after tables | VERIFIED | both tables present; raw logs agree with them |
| `docs/architecture/decision_log.md` L36, L37 | decisions | VERIFIED | read in full |
| `docs/tech_debt/resolved/*` x2 + INDEX | retirements | VERIFIED | statuses, shas, INDEX rows confirmed |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `verify` | `verify.static` | Makefile prerequisite | WIRED | `make -n verify` / `verify.fast` share the first four recipes |
| `.pre-commit-config.yaml` verify-fast | `make verify.fast` | hook entry | WIRED | hook files present in `.git/hooks`; SDK commit passed through it |
| `_run_with_timeout` timeout branch | `recreate_for` / `_closed` | guard then call | WIRED | read |
| `shutdown()` | `recreate_for` | `_closed` flag | WIRED | `test_a_closed_pool_never_builds_a_replacement_worker` passes |
| `scenario_identical` | `run_composed(record_500=True)` -> `_fetch` | registry | WIRED | diff read |

### Data-Flow Trace (Level 4)

Not applicable: no rendered dynamic data in this phase (build tooling, pool control flow, docs).

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Commit slice fits the SDK window | `make verify.fast` | 622 passed, 11.56 s wall | PASS |
| Stale-executor race on old code | pre-fix `pool.py` in scratch copy, `-k stale_executor...` | FAILED, `AttributeError` at `pool.py:204` | PASS (red as claimed) |
| Pool, hooks, bench tests on current code | `pytest tests/test_pool.py tests/test_hooks.py tests/test_bench.py` | 49 passed | PASS |
| Whole gate | `make verify` | 943 passed in 64.11 s, coverage 97.03 % (floor 96), ruff/mypy/lint-imports/no-fake-done clean | PASS |

The live bench was not re-run (per the brief); its committed logs and `RESULTS.md` tables were cross-read instead.

### Probe Execution

SKIPPED: no `scripts/*/tests/probe-*.sh` and none declared in the plans.

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| REQ-hook-and-commit-timeout-decided | 17-01, 17-02 | L36, subset target, sites corrected, live SDK commit, debt retired | SATISFIED | Truths 1 and 2 |
| REQ-same-slot-timeout-race-reproduced | 17-03 | scenario in `_SCENARIOS`, `record_500`, table with the 500 | SATISFIED | Truth 3 |
| REQ-same-slot-timeout-race-fixed | 17-04, 17-05 | two-fact guard, `_closed`, red/green tests, 20+20 loops, zero 500s on re-run | SATISFIED | Truth 4 |
| REQ-worst-row-margin-decided | 17-05 | L37, dated notes, debt retired on the closing commit | SATISFIED | Truth 5 |

All four IDs from the phase brief appear in a PLAN's `requirements`, in `REQUIREMENTS.md` (checked `[x]`, traceability "Complete") and in ROADMAP. No ORPHANED requirement: REQUIREMENTS.md maps exactly these four to Phase 17.

### Anti-Patterns Found

Debt-marker scan (`TBD|FIXME|XXX`, plus `make verify`'s own unfinished-work scan, which passed) found nothing in the files this phase changed. The review's 12 findings (0 critical, 5 warning, 7 info) are all `open` in `17-REVIEW-DISPOSITION.md`; none contradicts a must-have. Weighed here:

| Finding | Severity | Impact on the goal |
|---------|----------|--------------------|
| WR-01 `README.md:97`, L37, resolved race debt say "raise the variable on a bigger host" | WARNING (wording defect, not a failed truth) | The goal asks for a logged answer that names the number that set it. L37 does that with the readings, loads and rejected alternatives; nothing in the decision depends on the clause. But I agree with the review that it is backwards: the timeout needs raising on a slower or busier host (`app.py`'s own comment says margin for slower hardware), so as written it points an operator at the opposite remedy, and it is the only operator-facing sentence about this limit. Fix the three sites in one commit before ship: "on a slower or busier host, raise the variable". |
| WR-02 `test_hooks.py` does not pin the exact `--ignore` set | WARNING | The commit slice could shrink silently; the sub-30 s property still holds. Hardening, not a goal gap. |
| WR-03 failing `pre-commit install` fails every gate run | WARNING | Design tradeoff recorded in the Makefile comment ("no `|| true`"); not a goal gap. |
| WR-04 `HOW_TO_DEVELOP.md` "the push cannot be red" vs L36's own stated limit (`--no-verify`, other checkouts) | WARNING | Overstates a guarantee; L36 is accurate. Wording fix. |
| WR-05 resource-tracker debt record contradicts itself; its revisit trigger fired in this phase's new test | WARNING | The flake is a known, filed `nice` debt; the human accepted the one red run at the 17-04 checkpoint. Tidy the record. |
| IN-01..IN-07 | INFO | Comment and test-anchor nits; IN-07 (after `shutdown()` a timed-out request raises `BuildTimeout` without terminating its wedged worker) is a corner of the closed-pool path the REQ explicitly scopes to "never build a replacement". |

### Human Verification Required

None required for this phase's goal. Two items are carried forward by the phase's own record and are not unverified truths of Phase 17:

- L36 assumptions A1/A3 (a Linux CI runner installs the hooks and fires none): verified on a macOS shallow clone only; the plan schedules the first CI run to be read at ship.
- WR-01's wording fix, above.

### Gaps Summary

No gaps. Every must-have resolves to VERIFIED against the code, not the SUMMARYs: the fix in `pool.py` matches the locked shape; the stale-executor test is red on the pre-fix `pool.py` (I reproduced the `AttributeError` myself) and green on the fix; the committed server logs agree with the before/after tables (3 `AttributeError` build failures before, 0 after, 4 `BuildTimeout`); the whole gate passes on this tree; the SDK commit is evidenced by its JSON, its git object, the installed hooks and an 11.56 s measured commit stage. Residual risk is limited to the warnings above, none of which blocks the next phase. L08/L05 hold: no number moved, and L37 records readings with their loads instead of a ratio.

---

_Verified: 2026-10-06T10:23:50Z_
_Verifier: Claude (gsd-verifier)_
