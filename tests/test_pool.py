"""The one real end-to-end worker test, plus the routing-affinity tests (D-15, D-07).

Every other API test (tests/test_api.py) runs the export inline, in the test process,
via that file's autouse fixture. This file is deliberately different: it is the one
place in the suite that proves a build actually crosses the process boundary, so it
earns its own TestClient idiom -- see the comment on
test_a_real_worker_builds_and_downloads below for why, and don't "fix" it back.
"""

from __future__ import annotations

import asyncio
import multiprocessing as mp
import os
import time
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures.process import BrokenProcessPool

import pytest
from fastapi.testclient import TestClient

from spur.app import ModelQuery, _gear, app, build_backend
from spur.build_errors import BuildError, BuildTimeout
from spur.params import GearParams


def _sleep_past_timeout(seconds: float) -> bytes:
    """Module-level, not a lambda -- `spawn` can only pickle a function it can import
    by qualified name (02-RESEARCH.md's Anti-Patterns; confirmed empirically this
    session with a throwaway pytest run). Returns bytes only to match
    `BuildPool._run_with_timeout`'s `Callable[..., bytes]` contract -- the value is
    never used, only the fact that the call takes `seconds` to return.
    """
    time.sleep(seconds)
    return b""


def _die() -> bytes:
    """Module-level: ends its own worker process immediately, with no Python exception
    and no interpreter teardown -- `os._exit` bypasses both, which is what makes
    `concurrent.futures` detect this as a broken pool rather than a normal task
    failure [VERIFIED this session: a throwaway pytest run confirmed `os._exit(1)`
    inside a worker surfaces as `BrokenProcessPool` from `future.result()`, whereas a
    raised Python exception would surface as that exception instead].
    """
    os._exit(1)


def test_a_real_worker_builds_and_downloads() -> None:
    # `with TestClient(app) as client:` is required here, unlike tests/test_api.py's
    # module-level `client = TestClient(app)` -- only the `with` form sends the ASGI
    # lifespan.startup message that actually creates app.state.pool (verified in
    # 02-RESEARCH.md this session: a bare TestClient(app) never starts lifespan).
    with TestClient(app) as client:
        r = client.get("/api/model.stl", params={"quality": "preview", "teeth": 21})
        assert r.status_code == 200
        assert len(r.content) > 1000

        # Tripwire (RESEARCH.md Pitfall 1): prove the build actually crossed the process
        # boundary, not merely that the inline path would also have returned 200.
        params = GearParams(teeth=21)
        executor = app.state.pool.executor_for(params)
        worker_pid = executor.submit(os.getpid).result()
        assert worker_pid != os.getpid()


def test_the_same_gear_always_reaches_the_same_worker() -> None:
    """Routing-stability property D-07 depends on: same params, same executor, always."""
    with TestClient(app):
        pool = app.state.pool
        a = GearParams(teeth=21)
        b = GearParams(teeth=21)
        assert a is not b
        assert a == b
        assert pool.executor_for(a) is pool.executor_for(a)
        assert pool.executor_for(b) is pool.executor_for(b)
        assert pool.executor_for(a) is pool.executor_for(b)


def test_preview_fine_and_step_share_one_worker() -> None:
    """Preview STL, fine STL and STEP reduce to one GearParams, so one executor (D-07)."""
    with TestClient(app):
        pool = app.state.pool
        preview = _gear(ModelQuery(teeth=21, quality="preview"))
        fine = _gear(ModelQuery(teeth=21, quality="fine"))
        step = _gear(ModelQuery(teeth=21))  # STEP has no quality dimension
        assert pool.executor_for(preview) is pool.executor_for(fine)
        assert pool.executor_for(fine) is pool.executor_for(step)


def test_executor_processes_attribute_still_exists() -> None:
    """Regression guard for Plan 02-03's forced-termination path (RESEARCH.md A3).

    `ProcessPoolExecutor` has no public API to kill a running task -- Plan 02-03's
    timeout->terminate->recreate path reaches the OS process through the private,
    undocumented `_processes` dict (pid -> SpawnProcess). Confirmed present on
    CPython 3.12.13 this session (02-RESEARCH.md, "Pattern 2"); only checked on
    3.12, and this project's CI also runs 3.10 (L14). If a future interpreter
    removes or renames this attribute, this test fails `make verify` loudly instead
    of D-10's termination path silently becoming a no-op.
    """
    executor = ProcessPoolExecutor(max_workers=1, mp_context=mp.get_context("spawn"))
    try:
        executor.submit(os.getpid).result()  # a trivial task, so a worker actually starts
        assert hasattr(executor, "_processes")
        assert executor._processes  # non-empty: at least the one worker just used
    finally:
        # Explicit shutdown: filterwarnings = ["error"] in pyproject.toml turns a
        # leaked subprocess's ResourceWarning into a test failure (L13).
        executor.shutdown(wait=True)


