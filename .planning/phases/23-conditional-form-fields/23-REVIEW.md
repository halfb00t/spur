---
phase: 23-conditional-form-fields
reviewed: 2026-10-11T00:00:00Z
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
  warning: 2
  info: 5
  total: 7
status: issues_found
---

# Phase 23: Code Review Report

**Reviewed:** 2026-10-11
**Depth:** standard
**Files Reviewed:** 20
**Status:** issues_found

## Summary

Phase 23 adds `enabled_when` relation metadata on `GearParams` (built by `when()` / `_extra()`), emits it through `/api/schema`, and has generic `app.js` code dim an inert field while keeping it editable and sent. `tests/test_relations.py` proves each of the eleven relations against `calc`. The browser test checks the dim state under the golden links.

I checked each of the eleven relations against `calc.derive()` / `calc.check()` / `model.py`, and each one is backed.
- `bore_d` and `bore_flat` are never read on the `bore_hex > 0` branch of `check()`, `bore_rim_limit`, `bore_mouth_limit`, `bore_effective` or `model._cut_bore`.
- The spoke, hole and honeycomb dependents are read only under their own count or cell gate.
- The keyway pair is a 422 under a hex bore (`calc.py:652-657`), which `REFUSED` pins.

No relation contradicts the code, and no default, bound or type moved (L05 holds). The `eq`/`gt` evaluators in JS and Python agree on every op and every current value.

I ran the proof module and the static checks:
- `pytest tests/test_relations.py`: 10 passed.
- `ruff check src tests`: clean.
- `mypy --strict` on `params.py`, `test_relations.py` and `browser_session.py`: clean.

I did not run the browser test.

No security issues were found. The reason text is written with `textContent`, ids are built from schema field names, and nothing user-controlled reaches markup.

The two warnings are a failure-mode gap in the new JS and a regression guard that is narrower than the contract it claims to enforce. The info items are latent divergences and stale documentation references.

## Warnings

### WR-01: An unknown `enabled_when` op freezes the UI silently and leaves a stale part, dimensions and download links on screen

**File:** `src/spur/static/app.js:387` (also `:420`, `:148-157`)
**Issue:** `holds()` throws on an op it does not know. That is deliberate (D-02), but the throw has no visible effect on the page.
- The input listener is `() => { applyRelations(); scheduleUpdate(); }`. A throw in `applyRelations()` means `scheduleUpdate()` never runs. Every later keystroke changes the form, while the dimensions table, the 3D part and the `#dl-stl` / `#dl-step` links (which `setDownloads(null)` only clears inside `update()`) keep showing the previous parameters. That is a printed number and a download that no longer match the form, which L08 forbids.
- On load, `readHash()` sits in the async IIFE outside any `try`. A throw there is an unhandled rejection: the form renders, but no `update()` runs and no message is shown. The only trace is in the console.
- `when()`'s `Literal` makes a bad op a `mypy` error today. The path stays open for a hand-edited schema, a stale cached `app.js` against a newer server, or Phase 24 extending the grammar on one side only.

**Fix:** Keep the throw but make it visible and stop it from decoupling the form from the part. For example:
```js
form.addEventListener('input', () => {
  try { applyRelations(); }
  catch (err) { showMessages([`Form relation error: ${err.message}`]); }
  scheduleUpdate();
});
```
Wrap the `readHash()` call in the IIFE the same way, so a bad op shows a message instead of a blank page. If the throw must stay uncaught, call `scheduleUpdate()` first so the part always follows the fields.

### WR-02: The "never disables, hides or clears a field" guard is narrower than the contract it claims, and has a false-positive hole

**File:** `tests/test_api.py:257-261`
**Issue:** The comment and L41 say a relation "never disables, hides, clears or rewrites" a field. The regex enforces only these patterns:
- `.disabled =`
- `setAttribute('disabled'|'hidden')`
- `.hidden =`
- `.innerHTML`
- `insertAdjacentHTML`
- `.style.display|visibility`

It does not catch:
- `classList.add('hidden')`
- `toggleAttribute('disabled')` or `toggleAttribute('hidden')`
- `.readOnly = true`
- `.inert = true` or `setAttribute('inert')`
- `.style.pointerEvents` or `.style.opacity`
- `input.value = ''`, which is the "clears" case

A future edit that makes dimmed fields read-only, or clears them, would pass this test. `\.hidden\s*=` also matches the prefix of `x.hidden === y`, a false positive that would block a harmless comparison. The test's non-vacuity probe only checks `x.hidden = true`.

**Fix:** Widen the pattern to the set the contract names and anchor the equality case:
```python
writes_a_field_shut = (
    r"\.(?:disabled|hidden|readOnly|inert)\s*=(?!=)"
    r"|(?:setAttribute|toggleAttribute)\(\s*['\"](?:disabled|hidden|readonly|inert)['\"]"
    r"|classList\.(?:add|toggle)\(\s*['\"](?:hidden|disabled)['\"]"
    r"|\.innerHTML\b|insertAdjacentHTML"
    r"|\.style\.(?:display|visibility|pointerEvents|opacity)\b"
)
```
Keep the positive probe, and add one probe for each new alternative so none can stop matching silently.

## Info

### IN-01: The reason text is formatted differently in the two "independent" evaluators for non-trivial values

**File:** `tests/browser_session.py:343` vs `src/spur/static/app.js:134-137`
**Issue:** JS builds the reason with `${value}` (JS number-to-string). The Python reference uses `{wanted:g}`. They agree for 0, 0.05 and 1, which are all current thresholds. They diverge once a threshold is at least 1e6 (`1e+06` against `1000000`) or below 1e-4 (`1e-05` against `0.00001`). The step's "second implementation agrees on every state" proof would then fail on text, not on logic, the first time Phase 24 declares such a value.
A related latent difference: `expected_inactive` reads the link with `dict(parse_qsl(...))`, so a repeated key is last-wins. `URLSearchParams.get` is first-wins. The fixture links come from the app itself and never repeat a key, so this is not reachable today.
**Fix:** Format with `repr(float)` trimmed of `.0`, or compare numerically through the schema rather than by string. At minimum, add a comment that the values must stay inside the range where `:g` and JS agree.

### IN-02: A dimmed field's accessible name now contains its own reason, which `aria-describedby` repeats

**File:** `src/spur/static/app.js:87-89`, `:153-154`
**Issue:** The `.reason` span sits inside the wrapping `<label>`. Its text becomes part of the input's implicit label, along with the unit and the description, so the accessible name reads "Hub Ø mm Needs Spoke arms above 0 ...". `aria-describedby` then points at the same span, so a screen reader announces the reason twice. The unit and the description already behave this way, so the pattern is not new.
**Fix:** Give the reason `aria-hidden="true"` and keep `aria-describedby`. Or move the span out of the label.

### IN-03: A stale line reference in the new tech-debt item

**File:** `docs/tech_debt/active/2026-10-11-hex-bore-warns-about-default-bore-fields.md:9`
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

---

_Reviewed: 2026-10-11_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
