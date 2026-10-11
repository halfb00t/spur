---
phase: 23-conditional-form-fields
reviewed: 2026-10-11T18:00:00Z
depth: standard
files_reviewed: 20
files_reviewed_list:
  - bench/RESULTS.md
  - docs/architecture/decision_log.md
  - docs/architecture/http-api.md
  - docs/architecture/web-ui.md
  - docs/ideas/2026-10-11-the-two-relations-calc-does-not-back.md
  - docs/ideas/INDEX.md
  - docs/ideas/retired/2026-09-29-conditional-form-fields.md
  - docs/tech_debt/active/2026-10-06-resource-tracker-flake-fails-the-gate.md
  - docs/tech_debt/active/2026-10-11-hex-bore-warns-about-default-bore-fields.md
  - docs/tech_debt/INDEX.md
  - README.md
  - src/spur/params.py
  - src/spur/static/app.js
  - src/spur/static/style.css
  - tests/browser_session.py
  - tests/capture_requests.py
  - tests/test_api.py
  - tests/test_browser.py
  - tests/test_cli.py
  - tests/test_relations.py
findings:
  critical: 0
  warning: 0
  info: 10
  total: 10
status: issues_found
---

# Phase 23: Code Review Report

**Reviewed:** 2026-10-11
**Depth:** standard (incremental re-review since `fc5229b`)
**Files Reviewed:** 20
**Status:** issues_found

## Summary

This pass re-reviews the three fix commits `cea8c54` (WR-01), `59deb6e` (WR-02) and `ef5d4a7` (WR-03) against the diff `fc5229b..HEAD`. The scope handed over was the four source and test files. The doc and support files stay in `files_reviewed_list` for continuity, because IN-03..IN-05 cite them. No file outside the four changed in the range except the review ledger.

**WR-01, WR-02 and WR-03 are resolved and dropped from this report.** The ledger keeps their `fixed` rows.

- **WR-01.** `applyRelations()` now wraps each field in `try/catch`. A throw leaves that field undimmed (`classList.remove('inactive')`), writes a reason row `Cannot tell whether this field is used: …`, and points `aria-describedby` at it. The loop carries on with the other fields, so all four call sites (`readHash`, the input listener, `hashchange`, `#reset`) reach `update()` or `scheduleUpdate()`.
  - The catch also covers a gate that is not a field (`fields.get(name)` is undefined, so `effective()` and `need()` throw a `TypeError`). That is correct: the row carries the engine's message, the field is shown plain, and no plausible dim state is produced from an error (L08 holds).
  - `.reason:empty { display: none }` means a non-empty row is visible without `.inactive`, so the error is on screen. `update()` never writes `.reason`, so the row survives a build.
  - On "removed again when a later evaluation succeeds": the success path sets `reason.textContent = ''` and removes `aria-describedby`, so the row clears if a later evaluation passes. The relations come from `prop.enabled_when`, which `buildForm()` reads once, so a given field's throw is deterministic until a reload. There is no in-page recovery path to test.
  - The new browser step `unknown relation op` covers the load path, the field's row text, the other fields' dim set, and a keystroke that still reaches `/api/info` and `#dl-stl`.
- **WR-02.** The regex now has an alternative for each verb L41 names, an `=(?!=)` anchor, a probe per alternative, and a list of shapes it must leave alone. The `.value` write guard is limited to the section between the `-- relations (L41)` and `-- messages` banners, so the legitimate writes in `readHash()` and `#reset` (both outside that section) cannot trip it. I found no new false positive against them. The banner dependency is documented in the comment, and the assert message `the relations section moved: this guard would read nothing` fails loudly if a banner is renamed.
- **WR-03.** `_assert_relations_name_the_driver_calc_obeys()` holds. All 8 states validate under `GearParams` (the module passes: `pytest tests/test_relations.py tests/test_api.py` gave 116 passed, `ruff check src tests` is clean, `mypy --strict tests/test_relations.py` is clean). I ran a scratch script outside the repo (no repo file changed). The 21 wrong-driver swaps and 21 extra-gate variants go red, and the control test shows the owner alone passes. The docstring's stated residual, a gate that never differs across valid parts (`spoke_count eq 0` beside `hole_count gt 0`), is real and honestly described. I confirmed that this variant passes, along with `hex_cell eq 0` beside `spoke_count gt 0`. One further residual is not stated; see IN-08.

No new warning or critical defect was found. The fixes introduced two documentation and test-strength gaps (IN-08..IN-10). IN-01..IN-07 still hold, with line numbers refreshed where the edits moved them.

No security issues. The new reason text uses `textContent`, and `err.message` comes from `new Error(...)` built from the schema's own op string, not from markup.

## Info

### IN-01: The reason text is formatted differently in the two "independent" evaluators for non-trivial values

