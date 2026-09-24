---
phase: 04-typed-derived-dimensions-contract
plan: 02
subsystem: api-contract
tags: [pydantic, fastapi, openapi, mypy, paramspec]

# Dependency graph
requires:
  - phase: 04-typed-derived-dimensions-contract
    provides: "Plan 04-01's DerivedDimensions frozen-model pattern, matched here for
      HealthReport/PoolState (Field(description=...), ConfigDict(frozen=True), no
      defaults)"
provides:
  - "`spur.app.HealthReport`/`PoolState`, frozen pydantic response models; `health() ->
    HealthReport` with `pool` present-and-null (not absent) under a lifespan-free client"
  - "`/openapi.json`'s `#/components/schemas/HealthReport` and `#/components/schemas/PoolState`"
  - "`schema() -> JsonSchemaValue`, pydantic's own JSON-Schema-document alias"
  - "Every remaining explicit `Any` removed from `src/`, `docker/` and the tests: `params._f`
    generic over `TypeVar`, `app._BlobCache` keyed on `Hashable`, `pool._run_with_timeout`
    typed with a `ParamSpec` forwarded through `functools.partial`, `cli._add_gear_args`
    with explicit keyword calls, `docker/smoke.py` typed with starlette's `Message`"
  - "A fix to `app.py`'s `lifespan` so `app.state.pool` is deleted, not just shut down, on
    teardown -- the module-level FastAPI singleton no longer leaks a dead pool object
    across test files that share one pytest session"
affects: [04-03-any-explicit-ratchet-retired]

# Actuals (#2632)
actuals:
  tokens: 5421
  tasks: 3
  commits: 3

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "A published-response model (HealthReport) built entirely inside its route
      function from parent-local, O(1) reads, with the pool sub-object constructed
      only in the branch where a pool exists -- same never-partially-built discipline
      as DerivedDimensions"
    - "A ParamSpec + functools.partial pair at a spawn-process boundary: *args alone
      type-checks against a ParamSpec-typed Callable but silently drops any keyword
      argument at the executor call; a partial closes over both before crossing"

key-files:
  created: []
  modified:
    - src/spur/app.py
    - tests/test_api.py
    - docs/architecture/http-api.md
    - src/spur/params.py
    - src/spur/pool.py
    - src/spur/cli.py
    - docker/smoke.py
    - tests/test_calc.py
    - tests/test_model.py

key-decisions:
  - "health()'s docstring paragraph about pool absence rewritten to describe null,
    following D-06's present-and-null policy -- matching DerivedDimensions' own
    null-over-absent rule rather than introducing a second serialisation convention."
  - "pool._run_with_timeout forwards through functools.partial(func, *args, **kwargs)
    rather than a bare *args, **kwargs pass-through to run_in_executor, because
    run_in_executor takes positional arguments only -- PEP 612 requires *args: P.args
    and **kwargs: P.kwargs declared together, and a signature that only forwarded
    *args would type-check while silently discarding any keyword argument the new
    signature had just accepted (flagged assumption 2, verified during planning)."
  - "cli._add_gear_args narrows field.annotation with a plain assert (not an if-guard)
    before passing it to argparse's type= -- pydantic guarantees every declared field
    carries an annotation, so the assert exists only to satisfy mypy, never to change
    control flow."
  - "app.py's lifespan now dels app.state.pool in its finally block, in addition to
    shutting it down -- a bug this plan's own D-06 assertion exposed (see Deviations)."

patterns-established:
  - "A frozen response model that nests only in the branch where its dependency
    exists (PoolState inside HealthReport), rather than a model with an internal
    optional sub-object built unconditionally."

requirements-completed: [REQ-typed-derived-dimensions]

