---
phase: 17-debt-first-commit-gate-and-pool-race
plan: 04
subsystem: pool
tags: [build-pool, timeout-race, process-pool, asyncio, pytest-xdist]

requires:
  - phase: 17-debt-first-commit-gate-and-pool-race
    provides: "17-03: the 500 reproduced in attempt 1 with the server's own AttributeError records, verdict line 'Reproduced in attempt 1.'"
  - phase: 13-latency-bar
    provides: "SC3's two undocumented 500s (requests 912cd2d4, 0fc30d53) that this fix answers"
provides:
  - "src/spur/pool.py: the two-fact guard in _run_with_timeout's except TimeoutError branch, BuildPool._closed, recreate_for's _closed return, shutdown() setting _closed first"
  - "tests/test_pool.py: the stale-executor, same-tick, closed-pool and ast-tripwire tests plus _awaits_in_timeout_handler"
  - "investigation/17-04-stability.md: 43 rows (20 at -n 8 --cov, 20 at -n 4 --cov, 3 make verify), the tally, the blob ids of the code the runs ran"
  - "the fix commit 0628182, which 17-05's L37 and the race debt cite"
affects: [17-05]

actuals:
  tokens: 4585
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "a stale-executor test drives the race in process: one asyncio.sleep(0) lets the request reach wait_for, then the test plays the sibling and calls recreate_for itself, so no timing orders anything"
    - "a no-await rule that no behavioural test can see is pinned by an ast test with a seeded tripwire proving the check can see an await"

key-files:
  created:
    - .planning/phases/17-debt-first-commit-gate-and-pool-race/investigation/17-04-stability.md
    - .planning/phases/17-debt-first-commit-gate-and-pool-race/investigation/17-04-verify-2.log
    - .planning/phases/17-debt-first-commit-gate-and-pool-race/investigation/17-04-resource-tracker.log
  modified:
    - src/spur/pool.py
    - tests/test_pool.py
    - docs/tech_debt/active/2026-10-06-resource-tracker-flake-fails-the-gate.md

key-decisions:
  - "Proceeded as-is with make verify at 2/3: the human answered proceed-as-known-flake at the checkpoint raised on run 2 (the resource-tracker flake, not a new-test assertion)"
  - "The fix is exactly the locked shape; nothing else in pool.py changed"

patterns-established:
  - "Every non-green stability run keeps its whole log committed beside the table, under the name the table's log column gives"

requirements-completed: [REQ-same-slot-timeout-race-fixed]

plan_head_before: 17352fdb4e5c3051de9acab05b66fa6ce2f3d760
plan_head_after: c6f49487316b5f2efcdfcd9f24715c74dc35bb3a

coverage:
  - id: D1
    description: "A second same-slot timeout of one incident raises BuildTimeout (the documented 503 timeout), never AttributeError"
    requirement: REQ-same-slot-timeout-race-fixed
    verification:
      - kind: unit
        ref: "tests/test_pool.py#test_a_stale_executor_timeout_is_a_build_timeout_not_an_attribute_error"
        status: pass
    human_judgment: false
  - id: D2
    description: "Three same-tick same-slot timeouts each end in BuildTimeout or BrokenProcessPool, the worker is replaced once, reaped with -SIGTERM, and a fresh worker serves"
    requirement: REQ-same-slot-timeout-race-fixed
    verification:
      - kind: unit
        ref: "tests/test_pool.py#test_three_same_tick_same_slot_timeouts_each_end_in_a_documented_refusal"
        status: pass
    human_judgment: false
  - id: D3
    description: "A closed pool never builds a replacement worker (PITFALLS 9's second route)"
    requirement: REQ-same-slot-timeout-race-fixed
    verification:
      - kind: unit
        ref: "tests/test_pool.py#test_a_closed_pool_never_builds_a_replacement_worker"
        status: pass
    human_judgment: false
  - id: D4
    description: "The timeout branch never awaits and no handler hides a third defect; a seeded await is caught"
    requirement: REQ-same-slot-timeout-race-fixed
    verification:
      - kind: unit
        ref: "tests/test_pool.py#test_the_timeout_branch_never_awaits_before_it_raises"
        status: pass
    human_judgment: false
  - id: D5
    description: "The fix is stable: the new tests and tests/test_api.py held over 20 runs at -n 8 --cov and 20 at -n 4 --cov, and 2 of 3 full make verify runs, the third lost to a known flake"
    requirement: REQ-same-slot-timeout-race-fixed
    verification:
      - kind: other
        ref: ".planning/phases/17-debt-first-commit-gate-and-pool-race/investigation/17-04-stability.md (Tally: -n 8 --cov 20/20 green; -n 4 --cov 20/20 green; make verify 2/3 green.)"
        status: pass
    human_judgment: true
    rationale: "make verify read 2/3: run 2 failed on the resource-tracker flake, and whether to accept a 2/3 gate record was the human's call (proceed-as-known-flake)"
  - id: D6
    description: "The production-shaped confirmation that the 500 is gone (the after-fix bench run)"
    requirement: REQ-same-slot-timeout-race-fixed
    verification: []
    human_judgment: true
    rationale: "Not this plan's: 17-05 runs the after-fix bench and retires the race debt"

