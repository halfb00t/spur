# Phase 3: Structured Logging at the Composition Boundary - Pattern Map

**Mapped:** 2026-09-24
**Files analyzed:** 12 (2 new, 4 modified code, 6 docs/bookkeeping)
**Analogs found:** 12 / 12 (all files have a same-repo precedent; the new module has no
role-identical analog — see "No Analog Found" for its closest structural precedent)

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `src/spur/records.py` (new — name per RESEARCH.md Open Question 2; not `spur/logging.py`) | utility/config (log configuration + event emitters) | event-driven | `src/spur/build_errors.py` (kernel-free, dual-imported utility module) | role-match |
| `src/spur/app.py` (modified: `_build_slot`, `model()`, `lifespan()`) | controller (FastAPI route handlers) | request-response + event-driven | itself (pre-existing file, same file) | exact (editing in place) |
| `src/spur/pool.py` (modified: `recreate_for`, `_run_with_timeout`) | service (process-pool orchestration) | event-driven | itself (pre-existing file, same file) | exact (editing in place) |
| `src/spur/cli.py` (modified: `cmd_serve`) | route/entrypoint (composition root) | request-response | itself (pre-existing file, same file) | exact (editing in place) |
| `src/spur/__init__.py` (modified: add level-parsing sibling to `int_env`) | utility (env-var knob parsing) | transform | `int_env()` in the same file | exact |
| `tests/test_records.py` (new) | test | unit | `tests/test_pool.py`'s standalone-unit sections (`_BlobCache`-style, no app needed) — closest existing shape is actually `tests/test_api.py::test_the_export_cache_refuses_a_blob_bigger_than_its_budget` (a small pure-unit test against an internal class) | role-match |
| `tests/test_api.py` (modified: new `caplog` branch tests) | test | request-response | `test_each_build_failure_mode_maps_to_its_own_status_and_type` (parametrized branch test) + `test_a_saturated_service_refuses_instead_of_queueing` | exact |
| `tests/test_pool.py` (modified: extend wedge/die tests with `caplog`) | test | event-driven | `test_a_wedged_build_is_terminated_and_its_worker_replaced` / `test_a_dying_worker_surfaces_as_broken_pool_and_is_replaced` | exact |
| `docs/architecture/decision_log.md` (append `L20`) | config/doc | append-only log | `L19` entry (most recent, same append pattern) | exact |
| `docs/CODING_VALUES.md` §Logging, `docs/architecture/http-api.md` §Logging, `docs/architecture/solid-model/errors_and_logging.md` §Logging | doc | transform | `docs/architecture/gear-maths/errors_and_logging.md` §Logging (the one section that stays correct — shows the target prose shape) | role-match |
| `docs/tech_debt/active/2026-09-21-no-structured-logging.md` → `docs/tech_debt/resolved/` | doc (debt lifecycle) | transform | `docs/tech_debt/resolved/2026-09-21-cad-builds-block-the-event-loop.md` (the one prior resolved-debt file, same lifecycle) | exact |
| `docs/tech_debt/INDEX.md` (move one row) | doc | transform | its own "Resolved" table (one existing row already shows the target format) | exact |
| `README.md` (env-var table: add `SPUR_LOG_LEVEL` row) | doc | transform | the existing `SPUR_*` table rows (`SPUR_BUILD_TIMEOUT`, `SPUR_MAX_QUEUED_BUILDS`) | exact |

## Pattern Assignments

### `src/spur/records.py` (new module — utility/config, event-driven)

**No same-role analog exists** (this is the first logging module in the repo). Closest
structural precedent: `src/spur/build_errors.py` — a small, kernel-free module imported
by both `cli.py`/`app.py`-side code and worker-side code, whose own docstring explains
*why* it is split out to satisfy an import-boundary contract. `records.py` needs the same
justification (importable by `cli.py` and `app.py` without reaching `cadquery`/`OCP` or
`fastapi`).

**Docstring/why-comment pattern** (`src/spur/build_errors.py` lines 1-13):
```python
"""Build-failure exception types, kept free of the CAD kernel on purpose.

`app.py` has to name a build failure (to map it to a 422) without importing `cadquery` --
the serving process is not allowed to reach the kernel by any path (D-02). Splitting these
two exceptions out of `model.py` is what makes that possible: ...
```
Model `records.py`'s module docstring the same way: state *why* it is a separate module
(the import-linter contracts `spur.calc`/`spur.params`/`spur.cli` forbid `cadquery`/`OCP`,
and `spur.app` forbids it even indirectly — `pyproject.toml` lines 127-162), not just what
it contains.

