"""The DIN 5480 table values, read once from a private file and checked on the way in.

The values are the human's licensed copy, never in the repository or the image (D-01), so
this module reads them from the JSON file named by SPUR_DIN5480_TABLES (D-02) and reports
plainly when it is absent, instead of falling back to a number that merely looks right (L08).
The file is read once per process and cached, the third piece of documented process state
beside the kernel lock and the build semaphore (CODING_VALUES "State", D-13): shaft_calc runs
on every keystroke and must never touch the disk.

The pydantic schema carries provenance on every row (D-03), `problems()` holds the
structural invariants that make a transcription checked rather than trusted (D-04), and the
lookups answer the maths with an exact key or nothing. This file imports only os, json,
pathlib, typing, pydantic and `.din5480` (the import contracts say why: no kernel, no solid,
no logger, no gear maths). Every refusal names locations (row kind, key, field, pages) and
never a value, because a refusal reaches logs and stderr (34-RESEARCH Pitfall 3).
"""

from __future__ import annotations

import json
import os
from collections import Counter
from collections.abc import Hashable, Iterable
from pathlib import Path
from typing import Annotated, Literal, NamedTuple

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from .din5480 import measure_over_pins, profile_shift, tooth_thickness

ENV_VAR = "SPUR_DIN5480_TABLES"
SCHEMA_VERSION = 1
# The document is about 300 KB (34-RESEARCH); the cap is hygiene against a wrong path naming a
# large file, to be measured against the real file at 34-14.
MAX_FILE_BYTES = 4 * 1024 * 1024
# A micrometre value of three extra digits is a millimetre value typed in micrometres
# (34-RESEARCH Pattern 6). 34-14 stops and asks if the real file exceeds it.
UM_LIMIT = 1000
# Half the printed third decimal plus float noise on the tie: 720 of 720 DIN 5480-2 rows
# agree inside it, the worst at 0.0005 (34-RESEARCH Pattern 6).
M1_TOLERANCE = 0.0005 + 1e-9
# The 16 modules of DIN 5480-2:2006, Tables 2 to 33 (a nominal and an inspection table each).
PART_2_MODULES = (0.5, 0.6, 0.75, 0.8, 1.0, 1.25, 1.5, 1.75,
                  2.0, 2.5, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0)

# The two characters a copy prints a minus as: refused in the raw text, so a sign cannot
# change under a parser that reads it as something else (34-RESEARCH Don't Hand-Roll).
_BAD_MINUS = {chr(0x2212): "U+2212", chr(0x2013): "U+2013"}

_Mm = Annotated[float, Field(allow_inf_nan=False)]
_ROW = ConfigDict(frozen=True, extra="forbid", strict=True)


class TablesError(ValueError):
    """A table file that cannot be used; `str()` is the reason, with locations and no values."""


class Provenance(BaseModel):
    """Where in the standard a row was read; not free text, see `part_2_provenance`."""

    model_config = _ROW
    part: Literal[1, 2]
    clause: str
    table: str
    pages: Annotated[tuple[int, ...], Field(min_length=1)]


class SizeRow(BaseModel):
    """One size of DIN 5480-2: the shaft's D_M and M1 and the nominal table's d_Ff1 max."""

    model_config = _ROW
    provenance: Provenance
    module: _Mm
    reference_d: _Mm
    teeth: Annotated[int, Field(ge=1)]
    pin_d_mm: _Mm
    m1_mm: _Mm
    form_d_max_mm: _Mm

    @property
    def key(self) -> tuple[float, float, int]:
        return (self.module, self.reference_d, self.teeth)


class DeviationRow(BaseModel):
    """One shaft letter of Table 7: the upper deviation A_s in micrometres, per column."""

    model_config = _ROW
    provenance: Provenance
    letter: Annotated[str, Field(pattern=r"^[a-z]$")]
    a_s_um: tuple[int, ...]


class ClassRow(BaseModel):
    """One tolerance class of Table 7: per column, the 1-based tolerance row it points to."""

    model_config = _ROW
    provenance: Provenance
    tolerance_class: Annotated[int, Field(ge=1, le=99)]
    row_by_column: tuple[int, ...]


class ToleranceRow(BaseModel):
    """One row of Table 7's tolerance table, in micrometres: T_G = T_act + T_eff."""

    model_config = _ROW
    provenance: Provenance
    row: Annotated[int, Field(ge=1)]
    t_g_um: int
    t_act_um: int
    t_eff_um: int


