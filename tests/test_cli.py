"""The CLI had no tests, and the README's own example did not run."""

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import spur.app
from spur import cli
from spur.calc import DerivedDimensions


def test_info_reports_the_mate_it_was_asked_about(capsys: pytest.CaptureFixture[str]) -> None:
    cli.main(["info", "--teeth", "19", "--mate-teeth", "40"])
    out = json.loads(capsys.readouterr().out)
    assert out["mate_teeth"] == 40
    assert out["centre_distance"] == pytest.approx(51.625)


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


def test_infeasible_parameters_exit_2_and_name_the_problem(
        capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        cli.main(["info", "--bore-flat", "3"])
    assert exc.value.code == 2
    assert "D-flat" in capsys.readouterr().err


def test_unknown_output_extension_is_refused(tmp_path: Path) -> None:
    with pytest.raises(SystemExit) as exc:
        cli.main(["export", "-o", str(tmp_path / "gear.obj")])
    assert "must end in .stl or .step" in str(exc.value)
