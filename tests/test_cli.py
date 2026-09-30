"""The CLI had no tests, and the README's own example did not run."""

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import get_args

import cadquery as cq
import pytest
from composition import BORE_REFUSALS, CUTOUT_REFUSALS
from fastapi.testclient import TestClient

import spur.app
import spur.model
from spur import cli
from spur.app import InfoQuery
from spur.calc import DerivedDimensions, check
from spur.params import GearParams

# The README's composed link (D-14): every v0.2 family on one 19-tooth gear -- a keyed
# round bore, spoke arms, both recesses (the default) and a tooth-tip chamfer. Order
# matches the README line so `_flags` reproduces it verbatim.
COMPOSED: dict[str, object] = {
    "bore_flat": 0, "keyway_width": 3, "keyway_depth": 1.4, "spoke_count": 4,
    "spoke_width": 2, "hub_d": 13.2, "rim_wall": 1, "spoke_fillet": 1, "tip_chamfer": 0.4,
}


def _flags(params: dict[str, object]) -> list[str]:
    """A parameter dict as `--name-with-dashes=value` CLI arguments."""
    return [f"--{k.replace('_', '-')}={v}" for k, v in params.items()]


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

    holes = tmp_path / "holes.stl"
    cli.main(["export", "-o", str(holes), "--hole-count", "6", "--hole-d", "4",
              "--hole-circle-d", "20"])
    assert holes.stat().st_size > 1000
    assert "warning:" not in capsys.readouterr().err

    spokes = tmp_path / "spokes.stl"
    cli.main(["export", "-o", str(spokes), "--spoke-count", "4", "--spoke-width", "2",
              "--hub-d", "12", "--rim-wall", "1", "--spoke-fillet", "1"])
    assert spokes.stat().st_size > 1000
    assert "warning:" not in capsys.readouterr().err

    honeycomb = tmp_path / "honeycomb.stl"
    cli.main(["export", "-o", str(honeycomb), "--hex-cell", "3", "--hex-wall", "1"])
    assert honeycomb.stat().st_size > 1000
    assert "warning:" not in capsys.readouterr().err

    # D-14: the composed link -- every v0.2 family on one gear -- is documented, and the
    # documented command is asserted present before it is run (a doc/test drift would
    # fail here, not silently pass on a hand-typed copy).
    readme = (Path(__file__).parents[1] / "README.md").read_text()
    # The README spells flags space-separated (`--flag value`), _flags spells them
    # `--flag=value`; compare on the documented form.
    composed_cmd_readme_form = ("spur export -o everything.stl "
                                + " ".join(f"--{k.replace('_', '-')} {v}"
                                          for k, v in COMPOSED.items()))
    assert composed_cmd_readme_form in readme

    everything = tmp_path / "everything.stl"
    cli.main(["export", "-o", str(everything), *_flags(COMPOSED)])
    assert everything.stat().st_size > 1000
    assert "warning:" not in capsys.readouterr().err


def test_cli_and_api_print_the_same_composed_document(
        capsys: pytest.CaptureFixture[str]) -> None:
    """D-11: the composed link (every v0.2 family on) and the empty link (edge: empty)
    print the identical document on both interfaces, byte for byte once the API's
    compact JSON is re-indented the way the CLI already indents it (A1 -- the raw bytes
    can never match, since the API serves compact JSON and the CLI prints
    `indent=2`)."""
    client = TestClient(spur.app.app)

    for params in (COMPOSED, {}):
        cli.main(["info", *_flags(params)])
        cli_out = capsys.readouterr().out.rstrip("\n")
        api_out = client.get("/api/info", params=params)
        want = json.dumps(api_out.json(), indent=2, ensure_ascii=False)
        assert cli_out == want
        assert list(json.loads(cli_out)) == list(DerivedDimensions.model_fields)

    cli.main(["info", *_flags(COMPOSED)])
    composed_doc = json.loads(capsys.readouterr().out)
    assert composed_doc["warnings"] == []
    for key in ("tip_chamfer_effective", "bore_effective", "keyway_floor_to_wall",
               "keyway_width_effective", "recess_id", "recess_od", "recess_fillet",
               "web", "cutout_hub_wall", "cutout_rim_wall", "spoke_fillet_effective"):
        assert composed_doc[key] is not None, key


