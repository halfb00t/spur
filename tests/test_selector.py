"""The proofs behind a model-level selector (L42), in one module that runs at commit.

A selector is a list on `GearParams.model_config` that the form turns into a `<select>`: each
option is a label and the `when()` conditions of L41 that, all holding, make it the option the
form shows. It is a view of existing fields and never a field, so it moves no default (L05). The
page derives it from the fields and a pick writes the minimum flat fields back (D-07, D-08), and
the part is only the right part if the options say what `GearParams` and `derive()` say. This
module holds the four proofs together:

- the walk: every selector is a well-formed {title, group, options} that `/api/schema` emits
  unchanged, every option's `when` is judged by the one grammar of L41, and every condition names
  a numeric `GearParams` field with a threshold the field's own bounds allow;
- the keyword check: `selectors` is the one top-level key the model adds and no JSON Schema word;
- the grid: over every valid triple of the condition fields exactly one option holds, so the
  options need no precedence and declaration order is display order only (D-02), and where a
  negative value makes none hold the form shows a blank select (D-18) rather than a wrong one;
- the round trip: every pick from every state, and every second pick after it with the stash the
  first one left, through a Python mirror of the write rule, lands on the same `GearParams` and
  the same `derive()` document as typing the minimum flats by hand, changes only the fields that
  made the option false, and leaves the chosen option the only one that holds.

It imports `spur.params`, `spur.calc` and the condition evaluator of `tests/test_relations.py`
only, so there is one Python evaluator of the grammar (D-12). The import-boundary contracts keep
the first two off the CAD kernel, so it is not in `HEAVY_TEST_FILES` (tests/test_hooks.py) and
runs in `make verify.fast`, which is when a drifting option has to be caught.

What each test turns red:

- a selector with a missing or extra key, a label that is empty, padded or repeated, a condition
  on a field the model lacks or one that is not a number, an op outside {eq, gt}, a threshold
  outside the field's bounds, a field under both `eq` and `gt` in one option, or two conditions
  that share one object;
- a `selectors` key that is a JSON Schema word, a second top-level key, or a schema that emits
  the list differently from the model;
- an option on the wrong field or the wrong op, one that overlaps another or a gap where no
  option holds on a non-negative triple;
- a pick that writes the wrong fields, writes before it knows the pick can be made true, lands on
  a part the typed path would not build, or restores a number the user never had;
- the checkers themselves: each is fed doctored copies, so a checker that stops looking goes red
  here rather than passing silently.
"""

import copy
import itertools
from collections.abc import Callable, Iterator, Mapping, Sequence
from decimal import Decimal
from functools import cache

import pytest
from test_relations import (
    KEYWORDS_2020_12,
    LEGACY,
    Condition,
    _condition_holds,
    _conditions,
    _number,
    _properties,
)

from spur.calc import DerivedDimensions, derive
from spur.params import GearParams

Flat = dict[str, float]
# The pick's contract: the chosen option's conditions, the flats, the stash and the defaults in;
# the flats and the stash after in, or None when the pick is pending and writes nothing.
Pick = Callable[
    [Sequence[Condition], Mapping[str, float], Mapping[str, float], Mapping[str, float]],
    tuple[Flat, Flat] | None,
]

# What `derive()` can see of each label, as (bore_effective is set, hex_across_flats is set).
# MEASURED at planning (24-RESEARCH Finding 6): the default part and a Round part give the same
# `derive()` document (9.15 / None for both), a Hex part gives None / 0.2 and No bore None /
# None. Round and D-flat therefore share a class and `derive()` cannot tell them apart, which
# is why the round trip also asserts the changed-field set and that the chosen option alone
# holds: a Round pick that wrote nothing would pass on `derive()` equality alone.
CLASS: dict[str, tuple[bool, bool]] = {
    "Round": (True, False),
    "D-flat": (True, False),
    "Hex": (False, True),
    "No bore": (False, False),
}


