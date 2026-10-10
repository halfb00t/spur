# A browser test for the viewer

Date: 2026-09-21
Status: retired
Retired in: docs(21): log L39 and retire the browser-test idea -- a headless browser runs in make verify and CI
Source: writing docs/architecture/web-ui.md — noticed the UI has no automated coverage
Related files:
- src/spur/static/app.js
- tests/test_api.py (the only thing that touches the UI today, and only that it is served)

## Context

`tests/test_api.py` asserts that `/`, `static/app.js` and the vendored bundle are served,
and that `/api/schema` carries the metadata the form is generated from. Nothing checks
that the form actually builds, that an invalid field gets marked, that a warning renders,
or that the STL loads into the scene. The schema-shape test is a decent proxy for the
form generation and nothing else is covered.

## Why it matters

The UI is the product for most users, and the failure modes it has are ones the Python
tests structurally cannot see: a renamed CSS custom property, a `detail[].ctx.fields`
shape change, an ordering bug in the debounce/abort loop.

## Next step

Revisit when a UI regression actually reaches someone, or when the UI grows past the
single `app.js`. The first decision is not which framework but whether a headless browser
belongs in `make verify` at all — it would make the gate slower and need Node at test
time, which the runtime deliberately does not (L11). A cheaper first step: assert the
schema→form contract more strictly from Python.

## Phase 12 (2026-09-30)

12-07 took this file's own "cheaper first step" — asserting the schema→form contract more
strictly from Python — in
`tests/test_api.py::test_the_shareable_link_round_trips_every_field_through_generic_code`
(D-11, D-14). The cost question (whether a headless browser belongs in `make verify` at
all) stays open.

New trigger: revisit when either UI idea above is taken.

## Outcome

Phase 21 built it. L39 records the placement (`tests/test_browser.py` inside `make verify` and CI,
out of the commit slice) and its measured price, which the human accepted. The worry above that a
headless browser would "need Node at test time" is answered by L11 restated: the Playwright driver's
Node ships inside the dev wheel and runs at test time only, and the runtime has none. The two UI
ideas this was the trigger for are now open to Phases 23 and 24.
