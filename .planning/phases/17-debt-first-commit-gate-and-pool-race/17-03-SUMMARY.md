---
phase: 17-debt-first-commit-gate-and-pool-race
plan: 03
subsystem: testing
tags: [bench, latency, build-pool, timeout-race, httpx]

requires:
  - phase: 17-debt-first-commit-gate-and-pool-race
    provides: "17-02: SDK commits work under the make verify.fast hook (5a3332f), so both commits here went through gsd-tools query commit"
  - phase: 13-latency-bar
    provides: "run_composed, the composed worst row, SC3's two undocumented 500s, the deferred ten-identical scenario"
provides:
  - "bench/latency.py identical scenario: _fetch(..., record_500=True), run_composed(base_url, rows, label, record_500), _identical_rows, scenario_identical, registered but not in DEFAULT_SCENARIOS"
  - "bench/RESULTS.md '## Same-slot timeout race (Phase 17)': attempt 1 before the fix, hit, with the server's own AttributeError records, and the pinned verdict line"
  - "investigation/attempt-1.server.log and attempt-1.client.txt: the raw records behind it"
  - "the D-11 reading: the slot-holding request (29.42 s alone) read 503 timeout at 30.01 s client wall, 30003 ms server duration, at load 5.48 -> 5.88"
affects: [17-04, 17-05]

actuals:
  tokens: 4379
  tasks: 2
  commits: 2

tech-stack:
  added: []
  patterns:
    - "a scenario that must observe an undocumented status opts in with a flag (record_500); every other caller still raises on it"
    - "a reproduction enters the record only when the client's 500 rows and the server's own AttributeError build.failed records agree"

key-files:
  created:
    - .planning/phases/17-debt-first-commit-gate-and-pool-race/investigation/attempt-1.server.log
    - .planning/phases/17-debt-first-commit-gate-and-pool-race/investigation/attempt-1.client.txt
  modified:
    - bench/latency.py
    - tests/test_bench.py
    - bench/RESULTS.md

key-decisions:
  - "Stopped at the first hit (D-15): attempts 2 and 3 were not run; the verdict is 'Reproduced in attempt 1.'"
  - "The raw 7.4 MB server log is committed uncut, as the plan says; Phase 13's investigation directory already holds multi-MB raw files and no hook limits size"

patterns-established:
  - "Rows are matched to server request ids by outcome and start order when the client does not read ids, and the write-up says so"

requirements-completed: [REQ-same-slot-timeout-race-reproduced]

plan_head_before: 3fbc376053eee99280ce019a0bb467c43f630039
plan_head_after: fdf9c21f227d4ae3f51f81ef42ba0fd257b56093

coverage:
  - id: D1
    description: "the identical scenario is registered in _SCENARIOS, absent from DEFAULT_SCENARIOS, offered on the command line, and fires the composed worst row ten times"
    requirement: REQ-same-slot-timeout-race-reproduced
    verification:
      - kind: unit
        ref: "tests/test_bench.py#test_the_identical_scenario_fires_the_worst_composed_row_ten_times"
        status: pass
      - kind: unit
        ref: "tests/test_bench.py#test_the_no_argument_latency_run_is_still_concurrent_then_single"
        status: pass
    human_judgment: false
  - id: D2
    description: "_fetch records a 500 only when record_500=True; the default and every other status still raise"
    requirement: REQ-same-slot-timeout-race-reproduced
    verification:
      - kind: unit
        ref: "tests/test_bench.py#test_a_500_is_recorded_only_when_the_caller_asks"
        status: pass
      - kind: unit
        ref: "tests/test_bench.py#test_a_503_is_recorded_by_the_reason_the_server_gave"
        status: pass
    human_judgment: false
  - id: D3
    description: "the identical report omits the single/concurrent baseline line, as composed does"
    requirement: REQ-same-slot-timeout-race-reproduced
    verification:
      - kind: unit
        ref: "tests/test_bench.py#test_the_composed_report_omits_the_single_concurrent_baseline_line"
        status: pass
    human_judgment: false
  - id: D4
    description: "the same-slot timeout race was reproduced on a fresh server with shipping defaults before any fix: three client 500 rows, three server build.failed AttributeError records, three ASGI exceptions"
    requirement: REQ-same-slot-timeout-race-reproduced
    verification:
      - kind: other
        ref: "Task 2 automated check: attempts ['1'] hits [True]; verdict line == 'Reproduced in attempt 1.'"
        status: pass
    human_judgment: true
    rationale: "Whether a recorded 500 is 'the race' is read from the server records by a person as well as the check (the plan's adjacency probe is a backstop); a reviewer should read the attempt 1 readout in bench/RESULTS.md"
  - id: D5
    description: "the D-11 margin reading of the slot-holding request, with its load, recorded for L37"
    requirement: REQ-worst-row-margin-decided
    verification: []
    human_judgment: true
    rationale: "One reading at one host load; what it means for the margin is L37's decision in 17-05, not this plan's"

duration: 4min
completed: 2026-10-06
status: complete
---

# Phase 17 Plan 03: The ten-identical-worst-row race, reproduced Summary

