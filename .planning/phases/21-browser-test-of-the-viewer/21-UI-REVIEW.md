# Phase 21 — UI Review

**Audited:** 2026-10-10
**Baseline:** abstract 6-pillar standards (no UI-SPEC.md)
**Screenshots:** not captured. Nothing visual changed, so a capture would show the pre-phase UI. The gitignore gate was not run for the same reason, and because the brief forbids touching other files.
**Interaction captures:** off (workflow.ui_interaction_capture is false). Interaction findings are code-derived.

---

## Scope verification

`git diff 592506f -- src/spur/static/app.js src/spur/static/style.css src/spur/static/index.html` shows exactly one hunk, in `app.js` `showModel`: 2 added lines, a comment and `canvas.dataset.triangles = String(geometry.attributes.position.count / 3);`. `style.css` and `index.html` have no diff. The brief's scope claim holds.

The line writes a `data-triangles` attribute on the canvas. It has no CSS, layout, text or event effect, and it is invisible to users. It is a test hook, not UI.

---

## Pillar Scores

Pillars with nothing phase-attributable are marked N/A, not scored. The overall score covers only the pillars that were graded.

| Pillar | Score | Key Finding |
|--------|-------|-------------|
| 1. Copywriting | N/A | The phase added no user-facing strings. |
| 2. Visuals | N/A | The phase changed no pixels. |
| 3. Color | N/A | The phase added no color usage. |
| 4. Typography | N/A | The phase added no type styles. |
| 5. Spacing | N/A | `style.css` is unchanged. |
| 6. Experience Design | 3/4 | The hook is correct and non-regressive, but it is unguarded and untyped. |

**Overall: 3/4 on the one graded pillar. There is no meaningful /24 total.** Summing five N/A pillars to 24 would invent a score. This phase neither improved nor harmed the UI's visual quality.

---

## Top Fixes

1. **WARNING: the `canvas.dataset.triangles` write is an unguarded, silent contract.** If `showModel` is refactored, or the STLLoader stops returning non-indexed geometry, the value silently becomes wrong. `position.count / 3` is only the triangle count for non-indexed geometry. The comment says so, which is good. But `String(1.5)` would render a fractional value if the geometry were ever indexed or malformed. Phases 23–24 assertions sit on this attribute, so the test side should assert an integer, not just equality with the STL header.
2. **WARNING: stale value on failed rebuild.** The attribute is written only on success, in `showModel`. If a later request errors, the canvas keeps the previous model's `data-triangles` while the page shows an error state. Any test that reads it after a failure sees a plausible stale number. Clear it, or document that tests must wait for the model-loaded signal.
3. **Minor: confirm the attribute is not part of the shipped UX surface.** It is exposed to anyone inspecting the DOM and to user scripts. It is harmless, but `docs/architecture/web-ui.md` was updated in this phase. Check that it names the attribute as test-only.

---

## Detailed Findings

### Pillars 1–5: not phase-attributable

The brief's scope facts are confirmed, so there is nothing to grade.
- Copywriting: no strings were added or changed. The only user-visible text the tests pin (the warning renders as exactly the `/api/info` text) is pre-existing behavior that the phase now verifies.
- Visuals, Color, Typography and Spacing: no HTML or CSS diff, and the new JS line does no styling.

Grading the untouched UI would credit or blame this phase for work it did not do.

### Pillar 6: Experience Design (3/4)

Positive evidence:
- The hook adds no new interaction, state or visible behavior. It cannot regress loading, error or empty states.
- It is placed after `scene.add(mesh, edges)`, so it reflects the actually-drawn model, not a request in flight.
- The comment states why and gives the non-indexed assumption.
- The phase's indirect experience contribution is real. Tests now pin the form-from-schema build, 422 field marking, warning text, the first STL draw, hash round-trip, Reset and `hashchange`, which were previously unverified in a real browser. The query-string pins for the 44 fixture records protect users' shareable links (L05).

Deductions (why not 4):
- Findings 1 and 2 above: the observable can be stale or fractional without any signal.
- `#root_shape=bogus` is pinned "as it behaves today" and filed as debt (`2026-10-10-root-shape-bogus-loads-a-blank-select`). A user following that link gets a blank select. The phase documents the defect but does not fix it, which was intended. It is still a known experience defect shipping behind a passing test, and a future fix has to change a pin.

---

## Registry Safety

Not applicable: no `components.json` and no shadcn use.

---

## Files Audited
- `src/spur/static/app.js` (diff hunk around line 311)
- `src/spur/static/style.css` and `src/spur/static/index.html` (confirmed unchanged by diff)
- Phase 21 CONTEXT and the diff stat. The test files (`tests/test_browser.py`, `tests/browser_session.py`) were not audited as UI.