@cache
def _defaults() -> dict[str, float]:
    """The schema default of every numeric field: what `effective()` reads in an emptied box."""
    return {name: _number(prop, "default") for name, prop in _properties().items()
            if prop.get("type") in ("number", "integer")}


def _model_selectors() -> list[dict[str, object]]:
    """The selector list straight off `GearParams.model_config`, as the model wrote it."""
    extra = GearParams.model_config.get("json_schema_extra")
    assert isinstance(extra, dict), extra
    raw = extra["selectors"]
    assert isinstance(raw, list), raw
    found: list[dict[str, object]] = []
    for selector in raw:
        assert isinstance(selector, dict), selector
        found.append(dict(selector))
    return found


def _raw_list(parent: Mapping[str, object], key: str) -> list[dict[str, object]]:
    """The live list under `key`, so a doctored copy can be edited in place."""
    value = parent[key]
    assert isinstance(value, list), (key, value)
    return value


def _options(selector: Mapping[str, object]) -> list[tuple[str, list[Condition]]]:
    """Each option's label and its conditions, judged by the grammar of L41."""
    found: list[tuple[str, list[Condition]]] = []
    for option in _raw_list(selector, "options"):
        label = option["label"]
        assert isinstance(label, str), option
        found.append((label, _conditions(option["when"])))
    return found


def _have(flat: Mapping[str, float], field: str, defaults: Mapping[str, float]) -> float:
    """The number the form reads for a field: an absent field is its default, as `effective()`
    reads an emptied box."""
    return flat.get(field, defaults[field])


def _holding(
    options: Sequence[tuple[str, Sequence[Condition]]],
    flat: Mapping[str, float],
    defaults: Mapping[str, float],
) -> list[str]:
    """The labels whose every condition holds. Every condition is evaluated, as the page maps
    every one of them."""
    return [label for label, conditions in options
            if all(_condition_holds(op, _have(flat, field, defaults), threshold)
                   for field, op, threshold in conditions)]


def _pick(
    conditions: Sequence[Condition],
    flat: Mapping[str, float],
    stash: Mapping[str, float],
    defaults: Mapping[str, float],
) -> tuple[Flat, Flat] | None:
    """The model-side mirror of the page's `pick()` (D-07, D-08, PD-08): plan, then write.

    Walk the chosen option's conditions. A condition that holds needs nothing. A false `eq`
    is planned as a write of its value that stashes the number the field holds now. A false
    `gt` is planned as a restore when the stash holds a number above the threshold, and
    otherwise the pick is pending: None, nothing written (the second standing rule, a pick that
    cannot be made true leaves the part alone). Only after the whole walk are the writes
    applied, to copies. A restore leaves its stash entry where it is.
    """
    writes: Flat = {}
    stashed: Flat = {}
    for field, op, threshold in conditions:
        if _condition_holds(op, _have(flat, field, defaults), threshold):
            continue
        if op == "eq":
            writes[field] = threshold
            stashed[field] = _have(flat, field, defaults)
            continue
        kept = stash.get(field)
        if kept is None or not kept > threshold:
            return None
        writes[field] = kept
    return {**flat, **writes}, {**stash, **stashed}


def _pick_write_first(
    conditions: Sequence[Condition],
    flat: Mapping[str, float],
    stash: Mapping[str, float],
    defaults: Mapping[str, float],
) -> tuple[Flat, Flat]:
    """The order the CONTEXT `<specifics>` first sketched, kept only to be seen red.

    Write every false `eq` as it is met, then restore each false `gt` or stop. A stop leaves
    the `eq` writes standing, so a pick that cannot be made true still changes the part: from
    a link with `bore_d` at 0, Round zeroes `bore_flat` and the part becomes No bore under a
    "pending" Round (24-RESEARCH Finding 10). It returns the partly written flats where `_pick`
    returns None.
    """
    after: Flat = dict(flat)
    kept: Flat = dict(stash)
    for field, op, threshold in conditions:
        if op == "eq" and not _condition_holds(op, _have(after, field, defaults), threshold):
            kept[field] = _have(after, field, defaults)
            after[field] = threshold
    for field, op, threshold in conditions:
        if op == "gt" and not _condition_holds(op, _have(after, field, defaults), threshold):
            restored = stash.get(field)
            if restored is None or not restored > threshold:
                break
            after[field] = restored
    return after, kept


