# A hex bore warns that the default bore_d and bore_flat are ignored, on every hex link

Severity: nice
Status: active
Date: 2026-10-11
Source: Phase 23 discuss-phase (`.planning/phases/23-conditional-form-fields/23-CONTEXT.md`) and REQUIREMENTS.md "Form follow-ups (v0.5.x)"
Related files:
- src/spur/calc.py:1166 (the "Hex bore replaces the round profile: ... ignored" sentence)
- src/spur/params.py:102 (`bore_d` default 9.0) and src/spur/params.py:105 (`bore_flat` default 8.0)
- tests/test_browser.py:425 (the `warning rendered` step's `bore_hex=6` link)

## Context
`?bore_hex=6` answers `Hex bore replaces the round profile: bore_d (9 mm) and bore_flat
(8 mm) are ignored.` because the defaults are 9 and 8 (L05 keeps them), so every hex link
warns about values nobody set (PITFALLS M-7). Since L41 the form also dims both fields with
`Needs Hex bore A/F = 0`.

## Why it matters
A warning on every hex part trains users to skip warnings, which is where L08 puts what
could not be computed honestly.

## Next step
A `calc` change, never a filter in `app.js`: name only the bore fields the request set. Two
candidates for the human: `model_fields_set`, or a value that differs from its default. It
rewrites `warnings` for every hex link that omits them, and the `warning rendered` step's
`bore_hex=6` expectation (no fixture record sets `bore_hex`; re-check at the time). Revisit
when Phase 24's bore-shape selector ships (choosing Hex leaves both defaults, so every hex
part warns) or a user reports the warning as noise.

<!-- On resolve: set Status: resolved, add `Resolved in: <commit sha>`,
     git mv into resolved/, move the INDEX row to Resolved — same commit as the fix. -->
