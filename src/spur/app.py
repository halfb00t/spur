"""HTTP API and web UI.

    GET /                    web UI
    GET /api/health          liveness
    GET /api/schema          JSON schema of the parameters (drives the UI form)
    GET /api/info?...        derived dimensions, measurement aids, warnings
    GET /api/model.stl?...   binary STL   (quality=preview|fine)
    GET /api/model.step?...  STEP AP214 solid

Every gear parameter is a query string field, so a model URL is shareable and
curl-able. Unset fields take their defaults.
"""

from __future__ import annotations

import threading
from collections import OrderedDict
from collections.abc import AsyncIterator, Awaitable, Callable, Iterator
from concurrent.futures.process import BrokenProcessPool
from contextlib import asynccontextmanager, contextmanager
from pathlib import Path
from typing import Annotated, Any, Literal

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import Field

from . import __version__, int_env
from .build_errors import BuildError, BuildTimeout
from .calc import derive, with_mate
from .params import GearParams
from .pool import BuildPool

STATIC = Path(__file__).parent / "static"
MEDIA_TYPES = {"stl": "model/stl", "step": "model/step"}


class _BlobCache:
    """LRU of exported bytes bounded by total size rather than by entry count.

    Moved here from model.py (D-06): this is now the only exported-bytes cache in the
    whole topology, one instead of N. It needs no lock of its own -- unlike the old
    per-process version, whose docstring claimed callers held model.py's _LOCK, this one
    is the only thing touching its dict, single-threaded, on one event loop, in the one
    uvicorn worker this app runs as (D-01).
    """

    def __init__(self, budget: int) -> None:
        self._budget = budget
        self._items: OrderedDict[Any, bytes] = OrderedDict()
        self._bytes = 0

    def get(self, key: Any) -> bytes | None:
        data = self._items.get(key)
        if data is not None:
            self._items.move_to_end(key)
        return data

    def put(self, key: Any, data: bytes) -> None:
        old = self._items.pop(key, None)
        if old is not None:
            self._bytes -= len(old)
        if len(data) > self._budget:
            return
        self._items[key] = data
        self._bytes += len(data)
        while self._bytes > self._budget:
            self._bytes -= len(self._items.popitem(last=False)[1])


_EXPORTS = _BlobCache(int_env("SPUR_EXPORT_CACHE_MB", 64) * 1024 * 1024)


def _max_queued_builds() -> int:
    """A queue deeper than the pool can drain is latency with no payoff (D-09).

    A function, not a bare module constant, so SPUR_BUILD_WORKERS and
    SPUR_MAX_QUEUED_BUILDS are read together, on every call -- tests exercise all three
    derivation cases via monkeypatch + a direct call, without reloading this module.
    """
    return int_env("SPUR_MAX_QUEUED_BUILDS", 2 * int_env("SPUR_BUILD_WORKERS", 2))


MAX_QUEUED_BUILDS = _max_queued_builds()
BUILD_QUEUE = threading.BoundedSemaphore(MAX_QUEUED_BUILDS)

# D-13: a plain in-flight counter, not BUILD_QUEUE._value -- threading.BoundedSemaphore's
# internal counter is itself a private attribute (02-RESEARCH.md Assumption A4), so this
# module keeps its own instead of reading another module's undocumented internals to
# report the same number. Incremented/decremented only inside _build_slot's own
# acquire/release pair below. With one uvicorn worker (D-01) and this counter only ever
# touched from the event-loop thread, it needs no lock of its own -- that stops being
# true the moment SPUR_WORKERS raises the serving-process count again.
_in_flight_builds = 0

