---
phase: 23-conditional-form-fields
reviewed: 2026-10-12T12:00:00Z
depth: standard
files_reviewed: 8
files_reviewed_list:
  - docs/architecture/decision_log.md
  - docs/ideas/2026-09-27-bore-shape-selector-in-the-web-form.md
  - docs/ideas/INDEX.md
  - docs/tech_debt/active/2026-10-11-hex-bore-warns-about-default-bore-fields.md
  - src/spur/static/app.js
  - tests/browser_session.py
  - tests/test_browser.py
  - tests/test_relations.py
findings:
  critical: 0
  warning: 0
  info: 2
  total: 2
status: issues_found
---

# Phase 23: Code Review Report

**Reviewed:** 2026-10-12
**Depth:** standard (incremental re-review, `c9e4af5..HEAD`, the eight files above)
**Files Reviewed:** 8
**Status:** issues_found

## Summary

This pass re-reviews the nine fix commits `8a16990`, `4f9b87b`, `6889ea4`, `10049f2`, `f0bcbc5`, `efded46`, `1ff2f17`, `247d09e` and `702d6ba`. I read `23-REVIEW.md` (at `c9e4af5`) and `23-REVIEW-FIX.md`, then checked each fix against the source.

**Verified fixed and dropped: IN-01, IN-02, IN-03, IN-04, IN-05, IN-06, IN-07, IN-09, IN-10.**
**Carried forward, narrowed: IN-08.** One new Info, IN-11, comes from the `_js_number` probe.

`git diff --stat c9e4af5 HEAD -- src/spur/calc.py src/spur/params.py src/spur/static/style.css tests/regression/` is empty, so those four stay byte-identical.

I ran `pytest tests/test_relations.py` (56 passed) and `pytest tests/test_browser.py tests/test_api.py` (64 passed, 30 s). I did not run `make verify`. No critical or warning finding. Details per ID:

- **IN-01, `_js_number`.** I compared it with node `String(x)` over 0, 1, 0.05, 1e6, 1e-6, 1e16, 100, 0.0025, 0.1+0.2, negatives and large integers below 1e21. It matches for all of them. It diverges outside the stated range (see IN-11). The three declared threshold shapes (0, 0.05, 1) are well inside it.
- **IN-06, `setdefault` plus blank-as-default.** It matches `URLSearchParams.get` first-wins. A blank first value stays present (`keep_blank_values`) and `given.get(name) or default` turns it into the default. This is the same as `readHash`'s `h.get(name) ?? defaults[name]` followed by `effective()`'s `'' -> default`. A bare key with no `=` reads as blank on both sides. The new no-browser test pins first-wins, the blank case and the number text.
- **IN-02, `aria-hidden` on `.reason`.** The code comment is correct. The accessible-name algorithm (accname 1.2, step 2A) skips a hidden node during recursion, except a node directly referenced by `aria-describedby` or `aria-labelledby`. So the reason leaves the label-derived name and stays the description. The `tests/test_api.py` pins `input.setAttribute('aria-describedby', reason.id)` and the `reason.textContent = off ?` snippet are intact (that module passes). The browser step asserts that every reason carries the attribute and that exactly the dimmed inputs carry `aria-describedby`. That proves the attribute, not the announcement, and the fix report says so honestly.
- **IN-07 and IN-10.** The assertions check what their comments claim. The invalid set is compared in full with the server's named set. The pair is derived from `REFUSED_LINK` minus the gates, with its size asserted. The post-keystroke step now compares the row text and the other fields' dim set.
- **IN-03, IN-04 and IN-05.** The `warning rendered` step exists (`test_browser.py:449`). The `(superseded by L41)` annotations match L41's own title and its line 2573. L41's past tense reads cleanly. There is no leftover "this commit" or "goes red" in the entry.
- **IN-09, L41 edit.** "Caught per field in `applyRelations()` and nowhere else" is accurate. `holds()`, `effective()` and `need()` are only reached from inside the `try`. "Stays undimmed with its own reason row" and "the other fields and the build are unaffected" match `app.js:158-170`.
- **IN-08, cutout states.** Both new states (`spokes (4)`, `holes (3)`) validate under `GearParams`. The control test counts 12 cells per dependent. The new meta-test fails on `wrong or extra driver`, and the `ValidationError` branch uses a different message, so `match=` cannot be satisfied by the masking error. This part of IN-08 is fixed. A residual is below.

No security issues. The reason text is still written with `textContent`.

## Info

### IN-08: The driver check cannot tell `hex_cell eq 0.05` from `hex_cell gt 0`; only the forward check's incidental `ValidationError` catches it

**File:** `tests/test_relations.py:231-250` (`CUTOUT_STATES`), `:262-275` (docstring)
**Issue:** The fix added a second open value for the two count gates (spokes 4, holes 3) but left the honeycomb gate with one open value, `hex_cell` 0.05. I ran `_assert_relations_name_the_driver_calc_obeys({"hex_wall": [("hex_cell", "eq", 0.05)]})`. It passes with 12 cells, the same `eq`-at-the-first-open-value blindness that IN-08 was filed for. On a real 4 mm cell that relation would dim `hex_wall`, a live value (L08). The forward check does turn red on it, but only through `ValidationError: A honeycomb needs hex_wall` on its `base = derive(...)` line (`hex_cell` 0.1 without `hex_wall`). That is the incidental catch the finding named. The new docstring sentence, "Each count gate is probed at two open values", is true for counts only and does not mention the cell. There is also no meta-test for the cell.
**Fix:** Add `"honeycomb (4)": {"hex_cell": 4, "hex_wall": 1}` to `CUTOUT_STATES`. It validates (`hex_cell` 4, `hex_wall` 1 builds a `GearParams`). Raise the `len(CUTOUT_STATES) * len(BORE_STATES)` count to 14, and add `("hex_wall", "hex_cell")` to the parametrised meta-test (with value 0.05 for `eq`). Reword the docstring to "each gate".

### IN-11: `_js_number` returns a string JavaScript would not write for -0.0 and outside 1e-6 <= |x| < 1e21, and nothing guards the range

**File:** `tests/browser_session.py:312-320`
**Issue:** The docstring states the exact range, which is honest, but the function accepts any float. I probed it against node. `-0.0` gives `-0` where JS `String(-0)` is `0`. `1e21` gives `1000000000000000000000` where JS writes `1e+21`. `1e-7` gives `0.0000001` where JS writes `1e-7`. No declared threshold is near any of these (the values are 0, 0.05 and 1), and a future one that was would fail with a reason-text mismatch in the browser step, not pass silently. So the cost is a confusing failure message, not a wrong pass. The unit test pins the in-range pairs only.
**Fix:** Make the stated range a check, so a threshold outside it fails with its own name:
```python
number = float(value)
assert number == 0 or 1e-6 <= abs(number) < 1e21, f"{value!r}: JavaScript writes this with an exponent"
return format(Decimal(repr(number)).normalize() + 0, "f")  # + 0 turns -0 into 0
```

---

_Reviewed: 2026-10-12_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
