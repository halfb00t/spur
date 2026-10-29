"""WR-02: a link number the page's number box would blank is refused as written (D-01..D-05).

The page keeps a link token its control cannot hold aside and sends it as given (L44); a
number box blanks `5.`, `+22`, ` 22` and `1_0`, so before L49 the API built a part from a
token the form showed as blank (L05, L08). `app._numbers_as_written` refuses those tokens
before pydantic reads the query, on both gear query routes, and the rule is whatever Chromium
does (D-02): tests/number_box_tokens.py is the table 33-01 measured.

Light on purpose: a stub `build_backend` returns fixed bytes and the export cache is replaced
per test, so no test here builds a solid and the file runs in `make verify.fast`. What each
test turns red if the rule is dropped:

- the exact-sentence tests (D-04): the wording, the escaping, the 422 shape.
- the table walkers (D-02): a blanked token with a 200, or a held token refused by the rule.
- the boundary, empty and repeated-key tests (D-03, D-05): where the rule stops and which
  value of a repeated key it reads.
- the seam test: the dependency adds no query parameter to either route.
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from number_box_tokens import TOKENS
from pydantic import ValidationError

import spur.app as app_module
from spur.app import InfoQuery, ShaftInfoQuery, app, build_backend
from spur.params import GearParams

client = TestClient(app)

# One int field, two float fields and the mate box on /api/info; the same three gear
# fields on the model route (it has no mate box).
INFO_FIELDS = ("teeth", "face_width", "module", "mate_teeth")
MODEL_FIELDS = ("teeth", "face_width", "module")
AS_WRITTEN = "number_as_written"


class _Stub:
    """A backend that builds nothing and counts its calls."""

    def __init__(self) -> None:
        self.calls = 0

    async def __call__(self, *_: object) -> bytes:
        self.calls += 1
        return b"stub"


@pytest.fixture
def stub(monkeypatch: pytest.MonkeyPatch) -> Iterator[_Stub]:
    """A stub backend and a fresh export cache, the prior override put back afterwards.

    Restored and not popped: tests/test_api.py installs its own module-wide override on the
    same `app`, and an xdist worker may run both files.
    """
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


def _types(response_json: object) -> list[str]:
    assert isinstance(response_json, dict), f"a 422 body that is not an object: {response_json!r}"
    detail = response_json["detail"]
    assert isinstance(detail, list), f"a 422 with no detail list: {response_json!r}"
    return [str(item["type"]) for item in detail]


def _refused_detail(path: str, params: list[tuple[str, str]]) -> list[dict[str, object]]:
    response = client.get(path, params=params)
    assert response.status_code == 422, f"{path} {params} answered {response.status_code}"
    detail = response.json()["detail"]
    assert isinstance(detail, list)
    return detail


def test_a_trailing_dot_is_refused_as_written_with_the_canonical_form(stub: _Stub) -> None:
    """D-01, D-04: `face_width=5.` is the token the browser pin used to build; /api/info and
    the model route both answer the same one-entry 422 and the model route builds nothing."""
    want = [{
        "loc": ["query", "face_width"],
        "type": AS_WRITTEN,
        "msg": '"5." is not a number as written; write it as 5 or 5.0',
    }]
    assert _refused_detail("/api/info", [("face_width", "5.")]) == want
    assert _refused_detail("/api/model.stl", [("face_width", "5.")]) == want
    assert stub.calls == 0, "the model route built a part for a token the box blanks"


@pytest.mark.parametrize(("field", "token", "msg"), [
    pytest.param("teeth", "+22", '"+22" is not a number as written; write it as 22',
                 id="plus-int"),
    pytest.param("teeth", " 22", '" 22" is not a number as written; write it as 22',
                 id="space-int"),
    pytest.param("teeth", "22.", '"22." is not a number as written; write it as 22',
                 id="dot-int-has-no-point-zero"),
    pytest.param("face_width", "1_0",
                 '"1_0" is not a number as written; write it as a plain number, e.g. 22 or 2.5',
                 id="underscore-has-no-canonical-form"),
    pytest.param("module", "+.5",
                 '"+.5" is not a number as written; write it as a plain number, e.g. 22 or 2.5',
                 id="plus-point-five"),
    pytest.param("mate_teeth", "+30", '"+30" is not a number as written; write it as 30',
                 id="mate-box"),
])
def test_the_message_quotes_the_token_and_suggests_the_form_when_there_is_one(
        field: str, token: str, msg: str) -> None:
    """D-04: the token is quoted as JSON; the suggestion is the token with its surrounding
    whitespace, one leading `+` and one trailing `.` removed, when that is a plain number."""
    assert _refused_detail("/api/info", [(field, token)]) == [
        {"loc": ["query", field], "type": AS_WRITTEN, "msg": msg}]


def test_a_control_character_in_a_token_is_escaped_in_the_message() -> None:
    """T-33-06: the message reflects the token, so it is quoted with json.dumps and no raw
    control or non-ASCII character reaches the page."""
    detail = _refused_detail("/api/info", [("teeth", "\x0b22" + chr(0x2028))])
    msg = str(detail[0]["msg"])
    assert msg.isascii(), f"a non-ASCII character in {msg!r}"
    assert msg.isprintable(), f"a control character in {msg!r}"
    assert msg == '"\\u000b22\\u2028" is not a number as written; write it as 22'


@pytest.mark.parametrize("route", ["/api/info", "/api/model.stl"])
def test_every_blanked_token_is_refused_and_no_held_token_is_by_the_rule(
        route: str, stub: _Stub) -> None:
    """D-02: walk the committed Chromium table over every gear number field of the route.

    A token the box blanks never gets a 200, whether the rule or pydantic refuses it; the
    rule itself fires on none of the held tokens. An empty token is blank in the box but is
    not the rule's: pydantic answers it and the page never sends it (L44 D-06).
    """
    fields = INFO_FIELDS if route == "/api/info" else MODEL_FIELDS
    sent_ok: list[str] = []
    wrongly_refused: list[str] = []
    for token in TOKENS:
        rule = app_module.blank_in_a_number_box(token.text)
        if token.text == "":
            assert not rule, "the rule fired on an empty value"
        elif not token.blank and rule:
            wrongly_refused.append(repr(token.text))
        for field in fields:
            response = client.get(route, params={"quality": "preview", field: token.text})
            if token.blank and response.status_code == 200:
                sent_ok.append(f"{field}={token.text!r}")
            refused_by_rule = response.status_code == 422 and AS_WRITTEN in _types(response.json())
            if refused_by_rule and not token.blank:
                wrongly_refused.append(f"{field}={token.text!r}")
    assert not sent_ok, f"{route}: a blanked token was answered 200: {sent_ok[:5]}"
    assert not wrongly_refused, f"{route}: a held token was refused: {wrongly_refused[:5]}"


def test_a_held_token_keeps_the_answer_it_had(stub: _Stub) -> None:
    """Precision: tokens the box holds that look odd are the rule's non-business. `00022` is
    22, `1e-400` is 0.0 and fails the bound, `-0` is a bound failure; none is
    `number_as_written`."""
    for text in ("1e-400", "00022", "1.e1", "-0", "0.1e1", "5.0", "1e1"):
        assert not app_module.blank_in_a_number_box(text), text
        for field in ("teeth", "face_width"):
            response = client.get("/api/info", params={field: text})
            if response.status_code == 422:
                assert AS_WRITTEN not in _types(response.json()), (field, text)


def test_the_bound_is_the_bounds_and_the_rule_stops_at_the_digit() -> None:
    """D-03 boundary: 200 teeth build, `+200` is refused as written, 201 keeps pydantic's own
    bound sentence, and an empty value keeps pydantic's own 422 (the rule never reads it)."""
    assert client.get("/api/info", params={"teeth": "200"}).status_code == 200
    assert _refused_detail("/api/info", [("teeth", "+200")])[0]["type"] == AS_WRITTEN
    over = _refused_detail("/api/info", [("teeth", "201")])
    assert over[0]["type"] == "less_than_equal"
    empty = _refused_detail("/api/info", [("teeth", "")])
    assert AS_WRITTEN not in [str(item["type"]) for item in empty]


