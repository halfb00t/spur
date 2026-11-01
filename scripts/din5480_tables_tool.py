"""`make tables.check|diff|join|assemble`: what the two reads of the DIN 5480 tables run through.

Two independent reads of the same pages are written in one schema (D-03, the models of
`spur.din5480_tables`) so they can be compared as parsed models, and the table file the
server loads exists only once every pair of reads agrees (D-08). The subcommands:

- `check FILE [--complete]`: the loader's own checks on one file, so a read is judged by the
  invariants the server applies. `--complete` also compares the counts with `EXPECTED_COUNTS`:
  completeness is a transcription-time check, not a load-time one, so the synthetic fixture
  stays small, and a real file missing a letter would read as "fit outside Table 7".
- `diff A B [--values]`: key every row, then print one location line per differing field and
  one per row only one read holds. A row printed twice inside one read is a difference too.
- `join OUT IN...`: concatenate the parts of one read (read 2 arrives in four parts).
- `assemble OUT --part2 A B --table7 C D`: write the table file only when both pairs diff to
  zero and the union passes `check --complete`.

Output is locations and counts, never a value, unless `diff --values` is passed. That output
belongs in the conversation of the person comparing, and must never go into a committed
file, a log or a SUMMARY: a refusal that carried the values would copy the licensed table
into the repository through the back door (34-RESEARCH Pitfall 3). Every command that writes
refuses an output path git does not ignore (D-01).
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from collections.abc import Hashable, Iterator
from pathlib import Path

from pydantic import ValidationError

from scripts.din5480_read1 import ensure_ignored
from spur.din5480_tables import (
    ClassRow,
    ColumnRow,
    DeviationRow,
    SizeRow,
    Tables,
    TablesError,
    ToleranceRow,
    canonical,
    parse,
)

# What a complete DIN 5480 table file holds (34-RESEARCH "Table structure", corrected below):
# 720 size rows over 16 modules, 18 shaft letters by 9 columns of A_s, 8 tolerance classes by
# the same 9 columns, 30 rows of Table 7's tolerance table and 21 module-group by d_B-range
# cells.
# The tolerance table has 30 rows, not the 24 the research counted: two independent reads of
# page 24 each counted 30, all 30 satisfy T_G = T_act + T_eff, and with 24 the classes 11 and
# 12 would point past the table (3 rows per class step, 1 row per column). Settled by the
# human at 34-14.
# The size rows are 720, not the 721 the research counted: Table 12's m=1.25 d_B 19 z 14
# nominal row is not printed on page 18 of our copy. Both reads left the key out, and the
# human chose to leave it out at 34-14 rather than build a row from one page.
EXPECTED_COUNTS = {
    "sizes": 720,
    "modules": 16,
    "letters": 18,
    "columns_per_row": 9,
    "classes": 8,
    "tolerance_rows": 30,
    "column_rows": 21,
}

KINDS = ("sizes", "deviations", "classes", "tolerances", "columns")
Row = SizeRow | DeviationRow | ClassRow | ToleranceRow | ColumnRow
_MISSING = object()


def _key(row: Row) -> Hashable:
    """The key the loader's `problems()` treats as unique for this kind of row."""
    if isinstance(row, SizeRow):
        return row.key
    if isinstance(row, DeviationRow):
        return row.letter
    if isinstance(row, ClassRow):
        return row.tolerance_class
    if isinstance(row, ToleranceRow):
        return row.row
    return (row.module_min_mm, row.module_max_mm, row.d_b_over_mm, row.d_b_upto_mm)


def _rows(t: Tables, kind: str) -> tuple[Row, ...]:
    rows: tuple[Row, ...] = getattr(t, kind)
    return rows


def _show(key: Hashable) -> str:
    return str(key)


def _fields(prefix: str, value: object) -> Iterator[tuple[str, object]]:
    """Every cell of a row as (name, value); a tuple is one cell per 1-based column."""
    if isinstance(value, dict):
        for name, inner in value.items():
            yield from _fields(f"{prefix}.{name}" if prefix else str(name), inner)
    elif isinstance(value, list):
        for i, inner in enumerate(value, start=1):
            yield from _fields(f"{prefix}[{i}]", inner)
    else:
        yield prefix, value


