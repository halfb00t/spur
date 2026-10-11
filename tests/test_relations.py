"""The three proofs behind a field relation (L41), in one module that runs at commit.

A relation is `enabled_when` on a `GearParams` field: a claim that, with the relation
false, the field does nothing (or is refused). The claim is only worth printing if `calc`
says the same thing, so this module holds the three proofs together:

- the grammar walk: every relation is a well-formed list of {field, op, value}, emitted by
  `/api/schema` exactly as the model wrote it, under a key no JSON Schema validator
  enforces;
- the keyword collision: no extra key the model contributes is a JSON Schema word, and
  both construction styles (`_f` and the two `Literal` fields) build it through `_extra()`;
- the calc parity: with its relation false, a dependent moves nothing in `derive()` but
  `warnings`, and a warning names it (forward); every field `derive()` calls ignored
  has a relation (reverse); and in each of eight whole-part states the relation is true
  exactly where `derive()` does not call the field ignored (the driver check).

It imports `spur.params` and `spur.calc` only. The import-boundary contracts keep both off
the CAD kernel, so it is not in `HEAVY_TEST_FILES` (tests/test_hooks.py) and runs in
`make verify.fast`, which is when a drifting relation has to be caught.

What each test turns red:

- a condition naming a missing or non-numeric field, an op outside {eq, gt}, a bool or
  string value, a dependent that is also a driver, an emitted empty list, an extra key
  outside {group, unit, step, enabled_when};
- an extra key that collides with a JSON Schema word, or a `Field(...)` that builds its
  extra without `_extra()` (a `Literal` field would drop `enabled_when` silently);
- a relation `derive()` contradicts (it changes something but `warnings`), one `calc`
  never calls ignored (nothing names the field), or a keyway field that changes class;
- a "ignored" sentence in `derive()` for a field that has no relation;
- a relation on the wrong driver: a spoke field gated on `hole_count`, a hole field on
  `bore_hex`, or a right driver with an extra gate beside it. The forward parity cannot see
  these (WR-03): every probe there leaves the other cutout gates at their default 0, so
  the right driver and a wrong one are closed alike.
"""

import ast
import inspect
import re
from collections.abc import Mapping, Sequence
from functools import cache
from pathlib import Path
from typing import Literal

import pytest
from pydantic import BaseModel, Field, ValidationError

from spur.calc import derive
from spur.params import GearParams, _extra, when

Condition = tuple[str, str, float]

# The refused class: under a hex bore each keyway field alone is a 422 naming bore_hex,
# keyway_depth and keyway_width (PITFALLS CF-2, measured), not an ignored value, so the two
# are never gated on each other. Pinned so a row that changes class goes red.
REFUSED = frozenset({"keyway_width", "keyway_depth"})

# D-02: the grammar knows two ops. A third is a decision, not an edit.
OPS = frozenset({"eq", "gt"})
# D-05: one relation key and no class marker; the other three are the existing metadata.
EXTRA_KEYS = frozenset({"group", "unit", "step", "enabled_when"})

# Source: https://json-schema.org/draft/2020-12/json-schema-validation and the core page's
# vocabularies (core, applicator, unevaluated, validation, format, content, meta-data).
# 23-RESEARCH A1: the core page was truncated at the applicator vocabulary when fetched, so
# anyOf/if/then/else/dependentSchemas come from the validation spec's cross-reference list.
KEYWORDS_2020_12 = frozenset({
    "$id", "$schema", "$ref", "$anchor", "$dynamicRef", "$dynamicAnchor", "$vocabulary",
    "$comment", "$defs",
    "prefixItems", "items", "contains", "additionalProperties", "properties",
    "patternProperties", "dependentSchemas", "propertyNames", "if", "then", "else",
    "allOf", "anyOf", "oneOf", "not", "unevaluatedItems", "unevaluatedProperties",
    "type", "const", "enum", "multipleOf", "maximum", "exclusiveMaximum", "minimum",
    "exclusiveMinimum", "maxLength", "minLength", "pattern", "maxItems", "minItems",
    "uniqueItems", "maxContains", "minContains", "maxProperties", "minProperties",
    "required", "dependentRequired",
    "format", "contentEncoding", "contentMediaType", "contentSchema",
    "title", "description", "default", "deprecated", "readOnly", "writeOnly", "examples",
})
# Draft-7 words a validator reading an older dialect still enforces.
LEGACY = frozenset({"definitions", "dependencies", "additionalItems"})


