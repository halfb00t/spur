"""The shipped viewer in a real browser: what no Python test can see.

`TestClient` tests prove the API answers; none of them runs `app.js`. This module opens the
page the product ships, in Chrome Headless Shell, against a real `uvicorn`, and checks what
only a browser can: that WebGL2 exists (without it the page builds no form at all: app.js
creates its WebGLRenderer at load, before the form), that the first part is actually drawn,
that the scene holds as many triangles as the STL it was fed, that the download link appears
only after the model was shown, and that a click on `#dl-stl` saves the file under the name
the server gives the part, that a field the model says is inert is dimmed with its reason and
is still typed into and sent (L41), that a bore shape is picked from a select the schema
describes, derived from the fields on load and written back as flat fields (L42), and that a
link value its control cannot hold is sent and refused through the 422 path with the server's
text, and no part is drawn for it (L44).

It runs inside `make verify`'s `test` -- so also the pre-push hook, `make worktree.land` and
CI's `test (3.12)` -- and is excluded by name from `make verify.fast` and `make test-image`
(D-01): the commit-time slice has 30 s (L36) and the image installs no browser. `make test`
installs the headless shell first, through the `$(BROWSER)` stamp. Quick run:

    make test PYTEST_ARGS="tests/test_browser.py -n0 --no-cov -q"

One test function walks every step in order against one server (D-10), so a gate run
starts one `uvicorn` and one `BuildPool`; each step prints its name and seconds, and a
failure carries the step's name as a note. Costs and bars are in bench/RESULTS.md,
"Browser test of the viewer (Phase 21)".
"""

from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from collections.abc import Callable, Iterator

import pytest
from browser_session import (
    BUILD_WAIT_MS,
    GOLDEN_PATH,
    PNG_RATIO_BAR,
    STL_ROUTE,
    eval_bool,
    eval_inactive,
    eval_int,
    eval_opt_str,
    eval_pairs,
    eval_shown,
    eval_str,
    eval_str_list,
    expected_inactive,
    expected_pick,
    expected_shown,
    fixture_hash,
    fixture_hashes,
    flip_links,
    foreign_keys,
    launch,
    negative_link,
    number_above,
    record_api,
    serve,
    serve_stl_from,
    state_links,
    step,
    stl_triangles,
    sweep,
)
from playwright.sync_api import Page, Route, expect, sync_playwright

# app.js's scheduleUpdate() sends its request 350 ms after the event (`setTimeout(update, 350)`),
# so a request count taken sooner can pass before a stray request is sent (24 CX-05). The settle
# is that debounce plus margin for a runner about twice as slow as the dev host. The CX-05
# control (26-03) read the stray /api/info request 354 ms after its event here.
DEBOUNCE_SETTLE_MS = 1_000

# The four custom properties app.js reads for the scene (applyTheme, placeGrid): a rename in
# style.css leaves the page loading and the scene silently unthemed.
THEME_VARIABLES = ("--view-bg", "--grid", "--mesh", "--edge")

# A fresh canvas, not the page's own: it answers whether this browser can do WebGL2 at all.
WEBGL2_PROBE = """() => {
  const gl = document.createElement('canvas').getContext('webgl2');
  if (!gl) return null;
  const info = gl.getExtension('WEBGL_debug_renderer_info');
  return String(gl.getParameter(info ? info.UNMASKED_RENDERER_WEBGL : gl.RENDERER));
}"""

# Shared links for `link round trip`. Chosen from /api/schema (31 fields, 7 groups) by hand,
# each value inside its field's minimum/maximum/enum and none equal to the field's default,
# because gearQuery() drops a default and the sent query would then rightly lack it. Each
# spans three groups (Teeth, Body, Recess; A adds Bore) and holds an enum `select` at a
# non-default option (`root_shape`, `recess_sides`), plus the mate's `mate_teeth`, which is
# not a schema field. A is written out of schema order on purpose: gearQuery() emits schema
# order whatever order the hash used, so the comparison has to be on pairs, not on strings.
# The API answered 200 for both on 2026-10-10 (A with one warning, B with none).
LINK_A = (
    "mate_teeth=30&recess_sides=top&root_shape=trochoid&face_width=9&teeth=24&module=2&bore_d=10"
)
LINK_B = "mate_teeth=45&recess_sides=bottom&pressure_angle=20&face_width=6&teeth=31&module=1.5"
# C sets `teeth` to its schema default (read at test time) beside a non-default `face_width`.
LINK_C_OTHER = "face_width=8"

# Links the page must refuse (L44). Each token is one its control cannot hold AND the API
# refuses, so the page sends it as given. A number box also blanks ` 22`, `1_0`, `22.`, `5.`
# and `+5`, which the API refuses as written since L49, so none of those stands for a bad link
# here (the step `as-written sweep` owns them); select options compare case-sensitively, so
# `Trochoid` is as bad as `bogus`.
# The second member is the field the 422 names, or the mate box, which is not a schema field.
BAD_LINKS = (
    ("root_shape=bogus&teeth=22", "root_shape"),
    ("recess_sides=bogus", "recess_sides"),
    ("teeth=abc", "teeth"),
    ("mate_teeth=abc", "mate_teeth"),
    ("root_shape=Trochoid", "root_shape"),
)
# Blank is the default on the page (D-06), though the API answers 422 for an empty value.
BLANK_LINK = "teeth=&root_shape=&mate_teeth=&face_width=8"
UNKNOWN_KEY_LINK = "not_a_field=1&face_width=9"
# The box blanks `5.` and the API refuses it as written (L49): it is sent as given, answered
# 422 `number_as_written`, and the face_width field is marked. Before L49 this link built.
ACCEPTED_LINK = "face_width=5."

# Links for `root_fillet label`. 26 is the last tooth count where a trochoid request builds the
# hob root at the default module and angle, 27 the first where it falls back to radial
# (`rb <= rf`: the `26-applies-last` and `27-ignored-first` rows of tests/test_trochoid.py),
# and 23 asks for nothing. The label follows the root the server built, not the one asked for.
LABEL_LINKS = ("teeth=26&root_shape=trochoid", "teeth=27&root_shape=trochoid", "teeth=23")

# The refused pair under a hex bore: a 422 naming the gate and both fields (23-RESEARCH,
# reproduced), where `.invalid` and `.inactive` must coexist on the keyway fields (PD-07).
REFUSED_LINK = "bore_hex=6&keyway_width=3&keyway_depth=1.4"

MATE_VALUE = "() => document.querySelector('#mate-teeth').value"
FRAGMENT = "() => location.hash.slice(1)"
CONTROL_VALUE = "(n) => document.querySelector(`form#params [name=${n}]`).value"
CONTROL_INDEX = "(n) => document.querySelector(`form#params select[name=${n}]`).selectedIndex"
CONTROL_OPTIONS = "(n) => document.querySelector(`form#params select[name=${n}]`).options.length"


@pytest.fixture(scope="module")
def server(request: pytest.FixtureRequest) -> Iterator[str]:
    """One real server for the module.

    A subprocess and not an in-process thread: `spur.app.app` is a singleton whose lifespan
    and `dependency_overrides` every TestClient test on the same worker shares. Torn down
    in a `finally` inside `serve()`, so a failing assertion still kills the process group.
    A test that failed (a missing shell, no WebGL) built nothing, so the pool had not started
    its workers and the group floor is not asserted for it: one failure, reported once.
    """
    failed_before = request.session.testsfailed
    with serve(lambda: request.session.testsfailed == failed_before) as base:
        yield base


def _api_get(base: str, path: str, query: str) -> tuple[int, object]:
    """GET `path?query` and return the status with the JSON body, a 4xx included."""
    try:
        with urllib.request.urlopen(f"{base}{path}?{query}", timeout=30) as response:
            body: object = json.load(response)
            return response.status, body
    except urllib.error.HTTPError as error:
        with error:
            failure: object = json.load(error)
            return error.code, failure


def _schema_properties(base: str) -> dict[str, dict[str, object]]:
    status, schema = _api_get(base, "/api/schema", "")
    assert status == 200, f"/api/schema answered {status}"
    assert isinstance(schema, dict), "/api/schema is not an object"
    properties = schema["properties"]
    assert isinstance(properties, dict), "/api/schema has no properties"
    for name, prop in properties.items():
        assert isinstance(prop, dict), f"/api/schema property {name!r} is not an object"
    return properties


def _schema_selectors(base: str) -> list[dict[str, object]]:
    status, schema = _api_get(base, "/api/schema", "")
    assert status == 200, f"/api/schema answered {status}"
    assert isinstance(schema, dict), "/api/schema is not an object"
    selectors = schema.get("selectors")
    assert isinstance(selectors, list), "/api/schema has no `selectors` list (L42)"
    found: list[dict[str, object]] = []
    for selector in selectors:
        assert isinstance(selector, dict), f"/api/schema selector {selector!r} is not an object"
        found.append(selector)
    return found


def _title(properties: dict[str, dict[str, object]], name: str) -> str:
    # app.js buildForm(): `prop.title ?? name`.
    title = properties[name].get("title")
    return name if title is None else str(title)


def _expected_422(
    properties: dict[str, dict[str, object]], body: object
) -> tuple[set[str], list[str]]:
    """What app.js problems() must show for this 422 body: the marked titles and the texts.

    Marks every `detail[].loc[1]` and every `detail[].ctx.fields` that names a field. The
    text is `msg` with a leading "Value error, " removed, prefixed with "<title>: " only when
    `loc[1]` names a field (so the single-field `infeasible` error, whose loc is just
    ["query"], carries no prefix).
    """
    assert isinstance(body, dict), f"a 422 body that is not an object: {body!r}"
    detail = body["detail"]
    assert isinstance(detail, list), f"a 422 with no detail list: {body!r}"
    assert detail, "a 422 with an empty detail list"
    marked: set[str] = set()
    texts: list[str] = []
    for item in detail:
        assert isinstance(item, dict), f"a detail entry that is not an object: {item!r}"
        loc = item.get("loc")
        ctx = item.get("ctx")
        owner = loc[1] if isinstance(loc, list) and len(loc) > 1 else None
        named: list[object] = [owner]
        if isinstance(ctx, dict) and isinstance(ctx.get("fields"), list):
            named.extend(ctx["fields"])
        for name in named:
            if isinstance(name, str) and name in properties:
                marked.add(_title(properties, name))
        msg = str(item["msg"]).removeprefix("Value error, ")
        if isinstance(owner, str) and owner in properties:
            msg = f"{_title(properties, owner)}: {msg}"
        texts.append(msg)
    return marked, texts


def _follow_link(page: Page, fragment: str) -> str:
    """Open `#fragment` and return the query string of the /api/info request the page sent.

    The fragment must differ from the current one: assigning the same fragment fires no
    `hashchange`, and the request this waits for would never come (21-RESEARCH P5). The
    query is the page's own (defaults dropped, schema order), not one rebuilt here.
    """
    current = eval_str(page, "() => location.hash.slice(1)")
    assert current != fragment, f"the page is already on #{fragment}: no hashchange would fire"
    with page.expect_request(
        lambda request: "/api/info" in request.url, timeout=BUILD_WAIT_MS
    ) as sent:
        page.evaluate("(f) => { location.hash = f; }", fragment)
    return urllib.parse.urlsplit(sent.value.url).query


def _pairs(query: str) -> list[tuple[str, str]]:
    """A query string as its (name, value) pairs, sorted: order is not what a link means."""
    return sorted(urllib.parse.parse_qsl(query, keep_blank_values=True))


def _stl_requests(seen: list[str]) -> int:
    """How many /api/model.stl requests the recorded pages sent.

    The main page fulfils every STL request with the first build's bytes, so `data-triangles`
    cannot tell a default part from another there; the request count is the evidence.
    """
    return sum(1 for url in seen if urllib.parse.urlsplit(url).path == "/api/model.stl")


def _differing(
    got: list[tuple[str, str]], want: list[tuple[str, str]]
) -> list[tuple[tuple[str, str], tuple[str, str]]]:
    """The (got, want) pairs that differ, so a failure names the fields and not the form."""
    assert len(got) == len(want), f"{len(got)} form fields where {len(want)} were expected"
    return [(have, expected) for have, expected in zip(got, want, strict=True) if have != expected]


SELECT = "form#params label.selector select"
SELECTOR_PENDING = (
    "() => document.querySelector('form#params label.selector').classList.contains('pending')"
)
SELECT_BORDER = "() => getComputedStyle(document.querySelector('form#params label.selector select')).borderTopStyle"  # noqa: E501
SELECT_FOCUSED = "() => document.activeElement === document.querySelector('form#params label.selector select')"  # noqa: E501
PENDING_AT = (
    "(i) => document.querySelectorAll('form#params label.selector')[i]"
    ".classList.contains('pending')"
)
SELECT_DESCRIBED_BY = (
    "(f) => document.querySelector('form#params label.selector select').getAttribute("
    "'aria-describedby') === document.querySelector("
    "`form#params label.field:has([name=${f}]) .reason`).id"
)


