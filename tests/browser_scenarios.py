"""The shipped viewer in a real browser: what no Python test can see.

`TestClient` tests prove the API answers; none of them runs `app.js`. This module opens the
page the product ships, in Chrome Headless Shell, against a real `uvicorn`, and checks what
only a browser can: that WebGL2 exists (without it the page builds no form at all,
app.js:229), that the first part is actually drawn, that the scene holds as many triangles
as the STL it was fed, and that the download link appears only after the model was shown.

Staging module (PD-01): pytest collects it only when it is named on the command line, so
neither `make verify` nor the commit-time slice runs it until 21-06 renames it
`tests/test_browser.py` in the single commit that adds every exclusion. Quick run:

    make .venv/.browser && make test PYTEST_ARGS="tests/browser_scenarios.py -n0 --no-cov -q"

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
from collections.abc import Iterator

import pytest
from browser_session import (
    BUILD_WAIT_MS,
    PNG_RATIO_BAR,
    STL_ROUTE,
    eval_opt_str,
    eval_str,
    eval_str_list,
    launch,
    serve,
    serve_stl_from,
    step,
    stl_triangles,
)
from playwright.sync_api import Page, Route, expect, sync_playwright

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
    with page.expect_request(lambda request: "/api/info" in request.url) as sent:
        page.evaluate("(f) => { location.hash = f; }", fragment)
    return urllib.parse.urlsplit(sent.value.url).query


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


def test_the_shipped_viewer_in_a_real_browser(server: str) -> None:
    """Opens the shipped page and draws the first part; costs are in bench/RESULTS.md."""
    properties = _schema_properties(server)
    field_count = len(properties)
    parked: list[Route] = []

    with sync_playwright() as pw:
        # In the body, not a fixture: a missing shell must be a FAILED test with the install
        # command in its message, not an ERROR and not a skip (D-02, D-07).
        browser = launch(pw)
        try:
            page = browser.new_page()

            with step("webgl2"):
                renderer = eval_opt_str(page, WEBGL2_PROBE)
                assert renderer is not None, (
                    "this browser gives no WebGL2 context: the viewer builds no form without "
                    "WebGL (app.js:229)"
                )
                print(f"webgl2 renderer: {renderer}")

            # A lambda, never the bound `parked.append`: Playwright rejects a builtin
            # method as a handler at run time, although mypy accepts it.
            page.route(STL_ROUTE, lambda route: parked.append(route))
            page.goto(server + "/")

            with step("form built"):
                expect(page.locator("form#params [name]")).to_have_count(field_count)
                _wait_until_parked(page, parked)
                assert page.locator("#dl-stl").get_attribute("href") is None, (
                    "the STL link has an href before any STL was shown"
                )

            with step("form from schema"):
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

            with step("first build drawn"):
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

            with step("href after showModel"):
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

            with step("invalid field marked"):
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

            with step("warning rendered"):
                # Equality of ordered lists, against links whose API answer holds two warnings,
                # one warning and none: the two-warning link is what separates "renders the
                # list" from "renders something that contains the first warning". The STL is
                # fulfilled from the first build (serve_stl_from), so nothing here builds.
                counts: list[int] = []
                for fragment, at_least in (
                    ("module=1&pressure_angle=14.5", 2),
                    ("bore_hex=6", 1),
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
        finally:
            browser.close()