class ColumnRow(BaseModel):
    """Which Table 7 column a module group and a d_B range select.

    The header words are the field names (`d_b_over_mm` for "über", `d_b_upto_mm` for
    "bis"), so the edge convention lives in `Tables.column_for` alone.
    """

    model_config = _ROW
    provenance: Provenance
    module_min_mm: _Mm
    module_max_mm: _Mm
    d_b_over_mm: _Mm | None
    d_b_upto_mm: _Mm | None
    column: Annotated[int, Field(ge=1)]


class FitTolerance(NamedTuple):
    """The four Table 7 values of one fit at one size, in micrometres."""

    a_s_um: int
    t_g_um: int
    t_act_um: int
    t_eff_um: int


class Tables(BaseModel):
    """The whole document: DIN 5480-2's size rows and DIN 5480-1's Table 7."""

    model_config = _ROW
    schema_version: Literal[1]
    sizes: tuple[SizeRow, ...]
    deviations: tuple[DeviationRow, ...]
    classes: tuple[ClassRow, ...]
    tolerances: tuple[ToleranceRow, ...]
    columns: tuple[ColumnRow, ...]

    def size(self, module: float, reference_d: float, teeth: int) -> SizeRow | None:
        """The row with exactly this key. No nearest row, no rounding (L08)."""
        for row in self.sizes:
            if row.key == (module, reference_d, teeth):
                return row
        return None

    def column_for(self, module: float, reference_d: float) -> int | None:
        """Table 7's column for this module and d_B, or None unless exactly one row selects it.

        The edge convention (a d_B exactly on a range edge) is in `_columns_selecting`, confirmed
        there (34-RESEARCH A1, 34-15 checkpoint); this is the one place a read goes through it.
        """
        selecting = _columns_selecting(self, module, reference_d)
        return selecting[0].column if len(selecting) == 1 else None

    def fit(self, module: float, reference_d: float, fit: str) -> FitTolerance | None:
        """A_s, T_G, T_act and T_eff of a fit such as `8f` at this size, in micrometres.

        None when the letter or the class is not in the file, or the size has no column. `fit`
        already matched FIT_PATTERN, so it is one or two digits and a letter.
        """
        deviation = next((d for d in self.deviations if d.letter == fit[-1]), None)
        tolerance_class = next(
            (c for c in self.classes if c.tolerance_class == int(fit[:-1])), None)
        column = self.column_for(module, reference_d)
        if deviation is None or tolerance_class is None or column is None:
            return None
        row = next((r for r in self.tolerances
                    if r.row == tolerance_class.row_by_column[column - 1]), None)
        if row is None:
            return None
        return FitTolerance(deviation.a_s_um[column - 1], row.t_g_um, row.t_act_um, row.t_eff_um)

    @property
    def letters(self) -> tuple[str, ...]:
        """The shaft letters the file holds, never a constant in the repository."""
        return tuple(sorted(d.letter for d in self.deviations))

    @property
    def tolerance_classes(self) -> tuple[int, ...]:
        """The tolerance classes the file holds, never a constant in the repository."""
        return tuple(sorted(c.tolerance_class for c in self.classes))


def _column_key(row: ColumnRow) -> tuple[float, float, float | None, float | None]:
    return (row.module_min_mm, row.module_max_mm, row.d_b_over_mm, row.d_b_upto_mm)


TABLE_7_PROVENANCE = Provenance(part=1, clause="10.9", table="7", pages=(24,))


def part_2_provenance(module: float) -> Provenance:
    """The clause, table pair and pages of a module in DIN 5480-2:2006.

    Section 4 is m 0.5 and section 19 is m 10; each module has a nominal and an inspection
    table, Tables 2 and 3 for the first, on pages 8 and 9 (34-RESEARCH "Table structure").
    """
    i = PART_2_MODULES.index(module)
    return Provenance(part=2, clause=str(4 + i), table=f"{2 + 2 * i} and {3 + 2 * i}",
                      pages=(8 + 2 * i, 9 + 2 * i))


def _duplicates(keys: Iterable[Hashable]) -> list[Hashable]:
    return [k for k, n in Counter(keys).items() if n > 1]


def _pages(provenance: Provenance) -> str:
    return ", ".join(str(p) for p in provenance.pages)


def _columns_selecting(t: Tables, module: float, reference_d: float) -> list[ColumnRow]:
    """The column rows whose module group and d_B range hold this size.

    "über x bis y" is read as x < d_B <= y, the DIN ISO 286 reading. The human confirmed it
    against page 24 of the copy at the 34-15 checkpoint, 2026-10-31 (34-RESEARCH A1), and
    tests/din5480_real_tables_check.py pins it on both sides of every printed edge of the
    real file. The default shaft sits on the edge 25, so the two comparisons below decide
    its column.
    """
    return [c for c in t.columns
            if c.module_min_mm <= module <= c.module_max_mm
            and (c.d_b_over_mm is None or reference_d > c.d_b_over_mm)
            and (c.d_b_upto_mm is None or reference_d <= c.d_b_upto_mm)]