def _pick(page: Page, label: str) -> None:
    """Choose `label` in the first selector as a user does: focus it; `input` then `change` fire."""
    select = page.locator(SELECT).first
    select.focus()
    select.select_option(label=label)


def _writing_pick(
    page: Page,
    chooser: dict[str, object],
    properties: dict[str, dict[str, object]],
    label: str,
    current: str,
    stash: dict[str, str],
) -> tuple[str, dict[str, str]]:
    """Pick `label` on a page showing `current` and check it did what the rule says (L42).

    Returns the page's fragment afterwards and the stash the rule leaves. Every expectation is
    `expected_pick()`'s, the schema's second implementation of `pick()`; the page must send the
    one query it predicts, write the same fragment, show the label and dim what the fields say.
    """
    rule = expected_pick(chooser, properties, label, current, stash)
    assert rule.sent is not None, f"bore shape, #{current} + {label}: the rule says pending"
    with page.expect_request(
        lambda request: "/api/info" in request.url, timeout=BUILD_WAIT_MS
    ) as picked:
        _pick(page, label)
        # A fast red: the writes and the re-derive ran in the pick's own dispatch, so a page
        # that left the pick pending fails here and not after BUILD_WAIT_MS.
        assert not eval_bool(page, SELECTOR_PENDING), (
            f"bore shape, #{current} + {label}: the pick was left pending"
        )
    sent = urllib.parse.urlsplit(picked.value.url).query
    assert _pairs(sent) == _pairs(rule.sent), (
        f"bore shape, #{current} + {label}: the page sent {sent!r}, the rule says {rule.sent!r}"
    )
    fragment = eval_str(page, FRAGMENT)
    assert _pairs(fragment) == _pairs(rule.sent), (
        f"bore shape, #{current} + {label}: the fragment is {fragment!r}, the rule says "
        f"{rule.sent!r}"
    )
    assert eval_shown(page)[0] == label, (
        f"bore shape, #{current} + {label}: shows {eval_shown(page)}"
    )
    assert eval_inactive(page) == expected_inactive(properties, fragment), (
        f"bore shape, #{current} + {label}: the dimmed set is not the fields'"
    )
    print(f"bore shape: #{current} + {label} -> sent {sent!r}")
    return fragment, dict(rule.stash)


def _pending_pick(
    page: Page,
    chooser: dict[str, object],
    properties: dict[str, dict[str, object]],
    label: str,
    current: str,
    stash: dict[str, str],
) -> None:
    """Pick `label` where the rule says it cannot be made true, and check nothing moved (D-09).

    Nothing is written and no request is awaited: the form's pairs and the fragment are what
    they were. The select keeps the picked label under `.pending` with a dashed border and
    keeps the focus, the field that needs a number says so in its own reason row, which is its
    `aria-describedby` and the select's, and the relations still read the fields and not the
    select (D-11).
    """
    rule = expected_pick(chooser, properties, label, current, stash)
    assert rule.sent is None, f"bore shape, #{current} + {label}: the rule says it writes"
    pairs_before = eval_pairs(page)
    fragment_before = eval_str(page, FRAGMENT)
    _pick(page, label)
    assert eval_pairs(page) == pairs_before, f"bore shape, pending {label}: a field was written"
    assert eval_str(page, FRAGMENT) == fragment_before, (
        f"bore shape, pending {label}: the fragment moved"
    )
    assert eval_shown(page)[0] == label, (
        f"bore shape, pending {label}: the select snapped back to {eval_shown(page)}"
    )
    assert eval_bool(page, SELECTOR_PENDING), f"bore shape, pending {label}: wrapper not .pending"
    # 24 WR-01: the focus stays on the select. A focus() onto the field ended a keyboard walk
    # at the first pending step on Blink and Gecko (Windows, Linux), where an arrow key commits
    # the option and fires `input`. The engines' arrow handling is not driven here (Chrome
    # Headless Shell on macOS opens the popup instead); the property that is the page's to
    # keep is.
    assert eval_bool(page, SELECT_FOCUSED), (
        f"bore shape, pending {label}: the focus left the select for "
        f"{eval_str(page, '() => document.activeElement.name ?? document.activeElement.tagName')!r}"
    )
    assert eval_bool(page, SELECT_DESCRIBED_BY, rule.field), (
        f"bore shape, pending {label}: the select is not described by {rule.field}'s reason row"
    )
    reason = page.locator(f"form#params label.field:has([name={rule.field}]) .reason")
    expect(reason).to_have_text(rule.note)
    assert eval_bool(
        page,
        "(f) => document.querySelector(`form#params [name=${f}]`).getAttribute("
        "'aria-describedby') === document.querySelector("
        "`form#params label.field:has([name=${f}]) .reason`).id",
        rule.field,
    ), f"bore shape, pending {label}: {rule.field} is not described by its reason row"
    assert eval_inactive(page) == expected_inactive(properties, current), (
        f"bore shape, pending {label}: the select changed what the relations dim"
    )
    assert eval_str(page, SELECT_BORDER) == "dashed", (
        f"bore shape, pending {label}: the pending select is not drawn dashed"
    )
    print(f"bore shape: #{current} + {label} -> pending: {rule.field}: {rule.note}")


def _complete_pending(
    page: Page,
    chooser: dict[str, object],
    properties: dict[str, dict[str, object]],
    label: str,
    current: str,
    stash: dict[str, str],
    empty_first: bool = False,
) -> tuple[str, dict[str, str], int]:
    """Type the number a pending pick of `label` asks for, until the pick writes (D-09, CX-01).

    Each number typed clears the threshold the schema sets, through `number_above()`, never a
    literal. A pick still short of another number stays pending on that field with its note,
    and only the typed field moves; the pick that holds writes what it held back -- the zeros
    and the stashed strings `expected_pick()` plans from the completed state -- sends that one
    query, shows the label and leaves nothing pending. With `empty_first`, the asked field is
    first emptied: an empty box reads as the field's default (D-18), which is not a typed
    number, so the pick must stay pending with its note and nothing else may move (WR-02).
    Returns the query sent, the stash and how many numbers were typed.
    """
    typed_count = 0
    while True:
        rule = expected_pick(chooser, properties, label, current, stash)
        assert rule.sent is None, f"bore shape, completing {label}: the rule says it writes"
        if empty_first:
            empty_first = False
            boxes = dict(eval_pairs(page))
            with page.expect_request(
                lambda request: "/api/info" in request.url, timeout=BUILD_WAIT_MS
            ):
                page.locator(f"form#params [name={rule.field}]").fill("")
            emptied = {name for name, value in eval_pairs(page) if boxes[name] != value}
            assert emptied == {rule.field}, (
                f"bore shape, {label} with {rule.field} emptied: {sorted(emptied)} moved"
            )
            assert eval_bool(page, SELECTOR_PENDING), (
                f"bore shape, {label} with {rule.field} emptied: the pick completed on the default"
            )
            assert eval_shown(page)[0] == label, (
                f"bore shape, {label} with {rule.field} emptied: shows {eval_shown(page)}"
            )
            reason = page.locator(f"form#params label.field:has([name={rule.field}]) .reason")
            expect(reason).to_have_text(rule.note)
            print(f"bore shape: {rule.field} emptied, {label} still pending")
        typed_value = number_above(properties, rule.field, _threshold(chooser, label, rule.field))
        completed = urllib.parse.urlencode(
            [(k, v) for k, v in urllib.parse.parse_qsl(current) if k != rule.field]
            + [(rule.field, typed_value)]
        )
        after = expected_pick(chooser, properties, label, completed, stash)
        before = dict(eval_pairs(page))
        with page.expect_request(
            lambda request: "/api/info" in request.url, timeout=BUILD_WAIT_MS
        ) as typed:
            page.locator(f"form#params [name={rule.field}]").fill(typed_value)
        typed_count += 1
        sent = urllib.parse.urlsplit(typed.value.url).query
        if after.sent is None:
            moved = {name for name, value in eval_pairs(page) if before[name] != value}
            assert moved == {rule.field}, (
                f"bore shape, completing {label}: typed {rule.field}, but {sorted(moved)} moved"
            )
            assert eval_shown(page)[0] == label, (
                f"bore shape, completing {label}: shows {eval_shown(page)} with {after.field} "
                "still missing"
            )
            assert eval_bool(page, SELECTOR_PENDING), (
                f"bore shape, completing {label}: not pending on {after.field}"
            )
            reason = page.locator(f"form#params label.field:has([name={after.field}]) .reason")
            expect(reason).to_have_text(after.note)
            print(
                f"bore shape: typed {rule.field}={typed_value}, {label} still pending: "
                f"{after.field}: {after.note}"
            )
            current = completed
            continue
        assert _pairs(sent) == _pairs(after.sent), (
            f"bore shape, completing {label}: typed {rule.field}={typed_value}, the page sent "
            f"{sent!r}, the rule says {after.sent!r}"
        )
        fragment = eval_str(page, FRAGMENT)
        assert _pairs(fragment) == _pairs(after.sent), (
            f"bore shape, completing {label}: the fragment is {fragment!r}, the rule says "
            f"{after.sent!r}"
        )
        assert eval_shown(page)[0] == label, (
            f"bore shape, completing {label}: shows {eval_shown(page)}"
        )
        assert not eval_bool(page, SELECTOR_PENDING), (
            f"bore shape, completing {label}: the typed number left the select pending"
        )
        assert eval_str(page, SELECT_BORDER) != "dashed", (
            f"bore shape, completing {label}: the typed number left the select drawn pending"
        )
        assert eval_inactive(page) == expected_inactive(properties, after.sent), (
            f"bore shape, completing {label}: the dimmed set is not the fields'"
        )
        print(f"bore shape: completed {label} with {typed_count} number(s) -> sent {sent!r}")
        return sent, dict(after.stash), typed_count


def _gt_thresholds(selector: dict[str, object], label: str) -> list[tuple[str, str]]:
    """The `gt` conditions of the option `label`, as (field, threshold) pairs the link can carry.

    Read from the schema (L42), formatted with `:g` as `negative_link` is. A link made of them
    leaves every one of those conditions false, so a pick of `label` from it must be typed
    through each field in turn (CX-01).
    """
    options = selector["options"]
    assert isinstance(options, list), f"the selector's options {options!r} are not a list"
    for option in options:
        assert isinstance(option, dict), f"an option that is not an object: {option!r}"
        if option["label"] != label:
            continue
        when = option["when"]
        assert isinstance(when, list), f"an option whose when is {when!r}, not a list"
        pairs: list[tuple[str, str]] = []
        for condition in when:
            assert isinstance(condition, dict), f"a condition that is not an object: {condition!r}"
            if condition["op"] != "gt":
                continue
            field, value = condition["field"], condition["value"]
            assert isinstance(field, str), f"a condition field that is not a str: {field!r}"
            assert isinstance(value, int | float), f"{label}: a threshold {value!r}, not a number"
            assert not isinstance(value, bool), f"{label}: a gt threshold {value!r}, a bool"
            pairs.append((field, f"{float(value):g}"))
        return pairs
    raise AssertionError(f"{label!r} is not an option of the selector")


def _threshold(selector: dict[str, object], label: str, field: str) -> float:
    """The `gt` threshold the option `label` sets on `field`, read from the schema (L42)."""
    for name, value in _gt_thresholds(selector, label):
        if name == field:
            return float(value)
    raise AssertionError(f"{label} sets no gt threshold on {field}")


def _default_clears(
    properties: dict[str, dict[str, object]], selector: dict[str, object], label: str, field: str
) -> bool:
    """Whether `field`'s schema default is above the threshold `label` sets on it.

    Exactly then an emptied box, which the page reads as the default (D-18), would complete a
    pending pick of `label` with a number nobody typed (WR-02); the case is worth driving only
    where it can go wrong.
    """
    default = properties[field].get("default")
    assert isinstance(default, int | float), f"{field}: default {default!r} is not a number"
    assert not isinstance(default, bool), f"{field}: default {default!r} is a bool"
    return float(default) > _threshold(selector, label, field)


# The fields the page marks `.invalid`, by name, as the 422 path of app.js problems() sets them.
INVALID_NAMES = (
    "() => [...document.querySelectorAll('form#params label.field.invalid [name]')]"
    ".map(e => e.name)"
)


