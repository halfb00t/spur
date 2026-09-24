import logging
import re
from collections.abc import Iterator
from concurrent.futures.process import BrokenProcessPool
from typing import Any, cast

import pytest
from fastapi.testclient import TestClient

from spur.app import STATIC, app, build_backend
from spur.build_errors import BuildError, BuildTimeout
from spur.calc import DerivedDimensions
from spur.model import Format, Quality, export
from spur.params import GearParams

client = TestClient(app)


async def _inline_backend(p: GearParams, fmt: str, quality: str) -> bytes:
    # build_backend's BuildBackend type is str/str (app.py has no static import path to
    # model.Format/model.Quality to name them with, D-02); this override does, so the
    # cast just narrows back to what export() actually wants.
    return export(p, cast(Format, fmt), cast(Quality, quality))


@pytest.fixture(autouse=True, scope="module")
def _inline_build_backend() -> Iterator[None]:
    """Override the pool-backed dependency with an in-process build, for every test here.

    The module-level `client = TestClient(app)` above never runs the app's lifespan (it
    is used without `with` -- see tests/test_pool.py's comment for why), so app.state.pool
    never exists for these tests. Overriding the dependency directly means these 12 tests
    exercise the exact code path the CLI takes (D-15) and never depend on lifespan state.
    tests/test_pool.py deliberately does not install this override, to prove the pool
    path for real.
    """
    app.dependency_overrides[build_backend] = lambda: _inline_backend
    yield
    app.dependency_overrides.pop(build_backend, None)


def test_health() -> None:
    body = client.get("/api/health").json()
    assert body["status"] == "ok"
    # D-06: pool is present-and-null under the bare client, not absent.
    assert "pool" in body
    assert body["pool"] is None


def test_index_and_static() -> None:
    assert "spur" in client.get("/").text
    assert client.get("/static/app.js").status_code == 200
    assert client.get("/static/vendor/three.bundle.min.js").status_code == 200


def test_schema_drives_the_form() -> None:
    props = client.get("/api/schema").json()["properties"]
    assert props["teeth"]["group"] == "Teeth"
    assert props["module"]["unit"] == "mm"
    assert props["recess_sides"]["enum"] == ["both", "top", "bottom", "none"]


def test_openapi_documents_the_typed_contracts() -> None:
    """D-11, the info half (Plan 04-02 adds the health half to this same function).

    The field names are written out literally here, not derived from
    DerivedDimensions.model_fields -- a renamed field, or a route that lost its typed
    return annotation, must fail this test rather than pass tautologically.
    """
    schema = client.get("/openapi.json").json()

    info_response = schema["paths"]["/api/info"]["get"]["responses"]["200"]
    assert info_response["content"]["application/json"]["schema"] == {
        "$ref": "#/components/schemas/DerivedDimensions"}

    fields = {
        "pitch_d", "tip_d", "root_d", "base_d", "caliper_over_tips", "tip_thickness",
        "root_thickness", "root_gap", "root_fillet", "span_teeth", "span",
        "bore_effective", "recess_id", "recess_od", "recess_fillet", "web", "warnings",
        "mate_teeth", "centre_distance",
    }
    component = schema["components"]["schemas"]["DerivedDimensions"]
    assert set(component["properties"]) == fields
    # The null-over-absent invariant (D-01): a field with a default drops out of
    # `required` in OpenAPI (Pitfall 2), so a field that quietly regained one would show
    # up here first.
    assert set(component["required"]) == fields

    assert component["properties"]["pitch_d"]["unit"] == "mm"
    assert component["properties"]["centre_distance"]["unit"] == "mm"  # nullable, still a length
    assert "unit" not in component["properties"]["span_teeth"]

    health_response = schema["paths"]["/api/health"]["get"]["responses"]["200"]
    assert health_response["content"]["application/json"]["schema"] == {
        "$ref": "#/components/schemas/HealthReport"}

    health_component = schema["components"]["schemas"]["HealthReport"]
    assert set(health_component["required"]) == {"status", "version", "pool"}

    pool_component = schema["components"]["schemas"]["PoolState"]
    assert set(pool_component["required"]) == {
        "workers", "queue_available", "workers_replaced"}