def test_a_wedged_build_is_terminated_and_its_worker_replaced() -> None:
    """D-10, D-12: a build that overruns its per-build timeout is killed, not merely
    abandoned -- the wait ends and the work ends with it -- and the wedged hash slot's
    worker is replaced rather than left dead, so the next request for that slot
    succeeds against a fresh worker."""
    with TestClient(app):
        pool = app.state.pool
        params = GearParams(teeth=21)
        executor = pool.executor_for(params)
        worker_pid_before = executor.submit(os.getpid).result()  # starts the worker
        [proc] = list(executor._processes.values())
        replaced_before = pool.replaced

        original_timeout = pool.timeout
        pool.timeout = 0.2  # short, injected timeout -- a test that waited out the
        # real production default would not be exercising this path (it would just be
        # slow), and 0.2s is well past _sleep_past_timeout's own scheduling overhead.
        try:
            with pytest.raises(BuildTimeout):
                asyncio.run(pool._run_with_timeout(params, _sleep_past_timeout, 5.0))
        finally:
            pool.timeout = original_timeout

        proc.join(timeout=5)  # give the terminated process a moment to actually exit
        assert not proc.is_alive()
        assert pool.replaced == replaced_before + 1

        # the next request routed to the same hash slot succeeds against the fresh worker
        new_pid = pool.executor_for(params).submit(os.getpid).result()
        assert new_pid != worker_pid_before


def test_a_dying_worker_surfaces_as_broken_pool_and_is_replaced() -> None:
    """D-12: a worker that dies unexpectedly (a hard process death, not a Python
    exception) surfaces as BrokenProcessPool from the awaited call, and its slot is
    replaced rather than left dead."""
    with TestClient(app):
        pool = app.state.pool
        params = GearParams(teeth=21)
        replaced_before = pool.replaced

        with pytest.raises(BrokenProcessPool):
            asyncio.run(pool._run_with_timeout(params, _die))

        assert pool.replaced == replaced_before + 1
        # the slot is usable again, against a fresh worker
        assert pool.executor_for(params).submit(os.getpid).result() > 0


@pytest.mark.parametrize(("exc", "want_status", "want_type"), [
    (BuildError("D-flat too small for this bore"), 422, "build_error"),
    (BuildTimeout("Build exceeded the 30s per-build timeout."), 503, "timeout"),
    (BrokenProcessPool("worker died"), 503, "pool_broken"),
])
def test_each_build_failure_mode_maps_to_its_own_status_and_type(
        exc: Exception, want_status: int, want_type: str) -> None:
    """D-12: BuildError -> 422 (unchanged), BuildTimeout -> 503, BrokenProcessPool ->
    503 -- three distinct exception mappings, reusing _build_slot's `503` +
    `Retry-After` + `detail[].type` shape for the two new ones rather than inventing a
    new response contract. Drives each failure via the D-15 injectable build_backend,
    exactly as it's meant to be used: no real worker or build needed for a contract
    test about status codes and body shapes.
    """
    from spur import app as app_module

    async def backend(p: GearParams, fmt: str, quality: str) -> bytes:
        raise exc

    # A plain (non-`with`) TestClient never runs the lifespan (Pitfall 1) -- fine here,
    # since overriding build_backend means the real pool is never consulted.
    client = TestClient(app)
    app.dependency_overrides[build_backend] = lambda: backend
    try:
        capacity_before = app_module.BUILD_QUEUE._value
        # teeth=43: a count no other test in this suite ever successfully downloads,
        # so the parent's byte cache (_EXPORTS, D-06) can never short-circuit this
        # request before the raising backend gets a chance to run (the same reasoning
        # tests/test_api.py's own cache test uses for picking teeth=22 over 21).
        r = client.get("/api/model.stl", params={"quality": "preview", "teeth": 43})
        assert r.status_code == want_status
        detail = r.json()["detail"][0]
        assert detail["type"] == want_type
        if want_status == 503:
            assert r.headers["retry-after"] == "5"
        # the admission slot is released on every failure path (D-12): a repeated
        # failure must never leak capacity and turn into a service that refuses
        # everything -- the failure mode hardest to diagnose from the outside.
        assert app_module.BUILD_QUEUE._value == capacity_before
    finally:
        app.dependency_overrides.pop(build_backend, None)


