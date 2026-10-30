---
phase: 33-interfaces-and-parity
fixed_at: 2026-10-29T00:00:00Z
review_path: .planning/phases/33-interfaces-and-parity/33-REVIEW.md
iteration: 1
findings_in_scope: 13
fixed: 13
skipped: 0
status: all_fixed
---

# Phase 33: Code Review Fix Report

**Fixed at:** 2026-10-29
**Source review:** .planning/phases/33-interfaces-and-parity/33-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 13
- Fixed: 13
- Skipped: 0

**Verification:** `make verify` ran in the main checkout (`workflow.use_worktrees` is `false`, so no
worktree was created). Result line: `======================= 2783 passed in 348.19s (0:05:48) =======================`
(exit 0; ruff, mypy --strict, import contracts, unfinished-work scan and pytest, which includes the
browser test). Each commit also passed the commit-time `make verify.fast`.

## Fixed Issues

### WR-01: A stale `buildForm` that rejects writes its error, and clears the refusal, over a newer build's page (prior)

**Files modified:** `src/spur/static/app.js`, `tests/test_browser.py`
**Commit:** 1d3c2ce
**Applied fix:** `buildForm` wraps the schema fetch, status check and `res.json()` in a `try`; its `catch` returns
`false` when `build !== formSeq` and rethrows otherwise, as the review suggested. New browser step
`superseded build that fails` holds the shaft schema's answer, follows `part=bogus`, releases the answer as a 500
and asserts the refusal text, `DEAD_LOOK` and that a keystroke builds nothing and keeps the hash. Watched it fail
before the fix (the build error replaced the refusal text).
Status note: the change is a logic fix covered by a browser step, so it is worth a human glance.

### WR-05: After a build that threw midway the page holds no part, but `update()` still builds one (new)

**Files modified:** `src/spur/static/app.js`, `tests/test_browser.py`
**Commit:** b0de2ba
**Applied fix:** `update()` returns first thing when `part` is empty, with a comment saying why. The step
`form build that throws midway` now presses Reset and types in `#mate-teeth` after the error, waits
`DEBOUNCE_SETTLE_MS`, and asserts no build request, no result rows, no download `href` and no `data-triangles`.
Watched it fail before the fix (four build requests).
Status note: logic fix, covered by the browser step.

### IN-07: The refused-look checks leave three reachable states unasserted (new)

**Files modified:** `tests/test_browser.py`
**Commit:** c4a1ba2
**Applied fix:** (a) `DEAD_LOOK` is asserted after the refusal reached from the shaft. (b) `narrow layout` follows
`part=bogus` at 800 px, asserts `DEAD_LOOK`, then follows `part=shaft` and asserts `LIVE_LOOK` and the shaft's
download so `primary button contrast` still reads a live shaft. (c) The layout is also checked at 820 px (stacked)
and 821 px (desktop columns). Non-vacuity: with the media query moved to `max-width: 800px` the 820 px check fails
(`assert (60.8 + 42.8) <= 44.8`); the stylesheet was restored by `git checkout`. Also reworded a stale "Last in the
walk" comment in that step.

### IN-08: `aside { display: contents }` rests on one engine's behaviour, and the focus order no longer follows the visual order (new)

**Files modified:** `docs/architecture/web-ui.md`
**Commit:** 8359ec0
**Applied fix:** The review's own fix, the doc half: `web-ui.md` now records that the landmark is verified on the
headless Chromium shell only and that under 820 px the tab order is the markup order while the picture is
reordered (WCAG 2.4.3). The engine behaviour itself is outside this codebase and no code was added for it; if
cross-engine verification or a focus-order change is wanted it needs its own item.

### IN-09: The L41 guard checks only `app.js`; the CSS route around it is guarded by a comment (new)

**Files modified:** `tests/test_api.py`
**Commit:** 2e7653c
**Applied fix:** The existing `app.js` guard test now also asserts that `dataset.refused` has exactly one setter
and one `delete`, no other occurrence, and that `markRefused(` appears twice (definition and one call). The L41
regex and its probes are untouched. Non-vacuity: a second setter appended to `app.js` failed the new assertion; the
file was restored by `git checkout`.

