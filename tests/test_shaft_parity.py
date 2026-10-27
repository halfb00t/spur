"""D-21 part two, REQ-shaft-parity: the API and the CLI print one shaft document.

Over the fixed set in tests/shaft_parity.py, `/api/shaft/info` and `spur shaft info` are
raw-equal as parsed JSON, in `ShaftDimensions` key order, nulls included; and the API names
its download `ShaftParams.slug()` plus the suffix. Light on purpose: a stub backend answers
the download, so no solid is built and the file runs in `make verify.fast`. Each test
replaces the export cache and the backend through `monkeypatch`, so the file is safe under
`-n 8`.

The comparison was seen red once on a one-ulp change to `tip_d` in `cmd_shaft_info`
(bench/RESULTS.md `### Seen red once (Phase 33)`, 33-05); `test_the_comparison_sees_a_...`
keeps `differences()` honest on its own.
"""

from __future__ import annotations

import json
import math

import pytest
from fastapi.testclient import TestClient
from shaft_parity import SHAFTS, cli_argv, differences, displayed, web_rows

import spur.app as app_module
from spur import cli
from spur.app import app, build_backend
from spur.shaft_calc import ShaftDimensions, derive_shaft
from spur.shaft_params import ShaftParams

client = TestClient(app)

# Typed from the planning measurements, never computed from the code under test (L08): the
# keys each shaft prints as null.
NULLS = {
    "default": {"form_d"},
    "w30x2x14": {"form_d"},
    "odd-z": {"form_d", "measure_over_pins"},
    "no-shank-no-chamfer": {"form_d", "end_chamfer_effective"},
}


class _Stub:
    """A backend that builds nothing."""

    async def __call__(self, *_: object) -> bytes:
        return b"stub"


@pytest.fixture
def stub(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(app_module, "_EXPORTS", app_module._BlobCache(1 << 20))
    monkeypatch.setitem(app.dependency_overrides, build_backend, _Stub)


@pytest.mark.parametrize("name", SHAFTS)
def test_the_api_and_the_cli_print_one_shaft_document(
        name: str, capsys: pytest.CaptureFixture[str]) -> None:
    values = SHAFTS[name]
    cli.main(cli_argv(values))
    from_cli = json.loads(capsys.readouterr().out)
    from_api = client.get("/api/shaft/info", params=values).json()

    assert differences(from_cli, from_api) == []
    assert list(from_cli) == list(ShaftDimensions.model_fields)       # ordering
    assert list(from_api) == list(ShaftDimensions.model_fields)
    assert {k for k, v in from_cli.items() if v is None} == NULLS[name]   # empty


@pytest.mark.parametrize("name", SHAFTS)
@pytest.mark.parametrize("fmt", ["stl", "step"])
def test_the_download_is_named_by_the_slug(name: str, fmt: str, stub: None) -> None:
    values = SHAFTS[name]
    r = client.get(f"/api/shaft/model.{fmt}", params=values)
    assert r.status_code == 200
    want = ShaftParams.model_validate(values).slug() + "." + fmt
    got = r.headers["content-disposition"]
    assert got == f'attachment; filename="{want}"'
    assert got.isascii()                                              # encoding
    assert want.isascii()


def test_the_default_and_the_shaft_without_shank_or_chamfer_share_one_name(stub: None) -> None:
    names = {name: client.get("/api/shaft/model.step", params=SHAFTS[name]).headers[
        "content-disposition"] for name in ("default", "no-shank-no-chamfer")}
    assert names["default"] == names["no-shank-no-chamfer"]           # adjacency
    assert "spur_shaft_w25x1.25x18.step" in names["default"]


def test_the_set_spans_the_edges_of_the_ranges_it_is_chosen_for() -> None:
    shifts = {n: round(derive_shaft(ShaftParams.model_validate(v)).profile_shift, 9)
              for n, v in SHAFTS.items()}
    assert shifts["default"] == 0.45                                  # boundary: upper edge
    assert shifts["w30x2x14"] == -0.05                                # boundary: lower edge
    assert SHAFTS["no-shank-no-chamfer"]["shank_length"] == 0         # boundary: the minimum


def test_the_comparison_sees_a_one_ulp_change_and_a_changed_name() -> None:
    doc = json.loads(derive_shaft(ShaftParams()).model_dump_json())
    assert differences(doc, doc) == []

    nudged = {**doc, "tip_d": math.nextafter(doc["tip_d"], math.inf)}
    assert [line.split(":")[0] for line in differences(doc, nudged)] == ["tip_d"]

    renamed = {("tip_diameter" if k == "tip_d" else k): v for k, v in doc.items()}
    assert {line.split(":")[0] for line in differences(doc, renamed)} == {
        "tip_d", "tip_diameter"}

    swapped = {k: doc[k] for k in reversed(doc)}
    assert differences(doc, swapped)                                  # order alone is a difference


def test_displayed_is_the_browsers_fmt() -> None:
    assert displayed(0.0625) == "0.063"
    assert displayed(-0.0001) == "-0"
    assert displayed(-0.0) == "0"
    assert displayed(25.0) == "25"
    assert displayed(27.9994) == "27.999"
    assert displayed(100.0) == "100"


def test_web_rows_print_what_the_page_prints_and_skip_what_is_null() -> None:
    dims = client.get("/api/shaft/schema").json()["dims"]
    rows = dict(web_rows(json.loads(derive_shaft(ShaftParams()).model_dump_json()), dims))
    assert rows["Reference Ø d_B"] == "25 mm"
    assert rows["Profile shift x"] == "0.45"                          # no unit, no space
    assert rows["Designation"] == "W 25x1.25x18x8f"
    assert "Form Ø d_Ff" not in rows                                  # null, so not a row

    odd = dict(web_rows(json.loads(
        derive_shaft(ShaftParams(reference_d=26, module=1.25, teeth=19)).model_dump_json()), dims))
    assert "Measurement over pins M_Re" not in odd
