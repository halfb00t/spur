---
phase: 27-ledger-tests-and-harness
plan: 03
subsystem: testing
tags: [pytest, process-groups, teardown, sigterm, sigkill, ps, test-image]

requires:
  - phase: 27-ledger-tests-and-harness
    provides: 27-02 left docs/tech_debt/INDEX.md and the investigation/ directory in a clean state (one writer per wave)
provides:
  - tests/process_group.py, a module with no browser-driver import that holds the server group teardown
  - stop_group reordered: the group is signalled before any ps read and before the leader is reaped
  - a failed or absent ps fails the teardown as "survivors unknown" with both signals already sent
  - tests/test_process_group.py, 3 tests in 0.04 s, run at commit and in make test-image
  - the stop_group debt item retired
affects: [27-06 bench/RESULTS.md "Seen red once (Phase 27)" rows, Phase 28 disposition files]

actuals:
  tokens: 6500
  tasks: 2
  commits: 2   # MEASURED: git rev-list --count 2ef2a22..HEAD at write time (before the SUMMARY commit)

plan_head_before: 2ef2a22aa53b7f78ec7d67f6eaf9c464f0d1843f
plan_head_after: a7c5f78a0bef27c849e3a2e6b585576cb225aa9a

tech-stack:
  added: []
  patterns:
    - "A test-only helper module split from its driver-importing sibling so the unit test runs in the commit slice and in the image"
    - "Event order recorded from wrapped functions (signal, read, wait, poll) instead of timed; class-level Popen.wait/poll bypass the recorders for cleanup"

key-files:
  created:
    - tests/process_group.py
    - tests/test_process_group.py
    - .planning/phases/27-ledger-tests-and-harness/investigation/27-03-red-old-order.log
    - .planning/phases/27-ledger-tests-and-harness/investigation/27-03-green.log
    - .planning/phases/27-ledger-tests-and-harness/investigation/27-03-image.log
    - .planning/phases/27-ledger-tests-and-harness/investigation/27-03-red-leader-only.log
  modified:
    - tests/browser_session.py
    - docs/tech_debt/INDEX.md
    - docs/tech_debt/resolved/2026-10-10-stop-group-reads-ps-before-it-signals.md

key-decisions:
  - "The leader-only red that fires on the real server is the 21-01 break (os.kill(pgid, SIGKILL)), not the plan's literal os.kill(pgid, sig): uvicorn shuts its pool workers down on SIGTERM, so a leader-only SIGTERM leaves no survivor"
  - "process_group.py's docstring says 'browser driver', never the package name, so the plan's own 'names no playwright' check holds"

patterns-established:
  - "Signal first, read second: a reader that can fail decides how long to wait and what to report, never whether to signal"

requirements-completed: [REQ-stop-group-signals-first]

coverage:
  - id: D1
    description: "The teardown lives in tests/process_group.py, importable without the browser driver; the move is verbatim (AST-equal to v0.5) and committed alone"
    requirement: REQ-stop-group-signals-first
    verification:
      - kind: other
        ref: "Task 1 automated checks: the sys.modules['playwright'] = None import, the AST comparison against v0.5:tests/browser_session.py, and make test PYTEST_ARGS=\"tests/test_browser.py tests/test_browser_pins.py -n0 --no-cov -q\" (5 passed in 23.38s)"
        status: pass
    human_judgment: false
  - id: D2
    description: "stop_group sends SIGTERM to the group before any ps read, wait or poll; a group that reads empty after SIGTERM gets no SIGKILL"
    requirement: REQ-stop-group-signals-first
    verification:
      - kind: unit
        ref: "tests/test_process_group.py#test_the_group_is_signalled_before_ps_is_read_or_the_leader_reaped"
        status: pass
    human_judgment: false
  - id: D3
    description: "A failed or absent ps fails the teardown as 'survivors unknown' after SIGTERM and SIGKILL were both sent"
    requirement: REQ-stop-group-signals-first
    verification:
      - kind: unit
        ref: "tests/test_process_group.py#test_a_failed_ps_fails_the_teardown_with_the_group_already_signalled[ps-exits-non-zero] and [ps-is-absent]"
        status: pass
    human_judgment: false
  - id: D4
    description: "The tests were seen red against the unreordered body and the survivor check still fires on the real server"
    requirement: REQ-stop-group-signals-first
    verification:
      - kind: other
        ref: "investigation/27-03-red-old-order.log (3 failed) and 27-03-red-leader-only.log run 2 (still has live pids ... after SIGTERM (10 s) and SIGKILL (5 s))"
        status: pass
    human_judgment: false
  - id: D5
    description: "The stop_group debt item is retired in the fixing commit"
    verification:
      - kind: other
        ref: "Task 2 automated check over docs/tech_debt/{resolved,active}/ and INDEX.md"
        status: pass
    human_judgment: true
    rationale: "Whether the Resolved in wording and the INDEX row read as the ledger's convention is a reading, not a test"