def _named_fields(selector: dict[str, object]) -> set[str]:
    """Every field any option of the selector names in a condition, read from the schema (L42)."""
    options = selector["options"]
    assert isinstance(options, list), f"the selector's options {options!r} are not a list"
    named: set[str] = set()
    for option in options:
        assert isinstance(option, dict), f"an option that is not an object: {option!r}"
        when = option["when"]
        assert isinstance(when, list), f"an option whose when is {when!r}, not a list"
        for condition in when:
            assert isinstance(condition, dict), f"a condition that is not an object: {condition!r}"
            field = condition["field"]
            assert isinstance(field, str), f"a condition field that is not a str: {field!r}"
            named.add(field)
    return named


def _golden_records() -> dict[str, str]:
    """The committed pin, read and never written: only `make golden.regen` writes it (D-09)."""
    document: object = json.loads(GOLDEN_PATH.read_text())
    assert isinstance(document, dict), "golden_requests.json is not an object"
    records = document["records"]
    assert isinstance(records, dict), "golden_requests.json has no records object"
    pinned: dict[str, str] = {}
    for name, query in records.items():
        assert isinstance(query, str), f"golden_requests.json: {name!r} is {query!r}, not a str"
        pinned[name] = query
    return pinned


def _assert_link_applied(
    page: Page,
    where: str,
    link: str,
    sent: str,
    default_pairs: list[tuple[str, str]],
    kept: list[tuple[str, str]],
) -> None:
    """The link reached the form, and what the page sent and wrote back is `kept`.

    Every form field the link names reads that exact string, every other field reads what
    the fresh default load read, and `#mate-teeth` reads the link's `mate_teeth`. `kept` is
    the link minus whatever gearQuery() drops as a default; the query the page sent and the
    fragment update() rewrote must both equal it, as sorted pairs.
    """
    wanted = dict(urllib.parse.parse_qsl(link))
    fields = {name for name, _ in default_pairs}
    unknown = set(wanted) - fields - {"mate_teeth"}
    assert not unknown, f"{where}: the link names {sorted(unknown)}, which are no form fields"
    expected = [(name, wanted.get(name, default)) for name, default in default_pairs]
    form = eval_pairs(page)
    assert form == expected, (
        f"{where}: the form differs from the link on {_differing(form, expected)}"
    )
    mate = eval_str(page, MATE_VALUE)
    assert mate == wanted.get("mate_teeth", ""), (
        f"{where}: #mate-teeth reads {mate!r}, the link says {wanted.get('mate_teeth')!r}"
    )
    assert _pairs(sent) == kept, f"{where}: the page sent {_pairs(sent)}, expected {kept}"
    fragment = eval_str(page, FRAGMENT)
    assert _pairs(fragment) == kept, (
        f"{where}: update() wrote the fragment {_pairs(fragment)}, expected {kept}"
    )


def _wait_until_parked(page: Page, parked: list[Route]) -> None:
    # Under the sync API a route handler runs only while a Playwright call is in flight, so
    # a sleep loop would never see it fire. A round trip per turn lets it run; the bound is
    # a build's, and the signal is the request itself, not elapsed time.
    deadline = time.monotonic() + BUILD_WAIT_MS / 1000
    while not parked:
        assert time.monotonic() < deadline, (
            f"the page asked for no STL within {BUILD_WAIT_MS} ms of loading"
        )
        page.evaluate("0")


def test_the_oracle_reads_a_link_as_the_page_does() -> None:
    """IN-06, IN-01: `expected_inactive` is the second evaluator, so it has to resolve a link
    and word a reason exactly as app.js does. No browser: a hand-written schema, so a
    repeated key or a threshold of 1e6 need not exist in the real one. Red on a last-wins
    repeated key, a blank first value that is not the default, or a reason whose number
    differs from JavaScript's `${value}`, or a threshold JavaScript writes with an exponent
    (23-REVIEW IN-11, read from node: `${-0}` is `0`, `${1e21}` is `1e+21`, `${1e-7}` is
    `1e-7`)."""
    properties: dict[str, dict[str, object]] = {
        "gate": {"title": "Gate", "default": 0},
        "tiny": {"title": "Tiny", "default": 0},
        "huge": {"title": "Huge", "default": 0},
        "dep": {"title": "Dep", "default": 1, "enabled_when": [
            {"field": "gate", "op": "eq", "value": 0}]},
    }
    # URLSearchParams.get is first-wins: the page sees gate=0 and leaves dep live.
    assert expected_inactive(properties, "gate=0&gate=6") == {}
    assert expected_inactive(properties, "gate=6&gate=0") == {"dep": "Needs Gate = 0"}
    # A blank first value is a present, empty box: the default (0), not the second pair.
    assert expected_inactive(properties, "gate=&gate=6") == {}
    assert expected_inactive(properties, "gate=6") == {"dep": "Needs Gate = 0"}
    # Each pair was read from node: `${1e6}` is 1000000 and `${1e-5}` is 0.00001, where
    # Python's `:g` wrote 1e+06 and 1e-05. JavaScript stays positional from 1e-6 up to 1e21.
    for threshold, written in ((0, "0"), (-0.0, "0"), (1, "1"), (1.0, "1"), (0.05, "0.05"),
                               (1e6, "1000000"), (1e-5, "0.00001"), (1e-6, "0.000001"),
                               (1e16, "10000000000000000")):
        properties["dep"]["enabled_when"] = [{"field": "gate", "op": "gt", "value": threshold}]
        assert expected_inactive(properties, "gate=0") == {"dep": f"Needs Gate above {written}"}
    for beyond in (1e21, 1e-7):
        properties["dep"]["enabled_when"] = [{"field": "gate", "op": "gt", "value": beyond}]
        with pytest.raises(AssertionError, match="exponent"):
            expected_inactive(properties, "gate=0")


def test_a_fixture_link_refuses_a_value_no_person_would_type() -> None:
    """21-REVIEW IN-02: `fixture_hash` writes `str(value)` per param, which is right for an
    int, a float or a str. `str(True)` is `True`, which no person types into a link, and a
    bool or null field would pin a wrong query in the golden file. No browser, no fixture."""
    for bad in (True, None):
        with pytest.raises(AssertionError, match="'x'"):
            fixture_hash({"x": bad}, None)
    link = fixture_hash({"teeth": 19, "module": 1.75, "root_shape": "trochoid"}, None)
    assert link == "teeth=19&module=1.75&root_shape=trochoid"


