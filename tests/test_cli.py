"""The CLI had no tests, and the README's own example did not run."""

import json
from pathlib import Path

import cadquery as cq
import pytest
from fastapi.testclient import TestClient

import spur.app
import spur.model
from spur import cli
from spur.app import InfoQuery
from spur.calc import DerivedDimensions


def test_info_reports_the_mate_it_was_asked_about(capsys: pytest.CaptureFixture[str]) -> None:
    cli.main(["info", "--teeth", "19", "--mate-teeth", "40"])
    out = json.loads(capsys.readouterr().out)
    assert out["mate_teeth"] == 40
    assert out["centre_distance"] == pytest.approx(51.625)


def test_info_rejects_a_mate_the_api_would_reject(capsys: pytest.CaptureFixture[str]) -> None:
    """A centre distance to a gear that cannot exist is the plausible wrong number L08
    forbids; the CLI must refuse exactly the mate teeth the API's InfoQuery refuses
    (REQ-cli-parity), not a hand-picked range that can drift from it."""
    schema = InfoQuery.model_json_schema()
    bounds = next(b for b in schema["properties"]["mate_teeth"]["anyOf"]
                  if b["type"] == "integer")
    minimum, maximum = bounds["minimum"], bounds["maximum"]

    for value in (-5, 3, 0, minimum - 1, maximum + 1):
        with pytest.raises(SystemExit) as exc:
            cli.main(["info", f"--mate-teeth={value}"])
        assert exc.value.code == 2
        captured = capsys.readouterr()
        assert "centre_distance" not in captured.out
        assert "--mate-teeth" in captured.err

    for value in (minimum, maximum):
        cli.main(["info", f"--mate-teeth={value}"])
        out = json.loads(capsys.readouterr().out)
        assert isinstance(out["centre_distance"], float)


def test_cli_and_api_print_the_same_document(capsys: pytest.CaptureFixture[str]) -> None:
    """D-13: the CLI and the API must never disagree on the document they both print --
    `cmd_info` prints the model's own JSON, so there is only one serialiser to drift."""
    client = TestClient(spur.app.app)

    # No mate (edge: empty) -- mate_teeth and centre_distance are present and null.
    cli.main(["info", "--teeth", "21"])
    cli_out = json.loads(capsys.readouterr().out)
    api_out = client.get("/api/info", params={"teeth": 21}).json()
    assert cli_out == api_out
    assert list(cli_out) == list(DerivedDimensions.model_fields)  # edge: ordering
    assert cli_out["mate_teeth"] is None
    assert cli_out["centre_distance"] is None

    # A mate that meshes fine.
    cli.main(["info", "--teeth", "21", "--mate-teeth", "40"])
    cli_out = json.loads(capsys.readouterr().out)
    api_out = client.get("/api/info", params={"teeth": 21, "mate_teeth": 40}).json()
    assert cli_out == api_out
    assert list(cli_out) == list(DerivedDimensions.model_fields)

    # The impossible pair (edge: adjacency) -- centre_distance null, "cannot mesh" warned.
    impossible = {"teeth": 6, "pressure_angle": 14.5, "profile_shift": -0.6, "bore_d": 0,
                 "bore_flat": 0, "bore_chamfer": 0, "recess_sides": "none", "mate_teeth": 40}
    cli.main(["info",
             *(f"--{k.replace('_', '-')}={v}" for k, v in impossible.items())])
    cli_out = json.loads(capsys.readouterr().out)
    api_out = client.get("/api/info", params=impossible).json()
    assert cli_out == api_out
    assert list(cli_out) == list(DerivedDimensions.model_fields)
    assert cli_out["centre_distance"] is None
    assert any("cannot mesh" in w for w in cli_out["warnings"])