class _Probe(BaseModel):
    """A throwaway model with a `Literal` field that carries two conditions. Module level so
    pydantic resolves `Literal` from this module's names."""

    s: Literal["x", "y"] = Field(
        "x", title="S",
        json_schema_extra=_extra("g", enabled_when=[when("a", "gt", 0), when("b", "eq", 0)]))


@cache
def _properties() -> dict[str, dict[str, object]]:
    raw = GearParams.model_json_schema()["properties"]
    assert isinstance(raw, dict)
    props: dict[str, dict[str, object]] = {}
    for name, prop in raw.items():
        assert isinstance(prop, dict), name
        props[name] = prop
    return props


def _number(prop: Mapping[str, object], key: str) -> float:
    value = prop[key]
    assert isinstance(value, int | float), (key, value)
    assert not isinstance(value, bool), (key, value)
    return float(value)


def _conditions(value: object) -> list[Condition]:
    """The one judge of a relation's grammar: a non-empty list of {field, op, value}."""
    assert isinstance(value, list), f"enabled_when is not a list: {value!r}"
    assert value, "enabled_when is an empty list"
    found: list[Condition] = []
    for item in value:
        assert isinstance(item, dict), item
        assert set(item) == {"field", "op", "value"}, item
        field, op, number = item["field"], item["op"], item["value"]
        assert isinstance(field, str), item
        assert isinstance(op, str), item
        assert op in OPS, f"op {op!r} is outside {sorted(OPS)}"
        assert isinstance(number, int | float), f"value {number!r} is not a number"
        assert not isinstance(number, bool), f"value {number!r} is a bool"
        found.append((field, op, float(number)))
    return found


def _relations() -> dict[str, list[Condition]]:
    return {name: _conditions(prop["enabled_when"])
            for name, prop in _properties().items() if "enabled_when" in prop}


def _closed(gate: str, op: str, value: float) -> float:
    """The gate value that makes the condition false: the threshold itself for `gt`, one
    schema step off it for `eq`."""
    prop = _properties()[gate]
    closed = value if op == "gt" else value + _number(prop, "step")
    assert _number(prop, "minimum") <= closed <= _number(prop, "maximum"), (gate, closed)
    return closed


def _named_fields(error: ValidationError) -> set[str]:
    """The fields `GearParams._feasible` named, from the first error's `ctx`."""
    ctx = error.errors()[0].get("ctx")
    assert isinstance(ctx, dict), error
    fields = ctx["fields"]
    assert isinstance(fields, list), ctx
    return {str(f) for f in fields}


