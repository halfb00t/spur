---
phase: 02-cad-off-the-event-loop
plan: 03
subsystem: api
tags: [asyncio, concurrent.futures, fastapi, process-pool, http-error-contract]

# Dependency graph
requires:
  - phase: 02-cad-off-the-event-loop
    provides: "02-01's BuildPool, affinity routing, and the async model endpoint this
      plan adds a timeout, failure-mode mapping, and health fields on top of."
provides:
  - "A per-build timeout (SPUR_BUILD_TIMEOUT) that terminates the overrunning worker
    process, not just abandons the future, and replaces that hash slot's executor."
  - "Three distinct, documented HTTP answers for the three ways a build can fail:
    BuildError -> 422, BuildTimeout -> 503, BrokenProcessPool -> 503 -- each with its
    own detail[0].type and, for the 503s, a Retry-After header."
  - "/api/health reports pool state (worker count, remaining admission capacity,
    workers replaced since start) from parent-local counters only, nested under one
    `pool` key, with no await, lock or worker round-trip in the handler."
  - "docs/architecture/http-api.md brought current with the new topology: the retired
    kernel-lock-serialises-everything claim, the four detail[].type values, the health
    shape, and tests/test_pool.py's coverage."
affects: [02-04, 02-05]

# Actuals (#2632)
actuals:
  tokens: 8548      # chars/4 over b04acb1..HEAD, .planning excluded
  tasks: 4
  commits: 3
  plan_head_before: b04acb1

# Tech tracking
tech-stack:
  added: []   # stdlib only: asyncio.wait_for/TimeoutError, concurrent.futures.process.BrokenProcessPool
  patterns:
    - "Timeout -> terminate -> recreate: asyncio.wait_for around run_in_executor,
      catch asyncio.TimeoutError by its qualified name (not the 3.10-distinct
      builtin), terminate the live processes in the executor's private _processes
      mapping, then recreate_for() the hash slot rather than leaving it dead."
    - "Reuse, don't reinvent, the existing 503 + Retry-After + detail[].type shape for
      every new failure mode, so the response contract gains members instead of a
      second shape."
    - "Parent-local liveness: /api/health reads only attributes and a plain module
      counter it maintains itself (never a private semaphore/executor internal), and
      stays a synchronous def so there is nothing for FastAPI to await."

key-files:
  created: []
  modified:
    - src/spur/pool.py
    - src/spur/app.py
    - tests/test_pool.py
    - docs/architecture/http-api.md

key-decisions:
  - "Task 3 checkpoint (D-13, one-way): the shape of /api/health's pool fields. Human
    selected option B -- one nested `pool` object -- over flat top-level keys (option
    A) or a separate /api/pool endpoint (option C). Rationale: every later pool field
    lands inside `pool` without touching the published top level `status`/`version`
    the UI and the container healthcheck already read, converting what CONTEXT.md
    rated a one-way decision (the response is a published contract Phase 4's OpenAPI
    work inherits) into a reversible one. Confirmed src/spur/static/app.js does not
    read /api/health at all, so no UI client change was needed."
  - "Task 1 and Task 2's RED-phase tests were committed together with their GREEN
    implementation, not as separate failing commits: this repo's pre-commit hook runs
    the full `make verify` gate unconditionally, so a standalone commit with failing
    tests cannot pass it (same constraint 02-01-SUMMARY.md's key-decisions record, and
    --no-verify was out of bounds). RED was still performed and verified for real --
    pytest run against each task's tests before its implementation existed, failures
    confirmed for the intended reason (asserted via inspection of the failure, not
    just a nonzero exit) -- only the commit granularity differs from the generic TDD
    protocol's default. Task 4 (this continuation) followed the identical pattern; see
    'TDD Gate Compliance' below for its own RED evidence."
  - "Remaining admission capacity on /api/health comes from a plain module-level
    in-flight counter incremented/decremented inside _build_slot's own acquire/release
    pair, not threading.BoundedSemaphore._value -- 02-RESEARCH.md flags that as private,
    undocumented (Assumption A4), and the plan's Task 4 action explicitly rejects
    reading it from app.py."

patterns-established:
  - "A checkpoint:decision task whose answer changes a published response's shape
    (not just its content) gets its own dedicated task afterwards to implement the
    chosen shape, rather than folding the implementation into the decision task
    itself -- keeps the decision checkpoint free of code and the implementation task's
    acceptance criteria concrete and checkpoint-agnostic until the human has answered."

requirements-completed: [REQ-cad-off-event-loop]

