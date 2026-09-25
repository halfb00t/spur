# Phase 3: Structured Logging at the Composition Boundary - Research

**Researched:** 2026-09-24
**Domain:** stdlib `logging` configuration at a process composition root; JSON formatter
design; uvicorn/multiprocessing interaction with logger configuration
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Format and library**
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

**Configuration point and emitting process**
- **D-05:** The root logger is configured in `cli.cmd_serve`, before `uvicorn.run` — the
  literal composition root: every production start is `spur serve` (Dockerfile
  `CMD ["spur", "serve"]`, `make serve`). Not covered by design: `docker/smoke.py`
  (asserts status codes only), a bare `uvicorn spur.app:app`, `TestClient` — they get
  stdlib's `lastResort` (stderr, WARNING+), a degraded state, not a broken one.
  **ASSUMPTION to verify in research:** with `SPUR_WORKERS>1` uvicorn's child processes
  inherit the parent's root configuration (spawn vs fork on the installed version). If
  they do not, the planner adds an idempotent call in `app.py`'s lifespan; that is the
  rejected-for-now second option, not a new decision.
  — **This research falsified the assumption; see Summary. The planner must implement
  the second option, not treat it as rejected-for-now.**
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

**Record vocabulary**
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

**Levels and the proof**
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

**Bookkeeping this phase owes (from CLAUDE.md, not discussed — required)**
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

### Deferred Ideas (OUT OF SCOPE)
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
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-------------------|
| REQ-structured-logging | A structured logger is configured at the composition boundary (`cli.cmd_serve` / `app.py` startup) and emits the decision branches that already exist — build started (with parameter slug), build failed (with exception class), export served from cache vs. built, queue refused. Acceptance: a test asserts the branch records are emitted with their field names. Boundary: `calc.py` stays log-free. | Architectural Responsibility Map identifies exactly which module owns each branch; Pattern 1 (idempotent `configure()` at two call sites) resolves the composition-boundary question for both `SPUR_WORKERS=1` and `>1`; Patterns 2-5 give verified, line-cited implementation guidance for the formatter and each of the five event call sites (including `worker.replaced`, added by CONTEXT.md after the requirement text was written); Pitfalls 1-4 and the Validation Architecture's Phase Requirements → Test Map give the D-16 test author concrete `caplog` gotchas and file-level test targets. |
</phase_requirements>

## Summary

This phase adds no new dependency (D-01: stdlib `logging` only). The work is almost
entirely a design/wiring problem, not a library-selection problem, so this research
leans on direct inspection of the installed `.venv` (uvicorn 0.53.0, Python 3.12.13) and
the current source tree rather than external documentation lookups — every load-bearing
claim below was checked by running code against the actual installed versions, which is
a stronger source than a web search would have been.

