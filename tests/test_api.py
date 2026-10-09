import logging
import re
from collections.abc import Iterator
from concurrent.futures.process import BrokenProcessPool
from typing import cast

import cadquery as cq
import pytest
from fastapi.testclient import TestClient

import spur.model
from spur.app import STATIC, app, build_backend
from spur.build_errors import BuildError, BuildTimeout
from spur.calc import HEX_CELL_CAP, DerivedDimensions
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
        "root_thickness", "root_gap", "root_fillet", "tip_chamfer_effective", "span_teeth",
        "span", "bore_effective", "hex_across_flats", "hex_across_corners",
        "keyway_floor_to_wall", "keyway_width_effective", "recess_id", "recess_od",
        "recess_fillet", "web", "cutout_hub_wall", "cutout_rim_wall",
        "spoke_fillet_effective", "hex_cell_effective", "hex_cell_count", "warnings",
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
    assert component["properties"]["hex_across_flats"]["unit"] == "mm"
    assert component["properties"]["hex_across_corners"]["unit"] == "mm"
    assert component["properties"]["keyway_floor_to_wall"]["unit"] == "mm"
    assert component["properties"]["keyway_width_effective"]["unit"] == "mm"
    assert component["properties"]["tip_chamfer_effective"]["unit"] == "mm"
    assert component["properties"]["cutout_hub_wall"]["unit"] == "mm"
    assert component["properties"]["cutout_rim_wall"]["unit"] == "mm"
    assert component["properties"]["spoke_fillet_effective"]["unit"] == "mm"
    assert component["properties"]["hex_cell_effective"]["unit"] == "mm"
    assert "unit" not in component["properties"]["span_teeth"]
    assert "unit" not in component["properties"]["hex_cell_count"]

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

    for read_form in (".span_teeth", "info.centre_distance", "info.warnings",
                     ".hex_cell_count"):
        assert read_form in source

    model_fields = set(DerivedDimensions.model_fields)
    assert set(dims_keys) <= model_fields
    assert {"span_teeth", "centre_distance", "warnings"} <= model_fields


def test_the_shareable_link_round_trips_every_field_through_generic_code() -> None:
    """D-11's static proof, the browser-test idea's own "cheaper first step": the
    hash -> form -> query path in app.js handles every `GearParams` field generically,
    with no per-field code (D-12; 08 D-09 stands). A renamed or added field cannot
    silently break the shareable-link round trip without this catching it. The browser
    itself is checked by hand at gsd-verify-work, against the checklist in
    12-07-PLAN.md's `<verification>`.
    """
    source = (STATIC / "app.js").read_text()

    # IN-04 (12-REVIEW.md): this proof is pinned to these exact tokens (D-4,
    # 12-07-SUMMARY.md) -- a renamed variable or restructured loop must fail it -- but a
    # whitespace-only reformat of app.js (indent width, a long line re-wrapped) proves
    # nothing about field-genericity and must not fail it. Collapsing all whitespace runs
    # to one space on both sides keeps the token-level proof and drops only the part that
    # was never load-bearing.
    collapsed_source = re.sub(r"\s+", " ", source)

    # The generic loops the round trip rests on: buildForm() reads every schema
    # property and records it under its own name; readHash() writes the hash back into
    # every recorded field; gearQuery() reads every field back into the query; update()
    # builds the shareable hash from that query and writes it with history.
    # replaceState(); the copy-link handler copies the resulting location.href; and
    # hashchange re-reads the hash on navigation (e.g. the copied link opened fresh).
    for snippet in (
        "for (const [name, prop] of Object.entries(schema.properties)) {",
        "fields.set(name, { input, wrap, title });",
        "for (const [name, { input }] of fields) input.value = h.get(name) ?? defaults[name];",
        "q.set(name, input.value)",
        "const infoQ = new URLSearchParams(q);",
        "history.replaceState(null, '', hash ? `#${hash}` : location.pathname + location.search);",
        "navigator.clipboard.writeText(location.href)",
        "window.addEventListener('hashchange', () => { readHash(); update(); });",
    ):
        assert re.sub(r"\s+", " ", snippet) in collapsed_source, snippet

    # Cut the `const DIMS = [` ... `];` block out: two of its keys (root_fillet,
    # recess_fillet) are also GearParams names, and the sibling test above already
    # covers DIMS's own generic-enough shape for the UI's dimension list. What remains
    # must name no GearParams field, outside that block, as a per-field special case.
    dims_block = re.search(r"const DIMS = \[.*?\];", source, re.DOTALL)
    assert dims_block  # a regex that silently stopped matching must fail, not pass
    rest = source[:dims_block.start()] + source[dims_block.end():]

    # The pattern's own known false-positive case: a bare-word search for "teeth"
    # matches inside the '#mate-teeth' DOM id (line 9), which must not be read as the
    # field "teeth". Quote-adjacency (a quote immediately before AND after the name) is
    # what tells them apart -- '#mate-teeth' has no quote immediately before "teeth".
    assert not re.search(r"""['"]teeth['"]""", "'#mate-teeth'")

    for name in GearParams.model_fields:
        # A field name written as a complete quoted string literal ('name' or "name"),
        # not merely as a substring of a longer quoted string (the case above).
        assert not re.search(r"""['"]""" + re.escape(name) + r"""['"]""", rest), name
        # A field name read off an object as `something.<field>` -- per-field property
        # access, the shape a conditional-field or bore-selector patch would add.
        assert not re.search(r"\." + re.escape(name) + r"\b", rest), name


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


