---
phase: 23-conditional-form-fields
fixed_at: 2026-10-12T00:00:00Z
review_path: /Users/halfb00t/git/halfb00t/spur/.planning/phases/23-conditional-form-fields/23-REVIEW.md
iteration: 2
findings_in_scope: 10
fixed: 10
skipped: 0
status: all_fixed
---

# Phase 23: Code Review Fix Report

**Fixed at:** 2026-10-12
**Source review:** `.planning/phases/23-conditional-form-fields/23-REVIEW.md`
**Iteration:** 2 (cumulative: the iteration-1 sections for WR-01..WR-03 are kept below, unchanged)

**Summary:**
- Findings in scope: 10 (IN-01..IN-10; the review has no Critical and no Warning finding, and `fix_scope` was `all`)
- Fixed: 10
- Skipped: 0

IN-01 and IN-06 share one commit (`4f9b87b`): both are one concern in `expected_inactive` in `tests/browser_session.py`, so a split would have left two commits editing the same twelve lines. Every other finding has its own commit. Nine commits, `1a34f17..702d6ba`.

**Verification environment:** `workflow.use_worktrees` is `false`, so every edit, check and commit ran in the main checkout on `gsd/phase-23-conditional-form-fields`, not in an isolated worktree. No worktree, temp branch or recovery sentinel was created. The numbers below reproduce from this tree.

One environment step outside the repo: the first run of `tests/test_browser.py` failed with "Executable doesn't exist ... chromium_headless_shell-1243" (the cache held only revisions 1208 and 1228 although `playwright==1.63.0` is pinned and `.venv/.browser` was up to date). I ran the project's own command from the failure message, `.venv/bin/python -m playwright install --only-shell chromium`, which fetched Chrome Headless Shell 153.0.8010.12 into `~/Library/Caches/ms-playwright`. No repo file changed. The pre-commit hook (`make verify.fast`) refused two commits on a lint error (E501 in IN-08, PT018 in IN-07); both were fixed and re-committed. No hook was bypassed.

**Gate:** `make verify` on the final tree (after the ninth commit), exit 0, with ruff, mypy `--strict`, import-linter (5 kept, 0 broken), the unfinished-work scan and pytest all in it. Result lines:

```
Required test coverage of 96.0% reached. Total coverage: 97.99%
======================= 1295 passed in 300.89s (0:05:00) =======================
```

The count is 1292 (iteration 1) plus 3 new tests: two IN-08 meta-tests and one oracle test (IN-01/IN-06). The `test_pool.py::test_health_reports_pool_state` flake did not occur; there was one run and no re-run.

**Untouched files:** `git diff --exit-code 1a34f17 -- src/spur/calc.py src/spur/params.py src/spur/static/style.css tests/regression/` is empty (checked after the gate). `style.css` is byte-identical to HEAD, so the UAT visuals do not change.

## Fixed Issues

### IN-01: The reason text is formatted differently in the two "independent" evaluators for non-trivial values

**Files modified:** `tests/browser_session.py`, `tests/test_browser.py`
**Commit:** 4f9b87b (shared with IN-06)
**Applied fix:** The code fix, not the range comment. New `_js_number(value)` returns `format(Decimal(repr(float(value))).normalize(), "f")`, and `expected_inactive` uses it where it had `{wanted:g}`. `repr` yields the shortest round-trip digits JavaScript prints, `Decimal(...).normalize()` with the `f` format keeps them positional and writes `1.0` as `1`. I read the JavaScript side from node: `${1e6}` is `1000000`, `${1e-5}` is `0.00001`, `${1e-6}` is `0.000001`, `${1e16}` is `10000000000000000`. The docstring states the range where the two agree (1e-6 <= |value| < 1e21), because JavaScript switches to an exponent outside it and no threshold is near that.
**Test and result:** new `test_the_oracle_reads_a_link_as_the_page_does` in `tests/test_browser.py`, no browser, on a hand-written schema: thresholds 0, 1, 1.0, 0.05, 1e6, 1e-5, 1e-6 and 1e16. Red-then-green: with `{wanted:g}` restored (scratch edit, reverted) it fails with `assert {'dep': 'Needs Gate above 1e+06'} == {'dep': 'Needs Gate above 1000000'}`; with the fix it passes. `python -m pytest tests/test_browser.py -q`: `2 passed in 13.95s`. That is the real-schema run, so the 44 golden-sweep records and the flip links stay green.