def _assert_relations_hold_in_calc(relations: Mapping[str, Sequence[Condition]]) -> int:
    """Forward parity. With each dependent's relation false, at `minimum + step` and at
    `maximum` of its schema bounds: a refused field is one of `REFUSED` and the refusal
    names the gate; any other changes nothing in `derive()` but `warnings`, and a warning
    names it. Returns the number of perturbations made.

    Derive-invariance alone proves too little (23-RESEARCH Pitfall 2): `bore_chamfer`
    shapes the hex bore mouth yet moves nothing `derive()` reports, so it would pass. What
    makes a relation true is that `calc` says the field is ignored, hence the warning
    check. It is a membership test on the field's own fragment, never the whole sentence:
    a sibling at its default is named too (Pitfall 3).
    """
    props = _properties()
    checked = 0
    for dep, conditions in relations.items():
        prop = props[dep]
        unit = prop["unit"]
        assert isinstance(unit, str), dep
        low, step = _number(prop, "minimum"), _number(prop, "step")
        high, default = _number(prop, "maximum"), _number(prop, "default")
        for gate, op, threshold in conditions:
            closed = _closed(gate, op, threshold)
            base = derive(GearParams.model_validate({gate: closed})).model_dump()
            for value in (low + step, high):
                assert value != default, f"{dep}={value:g} is its default: a no-op proves nothing"
                checked += 1
                where = f"{dep}={value:g} with {gate}={closed:g}"
                try:
                    gear = GearParams.model_validate({gate: closed, dep: value})
                except ValidationError as error:
                    assert dep in REFUSED, f"{where}: refused, but {dep} is not in REFUSED"
                    named = _named_fields(error)
                    assert {gate} | REFUSED <= named, f"{where}: the refusal names only {named}"
                    continue
                assert dep not in REFUSED, f"{where}: accepted, but {dep} is in REFUSED"
                doc = derive(gear).model_dump()
                moved = sorted(key for key in doc if doc[key] != base[key])
                assert set(moved) <= {"warnings"}, f"{where}: derive() changed {moved}"
                warnings = doc["warnings"]
                assert isinstance(warnings, list | tuple), where
                fragment = f"{dep} ({value:g} {unit})"
                assert fragment in " ".join(warnings), (
                    f"{where}: no warning names {fragment}: calc does not say it is ignored")
    return checked


def _assert_calc_ignores_only(declared: frozenset[str]) -> int:
    """Reverse coverage. Set each undeclared numeric field alone, at `minimum + step` and
    at `maximum`, under defaults; every field an "ignored" sentence of `derive()` then
    names must be declared. A request `check()` refuses names no ignored field and is
    skipped. Returns the number of "ignored" sentences seen, so an empty scan is visible.
    """
    seen = 0
    for name, prop in _properties().items():
        if name in declared or prop.get("type") not in ("number", "integer"):
            continue
        low, step = _number(prop, "minimum"), _number(prop, "step")
        high, default = _number(prop, "maximum"), _number(prop, "default")
        for value in (low + step, high):
            if value == default:
                continue
            try:
                gear = GearParams.model_validate({name: value})
            except ValidationError:
                continue
            for warning in derive(gear).warnings:
                if "ignored" not in warning:
                    continue
                seen += 1
                for field in GearParams.model_fields:
                    named = re.search(rf"\b{field} \(", warning) is not None
                    assert not named or field in declared, (
                        f"{name}={value:g}: calc says {warning!r}, naming {field}, "
                        f"but no relation declares {field}")
    return seen


# The driver check's states: one whole part per cutout pattern times one per bore kind. `calc`
# refuses two cutout patterns at once ("Only one body cutout pattern per part"), so a part
# cannot open every driver together and each family is opened alone, as a full set: the
# spoke and hole fields are required once their count is set, and hex_wall must be at least
# 0.4 mm. Each gate sits at the first value past its closed one (the count 1, the cell
# 0.05 mm, which `calc` enlarges with a warning and accepts), because a relation whose
# threshold is off by one (`spoke_count gt 1`) is false at exactly that value. All eight
# states validate (measured 2026-10-11).
CUTOUT_STATES: dict[str, dict[str, float]] = {
    "no cutout": {},
    "spokes": {"spoke_count": 1, "spoke_width": 4, "hub_d": 20, "rim_wall": 3,
               "spoke_fillet": 0.5},
    "holes": {"hole_count": 1, "hole_d": 3, "hole_circle_d": 24},
    "honeycomb": {"hex_cell": 0.05, "hex_wall": 1},
}
# A hex bore refuses a keyway (the REFUSED pair); a round bore with one is the other kind.
BORE_STATES: dict[str, dict[str, float]] = {
    "round bore": {"keyway_width": 3, "keyway_depth": 1.4},
    "hex bore": {"bore_hex": 6},
}


def _condition_holds(op: str, have: float, threshold: float) -> bool:
    return have == threshold if op == "eq" else have > threshold