duration: about 31 min since 17-03 closed (15:21 to 15:52 +06), including the human's checkpoint wait; the previous executor's start time was not passed to this continuation
completed: 2026-10-06
status: complete
---

# Phase 17 Plan 04: Same-slot timeout race fix Summary

**A second same-slot timeout now raises BuildTimeout (the documented 503) instead of an AttributeError: a two-fact guard (this request's executor is still the slot's, and its _processes is not None) plus a `_closed` flag, with a red-then-green stale-executor test, an ast tripwire for the no-await rule, and 43 recorded stability runs.**

## Performance

- **Duration:** about 31 min since 17-03 closed, including the checkpoint wait (see frontmatter)
- **Completed:** 2026-10-06
- **Tasks:** 3 (Task 2 not reached, Task 3 resumed after the executor-raised checkpoint)
- **Files modified:** 5 (pool.py, test_pool.py, the stability record, the resource-tracker debt item and its log), plus one duplicate log

## D-17 checkpoint

D-17 checkpoint not reached -- reproduced in attempt 1

`bench/RESULTS.md`'s first line under `### Before the fix: verdict` is exactly `Reproduced in attempt 1.`, and 17-03-SUMMARY.md repeats it, so the plan's Task 2 decision was not presented. The fix was written against a 500 someone saw (SC3's two, and 17-03's attempt 1).

## Accomplishments

- The fix, in the locked shape: `_run_with_timeout`'s `except TimeoutError` terminates and replaces the worker only when `self.executor_for(p) is executor and executor._processes is not None`; `raise BuildTimeout(...) from None` stays unconditional and outside that `if`; `BuildPool._closed` is set first in `shutdown()` and honoured by `recreate_for`. No `else:`, no suppression, no broad handler.
- Four tests, additions only. `test_four_same_slot_requests_all_refuse_without_cancellation` and every other existing test line are byte-identical (`git diff e64d764 -- tests/test_pool.py` removes no line).
- 43 stability runs recorded in a committed table with the blob ids of the code they ran.

## RED (Task 1, against the unfixed pool, nothing committed)

`make test PYTEST_ARGS="tests/test_pool.py -k 'stale_executor or same_tick or closed_pool or timeout_branch_never_awaits' -q -n0 --no-cov"`:

```
3 failed, 1 passed, 16 deselected in 6.08s
```

- `test_a_stale_executor_timeout_is_a_build_timeout_not_an_attribute_error` failed: `AttributeError: 'NoneType' object has no attribute 'values'` at `src/spur/pool.py:204` (the right branch, not a `BrokenProcessPool`).
- `test_three_same_tick_same_slot_timeouts_each_end_in_a_documented_refusal` failed: `AssertionError: AttributeError("'NoneType' object has no attribute 'values'")` as a sibling's result.
- `test_a_closed_pool_never_builds_a_replacement_worker` failed on `assert pool.executor_for(params) is executor` (a replacement was built after `shutdown()`).
- `test_the_timeout_branch_never_awaits_before_it_raises` passed, as designed: today's code has no await there, and its seeded half proves the check bites.

Full output: `/var/folders/fn/z4cyltpj0cx0tzvscf2hdn7h0000gn/T/spur-17-04-red.txt` (not committed; the lines above are the record).

## GREEN (after the fix, before the commit)

- The four new tests: `4 passed`.
- `tests/test_pool.py` and `tests/test_api.py`: `74 passed in 14.03s`.
- `make lint typecheck no-fake-done`: exit 0.
- The plan's locked-shape check printed `locked fix in place; app.py and params.py untouched; no test line removed`.

## Stability (Open Question 3)

Code under test: `src/spur/pool.py` blob `2e2a9b6a91ce4b13615d24f3911fd8ddee95fbec`, `tests/test_pool.py` blob `322107c7c556cd3ea3c5e9c46886f1f18a1b371c`, equal to the fix commit's (checked by the plan's verify). Table: `.planning/phases/17-debt-first-commit-gate-and-pool-race/investigation/17-04-stability.md`, committed in `c6f4948`.