# Coverage metadata (#1602)
coverage:
  - id: D1
    description: "A build that overruns SPUR_BUILD_TIMEOUT has its worker process
      terminated (not merely abandoned), the wedged hash slot's executor is replaced,
      and the next request routed to that slot succeeds against the fresh worker."
    requirement: "REQ-cad-off-event-loop"
    verification:
      - kind: unit
        ref: "tests/test_pool.py#test_a_wedged_build_is_terminated_and_its_worker_replaced"
        status: pass
    human_judgment: false
  - id: D2
    description: "A worker that dies unexpectedly (not via our own termination) surfaces
      as BrokenProcessPool from the awaited call, and its slot is replaced rather than
      left dead."
    requirement: "REQ-cad-off-event-loop"
    verification:
      - kind: unit
        ref: "tests/test_pool.py#test_a_dying_worker_surfaces_as_broken_pool_and_is_replaced"
        status: pass
    human_judgment: false
  - id: D3
    description: "BuildError still maps to 422 (build_error); BuildTimeout and
      BrokenProcessPool both map to 503 with Retry-After and their own, pairwise-
      distinct detail[0].type; the admission slot is released on every one of the
      three failure paths, so a repeated failure never leaks queue capacity."
    requirement: "REQ-cad-off-event-loop"
    verification:
      - kind: unit
        ref: "tests/test_pool.py#test_each_build_failure_mode_maps_to_its_own_status_and_type"
        status: pass
      - kind: unit
        ref: "tests/test_pool.py#test_the_four_failure_types_are_pairwise_distinct"
        status: pass
    human_judgment: false
  - id: D4
    description: "/api/health additionally reports build-worker count, remaining
      admission capacity, and workers-replaced-since-start, nested under one `pool`
      key (Task 3 checkpoint decision, option B); status/version are unaffected;
      capacity falls while a slot is held and returns to full afterwards; the
      workers_replaced count tracks BuildPool.replaced live."
    requirement: "REQ-cad-off-event-loop"
    verification:
      - kind: unit
        ref: "tests/test_pool.py#test_health_reports_pool_state"
        status: pass
      - kind: unit
        ref: "tests/test_pool.py#test_health_queue_available_falls_while_a_slot_is_held"
        status: pass
      - kind: unit
        ref: "tests/test_pool.py#test_health_workers_replaced_increases_after_a_forced_termination"
        status: pass
      - kind: unit
        ref: "tests/test_pool.py#test_health_handler_never_awaits_or_touches_pool_internals"
        status: pass
      - kind: manual_procedural
        ref: "make serve on port 8001; curl /api/health during three concurrent
          teeth=197-199 fine builds (3.2s-8.6s each) -- health answered in ~1-2ms each
          time and queue_available correctly read 1 (3 of 4 admission slots held)"
        status: pass
    human_judgment: false

duration: ~25min active work (Tasks 1-2: ~10min same-session on 2026-09-23 09:34-09:45;
  Task 3 checkpoint then paused for the human decision; Task 4, this continuation
  session: ~15min, 2026-09-23 08:40-08:55 UTC)
completed: 2026-09-23
status: complete
---

# Phase 2 Plan 3: Failure Modes and Liveness Summary

Every way a `/api/model.{stl,step}` build can fail now has its own status code and
`detail[0].type` (kernel rejection stays 422; a timeout or a dead worker are both 503
with `Retry-After`), a wedged build's worker process is actually killed and replaced
rather than abandoned, and `/api/health` reports live pool state from parent-local
counters alone, nested under a `pool` object chosen at this plan's checkpoint.

## Performance

- **Tasks:** 4 completed (2 `auto`+TDD, 1 `checkpoint:decision`, 1 `auto`+TDD)
- **Files modified:** 4 (`src/spur/pool.py`, `src/spur/app.py`, `tests/test_pool.py`,
  `docs/architecture/http-api.md`)
- **Commits:** 3 (Task 3 is a decision checkpoint with no code)

## Accomplishments

- `BuildPool.export` now enforces `SPUR_BUILD_TIMEOUT` (provisional default, Plan
  02-04 sets the measured value) via `asyncio.wait_for`, terminates the wedged
  worker process through the private `_processes` mapping on timeout, and replaces
  the hash slot's executor -- proven by a test that asserts the process is dead and
  `BuildPool.replaced` increased by exactly 1.
- A worker that dies on its own now surfaces as `BrokenProcessPool` and is likewise
  replaced, rather than leaving a permanently dead slot.
- The model endpoint maps three failure modes to three distinct client-actionable
  answers -- `BuildError` -> 422 `build_error` (unchanged), `BuildTimeout` -> 503
  `timeout`, `BrokenProcessPool` -> 503 `pool_broken` -- reusing the existing 503 +
  `Retry-After` + `detail[].type` shape rather than inventing a new one, with a test
  proving admission capacity is restored after each.
- Human decision (Task 3): `/api/health`'s pool fields nest under one `pool` object
  (option B), keeping `status`/`version` exactly where the UI and container
  healthcheck already read them.
