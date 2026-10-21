---
phase: 28-refuse-the-bad-link
reviewed: 2026-10-21T00:00:00Z
depth: standard
files_reviewed: 18
files_reviewed_list:
  - Makefile
  - bench/RESULTS.md
  - docs/architecture/decision_log.md
  - docs/architecture/web-ui.md
  - docs/ideas/2026-10-21-stash-entry-survives-a-hand-edit.md
  - docs/ideas/INDEX.md
  - docs/tech_debt/INDEX.md
  - docs/tech_debt/active/2026-10-10-make-verify-hung-at-98-percent-with-no-failure.md
  - docs/tech_debt/active/2026-10-15-wait-until-parked-spins-without-a-pause.md
  - docs/tech_debt/active/2026-10-21-phase-18-review-info-findings-deferred.md
  - docs/tech_debt/active/2026-10-21-tip-chamfer-effective-gate-reads-the-request.md
  - docs/tech_debt/resolved/2026-10-09-phase-19-review-info-findings-deferred.md
  - docs/tech_debt/resolved/2026-10-10-root-shape-bogus-loads-a-blank-select.md
  - src/spur/calc.py
  - src/spur/static/app.js
  - tests/test_api.py
  - tests/test_browser.py
  - tests/test_browser_pins.py
findings:
  critical: 0
  warning: 3
  info: 2
  total: 5
status: issues_found
---

# Phase 28: Code Review Report

**Reviewed:** 2026-10-21
**Depth:** standard
**Files Reviewed:** 18
**Status:** issues_found

## Summary

Reviewed the diff `1434a47..HEAD` for the listed files. The core mechanism (the `rejected` map, `refuse()`, the `gearQuery()` early branch, `update()` mate fallback, the `DIMS` label function) is small and mostly correct. I traced the `DIMS` label rule against `derive()` (`root_form_d` is non-null exactly when `rm.curve` exists, and `rfil` is `rm.cutter.rho` in that case), so the "Hob tip radius used" label does follow the built root. The `calc.py` docstring edit matches `cutter()`'s guard (line 1415) and `root_mode`'s early return for "nothing requested". Cited commits (`61154d1`, `cb93d4e`, `0efc87c`), the archived log path, the `Makefile:185` line and the bench line citations resolve. The `test_api.py` pins and the new browser steps are consistent with the code; I found no race in the new steps (consecutive bad links in `BAD_LINKS` never share a message text, and `problems()` adds the `invalid` marks before `fail()` shows the message).

The defects are one reproducible UI/server divergence that L44 knowingly accepted, one display mismatch on accepted tokens, and one known printed-number gap that is filed but not scheduled.

## Warnings

### WR-01: A selector pick that writes a rejected field leaves the page sending the old token

**File:** `src/spur/static/app.js:133-139` (gearQuery), `src/spur/static/app.js:399-404` (write), `src/spur/static/app.js:633` (the only clearing listener)
**Issue:** `rejected` is cleared only by an `input` event whose `target.name` is the field. A bore-shape pick fires `input` on a select with no `name`, and `write()` assigns `input.value` programmatically, so the entry survives. Reproduction by reading the code: open `#bore_d=abc`, so the Bore Ø box is blank and `rejected` holds `bore_d=abc`. Pick "No bore": `plan()` finds `bore_d eq 0` not holding (blank reads as the default 9) and writes `"0"`. The box now shows 0 and the select shows "No bore", but `gearQuery()` still sends `bore_d=abc`. The 422 persists, naming Bore Ø, beside a box that visibly holds a valid 0. The same happens for "Hex" over `#bore_hex=abc` with a stashed `6`. L44 records that the guard "was not adopted", but the result is a screen that contradicts the request being sent, the opposite of what the L08 and L05 standing rules ask for, and no browser step covers it. The fix is one line and the mechanism already has the field name at hand.
**Fix:**
```js
function write(writes) {
  for (const [field, to, zeroed] of writes) {
    const { input } = fields.get(field);
    if (zeroed) stash.set(field, input.value);
    input.value = to;
    rejected.delete(field); // the box now holds what the user picked; send that
  }
}
```
Update the `test_api.py` token list (the pin on the single field-writing statement) and add a `bad link cleared` case that picks a bore shape over `bore_d=abc`. Amend the "When it clears" paragraph of L44.