def _starts(
    options: Sequence[tuple[str, Sequence[Condition]]], defaults: Mapping[str, float],
) -> dict[str, Flat]:
    """Per label, the minimal flats from the defaults that make it the one option that holds:
    a false `eq` gets its value, a false `gt` the first of `minimum + step` and `maximum`
    above its threshold. Today Round is `{bore_flat: 0}`, D-flat `{}` (the default part, D-02),
    Hex `{bore_hex: 0.05}` and No bore `{bore_d: 0}`."""
    props = _properties()
    starts: dict[str, Flat] = {}
    for label, conditions in options:
        start: Flat = {}
        for field, op, threshold in conditions:
            if _condition_holds(op, _have(start, field, defaults), threshold):
                continue
            if op == "eq":
                start[field] = threshold
                continue
            low, step = _number(props[field], "minimum"), _number(props[field], "step")
            above = [v for v in (low + step, _number(props[field], "maximum")) if v > threshold]
            assert above, f"{label}: no value of {field} above {threshold:g} is in range"
            start[field] = above[0]
        assert _holding(options, start, defaults) == [label], (label, start)
        starts[label] = start
    return starts


def _page_string(value: float) -> str:
    """`${value}` as JavaScript writes it, which is what the page puts in a box.

    The same `Decimal(repr(float(value))).normalize()` with `f` formatting that
    `tests/browser_session.py`'s `_js_number` uses, copied here because that module imports
    playwright and this one must stay in the commit slice. `repr` gives JavaScript's shortest
    round-trip digits and `1.0` becomes `1`; exact for 1e-6 <= |value| < 1e21, which is
    checked, and `-0` is `0`.
    """
    number = float(value)
    assert number == 0 or 1e-6 <= abs(number) < 1e21, (
        f"{number!r}: JavaScript writes this with an exponent, which this function does not"
    )
    return format(Decimal(repr(number)).normalize() + 0, "f")


def _derive_class(gear: GearParams) -> tuple[bool, bool]:
    doc: DerivedDimensions = derive(gear)
    return doc.bore_effective is not None, doc.hex_across_flats is not None


def _positive(field: str) -> float:
    """One in-range positive value: the default, or `minimum + step` when the default is 0."""
    default = _defaults()[field]
    prop = _properties()[field]
    return default if default != 0 else _number(prop, "minimum") + _number(prop, "step")


def _non_negative(field: str) -> tuple[float, ...]:
    return 0.0, _positive(field)


def _wider(field: str) -> tuple[float, ...]:
    """The non-negative values plus one negative one, which `GearParams` refuses with a 422 but
    the form's number box keeps (24-RESEARCH Finding 5)."""
    return -1.0, 0.0, _positive(field)


def _grid(
    selector: Mapping[str, object], values: Callable[[str], Sequence[float]],
) -> Iterator[tuple[tuple[float, ...], list[str]]]:
    """Every cell of the product of `values(field)` over the selector's distinct condition
    fields, in order of first appearance, with the labels that hold there."""
    options = _options(selector)
    fields = list(dict.fromkeys(f for _, conditions in options for f, _, _ in conditions))
    defaults = _defaults()
    for cell in itertools.product(*(values(field) for field in fields)):
        yield cell, _holding(options, dict(zip(fields, cell, strict=True)), defaults)