### IN-02: A dimmed field's accessible name now contains its own reason, which `aria-describedby` repeats

**Files modified:** `src/spur/static/app.js`, `tests/test_browser.py`
**Commit:** f0bcbc5
**Applied fix:** `reason.setAttribute('aria-hidden', 'true')` where the span is created in `buildForm()`, with a comment saying why. This takes the span out of the label's computed name only; a node an `aria-describedby` references is still read as the description. The `aria-describedby` line is unchanged (`input.setAttribute('aria-describedby', reason.id)` at both sites, byte for byte), and no CSS edit. WR-01's error row is covered by the same span.
**Test and result:** the `inert fields` browser step now asserts every `.reason` carries `aria-hidden="true"` and that exactly the dimmed inputs carry `aria-describedby`. Red before the change (all 31 reasons listed as `reasons readable twice`), green after. `python -m pytest tests/test_browser.py tests/test_api.py -q`: `64 passed in 28.26s`; the static no-disable guard in `test_api.py` does not match `aria-hidden`, as predicted.
**Status:** fixed: requires human verification. The attribute is proven; I did not listen to a screen reader, so the single announcement is the spec's behaviour for `aria-hidden` with `aria-describedby`, not something I heard.
**Human verification (2026-10-12):** the developer opened `http://127.0.0.1:8000/#spoke_count=0` on the shipped tree (`21f6fb7`), tabbed to Hub diameter with VoiceOver and reported the reason row announced once. Closed.

### IN-03: A stale line reference in the new tech-debt item

**Files modified:** `docs/tech_debt/active/2026-10-11-hex-bore-warns-about-default-bore-fields.md`
**Commit:** 247d09e
**Applied fix:** The reference is now `tests/test_browser.py, the \`warning rendered\` step` instead of `:425`, as the finding allows. The `params.py` and `calc.py` references were correct and stay. Docs only; the commit hook (`make verify.fast`) passed.

### IN-04: A verdict that "08 D-09 stands" remains in the ideas index after L41 superseded it

**Files modified:** `docs/ideas/INDEX.md`, `docs/ideas/2026-09-27-bore-shape-selector-in-the-web-form.md`
**Commit:** 702d6ba
**Applied fix:** "(superseded by L41)" is added where each verdict is stated: inside the parenthesis in the index row (`08 D-09 stands; superseded by L41`) and after the Verdict sentence in the idea file (the matching line, now at line 50). In the index row I put it next to the "stands" clause rather than at the very end of the row, where it would have followed the unrelated "otherwise revisit" trigger. The Phase 12 judgement is kept as the record.

### IN-05: The L41 text is in two tenses about what the commit declares

**Files modified:** `docs/architecture/decision_log.md`
**Commit:** efded46
**Applied fix:** The declared-set paragraph of L41 is in the past tense: "23-01 declared `hub_d` alone ...; 23-02 declared the other ten after its proof module went red and then green", and the two Not-declared items "which 23-02 filed as ...". Four lines changed; no decision and no other sentence of L41 changed. This edit to the locked log was authorised by the human's `--all`.

### IN-06: The browser oracle resolves a repeated parameter last-wins where the page resolves it first-wins (external: codex)

**Files modified:** `tests/browser_session.py`, `tests/test_browser.py`
**Commit:** 4f9b87b (shared with IN-01)
**Applied fix:** Exactly the finding's semantics. `expected_inactive` builds `given` with `parse_qsl(link, keep_blank_values=True)` and `setdefault`, so the first occurrence wins, and `number()` reads `given.get(name) or <schema default>`, so a blank raw value is the default. The comment names the page's behaviour (`URLSearchParams.get`, then `effective()`) and the case that was wrong.
**Test and result:** the same new test: `gate=0&gate=6` leaves the dependent live, `gate=6&gate=0` dims it, `gate=&gate=6` is the default 0 and leaves it live. Red-then-green: before the change the first assertion fails with `assert {'dep': 'Needs Gate = 0'} == {}`; after it the test passes. Browser run as above: `2 passed in 13.95s`.