def test_a_hex_bore_link_is_served_with_its_two_numbers() -> None:
    """?bore_hex=6 end to end (D-01, D-04, D-05): the schema, /api/info's two new
    numbers with bore_effective null, the plain-default case with both hex fields null,
    the le-200 refusal, and both export formats."""
    props = client.get("/api/schema").json()["properties"]
    assert props["bore_hex"]["group"] == "Bore"
    assert props["bore_hex"]["unit"] == "mm"
    assert props["bore_hex"]["maximum"] == 200
    assert props["bore_hex"]["default"] == 0
    names = list(props)
    assert names.index("bore_hex") == names.index("keyway_depth") + 1

    r = client.get("/api/info", params={"bore_hex": 6})
    assert r.status_code == 200
    body = r.json()
    assert body["hex_across_flats"] == pytest.approx(6.15)
    assert body["hex_across_corners"] == pytest.approx(7.101)
    assert body["bore_effective"] is None

    r = client.get("/api/info")
    assert r.status_code == 200
    body = r.json()
    assert body["hex_across_flats"] is None
    assert body["hex_across_corners"] is None
    assert body["bore_effective"] == pytest.approx(9.15)

    r = client.get("/api/info", params={"bore_hex": 200.05})
    assert r.status_code == 422
    assert r.json()["detail"][0]["loc"] == ["query", "bore_hex"]

    r = client.get("/api/model.stl", params={"bore_hex": 6, "quality": "preview"})
    assert r.status_code == 200
    assert r.headers["content-type"] == "model/stl"
    assert len(r.content) > 84

    r = client.get("/api/model.step", params={"bore_hex": 6})
    assert r.status_code == 200
    assert r.content.startswith(b"ISO-10303-21;")