def _assert_well_formed(selectors: Sequence[Mapping[str, object]]) -> None:
    """The walk (D-05, D-12a). Every failure names the selector, the option and the fault."""
    assert selectors, "no selector is declared"
    props = _properties()
    groups = {prop["group"] for prop in props.values()}
    condition_ids: list[int] = []
    for index, selector in enumerate(selectors):
        where = f"selector {index}"
        assert set(selector) == {"title", "group", "options"}, f"{where}: keys {sorted(selector)}"
        for key in ("title", "group"):
            value = selector[key]
            assert isinstance(value, str), f"{where}: {key} is not a string"
            assert value, f"{where}: {key} is empty"
        assert selector["group"] in groups, f"{where}: no field carries group {selector['group']!r}"
        options = _raw_list(selector, "options")
        assert options, f"{where}: no options"
        labels: list[str] = []
        for option in options:
            assert set(option) == {"label", "when"}, f"{where}: option keys {sorted(option)}"
            label = option["label"]
            assert isinstance(label, str), f"{where}: a label is not a string"
            assert label, f"{where}: an option has an empty label"
            assert label == " ".join(label.split()), f"{where}: label {label!r} has stray space"
            assert label not in labels, f"{where}: label {label!r} is repeated"
            labels.append(label)
            there = f"{where}, {label}"
            eq_fields: set[str] = set()
            gt_fields: set[str] = set()
            for field, op, threshold in _conditions(option["when"]):
                assert field in GearParams.model_fields, f"{there}: {field} is no such field"
                annotation = GearParams.model_fields[field].annotation
                assert annotation in (int, float), f"{there}: {field} is not numeric"
                assert _number(props[field], "minimum") <= threshold, (
                    f"{there}: {field} {op} {threshold:g} is below the minimum")
                assert threshold <= _number(props[field], "maximum"), (
                    f"{there}: {field} {op} {threshold:g} is above the maximum")
                (eq_fields if op == "eq" else gt_fields).add(field)
            # A pick zeroes the false `eq` fields and restores the false `gt` fields, so a field
            # under both would be zeroed and then needed (24-RESEARCH Finding 10).
            assert not eq_fields & gt_fields, (
                f"{there}: {sorted(eq_fields & gt_fields)} is under both eq and gt")
            condition_ids.extend(id(c) for c in _raw_list(option, "when"))
    assert len(set(condition_ids)) == len(condition_ids), "two conditions share one object"


def _bad_cells(
    selectors: Sequence[Mapping[str, object]], values: Callable[[str], Sequence[float]],
) -> list[tuple[tuple[float, ...], list[str]]]:
    """Every cell where the number of holding options is not exactly one, with the labels that
    held: `[]` is a gap, two labels an overlap."""
    return [(cell, held) for selector in selectors for cell, held in _grid(selector, values)
            if len(held) != 1]


def _assert_exactly_one(selectors: Sequence[Mapping[str, object]]) -> int:
    """Totality and exclusivity (D-02, D-18). Over `{0, positive}` per field exactly one option
    holds. Over `{-1, 0, positive}` no cell has two, every cell with none has a negative value
    in it, and at least one such cell exists, so the blank state is exercised. Returns the
    number of cells checked."""
    cells = 0
    gaps = 0
    for selector in selectors:
        title = selector["title"]
        for cell, held in _grid(selector, _non_negative):
            cells += 1
            assert len(held) == 1, f"{title}: cell {cell} holds {held}, not exactly one option"
        for cell, held in _grid(selector, _wider):
            cells += 1
            assert len(held) <= 1, f"{title}: cell {cell} holds {held}: two options claim it"
            if not held:
                gaps += 1
                assert min(cell) < 0, f"{title}: cell {cell} holds no option and no value < 0"
    assert gaps > 0, "no cell holds no option: the blank state is not exercised"
    return cells


