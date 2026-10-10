# A link with an invalid enum value loads a blank select and builds the default part

Severity: must
Status: active
Date: 2026-10-10
Source: Phase 21, 21-04 -- the browser test's pin (step `root_shape=bogus as today`)
Related files:
- `src/spur/static/app.js` -- `buildForm()` enum `select` (lines 66-69), `readHash()` (96-100), `gearQuery()` (103-109)
- `tests/browser_scenarios.py` -- step `root_shape=bogus as today`, which pins the behaviour below

## Context
Opening `#root_shape=bogus&teeth=22` gives the `root_shape` select a value that is not among
its options, so the browser sets the select's value to `''` and its `selectedIndex` to -1:
the control shows blank. `gearQuery()` skips an empty value, so the page sends
`/api/info?teeth=22` and `/api/model.stl?teeth=22&quality=preview` with no `root_shape`,
rewrites the fragment to `#teeth=22`, shows no error and no message about the dropped field,
and draws the default (radial) part. The API alone answers `/api/info?root_shape=bogus&teeth=22`
with a 422 whose message is "Input should be 'radial' or 'trochoid'". Measured in a real
browser (Chrome Headless Shell on SwiftShader) in 21-04; 21-RESEARCH Code Example 8 read the
same.

## Why it matters
A value someone put in a shared link is dropped without a word, and the page then builds the
default part where the API would have refused. That is the spirit of L03 and L05 turned
upside down: a parameter the user set must never silently change the part, and an invalid one
is a 422, not a guess. No printed number is wrong (the part shown is the default one and its
numbers are honest for it), but a link that was meant to mean something else loads as if it
meant the default, and the fragment is rewritten so the evidence of what was asked is gone
from the address bar.

## Next step
Revisit when Phase 23 or 24 touches `buildForm`'s enum rendering, or when a user reports a link
that loaded a blank select. The browser test pins today's behaviour, so the fix (keep the
invalid value and let the API's 422 mark the field, or mark the field client-side) is a
deliberate change of that pin, made in the same commit as the fix.

<!-- On resolve: set Status: resolved, add `Resolved in: <commit sha>`,
     git mv into resolved/, move the INDEX row to Resolved -- same commit as the fix. -->
