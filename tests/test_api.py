import pytest
from fastapi.testclient import TestClient

from spur.app import app

client = TestClient(app)


def test_health():
    assert client.get("/api/health").json()["status"] == "ok"


def test_index_and_static():
    assert "spur" in client.get("/").text
    assert client.get("/static/app.js").status_code == 200
    assert client.get("/static/vendor/three.bundle.min.js").status_code == 200


def test_schema_drives_the_form():
    props = client.get("/api/schema").json()["properties"]
    assert props["teeth"]["group"] == "Teeth"
    assert props["module"]["unit"] == "mm"
    assert props["recess_sides"]["enum"] == ["both", "top", "bottom", "none"]


def test_info_with_mate():
    r = client.get("/api/info", params={"teeth": 21, "mate_teeth": 40})
    assert r.status_code == 200
    assert r.json()["centre_distance"] == pytest.approx(1.75 * 61 / 2)


def test_infeasible_is_422_with_fields():
    r = client.get("/api/info", params={"bore_flat": 3})
    assert r.status_code == 422
    detail = r.json()["detail"][0]
    assert "D-flat" in detail["msg"]
    assert detail["ctx"]["fields"] == ["bore_flat"]


def test_bad_type_is_422_on_the_field():
    r = client.get("/api/info", params={"teeth": "many"})
    assert r.status_code == 422
    assert r.json()["detail"][0]["loc"] == ["query", "teeth"]


@pytest.mark.parametrize(("fmt", "ctype", "magic"), [
    ("stl", "model/stl", None),
    ("step", "model/step", b"ISO-10303-21;"),
])
def test_model_download(fmt, ctype, magic):
    r = client.get(f"/api/model.{fmt}", params={"quality": "preview", "teeth": 21})
    assert r.status_code == 200
    assert r.headers["content-type"] == ctype
    assert r.headers["content-disposition"] == f'attachment; filename="spur_z21_m1.75_pa25.{fmt}"'
    if magic:
        assert r.content.startswith(magic)


def test_unknown_format_is_rejected():
    assert client.get("/api/model.obj").status_code == 422
