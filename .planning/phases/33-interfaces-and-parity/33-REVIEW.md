---
phase: 33-interfaces-and-parity
reviewed: 2026-10-29T00:00:00Z
depth: standard
files_reviewed: 12
files_reviewed_list:
  - docs/architecture/http-api.md
  - docs/architecture/web-ui.md
  - src/spur/static/app.js
  - src/spur/static/style.css
  - tests/test_browser.py
  - src/spur/app.py
  - src/spur/cli.py
  - src/spur/shaft_params.py
  - tests/test_api.py
  - tests/number_box_tokens.py
  - tests/shaft_parity.py
  - tests/test_shaft_interfaces.py
findings:
  critical: 0
  warning: 2
  info: 11
  total: 13
status: issues_found
---

# Phase 33: Code Review Report

**Reviewed:** 2026-10-29
**Depth:** standard
**Files Reviewed:** 12
**Status:** issues_found

## Summary

Incremental re-review after the four fix commits 13dcdfd (WR-03), cace100 (WR-04), 6f4dc28 (WR-01) and dfba6f4 (WR-02).
I read `git diff 09aaa8c HEAD` over the five files in scope against the full `app.js`, `style.css`, the `Reset` and
`input` wiring, `index.html`'s `#messages`, and the `bad part refused` step. I did not run the browser test or
`make verify`; the browser claims below come from reading the code and its event order.

Verified fixed and dropped: WR-02 (the shaft rows are contiguous with the endpoint table), WR-03 (`followHash`'s
`catch` clears the refusal and re-syncs the radios; a `refuseLink` that throws never reaches `markRefused`, and
`clearRefusal` removes both the variable and the attribute), WR-04 (`markRefused` runs after the gear build, so it sees
the rebuilt fieldsets; `clearRefusal` runs before every build, so no stale `aria-disabled` survives a rebuild; the
attributes do not match the L41 guard regex and `.part-switch` is correctly left unmarked).

