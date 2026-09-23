from collections.abc import Iterator
from typing import cast

import pytest
from fastapi.testclient import TestClient

from spur.app import app, build_backend
from spur.model import Format, Quality, export
from spur.params import GearParams

client = TestClient(app)


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

    async def inline_backend(p: GearParams, fmt: str, quality: str) -> bytes:
        # build_backend's BuildBackend type is str/str (app.py has no static import path
        # to model.Format/model.Quality to name them with, D-02); this override does, so
        # the cast just narrows back to what export() actually wants.
        return export(p, cast(Format, fmt), cast(Quality, quality))

    app.dependency_overrides[build_backend] = lambda: inline_backend
    yield
    app.dependency_overrides.pop(build_backend, None)


def test_health() -> None:
    assert client.get("/api/health").json()["status"] == "ok"


def test_index_and_static() -> None:
    assert "spur" in client.get("/").text
    assert client.get("/static/app.js").status_code == 200
    assert client.get("/static/vendor/three.bundle.min.js").status_code == 200


def test_schema_drives_the_form() -> None:
    props = client.get("/api/schema").json()["properties"]
    assert props["teeth"]["group"] == "Teeth"
    assert props["module"]["unit"] == "mm"
    assert props["recess_sides"]["enum"] == ["both", "top", "bottom", "none"]


def test_info_with_mate() -> None:
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
    """Builds serialise on the kernel lock, so a deep queue is latency with no payoff."""
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