# Coverage metadata (#1602)
coverage:
  - id: D1
    description: "/api/health returns a frozen HealthReport (status: Literal[\"ok\"],
      version: str, pool: PoolState | None); PoolState holds workers, queue_available,
      workers_replaced. Under a bare TestClient with no lifespan, pool is present and
      null, not absent; with the lifespan running it carries the same three values as
      before (D-05, D-06)."
    requirement: REQ-typed-derived-dimensions
    verification:
      - kind: unit
        ref: "tests/test_api.py::test_health"
        status: pass
      - kind: integration
        ref: "tests/test_pool.py::test_health_reports_pool_state"
        status: pass
      - kind: integration
        ref: "tests/test_pool.py::test_health_queue_available_falls_while_a_slot_is_held"
        status: pass
      - kind: integration
        ref: "tests/test_pool.py::test_health_workers_replaced_increases_after_a_forced_termination"
        status: pass
      - kind: unit
        ref: "tests/test_pool.py::test_health_handler_never_awaits_or_touches_pool_internals"
        status: pass
    human_judgment: false
  - id: D2
    description: "/openapi.json's /api/health 200 response $refs HealthReport; its
      required list is exactly status/version/pool, and PoolState's required list is
      exactly its three fields (D-11, health half)."
    requirement: REQ-typed-derived-dimensions
    verification:
      - kind: integration
        ref: "tests/test_api.py::test_openapi_documents_the_typed_contracts"
        status: pass
    human_judgment: false
  - id: D3
    description: "/api/schema is annotated JsonSchemaValue (pydantic's own alias) and
      serves byte-identical JSON to before this task (D-07)."
    verification:
      - kind: manual_procedural
        ref: "json.dumps(TestClient(app).get('/api/schema').json(), sort_keys=True),
          captured before and after src/spur/app.py's edit; diff empty (see
          'Before/After Diffs' below)"
        status: pass
    human_judgment: false
  - id: D4
    description: "Every remaining explicit Any in src/ and docker/ is gone: params._f
      generic over TypeVar T with extra: JsonDict; app._BlobCache keyed on Hashable;
      pool._run_with_timeout typed with a ParamSpec, forwarding through
      functools.partial; cli._add_gear_args uses explicit keyword add_argument calls
      per field kind; docker/smoke.py's receive/send typed with starlette's own
      Message alias, no cast (D-08)."
    requirement: REQ-typed-derived-dimensions
    verification:
      - kind: unit
        ref: "make test PYTEST_ARGS=\"tests/test_pool.py tests/test_cli.py tests/test_api.py tests/test_calc.py -q\" (74 passed)"
        status: pass
      - kind: integration
        ref: ".venv/bin/python docker/smoke.py (prints the 'all live' line)"
        status: pass
      - kind: manual_procedural
        ref: ".venv/bin/spur info --help / .venv/bin/spur export --help, captured
          before and after src/spur/cli.py's edit; both diffs empty"
        status: pass
    human_judgment: false
  - id: D5
    description: "Every remaining explicit Any in the tests is gone: tests/test_calc.py
      and tests/test_model.py's kw: dict[str, Any] parametrizations are dict[str,
      object] constructed via GearParams.model_validate(); tests/test_api.py's _field
      returns object, with duration_ms narrowed by isinstance before the > 0 compare
      (D-08)."
    requirement: REQ-typed-derived-dimensions
    verification:
      - kind: unit
        ref: "make test PYTEST_ARGS=\"tests/test_calc.py tests/test_model.py tests/test_api.py -q\" (66 passed)"
        status: pass
    human_judgment: false
  - id: D6
    description: "With disallow_any_explicit still off in pyproject.toml, a hand-run
      mypy --disallow-any-explicit src tests docker bench reports exactly Found 6
      errors in 3 files (checked 23 source files), and each of the six lines is a
      pydantic model's class line: GearParams, DerivedDimensions, InfoQuery,
      ModelQuery, PoolState, HealthReport -- the plugin's own generated-initialiser
      Any, which Plan 04-03 removes by turning on init_typed."
    requirement: REQ-typed-derived-dimensions
    verification:
      - kind: manual_procedural
        ref: ".venv/bin/mypy --disallow-any-explicit src tests docker bench (see
          'The Intermediate Proof' below for the full transcript)"
        status: pass
    human_judgment: false
  - id: D7
    description: "http-api.md's /api/health row names HealthReport, and the file no
      longer describes this contract as inherited by 'Phase 4's typed OpenAPI work'
      (D-15)."
    verification:
      - kind: other
        ref: "grep -n \"typed OpenAPI work\" docs/architecture/http-api.md (expected:
          no output, confirmed)"
        status: pass
    human_judgment: false

