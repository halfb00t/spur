---
phase: 03-structured-logging-at-the-composition-boundary
plan: 01
subsystem: infra
tags: [logging, json-formatter, uvicorn, structlog-alternative-stdlib, caplog]

# Dependency graph
requires: []
provides:
  - "spur.records: configure(), the JSON Formatter/Handler, SPUR_LOG_LEVEL, and the two
    per-event helpers this plan needed (build_started, export_served) -- the kernel-free
    module 03-02 and 03-03 add build_failed/queue_refused/worker_replaced to."
  - "configure() wired at both composition points (cli.cmd_serve before uvicorn.run, and
    app.py's lifespan() startup), idempotent, so SPUR_WORKERS=1 installs one handler and
    SPUR_WORKERS>1 still gets every worker configured."
  - "A real /api/model.stl request emits build.started (on a fresh build) then
    export.served, carrying request/slug/params/fmt/quality/encoding/source/duration_ms,
    proven end to end by reading the formatted stderr line back through json.loads."
  - "The record format's edges pinned as tests, not left incidental: one-physical-line
    encoding, stable key order, integer-millisecond half-to-even rounding, the
    SPUR_LOG_LEVEL threshold (including its empty/nonsense fallback to INFO), and
    configure()'s double-call idempotency down to the line count."
affects: [03-02, 03-03]

# Actuals (#2632)
actuals:
  tokens: 9925      # chars/4 over the realized diff (782730d..HEAD, .planning excluded)
  tasks: 3
  commits: 4
  plan_head_before: 782730d918c712e2f4adca985804267f9e1c328e

# Tech tracking
tech-stack:
  added: []   # stdlib only: logging, json, datetime, uuid, time -- no new dependency
  patterns:
    - "Kernel-free logging module (records.py), mirroring build_errors.py's shape: a
      small module both cli.py and app.py import without either reaching cadquery/OCP
      or fastapi/starlette through it."
    - "Idempotent configure() guarded by isinstance(handler, _JsonHandler) on the root
      logger's own handler list, not a module-level flag -- state lives on the object
      it describes, so a test fixture can tear it down without reaching into privates."
    - "Per-event helper functions (build_started, export_served) as the only call sites
      that ever touch the stdlib logger directly -- app.py/pool.py never assemble an
      extra= dict by hand, and ruff's G004/LOG015 enforce this by construction."
    - "caplog branch tests for per-request events, capsys + a real installed handler for
      the one true end-to-end proof and the formatter's own edges -- two different test
      techniques for two different claims (event fired vs. bytes-on-the-wire correct)."

key-files:
  created:
    - src/spur/records.py
    - tests/conftest.py
    - tests/test_records.py
    - docs/tech_debt/active/2026-09-24-shared-solid-cache-corrupts-later-boundingbox.md
  modified:
    - src/spur/cli.py
    - src/spur/app.py
    - tests/test_api.py
    - docs/tech_debt/INDEX.md

key-decisions:
  - "The formatter falls back to record.getMessage() for the envelope's `event` field
    when a record carries no `event` extra (uvicorn's own uvicorn.error/uvicorn.access
    records, which flow through the same root handler per D-02) -- required so the
    shared formatter never raises on a record it didn't originate, confirmed live: a
    real `spur serve` run's stderr is 100% valid JSON via `jq`, uvicorn's own lines
    included."
  - "duration_s/source are initialised to 0.0/\"cache\" before the cache lookup, not as
    a branch inside it -- a plain cache hit skips the build slot entirely, so its
    duration is zero and its source is \"cache\" by construction, matching the plan's
    own reasoning for avoiding a special-cased branch."
  - "export_served() is called from exactly one call site in model(), immediately before
    the response headers are built, reached by all three source paths (cache, compressed,
    built) -- not duplicated per branch."

requirements-completed: [REQ-structured-logging]

