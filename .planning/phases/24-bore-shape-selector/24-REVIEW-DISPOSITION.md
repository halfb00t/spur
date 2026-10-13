---
phase: 24
review: 24-REVIEW.md
titles: json
findings:
  - id: WR-02
    severity: warning
    disposition: fixed
    title: "A blank or unreadable number box completes a pending pick with the field's default, and writes the zeros, although no number was typed"
  - id: IN-01
    severity: info
    disposition: open
    title: "The stash can restore a number older than what the user last typed, and the comment calls it \"the user's own string\" while it also holds page defaults"
  - id: IN-02
    severity: info
    disposition: open
    title: "A selector that names a group no field has fails with a message about the schema fetch and leaves a built but empty form"
  - id: IN-03
    severity: info
    disposition: open
    title: "The OpenAPI pin is a substring test on the whole document"
  - id: IN-04
    severity: info
    disposition: open
    title: "Every selector-made Hex part prints a warning in snake_case field names the form does not show (already filed)"
  - id: IN-05
    severity: info
    disposition: fixed
    title: "L42 still says a pending pick \"focuses the field that needs a number\" and ends at the next derive; the correction is an appended paragraph"
  - id: IN-06
    severity: info
    disposition: fixed
    title: "A garbled comment in the `twin selectors` step"
  - id: WR-01
    severity: warning
    disposition: fixed
    title: "A pending pick steals focus on every arrow-key step, so a keyboard user cannot walk the select, and the next arrow press edits a number nobody chose (confirms the unverified UI-review concern, with a platform caveat)"
  - id: CX-01
    severity: warning
    disposition: fixed
    title: "A pending pick is discarded before completion: Round from #bore_d=0 completed by typing bore_d shows D-flat because bore_flat stays 8 (Codex cross-review of PR #36)"
  - id: CX-02
    severity: warning
    disposition: fixed
    title: "WR-01 confirmed on Blink and Gecko (Windows, Linux): ArrowDown from D-flat selects Hex and moves the focus to bore_hex, the next arrow edits that number (Codex cross-review of PR #36)"
  - id: CX-03
    severity: info
    disposition: open
    title: "A selector with no options, a null entry or an unknown group throws in buildForm(), so startup shows the schema message and never calls update() (Codex cross-review of PR #36; the same case as IN-02)"
  - id: CX-04
    severity: warning
    disposition: fixed
    title: "With two selectors, a pending pick in the second ends the first's pending pick without restoring its row or re-deriving it, because the second pick stops the event before the form's listener (Codex re-review of faed50a)"
  - id: CX-05
    severity: info
    disposition: open
    title: "The twin selectors request-count assertion can pass before a queued 350 ms debounce fires and the page is closed; settle beyond the debounce before asserting zero requests (Codex review of 9da4851)"
open: 6
total: 13
recorded: 2026-10-13T03:54:13.390Z
---

# Phase 24: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| WR-02 | warning | fixed | `completePending()` keeps the pick pending while the asked box reads `''` (`94bccc4`); the every-state browser loop empties the box first wherever the field's default would clear the threshold and asserts the pick stays pending, seen red once with the fix line reverted |
| IN-01 | info | open | - |
| IN-02 | info | open | - |
| IN-03 | info | open | - |
| IN-04 | info | open | - |
| IN-05 | info | fixed | the superseded L42 sentences point at the amendment; the single timing reading is no longer compared with 24-04's mean (`94bccc4`) |
| IN-06 | info | fixed | the `twin selectors` comment names `pendings[0]` and `twins_page` correctly (`94bccc4`) |
| WR-01 | warning | fixed | `app.js` `pend()` no longer calls `focus()`; the select keeps the focus and is described by the field's reason row; asserted after every pending pick in `tests/test_browser.py` (fixed on the PR #36 branch after the Codex cross-review, `24-CROSS-REVIEW.md`) (not in the current review) |
| CX-01 | warning | fixed | `24-CROSS-REVIEW.md` finding 1: a pending pick stays until its number is typed, then `completePending()` writes what it held back (`faed50a`); proved for every pending pick, a two-number chain and an abandoned pick in `tests/test_browser.py`; L42 amended 2026-10-13 |
| CX-02 | warning | fixed | `24-CROSS-REVIEW.md` finding 2, the same defect as WR-01 with the engine evidence; fixed with it (`faed50a`) |
| CX-03 | info | open | `24-CROSS-REVIEW.md` finding 3, the same case as IN-02: fail-loud on the self-served schema; `tests/test_selector.py` and `test_schema_drives_the_form` catch a malformed entry before it ships |
| CX-04 | warning | fixed | `24-CROSS-REVIEW.md` re-review of `faed50a`: `completePending()` puts the ended pick's row back and re-derives that selector (`deriveSelector()`, `9da4851`); proved by the `twin selectors` browser step on a schema with its selector list doubled; latent today, the schema carries one selector |
| CX-05 | info | open | `24-CROSS-REVIEW.md` review of `9da4851`: the `twin selectors` zero-request assertion could pass before a 350 ms debounce fires; add a settle before it |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved. A `|` in the reason is kept as prose and escaped on the next run.
Re-running the gate keeps every row it can. A row the current review no longer reports is kept and its Source cell flagged, so a finding does not leave this record silently. ONE exception: when a finding id is REUSED by a different finding, the earlier decision cannot keep a row — the id is taken — and it is dropped. A RECORDED decision (anything but `open`) is named on the console when that happens; a row still at `open` is replaced silently, because `open` records no decision to lose.