The single most important finding changes one of CONTEXT.md's two open assumptions:
**D-05's assumption is false.** `uvicorn`'s multi-worker mode (`SPUR_WORKERS>1`) spawns
child processes via `multiprocessing.get_context("spawn")`, and a spawned child does
**not** inherit the parent's `logging` module state — no handlers, no configured level.
This was confirmed two ways: (1) reading `uvicorn`'s installed `_subprocess.py` and
`supervisors/multiprocess.py` source, and (2) a minimal live reproduction with
`multiprocessing.get_context("spawn")` showing a child process's root logger has zero
handlers even though the parent's root logger was configured immediately before
spawning. Because `SPUR_WORKERS` defaults to `1` (`cli.py`'s `--workers` default), the
single-worker path (`server.run()` directly in the process that called `cmd_serve`) is
unaffected — `configure()` called once in `cli.cmd_serve` is correct and sufficient for
the default deployment. The gap only appears if a deployer raises `SPUR_WORKERS` above 1,
at which point every per-request event this phase adds would silently vanish in every
worker but the one that happened to inherit nothing. CONTEXT.md already named the fix
for this case ("the planner adds an idempotent call in `app.py`'s lifespan") — this
research confirms that fix is *necessary*, not merely a defensive fallback.

D-02's assumption — that `uvicorn.run(..., log_config=None)` leaves root logging alone
and lets `uvicorn`'s own loggers propagate to root — is **confirmed true** by reading the
installed `uvicorn.config.Config.configure_logging()` source: the entire body is gated
behind `if self.log_config is not None:`, so passing `None` skips `dictConfig` entirely,
and since `self.log_level` is also `None` by default, uvicorn never touches
`uvicorn.error`/`uvicorn.access` logger levels or handlers either. Both loggers keep
Python's default `propagate=True`, so they flow to whatever the root logger is configured
with — the one handler `configure()` installs.

**Primary recommendation:** Implement `configure()` and the five per-event functions in
one small kernel-free module (see Claude's Discretion for naming), call `configure()`
once in `cli.cmd_serve` before `uvicorn.run(..., log_config=None)` per D-05, and add an
**idempotent** second call to `configure()` inside `app.py`'s `lifespan()` startup — the
only path that reaches every uvicorn worker process regardless of `SPUR_WORKERS`. Guard
`configure()` against double-installing a handler (checked by name or a module-level
flag) so the common `SPUR_WORKERS=1` case, where both call sites run in the same process,
does not end up with two stderr handlers double-printing every line.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Log configuration (composition root) | API/Backend — `cli.cmd_serve` | API/Backend — `app.py` `lifespan()` | `cmd_serve` is the literal single production entrypoint (Dockerfile `CMD ["spur", "serve"]`); `lifespan()` is the only code that reaches every uvicorn worker process when `SPUR_WORKERS>1`, since spawn does not inherit `cmd_serve`'s configuration (verified, see Summary). |
| `build.started` / `build.failed` emission | API/Backend — `app.py` around `pool.export()` | — | The parent process owns the `except BuildError/BuildTimeout/BrokenProcessPool` branches (D-06); the worker never runs application code that could log. |
| `export.served` emission | API/Backend — `app.py` `model()` | — | Cache/compression/build decisions and `duration_ms` timing all live in the parent event loop, never in a worker. |
| `queue.refused` emission | API/Backend — `app.py` `_build_slot()` | — | The single `raise HTTPException(503, ...)` branch already lives there with `_in_flight_builds`/`MAX_QUEUED_BUILDS` in scope. |
| `worker.replaced` emission | API/Backend — `pool.py` `recreate_for` | — | The identity-guarded replacement decision (only the caller that actually swaps the executor should log/count) already lives there; the cause (timeout vs. broken pool) is only known at `_run_with_timeout`'s two call sites and must be threaded in. |
| CAD build execution | Worker subprocess (spawned, kernel-loaded) | — | Deliberately **not** a logging tier by decision (D-06): no handler is configured in `pool._warm()`, no record is emitted from `model.py`. Log-free by design, not by omission. |
| Gear maths (`calc.py`) | Pure domain logic, no tier | — | Stays outside every process/serving concern; `warnings` in its return value is its only diagnostic (L01, unchanged). |

## Package Legitimacy Audit

**Not applicable — no external package is installed in this phase.** D-01 locks stdlib
`logging` with a project-owned `Formatter`; `structlog` and logfmt were explicitly
rejected in CONTEXT.md. `pyproject.toml`'s `dependencies` list (`cadquery`, `fastapi`,
`pydantic`, `uvicorn`) is unchanged by this phase — confirmed by reading
`pyproject.toml` this session; no `structlog`, `python-json-logger`, or similar appears
anywhere in the tree (`grep -rn "structlog\|json.logger\|pythonjsonlogger" src/`
returns nothing). `docker/refresh-requirements.sh` and the pinned closure (L12) are
therefore untouched, and no ecosystem registry check is needed.

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|---------------|
| `logging` (stdlib) | Python 3.12.13 (installed `.venv`), floor 3.10 per `pyproject.toml` | Root logger, handler, per-event calls | Zero new dependency; the project's own precedent (Phase 2 D-03) is stdlib-only for exactly this kind of cross-cutting infrastructure. `ruff`'s `LOG`/`G` rule families (already selected in `pyproject.toml`'s `[tool.ruff.lint]`, confirmed by reading it this session) police call-site correctness for free. |
| `logging.Formatter` (subclassed) | stdlib | One JSON object per line built from `LogRecord` attributes + `extra` | No parser needed on the reading side (`make serve 2>&1 \| jq`, D-03); a custom `Formatter.format()` is the documented extension point for this — confirmed by inspecting a `LogRecord.__dict__` this session (see Code Examples) rather than assumed from memory. |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `uuid` (stdlib) | stdlib | `uuid4().hex[:8]` per-request correlation id (D-13) | Minted once per request in `app.model()`, passed as a plain local — not `contextvars`, not middleware. |
| `time.monotonic()` (stdlib) | stdlib | `duration_ms` on `export.served`/`build.failed` (D-12) | Wrap the `_build_slot()` block in `app.model()`; a full cache hit (source=`cache`) never enters that block, so its `duration_ms` is `0` by construction, not by a separate branch. |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| stdlib `logging` + custom `Formatter` | `structlog` | Rejected in CONTEXT.md (D-01): a new pinned package in an image that already carries 1.6 GB of OpenCascade/VTK (per `docs/CODING_VALUES.md` §Dependencies), for a five-event, one-process-boundary problem stdlib already solves. |
| JSON lines | logfmt | Rejected in CONTEXT.md (D-01): "a convention with no parser" — `jq` is the intended local reader (D-03), and logfmt buys nothing over JSON for that. |

**Installation:** None — no new dependency.

**Version verification:** N/A (stdlib only). Installed `uvicorn` confirmed at `0.53.0`
via `.venv/bin/python -c "import uvicorn; print(uvicorn.__version__)"` this session
(newer than `pyproject.toml`'s `uvicorn>=0.30` floor — the multiprocessing/logging
behavior below was checked against the *installed* version, which is what actually runs).

## Architecture Patterns

### System Architecture Diagram

```
                         SPUR_WORKERS=1 (default)                    SPUR_WORKERS>1
                         ─────────────────────────                   ────────────────
cli.cmd_serve()                                                      cli.cmd_serve()
  configure() ──────┐                                                  configure() [runs,
  (installs stderr   │                                                  but only in the
   JSON handler on    │                                                  PARENT process --
   root logger)       │                                                  see Summary]
  uvicorn.run(        │                                                  │
    log_config=None)  │                                                  uvicorn.run(workers=N)
      │               │                                                     │
      ▼               │                                                     ▼
  same process ◄──────┘                                              Multiprocess(...).run()
      │                                                                     │
      │  (root logger already configured;                        spawn.Process each ──► child re-imports
      │   uvicorn.error / uvicorn.access                                   │            "spur.app" fresh;
      │   propagate=True, land on it)                                      │            root logger has
      ▼                                                                    │            NO handlers unless
  app.py  lifespan() startup                                               ▼            lifespan() configures
     configure()  ◄── IDEMPOTENT call here is what makes the        app.py  lifespan()
     (no-op: handler                right-hand path work too           configure()  ◄── the ONLY call that
      already installed)                                               (installs the         reaches this
     BuildPool(...)                                                     handler for THIS      process)
        │                                                                worker, first time)
        ▼                                                               BuildPool(...)
  per-request events:                                                       │
   app._build_slot() ──► queue_refused()                                    ▼
   app.model()        ──► build_started() / build_failed() / export_served()
   pool.recreate_for()──► worker_replaced()
        │
        ▼
  root logger (INFO+, JSON Formatter) ──► one stderr StreamHandler ──► docker logs
  (uvicorn.error / uvicorn.access also land here, unconfigured by uvicorn itself)
```

A reader can trace: request enters `app.model()` → decision branch (`cache` / `compressed`
/ `built` / refused / `BuildError` / `BuildTimeout` / `BrokenProcessPool`) → the matching
per-event helper call → root logger → JSON `Formatter` → one stderr stream → `docker logs`
or `make serve 2>&1 | jq`.

### Recommended Project Structure
```
src/spur/
├── app.py             # calls the per-event helpers at the 4 request-facing branches
├── pool.py             # calls worker_replaced() from recreate_for (with cause threaded in)
├── cli.py              # calls configure() once in cmd_serve, before uvicorn.run(log_config=None)
├── <new module>.py      # configure(), the JSON Formatter, and the 5 per-event functions
│                        # (naming: Claude's Discretion below — not spur/logging.py)
└── calc.py             # UNCHANGED — no logging import, ever
```

### Pattern 1: Idempotent `configure()` at two call sites
**What:** `configure()` installs exactly one stderr `StreamHandler` with the JSON
`Formatter` on the root logger, and sets the root level from `SPUR_LOG_LEVEL`. It must be
safe to call twice in the same process without doubling output.
**When to use:** Called once in `cli.cmd_serve` (D-05, the composition root for the
`SPUR_WORKERS=1` default) **and** once at the top of `app.py`'s `lifespan()` startup (the
only call site that runs inside every spawned uvicorn worker — see Summary).
**Example:**
```python
# Source: pattern derived from this session's direct verification of uvicorn 0.53.0's
# spawn-based multiprocessing (see Summary); idempotency technique is the standard
# stdlib-logging-cookbook guard (checking for an existing handler instance/marker
# before adding another) -- not from any external doc, written for this design.
_CONFIGURED = False

def configure(level: str = "INFO") -> None:
    global _CONFIGURED
    if _CONFIGURED:
        return
    root = logging.getLogger()
    handler = logging.StreamHandler()  # stderr by default (D-04)
    handler.setFormatter(_JsonFormatter())
    root.addHandler(handler)
    root.setLevel(_parse_level(level))
    _CONFIGURED = True
```
**Verified this session:** a spawned child process (`multiprocessing.get_context("spawn")`)
does not see a parent's `root.addHandler(...)` call — reproduced live:
```
$ .venv/bin/python spawn_test.py
parent root handlers: [<StreamHandler <stderr> (NOTSET)>]
child root handlers: []
```
This is why the `lifespan()` call site is required, not optional, once `SPUR_WORKERS>1`
is in play.

### Pattern 2: JSON `Formatter` built from `LogRecord.__dict__` minus the standard attribute set
**What:** Iterate `record.__dict__`, excluding the fixed set of attributes every
`LogRecord` carries regardless of `extra=`, and treat everything else as the
application's fields (`event`, `slug`, `params`, `duration_ms`, ...).
**When to use:** The one formatter, used by the one handler (D-03).
**Verified this session** — the exact key set a stock `LogRecord` carries with no
`extra=` beyond two custom keys (`.venv/bin/python`, direct `logging.Logger.makeRecord`
call):
```
['args', 'created', 'event', 'exc_info', 'exc_text', 'filename', 'funcName', 'levelname',
 'levelno', 'lineno', 'module', 'msecs', 'msg', 'name', 'pathname', 'process',
 'processName', 'relativeCreated', 'slug', 'stack_info', 'taskName', 'thread',
 'threadName']
```
`event` and `slug` above are the two keys this test passed via `extra=`; everything else
in that list is the standard envelope. A formatter should special-case a small subset of
the standard ones into fixed JSON keys (`ts` from `created`, `level` from `levelname`,
`logger` from `name`) and dump the rest of the non-standard keys as the event's own
fields — this is what makes D-16's round-trip test ("a formatter that dropped `extra`
could not pass") meaningful: the standard-attribute exclusion set must be a named
constant the formatter and its test both reference, not a guess re-derived by eye.

### Pattern 3: `SPUR_LOG_LEVEL` parsing via `logging.getLevelName()`, not a private mapping
**What:** `logging.getLevelName(name.upper())` returns the integer level for a valid
name and a `"Level <name>"` string for anything else — usable as a validity check with no
private API.
**Verified this session:**
```
>>> logging.getLevelName("INFO")
20
>>> logging.getLevelName("NONSENSE")
'Level NONSENSE'
```
**Example, matching `int_env`'s own "nonsense falls back to default" shape** (`spur/__init__.py`,
read this session — `int_env`'s body: `try: return max(1, int(os.environ.get(name) or default)) except ValueError: return default`):
```python
# Source: this session's verification of logging.getLevelName's documented behavior
# (stable since early stdlib logging, not version-specific to 3.12) -- a sibling of
# int_env's own fallback shape, not a new pattern.
def _parse_level(raw: str) -> int:
    level = logging.getLevelName(raw.upper())
    return level if isinstance(level, int) else logging.INFO
```
Do **not** use `logging._nameToLevel` (private) or `logging.getLevelNamesMapping()`
(added in 3.11 only — `pyproject.toml`'s `target-version = "py310"` and the dual-version
CI matrix (`ruff` comment: "CI runs 3.10 and 3.12") rule it out as a floor violation).

### Pattern 4: threading `cause` through `recreate_for` for `worker.replaced`
**What:** `pool.py`'s `recreate_for(p, executor)` (read this session,
`src/spur/pool.py:94-140`) is the identity-guarded single place that actually performs a
replacement — the right place for the `worker_replaced()` call per D-08. But the *cause*
(`timeout` vs. `broken_pool`) is only known at its two call sites inside
`_run_with_timeout` (`src/spur/pool.py:163` the `except asyncio.TimeoutError:` branch,
and `src/spur/pool.py:190` the `except BrokenProcessPool:` branch) — `recreate_for`
itself has no way to know which one is calling it.
**When to use:** Add a `cause: str` parameter to `recreate_for`, passed as `"timeout"`
from line 185's call and `"broken_pool"` from line 197's call (both read this session);
call `worker_replaced(slot=i, cause=cause)` immediately after the `self.replaced += 1`
increment at the end of `recreate_for` (`src/spur/pool.py:140`), inside the identity
guard, so a duplicate same-slot caller (the `CR-01`/`WR-01` case the docstring at
`src/spur/pool.py:94-113` already documents) never double-logs.
**Verified:** `src/spur/pool.py:110` is the guard (`if self._executors[i] is not executor:
return`); `src/spur/pool.py:137` is the executor swap; `src/spur/pool.py:140` is
`self.replaced += 1` — read directly this session, exact line offsets confirmed via
`grep -n`.

