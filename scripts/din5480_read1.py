"""`make tables.read1`: read 1 of DIN 5480-2, a `pdftotext -layout` parser (D-06).

Reads pages 8 to 39 of the human's licensed copy (Tables 2 to 33: a nominal and an
inspection table for each of the 16 modules) and writes a sizes-only `Tables` document: per
size, d_Ff1 max from the nominal table, the shaft's D_M and M1 from the inspection table.
The PDF path is an argument and no value of the standard is in this file (D-01); the output
path must be one git ignores, because a read is the licensed values.

The copy's quirks are handled on purpose, each measured on it (34-RESEARCH Pitfall 10):

- decimal commas, and U+2013 or U+2212 as the minus sign: normalised before anything is read;
- footnote marks after a number, glued (`8a`) or spaced (`12 a`), and two letters occur,
  `a` and `b` (the `b` once, on an m 8 inspection row; stripping only `a` read 720 rows);
- one licence-stamp line per page and one module header line (6 tokens): skipped by shape,
  because a row is exactly 14 numeric tokens (nominal) or 10 (inspection);
- Table 12 prints one nominal row twice where Table 13 has another key. A key that is not
  printed exactly once on both pages of its module is not joined and not guessed: it is
  reported by location, and the human settles it from the page (D-08).

A row-shaped line (two leading numbers, 10 or more tokens) holding something that is not a
number is an error naming the page and line, never a skipped row.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import NamedTuple

from spur.din5480_tables import (
    PART_2_MODULES,
    SizeRow,
    Tables,
    TablesError,
    canonical,
    parse,
    part_2_provenance,
)

FIRST_PAGE = 8
LAST_PAGE = 39
NOMINAL_TOKENS = 14
INSPECTION_TOKENS = 10
# Token positions in a row (0-based): d_B and z lead both kinds.
NOMINAL_FORM_D_MAX = 11   # the 12th token
INSPECTION_PIN_D = 5      # the 6th token, the shaft's D_M (the second D_M column)
INSPECTION_M1 = 6         # the 7th token

_NUM = re.compile(r"^-?\d+(\.\d+)?$")
_TITLE = re.compile(
    r"Table\s+(\d+)\s*[-—]\s*(Nominal|Inspection)\s+dimensions[.,]\s*m\s*=\s*(\d+(?:\.\d+)?)\s*mm")


class ParseError(ValueError):
    """The text is not shaped like the copy; `str()` names the page and line."""


class ParseResult(NamedTuple):
    rows: tuple[SizeRow, ...]
    report: tuple[str, ...]
    counts: dict[str, int]


def normalise(line: str) -> str:
    """U+2013 and U+2212 to `-`, the decimal comma to `.`, footnote marks a and b removed."""
    line = line.replace(chr(0x2013), "-").replace(chr(0x2212), "-").replace(",", ".")
    return re.sub(r"(?<=\d)\s*[ab]\b", " ", line).strip()


def _number(token: str, page: int, number: int) -> float:
    if not _NUM.match(token):
        raise ParseError(f"page {page}, line {number}: not a number")
    return float(token)


def _tooth_count(token: str, page: int, number: int) -> int:
    if not re.fullmatch(r"\d+", token):
        raise ParseError(f"page {page}, line {number}: tooth count is not an integer")
    return int(token)


def _read_page(page: int, text: str) -> tuple[float, str, int, list[tuple[int, list[str]]]]:
    """(module, kind, table number, [(line number, tokens) per row]) of one page."""
    title: re.Match[str] | None = None
    rows: list[tuple[int, list[str]]] = []
    for number, raw in enumerate(text.splitlines(), start=1):
        line = normalise(raw)
        if title is None:
            title = _TITLE.search(line)
            continue
        tokens = line.split()
        if all(_NUM.match(t) for t in tokens):
            if len(tokens) in (NOMINAL_TOKENS, INSPECTION_TOKENS):
                rows.append((number, tokens))
        elif (len(tokens) >= INSPECTION_TOKENS and _NUM.match(tokens[0])
              and _NUM.match(tokens[1])):
            raise ParseError(f"page {page}, line {number}: a row holds a token that is "
                             "not a number")
    if title is None:
        raise ParseError(f"page {page}: no table title")
    kind = title.group(2)
    want = NOMINAL_TOKENS if kind == "Nominal" else INSPECTION_TOKENS
    for number, tokens in rows:
        if len(tokens) != want:
            raise ParseError(f"page {page}, line {number}: a {kind.lower()} row has "
                             f"{len(tokens)} columns, not {want}")
    return float(title.group(3)), kind, int(title.group(1)), rows


def parse_pages(pages: Sequence[tuple[int, str]]) -> ParseResult:
    """Join each module's nominal and inspection page on (d_B, z)."""
    nominal: dict[float, dict[tuple[float, int], list[list[str]]]] = {}
    inspection: dict[float, dict[tuple[float, int], list[list[str]]]] = {}
    counts = {"pages": 0, "nominal_rows": 0, "inspection_rows": 0, "joined": 0}
    for page, text in pages:
        module, kind, table, rows = _read_page(page, text)
        if module not in PART_2_MODULES:
            raise ParseError(f"page {page}: module {module:g} is not one of the 16 of Part 2")
        i = PART_2_MODULES.index(module)
        want_table = 2 + 2 * i if kind == "Nominal" else 3 + 2 * i
        want_page = FIRST_PAGE + 2 * i if kind == "Nominal" else FIRST_PAGE + 1 + 2 * i
        if table != want_table:
            raise ParseError(f"page {page}: table {table} where module {module:g} "
                             f"has table {want_table}")
        if page != want_page:
            raise ParseError(f"page {page}: module {module:g} {kind.lower()} table is on "
                             f"page {want_page}")
        keyed: dict[tuple[float, int], list[list[str]]] = {}
        for number, tokens in rows:
            key = (_number(tokens[0], page, number), _tooth_count(tokens[1], page, number))
            keyed.setdefault(key, []).append(tokens)
        target = nominal if kind == "Nominal" else inspection
        if module in target:
            raise ParseError(f"page {page}: module {module:g} {kind.lower()} table read twice")
        target[module] = keyed
        counts["pages"] += 1
        counts["nominal_rows" if kind == "Nominal" else "inspection_rows"] += len(rows)

    result: list[SizeRow] = []
    report: list[str] = []
    for module in PART_2_MODULES:
        n_rows = nominal.get(module, {})
        i_rows = inspection.get(module, {})
        provenance = part_2_provenance(module)
        where = f"module {module:g}, tables {provenance.table}, pages {provenance.pages[0]}, " \
                f"{provenance.pages[1]}"
        for key in sorted(set(n_rows) | set(i_rows)):
            n, i_n = n_rows.get(key, []), i_rows.get(key, [])
            if len(n) == 1 and len(i_n) == 1:
                result.append(SizeRow(
                    provenance=provenance, module=module, reference_d=key[0], teeth=key[1],
                    pin_d_mm=float(i_n[0][INSPECTION_PIN_D]), m1_mm=float(i_n[0][INSPECTION_M1]),
                    form_d_max_mm=float(n[0][NOMINAL_FORM_D_MAX])))
                continue
            report.append(f"{where}: d_B {key[0]:g} z {key[1]} is printed {len(n)} times on "
                          f"the nominal page and {len(i_n)} on the inspection page; not joined")
    counts["joined"] = len(result)
    return ParseResult(tuple(result), tuple(report), counts)


