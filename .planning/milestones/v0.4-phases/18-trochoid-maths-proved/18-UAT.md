---
status: complete
phase: 18-trochoid-maths-proved
source: [18-VERIFICATION.md]
started: "2026-10-08T03:40:45Z"
updated: "2026-10-08T05:14:39Z"
---

## Current Test

[testing complete]

## Tests

### 1. The fourth `curve invalid` guard arm refuses a crossing curve with an early point outside the involute
expected: Returns `"curve invalid"` under the patched `_trochoid_point`; the arm is present and wired (calc.py ~1465-1468) but no test makes it fire — `test_every_structural_failure_is_refused_as_curve_invalid` is named for four arms and covers three. Mutation to `or False` reproduced by the verifier (and independently by review WR-01). Human decides: add the one test, or accept the arm as untested.
result: passed — the test exists (8e96c2d): `test_a_crossing_curve_with_an_early_point_outside_the_involute_is_refused` makes the fourth arm fire on the tracer gear and is red with the arm replaced by `False` (18-06-SUMMARY)

## Summary

total: 1
passed: 1
issues: 0
pending: 0
skipped: 0
blocked: 0

## Gaps
