---
phase: 33-interfaces-and-parity
reviewed: 2026-10-29T00:00:00Z
depth: standard
files_reviewed: 33
files_reviewed_list:
  - bench/latency.py
  - bench/RESULTS.md
  - docs/architecture/cli.md
  - docs/architecture/decision_log.md
  - docs/architecture/http-api.md
  - docs/architecture/web-ui.md
  - docs/ideas/2026-10-27-gear-result-rows-from-the-schema.md
  - docs/ideas/INDEX.md
  - docs/tech_debt/INDEX.md
  - docs/tech_debt/resolved/2026-10-21-an-accepted-link-token-builds-under-a-blank-box.md
  - docs/tech_debt/resolved/2026-10-27-shaft-contention-row.md
  - docs/tech_debt/resolved/2026-10-27-shaft-model-two-guard-lines-no-passing-test-reaches.md
  - docs/tech_debt/resolved/2026-10-27-shaft-volume-guard-accepts-an-uncut-chamfer.md
  - README.md
  - src/spur/app.py
  - src/spur/cli.py
  - src/spur/shaft_model.py
  - src/spur/shaft_params.py
  - src/spur/static/app.js
  - src/spur/static/index.html
  - src/spur/static/style.css
  - tests/number_box_tokens.py
  - tests/shaft_parity.py
  - tests/test_api.py
  - tests/test_bench.py
  - tests/test_browser.py
  - tests/test_cli.py
  - tests/test_number_as_written.py
  - tests/test_seam.py
  - tests/test_shaft_interfaces.py
  - tests/test_shaft_model.py
  - tests/test_shaft_params.py
  - tests/test_shaft_parity.py
findings:
  critical: 0
  warning: 4
  info: 9
  total: 13
status: issues_found
---

# Phase 33: Code Review Report

**Reviewed:** 2026-10-29
**Depth:** standard
**Files Reviewed:** 33
**Status:** issues_found

## Summary

This file carries two reviews. The first (2026-10-28) covered the phase diff `6800769..HEAD`: the shaft's API routes,
CLI group, web part switch, the as-written number rule (L49), the end-face read-back guard, the bench scenarios and the
docs. Its findings WR-01, WR-02 and IN-01..IN-06 are carried forward below unchanged in substance and marked
**(prior)**. Line numbers in prior findings are as of that review; in `app.js` every line after 78 is now one higher.

The second review (2026-10-29, incremental) covers the 33-10 gap-closure commits `6632e7a`, `a090389` and `d7f642d`
(`git diff 2369167 HEAD` over `app.js`, `style.css` and `test_browser.py`): the `body[data-refused]` look, the 820 px
`display: contents` reorder, the dark `--accent-fg`, and the steps `narrow layout` and `primary button contrast`. Its
findings WR-03, WR-04 and IN-07..IN-09 are marked **(new)**. I read the three diffs against the full `app.js`,
`style.css`, `index.html` and the `writes_a_field_shut` guard in `tests/test_api.py`. I did not run the browser test or
`make verify`; I confirmed by arithmetic that `_contrast(white, black)` is exactly `21.0` in floating point, so the formula
test's `==` is sound.

What holds up in 33-10: the attribute is written in exactly the three places `refused` is assigned (`app.js:198-199`,
`:261-262`, `:277-278`), `refuse()` and `gearQuery()` are untouched, `index.html` is untouched, the aside's only children
are the switch, the form and the actions (so the `margin-inline` replacement for its padding misses nothing), and the
CSS specificity of the narrow margin rules beats `fieldset { margin: .75rem 0 0 }`. The contrast arithmetic and the
`_rgb` fail-loud parse are correct. No blocker found. The new defects are a stranded dimmed form when the refusal's own
build fails (WR-03) and a look that tells keyboard and assistive-tech users nothing (WR-04).

## Warnings

### WR-03: A refusal whose gear build fails leaves a dimmed, unresponsive form of the old part with a message about something else (new)

