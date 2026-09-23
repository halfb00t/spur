"""The one real end-to-end worker test, plus the routing-affinity tests (D-15, D-07).

Every other API test (tests/test_api.py) runs the export inline, in the test process,
via that file's autouse fixture. This file is deliberately different: it is the one
place in the suite that proves a build actually crosses the process boundary, so it
earns its own TestClient idiom -- see the comment on
test_a_real_worker_builds_and_downloads below for why, and don't "fix" it back.
"""

from __future__ import annotations

import multiprocessing as mp
import os
from concurrent.futures import ProcessPoolExecutor

from fastapi.testclient import TestClient

from spur.app import ModelQuery, _gear, app
from spur.params import GearParams


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
