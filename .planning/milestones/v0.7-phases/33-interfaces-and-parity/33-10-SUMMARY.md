---
phase: 33-interfaces-and-parity
plan: 10
subsystem: ui
tags: [web, css, wcag, contrast, browser-test, gap-closure, G-33-2]

requires:
  - phase: 33-interfaces-and-parity
    provides: "33-06/07 the part switch, followHash and the refused state (D-15, D-20); 33-09 the close checks; 33-UI-REVIEW the three findings"
provides:
  - "a refused-part link leaves the form and Reset dimmed with no pointer input and the switch outlined (body[data-refused], CSS only)"
  - "under 820 px the Gear | Shaft switch is ordered above the canvas, still the first child of <aside> (D-12)"
  - "the dark theme's primary button text reads 4.85:1 (light 5.48:1, unchanged), measured in the browser"
  - "browser steps `narrow layout` and `primary button contrast`, and the `bad part refused` look checks"
  - "debt item: dark-mode link text 4.47:1"
affects: [phase-33-verification, verify-work, ui-review]

actuals:
  tokens: 6270   # chars/4 over the diff of src/, tests/, docs/ and bench/ (logs and pictures excluded)
  tasks: 3
  commits: 5
plan_head_before: 9db8a31d0faaf1069231da7e2fe980bc7ace26f2
plan_head_after: 41ec1ba8f6e44163e46fb524da2a063ade1f0044

tech-stack:
  added: []
  patterns:
    - "A look the script may not write (L41) is CSS on a body attribute set beside the state it mirrors (body[data-part], body[data-refused])"
    - "Order a first child of a container that must stay first in the markup with `display: contents` on the container and `order` on the child"
    - "A colour claim is read in the browser as computed style and ratioed with the WCAG 2 formula, the formula pinned by its own test"

key-files:
  created:
    - docs/tech_debt/active/2026-10-29-dark-mode-link-text-under-wcag-aa.md
    - .planning/phases/33-interfaces-and-parity/investigation/33-10-refused.png
    - .planning/phases/33-interfaces-and-parity/investigation/33-10-narrow.png
    - .planning/phases/33-interfaces-and-parity/investigation/33-10-dark-buttons.png
    - .planning/phases/33-interfaces-and-parity/investigation/33-10-verify.log
  modified:
    - src/spur/static/app.js
    - src/spur/static/style.css
    - tests/test_browser.py
    - docs/architecture/web-ui.md
    - bench/RESULTS.md
    - docs/tech_debt/INDEX.md

key-decisions:
  - "The review's `place the message by the switch` is met by outlining the switch while the refusal stands, under D-15; moving the message out of #messages would amend D-15 and is not done"
  - "The narrow order is CSS (`aside { display: contents; }` plus `order`), not a move of the switch out of <aside>, so D-12 stands and index.html is untouched"
  - "The refused look is CSS on body[data-refused], not `inert` or a script write, because the writes_a_field_shut guard refuses a script that shuts a control (L41) and D-20 rules out letting an edit end the refusal"
  - "The dark --accent stays #e0573f; only the dark --accent-fg is new (#131619, the theme's own --bg)"

requirements-completed: [REQ-shaft-web]

coverage:
  - id: D1
    description: "A refused-part link dims the form and Reset (opacity 0.45, pointer-events none) and outlines the switch; a radio click or a valid link restores the live look; edits and a keyboard Reset still build nothing"
    requirement: REQ-shaft-web
    verification:
      - kind: e2e
        ref: "tests/test_browser.py#test_the_shipped_viewer_in_a_real_browser (step bad part refused)"
        status: pass
    human_judgment: true
    rationale: "The computed look is asserted; whether the outline reads as attached to the switch is a visual call, read from 33-10-refused.png"
  - id: D2
    description: "At 800x900 the part switch is above the canvas, then the results, then the form; it is still the first child of <aside> with both radios inside the complementary landmark; the desktop column is unchanged"
    requirement: REQ-shaft-web
    verification:
      - kind: e2e
        ref: "tests/test_browser.py#test_the_shipped_viewer_in_a_real_browser (step narrow layout)"
        status: pass
    human_judgment: true
    rationale: "The box order is asserted; whether the narrow page reads like the desktop column on a phone is a visual call, read from 33-10-narrow.png"
  - id: D3
    description: "Dark-mode primary button text reads at least 4.5:1 (dark 4.85:1, light 5.48:1), measured in the browser, with the WCAG formula pinned by its own test"
    requirement: REQ-shaft-web
    verification:
      - kind: e2e
        ref: "tests/test_browser.py#test_the_shipped_viewer_in_a_real_browser (step primary button contrast)"
        status: pass
      - kind: unit
        ref: "tests/test_browser.py#test_the_contrast_ratio_is_the_wcag_formula"
        status: pass
    human_judgment: false

