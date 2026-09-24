---
phase: 03-structured-logging-at-the-composition-boundary
plan: 02
subsystem: observability
tags: [logging, structured-logging, fastapi, process-pool, caplog]

# Dependency graph
requires:
  - phase: 03-structured-logging-at-the-composition-boundary
    provides: "Plan 03-01's records.py module (_emit, _gear_fields, _ms, configure) and the request_id/time.monotonic() clock already wired into app.model()"
provides:
  - "records.build_failed(), records.queue_refused() and records.worker_replaced() -- the remaining three of D-17's five per-event helpers"
  - "build.failed emitted at app.model()'s three except clauses, at a level (WARNING/ERROR) that says whose fault the failure was"
  - "queue.refused emitted at _build_slot()'s single admission refusal, naming the refused gear and the in-flight/ceiling counts"
  - "worker.replaced emitted inside pool.recreate_for's identity guard, exactly once per incident, with the hash slot and a cause of timeout or broken_pool"
affects: [03-03 (any remaining Phase 03 plan touching records.py/app.py/pool.py), any later phase reading stderr JSON for incident diagnosis]

# Actuals (#2632)
actuals:
  tokens: 5629
  tasks: 3
  commits: 3

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Per-event helper in records.py stays the only call site that touches the stdlib logger (D-17); app.py/pool.py never build an extra= dict by hand"
    - "A record's level is derived from D-15's 'whose fault is it' rule at the one place the exception class is known, not restated per call site"

key-files:
  created: []
  modified:
    - src/spur/records.py
    - src/spur/app.py
    - src/spur/pool.py
    - tests/test_api.py
    - tests/test_pool.py

key-decisions:
  - "build.failed carries no hash slot (flagged assumption 1, 03-02-PLAN.md): app.model() reaches the pool only through the injected build_backend seam and must never touch pool internals, so the slot rides on worker.replaced instead, correlated by stream adjacency and the cause field."
  - "worker.replaced carries no request correlation id (flagged assumption 2): threading a request id into BuildPool.export would change the BuildBackend type the CLI-shared path depends on; the preceding build.failed record already carries the request id, and worker.replaced follows it within microseconds."
  - "RED and GREEN land in one commit per task, not two, for all three tasks: the pre-commit hook runs the full `make verify` with no bypass (--no-verify is prohibited by both project policy and dispatch instructions), and a RED-only commit fails that hook by construction. Matches the choice STATE.md already records for Phase 2's TDD plans. Each RED phase was still proven by running the target test in isolation before any implementation changed, with output pasted into the corresponding commit message."

requirements-completed: [REQ-structured-logging]

coverage:
  - id: D1
    description: "A failed build emits one build.failed record naming the exception class and duration, at a level that says whose fault it was, and no export.served record follows it"
    requirement: "REQ-structured-logging"
    verification:
      - kind: integration
        ref: "tests/test_api.py#test_a_failed_build_emits_build_failed_naming_the_class_and_the_level"
        status: pass
      - kind: integration
        ref: "tests/test_pool.py#test_each_build_failure_mode_maps_to_its_own_status_and_type"
        status: pass
    human_judgment: false
  - id: D2
    description: "A refused request emits one queue.refused record naming the gear, the in-flight count and the ceiling, and the 503 response contract is unchanged"
    requirement: "REQ-structured-logging"
    verification:
      - kind: integration
        ref: "tests/test_api.py#test_a_saturated_service_emits_queue_refused_naming_the_gear_and_the_ceiling"
        status: pass
      - kind: integration
        ref: "tests/test_pool.py#test_health_queue_available_falls_while_a_slot_is_held"
        status: pass
    human_judgment: false
  - id: D3
    description: "A worker replacement emits exactly one worker.replaced record per incident, with the hash slot and a cause of timeout or broken_pool, from inside recreate_for's identity guard"
    requirement: "REQ-structured-logging"
    verification:
      - kind: integration
        ref: "tests/test_pool.py#test_a_wedged_build_is_terminated_and_its_worker_replaced"
        status: pass
      - kind: integration
        ref: "tests/test_pool.py#test_a_dying_worker_surfaces_as_broken_pool_and_is_replaced"
        status: pass
      - kind: integration
        ref: "tests/test_pool.py#test_two_same_slot_deaths_from_one_incident_replace_the_worker_once"
        status: pass
    human_judgment: false

duration: 27min
completed: 2026-09-24
status: complete
---

# Phase 3 Plan 2: The Three Failure Branches Summary

**`build.failed`, `queue.refused` and `worker.replaced` complete D-17's five per-event helpers, each observing an `except`/refusal/replacement branch that already existed rather than adding new control flow.**

## Performance

- **Duration:** 27 min
- **Started:** 2026-09-24T09:31:35Z
- **Completed:** 2026-09-24T10:01:00Z
- **Tasks:** 3
- **Files modified:** 5