def _load(path: Path) -> Tables:
    """A read as a schema-valid model; an invariant it fails does not stop it being compared."""
    try:
        return Tables.model_validate_json(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise SystemExit(f"{path}: cannot be read ({exc.strerror})") from None
    except ValidationError as exc:
        lines = [f"{'.'.join(str(p) for p in e['loc']) or '(document)'}: {e['type']}"
                 for e in exc.errors(include_input=False, include_url=False,
                                     include_context=False)]
        raise SystemExit(f"{path}: not a table document:\n" + "\n".join(lines)) from None


def _where(row: Row) -> str:
    provenance = row.provenance
    pages = ", ".join(str(p) for p in provenance.pages)
    return f"part {provenance.part}, table {provenance.table}, page(s) {pages}"


def diff_lines(a: Tables, b: Tables, *, values: bool = False) -> list[str]:
    """One line per difference between two reads, in a fixed order, values only on request."""
    lines: list[str] = []
    for kind in KINDS:
        keyed: dict[str, dict[Hashable, Row]] = {"A": {}, "B": {}}
        for side, t in (("A", a), ("B", b)):
            for row in _rows(t, kind):
                key = _key(row)
                if key in keyed[side]:
                    lines.append(f"duplicate key in {side}: {kind} {_show(key)}, "
                                 f"{_where(row)}")
                else:
                    keyed[side][key] = row
        for key in sorted(set(keyed["A"]) | set(keyed["B"]), key=repr):
            in_a, in_b = keyed["A"].get(key), keyed["B"].get(key)
            if in_a is None or in_b is None:
                only = "B" if in_a is None else "A"
                holder = in_b if in_a is None else in_a
                assert holder is not None
                lines.append(f"only in {only}: {kind} {_show(key)}, {_where(holder)}")
                continue
            cells_a = dict(_fields("", in_a.model_dump(mode="json")))
            cells_b = dict(_fields("", in_b.model_dump(mode="json")))
            for name in sorted(set(cells_a) | set(cells_b)):
                if cells_a.get(name, _MISSING) != cells_b.get(name, _MISSING):
                    line = f"{kind} {_show(key)}, {name}: {_where(in_a)}"
                    if values:
                        line += f" [A={cells_a.get(name, '(absent)')}, " \
                                f"B={cells_b.get(name, '(absent)')}]"
                    lines.append(line)
    return lines


def shortfalls(t: Tables) -> list[str]:
    """Where `t` falls short of `EXPECTED_COUNTS`, counts only."""
    found = {
        "sizes": len(t.sizes),
        "modules": len({r.module for r in t.sizes}),
        "letters": len(t.deviations),
        "classes": len(t.classes),
        "tolerance_rows": len(t.tolerances),
        "column_rows": len(t.columns),
    }
    lines = [f"{name}: {count}, expected {EXPECTED_COUNTS[name]}"
             for name, count in found.items() if count != EXPECTED_COUNTS[name]]
    width = EXPECTED_COUNTS["columns_per_row"]
    for letter_row in t.deviations:
        if len(letter_row.a_s_um) != width:
            lines.append(f"columns_per_row: deviations {letter_row.letter} has "
                         f"{len(letter_row.a_s_um)}, expected {width}")
    for class_row in t.classes:
        if len(class_row.row_by_column) != width:
            lines.append(f"columns_per_row: classes {class_row.tolerance_class} has "
                         f"{len(class_row.row_by_column)}, expected {width}")
    return lines


def _check_file(path: Path) -> Tables | None:
    try:
        return parse(path.read_text(encoding="utf-8"))
    except OSError as exc:
        print(f"{path}: cannot be read ({exc.strerror})")
    except TablesError as exc:
        print(exc)
    return None


def cmd_check(args: argparse.Namespace) -> int:
    t = _check_file(args.file)
    if t is None:
        return 1
    if args.complete:
        short = shortfalls(t)
        if short:
            print("\n".join(short))
            return 1
    print("ok")
    return 0


def cmd_diff(args: argparse.Namespace) -> int:
    lines = diff_lines(_load(args.a), _load(args.b), values=args.values)
    print("\n".join([*lines, f"{len(lines)} differences"]))
    return 1 if lines else 0


def _join(parts: list[Tables]) -> Tables:
    merged: dict[str, dict[Hashable, Row]] = {kind: {} for kind in KINDS}
    for part in parts:
        for kind in KINDS:
            for row in _rows(part, kind):
                key = _key(row)
                if key in merged[kind]:
                    raise SystemExit(f"join: {kind} {_show(key)} is present twice")
                merged[kind][key] = row
    return Tables.model_validate({"schema_version": 1,
                                  **{kind: tuple(rows.values()) for kind, rows in merged.items()}})


def cmd_join(args: argparse.Namespace) -> int:
    joined = _join([_load(path) for path in args.inputs])
    ensure_ignored(args.out)
    args.out.write_text(canonical(joined), encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


def _wrong_shape(option: str, path: Path, read: Tables) -> str | None:
    """Why `read` may not be a `--part2` (sizes only) or `--table7` (no sizes) input."""
    if option == "--part2":
        extra = [kind for kind in KINDS[1:] if _rows(read, kind)]
        if extra or not read.sizes:
            return (f"refused: {option} input {path} must hold only sizes"
                    + (f" (found {', '.join(extra)})" if extra else " (found none)"))
    elif read.sizes:
        return f"refused: {option} input {path} must hold no sizes"
    return None


def cmd_assemble(args: argparse.Namespace) -> int:
    # D-08: two independent reads. One file given twice would be compared with itself.
    for option, paths in (("--part2", args.part2), ("--table7", args.table7)):
        if paths[0].resolve() == paths[1].resolve():
            print(f"refused: {option} names one file twice; give two independent reads")
            return 1
    part2 = [_load(path) for path in args.part2]
    table7 = [_load(path) for path in args.table7]
    for option, paths, reads in (("--part2", args.part2, part2), ("--table7", args.table7, table7)):
        for path, read in zip(paths, reads, strict=True):
            problem = _wrong_shape(option, path, read)
            if problem:
                print(problem)
                return 1
    differing = diff_lines(part2[0], part2[1]) + diff_lines(table7[0], table7[1])
    if differing:
        print("\n".join([*differing, "refused: the reads differ; nothing was written"]))
        return 1
    union = Tables(schema_version=1, sizes=part2[0].sizes, deviations=table7[0].deviations,
                   classes=table7[0].classes, tolerances=table7[0].tolerances,
                   columns=table7[0].columns)
    text = canonical(union)
    try:
        checked = parse(text)
    except TablesError as exc:
        print(f"refused: the union fails the loader's checks:\n{exc}")
        return 1
    short = shortfalls(checked)
    if short:
        print("\n".join([*short, "refused: the union is incomplete; nothing was written"]))
        return 1
    ensure_ignored(args.out)
    args.out.write_text(text, encoding="utf-8")
    data = text.encode("utf-8")
    print(f"wrote {args.out}: {len(data)} bytes, sha256 {hashlib.sha256(data).hexdigest()}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="scripts.din5480_tables_tool",
        description="Check, diff, join and assemble the two reads of the DIN 5480 tables.")
    commands = parser.add_subparsers(dest="command", required=True)

    check = commands.add_parser("check", help="the loader's checks on one file")
    check.add_argument("file", type=Path)
    check.add_argument("--complete", action="store_true",
                       help="also compare the counts with EXPECTED_COUNTS")
    check.set_defaults(run=cmd_check)

    diff = commands.add_parser("diff", help="locations of every disagreement between two reads")
    diff.add_argument("a", type=Path)
    diff.add_argument("b", type=Path)
    diff.add_argument("--values", action="store_true",
                      help="also print both values; never put this output in a committed file")
    diff.set_defaults(run=cmd_diff)

    join = commands.add_parser("join", help="concatenate the parts of one read")
    join.add_argument("out", type=Path)
    join.add_argument("inputs", type=Path, nargs="+")
    join.set_defaults(run=cmd_join)

    assemble = commands.add_parser("assemble", help="write the table file from agreeing reads")
    assemble.add_argument("out", type=Path)
    assemble.add_argument("--part2", type=Path, nargs=2, required=True, metavar=("A", "B"))
    assemble.add_argument("--table7", type=Path, nargs=2, required=True, metavar=("C", "D"))
    assemble.set_defaults(run=cmd_assemble)

    args = parser.parse_args(argv)
    code: int = args.run(args)
    return code


if __name__ == "__main__":
    sys.exit(main())