def test_every_key_the_ui_reads_is_a_derived_dimensions_field() -> None:
    """D-12: a renamed or dropped field silently blanks a row of the UI, and there is no
    browser test to catch it (the browser-test idea is deferred, CONTEXT.md). This checks
    one direction only -- a new model field with no DIMS row is not caught, and that is
    deliberate.
    """
    source = (STATIC / "app.js").read_text()
    # Each DIMS row starts with `['key', ...` at the top of its line; verified against
    # the shipped file to extract exactly the 15 DIMS keys and nothing else (04-01-PLAN.md
    # Task 2's action).
    dims_keys = re.findall(r"^\s*\['(\w+)',", source, re.MULTILINE)
    assert len(dims_keys) >= 15  # a regex that silently stopped matching must fail, not pass

    for read_form in (".span_teeth", "info.centre_distance", "info.warnings"):
        assert read_form in source

    model_fields = set(DerivedDimensions.model_fields)
    assert set(dims_keys) <= model_fields
    assert {"span_teeth", "centre_distance", "warnings"} <= model_fields


def test_info_reports_the_mate() -> None:
    r = client.get("/api/info", params={"teeth": 21, "mate_teeth": 40})
    assert r.status_code == 200
    assert r.json()["centre_distance"] == pytest.approx(1.75 * 61 / 2)


def test_infeasible_is_422_with_fields() -> None:
    r = client.get("/api/info", params={"bore_flat": 3})
    assert r.status_code == 422
    detail = r.json()["detail"][0]
    assert "D-flat" in detail["msg"]
    assert detail["ctx"]["fields"] == ["bore_flat"]


def test_bad_type_is_422_on_the_field() -> None:
    r = client.get("/api/info", params={"teeth": "many"})
    assert r.status_code == 422
    assert r.json()["detail"][0]["loc"] == ["query", "teeth"]


@pytest.mark.parametrize(("fmt", "ctype", "magic"), [
    ("stl", "model/stl", None),
    ("step", "model/step", b"ISO-10303-21;"),
])
def test_model_download(fmt: str, ctype: str, magic: bytes | None) -> None:
    r = client.get(f"/api/model.{fmt}", params={"quality": "preview", "teeth": 21})
    assert r.status_code == 200
    assert r.headers["content-type"] == ctype
    assert r.headers["content-disposition"] == f'attachment; filename="spur_z21_m1.75_pa25.{fmt}"'
    if magic:
        assert r.content.startswith(magic)


def test_unknown_format_is_rejected() -> None:
    assert client.get("/api/model.obj").status_code == 422


SMALL_GEAR = {"teeth": 6, "pressure_angle": 14.5, "profile_shift": -0.6,
              "bore_d": 0, "bore_flat": 0, "bore_chamfer": 0, "recess_sides": "none"}


def test_impossible_mate_is_a_warning_not_a_number() -> None:
    r = client.get("/api/info", params={**SMALL_GEAR, "mate_teeth": 40})
    assert r.status_code == 200
    body = r.json()
    assert body["mate_teeth"] == 40
    assert body["centre_distance"] is None
    assert any("cannot mesh" in w for w in body["warnings"])


def test_a_gear_too_small_for_the_stock_recess_is_still_served() -> None:
    r = client.get("/api/model.stl", params={"teeth": 24, "module": 1,
                                             "pressure_angle": 20, "bore_flat": 0,
                                             "quality": "preview"})
    assert r.status_code == 200
    assert client.get("/api/info", params={"teeth": 24, "module": 1, "pressure_angle": 20,
                                           "bore_flat": 0}).json()["recess_id"] is not None


