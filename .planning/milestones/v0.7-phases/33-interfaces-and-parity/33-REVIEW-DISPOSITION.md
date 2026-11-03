---
phase: 33
review: 33-REVIEW.md
titles: json
findings:
  - id: WR-01
    severity: warning
    disposition: fixed
    title: "A stale `buildForm` that rejects writes its error, and clears the refusal, over a newer build's page (prior)"
  - id: WR-05
    severity: warning
    disposition: fixed
    title: "After a build that threw midway the page holds no part, but `update()` still builds one (new)"
  - id: IN-07
    severity: info
    disposition: fixed
    title: "The refused-look checks leave three reachable states unasserted (new)"
  - id: IN-08
    severity: info
    disposition: fixed
    title: "`aside { display: contents }` rests on one engine's behaviour, and the focus order no longer follows the visual order (new)"
  - id: IN-09
    severity: info
    disposition: fixed
    title: "The L41 guard checks only `app.js`; the CSS route around it is guarded by a comment (new)"
  - id: IN-10
    severity: info
    disposition: fixed
    title: "`force=True` on the refused-state fill removes the proof that the field takes typing"
  - id: IN-11
    severity: info
    disposition: fixed
    title: "`web-ui.md` does not describe the two new browser steps, and calls `narrow layout` the last step"
  - id: IN-01
    severity: info
    disposition: fixed
    title: "\"No blanked token builds a part\" is not true for int fields: pydantic reads `0-<digits>` as a negative number (prior)"
  - id: IN-02
    severity: info
    disposition: fixed
    title: "The refused-token suggestion guesses for a token that is not a number (`+-5` becomes \"write it as -5\") (prior)"
  - id: IN-03
    severity: info
    disposition: fixed
    title: "Cache- and queue-sharing API tests depend on parameters no other test uses (prior)"
  - id: IN-04
    severity: info
    disposition: fixed
    title: "`_js_fmt` in the browser test rounds half-even where `fmt()` rounds half-up, and it duplicates `displayed()` (prior)"
  - id: IN-05
    severity: info
    disposition: fixed
    title: "The CLI's top-level description and `slug()` precision are stale or narrow after the shaft (prior)"
  - id: IN-06
    severity: info
    disposition: fixed
    title: "A repeated `designation` key is read as its last value, and no test pins it (prior)"
  - id: WR-03
    severity: warning
    disposition: fixed
    title: "A refusal whose gear build fails leaves a dimmed, unresponsive form of the old part with a message about something else (new)"
  - id: WR-04
    severity: warning
    disposition: fixed
    title: "The refused look is visual only; the form stays focusable, typable and announced as live (new)"
  - id: WR-02
    severity: warning
    disposition: fixed
    title: "The shaft's three route rows are cut off from the endpoint table in `http-api.md` (prior)"
open: 0
total: 16
recorded: 2026-10-29T11:44:43.036Z
---

# Phase 33: Code Review Disposition

| Finding | Severity | Disposition | Source |
|---------|----------|-------------|--------|
| WR-01 | warning | fixed | 33-REVIEW-FIX.md |
| WR-05 | warning | fixed | 33-REVIEW-FIX.md |
| IN-07 | info | fixed | 33-REVIEW-FIX.md |
| IN-08 | info | fixed | 33-REVIEW-FIX.md |
| IN-09 | info | fixed | 33-REVIEW-FIX.md |
| IN-10 | info | fixed | 33-REVIEW-FIX.md |
| IN-11 | info | fixed | 33-REVIEW-FIX.md |
| IN-01 | info | fixed | 33-REVIEW-FIX.md |
| IN-02 | info | fixed | 33-REVIEW-FIX.md |
| IN-03 | info | fixed | 33-REVIEW-FIX.md |
| IN-04 | info | fixed | 33-REVIEW-FIX.md |
| IN-05 | info | fixed | 33-REVIEW-FIX.md |
| IN-06 | info | fixed | 33-REVIEW-FIX.md |
| WR-03 | warning | fixed | 33-REVIEW-FIX.md (not in the current review) |
| WR-04 | warning | fixed | 33-REVIEW-FIX.md (not in the current review) |
| WR-02 | warning | fixed | 33-REVIEW-FIX.md (not in the current review) |

Dispositions: `open` (recorded, not yet triaged), `fixed`, `skipped`, `deferred`.
Set `deferred` by hand and put the reason in the Source cell; both are preserved. A `|` in the reason is kept as prose and escaped on the next run.
Re-running the gate keeps every row it can. A row the current review no longer reports is kept and its Source cell flagged, so a finding does not leave this record silently. ONE exception: when a finding id is REUSED by a different finding, the earlier decision cannot keep a row — the id is taken — and it is dropped. A RECORDED decision (anything but `open`) is named on the console when that happens; a row still at `open` is replaced silently, because `open` records no decision to lose.
