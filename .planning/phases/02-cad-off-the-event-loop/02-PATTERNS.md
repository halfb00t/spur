# Phase 2: CAD Off the Event Loop - Pattern Map

**Mapped:** 2026-09-22
**Files analyzed:** 12 (5 edited source, 1 new source module, 1 new test set, 1 new bench
harness + Makefile wiring, 4 docs/config)
**Analogs found:** 10 / 12 (bench harness and the kernel-free `BuildError` module have no
in-tree analog of the same shape; both are still classified below with the closest partial
match and a "no analog" note)

All analog paths below were confirmed git-tracked with `git ls-files -- <path>`; none are
gitignored mirrors. This is a single-package repo with no plugin/capability mirror
directories, so the tracked-source gate is trivially satisfied for every entry.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `src/spur/build_errors.py` (NEW) | model/utility (exception type) | n/a (no I/O) | `src/spur/model.py:42-43` (`BuildError`'s current definition, being extracted) | partial — extraction, not a new shape |
| `src/spur/app.py` (EDITED — pool lifecycle, routing, health, failure mapping) | controller + provider (pool lifecycle) | request-response | itself (`src/spur/app.py`, pre-phase) | exact — same file, same role, extending its own patterns |
| `src/spur/model.py` (EDITED — drop `BuildError` def, keep `export()` surface) | service (CAD kernel wrapper) | CRUD (solid cache) + file-I/O (export) | itself (`src/spur/model.py`, pre-phase) | exact |
| `src/spur/cli.py` (EDITED — import path for `BuildError` only) | CLI entry point | request-response (in-process, no pool) | itself (`src/spur/cli.py`, pre-phase) | exact |
| `pyproject.toml` `[tool.importlinter]` (EDITED — new contract) | config | n/a | the three existing contracts in the same file, `pyproject.toml:121-146` | exact |
| `compose.yaml` (EDITED — `SPUR_WORKERS`, `SPUR_BUILD_WORKERS`, `mem_limit`) | config | n/a | itself (`compose.yaml`, pre-phase) | exact |
| `Dockerfile` (EDITED — `HEALTHCHECK --timeout`, comment) | config | n/a | itself (`Dockerfile`, pre-phase) | exact |
| `tests/test_api.py` (EDITED — D-09 sizing, NEW: e2e pool test, 3 failure-mode tests) | test | request-response | itself (`tests/test_api.py`, pre-phase) + `tests/test_model.py` for build/export assertions | exact |
| `bench/` harness (NEW, name/location at discretion) + `make bench` | utility/script (measurement) | batch (load gen) + event-driven (memory sweep) | `docker/smoke.py` (raw-ASGI HTTP-call pattern) + `Makefile`'s `smoke`/`up`/`test-image` targets (docker-driven `make` target shape) | partial — no committed harness exists yet; methodology precedent is prose in `docs/plan-2026-09-21.md`, not code |
| `Makefile` (EDITED — add `bench` target) | config/build script | n/a | `smoke:`, `up:`, `test-image:` targets, `Makefile:73-95` | exact |
| `docs/architecture/decision_log.md` (EDITED — append L17, L18) | docs | n/a | `L06`/`L07` entries, `docs/architecture/decision_log.md:57-73` | exact |
| `docs/tech_debt/active/2026-09-21-cad-builds-block-the-event-loop.md` → `resolved/` + `docs/tech_debt/INDEX.md` row move | docs (lifecycle move) | n/a | `docs/tech_debt/TEMPLATE.md` + `INDEX.md`'s existing Active table row shape (no prior resolved-file example exists — "Resolved: (none yet)") | partial — first-ever resolution, no prior `git mv` to mimic in this repo |

## Pattern Assignments

### `src/spur/build_errors.py` (NEW — model/utility)

**Analog:** `src/spur/model.py` lines 42-43 (the code being extracted, verbatim)

**What to copy — the class itself, unchanged:**
```python
# Source: src/spur/model.py:42-43 (current location, to be moved)
class BuildError(RuntimeError):
    """The CAD kernel could not produce a valid solid for these parameters."""
```

**Module docstring convention to match** (every module in this repo opens with a one-line
purpose + a "why" paragraph, e.g. `model.py:1-9`, `params.py:1-6`, `app.py:1-12`):
```python
# Source: src/spur/model.py:1-9 — the docstring shape to follow
"""CadQuery solid construction and STL/STEP export.

OpenCascade isn't safe to drive from several threads at once, so every kernel call goes
through one lock. ...
"""
```
The new module's docstring should say *why* it exists apart from `model.py` — D-02's
reason: `app.py` needs to name `BuildError` without importing `cadquery`. One sentence,
in the file, not just in the plan.

**No analog found for the module's placement/shape itself** — this repo has never split
an exception class into its own file before. The plan should treat this as a mechanical
extraction (move the class, update the two importers: `app.py` and `cli.py`), not as a
pattern lookup.

---

### `src/spur/app.py` (EDITED — controller + pool lifecycle provider)

**Analog:** itself, pre-phase (`src/spur/app.py`, all 124 lines read this session)

**Imports pattern** (lines 14-31, current) — path-relative imports, `from __future__ import
annotations`, stdlib first, third-party (`fastapi`, `pydantic`) second, project-local last:
```python
from __future__ import annotations

import threading
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Annotated, Any, Literal

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import Field

from . import __version__, int_env
from .calc import derive, with_mate
from .model import BuildError, export          # <-- D-02 removes this line entirely
from .params import GearParams
```
Post-D-02, `BuildError` comes from `.build_errors` instead, and `export` is no longer
imported at all in `app.py` — it is called only inside a worker process, never directly
by the parent (D-05).

**Admission-control / bounded-queue pattern to reuse for the new refusal modes** (D-12),
copied near-verbatim (lines 36-39, 70-84):
```python
# Source: src/spur/app.py:36-39
MAX_QUEUED_BUILDS = int_env("SPUR_MAX_QUEUED_BUILDS", 4)   # D-09: derive from SPUR_BUILD_WORKERS instead
BUILD_QUEUE = threading.BoundedSemaphore(MAX_QUEUED_BUILDS)

# Source: src/spur/app.py:70-84
@contextmanager
def _build_slot() -> Iterator[None]:
    """Admission control: refuse work we cannot start soon rather than queue it."""
    if not BUILD_QUEUE.acquire(blocking=False):
        raise HTTPException(
            503,
            detail=[{"loc": ["query"], "type": "busy",
                     "msg": f"Busy: {MAX_QUEUED_BUILDS} gears are already being built. "
                            "Try again in a moment."}],
            headers={"Retry-After": "5"},
        )
    try:
        yield
    finally:
        BUILD_QUEUE.release()
```
D-12's two new refusal modes (`BrokenProcessPool`, timeout) reuse this exact `503` +
`Retry-After` + `detail[].type` shape — same `loc`/`msg`/`type` keys, new `type` values
(e.g. `"pool_broken"`, `"timeout"`), not a new response contract.

**Error-mapping pattern to extend** (lines 112-119) — the existing `BuildError → 422` map
is the template for the two new `except` clauses D-12 adds:
```python
# Source: src/spur/app.py:112-119
@app.get("/api/model.{fmt}", response_class=Response, ...)
def model(fmt: Literal["stl", "step"], q: Annotated[ModelQuery, Query()]) -> Response:
    params = _gear(q)
    try:
        with _build_slot():
            data = export(params, fmt, q.quality)
    except BuildError as exc:
        raise HTTPException(422, detail=[{"loc": ["query"], "msg": str(exc),
                                          "type": "build_error"}]) from exc
    return Response(...)
```
This endpoint becomes `async def`, `export(...)` becomes `await loop.run_in_executor(...)`
per RESEARCH.md Pattern 1/2, and the `try` grows `except BrokenProcessPool` and
`except TimeoutError` clauses following the `_build_slot` 503 shape above, not the 422 shape.

**`int_env` pattern for every new knob** (`SPUR_BUILD_WORKERS`, `SPUR_BUILD_TIMEOUT`) —
copy exactly, from `src/spur/__init__.py:8-13`:
```python
# Source: src/spur/__init__.py:8-13 — verbatim, this is the established knob pattern
def int_env(name: str, default: int) -> int:
    """A positive integer setting from the environment, falling back on nonsense."""
    try:
        return max(1, int(os.environ.get(name) or default))
    except ValueError:
        return default
```

**`/api/health` pattern to extend** (lines 92-94) — currently trivial, D-13 adds pool
counters as plain attribute reads, same dict-literal shape:
```python
# Source: src/spur/app.py:92-94, current
@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": __version__}
```
D-13 changes the return type to `dict[str, object]` (mixed str/int fields) and adds
`build_workers`, `queue_available`, `workers_replaced` — see RESEARCH.md's Code Examples
section for the exact field shape; no new pattern needed, just more keys in the same
literal dict.

**Lifespan/pool wiring — no in-repo analog** (this app has never had a `lifespan=` before);
use RESEARCH.md's `Pattern 1: Lifespan-managed, affinity-routed process pool` verbatim as
the starting shape (`asynccontextmanager` + `app.state.pool`), since nothing in this
codebase does async context-managed startup/shutdown today.

---

### `src/spur/model.py` (EDITED — service, worker-side entry point)

**Analog:** itself, pre-phase (all 317 lines read this session)

**What changes:** only the `BuildError` definition moves out (lines 42-43 deleted, replaced
by `from .build_errors import BuildError`, or re-exported for backward compatibility if the
plan wants `model.BuildError` to keep working for any lingering importers). `export()`'s
signature and body (lines 309-317) are the D-05 boundary function and **do not change
shape** — they simply now execute inside a worker process instead of the parent:
```python
# Source: src/spur/model.py:309-317 — the exact function that crosses the process
# boundary under D-05; signature and body stay as-is, only *where* it runs changes.
def export(p: GearParams, fmt: Format, quality: Quality = "fine") -> bytes:
    key = (p, fmt, quality)
    with _LOCK:
        data = _EXPORTS.get(key)
        if data is None:
            data = _write_export(_build_cached(p), p, fmt, quality)
            _EXPORTS.put(key, data)
            _release_arenas()
        return data
```

**Cache-bound pattern already in the right shape for D-06's `_BlobCache` relocation**
(lines 265-294) — moves to `app.py` essentially unchanged per CONTEXT.md's Reusable
assets note:
```python
# Source: src/spur/model.py:265-294 — moves into app.py under D-06, keyed on
# (params, fmt, quality) exactly as it is keyed here today.
class _BlobCache:
    """LRU of exported bytes bounded by total size rather than by entry count.

    Callers hold _LOCK, so this needs no lock of its own.
    """
    def __init__(self, budget: int) -> None: ...
    def get(self, key: Any) -> bytes | None: ...
    def put(self, key: Any, data: bytes) -> None: ...
```
Note the docstring's "callers hold `_LOCK`" claim stops being true once `_BlobCache` moves
to the parent process (D-06) — the parent has no `_LOCK`, and doesn't need one since the
byte cache is now the *only* thing touching that dict, single-threaded under one uvicorn
worker (D-01). The moved class's docstring should be corrected, not carried over verbatim.

**`_release_arenas`/`malloc_trim` pattern — stays exactly as-is** (lines 46-69), just now
runs inside each worker instead of the single server process (D-11); no code change, only
a change of which process calls it:
```python
# Source: src/spur/model.py:58-69 — unchanged by this phase, per D-11
def _release_arenas() -> None:
    """Hand freed heap back to the operating system after a build. ..."""
    if _MALLOC_TRIM is not None:
        _MALLOC_TRIM(0)
```

**`_LOCK` pattern — stays exactly as-is** (line 39, D-08): `_LOCK = threading.RLock()`.
Uncontended under one-task-per-worker; no change.

---

### `src/spur/cli.py` (EDITED — import path only)

**Analog:** itself, pre-phase (all 114 lines read this session)

**The only change:** line 65's import moves `BuildError` to the new module while `export`
stays imported from `model` directly (L04: the CLI never queues, never touches the pool):
```python
# Source: src/spur/cli.py:63-77, current
def cmd_export(ns: argparse.Namespace) -> None:
    from .calc import derive
    from .model import BuildError, Format, export      # <-- BuildError's import changes

    out: Path = ns.output
    ...
    try:
        data = export(p, cast("Format", fmt), ns.quality)   # the check above is the proof
    except BuildError as exc:
        raise SystemExit(f"error: {exc}") from None
    ...
```
Becomes `from .build_errors import BuildError` + `from .model import Format, export` (two
lines instead of one), everything else in the function is untouched. This is the exact
place D-15's "CLI still takes the in-process path" claim is proven: `export()` is called
directly, no `app.state.pool`, no `run_in_executor`.

---

### `pyproject.toml` `[tool.importlinter]` (EDITED — new contract)

**Analog:** the three existing contracts in the same file, `pyproject.toml:121-146`

**Pattern to copy exactly** (contract table shape, comment-above-source_modules convention):
```toml
# Source: pyproject.toml:139-146 — closest existing contract in shape (a "CLI must not
# reach into a policy layer" rule); D-02's new contract is the same shape inverted.
[[tool.importlinter.contracts]]
name = "The CLI does not inherit web-serving policy"
# Admission control (the bounded build queue) is a property of serving HTTP, not of
# building a gear -- see L04. A CLI export must never queue behind anything.
type = "forbidden"
source_modules = ["spur.cli"]
forbidden_modules = ["spur.app", "fastapi", "starlette"]
allow_indirect_imports = true
```
D-02's new contract flips `allow_indirect_imports` to `false` and targets `spur.app`:
```toml
# New contract (D-02) — same table shape as above, name/comment/values only
[[tool.importlinter.contracts]]
name = "The serving process never imports the CAD kernel"
# app.py stops importing model.py under D-02: builds happen in worker processes only.
# allow_indirect_imports = false makes this enforced through any transitive path too,
# not just a direct `import cadquery` in app.py itself.
type = "forbidden"
source_modules = ["spur.app"]
forbidden_modules = ["cadquery", "OCP"]
allow_indirect_imports = false
```
Note the existing "gear maths stays free of the CAD kernel" contract
(`pyproject.toml:127-137`) already lists `spur.app` in `source_modules` with
`allow_indirect_imports = true` — that contract's reasoning ("reaching the kernel *through*
model.py is the whole point") is exactly what D-02 revokes for `app.py` specifically. The
plan should either narrow that existing contract's `source_modules` to drop `spur.app`, or
note explicitly why both contracts coexist (the new one is strictly tighter for `spur.app`
alone).

---

### `compose.yaml` (EDITED — env vars, `mem_limit`)

**Analog:** itself, pre-phase (all 26 lines read this session)

**Pattern to copy — the measured-comment convention** (lines 9-17), every numeric knob in
this file carries the measurement that set it; the new `mem_limit` comment must do the same:
```yaml
# Source: compose.yaml:9-17, current
environment:
  SPUR_WORKERS: "2"
  # SPUR_ROOT_PATH: /spur   # when served under a sub-path by a reverse proxy
  # SPUR_SOLID_CACHE, SPUR_EXPORT_CACHE_MB, SPUR_MAX_QUEUED_BUILDS: see the README
# Sized by measurement, not by guess: two workers sweeping 40 distinct 160-199
# tooth gears settle at ~740 MB resident, but one large build peaks far above its
# steady state, and 1g made ~5% of those requests fail. Raise it if you raise
# SPUR_WORKERS or the cache settings.
mem_limit: 2g
```
D-01/D-19 change `SPUR_WORKERS` to `"1"`, add `SPUR_BUILD_WORKERS: "2"`, and the
`mem_limit` comment must be rewritten to cite D-18's new per-N table and formula (parent
byte budget + N × solid cache) — the *convention* (a number, with the measurement that
produced it, right above the number) is what to copy; the *content* is new per D-20.

