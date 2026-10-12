# Phase 24 — UI Review

**Audited:** 2026-10-12
**Baseline:** abstract 6-pillar standards (no UI-SPEC.md). The contract used for intent is 24-CONTEXT.md D-01 to D-19.
**Screenshots:** not captured. This was a code-derived audit, as in Phase 21. No dev server was started, and no capture was attempted. Every visual finding below is read from the CSS and the JS, not seen. Treat the contrast and "does the pending state read" claims as unverified until someone looks at it in both themes.
**Interaction captures:** off (workflow.ui_interaction_capture is false). Interaction findings are code-derived from `git show 470b78a`.

---

## Scope verification

The diff of `470b78a` in `app.js` adds `buildSelectors`, `deriveSelectors`, `pick` and `pend`, the `stash` map, one call in `buildForm`, and one call each at the three derive sites. `style.css` shares the `.field` grid rules with `.selector` and adds `.selector.pending`. `index.html` is not touched. The brief's scope claim holds. The select has no `name`, so `fields` and `gearQuery()` cannot see it.

---

## Pillar Scores

| Pillar | Score | Key Finding |
|--------|-------|-------------|
| 1. Copywriting | 3/4 | Title and options come from the schema, but the pending reason reads "Hex needs Hex bore A/F above 0", and the blank state has no words. |
| 2. Visuals | 2/4 | The pending signal is a muted dashed select, the same tone as "disabled". The explanation appears on a different row, and for Hex that row is far from the select. |
| 3. Color | 3/4 | Only existing custom properties are used and nothing is hardcoded. Pending reuses the dimmed tone, so it cannot be told from an inactive field. |
| 4. Typography | 4/4 | No new size, weight or family. The selector shares the `.field` rules. |
| 5. Spacing | 3/4 | The shared grid keeps the row aligned. The selector gets no `small` help line. A pending reason row can push the layout down, and it sits on another field. |
| 6. Experience Design | 2/4 | Arrow-key use of a closed select moves focus away mid-gesture. A blank select explains nothing. A pick over a keyed bore turns the form red by design. |

**Overall: 17/24.** The score is not rounded up.

---

## Top Fixes