def problems(t: Tables) -> list[str]:
    """Every structural fault in `t`, one sentence each, naming locations and never values.

    Each rule was seen failing once against a deliberately broken row (34-02 red logs).
    """
    found: list[str] = []
    for size in t.sizes:
        at = f"sizes {size.key} (pages {_pages(size.provenance)})"
        if size.module not in PART_2_MODULES:
            found.append(f"{at}: module is not one of DIN 5480-2's sixteen")
            continue
        if size.provenance != part_2_provenance(size.module):
            found.append(f"{at}: provenance is not the layout's for this module")
        if not 0 < size.pin_d_mm < size.reference_d:
            found.append(f"{at}: pin_d_mm is not between 0 and d_B")
        if not 0 < size.form_d_max_mm < size.reference_d:
            found.append(f"{at}: form_d_max_mm is not between 0 and d_B")
        if size.m1_mm <= 0:
            found.append(f"{at}: m1_mm is not positive")
        # The printed M1 against the formula at the printed pin and the nominal thickness: a
        # last-digit typo in D_M, d_B, z or M1 moves the difference to 0.0005..0.0015 (720 of
        # 720 rows agree inside M1_TOLERANCE). d_Ff1 max is not covered; only the two reads
        # protect it.
        x = profile_shift(size.reference_d, size.module, size.teeth)
        reading = measure_over_pins(size.module, size.teeth,
                                    tooth_thickness(size.module, x * size.module), size.pin_d_mm)
        if reading is None:
            found.append(f"{at}: M1 cannot be computed at the printed pin")
        elif abs(reading[0] - size.m1_mm) > M1_TOLERANCE:
            found.append(f"{at}: M1 disagrees with the formula at the printed pin")
        if t.columns:
            n_selecting = len(_columns_selecting(t, size.module, size.reference_d))
            if n_selecting != 1:
                found.append(f"{at}: selected by {n_selecting} column rows, not one")
    for kind, rows in (("deviations", t.deviations), ("classes", t.classes),
                       ("tolerances", t.tolerances), ("columns", t.columns)):
        found += [f"{kind}: a row's provenance is not Part 1 Table 7's"
                  for row in rows if row.provenance != TABLE_7_PROVENANCE]
    for tol in t.tolerances:
        at = f"tolerances {tol.row} (page 24)"
        if tol.t_g_um != tol.t_act_um + tol.t_eff_um:
            found.append(f"{at}: T_G is not T_act + T_eff")
        # With the sum above this also gives T_G >= T_eff >= 0; a sign slip that keeps the sum
        # would print s_max above s_vmax (L08).
        if tol.t_act_um < 0 or tol.t_eff_um < 0:
            found.append(f"{at}: T_act or T_eff is negative")
        if any(abs(v) > UM_LIMIT for v in (tol.t_g_um, tol.t_act_um, tol.t_eff_um)):
            found.append(f"{at}: a micrometre field is beyond {UM_LIMIT}")
    for dev in t.deviations:
        if any(abs(v) > UM_LIMIT for v in dev.a_s_um):
            found.append(f"deviations {dev.letter!r} (page 24): a micrometre field is beyond "
                         f"{UM_LIMIT}")
    # One column count for every Table 7 row; the first deviation row (else the first class
    # row) sets it.
    widths = [len(r.a_s_um) for r in t.deviations] + [len(r.row_by_column) for r in t.classes]
    n = widths[0] if widths else None
    for dev in t.deviations:
        if len(dev.a_s_um) != n:
            found.append(f"deviations {dev.letter!r} (page 24): column count differs from the "
                         f"first row's")
    rows_known = {r.row for r in t.tolerances}
    for cls in t.classes:
        at = f"classes {cls.tolerance_class} (page 24)"
        if len(cls.row_by_column) != n:
            found.append(f"{at}: column count differs from the first row's")
        if any(v not in rows_known for v in cls.row_by_column):
            found.append(f"{at}: row_by_column names a tolerance row that does not exist")
    for col in t.columns:
        at = f"columns {_column_key(col)} (page 24)"
        if col.module_min_mm > col.module_max_mm or not {
                col.module_min_mm, col.module_max_mm} <= set(PART_2_MODULES):
            found.append(f"{at}: module bounds are reversed or not DIN 5480-2 modules")
        if col.d_b_over_mm is not None and col.d_b_upto_mm is not None \
                and col.d_b_over_mm >= col.d_b_upto_mm:
            found.append(f"{at}: d_b_over_mm is not below d_b_upto_mm")
        if n is not None and col.column > n:
            found.append(f"{at}: column is outside 1..{n}")
    for kind, keys in (
        ("sizes", [r.key for r in t.sizes]),
        ("deviations", [r.letter for r in t.deviations]),
        ("classes", [r.tolerance_class for r in t.classes]),
        ("tolerances", [r.row for r in t.tolerances]),
        ("columns", [_column_key(r) for r in t.columns]),
    ):
        found += [f"{kind}: key {k} appears more than once" for k in _duplicates(keys)]
    return found


