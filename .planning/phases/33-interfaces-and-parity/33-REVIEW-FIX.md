---
phase: 33-interfaces-and-parity
fixed_at: 2026-10-29T00:00:00Z
review_path: .planning/phases/33-interfaces-and-parity/33-REVIEW.md
iteration: 1
findings_in_scope: 4
fixed: 4
skipped: 0
status: all_fixed
---

# Phase 33: Code Review Fix Report

**Fixed at:** 2026-10-29
**Source review:** .planning/phases/33-interfaces-and-parity/33-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 4
- Fixed: 4
- Skipped: 0

**Verification:** `make verify` ran in the main checkout (`workflow.use_worktrees` is `false`, so no
worktree was created). Result line: `======================= 2779 passed in 244.76s (0:04:04) =======================`
(exit 0; ruff, mypy --strict, import contracts, unfinished-work scan and pytest).

## Fixed Issues

### WR-03: A refusal whose gear build fails leaves a dimmed, unresponsive form of the old part

**Files modified:** `src/spur/static/app.js`, `tests/test_browser.py`
**Commit:** 13dcdfd
**Applied fix:** `followHash`'s `catch` now clears the refusal (`refused` and `body[data-refused]`) and calls
`markPart()`, as the review suggested. New browser step `refused link whose build fails` opens the shaft, routes
`**/api/schema` to a 500, follows `#part=bogus`, and asserts the build-error message, `LIVE_LOOK`, the shaft radio
still checked, and that a shaft keystroke builds and leaves no error. Watched the `LIVE_LOOK` assertion fail
(`0.45` against `1`) before the fix.
Status note: the clear is a logic fix; the browser step covers it, but it is the kind of change worth a human glance.

### WR-04: The refused look is visual only; the form stays focusable, typable and announced as live

**Files modified:** `src/spur/static/app.js`, `src/spur/static/style.css`, `docs/architecture/web-ui.md`, `tests/test_browser.py`
**Commit:** cace100
**Applied fix:** `refuseLink` now calls `markRefused()` after its gear build, which sets `aria-disabled="true"` and
`aria-describedby="messages"` on the form's fieldsets and on Reset. A new `clearRefusal()` replaces the three
`refused = null; delete dataset.refused` pairs and also removes the attributes. Placement differs from the review's
first suggestion (the `<form>`): the form has no accessible name so it has no role, and WAI-ARIA 1.2 supports
`aria-disabled` on `group` (the fieldsets) and `button` (Reset), not on it. Neither attribute matches the L41 guard
regex in `tests/test_api.py` (left untouched, and `tests/test_api.py` passes), and L41 in the decision log does not
mention `aria-disabled`. `REFUSED_LOOK`/`LIVE_LOOK`/`DEAD_LOOK` in the browser test now also read the attributes,
so every existing look assertion (and the WR-03 step) covers them; watched it fail before the fix. The step's
`page.fill` under a refusal needed `force=True`, because Playwright treats an `aria-disabled` group as not enabled
(which is the intended signal to assistive tech). The CSS comment and `web-ui.md` were updated to match.

### WR-01: A `buildForm` that throws after it has emptied the page leaves `part` pointing at the old part

**Files modified:** `src/spur/static/app.js`, `tests/test_browser.py`
**Commit:** 6f4dc28
**Applied fix:** `part = ''` immediately after the stale check and before `form.replaceChildren()`, with a comment
saying why. `markPart()` already unchecks both radios for `''`. New browser step `form build that throws midway`
makes the shaft schema `{}`, clicks the shaft radio, and asserts the error, an empty form, neither radio checked, and
that a following `#teeth=24` link rebuilds the gear form with 24 teeth. Watched it fail before the fix (gear radio
checked over a blank form). The review's alternative (ignore a stale build's error in the catch blocks) was not
taken; the stale-error half of the finding remains open.
Status note: logic fix, covered by the browser step; worth a human glance.

### WR-02: The shaft's three route rows are cut off from the endpoint table in `http-api.md`

**Files modified:** `docs/architecture/http-api.md`
**Commit:** dfba6f4
**Applied fix:** deleted the blank line between the gear's last row and the shaft rows so they continue the
`Endpoint | Returns` table. No test (documentation only).

---

_Fixed: 2026-10-29_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
