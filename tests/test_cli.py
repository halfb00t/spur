"""The CLI had no tests, and the README's own example did not run."""

import json

import pytest

from spur import cli


def test_info_reports_the_mate_it_was_asked_about(capsys):
    cli.main(["info", "--teeth", "19", "--mate-teeth", "40"])
    out = json.loads(capsys.readouterr().out)
    assert out["mate_teeth"] == 40
    assert out["centre_distance"] == pytest.approx(51.625)


def test_readme_export_examples_run(tmp_path, capsys):
    step = tmp_path / "gear.step"
    cli.main(["export", "-o", str(step)])
    assert step.read_bytes().startswith(b"ISO-10303-21;")

    stl = tmp_path / "gear.stl"
    cli.main(["export", "-o", str(stl), "--teeth", "24", "--module", "1",
              "--pressure-angle", "20", "--bore-flat", "0"])
    assert stl.stat().st_size > 1000
    assert "Recess narrowed" in capsys.readouterr().err


def test_infeasible_parameters_exit_2_and_name_the_problem(capsys):
    with pytest.raises(SystemExit) as exc:
        cli.main(["info", "--bore-flat", "3"])
    assert exc.value.code == 2
    assert "D-flat" in capsys.readouterr().err


def test_unknown_output_extension_is_refused(tmp_path):
    with pytest.raises(SystemExit) as exc:
        cli.main(["export", "-o", str(tmp_path / "gear.obj")])
    assert "must end in .stl or .step" in str(exc.value)