1. **BLOCKER (keyboard): `pick` runs on every `input` event, and a pending pick calls `input.focus()` on another field.** In Chromium, ArrowDown on a closed `<select>` changes the value and fires `input` for each press. A keyboard user on Round presses ArrowDown to D-flat, which writes `bore_flat`. They press ArrowDown again to Hex. That pick is pending, so focus jumps to `bore_hex` and the user cannot reach No bore by arrow keys. Each intermediate stop also writes fields and sends a request (Round writes `bore_flat=0`, D-flat then restores it). Fix: either act on `change` (fires on commit, not on each arrow, for an open list), or do not move focus when the event came from a key press, or keep focus on the select and move the need into the select's own reason row. This was not run in a browser, so confirm in Chromium and Firefox. Firefox does not behave the same way.
2. **WARNING: the pending state does not read as "you must type a number".** `.selector.pending` only sets `--muted` on the name and select and a dashed border (`style.css:131-132`). That is exactly the `.inactive` look, which elsewhere means "this has no effect". The message "Hex needs Hex bore A/F above 0" is written to the `bore_hex` field's reason row (`pend`, `app.js` near 392), and that field is the last in the Bore group, after the keyway pair. The select that was just clicked shows no text. Fix: also write the need into the selector's own `.reason` (it already exists and has `aria-describedby` wiring), and give `.pending` a cue that is not the dim tone, for example the `--accent` border used by `.field.invalid`'s sibling rule.
3. **WARNING: the redundant wording "Hex needs Hex bore A/F above 0".** `pend` builds `${chosen.label} needs ${need(condition)}`, and `need()` prepends the field title. For Hex and D-flat the label and the title say the same thing twice. For D-flat the sentence is "D-flat needs Flat width above 0", which is fine, but Hex is not. Fix: drop the label (`Needs Hex bore A/F above 0`, which matches the existing L41 reason wording "Needs ... = 0") so the pending and the dim reasons use one voice.
4. **WARNING: the blank select has no explanation.** Negative values (13 of 27 cells in the {-1, 0, 6} grid per `deriveSelectors`' comment) and two-holding options give `selectedIndex = -1`. A blank closed select looks like a loading bug. Only the unreadable-option catch path writes a reason. Add a short reason, or a hidden placeholder option, for the negative case, so a blank select says "Bore values do not match one shape".
5. **WARNING: Hex over a keyed bore shows a red form.** D-10 accepted this. The selector writes nothing to the keyway, and the server's 422 marks `keyway_width` and `keyway_depth` invalid. A user who picked Hex gets red fields far from the select, and no link from the select to the cause. Consider a note in the selector's reason row when the pick leaves a keyway set. This is deferred, not new. It is recorded here because the audit is of what the user sees.
6. **Minor: no help text.** Every `.field` has a `small` help line shown on `:focus-within`. The selector has none, so "No bore" gives no sense of what it does to the keyway and the part. A one-line `help` in the metadata would use the existing styling.
7. **Minor: `<label>` wraps the reason span.** `wrap` is a `label.selector` that contains the `.reason`. When the reason has text, the select's computed name can include it, depending on the engine. The span is `aria-hidden`, which excludes it from a name computed from content in most engines, so this is unconfirmed. A `div` with a `for`-bound `label` avoids the question.

---

## Detailed Findings

### Pillar 1: Copywriting (3/4)

Positive evidence:
- Title "Bore shape", the four labels (Round, D-flat, Hex, No bore) and the group come from `/api/schema`. `app.js` names no bore word, which keeps the project's one-source rule (L02).
- "No bore" is used for the zero state, so the select never claims a shape for a 0 bore (BS-1).

Deductions:
- Pending text duplicates the label and the field title ("Hex needs Hex bore A/F above 0"). It also uses a different voice from the L41 inactive reason ("Needs Hex bore A/F = 0").
- The blank state (negative or ambiguous values) has no copy. The comment cites 13 of 27 grid cells that blank the select.
- The unreadable-option message "Cannot tell which option holds: <err.message>" prints a JS error message to the user. It is only reachable with a broken schema, so it is minor.

### Pillar 2: Visuals (2/4)

- The pending state is the select in `--muted` with a dashed border. The dim tone is the project's existing signal for an inert field (`.field.inactive`), so a pending select looks switched off, when it is waiting for input. This is the weakest part of the phase.
- The cause is shown on a different row. For Hex, `bore_hex` follows `bore_d`, `bore_flat` and the keyway pair, so the explanation can sit several rows below the control that the user just changed. Focus moves there, so the page scrolls on a short viewport, and the select is left behind.
- The selector row aligns with the field rows through the shared grid (`1fr 8.5rem`), and it sits first in the Bore group, before `Bore Ø`. That placement is correct.
- No unit column for the select, so its control stays in the same grid track as the numeric inputs. Fine.
- Screenshots were not captured, so none of this was seen.

### Pillar 3: Color (3/4)

- No hardcoded colors. `.selector.pending` uses `--muted` only, which both themes define (light `#677080`, dark `#97a0ab`).
- The `--muted` text on the page background was not measured here. It is the same token used by `.unit`, `small` and `.hint`, so any contrast defect is pre-existing and not attributable to this phase.
- Accent count is unchanged. The deduction is for semantic reuse: pending and inactive share one tone, so color cannot tell them apart.

### Pillar 4: Typography (4/4)

- The selector inherits `font: inherit` through the shared `.field select` rule group. The `.name` weight (500) and the `.reason` size (`.78rem`) match the field rows. No new size or weight was added. Nothing to deduct.

### Pillar 5: Spacing (3/4)

- Selector and field share `margin: .5rem 0` and the gap (`.1rem .5rem`), so the row rhythm holds.
- The `.reason` row is `display: none` when empty, so the layout is steady at rest. A pending reason appears on another field's row and moves everything below it by one line. Because `pend` does not reset the earlier note until the next pending pick or derive, two adjacent notes are not possible, so no stacking defect was found.
- No arbitrary values were added.

### Pillar 6: Experience Design (2/4)

Positive evidence:
- Derive never writes, and it runs at the three `applyRelations()` sites. A shared link loads exactly as before (L05).
- A pick plans first and writes after, so a pending pick writes nothing (second standing rule). The stash restores only the user's own string and never invents an A/F (first standing rule).
- `deriveSelectors` is caught per selector, so a bad option blanks one select without stopping `update()`.
- The pending target gets `aria-describedby` pointing at its reason row, so a screen reader hears the need on focus.

Deductions:
- Fix 1: `input` on a closed select fires per arrow press, and a pending pick steals focus. This breaks keyboard completion of the task "reach No bore from Round". Mouse users are not affected.
- Fix 4: blank select without words.
- Fix 5: a red form after Hex over a keyed bore, by design.
- `stopPropagation()` in `pend` keeps the form's `input` listener from running. A consequence is that `applyRelations()` and `deriveSelectors()` do not run for that event, so any other stale `.pending` state relies on the next event to clear. It is by design (D-09) and was measured, but it is one more special path to keep in sync.
- Loading, error and empty states for the select itself are not needed. The select is built from the schema in `buildForm()`, which already handles the schema fetch.

---

## Registry Safety

Not applicable: no `components.json` and no shadcn use.

---

## Files Audited
- `src/spur/static/app.js` (diff of `470b78a`: `buildSelectors`, `deriveSelectors`, `pick`, `pend`, the three derive sites; `need()` and the relation code around it)
- `src/spur/static/style.css` (shared `.field, .selector` rules, `.selector.pending`, custom properties)
- `.planning/phases/24-bore-shape-selector/24-CONTEXT.md` (D-01 to D-19)
- `.planning/phases/21-browser-test-of-the-viewer/21-UI-REVIEW.md` (format only)
- Not read in full: the four SUMMARY and PLAN files, the test files, `index.html`. The review is based on the feature diff and the context file.