coverage:
  - id: D1
    description: "records.py's configure() installs one stderr JSON handler, called
      idempotently from both cli.cmd_serve and app.py's lifespan()"
    requirement: REQ-structured-logging
    verification:
      - kind: unit
        ref: "tests/test_records.py#test_configure_called_twice_installs_exactly_one_handler"
        status: pass
      - kind: unit
        ref: "tests/test_records.py#test_configure_twice_still_emits_exactly_one_line_per_record"
        status: pass
      - kind: integration
        ref: "manual: spur serve, real process, stderr piped through jq -- all lines valid JSON"
        status: pass
    human_judgment: false
  - id: D2
    description: "A real /api/model.stl request emits export.served with the full
      per-request field set, readable back through json.loads"
    requirement: REQ-structured-logging
    verification:
      - kind: e2e
        ref: "tests/test_records.py#test_a_model_request_emits_one_export_served_line_that_json_loads_round_trips"
        status: pass
    human_judgment: false
  - id: D3
    description: "build.started precedes a fresh build; export.served's source
      distinguishes built/cache/compressed, each proven by a test driving the real path"
    requirement: REQ-structured-logging
    verification:
      - kind: integration
        ref: "tests/test_api.py#test_a_fresh_build_emits_build_started_then_export_served_with_source_built"
        status: pass
      - kind: integration
        ref: "tests/test_api.py#test_a_repeat_download_is_served_from_cache_with_zero_duration_and_no_build_started"
        status: pass
      - kind: integration
        ref: "tests/test_api.py#test_a_gzip_request_after_an_identity_download_emits_source_compressed"
        status: pass
      - kind: integration
        ref: "tests/test_api.py#test_an_all_default_gear_logs_params_as_an_empty_object_not_omitted"
        status: pass
      - kind: integration
        ref: "tests/test_api.py#test_two_requests_for_one_gear_get_two_different_request_ids"
        status: pass
    human_judgment: false
  - id: D4
    description: "The record format's edges are guarantees: one physical line under any
      encoding, stable key order, integer-millisecond half-to-even rounding,
      SPUR_LOG_LEVEL's threshold and nonsense/empty fallback, and calc.py stays log-free"
    requirement: REQ-structured-logging
    verification:
      - kind: unit
        ref: "tests/test_records.py#test_the_formatter_round_trips_every_application_field_through_json_loads"
        status: pass
      - kind: unit
        ref: "tests/test_records.py#test_a_field_with_a_newline_and_non_ascii_stays_one_physical_line"
        status: pass
      - kind: unit
        ref: "tests/test_records.py#test_two_records_of_the_same_event_serialize_identical_key_order"
        status: pass
      - kind: unit
        ref: "tests/test_records.py#test_ms_is_an_integer_with_half_to_even_rounding"
        status: pass
      - kind: unit
        ref: "tests/test_records.py#test_parse_level_falls_back_to_info_on_nonsense_and_empty"
        status: pass
      - kind: unit
        ref: "tests/test_records.py#test_spur_log_level_moves_the_threshold"
        status: pass
      - kind: unit
        ref: "tests/test_records.py#test_spur_log_level_unset_defaults_to_info"
        status: pass
      - kind: unit
        ref: "tests/test_records.py#test_calc_module_stays_log_free"
        status: pass
    human_judgment: false

# Metrics
duration: 25min
completed: 2026-09-24
status: complete
---

# Phase 3 Plan 1: One Request, One JSON Line -- Records.py Wired at Both Composition Points Summary

**Stdlib `logging` + a project-owned JSON `Formatter`, configured idempotently at
`cli.cmd_serve` and `app.py`'s `lifespan()`, emits `build.started`/`export.served` for
every `/api/model.stl` request -- proven end to end by reading a real formatted stderr
line back through `json.loads`, and confirmed live against a real `spur serve` process
piped through `jq`.**

## Performance