**Env-var knob pattern to copy** (`src/spur/__init__.py` lines 8-13, `int_env`):
```python
def int_env(name: str, default: int) -> int:
    """A positive integer setting from the environment, falling back on nonsense."""
    try:
        return max(1, int(os.environ.get(name) or default))
    except ValueError:
        return default
```
`SPUR_LOG_LEVEL`'s parser (D-14, RESEARCH.md Pattern 3) is a string sibling of this shape:
same "read once, fall back to a named default on nonsense" contract, but validated via
`logging.getLevelName(name.upper())` + `isinstance(..., int)` rather than `int()` +
`except ValueError`. Per RESEARCH.md Pattern 3, do **not** use `logging._nameToLevel`
(private) or `logging.getLevelNamesMapping()` (3.11+ only — floor is 3.10).

**Idempotent configure() and JSON Formatter — from RESEARCH.md Pattern 1/2 (verified this
session against installed uvicorn 0.53.0 / Python 3.12.13, not from memory):**
```python
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
Call sites (RESEARCH.md's falsified-assumption finding, D-05): **both**
`cli.cmd_serve` (before `uvicorn.run(..., log_config=None)`) **and** the top of
`app.py`'s `lifespan()` startup — the only path that reaches every spawned uvicorn
worker when `SPUR_WORKERS>1`. The guard above is what keeps the common
`SPUR_WORKERS=1` case (both call sites run in the same process) from installing two
stderr handlers.

**Comment-carries-the-measurement pattern to match** (project convention, see
`src/spur/app.py` lines 146-168's `_GZIP_LEVEL` comment, and `src/spur/pool.py` lines
73-85's memory-sweep comment): every knob in `records.py` (the level default, the stderr
choice, the standard-`LogRecord`-attribute exclusion set) needs a comment citing the
concrete verification, e.g. cite RESEARCH.md's live reproduction of
`LogRecord.__dict__`'s key set (`['args', 'created', 'event', 'exc_info', 'exc_text',
'filename', 'funcName', 'levelname', 'levelno', 'lineno', 'module', 'msecs', 'msg',
'name', 'pathname', 'process', 'processName', 'relativeCreated', 'slug', 'stack_info',
'taskName', 'thread', 'threadName']`) as a single module-level frozenset both the
formatter and its round-trip test reference — not re-derived by eye in two places
(RESEARCH.md "Don't Hand-Roll").

**Five per-event functions (D-17):** `build_started(...)`, `build_failed(...)`,
`export_served(...)`, `queue_refused(...)`, `worker_replaced(...)` — each a
mypy-checked, intent-named signature that wraps a `logger.info(event, extra={...})` /
`logger.warning(...)` / `logger.error(...)` call at the correct D-15 level. Use
`logging.getLogger(__name__)`, never bare `logging.info(...)` module-level calls (ruff
`LOG015`, confirmed selected in `pyproject.toml`). Never an f-string in the message
argument (ruff `G004`, already selected) — pass structured fields via `extra=` only.

---

### `src/spur/app.py` (controller, request-response + event-driven)

**Analog:** itself — this is an in-place edit to existing branches, not a new file. The
"pattern to copy" is the file's own existing branch structure; `records.py`'s helpers
slot into branches that already exist, per D-06/D-08.

**Import pattern to add** (matches the existing import block, `src/spur/app.py` lines
14-36 — stdlib first, then third-party, then local with `from . import`):
```python
from . import __version__, int_env
from .build_errors import BuildError, BuildTimeout
```
Add `from .records import build_failed, build_started, export_served, queue_refused` in
the same local-import group (alphabetical among `.records`/`.pool` per the existing
ordering), plus `import time` and `import uuid` in the stdlib group.

**`queue_refused()` call site — `_build_slot()`** (`src/spur/app.py` lines 220-246,
specifically the single refusal branch at lines 233-240):
```python
    global _in_flight_builds
    if not BUILD_QUEUE.acquire(blocking=False):
        raise HTTPException(
            503,
            detail=[{"loc": ["query"], "type": "busy",
                     "msg": f"Busy: {MAX_QUEUED_BUILDS} gears are already being built or "
                            "compressed. Try again in a moment."}],
            headers={"Retry-After": "5"},
        )
