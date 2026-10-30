# The `dropped` flag survives a same-part link that overtakes its build

Severity: nice
Status: active
Date: 2026-10-30
Source: Phase 33 re-verification after d1c520a (`.planning/phases/33-interfaces-and-parity/33-VERIFICATION.md`,
advisory); merged as is in PR #53
Related files:
- src/spur/static/app.js:337 (`followHash`, same-part branch)
- src/spur/static/app.js:491 (`update`, sets `dropped`)
- src/spur/static/app.js:115 (`buildForm` catch, reads `dropped`)

## Context
`update()` sets `dropped = true` when it returns because a newer form build is pending. A build that
finishes, or fails without being overtaken, resets it. A same-part link that overtakes the pending
build does not: its branch of `followHash` re-reads the hash and builds, but leaves `dropped` set.
A later schema fetch that fails then clears `#dims` and the downloads although they still match
the form on the page.

## Why it matters
The page loses numbers it could have kept. It never shows a wrong number (L08), so this is not a
correctness bug. Reaching it needs a link, a dropped edit, a same-part link and a failed fetch in
that order. No test covers it.

## Next step
Add `dropped = false;` to `followHash`'s same-part branch, with a browser step that drives the
sequence above red first. Revisit when `app.js`'s form-build guards are next touched.

<!-- On resolve: set Status: resolved, add `Resolved in: <commit sha>`,
     git mv into resolved/, move the INDEX row to Resolved — same commit as the fix. -->