duration: 16min
completed: 2026-09-24
status: complete
---

# Phase 4 Plan 2: Typed Health/Pool Contract and the Any-Explicit Cleanup Summary

`/api/health` now returns a frozen `HealthReport` (`status`, `version`, `pool:
PoolState | None`) with `pool` present-and-`null` rather than absent when the app runs
without its lifespan, closing the second published-response gap Phase 2 D-13 deferred
to this phase; `/api/schema` is annotated with pydantic's own `JsonSchemaValue` alias;
and every other explicit `Any` the baseline named in `src/`, `docker/` and the tests is
gone, leaving exactly the six pydantic-plugin class-line errors Plan 04-03 retires next.

## Performance

- **Duration:** 16 min
- **Started:** 2026-09-24T14:17:14Z
- **Completed:** 2026-09-24T14:33:39Z
- **Tasks:** 3 completed
- **Files modified:** 9 (0 created)

## Accomplishments
- `HealthReport`/`PoolState`, frozen pydantic models declared above `@app.get("/api/health")`,
  matching `DerivedDimensions`' convention (`ConfigDict(frozen=True)`, one-line
  `Field(description=...)` per field, no field carrying a default) (D-05).
- `health()` annotated `-> HealthReport`; `pool` is `null`, not absent, under a bare
  `TestClient(app)` with no lifespan, and carries the same three values as before with
  the lifespan running (D-06). `health()` stays a plain synchronous `def`, still proven
  by `tests/test_pool.py::test_health_handler_never_awaits_or_touches_pool_internals`.
- `schema()` annotated `-> JsonSchemaValue` (`pydantic.json_schema.JsonSchemaValue`);
  `/api/schema`'s served document is byte-identical before and after (D-07).
- `test_openapi_documents_the_typed_contracts` extended with the health half of D-11:
  the `$ref`, and both `HealthReport`/`PoolState` `required` sets.
- `params._f()` generic over `TypeVar T`, `extra` typed `JsonDict` (from
  `pydantic.config`, not `dict[str, object]` -- pydantic's `json_schema_extra` is
  invariant in its value type); `teeth: int = _f(19, ...)` still resolves to `int`.
- `app._BlobCache` keyed on `Hashable`, not `Any`, in `_items`, `get()` and `put()`.
- `pool._run_with_timeout` takes `func: Callable[P, bytes], *args: P.args, **kwargs:
  P.kwargs` (a `ParamSpec`), forwarding both through `functools.partial` to
  `run_in_executor` -- a bare `*args` forward would type-check while silently dropping
  any keyword argument the new signature just accepted (PEP 612).
- `cli._add_gear_args` replaced its heterogeneous `kw` dict with two explicit
  `add_argument` call shapes (`Literal` fields vs. every other field);
  `field.annotation` narrowed with an `assert ... is not None` before use as `type=`.
  `spur info --help`/`spur export --help` output is byte-identical before and after.
- `docker/smoke.py`'s `receive`/`send` typed with starlette's own `Message` alias
  (the type `app.__call__` itself declares); no `cast(` needed; `.venv/bin/python
  docker/smoke.py` still prints its "all live" line.
- `tests/test_calc.py`/`tests/test_model.py`'s `kw: dict[str, Any]` parametrizations
  became `dict[str, object]`, constructed through `GearParams.model_validate(...)`.
  `tests/test_api.py`'s `_field()` returns `object`; the one arithmetic use
  (`duration_ms > 0`) is now `isinstance(duration_ms, int)` plus a separate `> 0`
  assert (ruff PT018).
- A hand-run `mypy --disallow-any-explicit src tests docker bench` reports exactly
  `Found 6 errors in 3 files (checked 23 source files)`, each on a pydantic model's
  `class` line -- the plugin's own generated-initialiser `Any`, which Plan 04-03's
  `init_typed = true` removes.

