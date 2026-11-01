"""Read 1 of DIN 5480-2: the pdftotext parser, tested on invented text in the copy's layout.

Every number in the page text below is invented (D-01): the shapes are the copy's (decimal
commas, an en dash for a minus, footnote marks `a` and `b` glued or spaced, a licence-stamp
line, a module header line), the values are not. The real copy is only ever an argument of
`scripts/din5480_read1.py`.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

from scripts import din5480_read1 as read1
from scripts.din5480_read1 import ParseError, ParseResult, normalise, parse_pages
from spur.din5480_tables import part_2_provenance

REPO = Path(__file__).resolve().parents[1]
needs_checkout = pytest.mark.skipif(
    shutil.which("git") is None or not (REPO / ".git").exists(), reason="not a git checkout")

# The two characters the copy prints a minus as, spelled so the source holds neither.
EN_DASH = chr(0x2013)
MINUS_SIGN = chr(0x2212)
STAMP = "                  SUPPLIED BY BSB UNDER LICENCE FROM DIN FOR NOBODY ON 01/01/01"
# 14 nominal tokens: d_B z d d_b x1*m e2 df2 Adf2 dFf2min da2 da1 dFf1max df1 Adf1
# Invented; the 12th (dFf1 max) is the one read.
NOMINAL = "{d_b:>4} {z:>4}  9 8,111 -0,222 3,333 4 0,55 6,66 7 8,8 {form} 9,99 {dev}"
# 10 inspection tokens: d_B z hubD_M M2 A*M2 shaftD_M M1 A*M1 k Wk. Invented.
INSPECTION = "{d_b:>4} {z:>4}  1,5 2,222 0,33 {pin} {m1} 0,44 {k} 5,555"


def nominal_page(table: int, module: str, rows: list[tuple[str, str, str]],
                 *, mark: str = "") -> str:
    lines = ["DIN 0000-0:0000-00", "", f"{table // 2 + 3}    Module m = {module} mm", "",
             f"Table {table} — Nominal dimensions, m = {module} mm",
             "    dB  z  d  db  x1 . m  e1 = s1  df1", STAMP]
    for d_b, z, form in rows:
        lines.append(NOMINAL.format(d_b=d_b, z=z, form=form, dev=EN_DASH + "0,12" + mark))
    return "\n".join(lines) + "\n"


def inspection_page(table: int, module: str, rows: list[tuple[str, str, str, str, str]]) -> str:
    lines = ["DIN 0000-0:0000-00", "", f"Table {table} — Inspection dimensions, m = {module} mm",
             "    dB  z  DM  MN  A*MN  DM  MN  A*MN  k  Wk", STAMP]
    for d_b, z, pin, m1, k in rows:
        lines.append(INSPECTION.format(d_b=d_b, z=z, pin=pin, m1=m1, k=k))
    lines.append("a    The deviation values stated here relate to a method (see DIN 0000-0, 1.2).")
    return "\n".join(lines) + "\n"


def two_pages(module: str = "0,5") -> list[tuple[int, str]]:
    return [
        (8, nominal_page(2, module, [("6", "10", "5,17"), ("7", "12", "6,28")])),
        (9, inspection_page(3, module, [("6", "10", "1,0", "4,321", "3a"),
                                        ("7", "12", "1,0", "5,432", "4 a")])),
    ]


def test_normalise_reads_commas_dashes_and_marks() -> None:
    assert normalise(f"12,5 {EN_DASH} 0,3 8a") == "12.5 - 0.3 8"
    assert normalise(f"1 {MINUS_SIGN}2,5").split() == ["1", "-2.5"]
    assert normalise("12 a 4").split() == ["12", "4"]
    assert normalise("13b").split() == ["13"]


def test_normalise_keeps_a_word_that_ends_in_a() -> None:
    assert normalise("Data area").split() == ["Data", "area"]
    assert normalise("5 data") == "5 data"


def test_one_row_per_key_printed_once_on_both_pages() -> None:
    result = parse_pages(two_pages())
    assert isinstance(result, ParseResult)
    assert result.report == ()
    assert result.counts == {"pages": 2, "nominal_rows": 2, "inspection_rows": 2, "joined": 2}
    first, second = result.rows
    assert (first.module, first.reference_d, first.teeth) == (0.5, 6.0, 10)
    assert first.form_d_max_mm == 5.17
    assert first.pin_d_mm == 1.0
    assert first.m1_mm == 4.321
    assert second.m1_mm == 5.432
    assert first.provenance == part_2_provenance(0.5)


def test_the_mark_on_a_row_does_not_shift_the_tokens() -> None:
    pages = [(8, nominal_page(2, "0,5", [("6", "10", "5,17")], mark="a")),
             (9, inspection_page(3, "0,5", [("6", "10", "1,0", "4,321", "13b")]))]
    result = parse_pages(pages)
    assert result.counts["joined"] == 1


def test_the_second_module_takes_its_own_provenance() -> None:
    pages = [
        *two_pages(),
        (10, nominal_page(4, "0,6", [("8", "11", "7,07")])),
        (11, inspection_page(5, "0,6", [("8", "11", "2,0", "6,543", "3")]))]
    result = parse_pages(pages)
    assert [r.module for r in result.rows] == [0.5, 0.5, 0.6]
    assert result.rows[2].provenance == part_2_provenance(0.6)


def test_a_key_printed_twice_is_reported_not_guessed() -> None:
    # The Table 12 shape: the nominal page prints one row twice, the inspection page holds
    # the row the nominal page lacks.
    pages = [
        (8, nominal_page(2, "0,5", [("6", "10", "5,17"), ("7", "12", "6,28"),
                                     ("7", "12", "6,29")])),
        (9, inspection_page(3, "0,5", [("6", "10", "1,0", "4,321", "3"),
                                        ("7", "12", "1,0", "5,432", "4"),
                                        ("6", "12", "1,0", "5,111", "4")])),
    ]
    result = parse_pages(pages)
    assert [(r.reference_d, r.teeth) for r in result.rows] == [(6.0, 10)]
    assert len(result.report) == 2
    joined = "\n".join(result.report)
    assert "module 0.5" in joined
    assert "tables 2 and 3" in joined
    assert "pages 8, 9" in joined
    assert "d_B 7 z 12" in joined
    assert "d_B 6 z 12" in joined
    # A location line names no value of the page text.
    for invented in ("6,28", "6,29", "5,111", "6.28", "6.29", "5.111", "5.432"):
        assert invented not in joined


def test_a_stamp_and_a_header_line_are_not_rows() -> None:
    result = parse_pages(two_pages())
    assert result.counts["nominal_rows"] == 2


def test_a_row_shaped_line_with_a_word_in_it_is_an_error() -> None:
    page = nominal_page(2, "0,5", [("6", "10", "5,17")]) + \
        "   7   12   9   8,111   x   3,333   4   0,55   6,66   7   8,8   5,17   9,99   1,00\n"
    with pytest.raises(ParseError, match=r"page 8, line \d+"):
        parse_pages([(8, page), (9, inspection_page(3, "0,5", []))])


def test_a_table_number_out_of_step_with_its_module_is_an_error() -> None:
    with pytest.raises(ParseError, match="table 4"):
        parse_pages([(8, nominal_page(4, "0,5", []))])


def test_a_page_with_no_title_is_an_error() -> None:
    with pytest.raises(ParseError, match="page 8"):
        parse_pages([(8, "nothing here\n")])


def test_a_module_outside_part_2_is_an_error() -> None:
    with pytest.raises(ParseError, match="module"):
        parse_pages([(8, nominal_page(2, "0,7", []))])


def test_a_page_in_the_wrong_place_is_an_error() -> None:
    with pytest.raises(ParseError, match="page 20"):
        parse_pages([(20, nominal_page(2, "0,5", []))])


def test_a_non_integer_tooth_count_is_an_error() -> None:
    with pytest.raises(ParseError, match="tooth count"):
        parse_pages([(8, nominal_page(2, "0,5", [("6", "10,5", "5,17")]))])


@needs_checkout
def test_a_read_cannot_be_written_into_a_tracked_path() -> None:
    with pytest.raises(SystemExit, match=r"x\.json"):
        read1.ensure_ignored(REPO / "tests" / "x.json")


def test_a_repository_git_cannot_read_refuses_and_creates_nothing(tmp_path: Path) -> None:
    """Git exits 128 for a corrupt repository exactly as for no repository (WR-01)."""
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / ".git" / "HEAD").write_text("garbage\n", encoding="ascii")
    with pytest.raises(SystemExit, match="cannot say"):
        read1.ensure_ignored(tmp_path / "new" / "reads" / "x.json")
    assert not (tmp_path / "new").exists()


def test_a_path_outside_any_repository_passes_and_gets_its_directory(tmp_path: Path) -> None:
    read1.ensure_ignored(tmp_path / "new" / "x.json")
    assert (tmp_path / "new").is_dir()


@needs_checkout
def test_the_private_reads_directory_passes() -> None:
    read1.ensure_ignored(REPO / "private" / "reads" / "x.json")


def test_main_writes_nothing_when_the_loader_refuses(
        tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # An invented M1 that fails the identity: the loader refuses, no file appears.
    out = tmp_path / "read.json"
    monkeypatch.setattr(read1, "ensure_ignored", lambda _path: None)
    monkeypatch.setattr(read1, "extract_pages", lambda _pdf: two_pages())
    assert read1.main(["whatever.pdf", "-o", str(out)]) == 1
    assert not out.exists()