### Pattern 5: `duration_ms` and `source` derivation in `app.model()`
**What:** `app.model()` (`src/spur/app.py:311-380`, read this session) already has three
distinct code paths that map 1:1 to D-11's `source` values:
- `source="cache"` — `_EXPORTS.get(key)` hits at `src/spur/app.py:322`; `_build_slot()` is
  never entered, so `duration_ms=0` is correct by construction, not a special case.
- `source="compressed"` — `_build_slot()` is entered (`src/spur/app.py:330`), the raw
  bytes are already cached (`raw is not None` at the check following `src/spur/app.py:332`),
  but this gzip encoding is not — `_gzip()` runs inside the slot.
- `source="built"` — `raw is None` at `src/spur/app.py:333`; `backend(...)` runs inside
  the slot.
**When to use:** Start a `time.monotonic()` clock immediately before the `with
_build_slot():` line (`src/spur/app.py:330`) and stop it right after the block exits
(before the `except` handlers, since `build.failed`'s `duration_ms` needs the same
clock on the failure path too — an exception inside the `with` block still lets a
`try/finally`-timed duration be read in the `except` clauses).

### Anti-Patterns to Avoid
- **Configuring logging only in `cli.cmd_serve`:** silently drops every event once a
  deployer sets `SPUR_WORKERS>1` — verified this session (Pattern 1). `app.py`'s
  `lifespan()` must also call `configure()`, idempotently.