**The `identical` latency scenario (ten copies of the composed worst row, one hash slot) reproduced the same-slot undocumented 500 in its first attempt on a fresh server: three raw 500s, each backed by an `AttributeError: 'NoneType' object has no attribute 'values'` `build.failed` record, after one `timeout` worker replacement.**

## Performance

- **Duration:** about 4 min (247 s from the first command to the last verified check)
- **Started:** 2026-10-06T09:16:15Z
- **Completed:** 2026-10-06T09:20:22Z
- **Tasks:** 2
- **Files modified:** 3 tracked (`bench/latency.py`, `tests/test_bench.py`, `bench/RESULTS.md`), plus 2 new records under `investigation/`

## Accomplishments

- **Scenario.** `python -m bench.latency identical` exists, records a 500 instead of raising, fires `composed.json` row 4 ten times, and stays out of the no-argument run (`DEFAULT_SCENARIOS` is still `("concurrent", "single")`; `--help` offers `identical`).
- **Reproduction (SC3).** Attempt 1, fresh server on :8001, shipping defaults (2 workers, 4 queued builds, 30 s), commit under test `814f4f3`: rows 2, 3 and 5 returned `500`; the server logged three `build.failed` with `exception: AttributeError` and three "Exception in ASGI application" lines; one `worker.replaced` (slot 0, `cause: timeout`). The three `AttributeError` records land 2.7, 11.3 and 12.5 ms after the slot-holder's own `BuildTimeout` record.
- **D-11 reading.** The slot-holder (#1, `cf3e6608`, 29.42 s alone) was not served: `503 timeout`, client wall 30.01 s, server `duration_ms` 30003, at load 5.48 -> 5.88 (1-minute, `sysctl -n vm.loadavg`), with three same-key siblings queued behind it. One reading at one load; L37 (17-05) reads it.

## Verdict line, verbatim (17-04's D-17 checkpoint reads this from `bench/RESULTS.md`)

`Reproduced in attempt 1.`

D-17's checkpoint at 17-04 is not reached; the fix is written against a failure someone saw. Attempts 2 and 3 were not run (stop at the first hit, D-15).

## TDD record (Task 1)

- **RED**, `make test PYTEST_ARGS="tests/test_bench.py -q --no-cov"` before any production change:
  `tests/test_bench.py:45: in <module>  from bench.latency import (` ...
  `E   ImportError: cannot import name '_identical_rows' from 'bench.latency'`,
  `ERROR tests/test_bench.py - ImportError while importing test module ...`, `1 error in 4.34s`, `make: *** [Makefile:143: test] Error 1`. This is the red the plan names. Semantic assessment: a collection error, not an assertion on the planned behavior, so by `tdd.md` strictness it is weak RED evidence; the plan states it as the expected red, and `workflow.tdd_mode` is not enabled in `.planning/config.json`, so the classifier gate does not apply.
- **GREEN**, same command after the change: `26 passed in 3.41s`. Then `make lint typecheck`: `All checks passed!` and `Success: no issues found in 39 source files`.
- **REFACTOR:** none; nothing to clean up.
- **One commit, not test then feat.** `tdd.md`'s commit-scope contract asks for a `test(...)` commit before the `feat(...)` commit. The pre-commit hook runs `make verify.fast`, which includes `tests/test_bench.py`, so a commit of a red test is blocked unless the hook is bypassed, and `--no-verify` and `SKIP=` are forbidden here. The plan also asks for exactly one commit carrying both files. The RED run above is the record instead.

## Task Commits

1. **Task 1: the ten-identical-worst-row scenario** - `814f4f3` (feat). SDK JSON: `{"committed": true, "hash": "814f4f3", "reason": "committed"}`, 12.2 s real under the hook. Carries exactly `bench/latency.py` and `tests/test_bench.py`.
2. **Task 2: attempt 1 recorded with its verdict** - `fdf9c21` (docs). SDK JSON: `{"committed": true, "hash": "fdf9c21", "reason": "committed"}`, 12.1 s real. Carries `bench/RESULTS.md`, `attempt-1.server.log`, `attempt-1.client.txt`.

D-07's recovery never ran: neither commit returned `committed: false`.

**Plan metadata:** the closing `docs(17-03)` commit of this file, STATE.md, ROADMAP.md and REQUIREMENTS.md (made after this file; not counted in `commits:`, which was measured before it: `git rev-list --count 3fbc376..HEAD` = 2).

## Attempt 1: preflight, loads, outcome

- Preflight: `lsof -nP -iTCP:8001 -sTCP:LISTEN` printed nothing; `docker ps` showed no containers (see Deviations); load 5.94 at the preflight and 5.48 at the start; HEAD `814f4f3`; no `SPUR_*` in the environment; `pgrep -fl 'pre_commit hook-impl|pytest|mypy'` printed nothing.
- Server started with `env -u SPUR_BUILD_WORKERS -u SPUR_MAX_QUEUED_BUILDS -u SPUR_BUILD_TIMEOUT SPUR_PORT=8001 .venv/bin/spur serve` (PID 27787); first `/api/health`: `{"workers":2,"queue_available":4,"workers_replaced":0}`.
- Client exit status 0. Table: 1 `503 timeout`, 3 `500`, 6 `503 busy`; `workers_replaced` 0 -> 1.
- Server stopped by PID; :8001 free afterwards (`lsof` printed nothing). Load after: 5.88. `docker ps` after: no containers.
- Classification: a hit, because a `500` row and a `build.failed` with `exception: AttributeError` both exist and agree 3 to 3 to 3 (client rows, server records, ASGI exceptions). No `503 pool_broken` row exists, so none was counted as the race. Rows were matched to request ids by outcome and start order (the client does not read ids); that is stated in the write-up.

## Files Created/Modified

- `bench/latency.py` - `record_500` on `_fetch`, `rows`/`label`/`record_500` on `run_composed`, `_identical_rows`, `scenario_identical`, registry entry, the baseline-line omission for `identical`, a comment saying the fourth scenario changes nothing for the no-argument run
- `tests/test_bench.py` - the two new tests, the registry and baseline tests extended; `test_a_503_is_recorded_by_the_reason_the_server_gave` untouched (`git diff e64d764` removes no line inside it)
- `bench/RESULTS.md` - `## Same-slot timeout race (Phase 17)` with the question, the scenario, `### Attempt 1 (before the fix)` and `### Before the fix: verdict`
- `investigation/attempt-1.server.log` - the server's stderr, 43,328 JSON lines, 7.4 MB, 43,292 of them uvicorn access lines for the `/api/health` samples; sha1 `7de9791f28609415a1bca8917ffbd56e20a3d761`
- `investigation/attempt-1.client.txt` - the client's whole output

## Decisions Made

None beyond the plan: stop at the first hit (D-15), commit the raw log uncut. No new `Lxx`.

## Deviations from Plan

**1. [Rule 3 - Blocking] `gsd_run` is not on PATH**
- **Found during:** start
- **Fix:** every gsd-tools call used `node "$HOME/.claude/gsd-core/bin/gsd-tools.cjs"`, as the dispatcher instructed. No files modified.

**2. [Observation, not a code change] `spur-spur-1` was not running**
- **Found during:** Task 2 preflight
- **Issue:** the plan assumes the long-lived container holds :8000 and asks that it read the same in `docker ps` before and after. `docker ps` printed only the header (no containers) before and after, and nothing listened on :8000. The condition holds trivially: nothing was started, stopped or touched, and the attempt never targeted :8000. Not a stop condition (the plan's only stop is a listener on :8001).
- **Recorded in:** the attempt's Host state in `bench/RESULTS.md`.

**3. [Process] RED and GREEN share one commit**
- See "TDD record" above: the commit hook runs the tests, the plan asks for one commit, and the hook may not be bypassed.

**Total deviations:** 1 auto-fixed (Rule 3, tooling path), 1 observation, 1 process note. **Impact on plan:** none on the outcome.

## Issues Encountered

- The harness's own latency section, printed after the table, reports idle p95 0.6 ms, under-load p95 1.3 ms, ratio 2.11x against a "pass bar is <= 2.00x" line. That section is the shared report format and is not a bar reading for this scenario (no quiet-host gate, one run, not the gate); the write-up says it is kept in `attempt-1.client.txt` and not read against the bar. Nothing was changed in the harness for it.
- The raw server log is large because uvicorn logs every health sample. It is committed uncut as planned; filtering it would have been a change to the record.

## Known Stubs

None.

## Threat Flags

None. T-17-08 (disturbing `spur-spur-1`): the attempt used a fresh server on :8001, nothing was listening on :8001 before or after, and no container existed to disturb. T-17-09 (a reproduction nobody saw): the 500 rows are tied to the server's `AttributeError` records by the Task 2 check, which passed. T-17-10 (paths in a committed log): accepted; the log carries uvicorn tracebacks with local paths, the same kind of record SC3 committed, and no secret or user data.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Ready for 17-04 (the pool fix). 17-04's Task 2 reads the verdict line from `bench/RESULTS.md`: it is exactly `Reproduced in attempt 1.`, so the D-17 checkpoint is not presented. 17-05 reads the D-11 reading above for L37, and writes `### After the fix` into the same section. REQ-worst-row-margin-decided stays open until 17-05 (the margin decision is L37's). No server is left listening on :8001.

## Self-Check: PASSED

- FOUND: `bench/latency.py`, `tests/test_bench.py`, `bench/RESULTS.md`, `investigation/attempt-1.server.log`, `investigation/attempt-1.client.txt`
- FOUND: commits `814f4f3` and `fdf9c21` (both ancestors of HEAD); `git rev-list --count 3fbc376..HEAD` = 2 at write time
- FOUND in `bench/latency.py`: `record_500: bool = False`, `def _identical_rows(`, `def scenario_identical(base_url: str) -> ScenarioResult:`, `"identical": scenario_identical`; `DEFAULT_SCENARIOS` unchanged
- Task 2's two automated checks printed `attempts ['1'] hits [True]` and `write-up complete`; the commit-subject checks printed `scenario committed` and `attempts committed`

---
*Phase: 17-debt-first-commit-gate-and-pool-race*
*Completed: 2026-10-06*
