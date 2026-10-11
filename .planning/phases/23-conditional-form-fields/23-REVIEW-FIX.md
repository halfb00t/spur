---
phase: 23-conditional-form-fields
fixed_at: 2026-10-11T00:00:00Z
review_path: /Users/halfb00t/git/halfb00t/spur/.planning/phases/23-conditional-form-fields/23-REVIEW.md
iteration: 1
findings_in_scope: 3
fixed: 3
skipped: 0
status: all_fixed
---

# Phase 23: Code Review Fix Report

**Fixed at:** 2026-10-11
**Source review:** `.planning/phases/23-conditional-form-fields/23-REVIEW.md`
**Iteration:** 1

**Summary:**
- Findings in scope: 3 (WR-01, WR-02, WR-03; no Critical findings)
- Fixed: 3
- Skipped: 0

Info findings IN-01..IN-07 were out of scope and left alone. No fix touched their lines, except that WR-01's catch block sits in the same `applyRelations()` function IN-02 cites (`app.js:153-154`). IN-02's `aria-hidden` suggestion was not applied.

**Verification environment:** `workflow.use_worktrees` is `false` in `.planning/config.json`, so every edit, check and commit ran in the main checkout on `gsd/phase-23-conditional-form-fields`, not in an isolated worktree. The numbers below reproduce from this tree.

**Gate:** `make verify` on the final tree (after the third commit), with ruff, mypy `--strict`, import-linter, the unfinished-work scan and pytest all in it. Result line: `1292 passed in 318.37s (0:05:18)`, `Required test coverage of 96.0% reached. Total coverage: 97.99%`. It also passed after the first commit (`1248 passed in 320.84s`). The pre-commit hook (`make verify.fast`) passed on all three commits and no hook was bypassed. `git diff --exit-code 020df5f -- src/spur/calc.py tests/regression/` is empty, and `src/spur/params.py` is unchanged.

## Fixed Issues

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

### WR-03: The calc parity proof cannot tell a right driver from a wrong one for the seven cutout dependents

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

## Skipped Issues

None.

## Debt filed

None.

---

_Fixed: 2026-10-11_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