**File:** `tests/browser_session.py:353` vs `src/spur/static/app.js:136-141`
**Issue:** JS builds the reason with `${value}` (JS number-to-string). The Python reference uses `{wanted:g}`. They agree for 0, 0.05 and 1, which are all current thresholds. They diverge once a threshold is at least 1e6 (`1e+06` against `1000000`) or below 1e-4 (`1e-05` against `0.00001`). The step's "second implementation agrees on every state" proof would then fail on text, not on logic, the first time Phase 24 declares such a value.
A related latent difference: `expected_inactive` reads the link with `dict(parse_qsl(...))`, so a repeated key is last-wins. `URLSearchParams.get` is first-wins. The fixture links come from the app itself and never repeat a key, so this is not reachable today. (IN-06 below carries the concrete repeated-key case.)
**Fix:** Format with `repr(float)` trimmed of `.0`, or compare numerically through the schema rather than by string. At minimum, add a comment that the values must stay inside the range where `:g` and JS agree.

### IN-02: A dimmed field's accessible name now contains its own reason, which `aria-describedby` repeats

**File:** `src/spur/static/app.js:87-90`, `:159-165`
**Issue:** The `.reason` span sits inside the wrapping `<label>`. Its text becomes part of the input's implicit label, along with the unit and the description, so the accessible name reads "Hub Ø mm Needs Spoke arms above 0 ...". `aria-describedby` then points at the same span, so a screen reader announces the reason twice. The unit and the description already behave this way, so the pattern is not new. WR-01's catch branch (`:163-165`) sets the same `aria-describedby` for the "Cannot tell whether this field is used" row, so the doubling now applies to the error row too.
**Fix:** Give the reason `aria-hidden="true"` and keep `aria-describedby`. Or move the span out of the label.

### IN-03: A stale line reference in the new tech-debt item

**File:** `docs/tech_debt/active/2026-10-11-hex-bore-warns-about-default-bore-fields.md:10`
**Issue:** The file cites `tests/test_browser.py:425` for the `bore_hex=6` link, but the line is `430` at HEAD. The other three refs (`params.py:102`, `:105` and `calc.py:1166`) are correct. A line number in a debt item rots, and this one was wrong when written.
**Fix:** Cite `tests/test_browser.py` with the step name `warning rendered`, or correct the number to 430.

### IN-04: A verdict that "08 D-09 stands" remains in the ideas index after L41 superseded it

**File:** `docs/ideas/INDEX.md:13`
**Issue:** The bore-shape-selector row still reads "Judged 'not taken' at Phase 12 (08 D-09 stands); a browser test now exists (L39) and Phase 24 takes it". L41, in this phase, supersedes 08 D-09, and the phase updated the conditional-fields row and docstring but not this one. The linked idea file has the same "not taken; 08 D-09 stands" line (`2026-09-27-bore-shape-selector-in-the-web-form.md:50`). It is historical, but a reader now meets a live-sounding "stands" next to a superseding L41.
**Fix:** Append "(superseded by L41)" to the index row, or reword the trigger to "L41 supersedes 08 D-09; Phase 24 takes it".

### IN-05: The L41 text is in two tenses about what the commit declares

**File:** `docs/architecture/decision_log.md:2597-2606`
**Issue:** The "declared set" paragraph says "Eleven rows" and lists them, then says "This commit declares `hub_d` alone ... 23-02 declares the other ten". The final text mixes the plan-time narrative with the end state. Agents are told never to re-litigate a logged decision, and they read the log as the current truth.
**Fix:** Reword in the past tense: "23-01 declared `hub_d` alone, whose parity ...; 23-02 declared the other ten after the proof module went red and then green."

### IN-06: The browser oracle resolves a repeated parameter last-wins where the page resolves it first-wins (external: codex)

**File:** `tests/browser_session.py:325-332` (`given = dict(urllib.parse.parse_qsl(link))`) vs `src/spur/static/app.js:100-101` (`h.get(name)`)
**Issue:** For `bore_hex=0&bore_hex=6` the page reads `URLSearchParams.get` and gets `0`, so the bore fields stay live. `dict(parse_qsl(...))` keeps the last pair, `6`, so `expected_inactive` predicts `bore_d` and `bore_flat` dimmed, and a comparison on that link would fail for the wrong reason. A blank first value is a second case: `bore_hex=&bore_hex=6` gives `''` on the page (default 0, live), while `parse_qsl` drops the blank and keeps `6`. The fixture and flip links come from the app and the schema and never repeat a key, so nothing is red today. It would turn a first hand-written link with a repeated key into a false failure, or worse a false pass on a wrong prediction.
**Fix:** Keep the first occurrence and treat a blank as the default, as the page does:
```python
given: dict[str, str] = {}
for key, raw in urllib.parse.parse_qsl(link, keep_blank_values=True):
    given.setdefault(key, raw)
# number(): a blank first value reads as the schema default
raw = given.get(name) or properties[name].get("default")
```

