"""Structured logging (Phase 3): the traced proof, the formatter's edges, and the level
knob. tests/test_api.py covers the per-request vocabulary's branches with `caplog`; this
file covers everything specific to `records.py` itself.
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import cast

import pytest
from fastapi.testclient import TestClient

from spur import calc as calc_module
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


def _make_record(**extra: object) -> logging.LogRecord:
    """A LogRecord built the way `03-RESEARCH.md`'s "Code Examples" verified --
    `Logger.makeRecord` with `extra=`, the same mechanism `_emit` uses -- so these tests
    exercise `_JsonFormatter` directly, independent of the logging call site."""
    logger = logging.getLogger("spur.records")
    return logger.makeRecord("spur.records", logging.INFO, __file__, 1,
                             extra.get("event", "test.probe"), (), None, extra=extra)


def test_the_formatter_round_trips_every_application_field_through_json_loads() -> None:
    """D-16's separate formatter proof: a formatter that dropped `extra` could not pass
    this, unlike a branch test that only checks the fields it happens to look at."""
    record = _make_record(event="export.served", request="abc12345", slug="spur_z19",
                          params={"teeth": 19}, duration_ms=42)
    payload = json.loads(records._JsonFormatter().format(record))

    assert payload["event"] == "export.served"
    assert payload["request"] == "abc12345"
    assert payload["slug"] == "spur_z19"
    assert payload["params"] == {"teeth": 19}
    assert payload["duration_ms"] == 42
    for envelope_field in ("ts", "level", "logger", "version"):
        assert envelope_field in payload


def test_a_field_with_a_newline_and_non_ascii_stays_one_physical_line() -> None:
    """The one-record-one-line contract `jq` depends on, whatever the stream's real
    encoding is (edge: encoding) -- the formatter must escape, not emit raw bytes."""
    tricky = "line one\nline two: pressure angle ° façade"
    record = _make_record(event="export.served", note=tricky)
    line = records._JsonFormatter().format(record)

    assert "\n" not in line
    assert json.loads(line)["note"] == tricky


def test_two_records_of_the_same_event_serialize_identical_key_order() -> None:
    """Two records that compare equal on event must not disagree on shape (edge:
    ordering) -- envelope first, then the event's own fields in the order `_emit` built
    them, regardless of what the *values* happen to be."""
    def keys_for(request_value: str) -> list[str]:
        record = _make_record(event="export.served", request=request_value, source="cache")
        return list(json.loads(records._JsonFormatter().format(record)))

    assert keys_for("aaaaaaaa") == keys_for("bbbbbbbb")


def test_ms_is_an_integer_with_half_to_even_rounding() -> None:
    """Never a float (edge: precision); a sub-millisecond duration reads 0; the exact
    half-millisecond tie-break is Python's own round() (half-to-even), pinned as a
    recorded contract rather than left as an accident of the implementation."""
    assert type(records._ms(0.0179)) is int
    assert records._ms(0.00001) == 0            # sub-millisecond
    assert records._ms(0.0025) == 2              # exact 2.5ms tie -> even (2)
    assert records._ms(0.0035) == 4              # exact 3.5ms tie -> even (4)


def test_parse_level_falls_back_to_info_on_nonsense_and_empty() -> None:
    """The same "read once, fall back on nonsense" shape as `int_env` (edges: boundary,
    empty)."""
    assert records._parse_level("INFO") == logging.INFO
    assert records._parse_level("warning") == logging.WARNING  # case-insensitive
    assert records._parse_level("NONSENSE") == logging.INFO
    assert records._parse_level("") == logging.INFO


def test_spur_log_level_moves_the_threshold(
        monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """D-14, driven through the real `configure()` + env var, not just `_parse_level`
    in isolation: with SPUR_LOG_LEVEL=WARNING an INFO record is suppressed and a
    WARNING record still gets through -- one step either side of the threshold."""
    monkeypatch.setenv("SPUR_LOG_LEVEL", "WARNING")
    records.configure()

    records._emit(logging.INFO, "test.info.suppressed", {})
    records._emit(logging.WARNING, "test.warning.visible", {})

    events = [json.loads(line)["event"]
              for line in capsys.readouterr().err.strip().splitlines()]
    assert "test.info.suppressed" not in events
    assert "test.warning.visible" in events


def test_spur_log_level_unset_defaults_to_info(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SPUR_LOG_LEVEL", raising=False)
    records.configure()
    assert logging.getLogger().level == logging.INFO


def test_configure_twice_still_emits_exactly_one_line_per_record(
        capsys: pytest.CaptureFixture[str]) -> None:
    """RESEARCH.md Pitfall 3: the default SPUR_WORKERS=1 deployment runs both call
    sites in one process -- a naive configure() would double every printed line, not
    just double-install the handler."""
    records.configure()
    records.configure()
    handlers = [h for h in logging.getLogger().handlers
                if isinstance(h, records._JsonHandler)]
    assert len(handlers) == 1

    records._emit(logging.INFO, "test.idempotency.probe", {})
    lines = [line for line in capsys.readouterr().err.strip().splitlines()
             if json.loads(line)["event"] == "test.idempotency.probe"]
    assert len(lines) == 1


def test_calc_module_stays_log_free() -> None:
    """L01, REQ boundary: calc.py runs on every keystroke in the UI and must never
    import logging -- cheap insurance against drift into the module that matters most
    to keep pure."""
    source = Path(calc_module.__file__).read_text()
    assert not re.search(r"^\s*(import|from)\s+logging\b", source, re.MULTILINE)