- **f-strings in log calls:** `ruff`'s `G004` (already selected via `[tool.ruff.lint]`
  `"LOG", "G"`, confirmed by reading `pyproject.toml`) flags this; use `extra=` or
  `logger.info("%s", value)` positional substitution instead — but per Pattern 2/D-17,
  the per-event helper functions should be the only call sites, so this is enforced by
  construction if `app.py`/`pool.py` never call `logging` directly.
- **Root-logger module-level calls (`logging.info(...)`):** `ruff`'s `LOG015` flags this
  (confirmed by `ruff rule LOG015` this session) — use `logging.getLogger(__name__)` in
  the new module, not the bare `logging` functions.
- **Emitting from a worker process:** D-06's explicit rejection — no handler in
  `pool._warm()`, nothing from `model.py`. The kernel's own traceback is only available
  to the parent as `_RemoteTraceback` text via `concurrent.futures`, never as a class
  object — accepted cost, not a bug to fix in this phase.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Validating `SPUR_LOG_LEVEL` against real level names | A hand-written dict of name→int | `logging.getLevelName(name.upper())` + `isinstance(..., int)` check | Verified this session (Pattern 3) — stdlib already exposes exactly this validation surface; a hand-rolled dict would drift from `logging`'s own level names (e.g. if a level is ever aliased). |
