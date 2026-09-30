---
status: testing
phase: 12-composition-pass
source: [12-VERIFICATION.md]
started: 2026-09-30T14:24:48Z
updated: 2026-09-30T14:24:48Z
---

## Current Test

number: 1
name: Seven fieldsets in order on the live form
expected: |
  Open the app with `make serve`. The form shows seven fieldsets in exactly this order:
  Teeth, Body, Bore, Recess, Spokes, Holes, Honeycomb — matching the human-confirmed 12-01
  answer ("seven") and the live /api/schema group order the automated test already pins.
awaiting: user response

## Tests

### 1. Seven fieldsets in order on the live form
expected: Open the app with `make serve`. Seven fieldsets appear in exactly this order: Teeth, Body, Bore, Recess, Spokes, Holes, Honeycomb — matching the human-confirmed 12-01 answer and the live /api/schema group order the automated test already pins.
result: [pending]

### 2. The composed link populates the form, builds the preview and prints every dimension
expected: Open `http://127.0.0.1:8000/#bore_flat=0&keyway_width=3&keyway_depth=1.4&spoke_count=4&spoke_width=2&hub_d=13.2&rim_wall=1&spoke_fillet=1&tip_chamfer=0.4`. All nine fields show the link's value, the 3D preview builds, the dimensions list shows the tip chamfer, keyway, recess, both cutout walls and the spoke fillet, and no warning appears.
result: [pending]

### 3. Copy link round-trips the same nine values
expected: Click "copy link" on that page and open the copied link in a new tab. The same nine values load and the same numbers print.
result: [pending]

### 4. A live 422 names both conflicting fields in the UI
expected: In that new tab, set `bore_hex` to 6. A 422 sentence naming the keyway and the hex fields appears in the UI, and the bore fields are marked invalid.
result: [pending]

## Summary

total: 4
passed: 0
issues: 0
pending: 4
skipped: 0
blocked: 0

## Gaps
