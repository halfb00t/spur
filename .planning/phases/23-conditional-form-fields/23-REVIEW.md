---
phase: 23-conditional-form-fields
reviewed: 2026-10-11T14:00:00Z
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
  warning: 3
  info: 7
  total: 10
status: issues_found
---

# Phase 23: Code Review Report

**Reviewed:** 2026-10-11
**Depth:** standard
**Files Reviewed:** 20
**Status:** issues_found

## Summary

Phase 23 adds `enabled_when` relation metadata on `GearParams` (built by `when()` / `_extra()`), emits it through `/api/schema`, and has generic `app.js` code dim an inert field while keeping it editable and sent. `tests/test_relations.py` proves each of the eleven relations against `calc`. The browser test checks the dim state under the golden links.

This pass re-verified every earlier finding against the current tree (WR-01, WR-02 and IN-01..IN-05 all still hold; only line numbers moved, and IN-03's cited line is corrected) and added the three claims from the Codex lane that I could confirm against the source (WR-03, IN-06, IN-07). The review scope handed to this pass was the ten source and test files; the earlier review's doc and README files stay in `files_reviewed_list` because IN-03..IN-05 cite them.

I checked each of the eleven relations against `calc.derive()` / `calc.check()` / `model.py`, and each one is backed.
- `bore_d` and `bore_flat` are never read on the `bore_hex > 0` branch of `check()`, `bore_rim_limit`, `bore_mouth_limit`, `bore_effective` or `model._cut_bore`.
- The spoke, hole and honeycomb dependents are read only under their own count or cell gate.
- The keyway pair is a 422 under a hex bore (`calc.py:652-657`), which `REFUSED` pins.

No relation contradicts the code, and no default, bound or type moved (L05 holds). The `eq`/`gt` evaluators in JS and Python agree on every op and every current value.

The static checks from the earlier pass: `pytest tests/test_relations.py` 10 passed, `ruff check src tests` clean, `mypy --strict` on `params.py`, `test_relations.py` and `browser_session.py` clean. I did not run the browser test. For WR-03 I ran `_assert_relations_hold_in_calc` from `tests/test_relations.py` on deliberately wrong relation maps from a scratch script outside the repo, and changed no repo file.

No security issues were found. The reason text is written with `textContent`, ids are built from schema field names, and nothing user-controlled reaches markup.

The three warnings are a failure-mode gap in the new JS, a regression guard narrower than the contract it claims, and a parity proof that cannot tell a right driver from a wrong one for most of the relations. The info items are latent divergences, a weak assertion and stale documentation references.

## Warnings

### WR-01: An unknown `enabled_when` op freezes the UI silently and leaves a stale part, dimensions and download links on screen

**File:** `src/spur/static/app.js:387` (also `:420`, `:148-157`)
**Issue:** `holds()` throws on an op it does not know. That is deliberate (D-02), but the throw has no visible effect on the page.
- The input listener is `() => { applyRelations(); scheduleUpdate(); }`. A throw in `applyRelations()` means `scheduleUpdate()` never runs. Every later keystroke changes the form, while the dimensions table, the 3D part and the `#dl-stl` / `#dl-step` links (which `setDownloads(null)` only clears inside `update()`) keep showing the previous parameters. That is a printed number and a download that no longer match the form, which L08 forbids.
- On load, `readHash()` sits in the async IIFE outside any `try`. A throw there is an unhandled rejection: the form renders, but no `update()` runs and no message is shown. The only trace is in the console.
- `when()`'s `Literal` makes a bad op a `mypy` error today. The path stays open for a hand-edited schema, a stale cached `app.js` against a newer server, or Phase 24 extending the grammar on one side only.
- Still true at HEAD on the other two call sites: the `hashchange` handler (`:389`, `readHash(); update();`) and `#reset` (`:397`, `applyRelations(); update();`) both skip `update()` when `applyRelations()` throws.

**Fix:** Keep the throw but make it visible and stop it from decoupling the form from the part. For example:
```js
form.addEventListener('input', () => {
  try { applyRelations(); }
  catch (err) { showMessages([`Form relation error: ${err.message}`]); }
  scheduleUpdate();
});
```
Wrap the `readHash()` call in the IIFE, the `hashchange` handler and `#reset` the same way, so a bad op shows a message instead of a blank page. If the throw must stay uncaught, call `scheduleUpdate()` / `update()` first so the part always follows the fields.

### WR-02: The "never disables, hides or clears a field" guard is narrower than the contract it claims, and has a false-positive hole

**File:** `tests/test_api.py:255-261`
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

### WR-03: The calc parity proof cannot tell a right driver from a wrong one for the seven cutout dependents (external: codex)

**File:** `tests/test_relations.py:167-190` (probe base at `:169`, gate value from `_closed` at `:129-135`); `src/spur/calc.py:1207-1218`, `:1221-1229`, `:1239-1247`
**Issue:** `_assert_relations_hold_in_calc` builds every probe from a defaults-based model. For each condition it sets only that condition's gate to its closed value and the dependent to `minimum + step` or `maximum`. Every other field stays at its default. For a `gt 0` gate the closed value is `0`, which is also the default, so in each probe all three cutout gates (`spoke_count`, `hole_count`, `hex_cell`) are already off. `calc` prints the "ignored" sentence for a cutout dependent whenever its own family's gate is 0 (`spoke_count == 0` at `:1207`, `hole_count == 0` at `:1221`, `hex_cell` 0 at `:1239`), whatever the declared driver is. The check only asks that some warning names `dep (value unit)`, so it is blind to which driver closed the field.

I ran the test's own function on deliberately wrong relation maps. These pass, so the test would not turn red:
- Each of the seven cutout dependents (`spoke_width`, `hub_d`, `rim_wall`, `spoke_fillet`, `hole_d`, `hole_circle_d`, `hex_wall`) gated on either of the two other cutout drivers instead of its own, for example `spoke_width <- hole_count gt 0` or `hex_wall <- spoke_count gt 0`. That is 14 swaps.
- Each of the seven gated on `bore_hex eq 0` (closed value 0.05, `spoke_count` still the default 0). That is 7 more.
- Each of those 21 added as an extra AND-conjunct beside the right driver, because the loop probes each condition alone. A field then dims when an unrelated gate is off while calc really uses it.

These do turn red, so the coverage is real but narrow:
- Any bore-family dependent (`bore_d`, `bore_flat`, `keyway_width`, `keyway_depth`) gated on a cutout driver, because at defaults `bore_hex` is 0 and the bore field is live (refused or `derive()` moves).
- A threshold or op that opens the field: `hub_d <- spoke_count gt 1`, `hub_d <- spoke_count eq 0`, `hex_wall <- hex_cell gt 5`, `bore_d <- bore_hex gt 0`. These fail incidentally, some on a `ValidationError` at the `base = derive(...)` line (`:169`) and not on a designed assertion.

The reverse check (`_assert_calc_ignores_only`, `:193-221`) only requires that each field `calc` calls ignored has some relation, not that its relation names the right driver. `test_cli.py` and `test_api.py` check the schema shape only. The browser test derives its expected dim set from the same `enabled_when` metadata, so it agrees with any wrong relation too (WR-03's subject is the only place a driver is checked against `calc`).

The product consequence: all eleven declarations are correct today, but the proof meant to hold them to `calc` would accept a swap in Phase 24 or a later edit. The page would then dim a live hole or spoke field (and show "Needs Spoke arms above 0" for a part that has holes), which tells someone cutting metal that a value does nothing when it does (L08). The swap needs no change to `calc`, so nothing else would catch it.

**Fix:** Add the negative case the forward check lacks. For each dependent, take a valid base where every other driver is open, close only the declared one, and separately close each driver the dependent does not declare while its own are open. For example:
```python
OPEN = {"spoke_count": 4, "spoke_width": 4, "hub_d": 20, "rim_wall": 3,
        "hole_count": 3, "hole_d": 3, "hole_circle_d": 24,
        "hex_cell": 4, "hex_wall": 1}   # pick values that validate; bore_hex stays 0

def _assert_declared_driver_is_the_one(dep, conditions, value):
    own = {gate for gate, _, _ in conditions}
    for gate, op, threshold in conditions:                      # closing the declared gate
        gear = GearParams.model_validate({**OPEN, gate: _closed(gate, op, threshold), dep: value})
        assert _is_named_ignored(gear, dep, value), (dep, gate)
    for other in _DRIVERS - own:                                # closing an undeclared one
        if other not in OPEN: continue
        gear = GearParams.model_validate({**OPEN, other: 0, dep: value})
        assert not _is_named_ignored(gear, dep, value), f"{dep} is live with {other} off"
```
Each of the 21 swaps above should then go red; add a probe for one swap (like `test_a_relation_calc_uses_goes_red`) so the new check cannot go vacuous. For `bore_hex eq 0` as a wrong gate on a cutout dependent, the undeclared-driver case needs `bore_hex = step` with the cutout open, which the same loop covers by listing `bore_hex` in the driver set.

## Info

### IN-01: The reason text is formatted differently in the two "independent" evaluators for non-trivial values

**File:** `tests/browser_session.py:353` vs `src/spur/static/app.js:138-141`
**Issue:** JS builds the reason with `${value}` (JS number-to-string). The Python reference uses `{wanted:g}`. They agree for 0, 0.05 and 1, which are all current thresholds. They diverge once a threshold is at least 1e6 (`1e+06` against `1000000`) or below 1e-4 (`1e-05` against `0.00001`). The step's "second implementation agrees on every state" proof would then fail on text, not on logic, the first time Phase 24 declares such a value.
A related latent difference: `expected_inactive` reads the link with `dict(parse_qsl(...))`, so a repeated key is last-wins. `URLSearchParams.get` is first-wins. The fixture links come from the app itself and never repeat a key, so this is not reachable today. (IN-06 below carries the concrete repeated-key case.)
**Fix:** Format with `repr(float)` trimmed of `.0`, or compare numerically through the schema rather than by string. At minimum, add a comment that the values must stay inside the range where `:g` and JS agree.

### IN-02: A dimmed field's accessible name now contains its own reason, which `aria-describedby` repeats

**File:** `src/spur/static/app.js:87-90`, `:153-154`
**Issue:** The `.reason` span sits inside the wrapping `<label>`. Its text becomes part of the input's implicit label, along with the unit and the description, so the accessible name reads "Hub Ø mm Needs Spoke arms above 0 ...". `aria-describedby` then points at the same span, so a screen reader announces the reason twice. The unit and the description already behave this way, so the pattern is not new.
**Fix:** Give the reason `aria-hidden="true"` and keep `aria-describedby`. Or move the span out of the label.

### IN-03: A stale line reference in the new tech-debt item

**File:** `docs/tech_debt/active/2026-10-11-hex-bore-warns-about-default-bore-fields.md:10`
**Issue:** The file cites `tests/test_browser.py:425` for the `bore_hex=6` link, but the line is `430` at HEAD. The other three refs (`params.py:102`, `:105` and `calc.py:1166`) are correct. A line number in a debt item rots, and this one was wrong when written. (The earlier pass cited the file line as `:9`; the stale reference is on line 10.)
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

**File:** `tests/browser_session.py:325-332` (`given = dict(urllib.parse.parse_qsl(link))`) vs `src/spur/static/app.js:99-103` (`h.get(name)`)
**Issue:** I confirmed the divergence IN-01 mentions in passing, with a concrete case. For `bore_hex=0&bore_hex=6` the page reads `URLSearchParams.get` and gets `0`, so the bore fields stay live. `dict(parse_qsl(...))` keeps the last pair, `6`, so `expected_inactive` predicts `bore_d` and `bore_flat` dimmed, and a comparison on that link would fail for the wrong reason. A blank first value is a second case: `bore_hex=&bore_hex=6` gives `''` on the page (default 0, live), while `parse_qsl` drops the blank and keeps `6`. The fixture and flip links come from the app and the schema and never repeat a key, so nothing red today. It would turn a first hand-written link with a repeated key into a false failure, or worse a false pass on a wrong prediction.
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
**Issue:** `_expected_422` returns the set of titles the server names (`marked`), but this step discards it (`_, texts = ...`) and checks only that `set(refused_invalid) & set(dimmed)` is non-empty and that some gate is among the invalid fields. The server names three fields for `REFUSED_LINK` (`bore_hex`, `keyway_depth`, `keyway_width`, `calc.py:653-657`). A page that marked `bore_hex` and only `keyway_width` would pass: one keyway field in the intersection, the gate in the gate check. The intended contract is that the coexistence of `.invalid` and `.inactive` holds on the whole refused pair (PD-07). The general marking of a 422 is compared in full at `:394`, so this is a gap in this step's coexistence claim only, not in `problems()` as a whole.
**Fix:** Compare the whole set and require the pair in the intersection:
```python
marked, texts = _expected_422(properties, body)
...
invalid_titles = {_title(properties, n) for n in refused_invalid}
assert invalid_titles == marked, f"marked {sorted(invalid_titles)}, server named {sorted(marked)}"
assert {"keyway_width", "keyway_depth"} <= set(both), both
```

---

_Reviewed: 2026-10-11_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