def test_a_keyed_link_is_served_with_its_two_numbers() -> None:
    """?keyway_width=3&keyway_depth=1.4 end to end (D-01, D-04, D-14, D-15): the schema,
    /api/info's two new numbers with the recess moved out to clear the keyway corner,
    the plain-default case with both keyway fields null, the le-200 refusal, and both
    export formats."""
    props = client.get("/api/schema").json()["properties"]
    for name in ("keyway_width", "keyway_depth"):
        assert props[name]["group"] == "Bore"
        assert props[name]["unit"] == "mm"
        assert props[name]["minimum"] == 0
        assert props[name]["maximum"] == 200
        assert props[name]["default"] == 0
    names = list(props)
    assert names.index("keyway_width") == names.index("bore_flat") + 1
    assert names.index("keyway_depth") == names.index("keyway_width") + 1

    r = client.get("/api/info", params={"keyway_width": 3, "keyway_depth": 1.4})
    assert r.status_code == 200
    body = r.json()
    assert body["keyway_floor_to_wall"] == pytest.approx(10.55)
    assert body["keyway_width_effective"] == pytest.approx(3.15)
    assert body["bore_effective"] == pytest.approx(9.15)  # D-04: still a D-flat bore
    assert body["recess_id"] == pytest.approx(13.158)
    assert body["recess_od"] == pytest.approx(25.158)
    assert body["warnings"] == []

    r = client.get("/api/info")
    assert r.status_code == 200
    body = r.json()
    assert body["keyway_floor_to_wall"] is None
    assert body["keyway_width_effective"] is None

    r = client.get("/api/info", params={"keyway_width": 200.05})
    assert r.status_code == 422
    assert r.json()["detail"][0]["loc"] == ["query", "keyway_width"]

    r = client.get("/api/model.stl", params={"keyway_width": 3, "keyway_depth": 1.4,
                                             "quality": "preview"})
    assert r.status_code == 200
    assert r.headers["content-type"] == "model/stl"
    assert len(r.content) > 84

    r = client.get("/api/model.step", params={"keyway_width": 3, "keyway_depth": 1.4})
    assert r.status_code == 200
    assert r.content.startswith(b"ISO-10303-21;")


def test_a_tip_chamfer_link_is_served_with_the_chamfer_it_cut() -> None:
    """?tip_chamfer=0.4 end to end (D-01, D-02, D-04, D-08, D-09, D-10): the schema,
    /api/info's applied value and cap warning, the plain-default null case, the field's
    le-3 refusal, and both export formats."""
    props = client.get("/api/schema").json()["properties"]
    assert props["tip_chamfer"]["group"] == "Teeth"
    assert props["tip_chamfer"]["unit"] == "mm"
    assert props["tip_chamfer"]["minimum"] == 0
    assert props["tip_chamfer"]["maximum"] == 3
    assert props["tip_chamfer"]["default"] == 0
    assert props["tip_chamfer"]["step"] == 0.05
    names = list(props)
    assert names.index("tip_chamfer") == names.index("root_fillet") + 1
    # D-02 put root_shape directly after tip_chamfer, so it now precedes face_width.
    assert names.index("root_shape") == names.index("tip_chamfer") + 1
    assert names.index("face_width") == names.index("root_shape") + 1

    r = client.get("/api/info", params={"tip_chamfer": 0.4})
    assert r.status_code == 200
    body = r.json()
    assert body["tip_chamfer_effective"] == pytest.approx(0.4)
    assert body["tip_d"] == pytest.approx(36.75)
    assert body["warnings"] == []

    r = client.get("/api/info", params={"tip_chamfer": 3})
    assert r.status_code == 200
    body = r.json()
    assert body["tip_chamfer_effective"] == pytest.approx(1.75)
    assert body["warnings"] == [
        "Tip chamfer reduced to 1.75 mm to keep it above the pitch circle."]

    r = client.get("/api/info")
    assert r.status_code == 200
    assert r.json()["tip_chamfer_effective"] is None

    r = client.get("/api/info", params={"tip_chamfer": 3.05})
    assert r.status_code == 422
    assert r.json()["detail"][0]["loc"] == ["query", "tip_chamfer"]

    r = client.get("/api/model.stl", params={"tip_chamfer": 0.4, "quality": "preview"})
    assert r.status_code == 200
    assert r.headers["content-type"] == "model/stl"
    assert len(r.content) > 84

    r = client.get("/api/model.step", params={"tip_chamfer": 0.4})
    assert r.status_code == 200
    assert r.content.startswith(b"ISO-10303-21;")


