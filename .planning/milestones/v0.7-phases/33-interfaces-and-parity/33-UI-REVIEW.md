# Phase 33 — UI Review (re-audit after 33-10)

**Audited:** 2026-10-29
**Baseline:** abstract 6-pillar standards (no UI-SPEC.md)
**Screenshots:** captured live from `make serve` (Chromium headless shell 1228, light and dark): desktop 1440, tablet 768, mobile 375, `#part=bogus`, `#part=shaft`. Stored in the scratchpad, not in the repo. Prior-fix measurements were taken as computed style in the browser.
**Interaction captures:** off (workflow.ui_interaction_capture is false). Interaction findings are code-derived.

---

## Prior findings, confirmed on the shipped page

| Prior finding | Result |
|---|---|
| Switch below canvas under 820 px | FIXED. At 375 and 768 px the switch top is 56.8 and the canvas top 109.2. The order is header, PART, canvas, downloads and results, then form (light-mobile, light-shaft-mobile). No horizontal overflow (scrollWidth equals innerWidth). |
| Refused link leaves a live-looking form | FIXED visually. With `#part=bogus` (light and dark) `body[data-refused]` is set, both radios are unchecked, the downloads and form are dimmed, and the switch has a 2 px accent outline (dark-refused.png). The message reads `Unknown part "bogus" in the link; use the Gear or Shaft switch`. |
| Dark primary button contrast 3.7:1 | FIXED. Computed light 5.48:1 (white on #b8412c), dark 4.85:1 (#131619 on #e0573f). |

Known filed debt, not re-filed: dark-mode header link text at 4.47:1 (`docs/tech_debt/active/2026-10-29-dark-mode-link-text-under-wcag-aa.md`). It is visible as the orange `API` link in the dark header.

---

## Pillar Scores

| Pillar | Score | Key Finding |
|--------|-------|-------------|
| 1. Copywriting | 3/4 | Specific, part-aware text. The shaft sub line still drops "parametric". The raw transport strings from the last audit were not re-checked or fixed (no plan touched them). |
| 2. Visuals | 3/4 | Mobile shaft page: six stacked amber warnings (about 600 px) sit between the downloads and the numbers. The refused outline crowds the TEETH legend. |
| 3. Color | 3/4 | Tokens only, and the primary-button pair now passes in both themes. Dark link text is 4.47:1 (filed). Disabled buttons use opacity .45, which lowers contrast further. |
| 4. Typography | 3/4 | Unchanged: 5 sizes, 2 weights. .75, .78 and .85rem are nearly indistinguishable. The h1 is 17.6px, barely above the 14px body. |
| 5. Spacing | 3/4 | The narrow layout now reads like the desktop column. Spacing is still a set of hand-tuned rem values with no scale. |
| 6. Experience Design | 3/4 | The refused state is now clearly inert to the mouse. The fields stay keyboard-focusable, and typing in them does nothing with no cue. A part switch still discards values (D-13). |

**Overall: 18/24.** The score is unchanged because the three fixes closed named defects without lifting any pillar past "minor issues remain". The audit found new minor issues. Scores are not raised for effort.

---

## Top 3 Priority Fixes

1. **Warning wall on the mobile shaft page** (`#part=shaft` at 375 px, light-shaft-mobile.png). Six full-width amber paragraphs push the results table and the whole form about 1,100 px below the canvas. On a phone the user must scroll past roughly 600 px of standing caveats (the same text on every shaft) before reaching any input. Fix: collapse the standing warnings into a `<details>` or a one-line "6 notes" toggle under 820 px. Keep the L08 content intact and keep errors expanded. WARNING.
2. **Refused form is still keyboard-reachable.** The CSS comment in style.css admits that focus still reaches the fields and typing builds nothing, because `inert` is barred by the `writes_a_field_shut` guard (L41). A keyboard or screen-reader user sees no cue, and the dimming is purely visual. Fix: give the dimmed block `aria-describedby` pointing at the refusal message, or add a one-line note in `#messages` saying edits are ignored until a part is chosen. Either stays within L41 and D-15. WARNING.
3. **Disabled-button and refused dimming stack on contrast.** `opacity: .45` on the downloads and on the whole refused form takes already-muted text well below 4.5:1 (visible in dark-refused.png, where the field labels turn faint). It is conventional for disabled controls, but in the refused state it dims the labels the user must read to understand what is on the page. Fix: dim only the inputs and keep `.name` labels at full opacity. WARNING.

Further issues, not in the top 3:

4. Switching part discards typed values (D-13, by design) with no warning or undo.
5. The sub line `DIN 5480 splined shaft` is inconsistent with `parametric involute spur gear`.
6. The refused outline has a 4 px offset that reaches the next section's legend (TEETH, 8 px below). It reads cleanly but with no breathing room.
7. Field help for `fit` shows only on `:focus-within` (style.css:215), so touch users never see it.
8. Numbers use the locale decimal comma (`1,75`, `0,15`). That is correct for the headless locale, but the unit labels and warnings use periods (`22.125 mm`). The mixed notation is jarring in one view.
9. Carried from the last audit and not touched by 33-10: raw `404 Not Found` and `Failed to fetch` strings, the dark-mode radio ring faintness, and the longest-shaft sliver in the canvas.

---

## Detailed Findings

### Pillar 1: Copywriting (3/4)
- Good: the refusal message names the bad value and the way out. Part-aware titles and hints are in place.
- Warning: the sub line is inconsistent between parts (finding 5).
- Warning: error strings built from `status statusText` (app.js:94, 201, 282) and `Request failed: ...` are developer text. These were not re-exercised here.
- Warning: the shaft warnings are accurate but long. Each runs 3-6 lines on mobile. They are honest per L08, but they are written as spec notes, not user guidance.

### Pillar 2: Visuals (3/4)
- Good: the switch is first under 820 px and the canvas is the focal point. The gear and shaft previews render with a visible grid in both themes.
- Warning: the shaft warning stack dominates the mobile page (fix 1).
- Warning: the PART switch is still a muted 12px uppercase legend with two 14px radios. It is now findable on mobile but still low-weight. The refused outline is the only time it gets emphasis.
- Warning: the canvas `aria-label` gives no text equivalent. The results table partly serves.

### Pillar 3: Color (3/4)
- Verified: dark primary 4.85:1, light 5.48:1. The accent is restricted to links, primary buttons, the invalid outline and the refused outline.
- Warning: dark link text at 4.47:1 (filed debt).
- Warning: the opacity-based dimming on the refused form (fix 3).
- Hardcoded colors appear only in `:root` and the dark-theme block.

### Pillar 4: Typography (3/4)
- Sizes: 14px base, .75, .78, .85 and 1.1rem. Weights: 500 and 600. Tabular numerals are applied to inputs and results.
- Warning: three near-identical small sizes. The h1 is understated.

### Pillar 5: Spacing (3/4)
- Good: the 820 px block (`display: contents` on the aside, `order`, `margin-inline: 1rem`) reproduces the desktop padding. The switch has `padding-bottom: .6rem`, and the canvas no longer touches it.
- Warning: more than 12 distinct rem values with no scale.
- Warning: the 4 px refused-outline offset against `fieldset` margin .75rem leaves 8 px to the next legend.
- Tablet at 768 px uses the single-column layout, so a 768 px-wide iPad gets a 55vh canvas with the form far below. This is by the 820 px breakpoint and is acceptable, but the layout is not tuned for that width.

### Pillar 6: Experience Design (3/4)
- Good: refused state is now unmistakable to a pointer user. Building, last-valid and stale-build handling are as before. Console errors: none in any of the 12 loads.
- Warning: the keyboard gap (fix 2).
- Warning: part switch discards values with no undo (D-13).
- Warning: the form is cleared during `buildForm` until the schema returns (not re-measured).
- Warning: disabled download anchors are not focusable and give no reason.
- Registry audit: not applicable (no `components.json`).

---

## Files Audited
- /Users/half/git/halfb00t/spur/src/spur/static/index.html
- /Users/half/git/halfb00t/spur/src/spur/static/style.css (read in full)
- /Users/half/git/halfb00t/spur/src/spur/static/app.js (not re-read in full; cited from the prior audit and 33-10-SUMMARY)
- 33-10-SUMMARY.md, 33-UAT.md and the prior 33-UI-REVIEW.md
- Live captures (scratchpad): light and dark x desktop, mobile, tablet, refused, shaft, shaft-mobile