def test_the_four_failure_types_are_pairwise_distinct() -> None:
    """`busy` (existing, from a saturated queue), `build_error`, `timeout` and
    `pool_broken` (all D-12) must all differ, so a client can tell "your gear is
    impossible" from "come back in a moment" from "something died" from "the queue is
    full" -- checked against the values the app actually returns, not restated
    constants that would trivially agree with themselves.
    """
    from spur import app as app_module

    client = TestClient(app)
    types: set[str] = set()

    # teeth=44: a count no other test in this suite ever successfully downloads (see
    # the comment in test_each_build_failure_mode_maps_to_its_own_status_and_type),
    # so _EXPORTS can never short-circuit any of the four requests below.
    query = {"quality": "preview", "teeth": 44}

    async def _never_called(p: GearParams, fmt: str, quality: str) -> bytes:
        # build_backend is a FastAPI dependency, resolved before the endpoint body
        # runs, on every request regardless of which branch inside it ends up
        # executing -- so even the "busy" sub-case below needs an override in place
        # (a plain TestClient(app), unlike `with TestClient(app):`, never starts the
        # lifespan that would otherwise supply a real one). This tripwire is that
        # override: it must never actually run, because _build_slot's admission check
        # is supposed to refuse the request before backend(...) is ever awaited.
        raise AssertionError("_build_slot should have refused before calling backend")

    app.dependency_overrides[build_backend] = lambda: _never_called
    try:
        held = [app_module.BUILD_QUEUE.acquire(blocking=False)
                for _ in range(app_module.MAX_QUEUED_BUILDS)]
        try:
            r = client.get("/api/model.stl", params=query)
            assert r.status_code == 503
            types.add(r.json()["detail"][0]["type"])
        finally:
            for _ in held:
                app_module.BUILD_QUEUE.release()

        for exc in (BuildError("D-flat too small"),
                    BuildTimeout("Build exceeded the 30s per-build timeout."),
                    BrokenProcessPool("worker died")):
            async def backend(p: GearParams, fmt: str, quality: str,
                               _exc: Exception = exc) -> bytes:
                raise _exc

            app.dependency_overrides[build_backend] = lambda b=backend: b
            r = client.get("/api/model.stl", params=query)
            types.add(r.json()["detail"][0]["type"])
    finally:
        app.dependency_overrides.pop(build_backend, None)

    assert len(types) == 4


def test_health_reports_pool_state() -> None:
    """D-13: /api/health additionally reports pool state -- worker count, remaining
    admission capacity and workers replaced since start -- nested under one `pool` key
    (Task 3 checkpoint decision: option B), without disturbing the existing top-level
    `status`/`version` shape the UI and the container healthcheck already read.
    """
    from spur import app as app_module

    with TestClient(app) as client:
        pool = app.state.pool
        body = client.get("/api/health").json()
        assert body["status"] == "ok"
        assert "version" in body
        assert body["pool"] == {
            "workers": pool.workers,
            "queue_available": app_module.MAX_QUEUED_BUILDS,
            "workers_replaced": pool.replaced,
        }


def test_health_queue_available_falls_while_a_slot_is_held() -> None:
    """Remaining admission capacity in /api/health drops while a build holds a slot and
    returns to full once it's released -- backed by the plain in-flight counter
    `_build_slot` maintains, not `BUILD_QUEUE._value` (02-RESEARCH.md Assumption A4,
    which this plan's Task 4 explicitly rejects reading from app.py).
    """
    from spur import app as app_module

    with TestClient(app) as client:
        full = client.get("/api/health").json()["pool"]["queue_available"]
        with app_module._build_slot():
            held = client.get("/api/health").json()["pool"]["queue_available"]
            assert held == full - 1
        released = client.get("/api/health").json()["pool"]["queue_available"]
        assert released == full


def test_health_workers_replaced_increases_after_a_forced_termination() -> None:
    """`workers_replaced` on /api/health reflects `BuildPool.replaced`, and increases
    after Task 1's timeout-terminate-replace path fires -- proving the reported field
    tracks live pool state rather than being frozen at startup.
    """
    with TestClient(app) as client:
        pool = app.state.pool
        params = GearParams(teeth=21)
        before = client.get("/api/health").json()["pool"]["workers_replaced"]

        original_timeout = pool.timeout
        pool.timeout = 0.2
        try:
            with pytest.raises(BuildTimeout):
                asyncio.run(pool._run_with_timeout(params, _sleep_past_timeout, 5.0))
        finally:
            pool.timeout = original_timeout

        after = client.get("/api/health").json()["pool"]["workers_replaced"]
        assert after == before + 1


def test_health_handler_never_awaits_or_touches_pool_internals() -> None:
    """D-13: the health handler is a plain sync function -- FastAPI never awaits a sync
    route, so a sync `def health()` is itself the structural proof that this endpoint
    performs no `await` on a worker. Guards against a future edit accidentally making it
    `async def` and reaching into the pool's executors.
    """
    from spur.app import health

    assert not asyncio.iscoroutinefunction(health)