## Task Commits

Each task was committed atomically:

1. **Task 1: The other published contract -- `/api/health` as `HealthReport`,
   `/api/schema` as `JsonSchemaValue` (D-05, D-06, D-07, D-11)** -- `64b53ab` (feat)
2. **Task 2: The remaining explicit `Any` in `src/` and `docker/`** -- `8d662f1` (feat)
3. **Task 3: The remaining explicit `Any` in the tests, and the proof only the
   class-line errors remain** -- `6064c4f` (test)

**Plan metadata:** committed alongside this file (see below).

## Files Created/Modified
- `src/spur/app.py` -- `HealthReport`/`PoolState` models; `health() -> HealthReport`,
  `schema() -> JsonSchemaValue`; `_BlobCache` keyed on `Hashable`; `lifespan`'s
  `finally` block now `del`s `app.state.pool` in addition to shutting it down
- `tests/test_api.py` -- `test_health` asserts `pool` present-and-`None`;
  `test_openapi_documents_the_typed_contracts` extended with the health half;
  `_field()` returns `object`; `duration_ms` narrowed with `isinstance` before `> 0`
- `docs/architecture/http-api.md` -- `/api/health` row names `HealthReport`; the D-13
  paragraph states the present-tense `/openapi.json` contract instead of deferring to
  "Phase 4's typed OpenAPI work"
- `src/spur/params.py` -- `_f()` generic over `TypeVar T`, `extra: JsonDict`
- `src/spur/pool.py` -- `_run_with_timeout` typed with `ParamSpec P`, forwards through
  `functools.partial`
- `src/spur/cli.py` -- `_add_gear_args` uses explicit keyword `add_argument` calls per
  field kind, with an `assert`-narrowed `field.annotation`
- `docker/smoke.py` -- `receive`/`send` typed with `starlette.types.Message`
- `tests/test_calc.py` -- two `kw: dict[str, Any]` parametrizations moved to
  `dict[str, object]` + `GearParams.model_validate(...)`
- `tests/test_model.py` -- `test_builds_one_valid_solid`'s `kw` moved the same way

## Decisions Made

See `key-decisions` in the frontmatter. The most consequential: `pool._run_with_timeout`
forwards through `functools.partial`, not a bare `*args`/`**kwargs` pass-through to
`run_in_executor`, because the latter accepts positional arguments only -- a signature
that only forwarded `*args` would type-check while silently discarding any keyword
argument the new `ParamSpec` had just promised to accept.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `app.state.pool` leaked a shut-down pool object across test files
in one pytest session, defeating the bare client's absent-vs-set distinction**
- **Found during:** Task 2's own `<verify>` command
  (`make test PYTEST_ARGS="tests/test_pool.py tests/test_cli.py tests/test_api.py
  tests/test_calc.py -q"`), run in the file order the plan specifies
- **Issue:** `app` is one module-level `FastAPI` singleton, shared by every test file
  in a pytest session. `lifespan`'s `finally` block called `app.state.pool.shutdown()`
  but never cleared the attribute itself. When `tests/test_pool.py` (which runs the
  real lifespan inside `with TestClient(app):` blocks) executed before
  `tests/test_api.py` in the same session, its shut-down `BuildPool` object lingered
  on `app.state.pool` for `tests/test_api.py`'s module-level, lifespan-free `client`
  to see. Task 1's new `test_health` assertion (`body["pool"] is None`) is what
  surfaced this: it had always been an implicit assumption in
  `tests/test_api.py`'s own `_inline_build_backend` fixture docstring ("the module-level
  `client = TestClient(app)` above never runs the app's lifespan ... `app.state.pool`
  never exists for these tests") -- an assumption the code never actually enforced.
  `make verify`'s own default pytest invocation happens to run `test_api.py` before
  `test_pool.py` alphabetically, so this was invisible there; the plan's own literal
  Task 2 `<verify>` command order (`test_pool.py` first) exposed it directly.
