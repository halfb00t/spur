# Phase 2: CAD Off the Event Loop - Research

**Researched:** 2026-09-22
**Domain:** Python `concurrent.futures.ProcessPoolExecutor` under FastAPI/uvicorn; per-process memory measurement for a CadQuery/OpenCascade kernel
**Confidence:** HIGH for stdlib mechanics (verified this session against the installed interpreter/library); MEDIUM for absolute performance numbers (they must be re-measured on the actual target, per L08 and D-16/D-17 — nothing here substitutes for that); LOW/ASSUMED flagged individually below

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Pool topology**
- **D-01:** One server process, N builders. `compose.yaml` drops to `SPUR_WORKERS: "1"`;
  a new `SPUR_BUILD_WORKERS` sizes the CAD pool. Serving is pure I/O once builds leave it,
  so process count and cache count move together on one knob — the memory sweep has one
  variable, not two multiplied.
- **D-02:** Hard split: the serving process never imports the CAD kernel. `app.py` stops
  importing `model.py`; `BuildError` moves to a kernel-free module so the web layer can
  still name it. A new import-linter contract forbids `spur.app` → `cadquery`/`OCP`
  **including indirectly** (`allow_indirect_imports = false`), so the boundary is enforced
  rather than reviewed. — Reversibility: costly.
- **D-03:** `concurrent.futures.ProcessPoolExecutor`, driven from the async endpoint via
  `loop.run_in_executor`. `mp_context = spawn` (portable, and with D-02 the parent has no
  OCP to fork); `initializer` imports `cadquery`/`model` to pre-warm; `max_tasks_per_child`
  available as the recycling lever (see D-11). Stdlib only — no new dependency, no
  hand-rolled IPC.
- **D-04:** Pool comes up eagerly in the FastAPI lifespan, initializer importing only (no
  warm build). The memory sweep then measures steady state from t=0 instead of a ramp.

**Cache and process boundary**
- **D-05:** The function that crosses the boundary is `export(params, fmt, quality) ->
  bytes`. The solid is built, cached and exported entirely inside the worker; no `cq.Solid`
  is ever pickled, and vendor types still stop at `model.py`. — Reversibility: costly.
- **D-06:** Cache placement: the exported-bytes cache (`_BlobCache`, 64 MB) moves into the
  serving process, keyed on `(params, fmt, quality)`; the solid `lru_cache` stays per
  worker. A repeat download never crosses the boundary and never wakes a worker; there is
  one byte cache instead of N. The superseding L07 formula therefore reads: *parent byte
  budget + N × solid cache*.
- **D-07:** Routing has affinity: N single-worker executors indexed by a hash of the
  `GearParams`, not one N-worker pool. The UI's preview STL → fine STL → STEP are three
  byte-cache keys but one solid, so affinity preserves build-once-export-three-times and
  stops the same ~280 MiB solid becoming resident in N workers. Accepted cost: no work
  stealing — a hot gear serialises, which is what it does today.
