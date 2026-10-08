---
status: testing
phase: 18-trochoid-maths-proved
source: [18-VERIFICATION.md]
started: "2026-10-08T03:40:45Z"
updated: "2026-10-08T03:40:45Z"
---

## Current Test

number: 1
name: The fourth `curve invalid` guard arm refuses a crossing curve with an early point outside the involute
expected: |
  Patch `spur.calc._trochoid_point` on the tracer gear (10 teeth, module 1, 20 degrees, rho 0.38) so one
  early point past rb has half-angle = pr.half_angle(radius) + 1e-3, then call `_root_curve(c)`.
  Returns `"curve invalid"`. Today the fourth arm of the guard
  (`join == "crossing" and any(radius >= pr.rb and half >= pr.half_angle(radius) ...)`, calc.py ~1465-1468)
  can be replaced by `False` and all 473 tests in test_trochoid.py + test_calc.py + test_bench.py still pass.
  Decision: add the one test (cheap, recommended) or accept the arm as untested defensive code.
awaiting: user response

## Tests

### 1. The fourth `curve invalid` guard arm refuses a crossing curve with an early point outside the involute
expected: Returns `"curve invalid"` under the patched `_trochoid_point`; the arm is present and wired (calc.py ~1465-1468) but no test makes it fire — `test_every_structural_failure_is_refused_as_curve_invalid` is named for four arms and covers three. Mutation to `or False` reproduced by the verifier (and independently by review WR-01). Human decides: add the one test, or accept the arm as untested.
result: [pending]

## Summary

total: 1
passed: 0
issues: 0
pending: 1
skipped: 0
blocked: 0

## Gaps