- **Duration:** ~25 min
- **Started:** 2026-09-24T09:00Z (approx, first task commit)
- **Completed:** 2026-09-24T09:27Z
- **Tasks:** 3 (plus one small in-scope test-completeness fix)
- **Files modified:** 8 (4 created, 4 modified)

## Accomplishments
- `src/spur/records.py`: the kernel-free module owning this phase's logging vocabulary --
  `configure()`, `_JsonFormatter`, `_JsonHandler`, `_parse_level`, `_gear_fields`, `_ms`,
  `_emit`, `build_started()`, `export_served()`.
- `configure()` called at both composition points (`cli.cmd_serve` before
  `uvicorn.run(..., log_config=None)`, and `app.py`'s `lifespan()` startup) so the
  default `SPUR_WORKERS=1` case installs exactly one handler and `SPUR_WORKERS>1` still
  gets every spawned worker configured (03-RESEARCH.md's falsified-assumption finding).
- `app.model()` mints a per-request correlation id, tracks `source`/`duration_s` through
  the cache/compressed/built branches, and emits one `export_served(...)` call reached by
  all three paths, plus `build_started(...)` immediately before a fresh build's backend
  call.
- The record format's edges (one-physical-line encoding, stable key order, integer
  milliseconds with half-to-even rounding, the `SPUR_LOG_LEVEL` knob, idempotency down to
  the line count) and `calc.py`'s log-free boundary are pinned as tests, not left
  incidental.
- Live-verified against a real `spur serve` process: every stderr line (uvicorn's own
  records included) parses as JSON via `jq`; `spur info`/`spur export` remain unaffected
  (no configured logger, unchanged stderr prose).

## Task Commits

Each task was committed atomically:

1. **Task 1: One request, one JSON line -- records.py wired at both composition points** -
   `8b904df` (feat)
2. **Task 2: The per-request vocabulary -- identity, correlation, the three sources, and
   build.started** - `bc124f0` (feat, includes a Rule 3 test-isolation deviation)
3. **Task 3: The knob and the line format become guarantees, not incidents** - `6fad6d2`
   (test)
4. **Follow-up: explicit non-empty caplog assertion** - `047c123` (test) -- a same-scope
   completeness fix to Task 2's branch tests, made while re-checking the plan's own
   acceptance criteria (see Deviations).

## Files Created/Modified
- `src/spur/records.py` - The logging module: formatter, handler, level knob, per-event
  helpers.
- `src/spur/cli.py` - `cmd_serve` calls `configure()` and passes `log_config=None`.
- `src/spur/app.py` - `lifespan()`'s second `configure()` call; `model()`'s
  request id/duration/source tracking and the two emission call sites.
- `tests/conftest.py` - Autouse root-logger reset; autouse solid-cache reset (see
  Deviations).
- `tests/test_records.py` - The traced end-to-end proof, the formatter's edges, the level
  knob, and the negative `calc.py` check.
- `tests/test_api.py` - Five new `caplog`-based branch tests for the per-request
  vocabulary.
- `docs/tech_debt/active/2026-09-24-shared-solid-cache-corrupts-later-boundingbox.md` /
  `docs/tech_debt/INDEX.md` - A `must`-severity debt item filed for a pre-existing
  `model.py` defect this plan's tests exposed (see Deviations).

## Decisions Made
- The formatter falls back to `record.getMessage()` for `event` when a record carries no
  `event` extra (uvicorn's own records) -- required so the shared root handler's
  formatter never raises on a record it did not originate.
- `duration_s`/`source` are initialised to `0.0`/`"cache"` before the cache lookup, so a
  plain cache hit has a defined value for both without a special-cased branch.
- `export_served()` has exactly one call site in `model()`, reached by all three source
  paths, immediately before the response headers are built.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] A pre-existing `model.py` cache-sharing defect blocked
`make verify` once the plan's required all-default-gear test was added**
- **Found during:** Task 2 (the `params == {}` branch test)
- **Issue:** `model.py`'s `_build_cached` is a process-global `lru_cache` returning the
  *same* `cq.Solid` object for identical `GearParams`. `Shape.exportStl()` has a side
  effect on that shared object (attaching a coarser mesh) that skews a *later*
  `.BoundingBox()` call on it -- even from a wholly unrelated test. This plan's new
  all-default-gear test (`tests/test_api.py`) and `tests/test_model.py`'s pre-existing
  `kw={}` case both build the literal same `GearParams()`; whichever ran second silently
  measured the first one's leftover mesh (`bb.zlen` read `7.5877` instead of `7.5`).
  Reproduced and isolated this session with a series of throwaway scripts (see the
  filed debt item for the exact numbers); confirmed the actual exported STL *bytes* are
  unaffected (a fresh build and a preview-then-fine build are byte-identical) and that
  no `src/spur/*.py` production code calls `.BoundingBox()` today, so there is no live
  shipped impact -- the defect is latent, not shipping.
- **Fix:** Added an autouse `tests/conftest.py` fixture (`_reset_solid_cache`) that
  clears `_build_cached` before every test, matching the unique-parameter-per-test
  discipline the rest of the suite already follows informally for the app-level byte
  cache. Filed
  `docs/tech_debt/active/2026-09-24-shared-solid-cache-corrupts-later-boundingbox.md`
  (severity `must`, trigger: a future production consumer of `.BoundingBox()`, or a test
  outside this suite's autouse protection) for the underlying `model.py` behavior, since
  the fix here is test-side isolation, not a change to the shared-cache design itself.
- **Files modified:** `tests/conftest.py`, `docs/tech_debt/active/2026-09-24-shared-solid-cache-corrupts-later-boundingbox.md`, `docs/tech_debt/INDEX.md`
- **Verification:** Full suite (92 tests) green before and after in isolation; reproduced
  the failure deterministically with just the two colliding tests, confirmed the fix
  resolves it, confirmed `make verify` passes.
- **Committed in:** `bc124f0` (Task 2 commit)

**2. [Rule 1 - Completeness] One branch test was missing the explicit non-empty
`caplog.records` assertion the plan's acceptance criteria require of every INFO-level
branch test**
- **Found during:** final plan-level self-review against the plan's acceptance criteria
- **Issue:** `test_two_requests_for_one_gear_get_two_different_request_ids` asserted
  `len(served) == 2` (which is strictly stronger than non-emptiness) but had no separate
  literal `assert caplog.records` line, unlike its four siblings.
- **Fix:** Added `assert caplog.records` immediately after the two requests, matching
  every other branch test's Pitfall-1 guard.
- **Files modified:** `tests/test_api.py`
- **Verification:** `make test PYTEST_ARGS="tests/test_api.py -q"` (24 passed);
  `make verify` (92 passed).
- **Committed in:** `047c123`

---

**Total deviations:** 2 auto-fixed (1 blocking, 1 completeness).
**Impact on plan:** Both were necessary to satisfy this plan's own acceptance criteria
and to keep `make verify` green; neither touched anything outside logging/tests except
the one debt file and its INDEX row, which is exactly what CLAUDE.md's tech-debt process
asks for when a fix is test-side rather than a change to the underlying production
behavior.

## Issues Encountered
None beyond the deviation documented above.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- `records.py`'s `build_started`/`export_served` are in place; Plan 03-02 adds
  `build_failed`, `queue_refused`, and `worker_replaced` on top of the same module and
  wiring pattern.
- `docs/tech_debt/active/2026-09-24-shared-solid-cache-corrupts-later-boundingbox.md` is
  a new, unrelated `must` item for future awareness -- not a blocker for 03-02/03-03.
- No blockers for the next plan.

---
*Phase: 03-structured-logging-at-the-composition-boundary*
*Completed: 2026-09-24*

## Self-Check: PASSED