def _check_pick(
    options: Sequence[tuple[str, Sequence[Condition]]],
    label: str,
    before: Mapping[str, float],
    stash: Mapping[str, float],
    pick: Pick,
    where: str,
) -> tuple[Flat, Flat] | None:
    """One pick, judged. Returns what it left, or None when it was pending."""
    defaults = _defaults()
    conditions = dict(options)[label]
    result = pick(conditions, before, stash, defaults)
    if result is None:
        # Pending is only honest when a `gt` field is short and nothing stashed could make it
        # long enough: the pick had no number to write that the user had not typed.
        assert any(
            op == "gt" and not _condition_holds(op, _have(before, field, defaults), threshold)
            and not stash.get(field, threshold) > threshold
            for field, op, threshold in conditions), f"{where}: pending with every gt satisfiable"
        return None
    after, _ = result
    false = {field for field, op, threshold in conditions
             if not _condition_holds(op, _have(before, field, defaults), threshold)}
    # The page sends strings, so both paths are validated from the strings it would send.
    gear = GearParams.model_validate({k: _page_string(v) for k, v in after.items()})
    assert _holding(options, after, defaults) == [label], (
        f"{where}: {label} is not the one that holds")
    changed = {field for field in set(before) | set(after)
               if _have(before, field, defaults) != _have(after, field, defaults)}
    assert changed == false, f"{where}: changed {sorted(changed)}, expected {sorted(false)}"
    typed = {k: _page_string(v) for k, v in before.items()}
    for field, op, threshold in conditions:
        if field in false:
            assert op == "eq" or field in stash, f"{where}: {field} has nothing stashed to type"
            typed[field] = _page_string(threshold if op == "eq" else stash[field])
    typed_gear = GearParams.model_validate(typed)
    assert gear == typed_gear, f"{where}: the pick and the typed path differ as parameters"
    assert derive(gear).model_dump() == derive(typed_gear).model_dump(), (
        f"{where}: the pick and the typed path differ in derive()")
    assert _derive_class(gear) == CLASS[label], f"{where}: {label} has the wrong derive() class"
    return result


def _assert_round_trips(
    selectors: Sequence[Mapping[str, object]], pick: Pick = _pick,
) -> tuple[int, int]:
    """The round trip per state (D-07, D-08, D-09, D-12c). From each option's minimal start,
    every option is picked with an empty stash and, when that pick wrote, every option again
    with the stash the first left. Returns (writing picks, pending picks)."""
    writing = 0
    pending = 0
    for selector in selectors:
        options = _options(selector)
        for start_label, start in _starts(options, _defaults()).items():
            for first, _ in options:
                where = f"from {start_label}, pick {first}"
                left = _check_pick(options, first, start, {}, pick, where)
                if left is None:
                    pending += 1
                    continue
                writing += 1
                for second, _ in options:
                    again = _check_pick(options, second, left[0], left[1], pick,
                                        f"{where}, then {second}")
                    if again is None:
                        pending += 1
                    else:
                        writing += 1
    return writing, pending


def test_every_selector_is_well_formed_and_emitted_unchanged() -> None:
    """SC1, D-05, D-12a: the walk. Red on any malformed selector or option, an unjudgeable
    condition, a threshold outside its field's bounds, a field under both ops, a shared
    condition object, or a schema that emits the list differently from the model."""
    selectors = _model_selectors()
    _assert_well_formed(selectors)
    assert GearParams.model_json_schema()["selectors"] == selectors


def test_selectors_is_the_one_top_level_key_and_no_json_schema_keyword() -> None:
    """D-05: `selectors` is the only key the model adds beside what pydantic emits, and a
    validator reading either dialect would not enforce it. Red when a second key appears or
    `selectors` joins a keyword list. The check is not recursive on purpose: the selector's
    own `title` is a keyword, harmless as the value of an unknown key, and a recursive scan
    would flag it for nothing (24-RESEARCH Finding 2)."""
    assert sorted(GearParams.model_json_schema()) == [
        "description", "properties", "selectors", "title", "type"]
    assert "selectors" not in KEYWORDS_2020_12 | LEGACY


