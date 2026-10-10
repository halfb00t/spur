# web-ui

`src/spur/static/` (served) and `web/` (build-time only).

## Responsibility

A form, a live three.js preview, the measured dimensions, and download links — with every
parameter in the URL so a gear can be shared as a link.

## Boundaries

- **The runtime needs no Node** (L11). `static/vendor/three.bundle.min.js` is a committed,
  tree-shaken esbuild output; `web/` exists only to regenerate it, and CI fails if the
  committed bytes differ from a fresh build.
- The UI knows no gear geometry. The form is generated from `GET /api/schema`, including
  each field's group, unit and step, so a parameter added in `params.py` appears here
  with no edit (L02).
- All URLs are relative, so `SPUR_ROOT_PATH` works — with the caveat that the proxy must
  redirect `/spur` to `/spur/`, or the browser resolves `static/app.js` one level too
  high. That is documented in the README because it cannot be fixed from inside the app.

## Shape

`app.js`, roughly in this order: build the form from the schema; read the hash into the
inputs; on change, debounce, cancel the in-flight request (`AbortController`), fetch
`/api/info` and `/api/model.stl?quality=preview`, update the dimensions table, the
warnings and the invalid-field marks, then load the STL into the scene. A `seq` counter
drops responses that arrive out of order. The viewer is a `WebGLRenderer` with
`OrbitControls`, a key light that follows the camera, an edges overlay and a grid placed
under the part; colours come from CSS custom properties, so light and dark themes are one
source.

`entry.js` names the twelve three.js exports the viewer actually uses — that list is what
makes the bundle small.

## Errors

`422` bodies are read back and rendered twice: the message in the messages strip, and the
`detail[].ctx.fields` names as an `invalid` class on the inputs responsible. Warnings from
`derive()` render in the same strip in a different tone.

## Known gap

Aborting in the browser cancels the *request*, not the server-side build — dragging a
slider still queues work nobody will read (`app.js` update loop). Tracked in
`docs/tech_debt/active/2026-09-21-no-server-side-cancellation.md`.

## Tests

Thin, and honestly so: `tests/test_api.py` asserts `/` and the static assets are served
and that the schema carries the metadata the form depends on.

`tests/test_browser.py` is the one test that runs `app.js`, in Chrome Headless Shell against a
real `uvicorn` with the shipped pool. It proves that WebGL2 exists; that the form is built
from `/api/schema`; that the first part is drawn, with `canvas.dataset.triangles` equal to
the STL header's count; that both `422` paths mark their fields; that the rendered warnings
equal `/api/info`'s; that the shareable link round-trips on load, on Reset and on
`hashchange`; and that the query the page sends for each record of the regression fixture
equals the pin in `tests/regression/golden_requests.json` (rewritten only by
`make golden.regen`, in a commit of its own). `#root_shape=bogus` is pinned as today's
behaviour and filed as debt. It runs inside `make verify` and CI's `test (3.12)`, which
install the headless shell under `.venv` first; the commit-time `make verify.fast` never
collects it.

Rebuild the bundle: `make vendor`. Check it still matches: `make vendor-check`.
