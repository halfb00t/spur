# `limit_measurement`'s `odd_confirmed` parameter and its odd-count branch are unreachable in production

Severity: must
Status: active
Date: 2026-11-01
Source: Phase 34 code review (34-REVIEW.md IN-01)
Related files:
- src/spur/shaft_calc.py:380-406

## Context
`derive_shaft` is the only production caller of `limit_measurement` and passes `odd_confirmed=True` every time, so the `if p.teeth % 2 and not odd_confirmed: return LimitReading(None, ())` return (line 405) and the parameter that gates it run only in a test. The existing item `2026-10-31-din5480-tables-loader-refusals-not-reached-by-a-test.md` lists line 405 as "reached by no test" and proposes a test for it.

## Why it matters
`docs/CODING_VALUES.md` says not to leave unreachable branches as if finished. A test for line 405 would pin dead code and keep the parameter alive.

## Next step
Drop the parameter and the branch (the limit is only computed for a listed size), or keep it and correct the other debt note to say the line is dead rather than untested. Revisit when `limit_measurement` is next edited.
