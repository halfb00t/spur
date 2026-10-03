---
status: testing
phase: 14-honest-record
source: [14-VERIFICATION.md]
started: 2026-10-03T12:00:00Z
updated: 2026-10-03T10:40:00Z
---

## Current Test

number: 1
name: Accept or reject the 14-02 volume_rel deviation (15 composed rows at rel=1e-6)
expected: |
  Accept as an override, or require the 15 literals re-pinned at full precision
awaiting: user response

## Tests

### 1. 14-02 deviation: shared cutout assertion gained opt-in volume_rel; 15 composed rows (12 tip-chamfer, 3 single-sided-recess) assert at rel=1e-6
expected: Accept as an override, or require the 15 literals re-pinned at full precision
result: [pending]

### 2. WR-02: L33 says all three skip-the-cutout tripwire rows run at abs=1e-9, but holes/cells literals are 6 dp and the face-delta assert fires first on holes and spokes-filleted
expected: L33 states only what the rows prove, or the rows prove what L33 states (reword L33, or make the rows discriminating)
result: [pending]

### 3. WR-01: abs=1e-9 gaps measured on macOS arm64 only; CI is ubuntu-latest
expected: All four kernel-to-formula gaps stay far below 1e-9 mm3 on CI; record next to the arm64 ones
result: [pending]

### 4. README number guard: no repo test enforces "no number in README the tests do not prove"
expected: Accept the verifier's manual check (1.188, 1.25, 0.125 only, each a test row value), or ask for a repo test guarding README numbers
result: [pending]

### 5. WR-03: "no closed form exists after an arbitrary boolean" is false for 4 of the 15 composed rows; the claim sits in the debt file, L33 (twice) and three test_model.py docstrings
expected: Reword to "not derived" where it is false (tied to item 2's L33 decision: edit in place on the unlanded branch, or append an amendment), and decide whether the four web-formula rows move to abs=1e-9 now or stay with the debt
result: [pending]

## Summary

total: 5
passed: 0
issues: 0
pending: 5
skipped: 0
blocked: 0

## Gaps