def test_every_gear_field_reaches_the_schema_the_form_and_the_cli_in_one_order(
        capsys: pytest.CaptureFixture[str]) -> None:
    """D-11: walks `GearParams.model_fields` -- never the consumer under test's own
    field list -- across `/api/schema` (the form's source) and the CLI parser. A field
    missing a group/title/unit/step, a moved field, or a flag that drifted from its
    field name now fails here generically, instead of only on the handful of fields the
    per-feature parity tests happen to cover.

    Order and group names are pinned, not discretionary (12-01-SUMMARY.md, the human's
    binding "seven" answer): the schema carries seven groups, in this order --
    Teeth, Body, Bore, Recess, Spokes, Holes, Honeycomb -- and `recess_sides` lives in
    Recess, checked as `enum`, not `step`.
    """
    names = list(GearParams.model_fields)
    props = TestClient(spur.app.app).get("/api/schema").json()["properties"]
    assert list(props) == names  # buildForm() renders schema.properties in this order

    for name in names:
        prop = props[name]
        assert "group" in prop, name
        assert "title" in prop, name
        assert "unit" in prop, name
        if name == "recess_sides":
            assert "step" not in prop
        else:
            assert "step" in prop, name

    assert props["recess_sides"]["enum"] == list(
        get_args(GearParams.model_fields["recess_sides"].annotation))

    # Each fieldset holds a contiguous run: a group may not start, end and then start
    # again further down the field list.
    seen_groups: list[str] = []
    for name in names:
        group = props[name]["group"]
        if not seen_groups or seen_groups[-1] != group:
            assert group not in seen_groups, f"group {group!r} reappeared out of order"
            seen_groups.append(group)
    assert seen_groups == ["Teeth", "Body", "Bore", "Recess", "Spokes", "Holes",
                          "Honeycomb"]

    with pytest.raises(SystemExit) as exc:
        cli.main(["info", "--help"])
    assert exc.value.code == 0
    out = capsys.readouterr().out
    _, _, after = out.partition("gear parameters (defaults in brackets):\n")
    assert after  # the section header must have been found
    flags = re.findall(r"^\s+(--[a-z][a-z-]*)", after, re.MULTILINE)
    assert flags == ["--" + n.replace("_", "-") for n in names]


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


def test_cli_and_api_print_the_same_spoke_document(
        capsys: pytest.CaptureFixture[str]) -> None:
    """REQ-cli-parity for a spoke link: same document, same key order, and the
    fillet cap's warning when spoke_fillet is set past its limit."""
    client = TestClient(spur.app.app)

    cli.main(["info", "--spoke-count", "4", "--spoke-width", "2", "--hub-d", "12",
              "--rim-wall", "1", "--spoke-fillet", "5"])
    cli_out = json.loads(capsys.readouterr().out)
    api_out = client.get("/api/info", params={"spoke_count": 4, "spoke_width": 2,
                                              "hub_d": 12, "rim_wall": 1,
                                              "spoke_fillet": 5}).json()
    assert cli_out == api_out
    assert list(cli_out) == list(DerivedDimensions.model_fields)
    assert cli_out["spoke_fillet_effective"] == pytest.approx(3.337)
    assert cli_out["warnings"] == [
        "Spoke fillet reduced to 3.337 mm to fit the opening between the arms at "
        "the hub."]


def test_a_rim_wall_under_min_wall_exits_2_and_names_it(
        capsys: pytest.CaptureFixture[str]) -> None:
    """D-17 on the CLI: the same rim-wall refusal the API gives, on stderr, exit 2."""
    with pytest.raises(SystemExit) as exc:
        cli.main(["info", "--spoke-count", "4", "--spoke-width", "2", "--hub-d", "12",
                  "--rim-wall", "0.35"])
    assert exc.value.code == 2
    err = capsys.readouterr().err
    assert "The rim wall (0.35 mm) is thinner than 0.4 mm" in err
    assert "increase rim_wall" in err


def test_cli_and_api_print_the_same_honeycomb_document(
        capsys: pytest.CaptureFixture[str]) -> None:
    """REQ-cli-parity for a honeycomb link: same document, same key order, and the
    raise-to-fit warning on a large gear."""
    client = TestClient(spur.app.app)

    cli.main(["info", "--teeth", "200", "--hex-cell", "3", "--hex-wall", "1"])
    cli_out = json.loads(capsys.readouterr().out)
    api_out = client.get("/api/info",
                         params={"teeth": 200, "hex_cell": 3, "hex_wall": 1}).json()
    assert cli_out == api_out
    assert list(cli_out) == list(DerivedDimensions.model_fields)
    assert cli_out["hex_cell_effective"] > 3
    # Root fillet also caps at 200 teeth (pre-existing, unrelated to the honeycomb) --
    # the honeycomb's own warning is checked by substring, not an exact single-length
    # tuple.
    assert any(w.startswith("Honeycomb cells enlarged from 3 mm to ")
              for w in cli_out["warnings"])