### IN-07: The refused-pair step does not require both keyway fields to be marked invalid (external: codex)

**File:** `tests/test_browser.py:697-715`
**Issue:** `_expected_422` returns the set of titles the server names (`marked`), but this step discards it (`_, texts = ...`) and checks only that `set(refused_invalid) & set(dimmed)` is non-empty and that some gate is among the invalid fields. The server names three fields for `REFUSED_LINK` (`bore_hex`, `keyway_depth`, `keyway_width`, `calc.py:653-657`). A page that marked `bore_hex` and only `keyway_width` would pass: one keyway field in the intersection, the gate in the gate check. The intended contract is that the coexistence of `.invalid` and `.inactive` holds on the whole refused pair (PD-07). The general marking of a 422 is compared in full at `:394`, so this is a gap in this step's coexistence claim only.
**Fix:** Compare the whole set and require the pair in the intersection:
```python
marked, texts = _expected_422(properties, body)
...
invalid_titles = {_title(properties, n) for n in refused_invalid}
assert invalid_titles == marked, f"marked {sorted(invalid_titles)}, server named {sorted(marked)}"
assert {"keyway_width", "keyway_depth"} <= set(both), both
```

### IN-08: The driver check cannot tell `spoke_count eq 1` from `spoke_count gt 0`; the docstring's residual does not say so

**File:** `tests/test_relations.py:229-239` (state values), `:257-267` (docstring), `:289-314` (loop)
**Issue:** Every state opens its cutout gate at the first value past closed (count 1, cell 0.05), which is the right choice for catching `gt 1`. It also means a relation that is true at exactly that value and false at every other open value cannot be told from the right one. I ran `_assert_relations_name_the_driver_calc_obeys({"hub_d": [("spoke_count", "eq", 1.0)]})` and `{"hole_d": [("hole_count", "eq", 1.0)]}`: both pass. Such a relation would dim `hub_d` on a real 4-spoke part, which tells a user a live value does nothing (L08).
Today the forward check (`_assert_relations_hold_in_calc`) catches both, but only incidentally. For an `eq` condition it closes the gate to threshold + one step (count 2), and that probe raises a `ValidationError` ("Lightening holes need ...") because the dependent is set without its siblings. The designed assertion never ran. The docstring's residual covers only "a gate that never differs across valid parts". It does not say that the eight states probe each gate at one open value, so the `eq`/`gt` choice at the threshold depends on the forward check's incidental failure.
**Fix:** Either add a ninth cell per cutout family at a larger open value (spokes: `spoke_count` 4; holes: `hole_count` 3), or state the residual in the docstring and name the forward check as the one that covers it. Add one meta-test for `spoke_count eq 1` so the coverage cannot lapse silently.

### IN-09: L41 and the threat model still describe an unknown op as an uncaught throw

**File:** `docs/architecture/decision_log.md:2629`; `.planning/phases/23-conditional-form-fields/23-01-PLAN.md:629` (T-23-04)
**Issue:** I agree this is wording drift. L41 says an unknown op "throws and is not short-circuited past". That is still true of `holds()`, but after `cea8c54` the throw is caught per field in `applyRelations()`. The field is left plain and carries a `Cannot tell whether this field is used: …` row, and the form still builds the part. L41 never records that. The plan's T-23-04 says the throw "inside `readHash()` ... the form never builds a part", which is no longer true. The log says never to re-litigate a decision, so an agent reading L41 as current truth will believe an unknown op halts the page, and could remove the catch as dead. The code comment at `app.js:147-153` is the only place the new behaviour and its reason are written down.
**Fix:** Add one sentence to L41 after the "not short-circuited past" clause: the throw is caught per field in `applyRelations()` and nowhere else; the field stays undimmed with its own reason row, and the other fields and the build are unaffected (WR-01). The `23-01-PLAN.md` threat row is historical and can stay with a "superseded by WR-01" note.

### IN-10: The last assertion of the `unknown relation op` step does not check what its comment claims

**File:** `tests/test_browser.py:803` (`expect(broken_reason).to_have_count(1)`)
**Issue:** The `applyRelations()` comment says the row "outlives the next keystroke". After `fill("24")` the step asserts `to_have_count(1)` on the locator `label.field:has([name=...]) .reason`. That locator matches the span whether it holds the error or is empty (an `:empty` span is still in the DOM, just `display: none`), so the assertion is true even if the next `applyRelations()` cleared the text. The step also does not re-check the other fields' dim set after the keystroke. The load-time text assertion is the only check of the error row.
**Fix:** Replace it with the same `to_have_text("Cannot tell whether this field is used: Unknown enabled_when op: ge")` assertion, and repeat the `eval_inactive(bad) == others` check for `teeth=24`.

---

_Reviewed: 2026-10-11_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
