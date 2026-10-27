---
phase: 33-interfaces-and-parity
reviewed: 2026-10-28T00:00:00Z
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
  warning: 2
  info: 6
  total: 8
status: issues_found
---

# Phase 33: Code Review Report

**Reviewed:** 2026-10-28
**Depth:** standard
**Files Reviewed:** 33
**Status:** issues_found

## Summary

Reviewed the phase diff (`6800769..HEAD`) for the shaft's API routes, CLI group, web part switch, the
as-written number rule (L49), the end-face read-back guard, the bench scenarios and the docs. I read the
source in full and probed it rather than trusting the tests:

- Ran the light shaft/number/parity/seam tests (188 passed), the shaft model and CLI shaft tests (61 passed),
  `ruff check` (clean) and `mypy --strict src` (clean). I did not run the browser test or `make verify`.
- Probed `/api/shaft/info` with 20+ designation, conflict, number and fit cases. Every refusal is a 422 with the
  documented `loc` and `type`; none was a 500. The conflict check does run before value parsing.
- Fuzzed `blank_in_a_number_box` against the gate's own Chromium (49,304 tokens over an alphabet of digits,
  signs, `.`, `e`, `_`, whitespace and Unicode spaces) and against pydantic's lax float/int parse. No token that
  Chromium blanks is accepted as a float unflagged, and no token Chromium holds is refused. One int-only escape
  exists (IN-01). The 91-token table counts (66 blank, 25 held, 34 refused by the rule) match the decision log.
- Built 70 random honest shafts (tiny and capped chamfers, odd and even counts, shank on and off) through the
  new `_guard_volume` end-face check: 70 of 70 built, so the new guard refuses no honest part I could find.
- Checked every `cadquery` boundary, the sha references in the resolved debt items and the arithmetic in the
  decision log's gate-delta paragraph; all are consistent.

No blocker found. The remaining defects are one page-state hazard (WR-01), one documentation rendering defect
(WR-02) and six smaller items.

## Warnings

### WR-01: A `buildForm` that throws after it has emptied the page leaves `part` pointing at the old part

**File:** `src/spur/static/app.js:91-186` (clear at 97-113, `part = which` at 174), `:196-209`, `:273-284`
**Issue:** `buildForm` empties the form, `fields`, `defaults`, `selectors`, the scene and the downloads (lines
97-113) before it builds the new controls, and sets `part = which` only at line 174. Anything that throws between
the two leaves the page empty or half built while `part` still names the old part. Examples are a `schema` without
`properties`, which makes `Object.entries` throw, and `buildSelectors` throwing "names the group ... which no field
has". The catch blocks in `switchTo` and `followHash` then show "Could not build the form" and `switchTo` calls
`markPart()`, which re-checks the old part's radio over a blank form. The next hashchange that names the old part
takes the `which === part` branch in `followHash` (line 277). That branch skips the rebuild and runs `readHash()`
and `update()` against an empty `fields` map. A radio click on the already-checked radio fires no `change`, so the
user has no way to rebuild without a reload. A stale build that rejects also writes its error over a newer build's
page, because the stale check at line 96 runs only after a successful fetch. The failure needs a malformed schema,
so it is unlikely today, but the page lies about which part it holds, which is the failure L05 guards against.
**Fix:** Put `part = ''` immediately after the clear block, so any failure after the point of no return makes the next
link or switch rebuild, and let `markPart()` uncheck both radios in that state:
```js
  if (build !== formSeq) return false;
  part = '';          // the page holds no part until the build below finishes
  form.replaceChildren();
```
Alternatively, build into a detached `DocumentFragment` and swap it in as the last step. In the `catch` blocks, ignore
an error when `build !== formSeq`.

### WR-02: The shaft's three route rows are cut off from the endpoint table in `http-api.md`

**File:** `docs/architecture/http-api.md:45-48`
**Issue:** The new `GET /api/shaft/schema`, `/api/shaft/info` and `/api/shaft/model.{stl,step}` rows sit after a blank
line that follows the gear rows. In Markdown a blank line ends the table, and these rows have no header or separator
row of their own. The three routes therefore render as raw `| ... |` text in a paragraph and not as table rows. This is
the architecture reference for the API's public surface, and the shaft's frozen download name is documented only in these
lines.
**Fix:** Delete the blank line at line 45 so the rows continue the `Endpoint | Returns` table.

## Info

### IN-01: "No blanked token builds a part" is not true for int fields: pydantic reads `0-<digits>` as a negative number

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