| Excluding envelope attributes in the JSON formatter | Enumerating them freshly at write time from memory | A single module-level frozenset of standard `LogRecord` attribute names, defined once and referenced by both the formatter and its round-trip test | The exact key set is version-sensitive in principle (verified this session against 3.12.13, but the list is what Python's own docs call "LogRecord attributes" and is stable across 3.10-3.12) — define it once, verified against the installed interpreter, not re-derived by eye in two places. |
| Per-request correlation | Middleware, `contextvars` | A plain local `uuid4().hex[:8]` minted at the top of `app.model()` (D-13) | CONTEXT.md already rejected the heavier options; this is a locked decision, not a research question — noted here only so the planner doesn't reopen it. |

**Key insight:** Every "don't hand-roll" item above is really "don't re-derive by eye
something the interpreter can answer" — the level-name validation and the standard
`LogRecord` attribute set are both places a guess could quietly drift from the installed
Python's actual behavior.

## Common Pitfalls

### Pitfall 1: `caplog` defaults to WARNING — INFO-level events are invisible without `set_level`
**What goes wrong:** D-16's tests assert `build.started`/`export.served` at INFO
(D-15's levels), but `pytest`'s `caplog` fixture only captures WARNING+ unless told
otherwise.
**Why it happens:** Verified this session — a plain `caplog.records` after a
`logger.info(...)` call with no `caplog.set_level()` returned `[]` for the INFO record
and only `['WARNING']` for a WARNING record in the same test, live reproduction:
```
$ .venv/bin/python -m pytest test_caplog_probe.py -q -s
DEFAULT CAPLOG LEVELS: ['WARNING']
SET_LEVEL CAPLOG LEVELS: ['INFO']
```
**How to avoid:** Every D-16 branch test that asserts an INFO-level record must call
`caplog.set_level(logging.INFO)` (or `caplog.at_level(logging.INFO)`), scoped as narrowly
as the test needs. `pytest.ini_options` has `filterwarnings = ["error", ...]` (confirmed
by reading `pyproject.toml`), and `caplog.set_level` was confirmed to raise no warnings
in this session's probe — clean.
**Warning signs:** A D-16 test for `build.started`/`export.served` (INFO) passes locally
with zero assertions actually exercised because `caplog.records` was silently empty — a
test that would pass even if the code never logged at all. Assert `caplog.records` is
non-empty as well as its contents, or the missing-`set_level` bug produces a false green.

### Pitfall 2: `SPUR_WORKERS>1` silently drops every event unless `lifespan()` also configures
**What goes wrong:** Configuring only in `cli.cmd_serve` (as D-05 originally proposed)
works for the default `SPUR_WORKERS=1`, but the moment a deployer raises it, the spawned
uvicorn workers run in fresh interpreters with an unconfigured root logger — records at
INFO/WARNING never reach `lastResort`'s WARNING floor cleanly formatted, and ERROR
records that do reach `lastResort` are plain text, not JSON, breaking `jq`.
**Why it happens:** `multiprocessing`'s `spawn` context (confirmed as what uvicorn's
`_subprocess.py` uses this session) starts a fresh Python interpreter per child; only
picklable data crosses the boundary, and a parent's live `logging.Logger`/`Handler`
objects are not part of what's pickled to the child's target callable
(`subprocess_started`, which is what actually runs in the child — not `cli.cmd_serve`).
**How to avoid:** Add the idempotent second `configure()` call in `app.py`'s `lifespan()`
startup (Pattern 1) — the only code that runs inside every worker process regardless of
`SPUR_WORKERS`.
**Warning signs:** A manual test with `SPUR_WORKERS=2` shows some requests logging JSON
and others not, or none at all, depending on which worker served them.

### Pitfall 3: Double-configuring root logging doubles every line
**What goes wrong:** With the fix for Pitfall 2 in place, the default `SPUR_WORKERS=1`
path calls `configure()` twice in the *same* process (`cmd_serve`, then `lifespan()`
startup, since the single-process path never spawns) — a naive `configure()` that always
calls `addHandler` would attach two stderr handlers, printing every line twice.
**Why it happens:** `logging.getLogger().addHandler()` is additive and idempotent-unsafe
by default — nothing in stdlib prevents adding the same handler class twice.
**How to avoid:** Pattern 1's module-level `_CONFIGURED` guard (or equivalently, check
`any(isinstance(h, _JsonHandler) for h in root.handlers)` before adding).
**Warning signs:** `make serve 2>&1 | jq` shows every event line twice; a D-16 test
asserting `len(caplog.records) == 1` for a single request instead reads `2`.

