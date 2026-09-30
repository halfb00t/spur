# Conditional form fields ("disabled when")

Date: 2026-09-29
Source: Phase 11 discuss-phase (11-CONTEXT.md Deferred Ideas)
Related files:
- src/spur/static/app.js (schema-driven group renderer)
- src/spur/params.py (Spokes, Holes, Honeycomb groups)
- docs/architecture/decision_log.md (L30, D-15)

## Context

08's deferred idea named its own trigger as "Phase 9 or 11 accumulates more
ignored-when relations than a warning sentence carries well". D-15 adds three more this
phase: a spoke, hole or honeycomb dimension set while its own count/selector field is 0
is ignored and warned about, on top of the keyway and hex-bore ignored-field warnings
Phases 8 and 9 already ship. The web form still renders every field regardless of
whether it currently does anything, and the only signal that a value is inert is a
warning sentence returned after the fact.

## Why it matters

A clearer web form — dimming or hiding a group's fields while its selector is 0 would
tell the user before they set a value that will be ignored, not after. Purely a UI
concern; the API and CLI already say so in `warnings`.

## Next step

Weigh at Phase 12's UI pass, against the whole v0.2 field set (including the bore-shape
selector idea, `docs/ideas/2026-09-27-bore-shape-selector-in-the-web-form.md`, which
raises the same "several fields' relevance depends on another field" question).

## Judged at Phase 12 (2026-09-30)

Verdict: not taken; 08 D-09 stands (the form is generated from `/api/schema` and nothing
else).

Reason: a proof-and-measurement phase must not ship the first bore-specific (or
field-relation) logic in `app.js` with no UI test; the ignored-field warnings are the
current, honest signal.

New trigger: revisit when a browser test exists, or a user reports the ignored-field
warnings as insufficient.

If taken, the schema-driven route is a `json_schema_extra` key on the model (on the order
of `enabled_when`), not relations hard-coded in `app.js`, superseding 08 D-09 with a new
`Lxx`.
