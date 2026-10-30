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
- designation (D-07..D-09): a designation in place of the four spline fields, refused beside
  any of them on key presence, and every bad or infeasible one a 422 at `designation`.
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

import spur.app as app_module
from spur.app import app, build_backend
from spur.build_errors import BuildError
from spur.din5480 import DESIGNATION_MAX_LENGTH, Designation, DesignationError
from spur.shaft_calc import ShaftDimensions, derive_shaft
from spur.shaft_params import (
    SPLINE_KEYS,
    DesignationConflict,
    ShaftParams,
    clash_message,
    designation_clash,
    resolve_shaft,
)

client = TestClient(app)

NUMBER_FIELDS = ("reference_d", "module", "teeth", "splined_length", "end_chamfer",
                 "shank_d", "shank_length")


class _Stub:
    """A backend that builds nothing, counts its calls and may be told to fail."""

    def __init__(self) -> None:
        self.calls = 0
        self.error: Exception | None = None
        self.seen: list[object] = []

    async def __call__(self, params: object, *_: object) -> bytes:
        self.calls += 1
        self.seen.append(params)
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


# --- a designation in place of the spline fields (D-07..D-09) -------------------------

DESIGNATION = "W 30x2x14x8f"
FLAT = {"reference_d": 30, "module": 2, "teeth": 14, "fit": "8f"}
INFO = "/api/shaft/info"


def test_the_spline_keys_are_the_codecs_fields() -> None:
    assert Designation._fields == SPLINE_KEYS


def test_the_clash_is_the_spline_keys_present_in_spline_order() -> None:
    assert designation_clash(["designation", "teeth", "reference_d"]) == ("reference_d", "teeth")
    assert designation_clash(["splined_length", "end_chamfer", "shank_d", "shank_length"]) == ()
    assert designation_clash([]) == ()


def test_the_clash_message_names_every_field_it_refuses() -> None:
    one = clash_message(("teeth",))
    assert "teeth" in one
    assert "reference_d, module, teeth and fit" in one
    two = clash_message(("reference_d", "fit"))
    assert "reference_d and fit" in two
    three = clash_message(("reference_d", "teeth", "fit"))
    assert "reference_d, teeth and fit" in three


def test_resolve_shaft_refuses_a_clash_itself() -> None:
    """A second guard: no caller may let a designation silently win (D-07)."""
    with pytest.raises(DesignationConflict) as caught:
        resolve_shaft(DESIGNATION, {"teeth": 14})
    assert caught.value.fields == ("teeth",)
    assert str(caught.value) == clash_message(("teeth",))


def test_resolve_shaft_combines_a_designation_with_the_solid_fields() -> None:
    p = resolve_shaft(DESIGNATION, {"splined_length": 50.0, "shank_length": 0.0})
    assert p == ShaftParams.model_validate({**FLAT, "splined_length": 50, "shank_length": 0})


def test_resolve_shaft_lets_the_codec_and_the_model_speak() -> None:
    with pytest.raises(DesignationError):
        resolve_shaft("W 25x1.25x18x8F", {})
    with pytest.raises(ValueError, match="profile shift"):
        resolve_shaft("W 6x0.5x6x8f", {})


def test_a_designation_is_the_same_shaft_as_its_four_fields() -> None:
    by_designation = client.get(INFO, params={"designation": DESIGNATION})
    by_fields = client.get(INFO, params=FLAT)
    assert by_designation.status_code == by_fields.status_code == 200
    assert by_designation.json() == by_fields.json()
    assert by_designation.json()["designation"] == DESIGNATION


def test_a_designation_builds_the_shaft_its_fields_build(stub: _Stub) -> None:
    """The backend is handed an equal plain ShaftParams, so the two links share a cache key."""
    client.get("/api/shaft/model.stl", params={"designation": DESIGNATION, "quality": "preview"})
    client.get("/api/shaft/model.stl", params={**FLAT, "quality": "preview"})
    assert stub.calls == 1
    assert stub.seen == [ShaftParams.model_validate(FLAT)]
    assert type(stub.seen[0]) is ShaftParams


def test_a_designation_combines_freely_with_the_solid_fields(stub: _Stub) -> None:
    solid = {"splined_length": 50, "end_chamfer": 0.5, "shank_d": 20, "shank_length": 10}
    r = client.get("/api/shaft/model.stl", params={"designation": DESIGNATION, **solid})
    assert r.status_code == 200
    assert stub.seen == [ShaftParams.model_validate({**FLAT, **solid})]
    flat = client.get(INFO, params={**FLAT, **solid})
    assert client.get(INFO, params={"designation": DESIGNATION, **solid}).json() == flat.json()


@pytest.mark.parametrize(("written", "spelling"), [
    ("designation=W30X2x14x8f", "no space after W, upper-case X"),
    ("designation=W%2030x2,0x14x8f", "a comma for the decimal mark"),
    ("designation=W+30x2x14x8f", "a raw plus decodes to a space"),
    ("designation=W%2030.0x2.00x14x8f", "trailing zeros"),
])
def test_the_codecs_spellings_are_accepted_and_the_row_is_canonical(
        written: str, spelling: str) -> None:
    r = client.get(f"{INFO}?{written}")
    assert r.status_code == 200, spelling
    assert r.json()["designation"] == DESIGNATION