def _assert_relations_name_the_driver_calc_obeys(
    relations: Mapping[str, Sequence[Condition]],
) -> int:
    """Driver parity (WR-03). In each whole-part state, a dependent's relation holds exactly
    when `derive()` does not call the dependent ignored; a refusal counts as ignored for a
    `REFUSED` field only. Returns the number of (dependent, state) cells compared.

    The forward check closes one gate from the defaults, where the other cutout gates are
    already 0, so it passes a relation on the wrong driver (`spoke_width <- hole_count`) and
    one with an extra gate beside the right one. Here a family's own fields are live in its
    own state, so a relation naming another driver is false where `calc` uses the field, and
    one that is true in another family's state is true where `calc` says ignored. The value
    tried is the state's own, else the field's default, else `minimum + step`: a default
    is what a hex bore says is ignored (bore_d (9 mm)), and 0 would be named by nothing.
    A gate that never differs across valid parts (`spoke_count eq 0` beside `hole_count gt
    0`, since two patterns are refused) changes nothing a user can see and passes.
    """
    props = _properties()
    cells = 0
    for dep, conditions in relations.items():
        prop = props[dep]
        unit = prop["unit"]
        assert isinstance(unit, str), dep
        default = _number(prop, "default")
        fallback = default if default != 0 else _number(prop, "minimum") + _number(prop, "step")
        for cutout, bore in ((c, b) for c in CUTOUT_STATES for b in BORE_STATES):
            state = {**CUTOUT_STATES[cutout], **BORE_STATES[bore]}
            where = f"{dep} in {cutout} + {bore}"
            value = state.get(dep, fallback)
            predicted_live = all(
                _condition_holds(op, state.get(gate, _number(props[gate], "default")), threshold)
                for gate, op, threshold in conditions)
            try:
                gear = GearParams.model_validate({**state, dep: value})
            except ValidationError as error:
                refusal = error.errors()[0]["msg"]
                assert dep in REFUSED, f"{where}: {dep}={value:g} is refused: {refusal}"
                calc_live = False
            else:
                fragment = f"{dep} ({value:g} {unit})"
                calc_live = not any(
                    fragment in warning and "ignored" in warning
                    for warning in derive(gear).warnings)
            cells += 1
            assert calc_live == predicted_live, (
                f"{where}: the relation says {'used' if predicted_live else 'ignored'}, "
                f"calc says {'used' if calc_live else 'ignored'}: wrong or extra driver")
    return cells


def test_every_relation_is_well_formed_and_emitted_unchanged() -> None:
    """SC1, D-04: the grammar walk. Red on any malformed condition, a dependent that is
    also a driver, an emitted empty list or one that differs from the model's, an extra
    key outside `EXTRA_KEYS`, or two conditions that share one dict."""
    props = _properties()
    declared: dict[str, list[Condition]] = {}
    objects: list[object] = []
    for name, model_field in GearParams.model_fields.items():
        extra = model_field.json_schema_extra
        assert isinstance(extra, dict), name
        assert set(extra) <= EXTRA_KEYS, f"{name}: extra keys {sorted(set(extra) - EXTRA_KEYS)}"
        if "enabled_when" not in extra:
            # An absent relation is an absent key: the form reads it as [] and never dims.
            assert "enabled_when" not in props[name], name
            continue
        raw = extra["enabled_when"]
        declared[name] = _conditions(raw)
        for driver, _, _ in declared[name]:
            assert driver in GearParams.model_fields, f"{name} <- {driver}: no such field"
            # D-03: a gate is a number, compared as a number.
            assert GearParams.model_fields[driver].annotation in (int, float), (name, driver)
        emitted = props[name]["enabled_when"]
        assert emitted == raw, name
        assert isinstance(emitted, list)
        for condition in emitted:
            # model_json_schema() key-sorts, and the order is the one tests read.
            assert list(condition) == ["field", "op", "value"], (name, condition)
        assert isinstance(raw, list)
        objects.extend(raw)
    assert declared, "no relation is declared"
    drivers = {driver for conditions in declared.values() for driver, _, _ in conditions}
    assert not drivers & set(declared), sorted(drivers & set(declared))  # depth 1 (D-20)
    assert len({id(o) for o in objects}) == len(objects), "two conditions share one object"


