"""REQ-shaft-api: the shaft on the HTTP API, light (L46, L49, D-07..D-09, D-17).

Light on purpose: a stub `build_backend` returns fixed bytes (or raises) and the export cache
is replaced per test, so no test here builds a solid and the file runs in `make verify.fast`.
The real builds, magic bytes and the cache proof live in tests/test_api.py. What each group
turns red if the code it pins is dropped:

- schema: the `dims` rows carried by `/api/shaft/schema` (a second row table in app.js is
  forbidden by two pins, and the gear schema's bytes are frozen).
- info: the document is `derive_shaft`'s, key order included, and a bad field is a 422 at it.
- as written: the 33-03 rule reaches every shaft number field on both routes.
- download: the name, the error contract and the admission are `_serve_model`'s.
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

import spur.app as app_module
from spur.app import app, build_backend
from spur.build_errors import BuildError
from spur.shaft_calc import ShaftDimensions, derive_shaft
from spur.shaft_params import ShaftParams

client = TestClient(app)

NUMBER_FIELDS = ("reference_d", "module", "teeth", "splined_length", "end_chamfer",
                 "shank_d", "shank_length")


class _Stub:
    """A backend that builds nothing, counts its calls and may be told to fail."""

    def __init__(self) -> None:
        self.calls = 0
        self.error: Exception | None = None

    async def __call__(self, *_: object) -> bytes:
        self.calls += 1
        if self.error is not None:
            raise self.error
        return b"stub"


@pytest.fixture
def stub(monkeypatch: pytest.MonkeyPatch) -> Iterator[_Stub]:
    """A stub backend and a fresh export cache, the prior override put back afterwards."""
    backend = _Stub()
    monkeypatch.setattr(app_module, "_EXPORTS", app_module._BlobCache(1 << 20))
    prior = app.dependency_overrides.get(build_backend)
    app.dependency_overrides[build_backend] = lambda: backend
    try:
        yield backend
    finally:
        if prior is None:
            app.dependency_overrides.pop(build_backend, None)
        else:
            app.dependency_overrides[build_backend] = prior


def _detail(response_json: object) -> list[dict[str, object]]:
    assert isinstance(response_json, dict), response_json
    detail = response_json["detail"]
    assert isinstance(detail, list), response_json
    return detail


# --- the schema and its rows ----------------------------------------------------------


def test_the_schema_is_the_shafts_with_its_result_rows() -> None:
    body = client.get("/api/shaft/schema").json()
    assert body == ShaftParams.model_json_schema()
    assert set(body["properties"]) == set(ShaftParams.model_fields)
    shank = body["properties"]["shank_d"]
    assert shank["enabled_when"] == [{"field": "shank_length", "op": "gt", "value": 0}]


def test_the_rows_are_every_dimension_but_the_warnings_in_order_with_their_own_units() -> None:
    rows = client.get("/api/shaft/schema").json()["dims"]
    keys = [k for k in ShaftDimensions.model_fields if k != "warnings"]
    assert [r["key"] for r in rows] == keys
    for row in rows:
        extra = ShaftDimensions.model_fields[row["key"]].json_schema_extra
        assert isinstance(extra, dict) or extra is None
        assert row["unit"] == (extra or {}).get("unit", "")
        assert isinstance(row["label"], str)
        assert row["label"]
        assert set(row) == {"key", "label", "unit"}


def test_the_unitless_rows_say_so() -> None:
    units = {r["key"]: r["unit"] for r in client.get("/api/shaft/schema").json()["dims"]}
    assert units["profile_shift"] == ""
    assert units["designation"] == ""
    assert units["tip_d"] == "mm"


# --- info -----------------------------------------------------------------------------


def test_info_with_no_query_is_the_default_shafts_document() -> None:
    r = client.get("/api/shaft/info")
    assert r.status_code == 200
    expected = derive_shaft(ShaftParams()).model_dump(mode="json")
    assert r.json() == expected
    assert list(r.json()) == list(expected)


def test_info_follows_the_parameters() -> None:
    r = client.get("/api/shaft/info", params={"reference_d": 30, "module": 2, "teeth": 14})
    assert r.status_code == 200
    expected = derive_shaft(ShaftParams(reference_d=30, module=2, teeth=14))
    assert r.json() == expected.model_dump(mode="json")


@pytest.mark.parametrize(("key", "value"), [("shank_length", "500.5"), ("fit", "8F"),
                                            ("teeth", "many"), ("module", "0.1")])
def test_a_bad_field_is_a_422_at_that_field(key: str, value: str) -> None:
    r = client.get("/api/shaft/info", params={key: value})
    assert r.status_code == 422
    assert _detail(r.json())[0]["loc"] == ["query", key]


def test_an_infeasible_shaft_is_a_422_naming_the_fields() -> None:
    r = client.get("/api/shaft/info", params={"reference_d": 6, "module": 0.5, "teeth": 6})
    assert r.status_code == 422
    assert _detail(r.json())[0]["type"] == "infeasible"


# --- the 33-03 rule on the shaft's number fields --------------------------------------


@pytest.mark.parametrize("path", ["/api/shaft/info", "/api/shaft/model.stl"])
@pytest.mark.parametrize("field", NUMBER_FIELDS)
def test_a_plus_sign_is_refused_as_written_on_every_shaft_number_field(
        stub: _Stub, path: str, field: str) -> None:
    default = ShaftParams.model_fields[field].default
    r = client.get(path, params={field: f"+{default:g}"})
    assert r.status_code == 422
    assert _detail(r.json()) == [
        {"loc": ["query", field], "type": "number_as_written",
         "msg": f'"+{default:g}" is not a number as written; write it as {default:g}'}]
    assert stub.calls == 0


@pytest.mark.parametrize("path", ["/api/shaft/info", "/api/shaft/model.stl"])
def test_a_trailing_dot_is_refused_as_written(stub: _Stub, path: str) -> None:
    r = client.get(path, params={"reference_d": "25."})
    assert r.status_code == 422
    assert _detail(r.json())[0]["type"] == "number_as_written"


# --- the download ---------------------------------------------------------------------


@pytest.mark.parametrize("fmt", ["stl", "step"])
def test_the_default_shaft_downloads_under_its_frozen_name(stub: _Stub, fmt: str) -> None:
    r = client.get(f"/api/shaft/model.{fmt}")
    assert r.status_code == 200
    assert r.content == b"stub"
    name = f"spur_shaft_w25x1.25x18.{fmt}"
    assert r.headers["content-disposition"] == f'attachment; filename="{name}"'
    assert r.headers["content-type"] == {"stl": "model/stl", "step": "model/step"}[fmt]


def test_the_quality_key_belongs_to_the_model_route(stub: _Stub) -> None:
    assert client.get("/api/shaft/model.stl", params={"quality": "preview"}).status_code == 200
    assert client.get("/api/shaft/model.stl", params={"quality": "best"}).status_code == 422


def test_a_build_error_is_a_422_of_type_build_error(stub: _Stub) -> None:
    stub.error = BuildError("the kernel refused")
    r = client.get("/api/shaft/model.stl")
    assert r.status_code == 422
    assert _detail(r.json())[0]["type"] == "build_error"


def test_an_unknown_format_is_rejected(stub: _Stub) -> None:
    assert client.get("/api/shaft/model.obj").status_code == 422
