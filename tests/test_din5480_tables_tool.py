"""The check, diff, join and assemble tool for the two DIN 5480 reads (34-03, D-03, D-08).

Every table value here comes from the synthetic fixture, so nothing in this file is a value
of the standard. The tests assert what the tool prints: locations by default, never a value,
and nothing written unless the two pairs of reads agree.
"""

from __future__ import annotations

import json
import shutil
from collections.abc import Callable
from pathlib import Path

import din5480_tables_fixture as fixture
import pytest

from scripts import din5480_tables_tool as tool
from spur.din5480_tables import Tables, canonical, parse

REPO = Path(__file__).resolve().parents[1]
needs_checkout = pytest.mark.skipif(
    shutil.which("git") is None or not (REPO / ".git").exists(), reason="not a git checkout")


def document() -> dict[str, list[dict[str, object]]]:
    loaded: dict[str, list[dict[str, object]]] = json.loads(fixture.text())
    return loaded


def write(path: Path, doc: dict[str, list[dict[str, object]]] | None = None) -> Path:
    path.write_text(json.dumps(document() if doc is None else doc), encoding="utf-8")
    return path


def edited(path: Path, edit: Callable[[dict[str, list[dict[str, object]]]], None]) -> Path:
    doc = document()
    edit(doc)
    return write(path, doc)


def run(capsys: pytest.CaptureFixture[str], *argv: str) -> tuple[int, str]:
    code = tool.main(list(argv))
    captured = capsys.readouterr()
    return code, captured.out + captured.err


def split(tmp_path: Path) -> tuple[Path, Path]:
    """The fixture as a sizes-only document and a Table 7-only document."""
    t = fixture.build()
    part2 = Tables(schema_version=1, sizes=t.sizes, deviations=(), classes=(), tolerances=(),
                   columns=())
    table7 = Tables(schema_version=1, sizes=(), deviations=t.deviations, classes=t.classes,
                    tolerances=t.tolerances, columns=t.columns)
    a = tmp_path / "part2.json"
    c = tmp_path / "table7.json"
    a.write_text(canonical(part2), encoding="utf-8")
    c.write_text(canonical(table7), encoding="utf-8")
    return a, c


def twin(path: Path) -> Path:
    """A byte-identical second read: assemble refuses the same path given twice (WR-04)."""
    copy = path.with_name(path.stem + "-twin" + path.suffix)
    copy.write_bytes(path.read_bytes())
    return copy


# --- check ---------------------------------------------------------------------------