**File:** `src/spur/static/app.js:259-263` (`refuseLink`), `:276-288` (`followHash`'s `catch`)
**Issue:** `refuseLink` sets `refused` and `body[data-refused]` (lines 261-262) before `await buildForm('gear')`. If that
build throws (schema fetch fails or answers non-2xx), `followHash`'s `catch` shows "Could not build the form: ..." and
nothing else. `refused` and the attribute are still set, and `buildForm` threw before it emptied anything, so the page
still holds the previous part's form (the shaft form after `#part=shaft` then `#part=bogus`, or nothing at bootstrap).
Three things then disagree:
1. The form and Reset are dimmed with `pointer-events: none` and the switch is outlined, though the page never showed
   the refusal message that the outline points at.
2. The old part's radio is still checked (`markPart` is not called on this path), so the already-checked radio's click
   fires no `change`. The only ways out are the other radio or a reload.
3. A keystroke in the old form runs `update()`, which answers with the refusal text ("Unknown part ... use the Gear or
   Shaft switch") over a form that is not the gear's. That text replaces the build error the user needs.
Before 33-10 this state was invisible; the new look makes the page lie about being refused, and the plan's threat
T-33-26 ("the attribute and the variable move together") is met for the assignments but not for this failure exit.
**Fix:** In the `catch`, clear the refusal the failed build never completed:
```js
  } catch (err) {
    refused = null;
    delete document.body.dataset.refused;
    showMessages([`Could not build the form: ${err.message}`]);
    markPart();
  }
```
(the `markPart()` also makes the radios follow the page, as `switchTo`'s catch already does). Add a browser step that
routes `api/schema` to a 500 for one `#part=bogus` link and asserts `LIVE_LOOK` and the build-error message.

### WR-04: The refused look is visual only; the form stays focusable, typable and announced as live (new)

**File:** `src/spur/static/style.css:221-223`, `src/spur/static/app.js:262`
**Issue:** `opacity: .45; pointer-events: none` removes the form from the mouse and nothing else. A keyboard user tabs
into every field of a form that looks disabled, types, and sees no result except the refusal text re-announced on each
keystroke (`update()` line 425). A screen-reader user gets no signal at all that the form is out of action: no
`aria-disabled`, no description, and the outlined switch is a colour/shape cue only. The CSS comment records that this is a
deliberate trade against the L41 guard, which is fair, but the guard's regex (`tests/test_api.py:384`) forbids
`disabled`, `hidden`, `readonly`, `inert` and style writes, and does not forbid `aria-disabled` or `aria-describedby`.
The result is a control that is "disabled" for sighted mouse users only.
**Fix:** In `refuseLink` set `form.setAttribute('aria-disabled', 'true')` and `aria-describedby="messages"` on the form
(or on each group's fieldset), and remove them beside `delete document.body.dataset.refused`. Neither matches the
guard, and the existing `to_have_text` assertions on `#messages` still hold. If that is judged out of scope for the
phase, file it in `docs/tech_debt/active/` as `must`; CLAUDE.md asks for deferred risk to survive in a file.

### WR-01: A `buildForm` that throws after it has emptied the page leaves `part` pointing at the old part (prior)

**File:** `src/spur/static/app.js:92-187` (clear at 98-114, `part = which` at 175), `:197-211`, `:276-288`
**Issue:** `buildForm` empties the form, `fields`, `defaults`, `selectors`, the scene and the downloads before it builds the
new controls, and sets `part = which` only at the end. Anything that throws between the two leaves the page empty or half
built while `part` still names the old part. Examples are a `schema` without `properties`, which makes `Object.entries`
throw, and `buildSelectors` throwing "names the group ... which no field has". The catch blocks in `switchTo` and
`followHash` then show "Could not build the form" and `switchTo` calls `markPart()`, which re-checks the old part's radio
over a blank form. The next hashchange that names the old part takes the `which === part` branch in `followHash`. That
branch skips the rebuild and runs `readHash()` and `update()` against an empty `fields` map. A radio click on the
already-checked radio fires no `change`, so the user has no way to rebuild without a reload. A stale build that rejects
also writes its error over a newer build's page, because the stale check runs only after a successful fetch. The failure
needs a malformed schema, so it is unlikely today, but the page lies about which part it holds, which is the failure
L05 guards against.
**Fix:** Put `part = ''` immediately after the clear block, so any failure after the point of no return makes the next
link or switch rebuild, and let `markPart()` uncheck both radios in that state:
```js
  if (build !== formSeq) return false;
  part = '';          // the page holds no part until the build below finishes
  form.replaceChildren();
```
Alternatively, build into a detached `DocumentFragment` and swap it in as the last step. In the `catch` blocks, ignore
an error when `build !== formSeq`.

### WR-02: The shaft's three route rows are cut off from the endpoint table in `http-api.md` (prior)

**File:** `docs/architecture/http-api.md:45-48`
**Issue:** The new `GET /api/shaft/schema`, `/api/shaft/info` and `/api/shaft/model.{stl,step}` rows sit after a blank
line that follows the gear rows. In Markdown a blank line ends the table, and these rows have no header or separator
row of their own. The three routes therefore render as raw `| ... |` text in a paragraph and not as table rows. This is
the architecture reference for the API's public surface, and the shaft's frozen download name is documented only in these
lines.
**Fix:** Delete the blank line at line 45 so the rows continue the `Endpoint | Returns` table.

## Info

### IN-07: The refused-look checks leave three reachable states unasserted (new)

**File:** `tests/test_browser.py:2665-2729` (step `bad part refused`), `:2905-2983`
**Issue:** (a) `DEAD_LOOK` is asserted after each bad link loaded from the gear and once more after `part=shaft&part=gear`,
but not after the second refusal, `part=bogus` reached from the shaft (line 2714-2717), which is the path that rebuilds
the gear form over a built shaft. (b) The look is never read at the narrow size, so the combination `aside { display:
contents }` plus `body[data-refused] .part-switch` outline (offset 4 px, inside a `margin-inline` of 1 rem) is untested.
(c) `narrow layout` measures only 800 px; the breakpoint is 820 px, and a regression that moves the media query to
`max-width: 800px` would still pass.
**Fix:** Add `assert eval_str_list(page, REFUSED_LOOK) == DEAD_LOOK` after line 2717. Run the 820 px check at 820 and at
821 (the desktop columns must return at 821). Optionally read `REFUSED_LOOK` once inside `narrow layout`.

### IN-08: `aside { display: contents }` rests on one engine's behaviour, and the focus order no longer follows the visual order (new)

**File:** `src/spur/static/style.css:225-242`
**Issue:** The comment, the plan and the test establish only that the headless Chromium 153 shell keeps the `complementary`
role under `display: contents`. Other engines have shipped, and may still ship, accessibility-tree bugs for
`display: contents` on landmark elements; the gate cannot see that. Also, under 820 px the tab order stays the DOM
order (switch, form, actions, canvas Fit, downloads) while the visual order is switch, canvas, downloads, results, form.
`#view { order: -1 }` already did this before 33-10, so the gap is not new, but the reorder now moves the whole results
block above the form and widens it (WCAG 2.4.3).
**Fix:** Record in `docs/architecture/web-ui.md` that the landmark is verified on Chromium only and the focus order differs
from the visual order under 820 px, or file the same in `docs/tech_debt/active/`.

### IN-09: The L41 guard checks only `app.js`; the CSS route around it is guarded by a comment (new)

**File:** `src/spur/static/style.css:211-223`, `tests/test_api.py:384-426`
**Issue:** `writes_a_field_shut` stops a script from shutting a field, and 33-10 achieves the same effect (form takes no
pointer input) from CSS on a body attribute. The comment correctly argues that nothing a link loads is in the form while
refused. But the argument lives only in a comment: a later change that sets `data-refused` anywhere else, or loads link
values into the form while `refused` stands, would silently break L41 with every test green. `dataset.refused` is
counted by the plan's one-off grep, not by a test.
**Fix:** Add an assertion in `tests/test_api.py` that `dataset.refused` appears exactly three times in `app.js`, once as
an assignment and twice as a `delete`, so the T-33-26 mitigation is pinned by the suite and not by a plan's verify
command.

### IN-01: "No blanked token builds a part" is not true for int fields: pydantic reads `0-<digits>` as a negative number (prior)

**File:** `src/spur/app.py:274-292` (`blank_in_a_number_box`), `tests/number_box_tokens.py`
**Issue:** The docstring and L49 say none of the 32 tokens left to pydantic can build under a blank box. I fuzzed
against the gate's Chromium and found a counter-example. For an `int` field pydantic parses `0-0`, `0-9` and `00-9`
as `0`, `-9` and `-9`, while Chromium blanks all of them. For `spoke_count`, whose range starts at 0, `?spoke_count=0-0`
(also `00-0`) answers 200 and builds, and the box shows blank. It is harmless today only because that field's default is
also 0, so the part is the same one the blank box implies. The invariant holds by coincidence of defaults, not by the rule,
and the committed table has no such row, so the walker test cannot see it. The floats are unaffected.
**Fix:** Add `Token("0-0", True)` and `Token("0-9", True)` to `tests/number_box_tokens.py`, so the browser step records
Chromium's side. Either add `"-" in token[1:]` to the rule, which flags an interior minus that no valid number has outside
an exponent and so needs an `e` guard, or note the coincidence beside the docstring's claim.

### IN-02: The refused-token suggestion guesses for a token that is not a number (`+-5` becomes "write it as -5") (prior)

**File:** `src/spur/app.py:308-321` (`_as_written_message`)
**Issue:** The suggestion strips one leading `+` and one trailing `.` and then offers whatever is left if it is a plain
number. For `"+-5"` that is `-5`. I confirmed `teeth=%2B-5` answers `"+-5" is not a number as written; write it as -5`.
Nobody knows that `-5` is what was meant, which is the "plausible guess" that CODING_VALUES warns against. `-5` is
out of every field's range anyway, so the advice leads to a second 422.
**Fix:** Offer a canonical form only when the stripped token held a lone `+` or `.` and no sign remains, for example
`if not _PLAIN_NUMBER.fullmatch(core) or (token.lstrip().startswith("+") and core.startswith("-"))`.

### IN-03: Cache- and queue-sharing API tests depend on parameters no other test uses (prior)

**File:** `tests/test_api.py:1060-1096` (`test_a_saturated_service_refuses_a_shaft`), `:1213-1237`
(`test_a_designation_and_its_fields_share_one_cached_shaft`)
**Issue:** Both tests use the real module-level export cache. The first docstring says it needs "a shaft no other test
downloads". The second asserts `calls == 1`, which fails as `calls == 0` if any other test in the same worker has
already put the preview of `W 30x2x14x8f` with default solid fields in `_EXPORTS`. The sibling files avoid this by
monkeypatching `_EXPORTS`. The tests are green today and fail only after an unrelated test is added, and the failure
would be hard to trace.
**Fix:** Give both tests the `monkeypatch.setattr(app_module, "_EXPORTS", app_module._BlobCache(1 << 20))` fixture the
other shaft files use, and drop the "unique `splined_length`" trick.

### IN-04: `_js_fmt` in the browser test rounds half-even where `fmt()` rounds half-up, and it duplicates `displayed()` (prior)

**File:** `tests/test_browser.py` (`_js_fmt`, now line 285), `tests/shaft_parity.py:displayed`
**Issue:** `_js_fmt` uses Python's `f"{value:.3f}"`, which rounds an exact binary tie to even (`0.0625` becomes `0.062`).
JavaScript's `toFixed` rounds it half up (`0.063`). The phase wrote `displayed()` for this reason and checks it against
the browser, but the `part switch` step still builds its expected rows with the weaker `_js_fmt`. The default shaft has
no tie, so the step passes. A future default or sweep value on a tie would give a false failure in the step that runs
first and stops the walk.
**Fix:** Replace `_js_fmt` by `shaft_parity.displayed` in the `part switch` step, as `web_rows` already does.

### IN-05: The CLI's top-level description and `slug()` precision are stale or narrow after the shaft (prior)

**File:** `src/spur/cli.py:186`, `src/spur/shaft_params.py:114-125`
**Issue:** (a) `spur --help` still says "Parametric involute spur gears." although the CLI now has a `shaft` group.
(b) `slug()` formats `reference_d` and `module` with `:g`, which keeps six significant digits. `reference_d=123.4567`
and `123.4571` both name the file `..._w123.457x...`, and `25.00004` names it `w25`. The name is documented as frozen
(L49, D-17) and the fit and solid fields are already left out on purpose. The precision loss is a second collision
source that is not recorded anywhere, and it cannot be fixed later without superseding L49.
**Fix:** (a) Change the description to "Parametric spur gears and DIN 5480 splined shafts." (b) Either record the 6-digit
rounding next to the "frozen" note in `slug()`, or decide now whether the name should use `repr`-exact numbers.

### IN-06: A repeated `designation` key is read as its last value, and no test pins it (prior)

**File:** `src/spur/app.py:371` (`_shaft`), `tests/test_shaft_interfaces.py`
**Issue:** This is the behaviour the task marks as accepted. I confirmed that
`?designation=a&designation=W%2030x2x14x8f` answers 200 for the second value. No test pins it, so a pydantic or FastAPI
upgrade that reads the first value, or refuses the repeat, would change which shaft a published link builds, with no signal.
Note the asymmetry: for number keys the as-written rule inspects every repeat, but `_designation_conflict` and
`designation` do not.
**Fix:** Add one test in `tests/test_shaft_interfaces.py` that sends `designation=nonsense&designation=W 30x2x14x8f` and
asserts 200 with `designation == "W 30x2x14x8f"`.

---

_Reviewed: 2026-10-29_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
