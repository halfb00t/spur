"""The one real end-to-end worker test, plus the routing-affinity tests (D-15, D-07).

Every other API test (tests/test_api.py) runs the export inline, in the test process,
via that file's autouse fixture. This file is deliberately different: it is the one
place in the suite that proves a build actually crosses the process boundary, so it
earns its own TestClient idiom -- see the comment on
test_a_real_worker_builds_and_downloads below for why, and don't "fix" it back.
"""

from __future__ import annotations

import os

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