### IN-07: The refused-pair step does not require both keyway fields to be marked invalid (external: codex)

**Files modified:** `tests/test_browser.py`
**Commit:** 6889ea4
**Applied fix:** The step keeps `marked` from `_expected_422` and asserts the invalid titles equal what the server named (`bore_hex`, `keyway_depth` and `keyway_width` titles). It then requires both keyway fields to be in the invalid-and-dimmed intersection. I derived the pair from the link (`set(parse_qs(REFUSED_LINK)) - gates`) rather than hard-coding the two names as the finding sketched, and asserted it has two members so an empty pair cannot pass. The old non-empty-intersection and gate-marked assertions are kept.
**Test and result:** red-then-green with a scratch mutation of `problems()` in `app.js` that skipped marking `keyway_depth` on this link only (reverted before the commit). The old step still passed (`2 passed in 12.50s`); the new one fails with `marked ['Hex bore A/F', 'Keyway width'], server named ['Hex bore A/F', 'Keyway depth', 'Keyway width']`. On the real `app.js`: `2 passed in 11.91s`; after the lint fix and the re-commit, `2 passed in 11.78s`.

### IN-08: The driver check cannot tell `spoke_count eq 1` from `spoke_count gt 0`; the docstring's residual does not say so

**Files modified:** `tests/test_relations.py`
**Commit:** 8a16990
**Applied fix:** The first fix option, with the residual also stated. `CUTOUT_STATES` gains `"spokes (4)"` (`spoke_count` 4 with the same full set) and `"holes (3)"` (`hole_count` 3), so each count gate is probed at two open values and the check runs in twelve whole-part states, not eight. The module docstring, the helper docstrings and the `* 8` in the control test are updated (the control now multiplies `len(CUTOUT_STATES) * len(BORE_STATES)`). All four new cells validate (measured: 0, 1, 0 and 1 warnings for spokes/holes crossed with round/hex bore). A new parametrised meta-test, `test_a_relation_true_only_at_the_first_open_count_goes_red`, pins `hub_d <- spoke_count eq 1` and `hole_d <- hole_count eq 1` to the check's own `wrong or extra driver` assertion.
**Test and result:** red-then-green with the reviewer's probe, run before editing: `_assert_relations_name_the_driver_calc_obeys({hub_d: [spoke_count eq 1]})` and the `hole_d <- hole_count eq 1` twin both returned (`PASS (gap) ... cells 8`). After the change both fail on the designed assertion: `hub_d in spokes (4) + round bore: the relation says ignored, calc says used: wrong or extra driver` and `hole_d in holes (3) + round bore: ...`. `python -m pytest tests/test_relations.py -q`: `56 passed in 0.17s`.

### IN-09: L41 and the threat model still describe an unknown op as an uncaught throw

**Files modified:** `docs/architecture/decision_log.md`, `.planning/phases/23-conditional-form-fields/23-01-PLAN.md`, `.planning/phases/23-conditional-form-fields/23-SECURITY.md`
**Commit:** 1ff2f17
**Applied fix:** In L41, after the "not short-circuited past" clause, one sentence: the throw is caught per field in `applyRelations()` and nowhere else; the field stays undimmed with its own reason row (`Cannot tell whether this field is used: ...`); the other fields and the build are unaffected (WR-01, `cea8c54`). The `;` before the `holds()` clause became a full stop. `23-01-PLAN.md` T-23-04 gets "Superseded by WR-01 (`cea8c54`): the throw is caught per field" appended and is not rewritten. `23-SECURITY.md` T-23-04: the residual clause "23-REVIEW WR-01 (latent throw path) — advisory, triage before Phase 24 widens the grammar" is replaced with "WR-01 fixed in `cea8c54`: the throw is caught per field in `applyRelations()` and surfaced as the field's reason row". The row stays `closed` and `threats_open: 0` is unchanged. The edit to the locked log was authorised by the human's `--all`; no other decision changed.

### IN-10: The last assertion of the `unknown relation op` step does not check what its comment claims