---

### `Dockerfile` (EDITED — `HEALTHCHECK --timeout`)

**Analog:** itself, pre-phase (all 46 lines read this session)

**Pattern to copy — comment justifies the number, same as compose.yaml's convention**
(lines 41-45):
```dockerfile
# Source: Dockerfile:41-45, current
# 10 s rather than 5: OpenCascade holds the GIL, so one large gear legitimately stalls
# the event loop for a few seconds. Failing liveness over that restarts a healthy
# container mid-build.
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD ["python", "-c", "import os, urllib.request as u; u.urlopen('http://127.0.0.1:' + os.environ.get('SPUR_PORT', '8000') + '/api/health', timeout=8)"]
```
D-14 rewrites the comment to cite the new measured p95 and drops `--timeout` to ~5s. Per
CONTEXT.md's specifics: "If `HEALTHCHECK --timeout` cannot come down from 10 s, treat that
as evidence the phase did not land" — this is a hard success signal, not a style note.

---

### `tests/test_api.py` (EDITED + 4 new tests)

**Analog:** itself, pre-phase (all 99 lines read this session) + `tests/test_model.py` for
the build/export assertion style

**Existing module-scope client — the pitfall RESEARCH.md flags** (line 6):
```python
# Source: tests/test_api.py:1-6, current — this pattern must NOT be reused for the new
# e2e test (RESEARCH.md Pitfall 1): TestClient(app) without `with` never runs lifespan.
import pytest
from fastapi.testclient import TestClient

from spur.app import app

client = TestClient(app)
```
The 11 existing tests using this module-level `client` stay as-is (D-15: they exercise the
inline path, which must not require the pool to have started).