def test_check_says_ok_for_the_fixture(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code, out = run(capsys, "check", str(write(tmp_path / "a.json")))
    assert (code, out.strip()) == (0, "ok")


def test_check_lists_each_problem_by_location(
        tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    def break_it(doc: dict[str, list[dict[str, object]]]) -> None:
        doc["tolerances"][0]["t_g_um"] = 12345
    code, out = run(capsys, "check", str(edited(tmp_path / "a.json", break_it)))
    assert code == 1
    assert "T_G" in out
    assert "12345" not in out


def test_check_complete_lists_every_shortfall(
        tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code, out = run(capsys, "check", "--complete", str(write(tmp_path / "a.json")))
    assert code == 1
    for name in ("sizes", "modules", "letters", "classes", "tolerance_rows", "column_rows",
                 "columns_per_row"):
        assert name in out, name


def test_check_complete_passes_a_document_with_the_expected_counts(
        tmp_path: Path, capsys: pytest.CaptureFixture[str],
        monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(tool, "EXPECTED_COUNTS", FIXTURE_COUNTS)
    code, out = run(capsys, "check", "--complete", str(write(tmp_path / "a.json")))
    assert (code, out.strip()) == (0, "ok")


FIXTURE_COUNTS = {"sizes": 5, "modules": 3, "letters": 3, "columns_per_row": 3, "classes": 3,
                  "tolerance_rows": 5, "column_rows": 5}


def test_the_expected_counts_are_the_standards_shape() -> None:
    assert tool.EXPECTED_COUNTS == {
        "sizes": 720, "modules": 16, "letters": 18, "columns_per_row": 9, "classes": 8,
        "tolerance_rows": 30, "column_rows": 21}


# --- diff ----------------------------------------------------------------------------

def test_diff_two_equal_reads_give_zero(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    a = write(tmp_path / "a.json")
    code, out = run(capsys, "diff", str(a), str(twin(a)))
    assert (code, out.strip()) == (0, "0 differences")


def test_diff_one_changed_cell_gives_one_location_line_and_no_value(
        tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    def change(doc: dict[str, list[dict[str, object]]]) -> None:
        row = doc["tolerances"][2]
        assert row["t_g_um"] == 45   # row 3 of the invented table: (6+4*3) + (9+6*3)
        row["t_g_um"] = 4711
    a, b = write(tmp_path / "a.json"), edited(tmp_path / "b.json", change)
    code, out = run(capsys, "diff", str(a), str(b))
    lines = out.strip().splitlines()
    assert code == 1
    assert len(lines) == 2
    assert lines[0] == "tolerances 3, t_g_um: part 1, table 7, page(s) 24"
    assert lines[1] == "1 differences"
    # Pitfall 3: the default output carries no field value, old or new.
    assert "4711" not in out
    assert "45" not in out


def test_diff_prints_values_only_on_request(
        tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    def change(doc: dict[str, list[dict[str, object]]]) -> None:
        doc["tolerances"][2]["t_g_um"] = 4711
    a, b = write(tmp_path / "a.json"), edited(tmp_path / "b.json", change)
    code, out = run(capsys, "diff", "--values", str(a), str(b))
    assert code == 1
    assert "4711" in out
    assert "45" in out


def test_diff_compares_provenance_too(
        tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    def change(doc: dict[str, list[dict[str, object]]]) -> None:
        doc["deviations"][0]["provenance"] = {"part": 1, "clause": "10.8", "table": "7",
                                              "pages": [24]}
    a, b = write(tmp_path / "a.json"), edited(tmp_path / "b.json", change)
    code, out = run(capsys, "diff", str(a), str(b))
    assert code == 1
    assert "provenance.clause" in out


def test_diff_locates_a_tuple_cell_by_its_column(
        tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    def change(doc: dict[str, list[dict[str, object]]]) -> None:
        a_s = doc["deviations"][0]["a_s_um"]
        assert isinstance(a_s, list)
        a_s[1] += 1
    a, b = write(tmp_path / "a.json"), edited(tmp_path / "b.json", change)
    code, out = run(capsys, "diff", str(a), str(b))
    assert code == 1
    assert out.splitlines()[0].startswith("deviations f, a_s_um[2]:")


def test_diff_reports_a_row_only_one_read_holds_with_its_key(
        tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    def drop(doc: dict[str, list[dict[str, object]]]) -> None:
        del doc["sizes"][0]
    a, b = write(tmp_path / "a.json"), edited(tmp_path / "b.json", drop)
    code, out = run(capsys, "diff", str(a), str(b))
    assert code == 1
    assert out.splitlines()[0].startswith("only in A: sizes (1.25, 25.0, 18)")
    code, out = run(capsys, "diff", str(b), str(a))
    assert out.splitlines()[0].startswith("only in B: sizes (1.25, 25.0, 18)")


def test_two_empty_documents_diff_to_zero(
        tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    empty = tmp_path / "e.json"
    empty.write_text(canonical(Tables(schema_version=1, sizes=(), deviations=(), classes=(),
                                      tolerances=(), columns=())), encoding="utf-8")
    code, out = run(capsys, "diff", str(empty), str(twin(empty)))
    assert (code, out.strip()) == (0, "0 differences")


def test_diff_never_calls_a_skipped_row_equal(
        tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    empty = tmp_path / "e.json"
    empty.write_text(canonical(Tables(schema_version=1, sizes=(), deviations=(), classes=(),
                                      tolerances=(), columns=())), encoding="utf-8")
    code, out = run(capsys, "diff", str(write(tmp_path / "a.json")), str(empty))
    assert code == 1
    assert out.count("only in A") == 5 + 3 + 3 + 5 + 5


def test_diff_ignores_row_order(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    def reverse(doc: dict[str, list[dict[str, object]]]) -> None:
        for kind in tool.KINDS:
            doc[kind].reverse()
    a, b = write(tmp_path / "a.json"), edited(tmp_path / "b.json", reverse)
    code, out = run(capsys, "diff", str(a), str(b))
    assert (code, out.strip()) == (0, "0 differences")


def test_diff_counts_a_key_printed_twice_in_one_read(
        tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    def duplicate(doc: dict[str, list[dict[str, object]]]) -> None:
        doc["sizes"].append(dict(doc["sizes"][0]))
    a, b = write(tmp_path / "a.json"), edited(tmp_path / "b.json", duplicate)
    code, out = run(capsys, "diff", str(a), str(b))
    assert code == 1
    assert "duplicate key in B: sizes (1.25, 25.0, 18)" in out


# --- join ----------------------------------------------------------------------------

def test_join_concatenates_the_parts(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    a, c = split(tmp_path)
    out_path = tmp_path / "joined.json"
    code, _ = run(capsys, "join", str(out_path), str(a), str(c))
    assert code == 0
    joined = Tables.model_validate_json(out_path.read_text(encoding="utf-8"))
    assert canonical(joined) == canonical(fixture.build())


def test_join_refuses_a_key_present_in_both_inputs(tmp_path: Path) -> None:
    a, _ = split(tmp_path)
    out_path = tmp_path / "joined.json"
    with pytest.raises(SystemExit, match=r"sizes \(1\.25, 25\.0, 18\)"):
        tool.main(["join", str(out_path), str(a), str(twin(a))])
    assert not out_path.exists()


# --- assemble ------------------------------------------------------------------------

def test_assemble_writes_the_union_when_both_pairs_agree(
        tmp_path: Path, capsys: pytest.CaptureFixture[str],
        monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(tool, "EXPECTED_COUNTS", FIXTURE_COUNTS)
    a, c = split(tmp_path)
    out_path = tmp_path / "tables.json"
    code, out = run(capsys, "assemble", str(out_path), "--part2", str(a), str(twin(a)),
                    "--table7", str(c), str(twin(c)))
    assert code == 0
    assert out_path.read_text(encoding="utf-8") == fixture.text()
    assert "bytes" in out
    assert "sha256" in out
    parse(out_path.read_text(encoding="utf-8"))


@pytest.mark.parametrize("option", ["--part2", "--table7"])
def test_assemble_refuses_one_read_given_twice(
        option: str, tmp_path: Path, capsys: pytest.CaptureFixture[str],
        monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(tool, "EXPECTED_COUNTS", FIXTURE_COUNTS)
    a, c = split(tmp_path)
    p2 = (a, a) if option == "--part2" else (a, twin(a))
    t7 = (c, c) if option == "--table7" else (c, twin(c))
    out_path = tmp_path / "tables.json"
    code, out = run(capsys, "assemble", str(out_path), "--part2", str(p2[0]), str(p2[1]),
                    "--table7", str(t7[0]), str(t7[1]))
    assert code == 1
    assert f"{option} names one file twice" in out
    assert not out_path.exists()


def test_assemble_refuses_while_the_part_2_reads_differ(
        tmp_path: Path, capsys: pytest.CaptureFixture[str],
        monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(tool, "EXPECTED_COUNTS", FIXTURE_COUNTS)
    a, c = split(tmp_path)
    doc = json.loads(a.read_text(encoding="utf-8"))
    doc["sizes"][0]["m1_mm"] += 0.001
    b = tmp_path / "part2-b.json"
    b.write_text(json.dumps(doc), encoding="utf-8")
    out_path = tmp_path / "tables.json"
    code, out = run(capsys, "assemble", str(out_path), "--part2", str(a), str(b),
                    "--table7", str(c), str(twin(c)))
    assert code == 1
    assert "m1_mm" in out
    assert not out_path.exists()


def test_assemble_refuses_while_the_table_7_reads_differ(
        tmp_path: Path, capsys: pytest.CaptureFixture[str],
        monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(tool, "EXPECTED_COUNTS", FIXTURE_COUNTS)
    a, c = split(tmp_path)
    doc = json.loads(c.read_text(encoding="utf-8"))
    doc["deviations"][0]["a_s_um"][0] -= 1
    d = tmp_path / "table7-b.json"
    d.write_text(json.dumps(doc), encoding="utf-8")
    out_path = tmp_path / "tables.json"
    code, out = run(capsys, "assemble", str(out_path), "--part2", str(a), str(twin(a)),
                    "--table7", str(c), str(d))
    assert code == 1
    assert "a_s_um[1]" in out
    assert not out_path.exists()


def test_assemble_refuses_a_part_2_input_holding_table_7_rows(
        tmp_path: Path, capsys: pytest.CaptureFixture[str],
        monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(tool, "EXPECTED_COUNTS", FIXTURE_COUNTS)
    a, c = split(tmp_path)
    whole = write(tmp_path / "whole.json")
    out_path = tmp_path / "tables.json"
    code, out = run(capsys, "assemble", str(out_path), "--part2", str(whole), str(twin(whole)),
                    "--table7", str(c), str(twin(c)))
    assert code == 1
    assert "part2" in out
    code, out = run(capsys, "assemble", str(out_path), "--part2", str(a), str(twin(a)),
                    "--table7", str(whole), str(twin(whole)))
    assert code == 1
    assert "table7" in out
    assert not out_path.exists()


def test_assemble_refuses_an_incomplete_table(
        tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    # The real EXPECTED_COUNTS against the small fixture: a file missing a letter would read
    # as "fit outside Table 7", so assemble must not write it.
    a, c = split(tmp_path)
    out_path = tmp_path / "tables.json"
    code, out = run(capsys, "assemble", str(out_path), "--part2", str(a), str(twin(a)),
                    "--table7", str(c), str(twin(c)))
    assert code == 1
    assert "sizes" in out
    assert not out_path.exists()


@needs_checkout
def test_assemble_and_join_refuse_a_path_git_does_not_ignore(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(tool, "EXPECTED_COUNTS", FIXTURE_COUNTS)
    a, c = split(tmp_path)
    tracked = REPO / "tests" / "_tool_guard.json"
    with pytest.raises(SystemExit, match="_tool_guard"):
        tool.main(["assemble", str(tracked), "--part2", str(a), str(twin(a)),
                   "--table7", str(c), str(twin(c))])
    with pytest.raises(SystemExit, match="_tool_guard"):
        tool.main(["join", str(tracked), str(a), str(c)])
    assert not tracked.exists()