def test_a_saturated_service_refuses_instead_of_queueing() -> None:
    """A queue deeper than the pool can drain is latency with no payoff (D-09)."""
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


def test_a_saturated_service_emits_queue_refused_naming_the_gear_and_the_ceiling(
        caplog: pytest.LogCaptureFixture) -> None:
    """D-09, D-10, D-15: a refusal says which gear was turned away and how close to
    the ceiling the service was, at WARNING -- capacity, not breakage."""
    from spur import app as app_module

    caplog.set_level(logging.INFO)
    # Same synthetic-saturation shape as test_a_saturated_service_refuses_instead_of_
    # queueing above: the semaphore is exhausted directly, not through _build_slot, so
    # the parent's own `_in_flight_builds` counter is whatever it already reads (0 in
    # this synthetic scenario, since no real slot holder incremented it) -- captured
    # here rather than hardcoded, so the assertion checks the record against the
    # module's own counter, not a value this test happens to expect.
    in_flight_before = app_module._in_flight_builds
    held = [app_module.BUILD_QUEUE.acquire(blocking=False)
            for _ in range(app_module.MAX_QUEUED_BUILDS)]
    try:
        assert all(held)
        r = client.get("/api/model.stl", params={"quality": "preview", "teeth": 72})
        assert r.status_code == 503
    finally:
        for _ in held:
            app_module.BUILD_QUEUE.release()
    assert caplog.records  # Pitfall 1: an empty caplog would pass with nothing proven

    refused = _event_records(caplog, "queue.refused")
    assert len(refused) == 1
    assert refused[0].levelno == logging.WARNING
    assert _field(refused[0], "request")
    assert _field(refused[0], "slug")
    assert _field(refused[0], "in_flight") == in_flight_before
    assert _field(refused[0], "max_queued") == app_module.MAX_QUEUED_BUILDS

    assert not _event_records(caplog, "export.served")
    assert not _event_records(caplog, "build.started")
    # WR-01 (review fix) regression: the catch-all `except Exception` model() gained
    # must not also fire for _build_slot()'s own admission-control HTTPException --
    # that would duplicate this queue.refused record as a spurious build.failed one.
    assert not _event_records(caplog, "build.failed")


def test_max_queued_builds_is_derived_from_build_workers(
        monkeypatch: pytest.MonkeyPatch) -> None:
    """One knob moves both, so a deployer cannot configure a queue deeper than the pool
    can drain (D-09) -- SPUR_MAX_QUEUED_BUILDS still overrides the derivation when set."""
    from spur import app as app_module

    monkeypatch.delenv("SPUR_BUILD_WORKERS", raising=False)
    monkeypatch.delenv("SPUR_MAX_QUEUED_BUILDS", raising=False)
    assert app_module._max_queued_builds() == 4  # 2 x the default 2 workers

    monkeypatch.setenv("SPUR_BUILD_WORKERS", "3")
    assert app_module._max_queued_builds() == 6

    monkeypatch.setenv("SPUR_MAX_QUEUED_BUILDS", "1")
    assert app_module._max_queued_builds() == 1  # explicit override still wins


def test_the_export_cache_refuses_a_blob_bigger_than_its_budget() -> None:
    """A _BlobCache never reports a stored size above its budget (D-06)."""
    from spur import app as app_module

    cache = app_module._BlobCache(budget=10)
    cache.put("fits", b"12345")
    assert cache.get("fits") == b"12345"

    cache.put("too_big", b"x" * 20)
    assert cache.get("too_big") is None