def test_readme_export_examples_run(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    step = tmp_path / "gear.step"
    cli.main(["export", "-o", str(step)])
    assert step.read_bytes().startswith(b"ISO-10303-21;")

    stl = tmp_path / "gear.stl"
    cli.main(["export", "-o", str(stl), "--teeth", "24", "--module", "1",
              "--pressure-angle", "20", "--bore-flat", "0"])
    assert stl.stat().st_size > 1000
    assert "Recess narrowed" in capsys.readouterr().err

    hexgear = tmp_path / "hexgear.stl"
    cli.main(["export", "-o", str(hexgear), "--bore-hex", "6"])
    assert hexgear.stat().st_size > 1000
    assert ("warning: Hex bore replaces the round profile: bore_d (9 mm) and bore_flat "
            "(8 mm) are ignored.") in capsys.readouterr().err

    keyed = tmp_path / "keyedgear.step"
    cli.main(["export", "-o", str(keyed), "--keyway-width", "3", "--keyway-depth", "1.4"])
    assert keyed.read_bytes().startswith(b"ISO-10303-21;")
    assert "warning:" not in capsys.readouterr().err

    chamfered = tmp_path / "chamfered.stl"
    cli.main(["export", "-o", str(chamfered), "--tip-chamfer", "0.4"])
    assert chamfered.stat().st_size > 1000
    assert "warning:" not in capsys.readouterr().err


def test_infeasible_parameters_exit_2_and_name_the_problem(
        capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        cli.main(["info", "--bore-flat", "3"])
    assert exc.value.code == 2
    assert "D-flat" in capsys.readouterr().err


def test_a_hex_bore_the_root_cannot_hold_exits_2_and_names_it(
        capsys: pytest.CaptureFixture[str]) -> None:
    """D-03a on the CLI: the same refusal the API gives, on stderr, exit 2."""
    with pytest.raises(SystemExit) as exc:
        cli.main(["info", "--bore-hex", "25"])
    assert exc.value.code == 2
    err = capsys.readouterr().err
    assert "Hex bore is too large for the root diameter" in err
    assert "reduce bore_hex" in err


def test_cli_and_api_print_the_same_hex_bore_document(
        capsys: pytest.CaptureFixture[str]) -> None:
    """REQ-cli-parity for a hex link: same document, same key order, same D-02
    warning."""
    client = TestClient(spur.app.app)

    cli.main(["info", "--bore-hex", "6"])
    cli_out = json.loads(capsys.readouterr().out)
    api_out = client.get("/api/info", params={"bore_hex": 6}).json()
    assert cli_out == api_out
    assert list(cli_out) == list(DerivedDimensions.model_fields)
    assert any("Hex bore replaces the round profile" in w for w in cli_out["warnings"])


def test_a_keyway_the_root_cannot_hold_exits_2_and_names_it(
        capsys: pytest.CaptureFixture[str]) -> None:
    """D-10 on the CLI: the same refusal the API gives, on stderr, exit 2."""
    with pytest.raises(SystemExit) as exc:
        cli.main(["info", "--keyway-width", "3", "--keyway-depth", "9.4"])
    assert exc.value.code == 2
    err = capsys.readouterr().err
    assert "Keyway is too deep for the root diameter" in err
    assert "reduce keyway_depth or keyway_width" in err


def test_cli_and_api_print_the_same_keyed_document(
        capsys: pytest.CaptureFixture[str]) -> None:
    """REQ-cli-parity for a keyed link: same document, same key order."""
    client = TestClient(spur.app.app)

    cli.main(["info", "--keyway-width", "3", "--keyway-depth", "1.4"])
    cli_out = json.loads(capsys.readouterr().out)
    api_out = client.get("/api/info",
                         params={"keyway_width": 3, "keyway_depth": 1.4}).json()
    assert cli_out == api_out
    assert list(cli_out) == list(DerivedDimensions.model_fields)


def test_cli_and_api_print_the_same_tip_chamfer_document(
        capsys: pytest.CaptureFixture[str]) -> None:
    """REQ-cli-parity for a capped tip chamfer: same document, same key order, the
    pitch-circle warning, tip_chamfer_effective 1.75."""
    client = TestClient(spur.app.app)

    cli.main(["info", "--tip-chamfer", "3"])
    cli_out = json.loads(capsys.readouterr().out)
    api_out = client.get("/api/info", params={"tip_chamfer": 3}).json()
    assert cli_out == api_out
    assert list(cli_out) == list(DerivedDimensions.model_fields)
    assert cli_out["tip_chamfer_effective"] == pytest.approx(1.75)
    assert cli_out["warnings"] == [
        "Tip chamfer reduced to 1.75 mm to keep it above the pitch circle."]


def test_cli_and_api_print_the_same_hole_document(
        capsys: pytest.CaptureFixture[str]) -> None:
    """REQ-cli-parity for a hole link: same document, same key order, both walls."""
    client = TestClient(spur.app.app)

    cli.main(["info", "--hole-count", "6", "--hole-d", "4", "--hole-circle-d", "20"])
    cli_out = json.loads(capsys.readouterr().out)
    api_out = client.get("/api/info",
                         params={"hole_count": 6, "hole_d": 4, "hole_circle_d": 20}).json()
    assert cli_out == api_out
    assert list(cli_out) == list(DerivedDimensions.model_fields)
    assert cli_out["cutout_hub_wall"] == pytest.approx(3.025)
    assert cli_out["cutout_rim_wall"] == pytest.approx(2.438)


def test_a_hole_too_close_to_the_bore_exits_2_and_names_it(
        capsys: pytest.CaptureFixture[str]) -> None:
    """D-17 on the CLI: the same hub refusal the API gives, on stderr, exit 2."""
    with pytest.raises(SystemExit) as exc:
        cli.main(["info", "--hole-count", "6", "--hole-d", "4", "--hole-circle-d", "14.7"])
    assert exc.value.code == 2
    err = capsys.readouterr().err
    assert "Lightening holes come too close to the bore" in err
    assert "increase hole_circle_d or reduce hole_d" in err


def test_unknown_output_extension_is_refused(tmp_path: Path) -> None:
    with pytest.raises(SystemExit) as exc:
        cli.main(["export", "-o", str(tmp_path / "gear.obj")])
    assert "must end in .stl or .step" in str(exc.value)


def test_a_tip_chamfer_that_selects_no_tip_arcs_stops_the_export_and_writes_nothing(
        monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """States the exit status D-14 decided. cmd_export turns every BuildError into
    `SystemExit("error: ...")`, which exits 1, and has done so since v0 (docs/
    architecture/cli.md "Errors"); exit 2 stays argparse's parameter-error code. D-14, as
    amended 2026-09-28, routes this guard to exit 1 like every BuildError, so this test
    pins the CLI as it behaves and as decided."""
    spur.model._build_cached.cache_clear()
    real = spur.model._tip_edges

    def wrapper(solid: cq.Shape, ra: float, face_width: float) -> list[cq.Edge]:
        return real(solid, ra + 1.0, face_width)  # a radius where no arc exists

    monkeypatch.setattr("spur.model._tip_edges", wrapper)
    out = tmp_path / "gear.stl"
    with pytest.raises(SystemExit) as exc:
        cli.main(["export", "-o", str(out), "--teeth", "67", "--tip-chamfer", "0.4",
                  "--quality", "preview"])
    assert str(exc.value.code).startswith("error: Tip chamfer selected no tip-arc edges")
    assert not out.exists()