Partly fixed and kept: WR-01. The `part = ''` half works for the next link or switch, but the stale-error half is
open, and the WR-03 `clearRefusal()` in the `catch` makes it worse (it can now undo a newer link's refusal). The
`part = ''` sentinel also introduces a defect of its own (WR-05, `update()` does not honour it). IN-01..IN-09 are
re-checked against current code and still hold; `app.js` and `test_browser.py` line references moved. Two new Info
items (IN-10, IN-11) cover the test fix's `force=True` and the stale doc. No blocker found.

## Warnings

### WR-01: A stale `buildForm` that rejects writes its error, and clears the refusal, over a newer build's page (prior)

**File:** `src/spur/static/app.js:92-97` (the stale check), `:226-234` (`switchTo`'s `catch`), `:313-320` (`followHash`'s `catch`)
**Issue:** `buildForm` compares `build !== formSeq` only after `fetch` and `res.json()` have succeeded. A superseded build
whose fetch rejects (network error), whose status is not 2xx, or whose body is not JSON throws out of `buildForm`
unchecked, and the caller's `catch` runs for a build nobody is waiting for any more. Two consequences:
1. The `catch` shows "Could not build the form: ..." over whatever the newer build left (the newer build's own
   `showMessages()` has already run if it finished first), and `markPart()` re-points the radios at the old `part` while
   the newer build is still in flight.
2. Since 13dcdfd the `followHash` `catch` also calls `clearRefusal()`. Trace: link A (`#part=shaft`) is in flight and
   will fail; link B (`#part=bogus`) arrives, `refuseLink` sets `refused` and `body[data-refused]` and awaits its gear
   build; A's rejection lands and `clearRefusal()` wipes both; B's build then finishes, calls `markRefused()` and shows
   the refusal. The page now has unchecked radios, `aria-disabled` fieldsets and the refusal text, but `refused === null`
   and no `data-refused`, so it looks live, and the next keystroke runs `update()` and builds a gear under a link whose
   `part` is bad and rewrites the hash. That is the D-20 breach the refusal exists to prevent.
Neither case needs a malformed schema, only a failure that arrives out of order. The 6f4dc28 browser step does not cover
it, and its commit message records the stale half as open.
**Fix:** Make a superseded build silent in `buildForm` itself, so no caller needs to know:
```js
  const build = ++formSeq;
  let schema;
  try {
    const res = await fetch(PARTS[which].schema);
    if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
    schema = await res.json();
  } catch (err) {
    if (build !== formSeq) return false;   // overtaken: the newer build owns the page and the message
    throw err;
  }
  if (build !== formSeq) return false;
```
Add a browser step that routes `api/shaft/schema` to a delayed 500, follows `#part=shaft` then `#part=bogus`, and asserts
the refusal text, `DEAD_LOOK` and that a keystroke builds nothing.

### WR-05: After a build that threw midway the page holds no part, but `update()` still builds one (new)

**File:** `src/spur/static/app.js:102` (`part = ''`), `:457-459` (`update`), `:860-868` (`#reset`), `:850` (mate box)
**Issue:** 6f4dc28 makes `part === ''` mean "the page holds no part: blank form, neither radio checked". Nothing that can
still run in that state honours it. `#reset` and the mate-teeth box are outside the emptied form and stay live: Reset
loops over the now empty `fields`, then calls `update()`, which sees `refused === null`, builds an empty `gearQuery()`,
rewrites the hash to the bare path, fetches `P.info` and `P.model.stl` for the *old* `P` (still set, because `P = PARTS[which]`
runs last), draws that part's default solid and enables the downloads. The user gets a drawn default gear (or shaft)
with a blank form and no radio checked, which is the page lying about its state, and a number they would cut metal to
that no control produced (L08, L05). The same path exists at a failed bootstrap, but only the 6f4dc28 step makes it a
designed state. The new step never presses Reset or types a mate count, so it passes.
**Fix:** Guard on the sentinel at the top of `update()`:
```js
async function update() {
  if (!part) return;       // a build threw midway: there is no form to read, so nothing to build
  if (refused) { showMessages([refused]); return; }
```
`followHash` always builds before it calls `update()` and `switchTo` sets `part` first, so no live path is affected. Extend
the `form build that throws midway` step: after the error, press Reset and type in `#mate-teeth`, wait
`DEBOUNCE_SETTLE_MS`, assert `_build_requests(seen)` is unchanged, `#dims` is empty and `#dl-stl` has no `href`.

## Info

### IN-07: The refused-look checks leave three reachable states unasserted (new)

**File:** `tests/test_browser.py:2723-2731` (step `bad part refused`), `:2988-3031` (`narrow layout`)
**Issue:** (a) `DEAD_LOOK` is asserted after each bad link loaded from the gear (line 2676) and once after the keyboard
Reset (2702), but not after the second refusal, `part=bogus` reached from the shaft (2723-2731), which is the path that
rebuilds the gear form over a built shaft and then calls `markRefused()` on the new fieldsets. (b) The look is never read
at the narrow size, so `aside { display: contents }` plus the `body[data-refused] .part-switch` outline (offset 4 px,
inside a `margin-inline` of 1 rem) is untested. (c) `narrow layout` measures only 800 px; the breakpoint is 820 px
(`style.css:232`), and a regression that moves the media query to `max-width: 800px` would still pass.
**Fix:** Add `assert eval_str_list(page, REFUSED_LOOK) == DEAD_LOOK` after the `field_count` check at line 2727. Run the
820 px check at 820 and at 821 (the desktop columns must return at 821). Optionally read `REFUSED_LOOK` once inside
`narrow layout`.

### IN-08: `aside { display: contents }` rests on one engine's behaviour, and the focus order no longer follows the visual order (new)

**File:** `src/spur/static/style.css:225-243`
**Issue:** The comment, the plan and the test establish only that the headless Chromium 153 shell keeps the `complementary`
role under `display: contents`. Other engines have shipped, and may still ship, accessibility-tree bugs for
`display: contents` on landmark elements; the gate cannot see that. Also, under 820 px the tab order stays the DOM
order (switch, form, actions, canvas Fit, downloads) while the visual order is switch, canvas, downloads, results, form.
`#view { order: -1 }` already did this before 33-10, so the gap is not new, but the reorder now moves the whole results
block above the form and widens it (WCAG 2.4.3).
**Fix:** Record in `docs/architecture/web-ui.md` that the landmark is verified on Chromium only and the focus order differs
from the visual order under 820 px, or file the same in `docs/tech_debt/active/`.

### IN-09: The L41 guard checks only `app.js`; the CSS route around it is guarded by a comment (new)

**File:** `src/spur/static/style.css:211-223`, `src/spur/static/app.js:216-217` and `:289-290`, `tests/test_api.py:384-426`
**Issue:** `writes_a_field_shut` stops a script from shutting a field, and 33-10 achieves the same effect (form takes no
pointer input) from CSS on a body attribute. The comment correctly argues that nothing a link loads is in the form while
refused. But the argument lives only in a comment: a later change that sets `data-refused` anywhere else, or loads link
values into the form while `refused` stands, would silently break L41 with every test green. Since cace100 the attribute
is written at exactly two sites (`refuseLink` sets it, `clearRefusal` deletes it) and `markRefused()` has one caller;
none of that is pinned by a test.
**Fix:** Add an assertion in `tests/test_api.py` that `dataset.refused` appears exactly twice in `app.js`, once as an
assignment and once as a `delete`, and that `markRefused(` appears exactly twice (definition and one call), so the
T-33-26 mitigation is pinned by the suite and not by a plan's verify command.

### IN-10: `force=True` on the refused-state fill removes the proof that the field takes typing

**File:** `tests/test_browser.py:2685-2689`
**Issue:** The comment says a keyboard user "is not stopped", and the step exists to show that D-20 holds when they type.
Playwright's `force` skips the enabled and editable checks, so the fill no longer fails if a later change makes the
field `readonly` or `disabled` (the L41 guard stops a script doing that, not markup), and nothing then asserts that
`teeth` held `30` before Reset. The comment at 2693 says "teeth was 30 just before" but only the post-Reset
`eval_pairs(page) == default_pairs` is checked, and that passes whether or not the typing took.
**Fix:** After the fill add `assert page.locator("input[name=teeth]").input_value() == "30"`, or type with
`page.locator("input[name=teeth]").press_sequentially("30")` after `.focus()`, which needs no `force`.

### IN-11: `web-ui.md` does not describe the two new browser steps, and calls `narrow layout` the last step

**File:** `docs/architecture/web-ui.md:119-130`
**Issue:** The paragraph that lists the shaft-page steps names `part switch`, `shaft link round trip` and `bad part
refused`. 13dcdfd and 6f4dc28 added `refused link whose build fails` and `form build that throws midway` after them, and the
doc is silent about both. It also says "The last step, `narrow layout`", but `primary button contrast` runs after it
(`tests/test_browser.py:3033`) and is not mentioned. A reader of the reference learns neither what guards the failed-build
exits nor which step ends the walk.
**Fix:** Add one sentence naming the two steps and what each pins (a refusal whose gear build fails leaves the page live;
a build that throws midway leaves no part held and the next link rebuilds). Reword "The last step" to "Another step" and
mention `primary button contrast`.

### IN-01: "No blanked token builds a part" is not true for int fields: pydantic reads `0-<digits>` as a negative number (prior)

**File:** `src/spur/app.py:274-292` (`blank_in_a_number_box`), `tests/number_box_tokens.py`
**Issue:** The docstring and L49 say none of the 32 tokens left to pydantic can build under a blank box. I fuzzed
against the gate's Chromium and found a counter-example. For an `int` field pydantic parses `0-0`, `0-9` and `00-9`
as `0`, `-9` and `-9`, while Chromium blanks all of them. For `spoke_count`, whose range starts at 0, `?spoke_count=0-0`
(also `00-0`) answers 200 and builds, and the box shows blank. It is harmless today only because that field's default is
also 0, so the part is the same one the blank box implies. The invariant holds by coincidence of defaults, not by the rule,
and the committed table has no such row, so the walker test cannot see it. The floats are unaffected. Re-checked against
current code: `blank_in_a_number_box` is unchanged and the token table still has no `0-0` or `0-9` row.
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

**File:** `tests/test_api.py:1077-1094` (`test_a_saturated_service_refuses_a_shaft`), `:1213-1236`
(`test_a_designation_and_its_fields_share_one_cached_shaft`)
**Issue:** Both tests use the real module-level export cache. The first docstring says it needs "a shaft no other test
downloads". The second asserts `calls == 1`, which fails as `calls == 0` if any other test in the same worker has
already put the preview of `W 30x2x14x8f` with default solid fields in `_EXPORTS`. The sibling tests (for example the one
at line 1477) avoid this by monkeypatching `_EXPORTS`. The tests are green today and fail only after an unrelated test is
added, and the failure would be hard to trace.
**Fix:** Give both tests the `monkeypatch.setattr(app_module, "_EXPORTS", app_module._BlobCache(1 << 20))` fixture the
other shaft files use, and drop the "unique `splined_length`" trick.

### IN-04: `_js_fmt` in the browser test rounds half-even where `fmt()` rounds half-up, and it duplicates `displayed()` (prior)

**File:** `tests/test_browser.py:293` (`_js_fmt`, used at `:2467`), `tests/shaft_parity.py:displayed`
**Issue:** `_js_fmt` uses Python's `f"{value:.3f}"`, which rounds an exact binary tie to even (`0.0625` becomes `0.062`).
JavaScript's `toFixed` rounds it half up (`0.063`). The phase wrote `displayed()` for this reason and checks it against
the browser, but the `part switch` step still builds its expected rows with the weaker `_js_fmt`. The default shaft has
no tie, so the step passes. A future default or sweep value on a tie would give a false failure in the step that runs
first and stops the walk.
**Fix:** Replace `_js_fmt` by `shaft_parity.displayed` in the `part switch` step, as `web_rows` already does.

### IN-05: The CLI's top-level description and `slug()` precision are stale or narrow after the shaft (prior)

**File:** `src/spur/cli.py:186`, `src/spur/shaft_params.py:114-123`
**Issue:** (a) `spur --help` still says "Parametric involute spur gears." although the CLI now has a `shaft` group.
(b) `slug()` formats `reference_d` and `module` with `:g`, which keeps six significant digits. `reference_d=123.4567`
and `123.4571` both name the file `..._w123.457x...`, and `25.00004` names it `w25`. The name is documented as frozen
(L49, D-17) and the fit and solid fields are already left out on purpose. The precision loss is a second collision
source that is not recorded anywhere, and it cannot be fixed later without superseding L49.
**Fix:** (a) Change the description to "Parametric spur gears and DIN 5480 splined shafts." (b) Either record the 6-digit
rounding next to the "frozen" note in `slug()`, or decide now whether the name should use `repr`-exact numbers.

### IN-06: A repeated `designation` key is read as its last value, and no test pins it (prior)

**File:** `src/spur/app.py:357-371` (`_designation_conflict`, `_shaft`), `tests/test_shaft_interfaces.py`
**Issue:** This is the behaviour the task marks as accepted. I confirmed that
`?designation=a&designation=W%2030x2x14x8f` answers 200 for the second value. No test pins it (a grep of `tests/` finds
no request that repeats the key), so a pydantic or FastAPI upgrade that reads the first value, or refuses the repeat,
would change which shaft a published link builds, with no signal. Note the asymmetry: for number keys the as-written
rule inspects every repeat, but `_designation_conflict` and `designation` do not.
**Fix:** Add one test in `tests/test_shaft_interfaces.py` that sends `designation=nonsense&designation=W 30x2x14x8f` and
asserts 200 with `designation == "W 30x2x14x8f"`.

---

_Reviewed: 2026-10-29_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