def ensure_ignored(path: Path) -> None:
    """Refuse a path git does not ignore: a read must never land in a tracked path (D-01).

    Exit 128 is git's code for every fatal error, "not a repository" and a corrupt or
    unreadable repository alike with the same message. So 128 passes only when no `.git`
    exists above the path; otherwise git cannot say and the write is refused.
    """
    path = path.resolve()
    anchor = next(p for p in (path.parent, *path.parent.parents) if p.exists())
    code = subprocess.run(["git", "-C", str(anchor), "check-ignore", "-q", str(path)],
                          check=False, capture_output=True).returncode
    if code == 128 and not any((p / ".git").exists() for p in (anchor, *anchor.parents)):
        code = 0
    if code == 128:
        raise SystemExit(f"refusing to write {path}: git cannot say whether it is ignored (D-01)")
    if code != 0:
        raise SystemExit(f"refusing to write {path}: git does not ignore it (D-01)")
    path.parent.mkdir(parents=True, exist_ok=True)


def extract_pages(pdf: Path) -> list[tuple[int, str]]:
    done = subprocess.run(
        ["pdftotext", "-layout", "-f", str(FIRST_PAGE), "-l", str(LAST_PAGE), str(pdf), "-"],
        check=True, capture_output=True, text=True)
    texts = done.stdout.split("\f")
    if texts and not texts[-1].strip():
        texts.pop()
    return [(FIRST_PAGE + i, text) for i, text in enumerate(texts)]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="scripts.din5480_read1",
        description="Read 1 of DIN 5480-2: pages 8 to 39 through pdftotext into a sizes-only "
                    "table document.")
    parser.add_argument("pdf", type=Path, help="the licensed copy of DIN 5480-2")
    parser.add_argument("-o", "--output", type=Path, required=True,
                        help="where to write the read; git must ignore this path")
    args = parser.parse_args(argv)
    ensure_ignored(args.output)
    try:
        result = parse_pages(extract_pages(args.pdf))
    except ParseError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    tables = Tables(schema_version=1, sizes=result.rows, deviations=(),
                    classes=(), tolerances=(), columns=())
    try:
        parse(canonical(tables))
    except TablesError as exc:
        print(f"error: the loader refuses the read:\n{exc}", file=sys.stderr)
        return 1
    args.output.write_text(canonical(tables), encoding="utf-8")
    for name, count in result.counts.items():
        print(f"{name}: {count}")
    print(f"report_lines: {len(result.report)}")
    for line in result.report:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