### IN-02: The refused-token suggestion guesses for a token that is not a number (`+-5` becomes "write it as -5")

**File:** `src/spur/app.py:308-321` (`_as_written_message`)
**Issue:** The suggestion strips one leading `+` and one trailing `.` and then offers whatever is left if it is a plain
number. For `"+-5"` that is `-5`. I confirmed `teeth=%2B-5` answers `"+-5" is not a number as written; write it as -5`.
Nobody knows that `-5` is what was meant, which is the "plausible guess" that CODING_VALUES warns against. `-5` is
out of every field's range anyway, so the advice leads to a second 422.
**Fix:** Offer a canonical form only when the stripped token held a lone `+` or `.` and no sign remains, for example
`if not _PLAIN_NUMBER.fullmatch(core) or (token.lstrip().startswith("+") and core.startswith("-"))`.

### IN-03: Cache- and queue-sharing API tests depend on parameters no other test uses

**File:** `tests/test_api.py:1060-1096` (`test_a_saturated_service_refuses_a_shaft`), `:1213-1237`
(`test_a_designation_and_its_fields_share_one_cached_shaft`)
**Issue:** Both tests use the real module-level export cache. The first docstring says it needs "a shaft no other test
downloads". The second asserts `calls == 1`, which fails as `calls == 0` if any other test in the same worker has
already put the preview of `W 30x2x14x8f` with default solid fields in `_EXPORTS`. The sibling files avoid this by
monkeypatching `_EXPORTS`. The tests are green today and fail only after an unrelated test is added, and the failure
would be hard to trace.
**Fix:** Give both tests the `monkeypatch.setattr(app_module, "_EXPORTS", app_module._BlobCache(1 << 20))` fixture the
other shaft files use, and drop the "unique `splined_length`" trick.

### IN-04: `_js_fmt` in the browser test rounds half-even where `fmt()` rounds half-up, and it duplicates `displayed()`

**File:** `tests/test_browser.py` (`_js_fmt`, added line 273), `tests/shaft_parity.py:displayed`
**Issue:** `_js_fmt` uses Python's `f"{value:.3f}"`, which rounds an exact binary tie to even (`0.0625` becomes `0.062`).
JavaScript's `toFixed` rounds it half up (`0.063`). The phase wrote `displayed()` for this reason and checks it against
the browser, but the `part switch` step still builds its expected rows with the weaker `_js_fmt`. The default shaft has
no tie, so the step passes. A future default or sweep value on a tie would give a false failure in the step that runs
first and stops the walk.
**Fix:** Replace `_js_fmt` by `shaft_parity.displayed` in the `part switch` step, as `web_rows` already does.

### IN-05: The CLI's top-level description and `slug()` precision are stale or narrow after the shaft

**File:** `src/spur/cli.py:186`, `src/spur/shaft_params.py:114-125`
**Issue:** (a) `spur --help` still says "Parametric involute spur gears." although the CLI now has a `shaft` group.
(b) `slug()` formats `reference_d` and `module` with `:g`, which keeps six significant digits. `reference_d=123.4567`
and `123.4571` both name the file `..._w123.457x...`, and `25.00004` names it `w25`. The name is documented as frozen
(L49, D-17) and the fit and solid fields are already left out on purpose. The precision loss is a second collision
source that is not recorded anywhere, and it cannot be fixed later without superseding L49.
**Fix:** (a) Change the description to "Parametric spur gears and DIN 5480 splined shafts." (b) Either record the 6-digit
rounding next to the "frozen" note in `slug()`, or decide now whether the name should use `repr`-exact numbers.

### IN-06: A repeated `designation` key is read as its last value, and no test pins it

**File:** `src/spur/app.py:371` (`_shaft`), `tests/test_shaft_interfaces.py`
**Issue:** This is the behaviour the task marks as accepted. I confirmed that
`?designation=a&designation=W%2030x2x14x8f` answers 200 for the second value. No test pins it, so a pydantic or FastAPI
upgrade that reads the first value, or refuses the repeat, would change which shaft a published link builds, with no signal.
Note the asymmetry: for number keys the as-written rule inspects every repeat, but `_designation_conflict` and
`designation` do not.
**Fix:** Add one test in `tests/test_shaft_interfaces.py` that sends `designation=nonsense&designation=W 30x2x14x8f` and
asserts 200 with `designation == "W 30x2x14x8f"`.

---

_Reviewed: 2026-10-28_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