**D-09 test to adapt** (lines 85-99) — reaches into `BUILD_QUEUE`/`MAX_QUEUED_BUILDS`
directly, must keep working once those are derived from `SPUR_BUILD_WORKERS`:
```python
# Source: tests/test_api.py:85-99, current
def test_a_saturated_service_refuses_instead_of_queueing() -> None:
    """Builds serialise on the kernel lock, so a deep queue is latency with no payoff."""
    from spur import app as app_module

    held = [app_module.BUILD_QUEUE.acquire(blocking=False)
            for _ in range(app_module.MAX_QUEUED_BUILDS)]
    try:
        assert all(held)
        r = client.get("/api/model.stl", params={"quality": "preview"})
        assert r.status_code == 503
        assert r.headers["retry-after"] == "5"
        assert r.json()["detail"][0]["type"] == "busy"
    finally:
        for _ in held:
            app_module.BUILD_QUEUE.release()
```
No structural change needed — `MAX_QUEUED_BUILDS` still exists as a module attribute, just
computed differently (D-09). The docstring's "serialise on the kernel lock" framing becomes
inaccurate post-phase (N kernels now) and should be corrected in the same edit.

**New e2e test — copy RESEARCH.md's verified shape exactly** (this is the one place a
different `TestClient` idiom than the file's own convention is required, and the file
must say why in a comment so a future edit doesn't "fix" it back to the module-level
`client`):
```python
# Source: this project's design (D-15); TestClient lifespan behavior verified in
# 02-RESEARCH.md this session against starlette==1.6.0 / fastapi==0.141.1.
def test_a_real_worker_builds_and_downloads() -> None:
    with TestClient(app) as client:  # runs lifespan startup/shutdown — see Pitfall 1
        r = client.get("/api/model.stl", params={"quality": "preview", "teeth": 21})
    assert r.status_code == 200
    assert len(r.content) > 1000
    # tripwire (RESEARCH.md Pitfall 1's warning sign): prove the boundary was actually
    # crossed, not just that the inline path also would have passed.
```