def test_a_hole_link_is_served_with_its_walls() -> None:
    """?hole_count=6&hole_d=4&hole_circle_d=20 end to end (D-03, D-17, D-19, D-20): the
    schema, /api/info's two new numbers, the plain-default null case, and both export
    formats."""
    props = client.get("/api/schema").json()["properties"]
    assert props["hole_count"]["group"] == "Holes"
    assert props["hole_count"]["type"] == "integer"
    assert props["hole_count"]["minimum"] == 0
    assert props["hole_count"]["maximum"] == 60
    assert props["hole_count"]["default"] == 0
    assert props["hole_count"]["step"] == 1
    assert props["hole_d"]["unit"] == "mm"
    assert props["hole_d"]["maximum"] == 100
    assert props["hole_d"]["step"] == 0.05
    assert props["hole_d"]["default"] == 0
    assert props["hole_circle_d"]["maximum"] == 400
    names = list(props)
    assert names.index("hole_count") == names.index("spoke_fillet") + 1
    assert names.index("hole_d") == names.index("hole_count") + 1
    assert names.index("hole_circle_d") == names.index("hole_d") + 1

    r = client.get("/api/info", params={"hole_count": 6, "hole_d": 4, "hole_circle_d": 20})
    assert r.status_code == 200
    body = r.json()
    assert body["cutout_hub_wall"] == pytest.approx(3.025)
    assert body["cutout_rim_wall"] == pytest.approx(2.438)
    assert body["warnings"] == []

    r = client.get("/api/info")
    assert r.status_code == 200
    body = r.json()
    assert body["cutout_hub_wall"] is None
    assert body["cutout_rim_wall"] is None

    r = client.get("/api/model.stl", params={"hole_count": 6, "hole_d": 4,
                                             "hole_circle_d": 20, "quality": "preview"})
    assert r.status_code == 200
    assert r.headers["content-type"] == "model/stl"
    assert len(r.content) > 84

    r = client.get("/api/model.step",
                   params={"hole_count": 6, "hole_d": 4, "hole_circle_d": 20})
    assert r.status_code == 200
    assert r.content.startswith(b"ISO-10303-21;")


def test_a_hole_conflict_is_422_naming_its_fields() -> None:
    """D-17, REQ-cutout-conflicts-refused-early: a hole set that breaches the hub wall
    is refused before any build, on both /api/info and /api/model.stl."""
    r = client.get("/api/info", params={"hole_count": 6, "hole_d": 4, "hole_circle_d": 14.7})
    assert r.status_code == 422
    detail = r.json()["detail"][0]
    assert detail["ctx"]["fields"] == ["hole_circle_d", "hole_d"]
    assert "Lightening holes come too close to the bore" in detail["msg"]

    r = client.get("/api/model.stl", params={"hole_count": 6, "hole_d": 4,
                                             "hole_circle_d": 14.7, "quality": "preview"})
    assert r.status_code == 422
    assert r.json()["detail"][0]["ctx"]["fields"] == ["hole_circle_d", "hole_d"]