duration: 25min
completed: 2026-10-29
status: complete
---

# Phase 33 Plan 10: G-33-2 Gap Closure Summary

**A refused-part link now dims the form and Reset and outlines the switch (CSS on `body[data-refused]`), the Gear | Shaft switch is ordered above the canvas under 820 px with `aside { display: contents; }`, and the dark primary buttons read 4.85:1 through a `--accent-fg` of the theme's own `--bg`; each seen red first in the browser.**

## Performance

- **Duration:** about 25 min (started about 01:25Z, finished 01:48Z; the start was not recorded at the time, so this is read from file times)
- **Tasks:** 3
- **Files modified:** 6 source, test and doc files, 1 created debt file, 3 pictures and 1 log

## Accomplishments

- G-33-2's three UI-review findings are closed in the shipped page, D-12, D-15 and D-20 standing.
- Each new check was seen red once on the unfixed page and is a row under `### Seen red once (Phase 33)` in `bench/RESULTS.md`.
- The dark link text shortfall found at planning is filed as `must` debt, not fixed here.

### The red lines and the green results

| Step | First failure on the unfixed page | After the fix |
|---|---|---|
| `bad part refused` | `AssertionError: #part=bogus: the form does not look refused` (`At index 0 diff: '1' != '0.45'`) | pass, 3.56 s |
| `narrow layout` | `AssertionError: the part switch is not above the canvas at 800 px: switch 1170, canvas 45, results 540, form 1225` | pass, 0.09 s |
| `primary button contrast` | `AssertionError: dark: the primary button's text rgb(255, 255, 255) on rgb(224, 87, 63) reads 3.75:1, under WCAG AA's 4.5:1` | pass, 0.11 s |

- **Printed contrast ratios:** light 5.48:1, dark 4.85:1.
- **Narrow layout's four tops at 800x900:** switch 57, canvas 109, results 604, form 1217 (px).
- **Gate:** `make verify` ended `======================= 2779 passed in 229.02s (0:03:49) =======================`, with ruff, `mypy --strict` and the import contracts clean. The log is `.planning/phases/33-interfaces-and-parity/investigation/33-10-verify.log`.

### What the pictures show

- `33-10-refused.png` (aside, scrolled to its top): the form's fields faded to the disabled look, neither radio checked, and a 2 px accent outline with a 4 px offset and a rounded corner around the PART switch, so the outline reads as attached to the switch. The first take was scrolled to the Reset row by the keyboard Reset, with the switch out of frame, so the step now scrolls the aside to its top before the shot.
- `33-10-narrow.png` (full page at 800 px): the header, then PART with both radios, then the canvas, then the downloads, warnings and results, then the form and the Reset and Copy link row, which reads like the desktop column. The first take had the switch flush against the canvas, so the switch got `padding-bottom: .6rem` in the narrow block.
- `33-10-dark-buttons.png`: Download STL and Download STEP in dark-gray text on the red-orange fill, legible.

## Task Commits

1. **Task 1 (tracer): the refused look** - `6632e7a` (fix)
2. **Task 2: the narrow order** - `a090389` (fix)
3. **Task 3: dark primary button contrast** - `d7f642d` (fix), with the debt item in `777778a` (docs)
4. **Pictures and gate log** - `41ec1ba` (docs)

The tracer feedback gate (auto-mode off, `HUMAN_VERIFY_MODE` end-of-phase, automated-only verify): the tracer's verify was re-run end to end (the browser test, test_api, test_browser_pins, ruff, mypy, the C1 identity check) and passed, so the plan expanded.

**Plan metadata:** the final docs commit follows this file.

## Files Created/Modified

