# `limit_measurement`'s `odd_confirmed` parameter and its odd-count branch are unreachable in production

Severity: must
Status: resolved
Date: 2026-11-01
Resolved in: refactor(34.1-03): drop limit_measurement's unreachable odd-count branch (D-09)
Source: Phase 34 code review (34-REVIEW.md IN-01)
Related files:
- src/spur/shaft_calc.py:380-406

## Context
`derive_shaft` is the only production caller of `limit_measurement` and passes `odd_confirmed=True` every time, so the `if p.teeth % 2 and not odd_confirmed: return LimitReading(None, ())` return (line 405) and the parameter that gates it run only in a test. The existing item `2026-10-31-din5480-tables-loader-refusals-not-reached-by-a-test.md` lists line 405 as "reached by no test" and proposes a test for it.

## Why it matters
`docs/CODING_VALUES.md` says not to leave unreachable branches as if finished. A test for line 405 would pin dead code and keep the parameter alive.

## Next step
Drop the parameter and the branch (the limit is only computed for a listed size), or keep it and correct the other debt note to say the line is dead rather than untested. Revisit when `limit_measurement` is next edited.

## Resolution
The branch and the `odd_confirmed` parameter were deleted, not tested (D-09): `limit_measurement` is asked for a limit only for a size the tables list, where D-11 confirms the odd formula at the tabulated pin, and `pin_measurement` keeps its own gate for the nominal reading. Both `derive_shaft` calls dropped the keyword; every printed number is unchanged (the shaft and parity tests ran unedited). The loader-refusals item's line 405 was therefore dead, not untested.