def test_every_value_of_a_repeated_key_is_checked_in_either_order() -> None:
    """D-05: pydantic would read one value of a repeated key; the rule reads all of them, so
    a blanked token cannot hide behind a good one."""
    for pairs in ([("teeth", "22"), ("teeth", "+22")], [("teeth", "+22"), ("teeth", "22")]):
        detail = _refused_detail("/api/info", pairs)
        assert [item["loc"] for item in detail] == [["query", "teeth"]], pairs
        assert detail[0]["msg"] == '"+22" is not a number as written; write it as 22'


def test_two_offending_keys_answer_two_entries_in_query_order() -> None:
    """D-05: one detail entry per offending key, in the order the keys were sent."""
    detail = _refused_detail("/api/info", [("face_width", "5."), ("teeth", "+22")])
    assert [item["loc"] for item in detail] == [["query", "face_width"], ["query", "teeth"]]
    swapped = _refused_detail("/api/info", [("teeth", "+22"), ("face_width", "5.")])
    assert [item["loc"] for item in swapped] == [["query", "teeth"], ["query", "face_width"]]


def test_the_rule_answers_before_pydantic_reads_the_query() -> None:
    """D-01: a query with a blanked token and a token pydantic would refuse answers only the
    as-written entry; the second refusal appears once the first is fixed."""
    detail = _refused_detail("/api/info", [("face_width", "5."), ("teeth", "abc")])
    assert [str(item["type"]) for item in detail] == [AS_WRITTEN]


