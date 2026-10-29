# The shaft download name rounds `reference_d` and `module` to six significant digits

Severity: nice
Status: active
Date: 2026-10-29
Source: Phase 33 code review IN-05 (`.planning/phases/33-interfaces-and-parity/33-REVIEW.md`); the fix report
(`33-REVIEW-FIX.md`) deferred the repr-exact half "see debt below" without filing it, caught by the
phase 33 re-verification
Related files:
- src/spur/shaft_params.py:114 (`ShaftParams.slug`)

## Context
`slug()` formats `reference_d` and `module` with `:g`, which keeps six significant digits. Two
shafts with `reference_d` 123.4567 and 123.4571 at one module and tooth count share the stem
`spur_shaft_w123.457x...`, and 25.00004 reads `w25`. The fit is also left out of the name, so the
rounding is a second collision source beside the fit. Commit 9612559 recorded this in the
docstring only. The output was not changed, because L49 and D-17 freeze the name.

## Why it matters
Two different shafts can download under the same filename, and the second download can overwrite the
first in the user's downloads folder. No cache is keyed by the slug (L40), so the part itself is
never wrong. The impact is confusion over files, not wrong geometry.

## Next step
Revisit when L49 is next superseded or a user reports a download-name collision. Then propose a new
`Lxx` that makes the name repr-exact (for example `{reference_d!r}`), with a test that names two
shafts that differ only past the sixth digit.

<!-- On resolve: set Status: resolved, add `Resolved in: <commit sha>`,
     git mv into resolved/, move the INDEX row to Resolved — same commit as the fix. -->
