# Phase 33 — UI Review

**Audited:** 2026-10-28
**Baseline:** abstract 6-pillar standards (no UI-SPEC.md)
**Screenshots:** not captured fresh. The six committed 33-08-shaft-{default,longest,widest}{,-after}.png were reviewed (default-after and longest-after were opened). No live server was started.
**Interaction captures:** off (workflow.ui_interaction_capture is false). Every interaction finding below comes from reading the code.

---

## Pillar Scores

| Pillar | Score | Key Finding |
|--------|-------|-------------|
| 1. Copywriting | 3/4 | Specific, part-aware texts. Raw `404 Not Found` and `Failed to fetch` strings reach the user, and the sub line drops "parametric". |
| 2. Visuals | 3/4 | The Part switch is the lowest-weight element on the page. The longest shaft is a thin sliver in a mostly empty canvas. |
| 3. Color | 3/4 | Tokens are clean and there are no hardcoded colors. In dark mode, white on the `#e0573f` primary buttons is about 3.7:1, below AA for 14px text. |
| 4. Typography | 3/4 | There are 5 distinct sizes (14px, .75, .78, .85, 1.1rem). Three of them sit within .07rem of each other. |
| 5. Spacing | 3/4 | Spacing is consistent but hand-tuned rem values with no scale. On narrow screens the switch moves below the fold. |
| 6. Experience Design | 3/4 | State coverage is good (Building…, last-valid status, formSeq races). The refused-link state leaves a live-looking, inert form, and a switch silently discards edits. |

**Overall: 18/24**

---

## Top 3 Priority Fixes

1. **Part switch is buried on small screens** — At max-width 820px `#view` gets `order:-1`, so the `<aside>` holding the Gear|Shaft radios comes after the 55vh canvas and the whole results block. A phone user has to scroll past everything to find the primary control of the page. Fix: move `.part-switch` out of `<aside>`, into the header or above `main`, or keep it first in the mobile order.
2. **Refused-link state is a dead form** — `update()` returns while `refused` is set (app.js:421), so the gear form shows at defaults, looks editable, and typing builds nothing. The only cue is one red message in the bottom-left column. Fix: dim or `inert` the form while refused, or let an edit end the refused state, and put the message beside the switch.
3. **Dark-mode primary button contrast** — `.btn.primary` is `--accent-fg:#fff` on `--accent:#e0573f` (style.css:35 and :11). That is about 3.7:1 for 14px text, below the 4.5:1 AA threshold. The download buttons are the page's main action. Fix: define a darker dark-mode accent for fills, or use dark text on it.

Further issues, not in the top 3:

4. Switching part discards typed values with no warning or undo (D-13, by design). The cost is lost work. Consider one line of hint text or a remembered per-part state.
5. Raw transport strings are shown: `Could not build the form: ${status} ${statusText}` (app.js:94, 201, 282) and `Request failed: Failed to fetch`. Replace them with a retry-oriented sentence.
6. The longest shaft renders as a sliver (33-08-shaft-longest-after.png): about 215px tall and under 10px wide in a 930x320 canvas. It is whole and in view, but features are unreadable. The Fit framing could fill the height better, or the viewport could be taller than the 320px min-height.
7. The radios have no `checked` in `index.html`; JS sets them. With scripts off or before the bootstrap, neither is selected, which contradicts the gear page the CSS defaults to.

---

## Detailed Findings

### Pillar 1: Copywriting (3/4)
- **Good:** per-part title, sub, aria-label and Fit tooltip live in the `PARTS` descriptor (app.js:59-72).
- **Good:** the shaft hint (index.html:51) says what the numbers are and where the warnings are.
- **Good:** the refused-link message names the offending value, JSON-quoted, and the way out: `Unknown part "bogus" in the link; use the Gear or Shaft switch` (app.js:258).
- **Warning:** the sub line `DIN 5480 splined shaft` drops "parametric", while the gear's reads `parametric involute spur gear`. The two are inconsistent.
- **Warning:** app.js:201 and 282 surface `Could not build the form: 404 Not Found`, and app.js:461 surfaces `Request failed: Failed to fetch`. These are developer strings with no next step.
- **Warning:** the refused message has no terminal period, unlike the other messages.
- **Warning:** the `fit` field's help is a `<small>` shown only on `:focus-within` (style.css:215). A touch user with no hover never sees the `8f`-style format help.

