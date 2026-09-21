# A browser test for the viewer

Date: 2026-09-21
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
