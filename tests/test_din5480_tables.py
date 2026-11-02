"""The private DIN 5480 table loader, against the synthetic document in
din5480_tables_fixture.py (D-01: no value of the standard is in this repository).

D-02 the variable names the file, D-04 a broken file is an error with locations and never a
quiet null, D-13 the file is read once per process (the keystroke path never touches disk).
"""

from __future__ import annotations

import errno
import io
import json
import math
import shutil
import subprocess
import sys
from collections.abc import Callable
from contextlib import AbstractContextManager, nullcontext
from pathlib import Path
from types import ModuleType
from typing import IO, Literal

import din5480_tables_fixture as fixture
import pytest
from pydantic import ValidationError

from spur import din5480, din5480_tables
from spur.din5480_tables import (
    ENV_VAR,
    M1_TOLERANCE,
    MAX_FILE_BYTES,
    UM_LIMIT,
    FitTolerance,
    Tables,
    TablesError,
)

Document = dict[str, list[dict[str, object]]]


def test_with_the_variable_unset_there_are_no_tables() -> None:
    assert din5480_tables.active() is None


def test_an_empty_variable_is_no_file(monkeypatch: pytest.MonkeyPatch) -> None:
    """The `int_env` reading of an empty variable: `SPUR_X=` in a compose file is unset."""
    monkeypatch.setenv(ENV_VAR, "")
    assert din5480_tables.active() is None


