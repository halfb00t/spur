# Phase 3: Structured Logging at the Composition Boundary - Context

**Gathered:** 2026-09-24
**Status:** Ready for planning

<domain>
## Phase Boundary

The serving process leaves structured evidence for the decision branches that already
exist. A JSON-lines logger is configured once, at the composition boundary, and the
following records are emitted and proven by tests: `build.started`, `build.failed` (with
the exception class), `export.served` (from cache vs built), `queue.refused`, plus
`worker.replaced` for the pool-recovery branch Phase 2 added after the debt file was
written. `calc.py` stays log-free. `docs/tech_debt/active/2026-09-21-no-structured-logging.md`
ends the phase `Status: resolved`, `git mv`'d, INDEX row moved, in the same commit as the
fix. `make verify` passes.

Requirement: REQ-structured-logging.

Not in this phase: metrics, tracing, log shipping, request IDs in HTTP responses or headers,
worker-side logging, any change to the `warnings` contract, the typed `DerivedDimensions`
model (Phase 4), CI observation (Phase 5).

</domain>

<decisions>
## Implementation Decisions

### Format and library
- **D-01:** stdlib `logging` with a project-owned JSON `Formatter` — one JSON object per
  line, built from the record's attributes plus `extra`. No new dependency: L12's pinned
  closure and `docker/refresh-requirements.sh` are untouched, matching Phase 2 D-03's
  stdlib-only reasoning. ruff's `LOG`/`G` rules (already on) police the call sites.
  `structlog` and logfmt were rejected — a new pinned package, and a convention with no
  parser, respectively.
- **D-02:** uvicorn's own records (`uvicorn`, `uvicorn.error`, `uvicorn.access`) go
  through the same root handler, so stdout/stderr carry one format. `cmd_serve` passes
  `log_config=None` to `uvicorn.run` so uvicorn does not install its own dictConfig on
  top. **ASSUMPTION to verify in research:** `log_config=None` leaves root logging alone
  and uvicorn's loggers propagate to root on the installed version. The access log stays
  on — it is the only per-request trace `/api/info`, `/api/schema`, `/api/health` and
  422 validation refusals have.
- **D-03:** JSON always. No `SPUR_LOG_FORMAT` knob, no TTY detection: one formatter, one
  code path, one thing the test proves. Reading locally is `make serve 2>&1 | jq`.
- **D-04:** One handler, on **stderr**. Matches the convention `cli.py` already sets
  (stdout is product output — `spur info` prints JSON there; stderr is diagnostics —
  `wrote ...`, `warning: ...`). uvicorn's default access→stdout / rest→stderr split
  collapses into it. `docker logs` captures both streams, so nothing is lost.

### Configuration point and emitting process
- **D-05:** The root logger is configured in `cli.cmd_serve`, before `uvicorn.run` — the
  literal composition root: every production start is `spur serve` (Dockerfile
  `CMD ["spur", "serve"]`, `make serve`). Not covered by design: `docker/smoke.py`
  (asserts status codes only), a bare `uvicorn spur.app:app`, `TestClient` — they get
  stdlib's `lastResort` (stderr, WARNING+), a degraded state, not a broken one.
  **ASSUMPTION to verify in research:** with `SPUR_WORKERS>1` uvicorn's child processes
  inherit the parent's root configuration (spawn vs fork on the installed version). If
  they do not, the planner adds an idempotent call in `app.py`'s lifespan; that is the
  rejected-for-now second option, not a new decision.
- **D-06:** The **parent** records `build.started` and `build.failed`, around the pool
  call in `app.py`/`pool.py`, where the existing `except` branches already see
  `BuildError` (the OCCT class name is inside its message), `BuildTimeout` and
  `BrokenProcessPool`, plus the hash slot. Workers stay silent — no handler is configured
  in `pool._warm()`, no record is emitted from `model.py`. `spur export` on the CLI emits
  nothing; its stderr prints remain its diagnostic. Accepted cost: the kernel's own
  traceback is available to the parent only as the `_RemoteTraceback` text
  `concurrent.futures` ships back, not as a class object. — **Reversibility:** costly —
  moving emission into the worker later means a second configuration point in a spawned
  process, N interleaved writers on stderr, and a null handler for the CLI's `export`
  path so it stays quiet.