- `/api/health` now reports `pool.workers`, `pool.queue_available` and
  `pool.workers_replaced` from a plain in-flight counter and `BuildPool` attributes
  only -- no `await`, no lock, no worker round-trip -- confirmed both by tests and by
  a live manual check: the endpoint answered in 1-2ms while three concurrent 3-8.6s
  builds held 3 of 4 admission slots.
- `docs/architecture/http-api.md` updated in the same change as the code: the
  kernel-lock-serialises-everything claim retired, the import-linter contract named,
  the new health shape, the two new `503` types, and `tests/test_pool.py`'s coverage.

## Task Commits

1. **Task 1: A timeout that stops the build, not just the waiting** - `4fb7037` (feat)
2. **Task 2: Three ways to fail, three answers a client can act on** - `34e267e` (feat)
3. **Task 3: Decision -- the shape of the pool fields on /api/health** - no commit
   (checkpoint:decision; human selected option B)
4. **Task 4: Pool state on /api/health, read from the parent and nothing else** -
   `520c71c` (feat)

**Plan metadata:** commit follows this summary.

_Note: TDD tasks (1, 2, 4) combine their RED and GREEN into a single `feat(02-03)`
commit each -- see "TDD Gate Compliance" below for why._

## Files Created/Modified

- `src/spur/pool.py` - `BuildPool.timeout`, timeout-and-replacement handling inside
  `_run_with_timeout` (Task 1; unchanged by this continuation)
- `src/spur/app.py` - the three exception-to-status mappings (Task 2, unchanged by
  this continuation); this continuation added `_in_flight_builds` (a plain module
  counter maintained inside `_build_slot`) and rewrote `health()` to return the
  `pool` object built from it plus `BuildPool.workers`/`.replaced`
- `tests/test_pool.py` - Task 1/2's timeout-terminate-replace, broken-pool-replace,
  and failure-mapping tests (unchanged by this continuation); this continuation added
  four tests for the health shape, the capacity-falls-while-held behavior, the
  workers_replaced-tracks-live-state behavior, and a structural guard that `health`
  stays a plain `def` (never `async def`)
- `docs/architecture/http-api.md` - Boundaries, Shape, Errors and Tests sections
  brought current with the process-pool topology, the two new `503` types, and the
  `pool` health shape

## Decisions Made

See `key-decisions` in frontmatter above.

## Deviations from Plan

None beyond the RED/GREEN commit-granularity accommodation already recorded under
"TDD Gate Compliance" and in `key-decisions` -- inherited from the same repo-wide
pre-commit-hook constraint 02-01-SUMMARY.md and 02-02's STATE.md decision entry
already document for this project. No Rule 1-4 auto-fixes or architectural questions
came up in Task 4.

## TDD Gate Compliance

This plan is `type: execute` with individual `tdd="true"` tasks, not a `type: tdd`
plan, so the strict RED/GREEN/REFACTOR commit-sequence gate in `tdd.md` does not apply
verbatim -- but the RED-before-GREEN discipline itself was followed for every `tdd="true"`
task, including this continuation's Task 4:

- **Task 1** (`4fb7037`) and **Task 2** (`34e267e`): RED performed and confirmed by the
  prior executor before implementation existed (per `02-CONTEXT.md`'s continuation
  state); GREEN and RED committed together in one `feat(02-03)` commit each, because
  this repo's pre-commit hook runs the full `make verify` gate unconditionally on
  every commit with no bypass configured -- a standalone RED commit with failing tests
  cannot pass it, and `--no-verify` is out of bounds per this session's own
  instructions (identical to the accommodation 02-01-SUMMARY.md records).
- **Task 4** (`520c71c`): RED confirmed this session -- the four new health tests were
  written first and run against the pre-Task-4 `health()`; three failed with
  `KeyError: 'pool'` (the target assertion, not a collection or fixture error) and the
  fourth (the `async def` structural guard) passed immediately since `health()` was
  already a plain `def` before this task. GREEN was then implemented (`_in_flight_builds`
  counter plus the rewritten `health()`), all four tests plus the full suite passed,
  and `make verify` was green before the single `feat(02-03)` commit that carries both
  the tests and the implementation, for the same pre-commit-hook reason as Tasks 1-2.
  No REFACTOR step was needed.

No RED/GREEN gate violations to report.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Plan 02-04 (the measured numbers) can now run `bench/` against a topology that
actually terminates a wedged build and reports pool state without touching a worker --
the qualitative property this plan's human-check proved by eye, and that 02-04 will
make precise. No blockers.

---
*Phase: 02-cad-off-the-event-loop*
*Completed: 2026-09-23*

## Self-Check: PASSED

- `src/spur/pool.py`, `src/spur/app.py`, `tests/test_pool.py`,
  `docs/architecture/http-api.md`, and this SUMMARY.md all confirmed present on disk.
- Commits `4fb7037`, `34e267e`, `520c71c` (task code) and `043b79d` (this SUMMARY) all
  confirmed present in `git log --oneline --all`.
