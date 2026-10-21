# Phase 19 code review: the root_fillet label finding is still deferred

Severity: nice
Status: resolved
Resolved in: 61154d1 fix(28): label the root_fillet row by the root the server built (gsd/phase-28-refuse-the-bad-link)
Date: 2026-10-09
Source: `.planning/phases/19-the-trochoid-in-the-part/19-REVIEW.md` IN-01 to IN-04 (gsd-code-reviewer, standard depth); the human chose `fix-now` for CR-01 and WR-01 only
Related files:
- src/spur/static/app.js:23 (`['root_fillet', 'Root fillet used']` while a hob root is in force)
- History: the four findings are in Context below; the Update paragraph there says which are fixed

## Context
Four `Info` findings from the Phase 19 review, none a defect in a printed number or a built part:

- **IN-01** `_build` says `root_mode` is asked once so the part and the numbers cannot name different roots, but `_chamfer_tips` re-runs `tip_chamfer_effective(p)` without `rm`, which re-solves the curve for a chamfered trochoid build. `root_mode` is pure, so the two answers cannot diverge today; the comment overstates the guarantee and the curve is solved twice.
- **IN-02** `bench/trochoid_part.py` carries a stale "does not exist until 19-04" paragraph and re-solves the curve; its edge selector and oracle reading are near-copies of the ones in `tests/test_model.py`, so the "selector that must count" has two definitions that can drift.
- **IN-03** The Makefile comment quotes L34's 63.555 s gate while the gate reads 161–240 s on this host (19-09, accepted as `accept-A`, recorded in L38). The comment is a claim the repo contradicts. Resolved in: 34270c8 (L43 re-set the bar and the Makefile comment now cites it).
- **IN-04** The UI result row labels `root_fillet` "Root fillet used" under a hob root, where the value is the hob's tip radius; `_host_state` crashes outside a git checkout instead of printing "unknown".

**Update (2026-10-20, Phase 27).** IN-01 is fixed in `refactor(model): pass the build's one root answer to the tip chamfer`. IN-02's bench half (the stale paragraph and the re-solve) and IN-04's `_host_state` half are fixed in `fix(bench): read root_mode's curve and name an unknown HEAD in the trochoid bench`. IN-02's near-copy replacement (`root_edges`, `tooth0_root_edges`, `oracle_reading` against `tests/test_model.py`'s `_root_edges`, `_oracle_reading`) is `skipped` (D-07): the two sets differ in the error type (an assert against `ValueError`), in the sample count (a fixed 400 against a `samples` parameter) and in signature, and Phase 27's triage table records it. IN-03 was already resolved in `34270c8`. What remains is IN-04's `root_fillet` label (`src/spur/static/app.js:23`), which is Phase 28's REQ-root-fillet-label-follows-root. Phase 28 made that label a function of the info document (`root_form_d` set means the hob root was built), so the row reads "Hob tip radius used" under a hob root and "Root fillet used" otherwise.

## Why it matters
Maintainability only: a comment and a label that overstate, duplicated test helpers that can drift apart, and a bench that re-solves what it already has. No user-visible number is wrong (CR-01, the one that was, is fixed in the same review round).

## Next step
Make the `root_fillet` label a function of the document (Phase 28, REQ-root-fillet-label-follows-root), or when the `DIMS` table in `src/spur/static/app.js` is next touched. Then set this item resolved with that commit.

<!-- On resolve: set Status: resolved, add `Resolved in: <commit sha>`,
     git mv into resolved/, move the INDEX row to Resolved — same commit as the fix. -->
