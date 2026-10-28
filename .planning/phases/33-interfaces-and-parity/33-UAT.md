---
status: diagnosed
phase: 33-interfaces-and-parity
source: [33-VERIFICATION.md]
started: 2026-10-28T02:52:43Z
updated: 2026-10-28T15:27:08Z
---

## Current Test

[testing complete]

## Tests

### 1. Accept or reject the IN-01 residual against REQ-wr02-fixed's wording
expected: spoke_count=0-0, hole_count=0-0 and hole_count=00-0 answering 200 under a blank box, building the default part, is accepted as a tracked residual (deferred at /gsd-validate-phase 33), or rejected as a gap.
result: pass

### 2. Look at the UI-REVIEW findings on the real page (33-UI-REVIEW.md, 18/24)
expected: Under 820 px the Gear | Shaft switch sits below the canvas; a refused link leaves a form that still looks editable; dark-mode primary button text is about 3.7:1 (under WCAG AA 4.5:1). The human decides fix now, file as debt, or accept.
result: issue
reported: "fix"
severity: major

## Summary

total: 2
passed: 1
issues: 1
pending: 0
skipped: 0
blocked: 0

## Gaps

- gap_id: G-33-2
  truth: "Under 820 px the Gear | Shaft switch stays reachable above the canvas; a refused link leaves the form visibly non-editable; dark-mode primary button text meets WCAG AA 4.5:1 (33-UI-REVIEW.md findings)"
  status: failed
  reason: "User reported: fix"
  severity: major
  test: 2
  root_cause: "Three independent causes, each cited in 33-UI-REVIEW.md and confirmed against the code: (1) the 820 px media query reorders #view with order:-1 while the Gear | Shaft fieldset lives inside <aside>, so the switch renders after the canvas and results; (2) update() returns early while `refused` is set and nothing marks the form inert, so a refused link leaves a default-looking form that silently ignores edits; (3) dark-mode --accent #e0573f under --accent-fg #fff gives about 3.7:1 for 14 px .btn.primary text, below WCAG AA 4.5:1."
  artifacts:
    - path: "src/spur/static/style.css"
      issue: "@media (max-width: 820px) sets #view { order: -1 } (line 208), pushing the aside-held part switch below the canvas"
    - path: "src/spur/static/index.html"
      issue: "fieldset.part-switch sits inside <aside> (line 19), so it moves with the form column"
    - path: "src/spur/static/app.js"
      issue: "update() returns on `refused` (line 421); refuseLink() (line 257) sets the message but leaves the form live-looking and editable"
    - path: "src/spur/static/style.css"
      issue: "dark-mode --accent #e0573f (line 27) with --accent-fg #fff (line 9) on .btn.primary (line 152) is about 3.7:1"
  missing:
    - "Keep the Gear | Shaft switch above the canvas under 820 px (move it out of <aside> or keep it first in the mobile order)"
    - "Make the refused-link state visibly non-editable (inert/dimmed form) or let an edit end it; place the message by the switch"
    - "Dark-mode primary button fill/text pair measured at or above 4.5:1; light theme stays as is (about 5.5:1)"
  debug_session: ""