- **D-07:** Only `serve` configures logging. `spur info` and `spur export` do not: none of
  the branches exist on the CLI (no queue, no byte cache, no pool — L04), and their
  human-facing stderr prose stays as it is.
- **D-08:** Phase 2's failure paths map as follows: `BuildTimeout` and `BrokenProcessPool`
  are `build.failed` kinds, distinguished by the exception-class field; the pool
  replacing a worker (`BuildPool.recreate_for`) emits its own `worker.replaced` record
  with the slot index, because `/api/health` only exposes a count (`workers_replaced`)
  and the log is the only place the *when* can live. These are branches that already
  exist, not new capability.

### Record vocabulary
- **D-09:** Event names, fixed: `build.started`, `build.failed`, `export.served`,
  `queue.refused`, `worker.replaced`. — **Reversibility:** costly — the debt file's own
  instruction is "pick the field names once"; the first dashboard or alert built on them
  makes them a published contract, and the tests assert them as literal strings.
- **D-10:** Gear identity on every per-request record is `slug` (`params.slug()`, for the
  human eye and grep) **plus** `params`: the non-default parameters as a nested object
  (`model_dump(exclude_defaults=True)`), which is exactly the shareable-link form L05
  keeps stable. A failed build is reproducible by pasting `params` into
  `/api/model.stl?`. Typically 2–6 keys. `slug` alone was rejected (two gears differing
  in profile shift, bore or recesses share a slug); a content hash was rejected (not
  reproducible from the log alone; and Python's `hash(p)` is per-process salted, so it
  could not be that value anyway).
- **D-11:** "Served from cache vs built" is **one** event, `export.served`, with a
  `source` field carrying one of three values that each name a code path that exists in
  `app.model()` today: `cache` (byte-cache hit, no slot), `compressed` (raw bytes cached,
  gzip-encoded now under a slot — the path quick task 260923-qwr found behind the
  concurrent-latency ratios), `built` (pool build under a slot). Also carries `fmt`,
  `quality`, `encoding`.
- **D-12:** `duration_ms` rides on `export.served` and `build.failed`: one monotonic clock
  in the parent around the slot in `app.model()`, so it includes IPC and the bytes
  crossing the boundary — what the client actually waited for. Zero on a plain cache hit
  is itself evidence. No worker-side clock (consistent with D-06). This is the debt
  file's own "a build that took three seconds".
- **D-13:** A per-request correlation id, `request`: `uuid4().hex[:8]`, minted at the top
  of `app.model()` and passed as a plain local to every record that request emits. Not
  middleware, not `contextvars`, not a response header. The one case `params` + time
  cannot disambiguate is two concurrent requests for the same gear — D-07 affinity's
  four-same-slot scenario is exactly that. Honouring an incoming `X-Request-ID` is
  deferred (see below).