### Pitfall 4: worker-replacement double-counting collapses if `cause` is dropped
**What goes wrong:** If the executor swap and the `worker_replaced()` call are
accidentally moved to *before* the identity guard (`src/spur/pool.py:110`), or if the
`cause` parameter is threaded incorrectly, the already-fixed `CR-01`/`WR-01` double-count
bug (documented in `pool.py`'s own docstring, `src/spur/pool.py:94-113`, and covered by
`tests/test_pool.py::test_two_same_slot_deaths_from_one_incident_replace_the_worker_once`)
regresses — now for the log record as well as the counter.
**Why it happens:** D-07's hash-slot affinity means multiple concurrent same-slot
requests can each observe the same dead/wedged worker and each call `recreate_for`.
**How to avoid:** Put the `worker_replaced()` call *inside* the existing identity guard
(`src/spur/pool.py:110`), after `self.replaced += 1` (`src/spur/pool.py:140`) — never at
either call site (`src/spur/pool.py:185`/`:197`) directly, which would run once per
caller rather than once per incident.
**Warning signs:** `tests/test_pool.py`'s existing four-same-slot / two-same-slot tests
(`test_four_same_slot_requests_all_refuse_without_cancellation`,
`test_two_same_slot_deaths_from_one_incident_replace_the_worker_once`) still pass on
`pool.replaced`, but a new D-16 assertion on caplog record count for `worker.replaced`
would catch a regression the existing counter-only tests cannot.

## Code Examples

### Verified: uvicorn 0.53.0's `configure_logging()` — confirms D-02
```python
# Source: .venv/lib/python3.12/site-packages/uvicorn/config.py, Config.configure_logging,
# read this session in full.
def configure_logging(self) -> None:
    logging.addLevelName(TRACE_LOG_LEVEL, "TRACE")
    if self.log_config is not None:          # <-- log_config=None skips this whole branch
        ...                                   #     (dictConfig, fileConfig, etc.)
    if self.log_level is not None:            # <-- also None by default; skipped too
        logging.getLogger("uvicorn.error").setLevel(log_level)
        logging.getLogger("uvicorn.access").setLevel(log_level)
        logging.getLogger("uvicorn.asgi").setLevel(log_level)
    if self.access_log is False:
        ...
```
With `log_config=None` and no `log_level` passed, this function is a no-op beyond
registering the `TRACE` level name — root logging is untouched, exactly as D-02 assumed.

### Verified: spawn child does not inherit parent's logging configuration
```python
# Source: this session's live reproduction, .venv/bin/python, spawn context (same
# context uvicorn.supervisors.multiprocess / uvicorn._subprocess use, confirmed by
# reading those files this session).
import logging, multiprocessing as mp

def child():
    print("child root handlers:", logging.getLogger().handlers)

if __name__ == "__main__":
    logging.getLogger().addHandler(logging.StreamHandler())
    print("parent root handlers:", logging.getLogger().handlers)
    ctx = mp.get_context("spawn")
    p = ctx.Process(target=child)
    p.start(); p.join()

# Output:
# parent root handlers: [<StreamHandler <stderr> (NOTSET)>]
# child root handlers: []
```