def test_a_spoke_link_is_served_with_the_fillet_it_cut() -> None:
    """?spoke_count=4&spoke_width=2&hub_d=12&rim_wall=1&spoke_fillet=1 end to end
    (D-01, D-04, D-18, D-19, D-20): the schema's Spokes group, /api/info's cap and
    walls, the plain-default null case, and both export formats."""
    props = client.get("/api/schema").json()["properties"]
    assert props["spoke_count"]["group"] == "Spokes"
    assert props["spoke_count"]["type"] == "integer"
    assert props["spoke_count"]["minimum"] == 0
    assert props["spoke_count"]["maximum"] == 32
    assert props["spoke_count"]["default"] == 0
    assert props["spoke_count"]["step"] == 1
    assert props["spoke_width"]["unit"] == "mm"
    assert props["spoke_width"]["maximum"] == 100
    assert props["spoke_width"]["step"] == 0.05
    assert props["spoke_width"]["default"] == 0
    assert props["hub_d"]["maximum"] == 400
    assert props["rim_wall"]["maximum"] == 100
    assert props["spoke_fillet"]["maximum"] == 5
    names = list(props)
    assert names.index("spoke_count") == names.index("recess_fillet") + 1
    assert names.index("spoke_width") == names.index("spoke_count") + 1
    assert names.index("hub_d") == names.index("spoke_width") + 1
    assert names.index("rim_wall") == names.index("hub_d") + 1
    assert names.index("spoke_fillet") == names.index("rim_wall") + 1

    r = client.get("/api/info", params={"spoke_count": 4, "spoke_width": 2, "hub_d": 12,
                                        "rim_wall": 1, "spoke_fillet": 1})
    assert r.status_code == 200
    body = r.json()
    assert body["spoke_fillet_effective"] == pytest.approx(1.0)
    assert body["cutout_hub_wall"] == pytest.approx(1.025)
    assert body["cutout_rim_wall"] == pytest.approx(1.0)
    assert body["warnings"] == []

    r = client.get("/api/info", params={"spoke_count": 4, "spoke_width": 2, "hub_d": 12,
                                        "rim_wall": 1, "spoke_fillet": 5})
    assert r.status_code == 200
    body = r.json()
    assert body["spoke_fillet_effective"] == pytest.approx(3.337)
    assert body["warnings"] == [
        "Spoke fillet reduced to 3.337 mm to fit the opening between the arms at "
        "the hub."]

    r = client.get("/api/info")
    assert r.status_code == 200
    body = r.json()
    assert body["spoke_fillet_effective"] is None
    assert body["cutout_hub_wall"] is None
    assert body["cutout_rim_wall"] is None

    r = client.get("/api/model.stl", params={"spoke_count": 4, "spoke_width": 2,
                                             "hub_d": 12, "rim_wall": 1,
                                             "spoke_fillet": 1, "quality": "preview"})
    assert r.status_code == 200
    assert r.headers["content-type"] == "model/stl"
    assert len(r.content) > 84

    r = client.get("/api/model.step", params={"spoke_count": 4, "spoke_width": 2,
                                               "hub_d": 12, "rim_wall": 1,
                                               "spoke_fillet": 1})
    assert r.status_code == 200
    assert r.content.startswith(b"ISO-10303-21;")


def test_a_honeycomb_link_is_served_with_its_cells() -> None:
    """?hex_cell=3&hex_wall=1 end to end (D-07...D-13, D-19, D-20): the schema's
    Honeycomb group, /api/info's cell count and exact walls, the plain-default null
    case, a large-gear raise-to-fit with its warning, and both export formats."""
    props = client.get("/api/schema").json()["properties"]
    assert props["hex_cell"]["group"] == "Honeycomb"
    assert props["hex_cell"]["unit"] == "mm"
    assert props["hex_cell"]["maximum"] == 100
    assert props["hex_cell"]["step"] == 0.05
    assert props["hex_cell"]["default"] == 0
    assert props["hex_wall"]["unit"] == "mm"
    assert props["hex_wall"]["maximum"] == 100
    names = list(props)
    assert names.index("hex_cell") == names.index("hole_circle_d") + 1
    assert names.index("hex_wall") == names.index("hex_cell") + 1

    r = client.get("/api/info", params={"hex_cell": 3, "hex_wall": 1})
    assert r.status_code == 200
    body = r.json()
    assert body["hex_cell_effective"] == pytest.approx(3.0)
    assert body["hex_cell_count"] == 18
    assert body["cutout_hub_wall"] == pytest.approx(1.525, abs=1e-3)
    assert body["cutout_rim_wall"] == pytest.approx(2.149, abs=1e-3)
    assert body["warnings"] == []

    r = client.get("/api/info")
    assert r.status_code == 200
    body = r.json()
    assert body["hex_cell_effective"] is None
    assert body["hex_cell_count"] is None

    r = client.get("/api/info", params={"teeth": 200, "hex_cell": 3, "hex_wall": 1})
    assert r.status_code == 200
    body = r.json()
    assert body["hex_cell_effective"] > 3
    assert (body["hex_cell_effective"] - 3) / 0.05 == pytest.approx(
        round((body["hex_cell_effective"] - 3) / 0.05))
    assert 0 < body["hex_cell_count"] <= HEX_CELL_CAP
    assert any(w.startswith("Honeycomb cells enlarged from 3 mm to ")
              for w in body["warnings"])

    r = client.get("/api/model.stl", params={"hex_cell": 3, "hex_wall": 1,
                                             "quality": "preview"})
    assert r.status_code == 200
    assert r.headers["content-type"] == "model/stl"
    assert len(r.content) > 84

    r = client.get("/api/model.step", params={"hex_cell": 3, "hex_wall": 1})
    assert r.status_code == 200
    assert r.content.startswith(b"ISO-10303-21;")