**New failure-mode tests (D-12)** follow the existing `test_infeasible_is_422_with_fields`
/ `test_bad_type_is_422_on_the_field` shape (lines 32-43) for the response-body assertions,
and the `test_a_saturated_service_refuses_instead_of_queueing` shape (lines 85-99) for the
`503`/`Retry-After` assertions — one test per D-12 failure mode
(`BuildError`→422 unchanged, `BrokenProcessPool`→503, timeout→503), each asserting the
`detail[0]["type"]` value distinguishes the three.

**Regression test for the private API (Assumption A3)** — no analog in this repo (nothing
here has ever tested a stdlib private attribute); write directly from RESEARCH.md's
Assumptions Log entry A3: `assert hasattr(ProcessPoolExecutor(...), "_processes")`, with a
comment naming the CPython version it was verified against (RESEARCH.md: 3.12.13).

---

### `bench/` harness + `make bench` (NEW)

**No close analog for the harness itself.** This repo has no committed load/memory-sweep
script — the F2/F4 methodology it must reuse (RESEARCH.md's "Don't Hand-Roll" row) exists
only as **prose** in `docs/plan-2026-09-21.md`'s "Outcome" table, not as code. Two partial
analogs to build from:

**HTTP-call-without-a-test-client pattern** (useful if the harness wants to drive the ASGI
app directly rather than shelling out to `curl`/`httpx` against a running container) —
`docker/smoke.py:20-44`:
```python
# Source: docker/smoke.py:20-44 — raw ASGI call pattern, reusable if the latency half of
# the harness wants to avoid a network round-trip; the memory half (D-17) must go through
# a real running container regardless, since mem_limit is a container-accounting setting.
async def get(path: str, query: bytes = b"") -> tuple[int, bytes]:
    """One GET straight through the ASGI app; the image has no HTTP test client."""
    ...
```
For D-16/D-17's actual design (host-side latency via `make serve`, container-side memory
via `docker compose up`), a real HTTP client (`httpx`, already a dev dependency) against
the running service is closer to what's needed than this in-process pattern — the smoke.py
shape is offered only as a fallback if the harness needs a dependency-free ASGI probe.