```
`_in_flight_builds` and `MAX_QUEUED_BUILDS` are already in scope here (module-level,
lines 95, 105) — `queue_refused(in_flight=_in_flight_builds, max_queued=MAX_QUEUED_BUILDS)`
belongs immediately before the `raise`.

**`build.started`/`build.failed`/`export.served` + `request`/`duration_ms` — `model()`**
(`src/spur/app.py` lines 311-383). The three `source` branches already exist exactly as
D-11 describes:
```python
    data = _EXPORTS.get(key)
    if data is None:
        try:
            with _build_slot():
                raw_key = (params, fmt, q.quality, "identity")
                raw = _EXPORTS.get(raw_key)
                if raw is None:
                    raw = await backend(params, fmt, q.quality)   # source="built"
                    _EXPORTS.put(raw_key, raw)
                if wants_gzip:
                    data = await run_in_threadpool(_gzip, raw)    # source="compressed"
                    _EXPORTS.put(key, data)
                else:
                    data = raw
        except BuildError as exc:
            raise HTTPException(422, ...) from exc
        except BuildTimeout as exc:
            raise HTTPException(503, ...) from exc
        except BrokenProcessPool as exc:
            raise HTTPException(503, ...) from exc
```
`data = _EXPORTS.get(key)` returning non-`None` *before* the `if data is None:` block is
`source="cache"` — never enters `_build_slot()`, so `duration_ms=0` by construction
(RESEARCH.md Pattern 5). Per D-13, mint `request = uuid.uuid4().hex[:8]` as the first
line of `model()`. Per RESEARCH.md Pattern 5, start `time.monotonic()` immediately before
`with _build_slot():` and read the elapsed time in each of the three `except` clauses
(for `build_failed`'s `duration_ms`) and after the `with` block exits (for
`export_served`'s `duration_ms`) — a `try/finally`-timed duration is readable from both
paths.

**Exception-class field for `build_failed`:** `type(exc).__name__` at each of the three
`except` clauses — `BuildError`, `BuildTimeout`, `BrokenProcessPool` are already the
literal class names D-08 wants; no new mapping needed.

**`lifespan()` idempotent second `configure()` call** (`src/spur/app.py` lines 114-137):
```python
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Build the pool eagerly at startup, tear it down at shutdown (D-04).
    ...
    """
    app.state.pool = BuildPool(
        int_env("SPUR_BUILD_WORKERS", 2),
        int_env("SPUR_BUILD_TIMEOUT", 30),
    )
```
Add `configure(int_env... )` — actually `configure(os.environ.get("SPUR_LOG_LEVEL", ...))`
via the new string-env helper — as the first line inside `lifespan()`, before
`app.state.pool = BuildPool(...)`. This is the call site RESEARCH.md's falsified
assumption (D-05) makes mandatory, not optional: it is the only code that runs inside
every spawned `SPUR_WORKERS>1` uvicorn child.

**Error-handling pattern already established** (three `except` clauses, lines 344-374):
each already builds a `detail=[{"loc": ..., "msg": ..., "type": ...}]` HTTPException —
`build_failed()`'s call goes *inside* each of these three blocks, before or after the
`raise HTTPException(...)`, since D-06 says "either side of `pool.export` as long as they
see the exception class and the slot" is fine.

---

### `src/spur/pool.py` (service, event-driven)

**Analog:** itself — in-place edit to `recreate_for` and `_run_with_timeout`.

**Import pattern to add** (matches existing local-import group,
`src/spur/pool.py` lines 30-31):
```python
from .build_errors import BuildTimeout
from .params import GearParams
```
Add `from .records import worker_replaced` in the same group.

**`cause` threading pattern (RESEARCH.md Pattern 4, verified line offsets):**
```python
    def recreate_for(self, p: GearParams, executor: ProcessPoolExecutor, cause: str) -> None:
        i = hash(p) % self.workers
        if self._executors[i] is not executor:
            return  # someone else already replaced this slot for this incident
        ...
        self._executors[i].shutdown(wait=False)
        self._executors[i] = ProcessPoolExecutor(
            max_workers=1, mp_context=_SPAWN, initializer=_warm)
        self.replaced += 1
        worker_replaced(slot=i, cause=cause)   # NEW — inside the identity guard,
                                                # after self.replaced += 1 (line 140)
```
The two call sites to update (`src/spur/pool.py` lines 185 and 197):
```python
            self.recreate_for(p, executor, cause="timeout")       # was line 185
            ...
            self.recreate_for(p, executor, cause="broken_pool")   # was line 197
```
**Do not** call `worker_replaced()` at either call site directly (RESEARCH.md Pitfall 4)
— it must live inside `recreate_for`'s identity guard (line 110, `if self._executors[i]
is not executor: return`), immediately after `self.replaced += 1` (line 140), so a
duplicate same-slot caller never double-logs the way `CR-01`/`WR-01` once double-counted
(the docstring at lines 94-113 documents the original bug this guard fixed;
`tests/test_pool.py::test_two_same_slot_deaths_from_one_incident_replace_the_worker_once`
is the regression test the log-record assertion must extend).

---

### `src/spur/cli.py` (composition root, request-response)

**Analog:** itself — `cmd_serve` in place.

**Current shape to extend** (`src/spur/cli.py` lines 46-50):
```python
def cmd_serve(ns: argparse.Namespace) -> None:
    import uvicorn

    uvicorn.run("spur.app:app", host=ns.host, port=ns.port, workers=ns.workers,
                root_path=ns.root_path, proxy_headers=True)
```
Add, per D-05:
```python
def cmd_serve(ns: argparse.Namespace) -> None:
    import uvicorn

    from .records import configure
    configure(os.environ.get("SPUR_LOG_LEVEL", "INFO"))
    uvicorn.run("spur.app:app", host=ns.host, port=ns.port, workers=ns.workers,
                root_path=ns.root_path, proxy_headers=True, log_config=None)
```
`log_config=None` is the D-02 change verified true by RESEARCH.md (reading installed
`uvicorn.config.Config.configure_logging()` — gated entirely behind
`if self.log_config is not None:`). `os` is already imported at module level
(`src/spur/cli.py` line 10); the local `import uvicorn` inside the function is the
existing pattern for a deferred/optional import — `from .records import configure` can
follow the same local-import style, or be hoisted to the top-level import block
alongside `from .params import GearParams` (line 18) — Claude's Discretion, either is
consistent with the file's existing mixed style (top-level `.params` import,
function-local `uvicorn`/`.build_errors`/`.calc`/`.model` imports at lines 47, 64-66).

**Per D-07, `cmd_info`/`cmd_export` (lines 53-80) are explicitly unchanged** — do not add
`configure()` calls there; their existing stderr prose (`print(..., file=sys.stderr)` at
lines 42, 78, 80) stays as-is.

---

### `src/spur/__init__.py` (utility, transform)

**Analog:** `int_env` in the same file (lines 8-13, reproduced above under `records.py`).
The `SPUR_LOG_LEVEL` parser is Claude's Discretion to place either here (as a direct
sibling of `int_env`, importable the same way) or inside `records.py` itself
(`_parse_level`, per RESEARCH.md Pattern 3's example, which keeps the `logging`-specific
validation next to the module that owns `logging` entirely). RESEARCH.md's own example
names it `_parse_level` inside the new module; `int_env`'s existing "nonsense falls back
to default" *shape* is what must be matched regardless of which file it lives in.

---

### `tests/test_records.py` (new — test, unit)

**No existing test file for a logging module** (RESEARCH.md: `grep -rn "caplog" tests/`
returns nothing — this is a genuinely new pattern for the suite). Closest shape:
`tests/test_api.py`'s small pure-unit test against an internal class,
`test_the_export_cache_refuses_a_blob_bigger_than_its_budget` (lines 147-152):
```python
def test_the_export_cache_refuses_a_blob_bigger_than_its_budget() -> None:
    """A _BlobCache never reports a stored size above its budget (D-06)."""
    from spur import app as app_module

    cache = app_module._BlobCache(budget=10)
    cache.put("fits", b"12345")
    assert cache.get("fits") == b"12345"

    cache.put("too_big", b"x" * 20)
    assert cache.get("too_big") is None
```
Match this "requirement-shaped name, import the module under test, construct/call
directly, assert the contract" structure for: the formatter round-trip test (build a
`LogRecord` via `logging.Logger.makeRecord`, format it, `json.loads` the line, assert
`extra` fields survived), and any `SPUR_LOG_LEVEL` parsing tests (valid name → int,
nonsense → `INFO` fallback, mirroring how `tests/test_api.py`'s
`test_max_queued_builds_is_derived_from_build_workers` (lines 130-144) drives
`int_env`-derived values via `monkeypatch.setenv`/`delenv`).

**`caplog` pitfall to encode into every branch test (RESEARCH.md Pitfall 1, verified live
this session):** `caplog` defaults to WARNING; every test asserting an INFO-level record
(`build.started`, `export.served`) must call `caplog.set_level(logging.INFO)` first, and
should assert `caplog.records` is non-empty as well as its contents — a missing
`set_level` produces a false-green test that would pass even if the code never logged.

**One-line negative test for `calc.py` staying log-free** (REQ's own acceptance line,
RESEARCH.md Test Map): a plain `grep`-equivalent assertion, e.g.
```python
def test_calc_stays_log_free() -> None:
    import re
    from pathlib import Path
    text = Path(spur.calc.__file__).read_text()
    assert not re.search(r"^\s*(import logging|from logging)", text, re.MULTILINE)
```
placed in `tests/test_records.py` (or `tests/test_calc.py` if one already covers
`calc.py`'s other boundary properties — check before adding a new file for one
assertion).

---

### `tests/test_api.py` (modified — test, request-response)

**Analog:** `test_each_build_failure_mode_maps_to_its_own_status_and_type` (lines
163-190) for the `build_failed` branches, and
`test_a_saturated_service_refuses_instead_of_queueing` (lines 113-127) for
`queue_refused`. Both already drive the exact branches D-16 needs via the injected
`build_backend` (see excerpts above under `pool.py`'s test file, same pattern reused
here). New tests should follow the same `from spur import app as app_module`,
override-dependency-in-`try`/`finally`, parametrize-by-exception-type shape. Each needs
`caplog.set_level(...)` per the Pitfall 1 note above, and must assert the **literal**
event-name string (`"build.failed"`, `"queue.refused"`, `"export.served"`) and field
names per D-16 ("Names are chosen once, in code ... Tests assert the literal strings, so
a rename is a deliberate test change").

**`export.served` `source` variants** — reuse `counting_backend`
(`test_a_second_identical_download_is_served_from_the_byte_cache`, lines 159-179) and
`counting_gzip` (`test_a_gear_is_compressed_once_per_cache_fill_not_once_per_download`,
lines 206-227) patterns to drive `source="built"`, `source="compressed"`, and a plain
repeat `client.get(...)` to drive `source="cache"`.

---

### `tests/test_pool.py` (modified — test, event-driven)

**Analog:** `test_a_wedged_build_is_terminated_and_its_worker_replaced` (lines 114-144)
and `test_a_dying_worker_surfaces_as_broken_pool_and_is_replaced` (lines 146-159) — both
already drive `recreate_for` through a real pool/real subprocess. The `worker_replaced`
assertion (slot index, `cause`) attaches to these existing tests (add
`caplog.set_level(logging.ERROR)` and assert on `caplog.records` inside the existing
`with TestClient(app):` block) rather than writing new end-to-end tests — per D-16's own
instruction ("the existing real-pool wedge test for `worker.replaced`").

**Regression guard to extend, not replace:**
`test_two_same_slot_deaths_from_one_incident_replace_the_worker_once` (lines 423-444) —
add a `caplog` record-count assertion (`== 1`, not `== 2`) alongside the existing
`pool.replaced == replaced_before + 1` assertion, per RESEARCH.md Pitfall 4's own
recommendation.

---

## Shared Patterns

### Kernel-free / import-boundary discipline
**Source:** `pyproject.toml` lines 117-162 (`[tool.importlinter]` contracts),
`src/spur/build_errors.py` lines 1-13 (docstring explaining the boundary)
**Apply to:** `records.py` (new module), and every call site in `app.py`/`pool.py`/`cli.py`
```toml
[[tool.importlinter.contracts]]
name = "The gear maths stays free of the CAD kernel"
type = "forbidden"
source_modules = ["spur.calc", "spur.params", "spur.cli"]
forbidden_modules = ["cadquery", "OCP"]
allow_indirect_imports = true

[[tool.importlinter.contracts]]
name = "The serving process never imports the CAD kernel"
type = "forbidden"
source_modules = ["spur.app"]
forbidden_modules = ["cadquery", "OCP"]
allow_indirect_imports = false
```
No new contract is needed — `records.py` must simply never import `cadquery`/`OCP` or
`fastapi`/`starlette`/`spur.app`, so the four existing contracts pass unchanged.

### Comment-carries-the-measurement (`docs/CODING_VALUES.md` standard; see also
`CLAUDE.md` "Code style")
**Source:** `src/spur/app.py` lines 146-168 (`_GZIP_LEVEL`'s measured table),
`src/spur/pool.py` lines 73-85 (memory-sweep comment)
**Apply to:** every knob `records.py` introduces (default level, stderr stream choice,
the standard-`LogRecord`-attribute-name frozenset) and every new call site's rationale
comment (why this branch emits this event at this level).

### Error-response shape (`detail=[{"loc": ..., "msg": ..., "type": ...}]`, `Retry-After`)
**Source:** `src/spur/app.py` lines 233-240, 344-374
**Apply to:** unchanged by this phase — `build_failed`/`queue_refused` observe these
existing HTTPException branches, they do not alter their shape (D-08: "branches that
already exist, not new capability").

### ruff `LOG`/`G` rule enforcement (already selected, polices call sites for free)
**Source:** `pyproject.toml` `[tool.ruff.lint]` (confirmed selected this session per
RESEARCH.md; `G004` no-f-string-in-log-call, `LOG015` no-root-logger-calls)
**Apply to:** `records.py`'s five per-event functions — always
`logging.getLogger(__name__)`, never bare `logging.info(...)`; always `extra=`/`%s`
substitution, never an f-string in a log call.

### `filterwarnings = error` + `caplog` (new to this suite)
**Source:** `pyproject.toml` `[tool.pytest.ini_options]`
**Apply to:** every D-16 branch test — confirmed clean this session (RESEARCH.md: "clean
— no warning surfaces from caplog usage"), but every new test must call
`caplog.set_level(...)` explicitly per Pitfall 1, since `caplog`'s default WARNING floor
would otherwise silently produce an empty-but-passing test for every INFO-level event.

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `src/spur/records.py` | utility/config | event-driven | First logging module in the repo — no same-role, same-data-flow analog exists. `src/spur/build_errors.py` is the closest structural precedent (small, dual-imported, kernel-free module with a why-focused docstring) but is a data-shape module (exception classes), not a configuration/emission module. RESEARCH.md's Patterns 1-5 and Code Examples (verified against the installed `.venv`) are the primary source for this file's actual content; use them directly rather than searching further for a same-shape analog. |

## Metadata

**Analog search scope:** `src/spur/` (all 6 non-test modules read in full or via targeted
`grep`+`Read`), `tests/test_api.py` (full, 272 lines), `tests/test_pool.py` (full read of
lines 1-210, `grep` for remaining structure), `docs/architecture/decision_log.md` (tail +
L03/L04/L05/L19 excerpts), `docs/tech_debt/` (both active and resolved directories),
`docs/CODING_VALUES.md`, `docs/architecture/http-api.md`,
`docs/architecture/solid-model/errors_and_logging.md`,
`docs/architecture/gear-maths/errors_and_logging.md`, `docs/architecture/cli.md`,
`README.md`, `pyproject.toml` (`[tool.importlinter]`, referenced for the shared pattern).
**Files scanned:** 18 (12 classified + 6 read only for shared-pattern/lifecycle context:
`docs/architecture/decision_log.md`, `docs/tech_debt/resolved/2026-09-21-cad-builds-block-the-event-loop.md`,
`docs/architecture/cli.md`, and three `§Logging` doc sections already counted above).
**Pattern extraction date:** 2026-09-24
**Tracked-source gate:** every path cited above was verified with `git ls-files --
<path>` this session; all print (tracked, not a gitignored mirror). No `.gsd/`,
`capabilities/`, or plugin-mirror paths appear anywhere in this document.