### Levels and the proof
- **D-14:** Default level INFO, with a `SPUR_LOG_LEVEL` environment knob following the
  existing `SPUR_*` pattern (one row in README's table). Parsed against `logging`'s level
  names; nonsense falls back to INFO the way `int_env` falls back to its default. INFO is
  where `build.started`/`export.served` live, so all branches are visible out of the box;
  a deployer who only wants trouble sets WARNING.
- **D-15:** Levels split by whose fault it is. `build.started`, `export.served` → INFO.
  `build.failed` with `BuildError` → WARNING (a 422: the user's gear, deterministic —
  `solid-model/errors_and_logging.md` reads it as "a rule is missing", worth noticing, not
  paging). `build.failed` with `BuildTimeout` or `BrokenProcessPool`, and
  `worker.replaced` → ERROR (the service's fault; these are the 503s). `queue.refused` →
  WARNING (capacity, not breakage).
- **D-16:** The proof: one `caplog`-based test per branch, driving each branch the way the
  suite already does — `TestClient` + the injected `build_backend` (D-15 of Phase 2) for
  refused / cache / compressed / built / `BuildError` / `BuildTimeout` /
  `BrokenProcessPool`, and the existing real-pool wedge test for `worker.replaced` —
  asserting the **literal** event name and field names on the captured record. Plus one
  separate test that feeds a record through the formatter and `json.loads` the line, so
  the formatter is proven once and a formatter that dropped `extra` could not pass.
- **D-17:** Names are chosen once, in code: one new **kernel-free** module holding
  `configure()`, the formatter, and one small function per event
  (`build_started(...)`, `build_failed(...)`, `export_served(...)`, `queue_refused(...)`,
  `worker_replaced(...)`). Each event's field set is a mypy-checked signature; `app.py`
  and `pool.py` call intent-named functions instead of assembling `extra=` dicts. Tests
  assert the literal strings, so a rename is a deliberate test change. Five functions,
  not a framework. The module must be importable by both `cli.py` and `app.py` without
  reaching `cadquery`/`OCP` or `fastapi` — the existing import-linter contracts apply to
  it unchanged.

### Bookkeeping this phase owes (from CLAUDE.md, not discussed — required)
- **D-18:** The library/format/stream/level choice is a locked architectural decision:
  append a new entry (`L20`) to `docs/architecture/decision_log.md` recording D-01–D-04,
  D-06, D-14 with the rationale, dated. — **Reversibility:** one-way — the log is
  append-only by policy; a wrong entry is superseded, never rewritten.
- **D-19:** The three docs sections that currently say "Logging: None" become false and
  are updated in the same change: `docs/CODING_VALUES.md` §Logging,
  `docs/architecture/http-api.md` §Logging,
  `docs/architecture/solid-model/errors_and_logging.md` §Logging (now: the worker stays
  silent by decision, records are parent-side). `docs/architecture/gear-maths/errors_and_logging.md`
  §Logging stays "None, deliberately"; only its pointer sentence to the debt file
  changes. README's env-var table gains `SPUR_LOG_LEVEL`.
- **D-20:** Debt-file lifecycle per CLAUDE.md: `Status: resolved`, commit sha recorded,
  `git mv` to `docs/tech_debt/resolved/`, `docs/tech_debt/INDEX.md` row moved — in the
  same commit as the fix.

### Claude's Discretion
Decided by the planner/executor, not by the human — but do not drop them:
- The new module's name and location (not `spur/logging.py` — it shadows the stdlib name
  in readers' heads). Whether the per-event helpers live next to `configure()` or the
  formatter lives apart is a placement detail.
- Which of `app.py` / `pool.py` calls each helper. `queue.refused`, `export.served` and
  the request id belong where the request lives (`app.py`); `worker.replaced` belongs
  where `recreate_for` lives (`pool.py`); `build.started`/`build.failed` may sit on
  either side of `pool.export` as long as they see the exception class and the slot.
- The remaining field names beyond D-09–D-13: the exception-class field on
  `build.failed`, the slot and cause on `worker.replaced`, the in-flight count and
  `MAX_QUEUED_BUILDS` on `queue.refused`, and the envelope keys (timestamp, level, logger
  name). Timestamp format (ISO-8601 UTC recommended). Whether `exc_info`/traceback text
  rides on ERROR records. Whether `version` rides on every record.
- How `SPUR_LOG_LEVEL` is parsed (a sibling of `int_env` in `spur/__init__.py` is the
  obvious shape).
- Sequencing of the docs updates (D-19), the `L20` entry (D-18) and the debt move (D-20)
  against the code commits — CLAUDE.md already fixes that the debt move lands with the
  fix.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### The debt this phase retires
- `docs/tech_debt/active/2026-09-21-no-structured-logging.md` — the four branches, the
  "pick the field names once" instruction, the "no `print()` by accident" risk, and the
  boundary (`calc.py` stays log-free). Must end the phase `Status: resolved`, sha
  recorded, `git mv`'d to `docs/tech_debt/resolved/`, row moved in
  `docs/tech_debt/INDEX.md`.
- `docs/tech_debt/INDEX.md` — the row that moves with it.

### Locked decisions and standards
- `docs/architecture/decision_log.md` — L04 (admission control is web-layer only; the CLI
  never queues), L12 (pinned closure — why no new dependency), L13 (`make verify` is the
  gate), L15 (`TRY003` off, messages are the product), L05 (defaults never rescale — why
  `exclude_defaults=True` is a stable identity). Append-only: `L20` is appended, nothing
  edited.
- `CLAUDE.md` / `AGENTS.md` — the gate, the debt-file lifecycle, "one concern per commit".
- `docs/CODING_VALUES.md` — §Logging (currently "none today"; D-19 updates it), and the
  comment standard every new comment must meet.

### Docs that currently say "Logging: None" (D-19)
- `docs/architecture/http-api.md` §Logging
- `docs/architecture/solid-model/errors_and_logging.md` §Logging — also the source of the
  "a `BuildError` means a rule is missing" reading behind D-15's WARNING level.
- `docs/architecture/gear-maths/errors_and_logging.md` §Logging — stays "None,
  deliberately"; pointer sentence only.
- `README.md` — the `SPUR_*` environment-variable table (`SPUR_LOG_LEVEL` row).
- `docs/architecture/cli.md` — check whether it states the stdout/stderr convention D-04
  relies on; update only if it does.

### Phase 2 decisions this phase builds on
- `.planning/phases/02-cad-off-the-event-loop/02-CONTEXT.md` — D-02 (serving process is
  kernel-free; the new module must be too), D-05 (bytes-only boundary), D-07 (hash-slot
  affinity — the slot index in `worker.replaced`), D-10/D-12 (timeout and broken-pool
  paths and their status codes), D-15 (injectable `build_backend` — how the branch tests
  drive each path).

### Code this phase edits or reads
- `src/spur/app.py` — `_build_slot()` (the `queue.refused` branch), `model()` (the three
  `export.served` sources, the three `except` branches, where `request` and
  `duration_ms` are minted), `lifespan()`.
- `src/spur/pool.py` — `BuildPool._run_with_timeout` (timeout / broken-pool branches),
  `recreate_for` (the `worker.replaced` branch), `executor_for` (the slot index).
- `src/spur/cli.py` — `cmd_serve` (D-05: `configure()` + `log_config=None`); `cmd_info`
  / `cmd_export` unchanged (D-07).
- `src/spur/build_errors.py` — the exception classes whose names are the
  exception-class field.
- `src/spur/params.py` — `slug()`, and `model_dump(exclude_defaults=True)` for D-10.
- `src/spur/__init__.py` — `int_env`, the pattern the level knob follows.
- `pyproject.toml` — ruff `LOG`/`G` rules (already on); the four import-linter contracts
  the new module must satisfy; pytest `filterwarnings = error`.
- `tests/test_api.py` — the autouse inline-backend fixture, the saturation test
  (`test_a_saturated_service_refuses_instead_of_queueing`), the counting-backend and
  counting-gzip patterns for cache / compressed / built.
- `tests/test_pool.py` — the raising-backend pattern
  (`test_each_build_failure_mode_maps_to_its_own_status_and_type`) and the real wedge /
  die tests that already exercise `recreate_for`.
- `docker/smoke.py` — bypasses `cli`; gets no configured logger by design (D-05).

### Milestone context
- `.planning/REQUIREMENTS.md` — REQ-structured-logging and its acceptance criterion
  ("a test asserts the branch records are emitted with their field names").
- `.planning/ROADMAP.md` §Phase 3 — the four success criteria.
- `.planning/PROJECT.md` §Success Metric #3 — "Logs answer an incident".

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `int_env()` (`spur/__init__.py`) — the established knob pattern; `SPUR_LOG_LEVEL` needs
  a string sibling with the same "nonsense falls back" behaviour.
- `_build_slot()` (`app.py`) — the `queue.refused` branch is the single `raise
  HTTPException(503, ...)` inside it; `_in_flight_builds` and `MAX_QUEUED_BUILDS` are
  already in scope there.
- The three `except` branches in `app.model()` and the two in
  `pool._run_with_timeout` — every failure kind D-08 names already has its own branch;
  no new control flow is needed.
- `params.slug()` and `GearParams.model_dump(exclude_defaults=True)` — the identity
  fields of D-10 exist; `GearParams` is frozen and pydantic v2.
- Phase 2 D-15's injectable `build_backend` and the tests that already use it
  (`counting_backend`, `counting_gzip`, the raising backend in `test_pool.py`) — each
  D-16 branch test is a variant of a test that already exists.
- `tests/test_pool.py::test_a_wedged_build_is_terminated_and_its_worker_replaced` and
  `test_a_dying_worker_surfaces_as_broken_pool_and_is_replaced` — already drive
  `recreate_for`; the `worker.replaced` assertion attaches to one of them.
- ruff `LOG` and `G` rule families are already enabled — no f-strings in log calls, no
  `logging.warn`, etc. — so the lint gate polices the new call sites for free.

### Established Patterns
- Module boundaries are enforced by import-linter contracts, not discipline. The new
  module sits under `spur.*` and is imported by `spur.cli` and `spur.app`; it therefore
  must import neither `cadquery`/`OCP` nor `fastapi`/`starlette`/`spur.app`. No new
  contract is needed; the existing four already forbid the wrong edges.
- Every knob carries the measurement or constraint that set it, in a comment at the point
  of definition. `SPUR_LOG_LEVEL` and the stderr choice get the same treatment.
- Vendor types stop at their boundary — a `LogRecord` is stdlib, not vendor; the
  per-event helpers (D-17) are the intent-named boundary that keeps `extra=` dict shapes
  out of `app.py`/`pool.py`.
- Tests are named as requirements
  (`test_a_saturated_service_refuses_instead_of_queueing`); the D-16 tests follow suit.
- `pytest` runs with `filterwarnings = error`: anything that emits a `Warning` during a
  branch test fails it. stdlib `logging` emits none, but the researcher should confirm
  `caplog` + a root handler on the installed pytest raises nothing.

### Integration Points
- `cli.cmd_serve` → `configure()` → `uvicorn.run(..., log_config=None)`: the one
  composition point (D-05).
- `app.model()` → per-event helpers: `request` id, `export.served`, `build.started`,
  `build.failed`, `duration_ms`.
- `app._build_slot()` → `queue_refused(...)`.
- `pool.recreate_for()` → `worker_replaced(...)`.
- `tests/test_api.py`, `tests/test_pool.py` → `caplog`; one new formatter round-trip test.
- `docs/` (D-19), `decision_log.md` (D-18), `docs/tech_debt/` (D-20), `README.md`.

</code_context>

<specifics>
## Specific Ideas

- Target record shape (field names from D-09–D-13 are fixed; envelope keys are
  discretion):
  `{"ts": "...", "level": "INFO", "logger": "spur.app", "event": "export.served",
  "request": "a3f9c1d2", "slug": "spur_z21_m1.75_pa20", "params": {"teeth": 21},
  "fmt": "stl", "quality": "preview", "encoding": "gzip", "source": "built",
  "duration_ms": 1834}`
- The incident question the phase must answer (PROJECT.md success metric #3): from the
  stderr stream alone, for one request — was it refused, served from cache, compressed,
  or built; if built, how long; if it failed, which class, and was a worker replaced.
- `make serve 2>&1 | jq` is the intended local reading experience; no second renderer.
- `hash(p)` is per-process salted and must not appear in any record as an identity;
  the slot index (`hash(p) % workers`) is fine because it is only meaningful within one
  serving-process lifetime, which is what `worker.replaced` describes.

</specifics>

<deferred>
## Deferred Ideas

- **Honour an incoming `X-Request-ID` header** — correlates with a reverse proxy's own
  logs. Proxy integration, a new capability; the local 8-hex id (D-13) is what ships.
  Revisit when the service is deployed behind a proxy whose logs someone actually reads.
- **A byte-cache eviction record** — named as "invisible" in the debt file's context but
  not in its "next step" and not asked for; `export.served` with `source` answers the
  hit-rate question the eviction record would have served. Add only if a measured cache
  question arises.
- **Worker-side logging** (rejected variant of D-06) — revisit only if an incident needs
  the kernel's exception class as an object rather than the class name already in
  `BuildError`'s message.
- **Querying workers from `/api/health`** — still deferred from Phase 2 (D-13 there);
  `worker.replaced` records reduce, not remove, the reason for it.

</deferred>

---

*Phase: 3-Structured Logging at the Composition Boundary*
*Context gathered: 2026-09-24*
