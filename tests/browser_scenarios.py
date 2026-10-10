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
import urllib.request
from collections.abc import Iterator

import pytest
from browser_session import (
    BUILD_WAIT_MS,
    PNG_RATIO_BAR,
    eval_opt_str,
    launch,
    serve,
    step,
    stl_triangles,
)
from playwright.sync_api import Page, Route, expect, sync_playwright

STL_ROUTE = "**/api/model.stl*"

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


def _schema_field_count(base: str) -> int:
    with urllib.request.urlopen(f"{base}/api/schema", timeout=10) as response:
        schema: object = json.load(response)
    assert isinstance(schema, dict), "/api/schema is not an object"
    properties = schema["properties"]
    assert isinstance(properties, dict), "/api/schema has no properties"
    return len(properties)


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
    field_count = _schema_field_count(server)
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
        finally:
            browser.close()
