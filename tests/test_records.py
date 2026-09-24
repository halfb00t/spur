"""Structured logging (Phase 3): the traced proof, the formatter's edges, and the level
knob. tests/test_api.py covers the per-request vocabulary's branches with `caplog`; this
file covers everything specific to `records.py` itself.
"""

from __future__ import annotations

import json
import logging
from typing import cast

import pytest
from fastapi.testclient import TestClient

from spur import records
from spur.app import app, build_backend
from spur.model import Format, Quality, export
from spur.params import GearParams

client = TestClient(app)


async def _inline_backend(p: GearParams, fmt: str, quality: str) -> bytes:
    # Same seam tests/test_api.py uses (D-15): app.state.pool never exists for this
    # module-level TestClient (no `with`, so lifespan never runs), so the dependency is
    # overridden with an in-process build instead.
    return export(p, cast(Format, fmt), cast(Quality, quality))


def test_a_model_request_emits_one_export_served_line_that_json_loads_round_trips(
        capsys: pytest.CaptureFixture[str]) -> None:
    """The one end-to-end check of the one path: configure, the call site, the
    formatter, the handler, the stream -- proven by reading the real stderr output of a
    real request back through `json.loads`, not by inspecting any layer in isolation."""
    records.configure()
    app.dependency_overrides[build_backend] = lambda: _inline_backend
    try:
        resp = client.get("/api/model.stl", params={"quality": "preview", "teeth": 41})
    finally:
        app.dependency_overrides.pop(build_backend, None)
    assert resp.status_code == 200

    # Every line on stderr, not just the last: httpx (the TestClient's own transport)
    # also logs at INFO once the root handler is installed, and its own "HTTP Request"
    # line can land after ours -- a real `spur serve` process has no httpx client
    # logging its own requests, so this is a test-harness artifact, not a production
    # ordering guarantee to assert on.
    lines = capsys.readouterr().err.strip().splitlines()
    assert lines, "configure() should have installed a handler that wrote to stderr"
    served = [record for line in lines
              if (record := json.loads(line)).get("event") == "export.served"]
    assert served, "no export.served record found on stderr"
    record = served[-1]

    assert record["event"] == "export.served"
    for field in ("ts", "level", "logger", "version", "request", "slug", "params",
                  "fmt", "quality", "encoding", "source", "duration_ms"):
        assert field in record, f"missing field: {field}"
    assert record["source"] in ("cache", "compressed", "built")


def test_configure_called_twice_installs_exactly_one_handler() -> None:
    """The default SPUR_WORKERS=1 deployment runs both call sites (cli.cmd_serve and
    app.py's lifespan()) in one process -- a configure() that always added a handler
    would print every production line twice (03-RESEARCH.md Pitfall 3)."""
    records.configure()
    records.configure()
    handlers = [h for h in logging.getLogger().handlers
                if isinstance(h, records._JsonHandler)]
    assert len(handlers) == 1