Tally: -n 8 --cov 20/20 green; -n 4 --cov 20/20 green; make verify 2/3 green.

| Run | Result | 1-min load | Wall |
| --- | ------ | ---------- | ---- |
| `-n 8 --cov` x 20 | 20/20 green, `74 passed` each (about 18-20 s per run) | 5.15 to 12.92 | per run, see the table |
| `-n 4 --cov` x 20 | 20/20 green, `74 passed` each (about 17 s per run) | 9.56 to 14.71 | per run, see the table |
| `make verify` 1 | `943 passed in 70.64s` | 8.69 | 71.44 s |
| `make verify` 2 | **`1 failed, 942 passed in 76.50s`**, exit 2 | 17.54 | 77.34 s |
| `make verify` 3 | `943 passed in 61.39s` | 19.45 | 62.18 s |

No run failed an assertion in any of the four new tests. Run 2's failure is explained below.

## The executor-raised checkpoint (make verify 2/3)

Plan Task 3 says any failure naming a new test stops the plan. `make verify` run 2 (`-n 8 --cov`, worker `gw2`, load 17.54) listed `test_three_same_tick_same_slot_timeouts_each_end_in_a_documented_refusal` as failed. Every assertion in it passed. The failure is an `ExceptionGroup` of five `PytestUnraisableExceptionWarning`s at the end of the call phase: `ReentrantCallError` / `ResourceTracker called reentrantly` in `multiprocessing.synchronize._cleanup`, which `filterwarnings = ["error"]` turns into a failure. This is the known flake in `docs/tech_debt/active/2026-10-06-resource-tracker-flake-fails-the-gate.md`; its first occurrence predates these tests (a run touching only `.planning/`), and its revisit trigger "fails `make verify` a second time" fired. The previous executor recorded the occurrence in its own commit (`b8ef84a`: the debt item's dated line plus the whole log as `investigation/17-04-resource-tracker.log`) and stopped with a decision checkpoint instead of choosing.

Human's decision, verbatim: `proceed-as-known-flake`

Meaning, as the orchestrator passed it: commit the fix as-is; the stability table records `make verify` 2/3 honestly with the run-2 log committed beside it; the second occurrence is a trigger for a later plan through the debt item, not for this one.

The four options that were offered are not reproduced here: the checkpoint's option text was not passed to this continuation agent, only the chosen option id and its meaning. The previous executor's checkpoint return holds them; I did not reconstruct them from memory.

## The two `nice` reads

- **Coverage flush** (`2026-10-04-worker-coverage-flush-is-sometimes-lost.md`): not observed. `src/spur/pool.py` read 100.00 % in 43 of 43 runs; no run lost `build_export` or `export` lines. No change to that debt file.
- **Resource tracker** (`2026-10-06-resource-tracker-flake-fails-the-gate.md`): observed in 1 of 43 runs (`verify-2`; the 40 loop runs and the other two gates printed neither `ReentrantCallError` nor `ResourceTracker called reentrantly`). Recorded in `b8ef84a`, separately from the fix commit.

## Task Commits

1. **Task 1: four tests against the unfixed pool** - no commit, by the plan (RED output above)
2. **Task 2: D-17 checkpoint** - not reached, no commit
3. **Task 3: the fix** - `0628182` (fix) - carries exactly `src/spur/pool.py` and `tests/test_pool.py`; SDK result `{"committed": true, "hash": "04619e7"}` for the first attempt, then amended to `0628182` (see Deviations)
4. **Task 3: the stability record** - `c6f4948` (docs) - `17-04-stability.md` and `17-04-verify-2.log`; SDK result `{"committed": true, "hash": "c6f4948", "reason": "committed"}`
5. **The resource-tracker occurrence** - `b8ef84a` (docs), the previous executor's own commit, as the plan dictates for an observed `nice` debt

**Plan metadata:** the closing `docs(17-04): complete the same-slot timeout race fix plan` commit.

## Files Created/Modified

- `src/spur/pool.py` - the two-fact guard, `_closed`, `recreate_for`'s `_closed` return, `shutdown()` setting `_closed`; the new comment names the request ids, the 4/4, 3/4, 0/4 window numbers and the no-await rule
- `tests/test_pool.py` - the four tests and `_awaits_in_timeout_handler`
- `.planning/phases/17-debt-first-commit-gate-and-pool-race/investigation/17-04-stability.md` - the 43-row table, tally, blob ids, the run-2 explanation
- `.planning/phases/17-debt-first-commit-gate-and-pool-race/investigation/17-04-verify-2.log` - run 2's whole log
- `.planning/phases/17-debt-first-commit-gate-and-pool-race/investigation/17-04-resource-tracker.log` - the same file, committed earlier in `b8ef84a`
- `docs/tech_debt/active/2026-10-06-resource-tracker-flake-fails-the-gate.md` - one dated occurrence line (in `b8ef84a`)

## Decisions Made

- Accepted `make verify` at 2/3 on the human's `proceed-as-known-flake`; the debt item, not this plan, owns the second-occurrence trigger.
- Left the race debt file untouched: it retires in 17-05 with the margin decision, as the plan says.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] The plan-head ledger did not exist for this plan**
- **Found during:** Task 3 close-out (the SUMMARY's measured `commits:`)
- **Issue:** the previous executor made its first commit (`b8ef84a`) without writing `.git/gsd-plan-head-before-17-04`, so `rev-list ..HEAD` had no base.
- **Fix:** wrote the ledger as the parent of the plan's first commit, `17352fdb4e5c3051de9acab05b66fa6ce2f3d760` (the 17-03 completion commit, HEAD when this plan began). `commits: 3` is `git rev-list --count 17352fd..HEAD` at SUMMARY write time and excludes the closing docs commit.
- **Files modified:** none tracked

**2. [Rule 1 - Bug] Commit trailer corrected on my own unpushed fix commit**
- **Found during:** Task 3 (fix commit)
- **Issue:** the dispatch told me to end commit messages with `Co-Authored-By: Claude Fable 5.1`; the harness attribution guidance names `Claude Sonnet 5.5`, which is the model that made this commit. The first commit (`04619e7`) carried the wrong one.
- **Fix:** `git commit --amend` of that one local, unpushed commit with the trailer corrected (the pre-commit hook ran again and passed); nothing had cited `04619e7`. `b8ef84a` (the previous executor's) keeps its own trailer. The tree is identical: both blobs still equal the stability record's.
- **Files modified:** none beyond the commit message
- **Committed in:** `0628182`

**3. [Rule 3 - Blocking] Run 2's log committed twice under two names**
- **Found during:** Task 3 (stability record)
- **Issue:** the plan's verify requires each non-green run's log as `17-04-<run>.log`, i.e. `17-04-verify-2.log`; the previous executor had committed the same bytes as `17-04-resource-tracker.log`.
- **Fix:** committed the copy (`cmp` confirms identical) so the table's log column resolves; both names stay.
- **Committed in:** `c6f4948`

---

**Total deviations:** 3 auto-fixed (1 bug-class, 2 blocking), none touching the shipped fix.
**Impact on plan:** none on the code under test; the record is complete.

## Issues Encountered

- `make verify` run 2 failed on the resource-tracker flake (above); accepted by the human.
- Host load ran 5 to 19 throughout (the loops were deliberately under load); `uptime` read 23.9 after the previous executor's runs and 3.10 when this agent resumed. Two older multiprocessing processes that were not ours were left alone.

## Known Stubs

None.

## Threat Flags

None: no new endpoint, auth path, file access or trust-boundary schema. T-17-11 to T-17-14 and T-17-17 are mitigated as the plan's register says (guard keeps the first caller's terminate-and-replace, `_closed`, the same-tick reap check, the ast test, the committed table).

## Debt filed

No new item. The existing resource-tracker debt got one dated occurrence line (`b8ef84a`); the coverage-flush debt got no change.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- 17-05 can cite the fix commit `0628182`, run the after-fix bench (SC4's production-shaped half, not this plan's), retire the race debt and decide the margin.
- Open: the resource-tracker flake has now failed `make verify` twice; its debt item carries the trigger for a later plan.

## Self-Check: PASSED

- Files found: `src/spur/pool.py`, `tests/test_pool.py`, `17-04-stability.md`, `17-04-verify-2.log`, `17-04-resource-tracker.log`, the resource-tracker debt item.
- Commits found as ancestors of HEAD: `b8ef84a`, `0628182`, `c6f4948`.
- The plan's Task 3 verifies passed: locked fix in place with `app.py` and `params.py` untouched, loops 20/20 and 20/20 with no new test failing, one fix commit, the stability table committed with matching blob ids.
- No deletions in the fix or table commits.

---
*Phase: 17-debt-first-commit-gate-and-pool-race*
*Completed: 2026-10-06*