**`make` target wiring pattern — copy exactly**, `Makefile:73-95` (`smoke`, `up`, `down`,
`logs` targets show the "docker compose driven, waits/polls, prints a result" shape):
```makefile
# Source: Makefile:80-88 — the shape a new `bench` target should follow: docker-compose
# driven, one-line `## comment` for `make help`, no hidden state.
up:  ## build, start and wait for the service on http://localhost:8000
	docker compose up -d --build
	@printf 'waiting for the container to report healthy'
	@n=0; until [ "$$(docker compose ps --format '{{.Health}}')" = healthy ]; do \
	   ...
	 done
	@echo ' -> http://localhost:8000'
```
And the `.PHONY` list convention at the top of the file (`Makefile:15-16`) — `bench` must
be added there too. Per D-16, `bench` must **not** be a dependency of `verify` or `check`
(it needs a running service and minutes); model it as its own top-level target the way
`smoke`/`up`/`down`/`logs` are already siblings of, not dependents of, `verify`.

**Corpus/methodology to reuse verbatim (not reinvent), per RESEARCH.md's "Don't Hand-Roll"
table:** 40 distinct 160-199 tooth gears (the exact corpus `docs/plan-2026-09-21.md`'s F2
used), anon RSS measured in the container, sweep `mem_limit` candidates, require zero
failures at the chosen value — "the same way `2g` was earned" (quoted from
`docs/plan-2026-09-21.md`'s Outcome section and `compose.yaml:13-16`'s own comment).

---

### `docs/architecture/decision_log.md` (EDITED — append L17, L18)

**Analog:** `L06`/`L07` entries, `docs/architecture/decision_log.md:57-73` — the exact
entries these two supersede, and the format every new entry must match (heading, one-line
statement, "Reason:" paragraph with numbers inline):
```markdown
# Source: docs/architecture/decision_log.md:64-73 — the entry L17 supersedes; copy this
# exact heading/Reason shape for L17 and L18.
## L07 — Bounded caches, and hand the arenas back

