---
phase: 24-bore-shape-selector
reviewed: 2026-10-12T17:00:00Z
depth: standard
files_reviewed: 16
files_reviewed_list:
  - README.md
  - bench/RESULTS.md
  - docs/architecture/decision_log.md
  - docs/architecture/http-api.md
  - docs/architecture/web-ui.md
  - docs/ideas/INDEX.md
  - docs/ideas/retired/2026-09-27-bore-shape-selector-in-the-web-form.md
  - docs/tech_debt/INDEX.md
  - docs/tech_debt/active/2026-10-11-hex-bore-warns-about-default-bore-fields.md
  - src/spur/params.py
  - src/spur/static/app.js
  - src/spur/static/style.css
  - tests/browser_session.py
  - tests/test_api.py
  - tests/test_browser.py
  - tests/test_selector.py
findings:
  critical: 0
  warning: 1
  info: 4
  total: 5
status: issues_found
---

# Phase 24: Code Review Report

**Reviewed:** 2026-10-12
**Depth:** standard (the phase diff `d8c5de8..HEAD`, read file by file, with the cross-references the selector needs)
**Files Reviewed:** 16
**Status:** issues_found

## Summary

I read the phase diff of `params.py`, `app.js` and `style.css` in full, the whole of `buildForm()`, `holds()`, `applyRelations()`, the update loop and the wiring block of `app.js` for context, the diffs of the four test files and the docs, and the first 200 lines of `tests/test_selector.py`. I did not read the remaining body of `tests/test_selector.py` or every line of the 575-line `tests/test_browser.py` diff.

What I ran:

- `pytest tests/test_selector.py tests/test_api.py -n0 --no-cov -q` gave 78 passed.
- `ruff check src tests` was clean.
- `mypy --strict src tests/test_selector.py tests/browser_session.py` reported no issues in 12 files.
- I did not run `make verify` or `tests/test_browser.py`.

What I checked and found sound:

- **The schema carriage.** `GearParams.model_json_schema()` returns a deep copy, so the module-level `_BORE_SHAPE` cannot be mutated through `/api/schema`. I changed the title in the returned schema and `_BORE_SHAPE` kept `Bore shape`.
- **The option grid.** The four options hold exactly one at a time over every non-negative triple. No bore deliberately leaves `bore_flat` free, so `bore_d=0` with the default flat of 8 is a legal part with no warning (checked with `calc.derive`).
- **The pick.** It plans before it writes. An unknown op throws inside the planning loop, before any write. `pend()` writes nothing and stashes nothing.
- **Text only.** Titles, labels and error messages reach the DOM through `textContent` or `new Option(label)`, so there is no injection path from the schema.
- **Not a field.** The select has no `name` and no `fields` entry, so `gearQuery()` cannot send it and `update()` cannot put it in the hash. The `fields.set(` count pin in `test_api.py` guards this.

One keyboard concern from the UI review is confirmed on the wiring and reproduced in a simulation (WR-01). No critical finding.

## Warnings

### WR-01: A pending pick steals focus on every arrow-key step, so a keyboard user cannot walk the select, and the next arrow press edits a number nobody chose (confirms the unverified UI-review concern, with a platform caveat)

**File:** `src/spur/static/app.js:329` (the `input` listener in `buildSelectors`) and `src/spur/static/app.js:411` (`input.focus()` in `pend()`)
**Issue:** The select listens on `input` only, and `pend()` calls `input.focus()` synchronously. In Firefox on every platform, and in Chrome on Windows and Linux, the arrow keys on a closed select commit the next option and fire `input` and `change` per step. So the first arrow step toward any pending option runs `pick()`, then `pend()`, which moves focus to the number box. The user's next arrow key goes to a `type=number` input, where Up and Down spin the value.

The default part makes this the common case. Walking down from the default D-flat, the very first step, to Hex, is always pending: `bore_hex` has no stash entry until a pick has zeroed it, so a Hex pick from a part that never had a hex bore needs a typed number. Focus jumps to the Hex box on that first step, and the user can never arrow on to No bore from the select. Steps that write (Round from D-flat, and D-flat back from Round while the stash holds the flat) do not move focus, so the trap is specific to the pending options.

I reproduced the mechanism with Playwright against a local server. I dispatched a single `input` event on the select after setting `selectedIndex = 2` (Hex), which is what one arrow step does on the affected platforms. I then pressed ArrowUp:

- `document.activeElement` became `bore_hex` straight after the first step.
- ArrowUp on that box turned `bore_hex` into `0.05`, which is its `step`.
- After the debounce the hash read `#bore_hex=0.05` and a request for a 0.05 mm hex bore had been sent.

That is a number the tool built that the user never typed. It is also a change to the part that came from an arrow key meant to navigate a select. The user did press the key, so this is a keyboard-operability defect first and a standing-rule risk second.

What I could not confirm: arrow keys on a closed select in headless Chrome 153 on macOS did nothing at all (no value change, no `input`). They opened the popup instead, which is the usual macOS behaviour. So the problem does not reproduce on macOS Chrome. I could not run Firefox or Chrome on Windows or Linux here, and I did not reproduce real arrow-key navigation, only the equivalent `input` dispatch.