duration: 6min
completed: 2026-10-20
status: complete
---

# Phase 27 Plan 03: stop_group signals first Summary

**`stop_group` now sends SIGTERM to the whole server group before any `ps` read or `proc.wait()`, a failed or absent `ps` fails the teardown as "survivors unknown" with SIGTERM and SIGKILL already sent, and a 0.04 s unit test in a driver-free module proves both paths at commit and in `make test-image`.**

## Performance

- **Duration:** 6 min
- **Started:** 2026-10-20T13:33:10Z
- **Completed:** 2026-10-20T13:39Z
- **Tasks:** 2
- **Files modified:** 9 in the two task commits (3 tests files, INDEX, the moved debt item, 4 logs)

## Accomplishments

- Task 1 (`675cf68`): `group_members`, `_signal_group`, `stop_group`, `_log_tail`, `TERM_BOUND_S` (10.0) and `KILL_BOUND_S` (5.0) moved to `tests/process_group.py`; `browser_session.py` imports them and keeps `READY_BOUND_S`. The four function ASTs equal v0.5's. The real browser test and the pins test pass through the moved code (`5 passed in 23.38s`).
- Task 2 (`a7c5f78`): `stop_group` reordered. Per signal it calls `_signal_group` first, then reads and polls inside a `try`; `CalledProcessError` or `OSError` marks the survivors unknown and goes straight to the next signal. The leader is reaped only after the loop. The two failure messages are "survivors unknown" and "still has live pids ... after SIGTERM (10 s) and SIGKILL (5 s)". The dead first read and the dead `bound = TERM_BOUND_S` assignment are gone (21 IN-01).
- Test results: red against the moved, unreordered body `3 failed in 0.05s`; green `3 passed in 0.04s`; in the image `3 passed in 0.02s`. No `sleep 60` of the runs survived (`pgrep` read 0 before and after each).
- `make verify.fast` exits 0: `929 passed in 10.07s` (926 before, plus the 3). `make lint typecheck` clean. `Makefile` and `tests/test_hooks.py` are unchanged against B (`675cf68^`); no new `--ignore`.

## Red runs

| Guard | Break | First failure line | Log |
|---|---|---|---|
| signal-first test | the unreordered body | `AssertionError: ['read', 'signal SIGTERM', 'read', 'wait']`, `assert 'read' == 'signal SIGTERM'` | `investigation/27-03-red-old-order.log` |
| failed-ps test, both rows | the unreordered body | `CalledProcessError: Command '['ps']' returned non-zero exit status 1` and `FileNotFoundError: [Errno 2] No such file or directory: 'ps'` escape before any signal; `3 failed in 0.05s` | same |
| survivor check, real server | `_signal_group` sends `os.kill(pgid, signal.SIGKILL)` to the leader only (the 21-01 break) | `Failed: server process group 46075 still has live pids [46103, 46206, 49708] after SIGTERM (10 s) and SIGKILL (5 s)`, `2 passed, 1 error in 38.48s` (teardown 15.14 s) | `investigation/27-03-red-leader-only.log`, run 2 |

After the leader-only red, the orphaned workers were killed by group (`kill -KILL -- -46075`) and `ps -A -o pgid=,pid=` filtered to 46075 listed nothing; the module was restored from a saved copy and `cmp` confirmed it. `grep -c 'os.kill(pgid' tests/process_group.py` reads 0, `os.killpg(pgid, sig)` is present.

## Task Commits

1. **Task 1: move the teardown into `tests/process_group.py`** - `675cf68` (refactor)
2. **Task 2: the unit test, the reorder, the leader-only red, the item retired** - `a7c5f78` (fix)

**Plan metadata:** the commit that adds this SUMMARY, STATE.md, ROADMAP.md and REQUIREMENTS.md (docs: complete plan)

TDD note: `workflow.tdd_mode` is not enabled for this plan (`type: execute`), so RED and GREEN share the fix commit, as 27-02 and Phase 11 did; the red was run and kept in the log before the reorder was written.