def test_the_shipped_viewer_in_a_real_browser(server: str) -> None:
    """Opens the shipped page and draws the first part; costs are in bench/RESULTS.md."""
    properties = _schema_properties(server)
    selectors = _schema_selectors(server)
    field_count = len(properties)
    parked: list[Route] = []
    seen: list[str] = []

    with sync_playwright() as pw:
        # In the body, not a fixture: a missing shell must be a FAILED test with the install
        # command in its message, not an ERROR and not a skip (D-02, D-07).
        browser = launch(pw)
        try:
            page = record_api(browser.new_page(), seen)

            # D-14, BS-2: no page may send, and no link may carry, a key the form does not own.
            # `GearParams` is the form's whole vocabulary; the API takes two parameters beside
            # it, `ModelQuery.quality` and `InfoQuery.mate_teeth` (app.py), and the hash carries
            # `mate_teeth` but never `quality`. The rest is read from the schema, so a field
            # added later is allowed with no edit here and a selector's state, which is not a
            # field, is refused wherever it leaks.
            allowed_query = set(properties) | {"quality", "mate_teeth"}
            allowed_hash = set(properties) | {"mate_teeth"}

            def no_foreign_key() -> None:
                leaked = foreign_keys(seen, allowed_query)
                assert not leaked, f"a request carried a key GearParams lacks: {leaked}"
                keys = [
                    key
                    for key, _ in urllib.parse.parse_qsl(
                        eval_str(page, FRAGMENT), keep_blank_values=True
                    )
                ]
                stray = [key for key in keys if key not in allowed_hash]
                assert not stray, f"the main page's hash carries {stray}, not a field of the form"

            with step("webgl2", no_foreign_key):
                renderer = eval_opt_str(page, WEBGL2_PROBE)
                assert renderer is not None, (
                    "this browser gives no WebGL2 context: the viewer builds no form without "
                    "WebGL (app.js creates its renderer before it builds the form)"
                )
                print(f"webgl2 renderer: {renderer}")

            # A lambda, never the bound `parked.append`: Playwright rejects a builtin
            # method as a handler at run time, although mypy accepts it.
            page.route(STL_ROUTE, lambda route: parked.append(route))
            page.goto(server + "/")

            with step("form built", no_foreign_key):
                expect(page.locator("form#params [name]")).to_have_count(field_count)
                _wait_until_parked(page, parked)
                # The fresh default load: empty hash, readHash() and update() have run.
                default_pairs = eval_pairs(page)
                assert page.locator("#dl-stl").get_attribute("href") is None, (
                    "the STL link has an href before any STL was shown"
                )

            with step("form from schema", no_foreign_key):
                # Every expectation is the schema's, read above at test time. A property with
                # no group sits under "Other" (app.js buildForm), and a group opens its
                # fieldset at its first property, so two properties of one group are one legend.
                groups: dict[str, list[str]] = {}
                for name, prop in properties.items():
                    group = prop.get("group")
                    groups.setdefault("Other" if group is None else str(group), []).append(name)
                expected_names = [name for names in groups.values() for name in names]
                assert expected_names, "/api/schema holds no properties: nothing to compare"

                # Lists, not sets: the order is the form's, and a reversed form is a bug.
                rendered = eval_str_list(
                    page,
                    "() => [...document.querySelectorAll('form#params [name]')].map(e => e.name)",
                )
                assert rendered == expected_names, (
                    f"form fields {rendered} differ from the schema's, grouped: {expected_names}"
                )
                legends = page.locator("form#params legend").all_text_contents()
                assert legends == list(groups), (
                    f"form legends {legends} differ from the schema's groups {list(groups)}"
                )
                shown = page.locator("form#params label.field .name").all_text_contents()
                titles = [_title(properties, name) for name in expected_names]
                assert shown == titles, f"field names {shown} differ from the titles {titles}"
                for variable in THEME_VARIABLES:
                    value = eval_str(
                        page,
                        "(v) => getComputedStyle(document.documentElement)"
                        ".getPropertyValue(v).trim()",
                        variable,
                    )
                    assert value != "", f"the custom property {variable} is empty on :root"
                print(f"schema: {len(expected_names)} fields in {len(groups)} groups")

            with step("first build drawn", no_foreign_key):
                canvas = page.locator("#canvas")
                blank = canvas.screenshot()  # same element, same page, STL request parked
                with page.expect_response(
                    lambda response: "/api/model.stl" in response.url, timeout=BUILD_WAIT_MS
                ) as served:
                    parked[0].continue_()
                expect(page.locator("#dl-stl")).to_have_attribute(
                    "href", re.compile(r"^api/model\.stl"), timeout=BUILD_WAIT_MS
                )
                drawn = canvas.screenshot()
                stl = served.value.body()

                ratio = len(drawn) / len(blank)
                declared = canvas.get_attribute("data-triangles")
                header = stl_triangles(stl)
                print(
                    f"canvas PNG blank {len(blank)} B, drawn {len(drawn)} B, ratio {ratio:.2f} "
                    f"(bar {PNG_RATIO_BAR}); data-triangles {declared}, STL header {header}"
                )
                assert ratio >= PNG_RATIO_BAR, (
                    f"the canvas looks undrawn: PNG {len(drawn)} B against a blank {len(blank)} B "
                    f"is {ratio:.2f}x, bar {PNG_RATIO_BAR}"
                )
                assert declared is not None, "the scene reported no data-triangles"
                assert int(declared) == header, (
                    f"the scene holds {declared} triangles, the STL header declares {header}"
                )

            with step("href after showModel", no_foreign_key):
                # An STL too short to parse makes showModel throw. The link must still have
                # no href: it is set only after showModel returns (app.js update()).
                page.unroute(STL_ROUTE)
                page.route(STL_ROUTE, lambda route: route.fulfill(body=b"\0" * 10))
                page.evaluate("() => { location.hash = 'teeth=23'; }")
                expect(page.locator("#messages .error")).to_contain_text("Request failed")
                assert page.locator("#dl-stl").get_attribute("href") is None, (
                    "the STL link has an href although showModel failed on the body"
                )
                assert page.locator("#dl-stl").get_attribute("aria-disabled") == "true"
                kept = canvas.get_attribute("data-triangles")
                assert kept == declared, (
                    f"a failed build changed data-triangles from {declared} to {kept}"
                )

            serve_stl_from(page, stl)

            with step("invalid field marked", no_foreign_key):
                # Both marking paths of app.js problems(): `bore_flat=3` is the single-field
                # `infeasible` error (marked through ctx.fields), `teeth=2` a field-level range
                # error (marked through loc[1]). The expectation is the API's own 422 body for
                # the very query the page sent, never a literal.
                for fragment in ("bore_flat=3", "teeth=2"):
                    sent = _follow_link(page, fragment)
                    status, body = _api_get(server, "/api/info", sent)
                    assert status == 422, f"/api/info?{sent} answered {status}, not 422"
                    marked, texts = _expected_422(properties, body)
                    assert marked, f"/api/info?{sent} names no schema field: nothing to mark"
                    for text in texts:
                        assert any(title in text for title in marked), (
                            f"the message {text!r} names none of {sorted(marked)}"
                        )
                    # On the text, never on the element count: the previous state's error is
                    # still on screen until this one replaces it (21-RESEARCH P6).
                    expect(page.locator("#messages .error")).to_have_text(texts)
                    invalid = set(page.locator("label.field.invalid .name").all_text_contents())
                    assert invalid == marked, (
                        f"#{fragment}: marked {sorted(invalid)}, the 422 names {sorted(marked)}"
                    )
                    kept = canvas.get_attribute("data-triangles")
                    assert kept == declared, (
                        f"a 422 changed data-triangles from {declared} to {kept}"
                    )
                    print(f"422 #{fragment}: marked {sorted(marked)}, text {texts}")

                # update() clears the class before each request, so a valid link leaves none.
                sent = _follow_link(page, "teeth=23")
                expect(page.locator("#dl-stl")).to_have_attribute(
                    "href", f"api/model.stl?{sent}", timeout=BUILD_WAIT_MS
                )
                assert page.locator("label.field.invalid").count() == 0, (
                    "a valid link left a field marked invalid"
                )

            with step("warning rendered", no_foreign_key):
                # Equality of ordered lists, against links whose API answer holds two warnings,
                # one warning and none: the two-warning link is what separates "renders the
                # list" from "renders something that contains the first warning". The STL is
                # fulfilled from the first build (serve_stl_from), so nothing here builds.
                counts: list[int] = []
                for fragment, at_least in (
                    ("module=1&pressure_angle=14.5", 2),
                    ("bore_hex=6&bore_d=12", 1),
                    ("teeth=23", 0),
                ):
                    sent = _follow_link(page, fragment)
                    status, body = _api_get(server, "/api/info", sent)
                    assert status == 200, f"/api/info?{sent} answered {status}, not 200"
                    assert isinstance(body, dict), f"/api/info?{sent} is not an object"
                    warnings = body["warnings"]
                    assert isinstance(warnings, list), f"/api/info?{sent} has no warnings list"
                    if at_least == 0:
                        assert warnings == [], f"/api/info?{sent} warns: {warnings}"
                    else:
                        assert len(warnings) >= at_least, (
                            f"/api/info?{sent} holds {len(warnings)} warnings, "
                            f"expected at least {at_least}"
                        )
                    # The page shows the warnings before it asks for the STL, so the href
                    # for this very query means the whole update finished: the messages are
                    # this link's, not an earlier or aborted one's.
                    expect(page.locator("#dl-stl")).to_have_attribute(
                        "href", f"api/model.stl?{sent}", timeout=BUILD_WAIT_MS
                    )
                    rendered_warnings = page.locator("#messages .warning").all_text_contents()
                    assert rendered_warnings == warnings, (
                        f"#{fragment}: rendered warnings {rendered_warnings} differ from "
                        f"the API's {warnings}"
                    )
                    assert page.locator("#messages .error").count() == 0, (
                        f"#{fragment}: an error is shown beside the warnings"
                    )
                    counts.append(len(warnings))
                print(f"warnings per link (two, one, none expected): {counts}")

            with step("link round trip", no_foreign_key):
                # The three places app.js sets form values programmatically: the load
                # (readHash), the `hashchange` listener and #reset. The wait on each is the
                # /api/info request itself, captured around the action: readHash(), the
                # fragment rewrite and the request all happen before any response, whereas an
                # empty #status or the mere presence of an href is already true before the
                # 350 ms debounce fires (21-RESEARCH P6).
                pairs_a, pairs_b = _pairs(LINK_A), _pairs(LINK_B)
                for link in (LINK_A, LINK_B):
                    status, _ = _api_get(server, "/api/info", link)
                    assert status == 200, f"the link #{link} answers {status}, not 200"

                # fresh load: a new page opened on the link.
                page2 = record_api(browser.new_page(), seen)
                try:
                    serve_stl_from(page2, stl)
                    with page2.expect_request(
                        lambda request: "/api/info" in request.url, timeout=BUILD_WAIT_MS
                    ) as info_request:
                        page2.goto(f"{server}/#{LINK_A}")
                    _assert_link_applied(
                        page2,
                        "link round trip, fresh load",
                        LINK_A,
                        urllib.parse.urlsplit(info_request.value.url).query,
                        default_pairs,
                        pairs_a,
                    )
                finally:
                    page2.close()

                # hashchange: a link assigned on the page that is already open. The fragment
                # must differ from the current one or no event fires (_follow_link asserts it).
                sent_b = _follow_link(page, LINK_B)
                _assert_link_applied(
                    page, "link round trip, hashchange", LINK_B, sent_b, default_pairs, pairs_b
                )

                # Default dropped: the link names `teeth` at its schema default beside a
                # non-default field. The form shows the default; the page does not send it.
                teeth_default = properties["teeth"]["default"]
                assert isinstance(teeth_default, int), f"teeth default {teeth_default!r}: no int"
                assert not isinstance(teeth_default, bool), "the teeth default is a bool"
                link_c = f"teeth={teeth_default}&{LINK_C_OTHER}"
                sent_c = _follow_link(page, link_c)
                assert "teeth" not in dict(_pairs(sent_c)), (
                    f"link round trip, default dropped: the page sent the default {sent_c!r}"
                )
                _assert_link_applied(
                    page,
                    "link round trip, default dropped",
                    link_c,
                    sent_c,
                    default_pairs,
                    _pairs(LINK_C_OTHER),
                )

                # Reset: back to exactly the fresh default load.
                assert eval_str(page, FRAGMENT) != "", "link round trip, Reset: nothing to clear"
                with page.expect_request(
                    lambda request: "/api/info" in request.url, timeout=BUILD_WAIT_MS
                ) as info_request:
                    page.locator("#reset").click()
                reset_query = urllib.parse.urlsplit(info_request.value.url).query
                assert reset_query == "", f"link round trip, Reset: the page sent {reset_query!r}"
                assert eval_str(page, FRAGMENT) == "", "link round trip, Reset: fragment left"
                assert eval_str(page, MATE_VALUE) == "", "link round trip, Reset: mate left"
                after = eval_pairs(page)
                assert after == default_pairs, (
                    "link round trip, Reset: the form differs from the fresh default load on "
                    f"{_differing(after, default_pairs)}"
                )

            with step("golden sweep", no_foreign_key):
                # What only a browser can prove: the server's acceptance of every fixture
                # record is tests/regression's, but what the form SENDS for each link is the
                # page's. Each record's link goes through location.hash on one page whose STL
                # route is aborted, so nothing is built (D-08); the sent api/info query must
                # equal the committed pin. Phases 23-24 change the form and must leave this
                # file's diff empty (D-09). Beside the query, the fields the page dimmed for
                # the link, with their reasons, must equal the Python evaluator's over
                # /api/schema (23 D-14, D-16): two implementations that share no code agreeing
                # on every record. The query pin is unchanged. L42, D-06, D-13: the option each
                # selector shows is read in the same pass and must equal the schema's own
                # derivation, so the shown option with the unchanged query pin is the proof that
                # loading never writes (SC2): a page that wrote a field to make an option true
                # would move a query.
                pinned = _golden_records()
                hashes = fixture_hashes()
                assert set(pinned) == set(hashes), (
                    "golden sweep: the pin and the fixture name different records: only in "
                    f"the pin {sorted(set(pinned) - set(hashes))}, only in the fixture "
                    f"{sorted(set(hashes) - set(pinned))}; run `make golden.regen`"
                )
                sweep_page = record_api(browser.new_page(), seen)
                try:
                    swept = sweep(sweep_page, server, hashes)
                finally:
                    sweep_page.close()
                moved = {
                    name: (pinned[name], swept[name].query)
                    for name in hashes
                    if swept[name].query != pinned[name]
                }
                detail = "; ".join(
                    f"{name}: expected {want!r}, sent {got!r}"
                    for name, (want, got) in moved.items()
                )
                assert not moved, f"golden sweep: the form sends other queries: {detail}"
                wanted_dim = {
                    name: expected_inactive(properties, link) for name, link in hashes.items()
                }
                assert any(wanted_dim.values()), (
                    "golden sweep: no record expects a dimmed field, so a schema with no "
                    "relation would pass this step"
                )
                dim_differs = "; ".join(
                    f"{name}: the page dims {swept[name].inactive}, the schema says {want}"
                    for name, want in wanted_dim.items()
                    if swept[name].inactive != want
                )
                assert not dim_differs, f"golden sweep: the dimmed sets differ: {dim_differs}"
                wanted_shown = {
                    name: expected_shown(selectors, properties, link)
                    for name, link in hashes.items()
                }
                assert all(option for shown in wanted_shown.values() for option in shown), (
                    "golden sweep: a fixture link derives no option for a selector, so the "
                    "total grid of D-02 does not cover the fixture"
                )
                assert len(set(wanted_shown.values())) >= 2, (
                    "golden sweep: every link derives the same option, so a select stuck on "
                    "one option would pass this step"
                )
                shown_differs = "; ".join(
                    f"{name}: the page shows {swept[name].shown}, the schema says {want}"
                    for name, want in wanted_shown.items()
                    if swept[name].shown != want
                )
                assert not shown_differs, f"golden sweep: the shown options differ: {shown_differs}"
                distinct_queries = len({s.query for s in swept.values()})
                distinct_dims = len({tuple(sorted(s.inactive.items())) for s in swept.values()})
                print(
                    f"golden sweep: {len(swept)} records, {distinct_queries} distinct queries, "
                    f"{distinct_dims} distinct dimmed sets"
                )
                shown_counts = Counter(shown[0] for shown in wanted_shown.values())
                print(f"golden sweep: shown {dict(sorted(shown_counts.items()))}")

            with step("inert fields", no_foreign_key):
                # The roadmap's own link: #spoke_count=0&hub_d=40, a value the model says does
                # nothing, shared and opened fresh (L41, D-17). A fresh page, because a fragment
                # assigned after the load can be erased before buildForm() returns (22-RESEARCH
                # Pitfall 2), so it rides the goto URL; serve_stl_from, so nothing builds.
                # What must hold is that the field is dimmed AND still a field: visible,
                # editable, holding the link's value, and sent. The expected set comes from
                # /api/schema through the Python evaluator, never a literal (D-14).
                fresh = record_api(browser.new_page(), seen)
                try:
                    serve_stl_from(fresh, stl)
                    with fresh.expect_request(
                        lambda request: "/api/info" in request.url, timeout=BUILD_WAIT_MS
                    ) as loaded:
                        fresh.goto(server + "/#spoke_count=0&hub_d=40")
                    load_query = urllib.parse.urlsplit(loaded.value.url).query
                    assert load_query == "hub_d=40", (
                        f"inert fields, fresh load: the page sent {load_query!r}, not the "
                        "link's hub_d=40 (spoke_count=0 is the default and is dropped)"
                    )

                    want = expected_inactive(properties, "spoke_count=0&hub_d=40")
                    got = eval_inactive(fresh)
                    assert "hub_d" in want, "inert fields: the link's own field is not dimmed"
                    assert got == want, f"inert fields: the page dims {got}, the schema says {want}"
                    for name, reason in sorted(got.items()):
                        print(f"inert fields: {name}: {reason}")

                    hub_d = fresh.locator("form#params [name=hub_d]")
                    expect(hub_d).to_be_visible()
                    expect(hub_d).to_be_editable()
                    expect(hub_d).to_have_value("40")

                    # A real keystroke into the dimmed field reaches the request.
                    with fresh.expect_request(
                        lambda request: "/api/info" in request.url, timeout=BUILD_WAIT_MS
                    ) as typed:
                        hub_d.fill("41")
                    typed_query = urllib.parse.urlsplit(typed.value.url).query
                    assert typed_query == "hub_d=41", (
                        f"inert fields, typed into the dimmed field: the page sent {typed_query!r}"
                    )
                    assert "hub_d" in eval_inactive(fresh), "inert fields: typing made hub_d live"

                    # The gate going live: read in the same JS task as the event, before the
                    # 350 ms debounce (23-RESEARCH Pitfall 8), so only the input
                    # listener's own call can have changed it.
                    with fresh.expect_request(
                        lambda request: "/api/info" in request.url, timeout=BUILD_WAIT_MS
                    ) as gated:
                        still_dimmed = eval_bool(
                            fresh,
                            """() => {
                              const gate = document.querySelector('form#params [name=spoke_count]');
                              gate.value = '4';
                              gate.dispatchEvent(new Event('input', { bubbles: true }));
                              return document.querySelector('form#params [name=hub_d]')
                                .closest('label').classList.contains('inactive');
                            }""",
                        )
                    assert not still_dimmed, (
                        "inert fields: hub_d still dimmed right after spoke_count's input event, "
                        "so the input listener did not re-evaluate before scheduleUpdate"
                    )
                    gated_query = urllib.parse.urlsplit(gated.value.url).query
                    assert _pairs(gated_query) == _pairs("spoke_count=4&hub_d=41"), (
                        f"inert fields, gate set: the debounced request was {gated_query!r}"
                    )
                    assert eval_inactive(fresh) == expected_inactive(
                        properties, "spoke_count=4&hub_d=41"
                    ), "inert fields: the dimmed set after the gate went live is not the schema's"

                    # Reset: the empty query, and exactly the set the empty link gives.
                    with fresh.expect_request(
                        lambda request: "/api/info" in request.url, timeout=BUILD_WAIT_MS
                    ) as reset_request:
                        fresh.locator("#reset").click()
                    reset_query = urllib.parse.urlsplit(reset_request.value.url).query
                    assert reset_query == "", f"inert fields, Reset: the page sent {reset_query!r}"
                    assert eval_inactive(fresh) == expected_inactive(properties, ""), (
                        "inert fields, Reset: the dimmed set differs from the empty link's"
                    )
                finally:
                    fresh.close()

                # One link per gate condition, derived from the schema (D-15): the dimmed set
                # must follow the fields and never the server's answer, so a flip the API
                # refuses with a 422 is held to the evaluator too. The main page's fragment
                # is empty here and its STL route serves the first build, so nothing builds.
                default_dimmed = expected_inactive(properties, "")
                links = flip_links(properties)
                assert links, "inert fields: the schema yields no flip link"
                gates = {link.split("=")[0] for link in links}
                for link in links:
                    sent = _follow_link(page, link)
                    status, _ = _api_get(server, "/api/info", sent)
                    flipped = expected_inactive(properties, link)
                    assert flipped != default_dimmed, f"inert fields: #{link} flips nothing"
                    got = eval_inactive(page)
                    assert got == flipped, (
                        f"inert fields: #{link} (API {status}): the page dims {got}, the "
                        f"schema says {flipped}; the dim state follows the fields, not the "
                        "server's answer"
                    )
                    print(f"inert fields: flip #{link}: API {status}, dimmed {sorted(got)}")

                sent = _follow_link(page, REFUSED_LINK)
                status, body = _api_get(server, "/api/info", sent)
                assert status == 422, f"inert fields: #{REFUSED_LINK} answered {status}, not 422"
                marked, texts = _expected_422(properties, body)
                expect(page.locator("#messages .error")).to_have_text(texts)
                refused_invalid = eval_str_list(
                    page,
                    "() => [...document.querySelectorAll('form#params label.field.invalid [name]')]"
                    ".map(e => e.name)",
                )
                dimmed = eval_inactive(page)
                assert dimmed == expected_inactive(properties, REFUSED_LINK), (
                    f"inert fields, refused pair: the page dims {dimmed}"
                )
                # PD-07 is a claim about the whole pair, so the page must mark exactly what
                # the server named (the gate and both keyway fields, calc.py REFUSED) and both
                # keyway fields must carry .invalid and .inactive together. One in the
                # intersection is not enough: a page that marked only keyway_width passed (IN-07).
                invalid_titles = {_title(properties, n) for n in refused_invalid}
                assert invalid_titles == marked, (
                    f"inert fields, refused pair: marked {sorted(invalid_titles)}, "
                    f"server named {sorted(marked)}"
                )
                both = sorted(set(refused_invalid) & set(dimmed))
                pair = set(urllib.parse.parse_qs(REFUSED_LINK)) - gates
                assert len(pair) == 2, f"inert fields, refused pair: {REFUSED_LINK} names {pair}"
                assert pair <= set(both), (
                    f"inert fields, refused pair: {sorted(pair)} are not both invalid "
                    f"{refused_invalid} and dimmed {sorted(dimmed)}"
                )
                assert not gates & set(dimmed), "inert fields, refused pair: a gate is dimmed"
                assert gates & set(refused_invalid), (
                    f"inert fields, refused pair: no gate marked invalid among {refused_invalid}: "
                    "the user could not see how to get back (D-20)"
                )
                print(
                    f"inert fields: refused pair: invalid {sorted(refused_invalid)}, "
                    f"dimmed and invalid {both}"
                )

                # The dim is shown (PD-06): a reason is displayed for exactly the dimmed
                # fields, and their names are drawn in colours no live field's name uses.
                shown = eval_str_list(
                    page,
                    "() => [...document.querySelectorAll('form#params label.field')]"
                    ".filter(l => getComputedStyle(l.querySelector('.reason')).display !== 'none')"
                    ".map(l => l.querySelector('[name]').name)",
                )
                assert sorted(shown) == sorted(dimmed), (
                    f"inert fields: reasons shown for {sorted(shown)}, dimmed {sorted(dimmed)}"
                )
                # The reason sits inside the wrapping <label>, so its text is already part of
                # the input's accessible name; aria-describedby then reads it a second time.
                # aria-hidden removes it from the name, and a node a describedby points at is
                # still read as the description (IN-02).
                unhidden = eval_str_list(
                    page,
                    "() => [...document.querySelectorAll('form#params .reason')]"
                    ".filter(r => r.getAttribute('aria-hidden') !== 'true').map(r => r.id)",
                )
                assert not unhidden, f"inert fields: reasons readable twice: {unhidden}"
                described = eval_str_list(
                    page,
                    "() => [...document.querySelectorAll('form#params [aria-describedby]')]"
                    ".map(e => e.name)",
                )
                assert sorted(described) == sorted(dimmed), (
                    f"inert fields: described {sorted(described)}, dimmed {sorted(dimmed)}"
                )
                name_colours = (
                    "() => [...new Set([...document.querySelectorAll("
                    "'form#params label.field%s .name')].map(e => getComputedStyle(e).color))]"
                )
                dim_colours = eval_str_list(page, name_colours % ".inactive")
                live_colours = eval_str_list(page, name_colours % ":not(.inactive)")
                assert dim_colours, "inert fields: no dimmed name has a colour"
                assert live_colours, "inert fields: no live name has a colour"
                shared = set(dim_colours) & set(live_colours)
                assert not shared, f"inert fields: dimmed and live names both use {sorted(shared)}"

                # Reset from the refused state: the empty query, the default set, nothing
                # left marked invalid.
                with page.expect_request(
                    lambda request: "/api/info" in request.url, timeout=BUILD_WAIT_MS
                ) as reset_sent:
                    page.locator("#reset").click()
                reset_query = urllib.parse.urlsplit(reset_sent.value.url).query
                assert reset_query == "", f"inert fields, Reset: the page sent {reset_query!r}"
                assert eval_inactive(page) == default_dimmed, (
                    "inert fields, Reset: the dimmed set is not the default one"
                )
                expect(page.locator("form#params label.field.invalid")).to_have_count(0)

            with step("bore shape", no_foreign_key):
                # L42: a bore shape is picked from a select the schema describes. Its own
                # page with the STL route aborted, as in the sweep, so nothing builds; the
                # fragment of a fresh load rides the goto URL (22-RESEARCH Pitfall 2). Every
                # option, link, query, field and note comes from /api/schema through
                # expected_shown(), state_links() and expected_pick(), never a literal (D-13).
                # It sits after `inert fields` and before `unknown relation op`, the steps
                # whose state it would disturb (22 D-07). One selector today: the schema's
                # list is read at index 0.
                chooser = selectors[0]
                shape_links = state_links(chooser, properties)
                default_label = expected_shown(selectors, properties, "")[0]
                picks = {
                    label: expected_pick(chooser, properties, label, "", {})
                    for label in shape_links
                    if label != default_label
                }
                writing = [label for label, pick in picks.items() if pick.sent is not None]
                pending = [label for label, pick in picks.items() if pick.sent is None]
                assert writing, "bore shape: the schema yields no pick that writes"
                assert pending, "bore shape: the schema yields no pick that stays pending"
                bore = record_api(browser.new_page(), seen)
                try:
                    bore.route(STL_ROUTE, lambda route: route.abort())
                    link = shape_links[pending[0]]
                    with bore.expect_request(
                        lambda request: "/api/info" in request.url, timeout=BUILD_WAIT_MS
                    ) as loaded:
                        bore.goto(server + "/#" + link)
                    load_query = urllib.parse.urlsplit(loaded.value.url).query
                    assert _pairs(load_query) == _pairs(link), (
                        f"bore shape, fresh load of #{link}: the page sent {load_query!r}"
                    )
                    now_shown = eval_shown(bore)
                    assert now_shown == expected_shown(selectors, properties, link), (
                        f"bore shape, #{link}: the page shows {now_shown}"
                    )
                    assert now_shown[0] == pending[0], (
                        f"bore shape, #{link}: shows {now_shown}, expected {pending[0]!r}"
                    )
                    assert eval_inactive(bore) == expected_inactive(properties, link), (
                        f"bore shape, #{link}: the select changed what the relations dim"
                    )
                    first_field = next(
                        name for name, prop in properties.items()
                        if prop.get("group") == chooser["group"]
                    )
                    place = eval_str(
                        bore,
                        """() => {
                          const wrap = document.querySelector('form#params label.selector');
                          return [
                            wrap.closest('fieldset').querySelector('legend').textContent,
                            wrap.previousElementSibling.tagName,
                            wrap.nextElementSibling.querySelector('[name]').name,
                            wrap.querySelector('.name').textContent,
                          ].join('|');
                        }""",
                    )
                    assert place == f"{chooser['group']}|LEGEND|{first_field}|{chooser['title']}", (
                        f"bore shape: the row sits at {place!r}, not first in its fieldset (D-04)"
                    )
                    print(f"bore shape: loaded #{link}: shows {now_shown[0]!r}")

                    def reset_bore() -> None:
                        with bore.expect_request(
                            lambda request: "/api/info" in request.url, timeout=BUILD_WAIT_MS
                        ) as reset_sent:
                            bore.locator("#reset").click()
                        reset_query = urllib.parse.urlsplit(reset_sent.value.url).query
                        assert reset_query == "", (
                            f"bore shape, Reset: the page sent {reset_query!r}"
                        )
                        assert eval_shown(bore)[0] == default_label, (
                            f"bore shape, Reset: shows {eval_shown(bore)}, not {default_label!r}"
                        )

                    reset_bore()
                    current, stash = _writing_pick(
                        bore, chooser, properties, writing[0], "", {}
                    )

                    # D-08: back to the part the user had, the box restored byte for byte from
                    # the stash and not re-formatted (probe: write precision). The restore keeps
                    # its stash entry (PD-08).
                    before = dict(eval_pairs(bore))
                    current, stash = _writing_pick(
                        bore, chooser, properties, default_label, current, stash
                    )
                    restored = {
                        name: value for name, value in eval_pairs(bore) if before[name] != value
                    }
                    assert restored, "bore shape: the restore changed no box"
                    for name, value in restored.items():
                        assert stash.get(name) == value, (
                            f"bore shape: {name} holds {value!r}, the stash held "
                            f"{stash.get(name)!r}"
                        )
                        print(f"bore shape: {name} back to {value!r} from the stash")

                    # D-09: a pick that needs a number the user has not typed writes nothing.
                    _pending_pick(bore, chooser, properties, pending[0], current, stash)

                    # D-09: the number typed into the field the pick named completes the pick.
                    _complete_pending(bore, chooser, properties, pending[0], current, stash)

                    # D-08: Reset clears the stash, so a pick after Reset and a link restores
                    # nothing and is pending (a page that kept the stash would restore).
                    reset_bore()
                    _writing_pick(bore, chooser, properties, writing[0], "", {})
                    reset_bore()
                    zeroed_link = shape_links[writing[0]]
                    _follow_link(bore, zeroed_link)
                    _pending_pick(bore, chooser, properties, default_label, zeroed_link, {})

                    # D-06, D-13: every option's own link loads as that option, through
                    # hashchange, and the dimmed set is the fields'.
                    reset_bore()
                    for label, state_link in shape_links.items():
                        if state_link == "":
                            continue
                        _follow_link(bore, state_link)
                        assert eval_shown(bore)[0] == label, (
                            f"bore shape: #{state_link} shows {eval_shown(bore)}, not {label!r}"
                        )
                        assert eval_inactive(bore) == expected_inactive(properties, state_link), (
                            f"bore shape: #{state_link} dims a set that is not the fields'"
                        )
                        print(f"bore shape: loaded #{state_link}: shows {label!r}")
                    # Probe, precision: the zero written 0.0 is the same number, so the same
                    # option (the comparison is numeric, never of strings).
                    written = urllib.parse.urlencode(
                        [(k, f"{float(v):.1f}") for k, v in urllib.parse.parse_qsl(zeroed_link)]
                    )
                    _follow_link(bore, written)
                    assert eval_shown(bore)[0] == writing[0], (
                        f"bore shape: #{written} shows {eval_shown(bore)}, not {writing[0]!r}"
                    )
                    print(f"bore shape: loaded #{written}: shows {writing[0]!r}")

                    # D-18: a negative matches no option, so the select is blank, nothing is
                    # written and the page still builds the part (the request is sent).
                    below = negative_link(chooser, properties)
                    _follow_link(bore, below)
                    assert eval_shown(bore) == expected_shown(selectors, properties, below), (
                        f"bore shape: #{below} shows {eval_shown(bore)}"
                    )
                    assert eval_shown(bore)[0] == "", f"bore shape: #{below} still shows an option"
                    assert not eval_bool(bore, SELECTOR_PENDING), "bore shape: a blank select pends"
                    print(f"bore shape: loaded #{below}: shows ''")

                    # D-07, D-09, D-13: every pick from every state. The sixteen picks, the
                    # shown option included, are each compared with expected_pick(), the
                    # schema's mirror of the write rule, from a page Reset and then taken to the
                    # state's own link. A pick of the shown option writes nothing, so it must
                    # send the query the page already had (Playwright's select_option fires
                    # `input` even when the value is unchanged).
                    for start, start_link in shape_links.items():
                        for label in shape_links:
                            reset_bore()
                            if start_link != "":
                                _follow_link(bore, start_link)
                            assert eval_shown(bore)[0] == start, (
                                f"bore shape: #{start_link} shows {eval_shown(bore)}, "
                                f"not {start!r}"
                            )
                            rule = expected_pick(chooser, properties, label, start_link, {})
                            if rule.sent is None:
                                _pending_pick(bore, chooser, properties, label, start_link, {})
                                # CX-01 (PR #36, Codex): completing it writes what it held
                                # back, the zeros included, and lands on the label. WR-02:
                                # where the field's default would clear the threshold, the
                                # box is emptied first and the pick must stay pending.
                                _complete_pending(
                                    bore,
                                    chooser,
                                    properties,
                                    label,
                                    start_link,
                                    {},
                                    empty_first=_default_clears(
                                        properties, chooser, label, rule.field
                                    ),
                                )
                            else:
                                _writing_pick(bore, chooser, properties, label, start_link, {})

                    # CX-01: a pick short of two numbers stays pending through the first and
                    # completes on the second. The link puts every `gt` field of the option at
                    # its threshold, so each is typed in turn; a page that ended the pick at the
                    # first derive would show the fields' option instead.
                    chains_seen = 0
                    for label in shape_links:
                        at_threshold = _gt_thresholds(chooser, label)
                        if len(at_threshold) < 2:
                            continue
                        threshold_link = urllib.parse.urlencode(at_threshold)
                        reset_bore()
                        _follow_link(bore, threshold_link)
                        assert eval_shown(bore) == expected_shown(
                            selectors, properties, threshold_link
                        ), f"bore shape: #{threshold_link} shows {eval_shown(bore)}"
                        _pending_pick(bore, chooser, properties, label, threshold_link, {})
                        _chain_sent, _chain_stash, typed_count = _complete_pending(
                            bore, chooser, properties, label, threshold_link, {}
                        )
                        assert typed_count == len(at_threshold), (
                            f"bore shape, {label} from #{threshold_link}: {typed_count} number(s) "
                            f"typed, {len(at_threshold)} thresholds"
                        )
                        chains_seen += 1
                    assert chains_seen, "bore shape: no option sets two gt thresholds"

                    # CX-01: any other field moving ends the pending pick, and the select shows
                    # the fields' state, not the asked-for one. The first pending pick whose
                    # selector names another field is taken; that field gets a number above
                    # the one its box holds.
                    abandoned = False
                    for start_link in shape_links.values():
                        for label in shape_links:
                            rule = expected_pick(chooser, properties, label, start_link, {})
                            other_fields = sorted(_named_fields(chooser) - {rule.field})
                            if rule.sent is not None or not other_fields:
                                continue
                            reset_bore()
                            if start_link != "":
                                _follow_link(bore, start_link)
                            _pending_pick(bore, chooser, properties, label, start_link, {})
                            boxes_before = dict(eval_pairs(bore))
                            other_field = other_fields[0]
                            held_text = boxes_before[other_field]
                            held = held_text if held_text != "" else None
                            typed_value = number_above(
                                properties, other_field, float(held) if held is not None else -1.0
                            )
                            kept_pairs = [
                                (k, v)
                                for k, v in urllib.parse.parse_qsl(start_link)
                                if k != other_field
                            ]
                            moved_link = urllib.parse.urlencode(
                                [*kept_pairs, (other_field, typed_value)]
                            )
                            with bore.expect_request(
                                lambda request: "/api/info" in request.url, timeout=BUILD_WAIT_MS
                            ):
                                bore.locator(f"form#params [name={other_field}]").fill(typed_value)
                            moved_fields = {k for k, v in eval_pairs(bore) if boxes_before[k] != v}
                            assert moved_fields == {other_field}, (
                                f"bore shape, {label} abandoned: typed {other_field}, "
                                f"{sorted(moved_fields)} moved"
                            )
                            assert eval_shown(bore) == expected_shown(
                                selectors, properties, moved_link
                            ), (
                                f"bore shape, {label} abandoned by {other_field}={typed_value}: "
                                f"shows {eval_shown(bore)}, not the fields' option"
                            )
                            assert not eval_bool(bore, SELECTOR_PENDING), (
                                f"bore shape, {label} abandoned by {other_field}: still pending"
                            )
                            assert eval_str(bore, SELECT_BORDER) != "dashed", (
                                f"bore shape, {label} abandoned by {other_field}: drawn pending"
                            )
                            print(
                                f"bore shape: #{start_link} + {label} abandoned by "
                                f"{other_field}={typed_value}: shows {eval_shown(bore)[0]!r}"
                            )
                            abandoned = True
                            break
                        if abandoned:
                            break
                    assert abandoned, "bore shape: no pending pick to abandon was found"

                    # D-19: the stash outlives hash navigations. The first pick zeroes a field
                    # and stashes the user's number; two links later the pick back restores it
                    # and sends the empty query. Only Reset clears the stash.
                    reset_bore()
                    _, carried = _writing_pick(bore, chooser, properties, writing[0], "", {})
                    away, back = shape_links[pending[0]], shape_links[writing[0]]
                    _follow_link(bore, away)
                    _follow_link(bore, back)
                    _writing_pick(bore, chooser, properties, default_label, back, carried)
                    print(f"bore shape: the stash outlived #{away} and #{back}")

                    # D-03, D-10: over a keyed bore every pick leaves the keyway fields as the
                    # link set them, and a refusal stays the server's. `keyed` is the refused
                    # link without the fields the selector names, so nothing of the selector's
                    # own is in it. A writing pick must send the keyway pair unchanged; the
                    # pending pick is completed by typing its value. The server's 422 for the
                    # sent query is then fetched and the page must mark exactly what it names.
                    chooser_fields = _named_fields(chooser)
                    refused_pairs = urllib.parse.parse_qsl(REFUSED_LINK)
                    keyed = urllib.parse.urlencode(
                        [(k, v) for k, v in refused_pairs if k not in chooser_fields]
                    )
                    keyed_fields = {name for name, _ in _pairs(keyed)}
                    assert len(keyed_fields) == 2, f"bore shape: {keyed!r} is not the keyway pair"
                    refusals = 0
                    for label in shape_links:
                        reset_bore()
                        _follow_link(bore, keyed)
                        assert eval_shown(bore) == expected_shown(selectors, properties, keyed), (
                            f"bore shape, keyed #{keyed}: shows {eval_shown(bore)}"
                        )
                        rule = expected_pick(chooser, properties, label, keyed, {})
                        if rule.sent is not None:
                            query, _ = _writing_pick(bore, chooser, properties, label, keyed, {})
                        else:
                            _pending_pick(bore, chooser, properties, label, keyed, {})
                            query, _keyed_stash, _keyed_typed = _complete_pending(
                                bore, chooser, properties, label, keyed, {}
                            )
                        changed = set(_pairs(keyed)) - set(_pairs(query))
                        assert not changed, (
                            f"bore shape, keyed + {label}: the keyway pair {sorted(changed)} was "
                            f"changed in {query!r}"
                        )
                        status, body = _api_get(server, "/api/info", query)
                        print(f"bore shape: keyed + {label} -> {query!r}: API {status}")
                        if status != 422:
                            continue
                        refusals += 1
                        named, texts = _expected_422(properties, body)
                        expect(bore.locator("#messages .error")).to_have_text(texts)
                        marked_names = eval_str_list(bore, INVALID_NAMES)
                        assert {_title(properties, n) for n in marked_names} == named, (
                            f"bore shape, keyed + {label}: marked {sorted(marked_names)}, the 422 "
                            f"names {sorted(named)}"
                        )
                        if rule.sent is None:
                            # L41's PD-07 pair: the refused keyway fields are dimmed AND marked.
                            dimmed_names = set(eval_inactive(bore))
                            dimmed_marked = keyed_fields & dimmed_names & set(marked_names)
                            assert dimmed_marked == keyed_fields, (
                                f"bore shape, keyed + {label}: {sorted(keyed_fields)} are not "
                                f"both dimmed and invalid; both: {sorted(dimmed_marked)}"
                            )
                    assert refusals, "bore shape: no keyed pick met a 422, the refusal went unseen"
                finally:
                    bore.close()

            with step("twin selectors", no_foreign_key):
                # CX-04 (PR #36, Codex re-review): a pending pick in one selector is ended by
                # a pending pick in another -- its row put back, its select re-derived to the
                # fields' option -- although the second pick stops its event before the form's
                # listener. The schema is served with its selector list doubled, so both
                # selects derive the same option and either can go pending from one link;
                # nothing else about the page changes. `pendings[0]` is the first state link
                # with two labels pending on different fields, read from the schema;
                # `twins_page` is the page served with the doubled list.
                status, schema = _api_get(server, "/api/schema", "")
                assert status == 200, f"twin selectors: /api/schema answered {status}"
                assert isinstance(schema, dict), "twin selectors: the schema is not an object"
                doubled = json.loads(json.dumps(schema))
                doubled["selectors"].append(json.loads(json.dumps(doubled["selectors"][0])))
                chooser = selectors[0]
                shape_links = state_links(chooser, properties)
                pendings = [
                    (start_link, a, b)
                    for start_link in shape_links.values()
                    for a in shape_links
                    for b in shape_links
                    if a != b
                    and expected_pick(chooser, properties, a, start_link, {}).sent is None
                    and expected_pick(chooser, properties, b, start_link, {}).sent is None
                    and expected_pick(chooser, properties, a, start_link, {}).field
                    != expected_pick(chooser, properties, b, start_link, {}).field
                ]
                assert pendings, "twin selectors: no two picks pend on different fields"
                link, first, second = pendings[0]
                # app.js returns before the STL fetch when /api/info refuses the link, so the
                # STL wait below would time out on a misleading cause.
                info_status, _ = _api_get(server, "/api/info", link)
                assert info_status == 200, (
                    f"twin selectors: /api/info answered {info_status} for #{link}, so the page "
                    "would send no STL request"
                )
                first_rule = expected_pick(chooser, properties, first, link, {})
                second_rule = expected_pick(chooser, properties, second, link, {})
                shown_at_link = expected_shown([chooser], properties, link)[0]
                twins_page = record_api(browser.new_page(), seen)
                try:
                    twins_page.route("**/api/schema", lambda route: route.fulfill(json=doubled))
                    twins_page.route(STL_ROUTE, lambda route: route.abort())
                    # The link's own build sends /api/info and, after that response,
                    # /api/model.stl (app.js update()). The baseline once waited only for the
                    # info request, so on a slow runner the STL request landed inside the
                    # counted window (main runs 38347283201 and 38680454993, one request
                    # each). Measured on the real app (26-03 arms): a parked STL route left
                    # that baseline green, a parked /api/info turned it red, waiting for the
                    # STL request turned it green -- the info response is the lever, not the
                    # STL route.
                    with twins_page.expect_request(
                        lambda request: "/api/model.stl" in request.url, timeout=BUILD_WAIT_MS
                    ):
                        twins_page.goto(server + "/#" + link)
                    # No timer is pending at load (app.js's bootstrap runs readHash() and update());
                    # the settle keeps the baseline true for any scheduleUpdate() a future
                    # load path queues.
                    twins_page.wait_for_timeout(DEBOUNCE_SETTLE_MS)
                    assert eval_shown(twins_page) == (shown_at_link, shown_at_link), (
                        f"twin selectors: #{link} shows {eval_shown(twins_page)}"
                    )
                    pairs_before = eval_pairs(twins_page)
                    requests_before = len(seen)
                    first_reason = twins_page.locator(
                        f"form#params label.field:has([name={first_rule.field}]) .reason"
                    )
                    second_reason = twins_page.locator(
                        f"form#params label.field:has([name={second_rule.field}]) .reason"
                    )
                    first_select = twins_page.locator("#selector-0")
                    first_select.focus()
                    first_select.select_option(label=first)
                    assert eval_bool(twins_page, PENDING_AT, 0), (
                        f"twin selectors: {first} not pending"
                    )
                    expect(first_reason).to_have_text(first_rule.note)
                    second_select = twins_page.locator("#selector-1")
                    second_select.focus()
                    second_select.select_option(label=second)
                    # The first pick is over: wrapper plain, select back on the fields' option,
                    # its field's row back to what the relations say; the second is pending.
                    assert not eval_bool(twins_page, PENDING_AT, 0), (
                        f"twin selectors: {first} still pending after {second} in the other"
                    )
                    assert eval_bool(twins_page, PENDING_AT, 1), (
                        f"twin selectors: {second} not pending"
                    )
                    assert eval_shown(twins_page) == (shown_at_link, second), (
                        f"twin selectors: shows {eval_shown(twins_page)}, expected "
                        f"{(shown_at_link, second)}"
                    )
                    row_back = expected_inactive(properties, link).get(first_rule.field, "")
                    expect(first_reason).to_have_text(row_back)
                    expect(second_reason).to_have_text(second_rule.note)
                    assert eval_pairs(twins_page) == pairs_before, (
                        "twin selectors: a field was written"
                    )
                    # CX-05: a stray scheduleUpdate() sends its request 350 ms later, so a count
                    # taken at once passes before it can fail.
                    twins_page.wait_for_timeout(DEBOUNCE_SETTLE_MS)
                    assert len(seen) == requests_before, (
                        f"twin selectors: {len(seen) - requests_before} request(s) sent by two "
                        "pending picks"
                    )
                finally:
                    twins_page.close()
                print(
                    f"twin selectors: #{link} + {first} in one, then {second} in the other: "
                    f"the first back to {shown_at_link!r}, the second pending on "
                    f"{second_rule.field}"
                )

            with step("unknown relation op", no_foreign_key):
                # D-02: an op the page does not know is loud, never "active". WR-01: but loud
                # on the field, not by stopping the page. A throw out of applyRelations()
                # used to skip update() on every keystroke, so the part, the dimensions and
                # the download links stayed on the previous parameters while the form moved.
                # The schema is served with the first related field's first op changed to
                # one the page lacks; its own page, because the route replaces the schema.
                # L42: the same holds for a bore-shape option the page cannot read: it is
                # caught per selector, as a relation is per field, so that select goes blank
                # and says why in its own row while the part still builds. And a selector on
                # which two options hold shows none, because a select that picked the first
                # would claim a shape the fields do not single out (PD-06, BS-3): a twin
                # selector is served beside it with one option's conditions copied onto
                # another.
                status, schema = _api_get(server, "/api/schema", "")
                assert status == 200, f"unknown relation op: /api/schema answered {status}"
                assert isinstance(schema, dict), "unknown relation op: the schema is not an object"
                tampered = json.loads(json.dumps(schema))
                tampered_properties = tampered["properties"]
                related = [n for n, prop in tampered_properties.items() if "enabled_when" in prop]
                assert related, "unknown relation op: no field carries a relation to tamper with"
                broken = related[0]
                tampered_properties[broken]["enabled_when"][0]["op"] = "ge"
                # The first condition of the first option of the first selector: names no field.
                tampered["selectors"][0]["options"][0]["when"][0]["op"] = "ge"
                twin = json.loads(json.dumps(selectors[0]))
                twin_labels = [option["label"] for option in twin["options"]]
                twin_shown = expected_shown([selectors[0]], properties, "teeth=23")[0]
                holder = twin_labels.index(twin_shown)
                other = next(i for i in range(len(twin_labels)) if i != holder)
                twin["options"][other]["when"] = json.loads(
                    json.dumps(twin["options"][holder]["when"])
                )
                assert expected_shown([twin], properties, "teeth=23") == ("",), (
                    "unknown relation op: the Python oracle shows an option where two hold"
                )
                tampered["selectors"].append(twin)
                bad = record_api(browser.new_page(), seen)
                try:
                    bad.route("**/api/schema", lambda route: route.fulfill(json=tampered))
                    bad.goto(server + "/#teeth=23")
                    # The selectors are read through their ids: two of them would make a
                    # class locator ambiguous.
                    unreadable_option = (
                        "Cannot tell which option holds: Unknown enabled_when op: ge"
                    )
                    expect(bad.locator("#selector-0")).to_have_js_property("selectedIndex", -1)
                    expect(bad.locator("#reason-selector-0")).to_have_text(unreadable_option)
                    expect(
                        bad.locator("#selector-1"),
                        "unknown relation op: two holding options must leave the select blank",
                    ).to_have_js_property("selectedIndex", -1)
                    expect(bad.locator("#dl-stl")).to_have_attribute(
                        "href", "api/model.stl?teeth=23", timeout=BUILD_WAIT_MS
                    )
                    broken_reason = bad.locator(f"label.field:has([name={broken}]) .reason")
                    unreadable = (
                        "Cannot tell whether this field is used: Unknown enabled_when op: ge"
                    )
                    expect(broken_reason).to_have_text(unreadable)
                    others = {
                        name: why
                        for name, why in expected_inactive(properties, "teeth=23").items()
                        if name != broken
                    }
                    assert eval_inactive(bad) == others, (
                        f"unknown relation op: the page dims {eval_inactive(bad)}, the other "
                        f"fields' relations say {others}"
                    )
                    with bad.expect_request(
                        lambda request: "/api/info" in request.url
                        and urllib.parse.urlsplit(request.url).query == "teeth=24",
                        timeout=BUILD_WAIT_MS,
                    ):
                        bad.locator("[name=teeth]").fill("24")
                    expect(bad.locator("#dl-stl")).to_have_attribute(
                        "href", "api/model.stl?teeth=24", timeout=BUILD_WAIT_MS
                    )
                    # The row outlives the keystroke (applyRelations() comment): its text, not
                    # its presence. A cleared span is still one node, `display: none`, so a
                    # count of 1 held whether or not the error was still there (IN-10).
                    expect(broken_reason).to_have_text(unreadable)
                    # The input listener re-derived both selectors: still blank, still said.
                    expect(bad.locator("#reason-selector-0")).to_have_text(unreadable_option)
                    expect(
                        bad.locator("#selector-1"),
                        "unknown relation op: two holding options must leave the select blank",
                    ).to_have_js_property("selectedIndex", -1)
                    others = {
                        name: why
                        for name, why in expected_inactive(properties, "teeth=24").items()
                        if name != broken
                    }
                    assert eval_inactive(bad) == others, (
                        f"unknown relation op, after a keystroke: the page dims "
                        f"{eval_inactive(bad)}, the other fields' relations say {others}"
                    )
                finally:
                    bad.close()
                print(
                    f"unknown relation op: {broken} unreadable, the bore-shape select blank, "
                    "two holding options blank, the form still builds the part"
                )

            with step("form build error", no_foreign_key):
                # 24 IN-02: the schema loaded, so a message about the schema fetch named the
                # wrong failure when a selector names a group no field has. The bootstrap
                # still returns before readHash() and update() (Codex's isolate-and-continue
                # proposal is not taken, D-14); a malformed selector is caught before it
                # ships by tests/test_selector.py and test_schema_drives_the_form (CX-03).
                status, schema = _api_get(server, "/api/schema", "")
                assert status == 200, f"form build error: /api/schema answered {status}"
                assert isinstance(schema, dict), "form build error: the schema is not an object"
                broken_schema = json.loads(json.dumps(schema))
                assert not any(
                    prop.get("group") == "No such group"
                    for prop in broken_schema["properties"].values()
                ), "form build error: a field already sits in the made-up group"
                broken_selector = broken_schema["selectors"][0]
                broken_selector["group"] = "No such group"
                selector_title = broken_selector["title"]
                info_before = sum(
                    1 for url in seen if urllib.parse.urlsplit(url).path == "/api/info"
                )
                bad = record_api(browser.new_page(), seen)
                try:
                    bad.route("**/api/schema", lambda route: route.fulfill(json=broken_schema))
                    bad.goto(server + "/")
                    expect(bad.locator("#messages .error")).to_have_text(
                        "Could not build the form: "
                        f'Selector "{selector_title}" names the group "No such group", '
                        "which no field has"
                    )
                    bad.wait_for_timeout(DEBOUNCE_SETTLE_MS)
                finally:
                    bad.close()
                info_after = sum(
                    1 for url in seen if urllib.parse.urlsplit(url).path == "/api/info"
                )
                assert info_after == info_before, (
                    f"the page asked /api/info {info_after - info_before} times with no form"
                )
                print(f"form build error: the bootstrap names {selector_title!r}, sent no info")

            with step("download name", no_foreign_key):
                # The main `page` carries serve_stl_from(page, stl), whose STL_ROUTE answers
                # with the first build's bytes and no Content-Disposition, so a click there
                # saves `model.stl` (22-RESEARCH Pitfall 1, reproduced): this step opens its
                # own page. A fragment assigned after the load can be erased before
                # buildForm() returns (Pitfall 2, one lost in about a dozen runs), so the
                # fragment rides the goto URL, the way a shared link does. The href carries no
                # `quality`, so the click asks ModelQuery's default `fine` (app.py:238-239):
                # one 23-tooth hob-root build at load plus a fine re-mesh of the cached solid.
                fresh = record_api(browser.new_page(), seen)
                try:
                    fresh.goto(server + "/#teeth=23&root_shape=trochoid")
                    expect(fresh.locator("#dl-stl")).to_have_attribute(
                        "href", "api/model.stl?teeth=23&root_shape=trochoid", timeout=BUILD_WAIT_MS
                    )
                    started = time.monotonic()
                    with fresh.expect_download(timeout=BUILD_WAIT_MS) as download:
                        fresh.click("#dl-stl")
                    name = download.value.suggested_filename
                    clicked = time.monotonic() - started
                finally:
                    fresh.close()
                print(f"download name: {name}, click to download {clicked:.2f} s")
                assert name == "spur_z23_m1.75_pa25_trochoid.stl", (
                    f"the download is named {name!r}, not the name the server gives this part"
                )

            with step("bad link refused", no_foreign_key):
                # A token its control cannot hold is sent as given and refused by the API's own
                # 422 through the path every other refusal takes (app.js readHash(), gearQuery()
                # and update(); L44). The expectation is the 422 body for the query the page
                # sent, never a literal. The page has no part to show for the link, so no STL
                # request follows (D-04); the main page fulfils every STL request with the first
                # build's bytes, so the request count is the evidence, not data-triangles.
                stl_before = _stl_requests(seen)
                for link, field in BAD_LINKS:
                    sent = _follow_link(page, link)
                    assert _pairs(sent) == _pairs(link), (
                        f"#{link}: /api/info was sent {sent!r}, the link's pairs are {_pairs(link)}"
                    )
                    # gearQuery() walks the schema in order and update() adds the mate last;
                    # _pairs sorts, so it cannot show the order.
                    keys = [k for k, _ in urllib.parse.parse_qsl(link, keep_blank_values=True)]
                    want_keys = [k for k in properties if k in keys]
                    if "mate_teeth" in keys:
                        want_keys.append("mate_teeth")
                    sent_keys = [
                        k for k, _ in urllib.parse.parse_qsl(sent, keep_blank_values=True)
                    ]
                    assert sent_keys == want_keys, (
                        f"#{link}: the keys were sent in the order {sent_keys}, not {want_keys}"
                    )
                    status, body = _api_get(server, "/api/info", sent)
                    assert status == 422, f"/api/info?{sent} answered {status}, not 422"
                    marked, texts = _expected_422(properties, body)
                    named = {_title(properties, field)} if field in properties else set()
                    assert marked == named, (
                        f"#{link}: the 422 names {sorted(marked)}, not the field {field}"
                    )
                    expect(page.locator("#messages .error")).to_have_text(texts)
                    invalid = set(page.locator("label.field.invalid .name").all_text_contents())
                    assert invalid == marked, (
                        f"#{link}: marked {sorted(invalid)}, the 422 names {sorted(marked)}"
                    )
                    if field not in properties:
                        # D-05: the mate box is not in `fields`, so the server's bare message
                        # is shown with no outline anywhere.
                        assert page.locator("label.field.invalid").count() == 0, (
                            f"#{link}: a field is outlined for the mate box's refusal"
                        )
                    assert _pairs(eval_str(page, FRAGMENT)) == _pairs(link), (
                        f"#{link}: the fragment is #{eval_str(page, FRAGMENT)}, not the link"
                    )
                    # D-01: the control that could not hold the token reads blank.
                    if field in properties:
                        held = eval_str(page, CONTROL_VALUE, field)
                        enum = properties[field].get("enum")
                        if isinstance(enum, list):
                            index = eval_int(page, CONTROL_INDEX, field)
                            count = eval_int(page, CONTROL_OPTIONS, field)
                            assert (held, index, count) == ("", -1, len(enum)), (
                                f"#{link}: the {field} select reads {held!r} at index {index} "
                                f"with {count} options, not blank at -1 with {len(enum)}"
                            )
                        else:
                            assert held == "", f"#{link}: the {field} box reads {held!r}"
                    else:
                        held = eval_str(page, MATE_VALUE)
                        assert held == "", f"#{link}: the mate box reads {held!r}"
                    assert page.locator("#dl-stl").get_attribute("href") is None, (
                        f"#{link}: the STL link has an href for a refused link"
                    )
                    assert _stl_requests(seen) == stl_before, (
                        f"#{link}: the page asked for an STL after the refusal"
                    )
                    print(
                        f"bad link #{link}: sent {sent!r}, API {status}, marked "
                        f"{sorted(marked)}, text {texts}"
                    )
                page.wait_for_timeout(DEBOUNCE_SETTLE_MS)
                assert _stl_requests(seen) == stl_before, "a late STL request followed a refusal"
                kept = canvas.get_attribute("data-triangles")
                assert kept == declared, f"a refusal changed data-triangles: {declared} to {kept}"

            with step("bad link cleared", no_foreign_key):
                # D-03: the token is kept while anything else is edited, and ends with an edit
                # of its own field, a pick on its select, the mate box typed, Reset or a new link.
                # A pick that writes the field also ends its token: the box then holds what the
                # pick wrote, and the request must send that, not the token (28-REVIEW WR-01, D-19).
                sent = _follow_link(page, "teeth=abc")
                with page.expect_request(
                    lambda request: "/api/info" in request.url, timeout=BUILD_WAIT_MS
                ) as kept_request:
                    page.fill("form#params [name=module]", "3")
                sent = urllib.parse.urlsplit(kept_request.value.url).query
                assert _pairs(sent) == [("module", "3"), ("teeth", "abc")], (
                    f"editing module dropped the teeth token: /api/info was sent {sent!r}"
                )
                status, body = _api_get(server, "/api/info", sent)
                assert status == 422, f"/api/info?{sent} answered {status}, not 422"
                marked, texts = _expected_422(properties, body)
                expect(page.locator("#messages .error")).to_have_text(texts)
                expect(page.locator("label.field.invalid .name")).to_have_text(sorted(marked))
                assert marked == {_title(properties, "teeth")}, f"the 422 names {sorted(marked)}"

                def recovered(trigger: Callable[[], object], want: str, href: str | None) -> str:
                    """Run `trigger`, and return the /api/info query the page sent for it; the
                    build then ends green: `want` is that query, `href` the STL link."""
                    with page.expect_request(
                        lambda request: "/api/info" in request.url, timeout=BUILD_WAIT_MS
                    ) as info_request:
                        trigger()
                    got = urllib.parse.urlsplit(info_request.value.url).query
                    assert _pairs(got) == _pairs(want), f"/api/info was sent {got!r}, not {want!r}"
                    expect(page.locator("#dl-stl")).to_have_attribute(
                        "href", href if href is not None else f"api/model.stl?{got}",
                        timeout=BUILD_WAIT_MS,
                    )
                    assert page.locator("label.field.invalid").count() == 0, (
                        f"{want!r}: a field is still marked invalid"
                    )
                    assert page.locator("#messages .error").count() == 0, (
                        f"{want!r}: an error is still shown"
                    )
                    return got

                recovered(
                    lambda: page.fill("form#params [name=teeth]", "21"),
                    "module=3&teeth=21", None,
                )

                _follow_link(page, "recess_sides=bogus")
                recovered(
                    lambda: page.select_option("form#params select[name=recess_sides]", "top"),
                    "recess_sides=top", None,
                )

                # "No bore" writes bore_d (the string 0) without an input event on the field.
                _follow_link(page, "bore_d=abc")
                recovered(lambda: _pick(page, "No bore"), "bore_d=0", None)

                _follow_link(page, "root_shape=bogus&teeth=22")
                recovered(lambda: page.locator("#reset").click(), "", "api/model.stl")
                assert eval_str(page, FRAGMENT) == "", "Reset left a fragment"
                assert eval_pairs(page) == default_pairs, "Reset did not restore the defaults"

                _follow_link(page, "mate_teeth=abc")
                recovered(
                    lambda: page.fill("#mate-teeth", "30"), "mate_teeth=30", "api/model.stl"
                )
                assert eval_str(page, FRAGMENT) == "mate_teeth=30"

                # A valid link leaves nothing marked.
                sent = _follow_link(page, "teeth=23")
                expect(page.locator("#dl-stl")).to_have_attribute(
                    "href", f"api/model.stl?{sent}", timeout=BUILD_WAIT_MS
                )
                assert page.locator("label.field.invalid").count() == 0
                assert page.locator("#messages .error").count() == 0
                print("bad link cleared: edit, pick, mate, Reset and a new link all recover")

            with step("bad link on a fresh page", no_foreign_key):
                # The strong form of "draws no default part": no STL route here, so a request
                # would build for real, and a page that never drew has no data-triangles. The
                # fragment rides the goto URL, as in `download name`.
                stl_before = _stl_requests(seen)
                fresh = record_api(browser.new_page(), seen)
                try:
                    with fresh.expect_request(
                        lambda request: "/api/info" in request.url, timeout=BUILD_WAIT_MS
                    ) as info_request:
                        fresh.goto(server + "/#root_shape=bogus&teeth=22")
                    sent = urllib.parse.urlsplit(info_request.value.url).query
                    assert _pairs(sent) == _pairs("root_shape=bogus&teeth=22"), (
                        f"the fresh page sent {sent!r}"
                    )
                    status, body = _api_get(server, "/api/info", sent)
                    assert status == 422, f"/api/info?{sent} answered {status}, not 422"
                    marked, texts = _expected_422(properties, body)
                    expect(fresh.locator("#messages .error")).to_have_text(
                        texts, timeout=BUILD_WAIT_MS
                    )
                    assert marked == {_title(properties, "root_shape")}, sorted(marked)
                    expect(fresh.locator("label.field.invalid .name")).to_have_text(sorted(marked))
                    fresh.wait_for_timeout(DEBOUNCE_SETTLE_MS)
                    assert _stl_requests(seen) == stl_before, "the fresh page asked for an STL"
                    assert fresh.locator("#canvas").get_attribute("data-triangles") is None, (
                        "the fresh page drew a part for a refused link"
                    )
                    assert fresh.locator("#dl-stl").get_attribute("href") is None
                    assert _pairs(eval_str(fresh, FRAGMENT)) == _pairs("root_shape=bogus&teeth=22")
                finally:
                    fresh.close()
                print(f"bad link on a fresh page: sent {sent!r}, API {status}, text {texts}")

            with step("blank, unknown and accepted tokens", no_foreign_key):
                # D-06: blank is the default and unknown keys are ignored, as before; the API
                # alone is stricter about an empty value. A token the box blanks (`5.`) is sent
                # as given and refused as written, not built under a blank box (L44, L49).
                sent = _follow_link(page, BLANK_LINK)
                assert _pairs(sent) == [("face_width", "8")], f"the blank link sent {sent!r}"
                status, _ = _api_get(server, "/api/info", sent)
                assert status == 200, f"/api/info?{sent} answered {status}, not 200"
                expect(page.locator("#dl-stl")).to_have_attribute(
                    "href", f"api/model.stl?{sent}", timeout=BUILD_WAIT_MS
                )
                assert page.locator("label.field.invalid").count() == 0
                assert page.locator("#messages .error").count() == 0
                assert eval_str(page, FRAGMENT) == sent
                status, _ = _api_get(server, "/api/info", BLANK_LINK)
                assert status == 422, f"the API answered {status} for the raw blank link"

                sent = _follow_link(page, UNKNOWN_KEY_LINK)
                assert _pairs(sent) == [("face_width", "9")], f"the unknown key link sent {sent!r}"
                status, _ = _api_get(server, "/api/info", sent)
                assert status == 200, f"/api/info?{sent} answered {status}, not 200"
                expect(page.locator("#dl-stl")).to_have_attribute(
                    "href", f"api/model.stl?{sent}", timeout=BUILD_WAIT_MS
                )
                assert eval_str(page, FRAGMENT) == sent

                # L49 (WR-02): the box blanks `5.`, so the API refuses it as written and no
                # part is built under a blank box.
                stl_before = _stl_requests(seen)
                sent = _follow_link(page, ACCEPTED_LINK)
                assert _pairs(sent) == [("face_width", "5.")], f"the refused link sent {sent!r}"
                status, body = _api_get(server, "/api/info", sent)
                assert status == 422, f"/api/info?{sent} answered {status}, not 422"
                assert isinstance(body, dict), f"/api/info?{sent} is not an object"
                assert body["detail"][0]["type"] == "number_as_written", body
                marked, texts = _expected_422(properties, body)
                assert marked == {_title(properties, "face_width")}, sorted(marked)
                expect(page.locator("#messages .error")).to_have_text(texts, timeout=BUILD_WAIT_MS)
                expect(page.locator("label.field.invalid .name")).to_have_text(sorted(marked))
                assert page.locator("#dl-stl").get_attribute("href") is None, (
                    "the STL link has an href for a link the API refuses as written"
                )
                page.wait_for_timeout(DEBOUNCE_SETTLE_MS)
                assert _stl_requests(seen) == stl_before, "the page asked for an STL after it"
                print("blank, unknown and refused: face_width=8, face_width=9, face_width=5.")
            with step("root_fillet label", no_foreign_key):
                # D-09, D-10: while a hob root is in force the row reads "Hob tip radius used",
                # else "Root fillet used"; the key is the info document's `root_form_d`, so a
                # trochoid request that fell back to radial never reads as the hob.
                row_labels: list[str] = []
                for link in LABEL_LINKS:
                    sent = _follow_link(page, link)
                    status, body = _api_get(server, "/api/info", sent)
                    assert status == 200, f"/api/info?{sent} answered {status}, not 200"
                    assert isinstance(body, dict), f"/api/info?{sent} is not an object"
                    assert body["root_fillet"] is not None, f"/api/info?{sent} has no root_fillet"
                    hob = body["root_form_d"] is not None
                    expected = "Hob tip radius used" if hob else "Root fillet used"
                    absent = "Root fillet used" if hob else "Hob tip radius used"
                    # The rows are written before the STL request, so the href for this very
                    # query means the rows are this link's.
                    expect(page.locator("#dl-stl")).to_have_attribute(
                        "href", f"api/model.stl?{sent}", timeout=BUILD_WAIT_MS
                    )
                    dim_labels = page.locator("#dims dt").all_text_contents()
                    assert expected in dim_labels, (
                        f"#{link}: the rows {dim_labels} lack {expected!r}"
                    )
                    assert absent not in dim_labels, (
                        f"#{link}: the rows {dim_labels} hold {absent!r}"
                    )
                    row_labels.append(expected)
                assert row_labels == [
                    "Hob tip radius used",
                    "Root fillet used",
                    "Root fillet used",
                ], f"the label follows the request and not the build: {row_labels}"
                print(f"root_fillet label per link {LABEL_LINKS}: {row_labels}")
            # The sweep's page sends one api/info request per record by itself, so a recorder
            # that missed any page but the main one would count fewer than that (24-RESEARCH
            # Finding 9): the count is what shows every page was watched.
            no_foreign_key()
            info = [url for url in seen if urllib.parse.urlsplit(url).path == "/api/info"]
            assert len(info) > len(fixture_hashes()), (
                f"the recorder saw {len(info)} api/info requests, not more than the "
                f"{len(fixture_hashes())} the sweep alone sends: a page went unwatched"
            )
            print(
                f"request recorder: {len(seen)} /api requests ({len(info)} api/info) from "
                "every page, every key a GearParams field, quality or mate_teeth"
            )
        finally:
            browser.close()