def test_two_cutout_patterns_are_422_naming_both() -> None:
    """REQ-one-cutout-pattern over HTTP: spokes and holes both set is refused before
    any build, on both /api/info and /api/model.step."""
    params = {"spoke_count": 4, "spoke_width": 2, "hub_d": 12, "rim_wall": 1,
             "hole_count": 6, "hole_d": 4, "hole_circle_d": 20}
    r = client.get("/api/info", params=params)
    assert r.status_code == 422
    detail = r.json()["detail"][0]
    assert detail["ctx"]["fields"] == ["hole_count", "spoke_count"]
    assert "Only one body cutout pattern per part" in detail["msg"]

    r = client.get("/api/model.step", params=params)
    assert r.status_code == 422
    assert r.json()["detail"][0]["ctx"]["fields"] == ["hole_count", "spoke_count"]


def test_a_honeycomb_that_cannot_exist_is_422_naming_its_fields() -> None:
    """D-10, D-14, REQ-cutout-conflicts-refused-early: a honeycomb wall under MIN_WALL,
    and a cell too large for any whole cell to fit, are both 422s naming their fields
    before any build, on /api/info and /api/model.stl."""
    r = client.get("/api/info", params={"hex_cell": 3, "hex_wall": 0.35})
    assert r.status_code == 422
    detail = r.json()["detail"][0]
    assert detail["ctx"]["fields"] == ["hex_wall"]
    assert "thinner than 0.4 mm" in detail["msg"]

    r = client.get("/api/model.stl", params={"hex_cell": 5.1, "hex_wall": 1,
                                             "quality": "preview"})
    assert r.status_code == 422
    detail = r.json()["detail"][0]
    assert detail["ctx"]["fields"] == ["hex_cell", "hex_wall"]
    assert "No whole honeycomb cell fits" in detail["msg"]


def test_a_hex_bore_the_root_cannot_hold_is_422_naming_bore_hex() -> None:
    """D-03a over HTTP: a corner beyond the root is a 422 naming only bore_hex."""
    r = client.get("/api/info", params={"bore_hex": 24.2, "bore_chamfer": 0})
    assert r.status_code == 422
    detail = r.json()["detail"][0]
    assert detail["ctx"]["fields"] == ["bore_hex"]
    assert "Hex bore is too large for the root diameter" in detail["msg"]

    r = client.get("/api/info", params={"bore_hex": 23.4})
    assert r.status_code == 422
    detail = r.json()["detail"][0]
    assert detail["ctx"]["fields"] == ["bore_chamfer", "bore_hex"]


def test_a_hex_bore_chamfer_reaching_the_root_is_422_naming_both_fields() -> None:
    """D-03b over HTTP: a chamfer that carries the corners to the root is a 422 naming
    bore_chamfer and bore_hex, at the measured boundary."""
    r = client.get("/api/info", params={"bore_hex": 23.35})
    assert r.status_code == 200

    r = client.get("/api/info", params={"bore_hex": 23.4})
    assert r.status_code == 422
    detail = r.json()["detail"][0]
    assert detail["ctx"]["fields"] == ["bore_chamfer", "bore_hex"]
    assert "Bore chamfer is too large for this hex bore" in detail["msg"]


def test_a_hex_link_with_a_d_flat_builds_and_says_both_round_fields_are_ignored() -> None:
    """D-01/D-02 over HTTP: a hex link that also carries a non-default bore_flat builds
    (never a 422) and warns about both ignored round fields."""
    r = client.get("/api/info", params={"bore_hex": 6, "bore_flat": 3})
    assert r.status_code == 200
    warnings = r.json()["warnings"]
    assert ("Hex bore replaces the round profile: bore_d (9 mm) and bore_flat (3 mm) "
            "are ignored.") in warnings

    r = client.get("/api/model.stl", params={"bore_hex": 6, "bore_flat": 3,
                                             "quality": "preview"})
    assert r.status_code == 200