### WR-02: A token the box blanks but the API accepts builds a non-default part under a blank box

**File:** `src/spur/static/app.js:116-118` (refuse), `tests/test_browser.py` (`ACCEPTED_LINK = "face_width=5."`, step `blank, unknown and accepted tokens`)
**Issue:** The page's own convention (D-06) is that a blank control means the default. For ` 22`, `22 `, `1_0` (both `teeth` and `face_width`) and `22.`, `5.`, `+5` (`face_width`), `bench/RESULTS.md` shows the box reads `''` and the API answers 200. The part is now built from the token while the box shows blank, so the visible form says "default" and the part is not the default. Before this phase the page built the default part, which at least matched the blank box. The dimensions table is honest, but a user reading the form cannot tell which field carries the hidden value, and Reset is the only visible cue. L44 documents this and pins it, so it is a known trade-off, but it is a standing L05 tension that has no user-visible signal.
**Fix:** When a rejected token builds successfully, tell the user. For example, in `renderInfo`'s caller, if `rejected.size > 0` and the info response was OK, call `showMessages([], [...rejected].map(([n, t]) => `${fields.get(n)?.title ?? 'Mate teeth'} was opened as "${t}" and is built as the server reads it`))`. Alternatively, have `refuse()` set the control's `placeholder`/`title` to the token. Add a step assertion for `face_width=5.`.

### WR-03: A printed value the project's own rule forbids is filed `must` with no trigger other than a decision

**File:** `docs/tech_debt/active/2026-10-21-tip-chamfer-effective-gate-reads-the-request.md:1`, `src/spur/calc.py:1294`
**Issue:** `tip_chamfer_effective=r3(tch) if p.tip_chamfer > 0 else None` prints `0.0` for a chamfer that was asked for and not cut (`tip_chamfer=0.0004`), while no chamfer prints `null`. CLAUDE.md states "If a value cannot be computed honestly, report a warning and no number" (L08). The item's own text admits `0.0` "can be read as a chamfer of zero was cut". It is tagged `must`, and its INDEX trigger is "the human's decision", which is not an event that will fire: nothing is scheduled to ask the question. I confirmed line 1294 reads `p.tip_chamfer`, not `tch`.
**Fix:** Either decide now and fix with `tip_chamfer_effective=r3(tch) if tch > 0 else None` (no pinned record names `tip_chamfer`, per the item; run `make fixture.regen --check` to prove it), logging the decision as an Lxx, or change the INDEX trigger to a concrete event (next edit of `derive()` or the `tip_chamfer` field) and surface the question to the human in the phase close-out.

## Info

### IN-01: `readHash()` assigns the mate box twice only to keep an old test pin adjacent

**File:** `src/spur/static/app.js:126-128`
**Issue:** `mateInput.value = h.get('mate_teeth') ?? ''` runs, then `refuse(...)`, then the identical assignment again. `refuse()` does not change the value, so the second line is dead. The comment's reason ("a read-back after it would sit outside readHash()") only makes sense as a way to keep the string `mateInput.value = ...; applyRelations(); deriveSelectors(); }` contiguous for `tests/test_api.py:263`. Code written to satisfy a text pin invites someone to delete the "redundant" line and break the gate, or to copy the pattern.
**Fix:** Delete the first assignment and keep the one before `applyRelations()`, doing the `refuse(...)` read-back after it and before `applyRelations()`; the pin string does not need the two lines adjacent if the read-back sits before the final assignment. Alternatively, loosen the pin to match the statement by itself.

### IN-02: `web-ui.md` has a 190-character line inserted mid-paragraph

**File:** `docs/architecture/web-ui.md:34`
**Issue:** The inserted parenthetical lengthens one line of an otherwise hand-wrapped paragraph to roughly 190 characters, unlike its neighbours (about 95). Cosmetic, but the file's other lines wrap consistently.
**Fix:** Re-wrap the paragraph at the file's existing width.

---

_Reviewed: 2026-10-21_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