def test_no_extra_key_is_a_json_schema_keyword() -> None:
    """CF-3: a key a validator enforces would turn a relation into a schema constraint, and
    a link the API accepts would stop validating. Red when `enabled_when` or any key the
    model contributes joins `KEYWORDS_2020_12` or `LEGACY`, so the next key is checked too."""
    words = KEYWORDS_2020_12 | LEGACY
    assert "enabled_when" not in words
    assert not EXTRA_KEYS & words, sorted(EXTRA_KEYS & words)
    contributed = {key for f in GearParams.model_fields.values()
                   if isinstance(f.json_schema_extra, dict) for key in f.json_schema_extra}
    assert "enabled_when" in contributed
    assert contributed <= EXTRA_KEYS, sorted(contributed - EXTRA_KEYS)


def test_both_construction_styles_build_their_extra_through_one_helper() -> None:
    """CF-3: `_f` and the two `Literal` fields write `Field(...)` directly. A third style
    that builds its extra by hand could drop `enabled_when` without a failure anywhere.
    Red on a `Field` whose `json_schema_extra` is not a call to `_extra`, a count other
    than three, or an `_f` that stops calling it."""
    source = Path(inspect.getfile(GearParams)).read_text(encoding="utf-8")
    tree = ast.parse(source)
    extras = [kw.value for node in ast.walk(tree)
              if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
              and node.func.id == "Field"
              for kw in node.keywords if kw.arg == "json_schema_extra"]
    for value in extras:
        assert isinstance(value, ast.Call), ast.dump(value)
        assert isinstance(value.func, ast.Name), ast.dump(value)
        assert value.func.id == "_extra", ast.dump(value)
    assert len(extras) == 3, len(extras)  # _f, root_shape, recess_sides
    helper = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_f")
    assert any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "_extra"
               for n in ast.walk(helper))


def test_a_literal_field_carries_enabled_when_unchanged() -> None:
    """CF-3's silent-drop trap: a `Literal` field is built outside `_f`. Red when its
    extra loses a relation or merges two conditions into one object."""
    emitted = _Probe.model_json_schema()["properties"]["s"]["enabled_when"]
    assert emitted == [{"field": "a", "op": "gt", "value": 0},
                       {"field": "b", "op": "eq", "value": 0}]
    assert emitted[0] is not emitted[1]


def test_with_its_relation_false_a_dependent_moves_only_the_warning_that_names_it() -> None:
    """SC2, D-10, D-11: forward parity over every declared relation. Red on a relation
    `derive()` contradicts, one `calc` never calls ignored, or a keyway field that is
    refused where a relation says it is ignored."""
    relations = _relations()
    perturbations = 2 * sum(len(conditions) for conditions in relations.values())
    assert perturbations > 0
    assert _assert_relations_hold_in_calc(relations) == perturbations


def test_the_keyway_pair_is_refused_under_a_hex_bore_alone_and_together() -> None:
    """CF-2: the pair is refused, not ignored, and never gated on each other. Red when
    either is undeclared, they do not share a gate, or both together are not refused
    naming the gate and both."""
    relations = _relations()
    assert set(relations) >= REFUSED, sorted(REFUSED - set(relations))
    shared = {tuple(relations[name]) for name in REFUSED}
    assert len(shared) == 1, shared
    ((gate, op, threshold),) = shared.pop()
    props = _properties()
    closed = _closed(gate, op, threshold)
    both = {name: _number(props[name], "minimum") + _number(props[name], "step")
            for name in REFUSED}
    with pytest.raises(ValidationError) as refusal:
        GearParams.model_validate({gate: closed, **both})
    assert {gate} | REFUSED <= _named_fields(refusal.value)


def test_every_field_calc_ignores_is_declared() -> None:
    """SC2, D-10 reverse coverage: every field an "ignored" sentence can name has a
    relation. Red when `calc` gains an ignored rule without one."""
    assert _assert_calc_ignores_only(frozenset(_relations())) > 0