def test_exactly_one_option_holds_on_every_valid_cell_and_the_default_is_d_flat() -> None:
    """SC2, D-02, D-18: totality and exclusivity. Red on a gap or an overlap on any
    non-negative cell, two options on any cell, a no-match cell without a negative value, or a
    default part that is not shown as D-flat. The literal pins the shipped default (D-02)."""
    selectors = _model_selectors()
    assert _assert_exactly_one(selectors) == 8 + 27
    assert _holding(_options(selectors[0]), {}, _defaults()) == ["D-flat"]


def test_each_pick_from_each_state_writes_the_minimum_and_matches_the_typed_path() -> None:
    """SC3, D-07, D-08, D-09, D-12c: the round trip. Red on a pick that writes a field it need
    not, leaves its option false, or builds a part (or a `derive()` document) the same flats
    typed by hand would not. Both branches must be exercised or the proof is half empty."""
    writing, pending = _assert_round_trips(_model_selectors())
    assert writing > 0
    assert pending > 0


def test_a_zeroed_value_comes_back_from_the_stash_and_never_from_a_starter() -> None:
    """D-08: after a pick zeroes a field, picking the first state back restores what the user
    had, never a starter value, and with nothing stashed that pick is pending. Red when the
    restore returns another number or the empty stash writes one."""
    defaults = _defaults()
    options = _options(_model_selectors()[0])
    exercised = 0
    for label, start in _starts(options, defaults).items():
        named = {field for field, _, _ in dict(options)[label]}
        for other, conditions in options:
            first = _pick(conditions, start, {}, defaults)
            if first is None or first[0] == start:
                continue
            back = _pick(dict(options)[label], first[0], first[1], defaults)
            assert back is not None, f"{label} -> {other} -> {label} is pending with a stash"
            for field in named:
                assert _have(back[0], field, defaults) == _have(start, field, defaults), (
                    f"{label} -> {other} -> {label}: {field} did not come back")
            zeroed_gt = [field for field, op, threshold in dict(options)[label]
                         if op == "gt" and not _have(first[0], field, defaults) > threshold]
            if zeroed_gt:
                assert _pick(dict(options)[label], first[0], {}, defaults) is None, (
                    f"{label} -> {other} -> {label}: an empty stash still wrote a number")
            exercised += 1
    assert exercised > 0


def _wrong_field(selectors: list[dict[str, object]]) -> None:
    _condition(_option_named(selectors, "D-flat"), "bore_flat")["field"] = "bore_hex"


def _wrong_op(selectors: list[dict[str, object]]) -> None:
    _condition(_option_named(selectors, "Round"), "bore_flat")["op"] = "gt"


def _overlap(selectors: list[dict[str, object]]) -> None:
    when = _raw_list(_option_named(selectors, "Round"), "when")
    when[:] = [c for c in when if c["field"] != "bore_flat"]


def _gap(selectors: list[dict[str, object]]) -> None:
    options = _raw_list(selectors[0], "options")
    options[:] = [o for o in options if o["label"] != "No bore"]


def _option_named(selectors: list[dict[str, object]], label: str) -> dict[str, object]:
    return next(o for o in _raw_list(selectors[0], "options") if o["label"] == label)


def _condition(option: dict[str, object], field: str) -> dict[str, object]:
    return next(c for c in _raw_list(option, "when") if c["field"] == field)


WRONG_OPTIONS = {"wrong field": _wrong_field, "wrong op": _wrong_op, "overlap": _overlap,
                 "gap": _gap}


@pytest.mark.parametrize(("case", "bad"),
                         [("wrong field", 1), ("wrong op", 2), ("overlap", 1), ("gap", 2)])
def test_a_wrong_option_goes_red(case: str, bad: int) -> None:
    """D-12d, 24-RESEARCH Finding 7: the cells that match not exactly one option of the eight
    non-negative ones are 1, 2, 1 and 2 for the four doctored copies, and the checker raises.
    The unedited model is the control, so a red here is the edit and not an unusable grid."""
    assert _bad_cells(_model_selectors(), _non_negative) == []
    doctored = copy.deepcopy(_model_selectors())
    WRONG_OPTIONS[case](doctored)
    assert len(_bad_cells(doctored, _non_negative)) == bad
    with pytest.raises(AssertionError, match="not exactly one"):
        _assert_exactly_one(doctored)