def test_a_second_identical_download_is_served_from_the_byte_cache() -> None:
    """The parent's byte cache means a repeat download never reaches a worker (D-06)."""
    from spur import app as app_module

    calls = 0

    async def counting_backend(p: GearParams, fmt: str, quality: str) -> bytes:
        nonlocal calls
        calls += 1
        return export(p, cast(Format, fmt), cast(Quality, quality))

    app_module.app.dependency_overrides[build_backend] = lambda: counting_backend
    try:
        params = {"quality": "preview", "teeth": 22}
        first = client.get("/api/model.stl", params=params)
        second = client.get("/api/model.stl", params=params)
    finally:
        app_module.app.dependency_overrides[build_backend] = lambda: _inline_backend

    assert first.status_code == second.status_code == 200
    assert first.content == second.content
    assert calls == 1


def test_a_gzip_client_gets_compressed_bytes_an_identity_client_gets_the_raw_file() -> None:
    """One encoding's bytes must never be served under another's label (T-QWR-03)."""
    params = {"quality": "preview", "teeth": 31}

    gzip_resp = client.get("/api/model.stl", params=params)
    assert gzip_resp.status_code == 200
    assert gzip_resp.headers["content-encoding"] == "gzip"
    assert "accept-encoding" in gzip_resp.headers["vary"].lower()

    identity_resp = client.get("/api/model.stl", params=params,
                               headers={"Accept-Encoding": "identity"})
    assert identity_resp.status_code == 200
    assert "content-encoding" not in identity_resp.headers
    assert not identity_resp.content.startswith(b"\x1f\x8b")  # not gzip magic -- a raw STL

    # httpx decodes the gzip response transparently (hard_fact_8): decoded bytes must
    # equal the identity bytes exactly, or a client silently gets the wrong gear.
    assert gzip_resp.content == identity_resp.content


def test_a_gear_is_compressed_once_per_cache_fill_not_once_per_download(
        monkeypatch: pytest.MonkeyPatch) -> None:
    """A repeat gzip download must hit the cached compressed bytes, not recompress."""
    from spur import app as app_module

    calls = 0
    original = app_module._gzip

    def counting_gzip(data: bytes) -> bytes:
        nonlocal calls
        calls += 1
        return original(data)

    monkeypatch.setattr(app_module, "_gzip", counting_gzip)

    params = {"quality": "preview", "teeth": 32}
    first = client.get("/api/model.stl", params=params)
    second = client.get("/api/model.stl", params=params)

    assert first.status_code == second.status_code == 200
    assert first.content == second.content
    assert calls == 1


def test_a_cache_hit_that_still_needs_compressing_goes_through_admission_control() -> None:
    """The gear is already built; only the compression itself can refuse this request --
    exactly the property a naive cache-hit-bypasses-the-slot implementation would fail to
    deliver (hard_fact_2)."""
    from spur import app as app_module

    params = {"quality": "preview", "teeth": 33}

    # Warm only the raw bytes.
    warm = client.get("/api/model.stl", params=params, headers={"Accept-Encoding": "identity"})
    assert warm.status_code == 200

    held = [app_module.BUILD_QUEUE.acquire(blocking=False)
            for _ in range(app_module.MAX_QUEUED_BUILDS)]
    try:
        assert all(held)
        r = client.get("/api/model.stl", params=params)
        assert r.status_code == 503
        assert r.headers["retry-after"] == "5"
        assert r.json()["detail"][0]["type"] == "busy"
    finally:
        for _ in held:
            app_module.BUILD_QUEUE.release()


def test_an_already_compressed_download_needs_no_slot_at_all() -> None:
    """Once a gear's gzip bytes are cached, a repeat download takes zero slots -- the E2c
    scenario (measured at 4.33x and 5.52x) becoming free."""
    from spur import app as app_module

    params = {"quality": "preview", "teeth": 33}

    # Fill the gzip cache too (raw bytes already warm from the previous test; slots free).
    first = client.get("/api/model.stl", params=params)
    assert first.status_code == 200
    assert first.headers["content-encoding"] == "gzip"

    held = [app_module.BUILD_QUEUE.acquire(blocking=False)
            for _ in range(app_module.MAX_QUEUED_BUILDS)]
    try:
        assert all(held)
        r = client.get("/api/model.stl", params=params)
        assert r.status_code == 200
    finally:
        for _ in held:
            app_module.BUILD_QUEUE.release()


