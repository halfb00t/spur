---
status: testing
phase: 23-conditional-form-fields
source: [23-VERIFICATION.md]
started: 2026-10-11T13:52:41Z
updated: 2026-10-11T13:52:41Z
---

## Current Test

number: 1
name: Does the dim read well, in both themes
expected: |
  A dimmed field is clearly inert but legible and clearly still typeable: muted
  name/value/unit, dashed control border, the reason ("Needs Spoke arms above 0") as a
  full readable row — in light and in dark theme. On the refused keyway pair
  (`/#bore_hex=6&keyway_width=3&keyway_depth=1.4`) the accent invalid outline stays the
  stronger mark over the dim.
awaiting: user response

## Tests

### 1. Does the dim read well, in both themes
test: Open the viewer at `/#spoke_count=0&hub_d=40` in light and then dark theme, and at `/#bore_hex=6&keyway_width=3&keyway_depth=1.4`. Look at the seven dimmed fields (spoke_width, hub_d, rim_wall, spoke_fillet, hole_d, hole_circle_d, hex_wall) and at the keyway pair.
expected: A dimmed field is clearly inert but legible and clearly still typeable (muted text, dashed border, the reason as a full readable row) in both themes. On the refused keyway pair the accent invalid outline stays the stronger mark.
why_human: 23-01 D4 and 23-03 D5 are `human_judgment: true`. The browser test proves the CSS rules apply, computed colours differ between dimmed and live fields, the reason is displayed and the field stays editable — not that the result reads well.
result: [pending]

### 2. Judgment-tier prohibitions
test: Read the three rows of the Prohibitions table in 23-VERIFICATION.md (no `app.js` pin in `tests/test_api.py` loosened to get green; the eleven D-09 rows neither dropped nor added to; no wait or timeout moved). Spot-check with `git diff c065d6d..HEAD -- tests/test_api.py`.
expected: You agree with the verifier's reading — the `test_api.py` diff deletes only one docstring clause and rewrites one token (`fields.set`) to a stricter one; the declared set is exactly L41's eleven rows; no `BUILD_WAIT_MS` or debounce value moved.
why_human: Flagged `unverified-prohibition: human review recommended` — judgment-tier prohibitions carry no deterministic enforcement; the verifier's verdict is an LLM-judge reading, not authoritative.
result: [pending]

## Summary

total: 2
passed: 0
issues: 0
pending: 2
skipped: 0
blocked: 0

## Gaps