## Files Created/Modified

- `tests/process_group.py` - the teardown, reordered; imports no browser driver
- `tests/test_process_group.py` - `test_the_group_is_signalled_before_ps_is_read_or_the_leader_reaped`, `test_a_failed_ps_fails_the_teardown_with_the_group_already_signalled` (ids `ps-exits-non-zero`, `ps-is-absent`)
- `tests/browser_session.py` - imports the three names; `import signal` and the six moved definitions removed
- `docs/tech_debt/INDEX.md`, `docs/tech_debt/resolved/2026-10-10-stop-group-reads-ps-before-it-signals.md` - item retired
- `.planning/phases/27-ledger-tests-and-harness/investigation/27-03-{red-old-order,green,image,red-leader-only}.log`

## Decisions Made

- The leader-only red is recorded as two runs in one log. Run 1 is the plan's literal mutation and it did not go red; run 2 is the 21-01 mutation and it did (see Deviations).
- The SIGTERM grace is unchanged: after SIGTERM the group is polled until it reads empty or 10.0 s pass. Only a `ps` that cannot read skips it, because it cannot observe.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug in the plan's expectation] The plan's leader-only mutation does not turn the real browser test red**
- **Found during:** Task 2 step 6
- **Issue:** with `_signal_group` calling `os.kill(pgid, sig)` (leader only, SIGTERM then SIGKILL), `tests/test_browser.py` passed (`2 passed in 23.66s`). uvicorn handles SIGTERM by shutting its pool workers down, so the group reads empty before SIGKILL; there is no survivor to report. The expected "still has live pids" never appeared.
- **Fix:** ran the break `bench/RESULTS.md` row 21-01 actually names, `os.kill(pgid, signal.SIGKILL)` to the leader only. That fails the teardown with `still has live pids [46103, 46206, 49708] after SIGTERM (10 s) and SIGKILL (5 s)`. Both runs are in the log with a header each.
- **Files modified:** none kept (the mutation was reverted by `cp` from a saved copy, `cmp` clean)
- **Verification:** the plan's three greps over the log hold; the module has no leader-only call
- **Committed in:** `a7c5f78` (the log)

**2. [Rule 3 - Blocking] The module docstring tripped the plan's "names no playwright" check**
- **Found during:** Task 1 verify
- **Issue:** the plan asks the docstring to explain why the module is separate (the other module imports playwright) and its AST check asserts the substring `playwright` is absent from the file.
- **Fix:** the docstring says "the browser driver".
- **Files modified:** tests/process_group.py
- **Verification:** the check prints `verbatim move`
- **Committed in:** `675cf68`

---

**Total deviations:** 2 auto-fixed (1 Rule 1, 1 Rule 3)
**Impact on plan:** none on scope. The first records that the plan's leader-only mutation is weaker than the 21-01 one; the survivor check is still shown firing on the real thing.

## Issues Encountered

- `.planning/milestone.lock` is untracked and predates this plan; left alone.
- `ruff format --check tests/` would reformat several test files that predate this plan; the project gate is `ruff check` through `make lint`, which passes. Not touched.

## Known Stubs

None.

## Debt filed

None filed. One item retired: `docs/tech_debt/resolved/2026-10-10-stop-group-reads-ps-before-it-signals.md` (`Resolved in: fix(tests): stop_group signals the server group before it reads ps`).

## Authentication Gates

None.

## User Setup Required

None - no external service configuration required.

## Threat Flags

None. No new network endpoint, auth path or trust-boundary file access; the spawn stays an argv list with no shell.

## Next Phase Readiness

- 27-06 can copy the three rows above into "Seen red once (Phase 27)". It should also note that the leader-only SIGTERM-and-SIGKILL form of the 21-01 break does not go red on the real server; only the SIGKILL-to-leader form does.
- `docs/tech_debt/INDEX.md` is free for the next wave.

---
*Phase: 27-ledger-tests-and-harness*
*Completed: 2026-10-20*

## Self-Check: PASSED

Verified: `tests/process_group.py`, `tests/test_process_group.py`, the four `27-03-*.log` files and the retired item under `docs/tech_debt/resolved/` exist; `675cf68` and `a7c5f78` are ancestors of HEAD; no `docs/tech_debt/active/` copy of the item remains; `git diff --exit-code 675cf68^ -- Makefile tests/test_hooks.py` exits 0.