# The type an injected build backend must satisfy -- plain str for fmt/quality (not
# model.Format/model.Quality) because this module has no static import path to model.py
# to name them with (D-02); the endpoint's own Literal types are still checked at the
# call site.
BuildBackend = Callable[[GearParams, str, str], Awaitable[bytes]]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Build the pool eagerly at startup, tear it down at shutdown (D-04).

    Eager, import-only warm-up: the memory sweep then measures steady state from t=0
    instead of a ramp. SPUR_BUILD_WORKERS defaults to a fixed 2, not os.cpu_count() --
    a machine-dependent default would make the measured mem_limit untrue somewhere (D-19).
    """
    app.state.pool = BuildPool(
        int_env("SPUR_BUILD_WORKERS", 2),
        # D-10: set above the worst measured build. bench/latency.py's two load
        # scenarios (bench/RESULTS.md) observed a worst single build of 7.39s (a
        # 200-tooth fine gear, ten concurrent requests, this machine under host
        # contention -- see bench/RESULTS.md's Machine caveat). 30s is ~4x that
        # observation, chosen as margin for hardware slower than the measurement
        # machine (the debt file's own concern: the stall is proportionally worse on
        # slower hardware). Re-measure and adjust if bench/RESULTS.md's worst observed
        # build ever approaches this value.
        int_env("SPUR_BUILD_TIMEOUT", 30),
    )
    try:
        yield
    finally:
        app.state.pool.shutdown()


app = FastAPI(
    title="spur",
    version=__version__,
    summary="Parametric involute spur gear generator with STL/STEP export.",
    lifespan=lifespan,
)
# Measured against the real 9,062,784-byte STL this app serves for teeth=199&quality=fine
# (02-LATENCY-INVESTIGATION.md's own corpus), gzip.compress at levels 1/6/9, host loadavg
# 2.68/3.07/2.78 just before measuring (quiet, but not test-lab-idle -- this run's level-9
# single-threaded 788.0ms is ~34% faster than the investigation's 1181.7ms on a busier
# host that session, consistent with the difference being host load, not the input: the
# compressed byte count at level 9 is 2,404,371 in both runs, so the input is identical):
#
#   level | single-threaded median | output bytes (% of input) | 10-concurrent wall (median of 3)
#   ----- | ----------------------- | -------------------------- | ---------------------------------
#     1   |  51.5 ms                | 2,632,467 (29.0%)          |  74.4 ms
#     6   | 147.9 ms                | 2,403,312 (26.5%)          | 198.9 ms
#     9   | 788.0 ms                | 2,404,371 (26.5%)          | 925.5 ms
#
# Selection rule (02-LATENCY-INVESTIGATION.md): adopt a higher level only if it shrinks
# output by >=10% AND costs <=1.5x the 10-concurrent wall time of the level below it.
# Level 6 over level 1: only 8.7% smaller (229,155 / 2,632,467) -- misses the 10% bar, so
# it is never reached; level 9 over level 1: only 8.66% smaller, also misses it (and its
# concurrent wall is 12.4x level 1's, far past 1.5x regardless). STL triangle data is
# mostly non-repeating 32-bit floats -- there is little redundancy left for a slower zlib
# search to find, so the extra CPU cost buys almost nothing here. Level 1 wins on both
# rule clauses.
_GZIP_LEVEL = 1

app.add_middleware(GZipMiddleware, minimum_size=1024, compresslevel=_GZIP_LEVEL)
app.mount("/static", StaticFiles(directory=STATIC), name="static")


def build_backend() -> BuildBackend:
    """The injectable seam D-15 needs: exposes the pool's export to the endpoint.

    Hard-fails rather than falling back to an inline build when no pool has started: a
    production request that skipped the pool would silently reinstate the event-loop
    stall this phase removes, and would also skip D-07's cache-locality affinity
    (02-RESEARCH.md Open Question 1). Tests override this dependency with an inline
    backend instead (see tests/test_api.py's autouse fixture); the production code path
    never goes inline.
    """
    pool: BuildPool | None = getattr(app.state, "pool", None)
    if pool is None:
        raise RuntimeError("Build pool not started -- did the app's lifespan run?")
    return pool.export


class InfoQuery(GearParams):
    mate_teeth: int | None = Field(None, ge=6, le=1000, title="Mating gear teeth",
                                   description="Also report the centre distance to this gear.")


class ModelQuery(GearParams):
    quality: Literal["preview", "fine"] = Field(
        "fine", description="STL tessellation: preview (coarse, small) or fine.")


def _gear(q: GearParams) -> GearParams:
    """Strip the per-endpoint extras back to a plain GearParams.

    The build caches are keyed on the parameter object, and pydantic equality includes
    the class, so a ModelQuery and an InfoQuery describing the same gear would otherwise
    never hit each other's cache entries.
    """
    return GearParams(**q.model_dump(include=set(GearParams.model_fields)))


@contextmanager
def _build_slot() -> Iterator[None]:
    """Admission control: refuse work we cannot start soon rather than queue it."""
    global _in_flight_builds
    if not BUILD_QUEUE.acquire(blocking=False):
        raise HTTPException(
            503,
            detail=[{"loc": ["query"], "type": "busy",
                     "msg": f"Busy: {MAX_QUEUED_BUILDS} gears are already being built. "
                            "Try again in a moment."}],
            headers={"Retry-After": "5"},
        )
    _in_flight_builds += 1
    try:
        yield
    finally:
        _in_flight_builds -= 1
        BUILD_QUEUE.release()


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(STATIC / "index.html")


@app.get("/api/health")
def health() -> dict[str, Any]:
    """Liveness, plus pool state (D-13) -- parent-local counters only.

    `status` and `version` stay exactly where they are today, at the top level, so the
    container healthcheck and the UI (neither of which reads pool fields today) are
    unaffected. Pool state nests under one `pool` key instead (02-03-PLAN.md Task 3
    checkpoint decision, option B): every later pool field lands inside `pool` without
    touching the published top level, which is what keeps this a reversible decision
    instead of a fresh one-way door each time a field is added.

    This endpoint's p95 under load is Phase 2's headline success criterion
    (02-RESEARCH.md REQ-cad-off-event-loop), so it has to measure the event loop and not
    the pool: a plain `def`, not `async def`, means there is nothing here for FastAPI to
    await, and every value below is an O(1) attribute or counter read -- no lock, no IPC,
    no call into a worker. Querying the workers themselves (the only way to spot one that
    is alive but wedged) was the rejected D-13 variant; it stays deferred in CONTEXT.md
    with its own trigger, because asking a worker how it's doing would make the
    measurement measure the exact thing it's supposed to be independent of.

    `pool` is absent only when `app.state.pool` hasn't been set -- the one path that can
    happen on is a bare `TestClient(app)` used without `with`, which never runs this
    app's lifespan (tests/test_api.py's module-level client does this deliberately, to
    exercise the inline build backend without paying pool startup cost). Every real
    deployment runs the lifespan, so `pool` is always present in production.
    """
    pool: BuildPool | None = getattr(app.state, "pool", None)
    payload: dict[str, Any] = {"status": "ok", "version": __version__}
    if pool is not None:
        payload["pool"] = {
            "workers": pool.workers,
            "queue_available": MAX_QUEUED_BUILDS - _in_flight_builds,
            "workers_replaced": pool.replaced,
        }
    return payload


@app.get("/api/schema")
def schema() -> dict[str, Any]:
    return GearParams.model_json_schema()


@app.get("/api/info")
def info(q: Annotated[InfoQuery, Query()]) -> dict[str, Any]:
    """Derived dimensions. With `mate_teeth`, also the centre distance to that gear."""
    params = _gear(q)
    out = derive(params)
    return with_mate(out, params, q.mate_teeth) if q.mate_teeth else out


@app.get("/api/model.{fmt}", response_class=Response,
         responses={200: {"content": {t: {} for t in MEDIA_TYPES.values()}}})
async def model(fmt: Literal["stl", "step"], q: Annotated[ModelQuery, Query()],
                backend: Annotated[BuildBackend, Depends(build_backend)]) -> Response:
    params = _gear(q)
    key = (params, fmt, q.quality)
    data = _EXPORTS.get(key)
    if data is None:
        try:
            with _build_slot():
                data = await backend(params, fmt, q.quality)
        except BuildError as exc:
            raise HTTPException(422, detail=[{"loc": ["query"], "msg": str(exc),
                                              "type": "build_error"}]) from exc
        except BuildTimeout as exc:
            # 503, not 422 (D-12): the same gear succeeds on faster hardware, so
            # overrunning is a property of this machine and this moment, not of the
            # parameters -- calling it a parameter error would tell the user to change
            # a gear that is fine. Same busy-refusal shape as _build_slot above (reused,
            # not reinvented), with its own `type` so a client can tell "come back in a
            # moment" from "your gear is impossible".
            raise HTTPException(503, detail=[{"loc": ["query"], "msg": str(exc),
                                              "type": "timeout"}],
                                headers={"Retry-After": "5"}) from exc
        except BrokenProcessPool as exc:
            # 503, not 422 (D-12): the worker died, the parameters didn't do anything
            # wrong. BuildPool.export already replaced the dead slot before this
            # propagated here (pool.py's _run_with_timeout); the client just needs to
            # know it can retry.
            raise HTTPException(
                503,
                detail=[{"loc": ["query"],
                         "msg": "A build worker died unexpectedly. The request can be "
                                "retried.",
                         "type": "pool_broken"}],
                headers={"Retry-After": "5"},
            ) from exc
        _EXPORTS.put(key, data)
    return Response(
        data,
        media_type=MEDIA_TYPES[fmt],
        headers={"Content-Disposition": f'attachment; filename="{params.slug()}.{fmt}"'},
    )