@pytest.mark.parametrize("pair", [("root_shape", "+5"), ("quality", "+5"), ("recess_sides", "5.")])
def test_a_field_that_is_not_a_number_is_left_to_pydantic(
        pair: tuple[str, str], stub: _Stub) -> None:
    """Only `int`, `float` and `int | None` fields are the rule's: a select's token keeps its
    own `literal_error`, and `quality` is the model route's, not a gear number."""
    for route in ("/api/info", "/api/model.stl"):
        response = client.get(route, params=[pair])
        if response.status_code == 422:
            assert AS_WRITTEN not in _types(response.json()), (route, pair)


def test_the_dependency_adds_no_query_parameter_to_either_route() -> None:
    """D-03: the schema bytes and the routes' query keys do not move; the pre-check reads the
    raw request and is not a parameter."""
    paths = app.openapi()["paths"]

    def query_names(path: str) -> set[str]:
        parameters = paths[path]["get"]["parameters"]
        return {p["name"] for p in parameters if p["in"] == "query"}

    assert query_names("/api/info") == set(GearParams.model_fields) | {"mate_teeth"}
    assert query_names("/api/model.{fmt}") == set(GearParams.model_fields) | {"quality"}


def test_an_interior_minus_builds_an_int_field_only_as_its_default() -> None:
    """IN-01: pydantic reads `0-0` and `00-0` as the int 0, and `0-9` as -9, while Chromium's
    number box blanks all of them, so the blanked-token invariant (no token builds a part the
    blank box does not imply) holds for them only where 0 is the field's default. It does for
    `spoke_count` and `hole_count`, whose range starts at 0 and whose default is 0, and by that
    coincidence and not by the rule. A new int field that reads one of these tokens as a
    value other than its default fails here, and then the rule gets a fifth condition (L49)."""
    for model in (InfoQuery, ShaftInfoQuery):
        for name, is_int in app_module._number_keys(model).items():
            if not is_int:
                continue
            for token in ("0-0", "00-0", "0-9", "00-9"):
                try:
                    value = getattr(model.model_validate({name: token}), name)
                except ValidationError:
                    continue
                assert value == model.model_fields[name].default, (
                    f"{model.__name__}.{name}={token!r} builds {value}, not the default"
                )