Solids are cached by entry count (`SPUR_SOLID_CACHE`, default 4), exported bytes by
total size (`SPUR_EXPORT_CACHE_MB`, default 64), and `malloc_trim(0)` runs after every
cache-missing export.

Reason: measured. "32 entries" is not a memory bound when one solid costs ~280 MiB.
Cache trimming alone moved the plateau from 1.87 GiB to 1.5 GiB; the arena release took
it to 358 MiB — almost all of the apparent leak was glibc holding freed arenas, not live
cached data. The caches stay because they make the ceiling predictable.
```
Per D-20/CLAUDE.md: append-only, never edit L06/L07 in place; each new entry states which
id it supersedes (as the file's own header instructs: "to change one, add a new entry that
supersedes it and say which" — `decision_log.md:3-4`).

---

### `docs/tech_debt/active/2026-09-21-cad-builds-block-the-event-loop.md` → resolved (EDITED + moved)

**Analog:** `docs/tech_debt/TEMPLATE.md` (field shape) and `docs/tech_debt/INDEX.md`'s
Active-table row format, `docs/tech_debt/INDEX.md:17-26` — there is no prior `Resolved`
entry to copy from (`INDEX.md:28-29` literally says "(none yet)"), so this phase's move is
the first exercise of the lifecycle CLAUDE.md describes, not a copy of an existing example.

**What changes in the file itself:** `Status: active` → `Status: resolved` + a commit sha
line, per CLAUDE.md's "On fixing debt" rule, quoted:
```
Status: resolved  (was: active)
Resolved: <sha of the commit that lands this>
```
Then `git mv docs/tech_debt/active/2026-09-21-cad-builds-block-the-event-loop.md
docs/tech_debt/resolved/`, and the `INDEX.md` row moves from the `## Active` table
(`INDEX.md:19`) into a new `## Resolved` list entry, replacing the placeholder
`- (none yet)` (`INDEX.md:29`) — same commit as the code fix, per CLAUDE.md and per
CONTEXT.md's own restatement of that rule under "Claude's Discretion".

## Shared Patterns