def test_a_relation_calc_uses_goes_red() -> None:
    """RESEARCH Pitfall 2 (a): `recess_depth` is used under a hex bore (`web` moves), so
    the forward check must refuse the relation, whatever the declared set says."""
    with pytest.raises(AssertionError, match=r"derive\(\) changed"):
        _assert_relations_hold_in_calc({"recess_depth": [("bore_hex", "eq", 0.0)]})


def test_a_relation_calc_never_calls_ignored_goes_red() -> None:
    """RESEARCH Pitfall 2 (b): `bore_chamfer` changes nothing `derive()` reports under a
    hex bore and no sentence names it, so only the warning-names check can see it."""
    with pytest.raises(AssertionError, match="no warning names"):
        _assert_relations_hold_in_calc({"bore_chamfer": [("bore_hex", "eq", 0.0)]})


def test_each_relation_names_the_driver_calc_obeys() -> None:
    """WR-03: driver parity over every declared relation, in eight whole-part states. Red on
    a relation whose driver `calc` does not use for the field, or whose extra gate makes
    it true where `calc` says ignored."""
    relations = _relations()
    cells = _assert_relations_name_the_driver_calc_obeys(relations)
    assert cells == len(relations) * len(CUTOUT_STATES) * len(BORE_STATES)


# Every field a cutout family owns, and the gates it must not be declared on instead.
_CUTOUT_GATES = {"spoke_count", "hole_count", "hex_cell"}
_OWNER_OF = {"spoke_width": "spoke_count", "hub_d": "spoke_count", "rim_wall": "spoke_count",
             "spoke_fillet": "spoke_count", "hole_d": "hole_count",
             "hole_circle_d": "hole_count", "hex_wall": "hex_cell"}
_WRONG_DRIVERS = [(dep, wrong) for dep, owner in _OWNER_OF.items()
                  for wrong in sorted((_CUTOUT_GATES - {owner}) | {"bore_hex"})]


def test_the_driver_check_passes_for_the_declared_owner_alone() -> None:
    """The control for the swaps below: the same seven fields on their own gate are
    accepted, so a red below is the wrong driver and not an unusable state."""
    relations = {dep: _relations()[dep] for dep in _OWNER_OF}
    assert _assert_relations_name_the_driver_calc_obeys(relations) == len(_OWNER_OF) * 8


@pytest.mark.parametrize(("dep", "wrong"), _WRONG_DRIVERS)
def test_a_relation_on_the_wrong_driver_goes_red(dep: str, wrong: str) -> None:
    """WR-03: the 21 swaps the forward parity accepted (each cutout field on either other
    cutout gate, or on bore_hex eq 0) all fail the driver check."""
    op = "eq" if wrong == "bore_hex" else "gt"
    with pytest.raises(AssertionError, match="wrong or extra driver"):
        _assert_relations_name_the_driver_calc_obeys({dep: [(wrong, op, 0.0)]})


@pytest.mark.parametrize(("dep", "wrong"), _WRONG_DRIVERS)
def test_an_extra_gate_beside_the_right_driver_goes_red(dep: str, wrong: str) -> None:
    """WR-03: the same 21 as an extra AND-conjunct. A field then dims when an unrelated
    gate is off while `calc` uses it (or, for a second cutout gate, is never usable)."""
    op = "eq" if wrong == "bore_hex" else "gt"
    owner = _OWNER_OF[dep]
    with pytest.raises(AssertionError, match="wrong or extra driver"):
        _assert_relations_name_the_driver_calc_obeys(
            {dep: [(owner, "gt", 0.0), (wrong, op, 0.0)]})


def test_an_ignored_field_without_its_relation_goes_red() -> None:
    """RESEARCH Pitfall 2 (c): drop `spoke_fillet` from the declared set and its "ignored"
    sentence is undeclared. The first call proves the full set passes, so the red below is
    not an empty scan or an unrelated gap."""
    declared = frozenset(_relations())
    assert _assert_calc_ignores_only(declared) > 0
    with pytest.raises(AssertionError, match="no relation declares spoke_fillet"):
        _assert_calc_ignores_only(declared - {"spoke_fillet"})