### Verified: standard `LogRecord` attribute set (for the formatter's exclusion list)
```python
# Source: this session, .venv/bin/python, logging.Logger.makeRecord with extra={"event":
# ..., "slug": ...} — the two application keys are visibly appended to the fixed set.
['args', 'created', 'event', 'exc_info', 'exc_text', 'filename', 'funcName', 'levelname',
 'levelno', 'lineno', 'module', 'msecs', 'msg', 'name', 'pathname', 'process',
 'processName', 'relativeCreated', 'slug', 'stack_info', 'taskName', 'thread',
 'threadName']
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|---------------|--------|
| No logging anywhere in `src/`, `docker/` | Structured JSON via one root handler, configured at two idempotent call sites | This phase | A `503`, a `BuildError`, a cache hit vs. a 3-second build all become observable, proven by tests instead of console-reading (the debt file's own framing). |

**Deprecated/outdated:** N/A — nothing in this domain is being replaced; this is a
net-new capability on an otherwise unchanged stack.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The exact standard `LogRecord` attribute-name list is stable across the 3.10-3.12 floor this project targets (verified only against the installed 3.12.13 interpreter this session) | Pattern 2 / Don't Hand-Roll | Low — this is documented, long-stable stdlib behavior (Python's own "LogRecord attributes" table), not a recent addition; if it ever drifted, D-16's formatter round-trip test would catch a dropped/added key immediately at test time, before it reached production. |
| A2 | Placing the `worker_replaced()` call inside `recreate_for` (after the identity guard) rather than at the two `_run_with_timeout` call sites is the correct location to avoid double-counting | Pattern 4 | Medium — if wrong, a regression of the already-fixed CR-01/WR-01 double-count bug is possible; mitigated by the existing `test_two_same_slot_deaths_from_one_incident_replace_the_worker_once` test, which the planner should extend rather than replace. |

**If this table is empty:** N/A — two low/medium-risk assumptions remain, both about
*where* to place code (a design choice, not a fact about the world), and both mitigated
by existing tests that would catch the more serious failure mode.

## Open Questions

1. **Exact envelope key set beyond D-09-D-13's fixed fields**
   - What we know: `ts`, `level`, `logger`, `event` are needed at minimum (target shape
     in CONTEXT.md's `<specifics>`); D-13's `request` id; D-09's `event` name; D-10's
     `slug`/`params`; D-11's `fmt`/`quality`/`encoding`/`source`; D-12's `duration_ms`.
   - What's unclear: whether `exc_info`/traceback text rides on ERROR records, and
     whether `version` (the app version) rides on every record — both explicitly left to
     Claude's Discretion in CONTEXT.md.
   - Recommendation: include `version` (cheap, already available as `spur.__version__`,
     useful for correlating incidents across deploys) but leave `exc_info` off by default
     — D-06's own accepted cost is that the kernel's traceback is only available as text
     inside `BuildError`'s message already, so a second, separate traceback field would
     be redundant for `BuildError` and simply absent for `BuildTimeout`/`BrokenProcessPool`
     (which have no kernel traceback at all).

2. **New module's name and location**
   - What we know: not `spur/logging.py` (CONTEXT.md is explicit — shadows the stdlib
     name). Must be importable by both `cli.py` and `app.py` without reaching
     `cadquery`/`OCP` or `fastapi`/`starlette` (existing import-linter contracts,
     confirmed unchanged by reading `pyproject.toml`'s `[tool.importlinter]` this
     session).
   - What's unclear: exact name — left to Claude's Discretion in CONTEXT.md.
   - Recommendation: `spur/records.py` or `spur/observability.py` are both defensible;
     `records.py` reads well against D-17's framing ("one small function per event") and
     avoids any ambiguity with Python's own `logging` module or with `records` as a noun
     already meaning something else in this codebase (a targeted `grep -rn "records"
     src/` this session found no prior use of that name) — a mild preference, not a
     locked recommendation.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | `logging`, `uuid`, `time.monotonic` (all stdlib) | Yes | 3.12.13 (`.venv`); floor 3.10 per `pyproject.toml`, CI matrix runs both | — |
| uvicorn | `log_config=None` behavior, multiprocess spawn behavior | Yes | 0.53.0 (installed; `pyproject.toml` floor `>=0.30`) | — |

No missing dependencies; nothing in this phase touches Docker, a database, or any
network service.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | `pytest` 8+ (installed; `pyproject.toml` `dev` extra `pytest>=8`) |
| Config file | `pyproject.toml` `[tool.pytest.ini_options]` — `testpaths = ["tests"]`, `filterwarnings = ["error", ...]` (confirmed no warning surfaces from `caplog` usage in this session's probe) |
| Quick run command | `.venv/bin/python -m pytest tests/test_api.py tests/test_pool.py -q` |
| Full suite command | `make verify` (76 tests currently pass, confirmed this session: `.venv/bin/python -m pytest -q` → `76 passed in 29.02s`) |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|---------------------|-------------|
| REQ-structured-logging | `build.started` emitted with `slug`, `params` | unit/contract (`caplog`) | `pytest tests/test_api.py -k build_started -x` | ❌ Wave 0 — new test |
| REQ-structured-logging | `build.failed` emitted with exception-class field, for `BuildError`/`BuildTimeout`/`BrokenProcessPool` | unit/contract (`caplog`), parametrized like the existing `test_each_build_failure_mode_maps_to_its_own_status_and_type` | `pytest tests/test_api.py -k build_failed -x` | ❌ Wave 0 — new test, but the D-15 injectable `build_backend` pattern it reuses already exists |
| REQ-structured-logging | `export.served` emitted with `source` in `{cache, compressed, built}`, `duration_ms`, `fmt`, `quality`, `encoding` | unit/contract (`caplog`) | `pytest tests/test_api.py -k export_served -x` | ❌ Wave 0 — new test, three variants of `counting_backend`/`counting_gzip` patterns that already exist |
| REQ-structured-logging | `queue.refused` emitted with in-flight count, `MAX_QUEUED_BUILDS` | unit/contract (`caplog`), variant of `test_a_saturated_service_refuses_instead_of_queueing` | `pytest tests/test_api.py -k queue_refused -x` | ❌ Wave 0 — new test |
| REQ-structured-logging | `worker.replaced` emitted with slot index, cause | integration (`caplog` + real pool), variant of the existing wedge/die tests | `pytest tests/test_pool.py -k worker_replaced -x` | ❌ Wave 0 — new test, reuses `test_a_wedged_build_is_terminated_and_its_worker_replaced` / `test_a_dying_worker_surfaces_as_broken_pool_and_is_replaced` |
| REQ-structured-logging | JSON `Formatter` round-trips a record through `json.loads`, proving `extra` is not dropped | unit | `pytest tests/test_<new module>.py -x` | ❌ Wave 0 — new test file |
| REQ-structured-logging | `calc.py` stays log-free | static/negative check | `grep -rn "^import logging\|^from logging" src/spur/calc.py` (expect empty) — cheap enough to be a plain assertion in a test, not a manual step | ❌ Wave 0 — a one-line negative test is cheap insurance against drift |

### Sampling Rate
- **Per task commit:** `.venv/bin/python -m pytest tests/test_api.py tests/test_pool.py -q`
- **Per wave merge:** `make verify`
- **Phase gate:** Full suite green before `/gsd-verify-work`

### Wave 0 Gaps
- [ ] `tests/test_<new module>.py` — the formatter round-trip test, and any
  `SPUR_LOG_LEVEL` parsing tests (Pattern 3) — new file, no existing coverage of a
  logging module because none exists yet.
- [ ] Every D-16 branch test above needs a `caplog.set_level(logging.INFO)` (or
  `.at_level(...)`) call per Pitfall 1 — **not a missing file**, but a missing habit; the
  existing test suite has zero precedent for `caplog` usage (`grep -rn "caplog"
  tests/` returns nothing this session), so this is a genuinely new pattern for this
  codebase's test suite, not a copy of an existing fixture.
- [ ] No framework install needed — `pytest`'s `caplog` fixture is built in.

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-------------------|
| V2 Authentication | No | Out of scope — `REQ-no-auth-default` is a deliberate, separate decision (L-level, not this phase). |
| V3 Session Management | No | No sessions in this app. |
| V4 Access Control | No | No access-control surface touched by this phase. |
| V5 Input Validation | No (unchanged) | `GearParams`/`calc.check()` already validate at the model boundary (L03); this phase adds no new input surface — logged fields are all derived from already-validated `GearParams` or internal counters. |
| V6 Cryptography | No | Not applicable. |
| V7 Logging/Error Handling (custom addition — the phase's actual security-relevant category) | Yes | See below. |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|----------------------|
| Sensitive data landing in logs (secrets, PII, credentials) | Information Disclosure | CONTEXT.md is explicit: "Redact nothing sensitive because there is nothing sensitive" — this app has no auth, no user accounts, no secrets in its parameter model (`GearParams` fields are all dimensional numbers). Confirmed by reading `params.py`'s full field list this session: teeth, module, pressure angle, bore, recess dimensions — nothing that identifies a person or grants access. No redaction logic is needed as a result, but the planner should note this reasoning explicitly rather than silently assuming it, since it is the one place a "log everything" decision could go wrong in a different codebase. |
| Log injection via attacker-controlled values landing verbatim in log lines | Tampering | The JSON `Formatter` serializes fields as structured JSON values (not string-interpolated into a text template), so a value containing e.g. a newline or fake JSON cannot forge a second log line the way it could with a naive `f"{event} {field}"` text format. `params` values are numeric (validated `GearParams` fields, not free text), further limiting this surface. |
| Denial of service via log volume (an attacker driving high-cardinality or high-volume log lines) | Denial of Service | Out of scope for this phase by CONTEXT.md's own boundary ("Not in this phase: metrics, tracing, log shipping"); `MAX_QUEUED_BUILDS`/admission control (L04, unchanged) already bounds request volume independently of logging, so log volume is capped by the same mechanism that already caps build volume. |

## Sources

### Primary (HIGH confidence — verified this session against installed code/tools)
- `.venv/lib/python3.12/site-packages/uvicorn/config.py` — `Config.configure_logging()`,
  read in full this session (confirms D-02).
- `.venv/lib/python3.12/site-packages/uvicorn/_subprocess.py` and
  `.venv/lib/python3.12/site-packages/uvicorn/supervisors/multiprocess.py` — read in full
  this session (confirms D-05's assumption is false; spawn does not run `cli.cmd_serve`
  in the child).
- Live reproduction: `multiprocessing.get_context("spawn")` child vs. parent root-logger
  handler state, run this session.
- Live reproduction: `pytest` `caplog` default level (WARNING) vs. `caplog.set_level`, run
  this session.
- Live reproduction: `logging.getLevelName("INFO")` / `logging.getLevelName("NONSENSE")`,
  run this session.
- Live reproduction: `LogRecord.__dict__` key set via `Logger.makeRecord`, run this
  session.
- `src/spur/app.py`, `src/spur/pool.py`, `src/spur/cli.py`, `src/spur/build_errors.py`,
  `src/spur/params.py`, `src/spur/__init__.py` — read in full this session.
- `pyproject.toml` — read in full this session (ruff `LOG`/`G` selection, import-linter
  contracts, mypy strict config, pytest config, dependency list).
- `ruff rule G004`, `ruff rule LOG015`, `ruff rule G201` — fetched from the installed
  `ruff` 0.16.8 this session.
- `.venv/bin/python -m pytest -q` — 76 tests passing, run this session (baseline
  confirmed clean before planning).

### Secondary (MEDIUM confidence)
- None — every claim in this research was independently verified this session rather than
  taken from a secondary source.

### Tertiary (LOW confidence)
- None.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — stdlib only, no external library research needed; every claim
  checked against the installed interpreter/packages.
- Architecture: HIGH — the uvicorn/multiprocessing finding (D-05) was independently
  confirmed by source reading and a live reproduction, not assumed either way.
- Pitfalls: HIGH — all four pitfalls were reproduced live this session, not inferred.

**Research date:** 2026-09-24
**Valid until:** 30 days, or immediately if `uvicorn` is upgraded past `0.53.0` (the
spawn/logging behavior documented here should be re-checked against any major-version
bump, though it reflects a `multiprocessing.spawn` fundamental unlikely to change).