**Files modified:** `tests/test_browser.py`
**Commit:** 10049f2
**Applied fix:** `expect(broken_reason).to_have_count(1)` is replaced with `to_have_text(unreadable)` (the message is now a local so the load-time and post-keystroke assertions share it), and the other fields' dim set is re-checked against `expected_inactive(properties, "teeth=24")` minus the broken field.
**Test and result:** red-then-green with a scratch mutation of `app.js` that cleared any "Cannot tell" row in the form's input listener (reverted before the commit). The old assertion still passed (`2 passed in 11.75s`); the new one fails on `label.field:has([name=bore_d]) .reason`, `Actual value:` empty. My first mutation cleared every reason row and broke an earlier step, so it proved nothing and I narrowed it. On the real `app.js`: `2 passed in 9.69s`.

## Skipped Issues

None.

## Debt filed

None.

## Iteration 1 (WR-01…03)

The three sections below are the iteration-1 report, kept as written. Their commits (`cea8c54`, `59deb6e`, `ef5d4a7`) were not touched in iteration 2.

### WR-01: An unknown `enabled_when` op freezes the UI silently and leaves a stale part, dimensions and download links on screen

**Files modified:** `src/spur/static/app.js`, `tests/test_browser.py`
**Commit:** cea8c54
**Applied fix:** `holds()` still throws on an unknown op (D-02). `applyRelations()` now catches per field, and the call sites are unchanged. The review suggested wrapping the call sites, but the `tests/test_api.py` pins fix them byte for byte (`form.addEventListener('input', () => { applyRelations(); scheduleUpdate(); });`, `readHash(); update();` and the rest). Catching inside the function also covers all four sites, including `readHash()` in the load IIFE, with one change.

On a throw, the field loses `.inactive`. It is never dimmed on a guess and never treated as plainly active either. Its own reason row reads `Cannot tell whether this field is used: Unknown enabled_when op: ge`, with `aria-describedby` pointing at it. I chose the field's reason row over `#messages` because every build rewrites `#messages` (`renderInfo` / `fail`), so a message there would vanish on the next keystroke. The reason row persists. The other fields are still evaluated, and `update()` always runs, so the part follows the form.

A gate that is not a field (`fields.get(...)` destructuring in `effective()` / `need()`) is covered by the same catch.

The comment above `applyRelations()` carries the why. `gearQuery()` and the field-name / `DIMS` pins are byte-identical.

Test: a new browser step, `unknown relation op`, in `tests/test_browser.py`. It serves `/api/schema` with the first related field's first op changed to `ge`, through `page.route`, on its own page. It checks:
- the load still builds the part (`#dl-stl` gets its href);
- the broken field's reason row carries the text above;
- every other field dims exactly as `expected_inactive` says;
- typing in `teeth` still sends `/api/info?teeth=24` and updates the download link.

Seen red: with the old `app.js` restored, the step fails at `Locator expected to have attribute 'api/model.stl?teeth=23'  Actual value: None` (`#dl-stl` stays `aria-disabled`). With the fix it passes (`step unknown relation op: 5.53 s`).

Status note: this is an error-handling change, not a logic fix. The decision log's wording at `decision_log.md:2629` ("an unknown op anywhere in a list throws") remains true of `holds()`. I did not edit the locked text.

### WR-02: The "never disables, hides or clears a field" guard is narrower than the contract it claims, and has a false-positive hole

**Files modified:** `tests/test_api.py`
**Commit:** 59deb6e
**Applied fix:** `writes_a_field_shut` is now a case-insensitive compiled pattern. It covers:
- the properties `disabled|hidden|readOnly|inert` with `=(?!=)`, so `x.hidden === y` is no longer read as an assignment;
- `setAttribute` and `toggleAttribute` of `disabled|hidden|readonly|inert`;
- `classList.add|toggle` of `hidden|disabled|readonly|inert`;
- `.innerHTML`, `insertAdjacentHTML`;
- `.style.display|visibility|pointerEvents|opacity`, plus `.style.setProperty('display|visibility|pointer-events|opacity')`, a small addition for the equivalent call.

There is one positive probe per alternative (19) and negative probes for a `===` and a `==` comparison, `classList.toggle('inactive', off)`, `classList.remove('inactive')` and `setAttribute('aria-describedby', ...)`.

