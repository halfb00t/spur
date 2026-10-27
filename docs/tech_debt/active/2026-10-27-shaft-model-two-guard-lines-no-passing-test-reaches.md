# Two guard lines in shaft_model.build_shaft are reached by no passing test

Severity: nice
Status: active
Date: 2026-10-27
Source: 32-06 `make verify` coverage table, `src/spur/shaft_model.py 77 2 16 1 96.77%` (`coverage report -m` names lines 179 and 187)
Related files:
- src/spur/shaft_model.py:179
- src/spur/shaft_model.py:187
- bench/RESULTS.md (`### The gate delta (32-06)`, `### Seen red once (Phase 32)`)

## Context
`build_shaft` has two lines no passing test runs: the bare `raise` of `except BuildError: raise` (179), and the
`The shaft solid is not one valid solid` raise after the kernel returns (187). Every other shaft module reads 100 %.
The second line is a real guard: 32-03 saw it fire against a deliberate break (a `.clean()` on the fuse result,
`32-03-red-clean.log`), but that break was reverted, so no durable test holds it. The first is a pass-through for a
`BuildError` raised inside the `try`; today nothing inside the `try` raises one.

## Why it matters
The total coverage floor (96 %) is met, so the gate stays green. If a later change to the construction stops the
one-valid-solid check from firing, no test says so: the shaft would hand a broken solid to the exporter (L08).

## Next step
Revisit when `src/spur/shaft_model.py` is next touched: add a test that makes the kernel return two solids (or an invalid
one) through a stub and asserts the BuildError, as `test_a_kernel_failure_is_a_shaft_modelling_defect_and_never_fillet_advice`
does for the kernel's own exception; then decide whether the re-raise is needed at all.
