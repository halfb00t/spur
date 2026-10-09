# Phase 19 code review: four info findings deferred

Severity: nice
Status: active
Date: 2026-10-09
Source: `.planning/phases/19-the-trochoid-in-the-part/19-REVIEW.md` IN-01 to IN-04 (gsd-code-reviewer, standard depth); the human chose `fix-now` for CR-01 and WR-01 only
Related files:
- src/spur/model.py (`_build`'s "one answer" comment; `_chamfer_tips` calls `tip_chamfer_effective(p)` without `rm`)
- bench/trochoid_part.py:109-121 (`trochoid_curve` re-solves the curve `RootMode.curve` already holds), :172-195 (`root_edges`, `tooth0_root_edges`, `oracle_reading` near-copies of `tests/test_model.py` `_root_edges`, `_oracle_reading`), :333 (`_host_state` `check=True` on `git rev-parse`)
- Makefile:152-156 (comment still quotes "the whole gate is 63.555 s (L34)")
- src/spur/static/app.js:23 (`['root_fillet', 'Root fillet used']` while a hob root is in force)

## Context
Four `Info` findings from the Phase 19 review, none a defect in a printed number or a built part:

- **IN-01** `_build` says `root_mode` is asked once so the part and the numbers cannot name different roots, but `_chamfer_tips` re-runs `tip_chamfer_effective(p)` without `rm`, which re-solves the curve for a chamfered trochoid build. `root_mode` is pure, so the two answers cannot diverge today; the comment overstates the guarantee and the curve is solved twice.
- **IN-02** `bench/trochoid_part.py` carries a stale "does not exist until 19-04" paragraph and re-solves the curve; its edge selector and oracle reading are near-copies of the ones in `tests/test_model.py`, so the "selector that must count" has two definitions that can drift.
- **IN-03** The Makefile comment quotes L34's 63.555 s gate while the gate reads 161–240 s on this host (19-09, accepted as `accept-A`, recorded in L38). The comment is a claim the repo contradicts.
- **IN-04** The UI result row labels `root_fillet` "Root fillet used" under a hob root, where the value is the hob's tip radius; `_host_state` crashes outside a git checkout instead of printing "unknown".

## Why it matters
Maintainability only: a comment and a label that overstate, duplicated test helpers that can drift apart, and a bench that re-solves what it already has. No user-visible number is wrong (CR-01, the one that was, is fixed in the same review round).

## Next step
Fix IN-01, IN-02 and IN-04 together when `model.py`, `bench/trochoid_part.py` or the `DIMS` table is next touched (one small commit: pass `rm` through `_chamfer_tips`, read `rm.curve` in the bench and import the test helpers, make the `root_fillet` label a function of the document, catch `CalledProcessError`/`FileNotFoundError` in `_host_state`). IN-03 belongs to the L34 re-set: when a new `Lxx` re-reads the gate bar on an idle host, rewrite the Makefile comment to cite it; until then the comment should at least point at L38.

<!-- On resolve: set Status: resolved, add `Resolved in: <commit sha>`,
     git mv into resolved/, move the INDEX row to Resolved — same commit as the fix. -->
