# Nothing pins that `_build` passes its own `rm` to `_chamfer_tips`

Severity: nice
Status: active
Date: 2026-10-20
Source: 27-REVIEW IN-04 (carried from the 19-REVIEW IN-01 follow-up), skipped on purpose in 27-REVIEW-FIX
Related files:
- tests/test_model.py:899
- tests/test_model.py:926
- tests/test_model.py:976
- src/spur/model.py:640
- src/spur/model.py:783

## Context
The chamfer limit reads the curve the part was cut from (`rm`) and does not solve it again.
The monkeypatches in `tests/test_model.py` (`lambda solid, _p, _pr, _rm: solid`,
`lambda _p, _rm=None: ...`) accept either calling shape, so reverting `_chamfer_tips` to
`tip_chamfer_effective(p)` would leave every test green. The change is correct today and
unguarded.

Both fixes the reviewer suggested assert an internal call: a counting wrapper on
`spur.model.root_mode` is an internal call count, and a stand-in on `tip_chamfer_effective`
that checks its `rm` argument is a private argument. `docs/CODING_VALUES.md` (Testing) bans
asserting private calls or internal call counts. The result is also identical either way,
because `tip_chamfer_effective(p)` re-derives the same `rm`; only the cost differs (a second
root solve), and a cost claim is measured, not asserted. So no test was forced.

## Why it matters
A revert would silently add a second root solve to every build that has a tip chamfer. Nothing
printed changes, so this is a performance regression a reader would only catch in a timing
run, not a wrong number. Hence `nice`.

## Next step
Revisit when `_build` or `_chamfer_tips` is next touched, or when a public per-build cost
counter exists. Then add a behaviour-level check (measured build time or root-solve count
through a public counter), not a call-count assertion.

<!-- On resolve: set Status: resolved, add `Resolved in: <commit sha>`,
     git mv into resolved/, move the INDEX row to Resolved — same commit as the fix. -->