- `src/spur/static/app.js` - `document.body.dataset.refused` set in `refuseLink` and deleted in `switchTo` and `followHash`, beside `refused` (three occurrences); `refuse()` and `gearQuery()` byte-identical to 6800769 (C1)
- `src/spur/static/style.css` - the `body[data-refused]` rules, the narrow block (`display: contents`, `order`, margins, panel colour on main), the dark `--accent-fg: #131619` with its measured comment
- `tests/test_browser.py` - `REFUSED_LOOK` and the look checks in `bad part refused`, the steps `narrow layout` and `primary button contrast`, `_rgb`, `_contrast` and `test_the_contrast_ratio_is_the_wcag_formula`
- `docs/architecture/web-ui.md` - the refused look, the narrow order and the two steps in the tests paragraph
- `bench/RESULTS.md` - three `33-10` seen-red rows
- `docs/tech_debt/active/2026-10-29-dark-mode-link-text-under-wcag-aa.md`, `docs/tech_debt/INDEX.md` - the filed debt, 4.47:1 re-measured with `_contrast`

## Decisions Made

- The review's "place the message by the switch" was met by the outline under D-15. Moving the message out of `#messages` would mean amending D-15.
- The narrow order is CSS only, so D-12 holds and index.html and the vendored bundle are unchanged (`git diff 0248ce3` is empty for both).
- Chromium 153 kept the aside's `complementary` landmark under `display: contents` on the gate's shell, so the plan's stop condition did not fire.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] The refused picture missed the switch**
- **Found during:** Task 1
- **Issue:** the keyboard Reset (focus plus Enter) scrolled the aside to its end, so `aside.screenshot` showed the Reset row and not the outlined switch.
- **Fix:** the step sets the aside's `scrollTop` to 0 before the shot.
- **Files modified:** tests/test_browser.py
- **Committed in:** 6632e7a

**2. [Rule 1 - Bug] The narrow switch sat flush against the canvas**
- **Found during:** Task 2
- **Issue:** the plan moved the side padding but the switch had no space below it once it ceased to be followed by a form.
- **Fix:** `padding-bottom: .6rem` on `.part-switch` in the narrow block; side space is `margin-inline: 1rem` on the three children and not padding, which keeps the fieldset's top rule inset as on the desktop.
- **Files modified:** src/spur/static/style.css
- **Committed in:** a090389

**3. [Rule 3 - Blocking] mypy rejected the box helper's return type**
- **Found during:** Task 2
- **Issue:** `bounding_box()` returns Playwright's `FloatRect`, not `dict[str, float]`.
- **Fix:** typed the helper `-> FloatRect` and imported it from `playwright.sync_api`.
- **Files modified:** tests/test_browser.py
- **Committed in:** a090389

**4. [Plan wording] The debt file carries 2026-10-29, not 2026-10-28**
- The plan allows a later filing day; the work ran on 2026-10-29. The file's style.css line reference for the `a` rule is 54, since the new comment and token moved it from 48.

---

**Total deviations:** 3 auto-fixed (2 bug, 1 blocking), 1 dated filing. **Impact on plan:** no scope change; the choices the plan left to the screenshot (outline offset and radius, the narrow padding) were settled by reading the pictures.

## Issues Encountered

None beyond the deviations above. The formula test passed on its first run, as it is a pure function, so only the browser steps have a red line.

## Known Stubs

None.

## Threat Flags

None. The only new surface is a body attribute written beside the refused state; T-33-26 is mitigated (three `dataset.refused` occurrences in app.js, the live look asserted after a radio click and after a valid link, `writes_a_field_shut` green).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- G-33-2 is closed in the page; the phase is ready for `/gsd-verify-work` to re-run UAT test 2.
- Open debt filed by this plan: `docs/tech_debt/active/2026-10-29-dark-mode-link-text-under-wcag-aa.md` (must; trigger: the dark palette is next edited, or the next UI review). Debt item filed, with its INDEX row.

---
*Phase: 33-interfaces-and-parity*
*Completed: 2026-10-29*

## Self-Check: PASSED

- Created files exist: the debt file, the three pictures and the gate log, all found on disk.
- Commits `6632e7a`, `a090389`, `d7f642d`, `777778a` and `41ec1ba` are ancestors of HEAD.
- The plan's acceptance checks re-ran green after the last code commit: `dataset.refused` count 3, `refuse` and `gearQuery` identical to 6800769, the four style.css greps 1 each, the RESULTS rows present, and `make verify` green.