### Pillar 2: Visuals (3/4)
- **Good:** in the shaft screenshots the canvas is the focal point. Grid and part contrast is fine, and the `gridAlong` fix made the floor grid visible for long shafts.
- **Warning:** `.part-switch` reuses the muted 12px uppercase legend with a top border (style.css:58-66, 85). It looks like a form section divider, not a mode switch. Two 14px radios give the lowest visual weight to the control that changes the whole page.
- **Warning:** the longest shaft occupies about 3% of the canvas width, which wastes the viewport.
- **Warning:** the canvas `aria-label` says only `3D preview of the shaft`. There is no text equivalent, though the results table partly provides one.
- The Fit button is a text button, not icon-only, so no aria gap.

### Pillar 3: Color (3/4)
- All colors are CSS custom properties with a dark variant. A grep for hardcoded colors finds them only in `:root` and in the favicon.
- The accent is limited to links, primary buttons and the invalid outline. This is good restraint, but `a { color: var(--accent) }` makes the API link accent as well, and the 60/30/10 split is not documented.
- **Warning:** dark-mode `.btn.primary` is white on `#e0573f`, about 3.7:1, which fails AA for normal text. The light theme (`#b8412c`, about 5.5:1) passes.
- **Warning:** the disabled download buttons use `opacity:.45`, which lowers contrast further. This is acceptable as "disabled", but there is no reason text for why they are disabled.
- `.inactive` fields rely on `--muted` plus a dashed border. The reason row carries the real information, so that is fine.

### Pillar 4: Typography (3/4)
- Sizes in use: 14px base, .75rem (legend), .78rem (small, reason, hint), .85rem (unit, status, messages) and 1.1rem (h1). The .75, .78 and .85 steps are nearly indistinguishable and could collapse to two.
- Weights: 500 (names) and 600 (legend), so 2 weights. This is fine.
- Tabular-nums is applied to inputs and result values, which is correct for a measurement tool.
- The h1 `spur` is 1.1rem, barely larger than body text. The page title is understated, and the sub line does the identifying work.

### Pillar 5: Spacing (3/4)
- Spacing is applied consistently: .5rem field margin, .75rem gaps, 1rem aside padding. But it is raw rem with no named scale: .1, .15, .25, .3, .35, .4, .45, .5, .6, .75, .8, .85, 1.25 and others. There are more than 12 distinct values.
- There are no arbitrary-pixel Tailwind-style values, because this is plain CSS.
- **Warning:** the mobile layout (style.css:195-202) puts the switch and form after the canvas and results. See fix 1.
- The `#dims` auto-fill grid with a 12.5rem minimum copes with the longer shaft row labels. No overflow was visible in the screenshots, though a screenshot of the results table was not reviewed.

### Pillar 6: Experience Design (3/4)
- **Good:** the status line shows `Building…` and `Showing the last valid shaft`. Stale builds are dropped through `formSeq` and `seq`, and in-flight requests are aborted on a new edit. Invalid boxes get an `.invalid` outline plus a message. Inert fields are dimmed with a reason, and `aria-describedby` is wired.
- **Good:** the mate box and the other part's hint are hidden through CSS on `body[data-part]`, so there is no flash and no script-written hiding.
- **Good:** the radios keep native arrow-key switching, and `markPart` follows the real part, not the click.
- **Warning:** the refused state leaves both radios unchecked, the gear form at defaults, and no preview. Edits and Reset do nothing, silently apart from the one message, which is the live-looking dead form of fix 2.
- **Warning:** a switch resets all values (D-13) with no confirmation. For 8 shaft fields or 31 gear fields that is a real loss, and there is no undo.
- **Warning:** there is no loading state for the form itself. During `buildForm` the old part's form is cleared first, so the aside is blank until the schema fetch returns. This is not a skeleton, though it is a brief flash.
- Downloads are disabled anchors (`aria-disabled`, no href) until a build succeeds. They are not focusable, and nothing explains why they are off. This is a minor gap.
- Registry audit: not applicable (no `components.json`).

---

## Files Audited
- /Users/half/git/halfb00t/spur/src/spur/static/index.html
- /Users/half/git/halfb00t/spur/src/spur/static/app.js (PARTS, buildForm, switchTo, markPart, followHash/refuseLink, update, showMessages)
- /Users/half/git/halfb00t/spur/src/spur/static/style.css
- /Users/half/git/halfb00t/spur/.planning/phases/33-interfaces-and-parity/investigation/33-08-shaft-default-after.png
- /Users/half/git/halfb00t/spur/.planning/phases/33-interfaces-and-parity/investigation/33-08-shaft-longest-after.png
- /Users/half/git/halfb00t/spur/.planning/phases/33-interfaces-and-parity/33-06-SUMMARY.md, 33-07-SUMMARY.md and 33-08-SUMMARY.md