### IN-10: `force=True` on the refused-state fill removes the proof that the field takes typing

**Files modified:** `tests/test_browser.py`
**Commit:** 57927e2
**Applied fix:** After the forced fill the step asserts `input[name=teeth]` holds `30`. The assertion passes on
current code (it guards a future `readonly` or `disabled`), so there is no red run.

### IN-11: `web-ui.md` does not describe the two new browser steps, and calls `narrow layout` the last step

**Files modified:** `docs/architecture/web-ui.md`
**Commit:** 31a390a
**Applied fix:** One paragraph names the three failed-build steps (`refused link whose build fails`, `superseded
build that fails`, `form build that throws midway`) and what each leaves on the page. "The last step" became "The
step", the 820/821 px checks and the narrow refused look are described, and `primary button contrast` is
mentioned as running after it.

### IN-01: "No blanked token builds a part" is not true for int fields: pydantic reads `0-<digits>` as a negative number (prior)

**Files modified:** `tests/number_box_tokens.py`, `tests/test_number_as_written.py`, `src/spur/app.py`
**Commit:** 8e913c4
**Applied fix:** The review's table-and-note option. `0-0`, `0-9` and `00-9` join the token table as blanked, so the
browser step re-reads Chromium's side at every gate run; it passes, so Chromium blanks all three. The
`blank_in_a_number_box` docstring now names the exception (`0-0` reads as 0, which `spoke_count` and `hole_count`
accept and default to) instead of claiming none exists. A new test fails when any int field of the gear or shaft
query models reads `0-0`, `00-0`, `0-9` or `00-9` as anything but its default. The rule keeps its four conditions:
adding an interior-minus condition would change the rule L49 locks, so that half was not done (see debt below).
The new test passes on current code, so there is no red run.

### IN-02: The refused-token suggestion guesses for a token that is not a number (`+-5` becomes "write it as -5") (prior)

**Files modified:** `src/spur/app.py`, `tests/test_number_as_written.py`
**Commit:** dd28628
**Applied fix:** `_as_written_message` offers the generic "a plain number, e.g. 22 or 2.5" sentence when the token
starts with `+` and the remainder starts with `-`. The other suggestions are unchanged. A new parametrised case in
the message test failed before the change (`write it as -5`).

### IN-03: Cache- and queue-sharing API tests depend on parameters no other test uses (prior)

**Files modified:** `tests/test_api.py`
**Commit:** 5244c5a
**Applied fix:** Both tests use the existing `fresh_exports` fixture; the saturated-service test drops its unique
`splined_length` and its docstring is updated. The fragility is latent (no current test fills either cache entry),
so there is no red run to show.

### IN-04: `_js_fmt` in the browser test rounds half-even where `fmt()` rounds half-up, and it duplicates `displayed()` (prior)

**Files modified:** `tests/test_browser.py`
**Commit:** f4a8514
**Applied fix:** The `part switch` step builds its expected rows with `shaft_parity.displayed`, and `_js_fmt` is
removed. The default shaft has no tie, so the step passed before and after.

### IN-05: The CLI's top-level description and `slug()` precision are stale or narrow after the shaft (prior)

**Files modified:** `src/spur/cli.py`, `src/spur/shaft_params.py`, `tests/test_cli.py`
**Commit:** 9612559
**Applied fix:** (a) The top-level description is "Parametric spur gears and DIN 5480 splined shafts.", with a test on
`spur --help` that failed before. (b) `slug()`'s output is unchanged (L49, D-17 freeze it); its docstring records the
six-significant-digit rounding of `:g` beside the freeze, with the two collision examples. Whether the name should
become repr-exact is left as a decision (see debt below).

### IN-06: A repeated `designation` key is read as its last value, and no test pins it (prior)

**Files modified:** `tests/test_shaft_interfaces.py`
**Commit:** 2b74594
**Applied fix:** New test sends `designation=nonsense&designation=W 30x2x14x8f` to `/api/shaft/info` and asserts 200
with the canonical designation. It records existing behaviour, so there is no red run.

## Skipped Issues

None — all findings were fixed.

---

_Fixed: 2026-10-29_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