@pytest.mark.parametrize(("params", "fields"), [
    pytest.param({"bore_hex": 6, "keyway_width": 3, "keyway_depth": 1.4},
                 ["bore_hex", "keyway_depth", "keyway_width"], id="hex"),
    pytest.param({"bore_d": 0, "keyway_width": 3, "keyway_depth": 1.4},
                 ["bore_d", "keyway_depth", "keyway_width"], id="no-bore"),
    pytest.param({"keyway_width": 3},
                 ["keyway_depth", "keyway_width"], id="half-set"),
    pytest.param({"bore_flat": 0, "keyway_width": 9, "keyway_depth": 1.4},
                 ["bore_d", "keyway_width"], id="too-wide"),
    pytest.param({"keyway_width": 6.5, "keyway_depth": 1.4},
                 ["bore_flat", "keyway_width"], id="into-flat"),
    pytest.param({"keyway_width": 3, "keyway_depth": 9.4},
                 ["keyway_depth", "keyway_width"], id="too-deep"),
])
def test_a_keyway_conflict_is_422_naming_its_fields(
        params: dict[str, object], fields: list[str]) -> None:
    """The six keyway refusals (D-13, D-03, D-11, D-02, D-10) over HTTP, on both
    /api/info and /api/model.stl (the check runs before any CAD work either way)."""
    r = client.get("/api/info", params=params)
    assert r.status_code == 422
    assert r.json()["detail"][0]["ctx"]["fields"] == fields

    r = client.get("/api/model.stl", params={**params, "quality": "preview"})
    assert r.status_code == 422
    assert r.json()["detail"][0]["ctx"]["fields"] == fields


@pytest.mark.parametrize("params", [
    pytest.param({"keyway_width": 6.45, "keyway_depth": 1.4}, id="d-02-flat"),
    pytest.param({"keyway_width": 3, "keyway_depth": 9.35}, id="d-10-root"),
    pytest.param({"bore_flat": 0, "keyway_width": 8.95, "keyway_depth": 1.4},
                 id="d-11-bore"),
])
def test_the_largest_keyway_each_rule_allows_is_served(params: dict[str, object]) -> None:
    """One step inside each keyway rule is a 200, not a 422."""
    r = client.get("/api/info", params=params)
    assert r.status_code == 200


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


def _field(rec: logging.LogRecord, name: str) -> object:
    """Read a field one of this module's per-event helpers attached via `extra=`, on a
    record already selected by `_event_records` -- so the field is known present.
    LogRecord's stub declares no such attribute, so `getattr` on it yields an untyped
    value; `object` states that honestly. Each caller compares by equality/identity or
    narrows before doing arithmetic on it. ruff's B009 ("no getattr with a constant")
    does not fire here because `name` is a parameter, not a literal, at this call site.
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
    duration_ms = _field(served[0], "duration_ms")
    assert isinstance(duration_ms, int)
    assert duration_ms > 0


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


def test_a_tip_chamfer_that_selects_no_tip_arcs_is_a_422_naming_the_defect(
        monkeypatch: pytest.MonkeyPatch) -> None:
    """D-14's guard over HTTP: an empty tip-arc selection is a BuildError, which the
    API maps to a 422 naming the defect, not the catch-all's "try smaller"."""
    spur.model._build_cached.cache_clear()
    real = spur.model._tip_edges

    def wrapper(solid: cq.Shape, ra: float, face_width: float) -> list[cq.Edge]:
        return real(solid, ra + 1.0, face_width)  # a radius where no arc exists

    monkeypatch.setattr("spur.model._tip_edges", wrapper)
    # teeth=67: a count no other test in this suite downloads, so the byte cache cannot
    # short-circuit this request before the patched selector runs (the teeth=71 comment's
    # reason, above).
    r = client.get("/api/model.stl",
                   params={"teeth": 67, "tip_chamfer": 0.4, "quality": "preview"})
    assert r.status_code == 422
    detail = r.json()["detail"][0]
    assert detail["type"] == "build_error"
    assert "Tip chamfer selected no tip-arc edges" in detail["msg"]
    assert "try smaller" not in detail["msg"]