def test_a_named_file_loads_and_answers_an_exact_key_size_lookup(
        monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv(ENV_VAR, str(fixture.write(tmp_path / "t.json")))
    tables = din5480_tables.active()
    assert tables is not None
    assert len(tables.sizes) == 5
    row = tables.size(1.25, 25.0, 18)
    assert row is not None
    assert row.pin_d_mm == 2.75
    found = tables.size(1.25, 25, 18)
    assert found is not None
    assert found.pin_d_mm == 2.75
    # L08: an exact key or nothing, never the nearest row.
    assert tables.size(1.25, 25.000001, 18) is None


def test_the_file_is_read_once_per_process(
        monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """D-13: shaft_calc runs on every keystroke, so a later call must not touch the disk."""
    path = fixture.write(tmp_path / "t.json")
    monkeypatch.setenv(ENV_VAR, str(path))
    first = din5480_tables.active()
    path.unlink()
    assert din5480_tables.active() is first
    din5480_tables.reset()
    with pytest.raises(TablesError, match=r"t\.json"):
        din5480_tables.active()


def test_a_broken_file_is_an_error_on_every_call_and_is_read_once(
        monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """D-04: the failure is cached too, so a library caller pays one read, not one per
    keystroke, and never sees a quiet None in its place."""
    path = tmp_path / "t.json"
    path.write_text("{", encoding="utf-8")
    monkeypatch.setenv(ENV_VAR, str(path))
    with pytest.raises(TablesError) as first:
        din5480_tables.active()
    fixture.write(path)
    with pytest.raises(TablesError) as second:
        din5480_tables.active()
    assert str(first.value) == str(second.value)
    assert str(first.value).startswith(f"{ENV_VAR}={path}")


def test_install_sets_the_state_without_reading_the_environment(
        monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """A build worker gets the parent's tables through `install` (34-05), whatever its own
    environment says."""
    monkeypatch.setenv(ENV_VAR, str(tmp_path / "missing.json"))
    tables = fixture.build()
    din5480_tables.install(tables)
    assert din5480_tables.active() is tables


# --- Task 2: every structural invariant refuses a deliberately broken row ---------------
# Each case edits the fixture's document (or its raw text) and names what the refusal must
# say. The refusals name locations and types, so the needles are keys and field names.


def _doc(edit: Callable[[Document], None]) -> Callable[[str], str]:
    def apply(text: str) -> str:
        document: Document = json.loads(text)
        edit(document)
        return json.dumps(document, indent=1)
    return apply


def _raw(old: str, new: str) -> Callable[[str], str]:
    def apply(text: str) -> str:
        assert old in text, "the raw edit found nothing to break"
        return text.replace(old, new, 1)
    return apply


def _set(kind: str, index: int, field: str, value: object) -> Callable[[str], str]:
    def edit(document: Document) -> None:
        document[kind][index][field] = value
    return _doc(edit)


def _element(kind: str, index: int, field: str, at: int, value: object) -> Callable[[str], str]:
    def edit(document: Document) -> None:
        values = document[kind][index][field]
        assert isinstance(values, list)
        values[at] = value
    return _doc(edit)


def _append(kind: str, index: int, field: str, value: object) -> Callable[[str], str]:
    def edit(document: Document) -> None:
        values = document[kind][index][field]
        assert isinstance(values, list)
        values.append(value)
    return _doc(edit)


def _duplicate(kind: str) -> Callable[[str], str]:
    return _doc(lambda d: d[kind].append(dict(d[kind][0])))


def _default_row(document: Document) -> dict[str, object]:
    return next(r for r in document["sizes"] if r["teeth"] == 18)


def _drop_default_column(document: Document) -> None:
    document["columns"] = [c for c in document["columns"]
                           if (c["module_min_mm"], c["d_b_upto_mm"]) != (0.5, 25.0)]


def _overlapping_column(document: Document) -> None:
    document["columns"].append({**document["columns"][0], "d_b_over_mm": 20.0,
                                "d_b_upto_mm": 30.0, "column": 2})


def _column_beyond_the_last(document: Document) -> None:
    document["columns"][0]["column"] = 4


def _pin_in_micrometres(document: Document) -> None:
    row = _default_row(document)
    assert isinstance(row["pin_d_mm"], float)
    row["pin_d_mm"] = row["pin_d_mm"] * 1000


def _form_at_d_b(document: Document) -> None:
    row = _default_row(document)
    row["form_d_max_mm"] = row["reference_d"]


def _m1_plus(amount: float) -> Callable[[Document], None]:
    def edit(document: Document) -> None:
        row = _default_row(document)
        assert isinstance(row["m1_mm"], float)
        row["m1_mm"] = row["m1_mm"] + amount
    return edit


def _pin_plus(document: Document) -> None:
    row = _default_row(document)
    assert isinstance(row["pin_d_mm"], float)
    row["pin_d_mm"] = row["pin_d_mm"] + 0.01


def _last_column_d_b(document: Document) -> None:
    document["columns"][-1].update(d_b_over_mm=60.0, d_b_upto_mm=50.0)


def _last_column_reversed(document: Document) -> None:
    document["columns"][-1].update(module_min_mm=10.0, module_max_mm=5.0)


def _clause_changed(document: Document) -> None:
    provenance = document["sizes"][0]["provenance"]
    assert isinstance(provenance, dict)
    provenance["clause"] = "section 9"


MINUS_SIGN = chr(0x2212)
EN_DASH = chr(0x2013)

BROKEN: list[tuple[str, Callable[[str], str], str]] = [
    ("t_g sum off by one",
     _doc(lambda d: d["tolerances"][0].update(t_g_um=int(str(d["tolerances"][0]["t_g_um"])) + 1)),
     "T_G is not T_act + T_eff"),
    ("tolerance row negated, sum intact",
     _doc(lambda d: d["tolerances"][0].update(
         {k: -int(str(d["tolerances"][0][k])) for k in ("t_g_um", "t_act_um", "t_eff_um")})),
     "T_act or T_eff is negative"),
    ("negative T_act, sum intact",
     _doc(lambda d: d["tolerances"][0].update(
         t_act_um=-5, t_eff_um=int(str(d["tolerances"][0]["t_g_um"])) + 5)),
     "T_act or T_eff is negative"),
    ("deviation over the micrometre limit", _element("deviations", 0, "a_s_um", 0, UM_LIMIT + 1),
     "a micrometre field is beyond"),
    ("pin typed in micrometres", _doc(_pin_in_micrometres), "pin_d_mm is not between"),
    ("form diameter at d_B", _doc(_form_at_d_b), "form_d_max_mm is not between"),
    ("minus sign U+2212", _raw("-21", MINUS_SIGN + "21"), "U+2212"),
    ("en dash U+2013", _raw("-21", EN_DASH + "21"), "U+2013"),
    ("NaN", _set("sizes", 0, "pin_d_mm", float("nan")), "sizes.0.pin_d_mm"),
    ("infinity as 1e999", _raw('"pin_d_mm": 2.75', '"pin_d_mm": 1e999'), "sizes.0.pin_d_mm"),
    ("a string for an int", _element("deviations", 0, "a_s_um", 0, "28"), "int_type"),
    ("a float for an int", _element("deviations", 0, "a_s_um", 0, 28.0), "int_type"),
    ("a millimetre value for an int", _element("deviations", 0, "a_s_um", 0, 0.028), "int_type"),
    ("an unknown key", _doc(lambda d: d["sizes"][0].update(extra=1)), "extra_forbidden"),
    ("duplicate size", _duplicate("sizes"), "sizes: key"),
    ("duplicate deviation", _duplicate("deviations"), "deviations: key"),
    ("duplicate class", _duplicate("classes"), "classes: key"),
    ("duplicate tolerance row", _duplicate("tolerances"), "tolerances: key"),
    ("duplicate column row", _duplicate("columns"), "columns: key"),
    ("clause changed", _doc(_clause_changed), "provenance is not the layout's"),
    ("column index beyond the last", _doc(_column_beyond_the_last), "column is outside 1..3"),
    ("row_by_column naming no row", _element("classes", 0, "row_by_column", 0, 99),
     "names a tolerance row that does not exist"),
    ("default size has no column", _doc(_drop_default_column), "selected by 0 column rows"),
    ("two columns select the default size", _doc(_overlapping_column),
     "selected by 2 column rows"),
    ("M1 plus a thousandth", _doc(_m1_plus(0.001)), "M1 disagrees with the formula"),
    ("pin plus a hundredth", _doc(_pin_plus), "M1 disagrees with the formula"),
    # 34.1: one case per refusal line the gate did not reach (D-11, the loader-refusals debt item).
    ("module not one of the sixteen", _set("sizes", 0, "module", 1.3),
     "module is not one of DIN 5480-2's sixteen"),
    # The last column row is m 5 to 10, which no fixture size selects, so each column edit
    # below trips only its own rule.
    ("m1 not positive", _set("sizes", 0, "m1_mm", 0.0), "m1_mm is not positive"),
    ("a deviation row one column wider", _append("deviations", 1, "a_s_um", 0),
     "deviations 'h' (page 24): column count differs"),
    ("a class row one column wider", _append("classes", 1, "row_by_column", 2),
     "classes 8 (page 24): column count differs"),
    ("column module bounds reversed", _doc(_last_column_reversed),
     "module bounds are reversed or not DIN 5480-2 modules"),
    ("column module bound not a DIN 5480-2 module", _set("columns", -1, "module_max_mm", 12.0),
     "module bounds are reversed or not DIN 5480-2 modules"),
    ("column d_B range reversed", _doc(_last_column_d_b),
     "d_b_over_mm is not below d_b_upto_mm"),
]


@pytest.mark.parametrize(("edit", "needle"), [(e, n) for _, e, n in BROKEN],
                         ids=[i for i, _, _ in BROKEN])
def test_a_broken_row_refuses_to_load(edit: Callable[[str], str], needle: str) -> None:
    """D-04, REQ-tables-transcribed-twice: a transcription that breaks any rule cannot load."""
    with pytest.raises(TablesError) as refused:
        din5480_tables.parse(edit(fixture.text()))
    assert needle in str(refused.value)


@pytest.mark.parametrize(("make", "needle"), [
    (lambda path: path.write_bytes(b""), "is empty"),
    (lambda path: path.mkdir(), "is not a regular file"),
    (lambda path: path.write_bytes(b"\xff\xfe\x00{"), "is not UTF-8"),
    (lambda path: path.write_text("not json", encoding="utf-8"), "json_invalid"),
], ids=["zero bytes", "a directory", "not UTF-8", "not JSON"])
def test_an_unusable_file_refuses_naming_its_path(
        make: Callable[[Path], object], needle: str, tmp_path: Path) -> None:
    path = tmp_path / "t.json"
    make(path)
    with pytest.raises(TablesError) as refused:
        din5480_tables.load_file(path)
    assert str(refused.value).startswith(str(path))
    assert needle in str(refused.value)


def test_a_missing_file_refuses_naming_its_path(tmp_path: Path) -> None:
    with pytest.raises(TablesError, match="does not exist"):
        din5480_tables.load_file(tmp_path / "absent.json")


def test_the_file_size_cap_is_exact(tmp_path: Path) -> None:
    body = fixture.text().encode("ascii")
    path = tmp_path / "t.json"
    path.write_bytes(body + b" " * (MAX_FILE_BYTES - len(body)))
    assert din5480_tables.load_file(path).size(1.25, 25.0, 18) is not None
    path.write_bytes(body + b" " * (MAX_FILE_BYTES - len(body) + 1))
    with pytest.raises(TablesError, match=str(MAX_FILE_BYTES)):
        din5480_tables.load_file(path)


def test_a_path_the_system_cannot_stat_refuses_naming_it(tmp_path: Path) -> None:
    """A name over NAME_MAX is an OSError that `Path.is_file` re-raises on CPython 3.12 (L23),
    so the `stat` handler answers, not the "does not exist" branch."""
    path = tmp_path / ("x" * 300 + ".json")
    with pytest.raises(TablesError) as refused:
        din5480_tables.load_file(path)
    assert str(refused.value).startswith(str(path))
    assert "cannot be read (" in str(refused.value)


def _open_answering(monkeypatch: pytest.MonkeyPatch, path: Path,
                    answer: Callable[[], AbstractContextManager[IO[bytes]]]) -> None:
    """`Path.open("rb")`, the loader's one call, answers `answer()` for `path` only and is the
    original otherwise. Write the file before calling this: CPython 3.12's `Path.write_bytes`
    opens through `Path.open`."""
    original = Path.open

    def open_(self: Path, mode: Literal["rb"]) -> AbstractContextManager[IO[bytes]]:
        return answer() if self == path else original(self, mode)
    monkeypatch.setattr(Path, "open", open_)


def test_a_file_over_the_cap_is_refused_at_the_stat_before_it_is_opened(
        monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Tells the stat-time check from the read-time one, which prints the same sentence
    (D-10): the open is faulted, so only the stat can have refused."""
    path = tmp_path / "t.json"
    path.write_bytes(b" " * (MAX_FILE_BYTES + 1))

    def opened() -> AbstractContextManager[IO[bytes]]:
        raise AssertionError("opened past the stat-time cap")
    _open_answering(monkeypatch, path, opened)
    with pytest.raises(TablesError) as refused:
        din5480_tables.load_file(path)
    assert str(refused.value) == f"{path}: is larger than the {MAX_FILE_BYTES} byte cap"


def test_a_read_error_after_the_stat_refuses_naming_the_path(
        monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """The fault is injected at the open: a mode-000 file still opens as root, and
    `make test-image` runs as root. A file that is readable at the stat and not at the open
    is a race."""
    path = fixture.write(tmp_path / "t.json")

    def refuse() -> AbstractContextManager[IO[bytes]]:
        raise PermissionError(errno.EACCES, "Permission denied")
    _open_answering(monkeypatch, path, refuse)
    with pytest.raises(TablesError) as refused:
        din5480_tables.load_file(path)
    assert str(refused.value) == f"{path}: cannot be read (Permission denied)"


def test_a_file_that_grew_past_the_cap_after_the_stat_refuses(
        monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """The read-time check's test; the stat-time check's is the one before the read-error
    test. A file that grows between the stat and the read is a race, so the open is injected
    with a file twice the cap, and the loader must have taken exactly one byte past the cap
    from it, not the whole of it (D-10)."""
    path = fixture.write(tmp_path / "t.json")
    grown = io.BytesIO(b" " * (2 * (MAX_FILE_BYTES + 1)))
    _open_answering(monkeypatch, path, lambda: nullcontext(grown))
    with pytest.raises(TablesError) as refused:
        din5480_tables.load_file(path)
    assert str(refused.value) == f"{path}: is larger than the {MAX_FILE_BYTES} byte cap"
    assert grown.tell() == MAX_FILE_BYTES + 1


def test_fit_is_none_when_an_unchecked_document_names_a_missing_tolerance_row() -> None:
    """A caller of `install` can hold a document that skipped `problems()`. The lookup then
    answers None, not an IndexError or a near row (L08). `parse` refuses such a document
    (`[row_by_column naming no row]`)."""
    tables = Tables.model_validate_json(
        _element("classes", 1, "row_by_column", 0, 99)(fixture.text()))
    assert tables.fit(1.25, 25.0, "8f") is None


def _w26_m1_plus(amount: float) -> Callable[[str], str]:
    """The W 26x1.25x19 row's M1 set to the formula's value plus `amount`."""
    def edit(document: Document) -> None:
        row = next(r for r in document["sizes"] if r["teeth"] == 19)
        x = din5480.profile_shift(26.0, 1.25, 19)
        s = din5480.tooth_thickness(1.25, x * 1.25)
        reading = din5480.measure_over_pins(1.25, 19, s, 2.75)
        assert reading is not None
        row["m1_mm"] = reading[0] + amount
    return _doc(edit)


def test_the_m1_identity_accepts_exactly_half_a_printed_digit() -> None:
    assert M1_TOLERANCE == 0.0005 + 1e-9
    din5480_tables.parse(_w26_m1_plus(0.0005)(fixture.text()))


def test_the_m1_identity_refuses_a_hair_beyond_half_a_printed_digit() -> None:
    with pytest.raises(TablesError, match="M1 disagrees"):
        din5480_tables.parse(_w26_m1_plus(0.0005 + 2e-9)(fixture.text()))


def test_a_document_of_empty_row_tuples_loads() -> None:
    """Completeness is a transcription-time check (34-03), not a load-time one."""
    document = json.loads(fixture.text())
    for kind in ("sizes", "deviations", "classes", "tolerances", "columns"):
        document[kind] = []
    assert din5480_tables.parse(json.dumps(document)).sizes == ()


def test_canonical_ignores_row_order() -> None:
    document = json.loads(fixture.text())
    for kind in ("sizes", "deviations", "classes", "tolerances", "columns"):
        document[kind].reverse()
    reordered = din5480_tables.parse(json.dumps(document))
    assert din5480_tables.canonical(reordered) == fixture.text()


def test_a_refusal_names_locations_never_values() -> None:
    """Pitfall 3: a refusal reaches logs, so it holds the dotted location and the error
    type and not pydantic's `input_value`, and not a value of a row that failed a rule."""
    typed = _element("deviations", 0, "a_s_um", 0, 0.028)(fixture.text())
    with pytest.raises(TablesError) as schema:
        din5480_tables.parse(typed)
    assert "deviations.0.a_s_um.0" in str(schema.value)
    assert "int_type" in str(schema.value)
    assert "input_value" not in str(schema.value)
    assert "0.028" not in str(schema.value)
    with pytest.raises(TablesError) as rule:
        din5480_tables.parse(_doc(_pin_in_micrometres)(fixture.text()))
    assert "2750" not in str(rule.value)


# --- Task 3: the Table 7 lookup, the guards, the with_tables fixture ---------------------


def test_the_default_shaft_reads_one_table_7_column() -> None:
    """Class 8 in column 1 points at tolerance row 2; letter f in column 1 is A_s -21."""
    assert fixture.build().fit(1.25, 25.0, "8f") == FitTolerance(-21, 36, 21, 15)


def test_edge_a_d_b_on_a_range_edge_falls_in_the_range_it_closes() -> None:
    """"über x bis y" is x < d_B <= y (34-RESEARCH A1, confirmed by the human against page 24
    at the 34-15 checkpoint, 2026-10-31): the default shaft's d_B 25 is the upper edge of the
    first range, one float step above is the next one's."""
    tables = fixture.build()
    assert tables.column_for(1.25, 25.0) == 1
    assert tables.column_for(1.25, math.nextafter(25.0, math.inf)) == 2
    assert tables.column_for(1.25, math.nextafter(25.0, -math.inf)) == 1
    assert tables.column_for(1.25, 24.999) == 1
    assert tables.column_for(2.0, 100.0) == 2
    assert tables.column_for(2.0, math.nextafter(100.0, math.inf)) == 3


def test_edge_the_fit_changes_with_the_column_across_the_edge() -> None:
    tables = fixture.build()
    assert tables.fit(1.25, 25.0, "8f") == FitTolerance(-21, 36, 21, 15)
    assert tables.fit(1.25, math.nextafter(25.0, math.inf), "8f") == FitTolerance(-17, 45, 27, 18)


def test_a_size_in_no_column_has_no_fit() -> None:
    tables = fixture.build()
    assert tables.column_for(0.6, 25.0) == 1
    assert tables.column_for(1.6, 25.0) is None
    assert tables.fit(1.6, 25.0, "8f") is None


def test_column_for_a_module_group_reads_the_third_column() -> None:
    assert fixture.build().column_for(3.0, 120.0) == 3


@pytest.mark.parametrize("fit", ["3z", "13f", "8q"])
def test_a_fit_the_file_does_not_hold_is_none(fit: str) -> None:
    """D-14: the letter or the class missing from the file is a None, never a near fit."""
    assert fixture.build().fit(1.25, 25.0, fit) is None


def test_the_letters_and_classes_come_from_the_file() -> None:
    tables = fixture.build()
    assert tables.letters == ("f", "h", "k")
    assert tables.tolerance_classes == (7, 8, 9)
    document = json.loads(fixture.text())
    for row, letter in zip(document["deviations"], "abc", strict=True):
        row["letter"] = letter
    other = din5480_tables.parse(json.dumps(document))
    assert other.letters == ("a", "b", "c")


REPO = Path(__file__).resolve().parents[1]
# The image holds neither git nor the ignore files (make test-image mounts src and tests
# only), so the repository guards cannot run there.
needs_checkout = pytest.mark.skipif(
    shutil.which("git") is None or not (REPO / ".git").exists(),
    reason="not a git checkout")


@needs_checkout
def test_the_private_directory_is_ignored_by_git_and_by_docker() -> None:
    """Pitfall 9: git itself says the paths are ignored (a name grep would match
    din5480_tables.py), and the Docker build context never receives the directory."""
    for path in ("private/din5480-tables.json", "private/reads/x.json"):
        ignored = subprocess.run(["git", "check-ignore", "-q", path], cwd=REPO, check=False)
        assert ignored.returncode == 0, path
    assert "private" in (REPO / ".dockerignore").read_text(encoding="utf-8").splitlines()


@needs_checkout
def test_no_tracked_json_file_is_a_table_file() -> None:
    """Pitfall 9: a renamed copy of the table file anywhere in the tree would validate."""
    listing = subprocess.run(["git", "ls-files", "-z", "--", "*.json"], cwd=REPO,
                             check=True, capture_output=True).stdout
    paths = [p for p in listing.decode("utf-8").split("\0") if p and (REPO / p).is_file()]
    assert paths, "git lists no tracked JSON, so this guard would pass on nothing"
    for path in paths:
        with pytest.raises(ValidationError):
            Tables.model_validate_json((REPO / path).read_bytes())


class _CacheProbe:
    def __init__(self) -> None:
        self.cleared = 0

    def cache_clear(self) -> None:
        self.cleared += 1


class _FakeBlobCache:
    def __init__(self, budget: int) -> None:
        self.budget = budget


@pytest.fixture
def imported_kernel_modules(monkeypatch: pytest.MonkeyPatch) -> tuple[_CacheProbe, ModuleType]:
    """Stand-ins for spur.model and spur.app, so the test never loads the kernel."""
    model, app = ModuleType("spur.model"), ModuleType("spur.app")
    probe = _CacheProbe()
    model.__dict__["_build_cached"] = probe
    app.__dict__["_BlobCache"] = _FakeBlobCache
    app.__dict__["_EXPORTS"] = "the export cache the test found"
    monkeypatch.setitem(sys.modules, "spur.model", model)
    monkeypatch.setitem(sys.modules, "spur.app", app)
    return probe, app


def test_with_tables_installs_the_tables_and_empties_the_caches(
        imported_kernel_modules: tuple[_CacheProbe, ModuleType], with_tables: Tables) -> None:
    probe, app = imported_kernel_modules
    assert din5480_tables.active() is with_tables
    assert probe.cleared >= 1
    assert isinstance(app.__dict__["_EXPORTS"], _FakeBlobCache)