The test suite cannot see this. `_pick()` in `tests/test_browser.py` uses `select_option`, which sets the value and fires `input` once. No test presses a key on the select.

**Fix:** Do not move focus when the pick came from the keyboard. The select already has the reason row on the target field and the `.pending` mark, so the note is not lost. One small way:

```js
let byKey = false;
select.addEventListener('keydown', () => { byKey = true; });
select.addEventListener('input', (event) => { pick(s, event, byKey); byKey = false; });
// in pend(s, chosen, condition, event, byKey): input.focus() only when !byKey
```

The alternative is to move focus on `change` after the select closes (`blur` or `Enter`), not on `input`. Add a browser step that presses ArrowDown twice on the focused select and asserts `document.activeElement` is still the select and no box changed. That test needs a Firefox or non-macOS-Chrome engine to be meaningful, so say in the step which engine it was seen red on.

## Info

### IN-01: The stash can restore a number older than what the user last typed, and the comment calls it "the user's own string" while it also holds page defaults

**File:** `src/spur/static/app.js:292-300` (the `stash` comment) and `src/spur/static/app.js:382` (the restore in `pick()`)
**Issue:** A zeroing pick records the box string at that moment. Nothing updates it when the user then edits the same field by hand, and hash navigation keeps it (D-19). Two concrete orders:

1. On the default part, pick Round (stash `bore_flat` = `'8'`, the page default, not something typed). Type `bore_flat` = 5, then type 0 by hand. Pick D-flat. The box returns to `8`, not the 5 the user last chose.
2. Open a link with `bore_flat=3`, pick Round (stash `'3'`), then follow another link that has `bore_flat=0`. Pick D-flat. The box shows `3`, a value from a different gear.

Both are visible in the box and sent, and D-19 accepts the second knowingly. But the comment "puts the user's own string back and never invents one" and "a flat the user did not type would be a number the tool printed and nobody chose" overstates it, since case 1 restores the default and case 2 restores a value typed for another part. Under L08 and L05 a number from another part is the kind of plausible value the project says to avoid.
**Fix:** Either delete the stash entry for a field when its box is edited by hand (in the form `input` listener, `if (event.target.name) stash.delete(event.target.name)`, which leaves picks alone because the select has no `name`), or say in the comment that the stash can hold a page default and a value from an earlier link. The first costs one line and a test that case 1 now ends pending.

### IN-02: A selector that names a group no field has fails with a message about the schema fetch and leaves a built but empty form

**File:** `src/spur/static/app.js:313` (the `throw` in `buildSelectors`) and `src/spur/static/app.js:558-562` (the bootstrap `catch`)
**Issue:** `buildSelectors()` throws after the fields are already in the DOM. The bootstrap `catch` then prints `Could not load the parameter schema: Selector "X" names the group "Y"...`, and returns before `readHash()` and `update()`. The schema loaded fine, so the prefix is wrong. The boxes sit blank (no defaults written), with no part, no dimensions and no download links. The failure is loud, which is better than silent, but it is not the state a user can recover from, and a model-side typo in a group name would only be caught by `test_selector.py` walking the list, not by the page.
**Fix:** Reword the bootstrap message to `Could not build the form: ...`. If a half-built form is not wanted, build the selectors before appending any fieldset, or run `readHash()` and `update()` anyway and show the selector error in `#messages`.

### IN-03: The OpenAPI pin is a substring test on the whole document

**File:** `tests/test_api.py:142`
**Issue:** `assert "selectors" not in client.get("/openapi.json").text` fails if any route description, field help string or future docstring contains the word "selectors" in prose. The test is meant to prove the key did not reach a schema, not that the word is absent. It is also coupled to the wording of `help=` strings in `params.py`, since those reach `parameters` descriptions.
**Fix:** Parse the JSON and walk it for a dict key named `selectors`, for example `assert not _has_key(client.get("/openapi.json").json(), "selectors")`, with a small recursive helper.

### IN-04: Every selector-made Hex part prints a warning in snake_case field names the form does not show (already filed)

**File:** `docs/tech_debt/active/2026-10-11-hex-bore-warns-about-default-bore-fields.md` (and `src/spur/calc.py`, which owns the sentence)
**Issue:** The phase's own decision (D-11) leaves `bore_d` and `bore_flat` at their defaults when Hex is picked, so the headline path of the new feature always renders `Hex bore replaces the round profile: bore_d (9 mm) and bore_flat (8 mm) are ignored.` The form labels these boxes `Bore Ø` and `D-flat`, so the message names fields the user cannot find, about values they did not set. The debt file already records this, the trigger is marked fired, and the INDEX row says fix before Phase 25. I add only that the wording problem (field names, not titles) is separate from the "default values" problem and should be in the fix's scope. No new debt item is needed.
**Fix:** When the `calc` change is made, name the fields by their form titles or drop the sentence unless the request set them, as the debt file proposes.

---

_Reviewed: 2026-10-12T17:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