### `int_env()` — every new environment knob
**Source:** `src/spur/__init__.py:8-13`
**Apply to:** `SPUR_BUILD_WORKERS`, `SPUR_BUILD_TIMEOUT` in `app.py` (D-03, D-10); already
the pattern `MAX_QUEUED_BUILDS`/`SPUR_MAX_QUEUED_BUILDS` uses today
```python
def int_env(name: str, default: int) -> int:
    """A positive integer setting from the environment, falling back on nonsense."""
    try:
        return max(1, int(os.environ.get(name) or default))
    except ValueError:
        return default
```

### `503` + `Retry-After` + `detail[].type` — every admission/pool refusal
**Source:** `src/spur/app.py:70-84` (`_build_slot`)
**Apply to:** the two new D-12 refusal modes (`BrokenProcessPool`, timeout) in `app.py`'s
`model()` endpoint — same headers, same `detail` list shape, new `type` string per mode.

### `422` from a kernel-refused build
**Source:** `src/spur/app.py:117-119` (`except BuildError`)
**Apply to:** unchanged by this phase (D-12: `BuildError` still means 422); only its
import path moves to `.build_errors`.

### Measured-number-in-a-comment
**Source:** `compose.yaml:13-16`, `Dockerfile:41-43`, `src/spur/model.py:64-67`
(`_release_arenas`'s docstring)
**Apply to:** every numeric knob this phase touches or introduces —
`mem_limit` (D-18), `HEALTHCHECK --timeout` (D-14), `SPUR_BUILD_TIMEOUT` (D-10),
`MAX_QUEUED_BUILDS`'s new derivation (D-09). CLAUDE.md's standing rule ("comments carry the
measurement or constraint that forced the choice") is enforced by precedent here, not just
by policy.

### Module boundary via import-linter contract, not review
**Source:** `pyproject.toml:121-146` (three existing `[[tool.importlinter.contracts]]`
entries)
**Apply to:** D-02's new `spur.app` → `cadquery`/`OCP` forbidden-indirect contract; same
table shape, comment-above-values convention.

### Append-only decision log, "supersedes" stated explicitly
**Source:** `docs/architecture/decision_log.md:3-4` (file header), `L06`/`L07` (the two
entries being superseded)
**Apply to:** L17 (supersedes L07), L18 (supersedes L06) — D-20.

## No Analog Found

| File | Role | Data Flow | Reason |
|---|---|---|---|
| `src/spur/build_errors.py` | model/utility | n/a | First time this repo has split an exception class into its own module; treat as a mechanical extraction of `model.py:42-43`, not a pattern lookup — see RESEARCH.md's "Recommended Project Structure" for the target shape (`BuildError` only, no `cadquery` import). |
| `bench/` harness | utility/script | batch + event-driven | No committed load/memory-sweep script exists; the methodology it must reuse (`docs/plan-2026-09-21.md`'s F2/F4 numbers) is prose, not code. Build from `docker/smoke.py`'s ASGI-call pattern (partial) and `Makefile`'s docker-driven target shape (partial); do not invent a new corpus or pass/fail bar — D-16/D-18 already fix both. |
| `docs/tech_debt/resolved/*` (the directory itself) | docs | n/a | `resolved/` has never been populated (`INDEX.md:29`: "(none yet)"). This phase's `git mv` is the first exercise of the documented lifecycle, not a copy of a prior example. |
| Lifespan-managed process pool (`app.state.pool`, `BuildPool`) | provider | event-driven (process lifecycle) | This app has never had an async `lifespan=` context before. Use RESEARCH.md's `Pattern 1` (verified against the installed interpreter, not copied from an external source) as the starting shape rather than searching for an in-tree analog that does not exist. |

## Metadata

**Analog search scope:** `src/spur/` (all 5 non-static modules), `tests/` (all 4 test
files), `pyproject.toml`, `compose.yaml`, `Dockerfile`, `Makefile`, `docker/smoke.py`,
`docs/architecture/{decision_log,http-api,packaging}.md`, `docs/tech_debt/{INDEX,TEMPLATE}.md`,
`docs/plan-2026-09-21.md`, `docs/review-2026-09-21.md`.
**Files scanned:** 20 (every git-tracked file relevant to this phase's edit list, per
CONTEXT.md's "Code this phase edits" section — all read in full given each is under 320
lines).
**Pattern extraction date:** 2026-09-22