def _not_a_model_field(selectors: list[dict[str, object]]) -> None:
    _condition(_option_named(selectors, "Round"), "bore_d")["field"] = "bore_diameter"


def _not_a_number_field(selectors: list[dict[str, object]]) -> None:
    _condition(_option_named(selectors, "Round"), "bore_d")["field"] = "recess_sides"


def _op_outside_the_grammar(selectors: list[dict[str, object]]) -> None:
    _condition(_option_named(selectors, "Round"), "bore_d")["op"] = "ge"


def _empty_label(selectors: list[dict[str, object]]) -> None:
    _option_named(selectors, "Round")["label"] = ""


def _one_field_under_both_ops(selectors: list[dict[str, object]]) -> None:
    _raw_list(_option_named(selectors, "D-flat"), "when").append(
        {"field": "bore_d", "op": "eq", "value": 0})


def _threshold_over_the_maximum(selectors: list[dict[str, object]]) -> None:
    _condition(_option_named(selectors, "Hex"), "bore_hex")["value"] = 999


MALFORMED = {
    "a field the model does not have": (_not_a_model_field, "no such field"),
    "a field that is not a number": (_not_a_number_field, "is not numeric"),
    "an op outside the grammar": (_op_outside_the_grammar, "is outside"),
    "an empty label": (_empty_label, "empty label"),
    "one field under both ops": (_one_field_under_both_ops, "under both eq and gt"),
    "a threshold over the maximum": (_threshold_over_the_maximum, "above the maximum"),
}


@pytest.mark.parametrize("case", list(MALFORMED))
def test_a_malformed_selector_goes_red(case: str) -> None:
    """D-12d: the walk raises, and for its own reason, on each of six doctored copies. The
    unedited model passes first, so a red is the edit and not an unusable selector."""
    _assert_well_formed(_model_selectors())
    edit, reason = MALFORMED[case]
    doctored = copy.deepcopy(_model_selectors())
    edit(doctored)
    with pytest.raises(AssertionError, match=reason):
        _assert_well_formed(doctored)


def test_writing_before_planning_goes_red() -> None:
    """D-09, D-12d, 24-RESEARCH Finding 10: the mirror that writes each `eq` before it knows a
    `gt` can be met leaves a changed part under a pending pick. From the No bore start, Round
    needs a `bore_d` the user never typed: `_pick` writes nothing and `_pick_write_first`
    zeroes `bore_flat`. The round trip raises on the second, and passes on the first."""
    selectors = _model_selectors()
    _assert_round_trips(selectors)
    with pytest.raises(AssertionError, match="is not the one that holds"):
        _assert_round_trips(selectors, pick=_pick_write_first)
    options = _options(selectors[0])
    start = _starts(options, _defaults())["No bore"]
    round_bore = dict(options)["Round"]
    assert _pick(round_bore, start, {}, _defaults()) is None
    written, _ = _pick_write_first(round_bore, start, {}, _defaults())
    assert written["bore_flat"] == 0


def test_the_page_string_reads_a_number_as_the_page_does() -> None:
    """27-REVIEW IN-03: `_page_string` is a copy of `tests/browser_session.py`'s `_js_number`,
    made so this module stays off playwright, and `tests/test_browser.py` pins only the
    original. The same rows here keep the two from drifting: `-0` is `0`, positional digits
    through 1e16, and an exponent range raises rather than writing a string the page does not."""
    for number, written in ((-0.0, "0"), (1.0, "1"), (0.05, "0.05"), (1e-6, "0.000001"),
                            (1e16, "10000000000000000")):
        assert _page_string(number) == written
    for beyond in (1e21, 1e-7):
        with pytest.raises(AssertionError, match="exponent"):
            _page_string(beyond)