def test_a_honeycomb_wall_under_min_wall_exits_2_and_names_it(
        capsys: pytest.CaptureFixture[str]) -> None:
    """D-10 on the CLI: the same wall refusal the API gives, on stderr, exit 2."""
    with pytest.raises(SystemExit) as exc:
        cli.main(["info", "--hex-cell", "3", "--hex-wall", "0.35"])
    assert exc.value.code == 2
    err = capsys.readouterr().err
    assert "The honeycomb wall (0.35 mm) is thinner than 0.4 mm" in err
    assert "increase hex_wall" in err


_ALL_REFUSALS: dict[str, dict[str, object]] = {**BORE_REFUSALS, **CUTOUT_REFUSALS}


@pytest.mark.parametrize(("refusal_id", "refusal"), list(_ALL_REFUSALS.items()),
                         ids=list(_ALL_REFUSALS))
def test_every_refusal_reads_the_same_on_the_api_and_the_cli(
        refusal_id: str, refusal: dict[str, object],
        capsys: pytest.CaptureFixture[str]) -> None:
    """D-08 (one API row and one CLI row per refusal) and D-11: each of the 23 locked
    refusals (`tests/composition.py`'s `BORE_REFUSALS`/`CUTOUT_REFUSALS`), composed with
    the tip chamfer and a single-sided recess, gives the identical sentence on the
    API's 422 and the CLI's exit 2.

    `tests/composition.py`'s `BORE_REFUSAL_FAMILIES`/`CUTOUT_REFUSAL_FAMILIES` list
    "tip"/`TIPS["on"]` and "recess-top"/`RECESSES["top"]` (never together) among the
    families 12-05's own calc-level test already proves leave a refusal's sentence and
    fields unchanged; neither appears in that test's `TWO_REFUSALS` or `DATUM_ROWS`
    tables, so composing both together, as this test does, carries no extra risk of a
    second refusal or a moved datum. `sentence`/`fields` are calc's own, read from
    `check()` on the refusal alone -- a differential test of an invariant (12-05's
    shape), not an oracle derived from the code under test (L08).
    """
    params: dict[str, object] = {"tip_chamfer": 1.75, "recess_sides": "top", **refusal}
    alone = check(GearParams.model_construct(**refusal))  # type: ignore[arg-type]
    sentence = " ".join(s for s, _ in alone)
    fields = sorted({f for _, fs in alone for f in fs})

    client = TestClient(spur.app.app)
    r = client.get("/api/info", params=params)
    assert r.status_code == 422
    detail = r.json()["detail"][0]
    assert detail["msg"] == sentence
    assert detail["ctx"]["fields"] == fields

    with pytest.raises(SystemExit) as exc:
        cli.main(["info", *_flags(params)])
    assert exc.value.code == 2
    err = capsys.readouterr().err.strip()
    assert err == f"error: {sentence}"


def test_unknown_output_extension_is_refused(tmp_path: Path) -> None:
    with pytest.raises(SystemExit) as exc:
        cli.main(["export", "-o", str(tmp_path / "gear.obj")])
    assert "must end in .stl or .step" in str(exc.value)
    # A SystemExit raised with a string argument prints it and exits 1, not argparse's 2
    # (D-13) -- cli.md's "Errors" section states this exactly.
    assert exc.value.code == "error: output must end in .stl or .step (or pass --format)"


def test_an_unknown_output_extension_exits_1_from_the_real_process(tmp_path: Path) -> None:
    """The doc's claim (cli.md "Errors") executed once against the real process, not just
    SystemExit's own `code` attribute -- the debt this closes (D-13) was exactly that the
    doc's claim had never been executed. `cmd_export` imports the kernel before checking
    the extension, so this subprocess costs ~2 s (measured at planning); every other test
    in this file calls `cli.main()` in-process instead."""
    out = tmp_path / "gear.obj"
    result = subprocess.run(
        [sys.executable, "-m", "spur.cli", "export", "-o", str(out)],
        capture_output=True, text=True, check=False)
    assert result.returncode == 1
    assert "error: output must end in .stl or .step (or pass --format)" in result.stderr
    assert not out.exists()


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
    assert isinstance(exc.value.code, str)  # a BuildError exits 1, not argparse's 2 (D-13)
    assert not out.exists()