def test_a_repeated_designation_key_is_read_as_its_last_value() -> None:
    """The accepted behaviour, pinned (33 IN-06): FastAPI reads the last value of a repeated
    scalar key, so `designation=nonsense&designation=<good>` builds the good one. An upgrade
    that read the first value, or refused the repeat, would change which shaft a published
    link builds; this fails then instead of nobody noticing."""
    r = client.get(INFO, params=[("designation", "nonsense"), ("designation", DESIGNATION)])
    assert r.status_code == 200
    assert r.json()["designation"] == DESIGNATION


def test_an_encoded_plus_is_a_refused_plus() -> None:
    r = client.get(f"{INFO}?designation=W%2B30x2x14x8f")
    assert r.status_code == 422
    entry = _detail(r.json())[0]
    assert entry["loc"] == ["query", "designation"]
    assert entry["type"] == "designation"
    assert "+30" in str(entry["msg"])


@pytest.mark.parametrize("path", [INFO, "/api/shaft/model.stl"])
@pytest.mark.parametrize(("extra", "fields"), [
    ("teeth=14", ["designation", "teeth"]),
    ("reference_d=30", ["designation", "reference_d"]),
    ("module=2", ["designation", "module"]),
    ("fit=8f", ["designation", "fit"]),
    ("teeth=abc", ["designation", "teeth"]),
    ("reference_d=&fit=", ["designation", "reference_d", "fit"]),
    ("fit=8f&teeth=14&module=2&reference_d=30", ["designation", "reference_d", "module", "teeth",
                                                  "fit"]),
])
def test_a_spline_field_beside_a_designation_is_a_conflict_on_key_presence(
        stub: _Stub, path: str, extra: str, fields: list[str]) -> None:
    r = client.get(f"{path}?designation=W%2030x2x14x8f&{extra}")
    assert r.status_code == 422
    assert _detail(r.json()) == [
        {"loc": ["query", "designation"], "type": "conflict",
         "msg": clash_message(tuple(fields[1:])), "ctx": {"fields": fields}}]
    assert stub.calls == 0


def test_the_conflict_comes_before_any_value_is_read(stub: _Stub) -> None:
    """The designation is also bad here, and the number is not a number: the conflict wins."""
    r = client.get(f"{INFO}?designation=nonsense&teeth=%2B14")
    assert [e["type"] for e in _detail(r.json())] == ["conflict"]


def test_a_solid_field_beside_a_designation_is_no_conflict() -> None:
    for key in ("splined_length", "end_chamfer", "shank_d", "shank_length"):
        default = ShaftParams.model_fields[key].default
        r = client.get(INFO, params={"designation": DESIGNATION, key: default})
        assert r.status_code == 200, key


def _designation_error(designation: str) -> dict[str, object]:
    r = client.get(INFO, params={"designation": designation})
    assert r.status_code == 422, designation
    detail = _detail(r.json())
    assert [e["loc"] for e in detail] == [["query", "designation"]] * len(detail)
    return detail[0]


def test_an_empty_designation_is_a_422_naming_it() -> None:
    assert _designation_error("")["type"] == "designation"


def test_an_unparseable_designation_carries_the_codecs_sentence() -> None:
    entry = _designation_error("W 25x1.25x18x8F")
    assert entry["type"] == "designation"
    assert "8F" in str(entry["msg"])


def test_a_hub_designation_is_refused_with_the_codecs_sentence() -> None:
    assert "internal spline" in str(_designation_error("N 25x1.25x18x8H")["msg"])


def test_an_overlong_designation_is_refused_by_the_codec_before_any_pattern() -> None:
    entry = _designation_error("W " + "9" * DESIGNATION_MAX_LENGTH + "x1x6x8f")
    assert entry["type"] == "designation"
    assert str(DESIGNATION_MAX_LENGTH) in str(entry["msg"])


def test_a_designation_of_exactly_the_cap_is_read_by_the_codec_not_the_length_rule() -> None:
    text = "W " + "9" * (DESIGNATION_MAX_LENGTH - 2)
    assert len(text) == DESIGNATION_MAX_LENGTH
    assert "characters long" not in str(_designation_error(text)["msg"])


def test_a_non_ascii_digit_is_not_a_digit() -> None:
    entry = _designation_error("W 3\u0663x0.5x6x8f")
    assert entry["type"] == "designation"


def test_an_infeasible_designation_is_a_422_with_the_models_sentence() -> None:
    """33-RESEARCH Pattern 1: the codec parses it, the model refuses it, and that is a 422."""
    entry = _designation_error("W 6x0.5x6x8f")
    assert entry["type"] == "infeasible"
    assert "profile shift" in str(entry["msg"])


def test_a_designation_the_fields_bound_refuses_is_a_422_at_the_designation() -> None:
    entry = _designation_error("W 900x1.25x18x8f")
    assert entry["loc"] == ["query", "designation"]


def test_the_download_is_named_for_the_designations_shaft(stub: _Stub) -> None:
    r = client.get("/api/shaft/model.step", params={"designation": DESIGNATION})
    assert r.status_code == 200
    assert r.headers["content-disposition"] == 'attachment; filename="spur_shaft_w30x2x14.step"'
