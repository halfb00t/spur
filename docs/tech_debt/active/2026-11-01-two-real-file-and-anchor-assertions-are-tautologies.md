# Two real-file and anchor assertions are tautologies

Severity: nice
Status: active
Date: 2026-11-01
Source: Phase 34 code review (34-REVIEW.md IN-05)
Related files:
- tests/din5480_real_tables_check.py:190-199
- tests/test_din5480_anchors.py

## Context
`test_the_guard_form_term_is_each_rows_d_ff1_maximum` asserts `low - margin == form_d_max` where `low` is `pin_contact_window(p, form_d_max)[0]`, which the function defines as `form_d_max + margin`. It fails only through float noise and checks nothing about the file. The first assertion of the anchors test (`low == approx(d_ff1 + GUARD_MARGIN_FACTOR * p.module)`) has the same shape; its second assertion (`low < contact < high`) is the real one.

## Why it matters
Tests that cannot fail count as coverage and hide that the property they are named for is unchecked.

## Next step
Delete the real-file test, or replace it with the property that matters: the tabulated pin's contact at nominal thickness lies above `form_d_max`, per row. Revisit when either file is next edited.