def _event_records(caplog: pytest.LogCaptureFixture, event: str) -> list[logging.LogRecord]:
    """The records this module's helpers emitted for one literal event name (D-16).
    `getattr(..., None)` (not a plain attribute access): `caplog.records` also holds
    records from other loggers (httpx logs its own "HTTP Request" line at INFO once
    anything sets the root level there), and those carry no `event` attribute at all."""
    return [rec for rec in caplog.records if getattr(rec, "event", None) == event]


def _field(rec: logging.LogRecord, name: str) -> Any:
    """Read a field one of this module's per-event helpers attached via `extra=`, on a
    record already selected by `_event_records` -- so the field is known present.
    LogRecord's stub declares no such attribute, so mypy --strict needs an explicit
    `Any` read; ruff's B009 ("no getattr with a constant") does not fire here because
    `name` is a parameter, not a literal, at this call site.
    """
    return getattr(rec, name)


def test_a_fresh_build_emits_build_started_then_export_served_with_source_built(
        caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.INFO)
    r = client.get("/api/model.stl", params={"quality": "preview", "teeth": 61})
    assert r.status_code == 200
    assert caplog.records  # Pitfall 1: an empty caplog would pass with nothing proven

    assert _event_records(caplog, "build.started")
    served = _event_records(caplog, "export.served")
    assert len(served) == 1
    assert _field(served[0], "source") == "built"
    assert _field(served[0], "request")
    assert _field(served[0], "slug")


def test_a_repeat_download_is_served_from_cache_with_zero_duration_and_no_build_started(
        caplog: pytest.LogCaptureFixture) -> None:
    params = {"quality": "preview", "teeth": 62}
    client.get("/api/model.stl", params=params)  # warm the byte cache

    caplog.clear()
    caplog.set_level(logging.INFO)
    r = client.get("/api/model.stl", params=params)
    assert r.status_code == 200
    assert caplog.records

    assert not _event_records(caplog, "build.started")
    served = _event_records(caplog, "export.served")
    assert len(served) == 1
    assert _field(served[0], "source") == "cache"
    assert _field(served[0], "duration_ms") == 0


def test_a_gzip_request_after_an_identity_download_emits_source_compressed(
        caplog: pytest.LogCaptureFixture) -> None:
    """Raw bytes are already cached; only this encoding is not -- the path quick task
    260923-qwr found behind the concurrent-latency ratios (D-11)."""
    params = {"quality": "preview", "teeth": 63}
    client.get("/api/model.stl", params=params, headers={"Accept-Encoding": "identity"})

    caplog.clear()
    caplog.set_level(logging.INFO)
    r = client.get("/api/model.stl", params=params)
    assert r.status_code == 200
    assert caplog.records

    served = _event_records(caplog, "export.served")
    assert len(served) == 1
    assert _field(served[0], "source") == "compressed"
    assert _field(served[0], "duration_ms") > 0


def test_an_all_default_gear_logs_params_as_an_empty_object_not_omitted(
        caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.INFO)
    r = client.get("/api/model.stl", params={"quality": "preview"})
    assert r.status_code == 200
    assert caplog.records

    served = _event_records(caplog, "export.served")
    assert len(served) == 1
    assert _field(served[0], "params") == {}


def test_two_requests_for_one_gear_get_two_different_request_ids(
        caplog: pytest.LogCaptureFixture) -> None:
    """Two concurrent requests for the same gear are the one case params + time cannot
    disambiguate (D-13, D-07's same-slot affinity)."""
    caplog.set_level(logging.INFO)
    params = {"quality": "preview", "teeth": 64}
    client.get("/api/model.stl", params=params)
    client.get("/api/model.stl", params=params)
    assert caplog.records  # Pitfall 1: an empty caplog would pass with nothing proven

    served = _event_records(caplog, "export.served")
    assert len(served) == 2
    assert _field(served[0], "request") != _field(served[1], "request")