- **Fix:** `lifespan`'s `finally` block now runs `del app.state.pool` after
  `app.state.pool.shutdown()`, so `getattr(app.state, "pool", None)` correctly returns
  `None`/absent again once a lifespan has torn down, regardless of which test file ran
  it first. Production behaviour is unchanged: a real deployment runs one lifespan for
  the life of the process and never reaches the `finally` block during normal operation.
- **Files modified:** `src/spur/app.py`
- **Verification:** `.venv/bin/python -m pytest tests/test_pool.py tests/test_cli.py
  tests/test_api.py tests/test_calc.py -q` -- 74 passed (was 1 failed, 73 passed before
  the fix); the full 103-test suite and `make verify` both still pass regardless of
  file order.
- **Committed in:** `8d662f1` (part of Task 2's commit, since Task 2's own `<verify>`
  step required it before proceeding)

---

**Total deviations:** 1 auto-fixed (Rule 1).
**Impact on plan:** None on scope -- a pre-existing test-isolation bug this plan's own
D-06 requirement was the first thing precise enough to expose. Not filed as tech debt:
fully resolved in the same commit that surfaced it, and the fix is a two-line addition
to code this plan was already editing for Task 1.

## Issues Encountered

None beyond the deviation above.

## User Setup Required

None -- no external service configuration required.

## Before/After Diffs

**`/api/schema` (Task 1, Step 4):** captured with
`json.dumps(TestClient(app).get('/api/schema').json(), sort_keys=True)`, before Task 1's
edits and again after -- `diff` empty (3555 bytes either side).

**`spur info --help` / `spur export --help` (Task 2):** captured before and after
`cli.py`'s edit -- both `diff`s empty.

## The Intermediate Proof (Task 3)

`.venv/bin/mypy --disallow-any-explicit src tests docker bench`, with
`disallow_any_explicit` still `false` in `pyproject.toml`'s `[tool.mypy]`:

```
src/spur/calc.py:165: error: Explicit "Any" is not allowed  [explicit-any]
src/spur/params.py:28: error: Explicit "Any" is not allowed  [explicit-any]
src/spur/app.py:211: error: Explicit "Any" is not allowed  [explicit-any]
src/spur/app.py:216: error: Explicit "Any" is not allowed  [explicit-any]
src/spur/app.py:281: error: Explicit "Any" is not allowed  [explicit-any]
src/spur/app.py:294: error: Explicit "Any" is not allowed  [explicit-any]
Found 6 errors in 3 files (checked 23 source files)
```

Each line, confirmed by direct inspection:

| File:Line | Class |
|---|---|
| `calc.py:165` | `class DerivedDimensions(BaseModel):` |
| `params.py:28` | `class GearParams(BaseModel):` |
| `app.py:211` | `class InfoQuery(GearParams):` |
| `app.py:216` | `class ModelQuery(GearParams):` |
| `app.py:281` | `class PoolState(BaseModel):` |
| `app.py:294` | `class HealthReport(BaseModel):` |

All six are pydantic model `class` lines -- the plugin's own generated-initialiser
`Any`, exactly as flagged_assumption/D-08 predicted. Plan 04-03 removes these six by
turning on `init_typed` and `warn_untyped_fields` in `pyproject.toml`'s pydantic plugin
config, then flips `disallow_any_explicit = true` for real.

## Next Phase Readiness

Plan 04-03 (turn `disallow_any_explicit` on for real, retire L14's ratchet, range-check
`spur info --mate-teeth`) depends on this plan's proof that only the six class-line
errors remain -- confirmed above, transcript included. `REQ-typed-derived-dimensions`
is still not complete: it also requires `disallow_any_explicit` on and L14's ratchet
retired, both Plan 04-03's scope. No blockers.

---
*Phase: 04-typed-derived-dimensions-contract*
*Completed: 2026-09-24*

## Self-Check: PASSED

All 9 created/modified files found on disk; all 3 task commits (`64b53ab`, `8d662f1`,
`6064c4f`) found in `git log --oneline --all`.
