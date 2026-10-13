---
phase: 24-bore-shape-selector
reviewed: 2026-10-13T09:00:00Z
depth: standard
files_reviewed: 5
files_reviewed_list:
  - docs/architecture/decision_log.md
  - docs/architecture/web-ui.md
  - src/spur/static/app.js
  - tests/browser_session.py
  - tests/test_browser.py
findings:
  critical: 0
  warning: 1
  info: 6
  total: 7
status: issues_found
---

# Phase 24: Code Review Report

**Reviewed:** 2026-10-13
**Depth:** standard (incremental: `git diff 0c2d639..HEAD` of the five files, with the whole of the selectors section, `buildForm()`, `applyRelations()`, the update loop and the wiring block read for grounding)
**Files Reviewed:** 5
**Status:** issues_found

## Summary

This round covers the two fix commits `faed50a` and `9da4851`. The earlier review (`0c2d639`, 16 files) is superseded by this file. Its findings IN-01..IN-04 name `src/spur/params.py`, `tests/test_api.py` and a tech-debt file that did not change since, so I did not re-read those. I carry the four forward with their ids and updated line numbers where the line is in `app.js`.

What I ran:

- `pytest tests/test_api.py tests/test_selector.py -n0 --no-cov -q` gave 78 passed. The token pins and the one-value-write pin hold.
- `pytest tests/test_browser.py -n0 --no-cov -q` gave 2 passed in 25.54 s.
- `ruff check src tests` was clean.
- `mypy --strict tests/browser_session.py tests/test_browser.py` reported no issues.
- Two Playwright probes against a local server, for WR-02 below.
- I did not run `make verify` or `make check`.

**WR-01 (focus stolen by a pending pick): confirmed fixed.** There is no `.focus()` call left in `app.js`. `pend()` now only stops the event, records `pending` and calls `showPending()`. The select keeps the focus and is described by the field's reason row. The browser step asserts both after every pending pick (`SELECT_FOCUSED`, `SELECT_DESCRIBED_BY`). One limit stands, and the decision log states it: no test drives an engine that commits an option per arrow key, so the walk itself is unproven by the suite. I traced a keyboard walk through `pick()` by hand: each step calls `endPending(s, true)` and then plans again, so the row of the previous pending step is put back and nothing is written.

The new pending machinery is otherwise sound where I traced it:

- **One pending pick at a time.** Any `input` on the form first ends a pending pick on another target. A pick on a second select ends the first's pending pick in the capture listener, so at most one pick is pending.
- **The `keep` flag.** It is set only in the capture listener and consumed by the derive on the same event. If the event does not reach the form's bubble listener it would stay set. The only event that stops propagation is the select's own pending pick, and `completePending()` skips a selector's own select, so it cannot strand a flag.
- **Stale row text.** `was` is read in `showPending()` after `applyRelations()` has rewritten every row, so `endPending(s, true)` never restores stale text.
- **One value write.** `write()` is the only place a field value is set in the section, so the pin holds. Both `plan()` and `write()` run on the same state: `plan()` completes in the capture phase, before the derive.

One new warning, six info items (four carried forward).

## Warnings

### WR-02: A blank or unreadable number box completes a pending pick with the field's default, and writes the zeros, although no number was typed

**File:** `src/spur/static/app.js:473-486` (`completePending()`, the `plan(chosen)` call) with `src/spur/static/app.js:126-129` (`effective()`)
**Issue:** `completePending()` re-runs `plan()` on the field the pick asked for, and `plan()` reads that field through `holds()`, which reads `effective()`. `effective()` turns an empty box into the field's default. So an empty box counts as a typed number whenever the default clears the threshold. `bore_d` has default 9 and `bore_flat` has default 8, so for Round and D-flat the empty box satisfies "above 0".

An empty box is easy to reach without typing a number:

- Select the pending box and press Backspace or Delete before retyping.
- Type `.` or `-` first. A `type=number` box reports `''` while its text is not yet a number, so `.5` and `-5` both pass through `''`.

The decision log amendment and `web-ui.md` both say the pick "stays until the number it asked for is typed". An empty box is not that.

I reproduced both paths against a local server in headless Chrome 153. From `#bore_d=0`:

- Pick D-flat (pending on `bore_d`), then `fill("")` on `bore_d`. Result: the select shows D-flat, `.pending` is gone, `bore_d` is `''`.
- Pick Round (pending on `bore_d`), triple-click the box, press `.`. Result: Round shown, pending gone, `bore_d=''`, and `bore_flat` rewritten from `8` to `0` with `8` stashed. After the 350 ms debounce the hash read `#bore_flat=0`, and the page had requested a Round 9 mm bore.

The 9 is the page default and the user never typed it, and a keystroke that was not a number has already zeroed `bore_flat`. Under L05 (a parameter the user did not set must not silently change the part) and L08 (a number someone will cut metal to), a pick the user was still making should not complete and send. The user's next keystroke repairs the box, so the stuck state is short, but a pause of 350 ms sends the request. For `-5` the completion has already happened when the box becomes `-5`, so the pick ended on a number that is below the threshold and the select goes blank.

The suite cannot see it. `_complete_pending()` always types `number_above()`, and no case types `''`.

**Fix:** Treat an unreadable or empty box as "not yet typed" in `completePending()` and keep the pick pending on the same condition:

```js
const { input } = fields.get(condition.field);
if (event.target !== input) { endPending(s, true); deriveSelector(s); continue; }
const next = input.value === '' ? { condition } : plan(chosen);
endPending(s, false);
if (next.condition) s.pending = { chosen, condition: next.condition, keep: true, was: null };
else write(next.writes);
```

The pick is then still pending when the user finishes the number. Add a case to the `bore shape` step: after a pending pick, `fill('')` on the named field and assert the select is still `.pending`, no field other than the typed one moved and no request carries a zero the pick would write; then type a number and assert the completion as today.

## Info

### IN-01: The stash can restore a number older than what the user last typed, and the comment calls it "the user's own string" while it also holds page defaults

**File:** `src/spur/static/app.js:292-300` (the `stash` comment) and `src/spur/static/app.js:401` (`stash.set` in `write()`)
**Issue:** Unchanged by the fix commits, and now reached from two paths: a pick and the completion of a pending pick. A zeroing write records the box string at that moment. Nothing updates it when the user then edits the same field by hand, and hash navigation keeps it (D-19). Two orders:

1. On the default part, pick Round (stash `bore_flat` = `'8'`, the page default, not something typed). Type `bore_flat` = 5, then 0 by hand. Pick D-flat. The box returns to `8`, not the 5 the user last chose.
2. Open a link with `bore_flat=3`, pick Round (stash `'3'`), then follow another link with `bore_flat=0`. Pick D-flat. The box shows `3`, a value from a different gear.

Both are visible in the box and sent, and D-19 accepts the second knowingly. But the comment ("puts the user's own string back and never invents one", "a flat the user did not type would be a number the tool printed and nobody chose") overstates it: case 1 restores a default and case 2 restores a value typed for another part.
**Fix:** Delete the stash entry for a field when its box is edited by hand (in `completePending()` or the form listener: `if (event.target.name) stash.delete(event.target.name)`; the selects have no `name` for selectors), or reword the comment to say the stash can hold a page default and a value from an earlier link.

### IN-02: A selector that names a group no field has fails with a message about the schema fetch and leaves a built but empty form

**File:** `src/spur/static/app.js:316` (the `throw` in `buildSelectors`) and `src/spur/static/app.js:633-638` (the bootstrap `catch`)
**Issue:** Unchanged. `buildSelectors()` throws after the fields are in the DOM. The bootstrap `catch` prints `Could not load the parameter schema: ...` and returns before `readHash()` and `update()`. The schema loaded fine, so the prefix is wrong, and the form stays blank with no part and no download links. The disposition records this as CX-03 as well.
**Fix:** Reword the bootstrap message to `Could not build the form: ...`, or run `readHash()` and `update()` anyway and show the selector error in `#messages`.

### IN-03: The OpenAPI pin is a substring test on the whole document

**File:** `tests/test_api.py:143`
**Issue:** Carried forward, not re-read this round. `assert "selectors" not in client.get("/openapi.json").text` fails if any description contains the word in prose, and it is coupled to the wording of `help=` strings.
**Fix:** Parse the JSON and walk it for a dict key named `selectors`.

### IN-04: Every selector-made Hex part prints a warning in snake_case field names the form does not show (already filed)

**File:** `docs/tech_debt/active/2026-10-11-hex-bore-warns-about-default-bore-fields.md` (and `src/spur/calc.py`)
**Issue:** Carried forward. Picking Hex leaves `bore_d` and `bore_flat` at their defaults (D-11), so the warning names `bore_d (9 mm)` and `bore_flat (8 mm)`, which the form labels `Bore Ø` and `D-flat`. The debt file records it; I add only that the field-name wording is separate from the default-values wording and should be in the fix's scope.
**Fix:** When `calc` is changed, name fields by their form titles or drop the sentence unless the request set them.

### IN-05: L42 still says a pending pick "focuses the field that needs a number" and ends at the next derive; the correction is an appended paragraph

**File:** `docs/architecture/decision_log.md:2736` and `docs/architecture/decision_log.md:2805-2824`
**Issue:** The amendment says "Two sentences above are superseded" and gives the new rule, but it leaves the superseded sentences in the entry body (line 2736 still reads "focuses the field that needs a number"). A reader of L42 from the top meets the old behaviour as the decision and finds the correction 70 lines later. The amendment names neither sentence by quoting it. The log already uses the "superseded" idiom for whole decisions, so this is a style choice and not an error, but the next reader of the log has to find the amendment. The amendment's last sentence ("the `bore shape` step read 12.26 s once ... against 24-04's 8.55 s mean") also compares a single reading with a mean of three; AGENTS.md asks for measured numbers, and one reading under a different load average does not support a "more picks" explanation. The amendment says "once", so it is honest, but it does not bound the claim.
**Fix:** Edit the line-2736 sentence to point at the amendment, for example "(focus: see Amended 2026-10-13)", or quote the two superseded sentences in the amendment. For the timing, record three runs the way 24-04 did, or drop the comparison and leave only "Phase 25 re-sets the bar".

### IN-06: A garbled comment in the `twin selectors` step

**File:** `tests/test_browser.py:1488-1489`
**Issue:** "The twins_page is the first two labels that are pending from one state link on different fields, read from the schema." The variable is a page; the sentence describes `pendings[0]`. A reader looking for what `twins_page` is gets a wrong answer.
**Fix:** "`pendings[0]` is the first state link with two labels that are pending on different fields, read from the schema; `twins_page` is the page served with the selector list doubled."

---

_Reviewed: 2026-10-13T09:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