## Accomplishments
- A failed build now says what failed (`build.failed`'s `exception` field, the literal class name), for how long (`duration_ms`, the same clock `export.served` uses) and whose fault it was (WARNING for the user's `BuildError`, ERROR for the service's `BuildTimeout`/`BrokenProcessPool`) -- all three response-contract statuses, types and headers untouched.
- A saturated service now says which gear it turned away and how far past its ceiling it was (`queue.refused`'s `in_flight`/`max_queued`), from the one refusal branch in `_build_slot`, which gained the request identity it needed to name the request.
- A worker replacement is now readable in the stream with its hash slot and its cause (`timeout` or `broken_pool`), emitted from exactly one place -- inside `recreate_for`'s existing identity guard, immediately after the counter it accompanies -- so the log agrees with `/api/health`'s `workers_replaced` counter down to the same one-incident-one-record guarantee CR-01/WR-01 already proved for the counter.

## Task Commits

Each task was committed atomically (RED+GREEN combined per commit -- see Deviations):

1. **Task 1: `build.failed`** - `7d64685` (feat)
2. **Task 2: `queue.refused`** - `b782bb0` (feat)
3. **Task 3: `worker.replaced`** - `21b8fe4` (feat)

**Plan metadata:** commit to follow (docs: complete plan)

## Files Created/Modified
- `src/spur/records.py` - Adds `build_failed()`, `queue_refused()` and `worker_replaced()`, completing D-17's five intent-named helpers
- `src/spur/app.py` - Calls `build_failed()` in `model()`'s three `except` clauses; `_build_slot()` gains `request_id`/`p`/`fmt`/`quality` params and calls `queue_refused()` before its 503 raise
- `src/spur/pool.py` - `recreate_for()` gains a `cause: str` parameter and calls `worker_replaced()` inside its identity guard, after `self.replaced += 1`; both `_run_with_timeout` call sites pass `"timeout"`/`"broken_pool"`
- `tests/test_api.py` - Adds the caplog branch tests for `build.failed` (three exception classes) and `queue.refused`; imports `BuildError`/`BuildTimeout`/`BrokenProcessPool`
- `tests/test_pool.py` - Updates the `_build_slot()` call site to the new signature; adds `worker.replaced` assertions to the two real-pool wedge/die tests and a record-count assertion to the two-same-slot-deaths regression guard; adds local `_event_records`/`_field` caplog helpers matching `test_api.py`'s own

## Decisions Made
See `key-decisions` in frontmatter: `build.failed` deliberately carries no hash slot (flagged assumption 1), `worker.replaced` deliberately carries no request id (flagged assumption 2), and RED+GREEN commits are combined per task rather than split (deviation, detailed below).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `queue.refused` test's `in_flight` assertion fixed to match how the test actually saturates the queue**
- **Found during:** Task 2 (writing the RED test for `queue.refused`)
- **Issue:** The test's first draft asserted `in_flight == MAX_QUEUED_BUILDS`, but the test saturates the queue the same way `test_a_saturated_service_refuses_instead_of_queueing` already does -- by acquiring `BUILD_QUEUE` directly, not through `_build_slot()` -- so the parent's `_in_flight_builds` counter (only incremented inside `_build_slot()`) never actually reaches `MAX_QUEUED_BUILDS` in this synthetic scenario. The assertion was wrong about what the code under test actually does, not the implementation.
- **Fix:** Capture `app_module._in_flight_builds` immediately before saturating the queue and assert the record's `in_flight` field equals that captured value, so the test checks the record against the module's own counter rather than a value the test happened to expect.
- **Files modified:** `tests/test_api.py`
- **Verification:** `make test PYTEST_ARGS="tests/test_api.py tests/test_pool.py -q"` -- 44 passed
- **Committed in:** `b782bb0` (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 bug, test-side only). **Impact on plan:** No production-code scope creep; the fix corrected a test assertion to match the queue-saturation mechanism the plan's own reference test (`test_a_saturated_service_refuses_instead_of_queueing`) already uses.

## Issues Encountered

**`gsd_run check tdd-red-evidence` does not support pytest output.** Per `tdd.md`'s Gate Enforcement Rules, each RED phase's evidence was run through `gsd_run check tdd-red-evidence <record.json>` before any implementation changed. The tool's TAP parser (`parseNodeTestSummary`/`tapFailedTestNames` in `gsd-core/bin/lib/prohibition-enforcement.cjs`) expects Node's `node --test` TAP output (`^# tests N`, `ok N - <name>`), which pytest's `-q` output never produces -- the check returns `INVALID_RED`/`zero_tests_discovered` on every genuinely-RED pytest run, regardless of whether the RED phase is valid. This is a tooling gap (Node-only TAP parser applied to a Python/pytest project), not an issue with this plan's RED phases: each RED run was independently verified by direct inspection of the pytest failure output, confirming the target test failed on the exact planned assertion (`assert len(...) == 1` -> `0 == 1`) rather than a collection/import/fixture error, before any production code changed. Documented here rather than silently worked around, per CLAUDE.md's "ground claims in evidence" and "flag guesses" directives -- future TDD plans in this phase (e.g. 03-03) will hit the same gap.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

All five of D-09's event names (`build.started`, `export.served` from Plan 03-01; `build.failed`, `queue.refused`, `worker.replaced` from this plan) are now emitted by the code and pinned by literal-string assertions in tests. `make verify` passes with all 96 tests. Ready for Plan 03-03 (if it exists) or Phase 03 verification.

---
*Phase: 03-structured-logging-at-the-composition-boundary*
*Completed: 2026-09-24*

## Self-Check: PASSED

- FOUND: src/spur/records.py (`def build_failed`, `def queue_refused`, `def worker_replaced`)
- FOUND: src/spur/app.py, src/spur/pool.py (`worker_replaced(slot=i` inside `recreate_for`)
- FOUND: tests/test_api.py, tests/test_pool.py
- FOUND commits: 7d64685, b782bb0, 21b8fe4
- Re-ran `make verify`: exits 0 (96 passed)
- Re-ran `make test PYTEST_ARGS="tests/test_api.py tests/test_pool.py tests/test_records.py -q"`: 55 passed
- Re-ran the three pre-existing response-contract tests named in `<verification>`: all pass unchanged