- **D-08:** `_LOCK` in `model.py` stays. It is uncontended under one-task-per-worker, costs
  nothing measurable, and still guards OCCT's process-global state against a future
  in-process thread. The superseding L06 entry retires the *consequence* ("concurrency
  buys latency, not throughput") — now false — not the lock.

**Behaviour under load**
- **D-09:** `MAX_QUEUED_BUILDS` is derived from `SPUR_BUILD_WORKERS` (workers plus a
  shallow queue, ~2×N) instead of the absolute 4. Still a bounded semaphore, still
  non-blocking acquire → `503` + `Retry-After`; env override kept. One knob moves both, so
  a deployer cannot configure a queue deeper than the pool can drain. L04 is untouched:
  admission control stays in the web layer, the CLI still never queues.
- **D-10:** Per-build timeout (`SPUR_BUILD_TIMEOUT`), set **above the worst measured
  build**, not picked. On expiry: terminate that worker, recreate its executor, refuse the
  request. This exists because D-07's affinity makes a wedged worker fatal to 1/N of the
  parameter space.
- **D-11:** Worker memory hygiene: keep `malloc_trim(0)` per worker (it is the measured
  win). Enable `max_tasks_per_child` **only if** the sweep shows drift that trim does not
  flatten — and record which way it went, with the numbers, in the superseding L07 entry.
  Recycling otherwise costs a respawn plus a `cadquery` import and wipes the solid cache
  D-07 exists to keep warm.
- **D-12:** Failure modes map to status codes: `BuildError` → `422` (unchanged, the kernel
  refused these parameters); `BrokenProcessPool` → `503` + `Retry-After` with its own
  `type`, matching the existing `busy` detail shape; timeout → `503` + `Retry-After` too.
  A timeout is explicitly **not** a `422` — the same gear succeeds on faster hardware, so
  it is not a property of the parameters. — Reversibility: costly.
- **D-13:** `/api/health` gains pool state, from **parent-local counters only**: live
  executors, current semaphore value, workers replaced since start. No IPC, no lock, no
  await on a worker — O(1) attribute reads, so the endpoint whose p95 is this phase's
  success criterion still measures the event loop and not the pool. — Reversibility:
  one-way.
- **D-14:** Dockerfile `HEALTHCHECK --timeout` drops from 10 s to ~5 s, **set from the
  measured under-load p95** rather than reverted by reflex, with the comment rewritten to
  cite the new number. If the timeout still has to be 10 s, the phase did not land.
  `--start-period=30s` stays unless the eager-startup measurement (D-04) says otherwise.
- **D-15:** Test strategy: the build backend is injectable, so most API tests run the
  export inline in-process (fast, and the same code path the CLI takes), plus **one** real
  end-to-end test that spawns a worker and downloads bytes. `make verify` stays near its
  ~11 s warm budget while the process boundary is still proven by the gate.

**Measurement**
- **D-16:** The harness is committed and rerunnable, wired to a `make` target (`make
  bench`), running both of the debt file's scenarios and the memory sweep. It is **not**
  part of `make verify`. The point is the claim stays falsifiable by whoever doubts it
  later.
- **D-17:** Two environments, deliberately: **latency on the host** (`make serve`), the way
  the 0.22 s → 0.76 s → 2.00 s baseline was produced, so old and new numbers are
  like-for-like; **memory in the container** (`docker compose up`), because `mem_limit` is a
  container setting and must be measured under the container's accounting. CPU count, arch
  and RAM are recorded alongside every number.
- **D-18:** The sweep varies worker count (N = 1, 2, 4) over L07's own corpus — 40 distinct
  160–199 tooth gears — recording peak container memory per N. `mem_limit` is set from the
  shipping default's peak plus a **named** headroom, then confirmed by re-running the
  corpus at that limit and requiring zero failures — the same way 2g was earned. The per-N
  table ships too.
- **D-19:** `SPUR_BUILD_WORKERS` defaults to a fixed **2**, justified by the per-N table
  rather than inherited from today's `SPUR_WORKERS: "2"`. Not derived from `cpu_count`:
  that would make the memory ceiling machine-dependent, and `mem_limit` is one number that
  has to be true everywhere (same reasoning L05 protects for parameter defaults).
- **D-20:** Two decision-log entries, numbers inline. **L17 supersedes L07** — the new
  cache/memory formula (parent byte budget + N × solid cache), the per-N peak table, the
  confirmed `mem_limit`. **L18 supersedes L06** — the lock stays, its consequence does not.
  Each dated, each stating what it supersedes, neither edited in place. — Reversibility:
  one-way — `docs/architecture/decision_log.md` is append-only by policy.

### Claude's Discretion

- The name and placement of the kernel-free boundary module that owns the pool, and where
  `BuildError` lands (D-02). It must be importable by `app.py` without pulling in
  `cadquery`.
- The bench harness's location (`bench/` vs `docker/`) and its output format, given D-16.
- The literal values of `SPUR_BUILD_TIMEOUT` (D-10) and the `mem_limit` headroom factor
  (D-18) — both are set *from* the measurement; only the rule is fixed here.
- Whether `docs/architecture/overview.md` and `docs/architecture/packaging.md` need updating
  for the new topology, and how the debt-file resolution (`Status: resolved`, sha, `git mv`,
  INDEX row) is sequenced against the code commits. CLAUDE.md already requires the debt
  move to land in the same commit as the fix.

### Deferred Ideas (OUT OF SCOPE)

- **Measure the Raspberry Pi 5 claim, or soften it.** File in `docs/ideas/`; trigger is
  someone actually running one. Not a phase deliverable.
- **Server-side cancellation on client abort** — `docs/tech_debt/active/2026-09-21-no-server-side-cancellation.md`
  (nice). This phase makes it possible; it does not do it.
- **Work stealing / non-affinity fallback routing** (rejected variant of D-07) — revisit
  only with a measurement showing affinity starves throughput under mixed load.
- **Querying workers from `/api/health`** (rejected variant of D-13) — revisit if D-10's
  timeout proves insufficient; it costs IPC behind the measured endpoint.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| REQ-cad-off-event-loop | CAD builds execute outside the serving process; `/api/health` latency stops scaling with build size | `## Architecture Patterns` (pool skeleton, affinity routing, lifespan startup), `## Common Pitfalls` (TestClient lifespan gotcha, `run_in_executor` positional-only args, private `_processes` termination), `## Validation Architecture` (test map for D-15's inline vs. e2e split) |
| REQ-measured-memory-ceiling | Multi-process memory ceiling measured (not derived), `compose.yaml` `mem_limit` set from it, superseding decision-log entry | `## Don't Hand-Roll` (reuse `docs/plan-2026-09-21.md`'s sweep methodology), `## Common Pitfalls` (macOS vs. Linux `malloc_trim` gap, dev-machine arch mismatch), `## Code Examples` (per-N sweep harness shape) |
</phase_requirements>

## Summary

This phase is a refactor of a fully-specified design (20 locked decisions in CONTEXT.md)
into stdlib code, not an open design search — research here is about **stdlib mechanics
that the plan must get right on the first try**, because several of them are the kind of
thing that passes a quick smoke check and then fails under the load scenario the success
criteria actually exercise (a wedged worker, a broken pool, a test that silently never
starts the pool it's supposed to be testing).

Three findings, verified against the installed interpreter/library this session, change
how the plan should be written, not just how it should be coded:

1. **`fastapi.testclient.TestClient` does not run lifespan startup/shutdown unless used as
   a context manager (`with TestClient(app) as client: ...`).** The existing
   `tests/test_api.py` module-level `client = TestClient(app)` (no `with`) — reused by
   11 of 12 current tests — will silently see an **unstarted pool** after D-02/D-04 land.
   D-15's design (most tests run the export inline, one real test spawns a worker) already
   anticipates this by making the backend injectable, but the plan must say explicitly
   that the **one** e2e test needs its own `with TestClient(app) as client:` block (or an
   equivalent manual lifespan `contextmanager`), or it will pass for the wrong reason
   (falling through to the inline path) or hang/error waiting on a pool that never started.
2. **`ProcessPoolExecutor` has no public API to kill a running (not merely pending) task.**
   `Executor.shutdown(cancel_futures=True)` only cancels futures that have not yet started
   running; a wedged worker executing OCCT code keeps running until it finishes or the
   process is killed directly. The only way to reach the underlying `multiprocessing`
   process objects is the **private, undocumented** `executor._processes` dict
   (`pid -> SpawnProcess`), confirmed to exist on the installed CPython 3.12/3.14. D-10's
   "terminate that worker, recreate its executor" is only achievable through this private
   attribute (or an equivalent lower-level approach); the plan should call this out as a
   version-fragility risk with a `make verify`-run regression test, not assume a clean
   public cancellation exists.
3. **`asyncio.AbstractEventLoop.run_in_executor(executor, func, *args)` takes positional
   args only** — no keyword arguments. `export(params, fmt, quality)`'s existing signature
   is already all-positional, so this is a non-issue for the D-05 boundary function as
   currently shaped, but if the plan's worker entry point grows a keyword-only parameter
   later, `functools.partial` is required; flag it so nobody adds a kwarg to the crossing
   function without noticing.

**Primary recommendation:** Build the pool exactly as D-01–D-20 specify — no alternative
libraries needed, this is textbook `concurrent.futures.ProcessPoolExecutor` plus
`asyncio.loop.run_in_executor`, both stdlib — but write the plan's task list so that (a)
the e2e test's lifespan-triggering is an explicit, separately-verified step, (b) the
timeout→terminate path is implemented against the private `_processes` API with a comment
naming the CPython version it was verified against, and (c) every absolute number (memory
ceiling, timeout value, p95 latency) is produced by re-running D-16's harness on the real
target, never carried over from the numbers measured in this research session on an
unrelated development machine.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| HTTP routing, admission control, response shaping | API / Backend (`app.py`) | — | Already owns this (L04); D-02 only removes its CAD import, not its role |
| CAD solid construction, tessellation/STEP export | Worker process (new tier: CPU-bound subprocess pool) | — | D-02/D-05 move this out of the API tier entirely; it was wrongly co-located with the event loop before this phase |
| Exported-bytes cache | API / Backend (`app.py`, via D-06) | — | Moved **up** from `model.py` deliberately — one cache instead of N, and it never needs the kernel |
| Solid cache (`lru_cache`) | Worker process | — | Stays per-worker (D-06); rebuilding a solid needs the kernel that only workers have |
| Pool lifecycle (start/stop/replace) | API / Backend (FastAPI lifespan, D-04) | — | The serving process is the only thing with a stable lifetime to hang pool lifecycle off |
| Liveness reporting | API / Backend (`/api/health`, D-13) | — | Parent-local counters only; explicitly not the worker tier, to keep the endpoint fast |
| CLI export | CLI process (`cli.py`) | — | Unchanged: in-process, no pool, no queue (L04); the CLI is its own tier, not a client of the API tier |
| Memory/latency measurement harness | Out-of-band (bench tooling, D-16) | Container runtime (for the memory half, D-17) | Not part of any serving tier; it observes the other tiers from outside |

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `concurrent.futures.ProcessPoolExecutor` | stdlib (installed interpreter: CPython 3.12.13 in `.venv`, project floor 3.10) | Process pool, worker lifecycle, task submission | `[VERIFIED: .venv/bin/python inspect.signature this session]` — signature is `(self, max_workers=None, mp_context=None, initializer=None, initargs=(), *, max_tasks_per_child=None)`, matching every knob D-03/D-11 needs with zero new dependency |
| `asyncio.AbstractEventLoop.run_in_executor` | stdlib | Bridge the async endpoint to the process pool without blocking the loop | `[VERIFIED: .venv/bin/python inspect.signature this session]` — signature `(self, executor, func, *args)`; positional-only, matches `export(params, fmt, quality)` exactly |
| `multiprocessing` (spawn context) | stdlib | `mp_context="spawn"` per D-03 | `[ASSUMED]` — spawn is the documented cross-platform-safe start method and the only one that doesn't fork a process that (post D-02) has no OCP loaded to begin with; not independently re-verified against the Python docs this session beyond the signature check above |

No new third-party dependency is added by this phase. `pyproject.toml`'s `dependencies`
list should be unchanged; only the import-linter `[[tool.importlinter.contracts]]` table
and `compose.yaml`/`Dockerfile` env/health lines change.

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `ctypes` + `libc.so.6` (`malloc_trim`) | stdlib, already in `model.py` | Per-worker arena release | Reused as-is inside each worker (D-11); no change needed to `_load_malloc_trim`/`_release_arenas`, only to *where* they run (now inside a worker process instead of the single server process) |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `concurrent.futures.ProcessPoolExecutor` | `multiprocessing.Pool` directly | Loses the `Future`/`asyncio.run_in_executor` integration for free; would require hand-rolling the async bridge. Rejected by D-03 ("stdlib only ... no hand-rolled IPC"). |
| `concurrent.futures.ProcessPoolExecutor` | `anyio.to_process` (already a transitive dependency via Starlette/FastAPI's `anyio`) | Simpler async-native API, but per-call process spawn by default (no persistent warm pool without extra plumbing) works against D-04's eager-warm-pool requirement and D-07's affinity requirement; would need its own worker-affinity layer built on top, which is the "hand-rolled IPC" D-03 rejects. `[ASSUMED]` — not benchmarked this session. |
| N single-worker executors (D-07 affinity) | One `ProcessPoolExecutor(max_workers=N)` | Simpler code, but breaks D-06/D-07's cache-locality guarantee (a hot gear's solid could load into any of the N workers depending on scheduling, multiplying resident memory). Rejected by D-07 explicitly. |

**Installation:** none — no new packages.

**Version verification:** N/A, no new packages to verify against a registry. Existing
pinned versions relevant to this phase, confirmed by import in `.venv`
`[VERIFIED: pip-installed packages in .venv, this session]`:
`cadquery==2.8.0`, `fastapi==0.141.1`, `starlette==1.6.0`, `uvicorn==0.53.0`,
`pydantic==2.13.5`, `anyio==4.15.1`.

## Package Legitimacy Audit

**Not applicable.** This phase installs no new external packages — `concurrent.futures`,
`asyncio`, `multiprocessing` and `ctypes` are all stdlib. No `gsd_run query
package-legitimacy check` call was made because there is nothing to check.

## Architecture Patterns

### System Architecture Diagram

```
                        ┌────────────────────────────────────────┐
                        │   Serving process (uvicorn, 1 worker)   │
                        │                                          │
  HTTP request ──────▶  │  app.py                                  │
                        │   ├─ admission control (BUILD_QUEUE,     │
                        │   │   BoundedSemaphore, D-09)            │
                        │   ├─ _gear(q) → GearParams                │
                        │   ├─ byte cache lookup (_BlobCache, D-06) │
                        │   │     hit  ──────────────────────────▶ Response (no worker touched)
                        │   │     miss │                            │
                        │   │          ▼                            │
                        │   ├─ route by hash(params) % N (D-07)     │
                        │   │          │                            │
                        │   │          ▼                            │
                        │   └─ loop.run_in_executor(executor_i,     │
                        │        export, params, fmt, quality)      │
                        │             │                              │
                        │             │ pickled GearParams (spawn)   │
                        └─────────────┼──────────────────────────────┘
                                      ▼
                  ┌───────────────────────────────────────┐
                  │ Worker process i (1 of N, spawn ctx)   │
                  │  initializer: import cadquery, model   │  (D-04, pre-warm)
                  │                                          │
                  │  model.export(params, fmt, quality)      │
                  │    ├─ _LOCK (D-08, uncontended per-task) │
                  │    ├─ solid lru_cache (per worker, D-06) │
                  │    ├─ build → tessellate/export → bytes  │
                  │    └─ _release_arenas() / malloc_trim    │
                  └───────────────────────────────────────┘
                                      │
                                      ▼ bytes (pickled back)
                        ┌────────────────────────────────────────┐
                        │  app.py: _BlobCache.put(key, data)      │
                        │  → Response(data, ...)                  │
                        └────────────────────────────────────────┘

Failure paths:
  BuildError (kernel refused params)   → 422, re-raised in parent from worker's pickled exception
  BrokenProcessPool (worker crashed)   → 503 + Retry-After, executor discarded, new one built (D-12)
  Timeout (future.result(timeout=T))   → 503 + Retry-After, worker terminated via executor._processes,
                                          executor for that hash slot recreated (D-10, D-12)
```

### Recommended Project Structure

No new top-level packages — this phase adds a module and edits existing ones. Given
D-02's requirement ("importable by `app.py` without pulling in `cadquery`") and the
"Claude's Discretion" naming freedom:

```
src/spur/
├── build_errors.py     # NEW (discretion: name/placement) — BuildError only, no cadquery import
├── app.py              # EDITED — drops `from .model import BuildError, export`;
│                        #          adds pool lifecycle (lifespan), routing, health fields
├── model.py             # EDITED — unchanged export() surface; runs inside workers now
├── cli.py               # UNCHANGED — still imports model.export directly, no pool (L04)
└── params.py             # UNCHANGED — GearParams already picklable/hashable, verified below
```

### Pattern 1: Lifespan-managed, affinity-routed process pool

**What:** N single-worker `ProcessPoolExecutor`s created eagerly in the FastAPI lifespan,
routed to by a hash of `GearParams`, driven from the async endpoint via
`run_in_executor`.

**When to use:** Exactly this phase's shape — CPU-bound, GIL-holding native work behind
an async HTTP server, where warm per-worker caches are worth preserving (D-07).

**Example (mechanics verified against the installed interpreter this session; the
integration shape itself is this project's own design per D-01–D-13, not copied from an
external source):**

```python
# Source: verified against .venv/bin/python (CPython 3.12.13) inspect.signature output,
# this session — ProcessPoolExecutor.__init__ and run_in_executor signatures.
from __future__ import annotations

import multiprocessing as mp
from collections.abc import AsyncIterator
from concurrent.futures import ProcessPoolExecutor
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .params import GearParams

_SPAWN = mp.get_context("spawn")


def _warm() -> None:
    """Runs once per worker process, before it accepts any task (D-04)."""
    import cadquery  # noqa: F401  -- imported for its side effect: OCP loaded once
    from . import model  # noqa: F401


class BuildPool:
    def __init__(self, n: int) -> None:
        self.n = n
        self._executors = [
            ProcessPoolExecutor(max_workers=1, mp_context=_SPAWN, initializer=_warm)
            for _ in range(n)
        ]
        self.replaced = 0  # D-13: workers replaced since start

    def executor_for(self, params: GearParams) -> ProcessPoolExecutor:
        return self._executors[hash(params) % self.n]  # D-07: affinity, not load-balance

    def recreate(self, params: GearParams) -> None:
        """D-10/D-12: discard a broken/wedged single-worker executor, replace it."""
        i = hash(params) % self.n
        old = self._executors[i]
        old.shutdown(wait=False, cancel_futures=True)
        self._executors[i] = ProcessPoolExecutor(
            max_workers=1, mp_context=_SPAWN, initializer=_warm
        )
        self.replaced += 1

    def shutdown(self) -> None:
        for ex in self._executors:
            ex.shutdown(wait=False)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.pool = BuildPool(n=int_env("SPUR_BUILD_WORKERS", 2))  # D-04: eager, import-only
    try:
        yield
    finally:
        app.state.pool.shutdown()
```

### Pattern 2: Timeout → terminate → recreate (D-10)

**What:** A per-build timeout that, on expiry, kills the specific wedged worker process
rather than waiting for it, then discards and rebuilds that hash slot's executor.

**Why this shape is necessary — verified this session, not assumed:**
`Executor.shutdown(cancel_futures=True)` `[VERIFIED: .venv/bin/python inspect.signature
concurrent.futures.ProcessPoolExecutor.shutdown, this session — signature `(self,
wait=True, *, cancel_futures=False)`]` only cancels futures that have not started
running yet; a future already executing inside the worker is untouched by
`cancel_futures`. The only way found this session to reach the underlying OS process is
the private attribute `executor._processes` (a `dict[int, multiprocessing.Process]`),
confirmed present on a freshly created `ProcessPoolExecutor` instance
`[VERIFIED: read via a script executed with .venv/bin/python this session — see output:
`has _processes: True`, `[(46460, <SpawnProcess name='SpawnProcess-1' pid=46460
parent=46458 started>)]`]`. This is undocumented, private CPython implementation detail —
flagged `[ASSUMED stable across 3.10–3.12]` since it was only checked on 3.12.13 here, and
the project's own CI runs both 3.10 and 3.12 (L14); a plan task should add a small
regression test that asserts `hasattr(executor, "_processes")` so a future CPython
release that removes the attribute fails loudly in `make verify` rather than silently
losing D-10's termination path.

```python
# Source: this project's own design (D-10, D-12); mechanics verified this session
# against CPython 3.12.13's concurrent.futures.process module.
import asyncio
from concurrent.futures import ProcessPoolExecutor

async def build_with_timeout(pool: BuildPool, params: GearParams, fmt: str,
                              quality: str, timeout: float) -> bytes:
    executor = pool.executor_for(params)
    loop = asyncio.get_running_loop()
    future = loop.run_in_executor(executor, export, params, fmt, quality)
    try:
        return await asyncio.wait_for(future, timeout=timeout)
    except TimeoutError:
        for proc in executor._processes.values():  # private API — see note above
            proc.terminate()
        pool.recreate(params)
        raise  # caller maps to 503 + Retry-After (D-12), not 422
```

### Pattern 3: Testing the pool boundary without hanging `make verify`

**What:** D-15's split — most tests call `model.export` inline (the CLI's own code path,
no pool involved at all), exactly one test proves the actual process boundary.

**The pitfall this must avoid — verified this session:** `fastapi.testclient.TestClient`
does **not** run the app's lifespan context unless used as `with TestClient(app) as
client:`. Confirmed empirically this session: instantiating `TestClient(app)` without a
`with` block and issuing a request through it left a lifespan-tracked list of events
empty (`{'events': []}`) even though the route handler executed and returned `200`
`[VERIFIED: script run with .venv/bin/python this session against a minimal FastAPI app
with an `asynccontextmanager` lifespan]`. The existing `tests/test_api.py:6` does exactly
this (`client = TestClient(app)` at module scope, no `with`), and 11 of its 12 tests
reuse that client. After D-02/D-04, those 11 tests must **not** depend on the pool having
started — which D-15's "run the export inline" design already guarantees, provided the
injectable backend defaults to the inline path when no pool has been started. The **one**
new e2e test needs its own explicit lifespan trigger:

```python
# Source: this project's design (D-15); TestClient lifespan behavior verified this
# session against the installed starlette==1.6.0 / fastapi==0.141.1.
def test_a_real_worker_builds_and_downloads() -> None:
    with TestClient(app) as client:  # <-- required: runs lifespan startup/shutdown
        r = client.get("/api/model.stl", params={"quality": "preview", "teeth": 21})
    assert r.status_code == 200
    assert len(r.content) > 1000
```

### Anti-Patterns to Avoid

- **Passing a lambda or closure as the `run_in_executor`/`ProcessPoolExecutor` target.**
  Confirmed this session: a `submit(lambda: 1)` with `mp_context="spawn"` fails with
  `PicklingError: Can't pickle <function <lambda> ...>: attribute lookup <lambda> on
  __main__ failed`. Every function crossing the boundary (`export`, the `initializer`)
  must be a plain module-level function, importable by its qualified name in the child.
- **Assuming `cancel_futures=True` stops a running build.** It only prevents *queued*
  futures from starting; see Pattern 2.
- **Reusing the module-level `client = TestClient(app)` pattern for the new e2e test.**
  See Pattern 3 — it silently tests the wrong (inline) path once D-02 lands, unless the
  injectable-backend default is audited to confirm it does not accidentally also cover
  the pool path with no pool running.
- **Sizing `SPUR_BUILD_WORKERS` from `os.cpu_count()`.** Explicitly rejected by D-19 — it
  would make the measured `mem_limit` machine-dependent, defeating the point of
  measuring it at all.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Cross-process work dispatch + result futures | A custom pipe/queue protocol around `multiprocessing.Process` | `concurrent.futures.ProcessPoolExecutor` | Already gives `Future` objects that compose with `asyncio.run_in_executor`; D-03 already locks this in |
| Async/sync bridging for the executor call | A manual thread + `asyncio.Future` bridge | `loop.run_in_executor(executor, func, *args)` | Stdlib does exactly this, verified signature this session; no reason to reimplement |
| Memory sweep methodology | A new corpus/methodology invented for this phase | Reuse `docs/plan-2026-09-21.md`'s own F2 methodology: 40 distinct 160–199 tooth gears, anon RSS measured in the container, sweep `mem_limit` candidates and require zero failures at the chosen value (the same way `2g` was earned before) | The exact corpus and pass/fail bar are already precedent in this repo (D-18 explicitly says "the same corpus" and "the same way 2g was earned") — inventing a new one would produce a ceiling that isn't comparable to L07's, defeating the "measured, not derived" requirement |
| Worker crash detection | Polling or health-pinging each worker | Let `BrokenProcessPool` propagate from `future.result()`/`run_in_executor` — it is raised automatically by `concurrent.futures` when a worker process dies unexpectedly `[VERIFIED: .venv/bin/python inspect — `BrokenProcessPool.__mro__` is `(BrokenProcessPool, BrokenExecutor, RuntimeError, Exception, BaseException, object)`, this session]` | D-12 already maps this exception type to `503`; no custom detection needed, just a `try/except BrokenProcessPool` around the `run_in_executor` await |

**Key insight:** every mechanism this phase needs (dispatch, futures, crash signaling,
async bridging) already exists in `concurrent.futures`/`asyncio`. The actual engineering
risk is not "does the pool work" — it's the three gaps found this session where the
*obvious* code is subtly wrong (unstarted-lifespan test client, `cancel_futures` not
killing running work, private-API worker termination).

## Common Pitfalls

### Pitfall 1: `TestClient` silently never starts the lifespan
**What goes wrong:** A test written against the un-context-managed `client = TestClient(app)`
module fixture appears to pass, but the pool was never started — the request either
falls through to an inline path (masking that the pool boundary was never exercised) or
hangs/errors if the endpoint unconditionally expects `app.state.pool` to exist.
**Why it happens:** `TestClient` only sends the ASGI `lifespan.startup` message inside its
`__enter__`; used as a plain object it never sends it at all — confirmed empirically this
session.
**How to avoid:** The one e2e test (D-15) must use `with TestClient(app) as client:`
explicitly; the other 11 existing tests must be verified to not touch `app.state.pool`
directly (they call `_build_slot`/`BUILD_QUEUE` today, which move to depend on
`SPUR_BUILD_WORKERS` under D-09 — check they don't also reach into pool internals that
require the lifespan to have run).
**Warning signs:** A green test suite where the "real worker" test's assertions would
also pass against `model.export` called inline — i.e., the test doesn't actually prove
the process boundary. Add an assertion that the export ran in a *different* PID than the
test process, as an explicit tripwire.

### Pitfall 2: Timeout does not stop the work, just the wait
**What goes wrong:** `asyncio.wait_for(future, timeout=T)` raises `TimeoutError` in the
caller, but the OCCT call inside the worker keeps running — CPU and the eventual return
value are wasted, and if the plan does not also kill the process, the next task routed to
that hash slot queues up behind the still-running old one.
**Why it happens:** Cancelling an `asyncio.Future` wrapping a `concurrent.futures.Future`
does not propagate to the OS process; there is no cooperative cancellation inside OCCT
(the debt file itself says as much for the related cancellation-on-abort issue).
**How to avoid:** D-10's "terminate that worker, recreate its executor" must be
implemented literally — kill the process object, not just abandon the future. See
Pattern 2 above for the verified mechanism (private `_processes` attribute).
**Warning signs:** A load test where a single deliberately-oversized gear causes every
subsequent request to that hash slot to also time out, instead of failing fast after the
first one.

### Pitfall 3: `malloc_trim` is a no-op on the development machine
**What goes wrong:** A developer on macOS (Darwin, as this research session's environment
is) runs the bench harness locally and sees no memory-plateau effect from `_release_arenas`,
and might wrongly conclude the per-worker hygiene isn't working.
**Why it happens:** `_load_malloc_trim` in `model.py` already catches `OSError` and returns
`None` on anything without `libc.so.6` — i.e., macOS. This is documented in
`docs/architecture/packaging.md`'s "Known gap" section already, and remains true when the
same function runs inside a worker process instead of the main one.
**How to avoid:** D-17 already mandates measuring memory only inside the container
(`docker compose up`), which is Linux/glibc — the plan should not add a memory assertion
that runs on the host.
**Warning signs:** A memory number recorded from `make serve` (host) instead of `docker
compose up` (container) for the ceiling claim.

### Pitfall 4: The benchmark machine and the dev machine are not the same machine
**What goes wrong:** The debt file's baseline (0.22 s → 0.76 s → 2.00 s, 12-core machine)
gets compared directly against numbers produced on a different-architecture machine,
producing an apples-to-oranges "2×" claim.
**Why it happens:** This research session's environment is Apple Silicon (arm64, Darwin
27.0.0) `[VERIFIED: uname -a, this session]`; the original baseline's machine
architecture is not stated beyond "12-core" in the debt file. D-17 anticipates exactly
this by requiring CPU count, arch and RAM to be recorded alongside every number, and by
scoping the *property* (p95 within 2× of idle p95) rather than the absolute figures as
the pass/fail bar.
**How to avoid:** Record arch/cores/RAM next to every latency number produced during
execution, per D-17; do not treat the debt file's absolute seconds as a target on a
different machine — only the ratio matters for the acceptance criterion.
**Warning signs:** A plan or PR that claims "matches the 0.22s baseline" on hardware that
was never confirmed to be comparable.

### Pitfall 5: `run_in_executor` cannot take keyword arguments
**What goes wrong:** A future refactor of the worker entry point that adds a keyword-only
parameter (e.g. `export(params, fmt, quality, *, debug=False)`) breaks silently at the
`run_in_executor` call site with a `TypeError`, or forces an awkward positional-only
signature change.
**Why it happens:** `loop.run_in_executor(executor, func, *args)` has no `**kwargs`
parameter `[VERIFIED: .venv/bin/python inspect.signature asyncio.AbstractEventLoop.run_in_executor,
this session — `(self, executor, func, *args)`]`.
**How to avoid:** Keep the crossing function's signature all-positional (it already is:
`export(p, fmt, quality)`), or wrap with `functools.partial` if a keyword becomes
unavoidable.
**Warning signs:** N/A for this phase's current signature — flagged for awareness only,
since `export()`'s three positional params match today.

## Code Examples

### Deriving `MAX_QUEUED_BUILDS` from `SPUR_BUILD_WORKERS` (D-09)

```python
# Source: this project's own int_env() helper, src/spur/__init__.py:8-13
# (verified by reading the file this session — see quote below).
n_workers = int_env("SPUR_BUILD_WORKERS", 2)
MAX_QUEUED_BUILDS = int_env("SPUR_MAX_QUEUED_BUILDS", 2 * n_workers)
BUILD_QUEUE = threading.BoundedSemaphore(MAX_QUEUED_BUILDS)
```
`int_env`'s existing body, quoted verbatim
`[VERIFIED: src/spur/__init__.py:8-13, read this session]`:
```
def int_env(name: str, default: int) -> int:
    """A positive integer setting from the environment, falling back on nonsense."""
    try:
        return max(1, int(os.environ.get(name) or default))
    except ValueError:
        return default
```

### `/api/health` pool fields (D-13) — parent-local, O(1)

```python
# Source: this project's own design (D-13); no library call involved, plain attribute
# reads on the BuildPool instance shown in Pattern 1 above.
@app.get("/api/health")
def health() -> dict[str, object]:
    pool: BuildPool = app.state.pool
    return {
        "status": "ok",
        "version": __version__,
        "build_workers": pool.n,
        "queue_available": BUILD_QUEUE._value,  # BoundedSemaphore internal counter
        "workers_replaced": pool.replaced,
    }
```
Note: `threading.BoundedSemaphore._value` is also a private attribute (not part of the
documented API) — `[ASSUMED]`, not independently re-verified this session beyond reading
the existing `app.py`'s own use of `BUILD_QUEUE.acquire`/`.release`; if the plan wants a
public-API-only counter, track `MAX_QUEUED_BUILDS - value` via a separate `AtomicInt`-style
counter incremented/decremented around `_build_slot()` instead of reading `_value`.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| One `RLock`-serialised kernel inside the request-serving process (L06/L07) | N single-worker `ProcessPoolExecutor`s, affinity-routed, warmed at lifespan startup (D-01–D-08) | This phase (v0.1, Phase 2) | `/api/health` decouples from build size; memory ceiling formula changes from "per-process caches × 1" to "parent byte budget + N × solid cache" (superseding L17) |
| Docker `HEALTHCHECK --timeout=10s` accommodating a known stall | `--timeout` set from the measured under-load p95 (expected ~5s per D-14), because the stall it accommodated is gone | This phase | If the timeout still needs to be 10s, the phase's own success criteria say it did not land |
| `MAX_QUEUED_BUILDS` a flat default of 4 | Derived from `SPUR_BUILD_WORKERS` (~2×N, D-09) | This phase | Queue depth now tracks pool capacity instead of being an arbitrary constant |

**Deprecated/outdated:**
- L06's stated consequence ("concurrency buys latency, not throughput") — the *lock*
  stays (D-08), but the consequence is false once there are N independent kernels; L18
  supersedes this specific claim, not the lock itself.
- L07's memory formula (bounded caches × 1 process) — superseded by L17's `parent byte
  budget + N × solid cache`, per D-06/D-20.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `mp_context="spawn"` is the correct/only sane choice given D-02's kernel-free parent | Standard Stack | Low — this is also explicitly locked by D-03 itself, not a discretionary choice; flagged only because the *reasoning* ("no OCP to fork") was not independently re-verified against the multiprocessing docs this session |
| A2 | `anyio.to_process` would need its own affinity/warm-pool layer built on top, making it a worse fit than `ProcessPoolExecutor` | Alternatives Considered | Low — D-03 already locks `concurrent.futures`; this is background reasoning only, not a live decision |
| A3 | `executor._processes` (private attribute) remains present and shaped the same way across CPython 3.10–3.12 | Pattern 2 / Common Pitfalls | Medium — only checked on 3.12.13 this session; if 3.10's implementation differs, D-10's termination path could silently no-op on one of the two CI-tested Python versions (L14). Mitigate with the recommended `hasattr` regression test. |
| A4 | `threading.BoundedSemaphore._value` is a stable way to read remaining queue capacity for `/api/health` | Code Examples | Low — cosmetic; a public-API counter is a trivial substitute if this is rejected during plan review |
| A5 | The debt file's 12-core baseline machine is x86, making it architecturally different from this research session's arm64 Mac | Common Pitfalls (Pitfall 4) | Low — D-17 already defends against this by recording arch/cores/RAM and scoping the pass/fail bar to a ratio, not an absolute; flagged only so the plan doesn't silently drop that discipline |

**If this table is empty:** N/A — five assumptions logged above, all low-to-medium risk
and all already defended against by the locked decisions themselves (D-03, D-17); none
block planning, but A3 warrants an explicit regression-test task.

## Open Questions (RESOLVED)

All three were open at the end of research and are answered by the phase plans
committed in `109769f`. Each carries its resolution inline below; none is outstanding.

1. **Does the injectable build backend (D-15) need an explicit "pool not started" fallback,
   or does it always default to inline?**
   - What we know: D-15 says "the build backend is injectable, so most API tests run the
     export inline in-process."
   - What's unclear: whether "injectable" means test code explicitly selects the inline
     backend (safe regardless of lifespan state), or whether the production code path
     itself falls back to inline when `app.state.pool` is absent (which would silently
     mask a lifespan that never ran, in production too, not just in tests).
   - Recommendation: the plan should make the fallback direction explicit — injection for
     tests only, with the production path hard-failing (not silently going inline) if the
     pool was never started, since a production request that skipped the pool would also
     skip the affinity/cache-locality guarantees D-07 depends on.
   - **RESOLVED — injection for tests only; the production path hard-fails.** Plan 02-01
     Task 1 builds the backend that way, and `02-VALIDATION.md`'s Wave 0 list records it
     as "the injectable build backend itself (D-15), hard-failing rather than falling back
     to inline when no pool started. Owner: 02-01 Task 1". The recommendation above was
     adopted unchanged.

2. **What is `SPUR_BUILD_TIMEOUT`'s literal default value?**
   - What we know: D-10 fixes the rule ("set above the worst measured build") but leaves
     the number to Claude's Discretion, set *from* the measurement.
   - What's unclear: this research session did not run the actual build-time sweep (that
     is execution work, not research — L08 forbids reporting a number that wasn't
     measured), so no candidate value is offered here.
   - Recommendation: the plan should make "run the sweep, then set the constant" an
     explicit task with its own verification step, not a value picked during planning.
   - **RESOLVED — no literal value was picked at planning time, by design.** Plan 02-03
     ships a provisional default carrying a comment that says so; Plan 02-04's
     "Re-run both load scenarios, and set the timeout above what was observed" task runs
     the sweep and replaces it with a number above the worst build actually observed,
     recorded in `bench/RESULTS.md`. Its acceptance criteria require that no provisional
     comment from 02-03 survives.

3. **Does `max_tasks_per_child` end up enabled or not?**
   - What we know: D-11 says "only if the sweep shows drift that trim does not flatten."
   - What's unclear: outcome is empirical and depends on the actual sweep this research
     did not run.
   - Recommendation: plan should include both code paths as trivial to wire (the
     `ProcessPoolExecutor` constructor already accepts the kwarg per the verified
     signature above) and gate the decision on the sweep's own numbers, recorded in L17.
   - **RESOLVED — the outcome stays empirical, and the plan gates it.** Plan 02-04's
     memory-sweep task enables `max_tasks_per_child` only if the sweep shows drift that
     `malloc_trim(0)` did not flatten, and requires the deciding numbers in the comment
     either way — an absent knob with no comment reads as an oversight. Plan 02-05 records
     the outcome in L17.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Docker | D-17's container-side memory measurement, `make check`/`make bench` | ✓ | `[VERIFIED: docker --version, this session]` Docker 29.4.0, build 9d7ad9f | — |
| python3.12 (host) | `make venv`, host-side latency measurement (`make serve`) | ✓ | `[VERIFIED: python3.12 --version, this session]` Python 3.12.13 | python3.10/3.11 also acceptable per `Makefile`'s interpreter search |
| glibc `malloc_trim` | D-11's per-worker arena release | ✗ on this dev machine | — | Darwin/macOS has no `libc.so.6`; `_load_malloc_trim` already returns `None` gracefully (existing code, unchanged). D-17 already routes the memory claim through the container, where glibc is present, so this is not a blocker — see Pitfall 3. |
| A machine matching the debt file's "12-core" baseline | Reproducing absolute latency numbers exactly | ✗ (this session's environment is a different, arm64 machine) | `[VERIFIED: uname -a, this session]` Darwin 27.0.0, arm64 | D-17's ratio-based acceptance criterion (p95 within 2× of idle p95) is architecture-independent; only the *comparable-baseline* framing needs the executor to record their own machine's arch/cores/RAM per D-17, not to match the original machine |

**Missing dependencies with no fallback:** none.

**Missing dependencies with fallback:** `malloc_trim` on the local dev machine (fallback:
measure in the container, already mandated by D-17); the exact original benchmark
hardware (fallback: record new machine's specs and use the ratio-based criterion, already
mandated by D-17).

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (`pytest>=8` dev extra), `httpx>=0.27` for `TestClient` `[VERIFIED: pyproject.toml, read this session]` |
| Config file | `pyproject.toml` `[tool.pytest.ini_options]` — `testpaths = ["tests"]`, `xfail_strict = true`, `filterwarnings = ["error", ...]` |
| Quick run command | `.venv/bin/python -m pytest tests/test_api.py tests/test_model.py -q` |
| Full suite command | `make test` (i.e. `$(PY) -m pytest`, ~11 s warm per L13/packaging.md) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| REQ-cad-off-event-loop | `app.py` no longer imports `model`/`cadquery` (D-02) | import-linter contract | `.venv/bin/lint-imports` (via `make verify`) | ❌ Wave 0 — new contract entry needed in `pyproject.toml` |
| REQ-cad-off-event-loop | Most API tests exercise the export inline, unaffected by pool state | unit/integration | `.venv/bin/python -m pytest tests/test_api.py -q` | ✅ existing 11 tests, adapted for D-09's `MAX_QUEUED_BUILDS` derivation |
| REQ-cad-off-event-loop | One real end-to-end build crosses the process boundary | integration (real subprocess) | `.venv/bin/python -m pytest tests/test_api.py::test_a_real_worker_builds_and_downloads -q` | ❌ Wave 0 — new test, must use `with TestClient(app) as client:` (Pattern 3) |
| REQ-cad-off-event-loop | `BuildError` → 422, `BrokenProcessPool` → 503, timeout → 503, each with correct `Retry-After`/`type` shape | unit/integration | extend `tests/test_api.py` | ❌ Wave 0 — new tests per D-12's three failure modes |
| REQ-cad-off-event-loop | `/api/health` p95 stays within 2× idle p95 under the two load scenarios | manual-only (load harness, not `make verify`) | `make bench` (D-16) | ❌ Wave 0 — harness itself is new, per D-16 |
| REQ-measured-memory-ceiling | Memory sweep across N=1,2,4 over the 40-gear corpus produces a peak-per-N table | manual-only (load harness) | `make bench` (D-16/D-18) | ❌ Wave 0 — harness, container-side |
| REQ-measured-memory-ceiling | `compose.yaml` `mem_limit` re-run at the chosen value shows zero failures over the corpus | manual-only | `make bench` variant / `docker compose up` + sweep script | ❌ Wave 0 |
| REQ-measured-memory-ceiling | `docs/architecture/decision_log.md` gains L17/L18 superseding entries | doc/manual check | none (human-verified content) | N/A |

### Sampling Rate
- **Per task commit:** `.venv/bin/python -m pytest tests/test_api.py -q` (fast, no Docker, matches D-15's design intent)
- **Per wave merge:** `make verify` (full gate, ~11 s warm per L13)
- **Phase gate:** `make verify` green, plus one manual `make bench` run (D-16) producing the numbers success criteria 1–2 require, before `/gsd-verify-work`

### Wave 0 Gaps
- [ ] `src/spur/build_errors.py` (or discretionary name) — the kernel-free `BuildError` module D-02 requires
- [ ] New import-linter contract: `spur.app` forbidden from `cadquery`/`OCP`, `allow_indirect_imports = false`
- [ ] `tests/test_api.py::test_a_real_worker_builds_and_downloads` — the one real e2e test (D-15), using `with TestClient(app) as client:`
- [ ] Tests for the three D-12 failure-mode → status-code mappings (`BuildError`/`BrokenProcessPool`/timeout)
- [ ] `bench/` (or `docker/`, per discretion) harness + `make bench` target (D-16), implementing both load scenarios and the N=1,2,4 memory sweep over the existing 40-gear corpus (reuse `docs/plan-2026-09-21.md`'s F2 corpus/methodology, don't invent a new one)
- [ ] Regression test asserting `hasattr(ProcessPoolExecutor_instance, "_processes")` so a future CPython release silently breaking D-10's termination path fails `make verify` loudly (see Assumption A3)

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | Out of scope — `REQ-no-auth-default` is a deliberate, separately-tracked decision (L-series, `docs/tech_debt/active/2026-09-21-no-authentication.md`); this phase does not touch it |
| V3 Session Management | no | No sessions in this application |
| V4 Access Control | no | No access-control surface changes in this phase |
| V5 Input Validation | yes (unchanged) | `GearParams`'s own Pydantic validators (L03) — this phase does not add new externally-controlled input surface; the same query parameters cross the same validation as before, just get built by a worker instead of inline |
| V6 Cryptography | no | Not applicable — no cryptographic operations in this phase |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Denial of service via a deliberately expensive gear (large tooth count, fine quality) wedging a worker indefinitely | Denial of Service | D-10's timeout + forced termination (Pattern 2) already addresses this; without it, a single crafted request could permanently degrade 1/N of the pool's capacity (D-07's affinity makes this worse, not better, without the timeout) |
| Resource exhaustion via the byte-cache or solid-cache growing unbounded | Denial of Service | Already bounded (L07's `_BlobCache`/`lru_cache`, unchanged by D-06 beyond relocation); no new risk introduced |
| Pickled data crossing the process boundary containing unexpected types | Tampering (low relevance here) | `GearParams` is a closed, validated Pydantic model — confirmed picklable/hashable this session (`[VERIFIED: .venv/bin/python pickle round-trip test, this session — "picklable: True True"]`); nothing arbitrary crosses the boundary, so this is a low-relevance pattern for this specific phase, noted for completeness |

## Sources

### Primary (HIGH confidence — verified against the installed interpreter/library this session)
- CPython 3.12.13 `concurrent.futures` — `ProcessPoolExecutor.__init__`, `.shutdown`, and `BrokenProcessPool`'s MRO, inspected via `inspect.signature`/`__mro__` in `.venv/bin/python`
- CPython 3.12.13 `asyncio.AbstractEventLoop.run_in_executor` signature, inspected the same way
- `starlette==1.6.0` / `fastapi==0.141.1` `TestClient` lifespan behavior — empirically reproduced with a minimal app this session
- This repo's own files, read in full this session: `src/spur/app.py`, `src/spur/model.py`, `src/spur/cli.py`, `src/spur/params.py`, `src/spur/__init__.py`, `pyproject.toml`, `compose.yaml`, `Dockerfile`, `Makefile`, `docker/smoke.py`, `docs/architecture/decision_log.md`, `docs/architecture/overview.md`, `docs/architecture/packaging.md`, `docs/architecture/http-api.md`, `docs/tech_debt/active/2026-09-21-cad-builds-block-the-event-loop.md`, `docs/tech_debt/active/2026-09-21-no-server-side-cancellation.md`, `docs/tech_debt/INDEX.md`, `docs/plan-2026-09-21.md`, `.github/workflows/ci.yml`, `README.md` (env var table), `tests/test_api.py`

### Secondary (MEDIUM confidence)
- None used — no WebSearch was performed for this phase; all facts needed were either
  already locked in CONTEXT.md's decisions or independently checkable against the
  installed toolchain and this repo's own history (`docs/plan-2026-09-21.md`'s prior
  memory-sweep methodology).

### Tertiary (LOW confidence)
- None — every claim above is either `[VERIFIED: ...]` against a tool run this session,
  a direct quote/citation of this repo's own committed files, or explicitly `[ASSUMED]`
  and logged in the Assumptions table.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — no new libraries, every stdlib signature used in the code
  examples was checked against the actual installed interpreter this session
- Architecture: HIGH for mechanics (verified), MEDIUM for the "why" reasoning behind
  choices already locked by CONTEXT.md (those decisions are the planner's inputs, not
  this research's to re-derive)
- Pitfalls: HIGH — all five were reproduced or directly confirmed against real code/tools
  this session, not inferred from training data alone
- Absolute performance/memory numbers: **not measured in this research pass** — L08
  forbids reporting a number that wasn't measured on the real target; D-16/D-17's harness
  is what produces those during execution, not during research

**Research date:** 2026-09-22
**Valid until:** 30 days (stdlib mechanics are stable; re-check if the project's Python
floor or pinned FastAPI/Starlette versions change before execution starts)