@pytest.mark.parametrize(("exc", "want_level", "want_exception"), [
    (BuildError("D-flat too small for this bore"), logging.WARNING, "BuildError"),
    (BuildTimeout("Build exceeded the 30s per-build timeout."), logging.ERROR, "BuildTimeout"),
    (BrokenProcessPool("worker died"), logging.ERROR, "BrokenProcessPool"),
])
def test_a_failed_build_emits_build_failed_naming_the_class_and_the_level(
        caplog: pytest.LogCaptureFixture, exc: Exception, want_level: int,
        want_exception: str) -> None:
    """D-08, D-15: the level says whose fault it is -- BuildError (the user's gear,
    422) is a WARNING, the two 503 classes are ERROR."""
    caplog.set_level(logging.INFO)

    async def backend(p: GearParams, fmt: str, quality: str) -> bytes:
        raise exc

    app.dependency_overrides[build_backend] = lambda: backend
    try:
        # teeth=71: a count no other test in this suite ever successfully downloads
        # (test_pool.py's own such test picks 43/44 for the same reason), so the
        # shared byte cache can never short-circuit this request before the raising
        # backend runs.
        r = client.get("/api/model.stl", params={"quality": "preview", "teeth": 71})
    finally:
        app.dependency_overrides[build_backend] = lambda: _inline_backend
    assert r.status_code in (422, 503)
    assert caplog.records  # Pitfall 1: an empty caplog would pass with nothing proven

    failed = _event_records(caplog, "build.failed")
    assert len(failed) == 1
    assert failed[0].levelno == want_level
    assert _field(failed[0], "exception") == want_exception
    assert _field(failed[0], "request")
    assert _field(failed[0], "slug")
    assert _field(failed[0], "params") is not None
    assert _field(failed[0], "duration_ms") is not None

    assert not _event_records(caplog, "export.served")


def test_an_unclassified_exception_still_emits_build_failed_and_is_not_swallowed(
        caplog: pytest.LogCaptureFixture) -> None:
    """WR-01 (review fix): model()'s three except clauses only covered BuildError/
    BuildTimeout/BrokenProcessPool -- anything else (`_gzip()` under memory pressure, or
    a future violation of model.py's "BuildError is the only exception that escapes"
    contract) propagated uncaught with no build.failed record at all, no exception
    class, nothing from spur's own vocabulary (the CR-01 review found this was the one
    scenario left with no traceback either). The catch-all must log then re-raise, not
    swallow -- the unhandled-error path still has to serve the response, so this test
    drives the exception through `pytest.raises`, not a status-code assertion."""
    caplog.set_level(logging.INFO)

    async def backend(p: GearParams, fmt: str, quality: str) -> bytes:
        raise MemoryError("out of memory compressing bytes")

    app.dependency_overrides[build_backend] = lambda: backend
    try:
        # teeth=73: unused by any other test in this suite (see the teeth=71 comment
        # above), so the shared byte cache can never short-circuit this request.
        with pytest.raises(MemoryError):
            client.get("/api/model.stl", params={"quality": "preview", "teeth": 73})
    finally:
        app.dependency_overrides[build_backend] = lambda: _inline_backend
    assert caplog.records  # Pitfall 1: an empty caplog would pass with nothing proven

    failed = _event_records(caplog, "build.failed")
    assert len(failed) == 1
    assert failed[0].levelno == logging.ERROR  # unrecognised class -> the service's fault
    assert _field(failed[0], "exception") == "MemoryError"
    assert _field(failed[0], "request")
    assert _field(failed[0], "slug")
    assert _field(failed[0], "duration_ms") is not None

    assert not _event_records(caplog, "export.served")