"Clears or rewrites" is a `.value` write, which `readHash()` and `#reset` do legitimately (`mateInput.value = ''` is also a pin). The review's sketch had no answer for that, so a second pattern (`.value =`, `.reset(`, `.setRangeText(`, `removeAttribute('value')`) is checked only inside the section between the `relations (L41)` and `messages` banners. That section holds `effective`, `holds`, `need` and `applyRelations`. An assertion fails loudly if the banners move and the section is not found. No existing pin was loosened.

Seen red on `app.js` (reverted after each), with the old pattern passing all four of these:
- `input.readOnly = true;` in `applyRelations()`: `assert not <re.Match ... match='.readOnly ='>`
- `input.value = '';` in `applyRelations()`: `assert not <re.Match ... match='.value ='>`
- `wrap.style.pointerEvents = 'none';`: `match='.style.pointerEvents'`
- `wrap.classList.add('hidden');`: `match="classList.add('hidden'"`

On the test itself: dropping the `opacity` alternative fails the probe `x.style.opacity = '.5'`, and dropping `(?!=)` fails `if (x.hidden === y) return;`.

### WR-03: The calc parity proof cannot tell a right driver from a wrong one for the seven cutout dependents (external: codex)

**Files modified:** `tests/test_relations.py`
**Commit:** ef5d4a7
**Applied fix:** New `_assert_relations_name_the_driver_calc_obeys()`. In eight whole-part states (four cutout patterns times a round and a hex bore), a field's relation must hold exactly when `derive()` does not call the field ignored. A refusal counts as ignored for a `REFUSED` field only, and a field refused anywhere else fails the check. It is tied to calc by the same fragment test as the forward check (`dep (value unit)` in an "ignored" warning). The value tried is the state's own, else the field's default, else `minimum + step`.

The review's sketch was not used as written. I checked it against the calc ignore rules (`calc.py:1207`, `:1221`, `:1239`) and it opens every driver together, which `calc` refuses (`Only one body cutout pattern per part: spoke_count (4), hole_count (3) and hex_cell (4) ar...`). Each family is opened alone as a full set, because the spoke and hole fields are required once their count is set and `hex_wall` must be at least 0.4 mm. Each gate sits at the first value past its closed one (the count 1, the cell 0.05 mm). That is also what catches a threshold off by one. All eight states validate (measured). The check runs in 0.17 s inside the commit slice.

Tests added:
- `test_each_relation_names_the_driver_calc_obeys`: the real map, with the cell count asserted.
- `test_the_driver_check_passes_for_the_declared_owner_alone`: a control for the seven cutout fields on their own gate.
- `test_a_relation_on_the_wrong_driver_goes_red[21]`: each cutout field on each of the other two cutout gates and on `bore_hex eq 0`; every swap must raise `wrong or extra driver`.
- `test_an_extra_gate_beside_the_right_driver_goes_red[21]`: the same 21 as an extra AND-conjunct.

Seen red against the real model: `spoke_width` gated on `hole_count gt 0` in `params.py`, reverted after. Result: `2 failed, 52 passed`. The old forward test stayed green, which confirms the review's claim. The new ones failed with:

```
AssertionError: spoke_width in spokes + round bore: the relation says ignored, calc says used: wrong or extra driver
FAILED tests/test_relations.py::test_each_relation_names_the_driver_calc_obeys
FAILED tests/test_relations.py::test_the_driver_check_passes_for_the_declared_owner_alone
```

An ad hoc probe of other wrong maps, outside the repo, also went red on the driver check: `bore_d <- spoke_count gt 0`, `keyway_width <- hole_count gt 0`, `bore_d <- bore_hex gt 0`, `hub_d <- spoke_count gt 1`, `hub_d <- spoke_count eq 0`, `hex_wall <- hex_cell gt 5`, `hex_wall <- hex_cell gt 0.05` and `hole_d <- hole_count gt 1`. The forward check was already red on all of these, but often on an incidental `ValidationError` at its `base = derive(...)` line (the review's own observation). The driver check now fails on a named assertion.

One honest limit, recorded in the docstring: a conjunct that never differs across valid parts passes. `hole_d <- [hole_count gt 0, spoke_count eq 0]` is equivalent on every valid part because two patterns are refused, so nothing a user sees changes.

---

_Fixed: 2026-10-12_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 2_
