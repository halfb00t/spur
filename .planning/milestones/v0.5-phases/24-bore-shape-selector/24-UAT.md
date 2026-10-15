---
status: complete
phase: 24-bore-shape-selector
source: [24-VERIFICATION.md]
started: 2026-10-12T16:46:32Z
updated: 2026-10-13T02:08:18.365Z
---

## Current Test

[testing complete]

## Tests

### 1. Keyboard walk of the Bore shape select (code review WR-01)
test: On Firefox (any platform) or Chrome on Windows or Linux, focus the Bore shape select with the keyboard (Tab) and press ArrowDown once from the default D-flat, then ArrowDown again.
expected: Focus stays on the select so the second ArrowDown reaches No bore, or at minimum the next arrow key does not spin the Hex bore A/F number box and no request for a 0.05 mm hex bore is sent.
why_human: Code review WR-01 confirms on the wiring that the select listens on `input` only and `pend()` calls `input.focus()` in the same handler, so on engines where an arrow key commits the next option and fires `input`, the first step to a pending option moves focus to `bore_hex`. It did not reproduce with real arrow keys in headless Chrome on macOS (arrow keys open the popup there), and the browser test drives the select with `select_option`, which fires `input` once and never presses a key. No engine that exhibits the behavior was available to the verifier.
result: pass

### 2. The pick plans and writes in one synchronous handler (24-01 backstop truth)
test: Read the `pick()` and `pend()` handlers in `src/spur/static/app.js` and confirm that no `await`, timer or callback sits between the plan loop and the writes.
expected: Both run as one synchronous input-event handler; the only deferred work is the form listener's `scheduleUpdate()` debounce, and `update()`'s `seq` counter drops answers to older queries.
why_human: The 24-01 truth "Probe (write, concurrency)" is tagged `verification: backstop` (non-inferable). No test exercises interleaving, so the truth cannot be marked verified on presence and wiring alone. The verifier read the code as synchronous (no `await` between lines 290 and 415; `update()` carries `seq` at lines 239 to 277) and expects it to hold; it stays a human confirmation by the rules for backstop truths.
result: pass

## Summary

total: 2
passed: 2
issues: 0
pending: 0
skipped: 0
blocked: 0

## Gaps