def parse(text: str) -> Tables:
    """The document in `text`, or a TablesError listing every fault by location."""
    for number, line in enumerate(text.splitlines(), start=1):
        for char, name in _BAD_MINUS.items():
            if char in line:
                raise TablesError(f"line {number}: {name} where an ASCII minus is required")
    try:
        tables = Tables.model_validate_json(text)
    except ValidationError as exc:
        # `errors()` without the input: pydantic's own message carries `input_value`, which
        # is a transcribed value (Pitfall 3).
        lines = [f"{'.'.join(str(p) for p in e['loc']) or '(document)'}: {e['type']}"
                 for e in exc.errors(include_input=False, include_url=False, include_context=False)]
        raise TablesError("\n".join(lines)) from None
    found = problems(tables)
    if found:
        raise TablesError("\n".join(found))
    return tables


def load_file(path: Path) -> Tables:
    """The tables in the file at `path`; every refusal starts with the path."""
    try:
        size = path.stat().st_size if path.is_file() else None
    except OSError as exc:
        raise TablesError(f"{path}: cannot be read ({exc.strerror})") from None
    if size is None:
        reason = "is not a regular file" if path.exists() else "does not exist"
        raise TablesError(f"{path}: {reason}")
    if size > MAX_FILE_BYTES:
        raise TablesError(f"{path}: is larger than the {MAX_FILE_BYTES} byte cap")
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise TablesError(f"{path}: cannot be read ({exc.strerror})") from None
    if not raw:
        raise TablesError(f"{path}: is empty")
    if len(raw) > MAX_FILE_BYTES:
        raise TablesError(f"{path}: is larger than the {MAX_FILE_BYTES} byte cap")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        raise TablesError(f"{path}: is not UTF-8") from None
    try:
        return parse(text)
    except TablesError as exc:
        raise TablesError(f"{path}: {exc}") from None


_UNSET = object()
# Written once per process (D-13): by the first `active()` call, or by `install` for a build
# worker. A refusal is cached too, so a broken file costs one read, not one per keystroke.
_state: Tables | TablesError | object | None = _UNSET


def active() -> Tables | None:
    """The process's tables: None when no file is named, a TablesError when it is unusable."""
    global _state
    if _state is _UNSET:
        raw = os.environ.get(ENV_VAR) or ""
        if not raw:
            _state = None
        else:
            try:
                _state = load_file(Path(raw))
            except TablesError as exc:
                _state = TablesError(f"{ENV_VAR}={exc}")
    if isinstance(_state, TablesError):
        raise TablesError(str(_state)) from None
    if isinstance(_state, Tables):
        return _state
    return None


def install(t: Tables | None) -> None:
    """Set the process's tables without reading the environment (a build worker, a test)."""
    global _state
    _state = t


def reset() -> None:
    """Forget the cached state so the next `active()` reads the environment again (tests)."""
    global _state
    _state = _UNSET


def canonical(t: Tables) -> str:
    """The document as sorted JSON: two documents that differ only in row order give the
    same bytes, which is what lets two independent reads diff to zero (D-03)."""
    document = t.model_dump(mode="json")
    document["sizes"] = [r.model_dump(mode="json") for r in sorted(t.sizes, key=lambda r: r.key)]
    document["deviations"] = [r.model_dump(mode="json")
                              for r in sorted(t.deviations, key=lambda r: r.letter)]
    document["classes"] = [r.model_dump(mode="json")
                           for r in sorted(t.classes, key=lambda r: r.tolerance_class)]
    document["tolerances"] = [r.model_dump(mode="json")
                              for r in sorted(t.tolerances, key=lambda r: r.row)]
    document["columns"] = [
        r.model_dump(mode="json") for r in sorted(
            t.columns, key=lambda r: (r.module_min_mm, r.module_max_mm,
                                      float("-inf") if r.d_b_over_mm is None else r.d_b_over_mm,
                                      float("inf") if r.d_b_upto_mm is None else r.d_b_upto_mm))]
    return json.dumps(document, sort_keys=True, indent=1, ensure_ascii=True) + "\n"
